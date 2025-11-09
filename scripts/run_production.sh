#!/usr/bin/env bash

# Strikte Fehlererkennung
set -euo pipefail

# Basis-Verzeichnisse
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME="$ROOT/.runtime"
LOGDIR="$ROOT/logs"

# Erstelle notwendige Verzeichnisse
mkdir -p "$RUNTIME" "$LOGDIR"

# Port-Finder Funktion (12344-12399)
pick_port() {
    for p in $(seq 12344-12399); do
        if ! ss -ltn | awk '{print $4}' | grep -q ":$p$"; then
            echo "$p"
            return 0
        fi
    done
    echo "Fehler: Kein freier Port im Bereich 12344-12399 verfügbar" >&2
    exit 2
}

# Prüfe und aktiviere Virtual Environment
VENV_PATH="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.portier_openai/venv313"
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "Fehler: Virtual Environment nicht gefunden in $VENV_PATH" >&2
    exit 1
fi
source "$VENV_PATH/bin/activate"

# Port finden und speichern
PORT="$(pick_port)"
echo -n "$PORT" > "$RUNTIME/port"
echo "Gewählter Port: $PORT"

# Umgebungsvariablen setzen
export DASHBOARD_PORT="$PORT"
export PYTHONPATH="${PYTHONPATH:-}${PYTHONPATH:+:}/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt"
export DASHBOARD_ADMIN_TOKEN="${DASHBOARD_ADMIN_TOKEN:-change_this_in_env}"

# Logging-Setup mit Zeitstempel
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_PREFIX="$LOGDIR/dashboard_${TIMESTAMP}"

# Starte FastAPI Server
echo "Starte Dashboard-Server auf Port $PORT..."
nohup uvicorn main_dashboard:app \
    --host 127.0.0.1 \
    --port "$PORT" \
    --log-level info \
    >> "${LOG_PREFIX}.out" 2>> "${LOG_PREFIX}.err" &

# Speichere PID
echo $! > "$RUNTIME/dashboard.pid"

# Warte auf Server-Start und prüfe Health
echo "Warte auf Server-Start..."
for i in $(seq 1 30); do
    if curl -sf "http://127.0.0.1:${PORT}/health" >/dev/null; then
        echo "✅ Dashboard läuft erfolgreich auf Port $PORT"
        echo "📁 Logs:"
        echo "   - Ausgabe: ${LOG_PREFIX}.out"
        echo "   - Fehler:  ${LOG_PREFIX}.err"
        echo "🔍 Health-Check: http://127.0.0.1:${PORT}/health"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo "❌ Fehler: Server-Start fehlgeschlagen" >&2
tail -n 20 "${LOG_PREFIX}.err"
exit 1
