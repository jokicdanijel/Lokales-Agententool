[PDI-ACTIVE: TRUE | VALIDATED | GITHUB-CHECK: PASS]

# Phase 4 Implementation Quickstart

**Copilot Bridge + VS Code Integration – Week 1 Kickoff Guide**

**Datum:** 2025-11-06  
**Target Start:** 2025-11-07  
**Target Week 1 Completion:** 2025-11-14

---

## 🎯 Day 1: Setup & Foundation

### Morning
1. **Review Documentation** (30 min)
   ```bash
   cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
   cat 19.dashboard_agent/docs/PDI/project_manifest.md
   cat 19.dashboard_agent/docs/PDI/chapters/00_kapitelplan.md
   ```

2. **Verify Phase 3 Status** (10 min)
   ```bash
   bin/ops.sh start
   bin/ops.sh verify
   bin/ops.sh stop
   # All green? Proceed. Otherwise: debug & fix.
   ```

3. **Create Branch** (5 min)
   ```bash
   cd /path/to/Gesamtprojekt
   git checkout -b feature/phase-4-bridge
   git push -u origin feature/phase-4-bridge
   ```

### Afternoon
1. **Position 01: Bridge Auth** (4 hours)
   - Create `bridge_auth.py` (100 lines)
   - Implement token validation middleware
   - Write 10 unit tests
   - Verify: `pytest tests/test_auth.py`

2. **Create Bridge Service Skeleton** (2 hours)
   - File: `copilot_bridge.py` (FastAPI app)
   - Port: 12351 (hardcoded for now)
   - Endpoints: `/api/auth/token`, `/health`
   - Test: `curl http://127.0.0.1:12351/health`

### Day 1 Completion Checklist
- [ ] Project manifest reviewed
- [ ] Phase 3 verified (all services running)
- [ ] Branch created + pushed
- [ ] `bridge_auth.py` implemented
- [ ] `copilot_bridge.py` skeleton created
- [ ] Position 01 tests passing (green)
- [ ] Commit pushed: "feat(bridge): auth & skeleton (pos 01)"

---

## 🎯 Day 2–3: Bridge Core (Positions 02–03)

### Position 02: OpenAPI Schema (4 hours)
```bash
# 1. Add FastAPI auto-docs to bridge
# 2. Generate bridge_schema.json via GET /openapi.json
# 3. Write bridge_api.md (200 lines)
# 4. Test: curl http://127.0.0.1:12351/openapi.json | jq .

# File to create:
# - bridge_schema.json (generated)
# - docs/bridge_api.md (handwritten reference)
# - tests/test_openapi.py
```

### Position 03: Dashboard Monitor (4 hours)
```bash
# 1. Add endpoint to main_dashboard.py: GET /api/bridge/status
# 2. Create response: { queue_length, pending, completed, last_sync }
# 3. Update ui_index.html with queue monitor widget
# 4. Test: 
#    - bin/ops.sh start
#    - curl -H "Authorization: Bearer $(cat .env)" http://127.0.0.1:12349/api/bridge/status
#    - Open UI, see queue widget
```

### Day 2–3 Deliverables
- [ ] OpenAPI schema generated + documented
- [ ] Dashboard bridge status endpoint
- [ ] UI queue monitor widget
- [ ] Tests passing
- [ ] Commit: "feat(bridge): openapi + dashboard monitor (pos 02-03)"

---

## 🎯 Week 1 Summary (Day 4–5): Positions 04–05

### Position 04: Retry & Backoff (4 hours)
Create in extension skeleton (TypeScript):
```typescript
// extension/src/retry.ts
export class RetryManager {
  async retryWithBackoff(fn, maxRetries=5) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        return await fn();
      } catch (e) {
        const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s, 8s, 16s
        console.log(`Retry ${i+1}/${maxRetries} after ${delay}ms`);
        await new Promise(r => setTimeout(r, delay));
      }
    }
    throw new Error(`Failed after ${maxRetries} retries`);
  }
}
```

### Position 05: Merge Strategy (4 hours)
Create in `merge.py`:
```python
# merge.py: 3-Way merge algorithm
def three_way_merge(base, local, remote):
    """Implement LCS-based 3-way merge"""
    # Returns: merged_text, conflicts (list of conflict regions)
    ...
```

### Week 1 Completion Checklist
- [ ] Retry manager implemented + tested
- [ ] Merge algorithm implemented + tested
- [ ] All 5 positions in progress or complete
- [ ] Commits pushed: "feat(bridge): retry (pos 04)", "feat(bridge): merge (pos 05)"
- [ ] PR created: "Phase 4 Week 1: Positions 01–05"
- [ ] Ready for code review

---

## 📂 File Structure After Week 1

```
19.dashboard_agent/
├── bridge_auth.py              ← NEW (Position 01)
├── copilot_bridge.py           ← NEW (Position 01–02)
├── merge.py                    ← NEW (Position 05)
├── main_dashboard.py           ← UPDATED (Position 03)
├── ui_index.html               ← UPDATED (Position 03)
├── docs/PDI/
│   ├── project_manifest.md
│   ├── chapters/00_kapitelplan.md
│   └── VALIDATION_FRAMEWORK.md
├── tests/
│   ├── test_auth.py            ← NEW (Position 01)
│   ├── test_openapi.py         ← NEW (Position 02)
│   ├── test_bridge_monitor.py  ← NEW (Position 03)
│   ├── test_merge.py           ← NEW (Position 05)
│   └── ...
└── extension/
    └── src/retry.ts            ← NEW (Position 04)
```

---

## 🔧 Development Workflow (Daily)

### Morning (30 min)
```bash
# 1. Sync latest
git pull origin feature/phase-4-bridge

# 2. Activate venv
source 1.portier_openai/venv313/bin/activate

# 3. Run tests
cd 19.dashboard_agent
pytest tests/ -q

# 4. Check lint
pylint bridge_auth.py copilot_bridge.py
shellcheck ../bin/*.sh

# 5. Smoke test
bin/ops.sh start && sleep 2 && bin/ops.sh health && bin/ops.sh stop
```

### Development (6 hours)
- Focus on 1–2 positions
- Write code + tests
- Document endpoints + examples

### Evening (30 min)
```bash
# 1. Final tests
pytest tests/ -q

# 2. Commit
git add -A
git commit -m "feat(bridge): [position] [brief description]"

# 3. Push
git push origin feature/phase-4-bridge

# 4. Check CI (GitHub Actions)
# Wait for green status
```

---

## 📋 Position 01–05 Details (Week 1)

### Position 01: Bridge Auth & RBAC
**Files to Create:**
- `bridge_auth.py` (100 lines)
- `tests/test_auth.py` (50 lines)

**Endpoint:**
```python
@app.post("/api/auth/token")
async def get_token(credentials: TokenRequest):
    """Issue Bearer token with role"""
    return {
        "token": generate_jwt(credentials.username, credentials.role),
        "role": credentials.role,
        "expires_in": 3600
    }
```

**Middleware:**
```python
@app.middleware("http")
async def auth_middleware(request, call_next):
    """Validate Bearer token on all endpoints except /health"""
    if request.url.path == "/health":
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse({"detail": "Unauthorized"}, 401)
    
    token = auth_header[7:]
    if not verify_token(token):
        return JSONResponse({"detail": "Forbidden"}, 403)
    
    return await call_next(request)
```

**Test:**
```python
def test_auth_required():
    response = client.post("/api/enqueue", json={...})
    assert response.status_code == 401

def test_auth_valid():
    token = "valid_token_here"
    response = client.post(
        "/api/enqueue",
        headers={"Authorization": f"Bearer {token}"},
        json={...}
    )
    assert response.status_code == 200
```

### Position 02: OpenAPI Schema
**Files to Create:**
- `docs/bridge_api.md` (200 lines)
- `tests/test_openapi.py` (30 lines)

**Schema Generation:**
```bash
# FastAPI auto-generates at /openapi.json
# Starlette middleware serves it
curl http://127.0.0.1:12351/openapi.json | jq . > bridge_schema.json
```

**Markdown Reference (Sample):**
```markdown
## Bridge API Reference

### POST /api/enqueue
Enqueue a task.

**Authorization:** Bearer token (writer or admin role)

**Request:**
\`\`\`json
{
  "prompt": "Summarize this file",
  "file_path": "src/main.py",
  "mode": "merge"
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "task_id": "task_12345",
  "status": "queued",
  "created_at": "2025-11-07T08:00:00Z"
}
\`\`\`

**Error (401):**
\`\`\`json
{"detail": "Unauthorized"}
\`\`\`
```

### Position 03: Dashboard Monitor
**Files to Update:**
- `main_dashboard.py` (add 30 lines)
- `ui_index.html` (add 50 lines)
- `tests/test_bridge_status.py` (new, 40 lines)

**Endpoint:**
```python
@app.get("/api/bridge/status")
async def get_bridge_status(token: HTTPAuthorizationCredentials = Security(security)):
    """Get Bridge queue status"""
    try:
        response = requests.get("http://127.0.0.1:12351/api/status", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        raise HTTPException(status_code=502, detail="Bridge unavailable")
```

**UI Widget (JavaScript):**
```javascript
async function updateQueueStatus() {
    const tok = localStorage.getItem('token');
    const r = await fetch('http://127.0.0.1:12349/api/bridge/status', {
        headers: { 'Authorization': `Bearer ${tok}` }
    });
    const data = await r.json();
    document.getElementById('queue-stats').innerHTML = `
        <p>Pending: ${data.pending}</p>
        <p>Completed: ${data.completed}</p>
        <p>Last Sync: ${data.last_sync}</p>
    `;
}
setInterval(updateQueueStatus, 5000);
```

### Position 04: Retry & Backoff
**Files to Create:**
- `extension/src/retry.ts` (100 lines)
- `extension/test/retry.test.ts` (50 lines)

**Implementation:**
```typescript
export async function retryWithBackoff<T>(
    fn: () => Promise<T>,
    maxRetries = 5
): Promise<T> {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            const delay = Math.pow(2, i) * 1000; // 1s, 2s, 4s, 8s, 16s
            console.log(`Retry ${i + 1}/${maxRetries} after ${delay}ms`);
            await new Promise(r => setTimeout(r, delay));
        }
    }
    throw new Error(`Failed after ${maxRetries} retries`);
}
```

### Position 05: Merge Strategy
**Files to Create:**
- `merge.py` (150 lines)
- `tests/test_merge.py` (100 lines)

**Implementation Skeleton:**
```python
def three_way_merge(base: str, local: str, remote: str) -> tuple:
    """
    Perform 3-way merge.
    Returns: (merged_text, conflicts)
    """
    # Step 1: Compute diffs (base→local, base→remote)
    local_changes = diff(base, local)
    remote_changes = diff(base, remote)
    
    # Step 2: Identify conflicts
    conflicts = find_conflicts(local_changes, remote_changes)
    
    # Step 3: Merge (simple append if no conflicts)
    if not conflicts:
        return merge_simple(base, local, remote), []
    
    # Step 4: Mark conflicts
    merged = mark_conflicts(base, local, remote, conflicts)
    return merged, conflicts

def mark_conflicts(base, local, remote, conflicts):
    """Mark conflict regions with <<<<<<, |||||, ======, >>>>>>"""
    result = []
    for region in conflicts:
        result.append(f"<<<<<<< LOCAL\n{local[region]}\n")
        result.append(f"|||||| BASE\n{base[region]}\n")
        result.append(f"======\n{remote[region]}\n")
        result.append(f">>>>>>> REMOTE\n")
    return "".join(result)
```

---

## 🧪 Week 1 Testing Plan

### Daily Smoke Tests
```bash
# Each morning, verify nothing broke
pytest tests/test_auth.py tests/test_openapi.py tests/test_merge.py -q
```

### Integration Test (Friday)
```bash
# Full bridge startup + dashboard access
bin/ops.sh start
curl -H "Authorization: Bearer $(cat .env)" http://127.0.0.1:12349/api/bridge/status
open http://127.0.0.1:12349/ui_index.html  # Verify queue widget
bin/ops.sh stop
```

### Lint Check
```bash
pylint 19.dashboard_agent/bridge_auth.py
pylint 19.dashboard_agent/copilot_bridge.py
pylint 19.dashboard_agent/merge.py
```

---

## 📊 Week 1 Metrics

**Target:**
- ✅ 5/20 positions started
- ✅ ~500 lines of code
- ✅ ~200 lines of tests
- ✅ 0 lint errors
- ✅ 1 PR merged (or in review)

**Daily Log Template:**
```markdown
## Day 1 (Mon 2025-11-07)
- [ ] Position 01 auth implementation (4h)
- [ ] Position 01 tests (1h)
- [ ] Bridge skeleton (1h)
- Commit: "feat(bridge): auth & skeleton"

## Day 2 (Tue 2025-11-08)
- [ ] Position 02 OpenAPI schema (3h)
- [ ] Position 02 tests (1h)
- [ ] Dashboard bridge endpoint (2h)
- Commit: "feat(bridge): openapi + dashboard"

...
```

---

## ✅ Week 1 Completion Criteria

- [ ] Positions 01–05 complete or ~80% done
- [ ] All tests passing (green CI)
- [ ] 0 lint errors
- [ ] PR created + ready for review
- [ ] Safepoints written (≥5 across all positions)
- [ ] Documentation updated
- [ ] Commit history clean + understandable

---

## 🚀 Ready to Start?

**Final Checklist Before Day 1:**

```bash
# 1. Verify Phase 3
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
bin/ops.sh verify
# Expected: all green

# 2. Review docs
cat 19.dashboard_agent/docs/PDI/project_manifest.md
cat 19.dashboard_agent/docs/PDI/chapters/00_kapitelplan.md

# 3. Create branch
git checkout -b feature/phase-4-bridge
git push -u origin feature/phase-4-bridge

# 4. Create directory for bridge
mkdir -p 19.dashboard_agent/extension/src
mkdir -p 19.dashboard_agent/tests

# 5. Start development
# → Begin Position 01
```

---

**[PDI-FOOTER: Phase 4 Week 1 guide ready. All positions documented. Development can commence. Estimated 4-5 days to complete first 5 positions.]**
