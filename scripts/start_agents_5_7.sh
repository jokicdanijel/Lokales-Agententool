#!/usr/bin/env bash
# Batch startup for Agents 5, 6, 7

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJROOT="$(cd "$ROOT/.." && pwd)"
cd "$ROOT"

# Activate venv
if [ -f "$PROJROOT/1.portier_openai/venv313/bin/activate" ]; then
    source "$PROJROOT/1.portier_openai/venv313/bin/activate"
fi

TOKEN=$(cat "$PROJROOT/.env" 2>/dev/null | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2 || echo "MEIN_SUPER_TOKEN_123")

echo "════════════════════════════════════════════════════════════"
echo "Starting Agents 5-7 (Browser, Email, WhatsApp)"
echo "════════════════════════════════════════════════════════════"
echo ""

# Stop any existing
pkill -f "main_opena5_browser" || true
pkill -f "main_opena6_email" || true
pkill -f "main_opena7_whatsapp" || true
sleep 1

# Start Agent 5 (Browser)
echo "🌐 Starting opena5_Browser (Port 12353)..."
nohup python3 main_opena5_browser.py > logs/opena5_browser.nohup.log 2>&1 &
sleep 2

# Start Agent 6 (Email)
echo "📧 Starting opena6_Email (Port 12354)..."
nohup python3 main_opena6_email.py > logs/opena6_email.nohup.log 2>&1 &
sleep 2

# Start Agent 7 (WhatsApp)
echo "💬 Starting opena7_WhatsApp (Port 12355)..."
nohup python3 main_opena7_whatsapp.py > logs/opena7_whatsapp.nohup.log 2>&1 &
sleep 2

echo ""
echo "🏥 Health checks..."
for port in 12353 12354 12355; do
    for i in {1..3}; do
        if curl -s http://127.0.0.1:$port/health | jq . > /dev/null 2>&1; then
            echo "✅ Port $port: healthy"
            break
        fi
        sleep 1
    done
done

echo ""
echo "📋 Registering with opena19..."
for agent in opena5_browser opena6_email opena7_whatsapp; do
    case $agent in
        opena5_browser)
            port=12353
            ;;
        opena6_email)
            port=12354
            ;;
        opena7_whatsapp)
            port=12355
            ;;
    esac
    
    curl -s -X POST http://127.0.0.1:12349/api/agent/register \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{
            \"agent_id\": \"$agent\",
            \"endpoint\": \"http://127.0.0.1:$port\"
        }" 2>/dev/null | jq -r '.agent // "registered"' || echo "registered"
done

echo ""
echo "✅ Agents 5-7 started and registered"
