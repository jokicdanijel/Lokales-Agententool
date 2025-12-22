#!/usr/bin/env bash
set -euo pipefail

# =======================================
# opena17 - Homepage Creator Agent START
# =======================================
# Port: 12362
# Kürzel: hpcreatep
# Service: Homepage-Generator, CMS, Deployment

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ROOT_DIR="$(dirname "$PROJECT_DIR")"

SERVICE_NAME="opena17"
PORT=12362
MAIN_FILE="$PROJECT_DIR/main_homepage_agent.py"
PID_FILE="$PROJECT_DIR/logs/opena17.pid"
LOG_FILE="$PROJECT_DIR/logs/opena17.nohup.log"

# Farben für Output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =======================================
# 1. Erstelle Logs-Verzeichnis
# =======================================

mkdir -p "$(dirname "$LOG_FILE")"

# =======================================
# 2. Python-Dependencies prüfen
# =======================================

echo -e "${YELLOW}[INFO]${NC} Prüfe Python-Dependencies..."

REQUIRED_PACKAGES=(
    "fastapi"
    "uvicorn"
    "pydantic"
)

MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${pkg}" 2>/dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}[INFO]${NC} Installiere fehlende Packages: ${MISSING_PACKAGES[*]}"
    
    # PEP 668 Workaround (Ubuntu 25.04)
    if python3 -m pip install --help | grep -q -- '--break-system-packages'; then
        python3 -m pip install --break-system-packages "${MISSING_PACKAGES[@]}"
    else
        python3 -m pip install "${MISSING_PACKAGES[@]}"
    fi
fi

echo -e "${GREEN}[INFO]${NC} ✅ Alle Dependencies vorhanden"

# =======================================
# 3. Port-Verfügbarkeit prüfen
# =======================================

echo -e "${YELLOW}[INFO]${NC} Prüfe Port $PORT..."

if lsof -i :$PORT >/dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} Port $PORT ist bereits belegt!"
    echo -e "${YELLOW}[INFO]${NC} Aktive Prozesse auf Port $PORT:"
    lsof -i :$PORT
    exit 1
fi

echo -e "${GREEN}[INFO]${NC} ✅ Port $PORT ist frei"

# =======================================
# 4. Laufenden Service prüfen
# =======================================

if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}[WARN]${NC} Service läuft bereits (PID: $OLD_PID)"
        echo -e "${YELLOW}[INFO]${NC} Stoppe alten Service..."
        kill "$OLD_PID" 2>/dev/null || true
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# =======================================
# 5. Service-Umgebung vorbereiten
# =======================================

# BEARER_TOKEN sollte von ops.sh durchgereicht werden
if [ -z "${BEARER_TOKEN:-}" ]; then
    echo -e "${YELLOW}[WARN]${NC} BEARER_TOKEN nicht gesetzt - verwende Standard"
    export BEARER_TOKEN="c899b90d-faf8-485b-afa4-078357cf5313"
fi

# =======================================
# 6. Service starten
# =======================================

echo -e "${YELLOW}[INFO]${NC} Starte $SERVICE_NAME..."

cd "$PROJECT_DIR"

nohup python3 "$MAIN_FILE" > "$LOG_FILE" 2>&1 &
SERVICE_PID=$!

echo $SERVICE_PID > "$PID_FILE"

echo -e "${GREEN}[INFO]${NC} ✅ Service gestartet (PID: $SERVICE_PID)"

# =======================================
# 7. Warte auf Service-Ready
# =======================================

echo -e "${YELLOW}[INFO]${NC} Warte auf Health-Check..."

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://127.0.0.1:$PORT/health > /dev/null 2>&1; then
        echo -e "${GREEN}[INFO]${NC} ✅ Health-Check erfolgreich"
        
        # Health-Response anzeigen
        curl -s http://127.0.0.1:$PORT/health | python3 -m json.tool
        
        echo ""
        echo -e "${GREEN}[SUCCESS]${NC} $SERVICE_NAME erfolgreich gestartet!"
        echo -e "${YELLOW}[INFO]${NC} PID: $SERVICE_PID"
        echo -e "${YELLOW}[INFO]${NC} Port: $PORT"
        echo -e "${YELLOW}[INFO]${NC} Logs: tail -f $LOG_FILE"
        
        exit 0
    fi
    
    sleep 1
    RETRY_COUNT=$((RETRY_COUNT + 1))
done

# Timeout
echo -e "${RED}[ERROR]${NC} Health-Check nach ${MAX_RETRIES}s fehlgeschlagen"
echo -e "${YELLOW}[INFO]${NC} Log-Output (letzte 20 Zeilen):"
tail -20 "$LOG_FILE"

exit 1
