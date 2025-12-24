# Portier Standardized Endpoints & Safepoints

## Overview

All core Portier services expose standardized endpoints and safepoint logging:

| Service | Port  | Health | Endpoint | Safepoint Type |
|---------|-------|--------|----------|----------------|
| opena1  | 12344 | `GET /health` | `POST /log/opena1` | Coordinator logs |
| kordp   | 12346 | `GET /health` | `POST /dispatch/kordp` | Dispatch events |
| archivp | 12348 | `GET /health` | `POST /store/archivp` | Data storage |
| opena2  | 12348 | `GET /health` | `POST /finalize/opena2` | Finalization |

## Health Endpoint

**Request:**
```bash
curl http://127.0.0.1:12344/health | jq .
```

**Response:**
```json
{
  "service": "opena1",
  "status": "online",
  "base": "http://127.0.0.1:12344",
  "port": 12344,
  "port_policy": {
    "allowed_min": 12344,
    "allowed_max": 12399,
    "current_port": 12344,
    "compliant": true
  },
  "timestamp": "2025-11-09T04:45:30Z"
}
```

## Safepoint Endpoints

### Safepoint Request Format

```json
{
  "src": "bootstrap",
  "dst": "opena1",
  "kind": "CMD",
  "payload": {
    "action": "start",
    "timestamp": "2025-11-09T04:45:00Z"
  }
}
```

### Safepoint File Format

Files written with **deterministic naming**:
```
SP<unix_ms>_src→dst_KIND.json
```

**Example:**
```
SP1731139430123_bootstrap→opena1_CMD.json
SP1731139430456_opena1→kordp_RESP.json
```

**File Content:**
```json
{
  "timestamp": "2025-11-09T04:45:30.123Z",
  "src": "bootstrap",
  "dst": "opena1",
  "kind": "CMD",
  "payload": {
    "action": "start"
  }
}
```

### Index Format (index.jsonl)

One line per safepoint:
```
{"path": "SP1731139430123_bootstrap→opena1_CMD.json", "ts": "2025-11-09T04:45:30Z", "src": "bootstrap", "dst": "opena1", "kind": "CMD"}
{"path": "SP1731139430456_opena1→kordp_RESP.json", "ts": "2025-11-09T04:45:31Z", "src": "opena1", "dst": "kordp", "kind": "RESP"}
```

## Usage Example

### 1. Start all services

```bash
make bootstrap
make generate-original  # Starts services in sequence
```

### 2. Test opena1 Health

```bash
curl http://127.0.0.1:12344/health | jq .
```

### 3. Write a Safepoint

```bash
curl -X POST http://127.0.0.1:12344/log/opena1 \
  -H "Content-Type: application/json" \
  -d '{
    "src": "test",
    "dst": "opena1",
    "kind": "CMD",
    "payload": {"msg": "Hello opena1"}
  }' | jq .
```

### 4. Check Archive

```bash
ls -la 1.opena1&2_portier/archivp/SP*.json | head -5
head index.jsonl 1.opena1&2_portier/archivp/
```

## Implementation Pattern

All services use the **PortierServiceBase** template:

```python
from src.portier_service_base import (
    PortierServiceBase,
    PortierServiceConfig,
    PortPolicyMiddleware
)

config = PortierServiceConfig(
    service_name="opena1",
    service_port=12344,
    allowed_port_min=12344,
    allowed_port_max=12399
)

app = FastAPI()
PortPolicyMiddleware(app, config)
service_base = PortierServiceBase(config)
service_base.setup_health_endpoint(app)
service_base.setup_safepoints(app, archiv_dir="./archiv")
```

## Compliance Checks

### Policy Check

```bash
make policy
# ✅ [POLICY] PASS – Port-Policy compliance verified
```

### Port Display

```bash
make ports
# Shows all active ports in range 12344-12399
```

### Health Check

```bash
make health
# ✅ opena1: ONLINE
# ✅ kordp: ONLINE
# ✅ archivp: ONLINE
# ✅ opena2: ONLINE
```

## Audit Trail

Every service operation creates an immutable safepoint file. The complete audit trail is available in:

- **Location:** `1.opena1&2_portier/archivp/SP<timestamp>_<src>→<dst>_<KIND>.json`
- **Index:** `1.opena1&2_portier/archivp/index.jsonl`
- **Query:** `cat index.jsonl | jq 'select(.kind=="CMD")'` to filter by type

## Port Policy Enforcement

All services validate port compliance:
- **Allowed Range:** 12344-12399
- **Exception:** 8080 only for OpenWebUI (2.openwebui/)
- **Enforcement:** Middleware adds response headers
  ```
  X-Portier-Port-Policy: 12344-12399
  X-Portier-Service: opena1
  X-Portier-Port: 12344
  ```

---

**Last Updated:** 2025-11-09
**Version:** 1.0
**Compliance:** ✅ Port-Policy, ✅ Safepoints, ✅ Health-Checks
