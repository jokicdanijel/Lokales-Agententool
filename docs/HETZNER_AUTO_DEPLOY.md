# Hetzner Auto-Deploy: PORTIER Agent Dashboards

## Übersicht

Automatisches Deployment von generierten Agent-Dashboards auf Hetzner Production Server.

**2 Deployment-Methoden:**
1. **N8N Workflow** (automatisch, empfohlen für CI/CD)
2. **Bash Script** (manuell, für On-Demand Deploys)

---

## Methode 1: N8N Workflow (Automatisch)

### Workflow-Pipeline

```
Manual Trigger
    ↓
Docker Compose Start (optional)
    ↓
Read system_baseline.yaml
    ↓
Parse Agents
    ↓
Generate HTML (Base64)
    ↓
Save to opena20 (Local)
    ↓
Restart opena20 (Local)
    ↓
Package Dashboards (.tar.gz)
    ↓
Upload to Hetzner (SCP)
    ↓
Deploy & Restart on Hetzner (SSH)
```

### Setup

1. **N8N Credentials erstellen:**
   - N8N UI: Settings → Credentials → Add Credential
   - Typ: `SSH` oder `Generic Credential`
   - Name: `hetzner_server`
   - Host: `your-server.hetzner.cloud`
   - SSH Key: Private Key einfügen

2. **Workflow importieren:**
   ```bash
   # N8N UI öffnen
   xdg-open http://localhost:5678

   # Workflow importieren:
   # Settings → Import from File
   # Datei: n8n-workflows/agent-html-generator.json
   ```

3. **Ausführen:**
   - Workflow öffnen
   - "Execute Workflow" klicken
   - Pipeline läuft durch bis Hetzner-Deployment

### Nodes im Detail

#### 1. Package Dashboards
```bash
cd 19.opena20_dashboard_agent
tar -czf /tmp/portier_dashboards_$(date +%Y%m%d_%H%M%S).tar.gz \
    data/dashboard_pages/*.html
```

#### 2. Upload to Hetzner
```bash
scp /tmp/portier_dashboards_*.tar.gz \
    root@HETZNER_HOST:/tmp/portier_dashboards.tar.gz
```

#### 3. Deploy & Restart on Hetzner
```bash
ssh root@HETZNER_HOST '
    cd /opt/Gesamtprojekt/19.opena20_dashboard_agent
    tar -xzf /tmp/portier_dashboards.tar.gz -C .
    cd /opt/Gesamtprojekt
    docker-compose -f docker-compose.prod.yml restart opena20
    rm /tmp/portier_dashboards.tar.gz
'
```

---

## Methode 2: Bash Script (Manuell)

### Voraussetzungen

```bash
# SSH Key Setup (ohne Passwort-Prompt)
ssh-copy-id root@your-server.hetzner.cloud

# Oder: SSH Config (~/.ssh/config)
Host hetzner-portier
    HostName your-server.hetzner.cloud
    User root
    IdentityFile ~/.ssh/id_rsa
```

### Ausführung

```bash
# Umgebungsvariable setzen
export HETZNER_HOST=your-server.hetzner.cloud

# Deploy ausführen
bash scripts/deploy_dashboards_hetzner.sh
```

**Oder direkt mit Host:**
```bash
HETZNER_HOST=your-server.hetzner.cloud \
    bash scripts/deploy_dashboards_hetzner.sh
```

### Script-Ablauf

1. ✅ Validierung (Dashboards vorhanden, Host gesetzt)
2. 📦 Tar-Archiv erstellen (`/tmp/portier_dashboards_TIMESTAMP.tar.gz`)
3. 📤 Upload via SCP
4. 🔧 Remote-Deployment:
   - Entpacken in `/opt/Gesamtprojekt/19.opena20_dashboard_agent/data/`
   - opena20 Restart (Docker Compose/Docker/ops.sh)
   - Cleanup temporärer Dateien
5. ✅ Erfolgsmeldung + URLs

---

## Hetzner Server-Struktur

### Erwarteter Pfad
```
/opt/Gesamtprojekt/
├── 19.opena20_dashboard_agent/
│   ├── data/
│   │   ├── dashboard_pages/        ← Hier werden Dashboards deployt
│   │   │   ├── opena6_dashboard.html
│   │   │   ├── opena16_dashboard.html
│   │   │   └── ...
│   │   └── opena15_generated/      ← Optional: Premium-Dashboards
│   └── main_dashboard_agent.py
├── docker-compose.prod.yml
└── bin/ops.sh
```

### opena20 Routing

opena20 serviert Dashboards über:
```
http://HETZNER_HOST:12349/agent/{agent_id}
```

**Prioritäten:**
1. `data/opena15_generated/{agent_id}_dashboard.html` (Premium)
2. `data/dashboard_pages/{agent_id}_dashboard.html` (Standard)
3. Dynamische Generierung (Fallback)

---

## Sicherheit & Best Practices

### SSH Key Management

```bash
# Key generieren (falls nicht vorhanden)
ssh-keygen -t ed25519 -C "portier-deploy@hetzner"

# Public Key auf Hetzner installieren
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@HETZNER_HOST
```

### N8N Credentials

- **Niemals** Private Keys im Workflow hardcoden
- Nutze N8N Credentials Store
- Rotate Keys regelmäßig (alle 90 Tage)

### Firewall

```bash
# Auf Hetzner: Port 12349 nur für bekannte IPs
ufw allow from YOUR_IP to any port 12349

# Oder: Reverse Proxy (nginx/Caddy) mit TLS
# https://dashboard.portier.example.com → localhost:12349
```

---

## Troubleshooting

### Problem: "HETZNER_HOST nicht gesetzt"
```bash
# Lösung: .env erstellen
echo "HETZNER_HOST=your-server.hetzner.cloud" >> .env
source .env
```

### Problem: "Permission denied (publickey)"
```bash
# SSH Key fehlt oder falsch
ssh-add -l  # Keys anzeigen
ssh-add ~/.ssh/id_rsa  # Key hinzufügen

# Test
ssh root@HETZNER_HOST "echo OK"
```

### Problem: "opena20 konnte nicht neu gestartet werden"
```bash
# SSH auf Hetzner
ssh root@HETZNER_HOST

# Manual restart
cd /opt/Gesamtprojekt
docker-compose -f docker-compose.prod.yml restart opena20

# Logs prüfen
docker-compose logs -f opena20
```

### Problem: "Dashboards nicht sichtbar auf Hetzner"
```bash
# SSH auf Hetzner
ssh root@HETZNER_HOST

# Dateien prüfen
ls -lh /opt/Gesamtprojekt/19.opena20_dashboard_agent/data/dashboard_pages/

# Sollte enthalten:
# opena6_dashboard.html, opena8_dashboard.html, ...

# Test: Direkter Zugriff
curl http://localhost:12349/agent/opena16
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy PORTIER Dashboards

on:
  push:
    branches: [main]
    paths:
      - '19.opena20_dashboard_agent/data/dashboard_pages/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.HETZNER_SSH_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.HETZNER_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy to Hetzner
        env:
          HETZNER_HOST: ${{ secrets.HETZNER_HOST }}
        run: bash scripts/deploy_dashboards_hetzner.sh
```

### GitLab CI Example

```yaml
deploy:hetzner:
  stage: deploy
  only:
    - main
  before_script:
    - 'which ssh-agent || ( apt-get update -y && apt-get install openssh-client -y )'
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
  script:
    - export HETZNER_HOST=$HETZNER_HOST
    - bash scripts/deploy_dashboards_hetzner.sh
```

---

## Monitoring

### Deployment-Logs

```bash
# N8N: Execution History ansehen
http://localhost:5678 → Executions

# Script: Logs werden auf stdout ausgegeben
bash scripts/deploy_dashboards_hetzner.sh 2>&1 | tee deploy.log
```

### Health Check nach Deploy

```bash
# Local
curl http://localhost:12349/health

# Hetzner
curl https://HETZNER_HOST:12349/health
```

---

## Kosten & Performance

### Transfer-Größe

```bash
# Typische Größe (10 Dashboards):
# ~70 KB gesamt (7 KB pro Dashboard)
# Tar.gz komprimiert: ~20 KB

# Upload-Zeit (100 Mbit/s): < 1 Sekunde
# Deployment-Zeit gesamt: ~5-10 Sekunden
```

### Hetzner Traffic

- Dashboards: ~20 KB/Deploy
- Bei 100 Deploys/Tag: 2 MB/Tag = 60 MB/Monat
- Hetzner Free Traffic: 20 TB/Monat
- **→ Praktisch kostenlos**

---

## Nächste Schritte

1. **Teste lokales Deployment:**
   ```bash
   python3 scripts/generate_agent_dashboards.py
   ```

2. **Teste Hetzner-Upload (Dry-Run):**
   ```bash
   # Nur bis Upload, kein Deployment
   export HETZNER_HOST=your-server.hetzner.cloud
   # Kommentiere in Script die SSH-Befehle aus
   ```

3. **Produktiv-Deployment:**
   ```bash
   # Via Script
   bash scripts/deploy_dashboards_hetzner.sh

   # Oder via N8N Workflow
   # http://localhost:5678 → Execute Workflow
   ```

4. **Verifizierung:**
   ```bash
   curl https://HETZNER_HOST:12349/agent/opena16
   ```

---

## Support

Bei Problemen:
- Logs prüfen: `docker-compose logs opena20`
- Script debuggen: `bash -x scripts/deploy_dashboards_hetzner.sh`
- N8N Execution Details ansehen (Fehlermeldungen pro Node)
