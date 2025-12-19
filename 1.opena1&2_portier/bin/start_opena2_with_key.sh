#!/bin/bash
# Startet opena2 mit OPENAI_API_KEY aus .env

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${BASE_DIR}/.env"
LOG_DIR="${BASE_DIR}/../logs"

# .env laden (multiline-safe mit sed)
if [[ -f "$ENV_FILE" ]]; then
    export OPENAI_API_KEY_OPENA2="$(sed -n 's/^OPENAI_API_KEY_OPENA2=\(.*\)/\1/p' "$ENV_FILE" | head -1)"
    # Key umbenennen für opena2_app.py
    export OPENAI_API_KEY="$OPENAI_API_KEY_OPENA2"
else
    echo "❌ Fehler: $ENV_FILE nicht gefunden"
    exit 1
fi

# Prüfen ob Key vorhanden
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "❌ Fehler: OPENAI_API_KEY_OPENA2 nicht in .env"
    exit 1
fi

# Service starten
cd "$BASE_DIR"
mkdir -p "$LOG_DIR"

echo "🚀 Starte opena2 (Port 12345)..."
nohup python3 opena2_app.py > "$LOG_DIR/opena2.nohup.log" 2>&1 &
PID=$!

echo "✅ opena2 gestartet (PID: $PID)"
echo "$PID" > "$LOG_DIR/opena2.pid"

# Health check
sleep 2
curl -s http://127.0.0.1:12345/health | jq '{status, service, entries, openai_key_present, openai_fp}'
