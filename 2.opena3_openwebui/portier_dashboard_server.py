"""
🟣 Portier HyperDashboard Server 3.0.0
Standalone Web-Dashboard für die Portier Suite
Integration mit OpenWebUI Tools
Author: LocalAgentPro
License: MIT
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import json
import os
import psutil
import logging
from datetime import datetime
from typing import Dict, List, Any
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
CONFIG = {
    "app_name": "Portier HyperDashboard",
    "version": "3.0.0",
    "port": 5001,
    "openwebui_port": 3000,
    "debug": False
}

# ============================================================================
# DATA MODELS
# ============================================================================

class DashboardData:
    """Zentrale Datenverwaltung"""

    def __init__(self):
        self.data_dir = "/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/OpenWebUI-Portier"
        self.users = []
        self.workflows = []
        self.sessions = []

    def get_system_metrics(self) -> Dict[str, Any]:
        """Hole System-Metriken"""
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "uptime": self._get_uptime()
        }

    def _get_uptime(self) -> str:
        """Berechne Uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = int(float(f.readline().split()[0]))
                days = uptime_seconds // 86400
                hours = (uptime_seconds % 86400) // 3600
                minutes = (uptime_seconds % 3600) // 60
                return f"{days}d {hours}h {minutes}m"
        except:
            return "N/A"

    def get_portier_status(self) -> Dict[str, Any]:
        """Hole Status aller Portier Module"""
        modules = [
            "portier_hyperdashboard_3_0_0.py",
            "portier_dashboard_user_1_0_0.py",
            "portier_workflow_builder_1_0_0.py",
            "portier_monitoring_engine_1_0_0.py",
            "portier_browseragent_recorder_1_0_0.py",
            "portier_pdf_viewer_1_0_0.py",
        ]

        status = {}
        modules_dir = f"{self.data_dir}/open-webui/extensions/functions"

        for module in modules:
            path = f"{modules_dir}/{module}"
            module_name = module.replace("_", " ").replace(".py", "").title()
            status[module_name] = {
                "installed": os.path.exists(path),
                "size": os.path.getsize(path) if os.path.exists(path) else 0,
                "path": path
            }

        return status

    def get_openwebui_status(self) -> Dict[str, Any]:
        """Prüfe OpenWebUI Status"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', CONFIG["openwebui_port"]))
            sock.close()
            return {
                "status": "online" if result == 0 else "offline",
                "port": CONFIG["openwebui_port"],
                "url": f"http://localhost:{CONFIG['openwebui_port']}"
            }
        except:
            return {
                "status": "error",
                "port": CONFIG["openwebui_port"],
                "url": f"http://localhost:{CONFIG['openwebui_port']}"
            }

dashboard_data = DashboardData()

# ============================================================================
# ROUTES - API
# ============================================================================

@app.route('/api/status', methods=['GET'])
def api_status():
    """Dashboard API Status"""
    return jsonify({
        "status": "online",
        "version": CONFIG["version"],
        "timestamp": datetime.now().isoformat(),
        "dashboard": "HyperDashboard 3.0.0"
    })

@app.route('/api/metrics', methods=['GET'])
def api_metrics():
    """System Metriken"""
    metrics = dashboard_data.get_system_metrics()
    return jsonify({
        "status": "success",
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/portier/status', methods=['GET'])
def api_portier_status():
    """Portier Module Status"""
    status = dashboard_data.get_portier_status()
    return jsonify({
        "status": "success",
        "modules": status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/openwebui/status', methods=['GET'])
def api_openwebui_status():
    """OpenWebUI Status"""
    status = dashboard_data.get_openwebui_status()
    return jsonify({
        "status": "success",
        "openwebui": status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health Check - vollständig"""
    portier_status = dashboard_data.get_portier_status()
    openwebui_status = dashboard_data.get_openwebui_status()
    metrics = dashboard_data.get_system_metrics()

    # Zähle Module
    installed = sum(1 for m in portier_status.values() if m['installed'])
    total = len(portier_status)

    return jsonify({
        "status": "healthy",
        "dashboard": "online",
        "portier_modules": f"{installed}/{total}",
        "openwebui": openwebui_status["status"],
        "system": {
            "cpu": metrics["cpu"],
            "memory": metrics["memory"],
            "disk": metrics["disk"],
            "uptime": metrics["uptime"]
        },
        "timestamp": datetime.now().isoformat()
    })

# ============================================================================
# ROUTES - HTML/UI
# ============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portier HyperDashboard 3.0.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #12001a 0%, #1e0030 100%);
            color: #FFFFFF;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #8d3cff;
        }

        h1 {
            font-size: 2.5em;
            color: #c084fc;
            margin-bottom: 10px;
            text-shadow: 0 0 10px rgba(192, 132, 252, 0.5);
        }

        .version {
            color: #E9D5FF;
            font-size: 0.9em;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: rgba(30, 0, 48, 0.8);
            border: 2px solid #8d3cff;
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 0 20px rgba(141, 60, 255, 0.2);
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(141, 60, 255, 0.4);
            border-color: #c084fc;
        }

        .card h2 {
            color: #c084fc;
            margin-bottom: 15px;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
            margin: 5px 0;
        }

        .status-online {
            background: rgba(144, 238, 144, 0.2);
            color: #90EE90;
            border: 1px solid #90EE90;
        }

        .status-offline {
            background: rgba(255, 69, 0, 0.2);
            color: #FF4500;
            border: 1px solid #FF4500;
        }

        .metric {
            margin: 10px 0;
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .metric-label {
            color: #E9D5FF;
        }

        .metric-value {
            color: #c084fc;
            font-weight: bold;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            margin-top: 5px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #8d3cff, #c084fc);
            transition: width 0.3s ease;
        }

        .module-list {
            list-style: none;
        }

        .module-item {
            padding: 10px;
            margin: 5px 0;
            background: rgba(255, 255, 255, 0.05);
            border-left: 3px solid #8d3cff;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .module-name {
            color: #E9D5FF;
        }

        .module-status {
            font-size: 0.85em;
        }

        .btn {
            background: #8d3cff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            margin: 10px 5px 0 0;
            transition: all 0.3s ease;
        }

        .btn:hover {
            background: #c084fc;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(141, 60, 255, 0.4);
        }

        .btn-secondary {
            background: #4c1d95;
            border: 1px solid #8d3cff;
        }

        .btn-secondary:hover {
            background: #8d3cff;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #8d3cff;
            color: #E9D5FF;
            font-size: 0.9em;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(192, 132, 252, 0.3);
            border-radius: 50%;
            border-top-color: #c084fc;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .alert {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }

        .alert-success {
            background: rgba(144, 238, 144, 0.1);
            border-color: #90EE90;
            color: #90EE90;
        }

        .alert-warning {
            background: rgba(255, 165, 0, 0.1);
            border-color: #FFA500;
            color: #FFA500;
        }

        .alert-error {
            background: rgba(255, 69, 0, 0.1);
            border-color: #FF4500;
            color: #FF4500;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🟣 Portier HyperDashboard</h1>
            <p class="version">Version 3.0.0 | Admin Edition</p>
        </header>

        <div class="grid">
            <!-- System Status Card -->
            <div class="card">
                <h2>📊 System Status</h2>
                <div id="system-metrics">
                    <div class="metric">
                        <span class="metric-label">CPU</span>
                        <span class="metric-value"><span class="loading"></span></span>
                    </div>
                </div>
            </div>

            <!-- Portier Modules Card -->
            <div class="card">
                <h2>🟣 Portier Module</h2>
                <div id="portier-modules">
                    <div class="metric">
                        <span class="metric-label">Loading...</span>
                    </div>
                </div>
            </div>

            <!-- OpenWebUI Status Card -->
            <div class="card">
                <h2>🌐 OpenWebUI Integration</h2>
                <div id="openwebui-status">
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="loading"></span>
                    </div>
                </div>
            </div>

            <!-- Health Check Card -->
            <div class="card">
                <h2>✅ Health Check</h2>
                <div id="health-check">
                    <div class="metric">
                        <span class="metric-label">Overall Status</span>
                        <span class="loading"></span>
                    </div>
                </div>
            </div>

            <!-- Actions Card -->
            <div class="card">
                <h2>⚙️ Aktionen</h2>
                <button class="btn" onclick="location.href='http://localhost:3000'">
                    🌐 OpenWebUI öffnen
                </button>
                <button class="btn btn-secondary" onclick="refreshAll()">
                    🔄 Aktualisieren
                </button>
                <button class="btn btn-secondary" onclick="location.href='/api/health'">
                    📋 API Health
                </button>
            </div>
        </div>

        <div class="footer">
            <p>Portier HyperDashboard 3.0.0 | LocalAgentPro Suite | © 2025</p>
            <p>Last Updated: <span id="last-update">-</span></p>
        </div>
    </div>

    <script>
        async function loadMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                const metrics = data.metrics;

                document.getElementById('system-metrics').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">CPU</span>
                        <span class="metric-value">${metrics.cpu.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width: ${metrics.cpu}%"></div></div>

                    <div class="metric">
                        <span class="metric-label">Memory</span>
                        <span class="metric-value">${metrics.memory.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width: ${metrics.memory}%"></div></div>

                    <div class="metric">
                        <span class="metric-label">Disk</span>
                        <span class="metric-value">${metrics.disk.toFixed(1)}%</span>
                    </div>
                    <div class="progress-bar"><div class="progress-fill" style="width: ${metrics.disk}%"></div></div>

                    <div class="metric">
                        <span class="metric-label">Uptime</span>
                        <span class="metric-value">${metrics.uptime}</span>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading metrics:', error);
            }
        }

        async function loadPortierStatus() {
            try {
                const response = await fetch('/api/portier/status');
                const data = await response.json();
                const modules = data.modules;

                let html = '<ul class="module-list">';
                for (const [name, info] of Object.entries(modules)) {
                    const status = info.installed ? 'installed' : 'missing';
                    const badge = info.installed
                        ? '<span class="status-badge status-online">✅ Installed</span>'
                        : '<span class="status-badge status-offline">❌ Missing</span>';
                    html += `<li class="module-item"><span class="module-name">${name}</span>${badge}</li>`;
                }
                html += '</ul>';
                document.getElementById('portier-modules').innerHTML = html;
            } catch (error) {
                console.error('Error loading portier status:', error);
            }
        }

        async function loadOpenWebUIStatus() {
            try {
                const response = await fetch('/api/openwebui/status');
                const data = await response.json();
                const openwebui = data.openwebui;

                const statusClass = openwebui.status === 'online' ? 'status-online' : 'status-offline';
                const statusIcon = openwebui.status === 'online' ? '✅' : '❌';

                document.getElementById('openwebui-status').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="status-badge ${statusClass}">${statusIcon} ${openwebui.status.toUpperCase()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Port</span>
                        <span class="metric-value">${openwebui.port}</span>
                    </div>
                    <a href="${openwebui.url}" target="_blank" style="text-decoration: none;">
                        <button class="btn">Open OpenWebUI →</button>
                    </a>
                `;
            } catch (error) {
                console.error('Error loading openwebui status:', error);
            }
        }

        async function loadHealthCheck() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                const health = data;

                document.getElementById('health-check').innerHTML = `
                    <div class="metric">
                        <span class="metric-label">Dashboard</span>
                        <span class="status-badge status-online">✅ ${health.dashboard}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Portier Modules</span>
                        <span class="metric-value">${health.portier_modules}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">OpenWebUI</span>
                        <span class="status-badge ${health.openwebui === 'online' ? 'status-online' : 'status-offline'}">
                            ${health.openwebui === 'online' ? '✅' : '❌'} ${health.openwebui.toUpperCase()}
                        </span>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading health check:', error);
            }
        }

        function updateTimestamp() {
            document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
        }

        function refreshAll() {
            loadMetrics();
            loadPortierStatus();
            loadOpenWebUIStatus();
            loadHealthCheck();
            updateTimestamp();
        }

        // Initial load
        refreshAll();

        // Auto-refresh every 10 seconds
        setInterval(refreshAll, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Hauptdashboard"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health():
    """Health Check Seite"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Health Check</title>
        <style>
            body { font-family: monospace; background: #12001a; color: #fff; padding: 20px; }
            pre { background: #1e0030; padding: 15px; border-radius: 8px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Portier Dashboard Health Check</h1>
        <pre id="health-data">Loading...</pre>
        <script>
            fetch('/api/health')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('health-data').textContent = JSON.stringify(data, null, 2);
                });
        </script>
    </body>
    </html>
    """)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print(f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║         🟣 Portier HyperDashboard 3.0.0                       ║
    ║              Standalone Web Server                             ║
    ╚════════════════════════════════════════════════════════════════╝

    📊 Dashboard:    http://localhost:{CONFIG['port']}
    🌐 OpenWebUI:    http://localhost:{CONFIG['openwebui_port']}
    ✅ API Health:   http://localhost:{CONFIG['port']}/api/health
    📋 Health Page:  http://localhost:{CONFIG['port']}/health

    ⏹️  Stoppen: Ctrl+C
    """)

    logger.info(f"🚀 Starting Portier HyperDashboard on port {CONFIG['port']}")
    app.run(host='0.0.0.0', port=CONFIG['port'], debug=CONFIG['debug'])

@app.route('/docs')
def docs():
    """Technische Dokumentation"""
    with open('/home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/2.opena3_openwebui/PORTIER_TECHNICAL_DOCS.html', 'r') as f:
        return f.read()
