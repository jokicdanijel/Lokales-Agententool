#!/usr/bin/env bash
set -euo pipefail
PORT_DASH=12349
TOK="$(cat .env)"
curl -s -H "Authorization: Bearer $TOK" "http://127.0.0.1:$PORT_DASH/health" | jq .
curl -s -H "Authorization: Bearer $TOK" "http://127.0.0.1:$PORT_DASH/api/status/all" | jq .
curl -s -X POST -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  "http://127.0.0.1:$PORT_DASH/api/agent/register" \
  -d '{"agent_id":"opena1","endpoint":"http://127.0.0.1:12344"}' | jq .
