#!/usr/bin/env python3
"""
Phase 15d: Multi-Service Orchestration Test
- Register 20 services with Portier (Route Registry)
- Dispatch actions to 5 random services
- Verify safepoint persistence
"""

import asyncio
import json
import random
import time
from typing import Any, Dict, List
import httpx

COORDINATOR_URL = "http://127.0.0.1:12344"
ARCHIVP_URL = "http://127.0.0.1:12345"

# Service mapping (port, program_target, name)
SERVICES = [
    (12344, "kordp", "portier"),
    (12345, "archivp", "opena2"),
    (12346, "telep", "telegram"),
    (12348, "infer", "inference"),
    (12349, "browsp", "browser"),
    (12350, "vscop", "vscode"),
    (12351, "emailp", "email"),
    (12352, "whatp", "whatsapp"),
    (12353, "phonep", "phone"),
    (12354, "kalp", "calendar"),
    (12355, "somep", "social_media"),
    (12356, "shopp", "shop"),
    (12357, "htmlp", "html_creator"),
    (12358, "homep", "homepage_creator"),
    (12359, "aktienp", "stocks_crypto"),
    (12360, "infmep", "influencer"),
    (12361, "onlockp", "unlock_master"),
    (12362, "locp", "local_archiv"),
    (12363, "cust1", "custom_1"),
    (12364, "cust2", "custom_2"),
]

STATS = {
    "health_checks": 0,
    "health_ok": 0,
    "registrations": 0,
    "registration_ok": 0,
    "dispatches": 0,
    "dispatch_ok": 0,
    "errors": 0,
}


async def check_service_health(port: int, name: str) -> bool:
    """Check if service is online."""
    STATS["health_checks"] += 1
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            r = await client.get(f"http://127.0.0.1:{port}/health")
            if r.status_code == 200:
                STATS["health_ok"] += 1
                return True
    except Exception as e:
        print(f"  ❌ {name:20} ({port}) — {str(e)[:40]}")
    return False


async def register_service(port: int, target: str, name: str) -> bool:
    """Register service with Portier."""
    STATS["registrations"] += 1
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            payload = {
                "service_name": name,
                "endpoint": f"http://127.0.0.1:{port}",
                "program_target": target,
                "tags": ["scalable", "auto_registered"],
            }
            r = await client.post(f"{COORDINATOR_URL}/route/update", json=payload)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    STATS["registration_ok"] += 1
                    return True
    except Exception as e:
        print(f"  ⚠️  {name:20} registration failed: {str(e)[:40]}")
        STATS["errors"] += 1
    return False


async def dispatch_action(target: str, action: str, name: str) -> bool:
    """Dispatch action to service via Portier."""
    STATS["dispatches"] += 1
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "service_target": target,
                "action": action,
                "params": {"test": True},
            }
            r = await client.post(f"{COORDINATOR_URL}/dispatch/kordp", json=payload)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok"):
                    STATS["dispatch_ok"] += 1
                    return True
    except Exception as e:
        print(f"  ⚠️  {name:20} dispatch failed: {str(e)[:40]}")
        STATS["errors"] += 1
    return False


async def get_archive_stats() -> Dict[str, Any]:
    """Get archive statistics."""
    try:
        with open("1.opena1&2_portier/archivp_store/index.jsonl", "r") as f:
            lines = f.readlines()
        
        total = len(lines)
        kinds = {}
        for line in lines[-100:]:
            try:
                entry = json.loads(line)
                kind = entry.get("kind", "unknown")
                kinds[kind] = kinds.get(kind, 0) + 1
            except json.JSONDecodeError:
                pass
        
        return {
            "total_entries": total,
            "recent_kinds": kinds,
            "status": "✅ Archive active",
        }
    except FileNotFoundError:
        return {"status": "❌ Archive not found"}


async def main():
    """Main orchestration test."""
    print("=" * 80)
    print("🔗 Phase 15d: Multi-Service Orchestration Test (20 Services)")
    print("=" * 80)
    print()
    
    # Step 1: Health check all services
    print("📊 Step 1: Health Check (20 Services)")
    print("-" * 80)
    health_tasks = [
        check_service_health(port, name)
        for port, target, name in SERVICES
    ]
    health_results = await asyncio.gather(*health_tasks)
    online_count = sum(1 for r in health_results if r)
    print(f"  ✅ Online: {online_count}/{len(SERVICES)}")
    print()
    
    # Step 2: Register all services
    print("📋 Step 2: Register Services with Portier (Route Registry)")
    print("-" * 80)
    registration_tasks = [
        register_service(port, target, name)
        for port, target, name in SERVICES
    ]
    registration_results = await asyncio.gather(*registration_tasks)
    registered_count = sum(1 for r in registration_results if r)
    print(f"  ✅ Registered: {registered_count}/{len(SERVICES)}")
    print()
    
    # Step 3: Dispatch to random services
    print("🚀 Step 3: Dispatch Actions to 5 Random Services")
    print("-" * 80)
    selected_services = random.sample(
        [(port, target, name) for port, target, name in SERVICES if port >= 12346],
        min(5, len([s for s in SERVICES if s[0] >= 12346]))
    )
    
    for port, target, name in selected_services:
        result = await dispatch_action(target, "echo", name)
        status = "✅" if result else "❌"
        print(f"  {status} Dispatch to {name:20} ({target:8}) — {'OK' if result else 'FAILED'}")
    
    print()
    
    # Step 4: Archive verification
    print("📁 Step 4: Archive Verification")
    print("-" * 80)
    archive_stats = await get_archive_stats()
    print(f"  Total entries: {archive_stats.get('total_entries', '?')}")
    print(f"  Recent kinds: {archive_stats.get('recent_kinds', {})}")
    print(f"  Status: {archive_stats.get('status', '?')}")
    print()
    
    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"  Health Checks: {STATS['health_ok']}/{STATS['health_checks']} OK")
    print(f"  Registrations: {STATS['registration_ok']}/{STATS['registrations']} OK")
    print(f"  Dispatches: {STATS['dispatch_ok']}/{STATS['dispatches']} OK")
    print(f"  Errors: {STATS['errors']}")
    print()
    print("✅ Phase 15d COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
