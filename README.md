## Ausgabe 1/4 — **Korrigierte Projektübersicht (IST/SOLL-Doku für Git)**

*(exakt deine Namen/Ordner – nur bereinigt nach unseren Absprachen: **jeder Agent hat Frontend+Backend**, Port-Policy, Port-Fix **opena8=12353**, und widersprüchliche Port-Stellen im Text harmonisiert)*

---

# PORTIER 3.0 – Git-Projektübersicht (korrigiert, verbindlich)

**Stand:** 2025-12-25
**Regeln (fix, wie besprochen):**

* **Agent-IDs sind exakt:** `opena1` … `opena21` (keine Aliase, keine Umbenennungen)
* **JEDER Agent hat:** `Frontend = ja` und `Backend = ja`
* **Ports sind fix** (Single Source of Truth = Baseline/Port-Tabelle unten)
* **Port-Policy:** erlaubt `12344–12399`, verboten `8080`
* **Domain (primary):** `www.hyperdashboard-one.de` / `hyperdashboard-one.de`

---

## 1) Repo-Root: Gesamtprojekt (PORTIER 3.0 Root)

```text
Gesamtprojekt/
│
├── .github/                                  # GitHub Config + CI
│   ├── copilot-master-prompt.md
│   ├── copilot-instructions.md
│   ├── COMPLETION_CHECKLIST.md
│   └── workflows/
│       └── ci.yml
│
├── 1.opena1&2_portier/                       # PORTIER Core Services (opena1, opena2, kordp)
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
│
├── src/                                      # Shared Modules
├── docs/                                     # Documentation
├── bin/                                      # Root Wrapper Scripts
├── scripts/                                  # Registry/Tests/Seed
├── configs/                                  # JSON registries
│
├── pyproject.toml
├── docker-compose.prod.yml
├── LICENSE
├── .gitignore
└── .env.example
```

---

## 2) Übersicht PORTIER 3.0 – Agenten opena1–opena21 (für Git)

> **Frontend = ja** bedeutet: jeder Agent hat eine **Webseite/Admin-UI/Diagnose-UI** (z. B. `frontend/index.html` oder `templates+static`).
> **Backend = ja** bedeutet: jeder Agent hat einen **Service-Entry** (FastAPI/Service/Worker API), plus Startbarkeit.

| Agent   | Ordnerpfad (exakt)                          | Rolle im System                                    | Frontend | Backend |
| ------- | ------------------------------------------- | -------------------------------------------------- | -------- | ------- |
| opena1  | `Gesamtprojekt/1.opena1&2_portier/opena1/`  | Koordinator (Routing/Decision/Discovery)           | ja       | ja      |
| opena2  | `Gesamtprojekt/1.opena1&2_portier/opena2/`  | Archivar (Safepoints/Audit Trail)                  | ja       | ja      |
| kordp   | `Gesamtprojekt/1.opena1&2_portier/kordp/`   | Gateway (Routing/Tool Resolver)                    | ja       | ja      |
| opena3  | `Gesamtprojekt/2.opena3_openwebui/`         | Chat/Terminal UI Agent (OpenWebUI Wrapper+Adapter) | ja       | ja      |
| opena4  | `Gesamtprojekt/3.opena4_telegram/`          | Telegram Bot Agent                                 | ja       | ja      |
| opena5  | `Gesamtprojekt/4.opena5_vscode/`            | VSCode Agent (Code Integration)                    | ja       | ja      |
| opena6  | `Gesamtprojekt/5.opena6_browser/`           | Browser Automation                                 | ja       | ja      |
| opena7  | `Gesamtprojekt/6.opena7_email/`             | E-Mail Client (SMTP/IMAP)                          | ja       | ja      |
| opena8  | `Gesamtprojekt/7.opena8_whatsapp/`          | WhatsApp Business/Automation                       | ja       | ja      |
| opena9  | `Gesamtprojekt/8.opena9_telephone/`         | Telefonie (VoIP/Transkription)                     | ja       | ja      |
| opena10 | `Gesamtprojekt/9.opena10_call_tracking/`    | Anrufverfolgung/Analytik                           | ja       | ja      |
| opena11 | `Gesamtprojekt/10.opena11_unlock/`          | Zutrittskontrolle/Auth                             | ja       | ja      |
| opena12 | `Gesamtprojekt/11.opena12_social_media/`    | Social Media (X/LinkedIn etc.)                     | ja       | ja      |
| opena13 | `Gesamtprojekt/12.opena13_influencer/`      | Influencer/Kampagnen Mgmt                          | ja       | ja      |
| opena14 | `Gesamtprojekt/13.opena14_calendar/`        | Kalender (Google/ICS etc.)                         | ja       | ja      |
| opena15 | `Gesamtprojekt/14.opena15_html/`            | HTML Generator                                     | ja       | ja      |
| opena16 | `Gesamtprojekt/15.opena16_shop/`            | Shop/E-Commerce                                    | ja       | ja      |
| opena17 | `Gesamtprojekt/16.opena17_homepagecreator/` | Homepage Creator                                   | ja       | ja      |
| opena18 | `Gesamtprojekt/17.opena18_CMR/`             | CRM                                                | ja       | ja      |
| opena19 | `Gesamtprojekt/18.opena19_Aktien&Crypto/`   | Finanzen (Aktien/Krypto)                           | ja       | ja      |
| opena20 | `Gesamtprojekt/19.opena20_dashboard_agent/` | Dashboard/Control Plane                            | ja       | ja      |
| opena21 | `Gesamtprojekt/20.opena21_workflow/`        | Workflow Engine/Orchestrierung                     | ja       | ja      |

---

## 3) Agenten-Ordnung 1 bis 21 — Ordnerdarstellung (so wie sie sein sollen)

### 3.1 `opena1`, `opena2`, `kordp` — PORTIER Core (bestehend)

```text
1.opena1&2_portier/
├── opena1/
│   ├── koordinator.py
│   └── main_production.py
├── opena2/
│   └── opena2_app.py
├── kordp/
│   ├── main_production.py
│   ├── router.py
│   └── tool_resolver.py
├── archivp_store/
│   ├── YYYY/MM/DD/
│   └── index.jsonl
├── bin/
│   ├── start_stack.sh
│   ├── stop_stack.sh
│   ├── verify_stack.sh
│   ├── check_ports.sh
│   └── env_bootstrap.sh
├── tests/
│   └── test_portier_stack.py
└── venv313/                                  # Runtime/venv (Git-Policy beachten)
```

### 3.2 `opena3` — OpenWebUI Agent (bestehend, Ports werden unten korrigiert)

```text
2.opena3_openwebui/
├── main_openwebui_agent.py
├── openwebui_adapter.py
└── bin/
    ├── start_opena3.sh
    └── start_openwebui_adapter.sh
```

### 3.3 `opena4` bis `opena19` — Feature Agents (einheitliche Darstellung)

> **Verbindlich:** jeder Agent besitzt **Frontend + Backend**.
> Wenn Frontend heute noch nicht als Ordner existiert → wird es **dorthin verfrachtet/angelegt**, ohne Umbenennungen.

```text
3.opena4_telegram/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
4.opena5_vscode/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
5.opena6_browser/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
6.opena7_email/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
7.opena8_whatsapp/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
8.opena9_telephone/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
9.opena10_call_tracking/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
10.opena11_unlock/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
11.opena12_social_media/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
12.opena13_influencer/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
13.opena14_calendar/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
14.opena15_html/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
15.opena16_shop/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
16.opena17_homepagecreator/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
17.opena18_CMR/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

```text
18.opena19_Aktien&Crypto/
├── backend/
│   └── app.py
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    └── config.js
```

### 3.4 `opena20` — Dashboard Agent (bestehend)

```text
19.opena20_dashboard_agent/
├── main.py
├── router.py
├── templates/
│   └── dashboard.html
├── static/
│   ├── css/
│   │   └── dashboard.css
│   └── js/
│       └── dashboard.js
└── bin/
    └── start_opena20.sh
```

### 3.5 `opena21` — Workflow Engine + UI (Variante B, wie beschlossen)

```text
20.opena21_workflow/
├── backend/
│   └── app.py
└── frontend/
    └── index.html
```

---

## 4) Ports, Rollen, Plan (korrigierte Tabelle – **opena8 = 12353**)

**Port-Policy:** `allow_range: 12344–12399`, `forbidden_ports: [8080]`
**Hinweis zur Korrektur:** In deiner Liste gab es Port-Kollisionen (z. B. `12350` mehrfach).
Diese Tabelle ist die **bereinigte, konfliktfreie** Fassung für die Baseline/CI.

```text
ID       Name                 Port   Rollen                               Plan
------------------------------------------------------------------------------
opena1    Koordinator          12344  Routing, Service Discovery           Kern
opena2    Archivar             12345  Protokollierung, Audit Trail         Kern
opena4    Telegramm            12346  Telegram Bot                         Basic
opena3    OpenWebUI            12347  Chat-Schnittstelle                   Basic
opena20   Dashboard            12349  Kontrollebene                        System
opena7    E-Mail               12350  SMTP/IMAP                            Basic
opena6    Browser              12351  Browser Automation                   Premium
opena5    VSCode               12365  Code Integration                     Ultimum
opena8    WhatsApp             12353  WhatsApp Business API                Pro   (FIX)
opena9    Telefon              12354  VoIP, Transkription                  Premium
opena10   Anrufverfolgung      12355  Analytik                             Ultimum
opena11   Zutrittskontrolle    12356  Auth, Berechtigungen                 Basic
opena12   Soziale Medien       12357  Twitter/LinkedIn                     Pro
opena13   Influencer           12358  Kampagne Mgmt                        Ultimum
opena14   Kalender             12359  Kalender-Integration                 Pro
opena15   HTML-Generator       12360  Dynamische HTML                      Premium
opena16   Einkaufen            12361  E-Commerce                           Premium
opena17   Homepage-Ersteller   12362  Website-Baumeister                   Ultimum
opena18   CRM                  12363  Kundenmanagement                     Pro
opena19   Finanzen             12364  Aktien/Krypto                        Ultimum
opena21   Workflow             12368  Orchestrierung/Workflows              System
------------------------------------------------------------------------------
```

---

## 5) Start-Reihenfolge (Operations-Standard, wie besprochen)

```text
1) Core Stack:
   Gesamtprojekt/1.opena1&2_portier/bin/start_stack.sh

2) Dashboard:
   Gesamtprojekt/19.opena20_dashboard_agent/bin/start_opena20.sh

3) Feature-Agenten gemäß Plan:
   Basic   → opena3, opena4, opena7, opena11
   Pro     → opena8, opena12, opena14, opena18
   Premium → opena6, opena9, opena15, opena16
   Ultimum → opena5, opena10, opena13, opena17, opena19

4) Workflow:
   Gesamtprojekt/20.opena21_workflow/backend/app.py (oder start_opena21.sh wenn vorhanden)
```
Hier ist die komplette, korrigierte Baseline-Ausgabe (Ports fix inkl. opena8=12353), plus Validator-Script und ein Beispiel-Artefakt.

Wichtig: Keine Umbenennungen, keine Aliase. IDs = opena1..opena21 fix.
Jeder Agent: Frontend+Backend = ja (Visibility/Plan steuert nur Abo/Anzeige, nicht Existenz).

1) system_baseline.yaml
# ============================================================================
# PORTIER 3.0 | System Baseline (Single Source of Truth)
# - IDs sind exakt: opena1..opena21 (keine Aliase)
# - Ports sind fix; Abweichung = FAIL
# - Jeder Agent hat Frontend+Backend (UI kann minimal sein)
# - Port-Policy: allow_range 12344-12399, forbidden 8080
# - Domain-Policy: primary_domain = hyperdashboard-one.de/policy
# ============================================================================
baseline:
  name: "PORTIER 3.0"
  version: "1.0.0"
  generated_at_utc: "2025-12-25T00:00:00Z"
  repo_root_hint: "Gesamtprojekt"
  authority: "system_baseline.yaml"

domain_policy:
  primary_domain: "hyperdashboard-one.de/policy"
  public_domain: "www.hyperdashboard-one.de"

port_policy:
  allow_range:
    min: 12344
    max: 12399
  forbidden_ports:
    - 8080
  rule_text: >
    Ports müssen innerhalb 12344–12399 liegen. Port 8080 ist verboten.
    Ports sind eindeutig. Keine Abweichungen und keine Doppelnutzung.

plans:
  core: ["opena1", "opena2"]
  system: ["opena20", "opena21"]
  basic: ["opena3", "opena4", "opena7", "opena11"]
  pro: ["opena8", "opena12", "opena14", "opena18"]
  premium: ["opena6", "opena9", "opena15", "opena16"]
  ultimum: ["opena5", "opena10", "opena13", "opena17", "opena19"]

core_agents: ["opena1", "opena2"]
system_agents: ["opena20", "opena21"]

agents:
  - id: "opena1"
    port: 12344
    name: "Koordinator"
    role: "Routing, Service Discovery"
    plan: "core"
    visibility: "core"
    folder_path: "1.opena1&2_portier/opena1"
    description: "Zentrale Koordination, Dispatch, Entscheidungslogik"

  - id: "opena2"
    port: 12345
    name: "Archivar"
    role: "Protokollierung, Audit Trail"
    plan: "core"
    visibility: "core"
    folder_path: "1.opena1&2_portier/opena2"
    description: "Safepoints CMD/RESP, Audit-Storage-Integration"

  - id: "opena3"
    port: 12347
    name: "OpenWebUI"
    role: "Chat-Schnittstelle"
    plan: "basic"
    visibility: "subscription"
    folder_path: "2.opena3_openwebui"
    description: "Terminal-/Chat-UI Agent Wrapper + Adapter"

  - id: "opena4"
    port: 12346
    name: "Telegramm"
    role: "Telegram Bot"
    plan: "basic"
    visibility: "subscription"
    folder_path: "3.opena4_telegram"
    description: "Telegram Bot, Webhook/Send/Receive"

  - id: "opena5"
    port: 12365
    name: "VSCode"
    role: "Code Integration"
    plan: "ultimum"
    visibility: "subscription"
    folder_path: "4.opena5_vscode"
    description: "Editor/IDE-Bridge, Code-Assist, Repo-Integration"

  - id: "opena6"
    port: 12351
    name: "Browser"
    role: "Browser Automation"
    plan: "premium"
    visibility: "subscription"
    folder_path: "5.opena6_browser"
    description: "Browser-Automation (z.B. Selenium/Playwright)"

  - id: "opena7"
    port: 12350
    name: "E-Mail"
    role: "SMTP/IMAP"
    plan: "basic"
    visibility: "subscription"
    folder_path: "6.opena7_email"
    description: "Mail-Client Agent"

  - id: "opena8"
    port: 12353
    name: "WhatsApp"
    role: "WhatsApp Business API"
    plan: "pro"
    visibility: "subscription"
    folder_path: "7.opena8_whatsapp"
    description: "WhatsApp Automation + Workflows (UI/Backend)"

  - id: "opena9"
    port: 12354
    name: "Telefon"
    role: "VoIP, Transkription"
    plan: "premium"
    visibility: "subscription"
    folder_path: "8.opena9_telephone"
    description: "Telefonie Agent, Calls, Transkription"

  - id: "opena10"
    port: 12355
    name: "Anrufverfolgung"
    role: "Analytik"
    plan: "ultimum"
    visibility: "subscription"
    folder_path: "9.opena10_call_tracking"
    description: "Call Tracking, Metriken, Reporting"

  - id: "opena11"
    port: 12356
    name: "Zutrittskontrolle"
    role: "Auth, Berechtigungen"
    plan: "basic"
    visibility: "subscription"
    folder_path: "10.opena11_unlock"
    description: "AuthN/AuthZ, Entitlements, Tokens"

  - id: "opena12"
    port: 12357
    name: "Soziale Medien"
    role: "Twitter/LinkedIn"
    plan: "pro"
    visibility: "subscription"
    folder_path: "11.opena12_social_media"
    description: "Posting, Scheduling, Social APIs"

  - id: "opena13"
    port: 12358
    name: "Influencer"
    role: "Kampagne Mgmt"
    plan: "ultimum"
    visibility: "subscription"
    folder_path: "12.opena13_influencer"
    description: "Influencer-Kampagnen, Tracking, Workflows"

  - id: "opena14"
    port: 12359
    name: "Kalender"
    role: "Kalender-Integration"
    plan: "pro"
    visibility: "subscription"
    folder_path: "13.opena14_calendar"
    description: "Calendar Agent (Google/ICS), Termine"

  - id: "opena15"
    port: 12360
    name: "HTML-Generator"
    role: "Dynamische HTML"
    plan: "premium"
    visibility: "subscription"
    folder_path: "14.opena15_html"
    description: "HTML Generator, Templates, Export"

  - id: "opena16"
    port: 12361
    name: "Einkaufen"
    role: "E-Commerce"
    plan: "premium"
    visibility: "subscription"
    folder_path: "15.opena16_shop"
    description: "Shop/E-Commerce Agent"

  - id: "opena17"
    port: 12362
    name: "Homepage-Ersteller"
    role: "Website-Baumeister"
    plan: "ultimum"
    visibility: "subscription"
    folder_path: "16.opena17_homepagecreator"
    description: "Homepage Builder + Publishing Workflows"

  - id: "opena18"
    port: 12363
    name: "CRM"
    role: "Kundenmanagement"
    plan: "pro"
    visibility: "subscription"
    folder_path: "17.opena18_CMR"
    description: "CRM Agent"

  - id: "opena19"
    port: 12364
    name: "Finanzen"
    role: "Aktien/Krypto"
    plan: "ultimum"
    visibility: "subscription"
    folder_path: "18.opena19_Aktien&Crypto"
    description: "Finanzdaten/Workflows"

  - id: "opena20"
    port: 12349
    name: "Dashboard"
    role: "Kontrollebene"
    plan: "system"
    visibility: "system"
    folder_path: "19.opena20_dashboard_agent"
    description: "Zentrales UI + Steuerung (Control Plane)"

  - id: "opena21"
    port: 12368
    name: "Workflow"
    role: "Orchestrierung/Workflows"
    plan: "system"
    visibility: "system"
    folder_path: "20.opena21_workflow"
    description: "Workflow Engine + UI (Production)"

2) scripts/validate_baseline.py
#!/usr/bin/env python3
# ============================================================================
# validate_baseline.py
# Deterministische Baseline-Validierung für PORTIER 3.0
#
# Ziele:
# - Read-only Analyse (keine Codeausführung, kein Netzwerk)
# - Deterministische Ausgabe (stabile Reihenfolge, Hash)
# - Fail fast: Exit-Code 1 bei jeder Verletzung
#
# Validierungen:
# 1) system_baseline.yaml existiert und ist parsebar
# 2) exakt 21 Agenten: opena1..opena21 (keine Aliase)
# 3) Ports sind eindeutig
# 4) Ports liegen in allow_range und nicht in forbidden_ports
# 5) folder_path existiert im Repo und ist nicht leer
# 6) Schreib ein Artefakt artifacts/Baseline_validation.json
# ============================================================================
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml  # type: ignore
except Exception:
    print("ERROR: Missing dependency 'pyyaml'. Install via: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


ROOT = Path(__file__).resolve().parent.parent  # repo root = ../
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "Baseline_validation.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_yaml(path: Path) -> Dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("baseline yaml is not a dict")
    return data


def write_artifact(payload: Dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def stable_sort_agents(agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # deterministisch: sort by id
    return sorted(agents, key=lambda a: str(a.get("id", "")))


def err(errors: List[str], msg: str) -> None:
    errors.append(msg)


def validate() -> Tuple[bool, Dict[str, Any]]:
    errors: List[str] = []

    if not BASELINE_PATH.exists():
        err(errors, f"Missing system_baseline.yaml at: {BASELINE_PATH}")
        return False, {"errors": errors}

    raw = BASELINE_PATH.read_text(encoding="utf-8")
    baseline_hash = sha256_text(raw)

    try:
        data = load_yaml(BASELINE_PATH)
    except Exception as e:
        err(errors, f"Failed to parse system_baseline.yaml: {e}")
        return False, {"errors": errors, "baseline_hash": baseline_hash}

    port_policy = (data.get("port_policy") or {}) if isinstance(data.get("port_policy"), dict) else {}
    allow_range = port_policy.get("allow_range") or {}
    forbidden_ports = set(port_policy.get("forbidden_ports") or [])
    min_port = int(allow_range.get("min", 0))
    max_port = int(allow_range.get("max", 0))

    agents = data.get("agents") or []
    if not isinstance(agents, list):
        err(errors, "agents must be a list")
        agents = []

    agents = stable_sort_agents([a for a in agents if isinstance(a, dict)])

    # 1) exakt opena1..opena21
    expected_ids = [f"opena{i}" for i in range(1, 22)]
    got_ids = [str(a.get("id", "")).strip() for a in agents]
    if got_ids != sorted(got_ids):
        err(errors, "agents list is not sorted deterministically by id (should be sorted).")

    missing = [i for i in expected_ids if i not in got_ids]
    extra = [i for i in got_ids if i not in expected_ids]
    if missing:
        err(errors, f"Missing agent IDs: {missing}")
    if extra:
        err(errors, f"Unexpected agent IDs: {extra}")
    if len(got_ids) != 21:
        err(errors, f"Expected exactly 21 agents, got {len(got_ids)}")

    # 2) Ports: uniqueness + range + forbidden
    ports: List[int] = []
    port_map: Dict[int, List[str]] = {}
    for a in agents:
        aid = str(a.get("id", "")).strip()
        try:
            p = int(a.get("port"))
        except Exception:
            err(errors, f"{aid}: port is missing or not an int")
            continue

        ports.append(p)
        port_map.setdefault(p, []).append(aid)

        if p in forbidden_ports:
            err(errors, f"{aid}: port {p} is forbidden")
        if not (min_port <= p <= max_port):
            err(errors, f"{aid}: port {p} out of allow_range {min_port}-{max_port}")

    duplicates = {p: ids for p, ids in port_map.items() if len(ids) > 1}
    if duplicates:
        err(errors, f"Duplicate ports detected: {duplicates}")

    # 3) folder_path existiert und nicht leer
    for a in agents:
        aid = str(a.get("id", "")).strip()
        folder_path = str(a.get("folder_path", "")).strip()
        if not folder_path:
            err(errors, f"{aid}: folder_path is missing")
            continue

        abs_path = (ROOT / folder_path).resolve()
        if not abs_path.exists():
            err(errors, f"{aid}: folder_path not found: {folder_path}")
            continue

        # "nicht leer" = mindestens eine Datei/Unterordner
        try:
            has_any = any(abs_path.iterdir())
        except Exception:
            has_any = False
        if not has_any:
            err(errors, f"{aid}: folder_path is empty: {folder_path}")

    ok = len(errors) == 0
    result = {
        "timestamp_utc": utc_now(),
        "baseline_path": str(BASELINE_PATH),
        "baseline_hash_sha256": baseline_hash,
        "success": ok,
        "errors": errors,
    }
    return ok, result


def main() -> None:
    ok, payload = validate()
    write_artifact(payload)

    if not ok:
        print("BASELINE VALIDATION: FAIL", file=sys.stderr)
        for e in payload.get("errors", []):
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    print("BASELINE VALIDATION: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)


if __name__ == "__main__":
    main()

3) artifacts/Baseline_validation.json (Beispiel-Ausgabe)

Das File wird von validate_baseline.py deterministisch geschrieben. So sieht es aus, wenn alles passt:

{
  "timestamp_utc": "2025-12-25T00:00:00Z",
  "baseline_path": "/path/to/Gesamtprojekt/system_baseline.yaml",
  "baseline_hash_sha256": "REPLACE_WITH_REAL_HASH",
  "success": true,
  "errors": []
}


Und wenn es knallt (z. B. Ordner fehlt / Port doppelt):

{
  "timestamp_utc": "2025-12-25T00:00:00Z",
  "baseline_path": "/path/to/Gesamtprojekt/system_baseline.yaml",
  "baseline_hash_sha256": "REPLACE_WITH_REAL_HASH",
  "success": false,
  "errors": [
    "opena8: folder_path not found: 7.opena8_whatsapp",
    "Duplicate ports detected: {12350: ['opena7','openaX']}"
  ]
}

Mini-Notiz (weil du’s explizit wolltest, “alles niederschreiben”)


# 1) `scripts/discover_agents.py`

```python
#!/usr/bin/env python3
# ============================================================================
# discover_agents.py
# Deterministische Agentenentdeckung (rekursiv, statisch auditierbar)
#
# HARTE EINSCHRÄNKUNGEN:
# - Read-only Analyse: KEINE Codeausführung, KEINE Netzwerkaufrufe.
# - Deterministische Ausgabe: stabile Reihenfolge + Hashing.
# - Wenn ein Agentenordner fehlt/leer => FAIL.
# - Wenn Ports, die im Code/Config referenziert werden, nicht mit Baseline
#   übereinstimmen => FAIL (es sei denn: keine Portreferenzen vorhanden).
#
# INPUTS:
# - Repo Root (implizit: parent von scripts/)
# - system_baseline.yaml (Single Source of Truth)
#
# OUTPUTS (MUSS EXISTIEREN):
# - artifacts/Agent_discovery.json (timestamp, hashes, file inventory, findings)
# - Exit-Code 0 bei Erfolg, 1 bei Fehler
# ============================================================================
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception:
    print("ERROR: Missing dependency 'pyyaml'. Install via: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent  # repo root
BASELINE_PATH = ROOT / "system_baseline.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_PATH = ARTIFACTS_DIR / "Agent_discovery.json"

# ignore runtime junk (read-only scan, but we don't want noisy inventory)
IGNORE_DIRS = {
    ".git", ".github", "__pycache__", ".mypy_cache", ".pytest_cache", ".venv", "venv", "venv313", "venv312",
    "node_modules", ".idea", ".vscode", "dist", "build",
}
IGNORE_FILE_PATTERNS = [
    re.compile(r".*\.pyc$"),
    re.compile(r".*\.log$"),
    re.compile(r".*\.pid$"),
]

TEXT_FILE_EXTS = {
    ".py", ".sh", ".yml", ".yaml", ".json", ".jsonl", ".toml", ".md",
    ".html", ".css", ".js", ".txt", ".conf", ".ini",
}

# Port reference detection:
# - We scan for patterns likely to include ports:
#   12344-12399 specifically, and also explicit "http://...:PORT" occurrences.
PORT_RANGE_MIN = 12344
PORT_RANGE_MAX = 12399
PORT_NUM_RE = re.compile(r"\b(12[0-9]{3})\b")  # catches 12000-12999 then we range-filter
URL_PORT_RE = re.compile(r":(12[0-9]{3})\b")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(t: str) -> str:
    return sha256_bytes(t.encode("utf-8"))


def read_text_safe(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def is_ignored_file(path: Path) -> bool:
    name = path.name
    for pat in IGNORE_FILE_PATTERNS:
        if pat.match(name):
            return True
    return False


def should_descend_dir(path: Path) -> bool:
    return path.name not in IGNORE_DIRS


def stable_rel(p: Path) -> str:
    # deterministic relative path (posix)
    return p.relative_to(ROOT).as_posix()


def load_baseline() -> Dict[str, Any]:
    if not BASELINE_PATH.exists():
        raise FileNotFoundError(f"Missing baseline: {BASELINE_PATH}")
    raw = BASELINE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("system_baseline.yaml is not a dict")
    return data


def expected_agent_ids() -> List[str]:
    return [f"opena{i}" for i in range(1, 22)]


def build_baseline_maps(data: Dict[str, Any]) -> Tuple[Dict[str, int], Dict[str, str]]:
    agents = data.get("agents") or []
    if not isinstance(agents, list):
        raise ValueError("baseline agents must be a list")
    id_to_port: Dict[str, int] = {}
    id_to_folder: Dict[str, str] = {}
    for a in agents:
        if not isinstance(a, dict):
            continue
        aid = str(a.get("id", "")).strip()
        if not aid:
            continue
        id_to_port[aid] = int(a.get("port"))
        id_to_folder[aid] = str(a.get("folder_path", "")).strip()
    return id_to_port, id_to_folder


@dataclass(frozen=True)
class FileHit:
    file: str
    ports: List[int]


def scan_agent_folder(agent_id: str, folder: Path) -> Tuple[List[str], str]:
    """
    Returns:
      - inventory: list of relative files (deterministic order)
      - folder_hash: hash over inventory + file hashes (deterministic)
    """
    files: List[Path] = []

    # recursive walk with deterministic traversal
    stack = [folder]
    while stack:
        d = stack.pop()
        try:
            entries = sorted(list(d.iterdir()), key=lambda p: p.name)
        except Exception:
            entries = []

        # push dirs in reverse so pop() processes in correct order
        dirs = []
        for e in entries:
            if e.is_dir():
                if should_descend_dir(e):
                    dirs.append(e)
            elif e.is_file():
                if not is_ignored_file(e):
                    files.append(e)
        for dd in reversed(dirs):
            stack.append(dd)

    rel_files = [stable_rel(p) for p in files]
    rel_files.sort()  # stable

    # hash: include each file relpath + sha256(content)
    h = hashlib.sha256()
    for rf in rel_files:
        h.update(rf.encode("utf-8"))
        h.update(b"\n")
        absp = ROOT / rf
        try:
            content = absp.read_bytes()
        except Exception:
            content = b""
        h.update(sha256_bytes(content).encode("utf-8"))
        h.update(b"\n")
    return rel_files, h.hexdigest()


def find_port_references_in_text(text: str) -> List[int]:
    hits: List[int] = []
    for m in PORT_NUM_RE.finditer(text):
        try:
            p = int(m.group(1))
        except Exception:
            continue
        if PORT_RANGE_MIN <= p <= PORT_RANGE_MAX:
            hits.append(p)
    # also catch url ports (same range filter anyway)
    for m in URL_PORT_RE.finditer(text):
        try:
            p = int(m.group(1))
        except Exception:
            continue
        if PORT_RANGE_MIN <= p <= PORT_RANGE_MAX:
            hits.append(p)
    # unique sorted
    return sorted(set(hits))


def scan_ports_in_files(file_list: List[str]) -> Tuple[List[FileHit], List[int]]:
    """
    Looks for port references in text-like files only.
    Returns:
      - file_hits: list of files that contain ports
      - ports_used: unique sorted list of referenced ports
    """
    hits: List[FileHit] = []
    used: List[int] = []

    for rf in file_list:
        p = ROOT / rf
        if p.suffix.lower() not in TEXT_FILE_EXTS:
            continue
        txt = read_text_safe(p)
        if txt is None:
            continue
        ports = find_port_references_in_text(txt)
        if ports:
            hits.append(FileHit(file=rf, ports=ports))
            used.extend(ports)

    used_unique = sorted(set(used))
    hits_sorted = sorted(hits, key=lambda x: x.file)
    return hits_sorted, used_unique


def write_artifact(payload: Dict[str, Any]) -> None:
    ARTIFACT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fail(errors: List[str], msg: str) -> None:
    errors.append(msg)


def main() -> None:
    errors: List[str] = []
    warnings: List[str] = []

    # Load baseline
    try:
        baseline_raw = BASELINE_PATH.read_text(encoding="utf-8")
        baseline_hash = sha256_text(baseline_raw)
        baseline = load_baseline()
    except Exception as e:
        fail(errors, f"Baseline load failed: {e}")
        baseline_hash = None
        baseline = {}

    if errors:
        payload = {
            "timestamp_utc": utc_now(),
            "success": False,
            "errors": errors,
            "warnings": warnings,
        }
        write_artifact(payload)
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        sys.exit(1)

    id_to_port, id_to_folder = build_baseline_maps(baseline)

    # Validate baseline contains all opena1..opena21
    exp = expected_agent_ids()
    missing_ids = [i for i in exp if i not in id_to_folder or not id_to_folder[i]]
    extra_ids = [i for i in id_to_folder.keys() if i not in exp]
    if missing_ids:
        fail(errors, f"Baseline missing folder_path for: {missing_ids}")
    if extra_ids:
        fail(errors, f"Baseline contains unexpected agent IDs: {sorted(extra_ids)}")

    # Discover each agent folder deterministically
    discovered: List[Dict[str, Any]] = []
    all_referenced_ports: Dict[str, List[int]] = {}

    for aid in exp:
        folder_rel = id_to_folder.get(aid, "")
        if not folder_rel:
            continue  # already error’d above
        folder_abs = (ROOT / folder_rel).resolve()

        if not folder_abs.exists():
            fail(errors, f"{aid}: folder_path not found: {folder_rel}")
            continue
        if not folder_abs.is_dir():
            fail(errors, f"{aid}: folder_path is not a directory: {folder_rel}")
            continue

        # not empty
        try:
            nonempty = any(folder_abs.iterdir())
        except Exception:
            nonempty = False
        if not nonempty:
            fail(errors, f"{aid}: agent folder is empty: {folder_rel}")
            continue

        inventory, folder_hash = scan_agent_folder(aid, folder_abs)

        # Port reference policy:
        # - If files reference ports in [12344..12399], they must include ONLY the baseline port for that agent,
        #   OR (optional) also the coordinator port opena1 if referenced (common case).
        file_hits, ports_used = scan_ports_in_files(inventory)
        all_referenced_ports[aid] = ports_used

        base_port = int(id_to_port.get(aid, -1))
        coordinator_port = int(id_to_port.get("opena1", -1))

        if ports_used:
            allowed = {base_port}
            # allow referencing coordinator port (common config)
            if coordinator_port > 0:
                allowed.add(coordinator_port)

            bad = [p for p in ports_used if p not in allowed]
            if bad:
                fail(
                    errors,
                    f"{aid}: found port references not matching baseline. "
                    f"allowed={sorted(allowed)} found={ports_used} bad={bad}"
                )

        discovered.append(
            {
                "id": aid,
                "folder_path": folder_rel,
                "baseline_port": base_port,
                "inventory_count": len(inventory),
                "folder_hash_sha256": folder_hash,
                "inventory_files": inventory,  # deterministic list
                "port_references": {
                    "ports_used": ports_used,
                    "files": [{"file": h.file, "ports": h.ports} for h in file_hits],
                },
            }
        )

    # Global determinism & hash
    discovered_sorted = sorted(discovered, key=lambda x: x["id"])
    h = hashlib.sha256()
    h.update((baseline_hash or "").encode("utf-8"))
    h.update(b"\n")
    for a in discovered_sorted:
        h.update(a["id"].encode("utf-8"))
        h.update(b"\n")
        h.update(a["folder_hash_sha256"].encode("utf-8"))
        h.update(b"\n")
    discovery_hash = h.hexdigest()

    success = len(errors) == 0

    payload = {
        "timestamp_utc": utc_now(),
        "success": success,
        "baseline_hash_sha256": baseline_hash,
        "discovery_hash_sha256": discovery_hash,
        "repo_root": str(ROOT),
        "agents_discovered_count": len(discovered_sorted),
        "agents_expected": exp,
        "agents": discovered_sorted,
        "warnings": warnings,
        "errors": errors,
    }

    write_artifact(payload)

    if not success:
        print("AGENT DISCOVERY: FAIL", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        print(f"Artifact written: {ARTIFACT_PATH}", file=sys.stderr)
        sys.exit(1)

    print("AGENT DISCOVERY: OK")
    print(f"Artifact written: {ARTIFACT_PATH}")
    sys.exit(0)


if __name__ == "__main__":
    main()
```

---

# 2) `artifacts/Agent_discovery.json` (Beispiel-Form)

> Wird **deterministisch** erzeugt. (In echt ist `inventory_files` lang — ist gewollt: auditierbar.)

```json
{
  "timestamp_utc": "2025-12-25T00:00:00Z",
  "success": true,
  "baseline_hash_sha256": "…",
  "discovery_hash_sha256": "…",
  "repo_root": "/…/Gesamtprojekt",
  "agents_discovered_count": 21,
  "agents_expected": ["opena1","opena2", "...", "opena21"],
  "agents": [
    {
      "id": "opena8",
      "folder_path": "7.opena8_whatsapp",
      "baseline_port": 12353,
      "inventory_count": 42,
      "folder_hash_sha256": "…",
      "inventory_files": [
        "7.opena8_whatsapp/frontend/index.html",
        "7.opena8_whatsapp/frontend/app.js"
      ],
      "port_references": {
        "ports_used": [12353, 12344],
        "files": [
          {"file":"7.opena8_whatsapp/frontend/config.js","ports":[12353,12344]}
        ]
      }
    }
  ],
  "warnings": [],
  "errors": []
}
```

---

# 3) So läuft’s (lokal + CI)

```bash
python3 scripts/discover_agents.py
# Exit 0 = OK
# Exit 1 = FAIL (mit konkreten Fehlern + Artifact)
```

---

## Was das Ding exakt absichert (ohne Diskussion 😄)

* **Jeder Agentenordner existiert** (aus `folder_path`)
* **Jeder Agentenordner ist nicht leer**
* **Rekursive Inventarisierung** (stabile Sortierung)
* **Folder Hash** pro Agent + **Discovery Hash** global
* **Portreferenzen im Code/Config**:

  * Wenn ein Agent **Ports erwähnt**, dürfen das nur sein:

    * **sein eigener Baseline-Port**
    * optional zusätzlich **opena1-Port** (Koordinator), weil das realistisch überall auftaucht
  * Alles andere = **FAIL**

---

## Ausgabe 4/4 — **CI-Gate + Ops-Wrapper (produktreif, deterministisch)**

Hier ist **Teil 4**: der **verbindliche Gate-Layer**, der **Baseline + Discovery** erzwingt – lokal **und** in CI.
Keine Strukturänderung. **Fail-fast**, auditierbar, company-tauglich.

---

# 1) Ops-Wrapper (lokal & CI identisch)

## `bin/verify_baseline_and_discovery.sh`

```bash
#!/usr/bin/env bash
# ============================================================================
# verify_baseline_and_discovery.sh
# Gate für PORTIER / ELION Hyper-Dashboard
#
# Aufgaben:
# - Prüft Existenz der system_baseline.yaml
# - Führt die deterministische Agenten-Discovery aus
# - Bricht bei JEDEM Fehler hart ab (Exit 1)
# - Erzeugt reproduzierbare Artefakte
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASELINE="${ROOT}/system_baseline.yaml"
DISCOVER="${ROOT}/scripts/discover_agents.py"
ARTIFACTS="${ROOT}/artifacts"

echo "[GATE] ROOT=${ROOT}"

if [[ ! -f "${BASELINE}" ]]; then
  echo "[GATE][FAIL] Missing system_baseline.yaml at ${BASELINE}" >&2
  exit 1
fi

if [[ ! -f "${DISCOVER}" ]]; then
  echo "[GATE][FAIL] Missing discovery script at ${DISCOVER}" >&2
  exit 1
fi

mkdir -p "${ARTIFACTS}"

echo "[GATE] Running deterministic agent discovery…"
python3 "${DISCOVER}"

echo "[GATE] OK — Baseline & Discovery verified"
```

**Eigenschaften**

* **Ein Befehl** für Dev/Ops/CI
* **Kein Netzwerk**, **kein Code-Exec** in Discovery
* **Exit 1** bei kleinster Abweichung

---

# 2) GitHub Actions — Hard Gate

## `.github/workflows/baseline-discovery-gate.yml`

```yaml
name: Baseline & Agent Discovery Gate

on:
  pull_request:
    branches: [ "main", "master" ]
  push:
    branches: [ "main", "master" ]

jobs:
  gate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install minimal deps
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml

      - name: Run Baseline & Discovery Gate
        run: |
          chmod +x bin/verify_baseline_and_discovery.sh
          ./bin/verify_baseline_and_discovery.sh

      - name: Upload Discovery Artifact
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: agent-discovery
          path: artifacts/Agent_discovery.json
```

**Warum so gebaut**

* **PR-Blocker**: nichts merged ohne konsistente Baseline
* **Artefakt** immer verfügbar (auch bei FAIL)
* **Minimal-Deps** (nur `pyyaml`)

---

# 3) Projekt-Regel (README-Snippet)

> **Pflichtregel (bindend):**
>
> * `system_baseline.yaml` ist **Single Source of Truth**
> * **Jede** Änderung an Agenten/Ports/Ordnern **muss** den Gate-Check bestehen
> * **Keine** Hardcoded-Ports außerhalb der Baseline
> * **Kein** leerer Agentenordner
>
> **Befehl (lokal & CI identisch):**
>
> ```bash
> ./bin/verify_baseline_and_discovery.sh
> ```

---

