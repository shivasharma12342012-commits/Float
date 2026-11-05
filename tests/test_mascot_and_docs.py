"""Regression tests for documentation integrity, unified logo & pixel mascot markup,
autofill hardening helpers, and car rental backend docstrings.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestDocumentationIntegrity(unittest.TestCase):
    def test_design_md_no_corrupted_chars_and_has_port_8766(self) -> None:
        text = (ROOT / "docs" / "DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("# Float — Architecture & Design", text)
        self.assertNotIn("# Float ? Architecture & Design", text)
        self.assertIn("8766", text)

    def test_design_md_documents_modules_and_security(self) -> None:
        text = (ROOT / "docs" / "DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("## Module Breakdown", text)
        self.assertIn("## Security & Fixed-Desk Session Architecture", text)
        self.assertIn("desk_ip", text)
        self.assertIn("data/float.sqlite3", text)

    def test_agency_server_md_uses_port_8766_and_sqlite3(self) -> None:
        text = (ROOT / "docs" / "AGENCY_SERVER.md").read_text(encoding="utf-8")
        self.assertIn("0.0.0.0:8766", text)
        self.assertNotIn("0.0.0.0:8000", text)
        self.assertIn("data/float.sqlite3", text)
        self.assertNotIn("data/float.db", text)
        self.assertIn("Apex Car Rentals — Airport Desk", text)
        self.assertNotIn("Apex Car Rentals ? Airport Desk", text)

    def test_agency_server_md_documents_desk_ip_and_macos(self) -> None:
        text = (ROOT / "docs" / "AGENCY_SERVER.md").read_text(encoding="utf-8")
        self.assertIn("Start Float Agency Server.command", text)
        self.assertIn("desk_ip", text)
        self.assertIn("## 5. CLI Administration & Troubleshooting", text)

    def test_root_agency_server_md_integrity(self) -> None:
        text = (ROOT / "Agency Server.md").read_text(encoding="utf-8")
        self.assertIn("http://192.168.1.25:8766", text)
        self.assertNotIn("http://192.168.1.25:8000", text)
        self.assertIn("Start Float Agency Server.command", text)
        self.assertIn("Stop Float.command", text)
        self.assertIn("desk_ip", text)
