# 🚀 PORTIER 3.0 – Quick Start Guide

**Version:** 3.0.0
**Datum:** 2025-11-27
**Zielgruppe:** Entwickler, DevOps, neue Team-Mitglieder

---

## ⚡ 60-Sekunden-Start

```bash
# 1. Repository klonen
git clone <repo-url>
cd Gesamtprojekt

# 2. Environment bootstrappen
bin/env_bootstrap.sh  # Generiert .env mit Bearer-Token

# 3. Stack starten
bin/ops.sh start

# 4. Verifizieren
bin/ops.sh status | jq .

# 5. Dashboard öffnen
open http://127.0.0.1:12349/ui_index.html
```

**Fertig!** System läuft auf Ports 12344-12367.

---

## 📋 Voraussetzungen

### System

- **OS:** Ubuntu 25.04 (oder kompatibel)
- **Python:** 3.12+ (3.13 empfohlen)
- **Virtuelle Umgebung:** `venv313` oder `venv_local`
- **Git:** Für Repository-Management

### Tools

```bash
# Installieren
sudo apt update
sudo apt install -y python3 python3-venv python3-pip jq curl
```

### Python-Pakete

```bash
# Erstelle venv (falls nicht vorhanden)
python3 -m venv venv313
source venv313/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🏗️ Systemarchitektur (kompakt)

### Option-2-Flow (unveränderbar)

```
OpenAI → opena1 (12344) → opena2 (12345) → kordp (12346) → Tools
         ↓                ↓                 ↓
      Koordinator      Archivator     Koordinatport
```

### Agenten-Übersicht

| Agent         | Port        | Funktion                        | Ordner                     |
| ------------- | ----------- | ------------------------------- | -------------------------- |
| **opena1**    | 12344       | Koordinator (OpenAI-Connector)  | 1.opena1&2_portier         |
| **opena2**    | 12345       | Archivator (Safepoints)         | 1.opena1&2_portier         |
| **kordp**     | 12346       | Koordinatport (Dispatcher)      | 1.opena1&2_portier         |
| **opena3**    | 12347       | OpenWebUI Terminal              | 2.opena3_openwebui         |
| **opena4**    | 12346       | Telegram                        | 3.opena4_telegram          |
| **opena5**    | 12349       | VS Code Agent                   | 4.opena5_vscode            |
| **opena6-20** | 12350-12367 | Browser, E-Mail, WhatsApp, etc. | 5-20.opena\*               |
| **Dashboard** | 12349       | Hyper-Dashboard (UI)            | 19.opena20_dashboard_agent |

### Externes UI

- **OpenWebUI:** Port 8080 (exklusiv, **NIEMALS Backend**)

---

## 🎛️ Zentrale Befehle (`bin/ops.sh`)

```bash
# === LIFECYCLE ===
bin/ops.sh start          # Startet alle Services
bin/ops.sh stop           # Stoppt alle Services
bin/ops.sh restart        # Neustart

# === MONITORING ===
bin/ops.sh status         # JSON-Status aller Agenten
bin/ops.sh health         # Health-Check (HTTP)
bin/ops.sh logs           # Tail alle Logs

# === INTEGRATION ===
bin/ops.sh verify         # Integration-Tests
bin/ops.sh agents:register # Registry aktualisieren

# === DEVELOPMENT ===
bin/ops.sh ports          # Port-Belegung prüfen
bin/ops.sh clean          # Python-Cache löschen
bin/ops.sh reset-today    # Heute-Logs löschen
```

---

## 📁 Datenverzeichnisse

### ARCHIV (Runtime-History)

```
*/ARCHIV/YYYY/MM/DD/SP*.json     # Safepoints (Dashboard, opena3-20)
1.opena1&2_portier/archivp/...   # Kern-Archiv (opena1, opena2)
```

**Regeln:**

- ✅ Append-only (niemals löschen/ändern)
- ✅ YYYY/MM/DD Struktur (temporal)
- ✅ Unicode-Pfeil `→` (U+2192) in Dateinamen
- ❌ NIE in `configs/` (nur statische Configs!)

### Konfiguration

```
.env                  # Secrets (Bearer-Token, API-Keys)
config.py             # Python-Config (Ports, Timeouts)
agent_registry.json   # Agenten-Metadata
```

---

## 🧪 Testing & Validation

### Unit-Tests

```bash
# Alle Tests
pytest -v

# Spezifische Agenten
pytest -v 19.dashboard_agent/tests/test_archivator.py
pytest -v 19.dashboard_agent/tests/test_openwebui_agent.py
```

### Integration

```bash
# Stack-Verifikation
bin/verify_stack.sh

# Manuell
curl -s http://127.0.0.1:12344/health | jq .
curl -s http://127.0.0.1:12349/api/status/all | jq .
```

### Governance

```bash
# Compliance-Check
python scripts/governance_correction.py analyze

# Validierung
python scripts/governance_correction.py validate
```

---

## 🔧 Entwicklungs-Workflow

### Neuer Agent erstellen

```bash
# 1. Ordner anlegen (z.B. 21.opena22_myagent)
mkdir -p 21.opena22_myagent/{bin,data,tests}

# 2. FastAPI-Server (main_myagent.py)
cp 3.opena4_telegram/main_telegram_agent.py 21.opena22_myagent/main_myagent.py
# Anpassen: Port (12369), routes, business logic

# 3. Start-Script
cat > 21.opena22_myagent/bin/start_opena22.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/.."
nohup python3 main_myagent.py > logs/opena22.nohup.log 2>&1 &
echo $! > logs/opena22.pid
EOF
chmod +x 21.opena22_myagent/bin/start_opena22.sh

# 4. Registrieren
python scripts/register_agents.py

# 5. Starten
21.opena22_myagent/bin/start_opena22.sh
```

### Code-Konventionen

- **Python:** Black formatting (line-length 120)
- **Imports:** Relative wo sinnvoll
- **Logging:** Strukturiert (JSON wo möglich)
- **Secrets:** Nur via `.env`
- **Tests:** pytest + fixtures

---

## 🚨 Troubleshooting

### Service startet nicht

```bash
# Ports belegt?
bin/check_ports.sh

# Logs prüfen
tail -f logs/opena*.nohup.log

# Prozess hängt?
pkill -9 -f "python.*main_.*_agent.py"
```

### Dashboard 401 Unauthorized

```bash
# Token prüfen
bin/print_token.sh

# Token neu generieren
bin/env_bootstrap.sh --force
```

### Safepoints in configs/

```bash
# Governance-Fix
./GOVERNANCE_FIX_ARCHIV.sh  # DRY-RUN default
# Wenn OK:
DRY_RUN=false ./GOVERNANCE_FIX_ARCHIV.sh
```

### OpenWebUI unreachable

```bash
# Container läuft?
docker ps | grep open-webui

# Neustarten
docker-compose -f docker-compose.prod.yml restart open-webui
```

---

## 📚 Weitere Ressourcen

| Dokument                             | Inhalt                         |
| ------------------------------------ | ------------------------------ |
| **OPERATIONS.md**                    | Detaillierte Betriebsanleitung |
| **OPENWEBUI_INTEGRATION.md**         | opena3 + Adapter Setup         |
| **GOVERNANCE_VIOLATIONS_REPORT.md**  | Compliance-Regeln              |
| **.github/copilot-master-prompt.md** | System-Prompt für AI           |
| **TROUBLESHOOTING.md**               | Fehlerszenarien + Lösungen     |

---

## ✅ Success Criteria

Nach erfolgreicher Installation sollte gelten:

- [ ] `bin/ops.sh status` zeigt alle Agenten als `"healthy"`
- [ ] Dashboard auf http://127.0.0.1:12349/ui_index.html erreichbar
- [ ] `python scripts/governance_correction.py validate` → "System is fully compliant!"
- [ ] `bin/verify_stack.sh` → Alle Tests bestanden
- [ ] `find configs/ -name 'SP*.json'` → Leer (0 Dateien)
- [ ] `pytest -v` → Alle Tests grün

---

## 🤝 Support & Contribution

**Maintainer:** Danijel (ELION Team)
**Last Updated:** 2025-11-27
**License:** Internal Use Only

Bei Fragen: Siehe `.github/copilot-instructions.md` für AI-Unterstützung.
