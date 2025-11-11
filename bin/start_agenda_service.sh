#!/usr/bin/env bash
# bin/start_agenda_service.sh — Start Agenda Pages API Service
# Port: 12399
# Usage: bash bin/start_agenda_service.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_PATH="$ROOT/src/services"
LOGS_DIR="$ROOT/logs"

mkdir -p "$LOGS_DIR"

echo "🚀 Starting Agenda Pages API Service (port 12399)..."

# Check if already running
if lsof -i :12399 > /dev/null 2>&1; then
    echo "⚠️  Port 12399 already in use (service may be running)"
    lsof -i :12399
    exit 0
fi

# Start service
cd "$SERVICE_PATH"
nohup python3 agenda_api.py > "$LOGS_DIR/agenda_api.nohup.log" 2>&1 &
PID=$!

sleep 1

if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Agenda API started (PID: $PID)"
    echo "   Port: 12399"
    echo "   Logs: $LOGS_DIR/agenda_api.nohup.log"
    echo ""
    echo "Test Login:"
    echo "  curl -X POST http://127.0.0.1:12399/login \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"username\":\"admin\",\"password\":\"250886\"}'"
else
    echo "❌ Failed to start Agenda API"
    exit 1
fi
