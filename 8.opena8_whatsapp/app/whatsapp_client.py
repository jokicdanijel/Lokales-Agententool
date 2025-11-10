"""
opena8 WhatsApp Client
Meta API integration, message parsing, classification
"""

import re
import json
import hashlib
from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime
import httpx

from app.config import config
from app.models import (
    MessageType, SentimentType, MediaType, MediaObject, WhatsAppMessage,
    MessageDirection, WebhookMessageEvent
)


class MessageClassifier:
    """Classify WhatsApp messages for sentiment, intent, language"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Detect language (DE/EN fallback)"""
        if not text:
            return "unknown"
        
        de_keywords = ["hallo", "guten", "danke", "bitte", "bitte", "wie", "wann"]
        en_keywords = ["hello", "hi", "thank", "please", "when", "what", "how"]
        
        text_lower = text.lower()
        de_count = sum(1 for kw in de_keywords if kw in text_lower)
        en_count = sum(1 for kw in en_keywords if kw in text_lower)
        
        if de_count > en_count:
            return "DE"
        elif en_count > 0:
            return "EN"
        return "unknown"
    
    @staticmethod
    def classify_sentiment(text: str) -> Tuple[SentimentType, int]:
        """Classify sentiment and urgency (0-10)"""
        if not config.ENABLE_SENTIMENT:
            return SentimentType.NEUTRAL, 5
        
        text_lower = text.lower() if text else ""
        
        # Check urgency first
        urgency_patterns = {
            r"urgent|asap|immediately|critical|help|emergency": 9,
            r"important|soon|high priority|needed": 7,
            r"normal|regular|standard": 5,
            r"when possible|no hurry": 2,
        }
        
        urgency = 5
        for pattern, score in urgency_patterns.items():
            if re.search(pattern, text_lower):
                urgency = score
                break
        
        # Sentiment patterns (URGENT prioritized)
        sentiment_patterns = {
            SentimentType.URGENT: r"urgent|emergency|help|critical|sos",
            SentimentType.POSITIVE: r"thank|great|excellent|happy|perfect|love|best",
            SentimentType.NEGATIVE: r"problem|issue|error|fail|upset|angry|hate|bad",
        }
        
        sentiment = SentimentType.NEUTRAL
        for sent, pattern in sentiment_patterns.items():
            if re.search(pattern, text_lower):
                sentiment = sent
                break
        
        return sentiment, urgency
    
    @staticmethod
    def check_allowlist(phone_number: str) -> bool:
        """Check phone against allowlist/blocklist"""
        if not phone_number:
            return False
        
        phone_lower = phone_number.lower()
        
        # Check allowlist (if defined)
        if config.WHATSAPP_ALLOWLIST:
            allowed = any(
                allowed.lower() in phone_lower or phone_lower.endswith(allowed.lower())
                for allowed in config.WHATSAPP_ALLOWLIST
            )
            if not allowed:
                return False
        
        # Check blocklist
        for blocked in config.WHATSAPP_BLOCKLIST:
            if blocked.lower() in phone_lower:
                return False
        
        return True


class MediaHandler:
    """Handle media downloads, storage, scanning"""
    
    @staticmethod
    def validate_media_size(size_bytes: int) -> bool:
        """Check media size limit"""
        max_bytes = config.MEDIA_MAX_SIZE_MB * 1024 * 1024
        return size_bytes <= max_bytes
    
    @staticmethod
    def calculate_sha256(data: bytes) -> str:
        """Calculate SHA256 of media"""
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    async def download_media(media_id: str, url: Optional[str]) -> Optional[bytes]:
        """Download media from Meta CDN"""
        if not url and not media_id:
            return None
        
        try:
            # If only media_id provided, construct Meta CDN URL
            if not url:
                url = f"https://graph.instagram.com/{media_id}"
                headers = {"Authorization": f"Bearer {config.META_ACCESS_TOKEN}"}
            else:
                headers = {"Authorization": f"Bearer {config.META_ACCESS_TOKEN}"}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return response.content
        except Exception as e:
            print(f"❌ Media download failed: {e}")
        
        return None


class WhatsAppClient:
    """Meta WhatsApp API client"""
    
    def __init__(self):
        self.base_url = f"https://graph.instagram.com/{config.META_API_VERSION}"
        self.phone_number_id = config.META_PHONE_NUMBER_ID
        self.access_token = config.META_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def parse_webhook_event(self, event_dict: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """Parse Meta webhook entry into WhatsAppMessage"""
        try:
            # Navigate webhook structure: entry[0] -> changes[0] -> value -> messages[0]
            changes = event_dict.get("changes", [])
            if not changes:
                return None
            
            value = changes[0].get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])
            
            if not messages:
                return None
            
            msg = messages[0]
            contact = contacts[0] if contacts else {}
            
            message_id = msg.get("id")
            phone_number = msg.get("from")
            timestamp = int(msg.get("timestamp", 0))
            msg_type_raw = msg.get("type", "text")
            
            # Determine message type and extract body
            msg_type = MessageType.TEXT
            body = None
            media = None
            
            if msg_type_raw == "text":
                msg_type = MessageType.TEXT
                body = msg.get("text", {}).get("body", "")
            elif msg_type_raw in ["image", "document", "audio", "video"]:
                msg_type = MessageType(msg_type_raw)
                obj = msg.get(msg_type_raw, {})
                media = MediaObject(
                    media_type=MediaType(msg_type_raw),
                    media_id=obj.get("id", ""),
                    mime_type=obj.get("mime_type", "application/octet-stream"),
                    caption=obj.get("caption", "")
                )
            
            # Classify message
            sentiment, urgency = MessageClassifier.classify_sentiment(body or "")
            language = MessageClassifier.detect_language(body or "")
            allowed = MessageClassifier.check_allowlist(phone_number)
            
            return WhatsAppMessage(
                message_id=message_id,
                phone_number=phone_number,
                name=contact.get("profile", {}).get("name", "Unknown"),
                timestamp=datetime.fromtimestamp(timestamp),
                direction=MessageDirection.INBOUND,
                type=msg_type,
                body=body,
                media=media,
                sentiment=sentiment,
                urgency=urgency,
                language=language,
                status="allowed" if allowed else "blocked"
            )
        except Exception as e:
            print(f"❌ Webhook parse failed: {e}")
            return None
    
    async def send_message(self, to_phone: str, body: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send text message via Meta API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": body}
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code in [200, 201]:
                    result = response.json()
                    return True, result.get("messages", [{}])[0].get("id"), None
                else:
                    return False, None, f"API error: {response.status_code}"
        except Exception as e:
            return False, None, str(e)
    
    async def send_media(self, to_phone: str, media_url: str, media_type: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send media message via Meta API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": media_type,
                media_type: {"link": media_url}
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                if response.status_code in [200, 201]:
                    result = response.json()
                    return True, result.get("messages", [{}])[0].get("id"), None
                else:
                    return False, None, f"API error: {response.status_code}"
        except Exception as e:
            return False, None, str(e)
    
    async def mark_message_read(self, message_id: str) -> bool:
        """Mark message as read"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload, headers=self.headers)
                return response.status_code in [200, 201]
        except Exception:
            return False
