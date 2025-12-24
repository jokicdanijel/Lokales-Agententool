# 🏗️ AGENT STRUCTURE MAPPING

**Kanonische Referenz:** OPENA1-OPENA21
**Root Verzeichnis:** `Gesamtprojekt/`
**Status:** ✅ VERIFIED 2025-12-24

---

## 📍 PORT & FOLDER MAPPING (Kanonisch)

```
Agent   Port    Verzeichnis                          Type         Description
──────────────────────────────────────────────────────────────────────────────────
opena1  12344   1.opena1&2_portier/opena1            portier      PORTIER 3.0 Manager
opena2  12345   1.opena1&2_portier/opena2            portier      PORTIER 3.0 Backup
opena3  12347   2.opena3_openwebui                   ui           OpenWebUI Interface
opena4  12346   3.opena4_telegram                    connector    Telegram Bot
opena5  12350   4.opena5_vscode                      connector    VS Code Integration
opena6  12351   5.opena6_browser                     connector    Browser Automation
opena7  12352   6.opena7_email                       connector    Email Integration
opena8  12353   7.opena8_whatsapp                    connector    WhatsApp Integration
opena9  12354   8.opena9_telephone                   connector    Telephone/VoIP
opena10 12355   9.opena10_call_tracking              analytics    Call Tracking
opena11 12356   10.opena11_unlock                    security     Vault & Secrets
opena12 12357   11.opena12_social_media              connector    Social Media
opena13 12358   12.opena13_influencer                analytics    Influencer Analytics
opena14 12359   13.opena14_calendar                  connector    Calendar Integration
opena15 12360   14.opena15_html                      generator    HTML Generation
opena16 12361   15.opena16_shop                      ecommerce    E-Commerce Shop
opena17 12362   16.opena17_homepagecreator           generator    Website Builder
opena18 12363   17.opena18_CMR                       crm          CRM System
opena19 12364   18.opena19_Aktien&Crypto             finance      Stock & Crypto
opena20 12349   19.opena20_dashboard_agent           dashboard    Central Dashboard
opena21 12367   20.opena21_workflow                  workflow     Workflow Engine
```

---

## 📂 VERZEICHNIS-STRUKTUR

```
Gesamtprojekt/
├── 1.opena1&2_portier/
│   ├── opena1/              (Port 12344)
│   └── opena2/              (Port 12345)
├── 2.opena3_openwebui/      (Port 12347)
├── 3.opena4_telegram/       (Port 12346)
├── 4.opena5_vscode/         (Port 12350)
├── 5.opena6_browser/        (Port 12351)
├── 6.opena7_email/          (Port 12352)
├── 7.opena8_whatsapp/       (Port 12353)
├── 8.opena9_telephone/      (Port 12354)
├── 9.opena10_call_tracking/ (Port 12355)
├── 10.opena11_unlock/       (Port 12356) ⚠️ CRITICAL SECURITY
├── 11.opena12_social_media/ (Port 12357)
├── 12.opena13_influencer/   (Port 12358)
├── 13.opena14_calendar/     (Port 12359)
├── 14.opena15_html/         (Port 12360)
├── 15.opena16_shop/         (Port 12361)
├── 16.opena17_homepagecreator/ (Port 12362)
├── 17.opena18_CMR/          (Port 12363)
├── 18.opena19_Aktien&Crypto/ (Port 12364)
├── 19.opena20_dashboard_agent/ (Port 12349) ⚙️ MAIN DASHBOARD
├── 20.opena21_workflow/     (Port 12367)
├── agent_directories.json   (Kanonisches Mapping)
├── scripts/
│   └── validate_agent_directories.sh
└── bin/
    └── merge_finalize.sh
```

---

## 🔍 KRITISCHE AGENTEN

### ⚠️ opena11 (Port 12356) - VAULT & SECRETS

**Kategorie:** 🔐 **CRITICAL SECURITY**
**Folder:** `Gesamtprojekt/10.opena11_unlock/`
**Funktion:** HashiCorp Vault Integration, Secrets Management
**Backup-Priorität:** 🔴 HIGHEST

**Backup-Strategie:**
```bash
# Vault Backup (täglig)
vault backup --path=/backup/vault/$(date +%Y-%m-%d).snap

# Git-basiert (Config-Versionierung)
git add 10.opena11_unlock/config/
git commit -m "chore: vault config snapshot"

# External Storage (90-Tage Retention)
aws s3 cp vault_backup.snap s3://backup/vault/
```

### 🎯 opena20 (Port 12349) - CENTRAL DASHBOARD

**Kategorie:** 📊 **MAIN ORCHESTRATION**
**Folder:** `Gesamtprojekt/19.opena20_dashboard_agent/`
**Funktion:** Central Dashboard, Agent Orchestration
**Sub-Components:**
- webpanel/ (Frontend)
- backend/ (FastAPI)
- tracing/ (Jaeger Integration - v2025.12.24)

---

## 🔗 AGENT DEPENDENCIES

### Layer 1: Infrastructure (opena1-opena2)
```
opena1, opena2 (PORTIER 3.0)
    ↓ Route & Load-Balance ↓
    (All other agents)
```

### Layer 2: Core Services
```
opena11 (Vault)        ← opena20 (Dashboard)
                       ← All authenticated agents
```

### Layer 3: Connectors (opena4-opena9, opena12, opena14)
```
opena4, opena5, opena6, opena7, opena8, opena9, opena12, opena14
    ↓ Integration Points ↓
    opena20 (Dashboard) ← Aggregates all signals
```

### Layer 4: Specialized Services
```
opena10 (Call Tracking)    → Analytics
opena13 (Influencer)       → Analytics
opena15 (HTML Gen)         → Content
opena16 (Shop)             → E-Commerce
opena17 (Homepage Creator) → Content
opena18 (CRM)              → Customer Data
opena19 (Finance)          → Trading Data
opena21 (Workflow)         → Automation
    ↓ All report to ↓
    opena20 (Central Dashboard)
```

---

## ✅ VALIDATION CHECKLIST

```bash
# 1. Prüfe alle Verzeichnisse existieren
bash scripts/validate_agent_directories.sh

# 2. Prüfe Port-Mappings
grep -E "port|Port|PORT" */*/main.py | head -20

# 3. Prüfe agent_directories.json ist aktuell
cat agent_directories.json | jq '.metadata.last_updated'

# 4. Prüfe all agents are reachable
for agent in opena{1..21}; do
    curl -s http://localhost:$(grep "\"$agent\"" agent_directories.json | grep port | head -1)/health || echo "❌ $agent unreachable"
done
```

---

## 📋 AGENT TYPES CLASSIFICATION

| Type | Agents | Purpose |
|------|--------|---------|
| 🏗️ **Portier** | opena1, opena2 | Port Management, Load Balancing |
| 🎨 **UI** | opena3 | Web Interface |
| 🔌 **Connectors** | opena4-9, 12, 14 | External Integrations |
| 📊 **Analytics** | opena10, opena13 | Data Collection & Analysis |
| 🔐 **Security** | opena11 | Vault & Secrets |
| ⚡ **Generators** | opena15, opena17 | Content Generation |
| 🛍️ **E-Commerce** | opena16 | Shop Integration |
| 👥 **CRM** | opena18 | Customer Management |
| 💰 **Finance** | opena19 | Trading & Markets |
| 📈 **Dashboard** | opena20 | Orchestration Hub |
| 🔄 **Workflow** | opena21 | Automation Engine |

---

## 🚀 DEPLOYMENT REFERENCE

### Full Stack Start (In dieser Reihenfolge)

```bash
# 1. Infrastructure Layer
docker-compose up -d opena1 opena2

# 2. Security Layer
docker-compose up -d opena11

# 3. Core UI
docker-compose up -d opena3

# 4. All Connectors (parallel)
docker-compose up -d opena4 opena5 opena6 opena7 opena8 opena9 opena12 opena14

# 5. Analytics & Specialized
docker-compose up -d opena10 opena13 opena15 opena16 opena17 opena18 opena19

# 6. Central Dashboard
docker-compose up -d opena20

# 7. Workflow Engine
docker-compose up -d opena21

# 8. Verify All Healthy
bash scripts/validate_agent_directories.sh
```

### Single Agent Start

```bash
# Prüfe Port aus Mapping
PORT=$(jq -r '.agents[] | select(.name=="opena20") | .port' agent_directories.json)
FOLDER=$(jq -r '.agents[] | select(.name=="opena20") | .folder' agent_directories.json)

cd "$FOLDER"
docker-compose up -d
curl http://localhost:$PORT/health
```

---

## 📝 USAGE GUIDELINES

1. **Beim Deployment:** Immer dieses Mapping konsultieren
2. **Bei Port-Konfiguration:** Verwende `agent_directories.json`
3. **Bei Validierung:** Nutze `validate_agent_directories.sh`
4. **Bei Monitoring:** Port-Range 12344-12367 ist kanonisch (außer opena20 @ 12349 und opena3 @ 12347)

---

## 🔄 SYNCHRONIZATION

**Quelle:** agent_directories.json
**Auto-Generated von:** Baseline Overview (2025-12-24)
**Sync-Frequenz:** Bei jedem Major Release
**Validation:** ✅ All 21 agents verified

```json
{
  "source": "Baseline Übersicht",
  "status": "CANONICAL",
  "last_sync": "2025-12-24",
  "total_verified": 21
}
```

---

**Status:** ✅ APPROVED & VERIFIED
**Maintainer:** DevOps / Infrastructure Team
**Last Updated:** 2025-12-24
