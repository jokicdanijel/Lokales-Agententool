# VS Code Browser Agent Bridge

Integriere den Browser Agent Tool Server direkt in VS Code mit vollständiger IDE-Unterstützung.

## 🎯 Features

### 1. **REST Client Integration**

- `.http` Dateien für alle API Calls
- Visual Request/Response Editor
- Environment Variables Support
- History & Autocomplete

### 2. **Debug Launcher**

- Start Tool Server mit Debugger
- Breakpoints & Step-through Debugging
- Console Output in VS Code
- Environment Variables Management

### 3. **Tasks & Commands**

- Build Tasks für Server Start
- Problem Matcher für Error Detection
- Quick Commands über Command Palette
- Keyboard Shortcuts

### 4. **File Nesting**

- Organisierte File Structure
- Related Files zusammengefasst
- Better Overview im Explorer

---

## 📦 Installation

### Schritt 1: VS Code Extension installieren

```bash
# Öffne VS Code Extensions
Ctrl+Shift+X (Windows/Linux)
Cmd+Shift+X (Mac)

# Suche und installiere:
- REST Client (humao.rest-client)
- Thunder Client (Alternative)
- Python (für Debugger)
```

### Schritt 2: Setup-Skript ausführen

```bash
cd LocalAgent-Pro/opena6
python3 vscode_bridge.py setup
```

Das erstellt automatisch:

- `.vscode/settings.json` - VS Code Einstellungen
- `.vscode/launch.json` - Debugger Konfiguration
- `.vscode/tasks.json` - Build Tasks
- `browser_agent.http` - REST Client Datei

---

## 🚀 Verwendung

### REST Client (.http Datei)

**Öffne `browser_agent.http` und klicke "Send Request":**

```
@baseUrl = http://192.168.0.70:8765
@token = sk_opena6_browser_v3_production

### 🏥 Health Check
GET {{baseUrl}}/health

### 🌐 Open Website
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "open",
  "url": "https://example.com"
}
```

**Ergebnis:** Response erscheint neben dem Request

---

### Debug Launcher

**Starte im Debug Mode:**

```
Run → Open Configurations → Wähle:
  - "Browser Agent Tool Server" (Starts server with debug)
  - "Browser Agent opena6" (Starts agent with debug)
  - "Full Stack" (Both mit Breakpoints)
```

**Features:**

- F5 zum Starten
- F10 Step Over
- F11 Step Into
- Breakpoints setzen
- Variables inspizieren

---

### Tasks

**Öffne Tasks über Command Palette:**

```
Ctrl+Shift+P → "Tasks: Run Task"
```

**Verfügbare Tasks:**

1. **Start Tool Server** - Startet Server (Background)
2. **Health Check** - Zeigt Server Status
3. **Test Tool Actions** - Testet Manifest
4. **View Dashboard** - Öffnet Browser Dashboard

---

### Keyboard Shortcuts

| Shortcut       | Aktion            |
| -------------- | ----------------- |
| `Ctrl+Shift+B` | Health Check      |
| `Ctrl+Shift+D` | Open Dashboard    |
| `Ctrl+Alt+T`   | Start Tool Server |

---

## 📚 Konfigurationsdateien

### .vscode/settings.json

```json
{
  "rest-client.environmentVariables": {
    "$shared": {
      "baseUrl": "http://192.168.0.70:8765",
      "token": "sk_opena6_browser_v3_production"
    }
  },
  "rest-client.timeoutinmilliseconds": 30000
}
```

**Ändere hier:**

- `baseUrl` - Server Adresse
- `token` - Bearer Token
- `timeoutinmilliseconds` - Request Timeout

---

### .vscode/launch.json

```json
{
  "configurations": [
    {
      "name": "Browser Agent Tool Server",
      "type": "python",
      "program": "tool_server.py",
      "args": ["--host", "0.0.0.0", "--port", "8765"]
    }
  ]
}
```

**Debugger Features:**

- Set Breakpoints
- Inspect Variables
- Debug Console
- Stack Trace

---

### .vscode/tasks.json

```json
{
  "tasks": [
    {
      "label": "Start Tool Server",
      "type": "shell",
      "command": "python3 tool_server.py"
    }
  ]
}
```

**Problem Matcher:**

- Automatische Error Detection
- Quick Navigation zu Errors
- Integrated Terminal Output

---

## 🧪 Workflow Beispiel

### 1. Development mit REST Client

```http
### Test Open Website
POST http://192.168.0.70:8765/call
Content-Type: application/json
Authorization: Bearer sk_opena6_browser_v3_production

{
  "action": "open",
  "url": "https://example.com"
}
```

**Klicke:** "Send Request" Button → Response erscheint

---

### 2. Debugging mit Launch Config

```bash
F5 → Start Debugging
```

**Im Debug Console:**

```python
# Breakpoint getroffen?
# Inspiziere Variables:
>>> request.action
'open'
>>> request.url
'https://example.com'
```

---

### 3. Automation mit Tasks

```bash
Ctrl+Shift+P → "Tasks: Run Task"
→ Wähle "Start Tool Server"
```

Task läuft im Background, Output im Terminal

---

## 💡 Pro Tipps

### 1. Environment Variables

```json
{
  "rest-client.environmentVariables": {
    "$shared": {
      "baseUrl": "http://192.168.0.70:8765"
    },
    "production": {
      "token": "sk_prod_token"
    },
    "development": {
      "token": "sk_dev_token"
    }
  }
}
```

Dann nutze: `@environment production`

---

### 2. Response History

REST Client speichert automatisch alle Responses:

```
Click "Response" Tab → "Timeline"
```

Alle bisherigen Responses werden angezeigt!

---

### 3. Request Collections

Speichere häufig genutzte Requests:

```http
# @name GetHealth
GET {{baseUrl}}/health

# @name GetManifest
GET {{baseUrl}}/manifest
```

Command Palette → "REST Client: Save Request as cURL"

---

### 4. Multi-Request Workflows

```http
### @name OpenWebsite
POST {{baseUrl}}/call
...

### @name ExtractText
POST {{baseUrl}}/call
...
```

REST Client führt sequenziell aus und verwendet Outputs

---

## 🔧 Troubleshooting

### Problem: "Extension not found"

```bash
Solution: Install "REST Client" from VS Code Extensions
```

### Problem: 404 beim Health Check

```bash
# Überprüfe:
1. Server läuft? → python3 tool_server.py
2. Port korrekt? → 8765?
3. Firewall offen? → sudo ufw allow 8765
```

### Problem: Authorization Failed

```bash
# Überprüfe Token in settings.json:
"token": "sk_opena6_browser_v3_production"
```

### Problem: Timeout Errors

```json
{
  "rest-client.timeoutinmilliseconds": 60000
}
```

---

## 📋 Checkliste

- [ ] REST Client Extension installiert
- [ ] `vscode_bridge.py setup` ausgeführt
- [ ] `.vscode/settings.json` existiert
- [ ] `.vscode/launch.json` existiert
- [ ] `browser_agent.http` existiert
- [ ] Health Check funktioniert (`GET /health`)
- [ ] Tool Server läuft (Port 8765)
- [ ] Browser Agent online (Port 12350)

---

## 🚀 Nächste Schritte

1. **Öffne VS Code** im Projektordner
2. **Installiere REST Client** Extension
3. **Öffne `browser_agent.http`**
4. **Klicke "Send Request"** auf Health Check
5. **Starte Debugger** mit F5
6. **Teste API Calls** im Response Tab

---

**Status**: 🟢 VS Code Integration Ready

Viel Spaß! 🎉
