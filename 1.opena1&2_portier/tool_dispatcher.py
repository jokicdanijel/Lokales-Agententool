"""
Tool Dispatcher – Routes commands to correct agent and manages safepoint lifecycle
Part of Schritt 2 (Tool-Registry & Mapping)
"""

import json
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging
from enum import Enum
import urllib.request
import urllib.error

from tool_registry import get_registry, Tool, Agent

logger = logging.getLogger(__name__)


class DispatcherEvent(str, Enum):
    """Event types for dispatcher"""
    CMD = "CMD"  # Command dispatched
    RESP = "RESP"  # Response received
    ERR = "ERR"  # Error occurred
    TIMEOUT = "TIMEOUT"  # Request timeout
    UNAUTHORIZED = "UNAUTHORIZED"  # Authorization failed


class SafepointWriter:
    """Writes safepoints to append-only archive"""

    def __init__(self, archive_path: Path):
        """Initialize with archive path"""
        self.archive_path = Path(archive_path)
        self.archive_path.mkdir(parents=True, exist_ok=True)

    def get_date_folder(self) -> Path:
        """Get YYYY/MM/DD folder for today"""
        now = datetime.utcnow()
        folder = self.archive_path / now.strftime("%Y") / now.strftime("%m") / now.strftime("%d")
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def create_safepoint_name(self, src: str, dst: str, kind: DispatcherEvent) -> str:
        """Create safepoint filename: SP<ts>_src→dst_KIND.json"""
        ts = int(datetime.utcnow().timestamp() * 1e6) // 1000  # Millisecond precision
        return f"SP{ts}_{src}→{dst}_{kind.value}.json"

    def write_safepoint(
        self,
        src: str,
        dst: str,
        kind: DispatcherEvent,
        payload: Dict[str, Any],
        request_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Path]]:
        """
        Write safepoint to disk with atomic rename
        
        Returns: (success, filename, full_path)
        """
        try:
            folder = self.get_date_folder()
            filename = self.create_safepoint_name(src, dst, kind)
            full_path = folder / filename

            # Create safepoint data
            safepoint = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "src": src,
                "dst": dst,
                "kind": kind.value,
                "request_id": request_id or str(uuid.uuid4()),
                "payload": payload
            }

            # Write to temp file first
            temp_path = full_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(safepoint, f, ensure_ascii=False, indent=2)

            # Atomic rename
            temp_path.replace(full_path)

            # Append to index.jsonl
            self._append_to_index(folder, filename, src, dst, kind, request_id)

            return True, filename, full_path

        except Exception as e:
            logger.error(f"Failed to write safepoint: {e}")
            return False, "", None

    def _append_to_index(
        self,
        folder: Path,
        filename: str,
        src: str,
        dst: str,
        kind: DispatcherEvent,
        request_id: Optional[str]
    ) -> None:
        """Append entry to index.jsonl (append-only log)"""
        try:
            index_path = folder / "index.jsonl"
            index_entry = {
                "sp": filename,
                "src": src,
                "dst": dst,
                "kind": kind.value,
                "ts": datetime.utcnow().isoformat() + "Z",
                "request_id": request_id
            }
            with open(index_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to index: {e}")


class ToolDispatcher:
    """Main dispatcher for routing tool commands to agents"""

    def __init__(self, archive_path: Path = Path("./archivp")):
        """Initialize dispatcher"""
        self.registry = get_registry()
        self.safepoint_writer = SafepointWriter(archive_path)
        self.default_timeout = 30  # seconds
        self.auth_token: Optional[str] = None

    def set_auth_token(self, token: str) -> None:
        """Set authentication token for API calls"""
        self.auth_token = token

    # ──────────────────────────────────────────────────────────────────────────
    # Tool Resolution & Validation
    # ──────────────────────────────────────────────────────────────────────────

    def validate_tool_request(self, tool_id: str, agent_id: Optional[str] = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate that tool exists and can be dispatched
        
        Returns: (is_valid, error_message, tool_info)
        """
        # Check if tool exists
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return False, f"Tool '{tool_id}' not found in registry", None

        # If specific agent requested, validate match
        if agent_id and tool.agent_id != agent_id:
            return False, f"Tool '{tool_id}' is handled by '{tool.agent_id}', not '{agent_id}'", None

        # Check if agent is enabled
        agent = self.registry.get_agent(tool.agent_id)
        if not agent or not agent.enabled:
            return False, f"Agent '{tool.agent_id}' is not available", None

        # Check authorization requirement
        if tool.requires_auth and not self.auth_token:
            return False, "This tool requires authentication", None

        tool_info = self.registry.resolve_tool(tool_id)
        if not tool_info:
            return False, f"Cannot resolve tool '{tool_id}' to endpoint", None

        return True, "", tool_info

    # ──────────────────────────────────────────────────────────────────────────
    # Dispatch Operations
    # ──────────────────────────────────────────────────────────────────────────

    async def dispatch(
        self,
        tool_id: str,
        params: Dict[str, Any],
        source_agent: str = "dashboard",
        request_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Dispatch tool command to target agent
        
        Returns: (success, response_dict)
        """
        request_id = request_id or str(uuid.uuid4())

        # Validate request
        is_valid, error_msg, tool_info = self.validate_tool_request(tool_id)
        if not is_valid or tool_info is None:
            await self._write_error_safepoint(
                source_agent, "dispatcher", error_msg, request_id
            )
            return False, self._error_response(error_msg, request_id)

        target_agent = tool_info["agent_id"]
        url = tool_info["url"]
        timeout = tool_info["timeout"]

        # Write CMD safepoint
        cmd_success, cmd_filename, cmd_path = self.safepoint_writer.write_safepoint(
            src=source_agent,
            dst=target_agent,
            kind=DispatcherEvent.CMD,
            payload={
                "tool": tool_id,
                "params": params,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            request_id=request_id
        )

        if not cmd_success:
            return False, self._error_response(
                "Failed to create command safepoint",
                request_id
            )

        logger.info(f"📤 CMD safepoint created: {cmd_filename}")

        # Dispatch to agent
        try:
            response = await self._send_request(
                url=url,
                method="POST",
                payload=params,
                timeout=timeout
            )

            # Write RESP safepoint
            resp_success, resp_filename, resp_path = self.safepoint_writer.write_safepoint(
                src=target_agent,
                dst=source_agent,
                kind=DispatcherEvent.RESP,
                payload=response,
                request_id=request_id
            )

            logger.info(f"📥 RESP safepoint created: {resp_filename}")

            return True, {
                "ok": True,
                "tool": tool_id,
                "target_agent": target_agent,
                "request_id": request_id,
                "result": response,
                "cmd_safepoint": str(cmd_path) if cmd_path else None,
                "resp_safepoint": str(resp_path) if resp_success and resp_path else None
            }

        except asyncio.TimeoutError:
            # Write TIMEOUT safepoint
            self.safepoint_writer.write_safepoint(
                src=target_agent,
                dst=source_agent,
                kind=DispatcherEvent.TIMEOUT,
                payload={"error": f"Tool execution timeout after {timeout}s"},
                request_id=request_id
            )

            logger.error(f"⏱️ TIMEOUT safepoint created")
            return False, self._error_response(
                f"Tool execution timeout after {timeout}s",
                request_id
            )

        except Exception as e:
            # Write ERR safepoint
            self.safepoint_writer.write_safepoint(
                src=target_agent,
                dst=source_agent,
                kind=DispatcherEvent.ERR,
                payload={"error": str(e), "exception_type": type(e).__name__},
                request_id=request_id
            )

            logger.error(f"❌ ERR safepoint created: {e}")
            return False, self._error_response(str(e), request_id)

    async def _send_request(
        self,
        url: str,
        method: str,
        payload: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Send HTTP request to agent (using urllib)"""
        return await asyncio.get_event_loop().run_in_executor(
            None,
            self._send_request_sync,
            url,
            method,
            payload,
            timeout
        )

    def _send_request_sync(
        self,
        url: str,
        method: str,
        payload: Dict[str, Any],
        timeout: int
    ) -> Dict[str, Any]:
        """Synchronous HTTP request using urllib"""
        import json as json_lib
        
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ToolDispatcher/1.0"
        }

        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            data = json_lib.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers=headers,
                method=method.upper()
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                response_data = response.read().decode("utf-8")
                return json_lib.loads(response_data)
                
        except urllib.error.URLError as e:
            raise Exception(f"Request failed: {e}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # Error Handling & Safepoints
    # ──────────────────────────────────────────────────────────────────────────

    async def _write_error_safepoint(
        self,
        src: str,
        dst: str,
        error: str,
        request_id: str
    ) -> None:
        """Write error safepoint"""
        self.safepoint_writer.write_safepoint(
            src=src,
            dst=dst,
            kind=DispatcherEvent.ERR,
            payload={"error": error},
            request_id=request_id
        )

    def _error_response(self, error_msg: str, request_id: str) -> Dict[str, Any]:
        """Create error response in schema 8.3 format"""
        return {
            "ok": False,
            "request_id": request_id,
            "error": {
                "code": "DISPATCH_ERROR",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Registry Queries
    # ──────────────────────────────────────────────────────────────────────────

    def get_available_tools(self) -> Dict[str, Any]:
        """Get all available tools organized by agent"""
        result = {}
        for agent in self.registry.list_agents(enabled_only=True):
            tools = self.registry.get_tools_for_agent(agent.id)
            if tools:
                result[agent.id] = {
                    "agent_name": agent.name,
                    "port": agent.port,
                    "tools": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "category": t.category.value,
                            "description": t.description
                        }
                        for t in tools
                    ]
                }
        return result

    def get_tool_info(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed tool information"""
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return None

        agent = self.registry.get_agent(tool.agent_id)
        if not agent:
            return None

        return {
            "id": tool.id,
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.value,
            "agent": {
                "id": agent.id,
                "name": agent.name,
                "port": agent.port,
                "url": agent.get_url(tool.endpoint)
            },
            "timeout": tool.timeout_seconds,
            "requires_auth": tool.requires_auth,
            "params": tool.params,
            "version": tool.version,
            "deprecated": tool.deprecated
        }

    def list_agent_tools(self, agent_id: str) -> Dict[str, Any]:
        """Get all tools available for an agent"""
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent '{agent_id}' not found"}

        tools = self.registry.get_tools_for_agent(agent_id)
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "enabled": agent.enabled,
            "tools": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "endpoint": t.endpoint
                }
                for t in tools
            ]
        }
