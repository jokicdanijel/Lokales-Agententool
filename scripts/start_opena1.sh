#!/usr/bin/env bash
set -Eeuo pipefail
BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent"
VENV="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313/bin/activate"
PORT=12344

cd "$BASE"
source "$VENV"
mkdir -p logs
python3 - <<'PY'
from security import _read_env_token
_ = _read_env_token()
PY

exec uvicorn main_opena1:app --host 127.0.0.1 --port "$PORT" --no-access-log
