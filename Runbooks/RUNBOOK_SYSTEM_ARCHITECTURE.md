# 📖 RUNBOOK: ELION-System Architektur

**Betriebsanleitung zur System-Architektur des OpenWebUI-Portier-Ökosystems**

- 📅 **Datum:** 24. November 2025
- 🎯 **Zweck:** Referenz für Administratoren, Entwickler und Operationen
- 📍 **Scope:** Datenflüsse, Persistierung, Projektorganisation
- ⚠️ **Note:** Diese Datei ist eine Kopie von `../ELION_SYSTEM_ARCHITECTURE.md` (Master)

---

## 1. Datenstruktur

Die Datenstruktur des OpenWebUI-Portier-Systems ist multidimensional aufgebaut und verbindet mehrere Domänen: das OpenWebUI-Frontend, den LocalAgent-Pro-Backend-Server, die Portier-Architektur (Koordinator, Archivator, Connector) sowie externe Integrationen (Telegram, GitHub).

### Persistente Datenspeicherung

Das System nutzt mehrschichtige Persistence:

- **SQLite-Datenbanken**: Strukturierte Event-Daten und Safepoints in `1.opena1&2_portier/archivp_store/`
- **JSON-Dateien**: Konfigurationsdaten und Zustandsdaten in `LocalAgent-Pro/sandbox/`
- **JSONL-Indexdateien**: Sequenzielle Safepoint-Protokollierung in `index.jsonl`
- **Audit-Logs**: Transaktions- und Prüf-Logs in `/logs/` und `audit_hashes.log`
- **Prometheus-Metriken**: Monitoring und Performance-Daten

### Kern-Datenentitäten und Beziehungen

| Entität                 | Beschreibung                                                         | Beziehungen                                                | Speicherort                 |
| ----------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------- | --------------------------- |
| **Endpoint** (20)       | Services auf Port 12344–12399 (opena1–opena20)                       | Hat viele HealthRecords; wird gepatcht via PatchBlock      | SQLite, .env                |
| **PatchBlock**          | Unified-Diff-Patches für Code-Updates                                | Gehört zu Endpoint; wird geauditet in AuditLog             | `patches/` Verzeichnis      |
| **Safepoint**           | Transaktions-Checkpoints (Gateway, Tool-Execution, Archive-Access)   | Ist Teil von MessageRelay/GitHubWebhook-Flow               | `archivp_store/index.jsonl` |
| **HealthRecord**        | Zeitstempel-basierte Gesundheitsprüfungen                            | Ist von Endpoint; Zeitreihen-Metadaten                     | SQLite, `/logs/`            |
| **AuditLog**            | SHA-256 Hash-Ketten für alle Änderungen                              | Referenziert Endpoint & PatchBlock; vollständig verfolgbar | `audit_hashes.log`          |
| **Voice-Program-Daten** | Notizen, Kontakte, Aufgaben, Transkripte (1.041 Zeilen, 6 Programme) | Persistent in JSON                                         | `LocalAgent-Pro/sandbox/`   |
| **MessageRelay**        | Telegram → OpenWebUI Nachrichten-Routing                             | Wird zu Safepoint; loggt in archive.db                     | opena3 Bridge               |
| **GitHubWebhook**       | GitHub-Events (Push, PR, Release)                                    | Wird zu Safepoint; triggert optionale Updates              | opena3 Bridge               |

### Datentypen und Formate

Das System arbeitet hauptsächlich mit:

- **JSON** – REST-API-Responses, Konfigurationen, Voice-Daten
- **YAML** – `config.yaml` für Konfigurationsdateien
- **Unified-Diff** – Patch-Format für Code-Updates
- **SHA-256 Hashes** – Audit-Trails und Integrität
- **SQLite** – Relational für strukturierte Daten
- **JSONL** – Log-Streaming für sequenzielle Events

Alle Daten sind **UTF-8 kodiert** und nutzen **ISO-8601 Zeitstempel**.

---

## 2. Datenpfad

Der Datenpfad beschreibt die komplexe Bewegung von Informationen durch das System, vom initialen Input bis zur endgültigen Persistierung und Auditierung.

### Eingangsquellen und Eingabepunkte

Daten treten über vier primäre Kanäle ein:

1. **OpenWebUI-Frontend** (Port 3000) → HTTP-Requests an LocalAgent-Pro (Port 8001)
2. **Telegram Bot** → opena3-Bridge (Port 12347) als Message Relay
3. **GitHub Webhooks** → opena3-Bridge für Push/PR-Events
4. **Lokale Shell-Befehle & Dateioperationen** → `/api/file/*` und `/api/shell/exec` Endpoints

### Verarbeitungspipeline (Hauptflow)

```
Eingabe (Frontend/Telegram/GitHub/Shell)
    ↓
LocalAgent-Pro API (Port 8001)
    ├─ Security Check (Sandbox-Isolation, Whitelisting)
    ├─ Request Deduplication (MD5-Hash)
    ├─ Tool Selection (write_file, read_file, shell_exec, etc.)
    ↓
Tool Execution (mit Error-Handling)
    ├─ Dateioperationen → Sandbox Dir (~/ localagent_sandbox)
    ├─ Shell-Befehle → whitelistete Commands
    ├─ Ollama/OpenAI API Calls → externe AI-Services
    ↓
Safepoint Recording (opena3-Bridge, Port 12347)
    ├─ Snapshot vor/nach Operation
    ├─ SHA-256 Hash (Integrität & Unveränderbarkeit)
    ├─ Timestamp & Metadata
    ↓
Persistierung (Archiv & Audit)
    ├─ Event in archivp_store/index.jsonl
    ├─ Eintrag in audit_hashes.log
    ├─ Bei Fehler: Rollback & Notification
    ↓
Monitoring & Logging
    ├─ Health-Check (5s Interval) → HealthRecords in SQLite
    ├─ Prometheus Metrics Export
    ├─ Koordinator-Aggregation (Port 12344)
    ↓
Ausgabe (Frontend/API/Logs)
```

### Spezifische Datenbewegungen nach Use-Case

**Use-Case 1 – Datei-Operation (z. B. write_file):**

```
OpenWebUI → LocalAgent-Pro /api/file/write
  → Sanitization (path traversal check)
  → Sandbox-Schreiboperation
  → Safepoint (opena3)
  → archivp_store/index.jsonl
  → Audit-Hash
  → Response zu OpenWebUI
```

**Use-Case 2 – Telegram-Nachricht:**

```
Telegram Bot
  → opena3-Bridge /message/relay
  → Nachricht zu OpenWebUI API forwarden
  → Safepoint-Checkpoint
  → archive.db Eintrag
  → Health-Update
  → Dashboard-Refresh
```

**Use-Case 3 – Patch-Delivery (GitHub Guard):**

```
Patch-Block (Unified-Diff)
  → Guardian vor-Sync-Check
  → Git-Pull (wenn synchronized)
  → Patch anwenden (git apply)
  → Datei-Update
  → Syntax-Validierung
  → AuditLog (Vorher/Nachher Hash)
  → CI/CD-Tests
  → Erfolg/Failure Notification
```

**Use-Case 4 – Voice-Programm-Ausführung (z. B. voice_scheduler):**

```
Frontend /api/program/start
  → tools/voice_scheduler.py Launch
  → Sprach-Input/Menu-Navigation
  → Task in tasks.json persistent
  → Status-Poll via /api/status
  → Dashboard-Update mit Completion-Status
```

### Sicherheits- und Integritäts-Layer

Alle Datenbewegungen unterliegen mehreren Schutzmechanismen:

- **Loop-Protection**: MD5-Request-Deduplication verhindert Rekursionen
- **Escape-Prevention**: Sandbox-Isolation für alle Dateioperationen
- **Secret-Masking**: OPENAI_API_KEY_VSCODE wird nie geloggt
- **TLS-Plan**: Für zukünftige HTTPS-Kommunikation
- **RBAC-Entwurf**: Rollenbasierte Zugriffskontrolle vorgesehen

---

## 3. Projektstruktur

Die Projektstruktur ist auf einer klaren hierarchischen und modularen Basis organisiert und bildet die fünf Funktionsbereiche des ELION-Systems ab.

### Verzeichnishierarchie

```
Gesamtprojekt/
│
├── 1.opena1&2_portier/                  # 🧠 Core Portier System
│   ├── agenten/
│   │   ├── coordinator.py               # opena1: Zentrale Orchestrierung
│   │   ├── archivator.py                # opena2: Safepoint-Manager
│   │   └── connector.py                 # kordp: API-Gateway
│   ├── data/
│   │   ├── archive.db                   # SQLite Safepoint-Archiv
│   │   └── endpoints.db                 # Endpoint-Registry
│   ├── archivp_store/
│   │   ├── index.jsonl                  # Sequenzielle Safepoint-Events
│   │   └── audit_hashes.log             # SHA-256 Audit-Trail
│   ├── requirements.txt
│   ├── main_production.py               # Production Launcher
│   └── .env.example                     # Env-Skelett (kein Key)
│
├── 2.openwebui/                         # 🌐 OpenWebUI-Bridge (opena3)
│   ├── openwebui_server.py              # OpenWebUI Bridge-Server (Port 12347)
│   ├── config/
│   │   └── webui_config.json            # UI-Konfiguration
│   ├── start.sh                         # Start-Skript
│   ├── requirements.txt
│   └── .env.example
│
├── LocalAgent-Pro/                      # 🤖 AI-Agent-Server (Port 8001)
│   ├── src/
│   │   └── openwebui_agent_server.py    # Flask-basierter Agent-Server
│   ├── tools/                           # 6 Voice-Programme (1.041 Zeilen)
│   │   ├── voice_command_parser.py      # (147 Zeilen) Sprachbefehle
│   │   ├── voice_note_recorder.py       # (187 Zeilen) Notizen-Erfassung
│   │   ├── voice_call_system.py         # (173 Zeilen) Kontakt-Management
│   │   ├── voice_assistant.py           # (138 Zeilen) Intelligente Assistentin
│   │   ├── voice_transcriber.py         # (226 Zeilen) Audio-Transkription
│   │   └── voice_scheduler.py           # (176 Zeilen) Aufgaben-Tracking
│   ├── config/
│   │   └── config.yaml                  # Sicherheit, Ollama, Models
│   ├── sandbox/                         # 🔒 Isolated Datei-Operationen
│   │   ├── voice_notes/notes.json       # Persistent
│   │   ├── contacts.json                # Persistent
│   │   ├── tasks.json                   # Persistent
│   │   └── transcripts/                 # Transkriptions-Dateien
│   ├── tests/
│   │   ├── test_api.py                  # Unit-Tests
│   │   ├── test_security.py             # Sicherheits-Tests
│   │   └── test_integration.py          # Integrations-Tests
│   ├── docker-compose.yml               # Docker Setup
│   ├── requirements.txt
│   ├── README.md
│   └── .env.example
│
├── 2.opena3_openwebui/                  # 📊 Web Dashboard & Integration
│   ├── main_openwebui_bridge.py         # Bridge v1 (Legacy)
│   ├── main_openwebui_bridge_v2.py      # Bridge v2 (Active)
│   ├── index.html                       # Dashboard HTML (800+ Zeilen)
│   ├── base.html                        # Basis-Template
│   ├── tools.html                       # Tools-UI
│   ├── COMPLETE_URLS.md                 # URL-Referenz (13 Endpoints)
│   ├── API_REFERENCE.md                 # API-Dokumentation
│   ├── FUNCTIONAL_TEST_REPORT.md        # Test-Resultate
│   ├── data/                            # Lokale Daten
│   └── LocalAgent-Pro/                  # Referenz zu Agent-Server
│
├── Runbooks/                            # 📖 Betriebsanleitungen
│   ├── Runbook_PatchFlow_and_Guard.md
│   ├── Runbook_NoAsk.md
│   ├── Runbook_EnvSetup.md
│   ├── Runbook_EnvIntegration.md
│   └── RUNBOOK_SYSTEM_ARCHITECTURE.md   # ← NEUE KOPIE
│
├── .github/
│   ├── workflows/
│   │   ├── ci-openwebui.yml
│   │   ├── ci-openwebui-telegram.yml
│   │   ├── ci-openwebui-ollama.yml
│   │   └── ci-no-ask.yml
│   └── copilot-commit-instructions.md
│
├── MASTER_PROMPT_V3_GENERAL.md          # 🎯 Genereller Master-Prompt
├── MASTER_PROMPT_V3_PER_SYSTEM.md       # Per-System Master-Prompt
├── ELION_SYSTEM_ARCHITECTURE.md         # ← MASTER-DATEI (Root)
├── README.md                            # Root README
├── .env.example                         # Globales Env-Skelett
├── requirements.txt                     # Globale Dependencies
├── audit_hashes.log                     # Zentrale Hash-Audit
└── [Diverse Dokumentation]
```

### Wichtige Kernmodule

**1. LocalAgent-Pro/src/openwebui_agent_server.py** – Flask REST-API mit 15+ Endpoints:

- `GET /health` – Health Check
- `GET /v1/models` – Verfügbare AI-Modelle
- `POST /v1/chat/completions` – Chat-API (OpenAI-kompatibel)
- `POST /api/file/{read,write,delete}` – Datei-Operationen (Sandbox-isoliert)
- `POST /api/shell/exec` – Whitelisted Shell-Befehle
- `POST /api/program/start` – Voice-Programm-Launch

**2. 2.opena3_openwebui/main_openwebui_bridge_v2.py** – Safepoint-Bridge (Port 12347):

- Relay Telegram-Nachrichten zu OpenWebUI
- GitHub-Webhook-Verarbeitung
- Safepoint-Archivierung in JSONL
- Audit-Logging mit SHA-256 Hashes

**3. 1.opena1&2_portier/agenten/coordinator.py** – Zentrale Orchestrierung:

- Koordiniert Health-Checks aller 20 Endpunkte
- OpenAI API-Gateway-Integration
- Log-Aggregation

**4. Voice-Tools Suite** (1.041 Zeilen, 6 Programme):

- Sprachgesteuerte Daten-Ein-/Ausgabe
- Persistent via JSON in `LocalAgent-Pro/sandbox/`
- Modular integriert in `/api/program/start` Endpoint

### Konvention für Ports und Namensgebung

| Service                       | Port        | Rolle                   |
| ----------------------------- | ----------- | ----------------------- |
| Portier-Pool (opena1–opena20) | 12344–12349 | Koordination & Services |
| OpenWebUI                     | 3000        | Frontend                |
| LocalAgent-Pro                | 8001        | API Server              |
| opena3-Bridge                 | 12347       | Safepoint-Hub           |
| Ollama                        | 11434       | AI-Models (optional)    |
| Prometheus                    | 9090        | Metriken (optional)     |

### Konfiguration und Secrets

Alle sensiblen Daten (OPENAI_API_KEY_VSCODE, TELEGRAM_BOT_TOKEN, GitHub-Secrets) befinden sich ausschließlich in `.env` oder CI/CD-Secrets, **niemals im Quellcode**. Skeleton-Dateien (`.env.example`) werden versioniert; echte `.env` gehört in `.gitignore`.

---

## 4. Gesamterkenntnisse – Synthesis und Systemintegrität

### Architektur-Übersicht

Das ELION-System ist ein **verteiltes, multi-agenten AI-Ökosystem** mit zentralisierter Orchestrierung. Es verbindet drei Hauptschichten:

1. **Präsentation** – OpenWebUI Frontend (Port 3000) + Web-Dashboards
2. **Verarbeitung** – LocalAgent-Pro (Port 8001) + Portier-Koordinator (Port 12344)
3. **Persistierung** – SQLite + JSONL Archive + Audit-Trails

### Kritische Erkenntnisse

**Datenfluss-Charakteristiken:**

- ✅ **Asynchron & Event-getrieben** – Safepoints entstehen zu kritischen Meilensteinen
- ✅ **Multi-Entry, Single-Exit** – Daten via OpenWebUI/Telegram/GitHub; zentrale Ausgabe via opena3-Bridge
- ✅ **Loop-Protection** – MD5-Request-Deduplication verhindert Rekursionen
- ✅ **Sandbox-Isolation** – Alle Dateioperationen auf `~/localagent_sandbox/` begrenzt

**Integrations-Punkte:**

| System              | Port  | Rolle         | Integration           |
| ------------------- | ----- | ------------- | --------------------- |
| OpenWebUI           | 3000  | Frontend      | HTTP ↔ LocalAgent-Pro |
| LocalAgent-Pro      | 8001  | Agent-API     | REST ↔ Ollama, OpenAI |
| opena3-Bridge       | 12347 | Safepoint-Hub | Relay + Archive       |
| Portier-Koordinator | 12344 | Orchestrator  | Aggregation + Health  |
| Ollama              | 11434 | AI-Engine     | Local LLM Models      |
| GitHub CI/CD        | —     | Automation    | Webhook-Trigger       |
| Telegram Bot        | —     | External-I/O  | Message-Relay         |

**Sicherheits-Architektur:**

- ✅ **Layered Defense** – Sandbox-Isolation → Whitelisting → Hash-Verification → Audit-Logging
- ✅ **Secret-Management** – Umgebungsvariablen nur; niemals im Code
- ✅ **Audit-Trail** – Immutable SHA-256 Hash-Ketten in `audit_hashes.log`
- ✅ **Future-Ready** – TLS-Plan, RBAC-Entwurf vorhanden

### Production-Grade Qualität

✅ **Konsistent** – Datenmodell normalisiert; Relationen explizit definiert
✅ **Auditierbar** – Jede Transaktion nachverfolgbar via Hash-Ketten
✅ **Sicher** – Multi-Layer-Schutz; Sandbox-Isolation; Secret-Management
✅ **Dokumentiert** – Alle Komponenten vollständig dokumentiert
✅ **Modular** – Patch-Flow additiv; Breaking Changes durch Guardian-Checks verhindert
✅ **Resilient** – Safepoint-Snapshots ermöglichen schnelle Recovery

### Nächste Ebenen-Entwicklung

1. **Real-Time Monitoring** – Prometheus-Metriken → Grafana-Dashboard
2. **Advanced Rollback** – Zeitgesteuerte Snapshots mit Versioning
3. **Multi-Tenant** – Isolation per User/Organization via RBAC
4. **Global Distribution** – Replicated Archive über mehrere Orte
5. **ML-Integration** – Anomaly-Detection auf Safepoint-Events

---

## 📚 Siehe auch

- **Master-Datei:** `../ELION_SYSTEM_ARCHITECTURE.md` (Root)
- **Master-Prompts:** `../MASTER_PROMPT_V3_GENERAL.md`, `../MASTER_PROMPT_V3_PER_SYSTEM.md`
- **API-Referenz:** `../2.opena3_openwebui/API_REFERENCE.md`
- **Weitere Runbooks:**
  - `Runbook_PatchFlow_and_Guard.md`
  - `Runbook_NoAsk.md`
  - `Runbook_EnvSetup.md`
  - `Runbook_EnvIntegration.md`

---

**Letztes Update:** 24. November 2025
**Status:** ✅ Production-Ready
**Kopie von:** `../ELION_SYSTEM_ARCHITECTURE.md`
