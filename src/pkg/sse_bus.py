"""
Einfacher Server-Sent-Events Bus für Live-Events im Dashboard.

API:
- publish(event: dict) -> None           # Event an alle Subscriber senden
- subscribe() -> AsyncIterator[dict]     # asynchroner Iterator für einen Client
- close() -> None                        # alle Subscriber beenden (optional)
"""

import asyncio
import contextlib
from typing import AsyncIterator, Dict, Any, List, Optional


class SSEBus:
    def __init__(self, per_subscriber_queue: int = 100, heartbeat_seconds: Optional[float] = None) -> None:
        """
        :param per_subscriber_queue: Max. Anzahl gepufferter Events pro Subscriber
        :param heartbeat_seconds:    Optionales Heartbeat-Intervall (z.B. 15.0), None = aus
        """
        self._subscribers: List[asyncio.Queue] = []
        self._lock = asyncio.Lock()
        self._per_subscriber_queue = int(per_subscriber_queue)
        self._heartbeat_seconds = heartbeat_seconds
        self._closed = False

    async def publish(self, event: Dict[str, Any]) -> None:
        """
        Sendet ein Event an alle Subscriber (best-effort).
        Verwirft Events bei vollen Queues anstatt zu blockieren.
        """
        if self._closed:
            return

        async with self._lock:
            for q in list(self._subscribers):
                try:
                    q.put_nowait(event)
                except asyncio.QueueFull:
                    # Subscriber ist zu langsam – wir verwerfen das Event, um Backpressure zu vermeiden
                    pass

    async def _send_heartbeat(self, q: asyncio.Queue) -> None:
        """
        Interner Heartbeat für einen Subscriber. Beendet sich automatisch,
        wenn der Subscriber entabonniert wird oder der Bus geschlossen wird.
        """
        if not self._heartbeat_seconds:
            return

        try:
            while (not self._closed) and (q in self._subscribers):
                await asyncio.sleep(self._heartbeat_seconds)
                # Heartbeat-Event sehr klein halten:
                hb = {"event": "heartbeat", "data": {"ts": asyncio.get_event_loop().time()}}
                try:
                    q.put_nowait(hb)
                except asyncio.QueueFull:
                    # ignorieren – der Client bekommt ohnehin bald echte Events
                    pass
        except asyncio.CancelledError:
            # normale Beendigung
            return

    async def subscribe(self) -> AsyncIterator[Dict[str, Any]]:
        """
        Erstellt eine dedizierte Queue für den Subscriber und liefert
        einen asynchronen Iterator, der Events liefert, bis:
          - der Client abbricht, oder
          - close() aufgerufen wird.
        """
        if self._closed:
            # Direkt leeren Iterator zurückgeben
            return
            yield  # pragma: no cover

        q: asyncio.Queue = asyncio.Queue(maxsize=self._per_subscriber_queue)
        heartbeat_task: Optional[asyncio.Task] = None

        async with self._lock:
            self._subscribers.append(q)
            if self._heartbeat_seconds:
                heartbeat_task = asyncio.create_task(self._send_heartbeat(q))

        try:
            while True:
                item = await q.get()
                # Bei close() schicken wir allen ein spezielles Event:
                if item is _CLOSE_SENTINEL:
                    break
                yield item
        finally:
            # Aufräumen (unsubscribe)
            async with self._lock:
                if q in self._subscribers:
                    self._subscribers.remove(q)
            if heartbeat_task:
                heartbeat_task.cancel()
                with contextlib.suppress(Exception):
                    await heartbeat_task

    async def close(self) -> None:
        """
        Beendet den Bus und signalisiert allen Subscribern, zu schließen.
        Danach werden keine Events mehr gesendet.
        """
        if self._closed:
            return
        self._closed = True
        async with self._lock:
            for q in list(self._subscribers):
                # nicht blockierend; wenn voll ist, erzwingen wir die Zustellung
                try:
                    q.put_nowait(_CLOSE_SENTINEL)
                except asyncio.QueueFull:
                    # Fallback: leeren & dann senden
                    try:
                        while not q.empty():
                            q.get_nowait()
                    except Exception:
                        pass
                    with contextlib.suppress(Exception):
                        q.put_nowait(_CLOSE_SENTINEL)


# internes Sentinel-Objekt zum sauberen Beenden
class _CloseSentinel:
    pass


_CLOSE_SENTINEL = _CloseSentinel()

# kleine Hilfs-Imports für finally/cleanup
import contextlib  # am Ende importiert, um den Kopf schlank zu halten

