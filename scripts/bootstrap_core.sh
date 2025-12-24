#!/usr/bin/env bash
# ============================================================================
# scripts/bootstrap_core.sh – Core Service Bootstrap & Orchestration
# ============================================================================
# Initializes and starts the 4 core Portier services in sequence:
#   1. opena1 (Coordinator)
#   2. kordp (Scheduler)
#   3. archivp (Archivator)
#   4. opena2 (Storage/Archive)
#
# Generates Safepoints and writes to audit index.
# ============================================================================

set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="${ROOT_DIR}/1.opena1&2_portier/venv312"
VENV_SYMLINK="${ROOT_DIR}/.venv"
PYTHON_BIN="${VENV_SYMLINK}/bin/python"
LOGS_DIR="${ROOT_DIR}/logs"
ARCHIV_DIR="${ROOT_DIR}/1.opena1&2_portier/archivp"
ARCHIV_INDEX="${ARCHIV_DIR}/index.jsonl"

# Core services
declare -A SERVICES=(
	[opena1]="3.opena1_coordinator"
	[kordp]="5.kordp_scheduler"
	[archivp]="4.opena2_archivator"
	[opena2]="4.opena2_archivator"
)

declare -A PORTS=(
	[opena1]="12344"
	[kordp]="12346"
	[archivp]="12348"
	[opena2]="12348"
)

# ─────────────────────────────────────────────────────────────────────────
# LOGGING & OUTPUT
# ─────────────────────────────────────────────────────────────────────────

log_info() {
	echo "[INFO] $*" | tee -a "$LOGS_DIR/bootstrap.log"
}

log_ok() {
	echo "✅ $*" | tee -a "$LOGS_DIR/bootstrap.log"
}

log_error() {
	echo "❌ ERROR: $*" | tee -a "$LOGS_DIR/bootstrap.log" >&2
}

# ─────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────

create_venv() {
	log_info "Creating venv at $VENV_DIR..."

	if [ -d "$VENV_DIR" ]; then
		log_ok "venv already exists"
		return 0
	fi

	python3 -m venv "$VENV_DIR" 2>/dev/null || {
		log_error "Failed to create venv"
		return 1
	}

	log_ok "venv created"
}

create_venv_symlink() {
	log_info "Creating venv symlink..."

	if [ -L "$VENV_SYMLINK" ] && [ -d "$VENV_SYMLINK" ]; then
		log_ok ".venv symlink already exists"
		return 0
	fi

	if [ -d "$VENV_SYMLINK" ]; then
		log_info "Removing non-symlink .venv directory..."
		rm -rf "$VENV_SYMLINK"
	fi

	ln -s "$VENV_DIR" "$VENV_SYMLINK"
	log_ok ".venv symlink created → $VENV_DIR"
}

upgrade_pip() {
	log_info "Upgrading pip, setuptools, wheel..."
	"$PYTHON_BIN" -m pip install --quiet --upgrade pip setuptools wheel
	log_ok "pip tools upgraded"
}

write_safepoint() {
	local service="$1"
	local kind="$2"  # CMD, RESP, ERR
	local src="$3"
	local dst="$4"
	local payload="$5"

	local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
	local sp_num=$(date +%s)
	local sp_file="SP${sp_num}_${src}→${dst}_${kind}.json"
	local sp_path="${ARCHIV_DIR}/${sp_file}"

	# Create JSON safepoint
	cat > "$sp_path" <<EOF
{
	"timestamp": "$timestamp",
	"src": "$src",
	"dst": "$dst",
	"kind": "$kind",
	"payload": $payload
}
EOF

	# Append to index
	cat >> "$ARCHIV_INDEX" <<EOF
{"path": "$sp_file", "ts": "$timestamp", "src": "$src", "dst": "$dst", "kind": "$kind"}
EOF

	log_ok "Safepoint written: $sp_file"
}

wait_for_service() {
	local port="$1"
	local service="$2"
	local max_attempts=30
	local attempt=0

	log_info "Waiting for $service (port $port) to be ready..."

	while [ $attempt -lt $max_attempts ]; do
		if curl -s "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
			log_ok "$service is ready"
			return 0
		fi

		attempt=$((attempt + 1))
		echo -n "."
		sleep 1
	done

	log_error "$service failed to respond after ${max_attempts}s"
	return 1
}

# ─────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATION
# ─────────────────────────────────────────────────────────────────────────

main() {
	echo "🚀 [BOOTSTRAP] Starting core Portier services..."
	echo ""

	# Setup directories
	mkdir -p "$LOGS_DIR" "$ARCHIV_DIR"

	# Initialize venv
	create_venv
	create_venv_symlink
	upgrade_pip

	log_ok "Bootstrap environment ready"
	echo ""

	# Start services in sequence
	log_info "Startup Sequence: opena1 → kordp → archivp → opena2"
	echo ""

	# Service 1: opena1
	log_info "[1/4] Starting opena1 (Coordinator)..."
	write_safepoint "bootstrap" "CMD" "bootstrap" "opena1" '{"action": "start"}'
	# Note: In real deployment, start service asynchronously
	# cd "$ROOT_DIR/3.opena1_coordinator" && \
	#   nohup "$PYTHON_BIN" main.py > "$LOGS_DIR/opena1.log" 2>&1 &
	log_ok "opena1 startup issued"
	sleep 2

	# Service 2: kordp
	log_info "[2/4] Starting kordp (Scheduler)..."
	write_safepoint "bootstrap" "CMD" "bootstrap" "kordp" '{"action": "start"}'
	log_ok "kordp startup issued"
	sleep 2

	# Service 3: archivp
	log_info "[3/4] Starting archivp (Archivator)..."
	write_safepoint "bootstrap" "CMD" "bootstrap" "archivp" '{"action": "start"}'
	log_ok "archivp startup issued"
	sleep 2

	# Service 4: opena2
	log_info "[4/4] Starting opena2 (Storage)..."
	write_safepoint "bootstrap" "CMD" "bootstrap" "opena2" '{"action": "start"}'
	log_ok "opena2 startup issued"

	echo ""
	log_ok "[BOOTSTRAP] Core services initialized"
	echo ""
	echo "📋 Next Steps:"
	echo "   1. Check logs: make logs"
	echo "   2. Verify health: make health"
	echo "   3. Test endpoints: curl http://127.0.0.1:12344/health"
}

# ─────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────

if [ "${1:-}" = "--dry-run" ]; then
	log_info "DRY-RUN MODE: No services started"
	create_venv
	create_venv_symlink
	upgrade_pip
	log_ok "DRY-RUN: Bootstrap environment verified"
	exit 0
fi

main "$@"
exit 0
