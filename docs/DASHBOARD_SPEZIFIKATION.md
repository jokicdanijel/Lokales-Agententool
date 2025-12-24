# 📊 Dashboard-Spezifikation & API-Endpunkte
## Version 1.0 (22.10.2025)

## 1️⃣ Ziel & Geltungsbereich

### Systemidentifikation
- **System**: Portier / ELION Hyper-Dashboard 2.0
- **Architekturmodus**: Option 2
  - **Hinweg**: OpenAI → opena1 (Koordinator) → opena2 (Archivator) → kordp → Tool/Agent
  - **Rückweg**: Tool/Agent → opena2 → opena1 → OpenAI

### Dokumentationszweck
Vollständige Spezifikation für:
- Backend- und Frontend-Layer
- Verbindliche API-Endpunkte
- Agenten-Seitenstandard
- Sicherheit
- Audit/Safepoints

## 2️⃣ Rollenmodell Dashboard

| Komponente | Typ | Verantwortung | Pfad (Root) |
|------------|-----|---------------|-------------|
| opena19 | Dashboard-Backend | Status-Aggregation, Routing, Events/SSE, Befehle, Safepoint-Query | /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent/ |
| opena16 | Frontend-Assembler | Gesamtlayout Dashboard-UI, Startseite, Navigationsrahmen | /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.homepage_creator/ |
| opena14 | HTML-Komponenten | Agenten-Unterseiten-Widgets (Kacheln, Tabellen, Logs-Viewer) | /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/14.html_creator/ |
| opena1 | Koordinator | Policy-Gate, Routing, DB/Audit-Schreiben, Befehlsannahme /log/opena1 | /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/ |
| opena2 | Archivator | Safepoints speichern/auflisten /finalize/opena2, /store/archivp | /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/ |

### Port-Policy
- ✅ Erlaubt: 12344–12399
- ❌ Verboten: 8080 (Ausnahme: interne OpenWebUI-Compose)
- 🔍 Health-Check: Jeder Dienst muss GET /health anbieten

## 3️⃣ Backend-API (opena19)

Basis-URL: `http://127.0.0.1:<PORT_DASHBOARD>` (Port aus .runtime/port, 12344–12399)

### 3.1 Status & Agenten

```http
GET /api/status/all
GET /api/status/{agent}
GET /api/agents
```

Antwortschema (Beispiel):
```json
{
  "strict": true,
  "timestamp": "2025-10-22T10:30:00+02:00",
  "agents": [
    {
      "name": "opena15",
      "role": "Homepage Creator",
      "port": 12356,
      "health": "healthy",
      "path": "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/16.homepage_creator/",
      "last_safepoints": ["SP173..._kordp→opena15_CMD.json", "SP173..._opena15→opena2_RESP.json"]
    }
  ]
}
```

### 3.2 Befehle

```http
POST /api/command/{agent}
```

Request-Schema:
```json
{
  "request_id": "uuid-...-...-...",
  "action": "start|stop|restart|ping|flush_cache",
  "strict": true
}
```

### 3.3 Events & Streams

```http
GET /api/events/live
```
SSE-Events:
- sp_created
- agent_status
- warning
- error

### 3.4 Safepoints

```http
POST /api/safepoints/query
```

Query-Schema:
```json
{
  "filter": {
    "date_from": "2025-10-18",
    "date_to": "2025-10-22",
    "src": ["opena1","kordp"],
    "dst": ["opena2","opena15"],
    "kind": ["CMD","RESP"]
  },
  "limit": 200,
  "strict": true
}
```

```http
GET /api/safepoints/download?path=...
```

### 3.5 UI-Bridge

```http
GET /ui/
GET /agent/{agent}
```

### 3.6 Health

```http
GET /health
```

Response:
```json
{
  "service": "opena19",
  "status": "healthy",
  "strict": true,
  "port": 12367
}
```

## 4️⃣ Koordinator-/Archiv-Endpunkte

### Koordinator (opena1)
```http
POST /log/opena1
```

### Archivator (opena2)
```http
POST /finalize/opena2
POST /store/archivp
```

### Dispatch
```http
POST /dispatch/kordp
```

Request-Schema (Mindestfelder):
```json
{
  "request_id": "uuid-...-...-...",
  "command": "STRING_ENUM",
  "target_preference": "agent_or_tool_name",
  "payload": {},
  "strict": true
}
```

## 5️⃣ Frontend-Standard

### Pfadkonventionen
- Startseite: `/ui/`
- Agentenseite: `/agent/{agent}`

### Pflicht-Abschnitte
1. Header
2. Controls
3. Statuspanel
4. Safepoint-Viewer
5. Logs-Viewer
6. Konfiguration
7. Events-Live

### UI-Richtlinien
✅ Erlaubt:
- div, section, table, thead, tbody, tr, td, th
- h1–h6, p, ul, li
- code, pre
- button, input[type=button|submit]
- form (ohne action)

❌ Verboten:
- script, iframe, embed
- externe Fonts/CDNs

## 6️⃣ Sicherheit & Auth

### Token-System
```http
Authorization: Bearer <DASHBOARD_ADMIN_TOKEN>
```

### Berechtigungsstufen
- `dashboard_admin`: volle Befehle + Query
- `dashboard_readonly`: nur GET-Zugriffe

### Rate Limiting
- 60 req/min pro Token
- HTTP 429 bei Überschreitung

## 7️⃣ Audit & Safepoints

### Safepoint-Kette
1. `SP<ts>_opena19→opena1_CMD.json`
2. `SP<ts>_opena1→opena2_CMD.json`
3. `SP<ts>_opena2→kordp_CMD.json`
4. `SP<ts>_<target>→opena2_RESP.json`

### Pfadstruktur
```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/archivp/
└── YYYY/
    └── MM/
        └── DD/
            ├── SP<epoch>_src→dst_CMD.json
            └── SP<epoch>_src→dst_RESP.json
```

## 8️⃣ Fehlerbehandlung

| Fehlerklasse | HTTP | Pflichtreaktion |
|--------------|------|-----------------|
| Validation | 422 | SP mit error.validation=true |
| Policy | 403 | SP-Log + policy_violation Event |
| Conflict | 409 | supported_actions im Body |
| Downstream | 502 | Retry-Hinweis + retry_after |
| Internal | 500 | SP mit error_id |

## 9️⃣ Health-Standard

```json
{
  "service": "opena19",
  "status": "healthy",
  "base": "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent/",
  "port_policy": {
    "allowed": "12344-12399",
    "forbidden": ["8080"]
  },
  "timestamp": "2025-10-22T10:45:00+02:00",
  "strict": true
}
```

## 🔟 Qualitätssicherung

### Musskriterien-Tests
1. Backend-Health
2. Agentenliste
3. Gesamtstatus
4. Event-Stream
5. Command-Chain
6. Safepoint-Queries
7. UI-Routen
8. Auth-System
9. Port-Policy

## Integration

### VS Code
- Status-Panel via `/api/status/all`
- Agent-Details via `/api/agent/{name}`
- Live-Events via SSE

### Telegram
- Command `/dashboard status`
- Tägliche Safepoint-Statistik

## Konformität

1. Strict Mode aktiviert (`"strict": true`)
2. CMD/RESP Safepoints für alle Aktionen
3. Strikte Port-Policy
4. Keine externen Skripte

## Nächste Schritte

1. Agenten-Seiten-Blueprint
2. UI-Implementierung
3. JSON-Schema-Definitionen
