#!/bin/bash
# Quick-Start für LocalAgent-Pro Logging-System

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    LocalAgent-Pro Logging - Quick Reference                     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}📋 Verfügbare Logging-Kommandos:${NC}"
echo ""

echo -e "${CYAN}1. Server mit Logging starten:${NC}"
echo -e "   ${BLUE}python3 src/openwebui_agent_server.py${NC}"
echo ""

echo -e "${CYAN}2. Logs live verfolgen:${NC}"
echo -e "   ${BLUE}./tail_logs.sh${NC}                    # Interaktives Menü"
echo -e "   ${BLUE}./tail_logs.sh localagent-pro${NC}    # Spezifische Datei"
echo ""

echo -e "${CYAN}3. Log-Analyse:${NC}"
echo -e "   ${BLUE}./analyze_logs.sh${NC}                # Statistiken anzeigen"
echo ""

echo -e "${CYAN}4. Logs aufräumen:${NC}"
echo -e "   ${BLUE}./cleanup_logs.sh${NC}                # Interaktives Cleanup"
echo ""

echo -e "${CYAN}5. Einzelne Log-Dateien:${NC}"
echo -e "   ${BLUE}tail -f logs/localagent-pro.log${NC}      # Haupt-Log"
echo -e "   ${BLUE}tail -f logs/api_requests.log${NC}        # API-Requests"
echo -e "   ${BLUE}tail -f logs/tool_executions.log${NC}     # Tool-Calls"
echo -e "   ${BLUE}tail -f logs/ollama_integration.log${NC}  # Ollama-Logs"
echo ""

echo -e "${CYAN}6. Log-Suche:${NC}"
echo -e "   ${BLUE}grep 'ERROR' logs/localagent-pro.log${NC}       # Nur Fehler"
echo -e "   ${BLUE}grep 'Ollama' logs/*.log${NC}                   # Ollama-bezogen"
echo -e "   ${BLUE}grep '2025-11-16 10:' logs/*.log${NC}           # Zeitraum"
echo ""

echo -e "${CYAN}7. Systemd-Service (falls eingerichtet):${NC}"
echo -e "   ${BLUE}journalctl -u localagent-pro -f${NC}            # Live-Logs"
echo -e "   ${BLUE}journalctl -u localagent-pro --since today${NC} # Heute"
echo -e "   ${BLUE}journalctl -u localagent-pro -p err${NC}        # Nur Fehler"
echo ""

echo -e "${YELLOW}📊 Log-Level (in src/openwebui_agent_server.py, Zeile 23):${NC}"
echo -e "   • ${BLUE}DEBUG${NC}    - Alle Details (Development)"
echo -e "   • ${BLUE}INFO${NC}     - Standard (Production)"
echo -e "   • ${BLUE}WARNING${NC}  - Nur Warnungen"
echo -e "   • ${BLUE}ERROR${NC}    - Nur Fehler"
echo ""

echo -e "${YELLOW}📁 Log-Verzeichnisse:${NC}"
echo -e "   ${BLUE}logs/${NC}     - Haupt-Log-Verzeichnis"
echo -e "   ${BLUE}logs/*.log.1${NC}, ${BLUE}.2${NC}, etc. - Rotierte Backups"
echo ""

echo -e "${GREEN}✅ Weitere Infos: ${BLUE}cat LOGGING_GUIDE.md${NC}"
