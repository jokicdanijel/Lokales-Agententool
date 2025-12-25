#!/usr/bin/env bash
# =============================================================================
# opena16 - Shop Management Agent Start Script
# Port: 12361
# Kürzel: shopp
# =============================================================================

set -euo pipefail

# Farbcodes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/logs/opena16.pid"
LOG_FILE="$PROJECT_DIR/logs/opena16.nohup.log"
MAIN_SCRIPT="$PROJECT_DIR/main_shop_agent.py"

# Config
PORT=12361
SERVICE_NAME="opena16"
HEALTH_ENDPOINT="http://127.0.0.1:$PORT/health"

# =============================================================================
# DEPENDENCY CHECK
# =============================================================================

check_dependencies() {
    echo -e "${YELLOW}[INFO] Überprüfe Dependencies...${NC}"

    # Core dependencies (erforderlich)
    local core_deps=("fastapi" "uvicorn" "pydantic")
    local missing_core=()

    for dep in "${core_deps[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            missing_core+=("$dep")
        fi
    done

    # Install missing dependencies
    if [ ${#missing_core[@]} -ne 0 ]; then
        echo -e "${YELLOW}[INFO] Installiere fehlende Dependencies...${NC}"

        # Try installing
        if pip install --break-system-packages "${missing_core[@]}" > /dev/null 2>&1; then
            echo -e "${GREEN}[INFO] ✅ Dependencies installiert: ${missing_core[*]}${NC}"
        else
            echo -e "${RED}[ERROR] ❌ Installation fehlgeschlagen${NC}"
            echo -e "${YELLOW}[HINT] Versuche: pip install ${missing_core[*]}${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}[INFO] ✅ Alle Dependencies vorhanden${NC}"
    fi
}

# =============================================================================
# PORT CHECK
# =============================================================================

check_port() {
    echo -e "${YELLOW}[INFO] Prüfe Port $PORT...${NC}"

    if lsof -i :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}[ERROR] ❌ Port $PORT bereits belegt${NC}"
        lsof -i :$PORT
        exit 1
    fi

    echo -e "${GREEN}[INFO] ✅ Port $PORT ist frei${NC}"
}

# =============================================================================
# SERVICE START
# =============================================================================

start_service() {
    echo -e "${YELLOW}[INFO] Starte $SERVICE_NAME...${NC}"

    # Check if already running
    if [ -f "$PID_FILE" ]; then
        local old_pid
        old_pid=$(cat "$PID_FILE")

        if kill -0 "$old_pid" 2>/dev/null; then
            echo -e "${YELLOW}[WARNING] Service läuft bereits (PID: $old_pid)${NC}"
            return 0
        else
            echo -e "${YELLOW}[INFO] Entferne veraltete PID-Datei${NC}"
            rm -f "$PID_FILE"
        fi
    fi

    # Ensure logs dir exists
    mkdir -p "$(dirname "$LOG_FILE")"

    # Start service in background
    cd "$PROJECT_DIR"
    nohup python3 "$MAIN_SCRIPT" > "$LOG_FILE" 2>&1 &
    local pid=$!

    # Save PID
    echo "$pid" > "$PID_FILE"

    echo -e "${GREEN}[INFO] ✅ Service gestartet (PID: $pid)${NC}"

    # Wait for startup
    echo -e "${YELLOW}[INFO] Warte auf Service-Initialisierung...${NC}"
    sleep 3
}

# =============================================================================
# HEALTH CHECK
# =============================================================================

verify_health() {
    echo -e "${YELLOW}[INFO] Führe Health-Check aus...${NC}"

    local max_attempts=5
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
            local health_response
            health_response=$(curl -s "$HEALTH_ENDPOINT" | jq . 2>/dev/null || echo "{}")

            echo -e "${GREEN}[INFO] ✅ Health-Check erfolgreich${NC}"
            echo -e "${GREEN}Health response:${NC}"
            echo "$health_response" | jq .

            return 0
        fi

        echo -e "${YELLOW}[INFO] Versuch $attempt/$max_attempts fehlgeschlagen, warte...${NC}"
        sleep 2
        ((attempt++))
    done

    echo -e "${RED}[ERROR] ❌ Health-Check fehlgeschlagen nach $max_attempts Versuchen${NC}"
    echo -e "${YELLOW}[HINT] Prüfe Logs: tail -f $LOG_FILE${NC}"

    return 1
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    echo "========================================="
    echo "  opena16 - Shop Management Agent (shopp)"
    echo "  Port: $PORT"
    echo "========================================="
    echo ""

    check_dependencies
    check_port
    start_service
    verify_health

    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}  $SERVICE_NAME erfolgreich gestartet${NC}"
    echo -e "${GREEN}=========================================${NC}"
    echo ""
    echo -e "${GREEN}PID:${NC}        $(cat "$PID_FILE")"
    echo -e "${GREEN}Port:${NC}       $PORT"
    echo -e "${GREEN}Logs:${NC}       $LOG_FILE"
    echo -e "${GREEN}Health:${NC}     $HEALTH_ENDPOINT"
    echo ""
    echo -e "${YELLOW}Stop service:${NC}  ./bin/stop_opena16.sh"
    echo -e "${YELLOW}View logs:${NC}     tail -f $LOG_FILE"
    echo ""
}

main "$@"
