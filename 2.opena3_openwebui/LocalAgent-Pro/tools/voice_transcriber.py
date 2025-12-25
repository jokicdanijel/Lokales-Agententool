#!/usr/bin/env python3
"""
Voice Transcriber - Transcribe audio files and live speech
Production tool for speech-to-text transcription
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import os
from datetime import datetime

from src.speech_input import SpeechInput


class VoiceTranscriber:
    """Transcribe audio files and live speech with metadata"""

    def __init__(self, transcripts_dir="transcripts", language="de-DE"):
        self.speech = SpeechInput(language=language)
        self.transcripts_dir = Path(transcripts_dir)
        self.transcripts_dir.mkdir(exist_ok=True)
        self.transcripts = []

    def transcribe_live(self, duration_seconds=None):
        """Transcribe live speech"""
        print("\n🎤 Live Transcription")
        print("-" * 40)
        print("Sprechen Sie jetzt...")

        text = self.speech.listen_once()

        if text:
            transcript = {
                "id": len(self.transcripts) + 1,
                "type": "live",
                "content": text,
                "word_count": len(text.split()),
                "timestamp": datetime.now().isoformat(),
                "language": self.speech.language,
            }
            self.transcripts.append(transcript)
            print(f"✅ Transkribiert: {len(text.split())} Wörter")
            return transcript
        else:
            print("❌ Keine Sprache erkannt")
            return None

    def transcribe_file(self, audio_file):
        """Transcribe audio file"""
        if not os.path.exists(audio_file):
            print(f"❌ Datei nicht gefunden: {audio_file}")
            return None

        print(f"\n📁 Transkribiere: {audio_file}")
        print("-" * 40)

        text = self.speech.recognize_from_file(audio_file)

        if text:
            file_size = os.path.getsize(audio_file)
            transcript = {
                "id": len(self.transcripts) + 1,
                "type": "file",
                "filename": os.path.basename(audio_file),
                "content": text,
                "word_count": len(text.split()),
                "file_size": file_size,
                "timestamp": datetime.now().isoformat(),
                "language": self.speech.language,
            }
            self.transcripts.append(transcript)
            print(f"✅ Transkribiert: {len(text.split())} Wörter")
            return transcript
        else:
            print("❌ Konnte Datei nicht transkribieren")
            return None

    def list_transcripts(self):
        """List all transcripts"""
        print("\n📋 Transkriptionen:")
        print("-" * 40)

        if not self.transcripts:
            print("Keine Transkriptionen vorhanden")
            return

        for t in self.transcripts:
            timestamp = datetime.fromisoformat(t["timestamp"]).strftime("%Y-%m-%d %H:%M")
            print(f"{t['id']}. [{t['type']}] {t.get('filename', 'Live')} ({t['word_count']} Wörter)")
            print(f"   📅 {timestamp}")

    def view_transcript(self, transcript_id):
        """View full transcript"""
        for t in self.transcripts:
            if t["id"] == transcript_id:
                print(f"\n📖 Transkript #{transcript_id}")
                print(f"Typ: {t['type']}")
                print(f"Wörter: {t['word_count']}")
                print(f"Sprache: {t['language']}")
                print("-" * 40)
                print(t["content"])
                return t

        print("❌ Transkript nicht gefunden")
        return None

    def export_transcript(self, transcript_id, format="txt"):
        """Export transcript to file"""
        transcript = None
        for t in self.transcripts:
            if t["id"] == transcript_id:
                transcript = t
                break

        if not transcript:
            print("❌ Transkript nicht gefunden")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "txt":
            filename = self.transcripts_dir / f"transcript_{transcript_id}_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Transkript #{transcript_id}\n")
                f.write(f"Typ: {transcript['type']}\n")
                f.write(f"Wörter: {transcript['word_count']}\n")
                f.write(f"Sprache: {transcript['language']}\n")
                f.write(f"Datum: {transcript['timestamp']}\n")
                f.write("=" * 50 + "\n\n")
                f.write(transcript["content"])

        elif format == "json":
            filename = self.transcripts_dir / f"transcript_{transcript_id}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(transcript, f, ensure_ascii=False, indent=2)

        print(f"✅ Exportiert: {filename}")
        return filename

    def search_transcripts(self, keyword):
        """Search transcripts"""
        print(f"\n🔍 Suche: '{keyword}'")
        print("-" * 40)

        results = [t for t in self.transcripts if keyword.lower() in t["content"].lower()]

        if results:
            for t in results:
                print(f"✓ Transkript #{t['id']}: {t['content'][:50]}...")
        else:
            print("Keine Ergebnisse gefunden")

        return results

    def get_statistics(self):
        """Get transcription statistics"""
        if not self.transcripts:
            print("Keine Daten vorhanden")
            return

        total_words = sum(t["word_count"] for t in self.transcripts)
        avg_words = total_words // len(self.transcripts) if self.transcripts else 0

        print("\n📊 Statistiken:")
        print("-" * 40)
        print(f"Transkriptionen: {len(self.transcripts)}")
        print(f"Gesamt Wörter: {total_words}")
        print(f"Durchschnitt: {avg_words} Wörter pro Transkript")
        print(f"Live: {sum(1 for t in self.transcripts if t['type'] == 'live')}")
        print(f"Dateien: {sum(1 for t in self.transcripts if t['type'] == 'file')}")

    def run_interactive(self):
        """Run interactive transcriber"""
        print("\n" + "=" * 60)
        print("  🎤 Voice Transcriber")
        print("=" * 60)

        while True:
            print("\n📝 Menü:")
            print("  1. Live transkribieren")
            print("  2. Datei transkribieren")
            print("  3. Transkriptionen anzeigen")
            print("  4. Transkript ansehen")
            print("  5. Transkript exportieren")
            print("  6. Durchsuchen")
            print("  7. Statistiken")
            print("  0. Beenden")

            choice = input("\nWahl: ").strip()

            if choice == "1":
                self.transcribe_live()
            elif choice == "2":
                filename = input("Audiodatei: ")
                self.transcribe_file(filename)
            elif choice == "3":
                self.list_transcripts()
            elif choice == "4":
                self.list_transcripts()
                transcript_id = int(input("Transkript-ID: "))
                self.view_transcript(transcript_id)
            elif choice == "5":
                self.list_transcripts()
                transcript_id = int(input("Transkript-ID: "))
                fmt = input("Format (txt/json) [txt]: ") or "txt"
                self.export_transcript(transcript_id, fmt)
            elif choice == "6":
                keyword = input("Suchbegriff: ")
                self.search_transcripts(keyword)
            elif choice == "7":
                self.get_statistics()
            elif choice == "0":
                print("👋 Auf Wiedersehen!")
                break


def main():
    transcriber = VoiceTranscriber()
    transcriber.run_interactive()


if __name__ == "__main__":
    main()
