#!/bin/bash
# Start Agent Server (Mini-Orchestrator) - opena_mini_orchestrator
# Port: 12350

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT/src/pkg"

# Umgebungsvariablen
export AGENT_SERVER_PORT=12350
export AGENT_ID="opena_mini_orchestrator"
export DASHBOARD_URL="http://127.0.0.1:12349"
export PYTHONPATH="$PROJECT_ROOT/src"

# Bearer Token aus .env laden
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -E '^BEARER_TOKEN=' "$PROJECT_ROOT/.env" | xargs)
fi

# PID-File
PID_FILE="$PROJECT_ROOT/.runtime/agent_server.pid"
LOG_FILE="$PROJECT_ROOT/logs/agent_server.nohup.log"

mkdir -p "$PROJECT_ROOT/.runtime"
mkdir -p "$PROJECT_ROOT/logs"

# Check ob läuft
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "❌ Agent Server bereits gestartet (PID: $OLD_PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Starten
echo "🚀 Starting Agent Server (Mini-Orchestrator)..."
echo "   Port: $AGENT_SERVER_PORT"
echo "   Agent ID: $AGENT_ID"
echo "   Dashboard: $DASHBOARD_URL"
echo "   Log: $LOG_FILE"

nohup python3 -m uvicorn agent_server:app \
    --host 0.0.0.0 \
    --port "$AGENT_SERVER_PORT" \
    --log-level info \
    > "$LOG_FILE" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"

# Warten auf Startup
sleep 2

if kill -0 "$PID" 2>/dev/null; then
    echo "✅ Agent Server gestartet (PID: $PID)"
    echo "   Health: curl http://127.0.0.1:$AGENT_SERVER_PORT/health"
else
    echo "❌ Agent Server konnte nicht gestartet werden"
    cat "$LOG_FILE" | tail -20
    exit 1
fi
