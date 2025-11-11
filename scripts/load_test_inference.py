#!/usr/bin/env python3
"""
Load Test: Inference Service
- 100 requests via Inference Service
- Mix: /health, /models, /chat/completions
- Measure: latency, throughput, tokens/sec
"""

import asyncio
import json
import time
from typing import Any, Dict, List
import httpx

INFERENCE_SERVICE = "http://127.0.0.1:12348"
TOTAL_REQUESTS = 100
CONCURRENT_REQUESTS = 5  # Limited due to Ollama inference time
TIMEOUT = 60.0

class Metrics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency = 0.0
        self.min_latency = float('inf')
        self.max_latency = 0.0
        self.total_tokens = 0
        self.errors: List[str] = []
        self.start_time = time.time()
        self.end_time = 0.0

    def record_success(self, latency: float, tokens: int = 0):
        self.successful_requests += 1
        self.total_requests += 1
        self.total_latency += latency
        self.total_tokens += tokens
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

    @property
    def tokens_per_sec(self) -> float:
        if self.duration == 0:
            return 0.0
        return self.total_tokens / self.duration

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
            "tokens_total": self.total_tokens,
            "tokens_per_sec": f"{self.tokens_per_sec:.2f}",
            "duration_sec": f"{self.duration:.2f}",
            "errors_count": len(self.errors),
        }


metrics = Metrics()


async def make_request(req_num: int, test_type: str) -> None:
    """Make a single request to Inference Service."""
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            if test_type == "health":
                r = await client.get(f"{INFERENCE_SERVICE}/health")
                latency = time.time() - start_time
                if 200 <= r.status_code < 300:
                    metrics.record_success(latency, 0)
                    print(f"  ✅ {req_num:3d}. health — {latency*1000:.1f}ms")
                else:
                    metrics.record_error(f"health — HTTP {r.status_code}")
                    print(f"  ❌ {req_num:3d}. health — HTTP {r.status_code}")
            
            elif test_type == "models":
                r = await client.get(f"{INFERENCE_SERVICE}/models")
                latency = time.time() - start_time
                if 200 <= r.status_code < 300:
                    metrics.record_success(latency, 0)
                    print(f"  ✅ {req_num:3d}. models — {latency*1000:.1f}ms")
                else:
                    metrics.record_error(f"models — HTTP {r.status_code}")
                    print(f"  ❌ {req_num:3d}. models — HTTP {r.status_code}")
            
            elif test_type == "completion":
                payload = {
                    "model": "llama2",
                    "messages": [{"role": "user", "content": f"Frage {req_num}: Sag kurz hallo"}],
                    "max_tokens": 50,
                    "temperature": 0.7,
                }
                r = await client.post(f"{INFERENCE_SERVICE}/chat/completions", json=payload)
                latency = time.time() - start_time
                if 200 <= r.status_code < 300:
                    data = r.json()
                    tokens = data.get("usage", {}).get("completion_tokens", 0)
                    metrics.record_success(latency, tokens)
                    print(f"  ✅ {req_num:3d}. completion — {latency*1000:.1f}ms — {tokens} tokens")
                else:
                    metrics.record_error(f"completion — HTTP {r.status_code}")
                    print(f"  ❌ {req_num:3d}. completion — HTTP {r.status_code}")
    
    except Exception as e:
        metrics.record_error(str(e))
        print(f"  ❌ {req_num:3d}. error — {str(e)[:50]}")


async def load_test() -> None:
    """Run load test."""
    print("=" * 80)
    print(f"🚀 INFERENCE LOAD TEST — {TOTAL_REQUESTS} requests, {CONCURRENT_REQUESTS} concurrent")
    print("=" * 80)
    print()
    
    # Distribute requests: 30% health, 20% models, 50% completions
    test_distribution = []
    for i in range(TOTAL_REQUESTS):
        if i % 10 < 3:
            test_distribution.append("health")
        elif i % 10 < 5:
            test_distribution.append("models")
        else:
            test_distribution.append("completion")
    
    # Run in batches
    num_batches = TOTAL_REQUESTS // CONCURRENT_REQUESTS
    for batch_num in range(num_batches):
        batch_start = batch_num * CONCURRENT_REQUESTS
        batch_end = batch_start + CONCURRENT_REQUESTS
        
        print(f"📊 Batch {batch_num + 1}/{num_batches}")
        
        tasks = [
            make_request(i + 1, test_distribution[i])
            for i in range(batch_start, batch_end)
        ]
        
        await asyncio.gather(*tasks)
        print()
    
    metrics.finalize()


async def verify_archive() -> Dict[str, Any]:
    """Verify safepoint persistence."""
    try:
        with open("1.opena1&2_portier/archivp_store/index.jsonl", "r") as f:
            lines = f.readlines()
        
        archive_entries = len(lines)
        entry_types = {}
        for line in lines[-50:]:
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
    print("✅ INFERENCE LOAD TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
