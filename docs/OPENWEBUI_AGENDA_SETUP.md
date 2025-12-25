# OpenWebUI Integration — 16 Agenda-Seiten

## Quick-Start

### 1. **Agenda API starten** (Port 12399)

```bash
source 1.opena1&2_portier/venv313/bin/activate
python3 src/services/agenda_api.py
```

### 2. **Login**

```bash
curl -X POST http://127.0.0.1:12399/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"250886"}'
```

**Response:**

```json
{
  "token": "250886",
  "message": "Willkommen admin! Token ist 30 Minuten gültig."
}
```

### 3. **Alle Agenda-Seiten abrufen**

```bash
TOKEN="250886"
curl -s -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:12399/agenda/pages | jq .
```

---

## API-Endpunkte

| Method   | Endpoint               | Beschreibung                                  |
| -------- | ---------------------- | --------------------------------------------- |
| `POST`   | `/login`               | Authentifizierung (Username/Password → Token) |
| `GET`    | `/agenda/pages`        | Alle 16 Seiten abrufen                        |
| `GET`    | `/agenda/pages/{id}`   | Einzelne Seite abrufen                        |
| `POST`   | `/agenda/pages/{id}`   | Seite aktualisieren                           |
| `DELETE` | `/agenda/pages/{id}`   | Seite löschen                                 |
| `GET`    | `/agenda/api-registry` | 20 Service-Endpunkte für OpenWebUI            |
| `GET`    | `/agenda/stats`        | Statistiken                                   |

---

## 16 Agenda-Seiten

### Struktur-Seiten (1-4)

1. **Main Dashboard** — Zentrale Übersicht & Navigation
2. **Logische Seite** — Regeln, Flusslogik, Validierung
3. **API Registry** — Katalog der 20 Service-Endpunkte
4. **Bromt Studio** — Textbausteine und Vorlagen

### Verarbeitungs-Seiten (5-8)

5. **Agenda 01 – Datenaufnahme** — Eingabe-API, Status-Tracking
6. **Agenda 02 – Bearbeitung** — Transformations-Pipeline
7. **Agenda 03 – Validierung** — Validierung, Fehlerbehandlung
8. **Agenda 04 – Speicherung** — Persistierung, Audit-Log

### Betrieb-Seiten (9-12)

9. **Agenda 05 – Auth/RBAC** — Token-basierte Authentifizierung
10. **Agenda 06 – Monitoring** — KPI-Definition, Dashboards
11. **Agenda 07 – Logging** — Strukturierte Logs, Log-Levels
12. **Agenda 08 – Alerts** — Alerting-Strategien, Runbooks

### Verwaltungs-Seiten (13-16)

13. **Agenda 09 – Reporting** — Berichte, Exportformate
14. **Agenda 10 – Import/Export** — Datenimporte, Snapshots
15. **Agenda 11 – Versionierung** — Change-Logs, Rollback
16. **Agenda 12 – Governance** — Compliance, Policy-Management

---

## OpenWebUI Integration

### Tool-Server Registrierung

In OpenWebUI:

1. **Settings** → **Tool Servers**
2. **Add Tool Server:**
   ```
   Name: ELION Agenda
   URL: http://127.0.0.1:12399
   Type: OpenAPI
   ```
3. Verfügbare Endpoints (auto-discovered):
   - Login
   - List Pages
   - Get Page
   - Update Page
   - API Registry
   - Stats

### Beispiel: Seite über OpenWebUI öffnen

```
User: "Öffne Agenda 01 – Datenaufnahme"

OpenWebUI → Tool: Get Page
  - ID: page05

Response: {
  "title": "Agenda 01 – Datenaufnahme",
  "bromt": "Eingabe-API, Bromt-Dokumentation, Status-Tracking.",
  "api_endpoint": "/agenda/pages/page05",
  "status": "active"
}
```

---

## Sicherheit (Produktion)

### Token-Management

```python
# ❌ NICHT in Produktion (Demo-only):
VALID_TOKEN = "250886"

# ✅ Produktion:
# 1. Vault/Secret Management
# 2. Environment Variables
# 3. JWT mit Expiration
# 4. HTTPS + mTLS
```

### Deployment mit Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/services/agenda_api.py .
EXPOSE 12399
CMD ["python", "-u", "agenda_api.py"]
```

**docker-compose.prod.yml:**

```yaml
agenda-api:
  build:
    context: .
    dockerfile: src/services/agenda_api/Dockerfile
  ports:
    - "12399:12399"
  environment:
    - AGENDA_TOKEN=${AGENDA_TOKEN}
    - PYTHONUNBUFFERED=1
  volumes:
    - ./configs/agenda_pages.json:/data/agenda.json
  networks:
    - elion
  restart: unless-stopped
```

---

## Testing

### Integration Test

```python
import requests

BASE_URL = "http://127.0.0.1:12399"

# 1. Login
resp = requests.post(f"{BASE_URL}/login", json={
    "username": "admin",
    "password": "250886"
})
token = resp.json()["token"]

# 2. List Pages
resp = requests.get(
    f"{BASE_URL}/agenda/pages",
    headers={"Authorization": f"Bearer {token}"}
)
pages = resp.json()
assert len(pages) == 16

# 3. Get Single Page
resp = requests.get(
    f"{BASE_URL}/agenda/pages/page01",
    headers={"Authorization": f"Bearer {token}"}
)
page = resp.json()
assert page["id"] == "page01"

# 4. Update Page
resp = requests.post(
    f"{BASE_URL}/agenda/pages/page01",
    headers={"Authorization": f"Bearer {token}"},
    json={"bromt": "Updated bromt text"}
)
assert resp.status_code == 200

print("✅ All tests passed")
```

---

## Logging & Monitoring

### Logs anschauen

```bash
tail -f logs/agenda_api.nohup.log
```

### Prometheus Metrics (künftig)

```yaml
# configs/prometheus.yaml
- job_name: "agenda-api"
  static_configs:
    - targets: ["127.0.0.1:12399"]
  scrape_interval: 30s
```

---

## Nächste Schritte

1. ✅ Agenda Pages JSON strukturiert
2. ✅ FastAPI Backend mit Login
3. ✅ CRUD-Endpunkte implementiert
4. 🟡 **OpenWebUI Tool-Server registrieren**
5. 🟡 Dashboard-Widgets für jede Seite erstellen
6. 🟡 Monitoring + Alerting integrieren
7. 🟡 HTTPS + Token-Vault für Produktion

---

**Status:** Ready for OpenWebUI Integration
**Port:** 12399
**Auth:** Bearer Token
**Documentation:** See above
