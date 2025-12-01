#!/bin/bash
# Start Agent17 (Pool Service, Port 12366)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

cd "$SCRIPT_DIR"

# ENV-Variablen
export SERVICE_NAME="agent17"
export PROGRAM_TARGET="agent17p"
export PORT=12366
export PYTHONPATH="$PROJECT_ROOT/src"

# Bearer Token aus .env laden
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -E '^BEARER_TOKEN=' "$PROJECT_ROOT/.env" | xargs)
fi

# PID & Log
PID_FILE="$PROJECT_ROOT/.runtime/agent17.pid"
LOG_FILE="$PROJECT_ROOT/logs/agent17.nohup.log"

mkdir -p "$PROJECT_ROOT/.runtime"
mkdir -p "$PROJECT_ROOT/logs"

# Check ob läuft
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "❌ Agent17 bereits gestartet (PID: $OLD_PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Starten
echo "🚀 Starting Agent17 ($PROGRAM_TARGET) on port $PORT..."

nohup python3 main.py > "$LOG_FILE" 2>&1 &

PID=$!
echo "$PID" > "$PID_FILE"

sleep 1

if kill -0 "$PID" 2>/dev/null; then
    echo "✅ Agent17 gestartet (PID: $PID)"
    echo "   Health: curl http://127.0.0.1:$PORT/health"
else
    echo "❌ Agent17 konnte nicht gestartet werden"
    cat "$LOG_FILE" | tail -10
    exit 1
fi
