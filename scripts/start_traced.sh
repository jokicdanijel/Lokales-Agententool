#!/usr/bin/env bash
set -euo pipefail

# Start key scanner scripts with tracing enabled.
# Usage: ./scripts/start_traced.sh [--venv path] [--otlp endpoint]

VENV=".venv"
OTLP=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://localhost:4318}

# optional venv activation
if [ -n "${1:-}" ] && [ "${1:-}" != "--otlp" ] && [ -d "$1" ]; then
  VENV="$1"
fi

if [ -f "$VENV/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
fi

export OTEL_EXPORTER_OTLP_ENDPOINT="$OTLP"

# ensure tracing deps are installed (best-effort)
python -m pip install --quiet -r scripts/requirements-tracing.txt || echo "⚠️  Could not auto-install tracing deps; ensure they are installed in your \$VENV (run \`python -m pip install -r scripts/requirements-tracing.txt\`)"

LOGDIR="artifacts/tracing_logs"
mkdir -p "$LOGDIR"

# Define the scripts to start (relative to repo root)
SCRIPTS=(
  "scripts/preflight_webpanel.py"
  "19.opena20_dashboard_agent/scripts/build_entitlements.py"
  "19.opena20_dashboard_agent/scripts/validate_entitlements.py"
  "19.opena20_dashboard_agent/scripts/preflight_gate_scanner.py"
  "19.opena20_dashboard_agent/scripts/entitlements_consistency_scanner.py"
  "19.opena20_dashboard_agent/scripts/api_binding_scanner.py"
  "19.opena20_dashboard_agent/scripts/secrets_vault_scanner.py"
)

PIDS=()
for s in "${SCRIPTS[@]}"; do
  logfile="$LOGDIR/$(basename "$s").log"
  echo "Starting $s -> $logfile"
  nohup python3 "$s" > "$logfile" 2>&1 &
  PIDS+=("$!")
  sleep 0.3
done

echo "Started scripts with PIDs: ${PIDS[*]}"
exit 0
