# opena7_whatsapp

**Port:** 12350  
**Description:** WhatsApp integration

## Quick Start

```bash
cd opena7_whatsapp
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
PORT=12350
TOKEN=${DASHBOARD_ADMIN_TOKEN}
LOG_LEVEL=INFO
```

## Health Check

```bash
curl http://127.0.0.1:12350/health
```

## Integration

Register with dashboard:

```bash
curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"opena7_whatsapp","endpoint":"http://127.0.0.1:12350"}'
```
