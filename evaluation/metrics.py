"""Helper metrics functions for evaluation framework."""
from __future__ import annotations

from typing import List, Dict, Any
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


def exact_match(text: str, expected: str) -> float:
    if not expected:
        return 0.0
    return 1.0 if text.strip() == expected.strip() else 0.0


def contains_frac(text: str, expected: str) -> float:
    """Return fraction of expected tokens that appear in text."""
    if not expected:
        return 0.0
    exp_tokens = [t for t in expected.split() if t]
    if not exp_tokens:
        return 0.0
    found = sum(1 for t in exp_tokens if t in text)
    return found / len(exp_tokens)


def length_ratio(text: str, expected: str) -> float:
    if not expected:
        return 0.0
    return len(text) / max(1, len(expected))


def aggregate(scores: Dict[str, List[float]]) -> Dict[str, Any]:
    """Aggregate score lists into summary metrics including a relevance pass rate."""
    res = {}
    # means
    for k, vals in scores.items():
        nums = [v for v in vals if isinstance(v, (int, float))]
        res[f"{k}_mean"] = statistics.mean(nums) if nums else 0.0
    # relevance pass rate: use contains_frac >= 0.5 as pass
    contains = scores.get('contains_frac', [])
    if contains:
        passes = sum(1 for v in contains if v >= 0.5)
        res['relevance_pass_rate'] = passes / len(contains)
    else:
        res['relevance_pass_rate'] = 0.0
    return res
