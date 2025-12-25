# 🚀 Quick Reference - Server Externe Freigabe

## Instant 5-Minuten Setup

### 1️⃣ LAN-Zugriff (Für lokales Netzwerk)

```bash
# Terminal öffnen
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui

# Server starten auf 0.0.0.0
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# In anderem Terminal: Lokale IP ermitteln
ip a | grep "inet " | grep -v 127.0.0.1
# Ergebnis: 192.168.0.70

# Von Handy/Laptop im selben Netz:
# Browser: http://192.168.0.70:8765
# oder: curl http://192.168.0.70:8765/health
```

✅ **Fertig!** Server läuft lokal.

---

### 2️⃣ Internet-Zugriff (ngrok)

```bash
# 1. ngrok installieren (einmalig)
brew install ngrok      # macOS
# oder: apt install ngrok  # Linux

# 2. Token abrufen (einmalig)
# https://dashboard.ngrok.com/signup
# https://dashboard.ngrok.com/auth/your-authtoken

# 3. Token konfigurieren (einmalig)
ngrok config add-authtoken YOUR_TOKEN

# 4. Terminal 1: Server starten
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# 5. Terminal 2: ngrok Tunnel
ngrok http 8765

# Output: Forwarding https://abc123.ngrok.io -> http://localhost:8765

# Von überall auf der Welt:
# Browser: https://abc123.ngrok.io
# oder: curl https://abc123.ngrok.io/health
```

✅ **Fertig!** Server ist im Internet erreichbar.

---

### 3️⃣ SSH Tunneling (Sicher)

```bash
# Forward Tunnel (Remote → Local)
ssh -L 8765:localhost:8765 user@example.com -N

# Reverse Tunnel (Local → Remote)
ssh -R 8765:localhost:8765 user@example.com -N

# Mit SSH Key
ssh -i ~/.ssh/id_rsa -L 8765:localhost:8765 user@example.com -N
```

✅ **Fertig!** Sichere Verbindung etabliert.

---

## 🔧 Interaktive Setup

### Automatisiertes Menü

```bash
# Wechsel ins Verzeichnis
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui

# Starte das Setup-Script
bash setup_external_access.sh
```

Wähle dann aus dem Menü:

1. LAN-Zugriff
2. ngrok Setup
3. SSH Tunneling
4. Konfiguration überprüfen
5. Services neu starten

---

## 📱 Testing

### Lokale Tests

```bash
# Health Check
curl http://127.0.0.1:8765/health

# Manifest
curl http://127.0.0.1:8765/manifest

# Status
curl http://127.0.0.1:8765/status
```

### LAN Tests (von anderem Gerät)

```bash
curl http://192.168.0.70:8765/health
```

### Internet Tests (mit ngrok)

```bash
curl https://abc123.ngrok.io/health
curl https://abc123.ngrok.io/manifest
```

---

## 🔍 Diagnostik

```bash
# Port überprüfen
ss -tlnp | grep 8765
netstat -tulpn | grep 8765

# Prozess finden
ps aux | grep tool_server

# Service neu starten
pkill -f tool_server.py
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765

# ngrok Status
curl http://127.0.0.1:4040/api/tunnels | jq

# Firewall Status
sudo ufw status
sudo iptables -L -n | grep 8765
```

---

## 🛡️ Sicherheit

### Bearer Token verwenden

```bash
curl -H "Authorization: Bearer sk_opena6_browser_v3_production" \
  http://192.168.0.70:8765/health
```

### Firewall freigeben

```bash
# Linux (UFW)
sudo ufw allow 8765/tcp
sudo ufw reload

# Linux (iptables)
sudo iptables -A INPUT -p tcp --dport 8765 -j ACCEPT
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

---

## 📊 Vergleichstabelle

| Methode | Latenz | Sicherheit         | Kosten      | Einrichtung |
| ------- | ------ | ------------------ | ----------- | ----------- |
| LAN     | <5ms   | ⚠️ Mittel          | Kostenlos   | 5 Min       |
| ngrok   | ~50ms  | ✅ HTTPS           | Kostenlos\* | 10 Min      |
| SSH     | ~20ms  | ✅✅ Verschlüsselt | Kostenlos   | 15 Min      |

\*ngrok Free: 1x pro 40 Minuten neue URL

---

## 📌 Wichtige Ports

- **8765** - Tool Server (Browser Agent)
- **12350** - Browser Agent Service
- **12349** - Compute Agent (opena5)
- **3000** - OpenWebUI
- **4040** - ngrok Dashboard

---

## 🆘 Häufige Probleme

### "Connection refused"

```bash
# Service läuft nicht
ps aux | grep tool_server

# Neu starten:
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

### "Port bereits in Benutzung"

```bash
# Finde Prozess
lsof -i :8765

# Beende ihn
kill -9 PID

# oder anderen Port nutzen:
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 9999
```

### "ngrok funktioniert nicht"

```bash
# Überprüfe Installation
which ngrok
ngrok --version

# Überprüfe Auth
cat ~/.ngrok2/ngrok.yml

# Test
ngrok http 8765 --log stdout
```

### "SSH Tunnel schließt sich"

```bash
# Mit autossh (auto-reconnect)
brew install autossh

# Starten
autossh -M 20000 -L 8765:localhost:8765 user@host -N
```

---

## 📚 Vollständige Dokumentation

Siehe: `EXTERNAL_ACCESS_GUIDE.md`

```bash
cat EXTERNAL_ACCESS_GUIDE.md
```

---

## 🚀 Next Steps

1. **LAN-Setup testen** → Browser öffnen: `http://192.168.0.70:8765`
2. **ngrok aktivieren** → Dauerhafter Internet-Zugriff
3. **SSH Tunnel** → Für sichere Remote-Verbindungen
4. **OpenWebUI Integration** → Mit externem Tool Server verbinden

---

## ⚡ Power User Commands

```bash
# Alle Services starten
./setup_external_access.sh

# Konfiguration überprüfen
python3 LocalAgent-Pro/opena6/external_access_manager.py --method firewall

# ngrok Diagnose
ngrok diagnose

# ngrok mit Rate Limiting
ngrok http 8765 --rate-limit 100r/m

# SSH mit Logging
ssh -v -L 8765:localhost:8765 user@host -N

# Port Forwarding überprüfen
sudo netstat -tulpn | grep LISTEN
```

---

**Happy Server Sharing! 🎉**
