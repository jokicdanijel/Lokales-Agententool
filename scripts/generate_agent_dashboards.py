#!/usr/bin/env python3
"""
PORTIER Agent Dashboard Generator
Generiert HTML-Dashboards für alle funktionierenden Agents basierend auf system_baseline.yaml
Nutzt opena15 (HTML Agent) falls verfügbar, sonst direktes Template-Rendering
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

import requests
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
BASELINE_PATH = PROJECT_ROOT / "system_baseline.yaml"

# Funktionierende Agents (aus ops.sh Ergebnis)
WORKING_AGENTS = [
    "opena6", "opena8", "opena10", "opena12", "opena14",
    "opena15", "opena16", "opena18", "opena19", "opena21"
]

# Capability Mapping (pro Agent)
CAPABILITY_MAP = {
    "opena3": ["chat_interface", "ai_models", "prompt_library", "conversation_history", "file_upload", "code_interpreter"],
    "opena4": ["bot_commands", "message_handler", "inline_keyboard", "media_sender", "webhook_support", "group_admin"],
    "opena5": ["code_editor", "file_explorer", "terminal", "git_integration", "extensions", "debugging"],
    "opena6": ["page_automation", "screenshot", "form_filling", "data_scraping", "navigation", "cookie_management"],
    "opena7": ["inbox_manager", "smtp_sender", "imap_receiver", "email_parser", "attachment_handler", "spam_filter"],
    "opena8": ["message_sender", "media_handler", "business_api", "webhook_receiver", "qr_auth", "group_messaging"],
    "opena9": ["incoming_handler", "outgoing_dialer", "voicemail_system", "ivr_menu", "call_recording", "stt_engine", "tts_engine", "caller_id", "call_routing", "conference", "sms_gateway", "ai_assistant"],
    "opena10": ["call_analytics", "kpi_dashboard", "call_logs", "recording_player", "report_generator", "alert_system"],
    "opena12": ["post_scheduler", "account_manager", "analytics", "content_library", "engagement_tracker", "hashtag_generator"],
    "opena13": ["campaign_manager", "collaboration_tools", "contract_tracking", "portfolio", "analytics", "payment_integration"],
    "opena14": ["event_list", "appointment_scheduler", "google_sync", "ics_export", "reminder_system", "timezone_support"],
    "opena16": ["product_catalog", "order_management", "payment_gateway", "inventory_tracker", "customer_portal", "shipping_integration"],
    "opena17": ["template_selector", "page_builder", "seo_optimizer", "publishing", "domain_manager", "analytics"],
    "opena18": ["contact_list", "pipeline_manager", "deal_tracker", "email_integration", "task_automation", "reporting"],
    "opena19": ["stock_tracker", "crypto_monitor", "portfolio_manager", "price_alerts", "trading_signals", "market_analysis"],
    "opena21": ["flow_builder", "trigger_manager", "execution_logs", "webhook_handler", "scheduler", "error_handler"],
}


def load_baseline() -> Dict:
    """Lädt system_baseline.yaml"""
    with open(BASELINE_PATH) as f:
        return yaml.safe_load(f)


def generate_html_template(agent: Dict, capabilities: List[str]) -> str:
    """Generiert HTML Dashboard für einen Agent"""
    capability_cards = "\n".join([
        f"""                <div class="capability-card">
                    <div class="icon">⚙️</div>
                    <div class="title">{cap.replace('_', ' ').upper()}</div>
                    <div class="desc">Verfügbar</div>
                </div>"""
        for cap in capabilities
    ])

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{agent['name']} Dashboard - PORTIER 3.0</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .header h1 {{ color: #667eea; font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #666; font-size: 1.2em; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }}
        .metric-card .label {{ color: #666; font-size: 0.9em; margin-bottom: 8px; }}
        .metric-card .value {{ color: #667eea; font-size: 2em; font-weight: bold; }}
        .capabilities {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px; }}
        .capabilities h2 {{ color: #333; margin-bottom: 20px; }}
        .capability-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; }}
        .capability-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; cursor: pointer; transition: transform 0.2s; }}
        .capability-card:hover {{ transform: translateY(-5px); }}
        .capability-card .icon {{ font-size: 2em; margin-bottom: 10px; }}
        .capability-card .title {{ font-size: 1.1em; font-weight: bold; margin-bottom: 5px; }}
        .capability-card .desc {{ font-size: 0.9em; opacity: 0.9; }}
        .api-console {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .api-console h2 {{ margin-bottom: 20px; }}
        .endpoint {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #667eea; }}
        .endpoint .method {{ display: inline-block; background: #667eea; color: white; padding: 5px 10px; border-radius: 5px; font-size: 0.9em; margin-right: 10px; }}
        .endpoint .path {{ font-family: monospace; color: #333; }}
        .status {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 0.9em; background: #4ade80; color: white; }}
        .refresh-btn {{ background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 1em; margin-top: 20px; }}
        .refresh-btn:hover {{ background: #5568d3; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {agent['name']}</h1>
            <p class="subtitle">{agent['role']} | Port {agent['port']} | <span class="status" id="status">ONLINE</span></p>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="label">Status</div>
                <div class="value" style="color: #4ade80;" id="status-value">✓ AKTIV</div>
            </div>
            <div class="metric-card">
                <div class="label">Port</div>
                <div class="value">{agent['port']}</div>
            </div>
            <div class="metric-card">
                <div class="label">Plan</div>
                <div class="value" style="font-size: 1.5em;">{agent['plan'].upper()}</div>
            </div>
            <div class="metric-card">
                <div class="label">Capabilities</div>
                <div class="value">{len(capabilities)}</div>
            </div>
        </div>

        <div class="capabilities">
            <h2>🚀 Capabilities</h2>
            <div class="capability-grid">
{capability_cards}
            </div>
        </div>

        <div class="api-console">
            <h2>🔌 API Endpoints</h2>
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">http://localhost:{agent['port']}/health</span>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">http://localhost:{agent['port']}/api/status</span>
            </div>
            <div class="endpoint">
                <span class="method">POST</span>
                <span class="path">http://localhost:{agent['port']}/api/execute</span>
            </div>
            <div class="endpoint">
                <span class="method">GET</span>
                <span class="path">http://localhost:{agent['port']}/api/capabilities</span>
            </div>
            <button class="refresh-btn" onclick="checkHealth()">🔄 Status aktualisieren</button>
        </div>
    </div>

    <script>
        async function checkHealth() {{
            try {{
                const response = await fetch('http://localhost:{agent['port']}/health');
                const data = await response.json();
                document.getElementById('status').style.background = '#4ade80';
                document.getElementById('status').textContent = 'ONLINE';
                document.getElementById('status-value').textContent = '✓ AKTIV';
                document.getElementById('status-value').style.color = '#4ade80';
            }} catch (error) {{
                document.getElementById('status').style.background = '#ef4444';
                document.getElementById('status').textContent = 'OFFLINE';
                document.getElementById('status-value').textContent = '✗ OFFLINE';
                document.getElementById('status-value').style.color = '#ef4444';
            }}
        }}

        // Auto-check on load
        window.addEventListener('load', checkHealth);
    </script>
</body>
</html>"""


def try_opena15_generation(agent: Dict, capabilities: List[str]) -> str:
    """Versucht HTML via opena15 (HTML Agent) zu generieren"""
    try:
        response = requests.post(
            "http://localhost:12361/api/generate",
            json={
                "agent_id": agent["id"],
                "agent_name": agent["name"],
                "port": agent["port"],
                "role": agent["role"],
                "plan": agent["plan"],
                "capabilities": capabilities,
            },
            timeout=5,
        )
        if response.ok:
            return response.text
    except Exception:
        pass
    return None


def save_dashboard(agent_id: str, html: str) -> bool:
    """Speichert HTML Dashboard in opena20 (zentrale Control-Plane)"""
    opena20_dir = PROJECT_ROOT / "19.opena20_dashboard_agent"
    if not opena20_dir.exists():
        print(f"⚠️  opena20 Ordner nicht gefunden: {opena20_dir}")
        return False

    # Priorität 1: static/generated (N8N-generierte Dashboards)
    dashboard_pages_dir = opena20_dir / "static" / "generated"
    dashboard_pages_dir.mkdir(parents=True, exist_ok=True)

    dashboard_path = dashboard_pages_dir / f"{agent_id}_dashboard.html"
    dashboard_path.write_text(html, encoding="utf-8")
    print(f"✅ [{agent_id}] Dashboard gespeichert: {dashboard_path}")
    print(f"   🌐 Verfügbar unter: http://localhost:12349/agent/{agent_id}")
    return True


def main():
    """Hauptprozess"""
    print("🚀 PORTIER Agent Dashboard Generator")
    print("=" * 60)

    # Baseline laden
    baseline = load_baseline()
    agents = {a["id"]: a for a in baseline["agents"]}

    # Stats
    generated = 0
    failed = 0

    # Nur funktionierende Agents
    for agent_id in WORKING_AGENTS:
        if agent_id not in agents:
            print(f"⚠️  [{agent_id}] nicht in Baseline gefunden")
            continue

        agent = agents[agent_id]
        capabilities = CAPABILITY_MAP.get(agent_id, agent.get("capabilities", []))

        print(f"\n🔹 [{agent_id}] {agent['name']} (Port {agent['port']})")

        # Versuche opena15 (falls läuft)
        html = try_opena15_generation(agent, capabilities)
        if html:
            print(f"   ✓ HTML via opena15 generiert")
        else:
            # Fallback: Direktes Template
            html = generate_html_template(agent, capabilities)
            print(f"   ✓ HTML via Template generiert")

        # Speichern
        if save_dashboard(agent_id, html):
            generated += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Ergebnis: {generated} erfolgreich, {failed} fehlgeschlagen")

    if generated > 0:
        print(f"\n🌐 Dashboards verfügbar via opena20:")
        print(f"   http://localhost:12349/  (Hauptdashboard)")
        for agent_id in WORKING_AGENTS:
            if agent_id in agents:
                print(f"   http://localhost:12349/agent/{agent_id}")

        print(f"\n🔄 opena20 neu starten:")
        print(f"   bash bin/ops.sh restart opena20")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
