"""Agency-server mode: one Float computer, many operators on other PCs.

A request carrying X-Forwarded-For is never treated as coming from the Float
computer itself, which lets these tests stand in for "an operator on another PC".
"""
from __future__ import annotations

import http.client
import json
import shutil
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
REMOTE = {"X-Forwarded-For": "10.0.0.23"}


class AgencyServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(tempfile.mkdtemp(prefix="float-lan-"))
        os.environ["FLOAT_DATA_DIR"] = str(cls.data_dir)
        os.environ["FLOAT_ALLOW_PLAINTEXT"] = "1"
        import importlib
        import float.config as config
        import float.db as db
        import float.server as server
        importlib.reload(config); importlib.reload(db); importlib.reload(server)
        cls.config = config
        config.settings.lan = True
        cls.srv = server.serve("127.0.0.1", 0)
        cls.port = cls.srv.server_port
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.config.settings.lan = False
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.data_dir, ignore_errors=True)

    def call(self, path, body=None, token=None, method=None, headers=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.base + path, data=data,
                                     method=method or ("POST" if data else "GET"))
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode() or "{}")

    def test_01_nobody_on_the_network_can_claim_the_school(self):
        status, data = self.call("/api/auth/signup", {
            "email": "intruder@x.in", "name": "Intruder", "password": "correct horse battery"},
            headers=REMOTE)
        self.assertEqual(status, 403)
        self.assertIn("Float computer", data.get("error", data.get("message", "")))

    def test_02_first_account_is_made_on_the_float_computer(self):
        status, data = self.call("/api/auth/signup", {
            "email": "admin@school.in", "name": "Admin", "password": "chalkboard sunrise",
            "school": "KV"})
        self.assertEqual(status, 200)
        self.assertEqual(data["user"]["role"], "admin")
        self.__class__.token = data["token"]

    def test_03_same_account_signs_in_from_another_pc(self):
        status, data = self.call("/api/auth/signin", {
            "email": "admin@school.in", "password": "chalkboard sunrise"}, headers=REMOTE)
        self.assertEqual(status, 200)
        self.__class__.remote_token = data["token"]

    def test_04_computer_control_is_only_offered_at_the_float_computer(self):
        _, here = self.call("/api/bootstrap", token=self.token, method="GET")
        _, there = self.call("/api/bootstrap", token=self.remote_token, method="GET", headers=REMOTE)
        self.assertTrue(here["capabilities"]["local"])
        self.assertFalse(there["capabilities"]["local"])
        self.assertFalse(there["capabilities"]["computer"])
        self.assertIn("Float computer", there["capabilities"]["computer_why"])
        self.assertTrue(there["capabilities"]["lan"])
        self.assertFalse(there["capabilities"]["drive"])

    def test_05_remote_pc_cannot_see_or_stop_what_the_float_computer_is_doing(self):
        status, data = self.call("/api/computer/status", token=self.remote_token,
                                 method="GET", headers=REMOTE)
        self.assertEqual(status, 200)
        self.assertFalse(data["available"])
        self.assertEqual(set(data), {"available", "why"})
        status, _ = self.call("/api/computer/stop", {}, token=self.remote_token, headers=REMOTE)
        self.assertEqual(status, 403)

    def test_06_google_sign_in_is_gone(self):
        status, _ = self.call("/api/auth/google/start", method="GET")
        self.assertEqual(status, 400)
        web = ROOT / "float" / "web"
        self.assertNotIn("google-signin", (web / "login.html").read_text(encoding="utf-8"))
        self.assertNotIn("/api/auth/google", (web / "login.js").read_text(encoding="utf-8"))

    def _host(self, host):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.putrequest("GET", "/login", skip_host=True)
        conn.putheader("Host", host)
        conn.endheaders()
        status = conn.getresponse().status
        conn.close()
        return status

    def test_07_host_check_allows_lan_addresses_but_not_made_up_names(self):
        import socket
        self.assertEqual(self._host(f"192.168.1.20:{self.port}"), 200)
        self.assertEqual(self._host(f"[::1]:{self.port}"), 200)
        self.assertEqual(self._host(f"{socket.gethostname().lower()}.local:{self.port}"), 200)
        self.assertNotEqual(self._host("evil.example.com"), 200)
        self.config.settings.lan = False
        try:
            self.assertNotEqual(self._host(f"192.168.1.20:{self.port}"), 200)
            self.assertEqual(self._host(f"[::1]:{self.port}"), 200)
        finally:
            self.config.settings.lan = True

    def test_08_proxy_headers_never_count_as_local(self):
        import float.server as server
        class Req:
            client_address = ("127.0.0.1", 5000)
            def __init__(self, h): self.headers = h
        self.assertTrue(server.Route.local.fget(type("R", (), {"request": Req({}), "ip": "127.0.0.1"})()))
        self.assertFalse(server.Route.local.fget(type("R", (), {"request": Req({"X-Real-IP": "1.2.3.4"}), "ip": "127.0.0.1"})()))

    def test_09_lan_flag_sets_twenty_minute_idle_timeout(self):
        self.config.settings.lan = False
        self.assertEqual(self.config.settings.idle_minutes, 45.0)
        self.config.settings.lan = True
        self.assertEqual(self.config.settings.idle_minutes, 20.0)

    def test_10_remote_chat_blocks_use_computer_tool_execution(self):
        import unittest.mock as mock
        import float.agent as agent
        import float.db as db
        user = db.get_user_by_email("admin@school.in")
        conv_id = db.new_conversation(int(user["id"]), "Test", "chat")
        fake_turns = [
            [{"type": "tool", "id": "t1", "name": "use_computer",
              "input": {"intent": "test", "steps": [{"action": "wait", "seconds": 0.01}]}},
             {"type": "done", "stop": "tool_use"}],
            [{"type": "text", "text": "Done"}, {"type": "done", "stop": "end_turn"}],
        ]
        with mock.patch("float.providers.stream", side_effect=fake_turns), \
             mock.patch("float.tools._tool_use_computer") as mock_uc:
            list(agent.run(user, conv_id, "open notepad", allow_computer=False))
            self.assertFalse(mock_uc.called)

    def test_11_tls_stalled_connection_does_not_block_other_teachers(self):
        import socket
        import ssl
        import float.server as server
        saved = os.environ.pop("FLOAT_ALLOW_PLAINTEXT", None)
        self.config.settings.allowed_hosts = "float.school.lan"
        try:
            tls = self.config.tls_files()
            if not tls:
                self.skipTest("cryptography not installed")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
                probe.bind(("127.0.0.1", 0))
                tls_port = probe.getsockname()[1]
            tls_srv = server.serve("127.0.0.1", tls_port)
            try:
                stalled = socket.create_connection(("127.0.0.1", tls_port), timeout=3)
                try:
                    ctx = ssl._create_unverified_context()
                    with urllib.request.urlopen(f"https://127.0.0.1:{tls_port}/login",
                                                context=ctx, timeout=3) as resp:
                        self.assertEqual(resp.status, 200)
                finally:
                    stalled.close()
            finally:
                tls_srv.shutdown()
                tls_srv.server_close()
        finally:
            self.config.settings.allowed_hosts = ""
            if saved is not None:
                os.environ["FLOAT_ALLOW_PLAINTEXT"] = saved

    def test_12_duplicate_port_bind_is_refused(self):
        import float.server as server
        with self.assertRaises(OSError):
            dup = server.FloatServer(("0.0.0.0", self.port), server.FloatHandler)
            dup.server_close()

    def test_13_admin_add_user_operator_role_and_set_cap_validation(self):
        status, data = self.call("/api/admin/users", {
            "email": "desk1@agency.in",
            "name": "Desk Operator 1",
            "password": "OperatorPass123!",
            "role": "operator",
            "school": "Hitech Hub",
        }, token=self.token)
        self.assertEqual(status, 200)
        added = [u for u in data["users"] if u["email"] == "desk1@agency.in"]
        self.assertEqual(len(added), 1)
        uid = added[0]["id"]

        status, _ = self.call(f"/api/admin/users/{uid}", {
            "action": "set_cap",
            "paise": "1250.0",
            "reason": "Weekend peak dispatch",
        }, token=self.token)
        self.assertEqual(status, 200)

        status, err = self.call(f"/api/admin/users/{uid}", {
            "action": "set_cap",
            "paise": "nan",
            "reason": "Test invalid cap",
        }, token=self.token)
        self.assertEqual(status, 400)
        self.assertIn("number", err.get("error", err.get("message", "")))

    def test_14_cli_status_and_doctor_commands(self):
        import main as cli_main
        rc_status = cli_main._cmd_status([])
        self.assertIn(rc_status, (0, 1))
        rc_doctor = cli_main._cmd_doctor([])
        self.assertEqual(rc_doctor, 0)

    def test_15_desk_ip_session_binding_prevents_cross_desk_replay(self):
        import float.db as db
        user = db.get_user_by_email("admin@school.in")
        desk_token = db.create_session(int(user["id"]), ip="10.0.0.42", agent="DeskBrowser/1.0")
        # Same desk IP succeeds
        resolved = db.resolve_session(desk_token, ip="10.0.0.42")
        self.assertIsNotNone(resolved)
        self.assertEqual(int(resolved["id"]), int(user["id"]))
        # Replay from another desk IP on the LAN is rejected
        hijacked = db.resolve_session(desk_token, ip="10.0.0.99")
        self.assertIsNone(hijacked)

    def test_16_non_admin_cannot_unlock_runtime_or_modify_mcp_servers(self):
        import float.db as db
        emp = db.create_user("desk2@agency.in", "Desk 2", role="teacher", password="Password12345")
        emp_token = db.create_session(int(emp["id"]), ip="127.0.0.1", agent="Test")
        status_unlock, _ = self.call("/api/unlock", {"phrase": "anything", "enable": True}, token=emp_token)
        self.assertEqual(status_unlock, 403)
        status_mcp, _ = self.call("/api/mcp/servers", {"name": "rogue", "command": "python"}, token=emp_token)
        self.assertEqual(status_mcp, 403)
        status_refresh, _ = self.call("/api/mcp/refresh", {}, token=emp_token)
        self.assertEqual(status_refresh, 403)

    def test_17_static_assets_use_etag_304_caching(self):
        req1 = urllib.request.Request(f"{self.base}/app.js", headers={"Host": "127.0.0.1"})
        with urllib.request.urlopen(req1) as resp1:
            self.assertEqual(resp1.status, 200)
            etag = resp1.headers.get("ETag")
            self.assertTrue(etag)
        req2 = urllib.request.Request(f"{self.base}/app.js", headers={"Host": "127.0.0.1", "If-None-Match": etag})
        try:
            urllib.request.urlopen(req2)
            self.fail("Expected HTTP 304 Not Modified")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 304)


if __name__ == "__main__":
    unittest.main()
