# 🚀 ELION PORTIER 3.0 - Operations Guide

**Version:** 3.0  
**Datum:** 28. November 2025  
**Status:** ✅ Production-Ready (Post-Security-Incident)

---

## 📋 Inhaltsverzeichnis

1. [Quick Start](#quick-start)
2. [Systemarchitektur](#systemarchitektur)
3. [Service-Management](#service-management)
4. [Health-Monitoring](#health-monitoring)
5. [Testing & Validation](#testing--validation)
6. [Security & Tokens](#security--tokens)
7. [Troubleshooting](#troubleshooting)
8. [Development Workflow](#development-workflow)

---

## 🎯 Quick Start

### Erstmalige Einrichtung

```bash
# 1. Repository klonen (falls noch nicht geschehen)
cd /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt

# 2. .env erstellen (wenn nicht vorhanden)
bin/env_bootstrap.sh

# 3. OpenAI API Keys hinzufügen
nano .env
# Füge hinzu:
# OPENAI_API_KEY_OPENA1=sk-proj-...
# OPENAI_API_KEY_OPENA2=sk-proj-...
# OPENAI_API_KEY_OPENA20=sk-proj-...  # Für Dashboard AI Chat ✅

# 4. Services starten
bin/ops.sh start

# 5. Health-Check
bin/ops.sh health
```

### Täglicher Gebrauch

```bash
# Services starten
bin/ops.sh start

# Status prüfen
bin/ops.sh status

# Monitoring starten (Ctrl+C zum Beenden)
bin/ops.sh monitor

# E2E-Test durchführen
bin/ops.sh e2e

# Services stoppen
bin/ops.sh stop
```

---

## 🏗️ Systemarchitektur

### Core Services

| Service | Port | Rolle | OpenAI Key | Startskript |
|---------|------|-------|------------|-------------|
| **opena1** | 12344 | Coordinator (Option-2-Flow Entry) | OPENA1 ✅ | `1.opena1&2_portier/bin/start_opena1_with_key.sh` |
| **opena2** | 12345 | Archivator (Safepoint Storage) | OPENA2 ✅ | `1.opena1&2_portier/bin/start_opena2_with_key.sh` |
| **Dashboard** | 12349 | Agent Registry + SSE + UI + **AI Chat** | **OPENA20 ✅** | `bin/start_dashboard.sh` |

### Option-2-Flow (Sacred Path)

```
OpenAI → opena1 (12344) → opena2 (12345) → Tool
                ↓                ↓
         CMD Safepoint   RESP Safepoint
                ↓                ↓
            archivp_store/YYYY/MM/DD/
```

### Port-Policy (Unverhandelbar)

- **Backend-Services:** 12344-12399 (erlaubt)
- **UI-Only:** 8080 (OpenWebUI, kein Backend!)
- **External:** 3000 (OpenWebUI), 8188 (ComfyUI)

### Archiv-Struktur

```
1.opena1&2_portier/archivp_store/
├── YYYY/
│   └── MM/
│       └── DD/
│           ├── SP<timestamp>_src→dst_CMD.json
│           └── SP<timestamp>_src→dst_RESP.json
└── index.jsonl (append-only)
```

**Kritisch:** Unicode-Pfeil `→` (U+2192) ist **Pflicht** in Safepoint-Namen!

---

## 🔧 Service-Management

### bin/ops.sh - Zentrale Steuerung

```bash
# Alle Services starten
bin/ops.sh start
# → Lädt .env
# → Exportiert OPENAI_API_KEY für opena1/opena2
# → Startet Services via bin/start_opena*_with_key.sh
# → Health-Check nach Start

# Services stoppen
bin/ops.sh stop
# → Stoppt via PID-Files (logs/*.pid)
# → Fallback: pkill -f "opena*_app.py"

# Services neu starten
bin/ops.sh restart

# Health-Check (ohne Token)
bin/ops.sh health
# → curl http://127.0.0.1:12344/health
# → curl http://127.0.0.1:12345/health
# → curl http://127.0.0.1:12349/health

# Status (mit Bearer Token)
bin/ops.sh status
# → Vollständiger Agent-Status
# → Benötigt BEARER_TOKEN aus .env

# Live-Monitoring
bin/ops.sh monitor
# → Kontinuierliche Health-Checks (5s Intervall)
# → Ctrl+C zum Beenden

# Logs anzeigen
bin/ops.sh logs           # Letzte 100 Zeilen
bin/ops.sh logs:follow    # Live-Logs

# E2E-Test ausführen
bin/ops.sh e2e
# → Führt tests/e2e_option2_flow.sh aus
# → Validiert Option-2-Flow komplett
```

### Manuelle Service-Starts

```bash
# opena1 (mit Key aus .env)
cd 1.opena1&2_portier
bin/start_opena1_with_key.sh

# opena2 (mit Key aus .env)
cd 1.opena1&2_portier
bin/start_opena2_with_key.sh

# Dashboard
cd 19.opena20_dashboard_agent
nohup python3 main_dashboard.py > ../logs/dashboard.nohup.log 2>&1 &
```

### Service-Logs

```
logs/
├── opena1.nohup.log      # opena1 Startup + Runtime
├── opena2.nohup.log      # opena2 Startup + Safepoint-Ops
├── dashboard.nohup.log   # Dashboard Backend
└── health_monitor.log    # Automatisches Monitoring
```

---

## 🏥 Health-Monitoring

### Automatisches Monitoring

```bash
# Single Check
bin/health_monitor.sh once

# Daemon-Modus (kontinuierlich)
bin/health_monitor.sh daemon

# Mit Custom-Einstellungen
CHECK_INTERVAL=60 ALERT_THRESHOLD=5 bin/health_monitor.sh daemon

# Als systemd-Service (optional)
sudo cp systemd/elion-health-monitor.service /etc/systemd/system/
sudo systemctl enable elion-health-monitor
sudo systemctl start elion-health-monitor
```

### Monitoring-Features

- **Continuous Checks:** Alle 30s (konfigurierbar)
- **Alert Threshold:** 3 Fehler → Notification
- **System Notifications:** via `notify-send` (Desktop)
- **Webhook Support:** `WEBHOOK_URL` für externe Alerts
- **State Persistence:** `.runtime/health_state.json`

### Health-Endpoints

```bash
# opena1
curl -s http://127.0.0.1:12344/health | jq .
# → {status, service, role, openai_key_present, openai_fp}

# opena2
curl -s http://127.0.0.1:12345/health | jq .
# → {status, service, role, entries, openai_key_present}

# Dashboard
curl -s http://127.0.0.1:12349/health | jq .
# → {service, status, strict, timestamp}
```

---

## 🧪 Testing & Validation

### E2E Option-2-Flow Test

```bash
# Vollständiger Test
bin/ops.sh e2e

# Oder direkt:
tests/e2e_option2_flow.sh
```

**Test-Ablauf:**
1. **Preconditions:** Health-Check opena1/opena2/Dashboard
2. **Flow-Trigger:** POST zu `/log/opena1` mit Test-Request
3. **Safepoint-Verifikation:** Prüfe `archivp_store/YYYY/MM/DD/`
4. **Validation:** Schema, Unicode-Pfeil, Request-ID

**Erfolgskriterien:**
- ✅ opena1/opena2 Health OK + Keys present
- ✅ Request akzeptiert (HTTP 200)
- ✅ Safepoint in `archivp_store/` gespeichert
- ✅ Korrekte Struktur: `src=kordp`, `dst=archivp`, `kind=LOG`

### Dashboard AI Chat Test (NEU ✅)

```bash
# OpenAI-Integration von opena20 testen
# MODEL: gpt-3.5-turbo (DEFAULT für gesamtes Dashboard)
# KEINE Token-Begrenzung
curl -X POST http://127.0.0.1:12349/api/ai/chat \
  -H "Authorization: Bearer $(grep BEARER_TOKEN .env | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Was ist ELION Hyper-Dashboard?",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7
  }' | jq .

# Erwartete Response:
# {
#   "strict": true,
#   "message": "Was ist ELION Hyper-Dashboard?",
#   "response": "ELION Hyper-Dashboard ist ein FastAPI-basiertes... [VOLLSTÄNDIG, KEIN LIMIT]",
#   "model": "gpt-3.5-turbo",
#   "usage": {
#     "prompt_tokens": 25,
#     "completion_tokens": 1500,  // Kann unbegrenzt sein
#     "total_tokens": 1525
#   }
# }
#
# WICHTIG:
# - Model: gpt-3.5-turbo (DEFAULT für Dashboard)
# - KEINE Token-Begrenzung mehr
# - Response vollständig ohne Truncation
```

### Unit-Tests

```bash
# Archivator-Tests
cd 19.opena20_dashboard_agent
python3 -m pytest tests/test_archivator.py -v

# OpenWebUI-Tests
python3 -m pytest tests/test_openwebui_agent.py -v
```

### Integration-Verification

```bash
bin/ops.sh verify
# → Port-Checks (12344-12350, 8080)
# → Health-Checks (alle Services)
# → Option-2-Flow Test
# → Safepoint-Count Validation
```

---

## 🔐 Security & Tokens

### .env Struktur

```bash
# Dashboard/Admin
DASHBOARD_ADMIN_TOKEN=<uuid>
BEARER_TOKEN=<uuid>

# OpenAI Keys (REQUIRED)
OPENAI_API_KEY_OPENA1=sk-proj-...
OPENAI_API_KEY_OPENA2=sk-proj-...
OPENAI_API_KEY_OPENA20=sk-proj-...  # Dashboard AI Chat ✅
OPENAI_API_KEY=sk-proj-...  # Default fallback

# Ports
DASHBOARD_PORT=12349
OPENA1_PORT=12344
OPENA2_PORT=12345
KORDP_PORT=12346

# URLs
DASHBOARD_URL=http://127.0.0.1:12349
ARCHIVATOR_URL=http://127.0.0.1:12345
```

### Token-Rotation (Security Incident Protocol)

**Falls API-Keys exponiert:**

1. **SOFORT OpenAI-Keys rotieren:** https://platform.openai.com/api-keys
2. **.env aktualisieren** (neue Keys eintragen)
3. **Services neu starten:** `bin/ops.sh restart`
4. **Validation:** `bin/ops.sh e2e`
5. **Incident dokumentieren:** `SECURITY_INCIDENT_<date>.md`

### Secrets Redaction

- **opena1/opena2:** Automatische Redaction in Safepoints (`_redact_secrets()`)
- **Niemals:** API-Keys in Git committen
- **.gitignore:** `.env`, `.env.local`, `.env.*.local` geschützt

---

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. "openai_key_present: false"

**Ursache:** Services wurden ohne ENV-Export gestartet

**Lösung:**
```bash
bin/ops.sh stop
bin/ops.sh start  # Lädt Keys aus .env automatisch
```

#### 2. "Port 8080 ist verboten"

**Ursache:** Port-Policy Middleware in opena1/Dashboard

**Lösung:** Port 8080 ist **nur für OpenWebUI UI**, nicht für Backend!

#### 3. "Keine Safepoints gespeichert"

**Ursache:** Duplicate `/store/archivp` Endpoint (Bug behoben 28.11.2025)

**Lösung:** Aktuelle Version verwenden, opena2 neu starten

#### 4. "401 Unauthorized" bei `/api/status/all`

**Ursache:** Fehlender/falscher Bearer Token

**Lösung:**
```bash
# Token aus .env holen
export TOKEN=$(grep '^BEARER_TOKEN=' .env | cut -d= -f2 | tr -d '"')

# Request mit Token
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:12349/api/status/all
```

### Debug-Commands

```bash
# Prozesse prüfen
ps aux | grep -E "(opena|dashboard)" | grep -v grep

# Ports prüfen
bin/check_ports.sh

# Logs live verfolgen
bin/ops.sh logs:follow

# Health-Status detailliert
curl -s http://127.0.0.1:12344/health | jq .
curl -s http://127.0.0.1:12345/health | jq .

# Letzten Safepoint prüfen
find 1.opena1\&2_portier/archivp_store/ -name "*.json" -type f | sort | tail -1 | xargs cat | jq .
```

---

## 💻 Development Workflow

### Branch-Strategie

- **main:** Production-Stable
- **masterprompt-v1:** Current Development (Master-Prompts Integration)
- **feature/*:** Feature-Branches

### Code-Qualität

```bash
# Formatting (Black)
black --line-length 120 .

# Linting (Flake8)
flake8 --max-line-length=120 --ignore=E203,W503 .

# Type-Checking (optional)
mypy --strict main_dashboard.py
```

### Pre-Commit Workflow

```bash
# 1. Tests
python3 -m pytest -v

# 2. E2E-Test
bin/ops.sh e2e

# 3. Code-Quality
black . && flake8 .

# 4. Commit
git add .
git commit -m "feat: ..."
git push origin masterprompt-v1
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml (Beispiel)
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup
        run: |
          bin/env_bootstrap.sh
          echo "OPENAI_API_KEY_OPENA1=${{ secrets.OPENAI_KEY }}" >> .env
          echo "OPENAI_API_KEY_OPENA2=${{ secrets.OPENAI_KEY }}" >> .env
      - name: Start Services
        run: bin/ops.sh start
      - name: E2E Test
        run: bin/ops.sh e2e
      - name: Stop Services
        run: bin/ops.sh stop
```

---

## 📚 Weitere Dokumentation

- **Architektur:** `.github/copilot-master-prompt.md`
- **Master-Prompts:** `1.opena1&2_portier/knowledge/prompts/`
- **API-Docs:** `docs/OPENWEBUI_API.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING.md`
- **System-Scan:** `SYSTEM_SCAN_2025-11-27.md`
- **Security-Incident:** `SECURITY_INCIDENT_2025-11-28.md`

---

## 🎯 Production Checklist

Vor Deployment:

- [ ] `.env` vollständig ausgefüllt (Keys, Tokens, Ports)
- [ ] Services starten: `bin/ops.sh start`
- [ ] Health-Check: `bin/ops.sh health` → Alle ✅
- [ ] E2E-Test: `bin/ops.sh e2e` → BESTANDEN
- [ ] Monitoring aktiv: `bin/health_monitor.sh daemon &`
- [ ] Logs rotierend konfiguriert (`logrotate`)
- [ ] Backup-Strategie für `archivp_store/`
- [ ] Security: Keys nie in Git, `.env` in `.gitignore`

---

**Maintainer:** Danijel (ELION Team)  
**Support:** Siehe `docs/TROUBLESHOOTING.md`  
**License:** Internal Use Only

**Last Updated:** 28. November 2025
