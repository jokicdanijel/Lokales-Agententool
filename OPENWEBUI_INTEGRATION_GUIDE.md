# 🌐 OpenWebUI Integration - Vollständige Anleitung

**Datum:** 2025-11-08  
**Status:** ✅ **PRODUKTIONSREIF**

---

## 📋 Übersicht

Diese Dokumentation beschreibt die vollständige Integration zwischen **OpenWebUI** und den **19 Agenten** im ELION-System.

### Komponenten

1. **openwebui_integration.py** - Zentrale Manager-Klasse für Agent-Verwaltung
2. **openwebui_adapter.py** - HTTP-Adapter für externe Verbindungen
3. **.vscode/launch.json** - Debug-Konfigurationen für VS Code
4. **.vscode/tasks.json** - Automation und Testing-Tasks

---

## 🚀 Quick Start

### 1. Installation

```bash
cd /path/to/Gesamtprojekt

# Installiere Abhängigkeiten
pip install -r 19.dashboard_agent/requirements.txt
pip install aiohttp pydantic python-dotenv

# (Optional) Installiere Development-Tools
pip install pytest black flake8 mypy
```

### 2. Starten aller Services (Terminal)

```bash
# Alle Services starten
bash bin/ops.sh start

# Services registrieren
bash bin/ops.sh agents:register

# Health-Check
bash bin/ops.sh health
```

### 3. Starten aller Services (VS Code Debug)

**Schritte:**
1. Öffne VS Code
2. Drücke `Ctrl+Shift+D` (Run and Debug)
3. Wähle **"Start: Alle Services"** aus der Dropdown
4. Drücke den grünen Play-Button

**Ergebnis:** Alle 5 Services starten parallel in separaten Terminals:
- Dashboard (Port 12349)
- Agent opena1 (Port 12344)
- Agent opena2 (Port 12345)
- Agent kordp (Port 12346)
- OpenWebUI (Port 3000)

### 4. Testen in VS Code Tasks

**Schritte:**
1. Drücke `Ctrl+Shift+P` (Command Palette)
2. Gib "Tasks: Run Task" ein
3. Wähle eine Task aus:
   - `ops: health check` - Prüft alle Services
   - `test: curl all agents health` - Testet alle Agent-Ports
   - `git: push origin main` - Pusht zu GitHub

---

## 📚 API-Referenz

### OpenWebUI Integration Manager

```python
from openwebui_integration import get_manager

# Manager abrufen
manager = await get_manager()

# Agenten registrieren (automatisch beim Start)
manager.register_all_default_agents()

# Health-Check aller Agenten
results = await manager.health_check_all()

# Agent aufrufen
response = await manager.invoke_agent(
    agent_id="opena1",
    payload={"test": "data"},
    timeout_seconds=30
)

# Agent-Liste abrufen
agents = manager.get_agents_list()

# Health-Summary
summary = manager.get_health_summary()
```

### Datatenmodelle

```python
# Agent definieren
agent = Agent(
    agent_id="opena1",
    name="Coordinator",
    port=12344,
    category=AgentCategory.CORE,
    description="Orchestrator Phase 1"
)

# Health-Check Result
result = HealthCheckResult(
    agent_id="opena1",
    healthy=True,
    response_time_ms=45.3,
    status_code=200
)

# Chat-Request
request = ChatRequest(
    agent_id="opena1",
    message="Hallo, wie geht es dir?",
    context={"session_id": "123"}
)

# Chat-Response
response = ChatResponse(
    agent_id="opena1",
    response="Es geht mir gut, danke der Nachfrage!",
    confidence=0.95
)
```

---

## 🔧 Konfiguration

### Environment Variables

```env
# .env Datei im Projekt-Root
DASHBOARD_ADMIN_TOKEN=your_token_here
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret

# Optional
LOG_LEVEL=INFO
OPENWEBUI_HOST=0.0.0.0
OPENWEBUI_PORT=3000
```

### Agent-Ports

| Agent-ID | Name | Port | Kategorie |
|----------|------|------|-----------|
| opena1 | Coordinator | 12344 | Core |
| opena2 | Archivator | 12345 | Core |
| kordp | Scheduler | 12346 | Core |
| opena4 | Telegram | 12347 | Integration |
| opena5 | Browser | 12348 | Tools |
| opena6 | Email | 12349 | Tools |
| opena7 | WhatsApp | 12350 | Integration |
| opena8 | Telephone | 12351 | Integration |
| opena9 | Call Tracking | 12352 | Analytics |
| opena10 | Unlock | 12353 | Security |
| opena11 | Social Media | 12359 | Integration |
| opena12 | Influencer | 12360 | Tools |
| opena13 | Calendar | 12361 | Tools |
| opena14 | HTML Creator | 12362 | Tools |
| opena15 | Shop | 12363 | Business |
| opena16 | CRM | 12364 | Business |
| opena17 | Analytics | 12365 | Analytics |
| opena18 | Dashboard | 12366 | UI |
| opena19 | Workflow | 12367 | Automation |

---

## 📊 Health-Check

### Einzelnen Agenten prüfen

```bash
curl -s http://127.0.0.1:12344/health | jq .
```

**Response:**
```json
{
  "status": "ok",
  "service": "opena1",
  "port": 12344,
  "version": "1.0.0"
}
```

### Alle Agenten prüfen

```bash
for port in {12344..12367}; do
  echo "Port $port:"
  curl -s http://127.0.0.1:$port/health | jq . 2>/dev/null || echo "❌ Not responding"
done
```

### Dashboard-Status abrufen

```bash
curl -s http://127.0.0.1:12349/api/status/all | jq .
```

---

## 🧪 Testing

### Unit-Tests ausführen

```bash
cd 19.dashboard_agent
python3 -m pytest tests/ -v
```

### Integration-Test

```bash
# Test openwebui_integration.py
python3 19.dashboard_agent/openwebui_integration.py
```

**Expected Output:**
```
=== Agenten-Liste ===
  opena1     | Coordinator         | Port 12344 | Core
  opena2     | Archivator          | Port 12345 | Core
  ...

=== Health-Check ===
  opena1     | ✅ OK | 45.3ms
  opena2     | ✅ OK | 52.1ms
  ...

=== Summary ===
  Total: 19 | Healthy: 19 | Unhealthy: 0 | Percentage: 100.0%
```

---

## 🔗 Integration Points

### OpenWebUI → Dashboard

```bash
# Dashboard registriert sich selbst auf Port 12349
POST http://127.0.0.1:12349/api/agent/register
Authorization: Bearer $(cat .env | head -1)
Content-Type: application/json

{
  "agent_id": "openwebui",
  "endpoint": "http://127.0.0.1:3000"
}
```

### OpenWebUI → Agenten

```bash
# Rufe opena1 auf
POST http://127.0.0.1:12344/invoke
Content-Type: application/json

{
  "prompt": "Hallo, wie geht es dir?",
  "context": {}
}
```

### Archivator (opena2) für Persistenz

```bash
# Speichere Daten im Archivator
POST http://127.0.0.1:12345/store/archivp
Content-Type: application/json

{
  "src": "openwebui",
  "dst": "opena2",
  "kind": "CHAT_LOG",
  "payload": {
    "user_message": "...",
    "agent_response": "...",
    "timestamp": "2025-11-08T..."
  }
}
```

---

## 📈 Monitoring

### Logs ansehen

```bash
# Dashboard-Logs
tail -f 19.dashboard_agent/logs/dashboard.nohup.log

# Agent-Logs
tail -f 3.opena1_coordinator/logs/app.log

# OpenWebUI-Logs
tail -f 2.openwebui/logs/app.log
```

### Performance-Metriken

Die `openwebui_integration.py` speichert Metriken:

```python
manager.health_cache  # Dict[agent_id: str, HealthCheckResult]
                       # Entält response_time_ms pro Agent
```

---

## ⚡ Troubleshooting

### Problem: Port bereits in Verwendung

```bash
# Finde Prozess auf Port
lsof -i :12344

# Beende Prozess
kill -9 <PID>

# Oder: Stoppe alle Services
bash bin/ops.sh stop
```

### Problem: Agent antwortet nicht

```bash
# Prüfe, ob Agent läuft
curl -s http://127.0.0.1:12344/health

# Prüfe Logs
tail -f 3.opena1_coordinator/logs/app.log

# Starte Agent neu
cd 3.opena1_coordinator
python3 main.py
```

### Problem: Health-Check fehlgeschlagen

```bash
# Debugge mit verbosem curl
curl -v http://127.0.0.1:12344/health

# Prüfe Firewall-Regeln
sudo ufw allow 12344
```

---

## 📝 Development Workflow

### 1. Änderungen an openwebui_integration.py

```bash
# Format Code
python3 -m black 19.dashboard_agent/openwebui_integration.py

# Lint
python3 -m flake8 19.dashboard_agent/openwebui_integration.py

# Type-Check
python3 -m mypy 19.dashboard_agent/openwebui_integration.py
```

### 2. Git-Workflow

```bash
# Änderungen stagen
git add 19.dashboard_agent/openwebui_integration.py

# Committe
git commit -m "feat: improve OpenWebUI integration manager"

# Pushe
git push origin main
```

### 3. Testing vor Merge

```bash
# Führe Tests aus
cd 19.dashboard_agent
python3 -m pytest -v tests/

# Starte Services
bash ../bin/ops.sh start

# Verifiziere Health
bash ../bin/ops.sh health
```

---

## 🎯 Nächste Schritte

- [ ] OpenWebUI Docker-Container einrichten
- [ ] WebSocket-Support für Echtzeit-Chat
- [ ] Caching-Layer für häufige Anfragen
- [ ] Automatische Retry-Logik
- [ ] Metriken-Export (Prometheus)
- [ ] Performance-Optimierung

---

## 📞 Support

**Bei Problemen:**
1. Prüfe logs/ Verzeichnisse
2. Führe `bash bin/ops.sh health` aus
3. Prüfe die `.env` Konfiguration
4. Konsultiere die README-Dateien in den Agent-Verzeichnissen

---

**Zuletzt aktualisiert:** 2025-11-08  
**Version:** 1.0.0  
**Status:** Production Ready ✅
