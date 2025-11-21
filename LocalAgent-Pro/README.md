# LocalAgent-Pro v1.0

**Production-Ready AI Agent Server** mit Tool-Execution, Sandbox-Isolation und Prometheus-Monitoring.

[![GitHub Release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://github.com/jokicdanijel/Lokales-Agententool/releases/tag/v1.0.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](#testing)
[![Coverage](https://img.shields.io/badge/coverage-80%25-green.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](#docker-deployment)

---

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Schnellstart](#schnellstart)
- [Installation](#installation)
- [Verwendung](#verwendung)
- [API-Dokumentation](#api-dokumentation)
- [Docker-Deployment](#docker-deployment)
- [Testing](#testing)
- [Security](#security)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Projekt-Status](#projekt-status)
- [Lizenz](#lizenz)

---

## 🎯 Überblick

**LocalAgent-Pro** ist ein intelligenter AI-Agent-Server, kompatibel mit **OpenWebUI**, der folgende Aufgaben autonom ausführen kann:

- 📝 **Datei-Management:** Dateien lesen, schreiben, löschen (in Sandbox)
- 🔧 **Shell-Befehle:** Sichere Ausführung whitelisteter Befehle (`ls`, `cat`, `grep`, etc.)
- 🌐 **Webseiten abrufen:** HTTP-Requests an vertrauenswürdige Domains
- 🔒 **Loop-Protection:** MD5-basierte Request-Deduplizierung mit 2s Timeout
- 📊 **Prometheus-Metriken:** 33 Metriken für Monitoring

**Basiert auf:**

- **Ollama** (llama3.1:8b-instruct-q4_K_M)
- **Flask** (OpenAI-kompatible API)
- **Python 3.10+**

---

## ✨ Features

### Core-Funktionalität

✅ **OpenAI-kompatible Chat-API** (`/v1/chat/completions`)  
✅ **Tool-basierte Architektur** (write_file, read_file, delete_file, shell_exec, fetch_webpage)  
✅ **Sandbox-Isolation** (alle Dateioperationen in `/sandbox`)  
✅ **Loop-Protection** (MD5-basierte Request-Deduplizierung, 2s Timeout)  
✅ **Shell-Whitelisting** (nur sichere Befehle: ls, cat, grep, find, etc.)  
✅ **Domain-Whitelisting** (nur vertrauenswürdige Domains)

### Sicherheit

✅ **Escape-Prevention** (kein `../` in Dateinamen)  
✅ **Symlink-Blocking** (keine Symlinks in Sandbox)  
✅ **Dangerous-Commands-Filter** (rm -rf, sudo, dd blockiert)  
✅ **Non-root User** (Docker-Container läuft als `localagent`)  
✅ **Security-Audit-Script** (Bandit, Safety, pip-audit)

### Monitoring

✅ **Prometheus-Integration** (33 Metriken)  
✅ **Grafana-Dashboard** (Template verfügbar)  
✅ **Health-Check-Endpoint** (`/health`)  
✅ **Strukturiertes Logging** (DEBUG/INFO/WARNING/ERROR)

### Testing

✅ **100+ Unit-Tests** (pytest-basiert)  
✅ **10+ Integration-Tests** (End-to-End-Workflows)  
✅ **CI/CD-Pipeline** (GitHub Actions mit Matrix-Tests Python 3.10/3.11/3.12)  
✅ **Coverage-Report** (≥80% Ziel)

### Deployment

✅ **Docker-Container** (Multi-Stage Dockerfile, ~200MB)  
✅ **docker-compose** (4 Services: LocalAgent-Pro, Ollama, Prometheus, Grafana)  
✅ **Systemd-Service** (Auto-Start beim Booten)

---

## 🚀 Schnellstart

### 1. Manuelle Installation (5 Minuten)

```bash
# Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # oder: source ../venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Ollama starten (in separatem Terminal)
ollama serve

# Modell installieren
ollama pull llama3.1:8b-instruct-q4_K_M

# Server starten
python src/openwebui_agent_server.py
```

**Server läuft auf:** <http://localhost:8001>

### 2. Docker-Installation (1 Minute)

```bash
cd LocalAgent-Pro
docker-compose up -d
```

**Services:**

- LocalAgent-Pro: <http://localhost:8001>
- Ollama: <http://localhost:11434>
- Prometheus: <http://localhost:9090> (optional)
- Grafana: <http://localhost:3001> (optional)

### 3. Systemd-Service (Auto-Start)

```bash
sudo ./install_systemd_service.sh
```

---

## 📦 Installation

### Voraussetzungen

- **Python:** 3.10+ (getestet mit 3.10, 3.11, 3.12)
- **Ollama:** Installiert und laufend
- **Git:** Für Repository-Klonen
- **Docker:** Optional für Container-Deployment

### Schritt-für-Schritt-Anleitung

**Siehe:** [INSTALLATION.md](INSTALLATION.md)

**Kurzversion:**

```bash
# 1. Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro

# 2. Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Ollama starten
ollama serve &

# 5. Modell installieren
ollama pull llama3.1:8b-instruct-q4_K_M

# 6. Server starten
python src/openwebui_agent_server.py
```

---

## 💻 Verwendung

### Chat-Request senden

```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [
      {"role": "user", "content": "Erstelle eine Datei hello.txt mit Inhalt Hello World"}
    ]
  }'
```

### Health-Check

```bash
curl http://localhost:8001/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T10:30:00Z",
  "ollama_connected": true,
  "sandbox_path": "/home/user/localagent_sandbox"
}
```

### Prometheus-Metriken

```bash
curl http://localhost:8001/metrics
```

### OpenWebUI-Integration

**Siehe:** [QUICK_START.md](QUICK_START.md) | [OPENWEBUI_INTEGRATION.md](OPENWEBUI_INTEGRATION.md)

1. Öffne OpenWebUI
2. Gehe zu **Settings → Functions → + New Function**
3. Upload `openwebui_agent_server.py`
4. Aktiviere Function
5. Chat starten: "Erstelle Datei test.txt"

**Passwort vergessen?** Siehe [PASSWORD_RESET.md](PASSWORD_RESET.md) für Anleitung zum Zurücksetzen

---

## 📚 API-Dokumentation

### OpenAPI/Swagger

**Vollständige Dokumentation:** [docs/API.md](docs/API.md)

**OpenAPI-Spec:** [docs/openapi.yaml](docs/openapi.yaml)

**Swagger-UI lokal starten:**

```bash
cd docs
npx @apidevtools/swagger-cli serve openapi.yaml
# Öffne http://localhost:8080
```

### Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/v1/chat/completions` | POST | OpenAI-kompatible Chat-API |
| `/health` | GET | Server-Gesundheitsstatus |
| `/metrics` | GET | Prometheus-Metriken |
| `/test` | GET | Test-Endpoint (Development) |

### Tools

| Tool | Beschreibung | Argumente |
|------|--------------|-----------|
| `write_file` | Datei in Sandbox erstellen | `filename`, `content` |
| `read_file` | Datei aus Sandbox lesen | `filename` |
| `delete_file` | Datei aus Sandbox löschen | `filename` |
| `shell_exec` | Shell-Befehl ausführen | `command` |
| `fetch_webpage` | Webseite abrufen | `url` |

---

## 🐳 Docker-Deployment

**Vollständige Dokumentation:** [DOCKER.md](DOCKER.md)

### Quick Start

```bash
# Alle Services starten
docker-compose up -d

# Nur LocalAgent-Pro + Ollama
docker-compose up -d localagent-pro ollama

# Mit Monitoring (Prometheus + Grafana)
docker-compose --profile monitoring up -d

# Logs anzeigen
docker-compose logs -f localagent-pro

# Services stoppen
docker-compose down
```

### Image bauen

```bash
docker build -t localagent-pro:latest .
```

### Einzelner Container

```bash
docker run -d \
  --name localagent-pro \
  -p 8001:8001 \
  -v $(pwd)/sandbox:/app/sandbox \
  -v $(pwd)/logs:/app/logs \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  localagent-pro:latest
```

### Services

| Service | Port | Beschreibung |
|---------|------|--------------|
| localagent-pro | 8001 | AI Agent Server |
| ollama | 11434 | LLM Backend |
| prometheus | 9090 | Metrics Collection (optional) |
| grafana | 3001 | Dashboard (optional) |

---

## 🧪 Testing

**Vollständige Dokumentation:** [tests/README.md](tests/README.md)

### Test-Suite ausführen

```bash
# Alle Tests
./run_tests.sh all

# Nur Unit-Tests
./run_tests.sh unit

# Nur Integration-Tests
./run_tests.sh integration

# Mit Coverage-Report
./run_tests.sh coverage

# Fast-Mode (ohne slow tests)
./run_tests.sh fast
```

### Test-Kategorien

**100+ Unit-Tests:**

- `test_command_validation.py` - 40+ Tests für `_is_valid_command()`
- `test_tool_detection.py` - 15+ Tests für `analyze_and_execute()`
- `test_sandbox_isolation.py` - 12+ Tests für Sandbox-Pfade
- `test_shell_blocking.py` - 25+ Tests für Shell-Security
- `test_loop_protection.py` - 15+ Tests für Loop-Detection

**10+ Integration-Tests:**

- `test_workflows.py` - End-to-End Workflows (Chat → Tool → Response)

**CI/CD:**

- `.github/workflows/test.yml` - GitHub Actions Pipeline
  - Matrix-Tests: Python 3.10, 3.11, 3.12
  - Linting: flake8, mypy
  - Security: Bandit, Safety
  - Coverage: Codecov

### Coverage-Report

```bash
./run_tests.sh coverage
firefox htmlcov/index.html
```

**Ziel:** ≥80% Coverage

---

## 🔒 Security

**Vollständige Dokumentation:** [SECURITY.md](SECURITY.md)

### Security-Features

| Feature | Status | Beschreibung |
|---------|--------|--------------|
| **Sandbox-Isolation** | ✅ Aktiv | Alle Dateioperationen in `/sandbox` |
| **Shell-Whitelisting** | ✅ Aktiv | Nur sichere Befehle (ls, cat, grep) |
| **Loop-Protection** | ✅ Aktiv | MD5-basierte Request-Deduplizierung |
| **Domain-Whitelisting** | ✅ Aktiv | Nur vertrauenswürdige Domains |
| **Escape-Prevention** | ✅ Aktiv | Kein `../` in Dateinamen |
| **Dangerous-Commands** | ✅ Blockiert | rm -rf, sudo, dd, chmod 777 |

### Security-Audit

```bash
./security_audit.sh
```

**Scan-Tools:**

- **Bandit** - Python Security Scanner
- **Safety** - Dependency Vulnerabilities
- **pip-audit** - Package Vulnerabilities
- **Custom Checks** - hardcoded secrets, eval/exec, shell=True

**Report:** `security_reports/security_summary_TIMESTAMP.html`

### Best Practices

1. **Principle of Least Privilege:** Agent läuft als non-root User
2. **Defense in Depth:** Mehrere Sicherheitsschichten (Input-Validation, Whitelisting, Sandbox)
3. **Fail-Safe Defaults:** Default ist blockieren (Whitelist-Ansatz)
4. **Secure Secrets:** Keine hardcoded API-Keys (Umgebungsvariablen nutzen)

---

## 📊 Monitoring

**Vollständige Dokumentation:** [PROMETHEUS_INTEGRATION.md](PROMETHEUS_INTEGRATION.md)

### Prometheus-Metriken

**33 Metriken in 8 Kategorien:**

| Metrik | Typ | Labels | Beschreibung |
|--------|-----|--------|--------------|
| `localagent_requests_total` | Counter | `method`, `endpoint`, `status` | Anzahl Requests |
| `localagent_request_duration_seconds` | Histogram | `endpoint` | Request-Latenz |
| `localagent_active_requests` | Gauge | - | Aktive Requests |
| `localagent_ollama_calls_total` | Counter | `status` | LLM-Calls |
| `localagent_tool_executions_total` | Counter | `tool_name`, `status` | Tool-Aufrufe |
| `localagent_loop_detections_total` | Counter | - | Loop-Detections |

### Prometheus-Setup

**prometheus.yml:**

```yaml
scrape_configs:
  - job_name: 'localagent-pro'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 15s
```

### Grafana-Dashboard

**Template:** `grafana_dashboard_localagent.json`

**Panels:**

- Request-Rate (req/s)
- Error-Rate (%)
- Request-Latenz (P50/P95/P99)
- Tool-Usage (write_file, read_file, shell_exec)
- Loop-Detections
- Ollama-Calls
- Active Requests
- Health-Status

**Import:**

```bash
# Manual
1. Öffne Grafana (http://localhost:3001)
2. Gehe zu Dashboards → Import
3. Upload grafana_dashboard_localagent.json

# Automated (TODO #6)
./scripts/setup_grafana_dashboard.sh
```

---

## 🔧 Troubleshooting

### Server startet nicht

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Lösung:**

```bash
source venv/bin/activate  # venv aktivieren!
pip install -r requirements.txt
```

---

### Ollama nicht erreichbar

**Problem:** `ConnectionError: Ollama not reachable at http://localhost:11434`

**Lösung:**

```bash
# Ollama Status prüfen
curl http://localhost:11434/api/tags

# Falls nicht laufend:
ollama serve
```

---

### Loop-Protection triggert fälschlicherweise

**Problem:** `⚠️ Loop-Protection: Identische Anfrage innerhalb 2 Sekunden blockiert`

**Lösung:**

- Warte 2 Sekunden zwischen identischen Requests
- Oder ändere Loop-Timeout in `openwebui_agent_server.py`:

  ```python
  LOOP_TIMEOUT = 5.0  # statt 2.0
  ```

---

### Docker-Container startet nicht

**Problem:** `Error: Cannot connect to Ollama`

**Lösung:**

```bash
# Ollama-Container prüfen
docker-compose ps ollama

# Logs anzeigen
docker-compose logs ollama

# Ollama-Service neu starten
docker-compose restart ollama
```

---

### Tests schlagen fehl

**Problem:** `pytest: command not found`

**Lösung:**

```bash
source venv/bin/activate
pip install -r requirements-dev.txt
./run_tests.sh all
```

---

## 📈 Projekt-Status

**Version:** v1.0.0  
**Release:** 19. November 2025  
**Completion:** ~98%

### ✅ Abgeschlossene Komponenten

**Phase 1: Qualität (100%)**

- ✅ Unit-Tests (100+ Tests)
- ✅ Integration-Tests (10+ Tests)
- ✅ OpenAPI-Dokumentation

**Phase 2: Deployment (100%)**

- ✅ Docker-Containerisierung
- ✅ Systemd-Service
- ✅ Security-Audit

**Phase 3: Monitoring (100%)**

- ✅ Prometheus-Integration (33 Metriken)
- ✅ Grafana-Dashboard-Template
- ✅ Health-Check-Endpoint

### ⚠️ Optionale Komponenten (v1.1+)

- ⚠️ Grafana-Dashboard Auto-Deploy (TODO #6)
- ⚠️ ELION-Integration (TODO #7)
- ⚠️ Performance-Optimierung (TODO #8)
- ⚠️ Markdown-Lint-Fixes (TODO #10)

**Siehe:** [PROJECT_COMPLETION_ROADMAP.md](PROJECT_COMPLETION_ROADMAP.md)

---

## 📁 Projekt-Struktur

```text
LocalAgent-Pro/
├── src/
│   └── openwebui_agent_server.py  # Haupt-Server (1.250 LoC)
├── tests/
│   ├── unit/                      # 100+ Unit-Tests
│   │   ├── test_command_validation.py
│   │   ├── test_tool_detection.py
│   │   ├── test_sandbox_isolation.py
│   │   ├── test_shell_blocking.py
│   │   └── test_loop_protection.py
│   ├── integration/               # 10+ Integration-Tests
│   │   └── test_workflows.py
│   ├── conftest.py                # Pytest Fixtures
│   └── README.md                  # Test-Dokumentation
├── docs/
│   ├── openapi.yaml               # OpenAPI 3.0 Spec
│   └── API.md                     # API-Dokumentation
├── config/
│   ├── localagent-pro.service     # Systemd Unit-File
│   └── prometheus.yml             # Prometheus-Config
├── .github/workflows/
│   └── test.yml                   # CI/CD Pipeline
├── Dockerfile                     # Multi-Stage Build
├── docker-compose.yml             # 4 Services
├── .dockerignore                  # Build-Optimierung
├── requirements.txt               # Production-Dependencies
├── requirements-dev.txt           # Development-Dependencies
├── run_tests.sh                   # Test-Runner
├── security_audit.sh              # Security-Audit-Script
├── install_systemd_service.sh     # Systemd-Installer
├── README.md                      # Diese Datei
├── INSTALLATION.md                # Setup-Anleitung
├── DOCKER.md                      # Docker-Dokumentation
├── SECURITY.md                    # Security-Dokumentation
├── PROMETHEUS_INTEGRATION.md      # Monitoring-Dokumentation
└── PROJECT_COMPLETION_ROADMAP.md  # Projekt-Status
```

---

## 🤝 Beiträge

Contributions sind willkommen! Bitte beachte:

1. **Issues:** Erstelle ein Issue für Bugs/Feature-Requests
2. **Pull-Requests:** Fork → Branch → Commit → PR
3. **Tests:** Alle PRs müssen Tests enthalten (`./run_tests.sh all`)
4. **Code-Style:** flake8 + black (`flake8 src/`)
5. **Security:** Keine hardcoded secrets

---

## 📜 Lizenz

**MIT License**

Copyright (c) 2025 Danijel Jokic

```text
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📧 Kontakt

- **Autor:** Danijel Jokic
- **Email:** <jokicdanijel@protonmail.com>
- **GitHub:** <https://github.com/jokicdanijel/Lokales-Agententool>

---

## 🙏 Danksagungen

- **Ollama** - LLM Backend
- **OpenWebUI** - UI-Integration
- **Prometheus** - Monitoring
- **Grafana** - Dashboards
- **Flask** - Web-Framework
- **pytest** - Testing-Framework

---

## 📖 Weiterführende Dokumentation

- [QUICK_START.md](QUICK_START.md) - Schnelleinstieg
- [INSTALLATION.md](INSTALLATION.md) - Detaillierte Installation
- [DOCKER.md](DOCKER.md) - Docker-Deployment
- [SECURITY.md](SECURITY.md) - Security-Features
- [docs/API.md](docs/API.md) - API-Dokumentation
- [tests/README.md](tests/README.md) - Test-Dokumentation
- [PROMETHEUS_INTEGRATION.md](PROMETHEUS_INTEGRATION.md) - Monitoring
- [PROJECT_COMPLETION_ROADMAP.md](PROJECT_COMPLETION_ROADMAP.md) - Projekt-Status

---

**🎉 LocalAgent-Pro v1.0 - Production-Ready AI Agent Server!**

```bash
# Get Started:
docker-compose up -d
curl http://localhost:8001/health
```
