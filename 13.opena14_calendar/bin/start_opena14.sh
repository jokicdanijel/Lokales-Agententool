#!/usr/bin/env bash
#
# start_opena14.sh - Start opena14 (Calendar Management Agent)
# =============================================================
#
# Agent:   opena14
# Port:    12359
# Kürzel:  calp
# Status:  Production
#
# Dependencies:
#   - Python 3.13+
#   - FastAPI, uvicorn, pydantic
#   - icalendar, pytz (optional - für iCal-Support)
#
# Usage:
#   ./bin/start_opena14.sh
#
# Maintainer: ELION Team
# Last Update: 27. November 2025

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOGS_DIR="$PROJECT_ROOT/logs"
PID_FILE="$LOGS_DIR/opena14.pid"
NOHUP_LOG="$LOGS_DIR/opena14.nohup.log"
MAIN_SCRIPT="$PROJECT_ROOT/main_calendar_agent.py"
PORT=12359

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo "[INFO] $1"
}

log_error() {
    echo "[ERROR] $1" >&2
}

check_dependencies() {
    log_info "Prüfe Python-Dependencies..."
    
    # Check if imports work (no installation needed if already present)
    python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null && {
        log_info "✅ Core-Dependencies vorhanden"
    } || {
        log_info "⚠️  Core-Dependencies fehlen, versuche Installation..."
        
        pip3 install --break-system-packages fastapi uvicorn pydantic 2>/dev/null || {
            log_error "❌ pip install fehlgeschlagen (PEP 668)"
            
            python3 -c "import fastapi, uvicorn, pydantic" 2>/dev/null || {
                log_error "❌ Kritisch: FastAPI/uvicorn/pydantic nicht verfügbar"
                exit 1
            }
            
            log_info "✅ System-Pakete gefunden"
        }
    }
    
    # Check optional dependencies (icalendar, pytz)
    python3 -c "import icalendar, pytz" 2>/dev/null && {
        log_info "✅ iCalendar-Support verfügbar"
    } || {
        log_info "⚠️  iCalendar-Support deaktiviert (optional: pip install icalendar pytz)"
    }
}

check_port() {
    log_info "Prüfe Port $PORT Verfügbarkeit..."
    
    if lsof -i :$PORT >/dev/null 2>&1; then
        log_error "❌ Port $PORT bereits belegt!"
        lsof -i :$PORT
        exit 1
    fi
    
    log_info "✅ Port $PORT ist frei"
}

check_running() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" >/dev/null 2>&1; then
            log_error "❌ opena14 läuft bereits (PID: $PID)"
            exit 1
        else
            log_info "⚠️  Stale PID-File entfernt"
            rm -f "$PID_FILE"
        fi
    fi
}

start_service() {
    log_info "Starte opena14 (Port $PORT)..."
    
    mkdir -p "$LOGS_DIR"
    
    # Start in background with nohup
    nohup python3 "$MAIN_SCRIPT" > "$NOHUP_LOG" 2>&1 &
    SERVICE_PID=$!
    
    echo "$SERVICE_PID" > "$PID_FILE"
    log_info "✅ Service gestartet (PID: $SERVICE_PID)"
    log_info "📋 Logs: $NOHUP_LOG"
}

verify_health() {
    log_info "Warte auf Service-Start (5 Sekunden)..."
    sleep 5
    
    log_info "Prüfe Health-Endpoint..."
    
    HEALTH_URL="http://127.0.0.1:$PORT/health"
    
    if curl -s -f "$HEALTH_URL" >/dev/null 2>&1; then
        log_info "✅ Health-Check erfolgreich"
        curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || true
    else
        log_error "⚠️  Health-Check fehlgeschlagen (Service startet möglicherweise noch)"
        log_error "Prüfe Logs: tail -f $NOHUP_LOG"
    fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    log_info "=== opena14 (Calendar) START ==="
    
    check_running
    check_dependencies
    check_port
    start_service
    verify_health
    
    log_info "=== opena14 START ABGESCHLOSSEN ==="
    log_info ""
    log_info "Befehle:"
    log_info "  • Status: curl http://127.0.0.1:$PORT/health | jq ."
    log_info "  • Logs:   tail -f $NOHUP_LOG"
    log_info "  • Stopp:  ./bin/stop_opena14.sh"
}

main "$@"
