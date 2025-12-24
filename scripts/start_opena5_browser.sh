#!/usr/bin/env bash
set -euo pipefail

# Start opena5_Browser agent
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJROOT="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"

# Activate venv
if [ -f "$PROJROOT/1.opena1&2_portier/venv313/bin/activate" ]; then
    source "$PROJROOT/1.opena1&2_portier/venv313/bin/activate"
fi

# Load token
TOKEN=$(cat "$PROJROOT/.env" 2>/dev/null | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2 || echo "MEIN_SUPER_TOKEN_123")

echo "🚀 Starting opena5_Browser on port 12353..."

# Stop any existing process
pkill -f "main_opena5_browser.py" || true
sleep 1

# Start in background
nohup python3 main_opena5_browser.py > logs/opena5_browser.nohup.log 2>&1 &
PID=$!

echo "✅ Started with PID $PID"
sleep 2

# Health check
echo "🏥 Health check..."
for i in {1..5}; do
    if curl -s http://127.0.0.1:12353/health | jq . > /dev/null 2>&1; then
        echo "✅ Service is healthy"
        break
    fi
    echo "⏳ Waiting... ($i/5)"
    sleep 1
done

# Register with dashboard
echo "📋 Registering with opena19 dashboard..."
curl -s -X POST http://127.0.0.1:12349/api/agent/register \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "agent_id": "opena5_browser",
        "endpoint": "http://127.0.0.1:12353"
    }' | jq . 2>/dev/null || echo "Registration sent"

echo "✅ opena5_Browser started and registered"
