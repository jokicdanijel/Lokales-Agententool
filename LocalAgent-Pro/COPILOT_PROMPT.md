# 🤖 OpenWebUI-Integration Copilot Prompt

## System-Prompt für VSCode/OpenWebUI Copilot

```
Du bist ein AI-Assistant für LocalAgent-Pro mit OpenWebUI-Integration.

BACKEND-API:
- Base URL: http://127.0.0.1:8001/v1
- Port: 8001 (Backend API)

ENDPOINTS:
- POST http://127.0.0.1:8001/v1/chat/completions (Chat)
- GET  http://127.0.0.1:8001/v1/models (Modelliste)
- POST http://127.0.0.1:8001/test (Tool-Test)
- GET  http://127.0.0.1:8001/health (Status)

OPENWEBUI UI:
- Port: 3000 (separates Web-Interface)
- Verbindet sich mit Backend API über http://127.0.0.1:8001/v1

WICHTIG:
- /v1 alleine gibt 404 (normal) - nutze vollständige Pfade
- API Base URL in OpenWebUI: http://127.0.0.1:8001/v1
- Bei Problemen: Prüfe /health, /v1/models, /v1/chat/completions
```

---

## Anweisungen für Copilot

### 1. Server-Status prüfen
```bash
curl -s http://127.0.0.1:8001/health
```

### 2. Modelle prüfen
```bash
curl -s http://127.0.0.1:8001/v1/models
```

### 3. Chat-Endpoint testen
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hallo LocalAgent-Pro"}]}' \
  http://127.0.0.1:8001/v1/chat/completions
```

### 4. Bei 404-Fehler
- ✅ Nutze vollständigen Pfad: `/v1/chat/completions` statt `/v1`
- ✅ Prüfe ob Server läuft: `curl http://127.0.0.1:8001/health`
- ✅ Überprüfe Port: `ss -tlnp | grep 8001`

### 5. OpenWebUI konfigurieren
1. Öffne: http://localhost:3000
2. Settings → Connections → OpenAI API
3. **API Base URL**: `http://127.0.0.1:8001/v1`
4. **API Key**: `dummy`
5. Save & Test

---

## Erwartete Ausgaben

### Health Check
```json
{
  "status": "ok",
  "model": "llama3.1",
  "sandbox": true,
  "sandbox_path": "/home/danijel-jd/localagent_sandbox"
}
```

### Models
```json
{
  "object": "list",
  "data": [
    {"id": "localagent-pro", "object": "model"},
    {"id": "llama3.1", "object": "model"}
  ]
}
```

### Chat Response
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "🤖 LocalAgent-Pro: ..."
    }
  }]
}
```

---

## Troubleshooting Checkliste

- [ ] Backend läuft auf Port 8001
- [ ] OpenWebUI läuft auf Port 3000
- [ ] API Base URL korrekt: `http://127.0.0.1:8001/v1`
- [ ] Health-Endpoint antwortet
- [ ] Models-Endpoint listet Modelle
- [ ] Chat-Endpoint funktioniert
- [ ] Keine Firewall-Blockierung

---

## Quick Fix Commands

```bash
# Server starten
cd LocalAgent-Pro && ./start_server.sh

# Server stoppen
./stop_server.sh

# Vollständiger Check
./openwebui_check.sh

# Logs prüfen
tail -f server.log

# Port-Status
ss -tlnp | grep -E "8001|3000"
```

---

## Port-Übersicht

| Service | Port | URL |
|---------|------|-----|
| LocalAgent-Pro API | 8001 | http://127.0.0.1:8001/v1 |
| OpenWebUI UI | 3000 | http://127.0.0.1:3000 |

**Wichtig**: Verwende Port 8001 für API-Verbindungen, Port 3000 für Browser-Zugriff!
