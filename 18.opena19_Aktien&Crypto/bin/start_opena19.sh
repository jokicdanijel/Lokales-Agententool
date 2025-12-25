#!/bin/bash
# Start Script für opena19 (Stocks & Crypto Agent)
# Port: 12365
# Kürzel: stockcryptop

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

AGENT_ID="opena19"
PORT=12365
MAIN_FILE="main_stocks_crypto_agent.py"
PID_FILE="logs/${AGENT_ID}.pid"
LOG_FILE="logs/${AGENT_ID}.nohup.log"

echo "=========================================="
echo "  Starting opena19 (Stocks & Crypto)"
echo "  Port: $PORT"
echo "  Kürzel: stockcryptop"
echo "=========================================="

# ========== 1. Verzeichnisse erstellen ==========
mkdir -p logs data

if [[ ! -f "../.env" ]] && [[ ! -f ".env" ]]; then
    echo "[WARN] .env fehlt, verwende Default-Token"
fi

# ========== 3. Python-Version prüfen ==========
PYTHON_CMD=""
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "[ERROR] Python 3 nicht gefunden"
    exit 1
fi

echo "[INFO] Using Python: $($PYTHON_CMD --version)"

# ========== 4. Dependencies prüfen ==========
REQUIRED_PACKAGES=("fastapi" "uvicorn" "pydantic" "requests")
MISSING_PACKAGES=()

for pkg in "${REQUIRED_PACKAGES[@]}"; do
    if ! $PYTHON_CMD -c "import $pkg" 2>/dev/null; then
        MISSING_PACKAGES+=("$pkg")
    fi
done

if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    echo "[INFO] Installiere fehlende Packages: ${MISSING_PACKAGES[*]}"

    # PEP 668 Check (Ubuntu 25.04)
    if $PYTHON_CMD -m pip install --help | grep -q "break-system-packages"; then
        $PYTHON_CMD -m pip install --break-system-packages "${MISSING_PACKAGES[@]}" || {
            echo "[WARN] Installation mit --break-system-packages fehlgeschlagen, versuche ohne Flag"
            $PYTHON_CMD -m pip install "${MISSING_PACKAGES[@]}"
        }
    else
        $PYTHON_CMD -m pip install "${MISSING_PACKAGES[@]}"
    fi
fi

echo "[INFO] ✅ Alle Dependencies vorhanden"

# ========== 5. Port-Check ==========
if lsof -i :$PORT -sTCP:LISTEN &> /dev/null; then
    echo "[ERROR] ❌ Port $PORT bereits belegt"
    lsof -i :$PORT -sTCP:LISTEN
    exit 1
fi

echo "[INFO] ✅ Port $PORT ist frei"

# ========== 6. Service starten ==========
if [[ -f "$PID_FILE" ]]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "[WARN] Service bereits läuft (PID: $OLD_PID), stoppe zuerst"
        kill "$OLD_PID" 2>/dev/null || true
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

nohup $PYTHON_CMD "$MAIN_FILE" > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

echo "[INFO] Service gestartet (PID: $NEW_PID)"

# ========== 7. Health-Check (3s Wartezeit) ==========
sleep 3

if ! ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "[ERROR] ❌ Service-Start fehlgeschlagen"
    echo "[ERROR] Letzte 20 Zeilen aus Log:"
    tail -20 "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

# Health-Check via curl
if command -v curl &> /dev/null; then
    HEALTH_URL="http://127.0.0.1:$PORT/health"

    for i in {1..5}; do
        if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
            echo "[INFO] ✅ Service ist erreichbar"
            echo ""
            echo "Health response:"
            curl -s "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || curl -s "$HEALTH_URL"
            echo ""
            echo "=========================================="
            echo "  ✅ opena19 erfolgreich gestartet"
            echo "  PID: $NEW_PID"
            echo "  Port: $PORT"
            echo "  Logs: tail -f $LOG_FILE"
            echo "=========================================="
            exit 0
        fi
        echo "[INFO] Warte auf Service... ($i/5)"
        sleep 2
    done

    echo "[WARN] ⚠️  Service läuft, aber Health-Check fehlgeschlagen"
    echo "[WARN] Prüfe Logs: tail -f $LOG_FILE"
else
    echo "[INFO] ✅ Service gestartet (PID: $NEW_PID)"
    echo "[WARN] curl nicht verfügbar, Health-Check übersprungen"
fi

exit 0
