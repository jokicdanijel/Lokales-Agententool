# 📘 PORTIER 3.0 — Full System Documentation

**Coordinated AI Routing • Safepoint Archivator • Gateway Dispatch • Realtime Dashboard**

---

## 🧩 Überblick

PORTIER 3.0 ist eine vollständig modulare, produktionsreife Multi-Service-Architektur, die entwickelt wurde, um KI-Anfragen sicher, nachvollziehbar und skalierbar zu verarbeiten.

Es besteht aus **vier Kernservices**:

| Service | Port | Funktion |
|---------|------|----------|
| **opena1** | 12344 | Coordinator — verarbeitet Request71 und erzeugt Decision72 |
| **opena2** | 12345 | Archivator — persistiert CMD/RESP Safepoints inkl. Unicode-Pfeil → |
| **kordp** | 12346 | Gateway — Dispatch-Router zur Tool-Ausführung |
| **opena20** | 12349 | Dashboard — UI für Monitoring, Status, E2E-Trigger und Safepoints |

---

## 🔄 Option-2-Flow Architektur

Die Architektur folgt dem offiziellen **Option-2-Flow**:

```
OpenAI → opena1:12344 → opena2:12345 → kordp:12346 → Tools
         ↓ Request71    ↓ CMD safepoint  ↓ Dispatch
         ↓ Decision72   ↓ RESP safepoint ↓ Result
         ↓              ↓                 ↓
         OpenAI ←───────┴─────────────────┘
                         ↘
                    opena20:12349 (Dashboard)
```

**SYSTEMSTATUS:**

- ✅ Stabil
- ✅ E2E-Durchläufe erfolgreich
- ✅ Dashboard voll funktionsfähig
- ✅ Safepoints werden korrekt gespeichert
- ✅ Keine offenen Fehler

---

## 🏗️ ARCHITEKTUR

### 🔹 1. opena1 — Coordinator (Port 12344)

**Verantwortlichkeiten:**

- Validiert Requests (Schema Request71)
- Entscheidet Tool (Decision72)
- Erzeugt CMD-Envelope und leitet an opena2 weiter
- Port-Policy Enforcement

**Key-Features:**

- ✅ Strict Mode (`extra="forbid"`)
- ✅ UUID4 Validierung
- ✅ ISO-8601 Timestamps
- ✅ Reasoning für Tool-Selection
- ✅ Rückgabe an den Client: Decision72 JSON

**Endpoints:**

```bash
GET  /health                 # Service health check
POST /log/opena1             # Request71 → Decision72
```

**Schema Request71:**

```json
{
  "request_id": "uuid4-string",
  "timestamp": "2025-11-21T12:00:00Z",
  "source": "openai",
  "user_query": "Analysiere Datei X",
  "context": {...},
  "metadata": {...}
}
```

**Schema Decision72:**

```json
{
  "decision_id": "uuid4-string",
  "request_id": "uuid4-string",
  "selected_tool": "tool_file_manager",
  "reasoning": "User wants file analysis",
  "forwarded_to": "http://127.0.0.1:12345/finalize/opena2",
  "timestamp": "2025-11-21T12:00:01Z"
}
```

---

### 🔹 2. opena2 — Archivator (Port 12345)

**Verantwortlichkeiten:**

- Persistiert Datenstrukturen in Safepoints:
  - **CMD** (vom Coordinator)
  - **RESP** (von Tools)
  - **ROUTE** (von kordp)
  - **DISPATCH** (von kordp)
- Verwendet Unicode-Arrow `→` in Dateinamen
- Struktur: `archivp_store/YYYY/MM/DD/SP<TS>_src→dst_KIND.json`

**Zusatzfeatures:**

- ✅ `index.jsonl` append-only Log
- ✅ Secret-Redaction für API Keys
- ✅ Dateipfad-Wächter

**Endpoints:**

```bash
GET  /health                 # Service health check
POST /finalize/opena2        # CMD safepoint creation
POST /store/resp             # RESP safepoint creation
```

**Safepoint-Struktur:**

```
archivp_store/
├── 2025/
│   └── 11/
│       └── 21/
│           ├── SP1763725786_opena1→archivp_CMD.json
│           ├── SP1763725786_archivp→opena1_RESP.json
│           ├── SP1763726001_opena1→kordp_ROUTE.json
│           └── SP1763726001_kordp→tool_DISPATCH.json
└── index.jsonl  (append-only)
```

**Naming Convention:**

```
SP<timestamp>_<source>→<destination>_<KIND>.json
```

- Unicode arrow `→` (U+2192) mandatory
- KIND: CMD, RESP, ROUTE, DISPATCH
- Timestamps: Unix epoch (10 digits)

---

### 🔹 3. kordp — Dispatch Gateway (Port 12346)

**Verantwortlichkeiten:**

- Verbindet Tools mit opena1/opena2
- HTTP Forwarding via httpx
- Routen-Endpoint `/dispatch/routes`
- JSON-basierte Registrierungs-Engine

**Tool-Registry (Default):**

| Tool-ID | Ziel |
|---------|------|
| tool_file_manager | opena5:12351 |
| tool_file_searcher | opena5:12351 |
| tool_text_analyzer | opena5:12351 |
| tool_default | kordp (Fallback) |

**Endpoints:**

```bash
GET  /health                 # Service health check
POST /dispatch               # Tool dispatch
GET  /dispatch/routes        # List registered tools
```

**Dispatch Request:**

```json
{
  "tool_id": "tool_file_manager",
  "payload": {...},
  "request_id": "uuid4-string"
}
```

---

### 🔹 4. opena20 — Dashboard (Port 12349)

**Verantwortlichkeiten:**

- Realtime-Überwachung aller Services
- API-Status-Polling alle 5s
- Fehleranzeige & Activity Log
- Ausführung von E2E-Tests
- View für Safepoints des aktuellen Tages

**UI-Features:**

- ✅ Modernes Corporate-Design (blau)
- ✅ Responsive Flexbox-Kacheln
- ✅ Dynamisches Activity-Log (JS)
- ✅ Live Status Indikatoren (grün/rot)
- ✅ Buttons:
  - Run E2E Test
  - Load Safepoints
  - Refresh Services
  - Restart Stack

**Endpoints:**

```bash
GET  /health                 # Dashboard health
GET  /                       # Dashboard UI
GET  /dashboard              # Dashboard UI (alias)
GET  /api/status             # All services status
POST /api/e2e                # Trigger E2E test
GET  /api/safepoints         # List today's safepoints
POST /api/restart            # Restart stack
```

**API Response Example:**

```json
{
  "opena1": {
    "service": "opena1",
    "status": "ok",
    "timestamp": "2025-11-21T12:24:16.904778Z",
    "port_policy": {
      "window": [12344, 12349],
      "forbidden": [8080]
    }
  },
  "opena2": {
    "status": "ok",
    "service": "opena2",
    "role": "archivp",
    "port": 12345,
    "entries": 174,
    "strict": true
  },
  "kordp": {
    "service": "kordp",
    "status": "ok",
    "role": "gateway",
    "timestamp": "2025-11-21T12:24:16.909190Z",
    "port_policy": {
      "window": [12344, 12399],
      "forbidden": [8080]
    }
  },
  "archivp": {
    "status": "ok",
    "safepoints_today": 4
  }
}
```

---

## 🧪 TESTING (E2E)

Ein voller End-to-End-Test deckt ab:

```
Request71 → opena1 → Decision72 
→ CMD safepoint → opena2
→ Dispatch → kordp
→ Tool → RESP safepoint → opena2
```

**Beispiel E2E Response:**

```json
{
  "request_id": "e2e-dashboard-abc123",
  "source": "opena1",
  "decision": {
    "selected_tool": "tool_default",
    "reason": "fallback",
    "resolved_path": null
  },
  "archivator_forward": {
    "endpoint": "http://127.0.0.1:12345/finalize/opena2",
    "status": "sent"
  },
  "status": "FORWARDED",
  "strict": true
}
```

**Test ausführen:**

```bash
# Via Dashboard
curl -X POST http://127.0.0.1:12349/api/e2e

# Via opena1 direkt
curl -X POST http://127.0.0.1:12344/log/opena1 \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "timestamp": "2025-11-21T12:00:00Z",
    "source": "openai",
    "user_query": "Test query",
    "context": {},
    "metadata": {}
  }'
```

---

## 📦 SAFEPOINT-FORMATE

**Dateinamenstruktur:**

```
SP<TIMESTAMP>_<SOURCE>→<DEST>_<CATEGORY>.json
```

**Kategorien:**

- **CMD** — Command from coordinator
- **RESP** — Response from tool
- **ROUTE** — Routing information
- **DISPATCH** — Dispatch metadata

**Heute erkannte Beispiele:**

```
SP1763725786_opena1→archivp_CMD.json
SP1763725786_archivp→opena1_RESP.json
SP1763726001_opena1→kordp_ROUTE.json
SP1763726001_kordp→tool_DISPATCH.json
```

**Safepoint Policies:**

- ✅ Append-only (no overwrites)
- ❌ Never delete
- ❌ Never modify
- ✅ YYYY/MM/DD directory structure
- ✅ Full envelope logging
- ✅ Unicode arrow `→` mandatory

---

## 🚀 STARTEN / STOPPEN

### Stack starten

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier
./bin/start_stack.sh
```

**Output:**

```
▶️  Starting opena2 (Port 12345)...
✅ opena2 started (PID: 684455)
▶️  Starting opena1 (Port 12344)...
✅ opena1 started (PID: 684588)
▶️  Starting kordp (Port 12346)...
✅ kordp started (PID: 684607)
▶️  Starting opena20 (Port 12349)...
✅ opena20 started (PID: 705698)
```

### Stack stoppen

```bash
./bin/stop_stack.sh
```

**Output:**

```
🛑 Stopping opena2 (PID: 684455)...
✅ opena2 stopped
🛑 Stopping opena1 (PID: 684588)...
✅ opena1 stopped
🛑 Stopping kordp (PID: 684607)...
✅ kordp stopped
🛑 Stopping opena20 (PID: 705698)...
✅ opena20 stopped
```

---

## 🔍 STATUS PRÜFEN

### Via Dashboard API

```bash
curl -s http://127.0.0.1:12349/api/status | jq .
```

### Einzelne Services

```bash
# opena1
curl -s http://127.0.0.1:12344/health | jq .

# opena2
curl -s http://127.0.0.1:12345/health | jq .

# kordp
curl -s http://127.0.0.1:12346/health | jq .

# opena20
curl -s http://127.0.0.1:12349/health | jq .
```

### Dashboard öffnen

```bash
xdg-open http://127.0.0.1:12349/dashboard
```

**Oder im Browser:**

```
http://127.0.0.1:12349/dashboard
```

---

## 📁 PROJEKTSTRUKTUR

```
1.opena1&2_portier/
│
├── opena1/                      # Coordinator service
│   ├── koordinator.py           # Core logic (120 lines)
│   └── main_production.py       # FastAPI entry (91 lines)
│
├── opena2/                      # Archivator service
│   └── opena2_app.py            # Full service (212 lines)
│
├── kordp/                       # Gateway service
│   ├── main_production.py       # FastAPI entry (91 lines)
│   ├── router.py                # Route handling (148 lines)
│   └── tool_resolver.py         # Tool resolution (186 lines)
│
├── opena20/                     # Dashboard service
│   ├── main.py                  # FastAPI app (67 lines)
│   ├── router.py                # API routes (137 lines)
│   ├── templates/
│   │   └── dashboard.html       # UI template (73 lines)
│   └── static/
│       ├── css/
│       │   └── dashboard.css    # Styles (214 lines)
│       └── js/
│           └── dashboard.js     # Logic (219 lines)
│
├── bin/                         # Operational scripts
│   ├── start_stack.sh           # Start all services
│   ├── stop_stack.sh            # Stop all services
│   ├── verify_stack.sh          # Integration verification
│   ├── check_ports.sh           # Port availability check
│   └── env_bootstrap.sh         # .env token generation
│
├── tests/                       # Test suite
│   └── test_portier_stack.py    # E2E tests (450+ lines)
│
└── archivp_store/               # Safepoint storage
    ├── YYYY/MM/DD/              # Date-based structure
    └── index.jsonl              # Append-only index
```

---

## 🛡️ SECURITY & COMPLIANCE

**Security Features:**

- ✅ Keine externen Netzwerke (localhost only)
- ✅ Nur localhost Kommunikation (127.0.0.1)
- ✅ Keine Secrets im Repo (.env in .gitignore)
- ✅ Events werden unveränderlich archiviert
- ✅ Strict-Mode enforced in allen Services
- ✅ Port Policy Enforcement (12344-12399)
- ✅ Bearer Token Authentication (Dashboard)

**Port Policy:**

- **Allowed:** 12344-12399 (backend services)
- **Forbidden:** 8080 (reserved for OpenWebUI UI-only)

**Environment Variables:**

```bash
OPENAI_API_KEY=sk-...          # Required for OpenAI integration
BEARER_TOKEN=<uuid>            # Dashboard authentication
ARCHIVP_ROOT=/path/to/archivp  # Safepoint storage
DB_PATH=/path/to/db.sqlite     # (future use)
```

**Token Bootstrap:**

```bash
bin/env_bootstrap.sh  # Generates .env with UUID token
```

---

## 📊 METRICS

**Code Statistics:**

- **Total Lines:** ~2,700+
- **Core Services:** ~1,500 lines
- **Dashboard:** 717 lines
- **Tests:** 450+ lines
- **Scripts:** ~100 lines

**Files Created:**

- Python modules: 15+
- HTML templates: 1
- CSS files: 1
- JavaScript files: 1
- Shell scripts: 8+
- Test files: 3+

**Git Status:**

- Branch: main
- Latest tag: v3.0.0
- Remote: <https://github.com/jokicdanijel/Gesamtprojekt-start.git>
- Status: Synchronized ✅

---

## 🧩 TECHNOLOGY STACK

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | 0.104+ |
| **ASGI Server** | Uvicorn | Latest |
| **Validation** | Pydantic | 2.0+ |
| **Templates** | Jinja2 | 3.1.6 |
| **HTTP Client** | httpx | Latest |
| **Python** | CPython | 3.13.x |
| **OS** | Ubuntu | 25.04 |
| **Runtime** | venv313 / system python | - |

**Frontend:**

- Vanilla JavaScript (ES6+)
- CSS3 with Flexbox/Grid
- No external frameworks (lightweight)

---

## 🔮 FUTURE ROADMAP

### Phase 4: OpenWebUI Integration

- [ ] opena3 terminal agent (Port 12347)
- [ ] OpenWebUI adapter (Port 12350)
- [ ] Chat modal in dashboard UI
- [ ] Bearer token authentication

### Phase 5: Advanced Features

- [ ] Persistent chat history
- [ ] Multi-turn conversations
- [ ] OAuth2 integration
- [ ] Kubernetes deployment
- [ ] Docker containerization
- [ ] Video tutorials

### Phase 6: Observability

- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Distributed tracing (OpenTelemetry / OTLP) — see `docker-compose.otel.yml` for a local collector example. Start it with:

```bash
# Run a local OTLP-compatible collector (for testing traces)
docker compose -f docker-compose.otel.yml up -d
```

- [ ] Log aggregation (ELK stack)

---

## 🐛 TROUBLESHOOTING

### Service startet nicht

```bash
# Check logs
cat logs/opena1.log
cat logs/opena2.log
cat logs/kordp.log
cat logs/opena20.log

# Check ports
netstat -tulpn | grep -E '1234[4-9]'

# Check processes
ps aux | grep -E 'opena|kordp'
```

### Dashboard nicht erreichbar

```bash
# Verify opena20 running
curl http://127.0.0.1:12349/health

# Check firewall
sudo ufw status

# Restart service
./bin/stop_stack.sh
./bin/start_stack.sh
```

### Safepoints werden nicht erstellt

```bash
# Check archivp directory
ls -la archivp_store/$(date +%Y/%m/%d)/

# Check opena2 logs
cat logs/opena2.log

# Verify permissions
chmod -R 755 archivp_store/
```

---

## 📚 DOCUMENTATION

**Primary Guides:**

- `.github/copilot-master-prompt.md` - Complete system knowledge
- `.github/copilot-instructions.md` - AI integration guide
- `.github/COMPLETION_CHECKLIST.md` - Phase tracking
- `PORTIER_3.0_RELEASE.md` - Release documentation
- `PORTIER_SYSTEM_DOCS.md` - This document
- `docs/OPERATIONS.md` - Runtime commands
- `docs/TROUBLESHOOTING.md` - Error scenarios
- `README_STACK_START.md` - Quick start guide

---

## 🏁 Fazit

**✅ System ist stabil**

- Alle Services laufen fehlerfrei
- Dashboard voll funktionsfähig
- Option-2-Flow validiert
- Safepoints korrekt gespeichert
- E2E-Tests bestanden

**✅ Produktionsreif**

- Keine offenen Fehler
- Vollständige Dokumentation
- Automatisierte Scripts
- Health Checks implementiert
- Security Policies enforced

**✅ Bereit für:**

- GitHub Release
- Private Repository Snapshot
- Weitere Feature-Entwicklung
- Production Deployment

---

## 👥 Contributors

**Primary Developer:** Danijel (ELION Team)  
**AI Assistant:** GitHub Copilot (Claude Sonnet 4.5)

---

## 📄 License

**Internal Use Only**  
Proprietary - All Rights Reserved

---

## 📞 Support

**Issues:** <https://github.com/jokicdanijel/Gesamtprojekt-start/issues>  
**Discussions:** <https://github.com/jokicdanijel/Gesamtprojekt-start/discussions>

---

**Last Updated:** 21. November 2025  
**Version:** 3.0.0  
**Status:** ✅ PRODUCTION-READY

---

**Dashboard:** <http://127.0.0.1:12349/dashboard>  
**Status API:** <http://127.0.0.1:12349/api/status>  
**Health Check:** <http://127.0.0.1:12349/health>
