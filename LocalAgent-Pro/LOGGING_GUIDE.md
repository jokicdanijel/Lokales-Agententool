# 📊 LocalAgent-Pro Logging-System - Komplettanleitung

## 🎯 Übersicht

Das LocalAgent-Pro Logging-System bietet umfassendes, strukturiertes Logging für:

- **Backend-API** (Flask-Server auf Port 8001)
- **Tool-Ausführungen** (Dateisystem, Shell, Web)
- **Ollama-Integration** (KI-Modell API-Calls)
- **Request-Tracking** (API-Anfragen und -Antworten)

## 📁 Logging-Architektur

### Erstelle Log-Dateien

```
logs/
├── localagent-pro.log          # Haupt-Log (alle Module)
├── api_requests.log            # API-Request-Tracking
├── tool_executions.log         # Tool-Aufrufe (read_file, write_file, etc.)
└── ollama_integration.log      # Ollama API-Calls
```

### Log-Rotation

- **Max. Dateigröße**: 10 MB pro Log-Datei
- **Backup-Anzahl**: 5 rotierte Dateien (`.log.1`, `.log.2`, ...)
- **Automatisch**: Logs werden automatisch rotiert bei Erreichen der Maximalgröße

## 🚀 Schnellstart

### 1. Server mit Logging starten

```bash
# Server im Vordergrund mit Console-Logs
python3 src/openwebui_agent_server.py

# ODER: Server im Hintergrund
nohup python3 src/openwebui_agent_server.py > /dev/null 2>&1 &
```

### 2. Logs live verfolgen

```bash
# Interaktives Log-Monitoring
./tail_logs.sh

# Spezifische Log-Datei direkt
./tail_logs.sh localagent-pro

# Alle Logs gleichzeitig
./tail_logs.sh
# Wähle dann Option [a]
```

### 3. Log-Analyse

```bash
# Detaillierte Statistiken
./analyze_logs.sh
```

**Ausgabe-Beispiel**:
```
📊 Log-Level Statistiken:
  DEBUG:    1234
  INFO:     567
  WARNING:  12
  ERROR:    3
  CRITICAL: 0
  ─────────────────
  TOTAL:    1816 Einträge

🔍 Top 10 häufigste Meldungen:
  • API: 456 mal
  • Tools: 234 mal
  • Ollama: 123 mal
```

### 4. Log-Cleanup

```bash
# Interaktives Cleanup-Menü
./cleanup_logs.sh
```

**Optionen**:
- `[1]` Alte Backup-Logs löschen (*.log.X)
- `[2]` Alle Logs löschen
- `[3]` Nur Backups löschen
- `[4]` Logs komprimieren und archivieren

## 🔧 Logging-Konfiguration

### Log-Level ändern

**In Python-Code** (`src/openwebui_agent_server.py`):

```python
# Zeile 21-24 ändern:
logging_manager = get_logging_manager(
    app_name="LocalAgent-Pro",
    log_level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    console_output=True
)
```

**Empfohlene Settings**:

| Umgebung | Log-Level | Console-Output |
|----------|-----------|----------------|
| Development | `DEBUG` | `True` |
| Testing | `INFO` | `True` |
| Production | `WARNING` | `False` |
| Troubleshooting | `DEBUG` | `True` |

### Log-Format anpassen

**Datei-Format** (in `src/logging_config.py`, Zeile 93):

```python
file_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
```

**Console-Format** (Zeile 106):

```python
console_formatter = ColoredFormatter(
    '%(asctime)s | %(levelname_colored)s | %(name)-15s | %(message)s',
    datefmt='%H:%M:%S'
)
```

## 📊 Log-Level Bedeutung

### DEBUG (Detailliert)
- Alle API-Requests mit vollständigem Payload
- Tool-Parameter und Ergebnisse
- Datei-Pfade und Dateigrößen
- Ollama-Requests und -Responses (gekürzt)
- Regex-Pattern-Matching

**Beispiel**:
```
2025-11-16 03:09:27 | DEBUG | LocalAgent-Pro.Tools | read_file | 🔍 Prüfe Existenz: /home/sandbox/test.txt
2025-11-16 03:09:27 | DEBUG | LocalAgent-Pro.Tools | read_file | 📊 Dateigröße: 1234 bytes
```

### INFO (Standard)
- Server-Start und -Konfiguration
- Erfolgreiche API-Requests
- Tool-Aufrufe (welches Tool, Ergebnis)
- Ollama-Calls (Modell, Token-Anzahl, Dauer)

**Beispiel**:
```
2025-11-16 03:09:27 | INFO | LocalAgent-Pro.API | chat_completions | ✅ Chat Completion erfolgreich [a1b2c3d4]: prompt_tokens=45, completion_tokens=123
```

### WARNING (Warnungen)
- Blockierte Domains (Whitelist)
- Nicht gefundene Dateien
- Shell-Kommandos im Sandbox-Modus
- Timeouts (aber erfolgreich recovered)

**Beispiel**:
```
2025-11-16 03:09:27 | WARNING | LocalAgent-Pro.Tools | fetch | 🚫 Domain blockiert: evil.com (nicht in Whitelist)
```

### ERROR (Fehler)
- API-Request-Fehler
- Tool-Execution-Fehler
- Ollama-Connection-Fehler
- Datei-I/O-Fehler

**Beispiel**:
```
2025-11-16 03:09:27 | ERROR | LocalAgent-Pro.API | chat_completions | ❌ Chat Completion Fehler [xyz123]: 'NoneType' object has no attribute 'get'
```

### CRITICAL (Kritisch)
- Server kann nicht starten
- Config-Datei fehlt
- Kritische Systemfehler

## 🛠️ Detailliertes Logging pro Komponente

### 1. API-Request-Logging

**Was wird geloggt**:
- HTTP-Methode und Endpoint
- Request-Payload (gekürzt auf 500 Zeichen)
- User-Prompt (gekürzt auf 200 Zeichen)
- Response-Status
- Token-Anzahl (Prompt + Completion)
- Request-ID für Tracking

**Beispiel-Logs**:
```
INFO  | LocalAgent-Pro.API | 📨 Chat Completion Request [a1b2c3d4] empfangen
DEBUG | LocalAgent-Pro.API | 📦 Request Data [a1b2c3d4]: {'messages': [{'role': 'user', 'content': 'Lies Datei test.txt'}], ...
DEBUG | LocalAgent-Pro.API | 💬 Anzahl Messages: 1, Modell: localagent-pro
INFO  | LocalAgent-Pro.API | 👤 User Prompt [a1b2c3d4]: Lies Datei test.txt
DEBUG | LocalAgent-Pro.API | 🔍 Analysiere Prompt für Tool-Erkennung [a1b2c3d4]
INFO  | LocalAgent-Pro.API | ✅ Chat Completion erfolgreich [a1b2c3d4]: prompt_tokens=3, completion_tokens=50
```

### 2. Tool-Execution-Logging

**Tool: read_file**
```
INFO  | LocalAgent-Pro.Tools | 📖 Tool 'read_file' aufgerufen: path=test.txt
DEBUG | LocalAgent-Pro.Tools | 🔍 Prüfe Existenz: /home/sandbox/test.txt
DEBUG | LocalAgent-Pro.Tools | 📊 Dateigröße: 1234 bytes
INFO  | LocalAgent-Pro.Tools | ✅ Datei erfolgreich gelesen: /home/sandbox/test.txt (1234 Zeichen)
DEBUG | LocalAgent-Pro.Tools | 📄 Content-Vorschau: Hello World...
```

**Tool: write_file**
```
INFO  | LocalAgent-Pro.Tools | ✏️ Tool 'write_file' aufgerufen: path=output.txt, content_length=100
DEBUG | LocalAgent-Pro.Tools | 📝 Schreibe nach: /home/sandbox/output.txt
DEBUG | LocalAgent-Pro.Tools | 📄 Content-Vorschau: This is a test file...
INFO  | LocalAgent-Pro.Tools | ✅ Datei erfolgreich geschrieben: /home/sandbox/output.txt (100 Zeichen)
```

**Tool: list_files**
```
INFO  | LocalAgent-Pro.Tools | 📂 Tool 'list_files' aufgerufen: path=.
DEBUG | LocalAgent-Pro.Tools | 🔍 Liste Verzeichnis: /home/sandbox
INFO  | LocalAgent-Pro.Tools | ✅ Verzeichnis aufgelistet: /home/sandbox (12 Dateien, 3 Ordner, 45678 bytes)
```

**Tool: fetch**
```
INFO  | LocalAgent-Pro.Tools | 🌐 Tool 'fetch' aufgerufen: url=github.com
DEBUG | LocalAgent-Pro.Tools | 🔧 URL ergänzt zu: https://github.com
DEBUG | LocalAgent-Pro.Tools | 🔍 Extrahierte Domain: github.com
DEBUG | LocalAgent-Pro.Tools | ✅ Domain erlaubt: github.com
DEBUG | LocalAgent-Pro.Tools | 📡 Sende HTTP GET Request an: https://github.com
INFO  | LocalAgent-Pro.Tools | ✅ Web-Request erfolgreich: https://github.com (Status: 200, Größe: 123456 Zeichen)
DEBUG | LocalAgent-Pro.Tools | 📊 Response Headers: {'Content-Type': 'text/html', ...}
```

**Tool: run_shell**
```
INFO  | LocalAgent-Pro.Tools | 💻 Tool 'run_shell' aufgerufen: cmd=ls -la
WARNING | LocalAgent-Pro.Tools | 🚫 Shell-Kommando blockiert (Sandbox-Modus aktiv)
```

### 3. Ollama-Integration-Logging

**Generate Request**:
```
INFO  | LocalAgent-Pro.Ollama | 🧠 Generate Request [12345678] gestartet
INFO  | LocalAgent-Pro.Ollama | 📝 Model: llama3.1, Temperature: 0.7
DEBUG | LocalAgent-Pro.Ollama | 👤 Prompt [12345678]: Was ist Python? Antworte in einem Satz.
DEBUG | LocalAgent-Pro.Ollama | 📦 Payload [12345678]: {'model': 'llama3.1', 'prompt': '...', ...}
DEBUG | LocalAgent-Pro.Ollama | 📡 POST http://127.0.0.1:11434/api/generate
DEBUG | LocalAgent-Pro.Ollama | 📊 Response Status [12345678]: 200
INFO  | LocalAgent-Pro.Ollama | ✅ Generate erfolgreich [12345678]: 45 tokens in 2.34s (19.2 tokens/s)
DEBUG | LocalAgent-Pro.Ollama | 📊 Details [12345678]: load=0.12s, prompt_tokens=12, response_tokens=45, total=2.34s
DEBUG | LocalAgent-Pro.Ollama | 💬 Response [12345678]: Python ist eine vielseitige Programmiersprache...
```

**Chat Request**:
```
INFO  | LocalAgent-Pro.Ollama | 💬 Chat Request [87654321] gestartet
INFO  | LocalAgent-Pro.Ollama | 📝 Model: llama3.1, Messages: 2, Temperature: 0.7
DEBUG | LocalAgent-Pro.Ollama | 💬 Message 1 [87654321] (system): Du bist ein hilfreicher Assistent.
DEBUG | LocalAgent-Pro.Ollama | 💬 Message 2 [87654321] (user): Erkläre Docker in einem Satz.
DEBUG | LocalAgent-Pro.Ollama | 📦 Payload [87654321]: {'model': 'llama3.1', 'messages': [...], ...}
DEBUG | LocalAgent-Pro.Ollama | 📡 POST http://127.0.0.1:11434/api/chat
INFO  | LocalAgent-Pro.Ollama | ✅ Chat erfolgreich [87654321]: 52 tokens in 3.12s (16.7 tokens/s)
```

## 🔍 Troubleshooting mit Logs

### Problem: Server startet nicht

**Log-Datei prüfen**:
```bash
cat logs/localagent-pro.log | grep CRITICAL
```

**Häufige Fehler**:
```
CRITICAL | root | ❌ Config nicht gefunden: /path/to/config.yaml
CRITICAL | root | ❌ Fehler beim Laden der Config: ...
```

**Lösung**: Config-Datei erstellen oder Pfad korrigieren

### Problem: Tool wird nicht erkannt

**Log-Filter**:
```bash
grep "Tool-Erkennung" logs/localagent-pro.log | tail -20
```

**Was zu suchen**:
- Wurde der Prompt geloggt?
- Welche Regex-Pattern haben matched?
- Welches Tool wurde aufgerufen?

**Debug aktivieren**:
```python
# In openwebui_agent_server.py, Zeile 23
log_level="DEBUG"  # Statt INFO
```

### Problem: Ollama antwortet nicht

**Ollama-Logs prüfen**:
```bash
# Systemd-Service
journalctl -u ollama -f

# Oder: LocalAgent-Logs
grep "Ollama" logs/ollama_integration.log | tail -20
```

**Häufige Fehler**:
```
ERROR | LocalAgent-Pro.Ollama | ❌ Keine Verbindung zu Ollama auf http://127.0.0.1:11434
ERROR | LocalAgent-Pro.Ollama | ⏰ Generate Timeout [xyz] (>60s)
```

**Lösungen**:
1. Ollama-Service starten: `systemctl start ollama`
2. Timeout erhöhen in `ollama_integration.py`
3. Modell herunterladen: `ollama pull llama3.1`

### Problem: Langsame Performance

**Performance-Logs analysieren**:
```bash
./analyze_logs.sh
```

**Prüfen**:
- Wie viele DEBUG-Logs werden geschrieben?
- Wie groß sind die Log-Dateien?
- Gibt es viele ERROR-Logs (Overhead)?

**Optimierungen**:
1. Log-Level auf INFO setzen (Production)
2. Console-Output deaktivieren
3. Rotating File Handler nutzen (bereits aktiv)

## 📋 Systemd-Service mit Logging

### Service-Datei erstellen

```bash
sudo nano /etc/systemd/system/localagent-pro.service
```

**Inhalt**:
```ini
[Unit]
Description=LocalAgent-Pro Backend Server
After=network-online.target ollama.service

[Service]
Type=simple
User=danijel-jd
WorkingDirectory=/home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro
ExecStart=/usr/bin/python3 /home/danijel-jd/Dokumente/Workspace/Projekte/Lokales Agententool/LocalAgent-Pro/src/openwebui_agent_server.py
Restart=always
RestartSec=3

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=localagent-pro

[Install]
WantedBy=multi-user.target
```

### Service aktivieren

```bash
sudo systemctl daemon-reload
sudo systemctl enable localagent-pro
sudo systemctl start localagent-pro
```

### Logs ansehen

```bash
# Live-Logs
journalctl -u localagent-pro -f

# Logs seit heute
journalctl -u localagent-pro --since today

# Letzte 100 Zeilen
journalctl -u localagent-pro -n 100

# Nur ERROR-Logs
journalctl -u localagent-pro -p err
```

## 🔐 Sicherheit & Datenschutz

### Sensible Daten maskieren

**Automatisch maskiert**:
- Passwörter (`password`, `passwd`)
- API-Keys (`api_key`, `apikey`)
- Tokens (`token`, `access_token`)
- Secrets (`secret`)

**Beispiel**:
```python
# Vor Logging:
"password: secret123, api_key: abc-def-ghi"

# Nach Maskierung:
"password: ***MASKED***, api_key: ***MASKED***"
```

### Eigene Maskierungs-Patterns

**In `logging_config.py`**:
```python
# Zeile 311-318 erweitern:
patterns = [
    (r'password["\s:=]+([^"\s,]+)', 'password: ***MASKED***'),
    (r'api[_-]?key["\s:=]+([^"\s,]+)', 'api_key: ***MASKED***'),
    (r'token["\s:=]+([^"\s,]+)', 'token: ***MASKED***'),
    (r'secret["\s:=]+([^"\s,]+)', 'secret: ***MASKED***'),
    # Eigene Pattern hier hinzufügen:
    (r'email["\s:=]+([^"\s,]+)', 'email: ***MASKED***'),
]
```

### Log-Dateien schützen

```bash
# Nur Owner kann lesen
chmod 600 logs/*.log

# Log-Verzeichnis schützen
chmod 700 logs/
```

## 📈 Performance-Optimierung

### 1. Log-Level anpassen

**Development**:
```python
log_level="DEBUG"  # Alle Details
```

**Production**:
```python
log_level="INFO"   # Nur wichtige Events
```

**High-Load Production**:
```python
log_level="WARNING"  # Nur Warnungen und Fehler
```

### 2. Content-Kürzung konfigurieren

**In `logging_config.py`**, Funktion `truncate_long_content`:

```python
# Zeile 336-348: max_length anpassen
def truncate_long_content(content: str, max_length: int = 1000) -> str:
    # Für Production: max_length = 200
    # Für Debugging: max_length = 5000
```

### 3. Rotation-Settings

**Mehr Speicher, weniger I/O**:
```python
# Zeile 24-25 in logging_config.py
max_file_size: int = 50 * 1024 * 1024,  # 50 MB
backup_count: int = 10
```

**Weniger Speicher, mehr Rotation**:
```python
max_file_size: int = 5 * 1024 * 1024,   # 5 MB
backup_count: int = 3
```

## 🧪 Testing

### Logging-Modul testen

```bash
# Standalone-Test
python3 src/logging_config.py

# Ollama-Integration testen
python3 src/ollama_integration.py
```

### Vollständiger Server-Test mit Logging

```bash
# Server starten
python3 src/openwebui_agent_server.py &
SERVER_PID=$!

# Logs live verfolgen (in neuem Terminal)
./tail_logs.sh

# API testen
curl http://127.0.0.1:8001/health
curl -X POST http://127.0.0.1:8001/test -H "Content-Type: application/json" -d '{"prompt":"Liste alle Dateien auf"}'

# Server stoppen
kill $SERVER_PID
```

## 📚 Weiterführende Ressourcen

- **Python Logging Docs**: https://docs.python.org/3/library/logging.html
- **Log-Rotation**: https://docs.python.org/3/library/logging.handlers.html#rotatingfilehandler
- **Systemd Logging**: `man journalctl`

## 🆘 Häufige Fragen (FAQ)

### Q: Logs werden nicht erstellt?

**A**: Prüfe Berechtigungen:
```bash
mkdir -p logs
chmod 755 logs
```

### Q: Zu viele Logs, Festplatte voll?

**A**: Nutze Cleanup-Skript:
```bash
./cleanup_logs.sh
# Wähle Option [4] für Archivierung
```

### Q: Logs in Datei UND Console?

**A**: In `openwebui_agent_server.py`:
```python
console_output=True  # Zeile 24
```

### Q: Nur ERROR-Logs anzeigen?

**A**: Mit grep filtern:
```bash
grep " ERROR \| CRITICAL " logs/localagent-pro.log
```

### Q: Logs nach Zeitraum filtern?

**A**: Mit grep und Zeitstempel:
```bash
# Heute zwischen 10:00 und 11:00
grep "2025-11-16 10:" logs/localagent-pro.log
```

---

**✅ Logging-System erfolgreich implementiert!**

Für weitere Hilfe: Siehe `README.md` oder erstelle ein Issue auf GitHub.
