#!/bin/bash
#
# Start Browser Agent Tool Server
# HTTP-Server für OpenWebUI Integration
#
# Der Tool Server läuft auf Port 8765 und stellt die Browser-Automation
# als OpenWebUI-kompatibles Tool bereit.
#
# Verwendung:
#   bash start_tool_server.sh
#   bash start_tool_server.sh --port 9000
#   bash start_tool_server.sh --host 0.0.0.0 --port 8765
#

# ============================================================================
# SETUP
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_SERVER="${SCRIPT_DIR}/tool_server.py"
LOG_DIR="${SCRIPT_DIR}/logs"
LOG_FILE="${LOG_DIR}/tool_server.log"
PID_FILE="${SCRIPT_DIR}/.tool_server.pid"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8765}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            cat << EOF
Browser Agent Tool Server - Starter

Verwendung:
  bash start_tool_server.sh [OPTIONEN]

Optionen:
  --host HOST    Bind address (default: 0.0.0.0)
  --port PORT    Port (default: 8765)
  --help         Diese Hilfe zeigen

Beispiele:
  bash start_tool_server.sh
  bash start_tool_server.sh --port 9000
  bash start_tool_server.sh --host 127.0.0.1 --port 8765

OpenWebUI Integration:
  1. Öffne: http://192.168.0.70:3000/admin
  2. Settings → External Tools
  3. URL: http://192.168.0.70:${PORT}/manifest
  4. Speichern und testen

Dashboard:
  http://localhost:${PORT}

EOF
            exit 0
            ;;
        *)
            echo "❌ Unbekannte Option: $1"
            exit 1
            ;;
    esac
done

# ============================================================================
# SETUP DIRECTORIES
# ============================================================================

mkdir -p "$LOG_DIR"

# ============================================================================
# FUNCTIONS
# ============================================================================

log_info() {
    echo "ℹ️  $1"
}

log_success() {
    echo "✅ $1"
}

log_error() {
    echo "❌ $1"
}

# ============================================================================
# STARTUP
# ============================================================================

log_info "Browser Agent Tool Server - Starter"
log_info "===================================="
log_info ""
log_info "Konfiguration:"
log_info "  Host: ${HOST}"
log_info "  Port: ${PORT}"
log_info "  Log: ${LOG_FILE}"
log_info ""

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        log_error "Tool Server läuft bereits (PID: $OLD_PID)"
        log_info "Zum Stoppen: kill $OLD_PID"
        exit 1
    fi
fi

# Check if port is available
if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    log_error "Port ${PORT} ist bereits in Verwendung"
    exit 1
fi

# Start server
log_info "Starte Tool Server..."
echo ""

python3 "$TOOL_SERVER" --host "$HOST" --port "$PORT" 2>&1 | tee -a "$LOG_FILE" &
SERVER_PID=$!

# Save PID
echo "$SERVER_PID" > "$PID_FILE"

log_success "Tool Server gestartet (PID: $SERVER_PID)"
log_info ""
log_info "Dashboard verfügbar unter:"
log_info "  http://localhost:${PORT}"
log_info ""
log_info "OpenWebUI Integration:"
log_info "  1. Öffne: http://192.168.0.70:3000/admin"
log_info "  2. Settings → External Tools"
log_info "  3. URL: http://192.168.0.70:${PORT}/manifest"
log_info "  4. Speichern und testen"
log_info ""
log_info "Logs: tail -f ${LOG_FILE}"
log_info ""

# Wait for server to start
sleep 2

# Check if server started successfully
if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    log_success "Server läuft erfolgreich"

    # Check health
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        log_success "Health Check erfolgreich"
    else
        log_error "Health Check fehlgeschlagen"
    fi
else
    log_error "Server konnte nicht gestartet werden"
    exit 1
fi

# Keep running
wait $SERVER_PID
