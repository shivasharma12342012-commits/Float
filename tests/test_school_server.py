"""School-server mode: one Float computer, many teachers on other PCs.

A request carrying X-Forwarded-For is never treated as coming from the Float
computer itself, which lets these tests stand in for "a teacher on another PC".
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


class SchoolServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(tempfile.mkdtemp(prefix="float-lan-"))
        os.environ["FLOAT_DATA_DIR"] = str(cls.data_dir)
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
        self.assertEqual(self._host(f"192.168.1.20:{self.port}"), 200)
        self.assertNotEqual(self._host("evil.example.com"), 200)
        self.config.settings.lan = False
        try:
            self.assertNotEqual(self._host(f"192.168.1.20:{self.port}"), 200)
        finally:
            self.config.settings.lan = True

    def test_08_proxy_headers_never_count_as_local(self):
        import float.server as server
        class Req:
            client_address = ("127.0.0.1", 5000)
            def __init__(self, h): self.headers = h
        self.assertTrue(server.Route.local.fget(type("R", (), {"request": Req({}), "ip": "127.0.0.1"})()))
        self.assertFalse(server.Route.local.fget(type("R", (), {"request": Req({"X-Real-IP": "1.2.3.4"}), "ip": "127.0.0.1"})()))


if __name__ == "__main__":
    unittest.main()
