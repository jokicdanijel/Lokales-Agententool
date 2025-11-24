# Browser Agent - OpenWebUI Tool Integration

**Version**: 1.0.0
**Status**: Production Ready
**Zielversion**: OpenWebUI v0.3+

---

## 📋 Übersicht

Dieser Leitfaden erklärt, wie man den **5.opena6_browser** als Tool in **OpenWebUI** registriert und verwendet.

### Was ist ein Tool in OpenWebUI?

Ein Tool ist eine von OpenWebUI-Modellen aufrufbare Funktion, die automatisch basierend auf natürlicher Sprache verwendet wird. Der Browser Agent ermöglicht LLMs, Websites zu öffnen, Daten zu extrahieren und DOM-Operationen durchzuführen.

---

## 🚀 Schnellstart

### 1. Voraussetzungen

- OpenWebUI läuft auf `http://localhost:8080`
- Browser Agent läuft auf `http://localhost:12350`
- Python 3.8+ mit `requests`-Modul

### 2. Tool registrieren

```bash
# Im opena6-Verzeichnis:
bash register_with_openwebui.sh register

# Oder mit benutzerdefinierten URLs:
OPENWEBUI_URL=http://192.168.0.70:8080 bash register_with_openwebui.sh register
```

### 3. Status prüfen

```bash
bash register_with_openwebui.sh status
```

### 4. In OpenWebUI verwenden

1. Öffne OpenWebUI: `http://localhost:8080`
2. Starte ein neues Chat-Gespräch
3. Nutze den Browser Agent automatisch in deinen Prompts:

```
"Öffne https://example.com und extrahiere alle Links"
"Gib mir einen Screenshot von https://news.ycombinator.com"
"Suche auf Google nach 'Python web scraping' und extrahiere die Titel"
```

---

## 📦 Tool-Definition

### Tool-ID
```
opena6_browser_tool
```

### Verfügbare Aktionen

| Aktion | Parameter | Beschreibung |
|--------|-----------|-------------|
| `open` | url | Öffne eine Webseite |
| `click` | url, selector | Klicke auf ein Element |
| `type` | url, selector, text | Gib Text in Formular ein |
| `extract_text` | url, selector | Extrahiere Textinhalt |
| `extract_html` | url, selector | Extrahiere HTML-Code |
| `query_selector` | url, selector | Analysiere DOM-Struktur |
| `screenshot` | url | Mache einen Screenshot |
| `scroll` | url, selector | Scrolle durch Seite |
| `wait_for` | url, selector, wait_ms | Warte auf Element |

### Input-Schema

```json
{
  "action": "string",           // Erforderlich - siehe Tabelle oben
  "url": "string",              // Erforderlich - Zielseite
  "selector": "string",         // Optional - CSS/XPath Selektor
  "text": "string",             // Optional - Text zum eingeben
  "wait_ms": "integer",         // Optional - Wartezeit (default: 500)
  "return_format": "string"     // Optional - text|html|json|raw (default: text)
}
```

### Output-Schema

```json
{
  "status": "string",           // success|error
  "data": "object",             // Resultatdaten
  "timestamp": "string",        // ISO 8601 Timestamp
  "session_id": "string"        // Browser Session ID
}
```

---

## 🔧 Installation & Konfiguration

### Option 1: Automatisch (Empfohlen)

```bash
cd LocalAgent-Pro/opena6
bash register_with_openwebui.sh register
```

Die Registrierung erfolgt automatisch mit Standard-Konfiguration.

### Option 2: Manuell

```bash
# Python-Skript direkt ausführen
python3 openwebui_tool_registration.py \
  --action register \
  --openwebui-url http://localhost:8080 \
  --agent-url http://localhost:12350
```

### Option 3: Programmmatisch

```python
from openwebui_tool_registration import OpenWebUIToolManager

manager = OpenWebUIToolManager(
    openwebui_url="http://localhost:8080"
)
manager.agent_url = "http://localhost:12350"
manager.register_tool()
```

---

## 📝 Verwendungsbeispiele

### Beispiel 1: Text-Extraktion

**Prompt in OpenWebUI:**
```
Gib mir einen Überblick über die aktuellen Nachrichten auf https://www.bbc.com/news
```

**Intern (Modell-Generiert):**
```json
{
  "action": "extract_text",
  "url": "https://www.bbc.com/news",
  "selector": "h2.article-title",
  "return_format": "text"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "text": "Breaking News: ...",
    "elements_found": 15
  },
  "timestamp": "2025-11-24T18:30:00Z"
}
```

### Beispiel 2: Form-Ausfüllung

**Prompt:**
```
Fülle das Suchformular auf Google aus mit "climate change" und schicke es ab
```

**Intern:**
```json
[
  {
    "action": "open",
    "url": "https://www.google.com"
  },
  {
    "action": "click",
    "url": "https://www.google.com",
    "selector": "input[name='q']"
  },
  {
    "action": "type",
    "url": "https://www.google.com",
    "selector": "input[name='q']",
    "text": "climate change"
  },
  {
    "action": "click",
    "url": "https://www.google.com",
    "selector": "button[type='submit']"
  }
]
```

### Beispiel 3: Screenshot

**Prompt:**
```
Zeige mir einen Screenshot der Microsoft-Homepage
```

**Intern:**
```json
{
  "action": "screenshot",
  "url": "https://www.microsoft.com"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "screenshot_path": "/storage/screenshot_001.png",
    "url": "https://www.microsoft.com"
  },
  "timestamp": "2025-11-24T18:35:00Z"
}
```

---

## 🔐 Sicherheit & Authentifizierung

### Bearer Token

Der Browser Agent verwendet Bearer Token-Authentifizierung:

```
Authorization: Bearer sk_opena6_browser_v3_production
```

Alle OpenWebUI-Anfragen enthalten diesen Token automatisch.

### Sicherheitsregeln

✅ **ERLAUBT:**
- HTTP/HTTPS Requests zu öffentlichen Websites
- DOM-Manipulation (Click, Type, Scroll)
- Text/HTML-Extraktion
- Screenshots

❌ **VERBOTEN:**
- Zugriff auf localhost/interne Services
- Dateioperationen
- Beliebiger JavaScript-Code
- Netzwerk-Requests außerhalb des Browsers

### Validierung

OpenWebUI validiert automatisch:
- Bearer Token
- URL-Format und Sicherheit
- Aktion-Parameter
- Selektor-Syntax

---

## 🛠️ Verwaltung

### Tool registrieren

```bash
bash register_with_openwebui.sh register
```

### Tool-Status prüfen

```bash
bash register_with_openwebui.sh status
```

Output:
```
ℹ️  Tool-Status:
   openwebui_available: True
   agent_available: True
   tool_id: opena6_browser_tool
   tool_name: Browser Agent
   agent_url: http://localhost:12350
   openwebui_url: http://localhost:8080
   timestamp: 2025-11-24T18:40:00Z
```

### Tool aktualisieren

```bash
bash register_with_openwebui.sh update
```

### Tool deregistrieren

```bash
bash register_with_openwebui.sh unregister
```

### Gesundheitsprüfung

```bash
bash register_with_openwebui.sh health
```

Output:
```
ℹ️  Browser Agent: ONLINE (http://localhost:12350)
ℹ️  OpenWebUI: ONLINE (http://localhost:8080)
✅ Beide Services sind verfügbar - Registrierung möglich
```

---

## 📊 Architektur-Diagramm

```
┌─────────────────────────────────────────────────────────┐
│                     OpenWebUI (Port 8080)               │
│                                                         │
│  ┌──────────────┐         ┌──────────────────────┐    │
│  │   Chat UI    │────────▶ │  Tool Management     │    │
│  └──────────────┘         │                      │    │
│                           │  • register_tool()   │    │
│                           │  • call_tool()       │    │
│                           │  • update_tool()     │    │
│                           └──────────┬───────────┘    │
└─────────────────────────────────────┼─────────────────┘
                                      │
                                      │ HTTP POST
                                      │ /execute
                                      │
┌─────────────────────────────────────▼──────────────────┐
│            Browser Agent (Port 12350)                  │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │     openwebui_tool_registration.py              │ │
│  │                                                 │ │
│  │  • Tool Definition                             │ │
│  │  • OpenWebUIToolManager                        │ │
│  │  • BrowserAgentChatHandler                     │ │
│  │  • Bearer Token Validation                     │ │
│  └──────────────────┬───────────────────────────────┘ │
│                     │                                  │
│  ┌──────────────────▼───────────────────────────────┐ │
│  │     BrowserAgent (main.py)                       │ │
│  │                                                 │ │
│  │  • /execute - Action Handler                   │ │
│  │  • /health  - Status Endpoint                  │ │
│  │  • 9 Actions (open, click, type, ...)         │ │
│  └──────────────────┬───────────────────────────────┘ │
│                     │                                  │
│  ┌──────────────────▼───────────────────────────────┐ │
│  │     BrowserEngine (browser_engine.py)           │ │
│  │                                                 │ │
│  │  • Playwright/Selenium Wrapper                 │ │
│  │  • Session Management                          │ │
│  │  • DOM Manipulation                            │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🔍 Debugging

### Tool-Status anzeigen

```bash
bash register_with_openwebui.sh status
```

### Logs anschauen

```bash
# Browser Agent Logs
tail -f LocalAgent-Pro/opena6/logs/opena6.log

# OpenWebUI Logs
tail -f ~/openwebui/logs/backend.log
```

### Test-Request manuell

```bash
curl -X POST http://localhost:12350/execute \
  -H "Authorization: Bearer sk_opena6_browser_v3_production" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "open",
    "url": "https://example.com"
  }'
```

### Häufige Fehler

| Fehler | Ursache | Lösung |
|--------|--------|--------|
| Connection refused | Agent/OpenWebUI läuft nicht | `bash register_with_openwebui.sh health` |
| 401 Unauthorized | Falscher Bearer Token | Token in `register_with_openwebui.sh` prüfen |
| Tool not callable | Tool nicht registriert | `bash register_with_openwebui.sh register` |
| Selector not found | CSS Selektor ungültig | Selektor im Browser Inspector prüfen |
| Timeout | Seite lädt zu lange | `wait_ms` Parameter erhöhen |

---

## 📚 Weitere Ressourcen

- [Browser Agent README](README.md)
- [CMD Schema](CMD_SCHEMA.md)
- [Dispatcher Client](dispatcher_client.py)
- [Browser Engine](browser_engine.py)
- [Test Suite](tests/test_browser_agent.py)

---

## ✅ Checkliste für Produktionseinsatz

- [ ] Browser Agent läuft auf Port 12350
- [ ] OpenWebUI läuft auf Port 8080
- [ ] `bash register_with_openwebui.sh health` zeigt beide Services als ONLINE
- [ ] `bash register_with_openwebui.sh register` erfolgreich abgeschlossen
- [ ] `bash register_with_openwebui.sh status` zeigt "True" für beide Services
- [ ] Test-Prompt in OpenWebUI funktioniert
- [ ] Bearer Token in Konfiguration gespeichert
- [ ] SSL/HTTPS konfiguriert (optional, für Produktionseinsatz empfohlen)

---

## 📞 Support & Kontakt

Bei Fragen oder Problemen:

1. Prüfe die Logs: `LocalAgent-Pro/opena6/logs/opena6.log`
2. Führe Gesundheitsprüfung durch: `bash register_with_openwebui.sh health`
3. Konsultiere die [CMD Schema](CMD_SCHEMA.md) Dokumentation
4. Überprüfe die [Test Suite](tests/test_browser_agent.py)

---

**Stand**: 24. November 2025
**Autor**: PORTIER 3.0 System
**Status**: ✅ Production Ready
