#!/usr/bin/env python3
"""
Voice Command Parser - Convert voice input to executable commands
Production tool for command-based voice control
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os

from src.speech_input import SpeechInput


class VoiceCommandParser:
    """Parse and execute voice commands"""

    def __init__(self, language="de-DE"):
        self.speech = SpeechInput(language=language)
        self.commands = {
            "datei öffnen": self.open_file,
            "datei erstellen": self.create_file,
            "datei löschen": self.delete_file,
            "verzeichnis auflisten": self.list_directory,
            "system-information": self.system_info,
            "beende": self.exit_program,
        }

    def open_file(self, path):
        """Open file with default application"""
        try:
            os.system(f"xdg-open '{path}' 2>/dev/null &")
            print(f"✅ Öffne Datei: {path}")
            return True
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    def create_file(self, path):
        """Create new file"""
        try:
            Path(path).touch()
            print(f"✅ Datei erstellt: {path}")
            return True
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    def delete_file(self, path):
        """Delete file"""
        try:
            if os.path.exists(path):
                os.remove(path)
                print(f"✅ Datei gelöscht: {path}")
                return True
            else:
                print(f"❌ Datei nicht gefunden: {path}")
                return False
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    def list_directory(self, path="."):
        """List directory contents"""
        try:
            items = os.listdir(path)
            print(f"\n📁 Verzeichnis: {path}")
            for item in items[:20]:  # Limit to 20 items
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    print(f"  📂 {item}/")
                else:
                    size = os.path.getsize(full_path)
                    print(f"  📄 {item} ({size} bytes)")
            return True
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    def system_info(self):
        """Show system information"""
        try:
            os.system("uname -a")
            os.system("echo ''; df -h | head -3")
            return True
        except Exception as e:
            print(f"❌ Fehler: {e}")
            return False

    def exit_program(self):
        """Exit program"""
        print("👋 Auf Wiedersehen!")
        sys.exit(0)

    def parse_and_execute(self, text):
        """Parse voice command and execute"""
        text_lower = text.lower()

        for command_phrase, handler in self.commands.items():
            if command_phrase in text_lower:
                # Extract parameter if present
                param = text_lower.replace(command_phrase, "").strip()

                if param:
                    return handler(param)
                else:
                    return handler() if command_phrase != "datei öffnen" else handler(".")

        print(f"❌ Unbekannter Befehl: {text}")
        return False

    def run_interactive(self):
        """Run interactive voice command mode"""
        print("\n" + "=" * 60)
        print("  🎤 Voice Command Parser")
        print("=" * 60)
        print("\nVerfügbare Befehle:")
        print("  • datei öffnen <pfad>")
        print("  • datei erstellen <pfad>")
        print("  • datei löschen <pfad>")
        print("  • verzeichnis auflisten")
        print("  • system-information")
        print("  • beende")
        print("\nSprich einen Befehl...\n")

        while True:
            try:
                command = self.speech.listen_once()
                if command:
                    self.parse_and_execute(command)
                    print()
            except KeyboardInterrupt:
                print("\n👋 Programm beendet")
                break
            except Exception as e:
                print(f"❌ Fehler: {e}")


def main():
    parser = VoiceCommandParser(language="de-DE")
    parser.run_interactive()


if __name__ == "__main__":
    main()
