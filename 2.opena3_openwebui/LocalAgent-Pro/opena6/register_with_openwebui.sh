#!/bin/bash
#
# Browser Agent - OpenWebUI Tool Registration Script
# Registriert opena6_browser als Tool in OpenWebUI
#
# Verwendung:
#   bash register_with_openwebui.sh
#   bash register_with_openwebui.sh --openwebui-url http://localhost:8080
#   bash register_with_openwebui.sh --action status
#

set -e

# ============================================================================
# KONFIGURATION
# ============================================================================

AGENT_NAME="opena6_browser"
AGENT_PORT="12350"
AGENT_URL="${AGENT_URL:-http://localhost:${AGENT_PORT}}"
OPENWEBUI_URL="${OPENWEBUI_URL:-http://localhost:8080}"
BEARER_TOKEN="sk_opena6_browser_v3_production"
ACTION="${1:-register}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_SCRIPT="${SCRIPT_DIR}/openwebui_tool_registration.py"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# FUNKTIONEN
# ============================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 nicht gefunden"
        exit 1
    fi
    log_success "Python3 gefunden"
}

check_requests() {
    if ! python3 -c "import requests" 2>/dev/null; then
        log_warning "requests-Modul nicht installiert, installiere..."
        pip3 install requests --quiet
    fi
    log_success "requests-Modul verfügbar"
}

check_agent_health() {
    log_info "Prüfe Browser Agent Gesundheit..."

    if curl -s -f -H "Authorization: Bearer $BEARER_TOKEN" \
        "${AGENT_URL}/health" > /dev/null 2>&1; then
        log_success "Browser Agent verfügbar: ${AGENT_URL}"
        return 0
    else
        log_error "Browser Agent nicht erreichbar: ${AGENT_URL}"
        return 1
    fi
}

check_openwebui_health() {
    log_info "Prüfe OpenWebUI Gesundheit..."

    if curl -s -f "${OPENWEBUI_URL}/api/v1/auth" > /dev/null 2>&1; then
        log_success "OpenWebUI verfügbar: ${OPENWEBUI_URL}"
        return 0
    else
        log_error "OpenWebUI nicht erreichbar: ${OPENWEBUI_URL}"
        return 1
    fi
}

register_tool() {
    log_info "Registriere Browser Agent als Tool in OpenWebUI..."
    echo ""

    if ! check_agent_health; then
        return 1
    fi

    if ! check_openwebui_health; then
        return 1
    fi

    echo ""
    python3 "$TOOL_SCRIPT" \
        --action register \
        --openwebui-url "$OPENWEBUI_URL" \
        --agent-url "$AGENT_URL"

    if [ $? -eq 0 ]; then
        log_success "Tool erfolgreich registriert"
        echo ""
        log_info "Nächste Schritte:"
        echo "  1. Öffne OpenWebUI: ${OPENWEBUI_URL}"
        echo "  2. Starte ein neues Chat-Gespräch"
        echo "  3. Verwende den Browser Agent als Tool"
        echo ""
        echo "Beispiel-Verwendung:"
        echo '  "Öffne https://example.com und extrahiere alle Links"'
        return 0
    else
        log_error "Tool-Registrierung fehlgeschlagen"
        return 1
    fi
}

unregister_tool() {
    log_info "Deregistriere Browser Agent aus OpenWebUI..."
    echo ""

    python3 "$TOOL_SCRIPT" \
        --action unregister \
        --openwebui-url "$OPENWEBUI_URL"

    if [ $? -eq 0 ]; then
        log_success "Tool deregistriert"
        return 0
    else
        log_warning "Tool war möglicherweise nicht registriert"
        return 0
    fi
}

update_tool() {
    log_info "Aktualisiere Tool in OpenWebUI..."
    echo ""

    if ! check_openwebui_health; then
        return 1
    fi

    python3 "$TOOL_SCRIPT" \
        --action update \
        --openwebui-url "$OPENWEBUI_URL" \
        --agent-url "$AGENT_URL"

    if [ $? -eq 0 ]; then
        log_success "Tool aktualisiert"
        return 0
    else
        log_error "Tool-Update fehlgeschlagen"
        return 1
    fi
}

show_status() {
    log_info "Zeige Tool-Status..."
    echo ""

    python3 "$TOOL_SCRIPT" \
        --action status \
        --openwebui-url "$OPENWEBUI_URL" \
        --agent-url "$AGENT_URL"
}

show_help() {
    cat << EOF
${BLUE}Browser Agent - OpenWebUI Tool Registration${NC}

Verwendung:
  bash register_with_openwebui.sh [AKTION] [OPTIONEN]

Aktionen:
  register          Tool bei OpenWebUI registrieren (Standard)
  unregister        Tool aus OpenWebUI entfernen
  update            Tool in OpenWebUI aktualisieren
  status            Tool-Status anzeigen
  health            Gesundheitsprüfung durchführen
  help              Diese Hilfe anzeigen

Optionen:
  --openwebui-url   OpenWebUI API URL (Standard: http://localhost:8080)
  --agent-url       Browser Agent URL (Standard: http://localhost:12350)
  --bearer-token    Bearer Token (Standard: sk_opena6_browser_v3_production)

Umgebungsvariablen:
  OPENWEBUI_URL     OpenWebUI URL
  AGENT_URL         Browser Agent URL
  BEARER_TOKEN      Bearer Token

Beispiele:
  bash register_with_openwebui.sh register
  bash register_with_openwebui.sh status
  OPENWEBUI_URL=http://192.168.0.70:8080 bash register_with_openwebui.sh register

EOF
}

health_check() {
    log_info "Führe Gesundheitsprüfung durch..."
    echo ""

    local agent_ok=false
    local openwebui_ok=false

    if check_agent_health; then
        agent_ok=true
    fi

    if check_openwebui_health; then
        openwebui_ok=true
    fi

    echo ""
    log_info "Zusammenfassung:"
    if [ "$agent_ok" = true ]; then
        log_success "Browser Agent: ONLINE (${AGENT_URL})"
    else
        log_error "Browser Agent: OFFLINE (${AGENT_URL})"
    fi

    if [ "$openwebui_ok" = true ]; then
        log_success "OpenWebUI: ONLINE (${OPENWEBUI_URL})"
    else
        log_error "OpenWebUI: OFFLINE (${OPENWEBUI_URL})"
    fi

    if [ "$agent_ok" = true ] && [ "$openwebui_ok" = true ]; then
        echo ""
        log_success "Beide Services sind verfügbar - Registrierung möglich"
        return 0
    else
        echo ""
        log_error "Nicht alle Services verfügbar"
        return 1
    fi
}

# ============================================================================
# MAIN
# ============================================================================

echo ""
log_info "Browser Agent - OpenWebUI Tool Manager"
log_info "========================================"
echo ""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        register)
            ACTION="register"
            shift
            ;;
        unregister)
            ACTION="unregister"
            shift
            ;;
        update)
            ACTION="update"
            shift
            ;;
        status)
            ACTION="status"
            shift
            ;;
        health)
            ACTION="health"
            shift
            ;;
        help|--help|-h)
            show_help
            exit 0
            ;;
        --openwebui-url)
            OPENWEBUI_URL="$2"
            shift 2
            ;;
        --agent-url)
            AGENT_URL="$2"
            shift 2
            ;;
        --bearer-token)
            BEARER_TOKEN="$2"
            shift 2
            ;;
        *)
            log_error "Unbekannte Option: $1"
            show_help
            exit 1
            ;;
    esac
done

log_info "Konfiguration:"
echo "  OpenWebUI URL: ${OPENWEBUI_URL}"
echo "  Browser Agent: ${AGENT_URL}"
echo "  Aktion: ${ACTION}"
echo ""

# Prüfe Voraussetzungen
check_python
check_requests

echo ""

# Führe Aktion aus
case $ACTION in
    register)
        register_tool
        exit $?
        ;;
    unregister)
        unregister_tool
        exit $?
        ;;
    update)
        update_tool
        exit $?
        ;;
    status)
        show_status
        exit $?
        ;;
    health)
        health_check
        exit $?
        ;;
    *)
        log_error "Unbekannte Aktion: ${ACTION}"
        show_help
        exit 1
        ;;
esac
