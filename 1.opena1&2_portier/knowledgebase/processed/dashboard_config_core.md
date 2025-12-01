# Dashboard-Konfiguration - Processed Core Version

## 1. Ziel

### Visualisierung der gesamten Systemgesundheit
- Real-Time System-Status
- Agent-Health-Monitoring
- Safepoint-Statistics
- Error-Tracking
- Performance-Metrics

### Live-Ueberwachung (SSE)
- Server-Sent Events
- Push-Notifications
- Real-Time-Updates
- No-Polling
- Low-Latency

### Anzeige der Agents, Ports, Safepoints
- Agent-Status-Grid
- Port-Availability-Matrix
- Safepoint-Timeline
- Event-Stream
- Tool-Registry

## 2. Module

### Systemstatus
- CPU-Usage
- Memory-Usage
- Disk-Usage
- Network-I/O
- Uptime

### Safepoint-Ueberblick
- Total Safepoints
- Safepoint-Rate (per minute)
- CMD/RESP Ratio
- Latest Safepoints
- Error-Rate

### Event-Monitor
- SSE-Event-Stream
- Real-Time-Events
- Event-Types (chat, health, command, alert)
- Event-History
- Event-Search

### Prozess-Uebersicht
- Running Processes
- PID-Tracking
- Process-Health
- Resource-Usage
- Auto-Restart-Status

### Agent-Health
- opena1-opena20 Status
- Response-Times
- Error-Rates
- Last-Seen-Timestamp
- Health-Check-Results

## 3. Datenquellen

### archivp/index.jsonl
- Safepoint-Index
- CMD/RESP Tracking
- Source/Destination
- Timestamps
- Paths

### logs/
- opena1.log
- opena2.log
- kordp.log
- dashboard.log
- tool_*.log

### Knowledge-Index
- knowledge/index.json
- Processed-Documents
- Embeddings
- Search-Index

### Port-Lease
- Active Port-Assignments
- Port-Conflicts
- Port-History
- Availability-Matrix

### Tool-Registry
- config/registry.json
- Registered Tools
- Tool-Status
- Port-Mapping
- Health-Endpoints

## 4. Darstellung

### Tabellen
```html
<table class="agent-status-table">
  <thead>
    <tr>
      <th>Agent</th>
      <th>Port</th>
      <th>Status</th>
      <th>Last-Seen</th>
      <th>Response-Time</th>
    </tr>
  </thead>
  <tbody>
    <!-- Dynamic Rows via JavaScript -->
  </tbody>
</table>
```

### Status-Badges
```html
<span class="badge badge-success">Healthy</span>
<span class="badge badge-warning">Degraded</span>
<span class="badge badge-danger">Down</span>
<span class="badge badge-info">Starting</span>
```

### Port-Monitor
```
Port 12344 [opena1]     : ● Online  (Response: 45ms)
Port 12345 [opena2]     : ● Online  (Response: 32ms)
Port 12346 [kordp]      : ● Online  (Response: 28ms)
Port 12347 [opena3]     : ● Online  (Response: 51ms)
Port 12348 [opena4]     : ○ Offline
Port 12349 [Dashboard]  : ● Online  (Response: 12ms)
Port 12350 [Adapter]    : ● Online  (Response: 18ms)
```

### Routing-Graph
```
[OpenAI] → [opena1] → [opena2] → [kordp] → [Tool]
                          ↓
                    [Safepoint]
                          ↓
                    [index.jsonl]
```

## 5. Policy

### Strict:true
```javascript
// Frontend-Validation
function validateResponse(data) {
  if (!data.hasOwnProperty('strict') || data.strict !== true) {
    throw new Error("Response must have strict:true");
  }
  // No additional properties allowed
  const allowedKeys = ['status', 'agents', 'safepoints', 'strict'];
  const extraKeys = Object.keys(data).filter(k => !allowedKeys.includes(k));
  if (extraKeys.length > 0) {
    throw new Error(`Extra keys not allowed: ${extraKeys}`);
  }
}
```

### Nichts wird gecacht ohne Archivator
- Alle Dashboard-Daten via opena2
- Kein lokales Caching
- Immer Fresh-Data
- Safepoint-basiert

## 6. API-Endpoints

### GET /api/status/all
```json
{
  "timestamp": "2025-11-21T12:00:00Z",
  "agents": [
    {
      "name": "opena1",
      "port": 12344,
      "status": "healthy",
      "response_time_ms": 45,
      "last_seen": "2025-11-21T11:59:58Z"
    }
  ],
  "safepoints": {
    "total": 1234,
    "rate_per_minute": 5.2,
    "cmd_resp_ratio": 1.0
  },
  "strict": true
}
```

### GET /api/safepoints/latest
```json
{
  "safepoints": [
    {
      "sp_id": "00123",
      "timestamp": "2025-11-21T11:59:55Z",
      "src": "opena1",
      "dst": "kordp",
      "type": "CMD"
    }
  ],
  "strict": true
}
```

### GET /sse/events
```
event: health
data: {"agent":"opena1","status":"healthy"}

event: safepoint
data: {"sp_id":"00124","type":"CMD"}

event: chat
data: {"message":"Test","user":"admin"}
```

## 7. UI-Components

### Agent-Status-Card
```html
<div class="agent-card" data-agent="opena1">
  <div class="agent-header">
    <h3>opena1 - Koordinator</h3>
    <span class="badge badge-success">Healthy</span>
  </div>
  <div class="agent-body">
    <p>Port: 12344</p>
    <p>Response-Time: 45ms</p>
    <p>Last-Seen: 2 seconds ago</p>
  </div>
</div>
```

### Safepoint-Timeline
```html
<div class="timeline">
  <div class="timeline-item">
    <span class="time">11:59:55</span>
    <span class="event">CMD: opena1 → kordp</span>
  </div>
  <div class="timeline-item">
    <span class="time">11:59:56</span>
    <span class="event">RESP: kordp → opena1</span>
  </div>
</div>
```

### Event-Stream
```html
<div id="event-stream">
  <!-- Auto-Updated via SSE -->
</div>

<script>
const sse = new EventSource('/sse/events');
sse.addEventListener('health', (e) => {
  const data = JSON.parse(e.data);
  updateAgentStatus(data.agent, data.status);
});
</script>
```

## 8. Security

### Authentication
- Bearer-Token required
- Token from localStorage
- HTTPBearer Middleware
- 401 on Invalid-Token

### Rate-Limiting
- 10 req/sec per Client
- slowapi Middleware
- 429 on Exceed

### CORS
- Only from 127.0.0.1:12349
- Credentials allowed
- Strict Origin-Check

## 9. Performance

### SSE-Optimization
- Keep-Alive every 30s
- Client-Reconnect on Disconnect
- Server-Side Event-Buffering
- Low-Latency Push

### Lazy-Loading
- Initial Load: Essential Data only
- On-Demand: Details via Click
- Pagination: Large Lists
- Infinite-Scroll: Event-Stream

### Caching-Strategy
- No Client-Cache (Strict Policy)
- Server-Side: Memory-Cache (60s TTL)
- Redis (optional): Shared Cache
- Invalidate on Safepoint-Write
