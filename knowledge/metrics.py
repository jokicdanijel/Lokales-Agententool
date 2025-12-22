import threading
from typing import Dict

_lock = threading.RLock()
_counters: Dict[str, int] = {}
_gauges: Dict[str, float] = {}


def clear():
    with _lock:
        _counters.clear()
        _gauges.clear()


def inc_counter(name: str, amount: int = 1) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0) + amount


def set_gauge(name: str, value: float) -> None:
    with _lock:
        _gauges[name] = value


def get_metrics_text() -> str:
    """Return a simple Prometheus-style metrics exposition text."""
    with _lock:
        lines = []
        for k, v in sorted(_counters.items()):
            lines.append(f"{k} {v}")
        for k, v in sorted(_gauges.items()):
            lines.append(f"{k} {v}")
        return "\n".join(lines) + ("\n" if lines else "")
