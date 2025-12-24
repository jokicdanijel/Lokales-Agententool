#!/usr/bin/env bash
# ==============================================================================
# bin/start_openwebui_adapter.sh
#
# Startet den OpenWebUI Adapter (Port 12350) im Hintergrund
# ==============================================================================

set -euo pipefail

# Pfade
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$(dirname "${SCRIPT_DIR}")" && pwd)"
VENV_PATH="${PROJECT_ROOT}/../1.opena1&2_portier/venv313/bin/activate"
LOGS_DIR="${PROJECT_ROOT}/logs"
RUNTIME_DIR="${PROJECT_ROOT}/.runtime"
PID_FILE="${RUNTIME_DIR}/openwebui_adapter.pid"
LOG_FILE="${LOGS_DIR}/openwebui_adapter.nohup.log"

# Sicherstelle Verzeichnisse existieren
mkdir -p "${LOGS_DIR}" "${RUNTIME_DIR}"

# Venv aktivieren
if [[ ! -f "${VENV_PATH}" ]]; then
    echo "❌ Venv nicht gefunden: ${VENV_PATH}"
    exit 1
fi

source "${VENV_PATH}"

# Prüfe ob bereits laufend
if [[ -f "${PID_FILE}" ]]; then
    OLD_PID=$(cat "${PID_FILE}")
    if kill -0 "${OLD_PID}" 2>/dev/null; then
        echo "⚠️  OpenWebUI Adapter läuft bereits (PID: ${OLD_PID})"
        exit 0
    else
        echo "🧹 Alte PID-Datei bereinigt"
        rm -f "${PID_FILE}"
    fi
fi

# Starte Adapter im Hintergrund
cd "${PROJECT_ROOT}"

nohup python3 -m uvicorn openwebui_adapter:app \
    --host 127.0.0.1 \
    --port 12350 \
    --log-level info \
    > "${LOG_FILE}" 2>&1 &

NEW_PID=$!
echo "${NEW_PID}" > "${PID_FILE}"

echo "✅ OpenWebUI Adapter gestartet (PID: ${NEW_PID}, Port: 12350)"
echo "📋 Log: ${LOG_FILE}"

# Kurz warten und Status prüfen
sleep 2
if curl -s http://127.0.0.1:12350/health > /dev/null 2>&1; then
    echo "✅ Health-Check erfolgreich"
else
    echo "⚠️  Health-Check fehlgeschlagen – siehe Log"
fi
