#!/usr/bin/env bash
# ==============================================================================
# bin/logs.sh
# Zeige die letzten 200 Zeilen aller Logs
# ==============================================================================

set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck disable=SC1091
source "$SCRIPT_DIR/_lib.sh"
load_env

info "Zeige die letzten 200 Zeilen aller Logs..."

for log in "$PROJECT_ROOT"/logs/*.nohup.log; do
  if [[ -f "$log" ]]; then
    echo ""
    echo "=== $(basename "$log") ==="
    tail -200 "$log" || echo "(Keine Logs)"
  fi
done
