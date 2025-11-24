# 🤖 LocalAgent-Pro

> Production-Ready AI-Agent-Server mit OpenWebUI-Integration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

---

## 📋 Überblick

LocalAgent-Pro ist ein intelligenter AI-Agent-Server, der speziell für die Integration mit OpenWebUI entwickelt wurde. Er bietet sichere Dateioperationen, Shell-Befehle und Web-Requests mit umfassenden Sicherheitsmechanismen.

### ✨ Hauptfunktionen

- 📝 **Datei-Management:** Sandbox-isolierte Dateioperationen (Lesen, Schreiben, Löschen)
- 🔧 **Shell-Befehle:** Sichere Ausführung whitelisteter Befehle
- 🌐 **Web-Requests:** HTTP-Anfragen an vertrauenswürdige Domains
- 🔒 **Loop-Protection:** MD5-basierte Request-Deduplizierung
- 📊 **Prometheus-Monitoring:** 33 Metriken für Production-Deployment
- 🔐 **Sicherheit:** Sandbox, Command-Whitelisting, Domain-Whitelisting

### 🔑 Neue Features

- 🔑 **Password Reset:** OpenWebUI-Passwort-Reset-Utility - siehe [PASSWORD_RESET.md](PASSWORD_RESET.md)

---

## 🚀 Quick Start

### Docker-Installation (empfohlen)

```bash
# Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro

# Docker-Compose starten
docker-compose up -d

# Server läuft auf: http://localhost:8001
# OpenWebUI auf: http://localhost:3000
```

### Manuelle Installation

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Ollama starten (separates Terminal)
ollama serve
ollama pull llama3.1:8b-instruct-q4_K_M

# Server starten
python src/openwebui_agent_server.py
```

**Mehr Details:** [INSTALLATION.md](INSTALLATION.md)

---

## 📚 Dokumentation

| Dokument | Beschreibung |
|----------|--------------|
| [INSTALLATION.md](INSTALLATION.md) | Detaillierte Installationsanleitung |
| [QUICK_START.md](QUICK_START.md) | Schnelleinstieg für neue Nutzer |
| [COPILOT_SYSTEM_PROMPT.md](COPILOT_SYSTEM_PROMPT.md) | GitHub Copilot System-Prompt |
| [COPILOT_PROMPT.md](COPILOT_PROMPT.md) | Copilot OpenWebUI-Integration |
| [PASSWORD_RESET.md](PASSWORD_RESET.md) | OpenWebUI Passwort-Reset-Guide |
| [OPENWEBUI_INTEGRATION.md](OPENWEBUI_INTEGRATION.md) | OpenWebUI Integration |
| [SECURITY.md](SECURITY.md) | Sicherheitsfunktionen |
| [docs/API.md](docs/API.md) | API-Dokumentation |
| [tests/README.md](tests/README.md) | Test-Dokumentation |

---

## 🎯 Verfügbare Tools

LocalAgent-Pro bietet folgende Tools über die Chat-API:

| Tool | Beschreibung | Beispiel |
|------|--------------|----------|
| `write_file` | Datei in Sandbox erstellen | "Erstelle hello.txt mit 'Hello World'" |
| `read_file` | Datei aus Sandbox lesen | "Lies config.yaml" |
| `delete_file` | Datei aus Sandbox löschen | "Lösche test.txt" |
| `shell_exec` | Shell-Befehl ausführen | "Liste alle Dateien auf" |
| `fetch_webpage` | Webseite abrufen | "Hole Inhalt von example.com" |

**Wichtig:** Alle Dateioperationen sind sandbox-isoliert (`~/localagent_sandbox/`)

---

## 🔒 Sicherheit

- ✅ **Sandbox-Isolation:** Alle Dateioperationen in separatem Verzeichnis
- ✅ **Shell-Whitelisting:** Nur sichere Befehle (ls, cat, grep, echo, etc.)
- ✅ **Domain-Whitelisting:** Nur vertrauenswürdige Domains erlaubt
- ✅ **Loop-Protection:** MD5-basierte Request-Deduplizierung
- ✅ **Path-Traversal-Prevention:** Blockiert `../` in Dateinamen
- ✅ **Dangerous-Commands:** Blockiert rm -rf, sudo, dd, etc.

**Details:** [SECURITY.md](SECURITY.md)

---

## 🧪 Testing

```bash
# Alle Tests ausführen
./run_tests.sh all

# Nur Unit-Tests
./run_tests.sh unit

# Mit Coverage-Report
./run_tests.sh coverage
```

**Test-Coverage:** ≥80%
**Test-Suiten:** 100+ Unit-Tests, 10+ Integration-Tests

---

## 📦 Deployment

### Docker (empfohlen)

```bash
docker-compose up -d
```

**Services:**

- LocalAgent-Pro: `http://localhost:8001`
- Ollama: `http://localhost:11434`
- Prometheus: `http://localhost:9090` (optional)
- Grafana: `http://localhost:3001` (optional)

### Systemd-Service

```bash
sudo ./install_systemd_service.sh
```

**Auto-Start:** Server startet automatisch beim Booten

---

## 🤝 Beiträge

Contributions sind willkommen!

1. **Issues:** Erstelle ein Issue für Bugs/Feature-Requests
2. **Pull-Requests:** Fork → Branch → Commit → PR
3. **Tests:** Alle PRs müssen Tests enthalten
4. **Commit-Format:** Folge den [Copilot-Guidelines](../.github/copilot-commit-instructions.md)
5. **Code-Style:** flake8 + black

---

## 📜 Lizenz

**MIT License** - Copyright (c) 2025 Danijel Jokic

```text
MIT License

Copyright (c) 2025 Danijel Jokic

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
- **Email:** <jokicdanijel@gmail.com>
- **GitHub:** <https://github.com/jokicdanijel/Lokales-Agententool>

---

**🎉 Viel Erfolg mit LocalAgent-Pro!**
