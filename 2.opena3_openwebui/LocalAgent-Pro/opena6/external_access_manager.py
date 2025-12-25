#!/usr/bin/env python3
"""
External Server Access Manager

Mache lokale Server öffentlich zugänglich:
1. Firewall/Router Konfiguration (0.0.0.0 Binding für LAN)
2. ngrok Tunneling (für Internet-Zugriff)
3. SSH Tunneling (sichere Remote-Verbindungen)

Verwendung:
    python3 external_access_manager.py --method firewall --port 8765
    python3 external_access_manager.py --method ngrok --port 8765
    python3 external_access_manager.py --method ssh --remote user@host
"""

import argparse
import json
import socket
import subprocess
import time


class NetworkUtils:
    """Netzwerk-Hilfsfunktionen"""

    @staticmethod
    def get_local_ip() -> str:
        """Hole die lokale IP-Adresse"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @staticmethod
    def get_public_ip() -> str | None:
        """Hole die öffentliche IP-Adresse"""
        try:
            result = subprocess.run(["curl", "-s", "https://api.ipify.org"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def check_port_open(host: str, port: int) -> bool:
        """Überprüfe ob Port offen ist"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((host, port))
            s.close()
            return result == 0
        except Exception:
            return False

    @staticmethod
    def get_service_status(port: int) -> bool:
        """Überprüfe ob Service auf Port läuft"""
        return NetworkUtils.check_port_open("127.0.0.1", port)


class FirewallMethod:
    """Firewall/Router Methode für LAN-Zugriff"""

    def __init__(self, port: int = 8765):
        self.port = port
        self.host = "0.0.0.0"
        self.local_ip = NetworkUtils.get_local_ip()

    def verify_binding(self) -> bool:
        """Überprüfe ob Port auf 0.0.0.0 gebunden ist"""
        try:
            result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
            return f":{self.port}" in result.stdout
        except Exception:
            return False

    def show_configuration(self):
        """Zeige Konfigurationsschritte"""
        print(
            f"""
╔════════════════════════════════════════════════════════════╗
║ Firewall/Router Konfiguration für LAN-Zugriff             ║
╚════════════════════════════════════════════════════════════╝

📋 Schritt 1: Server auf 0.0.0.0 starten
   Befehl:
      python3 tool_server.py --host 0.0.0.0 --port {self.port}

✅ Schritt 2: Lokale Verbindung testen
   curl http://127.0.0.1:{self.port}/health
   curl http://{self.local_ip}:{self.port}/health

🔧 Schritt 3: Router Port Forwarding (Optional)
   - Öffne Router Admin: http://192.168.1.1
   - Suche: Port Forwarding oder UPnP
   - Externe Port: {self.port}
   - Interne Host: {self.local_ip}
   - Interne Port: {self.port}
   - Speichern & Router neustarten

🌐 Schritt 4: Von anderen Geräten zugänglich
   Lokales Netzwerk (LAN):
      http://{self.local_ip}:{self.port}

   Über Internet (mit Port Forwarding):
      curl https://YOUR_PUBLIC_IP:{self.port}/health

📱 Schritt 5: Testen von Mobile/Laptop
   iPhone/Android:
      http://{self.local_ip}:{self.port}

   Anderer Computer im Netz:
      curl http://{self.local_ip}:{self.port}/manifest

⚠️  Sicherheit:
   ✅ Nutze innerhalb vertrauenswürdiger Netzwerke
   ✅ Aktiviere Firewall auf dem Host
   ✅ Verwende Bearer Token für API-Zugriffe
   ✅ Für Internet: nutze ngrok oder SSH (sicherer)
"""
        )

    def verify_setup(self) -> bool:
        """Überprüfe ob Setup korrekt ist"""
        print("🔍 Überprüfe Konfiguration...")

        # Check if service is running
        if not NetworkUtils.get_service_status(self.port):
            print(f"❌ Service läuft nicht auf Port {self.port}")
            print(f"   Starten Sie: python3 tool_server.py --host 0.0.0.0 --port {self.port}")
            return False

        print(f"✅ Service läuft auf Port {self.port}")

        # Check if port is bound to 0.0.0.0
        if not self.verify_binding():
            print("❌ Port ist nicht auf 0.0.0.0 gebunden")
            return False

        print("✅ Port ist auf 0.0.0.0 gebunden")

        # Test local access
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://127.0.0.1:{self.port}/health"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print("✅ Lokaler Zugriff funktioniert")
            else:
                print("❌ Lokaler Zugriff fehlgeschlagen")
                return False
        except Exception as e:
            print(f"❌ Fehler beim Test: {e}")
            return False

        return True


class NgrokMethod:
    """ngrok Tunneling für Internet-Zugriff"""

    def __init__(self, port: int = 8765):
        self.port = port
        self.process = None
        self.tunnel_url = None

    def is_installed(self) -> bool:
        """Überprüfe ob ngrok installiert ist"""
        result = subprocess.run(["which", "ngrok"], capture_output=True, text=True)
        return result.returncode == 0

    def install(self) -> bool:
        """Installiere ngrok"""
        import platform

        os_type = platform.system()

        if os_type == "Darwin":  # macOS
            cmd = "brew install ngrok"
        elif os_type == "Linux":
            cmd = (
                "curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | "
                "sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && "
                "echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | "
                "sudo tee /etc/apt/sources.list.d/ngrok.list && "
                "sudo apt update && sudo apt install -y ngrok"
            )
        else:
            print("❌ Unsupported OS. Download von: https://ngrok.com/download")
            return False

        print("📦 Installiere ngrok...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0

    def authenticate(self, token: str) -> bool:
        """Authentifiziere ngrok"""
        result = subprocess.run(["ngrok", "config", "add-authtoken", token], capture_output=True, text=True)
        success = result.returncode == 0
        if success:
            print("✅ ngrok authentifiziert")
        else:
            print(f"❌ Authentifizierung fehlgeschlagen: {result.stderr}")
        return success

    def start_tunnel(self) -> str | None:
        """Starte ngrok Tunnel"""
        if not self.is_installed():
            print("❌ ngrok nicht installiert!")
            if not self.install():
                print("❌ Installation fehlgeschlagen")
                return None
            print("✅ ngrok installiert")

        print(f"🌐 Starte ngrok Tunnel für Port {self.port}...")

        cmd = ["ngrok", "http", str(self.port), "--log", "stdout"]

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            # Warte auf Tunnel-URL
            print("⏳ Warte auf Tunnel URL...")
            time.sleep(3)

            # Hole ngrok Status
            try:
                result = subprocess.run(
                    ["curl", "-s", "http://127.0.0.1:4040/api/tunnels"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if data.get("tunnels"):
                        tunnel = data["tunnels"][0]
                        self.tunnel_url = tunnel.get("public_url")
                        print(f"✅ Tunnel aktiv: {self.tunnel_url}")
                        return self.tunnel_url
            except Exception as e:
                print(f"⚠️  Konnte Tunnel URL nicht auslesen: {e}")

        except Exception as e:
            print(f"❌ Fehler beim Starten: {e}")

        return None

    def stop_tunnel(self) -> bool:
        """Stoppe ngrok Tunnel"""
        if self.process:
            self.process.terminate()
            return True
        return False

    def show_instructions(self, token: str = None):
        """Zeige ngrok Anweisungen"""
        print(
            f"""
╔════════════════════════════════════════════════════════════╗
║ ngrok Tunneling für Internet-Zugriff                       ║
╚════════════════════════════════════════════════════════════╝

📋 Schritt 1: ngrok Account erstellen (kostenlos)
   https://dashboard.ngrok.com/signup

📋 Schritt 2: Auth Token abrufen
   https://dashboard.ngrok.com/auth/your-authtoken

🔑 Schritt 3: Token konfigurieren
   ngrok config add-authtoken YOUR_TOKEN_HERE

   Oder direkt:
   python3 external_access_manager.py --method ngrok --auth YOUR_TOKEN

🚀 Schritt 4: Tunnel starten
   python3 external_access_manager.py --method ngrok --port {self.port}

✅ Schritt 5: Public URL verwenden
   https://your-tunnel.ngrok.io/health
   https://your-tunnel.ngrok.io/manifest

📊 Schritt 6: ngrok Dashboard überwachen
   http://127.0.0.1:4040

💡 Tipps:
   • Die URL ändert sich bei jedem Neustart (kostenlos)
   • Mit ngrok Pro: Feste URLs
   • Nutze reserved domains für konsistente URLs
   • Rate limiting ist aktiviert

🔄 Multi-Port Tunneling (mehrere Terminal-Fenster):
   Terminal 1: ngrok http 8765  # Tool Server
   Terminal 2: ngrok http 12350 # Browser Agent
   Terminal 3: ngrok http 12349 # Compute Agent
"""
        )


class SSHTunnelMethod:
    """SSH Tunneling für sichere Remote-Verbindungen"""

    @staticmethod
    def create_forward_tunnel(
        remote_host: str, remote_user: str, local_port: int, remote_port: int = None, ssh_key: str | None = None
    ) -> bool:
        """Erstelle SSH Forward Tunnel"""
        remote_port = remote_port or local_port

        cmd = ["ssh", "-L", f"{local_port}:localhost:{remote_port}", f"{remote_user}@{remote_host}", "-N", "-v"]

        if ssh_key:
            cmd.extend(["-i", ssh_key])

        print(f"🔐 SSH Forward Tunnel: localhost:{local_port} ← {remote_host}:{remote_port}")
        print(f"   Befehl: {' '.join(cmd)}")

        try:
            subprocess.Popen(cmd)
            print("✅ Tunnel aktiv!")
            return True
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    @staticmethod
    def create_reverse_tunnel(
        remote_host: str, remote_user: str, remote_port: int, local_port: int, ssh_key: str | None = None
    ) -> bool:
        """Erstelle SSH Reverse Tunnel"""
        cmd = ["ssh", "-R", f"{remote_port}:localhost:{local_port}", f"{remote_user}@{remote_host}", "-N", "-v"]

        if ssh_key:
            cmd.extend(["-i", ssh_key])

        print(f"🔄 SSH Reverse Tunnel: {remote_host}:{remote_port} ← localhost:{local_port}")
        print(f"   Befehl: {' '.join(cmd)}")

        try:
            subprocess.Popen(cmd)
            print("✅ Reverse Tunnel aktiv!")
            return True
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    @staticmethod
    def show_instructions():
        """Zeige SSH Tunnel Anweisungen"""
        print(
            """
╔════════════════════════════════════════════════════════════╗
║ SSH Tunneling für sichere Remote-Verbindungen             ║
╚════════════════════════════════════════════════════════════╝

🔐 Typ 1: SSH Forward Tunnel
   Lokal → Remote Server
   Anwendung: Von Remote-Server zum lokalen Service

   Befehl:
      ssh -L 8765:localhost:8765 user@remote.host -N

   Dann von Remote zugreifen:
      curl http://localhost:8765/health

   Oder:
      python3 external_access_manager.py \\
         --method ssh \\
         --ssh-type forward \\
         --remote user@remote.host

🔄 Typ 2: SSH Reverse Tunnel
   Remote → Lokal
   Anwendung: Lokalen Service von außen erreichbar machen

   Befehl:
      ssh -R 8765:localhost:8765 user@remote.host -N

   Dann von außen zugreifen (auf Remote-Server):
      curl http://remote.host:8765/health

   Oder:
      python3 external_access_manager.py \\
         --method ssh \\
         --ssh-type reverse \\
         --remote user@remote.host \\
         --remote-port 8765

🔑 Mit SSH Key authentifizieren:
   python3 external_access_manager.py \\
      --method ssh \\
      --remote user@remote.host \\
      --ssh-key ~/.ssh/id_rsa

📍 Konfiguration im Detail:

   Lokale Ports:
      8765   - Tool Server
      12349  - Compute Agent
      12350  - Browser Agent
      3000   - OpenWebUI

   Beispiel (alle Tunnels):
      # Terminal 1 - Tool Server
      ssh -L 8765:localhost:8765 user@remote.host -N

      # Terminal 2 - Browser Agent
      ssh -L 12350:localhost:12350 user@remote.host -N

      # Terminal 3 - Compute Agent
      ssh -L 12349:localhost:12349 user@remote.host -N

🛡️  Sicherheit:
   ✅ SSH ist verschlüsselt
   ✅ Keine Authentifizierung auf den Services notwendig
   ✅ Port Forwarding nur innerhalb SSH-Tunnel
   ✅ Standard SSH Public Key Auth
   ✅ Kann über Jumphost (Bastion) laufen

⚡ Performance:
   • Forward Tunnel: Lokal gebunden, Remote nutzbar
   • Reverse Tunnel: Remote gebunden, Lokal steuert
   • Verschlüsselung: Minimal Performance-Overhead
   • Latenz: Je nach SSH-Verbindung (+10-50ms)

🔧 Troubleshooting:
   # Port bereits in Benutzung:
   lsof -i :8765
   kill -9 PID

   # SSH Connection verweigert:
   ssh -v user@remote.host  # Verbose für Details

   # Test Tunnel:
   curl http://localhost:8765/health
"""
        )


def main():
    parser = argparse.ArgumentParser(description="External Server Access Manager")
    parser.add_argument("--method", choices=["firewall", "ngrok", "ssh"], default="firewall", help="Zugriffsmethode")
    parser.add_argument("--port", type=int, default=8765, help="Lokaler Port")
    parser.add_argument("--auth", help="ngrok Auth Token")
    parser.add_argument("--remote", help="SSH Remote Host (user@host)")
    parser.add_argument("--remote-port", type=int, help="SSH Remote Port")
    parser.add_argument("--ssh-key", help="SSH Private Key Pfad")
    parser.add_argument("--ssh-type", choices=["forward", "reverse"], default="forward")

    args = parser.parse_args()

    print(
        f"""
╔════════════════════════════════════════════════════════════╗
║ External Server Access Manager                            ║
║ Lokale Server öffentlich zugänglich machen                ║
╚════════════════════════════════════════════════════════════╝

Lokale IP: {NetworkUtils.get_local_ip()}
Methode: {args.method.upper()}
Port: {args.port}
"""
    )

    if args.method == "firewall":
        fw = FirewallMethod(args.port)
        fw.show_configuration()
        if fw.verify_setup():
            print("\n✅ Setup ist korrekt!")
        else:
            print("\n⚠️  Setup hat Probleme - siehe oben")

    elif args.method == "ngrok":
        ngrok = NgrokMethod(args.port)
        ngrok.show_instructions(args.auth)

        if args.auth:
            if ngrok.authenticate(args.auth):
                tunnel_url = ngrok.start_tunnel()
                if tunnel_url:
                    print(f"\n✅ Tunnel aktiv: {tunnel_url}")
                    print("   Drücke Ctrl+C zum Beenden")
                    try:
                        time.sleep(3600)  # 1 Stunde
                    except KeyboardInterrupt:
                        ngrok.stop_tunnel()
                        print("✅ Tunnel beendet")

    elif args.method == "ssh":
        SSHTunnelMethod.show_instructions()

        if args.remote:
            user, host = args.remote.split("@") if "@" in args.remote else ("user", args.remote)

            if args.ssh_type == "forward":
                SSHTunnelMethod.create_forward_tunnel(
                    host, user, args.port, args.remote_port or args.port, args.ssh_key
                )
            else:
                SSHTunnelMethod.create_reverse_tunnel(
                    host, user, args.remote_port or args.port, args.port, args.ssh_key
                )

            print("\n   Drücke Ctrl+C zum Beenden")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("✅ Tunnel beendet")


if __name__ == "__main__":
    main()
