#!/usr/bin/env bash
# Portier/ELION Policy-Validator (CI + lokal)
# - 8080 ausschließlich für OpenWebUI (Loopback)
# - Erlaubte Ports: 12344–12399
# - Keine Platzhalter/TODO im produktiven Code
# - Agenten-Dateien vorhanden + ausführbar
# - Unicode-Pfeil „→" in Safepoint-Dateinamen-Helfern (sofern vorhanden)

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "[Policy] Projektwurzel: $ROOT"

# 1) 8080 nur in OpenWebUI-Kontext
echo "[Policy] Prüfe 8080-Exklusivität (nur produktive Agenten) …"
violations=$(find "$ROOT"/{4,5,6,7}.*_agent -type f \( -name "*.py" -o -name "*.sh" \) -exec grep -l ":8080" {} \; 2>/dev/null || true)
if [[ -n "$violations" ]]; then
  echo "[FAIL] 8080 in Agent-Code (nicht OpenWebUI) gefunden:"
  echo "$violations"
  exit 2
fi
echo "[OK] 8080 nicht in Agenten-Code verwendet."

# 2) Verbotene TODO/Platzhalter (nur Agenten 4-7, 1.portier)
echo "[Policy] Prüfe auf TODO/Platzhalter …"
if find "$ROOT"/{1,4,5,6,7}.*_agent -type f \( -name "*.py" -o -name "*.sh" \) 2>/dev/null | \
   xargs grep -l '\b(TODO|FIXME|PLACEHOLDER)\b' 2>/dev/null >/dev/null; then
  echo "[FAIL] TODO/Platzhalter im Produktionscode gefunden:"
  find "$ROOT"/{1,4,5,6,7}.*_agent -type f \( -name "*.py" -o -name "*.sh" \) 2>/dev/null | \
  xargs grep -Hn '\b(TODO|FIXME|PLACEHOLDER)\b' 2>/dev/null || true
  exit 3
fi
echo "[OK] Keine TODO/Platzhalter im Code."

# 3) Agenten vorhanden + Startskripte
echo "[Policy] Prüfe Agenten opena4–opena7 …"
declare -a agents=(
  "4.telegram_agent"
  "5.vscode_agent"
  "6.mail_agent"
  "7.whatsapp_agent"
)
for a in "${agents[@]}"; do
  [[ -f "$ROOT/$a/main_agent.py" ]] || { echo "[FAIL] fehlt: $a/main_agent.py"; exit 4; }
  [[ -f "$ROOT/$a/skripte/start_agent.sh" ]] || { echo "[FAIL] fehlt: $a/skripte/start_agent.sh"; exit 4; }
done
echo "[OK] Agenten-Dateien vorhanden."

# 4) Safepoint-Pfeil (best effort – statische Prüfung)
echo "[Policy] Prüfe Unicode-Pfeil in Archivator-/Safepoint-Helfern …"
if grep -qr '→' "$ROOT/1.opena1&2_portier" 2>/dev/null; then
  echo "[OK] Unicode-Pfeil '→' referenziert."
else
  echo "[WARN] Kein Unicode-Pfeil '→' gefunden. Prüfe, ob Safepoint-Namensfunktion korrekt eingebaut ist."
fi

# 5) Schneller Syntaxcheck Python (nur offensichtliche Fehler)
echo "[Policy] Python Syntax-Check …"
python3 -c "
import py_compile, glob, sys
errors = False
for f in glob.glob('$ROOT/{1,4,5,6,7}.*_agent/**/*.py', recursive=True):
    try:
        py_compile.compile(f, doraise=True)
    except Exception as e:
        print(f'[FAIL] Syntax: {f}: {e}')
        errors = True
if errors:
    sys.exit(5)
print('[OK] Python-Dateien kompilieren.')
" || exit 5

echo "[PASS] Policy-Validator grün ✔"
