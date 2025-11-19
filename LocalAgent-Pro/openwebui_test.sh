#!/usr/bin/env bash
set -euo pipefail

BASE="http://127.0.0.1:8001"

echo "═══════════════════════════════════════════════════════════════"
echo "  OPENWEBUI TEST: Backend-API prüfen (Port 8001)"
echo "═══════════════════════════════════════════════════════════════"
echo "Base-URL: $BASE"
echo

# Health prüfen
echo "──────────────────────────────────────────────────────────────"
echo "1) Health-Check"
echo "──────────────────────────────────────────────────────────────"
health=$(curl -sS "$BASE/health" || true)
if [ -z "$health" ]; then
  echo "❌ Fehler: Health-Endpoint antwortet nicht."
  exit 1
fi
if echo "$health" | python3 -m json.tool >/dev/null 2>&1; then
  echo "✅ Health-Response (JSON):"
  echo "$health" | python3 -m json.tool
  status=$(echo "$health" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status',''))")
  if [ "$status" != "ok" ]; then
    echo "⚠️  Warnung: Health-Status != ok (ist $status)"
    exit 2
  fi
  echo "✅ Status: OK"
else
  echo "❌ Fehler: Health liefert kein gültiges JSON."
  echo "$health"
  exit 1
fi
echo

# Modelle prüfen
echo "──────────────────────────────────────────────────────────────"
echo "2) Modelle (v1/models)"
echo "──────────────────────────────────────────────────────────────"
models=$(curl -sS "$BASE/v1/models" || true)
if echo "$models" | python3 -m json.tool >/dev/null 2>&1; then
  echo "✅ Models-Response (JSON):"
  echo "$models" | python3 -m json.tool
  model_count=$(echo "$models" | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d.get('data',[])))")
  echo "✅ Anzahl verfügbarer Modelle: $model_count"
else
  echo "❌ Fehler: Models-Endpoint liefert kein gültiges JSON."
  exit 1
fi
echo

# Chat-Endpunkt testen
echo "──────────────────────────────────────────────────────────────"
echo "3) Chat-Endpunkt testen"
echo "──────────────────────────────────────────────────────────────"
chat_req='{"messages":[{"role":"user","content":"Hallo LocalAgent-Pro"}]}'
chat_resp=$(curl -sS -X POST -H "Content-Type: application/json" -d "$chat_req" "$BASE/v1/chat/completions" || true)
if echo "$chat_resp" | python3 -m json.tool >/dev/null 2>&1; then
  echo "✅ Chat-Endpunkt-Response (JSON):"
  echo "$chat_resp" | python3 -m json.tool
  echo "✅ Chat-Endpunkt funktioniert"
else
  echo "❌ Fehler: Chat-Endpunkt liefert kein gültiges JSON."
  echo "$chat_resp"
  exit 1
fi
echo

# Test-Endpunkt prüfen
echo "──────────────────────────────────────────────────────────────"
echo "4) Test-Endpunkt prüfen"
echo "──────────────────────────────────────────────────────────────"
test_req='{"prompt": "Liste Verzeichnis . auf"}'
test_resp=$(curl -sS -X POST -H "Content-Type: application/json" -d "$test_req" "$BASE/test" || true)
if echo "$test_resp" | python3 -m json.tool >/dev/null 2>&1; then
  echo "✅ Test-Endpunkt-Response (JSON):"
  echo "$test_resp" | python3 -m json.tool
  echo "✅ Test-Endpunkt funktioniert"
else
  echo "❌ Fehler: Test-Endpunkt liefert kein gültiges JSON."
  echo "$test_resp"
  exit 1
fi
echo

# OpenWebUI UI prüfen
echo "──────────────────────────────────────────────────────────────"
echo "5) OpenWebUI UI prüfen (Port 3000)"
echo "──────────────────────────────────────────────────────────────"
if curl -sS --connect-timeout 2 http://127.0.0.1:3000 >/dev/null 2>&1; then
  echo "✅ OpenWebUI UI läuft auf Port 3000"
else
  echo "⚠️  OpenWebUI UI scheint nicht auf Port 3000 zu laufen"
fi
echo

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ ALLE TESTS BESTANDEN"
echo "═══════════════════════════════════════════════════════════════"
echo
echo "📌 Nächste Schritte für OpenWebUI-Integration:"
echo "   1. Öffne OpenWebUI im Browser: http://127.0.0.1:3000"
echo "   2. Gehe zu: Einstellungen → Connections → OpenAI API"
echo "   3. Setze API Base URL: http://127.0.0.1:8001/v1"
echo "   4. API Key: dummy (beliebig)"
echo "   5. Teste mit: 'Liste Dateien im Workspace auf'"
echo

exit 0
