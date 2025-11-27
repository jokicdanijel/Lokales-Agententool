#!/usr/bin/env bash
#
# stop_opena14.sh - Stop opena14 (Calendar Management Agent)
# ===========================================================
#
# Usage: ./bin/stop_opena14.sh
#
# Maintainer: ELION Team

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOGS_DIR/opena14.pid"

echo "[INFO] Stoppe opena14..."

if [[ ! -f "$PID_FILE" ]]; then
    echo "[WARN] PID-File nicht gefunden - Service läuft nicht"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" >/dev/null 2>&1; then
    echo "[WARN] Prozess $PID läuft nicht - entferne PID-File"
    rm -f "$PID_FILE"
    exit 0
fi

echo "[INFO] Sende SIGTERM an PID $PID..."
kill "$PID"

# Wait for graceful shutdown (max 10 seconds)
for i in {1..10}; do
    if ! ps -p "$PID" >/dev/null 2>&1; then
        echo "[INFO] ✅ Service gestoppt"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "[WARN] Graceful shutdown timeout - force kill"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"

echo "[INFO] ✅ Service beendet"
