"""Unit tests for Float server shutdown and stop mechanics."""

from __future__ import annotations

import json
import os
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

import importlib
import float.config as config
import float.db as db
import float.server as server


class ServerStopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = Path(tempfile.mkdtemp(prefix="float-stop-test-"))
        os.environ["FLOAT_DATA_DIR"] = str(cls.data_dir)
        os.environ["FLOAT_ALLOW_PLAINTEXT"] = "1"
        importlib.reload(config)
        importlib.reload(db)
        importlib.reload(server)

        # Create admin and teacher users
        cls.admin_user = db.create_user("admin_stop@school.in", "Admin Stop", "AdminPass123!", role="admin")
        cls.admin_token = db.create_session(int(cls.admin_user["id"]), "127.0.0.1", "test-agent")

        cls.teacher_user = db.create_user("teacher_stop@school.in", "Teacher Stop", "TeacherPass123!", role="teacher")
        cls.teacher_token = db.create_session(int(cls.teacher_user["id"]), "192.168.1.50", "test-agent")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.data_dir, ignore_errors=True)

    def test_pid_file_helpers(self):
        pid_file = config.pid_path()
        self.assertEqual(pid_file.name, "float.pid")
        self.assertFalse(pid_file.exists())

        # Write test PID
        pid_file.write_text(json.dumps({"pid": os.getpid(), "port": 8766}), encoding="utf-8")
        self.assertTrue(pid_file.exists())
        data = json.loads(pid_file.read_text(encoding="utf-8"))
        self.assertEqual(data["pid"], os.getpid())
        self.assertEqual(data["port"], 8766)
        pid_file.unlink(missing_ok=True)

    def test_shutdown_remote_non_admin_forbidden(self):
        # Spin up ephemeral server
        srv = server.serve("127.0.0.1", 0)
        port = srv.socket.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        time.sleep(0.2)

        try:
            # We mock Route.local as False or simulate remote call
            # When calling without localhost, let's verify Route logic
            class MockRoute:
                local = False
                user = {"id": 2, "name": "Teacher", "role": "teacher"}
                ip = "192.168.1.50"
                request = type("Req", (), {"server": srv})()

            # Calling system_shutdown directly with remote non-admin should raise HttpError 403
            with self.assertRaises(server.HttpError) as ctx:
                server.system_shutdown(MockRoute())
            self.assertEqual(ctx.exception.status, 403)
        finally:
            srv.shutdown()
            srv.server_close()

    def test_shutdown_local_endpoint_success(self):
        # Spin up ephemeral server
        srv = server.serve("127.0.0.1", 0)
        port = srv.socket.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        time.sleep(0.2)

        # Call /api/system/shutdown over loopback (ctx.local == True)
        url = f"{base}/api/system/shutdown"
        req = urllib.request.Request(
            url,
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertTrue(data["ok"])
            self.assertIn("shutting down", data["message"].lower())


if __name__ == "__main__":
    unittest.main()
