# ELION Hyper-Dashboard 2.0 - Vollständige Wissensbasis

**Version:** 2.0 FINAL
**Datum:** 21. November 2025
**Status:** ✅ Production-Ready
**Maintainer:** Danijel (ELION Team)

---

## 📋 Inhaltsverzeichnis

1. [Projekt-Übersicht](#1-projekt-übersicht)
2. [System-Architektur](#2-system-architektur)
3. [Alle Agenten (opena1-opena21)](#3-alle-agenten)
4. [Port-Policy & Netzwerk](#4-port-policy--netzwerk)
5. [Option-2-Nachrichtenfluss](#5-option-2-nachrichtenfluss)
6. [Safepoints & Archivator](#6-safepoints--archivator)
7. [Dashboard-Agent (opena20)](#7-dashboard-agent-opena20)
8. [OpenWebUI Integration](#8-openwebui-integration)
9. [Sicherheit & Authentifizierung](#9-sicherheit--authentifizierung)
10. [Knowledgebase-System](#10-knowledgebase-system)
11. [API-Referenz](#11-api-referenz)
12. [Deployment & Operations](#12-deployment--operations)
13. [Entwickler-Workflows](#13-entwickler-workflows)
14. [Fehlerbehandlung & Troubleshooting](#14-fehlerbehandlung--troubleshooting)
15. [Best Practices & Governance](#15-best-practices--governance)
16. [Lessons Learned](#16-lessons-learned)

---

## 1. Projekt-Übersicht

### 1.1 Vision & Ziel

**ELION Hyper-Dashboard** ist ein stabiles, sicheres und für Endanwender verständliches KI-Agenten-System. Es ermöglicht auch Nicht-Experten, komplexe KI-Funktionalität produktiv zu nutzen.

**Kernziele:**

- ✅ **Stabilität**: Langfristig wartbar, reproduzierbar, produktionsreif
- ✅ **Sicherheit**: Token-basierte Auth, Port-Policy, Rate-Limiting, Audit-Logging
- ✅ **Zugänglichkeit**: Auch für Laien nutzbar durch klare UI und Dokumentation
- ✅ **Skalierbarkeit**: 20+ Agenten-Slots, erweiterbar auf 100+
- ✅ **Nachvollziehbarkeit**: Jede Operation wird als Safepoint archiviert

### 1.2 Technologie-Stack

| Komponente             | Technologie          | Version   |
| ---------------------- | -------------------- | --------- |
| **Backend**            | FastAPI              | 0.104+    |
| **Python**             | CPython              | 3.12.3    |
| **Virtuelle Umgebung** | venv                 | venv313   |
| **Web Server**         | Uvicorn              | Latest    |
| **Datenbank**          | JSONL (Append-Only)  | -         |
| **Frontend**           | OpenWebUI            | Port 8080 |
| **Container**          | Docker Compose       | Optional  |
| **Monitoring**         | Prometheus + Grafana | Optional  |

### 1.3 Projektstruktur

```
Gesamtprojekt/
├── 1.opena1&2_portier/          # Koordinator + Archivator
│   ├── main_opena1.py           # opena1 (Port 12344)
│   ├── main_opena2.py           # opena2 (Port 12345)
│   ├── archivp_store/           # Safepoint-Speicher
│   │   ├── index.jsonl          # Master-Index
│   │   └── YYYY/MM/DD/          # Tagespartitionen
│   └── knowledgebase/           # Wissensdatenbank
│
├── 2.opena3_openwebui/          # OpenWebUI Terminal Agent
│   └── main_openwebui_agent.py  # opena3 (Port 12347)
│
├── 3.opena4_telegram/           # Telegram Bot Agent
│   └── main.py                  # opena4 (Port 12346)
│
├── 19.opena20_dashboard_agent/  # Dashboard Backend
│   ├── src/pkg/
│   │   ├── main_dashboard.py   # opena20 (Port 12349)
│   │   ├── agent_registry.py   # Agent-Verwaltung
│   │   ├── sse_bus.py          # Server-Sent Events
│   │   ├── security.py         # Auth & Rate-Limiting
│   │   └── jwt_auth.py         # JWT Token-Management
│   ├── static/
│   │   └── admin.html          # Admin-Dashboard UI
│   └── bin/
│       ├── ops.sh              # Operations CLI
│       └── start_dashboard.sh  # Dashboard-Starter
│
├── bin/                         # Root-Level Scripts
│   ├── ops.sh                  # Zentraler Orchestrator
│   ├── start_all.sh            # Alle Services starten
│   ├── stop_all.sh             # Alle Services stoppen
│   └── verify_stack.sh         # Integration testen
│
├── .env                         # Secrets (NIEMALS in Git!)
├── docker-compose.prod.yml      # Production Deployment
└── README.md                    # Projekt-Dokumentation
```

---

## 2. System-Architektur

### 2.1 Komponenten-Übersicht

```
┌────────────────────────────────────────────────┐
│         Browser / UI (OpenWebUI Port 8080)      │
└────────────────┬───────────────────────────────┘
                 │
    ┌────────────▼─────────────┐
    │   Portier (opena1)       │  ← Zentral-Koordinator
    │   Port 12344             │     + Dispatcher
    └────────────┬─────────────┘
                 │
    ┌────────────▼─────────────┐
    │   Archivator (opena2)    │  ← Safepoint-System
    │   Port 12345             │     + Dedupe-Engine
    └────────────┬─────────────┘
                 │
    ┌────────────┴────────────────────┐
    │                                 │
┌───▼──────┐  ┌──────▼──────┐  ┌────▼─────┐
│opena3    │  │opena4       │  │Dashboard │
│OpenWebUI │  │Telegram     │  │(opena20) │
│12347     │  │12346        │  │12349     │
└──────────┘  └─────────────┘  └──────────┘
    │              │                │
    └──────────────┼────────────────┘
                   │
         ┌─────────▼────────┐
         │  16+ Agenten      │
         │  (opena5-opena21) │
         │  12350-12366      │
         └───────────────────┘
```

### 2.2 Datenfluss (Option-2-Prozess)

**Jede Operation folgt diesem strikten Pfad:**

```
1. Request → opena1 (Koordinator)
2. opena1 → opena2 (Archivator schreibt CMD-Safepoint)
3. opena2 → kordp (Koordinatport dispatcht zu Tool)
4. kordp → Tool (führt Business Logic aus)
5. Tool → opena2 (Archivator schreibt RESP-Safepoint)
6. opena2 → opena1 (Response an Requester)
7. opena1 → Client (finale Antwort)
```

**Verboten:**

- ❌ Direkter Zugriff auf Tools (Bypass von opena2)
- ❌ Shortcuts (opena1 → kordp ohne Archiv)
- ❌ Tool-zu-Tool-Kommunikation
- ❌ Backdoors jeglicher Art

---

## 3. Alle Agenten

### 3.1 Agenten-Mapping (opena1-opena21)

| Agent ID    | Port  | Rolle                     | Status      | API Endpoint         |
| ----------- | ----- | ------------------------- | ----------- | -------------------- |
| **opena1**  | 12344 | Koordinator (Dispatcher)  | ✅ Online   | `/api/agent/opena1`  |
| **opena2**  | 12345 | Archivator (Safepoints)   | ✅ Online   | `/api/agent/opena2`  |
| **kordp**   | 12346 | Koordinatport (Scheduler) | ✅ Online   | `/api/agent/kordp`   |
| **opena3**  | 12347 | OpenWebUI Terminal        | ✅ Online   | `/api/agent/opena3`  |
| **opena4**  | 12346 | Telegram Bot              | ✅ Online   | `/api/agent/opena4`  |
| **opena5**  | 12351 | VS Code Agent             | ⏳ Template | `/api/agent/opena5`  |
| **opena6**  | 12352 | Browser Automation        | ⏳ Template | `/api/agent/opena6`  |
| **opena7**  | 12353 | E-Mail Manager            | ⏳ Template | `/api/agent/opena7`  |
| **opena8**  | 12354 | WhatsApp Agent            | ⏳ Template | `/api/agent/opena8`  |
| **opena9**  | 12355 | Telephone Agent           | ⏳ Template | `/api/agent/opena9`  |
| **opena10** | 12356 | Call Tracking             | ⏳ Template | `/api/agent/opena10` |
| **opena11** | 12357 | Unlock Service            | ⏳ Template | `/api/agent/opena11` |
| **opena12** | 12358 | Social Media Manager      | ⏳ Template | `/api/agent/opena12` |
| **opena13** | 12359 | Influencer Manager        | ⏳ Template | `/api/agent/opena13` |
| **opena14** | 12360 | Calendar Agent            | ⏳ Template | `/api/agent/opena14` |
| **opena15** | 12361 | HTML Generator            | ⏳ Template | `/api/agent/opena15` |
| **opena16** | 12362 | Shop Manager              | ⏳ Template | `/api/agent/opena16` |
| **opena17** | 12363 | Homepage Creator          | ⏳ Template | `/api/agent/opena17` |
| **opena18** | 12364 | CRM System                | ⏳ Template | `/api/agent/opena18` |
| **opena19** | 12365 | Aktien & Crypto           | ⏳ Template | `/api/agent/opena19` |
| **opena20** | 12349 | **Dashboard (THIS)**      | ✅ Online   | `/api/agent/opena20` |
| **opena21** | 12366 | Workflow Manager          | ⏳ Template | `/api/agent/opena21` |

### 3.2 Agent-Rollen im Detail

#### **opena1 (Koordinator)**

- **Zweck**: Zentrale Dispatch-Stelle für alle Requests
- **Funktionen**:
  - Route-Registry verwalten
  - Requests an passende Tools weiterleiten
  - Response-Aggregation
  - Health-Monitoring koordinieren
- **Tech-Stack**: FastAPI, Pydantic v2
- **Kritisch**: Darf niemals direkt mit Tools kommunizieren (nur über opena2)

#### **opena2 (Archivator)**

- **Zweck**: Append-Only Safepoint-System
- **Funktionen**:
  - CMD/RESP-Safepoints schreiben
  - Deduplizierung (Hash-basiert)
  - Index-Verwaltung (JSONL)
  - Tagespartitionierung (YYYY/MM/DD)
- **Tech-Stack**: FastAPI, Filesystem (JSONL)
- **Kritisch**: Niemals Safepoints löschen oder modifizieren!

#### **opena3 (OpenWebUI Terminal)**

- **Zweck**: UI-Interface für OpenWebUI
- **Funktionen**:
  - Chat-Requests von OpenWebUI entgegennehmen
  - Über Option-2-Flow an Tools weiterleiten
  - SSE-Events an Dashboard publishen
- **Tech-Stack**: FastAPI, SSE
- **Port**: 12347 (Backend), 8080 (UI-only)

#### **opena20 (Dashboard - DIESES Modul)**

- **Zweck**: Zentrale Admin-Oberfläche
- **Funktionen**:
  - Agent-Registry (Registrierung, Status)
  - Server-Sent Events (SSE) für Live-Updates
  - JWT-Token-Management
  - Knowledgebase-API (Stats, Search, Read)
  - Security (Auth, Rate-Limiting, Audit-Log)
- **Tech-Stack**: FastAPI, SSE, JWT, Pydantic v2
- **Port**: 12349

---

## 4. Port-Policy & Netzwerk

### 4.1 Port-Ranges

**Erlaubte Backend-Ports:**

```
12344 - 12399  (Backend-Services)
```

**Verbotene Ports:**

```
8080           (Exklusiv für OpenWebUI UI)
```

### 4.2 Port-Enforcement (Middleware)

**Im Dashboard:**

```python
ALLOWED_PORTS = list(range(12344, 12400))
FORBIDDEN_PORTS = [8080]

@app.middleware("http")
async def validate_port_policy(request: Request, call_next):
    port = request.url.port

    if port in FORBIDDEN_PORTS:
        logger.error(f"[PORT_POLICY] Port {port} ist verboten")
        return JSONResponse(
            {"error": "Port 8080 ist exklusiv für UI"},
            status_code=403
        )

    if port not in ALLOWED_PORTS:
        logger.warning(f"[PORT_POLICY] Port {port} außerhalb 12344-12399")

    return await call_next(request)
```

### 4.3 CORS-Policy

**Erlaubte Origins:**

```python
cors_origins = [
    "http://127.0.0.1:12349",  # Dashboard
    "http://localhost:12349",
]
```

**Wichtig:** Port 8080 wird NICHT in `allow_origins` aufgenommen, da nur das Dashboard API-Zugriff gewährt.

---

## 5. Option-2-Nachrichtenfluss

### 5.1 Grundprinzip

**Jede Nachricht durchläuft:**

```
Client → opena1 → opena2 (CMD) → kordp → Tool → opena2 (RESP) → opena1 → Client
```

**Schlüsselpunkte:**

- ✅ opena2 ist IMMER in der Kette
- ✅ Jede Aktion wird doppelt archiviert (CMD + RESP)
- ✅ Keine Shortcuts
- ✅ Audit-Trail vollständig

### 5.2 Beispiel: Chat-Anfrage

**1. User sendet Chat in OpenWebUI:**

```http
POST http://127.0.0.1:8080/api/chat
{"prompt": "Wetter in Wien"}
```

**2. OpenWebUI → opena3 (Port 12347):**

```http
POST http://127.0.0.1:12347/command
{"prompt": "Wetter in Wien"}
```

**3. opena3 → opena1 (Option-2 Start):**

```http
POST http://127.0.0.1:12344/dispatch
{
  "service_target": "weather_tool",
  "action": "get_forecast",
  "params": {"city": "Wien", "days": 3}
}
```

**4. opena1 → opena2 (CMD-Safepoint):**

```json
{
  "sp_id": "00123",
  "src": "opena1",
  "dst": "weather_tool",
  "type": "CMD",
  "timestamp": "2025-11-21T12:00:00Z",
  "body": {
    "action": "get_forecast",
    "params": { "city": "Wien", "days": 3 }
  }
}
```

**5. opena2 → kordp (Dispatch):**

```
kordp führt weather_tool aus
```

**6. weather_tool → opena2 (RESP-Safepoint):**

```json
{
  "sp_id": "00123",
  "src": "weather_tool",
  "dst": "opena1",
  "type": "RESP",
  "timestamp": "2025-11-21T12:00:02Z",
  "body": {
    "forecast": [
      { "day": "Mi", "temp": "6°/-2°", "condition": "Bewölkt" },
      { "day": "Do", "temp": "6°/1°", "condition": "Schauer" },
      { "day": "Fr", "temp": "3°/0°", "condition": "Schnee" }
    ]
  }
}
```

**7. opena2 → opena1 → opena3 → User:**
Antwort wird zurückgeleitet.

---

## 6. Safepoints & Archivator

### 6.1 Safepoint-Format

**Naming Convention:**

```
SP<laufnummer>_src→dst_{CMD|RESP}.json
```

**Beispiele:**

```
SP00001_opena1→kordp_CMD.json
SP00001_kordp→opena1_RESP.json
SP00174_opena3→weather_tool_CMD.json
```

**Kritisch:** Unicode-Pfeil `→` (U+2192) ist **Pflicht**!

### 6.2 Verzeichnisstruktur

```
archivp_store/
├── index.jsonl              # Master-Index (append-only)
├── 2025/
│   └── 11/
│       └── 21/
│           ├── SP00001_opena1→kordp_CMD.json
│           ├── SP00001_kordp→opena1_RESP.json
│           ├── SP00002_opena3→weather_tool_CMD.json
│           └── SP00002_weather_tool→opena3_RESP.json
```

### 6.3 Index-Format (JSONL)

**Jeder Safepoint erzeugt einen Index-Eintrag:**

```json
{
  "sp_id": "00001",
  "timestamp": "2025-11-21T12:00:00Z",
  "src": "opena1",
  "dst": "kordp",
  "type": "CMD",
  "path": "2025/11/21/SP00001_opena1→kordp_CMD.json",
  "hash": "sha256:abc123..."
}
```

### 6.4 Regeln

- ✅ **Append-Only**: Niemals Safepoints löschen
- ✅ **Immutable**: Niemals Safepoints modifizieren
- ✅ **UTC-Timestamps**: Alle Zeiten in UTC
- ✅ **Full Envelope Logging**: Komplette Request/Response
- ✅ **Deduplizierung**: Hash-basiert (bei identischen Requests)

---

## 7. Dashboard-Agent (opena20)

### 7.1 Architektur

**Komponenten:**

```
main_dashboard.py
├── AgentRegistry      # Agent-Verwaltung
├── SSEBus            # Server-Sent Events
├── SecurityModule     # Auth + Rate-Limiting
├── JWTAuth           # Token-Management
├── BackgroundPoller   # Health-Monitoring
└── KnowledgebaseAPI  # Wissensdatenbank
```

### 7.2 Core Routes

**Status-Endpoints:**

```
GET  /health                          # Health-Check
GET  /api/status/all                  # Alle Agenten-Status
GET  /api/status/{agent_id}           # Einzelner Agent-Status
```

**Registry-Endpoints:**

```
GET  /api/agent/list                  # Alle registrierten Agenten
POST /api/agent/register              # Agent registrieren
POST /api/command/register            # Legacy-Alias
```

**OpenWebUI-Endpoints:**

```
GET  /api/openwebui/status            # opena3 Health-Check
POST /api/openwebui/chat              # Chat via opena3
```

**JWT-Token-Endpoints:**

```
POST /api/agents/{agent_id}/token     # Token generieren
POST /api/auth/verify                 # Token validieren
GET  /api/agents/tokens/all           # Batch-Token-Generierung
```

**Knowledgebase-Endpoints:**

```
GET  /api/knowledgebase/stats         # Statistiken
GET  /api/knowledgebase/list          # Alle Dateien
GET  /api/knowledgebase/search?q=...  # Volltextsuche
GET  /api/knowledgebase/read/{file}   # Datei lesen
```

**SSE-Endpoint:**

```
GET  /api/events/live                 # Live Event-Stream
```

**UI-Endpoints:**

```
GET  /ui/                             # Minimal-UI
GET  /admin                           # Redirect zu admin.html
GET  /static/admin.html               # Admin-Dashboard
```

### 7.3 Pydantic-Modelle (Strict Mode)

**Alle Modelle nutzen:**

```python
class StrictModel(BaseModel):
    class Config:
        extra = "forbid"
        json_schema_extra = {"additionalProperties": False}
```

**Beispiele:**

- `HealthResponse`
- `AgentRegistrationPayload`
- `TokenGenerationResponse`
- `TokenVerificationPayload`
- `ErrorResponse`

---

## 8. OpenWebUI Integration

### 8.1 Architektur

```
User (Browser)
    ↓ Port 8080
OpenWebUI (UI)
    ↓ HTTP
Adapter (Port 12350)
    ↓ HTTP
opena3 (Port 12347)
    ↓ Option-2
opena1 → opena2 → kordp → Tool
```

### 8.2 Komponenten

**OpenWebUI Container:**

```yaml
services:
  open-webui:
    image: open-webui/open-webui:main
    ports:
      - "8080:8080"
    environment:
      - WEBUI_AUTH=false
      - OLLAMA_ENDPOINT=http://host.docker.internal:11434
```

**OpenWebUI Adapter (Port 12350):**

```python
# openwebui_adapter.py
@app.post("/openwebui/chat")
async def forward_chat(payload: dict):
    response = requests.post(
        "http://127.0.0.1:8080/api/chat",
        json=payload,
        timeout=30
    )
    return response.json()
```

**opena3 (Port 12347):**

```python
# main_openwebui_agent.py
@app.post("/command")
async def handle_command(payload: dict):
    # Forward to opena1 (Option-2)
    response = requests.post(
        "http://127.0.0.1:12344/dispatch",
        json=payload,
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()
```

### 8.3 Dashboard-Integration

**Im Dashboard (main_dashboard.py):**

```python
@app.get("/api/openwebui/status")
async def get_openwebui_status(token: HTTPAuthorizationCredentials = Security(security)):
    try:
        response = requests.get("http://127.0.0.1:12347/health", timeout=5)
        return {"agent": "opena3", "health": response.json()}
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Timeout")
```

```python
@app.post("/api/openwebui/chat")
@rate_limiter.limit()
async def openwebui_chat(payload: dict, token: HTTPAuthorizationCredentials = Security(security)):
    response = requests.post(
        "http://127.0.0.1:12347/command",
        json=payload,
        timeout=30
    )

    # Publish SSE event
    await sse_bus.publish({
        "event": "openwebui_chat",
        "data": {"prompt": payload["prompt"], "response": response.json()}
    })

    return {"agent": "opena3", "response": response.json()}
```

---

## 9. Sicherheit & Authentifizierung

### 9.1 Bearer-Token-System

**Token-Generierung (beim Start):**

```python
# security.py
def _ensure_token_file() -> str:
    if ENV_FILE.exists():
        token = ENV_FILE.read_text().strip()
        if token:
            return token

    # Neu generieren
    token = secrets.token_urlsafe(32)
    ENV_FILE.write_text(token)
    logger.info("Neuer Token generiert und in .env gespeichert")
    return token
```

**.env-Datei:**

```bash
# NIEMALS in Git committen!
DASHBOARD_ADMIN_TOKEN=rAnDoM_32_bYtE_tOkEn_hErE
```

**Token-Validierung:**

```python
def verify_token(token: str) -> bool:
    ok = bool(token) and token == _CURRENT_TOKEN
    logger.info(f"Tokenprüfung ok={ok}")
    return ok
```

**In Routes:**

```python
@app.get("/api/status/all")
async def get_all_status(token: HTTPAuthorizationCredentials = Security(security)):
    ok = verify_token(token.credentials)
    if not ok:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # ...
```

### 9.2 JWT-Token-Management

**JWT-Token erstellen:**

```python
from jwt_auth import create_token

jwt_token = create_token(
    agent_id="opena4",
    scope="invoke",
    permissions=["read", "write"]
)
```

**JWT-Token verifizieren:**

```python
from jwt_auth import verify_token

result = verify_token(jwt_token)
# result.is_valid, result.agent_id, result.scope, result.permissions
```

**Batch-Token-Generierung:**

```http
GET /api/agents/tokens/all
Authorization: Bearer <admin_token>

Response:
{
  "count": 22,
  "tokens": {
    "opena1": "eyJhbGc...",
    "opena2": "eyJhbGc...",
    ...
  },
  "generated_at": "2025-11-21T12:00:00Z"
}
```

### 9.3 Rate-Limiting

**Implementierung:**

```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.rate_limit = requests_per_minute
        self.window_size = 60.0
        self._reqs: Dict[str, List[float]] = {}

    def check(self, token: str) -> bool:
        now = time.time()
        bucket = self._reqs.setdefault(token, [])

        # Alte Einträge entfernen
        bucket[:] = [t for t in bucket if now - t < self.window_size]

        if len(bucket) >= self.rate_limit:
            return False

        bucket.append(now)
        return True
```

**Usage:**

```python
rate_limiter = RateLimiter(requests_per_minute=120)

@app.get("/api/status/all")
@rate_limiter.limit()
async def get_all_status(...):
    # ...
```

**Response bei Limit:**

```http
HTTP/1.1 429 Too Many Requests
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Maximale Anzahl von Requests (120/min) überschritten"
  }
}
```

### 9.4 Security-Logging

**Alle Auth-Versuche werden geloggt:**

```python
class SecurityLog:
    def log_access(self, token: str, endpoint: str, allowed: bool):
        # Token maskieren (nur erste 8 Zeichen)
        masked_token = token[:8] + "..." if len(token) > 8 else token

        self.logger.info(
            f"Access: endpoint={endpoint}, "
            f"token={masked_token}, "
            f"allowed={allowed}"
        )
```

**Log-Datei:**

```
logs/security.log
```

**Beispiel:**

```
2025-11-21 12:00:00 - INFO - Access: endpoint=/api/status/all, token=rAnDoM_3..., allowed=True
2025-11-21 12:00:05 - INFO - Access: endpoint=/api/agent/register, token=invalid..., allowed=False
```

---

## 10. Knowledgebase-System

### 10.1 Verzeichnisstruktur

```
1.opena1&2_portier/
└── knowledgebase/
    └── opena1/
        ├── document1.txt
        ├── document2.md
        ├── config.yaml
        ├── guide.html
        └── archive.zip
```

**Aktuell:**

- 47 Dateien
- 116.09 MB
- Typen: .txt (34), .html (3), .zip (2), .deb (1), .odt (1), .prompt (1)

### 10.2 API-Endpoints

#### **GET /api/knowledgebase/stats**

**Response:**

```json
{
  "total_files": 47,
  "total_size": 121718784,
  "total_size_mb": 116.09,
  "file_types": {
    ".txt": { "count": 34, "size": 89234567 },
    ".html": { "count": 3, "size": 12345678 },
    ".zip": { "count": 2, "size": 19876543 }
  },
  "base_path": "/path/to/knowledgebase"
}
```

#### **GET /api/knowledgebase/list**

**Response:**

```json
{
  "count": 47,
  "files": [
    {
      "name": "document1.txt",
      "path": "opena1/document1.txt",
      "size": 1024,
      "modified": "2025-11-20T15:30:00",
      "extension": ".txt"
    },
    ...
  ],
  "base_path": "/path/to/knowledgebase"
}
```

#### **GET /api/knowledgebase/search?query=wetter**

**Response:**

```json
{
  "query": "wetter",
  "count": 3,
  "results": [
    {
      "name": "weather_guide.txt",
      "path": "opena1/weather_guide.txt",
      "size": 2048,
      "modified": "2025-11-20T12:00:00",
      "match_type": "filename"
    },
    {
      "name": "faq.md",
      "path": "opena1/faq.md",
      "size": 4096,
      "modified": "2025-11-19T10:00:00",
      "match_type": "content",
      "context": "...wie ist das Wetter in Wien?..."
    }
  ]
}
```

#### **GET /api/knowledgebase/read/{filename:path}**

**Request:**

```http
GET /api/knowledgebase/read/opena1/document1.txt
Authorization: Bearer <token>
```

**Response:**

```json
{
  "filename": "document1.txt",
  "path": "opena1/document1.txt",
  "size": 1024,
  "content": "Dies ist der Dateiinhalt...",
  "lines": 42
}
```

### 10.3 Sicherheitsmaßnahmen

**Directory Traversal Prevention:**

```python
def _safe_path(filename: str) -> Path:
    safe_path = (KNOWLEDGEBASE_ROOT / filename).resolve()

    if not str(safe_path).startswith(str(KNOWLEDGEBASE_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    return safe_path
```

**File Size Limit:**

```python
MAX_FILE_SIZE = 5_000_000  # 5MB

if safe_path.stat().st_size > MAX_FILE_SIZE:
    raise HTTPException(status_code=413, detail="File too large")
```

**Allowed Extensions (für Content-Search):**

```python
SEARCHABLE_EXTENSIONS = [".txt", ".md", ".html"]
MAX_SEARCH_SIZE = 1_000_000  # 1MB
```

---

## 11. API-Referenz

### 11.1 Authentifizierung

**Alle geschützten Endpoints benötigen:**

```http
Authorization: Bearer <token>
```

**Token aus .env holen:**

```bash
TOKEN=$(cat .env)
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:12349/api/status/all
```

### 11.2 Standard-Response-Format

**Erfolgreiche Antwort:**

```json
{
  "strict": true,
  "data": { ... },
  "timestamp": "2025-11-21T12:00:00Z"
}
```

**Fehler-Antwort:**

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }
  }
}
```

### 11.3 HTTP-Status-Codes

| Code    | Bedeutung             | Beispiel                          |
| ------- | --------------------- | --------------------------------- |
| **200** | OK                    | Erfolgreiche Abfrage              |
| **201** | Created               | Agent registriert                 |
| **400** | Bad Request           | Fehlende Parameter                |
| **401** | Unauthorized          | Ungültiger Token                  |
| **403** | Forbidden             | Port-Policy verletzt              |
| **404** | Not Found             | Agent nicht gefunden              |
| **413** | Payload Too Large     | Datei zu groß                     |
| **429** | Too Many Requests     | Rate-Limit überschritten          |
| **500** | Internal Server Error | Unerwarteter Fehler               |
| **502** | Bad Gateway           | Upstream-Service nicht erreichbar |
| **504** | Gateway Timeout       | Upstream-Timeout                  |

---

## 12. Deployment & Operations

### 12.1 Systemstart

**Einzelner Service:**

```bash
# Dashboard starten
cd 19.opena20_dashboard_agent
source ../venv313/bin/activate
python3 -m uvicorn src.pkg.main_dashboard:app --host 127.0.0.1 --port 12349
```

**Alle Services (via ops.sh):**

```bash
# Von Projekt-Root
bin/ops.sh start
```

**Befehle:**

```bash
bin/ops.sh start         # Alle Services starten
bin/ops.sh stop          # Alle Services stoppen
bin/ops.sh restart       # Alle Services neustarten
bin/ops.sh status        # Status abfragen (JSON)
bin/ops.sh health        # Health-Checks
bin/ops.sh verify        # Integration testen
bin/ops.sh logs          # Logs anzeigen
bin/ops.sh admin         # Dashboard im Browser öffnen
```

### 12.2 Service-Management

**PID-Files:**

```
logs/opena1.pid
logs/opena2.pid
logs/opena3.pid
logs/dashboard.pid
```

**Log-Files:**

```
logs/opena1.nohup.log
logs/opena2.nohup.log
logs/dashboard_runtime.log
logs/security.log
```

**Service stoppen:**

```bash
kill -9 $(cat logs/dashboard.pid)
rm logs/dashboard.pid
```

### 12.3 Monitoring

**Health-Check:**

```bash
curl -s http://127.0.0.1:12349/health | jq .
```

**Status aller Agenten:**

```bash
curl -s -H "Authorization: Bearer $(cat .env)" \
  http://127.0.0.1:12349/api/status/all | jq .
```

**Live-Events (SSE):**

```bash
curl -N http://127.0.0.1:12349/api/events/live
```

**Prometheus-Integration:**

```yaml
# docker-compose.prod.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
```

**Grafana-Dashboards:**

```
http://127.0.0.1:3001
```

---

## 13. Entwickler-Workflows

### 13.1 Neuen Agenten registrieren

**1. Agent startet und registriert sich:**

```bash
curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer $(cat .env)" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "opena5",
    "endpoint": "http://127.0.0.1:12351"
  }'
```

**2. Dashboard bestätigt:**

```json
{
  "strict": true,
  "agent": "opena5",
  "endpoint": "http://127.0.0.1:12351",
  "registered_at": "2025-11-21T12:00:00Z"
}
```

**3. SSE-Event wird gepublisht:**

```json
{
  "event": "agent_registered",
  "data": {
    "agent": "opena5",
    "endpoint": "http://127.0.0.1:12351"
  }
}
```

### 13.2 Code-Änderungen

**1. Code editieren:**

```bash
vim 19.opena20_dashboard_agent/src/pkg/main_dashboard.py
```

**2. Tests ausführen:**

```bash
pytest tests/test_dashboard.py -v
```

**3. Linting:**

```bash
black --line-length 120 src/
flake8 --max-line-length 120 src/
```

**4. Service neu starten:**

```bash
bin/ops.sh restart
```

**5. Verify:**

```bash
bin/ops.sh verify
```

### 13.3 Debugging

**Logs live verfolgen:**

```bash
tail -f logs/dashboard_runtime.log
```

**Security-Logs prüfen:**

```bash
tail -f logs/security.log
```

**Port-Konflikte finden:**

```bash
lsof -i :12349
```

**Prozess-Status:**

```bash
ps aux | grep uvicorn
```

---

## 14. Fehlerbehandlung & Troubleshooting

### 14.1 Häufige Fehler

#### **401 Unauthorized**

**Ursache:** Ungültiger oder fehlender Bearer-Token

**Lösung:**

```bash
# Token aus .env prüfen
cat .env

# Token neu generieren
rm .env
bin/ops.sh start  # Generiert neuen Token
```

#### **403 Forbidden (Port 8080)**

**Ursache:** Versuch, Backend auf Port 8080 zu starten

**Lösung:**

```bash
# Port-Policy prüfen
grep "FORBIDDEN_PORTS" src/pkg/main_dashboard.py

# Korrekten Port verwenden (12344-12399)
uvicorn main_dashboard:app --port 12349
```

#### **404 Not Found (Agent)**

**Ursache:** Agent nicht in Registry

**Lösung:**

```bash
# Registry prüfen
curl -H "Authorization: Bearer $(cat .env)" \
  http://127.0.0.1:12349/api/agent/list | jq .

# Agent neu registrieren
curl -X POST http://127.0.0.1:12349/api/agent/register \
  -H "Authorization: Bearer $(cat .env)" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"opena1","endpoint":"http://127.0.0.1:12344"}'
```

#### **429 Too Many Requests**

**Ursache:** Rate-Limit überschritten (120 req/min)

**Lösung:**

```python
# Rate-Limit erhöhen (security.py)
rate_limiter = RateLimiter(requests_per_minute=240)
```

#### **502 Bad Gateway**

**Ursache:** Upstream-Service (z.B. opena3) nicht erreichbar

**Lösung:**

```bash
# Service-Status prüfen
bin/ops.sh status | jq '.agents.opena3'

# Service starten
python3 2.opena3_openwebui/main_openwebui_agent.py
```

#### **504 Gateway Timeout**

**Ursache:** Upstream-Service antwortet nicht rechtzeitig

**Lösung:**

```python
# Timeout erhöhen
response = requests.get(
    "http://127.0.0.1:12347/health",
    timeout=10  # Statt 5
)
```

### 14.2 Diagnosewerkzeuge

**Health-Check aller Services:**

```bash
for port in {12344..12350}; do
  echo "Port $port:"
  curl -s http://127.0.0.1:$port/health | jq '.status' 2>/dev/null || echo "❌ Not responding"
done
```

**Registry-Dump:**

```bash
curl -H "Authorization: Bearer $(cat .env)" \
  http://127.0.0.1:12349/api/agent/list | jq .
```

**SSE-Stream testen:**

```bash
curl -N http://127.0.0.1:12349/api/events/live
```

**Safepoint-Index prüfen:**

```bash
tail -10 1.opena1&2_portier/archivp_store/index.jsonl | jq .
```

---

## 15. Best Practices & Governance

### 15.1 Code-Konventionen

**Naming:**

- **Agenten:** `opena1`, `opena2`, ... `opena21`
- **Ports:** `opena1` = `12344`, `opena2` = `12345`, etc.
- **Safepoints:** `SP00001_src→dst_CMD.json`
- **Logs:** `{service}.nohup.log`, `{service}_runtime.log`

**Modell-Vorgabe:**

```python
# IMMER verwenden:
model: "gpt-5-nano"
```

**JSON-Strict-Mode:**

```python
class Config:
    extra = "forbid"
    json_schema_extra = {"additionalProperties": False}
```

### 15.2 Sicherheitsregeln

**Secrets:**

- ❌ **NIEMALS** Secrets in Git committen
- ✅ **IMMER** `.env` in `.gitignore`
- ✅ **IMMER** `DASHBOARD_ADMIN_TOKEN` aus `.env` laden

**Tokens:**

- ❌ **NIEMALS** Tokens hardcoden
- ✅ **IMMER** Tokens über Umgebungsvariablen
- ✅ **IMMER** Tokens in Logs maskieren

**Port-Policy:**

- ❌ **NIEMALS** Backend auf Port 8080
- ✅ **IMMER** Backend auf 12344-12399
- ✅ **IMMER** Port-Validation-Middleware nutzen

### 15.3 Git-Workflows

**Was gehört in Git:**

- ✅ Source-Code (`.py`, `.js`, `.html`)
- ✅ Konfigurationsvorlagen (`.example`, `.template`)
- ✅ Dokumentation (`.md`)
- ✅ Scripts (`.sh`)

**Was gehört NICHT in Git:**

- ❌ `.env` (Secrets)
- ❌ `__pycache__/` (Python-Cache)
- ❌ `*.pyc` (Compiled Python)
- ❌ `logs/*.log` (Runtime-Logs)
- ❌ `archivp_store/` (Safepoints)
- ❌ `.venv/` (Virtuelle Umgebung)

**.gitignore:**

```gitignore
# Secrets
.env

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv313/

# Logs
logs/*.log
logs/*.pid

# Safepoints
archivp_store/

# IDE
.vscode/
.idea/
```

---

## 16. Lessons Learned

### 16.1 Was funktioniert gut

✅ **Option-2-Prozess**: Vollständiger Audit-Trail durch Archivator
✅ **Port-Policy**: Strikte Trennung UI/Backend verhindert Fehler
✅ **Agent-Registry**: Zentrale Verwaltung erleichtert Monitoring
✅ **SSE-Bus**: Live-Updates ohne Polling
✅ **Bearer-Token**: Einfaches, effektives Auth-System
✅ **Rate-Limiting**: Schutz vor Abuse
✅ **Strict JSON**: Fehler werden früh erkannt

### 16.2 Was zu vermeiden ist

❌ **GitHub Copilot unkontrolliert laufen lassen**

- Kann ungewollt Code modifizieren
- Backup vor Aktivierung erstellen

❌ **Binärdaten in Chat zurückgeben**

- GPG-Keys, ZIPs etc. nicht als Klartext anzeigen
- Immer auf Content-Type prüfen

❌ **Shell-Kommandos ohne Validierung**

- Immer `shell_execution.enabled` prüfen
- Niemals User-Input direkt in Shell ausführen

❌ **Safepoints löschen/modifizieren**

- Append-Only ist heilig
- Keine Ausnahmen!

❌ **Port 8080 für Backend nutzen**

- Exklusiv für OpenWebUI UI
- Middleware blockiert es automatisch

❌ **Secrets in Code hardcoden**

- Immer `.env` nutzen
- Tokens in Logs maskieren

### 16.3 Empfohlene Erweiterungen

**Testing:**

- Unit-Tests mit pytest
- Integration-Tests für API-Routes
- E2E-Tests für UI

**CI/CD:**

- GitHub Actions für Linting
- Pre-commit Hooks
- Automatische Deployments

**Monitoring:**

- Prometheus-Metriken exportieren
- Grafana-Dashboards erstellen
- Alert-Rules definieren

**Dokumentation:**

- API-Docs aktualisieren
- Architektur-Diagramme pflegen
- Onboarding-Guides schreiben

---

## 📚 Zusammenfassung

**ELION Hyper-Dashboard 2.0** ist ein produktionsreifes, sicheres und erweiterbares Multi-Agent-System mit:

- ✅ **22 Agent-Slots** (opena1-opena21 + kordp + opena20)
- ✅ **Option-2-konformer** Nachrichtenfluss
- ✅ **Strikte Port-Policy** (12344-12399, 8080 verboten)
- ✅ **Append-Only Safepoint-System**
- ✅ **Zentrale Admin-Oberfläche** (Dashboard + OpenWebUI)
- ✅ **Umfassende Sicherheit** (Auth, Rate-Limiting, Audit-Log)
- ✅ **Knowledgebase-Integration** (47 Dateien, 116 MB)
- ✅ **JWT-Token-Management**
- ✅ **Server-Sent Events (SSE)**
- ✅ **Vollständige API-Dokumentation**

**Dieses Dokument dient als Single Source of Truth für alle Aspekte des Systems.**

---

**Erstellt:** 21. November 2025
**Version:** 1.0
**Autor:** Danijel (ELION Team) + GitHub Copilot
**Lizenz:** Internal Use Only
