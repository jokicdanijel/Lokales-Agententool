#!/usr/bin/env python3
"""
Speech-to-Text Demo for LocalAgent-Pro
Interactive demonstration of speech recognition capabilities
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import time

from src.speech_input import SpeechInput


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_single_listen():
    """Demo: Single speech input"""
    print_header("Demo 1: Single Speech Input")

    speech = SpeechInput(language="de-DE")

    print(
        """
This demo listens for a single speech command.
Say something after the prompt appears.

Examples:
  - "Öffne die Datei report.txt"
  - "Was ist das Wetter?"
  - "Speichere diese Datei"
    """
    )

    input("Press Enter to start listening...")
    result = speech.listen_once()

    if result:
        print(f"\n✅ You said: '{result}'")
        print(f"   Length: {len(result)} characters")
    else:
        print("\n❌ No speech recognized")


def demo_continuous_listen():
    """Demo: Continuous speech input"""
    print_header("Demo 2: Continuous Speech Input")

    speech = SpeechInput(language="de-DE")

    print(
        """
This demo listens for multiple commands in sequence.
You can say different things for each attempt.

The system will attempt to listen up to 5 times or until you stop.
    """
    )

    input("Press Enter to start listening...")
    results = speech.listen_continuous(max_iterations=3)

    if results:
        print(f"\n✅ Captured {len(results)} commands:")
        for i, text in enumerate(results, 1):
            print(f"   {i}. {text}")
    else:
        print("\n❌ No speech recognized")


def demo_microphone_test():
    """Demo: Microphone test and diagnostics"""
    print_header("Demo 3: Microphone Test")

    speech = SpeechInput(language="de-DE")

    print("\nTesting microphone configuration and audio quality...")
    result = speech.test_microphone()

    print("\n📊 Test Results:")
    print(f"  Status: {result['status']}")
    print(f"  Timestamp: {result['timestamp']}")

    if result["microphones"]:
        print(f"  Microphones found: {len(result['microphones'])}")
        for mic in result["microphones"][:3]:  # Show first 3
            print(f"    - Index {mic['index']}: {mic['name']}")

    if result["noise_level"]:
        print(f"  Noise Level: {result['noise_level']}")

    if result["status"] == "ERROR":
        print(f"  Error: {result.get('error', 'Unknown error')}")


def demo_language_support():
    """Demo: Multiple language support"""
    print_header("Demo 4: Language Support")

    languages = {
        "de-DE": "🇩🇪 Deutsch",
        "en-US": "🇺🇸 English",
        "fr-FR": "🇫🇷 Français",
        "es-ES": "🇪🇸 Español",
        "it-IT": "🇮🇹 Italiano",
    }

    print("\nSupported languages:")
    for code, name in languages.items():
        print(f"  {name:20} ({code})")

    print("\nYou can select a language and listen in that language.")
    print("Example usage in code:")
    print(
        """
        speech = SpeechInput(language="en-US")
        result = speech.listen_once()
    """
    )


def demo_command_interpreter():
    """Demo: Voice command interpreter"""
    print_header("Demo 5: Voice Command Interpreter")

    speech = SpeechInput(language="de-DE")

    print(
        """
This demo shows how to use voice commands for application control.

Voice command examples:
  - "Starte die Anwendung"     → Application control
  - "Speichere die Datei"      → File operations
  - "Zeige den Status"         → Status check
  - "Beende das Programm"      → Exit command
    """
    )

    input("Press Enter to start listening for a command...")
    command = speech.listen_once()

    if command:
        print(f"\n📝 Parsed command: '{command}'")

        # Simple command interpretation
        command_lower = command.lower()

        if any(word in command_lower for word in ["starten", "starte", "start"]):
            print("   → Action: Starting application")
        elif any(word in command_lower for word in ["speichern", "speichere", "save"]):
            print("   → Action: Saving file")
        elif any(word in command_lower for word in ["zeigen", "zeige", "show"]):
            print("   → Action: Showing status")
        elif any(word in command_lower for word in ["beenden", "ende", "exit", "quit"]):
            print("   → Action: Exiting program")
        else:
            print("   → Action: Unknown command (log for later processing)")


def demo_file_recognition():
    """Demo: File-based speech recognition"""
    print_header("Demo 6: File-Based Speech Recognition")

    speech = SpeechInput(language="de-DE")

    print(
        """
This demo shows how to process pre-recorded audio files.

First, record an audio file:
    1. The system will record audio when you press Enter
    2. Speak during the recording
    3. The system will recognize speech from the file

Supported formats: WAV, AIFF, FLAC, AU
    """
    )

    input("Press Enter to start recording...")

    # Record audio
    if speech.save_audio("demo_speech.wav"):
        print("\nNow processing the recorded audio...")
        time.sleep(1)

        # Recognize from file
        result = speech.recognize_from_file("demo_speech.wav")
        if result:
            print(f"✅ Recognized: {result}")
        else:
            print("❌ Could not recognize speech from file")
    else:
        print("❌ Failed to record audio")


def main():
    """Main demo launcher"""
    print("\n" + "=" * 60)
    print("  🎤 LocalAgent-Pro Speech-to-Text Demo")
    print("=" * 60)

    demos = {
        "1": ("Single Speech Input", demo_single_listen),
        "2": ("Continuous Speech Input", demo_continuous_listen),
        "3": ("Microphone Test", demo_microphone_test),
        "4": ("Language Support", demo_language_support),
        "5": ("Voice Command Interpreter", demo_command_interpreter),
        "6": ("File-Based Recognition", demo_file_recognition),
        "0": ("Exit", None),
    }

    print("\nAvailable demos:")
    for key, (name, _) in demos.items():
        if key != "0":
            print(f"  {key}. {name}")
    print(f"  {key}. {demos['0'][0]}")

    while True:
        try:
            choice = input("\nSelect demo (0-6): ").strip()

            if choice == "0":
                print("\n👋 Goodbye!")
                break

            if choice in demos and choice != "0":
                name, demo_func = demos[choice]
                try:
                    demo_func()
                except KeyboardInterrupt:
                    print("\n⏹️  Demo interrupted")
                except Exception as e:
                    print(f"\n❌ Error: {e}")
            else:
                print("Invalid selection. Please try again.")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
