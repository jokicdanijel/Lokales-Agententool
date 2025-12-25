# Dashboard-Agent (opena20) - Processed Core Version

## 1. Funktion

### Hauptaufgaben

- Aggregiert Systemmetriken
- Liest Safepoint-Raten
- Zeigt Health-Status aller Agents
- Konsumiert archivp/index.jsonl
- Liefert SSE-Events an das Frontend

### Rolle

- Zentrale Monitoring-Instanz
- System-Health-Aggregator
- SSE-Event-Publisher
- Agent-Registry-Manager

## 2. Endpunkte

### Core Routes

```
GET  /dashboard/health        # Health-Check
GET  /dashboard/events        # SSE-Stream
GET  /dashboard/system        # System-Metrics
GET  /dashboard/safepoints    # Safepoint-Stats
```

### Extended Routes

```
GET  /api/status/all          # All Agents Status
POST /api/command             # Execute Command
GET  /api/openwebui/status    # OpenWebUI Status
POST /api/openwebui/chat      # OpenWebUI Chat
```

## 3. Datenquellen

### Archivp

- index.jsonl (Safepoint-Index)
- DEDUP_INDEX.json (Dedupe-Stats)
- blobs/metrics/ (Metrics-Daten)

### Logs

- logs/opena1.log
- logs/opena2.log
- logs/kordp.log
- logs/dashboard.log

### Agent-Health

- HTTP-Calls zu /health Endpoints
- Port 12344-12350
- Timeout: 5s

### Ports & Policy

- config/registry.json
- Port-Policy-Validator
- Allowed: 12344-12399
- Forbidden: 8080

## 4. Aufgaben

### Monitoring

- Agent-Health-Checks (alle 10s)
- Safepoint-Rate-Tracking
- Port-Availability-Checks
- Disk-Space-Monitoring

### Alerting

- Agent-Down-Detection
- Safepoint-Failure-Alerts
- Port-Conflict-Warnings
- Disk-Full-Alerts

### Anomalieerkennung

- Safepoint-Rate-Spikes
- Response-Time-Anomalien
- Error-Rate-Increases
- Dedupe-Hit-Rate-Anomalien

### UI-Updates

- SSE-Event-Publishing
- Real-Time-Metrics
- Agent-Status-Updates
- Safepoint-Stream

## 5. Port-Policy

### Compliance

- nutzt 12344-12399 (erlaubt)
- niemals 8080 (verboten)
- Middleware-Enforcement
- Registry-Validation

### Port-Assignment

- Dashboard: 12349
- OpenWebUI Adapter: 12350

## 6. SSE-Bus

### Event-Types

- "health" - Agent-Health-Updates
- "safepoint" - Neuer Safepoint
- "command" - Command-Execution
- "chat" - Chat-Message
- "alert" - System-Alert

### Implementation

```python
class SSEBus:
    async def publish(event_type, data):
        for client in clients:
            await client.send(event_type, data)
```

## 7. Metrics

### Safepoint-Metrics

- Total Safepoints
- Safepoint Rate (per minute)
- CMD/RESP Ratio
- Average Size

### Agent-Metrics

- Active Agents
- Response Times
- Error Rates
- Uptime

### System-Metrics

- Disk Usage
- CPU Usage
- Memory Usage
- Network I/O

## 8. Security

### Authentication

- HTTPBearer Token
- .env Storage
- localStorage im UI

### Rate-Limiting

- 5 req/min fuer /api/openwebui/chat
- slowapi Middleware

### CORS

- Nur von 127.0.0.1:12349
- Credentials allowed
- Strict Origin-Check
