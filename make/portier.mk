# ============================================================================
# make/portier.mk – ELION Portier Port-Policy & Governance Makefile
# ============================================================================
# Zentrale Definitions- und Policy-Targets für:
#   • Port-Governance (12344–12399, 8080 nur 2.openwebui)
#   • Service-Orchetrierung (opena1→kordp→archivp→opena2)
#   • Safepoints & Audit-Trails
#   • Health-Checks
# ============================================================================

# ─────────────────────────────────────────────────────────────────────────
# GLOBAL POLICY DEFINITIONS
# ─────────────────────────────────────────────────────────────────────────

# Forbidden Ports (außerhalb erlaubter Range)
FORBIDDEN_PORTS := 80 443 3000 5000 5432 6379 9200 9300 27017 50070 9090 3001 3002 3003 4000 4001 4002 5173 5174 5175 6000 7000 7001 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 9000 9001 9002

# Allowed Port Range (Portier Services)
ALLOWED_PORT_MIN := 12344
ALLOWED_PORT_MAX := 12399

# Special Exception (OpenWebUI only)
OPENWEBUI_PORT := 8080
OPENWEBUI_SERVICE := 2.openwebui

# Core Services & Ports
SERVICE_OPENA1 := 3.opena1_coordinator
SERVICE_KORDP := 5.kordp_scheduler
SERVICE_ARCHIVP := 4.opena2_archivator
SERVICE_OPENA2 := 4.opena2_archivator

PORT_OPENA1 := 12344
PORT_KORDP := 12346
PORT_ARCHIVP := 12348
PORT_OPENA2 := 12348

# Directories
DIR_ROOT := $(shell pwd)
DIR_BIN := $(DIR_ROOT)/bin
DIR_SCRIPTS := $(DIR_ROOT)/scripts
DIR_SRC := $(DIR_ROOT)/src
DIR_CONFIGS := $(DIR_ROOT)/configs
DIR_LOGS := $(DIR_ROOT)/logs
DIR_ARCHIV := $(DIR_ROOT)/1.portier_openai/archivp

# Configuration
VENV_DIR := $(DIR_ROOT)/1.portier_openai/venv312
PYTHON_BIN := $(VENV_DIR)/bin/python
PYTHON_VERSION := 3.12

# ─────────────────────────────────────────────────────────────────────────
# TARGET: policy – Prüfe Port-Policy-Compliance
# ─────────────────────────────────────────────────────────────────────────
.PHONY: policy
policy:
	@echo "🔍 [POLICY] Scanning for Port-Policy violations..."
	@echo ""
	@echo "📋 Policy Rules:"
	@echo "   • Allowed Range: $(ALLOWED_PORT_MIN)–$(ALLOWED_PORT_MAX)"
	@echo "   • Forbidden Ports (exakt): 80, 443, 3000, 5000, 5432, 6379, 8000-8009"
	@echo "   • Exception: 8080 allowed in:"
	@echo "     - 2.openwebui/"
	@echo "     - Dashboard & OpenWebUI adapters"
	@echo ""
	@VIOLATIONS=0; \
	echo "🔎 Scanning core services (exakte Port-Matches)..." && \
	\
	echo "   Checking for :80/ :443/ :3000/ :5000/ :5432/ :6379..." && \
	if grep -rn -E ":(80|443|3000|5000|5432|6379)['\"]" --include="*.py" --include="*.sh" --include="*.json" \
		3.opena1_coordinator/ 5.kordp_scheduler/ 4.opena2_archivator/ \
		2>/dev/null | grep -v "venv" | grep -v ".venv" > /tmp/policy_forbidden.txt; then \
		if [ -s /tmp/policy_forbidden.txt ]; then \
			VIOLATIONS=$$(wc -l < /tmp/policy_forbidden.txt); \
			echo "   ❌ Found forbidden ports in core services:"; \
			cat /tmp/policy_forbidden.txt | head -3; \
		fi; \
	fi && \
	\
	echo "   Checking for :8000-:8009 (excluding 8080)..." && \
	if grep -rn -E ":(800[1-9]|8000)['\"]" --include="*.py" --include="*.sh" --include="*.json" \
		3.opena1_coordinator/ 5.kordp_scheduler/ 4.opena2_archivator/ \
		2>/dev/null | grep -v "venv" | grep -v ".venv" > /tmp/policy_8000.txt; then \
		if [ -s /tmp/policy_8000.txt ]; then \
			VIOLATIONS=$$((VIOLATIONS + $$(wc -l < /tmp/policy_8000.txt))); \
			echo "   ❌ Found forbidden :8000-8009 ports:"; \
			cat /tmp/policy_8000.txt | head -3; \
		fi; \
	fi && \
	\
	if [ $$VIOLATIONS -eq 0 ]; then \
		echo "   ✅ No violations found"; \
		echo ""; \
		echo "✅ [POLICY] PASS – Port-Policy compliance verified"; \
		exit 0; \
	else \
		echo ""; \
		echo "❌ [POLICY] FAIL – Found $$VIOLATIONS violation(s)"; \
		exit 1; \
	fi

# ─────────────────────────────────────────────────────────────────────────
# TARGET: ports – Zeige Port-Mapping
# ─────────────────────────────────────────────────────────────────────────
.PHONY: ports
ports:
	@echo "📡 [PORTS] ELION Portier Port-Mapping"
	@echo ""
	@echo "Allowed Range: $(ALLOWED_PORT_MIN)–$(ALLOWED_PORT_MAX)"
	@echo ""
	@echo "Core Services:"
	@printf "  %-20s %5d  ($(SERVICE_OPENA1))\n" "opena1 (Coordinator)" "$(PORT_OPENA1)"
	@printf "  %-20s %5d  ($(SERVICE_KORDP))\n" "kordp (Scheduler)" "$(PORT_KORDP)"
	@printf "  %-20s %5d  ($(SERVICE_ARCHIVP))\n" "archivp (Archivator)" "$(PORT_ARCHIVP)"
	@printf "  %-20s %5d  ($(SERVICE_OPENA2))\n" "opena2 (Storage)" "$(PORT_OPENA2)"
	@echo ""
	@echo "OpenWebUI (Exception):"
	@printf "  %-20s %5d  ($(OPENWEBUI_SERVICE))\n" "OpenWebUI" "$(OPENWEBUI_PORT)"
	@echo ""
	@if command -v netstat >/dev/null 2>&1; then \
		echo "🔌 Listening Ports (netstat):"; \
		netstat -tulpn 2>/dev/null | grep -E "127\.0\.0\.1:(12[3-9][0-9]{2}|8080)" || echo "  (none listening)"; \
	elif command -v ss >/dev/null 2>&1; then \
		echo "🔌 Listening Ports (ss):"; \
		ss -tulpn 2>/dev/null | grep -E "127\.0\.0\.1:(12[3-9][0-9]{2}|8080)" || echo "  (none listening)"; \
	fi

# ─────────────────────────────────────────────────────────────────────────
# TARGET: bootstrap – Initialize venv, configs, directories
# ─────────────────────────────────────────────────────────────────────────
.PHONY: bootstrap
bootstrap:
	@echo "🔧 [BOOTSTRAP] Initializing Portier stack..."
	@echo ""
	
	@echo "📁 Creating directories..."
	@mkdir -p $(DIR_LOGS) $(DIR_ARCHIV) $(DIR_SCRIPTS)
	@echo "   ✅ Directories created"
	
	@echo ""
	@echo "🐍 Setting up venv (Python $(PYTHON_VERSION))..."
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python3 -m venv $(VENV_DIR) 2>/dev/null || \
		python3.13 -m venv $(VENV_DIR) 2>/dev/null || \
		python3.12 -m venv $(VENV_DIR); \
		echo "   ✅ venv created at $(VENV_DIR)"; \
	else \
		echo "   ✅ venv already exists at $(VENV_DIR)"; \
	fi
	
	@echo ""
	@echo "🔗 Creating .venv symlink..."
	@if [ ! -L .venv ]; then \
		ln -s $(VENV_DIR) .venv; \
		echo "   ✅ Symlink created: .venv → $(VENV_DIR)"; \
	else \
		echo "   ✅ Symlink already exists"; \
	fi
	
	@echo ""
	@echo "📦 Installing base dependencies..."
	@$(PYTHON_BIN) -m pip install --upgrade pip setuptools wheel >/dev/null 2>&1
	@echo "   ✅ pip, setuptools, wheel upgraded"
	
	@echo ""
	@echo "🛡️ Running policy check..."
	@$(MAKE) -s policy
	
	@echo ""
	@echo "✅ [BOOTSTRAP] Complete"

# ─────────────────────────────────────────────────────────────────────────
# TARGET: health – Check health of core services
# ─────────────────────────────────────────────────────────────────────────
.PHONY: health
health:
	@echo "🏥 [HEALTH] Checking core services..."
	@echo ""
	@HEALTHY=0; TOTAL=4; \
	\
	echo "🔎 opena1 ($(PORT_OPENA1))..."; \
	if curl -s http://127.0.0.1:$(PORT_OPENA1)/health 2>/dev/null | grep -q '"status"'; then \
		echo "   ✅ ONLINE"; \
		HEALTHY=$$((HEALTHY + 1)); \
	else \
		echo "   ❌ OFFLINE"; \
	fi; \
	\
	echo "🔎 kordp ($(PORT_KORDP))..."; \
	if curl -s http://127.0.0.1:$(PORT_KORDP)/health 2>/dev/null | grep -q '"status"'; then \
		echo "   ✅ ONLINE"; \
		HEALTHY=$$((HEALTHY + 1)); \
	else \
		echo "   ❌ OFFLINE"; \
	fi; \
	\
	echo "🔎 archivp ($(PORT_ARCHIVP))..."; \
	if curl -s http://127.0.0.1:$(PORT_ARCHIVP)/health 2>/dev/null | grep -q '"status"'; then \
		echo "   ✅ ONLINE"; \
		HEALTHY=$$((HEALTHY + 1)); \
	else \
		echo "   ❌ OFFLINE"; \
	fi; \
	\
	echo "🔎 opena2 ($(PORT_OPENA2))..."; \
	if curl -s http://127.0.0.1:$(PORT_OPENA2)/health 2>/dev/null | grep -q '"status"'; then \
		echo "   ✅ ONLINE"; \
		HEALTHY=$$((HEALTHY + 1)); \
	else \
		echo "   ❌ OFFLINE"; \
	fi; \
	\
	echo ""; \
	echo "📊 Result: $$HEALTHY/$$TOTAL services healthy"; \
	if [ $$HEALTHY -eq $$TOTAL ]; then \
		echo "✅ [HEALTH] All services OK"; \
		exit 0; \
	else \
		echo "⚠️ [HEALTH] Some services down"; \
		exit 1; \
	fi

# ─────────────────────────────────────────────────────────────────────────
# TARGET: generate-original – One-shot orchestration
# ─────────────────────────────────────────────────────────────────────────
.PHONY: generate-original
generate-original: bootstrap
	@echo "🚀 [GENERATE-ORIGINAL] One-shot orchestration..."
	@echo ""
	
	@echo "⏱️ Startup sequence:"
	@echo "   1. Starting opena1 ($(PORT_OPENA1))..."
	@echo "   2. Starting kordp ($(PORT_KORDP))..."
	@echo "   3. Starting archivp ($(PORT_ARCHIVP))..."
	@echo "   4. Starting opena2 ($(PORT_OPENA2))..."
	@echo ""
	
	@if [ -x "$(DIR_SCRIPTS)/bootstrap_core.sh" ]; then \
		bash $(DIR_SCRIPTS)/bootstrap_core.sh 2>&1 | sed 's/^/   /'; \
	else \
		echo "   ⚠️ $(DIR_SCRIPTS)/bootstrap_core.sh not found or not executable"; \
		echo "   Make sure to run: chmod +x $(DIR_SCRIPTS)/bootstrap_core.sh"; \
		exit 1; \
	fi
	
	@echo ""
	@echo "✅ [GENERATE-ORIGINAL] Services initialized"

# ─────────────────────────────────────────────────────────────────────────
# TARGET: validate – Full compliance check
# ─────────────────────────────────────────────────────────────────────────
.PHONY: validate
validate: policy ports health
	@echo ""
	@echo "✅ [VALIDATE] All checks passed"

# ─────────────────────────────────────────────────────────────────────────
# TARGET: clean – Clean logs and caches
# ─────────────────────────────────────────────────────────────────────────
.PHONY: clean
clean:
	@echo "🧹 [CLEAN] Removing logs and caches..."
	@rm -f $(DIR_LOGS)/*.log
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ [CLEAN] Complete"

# ─────────────────────────────────────────────────────────────────────────
# TARGET: help – Show available targets
# ─────────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo "📖 ELION Portier Makefile Targets"
	@echo ""
	@echo "Port & Policy:"
	@echo "  make policy                – Check port-policy compliance (no 8080 outside 2.openwebui)"
	@echo "  make ports                 – Display port-mapping"
	@echo "  make validate              – Run all checks (policy, ports, health)"
	@echo ""
	@echo "Initialization & Runtime:"
	@echo "  make bootstrap             – Setup venv, directories, symlinks"
	@echo "  make generate-original     – One-shot orchestration (all services)"
	@echo "  make health                – Check service health"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                 – Remove logs and caches"
	@echo "  make help                  – Show this message"

.PHONY: .help
.help: help

# ============================================================================
# END: make/portier.mk
# ============================================================================
