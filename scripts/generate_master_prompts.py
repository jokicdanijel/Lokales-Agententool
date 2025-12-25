#!/usr/bin/env python3
"""
Generator für 21 Agent-spezifische Master-Prompts (opena3-opena21)
Erstellt MASTER_PROMPT.md-Dateien in den jeweiligen Agent-Ordnern
"""

from pathlib import Path

# Base-Verzeichnis
BASE_DIR = Path("/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt")

# Agent-Konfiguration
AGENTS = [
    {
        "id": "opena5",
        "folder": "4.opena5_vscode",
        "port": 12351,
        "status": "🟡 Planned",
        "kuerzel": "vscop",
        "domain": "VS Code Agent, File-System-Watcher, Code-Analyse",
    },
    {
        "id": "opena6",
        "folder": "5.opena6_browser",
        "port": 12350,
        "status": "🟡 Planned",
        "kuerzel": "browsep",
        "domain": "Browser Automation, Playwright, Selenium, Web-Scraping",
    },
    {
        "id": "opena7",
        "folder": "6.opena7_email",
        "port": 12352,
        "status": "🟡 Planned",
        "kuerzel": "emailp",
        "domain": "E-Mail Client, IMAP/SMTP, Inbox-Monitoring",
    },
    {
        "id": "opena8",
        "folder": "7.opena8_whatsapp",
        "port": 12353,
        "status": "🟡 Planned",
        "kuerzel": "whatsappp",
        "domain": "WhatsApp Business Cloud API, Webhook, Templates",
    },
    {
        "id": "opena9",
        "folder": "8.opena9_telephone",
        "port": 12354,
        "status": "🟡 Planned",
        "kuerzel": "telphonep",
        "domain": "Telefonie, SIP/Twilio, Call-State-Machine",
    },
    {
        "id": "opena10",
        "folder": "9.opena10_call_tracking",
        "port": 12355,
        "status": "🟡 Planned",
        "kuerzel": "calltrackp",
        "domain": "Call Tracking, SQLAlchemy-Models, Campaign-Tracking",
    },
    {
        "id": "opena11",
        "folder": "10.opena11_unlock",
        "port": 12356,
        "status": "🟡 Planned",
        "kuerzel": "unlockp",
        "domain": "Unlock Master, RBAC, Permission-Store, Audit-Log",
    },
    {
        "id": "opena12",
        "folder": "11.opena12_social_media",
        "port": 12357,
        "status": "🟡 Planned",
        "kuerzel": "smp",
        "domain": "Social Media, Multi-Platform OAuth, Scheduling",
    },
    {
        "id": "opena13",
        "folder": "12.opena13_influencer",
        "port": 12358,
        "status": "🟡 Planned",
        "kuerzel": "influp",
        "domain": "Influencer-Matching, Kampagnen, Reichweiten-Metriken",
    },
    {
        "id": "opena14",
        "folder": "13.opena14_calendar",
        "port": 12359,
        "status": "🟡 Planned",
        "kuerzel": "calp",
        "domain": "Google Calendar, iCal, Exchange-Integration",
    },
    {
        "id": "opena15",
        "folder": "14.opena15_html",
        "port": 12360,
        "status": "🟡 Planned",
        "kuerzel": "htmlp",
        "domain": "HTML Creator, Jinja2, Template-Rendering, Validation",
    },
    {
        "id": "opena16",
        "folder": "15.opena16_shop",
        "port": 12361,
        "status": "🟡 Planned",
        "kuerzel": "shopp",
        "domain": "Shop Agent, Shopify, WooCommerce, Product-Sync",
    },
    {
        "id": "opena17",
        "folder": "16.opena17_homepagecreator",
        "port": 12362,
        "status": "🟡 Planned",
        "kuerzel": "hpcreatep",
        "domain": "Homepage Creator, Site-Generator, Deployment",
    },
    {
        "id": "opena18",
        "folder": "17.opena18_CMR",
        "port": 12363,
        "status": "🟡 Planned",
        "kuerzel": "crmp",
        "domain": "CRM Agent, Contacts, Deals, DSGVO-Compliance",
    },
    {
        "id": "opena19",
        "folder": "18.opena19_Aktien&Crypto",
        "port": 12364,
        "status": "🟡 Planned",
        "kuerzel": "stockcryptop",
        "domain": "Aktien & Crypto, Marktdaten, Portfolio, Alerts",
    },
    {
        "id": "opena20",
        "folder": "19.opena20_dashboard_agent",
        "port": 12349,
        "status": "✅ Running",
        "kuerzel": "dashp",
        "domain": "Dashboard, FastAPI, SSE, Web-UI, Status-Aggregation",
    },
    {
        "id": "opena21",
        "folder": "20.opena21_workflow",
        "port": 12365,
        "status": "🟡 Planned",
        "kuerzel": "workflowp",
        "domain": "Workflow Engine, State-Machine, Task-Queue, Multi-Agent-Orchestration",
    },
]

TEMPLATE = """# 🤖 MASTER PROMPT – {id} {name}

**Agent-ID:** {id}
**Port:** {port}
**Status:** {status}
**Kürzel:** `{kuerzel}`
**Domäne:** {domain}

---

## 🎯 Rolle & Zielsetzung

Du bist der **Co-Pilot für {id}**, verantwortlich für die vollständige Ausführung aller Aufgaben gemäß festgelegter Regeln. Alle Schritte werden **vollautomatisch** durchgeführt, ohne Rückfragen.

**Ziel:** {domain}

**Scope:** Option-2-Flow-Compliance, Port-Policy-Enforcement, Safepoint-Archivierung.

---

## 📋 Ablauf (vollautomatisch)

### 1. Initialisierung

- ❌ Keine Rückfragen – **Starte direkt**
- ✅ Lade Config aus `.env` (ENV-only Secrets)
- ✅ Prüfe Port {port} verfügbar
- ✅ Registriere in `tool_registry.json` als `{kuerzel}`

### 2. Struktur & Setup

- ✅ FastAPI-Service `main_{agent_file}.py` (Port {port})
- ✅ Health-Endpoint `/health`
- ✅ Command-Endpoint `/command` (POST)
- ✅ Auth-Middleware (Bearer Token)
- ✅ Strict JSON-Schemas (`extra="forbid"`)

### 3. Konfliktlogik & Regeln

- ✅ **Option-2-Flow:** `opena1 → opena2 → kordp → {id}`
- ✅ **Keine Direktcalls** ohne Archivierung
- ✅ Safepoints für CMD/RESP-Paare
- ✅ Unicode-Pfeil `→` in Safepoint-Namen
- ✅ **Largest File Wins:** Bei Konflikten größte Datei behalten

### 4. Berichte & Artefakte

Generiere/aktualisiere:

- `rename_map.csv`
- `path_index.json`
- `violations_report.md`
- `structure_checkpoint.json`

### 5. Validierung

- ✅ Max. Verzeichnis-Tiefe: 6 Ebenen
- ✅ Keine Duplikate
- ✅ Secrets niemals hardcoded
- ✅ Port-Policy: 12344-12399 (Backend), 8080 verboten

### 6. Dry-Run

Führe Simulation durch:

- Gib detaillierten Plan aus
- **Keine Änderungen durchführen**
- Validiere externe Abhängigkeiten

### 7. Apply

Falls Dry-Run erfolgreich:

- ✅ Änderungen anwenden
- ✅ PID-File schreiben (`logs/{id}.pid`)

### 8. Finalisierung

- ✅ Berichte speichern (`docs/{id}_report.md`)
- ✅ Logs rotieren (`logs/{id}.nohup.log`)

---

## 📦 Eingabeparameter (optional)

```json
{{
  "port": {port},
  "dry_run": true,
  "max_retries": 3,
  "timeout": 30
}}
```

---

## 📤 Ausgabe

### Erfolgreich

```json
{{
  "status": "success",
  "agent": "{id}",
  "port": {port},
  "safepoints_created": 5,
  "violations": 0
}}
```

### Fehler

```json
{{
  "status": "error",
  "agent": "{id}",
  "error_code": "PORT_CONFLICT",
  "message": "Port {port} bereits belegt"
}}
```

---

## 🔧 Spezifische Regeln für {id}

1. **ENV-only Secrets:** Niemals hardcoden
2. **Option-2-Flow:** Immer einhalten
3. **Safepoint-Archivierung:** Append-only, YYYY/MM/DD
4. **Port-Policy:** Nur 12344-12399
5. **Strict JSON:** `extra="forbid"` in allen Pydantic-Models

---

## 🚀 Verwendung in VSCode Copilot

Kopiere diesen Prompt in:

- **Chat:** Als System-Prompt für Agent-spezifische Aufgaben
- **Datei:** `{folder}/MASTER_PROMPT.md` (Referenz)
- **Workflow:** Trigger via `bin/ops.sh {id}:init`

---

**Letzte Aktualisierung:** 27. November 2025
**Maintainer:** Danijel Jokic (ELION Team)
"""


def generate_prompts():
    """Generiert alle MASTER_PROMPT.md-Dateien"""
    created = []
    skipped = []

    for agent in AGENTS:
        # Extrahiere Agent-Name aus Domain (erster Teil vor Komma)
        name = agent["domain"].split(",")[0].strip()

        # Agent-File-Name (ohne opena)
        agent_file = agent["id"].replace("opena", "agent")

        # Erstelle Prompt-Content
        content = TEMPLATE.format(
            id=agent["id"],
            name=name,
            port=agent["port"],
            status=agent["status"],
            kuerzel=agent["kuerzel"],
            domain=agent["domain"],
            folder=agent["folder"],
            agent_file=agent_file,
        )

        # Zielordner und Datei
        target_dir = BASE_DIR / agent["folder"]
        target_file = target_dir / "MASTER_PROMPT.md"

        # Prüfe ob Ordner existiert
        if not target_dir.exists():
            print(f"⚠️  Ordner nicht gefunden: {target_dir}")
            skipped.append(agent["id"])
            continue

        # Schreibe Datei (überschreibe wenn existiert)
        target_file.write_text(content, encoding="utf-8")
        created.append(agent["id"])
        print(f"✅ Erstellt: {target_file}")

    # Zusammenfassung
    print("\n📊 Zusammenfassung:")
    print(f"   ✅ Erstellt: {len(created)} Dateien")
    print(f"   ⚠️  Übersprungen: {len(skipped)} Dateien")
    print(f"\n📝 Erstellt für: {', '.join(created)}")
    if skipped:
        print(f"⚠️  Übersprungen: {', '.join(skipped)}")


if __name__ == "__main__":
    generate_prompts()
