# 📱 WhatsApp Business API Handler - PORTIER PAS-6.0
# Advanced WhatsApp Business API Integration with Rate Limiting and Error Handling

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """WhatsApp message types"""

    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"


@dataclass
class WhatsAppMessage:
    """WhatsApp message structure"""

    to: str
    message_type: MessageType
    content: dict[str, Any]
    context: dict[str, Any] | None = None


class RateLimiter:
    """Rate limiter for WhatsApp API calls"""

    def __init__(self, max_requests: int = 80, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    async def acquire(self) -> bool:
        """Check if request can be made within rate limits"""
        now = datetime.now()
        # Remove old requests outside time window
        self.requests = [req_time for req_time in self.requests if now - req_time < timedelta(seconds=self.time_window)]

        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False

    def reset_in(self) -> int:
        """Seconds until rate limit resets"""
        if not self.requests:
            return 0
        oldest = min(self.requests)
        return max(0, int((oldest + timedelta(seconds=self.time_window) - datetime.now()).total_seconds()))


class WhatsAppAPI:
    """WhatsApp Business API Handler with advanced features"""

    def __init__(self):
        # Environment configuration
        self.token = os.getenv("WHATSAPP_TOKEN", "")
        self.phone_id = os.getenv("WHATSAPP_PHONE_ID", "")
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v18.0")
        self.webhook_verify_token = os.getenv("WHATSAPP_WEBHOOK_TOKEN", "")

        # API endpoints
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        self.messages_url = f"{self.base_url}/{self.phone_id}/messages"
        self.media_url = f"{self.base_url}/{self.phone_id}/media"

        # Rate limiting
        self.rate_limiter = RateLimiter(max_requests=80, time_window=60)

        # Session for connection pooling
        self.session: aiohttp.ClientSession | None = None

        # Statistics
        self.stats = {
            "messages_sent": 0,
            "messages_failed": 0,
            "media_uploads": 0,
            "rate_limit_hits": 0,
            "last_activity": None,
        }

    async def initialize(self):
        """Initialize HTTP session and verify credentials"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "WhatsAppAgent/6.0 PORTIER-PAS",
            },
        )

        # Test connection
        if self.token and self.phone_id:
            try:
                await self.test_connection()
                logger.info("✅ WhatsApp API initialized successfully")
            except Exception as e:
                logger.error(f"❌ WhatsApp API initialization failed: {e}")
                raise

    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def test_connection(self) -> bool:
        """Test WhatsApp API connection"""
        if not self.session:
            await self.initialize()

        try:
            # Test with phone number info endpoint
            url = f"{self.base_url}/{self.phone_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"WhatsApp connection test successful: {data.get('display_phone_number', 'Unknown')}")
                    return True
                else:
                    logger.error(f"WhatsApp connection test failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"WhatsApp connection test error: {e}")
            return False

    async def _make_request(self, method: str, url: str, **kwargs) -> tuple[bool, dict[str, Any]]:
        """Make rate-limited API request"""
        if not await self.rate_limiter.acquire():
            self.stats["rate_limit_hits"] += 1
            wait_time = self.rate_limiter.reset_in()
            return False, {
                "error": "rate_limit_exceeded",
                "message": f"Rate limit exceeded. Try again in {wait_time} seconds",
                "retry_after": wait_time,
            }

        if not self.session:
            await self.initialize()

        try:
            async with self.session.request(method, url, **kwargs) as response:
                data = await response.json()

                if response.status in [200, 201]:
                    self.stats["last_activity"] = datetime.now().isoformat()
                    return True, data
                else:
                    logger.error(f"API request failed: {response.status} - {data}")
                    return False, {"error": "api_error", "status_code": response.status, "response": data}
        except Exception as e:
            logger.error(f"API request exception: {e}")
            return False, {"error": "request_failed", "message": str(e)}

    async def send_text_message(self, to: str, message: str, preview_url: bool = True) -> dict[str, Any]:
        """Send text message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": preview_url, "body": message},
        }

        success, result = await self._make_request("POST", self.messages_url, json=payload)

        if success:
            self.stats["messages_sent"] += 1
            logger.info(f"✅ Text message sent to {to}")
        else:
            self.stats["messages_failed"] += 1
            logger.error(f"❌ Failed to send text message to {to}")

        return {"status": "success" if success else "error", "to": to, "message_type": "text", "result": result}

    async def send_template_message(
        self, to: str, template_name: str, language_code: str = "en_US", parameters: list[dict] | None = None
    ) -> dict[str, Any]:
        """Send template message"""
        template_data = {"name": template_name, "language": {"code": language_code}}

        if parameters:
            template_data["components"] = [{"type": "body", "parameters": parameters}]

        payload = {"messaging_product": "whatsapp", "to": to, "type": "template", "template": template_data}

        success, result = await self._make_request("POST", self.messages_url, json=payload)

        if success:
            self.stats["messages_sent"] += 1
            logger.info(f"✅ Template message sent to {to}")
        else:
            self.stats["messages_failed"] += 1
            logger.error(f"❌ Failed to send template message to {to}")

        return {
            "status": "success" if success else "error",
            "to": to,
            "message_type": "template",
            "template_name": template_name,
            "result": result,
        }

    async def send_media_message(
        self, to: str, media_type: str, media_id: str, caption: str | None = None
    ) -> dict[str, Any]:
        """Send media message (image, document, audio, video)"""
        media_data = {"id": media_id}
        if caption and media_type in ["image", "video", "document"]:
            media_data["caption"] = caption

        payload = {"messaging_product": "whatsapp", "to": to, "type": media_type, media_type: media_data}

        success, result = await self._make_request("POST", self.messages_url, json=payload)

        if success:
            self.stats["messages_sent"] += 1
            logger.info(f"✅ Media message ({media_type}) sent to {to}")
        else:
            self.stats["messages_failed"] += 1
            logger.error(f"❌ Failed to send media message to {to}")

        return {
            "status": "success" if success else "error",
            "to": to,
            "message_type": media_type,
            "media_id": media_id,
            "result": result,
        }

    async def upload_media(self, media_path: str, media_type: str) -> dict[str, Any]:
        """Upload media file and get media ID"""
        if not os.path.exists(media_path):
            return {"status": "error", "error": "file_not_found", "message": f"Media file not found: {media_path}"}

        try:
            with open(media_path, "rb") as media_file:
                data = aiohttp.FormData()
                data.add_field("messaging_product", "whatsapp")
                data.add_field("type", media_type)
                data.add_field("file", media_file, filename=os.path.basename(media_path))

                # Remove Content-Type from session headers for multipart upload
                headers = {"Authorization": f"Bearer {self.token}"}

                async with self.session.post(self.media_url, data=data, headers=headers) as response:
                    result = await response.json()

                    if response.status in [200, 201]:
                        self.stats["media_uploads"] += 1
                        logger.info(f"✅ Media uploaded: {result.get('id')}")
                        return {"status": "success", "media_id": result.get("id"), "result": result}
                    else:
                        logger.error(f"❌ Media upload failed: {result}")
                        return {"status": "error", "error": "upload_failed", "result": result}
        except Exception as e:
            logger.error(f"Media upload exception: {e}")
            return {"status": "error", "error": "exception", "message": str(e)}

    async def get_media_url(self, media_id: str) -> dict[str, Any]:
        """Get downloadable URL for media"""
        url = f"{self.base_url}/{media_id}"

        success, result = await self._make_request("GET", url)

        return {"status": "success" if success else "error", "media_id": media_id, "result": result}

    async def mark_as_read(self, message_id: str) -> dict[str, Any]:
        """Mark message as read"""
        payload = {"messaging_product": "whatsapp", "status": "read", "message_id": message_id}

        success, result = await self._make_request("POST", self.messages_url, json=payload)

        return {"status": "success" if success else "error", "message_id": message_id, "result": result}

    def verify_webhook(self, mode: str, token: str, challenge: str) -> str | None:
        """Verify webhook subscription"""
        if mode == "subscribe" and token == self.webhook_verify_token:
            logger.info("✅ Webhook verified successfully")
            return challenge
        else:
            logger.error("❌ Webhook verification failed")
            return None

    async def process_webhook_message(self, webhook_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Process incoming webhook messages"""
        messages = []

        try:
            entry = webhook_data.get("entry", [])
            for entry_item in entry:
                changes = entry_item.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    webhook_messages = value.get("messages", [])

                    for msg in webhook_messages:
                        processed_msg = {
                            "id": msg.get("id"),
                            "from": msg.get("from"),
                            "timestamp": msg.get("timestamp"),
                            "type": msg.get("type"),
                            "content": self._extract_message_content(msg),
                        }
                        messages.append(processed_msg)

                        # Auto-mark as read
                        if msg.get("id"):
                            await self.mark_as_read(msg["id"])

            logger.info(f"Processed {len(messages)} webhook messages")

        except Exception as e:
            logger.error(f"Webhook processing error: {e}")

        return messages

    def _extract_message_content(self, message: dict[str, Any]) -> dict[str, Any]:
        """Extract content from webhook message based on type"""
        msg_type = message.get("type")

        if msg_type == "text":
            return {"text": message.get("text", {}).get("body", "")}
        elif msg_type == "image":
            return {
                "media_id": message.get("image", {}).get("id"),
                "caption": message.get("image", {}).get("caption", ""),
            }
        elif msg_type == "document":
            return {
                "media_id": message.get("document", {}).get("id"),
                "filename": message.get("document", {}).get("filename"),
                "caption": message.get("document", {}).get("caption", ""),
            }
        elif msg_type == "audio":
            return {"media_id": message.get("audio", {}).get("id")}
        elif msg_type == "video":
            return {
                "media_id": message.get("video", {}).get("id"),
                "caption": message.get("video", {}).get("caption", ""),
            }
        elif msg_type == "location":
            location = message.get("location", {})
            return {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "name": location.get("name"),
                "address": location.get("address"),
            }
        else:
            return {"raw": message}

    async def get_status(self) -> dict[str, Any]:
        """Get API status and statistics"""
        connection_status = await self.test_connection()

        return {
            "whatsapp_api_connected": connection_status,
            "phone_id": self.phone_id,
            "api_version": self.api_version,
            "rate_limit_remaining": self.rate_limiter.max_requests - len(self.rate_limiter.requests),
            "rate_limit_reset_in": self.rate_limiter.reset_in(),
            "statistics": self.stats.copy(),
        }

    def get_phone_number_format(self, number: str) -> str:
        """Format phone number for WhatsApp (remove + and spaces)"""
        return "".join(filter(str.isdigit, number))
