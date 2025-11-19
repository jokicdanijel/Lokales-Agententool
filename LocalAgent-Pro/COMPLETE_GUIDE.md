# 🚀 LocalAgent-Pro + OpenWebUI - Komplett-Paket

## ✅ Was ist bereit?

- ✅ Backend API läuft auf Port **8001**
- ✅ OpenWebUI UI läuft auf Port **3000**
- ✅ Alle Endpoints funktionieren
- ✅ Sandbox-Modus aktiv
- ✅ 5 Tools einsatzbereit

---

## 🎯 3-Schritte-Start

### 1. Server starten
```bash
cd LocalAgent-Pro
./start_server.sh
```

### 2. Alles testen
```bash
./openwebui_check.sh
```

### 3. OpenWebUI verbinden
1. Öffne: **http://localhost:3000**
2. **Settings → Connections → OpenAI API**
3. Trage ein:
   - **API Base URL**: `http://127.0.0.1:8001/v1`
   - **API Key**: `dummy`
4. **Save & Test Connection**

✅ **Fertig! Du kannst jetzt loslegen!**

---

## 📁 Alle verfügbaren Skripte

| Skript | Beschreibung |
|--------|--------------|
| `./start_server.sh` | Server im Hintergrund starten |
| `./stop_server.sh` | Server stoppen |
| `./health_check.sh` | Detaillierter API-Test |
| `./openwebui_check.sh` | Schneller OpenWebUI-Check |

---

## 🔧 Wichtige URLs

| Service | URL | Port |
|---------|-----|------|
| Backend API | `http://127.0.0.1:8001/v1` | 8001 |
| OpenWebUI UI | `http://localhost:3000` | 3000 |
| Browser Interface | `http://127.0.0.1:8001` | 8001 |

---

## 🧪 Test-Prompts für OpenWebUI

Nach der Verbindung teste diese Prompts:

```
"Liste Verzeichnis workspace auf"
```

```
"Erstelle Datei test.txt mit 'Hello from OpenWebUI!'"
```

```
"Lies Datei config.yaml"
```

```
"Lade Webseite example.com"
```

---

## 🛠️ Verfügbare Tools

### 1. 📄 read_file
Liest Dateien aus der Sandbox
```
"Lies Datei config.yaml"
"Zeige Inhalt von test.txt"
```

### 2. ✏️ write_file
Erstellt Dateien in der Sandbox
```
"Erstelle Datei hello.py mit 'print(\"Hello\")'"
"Schreibe Datei notes.txt mit 'Wichtige Notizen'"
```

### 3. 📁 list_files
Listet Verzeichnisse auf
```
"Liste Verzeichnis . auf"
"Zeige Ordner workspace"
```

### 4. 💻 run_shell
Shell-Kommandos (nur Live-Modus)
```
"Führe Kommando 'ls -la' aus"
```
⚠️ Im Sandbox-Modus deaktiviert!

### 5. 🌐 fetch
Lädt Webseiten (nur erlaubte Domains)
```
"Lade Webseite example.com"
"Hole github.com"
```

---

## 🔧 Troubleshooting

### Server läuft nicht
```bash
# Port prüfen
ss -tlnp | grep 8001

# Server starten
./start_server.sh

# Logs prüfen
tail -f server.log
```

### OpenWebUI verbindet nicht
```bash
# Vollständiger Check
./openwebui_check.sh

# Direkt testen
curl http://127.0.0.1:8001/health
```

### 404-Fehler
- ✅ Nutze vollständige Pfade: `/v1/chat/completions`
- ✅ Nicht nur `/v1` (gibt 404)
- ✅ API Base URL korrekt: `http://127.0.0.1:8001/v1`

---

## 🛡️ Sicherheit

### Sandbox-Modus (aktiv)
- Alle Datei-Operationen in: `/home/danijel-jd/localagent_sandbox`
- Shell-Kommandos deaktiviert
- Nur 4 Domains erlaubt

### Live-Modus aktivieren
```yaml
# config/config.yaml
sandbox: false
```
⚠️ **Vorsicht**: Voller System-Zugriff!

---

## 📊 System-Status

```bash
# Schneller Check
./openwebui_check.sh

# Detaillierter Check
./health_check.sh

# Server-Logs
tail -f server.log

# Prozess-Status
ps aux | grep openwebui_agent_server
```

---

## 📝 VSCode Integration

### Tasks verfügbar (Ctrl+Shift+P → Run Task):
- 🚀 Start LocalAgent-Pro
- 🛑 Stop LocalAgent-Pro
- 🏥 Health Check
- 📊 Server Status
- 📝 Server Logs

### Copilot-Prompt
Siehe: `COPILOT_PROMPT.md`

---

## 📦 Projekt-Struktur

```
LocalAgent-Pro/
├── start_server.sh              ✅ Server starten
├── stop_server.sh               ✅ Server stoppen
├── health_check.sh              ✅ Vollständiger Test
├── openwebui_check.sh           ✅ Schneller Check
├── COPILOT_PROMPT.md            📖 Copilot-Anleitung
├── OPENWEBUI_INTEGRATION.md     📖 Vollständige Doku
├── COMPLETE_GUIDE.md            📖 Diese Datei
├── server.log                   📊 Live-Logs
├── config/
│   └── config.yaml              ⚙️ Konfiguration
└── src/
    └── openwebui_agent_server.py 🤖 Server
```

---

## ✅ Checkliste

- [x] Server läuft auf Port 8001
- [x] OpenWebUI läuft auf Port 3000
- [x] API Base URL: `http://127.0.0.1:8001/v1`
- [x] Health-Check erfolgreich
- [x] Models verfügbar
- [x] Chat-Endpoint funktioniert
- [ ] OpenWebUI verbunden
- [ ] Test-Prompt erfolgreich

---

## 🎓 Weitere Hilfe

- **Vollständige Doku**: `OPENWEBUI_INTEGRATION.md`
- **Copilot-Anleitung**: `COPILOT_PROMPT.md`
- **Quick Reference**: `QUICK_REFERENCE.md`

---

**🎉 Viel Erfolg mit LocalAgent-Pro + OpenWebUI!**

Bei Fragen:
1. Prüfe `./openwebui_check.sh`
2. Schaue in `server.log`
3. Teste Endpoints mit `curl`
