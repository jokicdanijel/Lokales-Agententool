# Schritt 4 – Vollständige 20-Agent-Integration (Finale Architektur)

**Status:** Planning & Specification
**Version:** 1.0.0
**Datum:** 2025-11-10
**Abhängig von:** Schritt 2 ✅ + Schritt 3 ✅

---

## Übersicht

**Schritt 4** integriert alle 20 Agenten (opena1–opena20) in die ELION Hyper-Dashboard Architektur mit:

1. ✅ Vollständiger Port-Policy Compliance (12344–12369)
2. ✅ Unified Tool-Registry Routing (Schritt 2)
3. ✅ Append-Only Safepoint Persistence (Schritt 3)
4. 🟡 Cross-Agent Communication (HTTP REST)
5. 🟡 End-to-End Integration Testing
6. 🟡 Monitoring & Health Checks

---

## 1. Architektur-Übersicht

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ELION HYPER-DASHBOARD                             │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────┐         ┌─────────────────────┐              │
│  │ opena1              │         │ opena2              │              │
│  │ Koordinator         │────────▶│ Archivator          │              │
│  │ (Port 12344)        │         │ (Port 12345)        │              │
│  │                     │         │                     │              │
│  │ - Dispatch routing  │         │ - Safepoint store   │              │
│  │ - Validation        │         │ - Deduplication    │              │
│  │ - Error handling    │         │ - Integrity check   │              │
│  └─────────────────────┘         └─────────────────────┘              │
│           │                               │                           │
│           └───────────┬───────────────────┘                           │
│                       │                                               │
│         ┌─────────────▼──────────────────────────────┐                │
│         │                                            │                │
│      ┌──┴────────┐  ┌────────────┐  ┌────────────┐  │ Agent Clusters │
│      │            │  │            │  │            │  │                │
│      ▼            ▼  ▼            ▼  ▼            ▼  │                │
│   opena3      opena4-6        opena7-10       opena11-20              │
│  (8080)     Communication    Chatbots       Functional+Content+Data   │
│                                                                        │
│  - OpenWebUI      - Telegram     - Email AI       - Social Media      │
│  - Browser        - VS Code      - WhatsApp AI    - Shop Creator      │
│  - Telegram       - Browser      - Voice IVR      - Trading           │
│                                                    - Dashboard         │
│                                                                        │
│         ┌──────────────────┬──────────────────┐                       │
│         │ Tool-Dispatcher  │ Dedupe-Engine    │                       │
│         │ (Schritt 2)      │ (Schritt 3)      │                       │
│         └──────────────────┴──────────────────┘                       │
│                       │                                               │
└───────────────────────┼───────────────────────────────────────────────┘
                        │
                   Port-Policy
                   [12344-12369]
```

---

## 2. Dienst-Mapping & Port-Zuordnung

| #   | Agent                   | Port   | Kategorie     | Status     | Implementiert |
| --- | ----------------------- | ------ | ------------- | ---------- | ------------- |
| 1   | opena1 (Koordinator)    | 12344  | Infrastruktur | ✅ Aktiv   | Ja            |
| 2   | opena2 (Archivator)     | 12345  | Infrastruktur | ✅ Aktiv   | Ja            |
| 3   | opena3 (OpenWebUI)      | 8080\* | Kommunikation | ✅ Aktiv   | Ja            |
| 4   | opena4 (Telegram)       | 12347  | Kommunikation | ✅ Aktiv   | Ja            |
| 5   | opena5 (VS Code)        | 12348  | Kommunikation | 🟡 Geplant | Nein          |
| 6   | opena6 (Browser)        | 12349  | Kommunikation | 🔴 Pending | Nein          |
| 7   | opena7 (Email Chatbot)  | 12350  | Chatbot       | 🔴 Pending | Nein          |
| 8   | opena8 (WhatsApp)       | 12351  | Chatbot       | 🔴 Pending | Nein          |
| 9   | opena9 (Call Answer)    | 12352  | Chatbot       | 🔴 Pending | Nein          |
| 10  | opena10 (Call Initiate) | 12353  | Chatbot       | 🔴 Pending | Nein          |
| 11  | opena11 (Unlock Master) | 12354  | Funktional    | 🔴 Pending | Nein          |
| 12  | opena12 (Social Media)  | 12355  | Funktional    | 🔴 Pending | Nein          |
| 13  | opena13 (Influencer)    | 12356  | Funktional    | 🔴 Pending | Nein          |
| 14  | opena14 (Calendar)      | 12357  | Funktional    | 🔴 Pending | Nein          |
| 15  | opena15 (HTML Creator)  | 12358  | Content       | 🔴 Pending | Nein          |
| 16  | opena16 (Shop Creator)  | 12359  | Content       | 🔴 Pending | Nein          |
| 17  | opena17 (Homepage)      | 12360  | Content       | 🔴 Pending | Nein          |
| 18  | opena18 (Local Archive) | 12361  | Data          | 🔴 Pending | Nein          |
| 19  | opena19 (Trading)       | 12362  | Data          | 🔴 Pending | Nein          |
| 20  | opena20 (Dashboard)     | 12363  | Data          | ✅ Aktiv   | Ja            |

\*Port 8080 ist exklusiv reserviert (Docker/OpenWebUI)

---

## 3. Integration-Fases (Phased Rollout)

### Phase 4A: Basis-Integration (NOW)

- ✅ Schritt 2 (Tool-Registry) – Deployed
- ✅ Schritt 3 (Dedupe-Engine) – Deployed
- 🟡 Routing-Tests für existierende Agenten
- 🟡 Port-Policy Compliance Check (alle 20 Ports)

### Phase 4B: Kommunikations-Agenten

- opena3 (OpenWebUI) – Already deployed
- opena4 (Telegram) – Already deployed
- opena5 (VS Code) – Implementation (Schritt 5)
- opena6 (Browser) – New implementation

### Phase 4C: Chatbot-Agenten

- opena7 (Email) – New implementation
- opena8 (WhatsApp) – New implementation
- opena9 (Call Answer) – New implementation
- opena10 (Call Initiate) – New implementation

### Phase 4D: Funktional-Agenten

- opena11 (Unlock) – New implementation
- opena12 (Social Media) – New implementation
- opena13 (Influencer) – New implementation
- opena14 (Calendar) – New implementation

### Phase 4E: Content + Data Agenten

- opena15 (HTML) – New implementation
- opena16 (Shop) – New implementation
- opena17 (Homepage) – New implementation
- opena18 (Local Archive) – New implementation
- opena19 (Trading) – New implementation
- opena20 (Dashboard) – Schritt 5

---

## 4. Routing-Logik & Dispatch-Flow

### 4.1 Request-Flow (Eingang)

```
Client Request
    ↓
POST http://127.0.0.1:12344/api/dispatch
    ↓
opena1 (Koordinator)
    │
    ├─ 1. Validate token (Authorization header)
    ├─ 2. Parse tool_name (e.g., "telep", "emailp", "kalp")
    ├─ 3. Lookup in tool_registry
    │   └─ resolve_tool(tool_name) → AgentSchema + port
    ├─ 4. Create Safepoint request
    │   └─ call: opena2.write_safepoint()
    ├─ 5. Forward to agent
    │   └─ POST http://127.0.0.1:{PORT}/endpoint
    │
    └─ Error? → Return schema 8.3 error response
```

**Beispiel: Telegram-Nachricht**

```bash
POST http://127.0.0.1:12344/api/dispatch
Content-Type: application/json
Authorization: Bearer $TOKEN

{
  "tool_name": "telep",
  "command": "send_message",
  "user_id": "user_123",
  "text": "Hello from Koordinator"
}
```

**opena1 macht:**

1. Validate Token ✓
2. Parse tool_name="telep" ✓
3. Lookup registry.get_agent_by_tool("telep") → opena4 @ port 12347
4. Create Safepoint in opena2 ✓
5. Forward to http://127.0.0.1:12347/telegram/send ✓
6. Return response (or error)

### 4.2 Response-Flow (Ausgang)

```
opena[N] processes & returns response
    ↓
opena1 receives response
    │
    ├─ 1. Validate response schema
    ├─ 2. Create Safepoint response
    │   └─ call: opena2.write_safepoint()
    ├─ 3. Check for dedupe
    │   └─ Already seen hash? Log duplicate
    │
    └─ Return to client
```

---

## 5. Tool-Registry Integration

Alle Agenten sind in `config/agent_registry.yaml` definiert:

```yaml
# config/agent_registry.yaml
infrastructure:
  kordinator:
    agent_id: "opena1"
    port: 12344

  archivator:
    agent_id: "opena2"
    port: 12345

communication:
  telegram:
    agent_id: "opena4"
    port: 12347
    endpoints:
      - path: "/telegram/send"
        method: "POST"

  # ... (alle 20)
```

**Python-Code (opena1/koordinator.py):**

```python
from tool_registry import get_registry

registry = get_registry()

@app.post("/api/dispatch")
async def dispatch(req: DispatchRequest):
    # Resolve tool → agent
    agent = registry.get_agent_by_tool(req.tool_name)
    if not agent:
        raise HTTPException(404, "Tool not found")

    # Create safepoint
    sp = await manager.create_safepoint(
        source="opena1",
        destination=agent.agent_id,
        kind="REQUEST",
        payload=req.dict()
    )

    # Forward to agent
    url = f"http://127.0.0.1:{agent.port}{agent.endpoint}"
    response = await forward_to_agent(url, req.dict())

    # Write safepoint
    await manager.write_safepoint(sp)

    return response
```

---

## 6. Safepoint-Integration (Schritt 3)

Jeder Agent-Aufruf speichert Request/Response als Safepoint:

```json
{
  "sp_id": "SP1731227400_opena4→opena2_REQUEST.json",
  "timestamp": "2025-11-10T12:30:00Z",
  "source": "opena4",
  "destination": "opena2",
  "kind": "REQUEST",
  "payload": {
    "strict": true,
    "tool_name": "telep",
    "command": "send_message",
    "user_id": "user_123",
    "text": "Hello"
  },
  "hash": "sha256:abcd...1234",
  "dedupe_count": 1
}
```

**Speicherort:** `archivp/2025/11/10/index.jsonl`

**Deduplication (automatisch):**

- SHA-256 hash des Payloads
- Wenn hash bereits existiert: `dedupe_count += 1`
- Redundante Verarbeitung vermieden

---

## 7. Port-Policy Enforcement (Alle Services)

Jeder Agent muss diese Validierung durchführen:

```python
# config.py (alle Agenten)
import sys

ALLOWED_PORT_RANGE = (12344, 12369)
FORBIDDEN_PORTS = [8080]

def validate_port_policy(port: int):
    """Enforce port policy on startup"""
    if port in FORBIDDEN_PORTS:
        logger.error(f"❌ FATAL: Port {port} is forbidden by policy")
        sys.exit(1)

    if port < ALLOWED_PORT_RANGE[0] or port > ALLOWED_PORT_RANGE[1]:
        logger.warning(f"⚠️  Port {port} outside [12344-12369]")

    return True
```

---

## 8. End-to-End Test-Plan

### Test Suite 1: Health Checks

```bash
# Test alle 20 Agenten verfügbar sind
for port in {12344..12369}; do
  if ! curl -s http://127.0.0.1:$port/health > /dev/null; then
    echo "❌ Port $port not responding"
  fi
done
```

### Test Suite 2: Routing

```python
# test_routing.py
async def test_telegram_routing():
    # 1. Send dispatch request to opena1
    response = await dispatch(
        tool_name="telep",
        command="send_message",
        user_id="test_user",
        text="Hello"
    )

    # 2. Verify response
    assert response["status"] == "ok"

    # 3. Check safepoint in opena2
    safepoints = await get_last_safepoints(n=1)
    assert safepoints[0]["destination"] == "opena4"
    assert safepoints[0]["kind"] == "REQUEST"
```

### Test Suite 3: Safepoint Integrity

```python
# test_integrity.py
async def test_safepoint_chain():
    # 1. Execute 5 operations
    for i in range(5):
        await dispatch(tool_name="kalp", ...)

    # 2. Verify all safepoints in archive
    safepoints = await get_last_safepoints(n=5)
    assert len(safepoints) == 5

    # 3. Verify HEADS.json chain
    heads = await get_heads()
    assert len(heads) == 5

    # 4. Verify INTEGRITY.json
    integrity = await verify_integrity()
    assert integrity["status"] == "ok"
```

---

## 9. Implementierungs-Checkliste

### Phase 4A: Basis-Integration

- [ ] Prüfe tool_registry.py (alle 20 Agenten registriert)
- [ ] Prüfe port-policy enforcement in allen Services
- [ ] Starte Health-Check-Test Suite
- [ ] Verifiziere Routing-Logik opena1 → Ziel-Agent

### Phase 4B: Kommunikations-Agenten

- [ ] opena3 (OpenWebUI) – Health check
- [ ] opena4 (Telegram) – Health check
- [ ] opena5 (VS Code) – Startup test
- [ ] opena6 (Browser) – Startup test

### Phase 4C–4E: Remaining Agents

- [ ] Implementiere template für neue Agenten
- [ ] Port-Policy validation für alle Ports
- [ ] Routing test für jedes neue Service
- [ ] Safepoint test (write/read/dedupe)

### Final Integration Tests

- [ ] End-to-End dispatch flow (opena1 → opena[N])
- [ ] Error handling (schema 8.3 compliance)
- [ ] Safepoint chain integrity (HEADS.json + INTEGRITY.json)
- [ ] Port-Policy compliance check (alle 20 Ports)

---

## 10. Fehler-Handling & Resilienz

### 10.1 Fehler-Kategorien

| Code | Fehler                 | Behandlung                        |
| ---- | ---------------------- | --------------------------------- |
| 400  | Invalid request schema | Return schema 8.3 error + log     |
| 401  | Missing Authorization  | Reject + 401 response             |
| 403  | Invalid token          | Reject + 403 response             |
| 404  | Tool not found         | Return 404 + suggest alternatives |
| 500  | Agent internal error   | Retry logic (backoff)             |
| 503  | Agent unavailable      | Circuit breaker                   |

### 10.2 Retry-Logik

```python
# tool_dispatcher.py
async def dispatch_with_retry(tool_name: str, payload: dict):
    max_retries = 3
    backoff_ms = 500

    for attempt in range(max_retries):
        try:
            response = await forward_to_agent(...)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(backoff_ms / 1000)
                backoff_ms *= 2
            else:
                raise
```

---

## 11. Monitoring & Observability

### 11.1 Health Endpoints

Alle Agenten müssen `/health` implementieren:

```bash
curl http://127.0.0.1:{PORT}/health

{
  "service": "opena4",
  "status": "ok",
  "uptime_seconds": 3600,
  "timestamp": "2025-11-10T12:30:00Z",
  "port_policy": {
    "window": [12344, 12369],
    "forbidden": [8080]
  }
}
```

### 11.2 Logging

```python
logger.info(f"Dispatch: {tool_name} → {agent_id}")
logger.debug(f"Safepoint: {sp_id}")
logger.error(f"Agent error: {e}")
```

---

## 12. Abhängigkeiten & Next Steps

**Schritt 2:** ✅ Tool-Registry (committed 2025-11-10)
**Schritt 3:** ✅ Safepoint Dedupe (committed 2025-11-10)
**Schritt 4:** 🟡 **THIS DOCUMENT** – Spec ready, implementation starting
**Schritt 5:** 🔴 VS Code Bridge (blocked by Schritt 4)

---

## 13. Erfolgs-Kriterien

✅ Alle 20 Agenten in `tool_registry.py` registriert
✅ Port-Policy [12344-12369] durchgesetzt
✅ Routing opena1 → opena[N] getestet
✅ Safepoint write/read/dedupe funktional
✅ Health-Checks für alle Services grün
✅ E2E-Tests bestanden (≥ 80% coverage)
✅ Documentation vollständig
✅ Commits to main branch gepusht

---

**Dokumentation:** Danijel – ELION Gesamtprojekt
**Letztes Update:** 2025-11-10T12:45:00Z
