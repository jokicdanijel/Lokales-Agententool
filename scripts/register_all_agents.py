#!/usr/bin/env python3
"""
Agent Registry Update Script
ELION Hyper-Dashboard 2.0

Registriert alle verfügbaren Agenten (opena1-opena21) im System

Autor: ELION Team
Version: 2.0
Datum: 29. November 2025
"""

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx

# Agent-Definitionen (aktualisierte vollständige Liste)
AGENTS_REGISTRY = {
    "opena1": {
        "name": "Koordinator Agent",
        "port": 12344,
        "endpoint": "http://127.0.0.1:12344",
        "capabilities": ["coordination", "routing", "command_dispatch"],
        "directory": "1.opena1&2_portier",
        "script": "main_opena1.py",
        "status": "core",
        "description": "Zentraler Koordinator für alle Agent-Kommunikation",
    },
    "opena2": {
        "name": "Archivator Agent",
        "port": 12345,
        "endpoint": "http://127.0.0.1:12345",
        "capabilities": ["archiving", "safepoints", "data_persistence"],
        "directory": "1.opena1&2_portier",
        "script": "main_opena2.py",
        "status": "core",
        "description": "Archivierungs- und Safepoint-Management",
    },
    "opena3": {
        "name": "OpenWebUI Terminal Agent",
        "port": 12347,
        "endpoint": "http://127.0.0.1:12347",
        "capabilities": ["openwebui", "chat", "conversation_management"],
        "directory": "2.opena3_openwebui",
        "script": "main_opena3.py",
        "status": "active",
        "description": "OpenWebUI Terminal Integration und Chat Management",
    },
    "opena4": {
        "name": "Telegram Mobile Agent",
        "port": 12348,
        "endpoint": "http://127.0.0.1:12348",
        "capabilities": ["telegram", "mobile_chat", "media_handling", "notifications"],
        "directory": "3.opena4_telegram",
        "script": "main_opena4.py",
        "status": "active",
        "description": "Telegram Bot Integration für Mobile Kommunikation",
    },
    "opena5": {
        "name": "VSCode Programming Agent",
        "port": 12351,
        "endpoint": "http://127.0.0.1:12351",
        "capabilities": ["vscode", "programming", "code_editing", "project_management"],
        "directory": "4.opena5_vscode",
        "script": "main_opena5.py",
        "status": "planned",
        "description": "VSCode Integration und Programmier-Unterstützung",
    },
    "opena6": {
        "name": "Browser Control Agent",
        "port": 12350,
        "endpoint": "http://127.0.0.1:12350",
        "capabilities": ["browser_automation", "web_scraping", "screenshot", "form_filling"],
        "directory": "5.opena6_browser",
        "script": "main_opena6.py",
        "status": "active",
        "description": "Browser Automation und Web Interaction",
    },
    "opena7": {
        "name": "Email Chatbot Agent",
        "port": 12352,
        "endpoint": "http://127.0.0.1:12352",
        "capabilities": ["email", "smtp", "imap", "auto_response"],
        "directory": "6.opena7_email",
        "script": "main_opena7.py",
        "status": "planned",
        "description": "Email-Verarbeitung und automatische Antworten",
    },
    "opena8": {
        "name": "WhatsApp Chatbot Agent",
        "port": 12353,
        "endpoint": "http://127.0.0.1:12353",
        "capabilities": ["whatsapp", "messaging", "media_sharing"],
        "directory": "7.opena8_whatsapp",
        "script": "main_opena8.py",
        "status": "planned",
        "description": "WhatsApp Integration und Messaging",
    },
    "opena9": {
        "name": "Phone Answer Agent",
        "port": 12354,
        "endpoint": "http://127.0.0.1:12354",
        "capabilities": ["phone", "voice", "call_handling"],
        "directory": "8.opena9_phone_answer",
        "script": "main_opena9.py",
        "status": "planned",
        "description": "Telefonanruf-Bearbeitung und Sprachantworten",
    },
    "opena10": {
        "name": "Phone Call Agent",
        "port": 12355,
        "endpoint": "http://127.0.0.1:12355",
        "capabilities": ["phone", "voice", "outbound_calls"],
        "directory": "9.opena10_phone_call",
        "script": "main_opena10.py",
        "status": "planned",
        "description": "Ausgehende Telefonanrufe und Sprachkommunikation",
    },
    "opena11": {
        "name": "Door Unlock Decode Agent",
        "port": 12356,
        "endpoint": "http://127.0.0.1:12356",
        "capabilities": ["security", "door_control", "access_management"],
        "directory": "10.opena11_door_unlock",
        "script": "main_opena11.py",
        "status": "planned",
        "description": "Türsteuerung und Zugangsmanagement",
    },
    "opena12": {
        "name": "Social Media Automation Agent",
        "port": 12357,
        "endpoint": "http://127.0.0.1:12357",
        "capabilities": ["social_media", "automation", "posting", "scheduling"],
        "directory": "11.opena12_social_automation",
        "script": "main_opena12.py",
        "status": "planned",
        "description": "Automatisierung von Social Media Aktivitäten",
    },
    "opena13": {
        "name": "Social Media Influencer Agent",
        "port": 12358,
        "endpoint": "http://127.0.0.1:12358",
        "capabilities": ["social_media", "content_creation", "influencer_management"],
        "directory": "12.opena13_social_influencer",
        "script": "main_opena13.py",
        "status": "planned",
        "description": "Social Media Influencer Management und Content Creation",
    },
    "opena14": {
        "name": "Calendar Agent",
        "port": 12359,
        "endpoint": "http://127.0.0.1:12359",
        "capabilities": ["calendar", "scheduling", "reminders", "meetings"],
        "directory": "13.opena14_calendar",
        "script": "main_opena14.py",
        "status": "planned",
        "description": "Kalender-Management und Terminplanung",
    },
    "opena16": {
        "name": "Shop Creator & Service Agent",
        "port": 12360,
        "endpoint": "http://127.0.0.1:12360",
        "capabilities": ["ecommerce", "shop_creation", "product_management"],
        "directory": "14.opena16_shop",
        "script": "main_opena16.py",
        "status": "planned",
        "description": "E-Commerce Shop Erstellung und Verwaltung",
    },
    "opena17": {
        "name": "Homepage Creator & Service Agent",
        "port": 12361,
        "endpoint": "http://127.0.0.1:12361",
        "capabilities": ["website_creation", "template_management", "seo_optimization", "responsive_design"],
        "directory": "15.opena17_homepage",
        "script": "main_opena17.py",
        "status": "active",
        "description": "Website Creation und Management Service",
    },
    "opena18": {
        "name": "Local Storage Agent",
        "port": 12362,
        "endpoint": "http://127.0.0.1:12362",
        "capabilities": ["file_storage", "data_indexing", "backup_management", "search"],
        "directory": "16.opena18_storage",
        "script": "main_opena18.py",
        "status": "active",
        "description": "Local File und Data Storage Management",
    },
    "opena19": {
        "name": "Trading Agent",
        "port": 12363,
        "endpoint": "http://127.0.0.1:12363",
        "capabilities": ["trading_simulation", "market_analysis", "portfolio_management", "risk_assessment"],
        "directory": "17.opena19_trading",
        "script": "main_opena19.py",
        "status": "active",
        "description": "Cryptocurrency & Stock Trading Automation (SIMULATION)",
    },
    "opena20": {
        "name": "Dashboard Agent",
        "port": 12349,
        "endpoint": "http://127.0.0.1:12349",
        "capabilities": ["dashboard", "ui", "api", "monitoring", "self_cleaning"],
        "directory": "19.opena20_dashboard_agent",
        "script": "main_dashboard_agent.py",
        "status": "core",
        "description": "Haupt-Dashboard mit UI, API und Self-Cleaning System",
    },
    "opena21": {
        "name": "Workflow Engine Agent",
        "port": 12364,
        "endpoint": "http://127.0.0.1:12364",
        "capabilities": ["workflow", "orchestration", "automation", "scheduling"],
        "directory": "20.opena21_workflow",
        "script": "main_opena21.py",
        "status": "planned",
        "description": "Workflow-Orchestrierung und Automation",
    },
    "opena22": {
        "name": "System Monitoring Agent",
        "port": 12366,
        "endpoint": "http://127.0.0.1:12366",
        "capabilities": ["system_monitoring", "health_checks", "alerts", "metrics", "real_time_tracking"],
        "directory": "21.opena22_monitoring",
        "script": "main.py",
        "status": "active",
        "description": "Enterprise-Level System Monitoring & Performance Analytics",
    },
}

BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"
DASHBOARD_URL = "http://127.0.0.1:12349"


async def register_all_agents():
    """Registriert alle Agenten beim Dashboard"""
    print("🤖 ELION Agent Registry Update")
    print("=" * 50)

    registered = 0
    failed = 0

    async with httpx.AsyncClient() as client:
        for agent_id, agent_info in AGENTS_REGISTRY.items():
            try:
                registration_data = {
                    "agent_id": agent_id,
                    "name": agent_info["name"],
                    "endpoint": agent_info["endpoint"],
                    "port": agent_info["port"],
                    "capabilities": agent_info["capabilities"],
                    "status": agent_info["status"],
                    "description": agent_info["description"],
                    "directory": agent_info["directory"],
                    "script": agent_info["script"],
                    "registered_at": datetime.now(UTC).isoformat(),
                }

                response = await client.post(
                    f"{DASHBOARD_URL}/api/agent/register",
                    json=registration_data,
                    headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    print(f"✅ {agent_id}: {agent_info['name']} (Port {agent_info['port']})")
                    registered += 1
                else:
                    print(f"❌ {agent_id}: Registration failed - HTTP {response.status_code}")
                    failed += 1

            except Exception as e:
                print(f"❌ {agent_id}: Registration error - {e}")
                failed += 1

    print("-" * 50)
    print("📊 Registration Summary:")
    print(f"   ✅ Registered: {registered}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Total: {len(AGENTS_REGISTRY)}")

    # Save registry to file
    registry_file = Path("agent_registry_full.json")
    with open(registry_file, "w") as f:
        json.dump(AGENTS_REGISTRY, f, indent=2, ensure_ascii=False)

    print(f"💾 Registry saved to: {registry_file}")

    return registered, failed


def print_agent_summary():
    """Druckt Übersicht aller Agenten"""
    print("\n🏛️ ELION Agent Architecture Overview")
    print("=" * 60)

    status_groups = {"core": [], "active": [], "planned": []}

    for agent_id, info in AGENTS_REGISTRY.items():
        status_groups[info["status"]].append((agent_id, info))

    for status, agents in status_groups.items():
        print(f"\n🔹 {status.upper()} Agents ({len(agents)}):")
        print("-" * 30)
        for agent_id, info in agents:
            print(f"  {agent_id}: {info['name']}")
            print(f"    Port: {info['port']} | Capabilities: {', '.join(info['capabilities'][:3])}...")

    print(f"\n📊 Total Agents: {len(AGENTS_REGISTRY)}")
    print("📡 Port Range: 12344-12399 (Backend Services)")
    print("🔗 Option-2 Flow: opena1 → opena2 → [Tool Agents]")


async def main():
    """Hauptfunktion"""
    print_agent_summary()
    print("\n" + "=" * 60)

    registered, failed = await register_all_agents()

    if failed == 0:
        print(f"\n🎉 All {registered} agents successfully registered!")
    else:
        print(f"\n⚠️ {registered} agents registered, {failed} failed")
        print("💡 Make sure the Dashboard (opena20) is running on port 12349")


if __name__ == "__main__":
    asyncio.run(main())
