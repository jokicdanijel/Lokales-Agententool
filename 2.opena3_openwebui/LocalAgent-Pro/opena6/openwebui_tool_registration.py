#!/usr/bin/env python3
"""
Browser Agent - OpenWebUI Tool Registration
Registriert opena6_browser als Tool in OpenWebUI

Funktionen:
- Tool-Definition gemäß OpenWebUI-Schema erstellen
- Tool bei OpenWebUI-Instanz registrieren
- Health Check durchführen
- Tool-Aufrufe empfangen und delegieren
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [TOOL_REG] %(levelname)s - %(message)s'
)
logger = logging.getLogger('openwebui_registration')

# ============================================================================
# TOOL DEFINITION
# ============================================================================

BROWSER_AGENT_TOOL = {
    "id": "opena6_browser_tool",
    "name": "Browser Agent",
    "description": "Automatisierte Browser-Kontrolle für Web-Scraping, Datenextraktion und DOM-Manipulation",
    "valves": {
        "agent_url": "http://localhost:12350",
        "bearer_token": "sk_opena6_browser_v3_production",
        "timeout": 30,
        "enabled": True
    },
    "target": "opena6_browser_chat_handler",
    "input_schema": {
        "type": "object",
        "required": ["action", "url"],
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "open",
                    "click",
                    "type",
                    "extract_text",
                    "extract_html",
                    "query_selector",
                    "screenshot",
                    "scroll",
                    "wait_for"
                ],
                "description": "Browser-Aktion ausführen"
            },
            "url": {
                "type": "string",
                "description": "Zielseite URL"
            },
            "selector": {
                "type": "string",
                "description": "CSS oder XPath Selektor"
            },
            "text": {
                "type": "string",
                "description": "Text zum eingeben (für type-Aktion)"
            },
            "wait_ms": {
                "type": "integer",
                "default": 500,
                "description": "Wartezeit nach Aktion in Millisekunden"
            },
            "return_format": {
                "type": "string",
                "enum": ["text", "html", "json", "raw"],
                "default": "text",
                "description": "Format der Rückgabe"
            }
        }
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "data": {"type": "object"},
            "timestamp": {"type": "string"},
            "session_id": {"type": "string"}
        }
    }
}

# ============================================================================
# OPENWEBUI TOOL MANAGER
# ============================================================================

class OpenWebUIToolManager:
    """Verwaltet Tool-Registrierung bei OpenWebUI"""

    def __init__(self, openwebui_url: str = "http://localhost:8080"):
        """
        Initialize OpenWebUI Tool Manager

        Args:
            openwebui_url: OpenWebUI API URL (default: localhost:8080)
        """
        self.openwebui_url = openwebui_url.rstrip('/')
        self.tool_url = f"{self.openwebui_url}/api/v1/tools"
        self.health_url = f"{self.openwebui_url}/api/v1/auth"
        self.session = requests.Session()
        self.agent_url = "http://localhost:12350"
        self.bearer_token = "sk_opena6_browser_v3_production"

    def is_openwebui_available(self) -> bool:
        """Check if OpenWebUI is available"""
        try:
            response = self.session.get(self.health_url, timeout=5)
            logger.info(f"✅ OpenWebUI verfügbar: {self.openwebui_url}")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"⚠️  OpenWebUI nicht erreichbar: {e}")
            return False

    def is_agent_available(self) -> bool:
        """Check if Browser Agent is available"""
        try:
            response = self.session.get(
                f"{self.agent_url}/health",
                headers={"Authorization": f"Bearer {self.bearer_token}"},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"✅ Browser Agent verfügbar: {self.agent_url}")
                return True
            return False
        except Exception as e:
            logger.warning(f"⚠️  Browser Agent nicht erreichbar: {e}")
            return False

    def register_tool(self) -> bool:
        """Register browser tool with OpenWebUI"""
        if not self.is_openwebui_available():
            logger.error("❌ OpenWebUI nicht verfügbar - Registrierung abgebrochen")
            return False

        if not self.is_agent_available():
            logger.error("❌ Browser Agent nicht verfügbar - Registrierung abgebrochen")
            return False

        try:
            payload = BROWSER_AGENT_TOOL.copy()
            payload["valves"]["agent_url"] = self.agent_url
            payload["valves"]["bearer_token"] = self.bearer_token

            response = self.session.post(
                self.tool_url,
                json=payload,
                timeout=10
            )

            if response.status_code in [200, 201]:
                logger.info(f"✅ Tool erfolgreich registriert: {BROWSER_AGENT_TOOL['name']}")
                return True
            else:
                logger.error(f"❌ Registrierung fehlgeschlagen: {response.status_code}")
                logger.debug(f"Response: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Fehler bei Tool-Registrierung: {e}")
            return False

    def unregister_tool(self) -> bool:
        """Unregister browser tool from OpenWebUI"""
        try:
            tool_id = BROWSER_AGENT_TOOL["id"]
            response = self.session.delete(
                f"{self.tool_url}/{tool_id}",
                timeout=10
            )

            if response.status_code in [200, 204]:
                logger.info(f"✅ Tool deregistriert: {tool_id}")
                return True
            else:
                logger.warning(f"⚠️  Deregistrierung: {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Fehler bei Deregistrierung: {e}")
            return False

    def update_tool(self) -> bool:
        """Update browser tool in OpenWebUI"""
        if not self.is_openwebui_available():
            logger.error("❌ OpenWebUI nicht verfügbar")
            return False

        try:
            payload = BROWSER_AGENT_TOOL.copy()
            payload["valves"]["agent_url"] = self.agent_url
            tool_id = BROWSER_AGENT_TOOL["id"]

            response = self.session.put(
                f"{self.tool_url}/{tool_id}",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"✅ Tool aktualisiert: {BROWSER_AGENT_TOOL['name']}")
                return True
            else:
                logger.warning(f"⚠️  Update-Fehler: {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Fehler bei Update: {e}")
            return False

    def get_tool_status(self) -> Dict[str, Any]:
        """Get tool registration status"""
        return {
            "openwebui_available": self.is_openwebui_available(),
            "agent_available": self.is_agent_available(),
            "tool_id": BROWSER_AGENT_TOOL["id"],
            "tool_name": BROWSER_AGENT_TOOL["name"],
            "agent_url": self.agent_url,
            "openwebui_url": self.openwebui_url,
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# TOOL HANDLER FÜR OPENWEBUI
# ============================================================================

class BrowserAgentChatHandler:
    """Handles tool calls from OpenWebUI chat"""

    def __init__(self, agent_url: str = "http://localhost:12350"):
        self.agent_url = agent_url
        self.bearer_token = "sk_opena6_browser_v3_production"

    async def handle_tool_call(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle tool call from OpenWebUI chat

        Args:
            tool_input: Tool input from OpenWebUI

        Returns:
            Tool result
        """
        try:
            # Extract parameters
            action = tool_input.get("action")
            url = tool_input.get("url")
            selector = tool_input.get("selector", "")
            text = tool_input.get("text", "")
            wait_ms = tool_input.get("wait_ms", 500)
            return_format = tool_input.get("return_format", "text")

            # Prepare request for browser agent
            payload = {
                "action": action,
                "url": url,
                "selector": selector,
                "text": text,
                "wait_ms": wait_ms,
                "return_format": return_format
            }

            # Send to browser agent
            response = requests.post(
                f"{self.agent_url}/execute",
                json=payload,
                headers={"Authorization": f"Bearer {self.bearer_token}"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "data": result,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Browser Agent Error: {response.status_code}",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"❌ Tool Call Error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }

# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Browser Agent - OpenWebUI Tool Registration"
    )
    parser.add_argument(
        "--action",
        choices=["register", "unregister", "update", "status"],
        default="status",
        help="Aktion ausführen"
    )
    parser.add_argument(
        "--openwebui-url",
        default="http://localhost:8080",
        help="OpenWebUI API URL"
    )
    parser.add_argument(
        "--agent-url",
        default="http://localhost:12350",
        help="Browser Agent URL"
    )

    args = parser.parse_args()

    manager = OpenWebUIToolManager(openwebui_url=args.openwebui_url)
    manager.agent_url = args.agent_url

    logger.info(f"🚀 Browser Agent OpenWebUI Tool Manager")
    logger.info(f"   OpenWebUI: {args.openwebui_url}")
    logger.info(f"   Agent: {args.agent_url}")
    logger.info("")

    if args.action == "register":
        logger.info("📝 Registriere Tool bei OpenWebUI...")
        success = manager.register_tool()
        if success:
            logger.info("✅ Tool-Registrierung erfolgreich")
        else:
            logger.error("❌ Tool-Registrierung fehlgeschlagen")
        return 0 if success else 1

    elif args.action == "unregister":
        logger.info("🗑️  Deregistriere Tool aus OpenWebUI...")
        success = manager.unregister_tool()
        if success:
            logger.info("✅ Tool-Deregistrierung erfolgreich")
        else:
            logger.info("⚠️  Tool war nicht registriert")
        return 0 if success else 1

    elif args.action == "update":
        logger.info("🔄 Aktualisiere Tool in OpenWebUI...")
        success = manager.update_tool()
        if success:
            logger.info("✅ Tool-Update erfolgreich")
        else:
            logger.error("❌ Tool-Update fehlgeschlagen")
        return 0 if success else 1

    elif args.action == "status":
        status = manager.get_tool_status()
        logger.info("📊 Tool-Status:")
        for key, value in status.items():
            logger.info(f"   {key}: {value}")
        return 0

    return 1

if __name__ == "__main__":
    exit(main())
