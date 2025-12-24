#!/usr/bin/env python3
"""
ELION Hyper-Dashboard – opena20 (Dashboard-Agent)
Port: 12349
Role: HTML-Generator & Control-Plane

Responsibilities:
1. HTML-Skeleton-Generator (alle Dashboard-Seiten)
2. Control-Plane (Sichtbarkeit, Gates, Entitlements)
3. Daten-Router (alle Calls über opena1)

Principles:
- KEINE manuellen HTML-Dateien
- ALLE HTML aus Daten generiert
- KEINE Direktcalls zu Agenten (nur über opena1)
- Plan-Gates strikt durchgesetzt
"""

import json
import os
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================

# Load .env file
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

PORT = int(os.getenv("OPENA20_PORT", "12349"))
OPENA1_URL = os.getenv("OPENA1_URL", "http://127.0.0.1:12344")
BEARER_TOKEN = os.getenv("DASHBOARD_ADMIN_TOKEN", "baf54565-9eb3-4349-bdec-bcaf93b16977")

# API Keys aus .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_OPENA1")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app = FastAPI(
    title="opena20 - Dashboard Agent", description="HTML-Generator & Control-Plane (with .env support)", version="1.0.1"
)


PORT = 12349
OPENA1_URL = "http://127.0.0.1:12344"  # Koordinator (Option-2-Flow)

app = FastAPI(title="opena20 - Dashboard Agent", description="HTML-Generator & Control-Plane", version="1.0.0")

# ============================================================================
# DATA LOADERS
# ============================================================================


class DataLoader:
    """Lädt alle relevanten Datenquellen"""

    def __init__(self):
        self.root = Path(__file__).parent
        self.inventory_path = self.root / "artifacts" / "agent_inventory.json"
        self.baseline_path = self.root / "system_baseline.yaml"
        self.entitlements_path = self.root / "config" / "plan_entitlements.json"

        self.inventory = None
        self.baseline = None
        self.entitlements = None

        self._load_all()

    def _load_all(self):
        """Lade alle Datenquellen"""
        if not self.inventory_path.exists():
            raise RuntimeError(f"❌ FATAL: {self.inventory_path} not found. Run agent_discovery.py first!")

        with open(self.inventory_path) as f:
            self.inventory = json.load(f)

        if self.baseline_path.exists():
            import yaml

            with open(self.baseline_path) as f:
                self.baseline = yaml.safe_load(f)

        if self.entitlements_path.exists():
            with open(self.entitlements_path) as f:
                self.entitlements = json.load(f)
        else:
            # Fallback: Generate from baseline
            self.entitlements = self._generate_default_entitlements()

    def _generate_default_entitlements(self) -> dict:
        """Generate default entitlements from baseline"""
        if not self.baseline:
            return {"plans": {}}

        plans = self.baseline.get("plans", {})
        entitlements = {"plans": {}}

        for plan_name, plan_data in plans.items():
            entitlements["plans"][plan_name] = {
                "name": plan_data.get("name", plan_name.title()),
                "description": plan_data.get("description", ""),
                "agents": plan_data.get("agents", []),
                "features": [],
            }

        return entitlements

    def get_agent_list(self) -> list[dict]:
        """Get complete agent list with metadata"""
        agents = []
        for agent_id, agent_data in self.inventory["agents"].items():
            agents.append(
                {
                    "id": agent_id,
                    "name": agent_data["name"],
                    "port": agent_data["port"],
                    "role": agent_data["role"],
                    "visibility": agent_data["visibility"],
                    "description": agent_data["description"],
                    "has_main": agent_data["has_main"],
                    "endpoints": agent_data.get("all_endpoints", []),
                }
            )
        return sorted(agents, key=lambda x: x["port"])

    def get_plan_entitlements(self, plan: str) -> list[str]:
        """Get agent IDs for a specific plan"""
        if not self.entitlements:
            return []

        plan_data = self.entitlements.get("plans", {}).get(plan, {})
        agents = plan_data.get("agents", [])

        # Include core and system agents in all plans
        core_agents = self.entitlements.get("plans", {}).get("core", {}).get("agents", [])
        system_agents = self.entitlements.get("plans", {}).get("system", {}).get("agents", [])

        return list(set(agents + core_agents + system_agents))

    def get_all_plans(self) -> dict[str, dict]:
        """Get all plan definitions"""
        return self.entitlements.get("plans", {})


# Global data loader
data_loader = DataLoader()


# ============================================================================
# HTML GENERATORS
# ============================================================================


class HTMLGenerator:
    """HTML-Skeleton-Generator (semantisches HTML5)"""

    @staticmethod
    def generate_dashboard(plan: str, agents: list[dict], clickable_agents: list[str]) -> str:
        """Generate dashboard HTML skeleton"""

        plan_title = plan.upper() if plan else "DASHBOARD"

        # Sort agents by visibility and port
        visible_agents = [a for a in agents if a["visibility"] != "system"]

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyperDashboard – {plan_title}</title>
    <meta name="eden:plan" content="{plan}">
    <meta name="eden:generated" content="{datetime.now().isoformat()}">
</head>

<body data-plan="{plan}">

<!-- HEADER -->
<header>
    <h1>🤖 ELION HyperDashboard</h1>
    <p>Plan: <strong>{plan_title}</strong></p>
    <nav>
        <a href="/dashboard/basic">Basic</a>
        <a href="/dashboard/pro">Pro</a>
        <a href="/dashboard/premium">Premium</a>
        <a href="/dashboard/ultimum">Ultimum</a>
    </nav>
</header>

<!-- MAIN CONTENT -->
<main>
    <section aria-label="Agentenübersicht">
        <h2>Agenten ({len(visible_agents)})</h2>

        <div data-component="agent-grid">
"""

        # Generate agent cards
        for agent in visible_agents:
            is_clickable = agent["id"] in clickable_agents
            state = "active" if is_clickable else "locked"
            lock_emoji = "" if is_clickable else "🔒 "

            # Extract first endpoint for preview
            endpoint_preview = ""
            if agent["endpoints"]:
                endpoint_preview = f"<code>{agent['endpoints'][0]}</code>"

            html += f"""
            <!-- Agent: {agent['id']} -->
            <article data-agent="{agent['id']}" data-state="{state}">
                <h3>{lock_emoji}{agent['name']}</h3>
                <p><strong>ID:</strong> {agent['id']}</p>
                <p><strong>Port:</strong> {agent['port']}</p>
                <p><strong>Role:</strong> {agent['role']}</p>
                <p>{agent['description']}</p>

"""

            if endpoint_preview:
                html += f"                <p><strong>Endpoint:</strong> {endpoint_preview}</p>\n"

            if is_clickable:
                html += f"""                <a href="/agents/{agent['id']}" data-action="open-agent">Öffnen</a>
                <a href="/agents/{agent['id']}/logs" data-action="view-logs">Logs</a>
"""
            else:
                html += f"""                <p><em>🔒 Nicht verfügbar im {plan_title}-Plan</em></p>
                <a href="/billing" data-action="upgrade">Upgrade</a>
"""

            html += "            </article>\n"

        html += (
            """
        </div>
    </section>

    <!-- SYSTEM INFO -->
    <section aria-label="System-Informationen">
        <h2>System</h2>
        <article>
            <p><strong>Baseline Hash:</strong> <code>"""
            + data_loader.inventory.get("baseline_hash", "N/A")[:16]
            + """...</code></p>
            <p><strong>Total Agents:</strong> """
            + str(data_loader.inventory.get("agent_count", 0))
            + """</p>
            <p><strong>Total Endpoints:</strong> """
            + str(data_loader.inventory.get("total_endpoints", 0))
            + """</p>
            <p><strong>Generated:</strong> """
            + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            + """</p>
        </article>
    </section>
</main>

<!-- FOOTER -->
<footer>
    <p>ELION Hyper-Dashboard v1.0 | Powered by opena20 (Port 12349)</p>
    <nav>
        <a href="/docs">Dokumentation</a>
        <a href="/api/status/all" data-api="status">API Status</a>
        <a href="https://hyperdashboard-one.de">Website</a>
    </nav>
</footer>

</body>
</html>
"""
        )

        return html

    @staticmethod
    def generate_agent_page(agent: dict, is_allowed: bool) -> str:
        """Generate individual agent page"""

        if not is_allowed:
            return HTMLGenerator.generate_403(agent["id"])

        html = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>{agent['name']} – opena20</title>
</head>

<body data-agent="{agent['id']}">

<header>
    <h1>{agent['name']}</h1>
    <p><a href="/dashboard">← Zurück zum Dashboard</a></p>
</header>

<main>
    <section aria-label="Agent-Details">
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

            <dt>Main File:</dt>
            <dd>{'✅ Yes' if agent.get('has_main') else '❌ No'}</dd>
        </dl>
    </section>

    <section aria-label="Endpoints">
        <h2>API Endpoints ({len(agent.get('endpoints', []))})</h2>
"""

        if agent.get("endpoints"):
            html += "        <ul>\n"
            for endpoint in agent["endpoints"]:
                html += f"            <li><code>{endpoint}</code></li>\n"
            html += "        </ul>\n"
        else:
            html += "        <p><em>Keine Endpoints erkannt</em></p>\n"

        html += f"""
    </section>

    <section aria-label="Aktionen">
        <h2>Aktionen</h2>
        <nav>
            <a href="/agents/{agent['id']}/logs" data-action="view-logs">Logs anzeigen</a>
            <a href="/api/agents/{agent['id']}/health" data-api="health" target="_blank">Health Check</a>
            <a href="http://127.0.0.1:{agent['port']}/health" target="_blank">Direkter Health Check</a>
        </nav>
    </section>
</main>

<footer>
    <p><a href="/dashboard">Zurück zum Dashboard</a></p>
</footer>

</body>
</html>
"""

        return html

    @staticmethod
    def generate_403(agent_id: str) -> str:
        """Generate 403 Forbidden page"""
        return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>403 – Zugriff verweigert</title>
</head>

<body>

<header>
    <h1>🔒 Zugriff verweigert</h1>
</header>

<main>
    <p>Sie haben keinen Zugriff auf <strong>{agent_id}</strong>.</p>
    <p>Dieser Agent ist in Ihrem aktuellen Plan nicht freigeschaltet.</p>

    <nav>
        <a href="/billing">Plan upgraden</a>
        <a href="/dashboard">Zurück zum Dashboard</a>
    </nav>
</main>

</body>
</html>
"""

    @staticmethod
    def generate_404() -> str:
        """Generate 404 Not Found page"""
        return """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>404 – Nicht gefunden</title>
</head>

<body>

<header>
    <h1>404 – Seite nicht gefunden</h1>
</header>

<main>
    <p>Die angeforderte Seite existiert nicht.</p>
    <nav>
        <a href="/dashboard">Zum Dashboard</a>
    </nav>
</main>

</body>
</html>
"""

    @staticmethod
    def generate_landing_page() -> str:
        """Generate public landing page (hyperdashboard-one.de)"""
        agents = data_loader.get_agent_list()
        plans = data_loader.get_all_plans()

        html = (
            """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ELION HyperDashboard – Multi-Agent-System</title>
    <meta name="description" content="21 spezialisierte Agenten für Kommunikation, Automation und Business Intelligence">
</head>

<body>

<header>
    <h1>🤖 ELION HyperDashboard</h1>
    <p>Das vollständige Multi-Agent-System für modernes Business</p>
    <nav>
        <a href="#features">Features</a>
        <a href="#agents">Agenten</a>
        <a href="#plans">Pläne</a>
        <a href="/login">Login</a>
    </nav>
</header>

<main>
    <section id="features">
        <h2>Was ist ELION HyperDashboard?</h2>
        <p>Ein vollständig integriertes Multi-Agent-System mit 21 spezialisierten Agenten:</p>
        <ul>
            <li>✅ Zentrale Koordination (opena1)</li>
            <li>✅ Vollständiges Archiv (opena2)</li>
            <li>✅ Kommunikation (Telegram, WhatsApp, Email, Phone)</li>
            <li>✅ Automation (Browser, VSCode, Workflows)</li>
            <li>✅ Business (CRM, Shop, Calendar, Finance)</li>
            <li>✅ Marketing (Social Media, Influencer, Homepage)</li>
        </ul>
    </section>

    <section id="agents">
        <h2>Alle Agenten ("""
            + str(len(agents))
            + """)</h2>
        <div data-component="agent-showcase">
"""
        )

        # Show all agents (public view)
        for agent in agents:
            if agent["visibility"] == "system":
                continue  # Skip system agents on public page

            html += f"""
            <article>
                <h3>{agent['name']}</h3>
                <p><strong>{agent['id']}</strong> | Port {agent['port']}</p>
                <p>{agent['description']}</p>
            </article>
"""

        html += """
        </div>
    </section>

    <section id="plans">
        <h2>Pläne</h2>
        <div data-component="plan-grid">
"""

        # Generate plan cards
        for plan_name, plan_data in plans.items():
            if plan_name in ["core", "system"]:
                continue  # Skip internal plans

            agent_count = len(plan_data.get("agents", []))

            html += f"""
            <article data-plan="{plan_name}">
                <h3>{plan_data.get('name', plan_name.title())}</h3>
                <p>{plan_data.get('description', '')}</p>
                <p><strong>{agent_count} Agenten</strong></p>
                <a href="/{plan_name}">Details</a>
            </article>
"""

        html += """
        </div>
    </section>
</main>

<footer>
    <p>© 2025 ELION HyperDashboard | <a href="/docs">Dokumentation</a> | <a href="/api/status/all">API Status</a></p>
    <a href="/abrechnung">Upgrade</a>
</footer>

</body>
</html>
"""

        return html


# ============================================================================
# CONTROL-PLANE LOGIC
# ============================================================================


class ControlPlane:
    """Control-Plane: Sichtbarkeit, Gates, Entitlements"""

    @staticmethod
    def is_agent_clickable(agent_id: str, plan: str) -> bool:
        """Check if agent is clickable for given plan"""
        clickable_agents = data_loader.get_plan_entitlements(plan)
        return agent_id in clickable_agents

    @staticmethod
    def get_clickable_agents(plan: str) -> list[str]:
        """Get all clickable agent IDs for a plan"""
        return data_loader.get_plan_entitlements(plan)

    @staticmethod
    def validate_access(agent_id: str, plan: str) -> bool:
        """Validate if user can access agent"""
        return ControlPlane.is_agent_clickable(agent_id, plan)


# ============================================================================
# FASTAPI ROUTES
# ============================================================================


@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "ok",
        "agent": "opena20",
        "port": PORT,
        "role": "dashboard_generator",
        "inventory_loaded": data_loader.inventory is not None,
        "baseline_loaded": data_loader.baseline is not None,
        "entitlements_loaded": data_loader.entitlements is not None,
    }


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Public landing page (hyperdashboard-one.de)"""
    return HTMLGenerator.generate_landing_page()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect():
    """Redirect to default dashboard (basic)"""
    return RedirectResponse(url="/dashboard/basic")


@app.get("/dashboard/{plan}", response_class=HTMLResponse)
async def dashboard(plan: str):
    """Generate dashboard for specific plan"""
    valid_plans = ["basic", "pro", "premium", "ultimum"]

    if plan not in valid_plans:
        raise HTTPException(status_code=404, detail=f"Plan '{plan}' not found")

    agents = data_loader.get_agent_list()
    clickable_agents = ControlPlane.get_clickable_agents(plan)

    html = HTMLGenerator.generate_dashboard(plan, agents, clickable_agents)
    return HTMLResponse(content=html)


@app.get("/agents/{agent_id}", response_class=HTMLResponse)
async def agent_page(agent_id: str, plan: str = "basic"):
    """Generate individual agent page"""
    agents = data_loader.get_agent_list()
    agent = next((a for a in agents if a["id"] == agent_id), None)

    if not agent:
        return HTMLResponse(content=HTMLGenerator.generate_404(), status_code=404)

    is_allowed = ControlPlane.validate_access(agent_id, plan)
    html = HTMLGenerator.generate_agent_page(agent, is_allowed)

    if not is_allowed:
        return HTMLResponse(content=html, status_code=403)

    return HTMLResponse(content=html)


@app.get("/api/status/all")
async def status_all():
    """Get status of all agents (via opena1)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OPENA1_URL}/routes")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cannot reach opena1: {e}")


@app.get("/api/status/{agent_id}")
async def status_single(agent_id: str):
    """Get status of single agent (via opena1)"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Forward to opena1
            response = await client.get(f"{OPENA1_URL}/routes")
            routes = response.json()

            agent_route = routes.get(agent_id)
            if not agent_route:
                raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

            return agent_route
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Cannot reach opena1: {e}")


@app.get("/api/agents/{agent_id}/health")
async def agent_health(agent_id: str):
    """Check health of specific agent (via opena1)"""
    try:
        agents = data_loader.get_agent_list()
        agent = next((a for a in agents if a["id"] == agent_id), None)

        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        # Direct health check
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"http://127.0.0.1:{agent['port']}/health")
            return response.json()

    except httpx.RequestError as e:
        return {"agent": agent_id, "status": "unreachable", "error": str(e)}


# ============================================================================
# STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print(
        f"""
╔══════════════════════════════════════════════════════════════════╗
║                    opena20 - Dashboard Agent                     ║
║                  HTML-Generator & Control-Plane                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Port:              12349                                        ║
║  Role:              dashboard_generator                          ║
║  Inventory:         {'✅ Loaded' if data_loader.inventory else '❌ Missing'}                              ║
║  Baseline:          {'✅ Loaded' if data_loader.baseline else '❌ Missing'}                              ║
║  Entitlements:      {'✅ Loaded' if data_loader.entitlements else '❌ Missing'}                              ║
╠══════════════════════════════════════════════════════════════════╣
║  Endpoints:                                                      ║
║  • GET  /                  - Landing page                        ║
║  • GET  /dashboard/{plan}  - Dashboard HTML                      ║
║  • GET  /agents/{id}       - Agent page                          ║
║  • GET  /api/status/all    - All agents status                   ║
╚══════════════════════════════════════════════════════════════════╝
    """
    )

    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
