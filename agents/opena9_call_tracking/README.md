# opena9_call_tracking

**Port:** 12352  
**Description:** Call analytics and tracking

## Quick Start

```bash
cd opena9_call_tracking
python main.py
```

## Structure

- `bin/` – Scripts and utilities
- `config/` – Configuration files
- `tests/` – Unit and integration tests
- `logs/` – Runtime logs
- `docs/` – Documentation
- `data/` – Static data and resources
- `api/` – API endpoints
- `cache/` – Cached data

## Configuration

Create `.env` in this directory:

```env
PORT=12352
TOKEN=${DASHBOARD_ADMIN_TOKEN}
LOG_LEVEL=INFO
```

## Health Check

```bash
curl http://127.0.0.1:12352/health
```

## Integration

Register with dashboard:

```bash
curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"opena9_call_tracking","endpoint":"http://127.0.0.1:12352"}'
```
