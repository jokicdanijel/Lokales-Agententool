# 📱 WhatsApp Agent 6.0 - PORTIER PAS-6.0 (opena8)
# Advanced WhatsApp Business API Automation with AI Integration

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
try:
    from modules.whatsapp_core import WhatsAppCore
    from modules.whatsapp_api import WhatsAppAPI
    from modules.ai_reply_engine import AIReplyEngine
    from modules.metrics import Metrics
except ImportError as e:
    print(f"❌ Module import error: {e}")
    # Fallback for development
    WhatsAppCore = WhatsAppAPI = AIReplyEngine = Metrics = None

# Security
security = HTTPBearer()
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "fallback-token-whatsapp-6.0")

# Global instances
core: Optional[WhatsAppCore] = None
api: Optional[WhatsAppAPI] = None
ai_engine: Optional[AIReplyEngine] = None
metrics: Optional[Metrics] = None

# Pydantic Models für API
class WebhookVerification(BaseModel):
    """Webhook verification parameters"""
    hub_mode: str
    hub_challenge: str
    hub_verify_token: str

class SendMessageRequest(BaseModel):
    """Send message request"""
    to_phone: str
    body: str
    
class SendMediaRequest(BaseModel):
    """Send media request"""
    to_phone: str
    media_url: str
    media_type: str  # image, video, document, audio

# Storage für Nachrichten (temporär)
message_store = []

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "opena8",
        "component": "whatsapp",
        "port": config.PORT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/webhook")
async def webhook_verification(request: Request):
    """WhatsApp Webhook Verification (GET)"""
    try:
        # Extract query parameters
        hub_mode = request.query_params.get("hub.mode")
        hub_challenge = request.query_params.get("hub.challenge")
        hub_verify_token = request.query_params.get("hub.verify_token")
        
        logger.info(f"Webhook verification attempt: mode={hub_mode}, token={hub_verify_token}")
        
        # Verify token
        if (hub_mode == "subscribe" and 
            hub_verify_token == config.META_WEBHOOK_VERIFY_TOKEN):
            logger.info("✅ Webhook verification successful")
            return int(hub_challenge)
        else:
            logger.error("❌ Webhook verification failed - invalid token")
            raise HTTPException(status_code=403, detail="Invalid verify token")
            
    except Exception as e:
        logger.error(f"Webhook verification error: {e}")
        raise HTTPException(status_code=400, detail="Verification failed")

@app.post("/webhook")
async def webhook_handler(request: Request, background_tasks: BackgroundTasks):
    """WhatsApp Webhook Handler (POST)"""
    try:
        # Parse incoming webhook data
        webhook_data = await request.json()
        logger.info(f"Received webhook: {webhook_data}")
        
        # Verify webhook object type
        if webhook_data.get("object") != "whatsapp_business_account":
            logger.warning(f"Unknown webhook object: {webhook_data.get('object')}")
            return JSONResponse(content={"status": "ignored"})
        
        # Process each entry
        entries = webhook_data.get("entry", [])
        for entry in entries:
            # Schedule background processing
            background_tasks.add_task(process_webhook_entry, entry)
        
        return JSONResponse(content={"status": "received"})
        
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

async def process_webhook_entry(entry: Dict[str, Any]):
    """Process single webhook entry"""
    try:
        # Parse message from webhook entry
        message = await whatsapp_client.parse_webhook_event(entry)
        
        if not message:
            logger.warning("Could not parse message from webhook entry")
            return
        
        logger.info(f"📱 Received message: {message.message_id} from {message.phone_number}")
        
        # Store message
        message_store.append({
            "id": message.message_id,
            "phone": message.phone_number,
            "name": message.name,
            "body": message.body,
            "type": message.type.value,
            "sentiment": message.sentiment.value,
            "urgency": message.urgency,
            "language": message.language,
            "timestamp": message.timestamp.isoformat(),
            "status": message.status
        })
        
        # Archive to opena2 if configured
        if config.OPENA2_URL:
            await archive_message(message)
        
        # Auto-reply if enabled
        if config.AUTOREPLY_ENABLED and message.status == "allowed":
            await send_auto_reply(message)
            
        # Mark as read
        await whatsapp_client.mark_message_read(message.message_id)
        
    except Exception as e:
        logger.error(f"Webhook entry processing error: {e}")

async def archive_message(message: WhatsAppMessage):
    """Archive message to opena2"""
    try:
        import httpx
        
        archive_data = {
            "tool_name": "opena8_whatsapp",
            "input_data": {
                "message_id": message.message_id,
                "phone_number": message.phone_number,
                "name": message.name,
                "body": message.body,
                "type": message.type.value,
                "sentiment": message.sentiment.value,
                "urgency": message.urgency,
                "language": message.language
            },
            "output_data": {
                "processed_at": datetime.now().isoformat(),
                "status": message.status
            },
            "metadata": {
                "direction": "inbound",
                "timestamp": message.timestamp.isoformat()
            }
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{config.OPENA2_URL}/archiv/store",
                json=archive_data
            )
            
            if response.status_code == 200:
                logger.info(f"📁 Message {message.message_id} archived")
            else:
                logger.error(f"❌ Archive failed: {response.status_code}")
                
    except Exception as e:
        logger.error(f"Archive error: {e}")

async def send_auto_reply(message: WhatsAppMessage):
    """Send automatic reply"""
    try:
        # Simple auto-reply template
        reply_text = f"Hallo {message.name}! Ihre Nachricht wurde empfangen und wird bearbeitet. 🤖"
        
        success, msg_id, error = await whatsapp_client.send_message(
            message.phone_number,
            reply_text
        )
        
        if success:
            logger.info(f"📤 Auto-reply sent: {msg_id}")
        else:
            logger.error(f"❌ Auto-reply failed: {error}")
            
    except Exception as e:
        logger.error(f"Auto-reply error: {e}")

@app.post("/api/send-message")
async def send_message_api(request: SendMessageRequest):
    """Send WhatsApp message via API"""
    try:
        success, message_id, error = await whatsapp_client.send_message(
            request.to_phone,
            request.body
        )
        
        if success:
            return {
                "status": "sent",
                "message_id": message_id,
                "to_phone": request.to_phone
            }
        else:
            raise HTTPException(status_code=400, detail=f"Send failed: {error}")
            
    except Exception as e:
        logger.error(f"Send message API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/send-media")
async def send_media_api(request: SendMediaRequest):
    """Send WhatsApp media via API"""
    try:
        # Media sending not implemented yet - placeholder
        return {
            "status": "not_implemented", 
            "message": "Media sending coming soon",
            "to_phone": request.to_phone,
            "media_type": request.media_type
        }
            
    except Exception as e:
        logger.error(f"Send media API error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/messages")
async def get_messages():
    """Get received messages"""
    return {
        "total": len(message_store),
        "messages": message_store[-50:]  # Last 50 messages
    }

@app.get("/api/stats")
async def get_stats():
    """Get WhatsApp statistics"""
    total_messages = len(message_store)
    
    # Count by sentiment
    sentiment_counts = {}
    urgency_sum = 0
    
    for msg in message_store:
        sentiment = msg.get("sentiment", "neutral")
        sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        urgency_sum += msg.get("urgency", 5)
    
    avg_urgency = urgency_sum / total_messages if total_messages > 0 else 0
    
    return {
        "total_messages": total_messages,
        "sentiment_distribution": sentiment_counts,
        "average_urgency": round(avg_urgency, 1),
        "auto_reply_enabled": config.AUTOREPLY_ENABLED,
        "classification_enabled": config.ENABLE_CLASSIFICATION
    }

if __name__ == "__main__":
    logger.info(f"🚀 Starting opena8 WhatsApp Agent on port {config.PORT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=config.PORT,
        log_level=config.LOG_LEVEL.lower()
    )