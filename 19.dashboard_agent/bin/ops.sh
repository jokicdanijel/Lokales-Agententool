#!/usr/bin/env bash
set -euo pipefail

# Basis = Projektwurzel (Ordner über "bin")
BASE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BASE"

# Endpunkte
DASH="http://127.0.0.1:12349"
OPENA1="http://127.0.0.1:12344"
OPENA2="http://127.0.0.1:12345"
OPENA3="http://127.0.0.1:8080"  # optional (OpenWebUI)

# Token aus .env lesen (nur erste Zeile verwenden, Rest sind optionale Variablen)
TOK="$(head -n 1 .env 2>/dev/null || true)"

need_token() {
  if [[ -z "${TOK:-}" ]]; then
    echo "FEHLER: .env fehlt oder ist leer."
    echo "  → Starte das Dashboard einmal (python3 main_dashboard.py) – dabei wird .env erzeugt."
    echo "  → Danach erneut: bin/ops.sh status"
    exit 1
  fi
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "FEHLER: Befehl '$1' fehlt. Bitte installieren."
    exit 1
  }
}

case "${1:-}" in
  start)
    chmod +x bin/*.sh 2>/dev/null || true
    if [[ -x bin/start_all.sh ]]; then
      ./bin/start_all.sh
    else
      echo "Hinweis: bin/start_all.sh nicht gefunden – starte Dashboard nur direkt:"
      echo "  source ../1.portier_openai/venv313/bin/activate"
      echo "  python3 main_dashboard.py"
    fi
    ;;

  stop)
    if [[ -x bin/stop_all.sh ]]; then
      ./bin/stop_all.sh
    else
      echo "Hinweis: bin/stop_all.sh nicht gefunden. Alternativ:"
      echo "  pkill -f main_dashboard.py || true"
      echo "  pkill -f main_opena1.py || true"
      echo "  pkill -f main_opena2.py || true"
      echo "  pkill -f main_kordp.py  || true"
    fi
    ;;

  health)
    need_cmd curl
    curl -s "$DASH/health" | jq .
    ;;

  status)
    need_cmd curl
    need_cmd jq
    need_token
    curl -s -H "Authorization: Bearer $TOK" "$DASH/api/status/all" | jq .
    ;;

  agents:register)
    need_cmd curl
    need_cmd jq
    need_token
    
    echo "# Registriere Phase 1-5 Agenten..."
    
    # Phase 1
    echo "# opena1 (Coordinator) → 12344"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena1\",\"endpoint\":\"http://127.0.0.1:12344\"}" | jq .

    echo "# opena2 (Archivator) → 12345"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena2\",\"endpoint\":\"http://127.0.0.1:12345\"}" | jq .

    echo "# kordp (Scheduler) → 12346"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"kordp\",\"endpoint\":\"http://127.0.0.1:12346\"}" | jq .
    
    # Phase 4
    echo "# opena11 (Social Media) → 12359"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena11\",\"endpoint\":\"http://127.0.0.1:12359\"}" | jq .

    echo "# opena12 (Influencer) → 12360"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena12\",\"endpoint\":\"http://127.0.0.1:12360\"}" | jq .

    echo "# opena13 (Calendar) → 12361"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena13\",\"endpoint\":\"http://127.0.0.1:12361\"}" | jq .

    echo "# opena14 (HTML) → 12362"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena14\",\"endpoint\":\"http://127.0.0.1:12362\"}" | jq .

    echo "# opena15 (Shop) → 12363"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena15\",\"endpoint\":\"http://127.0.0.1:12363\"}" | jq .
    
    # Phase 5
    echo "# opena16 (CRM) → 12364"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena16\",\"endpoint\":\"http://127.0.0.1:12364\"}" | jq .

    echo "# opena17 (Analytics) → 12365"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena17\",\"endpoint\":\"http://127.0.0.1:12365\"}" | jq .

    echo "# opena18 (Dashboard) → 12366"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena18\",\"endpoint\":\"http://127.0.0.1:12366\"}" | jq .

    echo "# opena19 (Workflow) → 12367"
    curl -s -X POST "$DASH/api/agent/register" \
      -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
      -d "{\"agent_id\":\"opena19\",\"endpoint\":\"http://127.0.0.1:12367\"}" | jq .

    echo "# Prüfe optional OpenWebUI ($OPENA3)"
    if curl -fsS "$OPENA3" >/dev/null 2>&1; then
      echo "# opena3 (OpenWebUI) → $OPENA3"
      curl -s -X POST "$DASH/api/agent/register" \
        -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
        -d "{\"agent_id\":\"opena3\",\"endpoint\":\"$OPENA3\"}" | jq .
    else
      echo "(Hinweis) $OPENA3 nicht erreichbar – überspringe opena3."
    fi
    ;;

  agents:check)
    need_cmd curl
    need_cmd jq
    echo "# opena1"; curl -s "$OPENA1/health" | jq . || true
    echo "# opena2"; curl -s "$OPENA2/health" | jq . || true
    echo "# opena3"; curl -s "$OPENA3" | head -n1 || true
    ;;

  write:test)
    need_cmd curl
    need_cmd jq
    # 1) Schreibformat A: op/path/content
    SP="SP$(( $(date +%s) ))_kordp→opena2_CMD.json"
    curl -s -X POST "$OPENA2/store/archivp" \
      -H 'Content-Type: application/json' \
      -d "{
            \"op\":\"WRITE\",
            \"path\":\"$(date +%Y/%m/%d)/$SP\",
            \"content\":{\"strict\":true, \"ts\":\"$(date -u +%FT%TZ)\", \"payload\":{\"ping\":\"ok\"}}
          }" | jq .

    # 2) Schreibformat B: src/dst/kind/payload
    curl -s -X POST "$OPENA2/store/archivp" \
      -H 'Content-Type: application/json' \
      -d '{"src":"kordp","dst":"opena2","kind":"CMD","payload":{"msg":"hello","strict":true}}' | jq .

    # 3) Letzte Einträge listen
    curl -s "$OPENA2/archiv/last?n=5" | jq .
    ;;

  logs)
    tail -n 200 logs/dashboard_runtime.log 2>/dev/null || true
    tail -n 200 logs/opena1_runtime.log   2>/dev/null || true
    tail -n 200 logs/opena1_registry.log  2>/dev/null || true
    tail -n 200 logs/opena2.nohup.log     2>/dev/null || true
    tail -n 200 logs/kordp.nohup.log      2>/dev/null || true
    ;;

  verify)
    # Schneller Integrationslauf
    echo "# 1) Dashboard /health"
    bash "$0" health || true
    echo "# 2) Agent-Endpunkte direkt prüfen"
    bash "$0" agents:check || true
    echo "# 3) Agenten registrieren"
    bash "$0" agents:register || true
    echo "# 4) Dashboard-Status"
    bash "$0" status || true
    echo "# 5) Archivator Schreib-/Lese-Test"
    bash "$0" write:test || true
    ;;

  *)
    cat <<'USAGE'
Nutzung: bin/ops.sh <command>

Verfügbar:
  start             - alle Services starten (falls bin/start_all.sh vorhanden)
  stop              - alle Services stoppen (falls bin/stop_all.sh vorhanden)
  health            - Dashboard /health (ohne Token)
  status            - Dashboard /api/status/all (mit Token aus .env)
  agents:register   - opena1/opena2 (und optional opena3) im Dashboard registrieren
  agents:check      - direkte Reachability der Agenten prüfen (ohne Dashboard)
  write:test        - 2 Test-Safepoints in opena2 schreiben + letzte 5 listen
  logs              - wichtigste Logs anzeigen
  verify            - kompletter Mini-Integrationslauf

WICHTIG:
- JavaScript 'fetch(...)' gehört in die Browser-Konsole (F12), NICHT in die Bash.
- Python-Quelltext nie in die Bash pasten; Dateien editieren und Dienste neu starten.
USAGE
    ;;
esac
