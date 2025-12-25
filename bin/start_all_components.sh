#!/usr/bin/env bash
set -euo pipefail

# bin/start_all_components.sh
# Starts local dev services for the Portier stack with logs, PID files and health checks.

# Configurable options
LOG_DIR="${LOG_DIR:-logs}"
SKIP_DOCKER="${SKIP_DOCKER:-0}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HEALTH_RETRIES=10
HEALTH_INTERVAL=1

mkdir -p "$REPO_ROOT/$LOG_DIR"
cd "$REPO_ROOT/1.opena1&2_portier"

# Ensure virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
  echo "❌ virtuelle Umgebung 'venv' nicht gefunden. Bitte 'python -m venv venv' ausführen."
  exit 1
fi
# shellcheck disable=SC1091
source venv/bin/activate

PIDS_FILE="$REPO_ROOT/$LOG_DIR/started_pids.txt"
: > "$PIDS_FILE"

cleanup() {
  echo "⚠️ Fehler oder Abbruch — Prozesse werden beendet..."
  while read -r pid _; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
    fi
  done < "$PIDS_FILE" || true
  exit 1
}
trap cleanup ERR INT TERM

start_uvicorn() {
  local module="$1"; local port="$2"; local name="$3"
  local log="$REPO_ROOT/$LOG_DIR/${name}.log"
  echo "→ Starte $name auf :$port (Logs: $log)"
  nohup uvicorn "$module:app" --host 127.0.0.1 --port "$port" --env-file .env \
    > "$log" 2>&1 &
  local pid=$!
  echo "$pid $name" >> "$PIDS_FILE"
  echo "$pid" > "$REPO_ROOT/$LOG_DIR/${name}.pid"
}

wait_for_health() {
  local url="$1"; local retries=${2:-$HEALTH_RETRIES}
  local i=0
  until curl -fsS "$url" >/dev/null 2>&1 || [ $i -ge $retries ]; do
    i=$((i+1))
    sleep "$HEALTH_INTERVAL"
  done
  if [ $i -ge $retries ]; then
    echo "❌ Healthcheck $url fehlgeschlagen nach $retries Versuchen"
    return 1
  fi
  echo "✅ $url ist erreichbar"
  return 0
}

# Start Uvicorn services
start_uvicorn "opena1_app" 12344 "opena1"
start_uvicorn "opena2_app" 12345 "opena2"
start_uvicorn "opena20_app" 12349 "opena20"
start_uvicorn "opena11_app" 12356 "opena11"

sleep 2

# Health checks
wait_for_health "http://127.0.0.1:12349/health" || exit 1
wait_for_health "http://127.0.0.1:12349/api/status/all" || exit 1

# Docker Compose (optional)
if [ "$SKIP_DOCKER" -ne 1 ]; then
  echo "→ Starte Docker Compose (basic)"
  docker compose -f artifacts/merged/compose.basic.yml up -d auth website
else
  echo "⚠️ Docker Compose übersprungen (SKIP_DOCKER=1)"
fi

echo "✅ Basic-Komponenten gestartet. PIDs:"
nl -ba "$PIDS_FILE" || true
