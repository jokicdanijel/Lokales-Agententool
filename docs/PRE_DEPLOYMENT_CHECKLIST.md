# Pre-Deployment Checklist – ELION Hyper-Dashboard

**Ziel:** Externe URL https://hyperdashboard-one.de vollständig produktiv machen  
**Status:** Vorbereitung (Pre-Flight)  
**Geschätzte Dauer:** 30–60 Min. (Infrastruktur) + 30 Min. (Deployment)

---

## Phase 0: Infrastructure (Diese Schritte jetzt durchführen)

### ✅ Schritt 1: Server mieten (VPS)

**Empfohlen:** Linode, DigitalOcean, Hetzner, Vultr  
**Anforderungen:**
- **OS:** Ubuntu 20.04 LTS oder Debian 11+
- **RAM:** Mindestens 2 GB (4 GB empfohlen für 18+ Agenten + Docker)
- **Speicher:** 30 GB SSD (minimal), 50+ GB empfohlen
- **CPU:** 2 vCPU (minimal), 4 vCPU empfohlen
- **Netzwerk:** Unbegrenzter Traffic oder großes Limit
- **Region:** Europa (für latency-sensitive Anwendungen)

**Kosten (ungefähr):**
- Linode: ~$12–20 USD/Monat (2GB RAM)
- DigitalOcean: ~$6–12 USD/Monat (1–2GB RAM)
- Hetzner: ~€5–10 EUR/Monat (2GB RAM, Bonus: beste Raw Performance)

**Status nach diesem Schritt:**
- [ ] VPS gemietet und aktiviert
- [ ] Root SSH-Zugang erhalten (Private Key oder Password)
- [ ] Server-IP: `___.___.___.___ ` (notieren!)
- [ ] SSH-Port (Standard: 22) getestet

---

### ✅ Schritt 2: Domain registrieren

**Provider:** Domain.com, Namecheap, GoDaddy, Ionos, Hetzner, etc.

**Domain:** `hyperdashboard-one.de`

**Typen:**
- `.de` Domain (Registrar: Denic, über oben genannte Provider)
- Kosten: ~€1–5 EUR/Jahr
- Verfügbarkeit: **Jetzt prüfen!** https://www.namecheap.com/ oder Domain-Registrar

**Status nach diesem Schritt:**
- [ ] Domain registriert
- [ ] Domain gekauft und verlängert (≥1 Jahr)
- [ ] Registrar-Account zugänglich (Login Daten sicher ablegen)
- [ ] Nameserver erreichbar (sollte automatisch vom Registrar gesetzt sein)

---

### ✅ Schritt 3: DNS A-Record setzen

**Ziel:** `hyperdashboard-one.de` → `<SERVER_IP>` (Schritt 1)

**Vorgehensweise:**

1. **Registrar-Konto öffnen** (z.B. Namecheap, Ionos, GoDaddy)
2. **DNS / Nameserver bereich öffnen**
3. **A-Record eintragen:**
   - **Type:** A
   - **Name/Subdomain:** `@` (oder leer für Root-Domain)
   - **Value/Points to:** `<SERVER_IP_VON_SCHRITT_1>`
   - **TTL:** 3600 (oder Standard)

4. **Optional (für Zukunft):** Wildcard für alle Subdomains
   - **Type:** A
   - **Name:** `*`
   - **Value:** `<SERVER_IP_VON_SCHRITT_1>`
   - (Ermöglicht: `api.hyperdashboard-one.de`, `grafana.hyperdashboard-one.de`, etc.)

5. **Speichern & DNS-Propagation abwarten** (5–15 Min., manchmal bis 24h)

**Verifikation (lokal):**
```bash
# Nach 5–15 Min. testen:
nslookup hyperdashboard-one.de
# oder
dig hyperdashboard-one.de

# Sollte zeigen:
# hyperdashboard-one.de. IN A <SERVER_IP>
```

**Status nach diesem Schritt:**
- [ ] A-Record in DNS eingetragen
- [ ] DNS-Propagation verwaltet (nslookup zeigt Server-IP)
- [ ] Ping zur Domain funktioniert: `ping hyperdashboard-one.de`

---

### ✅ Schritt 4: SSH zum Server verbinden

**Vorabprüfung (lokal):**
```bash
# SSH Key-Pair prüfen (falls privat key vorhanden)
ls -la ~/.ssh/id_rsa  # oder id_ed25519

# Falls nicht: SSH Key generieren
ssh-keygen -t ed25519 -C "root@hyperdashboard-one.de" -f ~/.ssh/hyperdash_key

# Rechte setzen
chmod 600 ~/.ssh/hyperdash_key
```

**Verbindung zum Server:**
```bash
# Mit Private Key (empfohlen)
ssh -i ~/.ssh/hyperdash_key root@<SERVER_IP>

# Oder mit Password (falls nur PW vergeben)
ssh root@<SERVER_IP>

# Optional: SSH Config speichern (~/.ssh/config)
Host hyperdash
  HostName <SERVER_IP>
  User root
  IdentityFile ~/.ssh/hyperdash_key
  Port 22

# Dann später nur: ssh hyperdash
```

**Nach erfolgreicher Verbindung (am Server):**
```bash
# Server-Info prüfen
uname -a
lsb_release -a  # Ubuntu/Debian Version

# Aktualisierungen prüfen
apt update && apt upgrade -y

# Notwendige Pakete vorinstallieren (später automatisiert via bin/ops.sh)
# wird in Phase 1 gemacht
```

**Status nach diesem Schritt:**
- [ ] SSH-Verbindung zum Server erfolgreich
- [ ] Root-Zugang bestätigt
- [ ] Server antwortet auf Befehle
- [ ] OS + Version ermittelt
- [ ] SSH Key sicher gespeichert (lokal ~/.ssh/)

---

## Phase 1: Deployment (nachfolgende Schritte)

Siehe: [`docs/PRODUCTION_DEPLOYMENT_STEPS.md`](./PRODUCTION_DEPLOYMENT_STEPS.md)

**Schritt-by-Step von Phase 1:**
1. Systemische Pakete installieren (Nginx, Docker, Certbot)
2. DNS-Verifikation (sollte bereits von Phase 0, Schritt 3 done sein)
3. Code auf Server deployen (Git Clone)
4. .env konfigurieren (Secrets setzen)
5. Services starten (bin/ops.sh start)
6. Nginx reverse proxy konfigurieren (von DEPLOYMENT_OPENA4.md)
7. SSL-Zertifikat installieren (Let's Encrypt via Certbot)
8. Nginx mit HTTPS restarten
9. Externe Tests (curl + Browser)
10. Monitoring + Logging aufsetzen
11. Firewall-Regeln (UFW) konfigurieren
12. Verifikations-Checklist durchlaufen

---

## Zusammenfassung – Phase 0 Checkliste

| Schritt | Task | Status | Notizen |
|---------|------|--------|---------|
| 1 | VPS mieten + aktivieren | ⬜ TODO | Server-IP eintragen |
| 2 | Domain registrieren | ⬜ TODO | hyperdashboard-one.de |
| 3 | DNS A-Record setzen | ⬜ TODO | @ → Server-IP |
| 4 | SSH-Verbindung testen | ⬜ TODO | SSH Key sichern |

**Nach Phase 0:**
```
Server-IP: ___.___.___.___ 
Domain: hyperdashboard-one.de
SSH-Key: ~/.ssh/hyperdash_key
DNS: Propagiert (ja/nein)
SSH-Test: ✅/❌
```

---

## Nächste Schritte

1. **Checkliste Phase 0 abarbeiten** (Infrastruktur 30–60 Min.)
2. **SSH-Verbindung testen:** `ssh root@<SERVER_IP>`
3. **Dann:** Phase 1 aus `PRODUCTION_DEPLOYMENT_STEPS.md` starten (SSH am Server)
4. **Zeit für komplett Deploy:** ~1 Stunde (Pakete installieren, Code deployen, SSL-Cert, Tests)

---

**Dokumentation:**
- `docs/PRODUCTION_DEPLOYMENT_STEPS.md` – Schritt 1–12 Server-Setup + Deployment
- `docs/DEPLOYMENT_OPENA4.md` – Nginx-Konfiguration + SSL + Monitoring
- `docs/opena4_telegram.md` – API + Workflows-Dokumentation

**Support während Deployment:**
- Logs: `tail -100f /var/log/nginx/error.log`
- Health: `curl http://127.0.0.1:12349/health` (lokal am Server)
- Dashboard: `https://hyperdashboard-one.de` (extern nach Nginx-Setup)

---

**Status:** Ready für Phase 1 nach Phase 0 ✅  
**Gültig ab:** 17. Dezember 2025  
**Zielkonfiguration:** ELION Hyper-Dashboard produktiv unter https://hyperdashboard-one.de
