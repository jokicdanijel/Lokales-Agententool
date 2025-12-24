# 🤖 GitHub Copilot – Handoff Documentation

**System:** ELION Hyper-Dashboard
**Version:** 1.0.0
**Status:** Production Ready
**Datum:** 2025-12-23

---

## 🎯 Zweck dieses Dokuments

Dieses Dokument enthält **alle Regeln, Constraints und Workflows**, die GitHub Copilot bei der Code-Generierung für ELION Hyper-Dashboard beachten MUSS.

**Grundprinzip:** Copilot arbeitet IMMER nach Preflight-Check und nutzt AUSSCHLIESSLICH generierte Manifests als Wahrheit.

---

## 🔐 IMMUTABLE RULES (NIEMALS VERLETZEN)

### 1. Canonical Agent Registry (ABSOLUT UNVERÄNDERLICH)

```json
{
  "opena1": 12344,   "opena2": 12345,   "opena3": 12347,
  "opena4": 12346,   "opena5": 12351,   "opena6": 12352,
  "opena7": 12350,   "opena8": 12354,   "opena9": 12355,
  "opena10": 12356,  "opena11": 12357,  "opena12": 12358,
  "opena13": 12359,  "opena14": 12360,  "opena15": 12361,
  "opena16": 12362,  "opena17": 12366,  "opena18": 12363,
  "opena19": 12367,  "opena20": 12349,  "opena21": 12368
}
```

**Regeln:**

- ❌ NIEMALS einen Port ändern
- ❌ NIEMALS einen Agent-Namen ändern
- ❌ NIEMALS einen neuen Agenten hinzufügen ohne Preflight-Update
- ❌ NIEMALS Ports 8080 oder 3000 verwenden

### 2. Verbotene Ports

```python
FORBIDDEN_PORTS = [8080, 3000]
```

**Grund:** 8080 = OpenWebUI extern, 3000 = Node.js Dev

### 3. Agent-Naming-Konvention

```
Format: opena[1-21]
Ordner: *opena[X]* oder [X].opena[X]_*

Beispiele:
  ✅ opena7
  ✅ 6.opena7_email
  ❌ email_agent
  ❌ agent7
  ❌ opena-7
```

---

## 📋 MANDATORY WORKFLOW (Copilot-Execution-Flow)

### Phase 1: Pre-Generation Check

```bash
# STEP 1: Run Preflight
python3 scripts/preflight_check.py

# STEP 2: Check Exit Code
if [ $? -ne 0 ]; then
  echo "❌ Preflight failed - ABORT generation"
  exit 1
fi

# STEP 3: Load Manifests
CAPABILITIES=$(cat artifacts/agent_capabilities.json)
BASELINE=$(cat system_baseline.yaml)
```

### Phase 2: Data-Driven Generation

**Copilot MUSS:**

1. ✅ Capability-Manifest als Single Source of Truth nutzen
2. ✅ Ports aus Manifest übernehmen
3. ✅ Features aus Manifest übernehmen
4. ✅ Endpoints aus Manifest übernehmen
5. ❌ NIEMALS Ports/Namen/Features raten oder erfinden

---

## 🏗️ CODE GENERATION RULES

### Rule 1: Agent Structure (Template)

```python
#!/usr/bin/env python3
"""
ELION Hyper-Dashboard – {AGENT_NAME}
Port: {PORT}
Role: {ROLE}
"""

from fastapi import FastAPI
import uvicorn

# CANONICAL PORT (from manifest)
PORT = {PORT}  # DO NOT CHANGE

app = FastAPI(
    title="{AGENT_ID}",
    description="{DESCRIPTION}",
    version="1.0.0"
)

@app.get("/health")
async def health():
    """Health check endpoint (REQUIRED)"""
    return {
        "status": "ok",
        "agent": "{AGENT_ID}",
        "port": PORT,
        "role": "{ROLE}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT)
```

### Rule 2: Database Access (Production)

```python
# ❌ WRONG (JSON files)
with open('data/users.json') as f:
    users = json.load(f)

# ✅ CORRECT (PostgreSQL)
import asyncpg

async def get_user(user_id: str):
    conn = await asyncpg.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        user=os.getenv('DB_USER', 'eden_user'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'eden')
    )

    row = await conn.fetchrow(
        'SELECT * FROM users WHERE user_id = $1',
        user_id
    )

    await conn.close()
    return dict(row) if row else None
```

### Rule 3: Session Management (Redis)

```python
# ❌ WRONG (in-memory dict)
sessions = {}

# ✅ CORRECT (Redis)
import redis.asyncio as redis

redis_client = redis.from_url(
    f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:6379"
)

async def create_session(user_id: str, session_id: str):
    await redis_client.setex(
        f"session:{session_id}",
        30 * 24 * 3600,  # 30 days
        user_id
    )
```

---

## 🚫 FORBIDDEN PATTERNS

### ❌ DO NOT DO THIS

```python
# ❌ Hardcoded ports
port = 8000

# ❌ Invented agent names
agent = "email_service"

# ❌ Hardcoded secrets
password = "admin123"

# ❌ JSON files in production
with open('data.json') as f:
    data = json.load(f)
```

### ✅ DO THIS INSTEAD

```python
# ✅ Port from manifest
with open('artifacts/agent_capabilities.json') as f:
    port = json.load(f)['agents']['opena7']['port']

# ✅ Canonical agent name
agent_id = "opena7"

# ✅ Secrets from environment
password = os.getenv('DB_PASSWORD')

# ✅ Use PostgreSQL
async with asyncpg.create_pool(...) as pool:
    async with pool.acquire() as conn:
        data = await conn.fetch("SELECT * FROM table")
```

---

## 📊 TESTING REQUIREMENTS

### Test 1: Preflight Must Pass

```bash
# Before ANY code generation
python3 scripts/preflight_check.py

# Must exit with code 0
echo $?  # Should be 0
```

### Test 2: Health Check

```python
def test_health_endpoint():
    """Test that health endpoint exists and returns correct data"""
    response = requests.get("http://localhost:12350/health")

    assert response.status_code == 200
    data = response.json()

    assert data['agent'] == 'opena7'
    assert data['port'] == 12350
    assert data['status'] == 'ok'
```

---

## 🎯 COPILOT GENERATION CHECKLIST

**Before generating ANY code:**

- [ ] ✅ Run `python3 scripts/preflight_check.py`
- [ ] ✅ Load `artifacts/agent_capabilities.json`
- [ ] ✅ Load `system_baseline.yaml`
- [ ] ✅ Load `config/plan_entitlements.json`

**When generating agent code:**

- [ ] ✅ Use canonical port from manifest
- [ ] ✅ Use exact agent ID (openaX)
- [ ] ✅ Include `/health` endpoint
- [ ] ✅ Use environment variables for config
- [ ] ✅ No hardcoded secrets
- [ ] ✅ Route through opena1 (no direct calls)

**After generating code:**

- [ ] ✅ Run preflight again
- [ ] ✅ Test health endpoints
- [ ] ✅ Check for violations
- [ ] ✅ Commit only if all checks pass

---

## ✅ FINAL VALIDATION COMMAND

```bash
# Run this before ANY deployment
make -f Makefile.production deploy

# This will:
# 1. Run preflight check
# 2. Build Docker images
# 3. Start services
# 4. Validate health endpoints
# 5. Show status

# Only deploy if ALL steps pass
```

---

**END OF COPILOT HANDOFF DOCUMENTATION**

This document is the **definitive guide** for GitHub Copilot when working with ELION Hyper-Dashboard.

**Any deviation from these rules MUST be flagged and require human approval.**
