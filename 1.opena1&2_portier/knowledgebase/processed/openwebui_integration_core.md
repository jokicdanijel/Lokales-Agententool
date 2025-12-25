# OpenWebUI Integration (opena3) - Processed Core Version

## 1. Architecture

### Flow

```
User → OpenWebUI (8080) → Adapter (12350) → opena3 (12347) → Option-2-Flow
```

### Components

- **OpenWebUI UI** - Port 8080 (Docker)
- **Adapter** - Port 12350 (HTTP-Forwarder)
- **opena3 Agent** - Port 12347 (FastAPI)
- **Option-2 Integration** - via opena1 → opena2 → kordp

## 2. Adapter Pattern

### openwebui_adapter.py

```python
# Port 12350
# Forwardet HTTP-Requests von Dashboard → OpenWebUI

@app.post("/openwebui/chat")
async def chat(request: ChatRequest):
    # Forward to OpenWebUI
    response = await http_client.post(
        "http://127.0.0.1:8080/api/chat",
        json=request.dict()
    )
    return response.json()
```

### Responsibilities

- HTTP-Forwarding
- Request-Transformation
- Response-Mapping
- Error-Handling

## 3. Port 8080 - UI Only

### Docker-Container

```yaml
services:
  openwebui:
    image: open-webui/open-webui:main
    ports:
      - "8080:8080"
    volumes:
      - ./data:/app/backend/data
```

### Restrictions

- **NUR Frontend-Assets**
- Keine Backend-Logik
- Keine API-Routes (ausser UI)
- Keine FastAPI-Services
- Keine Agent-Kommunikation

### Enforcement

```python
# Port-Policy prueft:
if port == 8080 and service_type == "backend":
    raise Forbidden("Port 8080 nur fuer UI")
```

## 4. opena3 Agent

### main_openwebui_agent.py

```python
# Port 12347
# Agent-Wrapper um OpenWebUI-Terminal

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "opena3"}

@app.post("/command")
async def command(cmd: Command):
    # Startet Chat via OpenWebUI
    ...

@app.post("/invoke")
async def invoke(action: Action):
    # Direkte Tool-Invocation
    ...
```

### Responsibilities

- Command-Handling
- OpenWebUI-Integration
- Option-2-Flow-Compliance
- Response-Generation

## 5. Endpoints

### Dashboard-Endpoints

```python
# In main_dashboard.py (Port 12349)

@app.get("/api/openwebui/status")
async def openwebui_status():
    # Health-Check opena3
    response = await http_client.get("http://127.0.0.1:12347/health")
    return response.json()

@app.post("/api/openwebui/chat")
@limiter.limit("5/minute")
async def openwebui_chat(request: ChatRequest):
    # Chat-Request (rate-limited)
    # SSE-Event published
    await sse_bus.publish("chat", request.dict())
    ...
```

### opena3-Endpoints

```python
# main_openwebui_agent.py (Port 12347)

GET  /health           # Health-Check
POST /command          # Command-Execution
POST /invoke           # Tool-Invocation
```

### Adapter-Endpoints

```python
# openwebui_adapter.py (Port 12350)

POST /openwebui/chat   # Chat-Forwarding
GET  /openwebui/health # Health-Check
```

## 6. Integration Flow

### Chat-Request

1. User → Dashboard UI (12349)
2. Dashboard → opena3 (12347)
3. opena3 → opena1 (12344) - Option-2
4. opena1 → opena2 → kordp → Tool
5. Tool → opena2 → opena1 → opena3
6. opena3 → Dashboard → User

### Health-Check

1. Dashboard → GET /api/openwebui/status
2. Dashboard → opena3 /health
3. opena3 → 200 OK
4. Dashboard → Response

## 7. Security

### Bearer-Token

- Alle /api/openwebui/\* Routen
- Token aus .env
- localStorage im UI

### Rate-Limiting

- 5 req/min fuer /api/openwebui/chat
- slowapi Middleware

### CORS

- Nur von 127.0.0.1:12349
- Credentials allowed

## 8. Error-Handling

### 502 Bad Gateway

```json
{
  "error": "OPENWEBUI_UNREACHABLE",
  "message": "OpenWebUI nicht erreichbar",
  "port": 8080
}
```

### 504 Gateway Timeout

```json
{
  "error": "OPENWEBUI_TIMEOUT",
  "message": "OpenWebUI antwortet nicht",
  "timeout": 30
}
```

### 401 Unauthorized

```json
{
  "error": "INVALID_TOKEN",
  "message": "Bearer-Token ungueltig"
}
```

## 9. Testing

### Health-Check

```bash
curl -s http://127.0.0.1:12347/health | jq .
```

### Chat-Request

```bash
curl -X POST http://127.0.0.1:12349/api/openwebui/chat \
  -H "Authorization: Bearer $BEARER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'
```

### Status-Check

```bash
curl -s http://127.0.0.1:12349/api/openwebui/status \
  -H "Authorization: Bearer $BEARER_TOKEN" | jq .
```
