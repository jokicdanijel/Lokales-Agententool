# Browser Agent - JSON Quick Reference

## 🎯 Copy & Paste für OpenWebUI

### Tool Definition (für Admin Panel)

```json
{
  "type": "function",
  "function": {
    "name": "browser_agent",
    "description": "Lokale Browser-Automation für Web-Scraping, Datenextraktion und DOM-Manipulation",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": [
            "open",
            "click",
            "type",
            "extract_text",
            "extract_html",
            "query_selector",
            "screenshot",
            "scroll",
            "wait_for"
          ],
          "description": "Browser-Aktion"
        },
        "url": {
          "type": "string",
          "description": "Zielseite URL"
        },
        "selector": {
          "type": "string",
          "description": "CSS/XPath Selektor"
        },
        "text": {
          "type": "string",
          "description": "Text zum eingeben"
        },
        "wait_ms": {
          "type": "integer",
          "default": 500,
          "description": "Wartezeit in ms"
        },
        "return_format": {
          "type": "string",
          "enum": ["text", "html", "json", "raw"],
          "default": "text"
        }
      },
      "required": ["action", "url"]
    }
  }
}
```

---

## 📝 Request/Response Beispiele

### 1. Website öffnen

**Request**:

```json
{
  "action": "open",
  "url": "https://example.com"
}
```

**Response**:

```json
{
  "status": "success",
  "session_id": "sess_12345",
  "page_title": "Example Domain"
}
```

---

### 2. Text extrahieren

**Request**:

```json
{
  "action": "extract_text",
  "url": "https://example.com",
  "selector": "h1"
}
```

**Response**:

```json
{
  "status": "success",
  "text": "Example Domain",
  "elements_found": 1
}
```

---

### 3. Formular ausfüllen & abschicken

**Request 1 - Input klicken**:

```json
{
  "action": "click",
  "url": "https://example.com",
  "selector": "input[name='query']"
}
```

**Request 2 - Text eingeben**:

```json
{
  "action": "type",
  "url": "https://example.com",
  "selector": "input[name='query']",
  "text": "search term"
}
```

**Request 3 - Button klicken**:

```json
{
  "action": "click",
  "url": "https://example.com",
  "selector": "button[type='submit']"
}
```

---

### 4. Screenshot machen

**Request**:

```json
{
  "action": "screenshot",
  "url": "https://example.com"
}
```

**Response**:

```json
{
  "status": "success",
  "screenshot_path": "/storage/screenshot_001.png"
}
```

---

### 5. DOM analysieren

**Request**:

```json
{
  "action": "query_selector",
  "url": "https://example.com",
  "selector": "div.main",
  "return_format": "json"
}
```

**Response**:

```json
{
  "status": "success",
  "dom_analysis": {
    "total_elements": 42,
    "divs": 12,
    "spans": 18,
    "forms": 2
  }
}
```

---

## 🔗 Tool Server URLs

```
GET  /               → Dashboard (HTML)
GET  /health         → Health Check
GET  /status         → Detaillierter Status
GET  /manifest       → Tool Definition (JSON)
POST /call           → Tool Call
POST /execute        → Browser Aktion
```

---

## 💻 Command Line Tests

```bash
# Health Check
curl http://192.168.0.70:8765/health

# Manifest abrufen
curl http://192.168.0.70:8765/manifest | jq

# Website öffnen
curl -X POST http://192.168.0.70:8765/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "open",
    "url": "https://example.com"
  }'

# Text extrahieren
curl -X POST http://192.168.0.70:8765/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "extract_text",
    "url": "https://example.com",
    "selector": "h1"
  }' | jq
```

---

## 🎨 Action Parameter Übersicht

| Action         | Erforderlich        | Optional      | Beispiel                                                         |
| -------------- | ------------------- | ------------- | ---------------------------------------------------------------- |
| open           | url                 | wait_ms       | `{"action":"open","url":"https://..."}`                          |
| click          | url, selector       | wait_ms       | `{"action":"click","url":"...","selector":"button"}`             |
| type           | url, selector, text | wait_ms       | `{"action":"type","url":"...","selector":"input","text":"text"}` |
| extract_text   | url, selector       | return_format | `{"action":"extract_text","url":"...","selector":"p"}`           |
| extract_html   | url, selector       | return_format | `{"action":"extract_html","url":"...","selector":"div"}`         |
| query_selector | url, selector       | return_format | `{"action":"query_selector","url":"...","selector":".class"}`    |
| screenshot     | url                 | -             | `{"action":"screenshot","url":"..."}`                            |
| scroll         | url, selector       | wait_ms       | `{"action":"scroll","url":"...","selector":"div"}`               |
| wait_for       | url, selector       | wait_ms       | `{"action":"wait_for","url":"...","selector":".loaded"}`         |

---

## ⚡ Performance Tipps

1. **Selektoren spezifisch machen**: `.specific-class` statt `.class`
2. **IDs verwenden wenn möglich**: `#element-id` ist schneller
3. **wait_ms anpassen**: Für langsame Seiten erhöhen
4. **Mehrere Aktionen kombinieren**: Batch-Processing
5. **Screenshots nur bei Bedarf**: Spart Ressourcen

---

## 🐛 Häufige Fehler

| Fehler               | Ursache                | Lösung                        |
| -------------------- | ---------------------- | ----------------------------- |
| `SELECTOR_NOT_FOUND` | Element nicht gefunden | Selektor im Browser prüfen    |
| `TIMEOUT`            | Seite lädt zu lange    | `wait_ms` erhöhen             |
| `INVALID_URL`        | URL ungültig           | URL mit `https://` prefix     |
| `BROWSER_ERROR`      | Browser Fehler         | Agent neu starten             |
| `AGENT_UNREACHABLE`  | Agent läuft nicht      | `bash start_browser_agent.sh` |

---

## 📋 Checkliste OpenWebUI Integration

- [ ] Tool Server läuft: `http://192.168.0.70:8765/health`
- [ ] Browser Agent online: `http://192.168.0.70:12350/health`
- [ ] OpenWebUI verfügbar: `http://192.168.0.70:3000`
- [ ] Admin Panel geöffnet: `http://192.168.0.70:3000/admin`
- [ ] External Tools eingestellt
- [ ] Manifest URL: `http://192.168.0.70:8765/manifest`
- [ ] Tool registriert und aktiviert
- [ ] Neuer Chat gestartet
- [ ] Browser Agent Tool sichtbar in Chat
- [ ] Test-Prompt erfolgreich

---

**Mehr Infos**: Siehe `TOOL_JSON_SPECIFICATION.md` für vollständige Dokumentation
