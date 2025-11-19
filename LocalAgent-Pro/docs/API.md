# 📚 API Dokumentation

Vollständige OpenAPI/Swagger Dokumentation für LocalAgent-Pro.

## 🚀 Quick Start

### Swagger-UI lokal anzeigen

```bash
# Option 1: Mit Swagger Editor (Browser)
cd LocalAgent-Pro/docs
npx @apidevtools/swagger-cli serve openapi.yaml

# Option 2: Mit Redoc (Browser)
npx @redocly/cli preview-docs openapi.yaml

# Option 3: Mit Docker
docker run -p 8080:8080 -v $(pwd)/docs:/app swaggerapi/swagger-ui
# Öffne http://localhost:8080/?url=/app/openapi.yaml
```

### OpenAPI-Spec validieren

```bash
# Mit Swagger CLI
npx @apidevtools/swagger-cli validate docs/openapi.yaml

# Mit Redocly CLI
npx @redocly/cli lint docs/openapi.yaml
```

## 📋 Endpoints

### Chat Completion API

**POST** `/v1/chat/completions`

OpenAI-kompatible Chat-API für AI Agent Interaktion.

**Request:**
```json
{
  "model": "localagent-pro",
  "messages": [
    {
      "role": "user",
      "content": "Erstelle eine Datei hello.txt mit Inhalt 'Hello World'"
    }
  ],
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1732022400,
  "model": "localagent-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Datei hello.txt erfolgreich erstellt.",
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "write_file",
              "arguments": "{\"filename\":\"hello.txt\",\"content\":\"Hello World\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 15,
    "completion_tokens": 25,
    "total_tokens": 40
  }
}
```

**cURL-Beispiel:**
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "localagent-pro",
    "messages": [
      {"role": "user", "content": "Erstelle Datei test.txt"}
    ]
  }'
```

### Health Check

**GET** `/health`

Prüft Server-Status und Ollama-Verbindung.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-19T10:30:00Z",
  "ollama_connected": true,
  "sandbox_path": "/home/user/sandbox"
}
```

**cURL-Beispiel:**
```bash
curl http://localhost:8001/health
```

### Prometheus Metrics

**GET** `/metrics`

Exportiert Prometheus-Metriken im Text-Format.

**Response:**
```
# HELP localagent_requests_total Total number of requests
# TYPE localagent_requests_total counter
localagent_requests_total{endpoint="/v1/chat/completions",method="POST",status="200"} 42.0

# HELP localagent_tool_calls_total Total number of tool calls
# TYPE localagent_tool_calls_total counter
localagent_tool_calls_total{status="success",tool_name="write_file"} 15.0
```

**cURL-Beispiel:**
```bash
curl http://localhost:8001/metrics
```

## 🛠️ Tools

LocalAgent-Pro unterstützt folgende Tools:

### 1. write_file

Erstellt oder überschreibt Datei in Sandbox.

**Arguments:**
```json
{
  "filename": "hello.txt",
  "content": "Hello World"
}
```

**Beispiel:**
```json
{
  "role": "user",
  "content": "Erstelle Datei config.json mit {\"debug\": true}"
}
```

### 2. read_file

Liest Datei aus Sandbox.

**Arguments:**
```json
{
  "filename": "hello.txt"
}
```

**Beispiel:**
```json
{
  "role": "user",
  "content": "Lese den Inhalt von config.json"
}
```

### 3. delete_file

Löscht Datei aus Sandbox.

**Arguments:**
```json
{
  "filename": "old_file.txt"
}
```

**Beispiel:**
```json
{
  "role": "user",
  "content": "Lösche die Datei old_file.txt"
}
```

### 4. shell_exec

Führt Shell-Befehl aus (whitelisted).

**Erlaubte Befehle:**
- `ls`, `cat`, `grep`, `find`, `pwd`, `echo`, `head`, `tail`, `wc`, `sort`

**Arguments:**
```json
{
  "command": "ls -la"
}
```

**Beispiel:**
```json
{
  "role": "user",
  "content": "Führe 'ls -la' aus"
}
```

**⚠️ Blockierte Befehle:**
- `rm -rf`, `sudo`, `dd`, `chmod 777`, `mkfs`, `reboot`, `shutdown`

### 5. fetch_webpage

Ruft Webseite ab (domain-whitelisted).

**Erlaubte Domains:**
- `github.com`, `wikipedia.org`, `python.org`, `stackoverflow.com`

**Arguments:**
```json
{
  "url": "https://example.com"
}
```

**Beispiel:**
```json
{
  "role": "user",
  "content": "Rufe https://github.com ab"
}
```

## 🔒 Security

### Loop-Protection

- **Timeout:** Identische Requests innerhalb 2 Sekunden blockiert
- **Max Retries:** 1 Retry bei Fehlern
- **Detection:** MD5-basierte Request-Deduplizierung

**Response bei Loop:**
```json
{
  "choices": [{
    "message": {
      "content": "⚠️ Loop-Protection: Identische Anfrage innerhalb 2 Sekunden blockiert"
    }
  }]
}
```

### Sandbox-Isolation

- Alle Dateioperationen in `/sandbox` Verzeichnis
- Escape-Prevention (kein `../` erlaubt)
- Symlink-Blocking

### Shell-Whitelisting

Nur sichere Befehle erlaubt:
```python
ALLOWED_COMMANDS = ['ls', 'cat', 'grep', 'find', 'pwd', 'echo', 'head', 'tail', 'wc', 'sort']
BLOCKED_COMMANDS = ['rm -rf', 'sudo', 'dd', 'chmod 777', 'mkfs', 'reboot']
```

### Domain-Whitelisting

Nur vertrauenswürdige Domains:
```python
ALLOWED_DOMAINS = ['github.com', 'wikipedia.org', 'python.org', 'stackoverflow.com']
```

## 📊 Monitoring

### Verfügbare Metriken

| Metrik | Typ | Labels | Beschreibung |
|--------|-----|--------|--------------|
| `localagent_requests_total` | Counter | `method`, `endpoint`, `status` | Anzahl Requests |
| `localagent_request_duration_seconds` | Histogram | `endpoint` | Request-Latenz |
| `localagent_tool_calls_total` | Counter | `tool_name`, `status` | Tool-Aufrufe |
| `localagent_loop_detections_total` | Counter | - | Loop-Detections |
| `localagent_errors_total` | Counter | `error_type` | Fehler |

### Prometheus-Query-Beispiele

```promql
# Request-Rate (letzte 5 Minuten)
rate(localagent_requests_total[5m])

# Erfolgreiche Tool-Calls
localagent_tool_calls_total{status="success"}

# 95th Percentile Latenz
histogram_quantile(0.95, localagent_request_duration_seconds_bucket)

# Loop-Detection-Rate
rate(localagent_loop_detections_total[1h])
```

## 🧪 Testing

### Unit-Tests

```bash
# Alle Tests
./run_tests.sh all

# Nur API-Tests
pytest tests/unit/test_api.py -v

# Mit Coverage
./run_tests.sh coverage
```

### Integration-Tests

```bash
# E2E Workflow-Tests
pytest tests/integration/test_workflows.py -v

# Einzelner Test
pytest tests/integration/test_workflows.py::test_chat_request_write_file -v
```

### cURL-Tests

```bash
# Health Check
curl http://localhost:8001/health

# Chat Completion
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"localagent-pro","messages":[{"role":"user","content":"Test"}]}'

# Metrics
curl http://localhost:8001/metrics | grep localagent
```

## 🔄 Versionierung

- **Aktuell:** v1.0.0
- **API-Version:** `/v1/chat/completions`
- **OpenAPI-Spec:** 3.0.3

**Breaking Changes:**
- v1.0 → v2.0: API-Key-Authentifizierung wird Pflicht

## 📖 Weitere Ressourcen

- **GitHub:** https://github.com/jokicdanijel/Lokales-Agententool
- **OpenAPI-Spec:** `docs/openapi.yaml`
- **Swagger-UI:** Lokal via `npx @apidevtools/swagger-cli serve`
- **Redoc:** Lokal via `npx @redocly/cli preview-docs`

---

**Status:** ✅ Vollständige API-Dokumentation  
**OpenAPI-Version:** 3.0.3  
**Letztes Update:** 19. November 2025
