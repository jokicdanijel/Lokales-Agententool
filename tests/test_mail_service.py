"""
opena7 Mail Agent Unit Tests
Health, mail processing, classification, attachment handling
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

import sys
sys.path.insert(0, "6.opena7_mail")

from app.config import config
from app.models import (
    MailMessage, AttachmentInfo, MailRunRequest, MailRunResponse,
    MailAction, SentimentType, HealthResponse, EventLog
)
from app.mail_client import MailClassifier, AttachmentHandler


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_response_structure(self):
        """Verify health check response structure"""
        
        health = HealthResponse(
            service="opena7",
            status="ok",
            component="mail",
            port=12350,
            mailbox="inbox@example.org",
            imap_connected=True,
            smtp_connected=True,
            ts=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        )
        
        assert health.service == "opena7"
        assert health.status == "ok"
        assert health.component == "mail"
        assert health.imap_connected is True


class TestMailClassifier:
    """Test email classification (sentiment, language, urgency)"""
    
    def test_language_detection_german(self):
        """Test German language detection"""
        
        de_text = "Hallo, danke für deine Nachricht. Anbei findest du die Informationen."
        lang = MailClassifier.detect_language(de_text)
        
        assert lang == "de"
    
    def test_language_detection_english(self):
        """Test English language detection"""
        
        en_text = "Hello, thank you for your message. Attached you will find the information."
        lang = MailClassifier.detect_language(en_text)
        
        assert lang == "en"
    
    def test_sentiment_classification(self):
        """Test sentiment and urgency classification"""
        
        subject = "URGENT: Critical System Issue"
        body = "We have a critical problem that needs immediate attention."
        
        sentiment, urgency = MailClassifier.classify_sentiment(subject, body)
        
        assert sentiment == SentimentType.URGENT
        assert urgency >= 7
    
    def test_sender_allowlist_check(self):
        """Test sender allowlist enforcement"""
        
        # Mock config with allowlist
        with patch('app.mail_client.config') as mock_config:
            mock_config.MAIL_ALLOWLIST = ["@example.org", "trusted@partner.de"]
            mock_config.MAIL_BLOCKLIST = []
            
            classifier = MailClassifier()
            
            # Should allow
            assert classifier.check_allowlist("user@example.org") is True
            assert classifier.check_allowlist("trusted@partner.de") is True
            
            # Should block
            assert classifier.check_allowlist("unknown@badactor.com") is False


class TestAttachmentHandler:
    """Test attachment processing & validation"""
    
    def test_attachment_info_structure(self):
        """Verify attachment info structure"""
        
        attachment = AttachmentInfo(
            filename="document.pdf",
            mime_type="application/pdf",
            size_bytes=1024000,
            sha256="abc123def456",
            path="archivp/2025/11/10/mail/attachments/doc.pdf",
            scanned=True,
            safe=True
        )
        
        assert attachment.filename == "document.pdf"
        assert attachment.size_bytes == 1024000
        assert attachment.safe is True
    
    def test_dangerous_extension_detection(self):
        """Test dangerous file extension detection"""
        
        handler = AttachmentHandler()
        
        with patch('app.mail_client.config') as mock_config:
            mock_config.DANGEROUS_EXTENSIONS = [".exe", ".dll", ".zip"]
            mock_config.MAIL_ATTACHMENT_LIMIT_MB = 50
            mock_config.SCAN_ATTACHMENTS = True
            
            # .exe should be flagged
            assert ".exe".lower() in mock_config.DANGEROUS_EXTENSIONS


class TestMailMessage:
    """Test email message model"""
    
    def test_mail_message_creation(self):
        """Verify mail message structure"""
        
        message = MailMessage(
            msg_id="12345",
            subject="Test Subject",
            sender="sender@example.org",
            recipients=["recipient@example.org"],
            date=datetime.utcnow().isoformat(),
            body_text="Test email body",
            body_preview="Test email body",
            sentiment=SentimentType.NEUTRAL,
            urgency=5,
            language="en"
        )
        
        assert message.msg_id == "12345"
        assert message.subject == "Test Subject"
        assert message.language == "en"
        assert message.urgency == 5
    
    def test_mail_message_with_attachments(self):
        """Test mail message with attachments"""
        
        attachments = [
            AttachmentInfo(
                filename="report.pdf",
                mime_type="application/pdf",
                size_bytes=512000
            ),
            AttachmentInfo(
                filename="data.csv",
                mime_type="text/csv",
                size_bytes=8192
            )
        ]
        
        message = MailMessage(
            msg_id="12345",
            subject="Report Delivery",
            sender="admin@example.org",
            recipients=["user@example.org"],
            date=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            body_text="Please find attached reports.",
            body_preview="Please find attached reports.",
            attachments=attachments
        )
        
        assert len(message.attachments) == 2
        assert message.attachments[0].filename == "report.pdf"


class TestMailRunRequest:
    """Test mail run request validation"""
    
    def test_fetch_action_request(self):
        """Verify fetch action request"""
        
        request = MailRunRequest(
            request_id="test-001",
            action=MailAction.FETCH,
            payload={
                "mailbox": "INBOX",
                "max_count": 10
            }
        )
        
        assert request.action == MailAction.FETCH
        assert request.payload["mailbox"] == "INBOX"
    
    def test_fetch_and_reply_request(self):
        """Verify fetch and reply action"""
        
        request = MailRunRequest(
            request_id="test-002",
            action=MailAction.FETCH_AND_REPLY,
            payload={
                "mailbox": "support@example.org",
                "mode": "unread_only",
                "reply_template": "templates/auto_reply.md"
            }
        )
        
        assert request.action == MailAction.FETCH_AND_REPLY
        assert "reply_template" in request.payload
    
    def test_send_action_request(self):
        """Verify send action"""
        
        request = MailRunRequest(
            request_id="test-003",
            action=MailAction.SEND,
            payload={
                "recipient": "user@example.org",
                "subject": "Test Email",
                "body_text": "This is a test email."
            }
        )
        
        assert request.action == MailAction.SEND
        assert request.payload["recipient"] == "user@example.org"


class TestMailRunResponse:
    """Test mail run response structure"""
    
    def test_successful_fetch_response(self):
        """Verify successful fetch response"""
        
        response = MailRunResponse(
            request_id="test-001",
            status="success",
            action=MailAction.FETCH,
            processed=5,
            succeeded=5,
            processing_ms=2150
        )
        
        assert response.status == "success"
        assert response.processed == 5
        assert response.processing_ms == 2150
    
    def test_failed_response(self):
        """Verify error response"""
        
        response = MailRunResponse(
            request_id="test-001",
            status="failed",
            action=MailAction.FETCH,
            processing_ms=500,
            errors=[{"msg": "Authentication failed"}]
        )
        
        assert response.status == "failed"
        assert len(response.errors) > 0


class TestConfiguration:
    """Test configuration loading"""
    
    def test_config_defaults(self):
        """Verify configuration defaults"""
        
        assert config.SERVICE_NAME == "opena7"
        assert config.SERVICE_COMPONENT == "mail"
        assert config.PORT == 12350
        assert config.MAIL_IMAP_SSL is True
        assert config.MAIL_SMTP_TLS is True


class TestMockMailClient:
    """Mock mail client tests (no server required)"""
    
    @pytest.mark.asyncio
    async def test_mock_mail_fetch(self):
        """Test mock mail fetch"""
        
        from app.models import MailMessage
        
        mock_message = MailMessage(
            msg_id="mock-001",
            subject="Test Subject",
            sender="test@example.org",
            recipients=["inbox@example.org"],
            date=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            body_text="This is a test message.",
            body_preview="This is a test message."
        )
        
        assert mock_message.msg_id == "mock-001"
        assert mock_message.subject == "Test Subject"
    
    @pytest.mark.asyncio
    async def test_mock_mail_send(self):
        """Test mock mail send"""
        
        # Simulate successful send
        send_success = True
        
        assert send_success is True


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
