#!/usr/bin/env bash
set -Eeuo pipefail
BASE="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent"
VENV="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai/venv313/bin/activate"
PORT=12349

cd "$BASE"
source "$VENV"
mkdir -p logs .runtime
echo "$PORT" > .runtime/port
# Token sicherstellen (security._read_env_token erzeugt bei Bedarf .env)
python3 - <<'PY'
from security import _read_env_token
_ = _read_env_token()
PY

exec uvicorn main_dashboard:app --host 127.0.0.1 --port "$PORT" --no-access-log

