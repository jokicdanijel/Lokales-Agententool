#!/usr/bin/env bash
set -euo pipefail

PROJ="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent"
cd "$PROJ"
source ../1.opena1&2_portier/venv313/bin/activate

mkdir -p logs .runtime

# Ziel-Archivator EXPLIZIT auf 12345 setzen
export KORDP_ARCHIV="http://127.0.0.1:12345"

# Falls 12346 belegt -> killen
if ss -ltnp 'sport = :12346' 2>/dev/null | grep -q LISTEN; then
  pid=$(ss -ltnp 'sport = :12346' | awk 'NR>1 {print $NF}' | sed 's/.*pid=\([0-9]\+\).*/\1/' | head -n1)
  if [[ -n "${pid:-}" ]]; then
    echo "Port 12346 belegt von PID $pid -> beenden"
    kill "$pid" || true
    sleep 1
  fi
fi

echo "Starte kordp (Ziel: $KORDP_ARCHIV) ..."
# Falls dein kordp als Uvicorn-ASGI läuft:
# nohup uvicorn main_kordp:app --host 127.0.0.1 --port 12346 --log-level info > logs/kordp.nohup.log 2>&1 &
# ODER falls es ein normaler Python-Worker ist:
nohup python3 main_kordp.py > logs/kordp.nohup.log 2>&1 &
echo $! > .runtime/kordp.pid
echo "kordp PID: $(cat .runtime/kordp.pid)"
