import threading
import queue
import time
import os
import fcntl
from concurrent.futures import Future
from typing import Callable, Any, Optional


class FileLock:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._fd = None

    def __enter__(self):
        # open file and acquire exclusive lock
        self._fd = open(self.path, 'a+')
        try:
            fcntl.lockf(self._fd.fileno(), fcntl.LOCK_EX)
        except Exception:
            self._fd.close()
            raise
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._fd:
                fcntl.lockf(self._fd.fileno(), fcntl.LOCK_UN)
                self._fd.close()
        finally:
            self._fd = None


class WriteQueue:
    """Single-writer queue for serializing commit operations.

    Usage:
        wq = WriteQueue(lock_path='/tmp/kv_lock')
        wq.start()
        fut = wq.submit(commit_fn, args)
        result = fut.result(timeout=5)
        wq.stop()

    Features:
    - Thread-safe submit
    - Optional FileLock for cross-process safety
    - Basic metrics: processed_total, failures_total, queue_depth
    """

    def __init__(self, lock_path: Optional[str] = None):
        self._q = queue.Queue()
        self._lock_path = lock_path
        self._running = False
        self._thread = None
        self._lock = threading.RLock()

        # metrics
        self._processed = 0
        self._failures = 0

    def start(self):
        with self._lock:
            if self._running:
                return
            self._running = True
            self._thread = threading.Thread(target=self._worker, daemon=True)
            self._thread.start()

    def stop(self, drain: bool = True, timeout: Optional[float] = None):
        with self._lock:
            self._running = False
        if drain:
            # wait until queue empty or timeout
            start = time.time()
            while not self._q.empty():
                if timeout and (time.time() - start) > timeout:
                    break
                time.sleep(0.01)
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def submit(self, fn: Callable[..., Any], *args, **kwargs) -> Future:
        fut = Future()
        self._q.put((fn, args, kwargs, fut))
        return fut

    def _worker(self):
        while self._running or not self._q.empty():
            try:
                job = self._q.get(timeout=0.1)
            except queue.Empty:
                continue
            fn, args, kwargs, fut = job
            try:
                if self._lock_path:
                    with FileLock(self._lock_path):
                        res = fn(*args, **kwargs)
                else:
                    res = fn(*args, **kwargs)
                self._processed += 1
                # metrics
                try:
                    from .metrics import inc_counter
                    inc_counter('writequeue_processed_total')
                except Exception:
                    pass
                fut.set_result(res)
            except Exception as e:
                self._failures += 1
                try:
                    from .metrics import inc_counter
                    inc_counter('writequeue_failures_total')
                except Exception:
                    pass
                fut.set_exception(e)
            finally:
                self._q.task_done()

    def stats(self) -> dict:
        return {
            'queue_depth': self._q.qsize(),
            'processed_total': self._processed,
            'failures_total': self._failures,
        }
