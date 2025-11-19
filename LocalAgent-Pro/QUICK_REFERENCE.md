# LocalAgent-Pro - Quick Reference

## 🚀 Schnellstart

### Server starten
```bash
./start_server.sh
```

### Server stoppen
```bash
./stop_server.sh
```

### Health-Check
```bash
./health_check.sh
```

## 📍 Wichtige URLs

- **Server**: http://127.0.0.1:8001
- **API Base**: http://127.0.0.1:8001/v1
- **Health**: http://127.0.0.1:8001/health
- **OpenWebUI**: http://localhost:3000

## 🔧 OpenWebUI Konfiguration

**Settings → Connections → Add OpenAI API**

```
Base URL: http://127.0.0.1:8001/v1
API Key: dummy
Model: localagent-pro
```

## 🧪 Test-Prompts

### 1. Datei-Operationen
- "Liste alle Dateien im workspace Verzeichnis auf"
- "Erstelle Datei test.txt mit 'Hello LocalAgent-Pro'"
- "Lies den Inhalt von test.txt"

### 2. Shell-Kommandos (Live-Modus)
- "Führe 'ls -la' aus"
- "Zeige aktuelles Verzeichnis"

### 3. Web-Requests
- "Lade die Webseite example.com"
- "Hole github.com und zeige die ersten 500 Zeichen"

## 📊 Verfügbare Tools

| Tool | Beschreibung | Beispiel |
|------|--------------|----------|
| `read_file` | Datei lesen | "Lies config.yaml" |
| `write_file` | Datei schreiben (Sandbox) | "Erstelle test.py mit Code" |
| `list_files` | Verzeichnis auflisten | "Liste workspace auf" |
| `run_shell` | Shell-Kommando | "Führe 'pwd' aus" |
| `fetch` | Webseite laden | "Lade example.com" |

## 🔒 Sicherheit

- ✅ Sandbox aktiv: `/home/danijel-jd/localagent_sandbox`
- ✅ Domain-Whitelist: 4 Domains erlaubt
- ✅ Shell-Protection: Gefährliche Kommandos blockiert

## 🚨 Troubleshooting

### Server läuft nicht
```bash
ps aux | grep openwebui_agent_server
./start_server.sh
```

### Port blockiert
```bash
lsof -i :8001
pkill -f openwebui_agent_server
```

### Logs prüfen
```bash
tail -f server.log
```

## 📁 Dateistruktur

```
LocalAgent-Pro/
├── src/
│   └── openwebui_agent_server.py  # Haupt-Server
├── config/
│   └── config.yaml                # Konfiguration
├── venv/                          # Virtual Environment
├── server.log                     # Server-Logs
├── start_server.sh               # Server starten
├── stop_server.sh                # Server stoppen
├── health_check.sh               # Vollständiger Test
├── OPENWEBUI_INTEGRATION.md      # Detaillierte Anleitung
└── QUICK_REFERENCE.md            # Diese Datei
```

## ✅ Status-Check

Führe `./health_check.sh` aus um zu prüfen:
- ✓ Port 8001 lauscht
- ✓ Health-Endpoint funktioniert
- ✓ Models-Endpoint funktioniert
- ✓ Chat-API funktioniert
- ✓ Tool-Test funktioniert
