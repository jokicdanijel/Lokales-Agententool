#!/usr/bin/env python3
"""
load_test.py — Multi-Service Load Test
- 100 concurrent requests across 4 services
- Measure latency, throughput, error rates
- Verify safepoint persistence
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List
import httpx

# ────────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────────

SERVICES = {
    "portier": ("http://127.0.0.1:12344", [
        {"endpoint": "/health", "method": "GET", "name": "health"},
    ]),
    "opena2": ("http://127.0.0.1:12345", [
        {"endpoint": "/health", "method": "GET", "name": "health"},
    ]),
    "telegram": ("http://127.0.0.1:12346", [
        {"endpoint": "/health", "method": "GET", "name": "health"},
        {"endpoint": "/echo", "method": "POST", "name": "echo", "payload": {"msg": "load-test"}},
    ]),
    "openwebui": ("http://127.0.0.1:3000", [
        {"endpoint": "/health", "method": "GET", "name": "health"},
    ]),
}

# Test parameters
TOTAL_REQUESTS = 100
CONCURRENT_REQUESTS = 10
TIMEOUT = 5.0

# ────────────────────────────────────────────────────────────────────────
# Metrics
# ────────────────────────────────────────────────────────────────────────

class Metrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        self.errors: List[str] = []
        self.start_time = time.time()
        self.end_time = 0.0

    def record_success(self, latency: float):
        self.successful_requests += 1
        self.total_requests += 1
        self.total_latency += latency
        self.min_latency = min(self.min_latency, latency)
        self.max_latency = max(self.max_latency, latency)

    def record_error(self, error: str):
        self.failed_requests += 1
        self.total_requests += 1
        self.errors.append(error)

    def finalize(self):
        self.end_time = time.time()

    @property
    def avg_latency(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_latency / self.successful_requests

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def throughput(self) -> float:
        if self.duration == 0:
            return 0.0
        return self.total_requests / self.duration

    def summary(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful": self.successful_requests,
            "failed": self.failed_requests,
            "success_rate": f"{(self.successful_requests / self.total_requests * 100):.1f}%",
            "latency_min_ms": f"{self.min_latency*1000:.2f}",
            "latency_max_ms": f"{self.max_latency*1000:.2f}",
            "latency_avg_ms": f"{self.avg_latency*1000:.2f}",
            "throughput_rps": f"{self.throughput:.2f}",
            "duration_sec": f"{self.duration:.2f}",
            "errors_count": len(self.errors),
        }


# ────────────────────────────────────────────────────────────────────────
# Load Test Functions
# ────────────────────────────────────────────────────────────────────────

metrics = Metrics()


async def make_request(service_name: str, base_url: str, test_def: Dict[str, Any]) -> None:
    """Make a single HTTP request and record metrics."""
    endpoint = test_def["endpoint"]
    method = test_def.get("method", "GET")
    payload = test_def.get("payload")
    name = test_def.get("name", endpoint)

    url = f"{base_url}{endpoint}"
    
    try:
        start_time = time.time()
        headers = {}
        if service_name == "openwebui":
            headers["Authorization"] = "Bearer test"
        
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                response = await client.post(url, json=payload or {}, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
        
        latency = time.time() - start_time
        
        if 200 <= response.status_code < 300:
            metrics.record_success(latency)
            print(f"  ✅ {service_name}/{name} ({response.status_code}) — {latency*1000:.1f}ms")
        else:
            metrics.record_error(f"{service_name}/{name} — HTTP {response.status_code}")
            print(f"  ❌ {service_name}/{name} — HTTP {response.status_code}")
    
    except Exception as e:
        metrics.record_error(f"{service_name}/{name} — {str(e)}")
        print(f"  ❌ {service_name}/{name} — {str(e)}")


async def load_test_batch(batch_num: int, batch_size: int) -> None:
    """Execute a batch of concurrent requests."""
    tasks = []
    
    for i in range(batch_size):
        # Distribute requests across services
        service_idx = i % len(SERVICES)
        service_name = list(SERVICES.keys())[service_idx]
        base_url, tests = SERVICES[service_name]
        
        # Rotate through tests for this service
        test_def = tests[i % len(tests)]
        
        task = make_request(service_name, base_url, test_def)
        tasks.append(task)
    
    await asyncio.gather(*tasks)


async def run_load_test() -> None:
    """Main load test orchestration."""
    print("=" * 80)
    print(f"🚀 LOAD TEST — {TOTAL_REQUESTS} requests, {CONCURRENT_REQUESTS} concurrent")
    print("=" * 80)
    print()
    
    num_batches = TOTAL_REQUESTS // CONCURRENT_REQUESTS
    
    for batch_num in range(num_batches):
        print(f"📊 Batch {batch_num + 1}/{num_batches}")
        await load_test_batch(batch_num, CONCURRENT_REQUESTS)
        print()
    
    metrics.finalize()


# ────────────────────────────────────────────────────────────────────────
# Archive Verification
# ────────────────────────────────────────────────────────────────────────

def verify_archive() -> Dict[str, Any]:
    """Verify safepoint persistence in archive."""
    try:
        with open("1.opena1&2_portier/archivp_store/index.jsonl", "r") as f:
            lines = f.readlines()
        
        archive_entries = len(lines)
        entry_types = {}
        for line in lines[-50:]:  # Last 50 entries
            try:
                entry = json.loads(line)
                kind = entry.get("kind", "unknown")
                entry_types[kind] = entry_types.get(kind, 0) + 1
            except json.JSONDecodeError:
                pass
        
        return {
            "total_entries": archive_entries,
            "recent_types": entry_types,
            "status": "✅ Archive active",
        }
    except FileNotFoundError:
        return {
            "total_entries": 0,
            "status": "❌ Archive not found",
        }


# ────────────────────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────────────────────

async def main():
    """Run complete load test."""
    await run_load_test()
    
    # Print metrics
    print("=" * 80)
    print("📈 RESULTS")
    print("=" * 80)
    summary = metrics.summary()
    for key, value in summary.items():
        print(f"  {key:.<30} {value}")
    
    # Archive verification
    print()
    print("=" * 80)
    print("📁 ARCHIVE VERIFICATION")
    print("=" * 80)
    archive_info = verify_archive()
    for key, value in archive_info.items():
        print(f"  {key:.<30} {value}")
    
    print()
    print("=" * 80)
    print("✅ LOAD TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
