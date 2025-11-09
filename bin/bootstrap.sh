#!/usr/bin/env bash
# ==============================================================================
# bin/bootstrap.sh
# Initialisiere Projekt-Verzeichnisse und prüfe Abhängigkeiten
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

info "Initialisiere ELION Hyper-Dashboard Projekt..."

# Erstelle notwendige Verzeichnisse
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/archive"
mkdir -p "$PROJECT_ROOT/.runtime"
mkdir -p "$PROJECT_ROOT/config"
mkdir -p "$PROJECT_ROOT/19.dashboard_agent/opena3"

ok "Verzeichnisse erstellt"

# Prüfe benötigte Tools
info "Prüfe benötigte Tools..."
for tool in curl jq python3; do
  if command -v "$tool" >/dev/null 2>&1; then
    ok "$tool vorhanden"
  else
    warn "$tool FEHLT — einige Funktionen arbeiten nicht"
  fi
done

# Optional: ss oder netstat
if command -v ss >/dev/null 2>&1 || command -v netstat >/dev/null 2>&1; then
  ok "Netzwerk-Tools vorhanden"
else
  warn "Weder ss noch netstat vorhanden — bin/ports.sh nutzt Fallback"
fi

# Prüfe .env
if [[ -f "$PROJECT_ROOT/.env" ]]; then
  ok ".env vorhanden ($(wc -c <"$PROJECT_ROOT/.env") Bytes)"
else
  warn ".env FEHLT — mache zuerst: bin/ops.sh start"
  warn "Das Dashboard erzeugt .env automatisch beim ersten Start"
fi

# Prüfe config/services.env
if [[ ! -f "$PROJECT_ROOT/config/services.env" ]]; then
  info "Erstelle config/services.env mit Standard-Ports..."
  cat >"$PROJECT_ROOT/config/services.env" <<'EOF'
# ELION Hyper-Dashboard Service Ports
export DASHBOARD_PORT=12349
export OPENA1_PORT=12344
export OPENA2_PORT=12345
export KORDP_PORT=12346
export OPENWEBUI_AGENT_PORT=12347
export OPENWEBUI_PORT=8080
EOF
  ok "config/services.env erstellt"
fi

ok "Bootstrap abgeschlossen ✔"
