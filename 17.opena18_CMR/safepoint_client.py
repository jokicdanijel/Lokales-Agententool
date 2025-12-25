import os
from datetime import UTC, datetime

import httpx

OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-xxx")


class SafepointClient:
    """Safepoint-Client 3.0 für opena18 (CMR/CRM-Agent)."""

    @staticmethod
    async def write(category: str, source: str, destination: str, request_id: str, payload: dict):
        iso = datetime.now(UTC).isoformat()
        ts = int(datetime.now().timestamp())

        def mask(obj):
            if isinstance(obj, dict):
                return {
                    k: ("***" if k.lower() in ["token", "auth", "password", "apikey", "secret", "key"] else mask(v))
                    for k, v in obj.items()
                }
            if isinstance(obj, list):
                return [mask(i) for i in obj]
            return obj

        body = {
            "timestamp": iso,
            "sp_timestamp": ts,
            "source": source,
            "destination": destination,
            "category": category,
            "request_id": request_id,
            "payload": mask(payload),
            "strict": True,
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{OPENA2_URL}/store/{category}",
                json=body,
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                timeout=15.0,
            )
        return body
