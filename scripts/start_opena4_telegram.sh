#!/usr/bin/env bash
# Start opena4_telegram Agent (Port 12346)
# Usage: bash start_opena4_telegram.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ROOT}/../1.opena1&2_portier/venv313"
PYTHON="${VENV}/bin/python3"
LOGS="${ROOT}/../logs"

mkdir -p "$LOGS"

echo "🚀 Starting opena4_telegram (Port 12346)..."

nohup "$PYTHON" "${ROOT}/main_opena4_telegram.py" > "${LOGS}/opena4_telegram.nohup.log" 2>&1 &
PID=$!

echo "✅ opena4_telegram PID: $PID"
sleep 2

# Health check
if curl -s http://127.0.0.1:12346/health &>/dev/null; then
    echo "✅ opena4_telegram is healthy"
else
    echo "❌ opena4_telegram health check failed"
    sleep 3
    tail -20 "${LOGS}/opena4_telegram.nohup.log"
    exit 1
fi
