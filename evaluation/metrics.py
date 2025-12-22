"""Helper metrics functions for evaluation framework."""
from __future__ import annotations

from typing import List, Dict
import statistics


def summarize_latencies(latencies: List[float]) -> Dict[str, float]:
    if not latencies:
        return {"count": 0, "mean_ms": 0.0, "p50_ms": 0.0, "p95_ms": 0.0, "max_ms": 0.0}
    lat_sorted = sorted(latencies)
    count = len(lat_sorted)
    mean = statistics.mean(lat_sorted)
    p50 = lat_sorted[int(0.5 * (count - 1))]
    p95 = lat_sorted[int(0.95 * (count - 1))]
    return {"count": count, "mean_ms": mean, "p50_ms": p50, "p95_ms": p95, "max_ms": lat_sorted[-1]}
