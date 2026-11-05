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

    def test_readme_references_float_ico_and_docs(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn('<img src="float.ico"', text)
        self.assertIn("Agency Server.md", text)
        self.assertIn("docs/DESIGN.md", text)
        self.assertIn("docs/AGENCY_SERVER.md", text)


class TestMascotAndBrandingMarkup(unittest.TestCase):
    def test_index_html_has_logo_and_pixel_mascot(self) -> None:
        html = (ROOT / "float" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('src="/float.ico"', html)
        self.assertIn('id="float-mascot"', html)
        self.assertIn('id="mascot-bubble"', html)
        self.assertIn('id="mascot-sprite"', html)
        self.assertIn('class="mascot-earcups"', html)
        self.assertIn('class="mascot-body"', html)

    def test_index_html_mascot_accessibility_and_eyes_id(self) -> None:
        html = (ROOT / "float" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn('aria-describedby="mascot-bubble"', html)
        self.assertIn('data-mascot-ready="true"', html)
        self.assertIn('id="mascot-eyes-normal"', html)
        self.assertIn('role="status"', html)

    def test_login_html_has_logo_and_pixel_mascot(self) -> None:
        html = (ROOT / "float" / "web" / "login.html").read_text(encoding="utf-8")
        self.assertIn('src="/float.ico"', html)
        self.assertIn('id="float-mascot"', html)
        self.assertIn('id="mascot-bubble"', html)
        self.assertIn('class="mascot-svg"', html)

    def test_login_html_autofill_suppression_attributes(self) -> None:
        html = (ROOT / "float" / "web" / "login.html").read_text(encoding="utf-8")
        self.assertIn('id="quick-pin"', html)
        self.assertIn('data-lpignore="true"', html)
        self.assertIn('data-1p-ignore="true"', html)
        self.assertIn('spellcheck="false"', html)

    def test_admin_html_has_logo_mascot_and_tablist(self) -> None:
        html = (ROOT / "float" / "web" / "admin.html").read_text(encoding="utf-8")
        self.assertIn('src="/float.ico"', html)
        self.assertIn('id="float-mascot"', html)
        self.assertIn('id="mascot-bubble"', html)
        self.assertIn('role="tablist"', html)

    def test_login_js_mascot_and_harden_input(self) -> None:
        js = (ROOT / "float" / "web" / "login.js").read_text(encoding="utf-8")
        self.assertIn("initLoginMascot", js)
        self.assertIn("FloatSecure.hardenInput", js)
        self.assertNotIn("a school that allows self sign-up", js)

    def test_admin_js_mascot_and_harden_all(self) -> None:
        js = (ROOT / "float" / "web" / "admin.js").read_text(encoding="utf-8")
        self.assertIn("initAdminMascot", js)
        self.assertIn("FloatSecure.hardenAll", js)
        self.assertIn("Weekend SUV tariff update", js)
        self.assertNotIn("Report cards due Friday", js)

    def test_secure_js_exposes_harden_helpers(self) -> None:
        js = (ROOT / "float" / "web" / "secure.js").read_text(encoding="utf-8")
        self.assertIn("function hardenInput", js)
        self.assertIn("function hardenAll", js)
        self.assertIn("hardenInput, hardenAll", js)


class TestMascotInteractivityAndStyles(unittest.TestCase):
    def test_app_css_pupil_transition_and_dark_mode_bubble(self) -> None:
        css = (ROOT / "float" / "web" / "app.css").read_text(encoding="utf-8")
        self.assertIn(".mascot-eyes-normal", css)
        self.assertIn('[data-theme="dark"] .mascot-bubble', css)
        self.assertIn(".float-mascot.is-talking .mascot-bubble", css)

    def test_app_css_reduced_motion_and_focus_visible(self) -> None:
        css = (ROOT / "float" / "web" / "app.css").read_text(encoding="utf-8")
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)
        self.assertIn(".float-mascot:focus-visible", css)
        self.assertIn(".float-mascot.is-cheering .mascot-sprite", css)
