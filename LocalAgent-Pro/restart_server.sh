#!/usr/bin/env bash
# LocalAgent-Pro Server Restart (mit venv!)
# Stoppt und startet Server neu mit aktiviertem venv

cd "$(dirname "$0")"

echo "🔄 Server wird neu gestartet..."

# Stoppe alten Server
if pgrep -f "openwebui_agent_server" > /dev/null; then
    echo "Stoppe alten Server..."
    pkill -f "openwebui_agent_server"
    sleep 2
    echo "✓ Server gestoppt"
else
    echo "ℹ️  Kein laufender Server gefunden"
fi

# venv aktivieren
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ venv aktiviert (local)"
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✓ venv aktiviert (../.venv)"
else
    echo "❌ venv nicht gefunden!"
    exit 1
fi

# Server starten
echo "Starte Server..."
nohup python src/openwebui_agent_server.py > logs/server.log 2>&1 &
sleep 3

# Status prüfen
if curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
    echo "✅ Server erfolgreich gestartet!"
    echo ""
    echo "Status:"
    curl -s http://127.0.0.1:8001/health | python -m json.tool | grep -E "(status|sandbox|model)" | head -3
    echo ""
    echo "📡 Server: http://127.0.0.1:8001"
    echo "📊 Health: http://127.0.0.1:8001/health"
    echo "📝 Logs: tail -f logs/server.log"
else
    echo "❌ Server-Start fehlgeschlagen!"
    echo "Prüfe logs/server.log"
    exit 1
fi
