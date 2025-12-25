#!/usr/bin/env python3
"""
Voice Assistant - AI-powered voice command assistant
Production tool for intelligent voice control
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from datetime import datetime

from src.speech_input import SpeechInput


class VoiceAssistant:
    """Intelligent voice assistant with command routing"""

    def __init__(self, language="de-DE"):
        self.speech = SpeechInput(language=language)
        self.language = language
        self.session_start = datetime.now()
        self.conversation_log = []

    def process_command(self, text):
        """Process voice command intelligently"""
        text_lower = text.lower()

        # Time commands
        if "uhrzeit" in text_lower or "zeit" in text_lower:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"⏰ Die aktuelle Zeit ist: {now}")
            return

        if "datum" in text_lower:
            date = datetime.now().strftime("%d. %B %Y")
            print(f"📅 Heute ist: {date}")
            return

        # System commands
        if "wetter" in text_lower:
            print("🌤️  Wetterinformation: [Würde echte Wetter-API nutzen]")
            return

        if "rechnen" in text_lower or "berechne" in text_lower:
            # Extract math expression
            try:
                expr = text_lower.replace("rechnen", "").replace("berechne", "").strip()
                result = eval(expr)
                print(f"🧮 Ergebnis: {result}")
            except:
                print("❌ Konnte Ausdruck nicht berechnen")
            return

        # Information commands
        if "speicher" in text_lower or "ram" in text_lower:
            os.system("free -h | grep Mem")
            return

        if "festplatte" in text_lower or "disk" in text_lower:
            os.system("df -h | grep -E '^/dev'")
            return

        if "prozesse" in text_lower:
            os.system("ps aux | head -5")
            return

        # Default
        print(f"🤔 Befehl nicht verstanden: {text}")

    def save_conversation(self, filename=None):
        """Save conversation log"""
        if not filename:
            filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("Sprachassistent Sitzung\n")
            f.write(f"Start: {self.session_start}\n")
            f.write(f"Sprache: {self.language}\n")
            f.write("=" * 50 + "\n\n")

            for entry in self.conversation_log:
                f.write(f"[{entry['time']}] {entry['role']}: {entry['text']}\n")

        print(f"✅ Sitzung gespeichert: {filename}")

    def run_interactive(self):
        """Run interactive voice assistant"""
        print("\n" + "=" * 60)
        print("  🤖 Voice Assistant")
        print("=" * 60)
        print("\nVerfügbare Befehle:")
        print("  • Uhrzeit / Datum")
        print("  • Wetter")
        print("  • Rechnen / Berechne")
        print("  • Speicher / RAM / Festplatte")
        print("  • Prozesse")
        print("  • Beenden / Quit")
        print("\nSprich einen Befehl...\n")

        while True:
            try:
                print("🎤 Zuhören...")
                command = self.speech.listen_once()

                if command:
                    print(f"👤 Sie: {command}")
                    self.conversation_log.append({"time": datetime.now().isoformat(), "role": "User", "text": command})

                    if "beenden" in command.lower() or "quit" in command.lower():
                        print("👋 Auf Wiedersehen!")
                        self.save_conversation()
                        break

                    self.process_command(command)
                    print()

            except KeyboardInterrupt:
                print("\n👋 Sitzung beendet")
                self.save_conversation()
                break
            except Exception as e:
                print(f"❌ Fehler: {e}")


def main():
    assistant = VoiceAssistant(language="de-DE")
    assistant.run_interactive()


if __name__ == "__main__":
    main()
