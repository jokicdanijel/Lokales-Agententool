#!/usr/bin/env bash
# Stop-Skript für opena3 (OpenWebUI Terminal Agent)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  opena3 Stop${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"

PID_FILE="logs/opena3.pid"

if [ ! -f "$PID_FILE" ]; then
    echo -e "${RED}❌ PID-File nicht gefunden: $PID_FILE${NC}"
    echo -e "${YELLOW}   opena3 läuft vermutlich nicht.${NC}"
    exit 1
fi

PID=$(cat "$PID_FILE")

if ! kill -0 "$PID" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Prozess $PID läuft nicht mehr${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

echo -e "${YELLOW}🛑 Stoppe opena3 (PID: $PID)...${NC}"
kill "$PID"

# Warte auf Beendigung (max 10 Sekunden)
for i in {1..10}; do
    if ! kill -0 "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ opena3 gestoppt${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force-Kill falls nötig
echo -e "${RED}⚠️  Prozess reagiert nicht, Force-Kill...${NC}"
kill -9 "$PID" 2>/dev/null || true
rm -f "$PID_FILE"

echo -e "${GREEN}✅ opena3 beendet${NC}"
