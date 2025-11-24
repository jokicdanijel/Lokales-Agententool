# 🌐 OpenWebUI Integration - LocalAgent-Pro

Integration mit Open WebUI für eine benutzerfreundliche Chat-Oberfläche.

---

## 📋 Überblick

LocalAgent-Pro integriert sich nahtlos mit OpenWebUI und bietet:

- 💬 **Chat-Interface:** Moderne Web-UI für Konversationen
- 🔧 **Tool-Calling:** Automatische Funktionsausführung
- 📊 **Monitoring:** Echtzeit-Statistiken
- 🔐 **Multi-User:** Benutzerverwaltung (OpenWebUI-Feature)

### 🔑 Neu: Password Reset

LocalAgent-Pro bietet jetzt ein **OpenWebUI Password Reset Utility** für einfache Passwort-Updates:

- 📘 **Vollständige Anleitung:** [PASSWORD_RESET.md](PASSWORD_RESET.md)
- 🛠️ **Utility-Skript:** [update_openwebui_password.sh](update_openwebui_password.sh)
- 📝 **Beispiele:** [../examples/password_reset_example.sh](../examples/password_reset_example.sh)

**Schnellstart:**

```bash
./update_openwebui_password.sh -e user@example.com -p '$2b$12$HASH...'
```

---

## 🚀 Setup

### Docker-Compose (empfohlen)

```yaml
# docker-compose.yml
version: '3.8'

services:
  localagent-pro:
    build: .
    ports:
      - "8001:8001"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./sandbox:/app/sandbox
    networks:
      - agent-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - agent-network

  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    ports:
      - "3000:8080"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - OPENAI_API_BASE_URL=http://localagent-pro:8001/v1
      - OPENAI_API_KEY=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
    volumes:
      - openwebui-data:/app/backend/data
    networks:
      - agent-network

networks:
  agent-network:
    driver: bridge

volumes:
  ollama-data:
  openwebui-data:
```

### Starten

```bash
docker-compose up -d
```

**Services:**

- LocalAgent-Pro: <http://localhost:8001>
- OpenWebUI: <http://localhost:3000>
- Ollama: <http://localhost:11434>

---

## 🔧 Konfiguration

### OpenWebUI Settings

1. **Browser öffnen:** <http://localhost:3000>
2. **Admin Account erstellen:** Ersten Nutzer registrieren
3. **Settings → Connections:**
   - OpenAI API: `http://localagent-pro:8001/v1`
   - API Key: `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` (Konfiguriert)
4. **Model auswählen:** `llama3.1:8b-instruct-q4_K_M`

### LocalAgent-Pro API-Endpoints

```python
# Health Check
GET http://localhost:8001/health

# Models
GET http://localhost:8001/v1/models

# Chat Completions
POST http://localhost:8001/v1/chat/completions
```

---

## 💬 Nutzung

### 1. Chat starten

```
Du: Hallo! Was kannst du tun?
AI: Ich bin LocalAgent-Pro! Ich kann:
    - Dateien verwalten (lesen, schreiben, löschen)
    - Shell-Befehle ausführen
    - Web-Requests senden
```

### 2. Datei erstellen

```
Du: Erstelle eine Datei config.yaml mit:
    port: 8080
    host: 0.0.0.0

AI: Datei config.yaml wurde erstellt!
    [Tool: write_file]
```

### 3. Datei lesen

```
Du: Lies die Datei config.yaml

AI: Inhalt von config.yaml:
    port: 8080
    host: 0.0.0.0
    [Tool: read_file]
```

### 4. Shell-Befehl

```
Du: Zeige mir alle Dateien

AI: Dateien im Sandbox:
    config.yaml
    hello.txt
    [Tool: shell_exec - ls -la]
```

### 5. Web-Request

```
Du: Hole den Inhalt von https://api.github.com

AI: GitHub API Response:
    {...}
    [Tool: fetch_webpage]
```

---

## 🎯 Tool-Calling

LocalAgent-Pro erkennt automatisch Funktionsaufrufe:

### Automatische Tool-Erkennung

```
User: "Erstelle hello.txt mit 'Hello World'"
→ Tool: write_file(filename="hello.txt", content="Hello World")

User: "Lies config.yaml"
→ Tool: read_file(filename="config.yaml")

User: "Führe ls aus"
→ Tool: shell_exec(command="ls -la")

User: "Hole github.com"
→ Tool: fetch_webpage(url="https://github.com")
```

### Tool-Response-Format

```json
{
  "tool": "write_file",
  "args": {
    "filename": "hello.txt",
    "content": "Hello World"
  },
  "result": "success",
  "message": "File created: hello.txt"
}
```

---

## 📊 Monitoring

### Prometheus-Metriken

```bash
# Metriken abrufen
curl http://localhost:8001/metrics
```

**Verfügbare Metriken:**

- `http_requests_total` - Anzahl API-Requests
- `http_request_duration_seconds` - Request-Dauer
- `tool_calls_total` - Tool-Aufrufe
- `tool_errors_total` - Tool-Fehler
- `sandbox_file_operations_total` - Dateioperationen

### Grafana-Dashboard

```bash
# Grafana starten
docker-compose -f docker-compose.monitoring.yml up -d

# Dashboard: http://localhost:3001
# Username: admin
# Password: admin
```

---

## 🐛 Troubleshooting

### Problem: OpenWebUI kann LocalAgent-Pro nicht erreichen

**Lösung:**

```bash
# Network-Verbindung prüfen
docker network inspect agent-network

# Container-Logs
docker-compose logs -f openwebui
docker-compose logs -f localagent-pro
```

### Problem: Modell nicht verfügbar

**Lösung:**

```bash
# Modell herunterladen
docker-compose exec ollama ollama pull llama3.1:8b-instruct-q4_K_M

# Modelle anzeigen
docker-compose exec ollama ollama list
```

### Problem: Password vergessen

**Lösung:**

- Siehe [PASSWORD_RESET.md](PASSWORD_RESET.md) für detaillierte Anleitung
- Nutze `update_openwebui_password.sh` Utility

---

## 🔒 Sicherheit

### Production-Setup

```yaml
# docker-compose.prod.yml
services:
  openwebui:
    environment:
      - ENABLE_SIGNUP=false
      - DEFAULT_USER_ROLE=user
      - JWT_SECRET=${JWT_SECRET}
      - WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}
```

### Environment-Variables

```bash
# .env
JWT_SECRET=$(openssl rand -hex 32)
WEBUI_SECRET_KEY=$(openssl rand -hex 32)
```

---

## 📚 Weitere Ressourcen

- **OpenWebUI Docs:** <https://docs.openwebui.com>
- **LocalAgent-Pro API:** [docs/API.md](docs/API.md)
- **Security Guide:** [SECURITY.md](SECURITY.md)
- **Password Reset:** [PASSWORD_RESET.md](PASSWORD_RESET.md)

---

**🎉 Viel Erfolg mit LocalAgent-Pro & OpenWebUI!**
