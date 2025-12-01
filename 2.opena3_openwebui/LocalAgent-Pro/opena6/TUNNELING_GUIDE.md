# VS Code Server Tunneling Guide

Mache deine lokalen Server (Tool Server 8765, Browser Agent 12350, Compute Agent 12349) öffentlich zugänglich für Remote-Zugriff, Mobile-Testing und Team-Zusammenarbeit.

---

## 🎯 Übersicht: 3 Methoden

| Methode | Setup | Sicherheit | Geschwindigkeit | Best For |
|---------|-------|-----------|-----------------|----------|
| **ngrok** | ⭐⭐ Medium | ⭐⭐⭐ Hoch | ⭐⭐⭐ Schnell | Schnelle Prototypen, Teams |
| **LocalTunnel** | ⭐ Einfach | ⭐⭐ Mittel | ⭐⭐ Mittel | Kostenlos, GitHub Pages |
| **SSH Tunnel** | ⭐⭐⭐ Komplex | ⭐⭐⭐⭐ Sehr Hoch | ⭐⭐⭐ Schnell | Produktiv, Private Infrastruktur |

---

## 🌐 Methode 1: ngrok (Empfohlen für schnelle Tests)

### Installation

**macOS:**
```bash
brew install ngrok
```

**Linux (Ubuntu/Debian):**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update
sudo apt install ngrok
```

**Windows:**
```powershell
# Mit Chocolatey:
choco install ngrok

# Oder manuell: https://ngrok.com/download
```

### Authentifizierung

1. Gehe zu https://dashboard.ngrok.com/auth
2. Copy deinen Auth Token
3. Konfiguriere lokal:
```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### Tunnel starten

**Tool Server (Port 8765):**
```bash
ngrok http 8765
```

**Output:**
```
Session Status                online
Account                       username@example.com
Version                       3.0.0
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8765
```

**Die URL nutzen:**
```bash
# Health Check
curl https://abc123.ngrok.io/health

# Manifest
curl https://abc123.ngrok.io/manifest

# In OpenWebUI
http://abc123.ngrok.io/manifest
```

### Multiple Ports tunneln

```bash
# Terminal 1: Tool Server
ngrok http 8765

# Terminal 2: Browser Agent
ngrok http 12350 --subdomain browser-agent

# Terminal 3: Compute Agent
ngrok http 12349 --subdomain compute-agent

# Terminal 4: OpenWebUI
ngrok http 3000 --subdomain openwebui
```

### ngrok Web Dashboard

Öffne: **http://127.0.0.1:4040**

Sehe:
- Alle aktiven Tunnels
- Request/Response Inspektionen
- Logs und Debugging-Infos
- Replay Funktionalität

---

## 💻 Methode 2: LocalTunnel (Kostenlos & Einfach)

### Installation

```bash
# Benötigt Node.js
npm install -g localtunnel
```

### Tunnel starten

```bash
# Mit automatischer URL
lt --port 8765

# Mit custom Subdomain
lt --port 8765 --subdomain browser-agent

# Mit Optionen
lt --port 8765 --subdomain browser-agent --open false
```

**Output:**
```
your url is: https://browser-agent.loca.lt
```

### Mehrere Ports

```bash
# Terminal 1
lt --port 8765 --subdomain tool-server

# Terminal 2
lt --port 12350 --subdomain browser-agent

# Terminal 3
lt --port 12349 --subdomain compute-agent
```

### Features

- ✅ Kostenlos (keine Registrierung)
- ✅ HTTPS automatisch
- ✅ Custom Domains
- ✅ Lokal debuggen
- ⚠️ Nicht ideal für Produktion

---

## 🔐 Methode 3: SSH Tunneling (Sicherste Methode)

### Voraussetzungen

- SSH Zugriff zu Remote-Server
- SSH Key (optional, aber empfohlen)

### Forward Tunnel (Remote-Server → Lokal)

Du brauchst Zugriff auf einen Remote-Server und möchtest seinen Service lokal nutzen:

```bash
ssh -L LOCAL_PORT:REMOTE_HOST:REMOTE_PORT user@remote.server.com -N
```

**Beispiel:**
```bash
# Greife auf Remote Tool Server zu
ssh -L 8765:localhost:8765 danijel@192.168.0.70 -N

# Nutze lokal
curl http://localhost:8765/health
```

### Reverse Tunnel (Lokal → Remote-Server)

Du möchtest deinen lokalen Service auf Remote zugänglich machen:

```bash
ssh -R REMOTE_PORT:localhost:LOCAL_PORT user@remote.server.com -N
```

**Beispiel:**
```bash
# Mache lokalen Tool Server auf Remote Port 8765 zugänglich
ssh -R 8765:localhost:8765 danijel@192.168.0.70 -N

# Remote kann jetzt zugreifen
curl http://localhost:8765/health
```

### Mit SSH Key

```bash
ssh -i ~/.ssh/id_rsa -L 8765:localhost:8765 user@remote.host -N
```

### Keep-Alive (für lange Sessions)

```bash
ssh -L 8765:localhost:8765 user@remote.host -N \
    -o ServerAliveInterval=60 \
    -o ServerAliveCountMax=5
```

### SSH Config (.ssh/config)

```
Host browser-tunnel
    HostName 192.168.0.70
    User danijel
    LocalForward 8765 localhost:8765
    LocalForward 12350 localhost:12350
    LocalForward 12349 localhost:12349
    ServerAliveInterval 60
    ServerAliveCountMax 5
```

Dann einfach:
```bash
ssh -N browser-tunnel
```

---

## 🔧 VS Code Integration

### Tasks für schnellen Zugriff

Erstelle `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "🌐 Start ngrok (8765)",
      "type": "shell",
      "command": "ngrok http 8765",
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "🌐 Start LocalTunnel (8765)",
      "type": "shell",
      "command": "lt --port 8765 --subdomain browser-agent",
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "🔐 SSH Tunnel to Remote",
      "type": "shell",
      "command": "ssh -N browser-tunnel",
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "🌐 Check Tunnel Health",
      "type": "shell",
      "command": "curl",
      "args": ["-s", "http://127.0.0.1:4040/api/tunnels"],
      "problemMatcher": []
    }
  ]
}
```

**Nutzen:**
```
Ctrl+Shift+P → "Tasks: Run Task" → Wähle "🌐 Start ngrok"
```

### Debug Launch Config

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Tool Server (with ngrok)",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/LocalAgent-Pro/opena6/tool_server.py",
      "console": "integratedTerminal",
      "args": ["--host", "0.0.0.0", "--port", "8765"],
      "preLaunchTask": "🌐 Start ngrok (8765)"
    }
  ]
}
```

---

## 🚀 Praktische Beispiele

### Beispiel 1: Schnelles Mobile Testing

```bash
# Terminal 1: Starte Server
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# Terminal 2: Starte Tunnel
ngrok http 8765

# Output: Forwarding ... https://abc123.ngrok.io
# Auf Mobile-Browser öffnen:
# https://abc123.ngrok.io/health
```

### Beispiel 2: Team Collaboration

```bash
# Dein Laptop
ngrok http 8765 --subdomain team-tool-server

# Teile URL mit Team:
# https://team-tool-server.ngrok.io

# Team kann testen:
# curl https://team-tool-server.ngrok.io/health
```

### Beispiel 3: Full Stack Tunneling

```bash
# Terminal 1: Tool Server
ngrok http 8765 --subdomain=tool-server

# Terminal 2: Browser Agent
ngrok http 12350 --subdomain=browser-agent

# Terminal 3: Compute Agent
ngrok http 12349 --subdomain=compute-agent

# Terminal 4: OpenWebUI
ngrok http 3000 --subdomain=openwebui

# Alle URLs anzeigen:
# http://127.0.0.1:4040
```

### Beispiel 4: Remote Development

```bash
# Von Laptop zu Production Server:
ssh -L 8765:localhost:8765 \
    -L 12350:localhost:12350 \
    -L 12349:localhost:12349 \
    admin@production.server.com -N

# Entwickle lokal gegen Production:
curl http://localhost:8765/health
```

---

## 🔒 Sicherheit Best Practices

### 1. Verwende HTTPS (Automatisch)
- ngrok: ✅ HTTPS nur
- LocalTunnel: ✅ HTTPS nur
- SSH: ✅ Encrypted

### 2. Bearer Token Schutz

```bash
# Nie in Code:
export BEARER_TOKEN="sk_opena6_browser_v3_production"

# In .env (nicht in Git):
BEARER_TOKEN=sk_opena6_browser_v3_production

# Von dort laden:
import os
token = os.getenv('BEARER_TOKEN')
```

### 3. ngrok Basic Auth

```bash
ngrok http 8765 --auth="username:password"
```

### 4. IP Whitelisting

```bash
# SSH Config
ssh -L 8765:localhost:8765 user@host -N

# Oder ngrok (Pro):
ngrok http 8765 --allow-ip-range 192.168.1.0/24
```

### 5. Firewall Rules

```bash
# Linux
sudo ufw allow 8765
sudo ufw allow 12350
sudo ufw allow 12349

# Mac
# System Preferences → Security & Privacy → Firewall
```

---

## 🐛 Troubleshooting

### Problem: "Port already in use"

```bash
# Finde Prozess
lsof -i :8765

# Kill Prozess
kill -9 <PID>

# Oder nutze anderen Port
ngrok http 9999
```

### Problem: ngrok timeout

```bash
# Erhöhe Timeout
ngrok http 8765 --bind-tls=true --client-timeout=30s
```

### Problem: SSH Tunnel "Connection refused"

```bash
# Überprüfe Remote Port
ssh user@host "netstat -tlnp | grep 8765"

# Und lokaler Port
netstat -tlnp | grep 8765
```

### Problem: LocalTunnel "URL not reachable"

```bash
# Starte neu
lt --port 8765 --subdomain browser-agent --local-host 127.0.0.1
```

---

## 📊 Performance Vergleich

| Metrik | ngrok | LocalTunnel | SSH |
|--------|-------|------------|-----|
| Latenz | ~50ms | ~100ms | ~10ms |
| Uptime | 99.9% | 99% | 100% |
| Bandbreite | Unbegrenzt | Begrenzt | Unbegrenzt |
| Kosten | $5-20/mo | Kostenlos | Kostenlos |
| Support | ⭐⭐⭐ | ⭐⭐ | Selbst |

---

## ✅ Checkliste

- [ ] Tunneling-Tool installiert (ngrok/lt/SSH)
- [ ] Local Server läuft auf 0.0.0.0:8765
- [ ] Tunnel aktiv (Public URL verfügbar)
- [ ] Health Check funktioniert
- [ ] Von anderem Netzwerk testbar
- [ ] Logs monitored
- [ ] Security Settings konfiguriert
- [ ] VS Code Tasks eingerichtet

---

## 🚀 Quick Start (5 Min)

```bash
# 1. Installiere ngrok
brew install ngrok  # oder apt install ngrok

# 2. Auth Token (optional aber empfohlen)
ngrok config add-authtoken YOUR_TOKEN

# 3. Starte Server
cd LocalAgent-Pro/opena6
python3 tool_server.py --host 0.0.0.0 --port 8765

# 4. Starte Tunnel (Neue Terminal)
ngrok http 8765

# 5. Verwende Public URL (z.B. https://abc123.ngrok.io)
curl https://abc123.ngrok.io/health
```

**Fertig! 🎉**

---

**Status**: 🟢 Tunneling Setup Complete

Jetzt ist dein Server von überall erreichbar! 🌍
