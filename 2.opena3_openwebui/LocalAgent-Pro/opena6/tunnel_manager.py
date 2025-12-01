#!/usr/bin/env python3
"""
External Server Access Manager

Mache lokale Server (Port 8765, 12349, 12350, 3000) öffentlich zugänglich
über 3 Methoden:
1. Firewall/Router (für LAN)
2. ngrok Tunneling (für Internet)
3. SSH Tunneling (für sichere Remote-Verbindungen)

Anwendungsfälle:
- Browser Agent Tool Server (8765) über Internet/LAN zugänglich
- OpenWebUI von anderen Geräten erreichbar
- Remote-Entwicklung mit VS Code
- Testing auf mobilen Geräten
"""

from __future__ import annotations

import subprocess
import json
import time
import sys
import platform
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


# ==================== Type Aliases ====================

TunnelDict = Dict[str, Any]
TunnelRegistry = Dict[str, TunnelDict]


# ==================== Data Models ====================

@dataclass
class TunnelInfo:
    """Tunnel-Informationen mit sauberer Typisierung"""
    name: str
    port: int
    url: Optional[str]
    process: Optional[subprocess.Popen]  # type: ignore
    status: str
    created_at: datetime


# ==================== ngrok Tunneling ====================

class NgrokTunnel:
    """Verwalte ngrok Tunnels für lokale Server"""

    def __init__(self, ngrok_path: str = "/usr/local/bin/ngrok") -> None:
        self.ngrok_path = ngrok_path
        self.tunnels: TunnelRegistry = {}

    def is_installed(self) -> bool:
        """Überprüfe, ob ngrok installiert ist"""
        result = subprocess.run(
            ["which", "ngrok"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def install_ngrok(self) -> bool:
        """Installiere ngrok"""
        import platform
        os_type = platform.system()

        if os_type == "Darwin":  # macOS
            cmd = "brew install ngrok"
        elif os_type == "Linux":
            cmd = (
                "curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | "
                "sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && "
                "echo 'deb https://ngrok-ag                   ent.s3.amazonaws.com buster main' | "
                "sudo tee /etc/apt/sources.list.d/ngrok.list && "
                "sudo apt update && sudo apt install ngrok"
            )
        else:
            print("❌ Unsupported OS. Download from: https://ngrok.com/download")
            return False

        print(f"Installiere ngrok: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0

    def authenticate(self, token: str) -> bool:
        """Authentifiziere ngrok mit Auth Token"""
        result = subprocess.run(
            ["ngrok", "config", "add-authtoken", token],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    def start_tunnel(
        self,
        port: int,
        name: Optional[str] = None,
        protocol: str = "http"
    ) -> Optional[TunnelDict]:
        """Starte einen ngrok Tunnel"""
        if not self.is_installed():
            print("❌ ngrok nicht installiert!")
            print("Installiere mit: brew install ngrok (Mac) oder apt install ngrok (Linux)")
            return None

        tunnel_name = name or f"tunnel_{port}"
        cmd = ["ngrok", protocol, str(port), "--log", "stdout"]

        if name:
            cmd.extend(["--authtoken", name])

        print(f"🌐 Starte ngrok Tunnel für Port {port}...")

        try:
            # Starte ngrok im Background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Warte auf Tunnel-URL
            time.sleep(2)

            # Hole ngrok Status
            status = self.get_tunnel_status()
            if status and status.get("tunnels"):
                tunnel = status["tunnels"][0]
                public_url = tunnel.get("public_url")
                print(f"✅ Tunnel aktiv: {public_url}")

                self.tunnels[tunnel_name] = {
                    "port": port,
                    "url": public_url,
                    "process": process,
                    "status": "active"
                }
                return {
                    "name": tunnel_name,
                    "port": port,
                    "url": public_url,
                    "status": "running"
                }
        except Exception as ex:
            print(f"❌ Fehler beim Starten des Tunnels: {ex}")

        return None

    def get_tunnel_status(self) -> Optional[Dict[str, Any]]:
        """Hole aktuelle Tunnel-Status"""
        try:
            result = subprocess.run(
                ["curl", "-s", "http://127.0.0.1:4040/api/tunnels"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return None

    def stop_tunnel(self, name: str) -> bool:
        """Stoppe einen Tunnel"""
        if name in self.tunnels:
            tunnel = self.tunnels[name]
            process = tunnel.get("process")
            if process:
                process.terminate()
                tunnel["status"] = "stopped"
                return True
        return False

    def list_tunnels(self) -> Dict[str, Any]:
        """Zeige alle aktiven Tunnels"""
        return self.tunnels


# ==================== SSH Tunneling ====================

class SSHTunnel:
    """Verwalte SSH Tunnels für lokale Server"""

    @staticmethod
    def create_tunnel(
        remote_host: str,
        remote_user: str,
        local_port: int,
        remote_port: int = None,
        ssh_key: Optional[str] = None
    ) -> bool:
        """Erstelle SSH Tunnel (lokaler Port ← remote_host:remote_port)"""
        remote_port = remote_port or local_port

        cmd = [
            "ssh",
            "-L", f"{local_port}:localhost:{remote_port}",
            f"{remote_user}@{remote_host}",
            "-N"  # Keine Shell
        ]

        if ssh_key:
            cmd.extend(["-i", ssh_key])

        print(f"🔐 Starte SSH Tunnel: localhost:{local_port} ← {remote_host}:{remote_port}")

        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✅ SSH Tunnel aktiv: http://localhost:{local_port}")
            return True
        except Exception as ex:
            print(f"❌ Fehler: {ex}")
            return False

    @staticmethod
    def create_reverse_tunnel(
        remote_host: str,
        remote_user: str,
        remote_port: int,
        local_port: int,
        ssh_key: Optional[str] = None
    ) -> bool:
        """Erstelle Reverse SSH Tunnel (remote_host:remote_port ← lokaler Port)"""
        cmd = [
            "ssh",
            "-R", f"{remote_port}:localhost:{local_port}",
            f"{remote_user}@{remote_host}",
            "-N"
        ]

        if ssh_key:
            cmd.extend(["-i", ssh_key])

        print(f"🔄 Starte Reverse SSH Tunnel: {remote_host}:{remote_port} ← localhost:{local_port}")

        try:
            subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✅ Reverse Tunnel aktiv")
            return True
        except Exception as ex:
            print(f"❌ Fehler: {ex}")
            return False


# ==================== LocalTunnel ====================

class LocalTunnel:
    """Verwende localtunnel für Tunneling (Alternative zu ngrok)"""

    @staticmethod
    def is_installed() -> bool:
        """Überprüfe, ob lt CLI installiert ist"""
        result = subprocess.run(
            ["which", "lt"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    @staticmethod
    def install() -> bool:
        """Installiere localtunnel"""
        result = subprocess.run(
            ["npm", "install", "-g", "localtunnel"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0

    @staticmethod
    def start_tunnel(port: int, subdomain: Optional[str] = None) -> Optional[str]:
        """Starte localtunnel"""
        if not LocalTunnel.is_installed():
            print("❌ localtunnel nicht installiert!")
            print("Installiere mit: npm install -g localtunnel")
            return None

        cmd = ["lt", "--port", str(port)]
        if subdomain:
            cmd.extend(["--subdomain", subdomain])

        print(f"🌐 Starte localtunnel für Port {port}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            # Extrahiere URL aus Output
            for line in result.stdout.split("\n"):
                if "https://" in line:
                    url = line.strip()
                    print(f"✅ Tunnel aktiv: {url}")
                    return url
        except Exception as ex:
            print(f"❌ Fehler: {ex}")

        return None


# ==================== VS Code Server Configuration ====================

class VSCodeServerConfig:
    """Konfiguriere lokale Server für VS Code"""

    @staticmethod
    def get_launch_config() -> Dict[str, Any]:
        """Generiere VS Code launch.json für Debugging"""
        return {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Tool Server (Port 8765)",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/LocalAgent-Pro/opena6/tool_server.py",
                    "console": "integratedTerminal",
                    "args": ["--host", "0.0.0.0", "--port", "8765"],
                    "env": {
                        "PYTHONUNBUFFERED": "1",
                        "DEBUG": "1"
                    }
                },
                {
                    "name": "Browser Agent (Port 12350)",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/LocalAgent-Pro/opena6/main.py",
                    "console": "integratedTerminal",
                    "env": {
                        "PORT": "12350",
                        "DEBUG": "1"
                    }
                },
                {
                    "name": "Compute Agent (Port 12349)",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/LocalAgent-Pro/opena5/main.py",
                    "console": "integratedTerminal"
                }
            ]
        }

    @staticmethod
    def get_tasks_config() -> Dict[str, Any]:
        """Generiere VS Code tasks.json für Server Management"""
        return {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "🌐 Start All Servers (Tunnel Ready)",
                    "type": "shell",
                    "command": "python3",
                    "args": ["setup_tunnels.py"],
                    "isBackground": True,
                    "problemMatcher": []
                },
                {
                    "label": "🌐 Start ngrok Tunnel (8765)",
                    "type": "shell",
                    "command": "ngrok",
                    "args": ["http", "8765"],
                    "isBackground": True,
                    "problemMatcher": []
                },
                {
                    "label": "🌐 Start localtunnel (8765)",
                    "type": "shell",
                    "command": "lt",
                    "args": ["--port", "8765", "--subdomain", "browser-agent"],
                    "isBackground": True,
                    "problemMatcher": []
                },
                {
                    "label": "🔐 SSH Tunnel to Remote",
                    "type": "shell",
                    "command": "ssh",
                    "args": ["-L", "8765:localhost:8765", "user@remote.host", "-N"],
                    "isBackground": True,
                    "problemMatcher": []
                }
            ]
        }


# ==================== Setup Scripts ====================

def generate_setup_script() -> str:
    """Generiere Python Setup-Skript für Tunnel-Verwaltung"""
    return '''#!/usr/bin/env python3
"""
Setup-Skript: Starte alle Server mit ngrok Tunneling
"""

import asyncio
import subprocess
import time
from pathlib import Path

SERVERS = {
    "Tool Server": {
        "port": 8765,
        "cmd": "python3 LocalAgent-Pro/opena6/tool_server.py --host 0.0.0.0 --port 8765"
    },
    "Browser Agent": {
        "port": 12350,
        "cmd": "python3 LocalAgent-Pro/opena6/main.py"
    },
    "Compute Agent": {
        "port": 12349,
        "cmd": "python3 LocalAgent-Pro/opena5/main.py"
    }
}

def start_server(name: str, cmd: str):
    """Starte einen Server"""
    print(f"🚀 Starte {name}...")
    subprocess.Popen(cmd, shell=True)
    print(f"✅ {name} gestartet")

def start_tunnel(port: int, name: str):
    """Starte ngrok Tunnel"""
    print(f"🌐 Starte ngrok Tunnel für Port {port}...")
    cmd = f"ngrok http {port} --log stdout"
    subprocess.Popen(cmd, shell=True)
    print(f"✅ Tunnel für {name} aktiviert")

async def main():
    print("🔧 Starte All-In-One Setup...\n")

    # Starte alle Server
    for name, config in SERVERS.items():
        start_server(name, config["cmd"])
        time.sleep(1)

    print("\\n⏳ Warte auf Server-Start...")
    time.sleep(3)

    # Starte Tunnels
    print("\\n🌐 Starte Tunnels...\n")
    for name, config in SERVERS.items():
        start_tunnel(config["port"], name)
        time.sleep(1)

    print("\\n✅ Alle Server & Tunnels aktiv!")
    print("\\nZugängliche Ports:")
    for name, config in SERVERS.items():
        print(f"  - {name}: localhost:{config['port']}")

    print("\\nNgrok Web Interface: http://127.0.0.1:4040")
    print("\\nDrücke Ctrl+C zum Beenden...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\n⏹️  Fahre herunter...")

if __name__ == "__main__":
    asyncio.run(main())
'''


# ==================== Usage Examples ====================

def print_usage_examples():
    """Zeige Verwendungsbeispiele"""
    print("""
=== VS Code Server Tunneling - Verwendungsbeispiele ===

1️⃣  NGROK - Schnellste Methode

   a) Installiere ngrok:
      brew install ngrok  # Mac
      apt install ngrok   # Linux

   b) Authentifiziere:
      ngrok config add-authtoken YOUR_TOKEN
      # Token von: https://dashboard.ngrok.com/auth

   c) Starte Tunnel in VS Code Terminal:
      ngrok http 8765

   d) Nutze die Public URL:
      https://abc123.ngrok.io


2️⃣  LOCALTUNNEL - Einfach & Kostenlos

   a) Installiere:
      npm install -g localtunnel

   b) Starte Tunnel:
      lt --port 8765 --subdomain browser-agent

   c) Nutze die URL:
      https://browser-agent.loca.lt


3️⃣  SSH TUNNELING - Sicher & Zuverlässig

   a) Forward Tunnel (Von Remote zu Lokal):
      ssh -L 8765:localhost:8765 user@remote.host -N

   b) Reverse Tunnel (Lokal zu Remote):
      ssh -R 8080:localhost:8765 user@remote.host -N

   c) Mit SSH Key:
      ssh -i ~/.ssh/id_rsa -L 8765:localhost:8765 user@remote.host -N


4️⃣  VS CODE KONFIGURATION

   a) Öffne .vscode/tasks.json

   b) Füge hinzu:
      {
        "label": "🌐 Start ngrok",
        "type": "shell",
        "command": "ngrok http 8765",
        "isBackground": true
      }

   c) Starte mit: Ctrl+Shift+P → "Tasks: Run Task"


5️⃣  FIREWALL/ROUTER Konfiguration

   a) Lokale Server auf 0.0.0.0 binden:
      python3 tool_server.py --host 0.0.0.0 --port 8765

   b) Router Port-Forwarding:
      - Öffne Router Admin Panel (192.168.1.1)
      - Port Forwarding: 8765 → Computer-IP:8765
      - Save & Restart

   c) Zugriff:
      http://YOUR_PUBLIC_IP:8765


6️⃣  UMGEBUNGSVARIABLEN

   Setze in .env oder Export:
      export NGROK_AUTHTOKEN=your_token
      export TUNNEL_PORT=8765
      export SERVER_URL=https://your-tunnel.ngrok.io


7️⃣  SECURITY BEST PRACTICES

   ✅ Nutze HTTPS (ngrok, localtunnel)
   ✅ SSH Tunneling für sensitive Daten
   ✅ Rate Limiting aktivieren
   ✅ IP Whitelist konfigurieren
   ✅ VPN für zusätzliche Sicherheit
   ✅ Bearer Token in Environment speichern
   ✅ Logs monitoren auf verdächtige Aktivität


8️⃣  MULTI-PORT TUNNELING

   # Tool Server
   ngrok http 8765

   # Browser Agent (Separate Terminal)
   ngrok http 12350

   # Compute Agent (Separate Terminal)
   ngrok http 12349

   # OpenWebUI
   ngrok http 3000


9️⃣  TESTING von anderem Gerät

   # Mobile Device / Laptop:
   curl https://your-tunnel.ngrok.io/health
   curl https://your-tunnel.ngrok.io/manifest

   # Python Client:
   import requests
   r = requests.get('https://your-tunnel.ngrok.io/health')
   print(r.json())


🔟 MONITORING & DEBUGGING

   # Ngrok Web Dashboard:
   http://127.0.0.1:4040

   # Logs:
   tail -f logs/tunnel.log

   # Netzwerk-Status:
   ss -tlnp | grep 8765

   # Tunnel-Überprüfung:
   curl https://your-tunnel.ngrok.io/health | jq
""")


# ==================== Main ====================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print_usage_examples()
    else:
        cmd = sys.argv[1].lower()

        if cmd == "ngrok":
            tunnel = NgrokTunnel()
            if not tunnel.is_installed():
                tunnel.install_ngrok()
            tunnel.start_tunnel(8765)

        elif cmd == "localtunnel":
            url = LocalTunnel.start_tunnel(8765, subdomain="browser-agent")
            if url:
                print(f"✅ Tunnel: {url}")

        elif cmd == "config":
            config = VSCodeServerConfig()
            print(json.dumps(config.get_launch_config(), indent=2))

        else:
            print_usage_examples()
