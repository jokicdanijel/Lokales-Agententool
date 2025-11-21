"""
SIP Client und Call Manager für opena9
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.config import config
from app.models import CallRecord, CallDirection, CallStatus, SIPAccount

logger = logging.getLogger("opena9.sip")


class SIPClient:
    """SIP Protocol Client für VoIP-Kommunikation"""
    
    def __init__(self):
        self.account = SIPAccount(
            username=config.SIP_USERNAME,
            password=config.SIP_PASSWORD,
            server=config.SIP_SERVER,
            port=config.SIP_PORT,
            domain=config.SIP_DOMAIN
        )
        self.is_connected = False
        self.registration_status = "disconnected"
    
    async def connect(self) -> bool:
        """Verbindung zum SIP-Server herstellen"""
        try:
            logger.info(f"🔌 Connecting to SIP server: {self.account.server}:{self.account.port}")
            
            # Simuliere SIP-Verbindung
            # In echter Implementierung: SIP REGISTER senden
            await asyncio.sleep(1)  # Simuliere Netzwerk-Delay
            
            self.is_connected = True
            self.registration_status = "registered"
            
            logger.info("✅ SIP client connected and registered")
            return True
            
        except Exception as e:
            logger.error(f"❌ SIP connection failed: {e}")
            self.is_connected = False
            self.registration_status = "failed"
            return False
    
    async def disconnect(self) -> bool:
        """SIP-Verbindung trennen"""
        try:
            if self.is_connected:
                # Simuliere SIP UNREGISTER
                await asyncio.sleep(0.5)
                
                self.is_connected = False
                self.registration_status = "disconnected"
                
                logger.info("🔌 SIP client disconnected")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ SIP disconnect failed: {e}")
            return False
    
    async def send_invite(self, to_number: str, caller_id: str) -> Optional[str]:
        """SIP INVITE senden (Anruf initiieren)"""
        try:
            if not self.is_connected:
                await self.connect()
            
            call_id = str(uuid.uuid4())
            
            logger.info(f"📞 Sending SIP INVITE: {caller_id} → {to_number} (Call ID: {call_id})")
            
            # Simuliere SIP INVITE/Session Setup
            await asyncio.sleep(0.5)
            
            # Simuliere erfolgreichen Call-Setup
            return call_id
            
        except Exception as e:
            logger.error(f"❌ SIP INVITE failed: {e}")
            return None
    
    async def send_bye(self, call_id: str) -> bool:
        """SIP BYE senden (Anruf beenden)"""
        try:
            logger.info(f"📴 Sending SIP BYE for call: {call_id}")
            
            # Simuliere SIP BYE
            await asyncio.sleep(0.2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ SIP BYE failed: {e}")
            return False
    
    async def answer_call(self, call_id: str) -> bool:
        """Anruf annehmen (SIP 200 OK)"""
        try:
            logger.info(f"✅ Answering call: {call_id}")
            
            # Simuliere SIP 200 OK
            await asyncio.sleep(0.2)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Answer call failed: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """SIP-Client Status abrufen"""
        return {
            "connected": self.is_connected,
            "registration_status": self.registration_status,
            "server": f"{self.account.server}:{self.account.port}",
            "username": self.account.username,
            "domain": self.account.domain
        }


class CallManager:
    """Call Management und Audio-Handling"""
    
    def __init__(self):
        self.sip_client = SIPClient()
        self.active_calls: Dict[str, CallRecord] = {}
        self.call_limits_reached = False
    
    async def initiate_call(self, to_number: str, caller_id: str, duration_limit: int = 300) -> Optional[str]:
        """Ausgehenden Anruf initiieren"""
        try:
            # Prüfe Concurrent Call Limit
            if len(self.active_calls) >= config.MAX_CONCURRENT_CALLS:
                logger.warning(f"⚠️ Max concurrent calls reached: {config.MAX_CONCURRENT_CALLS}")
                return None
            
            # Prüfe Blocked Numbers
            if to_number in config.BLOCKED_NUMBERS:
                logger.warning(f"⚠️ Number blocked: {to_number}")
                return None
            
            # SIP INVITE senden
            call_id = await self.sip_client.send_invite(to_number, caller_id)
            
            if call_id:
                # Call Record erstellen
                call_record = CallRecord(
                    call_id=call_id,
                    from_number=caller_id,
                    to_number=to_number,
                    direction=CallDirection.OUTBOUND,
                    status=CallStatus.INITIATED,
                    started_at=datetime.now(),
                    caller_id=caller_id
                )
                
                self.active_calls[call_id] = call_record
                
                # Schedule automatic hangup
                asyncio.create_task(self._auto_hangup(call_id, duration_limit))
                
                logger.info(f"📞 Outbound call initiated: {call_id}")
                return call_id
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Call initiation failed: {e}")
            return None
    
    async def answer_call(self, call_id: str) -> bool:
        """Eingehenden Anruf annehmen"""
        try:
            if call_id not in self.active_calls:
                logger.error(f"❌ Call not found: {call_id}")
                return False
            
            success = await self.sip_client.answer_call(call_id)
            
            if success:
                self.active_calls[call_id].status = CallStatus.ACTIVE
                logger.info(f"✅ Call answered: {call_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Answer call failed: {e}")
            return False
    
    async def hangup_call(self, call_id: str) -> bool:
        """Anruf beenden"""
        try:
            if call_id not in self.active_calls:
                logger.error(f"❌ Call not found: {call_id}")
                return False
            
            success = await self.sip_client.send_bye(call_id)
            
            if success:
                call_record = self.active_calls[call_id]
                call_record.status = CallStatus.ENDED
                call_record.ended_at = datetime.now()
                
                if call_record.started_at:
                    duration = call_record.ended_at - call_record.started_at
                    call_record.duration_seconds = int(duration.total_seconds())
                
                logger.info(f"📴 Call ended: {call_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Hangup failed: {e}")
            return False
    
    async def control_call(self, call_id: str, action: str) -> bool:
        """Anruf kontrollieren (hold, unhold, etc.)"""
        try:
            if call_id not in self.active_calls:
                logger.error(f"❌ Call not found: {call_id}")
                return False
            
            call_record = self.active_calls[call_id]
            
            if action == "hold":
                call_record.status = CallStatus.HELD
                logger.info(f"⏸️ Call on hold: {call_id}")
            elif action == "unhold":
                call_record.status = CallStatus.ACTIVE
                logger.info(f"▶️ Call resumed: {call_id}")
            elif action == "mute":
                # Implementiere Mute-Logik
                logger.info(f"🔇 Call muted: {call_id}")
            elif action == "unmute":
                # Implementiere Unmute-Logik
                logger.info(f"🔊 Call unmuted: {call_id}")
            else:
                logger.warning(f"⚠️ Unknown action: {action}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Call control failed: {e}")
            return False
    
    async def transfer_call(self, call_id: str, target_number: str) -> bool:
        """Anruf weiterleiten"""
        try:
            if call_id not in self.active_calls:
                logger.error(f"❌ Call not found: {call_id}")
                return False
            
            call_record = self.active_calls[call_id]
            call_record.status = CallStatus.TRANSFERRING
            
            logger.info(f"🔀 Transferring call {call_id} to {target_number}")
            
            # Simuliere Call Transfer
            await asyncio.sleep(1)
            
            # Transfer erfolgreich - Call aus aktiver Liste entfernen
            call_record.status = CallStatus.ENDED
            call_record.ended_at = datetime.now()
            
            logger.info(f"✅ Call transferred: {call_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Call transfer failed: {e}")
            return False
    
    async def _auto_hangup(self, call_id: str, duration_limit: int):
        """Automatisches Beenden nach Zeitlimit"""
        try:
            await asyncio.sleep(duration_limit)
            
            if call_id in self.active_calls:
                logger.warning(f"⏰ Auto-hangup triggered for call: {call_id}")
                await self.hangup_call(call_id)
                
        except asyncio.CancelledError:
            # Task wurde abgebrochen (normaler Call-End)
            pass
        except Exception as e:
            logger.error(f"❌ Auto-hangup error: {e}")
    
    async def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Status eines spezifischen Anrufs abrufen"""
        if call_id not in self.active_calls:
            return None
        
        call_record = self.active_calls[call_id]
        
        duration = 0
        if call_record.started_at:
            end_time = call_record.ended_at or datetime.now()
            duration = (end_time - call_record.started_at).total_seconds()
        
        return {
            "call_id": call_id,
            "from_number": call_record.from_number,
            "to_number": call_record.to_number,
            "direction": call_record.direction.value,
            "status": call_record.status.value,
            "started_at": call_record.started_at.isoformat(),
            "duration": duration
        }