# Gate Report: api_gate

- OK: `True`
- Started (UTC): `2025-12-24T08:03:32Z`
- Finished (UTC): `2025-12-24T08:03:32Z`
- Duration: `219 ms`

## Errors

_none_

## Violations

_none_

## Warnings

_none_

## Info

_none_

## Stats

```json
{
  "tests_run": 3,
  "results": [
    {
      "name": "GET /health",
      "method": "GET",
      "path": "/health",
      "url": "http://localhost:12348/health",
      "status": 200,
      "allowed_statuses": [
        200,
        204
      ],
      "body_snippet": "{\"status\":\"healthy\",\"service\":\"opena4-telegram\",\"timestamp\":\"2025-12-24T09:03:32.519092\"}"
    },
    {
      "name": "GET /status",
      "method": "GET",
      "path": "/status",
      "url": "http://localhost:12348/status",
      "status": 200,
      "allowed_statuses": [
        200
      ],
      "body_snippet": "{\"status\":\"online\",\"timestamp\":\"2025-12-24T09:03:32.734065\",\"bot\":{\"is_running\":false,\"pid\":null,\"messages_sent\":0,\"messages_received\":0,\"active_chats\":0,\"response_time\":0},\"system\":{\"cpu_percent\":73.4,\"memory_percent\":43.6,\"memory_available_mb\":18051,\"disk_percent\":83.4,\"disk_free_gb\":71,\"uptime\":577.014424},\"workflows\":{\"total\":20,\"telegram\":10,\"terminal\":10},\"stats\":{\"total_requests\":4,\"errors\""
    },
    {
      "name": "POST /api/ai/generate",
      "method": "POST",
      "path": "/api/ai/generate",
      "url": "http://localhost:12348/api/ai/generate",
      "status": 422,
      "allowed_statuses": [
        200,
        201,
        202,
        400,
        401,
        422
      ],
      "body_snippet": "{\"detail\":[{\"type\":\"missing\",\"loc\":[\"body\",\"text\"],\"msg\":\"Field required\",\"input\":{\"prompt\":\"ping\"},\"url\":\"https://errors.pydantic.dev/2.12/v/missing\"}]}"
    }
  ]
}
```
