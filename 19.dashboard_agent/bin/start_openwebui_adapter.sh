#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
RUNTIME_DIR="$ROOT_DIR/.runtime"
mkdir -p "$LOG_DIR" "$RUNTIME_DIR"

# Venv aktivieren
VENV_PATH="${VENV_PATH:-../1.portier_openai/venv313}"
if [[ ! -f "$ROOT_DIR/$VENV_PATH/bin/activate" ]]; then
    echo "FEHLER: Venv nicht gefunden unter $VENV_PATH"
    exit 1
fi
source "$ROOT_DIR/$VENV_PATH/bin/activate"

PORT="${PORT:-12350}"

echo "Starte OpenWebUI Adapter auf Port $PORT..."
nohup python3 "$ROOT_DIR/openwebui_adapter.py" \
    >"$LOG_DIR/openwebui_adapter.nohup.log" 2>&1 &

PID=$!
echo "$PID" > "$RUNTIME_DIR/openwebui_adapter.pid"

sleep 1
echo "✓ OpenWebUI Adapter started (PID: $PID, Port: $PORT)"
