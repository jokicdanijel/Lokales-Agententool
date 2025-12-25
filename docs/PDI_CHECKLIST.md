[PDI-ACTIVE: TRUE | CHECKLIST | GITHUB-CHECK: PASS]

# PDI-Checkliste & Quick-Start

## 1. Pre-PDI-Checkliste (Vorbereitung)

```
☐ Alle Inputs dokumentiert
☐ Zielgruppe definiert (Developer, DevOps, Architect?)
☐ Umfang geklärt (wie viele Kapitel/Module?)
☐ Timeline verfügbar (ca. 15–20 Min pro Kapitel)
☐ Stakeholder informiert
☐ PDI-Core-Modul verfügbar
```

---

## 2. Pro-Artifact-Checkliste

Für jede Datei, die du erzeugst (Code, Doc, Config):

### Phase 1: Vorbereitung

```
☐ Artifact-ID definiert (z.B. "agents_auto_register.sh")
☐ Artifact-Type bekannt (bash | python | markdown | json | yaml)
☐ Content verfügbar
☐ Dependencies dokumentiert
```

### Phase 2: PDI-Validierung durchlaufen

```
☐ Module 1–6 durchlaufen (LINGUISTIC, TECHNICAL, CORRECTION, ANALYTICS, CONTROL, GITHUB)
☐ Alle Gates passed (1–6 ✓)
☐ Keine kritischen Errors
☐ Suggestions in Backlog (optional)
☐ Validation-Log gespeichert
```

### Phase 3: Freigabe

```
☐ PDI-Header hinzugefügt
☐ Validation-Report exportiert
☐ Artifact in validated-store
☐ Documentation aktualisiert
☐ Commit mit PDI-Tag
```

---

## 3. Gate-Spezifische Checklisten

### Gate 1: Syntaxprüfung (GITHUB)

```
Code-Type: Python
  ☐ python -m py_compile <file>  # Kein SyntaxError
  ☐ Imports vorhanden
  ☐ Keine unvollständigen Statements

Code-Type: Bash
  ☐ bash -n <file>               # Keine Bash-Fehler
  ☐ Korrekte Quotes
  ☐ Variablen definiert

Config-Type: JSON
  ☐ jq . <file> > /dev/null      # Valid JSON
  ☐ Keine trailing commas

Config-Type: YAML
  ☐ yamllint <file>              # Valid YAML
  ☐ Indentation konsistent
```

### Gate 2: Linguistische Validierung

````
Alle Artifact-Types:
  ☐ Verständlich für Zielgruppe
  ☐ Terminologie konsistent
  ☐ Keine Tippfehler (Spelling)
  ☐ Grammatik korrekt (wo relevant)
  ☐ Vollständigkeit check (nicht unvollständig)

Doc-Type:
  ☐ Headers (#, ##, ###) hierarchisch
  ☐ Code-Blöcke mit Sprache-Tag (```python, ```bash)
  ☐ Links funktional
  ☐ Bilder mit Alt-Text
````

### Gate 3: Technische Validierung

```
Alle Artifact-Types:
  ☐ Schnittstellen dokumentiert
  ☐ Parameter/Argumente erklärt
  ☐ Return-Types definiert
  ☐ Error-Cases dokumentiert
  ☐ Performance-Anforderungen erfüllt

Python-Code:
  ☐ Type-Hints vorhanden (@dataclass, def func(x: int) -> str)
  ☐ Docstrings vorhanden
  ☐ Error-Handling präsent (try/except)
  ☐ Logging statt print()

Bash-Code:
  ☐ set -euo pipefail am Anfang
  ☐ Funktionen dokumentiert
  ☐ Error-Messages aussagekräftig
  ☐ Exit-Codes korrekt (0 = success)
```

### Gate 4: Logik-Prüfung (GITHUB)

```
Alle Artifact-Types:
  ☐ Keine offensichtlichen Fehler
  ☐ Edge-cases berücksichtigt (empty input, null, etc.)
  ☐ Loop-Invarianten korrekt
  ☐ State-Transitions sauber

Python-Code:
  ☐ Off-by-one Fehler? Nein
  ☐ Infinite Loops? Nein
  ☐ Mutable Default-Arguments? Nein

Bash-Code:
  ☐ Globbing-Fehler? Nein
  ☐ Quoting-Fehler? Nein
  ☐ cd ohne Fehlercheck? Nein
```

### Gate 5: Sicherheitsprüfung (GITHUB)

```
Alle Artifact-Types:
  ☐ Keine hardcodierten Secrets (Keys, Tokens, Passwords)
  ☐ Keine eval()/exec() Calls
  ☐ Input-Validierung vorhanden
  ☐ Auth/Authz-Checks vorhanden (falls relevant)
  ☐ Keine SQL-Injection möglich

Python-Code:
  ☐ Kein eval(), exec(), __import__()
  ☐ Pickle nur von trusted sources
  ☐ Command-Injection nicht möglich (no shell=True ohne Escaping)

Bash-Code:
  ☐ Keine shell-Expansionen ohne Quoting
  ☐ Kein eval oder dynamic code
  ☐ find ... | xargs: -0 Flag vorhanden?
```

### Gate 6: Integrations-Prüfung

```
Code-Artifact:
  ☐ Abhängigkeiten auflösbar
  ☐ Versionsnummern korrekt
  ☐ Keine zirkulären Abhängigkeiten
  ☐ Mit bestehenden APIs kompatibel
  ☐ Keine Konflikte mit anderen Modulen

Dokumentation:
  ☐ Verweise auf bestehende Docs
  ☐ Links nicht broken
  ☐ Konsistent mit anderen Dokumenten
```

---

## 4. PDI-Header-Template

Kopiere dies an den Anfang jeder Datei und fülle aus:

### Python/Bash

```
"""
[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
[MODULES: LINGUISTIC,TECHNICAL,CORRECTION,ANALYTICS,CONTROL,GITHUB]
[GATES: 1,2,3,4,5,6 ✓]
[VALIDATION-TIMESTAMP: 2025-11-09T12:34:56Z]
[ARTIFACT-ID: agents_auto_register.sh]
[AUTHOR: danijel]
[REVIEWED-BY: pdi_core]
"""
```

### Markdown

```markdown
[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]
[MODULES: LINGUISTIC,TECHNICAL]
[GATES: 2,3,6 ✓]
[VALIDATION-TIMESTAMP: 2025-11-09T12:34:56Z]

# Dokumentation

...
```

---

## 5. Quick-Start: PDI für ein neues Projekt

### Schritt 1: Projekt initialisieren

```bash
cd /path/to/project
python3 << 'EOF'
from pdi_core import PDICore

pdi = PDICore("MyProject", "myproject-2025")
pdi.process_input(
    "Create auto-discovery agent registration system",
    author="danijel"
)
pdi.create_chapter_plan(num_chapters=5)

print(pdi.export_manifest("PDI_MANIFEST.json"))
EOF
```

### Schritt 2: Artifact validieren

```bash
python3 << 'EOF'
from pdi_core import PDICore

pdi = PDICore("MyProject", "myproject-2025")
pdi.process_input("...", author="danijel")

# Read artifact content
with open("agents_auto_register.sh") as f:
    content = f.read()

# Validate through all modules
results = pdi.validate_artifact(
    "agents_auto_register.sh",
    "bash",
    content
)

# Check results
if all(r.is_valid for r in results.values()):
    print("✓ All validations passed!")
    # Export with header
    validated = pdi.export_validated_artifact("agents_auto_register.sh")
    print(validated[:200])
else:
    print("✗ Some validations failed:")
    for name, result in results.items():
        if not result.is_valid:
            print(f"  {name}: {result.errors}")
EOF
```

### Schritt 3: Report generieren

```bash
python3 << 'EOF'
from pdi_core import PDICore
import json

pdi = PDICore("MyProject", "myproject-2025")
pdi.process_input("...", author="danijel")

# Validate artifacts (...)

report = pdi.get_validation_report()
print(json.dumps(report, indent=2))

# Save to file
with open("PDI_VALIDATION_REPORT.json", "w") as f:
    json.dump(report, f, indent=2)
EOF
```

---

## 6. Troubleshooting

| Problem               | Diagnose                      | Lösung                                            |
| --------------------- | ----------------------------- | ------------------------------------------------- |
| Gate 1 fehlgeschlagen | `python -m py_compile <file>` | Syntax-Fehler korrigieren                         |
| Gate 2 fehlgeschlagen | Lese Errors in result         | Text überarbeiten, Typos fixen                    |
| Gate 3 fehlgeschlagen | `flake8 <file>`               | Code-Style anpassen                               |
| Gate 4 fehlgeschlagen | Logik-Fehler im Trace         | Edge-Cases hinzufügen                             |
| Gate 5 fehlgeschlagen | Security-Warnings lesen       | eval(), hardcoded secrets entfernen               |
| Gate 6 fehlgeschlagen | Dependency-Conflicts?         | Versionen anpassen oder Conflict-Report schreiben |

---

## 7. Best Practices

### 1. Early & Often validieren

```
Nicht: Am Ende alles auf einmal validieren
Ja:    Nach jedem Kapitel validieren
```

### 2. Feedback ernst nehmen

```
Errors = Must fix
Warnings = Should fix
Suggestions = Nice to have (backlog)
```

### 3. Validation-Logs speichern

```bash
# Speichere nach jeder Validierung
pdi.get_validation_report() > PDI_REPORT_$(date +%s).json
```

### 4. PDI-Header bei Commit

```bash
git commit -m "feat: add agents_auto_register.sh [PDI-ACTIVE: PASS]"
```

---

## 8. Integration mit GitHub Actions

```yaml
# .github/workflows/pdi-validate.yml
name: PDI Validation

on: [push, pull_request]

jobs:
  pdi-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install PDI
        run: |
          pip install -e .  # or cp pdi_core.py to project

      - name: Run PDI Validation
        run: |
          python3 << 'EOF'
          from pdi_core import PDICore
          import glob

          pdi = PDICore("ELION-Dashboard", "elion-2025")
          pdi.process_input("GitHub Actions Check")

          # Find all artifacts to validate
          for file in glob.glob("**/*.py", recursive=True):
              with open(file) as f:
                  pdi.validate_artifact(file, "python", f.read())

          report = pdi.get_validation_report()

          if report['failed'] > 0:
              print(f"❌ {report['failed']} artifacts failed")
              exit(1)
          else:
              print(f"✅ All {report['passed']} artifacts passed")
              exit(0)
          EOF

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: pdi-report
          path: PDI_VALIDATION_REPORT.json
```

---

## 9. PDI-Befehle (CLI)

```bash
# Validate single file
python pdi_core.py validate agents_auto_register.sh

# Validate all Python files
python pdi_core.py validate "**/*.py"

# Generate report
python pdi_core.py report elion-2025

# Export manifest
python pdi_core.py export:manifest elion-2025

# Dry-run (simulate ohne zu committen)
python pdi_core.py dry-run agents_auto_register.sh
```

---

## 10. Status quo prüfen

Bevor du loslaufen: Führe diesen Check aus

```bash
python3 << 'EOF'
from pdi_core import PDICore

print("✓ PDI-Core importierbar")

pdi = PDICore("test", "test-2025")
print("✓ PDICore instantiierbar")

pdi.process_input("test input")
print("✓ process_input funktioniert")

pdi.create_chapter_plan(3)
print("✓ Chapter plan erstellbar")

results = pdi.validate_artifact("test", "python", "def test(): pass")
print(f"✓ Validierung durchführbar ({len(results)} modules)")

report = pdi.get_validation_report()
print(f"✓ Report generierbar ({report['artifacts_validated']} artifacts)")

print("\n✅ PDI-Core fully functional!")
EOF
```

---

**Status:** [PDI-ACTIVE: TRUE | CHECKLIST-COMPLETE | READY-TO-USE]
**Last Updated:** 2025-11-09
