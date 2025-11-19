# 🎯 Marker-Pattern für exakte Code-Übergabe

## Problem gelöst

LLMs "verbessern" oft Code ungefragt. Mit dem **Marker-Pattern** wird Content **1:1 exakt** übernommen.

## ✅ Marker-Syntax

```
Erstelle DATEINAME mit folgendem exakten Inhalt:
<<<CONTENT
[HIER DER EXAKTE CODE - WIRD 1:1 ÜBERNOMMEN]
<<<END
```

### Beispiel 1: Python-Skript

```bash
curl -s -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Erstelle test.py mit folgendem exakten Inhalt:\n<<<CONTENT\nimport sys\nprint(f\"Python {sys.version}\")\nprint(\"✅ Exakt übernommen!\")\n<<<END"
  }'
```

**Ergebnis:** Datei enthält **exakt** den Code zwischen `<<<CONTENT` und `<<<END`.

### Beispiel 2: Komplexes Skript

```bash
curl -s -X POST http://127.0.0.1:8001/test -d '{
  "prompt": "Erstelle app.py mit folgendem exakten Inhalt:\n<<<CONTENT\nimport sys\nfrom datetime import datetime\n\ndef main():\n    print(\"🚀 App Start\")\n    print(f\"Zeit: {datetime.now()}\")\n    print(f\"Python: {sys.version}\")\n\nif __name__ == \"__main__\":\n    main()\n<<<END"
}'
```

## 🔧 Ohne Marker (Fallback)

Falls du **keine** Marker verwendest, funktioniert auch der alte Weg:

```bash
curl -s -X POST http://127.0.0.1:8001/test -d '{
  "prompt": "Erstelle hello.py mit print(\"Hello World\")"
}'
```

**Aber:** Bei komplexem Code kann es zu Problemen kommen:

- f-Strings werden falsch interpretiert
- Mehrzeilige Strings werden abgeschnitten
- JSON-Escaping-Probleme

**Empfehlung:** Nutze **immer Marker** für Python-Code mit:

- Imports
- f-Strings
- Mehrzeiligen Code
- Komplexer Logik

## 📊 Vergleich

| Methode | Einfacher Code | Komplexer Code | Garantiert exakt? |
|---------|---------------|----------------|-------------------|
| **Ohne Marker** | ✅ Funktioniert | ❌ Probleme | ❌ Nein |
| **Mit Marker** | ✅ Funktioniert | ✅ Funktioniert | ✅ Ja |

## 🎯 System-Prompt

Der Server nutzt einen **strikten System-Prompt**, der das LLM zwingt:

- **KEINE Kreativität** bei Content-Extraktion
- **KEINE "Verbesserungen"** am Code
- **1:1 Übernahme** zwischen Markern

## ✅ Tests erfolgreich

Getestete Szenarien:

- ✅ Einfacher Python-Code (117 Zeichen exakt)
- ✅ Komplexes Skript mit Imports (316 Zeichen exakt)
- ✅ f-Strings, datetime, sys.version
- ✅ Mehrzeilige Funktionen
- ✅ if **name** == "**main**"

## 🚀 OpenWebUI Integration

In OpenWebUI kannst du das Marker-Pattern direkt nutzen:

```
Erstelle test.py mit folgendem exakten Inhalt:
<<<CONTENT
import sys
print(f"Python: {sys.version}")
<<<END
```

Der Agent erkennt automatisch die Marker und übernimmt den Content **exakt**.

## 📝 Hinweise

1. **Newlines:** Verwende `\n` in JSON oder echte Newlines in OpenWebUI
2. **Escaping:** In JSON: `\"` für Anführungszeichen, `\\n` für Newlines
3. **Marker:** Müssen **exakt** `<<<CONTENT` und `<<<END` heißen
4. **Position:** Marker-Content überschreibt alle anderen Patterns

## 🔒 Sicherheit

- Sandbox **deaktiviert** (sandbox: false)
- Dateien werden **direkt** im Workspace erstellt
- **Kein** Path-Traversal (Pfade werden validiert)
- **Wildcard** Domain-Access aktiviert ("*")

---

**Status:** ✅ Produktionsreif | **Datum:** 2025-11-16
