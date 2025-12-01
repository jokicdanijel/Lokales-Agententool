# 📡 Telephony API - PORTIER PAS-6.0
# Twilio/SIP/Asterisk Integration Handler

import os
import logging
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CallStatus(Enum):
    """Call status enumeration"""
    QUEUED = "queued"
    RINGING = "ringing"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    BUSY = "busy"
    FAILED = "failed"
    NO_ANSWER = "no-answer"
    CANCELED = "canceled"

class CallDirection(Enum):
    """Call direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"

@dataclass
class CallRecord:
    """Call record structure"""
    call_id: str
    from_number: str
    to_number: str
    direction: CallDirection
    status: CallStatus
    duration: int = 0
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class TelephonyAPI:
    """Telephony API Handler - Twilio/SIP Integration"""
    
    def __init__(self):
        # Twilio configuration
        self.provider = os.getenv("TELEPHONY_PROVIDER", "twilio")
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER", "")
        
        # API endpoints
        self.twilio_base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"
        
        # Session for connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Active calls tracking
        self.active_calls: Dict[str, CallRecord] = {}
        
        # Statistics
        self.stats = {
            "calls_made": 0,
            "calls_answered": 0,
            "calls_failed": 0,
            "total_duration_seconds": 0,
            "last_activity": None
        }
    
    async def initialize(self):
        """Initialize HTTP session"""
        if self.account_sid and self.auth_token:
            auth = aiohttp.BasicAuth(self.account_sid, self.auth_token)
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                auth=auth
            )
            logger.info("✅ Telephony API initialized with Twilio")
        else:
            logger.warning("⚠️ Twilio credentials not configured - using mock mode")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_connection(self) -> bool:
        """Test Twilio API connection"""
        if not self.session or not self.account_sid:
            return False
        
        try:
            async with self.session.get(f"{self.twilio_base_url}.json") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Twilio connection test failed: {e}")
            return False
    
    async def make_call(self, to: str, script: str = "", caller_id: str = None) -> Dict[str, Any]:
        """Initiate outbound call via Twilio"""
        from_number = caller_id or self.phone_number
        
        if not from_number:
            return {"error": "No caller ID configured"}
        
        # Generate TwiML for the call
        twiml = self._generate_twiml(script) if script else "<Response><Say>Hello from Telephone Agent 6.0</Say></Response>"
        
        if self.session and self.account_sid:
            try:
                payload = {
                    "To": to,
                    "From": from_number,
                    "Twiml": twiml
                }
                
                async with self.session.post(
                    f"{self.twilio_base_url}/Calls.json",
                    data=payload
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        call_id = data.get("sid")
                        
                        # Track the call
                        self.active_calls[call_id] = CallRecord(
                            call_id=call_id,
                            from_number=from_number,
                            to_number=to,
                            direction=CallDirection.OUTBOUND,
                            status=CallStatus.QUEUED,
                            started_at=datetime.now()
                        )
                        
                        self.stats["calls_made"] += 1
                        self.stats["last_activity"] = datetime.now().isoformat()
                        
                        logger.info(f"✅ Call initiated: {call_id}")
                        
                        return {
                            "status": "success",
                            "call_id": call_id,
                            "to": to,
                            "from": from_number,
                            "provider": "twilio",
                            "timestamp": datetime.now().isoformat()
                        }
                    else:
                        error = await response.text()
                        self.stats["calls_failed"] += 1
                        logger.error(f"❌ Call failed: {error}")
                        return {"error": f"Twilio API error: {response.status}", "details": error}
                        
            except Exception as e:
                self.stats["calls_failed"] += 1
                logger.error(f"Call initiation failed: {e}")
                return {"error": str(e)}
        
        # Mock response for development
        call_id = f"mock_call_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "status": "queued",
            "call_id": call_id,
            "to": to,
            "from": from_number,
            "provider": "mock",
            "note": "Twilio credentials not configured",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_twiml(self, script: str) -> str:
        """Generate TwiML from script text"""
        # Simple TwiML generation - can be enhanced for IVR flows
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice" language="de-DE">{script}</Say>
</Response>"""
    
    async def answer_call(self, call_id: str) -> Dict[str, Any]:
        """Answer incoming call"""
        if call_id in self.active_calls:
            self.active_calls[call_id].status = CallStatus.IN_PROGRESS
            self.stats["calls_answered"] += 1
        
        return {
            "call_id": call_id,
            "action": "answer_call",
            "status": "accepted",
            "timestamp": datetime.now().isoformat()
        }
    
    async def hangup(self, call_id: str) -> Dict[str, Any]:
        """End call"""
        if self.session and self.account_sid and call_id.startswith("CA"):
            try:
                payload = {"Status": "completed"}
                async with self.session.post(
                    f"{self.twilio_base_url}/Calls/{call_id}.json",
                    data=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"✅ Call ended: {call_id}")
            except Exception as e:
                logger.error(f"Hangup failed: {e}")
        
        if call_id in self.active_calls:
            call = self.active_calls[call_id]
            call.status = CallStatus.COMPLETED
            call.ended_at = datetime.now()
            if call.started_at:
                call.duration = int((call.ended_at - call.started_at).total_seconds())
                self.stats["total_duration_seconds"] += call.duration
        
        return {
            "call_id": call_id,
            "action": "hangup",
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }
    
    async def call_status(self, call_id: str) -> Dict[str, Any]:
        """Get call status"""
        if self.session and self.account_sid and call_id.startswith("CA"):
            try:
                async with self.session.get(
                    f"{self.twilio_base_url}/Calls/{call_id}.json"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "call_id": call_id,
                            "status": data.get("status"),
                            "direction": data.get("direction"),
                            "duration": data.get("duration"),
                            "from": data.get("from"),
                            "to": data.get("to"),
                            "start_time": data.get("start_time"),
                            "end_time": data.get("end_time")
                        }
            except Exception as e:
                logger.error(f"Status check failed: {e}")
        
        # Check local tracking
        if call_id in self.active_calls:
            call = self.active_calls[call_id]
            return {
                "call_id": call_id,
                "status": call.status.value,
                "direction": call.direction.value,
                "duration": call.duration,
                "from": call.from_number,
                "to": call.to_number,
                "started_at": call.started_at.isoformat() if call.started_at else None
            }
        
        return {
            "call_id": call_id,
            "status": "unknown",
            "timestamp": datetime.now().isoformat()
        }
    
    async def send_dtmf(self, call_id: str, digits: str) -> Dict[str, Any]:
        """Send DTMF tones during call"""
        if self.session and self.account_sid and call_id.startswith("CA"):
            try:
                twiml = f'<Response><Play digits="{digits}"/></Response>'
                payload = {"Twiml": twiml}
                async with self.session.post(
                    f"{self.twilio_base_url}/Calls/{call_id}.json",
                    data=payload
                ) as response:
                    if response.status == 200:
                        return {
                            "call_id": call_id,
                            "action": "send_dtmf",
                            "digits": digits,
                            "status": "sent"
                        }
            except Exception as e:
                logger.error(f"DTMF send failed: {e}")
        
        return {
            "call_id": call_id,
            "action": "send_dtmf",
            "digits": digits,
            "status": "sent",
            "provider": "mock"
        }
    
    async def play_audio(self, call_id: str, audio_url: str) -> Dict[str, Any]:
        """Play audio file during call"""
        if self.session and self.account_sid and call_id.startswith("CA"):
            try:
                twiml = f'<Response><Play>{audio_url}</Play></Response>'
                payload = {"Twiml": twiml}
                async with self.session.post(
                    f"{self.twilio_base_url}/Calls/{call_id}.json",
                    data=payload
                ) as response:
                    if response.status == 200:
                        return {
                            "call_id": call_id,
                            "action": "play_audio",
                            "audio_url": audio_url,
                            "status": "playing"
                        }
            except Exception as e:
                logger.error(f"Play audio failed: {e}")
        
        return {
            "call_id": call_id,
            "action": "play_audio",
            "audio_url": audio_url,
            "status": "playing",
            "provider": "mock"
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get API status and statistics"""
        connection_status = await self.test_connection()
        
        return {
            "telephony_api_connected": connection_status,
            "provider": self.provider,
            "phone_number": self.phone_number[:6] + "****" if self.phone_number else "not_configured",
            "active_calls": len(self.active_calls),
            "statistics": self.stats.copy()
        }
    
    async def get_call_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent call history"""
        if self.session and self.account_sid:
            try:
                async with self.session.get(
                    f"{self.twilio_base_url}/Calls.json?PageSize={limit}"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("calls", [])
            except Exception as e:
                logger.error(f"Call history retrieval failed: {e}")
        
        # Return local history
        return [
            {
                "call_id": call.call_id,
                "from": call.from_number,
                "to": call.to_number,
                "status": call.status.value,
                "duration": call.duration
            }
            for call in list(self.active_calls.values())[-limit:]
        ]
