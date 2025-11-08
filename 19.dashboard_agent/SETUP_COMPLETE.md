# ELION Hyper-Dashboard Setup - Vollständig

## ✅ Alle 20 Aufgaben abgeschlossen

### VS Code Integration
- ✅ `.vscode/launch.json` - Debug/Start aller 4 Services einzeln oder zusammen
- ✅ `.vscode/tasks.json` - 8 Tasks für ops.sh Befehle (start, stop, health, status, etc.)

### Zentrale Orchestrierung
- ✅ `bin/ops.sh` - Hauptskript mit allen Befehlen
- ✅ `bin/start_all.sh` - Startet alle Services
- ✅ `bin/stop_all.sh` - Stoppt alle Services
- ✅ `bin/verify_stack.sh` - Integrationslauf (health → register → status → write)
- ✅ `bin/agents_register.sh` - Registriert Agenten

### Entwickler-Tools
- ✅ `bin/print_token.sh` - Zeigt .env Token
- ✅ `bin/check_ports.sh` - Prüft Ports 12344/45/46/49/8080
- ✅ `bin/log_tail.sh` - Folgt allen Log-Dateien
- ✅ `bin/reset_today.sh` - Zeigt heutige Archiv-Dateien
- ✅ `bin/clean_pycache.sh` - Bereinigt __pycache__
- ✅ `bin/env_bootstrap.sh` - Erzeugt .env falls fehlend

### Python-Tools & Tests
- ✅ `scripts/register_agents.py` - Python-Alternative zu curl
- ✅ `scripts/curl_examples.sh` - Goldene cURL-Befehle
- ✅ `tests/test_archivator.py` - Pytest für opena2

### Dokumentation
- ✅ `docs/OPERATIONS.md` - Operator-Leitfaden
- ✅ `docs/OPENWEBUI_INTEGRATION.md` - OpenWebUI (opena3) Anbindung
- ✅ `README_STACK_START.md` - QuickStart Guide
- ✅ `sse_bus.py` - Bereits mit Heartbeat (kein Update nötig)

## 🚀 Sofort-Start

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/19.dashboard_agent

# 1. Token sicherstellen
./bin/env_bootstrap.sh

# 2. Alle Services starten
./bin/ops.sh start

# 3. Agenten registrieren
./bin/ops.sh agents:register

# 4. Status prüfen
./bin/ops.sh status | jq .

# 5. Write-Test
./bin/ops.sh write:test

# 6. Logs verfolgen
./bin/ops.sh logs
```

## 🎯 VS Code Features

### Debug & Run
- Öffne "Run and Debug" (Ctrl+Shift+D)
- Wähle "Start: Alle Services" für kompletten Stack
- Oder starte Services einzeln

### Tasks
- Terminal → Run Task (Ctrl+Shift+P → "Tasks: Run Task")
- Wähle z.B. "ops: verify" für kompletten Test

## 📊 Alle verfügbaren Befehle

```bash
./bin/ops.sh start              # Alle Services starten
./bin/ops.sh stop               # Alle Services stoppen
./bin/ops.sh health             # Dashboard /health
./bin/ops.sh status             # Status aller Agenten
./bin/ops.sh agents:register    # Agenten registrieren
./bin/ops.sh agents:check       # Agenten direkt prüfen
./bin/ops.sh write:test         # Schreib-/Lese-Test
./bin/ops.sh logs               # Logs anzeigen
./bin/ops.sh verify             # Kompletter Integrationslauf
```

## 🔧 Zusätzliche Tools

```bash
./bin/print_token.sh            # Token anzeigen
./bin/check_ports.sh            # Port-Status
./bin/log_tail.sh               # Live-Logs folgen
./bin/reset_today.sh            # Heutige Archiv-Dateien
./bin/clean_pycache.sh          # Cache bereinigen
python3 scripts/register_agents.py  # Python-Registrierung
./scripts/curl_examples.sh      # cURL-Beispiele
```

## 📁 Ports

| Service   | Port  | Beschreibung        |
|-----------|-------|---------------------|
| Dashboard | 12349 | Hauptdashboard      |
| opena1    | 12344 | Agent 1             |
| opena2    | 12345 | Archivator          |
| kordp     | 12346 | Koordinator         |
| opena3    | 8080  | OpenWebUI (optional)|

## 🧪 Tests

```bash
# Pytest für Archivator (wenn opena2 läuft)
pytest -q tests/test_archivator.py

# Oder Verify-Skript für alles
./bin/verify_stack.sh
```

## ⚠️ Wichtige Hinweise

1. **JavaScript gehört NICHT in Bash** - fetch(...) nur in Browser-Konsole (F12)
2. **Python-Code nie in Bash pasten** - Dateien editieren, dann Services neu starten
3. **Token in .env** - wird automatisch bei erstem Dashboard-Start oder via env_bootstrap.sh erzeugt
4. **Logs** - Immer in `logs/*.nohup.log` und `logs/*_runtime.log`

## 🎉 Fertig!

Alle 20 Dateien erstellt und getestet. Der Stack ist jetzt vollständig dokumentiert und scriptbar.
