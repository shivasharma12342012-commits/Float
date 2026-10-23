"""Float's test suite.

Run with: python -m pytest tests/ -v
(or just `python tests/test_float.py` — it also runs standalone.)

Each test gets its own throwaway data directory so nothing here touches a
real installation. The HTTP tests spin up the real server on an ephemeral
port and talk to it exactly the way the browser does.
"""

from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from float import config, tools, artifacts, security, db, stats, server

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _fresh_data_dir() -> Path:
    path = Path(tempfile.mkdtemp(prefix="float-test-"))
    os.environ["FLOAT_DATA_DIR"] = str(path)
    os.environ["FLOAT_ALLOW_PLAINTEXT"] = "1"
    return path


# ---------------------------------------------------------------------------
# artifacts: the hand-rolled docx/pdf/xlsx writers
# ---------------------------------------------------------------------------

class ArtifactTests(unittest.TestCase):
    SAMPLE_MD = (
        "# Weekly Notice\n\n"
        "**KV Sector 8**\n\n"
        "This is a *sample* notice with `inline code` and a list:\n\n"
        "- First point\n- Second point\n\n"
        "1. Numbered one\n2. Numbered two\n\n"
        "> A quoted line.\n\n"
        "| Item | Qty |\n|------|-----|\n| Chalk | 10 |\n| Duster | 3 |\n\n"
        "---\n\nSigned, Anita Sharma\n"
    )

    def setUp(self):
        _fresh_data_dir()
        import importlib
        global artifacts
        import float.artifacts as artifacts
        importlib.reload(artifacts)

    def test_docx_is_a_valid_zip_with_expected_parts(self):
        data = artifacts.render("docx", self.SAMPLE_MD, "Weekly Notice", "Anita Sharma")
        self.assertGreater(len(data), 500)
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            self.assertIsNone(zf.testzip())
            names = zf.namelist()
            for expected in ("[Content_Types].xml", "word/document.xml", "word/styles.xml"):
                self.assertIn(expected, names)
            body = zf.read("word/document.xml").decode("utf-8")
            self.assertIn("Weekly Notice", body)

    def test_xlsx_is_a_valid_zip_with_a_sheet(self):
        data = artifacts.render("xlsx", self.SAMPLE_MD, "Notice", "")
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            self.assertIsNone(zf.testzip())
            self.assertIn("xl/worksheets/sheet1.xml", zf.namelist())

    def test_pdf_has_valid_header_and_trailer(self):
        data = artifacts.render("pdf", self.SAMPLE_MD, "Notice", "")
        self.assertTrue(data.startswith(b"%PDF-1."))
        self.assertIn(b"%%EOF", data[-32:])
        self.assertIn(b"/Type /Catalog", data)

    def test_csv_has_bom_for_excel_and_hindi_text(self):
        data = artifacts.render("csv", "| Name | Marks |\n|---|---|\n| \u0906\u0930\u0935 | 42 |\n", "Marks", "")
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        self.assertIn("\u0906\u0930\u0935".encode("utf-8"), data)

    def test_html_is_self_contained_and_escapes_input(self):
        data = artifacts.render("html", "# <script>alert(1)</script>\n", "T", "")
        text = data.decode("utf-8")
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("&lt;script&gt;", text)

    def test_unknown_kind_falls_back_to_plain_text(self):
        # render() is deliberately forgiving: an unrecognised kind never
        # crashes a chat turn, it just degrades to plain text.
        data = artifacts.render("docm", "# Heading\n\nSome *text*.", "T", "")
        text = data.decode("utf-8")
        self.assertIn("Heading", text)
        self.assertNotIn("#", text)

    def test_safe_name_strips_illegal_chars(self):
        self.assertEqual(artifacts.safe_name('Quiz: Ch 1/2?*', 'pdf'), 'Quiz Ch 12.pdf')

    def test_safe_name_handles_empty_input(self):
        self.assertEqual(artifacts.safe_name('', 'docx'), 'Document.docx')

    def test_safe_name_deduplicates_extension(self):
        self.assertEqual(artifacts.safe_name('notes.pdf', 'pdf'), 'notes.pdf')

    def test_safe_name_preserves_devanagari(self):
        self.assertIn('गणित', artifacts.safe_name('गणित कार्यपत्रक', 'pdf'))

    def test_safe_name_strips_leading_dots(self):
        self.assertEqual(artifacts.safe_name('...hidden', 'txt'), 'hidden.txt')

    def test_parse_markdown_headings_levels_1_to_4(self):
        kinds = [b.kind for b in artifacts.parse_markdown('# H1\n## H2\n### H3\n#### H4')]
        self.assertEqual(kinds, ['h1', 'h2', 'h3', 'h4'])

    def test_parse_markdown_horizontal_rules(self):
        kinds = [b.kind for b in artifacts.parse_markdown('---\n\n***\n\n___')]
        self.assertEqual(kinds, ['rule', 'rule', 'rule'])

    def test_parse_markdown_pagebreaks(self):
        kinds = [b.kind for b in artifacts.parse_markdown('\\pagebreak\n<!-- pagebreak -->')]
        self.assertEqual(kinds, ['pagebreak', 'pagebreak'])

    def test_parse_markdown_fenced_code_block(self):
        blocks = artifacts.parse_markdown('```python\nprint(1)\n```')
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].kind, 'code')
        self.assertEqual(blocks[0].text, 'print(1)')

    def test_parse_markdown_nested_bullet_levels(self):
        blocks = artifacts.parse_markdown('- L0\n  - L1\n    - L2')
        self.assertEqual([b.level for b in blocks], [0, 1, 2])

    def test_parse_markdown_numbered_list(self):
        blocks = artifacts.parse_markdown('1. First\n2) Second')
        self.assertEqual([b.kind for b in blocks], ['number', 'number'])

    def test_parse_markdown_table_pads_short_rows(self):
        blocks = artifacts.parse_markdown('| A | B | C |\n|---|---|---|\n| 1 |')
        self.assertEqual(blocks[0].rows[1], ['1', '', ''])

    def test_inline_runs_bold_italic_code(self):
        runs = artifacts.inline_runs('**bold** *italic* `code` plain')
        self.assertIn(('bold', {'bold'}), runs)
        self.assertIn(('italic', {'italic'}), runs)
        self.assertIn(('code', {'code'}), runs)

    def test_strip_markdown_handles_none_and_symbols(self):
        self.assertEqual(artifacts.strip_markdown(None), '')
        self.assertEqual(artifacts.strip_markdown('**Hi** `#1`'), 'Hi 1')

    def test_render_md_returns_utf8_bytes(self):
        data = artifacts.render('md', '# Title\n\nBody', 'Title', '')
        self.assertIn('Title', data.decode('utf-8'))

    def test_render_txt_strips_formatting(self):
        data = artifacts.render('txt', '# Title\n\n**Bold** line', 'Title', 'Sub')
        self.assertIn('Bold line', data.decode('utf-8'))


# ---------------------------------------------------------------------------
# security: hashing, at-rest encryption, rate limiting
# ---------------------------------------------------------------------------

class SecurityTests(unittest.TestCase):
    def setUp(self):
        _fresh_data_dir()
        import importlib
        global security
        import float.security as security
        importlib.reload(security)

    def test_password_hash_roundtrip(self):
        digest = security.hash_password("chalkboard sunrise")
        self.assertTrue(security.verify_password("chalkboard sunrise", digest))
        self.assertFalse(security.verify_password("wrong phrase entirely", digest))

    def test_password_problems_rejects_short_passwords(self):
        self.assertTrue(security.password_problems("short"))
        self.assertFalse(security.password_problems("a proper long passphrase"))

    def test_pin_problems_rejects_non_numeric(self):
        self.assertTrue(security.pin_problems("abcd"))
        self.assertTrue(security.pin_problems("123"))  # too short
        self.assertFalse(security.pin_problems("4321"))

    def test_secret_encrypt_roundtrip(self):
        blob = security.encrypt_secret("sk-super-secret-key")
        self.assertNotIn("sk-super-secret-key", blob)
        self.assertEqual(security.decrypt_secret(blob), "sk-super-secret-key")

    def test_mask_key_shows_only_last_four(self):
        masked = security.mask_key("sk-abcdefghijklmnop")
        self.assertTrue(masked.endswith("mnop"))
        self.assertNotIn("abcdef", masked)

    def test_rate_limiter_blocks_after_threshold(self):
        limiter = security.RateLimiter(limit=3, window=60)
        key = "test-actor"
        for _ in range(3):
            allowed, _ = limiter.check(key)
            self.assertTrue(allowed)
        allowed, wait = limiter.check(key)
        self.assertFalse(allowed)
        self.assertGreater(wait, 0)

    def test_boot_nonce_is_present_and_changes_per_process_seed(self):
        self.assertTrue(security.BOOT_NONCE)
        self.assertIsInstance(security.BOOT_NONCE, str)

    def test_verify_password_handles_empty_and_malformed(self):
        self.assertFalse(security.verify_password('', 'scrypt$32768$aa$bb'))
        self.assertFalse(security.verify_password('validpass123', ''))
        self.assertFalse(security.verify_password('validpass123', 'not-a-valid-hash'))

    def test_verify_password_rejects_unknown_algorithm(self):
        self.assertFalse(security.verify_password('chalkboard sunrise', 'md5$1$00$00'))

    def test_password_problems_rejects_repeated_chars(self):
        self.assertTrue(security.password_problems('aaaaaaaaaaaa'))

    def test_password_problems_rejects_common_weak_list(self):
        self.assertTrue(security.password_problems('password123'))
        self.assertTrue(security.password_problems('qwerty12345'))

    def test_pin_problems_rejects_repeated_and_common_pins(self):
        self.assertTrue(security.pin_problems('1111'))
        self.assertTrue(security.pin_problems('999999'))
        self.assertTrue(security.pin_problems('123456'))

    def test_mask_key_handles_empty_and_short_keys(self):
        self.assertEqual(security.mask_key(''), '')
        self.assertEqual(security.mask_key('shortkey'), 'sho…')

    def test_decrypt_secret_rejects_tampered_ciphertext(self):
        blob = security.encrypt_secret('sk-live-secret')
        tampered = blob[:-4] + ('AAAA' if not blob.endswith('AAAA') else 'BBBB')
        self.assertEqual(security.decrypt_secret(tampered), '')

    def test_decrypt_secret_rejects_wrong_purpose(self):
        blob = security.encrypt_secret('sk-live-secret', purpose='apikey')
        self.assertEqual(security.decrypt_secret(blob, purpose='other'), '')

    def test_same_constant_time_comparison(self):
        self.assertTrue(security.same('abc', 'abc'))
        self.assertFalse(security.same('abc', 'abd'))
        self.assertTrue(security.same('', ''))

    def test_new_token_enforces_minimum_length(self):
        tok = security.new_token(2)
        self.assertGreaterEqual(len(tok), 10)

    def test_token_fingerprint_is_deterministic_hex(self):
        fp1 = security.token_fingerprint('tok-1')
        fp2 = security.token_fingerprint('tok-1')
        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 64)

    def test_env_int_and_float_preserve_zero(self):
        import float.config as config
        os.environ['FLOAT_TEST_ZERO'] = '0'
        try:
            self.assertEqual(config.env_int('FLOAT_TEST_ZERO', 99), 0)
            self.assertEqual(config.env_float('FLOAT_TEST_ZERO', 99.5), 0.0)
        finally:
            os.environ.pop('FLOAT_TEST_ZERO', None)

    def test_env_bool_handles_truthy_and_falsy_strings(self):
        import float.config as config
        for val, expected in [('1', True), ('true', True), ('yes', True), ('0', False), ('false', False), ('off', False)]:
            os.environ['FLOAT_TEST_BOOL'] = val
            self.assertEqual(config.env_bool('FLOAT_TEST_BOOL', not expected), expected)
        os.environ.pop('FLOAT_TEST_BOOL', None)

    def test_greeting_first_name_strips_honorifics(self):
        import float.greeting as greeting
        self.assertEqual(greeting._first_name('Mrs. Anita Sharma'), 'Anita')
        self.assertEqual(greeting._first_name('Dr. R. K. Narayan'), 'R')
        self.assertEqual(greeting._first_name(''), '')
        self.assertEqual(greeting._first_name('...'), '')

    def test_greeting_parse_clock_formats(self):
        import float.greeting as greeting
        self.assertEqual(greeting._parse_clock('08:30').hour, 8)
        self.assertEqual(greeting._parse_clock('2:15 PM').hour, 14)
        self.assertEqual(greeting._parse_clock('09.45').minute, 45)
        self.assertIsNone(greeting._parse_clock('invalid'))
        self.assertIsNone(greeting._parse_clock(''))

    def test_greeting_part_of_day_boundaries(self):
        import float.greeting as greeting
        self.assertEqual(greeting._part_of_day(2), 'night')
        self.assertEqual(greeting._part_of_day(8), 'morning')
        self.assertEqual(greeting._part_of_day(14), 'afternoon')
        self.assertEqual(greeting._part_of_day(19), 'evening')
        self.assertEqual(greeting._part_of_day(23), 'night')

    def test_greeting_regional_salutations(self):
        import float.greeting as greeting
        for lang in ('hi', 'bn', 'mr', 'ta', 'te', 'gu', 'kn', 'ml', 'pa', 'or', 'as', 'ur'):
            self.assertIn('morning', greeting.SALUTATIONS[lang])
            self.assertIn('afternoon', greeting.SALUTATIONS[lang])
            self.assertIn('evening', greeting.SALUTATIONS[lang])

    def test_stats_parse_and_compute_basic_sheet(self):
        import float.stats as stats
        parsed = stats.parse('Name, Q1(5), Q2(5)\nAarav, 4, 5\nDiya, 3, 4\nKabir, AB, AB')
        res = stats.compute(parsed)
        self.assertEqual(res['n'], 2)
        self.assertAlmostEqual(res['mean'], 8.0)
        self.assertEqual(res['max_total'], 10.0)

    def test_stats_parse_rejects_empty_input(self):
        import float.stats as stats
        with self.assertRaises(stats.MarksError):
            stats.parse('   \n  ')

    def test_stats_parse_rejects_header_only(self):
        import float.stats as stats
        with self.assertRaises(stats.MarksError):
            stats.parse('Name, Q1(10), Q2(10)')

    def test_stats_parse_records_out_of_range_marks(self):
        import float.stats as stats
        parsed = stats.parse('Name, Q1(5)\nAarav, 4\nDiya, 9')
        self.assertEqual(len(parsed.students), 1)
        self.assertEqual(len(parsed.problems), 1)

    def test_stats_analyse_formats_summary_text(self):
        import float.stats as stats
        out = stats.analyse('Name, Q1(10), Q2(10)\nAarav, 10, 10\nDiya, 10, 10')
        self.assertIn('Students counted: 2', out)
        self.assertIn('spread is zero', out)

    def test_attachments_to_text_plain_and_truncation(self):
        import base64, float.attachments as attachments
        raw = base64.b64encode(b'Hello class 8B').decode('ascii')
        self.assertEqual(attachments.to_text({'name': 'note.txt', 'data': raw}), 'Hello class 8B')

    def test_attachments_docx_roundtrip_extraction(self):
        import base64, float.artifacts as artifacts, float.attachments as attachments
        docx_bytes = artifacts.render('docx', '# Photosynthesis\n\nPlants make food.', 'Bio', '')
        b64 = base64.b64encode(docx_bytes).decode('ascii')
        extracted = attachments.to_text({'name': 'bio.docx', 'data': b64})
        self.assertIn('Photosynthesis', extracted)
        self.assertIn('Plants make food.', extracted)

    def test_attachments_xlsx_roundtrip_extraction(self):
        import base64, float.artifacts as artifacts, float.attachments as attachments
        xlsx_bytes = artifacts.render('xlsx', '| Roll | Name |\n|---|---|\n| 1 | Aarav |', 'Roster', '')
        b64 = base64.b64encode(xlsx_bytes).decode('ascii')
        extracted = attachments.to_text({'name': 'roster.xlsx', 'data': b64})
        self.assertIn('Aarav', extracted)

    def test_attachments_rejects_unsupported_legacy_binary(self):
        import base64, float.attachments as attachments
        b64 = base64.b64encode(b'binary').decode('ascii')
        with self.assertRaises(attachments.AttachmentError):
            attachments.to_text({'name': 'old.ppt', 'data': b64})

    def test_attachments_rejects_empty_text_file(self):
        import base64, float.attachments as attachments
        b64 = base64.b64encode(b'   \n  ').decode('ascii')
        with self.assertRaises(attachments.AttachmentError):
            attachments.to_text({'name': 'empty.txt', 'data': b64})

    def test_agent_title_for_short_and_long_messages(self):
        import float.agent as agent
        self.assertEqual(agent.title_for(''), 'New conversation')
        self.assertEqual(agent.title_for('   Lesson   plan  '), 'Lesson plan')
        long_msg = 'Prepare a detailed unit test paper for Class 10 Mathematics Trigonometry'
        self.assertTrue(agent.title_for(long_msg).endswith('…'))
        self.assertLessEqual(len(agent.title_for(long_msg)), 53)

    def test_agent_drop_old_screens_strips_earlier_images(self):
        import float.agent as agent
        hist = [{'role': 'user', 'content': [{'type': 'tool_result', 'content': [{'type': 'text', 'text': 'screen 1'}, {'type': 'image', 'source': {'data': 'abc'}}]}]}]
        agent._drop_old_screens(hist)
        self.assertEqual(hist[0]['content'][0]['content'], 'screen 1')

    def test_transport_seal_and_public_info(self):
        import float.transport as transport
        info = transport.public_info()
        self.assertIn('available', info)
        if info['available']:
            self.assertEqual(len(info['kid']), 16)
            sealed = transport.seal_response(b'0' * 32, '/api/test', {'ok': True})
            self.assertIn('enc', sealed)

    def test_transport_open_request_rejects_non_dict(self):
        import float.transport as transport
        if transport.AVAILABLE:
            with self.assertRaises(transport.TransportError):
                transport.open_request('not-a-dict', '/api/auth/signin')

    def test_transport_open_request_signals_rekey_on_kid_mismatch(self):
        import float.transport as transport
        if transport.AVAILABLE:
            try:
                transport.open_request({'kid': 'wrong-kid'}, '/api/auth/signin')
            except transport.TransportError as exc:
                self.assertTrue(exc.rekey)

    def test_providers_friendly_error_messages(self):
        import float.providers as providers
        self.assertEqual(providers._friendly(401, '{}', 'openai').status, 401)
        self.assertTrue(providers._friendly(429, '{}', 'anthropic').retryable)
        self.assertTrue(providers._friendly(503, 'server down', 'google').retryable)
        self.assertFalse(providers._friendly(404, '{"error": "not found"}', 'openai').retryable)

    def test_maintenance_backup_and_last_backup(self):
        import float.db as db, float.maintenance as maintenance
        db.init()
        path = maintenance.backup_now('unit')
        self.assertTrue(path.exists())
        info = maintenance.last_backup()
        self.assertGreaterEqual(info['count'], 1)
        self.assertIn('unit', info['file'])

    def test_maintenance_prune_runs_cleanly_on_fresh_db(self):
        import float.db as db, float.maintenance as maintenance
        db.init()
        res = maintenance.prune(batch=10)
        self.assertEqual(res, {'audit': 0, 'usage': 0})

    def test_google_decode_id_token_rejects_invalid_jwt(self):
        import float.google as google
        with self.assertRaises(google.GoogleError):
            google._decode_id_token('not-a-jwt')

    def test_tools_for_filters_use_computer_when_disabled(self):
        import float.tools as tools
        with_comp = {t['name'] for t in tools.tools_for({}, True)}
        without_comp = {t['name'] for t in tools.tools_for({}, False)}
        self.assertIn('use_computer', with_comp)
        self.assertNotIn('use_computer', without_comp)

    def test_tools_execute_rejects_unknown_tool(self):
        import float.tools as tools
        res = tools.execute('nonexistent_tool', {}, {'id': 1}, None)
        self.assertIn('No tool called', res['text'])

    def test_db_org_get_and_set_roundtrip(self):
        import float.db as db
        db.init()
        db.org_set('school_name', 'DPS RK Puram')
        self.assertEqual(db.org_get('school_name'), 'DPS RK Puram')
        self.assertEqual(db.org_get('missing_key', 'fallback'), 'fallback')

    def test_db_tasks_crud_lifecycle(self):
        import importlib, float.config as config, float.db as db
        importlib.reload(config); importlib.reload(db); db.init()
        uid = db.create_user('t1@school.in', 'Teacher 1', 'passphrase123')['id']
        tid = db.add_task(uid, 'Check copies', '2026-11-01')
        self.assertEqual(len(db.list_tasks(uid)), 1)
        db.set_task_done(tid, uid, True)
        self.assertEqual(len(db.list_tasks(uid, include_done=False)), 0)
        self.assertEqual(len(db.list_tasks(uid, include_done=True)), 1)
        db.delete_task(tid, uid)
        self.assertEqual(len(db.list_tasks(uid, include_done=True)), 0)

    def test_db_notices_add_and_retire(self):
        import importlib, float.config as config, float.db as db
        importlib.reload(config); importlib.reload(db); db.init()
        uid = db.create_user('admin2@school.in', 'Admin', 'passphrase123', role='admin')['id']
        nid = db.add_notice('Staff meeting', 'At 2 PM', 'info', uid)
        self.assertTrue(any(n['id'] == nid for n in db.active_notices()))
        db.retire_notice(nid)
        self.assertFalse(any(n['id'] == nid for n in db.active_notices()))

    def test_db_timetable_periods_roundtrip(self):
        import importlib, float.config as config, float.db as db
        importlib.reload(config); importlib.reload(db); db.init()
        uid = db.create_user('tt@school.in', 'Timetable Teacher', 'passphrase123')['id']
        db.set_periods(uid, [{'weekday': 0, 'slot': 1, 'starts': '08:00', 'ends': '08:40', 'label': '8B Maths', 'room': '204'}])
        periods = db.list_periods(uid, weekday=0)
        self.assertEqual(len(periods), 1)
        self.assertEqual(periods[0]['label'], '8B Maths')

    def test_db_conversation_rename_and_delete(self):
        import importlib, float.config as config, float.db as db
        importlib.reload(config); importlib.reload(db); db.init()
        uid = db.create_user('conv@school.in', 'Conv Teacher', 'passphrase123')['id']
        cid = db.new_conversation(uid, 'Initial', 'chat')
        db.rename_conversation(cid, uid, 'Updated Title')
        self.assertEqual(db.get_conversation(cid, uid)['title'], 'Updated Title')
        db.delete_conversation(cid, uid)
        self.assertIsNone(db.get_conversation(cid, uid))

    def test_db_attendance_save_and_range(self):
        import importlib, float.config as config, float.db as db
        importlib.reload(config); importlib.reload(db); db.init()
        uid = db.create_user('att@school.in', 'Att Teacher', 'passphrase123')['id']
        klid = db.add_class(uid, '7A', '7', 'A', 'English', 'CBSE')
        db.add_students(klid, [{'roll': '1', 'name': 'Aarav'}, {'roll': '2', 'name': 'Diya'}])
        students = db.list_students(klid)
        db.save_attendance(klid, '2026-10-23', [students[0]['id']], [students[1]['id']])
        att = db.attendance_range(klid)
        self.assertEqual(len(att), 1)
        self.assertEqual(att[0]['absent'], [students[1]['id']])

    def test_db_cap_override_and_default(self):
        import importlib, float.config as config, float.db as db
        importlib.reload(config); importlib.reload(db); db.init()
        uid = db.create_user('cap@school.in', 'Cap Teacher', 'passphrase123')['id']
        db.org_set('teacher_monthly_paise_cap', '5000')
        self.assertEqual(db.cap_for(uid), (5000, False))
        db.set_cap_override(uid, 12000)
        self.assertEqual(db.cap_for(uid), (12000, True))
        db.set_cap_override(uid, None)
        self.assertEqual(db.cap_for(uid), (5000, False))


# ---------------------------------------------------------------------------
# the HTTP server, exercised the way the browser does
# ---------------------------------------------------------------------------

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_dir = _fresh_data_dir()
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

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        shutil.rmtree(cls.data_dir, ignore_errors=True)

    def call(self, path, body=None, token=None, method=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            self.base + path, data=data,
            method=method or ("POST" if data else "GET"),
        )
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        if data:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=5) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read().decode())

    def test_01_state_reports_setup_needed_on_a_fresh_install(self):
        status, data = self.call("/api/auth/state", {})
        self.assertEqual(status, 200)
        self.assertTrue(data["setup_needed"])

    def test_02_first_signup_becomes_admin(self):
        status, data = self.call("/api/auth/signup", {
            "email": "anita@school.edu.in", "name": "Anita Sharma",
            "password": "chalkboard sunrise", "school": "KV Sector 8",
        })
        self.assertEqual(status, 200)
        self.assertEqual(data["user"]["role"], "admin")
        self.__class__.token = data["token"]

    def test_03_bootstrap_has_every_field_the_front_end_reads(self):
        status, data = self.call("/api/bootstrap", token=self.token, method="GET")
        self.assertEqual(status, 200)
        for key in ("user", "greeting", "conversations", "toolkit", "toolkit_groups",
                    "classes", "tasks", "artifacts", "notices", "models", "keys",
                    "providers", "options", "capabilities", "usage", "own_work"):
            self.assertIn(key, data)
        self.assertEqual(len(data["toolkit"]), 19)
        self.assertIn("openrouter", {p["id"] for p in data["providers"]})

    def test_04_class_roster_parses_from_free_text(self):
        status, data = self.call("/api/classes", {
            "name": "9A", "grade": "9", "section": "A", "subject": "Maths",
            "roster": "1 Aarav Kumar\n2 Diya Sharma\n3 Ishaan Patel",
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(data["students"], 3)

    def test_05_toolkit_entry_builds_a_prompt(self):
        status, data = self.call("/api/toolkit/worksheet", {
            "values": {"subject": "Science", "klass": "9A", "topic": "Photosynthesis"},
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertIn("prompt", data)
        self.assertGreater(len(data["prompt"]), 20)

    def test_06_pin_can_be_set_and_used_to_sign_in(self):
        status, data = self.call("/api/me/pin", {
            "password": "chalkboard sunrise", "pin": "4321",
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertTrue(data["has_pin"])

        status, data = self.call("/api/auth/signin", {
            "email": "anita@school.edu.in", "pin": "4321",
        })
        self.assertEqual(status, 200)
        self.assertIn("token", data)

    def test_07_wrong_pin_is_rejected(self):
        status, data = self.call("/api/auth/signin", {
            "email": "anita@school.edu.in", "pin": "0000",
        })
        self.assertEqual(status, 401)

    def test_08_admin_overview_reflects_the_one_teacher(self):
        status, data = self.call("/api/admin/overview", token=self.token, method="GET")
        self.assertEqual(status, 200)
        self.assertEqual(data["totals"]["teachers"], 1)

    def test_09_non_admin_cannot_reach_admin_routes(self):
        # self_signup is off by default, so the admin adds the second
        # teacher from the admin panel rather than the teacher signing up.
        status, data = self.call("/api/admin/users", {
            "email": "raj@school.edu.in", "name": "Raj Verma",
        }, token=self.token)
        self.assertEqual(status, 200)
        temp_password = data["temp_password"]

        status, data = self.call("/api/auth/signin", {
            "email": "raj@school.edu.in", "password": temp_password,
        })
        self.assertEqual(status, 200)
        teacher_token = data["token"]

        status, _ = self.call("/api/admin/overview", token=teacher_token, method="GET")
        self.assertEqual(status, 403)

    def test_10_missing_token_is_unauthorized(self):
        status, _ = self.call("/api/bootstrap", method="GET")
        self.assertEqual(status, 401)

    def test_11_org_settings_round_trip(self):
        status, data = self.call("/api/admin/org", {
            "school_name": "KV Sector 8", "self_signup": "1",
            "allowed_providers": ["anthropic"],
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(data["org"]["allowed_providers"]), ["anthropic"])

    def test_12_notice_appears_for_other_teachers(self):
        status, data = self.call("/api/admin/notice", {
            "title": "PTM Friday", "body": "Bring report cards.",
        }, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(len(data["notices"]), 1)

    def test_13_marks_are_validated(self):
        status, data = self.call("/api/classes", {"name": "8B", "roster": "1, Aarav\n2, Diya"},
                                 token=self.token)
        cid = data["id"]
        _, data = self.call(f"/api/classes/{cid}/students", token=self.token)
        sid = data["students"][0]["id"]

        def post(score, mx):
            return self.call(f"/api/classes/{cid}/marks", {"marks": [
                {"student_id": sid, "assessment": "UT", "score": score, "max_score": mx}]},
                token=self.token)[0]

        self.assertEqual(post(42, 50), 200)
        self.assertEqual(post(0, 50), 200)
        self.assertEqual(post(50, 50), 200)
        for bad in [(55, 50), (-5, 50), (3, 0), ("abc", 50), (None, 50), (float("nan"), 50),
                    (float("inf"), 50), (3, -10)]:
            self.assertEqual(post(*bad), 400, bad)

    def test_server_parse_roster_formats(self):
        import float.server as server
        rows = server._parse_roster('1, Aarav Sharma\n2. Diya Verma\nIshaan Patel')
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], {'roll': '1', 'name': 'Aarav Sharma'})
        self.assertEqual(rows[1], {'roll': '2', 'name': 'Diya Verma'})
        self.assertEqual(rows[2], {'roll': '3', 'name': 'Ishaan Patel'})

    def test_server_band_classification(self):
        import float.server as server
        self.assertEqual(server._band(0), 'No use')
        self.assertEqual(server._band(1), 'Light')
        self.assertEqual(server._band(19), 'Light')
        self.assertEqual(server._band(20), 'Regular')
        self.assertEqual(server._band(99), 'Regular')
        self.assertEqual(server._band(100), 'Frequent')

    def test_server_tasks_endpoints_roundtrip(self):
        status, data = self.call('/api/tasks', {'title': 'Prepare worksheet', 'due': '2026-11-15'}, token=self.token)
        self.assertEqual(status, 200)
        tid = data['tasks'][0]['id']
        status, data = self.call(f'/api/tasks/{tid}', {'done': True}, token=self.token)
        self.assertEqual(status, 200)
        status, _ = self.call(f'/api/tasks/{tid}', token=self.token, method='DELETE')
        self.assertEqual(status, 200)

    def test_server_timetable_endpoints_roundtrip(self):
        status, data = self.call('/api/timetable', {'periods': [{'weekday': 1, 'slot': 1, 'starts': '09:00', 'ends': '09:45', 'label': '9A Science', 'room': 'Lab 1'}]}, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(len(data['periods']), 1)
        status, got = self.call('/api/timetable', token=self.token, method='GET')
        self.assertEqual(status, 200)
        self.assertEqual(got['periods'][0]['room'], 'Lab 1')

    def test_server_conversations_crud_endpoints(self):
        status, created = self.call('/api/toolkit/worksheet', {'values': {'subject': 'Science', 'klass': '9A', 'topic': 'Atoms'}}, token=self.token)
        self.assertEqual(status, 200)
        cid = created['conv_id']
        status, _ = self.call(f'/api/conversations/{cid}', {'title': 'Draft Paper'}, token=self.token)
        self.assertEqual(status, 200)
        status, fetched = self.call(f'/api/conversations/{cid}', token=self.token, method='GET')
        self.assertEqual(status, 200)
        self.assertEqual(fetched['conversation']['title'], 'Draft Paper')
        status, _ = self.call(f'/api/conversations/{cid}', {}, token=self.token, method='DELETE')
        self.assertEqual(status, 200)

    def test_server_me_profile_update(self):
        status, data = self.call('/api/me', {'name': 'Anita S.', 'board': 'ICSE / ISC', 'assist_level': 'coach'}, token=self.token)
        self.assertEqual(status, 200)
        self.assertEqual(data['user']['name'], 'Anita S.')
        self.assertEqual(data['user']['assist_level'], 'coach')

    def test_server_static_path_traversal_is_blocked(self):
        status, _ = self.call('/..%2f..%2fmain.py', method='GET')
        self.assertIn(status, (403, 404))

    def test_server_options_returns_204_with_allow_header(self):
        req = urllib.request.Request(self.base + '/api/bootstrap', method='OPTIONS')
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 204)
            self.assertIn('POST', resp.headers.get('Allow', ''))

    def test_server_rejects_oversized_content_length(self):
        import http.client
        hc = http.client.HTTPConnection('127.0.0.1', self.srv.server_port, timeout=5)
        try:
            hc.putrequest('POST', '/api/auth/signin')
            hc.putheader('Content-Length', str(99_000_000))
            hc.endheaders()
            resp = hc.getresponse()
            resp.read()
            self.assertEqual(resp.status, 413)
        finally:
            hc.close()

    def test_server_rejects_invalid_json_body(self):
        import http.client
        hc = http.client.HTTPConnection('127.0.0.1', self.srv.server_port, timeout=5)
        try:
            hc.request('POST', '/api/auth/signin', body=b'{not-json', headers={'Content-Type': 'application/json'})
            resp = hc.getresponse()
            resp.read()
            self.assertEqual(resp.status, 400)
        finally:
            hc.close()

    def test_server_case_insensitive_bearer_header(self):
        req = urllib.request.Request(self.base + '/api/bootstrap', headers={'Authorization': 'bearer ' + self.token})
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)

    def test_server_admin_audit_handles_bad_limit_param(self):
        status, data = self.call('/api/admin/audit?limit=notanumber', token=self.token, method='GET')
        self.assertEqual(status, 200)
        self.assertIn('entries', data)

    def test_server_admin_export_returns_xlsx(self):
        req = urllib.request.Request(self.base + '/api/admin/export', headers={'Authorization': 'Bearer ' + self.token})
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            body = resp.read()
            self.assertGreater(len(body), 200)

    def test_server_admin_backup_endpoint(self):
        status, data = self.call('/api/admin/backup', {}, token=self.token)
        self.assertEqual(status, 200)
        self.assertTrue(data['ok'])
        self.assertGreaterEqual(data['backup']['count'], 1)




class HardeningTests(unittest.TestCase):

    def test_hardening_001_toolkit_lesson_plan(self):
        entry = tools.toolkit_entry('lesson-plan')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_002_toolkit_question_paper(self):
        entry = tools.toolkit_entry('question-paper')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_003_toolkit_worksheet(self):
        entry = tools.toolkit_entry('worksheet')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_004_toolkit_marking(self):
        entry = tools.toolkit_entry('marking')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_005_toolkit_rubric(self):
        entry = tools.toolkit_entry('rubric')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_006_toolkit_remarks(self):
        entry = tools.toolkit_entry('remarks')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_007_toolkit_parent_message(self):
        entry = tools.toolkit_entry('parent-message')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_008_toolkit_bilingual(self):
        entry = tools.toolkit_entry('bilingual')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_009_toolkit_activity(self):
        entry = tools.toolkit_entry('activity')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_010_toolkit_remedial(self):
        entry = tools.toolkit_entry('remedial')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_011_toolkit_pacing(self):
        entry = tools.toolkit_entry('pacing')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_012_toolkit_analysis(self):
        entry = tools.toolkit_entry('analysis')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_013_toolkit_notice(self):
        entry = tools.toolkit_entry('notice')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_014_toolkit_letter(self):
        entry = tools.toolkit_entry('letter')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_015_toolkit_slides(self):
        entry = tools.toolkit_entry('slides')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_016_toolkit_seating(self):
        entry = tools.toolkit_entry('seating')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_017_toolkit_doubt(self):
        entry = tools.toolkit_entry('doubt')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_018_toolkit_assembly(self):
        entry = tools.toolkit_entry('assembly')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_019_toolkit_hpc(self):
        entry = tools.toolkit_entry('hpc')
        self.assertIsNotNone(entry)
        vals = {'klass': '10', 'subject': 'Math', 'topic': 'Optics', 'chapters': 'Algebra',
                'question': 'Sample', 'task': 'Poster', 'students': 'Aarav', 'student': 'Diya',
                'reason': 'Attendance', 'language': 'Hindi', 'gap': 'Grammar', 'from_who': 'Principal',
                'occasion': 'Annual Day', 'speaker': 'Head', 'observations': 'Good',
                'data': 'Aarav, 90\nDiya, 85'}
        res = tools.fill_prompt(entry, vals)
        self.assertGreater(len(res), 20)

    def test_hardening_020(self):
        self.assertEqual(artifacts.safe_name('folder/sub/doc:test.pdf', 'pdf'), 'foldersubdoctest.pdf')

    def test_hardening_021(self):
        self.assertEqual(artifacts.safe_name('', 'docx'), 'Document.docx')

    def test_hardening_022(self):
        self.assertEqual(len(artifacts.parse_markdown('# H1\n## H2\n### H3')), 3)

    def test_hardening_023(self):
        self.assertEqual(len(artifacts.parse_markdown('| Col A | Col B |\n|---|---|\n| Val 1 | Val 2 |')), 1)

    def test_hardening_024(self):
        self.assertEqual(len(artifacts.parse_markdown('> Important note for KV teachers')), 1)

    def test_hardening_025(self):
        self.assertEqual(artifacts._column(0), 'A')

    def test_hardening_026(self):
        self.assertEqual(artifacts._column(25), 'Z')

    def test_hardening_027(self):
        self.assertEqual(artifacts._column(26), 'AA')

    def test_hardening_028(self):
        self.assertEqual(artifacts._split_row('| One | Two | Three |'), ['One', 'Two', 'Three'])

    def test_hardening_029(self):
        self.assertEqual(artifacts.strip_markdown('**Bold** and *Italic* text'), 'Bold and Italic text')

    def test_hardening_030(self):
        self.assertGreater(len(artifacts.build_csv('Name, Marks\nAarav, 90')), 10)

    def test_hardening_031(self):
        self.assertIn(b'<!doctype html>', artifacts.build_html('# Title\n\nContent', 'Page'))

    def test_hardening_032(self):
        self.assertGreater(len(artifacts.build_docx('# Notice\n\nKV Sector 8', 'Notice')), 500)

    def test_hardening_033(self):
        self.assertGreater(len(artifacts.build_xlsx('| C1 | C2 |\n|---|---|\n| 1 | 2 |', 'Sheet')), 500)

    def test_hardening_034(self):
        self.assertTrue(artifacts.build_pdf('# Notice\n\nKV Sector 8', 'Notice').startswith(b'%PDF-1.4'))

    def test_hardening_035(self):
        self.assertEqual(artifacts.render('txt', 'Plain teaching plan', 'Title'), b'Plain teaching plan')

    def test_hardening_036(self):
        self.assertIn(b'# Heading', artifacts.render('md', '# Heading\n\nBody', 'Title'))

    def test_hardening_037(self):
        self.assertTrue(artifacts.desktop_dir().exists())

    def test_hardening_038(self):
        self.assertEqual(len(artifacts.inline_runs('Hello **teacher** friend')), 3)

    def test_hardening_039(self):
        self.assertEqual(len(artifacts.inline_runs('Hello *important* concept')), 3)

    def test_hardening_040(self):
        self.assertEqual(len(artifacts.inline_runs('Run `python main.py` now')), 3)

    def test_hardening_041(self):
        self.assertTrue(security.same('secret123', 'secret123'))

    def test_hardening_042(self):
        self.assertFalse(security.same('secret123', 'secret456'))

    def test_hardening_043(self):
        self.assertFalse(security.same('short', 'longer_string'))

    def test_hardening_044(self):
        self.assertGreater(len(security.new_token(16)), 16)

    def test_hardening_045(self):
        self.assertEqual(len(security.token_fingerprint('sample_token')), 64)

    def test_hardening_046(self):
        self.assertGreater(len(security.pin_problems('')), 0)

    def test_hardening_047(self):
        self.assertGreater(len(security.pin_problems('123')), 0)

    def test_hardening_048(self):
        self.assertGreater(len(security.pin_problems('1234')), 0)

    def test_hardening_049(self):
        self.assertGreater(len(security.pin_problems('0000')), 0)

    def test_hardening_050(self):
        self.assertEqual(security.pin_problems('4829'), [])

    def test_hardening_051(self):
        self.assertGreater(len(security.password_problems('short')), 0)

    def test_hardening_052(self):
        self.assertEqual(security.password_problems('TeacherStrongPassword123!'), [])

    def test_hardening_053(self):
        h = security.hash_password('TeacherSecretPass1!')
        self.assertTrue(security.verify_password('TeacherSecretPass1!', h))
        self.assertFalse(security.verify_password('WrongSecret', h))

    def test_hardening_054(self):
        self.assertFalse(security.verify_password('', 'some_hash'))

    def test_hardening_055(self):
        self.assertFalse(security.verify_password('pass', ''))

    def test_hardening_056(self):
        self.assertFalse(security.verify_password('pass', 'not_a_valid_hash'))

    def test_hardening_057(self):
        masked = security.mask_key('sk-ant-1234567890abcdef')
        self.assertTrue(masked.startswith('sk-ant-') and masked.endswith('cdef'))

    def test_hardening_058(self):
        rl = security.RateLimiter(limit=2, window=60.0)
        self.assertTrue(rl.check('u1')[0])
        self.assertTrue(rl.check('u1')[0])
        self.assertFalse(rl.check('u1')[0])

    def test_hardening_059(self):
        rl = security.RateLimiter(limit=1, window=60.0)
        rl.check('u1')
        rl.reset('u1')
        self.assertTrue(rl.check('u1')[0])

    def test_hardening_060(self):
        enc = security.encrypt_secret('sk-test-secret-value-12345')
        self.assertEqual(security.decrypt_secret(enc), 'sk-test-secret-value-12345')

    def test_hardening_061(self):
        self.assertEqual(config.env_int('FLOAT_TEST_NONEXISTENT_VAR', 99), 99)

    def test_hardening_062(self):
        self.assertEqual(config.env_float('FLOAT_TEST_NONEXISTENT_VAR', 4.5), 4.5)

    def test_hardening_063(self):
        self.assertFalse(config.rt_phrase_matches(None))

    def test_hardening_064(self):
        self.assertFalse(config.rt_phrase_matches('   '))

    def test_hardening_065(self):
        self.assertIsNone(config.tls_files())

    def test_hardening_066(self):
        h = config._sha('kv_school_test')
        self.assertEqual(len(h), 64)
        self.assertTrue(all(c in '0123456789abcdef' for c in h))

    def test_hardening_067(self):
        self.assertIsNotNone(config.PROVIDERS['anthropic'].model('claude-sonnet-4-5'))

    def test_hardening_068(self):
        self.assertIsNone(config.PROVIDERS['anthropic'].model('non-existent-model'))

    def test_hardening_069(self):
        self.assertEqual(config.PROVIDER_ORDER, ('anthropic', 'openai', 'openrouter', 'google'))

    def test_hardening_070(self):
        self.assertIn('CBSE', config.BOARDS)

    def test_hardening_071(self):
        self.assertEqual(len(config.GRADES), 12)

    def test_hardening_072(self):
        self.assertIn('draft', config.ASSIST_LEVELS)

    def test_hardening_073(self):
        self.assertEqual(config.DEFAULT_ASSIST, 'draft')

    def test_hardening_074(self):
        self.assertIn('en', config.LANGUAGES)

    def test_hardening_075(self):
        for m, (ci, co) in config.MODEL_PRICES.items():
            self.assertGreaterEqual(ci, 0)
            self.assertGreaterEqual(co, 0)

    def test_hardening_076(self):
        s = config.Settings()
        self.assertEqual(s.host, '127.0.0.1')
        self.assertEqual(s.port, 8766)
        self.assertFalse(s.lan)

    def test_hardening_077(self):
        self.assertEqual(config.APP_NAME, 'Float')

    def test_hardening_078(self):
        self.assertEqual(config.VERSION, '1.0.0')

    def test_hardening_079(self):
        self.assertIn('hi', config.LANGUAGES)

    def test_hardening_080(self):
        self.assertIn('bn', config.LANGUAGES)

    def test_hardening_081(self):
        self.assertFalse(db.owns_class(999999, 1))

    def test_hardening_082(self):
        self.assertIsNone(db.get_user(999999))

    def test_hardening_083(self):
        self.assertIsNone(db.get_user_by_email('unknown_teacher_email@school.in'))

    def test_hardening_084(self):
        self.assertIsNone(db.get_user_by_google('unknown_google_sub_id'))

    def test_hardening_085(self):
        self.assertIsNone(db.resolve_session('completely_unknown_token_xyz'))

    def test_hardening_086(self):
        self.assertEqual(db.get_key('anthropic', user_id=999999), '')

    def test_hardening_087(self):
        self.assertFalse(db.has_own_key(999999))

    def test_hardening_088(self):
        self.assertIsNone(db.get_conversation(999999, 1))

    def test_hardening_089(self):
        self.assertIsNone(db.get_artifact(999999, 1))

    def test_hardening_090(self):
        self.assertEqual(db.list_students(999999), [])

    def test_hardening_091(self):
        self.assertEqual(db.class_marks(999999), [])

    def test_hardening_092(self):
        self.assertEqual(db.list_periods(999999), [])

    def test_hardening_093(self):
        self.assertEqual(db.list_tasks(999999), [])

    def test_hardening_094(self):
        self.assertEqual(db.list_artifacts(999999), [])

    def test_hardening_095(self):
        self.assertEqual(db.list_conversations(999999), [])

    def test_hardening_096(self):
        self.assertEqual(db.get_messages(999999), [])

    def test_hardening_097(self):
        self.assertIn('anthropic', db.allowed_providers())

    def test_hardening_098(self):
        cap, over = db.cap_for(999999)
        self.assertGreaterEqual(cap, 0)
        self.assertFalse(over)

    def test_hardening_099(self):
        self.assertIsInstance(db.active_notices(), list)

    def test_hardening_100(self):
        self.assertIsInstance(db.org_all(), dict)

    def test_hardening_101(self):
        self.assertGreaterEqual(db.count_users(), 1)

    def test_hardening_102(self):
        self.assertIsInstance(db.key_status(999999), dict)

    def test_hardening_103(self):
        self.assertGreaterEqual(db.pool_paise(), 0)

    def test_hardening_104(self):
        self.assertGreaterEqual(db.month_paise(999999), 0)

    def test_hardening_105(self):
        self.assertIsInstance(db.own_work_summary(999999), dict)

    def test_hardening_106(self):
        self.assertEqual(server._band(0), 'No use')

    def test_hardening_107(self):
        self.assertEqual(server._band(15), 'Light')

    def test_hardening_108(self):
        self.assertEqual(server._band(60), 'Regular')

    def test_hardening_109(self):
        self.assertEqual(server._band(250), 'Frequent')

    def test_hardening_110(self):
        self.assertEqual(server._as_list('["math", "science"]'), ['math', 'science'])

    def test_hardening_111(self):
        self.assertEqual(server._as_list('invalid-json-text'), [])

    def test_hardening_112(self):
        self.assertEqual(server._as_list(''), [])

    def test_hardening_113(self):
        self.assertEqual(server._as_list(None), [])

    def test_hardening_114(self):
        self.assertEqual(len(server._parse_roster('Aarav Sharma\nDiya Patel')), 2)

    def test_hardening_115(self):
        self.assertEqual(server._parse_roster('Aarav Sharma\nDiya Patel')[0]['name'], 'Aarav Sharma')

    def test_hardening_116(self):
        self.assertEqual(server._parse_roster('1, Aarav Sharma\n2, Diya Patel')[0]['roll'], '1')

    def test_hardening_117(self):
        self.assertEqual(server._parse_roster('1\tAarav Sharma\n2\tDiya Patel')[1]['roll'], '2')

    def test_hardening_118(self):
        self.assertEqual(server._parse_roster(''), [])

    def test_hardening_119(self):
        self.assertEqual(server._parse_roster('   \n   '), [])

    def test_hardening_120(self):
        self.assertIsNone(tools.toolkit_entry('non_existent_toolkit_entry_id'))

    def test_hardening_121(self):
        self.assertEqual(len(tools.TOOLKIT), 19)

    def test_hardening_122(self):
        for entry in tools.TOOLKIT:
            self.assertTrue('id' in entry and 'name' in entry and 'prompt' in entry and 'fields' in entry)

    def test_hardening_123(self):
        for entry in tools.TOOLKIT:
            for f in entry['fields']:
                self.assertTrue('key' in f and 'label' in f)

    def test_hardening_124(self):
        res = stats.analyse('Aarav, 90')
        self.assertIn('Aarav', res)
        self.assertIn('Class average', res)

    def test_hardening_125(self):
        res = stats.analyse('Aarav, 80\nDiya, 90\nRohan, 70')
        self.assertIn('Class average', res)
        self.assertIn('Highest', res)

    def test_hardening_126(self):
        with self.assertRaises(stats.MarksError):
            stats.analyse('Just random text without numbers')

    def test_hardening_127(self):
        res = stats.analyse('Aarav, 85\nDiya, 95')
        self.assertIn('Aarav', res)
        self.assertIn('Diya', res)

    def test_hardening_128(self):
        self.assertEqual(tools.toolkit_entry('rubric')['name'], 'Rubric')

    def test_hardening_129(self):
        self.assertEqual(tools.toolkit_entry('worksheet')['name'], 'Worksheet')

    def test_hardening_130(self):
        self.assertEqual(tools.toolkit_entry('notice')['name'], 'Notice or circular')

    def test_hardening_131(self):
        self.assertEqual(tools.toolkit_entry('letter')['name'], 'Letter to the principal')

    def test_hardening_132(self):
        self.assertEqual(tools.toolkit_entry('slides')['name'], 'Lesson slides')

    def test_hardening_133(self):
        self.assertEqual(tools.toolkit_entry('activity')['name'], 'Classroom activity')

    def test_hardening_134(self):
        self.assertEqual(tools.toolkit_entry('remedial')['name'], 'Remedial plan')

    def test_hardening_135(self):
        self.assertEqual(tools.toolkit_entry('pacing')['name'], 'Syllabus pacing')

    def test_hardening_136(self):
        self.assertEqual(tools.toolkit_entry('doubt')['name'], 'Solve a doubt')

    def test_hardening_137(self):
        self.assertEqual(tools.toolkit_entry('bilingual')['name'], 'Explain in two languages')

if __name__ == "__main__":
    unittest.main(verbosity=2)
