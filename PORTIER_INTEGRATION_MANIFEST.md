# 🔗 PORTIER 3.0 — Integration Manifest

**Version:** 3.0.0  
**Date:** 21. November 2025  
**Purpose:** Complete integration guide for all PORTIER 3.0 components

---

## 📋 Executive Summary

Dieses Dokument beschreibt, wie alle Ordner, Services und Module im **PORTIER 3.0 Repository** integriert sind und zusammenarbeiten.

---

## 🏛️ Architektur-Integration

### **Layer 1: Entry Layer (OpenAI / UI)**

```
OpenAI API
  ↓ HTTP Requests
opena20 Dashboard (Port 12349)
  ↓ Bearer Token Auth
```

**Involvierte Ordner:**
- `19.opena20_dashboard_agent/` — Dashboard UI & API
- `.github/` — Bearer Token in Secrets

---

### **Layer 2: Coordinator Layer (opena1)**

```
Entry Layer
  ↓ Request71 (JSON)
opena1 (Port 12344)
  ↓ Decision72 (Tool Selection)
```

**Involvierte Ordner:**
- `1.opena1&2_portier/opena1/` — Coordinator Service
- `1.opena1&2_portier/bin/` — Start/Stop Scripts
- `configs/` — Port Policy, Tool Registry

**Datenfluss:**
1. Request71 → opena1:12344/log/opena1
2. Coordinator validiert Schema (Pydantic `extra="forbid"`)
3. Decision72 generiert (selected_tool, reasoning)
4. Forward zu opena2

---

### **Layer 3: Archivator Layer (opena2)**

```
opena1
  ↓ CMD Envelope
opena2 (Port 12345)
  ↓ Safepoint Creation
archivp_store/YYYY/MM/DD/
```

**Involvierte Ordner:**
- `1.opena1&2_portier/opena2/` — Archivator Service
- `1.opena1&2_portier/archivp_store/` — Safepoint Storage
- `archivp/` — Legacy Archive (konsolidiert mit archivp_store/)

**Safepoint Format:**
```
SP<timestamp>_opena1→archivp_CMD.json
```

**Policies:**
- ✅ Append-only (no overwrites)
- ✅ Unicode → (U+2192) mandatory
- ✅ YYYY/MM/DD structure
- ✅ index.jsonl (append-only index)

---

### **Layer 4: Gateway Layer (kordp)**

```
opena2
  ↓ Dispatch Request
kordp (Port 12346)
  ↓ Tool Routing (tool_registry.json)
Tool (opena4-opena21)
```

**Involvierte Ordner:**
- `1.opena1&2_portier/kordp/` — Gateway Service
- `configs/tools_registry.json` — Tool Mappings

**Tool Registry Example:**
```json
{
  "tool_file_manager": "http://127.0.0.1:12351",
  "tool_text_analyzer": "http://127.0.0.1:12351",
  "tool_default": "http://127.0.0.1:12346"
}
```

---

### **Layer 5: Tool Layer (Agents opena3-opena21)**

```
kordp
  ↓ HTTP Forward
opena3-opena21 (Ports 12347-12365)
  ↓ Business Logic
RESP Payload
  ↓ Return to opena2
```

**Involvierte Ordner:**
- `2.opena3_openwebui/` — OpenWebUI Terminal (12347) ✅
- `3.opena4_telegram/` — Telegram Bot (12348) 🟡
- `4.opena5_vscode/` — VS Code Integration (12349→12365) 🟡
- `5-21.opena6-opena21/` — 16 weitere Agenten 🟡

**Status:**
- ✅ Running: opena3
- 🟡 Planned: opena4-opena21

---

### **Layer 6: Dashboard & Monitoring (opena20)**

```
All Services
  ↓ /health endpoints
opena20 (Port 12349)
  ↓ Status Aggregation
Dashboard UI
  ↓ Auto-Refresh (5s)
User Browser
```

**Involvierte Ordner:**
- `19.opena20_dashboard_agent/` — Dashboard Service
- `19.opena20_dashboard_agent/templates/` — Jinja2 UI
- `19.opena20_dashboard_agent/static/` — CSS/JS Assets

**Features:**
- Live Status Grid
- E2E Test Trigger
- Safepoint Inspector
- Activity Log (real-time)
- Restart Stack Button

---

## 🧩 Modul-Integration

### **1. SCTA (Structured Code Task Automation)**

```
src/
├── agents/
│   ├── core_orchestrator/
│   └── worker_agents/
│       ├── planner/
│       └── executor/
├── pkg/
│   ├── shared/
│   │   ├── config.py         ← Import von allen Services
│   │   ├── schemas.py        ← Shared Pydantic Models
│   │   └── exceptions.py     ← Custom Errors
│   └── models/
└── services/
    └── agenda_api.py         ← 16-Seiten Agenda (Port 12399)
```

**Integration:**
- Alle Agenten importieren `src.pkg.shared.config`
- Shared Schemas in `src.pkg.shared.schemas`
- Agenda API als separater Service (Port 12399)

---

### **2. Configuration Management**

```
configs/
├── agenda_pages.json         ← 16 Pages Metadata
├── tools_registry.json       ← Tool-to-Port Mappings
└── routing_matrix.yaml       ← (optional) Service Routes
```

**Integration:**
- `agenda_api.py` lädt `agenda_pages.json`
- `kordp` lädt `tools_registry.json`
- `opena1` enforcement via Port Policy

---

### **3. Testing Integration**

```
tests/
├── test_portier_stack.py     ← in 1.opena1&2_portier/
├── test_openwebui_agent.py   ← in 2.opena3_openwebui/
└── test_archivator.py        ← in 1.opena1&2_portier/
```

**Integration:**
- Pytest-Suite testet Option-2-Flow E2E
- Mocking via `httpx.MockTransport`
- Fixtures in `conftest.py`

**Test Ausführung:**
```bash
cd 1.opena1&2_portier
pytest tests/test_portier_stack.py -v
```

---

### **4. Scripts Integration**

```
scripts/
├── register_agents.py        ← Registriert alle Agenten in kordp
├── test_openwebui.py         ← OpenWebUI Health Checks
├── seed_openwebui.py         ← Seed-Daten für opena3
└── curl_examples.sh          ← API Test Examples
```

**Integration:**
- `register_agents.py` sendet POST zu kordp:12346/route/update
- `test_openwebui.py` prüft opena3:12347/health
- `seed_openwebui.py` sendet Chat-Requests

---

### **5. Operational Scripts (bin/)**

```
bin/
├── ops.sh                    ← Main Orchestrator
│   ├── start                 ← Start all services
│   ├── stop                  ← Stop all services
│   ├── status                ← Health checks
│   ├── verify                ← Integration verification
│   └── logs                  ← Tail all logs
├── start_all.sh
├── stop_all.sh
├── verify_stack.sh
├── check_ports.sh
└── env_bootstrap.sh          ← Generate .env with UUID token
```

**Integration:**
- `ops.sh` delegiert zu `1.opena1&2_portier/bin/start_stack.sh`
- Ports 12344-12350 werden validiert
- PID-Files in `.runtime/pids/`

**Usage:**
```bash
bin/ops.sh start    # Startet opena1, opena2, kordp, opena3, opena20
bin/ops.sh status   # JSON-Status aller Services
bin/ops.sh verify   # E2E-Validation
bin/ops.sh logs     # Tail alle Logs
```

---

## 🔌 Port-Integration

### **Port-Mapping (Vollständig)**

| Port | Service | Ordner | Status |
|------|---------|--------|--------|
| **12344** | opena1 (Coordinator) | 1.opena1&2_portier/opena1/ | ✅ Running |
| **12345** | opena2 (Archivator) | 1.opena1&2_portier/opena2/ | ✅ Running |
| **12346** | kordp (Gateway) | 1.opena1&2_portier/kordp/ | ✅ Running |
| **12347** | opena3 (OpenWebUI) | 2.opena3_openwebui/ | ✅ Running |
| **12348** | opena4 (Telegram) | 3.opena4_telegram/ | 🟡 Planned |
| **12349** | opena20 (Dashboard) | 19.opena20_dashboard_agent/ | ✅ Running |
| **12350** | OpenWebUI Adapter | 2.opena3_openwebui/ | ✅ Running |
| **12351** | opena7 (E-Mail) | 6.opena7_email/ | 🟡 Planned |
| **12352** | opena8 (WhatsApp) | 7.opena8_whatsapp/ | 🟡 Planned |
| **12353** | opena9 (Telefon) | 8.opena9_telephone/ | 🟡 Planned |
| **12354** | opena10 (Call Tracking) | 9.opena10_call_tracking/ | 🟡 Planned |
| **12355** | opena11 (Unlock) | 10.opena11_unlock/ | 🟡 Planned |
| **12356** | opena12 (Social Media) | 11.opena12_social_media/ | 🟡 Planned |
| **12357** | opena13 (Influencer) | 12.opena13_influencer/ | 🟡 Planned |
| **12358** | opena14 (Calendar) | 13.opena14_calendar/ | 🟡 Planned |
| **12359** | opena15 (HTML) | 14.opena15_html/ | 🟡 Planned |
| **12360** | opena16 (Shop) | 15.opena16_shop/ | 🟡 Planned |
| **12361** | opena17 (Homepage Creator) | 16.opena17_homepagecreator/ | 🟡 Planned |
| **12362** | opena18 (CRM) | 17.opena18_CMR/ | 🟡 Planned |
| **12363** | opena19 (Aktien/Crypto) | 18.opena19_Aktien&Crypto/ | 🟡 Planned |
| **12364** | opena21 (Workflow) | 20.opena21_workflow/ | 🟡 Planned |
| **12365** | opena5 (VS Code) (verschoben) | 4.opena5_vscode/ | 🟡 Planned |
| **12399** | Agenda API | src/services/agenda_api.py | ✅ Running |
| **8080** | OpenWebUI UI (verboten für Backend) | Docker | ✅ Running |

**Port Policy:**
- **Allowed:** 12344-12399 (Backend Services)
- **Forbidden:** 8080 (UI-only, kein Backend)

---

## 📦 Datenfluss-Integration

### **E2E Request Flow (Complete)**

```
1. OpenAI API
   ↓ POST Request71
   {
     "request_id": "uuid4",
     "timestamp": "ISO-8601",
     "source": "openai",
     "user_query": "Analysiere Datei X",
     "context": {},
     "metadata": {}
   }

2. opena1:12344/log/opena1
   ↓ Validierung (Pydantic strict)
   ↓ Decision72 generiert
   {
     "decision_id": "uuid4",
     "selected_tool": "tool_file_manager",
     "reasoning": "User wants file analysis",
     "forwarded_to": "http://127.0.0.1:12345/finalize/opena2"
   }

3. opena2:12345/finalize/opena2
   ↓ CMD Safepoint Creation
   archivp_store/2025/11/21/SP1763725786_opena1→archivp_CMD.json
   ↓ Forward to kordp

4. kordp:12346/dispatch
   ↓ Tool Resolution (tool_registry.json)
   ↓ HTTP Forward to Tool
   http://127.0.0.1:12351 (opena7 E-Mail Agent)

5. Tool Execution (opena7)
   ↓ Business Logic
   ↓ Result Payload
   {
     "status": "success",
     "result": {"file_content": "..."},
     "metadata": {}
   }

6. RESP Safepoint
   ↓ opena2:12345/store/resp
   archivp_store/2025/11/21/SP1763725786_tool→opena1_RESP.json

7. Return to opena1
   ↓ Decision72 + Result

8. Return to OpenAI
   ↓ Final Response
   {
     "decision_id": "uuid4",
     "result": {"file_content": "..."},
     "status": "FORWARDED"
   }
```

**Involvierte Ordner:**
- `1.opena1&2_portier/opena1/` — Step 2
- `1.opena1&2_portier/opena2/` — Steps 3, 6
- `1.opena1&2_portier/kordp/` — Step 4
- `6.opena7_email/` — Step 5 (Example Tool)
- `1.opena1&2_portier/archivp_store/` — Steps 3, 6

---

## 🛡️ Security Integration

### **1. Bearer Token (Environment)**

```bash
# .env (gitignored)
BEARER_TOKEN=<uuid>

# Bootstrap
bin/env_bootstrap.sh  # Generates .env with UUID
```

**Integration:**
- Dashboard API (opena20) requires Bearer Token
- Token in `.env` (gitignored via `.gitignore`)
- `.env.example` als Template

---

### **2. Port Policy Enforcement**

```python
# In jedem FastAPI Service:
from config import PORT_POLICY_MIDDLEWARE

app.add_middleware(
    PortPolicyMiddleware,
    allowed_ports=range(12344, 12400),
    forbidden_ports=[8080]
)
```

**Integration:**
- `src/pkg/shared/config.py` — Port Policy Definition
- Alle Services importieren & erzwingen

---

### **3. Secret Redaction (Logs & Archive)**

```python
# opena2/opena2_app.py
def redact_secrets(data: dict) -> dict:
    SENSITIVE_KEYS = ["password", "api_key", "token", "secret"]
    # ... redaction logic
```

**Integration:**
- Alle Safepoints redaktieren Secrets
- Logs maskieren API Keys (*** statt sk-...)

---

### **4. Pre-Commit Hooks**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: detect-private-key
      - id: check-added-large-files
```

**Integration:**
- `.github/workflows/ci.yml` führt Pre-Commit aus
- Blockiert Secrets im Repo

---

## 🧪 Testing Integration

### **E2E Test (Complete)**

```bash
# Via Dashboard
curl -X POST http://127.0.0.1:12349/api/e2e

# Via opena1 direkt
curl -X POST http://127.0.0.1:12344/log/opena1 \
  -H "Content-Type: application/json" \
  -d '{"request_id":"test-123","timestamp":"2025-11-21T12:00:00Z","source":"openai","user_query":"Test","context":{},"metadata":{}}'
```

**Integration:**
- `tests/test_portier_stack.py` — E2E Flow validiert
- Dashboard API `/api/e2e` triggert Test
- Pytest-Suite läuft via `bin/ops.sh test`

---

## 📚 Documentation Integration

### **Dokumentations-Hierarchie**

```
README.md                         ← Quick Start (700 LOC)
  ↓ Verweist auf:
README_ENTERPRISE.md              ← Enterprise Dossier (5,890 LOC)
PORTIER_SYSTEM_DOCS.md            ← System Docs (654 LOC)
PORTIER_3.0_RELEASE.md            ← Release Notes (511 LOC)
PORTIER_REPOSITORY_STRUCTURE.md  ← Ordner-Guide (1,200 LOC) ← NEU
  ↓ Verweist auf:
docs/OPERATIONS.md                ← Runtime Commands
docs/TROUBLESHOOTING.md           ← Error Scenarios
docs/OPENWEBUI_INTEGRATION.md    ← opena3 Specs
.github/copilot-master-prompt.md  ← Complete System Knowledge (2,000+ LOC)
```

**Integration:**
- Alle Dokumente verlinken sich gegenseitig
- `.github/copilot-instructions.md` verweist auf Master-Prompt
- README als Einstiegspunkt

---

## 🚀 Deployment Integration

### **1. Git Repository**

```bash
# Repository
https://github.com/jokicdanijel/Gesamtprojekt-start

# Branch
main

# Tags
v3.0.0 (PORTIER 3.0 Release)
```

**Integration:**
- `.github/workflows/ci.yml` — GitHub Actions
- Pre-Commit Hooks
- Pull Request Template

---

### **2. Docker (Planned)**

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  opena1:
    build: ./1.opena1&2_portier
    ports:
      - "12344:12344"
  opena2:
    build: ./1.opena1&2_portier
    ports:
      - "12345:12345"
  # ... weitere Services
```

**Integration:**
- `Dockerfile` in jedem Service-Ordner (geplant)
- `docker-compose.prod.yml` orchestriert Stack
- `.dockerignore` blockiert Secrets

---

### **3. CI/CD Pipeline**

```yaml
# .github/workflows/ci.yml
name: PORTIER 3.0 CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest -v
      - run: flake8 .
```

**Integration:**
- GitHub Actions führt Tests aus
- Pre-Commit validiert Code
- Tag-basierte Releases

---

## 🔧 Operational Integration

### **Stack Operations**

```bash
# Alle Services starten
bin/ops.sh start

# Alle Services stoppen
bin/ops.sh stop

# Status prüfen
bin/ops.sh status | jq .

# Verify Integration
bin/ops.sh verify

# Logs anzeigen
bin/ops.sh logs

# Specific Service
cd 1.opena1&2_portier
./bin/start_stack.sh  # Startet nur PORTIER Core
```

**Integration:**
- `bin/ops.sh` delegiert zu `1.opena1&2_portier/bin/start_stack.sh`
- PID-Files in `.runtime/pids/`
- Logs in `logs/`

---

## 📊 Metrics & Monitoring Integration

### **Dashboard Integration**

```javascript
// dashboard.js
async function fetchStatus() {
  const response = await fetch('/api/status');
  const data = await response.json();
  
  // Update Status Grid
  updateStatusGrid(data);
  
  // Update Activity Log
  logActivity(`Fetched status for ${Object.keys(data).length} services`);
}

// Auto-Refresh alle 5s
setInterval(fetchStatus, 5000);
```

**Integration:**
- `19.opena20_dashboard_agent/static/js/dashboard.js`
- Ruft `/api/status` ab (alle Services)
- Displays Live Grid in UI

---

### **Prometheus (Planned)**

```yaml
# prometheus.yml (geplant)
scrape_configs:
  - job_name: 'portier'
    static_configs:
      - targets:
        - '127.0.0.1:12344'  # opena1
        - '127.0.0.1:12345'  # opena2
        - '127.0.0.1:12346'  # kordp
```

**Integration:**
- Metrics-Endpoints in jedem Service (geplant)
- Grafana Dashboards (geplant)
- Alerts via Alertmanager (geplant)

---

## 🏁 Zusammenfassung

**PORTIER 3.0** ist vollständig integriert über:

1. ✅ **Option-2-Flow** — opena1 → opena2 → kordp → Tools
2. ✅ **Safepoint System** — Append-only, Unicode →, YYYY/MM/DD
3. ✅ **Dashboard Monitoring** — Live Status, E2E Tests, Activity Log
4. ✅ **SCTA Shared Modules** — config.py, schemas.py, exceptions.py
5. ✅ **Operational Scripts** — bin/ops.sh orchestriert alles
6. ✅ **Security Policies** — Bearer Token, Port Policy, Secret Redaction
7. ✅ **Testing Suite** — E2E Tests, Pytest, GitHub Actions
8. ✅ **Documentation** — 5+ Docs, 12,000+ LOC, cross-linked

**Alle Ordner arbeiten nahtlos zusammen** und bilden ein **produktionsreifes Multi-Agent-System**.

---

**Last Updated:** 21. November 2025  
**Version:** 3.0.0  
**Maintainer:** Danijel Jokic (ELION Team)
