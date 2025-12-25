# 🚀 Lokalen Server für externe Geräte freigeben - QUICK START

## Was wurde bereits konfiguriert?

✅ **Tool Server auf Port 8765**

- HTTP REST API für Browser Automation
- Status: Läuft auf `0.0.0.0` (alle Netzwerk-Interfaces)
- Lokal erreichbar: `http://127.0.0.1:8765`
- LAN erreichbar: `http://192.168.0.70:8765`

---

## 3 Zugriffsmethoden - Wähle eine:

### 🟢 Methode 1: LAN-Zugriff (EMPFOHLEN für lokal)

**Schritt 1: Server starten**

```bash
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

**Schritt 2: Von anderem Gerät im selben Netzwerk zugreifen**

Auf iPhone/Laptop/PC im Browser:

```
http://192.168.0.70:8765
```

oder via Terminal:

```bash
curl http://192.168.0.70:8765/health
```

**Fertig!** Dein Server ist jetzt von allen Geräten im Netzwerk erreichbar.

---

### 🟡 Methode 2: Internet-Zugriff mit ngrok

**Schritt 1: ngrok installieren**

```bash
# macOS
brew install ngrok

# Linux
sudo apt install ngrok
```

**Schritt 2: Account erstellen & Token konfigurieren**

- Gehe zu: https://dashboard.ngrok.com/signup
- Kopiere deinen Token: https://dashboard.ngrok.com/auth/your-authtoken
- Konfiguriere Token:

```bash
ngrok config add-authtoken YOUR_TOKEN_HERE
```

**Schritt 3: Server und Tunnel starten**

Terminal 1 - Server:

```bash
python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765
```

Terminal 2 - ngrok Tunnel:

```bash
ngrok http 8765
```

**Schritt 4: Nutze die Public URL**

ngrok zeigt:

```
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8765
```

Zugriff von überall auf der Welt:

```
https://abc123def456.ngrok.io
```

oder:

```bash
curl https://abc123def456.ngrok.io/health
```

---

### 🔵 Methode 3: SSH Tunneling (sicherste Variante)

**Für Remote Server mit SSH:**

```bash
# Forward Tunnel (Remote → Local)
ssh -L 8765:localhost:8765 user@example.com -N

# oder Reverse Tunnel (Local → Remote)
ssh -R 8765:localhost:8765 user@example.com -N
```

---

## 🔍 Schnelle Überprüfung

**Ist der Service erreichbar?**

```bash
# Lokal
curl http://127.0.0.1:8765/health

# LAN (von anderem Gerät)
curl http://192.168.0.70:8765/health

# Manifest anschauen
curl http://192.168.0.70:8765/manifest
```

**Port überprüfen:**

```bash
ss -tlnp | grep 8765
netstat -tulpn | grep 8765
```

**Prozess überprüfen:**

```bash
ps aux | grep tool_server
```

---

## 📱 Test von verschiedenen Geräten

| Gerät                      | URL                                |
| -------------------------- | ---------------------------------- |
| Gleiches Netzwerk (iPhone) | `http://192.168.0.70:8765`         |
| Anderer Computer (LAN)     | `http://192.168.0.70:8765`         |
| Über Internet (ngrok)      | `https://abc123.ngrok.io`          |
| Remote Server (SSH)        | `localhost:8765` (nach SSH Tunnel) |

---

## 🔐 Mit Bearer Token (für Sicherheit)

```bash
curl -H "Authorization: Bearer sk_opena6_browser_v3_production" \
  http://192.168.0.70:8765/health
```

---

## 🛠️ Tools & Dokumentation

- **Interaktives Menu**: `bash setup_external_access.sh`
- **Konfigurationsprüfer**: `python3 LocalAgent-Pro/opena6/external_access_manager.py --method firewall`
- **Vollständige Docs**: `EXTERNAL_ACCESS_GUIDE.md`
- **Quick Reference**: `QUICK_REFERENCE_EXTERNAL_ACCESS.md`

---

## ✨ Das war's!

Dein lokaler Browser Agent Tool Server ist nun:

- ✅ Von lokalen Geräten erreichbar (LAN)
- ✅ Von überall über Internet zugänglich (ngrok)
- ✅ Sicher über SSH geschützt
- ✅ Mit vollständiger Dokumentation

**Nächster Schritt**: Integriere den Server in OpenWebUI!
