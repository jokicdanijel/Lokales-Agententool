#!/usr/bin/env bash
# ==============================================================================
# bin/ports.sh
# Zeige aktive Service-Ports
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

info "Zeige aktive Service-Ports..."

for port in 12344 12345 12346 12349 8080 12347; do
  if command -v ss >/dev/null 2>&1; then
    if ss -tuln 2>/dev/null | grep -q ":$port "; then
      ok "Port $port — aktiv"
    else
      warn "Port $port — inaktiv"
    fi
  elif command -v netstat >/dev/null 2>&1; then
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
      ok "Port $port — aktiv"
    else
      warn "Port $port — inaktiv"
    fi
  else
    warn "Weder ss noch netstat verfügbar – nutze curl Fallback"
    if curl -sSf "http://127.0.0.1:$port/health" >/dev/null 2>&1; then
      ok "Port $port — antwortet"
    else
      warn "Port $port — keine Antwort"
    fi
  fi
done
