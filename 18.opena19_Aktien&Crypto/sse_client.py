#!/usr/bin/env python3
"""
opena19 - Stocks & Crypto Agent
SSE Client Module - PORTIER 3.0 Compliant

Server-Sent Events Client für Dashboard Integration
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import aiohttp

logger = logging.getLogger("opena19.sse_client")


class SSEClient:
    """SSE-Client für Dashboard-Integration (opena20)"""
    
    def __init__(
        self,
        dashboard_url: str = "http://127.0.0.1:12349",
        bearer_token: Optional[str] = None,
        agent_id: str = "opena19",
        kuerzel: str = "stockcryptop"
    ):
        self.dashboard_url = dashboard_url.rstrip("/")
        self.bearer_token = bearer_token or os.getenv("BEARER_TOKEN", "")
        self.agent_id = agent_id
        self.kuerzel = kuerzel
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            headers = {}
            if self.bearer_token:
                headers["Authorization"] = f"Bearer {self.bearer_token}"
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session
    
    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        category: str = "stocks_crypto"
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
                return response.status == 200
        except Exception as e:
            logger.warning(f"SSE Event publish error: {e}")
            return False
    
    async def publish_price_update(
        self,
        symbol: str,
        market: str,
        price: float,
        change_percent: Optional[float] = None
    ) -> bool:
        """Publiziert Preis-Update Event"""
        return await self.publish_event(
            "price_update",
            {
                "symbol": symbol,
                "market": market,
                "price": price,
                "change_percent": change_percent
            }
        )
    
    async def publish_alert_triggered(
        self,
        alert_id: str,
        symbol: str,
        condition: str,
        current_price: float,
        threshold: float
    ) -> bool:
        """Publiziert Alert-Triggered Event"""
        return await self.publish_event(
            "alert_triggered",
            {
                "alert_id": alert_id,
                "symbol": symbol,
                "condition": condition,
                "current_price": current_price,
                "threshold": threshold
            },
            category="alerts"
        )
    
    async def publish_portfolio_update(
        self,
        total_value: float,
        total_pnl: float,
        total_pnl_percent: float
    ) -> bool:
        """Publiziert Portfolio-Update Event"""
        return await self.publish_event(
            "portfolio_update",
            {
                "total_value": total_value,
                "total_pnl": total_pnl,
                "total_pnl_percent": total_pnl_percent
            }
        )


# Singleton
sse_client = SSEClient()
