# ELION Stack – Struktur-Analyse (2025-11-08)

## 📊 Überblick

**Status:** 3/5 Services operational (60%)  
**Zeitbudget:** 7 Tage bis 15. Nov (SPRINT-MODE)  
**Blocker:** Hauptdashboard (opena19) nicht getestet, .env fehlt, Finance-DB nicht gestartet

---

## ✅ OPERATIONAL (Getestet & Laufen)

### opena1 (Koordinator) – Port 12344
- **Datei:** `19.dashboard_agent/main_opena1.py` (7.7 KB)
- **Start:** `bin/start_opena1.sh`
- **Status:** ✅ Läuft
- **Endpoints:**
  - `GET /health` – Status
  - `POST /store/archivp` – Archiv schreiben
  - `GET /store/archivp` – Archiv lesen
  - `POST /finalize/opena2` – Finalisieren

### opena2 (Archivator) – Port 12345
- **Datei:** `19.dashboard_agent/main_opena2.py` (4.8 KB)
- **Start:** `bin/start_opena2.sh`
- **Status:** ✅ Läuft
- **Speicher:** Append-only JSON in `19.dashboard_agent/ARCHIV/YYYY/MM/DD/`
- **Endpoints:**
  - `GET /health`
  - `POST /store/archivp` – Daten persistieren
  - `GET /archiv/last?n=5` – Letzte N Einträge
  - `GET /archiv/get?path=...` – Spezifischer Eintrag

### kordp (Koordinator-Relay) – Port 12346
- **Datei:** `19.dashboard_agent/main_kordp.py` (4.6 KB)
- **Start:** `bin/start_kordp.sh`
- **Status:** ✅ Gestartet (Nov 8, 16:45)
- **Endpoints:**
  - `GET /health`
  - `POST /event/trigger` – Events auslösen

---

## ⚠️ HALF-DONE (Existiert, Untested)

### opena19 (Hauptdashboard) – Port 12349
- **Datei:** `19.dashboard_agent/main_dashboard.py` (9.6 KB)
- **Start:** `bin/start_opena19.sh` (existiert, nie getestet)
- **Status:** ⚠️ Code ready, **NEVER STARTED**
- **Kritikalität:** 🔴 BLOCKIERT Finance-DB Integration
- **Endpoints (dokumentiert):**
  - `GET /health`
  - `POST /api/agent/register`
  - `GET /api/status/all`
  - `SSE /api/stream/events`
  - Weitere: Siehe `main_dashboard.py` Zeile 90+
- **Dependencies:** 
  - `agent_registry.py` (vorhanden)
  - `sse_bus.py` (vorhanden)
  - `security.py` (vorhanden)

### OpenWebUI Adapter – Port 12351
- **Datei:** `19.dashboard_agent/main_openwebui_agent.py` (2.3 KB)
- **Start:** `bin/start_openwebui_adapter.sh` (existiert, nie getestet)
- **Status:** ⚠️ Code ready, **NEVER STARTED**
- **Kritikalität:** 🟡 Nice-to-have für UI

---

## ❌ NOT-STARTED (Dokumentiert, aber 0% Code)

### opena_finance (Finance Agent) – Port 12347?
- **Status:** 0% – Nicht gestartet
- **Bedarf:** 
  - `main_opena_finance.py` (erstellen)
  - SQLite Finance-DB schema
  - Endpoints: `POST /query`, `POST /archive`, `GET /statement`
- **Kritikalität:** 🔴 USER'S IMMEDIATE NEED

### opena4 (Telegram Bridge) – Port 12348?
- **Status:** 0% – Dokumentiert (5 Parts), kein Code
- **Bedarf:**
  - `main_opena4_telegram.py` (erstellen)
  - Webhook-Handler für Telegram
  - Integration mit opena19
- **Kritikalität:** 🟡 Phase 2

### opena5 (VS Code Bridge)
- **Status:** 0% – Konzeptionell nur
- **Kritikalität:** 🟢 Phase 3+

---

## 🛠️ Infrastructure (Orchestration)

### Root-Level Scripts (`bin/`)

| Script | Size | Status | Purpose |
|--------|------|--------|---------|
| `ops.sh` | 145B | ✅ | Main orchestrator |
| `start_all.sh` | 151B | ✅ | Start all services |
| `stop_all.sh` | 150B | ✅ | Stop all services |
| `health_matrix.sh` | 1.1K | ✅ **TESTED** | Port check (works!) |
| `env_bootstrap.sh` | 155B | ✅ | Generate .env |
| `env_probe.sh` | 1.4K | ✅ **TESTED** | Validate tokens |
| `fix_stack_now.sh` | 5.8K | ✅ | Full stack bring-up |
| `stack_status_badge.sh` | 493B | ⚠️ | Not yet tested |
| `port_kill_safeguard.sh` | 1.6K | ⚠️ | Not yet tested |
| `check_ports.sh` | 153B | ✅ | Show listening ports |
| `system_mode_switch.sh` | 15K | ⚠️ | Bootstrap (not tested) |
| `verify_stack.sh` | 154B | ⚠️ | Integration test |

### Dashboard-Level Scripts (`19.dashboard_agent/bin/`)

| Script | Purpose | Status |
|--------|---------|--------|
| `start_opena1.sh` | opena1 start | ✅ Works |
| `start_opena2.sh` | opena2 start | ✅ Works |
| `start_kordp.sh` | kordp start | ✅ Works |
| `start_opena19.sh` | Dashboard start | ⚠️ Never tried |
| `start_opena3.sh` | OpenWebUI start | ⚠️ Never tried |
| `start_openwebui_adapter.sh` | Adapter start | ⚠️ Never tried |
| `env_bootstrap.sh` | Token generation | ✅ |
| `ops.sh` | Local orchestrator | ⚠️ |

---

## 📁 Key Files Status

### Python Services
```
19.dashboard_agent/
├── main_dashboard.py      ✅ READY (9.6 KB, not started)
├── main_opena1.py         ✅ RUNNING (7.7 KB)
├── main_opena2.py         ✅ RUNNING (4.8 KB)
├── main_kordp.py          ✅ RUNNING (4.6 KB)
├── main_openwebui_agent.py ✅ READY (2.3 KB, not started)
├── agent_registry.py       ✅ (registry logic)
├── sse_bus.py             ✅ (event streaming)
├── security.py            ✅ (auth logic)
└── config.py              ✅ (settings)
```

### Configuration & Auth
```
.env                      ❌ MISSING (CRITICAL!)
19.dashboard_agent/.env   ⚠️ Check if exists
```

### Archive/Storage
```
19.dashboard_agent/ARCHIV/
├── 2025/
│   └── 11/
│       ├── 06/ (test data from earlier)
│       └── 07/
└── index.jsonl (append-only)
```

### Documentation (5-Part Spec)
```
docs/
├── Routing Matrix         ✅ (written)
├── Dashboard API          ✅ (written)
├── UI Blueprints          ✅ (written)
├── Reference Impl.        ✅ (written)
└── Governance             ✅ (written)
```

**Status:** Documentation complete, **NOT YET deployed to code**.

---

## 🔴 CRITICAL BLOCKERS

### 1. Missing `.env` Token
- **Impact:** Can't authenticate to any service
- **Fix:** Run `bin/env_bootstrap.sh`
- **Estimated Time:** 2 minutes
- **Priority:** 🔴 MUST DO FIRST

### 2. opena19 (Dashboard) Never Started
- **Impact:** Can't register agents, UI not available
- **Fix:** Run `bin/start_opena19.sh` or `python 19.dashboard_agent/main_dashboard.py`
- **Estimated Time:** 5 minutes
- **Priority:** 🔴 MUST DO SECOND

### 3. Finance DB Not Designed
- **Impact:** Can't store/query financial data
- **Fix:** Create `19.dashboard_agent/finance.db` schema + `main_opena_finance.py`
- **Estimated Time:** 1–2 hours
- **Priority:** 🔴 USER IMMEDIATE NEED

### 4. Telegram Bridge Not Deployed
- **Impact:** Can't integrate Telegram webhook
- **Fix:** Create `main_opena4_telegram.py` from 5-Part spec
- **Estimated Time:** 2–3 hours
- **Priority:** 🟡 Phase 2

---

## 📋 Next 24 Hours – SPRINT PLAN

### Hour 1: Stabilization
- [ ] Generate `.env` → `bin/env_bootstrap.sh`
- [ ] Test opena19 start → `bin/start_opena19.sh`
- [ ] Verify all 5 ports listening (health check)

### Hour 2–3: Finance DB
- [ ] Design SQLite schema (accounts, transactions, statements)
- [ ] Create `main_opena_finance.py` (REST API)
- [ ] Test `POST /query` + archive write to opena2

### Hour 4–5: Dashboard Finance Widget
- [ ] Extend `main_dashboard.py` with `/api/finance/*` endpoints
- [ ] Integrate opena_finance in agent registry
- [ ] Test full pipeline: Dashboard → Finance → Archive

### Hour 6–7: Telegram Bridge (opena4)
- [ ] Create `main_opena4_telegram.py` from spec
- [ ] Implement webhook receiver
- [ ] Register with Dashboard

### Hour 8: Deployment & Cleanup
- [ ] Run `bin/verify_stack.sh` (full integration test)
- [ ] Document current state
- [ ] Ready for Nov 9 sprint continuation

---

## 🎯 Success Criteria (End of 24h)

- ✅ All 5 base services running (opena1–4, kordp, opena19)
- ✅ Finance DB operational (read/write test)
- ✅ Telegram webhook registered
- ✅ Dashboard showing all agents
- ✅ Full integration test passing

---

## Port Allocation (12344–12399)

| Port | Service | Status | Notes |
|------|---------|--------|-------|
| 12344 | opena1 | ✅ | Coordinator |
| 12345 | opena2 | ✅ | Archivator |
| 12346 | kordp | ✅ | Relay |
| 12347 | opena_finance | ⏳ | Finance (TODO) |
| 12348 | opena4 | ⏳ | Telegram (TODO) |
| 12349 | opena19 | ⚠️ | Dashboard (ready, not started) |
| 12350 | (reserved) | - | - |
| 12351 | opena3 | ⚠️ | OpenWebUI adapter (ready, not started) |
| 8080 | (FORBIDDEN) | ❌ | Never use |

---

## Generated: 2025-11-08 16:47
**Analyst:** GitHub Copilot (Sprint Mode)
