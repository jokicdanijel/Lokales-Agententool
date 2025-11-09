#!/usr/bin/env bash
# ==============================================================================
# bin/check_env.sh
# Prüfe Umgebungs-Konfiguration
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

info "Prüfe Umgebungs-Konfiguration..."

echo ""
echo "=== Projekt-Pfade ==="
echo "PROJECT_ROOT: $PROJECT_ROOT"
echo "SCRIPT_DIR: $SCRIPT_DIR"

echo ""
echo "=== Ports ==="
echo "Dashboard: $DASHBOARD_PORT"
echo "opena1: $OPENA1_PORT"
echo "opena2: $OPENA2_PORT"
echo "kordp: $KORDP_PORT"
echo "OpenWebUI Agent: $OPENWEBUI_AGENT_PORT"
echo "OpenWebUI: $OPENWEBUI_PORT"

echo ""
echo "=== Token ==="
if [[ -n "${TOK:-}" ]]; then
  ok "Token vorhanden (${#TOK} Zeichen)"
else
  warn "Kein Token — mache zuerst: bin/ops.sh start"
fi

echo ""
if [[ -f "$PROJECT_ROOT/config/services.env" ]]; then
  ok "config/services.env vorhanden"
else
  warn "config/services.env FEHLT"
fi

echo ""
ok "Umgebungs-Prüfung abgeschlossen"
