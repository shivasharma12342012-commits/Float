"""Computer-control reliability: apps are found by name, typing never lands in the wrong window."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from float import computer, desktop, tools

W = desktop.Win


def fake_session():
    return computer.Session(user_id=1, user_name="T", intent="test")


class Names(unittest.TestCase):
    def test_aliases_normalise(self):
        for said in ("Google Chrome", "the Chrome browser", "chrome"):
            self.assertIn(desktop.norm(said), desktop.APPS)
        self.assertEqual(desktop.norm("Microsoft Word"), "word")
        self.assertEqual(desktop.norm("MS Excel"), "excel")

    def test_start_menu_picks_the_right_shortcut(self):
        with tempfile.TemporaryDirectory() as d:
            for n in ("Google Chrome.lnk", "Chrome Remote Desktop.lnk", "Uninstall Chrome.lnk",
                      "Microsoft Word.lnk", "Zoom Workplace.lnk", "Notes.lnk"):
                (Path(d) / n).write_text("")
            find = lambda name: desktop.find_start_shortcut(name, [Path(d)])
            self.assertEqual(find("chrome").name, "Google Chrome.lnk")
            self.assertEqual(find("word").name, "Microsoft Word.lnk")
            self.assertEqual(find("zoom").name, "Zoom Workplace.lnk")
            self.assertIsNone(find("photoshop"))

    def test_search_url_is_encoded(self):
        self.assertEqual(desktop.search_url("class 8 maths प्रश्न", "google").split("q=")[0],
                         "https://www.google.com/search?")
        self.assertIn("a+b", desktop.search_url("a b"))
        self.assertIn("youtube.com", desktop.search_url("x", "youtube"))


class Schema(unittest.TestCase):
    def test_every_schema_action_is_handled(self):
        schema = next(t for t in tools.TOOL_SCHEMAS if t["name"] == "use_computer")
        enum = set(schema["parameters"]["properties"]["steps"]["items"]["properties"]["action"]["enum"])
        self.assertEqual(enum, set(computer.ACTIONS))


class Guarded(unittest.TestCase):
    """The core promise: never type into the wrong window."""

    def setUp(self):
        self.py = mock.MagicMock()
        patches = [
            mock.patch.object(computer, "pyautogui", self.py), mock.patch.object(computer, "HAVE_PYAUTOGUI", True),
            mock.patch.object(computer, "available", return_value=(True, "")), mock.patch.object(computer, "_overlay", None),
            mock.patch.object(computer.db, "audit"), mock.patch.object(desktop, "can_verify", return_value=True),
            mock.patch.object(computer, "_paste_text", return_value=True),
        ]
        for p in patches:
            p.start(); self.addCleanup(p.stop)

    def test_refuses_to_type_into_float_itself(self):
        with mock.patch.object(desktop, "active_window", return_value=W(1, "Float", 10)):
            with self.assertRaises(desktop.ActionFailed) as cm:
                computer.act(fake_session(), "type", text="hello")
        self.assertIn("Float itself", str(cm.exception))

    def test_refuses_when_focus_was_stolen(self):
        s = fake_session(); s.target = W(5, "Notepad", 50)
        with mock.patch.object(desktop, "active_window", return_value=W(9, "Chat popup", 90)), \
             mock.patch.object(desktop, "bring_forward", return_value=False):
            with self.assertRaises(desktop.ActionFailed) as cm:
                computer.act(s, "type", text="hello")
        self.assertIn("wrong window", str(cm.exception))
        self.py.hotkey.assert_not_called()

    def test_types_when_the_right_window_is_in_front(self):
        s = fake_session(); s.target = W(5, "Notepad", 50)
        with mock.patch.object(desktop, "active_window", return_value=W(5, "Untitled - Notepad", 50)):
            out = computer.act(s, "type", text="hello", submit=True)
        self.assertIn("pressed Enter", out)
        self.py.press.assert_called_with("enter")

    def test_dialog_from_same_program_is_allowed(self):
        s = fake_session(); s.target = W(5, "Word", 50)
        with mock.patch.object(desktop, "active_window", return_value=W(8, "Save As", 50)):
            computer.act(s, "type", text="Plan.docx")

    def test_open_sets_the_target_and_reports(self):
        s = fake_session()
        chrome = W(7, "New Tab - Google Chrome", 70)
        with mock.patch.object(desktop, "open_app", return_value=(chrome, "Opened chrome")) as op:
            self.assertEqual(computer.act(s, "open", target="chrome"), "Opened chrome")
        self.assertEqual(s.target, chrome); op.assert_called_once()

    def test_focus_window_lists_what_is_open_when_missing(self):
        with mock.patch.object(desktop, "list_windows", return_value=[W(1, "Notepad", 1), W(2, "Excel", 2)]):
            with self.assertRaises(desktop.ActionFailed) as cm:
                computer.act(fake_session(), "focus_window", title="Photoshop")
        self.assertIn("Notepad", str(cm.exception))

    def test_win_key_is_not_blocked(self):
        with mock.patch.object(desktop, "active_window", return_value=W(1, "Float", 10)):
            computer.act(fake_session(), "press", key="win")
        self.py.press.assert_called_with("win")

    def test_run_stops_after_five_minutes(self):
        s = fake_session(); s.started -= 400
        with self.assertRaises(computer.Stopped):
            computer.act(s, "wait", seconds=1)


class OpenApp(unittest.TestCase):
    def test_already_open_app_is_switched_to_not_relaunched(self):
        chrome = W(7, "Docs - Google Chrome", 70)
        with mock.patch.object(desktop, "can_verify", return_value=True), \
             mock.patch.object(desktop, "list_windows", return_value=[chrome]), \
             mock.patch.object(desktop, "bring_forward", return_value=True), \
             mock.patch.object(desktop, "_launch") as launch:
            win, msg = desktop.open_app("Google Chrome")
        self.assertEqual(win, chrome); launch.assert_not_called(); self.assertIn("Switched", msg)

    def test_launch_then_confirm_window(self):
        pad = W(3, "Untitled - Notepad", 30)
        seen = iter([[], [pad], [pad]])
        with mock.patch.object(desktop, "can_verify", return_value=True), \
             mock.patch.object(desktop, "list_windows", side_effect=lambda: next(seen, [pad])), \
             mock.patch.object(desktop, "bring_forward", return_value=True), \
             mock.patch.object(desktop, "_launch") as launch, mock.patch.object(desktop.time, "sleep"):
            win, msg = desktop.open_app("notepad")
        self.assertEqual(win, pad); launch.assert_called_once(); self.assertEqual(msg, "Opened notepad")

    def test_fails_loudly_when_no_window_appears(self):
        with mock.patch.object(desktop, "can_verify", return_value=True), \
             mock.patch.object(desktop, "list_windows", return_value=[]), \
             mock.patch.object(desktop, "_launch"), mock.patch.object(desktop.time, "sleep"):
            with self.assertRaises(desktop.ActionFailed):
                desktop.open_app("notepad", timeout=0.01)

    def test_best_control_prefers_exact_name(self):
        found = [("a", "Search tabs", ""), ("b", "Search", ""), ("c", "Address and search bar", "")]
        self.assertEqual(desktop._best("search", found), "b")
        self.assertEqual(desktop._best("address", found), "c")
        self.assertIsNone(desktop._best("zzz", found))


if __name__ == "__main__":
    unittest.main()
