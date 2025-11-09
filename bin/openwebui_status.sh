#!/usr/bin/env bash
# ==============================================================================
# bin/openwebui_status.sh
# 
# Health-Check für OpenWebUI-Integration
# Prüft: OpenWebUI (8080), opena3 (12347), Adapter (12350)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENWEBUI_PORT=8080
OPENA3_PORT=12347
ADAPTER_PORT=12350
DASHBOARD_PORT=12349

# Farben
GREEN='\033[92m'
RED='\033[91m'
YELLOW='\033[93m'
BLUE='\033[94m'
RESET='\033[0m'

_print() {
    echo -e "${2}${1}${RESET}"
}

_check_port() {
    local port=$1
    local name=$2
    local url="http://127.0.0.1:${port}"
    
    _print "\n[CHECK] ${name} (Port ${port})" "${BLUE}"
    
    if curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "${url}/health" 2>/dev/null | grep -q "200"; then
        _print "  ✅ OK – Health-Check erfolgreich" "${GREEN}"
        return 0
    else
        _print "  ❌ FEHLER – Nicht erreichbar" "${RED}"
        return 1
    fi
}

_get_health_details() {
    local port=$1
    local name=$2
    local url="http://127.0.0.1:${port}"
    
    _print "\n[DETAILS] ${name} Health-Response:" "${BLUE}"
    
    if response=$(curl -s --connect-timeout 2 "${url}/health" 2>/dev/null); then
        _print "${response}" "${BLUE}"
    else
        _print "  (Keine Antwort)" "${YELLOW}"
    fi
}

main() {
    _print "════════════════════════════════════════════════════════════════" "${BLUE}"
    _print "OpenWebUI Integration – Status Check" "${BLUE}"
    _print "════════════════════════════════════════════════════════════════" "${BLUE}"
    
    # Prüfe alle Services
    results=()
    
    _check_port ${OPENWEBUI_PORT} "OpenWebUI (8080)"
    results+=(${PIPESTATUS[0]})
    
    _check_port ${OPENA3_PORT} "opena3 Agent (12347)"
    results+=(${PIPESTATUS[0]})
    
    _check_port ${ADAPTER_PORT} "Adapter (12350)"
    results+=(${PIPESTATUS[0]})
    
    _check_port ${DASHBOARD_PORT} "Dashboard (12349)"
    results+=(${PIPESTATUS[0]})
    
    # Detaillierte Health-Infos
    _print "\n" ""
    _get_health_details ${OPENWEBUI_PORT} "OpenWebUI"
    _get_health_details ${OPENA3_PORT} "opena3"
    _get_health_details ${ADAPTER_PORT} "Adapter"
    _get_health_details ${DASHBOARD_PORT} "Dashboard"
    
    # Zusammenfassung
    _print "\n════════════════════════════════════════════════════════════════" "${BLUE}"
    
    # Zähle OK/ERROR
    success_count=0
    for result in "${results[@]}"; do
        if [[ $result -eq 0 ]]; then
            ((success_count++))
        fi
    done
    
    total=${#results[@]}
    
    if [[ $success_count -eq $total ]]; then
        _print "✅ ALLE SERVICES OK" "${GREEN}"
        _print "════════════════════════════════════════════════════════════════" "${GREEN}"
        return 0
    else
        _print "⚠️  ${success_count}/${total} Services aktiv" "${YELLOW}"
        _print "════════════════════════════════════════════════════════════════" "${YELLOW}"
        
        if [[ $(( results[0] )) -ne 0 ]]; then
            _print "\n→ OpenWebUI starten: cd 2.openwebui && docker-compose up -d" "${YELLOW}"
        fi
        if [[ $(( results[1] )) -ne 0 ]]; then
            _print "→ opena3 starten: bash bin/start_opena3.sh" "${YELLOW}"
        fi
        if [[ $(( results[2] )) -ne 0 ]]; then
            _print "→ Adapter starten: bash bin/start_openwebui_adapter.sh" "${YELLOW}"
        fi
        if [[ $(( results[3] )) -ne 0 ]]; then
            _print "→ Dashboard starten: bash bin/ops.sh start" "${YELLOW}"
        fi
        
        return 1
    fi
}

main "$@"
