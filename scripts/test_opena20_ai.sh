#!/usr/bin/env bash
# ELION Hyper-Dashboard 2.0 - opena20 AI Chat Test
# Testet die OpenAI-Integration des Dashboard-Backends

set -Eeuo pipefail

PROJECT_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
cd "$PROJECT_ROOT"

# Lade Token aus .env
if [ ! -f .env ]; then
    echo "❌ ERROR: .env nicht gefunden"
    exit 1
fi

BEARER_TOKEN=$(grep BEARER_TOKEN .env | cut -d= -f2)

if [ -z "$BEARER_TOKEN" ]; then
    echo "❌ ERROR: BEARER_TOKEN nicht in .env gesetzt"
    exit 1
fi

echo "🧪 Testing opena20 AI Chat Integration"
echo "========================================"
echo ""

# 1. Health-Check
echo "1️⃣ Health-Check Dashboard..."
HEALTH=$(curl -sf http://127.0.0.1:12349/health)

if [ $? -ne 0 ]; then
    echo "❌ Dashboard nicht erreichbar (Port 12349)"
    echo "   Starte mit: bin/ops.sh start"
    exit 1
fi

echo "✅ Dashboard healthy"

# Parse OpenAI-Status
OPENAI_KEY_PRESENT=$(echo "$HEALTH" | jq -r '.openai_key_present // false')
OPENAI_CLIENT_READY=$(echo "$HEALTH" | jq -r '.openai_client_ready // false')

echo "   OpenAI Key present: $OPENAI_KEY_PRESENT"
echo "   OpenAI Client ready: $OPENAI_CLIENT_READY"
echo ""

if [ "$OPENAI_KEY_PRESENT" != "true" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY_OPENA20 nicht in .env gesetzt"
    echo "   AI Chat wird nicht funktionieren"
fi

if [ "$OPENAI_CLIENT_READY" != "true" ]; then
    echo "⚠️  WARNING: OpenAI Client nicht initialisiert"
    echo "   Installiere: pip install openai"
    exit 1
fi

# 2. AI Chat Test (Model: gpt-3.5-turbo, KEINE Token-Begrenzung)
echo "2️⃣ AI Chat Request..."
RESPONSE=$(curl -sf -X POST http://127.0.0.1:12349/api/ai/chat \
    -H "Authorization: Bearer $BEARER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "message": "Was ist 2+2?",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7
    }')

if [ $? -ne 0 ]; then
    echo "❌ AI Chat Request fehlgeschlagen"
    exit 1
fi

echo "✅ AI Chat erfolgreich"
echo ""

# Parse Response
MESSAGE=$(echo "$RESPONSE" | jq -r '.message')
ANSWER=$(echo "$RESPONSE" | jq -r '.response')
MODEL=$(echo "$RESPONSE" | jq -r '.model')
TOKENS=$(echo "$RESPONSE" | jq -r '.usage.total_tokens')

echo "📊 Test-Ergebnis:"
echo "   Frage:  $MESSAGE"
echo "   Antwort: $ANSWER"
echo "   Model:   $MODEL"
echo "   Tokens:  $TOKENS"
echo ""

# 3. Validation
if [ -n "$ANSWER" ] && [ "$ANSWER" != "null" ]; then
    echo "✅ TEST PASSED: OpenAI-Integration funktioniert"
    echo ""
    echo "🎉 opena20 AI Chat bereit für Produktion!"
    exit 0
else
    echo "❌ TEST FAILED: Keine gültige Antwort erhalten"
    exit 1
fi
