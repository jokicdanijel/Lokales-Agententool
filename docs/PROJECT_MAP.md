# ELION Hyper-Dashboard (PORTIER 3.0) — PROJECT MAP

Ziel dieser Map: **Single Pane of Glass** für Dev/Ops/Copilot.
Sie erklärt **wer ist wo**, **wer hört auf welchem Port**, **wie ist der Message-Flow**, **wie startet man das System**, und **wo sind die Gates**.

---

## 0) Governance (bindend)

### Agent-ID Gesetz (immutable)
- Agent-IDs sind exakt: **opena1 .. opena21**
- **Keine Aliase, keine Umbenennungen**
- **Jeder Agent hat Frontend + Backend** (UI darf minimal sein)

### Core-Komponente (kein Agent)
- `kordp` ist **Core-Service**, liegt unter:
  - `1.opena1&2_portier/kordp/`
- `kordp` ist **NICHT** Teil von `opena1..opena21` (kein Agent-ID)

### Port Policy
- Erlaubt: **12344–12399**
- Verboten: **8080**
- Baseline ist die **Port Authority**: Wenn Doku ≠ Baseline → **Baseline gewinnt**.

### Message-Flow (Option-2, sacred)
- Request: `Client/OpenAI → opena1 → opena2 → kordp → Tool`
- Response: `Tool → opena2 → opena1 → Client/OpenAI`

---

## 1) Repo Root Layout (High-Level)

```
Gesamtprojekt/
├── 1.opena1&2_portier/                 # Core Stack: opena1, opena2, kordp + ops/bin
├── 2.opena3_openwebui/                 # opena3 (OpenWebUI/Adapter)
├── 3.opena4_telegram/ ... 20.opena21_workflow/  # Feature Agents (opena4–opena21)
├── src/                                # Shared Modules
├── docs/                               # Documentation + PROJECT_MAP.md
├── bin/                                # Root scripts (ops.sh, verify_baseline_and_discovery.sh)
├── scripts/                            # Validators, discovery, tooling
├── configs/                            # JSON registries
├── artifacts/                          # Gate outputs (json)
├── system_baseline.yaml                # Single Source of Truth (SSoT)
└── .github/workflows/                  # CI/CD (baseline-discovery-gate.yml)
```

---

## 2) Agents & Ports (SSoT Snapshot)

| Agent | Port | Plan | Ordner | Rolle |
|------:|-----:|------|--------|------|
| opena1 | 12344 | core | `1.opena1&2_portier/opena1` | Koordinator (Routing/Discovery) |
| opena2 | 12345 | core | `1.opena1&2_portier/opena2` | Archivar (Safepoints/Audit) |
| opena3 | 12347 | basic | `2.opena3_openwebui` | OpenWebUI Bridge/Adapter |
| opena4 | 12346 | basic | `3.opena4_telegram` | Telegram Bot |
| opena5 | 12365 | ultimum | `4.opena5_vscode` | VSCode/IDE Integration |
| opena6 | 12351 | premium | `5.opena6_browser` | Browser Automation |
| opena7 | 12350 | basic | `6.opena7_email` | E-Mail (SMTP/IMAP) |
| opena8 | 12353 | pro | `7.opena8_whatsapp` | WhatsApp Business |
| opena9 | 12354 | premium | `8.opena9_telephone` | Telefonie/VoIP |
| opena10 | 12355 | ultimum | `9.opena10_call_tracking` | Call Tracking/Analytics |
| opena11 | 12356 | basic | `10.opena11_unlock` | Auth/Berechtigungen |
| opena12 | 12357 | pro | `11.opena12_social_media` | Social APIs |
| opena13 | 12358 | ultimum | `12.opena13_influencer` | Kampagnen Mgmt |
| opena14 | 12359 | pro | `13.opena14_calendar` | Kalender Integration |
| opena15 | 12360 | premium | `14.opena15_html` | HTML Generator |
| opena16 | 12361 | premium | `15.opena16_shop` | Shop/E-Commerce |
| opena17 | 12362 | ultimum | `16.opena17_homepagecreator` | Homepage Creator |
| opena18 | 12363 | pro | `17.opena18_CMR` | CRM |
| opena19 | 12364 | ultimum | `18.opena19_Aktien&Crypto` | Finance |
| opena20 | 12349 | system | `19.opena20_dashboard_agent` | Dashboard/Control Plane |
| opena21 | 12368 | system | `20.opena21_workflow` | Workflow Engine |

---

## 3) Standard Agent Folder Shape (Frontend + Backend)

```
<agent_folder>/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

---

## 4) Gate Layer (CI/Dev/Ops gleiche Wahrheit)

Ein Befehl:

```bash
./bin/verify_baseline_and_discovery.sh
```

Erzwingt:
- Baseline schema ok (IDs/Ports/Policy)
- Agent-Folder existieren + nicht leer
- Deterministische Artefakte

Artefakte:
- `artifacts/Baseline_validation.json`
- `artifacts/Agent_discovery.json`

---

## 5) "Do / Don't" (Copilot Shortlist)

✅ DO:
- Ports nur aus Baseline
- `GET /health` überall
- Token-Checks auf protected endpoints
- Logs strukturiert

❌ DON'T:
- Agent IDs ändern
- Ports außerhalb Pool/8080
- Message flow bypassen
- Secrets hardcoden
