"""
Tool Registry – Central mapping of agents, endpoints, and supported tools
Part of Schritt 2 (Tool-Registry & Mapping)
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path


class ToolCategory(str, Enum):
    """Tool categories for organization"""
    BROWSE = "browse"
    ANALYZE = "analyze"
    EDIT = "edit"
    MONITOR = "monitor"
    NOTIFY = "notify"
    EXECUTE = "execute"
    QUERY = "query"
    STORE = "store"


@dataclass
class Tool:
    """Definition of a single tool/command"""
    id: str  # e.g., "browse_url", "analyze_file"
    name: str  # Human-readable name
    category: ToolCategory
    description: str
    agent_id: str  # Agent that handles this tool (e.g., "opena3")
    port: int  # Agent port
    endpoint: str  # API endpoint path (e.g., "/tools/browse")
    timeout_seconds: int = 30
    requires_auth: bool = True
    params: Dict[str, Any] = field(default_factory=dict)  # Expected parameters
    response_type: str = "json"
    deprecated: bool = False
    version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "agent_id": self.agent_id,
            "port": self.port,
            "endpoint": self.endpoint,
            "timeout_seconds": self.timeout_seconds,
            "requires_auth": self.requires_auth,
            "params": self.params,
            "response_type": self.response_type,
            "deprecated": self.deprecated,
            "version": self.version
        }


@dataclass
class Agent:
    """Definition of an agent service"""
    id: str  # e.g., "opena1", "opena3", "opena4"
    name: str  # Human-readable name
    port: int  # HTTP port (12344-12399)
    host: str = "127.0.0.1"  # Loopback binding
    description: str = ""
    enabled: bool = True
    role: str = ""  # e.g., "Koordinator", "Telegram", "UI"
    tools: List[str] = field(default_factory=list)  # Tool IDs this agent handles
    dependencies: List[str] = field(default_factory=list)  # Other agents it depends on
    health_endpoint: str = "/health"
    max_concurrent: int = 100
    retry_count: int = 3
    retry_delay_ms: int = 100
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "port": self.port,
            "host": self.host,
            "description": self.description,
            "enabled": self.enabled,
            "role": self.role,
            "tools": self.tools,
            "dependencies": self.dependencies,
            "health_endpoint": self.health_endpoint,
            "max_concurrent": self.max_concurrent,
            "retry_count": self.retry_count,
            "retry_delay_ms": self.retry_delay_ms,
            "created_at": self.created_at
        }

    def get_url(self, path: str = "") -> str:
        """Get full URL for this agent"""
        return f"http://{self.host}:{self.port}{path}"


class ToolRegistry:
    """Central registry of all agents and tools"""

    def __init__(self):
        """Initialize registry with default agents and tools"""
        self.agents: Dict[str, Agent] = {}
        self.tools: Dict[str, Tool] = {}
        self._init_default_registry()

    def _init_default_registry(self):
        """Initialize with all 20 Portier agents and tools"""

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – INFRASTRUKTUR (2)
        # ──────────────────────────────────────────────────────────────────────

        # opena1 – Koordinator (Port 12344)
        self.register_agent(Agent(
            id="opena1",
            name="Portier Koordinator",
            port=12344,
            description="Central coordinator, routing, validation",
            role="Koordinator",
            tools=["status", "dispatch", "health_check"],
            dependencies=[],
            health_endpoint="/health"
        ))

        # opena2 – Archivator (Port 12345)
        self.register_agent(Agent(
            id="opena2",
            name="Archivator (Storage)",
            port=12345,
            description="Append-only persistence, safepoint deduplication, integrity",
            role="Persistence",
            tools=["store", "query", "dedupe", "verify_integrity"],
            dependencies=[],
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – KOMMUNIKATION (4)
        # ──────────────────────────────────────────────────────────────────────

        # opena3 – OpenWebUI (Port 8080, exclusive)
        self.register_agent(Agent(
            id="opena3",
            name="OpenWebUI Terminal",
            port=8080,
            description="Web-based terminal interface",
            role="Communication",
            tools=["browse", "chat", "display"],
            dependencies=["opena1", "opena2"],
            enabled=True,
            health_endpoint="/health"
        ))

        # opena4 – Telegram Agent (Port 12347)
        self.register_agent(Agent(
            id="opena4",
            name="Telegram Mobile-Anbindung",
            port=12347,
            description="Telegram messenger integration",
            role="Communication",
            tools=["send_message", "receive_message", "webhook"],
            dependencies=["opena1", "opena2"],
            enabled=True,
            health_endpoint="/health"
        ))

        # opena5 – VS Code Bridge (Port 12348)
        self.register_agent(Agent(
            id="opena5",
            name="VS Code Programmier-Bridge",
            port=12348,
            description="IDE integration for code editing and tasks",
            role="Communication",
            tools=["edit_file", "diff", "apply_patch", "run_task"],
            dependencies=["opena1", "opena2"],
            enabled=False,  # Schritt 5 pending
            health_endpoint="/health"
        ))

        # opena6 – Browser Automation (Port 12349)
        self.register_agent(Agent(
            id="opena6",
            name="Browser-Bedienung (Automation)",
            port=12349,
            description="Automated browser control and web automation",
            role="Communication",
            tools=["navigate", "click", "type", "screenshot"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – CHATBOTS SCHRIFT (2)
        # ──────────────────────────────────────────────────────────────────────

        # opena7 – Email Chatbot (Port 12350)
        self.register_agent(Agent(
            id="opena7",
            name="Email-Chatbot (Schrift)",
            port=12350,
            description="Email-based conversational AI",
            role="Chatbot",
            tools=["process_email", "reply", "classify"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena8 – WhatsApp Chatbot (Port 12351)
        self.register_agent(Agent(
            id="opena8",
            name="WhatsApp-Chatbot (Schrift)",
            port=12351,
            description="WhatsApp-based conversational AI",
            role="Chatbot",
            tools=["process_message", "send_reply", "forward"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – CHATBOTS TON (2)
        # ──────────────────────────────────────────────────────────────────────

        # opena9 – Telefon-Antwort Chatbot (Port 12352)
        self.register_agent(Agent(
            id="opena9",
            name="Telefon-Antwort Chatbot (IVR)",
            port=12352,
            description="Interactive Voice Response for incoming calls",
            role="Chatbot-Voice",
            tools=["answer_call", "process_audio", "transfer"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena10 – Telefon-Anruf Chatbot (Port 12353)
        self.register_agent(Agent(
            id="opena10",
            name="Telefon-Anruf Chatbot",
            port=12353,
            description="Outbound calling and voice automation",
            role="Chatbot-Voice",
            tools=["initiate_call", "play_audio", "collect_input"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – FUNKTIONAL (4)
        # ──────────────────────────────────────────────────────────────────────

        # opena11 – Unlock Master (Port 12354)
        self.register_agent(Agent(
            id="opena11",
            name="Unlock-Master (Decode)",
            port=12354,
            description="Security unlock, decode operations, cryptography",
            role="Functional",
            tools=["unlock", "decode", "encrypt", "verify"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena12 – Social Media Automation (Port 12355)
        self.register_agent(Agent(
            id="opena12",
            name="Sozialmedia-Automatisierung",
            port=12355,
            description="Social media sync, posting, scheduling",
            role="Functional",
            tools=["sync_accounts", "post", "schedule", "analyze"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena13 – Influencer Manager (Port 12356)
        self.register_agent(Agent(
            id="opena13",
            name="Influencer-Manager",
            port=12356,
            description="Influencer outreach and collaboration management",
            role="Functional",
            tools=["find_influencers", "propose_collab", "manage_campaign"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena14 – Calendar Agent (Port 12357)
        self.register_agent(Agent(
            id="opena14",
            name="Kalender-Agent",
            port=12357,
            description="Calendar sync, event management, scheduling",
            role="Functional",
            tools=["sync_calendar", "create_event", "schedule_meeting"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – CONTENT CREATORS (3)
        # ──────────────────────────────────────────────────────────────────────

        # opena15 – HTML Creator (Port 12358)
        self.register_agent(Agent(
            id="opena15",
            name="HTML-Creator Tool",
            port=12358,
            description="HTML generation, template rendering, code generation",
            role="ContentCreator",
            tools=["generate_html", "render_template", "validate"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena16 – Shop Creator (Port 12359)
        self.register_agent(Agent(
            id="opena16",
            name="Shop-Creator & Service",
            port=12359,
            description="E-commerce creation, shop setup, product catalog",
            role="ContentCreator",
            tools=["create_shop", "add_product", "configure_payment"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena17 – Homepage Creator (Port 12360)
        self.register_agent(Agent(
            id="opena17",
            name="Homepage-Creator & Service",
            port=12360,
            description="Homepage design, web page creation, site building",
            role="ContentCreator",
            tools=["create_homepage", "design_page", "publish"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # AGENTS – DATA MANAGEMENT (3)
        # ──────────────────────────────────────────────────────────────────────

        # opena18 – Local Archive Agent (Port 12361)
        self.register_agent(Agent(
            id="opena18",
            name="Lokaler Archiv-Agent",
            port=12361,
            description="Local storage management, backup, archival",
            role="DataManagement",
            tools=["backup", "archive", "restore", "cleanup"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena19 – Trading Agent (Port 12362)
        self.register_agent(Agent(
            id="opena19",
            name="Trading-Agent (Aktien/Crypto)",
            port=12362,
            description="Stock/crypto trading, market analysis, execution",
            role="DataManagement",
            tools=["analyze_market", "execute_trade", "manage_portfolio"],
            dependencies=["opena1", "opena2"],
            enabled=False,
            health_endpoint="/health"
        ))

        # opena20 – Dashboard Agent (Port 12363)
        self.register_agent(Agent(
            id="opena20",
            name="Dashboard-Agent (Kunden)",
            port=12363,
            description="Customer dashboard, reporting, analytics, UI serving",
            role="DataManagement",
            tools=["serve_ui", "get_data", "generate_report", "export"],
            dependencies=["opena1", "opena2"],
            enabled=True,  # Schritt 5 in progress
            health_endpoint="/health"
        ))

        # ──────────────────────────────────────────────────────────────────────
        # TOOLS
        # ──────────────────────────────────────────────────────────────────────

        # Browse Tool (opena3)
        self.register_tool(Tool(
            id="browse",
            name="Browse URL",
            category=ToolCategory.BROWSE,
            description="Open and preview a URL",
            agent_id="opena3",
            port=8080,
            endpoint="/tools/browse",
            params={"url": "string (required)", "timeout": "int (optional)"},
            timeout_seconds=30
        ))

        # Analyze File Tool (opena3)
        self.register_tool(Tool(
            id="analyze_file",
            name="Analyze File",
            category=ToolCategory.ANALYZE,
            description="Analyze file content",
            agent_id="opena3",
            port=8080,
            endpoint="/tools/analyze",
            params={"file": "string (required)", "depth": "int (optional)"},
            timeout_seconds=60
        ))

        # Edit File Tool (opena5)
        self.register_tool(Tool(
            id="edit_file",
            name="Edit File",
            category=ToolCategory.EDIT,
            description="Edit file in VS Code",
            agent_id="opena5",
            port=12348,
            endpoint="/tasks/apply",
            params={"file": "string (required)", "edits": "list (required)"},
            timeout_seconds=120,
            deprecated=False,
            version="1.0"
        ))

        # Store Data Tool (opena2)
        self.register_tool(Tool(
            id="store",
            name="Store Data",
            category=ToolCategory.STORE,
            description="Store data in Archivator",
            agent_id="opena2",
            port=12348,
            endpoint="/store/archivp",
            params={"data": "dict (required)", "src": "string (required)", "dst": "string (required)"},
            timeout_seconds=30,
            requires_auth=True
        ))

        # Query Data Tool (opena2)
        self.register_tool(Tool(
            id="query",
            name="Query Data",
            category=ToolCategory.QUERY,
            description="Query data from Archivator",
            agent_id="opena2",
            port=12348,
            endpoint="/archiv/last",
            params={"n": "int (optional)", "filter": "string (optional)"},
            timeout_seconds=30,
            requires_auth=False
        ))

        # Send Message Tool (opena4)
        self.register_tool(Tool(
            id="send_message",
            name="Send Telegram Message",
            category=ToolCategory.NOTIFY,
            description="Send message via Telegram",
            agent_id="opena4",
            port=12347,
            endpoint="/telegram/send",
            params={"chat_id": "int (required)", "text": "string (required)"},
            timeout_seconds=10,
            requires_auth=True
        ))

        # Health Check Tool (opena1)
        self.register_tool(Tool(
            id="health_check",
            name="Health Check",
            category=ToolCategory.MONITOR,
            description="Check service health",
            agent_id="opena1",
            port=12344,
            endpoint="/health",
            params={},
            timeout_seconds=5,
            requires_auth=False
        ))

        # Status Tool (opena1)
        self.register_tool(Tool(
            id="status",
            name="Service Status",
            category=ToolCategory.MONITOR,
            description="Get service status",
            agent_id="opena1",
            port=12344,
            endpoint="/api/status/all",
            params={},
            timeout_seconds=10,
            requires_auth=False
        ))

    # ──────────────────────────────────────────────────────────────────────────
    # Agent Management
    # ──────────────────────────────────────────────────────────────────────────

    def register_agent(self, agent: Agent) -> None:
        """Register an agent"""
        self.agents[agent.id] = agent

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def list_agents(self, enabled_only: bool = True) -> List[Agent]:
        """List all agents"""
        if enabled_only:
            return [a for a in self.agents.values() if a.enabled]
        return list(self.agents.values())

    def get_agents_by_role(self, role: str) -> List[Agent]:
        """Get agents by role"""
        return [a for a in self.agents.values() if a.role == role]

    # ──────────────────────────────────────────────────────────────────────────
    # Tool Management
    # ──────────────────────────────────────────────────────────────────────────

    def register_tool(self, tool: Tool) -> None:
        """Register a tool"""
        self.tools[tool.id] = tool

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get tool by ID"""
        tool = self.tools.get(tool_id)
        if tool and tool.deprecated:
            return None
        return tool

    def list_tools(self, agent_id: Optional[str] = None, category: Optional[ToolCategory] = None) -> List[Tool]:
        """List tools with optional filtering"""
        tools = [t for t in self.tools.values() if not t.deprecated]
        
        if agent_id:
            tools = [t for t in tools if t.agent_id == agent_id]
        
        if category:
            tools = [t for t in tools if t.category == category]
        
        return tools

    def get_tools_for_agent(self, agent_id: str) -> List[Tool]:
        """Get all tools for an agent"""
        return self.list_tools(agent_id=agent_id)

    def get_tools_by_category(self, category: ToolCategory) -> List[Tool]:
        """Get tools by category"""
        return self.list_tools(category=category)

    # ──────────────────────────────────────────────────────────────────────────
    # Discovery & Routing
    # ──────────────────────────────────────────────────────────────────────────

    def resolve_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Resolve tool to agent endpoint"""
        tool = self.get_tool(tool_id)
        if not tool:
            return None

        agent = self.get_agent(tool.agent_id)
        if not agent or not agent.enabled:
            return None

        return {
            "tool_id": tool.id,
            "agent_id": agent.id,
            "url": agent.get_url(tool.endpoint),
            "timeout": tool.timeout_seconds,
            "requires_auth": tool.requires_auth,
            "params": tool.params
        }

    def get_agent_endpoint(self, agent_id: str, path: str = "") -> Optional[str]:
        """Get full URL for agent endpoint"""
        agent = self.get_agent(agent_id)
        if not agent or not agent.enabled:
            return None
        return agent.get_url(path)

    # ──────────────────────────────────────────────────────────────────────────
    # Export & Serialization
    # ──────────────────────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Export registry as dictionary"""
        return {
            "agents": {aid: a.to_dict() for aid, a in self.agents.items()},
            "tools": {tid: t.to_dict() for tid, t in self.tools.items()},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def to_json(self) -> str:
        """Export registry as JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    def save_to_file(self, path: Path) -> None:
        """Save registry to JSON file"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    def load_from_file(self, path: Path) -> None:
        """Load registry from JSON file (overwrites current)"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Clear current registry
        self.agents.clear()
        self.tools.clear()
        
        # Load agents
        for agent_data in data.get("agents", {}).values():
            agent = Agent(
                id=agent_data["id"],
                name=agent_data["name"],
                port=agent_data["port"],
                host=agent_data.get("host", "127.0.0.1"),
                description=agent_data.get("description", ""),
                enabled=agent_data.get("enabled", True),
                role=agent_data.get("role", ""),
                tools=agent_data.get("tools", []),
                dependencies=agent_data.get("dependencies", [])
            )
            self.register_agent(agent)
        
        # Load tools
        for tool_data in data.get("tools", {}).values():
            tool = Tool(
                id=tool_data["id"],
                name=tool_data["name"],
                category=ToolCategory(tool_data["category"]),
                description=tool_data["description"],
                agent_id=tool_data["agent_id"],
                port=tool_data["port"],
                endpoint=tool_data["endpoint"],
                timeout_seconds=tool_data.get("timeout_seconds", 30),
                requires_auth=tool_data.get("requires_auth", True),
                params=tool_data.get("params", {}),
                response_type=tool_data.get("response_type", "json"),
                deprecated=tool_data.get("deprecated", False),
                version=tool_data.get("version", "1.0")
            )
            self.register_tool(tool)

    # ──────────────────────────────────────────────────────────────────────────
    # Statistics & Debugging
    # ──────────────────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        enabled_agents = [a for a in self.agents.values() if a.enabled]
        deprecated_tools = [t for t in self.tools.values() if t.deprecated]
        active_tools = [t for t in self.tools.values() if not t.deprecated]

        return {
            "total_agents": len(self.agents),
            "enabled_agents": len(enabled_agents),
            "total_tools": len(self.tools),
            "active_tools": len(active_tools),
            "deprecated_tools": len(deprecated_tools),
            "agents_by_role": self._count_by_role(),
            "tools_by_category": self._count_by_category()
        }

    def _count_by_role(self) -> Dict[str, int]:
        """Count agents by role"""
        count = {}
        for agent in self.agents.values():
            role = agent.role or "unassigned"
            count[role] = count.get(role, 0) + 1
        return count

    def _count_by_category(self) -> Dict[str, int]:
        """Count tools by category"""
        count = {}
        for tool in self.tools.values():
            cat = tool.category.value
            count[cat] = count.get(cat, 0) + 1
        return count

    def print_summary(self) -> None:
        """Print human-readable summary"""
        print("\n" + "=" * 80)
        print("PORTIER TOOL REGISTRY SUMMARY")
        print("=" * 80)

        print("\n📋 AGENTS:")
        for agent in sorted(self.agents.values(), key=lambda a: a.port):
            status = "✅" if agent.enabled else "⏸️ "
            print(f"  {status} {agent.id:12} ({agent.name:20}) – Port {agent.port} ({agent.role})")

        print("\n🧰 TOOLS:")
        for tool in sorted(self.tools.values(), key=lambda t: t.category.value):
            deprecated = "📦" if tool.deprecated else "✓"
            print(f"  {deprecated} {tool.id:20} → {tool.agent_id:8} ({tool.category.value})")

        print("\n📊 STATISTICS:")
        stats = self.get_stats()
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    - {k}: {v}")
            else:
                print(f"  {key}: {value}")

        print("\n" + "=" * 80 + "\n")


# Global singleton instance
_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get or create global registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def reset_registry() -> None:
    """Reset global registry (for testing)"""
    global _registry
    _registry = None
