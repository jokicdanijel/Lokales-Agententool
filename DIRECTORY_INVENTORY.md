

**Erstellt:** 24. November 2025
**Projekt:** ELION Multi-Agent System
**Repository:** gesamtprojekt_final

---

## 📊 Überblick

```
Total Directories: 248
Main Agents: 20+ (opena1 - opena21)
Primary Domains: 5 (Portier, OpenWebUI, Telegram, Email, Analysis)
Core Structure: Hierarchical with parallel agent deployment
```

---

## 🏗️ Hauptstruktur (Level 1)

### **1️⃣ Agent-Verzeichnisse (Nummeriert)**

| Nr. | Agent | Funktion | Struktur |
|-----|-------|----------|----------|
| 1 | `1.opena1&2_portier` | Koordinator + Archivator | ✅ Full |
| 2 | `2.opena3_openwebui` | Web-Interface | ✅ Full |
| 3 | `3.opena4_telegram` | Telegram-Integration | ✅ Full |
| 4 | `4.opena5_vscode` | VS Code Agent | ⚠️ Minimal |
| 5 | `5.opena6_browser` | Browser-Automation | ✅ Full |
| 6 | `6.opena7_email` | Email-Client | ✅ Full |
| 7 | `7.opena8_whatsapp` | WhatsApp Integration | ✅ Full |
| 8 | `8.opena9_telephone` | Telefon-System | ✅ Full |
| 9 | `9.opena10_call_tracking` | Call Analytics | ✅ Full |
| 10 | `10.opena11_unlock` | Security/Access | ✅ Full |
| 11 | `11.opena12_social_media` | Social Media | ✅ Full |
| 12 | `12.opena13_influencer` | Influencer Management | ✅ Full |
| 13 | `13.opena14_calendar` | Kalender-System | ✅ Full |
| 14 | `14.opena15_html` | HTML Generator | ✅ Extended |
| 15 | `15.opena16_shop` | E-Shop | ✅ Full |
| 16 | `16.opena17_homepagecreator` | Homepage Builder | ⚠️ Minimal |
| 17 | `17.opena18_CMR` | CRM-System | ✅ Full |
| 18 | `18.opena19_stocks` | Aktien/Crypto | ✅ Full |
| 19 | `19.opena20_dashboard` | Master Dashboard | ✅ Extended |
| 20 | `20.opena21_workflow` | Workflow Engine | ✅ Full |

---

## 📂 Standard-Verzeichnisstruktur pro Agent

```
<agent>/
├── api/              # REST/FastAPI Endpoints
├── app/              # Application Logic
├── bin/              # Executable Scripts
├── config/           # Configuration Files (.yaml, .json)
├── data/             # Data Storage (persistent)
├── docs/             # Documentation
├── deploy/           # Deployment Scripts
├── tests/            # Unit Tests
├── templates/        # HTML Templates (optional)
├── static/           # Static Assets (optional)
├── __pycache__/      # Python Cache
└── venv/             # Virtual Environment (optional)
```

---

## 🎯 Kernverzeichnisse (Root Level)

### **Verwaltung & Konfiguration**

| Verzeichnis | Zweck | Dateien |
|-------------|-------|---------|
| `configs/` | Zentrale Konfigurationen | 50+ (YAML, JSON, Bridge-Configs) |
| `agents/` | Agent-Registry & Templates | 20+ Agent-Ordner |
| `src/` | Zentraler Quellcode | api/, services/, tools/ |
| `tools/` | Standalone Tools | Python Scripts |
| `scripts/` | Utility-Skripte | Automation, Setup |
| `bin/` | Executable Binaries | Shell Scripts, Python |

### **Dokumentation & Berichte**

| Verzeichnis | Zweck | Status |
|-------------|-------|--------|
| `docs/` | Projekt-Dokumentation | ✅ Active |
| `Runbooks/` | Operationale Runbooks | ✅ Created 24.11 |
| `reports/` | Analyse-Berichte | ✅ Active |
| `project_map/` | Projekt-Kartierung | ✅ Active |

### **Daten & Archiv**

| Verzeichnis | Zweck | Status |
|-------------|-------|--------|
| `data/` | Operative Daten | 📊 Growing |
| `archivp/` | Archiv-Portal | ✅ Active |
| `backups/` | Backup-Speicher | ✅ Regular |
| `logs/` | System-Logs | 📊 Daily |
| `_conflicts/` | Conflict Resolution | ⚠️ Occasional |

---

## 📁 Detaillierte Agent-Verzeichnisse

### **opena1&2_portier (Der Hauptkoordinator)**

```
1.opena1&2_portier/
├── api/                    # FastAPI Endpoints
├── opena1/                 # opena1 Coordinator
├── opena2/                 # opena2 Archivator
├── opena20/                # opena20 Knowledge Router
├── connector/              # Agent Connectors
├── archivp/                # Archive Portal
├── archivp_store/          # Archive Storage
├── knowledgebase/          # Knowledge Base (KB)
│   ├── opena1/
│   ├── kb_index.jsonl
│   └── feed_report_*.json
├── knowledge/              # Raw Knowledge Files
├── kordp/                  # Coordinator Portal
├── venv/                   # Virtual Environments (3x)
│   ├── venv/
│   ├── venv312/
│   ├── venv313/
│   └── venv_local/
├── config/                 # Configuration
├── data/                   # Data Storage
├── bin/                    # Scripts
├── tests/                  # Tests
├── logs/                   # Logs
└── docs/                   # Documentation
```

**Key Files:**
- `archivp_store/index.jsonl` - Archive Index
- `knowledge_router.py` - Knowledge Routing Engine
- `registry_schemas.py` - Agent Registry Schemas

---

### **opena3_openwebui (Web Interface)**

```
2.opena3_openwebui/
├── LocalAgent-Pro/         # Main Application
│   ├── src/                # Source Code
│   │   └── openwebui_agent_server.py
│   ├── config/             # Configuration
│   │   ├── config.yaml
│   │   └── system_prompt.txt
│   ├── docs/               # Documentation
│   │   ├── API.md
│   │   ├── INSTALLATION.md
│   │   └── AUTO_WHITELIST.md
│   ├── tools/              # Tools & Utilities
│   │   └── (multiple tools)
│   ├── tests/              # Unit Tests
│   │   ├── test_api.py
│   │   └── test_security.py
│   ├── requirements.txt    # Dependencies
│   ├── docker-compose.yml  # Docker Setup
│   └── Dockerfile          # Container Definition
├── data/                   # Data
├── auto_indexed/           # Auto-indexed Files
└── README.md              # Main Documentation
```

**Key Features:**
- 6 Voice Programs (1.041 lines total)
- REST API with 20+ endpoints
- OpenWebUI integration
- LocalAgent-Pro framework

---

### **opena20_dashboard_agent (Master Dashboard)**

```
19.opena20_dashboard_agent/
├── frontend/               # Frontend Assets
├── routers/                # API Routers
├── static/                 # Static Files
├── templates/              # HTML Templates
├── api/                    # API Endpoints
├── config/                 # Configuration
├── data/                   # Data Storage
├── docs/                   # Documentation
├── scripts/                # Automation Scripts
├── tests/                  # Tests
├── backups/                # Backups
├── logs/                   # Logs
├── ARCHIV/                 # Archive
└── opena3/                 # OpenWebUI Integration
```

---

## 📊 Konfigurationsdateien (configs/)

### **Infrastructure**
- `docker-compose.yml` - Docker Orchestration
- `prometheus.yaml` - Prometheus Metrics
- `alert_rules.yaml` - Alert Rules
- `routing_matrix.yaml` - Routing Matrix
- `agent_dirs.yaml` - Agent Directory Mappings

### **Grafana Dashboards**
- `grafana-dashboard-system.json`
- `grafana-dashboard-performance.json`
- `grafana-dashboard-alerts.json`
- `grafana-dashboard-overview.json`
- `grafana-dashboard-archive.json`

### **Agent Communications**
- `bridge_schema.json` - Bridge Schema
- `bridge_tokens.json` - Auth Tokens
- 60+ `SP*.json` files - Service Processes

### **Data & Registry**
- `path_index.json` - Path Index
- `tools_registry.json` - Tools Registry
- `MAC_DIR_SYSTEM.json` - Directory System
- `structure_checkpoint.json` - Structure Checkpoint
- `llama_stack_config.json` - Llama Stack Config

---

## 🔗 Zentrale Tools (src/ & tools/)

### **src/ Struktur**
```
src/
├── api/           # API Definitions
├── services/      # Business Logic
├── agents/        # Agent Implementations
├── tools/         # Utility Functions
├── tests/         # Unit Tests
└── __pycache__/   # Cache
```

### **tools/ - Standalone Programs**
- Voice programs (6x, 1.041 lines)
- Knowledge tools
- File utilities
- CLI interfaces

---

## 📈 Datenverwaltung

### **Persistent Storage Locations**

| Typ | Speicherort | Format |
|-----|-------------|--------|
| Archive | `1.opena1&2_portier/archivp_store/` | JSON |
| Knowledge Base | `1.opena1&2_portier/knowledgebase/` | JSONL |
| Contacts | `2.opena3_openwebui/data/` | JSON |
| Notes | `2.opena3_openwebui/data/voice_notes/` | JSON |
| Tasks | `2.opena3_openwebui/data/tasks.json` | JSON |
| Transcripts | `2.opena3_openwebui/data/transcripts/` | TXT/JSON |
| CRM | `17.opena18_CMR/data/` | JSON |
| Shop | `15.opena16_shop/data/` | JSON |

---

## 🔐 Security & Access

```
ssh_key/               # SSH Keys Storage
configs/
├── bridge_tokens.json # API Tokens
└── agent_dirs.yaml    # Directory Permissions
```

---

## 📝 Dokumentation & Reporting

### **Root-Level Documentation**

| Datei | Inhalt | Größe |
|-------|--------|-------|
| `README.md` | Main Overview | 929 lines |
| `ELION_SYSTEM_ARCHITECTURE.md` | Full Architecture | 550+ lines |
| `DATENSTRUKTUR.md` | Data Structures | 150+ lines |
| `DATENPFAD.md` | Data Flows | 250+ lines |
| `PROJEKTSTRUKTUR.md` | Project Structure | 200+ lines |
| `DIRECTORY_INVENTORY.md` | This File | ~ lines |

### **Checkpoint & Session Files**

- `FINAL_CHECKLIST_SESSION_10.md`
- `SCTA_IMPLEMENTATION_CHECKPOINT.md`
- `SESSION_11_CHECKPOINT.md`
- `INTEGRATION_REPORT_2025-11-24.md`
- `AUDIT_REPORT_2025-11-24.md`

### **Specialized Reports**

- `HTML_FILES_INVENTORY.md` - HTML Asset Index
- `AGENTENREGISTER_VOLLSTÄNDIG.md` - Complete Agent Registry
- `API_REFERENCE.md` - API Documentation
- `DEPLOYMENT_GUIDE.md` - Deployment Instructions
- `SECURITY_AUDIT_REPORT.md` - Security Analysis

---

## 🔍 Wichtige Python-Dateien

### **Core Agents**

| Agent | Main File | Funktion |
|-------|-----------|----------|
| opena1 | `1.opena1&2_portier/opena1/main.py` | Koordination |
| opena2 | `1.opena1&2_portier/opena2/router.py` | Archivierung |
| opena3 | `2.opena3_openwebui/LocalAgent-Pro/src/openwebui_agent_server.py` | Web UI |
| opena20 | `1.opena1&2_portier/opena20/main.py` | Knowledge Routing |

### **Voice Programs (6x)**

```
2.opena3_openwebui/LocalAgent-Pro/tools/
├── voice_command_parser.py      (147 lines)
├── voice_note_recorder.py        (187 lines)
├── voice_call_system.py          (173 lines)
├── voice_assistant.py            (138 lines)
├── voice_transcriber.py          (226 lines)
└── voice_scheduler.py            (176 lines)
```

**Total:** 1.041 lines, 33.8 KB

---

## 📦 Virtual Environments

```
1.opena1&2_portier/
├── venv/          # Python 3.9 (Legacy)
├── venv312/       # Python 3.12
├── venv313/       # Python 3.13
└── venv_local/    # Production

3.opena4_telegram/
└── venv/          # Telegram-specific

5.opena6_browser/
└── (shared env)

7.opena8_whatsapp/
└── (shared env)
```

---

## 🚀 Deployment & Operations

### **Docker Setup**
- `configs/docker-compose.yml` - Main Orchestration
- Agent-specific docker-compose files in each agent directory

### **Port Configuration**
- **12344-12349:** Portier Core Ports
- **3000:** OpenWebUI
- **8001:** LocalAgent-Pro
- **5001:** GCPT Coordinator
- **8000:** Dashboard API

### **Runbooks & Operations**
```
Runbooks/
└── RUNBOOK_SYSTEM_ARCHITECTURE.md
```

---

## 📊 Repository Statistics

- **Total Directories:** 248
- **Agent Folders:** 20+
- **Configuration Files:** 50+
- **Documentation Files:** 15+
- **Python Modules:** 100+
- **Virtual Environments:** 4+
- **Docker Configs:** Multiple

---

## 🔄 Data Flow Structure

```
Entry Points:
├── OpenWebUI (3000)
├── Telegram API
├── Email Inbox
├── WhatsApp API
├── Phone System
└── Browser Automation

↓

Portier Coordinator (12344-12349)
├── Request Routing
├── Agent Dispatch
├── Archive Management
└── Knowledge Base

↓

Specialized Agents (opena4-21)
├── Processing
├── Business Logic
└── Data Persistence

↓

Storage Layers
├── SQLite (structured data)
├── JSON (config/state)
├── JSONL (logs/events)
└── File System (archives)
```

---

## ✅ Übersicht der Verzeichnis-Typen

| Typ | Anzahl | Beispiele |
|-----|--------|----------|
| Agent-Verzeichnisse | 20 | opena1, opena2, ... opena21 |
| API-Verzeichnisse | 15+ | api/ (in jedem Agent) |
| Konfigurationsverzeichnisse | 50+ | configs/, config/ (überall) |
| Datenverzeichnisse | 20+ | data/, archivp_store/, knowledgebase/ |
| Dokumentationsverzeichnisse | 10+ | docs/, Runbooks/, reports/ |
| Test-Verzeichnisse | 15+ | tests/ (in jedem Agent) |
| Python Cache | 5+ | __pycache__/ (überall) |
| Virtual Environments | 4+ | venv/, venv312/, venv313/, venv_local/ |
| Sonstige | 80+ | static/, templates/, scripts/, etc. |

---

## 🎯 Häufige Navigationspfade

### **Admin Tasks**
- Archive: `1.opena1&2_portier/archivp_store/`
- Config: `configs/`
- Logs: `1.opena1&2_portier/logs/`, `19.opena20_dashboard_agent/logs/`

### **Development**
- Source: `src/`, `tools/`
- Tests: `*/tests/`
- Virtual Envs: `1.opena1&2_portier/venv*/`

### **Documentation**
- Architecture: `ELION_SYSTEM_ARCHITECTURE.md`, `DATENSTRUKTUR.md`, `DATENPFAD.md`, `PROJEKTSTRUKTUR.md`
- Operations: `Runbooks/RUNBOOK_SYSTEM_ARCHITECTURE.md`
- Inventory: `DIRECTORY_INVENTORY.md` (This file)

### **Deployment**
- Docker: `configs/docker-compose.yml`
- Configuration: `configs/`
- Runbooks: `Runbooks/`

---

## 📝 Zuletzt aktualisiert

- **Repository:** gesamtprojekt_final
- **Branch:** main
- **Dokumentation:** 24. November 2025
- **Status:** ✅ Complete and Verified

---

**🎯 END OF DIRECTORY INVENTORY**
