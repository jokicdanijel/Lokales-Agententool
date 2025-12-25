# **OpenWebUI Agent V2 – Technische Dokumentation (Hyper-Dashboard-GL Format)**

**Version:** 2.0.0
**Build:** 2025-11-29
**PORTIER Compliance:** 3.0
**Kategorie:** Enterprise Agent Module
**Status:** ✅ Production Ready

---

## 1. Zweck des Moduls

Der OpenWebUI Agent V2 stellt die Kommunikationsschicht zwischen dem PORTIER-3.0-Backbone (opena1 → opena2 → kordp) und der lokalen OpenWebUI-Instanz dar.
Er abstrahiert Kommandos, orchestriert Safepoints und liefert UI-kompatible Chat-Antworten.

### Kernfunktionen

- **Option-2-Flow Compliance:** Vollständige Integration in PORTIER 3.0 Architektur
- **Bearer Authentication:** Enterprise-grade Sicherheit
- **Safepoint System:** Automatische Archivierung aller Operationen
- **Native Chat Processing:** Direkter OpenAI-kompatible Chat-Verarbeitung
- **Web Panel Interface:** Deployable HTML/CSS/JS Control Panel
- **Python SDK:** Typed async client library

---

## 2. Architekturübersicht

```
OpenAI → opena1 → opena2 → kordp → opena3 → OpenWebUI
                     ↓              ↑
               Safepoints      Live Dispatch
```

### Datenfluss

1. **Inbound:** OpenAI CMD → Option-2-Flow → opena3
2. **Processing:** CMD Validation → OpenWebUI Dispatch → Response Generation
3. **Outbound:** Response → Safepoint → opena2 → opena1 → OpenAI
4. **Parallel:** Native Chat → Direct Processing → UI Response

---

## 3. Verantwortlichkeiten

### Core Responsibilities

1. **CMD Envelope Processing:** Verarbeitung von Option-2-Flow CMD-Envelopes
2. **Native Chat Processing:** Chat-Verarbeitung inklusive Model-Routing
3. **Status Management:** Health-, Dispatch- und System-Signalisierung
4. **Safepoint Operations:** Erstellung und Archivierung von Safepoints
5. **Security Layer:** Bearer-authentifizierte REST-Schnittstelle
6. **Dashboard Integration:** SSE-Streaming für UI-Dashboards

### Service Boundaries

- **Input:** HTTP REST API (Port 12347)
- **Output:** OpenWebUI Terminal, Safepoint Archive, SSE Events
- **Dependencies:** kordp Gateway (12346), OpenWebUI (8080)
- **State:** Stateless service, persistent Safepoints only

---

## 4. API Endpoints

| Endpoint          | Method | Funktion                | Auth | Flow     | Rate Limit |
| ----------------- | ------ | ----------------------- | ---- | -------- | ---------- |
| `/health`         | GET    | Gesundheitszustand      | –    | Direct   | –          |
| `/native`         | POST   | Chat direkt von UI      | ✓    | Direct   | 5/min      |
| `/cmd`            | POST   | CMD-Envelope aus opena1 | ✓    | Option-2 | –          |
| `/dispatch_ready` | GET    | Routing-Status          | ✓    | Option-2 | –          |
| `/selftest`       | GET    | Gesamt-Modultest        | ✓    | Direct   | 1/min      |

### Request/Response Schemas

#### CMD Envelope (Strict JSON)

```json
{
  "request_id": "string (required)",
  "timestamp": "string (ISO 8601, required)",
  "source": "string (required)",
  "command": "string (required)",
  "payload": "object (required)"
}
```

#### Native Chat Request

```json
{
  "prompt": "string (required, min_length=1)",
  "model": "string (default: gpt-4)",
  "temperature": "float (0.0-2.0, default: 0.7)",
  "max_tokens": "integer (optional)"
}
```

---

## 5. Safepoint-System

### Safepoint Generation

Jede Operation erzeugt ein Paar aus:

- **CMD →** Safepoint (Ursprungsdaten, Request)
- **RESP →** Safepoint (Antwortdaten, Response)

### Naming Convention

```
archivp/YYYY/MM/DD/SP<timestamp>_opena3→opena2_CMD.json
archivp/YYYY/MM/DD/SP<timestamp>_opena3→opena2_RESP.json
```

### Index System

```jsonl
{
  "sp_id": "001234",
  "timestamp": "2025-11-29T12:00:00Z",
  "src": "opena3",
  "dst": "opena2",
  "type": "CMD",
  "path": "2025/11/29/SP001234_opena3→opena2_CMD.json"
}
```

### Security

- Alle Secrets werden maskiert (`"****"`)
- Bearer Tokens redacted
- PII-Daten anonymisiert
- Full audit trail persistent

---

## 6. Dispatcher-Integration

### Auto-Registration

Der Agent registriert sich beim Start automatisch am kordp Router:

```http
POST http://127.0.0.1:12346/dispatch/register
Authorization: Bearer <token>

{
  "service_id": "opena3",
  "service_target": "openwebui",
  "capabilities": ["chat", "terminal", "openwebui"],
  "port": 12347,
  "health_endpoint": "/health"
}
```

### Dispatch Flow

1. **Registration:** opena3 → kordp (`/dispatch/register`)
2. **Ready Check:** kordp → opena3 (`/dispatch_ready`)
3. **CMD Routing:** opena2 → kordp → opena3 (`/cmd`)
4. **Response Chain:** opena3 → kordp → opena2

---

## 7. Monitoring & Telemetrie

### Health Metrics

- **Service Status:** `ok` | `degraded` | `error`
- **Uptime:** Seconds since service start
- **Last CMD:** Timestamp of last processed command
- **Dependencies:** Status of kordp, OpenWebUI, Safepoint system

### Performance Metrics

- **Response Time:** Average CMD processing time
- **Success Rate:** Percentage of successful operations
- **Error Rate:** Failed operations per time window
- **Throughput:** Commands per minute

### Telemetry Export

- **SSE Events:** Real-time metrics to Dashboard
- **Structured Logs:** JSON format for log aggregation
- **Health Endpoint:** Prometheus-compatible metrics

---

## 8. Sicherheit

### Authentication

- **Bearer Token:** Required for all protected endpoints
- **Token Validation:** JWT or UUID format enforcement
- **Token Storage:** Environment variable only (`BEARER_TOKEN`)

### Authorization

- **CORS Policy:** Restrictive, Admin-UI only
- **Rate Limiting:** Protection against abuse
- **Input Validation:** Strict JSON schema enforcement

### Security Headers

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

---

## 9. Betrieb

### Deployment Modes

- **Production Mode:** Full security, rate limiting, audit logging
- **Development Mode:** Relaxed CORS, verbose logging, mock backends
- **Mock Mode:** Simulated responses when OpenWebUI offline

### Service Properties

- **Stateless:** No persistent state beyond Safepoints
- **Restart-Safe:** Automatic recovery, no data loss
- **Zero-Downtime:** Rolling deployment support
- **Resource Efficient:** Minimal memory footprint

### Configuration

```bash
# Required Environment Variables
BEARER_TOKEN=<uuid>
ARCHIVP_ROOT=/path/to/archivp
KORDP_URL=http://127.0.0.1:12346
OPENWEBUI_URL=http://127.0.0.1:8080

# Optional Configuration
DEV_MODE=false
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=5
TIMEOUT_SECONDS=30
```

---

## 10. Web Panel Interface

### Deployment

```bash
# Docker One-Liner
cd webpanel/
./build-and-run.sh
# Access: http://localhost:8088
```

### Features

- **Dark Theme:** Enterprise-grade UI
- **Real-time Testing:** Live API interaction
- **Token Management:** Persistent localStorage
- **Error Handling:** User-friendly error display
- **Mobile Responsive:** Full device compatibility

### Technology Stack

- **Frontend:** Pure HTML/CSS/JavaScript (no frameworks)
- **Backend Integration:** Fetch API with Bearer auth
- **Deployment:** Nginx + Docker
- **Configuration:** Dynamic base URL detection

---

## 11. Python SDK

### Installation

```bash
pip install ./opena3_sdk
```

### Usage Example

```python
import asyncio
from opena3_sdk import OpenA3Client, CMDRequest

async def main():
    async with OpenA3Client(token="your-token") as client:
        # Health check
        health = await client.health()
        print(f"Status: {health.status}")

        # Native chat
        response = await client.chat("Hello from SDK")
        print(response)

        # CMD dispatch
        cmd = client.create_cmd_request(
            command="chat",
            payload={"prompt": "SDK test"}
        )
        result = await client.cmd_dispatch(cmd)
        print(result)

asyncio.run(main())
```

### Features

- **Async/Await:** Full asyncio compatibility
- **Type Safety:** Pydantic models for all requests/responses
- **Error Handling:** Automatic retry logic with exponential backoff
- **Context Manager:** Proper resource cleanup
- **Bearer Auth:** Automatic token handling

---

## 12. Integration Points

### PORTIER 3.0 Stack

- **opena1:** CMD source via Option-2-Flow
- **opena2:** Safepoint destination and archival
- **kordp:** Gateway and routing layer
- **Dashboard:** SSE events and status reporting

### External Dependencies

- **OpenWebUI:** Chat processing backend (Port 8080)
- **File System:** Safepoint storage (`archivp/`)
- **Environment:** Token and configuration management

### Monitoring Integration

- **Prometheus:** Metrics endpoint `/metrics`
- **Grafana:** Dashboard template included
- **Alerting:** Health check failures, error rate thresholds

---

## 13. Troubleshooting

### Common Issues

| Issue            | Cause                        | Solution                     |
| ---------------- | ---------------------------- | ---------------------------- |
| 401 Unauthorized | Missing/invalid Bearer token | Check `BEARER_TOKEN` env var |
| 502 Bad Gateway  | OpenWebUI not running        | Start OpenWebUI on port 8080 |
| 404 Not Found    | kordp gateway offline        | Verify kordp on port 12346   |
| Rate Limit       | Too many requests            | Wait or adjust rate limits   |

### Debug Commands

```bash
# Health check all services
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:12347/health

# Test dispatch readiness
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:12347/dispatch_ready

# Run full self-test
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:12347/selftest

# Check logs
tail -f logs/opena3.nohup.log
```

---

## 14. Performance Characteristics

### Benchmarks

- **Throughput:** 100+ CMD/second
- **Latency:** <100ms (P95) for health checks
- **Memory:** <128MB resident set size
- **CPU:** <5% utilization under normal load

### Scaling Considerations

- **Horizontal:** Multiple instances behind load balancer
- **Vertical:** Memory scales with concurrent connections
- **Storage:** Safepoint disk usage grows linearly
- **Network:** Bandwidth limited by OpenWebUI backend

---

**Status:** ✅ **PRODUCTION READY**
**Maintainer:** PORTIER 3.0 Team
**Last Updated:** 2025-11-29
**Next Review:** 2025-12-29
