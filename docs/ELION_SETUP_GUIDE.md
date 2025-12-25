# 🧠 ELION Hyper-Dashboard 2.0 - Installations- und Setup-Anleitung

## Systemarchitektur (Option 2)

**Datenfluss:**

- Hinweg → OpenAI → opena1 (Koordinator) → opena2 (Archivator) → kordp → Tool
- Rückweg → Tool → opena2 → opena1 → OpenAI

### 1. Systemvoraussetzungen

**Basis-Anforderungen:**

- **System:** Linux Mint Cinnamon
- **Python:** Version 3.13.x mit virtueller Umgebung venv313
- **Modell:** gpt-5-nano
- **Port-Policy:** 12344-12399 (Port 8080 strikt verboten)
- **RAM:** Mindestens 4GB
- **Speicher:** Mindestens 10GB frei

**Port-Konfiguration:**

- **MCP Server:** Port 12350 (fest zugewiesen)
- **Agent Ports:** 12344-12349 (dynamisch)
- **Verboten:** Port 8080 (strikt)
- **Protokoll:** SSE (Server-Sent Events)
- **Binding:** 0.0.0.0 (alle Interfaces)

### 2. Projektstruktur

Basis-Verzeichnis: `/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/`

````
/
├── 1.opena1&2_portier/         # OpenAI Portier System
│   ├── docs/                 # Dokumentation
│   ├── scripts/              # Startskripte
│   ├── archivp/              # Safepoints & Audit
│   ├── .runtime/             # Laufzeitinfos (Port, PID)
│   └── venv313/             # Python 3.13 venv
├── 2.openwebui/
├── 3.telegram/
├── 4.vscode/
├── 5.browser/
├── 8.telefon_antwort/
├── 9.telefon_anruf/
├── 12.influencer/
├── 13.calendar/
├── 14.html_creator/
├── 15.shop_creator/
├── 16.homepage_creator/
├── 17.local_archiv/
├── 18.aktien_crypto/
└── 19.dashboard_agent/

### 3. Initiale Einrichtung
```bash
# Verzeichnisstruktur erstellen
mkdir -p /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/{docs,scripts,archivp,.runtime}

# Virtual Environment einrichten
python3 -m venv /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313
source /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313/bin/activate

# Pakete installieren
python -m pip install --upgrade pip
pip install fastapi==0.115.5 uvicorn[standard]==0.32.0 pydantic==2.9.2 python-dotenv==1.0.1 fastmcp==2.12.5 mcp-sdk==1.16.0
````

**MCP Server Installation:**

```bash
# MCP Server Abhängigkeiten
pip install fastmcp==2.12.5 mcp-sdk==1.16.0

# Server-Skript erstellen
cat > scripts/start_mcp_server.sh << 'EOL'
#!/usr/bin/env bash
set -euo pipefail

source venv313/bin/activate
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# MCP Server auf Port 12350 starten
python -m fastmcp.server \
  --host 0.0.0.0 \
  --port 12350 \
  --transport sse \
  --name "Agent8 MCP Server"
EOL

chmod +x scripts/start_mcp_server.sh
```

### 4. Umgebungskonfiguration

1. **.env Datei erstellen:**

```bash
cat > /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/.env << EOL
OPENAI_API_KEY=
PORTIER_ENV=production
PORTIER_BASE_DIR=/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier
PORTIER_ALLOWED_PORTS=12344,12345,12346,12347,12348,12349,12350
PORTIER_FORBIDDEN_PORTS=8080
MCP_SERVER_PORT=12350
MCP_SERVER_HOST=0.0.0.0
MCP_TRANSPORT=sse
FASTMCP_VERSION=2.12.5
MCP_SDK_VERSION=1.16.0
EOL
```

2. **Archiv/Safepoints initialisieren:**

```bash
base="/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/archivp"
mkdir -p "$base/$(date +%Y/%m/%d)"
touch "$base/index.jsonl"
```

### 5. Systemstart (Option 2)

**MCP Server Konfiguration:**

- **Server:** Agent8 MCP Server (Port 12350)
- **Transport:** SSE (Server-Sent Events)
- **Endpoints:**
  - Event Stream: http://0.0.0.0:12350/sse
  - Health Check: http://0.0.0.0:12350/health
  - Metrics: http://0.0.0.0:12350/metrics
- **Versionen:**
  - FastMCP: 2.12.5
  - MCP SDK: 1.16.0
- **Monitoring:**
  - Log-Level: INFO
  - Process ID: In .runtime/mcp.pid
  - Status: Via /health endpoint

**Startreihenfolge:**

1. opena2 - Archivator
2. opena1 - Koordinator
3. kordp - Dispatcher
4. Frontend/Tools (opena14-16-19)

**Standardisiertes Startskript:**

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME="$ROOT/.runtime"; LOGDIR="$ROOT/logs"
mkdir -p "$RUNTIME" "$LOGDIR"

pick_port() {
  for p in $(seq 12344 12399); do
    ss -ltn | awk '{print $4}' | grep -q ":$p$" || { echo "$p"; return; }
  done; exit 2
}
PORT="$(pick_port)"
echo -n "$PORT" > "$RUNTIME/port"

source /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313/bin/activate
nohup uvicorn main:app --host 127.0.0.1 --port "$PORT" >> "$LOGDIR/service.out" 2>> "$LOGDIR/service.err" &
for i in $(seq 1 15); do curl -sf "http://127.0.0.1:$PORT/health" && exit 0; sleep 1; done
echo "Healthcheck fehlgeschlagen ($PORT)" >&2; exit 1
```

### 6. System-Validierung

1. **Port-Validierung:**

```bash
ss -ltn sport ge 12344 sport le 12399
```

2. **Erste Inbetriebnahme:**

```bash
source /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/venv313/bin/activate
bash 1.opena1&2_portier/scripts/run_production.sh
```

3. **Health-Check aller Komponenten:**

```bash
for d in 1.opena1&2_portier 16.homepage_creator; do
  PORT=$(cat "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/$d/.runtime/port" 2>/dev/null || true)
  [ -n "$PORT" ] && curl -sf "http://127.0.0.1:$PORT/health" | jq .
done
```

### 7. Safepoints & Audit-System

1. **Safepoint-Format:**

- Dateinamenschema: `SP<epoch>_src→dst_{CMD|RESP}.json`
- Speicherort: `archivp/YYYY/MM/DD/`

2. **Index-Einträge (append-only):**

```json
{
  "sp": "SP1732222222_opena1→opena2_CMD.json",
  "ts": "2025-10-22T10:15:03Z",
  "src": "opena1",
  "dst": "opena2",
  "kind": "CMD",
  "path": "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/archivp/2025/10/22/SP1732222222_opena1→opena2_CMD.json",
  "strict": true
}
```

### 8. Troubleshooting

| Problem           | Prüfung                                 |
| ----------------- | --------------------------------------- |
| Port blockiert    | `ss -ltn sport ge 12344 sport le 12399` |
| Health fail       | `logs/service.err` lesen                |
| Safepoints fehlen | `strict:true` gesetzt?                  |
| 8080 aktiv        | sofort stoppen (Policy-Verstoß)         |

### 9. Dashboard-Architektur

**Komponenten:**

- Backend: Dashboard-Agenten (opena19, opena17)
- Frontend: HTML-Agenten (opena14, opena16)
- Jeder Agent → eigene Dashboard-Seite `/agent/<name>`
- Datenfluss: opena19 API → HTML-Renderer → Option 2-Kette

**Sicherheitsrichtlinien:**

- Strict-Mode: Jedes Request-Objekt muss `"strict": true` enthalten
- Keine Secrets im Code - nur aus `.env` lesen
- Port 8080 ist strikt verboten
- Regelmäßige Health-Checks durchführen

### 10. MCP Server & Deployment

**Server Management:**

```bash
# MCP Server starten
./scripts/start_mcp_server.sh

# Status überprüfen
curl -s http://localhost:12350/health | jq .
curl -s http://localhost:12350/metrics | jq .

# Event-Stream testen
curl -N http://localhost:12350/sse
```

**Log Management:**

```bash
# Live Logs
tail -f logs/mcp_server.log

# Fehlersuche
grep -i error logs/mcp_server.log
jq 'select(.level=="ERROR")' logs/mcp_server.log

# Performance Monitoring
tail -f logs/mcp_metrics.log | jq 'select(.type=="performance")'
```

**Deployment Workflow:**

```bash
# System-Status prüfen
./deployment_status.sh

# Deployment durchführen
./run_deploy.sh

# Port-Belegung verifizieren
ss -ltn sport ge 12344 sport le 12350

# Prozess-Status
cat .runtime/mcp.pid | xargs ps
```

## Support & Ressourcen

**Technischer Support:**

- E-Mail: support@elion-system.de
- Dokumentation: docs.elion-system.de

**MCP Ressourcen:**

- FastMCP Docs: https://gofastmcp.com
- Deployment: https://fastmcp.cloud
- SDK Reference: https://gofastmcp.com/sdk

---

**Stand:** 22. Oktober 2025
**FastMCP Version:** 2.12.5
**MCP SDK Version:** 1.16.0
