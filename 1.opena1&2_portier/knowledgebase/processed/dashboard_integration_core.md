# Dashboard Integration (opena20) - Processed Core Version

## 1. FastAPI Setup

### Framework
- FastAPI 0.104+
- Uvicorn ASGI Server
- Async/Await Pattern
- Port: 12349

### Dependencies
```python
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
slowapi  # Rate Limiting
```

## 2. SSE-Bus

### Architektur
- Eigener SSEBus (kein EventSource direkt)
- Async Queue Management
- Event-Type Routing
- Client-Subscription

### Implementation
```python
class SSEBus:
    def __init__(self):
        self.clients = {}
    
    async def publish(self, event_type, data):
        for client_id, queue in self.clients.items():
            await queue.put({"type": event_type, "data": data})
    
    async def subscribe(self, client_id):
        queue = asyncio.Queue()
        self.clients[client_id] = queue
        return queue
```

### Event-Types
- "chat" - Chat-Messages
- "status" - Agent-Status
- "health" - Health-Updates
- "command" - Command-Execution

## 3. Security

### HTTPBearer
```python
from fastapi.security import HTTPBearer

bearer = HTTPBearer()

@app.get("/api/status/all")
async def status(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials
    if token != os.getenv("BEARER_TOKEN"):
        raise HTTPException(401, "Invalid token")
    ...
```

### Token-Management
- .env Storage
- UUID-basiert
- bin/env_bootstrap.sh generiert
- localStorage fuer UI

### CORS
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:12349"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

## 4. Routes

### Core Routes
```python
GET  /health                    # Health-Check
GET  /api/status/all            # All Agents Status
POST /api/command               # Execute Command
GET  /sse/events                # Server-Sent Events
GET  /api/openwebui/status      # OpenWebUI Status
POST /api/openwebui/chat        # OpenWebUI Chat
```

### Security-Anforderungen
- HTTPBearer fuer alle /api/* Routen
- Rate-Limiting fuer /api/openwebui/chat
- Strict JSON (additionalProperties: false)
- Logging auf INFO level

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/openwebui/chat")
@limiter.limit("5/minute")
async def chat(...):
    ...
```

## 5. Agent-Registry

### Integration
```python
from agent_registry import AgentRegistry

registry = AgentRegistry()
registry.register_if_absent("opena1", "http://127.0.0.1:12344")
registry.register_if_absent("opena2", "http://127.0.0.1:12345")
```

### Functions
- `register_if_absent(name, endpoint)` - Idempotent
- `list_agents()` - Compact list
- `persist()` - Save to JSON
- `load()` - Load from JSON

### Persistence
```json
{
  "agents": [
    {
      "name": "opena1",
      "endpoint": "http://127.0.0.1:12344",
      "port": 12344,
      "status": "active"
    }
  ]
}
```

## 6. Logging

### Struktur
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/dashboard.log"),
        logging.RotatingFileHandler("logs/dashboard.log", maxBytes=10*1024*1024, backupCount=5)
    ]
)
```

### Log-Levels
- ERROR - Kritische Fehler
- WARNING - Warnungen
- INFO - Normale Operationen
- DEBUG - Detail-Informationen (nur DEV-Mode)

## 7. UI Integration

### ui_index.html
- Chat-Modal (`#openwebuiModal`)
- Token-Handling via localStorage
- State-Indicators (loading/ok/error)
- Fetch API mit Authorization Header

### JavaScript
```javascript
const token = localStorage.getItem('bearer_token');
const response = await fetch('/api/openwebui/chat', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: "Test" })
});
```

## 8. Monitoring

### Prometheus-Metrics
- GET /metrics - Prometheus Endpoint
- Request-Counts
- Latency-Histograms
- Error-Rates

### Health-Checks
- GET /health - Simple Health
- GET /api/status/all - Detailed Status
- SSE-Events fuer Live-Updates
