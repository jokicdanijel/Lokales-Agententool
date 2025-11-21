"""
opena8 WhatsApp Client - Meta API Integration
Lean & Mean Implementation
"""

import re
import hashlib
from typing import Optional, Dict, Any, TypedDict, Tuple
from datetime import datetime
import httpx
from app.config import config
from app.models import MessageType, SentimentType, MediaType, MediaObject, WhatsAppMessage, MessageDirection

# Type-safe JSON structures
class ContactDict(TypedDict, total=False):
    """WhatsApp contact structure"""
    name: str
    phone: str
    wa_id: str
    profile: Dict[str, str]

class WebhookPayload(TypedDict, total=False):
    """WhatsApp webhook payload structure"""
    object: str
    entry: list[Dict[str, Any]]

class MessageClassifier:
    """Message classification ohne externe Dependencies"""
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple DE/EN detection"""
        if not text:
            return "unknown"
        
        de_words = ["hallo", "danke", "bitte", "wie", "wann", "ich", "das", "ist"]
        en_words = ["hello", "thank", "please", "how", "when", "the", "this", "is"]
        
        text_lower = text.lower()
        de_count = sum(1 for word in de_words if word in text_lower)
        en_count = sum(1 for word in en_words if word in text_lower)
        
        return "DE" if de_count > en_count else ("EN" if en_count > 0 else "unknown")
    
    @staticmethod
    def classify_sentiment(text: str) -> Tuple[SentimentType, int]:
        """Basic sentiment + urgency (0-10)"""
        if not config.ENABLE_SENTIMENT:
            return SentimentType.NEUTRAL, 5
        
        text_lower = text.lower() if text else ""
        
        # Urgency patterns
        urgency_patterns = {
            r"urgent|asap|emergency|critical|hilfe": 9,
            r"important|soon|wichtig": 7,
            r"normal|regular": 5,
            r"no hurry|kein stress": 2,
        }
        
        urgency = 5
        for pattern, score in urgency_patterns.items():
            if re.search(pattern, text_lower):
                urgency = score
                break
        
        # Sentiment patterns
        if re.search(r"urgent|emergency|hilfe|problem", text_lower):
            return SentimentType.URGENT, urgency
        elif re.search(r"thank|great|super|danke|toll", text_lower):
            return SentimentType.POSITIVE, urgency
        elif re.search(r"problem|error|schlecht|ärger", text_lower):
            return SentimentType.NEGATIVE, urgency
        
        return SentimentType.NEUTRAL, urgency

class WhatsAppClient:
    """Meta WhatsApp Business API Client"""
    
    def __init__(self):
        self.base_url = f"https://graph.facebook.com/{config.META_API_VERSION}"
        self.phone_number_id = config.META_PHONE_NUMBER_ID
        self.access_token = config.META_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def parse_webhook_event(self, event_dict: Dict[str, Any]) -> Optional[WhatsAppMessage]:
        """Parse Meta webhook entry into WhatsAppMessage"""
        try:
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
            
            message_id = msg.get("id", "")
            phone_number = msg.get("from", "")
            timestamp = int(msg.get("timestamp", 0))
            msg_type_raw = msg.get("type", "text")
            
            # Extract message body
            body = None
            media = None
            
            if msg_type_raw == "text":
                body = msg.get("text", {}).get("body", "")
            elif msg_type_raw in ["image", "document", "audio", "video"]:
                obj = msg.get(msg_type_raw, {})
                body = obj.get("caption", "")
                media = MediaObject(
                    media_type=MediaType(msg_type_raw),
                    media_id=obj.get("id", ""),
                    mime_type=obj.get("mime_type", "application/octet-stream"),
                    caption=body
                )
            
            # Classify message
            sentiment, urgency = MessageClassifier.classify_sentiment(body or "")
            language = MessageClassifier.detect_language(body or "")
            
            return WhatsAppMessage(
                message_id=message_id,
                phone_number=phone_number,
                name=contact.get("profile", {}).get("name", "Unknown"),
                timestamp=datetime.fromtimestamp(timestamp),
                direction=MessageDirection.INBOUND,
                type=MessageType.TEXT if msg_type_raw == "text" else MessageType(msg_type_raw),
                body=body,
                media=media,
                sentiment=sentiment,
                urgency=urgency,
                language=language,
                status="received"
            )
            
        except Exception as e:
            print(f"❌ Webhook parse error: {e}")
            return None
    
    async def send_message(self, to_phone: str, body: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Send WhatsApp text message"""
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
                    msg_id = result.get("messages", [{}])[0].get("id", "")
                    return True, msg_id, None
                else:
                    return False, None, f"HTTP {response.status_code}: {response.text}"
                    
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