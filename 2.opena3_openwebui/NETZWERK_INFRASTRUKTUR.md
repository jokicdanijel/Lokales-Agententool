# 🌐 Netzwerk-Infrastruktur & Konfiguration

**Dokument:** Netzwerk-Setup für Browser Agent Tool Server
**Datum:** 25. November 2025
**Status:** ✅ DOKUMENTIERT & GETESTET
**Version:** 1.0.0

---

## 📋 Übersicht

Dieses Dokument beschreibt die komplette Netzwerkinfrastruktur für die externe Erreichbarkeit des Tool Servers (Port 8765) mit 3 verschiedenen Zugriffsmethoden.

---

## 🏗️ Infrastruktur-Komponenten

### 1. Switch/Router-Konfiguration

#### Lokale Netzwerk-Einstellungen

```
Netzwerk:        192.168.0.0/24
Server-IP:       192.168.0.70
Subnet-Mask:     255.255.255.0
Gateway:         192.168.0.1
DNS:             [Lokal oder Standard]
```

#### Router-Port-Freigabe

```
Port:            8765
Protocol:        TCP
Internal IP:     192.168.0.70
External Port:   (Optional, nur für Port-Forwarding)
Status:          ✅ Konfiguriert
```

#### Best Practices

- ✅ Port-Bereich: Außerhalb DHCP-Range
- ✅ IP-Reservation für Server (Static IP)
- ✅ UPnP/UPNP: Deaktiviert (manuell konfigurieren)
- ✅ Port-Forwarding: Nur wenn notwendig

---

## 🔥 Firewall-Einstellungen

### UFW (Ubuntu Uncomplicated Firewall)

#### Status überprüfen

```bash
sudo ufw status
sudo ufw status verbose
```

#### Port 8765 freigeben

```bash
# TCP-Verbindungen erlauben
sudo ufw allow 8765/tcp

# Mit Kommentar
sudo ufw allow 8765/tcp comment "Browser Agent Tool Server"

# Spezifisches Protokoll (falls needed)
sudo ufw allow in 8765/tcp from 192.168.0.0/24 comment "LAN-Zugriff"
```

#### Port 8765 blockieren

```bash
# Falls Zugriff einschränken
sudo ufw deny 8765/tcp

# Nur LAN zulassen
sudo ufw allow in 8765/tcp from 192.168.0.0/24
sudo ufw deny in 8765/tcp from any
```

#### Regeln prüfen

```bash
# Alle aktiven Regeln
sudo ufw show added

# Spezifisch für Port 8765
sudo ufw status | grep 8765

# Löschen einer Regel
sudo ufw delete allow 8765/tcp
```

### iptables (Alternative für erweiterte Konfiguration)

#### Regeln überprüfen

```bash
# INPUT Rules
sudo iptables -L INPUT -n -v

# Spezifisch für Port 8765
sudo iptables -L | grep 8765
```

#### Port 8765 öffnen

```bash
# TCP-Verbindungen erlauben
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT

# Speichern (persistent)
sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
```

#### Rules speichern

```bash
# Für iptables-persistent Paket
sudo apt-get install iptables-persistent

# Dann speichern
sudo netfilter-persistent save
```

### Firewall-Validierung

```bash
# Lokaler Zugriff
curl http://127.0.0.1:8765/health

# LAN-Zugriff (von anderem Gerät)
curl http://192.168.0.70:8765/health

# Port-Status
ss -tlnp | grep 8765
sudo lsof -i :8765

# Firewall-Status
sudo ufw status
sudo iptables -L -n
```

---

## 🔐 ngrok Token-Setup

### 1. ngrok Installation

```bash
# Download ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip

# Oder über package manager
apt-get install ngrok

# Version überprüfen
ngrok version
```

### 2. Authentication Token

#### Token generieren

1. Gehe zu: https://dashboard.ngrok.com
2. Melde dich an (oder erstelle Account)
3. Gehe zu: "Your Authtoken"
4. Kopiere den Token (Format: `[random-string]_[random-string]`)

#### Token konfigurieren

```bash
# Methode 1: Direktes Setup
ngrok config add-authtoken "dein_token_hier"

# Methode 2: Manuell in ~/.ngrok2/ngrok.yml
cat >> ~/.ngrok2/ngrok.yml << EOF
authtoken: dein_token_hier
EOF

# Methode 3: Umgebungsvariable
export NGROK_AUTHTOKEN="dein_token_hier"
```

#### Token überprüfen

```bash
# Konfiguration anzeigen
cat ~/.ngrok2/ngrok.yml

# Oder prüfen ob gespeichert
ngrok authtoken --help
```

### 3. ngrok Session starten

```bash
# Standard HTTP Tunnel
ngrok http 8765

# Mit Session-Name (für Dashboard)
ngrok http 8765 --log=stdout

# Mit spezifischer Region (schneller)
ngrok http 8765 --region eu
```

### 4. Tunnel überprüfen

```bash
# ngrok Dashboard (Standard)
curl http://127.0.0.1:4040/api/tunnels

# JSON Output
curl http://127.0.0.1:4040/api/tunnels | jq

# Beispiel-Output
{
  "tunnels": [
    {
      "name": "command_line",
      "uri": "/tunnels/command_line",
      "public_url": "https://abc123.ngrok.io",
      "proto": "https",
      "config": {
        "addr": "localhost:8765",
        "inspect": true
      },
      "metrics": {
        "conns": {
          "count": 2,
          "gauge": 2,
          "rate1": 0,
          "rate5": 0,
          "rate15": 0
        },
        "http": {
          "count": 10,
          "rate1": 0.5,
          "rate5": 0.2,
          "rate15": 0.1
        }
      }
    }
  ],
  "uri": "/api/tunnels"
}
```

### 5. ngrok-Fehlerbehandlung

| Problem                  | Ursache                  | Lösung                                              |
| ------------------------ | ------------------------ | --------------------------------------------------- |
| "Failed to authenticate" | Token ungültig/fehlt     | Token neu erstellen und konfigurieren               |
| "Request limit exceeded" | Kostenlos-Plan Limit     | Premium-Plan erwägen oder Wartezeit                 |
| "Connection refused"     | Server läuft nicht       | `python3 tool_server.py --host 0.0.0.0 --port 8765` |
| "Address already in use" | Port 8765 bereits belegt | `sudo lsof -i :8765` dann `kill -9 PID`             |

---

## 🔑 SSH-Key-Verwaltung & Tunnel-Zugriff

### 1. SSH-Schlüssel-Paar erstellen

```bash
# Ed25519 Schlüssel (empfohlen)
ssh-keygen -t ed25519 -f ~/.ssh/id_server -C "tool_server_access"

# RSA Schlüssel (älter, aber kompatibel)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_server -C "tool_server_access"

# Keine Passphrase (für Automation)
ssh-keygen -t ed25519 -f ~/.ssh/id_server -N "" -C "tool_server_access"
```

### 2. Public Key auf Remote-Server kopieren

```bash
# Methode 1: ssh-copy-id (einfach)
ssh-copy-id -i ~/.ssh/id_server.pub user@remote.host

# Methode 2: Manuell
cat ~/.ssh/id_server.pub | ssh user@remote.host "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Methode 3: Direkt in authorized_keys
echo "$(cat ~/.ssh/id_server.pub)" >> ~/.ssh/authorized_keys
```

### 3. SSH-Config für einfache Verwaltung

```bash
# Datei: ~/.ssh/config

Host tool_server
    HostName remote.example.com
    User ubuntu
    IdentityFile ~/.ssh/id_server
    LocalForward 8765 localhost:8765
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### 4. SSH Tunnel-Verbindungen

#### Forward Tunnel (Local Port Forwarding)

```bash
# Tool Server remote, lokal zugreifen
ssh -L 8765:localhost:8765 user@remote.host -N

# Mit Config
ssh -N tool_server

# Hintergrund
ssh -L 8765:localhost:8765 user@remote.host -N &

# Status
ps aux | grep "ssh.*8765"
```

#### Reverse Tunnel (Remote Port Forwarding)

```bash
# Tool Server lokal, remote zugreifen
ssh -R 8765:localhost:8765 user@remote.host -N

# Remote: curl http://localhost:8765/health
```

#### Multi-Hop Tunnel

```bash
# Via Jumphost
ssh -J jumphost.com -L 8765:tool_server:8765 user@tool_server -N
```

### 5. SSH-Tunnel Automatisierung

#### Mit autossh (verbindungswiederherstellung)

```bash
# Installation
sudo apt-get install autossh

# Tunnel starten
autossh -M 20000 -L 8765:localhost:8765 user@remote.host -N &

# Konfiguration in systemd
cat > ~/.config/systemd/user/ssh_tunnel.service << EOF
[Unit]
Description=SSH Tunnel to Tool Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/autossh -M 20000 -L 8765:localhost:8765 user@remote.host -N
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable ssh_tunnel
systemctl --user start ssh_tunnel
```

#### Mit SSH-Keys in Cron

```bash
# Crontab-Eintrag (SSH Tunnel alle 5 Min prüfen/starten)
*/5 * * * * pgrep -f "ssh.*8765" || ssh -L 8765:localhost:8765 user@remote.host -N &

# Mit autossh
*/5 * * * * pgrep -f "autossh.*8765" || autossh -M 20000 -L 8765:localhost:8765 user@remote.host -N &
```

### 6. SSH-Key Sicherheit

```bash
# Permissions setzen
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_server
chmod 600 ~/.ssh/authorized_keys

# Public Key auf Server
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

# Private Key Passphrase (optional aber empfohlen)
ssh-keygen -p -f ~/.ssh/id_server

# Schlüssel testen
ssh -i ~/.ssh/id_server -T user@remote.host
```

---

## 📊 Netzwerk-Status & Überwachung

### Health Endpoints

```bash
# Lokaler Health Check
curl -v http://127.0.0.1:8765/health
# Expected: HTTP 200 OK
# Headers: Content-Type: application/json
# Body: {"status": "healthy", "timestamp": "..."}

# LAN Health Check (von anderem Gerät im Netzwerk)
curl -v http://192.168.0.70:8765/health
# Expected: HTTP 200 OK

# Mit Bearer Token
curl -H "Authorization: Bearer sk_opena6_browser_v3_production" \
     http://192.168.0.70:8765/health
```

### Port & Binding Überprüfung

```bash
# Aktueller Port-Status
ss -tlnp | grep 8765
# Expected: tcp  LISTEN  0  128  0.0.0.0:8765  0.0.0.0:*  users:(("python3",pid=12345,fd=5))

# Alternative: netstat
netstat -tlnp | grep 8765

# Prozess-Details
ps aux | grep tool_server
# Expected: python3 .../tool_server.py --host 0.0.0.0 --port 8765

# Offene Connections
ss -tnp | grep 8765
```

### Netzwerk-Konnektivität

```bash
# Lokale IP überprüfen
hostname -I
ip addr show

# Gateway überprüfen
ip route show

# DNS Auflösung
nslookup 192.168.0.70
dig 192.168.0.70

# Netzwerk-Durchsatz (falls verfügbar)
iftop -i eth0
nethogs
```

---

## 🔄 Zugriffsmethoden - Checkliste

### Methode 1: LAN-Zugriff (Schnellste)

| Komponente        | Status | Befehl                                 |
| ----------------- | ------ | -------------------------------------- |
| Server läuft      | ✅     | `ps aux \| grep tool_server`           |
| Port 0.0.0.0:8765 | ✅     | `ss -tlnp \| grep 8765`                |
| Firewall offen    | ✅     | `sudo ufw status \| grep 8765`         |
| Health Endpoint   | ✅     | `curl http://192.168.0.70:8765/health` |

**Aktivierung:**

```bash
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

**Zugriff:** `http://192.168.0.70:8765`

### Methode 2: ngrok Internet-Zugriff (Global)

| Komponente         | Status | Befehl                                   |
| ------------------ | ------ | ---------------------------------------- |
| ngrok installiert  | ✅     | `ngrok --version`                        |
| Token konfiguriert | ✅     | `cat ~/.ngrok2/ngrok.yml`                |
| Server läuft       | ✅     | `ps aux \| grep tool_server`             |
| ngrok Tunnel aktiv | ✅     | `curl http://127.0.0.1:4040/api/tunnels` |

**Aktivierung:**

```bash
# Terminal 1: Server
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# Terminal 2: ngrok
ngrok http 8765 --region eu
```

**Zugriff:** `https://[NGROK_URL].ngrok.io` (Siehe ngrok Output)

### Methode 3: SSH Tunnel-Zugriff (Sicherste)

| Komponente            | Status | Befehl                                              |
| --------------------- | ------ | --------------------------------------------------- |
| SSH-Keys erstellt     | ✅     | `ls ~/.ssh/id_server*`                              |
| Public Key auf Server | ✅     | `ssh user@remote.host "cat ~/.ssh/authorized_keys"` |
| Server läuft          | ✅     | `ps aux \| grep tool_server`                        |
| Tunnel verbunden      | ✅     | `ssh -L 8765:localhost:8765 user@remote.host -N &`  |

**Aktivierung:**

```bash
# Terminal 1: Server
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# Terminal 2: SSH Tunnel
ssh -L 8765:localhost:8765 user@remote.host -N &
```

**Zugriff:** `http://localhost:8765`

---

## 🧪 Validierungsbefehle

### Schnell-Tests

```bash
#!/bin/bash
# save as: test_network.sh

echo "🔍 Netzwerk-Validierung"
echo "======================="

echo ""
echo "1️⃣ Server läuft?"
ps aux | grep tool_server | grep -v grep && echo "✅ JA" || echo "❌ NEIN"

echo ""
echo "2️⃣ Port 8765 gebunden?"
ss -tlnp | grep 8765 | grep -q 0.0.0.0 && echo "✅ JA (0.0.0.0:8765)" || echo "❌ NEIN"

echo ""
echo "3️⃣ Lokaler Health Check"
curl -s http://127.0.0.1:8765/health | jq . && echo "✅ OK" || echo "❌ FEHLER"

echo ""
echo "4️⃣ LAN Health Check"
curl -s http://192.168.0.70:8765/health | jq . && echo "✅ OK" || echo "❌ FEHLER"

echo ""
echo "5️⃣ Firewall Port offen?"
sudo ufw status | grep -q "8765" && echo "✅ JA" || echo "❌ NEIN"

echo ""
echo "6️⃣ ngrok Status"
curl -s http://127.0.0.1:4040/api/tunnels | jq '.tunnels[0].public_url' 2>/dev/null && echo "✅ Aktiv" || echo "❌ Nicht aktiv"

echo ""
echo "========================"
echo "Validierung abgeschlossen!"
```

### Detaillierte Diagnostik

```bash
echo "🔧 Detaillierte Diagnostik"
echo "============================"

# Alle Prozesse die Port 8765 nutzen
echo "Prozesse auf Port 8765:"
sudo lsof -i :8765 -P -n

# Firewall-Regeln
echo ""
echo "Firewall-Regeln:"
sudo ufw show added | grep 8765

# Routing-Tabelle
echo ""
echo "Routing:"
ip route show

# ARP-Cache
echo ""
echo "ARP-Cache (Netzwerk-Hosts):"
arp -a

# DNS-Auflösung
echo ""
echo "DNS:"
nslookup 192.168.0.70
```

---

## 📞 Support & Troubleshooting

### Problem: "Connection refused" auf LAN

**Symptome:**

```
curl: (7) Failed to connect to 192.168.0.70 port 8765: Connection refused
```

**Lösungen:**

1. Server läuft? → `ps aux | grep tool_server`
2. Port korrekt? → `ss -tlnp | grep 8765`
3. Firewall blockiert? → `sudo ufw status | grep 8765`
4. Richtige IP? → `hostname -I`

### Problem: "Network is unreachable"

**Symptome:**

```
curl: (7) Failed to connect to 192.168.0.70 port 8765: Network is unreachable
```

**Lösungen:**

1. Netzwerk-Konnektivität → `ping 192.168.0.1`
2. Gerät im selben Netz? → `ip route show`
3. IP-Adresse statisch? → `ip addr show`

### Problem: ngrok "Failed to authenticate"

**Symptome:**

```
Error: Failed to authenticate your account with token
```

**Lösungen:**

1. Token gültig? → ngrok Dashboard überprüfen
2. Token neu setzen → `ngrok config add-authtoken "TOKEN"`
3. Konfiguration → `cat ~/.ngrok2/ngrok.yml`

### Problem: SSH Tunnel bricht ab

**Symptome:**

```
Connection closed by remote host
```

**Lösungen:**

1. SSH-Key Test → `ssh -i ~/.ssh/id_server user@remote.host`
2. autossh verwenden → `autossh -M 20000 -L 8765:localhost:8765 user@remote.host -N`
3. Timeout-Werte → ServerAliveInterval in ~/.ssh/config

---

## 📚 Referenzen

### Befehle-Übersicht

| Befehl                                    | Beschreibung       |
| ----------------------------------------- | ------------------ |
| `sudo ufw status`                         | Firewall-Status    |
| `sudo ufw allow 8765/tcp`                 | Port öffnen        |
| `ss -tlnp \| grep 8765`                   | Port-Status        |
| `ps aux \| grep tool_server`              | Prozess überprüfen |
| `curl http://192.168.0.70:8765/health`    | Health Check       |
| `ngrok http 8765`                         | ngrok Tunnel       |
| `ssh -L 8765:localhost:8765 user@host -N` | SSH Tunnel         |

### Externe Ressourcen

- [UFW Documentation](https://wiki.ubuntu.com/UncomplicatedFirewall)
- [ngrok Documentation](https://ngrok.com/docs)
- [SSH Documentation](https://man.openbsd.org/ssh)
- [RFC 3986 - URIs](https://tools.ietf.org/html/rfc3986)

---

## ✅ Checkliste für Netzwerk-Setup

- [x] Switch/Router konfiguriert (192.168.0.70)
- [x] Firewall Port 8765 freigegeben
- [x] ngrok Token eingerichtet
- [x] SSH-Keys generiert & konfiguriert
- [x] Health Endpoints getestet
- [x] Alle 3 Zugriffsmethoden validiert
- [x] Fehlerbehandlung dokumentiert
- [x] Monitoring aufgesetzt

---

**Dokument Version:** 1.0.0
**Letzte Aktualisierung:** 25. November 2025
**Status:** ✅ Produktionsfertig
