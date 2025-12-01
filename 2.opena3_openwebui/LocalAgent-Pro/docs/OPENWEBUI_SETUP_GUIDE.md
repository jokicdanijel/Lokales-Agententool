# OpenWebUI LocalAgentPro Setup Guide
## Integration, Configuration, Deployment & Testing

**Version:** 1.0
**Date:** 25. November 2025
**Status:** Production Ready

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Backend Connection](#backend-connection)
3. [Tool Registration](#tool-registration)
4. [Persona Integration](#persona-integration)
5. [Configuration](#configuration)
6. [Testing](#testing)
7. [Example Usage](#example-usage)
8. [Troubleshooting](#troubleshooting)

---

## 1. SYSTEM OVERVIEW

### 1.1 Architecture

```
┌─────────────────────────────────────────────────────┐
│                    OpenWebUI                        │
│  ┌──────────────────────────────────────────────┐   │
│  │  LocalAgentPro System Prompt                 │   │
│  │  (SCAN-FIRST + META-AUTOPILOT)              │   │
│  └──────────────────────────────────────────────┘   │
│           ↓ @-Tools                                 │
│  ┌──────────────────────────────────────────────┐   │
│  │  Registered Tools                            │   │
│  │  • vscode_copilot_bridge                     │   │
│  │  • browser_agent                             │   │
│  │  • dispatcher_controller                     │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
         ↓ HTTP/REST
┌─────────────────────────────────────────────────────┐
│              Backend Services                       │
│  ┌─────────────┐  ┌────────────┐  ┌────────────┐  │
│  │ VSCode      │  │ Browser    │  │ Dispatcher │  │
│  │ Bridge      │  │ Agent      │  │ Controller │  │
│  │ :8765       │  │ :12350     │  │ :8100      │  │
│  └─────────────┘  └────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 1.2 Components

| Component | Port | Description |
|-----------|------|-------------|
| **OpenWebUI** | 3000 | Main UI + API |
| **VSCode Bridge** | 8765 | Code generation, tests, refactoring |
| **Browser Agent** | 12350 | Web automation, multi-step workflows |
| **Dispatcher** | 8100 | Multi-agent routing, safepoints |

---

## 2. BACKEND CONNECTION

### 2.1 Prerequisites

Stelle sicher, dass folgende Services laufen:

```bash
# Check OpenWebUI
curl -s http://localhost:3000/api/v1/health

# Check VSCode Bridge
curl -s http://localhost:8765/health

# Check Browser Agent
curl -s http://localhost:12350/health

# Check Dispatcher
curl -s http://localhost:8100/health
```

### 2.2 Docker Compose Setup

```yaml
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:latest
    ports:
      - "3000:8080"
    environment:
      - OPENAI_API_KEY=sk-...
    volumes:
      - ./data:/app/backend/data

  vscode_bridge:
    image: vscode-copilot-bridge:latest
    ports:
      - "8765:8765"
    environment:
      - PROJECT_PATH=/home/user/project

  browser_agent:
    image: browser-agent:latest
    ports:
      - "12350:12350"
    environment:
      - HEADLESS=true

  dispatcher:
    image: dispatcher:latest
    ports:
      - "8100:8100"
    environment:
      - LOG_LEVEL=info
```

**Starten:**
```bash
docker-compose up -d
```

---

## 3. TOOL REGISTRATION

### 3.1 Auto-Registration Script

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro

# Starte Registrierung
./scripts/register_tools_openwebui.sh

# Mit benutzerdefinierten Parametern
./scripts/register_tools_openwebui.sh http://localhost:3000/api/v1 sk-mytoken
```

### 3.2 Manual Registration

Falls Auto-Registration fehlschlägt, registriere Tools manuell:

```bash
# 1. VSCode Bridge
curl -X POST http://localhost:3000/api/v1/tools \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-token" \
  -d @openwebui_tools/vscode_copilot_bridge.json

# 2. Browser Agent
curl -X POST http://localhost:3000/api/v1/tools \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-token" \
  -d @openwebui_tools/browser_agent.json

# 3. Dispatcher
curl -X POST http://localhost:3000/api/v1/tools \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-token" \
  -d @openwebui_tools/dispatcher_controller.json
```

### 3.3 Verification

```bash
# Liste registrierte Tools
curl -X GET http://localhost:3000/api/v1/tools \
  -H "Authorization: Bearer sk-token"

# Output sollte alle 3 Tools enthalten
```

---

## 4. PERSONA INTEGRATION

### 4.1 OpenWebUI System Prompt Setup

1. Öffne OpenWebUI (http://localhost:3000)
2. Gehe zu **Settings** → **Models** → **Edit Model**
3. Wähle das verwendete Modell (z.B. Claude)
4. Kopiere den kompletten Inhalt von `personas/localagentpro_openwebui_prompt.md` in das **System Prompt** Feld
5. Speichern

### 4.2 Persona Files Location

Alle Persona-Files sind hier verfügbar:

```
LocalAgent-Pro/personas/
├── localagentpro_openwebui_prompt.md    ← OpenWebUI (System Prompt)
├── localagentpro_vscode_prompt.md       ← VSCode (für IDE Integration)
├── browser_agent_prompt.md              ← Browser Agent (opena6)
└── dispatcher_agent_prompt.md           ← Dispatcher (kordp)
```

### 4.3 Richtige Persona für richtige Kontext

**Verwende in OpenWebUI:**
```
System Prompt: localagentpro_openwebui_prompt.md
```

**Diese Persona ist speziell für OpenWebUI gebaut und enthält:**
- SCAN-FIRST Workflow
- Tool-Orchestrierung (@-Befehle)
- META-AUTOPILOT Loop
- SELF-REPAIR Mechanismen

---

## 5. CONFIGURATION

### 5.1 Environment Variables

Erstelle `.env` im LocalAgent-Pro Verzeichnis:

```bash
# OpenWebUI
OPENWEBUI_API_URL=http://localhost:3000/api/v1
OPENWEBUI_AUTH_TOKEN=sk-localagent-pro

# VSCode Bridge
VSCODE_BRIDGE_URL=http://localhost:8765
VSCODE_BRIDGE_TIMEOUT=30000

# Browser Agent
BROWSER_AGENT_URL=http://localhost:12350
BROWSER_AGENT_HEADLESS=true

# Dispatcher
DISPATCHER_URL=http://localhost:8100
DISPATCHER_LOG_LEVEL=info

# Project
PROJECT_PATH=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/LocalAgent-Pro
PROJECT_NAME=LocalAgentPro
```

### 5.2 Config File

**config/localagent_config.yaml:**

```yaml
openwebui:
  api_url: http://localhost:3000/api/v1
  auth_token: sk-localagent-pro
  model: claude
  temperature: 0.7
  max_tokens: 4096

tools:
  vscode_bridge:
    enabled: true
    url: http://localhost:8765
    timeout: 30000

  browser_agent:
    enabled: true
    url: http://localhost:12350
    headless: true
    timeout: 60000

  dispatcher:
    enabled: true
    url: http://localhost:8100
    timeout: 15000

logging:
  level: INFO
  format: json
  file: logs/localagent.log

security:
  verify_ssl: true
  auth_method: bearer
```

---

## 6. TESTING

### 6.1 Test Suite ausführen

```bash
# Alle Tests
pytest tests/ -v

# Nur OpenWebUI Integration Tests
pytest tests/openwebui/ -v

# Mit Coverage Report
pytest tests/ --cov=. --cov-report=html
```

### 6.2 Manual Testing

#### Test 1: OpenWebUI Connection

```bash
curl -X GET http://localhost:3000/api/v1/health \
  -H "Authorization: Bearer sk-token"

# Expected: {"status": "ok", "version": "..."}
```

#### Test 2: Tool Availability

In OpenWebUI Chat:

```
@vscode_copilot_bridge {
  "action": "health_check",
  "project_path": "/home/.../LocalAgent-Pro"
}
```

Expected Response:
```json
{
  "status": "success",
  "action": "health_check",
  "result": {
    "system_healthy": true,
    "tools_available": 3
  }
}
```

#### Test 3: SCAN-FIRST Workflow

Schreibe in OpenWebUI Chat:

```
Scan das Projekt und berichte über den Status
```

Expected: Automatische INVENTORY MODE Phase mit:
- Dateien-Klassifizierung
- Kritische Module Identifikation
- Abhängigkeits-Analyse
- Bestätigungsaufforderung

#### Test 4: Tool Orchestration

```
@vscode_copilot_bridge {
  "action": "test_generation",
  "project_path": "/home/.../LocalAgent-Pro"
}
```

Expected: VSCode Bridge wird getriggert und Tests werden generiert.

#### Test 5: Browser Agent

```
@browser_agent {
  "action": "open",
  "url": "https://example.com"
}
```

Expected: Browser öffnet Seite und returniert Screenshot + HTML.

---

## 7. EXAMPLE USAGE

### 7.1 Scenario: Complete Project Analysis

**User Input:**
```
Analysiere das gesamte LocalAgent-Pro Projekt und berichte über kritische Probleme
```

**LocalAgentPro Workflow:**

1. **INVENTORY MODE** (automatisch)
   ```
   Scanne Projekt...
   • 45 Python-Module
   • 8 Tools/Utilities
   • 20 Agenten (opena1-opena20)
   • 12 Test-Dateien

   Kritische Module: 3 (Server, Dispatcher, Agents)
   Potenzielle Probleme: 2 (circular imports, missing type hints)
   ```

2. **Riski-Bewertung**
   ```
   ⚠️  Circular import: opena5 ↔ opena6
   ⚠️  Missing type hints in dispatcher
   ```

3. **Bestätigung**
   ```
   Möchtest du dass ich diese Probleme analysiere und Lösungen vorschlage? [Ja/Nein]
   ```

4. **EXECUTION MODE** (nach Ja)
   - @vscode_copilot_bridge triggern für Deep-Scan
   - Reparaturvorschläge generieren
   - Refactoring-Plan erstellen

---

### 7.2 Scenario: Web Automation Task

**User Input:**
```
Öffne https://example.com/login, logge dich ein mit user@test.com / password123,
und extrahiere die Benutzer-ID von der Dashboard
```

**BrowserAgent Workflow:**

```json
{
  "workflow": [
    {"action": "open", "url": "https://example.com/login"},
    {"action": "wait_for", "selector": "input[name='email']"},
    {"action": "type", "selector": "input[name='email']", "text": "user@test.com"},
    {"action": "type", "selector": "input[name='password']", "text": "password123"},
    {"action": "click", "selector": "button[type='submit']"},
    {"action": "wait_for", "selector": ".dashboard"},
    {"action": "extract_text", "selector": ".user-id"},
    {"action": "screenshot"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "steps_completed": 8,
  "extracted_data": {
    "user_id": "USR_12345678"
  },
  "screenshot": "base64..."
}
```

---

## 8. TROUBLESHOOTING

### Problem: Tools nicht registriert

**Symptom:** `@vscode_copilot_bridge` wird nicht erkannt

**Lösung:**
```bash
# 1. Check OpenWebUI API
curl -X GET http://localhost:3000/api/v1/health

# 2. Re-register tools
./scripts/register_tools_openwebui.sh

# 3. Check logs
tail -f logs/tools_registration.log
```

### Problem: Connection Timeout zu VSCode Bridge

**Symptom:** Tool-Aufruf schlägt fehl mit Timeout

**Lösung:**
```bash
# 1. Check ob Bridge läuft
curl http://localhost:8765/health

# 2. Starten Sie die Bridge
docker start vscode-bridge
# oder
python3 -m vscode_bridge --port 8765

# 3. Erhöhen Sie Timeout in Config
# VSCODE_BRIDGE_TIMEOUT=60000
```

### Problem: Browser Agent startet nicht

**Symptom:** BrowserAgent-Aktion gibt Error

**Lösung:**
```bash
# 1. Check Abhängigkeiten
python3 -c "import selenium; import headless_chrome"

# 2. Starten Sie Chrome/Chromium
sudo apt-get install chromium-browser

# 3. Starten Sie BrowserAgent neu
docker restart browser-agent
```

### Problem: Dispatcher Safepoints nicht geschrieben

**Symptom:** Dispatcher läuft, aber Safepoints fehlen

**Lösung:**
```bash
# 1. Check Dispatcher Logs
tail -f logs/dispatcher.log

# 2. Überprüfe Routing-Validierung
# In Config: DISPATCHER_LOG_LEVEL=debug

# 3. Stelle sicher dass Speicherplatz vorhanden ist
df -h
```

---

## ✅ DEPLOYMENT CHECKLIST

Vor Production-Deployment:

- [ ] Alle Backend-Services laufen
- [ ] Tools sind registriert
- [ ] System Prompt ist in OpenWebUI geladen
- [ ] Test Suite läuft (pytest all tests pass)
- [ ] Logs sind aktiv und readable
- [ ] Auth-Token sind gesetzt
- [ ] Firewall-Regeln sind konfiguriert
- [ ] Backup-Strategie ist vorhanden
- [ ] Monitoring ist aktiviert
- [ ] Team ist geschult

---

## 📚 WEITERE RESSOURCEN

- **Hardened Security Docs**: `.github/copilot-instructions-openwebui-hardened.md`
- **Integration Guide**: `.github/OPENWEBUI_HARDENED_INTEGRATION_GUIDE.md`
- **Activation Checklist**: `.github/ACTIVATION_CHECKLIST.sh`
- **Personas**: `LocalAgent-Pro/personas/`

---

**Status:** ✅ Ready for Production
**Last Updated:** 25. November 2025
**Support:** See Troubleshooting section
