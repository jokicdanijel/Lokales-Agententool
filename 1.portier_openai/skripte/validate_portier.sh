#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT_DIR"

echo "🔎 Policy-Validierung startet…"

# 1) Verbotenen Port 8080 blockieren (mit intelligenten Ausschlüssen)
echo "  [1/5] Prüfe verbotenen Port 8080…"
# Ausschlüsse: OpenWebUI, Docker, venv, Kommentare, Tests
if grep -R "8080" . \
  --exclude-dir=venv312 --exclude-dir=venv313 --exclude-dir=.venv \
  --exclude-dir=__pycache__ --exclude-dir=.git \
  --exclude="*.pyc" --exclude="*.pyo" \
  --exclude-dir="openwebui*" \
  2>/dev/null | grep -v "^Binary" | grep -v "docker-compose" | grep -v "openwebui" | grep -v ".venv/"; then
  echo "❌ Verbotener Port 8080 im Repository gefunden (außerhalb OpenWebUI/Docker)."
  exit 1
fi
echo "✅ Kein verbotener Port 8080 gefunden."

# 2) Muss-Dateien prüfen
echo "  [2/5] Prüfe erforderliche Dateien…"
declare -a must_files=(
  ".github/workflows/portier-ci.yml"
  "1.portier_openai/config/tools_registry.json"
  "1.portier_openai/skripte/validate_portier.sh"
  "4.telegram_agent/main_agent.py"
  "5.vscode_agent/main_agent.py"
  "6.mail_agent/main_agent.py"
  "7.whatsapp_agent/main_agent.py"
  "bin/ops.sh"
)
for f in "${must_files[@]}"; do
  [[ -f "$f" ]] || { echo "❌ Datei fehlt: $f"; exit 1; }
done
echo "✅ Muss-Dateien vorhanden."

# 3) Port-Zuordnungen prüfen (fail-fast)
echo "  [3/5] Prüfe Port-Zuordnungen…"
declare -A expected_ports=(
  ["4.telegram_agent/main_agent.py"]="12347"
  ["5.vscode_agent/main_agent.py"]="12348"
  ["6.mail_agent/main_agent.py"]="12349"
  ["7.whatsapp_agent/main_agent.py"]="12350"
)
for file in "${!expected_ports[@]}"; do
  port="${expected_ports[$file]}"
  grep -q "PORT = $port" "$file" || { echo "❌ Port $port nicht in $file gefunden"; exit 1; }
  # Bereichsprüfung
  if ! [[ "$port" =~ ^[0-9]+$ ]] || (( port < 12344 || port > 12399 )); then
    echo "❌ Port $port außerhalb der erlaubten Range (12344–12399) in $file"
    exit 1
  fi
done
echo "✅ Port-Zuordnungen stimmen und liegen innerhalb der Policy-Range."

# 4) Skripte ausführbar
echo "  [4/5] Prüfe Ausführbarkeiten…"
[[ -x "1.portier_openai/skripte/validate_portier.sh" ]] || { echo "❌ validate_portier.sh ist nicht ausführbar"; exit 1; }
[[ -x "bin/ops.sh" ]] || { echo "❌ bin/ops.sh ist nicht ausführbar"; exit 1; }
echo "✅ Ausführbarkeiten korrekt."

# 5) Tools-Registry validieren (JSON-Format + Kernschlüssel)
echo "  [5/5] Prüfe tools_registry.json…"
python3 - <<'PY'
import json, sys
from pathlib import Path
try:
    p = Path("1.portier_openai/config/tools_registry.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    for key in ("archivp","opena1","kordp","opena2"):
        if key not in data:
            print(f"❌ tools_registry.json: Schlüssel '{key}' fehlt")
            sys.exit(1)
    print("✅ tools_registry.json: Kernschlüssel vorhanden")
except Exception as e:
    print(f"❌ tools_registry.json Fehler: {e}")
    sys.exit(1)
PY

echo ""
echo "✅ Policy-Validierung abgeschlossen – alle Prüfungen erfolgreich."
exit 0
