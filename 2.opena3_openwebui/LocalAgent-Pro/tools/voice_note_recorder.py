#!/usr/bin/env python3
"""
Voice Note Recorder - Record and transcribe voice notes
Production tool for voice-to-text note taking
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.speech_input import SpeechInput
import json
from datetime import datetime
import os


class VoiceNoteRecorder:
    """Record and manage voice notes with transcription"""
    
    def __init__(self, notes_dir="voice_notes", language="de-DE"):
        self.speech = SpeechInput(language=language)
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(exist_ok=True)
        self.notes_file = self.notes_dir / "notes.json"
        self.load_notes()
    
    def load_notes(self):
        """Load existing notes from JSON"""
        if self.notes_file.exists():
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
        else:
            self.notes = []
    
    def save_notes(self):
        """Save notes to JSON"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
    
    def record_note(self, title=None):
        """Record a new voice note"""
        print("\n🎤 Notiz aufnehmen")
        print("-" * 40)
        
        if not title:
            title = input("Titel der Notiz: ").strip()
            if not title:
                title = f"Notiz {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        print("Sprechen Sie jetzt die Notiz auf...")
        text = self.speech.listen_once()
        
        if text:
            note = {
                "id": len(self.notes) + 1,
                "title": title,
                "content": text,
                "timestamp": datetime.now().isoformat(),
                "language": self.speech.language
            }
            self.notes.append(note)
            self.save_notes()
            print(f"✅ Notiz gespeichert: {title}")
            return note
        else:
            print("❌ Keine Sprache erkannt")
            return None
    
    def list_notes(self):
        """List all notes"""
        print("\n📋 Gespeicherte Notizen")
        print("-" * 40)
        
        if not self.notes:
            print("Keine Notizen vorhanden")
            return
        
        for note in self.notes:
            timestamp = datetime.fromisoformat(note['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n{note['id']}. {note['title']}")
            print(f"   📅 {timestamp}")
            print(f"   📝 {note['content'][:50]}...")
    
    def view_note(self, note_id):
        """View full note content"""
        for note in self.notes:
            if note['id'] == note_id:
                print(f"\n📖 {note['title']}")
                print(f"📅 {note['timestamp']}")
                print(f"📝 {note['content']}")
                return note
        
        print(f"❌ Notiz #{note_id} nicht gefunden")
        return None
    
    def delete_note(self, note_id):
        """Delete a note"""
        self.notes = [n for n in self.notes if n['id'] != note_id]
        self.save_notes()
        print(f"✅ Notiz gelöscht")
    
    def search_notes(self, keyword):
        """Search notes by keyword"""
        print(f"\n🔍 Suche nach: '{keyword}'")
        print("-" * 40)
        
        results = [n for n in self.notes if keyword.lower() in n['content'].lower()]
        
        if results:
            for note in results:
                print(f"✓ {note['title']}: {note['content'][:50]}...")
        else:
            print("Keine Ergebnisse gefunden")
        
        return results
    
    def export_notes(self, format="txt"):
        """Export notes to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == "txt":
            filename = self.notes_dir / f"notizen_export_{timestamp}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                for note in self.notes:
                    f.write(f"{'='*60}\n")
                    f.write(f"Titel: {note['title']}\n")
                    f.write(f"Datum: {note['timestamp']}\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"{note['content']}\n\n")
        
        elif format == "json":
            filename = self.notes_dir / f"notizen_export_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Exportiert zu: {filename}")
        return filename
    
    def run_interactive(self):
        """Run interactive voice note recorder"""
        print("\n" + "=" * 60)
        print("  🎤 Voice Note Recorder")
        print("=" * 60)
        
        while True:
            print("\n📋 Menü:")
            print("  1. Neue Notiz aufnehmen")
            print("  2. Notizen auflisten")
            print("  3. Notiz anzeigen")
            print("  4. Notiz löschen")
            print("  5. Notizen durchsuchen")
            print("  6. Notizen exportieren")
            print("  0. Beenden")
            
            choice = input("\nWahl: ").strip()
            
            if choice == "1":
                self.record_note()
            elif choice == "2":
                self.list_notes()
            elif choice == "3":
                self.list_notes()
                note_id = int(input("Notiz-ID: "))
                self.view_note(note_id)
            elif choice == "4":
                self.list_notes()
                note_id = int(input("Notiz-ID löschen: "))
                self.delete_note(note_id)
            elif choice == "5":
                keyword = input("Suchbegriff: ")
                self.search_notes(keyword)
            elif choice == "6":
                fmt = input("Format (txt/json) [txt]: ") or "txt"
                self.export_notes(fmt)
            elif choice == "0":
                print("👋 Auf Wiedersehen!")
                break


def main():
    recorder = VoiceNoteRecorder()
    recorder.run_interactive()


if __name__ == "__main__":
    main()
