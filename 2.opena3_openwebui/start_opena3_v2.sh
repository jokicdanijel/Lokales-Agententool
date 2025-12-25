#!/bin/bash
"""
opena3 V2 Start Script
Startet den PORTIER 3.0 zertifizierten OpenWebUI Agent
"""

# Verzeichnis-Setup
cd "$(dirname "$0")"
PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui"

# Logs-Verzeichnis
mkdir -p "$PROJECT_ROOT/logs"

# PID-File Management
PID_FILE="$PROJECT_ROOT/logs/opena3_v2.pid"

# Funktion: Service stoppen
stop_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "🛑 Stopping opena3 V2 (PID: $PID)"
            kill $PID
            sleep 2
            # Force kill falls nötig
            if ps -p $PID > /dev/null 2>&1; then
                kill -9 $PID
                echo "⚡ Force killed opena3 V2"
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

# Funktion: Service starten
start_service() {
    echo "🚀 Starting opena3 V2 (PORTIER 3.0 Certified)"
    echo "📍 Port: 12347"
    echo "🔗 OpenWebUI: ${OPENWEBUI_URL:-http://127.0.0.1:8080}"

    # Aktiviere Virtual Environment falls vorhanden
    if [ -d "$PROJECT_ROOT/.venv" ]; then
        source "$PROJECT_ROOT/.venv/bin/activate"
        echo "✓ Virtual environment activated"
    fi

    # Starte Service
    cd "$PROJECT_ROOT"
    nohup python3 opena3_terminal_v2.py > logs/opena3_v2.nohup.log 2>&1 &

    # PID speichern
    echo $! > "$PID_FILE"

    echo "✓ opena3 V2 started (PID: $(cat $PID_FILE))"
    echo "📋 Logs: $PROJECT_ROOT/logs/opena3_v2.nohup.log"

    # Health Check
    sleep 3
    if curl -s --connect-timeout 3 "http://127.0.0.1:12347/health" > /dev/null; then
        echo "✅ Health check passed"
        echo "🌐 Service available: http://127.0.0.1:12347"
    else
        echo "⚠️  Health check failed - check logs"
    fi
}

# Funktion: Status anzeigen
show_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ opena3 V2 running (PID: $PID)"

            # API Health Check
            if curl -s --connect-timeout 2 "http://127.0.0.1:12347/health" | jq . > /dev/null 2>&1; then
                echo "✅ API responding"
                curl -s "http://127.0.0.1:12347/health" | jq '.status, .openwebui_status, .uptime_seconds'
            else
                echo "❌ API not responding"
            fi
        else
            echo "❌ opena3 V2 not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        echo "❌ opena3 V2 not running"
    fi
}

# Command Parsing
case "${1:-start}" in
    start)
        stop_service
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        stop_service
        sleep 1
        start_service
        ;;
    status)
        show_status
        ;;
    logs)
        if [ -f "$PROJECT_ROOT/logs/opena3_v2.nohup.log" ]; then
            tail -f "$PROJECT_ROOT/logs/opena3_v2.nohup.log"
        else
            echo "❌ Log file not found"
        fi
        ;;
    test)
        echo "🧪 Testing opena3 V2 endpoints..."

        # Health Test
        echo "1. Health Check:"
        curl -s "http://127.0.0.1:12347/health" | jq . || echo "❌ Failed"

        # Native Chat Test (needs Bearer token)
        echo -e "\n2. Native Chat Test:"
        if [ -n "$BEARER_TOKEN" ]; then
            curl -s -X POST "http://127.0.0.1:12347/native" \
                -H "Authorization: Bearer $BEARER_TOKEN" \
                -H "Content-Type: application/json" \
                -d '{"prompt":"Hello, test message"}' | jq . || echo "❌ Failed"
        else
            echo "⚠️  BEARER_TOKEN not set - skipping auth tests"
        fi

        # Self-Test
        echo -e "\n3. Self-Test:"
        if [ -n "$BEARER_TOKEN" ]; then
            curl -s "http://127.0.0.1:12347/selftest?token=$BEARER_TOKEN" | jq . || echo "❌ Failed"
        else
            echo "⚠️  BEARER_TOKEN not set - skipping self-test"
        fi
        ;;
    help|--help|-h)
        echo "opena3 V2 Control Script"
        echo "========================"
        echo "Usage: $0 {start|stop|restart|status|logs|test|help}"
        echo ""
        echo "Commands:"
        echo "  start   - Start opena3 V2 service"
        echo "  stop    - Stop opena3 V2 service"
        echo "  restart - Restart opena3 V2 service"
        echo "  status  - Show service status + health"
        echo "  logs    - Tail service logs"
        echo "  test    - Run endpoint tests"
        echo "  help    - Show this help"
        echo ""
        echo "Environment Variables:"
        echo "  BEARER_TOKEN     - API authentication token"
        echo "  OPENWEBUI_URL    - OpenWebUI base URL (default: http://127.0.0.1:8080)"
        echo "  DEV_MODE         - Enable development mode (default: false)"
        echo "  MOCK_MODE        - Enable mock mode (default: false)"
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
