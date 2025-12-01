#!/usr/bin/env python3
"""
5.opena6_browser - Main Agent Process
Local Browser Automation Agent with Portier Integration (Option-2-Flow)
Skeleton Implementation: Ready for Playwright/Selenium Plugin

ARCHITECTURE:
  opena1 (Dispatcher)
    ↓
  opena2 (Archivator) ← CMD Safepoint
    ↓
  5.opena6_browser (THIS) ← Execute
    ↓
  opena2 (Archivator) ← RESP Safepoint
    ↓
  opena1 (Dispatcher)
"""

import json
import logging
import http.server
import socketserver
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local imports (created below)
try:
    from dispatcher_client import DispatcherClient
    from browser_engine import BrowserEngineWrapper
except ImportError as e:
    print(f"⚠️  Warning: Could not import dependencies: {e}")

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_dir: str = './logs'):
    """Setup logging infrastructure"""
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'{log_dir}/opena6.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('opena6_browser')

logger = setup_logging()

# ============================================================================
# BROWSER AGENT CORE
# ============================================================================

class BrowserAgent:
    """Main browser agent class"""

    VALID_ACTIONS = [
        'open', 'click', 'type', 'extract_text', 'extract_html',
        'query_selector', 'screenshot', 'scroll', 'wait_for'
    ]

    def __init__(self, config_path: str = 'config.json'):
        """Initialize browser agent"""
        self.config = self._load_config(config_path)
        self.agent_name = self.config.get('agent_name', '5.opena6_browser')
        self.port = self.config.get('port', 12350)
        self.bearer_token = self.config.get('security', {}).get('bearer_token', 'sk_opena6_browser_v3_production')

        # Try to initialize dispatcher client (optional)
        try:
            self.dispatcher = DispatcherClient(
                agent_name=self.agent_name,
                bearer_token=self.bearer_token
            )
            logger.info("✅ Dispatcher client initialized")
        except Exception as e:
            logger.warning(f"⚠️  Dispatcher client not available: {e}")
            self.dispatcher = None

        # Try to initialize browser engine (optional)
        try:
            self.browser_engine = BrowserEngineWrapper(
                config=self.config.get('browser_engine', {})
            )
            logger.info("✅ Browser engine wrapper initialized")
        except Exception as e:
            logger.warning(f"⚠️  Browser engine not available: {e}")
            self.browser_engine = None

        # Session management
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = threading.Lock()

        # Health status
        self.is_healthy = True
        self.startup_time = datetime.utcnow().isoformat()
        self.command_count = 0
        self.command_lock = threading.Lock()

        logger.info(f"✅ Browser Agent initialized: {self.agent_name} on port {self.port}")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"✅ Config loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            return {}

    def create_session(self) -> str:
        """Create new browser session"""
        session_id = f"sess_{str(uuid.uuid4())[:8]}"
        with self.session_lock:
            self.sessions[session_id] = {
                'created_at': datetime.utcnow().isoformat(),
                'status': 'active',
                'last_action': None,
                'command_count': 0
            }
        logger.info(f"📍 Session created: {session_id}")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details"""
        with self.session_lock:
            return self.sessions.get(session_id)

    def execute_command(self, cmd: Dict[str, Any]) -> Dict[str, Any]:
        """Execute browser command from opena2"""
        try:
            action = cmd.get('action')
            url = cmd.get('url')

            if not action or not url:
                return self._error_response("Missing 'action' or 'url'")

            # Validate action
            if action not in self.VALID_ACTIONS:
                return self._error_response(f"Invalid action: {action}")

            # Get or create session
            session_id = cmd.get('session_id', self.create_session())
            session = self.get_session(session_id)

            if not session:
                return self._error_response(f"Session not found: {session_id}")

            logger.info(f"⚙️  Executing: {action} on {url}")

            # Execute action via browser engine
            if self.browser_engine:
                result = self._execute_via_engine(action, url, cmd)
            else:
                result = self._execute_stub(action, url, cmd)

            # Update session
            with self.session_lock:
                if session_id in self.sessions:
                    self.sessions[session_id]['last_action'] = action
                    self.sessions[session_id]['command_count'] += 1

            # Increment global counter
            with self.command_lock:
                self.command_count += 1

            # Create response envelope (PORTIER format)
            response = {
                'status': result.get('status', 'success'),
                'action': action,
                'url': url,
                'session_id': session_id,
                'timestamp': datetime.utcnow().isoformat(),
                'data': result.get('data', {}),
                'safepoint_id': str(uuid.uuid4())[:12]
            }

            logger.info(f"✅ Command executed: {action}")
            return response

        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return self._error_response(str(e))

    def _execute_via_engine(self, action: str, url: str, cmd: Dict) -> Dict:
        """Execute via browser engine"""
        try:
            if action == 'open':
                return self.browser_engine.open_url(url, cmd.get('wait_ms', 500))
            elif action == 'click':
                return self.browser_engine.click_element(url, cmd.get('selector'))
            elif action == 'type':
                return self.browser_engine.type_text(url, cmd.get('selector'), cmd.get('text'))
            elif action == 'extract_text':
                return self.browser_engine.extract_text(url, cmd.get('selector'))
            elif action == 'extract_html':
                return self.browser_engine.extract_html(url, cmd.get('selector'))
            elif action == 'query_selector':
                return self.browser_engine.query_selector(url, cmd.get('selector'))
            elif action == 'screenshot':
                return self.browser_engine.screenshot(url)
            elif action == 'scroll':
                return self.browser_engine.scroll(url, cmd.get('wait_ms', 500))
            elif action == 'wait_for':
                return self.browser_engine.wait_for(url, cmd.get('selector'), cmd.get('wait_ms', 5000))
        except Exception as e:
            logger.error(f"Browser engine error: {e}")
            return self._stub_response(action, url)

    def _execute_stub(self, action: str, url: str, cmd: Dict) -> Dict:
        """Execute stub (fallback when engine not available)"""
        return self._stub_response(action, url)

    def _stub_response(self, action: str, url: str) -> Dict:
        """Generate stub response"""
        responses = {
            'open': {'status': 'success', 'data': {'session_id': f'sess_{uuid.uuid4().hex[:8]}', 'url': url}},
            'click': {'status': 'success', 'data': {'executed': True}},
            'type': {'status': 'success', 'data': {'text_length': 0}},
            'extract_text': {'status': 'success', 'data': {'text': '[stub response]'}},
            'extract_html': {'status': 'success', 'data': {'html': '<html>[stub response]</html>'}},
            'query_selector': {'status': 'success', 'data': {'elements': 0}},
            'screenshot': {'status': 'success', 'data': {'path': '/tmp/screenshot.png'}},
            'scroll': {'status': 'success', 'data': {'scrolled': True}},
            'wait_for': {'status': 'success', 'data': {'element_appeared': True}}
        }
        return responses.get(action, {'status': 'success', 'data': {}})

    def get_health_status(self) -> Dict[str, Any]:
        """Get agent health status"""
        return {
            'agent': self.agent_name,
            'status': 'healthy' if self.is_healthy else 'unhealthy',
            'startup_time': self.startup_time,
            'active_sessions': len(self.sessions),
            'total_commands': self.command_count,
            'port': self.port,
            'timestamp': datetime.utcnow().isoformat()
        }

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            'status': 'error',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }


# ============================================================================
# HTTP REQUEST HANDLER
# ============================================================================

class BrowserAgentHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for browser agent requests"""

    agent: BrowserAgent = None
    bearer_token: str = None

    def do_GET(self):
        """Handle GET requests"""
        path = self.path.split('?')[0]

        if path == '/health':
            self._send_json(self.agent.get_health_status(), 200)
        elif path == '/status':
            self._send_json({
                'status': 'online',
                'agent': self.agent.agent_name,
                'sessions': len(self.agent.sessions),
                'timestamp': datetime.utcnow().isoformat()
            }, 200)
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def do_POST(self):
        """Handle POST requests"""
        # Verify bearer token
        if not self._verify_bearer_token():
            self._send_json({'error': 'Unauthorized'}, 401)
            return

        if self.path == '/execute':
            self._handle_execute()
        else:
            self._send_json({'error': 'Not Found'}, 404)

    def _handle_execute(self):
        """Handle command execution"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            cmd = json.loads(body)

            result = self.agent.execute_command(cmd)
            self._send_json(result, 200)

        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in execute: {e}")
            self._send_json({'error': str(e)}, 500)

    def _verify_bearer_token(self) -> bool:
        """Verify bearer token"""
        auth = self.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return False
        token = auth[7:]
        return token == self.bearer_token

    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Custom logging"""
        logger.info(f"{self.address_string()} - {format % args}")


# ============================================================================
# STARTUP
# ============================================================================

def run_agent(config_path: str = 'config.json', host: str = '0.0.0.0', port: int = 12350):
    """Start browser agent server"""

    # Initialize agent
    agent = BrowserAgent(config_path)

    # Set class variables for handler
    BrowserAgentHandler.agent = agent
    BrowserAgentHandler.bearer_token = agent.bearer_token

    # Create and start server
    server = socketserver.TCPServer((host, port), BrowserAgentHandler)
    server.allow_reuse_address = True

    logger.info(f"🚀 Starting {agent.agent_name} on {host}:{port}")
    logger.info(f"🔐 Bearer token: {agent.bearer_token[:20]}...")
    logger.info("📡 Listening for commands from opena2...")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down...")
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.json'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 12350

    run_agent(config_path, '0.0.0.0', port)
