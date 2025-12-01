# Browser Agent - OpenWebUI Tool Integration (JSON Specification)

**Version**: 1.0.0
**Format**: OpenAI Function Calling Schema
**Status**: Production Ready

---

## 📋 Complete Tool Manifest (JSON)

```json
{
  "type": "function",
  "function": {
    "name": "browser_agent",
    "description": "Lokale Browser-Automation für Web-Scraping, Datenextraktion und DOM-Manipulation. Wird vom PORTIER 3.0 System bereitgestellt.",
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
          "description": "Zu führende Browser-Aktion"
        },
        "url": {
          "type": "string",
          "description": "Zielseite URL (z.B. https://example.com)"
        },
        "selector": {
          "type": "string",
          "description": "CSS oder XPath Selektor"
        },
        "text": {
          "type": "string",
          "description": "Text zum eingeben (für 'type' Aktion)"
        },
        "wait_ms": {
          "type": "integer",
          "default": 500,
          "description": "Wartezeit nach Aktion in Millisekunden"
        },
        "return_format": {
          "type": "string",
          "enum": [
            "text",
            "html",
            "json",
            "raw"
          ],
          "default": "text",
          "description": "Format der Rückgabe"
        }
      },
      "required": [
        "action",
        "url"
      ]
    }
  }
}
```

---

## 🔧 API Endpoints

### 1. GET /manifest

**Zweck**: Tool Definition für OpenWebUI laden

```bash
curl http://192.168.0.70:8765/manifest
```

**Response**:

```json
{
  "type": "function",
  "function": {
    "name": "browser_agent",
    "description": "...",
    "parameters": { ... }
  }
}
```

### 2. GET /health

**Zweck**: Health Check

```bash
curl http://192.168.0.70:8765/health
```

**Response**:

```json
{
  "status": "ok",
  "timestamp": "2025-11-24T23:37:04.301042",
  "service": "Browser Agent Tool Server",
  "version": "1.0.0"
}
```

### 3. GET /status

**Zweck**: Detaillierter Server Status

```bash
curl http://192.168.0.70:8765/status
```

**Response**:

```json
{
  "status": "operational",
  "uptime": "00:05:12",
  "calls_total": 42,
  "last_call": "2025-11-24T23:42:15.123456",
  "timestamp": "2025-11-24T23:42:27.456789"
}
```

### 4. POST /call

**Zweck**: Tool Call von OpenWebUI

```bash
curl -X POST http://192.168.0.70:8765/call \
  -H "Content-Type: application/json" \
  -d '{
    "function": {
      "name": "browser_agent",
      "arguments": {
        "action": "open",
        "url": "https://example.com"
      }
    }
  }'
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "action": "open",
    "url": "https://example.com",
    "session_id": "sess_12345",
    "timestamp": "2025-11-24T23:42:30.123456"
  }
}
```

### 5. POST /execute

**Zweck**: Direkte Browser-Aktion ausführen

```bash
curl -X POST http://192.168.0.70:8765/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "extract_text",
    "url": "https://example.com",
    "selector": "h1",
    "return_format": "text"
  }'
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "text": "Welcome to Example",
    "elements_found": 1,
    "selector_matched": true
  }
}
```

---

## 📝 Action Specifications

### 1. OPEN - Browser öffnen

**JSON Request**:

```json
{
  "action": "open",
  "url": "https://example.com",
  "wait_ms": 500
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "open",
  "url": "https://example.com",
  "session_id": "sess_12345",
  "page_title": "Example Domain",
  "timestamp": "2025-11-24T23:45:00Z"
}
```

---

### 2. CLICK - Element klicken

**JSON Request**:

```json
{
  "action": "click",
  "url": "https://example.com",
  "selector": "button.submit",
  "wait_ms": 500
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "click",
  "selector": "button.submit",
  "executed": true,
  "timestamp": "2025-11-24T23:45:05Z"
}
```

---

### 3. TYPE - Text eingeben

**JSON Request**:

```json
{
  "action": "type",
  "url": "https://example.com",
  "selector": "input#email",
  "text": "user@example.com",
  "wait_ms": 300
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "type",
  "selector": "input#email",
  "text_length": 18,
  "element_focused": true,
  "timestamp": "2025-11-24T23:45:10Z"
}
```

---

### 4. EXTRACT_TEXT - Text extrahieren

**JSON Request**:

```json
{
  "action": "extract_text",
  "url": "https://example.com",
  "selector": "p.description",
  "return_format": "text"
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "extract_text",
  "text": "This is the extracted text content from the page...",
  "selector_matched": true,
  "elements_found": 1,
  "timestamp": "2025-11-24T23:45:15Z"
}
```

---

### 5. EXTRACT_HTML - HTML extrahieren

**JSON Request**:

```json
{
  "action": "extract_html",
  "url": "https://example.com",
  "selector": "div.content",
  "return_format": "html"
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "extract_html",
  "html": "<div class=\"content\"><p>Content here</p></div>",
  "elements_found": 1,
  "size_bytes": 456,
  "timestamp": "2025-11-24T23:45:20Z"
}
```

---

### 6. QUERY_SELECTOR - DOM analysieren

**JSON Request**:

```json
{
  "action": "query_selector",
  "url": "https://example.com",
  "selector": "div.main",
  "return_format": "json"
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "query_selector",
  "dom_analysis": {
    "total_elements": 42,
    "divs": 12,
    "spans": 18,
    "forms": 2,
    "inputs": 5,
    "buttons": 3
  },
  "timestamp": "2025-11-24T23:45:25Z"
}
```

---

### 7. SCREENSHOT - Screenshot machen

**JSON Request**:

```json
{
  "action": "screenshot",
  "url": "https://example.com"
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "screenshot",
  "screenshot_path": "/storage/screenshot_12345.png",
  "screenshot_url": "http://localhost:8765/screenshots/screenshot_12345.png",
  "width": 1920,
  "height": 1080,
  "timestamp": "2025-11-24T23:45:30Z"
}
```

---

### 8. SCROLL - Seite scrollen

**JSON Request**:

```json
{
  "action": "scroll",
  "url": "https://example.com",
  "selector": "div.content",
  "wait_ms": 300
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "scroll",
  "scrolled": true,
  "scroll_position": 500,
  "page_height": 2500,
  "timestamp": "2025-11-24T23:45:35Z"
}
```

---

### 9. WAIT_FOR - Auf Element warten

**JSON Request**:

```json
{
  "action": "wait_for",
  "url": "https://example.com",
  "selector": "div.loaded",
  "wait_ms": 5000
}
```

**JSON Response**:

```json
{
  "status": "success",
  "action": "wait_for",
  "element_appeared": true,
  "wait_duration_ms": 2345,
  "timestamp": "2025-11-24T23:45:40Z"
}
```

---

## 🌐 OpenWebUI Integration JSON

### Tool Registration Format

Für OpenWebUI Admin Panel zu kopieren:

```json
{
  "type": "function",
  "function": {
    "name": "browser_agent",
    "description": "Automatisierte Browser-Kontrolle für Web-Scraping, Datenextraktion und DOM-Manipulation mit lokalem PORTIER 3.0 Browser Agent",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["open", "click", "type", "extract_text", "extract_html", "query_selector", "screenshot", "scroll", "wait_for"],
          "description": "Browser-Aktion ausführen"
        },
        "url": {
          "type": "string",
          "description": "Zielseite URL (https://example.com)"
        },
        "selector": {
          "type": "string",
          "description": "CSS oder XPath Selektor"
        },
        "text": {
          "type": "string",
          "description": "Text zum eingeben"
        },
        "wait_ms": {
          "type": "integer",
          "default": 500,
          "description": "Wartezeit in Millisekunden"
        },
        "return_format": {
          "type": "string",
          "enum": ["text", "html", "json", "raw"],
          "default": "text",
          "description": "Format der Rückgabe"
        }
      },
      "required": ["action", "url"]
    }
  }
}
```

---

## 🔗 OpenWebUI External Tool Configuration

Zu konfigurieren in: **Admin → Settings → External Tools**

```json
{
  "name": "Browser Agent",
  "type": "external_function",
  "enabled": true,
  "url": "http://192.168.0.70:8765/manifest",
  "auth_required": false,
  "timeout": 30,
  "rate_limit": 1000,
  "rate_limit_period": 60,
  "models": ["*"],
  "description": "Lokale Browser-Automation via PORTIER 3.0 System"
}
```

---

## 📊 Error Response Format

Alle Fehler folgen diesem JSON-Format:

```json
{
  "status": "error",
  "error_code": "INVALID_SELECTOR",
  "message": "CSS selector '.nonexistent' did not match any elements",
  "action": "extract_text",
  "url": "https://example.com",
  "details": {
    "selector": ".nonexistent",
    "attempts": 1,
    "timeout_ms": 5000
  },
  "timestamp": "2025-11-24T23:50:00Z"
}
```

### Error Codes

| Code | Bedeutung | HTTP Status |
|------|-----------|------------|
| INVALID_JSON | Ungültiges JSON Format | 400 |
| INVALID_ACTION | Unbekannte Aktion | 400 |
| INVALID_URL | URL ist ungültig | 400 |
| SELECTOR_NOT_FOUND | Selektor passt zu keinem Element | 404 |
| TIMEOUT | Operation zeitlich überschritten | 504 |
| BROWSER_ERROR | Browser Fehler | 500 |
| AGENT_UNREACHABLE | Browser Agent nicht erreichbar | 503 |

---

## 🚀 Integration Steps

### Schritt 1: Tool Server starten

```bash
bash start_tool_server.sh
# oder
python3 tool_server.py --host 0.0.0.0 --port 8765
```

### Schritt 2: Manifest testen

```bash
curl http://192.168.0.70:8765/manifest
```

### Schritt 3: OpenWebUI konfigurieren

1. Öffne: `http://192.168.0.70:3000/admin`
2. Gehe zu: Settings → External Tools
3. Klick: "Add External Tool"
4. URL eingeben: `http://192.168.0.70:8765/manifest`
5. Speichern

### Schritt 4: Chat testen

```
Prompt: "Öffne https://example.com und zeige mir die Hauptüberschrift"

Das Modell ruft automatisch auf:
{
  "action": "open",
  "url": "https://example.com"
}

Dann:
{
  "action": "extract_text",
  "url": "https://example.com",
  "selector": "h1"
}
```

---

## 📚 Weitere URLs

- **Dashboard**: <http://localhost:8765/>
- **Manifest**: <http://localhost:8765/manifest>
- **Health**: <http://localhost:8765/health>
- **Status**: <http://localhost:8765/status>
- **Tool Repo**: /home/danijel-jd/.../LocalAgent-Pro/opena6/

---

**Stand**: 24. November 2025
**System**: PORTIER 3.0 Multi-Agent Platform
**Status**: ✅ Production Ready
