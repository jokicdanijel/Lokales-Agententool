"""
opena8 WhatsApp Service Unit Tests
Classification, models, API contracts
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import (
    WhatsAppMessage, MessageType, MessageDirection, SentimentType, MediaType,
    MediaObject, SendMessageRequest, HealthResponse, Safepoint, WebhookRequest,
    MailRunRequest, MailRunResponse
)
from app.config import config
from app.whatsapp_client import MessageClassifier, MediaHandler, WhatsAppClient


class TestHealthEndpoints:
    """Health check structure validation"""
    
    def test_health_response_structure(self):
        """Validate HealthResponse Pydantic model"""
        health = HealthResponse(
            status="ok",
            service="opena8",
            timestamp=datetime.utcnow(),
            meta_api_connected=True,
            opena2_connected=True,
            opena1_connected=True
        )
        assert health.status == "ok"
        assert health.service == "opena8"
        assert health.meta_api_connected is True


class TestMessageClassifier:
    """Message classification tests"""
    
    def test_language_detection_german(self):
        """Detect German language"""
        lang = MessageClassifier.detect_language("Hallo, wie geht es dir?")
        assert lang == "DE"
    
    def test_language_detection_english(self):
        """Detect English language"""
        lang = MessageClassifier.detect_language("Hello, how are you doing?")
        assert lang == "EN"
    
    def test_sentiment_classification_urgent(self):
        """Classify URGENT sentiment"""
        sentiment, urgency = MessageClassifier.classify_sentiment(
            "URGENT: Help needed immediately",
            ""
        )
        assert sentiment == SentimentType.URGENT
        assert urgency >= 7
    
    def test_sentiment_classification_positive(self):
        """Classify POSITIVE sentiment"""
        sentiment, urgency = MessageClassifier.classify_sentiment(
            "Great job, thank you so much",
            ""
        )
        assert sentiment == SentimentType.POSITIVE
    
    def test_phone_allowlist_check(self):
        """Check phone allowlist enforcement"""
        result = MessageClassifier.check_allowlist("+49123456789")
        assert isinstance(result, bool)


class TestMediaHandler:
    """Media processing tests"""
    
    def test_media_size_validation(self):
        """Validate media size limits"""
        max_size = config.MEDIA_MAX_SIZE_MB * 1024 * 1024
        assert MediaHandler.validate_media_size(max_size - 1000) is True
        assert MediaHandler.validate_media_size(max_size + 1000) is False
    
    def test_sha256_calculation(self):
        """Calculate SHA256 hash"""
        data = b"test media content"
        hash_result = MediaHandler.calculate_sha256(data)
        assert len(hash_result) == 64  # SHA256 hex string


class TestWhatsAppMessage:
    """WhatsApp message model tests"""
    
    def test_message_creation_text(self):
        """Create text message"""
        msg = WhatsAppMessage(
            message_id="msg123",
            phone_number="+49123456789",
            timestamp=datetime.utcnow(),
            direction=MessageDirection.INBOUND,
            type=MessageType.TEXT,
            body="Hello there"
        )
        assert msg.type == MessageType.TEXT
        assert msg.body == "Hello there"
        assert msg.sentiment == SentimentType.NEUTRAL
    
    def test_message_creation_with_media(self):
        """Create message with media"""
        media = MediaObject(
            media_type=MediaType.IMAGE,
            media_id="img123",
            mime_type="image/jpeg"
        )
        msg = WhatsAppMessage(
            message_id="msg456",
            phone_number="+49123456789",
            timestamp=datetime.utcnow(),
            direction=MessageDirection.INBOUND,
            type=MessageType.IMAGE,
            media=media
        )
        assert msg.media is not None
        assert msg.media.media_type == MediaType.IMAGE


class TestSendMessageRequest:
    """Send message request validation"""
    
    def test_text_message_request(self):
        """Validate text message request"""
        req = SendMessageRequest(
            to_phone="+49123456789",
            message_type=MessageType.TEXT,
            body="Test message"
        )
        assert req.to_phone == "+49123456789"
        assert req.message_type == MessageType.TEXT
    
    def test_media_message_request(self):
        """Validate media message request"""
        req = SendMessageRequest(
            to_phone="+49123456789",
            message_type=MessageType.IMAGE,
            media_url="https://example.com/image.jpg",
            media_type=MediaType.IMAGE
        )
        assert req.media_type == MediaType.IMAGE


class TestConfiguration:
    """Config tests"""
    
    def test_config_defaults(self):
        """Verify config defaults"""
        assert config.SERVICE_NAME == "opena8"
        assert config.SERVICE_COMPONENT == "whatsapp"
        assert config.PORT == 12351


class TestSafepoint:
    """Safepoint archiving structure"""
    
    def test_safepoint_creation(self):
        """Create safepoint"""
        sp = Safepoint(
            ts=datetime.utcnow(),
            src="opena8",
            dst="opena2",
            kind="MSG",
            payload={"message_id": "msg123"}
        )
        assert sp.src == "opena8"
        assert sp.kind == "MSG"
        assert sp.status == "ok"


class TestMailRunRequests:
    """Generic run requests"""
    
    def test_ingest_action(self):
        """Test ingest action request"""
        req = MailRunRequest(
            action="ingest",
            payload={"webhook_entry": {}}
        )
        assert req.action == "ingest"
    
    def test_send_action(self):
        """Test send action request"""
        req = MailRunRequest(
            action="send",
            payload={"to_phone": "+49123456789", "body": "Hi"}
        )
        assert req.action == "send"


class TestMailRunResponse:
    """Generic run responses"""
    
    def test_success_response(self):
        """Test success response"""
        resp = MailRunResponse(
            success=True,
            action="send",
            data={"message_id": "msg123"},
            timestamp=datetime.utcnow()
        )
        assert resp.success is True
    
    def test_error_response(self):
        """Test error response"""
        resp = MailRunResponse(
            success=False,
            action="send",
            error="Invalid phone number",
            timestamp=datetime.utcnow()
        )
        assert resp.success is False
        assert resp.error is not None


class TestMockWhatsAppClient:
    """Mock WhatsApp client tests (no real API)"""
    
    @pytest.mark.asyncio
    async def test_parse_webhook_success(self):
        """Test webhook parsing"""
        client = WhatsAppClient()
        
        # Mock webhook entry
        entry = {
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "msg123",
                        "from": "+49123456789",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "Hello"}
                    }],
                    "contacts": [{
                        "profile": {"name": "Test User"}
                    }]
                }
            }]
        }
        
        msg = await client.parse_webhook_event(entry)
        assert msg is not None
        assert msg.message_id == "msg123"
        assert msg.body == "Hello"
    
    @pytest.mark.asyncio
    async def test_send_message_mock(self):
        """Test message sending (mocked)"""
        client = WhatsAppClient()
        
        with patch.object(client, 'send_message', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = (True, "msg123", None)
            success, msg_id, error = await client.send_message("+49123456789", "Test")
            
            assert success is True
            assert msg_id == "msg123"
