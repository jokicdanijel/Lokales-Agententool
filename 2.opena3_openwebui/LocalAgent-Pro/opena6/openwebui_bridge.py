#!/usr/bin/env python3
"""
Browser Agent - OpenWebUI Tool Integration (v0.6+)
Unterstützt OpenWebUI 0.6.36+ mit Function Calling API

OpenWebUI v0.6+ hat eine spezifische API für Tools/Functions.
Dieses Skript registriert den Browser Agent ordnungsgemäß.
"""

import json
import logging
from datetime import datetime
from typing import Any

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [OPENWEBUI] %(levelname)s - %(message)s")
logger = logging.getLogger("openwebui_bridge")

# ============================================================================
# OPENWEBUI TOOL DEFINITION (v0.6+)
# ============================================================================

BROWSER_TOOL_MANIFEST = {
    "type": "function",
    "function": {
        "name": "browser_agent",
        "description": "Automatisierte Browser-Kontrolle für Web-Scraping, Datenextraktion und DOM-Manipulation mit dem lokalen Browser Agent",
        "parameters": {
            "type": "object",
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
                        "wait_for",
                    ],
                    "description": "Zu führende Browser-Aktion aus",
                },
                "url": {"type": "string", "description": "Zielseite URL (https://example.com)"},
                "selector": {"type": "string", "description": "CSS oder XPath Selektor für die Aktion"},
                "text": {"type": "string", "description": "Text zum eingeben (nur für 'type' Aktion)"},
                "wait_ms": {"type": "integer", "default": 500, "description": "Wartezeit nach Aktion in Millisekunden"},
                "return_format": {
                    "type": "string",
                    "enum": ["text", "html", "json", "raw"],
                    "default": "text",
                    "description": "Format der Rückgabe",
                },
            },
            "required": ["action", "url"],
        },
    },
}

# ============================================================================
# OPENWEBUI FUNCTION CALLING BRIDGE
# ============================================================================


class OpenWebUIBridge:
    """Bridge zwischen OpenWebUI und Browser Agent"""

    def __init__(self, openwebui_url: str = "http://localhost:3000", agent_url: str = "http://localhost:12350"):
        """
        Initialize OpenWebUI Bridge

        Args:
            openwebui_url: OpenWebUI URL
            agent_url: Browser Agent URL
        """
        self.openwebui_url = openwebui_url.rstrip("/")
        self.agent_url = agent_url.rstrip("/")
        self.bearer_token = "sk_opena6_browser_v3_production"
        self.session = requests.Session()

    def is_available(self) -> bool:
        """Check if services are available"""
        try:
            # Check OpenWebUI
            r1 = self.session.get(f"{self.openwebui_url}/api/config", timeout=5)
            # Check Browser Agent
            r2 = self.session.get(
                f"{self.agent_url}/health", headers={"Authorization": f"Bearer {self.bearer_token}"}, timeout=5
            )

            available = r1.status_code == 200 and r2.status_code == 200
            if available:
                logger.info("✅ Beide Services verfügbar")
            return available
        except Exception as e:
            logger.error(f"❌ Verfügbarkeitsprüfung fehlgeschlagen: {e}")
            return False

    async def handle_function_call(self, function_call: dict[str, Any]) -> dict[str, Any]:
        """
        Handle OpenWebUI function call

        Args:
            function_call: Function call from OpenWebUI

        Returns:
            Function result
        """
        try:
            # Extract function call details
            if "function" in function_call:
                func = function_call["function"]
                func_name = func.get("name")
                func_args = func.get("arguments", {})
            else:
                func_name = function_call.get("name")
                func_args = function_call.get("arguments", {})

            if func_name != "browser_agent":
                return {"status": "error", "message": f"Unknown function: {func_name}"}

            # Forward to Browser Agent
            response = self.session.post(
                f"{self.agent_url}/execute",
                json=func_args,
                headers={"Authorization": f"Bearer {self.bearer_token}", "Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                return {"status": "success", "data": result, "timestamp": datetime.now().isoformat()}
            else:
                return {
                    "status": "error",
                    "message": f"Browser Agent Error: {response.status_code}",
                    "details": response.text,
                }

        except Exception as e:
            logger.error(f"❌ Function Call Error: {e}")
            return {"status": "error", "message": str(e)}

    def setup_function_calling(self) -> bool:
        """
        Setup function calling in OpenWebUI

        For OpenWebUI 0.6+, function definitions are usually configured
        in the model settings or through API key authentication.
        This method provides configuration templates.
        """
        logger.info("📋 Function Calling Setup für OpenWebUI 0.6+")
        logger.info("")
        logger.info("1. Öffne: http://192.168.0.70:3000/admin")
        logger.info("2. Navigiere zu Settings → Models")
        logger.info("3. Wähle dein Modell und füge folgendes hinzu:")
        logger.info("")
        logger.info("Function Definition:")
        logger.info(json.dumps(BROWSER_TOOL_MANIFEST, indent=2, ensure_ascii=False))
        logger.info("")
        logger.info("Oder verwende den OpenWebUI Tool Editor für visuelle Konfiguration")
        return True

    def get_manifest(self) -> dict[str, Any]:
        """Get tool manifest for documentation"""
        return BROWSER_TOOL_MANIFEST


# ============================================================================
# INTEGRATION HELPER
# ============================================================================


class OpenWebUIIntegrationHelper:
    """Helper für OpenWebUI Integration"""

    @staticmethod
    def generate_prompt_template() -> str:
        """Generate prompt template for using browser agent"""
        return """
# Browser Agent Integration Prompt Template

Wenn der Benutzer mich auffordert:
- Websites zu öffnen
- Daten zu extrahieren
- Formulare auszufüllen
- Screenshots zu machen

Verwende ich die `browser_agent` Function:

```
Benutzer: "Öffne https://example.com und zeige mir die Hauptüberschrift"

Ich rufe auf:
{
  "function": "browser_agent",
  "arguments": {
    "action": "extract_text",
    "url": "https://example.com",
    "selector": "h1",
    "return_format": "text"
  }
}

Ergebnis: {
  "status": "success",
  "data": {
    "text": "Welcome to Example",
    "elements_found": 1
  }
}

Antwort an Benutzer: "Die Hauptüberschrift lautet: Welcome to Example"
```
"""

    @staticmethod
    def generate_model_system_prompt() -> str:
        """Generate system prompt for models using browser agent"""
        return """Du hast Zugriff auf einen lokalen Browser Agent namens 'browser_agent'.

Verwende ihn für:
- Web-Scraping und Datenextraktion
- Formular-Automatisierung
- DOM-Manipulation
- Screenshots und Seitenanalyse

Verfügbare Aktionen:
- open: Öffne eine Webseite
- click: Klicke auf ein Element
- type: Gib Text ein
- extract_text: Extrahiere Text
- extract_html: Extrahiere HTML
- query_selector: Analysiere DOM
- screenshot: Mache Screenshot
- scroll: Scrolle Seite
- wait_for: Warte auf Element

Immer zuerst 'open' aufrufen, bevor du andere Aktionen ausführst.
Verwende eindeutige und spezifische CSS-Selektoren.
Validiere URLs bevor du sie öffnest."""


# ============================================================================
# CLI
# ============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Browser Agent - OpenWebUI Integration (v0.6+)")
    parser.add_argument("--action", choices=["setup", "manifest", "prompt", "health"], default="setup")
    parser.add_argument("--openwebui-url", default="http://localhost:3000")
    parser.add_argument("--agent-url", default="http://localhost:12350")

    args = parser.parse_args()

    bridge = OpenWebUIBridge(openwebui_url=args.openwebui_url, agent_url=args.agent_url)

    logger.info("🔗 Browser Agent - OpenWebUI Bridge (v0.6+)")
    logger.info(f"   OpenWebUI: {args.openwebui_url}")
    logger.info(f"   Agent: {args.agent_url}")
    logger.info("")

    if args.action == "health":
        if bridge.is_available():
            logger.info("✅ Alle Services verfügbar")
            return 0
        else:
            logger.error("❌ Services nicht verfügbar")
            return 1

    elif args.action == "setup":
        bridge.setup_function_calling()
        return 0

    elif args.action == "manifest":
        manifest = bridge.get_manifest()
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0

    elif args.action == "prompt":
        logger.info(OpenWebUIIntegrationHelper.generate_model_system_prompt())
        return 0

    return 0


if __name__ == "__main__":
    exit(main())
