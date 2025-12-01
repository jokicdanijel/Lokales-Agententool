# 📊 Service-Matrix - ELION Hyper-Dashboard / Portier System

**Version:** 2.0  
**Stand:** 21. November 2025  
**Status:** ✅ Produktiv

---

## 🏗️ System-Topologie

```
┌─────────────────────────────────────────────────┐
│  Browser/UI (OpenWebUI Port 3000) - UI ONLY    │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  Portier (12344)   │ ← Koordinator/Dispatcher
         │  Route Registry    │   Option-2-Weiterleitung
         │  Dispatch Engine   │   service_target Validierung
         └─────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐   ┌────▼─────┐   ┌───▼──────┐
│OpenA2  │   │Telegram  │   │Inference │
│12345   │   │12346     │   │12348     │
│Archiv  │   │Messaging │   │llama2    │
└────────┘   └──────────┘   └──────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
        ┌──────────▼───────────┐
        │ Pool: 12349–12368    │
        │ (20 skalierbare      │
        │  Template-Services)  │
        └──────────────────────┘
```

---

## 📋 Haupt-Services (Core-Infrastruktur)

| Port | Service | Rolle | program_target | API-Endpoint | Status |
|------|---------|-------|----------------|--------------|--------|
| **3000** | **OpenWebUI** | UI Frontend (KEIN Backend!) | - | - | ✅ Online |
| **12344** | **Portier** | Koordinator/Dispatcher | `portierp` | `/route/update`, `/dispatch/kordp` | ✅ Online |
| **12345** | **OpenA2** | Archivator/JSONL Safepoints | `archp` | `/store/archivp`, `/query/archivp` | ✅ Online |
| **12346** | **Telegram** | Messaging ChatOps | `telep` | `/send_message`, `/poll_updates` | ✅ Online |
| **12348** | **Inference** | Llama2/Ollama ChatCompletion | `inferp` | `/chat/completions` | ✅ Online |

---

## 🔢 Pool-Services (Skalierbare Agents, 12349–12368)

| Port | Service | program_target | Rolle | Status |
|------|---------|----------------|-------|--------|
| **12349** | agent01 | `agent01p` | Template-basierter Service | 📋 Template |
| **12350** | agent02 (Mini-Orchestrator) | `miniorchp` | Interner Agent-Manager (Mail, Browser, Workflow) | ✅ Online |
| **12351** | agent03 | `agent03p` | Template-basierter Service | 📋 Template |
| **12352** | agent04 | `agent04p` | Template-basierter Service | 📋 Template |
| **12353** | agent05 | `agent05p` | Template-basierter Service | 📋 Template |
| **12354** | agent06 | `agent06p` | Template-basierter Service | 📋 Template |
| **12355** | agent07 | `agent07p` | Template-basierter Service | 📋 Template |
| **12356** | agent08 | `agent08p` | Template-basierter Service | 📋 Template |
| **12357** | agent09 | `agent09p` | Template-basierter Service | 📋 Template |
| **12358** | agent10 | `agent10p` | Template-basierter Service | 📋 Template |
| **12359** | agent11 | `agent11p` | Template-basierter Service | 📋 Template |
| **12360** | agent12 | `agent12p` | Template-basierter Service | 📋 Template |
| **12361** | agent13 | `agent13p` | Template-basierter Service | 📋 Template |
| **12362** | agent14 | `agent14p` | Template-basierter Service | 📋 Template |
| **12363** | agent15 | `agent15p` | Template-basierter Service | 📋 Template |
| **12364** | agent16 | `agent16p` | Template-basierter Service | 📋 Template |
| **12365** | agent17 | `agent17p` | Template-basierter Service | 📋 Template |
| **12366** | agent18 | `agent18p` | Template-basierter Service | 📋 Template |
| **12367** | agent19 | `agent19p` | Template-basierter Service | 📋 Template |
| **12368** | agent20 | `agent20p` | Template-basierter Service | 📋 Template |

---

## 🔌 Port-Policy (erweitert)

### ✅ **Erlaubte Ports:**
- **12344-12399:** Backend Services (Microservices, Agents, Tools)
- **3000:** UI (OpenWebUI) - **NUR Frontend, KEIN Backend-Prozess**

### ❌ **Verbotene Ports:**
- **< 12344:** Ungültig für Backend-Services
- **8080:** Historisch verboten (Portier/ELION-Legacy-Konflikt)
- **3000 als Backend:** UI-Port darf NIEMALS Backend-Logik hosten

### 🔓 **Reserviert:**
- **12369-12399:** Zukünftige Erweiterungen (31 Slots verfügbar)

---

## 🔄 Option-2-Routing (Kommunikationsfluss)

### **Vollständiger Flow:**

```
Client/UI (3000)
    ↓
Portier (12344) ← EINZIGER legitimer Einstieg
    ↓
OpenA2 CMD (12345) ← Safepoint: SP<n>_src→dst_CMD.json
    ↓
kordp/Dispatcher (intern, Portier-Modul)
    ↓
Zielservice (12346 Telegram / 12348 Inference / 12349-12368 Pool)
    ↓
OpenA2 RESP (12345) ← Safepoint: SP<n>_dst→src_RESP.json
    ↓
Portier (12344)
    ↓
Client/UI (3000)
```

### **Verbotene Kommunikation:**
❌ `UI → Service` (direkt)  
❌ `Service → Service` (ohne Portier)  
❌ `Service → OpenA2` (ohne Portier)  
❌ `UI → OpenA2` (direkt)

---

## 📡 API-Patterns (standardisiert)

### 1. **Portier Route Update** (Service-Registration)

**Endpoint:** `POST http://127.0.0.1:12344/route/update`

```json
{
  "service_name": "my_service",
  "endpoint": "http://127.0.0.1:12350",
  "program_target": "myservp"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Route registered",
  "service_name": "my_service",
  "program_target": "myservp"
}
```

---

### 2. **Portier Dispatch** (Command-Routing)

**Endpoint:** `POST http://127.0.0.1:12344/dispatch/kordp`

```json
{
  "service_target": "telep",
  "action": "send_message",
  "params": {
    "chat_id": 12345,
    "message": "Hello from Portier"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "message_id": 67890,
    "sent_at": "2025-11-21T12:00:00Z"
  }
}
```

---

### 3. **OpenA2 Safepoint Store** (Archivierung)

**Endpoint:** `POST http://127.0.0.1:12345/store/archivp`

```json
{
  "src": "portierp",
  "dst": "telep",
  "kind": "CMD",
  "body": {
    "action": "send_message",
    "params": {"chat_id": 12345, "message": "Test"}
  },
  "strict": true
}
```

**Response:**
```json
{
  "status": "success",
  "sp_id": "SP00123",
  "path": "2025/11/21/SP00123_portierp→telep_CMD.json"
}
```

---

### 4. **Inference Completion** (Llama2/Ollama)

**Endpoint:** `POST http://127.0.0.1:12348/chat/completions`

```json
{
  "model": "llama2",
  "messages": [
    {"role": "user", "content": "Hello, how are you?"}
  ],
  "max_tokens": 50,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1700580000,
  "model": "llama2",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I'm doing well, thank you!"
      },
      "finish_reason": "stop"
    }
  ]
}
```

---

## ⚡ Performance-Metriken (Load-Test-Ergebnisse)

| Szenario | Services | Throughput | Latenz (P95) | Status |
|----------|----------|------------|--------------|--------|
| **4 Services** | Portier + OpenA2 + Telegram + Inference | ~24.55 req/s | ~160ms | ✅ Getestet |
| **Inference-Only** | Llama2 ChatCompletion | ~0.87 req/s | ~1150ms (GPU-bound) | ✅ Getestet |
| **20 Services** | Full Pool Active | ~27.74 req/s | ~720ms | 📋 Geplant |

**Load-Test-Script:** `scripts/load_test_20_services.py`

---

## 🔐 Sicherheit & Authentifizierung

### **Security-Layer:**
1. ✅ **Bearer-Token-Validierung** für alle Endpoints außer `/health`
2. ✅ **Archiv-Anonymisierung** (token, api_key maskiert in Safepoints)
3. ✅ **`.env` NIEMALS in Git** (`.gitignore` enforcement)
4. ✅ **Portier = Security-Gateway** (Single Point of Auth)

### **Header-Format:**
```http
Authorization: Bearer <BEARER_TOKEN>
Content-Type: application/json
```

---

## 📊 Monitoring & Metrics (Prometheus)

**Metrics-Endpoint:** `/metrics` (Prometheus-Format)

**Verfügbare Metriken:**
- `service_requests_total{service, endpoint, status}` - Request Counter
- `service_request_duration_seconds{service, endpoint}` - Latenz Histogram
- `service_active_connections{service}` - Active Connections Gauge
- `service_health_status{service}` - Health Status (1=healthy, 0=unhealthy)
- `archiv_entries_total{kind}` - Archiv-Einträge (CMD/RESP)
- `agent_manager_agents_total{status}` - Agent-Manager Stats
- `memory_system_entries_total{agent_id}` - Memory-System Stats

**Prometheus Scraping Config:**
```yaml
scrape_configs:
  - job_name: 'portier_system'
    static_configs:
      - targets:
        - '127.0.0.1:12344'  # Portier
        - '127.0.0.1:12345'  # OpenA2
        - '127.0.0.1:12346'  # Telegram
        - '127.0.0.1:12348'  # Inference
        - '127.0.0.1:12350'  # Mini-Orchestrator
```

---

## 🗺️ Roadmap (PHASE 17-20)

| Phase | Feature | Status | Ziel-Datum |
|-------|---------|--------|------------|
| **17** | Monitoring Dashboard (Prometheus/Grafana) | ⏳ In Arbeit | Q1 2026 |
| **18** | Deployment (Docker Compose/K8s) | 📋 Geplant | Q1 2026 |
| **19** | Service Mesh (Istio/Linkerd) | 📋 Geplant | Q2 2026 |
| **20** | RBAC + Multi-Tenant | 📋 Geplant | Q2 2026 |

---

## 🚀 Quick Start

### **Alle Services starten:**
```bash
# Core-Services
bin/start_all.sh

# Pool-Services
bin/pool_services.sh start

# Mini-Orchestrator
bin/start_agent_server.sh

# Alle Health-Checks prüfen
curl http://127.0.0.1:12344/health | jq .
curl http://127.0.0.1:12345/health | jq .
curl http://127.0.0.1:12350/health | jq .
```

### **Test-Dispatch senden:**
```bash
curl -X POST http://127.0.0.1:12344/dispatch/kordp \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_target": "miniorchp",
    "action": "send_mail",
    "params": {"to": "test@example.com", "subject": "Test"}
  }' | jq .
```

### **Load-Test ausführen:**
```bash
python3 scripts/load_test_20_services.py
```

---

## 📁 Ordnerstruktur

```
Gesamtprojekt/
├── src/
│   ├── services/
│   │   ├── portier/        (12344)
│   │   ├── opena2/         (12345)
│   │   ├── telegram/       (12346)
│   │   ├── inference/      (12348)
│   │   └── pool/
│   │       ├── agent01/    (12349)
│   │       ├── agent02/    (12350) ← Mini-Orchestrator
│   │       └── agent03-20/ (12351-12368)
│   └── pkg/
│       ├── agent_server.py
│       ├── monitoring.py
│       └── agents/
├── 1.opena1&2_portier/
│   ├── archivp_store/
│   │   ├── index.jsonl
│   │   └── YYYY/MM/DD/
│   └── knowledgebase/
├── bin/
│   ├── start_all.sh
│   ├── pool_services.sh
│   └── start_agent_server.sh
├── scripts/
│   ├── load_test_20_services.py
│   └── integrate_mini_orchestrator_portier.py
├── docs/
│   ├── SERVICE_MATRIX.md (dieses Dokument)
│   └── AGENT_SERVER_ARCHITECTURE.md
└── README.md
```

---

## 🔗 Referenzen

- **Option-2-Flow:** Siehe `.github/copilot-master-prompt.md`
- **Mini-Orchestrator:** Siehe `docs/AGENT_SERVER_ARCHITECTURE.md`
- **Load-Test:** Siehe `scripts/load_test_20_services.py`
- **Monitoring:** Siehe `src/pkg/monitoring.py`

---

**Maintainer:** ELION Team  
**Lizenz:** Internal Use Only  
**Letzte Aktualisierung:** 21. November 2025
