#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

ELION Hyper-Dashboard Load Test""""""

Generates configurable RPS targeting services

"""ELION Hyper-Dashboard Load TestPhase 15e: Scaled Load-Test (20 Services)



import concurrent
import time

import 20
import 200
import across
import asyncioGenerates
import configurable
import requests
import RPS
import services-
import targeting

import services

import json"""- Mix: health checks, echo, completions

import sys

from typing import Optional, Dict, Any- Measure: routing latency, registry throughput

import httpx

import asyncio"""

# Service ports

SERVICES = [import time

    "http://127.0.0.1:12344",  # Portier

    "http://127.0.0.1:12345",  # OpenA2import jsonimport asyncio

    "http://127.0.0.1:12346",  # Telegram

    "http://127.0.0.1:12348",  # Inferenceimport sysimport json

    "http://127.0.0.1:12349",  # Dashboard

]from typing import List, Dictimport time



import typing

import Any
import Dict
import httpxfrom
import import
import List


class LoadTester:

    def __init__(self, target_rps: int = 200, duration: int = 60):import httpx

        self.target_rps = target_rps

        self.duration = duration# Service ports

        self.requests_sent = 0

        self.requests_completed = 0SERVICES = [SERVICES = [

        self.requests_succeeded = 0

        self.requests_failed = 0    "http://127.0.0.1:12344",  # Portier    ("http://127.0.0.1:12344", "portier"),

        self.latencies = []

        self.errors = {}    "http://127.0.0.1:12345",  # OpenA2    ("http://127.0.0.1:12345", "opena2"),

        self.start_time = None

    "http://127.0.0.1:12346",  # Telegram    ("http://127.0.0.1:12346", "telegram"),

    async def make_request(self, url: str) -> tuple:

        """Make single request and return (success, latency_ms, status)"""    "http://127.0.0.1:12348",  # Inference    ("http://127.0.0.1:12348", "inference"),

        try:

            start = time.perf_counter()    "http://127.0.0.1:12349",  # Dashboard    ("http://127.0.0.1:12349", "browser"),

            async with httpx.AsyncClient(timeout=5.0) as client:

                resp = await client.get(f"{url}/health")]    ("http://127.0.0.1:12350", "vscode"),

                latency_ms = (time.perf_counter() - start) * 1000

                return resp.status_code < 400, latency_ms, resp.status_code    ("http://127.0.0.1:12351", "email"),

        except Exception as e:

            latency_ms = (time.perf_counter() - start) * 1000class LoadTester:    ("http://127.0.0.1:12352", "whatsapp"),

            error_str = str(type(e).__name__)

            self.errors[error_str] = self.errors.get(error_str, 0) + 1    def __init__(self, target_rps: int = 200, duration: int = 60):    ("http://127.0.0.1:12353", "phone"),

            return False, latency_ms, 0

        self.target_rps = target_rps    ("http://127.0.0.1:12354", "calendar"),

    async def worker(self, request_queue: asyncio.Queue):

        """Worker processes requests from queue"""        self.duration = duration    ("http://127.0.0.1:12355", "social_media"),

        while True:

            try:        self.requests_sent = 0    ("http://127.0.0.1:12356", "shop"),

                url = await asyncio.wait_for(request_queue.get(), timeout=0.1)

                success, latency_ms, status = await self.make_request(url)        self.requests_completed = 0    ("http://127.0.0.1:12357", "html_creator"),

                self.requests_completed += 1

                if success:        self.requests_succeeded = 0    ("http://127.0.0.1:12358", "homepage_creator"),

                    self.requests_succeeded += 1

                    self.latencies.append(latency_ms)        self.requests_failed = 0    ("http://127.0.0.1:12359", "stocks_crypto"),

                else:

                    self.requests_failed += 1        self.latencies = []    ("http://127.0.0.1:12360", "influencer"),

                request_queue.task_done()

            except asyncio.TimeoutError:        self.errors = {}    ("http://127.0.0.1:12361", "unlock_master"),

                if time.time() - self.start_time > self.duration:

                    break        self.start_time = None    ("http://127.0.0.1:12362", "local_archiv"),

            except Exception:

                break    ("http://127.0.0.1:12363", "custom_1"),



    async def run(self) -> Dict[str, Any]:    async def make_request(self, url: str) -> tuple:    ("http://127.0.0.1:12364", "custom_2"),

        """Execute load test"""

        self.start_time = time.time()        """Make single request and return (success, latency_ms, status)"""]

        request_queue = asyncio.Queue()

                try:

        print(f"=== ELION Load Test ===")

        print(f"Target RPS: {self.target_rps}")            start = time.perf_counter()TOTAL_REQUESTS = 200

        print(f"Duration: {self.duration}s")

        print(f"Services: {len(SERVICES)}")            async with httpx.AsyncClient(timeout=5.0) as client:CONCURRENT_REQUESTS = 10

        print(f"Expected Requests: ~{self.target_rps * self.duration}\n")

                        resp = await client.get(f"{url}/health")TIMEOUT = 5.0

        # Create workers

        workers = [                latency_ms = (time.perf_counter() - start) * 1000

            asyncio.create_task(self.worker(request_queue))

            for _ in range(min(self.target_rps, 50))                return resp.status_code < 400, latency_ms, resp.status_codeclass Metrics:

        ]

                except Exception as e:    def __init__(self):

        # Generate requests

        request_interval = 1.0 / self.target_rps            latency_ms = (time.perf_counter() - start) * 1000        self.total_requests = 0

        service_idx = 0

                    error_str = str(type(e).__name__)        self.successful_requests = 0

        while time.time() - self.start_time < self.duration:

            service = SERVICES[service_idx % len(SERVICES)]            self.errors[error_str] = self.errors.get(error_str, 0) + 1        self.failed_requests = 0

            await request_queue.put(service)

            self.requests_sent += 1            return False, latency_ms, 0        self.total_latency = 0.0

            service_idx += 1

                    self.min_latency = float('inf')

            # Progress report

            if self.requests_sent % max(1, self.target_rps) == 0:    async def worker(self, request_queue: asyncio.Queue):        self.max_latency = 0.0

                elapsed = time.time() - self.start_time

                actual_rps = self.requests_sent / max(1, elapsed)        """Worker processes requests from queue"""        self.errors: List[str] = []

                print(f"Sent: {self.requests_sent} | Completed: {self.requests_completed} | "

                      f"Success: {self.requests_succeeded} | Actual RPS: {actual_rps:.1f}")        while True:        self.start_time = time.time()



            await asyncio.sleep(request_interval)            try:        self.end_time = 0.0



        # Wait for all requests                url = await asyncio.wait_for(request_queue.get(), timeout=0.1)

        await request_queue.join()

                        success, latency_ms, status = await self.make_request(url)    def record_success(self, latency: float):

        # Cancel workers

        for worker in workers:                self.requests_completed += 1        self.successful_requests += 1

            worker.cancel()

                        if success:        self.total_requests += 1

        return self._calculate_stats()

                    self.requests_succeeded += 1        self.total_latency += latency

    def _calculate_stats(self) -> Dict[str, Any]:

        """Calculate statistics"""                    self.latencies.append(latency_ms)        self.min_latency = min(self.min_latency, latency)

        if not self.latencies:

            return {"error": "No successful requests"}                else:        self.max_latency = max(self.max_latency, latency)



        elapsed = time.time() - self.start_time                    self.requests_failed += 1

        latencies = sorted(self.latencies)

                        request_queue.task_done()    def record_error(self, error: str):

        return {

            "duration_sec": self.duration,            except asyncio.TimeoutError:        self.failed_requests += 1

            "elapsed_sec": elapsed,

            "total_requests": self.requests_sent,                if time.time() - self.start_time > self.duration:        self.total_requests += 1

            "completed_requests": self.requests_completed,

            "successful_requests": self.requests_succeeded,                    break        self.errors.append(error)

            "failed_requests": self.requests_failed,

            "success_rate_pct": (self.requests_succeeded / self.requests_completed * 100) if self.requests_completed else 0,            except Exception:

            "actual_rps": self.requests_sent / elapsed,

            "response_times_ms": {                break    def finalize(self):

                "min": min(latencies),

                "max": max(latencies),        self.end_time = time.time()

                "mean": sum(latencies) / len(latencies),

                "p50": latencies[len(latencies) // 2],    async def run(self) -> Dict:

                "p95": latencies[int(len(latencies) * 0.95)],

                "p99": latencies[int(len(latencies) * 0.99)],        """Execute load test"""    @property

            },

            "errors": self.errors,        self.start_time = time.time()    def avg_latency(self) -> float:

        }

        request_queue = asyncio.Queue()        if self.successful_requests == 0:



async def main():                    return 0.0

    import argparse

    parser = argparse.ArgumentParser()        print(f"=== ELION Load Test ===")        return self.total_latency / self.successful_requests

    parser.add_argument('--target', type=int, default=200, help='Target RPS')

    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')        print(f"Target RPS: {self.target_rps}")

    parser.add_argument('--output', help='Output JSON file')

    args = parser.parse_args()        print(f"Duration: {self.duration}s")    @property



    tester = LoadTester(args.target, args.duration)        print(f"Services: {len(SERVICES)}")    def duration(self) -> float:

    stats = await tester.run()

            print(f"Expected Requests: ~{self.target_rps * self.duration}\n")        return self.end_time - self.start_time

    print(f"\n=== Results ===")

    print(f"Sent: {stats['total_requests']}")

    print(f"Completed: {stats['completed_requests']}")

    print(f"Success: {stats['successful_requests']} ({stats['success_rate_pct']:.1f}%)")        # Create workers    @property

    print(f"Failed: {stats['failed_requests']}")

    print(f"Actual RPS: {stats['actual_rps']:.2f}")        workers = [    def throughput(self) -> float:

    print(f"\nResponse Times (ms):")

    print(f"  Min: {stats['response_times_ms']['min']:.2f}")            asyncio.create_task(self.worker(request_queue))        if self.duration == 0:

    print(f"  Mean: {stats['response_times_ms']['mean']:.2f}")

    print(f"  P95: {stats['response_times_ms']['p95']:.2f}")            for _ in range(min(self.target_rps, 50))            return 0.0

    print(f"  P99: {stats['response_times_ms']['p99']:.2f}")

    print(f"  Max: {stats['response_times_ms']['max']:.2f}")        ]        return self.total_requests / self.duration



    if stats['errors']:

        print(f"\nErrors:")

        for error, count in stats['errors'].items():        # Generate requests    def summary(self) -> Dict[str, Any]:

            print(f"  {error}: {count}")

            request_interval = 1.0 / self.target_rps        return {

    if args.output:

        with open(args.output, 'w') as f:        service_idx = 0            "total_requests": self.total_requests,

            json.dump(stats, f, indent=2)

        print(f"\nResults saved to: {args.output}")                    "successful": self.successful_requests,



        while time.time() - self.start_time < self.duration:            "failed": self.failed_requests,

if __name__ == "__main__":

    asyncio.run(main())            service = SERVICES[service_idx % len(SERVICES)]            "success_rate": f"{(self.successful_requests / self.total_requests * 100):.1f}%",


            await request_queue.put(service)            "latency_min_ms": f"{self.min_latency*1000:.2f}",

            self.requests_sent += 1            "latency_max_ms": f"{self.max_latency*1000:.2f}",

            service_idx += 1            "latency_avg_ms": f"{self.avg_latency*1000:.2f}",

                        "throughput_rps": f"{self.throughput:.2f}",

            # Progress report            "duration_sec": f"{self.duration:.2f}",

            if self.requests_sent % max(1, self.target_rps) == 0:            "services_tested": len(SERVICES),

                elapsed = time.time() - self.start_time        }

                actual_rps = self.requests_sent / max(1, elapsed)

                print(f"Sent: {self.requests_sent} | Completed: {self.requests_completed} | "

                      f"Success: {self.requests_succeeded} | Actual RPS: {actual_rps:.1f}")metrics = Metrics()



            await asyncio.sleep(request_interval)

        async def make_request(req_num: int, base_url: str, service_name: str) -> None:

        # Wait for all requests    """Make request to service."""

        await request_queue.join()    try:

                start_time = time.time()

        # Cancel workers        async with httpx.AsyncClient(timeout=TIMEOUT) as client:

        for worker in workers:            r = await client.get(f"{base_url}/health")

            worker.cancel()

                latency = time.time() - start_time

        return self._calculate_stats()

        if 200 <= r.status_code < 300:

    def _calculate_stats(self) -> Dict:            metrics.record_success(latency)

        """Calculate statistics"""            print(f"  ✅ {req_num:3d}. {service_name:20} ({r.status_code}) — {latency*1000:.1f}ms")

        if not self.latencies:        else:

            return {"error": "No successful requests"}            metrics.record_error(f"{service_name} — HTTP {r.status_code}")

                    print(f"  ❌ {req_num:3d}. {service_name:20} — HTTP {r.status_code}")

        elapsed = time.time() - self.start_time

        latencies = sorted(self.latencies)    except Exception as e:

                metrics.record_error(str(e)[:50])

        return {        print(f"  ❌ {req_num:3d}. {service_name:20} — {str(e)[:40]}")

            "duration_sec": self.duration,

            "elapsed_sec": elapsed,

            "total_requests": self.requests_sent,async def load_test() -> None:

            "completed_requests": self.requests_completed,    """Run scaled load test."""

            "successful_requests": self.requests_succeeded,    print("=" * 80)

            "failed_requests": self.requests_failed,    print(f"🚀 SCALED LOAD TEST — {TOTAL_REQUESTS} requests, {CONCURRENT_REQUESTS} concurrent, {len(SERVICES)} services")

            "success_rate_pct": (self.requests_succeeded / self.requests_completed * 100) if self.requests_completed else 0,    print("=" * 80)

            "actual_rps": self.requests_sent / elapsed,    print()

            "response_times_ms": {

                "min": min(latencies),    num_batches = TOTAL_REQUESTS // CONCURRENT_REQUESTS

                "max": max(latencies),    for batch_num in range(num_batches):

                "mean": sum(latencies) / len(latencies),        batch_start = batch_num * CONCURRENT_REQUESTS

                "p50": latencies[len(latencies) // 2],        batch_end = batch_start + CONCURRENT_REQUESTS

                "p95": latencies[int(len(latencies) * 0.95)],

                "p99": latencies[int(len(latencies) * 0.99)],        print(f"📊 Batch {batch_num + 1}/{num_batches}")

            },

            "errors": self.errors,        tasks = []

        }        for i in range(batch_start, batch_end):

            # Distribute across services

            service_idx = i % len(SERVICES)

async def main():            base_url, service_name = SERVICES[service_idx]

    import argparse

    parser = argparse.ArgumentParser()            task = make_request(i + 1, base_url, service_name)

    parser.add_argument('--target', type=int, default=200, help='Target RPS')            tasks.append(task)

    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')

    parser.add_argument('--output', help='Output JSON file')        await asyncio.gather(*tasks)

    args = parser.parse_args()        print()



    tester = LoadTester(args.target, args.duration)    metrics.finalize()

    stats = await tester.run()



    print(f"\n=== Results ===")async def verify_archive() -> Dict[str, Any]:

    print(f"Sent: {stats['total_requests']}")    """Verify archive."""

    print(f"Completed: {stats['completed_requests']}")    try:

    print(f"Success: {stats['successful_requests']} ({stats['success_rate_pct']:.1f}%)")        with open("1.opena1&2_portier/archivp_store/index.jsonl", "r") as f:

    print(f"Failed: {stats['failed_requests']}")            lines = f.readlines()

    print(f"Actual RPS: {stats['actual_rps']:.2f}")

    print(f"\nResponse Times (ms):")        return {

    print(f"  Min: {stats['response_times_ms']['min']:.2f}")            "total_entries": len(lines),

    print(f"  Mean: {stats['response_times_ms']['mean']:.2f}")            "status": "✅ Archive active",

    print(f"  P95: {stats['response_times_ms']['p95']:.2f}")        }

    print(f"  P99: {stats['response_times_ms']['p99']:.2f}")    except FileNotFoundError:

    print(f"  Max: {stats['response_times_ms']['max']:.2f}")        return {"status": "❌ Archive not found"}



    if stats['errors']:

        print(f"\nErrors:")async def main():

        for error, count in stats['errors'].items():    """Main."""

            print(f"  {error}: {count}")    await load_test()



    if args.output:    print("=" * 80)

        with open(args.output, 'w') as f:    print("📈 RESULTS")

            json.dump(stats, f, indent=2)    print("=" * 80)

        print(f"\nResults saved to: {args.output}")    summary = metrics.summary()

    for key, value in summary.items():

        print(f"  {key:.<30} {value}")

if __name__ == "__main__":

    asyncio.run(main())    print()

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
,        host="
