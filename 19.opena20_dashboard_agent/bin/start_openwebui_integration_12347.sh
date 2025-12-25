#!/bin/bash
#
# Start OpenWebUI Integration Server - Port 12347
# HYPER-DASHBOARD 3.0 PORTIER Enterprise (Optimized)
#
# Usage: ./bin/start_openwebui_integration_12347.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="openwebui_integration_12347"
PORT=12347
PID_FILE="$PROJECT_DIR/.runtime/${SERVICE_NAME}.pid"
LOG_FILE="$PROJECT_DIR/logs/${SERVICE_NAME}.nohup.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"; }
info() { echo -e "${BLUE}[$(date '+%H:%M:%S')] INFO:${NC} $1"; }

# Ensure directories exist
mkdir -p "$PROJECT_DIR/.runtime" "$PROJECT_DIR/logs"

log "🚀 Starting OpenWebUI Integration Server (Port 12347)..."

# Check if port is already in use
if lsof -i :$PORT >/dev/null 2>&1; then
    warn "Port $PORT ist bereits belegt"

    # Check if it's our service
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" >/dev/null 2>&1; then
            log "✅ Service läuft bereits (PID: $PID)"
            exit 0
        else
            warn "Stale PID file gefunden, lösche..."
            rm -f "$PID_FILE"
        fi
    fi

    info "Stoppe Prozess auf Port $PORT..."
    pkill -f "openwebui_integration_12347.py" 2>/dev/null || true
    sleep 2
fi

# Check dependencies
if ! command -v python3 >/dev/null; then
    error "Python3 nicht gefunden"
    exit 1
fi

# Check if service file exists
SERVICE_FILE="$PROJECT_DIR/openwebui_integration_12347.py"
if [[ ! -f "$SERVICE_FILE" ]]; then
    error "Service file nicht gefunden: $SERVICE_FILE"
    exit 1
fi

# Check Python dependencies
log "🔍 Checking Python dependencies..."
python3 -c "import fastapi, aiohttp, uvicorn, pydantic" 2>/dev/null || {
    error "Fehlende Python-Dependencies. Installiere mit:"
    echo "pip install fastapi aiohttp uvicorn pydantic"
    exit 1
}

# Verify core services are running
log "🔍 Checking core services..."

# Check kordp (Port 12346)
if ! curl -s "http://127.0.0.1:12346/health" >/dev/null 2>&1; then
    warn "kordp Gateway (Port 12346) nicht erreichbar"
    info "Starte kordp falls verfügbar..."
fi

# Check HYPER-DASHBOARD (Port 12349)
if ! curl -s "http://127.0.0.1:12349/health" >/dev/null 2>&1; then
    warn "HYPER-DASHBOARD (Port 12349) nicht erreichbar"
    info "Dashboard sollte gestartet werden"
fi

# Start service
cd "$PROJECT_DIR"

log "▶️  Starting OpenWebUI Integration service..."
nohup python3 "$SERVICE_FILE" > "$LOG_FILE" 2>&1 &
PID=$!

# Save PID
echo "$PID" > "$PID_FILE"

# Wait for service to start
log "⏳ Waiting for service to start..."
for i in {1..20}; do
    if curl -s "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
        log "✅ OpenWebUI Integration Server started successfully!"
        info "📡 Port: $PORT"
        info "📄 PID: $PID"
        info "📋 Logs: $LOG_FILE"
        info "🔗 Health: http://127.0.0.1:$PORT/health"

        # Show service info
        echo ""
        info "🎯 Available Endpoints:"
        echo "  📊 System Status: http://127.0.0.1:$PORT/api/status/system"
        echo "  🚪 kordp Status: http://127.0.0.1:$PORT/api/status/kordp"
        echo "  🎯 Dashboard Status: http://127.0.0.1:$PORT/api/status/dashboard"
        echo "  💬 Chat (POST): http://127.0.0.1:$PORT/api/chat"
        echo "  🔄 Workflow (POST): http://127.0.0.1:$PORT/api/workflow/execute"
        echo "  🧪 Integration Test: http://127.0.0.1:$PORT/api/system/integration-test"

        # Test integration
        echo ""
        log "🧪 Running integration test..."
        if INTEGRATION_RESULT=$(curl -s "http://127.0.0.1:$PORT/api/system/integration-test" 2>/dev/null); then
            OVERALL_STATUS=$(echo "$INTEGRATION_RESULT" | jq -r '.overall_status' 2>/dev/null || echo "unknown")

            if [[ "$OVERALL_STATUS" == "ok" ]]; then
                log "✅ Integration test passed - all core services online"
            elif [[ "$OVERALL_STATUS" == "partial" ]]; then
                warn "⚠️ Integration test partial - some services offline"
            else
                warn "❓ Integration test result unclear"
            fi
        else
            warn "Integration test konnte nicht ausgeführt werden"
        fi

        # Port mapping info
        echo ""
        info "🗺️ Port Mapping:"
        echo "  12346: kordp Gateway"
        echo "  12347: OpenWebUI Integration (this service)"
        echo "  12349: HYPER-DASHBOARD 3.0"
        echo "  8080:  OpenWebUI UI (external)"

        exit 0
    fi

    if ! ps -p "$PID" >/dev/null 2>&1; then
        error "Service konnte nicht gestartet werden (Prozess beendet)"
        error "Logs: tail -20 '$LOG_FILE'"
        exit 1
    fi

    sleep 1
done

error "Service konnte nicht innerhalb von 20 Sekunden gestartet werden"
error "Logs: tail -20 '$LOG_FILE'"
exit 1
