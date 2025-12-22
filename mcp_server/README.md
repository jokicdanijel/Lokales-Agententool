# MCP Tool Server
## Model Context Protocol - Tool Server für LLM Actions

Der MCP Tool Server ermöglicht LLMs, Aktionen über einen standardisierten API-Server auszuführen. Die Implementierung folgt der [MCP Specification](https://modelcontextprotocol.io/).

---

## Schnellstart

```bash
# Server starten
cd mcp_server
python mcp_tool_server.py

# Alternativ mit uvicorn
uvicorn mcp_tool_server:app --host 127.0.0.1 --port 12398
```

**Port:** 12398  
**Kürzel:** mcpp  
**Health Check:** http://127.0.0.1:12398/health

---

## API Endpoints

### `POST /tools/list`
Listet alle verfügbaren Tools auf.

**Request:**
```json
{
  "cursor": null
}
```

**Response:**
```json
{
  "tools": [
    {
      "name": "calculate_sum",
      "title": "Calculate Sum",
      "description": "Add two numbers together",
      "inputSchema": {
        "type": "object",
        "properties": {
          "a": {"type": "number"},
          "b": {"type": "number"}
        },
        "required": ["a", "b"]
      },
      "annotations": {
        "readOnlyHint": true,
        "destructiveHint": false,
        "idempotentHint": true,
        "openWorldHint": false
      }
    }
  ],
  "nextCursor": null
}
```

### `POST /tools/call`
Führt ein Tool aus.

**Request:**
```json
{
  "name": "calculate_sum",
  "arguments": {
    "a": 5,
    "b": 3
  }
}
```

**Response (Erfolg):**
```json
{
  "content": [
    {
      "type": "text",
      "text": "The sum of 5 and 3 is 8"
    }
  ],
  "isError": false
}
```

**Response (Fehler):**
```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: Tool 'unknown' not found"
    }
  ],
  "isError": true
}
```

### `GET /health`
Health Check (kein Auth erforderlich).

```bash
curl http://127.0.0.1:12398/health
```

### `GET /tools`
Convenience-Endpoint: Einfache Liste aller Tools.

### `GET /tools/{tool_name}`
Info für ein spezifisches Tool.

---

## Verfügbare Tools

| Tool | Beschreibung | Readonly | Idempotent |
|------|--------------|----------|------------|
| `calculate_sum` | Addiert zwei Zahlen | ✅ | ✅ |
| `calculate_product` | Multipliziert zwei Zahlen | ✅ | ✅ |
| `get_current_time` | Aktuelle Zeit in Timezone | ✅ | ❌ |
| `echo_message` | Gibt Nachricht zurück (Test) | ✅ | ✅ |
| `list_files` | Listet Dateien (nur Projektroot) | ✅ | ✅ |
| `get_system_info` | System-Informationen | ✅ | ✅ |
| `validate_json` | JSON-Validierung | ✅ | ✅ |
| `hash_text` | Text hashen (md5/sha256/etc) | ✅ | ✅ |

---

## Authentifizierung

Alle Endpoints (außer `/health`) erfordern Bearer Token:

```bash
curl -X POST http://127.0.0.1:12398/tools/list \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Der Token wird aus `.env` geladen:
```
BEARER_TOKEN=your-secure-token-here
```

---

## Rate Limiting

- **Default:** 60 Requests pro Minute pro Client
- **Konfiguration:** `MCP_RATE_LIMIT` Environment Variable
- **HTTP 429** bei Überschreitung

---

## Tool Annotations

Jedes Tool kann Annotations haben, die sein Verhalten beschreiben:

| Annotation | Beschreibung |
|------------|--------------|
| `readOnlyHint` | Tool verändert nichts |
| `destructiveHint` | Tool kann Daten zerstören |
| `idempotentHint` | Mehrfacher Aufruf hat keine zusätzliche Wirkung |
| `openWorldHint` | Tool interagiert mit externen Systemen |

**Beispiel:**
```python
tool_registry.register(
    name="delete_file",
    description="Delete a file",
    input_schema={...},
    handler=delete_file_handler,
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
```

---

## Eigene Tools hinzufügen

### 1. Handler-Funktion erstellen

```python
async def my_custom_tool(param1: str, param2: int = 0) -> str:
    """Mein eigenes Tool"""
    result = f"Processed: {param1} with {param2}"
    return result
```

### 2. Tool registrieren

```python
tool_registry.register(
    name="my_custom_tool",
    title="My Custom Tool",
    description="Does something custom",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Second parameter", "default": 0}
        },
        "required": ["param1"]
    },
    handler=my_custom_tool,
    annotations={
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
```

### 3. Tool verwenden

```bash
curl -X POST http://127.0.0.1:12398/tools/call \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_custom_tool", "arguments": {"param1": "hello", "param2": 42}}'
```

---

## Fehlerbehandlung

Fehler werden im MCP-Format zurückgegeben (nicht als HTTP-Fehler):

```json
{
  "content": [{"type": "text", "text": "Error: Invalid arguments"}],
  "isError": true
}
```

**Best Practices:**
- LLMs können `isError` prüfen und reagieren
- Detaillierte Fehlermeldungen helfen beim Debugging
- Interne Fehler werden nicht an Clients weitergegeben

---

## Sicherheit

### Input Validation
- Strikte JSON Schema Validierung
- Pydantic V2 mit `extra="forbid"`
- Dateipfade auf Projektroot beschränkt

### Access Control
- Bearer Token Authentifizierung
- Rate Limiting pro Client
- Audit Logging aller Requests

### Audit Log
Alle Requests werden in `logs/mcp_audit.jsonl` protokolliert:

```json
{
  "timestamp": "2025-12-18T10:00:00Z",
  "event": "tools/call",
  "client_id": "abc123...",
  "details": {"tool": "calculate_sum", "arguments": {"a": 5, "b": 3}}
}
```

---

## Tests

```bash
# Alle Tests ausführen
pytest tests/test_mcp_tool_server.py -v

# Spezifische Tests
pytest tests/test_mcp_tool_server.py::TestToolsCall -v

# Mit Coverage
pytest tests/test_mcp_tool_server.py --cov=mcp_server
```

---

## cURL Beispiele

```bash
# Health Check
curl http://127.0.0.1:12398/health

# Tools auflisten
curl -X POST http://127.0.0.1:12398/tools/list \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Tool ausführen
curl -X POST http://127.0.0.1:12398/tools/call \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "calculate_sum", "arguments": {"a": 10, "b": 20}}'

# Zeit abfragen
curl -X POST http://127.0.0.1:12398/tools/call \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "get_current_time", "arguments": {"timezone_name": "Europe/Berlin"}}'

# JSON validieren
curl -X POST http://127.0.0.1:12398/tools/call \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "validate_json", "arguments": {"json_string": "{\"key\": \"value\"}"}}'
```

---

## Option-2-Flow Integration

Der MCP Server ist Teil des ELION Hyper-Dashboard Option-2-Flows:

```
LLM → opena1 → opena2 → kordp → mcp_server → Tool Execution
                                     ↓
                              Ergebnis zurück
```

---

## Dateien

```
mcp_server/
├── mcp_tool_server.py     # Hauptserver
├── logs/
│   └── mcp_audit.jsonl    # Audit Log
└── .env.example           # Environment Template
```

---

## Troubleshooting

### 401 Unauthorized
- BEARER_TOKEN in `.env` prüfen
- Header-Format: `Authorization: Bearer <token>`

### 429 Too Many Requests
- Rate Limit erreicht (60/min default)
- Warten oder `MCP_RATE_LIMIT` erhöhen

### Tool not found
- Tool-Name prüfen mit `/tools/list`
- Groß-/Kleinschreibung beachten

### Import Error
- Dependencies installieren: `pip install fastapi uvicorn pydantic`

---

## Version

- **Version:** 1.0.0
- **Port:** 12398
- **Kürzel:** mcp
- **Maintainer:** ELION Team
- **Datum:** 19. Dezember 202   5
