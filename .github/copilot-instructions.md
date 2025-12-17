# ELION Hyper-Dashboard — Copilot Quick Guide

**Kurzversion (lese zuerst):** Dies ist eine kompakte Anleitung für AI-Coding-Agenten. Die vollständigen, verbindlichen Regeln und Policies stehen in `.github/copilot-master-prompt.md` — lies diese Datei vor nicht-trivialen Änderungen.

## Schnellbefehle

- Env bootstrap: `bin/env_bootstrap.sh` (erzeugt `.env` aus `.env.example`)
- Start/Stop/Verify: `bin/ops.sh start|stop|verify|status|logs`
- Tests: `python -m pytest -v tests/ -k <pattern>` (z.B. `openwebui`)
- Lint/Format: `python -m flake8 <file>` / `python -m black <file>`

## Unbedingte Regeln (Kurz)

- Ports: **12344–12399** (niemals 8080 für Services). Änderungen an Ports sind _policy‑kritisch_ — verwerfen und Alternative vorschlagen.
- Option-2-Flow: **opena1 → opena2 → kordp → Tool** (zwangsläufig).
- Safepoints: Benennung `SP<number>_src→dst_{CMD|RESP|ERR}.json`, Ablage `archivp/YYYY/MM/DD/`.
- Env & Secrets: `.env` im Projekt-Root ist Source-of-Truth; **keine** Secrets in Git.
- JSON/Pydantic: `strict: true`, `extra="forbid"` — keine zusätzlichen Felder.

## Konventionen für Codeänderungen

- OpenWebUI / Tools: Pydantic-Models, **Tools class** mit `@staticmethod`, **async-ready**, Rückgabe `dict` mit `status` (`"success"|"error"`) und `data`.
- Tests: Bei Agent-Code immer Unit‑ und Security‑Tests (inkl. negative cases).
- Preflight PR-Checks: `.env` vorhanden, Ports geprüft, flake8/black ok, Tests laufen, `bin/ops.sh verify` (nach Infra-Änderungen).

## Wo nachschlagen (Files)

- `.github/copilot-master-prompt.md` (Policy & Start-Flow)
- `bin/ops.sh`, `bin/verify_stack.sh`, `bin/check_ports.sh`
- `docs/OPERATIONS.md`, `docs/OPENWEBUI_INTEGRATION.md`, `docs/TROUBLESHOOTING.md`
- `1.opena1&2_portier/README.md`, `19.opena20_dashboard_agent/README.md`, `2.opena3_openwebui/.github/copilot-instructions.md`

---

<!-- Archiv: ausführliche, ältere Instruktionen weiter unten — hilfreich für Kontext und Nachverfolgung -->

---

## Phase 1: Core Infrastructure (20 Tasks) ✅

- [x] **1. VS Code Launch Config** – `.vscode/launch.json` (4 configs + compound)
- [x] **2. VS Code Tasks** – `.vscode/tasks.json` (8 ops tasks)
- [x] **3. Main Orchestrator** – `bin/ops.sh` (central controller)
- [x] **4. Start All Services** – `bin/start_all.sh`
- [x] **5. Stop All Services** – `bin/stop_all.sh`
- [x] **6. Integration Verification** – `bin/verify_stack.sh`
- [x] **7. Agent Registration** – `bin/agents_register.sh`
- [x] **8. Token Bootstrap** – `bin/env_bootstrap.sh`
- [x] **9. Port Checker** – `bin/check_ports.sh`
- [x] **10. Log Tail** – `bin/log_tail.sh` (follow mode)
- [x] **11. Reset Today** – `bin/reset_today.sh`
- [x] **12. Clean Python Cache** – `bin/clean_pycache.sh`
- [x] **13. Print Token** – `bin/print_token.sh`
- [x] **14. Root Wrappers** – `Gesamtprojekt/bin/` delegation scripts (11 files)
- [x] **15. Register Script** – `scripts/register_agents.py`
- [x] **16. cURL Examples** – `scripts/curl_examples.sh`
- [x] **17. Archivator Test** – `tests/test_archivator.py`
- [x] **18. Operations Guide** – `docs/OPERATIONS.md`
- [x] **19. OpenWebUI Integration Guide** – `docs/OPENWEBUI_INTEGRATION.md`
- [x] **20. Quick Start** – `README_STACK_START.md`

**Artifacts:** 40+ files | **Status:** All tested ✅

---

## Phase 2: OpenWebUI Integration (20 Tasks) ✅

### Core Components (5 Tasks)

- [x] **1. OpenWebUI Adapter** – `openwebui_adapter.py` (Port 12350)
  - Purpose: HTTP forwarding to OpenWebUI (8080)
  - Methods: `/openwebui/chat`, `/openwebui/health`
- [x] **2. opena3 Agent** – `main_openwebui_agent.py` (Port 12347)
  - Purpose: FastAPI wrapper around OpenWebUI
  - Endpoints: `/health`, `/command`, `/invoke`
- [x] **3. Adapter Start Script** – `bin/start_openwebui_adapter.sh`
  - Launches adapter in nohup
  - Logs to `logs/openwebui_adapter.nohup.log`
- [x] **4. opena3 Start Script** – `bin/start_opena3.sh`
  - Launches agent in nohup
  - Logs to `logs/opena3.nohup.log`
- [x] **5. OpenWebUI Test Script** – `scripts/test_openwebui.py`
  - Health checks, command endpoint, OpenWebUI availability

### Dashboard Integration (3 Tasks)

- [x] **6. Dashboard Endpoints** – `main_dashboard.py` extended
  - `/api/openwebui/status` – GET agent health (Bearer token required)
  - `/api/openwebui/chat` – POST chat request (rate-limited, SSE event published)
- [x] **7. UI Enhancement** – `ui_index.html` ✅ **COMPLETED**
  - Modal dialog for OpenWebUI chat
  - Bearer token storage (localStorage)
  - JavaScript fetch integration
  - Status indicators (ok/error/loading)
- [x] **8. API Documentation** – `docs/OPENWEBUI_API.md`
  - Endpoint descriptions
  - cURL examples
  - Error handling (401, 502, 504)

### Configuration & Registry (3 Tasks)

- [x] **9. OpenWebUI Config** – `config.py` extended
  - `OpenWebUIConfig` class
  - URL, ports, timeouts from env
- [x] **10. Registry Extensions** – `agent_registry.py` extended
  - `register_if_absent()` – idempotent registration
  - `list_agents()` – compact list
  - `persist()`, `load()` – JSON persistence
- [x] **11. Security CORS** – Inline in `main_dashboard.py`
  - Middleware validates inbound ports
  - Agent communication unrestricted

### Data & Utilities (5 Tasks)

- [x] **12. Safepoint Latest** – `safepoints_latest.py`
  - `latest()` function retrieves newest checkpoint
- [x] **13. OpenWebUI Seeding** – `scripts/seed_openwebui.py`
  - Sends 3 example prompts to opena3
  - Stores responses in archivp via opena2
- [x] **14. opena3 Tests** – `tests/test_openwebui_agent.py`
  - Pytest suite (health, command, availability)
- [x] **15. OpenWebUI Status Checker** – `bin/openwebui_status.sh`
  - Checks ports 8080, 12347, 12350
- [x] **16. Troubleshooting Guide** – `docs/TROUBLESHOOTING.md`
  - 8+ scenarios (401, 404, unreachable, ports, tokens, logs, SSE, registration)

### Dependencies & Deployment (4 Tasks)

- [x] **17. Requirements Update** – `requirements.txt` extended
  - Added: `requests`, `aiohttp`, `httpx`
  - Total: 30 packages
- [x] **18. Docker Containerization** – `Dockerfile.openwebui`
  - Base: `python:3.12-slim`
  - Exposes ports 12349 + 8080
- [x] **19. Data Migration** – `scripts/migrate_data.py`
  - Safepoint format conversion
  - Adds `"migrated": true` flag
- [x] **20. Backlog & Tracking** – `docs/OPENWEBUI_TODO.md`
  - 30+ items across features, testing, docs, infrastructure

**Artifacts:** 20 files | **Status:** All executable ✅

---

## Phase 3: Documentation & Governance ✅

- [x] **AI Copilot Instructions** – `.github/copilot-instructions.md` (200+ lines)
  - Architecture overview
  - Port & service mapping
  - Build & runtime commands
  - Critical workflows (endpoints, agents, archivator)
  - Conventions (tokens, logging, testing, root wrapper)
  - Integration points
  - Debugging tips
  - VS Code setup
  - Extension guide

---

## Summary

| Phase                        | Tasks  | Status          | Key Deliverables                     |
| ---------------------------- | ------ | --------------- | ------------------------------------ |
| **1. Core Infrastructure**   | 20     | ✅ Complete     | Orchestration, docs, root wrappers   |
| **2. OpenWebUI Integration** | 20     | ✅ Complete     | Adapter, agent, endpoints, tests, UI |
| **3. AI Documentation**      | 1      | ✅ Complete     | 200+ line Copilot guide              |
| **Total**                    | **41** | **✅ COMPLETE** | **60+ files, fully tested**          |

---

## Quick Start (From Project Root)

```bash
# Generate .env token (if missing)
bin/env_bootstrap.sh

# Start all services
bin/ops.sh start

# Verify integration
bin/ops.sh verify

# Check status
bin/ops.sh status | jq .

# View logs
bin/ops.sh logs

# Access Dashboard UI
open http://127.0.0.1:12349/ui_index.html
# (or) Test OpenWebUI
python scripts/test_openwebui.py

# Stop all
bin/ops.sh stop
```

---

## File Structure (Final State)

```
Gesamtprojekt/
├── .github/
│   ├── copilot-instructions.md (200+ lines)
│   └── COMPLETION_CHECKLIST.md (this file)
├── bin/
│   ├── ops.sh ──────────────────┐
│   ├── start_all.sh             │
│   ├── stop_all.sh              ├─ Root-level wrappers
│   ├── verify_stack.sh          │
│   └── [8 more scripts] ────────┘
├── 19.dashboard_agent/
│   ├── bin/
│   │   ├── ops.sh (primary)
│   │   ├── start_opena1.sh
│   │   ├── start_opena2.sh
│   │   ├── start_opena3.sh ◄── OpenWebUI opena3
│   │   ├── start_openwebui_adapter.sh ◄── Port 12350 adapter
│   │   ├── [10+ scripts]
│   ├── main_dashboard.py ◄── Extended with /api/openwebui/* endpoints
│   ├── openwebui_adapter.py ◄── NEW
│   ├── main_openwebui_agent.py ◄── NEW
│   ├── ui_index.html ◄── Enhanced with Chat modal
│   ├── config.py ◄── Added OpenWebUIConfig
│   ├── agent_registry.py ◄── Added register_if_absent, list_agents
│   ├── safepoints_latest.py ◄── NEW
│   ├── requirements.txt ◄── Updated (30 packages)
│   ├── scripts/
│   │   ├── test_openwebui.py ◄── NEW
│   │   ├── seed_openwebui.py ◄── NEW
│   │   ├── migrate_data.py ◄── NEW
│   ├── tests/
│   │   ├── test_openwebui_agent.py ◄── NEW
│   │   ├── test_archivator.py
│   ├── docs/
│   │   ├── OPENWEBUI_API.md ◄── NEW
│   │   ├── TROUBLESHOOTING.md ◄── NEW
│   │   ├── OPENWEBUI_TODO.md ◄── NEW
│   │   ├── OPERATIONS.md
│   │   ├── OPENWEBUI_INTEGRATION.md
│   ├── README_STACK_START.md
```

---

## Validation Commands

```bash
# From project root
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# Test root wrappers exist
ls -la bin/*.sh

# Test core infrastructure
bin/ops.sh help
bin/ops.sh verify

# Test OpenWebUI integration
python 19.dashboard_agent/scripts/test_openwebui.py

# Test UI loads
curl -s http://127.0.0.1:12349/ui_index.html | head -20

# List all new files
git status | grep "new file" || echo "Not a git repo; use find instead"
```

---

## Known Limitations & Future Work

| Category       | Item                            | Status     |
| -------------- | ------------------------------- | ---------- |
| **Features**   | Persistent chat history         | 📋 Backlog |
| **Features**   | Multi-turn conversation         | 📋 Backlog |
| **Testing**    | E2E UI tests (Selenium/Cypress) | 📋 Backlog |
| **Docs**       | Video tutorials                 | 📋 Backlog |
| **Deployment** | Kubernetes manifests            | 📋 Backlog |
| **Security**   | OAuth2 integration              | 📋 Backlog |

See `docs/OPENWEBUI_TODO.md` for full backlog (30+ items).

---

## Success Criteria ✅

- [x] All 40 infrastructure tasks complete + executable
- [x] OpenWebUI integration fully functional (adapter + agent + endpoints)
- [x] UI modal for chat with Bearer token support
- [x] Comprehensive documentation (API, troubleshooting, backlog)
- [x] AI Copilot instructions (200+ lines) in place
- [x] All scripts have chmod +x permissions
- [x] Root-level wrapper pattern enforced
- [x] Test coverage for critical paths

**Result:** **✅ Project-Ready Infrastructure**

---

**Last Updated:** 2025-11-06  
**Maintainer:** Danijel (ELION Team)  
**License:** Internal Use Only
