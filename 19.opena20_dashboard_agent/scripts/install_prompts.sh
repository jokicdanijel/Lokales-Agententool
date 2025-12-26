#!/usr/bin/env bash
# OpenWebUI Custom Prompts - Installations-Hilfe für LocalAgent-Pro
set -euo pipefail
trap 'echo "✖ Fehler (exit $?)"; exit 1' ERR

PROMPTS_DIR="${1:-${PROMPTS_DIR:-openwebui_prompts}}"

BOLD='\033[1m' GREEN='\033[0;32m' BLUE='\033[0;34m' YELLOW='\033[1;33m' NC='\033[0m'

echo -e "${BOLD}🤖 OpenWebUI Custom Prompts - Installation${NC}\n"

# Dependencies
for cmd in curl jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️ Fehlendes Tool: $cmd — bitte installieren.${NC}"
    exit 2
  fi
done

# Directory exists?
if [ ! -d "$PROMPTS_DIR" ]; then
    echo -e "${YELLOW}⚠️ Prompts-Verzeichnis '$PROMPTS_DIR' nicht gefunden!${NC}"
    exit 1
fi

# Gather prompts safely
mapfile -t PROMPTS < <(printf '%s
' "$PROMPTS_DIR"/*.md | sed '/\.md$/!d' 2>/dev/null || true)
PROMPT_COUNT=${#PROMPTS[@]}

echo -e "${GREEN}✅ Prompts gefunden:${NC}"
if [ "$PROMPT_COUNT" -eq 0 ]; then
  echo "   (keine .md Dateien in $PROMPTS_DIR)"
else
  for p in "${PROMPTS[@]}"; do printf " - %s\n" "$p"; done
fi
echo ""
echo -e "${BLUE}📋 $PROMPT_COUNT Prompts verfügbar${NC}\n"

# Schnelltests
echo -e "${BOLD}🧪 Schnelltest:${NC}\n"
echo "1. Verbindungstest:"
echo -n "   Testing backend at http://127.0.0.1:8001/health ... "
if curl -fsS http://127.0.0.1:8001/health >/dev/null; then
  echo -e "${GREEN}OK${NC}"
  curl -s http://127.0.0.1:8001/health | jq '.'
else
  echo -e "${YELLOW}nicht erreichbar${NC}"
  echo "   Tipp: Starte Backend: ./start_server.sh"
fi

echo ""
echo "2. Modelle prüfen:"
curl -s http://127.0.0.1:8001/v1/models | jq '.' || echo "   Modelle nicht erreichbar"

echo ""
echo "3. OpenWebUI prüfen:"
curl -sSf http://localhost:3000 >/dev/null && echo '   ✅ Läuft' || echo '   ❌ Nicht erreichbar'

echo -e "${GREEN}✅ Bereit für die Nutzung!${NC}"
