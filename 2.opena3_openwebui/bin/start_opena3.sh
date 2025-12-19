#!/usr/bin/env bash
# Start-Skript für opena3 (OpenWebUI Terminal Agent)
# Port: 12347 | PID: logs/opena3.pid

set -euo pipefail
# Robustes .env-Parsing (safe für Keys mit = Zeichen)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Farben
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  opena3 Start (OpenWebUI Terminal Agent)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"

# Logs-Ordner erstellen
mkdir -p logs

# PID-Check
PID_FILE="logs/opena3.pid"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  opena3 läuft bereits (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}   Stoppe mit: kill $OLD_PID${NC}"
        exit 1
    else
        echo -e "${YELLOW}⚠️  Stale PID-File gefunden, entferne...${NC}"
        rm -f "$PID_FILE"
    fi
fi

# Port-Check
PORT=12347
if netstat -tuln 2>/dev/null | grep -q ":$PORT " || ss -tuln 2>/dev/null | grep -q ":$PORT "; then
    echo -e "${RED}❌ Port $PORT bereits belegt!${NC}"
    netstat -tulpn 2>/dev/null | grep ":$PORT " || ss -tulpn 2>/dev/null | grep ":$PORT " || true
    exit 1
fi


# Validierung
if [ -z "${BEARER_TOKEN:-}" ]; then
    echo -e "${RED}❌ BEARER_TOKEN nicht gesetzt!${NC}"
    echo -e "${YELLOW}   Generiere Token: uuidgen > .env (BEARER_TOKEN=...)${NC}"
    exit 1
fi

# Python-Umgebung
PYTHON_CMD="python3"
if [ -d "../venv313" ]; then
    echo -e "${GREEN}✅ Aktiviere venv313${NC}"
    source "../venv313/bin/activate"
elif [ -d "venv" ]; then
    echo -e "${GREEN}✅ Aktiviere lokale venv${NC}"
    source "venv/bin/activate"
fi

# Abhängigkeiten prüfen
if ! $PYTHON_CMD -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  FastAPI nicht installiert, installiere...${NC}"
    $PYTHON_CMD -m pip install fastapi uvicorn requests pydantic
fi

# Start opena3
echo -e "${GREEN}🚀 Starte opena3 auf Port $PORT...${NC}"

nohup $PYTHON_CMD main_openwebui_agent.py \
    > logs/opena3.nohup.log 2>&1 &

OPENA3_PID=$!
echo "$OPENA3_PID" > "$PID_FILE"

echo -e "${GREEN}✅ opena3 gestartet!${NC}"
echo -e "${GREEN}   PID: $OPENA3_PID${NC}"
echo -e "${GREEN}   Port: $PORT${NC}"
echo -e "${GREEN}   Logs: logs/opena3.nohup.log${NC}"
echo -e "${GREEN}   Health: http://127.0.0.1:$PORT/health${NC}"
echo ""
echo -e "${YELLOW}📋 Log-Tail:${NC}"
sleep 2
tail -n 20 logs/opena3.nohup.log

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  opena3 erfolgreich gestartet!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
