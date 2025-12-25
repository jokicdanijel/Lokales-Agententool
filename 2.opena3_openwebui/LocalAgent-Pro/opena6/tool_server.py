#!/usr/bin/env python3
"""
Browser Agent - OpenWebUI Tool Server
HTTP-Server für die Integration mit OpenWebUI als External Tool

Dieser Server stellt die Browser-Automation als OpenWebUI-kompatibles Tool
über HTTP-Endpoints zur Verfügung.

OpenWebUI verbindet sich mit diesem Server und kann dann den Browser Agent
in den Chat-Modellen verwenden.

Verfügbare Endpoints:
  GET  /health              - Health Check
  GET  /manifest            - Tool Manifest/Definition
  POST /call                - Tool aufrufen
  POST /execute             - Direkt Browser-Aktion ausführen
"""

import http.server
import json
import logging
import socketserver
import threading
from datetime import datetime
from typing import Any

# ============================================================================
# SETUP
# ============================================================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [TOOL_SERVER] %(levelname)s - %(message)s")
logger = logging.getLogger("tool_server")

# ============================================================================
# TOOL MANIFEST
# ============================================================================

TOOL_MANIFEST = {
    "type": "function",
    "function": {
        "name": "browser_agent",
        "description": "Lokale Browser-Automation für Web-Scraping, Datenextraktion und DOM-Manipulation. Wird vom PORTIER 3.0 System bereitgestellt.",
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
                    "description": "Browser-Aktion ausführen",
                },
                "url": {"type": "string", "description": "Zielseite URL (z.B. https://example.com)"},
                "selector": {"type": "string", "description": "CSS oder XPath Selektor"},
                "text": {"type": "string", "description": "Text zum eingeben (für 'type' Aktion)"},
                "wait_ms": {"type": "integer", "default": 500, "description": "Wartezeit nach Aktion in ms"},
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
# TOOL SERVER
# ============================================================================


class ToolServerHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP Handler für Tool Server"""

    # Referenz zum Hauptserver
    tool_server = None

    def do_GET(self):
        """Handle GET requests"""
        logger.info(f"GET {self.path}")

        if self.path == "/":
            self._send_html_dashboard()

        elif self.path == "/health":
            self._send_json(
                {
                    "status": "ok",
                    "timestamp": datetime.now().isoformat(),
                    "service": "Browser Agent Tool Server",
                    "version": "1.0.0",
                }
            )

        elif self.path == "/manifest":
            self._send_json(TOOL_MANIFEST)

        elif self.path == "/status":
            self._send_json(
                {
                    "status": "operational",
                    "uptime": self.tool_server.get_uptime() if self.tool_server else "unknown",
                    "calls_total": self.tool_server.call_count if self.tool_server else 0,
                    "last_call": self.tool_server.last_call if self.tool_server else None,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        logger.info(f"POST {self.path}")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON"}, status=400)
            return

        if self.path == "/call":
            self._handle_tool_call(data)

        elif self.path == "/execute":
            self._handle_execute(data)

        else:
            self._send_json({"error": "Unknown endpoint"}, status=404)

    def _handle_tool_call(self, data: dict[str, Any]):
        """Handle tool call from OpenWebUI"""
        logger.info(f"Tool call: {data}")

        # Extract function definition
        if "function" in data:
            func = data["function"]
            func_args = func.get("arguments", {})
        else:
            func_args = data.get("arguments", data)

        # Forward to Browser Agent
        result = self._forward_to_agent(func_args)
        self._send_json(result)

    def _handle_execute(self, data: dict[str, Any]):
        """Handle direct execute request"""
        logger.info(f"Execute: {data}")
        result = self._forward_to_agent(data)
        self._send_json(result)

    def _forward_to_agent(self, args: dict[str, Any]) -> dict[str, Any]:
        """Forward request to Browser Agent"""
        import requests

        try:
            agent_url = "http://localhost:12350"
            bearer_token = "sk_opena6_browser_v3_production"

            response = requests.post(
                f"{agent_url}/execute",
                json=args,
                headers={"Authorization": f"Bearer {bearer_token}", "Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Agent response: {result.get('status')}")
                return result
            else:
                logger.error(f"❌ Agent error: {response.status_code}")
                return {"status": "error", "message": f"Agent error: {response.status_code}", "details": response.text}

        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return {"status": "error", "message": str(e)}

    def _send_json(self, data: dict[str, Any], status: int = 200):
        """Send JSON response"""
        response = json.dumps(data, indent=2, ensure_ascii=False)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response.encode("utf-8"))

        # Track call
        if self.tool_server:
            self.tool_server.last_call = datetime.now().isoformat()
            self.tool_server.call_count += 1

    def _send_html_dashboard(self):
        """Send HTML dashboard"""
        html = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Browser Agent Tool Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        header p {
            opacity: 0.9;
            font-size: 14px;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            border-radius: 8px;
        }
        .status-box strong {
            display: block;
            margin-bottom: 5px;
            color: #333;
        }
        .status-box code {
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
            color: #666;
            background: white;
            padding: 8px;
            border-radius: 4px;
            display: block;
            word-break: break-all;
        }
        .endpoint {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 13px;
        }
        .endpoint strong {
            color: #667eea;
            display: block;
            margin-bottom: 8px;
        }
        .endpoint pre {
            background: white;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            color: #333;
        }
        .actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        button:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .alert {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert.error {
            background: #f8d7da;
            border-color: #f5c6cb;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌐 Browser Agent Tool Server</h1>
            <p>OpenWebUI Integration - PORTIER 3.0 System</p>
        </header>
        <div class="content">
            <div class="alert">
                ✅ Tool Server ist aktiv und bereit für die OpenWebUI-Integration
            </div>

            <div class="section">
                <h2>📊 Status</h2>
                <div class="status-grid">
                    <div class="status-box">
                        <strong>Server</strong>
                        <code id="status-server">🟢 ONLINE</code>
                    </div>
                    <div class="status-box">
                        <strong>Agent</strong>
                        <code id="status-agent">⏳ Prüfe...</code>
                    </div>
                    <div class="status-box">
                        <strong>Aufrufe</strong>
                        <code id="status-calls">0</code>
                    </div>
                    <div class="status-box">
                        <strong>Letzter Aufruf</strong>
                        <code id="status-last">Keine</code>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🔗 API Endpoints</h2>
                <div class="endpoint">
                    <strong>GET /health</strong>
                    <pre>curl http://localhost:8765/health</pre>
                </div>
                <div class="endpoint">
                    <strong>GET /manifest</strong>
                    <pre>curl http://localhost:8765/manifest</pre>
                </div>
                <div class="endpoint">
                    <strong>POST /execute</strong>
                    <pre>curl -X POST http://localhost:8765/execute \\
  -H "Content-Type: application/json" \\
  -d '{
    "action": "open",
    "url": "https://example.com"
  }'</pre>
                </div>
            </div>

            <div class="section">
                <h2>🚀 OpenWebUI Integration</h2>
                <ol style="line-height: 1.8; margin-left: 20px;">
                    <li>Öffne OpenWebUI Admin: <code>http://192.168.0.70:3000/admin</code></li>
                    <li>Navigiere zu: Settings → External Tools/Functions</li>
                    <li>Klick "Add External Tool"</li>
                    <li>Gib folgende URL ein: <code>http://192.168.0.70:8765/manifest</code></li>
                    <li>Speichere die Konfiguration</li>
                    <li>Starte einen Chat und teste den Browser Agent</li>
                </ol>
            </div>

            <div class="section">
                <h2>🧪 Test-Aktionen</h2>
                <div class="actions">
                    <button onclick="testHealth()">Health Check</button>
                    <button onclick="testManifest()">Manifest</button>
                    <button onclick="testAgent()">Agent Verbindung</button>
                </div>
                <div id="test-result" style="margin-top: 15px;"></div>
            </div>

            <div class="section">
                <h2>📚 Dokumentation</h2>
                <p style="line-height: 1.6; color: #666;">
                    Der Browser Agent Tool Server stellt eine HTTP-API bereit, die von OpenWebUI
                    verwendet werden kann, um Browser-Automation durchzuführen.
                </p>
                <p style="margin-top: 10px; font-size: 13px; color: #999;">
                    Siehe <code>OPENWEBUI_INTEGRATION.md</code> für vollständige Dokumentation.
                </p>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh status
        function updateStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status-calls').textContent = data.calls_total || 0;
                    document.getElementById('status-last').textContent = data.last_call || 'Keine';
                });

            // Check agent
            fetch('http://localhost:12350/health')
                .then(r => {
                    if (r.ok) {
                        document.getElementById('status-agent').textContent = '🟢 ONLINE';
                        document.getElementById('status-agent').style.color = '#28a745';
                    } else {
                        throw new Error();
                    }
                })
                .catch(() => {
                    document.getElementById('status-agent').textContent = '🔴 OFFLINE';
                    document.getElementById('status-agent').style.color = '#dc3545';
                });
        }

        function testHealth() {
            fetch('/health')
                .then(r => r.json())
                .then(data => {
                    showResult('✅ Health Check erfolgreich', data);
                })
                .catch(err => {
                    showResult('❌ Health Check fehlgeschlagen', {error: err.message});
                });
        }

        function testManifest() {
            fetch('/manifest')
                .then(r => r.json())
                .then(data => {
                    showResult('✅ Manifest geladen', data);
                })
                .catch(err => {
                    showResult('❌ Manifest Fehler', {error: err.message});
                });
        }

        function testAgent() {
            fetch('http://localhost:12350/health')
                .then(r => r.json())
                .then(data => {
                    showResult('✅ Agent verbunden', data);
                })
                .catch(err => {
                    showResult('❌ Agent nicht erreichbar', {error: err.message});
                });
        }

        function showResult(title, data) {
            const resultDiv = document.getElementById('test-result');
            resultDiv.innerHTML = `
                <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px;">
                    <strong style="display: block; margin-bottom: 10px;">${title}</strong>
                    <pre style="background: white; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px;">
${JSON.stringify(data, null, 2)}
                    </pre>
                </div>
            `;
        }

        // Update on load and every 5 seconds
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(format % args)


# ============================================================================
# MAIN TOOL SERVER
# ============================================================================


class ToolServer:
    """Main Tool Server"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.start_time = datetime.now()
        self.call_count = 0
        self.last_call = None
        self.server = None
        self.thread = None

    def get_uptime(self) -> str:
        """Get uptime string"""
        uptime = datetime.now() - self.start_time
        return str(uptime).split(".")[0]

    def start(self):
        """Start the server"""
        ToolServerHandler.tool_server = self

        self.server = socketserver.TCPServer((self.host, self.port), ToolServerHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

        logger.info(f"🚀 Tool Server gestartet auf {self.host}:{self.port}")
        logger.info(f"   Dashboard: http://localhost:{self.port}")
        logger.info(f"   Manifest: http://localhost:{self.port}/manifest")
        logger.info(f"   OpenWebUI URL: http://192.168.0.70:{self.port}/manifest")

    def stop(self):
        """Stop the server"""
        if self.server:
            self.server.shutdown()
            logger.info("Tool Server gestoppt")

    def run_forever(self):
        """Run server forever"""
        try:
            self.start()
            self.thread.join()
        except KeyboardInterrupt:
            logger.info("\n⏹️  Server wird heruntergefahren...")
            self.stop()


# ============================================================================
# CLI
# ============================================================================


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Browser Agent - OpenWebUI Tool Server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (0.0.0.0 für externen Zugriff)")
    parser.add_argument("--port", type=int, default=8765, help="Port")
    parser.add_argument("--local", action="store_true", help="Nur auf localhost (127.0.0.1) lauschen")

    args = parser.parse_args()

    # Wenn --local Flag gesetzt, nutze 127.0.0.1
    if args.local:
        args.host = "127.0.0.1"

    logger.info("")
    logger.info("╔═══════════════════════════════════════════════════════╗")
    logger.info("║   Browser Agent - OpenWebUI Tool Server              ║")
    logger.info("║   PORTIER 3.0 System Integration                     ║")
    logger.info("╚═══════════════════════════════════════════════════════╝")
    logger.info("")

    server = ToolServer(host=args.host, port=args.port)
    server.run_forever()


if __name__ == "__main__":
    main()
