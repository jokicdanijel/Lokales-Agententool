#!/usr/bin/env bash
# =============================================================================
# opena15 - HTML Creator Agent Start Script
# Port: 12360
# Kürzel: htmlp
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
PID_FILE="$PROJECT_DIR/logs/opena15.pid"
LOG_FILE="$PROJECT_DIR/logs/opena15.nohup.log"
MAIN_SCRIPT="$PROJECT_DIR/backend/app.py"

# Config
PORT=12360
SERVICE_NAME="opena15"
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

    # Template & HTML processing dependencies
    local html_deps=("jinja2" "bs4")
    local missing_html=()

    for dep in "${html_deps[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            missing_html+=("$dep")
        fi
    done

    # Install missing dependencies
    if [ ${#missing_core[@]} -ne 0 ] || [ ${#missing_html[@]} -ne 0 ]; then
        echo -e "${YELLOW}[INFO] Installiere fehlende Dependencies...${NC}"

        local all_missing=("${missing_core[@]}" "${missing_html[@]}")

        # Map bs4 -> beautifulsoup4
        local install_pkgs=()
        for pkg in "${all_missing[@]}"; do
            if [ "$pkg" == "bs4" ]; then
                install_pkgs+=("beautifulsoup4")
            else
                install_pkgs+=("$pkg")
            fi
        done

        # Try installing
        if pip install --break-system-packages "${install_pkgs[@]}" > /dev/null 2>&1; then
            echo -e "${GREEN}[INFO] ✅ Dependencies installiert: ${install_pkgs[*]}${NC}"
        else
            echo -e "${RED}[ERROR] ❌ Installation fehlgeschlagen${NC}"
            echo -e "${YELLOW}[HINT] Versuche: pip install ${install_pkgs[*]}${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}[INFO] ✅ Alle Dependencies vorhanden${NC}"
    fi

    # Check optional lxml (better HTML parsing)
    if ! python3 -c "import lxml" 2>/dev/null; then
        echo -e "${YELLOW}[INFO] ⚠️  Optional: lxml nicht installiert (besseres HTML-Parsing)${NC}"
        echo -e "${YELLOW}[HINT] pip install --break-system-packages lxml${NC}"
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
    echo "  opena15 - HTML Creator Agent (htmlp)"
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
    echo -e "${YELLOW}Stop service:${NC}  ./bin/stop_opena15.sh"
    echo -e "${YELLOW}View logs:${NC}     tail -f $LOG_FILE"
    echo ""
}

main "$@"
