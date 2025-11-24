#!/usr/bin/env python3
"""
Load Test: 20-Services-Szenario
Tests Portier → OpenA2 → Pool-Services (12349-12368) unter Last.

Testet:
- Concurrent Requests (asyncio)
- Latenz-Messung (P50, P95, P99)
- Throughput-Berechnung (req/s)
- Archiv-Entry-Validierung (index.jsonl)
- Service-Health-Checks
"""

import asyncio
import httpx
import time
import json
import statistics
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
PORTIER_URL = "http://127.0.0.1:12344"
OPENA2_URL = "http://127.0.0.1:12345"
BEARER_TOKEN = None  # Wird aus .env geladen

# Service-Pool (20 Services)
POOL_SERVICES = [
    {"port": 12349, "target": "agent01p", "name": "agent01"},
    {"port": 12350, "target": "agent02p", "name": "agent02"},
    {"port": 12351, "target": "agent03p", "name": "agent03"},
    {"port": 12352, "target": "agent04p", "name": "agent04"},
    {"port": 12353, "target": "agent05p", "name": "agent05"},
    {"port": 12354, "target": "agent06p", "name": "agent06"},
    {"port": 12355, "target": "agent07p", "name": "agent07"},
    {"port": 12356, "target": "agent08p", "name": "agent08"},
    {"port": 12357, "target": "agent09p", "name": "agent09"},
    {"port": 12358, "target": "agent10p", "name": "agent10"},
    {"port": 12359, "target": "agent11p", "name": "agent11"},
    {"port": 12360, "target": "agent12p", "name": "agent12"},
    {"port": 12361, "target": "agent13p", "name": "agent13"},
    {"port": 12362, "target": "agent14p", "name": "agent14"},
    {"port": 12363, "target": "agent15p", "name": "agent15"},
    {"port": 12364, "target": "agent16p", "name": "agent16"},
    {"port": 12365, "target": "agent17p", "name": "agent17"},
    {"port": 12366, "target": "agent18p", "name": "agent18"},
    {"port": 12367, "target": "agent19p", "name": "agent19"},
    {"port": 12368, "target": "agent20p", "name": "agent20"},
]

# Load-Test-Parameter
CONCURRENCY = 50  # Parallele Requests
TOTAL_REQUESTS = 1000  # Gesamt-Requests
REQUEST_TIMEOUT = 30  # Timeout in Sekunden

# Archiv-Pfad
ARCHIV_INDEX = Path("1.opena1&2_portier/archivp_store/index.jsonl")

# -------------------------------------------------------------------
# Metrics
# -------------------------------------------------------------------
class Metrics:
    def __init__(self):
        self.latencies: List[float] = []
        self.successes = 0
        self.failures = 0
        self.timeouts = 0
        self.errors_by_type: Dict[str, int] = defaultdict(int)
        self.service_calls: Dict[str, int] = defaultdict(int)
        self.start_time = None
        self.end_time = None
    
    def add_success(self, latency: float, service: str):
        self.latencies.append(latency)
        self.successes += 1
        self.service_calls[service] += 1
    
    def add_failure(self, error_type: str):
        self.failures += 1
        self.errors_by_type[error_type] += 1
    
    def add_timeout(self):
        self.timeouts += 1
    
    def report(self) -> Dict[str, Any]:
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        if self.latencies:
            p50 = statistics.median(self.latencies)
            p95 = statistics.quantiles(self.latencies, n=20)[18] if len(self.latencies) > 20 else max(self.latencies)
            p99 = statistics.quantiles(self.latencies, n=100)[98] if len(self.latencies) > 100 else max(self.latencies)
            avg = statistics.mean(self.latencies)
            min_lat = min(self.latencies)
            max_lat = max(self.latencies)
        else:
            p50 = p95 = p99 = avg = min_lat = max_lat = 0
        
        throughput = self.successes / duration if duration > 0 else 0
        
        return {
            "duration_seconds": round(duration, 2),
            "total_requests": self.successes + self.failures + self.timeouts,
            "successes": self.successes,
            "failures": self.failures,
            "timeouts": self.timeouts,
            "throughput_req_per_sec": round(throughput, 2),
            "latency_ms": {
                "min": round(min_lat * 1000, 2),
                "avg": round(avg * 1000, 2),
                "p50": round(p50 * 1000, 2),
                "p95": round(p95 * 1000, 2),
                "p99": round(p99 * 1000, 2),
                "max": round(max_lat * 1000, 2),
            },
            "errors_by_type": dict(self.errors_by_type),
            "service_calls": dict(self.service_calls),
        }

# -------------------------------------------------------------------
# Load Bearer Token
# -------------------------------------------------------------------
def load_bearer_token():
    global BEARER_TOKEN
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("BEARER_TOKEN="):
                    BEARER_TOKEN = line.split("=", 1)[1].strip()
                    return
    print("⚠️  BEARER_TOKEN nicht in .env gefunden, Requests ohne Auth")

# -------------------------------------------------------------------
# Health Checks
# -------------------------------------------------------------------
async def health_check_all() -> Dict[str, bool]:
    """Prüft Health aller Services"""
    async with httpx.AsyncClient(timeout=5.0) as client:
        results = {}
        
        # Portier
        try:
            r = await client.get(f"{PORTIER_URL}/health")
            results["portier"] = r.status_code == 200
        except:
            results["portier"] = False
        
        # OpenA2
        try:
            r = await client.get(f"{OPENA2_URL}/health")
            results["opena2"] = r.status_code == 200
        except:
            results["opena2"] = False
        
        # Pool-Services
        for svc in POOL_SERVICES:
            try:
                r = await client.get(f"http://127.0.0.1:{svc['port']}/health")
                results[svc["name"]] = r.status_code == 200
            except:
                results[svc["name"]] = False
        
        return results

# -------------------------------------------------------------------
# Single Request
# -------------------------------------------------------------------
async def dispatch_request(
    client: httpx.AsyncClient,
    service: Dict[str, Any],
    request_id: int,
    semaphore: asyncio.Semaphore,
    metrics: Metrics
):
    """Sendet einen Dispatch-Request über Portier"""
    async with semaphore:
        start = time.time()
        
        try:
            headers = {}
            if BEARER_TOKEN:
                headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
            
            payload = {
                "service_target": service["target"],
                "action": "process",
                "params": {
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            response = await client.post(
                f"{PORTIER_URL}/dispatch/kordp",
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            
            latency = time.time() - start
            
            if response.status_code == 200:
                metrics.add_success(latency, service["name"])
            else:
                metrics.add_failure(f"http_{response.status_code}")
        
        except asyncio.TimeoutError:
            metrics.add_timeout()
        except httpx.RequestError as e:
            metrics.add_failure(f"request_error_{type(e).__name__}")
        except Exception as e:
            metrics.add_failure(f"unknown_{type(e).__name__}")

# -------------------------------------------------------------------
# Load Test Runner
# -------------------------------------------------------------------
async def run_load_test():
    """Führt Load-Test durch"""
    print("🚀 Load Test: 20-Services-Szenario")
    print("=" * 60)
    
    # 1. Health-Checks
    print("\n1️⃣  Health-Checks...")
    health = await health_check_all()
    healthy_count = sum(1 for v in health.values() if v)
    total_count = len(health)
    
    print(f"   ✅ {healthy_count}/{total_count} Services healthy")
    
    if not health.get("portier"):
        print("❌ Portier nicht erreichbar, Test abgebrochen")
        return
    
    if not health.get("opena2"):
        print("⚠️  OpenA2 nicht erreichbar, Archiv-Validierung wird übersprungen")
    
    # 2. Load-Test
    print(f"\n2️⃣  Load-Test starten...")
    print(f"   Concurrency: {CONCURRENCY}")
    print(f"   Total Requests: {TOTAL_REQUESTS}")
    print(f"   Target Services: {len(POOL_SERVICES)}")
    
    metrics = Metrics()
    metrics.start_time = time.time()
    
    semaphore = asyncio.Semaphore(CONCURRENCY)
    
    async with httpx.AsyncClient() as client:
        tasks = []
        
        for i in range(TOTAL_REQUESTS):
            # Round-Robin über Services
            service = POOL_SERVICES[i % len(POOL_SERVICES)]
            task = dispatch_request(client, service, i, semaphore, metrics)
            tasks.append(task)
        
        # Ausführen mit Progress
        print("   Requests laufen...", end="", flush=True)
        await asyncio.gather(*tasks)
        print(" ✅ Done")
    
    metrics.end_time = time.time()
    
    # 3. Archiv-Validierung
    print("\n3️⃣  Archiv-Validierung...")
    if ARCHIV_INDEX.exists():
        with open(ARCHIV_INDEX) as f:
            entries = [json.loads(line) for line in f if line.strip()]
        
        # Zähle neue Einträge (seit Test-Start)
        test_start_iso = datetime.fromtimestamp(metrics.start_time).isoformat()
        new_entries = [
            e for e in entries
            if e.get("timestamp", "") >= test_start_iso
        ]
        
        print(f"   📦 {len(new_entries)} neue Safepoints seit Test-Start")
        print(f"   📋 {len(entries)} Gesamt-Einträge in index.jsonl")
    else:
        print("   ⚠️  index.jsonl nicht gefunden")
    
    # 4. Ergebnisse
    print("\n4️⃣  Ergebnisse:")
    print("=" * 60)
    
    report = metrics.report()
    
    print(f"\n⏱️  Duration: {report['duration_seconds']}s")
    print(f"📊 Total Requests: {report['total_requests']}")
    print(f"✅ Successes: {report['successes']}")
    print(f"❌ Failures: {report['failures']}")
    print(f"⏰ Timeouts: {report['timeouts']}")
    print(f"🚀 Throughput: {report['throughput_req_per_sec']} req/s")
    
    print(f"\n📈 Latency (ms):")
    for key, val in report['latency_ms'].items():
        print(f"   {key.upper()}: {val}ms")
    
    if report['errors_by_type']:
        print(f"\n⚠️  Errors by Type:")
        for err, count in report['errors_by_type'].items():
            print(f"   {err}: {count}")
    
    print(f"\n🔀 Service Call Distribution:")
    for svc, count in sorted(report['service_calls'].items()):
        print(f"   {svc}: {count}")
    
    # 5. JSON-Export
    output_file = Path("logs/load_test_results.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump({
            "test_timestamp": datetime.utcnow().isoformat(),
            "config": {
                "concurrency": CONCURRENCY,
                "total_requests": TOTAL_REQUESTS,
                "services_count": len(POOL_SERVICES),
                "timeout": REQUEST_TIMEOUT,
            },
            "health_checks": health,
            "metrics": report,
        }, f, indent=2)
    
    print(f"\n💾 Ergebnisse gespeichert: {output_file}")
    print("=" * 60)

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
if __name__ == "__main__":
    load_bearer_token()
    asyncio.run(run_load_test())
