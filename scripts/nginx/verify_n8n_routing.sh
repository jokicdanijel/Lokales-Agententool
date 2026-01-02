#!/usr/bin/env bash
set -euo pipefail

DOMAIN="n8n.hyperdashboard-one.de"

echo "[INFO] GET / (expect: n8n UI or n8n HTML, NOT '<h1>opena20</h1>')"
curl -k -s "https://${DOMAIN}/" | head -n 5

echo
echo "[INFO] POST webhook (expect: NOT 501)"
curl -k -i -X POST "https://${DOMAIN}/webhook/terminal-create-note" \
  -H "Content-Type: application/json" \
  -d '{"content":"hello from verify"}' | head -n 40
