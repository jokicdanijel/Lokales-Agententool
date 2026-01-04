# PORTIER 3.0: Hetzner Auto-Deploy - Quick Start

## ✅ Implementiert

### 1. N8N Workflow (Vollständig)
**Datei:** [n8n-workflows/agent-html-generator.json](../n8n-workflows/agent-html-generator.json)

**Pipeline:**
```
Generate → Save → Restart Local → Package → Upload → Deploy Hetzner
```

**Features:**
- ✅ Base64-sicheres HTML-Encoding
- ✅ Automatische Tar-Paketierung
- ✅ SCP-Upload mit Credentials
- ✅ Remote SSH-Deployment
- ✅ opena20 Restart auf Hetzner
- ✅ Cleanup temporärer Dateien

### 2. Bash Deploy-Script
**Datei:** [scripts/deploy_dashboards_hetzner.sh](../scripts/deploy_dashboards_hetzner.sh)

**Features:**
- ✅ Validierung (Dashboards, Host, SSH-Keys)
- ✅ Timestamped Tar-Archive
- ✅ SCP-Upload
- ✅ Remote-Deployment mit Fallbacks
- ✅ Colored Output & Fehlerbehandlung

### 3. Dokumentation
**Datei:** [docs/HETZNER_AUTO_DEPLOY.md](../docs/HETZNER_AUTO_DEPLOY.md)

**Inhalte:**
- Setup-Anleitung (N8N + Bash)
- SSH Key Management
- Troubleshooting
- CI/CD Integration (GitHub/GitLab)
- Monitoring & Performance

---

## 🚀 Schnellstart

### Option A: N8N Workflow

```bash
# 1. N8N öffnen
xdg-open http://localhost:5678

# 2. Workflow importieren
# Settings → Import → n8n-workflows/agent-html-generator.json

# 3. Credentials anlegen
# Settings → Credentials → Add "SSH"
# Name: hetzner_server
# Host: your-server.hetzner.cloud
# SSH Key: [Private Key einfügen]

# 4. Workflow ausführen
# → "Execute Workflow"
```

### Option B: Bash Script

```bash
# 1. SSH Key Setup
ssh-copy-id root@your-server.hetzner.cloud

# 2. Host setzen
export HETZNER_HOST=your-server.hetzner.cloud

# 3. Deploy
bash scripts/deploy_dashboards_hetzner.sh
```

---

## 📋 Voraussetzungen

**Lokal:**
- ✅ 10 generierte Dashboards in `19.opena20_dashboard_agent/data/dashboard_pages/`
- ✅ SSH-Zugang zu Hetzner (Public Key Auth)
- ✅ N8N läuft auf `localhost:5678` (für Workflow-Option)

**Auf Hetzner:**
- ✅ PORTIER installiert unter `/opt/Gesamtprojekt/`
- ✅ opena20 läuft (Docker Compose oder ops.sh)
- ✅ Port 12349 erreichbar

---

## 🎯 Workflow-Details

### Nodes im N8N Workflow

| Node | Funktion | Output |
|------|----------|--------|
| **Manual Trigger** | Workflow-Start | - |
| **Docker Compose Start** | Agents starten (optional) | Service-Status |
| **Read Baseline** | system_baseline.yaml laden | YAML-String |
| **Parse Baseline** | Agents extrahieren | Agent-Objekte |
| **Generate HTML** | Dashboards erstellen | html_b64, target_path |
| **Save HTML to opena20** | Lokal speichern | Success-Message |
| **Restart opena20 (Local)** | Lokalen Server neu starten | Restart-Status |
| **Package Dashboards** | Tar-Archiv erstellen | /tmp/portier_dashboards_*.tar.gz |
| **Upload to Hetzner** | SCP-Upload | Upload-Bestätigung |
| **Deploy & Restart on Hetzner** | Remote-Deployment | Deploy-Status |

---

## 🔒 Sicherheit

### SSH Key Best Practices

```bash
# Key generieren (Ed25519, empfohlen)
ssh-keygen -t ed25519 -C "portier-deploy@hetzner" -f ~/.ssh/portier_hetzner

# Public Key auf Hetzner
ssh-copy-id -i ~/.ssh/portier_hetzner.pub root@HETZNER_HOST

# SSH Config (~/.ssh/config)
Host hetzner-portier
    HostName your-server.hetzner.cloud
    User root
    IdentityFile ~/.ssh/portier_hetzner
    ServerAliveInterval 60
```

### N8N Credentials

- **Niemals** Private Keys im Git committen
- Nutze N8N Credentials Store (verschlüsselt)
- Key-Rotation alle 90 Tage

---

## 📊 Monitoring

### Deployment-Status prüfen

```bash
# Local
curl http://localhost:12349/health

# Hetzner
curl https://HETZNER_HOST:12349/health

# Dashboard-Zugriff testen
curl https://HETZNER_HOST:12349/agent/opena16
```

### N8N Execution History

```
http://localhost:5678 → Executions
→ Zeigt alle Workflow-Runs mit Timestamps, Erfolg/Fehler, Node-Details
```

---

## 🐛 Troubleshooting

### "HETZNER_HOST nicht gesetzt"
```bash
export HETZNER_HOST=your-server.hetzner.cloud
# Oder in .env: echo "HETZNER_HOST=your-server.hetzner.cloud" >> .env
```

### "Permission denied (publickey)"
```bash
# SSH Key fehlt
ssh-copy-id root@HETZNER_HOST

# Test
ssh root@HETZNER_HOST "echo OK"
```

### "Keine Dashboards gefunden"
```bash
# Erst generieren
python3 scripts/generate_agent_dashboards.py

# Prüfen
ls -lh 19.opena20_dashboard_agent/data/dashboard_pages/
```

### "opena20 nicht gefunden auf Hetzner"
```bash
# SSH auf Hetzner
ssh root@HETZNER_HOST

# Pfad prüfen
ls -la /opt/Gesamtprojekt/19.opena20_dashboard_agent/

# opena20 Status
docker ps | grep opena20
# oder
systemctl status opena20
```

---

## 📈 Performance

**Typisches Deployment:**
- Dashboards generieren: ~2s (lokal)
- Tar-Archiv erstellen: <1s
- Upload (20 KB): ~0.5s (100 Mbit/s)
- Remote-Deployment: ~3-5s
- **Gesamt: ~7-10 Sekunden** 🚀

**Netzwerk-Traffic:**
- 10 Dashboards: ~20 KB (komprimiert)
- 100 Deploys/Tag: ~2 MB/Tag
- **Hetzner Free Traffic:** 20 TB/Monat → Praktisch kostenlos

---

## 🎁 Bonus: CI/CD Integration

### GitHub Actions

```yaml
- name: Deploy Dashboards
  env:
    HETZNER_HOST: ${{ secrets.HETZNER_HOST }}
  run: |
    mkdir -p ~/.ssh
    echo "${{ secrets.HETZNER_SSH_KEY }}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa
    bash scripts/deploy_dashboards_hetzner.sh
```

Siehe [docs/HETZNER_AUTO_DEPLOY.md](../docs/HETZNER_AUTO_DEPLOY.md) für vollständige CI/CD-Beispiele.

---

## ✅ Nächste Schritte

1. **Dashboards generieren:**
   ```bash
   python3 scripts/generate_agent_dashboards.py
   ```

2. **Deployment testen:**
   ```bash
   # Via Script
   export HETZNER_HOST=your-server.hetzner.cloud
   bash scripts/deploy_dashboards_hetzner.sh

   # Oder via N8N Workflow
   ```

3. **Verifizierung:**
   ```bash
   curl https://HETZNER_HOST:12349/agent/opena16
   ```

---

## 📚 Weitere Dokumentation

- **Vollständige Anleitung:** [docs/HETZNER_AUTO_DEPLOY.md](../docs/HETZNER_AUTO_DEPLOY.md)
- **N8N Workflow:** [n8n-workflows/agent-html-generator.json](../n8n-workflows/agent-html-generator.json)
- **Dashboard Generator:** [scripts/generate_agent_dashboards.py](../scripts/generate_agent_dashboards.py)
