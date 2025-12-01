#!/bin/bash
# Stop-Script für opena21 (Workflow Engine)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/logs/opena21.pid"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Prüfen ob PID-Datei existiert
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}⚠️  opena21 läuft nicht (keine PID-Datei)${NC}"
    exit 0
fi

# PID auslesen
PID=$(cat "$PID_FILE")

# Prüfen ob Prozess läuft
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Prozess $PID nicht gefunden (bereits gestoppt)${NC}"
    rm -f "$PID_FILE"
    exit 0
fi

# Prozess stoppen
echo -e "${RED}🛑 Stoppe opena21 (PID: $PID)...${NC}"
kill "$PID"

# Warten auf Prozessende (max. 10s)
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ opena21 erfolgreich gestoppt${NC}"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force-Kill wenn nach 10s noch läuft
if ps -p "$PID" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Erzwinge Stop (SIGKILL)...${NC}"
    kill -9 "$PID"
    sleep 1
fi

# Cleanup
rm -f "$PID_FILE"
echo -e "${GREEN}✅ opena21 gestoppt${NC}"
