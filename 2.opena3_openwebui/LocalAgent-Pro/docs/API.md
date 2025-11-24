# 📡 API Documentation - LocalAgent-Pro

Complete API reference for LocalAgent-Pro.

---

## Base URL

```
http://localhost:8001
```

---

## Authentication

Currently no authentication required (local development only).

**Production:** Use API keys or JWT tokens.

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Check server status

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "sandbox": "/home/user/localagent_sandbox",
  "timestamp": "2025-11-21T10:30:00"
}
```

**Example:**
```bash
curl http://localhost:8001/health
```

---

### 2. List Models

**Endpoint:** `GET /v1/models`

**Description:** Get available AI models

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "llama3.1:8b-instruct-q4_K_M",
      "object": "model",
      "created": 1700000000,
      "owned_by": "localagent-pro"
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8001/v1/models
```

---

### 3. Chat Completions

**Endpoint:** `POST /v1/chat/completions`

**Description:** Send chat message and get AI response

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hallo!"
    }
  ]
}
```

**Response:**
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "llama3.1:8b-instruct-q4_K_M",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hallo! Wie kann ich helfen?"
      },
      "finish_reason": "stop"
    }
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hallo!"}
    ]
  }'
```

---

### 4. Prometheus Metrics

**Endpoint:** `GET /metrics`

**Description:** Get Prometheus-compatible metrics

**Response:**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="POST",endpoint="/v1/chat/completions"} 42

# HELP sandbox_files Total files in sandbox
# TYPE sandbox_files gauge
sandbox_files 5
```

**Example:**
```bash
curl http://localhost:8001/metrics
```

---

## Tool Calling

LocalAgent-Pro automatically detects tool calls in user messages.

### Available Tools

#### 1. write_file

**Trigger:** Keywords: "erstelle", "write", "create"

**Example:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Erstelle config.yaml\nport: 8080\nhost: 0.0.0.0"
    }
  ]
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Tool executed: {\n  \"status\": \"success\",\n  \"message\": \"File created: config.yaml\"\n}"
      }
    }
  ]
}
```

#### 2. read_file

**Trigger:** Keywords: "lies", "read"

**Example:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Lies config.yaml"
    }
  ]
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "content": "Tool executed: {\n  \"status\": \"success\",\n  \"content\": \"port: 8080\\nhost: 0.0.0.0\"\n}"
      }
    }
  ]
}
```

#### 3. delete_file

**Trigger:** Keywords: "lösche", "delete"

**Example:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Lösche old_config.yaml"
    }
  ]
}
```

#### 4. shell_exec

**Trigger:** Keywords: "führe aus", "execute", "command"

**Example:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Führe aus: ls -la"
    }
  ]
}
```

**Whitelisted Commands:**
- `ls`, `cat`, `grep`, `echo`, `pwd`, `date`, `whoami`, `uname`

#### 5. fetch_webpage

**Trigger:** Keywords: "hole", "fetch", URLs starting with "http"

**Example:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hole https://api.github.com"
    }
  ]
}
```

**Whitelisted Domains:**
- `example.com`, `api.github.com`, `httpbin.org`

---

## Error Handling

### Error Response Format

```json
{
  "error": "Error message here"
}
```

### HTTP Status Codes

- `200 OK` - Successful request
- `400 Bad Request` - Invalid request format
- `429 Too Many Requests` - Duplicate request detected
- `500 Internal Server Error` - Server error

### Common Errors

#### 1. Duplicate Request

```json
{
  "error": "Duplicate request"
}
```

**Status:** 429

**Cause:** MD5 hash collision in request cache

#### 2. Security Error

```json
{
  "error": "Path traversal detected: ../../../etc/passwd"
}
```

**Status:** 500

**Cause:** Security violation (path traversal, dangerous command, etc.)

#### 3. File Not Found

```json
{
  "status": "error",
  "message": "File not found: config.yaml"
}
```

**Cause:** File doesn't exist in sandbox

---

## Rate Limiting

Currently no rate limiting (local development).

**Production:** Implement rate limiting:
- 100 requests/minute per IP
- 1000 requests/hour per API key

---

## Security

### Sandbox Isolation

All file operations are restricted to:
```
~/localagent_sandbox/
```

### Command Whitelisting

Only whitelisted commands allowed:
```yaml
- ls, cat, grep, echo, pwd, date, whoami, uname
```

### Domain Whitelisting

Only whitelisted domains accessible:
```yaml
- example.com
- api.github.com
- httpbin.org
```

### Request Deduplication

MD5-based caching prevents duplicate requests:
- Cache size: 1000 requests
- Detection: MD5 hash of request JSON

---

## Examples

### Python Client

```python
import requests

# Chat completion
response = requests.post(
    'http://localhost:8001/v1/chat/completions',
    json={
        'messages': [
            {'role': 'user', 'content': 'Hallo!'}
        ]
    }
)

print(response.json())
```

### JavaScript Client

```javascript
fetch('http://localhost:8001/v1/chat/completions', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    messages: [
      {role: 'user', content: 'Hallo!'}
    ]
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

### Curl Examples

```bash
# Health check
curl http://localhost:8001/health

# List models
curl http://localhost:8001/v1/models

# Chat completion
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hallo!"}]}'

# Create file
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Erstelle hello.txt\nHello World!"}]}'

# Read file
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Lies hello.txt"}]}'
```

---

## WebSocket Support (Future)

**Planned:** Real-time streaming responses

```javascript
const ws = new WebSocket('ws://localhost:8001/v1/chat/stream');

ws.send(JSON.stringify({
  messages: [{role: 'user', content: 'Hallo!'}]
}));

ws.onmessage = (event) => {
  console.log(JSON.parse(event.data));
};
```

---

## Changelog

### v1.0.0 (2025-11-21)
- Initial release
- Chat completions
- Tool calling (file ops, shell, web)
- Health check
- Prometheus metrics

---

**📚 More:** [README.md](../README.md) | [Security](../SECURITY.md) | [Quick Start](../QUICK_START.md)
