#!/usr/bin/env python3
"""
opena18 - CRM Agent
SSE Client Module - PORTIER 3.0 Compliant

Server-Sent Events Client für Dashboard Integration
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Callable, Awaitable

import aiohttp

logger = logging.getLogger("opena18.sse_client")


class SSEClient:
    """SSE-Client für Dashboard-Integration (opena20)"""
    
    def __init__(
        self,
        dashboard_url: str = "http://127.0.0.1:12349",
        bearer_token: Optional[str] = None,
        agent_id: str = "opena18",
        kuerzel: str = "crmp"
    ):
        self.dashboard_url = dashboard_url.rstrip("/")
        self.bearer_token = bearer_token or os.getenv("BEARER_TOKEN", "")
        self.agent_id = agent_id
        self.kuerzel = kuerzel
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy Session-Initialisierung"""
        if self._session is None or self._session.closed:
            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def close(self) -> None:
        """Schließt Session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        category: str = "crm"
    ) -> bool:
        """Publiziert Event an Dashboard SSE-Bus"""
        try:
            session = await self._get_session()
            payload = {
                "event_type": event_type,
                "category": category,
                "agent": self.agent_id,
                "kuerzel": self.kuerzel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data
            }
            url = f"{self.dashboard_url}/api/events/publish"
            
            async with session.post(url, json=payload, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"SSE Event published: {event_type}")
                    return True
                return False
        except Exception as e:
            logger.warning(f"SSE Event publish error: {e}")
            return False
    
    async def publish_contact_created(self, contact_id: str, email: str) -> bool:
        """Publiziert Contact-Created Event"""
        return await self.publish_event(
            "contact_created",
            {"contact_id": contact_id, "email": email}
        )
    
    async def publish_deal_updated(self, deal_id: str, stage: str, value: float) -> bool:
        """Publiziert Deal-Updated Event"""
        return await self.publish_event(
            "deal_updated",
            {"deal_id": deal_id, "stage": stage, "value": value}
        )
    
    async def publish_activity_logged(self, activity_id: str, activity_type: str) -> bool:
        """Publiziert Activity-Logged Event"""
        return await self.publish_event(
            "activity_logged",
            {"activity_id": activity_id, "type": activity_type}
        )


# Singleton
sse_client = SSEClient()
