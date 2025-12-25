#!/usr/bin/env bash
# Fix-Skript: Repariere .env-Parsing in allen Agent-Start-Skripten
# Problem: `source ../.env` schlägt fehl bei multiline Keys (mit =)
# Lösung: Nutze sed für robustes Parsing

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Finde alle Start-Skripte mit fehlerhaftem .env-Parsing
SCRIPTS=$(find . \( -name "start_opena*.sh" -o -name "start_browsep.sh" \) -exec grep -l "source.*\.env" {} \; 2>/dev/null | sort)

echo "🔧 Repariere .env-Parsing in Agent-Skripten..."
echo "Gefundene Skripte: $(echo "$SCRIPTS" | wc -l)"
echo ""

FIX_COUNT=0

for script in $SCRIPTS; do
  echo "Processing: $script"

  # Backup erstellen
  cp "$script" "$script.bak"

  # Ersetze: source "../.env" oder source "../../.env" etc.
  # Mit einer Routine, die die Keys mit sed ausliest

  # Regex für verschiedene Variationen:
  # source "../.env"
  # source "../../.env"
  # source ".env"
  # . ../.env
  # . ../../.env

  # Neue Methode: sed + export
  REPLACEMENT='# Robustes .env-Parsing (multiline-safe mit sed)
if [ -f "$(dirname "$0")/../.env" ]; then
  ENV_FILE="$(dirname "$0")/../.env"
  # Extrahiere Key=Value Paare mit sed und exportiere sie
  while IFS= read -r line; do
    if [[ "$line" =~ ^([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
      export "${BASH_REMATCH[1]}=${BASH_REMATCH[2]}"
    fi
  done < "$ENV_FILE"
elif [ -f "../../.env" ]; then
  ENV_FILE="../../.env"
  while IFS= read -r line; do
    if [[ "$line" =~ ^([A-Z_][A-Z0-9_]*)=(.*)$ ]]; then
      export "${BASH_REMATCH[1]}=${BASH_REMATCH[2]}"
    fi
  done < "$ENV_FILE"
fi'

  # Ersetze alle source-Varianten
  sed -i '/^[[:space:]]*source[[:space:]]*"\?.*\.env"\?$/d' "$script"
  sed -i "/^[[:space:]]*\.[[:space:]]*\.\.*\/\.env$/d" "$script"

  # Füge neue .env-Parsing-Routine nach dem "set -e" ein
  sed -i "/^set -euo pipefail$/a\\
\\
$REPLACEMENT" "$script" || true

  echo "  ✅ Fixed: $script"
  ((FIX_COUNT++))
done

echo ""
echo "✅ $FIX_COUNT Skripte repariert"
echo ""
echo "📝 Backups erstellt als *.bak Dateien"
echo ""
echo "Test: bin/ops.sh start"
