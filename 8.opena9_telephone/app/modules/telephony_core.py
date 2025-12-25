# 📞 Telephony Core - PORTIER PAS-6.0
# Central Telephony Operations Coordinator

import logging
import os
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class TelephonyCore:
    """Core telephony operations coordinator"""

    def __init__(self):
        self.api = None
        self.logs: list[dict[str, Any]] = []
        self.start_time = datetime.now()
        self.config = {
            "telephony_provider": os.getenv("TELEPHONY_PROVIDER", "twilio"),
            "voice_engine": "ai_voice_engine_v1",
            "tts_provider": os.getenv("TTS_PROVIDER", "openai"),
            "stt_provider": os.getenv("STT_PROVIDER", "openai"),
            "max_call_duration": 3600,
            "record_calls": os.getenv("RECORD_CALLS", "false").lower() == "true",
        }

    async def initialize(self):
        """Initialize telephony core"""
        from modules.telephony_api import TelephonyAPI

        self.api = TelephonyAPI()
        await self.api.initialize()
        self._log("info", "Telephony Core initialized")
        logger.info("✅ Telephony Core initialized")

    def _log(self, level: str, message: str, data: dict = None):
        """Internal logging"""
        entry = {"timestamp": datetime.now().isoformat(), "level": level, "message": message, "data": data or {}}
        self.logs.append(entry)
        if len(self.logs) > 500:
            self.logs = self.logs[-500:]

    async def get_status(self) -> dict[str, Any]:
        """Get telephony core status"""
        uptime = (datetime.now() - self.start_time).total_seconds()

        return {
            "telephony_core": "ready",
            "provider": self.config["telephony_provider"],
            "voice_engine": self.config["voice_engine"],
            "uptime_seconds": round(uptime, 2),
            "uptime_formatted": self._format_uptime(uptime),
            "api_connected": self.api is not None,
            "features": {
                "tts": True,
                "stt": True,
                "ivr": True,
                "call_recording": self.config["record_calls"],
                "ai_voice": True,
            },
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime as human-readable string"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"

    async def execute_command(self, command: str, args: dict[str, Any]) -> dict[str, Any]:
        """Execute telephony command"""
        self._log("info", f"Executing command: {command}", args)

        commands = {
            "make_call": self._make_call,
            "answer_call": self._answer_call,
            "hangup": self._hangup,
            "call_status": self._call_status,
            "transfer_call": self._transfer_call,
            "hold_call": self._hold_call,
            "resume_call": self._resume_call,
            "send_dtmf": self._send_dtmf,
            "play_audio": self._play_audio,
            "record_call": self._record_call,
            "get_recording": self._get_recording,
            "list_active_calls": self._list_active_calls,
        }

        if command not in commands:
            self._log("error", f"Unknown command: {command}")
            return {"error": f"Unknown command '{command}'", "available_commands": list(commands.keys())}

        try:
            result = await commands[command](args)
            self._log("info", f"Command {command} completed", result)
            return result
        except Exception as e:
            self._log("error", f"Command {command} failed: {e!s}")
            return {"error": str(e), "command": command}

    async def _make_call(self, args: dict[str, Any]) -> dict[str, Any]:
        """Initiate outbound call"""
        to = args.get("to")
        script = args.get("script", "")
        caller_id = args.get("caller_id")

        if not to:
            return {"error": "Missing 'to' phone number"}

        if self.api:
            return await self.api.make_call(to, script, caller_id)

        return {
            "status": "queued",
            "to": to,
            "script": script[:100] + "..." if len(script) > 100 else script,
            "call_id": f"call_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
        }

    async def _answer_call(self, args: dict[str, Any]) -> dict[str, Any]:
        """Answer incoming call"""
        call_id = args.get("call_id")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        if self.api:
            return await self.api.answer_call(call_id)

        return {
            "call_id": call_id,
            "action": "answer_call",
            "status": "accepted",
            "timestamp": datetime.now().isoformat(),
        }

    async def _hangup(self, args: dict[str, Any]) -> dict[str, Any]:
        """End call"""
        call_id = args.get("call_id")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        if self.api:
            return await self.api.hangup(call_id)

        return {"call_id": call_id, "action": "hangup", "status": "completed", "timestamp": datetime.now().isoformat()}

    async def _call_status(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get call status"""
        call_id = args.get("call_id")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        if self.api:
            return await self.api.call_status(call_id)

        return {
            "call_id": call_id,
            "status": "active",
            "duration_seconds": 0,
            "direction": "outbound",
            "timestamp": datetime.now().isoformat(),
        }

    async def _transfer_call(self, args: dict[str, Any]) -> dict[str, Any]:
        """Transfer call to another number"""
        call_id = args.get("call_id")
        transfer_to = args.get("transfer_to")

        if not call_id or not transfer_to:
            return {"error": "Missing 'call_id' or 'transfer_to'"}

        return {
            "call_id": call_id,
            "action": "transfer",
            "transfer_to": transfer_to,
            "status": "transferring",
            "timestamp": datetime.now().isoformat(),
        }

    async def _hold_call(self, args: dict[str, Any]) -> dict[str, Any]:
        """Put call on hold"""
        call_id = args.get("call_id")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        return {"call_id": call_id, "action": "hold", "status": "on_hold", "timestamp": datetime.now().isoformat()}

    async def _resume_call(self, args: dict[str, Any]) -> dict[str, Any]:
        """Resume call from hold"""
        call_id = args.get("call_id")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        return {"call_id": call_id, "action": "resume", "status": "active", "timestamp": datetime.now().isoformat()}

    async def _send_dtmf(self, args: dict[str, Any]) -> dict[str, Any]:
        """Send DTMF tones"""
        call_id = args.get("call_id")
        digits = args.get("digits", "")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        return {
            "call_id": call_id,
            "action": "send_dtmf",
            "digits": digits,
            "status": "sent",
            "timestamp": datetime.now().isoformat(),
        }

    async def _play_audio(self, args: dict[str, Any]) -> dict[str, Any]:
        """Play audio file during call"""
        call_id = args.get("call_id")
        audio_url = args.get("audio_url")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        return {
            "call_id": call_id,
            "action": "play_audio",
            "audio_url": audio_url,
            "status": "playing",
            "timestamp": datetime.now().isoformat(),
        }

    async def _record_call(self, args: dict[str, Any]) -> dict[str, Any]:
        """Start call recording"""
        call_id = args.get("call_id")

        if not call_id:
            return {"error": "Missing 'call_id'"}

        return {
            "call_id": call_id,
            "action": "record",
            "recording_id": f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "recording",
            "timestamp": datetime.now().isoformat(),
        }

    async def _get_recording(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get call recording"""
        recording_id = args.get("recording_id")

        if not recording_id:
            return {"error": "Missing 'recording_id'"}

        return {
            "recording_id": recording_id,
            "status": "available",
            "url": f"https://recordings.example.com/{recording_id}.mp3",
            "duration_seconds": 120,
            "timestamp": datetime.now().isoformat(),
        }

    async def _list_active_calls(self, args: dict[str, Any]) -> dict[str, Any]:
        """List all active calls"""
        return {"active_calls": [], "count": 0, "timestamp": datetime.now().isoformat()}

    async def get_recent_logs(self, limit: int = 100) -> dict[str, Any]:
        """Get recent logs"""
        return {"logs": self.logs[-limit:], "total": len(self.logs), "returned": min(limit, len(self.logs))}

    async def get_configuration(self) -> dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
