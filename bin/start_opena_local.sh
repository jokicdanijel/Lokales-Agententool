#!/usr/bin/env bash
set -euo pipefail

# start_opena_local.sh
# Startet ein einzelnes Agenten‑App lokal in venv312 mit uvicorn.
# Safety:
#  - verweigert Ausführung im CI (Exit 2)
#  - verlangt ALLOW_UNLIMITED_START=1 (Exit 3) als opt‑in Schutz

if [ -n "${CI:-}" ]; then
  echo "Refusing to run in CI (exit 2)" >&2
  exit 2
fi

if [ "${ALLOW_UNLIMITED_START:-0}" != "1" ]; then
  echo "Requires ALLOW_UNLIMITED_START=1 to run locally (exit 3)" >&2
  exit 3
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found in PATH" >&2
  exit 4
fi

# ensure Python >= 3.12
python3 - <<'PY' || {
  echo "Python 3.12+ required (exit 5)" >&2
  exit 5
}
import sys
if sys.version_info < (3,12):
    sys.exit(1)
PY

VENVDIR=${VENVDIR:-venv312}
if [ ! -d "$VENVDIR" ]; then
  python3 -m venv "$VENVDIR"
fi
. "$VENVDIR/bin/activate"

# load .env into environment if present
if [ -f ".env" ]; then
  set -o allexport
  # shellcheck disable=SC1091
  . .env
  set +o allexport
fi

APP_DIR=${1:-.}
cd "$APP_DIR"

# default port and app entry
PORT="${PORT:-8000}"
UVICORN_APP="${UVICORN_APP:-app.main:app}"

TS=$(date +%Y%m%dT%H%M%S)
LOGDIR="artifacts/logs/start_local/${TS}"
mkdir -p "$LOGDIR"

echo "Starting app in '$APP_DIR' on port $PORT (log: $LOGDIR/start.log)"
exec uvicorn --host 127.0.0.1 --port "$PORT" "$UVICORN_APP" --reload >"$LOGDIR/start.log" 2>&1
