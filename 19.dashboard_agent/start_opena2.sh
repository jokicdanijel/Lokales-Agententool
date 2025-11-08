#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p logs .runtime

PORT="${1:-12345}"

# Port-Policy
if [ "$PORT" -eq 8080 ] || [ "$PORT" -lt 12344 ] || [ "$PORT" -gt 12399 ]; then
  echo "Ungültiger Port: $PORT" >&2
  exit 2
fi

export ARCHIVP_ROOT="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai/archivp"

# bereits laufend?
if ss -ltnp 'sport = :'$PORT | grep -q LISTEN; then
  echo "opena2 läuft bereits auf $PORT"
  exit 0
fi

nohup python3 main_opena2.py >/dev/null 2>logs/opena2.nohup.log &
sleep 1
# uvicorn Start:
nohup uvicorn main_opena2:app --host 127.0.0.1 --port "$PORT" >> logs/opena2.nohup.log 2>&1 &
echo "opena2 gestartet auf 127.0.0.1:$PORT"

