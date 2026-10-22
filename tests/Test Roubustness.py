"""Guards against the kinds of bug that make an app feel unreliable.

These are cheap checks that fail loudly the moment someone edits the project and
breaks something a teacher would only discover mid-lesson:

* a Python module whose file name does not match its import (works on Windows,
  breaks everywhere else, and broke Float once already);
* a button or panel in app.js that points at an element index.html no longer has;
* a front-end call to an API route that does not exist;
* a temporary password that can still be used for everything;
* a crash that leaks internals to the teacher instead of a calm message.

Run with: python -m unittest discover -s tests
"""

from __future__ import annotations

import ast
import json
import os
import re
import shutil
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PACKAGE = ROOT / "float"
WEB = PACKAGE / "web"


# ---------------------------------------------------------------------------
# static consistency
# ---------------------------------------------------------------------------

class StaticConsistencyTests(unittest.TestCase):
    def test_every_internal_import_matches_a_file_name_exactly(self):
        """`from . import attachments` must find `attachments.py`, not `Attachments.py`.
        Windows forgives the difference; Linux and macOS do not."""
        on_disk = {p.stem for p in PACKAGE.glob("*.py")}
        problems = []
        for path in PACKAGE.glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.level == 1:
                    names = [node.module] if node.module else [a.name for a in node.names]
                    for name in names:
                        head = name.split(".")[0]
                        if head not in on_disk:
                            problems.append(f"{path.name}: imports '{head}' but no float/{head}.py (check capitalisation)")
        self.assertEqual(problems, [])

    def test_every_element_app_js_looks_up_exists_in_index_html(self):
        html = (WEB / "index.html").read_text(encoding="utf-8")
        js = (WEB / "app.js").read_text(encoding="utf-8")
        present = set(re.findall(r'\bid="([^"]+)"', html))
        # Elements the script builds itself are fine; only static lookups are checked.
        created = set(re.findall(r'\.id\s*=\s*"([^"]+)"', js))
        wanted = set(re.findall(r'\$\("([^"]+)"\)', js))
        missing = sorted(wanted - present - created)
        self.assertEqual(missing, [], f"app.js looks up ids that index.html does not define: {missing}")

    def test_every_api_path_the_front_end_calls_has_a_route(self):
        import float.server as server

        patterns = [(verb, pattern) for verb, pattern, _h, _a in server._routes]
        paths = set()
        for name in ("app.js", "admin.js", "login.js"):
            text = (WEB / name).read_text(encoding="utf-8")
            for found in re.findall(r"""["'`](/api/[A-Za-z0-9_\-/${}.]*)""", text):
                paths.add(re.sub(r"\$\{[^}]*\}", "1", found).rstrip("/"))
        unknown = []
        for path in sorted(paths):
            if not any(p.match(path) for _verb, p in patterns):
                unknown.append(path)
        self.assertEqual(unknown, [], f"front end calls routes the server does not have: {unknown}")


# ---------------------------------------------------------------------------
# behaviour, through the real server
# ---------------------------------------------------------------------------

class RobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(tempfile.mkdtemp(prefix="float-robust-"))
        os.environ["FLOAT_DATA_DIR"] = str(cls.data_dir)
        os.environ["FLOAT_ALLOW_PLAINTEXT"] = "1"
        import importlib
        import float.config as config
        import float.db as db
        import float.server as server
        importlib.reload(config)
        importlib.reload(db)
        importlib.reload(server)
        cls.server_module = server
        cls.srv = server.serve("127.0.0.1", 0)
        cls.base = f"http://127.0.0.1:{cls.srv.server_port}"
        time.sleep(0.2)

        status, data = cls.call("/api/auth/signup", {
            "email": "head@school.edu.in", "name": "Head Teacher",
            "password": "chalkboard sunrise", "school": "Test School",
        })
        assert status == 200, data
        cls.admin_token = data["token"]

        status, data = cls.call("/api/admin/users", {
            "email": "new@school.edu.in", "name": "New Teacher", "role": "teacher",
        }, token=cls.admin_token)
        assert status == 200, data
        cls.temp_password = data["temp_password"]

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.data_dir, ignore_errors=True)

    @classmethod
    def call(cls, path, body=None, token=None, method=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(cls.base + path, data=data,
                                     method=method or ("POST" if data else "GET"))
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())

    # -- session tokens never travel in the URL --------------------------------

    def test_a_token_in_the_url_is_not_accepted(self):
        status, _ = self.call(f"/api/bootstrap?token={self.admin_token}")
        self.assertEqual(status, 401)
        status, _ = self.call("/api/bootstrap", token=self.admin_token)
        self.assertEqual(status, 200)

    # -- temporary passwords --------------------------------------------------

    def test_temporary_password_can_only_be_used_to_choose_a_real_one(self):
        status, data = self.call("/api/auth/signin", {
            "email": "new@school.edu.in", "password": self.temp_password})
        self.assertEqual(status, 200)
        self.assertTrue(data["must_change"])
        token = data["token"]

        # The app shell still loads, and says why Settings is about to open.
        status, boot = self.call("/api/bootstrap", token=token)
        self.assertEqual(status, 200)
        self.assertTrue(boot["user"]["must_change"])

        # Everything else is held back, and the reply says what to do.
        for method, path, body in (("GET", "/api/classes", None),
                                   ("POST", "/api/classes", {"name": "7C"}),
                                   ("POST", "/api/chat", {"message": "hello"}),
                                   ("GET", "/api/artifacts", None)):
            status, data = self.call(path, body, token=token, method=method)
            self.assertEqual(status, 403, f"{method} {path} should wait for a new password")
            self.assertTrue(data.get("must_change"))
            self.assertIn("password", data["error"].lower())

        # A weak choice is refused and changes nothing.
        status, _ = self.call("/api/me/password", {
            "current": self.temp_password, "new": "12345678"}, token=token)
        self.assertEqual(status, 400)
        status, _ = self.call("/api/classes", token=token, method="GET")
        self.assertEqual(status, 403)

        # A real one unlocks the account, with no need to sign in again.
        status, _ = self.call("/api/me/password", {
            "current": self.temp_password, "new": "monsoon library window"}, token=token)
        self.assertEqual(status, 200)
        status, _ = self.call("/api/classes", token=token, method="GET")
        self.assertEqual(status, 200)
        status, boot = self.call("/api/bootstrap", token=token)
        self.assertFalse(boot["user"]["must_change"])

    # -- unexpected errors ----------------------------------------------------

    def test_an_unexpected_crash_is_calm_logged_and_leaks_nothing(self):
        server = self.server_module

        def boom(ctx):
            raise RuntimeError("secret-internal-detail C:\\Users\\someone\\float\\data")

        server.route("GET", "/api/_boom")(boom)
        try:
            status, data = self.call("/api/_boom", token=self.admin_token)
        finally:
            server._routes[:] = [r for r in server._routes if "_boom" not in r[1].pattern]

        self.assertEqual(status, 500)
        self.assertNotIn("secret-internal-detail", data["error"])
        self.assertNotIn("Users", data["error"])
        self.assertIn("ref ", data["error"])
        self.assertIn("safe", data["error"].lower())

        log = self.data_dir / "float_errors.log"
        self.assertTrue(log.exists(), "the real error should be written to data/float_errors.log")
        self.assertIn("secret-internal-detail", log.read_text(encoding="utf-8"))

        # And the server is still perfectly healthy afterwards.
        status, _ = self.call("/api/bootstrap", token=self.admin_token)
        self.assertEqual(status, 200)

    def test_logging_never_raises_even_with_no_stderr_and_an_unwritable_folder(self):
        """When Float runs windowless there is no stderr; a logging failure must not
        turn one error into a dropped connection."""
        server = self.server_module
        saved = sys.stderr
        sys.stderr = None
        try:
            try:
                raise ValueError("x")
            except ValueError:
                ref = server._log_unexpected()
        finally:
            sys.stderr = saved
        self.assertTrue(ref)


if __name__ == "__main__":
    unittest.main()
