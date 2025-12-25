"""
kordp/tool_resolver.py — Tool Route Resolver
Resolves tool IDs to endpoint URLs based on registry.
LOCATION: /home/danijel-jd/Dokumente/Workspace/Projekte/Gesamtprojekt/1.opena1&2_portier/kordp/tool_resolver.py
"""

import logging
from typing import Any

logger = logging.getLogger("kordp.tool_resolver")


class ToolResolver:
    """
    Resolves tool IDs to endpoint URLs.

    In production, this would integrate with tool_registry.py.
    For now, uses hardcoded mapping for core tools.
    """

    def __init__(self):
        """Initialize resolver with default routes."""
        self.routes: dict[str, dict[str, Any]] = {
            "tool_file_manager": {
                "agent_id": "opena5",
                "port": 12351,
                "endpoint": "/tool/file/execute",
                "url": "http://127.0.0.1:12351/tool/file/execute",
                "timeout": 30,
                "enabled": True,
            },
            "tool_file_searcher": {
                "agent_id": "opena5",
                "port": 12351,
                "endpoint": "/tool/search/execute",
                "url": "http://127.0.0.1:12351/tool/search/execute",
                "timeout": 30,
                "enabled": True,
            },
            "tool_text_analyzer": {
                "agent_id": "opena5",
                "port": 12351,
                "endpoint": "/tool/analyze/execute",
                "url": "http://127.0.0.1:12351/tool/analyze/execute",
                "timeout": 30,
                "enabled": True,
            },
            "tool_default": {
                "agent_id": "kordp",
                "port": 12346,
                "endpoint": "/dispatch/fallback",
                "url": "http://127.0.0.1:12346/dispatch/fallback",
                "timeout": 10,
                "enabled": True,
            },
            "workflowp": {
                "agent_id": "opena21",
                "port": 12364,
                "endpoint": "/invoke",
                "url": "http://127.0.0.1:12364/invoke",
                "timeout": 60,
                "enabled": True,
            },
        }
        logger.info(f"ToolResolver initialized with {len(self.routes)} routes")

    def resolve(self, tool_id: str) -> dict[str, Any] | None:
        """
        Resolve tool ID to route info.

        Args:
            tool_id: Tool identifier

        Returns:
            Route info dict or None if not found
        """
        route = self.routes.get(tool_id)
        if not route:
            logger.warning(f"No route found for tool: {tool_id}")
            return None

        if not route.get("enabled", True):
            logger.warning(f"Tool disabled: {tool_id}")
            return None

        return route

    def register(
        self, tool_id: str, agent_id: str, port: int, endpoint: str, timeout: int = 30, enabled: bool = True
    ) -> bool:
        """
        Register a new tool route.

        Args:
            tool_id: Tool identifier
            agent_id: Agent identifier
            port: Agent port
            endpoint: Tool endpoint path
            timeout: Request timeout in seconds
            enabled: Enable/disable flag

        Returns:
            True if registered successfully
        """
        # Validate port
        if not (12344 <= port <= 12399):
            logger.error(f"Port {port} violates policy (12344-12399)")
            return False

        url = f"http://127.0.0.1:{port}{endpoint}"

        self.routes[tool_id] = {
            "agent_id": agent_id,
            "port": port,
            "endpoint": endpoint,
            "url": url,
            "timeout": timeout,
            "enabled": enabled,
        }

        logger.info(f"Registered tool: {tool_id} → {url}")
        return True

    def unregister(self, tool_id: str) -> bool:
        """
        Unregister a tool route.

        Args:
            tool_id: Tool identifier

        Returns:
            True if unregistered successfully
        """
        if tool_id in self.routes:
            del self.routes[tool_id]
            logger.info(f"Unregistered tool: {tool_id}")
            return True

        logger.warning(f"Tool not found for unregister: {tool_id}")
        return False

    def enable(self, tool_id: str) -> bool:
        """Enable a tool route."""
        if tool_id in self.routes:
            self.routes[tool_id]["enabled"] = True
            logger.info(f"Enabled tool: {tool_id}")
            return True
        return False

    def disable(self, tool_id: str) -> bool:
        """Disable a tool route."""
        if tool_id in self.routes:
            self.routes[tool_id]["enabled"] = False
            logger.info(f"Disabled tool: {tool_id}")
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        """
        List all registered routes.

        Returns:
            List of route info dicts
        """
        return [{"tool_id": tid, **info} for tid, info in self.routes.items()]

    def list_enabled(self) -> list[dict[str, Any]]:
        """List only enabled routes."""
        return [{"tool_id": tid, **info} for tid, info in self.routes.items() if info.get("enabled", True)]

    def get_stats(self) -> dict[str, Any]:
        """Get resolver statistics."""
        total = len(self.routes)
        enabled = sum(1 for r in self.routes.values() if r.get("enabled", True))

        return {
            "total_routes": total,
            "enabled_routes": enabled,
            "disabled_routes": total - enabled,
            "agents": list(set(r["agent_id"] for r in self.routes.values())),
        }
