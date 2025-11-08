# GitHub Copilot Instructions for ELION Hyper-Dashboard

## Project Overview

**ELION Hyper-Dashboard** ist ein verteiltes Python-Agenten-System mit orchestrierter REST-API-Integration.

**Kernkomponenten:**
- `19.dashboard_agent/` – Zentrales Dashboard + Service-Orchestrator
- `1.portier_openai/` – OpenAI Integration + venv313
- `2.openwebui/` – Docker-basiertes OpenWebUI (optional)
- `bin/` – Root-Wrapper für alle Operationen
- `.github/` – Copilot-Richtlinien und CI/CD (zu erstellen)

**Architektur:**
```
┌─────────────────────────────────────┐
│   Browser Dashboard (UI)             │ :12349
├─────────────────────────────────────┤
│   FastAPI Main (main_dashboard.py)   │
├──────────┬──────────┬───────────┬───┤
│ opena1   │ opena2   │  kordp    │ op│
│ Agent    │Archivat. │Koordinat. │ 3 │
│ :12344   │ :12345   │ :12346    │:80│
└──────────┴──────────┴───────────┴───┘
```

---

## Critical Knowledge for AI Agents

### 1. Port & Service Mapping

| Service    | Port  | File               | Purpose               |
|------------|-------|--------------------|-----------------------|
| Dashboard  | 12349 | main_dashboard.py  | Central REST API      |
| opena1     | 12344 | main_opena1.py     | AI Agent (GPT-4)      |
| opena2     | 12345 | main_opena2.py     | Archivator (Storage)  |
| kordp      | 12346 | main_kordp.py      | Coordinator (Events)  |
| OpenWebUI  | 8080  | docker-compose.yml | Web UI (optional)     |

**Token Storage:** `.env` (root-level, auto-generated if missing)

### 2. Build & Runtime Commands

**Activate Environment:**
```bash
source 1.portier_openai/venv313/bin/activate
```

**Start Full Stack (from project root):**
```bash
bin/ops.sh start           # Alle Services im nohup
bin/ops.sh agents:register # Registriere opena1/opena2 im Dashboard
bin/ops.sh status | jq .   # Zeige alle Agenten
```

**Integration Test:**
```bash
bin/ops.sh verify          # health → register → status → write
```

**Stop All:**
```bash
bin/ops.sh stop
```

**Debug Single Service (VS Code):**
- Öffne `19.dashboard_agent/.vscode/launch.json`
- Ctrl+Shift+D → Wähle "Dashboard (main_dashboard.py)" oder Compound "Start: Alle Services"

### 3. Critical Developer Workflows

#### A. Add a New Endpoint to Dashboard

**File:** `19.dashboard_agent/main_dashboard.py`

**Pattern:**
```python
@app.post("/api/agent/execute")
async def execute_agent(req: ExecuteRequest):
    # 1. Validate token from Authorization header
    # 2. Call agent endpoint: f"http://127.0.0.1:{PORT_AGENT}/invoke"
    # 3. Return JSON response
    # Example: curl -H "Authorization: Bearer $TOK" -X POST http://localhost:12349/api/agent/execute ...
```

**Key: Always use async/await; all I/O is concurrent.**

#### B. Add Agent Endpoint (opena1/opena2/kordp)

**File:** `19.dashboard_agent/main_opena1.py` (or opena2/kordp)

**Pattern:**
```python
@app.post("/invoke")
async def invoke(payload: dict):
    # Process payload
    # Return result as JSON
    # Framework: FastAPI + Uvicorn
    # Port: read from environment or use default (12344/12345/12346)
```

**Critical:** Agents communicate via HTTP REST; no direct imports between agents.

#### C. Write Data to Archivator (opena2)

**Endpoint:** `POST http://127.0.0.1:12345/store/archivp`

**Two Formats:**

1. **Generic Format:**
```json
{
  "op": "WRITE",
  "path": "2025/11/06/SP1730881234_kordp→opena2_CMD.json",
  "content": {
    "strict": true,
    "ts": "2025-11-06T12:00:00Z",
    "payload": {"key": "value"}
  }
}
```

2. **Kordp Format (simplified):**
```json
{
  "src": "kordp",
  "dst": "opena2",
  "kind": "CMD",
  "payload": {"msg": "hello", "strict": true}
}
```

**Response:** `{"written": true, "path": "..."}`

#### D. Query Archived Data

**Endpoint:** `GET http://127.0.0.1:12345/archiv/last?n=5`

**Response:**
```json
{
  "count": 5,
  "items": [
    {"path": "...", "ts": "...", "content": {...}},
    ...
  ]
}
```

### 4. Project-Specific Conventions

#### A. Token Management

- **Location:** `.env` in project root
- **Auto-Generation:** `bin/env_bootstrap.sh` creates if missing
- **Usage:** All API calls require: `Authorization: Bearer $(cat .env)`
- **Example:**
```bash
TOK=$(cat .env)
curl -H "Authorization: Bearer $TOK" http://127.0.0.1:12349/api/status/all | jq .
```

#### B. Logging Strategy

- **Location:** `logs/*.nohup.log` (one per service)
- **Viewing:** `bin/ops.sh logs` or `bin/log_tail.sh` (follow mode)
- **Format:** Each service writes unstructured text (no JSON logs by default)
- **Important Files:**
  - `dashboard.nohup.log` – Main API errors
  - `opena1.nohup.log` – Agent errors
  - `opena2.nohup.log` – Archivator I/O
  - `kordp.nohup.log` – Coordinator events

#### C. Testing Pattern

**File:** `19.dashboard_agent/tests/test_archivator.py`

**Pattern:**
```python
import json, urllib.request

def _post(path, payload):
    req = urllib.request.Request(
        f"http://127.0.0.1:12345{path}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def test_example():
    result = _post("/store/archivp", {...})
    assert result.get("written") is True
```

**Run:** `pytest -q` (from 19.dashboard_agent/)

#### D. Root Wrapper Pattern

**All bin/*.sh files in project root are wrappers:**
```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$ROOT/19.dashboard_agent/bin/ops.sh" "${@:-}"
```

**Benefit:** Calls from any project subdirectory resolve to the main orchestrator.

### 5. Integration Points & Cross-Component Communication

#### Dashboard ↔ Agents

- **Registration:** `POST /api/agent/register` with `{"agent_id": "...", "endpoint": "..."}`
- **Status Check:** Dashboard polls all registered agents periodically
- **No Shared State:** Each agent is stateless; state goes to opena2 (Archivator)

#### Agent → Archivator (opena2)

- **Write:** Agents POST to `/store/archivp` with data
- **Read:** Agents GET from `/archiv/last?n=N` to fetch recent entries
- **File Storage:** Data saved under `archiv/YYYY/MM/DD/` as JSON

#### Dashboard ↔ OpenWebUI (Optional)

- **Port:** 8080
- **Auto-Registration:** If opena3 is listening, `bin/ops.sh agents:register` detects it
- **No Direct Integration:** Just another registered agent endpoint

### 6. External Dependencies & Environment

**Python Version:** 3.12 (venv313)

**Key Packages** (from `19.dashboard_agent/requirements.txt`):
- `fastapi` – Web framework
- `uvicorn` – ASGI server
- `pydantic` – Data validation
- `aiohttp` – Async HTTP client (if used)

**Docker** (optional, for OpenWebUI):
- `docker-compose up -d` in `2.openwebui/`
- Auto-registers as opena3 if running

**No External APIs Required** (unless you extend with OpenAI directly)

### 7. Common Patterns & Idioms

#### Async Pattern (Always Use in Dashboard & Agents)
```python
@app.post("/endpoint")
async def handler(req: RequestModel):
    # Use async libraries only (aiohttp, asyncio, etc.)
    # Never block the event loop
    return {"result": "..."}
```

#### Best-Effort Publishing (SSE Bus)
```python
# From sse_bus.py
async with sse_bus._lock:
    for q in list(sse_bus._subscribers):
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            # Drop event if subscriber is slow (no backpressure)
            pass
```

#### Error Handling
- Always return `{"detail": "..."}` on error (Pydantic FastAPI default)
- HTTP status codes: 200 (OK), 401 (missing token), 403 (invalid token), 404 (not found), 500 (server error)
- Log full tracebacks to `.nohup.log` for debugging

### 8. Orchestration Files (All in `bin/`)

| Script              | Purpose                                      |
|---------------------|----------------------------------------------|
| `bin/ops.sh`        | Main orchestrator (start/stop/status/etc.)   |
| `bin/start_all.sh`  | Start all services                           |
| `bin/stop_all.sh`   | Stop all services                            |
| `bin/verify_stack.sh` | Full integration test                        |
| `bin/agents_register.sh` | Register agents only                    |
| `bin/env_bootstrap.sh` | Generate `.env` if missing                 |
| `bin/check_ports.sh` | Show listening ports                         |
| `bin/log_tail.sh`   | Follow all logs                              |
| `bin/print_token.sh` | Print current token                          |
| `bin/clean_pycache.sh` | Clean Python caches                        |
| `bin/reset_today.sh` | List today's archive files                   |

**All are callable from project root:**
```bash
cd /path/to/Gesamtprojekt
bin/ops.sh start
bin/ops.sh status | jq .
```

---

## Debugging Tips

### Port Already in Use
```bash
bin/ops.sh stop
bin/ops.sh start
```

### Token Missing/Invalid
```bash
bin/env_bootstrap.sh     # Regenerate
bin/ops.sh agents:register  # Re-register
```

### Agent Not Responding
```bash
bin/check_ports.sh       # Check if listening
bin/ops.sh logs          # Check logs
```

### Write/Read Test Failure
```bash
bin/ops.sh write:test    # Test archivator
bin/ops.sh status | jq . # Check opena2 registered
```

---

## VS Code Setup (Recommended)

**Open Workspace:** `19.dashboard_agent/` as root

**Launch Configs:**
- Ctrl+Shift+D → "Dashboard (main_dashboard.py)" (single)
- Ctrl+Shift+D → "Start: Alle Services" (compound)

**Tasks:**
- Ctrl+Shift+P → "Tasks: Run Task"
- Choose "ops: start", "ops: verify", "ops: logs", etc.

**Terminal Integration:**
- Terminal → New Terminal (opens in workspace root, which is 19.dashboard_agent/)
- Run: `./bin/ops.sh start`

---

## Key Files Reference

**Dashboard (Central):**
- `19.dashboard_agent/main_dashboard.py` – FastAPI REST API
- `19.dashboard_agent/main_opena1.py` – Agent template
- `19.dashboard_agent/main_opena2.py` – Archivator (file-based storage)
- `19.dashboard_agent/main_kordp.py` – Coordinator

**Configuration:**
- `19.dashboard_agent/config.py` – Settings
- `19.dashboard_agent/security.py` – Token validation
- `19.dashboard_agent/sse_bus.py` – Live event streaming

**Documentation:**
- `19.dashboard_agent/docs/OPERATIONS.md` – Operator guide
- `19.dashboard_agent/docs/OPENWEBUI_INTEGRATION.md` – Optional WebUI setup
- `19.dashboard_agent/README_STACK_START.md` – Quick start

**Tests:**
- `19.dashboard_agent/tests/test_archivator.py` – Integration test

---

## Coding Style & Requirements

1. **Python Version:** 3.12+
2. **Async-First:** Use `async def`, `await`, never block event loop
3. **Type Hints:** Always annotate function signatures (`def func(x: int) -> str:`)
4. **Error Messages:** Always include `{"detail": "..."}` for errors
5. **Token Validation:** Every API endpoint (except `/health`) must validate Authorization header
6. **Logging:** Use print() or logging module; output to `logs/*.nohup.log`
7. **No Shell in Python:** Never use `subprocess.run()` for shell logic; use Python-native libraries

---

## How to Extend

### Add a New Service
1. Create `19.dashboard_agent/main_newservice.py` with FastAPI app
2. Update `bin/ops.sh` to start it (add `start_newservice()` function)
3. Update `.vscode/launch.json` to include debug config
4. Update `.vscode/tasks.json` if needed
5. Update port mapping at top of this document

### Add an API Endpoint
1. Edit `19.dashboard_agent/main_dashboard.py`
2. Add `@app.post("/api/new/endpoint")` with full type hints
3. Validate token from `Authorization` header
4. Return JSON response
5. Test with `curl -H "Authorization: Bearer $(cat .env)" ...`

### Add a Test
1. Create `19.dashboard_agent/tests/test_new_feature.py`
2. Use pattern from `test_archivator.py` (urllib.request, no pytest fixtures initially)
3. Run: `pytest -q tests/test_new_feature.py`

---

## Last Notes for AI Agents

- **JavaScript belongs in browser (F12 console), NOT in Bash** – Never paste fetch() into terminal
- **Python code: edit files, restart services** – Never paste multi-line Python into terminal
- **Token is sacred** – Guard `.env`; regenerate only if compromised
- **Services are independent** – No direct Python imports between agents; use HTTP REST
- **Archivator is the source of truth** – All persistent state lives in opena2's archive
- **All operations are REST** – Everything happens over HTTP; leverage curl, Python urllib, or Postman

---

**Last Updated:** 2025-11-06  
**Maintained by:** Danijel (ELION Team)
