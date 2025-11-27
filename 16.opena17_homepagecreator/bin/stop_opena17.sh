#!/usr/bin/env bash
set -euo pipefail

# =======================================
# opena17 - Homepage Creator Agent STOP
# =======================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

SERVICE_NAME="opena17"
PID_FILE="$PROJECT_DIR/logs/opena17.pid"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}[INFO]${NC} Keine PID-Datei gefunden - Service läuft vermutlich nicht"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}[INFO]${NC} Service (PID: $PID) läuft nicht mehr"
    rm -f "$PID_FILE"
    exit 0
fi

echo -e "${YELLOW}[INFO]${NC} Stoppe $SERVICE_NAME (PID: $PID)..."

kill "$PID"

# Warte auf sauberes Shutdown
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}[INFO]${NC} ✅ Service gestoppt"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force-Kill falls nötig
echo -e "${YELLOW}[WARN]${NC} Service reagiert nicht - force kill"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"

echo -e "${GREEN}[INFO]${NC} ✅ Service gestoppt (force)"
