#!/bin/bash
# Start-Script für opena21 (Workflow Engine)
# Port: 12364

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/logs/opena21.pid"
NOHUP_LOG="$PROJECT_DIR/logs/opena21.nohup.log"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logs-Ordner erstellen
mkdir -p "$PROJECT_DIR/logs"

# Prüfen ob bereits läuft
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  opena21 läuft bereits (PID: $PID)${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Verwaiste PID-Datei gefunden, entferne...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# .env laden (falls vorhanden)
if [ -f "$PROJECT_DIR/.env" ]; then
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs)
fi

# Port-Check
PORT=${OPENA21_PORT:-12364}
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $PORT bereits belegt${NC}"
    lsof -i :$PORT
    exit 1
fi

# Python Virtual Environment aktivieren (falls vorhanden)
if [ -d "$PROJECT_DIR/../.venv" ]; then
    source "$PROJECT_DIR/../.venv/bin/activate"
elif [ -d "$PROJECT_DIR/../venv313" ]; then
    source "$PROJECT_DIR/../venv313/bin/activate"
fi

# Service starten
echo -e "${GREEN}▶️  Starte opena21 (Workflow Engine) auf Port $PORT...${NC}"

cd "$PROJECT_DIR"
nohup python3 main.py > "$NOHUP_LOG" 2>&1 &
PID=$!

# PID speichern
echo $PID > "$PID_FILE"

# Kurz warten und Health-Check
sleep 2

if ps -p $PID > /dev/null 2>&1; then
    # Health-Check via curl
    if command -v curl &> /dev/null; then
        if curl -s http://127.0.0.1:$PORT/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ opena21 erfolgreich gestartet (PID: $PID)${NC}"
            echo -e "${GREEN}📊 Health: http://127.0.0.1:$PORT/health${NC}"
            echo -e "${GREEN}📋 Logs: tail -f $NOHUP_LOG${NC}"
        else
            echo -e "${YELLOW}⚠️  Service läuft (PID: $PID), aber Health-Check fehlgeschlagen${NC}"
            echo -e "${YELLOW}📋 Logs prüfen: tail -f $NOHUP_LOG${NC}"
        fi
    else
        echo -e "${GREEN}✅ opena21 gestartet (PID: $PID)${NC}"
        echo -e "${GREEN}📋 Logs: tail -f $NOHUP_LOG${NC}"
    fi
else
    echo -e "${RED}❌ Start fehlgeschlagen${NC}"
    echo -e "${RED}📋 Logs prüfen: tail -f $NOHUP_LOG${NC}"
    rm -f "$PID_FILE"
    exit 1
fi
