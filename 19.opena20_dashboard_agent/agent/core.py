"""Minimal Agent core wrapper with a dry-run mode for safe local testing.

- Dry-run mode avoids network calls and returns deterministic responses for testing.
- Do NOT store secrets in code; credentials are read from environment variables.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger("agent.core")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


@dataclass
class AgentConfig:
    provider: str | None = None
    model: str | None = None
    project_endpoint: str | None = None
    dry_run: bool | None = None

    def __post_init__(self) -> None:
        self.provider = self.provider or os.environ.get("AGENT_PROVIDER", "github")
        self.model = self.model or os.environ.get("AGENT_MODEL", "openai/gpt-4.1-mini")
        self.project_endpoint = self.project_endpoint or os.environ.get("FOUNDRY_PROJECT_ENDPOINT")
        if self.dry_run is None:
            self.dry_run = os.environ.get("AGENT_DRY_RUN", "true").lower() in ("1", "true", "yes")


class AgentCore:
    """Minimal, test-friendly agent wrapper."""

    def __init__(self, config: AgentConfig | None = None):
        self.config = config or AgentConfig()
        logger.info(
            "AgentCore init: provider=%s model=%s dry_run=%s",
            self.config.provider,
            self.config.model,
            self.config.dry_run,
        )

    async def run(self, prompt: str) -> str:
        logger.info("run called (dry_run=%s) prompt=%s", self.config.dry_run, prompt[:100])
        if self.config.dry_run:
            return self._dry_run_response(prompt)

        # Real implementation placeholder: integrate with Agent Framework / Foundry client
        raise RuntimeError("Real model execution not implemented. Configure a chat client.")

    def _dry_run_response(self, prompt: str) -> str:
        return f"[DRY-RUN] Received {len(prompt)} chars — response: OK"


def run_sync(prompt: str, config: AgentConfig | None = None) -> str:
    """Run agent synchronously for CLI and smoke tests."""
    return asyncio.get_event_loop().run_until_complete(AgentCore(config).run(prompt))
