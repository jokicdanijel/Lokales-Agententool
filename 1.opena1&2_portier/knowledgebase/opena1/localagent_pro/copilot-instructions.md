# LocalAgent-Pro - GitHub Copilot Instructions

## Repository-Übersicht

**LocalAgent-Pro** ist ein lokaler KI-Agent mit OpenAI-kompatibler API, der natürliche Sprache in Tool-Aufrufe übersetzt.

### Tech-Stack
- **Backend:** Python 3.12+, Flask 3.1.2, PyYAML 6.0.3
- **API:** OpenAI-kompatibel auf Port 8001
- **Frontend:** OpenWebUI auf Port 3000
- **Sandbox:** Aktiv unter `/home/danijel-jd/localagent_sandbox`
- **Modell:** llama3.1, localagent-pro

## Repository-Struktur

```
LocalAgent-Pro/
├── src/
│   ├── openwebui_agent_server.py    # Haupt-Server (Flask)
│   └── agent_server.py              # Alternative mit OpenAI SDK
├── config/
│   └── config.yaml                  # Zentrale Konfiguration
├── .github/
│   └── copilot-instructions.md      # Diese Datei
├── venv/                            # Python Virtual Environment
├── Scripts/
│   ├── start_server.sh             # Server starten (nohup)
│   ├── stop_server.sh              # Server stoppen
│   ├── health_check.sh             # API-Tests
│   ├── openwebui_test.sh           # Vollständiger Systemtest
│   ├── openwebui_check.sh          # Schneller OpenWebUI-Check
│   └── chat-local.sh               # CLI Chat Interface
└── Docs/
    ├── SOFORT_START.md             # Schnellstart
    ├── COMPLETE_GUIDE.md           # Vollständige Dokumentation
    └── COPILOT_SYSTEM_PROMPT.md    # Ausführlicher Prompt
```

## Schnellstart für KI-Agenten

### 1. Repository-Scan
```bash
# Manifestdateien finden
find . -name "requirements.txt" -o -name "config.yaml" -o -name "package.json"

# Server-Status prüfen
./openwebui_test.sh
```

### 2. Server starten/stoppen
```bash
# Starten (im Hintergrund)
./start_server.sh

# Status prüfen
curl -s http://127.0.0.1:8001/health | python3 -m json.tool

# Stoppen
./stop_server.sh
```

### 3. API-Endpunkte testen
```bash
# Health
curl http://127.0.0.1:8001/health

# Modelle
curl http://127.0.0.1:8001/v1/models

# Chat
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Liste Dateien auf"}]}'
```

## API-Konfiguration

### Backend-API (Port 8001)
- **Base URL:** `http://127.0.0.1:8001/v1`
- **Health:** `GET /health`
- **Models:** `GET /v1/models`
- **Chat:** `POST /v1/chat/completions`
- **Test:** `POST /test`

### OpenWebUI (Port 3000)
- **UI:** `http://127.0.0.1:3000`
- **API Base URL:** `http://127.0.0.1:8001/v1`
- **API Key:** `dummy` (beliebig)

## Wichtige Regeln für Code-Änderungen

### ✅ DO
- Port 8001 für alle Backend-API-Aufrufe nutzen
- Natürliche Sprache für Tool-Aufrufe verwenden
- Health-Endpoint vor anderen Tests prüfen
- Sandbox-Pfade für Datei-Operationen verwenden
- Virtual Environment aktivieren: `source venv/bin/activate`

### ❌ DON'T
- Port 3000 für API-Aufrufe nutzen (nur UI)
- `/v1` allein aufrufen (404)
- Dateien außerhalb der Sandbox erstellen (wenn Sandbox aktiv)
- OpenAI SDK in `openwebui_agent_server.py` verwenden (SDK-frei)

## Verfügbare Tools

LocalAgent-Pro erkennt automatisch folgende natürlichsprachliche Befehle:

| Tool | Beispiel-Prompt | Python-Funktion |
|------|-----------------|-----------------|
| **Datei lesen** | "Lies Datei config.yaml" | `read_file()` |
| **Datei schreiben** | "Erstelle test.txt mit 'Hello'" | `write_file()` |
| **Verzeichnis** | "Liste Verzeichnis workspace auf" | `list_files()` |
| **Shell** | "Führe 'ls -la' aus" | `run_shell()` |
| **Web** | "Hole Webseite github.com" | `fetch()` |

## Development-Workflows

### Neues Feature hinzufügen
1. **Backup erstellen:** `cp src/openwebui_agent_server.py src/openwebui_agent_server.py.bak`
2. **Virtual Env aktivieren:** `source venv/bin/activate`
3. **Code ändern:** In `src/openwebui_agent_server.py`
4. **Server neu starten:** `./stop_server.sh && ./start_server.sh`
5. **Testen:** `./openwebui_test.sh`
6. **Logging prüfen:** `tail -f server.log`

### Neue Abhängigkeit hinzufügen
```bash
source venv/bin/activate
pip install <package>
pip freeze > requirements.txt
```

### Neuen Endpoint hinzufügen
```python
# In src/openwebui_agent_server.py
@app.route('/new_endpoint', methods=['POST'])
def new_endpoint():
    data = request.json
    # Implementierung
    return jsonify({"result": "..."})
```

## Sandbox-Sicherheit

- **Sandbox AKTIV:** `true` (siehe `config/config.yaml`)
- **Sandbox-Pfad:** `/home/danijel-jd/localagent_sandbox`
- **Erlaubte Domains:** `example.com`, `github.com`, `ubuntu.com`, `archlinux.org`
- **Alle Dateipfade** werden automatisch in Sandbox umgewandelt

## Integration Points

### 1. CLI Chat Interface
```bash
./chat-local.sh "Was kannst du alles machen?"
./chat-local.sh "Liste alle Dateien auf"
./chat-local.sh "Erstelle Datei test.txt mit 'Hallo Welt'"
```

### 2. OpenWebUI Verbindung
1. Browser: http://127.0.0.1:3000
2. Einstellungen → Connections → OpenAI API
3. API Base URL: `http://127.0.0.1:8001/v1`
4. API Key: `dummy`

### 3. Programmatische Nutzung
```python
import requests

response = requests.post(
    "http://127.0.0.1:8001/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Liste Dateien auf"}
        ]
    }
)
print(response.json()["choices"][0]["message"]["content"])
```

## Testing & Debugging

### Vollständiger Systemtest
```bash
./openwebui_test.sh
```
**Testet:** Health, Models, Chat, Test-Endpoint, OpenWebUI UI

### Einzelne Tests
```bash
# Health
curl -s http://127.0.0.1:8001/health | python3 -m json.tool

# Models
curl -s http://127.0.0.1:8001/v1/models | python3 -m json.tool

# Chat
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hallo"}]}' \
  http://127.0.0.1:8001/v1/chat/completions | python3 -m json.tool
```

### Logs analysieren
```bash
# Live-Logs
tail -f server.log

# Letzte 50 Zeilen
tail -n 50 server.log

# Nach Fehlern suchen
grep -i error server.log
```

## Patterns & Anti-Patterns

### ✅ Patterns
- **Self-contained Server:** Kein externes SDK, alles in einer Datei
- **Natürliche Sprache:** Regex-basierte Erkennung von User-Intent
- **OpenAI-kompatibel:** Standard-Response-Format für breite Kompatibilität
- **Sandbox-first:** Alle Datei-Ops werden automatisch in Sandbox ausgeführt

### ❌ Anti-Patterns zu vermeiden
- OpenAI SDK in `openwebui_agent_server.py` verwenden (bleibt SDK-frei)
- Hardcoded Pfade außerhalb der Sandbox
- Destruktive Operationen ohne Sandbox-Check
- Port 3000 für Backend-API nutzen

## Commit-Konventionen

```
feat: Neues Feature hinzufügen
fix: Bug beheben
docs: Dokumentation aktualisieren
test: Tests hinzufügen
refactor: Code umstrukturieren
```

**Beispiele:**
```
feat: Add file deletion endpoint
fix: Correct regex pattern for file read commands
docs: Update API documentation in COMPLETE_GUIDE.md
test: Add integration tests for chat endpoint
```

## Nützliche Befehle für Agenten

### Repository-Analyse
```bash
# Alle Python-Dateien finden
find . -name "*.py" -type f

# Alle Konfigurationsdateien
find . -name "*.yaml" -o -name "*.yml" -o -name "*.json"

# Alle ausführbaren Skripte
find . -name "*.sh" -type f -executable
```

### Server-Management
```bash
# Status prüfen
ps aux | grep openwebui_agent_server

# Port-Nutzung
ss -ltnp | grep 8001

# Prozess beenden
pkill -f openwebui_agent_server
```

### Virtual Environment
```bash
# Aktivieren
source venv/bin/activate

# Deaktivieren
deactivate

# Pakete auflisten
pip list

# Requirements exportieren
pip freeze > requirements.txt
```

## Beispiele für präzise Agent-Prompts

1. **"Finde alle API-Endpunkte und dokumentiere ihre HTTP-Methoden"**
2. **"Starte den Server lokal und teste alle Endpunkte mit curl"**
3. **"Füge einen DELETE-Endpoint für Dateien hinzu, teste ihn und dokumentiere"**
4. **"Analysiere die Tool-Erkennung in analyze_and_execute() und verbessere Regex-Patterns"**
5. **"Erstelle einen neuen Health-Check der auch OpenWebUI-Verbindung prüft"**

## Häufige Aufgaben

### Server neu starten
```bash
./stop_server.sh && sleep 2 && ./start_server.sh
```

### Alle Tests durchführen
```bash
./openwebui_test.sh && echo "✅ Alle Tests bestanden"
```

### Konfiguration ändern
```bash
nano config/config.yaml
# Dann Server neu starten
./stop_server.sh && ./start_server.sh
```

### Logs in Echtzeit verfolgen
```bash
tail -f server.log | grep -v "GET /health"  # Health-Checks ausblenden
```

---

**Bei Fragen oder fehlenden Informationen:** Konsultiere `COMPLETE_GUIDE.md` oder frage den Repository-Besitzer nach spezifischen Anforderungen.
