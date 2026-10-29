"""Unit tests for Float's Model Context Protocol (MCP) support."""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from float import config, mcp, tools, server, db


MOCK_SERVER_CODE = """
import sys, json

def send(data):
    sys.stdout.write(json.dumps(data) + "\\n")
    sys.stdout.flush()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        req = json.loads(line)
    except Exception:
        continue

    msg_id = req.get("id")
    method = req.get("method")

    if method == "initialize":
        send({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "mock-calculator", "version": "1.0.0"}
            }
        })
    elif method == "notifications/initialized":
        pass
    elif method == "tools/list":
        send({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": [
                    {
                        "name": "multiply",
                        "description": "Multiply two numbers",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "x": {"type": "number"},
                                "y": {"type": "number"}
                            },
                            "required": ["x", "y"]
                        }
                    }
                ]
            }
        })
    elif method == "tools/call":
        params = req.get("params", {})
        args = params.get("arguments", {})
        x = args.get("x", 0)
        y = args.get("y", 0)
        send({
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "content": [
                    {"type": "text", "text": f"{x} * {y} = {x * y}"}
                ],
                "isError": False
            }
        })
"""


class McpTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="float-mcp-test-"))
        self.server_file = self.temp_dir / "mock_server.py"
        self.server_file.write_text(MOCK_SERVER_CODE, encoding="utf-8")
        self.config_file = self.temp_dir / "mcp.json"

    def tearDown(self):
        mcp.manager.shutdown()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_mcp_tool_schema_conversion(self):
        t = mcp.McpTool(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {"q": {"type": "string"}}},
            server="my_server",
        )
        schema = t.to_float_schema()
        self.assertEqual(schema["name"], "mcp__my_server__test_tool")
        self.assertIn("[my_server]", schema["description"])
        self.assertEqual(schema["parameters"]["type"], "object")

    def test_mcp_stdio_client_lifecycle(self):
        client = mcp.McpStdioClient("mock_calc", sys.executable, [str(self.server_file)])
        try:
            connected = client.connect()
            self.assertTrue(connected)
            self.assertEqual(client.status, "connected")
            self.assertEqual(client.server_info.get("name"), "mock-calculator")

            tools_list = client.tools
            self.assertEqual(len(tools_list), 1)
            self.assertEqual(tools_list[0].name, "multiply")

            res = client.call_tool("multiply", {"x": 6, "y": 7})
            self.assertEqual(res["text"], "6 * 7 = 42")
        finally:
            client.close()
            self.assertEqual(client.status, "disconnected")

    def test_mcp_manager_crud_and_dispatch(self):
        mgr = mcp.McpManager(config_path=self.config_file)
        try:
            # Initially empty
            self.assertEqual(mgr.get_tools(), [])
            self.assertEqual(mgr.list_servers(), [])

            # Add server
            mgr.add_server("calc", {
                "command": sys.executable,
                "args": [str(self.server_file)]
            })

            servers = mgr.list_servers()
            self.assertEqual(len(servers), 1)
            self.assertEqual(servers[0]["name"], "calc")
            self.assertEqual(servers[0]["status"], "connected")
            self.assertEqual(servers[0]["tool_count"], 1)

            # Discover tools
            float_tools = mgr.get_tools()
            self.assertEqual(len(float_tools), 1)
            self.assertEqual(float_tools[0]["name"], "mcp__calc__multiply")

            # Call tool
            call_res = mgr.call_tool("mcp__calc__multiply", {"x": 9, "y": 9})
            self.assertEqual(call_res["text"], "9 * 9 = 81")

            # Tool label
            label = mgr.tool_label("mcp__calc__multiply")
            self.assertIn("Multiply", label)
            self.assertIn("calc", label)

            # Disable server
            mgr.toggle_server("calc", enabled=False)
            self.assertEqual(mgr.get_tools(), [])

            # Re-enable
            mgr.toggle_server("calc", enabled=True)
            self.assertEqual(len(mgr.get_tools()), 1)

            # Remove server
            mgr.remove_server("calc")
            self.assertEqual(mgr.list_servers(), [])
            self.assertEqual(mgr.get_tools(), [])
        finally:
            mgr.shutdown()

    def test_tools_integration(self):
        saved_mgr = mcp.manager
        custom_mgr = mcp.McpManager(config_path=self.config_file)
        mcp.manager = custom_mgr
        try:
            custom_mgr.add_server("calc", {
                "command": sys.executable,
                "args": [str(self.server_file)]
            })

            # Check tools.tools_for
            user = {"id": 1, "role": "teacher"}
            active_tools = tools.tools_for(user, allow_computer=False)
            tool_names = [t["name"] for t in active_tools]
            self.assertIn("mcp__calc__multiply", tool_names)
            self.assertIn("create_file", tool_names)

            # Check tools.execute routing
            res = tools.execute("mcp__calc__multiply", {"x": 5, "y": 4}, user, 1)
            self.assertEqual(res["text"], "5 * 4 = 20")

            # Check tools.tool_label
            label = tools.tool_label("mcp__calc__multiply")
            self.assertIn("Multiply", label)
        finally:
            custom_mgr.shutdown()
            mcp.manager = saved_mgr


class McpServerHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(tempfile.mkdtemp(prefix="float-mcp-http-"))
        os.environ["FLOAT_DATA_DIR"] = str(cls.data_dir)
        os.environ["FLOAT_ALLOW_PLAINTEXT"] = "1"
        import importlib
        import float.config as config
        import float.db as db
        import float.server as server
        import float.mcp as mcp
        importlib.reload(config)
        importlib.reload(db)
        importlib.reload(server)
        importlib.reload(mcp)

        cls.server_file = cls.data_dir / "mock_calc.py"
        cls.server_file.write_text(MOCK_SERVER_CODE, encoding="utf-8")

        # Create user & token
        cls.user = db.create_user("operator_mcp@agency.in", "Operator MCP", "OperatorPass123!", role="admin")
        cls.token = db.create_session(int(cls.user["id"]), "127.0.0.1", "test-agent")

        cls.http_server = server.serve(host="127.0.0.1", port=0)
        cls.port = cls.http_server.socket.getsockname()[1]
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        mcp.manager.shutdown()
        cls.http_server.shutdown()
        cls.http_server.server_close()
        shutil.rmtree(cls.data_dir, ignore_errors=True)

    def call(self, path: str, payload: dict | None = None, method: str = "GET") -> tuple[int, dict]:
        url = self.base + path
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return resp.status, body
        except urllib.error.HTTPError as exc:
            body = json.loads(exc.read().decode("utf-8"))
            return exc.code, body

    def test_mcp_api_endpoints(self):
        # 1. GET /api/mcp when empty
        status, data = self.call("/api/mcp")
        self.assertEqual(status, 200)
        self.assertEqual(data["servers"], [])

        # 2. POST /api/mcp/servers (add server)
        status, data = self.call(
            "/api/mcp/servers",
            {"name": "api_calc", "command": sys.executable, "args": [str(self.server_file)]},
            method="POST",
        )
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(len(data["servers"]), 1)
        self.assertEqual(data["servers"][0]["name"], "api_calc")
        self.assertEqual(data["servers"][0]["status"], "connected")
        self.assertEqual(len(data["tools"]), 1)

        # 3. POST /api/mcp/refresh
        status, data = self.call("/api/mcp/refresh", {}, method="POST")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["servers"]), 1)

        # 3b. POST /api/mcp/servers/{name}/toggle (disable and re-enable)
        status, data = self.call("/api/mcp/servers/api_calc/toggle", {"enabled": False}, method="POST")
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertTrue(data["servers"][0]["disabled"])
        self.assertEqual(len(data["tools"]), 0)

        status, data = self.call("/api/mcp/servers/api_calc/toggle", {"enabled": True}, method="POST")
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertFalse(data["servers"][0]["disabled"])
        self.assertEqual(len(data["tools"]), 1)

        # 4. DELETE /api/mcp/servers/{name}
        status, data = self.call("/api/mcp/servers/api_calc", method="DELETE")
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(len(data["servers"]), 0)


if __name__ == "__main__":
    unittest.main()
