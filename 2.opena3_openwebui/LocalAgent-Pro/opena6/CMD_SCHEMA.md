# 5.opena6_browser - CMD Schema & Tool Definition

**Version**: 3.0.0
**Agent**: 5.opena6_browser
**Type**: Local Execution Browser Agent
**Integration**: PORTIER 3.0 Multi-Agent Network

---

## 🔄 Command Schema (v3.0 - FINAL)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "BrowserAgentCMD",
  "type": "object",
  "required": ["action", "url"],
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
      ]
    },
    "url": {
      "type": "string",
      "description": "Zielseite, die geladen oder verarbeitet werden soll."
    },
    "selector": {
      "type": "string",
      "description": "CSS oder XPath Selektor, abhängig von Aktion."
    },
    "text": {
      "type": "string",
      "description": "Textinput für type-Aktion."
    },
    "wait_ms": {
      "type": "integer",
      "default": 500,
      "description": "Wartezeit nach Aktionen."
    },
    "return_format": {
      "type": "string",
      "enum": ["text", "html", "json", "raw"],
      "default": "text"
    }
  }
}
```

---

## 📋 Action Reference

### 1. OPEN - Browser Session

```json
{
  "action": "open",
  "url": "https://example.com",
  "wait_ms": 500
}
```

**Response**:

```json
{
  "status": "success",
  "session_id": "sess_000001",
  "url": "https://example.com"
}
```

### 2. CLICK - Element Interaction

```json
{
  "action": "click",
  "url": "https://example.com",
  "selector": "button.submit"
}
```

**Response**:

```json
{
  "status": "success",
  "action": "click",
  "selector": "button.submit",
  "executed": true
}
```

### 3. TYPE - Text Input

```json
{
  "action": "type",
  "url": "https://example.com",
  "selector": "input#email",
  "text": "user@example.com"
}
```

**Response**:

```json
{
  "status": "success",
  "action": "type",
  "selector": "input#email",
  "text_length": 18
}
```

### 4. EXTRACT_TEXT - Text Content

```json
{
  "action": "extract_text",
  "url": "https://example.com",
  "selector": "p.description",
  "return_format": "text"
}
```

**Response**:

```json
{
  "status": "success",
  "text": "Extracted text content...",
  "selector_matched": true
}
```

### 5. EXTRACT_HTML - HTML Extraction

```json
{
  "action": "extract_html",
  "url": "https://example.com",
  "selector": "div.content",
  "return_format": "html"
}
```

**Response**:

```json
{
  "status": "success",
  "content": "<div class='content'>...</div>",
  "elements_found": 1
}
```

### 6. QUERY_SELECTOR - DOM Analysis

```json
{
  "action": "query_selector",
  "url": "https://example.com",
  "selector": "//div[@class='main']",
  "return_format": "json"
}
```

**Response**:

```json
{
  "status": "success",
  "dom_elements": {
    "total": 42,
    "divs": 12,
    "spans": 18,
    "forms": 2
  }
}
```

### 7. SCREENSHOT - Browser Capture

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
  "screenshot_path": "/storage/screenshot_001.png",
  "timestamp": "2025-11-24T18:00:00Z"
}
```

### 8. SCROLL - Page Navigation

```json
{
  "action": "scroll",
  "url": "https://example.com",
  "selector": "div.content",
  "wait_ms": 300
}
```

**Response**:

```json
{
  "status": "success",
  "action": "scroll",
  "scrolled": true
}
```

### 9. WAIT_FOR - Synchronization

```json
{
  "action": "wait_for",
  "url": "https://example.com",
  "selector": "div.loaded",
  "wait_ms": 5000
}
```

**Response**:

```json
{
  "status": "success",
  "action": "wait_for",
  "element_appeared": true
}
```

---

## 🛠️ Tool Definition for AI Models

```json
{
  "tool_name": "opena6_browser_tool",
  "description": "Local Browser Automation Agent für das Gesamtprojekt. Steuert Webseiten, extrahiert Daten und führt DOM-Aktionen aus.",
  "input_schema": {
    "type": "object",
    "required": ["action", "url"],
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
        ]
      },
      "url": { "type": "string" },
      "selector": { "type": "string" },
      "text": { "type": "string" },
      "wait_ms": { "type": "integer", "default": 500 },
      "return_format": {
        "type": "string",
        "enum": ["text", "html", "json", "raw"],
        "default": "text"
      }
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "status": { "type": "string" },
      "data": {},
      "safepoint_id": { "type": "string" }
    }
  }
}
```

---

## 📊 Integration Flow

```
┌─────────────┐
│   User      │
│   Request   │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   opena1            │
│  Coordinator        │  ◄─ Validates request
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   opena2            │
│   Archivator        │  ◄─ Creates CMD safepoint
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   opena6            │
│   Browser Agent     │  ◄─ Executes action
│   (5.opena6)        │
└──────┬──────────────┘
       │
       ▼ (Result)
┌─────────────────────┐
│   opena2            │
│   Archivator        │  ◄─ Stores RESP safepoint
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   opena1            │
│  Coordinator        │  ◄─ Routes to user
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│   User      │
│   Response  │
└─────────────┘
```

---

## 🔐 Security Rules

✅ **PERMITTED**

- Click, type, scroll on authorized URLs
- Extract text and HTML from accessible pages
- Parse DOM structure
- Create browser sessions

❌ **FORBIDDEN**

- Execute arbitrary JavaScript
- Make external API calls
- Write to local filesystem
- Access resources outside target URL
- Bypass CORS restrictions
- Run commands outside sandbox

---

## 📌 Usage Example

**Request (from opena1→opena2→opena6):**

```bash
curl -X POST http://0.0.0.0:12350/execute \
  -H "Authorization: Bearer sk_opena6_browser_v3_production" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "scrape",
    "url": "https://example.com/data",
    "selector": "table.results tbody tr",
    "return_format": "json"
  }'
```

**Response:**

```json
{
  "status": "success",
  "action": "scrape",
  "url": "https://example.com/data",
  "selector": "table.results tbody tr",
  "content": "<tr>...</tr>",
  "elements_found": 5,
  "timestamp": "2025-11-24T18:00:00Z"
}
```

---

## 📚 README Summary

- **Agent Role**: Browser Automation & Scraping
- **Execution**: Local (no cloud dependencies)
- **Integration**: Full PORTIER 3.0 compatibility
- **Commands**: 7 core actions (open, scrape, extract, parse, click, type, scroll)
- **Authentication**: Bearer token (sk_opena6_browser_v3_production)
- **Port**: 12350
- **Rate Limit**: 1000 req/min
- **Status**: ✅ Production Ready
