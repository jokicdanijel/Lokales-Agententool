# 🔐 RBAC Engine - PORTIER PAS-6.0
# Role-Based Access Control Engine for opena11_unlock

import logging
import time
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class RBACEngine:
    """
    Role-Based Access Control Engine

    Supports:
    - Wildcard matching (* for any resource/action)
    - Time-based permissions (expires)
    - Hierarchical resources (/admin/* matches /admin/users)
    - Multiple permission rules per subject
    """

    def __init__(self, store):
        """Initialize RBAC engine with permission store"""
        self.store = store
        self.cache = {}
        self.cache_ttl = 60  # Cache TTL in seconds
        self.cache_timestamps = {}

        logger.info("✅ RBAC Engine initialized")

    def check(self, subject: str, resource: str, action: str) -> bool:
        """
        Check if subject has permission to perform action on resource

        Args:
            subject: User or entity ID
            resource: Resource path or identifier
            action: Permission action (read, write, delete, admin)

        Returns:
            bool: True if permission granted, False otherwise
        """
        # Check cache first
        cache_key = f"{subject}:{resource}:{action}"
        if self._check_cache(cache_key):
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}: {cached_result}")
                return cached_result

        # Get permissions for subject
        permissions = self.store.get(subject)

        if not permissions:
            logger.debug(f"No permissions found for subject: {subject}")
            self._update_cache(cache_key, False)
            return False

        current_time = int(time.time())

        for rule in permissions:
            # Check expiration
            if rule.get("expires", 0) > 0 and rule["expires"] < current_time:
                logger.debug(f"Permission expired: {rule}")
                continue

            # Check resource match
            if not self._match_resource(rule.get("resource", ""), resource):
                continue

            # Check action match
            if not self._match_action(rule.get("action", ""), action):
                continue

            # Permission granted
            logger.info(f"✅ Permission granted: {subject} -> {action} on {resource}")
            self._update_cache(cache_key, True)
            return True

        logger.debug(f"❌ Permission denied: {subject} -> {action} on {resource}")
        self._update_cache(cache_key, False)
        return False

    def _match_resource(self, rule_resource: str, target_resource: str) -> bool:
        """Match resource with wildcard support"""
        # Exact match
        if rule_resource == target_resource:
            return True

        # Wildcard match (any resource)
        if rule_resource == "*":
            return True

        # Hierarchical wildcard (e.g., /admin/* matches /admin/users)
        if rule_resource.endswith("/*"):
            prefix = rule_resource[:-2]
            if target_resource.startswith(prefix):
                return True

        # Path prefix match
        if rule_resource.endswith("/"):
            if target_resource.startswith(rule_resource):
                return True

        return False

    def _match_action(self, rule_action: str, target_action: str) -> bool:
        """Match action with wildcard support"""
        # Exact match
        if rule_action == target_action:
            return True

        # Wildcard match (any action)
        if rule_action == "*":
            return True

        # Admin action implies all actions
        if rule_action == "admin":
            return True

        return False

    def _check_cache(self, key: str) -> bool:
        """Check if cache entry is valid"""
        if key not in self.cache_timestamps:
            return False

        timestamp = self.cache_timestamps[key]
        if time.time() - timestamp > self.cache_ttl:
            # Cache expired
            del self.cache[key]
            del self.cache_timestamps[key]
            return False

        return True

    def _update_cache(self, key: str, value: bool):
        """Update cache entry"""
        self.cache[key] = value
        self.cache_timestamps[key] = time.time()

    def invalidate_cache(self, subject: str = None):
        """Invalidate cache entries"""
        if subject:
            # Invalidate entries for specific subject
            keys_to_remove = [k for k in self.cache if k.startswith(f"{subject}:")]
            for key in keys_to_remove:
                del self.cache[key]
                del self.cache_timestamps[key]
            logger.debug(f"Cache invalidated for subject: {subject}")
        else:
            # Invalidate all
            self.cache.clear()
            self.cache_timestamps.clear()
            logger.debug("Full cache invalidated")

    def check_bulk(self, subject: str, checks: list[dict[str, str]]) -> list[dict[str, Any]]:
        """
        Bulk permission check

        Args:
            subject: User or entity ID
            checks: List of {resource, action} dicts

        Returns:
            List of results with allowed status
        """
        results = []

        for check in checks:
            resource = check.get("resource", "")
            action = check.get("action", "read")
            allowed = self.check(subject, resource, action)
            results.append({"resource": resource, "action": action, "allowed": allowed})

        return results

    def get_effective_permissions(self, subject: str) -> list[dict[str, Any]]:
        """Get all effective permissions for a subject (expanded wildcards)"""
        permissions = self.store.get(subject)
        effective = []
        current_time = int(time.time())

        for rule in permissions:
            # Skip expired
            if rule.get("expires", 0) > 0 and rule["expires"] < current_time:
                continue

            effective.append(
                {
                    "resource": rule.get("resource"),
                    "action": rule.get("action"),
                    "is_wildcard": rule.get("resource") == "*" or rule.get("action") == "*",
                    "expires": rule.get("expires", 0),
                    "expires_formatted": (
                        datetime.fromtimestamp(rule["expires"]).isoformat() if rule.get("expires", 0) > 0 else "never"
                    ),
                }
            )

        return effective
