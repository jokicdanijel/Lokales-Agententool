# Agent: opena4_telegram

**Agent ID:** `opena4`  
**Port:** `12347`  
**Category:** `Integration`  
**Description:** Telegram Integration

## Quick Start

```bash
pip install -r requirements.txt
cp .env.template .env
bash bin/start.sh
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/status` | Agent status |
| POST | `/invoke` | Main invoke endpoint |

## Testing

```bash
curl -s http://127.0.0.1:12347/health | jq .
```

## Logging

```bash
tail -f logs/app.log
```

---

**Auto-generated:** 2025-11-08
