#!/usr/bin/env python3
"""
MCP Tool Server - Model Context Protocol Tools Implementation
=============================================================

Ermöglicht LLMs, Aktionen über diesen Server auszuführen.

Endpoints:
- POST /tools/list       → Alle verfügbaren Tools auflisten
- POST /tools/call       → Ein Tool ausführen
- GET  /health           → Health Check

Port: 12398 (MCP Server)
Kürzel: mcpp

Architektur:
- FastAPI + uvicorn
- Bearer Token Authentication
- Rate Limiting (10 req/min default)
- Pydantic V2 Strict Mode
- Comprehensive Error Handling

Option-2-Flow:
  LLM → opena1 → opena2 → kordp → mcp_server → Tool Execution

Port Policy:
  - Backend: 12344-12399 (✓ 12398)
  - Verboten: 8080

Security:
  - Bearer Token (ENV-only)
  - Input Validation (JSON Schema)
  - Rate Limiting
  - Audit Logging

Maintainer: ELION Team
Version: 1.0.0
Datum: 18. Dezember 2025
"""

import asyncio
import hashlib
import json
import os
import time
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# Load Bearer Token from .env
BEARER_TOKEN = None
if ENV_PATH.exists():
    with open(ENV_PATH) as f:
        for line in f:
            if line.strip().startswith("BEARER_TOKEN="):
                BEARER_TOKEN = line.split("=", 1)[1].strip()
                break

if not BEARER_TOKEN:
    print("⚠️  WARNING: BEARER_TOKEN nicht in .env gefunden!")
    BEARER_TOKEN = "dev-token-only"

# Port Policy Enforcement
PORT = 12398
ALLOWED_PORTS = range(12344, 12400)
FORBIDDEN_PORTS = [8080]

if PORT not in ALLOWED_PORTS or PORT in FORBIDDEN_PORTS:
    raise RuntimeError(f"❌ Port {PORT} verletzt Port-Policy! Erlaubt: {ALLOWED_PORTS}")

# Service Metadata
SERVICE_NAME = "mcp_tool_server"
KUERZEL = "mcpp"
VERSION = "1.0.0"

# Rate Limiting
RATE_LIMIT_REQUESTS = int(os.environ.get("MCP_RATE_LIMIT", "60"))  # per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Logging
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
AUDIT_LOG = LOG_DIR / "mcp_audit.jsonl"

# ============================================================================
# PYDANTIC V2 MODELS (STRICT MODE)
# ============================================================================


class ToolAnnotations(BaseModel):
    """MCP Tool Annotations - Hints about tool behavior"""

    title: str | None = None
    readOnlyHint: bool = False
    destructiveHint: bool = True
    idempotentHint: bool = False
    openWorldHint: bool = True

    model_config = ConfigDict(extra="forbid")


class ToolInputSchema(BaseModel):
    """JSON Schema for tool parameters"""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class ToolDefinition(BaseModel):
    """MCP Tool Definition"""

    name: str = Field(..., min_length=1, max_length=100)
    title: str | None = None
    description: str | None = Field(None, max_length=1000)
    inputSchema: ToolInputSchema
    annotations: ToolAnnotations | None = None

    model_config = ConfigDict(extra="forbid")


class ToolListRequest(BaseModel):
    """Request: tools/list"""

    cursor: str | None = None

    model_config = ConfigDict(extra="forbid")


class ToolListResponse(BaseModel):
    """Response: tools/list"""

    tools: list[ToolDefinition]
    nextCursor: str | None = None

    model_config = ConfigDict(extra="forbid")


class ToolCallRequest(BaseModel):
    """Request: tools/call"""

    name: str = Field(..., min_length=1, max_length=100)
    arguments: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")


class ToolContent(BaseModel):
    """Tool result content item"""

    type: str = "text"
    text: str

    model_config = ConfigDict(extra="forbid")


class ToolCallResponse(BaseModel):
    """Response: tools/call"""

    content: list[ToolContent]
    isError: bool = False

    model_config = ConfigDict(extra="forbid")


class HealthResponse(BaseModel):
    """Health Check Response"""

    status: str
    service: str
    kuerzel: str
    port: int
    version: str
    uptime_seconds: float
    total_tools: int
    rate_limit: int

    model_config = ConfigDict(extra="forbid")


# ============================================================================
# RATE LIMITING
# ============================================================================


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, max_requests: int = RATE_LIMIT_REQUESTS, window: int = RATE_LIMIT_WINDOW):
        self.max_requests = max_requests
        self.window = window
        self.requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request"""
        now = time.time()
        # Clean old requests
        self.requests[client_id] = [t for t in self.requests[client_id] if now - t < self.window]
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        # Record request
        self.requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        now = time.time()
        self.requests[client_id] = [t for t in self.requests[client_id] if now - t < self.window]
        return max(0, self.max_requests - len(self.requests[client_id]))


rate_limiter = RateLimiter()


# ============================================================================
# AUDIT LOGGING
# ============================================================================


def audit_log(event: str, details: dict[str, Any], client_id: str = "unknown") -> None:
    """Append audit event to JSONL log"""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        "client_id": client_id,
        "details": details,
    }
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"⚠️  Audit log error: {e}")


# ============================================================================
# TOOL REGISTRY
# ============================================================================


class ToolRegistry:
    """Registry for MCP Tools"""

    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, Callable] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: dict[str, Any],
        handler: Callable,
        title: str | None = None,
        annotations: dict[str, Any] | None = None,
    ) -> None:
        """Register a new tool"""
        self._tools[name] = {
            "name": name,
            "title": title or name.replace("_", " ").title(),
            "description": description,
            "inputSchema": input_schema,
            "annotations": annotations
            or {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
        }
        self._handlers[name] = handler

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Get all registered tools"""
        return list(self._tools.values())

    def get_tool(self, name: str) -> dict[str, Any] | None:
        """Get a specific tool definition"""
        return self._tools.get(name)

    def get_handler(self, name: str) -> Callable | None:
        """Get tool handler function"""
        return self._handlers.get(name)

    def tool_exists(self, name: str) -> bool:
        """Check if tool exists"""
        return name in self._tools


# Global registry
tool_registry = ToolRegistry()


# ============================================================================
# EXAMPLE TOOLS IMPLEMENTATION
# ============================================================================


async def calculate_sum(a: float, b: float) -> str:
    """Add two numbers together"""
    result = a + b
    return f"The sum of {a} and {b} is {result}"


async def calculate_product(a: float, b: float) -> str:
    """Multiply two numbers"""
    result = a * b
    return f"The product of {a} and {b} is {result}"


async def get_current_time(timezone_name: str = "UTC") -> str:
    """Get current time in specified timezone"""
    try:
        from zoneinfo import ZoneInfo

        tz = ZoneInfo(timezone_name)
        now = datetime.now(tz)
        return f"Current time in {timezone_name}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    except Exception as e:
        return f"Error getting time for timezone {timezone_name}: {e!s}"


async def echo_message(message: str) -> str:
    """Echo back a message (for testing)"""
    return f"Echo: {message}"


async def list_files(directory: str = ".") -> str:
    """List files in a directory (read-only, safe)"""
    try:
        path = Path(directory)
        if not path.exists():
            return f"Directory not found: {directory}"
        if not path.is_dir():
            return f"Not a directory: {directory}"

        # Security: Only allow listing within project
        abs_path = path.resolve()
        if not str(abs_path).startswith(str(PROJECT_ROOT)):
            return "Access denied: Directory outside project root"

        files = list(path.iterdir())[:50]  # Limit to 50 entries
        result = [f"{'📁' if f.is_dir() else '📄'} {f.name}" for f in files]
        return f"Contents of {directory}:\n" + "\n".join(result)
    except Exception as e:
        return f"Error listing directory: {e!s}"


async def get_system_info() -> str:
    """Get basic system information (read-only)"""
    import platform

    info = {
        "system": platform.system(),
        "release": platform.release(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
    }
    return f"System Info: {json.dumps(info, indent=2)}"


async def validate_json(json_string: str) -> str:
    """Validate if a string is valid JSON"""
    try:
        parsed = json.loads(json_string)
        return f"✅ Valid JSON with {len(str(parsed))} characters"
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON: {e!s}"


async def hash_text(text: str, algorithm: str = "sha256") -> str:
    """Generate hash of text"""
    algorithms = ["md5", "sha1", "sha256", "sha512"]
    if algorithm not in algorithms:
        return f"Unsupported algorithm. Choose from: {algorithms}"

    h = hashlib.new(algorithm)
    h.update(text.encode())
    return f"{algorithm.upper()} hash: {h.hexdigest()}"


# Register all tools
def register_default_tools() -> None:
    """Register all default tools"""

    tool_registry.register(
        name="calculate_sum",
        title="Calculate Sum",
        description="Add two numbers together",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        handler=calculate_sum,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )

    tool_registry.register(
        name="calculate_product",
        title="Calculate Product",
        description="Multiply two numbers together",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        handler=calculate_product,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )

    tool_registry.register(
        name="get_current_time",
        title="Get Current Time",
        description="Get the current time in a specified timezone",
        input_schema={
            "type": "object",
            "properties": {
                "timezone_name": {
                    "type": "string",
                    "description": "Timezone name (e.g., 'Europe/Berlin', 'UTC')",
                    "default": "UTC",
                }
            },
            "required": [],
        },
        handler=get_current_time,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": False, "openWorldHint": False},
    )

    tool_registry.register(
        name="echo_message",
        title="Echo Message",
        description="Echo back a message (useful for testing)",
        input_schema={
            "type": "object",
            "properties": {"message": {"type": "string", "description": "Message to echo"}},
            "required": ["message"],
        },
        handler=echo_message,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )

    tool_registry.register(
        name="list_files",
        title="List Files",
        description="List files in a directory (restricted to project root)",
        input_schema={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory path relative to project root",
                    "default": ".",
                }
            },
            "required": [],
        },
        handler=list_files,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )

    tool_registry.register(
        name="get_system_info",
        title="Get System Info",
        description="Get basic system information",
        input_schema={"type": "object", "properties": {}, "required": []},
        handler=get_system_info,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )

    tool_registry.register(
        name="validate_json",
        title="Validate JSON",
        description="Check if a string is valid JSON",
        input_schema={
            "type": "object",
            "properties": {"json_string": {"type": "string", "description": "JSON string to validate"}},
            "required": ["json_string"],
        },
        handler=validate_json,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )

    tool_registry.register(
        name="hash_text",
        title="Hash Text",
        description="Generate a hash of text using specified algorithm",
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to hash"},
                "algorithm": {
                    "type": "string",
                    "enum": ["md5", "sha1", "sha256", "sha512"],
                    "description": "Hash algorithm",
                    "default": "sha256",
                },
            },
            "required": ["text"],
        },
        handler=hash_text,
        annotations={"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
    )


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="MCP Tool Server",
    version=VERSION,
    description="Model Context Protocol - Tool Server for LLM Actions",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track service start time
SERVICE_START_TIME = time.time()


# ============================================================================
# SECURITY MIDDLEWARE
# ============================================================================


async def verify_bearer_token(authorization: str | None = Header(None)) -> str:
    """Verify Bearer Token and return client ID"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    token = parts[1]
    if token != BEARER_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid Bearer token")

    # Generate client ID from token hash (for rate limiting)
    client_id = hashlib.sha256(token.encode()).hexdigest()[:16]
    return client_id


async def check_rate_limit(client_id: str = Depends(verify_bearer_token)) -> str:
    """Check rate limit for client"""
    if not rate_limiter.is_allowed(client_id):
        remaining = rate_limiter.get_remaining(client_id)
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded. Try again later. Remaining: {remaining}")
    return client_id


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.get("/", response_model=dict[str, str])
async def root() -> dict[str, str]:
    """Root endpoint - Service Info"""
    return {
        "service": SERVICE_NAME,
        "kuerzel": KUERZEL,
        "version": VERSION,
        "port": str(PORT),
        "description": "MCP Tool Server - Model Context Protocol Tools",
    }


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health Check - No Auth Required"""
    uptime = time.time() - SERVICE_START_TIME
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        kuerzel=KUERZEL,
        port=PORT,
        version=VERSION,
        uptime_seconds=round(uptime, 2),
        total_tools=len(tool_registry.get_all_tools()),
        rate_limit=RATE_LIMIT_REQUESTS,
    )


@app.post("/tools/list", response_model=ToolListResponse)
async def list_tools(request: ToolListRequest, client_id: str = Depends(check_rate_limit)) -> ToolListResponse:
    """List all available tools (MCP tools/list)"""

    audit_log("tools/list", {"cursor": request.cursor}, client_id)

    tools = tool_registry.get_all_tools()
    tool_definitions = [
        ToolDefinition(
            name=t["name"],
            title=t.get("title"),
            description=t.get("description"),
            inputSchema=ToolInputSchema(**t["inputSchema"]),
            annotations=ToolAnnotations(**t.get("annotations", {})),
        )
        for t in tools
    ]

    return ToolListResponse(tools=tool_definitions, nextCursor=None)


@app.post("/tools/call", response_model=ToolCallResponse)
async def call_tool(request: ToolCallRequest, client_id: str = Depends(check_rate_limit)) -> ToolCallResponse:
    """Execute a tool (MCP tools/call)"""

    tool_name = request.name
    arguments = request.arguments

    audit_log("tools/call", {"tool": tool_name, "arguments": arguments}, client_id)

    # Check if tool exists
    if not tool_registry.tool_exists(tool_name):
        return ToolCallResponse(
            content=[ToolContent(type="text", text=f"Error: Tool '{tool_name}' not found")], isError=True
        )

    # Get handler
    handler = tool_registry.get_handler(tool_name)
    if not handler:
        return ToolCallResponse(
            content=[ToolContent(type="text", text=f"Error: No handler for tool '{tool_name}'")], isError=True
        )

    # Execute tool
    try:
        # Call handler with arguments
        if asyncio.iscoroutinefunction(handler):
            result = await handler(**arguments)
        else:
            result = handler(**arguments)

        return ToolCallResponse(content=[ToolContent(type="text", text=str(result))], isError=False)

    except TypeError as e:
        # Wrong arguments
        return ToolCallResponse(
            content=[ToolContent(type="text", text=f"Error: Invalid arguments - {e!s}")], isError=True
        )

    except Exception as e:
        # General error
        audit_log("tools/call/error", {"tool": tool_name, "error": str(e)}, client_id)
        return ToolCallResponse(content=[ToolContent(type="text", text=f"Error: {e!s}")], isError=True)


@app.get("/tools", response_model=list[dict[str, Any]])
async def get_tools_simple(client_id: str = Depends(check_rate_limit)) -> list[dict[str, Any]]:
    """Simple GET endpoint to list tools (convenience)"""
    return tool_registry.get_all_tools()


@app.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str, client_id: str = Depends(check_rate_limit)) -> dict[str, Any]:
    """Get info for a specific tool"""
    tool = tool_registry.get_tool(tool_name)
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    return tool


# ============================================================================
# NOTIFICATIONS (MCP Spec)
# ============================================================================

# Store for notification subscribers
_notification_subscribers: list[str] = []


@app.post("/notifications/tools/list_changed")
async def notify_tools_changed(client_id: str = Depends(check_rate_limit)) -> dict[str, str]:
    """Notify that tools list has changed (for dynamic tool registration)"""
    audit_log("notifications/tools/list_changed", {}, client_id)
    return {"status": "notification_sent", "message": "Tools list changed notification sent"}


# ============================================================================
# MCP PROTOCOL ENDPOINTS (VS Code MCP HTTP Transport)
# ============================================================================


class MCPRequest(BaseModel):
    """MCP JSON-RPC 2.0 Request"""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    method: str
    params: dict[str, Any] | None = None

    model_config = ConfigDict(extra="forbid")


class MCPResponse(BaseModel):
    """MCP JSON-RPC 2.0 Response"""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    result: Any | None = None
    error: dict[str, Any] | None = None


@app.post("/mcp")
async def mcp_endpoint(request: MCPRequest, client_id: str = Depends(check_rate_limit)) -> MCPResponse:
    """
    MCP JSON-RPC 2.0 Endpoint

    Supported methods:
    - initialize: Initialize the MCP session
    - tools/list: List all available tools
    - tools/call: Call a specific tool
    - ping: Health check
    """
    method = request.method
    params = request.params or {}
    req_id = request.id

    audit_log("mcp_request", {"method": method, "params": params}, client_id)

    try:
        if method == "initialize":
            # MCP initialization handshake
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": SERVICE_NAME, "version": VERSION},
                "capabilities": {"tools": {"listChanged": True}},
            }
            return MCPResponse(jsonrpc="2.0", id=req_id, result=result)

        elif method == "notifications/initialized":
            # Client confirmed initialization
            return MCPResponse(jsonrpc="2.0", id=req_id, result={})

        elif method == "tools/list":
            # List all available tools
            tools = tool_registry.get_all_tools()
            result = {"tools": tools}
            return MCPResponse(jsonrpc="2.0", id=req_id, result=result)

        elif method == "tools/call":
            # Call a specific tool
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})

            if not tool_name:
                return MCPResponse(
                    jsonrpc="2.0", id=req_id, error={"code": -32602, "message": "Missing 'name' parameter"}
                )

            if not tool_registry.tool_exists(tool_name):
                return MCPResponse(
                    jsonrpc="2.0", id=req_id, error={"code": -32601, "message": f"Tool not found: {tool_name}"}
                )

            handler = tool_registry.get_handler(tool_name)
            try:
                if asyncio.iscoroutinefunction(handler):
                    output = await handler(**tool_args)
                else:
                    output = handler(**tool_args)

                result = {
                    "content": [
                        {"type": "text", "text": json.dumps(output) if isinstance(output, dict) else str(output)}
                    ],
                    "isError": False,
                }
                return MCPResponse(jsonrpc="2.0", id=req_id, result=result)

            except Exception as e:
                return MCPResponse(
                    jsonrpc="2.0", id=req_id, result={"content": [{"type": "text", "text": str(e)}], "isError": True}
                )

        elif method == "ping":
            return MCPResponse(jsonrpc="2.0", id=req_id, result={})

        else:
            return MCPResponse(
                jsonrpc="2.0", id=req_id, error={"code": -32601, "message": f"Method not found: {method}"}
            )

    except Exception as e:
        return MCPResponse(jsonrpc="2.0", id=req_id, error={"code": -32603, "message": f"Internal error: {e!s}"})


# ============================================================================
# STARTUP
# ============================================================================


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize server on startup"""
    print(f"🚀 Starting {SERVICE_NAME} ({KUERZEL}) v{VERSION} on port {PORT}...")
    print(f"🔐 Bearer token loaded: {BEARER_TOKEN[:20]}..." if BEARER_TOKEN else "⚠️  No token!")
    print(f"⏱️  Rate limit: {RATE_LIMIT_REQUESTS} requests per minute")

    # Register default tools
    register_default_tools()
    print(f"🔧 Registered {len(tool_registry.get_all_tools())} tools")

    # Log startup
    audit_log(
        "startup", {"version": VERSION, "port": PORT, "tools": [t["name"] for t in tool_registry.get_all_tools()]}
    )


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="info")
