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

PORT="${PORT:-12347}"

echo "Starte OpenWebUI Agent (opena3) auf Port $PORT..."
nohup python3 "$ROOT_DIR/main_openwebui_agent.py" \
    >"$LOG_DIR/opena3.nohup.log" 2>&1 &

PID=$!
echo "$PID" > "$RUNTIME_DIR/opena3.pid"

sleep 1
echo "✓ OpenWebUI Agent started (PID: $PID, Port: $PORT)"
