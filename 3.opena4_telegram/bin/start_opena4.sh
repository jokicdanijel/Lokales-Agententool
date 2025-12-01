#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# opena4 Start Script (Telegram Agent)
# Port: 12348 | Kürzel: telep
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  opena4 Start (Telegram Agent)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOG_DIR/opena4.pid"
NOHUP_LOG="$LOG_DIR/opena4.nohup.log"

# Log-Verzeichnis erstellen
mkdir -p "$LOG_DIR"

# Port & Service (PORTIER 3.0 Range: 12344-12399)
PORT=12346
SERVICE_NAME="opena4"
KUERZEL="tgap"

# PID-Check
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  $SERVICE_NAME läuft bereits! PID: $OLD_PID${NC}"
        echo -e "${YELLOW}   Stoppe zuerst mit: bin/stop_opena4.sh${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Stale PID-File entfernt${NC}"
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
    echo -e "${GREEN}✅ Lade .env aus opena4-Verzeichnis${NC}"
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
else
    echo -e "${YELLOW}⚠️  Keine .env gefunden (optional)${NC}"
fi

# BEARER_TOKEN validieren
if [[ -z "${BEARER_TOKEN:-}" ]]; then
    echo -e "${RED}❌ BEARER_TOKEN nicht gesetzt!${NC}"
    echo -e "${YELLOW}   Erstelle .env mit:${NC}"
    echo -e "${YELLOW}   echo 'BEARER_TOKEN=<uuid>' > .env${NC}"
    exit 1
fi

# Python Virtual Environment aktivieren
if [[ -d "$PROJECT_ROOT/venv313" ]]; then
    source "$PROJECT_ROOT/venv313/bin/activate"
    echo -e "${GREEN}✅ venv313 aktiviert${NC}"
elif [[ -d "$PROJECT_ROOT/venv" ]]; then
    source "$PROJECT_ROOT/venv/bin/activate"
    echo -e "${GREEN}✅ venv aktiviert${NC}"
else
    echo -e "${YELLOW}⚠️  Kein venv gefunden, verwende System-Python${NC}"
fi

# Dependencies prüfen/installieren
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  FastAPI nicht gefunden, installiere Dependencies...${NC}"
    pip3 install -q fastapi uvicorn pydantic requests python-telegram-bot
fi

# Service starten (nohup)
cd "$PROJECT_ROOT"
echo -e "${BLUE}🚀 Starte $SERVICE_NAME auf Port $PORT...${NC}"

nohup python3 main_telegram_agent.py \
    --port "$PORT" \
    --host "127.0.0.1" \
    > "$NOHUP_LOG" 2>&1 &

NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

# Warte auf Startup
sleep 2

# Health-Check
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
