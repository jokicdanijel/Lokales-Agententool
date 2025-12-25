# 🤖 Lokales Agententool

**AI-Agent-Server für lokale Entwicklung mit GitHub Copilot-Integration**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Copilot](https://img.shields.io/badge/GitHub_Copilot-ready-brightgreen.svg)](https://github.com/features/copilot)
[![Lizenz: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Überblick

Dieses Repository enthält **LocalAgent-Pro**, einen production-ready AI-Agent-Server mit OpenWebUI-Integration, der speziell für die Arbeit mit GitHub Copilot optimiert ist.

### 🎯 Hauptprojekt: LocalAgent-Pro

**Verzeichnis:** [`LocalAgent-Pro/`](LocalAgent-Pro/)

LocalAgent-Pro ist ein intelligenter AI-Agent-Server mit den folgenden Features:

- 📝 **Datei-Management:** Lesen, Schreiben, Löschen (Sandbox-isoliert)
- 🔧 **Shell-Befehle:** Sichere Ausführung whitelisteter Befehle
- 🌐 **Web-Requests:** HTTP-Anfragen an vertrauenswürdige Domains
- 🔒 **Loop-Protection:** MD5-basierte Request-Deduplizierung
- 📊 **Prometheus-Monitoring:** 33 Metriken für Production-Deployment

---

## 🚀 Quick Start

### Für GitHub Copilot-Nutzer

Wenn du mit GitHub Copilot arbeitest, beachte folgende Hinweise:

1. **Hauptdokumentation:** Siehe [`LocalAgent-Pro/README.md`](LocalAgent-Pro/README.md)
2. **Copilot-Systemaufforderung:** [`LocalAgent-Pro/COPILOT_SYSTEM_PROMPT.md`](LocalAgent-Pro/COPILOT_SYSTEM_PROMPT.md)
3. **Copilot-Anleitung:** [`LocalAgent-Pro/COPILOT_PROMPT.md`](LocalAgent-Pro/COPILOT_PROMPT.md)
4. **Commit-Richtlinien:** [`.github/copilot-commit-instructions.md`](.github/copilot-commit-instructions.md)

### Docker-Installation (2 Minuten)

```bash
# Repository klonen
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro

# Docker-basierte Installation (empfohlen)
docker-compose up -d

# Server läuft auf: http://localhost:8001
# OpenWebUI auf: http://localhost:3000
```

### Manuelle Installation (5 Minuten)

```bash
cd LocalAgent-Pro

# Virtuelle Umgebung
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Ollama starten (separates Terminal)
ollama serve
ollama pull llama3.1:8b-instruct-q4_K_M

# Server starten
python src/openwebui_agent_server.py
```

---

## 📚 Wichtige Dokumentation

### Für Entwickler

| Dokument                                                         | Beschreibung                        |
| ---------------------------------------------------------------- | ----------------------------------- |
| [LocalAgent-Pro/README.md](LocalAgent-Pro/README.md)             | Vollständige Projekt-Dokumentation  |
| [LocalAgent-Pro/INSTALLATION.md](LocalAgent-Pro/INSTALLATION.md) | Detaillierte Installationsanleitung |
| [LocalAgent-Pro/QUICK_START.md](LocalAgent-Pro/QUICK_START.md)   | Schnelleinstieg                     |
| [LocalAgent-Pro/DOCKER.md](LocalAgent-Pro/DOCKER.md)             | Docker-Deployment                   |

### Für GitHub Copilot

| Dokument                                                                           | Beschreibung                      |
| ---------------------------------------------------------------------------------- | --------------------------------- |
| [LocalAgent-Pro/COPILOT_SYSTEM_PROMPT.md](LocalAgent-Pro/COPILOT_SYSTEM_PROMPT.md) | System-Prompt für VSCode Copilot  |
| [LocalAgent-Pro/COPILOT_PROMPT.md](LocalAgent-Pro/COPILOT_PROMPT.md)               | Copilot-Integration mit OpenWebUI |
| [.github/copilot-commit-instructions.md](.github/copilot-commit-instructions.md)   | Commit-Message-Guidelines         |

### API & Testing

| Dokument                                                         | Beschreibung       |
| ---------------------------------------------------------------- | ------------------ |
| [LocalAgent-Pro/docs/API.md](LocalAgent-Pro/docs/API.md)         | API-Dokumentation  |
| [LocalAgent-Pro/tests/README.md](LocalAgent-Pro/tests/README.md) | Test-Dokumentation |
| [LocalAgent-Pro/SECURITY.md](LocalAgent-Pro/SECURITY.md)         | Security-Features  |

---

## 🔧 GitHub Copilot Konfiguration

### VSCode Copilot einrichten

1. **Systemaufforderung einfügen:**
   - Drücke `Ctrl+Shift+P` (oder `Cmd+Shift+P` auf Mac)
   - Suche: "Copilot: Edit Custom Instructions"
   - Füge den Inhalt von [`LocalAgent-Pro/COPILOT_SYSTEM_PROMPT.md`](LocalAgent-Pro/COPILOT_SYSTEM_PROMPT.md) ein

2. **Repository-Kontext:**

   ```
   Backend-API: http://127.0.0.1:8001/v1
   OpenWebUI: http://127.0.0.1:3000
   Hauptprojekt: LocalAgent-Pro/
   ```

3. **Wichtige Endpoints:**
   - Health Check: `GET http://127.0.0.1:8001/health`
   - Modelle: `GET http://127.0.0.1:8001/v1/models`
   - Chat: `POST http://127.0.0.1:8001/v1/chat/completions`

### Commit-Messages mit Copilot

Folge den Guidelines in [`.github/copilot-commit-instructions.md`](.github/copilot-commit-instructions.md):

**Format:**

```
<typ>(<scope>): <kurze Beschreibung>

<ausführliche Beschreibung>

Relates-to: <Bezug>
```

**Typen:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Beispiel:**

```
docs(readme): Füge Root-README für Copilot-Nutzer hinzu

- Zentraler Einstiegspunkt für Repository
- Copilot-spezifische Konfigurationshinweise
- Quick-Start-Anleitung für verschiedene Installationsmethoden
- Verlinkungen auf Detaildokumentationen

Verbessert: Developer-Onboarding, Copilot-Integration
```

---

## 🎯 Verfügbare Tools (via Chat-API)

LocalAgent-Pro erkennt und führt folgende Tools automatisch aus:

| Tool            | Beschreibung               | Beispiel                                      |
| --------------- | -------------------------- | --------------------------------------------- |
| `write_file`    | Datei in Sandbox erstellen | "Erstelle hello.txt mit Inhalt 'Hello World'" |
| `read_file`     | Datei aus Sandbox lesen    | "Lies die Datei config.yaml"                  |
| `delete_file`   | Datei aus Sandbox löschen  | "Lösche test.txt"                             |
| `shell_exec`    | Shell-Befehl ausführen     | "Liste alle Dateien auf"                      |
| `fetch_webpage` | Webseite abrufen           | "Hole den Inhalt von example.com"             |

**Wichtig:** Alle Dateioperationen sind sandbox-isoliert (`~/localagent_sandbox/`)

---

## 🔒 Security-Features

- ✅ **Sandbox-Isolation:** Alle Dateioperationen im separaten Verzeichnis
- ✅ **Shell-Whitelisting:** Nur sichere Befehle (ls, cat, grep, etc.)
- ✅ **Domain-Whitelisting:** Nur vertrauenswürdige Domains
- ✅ **Loop-Protection:** Verhindert Endlosschleifen
- ✅ **Escape-Prevention:** Blockiert `../` in Dateinamen
- ✅ **Dangerous-Commands:** Blockiert rm -rf, sudo, dd, etc.

**Details:** [LocalAgent-Pro/SECURITY.md](LocalAgent-Pro/SECURITY.md)

---

## 📊 Projekt-Struktur

```
Lokales-Agententool/
├── LocalAgent-Pro/          # Hauptprojekt (AI-Agent-Server)
│   ├── src/                 # Source-Code
│   ├── tests/               # Unit- & Integration-Tests
│   ├── docs/                # API-Dokumentation
│   ├── config/              # Konfigurationsdateien
│   ├── README.md            # Hauptdokumentation
│   ├── COPILOT_*.md         # Copilot-Konfiguration
│   └── docker-compose.yml   # Docker-Setup
├── .github/
│   ├── workflows/           # CI/CD-Pipeline
│   └── copilot-commit-instructions.md
└── README.md                # Diese Datei
```

---

## 🧪 Testing

```bash
cd LocalAgent-Pro

# Alle Tests ausführen
./run_tests.sh all

# Nur Unit-Tests
./run_tests.sh unit

# Mit Coverage-Report
./run_tests.sh coverage
```

**Test-Abdeckung:** ≥80%
**Test-Suiten:** 100+ Unit-Tests, 10+ Integrations-Tests

---

## 📦 Deployment-Optionen

### 1. Docker (empfohlen)

```bash
cd LocalAgent-Pro
docker-compose up -d
```

**Services:**

- LocalAgent-Pro: `http://localhost:8001`
- Ollama: `http://localhost:11434`
- Prometheus: `http://localhost:9090` (optional)
- Grafana: `http://localhost:3001` (optional)

### 2. Systemd-Service

```bash
cd LocalAgent-Pro
sudo ./install_systemd_service.sh
```

**Auto-Start:** Server startet automatisch beim Booten

### 3. Manuelle Ausführung

```bash
cd LocalAgent-Pro
source venv/bin/activate
python src/openwebui_agent_server.py
```

---

## 🤝 Beiträge

Beiträge sind willkommen! Bitte beachte:

1. **Issues:** Erstelle ein Issue für Bugs/Feature-Requests
2. **Pull-Requests:** Fork → Branch → Commit → PR
3. **Tests:** Alle PRs müssen Tests enthalten
4. **Commit-Format:** Folge den [Copilot-Guidelines](.github/copilot-commit-instructions.md)
5. **Code-Style:** flake8 + black

---

## 📄 Lizenz

**MIT-Lizenz** - Copyright (c) 2025 Danijel Jokic

Siehe [LICENSE](LocalAgent-Pro/README.md#-lizenz) für Details.

---

## 📧 Kontakt

- **Autor:** Danijel Jokic
- **Email:** <jokicdanijel@protonmail.com>
- **GitHub:** <https://github.com/jokicdanijel/Lokales-Agententool>

---

## 🚀 Los geht's

```bash
# Schnellstart mit Docker
git clone https://github.com/jokicdanijel/Lokales-Agententool.git
cd Lokales-Agententool/LocalAgent-Pro
docker-compose up -d

# Gesundheitscheck
curl http://localhost:8001/health

# Erste Chat-Anfrage
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hallo LocalAgent-Pro!"}]}'
```

**Weitere Informationen:** [`LocalAgent-Pro/README.md`](LocalAgent-Pro/README.md)

---

**🎉 Viel Erfolg mit LocalAgent-Pro und GitHub Copilot!**
