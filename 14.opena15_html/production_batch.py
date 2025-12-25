#!/usr/bin/env python3
"""
🚀 OPENA15 Production HTML Generator

Vollautomatische HTML-Generierung via opena15 API
- Batch-Processing für mehrere Templates
- Validierung & Error-Handling
- Comprehensive Logging
- Option-2-Flow konform

Usage:
    python3 production_batch.py
    python3 production_batch.py --validate
    python3 production_batch.py --templates-list
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

# ============================================================================
# CONFIG
# ============================================================================

OPENA15_URL = "http://127.0.0.1:12360"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"
PROJECT_ROOT = Path(__file__).parent.parent

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}", "Content-Type": "application/json"}

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "production_output"
REPORTS_DIR = BASE_DIR / "production_reports"

OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# AGENT-DATEN (für Dashboard-Generierung)
# ============================================================================

# Ordner-Mapping (Agent-ID → Ordnername)
AGENT_DIRS = {
    "opena3": "2.opena3_openwebui",
    "opena4": "3.opena4_telegram",
    "opena5": "4.opena5_vscode",
    "opena6": "5.opena6_browser",
    "opena7": "6.opena7_email",
    "opena8": "7.opena8_whatsapp",
    "opena9": "8.opena9_telephone",
    "opena10": "9.opena10_call_tracking",
    "opena11": "10.opena11_unlock",
    "opena12": "11.opena12_social_media",
    "opena13": "12.opena13_influencer",
    "opena14": "13.opena14_calendar",
    "opena15": "14.opena15_html",
    "opena16": "15.opena16_shop",
    "opena17": "16.opena17_homepagecreator",
    "opena18": "17.opena18_CMR",
    "opena19": "18.opena19_Aktien&Crypto",
}

# Template-Mapping (Agent-ID → spezialisiertes Template)
# DEPRECATED: Jetzt via ui_profile + Partials-System
AGENT_TEMPLATES = {
    # Alle Agenten nutzen jetzt agent_dashboard_v2.html.j2 mit Partial-Includes
}

AGENTS = [
    {"id": "opena3", "name": "OpenWebUI Terminal", "kuerzel": "owuip", "port": 12347},
    {"id": "opena4", "name": "Telegram Agent", "kuerzel": "telep", "port": 12348},
    {"id": "opena5", "name": "VS Code Agent", "kuerzel": "vscop", "port": 12351},
    {"id": "opena6", "name": "Browser Agent", "kuerzel": "browsep", "port": 12352},
    {"id": "opena7", "name": "Email Agent", "kuerzel": "emailp", "port": 12353},
    {"id": "opena8", "name": "WhatsApp Agent", "kuerzel": "whatsappp", "port": 12354},
    {"id": "opena9", "name": "Telefonie Agent", "kuerzel": "telphonep", "port": 12355},
    {"id": "opena10", "name": "Call Tracking Agent", "kuerzel": "calltrackp", "port": 12356},
    {"id": "opena11", "name": "Unlock Agent", "kuerzel": "unlockp", "port": 12357},
    {"id": "opena12", "name": "Social Media Agent", "kuerzel": "smp", "port": 12358},
    {"id": "opena13", "name": "Influencer Agent", "kuerzel": "influp", "port": 12359},
    {"id": "opena14", "name": "Calendar Agent", "kuerzel": "calp", "port": 12360},
    {"id": "opena15", "name": "HTML Creator", "kuerzel": "htmlp", "port": 12361},
    {"id": "opena16", "name": "Shop Agent", "kuerzel": "shopp", "port": 12362},
    {"id": "opena17", "name": "Homepage Creator", "kuerzel": "hpcreatep", "port": 12363},
    {"id": "opena18", "name": "CRM Agent", "kuerzel": "crmp", "port": 12364},
    {"id": "opena19", "name": "Stocks & Crypto", "kuerzel": "stockcryptop", "port": 12365},
]

# ============================================================================
# README PARSER
# ============================================================================


def parse_readme(agent_id: str) -> dict[str, Any]:
    """Parse README.md aus Agent-Ordner - extrahiert Role, Features & UI-Profile"""
    agent_dir = AGENT_DIRS.get(agent_id)
    if not agent_dir:
        return {}

    readme_path = PROJECT_ROOT / agent_dir / "README.md"
    if not readme_path.exists():
        return {}

    try:
        content = readme_path.read_text(encoding="utf-8")

        # ===== UI-PROFILE DETECTION =====
        ui_profile = "generic"
        endpoints = {}
        workflows = []

        def contains(*patterns):
            return any(re.search(p, content, re.IGNORECASE) for p in patterns)

        # Detect UI Profile
        if contains(r"Telegram", r"/send", r"/webhook", r"/conversations"):
            ui_profile = "telegram_bot"
            workflows.append("message_flow: receive → process → respond")
        elif contains(r"WhatsApp", r"Meta", r"/webhook") and contains(r"/conversations"):
            ui_profile = "whatsapp_agent"
            workflows.append("message_flow: receive → process → respond")
        elif contains(r"Browser", r"Scrap", r"Playwright") and contains(r"/run"):
            ui_profile = "browser_automation"
            workflows.append("run_flow: url_input → execute_playbook → collect_results")
        elif contains(r"E-?Mail", r"IMAP", r"SMTP"):
            ui_profile = "email_agent"
            workflows.append("mail_flow: fetch_inbox → display → reply/send")
        elif contains(r"Calendar", r"/events"):
            ui_profile = "calendar_agent"
            workflows.append("event_flow: list → create → update → delete")
        elif contains(r"Shop", r"/products", r"/orders"):
            ui_profile = "shop_agent"
            workflows.append("product_flow: sync → update → order_management")
        elif contains(r"CRM", r"Customer"):
            ui_profile = "crm_agent"
            workflows.append("customer_flow: manage → track → analyze")

        # Extract Endpoints
        for route in [
            "/send",
            "/webhook",
            "/conversations",
            "/run",
            "/api/status",
            "/api/e2e",
            "/status",
            "/e2e",
            "/safepoints",
            "/events/list",
            "/events/create",
            "/inbox",
            "/outbox",
            "/generate",
            "/validate",
            "/products/sync",
            "/orders/list",
        ]:
            if route in content:
                key = route.strip("/").replace("/", "_")
                endpoints[key] = route

        # Extrahiere "Role:" Zeile (nach "## Überblick" oder ähnlich)
        role_match = re.search(r"\*\*Role:\*\*\s*(.+?)(?:\n|$)", content)
        if role_match:
            beschreibung = role_match.group(1).strip()
        else:
            # Fallback: Erste Zeile nach ## Überschrift
            overview_match = re.search(r"##[^#]+?Überblick[^#]*?\n\n(.+?)(?:\n\n|\n\*\*|$)", content, re.DOTALL)
            if overview_match:
                beschreibung = overview_match.group(1).strip().split("\n")[0]
            else:
                beschreibung = ""

        # Bereinige Markdown
        beschreibung = re.sub(r"\*\*(.+?)\*\*", r"\1", beschreibung)  # Bold
        beschreibung = re.sub(r"`(.+?)`", r"\1", beschreibung)  # Code
        beschreibung = re.sub(r"[🎯📧🚀✅🔧💬📱📞🔓🎤📊🎨🛒🏠💼📈🌐💡🔒📝🔄]", "", beschreibung)  # Emojis
        beschreibung = beschreibung.strip()

        # Extrahiere Features aus "## Features" Sektion
        features = []
        features_section = re.search(r"##\s*Features[^\n]*\n((?:[-*]\s+.+\n?)+)", content, re.IGNORECASE)

        if features_section:
            feature_lines = features_section.group(1).strip().split("\n")
            for line in feature_lines[:6]:  # Max 6 Features
                match = re.match(r"[-*]\s+(.+)", line)
                if match:
                    feature = match.group(1).strip()
                    # Bereinige
                    feature = re.sub(r"\*\*(.+?)\*\*", r"\1", feature)
                    feature = re.sub(r"`(.+?)`", r"\1", feature)
                    feature = re.sub(r"[🎯📧🚀✅🔧💬📱📞🔓🎤📊🎨🛒🏠💼📈🌐💡🔒📝🔄]", "", feature)
                    feature = feature.strip()
                    if feature and len(feature) > 8 and not feature.startswith("http"):
                        features.append(feature)

        # Fallback: Suche generell nach Listen-Items
        if not features:
            feature_matches = re.findall(r"[-*]\s+(.+?)(?:\n|$)", content)
            for match in feature_matches[:6]:
                feature = re.sub(r"\*\*(.+?)\*\*", r"\1", match)
                feature = re.sub(r"`(.+?)`", r"\1", feature)
                feature = re.sub(r"[🎯📧🚀✅🔧💬📱📞🔓🎤📊🎨🛒🏠💼📈🌐💡🔒📝🔄]", "", feature)
                feature = feature.strip()
                if feature and len(feature) > 15 and ":" not in feature[:5]:
                    features.append(feature)

        return {
            "beschreibung": beschreibung if beschreibung else "ELION/Portier Agent",
            "features": features[:5] if features else [],
            "ui_profile": ui_profile,
            "endpoints": endpoints,
            "workflows": workflows,
        }
    except Exception as e:
        print(f"   ⚠️  README parse error for {agent_id}: {e}")
        return {"ui_profile": "generic", "endpoints": {}, "workflows": []}


# ============================================================================
# API FUNCTIONS
# ============================================================================


def check_opena15_health() -> bool:
    """Prüfe opena15 Health-Status"""
    try:
        response = requests.get(f"{OPENA15_URL}/health", timeout=3)
        if response.status_code == 200:
            health = response.json()
            print("✅ opena15 ONLINE")
            print(f"   Port: {health.get('port')}")
            print(f"   Uptime: {health.get('uptime_seconds', 0):.0f}s")
            print(f"   Templates: {health.get('templates_available', 0)}")
            print(f"   Jinja2: {health.get('jinja2_support', False)}")
            return True
        else:
            print(f"⚠️  opena15 Status: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ opena15 OFFLINE: {e}")
        return False


def list_templates() -> list[dict[str, Any]]:
    """Liste verfügbare Templates"""
    try:
        response = requests.get(f"{OPENA15_URL}/templates", headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("templates", [])
        else:
            print(f"❌ Fehler beim Template-Abruf: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Template-Abruf fehlgeschlagen: {e}")
        return []


def generate_html(
    agent: dict[str, Any], template_name: str | None = None, css_framework: str = "bootstrap"
) -> dict[str, Any] | None:
    """
    Generiere HTML via opena15 /generate Endpoint MIT README-Daten

    Wählt automatisch das passende Template basierend auf Agent-Typ:
    - opena4 → telegram_dashboard.html.j2
    - opena6 → browser_dashboard.html.j2
    - opena7 → email_dashboard.html.j2
    - default → agent_dashboard.html.j2

    Returns:
        API-Response dict oder None bei Fehler
    """
    # Auto-Select Template basierend auf Agent-ID
    # Alle Agenten nutzen jetzt agent_dashboard.html.j2 mit ui_profile-basiertem Partial-System
    if not template_name:
        template_name = "agent_dashboard.html.j2"

    # Parse README für echte Daten
    readme_data = parse_readme(agent["id"])

    # Erweiterte Variablen mit UI-Profile
    variables = {
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "kuerzel": agent["kuerzel"],
        "port": agent["port"],
        "slug": agent["id"],  # z.B. "opena4"
        "beschreibung": readme_data.get("beschreibung") or f"{agent['name']} - ELION/Portier Agent",
        "features": readme_data.get("features")
        or ["Option-2-Flow Integration", "Health-Check Endpoint", "Bearer Token Security"],
        "ui_profile": readme_data.get("ui_profile", "generic"),
        "endpoints": readme_data.get("endpoints", {}),
        "workflows": readme_data.get("workflows", []),
    }

    payload = {
        "template_name": template_name,
        "variables": variables,
        "css_framework": css_framework,
        "title": f"{agent['name']} Dashboard",
    }

    try:
        response = requests.post(f"{OPENA15_URL}/generate", json=payload, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"   ❌ Fehler: {e}")
        return None


def validate_html(html: str, validation_level: str = "standard") -> dict[str, Any]:
    """Validiere HTML via opena15 /validate"""
    try:
        response = requests.post(
            f"{OPENA15_URL}/validate",
            json={"html": html, "validation_level": validation_level},
            headers=HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {"valid": False, "errors": [f"HTTP {response.status_code}"]}

    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


# ============================================================================
# BATCH PROCESSING
# ============================================================================


def batch_generate_dashboards() -> dict[str, Any]:
    """
    Generiere Dashboards für alle 17 Agenten

    Returns:
        Statistiken & Ergebnisse
    """
    print("\n" + "=" * 80)
    print("  🎨 BATCH DASHBOARD-GENERIERUNG")
    print("=" * 80)
    print(f"\nAgenten: {len(AGENTS)}")
    print("Template: agent_dashboard.html.j2")
    print("Framework: Bootstrap 5\n")

    results = []
    success_count = 0
    start_time = time.time()

    for i, agent in enumerate(AGENTS, 1):
        print(f"[{i:2d}/{len(AGENTS)}] {agent['id']:10s} ", end="", flush=True)

        # Generiere mit README-Daten
        result = generate_html(agent)

        if result:
            file_path = Path(result.get("file_path", ""))
            file_size = file_path.stat().st_size / 1024 if file_path.exists() else 0
            print(f"✅ {file_path.name} ({file_size:.1f} KB)")
            success_count += 1
            results.append(
                {
                    "agent": agent,
                    "success": True,
                    "result": result,
                    "file_path": str(file_path),
                    "file_size_kb": file_size,
                }
            )
        else:
            print("❌ Generierung fehlgeschlagen")
            results.append({"agent": agent, "success": False, "error": "API-Call fehlgeschlagen"})

        time.sleep(0.05)  # Rate limiting

    duration = time.time() - start_time

    print("\n" + "=" * 80)
    print("  📊 ZUSAMMENFASSUNG")
    print("=" * 80)
    print(f"✅ Erfolgreich:  {success_count}/{len(AGENTS)}")
    print(f"❌ Fehler:       {len(AGENTS) - success_count}/{len(AGENTS)}")
    print(f"⏱️  Dauer:        {duration:.2f}s")
    print(f"📁 Output:       {OUTPUT_DIR}")
    print("=" * 80)

    return {
        "total": len(AGENTS),
        "success": success_count,
        "failed": len(AGENTS) - success_count,
        "duration_seconds": duration,
        "results": results,
    }


def save_report(stats: dict[str, Any], filename: str = "batch_report.json"):
    """Speichere Batch-Report"""
    report_path = REPORTS_DIR / filename

    report = {
        "timestamp": datetime.now().isoformat(),
        "opena15_url": OPENA15_URL,
        "statistics": stats,
        "agents_processed": len(AGENTS),
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Report gespeichert: {report_path}")


# ============================================================================
# CLI
# ============================================================================


def main():
    """Main Entry Point"""
    parser = argparse.ArgumentParser(description="opena15 Production HTML Generator")
    parser.add_argument("--validate", action="store_true", help="Validiere generierte HTML-Dateien")
    parser.add_argument("--templates-list", action="store_true", help="Liste verfügbare Templates")
    parser.add_argument("--health-only", action="store_true", help="Nur Health-Check")

    args = parser.parse_args()

    print("=" * 80)
    print("  🚀 OPENA15 PRODUCTION HTML GENERATOR")
    print("=" * 80)

    # Health-Check
    if not check_opena15_health():
        print("\n❌ opena15 nicht erreichbar. Bitte starten:")
        print("   ./bin/start_opena15.sh")
        sys.exit(1)

    if args.health_only:
        sys.exit(0)

    # Templates auflisten
    if args.templates_list:
        print("\n📚 Verfügbare Templates:")
        templates = list_templates()
        if templates:
            for tmpl in templates:
                print(f"   - {tmpl['name']} ({tmpl['size']} Bytes)")
        else:
            print("   (keine Templates gefunden)")
        sys.exit(0)

    # Batch-Generierung
    stats = batch_generate_dashboards()

    # Report speichern
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_report(stats, f"batch_report_{timestamp}.json")

    # Validierung (optional)
    if args.validate:
        print("\n🔍 HTML-Validierung...")
        for result in stats["results"]:
            if result["success"]:
                file_path = Path(result["file_path"])
                if file_path.exists():
                    with open(file_path, encoding="utf-8") as f:
                        html = f.read()

                    validation = validate_html(html)
                    if validation.get("valid"):
                        print(f"   ✅ {file_path.name}")
                    else:
                        print(f"   ❌ {file_path.name}: {validation.get('errors')}")

    print("\n✅ Batch-Generierung abgeschlossen!")


if __name__ == "__main__":
    main()
