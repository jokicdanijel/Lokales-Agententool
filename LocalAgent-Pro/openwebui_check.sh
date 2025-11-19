#!/usr/bin/env bash
# OpenWebUI Quick Check - Alle wichtigen Endpoints testen
set -e

BASE="http://127.0.0.1:8001"
API_BASE="${BASE}/v1"

echo "================================"
echo "🔍 OpenWebUI Backend Check"
echo "================================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check (${BASE}/health)"
if curl -s "${BASE}/health" | python3 -m json.tool 2>/dev/null; then
    echo "✅ Health OK"
else
    echo "❌ Health Fehler"
fi
echo ""

# 2. Models Check
echo "2️⃣ Models Check (${API_BASE}/models)"
if curl -s "${API_BASE}/models" | python3 -m json.tool 2>/dev/null; then
    echo "✅ Models OK"
else
    echo "❌ Models Fehler"
fi
echo ""

# 3. Chat Endpoint Check
echo "3️⃣ Chat Endpoint (${API_BASE}/chat/completions)"
if curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"messages":[{"role":"user","content":"Hallo LocalAgent-Pro"}]}' \
    "${API_BASE}/chat/completions" | python3 -m json.tool 2>/dev/null; then
    echo "✅ Chat OK"
else
    echo "❌ Chat Fehler"
fi
echo ""

# 4. OpenWebUI UI Check (optional)
echo "4️⃣ OpenWebUI UI Check (Port 3000)"
if curl -s -I "http://127.0.0.1:3000" 2>/dev/null | head -n 1 | grep -q "200\|302"; then
    echo "✅ OpenWebUI UI läuft auf Port 3000"
else
    echo "⚠️ OpenWebUI UI nicht erreichbar auf Port 3000"
fi
echo ""

# 5. Port Check
echo "5️⃣ Port Status"
if ss -tlnp 2>/dev/null | grep -q ":8001"; then
    echo "✅ Backend läuft auf Port 8001"
else
    echo "❌ Port 8001 nicht aktiv - Server starten!"
fi

if ss -tlnp 2>/dev/null | grep -q ":3000"; then
    echo "✅ OpenWebUI UI läuft auf Port 3000"
else
    echo "⚠️ Port 3000 nicht aktiv - OpenWebUI starten?"
fi
echo ""

echo "================================"
echo "📝 Zusammenfassung"
echo "================================"
echo "Backend API: ${API_BASE}"
echo "OpenWebUI UI: http://127.0.0.1:3000"
echo ""
echo "💡 In OpenWebUI eintragen:"
echo "   API Base URL: ${API_BASE}"
echo "================================"
