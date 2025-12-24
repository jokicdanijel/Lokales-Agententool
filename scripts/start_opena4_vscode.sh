#!/usr/bin/env bash
set -euo pipefail

# Start opena4_VSCode agent
# Usage: ./bin/start_opena4_vscode.sh

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJROOT="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"

# Activate venv
if [ -f "$PROJROOT/1.opena1&2_portier/venv313/bin/activate" ]; then
    source "$PROJROOT/1.opena1&2_portier/venv313/bin/activate"
fi

# Load token
TOKEN=$(cat "$PROJROOT/.env" 2>/dev/null | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2 || echo "MEIN_SUPER_TOKEN_123")

echo "🚀 Starting opena4_VSCode on port 12352..."

# Stop any existing process
pkill -f "main_opena4_vscode.py" || true
sleep 1

# Start in background
nohup python3 main_opena4_vscode.py > logs/opena4_vscode.nohup.log 2>&1 &
PID=$!

echo "✅ Started with PID $PID"

# Wait for service to start
sleep 2

# Health check
echo "🏥 Health check..."
for i in {1..5}; do
    if curl -s http://127.0.0.1:12352/health | jq . > /dev/null 2>&1; then
        echo "✅ Service is healthy"
        break
    fi
    echo "⏳ Waiting... ($i/5)"
    sleep 1
done

# Register with dashboard
echo "📋 Registering with opena19 dashboard..."
RESPONSE=$(curl -X POST http://127.0.0.1:12349/api/agent/register \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{
        "agent_id": "opena4_vscode",
        "endpoint": "http://127.0.0.1:12352"
    }' 2>/dev/null || echo '{"detail":"registration_failed"}')

if echo "$RESPONSE" | jq . > /dev/null 2>&1; then
    echo "✅ Registered: $RESPONSE" | jq .
else
    echo "⚠️ Registration response: $RESPONSE"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "opena4_VSCode Status"
echo "════════════════════════════════════════════════════════════"
curl -s http://127.0.0.1:12352/status \
    -H "Authorization: Bearer $TOKEN" | jq . 2>/dev/null || echo "Status unavailable"

echo ""
echo "Log file: $ROOT/logs/opena4_vscode.nohup.log"
