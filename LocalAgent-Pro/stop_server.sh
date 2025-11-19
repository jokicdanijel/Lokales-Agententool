#!/usr/bin/env bash
# LocalAgent-Pro Server Stopper
set -euo pipefail

echo "🛑 LocalAgent-Pro Server wird gestoppt..."

if pgrep -f "openwebui_agent_server.py" > /dev/null; then
    PID=$(pgrep -f "openwebui_agent_server.py")
    echo "Stoppe Server (PID: $PID)..."
    pkill -f openwebui_agent_server.py
    sleep 1
    
    if pgrep -f "openwebui_agent_server.py" > /dev/null; then
        echo "⚠️  Server antwortet nicht, erzwinge Stopp..."
        pkill -9 -f openwebui_agent_server.py
    fi
    
    echo "✓ Server gestoppt"
else
    echo "ℹ️  Server läuft nicht"
fi
