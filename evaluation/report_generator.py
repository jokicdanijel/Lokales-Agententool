"""Save evaluation reports as JSON and human-readable summaries."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def save_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, default=str, indent=2)


def save_human(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    ts = report.get("data", {}).get("timestamp") or str(datetime.utcnow())
    lines.append(f"Evaluation Report — {ts}\n")
    if "data" in report:
        data = report["data"]
        # health
        hc = data.get("health_checks", [])
        lines.append("Health Checks:")
        for h in hc:
            lines.append(f" - {h.get('url')}: {'OK' if h.get('ok') else 'FAIL'} (latency={h.get('latency_ms')})")
        # latency
        lat = data.get("latency_summary")
        if lat:
            lines.append("")
            lines.append("Latency Summary:")
            lines.append(f" mean: {lat.get('mean_ms')}, p95: {lat.get('p95_ms')}, count: {lat.get('count')}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
