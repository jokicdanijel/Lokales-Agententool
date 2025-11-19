# LocalAgent-Pro — GitHub Copilot Instructions

**Handlungsorientierte Hinweise für KI-Coding-Agenten** — damit du in diesem Repo sofort produktiv bist.

---

## 🎯 Projekt-Übersicht

**LocalAgent-Pro** ist ein Flask-basierter AI-Agent-Server mit OpenWebUI-Integration:

- **Stack:** Python 3.12, Flask, OpenAI SDK, Ollama (LLM)
- **Zweck:** Lokaler Tool-Agent für Dateisystem-Operationen, Web-Fetching, Shell-Execution
- **Integration:** OpenWebUI (Port 3000), Agent-Server (Port 8001)
- **Sicherheit:** Sandbox-Modus, Domain-Whitelist, Loop-Protection
- **Storage:** SQLite Knowledge DB, Prometheus Monitoring

---

## 📁 Wichtige Dateien & Einstiegspunkte

```
LocalAgent-Pro/
├── src/
│   ├── openwebui_agent_server.py  # Haupt-Server (Production)
│   ├── simple_agent.py             # Vereinfachter Demo-Server
│   ├── tools/                      # Tool-Implementierungen
│   └── knowledge_db/               # Wissens-Datenbank
├── config/
│   ├── config.yaml                 # Hauptkonfiguration
│   ├── config_safe.yaml            # Safe-Mode (Loop-Protection)
│   └── domain_whitelist.yaml       # Domain Auto-Whitelist
├── scripts/
│   ├── restart_server.sh           # Server neu starten
│   ├── health_check.sh             # Health-Check
│   └── cleanup_logs.sh             # Log-Rotation
├── logs/                           # Server-Logs
├── sandbox/                        # Sandbox-Verzeichnis
└── workspace/                      # Test-Dateien
```

**Manifestdateien:**

- `requirements.txt` — Python Dependencies
- `config/config.yaml` — Runtime-Konfiguration
- `.gitignore` — Git-Ausschlüsse (inkl. venv)

---

## 🚀 Schnellstart-Befehle

### Server-Management

```bash
# Server starten
bash restart_server.sh

# Server stoppen
bash stop_server.sh

# Health-Check
curl http://127.0.0.1:8001/health | jq '.'

# Logs live anzeigen
tail -f logs/server.log

# Logs analysieren
bash analyze_logs.sh
```

### Testen

```bash
# Tool-Endpunkt testen
curl -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Liste alle Dateien auf"}'

# Chat-Interaktion
./chat-local.sh 'Erstelle Datei test.txt mit Hello World'

# Ollama-Integration testen
python3 test_ollama_integration.py
```

### Entwicklung

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Code-Qualität prüfen
python3 -m mypy src/
python3 -m pylint src/
```

---

## ⚙️ Konfiguration verstehen

### `config/config.yaml` — Haupteinstellungen

```yaml
sandbox: true # Sandbox-Modus (Datei-Isolation)
sandbox_path: "~/localagent_sandbox" # Sandbox-Verzeichnis

allowed_domains: # Domain-Whitelist für fetch()
  - "github.com"
  - "docs.python.org"

shell_execution:
  enabled: false # Shell-Commands deaktiviert (Sicherheit)
  require_explicit_trigger: true # Nur mit "execute", "run" Trigger

loop_protection: # Loop-Protection (Safe-Mode)
  enabled: true
  max_retries: 1

llm:
  base_url: "http://localhost:11434/v1" # Ollama API
  model: "llama3.1" # LLM-Modell
```

**Wichtig:**

- `sandbox: true` → Alle Dateien gehen nach `~/localagent_sandbox/`
- `shell_execution.enabled: false` → **Verhindert Loop-Problem** (siehe unten)

---

## 🔒 Sicherheits-Features (WICHTIG!)

### 1. Loop-Problem (BEHOBEN)

**Problem:** Früher interpretierte der Server normale Texteingaben als Shell-Commands → Endlosschleifen.

**Lösung:**

- `config_safe.yaml` verwenden (bereits aktiv)
- `shell_execution.enabled: false` (Standard)
- Loop-Protection mit `max_retries: 1`

**Dokumentation:** Siehe `LOOP_PROBLEM_ANALYSIS.md`, `LOOP_FIX_SUMMARY.md`

### 2. Sandbox-Modus

Alle Datei-Operationen werden in `~/localagent_sandbox/` umgeleitet:

```python
# User fragt: "Erstelle /etc/passwd"
# Tatsächlicher Pfad: ~/localagent_sandbox/etc/passwd ✅
```

### 3. Domain-Whitelist

Nur erlaubte Domains für `fetch()`:

```python
# ✅ fetch("https://github.com/...")  → Erlaubt
# ❌ fetch("https://evil.com/...")    → Blockiert
```

---

## 🛠️ Code-Änderungen: Best Practices

### Pattern: Tool-Implementierung

Neue Tools in `src/tools/` hinzufügen:

```python
# src/tools/new_tool.py
def my_new_tool(param: str) -> str:
    """Tool-Beschreibung für LLM."""
    # Implementierung
    return result

# In openwebui_agent_server.py registrieren:
TOOLS["my_new_tool"] = my_new_tool
```

### Pattern: Config-Änderungen

1. **Backup erstellen:** `cp config/config.yaml config/config_backup.yaml`
2. **Änderungen vornehmen**
3. **Server neu starten:** `bash restart_server.sh`
4. **Testen:** `curl http://127.0.0.1:8001/health`

### Anti-Pattern: Direkter DB-Zugriff

❌ **Nicht tun:**

```python
conn = sqlite3.connect('knowledge.db')
conn.execute("DROP TABLE ...") # Destruktiv!
```

✅ **Stattdessen:**

```python
from src.knowledge_db.manager import KnowledgeDB
kb = KnowledgeDB()
kb.safe_operation()  # Nutze API
```

---

## 🔍 Debugging & Troubleshooting

### Häufige Probleme

**Problem:** Server startet nicht

```bash
# Prüfe Port
sudo lsof -i :8001

# Prüfe Logs
tail -50 logs/server.log

# Prüfe Config-Syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

**Problem:** "Exit Code: 2" Fehler in Logs
→ **Loop-Problem aktiv!** Siehe `LOOP_FIX_QUICKSTART.md`

**Problem:** Ollama nicht erreichbar

```bash
# Ollama-Status prüfen
curl http://localhost:11434/api/tags

# Ollama neu starten
pkill ollama && ollama serve
```

---

## 📖 Dokumentations-Hierarchie

### Für Quick-Start:

1. `QUICK_START.md` — Erste Schritte
2. `SOFORT_START.md` — Installations-Guide
3. `README.md` — Projekt-Übersicht

### Für Entwicklung:

1. `COMPLETE_GUIDE.md` — Vollständige Referenz
2. `ENDPOINT_CHEATSHEET.md` — API-Endpunkte
3. `LOGGING_GUIDE.md` — Logging-Konfiguration

### Für Probleme:

1. `LOOP_FIX_QUICKSTART.md` — Loop-Problem 2-Min-Fix
2. `LOOP_PROBLEM_ANALYSIS.md` — Technische Analyse
3. `SECURITY_UPDATE.md` — Sicherheits-Updates

### Für Integration:

1. `OPENWEBUI_INTEGRATION.md` — OpenWebUI Setup
2. `PROMETHEUS_INTEGRATION.md` — Monitoring
3. `ELION_INTEGRATION.md` — Elion-CLI

---

## 💡 Typische Agent-Aufgaben

### Datei-Operationen

```bash
./chat-local.sh 'Liste alle Dateien im workspace auf'
./chat-local.sh 'Lies config/config.yaml'
./chat-local.sh 'Erstelle test.txt mit "Hello LocalAgent"'
```

### Code-Analyse

```bash
./chat-local.sh 'Zeige mir alle Python-Dateien in src/'
./chat-local.sh 'Erkläre die Tool-Architektur'
./chat-local.sh 'Welche Dependencies werden verwendet?'
```

### Troubleshooting

```bash
./chat-local.sh 'Warum startet der Server nicht?'
./chat-local.sh 'Analysiere die letzten 50 Log-Einträge'
./chat-local.sh 'Prüfe ob Ollama erreichbar ist'
```

---

## 🧪 Testing-Checkliste

Vor jedem Commit:

- [ ] `bash restart_server.sh` erfolgreich
- [ ] Health-Check: `curl http://127.0.0.1:8001/health` → `status: ok`
- [ ] Keine Errors in `logs/server.log`
- [ ] Loop-Test: Sende problematischen Input (`/mnt/data/test.py`) → Keine Loops
- [ ] Sandbox-Test: Datei erstellen → Landet in `~/localagent_sandbox/`

---

## 🚨 Kritische Regeln

1. **NIE `venv/` committen** — Ist bereits in `.gitignore`
2. **NIE `shell_execution.enabled: true`** ohne Loop-Protection
3. **IMMER** Config-Backups vor Änderungen
4. **IMMER** Safe-Mode testen nach Code-Änderungen
5. **NIE** destruktive DB-Operationen ohne Migration

---

## 📊 Monitoring & Metrics

### Health-Check Response

```json
{
  "status": "ok",
  "sandbox": true,
  "model": "llama3.1",
  "allowed_domains": ["github.com", "..."],
  "server_time": 1732000000
}
```

### Log-Analyse

```bash
# Fehler zählen
grep -c "ERROR" logs/server.log

# Loop-Erkennungen
grep "Loop" logs/server.log

# Shell-Executions
grep "Shell-Kommando" logs/server.log
```

---

## 🎯 Nächste Schritte für Agenten

1. **Erste Orientierung:** Lies `README.md` und `QUICK_START.md`
2. **Server starten:** `bash restart_server.sh`
3. **Test ausführen:** `./chat-local.sh 'Hallo LocalAgent!'`
4. **Config verstehen:** Öffne `config/config.yaml`
5. **Code erkunden:** Starte in `src/openwebui_agent_server.py`

---

**Status:** ✅ Production-Ready | **Letzte Aktualisierung:** 19.11.2025  
**Für Fragen:** Siehe `COMPLETE_GUIDE.md` oder führe `./chat-local.sh` mit deiner Frage aus.
