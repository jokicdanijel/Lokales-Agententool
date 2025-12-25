# OpenWebUI API Integration

## Neue Endpunkte

### GET /api/openwebui/status

Prüft die Gesundheit des OpenWebUI-Agenten (opena3).

**Authentifizierung:** Bearer Token (aus `.env`)

**Antwort:**

```json
{
  "service": "opena3",
  "status": "ok",
  "ts": "2025-11-06T12:00:00Z"
}
```

**Fehler:**

- `401` – Token ungültig
- `502` – OpenWebUI Agent nicht erreichbar

### POST /api/openwebui/chat

Sendet einen Chat-Prompt an OpenWebUI und gibt die Antwort zurück.

**Authentifizierung:** Bearer Token (aus `.env`)

**Request:**

```json
{
  "prompt": "What is ELION Hyper-Dashboard?",
  "context": {
    "system": "You are a helpful assistant."
  }
}
```

**Antwort:**

```json
{
  "response": {...},
  "ts": "2025-11-06T12:00:00Z"
}
```

**Fehler:**

- `400` – prompt erforderlich
- `401` – Token ungültig
- `502` – OpenWebUI Agent nicht erreichbar
- `504` – Timeout

## Beispiele mit curl

### Status prüfen

```bash
TOK=$(cat .env)
curl -H "Authorization: Bearer $TOK" \
  http://127.0.0.1:12349/api/openwebui/status | jq .
```

### Chat-Anfrage

```bash
TOK=$(cat .env)
curl -X POST \
  -H "Authorization: Bearer $TOK" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello!","context":{}}' \
  http://127.0.0.1:12349/api/openwebui/chat | jq .
```

## Authentifizierung

Alle Endpunkte erfordern einen Bearer Token aus `.env`:

```bash
# Token anzeigen
cat .env

# In Header eintragen
-H "Authorization: Bearer <token>"
```

## Fehlerbehandlung

| Code | Bedeutung                           |
| ---- | ----------------------------------- |
| 400  | Anfrage invalid (z.B. prompt fehlt) |
| 401  | Token ungültig/fehlt                |
| 502  | OpenWebUI Agent nicht erreichbar    |
| 504  | Timeout bei OpenWebUI               |

**Debug:** Logs in `logs/dashboard_runtime.log` und `logs/opena3.nohup.log` prüfen.
