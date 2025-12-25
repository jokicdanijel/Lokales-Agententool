#!/usr/bin/env python3
"""
PORTIER 3.0 - Scalable Services Generator
Generate opena4-opena19 agents automatically
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


class AgentGenerator:
    def __init__(self, base_dir, start_id=4, end_id=19, base_port=12348):
        self.base_dir = Path(base_dir)
        self.start_id = start_id
        self.end_id = end_id
        self.base_port = base_port
        self.template_dir = self.base_dir / "LocalAgent-Pro" / "opena3"
        self.agents_created = []

    def generate_config(self, agent_id, port):
        """Generate config.json for agent"""
        config_dict = {
            "service_name": f"opena{agent_id}",
            "port": port,
            "host": "127.0.0.1",
            "version": "3.0.0",
            "role": "scalable-agent",
            "program_target": f"opena{agent_id}",
            "bearer_token": f"sk_opena{agent_id}_scalable_v3_prod",
            "coordinator": "http://127.0.0.1:12345",
            "archivator": "http://127.0.0.1:12346",
            "logging": {
                "level": "INFO",
                "file": f"logs/opena{agent_id}.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "health_check": {"interval": 30, "timeout": 5, "enabled": True},
            "safepoint": {"interval": 300, "enabled": True},
            "created": datetime.now().isoformat(),
            "cluster": {"enable_scaling": True, "enable_routing": True, "enable_discovery": True},
        }
        return config_dict

    def generate_main_py(self, agent_id, port):
        """Generate main.py for agent"""
        return f'''#!/usr/bin/env python3
"""
OpenA{agent_id} - Scalable Agent Service
PORTIER 3.0 Agent Cluster Member
"""

import http.server
import socketserver
import json
import os
from datetime import datetime
import threading
import time
import sys

PORT = {port}
SERVICE_NAME = "opena{agent_id}"
VERSION = "3.0.0"

class AgentHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for opena{agent_id}"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self.send_json({{"status": "online", "service": "{SERVICE_NAME}", "version": "{VERSION}", "port": {PORT}}})
        elif self.path == "/info":
            self.send_json({{"name": "{SERVICE_NAME}", "role": "scalable-agent", "cluster_id": {agent_id}}})
        elif self.path == "/status":
            self.send_json({{"status": "active", "uptime": self.get_uptime(), "requests": self.request_count}})
        elif self.path.startswith("/api/"):
            self.handle_api_request()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body) if body else {{}}

            if self.path == "/api/task":
                self.send_json({{"status": "ok", "message": "Task received", "agent": "{SERVICE_NAME}"}})
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            self.send_error(400, str(e))

    def send_json(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def handle_api_request(self):
        """Handle API requests"""
        self.send_json({{"message": "OpenA{agent_id} API", "service": "{SERVICE_NAME}"}})

    def get_uptime(self):
        """Get uptime in seconds"""
        return int(time.time() - self.start_time) if hasattr(self, 'start_time') else 0

    def log_message(self, format, *args):
        """Suppress default logging"""
        return

def main():
    """Start the agent service"""
    print(f"\\n{'='*60}")
    print(f"  {SERVICE_NAME} - Scalable Agent")
    print(f"{'='*60}")
    print(f"✅ Service started on http://127.0.0.1:{{PORT}}")
    print(f"📡 Health endpoint: http://127.0.0.1:{{PORT}}/health")
    print(f"🔧 Info endpoint: http://127.0.0.1:{{PORT}}/info")
    print(f"⏹️  Press CTRL+C to stop")
    print(f"{'='*60}\\n")

    try:
        AgentHandler.start_time = time.time()
        AgentHandler.request_count = 0
        with socketserver.TCPServer(("127.0.0.1", PORT), AgentHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\\n👋 {{SERVICE_NAME}} stopped")
    except OSError as e:
        print(f"❌ Error: {{e}}")
        print(f"   Port {{PORT}} may already be in use")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    def generate_requirements_txt(self):
        """Generate requirements.txt"""
        return """# PORTIER 3.0 - Scalable Agent Requirements
# Minimal dependencies for cluster agents

# Core HTTP
requests>=2.28.0

# Monitoring (Phase 17)
prometheus-client>=0.15.0

# Utilities
python-dotenv>=0.20.0
pydantic>=1.9.0
"""

    def create_agent(self, agent_id, port):
        """Create a new agent directory"""
        agent_dir = self.base_dir / "LocalAgent-Pro" / f"opena{agent_id}"

        try:
            # Create directory
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create config.json
            config = self.generate_config(agent_id, port)
            with open(agent_dir / "config.json", "w") as f:
                json.dump(config, f, indent=2)

            # Create main.py
            main_py_content = self.generate_main_py(agent_id, port)
            with open(agent_dir / "main.py", "w") as f:
                f.write(main_py_content)

            # Make main.py executable
            os.chmod(agent_dir / "main.py", 0o755)

            # Create __init__.py
            with open(agent_dir / "__init__.py", "w") as f:
                f.write(f'"""OpenA{agent_id} - Scalable Agent Service"""\n__version__ = "3.0.0"\n')

            self.agents_created.append((agent_id, port))
            return True

        except Exception as e:
            print(f"❌ Error creating opena{agent_id}: {e}")
            return False

    def generate_all(self):
        """Generate all agents"""
        print(f"\n{'='*70}")
        print("  PORTIER 3.0 - Agent Cluster Generator")
        print(f"{'='*70}\n")

        success_count = 0
        for i in range(self.start_id, self.end_id + 1):
            port = self.base_port + (i - self.start_id)
            agent_name = f"opena{i}"

            print(f"🔧 Generating {agent_name} (Port {port})...", end=" ")
            if self.create_agent(i, port):
                print("✅")
                success_count += 1
            else:
                print("❌")

        return success_count

    def generate_startup_script(self):
        """Generate startup script for all agents"""
        script_path = self.base_dir / "bin" / "start_agents.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)

        commands = []
        for i in range(self.start_id, self.end_id + 1):
            port = self.base_port + (i - self.start_id)
            commands.append(f"python3 LocalAgent-Pro/opena{i}/main.py > LocalAgent-Pro/logs/opena{i}.log 2>&1 &")

        script_content = f"""#!/bin/bash
# PORTIER 3.0 - Start All Scalable Agents (opena4-opena19)

echo "🚀 Starting Agent Cluster (opena4-opena19)..."
echo "=========================================="
echo ""

cd $(dirname "$0")/..

{chr(10).join(commands)}

sleep 2

echo "✅ All agents started!"
echo ""
echo "🔍 Verify with:"
for port in {{{{12348..12364}}}}; do
  curl -s http://127.0.0.1:$port/health > /dev/null && echo "✅ Port $port online" || echo "❌ Port $port offline"
done
"""

        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)

        return script_path

    def generate_docker_compose(self):
        """Generate docker-compose for agents"""
        compose_path = self.base_dir / "docker-compose.agents.yml"

        services = {}
        for i in range(self.start_id, self.end_id + 1):
            port = self.base_port + (i - self.start_id)
            services[f"opena{i}"] = {
                "build": f"./LocalAgent-Pro/opena{i}",
                "ports": [f"{port}:80"],
                "environment": {"SERVICE_NAME": f"opena{i}", "PORT": "80"},
                "restart": "unless-stopped",
                "networks": ["portier-network"],
            }

        compose_data = {"version": "3.8", "services": services, "networks": {"portier-network": {"driver": "bridge"}}}

        with open(compose_path, "w") as f:
            json.dump(compose_data, f, indent=2)

        return compose_path


def main():
    """Main entry point"""
    base_dir = Path(__file__).parent.parent

    parser_args = {"--start": 4, "--end": 19, "--base-port": 12348}

    # Parse arguments
    for arg, default in parser_args.items():
        if arg in sys.argv:
            idx = sys.argv.index(arg)
            if idx + 1 < len(sys.argv):
                value = sys.argv[idx + 1]
                if arg == "--start":
                    parser_args[arg] = int(value)
                elif arg == "--end":
                    parser_args[arg] = int(value)
                elif arg == "--base-port":
                    parser_args[arg] = int(value)

    generator = AgentGenerator(
        base_dir, start_id=parser_args["--start"], end_id=parser_args["--end"], base_port=parser_args["--base-port"]
    )

    # Generate all agents
    success = generator.generate_all()

    # Generate startup script
    startup_script = generator.generate_startup_script()
    print(f"\n📝 Startup script: {startup_script}")

    # Summary
    print(f"\n{'='*70}")
    print(f"  ✅ Generated {success} agents successfully!")
    print("  🚀 Start them with: bash bin/start_agents.sh")
    print("  📊 Check status: curl http://127.0.0.1:12348/health")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
