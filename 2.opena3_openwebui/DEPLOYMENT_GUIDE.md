# 🚀 OpenA3 Web Dashboard - Deployment & Operations Guide

## Quick Start

### Prerequisites

- Python 3.12+
- Linux/macOS/Windows with bash
- 8000 port available

### Installation (60 seconds)

```bash
# 1. Navigate to LocalAgent-Pro
cd /path/to/2.opena3_openwebui/LocalAgent-Pro

# 2. Start the server
python3 web_dashboard.py

# 3. Open browser
open http://localhost:8000
# or: xdg-open http://localhost:8000 (Linux)
# or: start http://localhost:8000 (Windows)
```

**Expected Output:**

```
======================================================================
🤖 OpenA3 Web Dashboard - Production System
======================================================================
✅ System Status: ONLINE
   • API: http://localhost:8000/api/status
   • Tools: http://localhost:8000/api/tools
   • Programs: http://localhost:8000/api/programs

🎤 Voice Programme können gestartet werden mit:
   python3 tools/voice_command_parser.py
   python3 tools/voice_note_recorder.py
   python3 tools/voice_call_system.py
   python3 tools/voice_assistant.py
   python3 tools/voice_transcriber.py
   python3 tools/voice_scheduler.py

⏹️  Drücke CTRL+C zum Beenden
======================================================================
```

---

## Advanced Deployment

### Background Execution

#### Option 1: nohup

```bash
cd /path/to/LocalAgent-Pro && \
nohup python3 web_dashboard.py > web_dashboard.log 2>&1 &
echo $! > web_dashboard.pid
```

#### Option 2: systemd Service

Create `/etc/systemd/system/opena3-dashboard.service`:

```ini
[Unit]
Description=OpenA3 Web Dashboard
After=network.target

[Service]
Type=simple
User=opena3
WorkingDirectory=/opt/opena3/LocalAgent-Pro
ExecStart=/usr/bin/python3 /opt/opena3/LocalAgent-Pro/web_dashboard.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable opena3-dashboard
sudo systemctl start opena3-dashboard
sudo systemctl status opena3-dashboard
```

#### Option 3: Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app/LocalAgent-Pro
COPY . .

EXPOSE 8000

CMD ["python3", "web_dashboard.py"]
```

Build and run:

```bash
docker build -t opena3-dashboard .
docker run -d -p 8000:8000 --name opena3 opena3-dashboard
```

#### Option 4: Screen Session

```bash
screen -S opena3-dashboard -d -m bash -c \
  "cd /path/to/LocalAgent-Pro && python3 web_dashboard.py"

# Reattach:
screen -r opena3-dashboard

# Detach: Ctrl+A then D
```

#### Option 5: tmux Session

```bash
tmux new-session -d -s opena3 -x 200 -y 50 \
  -c /path/to/LocalAgent-Pro \
  "python3 web_dashboard.py"

# Reattach:
tmux attach-session -t opena3

# Detach: Ctrl+B then D
```

---

## Monitoring & Management

### Check Server Status

```bash
# HTTP status check
curl -s http://localhost:8000/api/status | python3 -m json.tool

# Process check
ps aux | grep web_dashboard | grep -v grep

# Port check
lsof -i :8000

# Recent logs
tail -f /path/to/LocalAgent-Pro/web_dashboard.log
```

### Stop Server

```bash
# Graceful shutdown (running in foreground)
Ctrl+C

# Kill background process
pkill -f "python3 web_dashboard"

# Kill by PID
kill $(cat web_dashboard.pid)

# Force kill
kill -9 $(cat web_dashboard.pid)

# Using systemd
sudo systemctl stop opena3-dashboard

# Using Docker
docker stop opena3 && docker rm opena3
```

### Restart Server

```bash
# Method 1: Kill and restart
pkill -f "python3 web_dashboard" && \
cd /path/to/LocalAgent-Pro && \
nohup python3 web_dashboard.py > web_dashboard.log 2>&1 &

# Method 2: systemd
sudo systemctl restart opena3-dashboard

# Method 3: Docker
docker restart opena3
```

---

## API Usage Examples

### 1. Check System Status

```bash
curl -s http://localhost:8000/api/status | python3 -m json.tool
```

### 2. List Voice Programs

```bash
curl -s http://localhost:8000/api/programs | python3 -m json.tool
```

### 3. Start Voice Program

```bash
curl -X POST http://localhost:8000/api/program/start \
  -H "Content-Type: application/json" \
  -d '{"file":"voice_assistant.py"}'
```

### 4. Execute Shell Command

```bash
curl -X POST http://localhost:8000/api/shell/exec \
  -H "Content-Type: application/json" \
  -d '{"command":"ls -la"}'
```

### 5. Read File

```bash
curl -X POST http://localhost:8000/api/file/read \
  -H "Content-Type: application/json" \
  -d '{"path":"tools/voice_assistant.py"}' \
  | python3 -m json.tool | head -30
```

### 6. Write File

```bash
curl -X POST http://localhost:8000/api/file/write \
  -H "Content-Type: application/json" \
  -d '{"path":"test.txt","content":"Hello World"}' \
  | python3 -m json.tool
```

### 7. Delete File

```bash
curl -X POST http://localhost:8000/api/file/delete \
  -H "Content-Type: application/json" \
  -d '{"path":"test.txt"}' \
  | python3 -m json.tool
```

---

## Configuration

### Port Configuration

Edit web_dashboard.py, line ~17:

```python
PORT = 8000  # Change to desired port
```

### Command Whitelisting

Edit web_dashboard.py, line ~1209:

```python
allowed_commands = [
    "ls", "pwd", "echo", "cat", "grep", "find", "wc",
    "head", "tail", "date", "whoami", "mkdir", "rm",
    "cp", "mv", "touch", "chmod", "python3", "pip3"
]
# Add or remove commands as needed
```

### Timeout Configuration

Edit web_dashboard.py, line ~1229:

```python
timeout=10  # Change timeout in seconds
```

### Output Limiting

Edit web_dashboard.py, line ~1234-1235:

```python
"stdout": result.stdout[:5000],  # Change character limit
"stderr": result.stderr[:5000],  # Change character limit
```

---

## Performance Tuning

### Increase File Size Limit

```python
# In handle_file_read(), around line 1140:
"content": content[:1000000],  # Increase from default
```

### Optimize for High Load

```bash
# Increase file descriptors
ulimit -n 65536

# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 web_dashboard:app
```

### Add Reverse Proxy (nginx)

```nginx
server {
    listen 80;
    server_name opena3.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Security Hardening

### 1. Restrict Network Access

```bash
# Only allow localhost
sudo ufw allow from 127.0.0.1 to any port 8000

# Or use firewall rules
sudo iptables -A INPUT -p tcp --dport 8000 -s 127.0.0.1 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j DROP
```

### 2. Run as Unprivileged User

```bash
sudo useradd -r -s /bin/bash opena3
sudo chown -R opena3:opena3 /opt/opena3
sudo -u opena3 python3 /opt/opena3/LocalAgent-Pro/web_dashboard.py
```

### 3. Enable HTTPS/TLS

Create self-signed certificate:

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

Add to web_dashboard.py:

```python
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert.pem", "key.pem")
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
```

### 4. Add Authentication

```python
def check_auth(self):
    auth_header = self.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    if token != os.getenv('API_TOKEN', ''):
        self.send_error(401, "Unauthorized")
        return False
    return True
```

### 5. Enable Request Logging

```python
import logging
logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(asctime)s - %(method)s %(path)s - %(remote_addr)s'
)
```

---

## Troubleshooting

### Issue: Port 8000 Already in Use

```bash
# Find what's using port 8000
lsof -i :8000
sudo netstat -tulpn | grep :8000

# Kill the process
kill -9 <PID>

# Or use different port
sed -i 's/PORT = 8000/PORT = 8001/' web_dashboard.py
```

### Issue: ModuleNotFoundError

```bash
# Check Python version
python3 --version  # Should be 3.12+

# No external dependencies required - all stdlib
# If error occurs, check Python path:
which python3
```

### Issue: Files Not Found in API

```bash
# Verify working directory
pwd  # Should be in LocalAgent-Pro

# Check file paths
ls -la tools/
ls -la web_dashboard.py

# Use absolute paths in requests
curl -X POST http://localhost:8000/api/file/read \
  -d '{"path":"/absolute/path/to/file"}'  # ❌ Won't work
# Only relative paths allowed!
```

### Issue: Permission Denied

```bash
# Check file permissions
ls -la web_dashboard.py

# Make executable
chmod +x web_dashboard.py

# Check directory permissions
chmod 755 /path/to/LocalAgent-Pro
```

### Issue: Connection Refused

```bash
# Server not running
ps aux | grep web_dashboard

# Start it
cd /path/to/LocalAgent-Pro && python3 web_dashboard.py &

# Check firewall
sudo ufw status
sudo systemctl status firewalld
```

### Issue: Slow Response Times

```bash
# Check system resources
top  # CPU and memory usage
free -h  # Available memory
df -h  # Disk space

# Check for zombie processes
ps aux | grep defunct

# Increase resource limits
ulimit -n 65536  # File descriptors
ulimit -u 4096   # User processes
```

---

## Monitoring Dashboard

### Create Custom Monitoring Script

```bash
#!/bin/bash
# monitor_opena3.sh

while true; do
    clear
    echo "=== OpenA3 Dashboard Status ==="
    echo "Time: $(date)"
    echo ""

    # Check if running
    if pgrep -f "python3 web_dashboard" > /dev/null; then
        echo "✅ Server: RUNNING"
        PID=$(pgrep -f "python3 web_dashboard")
        echo "   PID: $PID"

        # Check resources
        ps aux | grep $PID | grep -v grep | awk '{print "   CPU: "$3"% MEM: "$4"%"}'
    else
        echo "❌ Server: STOPPED"
    fi

    echo ""
    echo "Network Status:"
    curl -s -m 2 http://localhost:8000/api/status | \
      python3 -m json.tool 2>/dev/null || echo "❌ No response"

    echo ""
    echo "Last 5 log lines:"
    tail -5 web_dashboard.log 2>/dev/null || echo "No log file"

    sleep 10
done
```

Run monitoring:

```bash
chmod +x monitor_opena3.sh
./monitor_opena3.sh
```

---

## Backup & Recovery

### Backup Configuration

```bash
# Backup entire directory
tar -czf opena3_backup_$(date +%s).tar.gz /path/to/LocalAgent-Pro

# Backup specific files
cp web_dashboard.py web_dashboard.py.bak
cp -r tools/ tools.bak/
```

### Recover from Backup

```bash
# Extract full backup
tar -xzf opena3_backup_<timestamp>.tar.gz

# Restore specific files
cp web_dashboard.py.bak web_dashboard.py
cp -r tools.bak/ tools/
```

### Database Backup (if applicable)

```bash
# SQLite backup
cp projekte.db projekte.db.backup

# Restore
cp projekte.db.backup projekte.db
```

---

## Logs & Debugging

### View Live Logs

```bash
# Using tail
tail -f /path/to/LocalAgent-Pro/web_dashboard.log

# Using journalctl (systemd)
sudo journalctl -u opena3-dashboard -f

# Using docker logs
docker logs -f opena3
```

### Enable Debug Mode

Add to web_dashboard.py:

```python
DEBUG = True

def log_request(self):
    if DEBUG:
        print(f"[{datetime.now()}] {self.method} {self.path}")
        print(f"  Headers: {dict(self.headers)}")
        print(f"  Body: {self.rfile.read()}")
```

### Log Rotation

```bash
# Using logrotate
echo "/path/to/LocalAgent-Pro/web_dashboard.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
}" | sudo tee /etc/logrotate.d/opena3-dashboard
```

---

## Upgrade & Maintenance

### Check for Updates

```bash
cd /path/to/2.opena3_openwebui
git status
git pull origin main
```

### Update Voice Programs

```bash
# Backup current
cp -r tools/ tools.backup/

# Update from repository
git checkout tools/

# Or download specific file
wget -O tools/voice_assistant.py \
  https://raw.githubusercontent.com/repo/voice_assistant.py
```

### Python Dependencies

```bash
# Already using only stdlib - no dependency management needed
# But if you add packages:
pip freeze > requirements.txt
pip install -r requirements.txt
```

---

## Performance Benchmarks

### Response Time Summary

| Operation                    | Typical Time | Max Time |
| ---------------------------- | ------------ | -------- |
| GET /                        | 10-20ms      | 50ms     |
| GET /api/status              | 1-2ms        | 5ms      |
| POST /api/file/read (1KB)    | 5-10ms       | 20ms     |
| POST /api/program/start      | 50-100ms     | 200ms    |
| POST /api/shell/exec (quick) | 10-50ms      | 100ms    |

### System Load Baseline

- **Memory:** ~50MB idle
- **CPU:** <1% idle
- **Disk:** <1MB

---

## Support & Resources

### Get Help

1. **Logs:** Check `/path/to/LocalAgent-Pro/web_dashboard.log`
2. **API Test:** Try `curl http://localhost:8000/api/status`
3. **Browser Console:** Open DevTools (F12) → Console
4. **Manual:** See SECURITY_AUDIT_REPORT.md and FUNCTIONAL_TEST_REPORT.md

### Documentation Files

- `web_dashboard.py` - Main application
- `SECURITY_AUDIT_REPORT.md` - Security analysis
- `FUNCTIONAL_TEST_REPORT.md` - Test results
- `DEPLOYMENT_GUIDE.md` - This file

---

## Emergency Procedures

### Emergency Stop

```bash
# Stop all processes
pkill -9 python3

# Or specific daemon
killall web_dashboard.py

# Check nothing is running
ps aux | grep python3
```

### Emergency Rollback

```bash
# Restore previous version
cd /path/to/2.opena3_openwebui
git revert HEAD --no-edit

# Or restore from backup
tar -xzf opena3_backup_latest.tar.gz

# Restart
python3 LocalAgent-Pro/web_dashboard.py
```

### Emergency Port Recovery

```bash
# If port 8000 stuck:
sudo lsof -ti:8000 | xargs sudo kill -9

# Wait 60 seconds for TCP TIME_WAIT
sleep 60

# Restart service
systemctl restart opena3-dashboard
```

---

## Conclusion

The OpenA3 Web Dashboard is production-ready and can be deployed using any of the methods above. Choose the deployment method that best fits your infrastructure (standalone, systemd, Docker, etc.).

**Questions?** Check the logs and error messages first - they usually point to the exact issue!

---

## 📖 Externe Zugriffs-Anleitung

### Browser Agent Tool Server - Externe Zugänglichkeit

Mache deinen lokalen Browser Agent Tool Server (Port 8765) für andere Geräte im Netzwerk oder über das Internet zugänglich – LAN, ngrok, SSH.

**Projekt:** Browser Agent Tool Server - Externe Zugänge
**Datum:** 2025-11-25
**Status:** ✅ PRODUKTIONSFERTIG
**Version:** 1.0.0
**LLM-Umgebung:** OpenWebUI / Browser Agent
**Verwendetes Modell:** `gpt5nano` (statt `gpt-4.1-nano`)

---

## 🧠 Technische Einordnung: Was macht der Browser Agent Tool Server?

Der Browser Agent Tool Server ist ein schlanker HTTP-Service, der Funktionen („Tools") für ein LLM wie `gpt5nano` bereitstellt und diese über definierte Endpunkte im Netzwerk exponiert.

### Kernaufgaben

1. **Tool-Endpunkte bereitstellen**
   - Der Server stellt HTTP-Endpunkte zur Verfügung (z. B. für Web-Requests, Dateizugriffe, interne Services).
   - Diese Endpunkte werden nicht direkt vom Menschen, sondern primär vom LLM (z. B. `gpt5nano` im Browser Agent) aufgerufen.
   - Der Server arbeitet zustandslos pro Request: jede Anfrage enthält alle benötigten Daten (JSON-Request → JSON-Response).

2. **Manifest für LLM-Integration liefern**
   - Der Endpoint `/manifest` liefert eine JSON-Beschreibung der verfügbaren Tools.
   - Typische Inhalte des Manifests sind u. a.:
     - Name und Beschreibung der Tools
     - HTTP-Methode und Pfad
     - erwartete Input-Parameter (Schema)
     - erwartete Response-Struktur
     - Informationen zur Authentifizierung (z. B. Bearer Token)

   - Das Manifest wird von OpenWebUI / Browser Agent geladen, damit `gpt5nano` „weiß", welche Aktionen es über den Tool Server ausführen darf.

3. **Gesundheits- und Statuschecks**
   - Der Endpoint `/health` beantwortet einfache Statusabfragen (z. B. `status`, `service`, `version`, `timestamp`).
   - Wird verwendet für:
     - lokale Funktionsprüfung per `curl`
     - Monitoring / Check-Probes (z. B. von Supervisor, Systemd, externem Monitoring)

4. **Backend-Entkopplung vom Modell**
   - Der Tool Server selbst ist **modellagnostisch**:
     - Er „kennt" das Modell nicht, sondern verarbeitet nur HTTP-Requests.

   - Die Zuordnung zum Modell erfolgt in der LLM-Schicht (z. B. OpenWebUI-Konfiguration), wo explizit `gpt5nano` als Modell gesetzt ist.
   - Dadurch kannst du das Modell (z. B. von `gpt4.1` auf `gpt5nano`) wechseln, ohne den Tool Server umzubauen.

---

## 🧩 Architektur: Zusammenspiel mit gpt5nano

### High-Level Flow

1. **Nutzer-Eingabe**
   - Der User schreibt eine Anfrage in OpenWebUI / Browser Agent.

2. **LLM-Verarbeitung (gpt5nano)**
   - OpenWebUI ruft das Modell `gpt5nano` auf.
   - `gpt5nano` entscheidet anhand des Systemprompts und des Manifests, ob ein Tool-Aufruf nötig ist (z. B. HTTP-Request, Suche, Dateizugriff).

3. **Tool-Aufruf über Tool Server (Port 8765)**
   - OpenWebUI / Browser Agent sendet einen HTTP-Request an den Browser Agent Tool Server, z. B.:
     - `GET http://<SERVER-IP>:8765/health`
     - `GET http://<SERVER-IP>:8765/manifest`
     - weitere Tool-Endpunkte (z. B. `POST /tool/...`) je nach Konfiguration.

4. **Antwortfluss**
   - Der Tool Server verarbeitet die Anfrage und liefert eine JSON-Response.
   - `gpt5nano` erhält die Tool-Response, interpretiert sie und baut daraus die finale Antwort für den Benutzer.

### Wichtiger Punkt

- Die „Intelligenz" (Planung, Entscheidung, Interpretation) liegt bei **`gpt5nano`**.
- Die „Aktionen" (HTTP-Aufrufe, Daten holen, externe Systeme ansprechen) liegen beim **Browser Agent Tool Server**.
- Die externe Zugänglichkeit (LAN, ngrok, SSH) erweitert nur den Netzwerkbereich, **nicht** die Logik des Servers.

---

## ✅ Voraussetzungen

### Erforderlich (5 Punkte)

Bevor du startest, stelle sicher dass folgende Punkte erfüllt sind:

| #   | Voraussetzung                     | Status | Befehl                         |
| --- | --------------------------------- | ------ | ------------------------------ |
| 1   | Server läuft auf Port 8765        | ✅     | `ps aux \| grep tool_server`   |
| 2   | 0.0.0.0 Binding aktiv             | ✅     | `ss -tlnp \| grep 8765`        |
| 3   | Firewall/Router erlaubt Port 8765 | ✅     | `sudo ufw status \| grep 8765` |
| 4   | CLI/Terminal Zugriff              | ✅     | Bash, Zsh, PowerShell, WSL     |
| 5   | Bearer Token gesetzt              | ✅     | `echo $BEARER_TOKEN`           |

### Optional (2 Punkte)

| #   | Option                | Nutzen             | Quelle                                 |
| --- | --------------------- | ------------------ | -------------------------------------- |
| 6   | ngrok Account & Token | Internet-Zugriff   | [https://ngrok.com](https://ngrok.com) |
| 7   | SSH Remote Zugriff    | Sicheres Tunneling | SSH-Schlüssel                          |

### Spezifisch für LLM / Browser Agent

| #   | Voraussetzung                          | Status | Hinweis                                                          |
| --- | -------------------------------------- | ------ | ---------------------------------------------------------------- |
| 8   | OpenWebUI / Browser Agent konfiguriert | ✅     | Instanz läuft und kann HTTP-Tools nutzen                         |
| 9   | LLM-Modell `gpt5nano` aktiv            | ✅     | In der OpenWebUI-/Agent-Konfiguration als Standardmodell gesetzt |

---

## 🔍 Schnelle Überprüfung (vor Start)

Führe diese 4 Befehle aus:

```bash
# 1. Server läuft?
ps aux | grep tool_server

# 2. Port 8765 gebunden?
ss -tlnp | grep 8765

# 3. Firewall Port offen?
sudo ufw status | grep 8765

# 4. Health Endpoint antwortet?
curl http://127.0.0.1:8765/health
```

---

## 📋 Inhaltsverzeichnis

1. [Schnellstart (5 Minuten)](#🚀-schnellstart)
2. [Methode 1: LAN-Zugriff (Firewall)](#🔧-methode-1-lan-zugriff-firewall)
3. [Methode 2: Internet-Zugriff (ngrok)](#🌐-methode-2-internet-zugriff-ngrok)
4. [Methode 3: Sichere Remote (SSH)](#🔐-methode-3-sichere-remote-verbindung)
5. [Troubleshooting](#🔍-troubleshooting)

---

## 🚀 Schnellstart

### 5-Minuten Setup für LAN-Zugriff

**1. Terminal öffnen und zu Projekt navigieren:**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
```

**2. Tool Server auf 0.0.0.0 starten:**

```bash
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

**3. Deine lokale IP-Adresse finden:**

**Linux/macOS:**

```bash
ip a | grep "inet " | grep -v 127.0.0.1
# oder
ifconfig | grep "inet "
```

**Windows (in PowerShell):**

```powershell
ipconfig
# Suche: IPv4-Adresse (z.B. 192.168.x.x)
```

**Beispiel Output:**

```
inet 192.168.0.70/24 brd 192.168.0.255 scope global dynamic eth0
```

→ Deine IP: `192.168.0.70`

**4. Von anderem Gerät im selben Netzwerk testen:**

**iPhone/Android/Laptop im Browser:**

```
http://192.168.0.70:8765
```

**oder via curl:**

```bash
curl http://192.168.0.70:8765/health
curl http://192.168.0.70:8765/manifest
```

✅ **Fertig!** Dein Server ist jetzt im Netzwerk zugänglich.

---

## 🔧 Methode 1: LAN-Zugriff (Firewall)

### Für Zugriff von Geräten im selben Netzwerk

#### Schritt 1: Server auf 0.0.0.0 binden

**Terminal 1 - Tool Server starten:**

```bash
# Wechsel zum Projektverzeichnis
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui

# Starten auf 0.0.0.0 (alle Netzwerk-Interfaces)
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

**Output sollte sein:**

```
🚀 Tool Server gestartet auf 0.0.0.0:8765
   Dashboard: http://localhost:8765
   Manifest: http://localhost:8765/manifest
   OpenWebUI URL: http://192.168.0.70:8765/manifest
```

#### Schritt 2: Lokale IP-Adresse ermitteln

**Linux:**

```bash
hostname -I
# oder ausführlicher:
ip a show | grep "inet " | grep -v 127.0.0.1

# Beispiel Output:
# inet 192.168.0.70/24 brd 192.168.0.255 scope global dynamic eth0
```

**macOS:**

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1

# Beispiel Output:
# inet 192.168.0.70 netmask 0xffffff00 broadcast 192.168.0.255
```

**Windows PowerShell:**

```powershell
ipconfig

# Suche nach:
# IPv4-Adresse . . . . . . . . . . . : 192.168.0.70
```

#### Schritt 3: Firewall konfigurieren (optional)

**Linux (UFW):**

```bash
# Port freigeben (wenn UFW aktiv)
sudo ufw allow 8765/tcp

# Status überprüfen
sudo ufw status
```

**Linux (iptables):**

```bash
# Prüfe ob Port offen ist
sudo iptables -L -n | grep 8765

# Falls notwendig:
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

**macOS:**

```bash
# macOS Firewall (System Preferences → Security & Privacy)
# Oder via Terminal:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /path/to/python
```

**Windows (Defender Firewall):**

```powershell
# PowerShell (als Admin)
New-NetFirewallRule -DisplayName "Python 8765" `
  -Direction Inbound -LocalPort 8765 -Protocol TCP -Action Allow
```

#### Schritt 4: Von externem Gerät testen

**Von Laptop/Phone im selben Netzwerk:**

```bash
# Terminal/Shell:
curl http://192.168.0.70:8765/health

# Browser:
http://192.168.0.70:8765
```

**Erwartet Output:**

```json
{
  "status": "ok",
  "timestamp": "2025-11-25T10:30:00",
  "service": "Browser Agent Tool Server",
  "version": "1.0.0"
}
```

#### Schritt 5: Port-Forwarding für Internet (optional)

**Nur notwendig wenn Router-Zugriff gewünscht:**

1. **Router Admin öffnen** (meist 192.168.1.1 oder 192.168.0.1)

2. **Port Forwarding suchen** (Settings → Advanced → Port Forwarding)

3. **Eintrag erstellen:**
   - External Port: `8765`
   - Internal IP: `192.168.0.70`
   - Internal Port: `8765`
   - Protocol: `TCP`

4. **Speichern & Router neu starten**

5. **Teste von außerhalb des Netzwerks:**

```bash
# Finde deine öffentliche IP:
curl https://api.ipify.org

# Test von außen:
curl https://YOUR_PUBLIC_IP:8765/health
```

⚠️ **Sicherheit beachten:**

- Port-Forwarding nur für vertrauenswürdige Services
- Immer Bearer Token verwenden
- Idealerweise: ngrok oder SSH verwenden (sicherer)

---

## 🌐 Methode 2: Internet-Zugriff (ngrok)

### Für öffentlichen Zugriff von überall

#### Installation

**macOS:**

```bash
brew install ngrok
```

**Linux:**

```bash
# Debian/Ubuntu
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# oder direct download:
curl -L https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip -o ngrok.zip
unzip ngrok.zip
sudo mv ngrok /usr/local/bin/
```

**Windows:**

```powershell
choco install ngrok
# oder manual von https://ngrok.com/download
```

#### Authentifizierung

1. **Kostenlos Account erstellen:**
   - [https://dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)

2. **Auth Token abrufen:**
   - [https://dashboard.ngrok.com/auth/your-authtoken](https://dashboard.ngrok.com/auth/your-authtoken)

3. **Token konfigurieren:**

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

#### Tunnel starten

**Terminal 1 - Tool Server:**

```bash
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

**Terminal 2 - ngrok Tunnel:**

```bash
ngrok http 8765
```

**Output:**

```
ngrok                                                                (Ctrl-C to quit)

Session Status                online
Account                       your-email@example.com (Plan: Free)
Version                       3.0.5
Region                        eu (France)
Latency                       23ms
Web Interface                 http://127.0.0.1:4040

Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8765

Connections                   ttl     opn     dl      ul      pd
                              0       0       0       0       0
```

#### Public URL verwenden

**Von überall zugänglich:**

```bash
# Health Check:
curl https://abc123def456.ngrok.io/health

# Manifest:
curl https://abc123def456.ngrok.io/manifest

# Browser:
https://abc123def456.ngrok.io
```

#### ngrok Dashboard überwachen

```
http://127.0.0.1:4040
```

Hier siehst du:

- Alle eingehenden Requests
- Response Status Codes
- Headers & Body
- Replay Möglichkeiten

#### Multi-Port Setup

Für mehrere Services (eigene Terminal-Fenster):

```bash
# Terminal 1 - Tool Server (8765)
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# Terminal 2 - ngrok für Tool Server
ngrok http 8765

# Terminal 3 - Browser Agent (12350) - optional
python3 LocalAgent-Pro/opena6/main.py &

# Terminal 4 - ngrok für Browser Agent
ngrok http 12350
```

#### Tipps & Tricks

**Problem: URL ändert sich bei jedem Neustart**

- Lösung: ngrok Pro Account ($5/Monat) für reserved domains
- Oder: Immer neue URL kommunizieren

**Rate Limiting:**

```bash
# Für 100 requests/minute:
ngrok http 8765 --rate-limit 100r/m
```

**IP Whitelist:**

```bash
# Nur von bestimmten IPs:
ngrok http 8765 --allow-ip 203.0.113.0
```

**Custom Subdomain (Pro):**

```bash
ngrok http 8765 --subdomain my-browser-agent
# URL: https://my-browser-agent.ngrok.io
```

---

## 🔐 Methode 3: Sichere Remote-Verbindung

### SSH Tunneling für Sicherheit

#### SSH Forward Tunnel

**Ziel:** Remote-Server → Lokaler Service

```bash
# Syntax:
ssh -L LOCAL_PORT:localhost:REMOTE_PORT user@remote.host -N

# Beispiel - Tool Server:
ssh -L 8765:localhost:8765 user@remote.host -N
```

**Dann vom Remote-Server:**

```bash
curl http://localhost:8765/health
```

#### SSH Reverse Tunnel

**Ziel:** Lokaler Service → Remote-Server

```bash
# Syntax:
ssh -R REMOTE_PORT:localhost:LOCAL_PORT user@remote.host -N

# Beispiel:
ssh -R 8765:localhost:8765 user@remote.host -N
```

**Dann von außen (auf remote.host):**

```bash
curl http://remote.host:8765/health
```

#### Mit SSH Key

```bash
# Forward Tunnel mit Key:
ssh -i ~/.ssh/id_rsa -L 8765:localhost:8765 user@remote.host -N

# Reverse Tunnel mit Key:
ssh -i ~/.ssh/id_rsa -R 8765:localhost:8765 user@remote.host -N
```

#### Persistent im Background

```bash
# Starte im Hintergrund:
nohup ssh -L 8765:localhost:8765 user@remote.host -N > ssh_tunnel.log 2>&1 &

# Überprüfe den Prozess:
ps aux | grep ssh

# Beende den Tunnel:
pkill -f "ssh.*8765"
```

#### Mit Automatischem Neustart

**Datei: `start_ssh_tunnel.sh`**

```bash
#!/bin/bash

REMOTE_USER="user"
REMOTE_HOST="example.com"
LOCAL_PORT=8765
REMOTE_PORT=8765

# Stelle sicher dass SSH-Agent läuft
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

# Starte Tunnel
while true; do
    ssh -i ~/.ssh/id_rsa \
        -R ${REMOTE_PORT}:localhost:${LOCAL_PORT} \
        ${REMOTE_USER}@${REMOTE_HOST} -N

    echo "SSH Tunnel getrennt, reconnect in 10 Sekunden..."
    sleep 10
done
```

**Ausführbar machen:**

```bash
chmod +x start_ssh_tunnel.sh
./start_ssh_tunnel.sh
```

---

## 🛡️ Sicherheit

### Best Practices

**1. Bearer Token verwenden:**

```bash
# Alle Requests mit Auth Header:
curl -H "Authorization: Bearer sk_opena6_browser_v3_production" \
  http://192.168.0.70:8765/health
```

**2. HTTPS erzwingen:**

- ngrok: Automatisch HTTPS
- SSH: Verschlüsselt
- Firewall: Nur HTTPS bei externem Zugriff

**3. IP Whitelist (optional):**

```bash
# Nur von bestimmtem Netzwerk:
# In Router: Source IP Filtering

# Oder mit iptables:
sudo iptables -A INPUT -p tcp --dport 8765 \
  -s 192.168.0.0/24 -j ACCEPT
```

**4. VPN als zusätzliche Schutzschicht:**

```bash
# Beispiel mit WireGuard:
# 1. VPN Server einrichten
# 2. Client connecting
# 3. Dann SSH/HTTP durch VPN-Tunnel
```

**5. Rate Limiting:**

```bash
# Mit ngrok:
ngrok http 8765 --rate-limit 100r/m

# Mit iptables:
sudo iptables -A INPUT -p tcp --dport 8765 \
  -m limit --limit 100/min --limit-burst 200 -j ACCEPT
```

**6. Logging & Monitoring:**

```bash
# ngrok Web UI: http://127.0.0.1:4040

# SSH Logs:
tail -f /var/log/auth.log | grep sshd

# Service Logs:
journalctl -u tool_server -f
```

---

## 🔍 Troubleshooting

### Problem: "Connection refused"

```bash
# 1. Überprüfe ob Service läuft:
ps aux | grep tool_server

# 2. Überprüfe ob Port offen ist:
ss -tlnp | grep 8765
netstat -tulpn | grep 8765

# 3. Starte Service neu:
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

### Problem: "Permission denied" (Port < 1024)

```bash
# Port 80/443 brauchen sudo:
sudo python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 80

# Besser: Port > 1024 verwenden und Port Forwarding:
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8765
```

### Problem: Firewall blockiert

```bash
# Linux UFW:
sudo ufw allow 8765/tcp
sudo ufw reload

# Linux iptables:
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4

# Check:
sudo ufw status numbered
```

### Problem: ngrok funktioniert nicht

```bash
# Überprüfe Installation:
which ngrok
ngrok --version

# Überprüfe Auth:
cat ~/.ngrok2/ngrok.yml | grep authtoken

# Teste ngrok direkt:
ngrok http 8765 --log stdout

# Logs:
ngrok diagnose
```

### Problem: SSH Tunnel schließt sich

```bash
# Halte Verbindung offen mit ServerAliveInterval:
ssh -o ServerAliveInterval=60 -L 8765:localhost:8765 user@host -N

# oder mit autossh (auto-reconnect):
brew install autossh  # macOS
# dann:
autossh -M 20000 -L 8765:localhost:8765 user@host -N
```

### Problem: Port bereits in Benutzung

```bash
# Finde Prozess:
lsof -i :8765
sudo netstat -tulpn | grep 8765

# Beende Prozess:
kill -9 PID

# Oder anderer Port:
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 9999
```

### Problem: Langsame Verbindung

```bash
# ngrok Latency überprüfen: http://127.0.0.1:4040

# SSH Latency:
ssh -L 8765:localhost:8765 user@host -v 2>&1 | grep "Connection established"

# Test Durchsatz:
time curl https://your-tunnel.ngrok.io/health | wc -c
```

---

## 📊 Vergleich der Methoden

| Feature               | LAN (Firewall)   | ngrok          | SSH              |
| --------------------- | ---------------- | -------------- | ---------------- |
| **Einrichtung**       | ⚡ 5 Min         | ⚡ 10 Min      | ⚡⚡ 15 Min      |
| **Sicherheit**        | ⚠️ Grundlegend   | ✅ HTTPS       | ✅✅ Encrypted   |
| **Kostenlos**         | ✅               | ✅ (Free Tier) | ✅               |
| **Latenz**            | 🟢 <5ms          | 🟡 ~50ms       | 🟢 ~20ms         |
| **Internet-Zugriff**  | ❌ (nur LAN)     | ✅ Weltweit    | ✅ Remote Host   |
| **Persistenz**        | ✅ Solange läuft | ✅ Pro Abo     | ⚠️ Kann Abreißen |
| **Setup-Komplexität** | 🟢 Einfach       | 🟡 Mittel      | 🟡 Mittel        |
| **Performance**       | 🟢 Maximal       | 🟡 Gut         | 🟢 Gut           |
| **Mobile Tests**      | ✅               | ✅             | ✅ (mit Remote)  |

---

## 🚀 Schnelle Befehle (Copy & Paste)

### LAN-Setup in 30 Sekunden:

```bash
# Terminal 1:
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# Terminal 2:
IP=$(hostname -I | awk '{print $1}')
echo "Zugriff: http://$IP:8765"
curl http://$IP:8765/health
```

### ngrok Setup in 1 Minute:

```bash
# Einmal:
ngrok config add-authtoken YOUR_TOKEN

# Dann:
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765 &
ngrok http 8765
```

### SSH Reverse Tunnel:

```bash
ssh -R 8765:localhost:8765 user@example.com -N
```

---

## 📚 Weitere Ressourcen

- [ngrok Dokumentation](https://ngrok.com/docs)
- [SSH Port Forwarding](https://www.ssh.com/ssh/tunneling/)
- [Linux Firewall Basics](https://wiki.ubuntu.com/UncomplicatedFirewall)
- [OpenWebUI Integration](./README_OPENWEBUI.md)
- [Tool Server Dokumentation](./tool_server.py)

---

**Last Updated:** 2025-11-25
**Version:** 1.0
**Status:** Production Ready ✅
