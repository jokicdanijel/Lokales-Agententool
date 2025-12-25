# 📦 Projektstruktur des ELION-Systems

**Detaillierte Dokumentation der Verzeichnisorganisation und Modulkomposition**

- 📅 **Datum:** 24. November 2025
- 🎯 **Zweck:** Referenz für Frontend-Entwickler und Projektmanager
- 📍 **Scope:** Nur Abschnitt 3 aus `ELION_SYSTEM_ARCHITECTURE.md`

---

## Projektstruktur

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
│   └── Runbook_EnvIntegration.md
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
├── ELION_SYSTEM_ARCHITECTURE.md         # Master-Architektur-Datei
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
| Portier-Pool (opena1–opena20) | 12344–12399 | Koordination & Services |
| OpenWebUI                     | 3000        | Frontend                |
| LocalAgent-Pro                | 8001        | API Server              |
| opena3-Bridge                 | 12347       | Safepoint-Hub           |
| Ollama                        | 11434       | AI-Models (optional)    |
| Prometheus                    | 9090        | Metriken (optional)     |

### Konfiguration und Secrets

Alle sensiblen Daten (OPENAI_API_KEY_VSCODE, TELEGRAM_BOT_TOKEN, GitHub-Secrets) befinden sich ausschließlich in `.env` oder CI/CD-Secrets, **niemals im Quellcode**. Skeleton-Dateien (`.env.example`) werden versioniert; echte `.env` gehört in `.gitignore`.

---

## 🔗 Weiterführende Dokumentation

- **Gesamtübersicht:** `../ELION_SYSTEM_ARCHITECTURE.md`
- **Datenstruktur:** `DATENSTRUKTUR.md`
- **Datenpfad:** `DATENPFAD.md`

---

**Letztes Update:** 24. November 2025
