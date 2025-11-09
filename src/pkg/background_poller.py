"""
background_poller.py – Periodisches Polling aller Agenten für Live-Health-Status

Lädt im Dashboard-Startup und pollts alle registrierten Agenten im Hintergrund.
Aktualisiert last_health in der Registry, damit GET /api/status/all immer aktuell ist.

Verhindert: last_health = null, veraltete Status, tote Endpoints
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

# Globals (werden vom main_dashboard.py gesetzt)
_registry = None
_poller_task = None
_poll_interval_sec = 5
_logger = logging.getLogger("background_poller")

# ────────────────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────────────────

def set_registry(registry):
    """
    Registriere die Agent-Registry für Poller-Zugriff.
    
    Erwartet: registry mit Methoden:
      - get_all_status() → dict mit agent_id → {status, last_health, ...}
      - update_health(agent_id, is_alive, last_health_timestamp)
    """
    global _registry
    _registry = registry
    _logger.info("Registry set for polling")


async def start_polling(interval_sec: int = 5):
    """
    Starte Background-Poller mit konfigurierbarem Interval (Default: 5s).
    
    Sollte vom @app.on_event("startup") aufgerufen werden.
    """
    global _poll_interval_sec, _poller_task
    _poll_interval_sec = interval_sec
    
    if _poller_task is not None:
        _logger.warning("Poller already running")
        return
    
    _logger.info(f"Starting background poller (interval: {interval_sec}s)")
    _poller_task = asyncio.create_task(_poll_loop())


async def stop_polling():
    """Stoppe den Background-Poller (normalerweise beim Shutdown)."""
    global _poller_task
    if _poller_task is not None:
        _logger.info("Stopping background poller")
        _poller_task.cancel()
        _poller_task = None


def is_running() -> bool:
    """Prüfe, ob Poller aktiv ist."""
    return _poller_task is not None


# ────────────────────────────────────────────────────────────────────────────
# Internal Loop
# ────────────────────────────────────────────────────────────────────────────

async def _poll_loop():
    """
    Endlosschleife: Rufe alle registrierten Agenten auf, aktualisiere Health.
    Fehlertoleranz: Timeouts und Fehler loggen, aber nicht stoppen.
    """
    _logger.info("Poll loop started")
    
    while True:
        try:
            await _poll_all_agents()
        except asyncio.CancelledError:
            _logger.info("Poll loop cancelled")
            raise
        except Exception as e:
            _logger.error(f"Poll loop exception: {e}", exc_info=True)
        
        # Warte bis zum nächsten Interval
        try:
            await asyncio.sleep(_poll_interval_sec)
        except asyncio.CancelledError:
            _logger.info("Poll loop sleep cancelled")
            raise


async def _poll_all_agents():
    """
    Rufe get_all_status() auf der Registry auf.
    Das prüft alle Agenten und aktualisiert last_health.
    """
    if _registry is None:
        _logger.warning("Registry not set, skipping poll")
        return
    
    try:
        status = await _registry.get_all_status()
        
        # Kurz loggen (nur wenn sich was ändert oder je 10. Mal)
        up_count = sum(1 for s in status.values() if s.get("status") == "up")
        down_count = sum(1 for s in status.values() if s.get("status") == "down")
        
        # Log nur gelegentlich (noise reduction)
        _logger.debug(f"Poll: {up_count} up, {down_count} down, "
                     f"last_poll={datetime.now().isoformat()}")
        
    except Exception as e:
        _logger.error(f"Error during poll_all_agents: {e}", exc_info=True)


# ────────────────────────────────────────────────────────────────────────────
# Lifecycle Hooks (für main_dashboard.py)
# ────────────────────────────────────────────────────────────────────────────

async def on_startup():
    """Rufe vom @app.on_event("startup") auf."""
    try:
        await start_polling(interval_sec=5)
    except Exception as e:
        _logger.error(f"Failed to start polling: {e}", exc_info=True)


async def on_shutdown():
    """Rufe vom @app.on_event("shutdown") auf."""
    try:
        await stop_polling()
    except Exception as e:
        _logger.error(f"Failed to stop polling: {e}", exc_info=True)


# ────────────────────────────────────────────────────────────────────────────
# Diagnostics
# ────────────────────────────────────────────────────────────────────────────

def get_status() -> dict:
    """
    Diagnostics: Status des Pollers selbst.
    Nützlich für Debug-Endpoints.
    """
    return {
        "is_running": is_running(),
        "interval_sec": _poll_interval_sec,
        "registry_set": _registry is not None,
        "timestamp": datetime.now().isoformat(),
    }
