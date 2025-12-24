#!/usr/bin/env python3
"""
opena20 HTML Compiler
Generates all required HTML pages for dashboard and public website

Outputs:
- public/ (landing, plans, legal)
- app/ (dashboard, agents, errors)
- auth/ (login, register, forgot-password)
- artifacts/html_manifest.json
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================


class Config:
    """HTML Compiler Configuration"""

    ROOT = Path(__file__).parent.parent.parent
    OUTPUT_DIR = ROOT / "public"
    ARTIFACTS_DIR = ROOT / "artifacts"

    INVENTORY_PATH = ARTIFACTS_DIR / "agent_inventory.json"
    ENTITLEMENTS_PATH = ROOT / "config" / "plan_entitlements.json"

    # Output directories
    PUBLIC_DIR = OUTPUT_DIR / "public"
    APP_DIR = OUTPUT_DIR / "app"
    AUTH_DIR = OUTPUT_DIR / "auth"
    LEGAL_DIR = PUBLIC_DIR / "legal"


# ============================================================================
# DATA LOADER
# ============================================================================


class DataLoader:
    """Load all data sources"""

    def __init__(self):
        self.inventory = self._load_json(Config.INVENTORY_PATH)
        self.entitlements = self._load_json(Config.ENTITLEMENTS_PATH)

    @staticmethod
    def _load_json(path: Path) -> dict:
        """Load JSON file"""
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")
        with open(path) as f:
            return json.load(f)

    def get_agents(self) -> list[dict]:
        """Get all agents"""
        agents = []
        for agent_id, data in self.inventory["agents"].items():
            agents.append(
                {
                    "id": agent_id,
                    "name": data["name"],
                    "port": data["port"],
                    "role": data["role"],
                    "visibility": data["visibility"],
                    "description": data["description"],
                    "endpoints": data.get("all_endpoints", []),
                }
            )
        return sorted(agents, key=lambda x: x["port"])

    def get_plans(self) -> dict:
        """Get all plans"""
        return self.entitlements.get("plans", {})


# ============================================================================
# HTML COMPILER
# ============================================================================


class HTMLCompiler:
    """Compile all HTML pages"""

    def __init__(self, data_loader: DataLoader):
        self.data = data_loader
        self.manifest = []

    def compile_all(self):
        """Compile all HTML pages"""
        print("🔨 Starting HTML compilation...")

        # Create directories
        Config.PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
        Config.APP_DIR.mkdir(parents=True, exist_ok=True)
        Config.AUTH_DIR.mkdir(parents=True, exist_ok=True)
        Config.LEGAL_DIR.mkdir(parents=True, exist_ok=True)

        # Public pages
        self._compile_landing_page()
        self._compile_plan_pages()
        self._compile_legal_pages()

        # App pages
        self._compile_dashboard_pages()
        self._compile_agent_pages()
        self._compile_error_pages()

        # Auth pages
        self._compile_auth_pages()

        # Save manifest
        self._save_manifest()

        print(f"✅ Compilation complete: {len(self.manifest)} pages generated")

    def _save_page(self, path: Path, content: str):
        """Save HTML page and add to manifest"""
        path.write_text(content, encoding="utf-8")

        # Calculate hash
        sha256 = hashlib.sha256(content.encode()).hexdigest()

        # Add to manifest
        self.manifest.append(
            {
                "path": str(path.relative_to(Config.OUTPUT_DIR)),
                "sha256": sha256,
                "size": len(content),
                "generated": datetime.now().isoformat(),
            }
        )

        print(f"  ✓ {path.relative_to(Config.OUTPUT_DIR)}")

    def _save_manifest(self):
        """Save HTML manifest"""
        manifest_path = Config.ARTIFACTS_DIR / "html_manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(
                {"generated": datetime.now().isoformat(), "total_pages": len(self.manifest), "pages": self.manifest},
                f,
                indent=2,
            )
        print(f"\n📋 Manifest saved: {manifest_path}")

    # ========================================================================
    # PUBLIC PAGES
    # ========================================================================

    def _compile_landing_page(self):
        """Compile public landing page"""
        agents = [a for a in self.data.get_agents() if a["visibility"] != "system"]
        plans = self.data.get_plans()

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ELION HyperDashboard – Enterprise Multi-Agent System</title>
    <meta name="description" content="21 spezialisierte AI-Agenten für Enterprise-Kommunikation, Automation und Business Intelligence. Vollständig integriert, DSGVO-konform, On-Premise möglich.">
    <meta name="eden:page" content="landing">
    <meta name="eden:generated" content="{datetime.now().isoformat()}">
</head>

<body data-page="landing">

<header>
    <h1>🤖 ELION HyperDashboard</h1>
    <p><strong>Das vollständige Multi-Agent-System für Enterprise Business</strong></p>
    <nav>
        <a href="#overview">Überblick</a>
        <a href="#agents">Agenten</a>
        <a href="#plans">Pläne</a>
        <a href="#security">Sicherheit</a>
        <a href="/login" data-action="login">Login</a>
    </nav>
</header>

<main>
    <section id="overview">
        <h2>Was ist ELION HyperDashboard?</h2>
        <p><strong>Ein vollständig integriertes Multi-Agent-System mit 21 spezialisierten AI-Agenten</strong> – entwickelt für Unternehmen, die Kommunikation, Automation und Business Intelligence zentral steuern wollen.</p>

        <article>
            <h3>🎯 Kernkonzept: Eden Architecture</h3>
            <p>Jeder Agent ist eine eigenständige Mikroservice-Einheit mit definierter Rolle, Port und API. Die zentrale Control-Plane (opena20) orchestriert Zugriff, Sichtbarkeit und Plan-Gates.</p>
            <ul>
                <li><strong>Koordination:</strong> opena1 (zentraler Router) + opena2 (vollständiges Archiv)</li>
                <li><strong>Kommunikation:</strong> Telegram, WhatsApp, Email, Phone, SMS</li>
                <li><strong>Automation:</strong> Browser, VSCode, Workflows, File-Transfer</li>
                <li><strong>Business:</strong> CRM, Shop, Calendar, Finance, Forms</li>
                <li><strong>Marketing:</strong> Social Media, Influencer, Homepage</li>
            </ul>
        </article>

        <article>
            <h3>🏢 Für wen ist das System?</h3>
            <dl>
                <dt>Startups & Scale-Ups</dt>
                <dd>Rapid Prototyping mit Plan "Basic" (4 Agenten) → skalieren zu "Ultimum" (alle 21 Agenten)</dd>

                <dt>Enterprise & Corporate</dt>
                <dd>Vollständige Kontrolle über Kommunikationskanäle, DSGVO-konforme Datenverarbeitung, On-Premise-Deployment möglich</dd>

                <dt>Agenturen & Consultants</dt>
                <dd>Multi-Client-Fähigkeit, White-Label-Option, Workflow-Templates für wiederkehrende Aufgaben</dd>

                <dt>E-Commerce & Retail</dt>
                <dd>Shop-Integration (opena16), CRM (opena14), Influencer-Marketing (opena19), Social Media (opena18)</dd>
            </dl>
        </article>

        <article>
            <h3>🔒 Sicherheit & Governance</h3>
            <p><strong>Enterprise-Grade Security by Design:</strong></p>
            <ul>
                <li>✅ Plan-basierte Access Control (Control-Plane via opena20)</li>
                <li>✅ Port-Isolation (jeder Agent auf eigenem Port)</li>
                <li>✅ API-Gateway via opena1 (zentrale Authentifizierung)</li>
                <li>✅ Vollständiges Audit-Log via opena2</li>
                <li>✅ DSGVO-konforme Datenspeicherung</li>
                <li>✅ On-Premise Deployment möglich</li>
                <li>✅ Role-Based Access Control (RBAC) pro Agent</li>
            </ul>
        </article>
    </section>

    <section id="agents">
        <h2>Alle Agenten ({len(agents)})</h2>
        <p>Jeder Agent ist spezialisiert, dokumentiert und über REST-API zugänglich:</p>

        <div data-component="agent-showcase">
"""

        for agent in agents:
            html += f"""
            <article data-agent="{agent['id']}">
                <h3>{agent['name']}</h3>
                <p><strong>{agent['id']}</strong> | Port {agent['port']} | Role: {agent['role']}</p>
                <p>{agent['description']}</p>
            </article>
"""

        html += """
        </div>
    </section>

    <section id="plans">
        <h2>Pläne – Von Startup bis Enterprise</h2>
        <p><strong>Wählen Sie den Plan, der zu Ihrer Unternehmensgröße passt.</strong> Alle Pläne nutzen dieselbe Infrastruktur – nur die Anzahl freigeschalteter Agenten unterscheidet sich.</p>

        <div data-component="plan-grid">
"""

        for plan_name, plan_data in plans.items():
            if plan_name in ["core", "system"]:
                continue

            agent_count = len(plan_data.get("agents", []))
            html += f"""
            <article data-plan="{plan_name}">
                <h3>{plan_data.get('name', plan_name.title())}</h3>
                <p>{plan_data.get('description', 'Enterprise Plan')}</p>
                <p><strong>{agent_count} Agenten freigeschaltet</strong></p>
                <a href="/{plan_name}" data-action="view-plan">Details ansehen</a>
            </article>
"""

        html += """
        </div>
    </section>

    <section id="security">
        <h2>Technische Architektur</h2>
        <article>
            <h3>Control-Plane (opena20)</h3>
            <p>Die Control-Plane ist das Herzstück des Systems:</p>
            <ul>
                <li><strong>HTML-Generator:</strong> Alle Dashboard-Seiten werden dynamisch aus Daten generiert</li>
                <li><strong>Entitlement-Engine:</strong> Plan-basierte Sichtbarkeit (Basic = 4 Agenten, Ultimum = alle 21)</li>
                <li><strong>Gate-System:</strong> Locked Agenten zeigen 🔒 + Upgrade-CTA</li>
                <li><strong>API-Router:</strong> Alle Agent-Calls laufen über opena1 (keine Direktcalls)</li>
            </ul>
        </article>

        <article>
            <h3>Discovery & Inventory</h3>
            <p>System-Baseline definiert alle Agenten. Discovery-Script (Aufgabe 2) scannt Filesystem und generiert <code>agent_inventory.json</code> – diese Datei ist die Single Source of Truth für alle HTML-Seiten.</p>
        </article>

        <article>
            <h3>Deployment</h3>
            <ul>
                <li><strong>Cloud:</strong> Managed auf hyperdashboard-one.de</li>
                <li><strong>On-Premise:</strong> Docker Compose + Kubernetes Charts verfügbar</li>
                <li><strong>Hybrid:</strong> Cloud Control-Plane + On-Premise Agenten</li>
            </ul>
        </article>
    </section>
</main>

<footer>
    <nav>
        <a href="/legal/privacy">Datenschutz</a>
        <a href="/legal/terms">AGB</a>
        <a href="/legal/imprint">Impressum</a>
        <a href="/docs" data-action="docs">Dokumentation</a>
        <a href="/api/status/all" data-api="status">API Status</a>
    </nav>
    <p>© 2025 ELION HyperDashboard | <a href="/abrechnung">Upgrade</a></p>
</footer>

</body>
</html>
"""

        self._save_page(Config.PUBLIC_DIR / "index.html", html)

    def _compile_plan_pages(self):
        """Compile individual plan pages"""
        plans = self.data.get_plans()

        plan_descriptions = {
            "basic": {
                "who": "Startups, Einzelunternehmer, Freelancer",
                "why": "Schneller Einstieg mit essentiellen Kommunikations-Agenten",
                "limits": "4 Agenten (opena1, opena2, opena3, opena4)",
                "unlocks": "Koordination + Archiv + Telegram + WhatsApp",
            },
            "pro": {
                "who": "Kleine bis mittlere Teams (5-20 Mitarbeiter)",
                "why": "Erweiterte Kommunikation + erste Automation-Tools",
                "limits": "10 Agenten (Basic + Email, Phone, Browser, VSCode, Workflows, File-Transfer)",
                "unlocks": "Vollständige Kommunikations-Suite + Basis-Automation",
            },
            "premium": {
                "who": "Mittelständische Unternehmen, E-Commerce, Agenturen",
                "why": "Business-Tools + Marketing + CRM",
                "limits": "16 Agenten (Pro + CRM, Shop, Calendar, Finance, Forms, Social Media)",
                "unlocks": "Business Intelligence + Marketing Automation",
            },
            "ultimum": {
                "who": "Enterprise, Corporates, Full-Stack-Agenturen",
                "why": "Vollständige Kontrolle über alle 21 Agenten",
                "limits": "Alle 21 Agenten freigeschaltet",
                "unlocks": "Komplettes System + Influencer-Agent + Homepage-Agent + SMS-Agent + Transfer-Agent + Workflow-Designer",
            },
        }

        for plan_name, plan_data in plans.items():
            if plan_name in ["core", "system"]:
                continue

            desc = plan_descriptions.get(plan_name, {})
            agent_ids = plan_data.get("agents", [])
            agents = [a for a in self.data.get_agents() if a["id"] in agent_ids]

            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plan: {plan_data.get('name', plan_name.title())} – ELION HyperDashboard</title>
    <meta name="eden:page" content="plan">
    <meta name="eden:plan" content="{plan_name}">
    <meta name="eden:generated" content="{datetime.now().isoformat()}">
</head>

<body data-page="plan" data-plan="{plan_name}">

<header>
    <h1>Plan: {plan_data.get('name', plan_name.title())}</h1>
    <p><a href="/">← Zurück zur Übersicht</a></p>
</header>

<main>
    <section>
        <h2>Übersicht</h2>
        <article>
            <p><strong>{plan_data.get('description', '')}</strong></p>
            <dl>
                <dt>Für wen?</dt>
                <dd>{desc.get('who', 'N/A')}</dd>

                <dt>Warum dieser Plan?</dt>
                <dd>{desc.get('why', 'N/A')}</dd>

                <dt>Limits</dt>
                <dd>{desc.get('limits', 'N/A')}</dd>

                <dt>Was wird freigeschaltet?</dt>
                <dd>{desc.get('unlocks', 'N/A')}</dd>
            </dl>
        </article>
    </section>

    <section>
        <h2>Freigeschaltete Agenten ({len(agents)})</h2>
        <div data-component="agent-list">
"""

            for agent in agents:
                html += f"""
            <article data-agent="{agent['id']}">
                <h3>{agent['name']}</h3>
                <p><strong>{agent['id']}</strong> | Port {agent['port']}</p>
                <p>{agent['description']}</p>
            </article>
"""

            html += """
        </div>
    </section>

    <section>
        <h2>Jetzt starten</h2>
        <nav>
            <a href="/login" data-action="login">Einloggen</a>
            <a href="/register" data-action="register">Registrieren</a>
        </nav>
    </section>
</main>

<footer>
    <p><a href="/">Zurück zur Startseite</a></p>
</footer>

</body>
</html>
"""

            self._save_page(Config.PUBLIC_DIR / f"{plan_name}.html", html)

    def _compile_legal_pages(self):
        """Compile legal pages"""
        legal_pages = {
            "privacy": {
                "title": "Datenschutzerklärung",
                "content": """
                    <h2>Datenschutzerklärung</h2>
                    <p><strong>ELION HyperDashboard ist DSGVO-konform.</strong></p>
                    <article>
                        <h3>1. Datenerfassung</h3>
                        <p>Wir erfassen nur technisch notwendige Daten: Login-Credentials, Agent-Nutzung, API-Logs.</p>
                    </article>
                    <article>
                        <h3>2. Datenspeicherung</h3>
                        <p>Alle Daten werden verschlüsselt gespeichert. On-Premise-Kunden haben vollständige Kontrolle.</p>
                    </article>
                    <article>
                        <h3>3. Datenverarbeitung</h3>
                        <p>Agenten verarbeiten Daten nur im Kontext Ihrer Anfragen. Keine Weitergabe an Dritte.</p>
                    </article>
                """,
            },
            "terms": {
                "title": "Allgemeine Geschäftsbedingungen",
                "content": """
                    <h2>AGB</h2>
                    <article>
                        <h3>1. Geltungsbereich</h3>
                        <p>Diese AGB gelten für alle Nutzer von ELION HyperDashboard.</p>
                    </article>
                    <article>
                        <h3>2. Leistungsumfang</h3>
                        <p>Der Leistungsumfang richtet sich nach dem gewählten Plan (Basic, Pro, Premium, Ultimum).</p>
                    </article>
                    <article>
                        <h3>3. Zahlungsbedingungen</h3>
                        <p>Monatliche oder jährliche Abrechnung. Upgrade/Downgrade jederzeit möglich.</p>
                    </article>
                """,
            },
            "imprint": {
                "title": "Impressum",
                "content": """
                    <h2>Impressum</h2>
                    <article>
                        <p><strong>ELION HyperDashboard</strong></p>
                        <p>Musterstraße 123</p>
                        <p>12345 Musterstadt</p>
                        <p>Deutschland</p>
                        <p>E-Mail: legal@hyperdashboard-one.de</p>
                    </article>
                """,
            },
        }

        for page_name, page_data in legal_pages.items():
            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data['title']} – ELION HyperDashboard</title>
    <meta name="eden:page" content="legal">
    <meta name="eden:legal" content="{page_name}">
</head>

<body data-page="legal" data-legal="{page_name}">

<header>
    <h1>{page_data['title']}</h1>
    <p><a href="/">← Zurück zur Startseite</a></p>
</header>

<main>
{page_data['content']}
</main>

<footer>
    <nav>
        <a href="/legal/privacy">Datenschutz</a>
        <a href="/legal/terms">AGB</a>
        <a href="/legal/imprint">Impressum</a>
    </nav>
    <p><a href="/">Zurück zur Startseite</a></p>
</footer>

</body>
</html>
"""

            self._save_page(Config.LEGAL_DIR / f"{page_name}.html", html)

    # ========================================================================
    # APP PAGES
    # ========================================================================

    def _compile_dashboard_pages(self):
        """Compile dashboard pages (one per plan)"""
        plans = ["basic", "pro", "premium", "ultimum"]

        for plan in plans:
            plan_data = self.data.get_plans().get(plan, {})
            agent_ids = plan_data.get("agents", [])
            all_agents = self.data.get_agents()

            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard – {plan.upper()}</title>
    <meta name="eden:page" content="dashboard">
    <meta name="eden:plan" content="{plan}">
    <meta name="eden:generated" content="{datetime.now().isoformat()}">
</head>

<body data-page="dashboard" data-plan="{plan}">

<header>
    <h1>🤖 Dashboard</h1>
    <p>Plan: <strong>{plan.upper()}</strong></p>
    <nav>
        <a href="/app/dashboard/basic.html">Basic</a>
        <a href="/app/dashboard/pro.html">Pro</a>
        <a href="/app/dashboard/premium.html">Premium</a>
        <a href="/app/dashboard/ultimum.html">Ultimum</a>
    </nav>
</header>

<main>
    <section aria-label="Agenten">
        <h2>Ihre Agenten</h2>
        <div data-component="agent-grid">
"""

            for agent in all_agents:
                if agent["visibility"] == "system":
                    continue

                is_unlocked = agent["id"] in agent_ids
                state = "active" if is_unlocked else "locked"
                lock_emoji = "" if is_unlocked else "🔒 "

                html += f"""
            <article data-agent="{agent['id']}" data-state="{state}">
                <h3>{lock_emoji}{agent['name']}</h3>
                <p><strong>{agent['id']}</strong> | Port {agent['port']}</p>
                <p>{agent['description']}</p>
"""

                if is_unlocked:
                    html += f"""
                <a href="/app/agents/{agent['id']}.html" data-action="open">Öffnen</a>
"""
                else:
                    html += f"""
                <p><em>🔒 Nicht im {plan.upper()}-Plan enthalten</em></p>
                <a href="/abrechnung" data-action="upgrade">Upgrade</a>
"""

                html += "            </article>\n"

            html += """
        </div>
    </section>
</main>

<footer>
    <p><a href="/">Zur Website</a></p>
</footer>

</body>
</html>
"""

            dashboard_dir = Config.APP_DIR / "dashboard"
            dashboard_dir.mkdir(exist_ok=True)
            self._save_page(dashboard_dir / f"{plan}.html", html)

    def _compile_agent_pages(self):
        """Compile individual agent pages"""
        agents = self.data.get_agents()
        agents_dir = Config.APP_DIR / "agents"
        agents_dir.mkdir(exist_ok=True)

        for agent in agents:
            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{agent['name']} – Agent Details</title>
    <meta name="eden:page" content="agent">
    <meta name="eden:agent" content="{agent['id']}">
</head>

<body data-page="agent" data-agent="{agent['id']}">

<header>
    <h1>{agent['name']}</h1>
    <p><a href="/app/dashboard/basic.html">← Zurück zum Dashboard</a></p>
</header>

<main>
    <section>
        <h2>Details</h2>
        <dl>
            <dt>Agent ID:</dt>
            <dd>{agent['id']}</dd>

            <dt>Port:</dt>
            <dd>{agent['port']}</dd>

            <dt>Role:</dt>
            <dd>{agent['role']}</dd>

            <dt>Visibility:</dt>
            <dd>{agent['visibility']}</dd>

            <dt>Description:</dt>
            <dd>{agent['description']}</dd>
        </dl>
    </section>

    <section>
        <h2>API Endpoints ({len(agent['endpoints'])})</h2>
"""

            if agent["endpoints"]:
                html += "        <ul>\n"
                for endpoint in agent["endpoints"]:
                    html += f"            <li><code>{endpoint}</code></li>\n"
                html += "        </ul>\n"
            else:
                html += "        <p><em>Keine Endpoints erkannt</em></p>\n"

            html += f"""
    </section>

    <section>
        <h2>Aktionen</h2>
        <nav>
            <a href="/api/agents/{agent['id']}/health" data-api="health">Health Check</a>
            <a href="http://127.0.0.1:{agent['port']}/health" target="_blank">Direkter Health Check</a>
        </nav>
    </section>
</main>

<footer>
    <p><a href="/app/dashboard/basic.html">Zurück zum Dashboard</a></p>
</footer>

</body>
</html>
"""

            self._save_page(agents_dir / f"{agent['id']}.html", html)

    def _compile_error_pages(self):
        """Compile error pages"""
        errors_dir = Config.APP_DIR / "errors"
        errors_dir.mkdir(exist_ok=True)

        error_pages = {
            "403": {
                "title": "403 – Zugriff verweigert",
                "content": "<p>Sie haben keinen Zugriff auf diese Ressource.</p><p>Möglicherweise ist dieser Agent in Ihrem Plan nicht freigeschaltet.</p>",
            },
            "404": {"title": "404 – Nicht gefunden", "content": "<p>Die angeforderte Seite existiert nicht.</p>"},
            "500": {
                "title": "500 – Serverfehler",
                "content": "<p>Ein interner Serverfehler ist aufgetreten.</p><p>Bitte versuchen Sie es später erneut.</p>",
            },
        }

        for code, data in error_pages.items():
            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{data['title']}</title>
    <meta name="eden:page" content="error">
    <meta name="eden:error" content="{code}">
</head>

<body data-page="error" data-error="{code}">

<header>
    <h1>{data['title']}</h1>
</header>

<main>
{data['content']}
    <nav>
        <a href="/app/dashboard/basic.html">Zum Dashboard</a>
        <a href="/">Zur Startseite</a>
    </nav>
</main>

</body>
</html>
"""

            self._save_page(errors_dir / f"{code}.html", html)

    # ========================================================================
    # AUTH PAGES
    # ========================================================================

    def _compile_auth_pages(self):
        """Compile authentication pages"""

        auth_pages = {
            "login": {
                "title": "Login",
                "content": """
                    <form data-action="login" data-api="/api/auth/login">
                        <label for="email">E-Mail:</label>
                        <input type="email" id="email" name="email" required>

                        <label for="password">Passwort:</label>
                        <input type="password" id="password" name="password" required>

                        <button type="submit">Einloggen</button>
                    </form>
                    <nav>
                        <a href="/auth/register.html">Noch kein Konto? Registrieren</a>
                        <a href="/auth/forgot-password.html">Passwort vergessen?</a>
                    </nav>
                """,
            },
            "register": {
                "title": "Registrierung",
                "content": """
                    <form data-action="register" data-api="/api/auth/register">
                        <label for="email">E-Mail:</label>
                        <input type="email" id="email" name="email" required>

                        <label for="password">Passwort:</label>
                        <input type="password" id="password" name="password" required>

                        <label for="plan">Plan auswählen:</label>
                        <select id="plan" name="plan" required>
                            <option value="basic">Basic</option>
                            <option value="pro">Pro</option>
                            <option value="premium">Premium</option>
                            <option value="ultimum">Ultimum</option>
                        </select>

                        <button type="submit">Registrieren</button>
                    </form>
                    <nav>
                        <a href="/auth/login.html">Bereits registriert? Login</a>
                    </nav>
                """,
            },
            "forgot-password": {
                "title": "Passwort vergessen",
                "content": """
                    <form data-action="reset-password" data-api="/api/auth/reset-password">
                        <label for="email">E-Mail:</label>
                        <input type="email" id="email" name="email" required>

                        <button type="submit">Passwort zurücksetzen</button>
                    </form>
                    <nav>
                        <a href="/auth/login.html">Zurück zum Login</a>
                    </nav>
                """,
            },
        }

        for page_name, page_data in auth_pages.items():
            html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_data['title']} – ELION HyperDashboard</title>
    <meta name="eden:page" content="auth">
    <meta name="eden:auth" content="{page_name}">
</head>

<body data-page="auth" data-auth="{page_name}">

<header>
    <h1>{page_data['title']}</h1>
    <p><a href="/">← Zurück zur Startseite</a></p>
</header>

<main>
{page_data['content']}
</main>

<footer>
    <p><a href="/">Zur Startseite</a></p>
</footer>

</body>
</html>
"""

            self._save_page(Config.AUTH_DIR / f"{page_name}.html", html)


# ============================================================================
# MAIN
# ============================================================================


def main():
    """Main entry point"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║              opena20 HTML Compiler                               ║")
    print("║          Semantic HTML5 | Zero CSS | Zero JS                     ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    try:
        data_loader = DataLoader()
        compiler = HTMLCompiler(data_loader)
        compiler.compile_all()

        print("\n✅ HTML compilation successful!")
        print(f"📁 Output directory: {Config.OUTPUT_DIR}")
        print(f"📋 Manifest: {Config.ARTIFACTS_DIR / 'html_manifest.json'}")

    except Exception as e:
        print(f"\n❌ Compilation failed: {e}")
        raise


if __name__ == "__main__":
    main()
