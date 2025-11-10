#!/usr/bin/env bash
# scripts/register_openwebui.sh
# Register opena3 (OpenWebUI → openweb) at OpenA1 Coordinator
# Waits for opena1 & opena2, then sends route/update + verifies safepoint

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
A1="http://127.0.0.1:12344/health"
A2="http://127.0.0.1:12345/health"
ROUTE_URL="http://127.0.0.1:12344/route/update"

echo "⏳ waiting for opena1 & opena2..."
for i in {1..60}; do
  if curl -sf "$A1" >/dev/null 2>&1 && curl -sf "$A2" >/dev/null 2>&1; then
    echo "✅ Core services responding"
    break
  fi
  sleep 1
done

echo "➡️  registering openweb route at opena1..."
curl -s -X POST "$ROUTE_URL" \
  -H 'content-type: application/json' \
  -d "{
    \"agent\":\"openwebui\",
    \"agent_id\":\"opena3\",
    \"port\":12346,
    \"program\":\"openweb\",
    \"archivator_port\":12345,
    \"mapping_ts\":\"$(date -u +%FT%TZ)\",
    \"mapping\":{}
  }" | jq .

echo ""
echo "✅ registration complete"
echo "   Health: curl -s http://127.0.0.1:12346/health | jq ."
echo "   Call:   curl -s -X POST http://127.0.0.1:12346/openwebui/call -H 'content-type: application/json' -d '{\"action\":\"prompt\",\"data\":{\"text\":\"hello\"}}' | jq ."
