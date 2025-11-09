# ELION Registry Management & Auto-Discovery

## Überblick

Das **Self-Healing Registry System** registriert automatisch alle laufenden Agenten, indem es echte `/health`-Endpoints abfragt. Dadurch wird vermieden:
- Tippfehler bei agent_id/Port-Kombinationen
- Registrierung von nicht-laufenden Services
- Manuelle Port-Verwaltung
- `last_health: null` wegen veralteter Registry

---

## System-Architektur

```
┌──────────────────────────────────────────────────────────────┐
│  Dashboard (main_dashboard.py)                               │
│  ├─ Port 12349                                               │
│  ├─ /api/agent/register (POST)                              │
│  ├─ /api/agent/list (GET)                                   │
│  ├─ /api/status/all (GET)                                   │
│  ├─ Background-Poller (5s interval)                          │
│  └─ SSE Bus für Live-Events                                  │
└──────────────────────────────────────────────────────────────┘
                          ↕ HTTP
┌──────────────────────────────────────────────────────────────┐
│  Agent Registry (agent_registry.py)                          │
│  ├─ In-Memory Store                                          │
│  ├─ register(agent_id, endpoint)                            │
│  ├─ get_all_status()  ← triggers health probe               │
│  ├─ update_health(agent_id, is_alive, ts)                  │
│  └─ Last Health Timestamps                                   │
└──────────────────────────────────────────────────────────────┘
        ↕                 ↕ (Status Probe)      ↕
   ┌─────────────┐   ┌──────────┐  ... ┌──────────────┐
   │ opena1      │   │ opena2   │      │ opena3...19  │
   │ :12344      │   │ :12345   │      │ :12347–367   │
   │ /health ✓   │   │ /health✓ │      │ /health ✓    │
   └─────────────┘   └──────────┘      └──────────────┘
```

---

## 1. Auto-Discovery Workflow

### 1.1 Skript: `bin/agents_auto_register.sh`

**Zweck:** Findet alle laufenden Agenten und registriert sie sauber beim Dashboard.

**Ausführung:**
```bash
# Option A: Mit Token aus .env
cd /path/to/Gesamtprojekt
bash bin/agents_auto_register.sh

# Option B: Mit explizitem Token
TOKEN="MEIN_SUPER_TOKEN_123" bash bin/agents_auto_register.sh

# Option C: Mit Custom Dashboard-URL
DASHBOARD_URL="http://127.0.0.1:12349" TOKEN="xyz" bash bin/agents_auto_register.sh
```

**Output-Beispiel:**
```
════════════════════════════════════════════════════════════════
   Auto-Discovery & Registration – 2025-11-09 14:23:45
════════════════════════════════════════════════════════════════

Dashboard: http://127.0.0.1:12349
Token:     MEIN_SUPER_TOKEN_1... (length: 20)

Scanning ports: 12344 12345 12346 12347 12348 12349 12350 ...

✓ Port 12344: opena1_Agent → agent_id='opena1_agent'
✓ Port 12345: opena2_Archivator → agent_id='opena2_archivator'
✓ Port 12346: kordp_Coordinator → agent_id='kordp_coordinator'
...

────────────────────────────────────────────────────────────────
   Registration Phase
────────────────────────────────────────────────────────────────

✓ Registered: opena1_agent → http://127.0.0.1:12344
✓ Registered: opena2_archivator → http://127.0.0.1:12345
...

════════════════════════════════════════════════════════════════
   Registry Snapshot
════════════════════════════════════════════════════════════════

Total agents in registry: 12

Agents:
  opena1_agent → http://127.0.0.1:12344 (registered: 2025-11-09T14:23:45.123456Z)
  opena2_archivator → http://127.0.0.1:12345 (registered: 2025-11-09T14:23:45.234567Z)
  ...

Summary:
  Scanned ports:     46
  Found & listening: 12
  Registered:        12
  Failed:            0
  Skipped:           34

✓ Auto-Discovery & Registration complete.
```

### 1.2 Was das Skript macht

1. **Scan**: Fragt alle definierten Ports ab
   - Timeout: 1 Sekunde pro Port (schnell, non-blocking)
   - Silent: Fehler werden geloggt, nicht als Fehler behandelt

2. **Normalisierung**: Extrahiert `service` aus `/health`
   ```json
   {"service": "opena1_Agent", "status": "healthy", ...}
   ↓
   agent_id = "opena1_agent" (lowercase, spaces→underscores)
   ```

3. **Validierung**: Prüft JSON-Struktur mit `safe_jq`
   - Verhindert Parse-Fehler
   - Skipped ungültige Responses

4. **Registration**: POST an `/api/agent/register`
   ```bash
   curl -X POST http://127.0.0.1:12349/api/agent/register \
     -H "Authorization: Bearer TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"agent_id":"opena1_agent","endpoint":"http://127.0.0.1:12344"}'
   ```

5. **Feedback**: Zeigt Erfolge/Fehler und finale Registry-Snapshot

---

## 2. Background-Poller

### 2.1 Modul: `background_poller.py`

**Zweck:** Lädt im Dashboard-Startup und pollts alle Agenten im Hintergrund.

**Lifecycle:**
```
@app.on_event("startup")
  └─ background_poller.on_startup()
     └─ asyncio.create_task(poll_loop())
        └─ loop: every 5s: await registry.get_all_status()

@app.on_event("shutdown")
  └─ background_poller.on_shutdown()
     └─ Cancel poller_task
```

### 2.2 Funktionsweise

**Poll-Zyklus (alle 5 Sekunden):**
```python
async def _poll_loop():
    while True:
        # Probe alle registrierten Agenten
        status = await registry.get_all_status()
        
        # Registry aktualisiert:
        # - agents["opena1_agent"].status = "up" oder "down"
        # - agents["opena1_agent"].last_health = "2025-11-09T14:23:45.123Z"
        
        await asyncio.sleep(5)  # Nächste Runde
```

**Ergebnis:**
- `GET /api/status/all` zeigt immer aktuelle `last_health` (nicht null)
- `GET /api/status/all?probe=true` kann auch on-demand triggern

### 2.3 Konfiguration

In `main_dashboard.py`:
```python
from background_poller import on_startup as poller_startup, on_shutdown as poller_shutdown

@app.on_event("startup")
async def startup_event():
    set_registry(agent_registry)
    await poller_startup()  # Startet poller_task mit 5s interval

@app.on_event("shutdown")
async def shutdown_event():
    await poller_shutdown()
```

### 2.4 Diagnostics

**Endpoint:** `GET /api/diagnostics/poller`
```bash
curl -s -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:12349/api/diagnostics/poller | jq .

# Response:
{
  "poller": {
    "is_running": true,
    "interval_sec": 5,
    "registry_set": true,
    "timestamp": "2025-11-09T14:23:45.123456"
  }
}
```

---

## 3. Registry API (mit JWT Auth)

### 3.1 Agent Listing

**Endpoint:** `GET /api/agent/list`

```bash
curl -s -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:12349/api/agent/list | jq .

# Response:
{
  "strict": true,
  "count": 12,
  "agents": {
    "opena1_agent": {
      "endpoint": "http://127.0.0.1:12344",
      "status": "up",
      "last_health": "2025-11-09T14:23:45.123456Z",
      "registered_at": "2025-11-09T14:23:00.000000Z"
    },
    ...
  }
}
```

### 3.2 Full Status

**Endpoint:** `GET /api/status/all`

```bash
curl -s -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:12349/api/status/all | jq .

# Response:
{
  "strict": true,
  "agents": {
    "opena1_agent": {"status": "up", "last_health": "2025-11-09T14:23:45.123Z"},
    "opena2_archivator": {"status": "up", "last_health": "2025-11-09T14:23:44.456Z"},
    "kordp_coordinator": {"status": "down", "last_health": "2025-11-09T14:20:00.000Z"},
    ...
  }
}
```

### 3.3 JWT Token Management

**Generate for Single Agent:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  http://127.0.0.1:12349/api/agents/opena1_agent/token | jq .

# Response:
{
  "agent_id": "opena1_agent",
  "token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "scope": "invoke"
}
```

**Generate for ALL Agents:**
```bash
curl -s -X GET \
  -H "Authorization: Bearer TOKEN" \
  http://127.0.0.1:12349/api/agents/tokens/all | jq .

# Response:
{
  "count": 12,
  "tokens": {
    "opena1_agent": "eyJhbGciOiJSUzI1NiI...",
    "opena2_archivator": "eyJhbGciOiJSUzI1NiI...",
    ...
  },
  "generated_at": "2025-11-09T14:23:45.123456Z"
}
```

**Verify Token:**
```bash
curl -s -X POST \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token":"eyJhbGciOiJSUzI1NiI..."}' \
  http://127.0.0.1:12349/api/auth/verify | jq .

# Response:
{
  "valid": true,
  "agent_id": "opena1_agent",
  "scope": "invoke",
  "permissions": ["read", "write"],
  "expires_at": 1699598745,
  "error": null
}
```

---

## 4. Setup & Betrieb

### 4.1 Initial Setup

```bash
# 1. Dashboard starten
cd /path/to/Gesamtprojekt
bin/ops.sh start

# 2. Warte bis Dashboard läuft
sleep 2

# 3. Auto-Register alle Agenten
bash bin/agents_auto_register.sh

# 4. Prüfe Registry
TOKEN=$(cat .env)
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12349/api/agent/list | jq '.count'
```

### 4.2 Continuous Operation

**Dashboard lauft:**
- Poll-Zyklus startet automatisch in Startup
- Alle 5 Sekunden: Probe alle Agenten
- `last_health` immer aktuell

**Nach neuen Agent starten:**
```bash
# Option A: Auto-Register erneut laufen
bash bin/agents_auto_register.sh

# Option B: Manuell registrieren
TOKEN=$(cat .env)
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12349/api/agent/register \
  -d '{"agent_id":"opena20_new","endpoint":"http://127.0.0.1:12368"}'
```

### 4.3 Troubleshooting

**Nur 3 Agents registriert?**
```bash
# Prüfe laufende Services
bash bin/check_ports.sh

# Auto-Register erneut
bash bin/agents_auto_register.sh

# Prüfe Dashboard-Logs
tail -50 logs/dashboard_runtime.log
```

**last_health bleibt null?**
```bash
# Prüfe Poller
curl -s -H "Authorization: Bearer $(cat .env)" \
  http://127.0.0.1:12349/api/diagnostics/poller | jq .

# Sollte is_running: true zeigen
```

**Agent zeigt "down" obwohl online?**
```bash
# Prüfe Agent selbst
curl -s http://127.0.0.1:12344/health | jq .

# Wenn antwortet: Registry ist veraltet, erzwinge Probe
curl -s -H "Authorization: Bearer $(cat .env)" \
  http://127.0.0.1:12349/api/status/all?probe=true | jq .
```

---

## 5. Best Practices

### 5.1 Registry as Source of Truth

- **Nicht** manually registrieren (anfällig für Fehler)
- **Immer** `agents_auto_register.sh` verwenden
- Scripte sind idempotent (safe to run mehrmals)

### 5.2 Token Management

```bash
# Before any API call
TOKEN=$(cat .env)

# All dashboard endpoints require Bearer token
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12349/api/...

# Generate agent tokens for inter-agent auth
AGENT_TOKEN=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12349/api/agents/opena1_agent/token | jq -r .token)

# Use agent token for secure communication
curl -H "Authorization: Bearer $AGENT_TOKEN" \
  http://127.0.0.1:12344/invoke
```

### 5.3 Monitoring

```bash
# Quick health snapshot
watch -n 1 'curl -s -H "Authorization: Bearer $(cat .env)" \
  http://127.0.0.1:12349/api/status/all | jq ".agents | map(.status) | group_by(.) | map({status: .[0], count: length})"'

# Output:
# [
#   {"status": "down", "count": 2},
#   {"status": "up", "count": 10}
# ]
```

---

## 6. Implementation Details

### 6.1 Agent Registry State

```python
# In-memory store (from agent_registry.py)
{
  "opena1_agent": {
    "endpoint": "http://127.0.0.1:12344",
    "status": "up",  # "up" oder "down"
    "last_health": "2025-11-09T14:23:45.123456Z",
    "registered_at": "2025-11-09T14:23:00.000000Z",
    "healthy_count": 45,
    "unhealthy_count": 2,
    "last_probe_duration_ms": 123
  },
  ...
}
```

### 6.2 Probe Logic

```python
async def get_all_status():
    for agent_id, agent in self.agents.items():
        try:
            resp = await http_get(f"{agent['endpoint']}/health", timeout=2s)
            agent['status'] = 'up'
            agent['last_health'] = now()
        except (Timeout, ConnectionError):
            agent['status'] = 'down'
            # last_health bleibt alt
```

### 6.3 Poller Schedule

- **Interval:** 5 Sekunden (konfigurierbar)
- **Timeout pro Agent:** 2 Sekunden
- **Parallelität:** Alle Agenten gleichzeitig (asyncio)
- **Fehlertoleranz:** Einzelne Timeouts stoppen Poller nicht

---

## 7. Fehlerbehandlung

| Fehler | Ursache | Lösung |
|--------|--------|--------|
| `jq parse error` | Ungültige JSON-Response | Prüfe Agent `/health` Response |
| `403 Forbidden` | Falscher Token | Regeneriere `.env`: `bash bin/env_bootstrap.sh` |
| `Agent not responding` | Service nicht online | `bash bin/ops.sh start` |
| `last_health: null` | Poller läuft nicht | Prüfe Dashboard `/api/diagnostics/poller` |
| `Registry empty` | Keine Auto-Registration laufen | Führe `bash bin/agents_auto_register.sh` aus |

---

## 8. Integration mit CI/CD

```yaml
# .github/workflows/registry_verify.yml
name: Registry Health Check

on: [push]

jobs:
  registry:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start Services
        run: bash bin/ops.sh start
      - name: Auto-Register
        run: |
          TOKEN=$(cat .env) bash bin/agents_auto_register.sh
      - name: Verify Registry
        run: |
          curl -s -H "Authorization: Bearer $(cat .env)" \
            http://127.0.0.1:12349/api/agent/list | jq '.count > 8'
```

---

## Summary

| Komponente | Zweck | Trigger |
|-----------|--------|---------|
| `agents_auto_register.sh` | Findet + registriert alle Agenten | Manual oder CI/CD |
| `background_poller.py` | Lädt im Hintergrund, Updates `last_health` | Automatic @ startup |
| `/api/agent/list` | Zeigt alle registrierten Agenten | GET mit Token |
| `/api/status/all` | Health-Snapshot (mit poller data) | GET mit Token |
| `/api/agents/{id}/token` | Generiere JWT für Agent | POST mit Admin Token |

**Ergebnis:** Registry ist immer aktuell, kein `last_health: null`, alle Agenten laufen.
