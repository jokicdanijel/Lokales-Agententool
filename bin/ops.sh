#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Portier OPS – CLI Dispatcher

Befehle:
  start <agent>   Startet lokalen HTTP-Agenten (telegram|vscode|mail|whatsapp)
  help            Zeigt diese Hilfe

Beispiele:
  bin/ops.sh start telegram
USAGE
}

start_agent() {
  local agent="$1"
  case "$agent" in
    telegram) exec python3 4.telegram_agent/main_agent.py ;;
    vscode)   exec python3 5.vscode_agent/main_agent.py ;;
    mail)     exec python3 6.mail_agent/main_agent.py ;;
    whatsapp) exec python3 7.whatsapp_agent/main_agent.py ;;
    *) echo "❌ Unbekannter Agent: $agent"; exit 1 ;;
  esac
}

[[ $# -lt 1 ]] && { usage; exit 1; }

cmd="$1"; shift || true

case "$cmd" in
  start)
    [[ $# -eq 1 ]] || { echo "❌ Agent angeben (telegram|vscode|mail|whatsapp)"; exit 1; }
    start_agent "$1"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    echo "❌ Unbekannter Befehl: $cmd"
    usage
    exit 1
    ;;
esac
