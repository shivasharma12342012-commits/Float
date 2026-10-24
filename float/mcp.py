"""Float — Model Context Protocol (MCP) support.

Connects Float to external tool providers via the open Model Context Protocol
(2024-11-05). Teachers and schools can plug in local scripts or remote services
(e.g. database lookups, calculators, web fetchers, calendar links) without changing
Float's core code.

Servers are configured in ``data/mcp.json`` matching the standard MCP format:

    {
      "mcpServers": {
        "calculator": {
          "command": "python",
          "args": ["-m", "calc_mcp"],
          "env": {}
        },
        "school_db": {
          "url": "http://10.0.0.5:8000/mcp"
        }
      }
    }

Zero external dependencies: uses Python's standard library subprocess and urllib.
"""

from __future__ import annotations

import atexit
import json
import logging
import os
import queue
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from . import config

log = logging.getLogger("float.mcp")

MCP_PROTOCOL_VERSION = "2024-11-05"
DEFAULT_TIMEOUT = 30.0
_NAME_RE = re.compile(r"^[a-zA-Z0-9_\-]+$")


class McpError(Exception):
    """Raised when an MCP protocol, communication or server error occurs."""


@dataclass
class McpTool:
    """A tool advertised by an MCP server."""

    name: str
    description: str
    parameters: dict[str, Any]
    server: str

    def to_float_schema(self) -> dict[str, Any]:
        """Convert to Float's standard tool schema for LLM providers."""
        full_name = f"mcp__{self.server}__{self.name}"
        desc = f"[{self.server}] {self.description}" if self.description else f"[{self.server}] {self.name}"
        params = self.parameters if isinstance(self.parameters, dict) and self.parameters else {
            "type": "object",
            "properties": {},
        }
        return {
            "name": full_name,
            "description": desc,
            "parameters": params,
        }


# ---------------------------------------------------------------------------
# STDIO Client
# ---------------------------------------------------------------------------
class McpStdioClient:
    """Manages an MCP server running as a local child process over stdio."""

    def __init__(
        self,
        name: str,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.name = name
        self.command = command
        self.args = list(args or [])
        self.env = dict(env or {})
        self.timeout = timeout

        self.proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stderr_thread: Optional[threading.Thread] = None
        self._pending: dict[int, queue.Queue] = {}
        self._next_id = 1
        self._lock = threading.Lock()
        self._stderr_buffer: list[str] = []

        self.status: str = "disconnected"  # connected | connecting | disconnected | error
        self.last_error: Optional[str] = None
        self.tools: list[McpTool] = []
        self.server_info: dict[str, Any] = {}

    def connect(self) -> bool:
        """Start the process and perform the MCP initialize handshake."""
        with self._lock:
            if self.proc and self.proc.poll() is None and self.status == "connected":
                return True
            self.status = "connecting"
            self.last_error = None

            merged_env = os.environ.copy()
            merged_env.update(self.env)

            cmd = [self.command, *self.args]
            creationflags = 0x08000000 if sys.platform == "win32" else 0
            try:
                self.proc = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=creationflags,
                )
            except Exception as exc:
                self.status = "error"
                self.last_error = f"Could not start '{self.command}': {exc}"
                return False

            self._reader_thread = threading.Thread(
                target=self._read_stdout, daemon=True, name=f"float-mcp-stdout-{self.name}"
            )
            self._reader_thread.start()

            self._stderr_thread = threading.Thread(
                target=self._read_stderr, daemon=True, name=f"float-mcp-stderr-{self.name}"
            )
            self._stderr_thread.start()

        # Perform MCP initialize handshake
        try:
            init_res = self._request(
                "initialize",
                {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "Float", "version": config.VERSION},
                },
                timeout=self.timeout,
            )
            self.server_info = init_res.get("serverInfo", {})

            # Send initialized notification
            self._notify("notifications/initialized", {})

            # Discover tools
            self.refresh_tools()
            self.status = "connected"
            return True
        except Exception as exc:
            self.status = "error"
            self.last_error = f"Handshake failed: {exc}"
            self.close()
            return False

    def refresh_tools(self) -> list[McpTool]:
        """Query tools/list and update cached tools."""
        res = self._request("tools/list", {}, timeout=self.timeout)
        raw_tools = res.get("tools", [])
        tool_list = []
        for t in raw_tools:
            name = str(t.get("name", "")).strip()
            if not name:
                continue
            desc = str(t.get("description", "")).strip()
            schema = t.get("inputSchema") or {"type": "object", "properties": {}}
            tool_list.append(McpTool(name=name, description=desc, parameters=schema, server=self.name))
        self.tools = tool_list
        return tool_list

    def call_tool(
        self, tool_name: str, arguments: dict[str, Any], timeout: float | None = None
    ) -> dict[str, Any]:
        """Call a tool on this server and return standard Float tool result."""
        if not self.proc or self.proc.poll() is not None:
            if not self.connect():
                return {
                    "text": f"Error: MCP server '{self.name}' could not be reached: {self.last_error}",
                    "card": None,
                }

        t = timeout or self.timeout
        try:
            res = self._request(
                "tools/call",
                {"name": tool_name, "arguments": arguments},
                timeout=t,
            )
        except Exception as exc:
            return {
                "text": f"MCP tool '{tool_name}' on server '{self.name}' failed: {exc}",
                "card": None,
            }

        content = res.get("content", [])
        text_parts = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict):
                    if c.get("type") == "text":
                        text_parts.append(str(c.get("text", "")))
                    elif c.get("type") == "image":
                        text_parts.append("[Image output from MCP tool]")
                    elif c.get("type") == "resource":
                        text_parts.append(str(c.get("resource", "")))
        elif isinstance(content, str):
            text_parts.append(content)

        text = "\n".join(text_parts).strip()
        if res.get("isError"):
            text = f"Tool reported an error: {text}"
        return {"text": text or "Tool executed successfully with no text output.", "card": None}

    def _request(self, method: str, params: dict[str, Any], timeout: float) -> dict[str, Any]:
        with self._lock:
            req_id = self._next_id
            self._next_id += 1
            reply_q: queue.Queue = queue.Queue()
            self._pending[req_id] = reply_q

            payload = {
                "jsonrpc": "2.0",
                "id": req_id,
                "method": method,
                "params": params,
            }
            if not self.proc or not self.proc.stdin or self.proc.poll() is not None:
                self._pending.pop(req_id, None)
                raise McpError(f"Server '{self.name}' is not running.")

            try:
                line = json.dumps(payload) + "\n"
                self.proc.stdin.write(line)
                self.proc.stdin.flush()
            except Exception as exc:
                self._pending.pop(req_id, None)
                raise McpError(f"Failed sending data to '{self.name}': {exc}") from exc

        try:
            msg = reply_q.get(timeout=timeout)
        except queue.Empty:
            with self._lock:
                self._pending.pop(req_id, None)
            raise McpError(f"Request '{method}' to '{self.name}' timed out after {timeout}s.") from None

        if isinstance(msg, Exception):
            raise msg
        if "error" in msg:
            err = msg["error"]
            err_msg = err.get("message") if isinstance(err, dict) else str(err)
            raise McpError(f"MCP error from '{self.name}': {err_msg}")
        return msg.get("result", {})

    def _notify(self, method: str, params: dict[str, Any]) -> None:
        with self._lock:
            if not self.proc or not self.proc.stdin or self.proc.poll() is not None:
                return
            try:
                payload = {"jsonrpc": "2.0", "method": method, "params": params}
                self.proc.stdin.write(json.dumps(payload) + "\n")
                self.proc.stdin.flush()
            except Exception:
                pass

    def _read_stdout(self) -> None:
        while self.proc and self.proc.stdout:
            try:
                line = self.proc.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except ValueError:
                    continue

                if isinstance(data, dict) and "id" in data:
                    req_id = data["id"]
                    with self._lock:
                        q = self._pending.pop(req_id, None)
                    if q:
                        q.put(data)
            except Exception:
                break

        # If stdout closed, process exited
        with self._lock:
            for q in self._pending.values():
                q.put(McpError(f"MCP server '{self.name}' exited unexpectedly."))
            self._pending.clear()
            if self.status == "connected":
                self.status = "disconnected"

    def _read_stderr(self) -> None:
        while self.proc and self.proc.stderr:
            try:
                line = self.proc.stderr.readline()
                if not line:
                    break
                self._stderr_buffer.append(line.rstrip())
                if len(self._stderr_buffer) > 100:
                    self._stderr_buffer.pop(0)
            except Exception:
                break

    def close(self) -> None:
        """Close pipes and terminate process cleanly."""
        with self._lock:
            proc = self.proc
            self.proc = None
            self.status = "disconnected"
        if proc:
            try:
                if proc.stdin and not proc.stdin.closed:
                    proc.stdin.close()
            except Exception:
                pass
            try:
                proc.terminate()
                proc.wait(timeout=1.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                if proc.stdout and not proc.stdout.closed:
                    proc.stdout.close()
            except Exception:
                pass
            try:
                if proc.stderr and not proc.stderr.closed:
                    proc.stderr.close()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# HTTP Client
# ---------------------------------------------------------------------------
class McpHttpClient:
    """Manages an MCP server communicating over HTTP JSON-RPC."""

    def __init__(
        self,
        name: str,
        url: str,
        headers: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self.name = name
        self.url = url
        self.headers = dict(headers or {})
        self.timeout = timeout
        self.status: str = "disconnected"
        self.last_error: Optional[str] = None
        self.tools: list[McpTool] = []
        self.server_info: dict[str, Any] = {}
        self._next_id = 1
        self._lock = threading.Lock()

    def connect(self) -> bool:
        try:
            init_res = self._request(
                "initialize",
                {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "Float", "version": config.VERSION},
                },
                timeout=self.timeout,
            )
            self.server_info = init_res.get("serverInfo", {})
            self._request("notifications/initialized", {}, is_notification=True)
            self.refresh_tools()
            self.status = "connected"
            self.last_error = None
            return True
        except Exception as exc:
            self.status = "error"
            self.last_error = f"HTTP connection failed: {exc}"
            return False

    def refresh_tools(self) -> list[McpTool]:
        res = self._request("tools/list", {}, timeout=self.timeout)
        raw_tools = res.get("tools", [])
        tool_list = []
        for t in raw_tools:
            name = str(t.get("name", "")).strip()
            if not name:
                continue
            desc = str(t.get("description", "")).strip()
            schema = t.get("inputSchema") or {"type": "object", "properties": {}}
            tool_list.append(McpTool(name=name, description=desc, parameters=schema, server=self.name))
        self.tools = tool_list
        return tool_list

    def call_tool(
        self, tool_name: str, arguments: dict[str, Any], timeout: float | None = None
    ) -> dict[str, Any]:
        t = timeout or self.timeout
        try:
            res = self._request("tools/call", {"name": tool_name, "arguments": arguments}, timeout=t)
        except Exception as exc:
            return {"text": f"HTTP MCP tool call failed on '{self.name}': {exc}", "card": None}

        content = res.get("content", [])
        text_parts = []
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "text":
                    text_parts.append(str(c.get("text", "")))
        elif isinstance(content, str):
            text_parts.append(content)

        text = "\n".join(text_parts).strip()
        if res.get("isError"):
            text = f"Tool reported an error: {text}"
        return {"text": text or "Tool executed successfully with no text output.", "card": None}

    def _request(
        self, method: str, params: dict[str, Any], timeout: float = DEFAULT_TIMEOUT, is_notification: bool = False
    ) -> dict[str, Any]:
        with self._lock:
            req_id = self._next_id
            self._next_id += 1

        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
        if not is_notification:
            payload["id"] = req_id

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"Float/{config.VERSION}",
            **self.headers,
        }
        req = urllib.request.Request(self.url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if is_notification:
                    return {}
                body = resp.read().decode("utf-8", errors="replace")
                parsed = json.loads(body)
                if isinstance(parsed, dict) and "error" in parsed:
                    err = parsed["error"]
                    err_msg = err.get("message") if isinstance(err, dict) else str(err)
                    raise McpError(f"MCP error from '{self.name}': {err_msg}")
                return parsed.get("result", {})
        except urllib.error.URLError as exc:
            raise McpError(f"Could not reach '{self.url}': {exc}") from exc
        except TimeoutError:
            raise McpError(f"Request to '{self.url}' timed out.") from None

    def close(self) -> None:
        self.status = "disconnected"


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------
class McpManager:
    """Manages configured MCP servers, active client processes and tool routing."""

    def __init__(self, config_path: Optional[Path] = None) -> None:
        self._custom_config_path = config_path
        self.clients: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._initialised = False

    @property
    def config_path(self) -> Path:
        if self._custom_config_path:
            return self._custom_config_path
        return config.mcp_config_path()

    def load_config(self) -> dict[str, Any]:
        """Read mcp.json, returning empty structure if not found."""
        path = self.config_path
        if not path.exists():
            return {"mcpServers": {}}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {"mcpServers": {}}
            if "mcpServers" not in data or not isinstance(data["mcpServers"], dict):
                data["mcpServers"] = {}
            return data
        except Exception:
            return {"mcpServers": {}}

    def save_config(self, data: dict[str, Any]) -> None:
        """Write mcp.json safely."""
        path = self.config_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def ensure_started(self) -> None:
        """Initialize and connect to configured servers if not already done."""
        if self._initialised:
            return
        with self._lock:
            if self._initialised:
                return
            self._initialised = True
        self.init_servers()

    def init_servers(self) -> None:
        """Start clients for all non-disabled servers in mcp.json."""
        cfg = self.load_config()
        servers = cfg.get("mcpServers", {})
        for name, spec in servers.items():
            if not isinstance(spec, dict) or spec.get("disabled"):
                continue
            self._start_client(name, spec)

    def _start_client(self, name: str, spec: dict[str, Any]) -> Optional[Any]:
        with self._lock:
            old = self.clients.get(name)
            if old:
                old.close()

            url = spec.get("url")
            command = spec.get("command")

            if command:
                args = spec.get("args") or []
                env = spec.get("env") or {}
                client = McpStdioClient(name=name, command=command, args=args, env=env)
            elif url:
                headers = spec.get("headers") or {}
                client = McpHttpClient(name=name, url=url, headers=headers)
            else:
                return None

            self.clients[name] = client

        # Connect client (non-blocking if handshake takes normal time)
        client.connect()
        return client

    def get_tools(self) -> list[dict[str, Any]]:
        """Return all available MCP tools formatted for Float's LLM tool schemas."""
        self.ensure_started()
        tools = []
        with self._lock:
            clients = list(self.clients.values())
        for c in clients:
            if c.status == "connected":
                for t in c.tools:
                    tools.append(t.to_float_schema())
        return tools

    def is_mcp_tool(self, name: str) -> bool:
        """Check if a tool name belongs to an MCP server."""
        return str(name).startswith("mcp__")

    def tool_label(self, full_name: str) -> str:
        """Return user-friendly label for UI streaming."""
        if not self.is_mcp_tool(full_name):
            return "Using tool"
        parts = full_name.split("__", 2)
        if len(parts) >= 3:
            server, tool = parts[1], parts[2]
            clean_tool = tool.replace("_", " ").title()
            return f"{clean_tool} ({server})"
        return "Using MCP tool"

    def call_tool(
        self, full_name: str, arguments: dict[str, Any], timeout: float | None = None
    ) -> dict[str, Any]:
        """Execute a tool call against the appropriate MCP server."""
        self.ensure_started()
        if not self.is_mcp_tool(full_name):
            return {"text": f"'{full_name}' is not an MCP tool.", "card": None}
        parts = full_name.split("__", 2)
        if len(parts) < 3:
            return {"text": f"Malformed MCP tool name '{full_name}'.", "card": None}
        server_name, tool_name = parts[1], parts[2]

        with self._lock:
            client = self.clients.get(server_name)
        if not client:
            return {
                "text": f"MCP server '{server_name}' is not running or not configured.",
                "card": None,
            }
        return client.call_tool(tool_name, arguments, timeout=timeout)

    def list_servers(self) -> list[dict[str, Any]]:
        """Return list of configured servers and their current status."""
        self.ensure_started()
        cfg = self.load_config()
        servers = cfg.get("mcpServers", {})
        out = []
        with self._lock:
            for name, spec in servers.items():
                if not isinstance(spec, dict):
                    continue
                client = self.clients.get(name)
                is_disabled = bool(spec.get("disabled"))
                status = "disabled" if is_disabled else (client.status if client else "disconnected")
                err = client.last_error if client else None
                tools_info = [
                    {"name": t.name, "description": t.description, "parameters": t.parameters}
                    for t in (client.tools if client else [])
                ]
                out.append({
                    "name": name,
                    "command": spec.get("command", ""),
                    "args": spec.get("args", []),
                    "url": spec.get("url", ""),
                    "disabled": is_disabled,
                    "status": status,
                    "error": err,
                    "server_info": client.server_info if client else {},
                    "tools": tools_info,
                    "tool_count": len(tools_info),
                })
        return out

    def add_server(self, name: str, spec: dict[str, Any]) -> dict[str, Any]:
        """Add or update an MCP server configuration."""
        name = str(name).strip()
        if not name or not _NAME_RE.match(name):
            raise ValueError("Server name must contain only letters, numbers, hyphens or underscores.")
        if not spec.get("command") and not spec.get("url"):
            raise ValueError("Server configuration must specify either 'command' or 'url'.")

        cfg = self.load_config()
        cfg["mcpServers"][name] = spec
        self.save_config(cfg)

        if not spec.get("disabled"):
            self._start_client(name, spec)
        else:
            with self._lock:
                old = self.clients.pop(name, None)
            if old:
                old.close()

        return {"ok": True, "servers": self.list_servers()}

    def remove_server(self, name: str) -> dict[str, Any]:
        """Remove an MCP server from configuration and stop its process."""
        name = str(name).strip()
        cfg = self.load_config()
        if name in cfg.get("mcpServers", {}):
            del cfg["mcpServers"][name]
            self.save_config(cfg)
        with self._lock:
            client = self.clients.pop(name, None)
        if client:
            client.close()
        return {"ok": True, "servers": self.list_servers()}

    def toggle_server(self, name: str, enabled: bool) -> dict[str, Any]:
        """Enable or disable a server."""
        name = str(name).strip()
        cfg = self.load_config()
        if name not in cfg.get("mcpServers", {}):
            raise KeyError(f"No such MCP server '{name}'.")
        cfg["mcpServers"][name]["disabled"] = not enabled
        self.save_config(cfg)

        if enabled:
            self._start_client(name, cfg["mcpServers"][name])
        else:
            with self._lock:
                client = self.clients.pop(name, None)
            if client:
                client.close()
        return {"ok": True, "servers": self.list_servers()}

    def refresh(self) -> dict[str, Any]:
        """Refresh tools and reconnect disconnected active servers."""
        self.ensure_started()
        cfg = self.load_config()
        servers = cfg.get("mcpServers", {})
        for name, spec in servers.items():
            if not isinstance(spec, dict) or spec.get("disabled"):
                continue
            with self._lock:
                client = self.clients.get(name)
            if not client or client.status != "connected":
                self._start_client(name, spec)
            else:
                try:
                    client.refresh_tools()
                except Exception:
                    pass
        return {"ok": True, "servers": self.list_servers(), "tools": self.get_tools()}

    def shutdown(self) -> None:
        """Close all running client connections."""
        with self._lock:
            clients = list(self.clients.values())
            self.clients.clear()
            self._initialised = False
        for c in clients:
            try:
                c.close()
            except Exception:
                pass


# Module-level singleton
manager = McpManager()


def get_tools() -> list[dict[str, Any]]:
    return manager.get_tools()


def is_mcp_tool(name: str) -> bool:
    return manager.is_mcp_tool(name)


def tool_label(name: str) -> str:
    return manager.tool_label(name)


def call_tool(name: str, arguments: dict[str, Any], timeout: float | None = None) -> dict[str, Any]:
    return manager.call_tool(name, arguments, timeout=timeout)


def list_servers() -> list[dict[str, Any]]:
    return manager.list_servers()


def add_server(name: str, spec: dict[str, Any]) -> dict[str, Any]:
    return manager.add_server(name, spec)


def remove_server(name: str) -> dict[str, Any]:
    return manager.remove_server(name)


def toggle_server(name: str, enabled: bool) -> dict[str, Any]:
    return manager.toggle_server(name, enabled)


def refresh() -> dict[str, Any]:
    return manager.refresh()


def shutdown() -> None:
    manager.shutdown()


atexit.register(shutdown)
