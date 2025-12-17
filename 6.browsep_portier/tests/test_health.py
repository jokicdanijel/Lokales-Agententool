import httpx
import asyncio

async def test_health_endpoint():
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get("http://127.0.0.1:12370/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
