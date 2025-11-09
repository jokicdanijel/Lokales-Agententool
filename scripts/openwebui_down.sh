#!/usr/bin/env bash
# ==============================================================================
# bin/openwebui_down.sh
# Stoppe OpenWebUI Docker Container
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"

require docker

info "Stoppe OpenWebUI Docker Container..."

docker stop openwebui 2>/dev/null || warn "Container nicht aktiv"
docker rm openwebui 2>/dev/null || warn "Container konnte nicht gelöscht werden"

ok "OpenWebUI gestoppt"
