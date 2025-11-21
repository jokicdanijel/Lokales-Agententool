#!/bin/bash
# Start Data Deletion Callback Service for Meta WhatsApp Compliance

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔒 Starting Meta Data Deletion Callback Service..."

cd "$PROJECT_ROOT"

# Check if port is already in use
PORT=12370
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT already in use"
    exit 1
fi

# Start data deletion service
nohup ./.venv/bin/python 8.opena8_whatsapp/app/data_deletion.py > logs/data_deletion.log 2>&1 &

sleep 2

# Health check
echo "🔍 Health Check..."
curl -s http://127.0.0.1:$PORT/health | jq . || echo "❌ Service not responding"

echo "✅ Data Deletion Callback running on port $PORT"
echo "📋 Callback URL for Meta: https://YOUR_DOMAIN:$PORT/data-deletion-callback"
echo "📋 Status URL: https://YOUR_DOMAIN:$PORT/deletion-status?code=CODE"