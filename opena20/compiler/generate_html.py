#!/usr/bin/env python3
"""
opena20 HTML Compiler - Generator
Generates semantic HTML for App + Public Website driven by entitlements.

Outputs:
- public/index.html, public/legal/*.html, plan pages (public/roles)
- app/dashboard.html
- app/agents/opena1.html ... opena21.html
- app/errors/403.html, 404.html, 500.html
- auth/login.html, auth/regist.html, auth/forgot-password.html
- artifacts/html_manifest.json (sha256 for each page)
"""

import hashlib
import json
from pathlib import Path


class HTMLCompiler:
    def __init__(self, root: Path):
        self.root = root
        self.entitlements = self._load_json(self.root / "build" / "entitlements.json")
        self.inventory = self._load_json(self.root / "artifacts" / "agent_inventory.json")
        self.public_dir = self.root / "public"
        self.app_dir = self.root / "app"
        self.auth_dir = self.root / "auth"
        self.public_dir.mkdir(parents=True, exist_ok=True)
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.auth_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _load_json(path: Path):
        if not path.exists():
            return {}
        with open(path) as f:
            return json.load(f)

    @staticmethod
    def _compute_sha256(content: str) -> str:
        h = hashlib.sha256()
        h.update(content.encode("utf-8"))
        return h.hexdigest()

    def _write(self, path: Path, content: str) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return self._compute_sha256(content)

    def _page_meta(self, title: str, page_type: str) -> str:
        return f'<meta name="eden:page" content="{page_type}">' + f"<title>{title}</title>"

    def _page_header(self, title: str) -> str:
        return f"<header><h1>{title}</h1></header>"

    def _nav(self, links: list[str]) -> str:
        nav_items = "".join([f'<li><a href="{l}">{l.strip('/').title()}</a></li>' for l in links])
        return f"<nav><ul>{nav_items}</ul></nav>"

    def _get_agent_by_id(self, agent_id: str):
        for aid, ad in self.inventory.get("agents", {}).items():
            if aid == agent_id:
                return {"id": aid, **ad}
        return None

    def _render_agent_card(self, agent: dict, clickable: bool) -> str:
        locked = not clickable
        endpts = agent.get("endpoints", [])
        ep_html = ""
        if endpts:
            ep_html = "<ul>" + "".join([f"<li><code>{e}</code></li>" for e in endpts]) + "</ul>"
        action_links = ""
        if clickable:
            action_links = f'<a href="/agents/{agent["id"]}" data-action="open-agent" data-api="GET:/agents/{agent["id"]}">Öffnen</a>'
            action_links += f' <a href="/api/v1/logs/{agent["id"]}" data-action="view-logs" data-api="GET:/api/v1/logs/{agent["id"]}">Logs</a>'
        else:
            action_links = "<span>🔒 Upgrade</span>"
        return f"""
        <article data-agent="{agent['id']}" data-state="{'active' if clickable else 'locked'}">
          <h3>{agent.get('name', agent['id'])}</h3>
          <p><strong>Port:</strong> {agent.get('port', '?')}</p>
          <p><strong>Role:</strong> {agent.get('role', '')}</p>
          <p>{agent.get('description', '')}</p>
          {ep_html}
          <p>{action_links}</p>
        </article>
        """

    def _public_landing(self) -> str:
        # 2x density landing text (high-level marketing content, but semantic HTML)
        sections = [
            ("EDEN & Governance", "Hierarchie, Sicherheit & Governance für das ELION-Ökosystem."),
            ("Agenten & Control-Plane", "21 spezialisierte Agenten, zentrale Koordination und sichere Gateways."),
            ("Zielgruppen", "Unternehmen, Entwickler, IT-Sicherheitsteams."),
        ]
        body = "".join([f"<section><h2>{title}</h2><p>{desc}</p></section>" for title, desc in sections])
        # Plans overview
        plans = self.entitlements.get("basic", {})  # minimal placeholder for density
        return f"""<!DOCTYPE html>
<html lang=\"de\">
<head>{self._page_meta("ELION Hyper-Dashboard","landing")}</head>
<body data-auth=\"guest\" data-page=\"landing\">
<header><h1>ELION HyperDashboard</h1></header>
<main>
  {body}
  <section aria-label=\"Plans\">
    <h2>Verfügbare Pläne</h2>
    <ul>
      <li><a href=\"/public/basic\" data-action=\"navigate\" data-api=\"GET:/public/basic\">Basic</a></li>
      <li><a href=\"/public/pro\" data-action=\"navigate\" data-api=\"GET:/public/pro\">Pro</a></li>
      <li><a href=\"/public/premium\" data-action=\"navigate\" data-api=\"GET:/public/premium\">Premium</a></li>
      <li><a href=\"/public/ultimum\" data-action=\"navigate\" data-api=\"GET:/public/ultimum\">Ultimum</a></li>
    </ul>
  </section>
</main>
<footer><p>© 2025 ELION HyperDashboard</p></footer>
</body>
</html>"""

    def generate(self):
        # 1) Public landing
        landing = self._public_landing()
        landing_path = self.public_dir / "index.html"
        landing_sha = self._write(landing_path, landing)

        # 2) Legal pages
        legal_pages = {
            "/legal/privacy.html": "<h2>Privacy</h2><p>Datenschutztext.</p>",
            "/legal/terms.html": "<h2>Terms</h2><p>Nutzungsbedingungen.</p>",
            "/legal/imprint.html": "<h2>Impressum</h2><p>Impressum.</p>",
        }
        legal_art = {}
        for path_rel, body in legal_pages.items():
            # Ensure we always write into public/ subdirectory even if path_rel starts with '/'
            rel = path_rel.lstrip("/")
            p = self.public_dir / rel
            html = f'<!DOCTYPE html>\n<html lang="de">\n<head>{self._page_meta(path_rel.strip('.html'), 'legal')}</head>\n<body>\n<header><h1>{path_rel.strip('/')}</h1></header>\n<main>{body}</main>\n</body>\n</html>'
            legal_sha = self._write(p, html)
            legal_art[str(p)] = legal_sha

        # 3) Plan pages
        plan_pages = ["basic", "pro", "premium", "ultimum"]
        plan_contents = {}
        for plan in plan_pages:
            page = self.public_dir / f"{plan}.html"
            title = plan.capitalize() + " Plan"
            html = f"""<!DOCTYPE html>\n<html lang=\"de\">\n<head>{self._page_meta(title, 'plan')}</head>\n<body data-plan=\"{plan}\">\n<header>\n  <h1>{title}</h1>\n</header>\n<main>\n  <section>\n    <h2>Was ist {plan.capitalize()}?</h2>\n    <p>Plan-Übersicht: Wer/Warum/Limitierungen/Unlocks</p>\n  </section>\n</main>\n<footer><p>© 2025 ELION HyperDashboard</p></footer>\n</body>\n</html>"""
            plan_contents[plan] = (page, html)
            self._write(page, html)

        # 4) Public App Pages
        # Dashboard
        dashboard_path = self.app_dir / "dashboard.html"
        dashboard_html = self._generate_dashboard_html()
        dashboard_sha = self._write(dashboard_path, dashboard_html)

        # Agent pages
        agent_pages = {}
        for aid, ad in self.inventory.get("agents", {}).items():
            page_path = self.app_dir / "agents" / f"{aid}.html"
            is_clickable = False
            if self.entitlements:
                # try to find in any plan (basic to ultimum)
                for plan in ["basic", "pro", "premium", "ultimum"]:
                    plan_agents = self.entitlements.get(plan, {}).get("agents", {})
                    if aid in plan_agents:
                        is_clickable = plan_agents[aid].get("clickable", False)
                        break
            html = self._generate_agent_html(ad, is_clickable)
            agent_pages[aid] = (page_path, html)
            self._write(page_path, html)

        # Errors
        for code in [403, 404, 500]:
            path = self.app_dir / "errors" / f"{code}.html"
            html = self._generate_error_html(code)
            self._write(path, html)

        # Auth pages
        self._write(self.auth_dir / "login.html", self._generate_login_html())
        self._write(self.auth_dir / "regist.html", self._generate_regist_html())
        self._write(self.auth_dir / "forgot-password.html", self._generate_forgot_html())

        # Manifest
        manifest = {"pages": []}
        for p, sha in [(landing_path, landing_sha)] + [
            (p, self._compute_sha256(p.read_text())) for p in self.public_dir.glob("**/*.html")
        ]:
            manifest["pages"].append({"path": str(p), "sha256": sha})
        manifest_path = self.root / "artifacts" / "html_manifest.json"
        self._write(manifest_path, json.dumps(manifest, indent=2))

        return {
            "landing_sha": landing_sha,
            "dashboard_sha": dashboard_sha,
            "public_pages": len(list(self.public_dir.glob("**/*.html"))),
        }

    def _generate_dashboard_html(self) -> str:
        agents = self.inventory.get("agents", {})
        # Build simple grid of all agents; clickable only if allowed by entitlements
        html_agents = []
        for aid, ad in sorted(agents.items()):
            clickable = False
            # Determine plan entitlements if available
            if self.entitlements:
                for plan in ["basic", "pro", "premium", "ultimum"]:
                    plan_agents = self.entitlements.get(plan, {}).get("agents", {})
                    if aid in plan_agents:
                        clickable = plan_agents[aid].get("clickable", False)
                        break
            html_agents.append((aid, ad, clickable))

        body = "".join(
            [
                f'<article data-agent="{aid}" data-state="{'active' if c else 'locked'}">'
                f"<h3>{ad.get('name',''+aid)}</h3>"
                f"<p><strong>Port:</strong> {ad.get('port','')}</p>"
                f"<p><strong>Role:</strong> {ad.get('role','')}</p>"
                f"<p>{ad.get('description','')}</p>"
                f"{('<span>🔒 Upgrade</span>') if not c else f'<a href=\'/agents/{aid}\' data-action=\'open-agent\' data-api=\'GET:/agents/{aid}\'>Open</a>'}"
                f"</article>"
                for aid, ad, c in html_agents
            ]
        )

        return f"""<!DOCTYPE html>
<html lang=\"de\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"eden:page\" content=\"dashboard\">
  <title>HyperDashboard – App</title>
</head>
<body data-page=\"dashboard\" data-auth=\"guest\">
  <header><h1>HyperDashboard – App</h1></header>
  <main>
    <section aria-label=\"Agentenübersicht\">
      {body}
    </section>
  </main>
  <footer><p>© 2025 ELION</p></footer>
</body>
</html>"""

    def _generate_agent_html(self, agent: dict, clickable: bool) -> str:
        aid = agent.get("id") or ""
        name = agent.get("name", aid)
        port = agent.get("port", "")
        role = agent.get("role", "")
        visibility = agent.get("visibility", "public")
        description = agent.get("description", "")
        endpoints = agent.get("endpoints", [])
        ep_list = "<ul>" + "".join([f"<li><code>{e}</code></li>" for e in endpoints]) + "</ul>" if endpoints else ""
        if clickable:
            action = f"<a href='/agents/{aid}' data-action='open-agent' data-api='GET:/agents/{aid}'>Öffnen</a>"
        else:
            action = "<span>🔒 Upgrade</span>"
        # Build the agent block
        return f"""<article data-agent=\"{aid}\" data-state=\"{'active' if clickable else 'locked'}\">"""
        # Close string safely
        return (
            f'<article data-agent="{aid}" data-state="{'active' if clickable else 'locked'}">'
            f"<h3>{name}</h3>"
            f"<p><strong>Port:</strong> {port}</p>"
            f"<p><strong>Role:</strong> {role}</p>"
            f"<p>{description}</p>"
            f"{ep_list}"
            f"<p>{action}</p>"
            f"</article>"
        )

    def _generate_error_html(self, code: int) -> str:
        text = {403: "Zugriff verweigert", 404: "Seite nicht gefunden", 500: "Interner Serverfehler"}.get(
            code, "Fehler"
        )
        return f"""<!DOCTYPE html><html lang=\"de\"><head><title>{code} {text}</title></head><body data-error=\"{code}\"><header><h1>{code} {text}</h1></header><main><p>Ein Fehler ist aufgetreten.</p></main></body></html>"""

    def _generate_login_html(self) -> str:
        return HTMLCompiler._static_auth("Login", "/api/v1/auth/login")

    def _generate_regist_html(self) -> str:
        return HTMLCompiler._static_auth("Registrierung", "/api/v1/auth/register")

    def _generate_forgot_html(self) -> str:
        return HTMLCompiler._static_auth("Passwort vergessen", "/api/v1/auth/forgot-password")

    @staticmethod
    def _static_auth(title: str, action: str) -> str:
        return f"""<!DOCTYPE html><html lang=\"de\"><head><title>{title}</title></head><body data-auth=\"auth\"><main><h1>{title}</h1><form data-action=\"auth.{title.lower().replace(' ','_')}\" data-api=\"POST:{action}\" method=\"post\" action=\"{action}\"><input name=\"email\" placeholder=\"Email\" required><input name=\"password\" placeholder=\"Passwort\" required><button type=\"submit\">Absenden</button></form></main></body></html>"""


def main():
    root = Path(__file__).resolve().parents[2]
    compiler = HTMLCompiler(root)
    compiler.generate()


if __name__ == "__main__":
    main()
