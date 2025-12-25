#!/usr/bin/env python3
"""
Voice Scheduler - Schedule and manage tasks via voice commands
Production tool for voice-based task management
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from datetime import datetime

from src.speech_input import SpeechInput


class VoiceScheduler:
    """Manage scheduled tasks with voice interface"""

    def __init__(self, tasks_file="tasks.json", language="de-DE"):
        self.speech = SpeechInput(language=language)
        self.tasks_file = Path(tasks_file)
        self.load_tasks()
        self.running = False

    def load_tasks(self):
        """Load tasks from file"""
        if self.tasks_file.exists():
            with open(self.tasks_file, encoding="utf-8") as f:
                self.tasks = json.load(f)
        else:
            self.tasks = []

    def save_tasks(self):
        """Save tasks to file"""
        with open(self.tasks_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task_voice(self):
        """Add task via voice command"""
        print("\n🎤 Aufgabe diktieren")
        print("-" * 40)
        print("Beschreibe die Aufgabe...")

        description = self.speech.listen_once()
        if not description:
            print("❌ Keine Sprache erkannt")
            return

        print("Wann soll die Aufgabe stattfinden?")
        when = self.speech.listen_once()

        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "when": when,
            "created": datetime.now().isoformat(),
            "completed": False,
        }

        self.tasks.append(task)
        self.save_tasks()
        print(f"✅ Aufgabe hinzugefügt: {description}")
        return task

    def add_task_manual(self, description, when):
        """Add task manually"""
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "when": when,
            "created": datetime.now().isoformat(),
            "completed": False,
        }

        self.tasks.append(task)
        self.save_tasks()
        print(f"✅ Aufgabe hinzugefügt: {description}")
        return task

    def list_tasks(self, filter_completed=False):
        """List tasks"""
        print("\n📋 Aufgaben:")
        print("-" * 40)

        tasks_to_show = self.tasks
        if filter_completed:
            tasks_to_show = [t for t in self.tasks if not t["completed"]]

        if not tasks_to_show:
            print("Keine Aufgaben vorhanden")
            return

        for task in tasks_to_show:
            status = "✅" if task["completed"] else "⏳"
            print(f"{status} {task['id']}. {task['description']}")
            print(f"   Wann: {task['when']}")

    def complete_task(self, task_id):
        """Mark task as completed"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self.save_tasks()
                print(f"✅ Aufgabe abgeschlossen: {task['description']}")
                return task

        print("❌ Aufgabe nicht gefunden")
        return None

    def delete_task(self, task_id):
        """Delete task"""
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self.save_tasks()
        print("✅ Aufgabe gelöscht")

    def get_pending_tasks(self):
        """Get pending tasks"""
        pending = [t for t in self.tasks if not t["completed"]]

        if pending:
            print(f"\n📌 {len(pending)} ausstehende Aufgaben:")
            for task in pending[:5]:
                print(f"  • {task['description']}")
        else:
            print("\n✨ Keine ausstehenden Aufgaben!")

    def run_interactive(self):
        """Run interactive scheduler"""
        print("\n" + "=" * 60)
        print("  📅 Voice Scheduler")
        print("=" * 60)

        while True:
            print("\n📅 Menü:")
            print("  1. Aufgabe hinzufügen (Sprache)")
            print("  2. Aufgabe hinzufügen (manuell)")
            print("  3. Aufgaben anzeigen")
            print("  4. Aufgabe abschließen")
            print("  5. Aufgabe löschen")
            print("  6. Ausstehende Aufgaben")
            print("  0. Beenden")

            choice = input("\nWahl: ").strip()

            if choice == "1":
                self.add_task_voice()
            elif choice == "2":
                description = input("Beschreibung: ")
                when = input("Wann: ")
                self.add_task_manual(description, when)
            elif choice == "3":
                self.list_tasks()
            elif choice == "4":
                self.list_tasks()
                task_id = int(input("Aufgaben-ID: "))
                self.complete_task(task_id)
            elif choice == "5":
                self.list_tasks()
                task_id = int(input("Aufgaben-ID löschen: "))
                self.delete_task(task_id)
            elif choice == "6":
                self.get_pending_tasks()
            elif choice == "0":
                print("👋 Auf Wiedersehen!")
                break


def main():
    scheduler = VoiceScheduler()
    scheduler.run_interactive()


if __name__ == "__main__":
    main()
