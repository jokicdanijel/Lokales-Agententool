#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Mit docker-Gruppe ausführen (verhindert permission denied)
sg docker -c '
  docker compose pull
  docker compose up -d
  echo ""
  echo "✅ OpenWebUI läuft unter: http://localhost:3000"
  echo ""
  docker ps --filter "name=open-webui"
'
