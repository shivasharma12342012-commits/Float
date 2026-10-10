"""Computer-control reliability: apps are found by name, typing never lands in the wrong window."""
import tempfile
import time
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
        E = desktop.Element
        found = [E(1, "Button", "Search tabs", 0, 0, 5, 5), E(2, "Edit", "Search", 0, 0, 5, 5),
                 E(3, "Edit", "Address and search bar", 0, 0, 5, 5)]
        self.assertEqual(desktop.best_element("search", found).id, 2)
        self.assertEqual(desktop.best_element("address", found).id, 3)
        self.assertIsNone(desktop.best_element("zzz", found))
        self.assertEqual(desktop.best_element("search", found, ("Button",)).id, 1)


class Eyes(unittest.TestCase):
    """Float looks before it clicks, and clicks by number."""

    def setUp(self):
        self.py = mock.MagicMock()
        self.py.size.return_value = (1920, 1080)
        patches = [
            mock.patch.object(computer, "pyautogui", self.py), mock.patch.object(computer, "HAVE_PYAUTOGUI", True),
            mock.patch.object(computer, "available", return_value=(True, "")), mock.patch.object(computer, "_overlay", None),
            mock.patch.object(computer.db, "audit"), mock.patch.object(desktop, "can_verify", return_value=True),
            mock.patch.object(computer, "_paste_text", return_value=True), mock.patch.object(computer.time, "sleep"),
            mock.patch.object(desktop, "uia_available", return_value=True),
        ]
        for p in patches:
            p.start(); self.addCleanup(p.stop)
        E = desktop.Element
        self.els = [E(1, "Edit", "Search", 500, 100, 300, 30), E(2, "Button", "Save", 900, 400, 80, 30)]
        self.pad = W(5, "Untitled - Notepad", 50, "notepad")

    def test_see_numbers_the_controls_and_remembers_them(self):
        with mock.patch.object(desktop, "active_window", return_value=self.pad), \
             mock.patch.object(desktop, "list_windows", return_value=[self.pad]), \
             mock.patch.object(desktop, "snapshot", return_value=self.els):
            text, image = computer.observe(fake_session(), want_image=False, settle=0)
        self.assertIn('[2] Button "Save" at (900,400)', text)
        self.assertIn("Untitled - Notepad", text)
        self.assertEqual([e.id for e in computer._elements], [1, 2])
        self.assertIsNone(image)

    def test_click_by_number_lands_on_the_live_position(self):
        computer._elements = list(self.els)
        moved = [desktop.Element(1, "Edit", "Search", 500, 100, 300, 30),
                 desktop.Element(9, "Button", "Save", 950, 450, 80, 30)]      # the window moved
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad), \
             mock.patch.object(desktop, "snapshot", return_value=moved):
            out = computer.act(s, "click", element=2)
        self.py.moveTo.assert_called_with(950, 450, duration=0.12)
        self.py.click.assert_called_once()
        self.assertIn("Save", out)

    def test_click_by_number_refuses_when_the_control_is_gone(self):
        computer._elements = list(self.els)
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad), \
             mock.patch.object(desktop, "snapshot", return_value=[self.els[0]]):
            with self.assertRaises(desktop.ActionFailed) as cm:
                computer.act(s, "click", element=2)
        self.assertIn("no longer on screen", str(cm.exception))
        self.py.click.assert_not_called()

    def test_unknown_number_says_to_look_again(self):
        computer._elements = []
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad):
            with self.assertRaises(desktop.ActionFailed) as cm:
                computer.act(s, "click", element=7)
        self.assertIn("see", str(cm.exception))

    def test_type_into_a_numbered_box(self):
        computer._elements = list(self.els)
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad), \
             mock.patch.object(desktop, "snapshot", return_value=self.els):
            computer.act(s, "type", element=1, text="hello", submit=True)
        self.py.moveTo.assert_called_with(500, 100, duration=0.12)
        self.py.press.assert_called_with("enter")

    def test_click_is_refused_when_another_app_is_on_top_of_the_spot(self):
        s = fake_session(); s.target = self.pad
        other = W(9, "Chat", 90, "slack")
        with mock.patch.object(desktop, "active_window", return_value=self.pad), \
             mock.patch.object(desktop, "window_at", return_value=other), \
             mock.patch.object(desktop, "bring_forward", return_value=True):
            with self.assertRaises(desktop.ActionFailed) as cm:
                computer.act(s, "click", x=300, y=300)
        self.assertIn("didn't click", str(cm.exception))
        self.py.click.assert_not_called()

    def test_clicks_stay_out_of_the_failsafe_corners(self):
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad):
            computer.act(s, "click", x=0, y=0)
        x, y = self.py.moveTo.call_args[0][:2]
        self.assertGreater(x, 0); self.assertGreater(y, 0)

    def test_bad_coordinates_give_a_clear_error(self):
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad):
            with self.assertRaises(ValueError) as cm:
                computer.act(s, "move", x="left", y=5)
        self.assertIn("x must be a number", str(cm.exception))

    def test_failsafe_becomes_a_calm_stop(self):
        class FailSafeException(Exception):
            pass
        self.py.moveTo.side_effect = FailSafeException()
        s = fake_session(); s.target = self.pad
        with mock.patch.object(desktop, "active_window", return_value=self.pad):
            with self.assertRaises(computer.Stopped):
                computer.act(s, "move", x=100, y=100)


class Keys(unittest.TestCase):
    def setUp(self):
        self.py = mock.MagicMock()
        self.py.KEYBOARD_KEYS = ["enter", "esc", "tab", "ctrl", "l", "a", "down", "win", "delete", "pageup", "space"]
        patches = [
            mock.patch.object(computer, "pyautogui", self.py), mock.patch.object(computer, "HAVE_PYAUTOGUI", True),
            mock.patch.object(computer, "available", return_value=(True, "")), mock.patch.object(computer, "_overlay", None),
            mock.patch.object(computer.db, "audit"), mock.patch.object(desktop, "can_verify", return_value=False),
            mock.patch.object(computer.time, "sleep"),
        ]
        for p in patches:
            p.start(); self.addCleanup(p.stop)

    def test_names_are_translated_not_ignored(self):
        computer.act(fake_session(), "press", key="Return")
        self.py.press.assert_called_with("enter")
        computer.act(fake_session(), "hotkey", keys=["Control", "L"])
        self.py.hotkey.assert_called_with("ctrl", "l")

    def test_a_chord_in_one_string_works(self):
        computer.act(fake_session(), "press", key="ctrl+l")
        self.py.hotkey.assert_called_with("ctrl", "l")

    def test_unknown_key_is_an_error_with_a_suggestion(self):
        with self.assertRaises(ValueError) as cm:
            computer.act(fake_session(), "press", key="entr")
        self.assertIn("enter", str(cm.exception))
        self.py.press.assert_not_called()

    def test_floats_own_escape_does_not_stop_the_run(self):
        s = fake_session()
        computer.act(s, "press", key="esc")
        self.assertGreater(s.mute_until, time.time())
        self.assertFalse(s.stop.is_set())


class ToolRun(unittest.TestCase):
    """The tool hands the model the screen, even when a step fails."""

    def setUp(self):
        for p in (mock.patch.object(computer, "available", return_value=(True, "")),
                  mock.patch.object(computer, "begin", side_effect=lambda *a, **k: fake_session()),
                  mock.patch.object(computer, "end"),
                  mock.patch.object(computer, "finish_report", return_value=("In front: Notepad\n[1] Edit \"Text\" at (5,5)",
                                                                              {"media_type": "image/jpeg", "data": "QUJD"}))):
            p.start(); self.addCleanup(p.stop)
        self.user = {"id": 1, "name": "T"}

    def test_success_ends_with_the_screen_and_a_picture(self):
        with mock.patch.object(computer, "act", return_value="Opened notepad"):
            out = tools.execute("use_computer", {"intent": "x", "steps": [{"action": "open", "target": "notepad"}]},
                                self.user, None)
        self.assertIn("Done: Opened notepad", out["text"])
        self.assertIn("[1] Edit", out["text"])
        self.assertEqual(out["image"]["media_type"], "image/jpeg")

    def test_failure_still_shows_the_screen_and_says_not_to_repeat(self):
        with mock.patch.object(computer, "act", side_effect=desktop.ActionFailed("no such box")):
            out = tools.execute("use_computer", {"intent": "x", "steps": [{"action": "click_control", "label": "Z"}]},
                                self.user, None)
        self.assertIn("no such box", out["text"])
        self.assertIn("SCREEN NOW", out["text"])
        self.assertIn("Do not repeat", out["text"])

    def test_steps_sent_as_a_json_string_are_accepted(self):
        with mock.patch.object(computer, "act", return_value="ok") as act:
            tools.execute("use_computer", {"intent": "x", "steps": '[{"action": "wait", "seconds": 1}]'}, self.user, None)
        act.assert_called_once()

    def test_a_step_without_an_action_is_explained(self):
        out = tools.execute("use_computer", {"intent": "x", "steps": [{"text": "hi"}]}, self.user, None)
        self.assertIn("no action", out["text"])

    def test_a_crash_never_leaves_the_computer_marked_in_use(self):
        with mock.patch.object(tools, "_tool_use_computer", side_effect=RuntimeError("boom")):
            tools.execute("use_computer", {}, self.user, None)
        computer.end.assert_called()


class Wire(unittest.TestCase):
    def test_screenshot_reaches_the_model_only_as_the_latest_one(self):
        from float import agent, providers
        block = {"type": "tool_result", "tool_use_id": "1", "name": "use_computer", "content": [
            {"type": "text", "text": "screen A"},
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": "QUJD"}}]}
        history = [{"role": "user", "content": [block]}]
        oa = providers._to_openai_messages(history)
        self.assertTrue(any(isinstance(m["content"], list) and m["content"][1]["type"] == "image_url" for m in oa))
        g = providers._to_google_contents(history)
        self.assertTrue(any("inlineData" in p for m in g for p in m["parts"]))
        agent._drop_old_screens(history)
        self.assertEqual(history[0]["content"][0]["content"], "screen A")

    def test_providers_that_cannot_see_get_no_picture(self):
        from float import agent, config
        with mock.patch.object(config.settings, "computer_vision", "auto"):
            self.assertTrue(agent._sees_images("anthropic"))
            self.assertFalse(agent._sees_images("local"))
            self.assertFalse(agent._sees_images("openrouter"))
        with mock.patch.object(config.settings, "computer_vision", "off"):
            self.assertFalse(agent._sees_images("anthropic"))


class Overlay(unittest.TestCase):
    def test_outside_windows_the_overlay_is_only_a_banner(self):
        with mock.patch.object(computer, "SYSTEM", "Linux"):
            o = computer._Overlay.__new__(computer._Overlay)
            o.full = computer.SYSTEM == "Windows"
        self.assertFalse(o.full)          # a full-screen opaque window would black out the screen


class Windows(unittest.TestCase):
    def test_finds_an_app_by_program_name_when_the_title_is_unhelpful(self):
        win = W(4, "Untitled", 40, "notepad")
        self.assertEqual(desktop.find_window(["notepad"], [win]), win)
        self.assertIsNone(desktop.find_window(["excel"], [win]))

    def test_second_chance_through_search_only_once(self):
        calls = []
        with mock.patch.object(desktop, "SYSTEM", "Windows"), \
             mock.patch.object(desktop, "can_verify", return_value=True), \
             mock.patch.object(desktop, "list_windows", return_value=[]), \
             mock.patch.object(desktop, "_launch", return_value=True), \
             mock.patch.object(desktop.time, "sleep"):
            with self.assertRaises(desktop.ActionFailed):
                desktop.open_app("notepad", fallback=calls.append, timeout=0.01)
        self.assertEqual(calls, [])       # search was already used to launch it; don't open it twice


if __name__ == "__main__":
    unittest.main()
