"""Float — using the computer, visibly.

When an operator says "open the dispatch sheet and fill in today's bookings", Float
can do it: move the pointer, click, type. That is a serious capability to hand to
a program, so three things are true of it here.

**You can see it.** Float does not borrow the system cursor silently. It draws
its own pointer — a ring that travels to the target and lands on it a beat before
the click — and a banner across the top of the screen saying what it is doing.
Automation you cannot see is automation you cannot supervise.

**You can stop it.** Escape, the banner's stop button, or the stop control in the
app. The flag is checked between every step, so the worst case is one action in
flight, not a queue draining into your files.

**It is written down.** Every step goes to the audit log with the operator's name
against it, and an admin can switch the whole capability off for the agency.

**It can see.** After every run Float looks at the screen and hands the model a
numbered list of the buttons, links and boxes in the front window (with their
real positions) and, for models that can read images, a screenshot with those
numbers drawn on it. Float then clicks "[7]", not "somewhere around 400,300".
Its overlay outlines what it is looking at, so you can see what it sees.

Both dependencies are optional. Without ``pyautogui`` Float says plainly that it
cannot drive the machine, rather than pretending to and doing nothing. Without a
display, the pointer overlay is skipped and the actions still run.
"""

from __future__ import annotations

import base64
import difflib
import io
import os
import platform
import re
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from . import db, desktop

desktop.make_dpi_aware()   # before pyautogui or Tk exist: clicks must land where the pointer is drawn

try:  # pragma: no cover - depends on the host
    import pyautogui  # type: ignore

    pyautogui.FAILSAFE = True          # slam the pointer into a corner to abort
    pyautogui.PAUSE = 0.06
    HAVE_PYAUTOGUI = True
except Exception:
    pyautogui = None  # type: ignore
    HAVE_PYAUTOGUI = False

try:  # pragma: no cover - only used for the Escape watcher
    import keyboard  # type: ignore

    HAVE_KEYBOARD = True
except Exception:
    keyboard = None  # type: ignore
    HAVE_KEYBOARD = False

SYSTEM = platform.system()
_MOD = "command" if SYSTEM == "Darwin" else "ctrl"

#: Typing faster than this looks like a macro and trips some input fields.
_TYPE_INTERVAL = 0.012
#: How long the pointer takes to travel. Fast enough not to be tedious, slow
#: enough that a person can follow it and reach for Escape.
_GLIDE = 0.45
#: Pixels kept clear of the screen edge: pyautogui's fail-safe fires in the
#: corners, and a click there would abort the run for no reason.
_EDGE = 3
_MAX_SECONDS = 300
#: The longest side of the screenshot sent to the model.
_SHOT_MAX = 1400


class Stopped(Exception):
    """Raised when the operator interrupts a run."""


@dataclass
class Session:
    user_id: int
    user_name: str
    intent: str
    started: float = field(default_factory=time.time)
    steps: list[str] = field(default_factory=list)
    stop: threading.Event = field(default_factory=threading.Event)
    target: Any = None            # the window Float is working in (desktop.Win)
    mute_until: float = 0.0       # Float's own Escape key presses must not stop the run


_current: Session | None = None
_lock = threading.RLock()
_overlay: "_Overlay | None" = None
#: What Float saw last. Kept between runs so "[7]" from one look can be used in
#: the next run; every use re-checks the element is still there.
_elements: list[desktop.Element] = []


def available() -> tuple[bool, str]:
    if not HAVE_PYAUTOGUI:
        return False, (
            "Pointer control needs one extra package. Run "
            "`pip install pyautogui` in the Float folder, then restart Float."
        )
    if db.org_get("computer_control", "1") != "1":
        return False, "Your agency has switched pointer control off for all accounts."
    return True, "Ready."


def screen_size() -> tuple[int, int]:
    if not HAVE_PYAUTOGUI:
        return (0, 0)
    try:
        size = pyautogui.size()
        return int(size[0]), int(size[1])
    except Exception:
        return (0, 0)


def _clamp(x: int, y: int) -> tuple[int, int]:
    """Keep a target on-screen and out of the fail-safe corners. A bad tool call
    should never send the pointer off a monitor, into a negative coordinate or
    into a corner that aborts the run."""
    width, height = screen_size()
    if width <= 0 or height <= 0:
        return x, y
    return (max(_EDGE, min(x, width - 1 - _EDGE)), max(_EDGE, min(y, height - 1 - _EDGE)))


def _int(kwargs: dict[str, Any], key: str, default: int | None = None) -> int:
    value = kwargs.get(key)
    if value is None or value == "":
        if default is None:
            raise ValueError(f"{key} is needed (a whole number of screen pixels)")
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        raise ValueError(f"{key} must be a number, not {value!r}") from None


# ---------------------------------------------------------------------------
# The visible pointer
# ---------------------------------------------------------------------------
class _Overlay:
    """Float's pointer, banner and "what I'm looking at" outlines.

    Tkinter, because it ships with Python, on its own thread. It is entirely
    optional: if the display refuses it, every method becomes a no-op and the
    automation carries on without the visuals.

    On Windows it is a full-screen, see-through, **click-through** window - the
    drawn ring must never swallow the click Float is about to make, and the
    window must never take focus from the app being driven. Elsewhere, where
    see-through windows are unreliable, it is only a small banner at the top, so
    it can never black out the screen.
    """

    def __init__(self, accent: str = "#E8A33D") -> None:
        self.accent = accent
        self.ok = False
        self.full = SYSTEM == "Windows"
        self._queue: list[Callable[[], None]] = []
        self._queue_lock = threading.Lock()
        self._root = None
        self._canvas = None
        self._ring = None
        self._dot = None
        self._banner = None
        self._banner_bg = None
        self._width = 0
        self._thread = threading.Thread(target=self._run, daemon=True, name="float-overlay")
        self._ready = threading.Event()
        self._thread.start()
        self._ready.wait(timeout=3.0)

    def _run(self) -> None:
        try:
            import tkinter as tk

            root = tk.Tk()
            root.title("tk")
            root.overrideredirect(True)
            root.attributes("-topmost", True)
            screen_w, screen_h = root.winfo_screenwidth(), root.winfo_screenheight()
            if self.full:
                root.attributes("-transparentcolor", "#010203")
                root.geometry(f"{screen_w}x{screen_h}+0+0")
                width, height = screen_w, screen_h
            else:
                width, height = 660, 48
                root.geometry(f"{width}x{height}+{max(0, (screen_w - width) // 2)}+12")
            canvas = tk.Canvas(root, bg="#010203" if self.full else "#1E3A32",
                               highlightthickness=0, width=width, height=height)
            canvas.pack(fill="both", expand=True)
            root.update_idletasks()
            if self.full:
                self._click_through(root)

            self._root, self._canvas, self._width = root, canvas, width

            def pump() -> None:
                with self._queue_lock:
                    jobs, self._queue = self._queue, []
                for job in jobs:
                    try:
                        job()
                    except Exception:
                        pass
                root.after(16, pump)

            self.ok = True
            self._ready.set()
            root.after(16, pump)
            root.mainloop()
        except Exception:
            self.ok = False
            self._ready.set()

    @staticmethod
    def _click_through(root: Any) -> None:
        """Layered + transparent + no-activate + tool window: mouse clicks fall
        through to the app underneath and the overlay can never take focus."""
        try:
            import ctypes
            u = ctypes.windll.user32
            hwnd = u.GetParent(root.winfo_id()) or root.winfo_id()
            style = u.GetWindowLongW(hwnd, -20)
            u.SetWindowLongW(hwnd, -20, style | 0x80000 | 0x20 | 0x08000000 | 0x80)
        except Exception:
            pass

    def _post(self, job: Callable[[], None]) -> None:
        if not self.ok:
            return
        with self._queue_lock:
            self._queue.append(job)

    def banner(self, text: str) -> None:
        def draw() -> None:
            canvas = self._canvas
            for item in (self._banner, self._banner_bg):
                if item is not None:
                    canvas.delete(item)
            top = 18 if self.full else 2
            mid = self._width / 2
            self._banner_bg = canvas.create_rectangle(
                mid - 320, top, mid + 320, top + 44, fill="#1E3A32", outline=self.accent, width=2)
            self._banner = canvas.create_text(
                mid, top + 22, text=text[:90], fill="#FBF9F4", font=("Segoe UI", 11, "bold"))

        self._post(draw)

    def move(self, x: int, y: int) -> None:
        if not self.full:
            return

        def draw() -> None:
            canvas = self._canvas
            for item in (self._ring, self._dot):
                if item is not None:
                    canvas.delete(item)
            self._ring = canvas.create_oval(x - 22, y - 22, x + 22, y + 22, outline=self.accent, width=3)
            self._dot = canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=self.accent, outline="")

        self._post(draw)

    def flash(self, x: int, y: int) -> None:
        if not self.full:
            return

        def draw() -> None:
            canvas = self._canvas
            pulse = canvas.create_oval(x - 34, y - 34, x + 34, y + 34, outline="#FBF9F4", width=3)
            canvas.after(220, lambda: canvas.delete(pulse))

        self._post(draw)

    def look(self, boxes: list[tuple[int, int, int, int, int]], seconds: float = 1.6) -> None:
        """Outline what Float is looking at: (id, left, top, width, height)."""
        if not self.full or not boxes:
            return

        def draw() -> None:
            canvas = self._canvas
            items = []
            for ident, left, top, width, height in boxes:
                items.append(canvas.create_rectangle(left, top, left + width, top + height,
                                                     outline=self.accent, width=2))
                items.append(canvas.create_text(left + 3, max(top - 1, 0), text=str(ident), anchor="sw",
                                                fill=self.accent, font=("Segoe UI", 8, "bold")))
            canvas.after(int(seconds * 1000), lambda: [canvas.delete(i) for i in items])

        self._post(draw)

    def close(self) -> None:
        def shut() -> None:
            try:
                self._root.destroy()
            except Exception:
                pass

        self._post(shut)
        self.ok = False


# ---------------------------------------------------------------------------
# Escape watcher
# ---------------------------------------------------------------------------
def _watch_for_escape(session: Session) -> None:
    """Watch for Escape and stop the run the moment *the operator* presses it.

    Best effort, never required - the stop button and the API both work without
    this. Float's own Escape presses (closing a menu, say) are muted, or the run
    would stop itself.
    """
    if not HAVE_KEYBOARD:
        return
    try:
        while not session.stop.is_set():
            if keyboard.is_pressed("esc") and time.time() > session.mute_until:
                session.stop.set()
                return
            time.sleep(0.05)
    except Exception:
        return


# ---------------------------------------------------------------------------
# Session control
# ---------------------------------------------------------------------------
def begin(user_id: int, user_name: str, intent: str, accent: str = "#E8A33D") -> Session:
    global _current, _overlay
    with _lock:
        live = _current
        if live is not None and not live.stop.is_set() and time.time() - live.started < _MAX_SECONDS + 30:
            raise RuntimeError("Float is already using the computer. Stop that run first.")
        if live is not None:                                # a dead run must not block the next one
            live.stop.set()
            if _overlay:
                _overlay.close()
        session = Session(user_id=user_id, user_name=user_name, intent=intent)
        _current = session
        _overlay = _Overlay(accent)
        _overlay.banner(f"Float is using your computer — {intent[:60]}   ·   press Esc to stop")
        threading.Thread(target=_watch_for_escape, args=(session,),
                         daemon=True, name="float-escape-watch").start()
    db.audit("computer.begin", user_id=user_id, actor=user_name, detail=intent, level="warn")
    return session


def end(note: str = "finished") -> None:
    global _current, _overlay
    with _lock:
        session = _current
        _current = None
        overlay, _overlay = _overlay, None
    if overlay:
        overlay.close()
    if session:
        session.stop.set()                                  # also ends the Escape watcher
        db.audit(
            "computer.end",
            user_id=session.user_id,
            actor=session.user_name,
            detail=f"{note}; {len(session.steps)} steps in {time.time() - session.started:.1f}s",
            level="warn",
        )


def stop_current() -> bool:
    with _lock:
        session = _current
        if session is None:
            return False
        session.stop.set()
        db.audit("computer.stop", user_id=session.user_id, actor=session.user_name,
                 detail="stopped by the operator", level="warn")
        end("stopped by the operator")
    return True


def current_status() -> dict[str, Any]:
    with _lock:
        session = _current
    if session is None:
        return {"running": False}
    return {
        "running": True,
        "intent": session.intent,
        "steps": session.steps[-12:],
        "seconds": round(time.time() - session.started, 1),
    }


def _guard(session: Session) -> None:
    if session.stop.is_set():
        raise Stopped("Stopped.")
    if time.time() - session.started > _MAX_SECONDS:
        raise Stopped("This run took longer than five minutes, so I stopped it.")


def _note(session: Session, text: str) -> None:
    session.steps.append(text)
    overlay = _overlay
    if overlay:
        overlay.banner(f"Float: {text[:70]}   ·   press Esc to stop")


# ---------------------------------------------------------------------------
# Keys
# ---------------------------------------------------------------------------
_KEY_ALIASES = {
    "return": "enter", "escape": "esc", "control": "ctrl", "ctl": "ctrl", "cmd": "command",
    "meta": "command", "super": "win", "windows": "win", "option": "alt", "del": "delete",
    "pgup": "pageup", "pgdn": "pagedown", "page up": "pageup", "page down": "pagedown",
    "spacebar": "space", " ": "space", "bksp": "backspace", "back": "backspace",
    "arrowup": "up", "arrowdown": "down", "arrowleft": "left", "arrowright": "right",
    "up arrow": "up", "down arrow": "down", "left arrow": "left", "right arrow": "right",
}


def _norm_key(raw: Any) -> str:
    """One key name pyautogui really knows. pyautogui silently ignores a name it
    doesn't recognise, which looks like success; here it is an error instead."""
    key = str(raw).strip().lower()
    key = _KEY_ALIASES.get(key, key)
    known = getattr(pyautogui, "KEYBOARD_KEYS", None) if HAVE_PYAUTOGUI else None
    if isinstance(known, (list, tuple, set, frozenset)) and key not in known:
        close = difflib.get_close_matches(key, [k for k in known if len(k) > 1], n=3)
        hint = f" Did you mean {', '.join(close)}?" if close else ""
        raise ValueError(f"'{raw}' is not a key I know.{hint}")
    return key


def _split_keys(raw: Any) -> list[str]:
    """'ctrl+l' and ['ctrl', 'l'] both mean the same chord."""
    parts = raw if isinstance(raw, (list, tuple)) else [raw]
    out: list[str] = []
    for part in parts:
        text = str(part).strip()
        if len(text) > 1 and "+" in text.strip("+"):
            out.extend(p for p in text.split("+") if p.strip())
        elif text:
            out.append(text)
    return [_norm_key(k) for k in out]


def _send(session: Session, *keys: str) -> None:
    if "esc" in keys:
        session.mute_until = time.time() + 0.6
    if len(keys) == 1:
        pyautogui.press(keys[0])
    else:
        pyautogui.hotkey(*keys)


# ---------------------------------------------------------------------------
# Eyes
# ---------------------------------------------------------------------------
def _screenshot_b64(elements: list[desktop.Element]) -> dict[str, str] | None:
    """A JPEG of the screen for models that can read images. With named controls
    each one is boxed and numbered; without, a labelled grid makes coordinates
    readable. All labels are in real screen pixels whatever the picture's size."""
    if not HAVE_PYAUTOGUI:
        return None
    try:
        from PIL import ImageDraw  # type: ignore

        img = pyautogui.screenshot().convert("RGB")
        full_w, full_h = img.size
        scale = min(1.0, _SHOT_MAX / max(full_w, full_h))
        if scale < 1.0:
            img = img.resize((int(full_w * scale), int(full_h * scale)))
        draw = ImageDraw.Draw(img)
        accent = (232, 163, 61)
        if elements:
            for e in elements:
                left, top = (e.x - e.w // 2) * scale, (e.y - e.h // 2) * scale
                right, bottom = (e.x + e.w // 2) * scale, (e.y + e.h // 2) * scale
                draw.rectangle([left, top, right, bottom], outline=accent, width=2)
                label = str(e.id)
                draw.rectangle([left, max(top - 11, 0), left + 7 * len(label) + 4, max(top - 11, 0) + 11],
                               fill=accent)
                draw.text((left + 2, max(top - 11, 0)), label, fill=(0, 0, 0))
        else:
            step = 200
            for gx in range(0, full_w, step):
                draw.line([gx * scale, 0, gx * scale, img.size[1]], fill=(255, 60, 60), width=1)
            for gy in range(0, full_h, step):
                draw.line([0, gy * scale, img.size[0], gy * scale], fill=(255, 60, 60), width=1)
            for gx in range(0, full_w, step):
                for gy in range(0, full_h, step):
                    draw.text((gx * scale + 2, gy * scale + 2), f"{gx},{gy}", fill=(255, 60, 60))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=70)
        return {"media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode("ascii")}
    except Exception:
        return None


def _front_window(session: Session | None) -> "desktop.Win | None":
    cur = desktop.active_window() if desktop.can_verify() else None
    if cur is not None and not desktop.looks_like_float(cur) and cur.title.lower() != "tk":
        return cur
    return session.target if session is not None else None


def observe(session: Session | None = None, want_image: bool = False,
            settle: float = 0.4, show: bool = True) -> tuple[str, dict[str, str] | None]:
    """Look at the screen. Returns (text for the model, optional screenshot).

    The text names what is in front, what else is open and - when the controls
    can be read - a numbered list of them. The numbers are remembered so the next
    step can say "click [7]"."""
    global _elements
    if settle:
        time.sleep(settle)
    width, height = screen_size()
    lines: list[str] = []
    elements: list[desktop.Element] = []
    win = None
    try:
        win = _front_window(session)
        if desktop.can_verify():
            wins = "; ".join(w.title[:40] for w in desktop.list_windows()[:8]) or "none I can read"
            lines.append(f"Screen {width}x{height}. In front: “{win.title[:70] if win else 'unknown'}”. Open: {wins}.")
        else:
            lines.append(f"Screen {width}x{height}. I can't list windows on this system.")
        if win is not None and desktop.uia_available():
            try:
                elements = desktop.snapshot(win, screen=(width, height))
            except desktop.ActionFailed as exc:
                lines.append(str(exc))
        elif win is not None and desktop.SYSTEM == "Windows":
            lines.append("(Install `pywinauto` and I can read button and box names.)")
    except Exception as exc:                                # looking must never break a run
        lines.append(f"(I couldn't fully read the screen: {exc})")

    _elements = elements
    if elements:
        lines.append("Controls in the front window — act on one with element=N (click, type, double_click, "
                     "right_click) or by its name (click_control, type into):")
        lines.extend(e.line() for e in elements)
    else:
        lines.append("I can't read named controls here. " + (
            "Use the screenshot's red grid (labels are screen pixels) with click x,y, or keyboard shortcuts."
            if want_image else "Use keyboard shortcuts (ctrl+l, tab, enter) or a click x,y the operator gave."))
    overlay = _overlay
    if show and overlay and elements:
        overlay.look([(e.id, e.x - e.w // 2, e.y - e.h // 2, e.w, e.h) for e in elements])
    image = _screenshot_b64(elements) if want_image else None
    return "\n".join(lines), image


def _resolve(session: Session, ref: Any) -> desktop.Element:
    """Turn "[7]" into a live element: look again, find the same control (by
    kind and name, nearest where it was) and use where it is *now*."""
    digits = re.sub(r"\D", "", str(ref))
    if not digits:
        raise ValueError(f"element must be a number from the list I gave you, not {ref!r}")
    number = int(digits)
    old = next((e for e in _elements if e.id == number), None)
    if old is None:
        raise desktop.ActionFailed(
            f"There is no element [{number}] in my last look. Use the see action to look again.")
    if not desktop.uia_available():
        return old
    win = _work_window(session)
    try:
        fresh = desktop.snapshot(win, screen=screen_size())
    except desktop.ActionFailed:
        return old
    same = [e for e in fresh if e.kind == old.kind and e.name == old.name]
    if same:
        return min(same, key=lambda e: (e.x - old.x) ** 2 + (e.y - old.y) ** 2)
    if fresh:
        raise desktop.ActionFailed(
            f"[{number}] {old.kind} “{old.name[:40]}” is no longer on screen. "
            f"Now I can see: {'; '.join(e.name for e in fresh if e.name)[:300]}.")
    return old


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------
def _glide(session: Session, x: int, y: int) -> None:
    """Move Float's pointer to the target, visibly, then take the system one with it."""
    _guard(session)
    overlay = _overlay
    if overlay and overlay.ok and overlay.full:
        start = pyautogui.position() if HAVE_PYAUTOGUI else (x, y)
        steps = 18
        for i in range(1, steps + 1):
            _guard(session)
            t = i / steps
            ease = 1 - (1 - t) ** 3
            overlay.move(int(start[0] + (x - start[0]) * ease), int(start[1] + (y - start[1]) * ease))
            time.sleep(_GLIDE / steps)
    if HAVE_PYAUTOGUI:
        pyautogui.moveTo(x, y, duration=0.12)


ACTIONS = frozenset({
    "move", "click", "double_click", "right_click", "type", "press", "hotkey", "scroll", "wait",
    "open", "open_app", "focus_window", "list_windows", "search_web", "click_control",
    "focus_field", "describe", "see",
})


def _truthy(value: Any) -> bool:
    return value is True or str(value).strip().lower() in {"1", "true", "yes"}


def _ensure_focus(session: Session, doing: str) -> None:
    """Never type into the wrong place. If something else has taken the screen,
    take it back once; if it still isn't right, stop and say so."""
    if not desktop.can_verify():
        return
    cur = desktop.active_window()
    target = session.target
    if target is None:
        if cur is not None and desktop.looks_like_float(cur):
            raise desktop.ActionFailed(
                "Float itself is in front, so I stopped before " + doing + " into it. "
                "Open or switch to the app first (open, focus_window or search_web).")
        return
    if cur is None or desktop.same_app(cur, target):
        return
    desktop.bring_forward(target)
    cur = desktop.active_window()
    if cur is None or desktop.same_app(cur, target):
        return
    raise desktop.ActionFailed(
        f"'{cur.title[:50]}' took over the screen, so I stopped before {doing} in the wrong window.")


def _work_window(session: Session) -> "desktop.Win":
    _ensure_focus(session, "going on")
    win = session.target or desktop.active_window()
    if win is None:
        raise desktop.ActionFailed("I can't tell which window is in front. Open or switch to an app first.")
    return win


def _titles(limit: int = 10) -> str:
    return "; ".join(w.title[:45] for w in desktop.list_windows()[:limit]) or "none I can read"


def _check_point(session: Session, x: int, y: int) -> None:
    """The click must land in the app Float is working in - not on a window that
    has slid over it, the taskbar, or Float itself."""
    target = session.target
    if target is None:
        return
    hit = desktop.window_at(x, y)
    if hit is None or (hit.pid and hit.pid == os.getpid()):
        return
    if desktop.same_app(hit, target) or (hit.exe and hit.exe == getattr(target, "exe", "")):
        return
    desktop.bring_forward(target)
    hit = desktop.window_at(x, y)
    if hit is None or desktop.same_app(hit, target) or (hit.exe and hit.exe == getattr(target, "exe", "")):
        return
    raise desktop.ActionFailed(
        f"The spot ({x},{y}) belongs to '{hit.title[:40] or hit.exe or 'another window'}', not "
        f"'{target.title[:40]}', so I didn't click. Look again (see) and pick a control by number.")


def _click_at(session: Session, x: int, y: int, button: str = "left", clicks: int = 1) -> tuple[int, int]:
    _ensure_focus(session, "clicking")
    x, y = _clamp(x, y)
    _check_point(session, x, y)
    _glide(session, x, y)
    overlay = _overlay
    if overlay:
        overlay.flash(x, y)
    pyautogui.click(button=button, clicks=clicks, interval=0.08)
    time.sleep(0.15)
    return x, y


def _is_browser(win: "desktop.Win") -> bool:
    text = f"{win.exe} {win.title}".lower()
    return any(b in text for b in ("chrome", "edge", "firefox", "brave", "opera", "safari"))


def _focus_box(session: Session, label: str) -> str:
    """Put the keyboard cursor in the named box. Uses the real control when it
    can be read; browsers' address bar works from the keyboard even when not."""
    win = _work_window(session)
    ref = str(label).strip()
    if re.fullmatch(r"\[?\d+\]?", ref):
        el = _resolve(session, ref)
    elif desktop.uia_available():
        el = desktop.find_element(win, ref, desktop._FIELD_KINDS, screen=screen_size())
    else:
        low = ref.lower()
        if _is_browser(win) and any(w in low for w in ("address", "url", "search", "omnibox")):
            _send(session, _MOD, "l")
            time.sleep(0.15)
            return f"focused the '{ref}' box (Ctrl+L)"
        desktop._need_uia()
        raise AssertionError  # pragma: no cover - _need_uia always raises here
    _click_at(session, el.x, el.y)
    return f"clicked the '{el.name or ref}' box"


def act(session: Session, action: str, **kwargs: Any) -> str:
    """Perform one step. Returns a sentence describing what happened."""
    _guard(session)
    ok, reason = available()
    if not ok:
        raise RuntimeError(reason)
    action = str(action).strip().lower()
    if action not in ACTIONS:
        raise ValueError(f"Float does not know the action '{action}'. Known: {', '.join(sorted(ACTIONS))}.")
    try:
        _act(session, action, kwargs)
    except Exception as exc:
        if type(exc).__name__ == "FailSafeException":       # pointer hit a screen corner
            raise Stopped("The pointer reached a screen corner, which is the emergency stop. I stopped.") from None
        raise
    db.audit("computer.step", user_id=session.user_id, actor=session.user_name,
             detail=session.steps[-1] if session.steps else action)
    return session.steps[-1] if session.steps else action


def _act(session: Session, action: str, kwargs: dict[str, Any]) -> None:
    if action == "move":
        x, y = _clamp(_int(kwargs, "x"), _int(kwargs, "y"))
        _glide(session, x, y)
        _note(session, f"moved to {x}, {y}")

    elif action in {"click", "double_click", "right_click"}:
        button = "right" if action == "right_click" else "left"
        clicks = 2 if action == "double_click" else 1
        if kwargs.get("element") not in (None, ""):
            el = _resolve(session, kwargs["element"])
            _click_at(session, el.x, el.y, button, clicks)
            _note(session, f"{action.replace('_', ' ')} on [{el.id}] {el.kind} “{el.name[:40]}”")
        elif kwargs.get("x") not in (None, "") and kwargs.get("y") not in (None, ""):
            x, y = _click_at(session, _int(kwargs, "x"), _int(kwargs, "y"), button, clicks)
            _note(session, f"{action.replace('_', ' ')} at {x}, {y}")
        else:
            _ensure_focus(session, "clicking")
            pyautogui.click(button=button, clicks=clicks, interval=0.08)
            _note(session, action.replace("_", " ") + " where the pointer is")

    elif action == "type":
        text = str(kwargs.get("text", ""))[:4000]
        if not text:
            raise ValueError("type needs text")
        into = kwargs.get("element") if kwargs.get("element") not in (None, "") else kwargs.get("into")
        if into not in (None, ""):
            _note(session, _focus_box(session, str(into)))
        else:
            _ensure_focus(session, "typing")
        if _truthy(kwargs.get("clear")):
            _send(session, _MOD, "a")
            time.sleep(0.05)
        _type_text(text)
        submit = _truthy(kwargs.get("submit"))
        if submit:
            time.sleep(0.15)
            _send(session, "enter")
        preview = text[:40] + ("…" if len(text) > 40 else "")
        _note(session, f"typed “{preview}”" + (" and pressed Enter" if submit else ""))

    elif action == "press":
        keys = _split_keys(kwargs.get("key") or kwargs.get("keys") or "")
        if not keys:
            raise ValueError("press needs a key")
        if "win" not in keys:
            _ensure_focus(session, "pressing " + "+".join(keys))
        _send(session, *keys)
        _note(session, "pressed " + " + ".join(keys))

    elif action == "hotkey":
        keys = _split_keys(kwargs.get("keys") or kwargs.get("key") or [])
        if not keys:
            raise ValueError("hotkey needs keys")
        if "win" not in keys:
            _ensure_focus(session, "pressing " + "+".join(keys))
        _send(session, *keys)
        _note(session, "pressed " + " + ".join(keys))

    elif action == "scroll":
        amount = _int(kwargs, "amount", -400)
        _ensure_focus(session, "scrolling")
        if kwargs.get("element") not in (None, ""):
            el = _resolve(session, kwargs["element"])
            _glide(session, *_clamp(el.x, el.y))
        elif kwargs.get("x") not in (None, "") and kwargs.get("y") not in (None, ""):
            _glide(session, *_clamp(_int(kwargs, "x"), _int(kwargs, "y")))
        else:                                               # scroll the app, not whatever the pointer rests on
            rect = desktop.window_rect(session.target) if session.target is not None else None
            if rect:
                _glide(session, *_clamp((rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2))
        pyautogui.scroll(amount)
        _note(session, f"scrolled {'down' if amount < 0 else 'up'}")

    elif action == "wait":
        try:
            seconds = max(0.0, min(15.0, float(kwargs.get("seconds", 1))))
        except (TypeError, ValueError):
            raise ValueError("wait needs seconds as a number") from None
        until = str(kwargs.get("until") or "").strip().lower()
        deadline = time.time() + seconds
        seen = False
        while time.time() < deadline:
            _guard(session)
            if until and _appeared(session, until):
                seen = True
                break
            time.sleep(0.5 if until else 0.1)
        if until:
            _note(session, f"waited for “{until[:30]}”: " + ("it appeared" if seen else f"not seen after {seconds:g}s"))
        else:
            _note(session, f"waited {seconds:g}s")

    elif action in {"open", "open_app"}:
        target = str(kwargs.get("target") or kwargs.get("name") or "").strip()
        if not target:
            raise ValueError("open needs something to open")
        if target.lower().startswith(("http://", "https://")):
            win, message = desktop.open_url(target)
        elif _looks_like_path(target):
            win, message = desktop.open_path(os.path.expanduser(target))
        else:
            win, message = desktop.open_app(target, fallback=_launch_via_search)
        if win is not None:
            session.target = win
        _note(session, message)

    elif action == "focus_window":
        title = str(kwargs.get("title") or kwargs.get("name") or kwargs.get("target") or "").strip()
        if not title:
            raise ValueError("focus_window needs part of the window's title")
        win = desktop.find_window([title])
        if win is None:
            raise desktop.ActionFailed(f"No open window matches '{title}'. Open windows: {_titles()}.")
        if not desktop.bring_forward(win):
            raise desktop.ActionFailed(f"I found '{win.title[:40]}' but couldn't bring it to the front.")
        session.target = win
        _note(session, f"switched to {win.title[:50]}")

    elif action == "list_windows":
        cur = desktop.active_window()
        _note(session, f"saw: in front “{cur.title[:50] if cur else 'unknown'}”; open: {_titles()}")

    elif action == "search_web":
        query = str(kwargs.get("query") or kwargs.get("text") or "").strip()
        if not query:
            raise ValueError("search_web needs a query")
        win, _msg = desktop.open_url(desktop.search_url(query, str(kwargs.get("engine", "google"))))
        if win is not None:
            session.target = win
        _note(session, f"searched {kwargs.get('engine') or 'google'} for “{query[:40]}”")

    elif action == "focus_field":
        label = str(kwargs.get("element") or kwargs.get("label") or kwargs.get("into") or "search").strip()
        _note(session, _focus_box(session, label))

    elif action == "click_control":
        label = str(kwargs.get("label") or kwargs.get("name") or "").strip()
        if not label:
            raise ValueError("click_control needs the name of the button or link")
        win = _work_window(session)
        el = desktop.find_element(win, label, desktop._CLICK_KINDS, screen=screen_size())
        _click_at(session, el.x, el.y)
        _note(session, f"clicked '{el.name or label}'")

    elif action in {"see", "describe"}:
        text, _image = observe(session, want_image=False, settle=0.2)
        count = len(_elements)
        _note(session, f"looked at the screen ({count} controls)" if count else "looked at the screen")


def _appeared(session: Session, needle: str) -> bool:
    """Has a window or control with this text shown up?"""
    try:
        if any(needle in w.title.lower() for w in desktop.list_windows()):
            return True
        if desktop.uia_available() and session.target is not None:
            return any(needle in e.name.lower() for e in desktop.snapshot(session.target))
    except Exception:
        pass
    return False


def finish_report(session: Session | None = None, want_image: bool = False
                  ) -> tuple[str, dict[str, str] | None]:
    """What the model gets back after a run: the screen as it is *now*, so it
    reports what happened rather than what it hoped would happen."""
    try:
        return observe(session, want_image=want_image)
    except Exception:
        return "", None


def state_summary() -> str:
    """One line version of the above, kept for callers that only want text."""
    try:
        return observe(None, want_image=False, settle=0, show=False)[0].split("\n")[0]
    except Exception:
        return ""


def _looks_like_path(target: str) -> bool:
    return (os.path.exists(os.path.expanduser(target)) or target.startswith(("~", "/", "\\\\"))
            or re.match(r"^[A-Za-z]:[\\/]", target) is not None)


def _launch_via_search(name: str) -> None:
    """Last resort for an app Float can't find by name: the system search box."""
    pyautogui.press("command" if SYSTEM == "Darwin" else "win")
    time.sleep(0.8)
    _type_text(name)
    time.sleep(1.0)
    pyautogui.press("enter")


def _paste_text(text: str) -> bool:
    """Paste instead of typing: instant, never drops characters, handles Hindi
    and accents. Returns False if there is no working clipboard, in which case
    nothing has been typed yet. Once the paste keystroke is sent it returns True
    even if restoring the clipboard fails - typing again would duplicate the text."""
    try:
        import pyperclip  # type: ignore
    except Exception:
        return False
    previous = None
    try:
        previous = pyperclip.paste()
    except Exception:
        pass
    try:
        pyperclip.copy(text)
    except Exception:
        return False
    time.sleep(0.05)
    try:
        pyautogui.hotkey(_MOD, "v")
    except Exception as exc:
        if type(exc).__name__ == "FailSafeException":
            raise
        return False
    time.sleep(0.25)
    if previous is not None:
        try:
            pyperclip.copy(previous)
        except Exception:
            pass
    return True


def _type_text(text: str) -> None:
    if _paste_text(text):
        return
    try:
        pyautogui.typewrite(text, interval=_TYPE_INTERVAL)
        return
    except (KeyError, ValueError):
        pass
    for ch in text:                                         # at least the ASCII part lands
        try:
            pyautogui.typewrite(ch, interval=_TYPE_INTERVAL)
        except Exception as exc:
            if type(exc).__name__ == "FailSafeException":
                raise
            continue


def screenshot_size() -> dict[str, int]:
    width, height = screen_size()
    return {"width": width, "height": height}
