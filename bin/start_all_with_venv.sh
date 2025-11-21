#!/bin/bash
VENV_BIN="./.venv/bin/python"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🚀 Starte alle Services mit venv..."

# Agenda API
nohup "$VENV_BIN" "$PROJECT_ROOT/src/services/agenda_api.py" > logs/agenda_api.log 2>&1 &
echo "✅ Agenda API (12399) gestartet"

# Dashboard
nohup "$VENV_BIN" "$PROJECT_ROOT/19.dashboard_agent/main_dashboard.py" > logs/dashboard.log 2>&1 &
echo "✅ Dashboard (12349) gestartet"

# OpenWebUI Agent
nohup "$VENV_BIN" "$PROJECT_ROOT/19.dashboard_agent/main_openwebui_agent.py" > logs/opena3.log 2>&1 &
echo "✅ OpenWebUI Agent (12347) gestartet"

sleep 2
echo "✅ Alle Services gestartet"
