# 🚀 ELION Hyper-Dashboard – Deployment Progress

**Status:** Phase 0 in Bearbeitung (Schritt 1/4 ✅)
**Ziel:** https://hyperdashboard-one.de produktiv
**Datum:** 17. Dezember 2025

---

## ✅ Phase 0: Infrastruktur-Setup

### Schritt 1: Server gemietet ✅ DONE

**Provider:** Hetzner (CPX32)
**Server-Name:** cpx32 (ubuntu-8gb-hel1-1)

| Property        | Wert                                         |
| --------------- | -------------------------------------------- |
| **Public IPv4** | `77.42.23.168`                               |
| **IPv6**        | `2a01:4f9:c013:7352::/64`                    |
| **CPU**         | 4 vCPU                                       |
| **RAM**         | 8 GB                                         |
| **Disk**        | 160 GB (lokal)                               |
| **Region**      | Helsinkii (HEL)                              |
| **Reverse DNS** | `static.168.23.42.77.clients.your-server.de` |
| **Kosten**      | €12,59/Monat                                 |
| **OS**          | Ubuntu 20.04 LTS (Standard)                  |

✅ **Status:** Server aktiv und SSH-erreichbar

---

### Schritt 2: Domain registrieren ⏳ TODO

**Domain:** `hyperdashboard-one.de`

**Aktion:**

```
1. Öffne Registrar (Namecheap, GoDaddy, Ionos, Hetzner, etc.)
2. Suche: hyperdashboard-one.de
3. Kaufe für ≥1 Jahr
4. Notiere Registrar-Login
5. Warte auf Aktivierung (meist sofort)
```

**Geschätzte Dauer:** 5–10 Min.
**Nach diesem Schritt:** Registrar-Account mit Domain-Zugang

---

### Schritt 3: DNS A-Record setzen ⏳ TODO

**Ziel:** `hyperdashboard-one.de` → `77.42.23.168`

**Im Registrar:**

```
Type: A
Name: @  (oder leer)
Value: 77.42.23.168
TTL: 3600 (Standard)

→ SAVE
```

**Verifikation (nach 5–15 Min):**

```bash
nslookup hyperdashboard-one.de
# Sollte zeigen: 77.42.23.168
```

**Geschätzte Dauer:** 2–3 Min. + 5–15 Min. DNS-Propagation

---

### Schritt 4: SSH-Verbindung testen ⏳ TODO

**Lokal (auf deinem Laptop):**

#### Option A: Mit Hetzner SSH-Key (empfohlen)

```bash
# 1. Hetzner Dashboard öffnen
# 2. Server → SSH-Keys → Public Key herunterladen
# 3. Im Home speichern
mkdir -p ~/.ssh
# (Key speichern unter ~/.ssh/id_rsa oder ~/.ssh/hetzner_key)
chmod 600 ~/.ssh/hetzner_key

# 4. Verbinden
ssh -i ~/.ssh/hetzner_key root@77.42.23.168

# Oder mit Hostname (nach DNS-Propagation):
ssh -i ~/.ssh/hetzner_key root@hyperdashboard-one.de
```

#### Option B: Mit Root-Passwort (falls SSH-Key nicht verfügbar)

```bash
ssh root@77.42.23.168
# (Passwort eingeben, das Hetzner sendet)
```

#### Option C: SSH Config speichern (für später)

```bash
# Datei: ~/.ssh/config
cat >> ~/.ssh/config <<'SSH_CONFIG'
Host hyperdash
  HostName 77.42.23.168
  User root
  IdentityFile ~/.ssh/hetzner_key
  Port 22
SSH_CONFIG

# Dann später einfach:
ssh hyperdash
```

**Erfolgreich, wenn:**

```bash
root@ubuntu-8gb-hel1-1:~#
```

**Geschätzte Dauer:** 2–3 Min.

---

## 📋 Phase 0 – Checklist

```
☐ Schritt 1: Server gemietet ✅ DONE
  ├─ Server-IP: 77.42.23.168 ✅
  ├─ CPU: 4 vCPU ✅
  ├─ RAM: 8 GB ✅
  └─ SSH-Key heruntergeladen ⏳

☐ Schritt 2: Domain registrieren ⏳
  ├─ hyperdashboard-one.de gekauft ⏳
  └─ Registrar-Login bereit ⏳

☐ Schritt 3: DNS A-Record ⏳
  ├─ A-Record erstellt (@  → 77.42.23.168) ⏳
  └─ DNS propagiert (nslookup test) ⏳

☐ Schritt 4: SSH testen ⏳
  ├─ ssh root@77.42.23.168 funktioniert ⏳
  └─ Ready für Phase 1 ⏳
```

---

## 🎯 Nächste Aktion (JETZT)

### Quick Checklist (nächste 30 Min):

```bash
# 1. SSH-Key vorbereiten (lokal)
mkdir -p ~/.ssh
# → Key von Hetzner speichern unter ~/.ssh/hetzner_key
chmod 600 ~/.ssh/hetzner_key

# 2. SSH testen
ssh -i ~/.ssh/hetzner_key root@77.42.23.168

# 3. Am Server: Bestätigung
uname -a
# Sollte zeigen: Linux ubuntu-8gb-hel1-1 5.x.x-xx-generic ...

# 4. Zurück lokal: Domain registrieren + DNS setzen
# (Siehe Schritt 2 + 3 oben)

# 5. Nach 5–15 Min DNS-Propagation: SSH mit Domain testen
ssh -i ~/.ssh/hetzner_key root@hyperdashboard-one.de
```

---

## 📚 Dokumentation (parallel lesen)

| Datei                                                              | Verwendung                 |
| ------------------------------------------------------------------ | -------------------------- |
| [PRE_DEPLOYMENT_CHECKLIST.md](./PRE_DEPLOYMENT_CHECKLIST.md)       | Phase 0 Details + Commands |
| [PRODUCTION_DEPLOYMENT_STEPS.md](./PRODUCTION_DEPLOYMENT_STEPS.md) | Phase 1 (nach SSH)         |
| [DEPLOYMENT_OPENA4.md](./DEPLOYMENT_OPENA4.md)                     | Nginx + SSL Details        |

---

## ⏱️ Zeitplan Rest heute

| Zeit                 | Task                                      | Dauer    |
| -------------------- | ----------------------------------------- | -------- |
| **Jetzt**            | Domain registrieren + DNS A-Record        | 10 Min   |
| **+10 Min**          | DNS propagieren (warten)                  | 5–15 Min |
| **+25 Min**          | SSH testen + Server vorbereiten           | 5 Min    |
| **~35–45 Min**       | **Phase 0 COMPLETE** ✅                   |          |
| **+45 Min**          | **Phase 1 starten** (am Server)           | 60 Min   |
| **~2 Stunden total** | **https://hyperdashboard-one.de LIVE** 🚀 |          |

---

## 🔐 Server-Credentials (sicher verwahren!)

```
Server: ubuntu-8gb-hel1-1
IP: 77.42.23.168
Domain (kommend): hyperdashboard-one.de
User: root
SSH-Key: ~/.ssh/hetzner_key
Region: Helsinki (HEL)
Provider: Hetzner
```

⚠️ **Sicherheit:** Nicht in Git committen, .env für Secrets verwenden!

---

## 🚀 Nach Phase 0 (wenn SSH funktioniert)

```bash
# Am Server:
ssh root@hyperdashboard-one.de

# Dann:
cd /var/www
git clone https://github.com/jokicdanijel/Gesamtprojekt-start.git
cd Gesamtprojekt-start

# Phase 1 starten (12 Schritte)
# Siehe: PRODUCTION_DEPLOYMENT_STEPS.md
```

---

**Status:** � Phase 1 LIVE (90% done) – Infrastructure Ready!
**Letzter Checkpoint:** HTTPS unter https://hyperdashboard-one.de ✅
**ETA bis Agents Live:** ~30 Min (Services starten)

---

## 🎯 Phase 1 – LIVE! (17. Dezember 2025)

**✅ Abgeschlossen:**

1. System-Updates + Pakete (Nginx, Docker, Certbot)
2. DNS propagiert: hyperdashboard-one.de → 77.42.23.168
3. Nginx Reverse Proxy (mit /opena1–/opena4 routing)
4. SSL-Zertifikat (selbst-signiert, später Let's Encrypt)
5. Firewall UFW aktiv (22, 80, 443)
6. Code deployed zu /var/www/hyperdashboard
7. .env Template erstellt

**🌐 Infrastruktur Live:**

```
https://hyperdashboard-one.de     ← Domain aktiv ✅
  ├─ HTTP → HTTPS redirect
  ├─ Self-signed SSL cert
  ├─ Nginx routing konfiguriert
  └─ Agents will route over /opena1–/opena4
```

**⏳ Nächstes (30 Min):**

1. SSH: `ssh root@hyperdashboard-one.de`
2. Edit: `nano /var/www/hyperdashboard/.env` (API-Keys)
3. Start: `cd /var/www/hyperdashboard && bash bin/ops.sh start`
4. Live: Agenten verfügbar unter https://hyperdashboard-one.de

**🎯 Dann PRODUCTION LIVE!** 🚀
