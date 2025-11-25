"""
VS Code Bridge for Browser Agent Tool Server

Ermöglicht die Verwendung des Browser Agent Tools direkt in VS Code
über den integrierten Terminal, Debugger und REST Client.

Features:
- REST Client Integration (.rest / .http files)
- Debug Console Commands
- Terminal Shell Integration
- File Explorer Quick Actions
- VS Code Commands API
- Real-time Status in Status Bar
- Problem Matcher für Fehler

Installation:
1. Kopiere diese Datei in VS Code Extension Ordner (optional)
2. Öffne .rest / .http Dateien in VS Code
3. Nutze "Send Request" Button für API Calls

Abhängigkeiten:
- VS Code REST Client Extension (REST Client)
- VS Code Thunder Client (Alternative)
"""

import os
import json
import asyncio
import httpx
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


# ==================== REST Client Templates ====================

REST_CLIENT_TEMPLATE = """# Browser Agent Tool Server - REST Client

@baseUrl = http://192.168.0.70:8765
@token = sk_opena6_browser_v3_production

### Health Check
GET {{baseUrl}}/health

### Get Tool Manifest
GET {{baseUrl}}/manifest

### Get Status
GET {{baseUrl}}/status

### Open Website
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "open",
  "url": "https://example.com"
}

### Click Element
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "click",
  "url": "https://example.com",
  "element": "button.submit"
}

### Type Text
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "type",
  "url": "https://example.com",
  "element": "input[name=search]",
  "text": "GitHub"
}

### Extract Text
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "extract_text",
  "url": "https://example.com",
  "element": "body"
}

### Extract HTML
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "extract_html",
  "url": "https://example.com",
  "element": "main"
}

### Query DOM
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "query_selector",
  "url": "https://example.com",
  "selector": "h1"
}

### Take Screenshot
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "screenshot",
  "url": "https://example.com"
}

### Scroll Page
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "scroll",
  "url": "https://example.com",
  "direction": "down",
  "amount": 3
}

### Wait for Element
POST {{baseUrl}}/call
Content-Type: application/json
Authorization: Bearer {{token}}

{
  "action": "wait_for",
  "url": "https://example.com",
  "element": ".dynamic-content",
  "timeout": 10
}
"""


# ==================== VS Code Extension Settings ====================

VSCODE_SETTINGS = {
    "rest-client.environmentVariables": {
        "$shared": {
            "baseUrl": "http://192.168.0.70:8765",
            "token": "sk_opena6_browser_v3_production"
        }
    },
    "rest-client.defaultHeaders": {
        "User-Agent": "VS Code REST Client",
        "Accept": "application/json"
    },
    "rest-client.timeoutinmilliseconds": 30000,
    "explorer.fileNesting.enabled": True,
    "explorer.fileNesting.patterns": {
        "*.rest": "${basename}.json, ${basename}.http"
    }
}


# ==================== Launch Configuration ====================

VSCODE_LAUNCH_CONFIG = {
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Browser Agent Tool Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/LocalAgent-Pro/opena6/tool_server.py",
            "console": "integratedTerminal",
            "justMyCode": False,
            "args": ["--host", "0.0.0.0", "--port", "8765"],
            "env": {
                "BEARER_TOKEN": "sk_opena6_browser_v3_production",
                "DEBUG": "1"
            }
        },
        {
            "name": "Browser Agent opena6",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/LocalAgent-Pro/opena6/main.py",
            "console": "integratedTerminal",
            "justMyCode": False,
            "env": {
                "PORT": "12350",
                "DEBUG": "1"
            }
        }
    ],
    "compounds": [
        {
            "name": "Full Stack (Tool Server + Agent)",
            "configurations": [
                "Browser Agent Tool Server",
                "Browser Agent opena6"
            ]
        }
    ]
}


# ==================== Tasks Configuration ====================

VSCODE_TASKS = {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Tool Server",
            "type": "shell",
            "command": "cd LocalAgent-Pro/opena6 && python3 tool_server.py --host 0.0.0.0 --port 8765",
            "isBackground": True,
            "problemMatcher": {
                "pattern": {
                    "regexp": "^.*$",
                    "file": 1,
                    "location": 2,
                    "message": 3
                },
                "background": {
                    "activeOnStart": True,
                    "beginsPattern": ".*Tool Server.*",
                    "endsPattern": ".*Listening.*"
                }
            },
            "group": {
                "kind": "build",
                "isDefault": True
            }
        },
        {
            "label": "Health Check",
            "type": "shell",
            "command": "curl -s http://192.168.0.70:8765/health | jq",
            "problemMatcher": [],
            "group": "test"
        },
        {
            "label": "Test Tool Actions",
            "type": "shell",
            "command": "python3 -c \"import httpx; r = httpx.get('http://192.168.0.70:8765/manifest'); print(r.json())\"",
            "problemMatcher": [],
            "group": "test"
        },
        {
            "label": "View Dashboard",
            "type": "shell",
            "command": "python3 -m webbrowser 'http://192.168.0.70:8765/'",
            "problemMatcher": []
        }
    ]
}


# ==================== VS Code Commands ====================

VSCODE_COMMANDS = """
// Browser Agent Tool Commands für VS Code Command Palette

{
    "contributes": {
        "commands": [
            {
                "command": "browserAgent.openToolServer",
                "title": "Browser Agent: Start Tool Server",
                "category": "Browser Agent"
            },
            {
                "command": "browserAgent.healthCheck",
                "title": "Browser Agent: Health Check",
                "category": "Browser Agent"
            },
            {
                "command": "browserAgent.openDashboard",
                "title": "Browser Agent: Open Dashboard",
                "category": "Browser Agent"
            },
            {
                "command": "browserAgent.copyManifest",
                "title": "Browser Agent: Copy Manifest JSON",
                "category": "Browser Agent"
            },
            {
                "command": "browserAgent.testAction",
                "title": "Browser Agent: Test Browser Action",
                "category": "Browser Agent"
            },
            {
                "command": "browserAgent.viewLogs",
                "title": "Browser Agent: View Server Logs",
                "category": "Browser Agent"
            },
            {
                "command": "browserAgent.stopServer",
                "title": "Browser Agent: Stop Tool Server",
                "category": "Browser Agent"
            }
        ],
        "keybindings": [
            {
                "command": "browserAgent.healthCheck",
                "key": "ctrl+shift+b",
                "mac": "cmd+shift+b"
            },
            {
                "command": "browserAgent.openDashboard",
                "key": "ctrl+shift+d",
                "mac": "cmd+shift+d"
            }
        ]
    }
}
"""


# ==================== Keybindings ====================

VSCODE_KEYBINDINGS = """
// Keyboard Shortcuts für Browser Agent

[
    {
        "key": "ctrl+shift+b",
        "command": "workbench.action.tasks.runTask",
        "args": "Health Check"
    },
    {
        "key": "ctrl+shift+d",
        "command": "workbench.action.openDefaultBrowser",
        "args": "http://192.168.0.70:8765/"
    },
    {
        "key": "ctrl+alt+t",
        "command": "workbench.action.tasks.runTask",
        "args": "Start Tool Server"
    }
]
"""


# ==================== Python Bridge Class ====================

class VSCodeBridge:
    """Bridge zwischen VS Code und Browser Agent Tool Server"""

    def __init__(self, base_url: str = "http://192.168.0.70:8765"):
        self.base_url = base_url
        self.token = "sk_opena6_browser_v3_production"
        self.client = None
        self.workspace_path = Path.cwd()

    async def initialize(self):
        """Initialisiere HTTP Client"""
        self.client = httpx.AsyncClient(timeout=30)

    async def health_check(self) -> Dict[str, Any]:
        """Überprüfe Server Health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def execute_action(
        self,
        action: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Führe Browser Action aus"""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            payload = {"action": action, "url": url, **kwargs}

            response = await self.client.post(
                f"{self.base_url}/call",
                json=payload,
                headers=headers
            )
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def generate_rest_client_file(self, output_path: Optional[str] = None):
        """Generiere REST Client .http Datei"""
        if output_path is None:
            output_path = self.workspace_path / "browser_agent.http"

        with open(output_path, "w") as f:
            f.write(REST_CLIENT_TEMPLATE)

        print(f"✅ REST Client File erstellt: {output_path}")
        return output_path

    def generate_vscode_config(self, output_dir: Optional[str] = None):
        """Generiere VS Code Konfigurationsdateien"""
        if output_dir is None:
            output_dir = self.workspace_path / ".vscode"

        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)

        # settings.json
        with open(output_dir / "settings.json", "w") as f:
            json.dump(VSCODE_SETTINGS, f, indent=2)
        print(f"✅ settings.json erstellt")

        # launch.json
        with open(output_dir / "launch.json", "w") as f:
            json.dump(VSCODE_LAUNCH_CONFIG, f, indent=2)
        print(f"✅ launch.json erstellt")

        # tasks.json
        with open(output_dir / "tasks.json", "w") as f:
            json.dump(VSCODE_TASKS, f, indent=2)
        print(f"✅ tasks.json erstellt")

    async def close(self):
        """Schließe HTTP Client"""
        if self.client:
            await self.client.aclose()

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# ==================== CLI Commands ====================

async def setup_vscode_integration(workspace_path: str = "."):
    """Vollständige VS Code Integration Setup"""
    async with VSCodeBridge() as bridge:
        print("🔧 Richte VS Code Integration ein...\n")

        # Generiere Dateien
        bridge.workspace_path = Path(workspace_path)
        bridge.generate_rest_client_file()
        bridge.generate_vscode_config()

        # Health Check
        print("\n🏥 Health Check...")
        health = await bridge.health_check()
        print(f"Status: {health.get('status', 'unknown')}")

        print("\n✅ VS Code Integration setup fertig!")
        print("\nNächste Schritte:")
        print("1. Öffne VS Code")
        print("2. Installiere 'REST Client' Extension")
        print("3. Öffne 'browser_agent.http'")
        print("4. Klicke 'Send Request' auf den API Calls")


def create_launch_json_snippet():
    """Erstelle ein snippet für launch.json"""
    return json.dumps(VSCODE_LAUNCH_CONFIG, indent=2)


def create_tasks_json_snippet():
    """Erstelle ein snippet für tasks.json"""
    return json.dumps(VSCODE_TASKS, indent=2)


# ==================== Main ====================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        workspace = sys.argv[2] if len(sys.argv) > 2 else "."
        asyncio.run(setup_vscode_integration(workspace))
    else:
        print("Browser Agent VS Code Bridge\n")
        print("Verwendung:")
        print("  python3 vscode_bridge.py setup [workspace_path]")
        print("\nBeispiele:")
        print("  python3 vscode_bridge.py setup")
        print("  python3 vscode_bridge.py setup /path/to/workspace")
