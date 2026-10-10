"""Float — the desktop layer: windows, apps and on-screen controls, found by name.

Clicking at guessed coordinates is how a computer assistant ends up typing into
the wrong window. Everything here works the other way round: ask the operating
system what is open, bring the right window forward, *confirm* it is in front,
and (on Windows, with ``pywinauto``) find buttons and search boxes by their
names instead of by pixels. When something cannot be done or cannot be
confirmed, ``ActionFailed`` carries a plain sentence saying what was seen, so
the run stops honestly instead of carrying on blind.
"""
from __future__ import annotations

import difflib
import importlib.util
import os
import platform
import re
import shutil
import subprocess
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

SYSTEM = platform.system()


class ActionFailed(Exception):
    """A step could not be done, or could not be confirmed. Written to be read."""


@dataclass(frozen=True)
class Win:
    handle: int
    title: str
    pid: int = 0


def make_dpi_aware() -> None:
    """Without this, Windows scaled to 125-150% reports one set of pixels and
    clicks in another, so every click lands off-target."""
    if SYSTEM != "Windows":
        return
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Windows: list, front, focus
# ---------------------------------------------------------------------------
_SKIP_TITLES = {"program manager", "windows input experience", "microsoft text input application",
                "msctfime ui", "default ime", "tk"}


def _win_title(hwnd: int) -> str:
    import ctypes
    u = ctypes.windll.user32
    n = u.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(n + 1)
    u.GetWindowTextW(hwnd, buf, n + 1)
    return buf.value.strip()


def _win_pid(hwnd: int) -> int:
    import ctypes
    from ctypes import wintypes
    pid = wintypes.DWORD(0)
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return int(pid.value)


def _windows_list() -> list[Win]:
    import ctypes
    from ctypes import wintypes
    u = ctypes.windll.user32
    out: list[Win] = []
    proc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd: Any, _: Any) -> bool:
        try:
            if not u.IsWindowVisible(hwnd) or u.GetWindowTextLengthW(hwnd) == 0:
                return True
            if u.GetWindowLongW(hwnd, -20) & 0x80:          # tool windows (tray popups etc.)
                return True
            cloaked = ctypes.c_int(0)
            try:
                ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(cloaked), ctypes.sizeof(cloaked))
            except Exception:
                pass
            if cloaked.value:                               # suspended UWP shells
                return True
            title = _win_title(hwnd)
            if title and title.lower() not in _SKIP_TITLES:
                out.append(Win(int(hwnd), title, _win_pid(hwnd)))
        except Exception:
            pass
        return True

    u.EnumWindows(proc(visit), 0)
    return out


def _mac(script: str) -> str:
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=6)
    return r.stdout.strip()


def list_windows() -> list[Win]:
    """Visible top-level windows, front-most first. Empty if this system can't say."""
    try:
        if SYSTEM == "Windows":
            return _windows_list()
        if SYSTEM == "Darwin":
            names = _mac('tell application "System Events" to get name of (processes where background only is false)')
            return [Win(0, n.strip(), 0) for n in names.split(", ") if n.strip()]
        if shutil.which("wmctrl"):
            rows = subprocess.run(["wmctrl", "-l", "-p"], capture_output=True, text=True, timeout=5).stdout.splitlines()
            out = []
            for row in rows:
                parts = row.split(None, 4)
                if len(parts) == 5 and parts[1] != "-1":
                    out.append(Win(int(parts[0], 16), parts[4].strip(), int(parts[2])))
            return out[::-1]
    except Exception:
        pass
    return []


def active_window() -> Win | None:
    try:
        if SYSTEM == "Windows":
            import ctypes
            hwnd = int(ctypes.windll.user32.GetForegroundWindow() or 0)
            return Win(hwnd, _win_title(hwnd), _win_pid(hwnd)) if hwnd else None
        if SYSTEM == "Darwin":
            name = _mac('tell application "System Events" to get name of first process whose frontmost is true')
            return Win(0, name, 0) if name else None
        if shutil.which("xdotool"):
            r = subprocess.run(["xdotool", "getactivewindow", "getwindowname"], capture_output=True, text=True, timeout=5)
            return Win(0, r.stdout.strip(), 0) if r.stdout.strip() else None
    except Exception:
        pass
    return None


def can_verify() -> bool:
    """True when this system can tell us which window is in front."""
    if SYSTEM in ("Windows", "Darwin"):
        return True
    return bool(shutil.which("wmctrl") and shutil.which("xdotool"))


def same_app(a: Win, b: Win) -> bool:
    if a.handle and a.handle == b.handle:
        return True
    if a.pid and a.pid == b.pid:                            # a dialog from the same program
        return True
    return not a.handle and not b.handle and a.title.lower() == b.title.lower()


def looks_like_float(w: Win) -> bool:
    return w.title.strip().lower().startswith("float")


def focus(w: Win) -> None:
    if SYSTEM == "Windows":
        import ctypes
        u = ctypes.windll.user32
        if u.IsIconic(w.handle):
            u.ShowWindow(w.handle, 9)                       # restore
        u.keybd_event(0x12, 0, 0, 0)                        # a tap of Alt lets us take the foreground
        u.keybd_event(0x12, 0, 2, 0)
        u.BringWindowToTop(w.handle)
        u.SetForegroundWindow(w.handle)
    elif SYSTEM == "Darwin":
        _mac(f'tell application "{w.title}" to activate')
    elif w.handle and shutil.which("wmctrl"):
        subprocess.run(["wmctrl", "-i", "-a", hex(w.handle)], timeout=5)


def bring_forward(w: Win, tries: int = 3) -> bool:
    """Focus a window and check that it really is in front."""
    for _ in range(tries):
        try:
            focus(w)
        except Exception:
            pass
        time.sleep(0.35)
        cur = active_window()
        if cur is None or not can_verify() or same_app(cur, w):
            return True
    return False


def find_window(needles: list[str], windows: list[Win] | None = None) -> Win | None:
    wanted = [n.lower() for n in needles if n]
    for w in windows if windows is not None else list_windows():
        title = w.title.lower()
        if wanted and any(n in title for n in wanted) and not looks_like_float(w):
            return w
    return None


# ---------------------------------------------------------------------------
# Apps
# ---------------------------------------------------------------------------
_NOISE = {"the", "app", "application", "browser", "ms", "microsoft", "please"}


def norm(text: str) -> str:
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()
    return " ".join(w for w in words if w not in _NOISE) or " ".join(words)


#: name -> (things Windows can launch directly, words that appear in its window title)
APPS: dict[str, tuple[list[str], list[str]]] = {
    "chrome": (["chrome"], ["chrome"]), "google chrome": (["chrome"], ["chrome"]),
    "edge": (["msedge"], ["edge"]), "firefox": (["firefox"], ["firefox"]), "brave": (["brave"], ["brave"]),
    "notepad": (["notepad"], ["notepad"]), "calculator": (["calc"], ["calculator"]), "calc": (["calc"], ["calculator"]),
    "paint": (["mspaint"], ["paint"]), "word": (["winword"], ["word"]), "excel": (["excel"], ["excel"]),
    "powerpoint": (["powerpnt"], ["powerpoint"]), "outlook": (["outlook"], ["outlook"]),
    "onenote": (["onenote"], ["onenote"]), "file explorer": (["explorer"], []), "explorer": (["explorer"], []),
    "settings": (["ms-settings:"], ["settings"]), "whatsapp": (["whatsapp:"], ["whatsapp"]),
    "spotify": (["spotify:"], ["spotify"]), "teams": (["msteams:"], ["teams"]),
    "command prompt": (["cmd"], ["command prompt"]), "cmd": (["cmd"], ["command prompt"]),
    "terminal": (["wt"], ["terminal"]), "task manager": (["taskmgr"], ["task manager"]),
    "snipping tool": (["snippingtool"], ["snipping"]), "vlc": (["vlc"], ["vlc"]), "zoom": (["zoom"], ["zoom"]),
}


def _start_dirs() -> list[Path]:
    roots = []
    for var in ("PROGRAMDATA", "APPDATA"):
        base = os.environ.get(var)
        if base:
            roots.append(Path(base) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    return [r for r in roots if r.exists()]


def _score(target: str, stem: str) -> float:
    t, s = target.split(), stem.split()
    if not t or not s:
        return 0.0
    if target == stem:
        return 100.0
    if set(t) <= set(s):
        return 80.0 - 8.0 * (len(s) - len(t))
    if set(s) <= set(t):
        return 75.0 - 8.0 * (len(t) - len(s))
    ratio = difflib.SequenceMatcher(None, target, stem).ratio()
    return 60.0 * ratio if ratio >= 0.8 else 0.0


def find_start_shortcut(name: str, roots: list[Path] | None = None) -> Path | None:
    """Find an installed app by name from the Start Menu, so any program works,
    not just the ones Float has heard of."""
    target = norm(name)
    best: tuple[float, Path] | None = None
    for root in roots if roots is not None else _start_dirs():
        for folder, _dirs, files in os.walk(root):
            for f in files:
                if not f.lower().endswith((".lnk", ".url", ".appref-ms")):
                    continue
                stem = norm(Path(f).stem)
                if "uninstall" in stem or "readme" in stem:
                    continue
                score = _score(target, stem)
                if score >= 50 and (best is None or score > best[0]):
                    best = (score, Path(folder) / f)
    return best[1] if best else None


def _launch(raw: str, key: str, launch: list[str], fallback: Callable[[str], None] | None) -> None:
    if SYSTEM == "Windows":
        start = getattr(os, "startfile", None)
        for cand in launch:
            try:
                start(cand)                                  # type: ignore[misc]
                return
            except OSError:
                continue
        lnk = find_start_shortcut(raw)
        if lnk:
            try:
                start(str(lnk))                              # type: ignore[misc]
                return
            except OSError:
                pass
        if fallback:
            fallback(raw)
            return
        raise ActionFailed(f"I couldn't find an app called '{raw}' on this computer.")
    if SYSTEM == "Darwin":
        r = subprocess.run(["open", "-a", raw], capture_output=True, timeout=20)
        if r.returncode != 0:
            raise ActionFailed(f"I couldn't find an app called '{raw}' on this Mac.")
        return
    for cand in dict.fromkeys(launch + [key.replace(" ", "-"), key.split(" ")[0] if key else ""]):
        exe = shutil.which(cand) if cand else None
        if exe:
            subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return
    raise ActionFailed(f"I couldn't find an app called '{raw}' on this computer.")


def _wait_for(hints: list[str], before: set[int], timeout: float) -> Win | None:
    start = time.time()
    while time.time() - start < timeout:
        wins = list_windows()
        found = find_window(hints, wins) if hints else None
        if not found and time.time() - start > 3:           # unknown title: accept a brand-new window
            fresh = [w for w in wins if w.handle not in before and not looks_like_float(w)]
            found = fresh[0] if fresh else None
        if found:
            return found
        time.sleep(0.4)
    return None


def open_app(name: str, fallback: Callable[[str], None] | None = None,
             timeout: float = 15.0) -> tuple[Win | None, str]:
    raw = (name or "").strip()
    if not raw:
        raise ActionFailed("Tell me which app to open.")
    key = norm(raw)
    launch, hints = APPS.get(key, ([], [key] if key else []))
    if hints and can_verify():                              # already open: just bring it forward
        existing = find_window(hints)
        if existing:
            if not bring_forward(existing):
                raise ActionFailed(f"{raw} is open but I couldn't bring it to the front.")
            return existing, f"Switched to {raw}"
    before = {w.handle for w in list_windows()}
    _launch(raw, key, launch, fallback)
    if not can_verify():
        time.sleep(1.5)
        return None, f"Opened {raw} (I can't confirm the window on this system)"
    found = _wait_for(hints, before, timeout)
    if found is None:
        raise ActionFailed(f"I tried to open {raw} but no window appeared within {int(timeout)} seconds. "
                           "It may not be installed, or it may still be loading.")
    if not bring_forward(found):
        raise ActionFailed(f"{raw} opened but I couldn't bring it to the front.")
    return found, f"Opened {raw}"


def open_path(path: str, timeout: float = 10.0) -> tuple[Win | None, str]:
    before = {w.handle for w in list_windows()}
    if SYSTEM == "Windows":
        os.startfile(path)                                  # type: ignore[attr-defined]
    elif SYSTEM == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])
    if not can_verify():
        time.sleep(1.5)
        return None, f"Opened {path}"
    start = time.time()
    while time.time() - start < timeout:
        fresh = [w for w in list_windows() if w.handle not in before and not looks_like_float(w)]
        if fresh:
            bring_forward(fresh[0])
            return fresh[0], f"Opened {Path(path).name or path}"
        time.sleep(0.4)
    raise ActionFailed(f"I asked the system to open {path} but no window appeared.")


_BROWSERS = ["chrome", "edge", "firefox", "brave", "opera", "safari"]
_ENGINES = {
    "google": "https://www.google.com/search?q={}", "bing": "https://www.bing.com/search?q={}",
    "duckduckgo": "https://duckduckgo.com/?q={}", "youtube": "https://www.youtube.com/results?search_query={}",
    "maps": "https://www.google.com/maps/search/{}", "images": "https://www.google.com/search?tbm=isch&q={}",
}


def search_url(query: str, engine: str = "google") -> str:
    template = _ENGINES.get((engine or "google").lower(), _ENGINES["google"])
    return template.format(urllib.parse.quote_plus(query.strip()))


def open_url(url: str) -> tuple[Win | None, str]:
    if not url.lower().startswith(("http://", "https://")):
        raise ActionFailed("That doesn't look like a web address.")
    before = {w.handle for w in list_windows()}
    webbrowser.open(url, new=2)
    if not can_verify():
        time.sleep(2)
        return None, f"Opened {url[:60]}"
    start = time.time()
    while time.time() - start < 8:
        wins = list_windows()
        browser = find_window(_BROWSERS, wins)
        if browser:
            bring_forward(browser)
            return browser, f"Opened {url[:60]}"
        time.sleep(0.4)
    raise ActionFailed("I opened the address but no browser window appeared.")


# ---------------------------------------------------------------------------
# Controls by name (Windows, needs pywinauto)
# ---------------------------------------------------------------------------
_FIELD_KINDS = ("Edit", "ComboBox")
_CLICK_KINDS = ("Button", "MenuItem", "ListItem", "TabItem", "Hyperlink", "CheckBox", "RadioButton",
                "SplitButton", "TreeItem", "Edit", "ComboBox")


def uia_available() -> bool:
    return SYSTEM == "Windows" and importlib.util.find_spec("pywinauto") is not None


def _need_uia() -> None:
    if not uia_available():
        raise ActionFailed("Finding buttons and boxes by name needs one extra package on Windows: "
                           "run `pip install pywinauto`, then restart Float. Until then I can use "
                           "keyboard shortcuts instead (for example Ctrl+L for a browser's address bar).")


def _controls(win: Win, kinds: tuple[str, ...]) -> list[tuple[Any, str, str]]:
    from pywinauto import Desktop                           # type: ignore
    top = Desktop(backend="uia").window(handle=win.handle)
    out = []
    for kind in kinds:
        try:
            items = top.descendants(control_type=kind)
        except Exception:
            continue
        for c in items:
            try:
                if not c.is_visible():
                    continue
                name = (c.window_text() or c.element_info.name or "").strip()
                auto = str(getattr(c.element_info, "automation_id", "") or "")
                out.append((c, name, auto))
            except Exception:
                continue
    return out


def _best(label: str, found: list[tuple[Any, str, str]]) -> Any | None:
    want = norm(label)
    ranked = []
    for c, name, auto in found:
        n, a = norm(name), norm(auto)
        if n == want:
            score = 3
        elif n and n.startswith(want):
            score = 2
        elif (n and want in n) or (a and want in a):
            score = 1
        else:
            continue
        ranked.append((score, c))
    return max(ranked, key=lambda r: r[0])[1] if ranked else None


def find_control(win: Win, label: str, kinds: tuple[str, ...], timeout: float = 6.0) -> Any:
    _need_uia()
    deadline = time.time() + timeout
    while True:
        found = _controls(win, kinds)
        hit = _best(label, found)
        if hit is not None:
            return hit
        if time.time() >= deadline:
            names = [n for _c, n, _a in found if n][:12]
            seen = ("; ".join(names)) if names else "none I could read"
            raise ActionFailed(f"I couldn't find '{label}' in '{win.title[:40]}'. Controls I can see: {seen}.")
        time.sleep(0.5)


def focus_field(win: Win, label: str) -> str:
    c = find_control(win, label or "search", _FIELD_KINDS)
    c.click_input()
    time.sleep(0.2)
    try:
        if not c.has_keyboard_focus():
            c.set_focus()
    except Exception:
        pass
    return f"clicked the '{label or 'search'}' box"


def click_control(win: Win, label: str) -> str:
    c = find_control(win, label, _CLICK_KINDS)
    c.click_input()
    return f"clicked '{label}'"


def describe(win: Win, limit: int = 40) -> str:
    _need_uia()
    boxes = [n for _c, n, _a in _controls(win, _FIELD_KINDS) if n][:limit // 2]
    clicks = [n for _c, n, _a in _controls(win, _CLICK_KINDS[:-2]) if n][:limit]
    return (f"In '{win.title[:40]}' — boxes: {'; '.join(dict.fromkeys(boxes)) or 'none named'}. "
            f"Buttons and links: {'; '.join(dict.fromkeys(clicks)) or 'none named'}.")
