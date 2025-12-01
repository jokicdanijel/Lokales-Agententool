"""
Speech-to-Text Input Module for LocalAgent-Pro
Provides voice command recognition and audio processing
"""

import speech_recognition as sr
import os
import json
from datetime import datetime
from typing import Optional, Tuple, List
from pathlib import Path

# Optional PyAudio import for better microphone support
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class SpeechInput:
    """
    Handles speech recognition and audio input processing
    Uses Google Speech Recognition API
    """

    def __init__(self, language: str = "de-DE", timeout: int = 10):
        """
        Initialize Speech Recognition

        Args:
            language: Language code (default: German)
            timeout: Timeout for listening in seconds
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.timeout = timeout
        
        try:
            self.microphone = sr.Microphone()
            # Ambient noise calibration
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception as e:
            # Fallback: create microphone object without testing
            self.microphone = sr.Microphone()
            print(f"⚠️  Warning: Microphone initialization: {e}")

    def listen_once(self) -> Optional[str]:
        """
        Listen for a single speech input

        Returns:
            Recognized text or None if failed
        """
        try:
            with self.microphone as source:
                print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=self.timeout)

            print("⏳ Processing audio...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"✅ Recognized: {text}")
            return text

        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ API error: {e}")
            return None
        except sr.WaitTimeoutError:
            print("⏱️  Timeout: No speech detected")
            return None

    def listen_continuous(self, max_iterations: int = 5) -> List[str]:
        """
        Listen continuously for multiple speech inputs

        Args:
            max_iterations: Maximum number of listening attempts

        Returns:
            List of recognized texts
        """
        results = []
        for i in range(max_iterations):
            print(f"\n📢 Attempt {i+1}/{max_iterations}")
            text = self.listen_once()
            if text:
                results.append(text)
            else:
                break

        return results

    def test_microphone(self) -> dict:
        """
        Test microphone availability and quality

        Returns:
            Dictionary with microphone info
        """
        info = {
            "status": "OK",
            "timestamp": datetime.now().isoformat(),
            "microphones": [],
            "noise_level": None
        }

        try:
            # List all microphones
            for i, mic_name in enumerate(sr.Microphone.list_microphone_indexes()):
                info["microphones"].append({
                    "index": i,
                    "name": sr.Microphone.list_microphone_indexes()[i]
                })

            # Test default microphone
            with self.microphone as source:
                print("🎧 Testing microphone...")
                audio = self.recognizer.listen(source, timeout=2)
                info["noise_level"] = "OK - Microphone is working"
                print(f"✅ Microphone test passed")

        except Exception as e:
            info["status"] = "ERROR"
            info["error"] = str(e)
            print(f"❌ Microphone test failed: {e}")

        return info

    def save_audio(self, filename: str = "speech_input.wav") -> bool:
        """
        Record and save audio to file

        Args:
            filename: Output filename

        Returns:
            True if successful
        """
        try:
            with self.microphone as source:
                print("🎤 Recording... (speak now)")
                audio = self.recognizer.listen(source, timeout=self.timeout)

            # Save audio
            with open(filename, "wb") as f:
                f.write(audio.get_wav_data())

            print(f"✅ Audio saved to {filename}")
            return True

        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
            return False

    def recognize_from_file(self, filename: str) -> Optional[str]:
        """
        Recognize speech from audio file

        Args:
            filename: Path to audio file

        Returns:
            Recognized text or None
        """
        try:
            if not os.path.exists(filename):
                print(f"❌ File not found: {filename}")
                return None

            with sr.AudioFile(filename) as source:
                print(f"📁 Processing audio file: {filename}")
                audio = self.recognizer.record(source)

            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"✅ Recognized: {text}")
            return text

        except sr.UnknownValueError:
            print("❌ Could not understand audio file")
            return None
        except sr.RequestError as e:
            print(f"❌ API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def change_language(self, language_code: str) -> None:
        """
        Change recognition language

        Args:
            language_code: Language code (e.g., 'en-US', 'de-DE')
        """
        self.language = language_code
        print(f"🌐 Language changed to: {language_code}")


# Convenience functions
_speech_input = None

def initialize(language: str = "de-DE") -> SpeechInput:
    """Initialize global speech input instance"""
    global _speech_input
    _speech_input = SpeechInput(language=language)
    return _speech_input

def listen() -> Optional[str]:
    """Listen for single speech input"""
    global _speech_input
    if _speech_input is None:
        initialize()
    return _speech_input.listen_once()

def listen_continuous(max_iterations: int = 5) -> List[str]:
    """Listen continuously for multiple inputs"""
    global _speech_input
    if _speech_input is None:
        initialize()
    return _speech_input.listen_continuous(max_iterations)

def test_mic() -> dict:
    """Test microphone"""
    global _speech_input
    if _speech_input is None:
        initialize()
    return _speech_input.test_microphone()


if __name__ == "__main__":
    # Quick test
    print("🚀 Speech Input Module Test")
    print("=" * 50)

    speech = initialize("de-DE")

    # Test microphone
    print("\n1️⃣  Testing microphone...")
    speech.test_microphone()

    # Single listen
    print("\n2️⃣  Single listen test...")
    result = speech.listen_once()

    print("\n✅ Test complete!")
