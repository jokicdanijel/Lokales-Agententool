#!/bin/bash
# Startet opena1 mit OPENAI_API_KEY aus .env

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${BASE_DIR}/.env"
LOG_DIR="${BASE_DIR}/../logs"

# .env laden
if [[ -f "$ENV_FILE" ]]; then
    export $(grep "^OPENAI_API_KEY_OPENA1=" "$ENV_FILE" | xargs)
    # Key umbenennen für opena1_app.py
    export OPENAI_API_KEY="$OPENAI_API_KEY_OPENA1"
else
    echo "❌ Fehler: $ENV_FILE nicht gefunden"
    exit 1
fi

# Prüfen ob Key vorhanden
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "❌ Fehler: OPENAI_API_KEY_OPENA1 nicht in .env"
    exit 1
fi

# Service starten
cd "$BASE_DIR"
mkdir -p "$LOG_DIR"

echo "🚀 Starte opena1 (Port 12344)..."
nohup python3 opena1_app.py > "$LOG_DIR/opena1.nohup.log" 2>&1 &
PID=$!

echo "✅ opena1 gestartet (PID: $PID)"
echo "$PID" > "$LOG_DIR/opena1.pid"

# Health check
sleep 2
curl -s http://127.0.0.1:12344/health | jq '{status, service, openai_key_present, openai_fp}'
