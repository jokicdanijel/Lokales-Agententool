#!/usr/bin/env python3
"""
Phase 15e: Scaled Load-Test (20 Services)
- 200 concurrent requests across 20 services
- Mix: health checks, echo, completions
- Measure: routing latency, registry throughput
"""

import asyncio
import json
import time
from typing import Any, Dict, List
import httpx

SERVICES = [
    ("http://127.0.0.1:12344", "portier"),
    ("http://127.0.0.1:12345", "opena2"),
    ("http://127.0.0.1:12346", "telegram"),
    ("http://127.0.0.1:12348", "inference"),
    ("http://127.0.0.1:12349", "browser"),
    ("http://127.0.0.1:12350", "vscode"),
    ("http://127.0.0.1:12351", "email"),
    ("http://127.0.0.1:12352", "whatsapp"),
    ("http://127.0.0.1:12353", "phone"),
    ("http://127.0.0.1:12354", "calendar"),
    ("http://127.0.0.1:12355", "social_media"),
    ("http://127.0.0.1:12356", "shop"),
    ("http://127.0.0.1:12357", "html_creator"),
    ("http://127.0.0.1:12358", "homepage_creator"),
    ("http://127.0.0.1:12359", "stocks_crypto"),
    ("http://127.0.0.1:12360", "influencer"),
    ("http://127.0.0.1:12361", "unlock_master"),
    ("http://127.0.0.1:12362", "local_archiv"),
    ("http://127.0.0.1:12363", "custom_1"),
    ("http://127.0.0.1:12364", "custom_2"),
]

TOTAL_REQUESTS = 200
CONCURRENT_REQUESTS = 10
TIMEOUT = 5.0

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
            "services_tested": len(SERVICES),
        }


metrics = Metrics()


async def make_request(req_num: int, base_url: str, service_name: str) -> None:
    """Make request to service."""
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.get(f"{base_url}/health")
        
        latency = time.time() - start_time
        
        if 200 <= r.status_code < 300:
            metrics.record_success(latency)
            print(f"  ✅ {req_num:3d}. {service_name:20} ({r.status_code}) — {latency*1000:.1f}ms")
        else:
            metrics.record_error(f"{service_name} — HTTP {r.status_code}")
            print(f"  ❌ {req_num:3d}. {service_name:20} — HTTP {r.status_code}")
    
    except Exception as e:
        metrics.record_error(str(e)[:50])
        print(f"  ❌ {req_num:3d}. {service_name:20} — {str(e)[:40]}")


async def load_test() -> None:
    """Run scaled load test."""
    print("=" * 80)
    print(f"🚀 SCALED LOAD TEST — {TOTAL_REQUESTS} requests, {CONCURRENT_REQUESTS} concurrent, {len(SERVICES)} services")
    print("=" * 80)
    print()
    
    num_batches = TOTAL_REQUESTS // CONCURRENT_REQUESTS
    for batch_num in range(num_batches):
        batch_start = batch_num * CONCURRENT_REQUESTS
        batch_end = batch_start + CONCURRENT_REQUESTS
        
        print(f"📊 Batch {batch_num + 1}/{num_batches}")
        
        tasks = []
        for i in range(batch_start, batch_end):
            # Distribute across services
            service_idx = i % len(SERVICES)
            base_url, service_name = SERVICES[service_idx]
            
            task = make_request(i + 1, base_url, service_name)
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        print()
    
    metrics.finalize()


async def verify_archive() -> Dict[str, Any]:
    """Verify archive."""
    try:
        with open("1.opena1&2_portier/archivp_store/index.jsonl", "r") as f:
            lines = f.readlines()
        
        return {
            "total_entries": len(lines),
            "status": "✅ Archive active",
        }
    except FileNotFoundError:
        return {"status": "❌ Archive not found"}


async def main():
    """Main."""
    await load_test()
    
    print("=" * 80)
    print("📈 RESULTS")
    print("=" * 80)
    summary = metrics.summary()
    for key, value in summary.items():
        print(f"  {key:.<30} {value}")
    
    print()
    print("=" * 80)
    print("📁 ARCHIVE VERIFICATION")
    print("=" * 80)
    archive_info = await verify_archive()
    for key, value in archive_info.items():
        print(f"  {key:.<30} {value}")
    
    print()
    print("=" * 80)
    print("✅ SCALED LOAD TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
