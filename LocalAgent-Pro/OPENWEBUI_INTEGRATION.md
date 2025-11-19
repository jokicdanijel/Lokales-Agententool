# 🚀 OpenWebUI Integration - LocalAgent-Pro

## ✅ Aktueller Status

- **Modell**: llama3.1
- **Sandbox**: ✅ Aktiv
- **Sandbox-Pfad**: `/home/danijel-jd/localagent_sandbox`
- **Erlaubte Domains**: 4 (example.com, github.com, ubuntu.com, archlinux.org)
- **Server Port**: 8001
- **OpenWebUI API Base URL**: `http://127.0.0.1:8001/v1`

---

## 🚦 Schnellstart (3 Schritte)

### 1️⃣ Server starten
```bash
./start_server.sh
```

### 2️⃣ Server testen
```bash
./health_check.sh
```

### 3️⃣ OpenWebUI verbinden
1. Öffne: `http://localhost:3000`
2. **Settings → Connections → OpenAI API**
3. **API Base URL**: `http://127.0.0.1:8001/v1`
4. **API Key**: `dummy`
5. **Save & Test**

✅ **Fertig! Du kannst jetzt Tools in OpenWebUI nutzen!**

---

## 📋 Verfügbare Skripte

| Skript | Zweck |
|--------|-------|
| `./start_server.sh` | Server im Hintergrund starten |
| `./stop_server.sh` | Server stoppen |
| `./health_check.sh` | Alle APIs testen |

---

## 🧪 Manuelle API-Tests

### Health Check
```bash
curl -s http://127.0.0.1:8001/health | jq
```

### Models
```bash
curl -s http://127.0.0.1:8001/v1/models | jq
```

### Chat
```bash
curl -s -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"Hallo!"}]}' | jq
```

### Tool-Test
```bash
curl -s -X POST http://127.0.0.1:8001/test \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Liste Verzeichnis . auf"}' | jq
```

---

## 🛠️ Verfügbare Tools

### 📄 read_file
```
"Lies Datei config.yaml"
"Zeige Inhalt von test.txt"
```

### ✏️ write_file
```
"Erstelle Datei hello.py mit 'print(\"Hello\")'"
```

### 📁 list_files
```
"Liste Verzeichnis workspace auf"
```

### 💻 run_shell (nur Live-Modus)
```
"Führe Kommando 'ls -la' aus"
```

### 🌐 fetch
```
"Lade Webseite example.com"
```

---

## 🔧 Troubleshooting

### Server startet nicht
```bash
# Port belegt?
ss -tlnp | grep 8001

# Dependencies ok?
source venv/bin/activate
pip list | grep -E "flask|pyyaml"
```

### OpenWebUI verbindet nicht
```bash
# 1. Server läuft?
./health_check.sh

# 2. Logs prüfen
tail -f server.log

# 3. Direkt testen
curl http://127.0.0.1:8001/health
```

---

## 🛡️ Sicherheit

- ✅ **Sandbox aktiv** - Alle Dateien in `/home/danijel-jd/localagent_sandbox`
- ✅ **Domain-Whitelist** - Nur 4 erlaubte Domains
- ✅ **Shell-Kommandos deaktiviert** (Sandbox-Modus)

### Sandbox deaktivieren (Live-Modus)
```yaml
# config/config.yaml
sandbox: false
```
⚠️ **Vorsicht**: Voller Dateisystem- und Shell-Zugriff!

---

## 📦 Projekt-Struktur

```
LocalAgent-Pro/
├── start_server.sh          # Server starten
├── stop_server.sh           # Server stoppen  
├── health_check.sh          # API-Tests
├── server.log               # Server-Output
├── OPENWEBUI_INTEGRATION.md # Diese Datei
├── config/
│   └── config.yaml          # Konfiguration
└── src/
    └── openwebui_agent_server.py
```

---

## ✅ Integration-Checkliste

- [ ] Server gestartet
- [ ] Health-Check erfolgreich
- [ ] OpenWebUI konfiguriert (`http://127.0.0.1:8001/v1`)
- [ ] Test-Message gesendet
- [ ] Tool-Execution getestet

---

## 💡 VSCode Integration

### Tasks hinzufügen (`.vscode/tasks.json`):
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start LocalAgent",
      "type": "shell",
      "command": "${workspaceFolder}/start_server.sh"
    },
    {
      "label": "Health Check",
      "type": "shell",
      "command": "${workspaceFolder}/health_check.sh"
    }
  ]
}
```

Dann: **Terminal → Run Task → Start LocalAgent**

---

**🎉 Viel Erfolg mit LocalAgent-Pro + OpenWebUI!**
