# 📞 OPENA9 Telephone Agent - Tests
# PORTIER PAS-6.0

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTelephonyCore:
    """Tests for TelephonyCore module"""
    
    @pytest.mark.asyncio
    async def test_execute_make_call(self):
        """Test make_call command execution"""
        from modules.telephony_core import TelephonyCore
        
        core = TelephonyCore()
        result = await core.execute("make_call", {
            "to": "+491234567890",
            "from_number": "+490987654321"
        })
        
        assert result["status"] in ["success", "simulated"]
        assert "call_id" in result or "result" in result
    
    @pytest.mark.asyncio
    async def test_execute_list_active_calls(self):
        """Test list_active_calls command"""
        from modules.telephony_core import TelephonyCore
        
        core = TelephonyCore()
        result = await core.execute("list_active_calls", {})
        
        assert result["status"] == "success"
        assert "calls" in result
        assert isinstance(result["calls"], list)
    
    @pytest.mark.asyncio
    async def test_status(self):
        """Test status method"""
        from modules.telephony_core import TelephonyCore
        
        core = TelephonyCore()
        status = await core.status()
        
        assert status["core"] == "operational"
        assert "active_calls" in status
        assert "uptime" in status
    
    @pytest.mark.asyncio
    async def test_get_config(self):
        """Test config retrieval"""
        from modules.telephony_core import TelephonyCore
        
        core = TelephonyCore()
        config = await core.get_config()
        
        assert "port" in config
        assert config["port"] == 12355
        assert "name" in config
    
    @pytest.mark.asyncio
    async def test_execute_unknown_command(self):
        """Test handling of unknown command"""
        from modules.telephony_core import TelephonyCore
        
        core = TelephonyCore()
        result = await core.execute("unknown_command", {})
        
        assert result["status"] == "error"
        assert "Unknown command" in result.get("message", result.get("error", ""))


class TestTelephonyAPI:
    """Tests for TelephonyAPI module"""
    
    @pytest.mark.asyncio
    async def test_twilio_client_init(self):
        """Test TwilioClient initialization"""
        from modules.telephony_api import TelephonyAPI
        
        api = TelephonyAPI()
        # Should initialize without error even without credentials
        assert api is not None
    
    @pytest.mark.asyncio
    async def test_make_call_mock(self):
        """Test make_call with mock"""
        from modules.telephony_api import TelephonyAPI
        
        api = TelephonyAPI()
        result = await api.make_call(
            to="+491234567890",
            from_number="+490987654321"
        )
        
        # In mock mode, should return simulated result
        assert "call_id" in result or "status" in result


class TestAIVoiceEngine:
    """Tests for AIVoiceEngine module"""
    
    @pytest.mark.asyncio
    async def test_generate_voice_reply_mock(self):
        """Test voice generation in mock mode"""
        from modules.ai_voice_engine import AIVoiceEngine
        
        engine = AIVoiceEngine()
        result = await engine.generate_voice_reply("Hello, this is a test")
        
        assert result["status"] == "success"
        assert "text" in result
    
    @pytest.mark.asyncio
    async def test_generate_ivr_flow_mock(self):
        """Test IVR flow generation"""
        from modules.ai_voice_engine import AIVoiceEngine
        
        engine = AIVoiceEngine()
        result = await engine.generate_ivr_flow(
            scenario="customer_support",
            options=["sales", "support", "billing"]
        )
        
        assert result["status"] == "success"
        assert "ivr_flow" in result
    
    @pytest.mark.asyncio
    async def test_auto_response(self):
        """Test auto-response generation"""
        from modules.ai_voice_engine import AIVoiceEngine
        
        engine = AIVoiceEngine()
        result = await engine.auto_response(
            trigger="incoming_call",
            caller_id="+491234567890"
        )
        
        assert result["status"] == "success"
        assert "response" in result


class TestSpeechToText:
    """Tests for SpeechToText module"""
    
    @pytest.mark.asyncio
    async def test_transcribe_mock(self):
        """Test transcription in mock mode"""
        from modules.speech_to_text import SpeechToText
        
        stt = SpeechToText()
        result = await stt.transcribe(audio_data=b"fake_audio_data")
        
        assert result["status"] == "success"
        assert "text" in result
    
    @pytest.mark.asyncio
    async def test_transcribe_with_timestamps(self):
        """Test transcription with timestamps"""
        from modules.speech_to_text import SpeechToText
        
        stt = SpeechToText()
        result = await stt.transcribe_with_timestamps(audio_data=b"fake_audio_data")
        
        assert result["status"] == "success"
        assert "segments" in result
        assert "words" in result
    
    def test_is_supported_format(self):
        """Test format validation"""
        from modules.speech_to_text import SpeechToText
        
        stt = SpeechToText()
        
        assert stt.is_supported_format("audio.mp3") is True
        assert stt.is_supported_format("audio.wav") is True
        assert stt.is_supported_format("audio.pdf") is False
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        from modules.speech_to_text import SpeechToText
        
        stt = SpeechToText()
        stats = stt.get_stats()
        
        assert "engine" in stats
        assert stats["engine"] == "whisper"
        assert "statistics" in stats


class TestMetrics:
    """Tests for Metrics module"""
    
    def test_metrics_increment(self):
        """Test counter increment"""
        from modules.metrics import TelephonyMetrics
        
        metrics = TelephonyMetrics()
        initial = metrics.counters["calls_made"]
        
        metrics.increment("calls_made", 5)
        
        assert metrics.counters["calls_made"] == initial + 5
    
    def test_metrics_record_call(self):
        """Test call recording"""
        from modules.metrics import TelephonyMetrics
        
        metrics = TelephonyMetrics()
        
        metrics.record_call({
            "call_id": "test-123",
            "direction": "outbound",
            "duration": 60,
            "status": "completed"
        })
        
        assert len(metrics.call_history) > 0
        assert metrics.call_history[-1]["call_id"] == "test-123"
    
    def test_metrics_get_summary(self):
        """Test summary generation"""
        from modules.metrics import TelephonyMetrics
        
        metrics = TelephonyMetrics()
        summary = metrics.get_summary()
        
        assert "agent" in summary
        assert summary["agent"] == "opena9_telephone"
        assert "uptime" in summary
        assert "counters" in summary
    
    def test_prometheus_format(self):
        """Test Prometheus export"""
        from modules.metrics import TelephonyMetrics
        
        metrics = TelephonyMetrics()
        prom_output = metrics.to_prometheus_format()
        
        assert "opena9_uptime_seconds" in prom_output
        assert "opena9_calls_total" in prom_output


class TestMainApp:
    """Tests for main FastAPI application"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from main import app
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "opena9_telephone"
    
    def test_status_endpoint(self, client):
        """Test /status endpoint"""
        response = client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "agent" in data
        assert "version" in data
    
    def test_command_endpoint(self, client):
        """Test /command endpoint"""
        response = client.post("/command", json={
            "command": "list_active_calls",
            "params": {}
        })
        assert response.status_code == 200
    
    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
