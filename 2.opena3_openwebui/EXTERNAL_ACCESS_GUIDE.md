# Lokalen Server für externe Geräte freigeben

Mache deinen lokalen Browser Agent Tool Server (Port 8765) für andere Geräte im Netzwerk oder über das Internet zugänglich.

---

## ✅ Voraussetzungen

Bevor du startest, stelle sicher dass folgende Punkte erfüllt sind:

| Voraussetzung | Status | Details |
|---------------|--------|---------|
| Server läuft auf Port 8765 | ✅ | `python3 tool_server.py --host 0.0.0.0 --port 8765` |
| 0.0.0.0 Binding | ✅ | Server auf allen Netzwerk-Interfaces erreichbar |
| Firewall/Router erlaubt Port 8765 | ✅ | `sudo ufw allow 8765/tcp` |
| CLI/Terminal Zugriff | ✅ | Linux/macOS/Windows Terminal oder PowerShell |
| Für ngrok: Account & Token | ⚠️ | Optional für Methode 2 (Registrierung kostenlos) |
| Für SSH: Remote SSH-Zugang | ⚠️ | Optional für Methode 3 |

**Schnelle Überprüfung:**
```bash
# Server läuft?
ps aux | grep tool_server

# Port 8765 gebunden?
ss -tlnp | grep 8765

# Firewall Port offen?
sudo ufw status | grep 8765

# Health Endpoint antwortet?
curl http://127.0.0.1:8765/health
```

---

## 📋 Inhaltsverzeichnis

1. [Schnellstart (5 Minuten)](#schnellstart)
2. [Methode 1: LAN-Zugriff (Firewall)](#methode-1-lan-zugriff)
3. [Methode 2: Internet-Zugriff (ngrok)](#methode-2-internet-zugriff)
4. [Methode 3: Sichere Remote (SSH)](#methode-3-sichere-remote-verbindung)
5. [Troubleshooting](#troubleshooting)

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
   - https://dashboard.ngrok.com/signup

2. **Auth Token abrufen:**
   - https://dashboard.ngrok.com/auth/your-authtoken

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

| Feature | LAN (Firewall) | ngrok | SSH |
|---------|----------------|-------|-----|
| **Einrichtung** | ⚡ 5 Min | ⚡ 10 Min | ⚡⚡ 15 Min |
| **Sicherheit** | ⚠️ Grundlegend | ✅ HTTPS | ✅✅ Encrypted |
| **Kostenlos** | ✅ | ✅ (Free Tier) | ✅ |
| **Latenz** | 🟢 <5ms | 🟡 ~50ms | 🟢 ~20ms |
| **Internet-Zugriff** | ❌ (nur LAN) | ✅ Weltweit | ✅ Remote Host |
| **Persistenz** | ✅ Solange läuft | ✅ Pro Abo | ⚠️ Kann Abreißen |
| **Setup-Komplexität** | 🟢 Einfach | 🟡 Mittel | 🟡 Mittel |
| **Performance** | 🟢 Maximal | 🟡 Gut | 🟢 Gut |
| **Mobile Tests** | ✅ | ✅ | ✅ (mit Remote) |

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

**Viel Erfolg beim Freigeben deines Servers! 🚀**
