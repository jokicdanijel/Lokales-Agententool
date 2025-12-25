#!/bin/bash
# Start opena9 Telephone Agent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📞 Starting opena9 Telephone Agent..."

cd "$PROJECT_ROOT"

# Check if port is already in use
PORT=12352
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT already in use"
    exit 1
fi

# Start telephone agent
nohup ./.venv/bin/python 8.opena9_telephone/main.py > logs/opena9.log 2>&1 &

sleep 2

# Health check
echo "🔍 Health Check..."
curl -s http://127.0.0.1:$PORT/health | jq . || echo "❌ Service not responding"

echo "✅ opena9 Telephone Agent running on port $PORT"
