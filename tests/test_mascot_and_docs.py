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
