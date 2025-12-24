#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

sg docker -c '
  echo "=== Container Status ==="
  docker ps --filter "name=open-webui"
  echo ""
  echo "=== Logs (letzte 50 Zeilen) ==="
  docker logs --tail=50 open-webui
  echo ""
  echo "=== Volumes ==="
  docker inspect open-webui --format="{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}"
'
