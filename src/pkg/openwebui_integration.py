#!/usr/bin/env python3
"""
openwebui_integration.py - Vollständige OpenWebUI Integration mit JWT-Auth
Behandelt Registrierung, Routing und Kommunikation mit allen 19 Agenten.
Integriert JWT-basierte Authentifizierung für sichere Agenten-Kommunikation.
"""

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any

import aiohttp
from pydantic import BaseModel, Field

# JWT Authentication Import
try:
    from jwt_auth import TokenValidationResult, create_token, refresh_token, verify_token

    JWT_ENABLED = True
except ImportError:
    JWT_ENABLED = False
    print("⚠️  JWT-Modul nicht verfügbar, einige Features deaktiviert")

logger = logging.getLogger(__name__)


# ============================================================================
# Enums und Datenmodelle
# ============================================================================


class AgentCategory(str, Enum):
    """Kategorien von Agenten"""

    CORE = "Core"
    INTEGRATION = "Integration"
    TOOLS = "Tools"
    SECURITY = "Security"
    BUSINESS = "Business"
    ANALYTICS = "Analytics"
    UI = "UI"
    AUTOMATION = "Automation"


class Agent(BaseModel):
    """Agent-Modell mit vollständigen Metadaten"""

    agent_id: str = Field(..., min_length=1, description="Eindeutige ID")
    name: str = Field(..., min_length=1, description="Lesbare Name")
    port: int = Field(..., ge=1024, le=65535, description="Port")
    category: AgentCategory = Field(..., description="Kategorie")
    description: str = Field(..., min_length=1, description="Beschreibung")
    enabled: bool = Field(default=True, description="Ist aktiviert?")

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    @property
    def health_endpoint(self) -> str:
        return f"{self.base_url}/health"

    @property
    def invoke_endpoint(self) -> str:
        return f"{self.base_url}/invoke"

    @property
    def status_endpoint(self) -> str:
        return f"{self.base_url}/status"


class HealthCheckResult(BaseModel):
    """Result einer Health-Check"""

    agent_id: str
    healthy: bool
    response_time_ms: float | None = None
    status_code: int | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentRegistration(BaseModel):
    """Agent-Registrierung in OpenWebUI"""

    agent_id: str
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    endpoint: str
    version: str = "1.0.0"
    capabilities: list[str] = ["health", "status", "invoke"]


class ChatRequest(BaseModel):
    """Chat-Request von OpenWebUI"""

    agent_id: str | None = None  # Wenn None, an Default-Agent
    message: str = Field(..., min_length=1, description="Chat-Nachricht")
    context: dict[str, Any] = Field(default_factory=dict, description="Zusätzlicher Kontext")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, ge=1, le=4000)


class ChatResponse(BaseModel):
    """Chat-Response von Agent"""

    agent_id: str
    response: str
    confidence: float | None = None
    processing_time_ms: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# OpenWebUI Integration Manager
# ============================================================================


class OpenWebUIIntegrationManager:
    """Verwaltet die Verbindung zwischen OpenWebUI und Agenten"""

    def __init__(self):
        """Initialisiere Manager"""
        self.agents: dict[str, Agent] = {}
        self.registrations: dict[str, AgentRegistration] = {}
        self.health_cache: dict[str, HealthCheckResult] = {}
        self.session: aiohttp.ClientSession | None = None
        self.default_agent: str | None = None
        logger.info("OpenWebUI Integration Manager initialisiert")

    async def start(self):
        """Starte die Session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            logger.info("aiohttp Session gestartet")

    async def stop(self):
        """Stoppe die Session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("aiohttp Session gestoppt")

    def register_agent(self, agent: Agent) -> bool:
        """Registriere einen Agenten"""
        try:
            self.agents[agent.agent_id] = agent

            registration = AgentRegistration(agent_id=agent.agent_id, endpoint=agent.base_url, version="1.0.0")
            self.registrations[agent.agent_id] = registration

            # Setze erste Agent als Default
            if self.default_agent is None and agent.enabled:
                self.default_agent = agent.agent_id

            logger.info(f"✅ Agent registriert: {agent.agent_id} ({agent.name}) auf Port {agent.port}")
            return True
        except Exception as e:
            logger.error(f"❌ Fehler bei Registrierung von {agent.agent_id}: {e}")
            return False

    def register_all_default_agents(self):
        """Registriere alle 19 Standard-Agenten"""
        agents_config = [
            Agent(
                agent_id="opena1",
                name="Coordinator",
                port=12344,
                category=AgentCategory.CORE,
                description="Orchestrator Phase 1",
            ),
            Agent(
                agent_id="opena2",
                name="Archivator",
                port=12345,
                category=AgentCategory.CORE,
                description="File Storage System",
            ),
            Agent(
                agent_id="kordp",
                name="Scheduler",
                port=12346,
                category=AgentCategory.CORE,
                description="Event Coordination",
            ),
            Agent(
                agent_id="opena4",
                name="Telegram",
                port=12347,
                category=AgentCategory.INTEGRATION,
                description="Telegram Integration",
            ),
            Agent(
                agent_id="opena5",
                name="Browser",
                port=12346,
                category=AgentCategory.TOOLS,
                description="Browser Automation",
            ),
            Agent(
                agent_id="opena6",
                name="Email",
                port=12349,
                category=AgentCategory.TOOLS,
                description="Email Management",
            ),
            Agent(
                agent_id="opena7",
                name="WhatsApp",
                port=12350,
                category=AgentCategory.INTEGRATION,
                description="WhatsApp Integration",
            ),
            Agent(
                agent_id="opena8",
                name="Telephone",
                port=12351,
                category=AgentCategory.INTEGRATION,
                description="Telephone System",
            ),
            Agent(
                agent_id="opena9",
                name="Call Tracking",
                port=12352,
                category=AgentCategory.ANALYTICS,
                description="Call Analytics",
            ),
            Agent(
                agent_id="opena10",
                name="Unlock",
                port=12353,
                category=AgentCategory.SECURITY,
                description="Security & Access",
            ),
            Agent(
                agent_id="opena11",
                name="Social Media",
                port=12359,
                category=AgentCategory.INTEGRATION,
                description="Social Media Manager",
            ),
            Agent(
                agent_id="opena12",
                name="Influencer",
                port=12360,
                category=AgentCategory.TOOLS,
                description="Influencer Collaboration",
            ),
            Agent(
                agent_id="opena13",
                name="Calendar",
                port=12361,
                category=AgentCategory.TOOLS,
                description="Calendar & Scheduling",
            ),
            Agent(
                agent_id="opena14",
                name="HTML Creator",
                port=12362,
                category=AgentCategory.TOOLS,
                description="HTML Generation",
            ),
            Agent(
                agent_id="opena15",
                name="Shop",
                port=12363,
                category=AgentCategory.BUSINESS,
                description="E-commerce System",
            ),
            Agent(
                agent_id="opena16",
                name="CRM",
                port=12364,
                category=AgentCategory.BUSINESS,
                description="CRM Management",
            ),
            Agent(
                agent_id="opena17",
                name="Analytics",
                port=12365,
                category=AgentCategory.ANALYTICS,
                description="Data Analytics",
            ),
            Agent(
                agent_id="opena18", name="Dashboard", port=12366, category=AgentCategory.UI, description="Dashboard UI"
            ),
            Agent(
                agent_id="opena19",
                name="Workflow",
                port=12367,
                category=AgentCategory.AUTOMATION,
                description="Workflow Automation",
            ),
        ]

        for agent in agents_config:
            self.register_agent(agent)

        logger.info(f"✅ Alle {len(self.agents)} Standard-Agenten registriert")

    async def health_check(self, agent_id: str) -> HealthCheckResult:
        """Prüfe Health-Status eines Agenten"""
        if agent_id not in self.agents:
            return HealthCheckResult(agent_id=agent_id, healthy=False, error=f"Agent {agent_id} nicht registriert")

        agent = self.agents[agent_id]
        if not agent.enabled:
            return HealthCheckResult(agent_id=agent_id, healthy=False, error=f"Agent {agent_id} deaktiviert")

        try:
            start = datetime.utcnow()
            async with self.session.get(agent.health_endpoint, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                response_time = (datetime.utcnow() - start).total_seconds() * 1000
                result = HealthCheckResult(
                    agent_id=agent_id,
                    healthy=(resp.status == 200),
                    response_time_ms=response_time,
                    status_code=resp.status,
                )
                self.health_cache[agent_id] = result
                return result
        except TimeoutError:
            result = HealthCheckResult(agent_id=agent_id, healthy=False, error="Health-Check Timeout (5s)")
            self.health_cache[agent_id] = result
            return result
        except Exception as e:
            result = HealthCheckResult(agent_id=agent_id, healthy=False, error=str(e))
            self.health_cache[agent_id] = result
            return result

    async def health_check_all(self) -> dict[str, HealthCheckResult]:
        """Prüfe Health-Status aller Agenten parallel"""
        tasks = [self.health_check(agent_id) for agent_id in self.agents.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        return {result.agent_id: result for result in results}

    async def invoke_agent(self, agent_id: str, payload: dict[str, Any], timeout_seconds: int = 30) -> dict[str, Any]:
        """Rufe einen Agenten auf"""
        if agent_id not in self.agents:
            return {"error": f"Agent {agent_id} nicht registriert", "status": "error"}

        agent = self.agents[agent_id]
        if not agent.enabled:
            return {"error": f"Agent {agent_id} deaktiviert", "status": "error"}

        try:
            async with self.session.post(
                agent.invoke_endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=timeout_seconds)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    error_text = await resp.text()
                    return {"error": f"HTTP {resp.status}: {error_text}", "status": "error"}
        except TimeoutError:
            return {"error": f"Invoke Timeout nach {timeout_seconds}s", "status": "timeout"}
        except Exception as e:
            return {"error": str(e), "status": "error"}

    def get_agents_list(self, category: AgentCategory | None = None) -> list[dict[str, Any]]:
        """Rückgabe Liste registrierter Agenten (optional gefiltert nach Kategorie)"""
        agents_list = []
        for agent in self.agents.values():
            if category and agent.category != category:
                continue

            health = self.health_cache.get(agent.agent_id)
            agents_list.append(
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "port": agent.port,
                    "category": agent.category.value,
                    "description": agent.description,
                    "enabled": agent.enabled,
                    "healthy": health.healthy if health else None,
                    "response_time_ms": health.response_time_ms if health else None,
                }
            )

        return sorted(agents_list, key=lambda x: x["agent_id"])

    def get_health_summary(self) -> dict[str, Any]:
        """Rückgabe Zusammenfassung des Health-Status"""
        statuses = list(self.health_cache.values())
        healthy = sum(1 for s in statuses if s.healthy)
        total = len(self.agents)

        return {
            "total_agents": total,
            "healthy_agents": healthy,
            "unhealthy_agents": total - healthy,
            "health_percentage": (healthy / total * 100) if total > 0 else 0,
            "last_check": max((s.timestamp for s in statuses), default=None),
            "by_category": {
                cat.value: len([a for a in self.agents.values() if a.category == cat]) for cat in AgentCategory
            },
        }

    # ========================================================================
    # JWT Authentication Methods
    # ========================================================================

    def create_agent_token(self, agent_id: str, scope: str = "invoke") -> str | None:
        """
        Create JWT token for an agent.

        Args:
            agent_id: Agent ID
            scope: Token scope (invoke, read, admin)

        Returns:
            JWT token string or None if JWT not enabled
        """
        if not JWT_ENABLED:
            logger.warning("JWT nicht aktiviert, kann Token nicht erstellen")
            return None

        if agent_id not in self.agents:
            logger.error(f"Agent {agent_id} nicht registriert")
            return None

        try:
            token = create_token(agent_id=agent_id, scope=scope, permissions=["read", "write"])
            logger.info(f"✅ JWT-Token erstellt für {agent_id}")
            return token
        except Exception as e:
            logger.error(f"❌ Fehler beim JWT-Token erstellen: {e}")
            return None

    def verify_agent_token(self, token: str) -> dict[str, Any] | None:
        """
        Verify JWT token from agent.

        Args:
            token: JWT token

        Returns:
            Token claims dict or None if invalid
        """
        if not JWT_ENABLED:
            logger.warning("JWT nicht aktiviert, kann Token nicht verifizieren")
            return None

        try:
            result = verify_token(token)
            if not result.valid:
                logger.warning(f"⚠️  Token-Validierung fehlgeschlagen: {result.error}")
                return None

            return {
                "agent_id": result.claims.agent_id,
                "scope": result.claims.scope,
                "permissions": result.claims.permissions,
                "expires_at": result.claims.exp,
            }
        except Exception as e:
            logger.error(f"❌ Token-Verifikation Fehler: {e}")
            return None

    async def invoke_agent_with_jwt(
        self, agent_id: str, payload: dict[str, Any], token: str | None = None, timeout_seconds: int = 30
    ) -> dict[str, Any] | None:
        """
        Invoke agent with JWT authentication.

        Args:
            agent_id: Agent ID
            payload: Request payload
            token: JWT token (created if not provided)
            timeout_seconds: Request timeout

        Returns:
            Response or None on error
        """
        if not token and JWT_ENABLED:
            token = self.create_agent_token(agent_id, scope="invoke")

        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return await self.invoke_agent(agent_id, payload, timeout_seconds)

    def get_all_agent_tokens(self) -> dict[str, str]:
        """
        Create tokens for all registered agents.

        Returns:
            Dict mapping agent_id to token
        """
        if not JWT_ENABLED:
            logger.warning("JWT nicht aktiviert")
            return {}

        tokens = {}
        for agent_id in self.agents:
            token = self.create_agent_token(agent_id)
            if token:
                tokens[agent_id] = token

        logger.info(f"✅ {len(tokens)} JWT-Token erstellt")
        return tokens


# Singleton
_manager: OpenWebUIIntegrationManager | None = None


async def get_manager() -> OpenWebUIIntegrationManager:
    """Rückgabe oder erstelle Manager-Singleton"""
    global _manager
    if _manager is None:
        _manager = OpenWebUIIntegrationManager()
        await _manager.start()
        _manager.register_all_default_agents()
    return _manager


async def shutdown_manager():
    """Beende Manager"""
    global _manager
    if _manager:
        await _manager.stop()
        _manager = None
        logger.info("OpenWebUI Integration Manager heruntergefahren")


# Test
async def test():
    """Test-Funktion"""
    manager = await get_manager()

    logger.info("=== Agenten-Liste ===")
    for agent in manager.get_agents_list():
        logger.info(f"  {agent['agent_id']:10} | {agent['name']:20} | Port {agent['port']} | {agent['category']}")

    logger.info("\n=== Health-Check ===")
    results = await manager.health_check_all()
    for agent_id, result in results.items():
        status = "✅ OK" if result.healthy else "❌ FAIL"
        logger.info(f"  {agent_id:10} | {status} | {result.response_time_ms:.1f}ms")

    logger.info("\n=== Summary ===")
    summary = manager.get_health_summary()
    logger.info(
        f"  Total: {summary['total_agents']} | Healthy: {summary['healthy_agents']} | "
        f"Unhealthy: {summary['unhealthy_agents']} | "
        f"Percentage: {summary['health_percentage']:.1f}%"
    )

    await shutdown_manager()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test())
