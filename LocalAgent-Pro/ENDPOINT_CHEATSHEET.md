# 🚀 LocalAgent-Pro API Endpoint Cheatsheet (Linux Mint)

## 📋 Schnellübersicht

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/` | GET | HTML-Übersicht |
| `/health` | GET | Server-Status & Konfiguration |
| `/whitelist` | GET | Auto-Whitelist anzeigen |
| `/v1` | GET | API-Versionsinformationen |
| `/v1/models` | GET | Verfügbare Modelle |
| `/v1/chat/completions` | POST | Chat API (OpenAI-kompatibel) |
| `/test` | GET/POST | Tool-Test-Endpoint |

---

## 🧪 Schnell-Tests (Copy & Paste)

### 1️⃣ Server läuft?

```bash
curl -s http://127.0.0.1:8001/health | jq '.status'
# Output: "ok"
```

### 2️⃣ Welche Modelle verfügbar?

```bash
curl -s http://127.0.0.1:8001/v1/models | jq '.data[].id'
# Output: "localagent-pro" + "llama3.1" (oder dein LLM_MODEL)
```

### 3️⃣ Sandbox aktiv?

```bash
curl -s http://127.0.0.1:8001/health | jq '.sandbox'
# Output: false (bei dir deaktiviert)
```

### 4️⃣ Wildcard-Domains aktiv?

```bash
curl -s http://127.0.0.1:8001/health | jq '.allowed_domains'
# Output: ["*"]
```

### 5️⃣ Whitelist anzeigen

```bash
curl -s http://127.0.0.1:8001/whitelist | jq '.'
# Zeigt alle auto-genehmigten Domains
```

---

## 💬 Chat API Tests

### ✏️ Datei erstellen

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Erstelle demo.txt mit Hello World"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

### 📖 Datei lesen

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Lies demo.txt"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

### 🗑️ Datei löschen

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Lösche demo.txt"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

### 📂 Dateien auflisten

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Liste alle Dateien auf"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

### 🌐 Web-Request (nur mit Wildcard)

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Hole github.com"}],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

---

## 🔬 Test-Endpoint (Direkter Tool-Zugriff)

### GET-Methode

```bash
curl -s "http://127.0.0.1:8001/test?prompt=Erstelle%20quick.txt%20mit%20Quick%20Test" | jq '.'
```

### POST-Methode

```bash
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Lies quick.txt"}' | jq '.'
```

---

## 📡 Streaming-Test

```bash
curl -N -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{"role": "user", "content": "Erstelle stream.txt mit Streaming funktioniert"}],
    "stream": true
  }'
```

---

## 🎯 OpenWebUI Integration

### Konfiguration in OpenWebUI

1. Öffne OpenWebUI: `http://localhost:3000`
2. Gehe zu: **Settings → Connections**
3. Füge hinzu:
   - **API Base URL**: `http://127.0.0.1:8001/v1`
   - **API Key**: (leer lassen oder beliebig)
4. Speichern & Testen

### Testen in OpenWebUI

```
User: Erstelle test.txt mit OpenWebUI funktioniert!
Agent: ✅ Datei erstellt (Live: /absolute/path/test.txt)
      📝 31 Zeichen geschrieben
```

---

## 🐧 Linux Mint Spezifisch

### Server starten

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales\ Agententool/LocalAgent-Pro
./start_server.sh
```

### Server neustarten

```bash
./restart_server.sh
```

### Server stoppen

```bash
ps aux | grep "python.*openwebui_agent_server" | grep -v grep | awk '{print $2}' | xargs -r kill
```

### Logs anzeigen

```bash
tail -f logs/app.log
# oder für Ollama-Logs:
tail -f logs/ollama.log
```

### Vollständiger Endpoint-Test

```bash
./TEST_ENDPOINTS.sh
```

---

## 🔍 Debugging

### Prüfe ob Server läuft

```bash
curl -s http://127.0.0.1:8001/health && echo "✅ Server läuft" || echo "❌ Server offline"
```

### Prüfe Port 8001

```bash
netstat -tulpn | grep :8001
# oder mit ss:
ss -tulpn | grep :8001
```

### Prüfe Prozess

```bash
ps aux | grep openwebui_agent_server
```

### Log-Level ändern (temporär)

In `src/openwebui_agent_server.py` Zeile 24:

```python
log_level="DEBUG",  # DEBUG | INFO | WARNING | ERROR
```

---

## ⚙️ Konfiguration anpassen

### Sandbox deaktivieren (bereits erledigt)

`config/config.yaml`:

```yaml
sandbox: false  # ✅ Bereits deaktiviert
```

### Wildcard-Domains (bereits aktiv)

`config/config.yaml`:

```yaml
allowed_domains:
  - "*"  # ✅ Bereits aktiv
```

### Auto-Whitelist aktivieren

`config/config.yaml`:

```yaml
auto_whitelist_enabled: true  # Domains automatisch speichern
auto_whitelist_file: "config/domain_whitelist.yaml"
```

### LLM-Modell ändern

`config/config.yaml`:

```yaml
llm:
  model: "llama3.1"  # Ändern zu anderem Ollama-Modell
```

---

## 🎨 Erweiterte Beispiele

### Marker-Pattern (exakte Code-Übergabe)

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{
      "role": "user", 
      "content": "Erstelle advanced.py mit <<<CONTENT\nimport sys\nprint(f\"Python: {sys.version}\")\n<<<END"
    }],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

### Mehrere Tools in einer Anfrage

```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [{
      "role": "user", 
      "content": "Erstelle multi.txt mit Multiple Tools, dann lies die Datei"
    }],
    "stream": false
  }' | jq -r '.choices[0].message.content'
```

---

## 📊 Response-Struktur

### Health Check Response

```json
{
  "status": "ok",
  "server_time": 1731763200,
  "model": "llama3.1",
  "sandbox": false,
  "sandbox_path": "~/localagent_sandbox",
  "allowed_domains": ["*"],
  "auto_whitelist_enabled": true,
  "auto_whitelist_count": 4,
  "open_webui_port": 3000
}
```

### Chat Completion Response

```json
{
  "id": "chatcmpl-a1b2c3d4",
  "object": "chat.completion",
  "created": 1731763200,
  "model": "localagent-pro",
  "choices": [{
    "index": 0,
    "finish_reason": "stop",
    "message": {
      "role": "assistant",
      "content": "🤖 LocalAgent-Pro hat deine Anfrage bearbeitet:\n\n✏️ Datei schreiben:\n✅ Datei erstellt (Live: /path/to/file.txt)\n📝 25 Zeichen geschrieben"
    }
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 25,
    "total_tokens": 35
  }
}
```

---

## 🚨 Fehlerbehandlung

### 400 Bad Request

```bash
# Fehler: Leerer Prompt
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": ""}'

# Response:
{
  "error": "Kein Prompt angegeben",
  "hint": "Sende GET mit ?prompt=... oder POST mit {\"prompt\": \"...\"}",
  "examples": {
    "GET": "/test?prompt=Lies%20demo.py",
    "POST": "{\"prompt\": \"Erstelle demo.py mit print('Hello')\"}"
  }
}
```

### 500 Internal Server Error

```bash
# Server-Logs prüfen:
tail -f logs/app.log

# Typische Ursachen:
# - Ollama nicht erreichbar
# - Ungültige Konfiguration
# - Fehlende Berechtigungen
```

---

## ✅ Checkliste für Production

- [ ] Server läuft: `curl http://127.0.0.1:8001/health`
- [ ] Sandbox-Status geprüft: `sandbox: false` ✅
- [ ] Domains konfiguriert: Wildcard `*` ✅
- [ ] Logging aktiv: `logs/app.log` existiert
- [ ] Ollama erreichbar: `ollama list`
- [ ] OpenWebUI verbunden: API Base URL gesetzt
- [ ] Auto-Whitelist funktioniert: `curl /whitelist`
- [ ] Marker-Pattern getestet: `<<<CONTENT...<<<END` ✅

---

**🎯 Tipp für Linux Mint:**
Füge den Server zu Autostart hinzu:

```bash
# ~/.config/autostart/localagent-pro.desktop
[Desktop Entry]
Type=Application
Name=LocalAgent-Pro Server
Exec=/home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro/start_server.sh
Terminal=true
```

---

**Erstellt:** 16. November 2025  
**System:** Linux Mint 22.2  
**Server:** LocalAgent-Pro v1.0
