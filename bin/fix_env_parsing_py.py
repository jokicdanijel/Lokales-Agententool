#!/usr/bin/env python3
"""
Fix-Skript: Repariere .env-Parsing in allen Agent-Start-Skripten
Problem: `source ../.env` schlägt fehl bei multiline Keys mit = Zeichen
Lösung: Ersetze durch robustes sed/awk-basiertes Parsing
"""

import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

# Finde alle Start-Skripte mit fehlerhaftem .env-Parsing
result = subprocess.run(
    ["find", ".", "-type", "f", "-name", "start_*.sh", "-exec", "grep", "-l", "source.*\\.env", "{}", ";"],
    capture_output=True,
    text=True,
)
scripts = sorted([Path(s.strip()) for s in result.stdout.strip().split("\n") if s.strip()])

print(f"🔧 Repariere .env-Parsing in {len(scripts)} Agent-Skripten...\n")

# Neue .env-Parsing-Routine (robuster für multiline Keys)
NEW_ENV_PARSING = """# Robustes .env-Parsing (safe für Keys mit = Zeichen)
if [ -f "../.env" ]; then
    echo -e "${GREEN}✅ Lade .env aus Projekt-Root${NC}"
    # Nutze sed um Key=Value zu extrahieren (multiline-safe)
    while IFS='=' read -r key value; do
      # Ignoriere Comments und leere Zeilen
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      # Trim whitespace
      key="${key%% }"
      key="${key## }"
      value="${value%% }"
      value="${value## }"
      value="${value%\\"}"
      value="${value#\\"}"
      # Exportiere als Umgebungsvariable
      export "$key"="$value"
    done < "../.env"
elif [ -f ".env" ]; then
    echo -e "${GREEN}✅ Lade lokale .env${NC}"
    while IFS='=' read -r key value; do
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      key="${key%% }"
      key="${key## }"
      value="${value%% }"
      value="${value## }"
      value="${value%\\"}"
      value="${value#\\"}"
      export "$key"="$value"
    done < ".env"
else
    echo -e "${YELLOW}⚠️  Keine .env gefunden, nutze Defaults${NC}"
fi"""

fixed_count = 0

for script in scripts:
    print(f"Processing: {script}")

    try:
        with open(script) as f:
            content = f.read()

        original_content = content

        # 1. Entferne alte source-Zeilen mit .env
        # Pattern: set -a ... source ... set +a
        content = re.sub(r'set\s+-a\s*\n\s*source\s+"?\.\.?/?\.env"?\s*\n\s*set\s+\+a', "", content)

        # Pattern: bloße source-Zeile
        content = re.sub(r'^\s*source\s+"?\.\.?/?\.env"?\s*$', "", content, flags=re.MULTILINE)

        # Pattern: . (dot) sourcing
        content = re.sub(r'^\s*\.\s+"?\.\.?/?\.env"?\s*$', "", content, flags=re.MULTILINE)

        # 2. Entferne leere Zeilen nach dem Fix
        content = re.sub(r"\n\n\n+", "\n\n", content)

        # 3. Füge neue .env-Parsing-Routine nach "set -euo pipefail" ein
        # (falls nicht bereits vorhanden)
        if "Robustes .env-Parsing" not in content:
            content = re.sub(r"(set\s+-euo\s+pipefail)", r"\1\n" + NEW_ENV_PARSING, content)

        # Nur speichern wenn Änderungen vorgenommen
        if content != original_content:
            # Backup erstellen
            backup_path = Path(str(script) + ".bak")
            with open(backup_path, "w") as f:
                f.write(original_content)

            # Reparierte Version speichern
            with open(script, "w") as f:
                f.write(content)

            print(f"  ✅ Fixed: Backup: {backup_path.name}")
            fixed_count += 1
        else:
            print("  ✓ Already OK")

    except Exception as e:
        print(f"  ❌ Fehler: {e}")

print(f"\n✅ {fixed_count} Skripte repariert")
print("📝 Backups: *.bak Dateien erstellt")
print("\n🚀 Teste jetzt: bin/ops.sh start")
