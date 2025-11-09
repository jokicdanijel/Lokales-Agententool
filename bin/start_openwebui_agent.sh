#!/usr/bin/env bash
# ==============================================================================
# bin/start_openwebui_agent.sh
# Starte opena3 (OpenWebUI Adapter Agent) auf Port 12347
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

require python3

info "Starte opena3 (OpenWebUI Agent) auf Port $OPENWEBUI_AGENT_PORT..."

# Aktiviere venv falls vorhanden
if [[ -f "$PROJECT_ROOT/1.portier_openai/venv313/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$PROJECT_ROOT/1.portier_openai/venv313/bin/activate"
fi

cd "$PROJECT_ROOT/19.dashboard_agent"

nohup python3 -c "
import sys
sys.path.insert(0, '.')
from opena3.openwebui_agent import app
import uvicorn
uvicorn.run(app, host='127.0.0.1', port=$OPENWEBUI_AGENT_PORT)
" >"$PROJECT_ROOT/logs/opena3.nohup.log" 2>&1 &

sleep 2

if curl -sSf "http://127.0.0.1:$OPENWEBUI_AGENT_PORT/health" >/dev/null 2>&1; then
  ok "opena3 läuft auf Port $OPENWEBUI_AGENT_PORT"
else
  warn "opena3 startet noch — prüfe logs/opena3.nohup.log"
fi
