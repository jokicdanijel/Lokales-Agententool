#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# opena5 Start Script (VS Code Agent)
# Port: 12351 | Kürzel: vscop
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  opena5 Start (VS Code Agent)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/opena5.pid"
NOHUP_LOG="$LOG_DIR/opena5.nohup.log"

mkdir -p "$LOG_DIR"

PORT=12351
SERVICE_NAME="opena5"

# PID-Check
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  $SERVICE_NAME läuft bereits! PID: $OLD_PID${NC}"
        echo -e "${YELLOW}   Stoppe zuerst mit: bin/stop_opena5.sh${NC}"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Port-Check
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}❌ Port $PORT ist bereits belegt!${NC}"
    lsof -i :$PORT
    exit 1
fi

# .env laden
if [[ -f "$PROJECT_ROOT/../.env" ]]; then
    echo -e "${GREEN}✅ Lade .env aus Projekt-Root${NC}"
    set -a
    source "$PROJECT_ROOT/../.env"
    set +a
elif [[ -f "$PROJECT_ROOT/.env" ]]; then
    echo -e "${GREEN}✅ Lade .env aus opena5-Verzeichnis${NC}"
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
fi

# BEARER_TOKEN validieren
if [[ -z "${BEARER_TOKEN:-}" ]]; then
    echo -e "${RED}❌ BEARER_TOKEN nicht gesetzt!${NC}"
    exit 1
fi

# Python Dependencies
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installiere Dependencies...${NC}"
    pip3 install --break-system-packages -q fastapi uvicorn pydantic requests
fi

# Service starten
cd "$PROJECT_ROOT"
echo -e "${BLUE}🚀 Starte $SERVICE_NAME auf Port $PORT...${NC}"

nohup python3 main_vscode_agent.py > "$NOHUP_LOG" 2>&1 &

NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

sleep 2

if kill -0 "$NEW_PID" 2>/dev/null; then
    echo -e "${GREEN}✅ $SERVICE_NAME gestartet!${NC}"
    echo -e "${GREEN}   PID: $NEW_PID${NC}"
    echo -e "${GREEN}   Port: $PORT${NC}"
    echo -e "${GREEN}   Logs: $NOHUP_LOG${NC}"
    echo -e "${GREEN}   Health: http://127.0.0.1:$PORT/health${NC}"
    echo ""
    echo -e "${BLUE}📋 Log-Tail:${NC}"
    tail -20 "$NOHUP_LOG"
else
    echo -e "${RED}❌ Start fehlgeschlagen!${NC}"
    cat "$NOHUP_LOG"
    rm -f "$PID_FILE"
    exit 1
fi
