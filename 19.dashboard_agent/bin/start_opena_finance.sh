#!/usr/bin/env bash
# Start opena_finance Agent (Port 12347)
# Usage: bash start_opena_finance.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ROOT}/../1.portier_openai/venv313"
PYTHON="${VENV}/bin/python3"
LOGS="${ROOT}/../logs"

mkdir -p "$LOGS"

echo "🚀 Starting opena_finance (Port 12347)..."

nohup "$PYTHON" "${ROOT}/main_opena_finance.py" > "${LOGS}/opena_finance.nohup.log" 2>&1 &
PID=$!

echo "✅ opena_finance PID: $PID"
sleep 2

# Health check
if curl -s http://127.0.0.1:12347/health &>/dev/null; then
    echo "✅ opena_finance is healthy"
else
    echo "❌ opena_finance health check failed"
    sleep 3
    tail -20 "${LOGS}/opena_finance.nohup.log"
    exit 1
fi
