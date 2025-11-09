#!/usr/bin/env bash
# ==============================================================================
# bin/openwebui_up.sh
# Starte OpenWebUI Docker Container
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

require docker

info "Starte OpenWebUI Docker Container..."

docker run -d \
  --name openwebui \
  -p 8080:8080 \
  -v ~/.openwebui:/app/backend/data \
  -e "OPENWEBUI_AUTH_TRUST_EMAIL_HEADER=True" \
  ghcr.io/open-webui/open-webui:main || {
  warn "Container existiert bereits — versuche zu starten..."
  docker start openwebui || fail "Konnte OpenWebUI nicht starten"
}

ok "OpenWebUI läuft auf Port 8080"
sleep 2

info "Prüfe Erreichbarkeit..."
if curl -sSf http://127.0.0.1:8080 >/dev/null 2>&1; then
  ok "OpenWebUI erreichbar unter http://127.0.0.1:8080"
else
  warn "OpenWebUI nicht sofort erreichbar — warte 5 Sekunden..."
  sleep 5
fi
