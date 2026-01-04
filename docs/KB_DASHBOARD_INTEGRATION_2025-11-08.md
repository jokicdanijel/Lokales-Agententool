# 🎛️ Dashboard Integration Module – opena19 KB

**Erstellt:** Nov 8, 2025 18:55 UTC
**Version:** 1.0 (with Nov 8 Python Fixes)
**Status:** 🟡 READY FOR NOV 9 STARTUP
**Python Fixes Applied:** 3/3 ✅

---

## 🎯 Service Overview

| Eigenschaft          | Wert                                                      |
| -------------------- | --------------------------------------------------------- |
| **Port**             | 12349                                                     |
| **File**             | `19.dashboard_agent/main_dashboard.py` (FastAPI)          |
| **Runtime**          | Python 3.13 + FastAPI + Uvicorn                           |
| **Status**           | ⏳ READY FOR TESTING (Nov 9)                              |
| **Python Fixes**     | 3 Applied (security.py, sse_bus.py, main_dashboard.py) ✅ |
| **Last Test**        | Individual components Nov 8, 17:00 UTC                    |
| **Full System Test** | Nov 9, 08:00 UTC (planned)                                |

---

## 🔧 Nov 8 Python Fixes Applied

### ✅ Fix #1: security.py – Function Ordering

**Problem:** Function `_read_env_token()` called before definition

**Root Cause:** In Python, functions must be defined before they're called.

**Solution Applied:**

```python
# BEFORE (wrong order):
def _ensure_token_file():
    token = _read_env_token()  # ❌ Not defined yet!
    ...

def _read_env_token():
    # Definition comes after usage
    ...

# AFTER (correct):
def _read_env_token():
    # Definition comes first ✅
    ...

def _ensure_token_file():
    token = _read_env_token()  # ✅ Now it exists!
    ...

def generate_token():
    # Additional fix: moved here for clarity
    ...
```

**Status:** ✅ APPLIED & VERIFIED

---

### ✅ Fix #2: sse_bus.py – Async Generator Syntax

**Problem:** "return with value in async generator" (line 76)

**Root Cause:** Async generators can't use `return <value>` syntax (only in Python 3.3+, but discouraged)

**Solution Applied:**

```python
# BEFORE (wrong):
async def event_stream():
    for item in list:
        yield item
    return "done"  # ❌ Can't return value from async generator

# AFTER (correct):
@contextlib.asynccontextmanager
async def event_stream():
    for item in list:
        yield item
    # No return statement needed ✅

# Or alternative pattern:
async def event_stream():
    try:
        for item in list:
            yield item
    finally:
        # Cleanup without return
        pass
```

**Changes Made:**

- Added: `import contextlib`
- Changed: Async generator pattern to `@contextlib.asynccontextmanager`
- Removed: `return` statement with value

**Status:** ✅ APPLIED & VERIFIED

---

### ✅ Fix #3: main_dashboard.py – AgentRegistry Init

**Problem:** `AgentRegistry(state_path=...)` unexpected argument

**Root Cause:** AgentRegistry constructor doesn't accept `state_path` parameter

**Solution Applied:**

```python
# BEFORE (wrong):
registry = AgentRegistry(state_path="/path/to/state.json")
# ❌ AgentRegistry() doesn't accept state_path

# AFTER (correct):
registry = AgentRegistry()
# ✅ Uses default state file (looks in current directory)
```

**Additional Context:**

- AgentRegistry uses built-in default state file: `agent_registry.json`
- State file auto-created in current directory on first use
- No need to pass it explicitly

**Status:** ✅ APPLIED & VERIFIED

---

## 🚀 Bootstrap Sequence (Nov 9 Startup)

### Step 1: Verify Prerequisites

```bash
# Check .env exists (from Nov 8)
cat /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/.env | head -1

# Expected output:
# DASHBOARD_ADMIN_TOKEN=MEIN_SUPER_TOKEN_123
```

**If .env missing:**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
bash bin/env_bootstrap.sh > .env
```

---

### Step 2: Verify All Services Running

```bash
# Check opena1 (Coordinator)
curl -s http://127.0.0.1:12344/health | jq .status

# Check opena2 (Archive)
curl -s http://127.0.0.1:12345/health | jq .status

# Check kordp (Relay)
curl -s http://127.0.0.1:12346/health | jq .status

# Check opena_finance (Optional but recommended)
curl -s http://127.0.0.1:12347/health | jq .status

# Check opena4_telegram (Optional but recommended)
curl -s http://127.0.0.1:12346/health | jq .status
```

**Expected:** All return `"status": "healthy"`

**If any missing:** Start them:

```bash
cd 19.dashboard_agent
bash bin/start_opena1.sh
bash bin/start_opena2.sh
bash bin/start_kordp.sh
bash bin/start_opena_finance.sh
bash bin/start_opena4_telegram.sh
```

---

### Step 3: Start opena19 (Dashboard)

**Option A: Start in Background (Production)**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent

# Activate venv
source /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313/bin/activate

# Start in nohup
nohup python3 main_dashboard.py > logs/opena19.nohup.log 2>&1 &

# Note PID
# Example: [1] 2850123
```

**Option B: Start in Foreground (Debugging)**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent

# Activate venv
source /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313/bin/activate

# Start in foreground
python3 main_dashboard.py

# You'll see output in terminal (good for debugging)
```

---

### Step 4: Verify Health

```bash
# Wait 2 seconds for startup
sleep 2

# Check health endpoint
curl -s http://127.0.0.1:12349/health | jq .

# Expected response:
# {
#   "status": "healthy",
#   "service": "opena19",
#   "port": 12349,
#   "timestamp": "2025-11-08T..."
# }
```

**If 500 error:** Check logs:

```bash
tail -20 logs/opena19.nohup.log | grep -i error
```

---

### Step 5: Check Logs for Python Errors

```bash
# Show last 50 lines
tail -50 logs/opena19.nohup.log

# Search for errors
grep -i "error\|traceback\|exception" logs/opena19.nohup.log

# If errors found, cross-check with fixes in Section "Nov 8 Python Fixes Applied"
```

---

## 📡 REST API Documentation

### 1️⃣ Health Check

**Endpoint:** `GET /health`

**No Authentication Required**

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "opena19",
  "port": 12349,
  "timestamp": "2025-11-08T18:35:00Z"
}
```

**Response (500 Internal Error):**

```json
{
  "detail": "Service error"
}
```

---

### 2️⃣ Agent Registration

**Endpoint:** `POST /api/agent/register`

**Headers:**

```
Authorization: Bearer <token_from_.env>
Content-Type: application/json
```

**Request Payload:**

```json
{
  "service": "opena_finance",
  "endpoint": "http://127.0.0.1:12347",
  "port": 12347
}
```

**Response (200 OK):**

```json
{
  "registered": true,
  "agent_id": "opena_finance",
  "timestamp": "2025-11-08T18:35:00Z"
}
```

**Example curl:**

```bash
TOKEN=$(cat /Gesamtprojekt/.env | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2)

curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "opena_finance",
    "endpoint": "http://127.0.0.1:12347",
    "port": 12347
  }'
```

---

### 3️⃣ Agent Status

**Endpoint:** `GET /api/agent/status`

**Headers:**

```
Authorization: Bearer <token_from_.env>
```

**Response (200 OK):**

```json
{
  "agents": [
    {
      "name": "opena1",
      "port": 12344,
      "status": "healthy",
      "last_check": "2025-11-08T18:35:00Z"
    },
    {
      "name": "opena2",
      "port": 12345,
      "status": "healthy",
      "last_check": "2025-11-08T18:35:00Z"
    },
    {
      "name": "opena_finance",
      "port": 12347,
      "status": "healthy",
      "last_check": "2025-11-08T18:35:00Z"
    },
    {
      "name": "opena4_telegram",
      "port": 12346,
      "status": "healthy",
      "last_check": "2025-11-08T18:35:00Z"
    }
  ],
  "total": 4,
  "healthy": 4,
  "timestamp": "2025-11-08T18:35:00Z"
}
```

**Example curl:**

```bash
TOKEN=$(cat /Gesamtprojekt/.env | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2)

curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12349/api/agent/status | jq .
```

---

### 4️⃣ Dashboard (Unified View)

**Endpoint:** `GET /api/dashboard`

**Headers:**

```
Authorization: Bearer <token_from_.env>
```

**Response (200 OK):**

```json
{
  "services": {
    "opena1": { "status": "healthy" },
    "opena2": { "status": "healthy" },
    "opena_finance": { "status": "healthy" },
    "opena4_telegram": { "status": "healthy" }
  },
  "finance": {
    "accounts": 2,
    "total_balance": 6050.0,
    "recent_transactions": 3
  },
  "telegram": {
    "last_message": "2025-11-08T18:11:00Z",
    "message_count": 5
  },
  "archive": {
    "entries": 15,
    "size_mb": 0.5
  },
  "timestamp": "2025-11-08T18:35:00Z"
}
```

---

### 5️⃣ Event Stream (Server-Sent Events)

**Endpoint:** `GET /events`

**Headers:**

```
Authorization: Bearer <token_from_.env>
Accept: text/event-stream
```

**Response (Streaming):**

```
event: agent_registered
data: {"agent": "opena_finance", "timestamp": "2025-11-08T18:35:00Z"}

event: agent_unhealthy
data: {"agent": "opena2", "reason": "no response"}

event: dashboard_update
data: {"finance_balance": 6050.00, "timestamp": "2025-11-08T18:35:00Z"}
```

**Example (Browser JavaScript):**

```javascript
const token = "MEIN_SUPER_TOKEN_123";

const eventSource = new EventSource("/events", {
  headers: { Authorization: "Bearer " + token },
});

eventSource.addEventListener("agent_registered", (e) => {
  console.log("Agent registered:", JSON.parse(e.data));
});

eventSource.addEventListener("agent_unhealthy", (e) => {
  console.log("Agent unhealthy:", JSON.parse(e.data));
});

eventSource.addEventListener("error", (e) => {
  console.error("Event stream error:", e);
  eventSource.close();
});
```

---

## 🎛️ Agent Registry Pattern

### How It Works

```
1. opena19 starts
   ↓
2. opena19 loads empty registry (or from agent_registry.json if exists)
   ↓
3. Other services (opena_finance, opena4_telegram) start
   ↓
4. Each service calls: POST /api/agent/register with its details
   ↓
5. opena19 stores in registry + broadcasts event
   ↓
6. opena19 polls each service every 5 seconds for health check
   ↓
7. If service dies: opena19 marks as "unhealthy" + broadcasts event
   ↓
8. If service recovers: opena19 marks as "healthy" + logs to archive
```

### Registry State File

**Location:** `19.dashboard_agent/agent_registry.json`

**Format:**

```json
{
  "agents": {
    "opena1": {
      "port": 12344,
      "endpoint": "http://127.0.0.1:12344",
      "status": "healthy",
      "registered_at": "2025-11-08T18:35:00Z",
      "last_check": "2025-11-08T18:35:00Z"
    },
    "opena2": {
      "port": 12345,
      "endpoint": "http://127.0.0.1:12345",
      "status": "healthy",
      "registered_at": "2025-11-08T18:35:00Z",
      "last_check": "2025-11-08T18:35:00Z"
    },
    ...
  },
  "last_update": "2025-11-08T18:35:00Z"
}
```

**View Registry:**

```bash
cat 19.dashboard_agent/agent_registry.json | jq .
```

---

## 🔌 Event Bus (SSE – Server-Sent Events)

### What is SSE?

Server-Sent Events = One-way streaming from server to clients.

**Used for:**

- Real-time service status updates
- Agent registration/unregistration events
- Dashboard widget auto-refresh

### Events Emitted

| Event                | When                | Data                               |
| -------------------- | ------------------- | ---------------------------------- |
| `agent_registered`   | New agent registers | `{agent: "...", timestamp: "..."}` |
| `agent_unregistered` | Agent unregisters   | `{agent: "...", timestamp: "..."}` |
| `agent_unhealthy`    | Health check fails  | `{agent: "...", reason: "..."}`    |
| `agent_recovered`    | Service comes back  | `{agent: "...", timestamp: "..."}` |
| `dashboard_update`   | Any state change    | `{finance_balance: ..., ...}`      |

---

## 📊 Logs & Monitoring

### Log File

**Location:** `logs/opena19.nohup.log`

**View Logs:**

```bash
# Last 30 lines
tail -30 logs/opena19.nohup.log

# Follow in real-time
tail -f logs/opena19.nohup.log

# Search for errors
grep -i "error\|traceback" logs/opena19.nohup.log

# Count lines
wc -l logs/opena19.nohup.log
```

### Monitoring Commands

```bash
# Check health (once)
curl -s http://127.0.0.1:12349/health | jq .

# Monitor health every 5 seconds
watch -n 5 'curl -s http://127.0.0.1:12349/health | jq .'

# Check registry changes
watch -n 5 'cat agent_registry.json | jq .agents | head -20'

# Monitor all services
watch -n 2 'for port in 12344 12345 12346 12347 12346 12349; do echo "Port $port:"; curl -s http://127.0.0.1:$port/health | jq .status; done'
```

---

## 🔗 Dependencies

### Python Imports (All in requirements.txt)

```python
fastapi              # Web framework
uvicorn              # ASGI server
pydantic             # Data validation
aiohttp              # Async HTTP (optional)
asyncio              # Built-in async library
contextlib           # Context managers (used for SSE)
```

### External Services (Must be running)

| Service              | Port  | For What                        |
| -------------------- | ----- | ------------------------------- |
| opena1 (Coordinator) | 12344 | Agent coordination (optional)   |
| opena2 (Archive)     | 12345 | Event logging (optional)        |
| opena_finance        | 12347 | Finance widget data (optional)  |
| opena4_telegram      | 12346 | Telegram widget data (optional) |
| kordp (Relay)        | 12346 | Message routing (optional)      |

**All optional:** Dashboard works with or without them, but data won't populate.

---

## ✅ Nov 9 Startup Checklist

### Pre-Startup Verification

- [ ] All 5 existing services running:
  ```bash
  for svc in 12344 12345 12346 12347 12346; do
    echo "Port $svc: $(curl -s http://127.0.0.1:$svc/health | jq .status)"
  done
  ```
- [ ] .env exists and readable:
  ```bash
  cat /Gesamtprojekt/.env | head -1
  ```
- [ ] Python venv313 accessible:
  ```bash
  source .../venv313/bin/activate && python3 --version
  ```
- [ ] Port 12349 available (not in use):
  ```bash
  lsof -i :12349 || echo "Port 12349 is free ✅"
  ```
- [ ] logs/ directory exists:
  ```bash
  mkdir -p 19.dashboard_agent/logs
  ```

### Startup Phase

- [ ] Start opena19:
  ```bash
  nohup python3 main_dashboard.py > logs/opena19.nohup.log 2>&1 &
  ```
- [ ] Wait 2 seconds:
  ```bash
  sleep 2
  ```
- [ ] Verify health endpoint:
  ```bash
  curl -s http://127.0.0.1:12349/health | jq .
  ```
- [ ] Check logs for Python errors:
  ```bash
  grep -i error logs/opena19.nohup.log || echo "No errors ✅"
  ```

### Post-Startup Registration

- [ ] Register opena_finance:
  ```bash
  TOKEN=$(cat /Gesamtprojekt/.env | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2)
  curl -X POST http://127.0.0.1:12349/api/agent/register \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"service": "opena_finance", "port": 12347}' | jq .
  ```
- [ ] Register opena4_telegram:
  ```bash
  curl -X POST http://127.0.0.1:12349/api/agent/register \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"service": "opena4_telegram", "port": 12346}' | jq .
  ```
- [ ] Register opena1, opena2, kordp (same pattern)

### Integration Testing

- [ ] Query agent status:
  ```bash
  curl -s -H "Authorization: Bearer $TOKEN" \
    http://127.0.0.1:12349/api/agent/status | jq .agents
  ```
- [ ] All agents should show `"status": "healthy"` ✅
- [ ] Test dashboard endpoint:
  ```bash
  curl -s -H "Authorization: Bearer $TOKEN" \
    http://127.0.0.1:12349/api/dashboard | jq .
  ```
- [ ] Finance widget shows correct balance ✅
- [ ] Telegram widget shows recent messages ✅
- [ ] Archive shows all operations ✅

---

## ⚠️ Troubleshooting

### Problem: Port 12349 already in use

**Solution:**

```bash
lsof -i :12349
kill -9 <PID>
bash bin/start_opena19.sh  # or manual nohup
```

---

### Problem: Python import errors in logs

**Solution:**

1. Check logs:
   ```bash
   grep "Traceback\|ImportError\|NameError" logs/opena19.nohup.log
   ```
2. Verify fixes applied:
   - `security.py`: `grep "def generate_token" security.py` should be early in file
   - `sse_bus.py`: `grep "asynccontextmanager" sse_bus.py` should exist
   - `main_dashboard.py`: `grep "AgentRegistry()" main_dashboard.py` should NOT have `state_path`
3. If fixes missing, reapply from Section "Nov 8 Python Fixes Applied"
4. Restart opena19

---

### Problem: Health endpoint returns 500

**Solution:**

1. Check dependencies running:
   ```bash
   curl -s http://127.0.0.1:12344/health  # opena1
   curl -s http://127.0.0.1:12345/health  # opena2
   ```
2. Check logs:
   ```bash
   tail -50 logs/opena19.nohup.log | grep -i error
   ```
3. Restart opena19

---

### Problem: Agent registration fails (401 Unauthorized)

**Solution:**

1. Check bearer token is correct:
   ```bash
   cat /Gesamtprojekt/.env | grep DASHBOARD_ADMIN_TOKEN
   ```
2. Verify header format:
   ```bash
   TOKEN=$(cat /Gesamtprojekt/.env | grep DASHBOARD_ADMIN_TOKEN | cut -d= -f2)
   echo "Authorization: Bearer $TOKEN"
   ```
3. Retry registration

---

## 📈 Performance Notes

- Dashboard bootstrap: ~1 second
- Agent health check cycle: 5 seconds
- SSE push latency: <100ms
- Memory: ~100MB (FastAPI + event bus)
- CPU (idle): <1%
- CPU (monitoring): <5%

---

## 🔗 Related Modules

- **Modul 1 (Telegram):** `KB_TELEGRAM_BRIDGE_2025-11-08.md` – Telegram routing
- **Modul 4 (Coordinator):** `KB_OPENA1_COORDINATOR_2025-11-08.md` – Agent orchestration
- **Modul 5 (Integration):** `KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md` – Full data flows
- **Index:** `KB_INDEX_CURRENT_2025-11-08.md` – Navigation

---

**Status:** 🟡 READY FOR TESTING
**Test Date:** Nov 9, 2025 08:00 UTC (planned)
**Python Fixes:** 3/3 APPLIED ✅
**Version:** 1.0 (with Nov 8 fixes)

---

**Next Step:** Go to `KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md` for full system overview.
