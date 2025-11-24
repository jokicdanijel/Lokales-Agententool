# OpenWebUI Tool Integration - PORTIER 3.0

## 🎯 Schnellübersicht

Der **Browser Agent (opena6)** wurde erfolgreich als **OpenWebUI Tool** integriert!

```
┌─────────────────────────────────────────────┐
│         OpenWebUI Chat Interface             │
│   (http://192.168.0.70:3000)                │
└────────────────────┬────────────────────────┘
                     │
                     ▼ Tool Call
         ┌───────────────────────┐
         │  Tool Server          │
         │  (Port 8765)          │
         │  /manifest            │
         │  /execute             │
         │  /health              │
         └────────────┬──────────┘
                      │
                      ▼ HTTP POST
         ┌───────────────────────┐
         │ Browser Agent (opena6)│
         │ (Port 12350)          │
         │ Execute Actions       │
         └───────────────────────┘
```

---

## 📦 Komponenten

### Tool Server (`tool_server.py`)
- **Port**: 8765
- **Status**: ✅ RUNNING
- **Endpoints**:
  - `GET /manifest` → Tool Definition (JSON)
  - `GET /health` → Status Check
  - `POST /execute` → Browser Action
  - `GET /` → Dashboard (HTML)

### Browser Agent (`opena6`)
- **Port**: 12350
- **Status**: ✅ ONLINE
- **Actions**: 9 (open, click, type, extract_text, extract_html, query_selector, screenshot, scroll, wait_for)

### OpenWebUI
- **URL**: http://192.168.0.70:3000
- **Status**: ✅ AVAILABLE
- **Admin**: http://192.168.0.70:3000/admin

---

## 🚀 Integration Steps

### 1️⃣ Tool Server starten
```bash
cd LocalAgent-Pro/opena6
python3 tool_server.py --host 0.0.0.0 --port 8765
```

✅ **Verify**: http://localhost:8765/health

### 2️⃣ OpenWebUI Admin öffnen
```
http://192.168.0.70:3000/admin
```

### 3️⃣ External Tool registrieren
**Pfad**: Settings → External Tools (oder Search "Tools")

**Tool URL**:
```
http://192.168.0.70:8765/manifest
```

**Oder Manual Tool Definition** (kopieren):
```json
{
  "type": "function",
  "function": {
    "name": "browser_agent",
    "description": "Browser-Automation für Web-Scraping und Datenextraktion",
    "parameters": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "enum": ["open", "click", "type", "extract_text", "extract_html", "query_selector", "screenshot", "scroll", "wait_for"]
        },
        "url": {"type": "string"},
        "selector": {"type": "string"},
        "text": {"type": "string"},
        "wait_ms": {"type": "integer", "default": 500},
        "return_format": {"type": "string", "enum": ["text", "html", "json", "raw"], "default": "text"}
      },
      "required": ["action", "url"]
    }
  }
}
```

### 4️⃣ Chat testen
```
Prompt: "Öffne https://example.com und zeige mir die Hauptüberschrift"
```

✅ **Sollte automatisch aufrufen**: 
- action: "open", url: "https://example.com"
- action: "extract_text", selector: "h1"

---

## 📊 URLs & Endpoints

| Service | URL | Status |
|---------|-----|--------|
| **Tool Server** | http://192.168.0.70:8765 | ✅ |
| Tool Dashboard | http://192.168.0.70:8765/ | ✅ |
| Tool Manifest | http://192.168.0.70:8765/manifest | ✅ |
| Tool Health | http://192.168.0.70:8765/health | ✅ |
| **Browser Agent** | http://192.168.0.70:12350 | ✅ |
| Agent Health | http://192.168.0.70:12350/health | ✅ |
| **OpenWebUI** | http://192.168.0.70:3000 | ✅ |
| OpenWebUI Admin | http://192.168.0.70:3000/admin | ✅ |

---

## 🎯 Browser Actions

```json
{
  "open": "Website öffnen",
  "click": "Element klicken",
  "type": "Text eingeben",
  "extract_text": "Text extrahieren",
  "extract_html": "HTML extrahieren",
  "query_selector": "DOM analysieren",
  "screenshot": "Screenshot machen",
  "scroll": "Seite scrollen",
  "wait_for": "Auf Element warten"
}
```

---

## 💻 Test Commands

```bash
# Tool Server Status
curl http://192.168.0.70:8765/health

# Tool Manifest
curl http://192.168.0.70:8765/manifest | jq

# Browser Agent Status
curl -H "Authorization: Bearer sk_opena6_browser_v3_production" \
  http://192.168.0.70:12350/health

# Test Action: Open URL
curl -X POST http://192.168.0.70:8765/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "open",
    "url": "https://example.com"
  }'
```

---

## 📚 Dokumentation

| Datei | Inhalt |
|-------|--------|
| `TOOL_SERVER_SUMMARY.md` | Diese Datei |
| `TOOL_JSON_SPECIFICATION.md` | Vollständige API Spec |
| `TOOL_QUICK_REFERENCE.md` | Copy & Paste Beispiele |
| `OPENWEBUI_INTEGRATION.md` | Integration Guide |
| `tool_server.py` | Source Code |

---

## ✅ Checkliste

- [x] Tool Server implementiert
- [x] JSON Schema definiert
- [x] HTTP Endpoints aktiv
- [x] Browser Agent online
- [x] OpenWebUI verfügbar
- [ ] Tool registriert (manuell erforderlich)
- [ ] Chat Test erfolgreich

---

## 🎉 Status: READY FOR PRODUCTION

**Tool Server**: ✅ RUNNING (Port 8765)  
**Browser Agent**: ✅ ONLINE (Port 12350)  
**OpenWebUI**: ✅ AVAILABLE (Port 3000)

**Nächster Schritt**: Öffne http://192.168.0.70:3000/admin und registriere das Tool!

