# 🚀 ELION Hyper-Dashboard 2.0 - Technische Spezifikation

## 📋 Übersicht

### Systemidentifikation
- **Name:** ELION Hyper-Dashboard 2.0
- **Version:** Production 1.0
- **Basis-URL:** `http://127.0.0.1:12344`
- **Architektur:** Option 2 (OpenAI → opena1 → opena2 → kordp → Tool)

### Hauptkomponenten
1. **Backend (opena19)** - Port 12344
   - Status-Aggregation
   - Event-Streaming
   - Command-Routing
   - Safepoint-Management

2. **Frontend (opena16)** - Port 12345
   - Dashboard-UI
   - Agent-Kacheln
   - Live-Updates
   - Status-Anzeigen

3. **Koordinator (opena1)**
   - Policy-Enforcement
   - Routing-Logik
   - Audit-Logging

4. **Archivator (opena2)**
   - Safepoint-Speicherung
   - Event-Archivierung
   - Integrität-Sicherung

## 🔧 Technische Spezifikation

### Backend-API (Port 12344)

#### 1. Status-Endpunkte
```http
GET /api/status/all
GET /api/status/{agent}
GET /api/agents
```

Antwortschema:
```json
{
  "strict": true,
  "timestamp": "2025-10-22T10:00:00Z",
  "agents": [
    {
      "id": "opena19",
      "role": "Dashboard Backend",
      "port": 12344,
      "status": "healthy",
      "last_safepoint": "SP12345_src→dst_CMD.json"
    }
  ]
}
```

#### 2. Befehls-Endpunkte
```http
POST /api/command/{agent}
```

Request-Schema:
```json
{
  "request_id": "uuid-...",
  "command": "start|stop|restart|ping",
  "strict": true,
  "payload": {}
}
```

#### 3. Event-Stream
```http
GET /api/events/live
```

SSE-Format:
```
event: agent_status
data: {"agent": "opena19", "status": "healthy", "timestamp": "..."}

event: safepoint_created
data: {"path": "archivp/2025/10/22/SP12345...json", "type": "CMD"}
```

### Frontend-Integration

#### 1. Hauptdashboard
- URL: `http://127.0.0.1:12344/ui/`
- Layout: Grid mit Agent-Kacheln
- Live-Updates via SSE
- Responsive Design

#### 2. Agent-Detailseiten
- URL: `http://127.0.0.1:12344/agent/{agent}`
- Safepoint-Historie
- Status-Metriken
- Befehlsschnittstelle

## 🔒 Sicherheit

### Authentifizierung
```http
Authorization: Bearer <DASHBOARD_TOKEN>
```

### Port-Policy
- ✅ Erlaubt: 12344-12399
- ❌ Verboten: 8080
- Ausnahme: OpenWebUI intern

### Rate-Limiting
- 60 Requests/Minute pro Token
- 429 bei Überschreitung

## 📁 Dateisystem

### Projektstruktur
```
/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/
├── 19.dashboard_agent/        # Backend
│   ├── main.py
│   ├── api/
│   └── .env
├── 16.homepage_creator/       # Frontend
│   ├── templates/
│   └── assets/
└── 1.portier_openai/         # Basis
    ├── opena1/
    ├── opena2/
    └── archivp/
```

### Safepoint-Archiv
```
archivp/
└── 2025/
    └── 10/
        └── 22/
            ├── SP12345_src→dst_CMD.json
            └── SP12345_src→dst_RESP.json
```

## 🧪 Tests & Qualitätssicherung

### Pflicht-Tests
1. Port-Policy-Konformität
2. Token-Validierung
3. Safepoint-Integrität
4. Event-Stream-Stabilität

### Monitoring
- Health-Checks alle 60 Sekunden
- Safepoint-Validierung täglich
- Port-Scan stündlich

## 🔄 Integration

### VS Code
- Status-Panel via API
- Command-Palette-Integration
- Live-Diagnostics

### Telegram
- `/dashboard status`
- Automatische Alerts
- Tägliche Reports

## 📋 Checkliste für Produktivstart

1. **Umgebung**
   - [ ] Python 3.13 (venv313)
   - [ ] Alle Ports verfügbar
   - [ ] .env konfiguriert

2. **Sicherheit**
   - [ ] Tokens generiert
   - [ ] Port-Policy aktiv
   - [ ] Rate-Limiting eingerichtet

3. **Daten**
   - [ ] Archiv-Verzeichnis existiert
   - [ ] Safepoint-Index initialisiert
   - [ ] Backup-Strategie aktiv

4. **Monitoring**
   - [ ] Health-Checks laufen
   - [ ] Logging aktiviert
   - [ ] Alerts konfiguriert

## 🎯 Akzeptanzkriterien

1. **Performance**
   - Antwortzeit < 200ms
   - Event-Latenz < 100ms
   - Safepoint-Erstellung < 500ms

2. **Sicherheit**
   - Alle Tokens validiert
   - Port-Policy durchgesetzt
   - Audit-Trail lückenlos

3. **Zuverlässigkeit**
   - Zero Single Point of Failure
   - Automatische Wiederherstellung
   - Datenverlust ausgeschlossen

## 📚 Wartung & Support

### Logs
- Rotation: täglich
- Aufbewahrung: 90 Tage
- Format: JSON + Timestamp

### Backup
- Safepoints: stündlich
- Konfig: täglich
- Retention: 30 Tage

### Monitoring
- Grafana-Dashboard
- Prometheus-Metrics
- Alert-Manager

## 🔍 Fehlerbehandlung

### HTTP-Codes
- 200: Erfolg
- 202: Async accepted
- 400: Invalid request
- 401: Unauthorized
- 403: Forbidden
- 429: Rate limit
- 500: Server error

### Retry-Strategie
- Exponential Backoff
- Max 3 Versuche
- Jitter: 100-500ms

## 🏁 Abnahmetest-Szenario

1. **Start**
   ```bash
   ./venv313/bin/python3 main.py --port 12344
   ```

2. **Validierung**
   ```bash
   curl http://127.0.0.1:12344/health
   ```

3. **Test-Sequenz**
   ```bash
   # Health
   curl http://127.0.0.1:12344/health
   
   # Status
   curl http://127.0.0.1:12344/api/status/all
   
   # Command
   curl -X POST http://127.0.0.1:12344/api/command/opena19 \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"action":"ping","strict":true}'
   ```

4. **Erfolgskriterien**
   - Alle Endpoints erreichbar
   - Safepoints erzeugt
   - Events fließen
   - UI responsive