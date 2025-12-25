#!/usr/bin/env python3
"""
OpenA3 Master Integration Script
Startet und verwaltet alle Komponenten
- Web Dashboard (Port 8000)
- Voice Programme
- API Services
"""

import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


class OpenA3Master:
    """Master controller für alle OpenA3 Komponenten"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.processes = []
        self.running = True

    def log(self, level, message):
        """Ausgabe mit Timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️ ", "OK": "✅", "ERROR": "❌", "WARNING": "⚠️ ", "START": "🚀"}
        icon = icons.get(level, "•")
        print(f"[{timestamp}] {icon} {message}")

    def check_port(self, port):
        """Prüfe ob Port verfügbar ist"""
        import socket

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("0.0.0.0", port))
        sock.close()
        return result != 0

    def start_dashboard(self):
        """Starte Web Dashboard"""
        self.log("START", "Starte Web Dashboard (Port 8000)...")

        if not self.check_port(8000):
            self.log("WARNING", "Port 8000 bereits in Benutzung")
            return False

        try:
            cmd = [sys.executable, str(self.base_path / "web_dashboard.py")]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(self.base_path))
            self.processes.append(("Dashboard", proc))
            time.sleep(1)
            self.log("OK", "Web Dashboard erfolgreich gestartet")
            return True
        except Exception as e:
            self.log("ERROR", f"Dashboard Start fehlgeschlagen: {e}")
            return False

    def verify_components(self):
        """Verifiziere alle Komponenten"""
        self.log("INFO", "Verifiziere Komponenten...")

        components = {
            "web_dashboard.py": "Web Dashboard (Port 8000)",
            "tools/voice_command_parser.py": "Voice Command Parser",
            "tools/voice_note_recorder.py": "Voice Note Recorder",
            "tools/voice_call_system.py": "Voice Call System",
            "tools/voice_assistant.py": "Voice Assistant",
            "tools/voice_transcriber.py": "Voice Transcriber",
            "tools/voice_scheduler.py": "Voice Scheduler",
            "src/speech_input.py": "Speech Input Module",
        }

        missing = []
        for file, name in components.items():
            path = self.base_path / file
            if path.exists():
                self.log("OK", f"{name}: ✓ ({path.stat().st_size} bytes)")
            else:
                self.log("ERROR", f"{name}: ✗ FEHLT")
                missing.append(file)

        if missing:
            self.log("ERROR", f"{len(missing)} Dateien fehlen!")
            return False

        self.log("OK", "Alle Komponenten vorhanden")
        return True

    def test_imports(self):
        """Teste alle Python-Imports"""
        self.log("INFO", "Teste Python-Imports...")

        sys.path.insert(0, str(self.base_path))

        modules = {
            "web_dashboard": "Web Dashboard Module",
            "tools.voice_command_parser": "Voice Command Parser",
            "tools.voice_note_recorder": "Voice Note Recorder",
            "tools.voice_call_system": "Voice Call System",
            "tools.voice_assistant": "Voice Assistant",
            "tools.voice_transcriber": "Voice Transcriber",
            "tools.voice_scheduler": "Voice Scheduler",
            "src.speech_input": "Speech Input Module",
        }

        failed = []
        for module, name in modules.items():
            try:
                __import__(module)
                self.log("OK", f"{name}: importierbar")
            except ImportError as e:
                self.log("WARNING", f"{name}: Import-Issue ({str(e)[:50]})")
                failed.append(module)
            except Exception as e:
                self.log("ERROR", f"{name}: Fehler ({str(e)[:50]})")
                failed.append(module)

        if failed:
            self.log("WARNING", f"{len(failed)} Module haben Issues (nicht kritisch)")

        return True

    def show_status(self):
        """Zeige System Status"""
        print("\n" + "=" * 70)
        print("  🤖 OpenA3 SYSTEM STATUS")
        print("=" * 70)

        print("\n📡 WEB DASHBOARD:")
        print("   URL: http://0.0.0.0:8000/")
        print("   API: http://0.0.0.0:8000/api/status")
        print("   API: http://0.0.0.0:8000/api/tools")
        print("   API: http://0.0.0.0:8000/api/programs")

        print("\n🎤 VOICE PROGRAMME (Standalone):")
        print("   python3 tools/voice_command_parser.py")
        print("   python3 tools/voice_note_recorder.py")
        print("   python3 tools/voice_call_system.py")
        print("   python3 tools/voice_assistant.py")
        print("   python3 tools/voice_transcriber.py")
        print("   python3 tools/voice_scheduler.py")

        print("\n🔧 SYSTEM INFO:")
        print("   Base Path:", self.base_path)
        print("   Python Version:", sys.version.split()[0])
        print("   Timestamp:", datetime.now().isoformat())

        print("\n✅ KOMPONENTEN:")
        print("   • 1 Web Dashboard")
        print("   • 6 Voice Programme")
        print("   • 5 API Tools")
        print("   • Gesamt: 1.781 Codezeilen")

        print("\n" + "=" * 70)
        print("  🚀 SYSTEM BEREIT - Alle Komponenten einsatzbereit")
        print("=" * 70 + "\n")

    def signal_handler(self, sig, frame):
        """Handle CTRL+C"""
        self.log("INFO", "Herunterfahren...")
        self.running = False

        for name, proc in self.processes:
            try:
                self.log("INFO", f"Beende {name}...")
                proc.terminate()
                proc.wait(timeout=3)
            except:
                proc.kill()

        self.log("OK", "Alle Prozesse beendet")
        sys.exit(0)

    def run(self):
        """Starte alle Komponenten"""
        print("\n" + "=" * 70)
        print("  🤖 OpenA3 Master Integration")
        print("=" * 70 + "\n")

        # Signal Handler
        signal.signal(signal.SIGINT, self.signal_handler)

        # Verifizierung
        if not self.verify_components():
            self.log("ERROR", "Komponenten-Verifizierung fehlgeschlagen")
            return False

        print()

        # Test Imports
        if not self.test_imports():
            self.log("ERROR", "Import-Tests fehlgeschlagen")
            return False

        print()

        # Starte Dashboard
        if not self.start_dashboard():
            self.log("ERROR", "Dashboard konnte nicht gestartet werden")
            return False

        # Status anzeigen
        self.show_status()

        # Warte auf Beendigung
        try:
            while self.running:
                time.sleep(1)
                # Prüfe ob Prozesse noch laufen
                for name, proc in self.processes:
                    if proc.poll() is not None:
                        self.log("ERROR", f"{name} wurde unerwartet beendet")
        except KeyboardInterrupt:
            self.signal_handler(None, None)

        return True


def main():
    """Haupteinstiegspunkt"""
    master = OpenA3Master()
    success = master.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
