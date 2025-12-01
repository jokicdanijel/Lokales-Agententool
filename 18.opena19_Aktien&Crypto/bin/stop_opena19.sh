#!/bin/bash
# Stop Script für opena19 (Stocks & Crypto Agent)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

AGENT_ID="opena19"
PID_FILE="logs/${AGENT_ID}.pid"

echo "=========================================="
echo "  Stopping opena19 (Stocks & Crypto)"
echo "=========================================="

if [[ ! -f "$PID_FILE" ]]; then
    echo "[WARN] PID-File nicht gefunden: $PID_FILE"
    echo "[INFO] Service läuft möglicherweise nicht"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "[WARN] Prozess $PID läuft nicht mehr"
    rm -f "$PID_FILE"
    exit 0
fi

echo "[INFO] Stoppe Prozess $PID..."
kill "$PID"

# Warte max. 10 Sekunden
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "[INFO] ✅ Service gestoppt"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill falls nötig
echo "[WARN] Graceful shutdown fehlgeschlagen, force kill..."
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"

echo "[INFO] ✅ Service gestoppt (force)"
exit 0
