# 🗣️ Speech-to-Text Module - PORTIER PAS-6.0
# OpenAI Whisper Integration for Call Transcription

import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class SpeechToText:
    """Speech-to-Text engine using OpenAI Whisper"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY_OPENA9", os.getenv("OPENAI_API_KEY", ""))
        self.model = "whisper-1"
        self.client = None

        # Supported audio formats
        self.supported_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]

        # Statistics
        self.stats = {"transcriptions_completed": 0, "total_audio_seconds": 0, "last_transcription": None}

    async def initialize(self):
        """Initialize OpenAI client for Whisper"""
        if self.openai_api_key:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=self.openai_api_key)
                logger.info("✅ Speech-to-Text engine initialized with Whisper")
            except ImportError:
                logger.warning("⚠️ OpenAI library not installed")
        else:
            logger.warning("⚠️ OpenAI API key not configured - using mock mode")

    async def transcribe(self, audio_data: bytes = None, audio_url: str = None, language: str = None) -> dict[str, Any]:
        """Transcribe audio to text"""
        if not audio_data and not audio_url:
            return {"error": "No audio data or URL provided"}

        self.stats["last_transcription"] = datetime.now().isoformat()

        if self.client and audio_data:
            try:
                # Create a temporary file-like object
                import io

                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.mp3"

                kwargs = {"model": self.model, "file": audio_file}
                if language:
                    kwargs["language"] = language

                response = await self.client.audio.transcriptions.create(**kwargs)

                self.stats["transcriptions_completed"] += 1

                return {
                    "status": "success",
                    "text": response.text,
                    "language": language or "detected",
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Transcription failed: {e}")
                return {"error": str(e)}

        # Mock transcription
        self.stats["transcriptions_completed"] += 1
        return {
            "status": "success",
            "text": "Dies ist eine Beispiel-Transkription. Die tatsächliche Transkription würde den gesprochenen Text enthalten.",
            "language": language or "de",
            "model": "mock",
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat(),
        }

    async def transcribe_with_timestamps(self, audio_data: bytes = None, language: str = None) -> dict[str, Any]:
        """Transcribe audio with word-level timestamps"""
        if not audio_data:
            return {"error": "No audio data provided"}

        if self.client and audio_data:
            try:
                import io

                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.mp3"

                kwargs = {
                    "model": self.model,
                    "file": audio_file,
                    "response_format": "verbose_json",
                    "timestamp_granularities": ["word", "segment"],
                }
                if language:
                    kwargs["language"] = language

                response = await self.client.audio.transcriptions.create(**kwargs)

                self.stats["transcriptions_completed"] += 1

                return {
                    "status": "success",
                    "text": response.text,
                    "segments": response.segments if hasattr(response, "segments") else [],
                    "words": response.words if hasattr(response, "words") else [],
                    "duration": response.duration if hasattr(response, "duration") else 0,
                    "language": language or "detected",
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Transcription with timestamps failed: {e}")
                return {"error": str(e)}

        # Mock response with timestamps
        return {
            "status": "success",
            "text": "Beispiel Transkription mit Zeitstempeln.",
            "segments": [
                {"start": 0.0, "end": 2.5, "text": "Beispiel Transkription"},
                {"start": 2.5, "end": 4.0, "text": "mit Zeitstempeln."},
            ],
            "words": [
                {"word": "Beispiel", "start": 0.0, "end": 0.8},
                {"word": "Transkription", "start": 0.9, "end": 2.0},
                {"word": "mit", "start": 2.5, "end": 2.8},
                {"word": "Zeitstempeln", "start": 2.9, "end": 4.0},
            ],
            "duration": 4.0,
            "language": language or "de",
            "model": "mock",
            "timestamp": datetime.now().isoformat(),
        }

    async def translate_audio(self, audio_data: bytes) -> dict[str, Any]:
        """Translate audio to English text"""
        if not audio_data:
            return {"error": "No audio data provided"}

        if self.client:
            try:
                import io

                audio_file = io.BytesIO(audio_data)
                audio_file.name = "audio.mp3"

                response = await self.client.audio.translations.create(model=self.model, file=audio_file)

                return {
                    "status": "success",
                    "text": response.text,
                    "target_language": "en",
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Translation failed: {e}")
                return {"error": str(e)}

        return {
            "status": "success",
            "text": "This is an example translation to English.",
            "target_language": "en",
            "model": "mock",
            "timestamp": datetime.now().isoformat(),
        }

    def is_supported_format(self, filename: str) -> bool:
        """Check if audio format is supported"""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        return ext in self.supported_formats

    def get_stats(self) -> dict[str, Any]:
        """Get transcription statistics"""
        return {
            "engine": "whisper",
            "model": self.model,
            "client_initialized": self.client is not None,
            "supported_formats": self.supported_formats,
            "statistics": self.stats.copy(),
        }
