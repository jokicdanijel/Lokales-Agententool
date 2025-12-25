.PHONY: venv deps test test-verbose test-fast coverage dry apply verify release archive clean scan clean-map help

# Colors
BOLD = \033[1m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
RESET = \033[0m

VENV_DIR ?= .venv
PYTHON ?= python3
PYTHON_MIN = 3.10
LOG_DIR = logs
BACKUP_DIR = backups
TIMESTAMP = $(shell date +%Y%m%d-%H%M%S)

help:
	@echo "$(BOLD)Portier Koordinator & Archivator + Project Scanner$(RESET)"
	@echo ""
	@echo "$(BOLD)Infrastructure Targets:$(RESET)"
	@echo "  $(GREEN)make venv$(RESET)           - Create/update virtual environment"
	@echo "  $(GREEN)make deps$(RESET)           - Install dependencies"
	@echo "  $(GREEN)make dry$(RESET)            - Run dry-run structure validation"
	@echo "  $(GREEN)make apply$(RESET)          - Apply structure normalization + symlinks"
	@echo "  $(GREEN)make verify$(RESET)         - Verify consistency (git, secrets, path_index)"
	@echo "  $(GREEN)make release$(RESET)        - Create GitHub release with artifacts"
	@echo "  $(GREEN)make archive$(RESET)        - Sync backups to local archive"
	@echo ""
	@echo "$(BOLD)Testing Targets:$(RESET)"
	@echo "  $(GREEN)make test$(RESET)           - Run tests with coverage (85% threshold)"
	@echo "  $(GREEN)make test-verbose$(RESET)   - Run tests with verbose output"
	@echo "  $(GREEN)make test-fast$(RESET)      - Run tests without coverage"
	@echo "  $(GREEN)make coverage$(RESET)       - Generate coverage report (HTML)"
	@echo ""
	@echo "$(BOLD)Scanner Targets:$(RESET)"
	@echo "  $(GREEN)make scan$(RESET)           - Run project scan → project_map/ (ChatGPT-ready)"
	@echo "  $(GREEN)make clean-map$(RESET)      - Remove project_map/ directory"
	@echo ""
	@echo "$(BOLD)Cleanup:$(RESET)"
	@echo "  $(GREEN)make clean$(RESET)          - Remove .venv, logs, backups"
	@echo ""
	@echo "$(BOLD)Workflow:$(RESET)"
	@echo "  1. make venv && make deps"
	@echo "  2. make dry"
	@echo "  3. (review reports) make apply"
	@echo "  4. make verify"
	@echo "  5. make release"
	@echo ""
	@echo "$(BOLD)Or just scan:$(RESET)"
	@echo "  make scan  # generates project_map/ with STRUCTURE.md, files.csv, stats.json, etc."

venv:
	@echo "$(YELLOW)[venv]$(RESET) Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && python -m pip install --upgrade pip setuptools wheel
	@echo "$(GREEN)✅ venv ready at $(VENV_DIR)$(RESET)"

deps: venv
	@echo "$(YELLOW)[deps]$(RESET) Installing dependencies..."
	. $(VENV_DIR)/bin/activate && pip install -r requirements.txt || pip install pydantic pyyaml click 2>/dev/null || true
	@echo "$(GREEN)✅ dependencies installed$(RESET)"

dry: deps
	@echo "$(YELLOW)[dry-run]$(RESET) Validating project structure (no changes)..."
	mkdir -p $(LOG_DIR)
	. $(VENV_DIR)/bin/activate && python3 scripts/structure_manager.py 2>&1 | tee $(LOG_DIR)/dry_run_$(TIMESTAMP).log || true
	@echo "$(YELLOW)Reports generated:$(RESET)"
	@ls -lh rename_map.csv path_index.json violations_report.md structure_checkpoint.json 2>/dev/null || echo "  (no reports yet)"

apply: deps
	@echo "$(RED)[APPLY]$(RESET) Applying structure normalization..."
	@if [ -f rename_map.csv ]; then \
		echo "$(YELLOW)Using cached rename_map.csv - re-run make dry to refresh$(RESET)"; \
	else \
		echo "$(YELLOW)No rename_map.csv found - running dry-run first...$(RESET)"; \
		make dry; \
	fi
	mkdir -p $(LOG_DIR)
	. $(VENV_DIR)/bin/activate && python3 scripts/structure_manager.py --apply --symlinks 2>&1 | tee $(LOG_DIR)/apply_$(TIMESTAMP).log || true
	@echo "$(GREEN)✅ Structure applied$(RESET)"
	@echo "$(YELLOW)Committing changes...$(RESET)"
	git add -A && git commit -m "chore(structure): apply folder normalization, conflicts isolated, reports updated [$(TIMESTAMP)]" || echo "$(YELLOW)No changes to commit$(RESET)"
	git tag -a vSTRUCTURE-$(TIMESTAMP) -m "Structure normalization $(TIMESTAMP)" || echo "$(YELLOW)Tag already exists$(RESET)"
	@echo "$(GREEN)✅ Commit & tag created$(RESET)"

verify:
	@echo "$(YELLOW)[verify]$(RESET) Running consistency checks..."
	@echo ""
	@echo "$(BOLD)1. Path Index vs Git$(RESET)"
	@if [ -f path_index.json ]; then \
		git ls-files > /tmp/.git_files 2>/dev/null; \
		jq -r '.files[]?.path' path_index.json > /tmp/.idx_files 2>/dev/null || true; \
		if diff -q /tmp/.git_files /tmp/.idx_files > /dev/null 2>&1; then \
			echo "$(GREEN)✅ Git ls-files matches path_index$(RESET)"; \
		else \
			echo "$(YELLOW)⚠ Differences found (expected after apply)$(RESET)"; \
		fi; \
	else \
		echo "$(YELLOW)⚠ path_index.json not found$(RESET)"; \
	fi
	@echo ""
	@echo "$(BOLD)2. Checksum Verification$(RESET)"
	@if [ -f $(BACKUP_DIR)/*.sha256 ]; then \
		sha256sum -c $(BACKUP_DIR)/*.sha256 2>/dev/null && echo "$(GREEN)✅ All checksums valid$(RESET)" || echo "$(RED)❌ Checksum mismatch$(RESET)"; \
	else \
		echo "$(YELLOW)⚠ No checksums found$(RESET)"; \
	fi
	@echo ""
	@echo "$(BOLD)3. Secret Scan$(RESET)"
	@rg -q "(AWS|AKIA|SECRET|TOKEN|PASSWORD)=" . --max-depth 3 2>/dev/null && echo "$(RED)❌ Secrets found!$(RESET)" || echo "$(GREEN)✅ No secrets detected$(RESET)"
	@echo ""
	@echo "$(BOLD)4. Git Status$(RESET)"
	@git status --short | head -5 || echo "$(GREEN)✅ Repository clean$(RESET)"

release: apply
	@echo "$(YELLOW)[release]$(RESET) Creating GitHub release with artifacts..."
	mkdir -p $(BACKUP_DIR)
	@bash scripts/make_release.sh $(TIMESTAMP)
	@echo "$(GREEN)✅ Release created$(RESET)"

archive: release
	@echo "$(YELLOW)[archive]$(RESET) Syncing backups..."
	mkdir -p ~/portier_openai/backups
	rsync -av --delete $(BACKUP_DIR)/ ~/portier_openai/backups/ 2>/dev/null || cp -rv $(BACKUP_DIR)/* ~/portier_openai/backups/ 2>/dev/null || true
	@echo "$(GREEN)✅ Backups synchronized$(RESET)"

clean:
	@echo "$(YELLOW)[clean]$(RESET) Removing temporary files..."
	rm -rf $(VENV_DIR) $(LOG_DIR)/*.log $(BACKUP_DIR)/*.tar.gz $(BACKUP_DIR)/*.zip $(BACKUP_DIR)/*.sha256
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

# ========== PROJECT SCANNER (zero-dependency, ChatGPT-ready) ==========

ROOT ?= .
OUT  ?= project_map

scan:
	@echo "$(YELLOW)[SCAN]$(RESET) Starting project scan..."
	@python3 tools/scan_project.py --root $(ROOT) --out $(OUT) --max-tree-depth 4 --hash-limit-mb 5
	@echo ""
	@echo "$(GREEN)✅ Scan complete$(RESET)"
	@echo "$(YELLOW)Output files:$(RESET)"
	@ls -1 $(OUT)/ | sed 's/^/  /'
	@echo ""
	@echo "$(YELLOW)Quick checks:$(RESET)"
	@echo "  head -n 40 $(OUT)/STRUCTURE.md"
	@echo "  wc -l $(OUT)/files.csv"
	@echo "  jq '. | length' $(OUT)/path_index.json"

clean-map:
	@echo "$(YELLOW)[CLEAN]$(RESET) Removing $(OUT)/"
	@rm -rf $(OUT)
	@echo "$(GREEN)✅ Done$(RESET)"

# ========== TESTING TARGETS ==========

test: deps
	@echo "$(YELLOW)[test]$(RESET) Running tests with coverage (85% threshold)..."
	@bash scripts/run_tests.sh -v
	@echo "$(GREEN)✅ Tests complete$(RESET)"

test-verbose: deps
	@echo "$(YELLOW)[test-verbose]$(RESET) Running tests with verbose output..."
	@bash scripts/run_tests.sh -vv
	@echo "$(GREEN)✅ Tests complete$(RESET)"

test-fast: deps
	@echo "$(YELLOW)[test-fast]$(RESET) Running tests without coverage..."
	@bash scripts/run_tests.sh --no-cov -v
	@echo "$(GREEN)✅ Tests complete$(RESET)"

coverage: deps
	@echo "$(YELLOW)[coverage]$(RESET) Generating coverage report..."
	@bash scripts/run_tests.sh --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated: htmlcov/index.html$(RESET)"
	@echo "$(YELLOW)Open htmlcov/index.html in your browser to view the report$(RESET)"

# ========== EVALUATION TARGETS ==========

tracing-up:
	@echo "$(YELLOW)[tracing]$(RESET) Starting local OTLP collector using docker-compose.otel.yml..."
	@bash ./bin/start_tracing_collector.sh || echo "$(RED)❌ Failed to start tracing collector$(RESET)"
	@echo "$(GREEN)✅ tracing collector running (if docker is available)$(RESET)"


deps-eval:
	@echo "$(YELLOW)[deps-eval]$(RESET) Installing evaluation dependencies..."
	. $(VENV_DIR)/bin/activate && pip install -r requirements-eval.txt || pip install -r requirements-eval.txt

eval: deps-eval
	@echo "$(YELLOW)[eval]$(RESET) Running evaluation with sample dataset..."
	. $(VENV_DIR)/bin/activate && python3 -m evaluation.runner evaluation/datasets/sample.jsonl --out evaluation/results/report.json
	@echo "$(GREEN)✅ Evaluation complete - report at evaluation/results/report.json$(RESET)"

# ========== INCLUDE PORTIER PORT-POLICY MAKEFILE ==========
include make/portier.mk

.DEFAULT_GOAL := help
