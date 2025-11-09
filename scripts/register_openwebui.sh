#!/usr/bin/env bash
# ==============================================================================
# bin/register_openwebui.sh
# Registriere opena3 (OpenWebUI Agent) im Dashboard
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

require curl

info "Registriere opena3 (OpenWebUI Agent) im Dashboard..."

curl_auth POST "http://127.0.0.1:$DASHBOARD_PORT/api/agent/register" \
  '{"agent_id": "opena3", "endpoint": "http://127.0.0.1:12347"}'

echo ""
ok "opena3 registriert"
