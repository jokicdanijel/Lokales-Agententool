#!/bin/bash

# =============================================================================
# chat-local.sh - LocalAgent-Pro CLI Chat Interface
# =============================================================================
# Beschreibung: Sendet Nachrichten an LocalAgent-Pro über OpenAI-API
# Verwendung: ./chat-local.sh "Deine Frage hier"
# =============================================================================

# Konfiguration
MODEL="llama3.1"
ENDPOINT="http://127.0.0.1:8001/v1/chat/completions"
SYSTEM_PROMPT="Du bist LocalAgent-Pro, ein lokaler KI-Agent. Du kannst Dateien lesen/schreiben, Verzeichnisse auflisten, Shell-Befehle ausführen und Webinhalte abrufen. Antworte präzise auf Deutsch."

# Farben für Terminal-Ausgabe
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Prüfe ob Parameter übergeben wurde
USER_PROMPT="$1"

if [ -z "$USER_PROMPT" ]; then
  echo -e "${RED}❗ Bitte gib eine Frage ein.${NC}"
  echo ""
  echo -e "${YELLOW}🔹 Beispiele:${NC}"
  echo -e "  ${BLUE}./chat-local.sh 'Liste alle Dateien im workspace Verzeichnis auf'${NC}"
  echo -e "  ${BLUE}./chat-local.sh 'Erstelle eine Datei hello.txt mit \"Hallo Welt\"'${NC}"
  echo -e "  ${BLUE}./chat-local.sh 'Zeige mir den Inhalt von config.yaml'${NC}"
  echo -e "  ${BLUE}./chat-local.sh 'Wie trainiere ich ein neuronales Netz?'${NC}"
  echo ""
  echo -e "${YELLOW}📋 Verfügbare Tools:${NC}"
  echo -e "  • Datei lesen: 'Lies Datei config.yaml'"
  echo -e "  • Datei schreiben: 'Erstelle Datei test.txt mit Inhalt xyz'"
  echo -e "  • Verzeichnis: 'Liste Verzeichnis workspace auf'"
  echo -e "  • Web: 'Hole Webseite github.com'"
  echo ""
  exit 1
fi

# Prüfe ob Server läuft
if ! curl -s http://127.0.0.1:8001/health > /dev/null 2>&1; then
  echo -e "${RED}❌ LocalAgent-Pro Server läuft nicht!${NC}"
  echo -e "${YELLOW}💡 Starte den Server mit: ./start_server.sh${NC}"
  exit 1
fi

# Zeige Anfrage
echo -e "${BLUE}🤖 LocalAgent-Pro${NC}"
echo -e "${GREEN}❓ Frage:${NC} $USER_PROMPT"
echo -e "${YELLOW}⏳ Verarbeite...${NC}"
echo ""

# Sende Anfrage an LocalAgent-Pro
RESPONSE=$(curl -s $ENDPOINT \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"messages\": [
      {\"role\": \"system\", \"content\": \"$SYSTEM_PROMPT\"},
      {\"role\": \"user\", \"content\": \"$USER_PROMPT\"}
    ],
    \"temperature\": 0.7
  }")

# Prüfe ob Antwort JSON ist
if ! echo "$RESPONSE" | python3 -m json.tool >/dev/null 2>&1; then
  echo -e "${RED}❌ Fehler: Server hat kein gültiges JSON zurückgegeben${NC}"
  echo -e "${YELLOW}Rohe Antwort:${NC}"
  echo "$RESPONSE"
  exit 1
fi

# Extrahiere Antwort
CONTENT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['choices'][0]['message']['content'])" 2>/dev/null)

if [ -z "$CONTENT" ]; then
  echo -e "${RED}❌ Fehler: Keine Antwort erhalten${NC}"
  echo -e "${YELLOW}Rohe Antwort:${NC}"
  echo "$RESPONSE" | python3 -m json.tool
  exit 1
fi

# Zeige Antwort
echo -e "${GREEN}💬 Antwort:${NC}"
echo "$CONTENT"
echo ""

# Optional: Zeige Statistiken
TOKENS=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('usage', {}).get('total_tokens', 'N/A'))" 2>/dev/null)
echo -e "${YELLOW}📊 Tokens:${NC} $TOKENS"

exit 0
