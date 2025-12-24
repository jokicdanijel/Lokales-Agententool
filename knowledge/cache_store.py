import threading
import time
from typing import Any

from .metrics import inc_counter


class CacheEntry:
    def __init__(self, value: Any, expires_at: float | None):
        self.value = value
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        return self.expires_at is not None and time.time() >= self.expires_at


class CacheStore:
    """Simple thread-safe in-memory cache with TTL and namespace invalidation.

    Usage:
        cache = CacheStore(default_ttl=300, max_items=10000)
        cache.set(key, value, ttl_s=None, namespace='kb')
        v = cache.get(key, namespace='kb')
        cache.invalidate_namespace('kb')
        cache.invalidate_all()

    Notes:
        - Keys should already incorporate build_id / signatures (see EnhancedQueryCache)
        - This is a basic implementation for local testing; a Redis-backed store is recommended for production.
    """

    def __init__(self, default_ttl: int = 300, max_items: int = 10000):
        self._default_ttl = default_ttl
        self._max_items = max_items
        # store: namespace -> dict[key -> CacheEntry]
        self._store: dict[str, dict[str, CacheEntry]] = {}
        self._lock = threading.RLock()

    def _ensure_ns(self, namespace: str) -> None:
        if namespace not in self._store:
            self._store[namespace] = {}

    def set(self, key: str, value: Any, ttl_s: int | None = None, namespace: str = "kb") -> None:
        with self._lock:
            self._ensure_ns(namespace)
            if ttl_s is None:
                ttl_s = self._default_ttl
            expires_at = None if ttl_s is None else time.time() + ttl_s
            self._store[namespace][key] = CacheEntry(value, expires_at)
            # prune if necessary
            if len(self._store[namespace]) > self._max_items:
                # simple LRU-like by expiry (not perfect but simple)
                items = list(self._store[namespace].items())
                items.sort(key=lambda kv: (kv[1].expires_at or float("inf")))
                to_remove = len(items) - self._max_items
                for i in range(to_remove):
                    k = items[i][0]
                    del self._store[namespace][k]
                    inc_counter("kb_cache_evictions_total")

    def get(self, key: str, namespace: str = "kb") -> Any | None:
        with self._lock:
            ns = self._store.get(namespace)
            if not ns:
                inc_counter("kb_cache_misses_total")
                return None
            entry = ns.get(key)
            if not entry:
                inc_counter("kb_cache_misses_total")
                return None
            if entry.is_expired():
                # remove expired entry
                del ns[key]
                inc_counter("kb_cache_misses_total")
                return None
            inc_counter("kb_cache_hits_total")
            return entry.value

    def invalidate_namespace(self, namespace: str) -> None:
        with self._lock:
            if namespace in self._store:
                self._store[namespace] = {}

    def invalidate_all(self) -> None:
        with self._lock:
            self._store = {}

    def size(self, namespace: str | None = None) -> int:
        with self._lock:
            if namespace:
                return len(self._store.get(namespace, {}))
            else:
                return sum(len(ns) for ns in self._store.values())
