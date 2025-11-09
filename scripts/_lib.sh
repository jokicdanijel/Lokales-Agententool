#!/usr/bin/env bash
# ==============================================================================
# bin/_lib.sh
# Gemeinsame Helferfunktionen für ELION-Stack-CLI
# Source dieses Skripts in anderen Shell-Skripten
# ==============================================================================

set -euo pipefail

# Projektwurzel -> Pfad dieses Skripts /../
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Farben für Terminal-Output
c_green='\033[0;32m'
c_red='\033[0;31m'
c_yellow='\033[1;33m'
c_blue='\033[0;34m'
c_reset='\033[0m'

# ==============================================================================
# Output-Funktionen
# ==============================================================================

info()  { echo -e "${c_blue}ℹ${c_reset} $*"; }
warn()  { echo -e "${c_yellow}⚠${c_reset} $*"; }
ok()    { echo -e "${c_green}✔${c_reset} $*"; }
fail()  { echo -e "${c_red}✖${c_reset} $*"; exit 1; }

# ==============================================================================
# Prüf-Funktionen
# ==============================================================================

require() {
  local bin="$1"
  command -v "$bin" >/dev/null 2>&1 || fail "Benötigtes Tool fehlt: $bin"
}

# ==============================================================================
# Environment Laden
# ==============================================================================

load_env() {
  # Ports + Endpunkte (Defaults)
  DASHBOARD_PORT="${DASHBOARD_PORT:-12349}"
  OPENA1_PORT="${OPENA1_PORT:-12344}"
  OPENA2_PORT="${OPENA2_PORT:-12345}"
  KORDP_PORT="${KORDP_PORT:-12346}"
  OPENWEBUI_PORT="${OPENWEBUI_PORT:-8080}"
  OPENWEBUI_AGENT_PORT="${OPENWEBUI_AGENT_PORT:-12347}"

  # Optional zentrale Env aus config/services.env laden
  if [[ -f "$PROJECT_ROOT/config/services.env" ]]; then
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/config/services.env"
  fi

  # Token aus .env laden (falls vorhanden)
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    TOK="$(cat "$PROJECT_ROOT/.env")"
  else
    warn "Keine .env gefunden im Projektwurzel: $PROJECT_ROOT — manche Aufrufe brauchen den Token."
    TOK=""
  fi
}

# ==============================================================================
# HTTP-Funktionen
# ==============================================================================

curl_auth() {
  # curl_auth <method> <url> [data_json]
  # Macht HTTP-Aufrufe mit Bearer Token
  local method="$1"; shift
  local url="$1"; shift

  if [[ -z "${TOK:-}" ]]; then
    fail "Kein Token geladen (.env fehlt). Erstelle/fülle $PROJECT_ROOT/.env"
  fi

  if [[ "$method" == "GET" ]]; then
    curl -sS -H "Authorization: Bearer $TOK" "$url"
  else
    local data="${1:-{}}"
    curl -sS -H "Authorization: Bearer $TOK" \
      -H "Content-Type: application/json" \
      -X "$method" \
      -d "$data" \
      "$url"
  fi
}

# ==============================================================================
# Export für Use in Sub-Skripten
# ==============================================================================

export SCRIPT_DIR PROJECT_ROOT
export c_green c_red c_yellow c_blue c_reset
export DASHBOARD_PORT OPENA1_PORT OPENA2_PORT KORDP_PORT OPENWEBUI_PORT OPENWEBUI_AGENT_PORT
export TOK
