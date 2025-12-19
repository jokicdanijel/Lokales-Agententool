#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
DASH_URL="http://127.0.0.1:12349"

echo "=== Dashboard Quick-Evaluation ==="
echo "Projekt-Root: $PROJECT_ROOT"
echo
echo "1) Was NICHT das Problem ist:"
echo " - agent-framework Tracing ist optional (nur Telemetrie). Läuft auch ohne."
echo " - GIL / httptools RuntimeWarning ist meist harmlos (kein Crash)."

echo
echo "2) Prüfe, ob Port lauscht (127.0.0.1:12349):"
ss -ltnp 2>/dev/null | grep -E ":12349\b" && ss -ltnp 2>/dev/null | grep -E ":12349\b" || echo "➡️  nix lauscht auf 12349"

echo
echo "3) /health (kurz, max-time 2s):"
if curl -i --max-time 2 "$DASH_URL/health" 2>/dev/null | sed -n '1,20p'; then
  echo "(health call finished)"
else
  echo "(health call failed or timed out)"
fi

echo
echo "4) /api/status/all (mit Token falls vorhanden):"
TOK=""
if [[ -f "$ENV_FILE" ]]; then
  TOK="$(grep -m1 '^DASHBOARD_ADMIN_TOKEN=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"\'"')"
  [[ -z "$TOK" ]] && TOK="$(grep -m1 '^BEARER_TOKEN=' "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"\'"')" || true
fi

if [[ -z "$TOK" ]]; then
  echo "⚠️  Kein DASHBOARD_ADMIN_TOKEN/BEARER_TOKEN in $ENV_FILE gefunden. Versuche anonymen Aufruf (kann 401 geben)."
  curl -i --max-time 4 "$DASH_URL/api/status/all" 2>/dev/null || echo "(anon status call failed)"
else
  echo "Using token from .env (oberflächlich): ${TOK:0:6}..."
  curl -i -H "Authorization: Bearer $TOK" --max-time 6 "$DASH_URL/api/status/all" 2>/dev/null || echo "(status call failed or timed out)"
fi

echo
echo "5) Prozesse (uvicorn / main_dashboard):"
ps aux | egrep 'uvicorn|main_dashboard|opena20' | egrep -v 'egrep|grep' || echo "(no matching processes)"

echo
echo "6) Tail logs (letzte 80 Zeilen):"
LOG_FILE="$PROJECT_ROOT/logs/opena20.nohup.log"
if [[ -f "$LOG_FILE" ]]; then
  tail -n 80 "$LOG_FILE" || true
else
  echo "(Logfile $LOG_FILE fehlt)"
fi

echo
echo "7) Optional: ausführlicher Evaluator (scripts/workspace_evaluation.py)"
if [[ -x "$PROJECT_ROOT/scripts/workspace_evaluation.py" ]] || [[ -f "$PROJECT_ROOT/scripts/workspace_evaluation.py" ]]; then
  echo "Starte evaluator..."
  python3 "$PROJECT_ROOT/scripts/workspace_evaluation.py" "$PROJECT_ROOT" || true
else
  echo "(Evaluator fehlt)"
fi

echo
cat <<'EOF'
=== Quick-Fixes (wenn /health nicht antwortet) ===
1) Starte das Dashboard manuell:
   cd PROJECT_ROOT
   bin/ops.sh start:agent opena20
2) Prüfe health:
   curl -i http://127.0.0.1:12349/health
3) Rufe Status mit Token auf:
   TOK=$(grep -m1 '^DASHBOARD_ADMIN_TOKEN=' .env | cut -d= -f2- | tr -d '"')
   curl -i -H "Authorization: Bearer $TOK" http://127.0.0.1:12349/api/status/all
4) Wenn uvicorn mit --reload läuft => beenden und ohne --reload neu starten.
EOF

exit 0
