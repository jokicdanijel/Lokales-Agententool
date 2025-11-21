# 📂 PORTIER 3.0 — Repository Structure Guide

**Version:** 3.0.0  
**Date:** 21. November 2025  
**Purpose:** Complete guide to all folders, their purpose, and integration

---

## 🏢 Repository Overview

**PORTIER 3.0** ist ein modulares Multi-Agent-System mit 20+ spezialisierten Agenten, organisiert in einer klaren, skalierbaren Ordnerstruktur.

**Hauptpfad:**
```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
```

---

## 📁 Top-Level Struktur

### 1️⃣ **Kern-Service-Ordner (opena1-opena21)**

#### **1.opena1&2_portier/** — PORTIER Core Services ✅

**Zweck:** Koordinator, Archivator, Gateway (Kern des Option-2-Flow)

**Hauptkomponenten:**

```
1.opena1&2_portier/
├── opena1/                    # Coordinator Service
│   ├── koordinator.py         # Request71→Decision72 (120 LOC)
│   └── main_production.py     # FastAPI Entry (91 LOC)
│
├── opena2/                    # Archivator Service
│   └── opena2_app.py          # CMD/RESP Safepoints (212 LOC)
│
├── kordp/                     # Gateway Service
│   ├── main_production.py     # FastAPI Entry (91 LOC)
│   ├── router.py              # Route Handling (148 LOC)
│   └── tool_resolver.py       # Tool Resolution (186 LOC)
│
├── archivp_store/             # ✅ Safepoint Storage
│   ├── YYYY/MM/DD/            # Date-based partitions
│   │   ├── SP<TS>_opena1→archivp_CMD.json
│   │   └── SP<TS>_archivp→opena1_RESP.json
│   └── index.jsonl            # Append-only index
│
├── bin/                       # Operational Scripts
│   ├── start_stack.sh         # Start all PORTIER services
│   ├── stop_stack.sh          # Stop all services
│   ├── verify_stack.sh        # Integration verification
│   ├── check_ports.sh         # Port availability
│   └── env_bootstrap.sh       # .env token generation
│
├── tests/
│   └── test_portier_stack.py  # E2E Tests (450+ LOC)
│
└── venv313/                   # Python 3.13 Virtual Environment
```

**Ports:**
- opena1: 12344
- opena2: 12345
- kordp: 12346

**Status:** ✅ Running (Production)

---

#### **2.opena3_openwebui/** — OpenWebUI Terminal Agent ✅

**Zweck:** Chat-Interface, OpenWebUI Integration

**Hauptkomponenten:**

```
2.opena3_openwebui/
├── main_openwebui_agent.py    # FastAPI Wrapper (Port 12347)
├── openwebui_adapter.py       # HTTP Forwarder (Port 12350)
├── bin/
│   ├── start_opena3.sh
│   └── start_openwebui_adapter.sh
└── requirements.txt
```

**Ports:**
- opena3: 12347
- Adapter: 12350

**Status:** ✅ Running

---

#### **3.opena4_telegram/** — Telegram Bot 🟡

**Zweck:** Telegram API Integration, Bot Commands

**Struktur:**

```
3.opena4_telegram/
├── api/                       # Telegram Bot API
├── bin/                       # Start/Stop Scripts
├── config/
│   └── agent.conf             # Bot Configuration
├── data/                      # User data, chat logs
├── docs/                      # API Documentation
├── logs/                      # Runtime logs
└── requirements.txt
```

**Port:** 12348  
**Status:** 🟡 Planned (Struktur vorhanden)

---

#### **4.opena5_vscode/** — VS Code Integration 🟡

**Zweck:** Extension Host, Remote SSH, File Watcher

```
4.opena5_vscode/
├── api/
├── bin/
├── config/
├── data/
├── docs/
└── requirements.txt
```

**Port:** 12349 (Konflikt mit opena20, wird zu 12365 verschoben)  
**Status:** 🟡 Planned

---

#### **5.opena6_browser/** — Browser Automation 🟡

**Zweck:** Selenium/Playwright, Scraping, Testing

**Port:** 12350  
**Status:** 🟡 Planned

---

#### **6.opena7_email/** — E-Mail Client 🟡

**Zweck:** IMAP/SMTP, Inbox Monitoring, Templates

**Port:** 12351  
**Status:** 🟡 Planned

---

#### **7.opena8_whatsapp/** — WhatsApp API 🟡

**Zweck:** WhatsApp Business API, Message Queue

**Port:** 12352  
**Status:** 🟡 Planned

---

#### **8.opena9_telephone/** — Telefonie 🟡

**Zweck:** SIP/VoIP Integration, Call Logging

**Port:** 12353  
**Status:** 🟡 Planned

---

#### **9.opena10_call_tracking/** — Call Tracking 🟡

**Zweck:** Call Analytics, Recording, Transcription

**Port:** 12354  
**Status:** 🟡 Planned

---

#### **10.opena11_unlock/** — Unlock Master 🟡

**Zweck:** Password Manager Integration, Secret Vault

**Port:** 12355  
**Status:** 🟡 Planned

---

#### **11.opena12_social_media/** — Social Media 🟡

**Zweck:** Multi-Platform Posting (X, LinkedIn, etc.)

**Port:** 12356  
**Status:** 🟡 Planned

---

#### **12.opena13_influencer/** — Influencer 🟡

**Zweck:** Content Calendar, Analytics, Outreach

**Port:** 12357  
**Status:** 🟡 Planned

---

#### **13.opena14_calendar/** — Calendar 🟡

**Zweck:** Google Calendar, iCal Sync, Reminders

**Port:** 12358  
**Status:** 🟡 Planned

---

#### **14.opena15_html/** — HTML Creator 🟡

**Zweck:** Template Engine, Static Site Gen, Preview

**Port:** 12359  
**Status:** 🟡 Planned

---

#### **15.opena16_shop/** — Shop 🟡

**Zweck:** E-Commerce Integration, Product Catalog

**Port:** 12360  
**Status:** 🟡 Planned

---

#### **16.opena17_homepagecreator/** — Homepage Creator 🟡

**Zweck:** Website Builder, Template System

**Port:** 12361  
**Status:** 🟡 Planned

---

#### **17.opena18_CMR/** — CRM 🟡

**Zweck:** Contact Management, Sales Pipeline

**Port:** 12362  
**Status:** 🟡 Planned

**Hinweis:** Typo im Ordnernamen (sollte CRM sein)

---

#### **18.opena19_Aktien&Crypto/** — Aktien & Crypto 🟡

**Zweck:** Market Data, Portfolio Tracking, Alerts

**Port:** 12363  
**Status:** 🟡 Planned

---

#### **19.opena20_dashboard_agent/** — Dashboard ✅

**Zweck:** Live Monitoring UI, Status Grid, E2E Test Trigger

**Hauptkomponenten:**

```
19.opena20_dashboard_agent/
├── main.py                    # FastAPI App (67 LOC)
├── router.py                  # API Routes (137 LOC)
├── templates/
│   └── dashboard.html         # UI Template (73 LOC)
├── static/
│   ├── css/
│   │   └── dashboard.css      # Styles (214 LOC)
│   └── js/
│       └── dashboard.js       # Logic (219 LOC)
├── bin/
│   └── start_opena20.sh
└── requirements.txt
```

**Port:** 12349  
**Status:** ✅ Running (Production)

**Features:**
- Live Status Grid (alle Agenten)
- E2E Test Trigger
- Safepoint Inspector
- Activity Log (real-time)
- Auto-Refresh (5s)

---

#### **20.opena21_workflow/** — Workflow Engine 🟡

**Zweck:** Process Automation, Task Orchestration

**Port:** 12364  
**Status:** 🟡 Planned

---

### 2️⃣ **System-Ordner**

#### **.github/** — GitHub Configuration ✅

```
.github/
├── copilot-master-prompt.md      # Vollständiges System-Wissen (v2.0, 2000+ LOC)
├── copilot-instructions.md       # AI Integration Guide (200+ LOC)
├── COMPLETION_CHECKLIST.md       # Phase Tracking (40/40 Tasks ✅)
├── cpp-makefile-guide.md         # Build Documentation
├── pull_request_template.md      # PR Template
├── SYSTEM_ANALYSIS_BYPASS_MECHANISMS.md  # Security Analysis
└── workflows/
    └── ci.yml                    # GitHub Actions Pipeline
```

**Zweck:** Git-Konfiguration, CI/CD, AI-Prompts

---

#### **src/** — SCTA Shared Modules ✅

```
src/
├── agents/
│   ├── core_orchestrator/
│   └── worker_agents/
│       ├── planner/
│       └── executor/
├── api/
│   └── http/
├── pkg/
│   ├── shared/
│   │   ├── config.py             # Global Config (60 LOC)
│   │   ├── schemas.py            # Shared Schemas (150 LOC)
│   │   └── exceptions.py         # Custom Exceptions (80 LOC)
│   └── models/
└── services/
    └── agenda_api.py             # 16-Seiten Agenda API (260 LOC)
```

**Zweck:** SCTA (Structured Code Task Automation), Shared Modules

---

#### **docs/** — Documentation ✅

```
docs/
├── OPERATIONS.md                 # Runtime Commands
├── TROUBLESHOOTING.md            # Error Scenarios
├── OPENWEBUI_INTEGRATION.md      # opena3 Specs
├── OPENWEBUI_API.md              # Endpoint Specs
├── OPENWEBUI_TODO.md             # Backlog (30+ Items)
└── structure_runbook.md          # SCTA Architecture (500+ LOC)
```

**Zweck:** Systemdokumentation

---

#### **bin/** — Root-Level Scripts ✅

```
bin/
├── ops.sh                        # Main Orchestrator (start, stop, status, verify)
├── start_all.sh
├── stop_all.sh
├── verify_stack.sh
├── check_ports.sh
├── log_tail.sh
└── env_bootstrap.sh
```

**Zweck:** Operations, Stack Management

---

#### **scripts/** — Automation Scripts ✅

```
scripts/
├── register_agents.py            # Agent Registry Bootstrap
├── test_openwebui.py             # OpenWebUI Integration Tests
├── seed_openwebui.py             # Seed Data for opena3
└── curl_examples.sh              # API Test Examples
```

**Zweck:** Testing, Seeding, Automation

---

#### **configs/** — Configuration Files ✅

```
configs/
├── agenda_pages.json             # 16-Page Agenda Structure
├── tools_registry.json           # Tool Registry
└── routing_matrix.yaml           # Service Routing (optional)
```

**Zweck:** System Configuration

---

#### **tests/** — Test Suites ✅

```
tests/
├── test_portier_stack.py         # E2E Tests (in 1.opena1&2_portier/)
├── test_openwebui_agent.py       # OpenWebUI Tests (in 2.opena3_openwebui/)
└── test_archivator.py            # Archivator Tests
```

**Zweck:** Quality Assurance

---

#### **logs/** — Runtime Logs ✅

```
logs/
├── opena1.nohup.log
├── opena2.nohup.log
├── kordp.nohup.log
├── opena3.nohup.log
├── opena20.nohup.log
└── openwebui_adapter.nohup.log
```

**Zweck:** Debugging, Monitoring

---

#### **archivp/** — Safepoint Archive ✅

```
archivp/
├── YYYY/
│   └── MM/
│       └── DD/
│           ├── SP<TS>_opena1→archivp_CMD.json
│           └── SP<TS>_archivp→opena1_RESP.json
└── index.jsonl
```

**Zweck:** Unveränderliches Datenarchiv (Append-Only)

**Hinweis:** Duplicate von `1.opena1&2_portier/archivp_store/` (könnte konsolidiert werden)

---

### 3️⃣ **Konfigurations- & Build-Dateien**

#### **pyproject.toml** — Poetry Dependencies ✅

```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.0"
uvicorn = "^0.23.0"
pydantic = "^2.4.0"
# ... 27 packages total
```

**Zweck:** SCTA Dependency Management

---

#### **docker-compose.prod.yml** — Docker Stack 🟡

```yaml
version: '3.8'
services:
  opena1:
    build: ./1.opena1&2_portier
    ports:
      - "12344:12344"
  # ... weitere Services
```

**Zweck:** Production Deployment (geplant)

---

#### **Makefile** — Build Automation ✅

```makefile
start:
	bash bin/ops.sh start

stop:
	bash bin/ops.sh stop

test:
	pytest -v
```

**Zweck:** Convenience Commands

---

#### **.gitignore** — Git Ignore Patterns ✅

```
.env
*.log
__pycache__/
*.pyc
.pytest_cache/
venv*/
# ... 40+ patterns
```

**Zweck:** Secrets & Build Artifacts ausschließen

---

#### **.env.example** — Environment Template ✅

```bash
OPENAI_API_KEY=sk-...
BEARER_TOKEN=<uuid>
ARCHIVP_ROOT=/path/to/archivp
DB_PATH=/path/to/db.sqlite
# ... 18 fields total
```

**Zweck:** Environment Variable Guide

---

### 4️⃣ **Dokumentations-Dateien (Root)**

#### **README.md** — Main README ✅

**Inhalt:** Quick Start, Architektur, Port-Mapping, Operations  
**Zeilen:** ~700 LOC

---

#### **README_ENTERPRISE.md** — Enterprise Documentation ✅

**Inhalt:** 20-Seiten vollständiges Dossier (Executive Summary, Agenten-Register, Port-Registry, Ordnerstruktur, SCTA, Option-2-Flow, etc.)  
**Zeilen:** 5,890 LOC

---

#### **PORTIER_3.0_RELEASE.md** — Release Notes ✅

**Inhalt:** Release v3.0.0, Deliverables, E2E Testing, Metrics  
**Zeilen:** 511 LOC

---

#### **PORTIER_SYSTEM_DOCS.md** — System Documentation ✅

**Inhalt:** Complete Technical Docs (Architecture, APIs, Operations, Troubleshooting)  
**Zeilen:** 654 LOC

---

#### **SCTA_IMPLEMENTATION_CHECKPOINT.md** — SCTA Status ✅

**Inhalt:** Phases 1-3 Complete, Phases 4-10 Queued  
**Zeilen:** ~200 LOC

---

### 5️⃣ **Legacy & Backup Ordner**

```
_conflicts/                     # Merge-Konflikte (Backup)
archivp_store.backup.2025-11-11/ # Archiv-Backup
backups/                        # Weitere Backups
.runtime/pids/                  # PID-Files (Runtime)
htmlcov/                        # Coverage Reports
.pytest_cache/                  # Pytest Cache
__pycache__/                    # Python Bytecode
```

**Zweck:** Historische Daten, Backups, Build-Artefakte

---

## 📊 Ordner-Statistiken

| Typ | Anzahl | Zweck |
|-----|--------|-------|
| **Agenten** | 20 | opena1-opena21 (Service-Slots) |
| **✅ Running** | 5 | opena1, opena2, kordp, opena3, opena20 |
| **🟡 Planned** | 15 | opena4-opena21 (außer opena20) |
| **Systemordner** | 10+ | src/, docs/, bin/, scripts/, configs/, tests/, logs/ |
| **Konfigurationsdateien** | 6+ | pyproject.toml, Makefile, .env.example, etc. |
| **Hauptdokumente** | 5 | README.md, README_ENTERPRISE.md, PORTIER_*.md, SCTA_*.md |

---

## 🔗 Integrationspunkte

### **1. Option-2-Flow Integration**

```
opena1 (1.opena1&2_portier/) 
  → opena2 (1.opena1&2_portier/)
  → kordp (1.opena1&2_portier/)
  → Tools (3-21.opena*/)
```

### **2. Dashboard Integration**

```
opena20 (19.opena20_dashboard_agent/)
  → GET /api/status
  → opena1:12344/health
  → opena2:12345/health
  → kordp:12346/health
```

### **3. SCTA Integration**

```
src/ (Shared Modules)
  ← import von allen Agenten
  → agenda_api.py (16-Seiten System)
```

### **4. Archivp Integration**

```
opena2 (1.opena1&2_portier/opena2/)
  → archivp_store/ (YYYY/MM/DD/)
  → index.jsonl (append-only)
```

---

## 🚀 Navigation & Usage

### **Alle Services starten**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt
bin/ops.sh start
```

### **Einen Agent entwickeln**

```bash
# Template kopieren
cp -r 3.opena4_telegram/ 99.opena99_custom/

# In Agent-Ordner wechseln
cd 99.opena99_custom/

# Konfiguration anpassen
vim config/agent.conf

# Service starten
./bin/start.sh
```

### **Dokumentation lesen**

```bash
# Main README
less README.md

# Enterprise Docs (20 Seiten)
less README_ENTERPRISE.md

# System Docs
less PORTIER_SYSTEM_DOCS.md

# Operations Guide
less docs/OPERATIONS.md
```

---

## 📞 Support

**Issues:** https://github.com/jokicdanijel/Gesamtprojekt-start/issues  
**Docs:** https://github.com/jokicdanijel/Gesamtprojekt-start/wiki  
**Email:** contact@elion-tech.de (fiktiv)

---

**Last Updated:** 21. November 2025  
**Version:** 3.0.0  
**Maintainer:** Danijel Jokic (ELION Team)
