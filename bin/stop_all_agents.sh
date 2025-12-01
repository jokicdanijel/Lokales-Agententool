#!/bin/bash
# PORTIER 3.0 - Stop ALL Agents
# Stoppt alle PORTIER-Agenten sicher

echo "🛑 Stopping ALL PORTIER 3.0 Agents..."

# Stoppe alle main_*.py Prozesse
pkill -f "main_dashboard" 2>/dev/null
pkill -f "main_opena" 2>/dev/null
pkill -f "main_telegram" 2>/dev/null
pkill -f "main_browser" 2>/dev/null
pkill -f "main_email" 2>/dev/null
pkill -f "main_whatsapp" 2>/dev/null
pkill -f "main_telephone" 2>/dev/null
pkill -f "main_calendar" 2>/dev/null
pkill -f "main_html" 2>/dev/null
pkill -f "main_shop" 2>/dev/null
pkill -f "main_homepage" 2>/dev/null
pkill -f "main_workflow" 2>/dev/null
pkill -f "main_openwebui" 2>/dev/null
pkill -f "main_calltracking" 2>/dev/null

sleep 2

echo "✅ All PORTIER agents stopped."
echo ""
echo "Verbleibende Python-Prozesse:"
pgrep -a python3 | grep -E "main_|opena" || echo "Keine PORTIER-Prozesse mehr aktiv."
