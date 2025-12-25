#!/usr/bin/env python3
"""
Voice Call System - Make voice calls via command line
Production tool for voice-based communication
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime

from src.speech_input import SpeechInput


class VoiceCallSystem:
    """Manage voice calls and contacts"""

    def __init__(self, contacts_file="contacts.json", language="de-DE"):
        self.speech = SpeechInput(language=language)
        self.contacts_file = Path(contacts_file)
        self.load_contacts()
        self.call_history = []

    def load_contacts(self):
        """Load contacts from file"""
        if self.contacts_file.exists():
            with open(self.contacts_file, encoding="utf-8") as f:
                self.contacts = json.load(f)
        else:
            self.contacts = {}

    def save_contacts(self):
        """Save contacts to file"""
        with open(self.contacts_file, "w", encoding="utf-8") as f:
            json.dump(self.contacts, f, ensure_ascii=False, indent=2)

    def add_contact(self, name, phone, email=None):
        """Add new contact"""
        self.contacts[name] = {"phone": phone, "email": email, "added": datetime.now().isoformat()}
        self.save_contacts()
        print(f"✅ Kontakt hinzugefügt: {name}")

    def list_contacts(self):
        """List all contacts"""
        print("\n📞 Kontakte:")
        print("-" * 40)

        if not self.contacts:
            print("Keine Kontakte vorhanden")
            return

        for name, info in self.contacts.items():
            print(f"👤 {name}")
            print(f"   ☎️  {info['phone']}")
            if info.get("email"):
                print(f"   📧 {info['email']}")

    def dial_contact(self, name):
        """Initiate call to contact"""
        if name in self.contacts:
            contact = self.contacts[name]
            print(f"\n📞 Rufe an: {name}")
            print(f"   Nummer: {contact['phone']}")
            print("   [Simulated call - would use VoIP integration]")

            self.call_history.append(
                {"contact": name, "phone": contact["phone"], "timestamp": datetime.now().isoformat(), "duration": 0}
            )
            print("✅ Anruf beendet")
        else:
            print(f"❌ Kontakt nicht gefunden: {name}")

    def send_sms(self, name, message):
        """Send SMS to contact"""
        if name in self.contacts:
            contact = self.contacts[name]
            print(f"\n💬 SMS an: {name}")
            print(f"   Nummer: {contact['phone']}")
            print(f"   Nachricht: {message}")
            print("[Simulated SMS - would use SMS gateway]")
            print("✅ SMS gesendet")
        else:
            print(f"❌ Kontakt nicht gefunden: {name}")

    def voice_dial(self):
        """Dial using voice command"""
        print("\n🎤 Sagen Sie den Namen des Kontakts:")
        name = self.speech.listen_once()

        if name:
            # Find best match
            for contact_name in self.contacts.keys():
                if name.lower() in contact_name.lower():
                    self.dial_contact(contact_name)
                    return

            print(f"❌ Kontakt nicht gefunden: {name}")
        else:
            print("❌ Keine Sprache erkannt")

    def view_call_history(self):
        """View call history"""
        print("\n📋 Anrufverlauf:")
        print("-" * 40)

        if not self.call_history:
            print("Keine Anrufe vorhanden")
            return

        for i, call in enumerate(self.call_history[-10:], 1):  # Last 10 calls
            timestamp = datetime.fromisoformat(call["timestamp"]).strftime("%Y-%m-%d %H:%M")
            print(f"{i}. {call['contact']} - {timestamp}")

    def run_interactive(self):
        """Run interactive voice call system"""
        print("\n" + "=" * 60)
        print("  📞 Voice Call System")
        print("=" * 60)

        while True:
            print("\n📞 Menü:")
            print("  1. Kontakte anzeigen")
            print("  2. Kontakt hinzufügen")
            print("  3. Anrufen (Menü)")
            print("  4. Sprachanruf")
            print("  5. SMS senden")
            print("  6. Anrufverlauf")
            print("  0. Beenden")

            choice = input("\nWahl: ").strip()

            if choice == "1":
                self.list_contacts()
            elif choice == "2":
                name = input("Name: ")
                phone = input("Telefon: ")
                email = input("E-Mail (optional): ")
                self.add_contact(name, phone, email or None)
            elif choice == "3":
                self.list_contacts()
                name = input("Kontakt: ")
                self.dial_contact(name)
            elif choice == "4":
                self.voice_dial()
            elif choice == "5":
                self.list_contacts()
                name = input("An: ")
                message = input("Nachricht: ")
                self.send_sms(name, message)
            elif choice == "6":
                self.view_call_history()
            elif choice == "0":
                print("👋 Auf Wiedersehen!")
                break


def main():
    system = VoiceCallSystem()
    system.run_interactive()


if __name__ == "__main__":
    main()
