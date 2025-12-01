#!/usr/bin/env python3
"""
opena3 V2 Test Suite
Testet alle Option-2-Flow Features des PORTIER 3.0 zertifizierten Agents
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import httpx

# Configuration
BASE_URL = "http://127.0.0.1:12347"
BEARER_TOKEN = "c899b90d-faf8-485b-afa4-078357cf5313"
TIMEOUT = 10.0

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def success(self, test_name: str):
        print(f"✅ {test_name}")
        self.passed += 1
    
    def failure(self, test_name: str, error: str):
        print(f"❌ {test_name}: {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n📊 Test Summary:")
        print(f"   Passed: {self.passed}/{total}")
        print(f"   Failed: {self.failed}/{total}")
        
        if self.failed > 0:
            print(f"\n💥 Failures:")
            for error in self.errors:
                print(f"   - {error}")
        
        return self.failed == 0

async def test_health_check(client: httpx.AsyncClient, results: TestResults):
    """Test: Health Check (kein Auth erforderlich)"""
    try:
        resp = await client.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("service") == "opena3" and data.get("status") == "ok":
                results.success("Health Check")
            else:
                results.failure("Health Check", f"Unexpected response: {data}")
        else:
            results.failure("Health Check", f"Status {resp.status_code}")
    except Exception as e:
        results.failure("Health Check", str(e))

async def test_native_chat(client: httpx.AsyncClient, results: TestResults):
    """Test: Native Chat Endpoint"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    payload = {
        "prompt": "Hello, this is a test message",
        "context": {"test": True}
    }
    
    try:
        resp = await client.post(f"{BASE_URL}/native", json=payload, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if "text" in data and "timestamp" in data:
                results.success("Native Chat")
            else:
                results.failure("Native Chat", f"Missing fields: {data}")
        else:
            results.failure("Native Chat", f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        results.failure("Native Chat", str(e))

async def test_cmd_envelope(client: httpx.AsyncClient, results: TestResults):
    """Test: Option-2-Flow CMD Envelope"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    cmd_envelope = {
        "request_id": str(uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "opena1",
        "command": "chat",
        "payload": {"prompt": "Test CMD envelope message"}
    }
    
    try:
        resp = await client.post(f"{BASE_URL}/cmd", json=cmd_envelope, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("request_id") == cmd_envelope["request_id"] and "result" in data:
                results.success("CMD Envelope (Option-2-Flow)")
            else:
                results.failure("CMD Envelope", f"Invalid response: {data}")
        else:
            results.failure("CMD Envelope", f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        results.failure("CMD Envelope", str(e))

async def test_dispatch_ready(client: httpx.AsyncClient, results: TestResults):
    """Test: Dispatch Ready Status"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    try:
        resp = await client.get(f"{BASE_URL}/dispatch_ready", headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("service_id") == "opena3" and "ready" in data:
                results.success("Dispatch Ready")
            else:
                results.failure("Dispatch Ready", f"Invalid response: {data}")
        else:
            results.failure("Dispatch Ready", f"Status {resp.status_code}")
    except Exception as e:
        results.failure("Dispatch Ready", str(e))

async def test_self_test(client: httpx.AsyncClient, results: TestResults):
    """Test: Self-Test Endpoint"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    try:
        resp = await client.get(f"{BASE_URL}/selftest", headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if "tests" in data and "overall" in data:
                if data["overall"]:
                    results.success("Self-Test (all internal tests passed)")
                else:
                    results.failure("Self-Test", f"Internal tests failed: {data['tests']}")
            else:
                results.failure("Self-Test", f"Invalid response structure: {data}")
        else:
            results.failure("Self-Test", f"Status {resp.status_code}")
    except Exception as e:
        results.failure("Self-Test", str(e))

async def test_auth_rejection(client: httpx.AsyncClient, results: TestResults):
    """Test: Bearer Auth Rejection bei falschem Token"""
    headers = {"Authorization": "Bearer invalid-token"}
    
    try:
        resp = await client.get(f"{BASE_URL}/dispatch_ready", headers=headers, timeout=TIMEOUT)
        if resp.status_code == 401:
            results.success("Auth Rejection (invalid token)")
        else:
            results.failure("Auth Rejection", f"Expected 401, got {resp.status_code}")
    except Exception as e:
        results.failure("Auth Rejection", str(e))

async def test_dispatch_compatibility(client: httpx.AsyncClient, results: TestResults):
    """Test: Dispatcher-Kompatibilität (kordp)"""
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    dispatch_req = {
        "service_target": "openwebui3",
        "payload": {"prompt": "Test dispatch message"},
        "dispatch_id": str(uuid4())
    }
    
    try:
        resp = await client.post(f"{BASE_URL}/dispatch", json=dispatch_req, headers=headers, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("request_id") == dispatch_req["dispatch_id"]:
                results.success("Dispatch Compatibility (kordp)")
            else:
                results.failure("Dispatch Compatibility", f"Request ID mismatch: {data}")
        else:
            results.failure("Dispatch Compatibility", f"Status {resp.status_code}: {resp.text}")
    except Exception as e:
        results.failure("Dispatch Compatibility", str(e))

async def test_safepoint_creation(results: TestResults):
    """Test: Safepoint-Dateien werden erstellt"""
    archivp_root = Path("/tmp/archivp")
    
    if archivp_root.exists():
        # Prüfe auf heute erstellte Safepoints
        today = datetime.now()
        today_path = archivp_root / today.strftime("%Y") / today.strftime("%m") / today.strftime("%d")
        
        if today_path.exists():
            safepoint_files = list(today_path.glob("SP*_opena3→opena2_*.json"))
            if len(safepoint_files) > 0:
                results.success(f"Safepoint Creation ({len(safepoint_files)} files found)")
            else:
                results.failure("Safepoint Creation", "No safepoint files found for today")
        else:
            results.failure("Safepoint Creation", f"Today's safepoint directory not found: {today_path}")
    else:
        results.failure("Safepoint Creation", f"Archivp root not found: {archivp_root}")

async def main():
    print("🧪 opena3 V2 Test Suite")
    print("=" * 50)
    print(f"Target: {BASE_URL}")
    print(f"Token: {BEARER_TOKEN[:8]}...")
    print("")
    
    results = TestResults()
    
    async with httpx.AsyncClient() as client:
        # Basic Tests
        print("🔍 Basic Tests:")
        await test_health_check(client, results)
        await test_auth_rejection(client, results)
        
        print("\n💬 Chat Tests:")
        await test_native_chat(client, results)
        await test_cmd_envelope(client, results)
        
        print("\n🔄 Integration Tests:")
        await test_dispatch_ready(client, results)
        await test_dispatch_compatibility(client, results)
        
        print("\n🧩 Advanced Tests:")
        await test_self_test(client, results)
        await test_safepoint_creation(results)
    
    # Summary
    success = results.summary()
    
    if success:
        print("\n🎉 All tests passed! opena3 V2 is ready for PORTIER 3.0")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Check logs and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())