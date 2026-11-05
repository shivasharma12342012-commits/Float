"""Float — the desktop layer: windows, apps and on-screen controls, found by name.

Clicking at guessed coordinates is how a computer assistant ends up typing into
the wrong window. Everything here works the other way round: ask the operating
system what is open, bring the right window forward, *confirm* it is in front,
and (on Windows via Win32/``pywinauto``, or on macOS via ``osascript``/System Events)
find windows, buttons, and search boxes by their names instead of by pixels. When something cannot be done or cannot be
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
    exe: str = ""          # program file name without ".exe", lower case (Windows)


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


def _win_exe(pid: int) -> str:
    """Name of the program that owns a window, so 'notepad' is found even when
    its title is 'Untitled'. Empty when Windows won't say."""
    if SYSTEM != "Windows" or not pid:
        return ""
    try:
        import ctypes
        from ctypes import wintypes
        k = ctypes.windll.kernel32
        k.OpenProcess.restype = wintypes.HANDLE
        handle = k.OpenProcess(0x1000, False, pid)           # QUERY_LIMITED_INFORMATION
        if not handle:
            return ""
        try:
            size = wintypes.DWORD(520)
            buf = ctypes.create_unicode_buffer(520)
            if k.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
                return Path(buf.value).stem.lower()
        finally:
            k.CloseHandle(handle)
    except Exception:
        pass
    return ""


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
                pid = _win_pid(hwnd)
                out.append(Win(int(hwnd), title, pid, _win_exe(pid)))
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
            if not hwnd:
                return None
            pid = _win_pid(hwnd)
            return Win(hwnd, _win_title(hwnd), pid, _win_exe(pid))
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
        safe_title = w.title.replace("\\", "\\\\").replace('"', '\\"')
        _mac(f'tell application "{safe_title}" to activate')
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


def _matches(w: Win, wanted: list[str]) -> bool:
    title = w.title.lower()
    for n in wanted:
        if n in title:
            return True
        if w.exe and (n == w.exe or (len(n) >= 3 and n in w.exe)):
            return True
    return False


def find_window(needles: list[str], windows: list[Win] | None = None) -> Win | None:
    wanted = [n.lower() for n in needles if n]
    if not wanted:
        return None
    me = os.getpid()
    pool = windows if windows is not None else list_windows()
    for w in pool:                                          # the front-most match wins
        if _matches(w, wanted) and not looks_like_float(w) and not (w.pid and w.pid == me):
            return w
    return None


def window_rect(w: Win) -> tuple[int, int, int, int] | None:
    """(left, top, right, bottom) of a window in screen pixels, or None."""
    if SYSTEM != "Windows" or not w.handle:
        return None
    try:
        import ctypes
        from ctypes import wintypes
        r = wintypes.RECT()
        if ctypes.windll.user32.GetWindowRect(w.handle, ctypes.byref(r)):
            return int(r.left), int(r.top), int(r.right), int(r.bottom)
    except Exception:
        pass
    return None


def window_at(x: int, y: int) -> Win | None:
    """The top-level window under a screen point (Windows only). Float's own
    click-through overlay never answers - it is transparent to hit-testing."""
    if SYSTEM != "Windows":
        return None
    try:
        import ctypes
        from ctypes import wintypes
        u = ctypes.windll.user32
        u.WindowFromPoint.argtypes = [wintypes.POINT]
        u.WindowFromPoint.restype = wintypes.HWND
        u.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
        u.GetAncestor.restype = wintypes.HWND
        hwnd = u.WindowFromPoint(wintypes.POINT(int(x), int(y)))
        if not hwnd:
            return None
        root = u.GetAncestor(hwnd, 2) or hwnd               # GA_ROOT
        pid = _win_pid(root)
        return Win(int(root), _win_title(root), pid, _win_exe(pid))
    except Exception:
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


def _launch(raw: str, key: str, launch: list[str], fallback: Callable[[str], None] | None) -> bool:
    """Start an app. Returns True if the system search box was used to do it."""
    if SYSTEM == "Windows":
        start = getattr(os, "startfile", None)
        for cand in launch:
            try:
                start(cand)                                  # type: ignore[misc]
                return False
            except OSError:
                continue
        lnk = find_start_shortcut(raw)
        if lnk:
            try:
                start(str(lnk))                              # type: ignore[misc]
                return False
            except OSError:
                pass
        if fallback:
            fallback(raw)
            return True
        raise ActionFailed(f"I couldn't find an app called '{raw}' on this computer.")
    if SYSTEM == "Darwin":
        mac_map = {
            "chrome": "Google Chrome", "google chrome": "Google Chrome",
            "edge": "Microsoft Edge", "brave": "Brave Browser", "firefox": "Firefox",
            "safari": "Safari", "notepad": "TextEdit", "textedit": "TextEdit",
            "calculator": "Calculator", "calc": "Calculator",
            "word": "Microsoft Word", "excel": "Microsoft Excel",
            "powerpoint": "Microsoft PowerPoint", "outlook": "Microsoft Outlook",
            "onenote": "Microsoft OneNote", "file explorer": "Finder", "explorer": "Finder",
            "finder": "Finder", "settings": "System Settings", "cmd": "Terminal",
            "command prompt": "Terminal", "terminal": "Terminal",
            "task manager": "Activity Monitor", "notes": "Notes", "preview": "Preview",
        }
        candidates = list(dict.fromkeys([mac_map.get(key, ""), raw] + launch))
        for cand in [c for c in candidates if c]:
            r = subprocess.run(["open", "-a", cand], capture_output=True, timeout=20)
            if r.returncode == 0:
                return False
        if fallback:
            fallback(raw)
            return True
        raise ActionFailed(f"I couldn't find an app called '{raw}' on this Mac.")
    for cand in dict.fromkeys(launch + [key.replace(" ", "-"), key.split(" ")[0] if key else ""]):
        exe = shutil.which(cand) if cand else None
        if exe:
            subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            return False
    raise ActionFailed(f"I couldn't find an app called '{raw}' on this computer.")


def _win_id(w: Win) -> int | str:
    return w.handle if w.handle else w.title.lower()


def _wait_for(hints: list[str], before: set[Any], timeout: float) -> Win | None:
    start = time.time()
    while time.time() - start < timeout:
        wins = list_windows()
        found = find_window(hints, wins) if hints else None
        if not found and time.time() - start > 3:           # unknown title: accept a brand-new window
            fresh = [w for w in wins if _win_id(w) not in before and not looks_like_float(w)]
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
    before = {_win_id(w) for w in list_windows()}
    used_search = _launch(raw, key, launch, fallback)
    if not can_verify():
        time.sleep(1.5)
        return None, f"Opened {raw} (I can't confirm the window on this system)"
    found = _wait_for(hints, before, timeout)
    if found is None and fallback is not None and SYSTEM == "Windows" and used_search is not True:
        try:                                                # second chance: the system search box
            fallback(raw)
        except Exception:
            pass
        found = _wait_for(hints, before, min(timeout, 10.0))
    if found is None:
        raise ActionFailed(f"I tried to open {raw} but no window appeared within {int(timeout)} seconds. "
                           "It may not be installed, or it may still be loading.")
    if not bring_forward(found):
        raise ActionFailed(f"{raw} opened but I couldn't bring it to the front.")
    return found, f"Opened {raw}"


def open_path(path: str, timeout: float = 10.0) -> tuple[Win | None, str]:
    before = {_win_id(w) for w in list_windows()}
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
        fresh = [w for w in list_windows() if _win_id(w) not in before and not looks_like_float(w)]
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
# Eyes: what is on screen, by name and position (Windows, needs pywinauto)
# ---------------------------------------------------------------------------
_FIELD_KINDS = ("Edit", "ComboBox")
_CLICK_KINDS = ("Button", "MenuItem", "ListItem", "TabItem", "Hyperlink", "CheckBox", "RadioButton",
                "SplitButton", "TreeItem", "Edit", "ComboBox")
_SEE_KINDS = frozenset(_CLICK_KINDS) | {"Document", "Slider", "DataItem"}
MAX_ELEMENTS = 80
_SNAPSHOT_SECONDS = 7.0


@dataclass(frozen=True)
class Element:
    """One thing on screen Float can act on. ``x``/``y`` are the centre, in real
    screen pixels - exactly where a click should land."""
    id: int
    kind: str
    name: str
    x: int
    y: int
    w: int
    h: int
    auto: str = ""

    def line(self) -> str:
        return f'[{self.id}] {self.kind} "{self.name[:60]}" at ({self.x},{self.y})'


def uia_available() -> bool:
    return SYSTEM == "Windows" and importlib.util.find_spec("pywinauto") is not None


def _need_uia() -> None:
    if not uia_available():
        raise ActionFailed("Finding buttons and boxes by name needs one extra package on Windows: "
                           "run `pip install pywinauto`, then restart Float. Until then I can use "
                           "keyboard shortcuts instead (for example Ctrl+L for a browser's address bar).")


def _walk(win: Win, out: list) -> None:
    """Collect raw (kind, name, auto, rect) rows. Runs on a helper thread so a
    huge page cannot hang the run."""
    try:
        try:                                                # COM must be initialised on this thread
            import comtypes  # type: ignore
            comtypes.CoInitialize()
        except Exception:
            pass
        from pywinauto import Desktop as UiaDesktop         # type: ignore
        top = UiaDesktop(backend="uia").window(handle=win.handle)
        for info in top.element_info.descendants():
            try:
                kind = str(info.control_type or "")
                if kind not in _SEE_KINDS:
                    continue
                if getattr(info, "visible", True) is False:
                    continue
                rect = info.rectangle
                width, height = int(rect.right - rect.left), int(rect.bottom - rect.top)
                if width <= 1 or height <= 1:
                    continue
                name = str(info.name or "").strip()
                auto = str(getattr(info, "automation_id", "") or "")
                out.append((kind, name, auto, int(rect.left), int(rect.top), width, height))
            except Exception:
                continue
    except Exception as exc:                                # pragma: no cover - depends on the host
        out.append(exc)


def snapshot(win: Win, limit: int = MAX_ELEMENTS, screen: tuple[int, int] = (0, 0)) -> list[Element]:
    """Numbered list of what can be clicked or typed into in ``win``, in reading
    order. Raises ActionFailed with a plain reason when it can't look."""
    _need_uia()
    import threading
    rows: list = []
    worker = threading.Thread(target=_walk, args=(win, rows), daemon=True, name="float-eyes")
    worker.start()
    worker.join(timeout=_SNAPSHOT_SECONDS)
    if worker.is_alive():
        raise ActionFailed(f"'{win.title[:40]}' is too busy or too large for me to read its buttons in "
                           f"{int(_SNAPSHOT_SECONDS)} seconds. Use keyboard shortcuts or the screenshot.")
    errors = [r for r in rows if isinstance(r, Exception)]
    rows = [r for r in rows if not isinstance(r, Exception)]
    if not rows and errors:
        raise ActionFailed(f"I couldn't read '{win.title[:40]}': {errors[0]}")
    sw, sh = screen
    kept = []
    for kind, name, auto, left, top, width, height in rows:
        cx, cy = left + width // 2, top + height // 2
        if cx < 0 or cy < 0 or (sw and cx >= sw) or (sh and cy >= sh):
            continue                                        # off-screen
        if not name and kind not in ("Edit", "ComboBox", "Document"):
            continue                                        # nothing to call it by
        if any(k[2] == kind and k[3] == (name or auto) and abs(k[4] - cx) < 8 and abs(k[5] - cy) < 8
               for k in kept):
            continue                                        # the same control reported twice
        kept.append((cy // 12, cx, kind, name or auto or "(unnamed box)", cx, cy, width, height, auto))
    kept.sort()
    return [Element(i + 1, k[2], k[3], k[4], k[5], k[6], k[7], k[8]) for i, k in enumerate(kept[:limit])]


def best_element(label: str, elements: list[Element], kinds: tuple[str, ...] | None = None) -> Element | None:
    """The element whose name best matches ``label`` (exact > starts-with > contains)."""
    want = norm(label)
    if not want:
        return None
    ranked: list[tuple[int, int, Element]] = []
    for e in elements:
        if kinds and e.kind not in kinds:
            continue
        n, a = norm(e.name), norm(e.auto)
        if n == want:
            score = 3
        elif n and n.startswith(want):
            score = 2
        elif (n and want in n) or (a and want in a):
            score = 1
        else:
            continue
        ranked.append((score, -len(n), e))                  # shorter name = tighter match
    return max(ranked, key=lambda r: (r[0], r[1]))[2] if ranked else None


def find_element(win: Win, label: str, kinds: tuple[str, ...], timeout: float = 6.0,
                 screen: tuple[int, int] = (0, 0)) -> Element:
    deadline = time.time() + timeout
    while True:
        found = snapshot(win, screen=screen)
        hit = best_element(label, found, kinds)
        if hit is not None:
            return hit
        if time.time() >= deadline:
            names = [e.name for e in found if e.name][:15]
            seen = ("; ".join(names)) if names else "none I could read"
            raise ActionFailed(f"I couldn't find '{label}' in '{win.title[:40]}'. Controls I can see: {seen}.")
        time.sleep(0.5)


def describe(win: Win, limit: int = 40) -> str:
    els = snapshot(win)
    boxes = [e.name for e in els if e.kind in _FIELD_KINDS and e.name][:limit // 2]
    clicks = [e.name for e in els if e.kind not in _FIELD_KINDS and e.name][:limit]
    return (f"In '{win.title[:40]}' — boxes: {'; '.join(dict.fromkeys(boxes)) or 'none named'}. "
            f"Buttons and links: {'; '.join(dict.fromkeys(clicks)) or 'none named'}.")
