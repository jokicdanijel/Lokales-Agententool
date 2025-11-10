# Schritt 2: Tool-Registry & Mapping

## 1. Purpose & Overview

The **Tool Registry** is the central service discovery and command routing system for the ELION Hyper-Dashboard. It provides:

- **Service Registry:** Central mapping of all agents (opena1-5, opena20) to ports, endpoints, and health
- **Tool Definitions:** Catalog of all available tools with parameters, schemas, and requirements
- **Command Dispatcher:** Routes tool requests to correct agents via HTTP with automatic safepoint creation
- **Append-Only Auditing:** Every command + response creates verifiable safepoints (SP files + index.jsonl)

## 2. Architecture

### 2.1 Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Tool Registry System                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │ tool_registry.py │◄────────┤ ToolRegistry     │            │
│  │ Central Registry │         │ (Singleton)      │            │
│  └──────────────────┘         └──────────────────┘            │
│         ▲                              ▲                        │
│         │                              │                        │
│  ┌──────┴──────────────┬───────────────┴────────┐             │
│  │                     │                        │              │
│  │  Registry Data:     │   Tools:              │              │
│  │  - Agents (6x)      │   - browse, analyze   │              │
│  │  - Tools (10+x)     │   - edit, execute     │              │
│  │  - Roles            │   - store, query      │              │
│  │  - Dependencies     │   - monitor, notify   │              │
│  │                     │                        │              │
│  └─────────────────────┴────────────────────────┘             │
│                                                                 │
│  ┌──────────────────────────────────────────────┐             │
│  │ tool_dispatcher.py (ToolDispatcher)          │             │
│  │ ──────────────────────────────────────────   │             │
│  │ • Validate tool requests                    │             │
│  │ • Resolve tool → agent → endpoint           │             │
│  │ • Write CMD safepoint (src→dst)             │             │
│  │ • Dispatch HTTP request to agent            │             │
│  │ • Write RESP/ERR/TIMEOUT safepoint          │             │
│  │ • Manage request lifecycle                  │             │
│  └──────────────────────────────────────────────┘             │
│         ▲                                                       │
│         │                                                       │
│  ┌──────┴──────────────────────────────────────┐             │
│  │ SafepointWriter                            │             │
│  │ ──────────────────────────────────────────  │             │
│  │ • Create SP<ts>_src→dst_KIND.json files    │             │
│  │ • Append to archivp/YYYY/MM/DD/index.jsonl │             │
│  │ • Atomic file operations                   │             │
│  │ • Append-only persistence                  │             │
│  └──────────────────────────────────────────────┘             │
│                                                                 │
│  ┌──────────────────────────────────────────────┐             │
│  │ registry_schemas.py (Pydantic v2)           │             │
│  │ ──────────────────────────────────────────   │             │
│  │ • ToolSchema (extra='forbid', strict)       │             │
│  │ • AgentSchema (port validation)             │             │
│  │ • RegistrySchema (complete validation)      │             │
│  │ • ToolRequestParams71 (7.1 format)          │             │
│  │ • ErrorResponse83 (error format)            │             │
│  └──────────────────────────────────────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
Request: POST /api/dispatch
  │
  ├─► tool_dispatcher.validate_tool_request(tool_id)
  │   ├─► registry.get_tool(tool_id)
  │   ├─► registry.get_agent(agent_id)
  │   └─► registry.resolve_tool(tool_id) → {url, port, endpoint}
  │
  ├─► SafepointWriter.write_safepoint(src→dst, CMD)
  │   ├─► Create archivp/YYYY/MM/DD/SP<ts>_src→dst_CMD.json
  │   └─► Append to index.jsonl: {sp, src, dst, kind, ts, request_id}
  │
  ├─► ToolDispatcher._send_request(url, params) [HTTP POST]
  │   └─► urllib.request.urlopen() with timeout
  │
  ├─► On Success:
  │   └─► SafepointWriter.write_safepoint(src→dst, RESP)
  │       └─► Create archivp/YYYY/MM/DD/SP<ts>_src→dst_RESP.json
  │
  ├─► On Error/Timeout:
  │   └─► SafepointWriter.write_safepoint(src→dst, ERR/TIMEOUT)
  │       └─► Create archivp/YYYY/MM/DD/SP<ts>_src→dst_ERR.json
  │
  └─► Response: {ok: true, result, cmd_safepoint, resp_safepoint}
```

## 3. Registry Structure

### 3.1 Default Agents (Initialized)

| Agent ID | Name | Port | Role | Enabled | Tools |
|----------|------|------|------|---------|-------|
| opena1 | Koordinator | 12344 | Koordinator | ✅ | status, invoke, log |
| opena2 | Archivator | 12348 | Persistence | ✅ | store, query, dedupe |
| opena3 | OpenWebUI | 8080 | UI | ✅ | browse, chat, display |
| opena4 | Telegram Agent | 12347 | Messenger | ✅ | send_message, receive_message, notify |
| opena5 | VS Code Bridge | 12348 | Editor | ⏸️ | edit_file, diff, apply_patch |
| opena20 | Monitoring | 12349 | Monitoring | ⏸️ | health_check, metrics, alert |

### 3.2 Tool Categories

- **browse:** URL navigation and content preview
- **analyze:** File/data analysis
- **edit:** File modification
- **execute:** Code/command execution
- **query:** Data retrieval
- **store:** Data persistence
- **monitor:** Health/status monitoring
- **notify:** Alerting/messaging

### 3.3 Safepoint Naming Convention

```
SP<unix_ts>_<src>→<dst>_<KIND>.json

Example: SP1731245696_dashboard→opena1_CMD.json
         SP1731245696_opena1→dashboard_RESP.json
         SP1731245696_opena1→opena2_ERR.json

Where:
  SP        = Safepoint marker
  unix_ts   = Millisecond-precision Unix timestamp
  src       = Source agent (dashboard, opena1, etc.)
  dst       = Destination agent
  KIND      = CMD, RESP, ERR, TIMEOUT, UNAUTHORIZED

Storage: archivp/YYYY/MM/DD/SP<ts>_src→dst_KIND.json
Index:   archivp/YYYY/MM/DD/index.jsonl (append-only)
```

## 4. API Endpoints

### 4.1 Registry Queries

#### GET /api/tools
List all available tools

```bash
curl -s http://127.0.0.1:12349/api/tools | jq .
```

Response:
```json
{
  "ok": true,
  "timestamp": "2025-11-10T12:34:57Z",
  "count": 10,
  "tools": {
    "opena1": {
      "agent_name": "Koordinator",
      "port": 12344,
      "tools": [
        {"id": "status", "name": "Service Status", "category": "monitor"}
      ]
    }
  }
}
```

#### GET /api/tools/{tool_id}
Get tool details

```bash
curl -s http://127.0.0.1:12349/api/tools/browse | jq .
```

Response:
```json
{
  "id": "browse",
  "name": "Browse URL",
  "description": "Open and preview a URL",
  "category": "browse",
  "agent": {
    "id": "opena3",
    "name": "OpenWebUI",
    "port": 8080,
    "url": "http://127.0.0.1:8080/tools/browse"
  },
  "timeout": 30,
  "requires_auth": true,
  "params": {"url": "string (required)"}
}
```

#### GET /api/agents
List all agents

```bash
curl -s http://127.0.0.1:12349/api/agents | jq .
```

#### GET /api/status
Registry status overview

```bash
curl -s http://127.0.0.1:12349/api/status | jq .
```

Response:
```json
{
  "ok": true,
  "timestamp": "2025-11-10T12:34:57Z",
  "total_agents": 6,
  "enabled_agents": 4,
  "total_tools": 10,
  "active_tools": 9,
  "agents_by_role": {"Koordinator": 1, "Persistence": 1, "UI": 1},
  "tools_by_category": {"browse": 2, "analyze": 1, "edit": 1}
}
```

### 4.2 Tool Dispatch

#### POST /api/dispatch
Dispatch a tool command (creates safepoints)

```bash
TOK=$(cat .env)
curl -X POST http://127.0.0.1:12349/api/dispatch \
  -H "Authorization: Bearer $TOK" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "browse",
    "params": {"url": "https://example.com"},
    "source_agent": "dashboard",
    "request_id": "req-12345"
  }'
```

Request (DispatchRequest):
```json
{
  "tool_id": "browse",
  "params": {"url": "https://example.com"},
  "source_agent": "dashboard",
  "request_id": "req-12345"  // Auto-generated if not provided
}
```

Response (Success):
```json
{
  "ok": true,
  "tool": "browse",
  "target_agent": "opena3",
  "request_id": "req-12345",
  "timestamp": "2025-11-10T12:34:57Z",
  "result": {
    "status": "ok",
    "content": "...",
    "title": "Example Domain"
  },
  "cmd_safepoint": "archivp/2025/11/10/SP1731245696_dashboard→opena3_CMD.json",
  "resp_safepoint": "archivp/2025/11/10/SP1731245696_opena3→dashboard_RESP.json"
}
```

Response (Error):
```json
{
  "ok": false,
  "request_id": "req-12345",
  "error": {
    "code": "DISPATCH_ERROR",
    "message": "Tool 'unknown_tool' not found in registry",
    "timestamp": "2025-11-10T12:34:57Z"
  }
}
```

## 5. Safepoint Format & Lifecycle

### 5.1 CMD Safepoint

When a tool is dispatched:

```json
{
  "ts": "2025-11-10T12:34:57.123456Z",
  "src": "dashboard",
  "dst": "opena3",
  "kind": "CMD",
  "request_id": "req-12345",
  "payload": {
    "tool": "browse",
    "params": {"url": "https://example.com"},
    "timestamp": "2025-11-10T12:34:57Z"
  }
}
```

File location: `archivp/2025/11/10/SP1731245696_dashboard→opena3_CMD.json`

### 5.2 RESP Safepoint

When tool succeeds:

```json
{
  "ts": "2025-11-10T12:34:59.456789Z",
  "src": "opena3",
  "dst": "dashboard",
  "kind": "RESP",
  "request_id": "req-12345",
  "payload": {
    "ok": true,
    "status": "ok",
    "content": "...",
    "title": "Example Domain"
  }
}
```

File location: `archivp/2025/11/10/SP1731245696_opena3→dashboard_RESP.json`

### 5.3 ERR Safepoint

When tool fails or times out:

```json
{
  "ts": "2025-11-10T12:34:59.456789Z",
  "src": "opena3",
  "dst": "dashboard",
  "kind": "ERR",
  "request_id": "req-12345",
  "payload": {
    "error": "Connection refused",
    "exception_type": "URLError"
  }
}
```

File location: `archivp/2025/11/10/SP1731245696_opena3→dashboard_ERR.json`

### 5.4 Append-Only Index

Every safepoint is recorded in the daily index (one entry per line):

```jsonl
{"sp":"SP1731245696_dashboard→opena1_CMD.json","src":"dashboard","dst":"opena1","kind":"CMD","ts":"2025-11-10T12:34:57Z","request_id":"req-12345"}
{"sp":"SP1731245696_opena1→dashboard_RESP.json","src":"opena1","dst":"dashboard","kind":"RESP","ts":"2025-11-10T12:34:58Z","request_id":"req-12345"}
{"sp":"SP1731245697_dashboard→opena3_CMD.json","src":"dashboard","dst":"opena3","kind":"CMD","ts":"2025-11-10T12:34:59Z","request_id":"req-12346"}
```

Location: `archivp/2025/11/10/index.jsonl` (append-only, never overwritten)

## 6. Implementation Details

### 6.1 tool_registry.py

**Class: ToolRegistry**

- `__init__()` – Initialize with default agents + tools
- `register_agent(agent)` – Add agent to registry
- `register_tool(tool)` – Add tool to registry
- `get_agent(agent_id)` – Retrieve agent by ID
- `get_tool(tool_id)` – Retrieve tool by ID
- `list_agents(enabled_only=True)` – List all agents
- `list_tools(agent_id=None, category=None)` – List tools with filters
- `resolve_tool(tool_id)` – Get full endpoint info for tool
- `get_agent_endpoint(agent_id, path)` – Get full URL for agent
- `to_dict()` – Export registry as dictionary
- `to_json()` – Export registry as JSON string
- `save_to_file(path)` – Persist registry to JSON
- `load_from_file(path)` – Load registry from JSON
- `get_stats()` – Get registry statistics
- `print_summary()` – Print human-readable summary

**Singleton:**
```python
from tool_registry import get_registry
registry = get_registry()
tool = registry.get_tool("browse")
```

### 6.2 tool_dispatcher.py

**Class: ToolDispatcher**

- `__init__(archive_path)` – Initialize with safepoint storage path
- `set_auth_token(token)` – Set Bearer token for requests
- `validate_tool_request(tool_id, agent_id=None)` – Validate before dispatch
- `dispatch(tool_id, params, source_agent="dashboard", request_id=None)` – Main dispatch method
  - Validates tool
  - Writes CMD safepoint
  - Sends HTTP request
  - Writes RESP/ERR/TIMEOUT safepoint
  - Returns (success, response)
- `get_available_tools()` – Get all tools by agent
- `get_tool_info(tool_id)` – Get detailed tool info
- `list_agent_tools(agent_id)` – Get tools for specific agent

**SafepointWriter:**

- `get_date_folder()` – Get/create archivp/YYYY/MM/DD folder
- `create_safepoint_name(src, dst, kind)` – Generate SP<ts>_src→dst_KIND.json
- `write_safepoint(src, dst, kind, payload, request_id)` – Write SP file + index entry

**Usage Example:**

```python
import asyncio
from tool_dispatcher import ToolDispatcher

async def main():
    dispatcher = ToolDispatcher(archive_path=Path("./archivp"))
    dispatcher.set_auth_token("your-token-here")
    
    success, response = await dispatcher.dispatch(
        tool_id="browse",
        params={"url": "https://example.com"},
        source_agent="dashboard",
        request_id="req-12345"
    )
    
    if success:
        print(f"✅ Tool executed: {response['result']}")
        print(f"📝 Safepoints: {response['cmd_safepoint']}, {response['resp_safepoint']}")
    else:
        print(f"❌ Error: {response['error']}")

asyncio.run(main())
```

### 6.3 registry_schemas.py

**Pydantic v2 Models (all with extra='forbid'):**

- `ToolSchema` – Tool definition (strict validation)
- `AgentSchema` – Agent definition (port validation)
- `RegistrySchema` – Complete registry
- `ToolRequestParams71` – 7.1-compatible request (strict=True mandatory)
- `ToolResponse71` – 7.1-compatible response
- `ErrorDetail` – Error structure
- `ErrorResponse83` – Schema 8.3 error format
- `DispatchRequest` – Dispatch request model
- `AgentHealthResponse` – Health check response
- `RegistryStatusResponse` – Status overview

## 7. Error Handling

### 7.1 Error Codes

| Code | Meaning | HTTP |
|------|---------|------|
| TOOL_NOT_FOUND | Tool doesn't exist in registry | 404 |
| AGENT_NOT_AVAILABLE | Agent disabled or unreachable | 503 |
| AUTHORIZATION_FAILED | Missing/invalid auth token | 401 |
| DISPATCH_ERROR | Generic dispatch error | 400 |
| TIMEOUT | Tool execution exceeded timeout | 504 |
| VALIDATION_ERROR | Request validation failed | 400 |

### 7.2 Error Response (Schema 8.3)

```json
{
  "ok": false,
  "request_id": "req-12345",
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "Tool 'unknown_tool' not found in registry",
    "details": {
      "requested_tool": "unknown_tool",
      "available_categories": ["browse", "analyze", "edit"]
    },
    "timestamp": "2025-11-10T12:34:57Z"
  }
}
```

## 8. Testing Scenarios

### 8.1 Positive Test: Valid Tool Dispatch

```bash
#!/bin/bash

TOK=$(cat .env)

# Dispatch browse tool to opena3
curl -X POST http://127.0.0.1:12349/api/dispatch \
  -H "Authorization: Bearer $TOK" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "browse",
    "params": {"url": "https://example.com"},
    "source_agent": "dashboard",
    "request_id": "test-001"
  }' | jq .

# Expected: ok=true, cmd_safepoint and resp_safepoint created
```

### 8.2 Negative Test: Unknown Tool

```bash
curl -X POST http://127.0.0.1:12349/api/dispatch \
  -H "Authorization: Bearer $TOK" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "unknown_tool",
    "params": {},
    "source_agent": "dashboard"
  }' | jq .

# Expected: ok=false, error.code="DISPATCH_ERROR", TOOL_NOT_FOUND
```

### 8.3 Negative Test: Missing Authentication

```bash
curl -X POST http://127.0.0.1:12349/api/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "browse",
    "params": {"url": "https://example.com"}
  }' | jq .

# Expected: ok=false, error.code="AUTHORIZATION_FAILED"
```

### 8.4 Verification: Safepoint Creation

```bash
# List today's safepoints
ls -la archivp/2025/11/10/ | grep "SP.*_CMD\|SP.*_RESP\|SP.*_ERR"

# Check index for today
tail -10 archivp/2025/11/10/index.jsonl | jq .

# Verify CMD→RESP sequence
cat archivp/2025/11/10/SP*_CMD.json | jq '.src, .dst, .kind'
cat archivp/2025/11/10/SP*_RESP.json | jq '.src, .dst, .kind'
```

## 9. Integration Workflow

### 9.1 Typical Request Flow

1. **Client Request**: Dashboard or external agent calls `/api/dispatch`
2. **Validation**: ToolDispatcher validates tool exists and is available
3. **CMD Safepoint**: Write `SP<ts>_src→dst_CMD.json` to archivp
4. **HTTP Dispatch**: Forward request to target agent endpoint
5. **Response Handling**:
   - Success → Write RESP safepoint
   - Timeout → Write TIMEOUT safepoint
   - Error → Write ERR safepoint
6. **Index Update**: Append entry to `index.jsonl` (append-only)
7. **Response to Client**: Return response with safepoint paths

### 9.2 Audit Trail

Every dispatch creates permanent, append-only audit trail:

- `archivp/YYYY/MM/DD/SP<ts>_src→dst_CMD.json` – What was requested
- `archivp/YYYY/MM/DD/SP<ts>_src→dst_RESP.json` – What was returned
- `archivp/YYYY/MM/DD/index.jsonl` – Chronological record (can't be rewritten)

## 10. Security Considerations

### 10.1 Authentication

- All tool dispatch requires Bearer token in `Authorization` header
- Token loaded from `.env` file in project root
- Schema validation enforces strict format (Pydantic v2 extra='forbid')

### 10.2 Authorization

- Tools can require authentication (`requires_auth: true`)
- Agent availability checked before dispatch
- Port-Policy enforced (12344-12399 only, except 8080 for UI)

### 10.3 Audit

- All requests create immutable safepoint files
- Index is append-only JSONL (no overwrites)
- Timestamp precision: milliseconds + ISO-8601 Z format

## 11. Configuration & Deployment

### 11.1 Environment

```bash
# Create venv
cd 1.portier_openai
python3 -m venv venv313
source venv313/bin/activate
pip install -r requirements.txt
```

### 11.2 Import Registry & Dispatcher

```python
from tool_registry import get_registry, ToolRegistry
from tool_dispatcher import ToolDispatcher, SafepointWriter
from registry_schemas import DispatchRequest, ToolResponse71

# Get registry
registry = get_registry()
registry.print_summary()

# Initialize dispatcher
dispatcher = ToolDispatcher(archive_path=Path("./archivp"))
dispatcher.set_auth_token(token)
success, response = await dispatcher.dispatch(...)
```

### 11.3 Integration with FastAPI

```python
from fastapi import FastAPI, Depends
from tool_dispatcher import ToolDispatcher
from registry_schemas import DispatchRequest

app = FastAPI()
dispatcher = ToolDispatcher()

@app.post("/api/dispatch")
async def dispatch_tool(req: DispatchRequest):
    success, response = await dispatcher.dispatch(
        tool_id=req.tool_id,
        params=req.params,
        source_agent=req.source_agent,
        request_id=req.request_id
    )
    return response
```

## 12. Success Criteria

- ✅ Central registry maps all 6 agents with ports, roles, tools
- ✅ Tool dispatcher routes commands to correct agents
- ✅ Safepoints created for CMD/RESP/ERR/TIMEOUT events
- ✅ Append-only index.jsonl records all events chronologically
- ✅ Pydantic v2 strict validation enforced (extra='forbid')
- ✅ Schema 8.3 error responses on failures
- ✅ Bearer token authentication required
- ✅ Port-Policy compliance (12344-12399 window)
- ✅ All tests passing (positive, negative, safepoint verification)
- ✅ Documentation complete with examples

---

**Status:** Ready for implementation  
**Priority:** High (enables Schritt 3 & 5)  
**Estimated Lines:** 560 (registry) + 370 (dispatcher) + 250 (schemas) = ~1180 LOC
