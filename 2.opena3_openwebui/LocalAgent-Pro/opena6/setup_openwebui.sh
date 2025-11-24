#!/bin/bash
#
# Browser Agent - OpenWebUI Integration Setup
# Für OpenWebUI 0.6.36+
#
# Dieses Skript:
# 1. Prüft ob beide Services verfügbar sind
# 2. Erstellt die Function Definition
# 3. Liefert Instruktionen für die OpenWebUI-Konfiguration
#
# Verwendung:
#   bash setup_openwebui.sh
#   OPENWEBUI_URL=http://192.168.0.70:3000 bash setup_openwebui.sh
#

set -e

# ============================================================================
# SETUP
# ============================================================================

OPENWEBUI_URL="${OPENWEBUI_URL:-http://localhost:3000}"
AGENT_URL="${AGENT_URL:-http://localhost:12350}"
BEARER_TOKEN="sk_opena6_browser_v3_production"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIDGE_SCRIPT="${SCRIPT_DIR}/openwebui_bridge.py"
CONFIG_FILE="${SCRIPT_DIR}/.openwebui_config"

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# FUNCTIONS
# ============================================================================

log_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

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

log_step() {
    echo ""
    echo -e "${MAGENTA}📌 $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 nicht gefunden"
        exit 1
    fi
}

check_requests() {
    if ! python3 -c "import requests" 2>/dev/null; then
        log_warning "requests-Modul nicht installiert"
        pip3 install requests --quiet
    fi
}

check_services() {
    log_header "Service Health Check"

    # Browser Agent
    if curl -s -f -H "Authorization: Bearer $BEARER_TOKEN" \
        "${AGENT_URL}/health" > /dev/null 2>&1; then
        log_success "Browser Agent ONLINE: ${AGENT_URL}"
        AGENT_OK=1
    else
        log_error "Browser Agent OFFLINE: ${AGENT_URL}"
        AGENT_OK=0
    fi

    # OpenWebUI
    if curl -s -f "${OPENWEBUI_URL}/api/config" > /dev/null 2>&1; then
        log_success "OpenWebUI ONLINE: ${OPENWEBUI_URL}"
        OPENWEBUI_OK=1

        # Prüfe Version
        VERSION=$(curl -s "${OPENWEBUI_URL}/api/config" | grep -o '"version":"[^"]*' | cut -d'"' -f4)
        log_info "Version: $VERSION"
    else
        log_error "OpenWebUI OFFLINE: ${OPENWEBUI_URL}"
        OPENWEBUI_OK=0
    fi

    if [ $AGENT_OK -eq 0 ] || [ $OPENWEBUI_OK -eq 0 ]; then
        log_error "Nicht alle Services verfügbar"
        exit 1
    fi
}

show_manifest() {
    log_header "Function Definition (Manifest)"

    python3 "$BRIDGE_SCRIPT" --action manifest \
        --openwebui-url "$OPENWEBUI_URL" \
        --agent-url "$AGENT_URL"
}

show_instructions() {
    log_header "OpenWebUI Integration - Anleitung"

    cat << 'EOF'
🔧 MANUELLE INTEGRATION (Empfohlen für OpenWebUI 0.6+)

Schritt 1: OpenWebUI Admin Panel öffnen
────────────────────────────────────────
Öffne: http://192.168.0.70:3000/admin

Schritt 2: Zu Settings → Models navigieren
────────────────────────────────────────
1. Klick auf "Admin" oben rechts
2. Wähle "Settings"
3. Navigiere zu "Models"

Schritt 3: Model konfigurieren
────────────────────────────────────────
1. Wähle ein LLM-Modell (z.B. llama2, gpt-4)
2. Klick auf "Edit" oder "Settings"
3. Suche nach "Functions" oder "Tools" Sektion

Schritt 4: Function Definition hinzufügen
────────────────────────────────────────
Kopiere folgende JSON-Definition:

{
  "type": "function",
  "function": {
    "name": "browser_agent",
    "description": "Automatisierte Browser-Kontrolle für Web-Scraping, Datenextraktion und DOM-Manipulation",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["open", "click", "type", "extract_text", "extract_html", "query_selector", "screenshot", "scroll", "wait_for"],
          "description": "Zu führende Browser-Aktion"
        },
        "url": {
          "type": "string",
          "description": "Zielseite URL"
        },
        "selector": {
          "type": "string",
          "description": "CSS oder XPath Selektor"
        },
        "text": {
          "type": "string",
          "description": "Text zum eingeben"
        },
        "wait_ms": {
          "type": "integer",
          "default": 500,
          "description": "Wartezeit in Millisekunden"
        },
        "return_format": {
          "type": "string",
          "enum": ["text", "html", "json", "raw"],
          "default": "text",
          "description": "Format der Rückgabe"
        }
      },
      "required": ["action", "url"]
    }
  }
}

Schritt 5: System Prompt hinzufügen (Optional)
────────────────────────────────────────────────────────
Setze folgenden System Prompt für das Modell:

"Du hast Zugriff auf eine lokale Browser-Automation namens 'browser_agent'.

Verwende sie für Web-Scraping, Datenextraktion und Formular-Automatisierung.

Verfügbare Aktionen:
- open: Öffne eine Webseite
- click: Klicke auf ein Element
- type: Gib Text ein
- extract_text: Extrahiere Text
- extract_html: Extrahiere HTML
- query_selector: Analysiere DOM
- screenshot: Mache Screenshot
- scroll: Scrolle die Seite
- wait_for: Warte auf Element

Immer zuerst 'open' aufrufen, bevor du andere Aktionen ausführst."

Schritt 6: Speichern & Testen
─────────────────────────────────
1. Klick "Save" oder "Update"
2. Starte einen neuen Chat
3. Teste mit Prompts wie:
   "Öffne https://example.com und zeige mir die Titel"
   "Mache einen Screenshot von https://github.com"

AUTOMATISCHE INTEGRATION (Entwickler)
──────────────────────────────────────
Für API-Integration siehe: openwebui_bridge.py

Verwendung:
  python3 openwebui_bridge.py --action manifest
  python3 openwebui_bridge.py --action prompt

EOF
}

create_config() {
    log_step "Speichere Konfiguration"

    cat > "$CONFIG_FILE" << EOF
# Browser Agent - OpenWebUI Integration Config
# Erstellt: $(date)

OPENWEBUI_URL=${OPENWEBUI_URL}
AGENT_URL=${AGENT_URL}
BEARER_TOKEN=${BEARER_TOKEN}

# API Endpoints
OPENWEBUI_API=\${OPENWEBUI_URL}/api/v1
AGENT_API=\${AGENT_URL}

# Status
LAST_CHECK=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

    log_success "Konfiguration gespeichert: ${CONFIG_FILE}"
}

test_integration() {
    log_step "Teste Browser Agent Verbindung"

    # Test 1: Basis-Health
    log_info "Test 1: Health-Check..."
    if curl -s -f -H "Authorization: Bearer $BEARER_TOKEN" \
        "${AGENT_URL}/health" > /dev/null 2>&1; then
        log_success "Health-Check erfolgreich"
    else
        log_error "Health-Check fehlgeschlagen"
        return 1
    fi

    # Test 2: Execute Endpoint
    log_info "Test 2: Execute-Endpoint..."
    RESPONSE=$(curl -s -X POST \
        "${AGENT_URL}/execute" \
        -H "Authorization: Bearer $BEARER_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "action": "open",
            "url": "https://example.com"
        }' 2>&1)

    if echo "$RESPONSE" | grep -q "success\|status"; then
        log_success "Execute-Endpoint reagiert"
        log_info "Response: $RESPONSE" | head -c 200
        echo "..."
    else
        log_error "Execute-Endpoint fehlgeschlagen"
        log_info "Response: $RESPONSE"
        return 1
    fi

    log_success "Alle Tests erfolgreich"
    return 0
}

show_summary() {
    log_header "Setup Zusammenfassung"

    cat << EOF
✅ SETUP ABGESCHLOSSEN

Services Status:
  • Browser Agent:  ONLINE (${AGENT_URL})
  • OpenWebUI:      ONLINE (${OPENWEBUI_URL})

Nächste Schritte:
  1. Öffne OpenWebUI: ${OPENWEBUI_URL}
  2. Folge den Anweisungen oben zur manuellen Integration
  3. Starte einen Chat und teste den Browser Agent

Beispiel-Prompts:
  • "Öffne https://example.com"
  • "Zeige mir einen Screenshot von https://github.com"
  • "Extrahiere die Überschriften von https://news.ycombinator.com"

Hilfsdateien:
  • openwebui_bridge.py - Python API Bridge
  • OPENWEBUI_INTEGRATION.md - Vollständige Dokumentation

Status: 🟢 READY FOR PRODUCTION

EOF
}

# ============================================================================
# MAIN
# ============================================================================

clear

log_header "🚀 Browser Agent - OpenWebUI Integration Setup"

log_info "Umgebung:"
log_info "  OpenWebUI URL: ${OPENWEBUI_URL}"
log_info "  Agent URL: ${AGENT_URL}"
log_info "  Config Dir: ${SCRIPT_DIR}"

# Voraussetzungen
check_python
check_requests

# Health Check
check_services

# Konfiguration
show_manifest

# Integration Guide
show_instructions

# Config speichern
create_config

# Tests
test_integration

# Zusammenfassung
show_summary

exit 0
