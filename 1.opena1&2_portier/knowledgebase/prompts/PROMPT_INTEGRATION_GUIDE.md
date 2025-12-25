# PORTIER 3.0 – Prompt Integration Guide

**Version:** 1.0
**Datum:** 27. November 2025
**Zweck:** Anleitung zur Integration der Master-Prompts in verschiedene AI-Systeme

---

## Überblick

Dieser Guide erklärt, wie die Master-Prompts für **opena1** und **opena2** in unterschiedlichen Kontexten genutzt werden:

1. **ChatGPT / OpenAI Custom GPTs**
2. **VS Code Copilot**
3. **Agent-Startskripte (Python/FastAPI)**
4. **Neue Entwickler (Onboarding)**
5. **CI/CD-Validierung**

---

## 1. Integration in ChatGPT / OpenAI Custom GPTs

### Schritt 1: Custom GPT erstellen

1. Gehe zu [https://chat.openai.com/gpts/editor](https://chat.openai.com/gpts/editor)
2. Erstelle einen neuen Custom GPT namens **„PORTIER opena1 Coordinator"**
3. Im **System Instructions**-Bereich:

### Schritt 2: Master-Prompt einbinden

Kopiere den Inhalt von:

```
1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md
```

**Wichtig:** Füge zusätzlich die Knowledgebase-Referenzen hinzu:

```markdown
## Zusätzliche Kontextquellen

Nutze die folgenden Dokumente als Referenz (Upload als Knowledge Files):

- KB_OPENA1_COORDINATOR_2025-11-08.md
- KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md
- KB_ARCHIVE_PATTERNS_2025-11-08.md
- PORTIER_SYSTEM_DOCS.md
- PORTIER_3.0_SYSTEM_ARCHITECTURE.md
```

### Schritt 3: Knowledge Files hochladen

Lade die folgenden Dateien in den **Knowledge**-Bereich des Custom GPT:

```
docs/KB_OPENA1_COORDINATOR_2025-11-08.md
docs/KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md
docs/KB_ARCHIVE_PATTERNS_2025-11-08.md
PORTIER_SYSTEM_DOCS.md
PORTIER_3.0_SYSTEM_ARCHITECTURE.md
```

### Schritt 4: Testen

**Test-Prompt:**

```
Ich habe einen Request mit user_query="Sende eine Telegram-Nachricht an User 12345".
Welche Schritte führst du als opena1 durch?
```

**Erwartete Antwort:**

1. Request71-Validierung (Schema-Check)
2. Decision72 (Routing zu kordp mit service_target="telep")
3. CMD-Safepoint vor Dispatch
4. RESP-Safepoint nach Ergebnis
5. Antwort an OpenAI

---

## 2. Integration in VS Code Copilot

### Schritt 1: Copilot Instructions aktualisieren

Öffne:

```
.github/copilot-instructions.md
```

Füge am Anfang hinzu:

```markdown
## Master-Prompts für Agenten

Für vollständige Systemkenntnis der Kern-Services siehe:

- **opena1 (Koordinator):** `1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md`
- **opena2 (Archivator):** `1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA2.md`

Diese Prompts definieren:

- Option-2-Flow (OpenAI → opena1 → opena2 → kordp → Tools)
- Port-Policy (12344–12399 Backend, 8080 UI-only)
- Safepoint-Pflicht (CMD/RESP mit Unicode-Pfeil →)
- Knowledgebase-Hierarchie
- Fehlerverhalten & Security
```

### Schritt 2: Workspace Settings

Erstelle `.vscode/settings.json`:

```json
{
  "github.copilot.advanced": {
    "contextFiles": [
      ".github/copilot-instructions.md",
      "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md",
      "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA2.md",
      "PORTIER_SYSTEM_DOCS.md"
    ]
  }
}
```

### Schritt 3: Chat-Modus nutzen

Im **VS Code Copilot Chat**:

```
@workspace Wie implementiere ich eine neue Route in opena1, die den Option-2-Flow respektiert?
```

Copilot wird die Master-Prompts als Kontext nutzen.

---

## 3. Integration in Agent-Startskripte

### Python/FastAPI-Beispiel

**Datei:** `1.opena1&2_portier/opena1_app.py`

```python
from pathlib import Path

def load_system_prompt() -> str:
    """Lädt den Master-Prompt für opena1 als System-Context."""
    prompt_path = Path(__file__).parent / "knowledge/prompts/MASTER_PROMPT_OPENA1.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Master-Prompt nicht gefunden: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

# Bei OpenAI API Calls
import openai

system_prompt = load_system_prompt()

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
)
```

### Environment Variable

Alternativ als **ENV-Variable**:

```bash
export OPENA1_SYSTEM_PROMPT_PATH="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md"
```

In `config.py`:

```python
import os

SYSTEM_PROMPT_PATH = os.getenv("OPENA1_SYSTEM_PROMPT_PATH")
```

---

## 4. Onboarding neuer Entwickler

### README-Eintrag

Füge in `1.opena1&2_portier/README.md` hinzu:

```markdown
## Neue Entwickler: Startpunkt

Bevor du Code schreibst, lies diese Dokumente:

1. **Master-Prompt opena1:** `knowledge/prompts/MASTER_PROMPT_OPENA1.md`
2. **Master-Prompt opena2:** `knowledge/prompts/MASTER_PROMPT_OPENA2.md`
3. **System-Architektur:** `../../PORTIER_3.0_SYSTEM_ARCHITECTURE.md`
4. **Knowledgebase Index:** `knowledge/processed/master_prompts_core.md`

Diese Dokumente definieren:

- Deine Rolle im System
- Erlaubte/verbotene Patterns
- Option-2-Flow
- Port-Policy
- Safepoint-Konventionen
```

### Onboarding-Checklist

Erstelle `docs/ONBOARDING_CHECKLIST.md`:

```markdown
- [ ] Master-Prompt opena1 gelesen
- [ ] Master-Prompt opena2 gelesen
- [ ] Option-2-Flow verstanden
- [ ] Port-Policy memoriert (12344–12399 Backend, 8080 UI-only)
- [ ] Safepoint-Naming gelernt (Unicode-Pfeil →)
- [ ] Ersten Test-Safepoint erzeugt
- [ ] opena1_app.py gestartet (Port 12344)
- [ ] Health-Check erfolgreich: `curl http://127.0.0.1:12344/health`
```

---

## 5. CI/CD-Validierung

### Pre-Commit Hook

Erstelle `.git/hooks/pre-commit`:

```bash
#!/bin/bash

echo "🔍 Validiere Master-Prompts..."

# Prüfe, ob Master-Prompts existieren
if [ ! -f "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md" ]; then
    echo "❌ FEHLER: MASTER_PROMPT_OPENA1.md fehlt!"
    exit 1
fi

if [ ! -f "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA2.md" ]; then
    echo "❌ FEHLER: MASTER_PROMPT_OPENA2.md fehlt!"
    exit 1
fi

# Prüfe, ob Prompts Unicode-Pfeil enthalten
if ! grep -q "→" "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md"; then
    echo "⚠️  WARNUNG: Unicode-Pfeil → fehlt in MASTER_PROMPT_OPENA1.md"
fi

echo "✅ Master-Prompts validiert"
```

### GitHub Actions Workflow

`.github/workflows/validate-prompts.yml`:

```yaml
name: Validate Master Prompts

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check Master Prompt opena1
        run: |
          if [ ! -f "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md" ]; then
            echo "❌ MASTER_PROMPT_OPENA1.md missing"
            exit 1
          fi

      - name: Check Master Prompt opena2
        run: |
          if [ ! -f "1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA2.md" ]; then
            echo "❌ MASTER_PROMPT_OPENA2.md missing"
            exit 1
          fi

      - name: Validate Unicode Arrow
        run: |
          grep -q "→" 1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA*.md || {
            echo "⚠️  Unicode arrow → missing"
            exit 1
          }
```

---

## 6. Versionskontrolle & Updates

### Semantic Versioning

Master-Prompts folgen **SemVer**:

- **Major (1.0 → 2.0):** Breaking Changes (z.B. Option-2-Flow geändert)
- **Minor (1.0 → 1.1):** Neue Features (z.B. neue Knowledgebase-Dokumente)
- **Patch (1.0.0 → 1.0.1):** Bugfixes (z.B. Tippfehler)

### Änderungsprotokoll

Bei Updates:

1. Version in Header erhöhen
2. Eintrag in `CHANGELOG_PROMPTS.md`:

```markdown
## [1.1.0] - 2025-12-01

### Added

- KB_COMFYUI_INTEGRATION_2025-12-01.md zu Referenzen hinzugefügt

### Changed

- Port-Policy erweitert: ComfyUI Adapter auf Port 12351
```

---

## Best Practices

### ✅ DO

- **Immer** die aktuellste Version der Master-Prompts verwenden
- **Knowledgebase-Hierarchie** respektieren (Priorität 1 > 2 > 3)
- **Unicode-Pfeil →** in allen Safepoint-Dateinamen verwenden
- **Option-2-Flow** niemals bypassen
- **Port-Policy** strikt einhalten (12344–12399)

### ❌ DON'T

- Master-Prompts **nicht** manuell editieren ohne Review
- **Keine** Abkürzungen im Option-2-Flow
- **Keine** Backend-Services auf Port 8080
- **Keine** Secrets in Safepoints (immer `***REDACTED***`)
- **Keine** direkten Tool-Aufrufe (immer via kordp)

---

## Troubleshooting

### Problem: Copilot ignoriert Master-Prompts

**Lösung:**

1. Prüfe `.vscode/settings.json` → `contextFiles` korrekt?
2. Reload VS Code: `Cmd+Shift+P` → "Developer: Reload Window"
3. Teste mit: `@workspace Zeige mir den Option-2-Flow`

### Problem: Custom GPT gibt falsche Antworten

**Lösung:**

1. Prüfe Knowledge Files → alle hochgeladen?
2. System Instructions → Master-Prompt vollständig?
3. Teste mit klarem Kontext: "Du bist opena1. Beschreibe deine Rolle."

### Problem: Agent-Start schlägt fehl

**Lösung:**

```bash
# Prüfe Prompt-Pfad
ls -la 1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md

# Prüfe Encoding
file 1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md
# Sollte: UTF-8 Unicode text

# Prüfe Lesbarkeit
head -20 1.opena1&2_portier/knowledge/prompts/MASTER_PROMPT_OPENA1.md
```

---

## Nächste Schritte

Nach erfolgreicher Integration:

1. **Teste opena1** mit echtem Request71
2. **Validiere Safepoints** in `archivp/YYYY/MM/DD/`
3. **Monitoring aktivieren** (Dashboard Port 12349)
4. **Load-Tests** durchführen
5. **Dokumentation erweitern** (eigene Use-Cases)

---

**Ende Integration Guide**
**Maintainer:** PORTIER 3.0 Team
**Kontakt:** Siehe `PORTIER_3.0_RELEASE.md`
**Status:** ✅ Production-Ready
