"""
OpenA3 Client für PORTIER 3.0
Async HTTP Client mit Bearer Authentication
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime

from .models import (
    CMDRequest,
    ChatRequest, 
    HealthResponse,
    DispatchStatus,
    SelfTestResult
)

class OpenA3Client:
    """Async Client for OpenWebUI Agent V2"""
    
    def __init__(
        self, 
        base_url: str = "http://127.0.0.1:12347",
        token: Optional[str] = None,
        timeout: float = 30.0,
        retries: int = 3
    ):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        self.retries = retries
        
        # Headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "OpenA3-SDK/2.0.0"
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        
        # HTTP Client
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers=self.headers,
            follow_redirects=True
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    async def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Internal request method with retry logic"""
        url = f"{self.base_url}{path}"
        
        for attempt in range(self.retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if attempt == self.retries:
                    return {
                        "error": f"HTTP {e.response.status_code}: {e.response.text}",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
            except Exception as e:
                if attempt == self.retries:
                    return {
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
    
    async def health(self) -> HealthResponse:
        """Health check endpoint"""
        data = await self._request("GET", "/health")
        return HealthResponse.parse_obj(data)
    
    async def native_chat(self, request: ChatRequest) -> Dict[str, Any]:
        """Native chat endpoint"""
        return await self._request(
            "POST", 
            "/native",
            json=request.dict()
        )
    
    async def chat(self, prompt: str, model: str = "gpt-4", **kwargs) -> Dict[str, Any]:
        """Simplified chat method"""
        request = ChatRequest(prompt=prompt, model=model, **kwargs)
        return await self.native_chat(request)
    
    async def cmd_dispatch(self, request: CMDRequest) -> Dict[str, Any]:
        """CMD dispatch via Option-2-Flow"""
        return await self._request(
            "POST",
            "/cmd", 
            json=request.dict()
        )
    
    async def dispatch_ready(self) -> DispatchStatus:
        """Check dispatch ready status"""
        data = await self._request("GET", "/dispatch_ready")
        return DispatchStatus.parse_obj(data)
    
    async def selftest(self) -> SelfTestResult:
        """Run system self-test"""
        data = await self._request("GET", "/selftest")
        return SelfTestResult.parse_obj(data)
    
    # Helper methods
    def create_cmd_request(
        self,
        command: str,
        payload: Dict[str, Any],
        source: str = "sdk"
    ) -> CMDRequest:
        """Helper to create CMD request"""
        return CMDRequest(
            request_id=f"sdk-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            source=source,
            command=command,
            payload=payload
        )