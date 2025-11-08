#!/usr/bin/env bash
set -euo pipefail

# Pfade anpassen, falls Projekt verschoben ist
PROJ="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent"
cd "$PROJ"

# venv laden (deine bestehende venv313)
source ../1.portier_openai/venv313/bin/activate

mkdir -p logs .runtime ARCHIV

# Falls alter Prozess auf 12345 hängt, killen
if ss -ltnp 'sport = :12345' 2>/dev/null | grep -q LISTEN; then
  pid=$(ss -ltnp 'sport = :12345' | awk 'NR>1 {print $NF}' | sed 's/.*pid=\([0-9]\+\).*/\1/' | head -n1)
  if [[ -n "${pid:-}" ]]; then
    echo "Port 12345 belegt von PID $pid -> beenden"
    kill "$pid" || true
    sleep 1
  fi
fi

# Start opena2
echo "Starte opena2 auf 127.0.0.1:12345 ..."
nohup python3 main_opena2.py > logs/opena2.nohup.log 2>&1 &
echo $! > .runtime/opena2.pid
echo "opena2 PID: $(cat .runtime/opena2.pid)"

