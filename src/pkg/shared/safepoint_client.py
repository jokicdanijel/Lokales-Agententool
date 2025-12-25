#!/usr/bin/env python3
"""
Shared Safepoint Client Module

Reusable SafepointClient for all PORTIER 3.0 agents.
This module consolidates the duplicated safepoint_client.py files
across all agent directories into a single, maintainable implementation.

Usage:
    from src.pkg.shared.safepoint_client import SafepointClient

    # Option 1: Use environment variables (default)
    client = SafepointClient()

    # Option 2: Override defaults
    client = SafepointClient(
        opena2_url="http://custom:12345",
        bearer_token="custom-token"
    )
"""

import os
from datetime import UTC, datetime
from typing import Any

import httpx


class SafepointClient:
    """Safepoint Client 3.0 – Remote Archivp Writer (for all agents except opena2)."""

    SECRET_KEYS: set[str] = {"token", "auth", "password", "apikey", "key", "secret", "credentials", "bearer"}
    CATEGORIES: set[str] = {"CMD", "RESP", "ROUTE", "DISPATCH"}

    def __init__(self, opena2_url: str | None = None, bearer_token: str | None = None):
        """Initialize SafepointClient.

        Args:
            opena2_url: Base URL for opena2 service. Defaults to env var OPENA2_URL.
            bearer_token: Bearer token for authentication. Defaults to env var BEARER_TOKEN.
        """
        self.opena2_url = opena2_url or os.getenv("OPENA2_URL", "http://127.0.0.1:12345")
        self.bearer_token = bearer_token or os.getenv("BEARER_TOKEN", "c899b90d-xxx")

    @staticmethod
    def _mask(obj: Any) -> Any:
        """Recursively mask sensitive data in objects.

        Args:
            obj: Object to mask (dict, list, or primitive)

        Returns:
            Masked copy of the object
        """
        if isinstance(obj, dict):
            return {
                k: ("***" if any(s in k.lower() for s in SafepointClient.SECRET_KEYS) else SafepointClient._mask(v))
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [SafepointClient._mask(i) for i in obj]
        return obj

    async def write(
        self, category: str, source: str, destination: str, request_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Write a safepoint to opena2.

        Args:
            category: Safepoint category (CMD, RESP, ROUTE, DISPATCH)
            source: Source agent identifier
            destination: Destination agent identifier
            request_id: Unique request identifier
            payload: Data payload to store

        Returns:
            Dict containing the stored safepoint data

        Raises:
            ValueError: If category is invalid
            httpx.HTTPError: If the request to opena2 fails
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")

        iso = datetime.now(UTC).isoformat()
        ts = int(datetime.now().timestamp())

        body = {
            "timestamp": iso,
            "sp_timestamp": ts,
            "source": source,
            "destination": destination,
            "category": category,
            "request_id": request_id,
            "payload": self._mask(payload),
            "strict": True,
        }

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{self.opena2_url}/store/{category}",
                json=body,
                headers={"Authorization": f"Bearer {self.bearer_token}"},
                timeout=15.0,
            )
        return body


__all__ = ["SafepointClient"]
