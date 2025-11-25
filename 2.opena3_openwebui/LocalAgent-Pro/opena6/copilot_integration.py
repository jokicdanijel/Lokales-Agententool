"""
VS Code Copilot ↔ OpenWebUI Integration Bridge

Verbindet GitHub Copilot in VS Code direkt mit OpenWebUI Browser Agent.
Ermöglicht Web-Automation Commands direkt im VS Code Editor.

Features:
- Copilot Chat Integration
- Slash Commands für Browser Actions
- Inline Code Snippets Generierung
- Web-basierte Searches
- Real-time Terminal Output
- Auto-completion für Browser Actions
- Error Handling & Suggestions

Installation:
1. VS Code Extension: "Copilot" & "Copilot Chat"
2. Copy this file to .vscode/extensions/
3. Configure in settings.json
4. Nutze "/browser" Slash Command in Copilot Chat

Usage:
@copilot /browser open https://github.com
@copilot /browser extract h1
@copilot /browser click button.submit
"""

import json
import asyncio
import httpx
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime


# ==================== Copilot Chat Commands ====================

COPILOT_CHAT_COMMANDS = {
    "commands": [
        {
            "id": "browser-agent.openwebui",
            "title": "Browser Agent: OpenWebUI",
            "description": "Control Browser Agent via OpenWebUI",
            "when": "editorTextFocus"
        },
        {
            "id": "browser-agent.extract-content",
            "title": "Extract Content from URL",
            "description": "Extract text or HTML from any website"
        },
        {
            "id": "browser-agent.screenshot",
            "title": "Take Website Screenshot",
            "description": "Capture screenshot of website"
        },
        {
            "id": "browser-agent.test-action",
            "title": "Test Browser Action",
            "description": "Test browser automation action"
        }
    ],
    "slashCommands": [
        {
            "name": "browser",
            "description": "Control Browser Agent",
            "help": "Usage: @copilot /browser [action] [url] [selector]"
        },
        {
            "name": "screenshot",
            "description": "Take screenshot",
            "help": "Usage: @copilot /screenshot [url]"
        },
        {
            "name": "extract",
            "description": "Extract content",
            "help": "Usage: @copilot /extract [url] [selector]"
        },
        {
            "name": "click",
            "description": "Click element",
            "help": "Usage: @copilot /click [url] [selector]"
        }
    ]
}


# ==================== Copilot System Prompt ====================

COPILOT_SYSTEM_PROMPT = """You are an AI assistant integrated with Browser Agent Tool Server.
You have access to web automation capabilities through the Browser Agent.

Available Browser Actions:
1. open - Open website: /browser open https://example.com
2. click - Click element: /browser click selector
3. type - Type text: /browser type selector "text"
4. extract_text - Get text: /browser extract_text selector
5. extract_html - Get HTML: /browser extract_html selector
6. query_selector - Query DOM: /browser query_selector "h1"
7. screenshot - Screenshot: /browser screenshot
8. scroll - Scroll page: /browser scroll down 3
9. wait_for - Wait: /browser wait_for selector

When user asks to:
- "Open" a website → Suggest /browser open [url]
- "Extract" content → Suggest /browser extract_text or /browser extract_html
- "Click" something → Suggest /browser click [selector]
- "Screenshot" → Suggest /browser screenshot
- "Find" elements → Suggest /browser query_selector [selector]

Always provide:
1. The exact slash command
2. Code snippet if applicable
3. Explanation of what it does
4. Expected result

Connection Details:
- Server: http://192.168.0.70:8765
- Token: sk_opena6_browser_v3_production
- Health: /health endpoint
- Manifest: /manifest endpoint
"""


# ==================== VS Code Extension Settings ====================

COPILOT_SETTINGS = {
    "github.copilot.enable": {
        "*": True,
        "plaintext": False,
        "markdown": True
    },
    "[javascript]": {
        "editor.defaultFormatter": "esbenp.prettier-vscode"
    },
    "browser-agent.serverUrl": "http://192.168.0.70:8765",
    "browser-agent.bearerToken": "sk_opena6_browser_v3_production",
    "browser-agent.enableCopilotIntegration": True,
    "browser-agent.autoSuggestActions": True,
    "browser-agent.showStatusBar": True,
    "browser-agent.debugMode": False
}


# ==================== Extension package.json ====================

EXTENSION_PACKAGE = {
    "name": "browser-agent-copilot",
    "displayName": "Browser Agent Copilot Extension",
    "description": "Browser Agent integration for GitHub Copilot in VS Code",
    "version": "1.0.0",
    "publisher": "opena6",
    "engines": {
        "vscode": "^1.88.0"
    },
    "categories": [
        "AI",
        "Chat",
        "Debuggers"
    ],
    "keywords": [
        "copilot",
        "browser-automation",
        "web-scraping",
        "ai-assistant"
    ],
    "activationEvents": [
        "onCommand:browser-agent.openwebui",
        "onChatParticipant:browser"
    ],
    "contributes": {
        "commands": COPILOT_CHAT_COMMANDS["commands"],
        "chatParticipants": [
            {
                "id": "browser",
                "fullName": "Browser Agent",
                "description": "Browser automation assistant",
                "isSticky": True,
                "commands": [
                    {
                        "name": "open",
                        "description": "Open website"
                    },
                    {
                        "name": "extract",
                        "description": "Extract content"
                    },
                    {
                        "name": "screenshot",
                        "description": "Take screenshot"
                    }
                ]
            }
        ],
        "configuration": {
            "title": "Browser Agent",
            "properties": {
                "browser-agent.serverUrl": {
                    "type": "string",
                    "default": "http://192.168.0.70:8765",
                    "description": "Tool Server URL"
                },
                "browser-agent.bearerToken": {
                    "type": "string",
                    "default": "sk_opena6_browser_v3_production",
                    "description": "Bearer token for authentication"
                },
                "browser-agent.enableCopilotIntegration": {
                    "type": "boolean",
                    "default": True,
                    "description": "Enable Copilot chat integration"
                }
            }
        }
    },
    "main": "./out/extension.js",
    "scripts": {
        "vscode:prepublish": "npm run compile",
        "compile": "tsc -p ./",
        "watch": "tsc -watch -p ./",
        "pretest": "npm run compile && npm run lint",
        "lint": "eslint src --ext ts"
    },
    "devDependencies": {
        "@types/vscode": "^1.88.0",
        "@types/node": "^20.0.0",
        "typescript": "^5.0.0"
    },
    "dependencies": {
        "axios": "^1.6.0"
    }
}


# ==================== Extension TypeScript Code ====================

EXTENSION_TYPESCRIPT = '''
import * as vscode from 'vscode';

interface IBrowserAgentAPI {
    executeAction(action: string, url: string, selector?: string): Promise<any>;
    getStatus(): Promise<any>;
    getManifest(): Promise<any>;
}

class BrowserAgentCopilotExtension implements IBrowserAgentAPI {
    private serverUrl: string;
    private bearerToken: string;
    private statusBar: vscode.StatusBarItem;

    constructor() {
        const config = vscode.workspace.getConfiguration('browser-agent');
        this.serverUrl = config.get('serverUrl', 'http://192.168.0.70:8765');
        this.bearerToken = config.get('bearerToken', 'sk_opena6_browser_v3_production');

        // Create status bar
        this.statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBar.text = '$(chrome) Browser Agent';
        this.statusBar.command = 'browser-agent.openwebui';
        this.statusBar.show();
    }

    async executeAction(action: string, url: string, selector?: string): Promise<any> {
        try {
            const payload = { action, url, selector };
            const response = await fetch(`${this.serverUrl}/call`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.bearerToken}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            vscode.window.showErrorMessage(`Browser Agent Error: ${error}`);
            throw error;
        }
    }

    async getStatus(): Promise<any> {
        return await fetch(`${this.serverUrl}/status`).then(r => r.json());
    }

    async getManifest(): Promise<any> {
        return await fetch(`${this.serverUrl}/manifest`).then(r => r.json());
    }

    async handleCopilotSlashCommand(command: string, args: string[]): Promise<string> {
        switch (command) {
            case 'open':
                return await this.handleOpenCommand(args);
            case 'extract':
                return await this.handleExtractCommand(args);
            case 'screenshot':
                return await this.handleScreenshotCommand(args);
            case 'click':
                return await this.handleClickCommand(args);
            default:
                return `Unknown command: ${command}`;
        }
    }

    private async handleOpenCommand(args: string[]): Promise<string> {
        if (!args[0]) return 'Usage: /browser open <url>';

        const result = await this.executeAction('open', args[0]);
        return `✅ Opened ${args[0]}\\n${JSON.stringify(result, null, 2)}`;
    }

    private async handleExtractCommand(args: string[]): Promise<string> {
        if (!args[0] || !args[1]) return 'Usage: /browser extract <url> <selector>';

        const result = await this.executeAction('extract_text', args[0], args[1]);
        return `📄 Extracted content:\\n${result.result}`;
    }

    private async handleScreenshotCommand(args: string[]): Promise<string> {
        if (!args[0]) return 'Usage: /browser screenshot <url>';

        const result = await this.executeAction('screenshot', args[0]);
        return `📸 Screenshot saved: ${result.result}`;
    }

    private async handleClickCommand(args: string[]): Promise<string> {
        if (!args[0] || !args[1]) return 'Usage: /browser click <url> <selector>';

        const result = await this.executeAction('click', args[0], args[1]);
        return `🖱️ Clicked ${args[1]}`;
    }
}

export async function activate(context: vscode.ExtensionContext) {
    const extension = new BrowserAgentCopilotExtension();

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('browser-agent.openwebui', () => {
            vscode.window.showInformationMessage('Browser Agent OpenWebUI Integration Active');
        })
    );

    // Register chat handler
    const chatHandler = vscode.chat.createChatParticipant('browser', async (request, context, stream, token) => {
        if (request.command === 'open') {
            stream.markdown('Opening website...\\n');
            const result = await extension.executeAction('open', request.prompt);
            stream.markdown(`✅ ${JSON.stringify(result)}`);
        }
    });

    context.subscriptions.push(chatHandler);
}

export function deactivate() {}
'''


# ==================== Copilot Integration File ====================

COPILOT_INTEGRATION_JSON = {
    "participantId": "browser",
    "name": "Browser Agent",
    "description": "Web automation and scraping assistant",
    "isSticky": True,
    "commands": [
        {
            "name": "open",
            "description": "Open a website",
            "when": "always",
            "examples": [
                "@browser /open https://github.com",
                "@browser Open GitHub",
                "@browser Navigate to example.com"
            ]
        },
        {
            "name": "extract",
            "description": "Extract content from website",
            "when": "always",
            "examples": [
                "@browser /extract https://github.com h1",
                "@browser Extract the main heading",
                "@browser Get all text from the page"
            ]
        },
        {
            "name": "screenshot",
            "description": "Take website screenshot",
            "when": "always",
            "examples": [
                "@browser /screenshot https://github.com",
                "@browser Screenshot this site",
                "@browser Take a picture of example.com"
            ]
        },
        {
            "name": "click",
            "description": "Click element on page",
            "when": "always",
            "examples": [
                "@browser /click https://github.com button.submit",
                "@browser Click the submit button",
                "@browser Find and click the login button"
            ]
        }
    ],
    "defaultSlashCommand": "open"
}


# ==================== Python Bridge for Copilot ====================

class CopilotBrowserAgentBridge:
    """Bridge zwischen Copilot Chat und Browser Agent"""

    def __init__(self, server_url: str = "http://192.168.0.70:8765"):
        self.server_url = server_url
        self.token = "sk_opena6_browser_v3_production"
        self.client = None

    async def initialize(self):
        """Initialize async client"""
        self.client = httpx.AsyncClient(timeout=30)

    async def handle_copilot_request(
        self,
        command: str,
        args: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle Copilot slash command request"""

        command_handlers = {
            "open": self._handle_open,
            "extract": self._handle_extract,
            "screenshot": self._handle_screenshot,
            "click": self._handle_click,
            "type": self._handle_type,
            "query": self._handle_query,
            "scroll": self._handle_scroll,
            "wait": self._handle_wait
        }

        handler = command_handlers.get(command)
        if not handler:
            return {
                "status": "error",
                "message": f"Unknown command: {command}",
                "available_commands": list(command_handlers.keys())
            }

        try:
            return await handler(args, context)
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def _handle_open(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser open command"""
        if not args:
            return {"status": "error", "message": "URL required"}

        url = args[0]
        result = await self._execute_action("open", url)
        return {
            "status": "success",
            "action": "open",
            "url": url,
            "result": result,
            "snippet": f"```bash\\ncurl -X POST {self.server_url}/call \\\\\\n  -H 'Authorization: Bearer {self.token}' \\\\\\n  -d '{{\\"action\\": \\"open\\", \\"url\\": \\"{url}\\"}}'\n```"
        }

    async def _handle_extract(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser extract command"""
        if len(args) < 2:
            return {"status": "error", "message": "URL and selector required"}

        url, selector = args[0], args[1]
        result = await self._execute_action("extract_text", url, element=selector)
        return {
            "status": "success",
            "action": "extract_text",
            "url": url,
            "selector": selector,
            "result": result.get("result", ""),
            "code_example": f"```python\\nawait tool.extract_text(\\"{url}\\", \\"{selector}\\")\n```"
        }

    async def _handle_screenshot(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser screenshot command"""
        if not args:
            return {"status": "error", "message": "URL required"}

        url = args[0]
        result = await self._execute_action("screenshot", url)
        return {
            "status": "success",
            "action": "screenshot",
            "url": url,
            "filepath": result.get("result", ""),
            "message": f"📸 Screenshot captured: {result.get('result')}"
        }

    async def _handle_click(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser click command"""
        if len(args) < 2:
            return {"status": "error", "message": "URL and selector required"}

        url, selector = args[0], args[1]
        result = await self._execute_action("click", url, element=selector)
        return {
            "status": "success",
            "action": "click",
            "url": url,
            "selector": selector,
            "message": f"🖱️ Clicked: {selector}"
        }

    async def _handle_type(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser type command"""
        if len(args) < 3:
            return {"status": "error", "message": "URL, selector, and text required"}

        url, selector, text = args[0], args[1], " ".join(args[2:])
        result = await self._execute_action("type", url, element=selector, text=text)
        return {
            "status": "success",
            "action": "type",
            "url": url,
            "selector": selector,
            "text": text,
            "message": f"⌨️ Typed into {selector}: {text}"
        }

    async def _handle_query(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser query command"""
        if len(args) < 2:
            return {"status": "error", "message": "URL and selector required"}

        url, selector = args[0], args[1]
        result = await self._execute_action("query_selector", url, selector=selector)
        return {
            "status": "success",
            "action": "query_selector",
            "url": url,
            "selector": selector,
            "result": result
        }

    async def _handle_scroll(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser scroll command"""
        if len(args) < 2:
            return {"status": "error", "message": "URL and direction required"}

        url, direction = args[0], args[1]
        amount = int(args[2]) if len(args) > 2 else 3
        result = await self._execute_action("scroll", url, direction=direction, amount=amount)
        return {
            "status": "success",
            "action": "scroll",
            "url": url,
            "direction": direction,
            "amount": amount,
            "message": f"📜 Scrolled {direction} by {amount} steps"
        }

    async def _handle_wait(self, args: List[str], context: Optional[Dict]) -> Dict:
        """Handle /browser wait command"""
        if len(args) < 2:
            return {"status": "error", "message": "URL and selector required"}

        url, selector = args[0], args[1]
        timeout = int(args[2]) if len(args) > 2 else 10
        result = await self._execute_action("wait_for", url, element=selector, timeout=timeout)
        return {
            "status": "success",
            "action": "wait_for",
            "url": url,
            "selector": selector,
            "timeout": timeout,
            "message": f"⏳ Waited for {selector} (timeout: {timeout}s)"
        }

    async def _execute_action(self, action: str, url: str, **kwargs) -> Dict:
        """Execute browser action"""
        payload = {"action": action, "url": url, **kwargs}
        headers = {"Authorization": f"Bearer {self.token}"}

        response = await self.client.post(
            f"{self.server_url}/call",
            json=payload,
            headers=headers
        )
        return response.json()

    async def close(self):
        """Close client"""
        if self.client:
            await self.client.aclose()


# ==================== Testing ====================

async def test_copilot_integration():
    """Test Copilot integration"""
    bridge = CopilotBrowserAgentBridge()
    await bridge.initialize()

    print("🧪 Testing Copilot Browser Agent Integration...\n")

    # Test commands
    tests = [
        ("open", ["https://example.com"]),
        ("screenshot", ["https://example.com"]),
        ("extract", ["https://example.com", "h1"]),
    ]

    for cmd, args in tests:
        print(f"Test: /browser {cmd} {' '.join(args)}")
        result = await bridge.handle_copilot_request(cmd, args)
        print(f"Result: {result['status']}\n")

    await bridge.close()


if __name__ == "__main__":
    asyncio.run(test_copilot_integration())
