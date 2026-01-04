# ELION HYPER-DASHBOARD: ARCHITECTURE OVERVIEW

## 📐 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER / CLIENT (F12)                       │
│                    WebSocket + SSE Stream                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│            DASHBOARD (Main REST API) – Port 12349               │
│  FastAPI + Uvicorn  |  Authorization Bearer Token Validation   │
└────────────────────────┬────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
     PHASE 1          PHASE 4          PHASE 5
    (Core)           (Marketing)      (Enterprise)
        │                │                │
┌───────┴──────┐   ┌─────┴──────┐  ┌────┴──────┐
│              │   │            │  │           │
Phase 1        Phase 2   Phase 3   │  Phase 4   │  Phase 5
├─────────┐    ├──────┐   ├──────┐ │ ├───────┐ │ ├────────┐
│ opena1  │    │ope4  │   │ope7  │ │ │ope11  │ │ │ope16   │ CRM
│:12344   │    │:12347│   │:12350│ │ │:12359 │ │ │:12364  │
│Coord.   │    │Telegram│  │WhatsApp│ │Social │ │ │        │
└─────────┘    └──────┘   └──────┘ │ │:12359 │ │ ├────────┐
│              │            │  │ Media │ │ope17   │
│ opena2  │    │ope5  │   │ope8  │ │ │        │ │:12365  │ Analytics
│:12345   │    │:12346│   │:12351│ │ │├───────┐ │ │        │
│Archivator│   │Browser│  │Teleph.│ │ │ope12  │ │ ├────────┐
└─────────┘    └──────┘   └──────┘ │ │:12360 │ │ │ope18   │ Dashboard
│              │            │  │Influencer│ │:12366 │
│ kordp   │    │ope6  │   │ope9  │ │ │        │ │ (SSE)
│:12346   │    │:12349│   │:12352│ │ │├───────┐ │ ├────────┐
│Scheduler│   │Email  │  │TelCall│ │ │ope13  │ │ │ope19   │ Workflow
└─────────┘    └──────┘   └──────┘ │ │:12361 │ │ │:12367  │ Orchestration
│              │            │  │Calendar │ │        │
└────────────────────────┘ │ │        │ │ └────────┘
                        │ │├───────┐ │
                        │ │ope14  │ │
                        │ │:12362 │ │
                        │ │HTML   │ │
                        │ │       │ │
                        │ │├───────┐ │
                        │ │ope15  │ │
                        │ │:12363 │ │
                        │ │Shop   │ │
                        │ │       │ │
                        └─┴───────┘ │
```

---

## 🔄 Data Flow Architecture

### 1. Request Flow (Client → Dashboard → Agent)

```
┌─────────────┐
│   CLIENT    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP + Bearer Token
       ↓
┌──────────────────────────┐
│ DASHBOARD (12349)        │
│ Endpoint: /api/...       │
├──────────────────────────┤
│ 1. Validate token        │
│ 2. Parse request         │
│ 3. Call agent endpoint   │
│ 4. Wait for response     │
│ 5. Archive operation     │
│ 6. Return to client      │
└──────┬───────────────────┘
       │ HTTP 127.0.0.1:12XXX
       ↓
┌──────────────────────────┐
│    AGENT (12364+)        │
│ Example: opena16 (CRM)   │
├──────────────────────────┤
│ 1. Validate token        │
│ 2. Process business logic│
│ 3. Update in-memory DB   │
│ 4. Call archive endpoint │
│ 5. Return result         │
└──────┬───────────────────┘
       │ HTTP 127.0.0.1:12345
       ↓
┌──────────────────────────┐
│    ARCHIVATOR (12345)    │
│ opena2                   │
├──────────────────────────┤
│ 1. Receive operation log │
│ 2. Write to disk         │
│ 3. Confirm write         │
└──────────────────────────┘
```

### 2. Agent-to-Agent Communication (via Workflow)

```
┌────────────────────────┐
│  WORKFLOW AGENT (19)   │
│  Port 12367            │
├────────────────────────┤
│ Step 1: call_agent:crm │
│         ↓              │
│      CRM (16)          │ → Create customer
│      12364             │
│         ↓              │
│ Step 2: send_email     │ → Send confirmation
│         ↓              │
│ Step 3: call_agent:    │ → Generate report
│         analytics (17) │
│      12365             │
│         ↓              │
│ Step 4: call_agent:    │ → Update dashboard
│         dashboard (18) │
│      12366             │
│         ↓              │
│ Workflow complete ✅   │
└────────────────────────┘
```

### 3. Real-time SSE Flow (Dashboard Agent)

```
┌──────────────┐
│   BROWSER    │
│ EventSource  │
│ /data/stream │
└──────┬───────┘
       │ GET with Bearer Token
       │ Keep-Alive: HTTP/1.1
       ↓
┌──────────────────────────────┐
│  DASHBOARD AGENT (18)        │
│  Port 12366                  │
├──────────────────────────────┤
│ Active SSE subscribers: 3    │
│                              │
│ Event Queue:                 │
│  - widget_created            │
│  - widget_updated            │
│  - layout_saved              │
│  - refresh_realtime          │
└──────┬───────────────────────┘
       │ data: JSON\n\n
       │ (streaming)
       ↓
┌──────────────────────────────┐
│   Browser Console (F12)       │
│ client.onmessage = (event) => │
│   console.log(event.data)     │
└──────────────────────────────┘
```

---

## 📦 Data Model Architecture

### Entity Relationships

```
┌─────────────────┐
│    CUSTOMER     │
│  (CRM: 16)      │
├─────────────────┤
│ - customer_id   │───────┐
│ - name          │       │
│ - email         │       │ 1:N
│ - lifecycle_    │       │
│   stage         │       │
│ - created_at    │       │
└─────────────────┘       │
       │                  │
       │ 1:N              ↓
       ├─────────→ ┌─────────────────┐
       │           │   INTERACTION    │
       │           │ (CRM: 16)        │
       │           ├─────────────────┤
       │           │ - type (email,  │
       │           │   call, etc)    │
       │           │ - outcome       │
       │           │ - notes         │
       │           │ - timestamp     │
       │           └─────────────────┘
       │
       │ 1:N
       └─────────→ ┌─────────────────┐
                   │     DEAL        │
                   │  (CRM: 16)      │
                   ├─────────────────┤
                   │ - deal_id       │
                   │ - customer_id   │ (FK)
                   │ - title         │
                   │ - amount        │
                   │ - stage         │
                   │ - close_date    │
                   └─────────────────┘
```

### Metric Aggregation (Analytics: 17)

```
┌──────────────────────┐
│   AGENTS (1-15)      │
│   Operations         │
├──────────────────────┤
│ - Customer created   │
│ - Email sent         │
│ - Post published     │
│ - Event booked       │
│ - Product sold       │
└──────┬───────────────┘
       │
       │ Simulate metrics aggregation
       ↓
┌──────────────────────────────┐
│   ANALYTICS CACHE (17)       │
├──────────────────────────────┤
│ Metrics:                     │
│  - revenue: {current, prev}  │
│  - active_users: {...}       │
│  - conversions: {...}        │
│  - deals_pipeline: {...}     │
│  - customer_satisfaction: ...│
│  - email_sent: {...}         │
│  - social_posts: {...}       │
└──────┬───────────────────────┘
       │
       │ Calculate trends
       ↓
┌──────────────────────────────┐
│   TREND ANALYSIS (17)        │
├──────────────────────────────┤
│ For each metric:             │
│  - trend: up/down/stable     │
│  - change_%: ±X.XX%          │
│  - historical_values: [...]  │
│  - min/max/mean/stdev        │
└──────────────────────────────┘
```

---

## 🔐 Security Architecture

### Token Validation Pipeline

```
┌──────────────────────┐
│   HTTP REQUEST       │
│ GET /customer/123    │
│ Authorization: Bearer │
│ MEIN_SUPER_TOKEN_123 │
└──────┬───────────────┘
       │
       ↓
┌──────────────────────┐
│ DASHBOARD (12349)    │
│ Parse header:        │
│  → Extract token     │
│  → Compare with .env │
│  → Valid? Continue   │
│  → Invalid? → 403    │
└──────┬───────────────┘
       │
       ↓ (if valid)
┌──────────────────────┐
│    AGENT (12364)     │
│ Receive with header: │
│  → Extract token     │
│  → Compare with      │
│    TOKEN constant    │
│  → Valid? Process    │
│  → Invalid? → 403    │
└──────┬───────────────┘
       │
       ↓ (if valid)
┌──────────────────────┐
│  ARCHIVATOR (12345)  │
│ (no token needed)    │
│ Called only by agents│
│ (internal network)   │
└──────────────────────┘
```

---

## 🗂️ Storage Architecture

### Archive Directory Structure

```
archiv/
├── 2025/
│   └── 11/
│       └── 09/
│           ├── SP1730881234_opena16_crm→opena2_CUSTOMER_CREATE.json
│           │   {
│           │     "customer_id": "CUST_ABC123",
│           │     "name": "Acme Corp",
│           │     "ts": "2025-11-09T12:34:56Z"
│           │   }
│           │
│           ├── SP1730881235_opena16_crm→opena2_DEAL_CREATE.json
│           │   {
│           │     "deal_id": "DEAL_XYZ789",
│           │     "customer_id": "CUST_ABC123",
│           │     "amount": 50000.00,
│           │     "ts": "2025-11-09T12:34:57Z"
│           │   }
│           │
│           ├── SP1730881236_opena17_analytics→opena2_REPORT_GENERATED.json
│           │   {
│           │     "report_id": "RPT_ABC123",
│           │     "metrics_count": 7,
│           │     "ts": "2025-11-09T12:34:58Z"
│           │   }
│           │
│           └── SP1730881237_opena19_workflow→opena2_WORKFLOW_EXECUTED.json
│               {
│                 "workflow_id": "WFW_ABC123",
│                 "execution_id": "EXE_XYZ789",
│                 "status": "completed",
│                 "steps_executed": 4,
│                 "ts": "2025-11-09T12:35:00Z"
│               }
│
└── [more dates...]
```

---

## 🔗 Integration Points

### Phase 5 Inter-Agent Communication Matrix

```
        │ opena16 │ opena17 │ opena18 │ opena19
────────┼─────────┼─────────┼─────────┼─────────
opena16 │  self   │  report │ widget  │  exec
CRM     │ ✅      │ read    │ update  │ ↓
        │         │ metrics │ layout  │ context
────────┼─────────┼─────────┼─────────┼─────────
opena17 │ metrics │  self   │ stream  │  exec
Analyt. │ from    │ ✅      │ data    │ ↓
        │ archive │         │ stream  │ report
────────┼─────────┼─────────┼─────────┼─────────
opena18 │ request │ request │  self   │  exec
Dashbrd │ data    │ data    │ ✅      │ ↓
        │ update  │ update  │         │ refresh
────────┼─────────┼─────────┼─────────┼─────────
opena19 │ CALL    │ CALL    │ CALL    │  self
Workflow│ CRM     │ Analyt. │ Dashbrd │ ✅
        │ /exec   │ /exec   │ /exec   │ orch.
```

---

## 📊 Port Allocation

```
12344 ─┬─ opena1 (Coordinator)
       │
12345 ─┼─ opena2 (Archivator)
       │
12346 ─┼─ kordp (Scheduler)
       │
12347 ─┼─ opena4 (Telegram)
       │
12346 ─┼─ opena5 (Browser)
       │
12349 ─┼─ opena6 (Email)
       │
12350 ─┼─ opena7 (WhatsApp)
       │
12351 ─┼─ opena8 (Telephone)
       │
12352 ─┼─ opena9 (TelephoneCall)
       │
12353 ─┼─ opena10 (Unlock)
       │
12359 ─┼─ opena11 (Social Media)
       │
12360 ─┼─ opena12 (Influencer)
       │
12361 ─┼─ opena13 (Calendar)
       │
12362 ─┼─ opena14 (HTML)
       │
12363 ─┼─ opena15 (Shop)
       │
12364 ─┼─ opena16 (CRM) ← Phase 5
       │
12365 ─┼─ opena17 (Analytics) ← Phase 5
       │
12366 ─┼─ opena18 (Dashboard) ← Phase 5
       │
12367 ─┴─ opena19 (Workflow) ← Phase 5
```

---

## ✅ Architecture Compliance

- ✅ RESTful API design
- ✅ FastAPI + Uvicorn framework
- ✅ Async/Await throughout
- ✅ Bearer Token authentication
- ✅ Archive-centric logging
- ✅ Inter-agent HTTP communication
- ✅ Event streaming (SSE)
- ✅ Workflow orchestration
- ✅ Pydantic validation
- ✅ Error handling (5 HTTP status codes)

---

**Last Updated:** 9. November 2025
**Architecture Version:** Phase 5 Complete
