# LocalAgent-Pro Knowledge DB Tooling

## Übersicht

Drei neue Tools zur automatischen Verwaltung und Abfrage der LocalAgent-Pro Knowledge Database:

1. **GitHub Action** - Validiert Knowledge DB bei jedem Commit
2. **Update-Script** - Aktualisiert Knowledge DB automatisch
3. **Query-Tool** - Ermöglicht programmatische Abfragen (für opena1)

---

## 1. GitHub Action: Knowledge DB Validator

**Datei:** `.github/workflows/knowledge_db_validator.yml`

### Funktionen

- ✅ Validiert Config-Files aus Knowledge DB
- ✅ Prüft Quick-Check Command Syntax
- ✅ Validiert ELION Integration Schema
- ✅ Erstellt Validation Report als Artifact
- ✅ Kommentiert PR mit Ergebnissen

### Trigger

- Push auf `main` oder `develop`
- Pull Requests
- Täglich um 06:00 UTC (Cronjob)

### Verwendung

Automatisch bei jedem Commit. Validation Report verfügbar unter:

- GitHub Actions → Artifacts → `knowledge-db-validation-report`

---

## 2. Update-Script: Auto-Update Knowledge DB

**Datei:** `scripts/update_knowledge_db.py`

### Funktionen

- 🔄 Aktualisiert `config/localagent_knowledge_db.json` mit aktuellem Runtime-Status
- 📡 Holt Daten von:
  - `/health` Endpoint
  - `/metrics` Endpoint
  - Prometheus Targets API
  - Prozess-Status
- 📅 Fügt `last_updated` Timestamp hinzu

### Verwendung

#### Manuell

```bash
cd LocalAgent-Pro
python3 scripts/update_knowledge_db.py
```

#### VSCode Task

```
Ctrl+Shift+P → "Tasks: Run Task" → "LocalAgent-Pro: Update Knowledge DB"
```

#### Cronjob (stündlich)

```bash
# Crontab eintragen:
0 * * * * cd /home/danijel-jd/.../LocalAgent-Pro && python3 scripts/update_knowledge_db.py
```

### Output-Beispiel

```
🔄 LocalAgent-Pro Knowledge DB Auto-Update
📅 Timestamp: 2025-11-19T05:00:00

📡 Fetching health data...
   ✅ Status: ok
   ✅ Model: llama3.1
   ✅ Sandbox: True
📊 Counting metrics...
   ✅ Metrics: 33
🎯 Checking Prometheus target...
   ✅ Target health: up
⚙️ Checking process info...
   ✅ Process running

✅ Knowledge DB update complete!
📄 File: config/localagent_knowledge_db.json
```

---

## 3. Query-Tool: Knowledge DB Abfragen (für opena1)

**Datei:** `tools/knowledge_db_query.py`

### Funktionen

Python-API für programmatische Abfragen der Knowledge DB.

### Verwendung als Python-Modul

```python
from tools.knowledge_db_query import KnowledgeDBQuery

# Initialisieren
kb = KnowledgeDBQuery()

# Runtime-Queries
status = kb.get_runtime_status()           # "ok"
model = kb.get_model()                     # "llama3.1"
sandbox = kb.is_sandbox_enabled()          # True
sandbox_path = kb.get_sandbox_path()       # "/home/danijel-jd/localagent_sandbox"

# Monitoring-Queries
metrics_count = kb.get_metrics_count()     # 33
prometheus_healthy = kb.is_prometheus_healthy()  # True

# ELION Integration Queries
agent_id = kb.get_agent_id()               # "opena21"
agent_port = kb.get_agent_port()           # 12364
coordinator = kb.get_coordinator()         # "opena1"
archivator = kb.get_archivator()           # "opena2"

# Quick-Check Commands
health_cmd = kb.get_quick_check_command('health_check')
health_output = kb.run_quick_check('health_check')

# Validation
validation = kb.validate()  # {"runtime": True, "monitoring": True, ...}
```

### Verwendung als CLI-Tool

```bash
# Status-Check
python3 tools/knowledge_db_query.py --status
# Output: Runtime Status: ok

# Modell-Info
python3 tools/knowledge_db_query.py --model
# Output: Model: llama3.1

# Sandbox-Check
python3 tools/knowledge_db_query.py --sandbox
# Output: Sandbox Enabled: True
#         Sandbox Path: /home/danijel-jd/localagent_sandbox

# Metriken
python3 tools/knowledge_db_query.py --metrics
# Output: Metrics Count: 33

# Prometheus
python3 tools/knowledge_db_query.py --prometheus
# Output: Prometheus Target: up ✅

# ELION Agent-Info
python3 tools/knowledge_db_query.py --agent-id
# Output: ELION Agent ID: opena21
#         ELION Port: 12364

# Koordinator-Info
python3 tools/knowledge_db_query.py --coordinator
# Output: Coordinator: opena1
#         Archivator: opena2

# Quick-Check ausführen
python3 tools/knowledge_db_query.py --quick-check health_check
# Output: {"status":"ok","model":"llama3.1",...}

# Validation
python3 tools/knowledge_db_query.py --validate
# Output: Knowledge DB Validation:
#           ✅ runtime
#           ✅ config_files
#           ✅ monitoring
#           ✅ integration
#           ✅ quick_checks
#           ✅ meta
#           ✅ all_valid

# JSON-Export
python3 tools/knowledge_db_query.py --json
# Output: komplette Knowledge DB als JSON

# Zusammenfassung (ohne Argumente)
python3 tools/knowledge_db_query.py
# Output: LocalAgent-Pro Knowledge DB Summary:
#           Status: ok
#           Model: llama3.1
#           Sandbox: True
#           Metrics: 33
#           Prometheus: up
#           Agent: opena21 (Port 12364)
```

---

## VSCode Tasks

Vier neue Tasks wurden zur `tasks.json` hinzugefügt:

### 1. Update Knowledge DB

```
Ctrl+Shift+P → "Tasks: Run Task" → "LocalAgent-Pro: Update Knowledge DB"
```

Aktualisiert `config/localagent_knowledge_db.json` mit aktuellem Status.

### 2. Query Status

```
Ctrl+Shift+P → "Tasks: Run Task" → "LocalAgent-Pro: Query Knowledge DB (Status)"
```

Zeigt Runtime-Status, Model, Sandbox, Metrics, Prometheus.

### 3. Validate Knowledge DB

```
Ctrl+Shift+P → "Tasks: Run Task" → "LocalAgent-Pro: Validate Knowledge DB"
```

Prüft, ob alle erforderlichen Sektionen vorhanden sind.

### 4. Run Health Check

```
Ctrl+Shift+P → "Tasks: Run Task" → "LocalAgent-Pro: Run Health Check"
```

Führt Health-Check Command aus und zeigt Response.

---

## Integration in opena1 (ELION Koordinator)

### Beispiel: opena1 prüft LocalAgent-Pro Status

```python
# In opena1 Agent-Code
import sys
sys.path.append('/home/danijel-jd/.../LocalAgent-Pro')

from tools.knowledge_db_query import KnowledgeDBQuery

def check_opena21_availability():
    """Prüft, ob opena21 (LocalAgent-Pro) verfügbar ist."""
    kb = KnowledgeDBQuery()
    
    # Runtime-Check
    if kb.get_runtime_status() != "ok":
        return False, "LocalAgent-Pro status not ok"
    
    # Prometheus-Check
    if not kb.is_prometheus_healthy():
        return False, "Prometheus target down"
    
    # Sandbox-Check (sollte aktiv sein)
    if not kb.is_sandbox_enabled():
        return False, "Sandbox not enabled"
    
    return True, "opena21 ready"

# Verwendung in Task-Dispatch
available, msg = check_opena21_availability()
if available:
    # Dispatch Task zu opena21
    endpoint = kb.get_upstream_endpoint()  # http://127.0.0.1:8001
    # ... send request
else:
    # Fallback oder Fehlerbehandlung
    print(f"opena21 unavailable: {msg}")
```

### Beispiel: opena1 führt Quick-Check aus

```python
from tools.knowledge_db_query import KnowledgeDBQuery

kb = KnowledgeDBQuery()

# Führe Health-Check aus
health_output = kb.run_quick_check('health_check')

if health_output:
    import json
    health_data = json.loads(health_output)
    
    if health_data.get('status') == 'ok':
        print("opena21 healthy")
    else:
        print("opena21 degraded")
else:
    print("opena21 unreachable")
```

---

## Wartung

### Knowledge DB aktualisieren

```bash
# Manuell
python3 scripts/update_knowledge_db.py

# Automatisch (Cronjob)
0 * * * * cd /path/to/LocalAgent-Pro && python3 scripts/update_knowledge_db.py
```

### GitHub Action deaktivieren

Datei `.github/workflows/knowledge_db_validator.yml` löschen oder:

```yaml
on:
  workflow_dispatch:  # Nur manuell triggern
```

---

## Fehlerbehebung

### "Knowledge DB not found"

```bash
# Prüfe Pfad
ls -la config/localagent_knowledge_db.json

# Falls nicht vorhanden: Erstelle aus Template
# (siehe docs/LOCALAGENT_KNOWLEDGE.md)
```

### "Health data unavailable"

```bash
# Prüfe ob Server läuft
curl http://127.0.0.1:8001/health

# Falls nicht: Server starten
bash start_server.sh
```

### "Prometheus target status unavailable"

```bash
# Prüfe Prometheus
curl http://localhost:9090/api/v1/targets

# Falls nicht: Prometheus starten
docker start prometheus-elion
```

---

## Zusammenfassung

**3 neue Tools für vollautomatische Knowledge DB Verwaltung:**

1. ✅ **GitHub Action** - CI/CD Validation bei jedem Commit
2. ✅ **Update-Script** - Automatische Aktualisierung (manuell/VSCode/Cron)
3. ✅ **Query-Tool** - Programmatische Abfragen für opena1 und andere Tools

**Integration in ELION:**

- opena1 kann jederzeit LocalAgent-Pro Status abfragen
- Keine manuellen Checks mehr nötig
- Single Source of Truth für alle Agenten

**Nächste Schritte:**

- Cronjob für stündliche Updates einrichten
- opena1 Agent-Code erweitern (Knowledge DB Integration)
- Monitoring-Alerts bei Schema-Änderungen (GitHub Action)
