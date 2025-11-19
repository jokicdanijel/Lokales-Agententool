#!/usr/bin/env bash
# LocalAgent-Pro Server Starter
# WICHTIG: Startet immer mit aktiviertem venv!
set -euo pipefail

cd "$(dirname "$0")"

echo "🚀 LocalAgent-Pro Server wird gestartet..."

# Virtual Environment MUSS aktiviert werden!
# Prüfe erst lokales venv, dann Parent-Verzeichnis .venv
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual Environment aktiviert (venv)"
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✓ Virtual Environment aktiviert (../.venv)"
else
    echo "❌ Virtual Environment nicht gefunden!"
    echo "Erstelle venv mit: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Prüfen ob Server bereits läuft
if pgrep -f "openwebui_agent_server.py" > /dev/null; then
    echo "⚠️  Server läuft bereits!"
    echo "Prozess-ID: $(pgrep -f openwebui_agent_server.py)"
    read -p "Server neu starten? (j/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Jj]$ ]]; then
        echo "Stoppe alten Server..."
        pkill -f openwebui_agent_server.py
        sleep 2
    else
        echo "Abgebrochen."
        exit 0
    fi
fi

# Server im Hintergrund starten
echo "Starte Server auf Port 8001..."
nohup python src/openwebui_agent_server.py > server.log 2>&1 &
SERVER_PID=$!

echo "✓ Server gestartet (PID: $SERVER_PID)"
echo "📁 Log-Datei: $(pwd)/server.log"

# Warten bis Server bereit ist
echo "Warte auf Server..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
        echo "✓ Server ist bereit!"
        break
    fi
    sleep 1
    echo -n "."
done
echo

# Status anzeigen
echo ""
echo "============================================================"
echo "✅ LocalAgent-Pro Server läuft!"
echo "============================================================"
echo "📡 Server: http://127.0.0.1:8001"
echo "🎯 OpenWebUI API: http://127.0.0.1:8001/v1"
echo "📊 Health Check: http://127.0.0.1:8001/health"
echo ""
echo "📝 Nützliche Befehle:"
echo "  • Server-Log: tail -f server.log"
echo "  • Health-Check: ./health_check.sh"
echo "  • Server stoppen: pkill -f openwebui_agent_server.py"
echo "============================================================"
