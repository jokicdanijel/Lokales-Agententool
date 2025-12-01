import os
import httpx
from datetime import datetime, timezone

OPENA2_URL = os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "c899b90d-xxx")

class SafepointClient:
    """Safepoint-Client 3.0 – Remote Archivp Writer (für alle Agenten außer opena2)."""

    SECRET_KEYS = {"token", "auth", "password", "apikey", "key", "secret", "credentials", "bearer"}
    CATEGORIES = {"CMD", "RESP", "ROUTE", "DISPATCH"}

    @staticmethod
    def _mask(obj):
        if isinstance(obj, dict):
            return {
                k: ("***" if any(s in k.lower() for s in SafepointClient.SECRET_KEYS)
                    else SafepointClient._mask(v))
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [SafepointClient._mask(i) for i in obj]
        return obj

    @staticmethod
    async def write(category: str, source: str, destination: str, request_id: str, payload: dict):
        if category not in SafepointClient.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        iso = datetime.now(timezone.utc).isoformat()
        ts = int(datetime.now().timestamp())

        body = {
            "timestamp": iso,
            "sp_timestamp": ts,
            "source": source,
            "destination": destination,
            "category": category,
            "request_id": request_id,
            "payload": SafepointClient._mask(payload),
            "strict": True
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{OPENA2_URL}/store/{category}",
                json=body,
                headers={"Authorization": f"Bearer {BEARER_TOKEN}"},
                timeout=15.0,
            )
        return body


# Demo & Testing
if __name__ == "__main__":
    # Demo der Safepoint-Client Funktionalität
    client = SafepointClient("opena4_demo")
    
    print("🔥 PORTIER 3.0 Safepoint Client Demo")
    print("=" * 40)
    
    # CMD Safepoint
    cmd_file = client.write_cmd_safepoint("demo_req_001", {
        "command": "telegram_send",
        "message": "Hello Telegram",
        "token": "bot-secret-key"  # Wird maskiert
    })
    print(f"✓ CMD Safepoint: {cmd_file}")
    
    # RESP Safepoint
    resp_file = client.write_resp_safepoint("demo_req_001", {
        "success": True,
        "response": "Message sent successfully",
        "message_id": 12345
    })
    print(f"✓ RESP Safepoint: {resp_file}")
    
    # Statistiken
    stats = client.get_stats()
    print(f"✓ Stats: {stats}")
    
    # Konformitäts-Check
    compliance = client.validate_portier30_compliance()
    print(f"✓ PORTIER 3.0 Compliance: {all(compliance.values())}")