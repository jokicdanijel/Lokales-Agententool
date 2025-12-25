# 🔄 Coordinator Self-Knowledge Module – opena1 KB

**Erstellt:** Nov 8, 2025 19:00 UTC
**Version:** 1.0
**Status:** 🟢 OPERATIONAL & SELF-AWARE

---

## 🎯 Mission Statement

**opena1 = Central Coordinator für ELION Hyper-Dashboard**

```
Responsible for:
- Agent Discovery & Registration
- Health Monitoring (5s polling)
- Event Bus Management (inter-service communication)
- Registry Persistence (agent_registry.json)
- Failover Handling (agent death detection)
```

---

## 🏢 Core Identity

| Eigenschaft      | Wert                                               |
| ---------------- | -------------------------------------------------- |
| **Port**         | 12344                                              |
| **Role**         | Orchestrator / Event Broker                        |
| **Status**       | ✅ RUNNING (Nov 8)                                 |
| **Uptime**       | Continuous (since Nov 8, 12:00)                    |
| **Dependencies** | None (independent)                                 |
| **Dependents**   | All other services (opena2, 4, 19, finance, kordp) |

---

## 📋 Responsibilities

### 1. Agent Registry Management

**What:** Central registry of all active services

**How:**

```
opena1 maintains: agent_registry.json
├─ opena2 (Port 12345) → Archive
├─ opena_finance (Port 12347) → Finance DB
├─ opena4_telegram (Port 12348) → Telegram Bridge
├─ kordp (Port 12346) → Relay
├─ opena19 (Port 12349) → Dashboard [Nov 9]
└─ (future agents...)
```

**Updates:**

- New agent registers: POST /api/agent/register (via opena19)
- Agent dies: Detected via health check → marked "unhealthy"
- Agent recovers: Health check succeeds → marked "healthy"

---

### 2. Health Monitoring

**What:** Poll all registered agents every 5 seconds

**How:**

```
Every 5 seconds:
  FOR each agent in registry:
    GET /health from agent
    IF 200 response:
      mark as "healthy"
      update last_check timestamp
    IF timeout or error:
      mark as "unhealthy"
      broadcast event: "agent_unhealthy"
      log to archive: ERROR_<agent>_NO_RESPONSE
```

**Metrics Tracked:**

- Last check timestamp
- Current status (healthy/unhealthy)
- Consecutive failures
- Time since last healthy check

---

### 3. Event Bus Management

**What:** Route messages between services

**How:**

```
Service A wants to send message to Service B:
  ↓
Message → opena1 Event Bus
  ↓
opena1 routes to: opena2 (Archive) for logging
  ↓
opena1 broadcasts event to interested subscribers
  ↓
All listeners receive event via SSE (Server-Sent Events)
```

---

### 4. Registry Persistence

**What:** Save agent registry to disk

**How:**

```
File: agent_registry.json

Format:
{
  "agents": {
    "opena_finance": {
      "port": 12347,
      "endpoint": "http://127.0.0.1:12347",
      "status": "healthy",
      "registered_at": "2025-11-08T17:28:00Z",
      "last_check": "2025-11-08T19:00:00Z"
    },
    ...
  },
  "last_update": "2025-11-08T19:00:00Z"
}
```

**Durability:**

- Auto-saved on every registry change
- Read on startup (recover from last session)
- Append-only: Never overwrite, only update

---

### 5. Failover Handling

**Scenario 1: Agent Dies Unexpectedly**

```
opena1 polling detects:
  - 3 consecutive health check timeouts
  ↓
opena1 marks agent as "unhealthy"
  ↓
opena1 broadcasts: event_agent_unhealthy
  ↓
opena19 (Dashboard) shows: ⚠️ Agent Unavailable
  ↓
opena2 (Archive) logs: ERROR_opena_finance_TIMEOUT
  ↓
opena1 retries every 10s until recovery
```

**Scenario 2: Agent Recovers**

```
opena1 polling detects:
  - Health check succeeds after being down
  ↓
opena1 marks agent as "healthy"
  ↓
opena1 broadcasts: event_agent_recovered
  ↓
opena19 shows: ✅ Agent Operational
  ↓
opena2 logs: RECOVERED_opena_finance_OK
```

---

## 🔌 Input Sources

| Source              | Type                     | Example                |
| ------------------- | ------------------------ | ---------------------- |
| opena19 (Dashboard) | POST /api/agent/register | New agent registration |
| opena2 (Archive)    | Query /archiv/last       | Status queries         |
| External            | Manual registration      | CLI or API call        |
| Internal (opena1)   | Self-check               | 5s health polling      |

---

## 📤 Output Targets

| Target              | Type          | Message                                 |
| ------------------- | ------------- | --------------------------------------- |
| All Services        | Health Status | "Coordinator ready, registry available" |
| opena2 (Archive)    | Event Logs    | "agent_registered", "agent_unhealthy"   |
| opena19 (Dashboard) | Agent Status  | Registry state, health matrix           |
| SSE Bus             | Events        | Real-time updates to subscribers        |

---

## 🔗 Key Endpoints

### 1. Health Check

```
GET /health
Response: {"status": "healthy", "service": "opena1", "port": 12344}
```

### 2. Agent Registry Query

```
GET /agent/registry
Response: {"agents": {...}, "last_update": "..."}
```

### 3. Agent Status

```
GET /agent/status
Response: List of all agents with status
```

### 4. Register Agent

```
POST /agent/register
Payload: {"service": "...", "port": ..., "endpoint": "..."}
Response: {"registered": true, "agent_id": "..."}
```

### 5. Unregister Agent

```
POST /agent/unregister
Payload: {"service": "..."}
Response: {"unregistered": true}
```

### 6. Health Report

```
GET /health/report
Response: {"healthy_agents": 5, "unhealthy_agents": 0, "timestamp": "..."}
```

---

## ⚙️ Error Handling

### Error 1: Agent Not Responding

```
Detection: 3 consecutive timeout failures
Action: Mark as "unhealthy", log error
Recovery: Retry every 10s until response
Timeout: 5 seconds per health check
```

### Error 2: Archive Write Failure

```
Detection: POST /store/archivp fails
Action: Log locally, mark opena2 as "degraded"
Retry: 3x with exponential backoff
Fallback: Continue coordinator operations (don't cascade)
```

### Error 3: Port Conflict

```
Detection: Startup fails (port in use)
Action: Log error, refuse to start
Solution: Check "lsof -i :12344", kill conflicting process
```

---

## 📊 Nov 8 System Integration

**Agents Currently Monitored by opena1:**

| Agent           | Port  | Status (Nov 8)         | Registered | Last Check |
| --------------- | ----- | ---------------------- | ---------- | ---------- |
| opena1 (self)   | 12344 | ✅ Healthy             | N/A        | Continuous |
| opena2          | 12345 | ✅ Healthy             | 12:00 UTC  | 19:00 UTC  |
| kordp           | 12346 | ✅ Healthy             | 12:00 UTC  | 19:00 UTC  |
| opena_finance   | 12347 | ✅ Healthy             | 17:28 UTC  | 19:00 UTC  |
| opena4_telegram | 12348 | ✅ Healthy             | 18:09 UTC  | 19:00 UTC  |
| opena19         | 12349 | ⏳ Registering (Nov 9) | N/A        | TBD        |

---

## 🚀 opena1 Self-Check (Nov 8, 19:00 UTC)

**Question:** "What is my current state?"

**Answer:**

```
Service: opena1 (Coordinator)
Port: 12344
Status: Healthy
Uptime: 7+ hours (since Nov 8, 12:00)

Connected Services: 5
  ├─ opena2 (Archivator) – HEALTHY
  ├─ opena_finance (DB) – HEALTHY
  ├─ opena4_telegram (Bridge) – HEALTHY
  ├─ kordp (Relay) – HEALTHY
  └─ opena19 (Dashboard) – PENDING (Nov 9)

Events Processed: 50+
Registry Entries: 5
Archive Logs: 15+ (via opena2)

Last Event: opena4_telegram → opena2 MESSAGE (18:11 UTC)
Last Registry Update: 18:09 UTC (opena4_telegram registered)

Performance:
  - Health checks: 100% success rate
  - Response time: <10ms avg
  - Memory: ~75MB
  - CPU: <1% (idle)

Issues: None detected ✅
```

---

## 🔗 Related Modules

- **Modul 1 (Telegram):** `KB_TELEGRAM_BRIDGE_2025-11-08.md`
- **Modul 2 (Dashboard):** `KB_DASHBOARD_INTEGRATION_2025-11-08.md`
- **Modul 3 (Archive):** `KB_ARCHIVE_PATTERNS_2025-11-08.md`
- **Modul 5 (Integration):** `KB_SYSTEM_INTEGRATION_FLOWS_2025-11-08.md`
- **Index:** `KB_INDEX_CURRENT_2025-11-08.md`

---

**Status:** 🟢 OPERATIONAL
**Version:** 1.0
**Last Self-Check:** Nov 8, 19:00 UTC
