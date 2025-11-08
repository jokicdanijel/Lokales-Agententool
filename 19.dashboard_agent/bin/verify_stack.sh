#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DASH=12349
OPENA2=12345

TOK="$(cat .env 2>/dev/null || true)"
if [ -z "$TOK" ]; then
  echo ".env fehlt – starte Dashboard einmal mit: python3 main_dashboard.py"
  exit 1
fi

echo "# 1) Health-Checks"
curl -s http://127.0.0.1:$DASH/health | jq .
curl -s http://127.0.0.1:$OPENA2/health | jq . || true

echo "# 2) Dashboard-Status leer/gefüllt?"
curl -s -H "Authorization: Bearer $TOK" http://127.0.0.1:$DASH/api/status/all | jq .

echo "# 3) Manuelle Registrierung opena1 im Dashboard (falls leer)"
curl -s -X POST http://127.0.0.1:$DASH/api/agent/register \
  -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  -d '{"agent_id":"opena1","endpoint":"http://127.0.0.1:12344"}' | jq . || true

echo "# 4) Status erneut prüfen"
curl -s -H "Authorization: Bearer $TOK" http://127.0.0.1:$DASH/api/status/all | jq .

echo "# 5) Test-Dispatch: Safepoint via kordp-kompatiblem Write"
SP="SP$(( $(date +%s) ))_kordp→opena2_CMD.json"
curl -s -X POST http://127.0.0.1:$OPENA2/store/archivp \
  -H 'Content-Type: application/json' \
  -d "{
    \"op\":\"WRITE\",
    \"path\":\"$(date +%Y/%m/%d)/$SP\",
    \"content\":{\"strict\":true, \"ts\":\"$(date -u +%FT%TZ)\", \"payload\":{\"ping\":\"ok\"}}
  }" | jq .

echo "# 6) Letzte Safepoints im Archiv"
curl -s "http://127.0.0.1:$OPENA2/archiv/last?n=5" | jq .

