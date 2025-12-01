#!/usr/bin/env python3
"""
Register Pool Services (Agent17-20) with Portier (12344)
Automates service registration via /route/update endpoint.
"""

import asyncio
import httpx
import os
from typing import List, Dict, Any

# ────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────

PORTIER_URL = "http://127.0.0.1:12344"
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

SERVICES = [
    {
        "service_name": "agent17",
        "endpoint": "http://127.0.0.1:12366",
        "program_target": "agent17p"
    },
    {
        "service_name": "agent18",
        "endpoint": "http://127.0.0.1:12367",
        "program_target": "agent18p"
    },
    {
        "service_name": "agent19",
        "endpoint": "http://127.0.0.1:12368",
        "program_target": "agent19p"
    },
    {
        "service_name": "agent20",
        "endpoint": "http://127.0.0.1:12369",
        "program_target": "agent20p"
    },
]

# ────────────────────────────────────────────────────────────────────
# Registration Functions
# ────────────────────────────────────────────────────────────────────

async def register_service(
    client: httpx.AsyncClient,
    service: Dict[str, str]
) -> Dict[str, Any]:
    """Register a single service with Portier."""
    url = f"{PORTIER_URL}/route/update"
    
    headers = {"Content-Type": "application/json"}
    if BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    
    payload = {
        "service_name": service["service_name"],
        "endpoint": service["endpoint"],
        "program_target": service["program_target"]
    }
    
    try:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ {service['service_name']} registered successfully")
        print(f"   → {service['endpoint']} ({service['program_target']})")
        
        return {"status": "success", "service": service["service_name"], "data": data}
    
    except httpx.HTTPError as e:
        print(f"❌ {service['service_name']} registration failed: {e}")
        return {"status": "error", "service": service["service_name"], "error": str(e)}


async def verify_service_health(
    client: httpx.AsyncClient,
    service: Dict[str, str]
) -> bool:
    """Verify service is healthy before registration."""
    health_url = f"{service['endpoint']}/health"
    
    try:
        response = await client.get(health_url, timeout=3.0)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "healthy":
            print(f"✅ {service['service_name']} is healthy")
            return True
        else:
            print(f"⚠️  {service['service_name']} responded but not healthy")
            return False
    
    except Exception as e:
        print(f"❌ {service['service_name']} health check failed: {e}")
        return False


async def main():
    """Main registration workflow."""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Pool Services Registration (Agent17-20)")
    print("  Target: Portier (12344)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Verify all services are healthy
        print("📋 Step 1: Health Checks")
        print("-" * 50)
        
        healthy_services = []
        for service in SERVICES:
            if await verify_service_health(client, service):
                healthy_services.append(service)
        
        print()
        
        if not healthy_services:
            print("❌ No healthy services found. Start services first:")
            print("   bash bin/pool_services.sh start")
            return
        
        print(f"✅ {len(healthy_services)}/{len(SERVICES)} services healthy")
        print()
        
        # Step 2: Register healthy services with Portier
        print("📋 Step 2: Portier Registration")
        print("-" * 50)
        
        results = []
        for service in healthy_services:
            result = await register_service(client, service)
            results.append(result)
            await asyncio.sleep(0.5)  # Rate limiting
        
        print()
        
        # Step 3: Summary
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  Registration Summary")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        success_count = sum(1 for r in results if r["status"] == "success")
        error_count = len(results) - success_count
        
        print(f"✅ Successful: {success_count}")
        print(f"❌ Failed:     {error_count}")
        print()
        
        if error_count > 0:
            print("Failed services:")
            for r in results:
                if r["status"] == "error":
                    print(f"  - {r['service']}: {r['error']}")
        
        print()
        print("Next steps:")
        print("  1. Verify registration: bash bin/pool_services.sh status")
        print("  2. Test dispatch: scripts/test_pool_services.py")


if __name__ == "__main__":
    asyncio.run(main())
