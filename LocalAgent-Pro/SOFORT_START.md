# 🚀 LocalAgent-Pro - Sofort-Start-Anleitung für VSCode Copilot

## ✅ Was ist fertig

- ✅ Backend-API läuft auf Port 8001
- ✅ OpenWebUI UI läuft auf Port 3000
- ✅ Alle Endpoints funktionieren (Health, Models, Chat, Test)
- ✅ Sandbox-Modus aktiv
- ✅ 2 Modelle verfügbar: `localagent-pro` und `llama3.1`

## 📋 Für VSCode Copilot (Copy & Paste)

Öffne in VSCode: `Ctrl+Shift+P` → "Copilot: Edit Custom Instructions" → Füge ein:

```text
Du arbeitest mit LocalAgent-Pro. Backend-API: http://127.0.0.1:8001/v1

ENDPUNKTE:
- GET  http://127.0.0.1:8001/health
- GET  http://127.0.0.1:8001/v1/models
- POST http://127.0.0.1:8001/v1/chat/completions
- POST http://127.0.0.1:8001/test

WICHTIG:
- Port 8001 = Backend-API (für Copilot)
- Port 3000 = OpenWebUI UI (nur Browser)
- Nutze IMMER Port 8001 für API-Calls
- Sandbox aktiv: /home/danijel-jd/localagent_sandbox
- Erlaubte Domains: example.com, github.com, ubuntu.com, archlinux.org

TOOLS (natürliche Sprache):
- "Lies Datei config.yaml"
- "Schreibe 'Hello' in test.txt"
- "Liste Verzeichnis workspace auf"
- "Führe 'ls -la' aus"
- "Hole Webseite github.com"

FEHLERVERMEIDUNG:
❌ FALSCH: http://127.0.0.1:3000/v1/... (UI-Port)
✅ RICHTIG: http://127.0.0.1:8001/v1/... (API-Port)
```

## 🧪 Schnelltest

```bash
./openwebui_test.sh
```

## 🔧 OpenWebUI verbinden

1. Öffne im Browser: http://127.0.0.1:3000
2. Gehe zu: **Einstellungen** → **Connections** → **OpenAI API**
3. Setze:
   - **API Base URL:** `http://127.0.0.1:8001/v1`
   - **API Key:** `dummy` (beliebig)
4. Teste: "Liste Dateien im Workspace auf"

## 📁 Dateien-Übersicht

```
LocalAgent-Pro/
├── openwebui_test.sh           # ✅ Vollständiger API-Test
├── COPILOT_SYSTEM_PROMPT.md    # ✅ Ausführlicher Copilot-Prompt
├── SOFORT_START.md             # ✅ Diese Datei (Kurzversion)
├── start_server.sh             # Server starten
├── stop_server.sh              # Server stoppen
├── health_check.sh             # Health prüfen
└── src/
    └── openwebui_agent_server.py  # Haupt-Server
```

## 🐛 Troubleshooting

**Server läuft nicht?**
```bash
./start_server.sh
```

**Testen, ob alles funktioniert?**
```bash
./openwebui_test.sh
```

**Server stoppen?**
```bash
./stop_server.sh
```

**Logs ansehen?**
```bash
tail -f server.log
```

## 🎯 Beispiel-Anfragen für OpenWebUI

Nach der Verbindung kannst du testen:

1. "Liste alle Dateien im Workspace auf"
2. "Lies die Datei config.yaml"
3. "Erstelle eine Datei test.txt mit 'Hello World'"
4. "Zeige mir den Inhalt von README.md"
5. "Hole die Webseite github.com"

## ⚡ Wichtigste Befehle

| Befehl | Zweck |
|--------|-------|
| `./openwebui_test.sh` | Alle Endpoints testen |
| `./start_server.sh` | Server starten |
| `./stop_server.sh` | Server stoppen |
| `curl -s http://127.0.0.1:8001/health` | Health prüfen |
| `tail -f server.log` | Logs live ansehen |

---

**Alles läuft? Dann verbinde jetzt OpenWebUI und teste die Tools!** 🚀
