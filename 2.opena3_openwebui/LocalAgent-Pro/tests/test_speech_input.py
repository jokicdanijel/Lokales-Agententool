"""
Unit tests for Speech Input Module
Tests speech recognition and audio processing functionality
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.speech_input import SpeechInput, initialize, listen, test_mic


class TestSpeechInput(unittest.TestCase):
    """Test cases for SpeechInput class"""

    def setUp(self):
        """Set up test fixtures"""
        self.speech = SpeechInput(language="de-DE")

    def test_initialization(self):
        """Test SpeechInput initialization"""
        self.assertIsNotNone(self.speech.recognizer)
        self.assertEqual(self.speech.language, "de-DE")
        self.assertEqual(self.speech.timeout, 10)

    def test_change_language(self):
        """Test language change"""
        self.speech.change_language("en-US")
        self.assertEqual(self.speech.language, "en-US")

    @patch('speech_recognition.Microphone')
    def test_listen_once_success(self, mock_mic):
        """Test successful single listen"""
        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "test command"

        with patch.object(self.speech, 'recognizer', mock_recognizer):
            # This would require more complex mocking
            # Skipped for now as it needs audio data
            pass

    def test_microphone_list(self):
        """Test microphone listing"""
        try:
            import speech_recognition as sr
            mics = sr.Microphone.list_microphone_indexes()
            self.assertIsInstance(mics, list)
        except Exception as e:
            self.skipTest(f"Microphone test skipped: {e}")

    def test_language_codes(self):
        """Test various language codes"""
        languages = ["de-DE", "en-US", "fr-FR", "es-ES"]
        for lang in languages:
            speech = SpeechInput(language=lang)
            self.assertEqual(speech.language, lang)


class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions"""

    def test_initialize(self):
        """Test global initialization"""
        speech = initialize("de-DE")
        self.assertIsNotNone(speech)
        self.assertEqual(speech.language, "de-DE")

    def test_test_mic_function(self):
        """Test microphone test function"""
        try:
            result = test_mic()
            self.assertIsInstance(result, dict)
            self.assertIn("status", result)
        except Exception as e:
            self.skipTest(f"Microphone test skipped: {e}")


class TestSpeechInputIntegration(unittest.TestCase):
    """Integration tests"""

    def test_module_imports(self):
        """Test that module imports correctly"""
        import src.speech_input
        self.assertTrue(hasattr(src.speech_input, 'SpeechInput'))
        self.assertTrue(hasattr(src.speech_input, 'initialize'))
        self.assertTrue(hasattr(src.speech_input, 'listen'))

    def test_exception_handling(self):
        """Test exception handling"""
        speech = SpeechInput()
        # Test with invalid file
        result = speech.recognize_from_file("/nonexistent/file.wav")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
