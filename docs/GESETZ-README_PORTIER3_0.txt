# ==============================================================================
# PORTIER 3.0 – Git-Projektübersicht (korrigiert, verbindlich)
# Stand: 25.12.2025
# ==============================================================================
#
# GESETZ (fix, wie besprochen):
# - Agent-IDs sind exakt: opena1 … opena21 (keine Aliase, keine Umbenennungen)
# - JEDER Agent hat: Frontend = ja und Backend = ja
# - Ports sind fix (Single Source of Truth = system_baseline.yaml / Port-Tabelle)
# - Port-Policy: erlaubt 12344–12399, verboten 8080
# - Domäne (primär): www.hyperdashboard-one.de / hyperdashboard-one.de
#
# Start-Reihenfolge (Operations-Standard):
# 1) Core Stack:
#    Gesamtprojekt/1.opena1&2_portier/bin/start_stack.sh
# 2) Dashboard:
#    Gesamtprojekt/19.opena20_dashboard_agent/bin/start_opena20.sh
# 3) Feature-Agenten gemäß Plan:
#    Basic   → opena3, opena4, opena7, opena11
#    Pro     → opena8, opena12, opena14, opena18
#    Premium → opena6, opena9, opena15, opena16
#    Ultimum → opena5, opena10, opena13, opena17, opena19
# 4) Workflow:
#    Gesamtprojekt/20.opena21_workflow/backend/app.py (oder start_opena21.sh falls vorhanden)
#
# Repo-Root: Gesamtprojekt/ (PORTIER 3.0 Root)
# ==============================================================================
Gesamtprojekt/
├── .github/                                  # GitHub Config + CI
│   ├── copilot-master-prompt.md
│   ├── copilot-instructions.md
│   ├── COMPLETION_CHECKLIST.md
│   └── workflows/
│       └── ci.yml
├── 1.opena1&2_portier/                       # PORTIER Core (opena1, opena2, kordp)
├── 2.opena3_openwebui/                       # opena3
├── 3.opena4_telegram/                        # opena4
├── 4.opena5_vscode/                          # opena5
├── 5.opena6_browser/                         # opena6
├── 6.opena7_email/                           # opena7
├── 7.opena8_whatsapp/                        # opena8
├── 8.opena9_telephone/                       # opena9
├── 9.opena10_call_tracking/                  # opena10
├── 10.opena11_unlock/                        # opena11
├── 11.opena12_social_media/                  # opena12
├── 12.opena13_influencer/                    # opena13
├── 13.opena14_calendar/                      # opena14
├── 14.opena15_html/                          # opena15
├── 15.opena16_shop/                          # opena16
├── 16.opena17_homepagecreator/               # opena17
├── 17.opena18_CMR/                           # opena18
├── 18.opena19_Aktien&Crypto/                 # opena19
├── 19.opena20_dashboard_agent/               # opena20
├── 20.opena21_workflow/                      # opena21
├── src/                                      # Shared Modules
├── docs/                                     # Documentation
├── bin/                                      # Root Wrapper Scripts
├── scripts/                                  # Registry/Tests/Seed
├── configs/                                  # JSON registries
├── pyproject.toml
├── docker-compose.prod.yml
├── LICENSE
├── .gitignore
└── .env.example

# ==============================================================================
# Agenten & Pfade (verbindlich)
# ==============================================================================
Agenten (IDs exakt opena1..opena21) – Ordnerpfade (exakt):
- opena1  -> Gesamtprojekt/1.opena1&2_portier/opena1/
- opena2  -> Gesamtprojekt/1.opena1&2_portier/opena2/
- kordp   -> Gesamtprojekt/1.opena1&2_portier/kordp/   (Core-Komponente, kein Agent)
- opena3  -> Gesamtprojekt/2.opena3_openwebui/
- opena4  -> Gesamtprojekt/3.opena4_telegram/
- opena5  -> Gesamtprojekt/4.opena5_vscode/
- opena6  -> Gesamtprojekt/5.opena6_browser/
- opena7  -> Gesamtprojekt/6.opena7_email/
- opena8  -> Gesamtprojekt/7.opena8_whatsapp/
- opena9  -> Gesamtprojekt/8.opena9_telephone/
- opena10 -> Gesamtprojekt/9.opena10_call_tracking/
- opena11 -> Gesamtprojekt/10.opena11_unlock/
- opena12 -> Gesamtprojekt/11.opena12_social_media/
- opena13 -> Gesamtprojekt/12.opena13_influencer/
- opena14 -> Gesamtprojekt/13.opena14_calendar/
- opena15 -> Gesamtprojekt/14.opena15_html/
- opena16 -> Gesamtprojekt/15.opena16_shop/
- opena17 -> Gesamtprojekt/16.opena17_homepagecreator/
- opena18 -> Gesamtprojekt/17.opena18_CMR/
- opena19 -> Gesamtprojekt/18.opena19_Aktien&Crypto/
- opena20 -> Gesamtprojekt/19.opena20_dashboard_agent/
- opena21 -> Gesamtprojekt/20.opena21_workflow/

# ==============================================================================
# Standard-Agent-Shape (Frontend + Backend = ja)
# ==============================================================================
Feature-Agent Template (opena4..opena19 & opena21):
<agent_folder>/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js

Core (Sonderform, aber Frontend+Backend = ja):
1.opena1&2_portier/
├── opena1/ (koordinator.py, main_production.py)
├── opena2/ (opena2_app.py)
└── kordp/  (main_production.py, router.py, tool_resolver.py)

# ==============================================================================
# Ports (SSoT Snapshot – fix)
# ==============================================================================
Port-Policy: allowed 12344–12399, forbidden 8080. Ports eindeutig.

opena1  12344
opena2  12345
opena4  12346
opena3  12347
opena20 12349
opena7  12350
opena6  12351
opena8  12353   (FIX)
opena9  12354
opena10 12355
opena11 12356
opena12 12357
opena13 12358
opena14 12359
opena15 12360
opena16 12361
opena17 12362
opena18 12363
opena19 12364
opena5  12365
opena21 12368
