# Ports & IDs Compliance Scan (Enhanced)

**Status:** ❌ FAIL

## Summary

- Baseline agents: 21
- opena references found: 22
- Ports found: 36
- Compose entries: 4

## ❌ opena IDs outside 1..21

- opena99 in 1 locations

## ❌ Forbidden port literals in code

### Port 3000 (96 occurrences)

- .env.backup_20251221_061518:27 — `OPENWEBUI_URL=http://127.0.0.1:3000`
- .env.backup_20251221_061518:106 — `OPENWEBUI_URL=http://127.0.0.1:3000`
- .env.backup_20251221_061518:179 — `SCTA_API_PORT=3000`
- .env.backup_20251221_061518:272 — `OPENWEBUI_URL=http://127.0.0.1:3000`
- .env.backup_20251221_061518:315 — `OPENWEBUI_PORT=3000`
- main_dashboard_agent.py:1370 — `"url": "http://127.0.0.1:3000",`
- .env:180 — `OPENWEBUI_PORT=3000`
- .env:181 — `OPENWEBUI_URL=http://127.0.0.1:3000`
- .env:206 — `SCTA_API_PORT=3000`
- .env.original_corrupt:27 — `OPENWEBUI_URL=http://127.0.0.1:3000`

### Port 8080 (27 occurrences)

- openwebui_integration_12347.py:10 — `- Port 8080: OpenWebUI UI (external, UI-only)`
- openwebui_integration_12347.py:32 — `OPENWEBUI_UI_PORT = 8080           # OpenWebUI UI (external)`
- openwebui_integration_12347.py:398 — `"fallback": "Use direct OpenWebUI UI at port 8080"`
- config.py:35 — `origins = ["http://127.0.0.1:8080"]  # OpenWebUI Frontend`
- main_dashboard_agent.py:1306 — `"url": "http://127.0.0.1:8080",`
- security.py:236 — `return port in cls.ALLOWED_RANGE or port == 8080`
- openwebui_integration_12346.py:31 — `OPENWEBUI_UI_PORT = 8080           # OpenWebUI UI (external, UI-only)`
- openwebui_integration_12346.py:276 — `"note": "Port 8080 ist nur für UI erlaubt, Backend-Calls über opena3"`
- webpanel/README.md:178 — `- **OpenWebUI (8080)** - UI-only (extern)`
- bin/start_openwebui_integration_12347.sh:145 — `echo "  8080:  OpenWebUI UI (external)"`

## ⚠️ ID<->Port mismatches (line-local)

_Only lines with exactly 1 ID and 1 port are checked_

- main_dashboard_v3.py:60: opena4 found port 12348, expected 12346
  `{"id": "opena4",  "name": "Telegram Agent",      "kuerzel": "telep",       "port": 12348, "icon": "📱`
- config.py:117: opena4 found port 12348, expected 12346
  `AgentInfo(id="opena4",  name="Telegram Agent",          kuerzel="telep",       port=12348),`
- main_dashboard_final.py:65: opena4 found port 12348, expected 12346
  `{"id": "opena4", "name": "Telegram Agent", "kuerzel": "telep", "port": 12348},`
- main_dashboard_agent.py:200: opena4 found port 12348, expected 12346
  `{"id": "opena4", "name": "Telegram Agent", "kuerzel": "telep", "port": 12348},`
- hyper_dashboard_fusion.py:84: opena4 found port 12348, expected 12346
  `{"id": "opena4", "name": "Telegram", "port": 12348, "url": "http://127.0.0.1:12348"},`
- main_dashboard.py:185: opena4 found port 12348, expected 12346
  `{"id": "opena4",  "name": "Telegram Agent",            "kuerzel": "telep",      "port": 12348},`
- main_dashboard_v3.py:61: opena5 found port 12351, expected 12350
  `{"id": "opena5",  "name": "VS Code Agent",       "kuerzel": "vscop",       "port": 12351, "icon": "💻`
- config.py:118: opena5 found port 12351, expected 12350
  `AgentInfo(id="opena5",  name="VS Code Agent",           kuerzel="vscop",       port=12351),`
- main_dashboard_agent.py:201: opena5 found port 12351, expected 12350
  `{"id": "opena5", "name": "VS Code Agent", "kuerzel": "vscop", "port": 12351},`
- hyper_dashboard_fusion.py:85: opena5 found port 12349, expected 12350
  `{"id": "opena5", "name": "VSCode", "port": 12349, "url": "http://127.0.0.1:12349"},`
- main_dashboard.py:186: opena5 found port 12351, expected 12350
  `{"id": "opena5",  "name": "VS Code Agent",             "kuerzel": "vscop",      "port": 12351},`
- docs/SCANNERS.md:146: opena5 found port 12348, expected 12350
  ```- `agent://opena5:12348````
- scripts/api_binding_scanner.py:21: opena5 found port 12348, expected 12350
  `- agent://opena5:12348`
- main_dashboard_v3.py:62: opena6 found port 12352, expected 12351
  `{"id": "opena6",  "name": "Browser Agent",       "kuerzel": "browsep",     "port": 12352, "icon": "🌐`
- config.py:119: opena6 found port 12352, expected 12351
  `AgentInfo(id="opena6",  name="Browser Agent",           kuerzel="browsep",     port=12352),`
- main_dashboard_agent.py:202: opena6 found port 12352, expected 12351
  `{"id": "opena6", "name": "Browser Agent", "kuerzel": "browsep", "port": 12352},`
- main_dashboard_agent.py:1949: opena6 found port 12352, expected 12351
  `{"id": "opena6", "port": 12352, "type": "Browser Agent", "status": "online"},`
- hyper_dashboard_fusion.py:86: opena6 found port 12350, expected 12351
  `{"id": "opena6", "name": "Browser", "port": 12350, "url": "http://127.0.0.1:12350"},`
- main_dashboard.py:187: opena6 found port 12352, expected 12351
  `{"id": "opena6",  "name": "Browser Agent",             "kuerzel": "browsep",    "port": 12352},`
- main_dashboard_v3.py:63: opena7 found port 12353, expected 12352
  `{"id": "opena7",  "name": "Email Agent",         "kuerzel": "emailp",      "port": 12353, "icon": "📧`
- config.py:120: opena7 found port 12353, expected 12352
  `AgentInfo(id="opena7",  name="Email Agent",             kuerzel="emailp",      port=12353),`
- main_dashboard_agent.py:203: opena7 found port 12353, expected 12352
  `{"id": "opena7", "name": "Email Agent", "kuerzel": "emailp", "port": 12353},`
- hyper_dashboard_fusion.py:87: opena7 found port 12351, expected 12352
  `{"id": "opena7", "name": "Email", "port": 12351, "url": "http://127.0.0.1:12351"},`
- main_dashboard.py:188: opena7 found port 12353, expected 12352
  `{"id": "opena7",  "name": "Email Agent",               "kuerzel": "emailp",     "port": 12353},`
- main_dashboard_v3.py:64: opena8 found port 12354, expected 12353
  `{"id": "opena8",  "name": "WhatsApp Agent",      "kuerzel": "whatsappp",   "port": 12354, "icon": "💬`
- config.py:121: opena8 found port 12354, expected 12353
  `AgentInfo(id="opena8",  name="WhatsApp Agent",          kuerzel="whatsappp",   port=12354),`
- main_dashboard_agent.py:204: opena8 found port 12354, expected 12353
  `{"id": "opena8", "name": "WhatsApp Agent", "kuerzel": "whatsappp", "port": 12354},`
- hyper_dashboard_fusion.py:88: opena8 found port 12352, expected 12353
  `{"id": "opena8", "name": "WhatsApp", "port": 12352, "url": "http://127.0.0.1:12352"},`
- main_dashboard.py:189: opena8 found port 12354, expected 12353
  `{"id": "opena8",  "name": "WhatsApp Agent",            "kuerzel": "whatsappp",  "port": 12354},`
- main_dashboard_v3.py:65: opena9 found port 12355, expected 12354
  `{"id": "opena9",  "name": "Telefonie Agent",     "kuerzel": "telephonep",  "port": 12355, "icon": "📞`
- config.py:122: opena9 found port 12355, expected 12354
  `AgentInfo(id="opena9",  name="Telefonie Agent",         kuerzel="telephonep",  port=12355),`
- main_dashboard_agent.py:205: opena9 found port 12355, expected 12354
  `{"id": "opena9", "name": "Telefonie Agent", "kuerzel": "telphonep", "port": 12355},`
- hyper_dashboard_fusion.py:89: opena9 found port 12353, expected 12354
  `{"id": "opena9", "name": "Phone Response", "port": 12353, "url": "http://127.0.0.1:12353"},`
- main_dashboard.py:190: opena9 found port 12355, expected 12354
  `{"id": "opena9",  "name": "Telefonie Agent",           "kuerzel": "telphonep",  "port": 12355},`
- main_dashboard_v3.py:66: opena10 found port 12356, expected 12355
  `{"id": "opena10", "name": "Call Tracking",       "kuerzel": "calltrackp",  "port": 12356, "icon": "📊`
- config.py:123: opena10 found port 12356, expected 12355
  `AgentInfo(id="opena10", name="Call Tracking Agent",     kuerzel="calltrackp",  port=12356),`
- main_dashboard_agent.py:206: opena10 found port 12356, expected 12355
  `{"id": "opena10", "name": "Call Tracking Agent", "kuerzel": "calltrackp", "port": 12356},`
- hyper_dashboard_fusion.py:90: opena10 found port 12354, expected 12355
  `{"id": "opena10", "name": "Phone Caller", "port": 12354, "url": "http://127.0.0.1:12354"},`
- main_dashboard.py:191: opena10 found port 12356, expected 12355
  `{"id": "opena10", "name": "Call Tracking Agent",       "kuerzel": "calltrackp", "port": 12356},`
- main_dashboard_v3.py:67: opena11 found port 12357, expected 12356
  `{"id": "opena11", "name": "Unlock Agent",        "kuerzel": "unlockp",     "port": 12357, "icon": "🔓`
- config.py:124: opena11 found port 12357, expected 12356
  `AgentInfo(id="opena11", name="Unlock Agent",            kuerzel="unlockp",     port=12357),`
- main_dashboard_agent.py:207: opena11 found port 12357, expected 12356
  `{"id": "opena11", "name": "Unlock Agent", "kuerzel": "unlockp", "port": 12357},`
- hyper_dashboard_fusion.py:91: opena11 found port 12355, expected 12356
  `{"id": "opena11", "name": "Decoder", "port": 12355, "url": "http://127.0.0.1:12355"},`
- main_dashboard.py:192: opena11 found port 12357, expected 12356
  `{"id": "opena11", "name": "Unlock Agent",              "kuerzel": "unlockp",    "port": 12357},`
- main_dashboard_v3.py:68: opena12 found port 12358, expected 12357
  `{"id": "opena12", "name": "Social Media Agent",  "kuerzel": "smp",         "port": 12358, "icon": "📣`
- config.py:125: opena12 found port 12358, expected 12357
  `AgentInfo(id="opena12", name="Social Media Agent",      kuerzel="smp",         port=12358),`
- main_dashboard_agent.py:208: opena12 found port 12358, expected 12357
  `{"id": "opena12", "name": "Social Media Agent", "kuerzel": "smp", "port": 12358},`
- hyper_dashboard_fusion.py:92: opena12 found port 12356, expected 12357
  `{"id": "opena12", "name": "Social Automation", "port": 12356, "url": "http://127.0.0.1:12356"},`
- main_dashboard.py:193: opena12 found port 12358, expected 12357
  `{"id": "opena12", "name": "Social Media Agent",        "kuerzel": "smp",        "port": 12358},`
- main_dashboard_v3.py:69: opena13 found port 12359, expected 12358
  `{"id": "opena13", "name": "Influencer Agent",    "kuerzel": "influp",      "port": 12359, "icon": "⭐`

## ⚠️ Inventory mismatch

- Missing: []
- Extra: []

---

_Generated by ports_ids_compliance_scanner_v2.py_
