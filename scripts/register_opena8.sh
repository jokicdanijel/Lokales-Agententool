#!/bin/bash
# Register opena8 (WhatsApp Agent) with opena1 coordinator

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT_NAME="opena8"
AGENT_PORT=12351
OPENA1_URL="http://127.0.0.1:12344"
OPENA2_URL="http://127.0.0.1:12345"

echo "🔧 [opena8] Registering WhatsApp Agent..."

# 1. Health check: opena1
echo "  → Checking opena1 (:12344)..."
if ! curl -s "$OPENA1_URL/health" > /dev/null 2>&1; then
    echo "❌ opena1 not responding on $OPENA1_URL"
    echo "   Start with: bin/ops.sh start"
    exit 1
fi

# 2. Health check: opena2
echo "  → Checking opena2 (:12345)..."
if ! curl -s "$OPENA2_URL/health" > /dev/null 2>&1; then
    echo "❌ opena2 not responding on $OPENA2_URL"
    echo "   Start with: bin/ops.sh start"
    exit 1
fi

# 3. Start opena8 service (if not running)
echo "  → Starting opena8 (:$AGENT_PORT)..."
if ! curl -s "http://127.0.0.1:$AGENT_PORT/health" > /dev/null 2>&1; then
    cd "$ROOT"
    source .venv/bin/activate
    nohup python -m uvicorn 8.opena8_whatsapp.app.main:app --host 127.0.0.1 --port $AGENT_PORT > logs/opena8.nohup.log 2>&1 &
    OPENA8_PID=$!
    echo "    Started (PID: $OPENA8_PID). Waiting for health..."
    sleep 3

    if ! curl -s "http://127.0.0.1:$AGENT_PORT/health" > /dev/null 2>&1; then
        echo "❌ opena8 failed to start. Check logs/opena8.nohup.log"
        exit 1
    fi
else
    echo "    Already running ✅"
fi

# 4. Register route with opena1
echo "  → Registering route: $AGENT_NAME@$AGENT_PORT with opena1..."
REGISTER_RESPONSE=$(curl -s -X POST "$OPENA1_URL/route/update" \
    -H "Content-Type: application/json" \
    -d "{
        \"agent_id\": \"$AGENT_NAME\",
        \"endpoint\": \"http://127.0.0.1:$AGENT_PORT\",
        \"component\": \"whatsapp\"
    }")

if echo "$REGISTER_RESPONSE" | grep -q "registered\|success\|ok"; then
    echo "    ✅ Route registered"
else
    echo "    ⚠️  Registration response: $REGISTER_RESPONSE"
fi

# 5. Verify health
echo "  → Verifying $AGENT_NAME health..."
HEALTH_RESPONSE=$(curl -s "http://127.0.0.1:$AGENT_PORT/health")
if echo "$HEALTH_RESPONSE" | grep -q "ok"; then
    echo "    ✅ Health: ok"
else
    echo "    ⚠️  Health: $(echo "$HEALTH_RESPONSE" | jq -r '.status // "unknown"')"
fi

echo ""
echo "✅ opena8 (WhatsApp Agent) registered successfully!"
echo ""
echo "📖 Next steps:"
echo "   1. Configure .env with Meta credentials:"
echo "      cp 8.opena8_whatsapp/.env.example 8.opena8_whatsapp/.env"
echo "      # Edit .env with your Meta Phone Number ID, Access Token, Webhook Secret"
echo ""
echo "   2. Set webhook URL in Meta App Dashboard:"
echo "      URL: https://your-domain.com:443/webhook"
echo "      Verify Token: (use META_WEBHOOK_VERIFY_TOKEN from .env)"
echo ""
echo "   3. Test incoming message:"
echo "      curl -X POST http://127.0.0.1:12351/webhook ..."
echo ""
echo "   4. Send test message:"
echo "      curl -X POST http://127.0.0.1:12351/send \\
echo "        -H 'Content-Type: application/json' \\
echo "        -d '{\"to_phone\": \"+49123456789\", \"body\": \"Test\"}'"
