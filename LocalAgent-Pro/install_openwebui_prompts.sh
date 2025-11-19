#!/bin/bash
# OpenWebUI Custom Prompts - Installations-Hilfe für LocalAgent-Pro

set -e

PROMPTS_DIR="openwebui_prompts"
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}🤖 OpenWebUI Custom Prompts - Installation${NC}\n"

# Prüfe, ob Prompts-Verzeichnis existiert
if [ ! -d "$PROMPTS_DIR" ]; then
    echo -e "${YELLOW}⚠️ Prompts-Verzeichnis nicht gefunden!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prompts gefunden:${NC}"
ls -lh "$PROMPTS_DIR"/*.md
echo ""

# Zähle Prompts
PROMPT_COUNT=$(ls -1 "$PROMPTS_DIR"/*.md 2>/dev/null | wc -l)
echo -e "${BLUE}📋 $PROMPT_COUNT Prompts verfügbar${NC}\n"

# Zeige Prompt-Übersicht
echo -e "${BOLD}Verfügbare Custom Prompts:${NC}\n"

echo "1. connection_check.md"
echo "   Befehl: /openwebui_connection"
echo "   Zweck: Verbindung zwischen OpenWebUI und LocalAgent-Pro testen"
echo ""

echo "2. models_test.md"
echo "   Befehl: /openwebui_models_test"
echo "   Zweck: Modell-Verfügbarkeit und Performance testen"
echo ""

echo "3. e2e_test.md"
echo "   Befehl: /openwebui_e2e_test"
echo "   Zweck: Vollständiger End-to-End-Test"
echo ""

echo "4. README.md"
echo "   Dokumentation und Installations-Anleitung"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}📥 Installation in OpenWebUI:${NC}\n"

echo "Schritt 1: OpenWebUI öffnen"
echo "  → http://localhost:3000"
echo ""

echo "Schritt 2: Workspace → Functions → Custom Prompts"
echo ""

echo "Schritt 3: Für jeden Prompt:"
echo "  1. Klicke 'New Prompt'"
echo "  2. Kopiere Inhalt aus openwebui_prompts/<prompt>.md"
echo "  3. Füge 'Prompt-Template' Abschnitt ein"
echo "  4. Konfiguriere Command und Felder"
echo "  5. Speichern"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}🧪 Schnelltest:${NC}\n"

echo "1. Verbindungstest:"
echo "   curl -s http://127.0.0.1:8001/health | jq '.'"
echo ""

# Führe Verbindungstest aus
echo -e "${BLUE}Teste API-Verbindung...${NC}"
if curl -s http://127.0.0.1:8001/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend läuft!${NC}"
    HEALTH=$(curl -s http://127.0.0.1:8001/health)
    echo "$HEALTH" | jq '.'
else
    echo -e "${YELLOW}⚠️ Backend nicht erreichbar!${NC}"
    echo "   Starte mit: ./start_server.sh"
fi
echo ""

echo "2. Modelle prüfen:"
echo "   curl -s http://127.0.0.1:8001/v1/models | jq '.'"
echo ""

echo "3. OpenWebUI prüfen:"
echo "   curl -s http://localhost:3000 >/dev/null && echo '✅ Läuft' || echo '❌ Nicht erreichbar'"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}📚 Weitere Informationen:${NC}\n"
echo "  • Vollständige Anleitung: openwebui_prompts/README.md"
echo "  • System-Setup: INSTALLATION.md"
echo "  • GPU-Setup: GPU_SETUP.md"
echo ""

echo -e "${BOLD}💡 Nächste Schritte:${NC}\n"
echo "  1. OpenWebUI öffnen (falls noch nicht gestartet):"
echo "     docker run -d -p 3000:8080 \\"
echo "       -v open-webui:/app/backend/data \\"
echo "       --name open-webui \\"
echo "       ghcr.io/open-webui/open-webui:main"
echo ""
echo "  2. LocalAgent-Pro Backend starten (falls noch nicht läuft):"
echo "     ./start_server.sh"
echo ""
echo "  3. OpenWebUI konfigurieren:"
echo "     Settings → Connections → OpenAI API"
echo "     Base URL: http://127.0.0.1:8001/v1"
echo ""
echo "  4. Custom Prompts hinzufügen (siehe oben)"
echo ""
echo "  5. Ersten Test ausführen:"
echo "     /openwebui_connection"
echo ""

echo -e "${GREEN}✅ Bereit für die Nutzung!${NC}"
