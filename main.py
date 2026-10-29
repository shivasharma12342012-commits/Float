#!/usr/bin/env python3
"""Float — start here.

    python main.py                 start Float, open the browser
    python main.py --no-browser    start without opening a window
    python main.py --tab           open in a normal browser tab instead of an app window
    python main.py --port 9000     use a different port
    python main.py set-password you@school.edu.in   reset someone's password from the terminal
    python main.py make-admin you@school.edu.in     promote an existing account
    python main.py stop            stop the running Float server
    python main.py --version

Everything Float needs lives next to this file once it has run once:
a `data/` folder holding `float.sqlite3` (your accounts, classes and chat
history) and `data/files` (documents Float has made for you, until you save
them to your Desktop or Drive). Delete `data/` to start over completely.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import webbrowser

import os
import traceback
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def _tell_user(message: str) -> None:
    """Float normally runs with no console window, so a failure would be invisible.
    Show it in a plain message box (Windows) and keep a copy in data/."""
    try:
        data = _HERE / "data"
        data.mkdir(exist_ok=True)
        with open(data / "float_startup_error.log", "a", encoding="utf-8") as fh:
            fh.write(time.strftime("%Y-%m-%d %H:%M:%S ") + message + "\n\n")
    except OSError:
        pass
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, message[:900], "Float couldn't start", 0x10)
        else:
            print(message, file=sys.stderr)
    except Exception:
        pass


def _fix_file_case() -> None:
    """Windows keeps whatever capital letters a file was saved with, but Python's
    imports are case-exact. If `Attachments.py` came through a zip or copy with a
    capital A, rename it to the name the code expects."""
    pkg = _HERE / "float"
    try:
        names = os.listdir(pkg)
        if "attachments.py" not in names and "Attachments.py" in names:
            os.rename(pkg / "Attachments.py", pkg / "attachments_tmp.py")
            os.rename(pkg / "attachments_tmp.py", pkg / "attachments.py")
    except OSError:
        pass


_fix_file_case()
try:
    from float import APP_NAME, APP_TAGLINE, VERSION
    from float import config, db, security, server
except Exception:
    _tell_user("Float's files look damaged or incomplete, so it could not start.\n\n"
               "Re-download Float and copy it over this folder.\n\nDetails:\n"
               + traceback.format_exc(limit=3))
    raise SystemExit(1)


def _open_window(url: str) -> None:
    """Open Float in its own window (no tabs, no address bar) when Edge or Chrome
    is installed, so it gets the normal minimise / maximise / close buttons.
    Falls back to a plain browser tab."""
    import os
    import shutil
    import subprocess

    if sys.platform == "win32":
        roots = [os.environ.get(k) for k in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA")]
        candidates = []
        for root in filter(None, roots):
            candidates.append(os.path.join(root, "Microsoft", "Edge", "Application", "msedge.exe"))
            candidates.append(os.path.join(root, "Google", "Chrome", "Application", "chrome.exe"))
    elif sys.platform == "darwin":
        candidates = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                      "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"]
    else:
        candidates = [shutil.which(n) for n in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge")]

    for exe in candidates:
        if exe and os.path.exists(exe):
            try:
                subprocess.Popen([exe, f"--app={url}", "--window-size=1280,820"], close_fds=True)
                return
            except OSError:
                continue
    webbrowser.open(url)


def _lan_address() -> str:
    """The address teachers on other PCs should type."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("10.255.255.255", 1))
            return probe.getsockname()[0]
    except OSError:
        return socket.gethostname()


def _cmd_run(args: argparse.Namespace) -> None:
    if getattr(args, "lan", False):
        config.settings.lan = True
        if not args.host and config.settings.host == "127.0.0.1":
            config.settings.host = "0.0.0.0"
    host = args.host or config.settings.host
    port = args.port or config.settings.port
    scheme = "https" if config.tls_files() else "http"
    shown = "127.0.0.1" if host in ("0.0.0.0", "::") else host   # where THIS computer opens it
    try:
        db.init()           # runs any pending database upgrade (after a safety backup)
    except db.MigrationError as exc:
        _tell_user(str(exc))
        raise SystemExit(1)
    try:
        srv = server.serve(host, port)
    except OSError:
        # Port already taken. Usually that's Float itself, already running: just open it.
        import ssl
        import urllib.request
        url = f"{scheme}://{shown}:{port}"
        ctx = ssl._create_unverified_context()
        try:
            alive = b"Float" in urllib.request.urlopen(url, timeout=3, context=ctx).read(4000)
        except Exception:
            alive = False
        if alive:
            if not args.no_browser:
                webbrowser.open(url) if args.tab else _open_window(url)
            return
        alt_scheme = "http" if scheme == "https" else "https"
        try:
            alt_alive = b"Float" in urllib.request.urlopen(
                f"{alt_scheme}://{shown}:{port}", timeout=3, context=ctx).read(4000)
        except Exception:
            alt_alive = False
        if alt_alive and config.settings.lan:
            _tell_user(f"Float is already running in single-computer mode on port {port}.\n\n"
                       "Close that Float window first, then start the School Server again.")
            raise SystemExit(1)
        _tell_user(f"Port {port} is being used by another program, so Float could not start.\n\n"
                   f"Close that program, or start Float with a different port:\npython main.py --port {port + 1}")
        raise SystemExit(1)
    pid_file = config.pid_path()
    try:
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        pid_file.write_text(
            json.dumps({"pid": os.getpid(), "port": srv.server_port, "host": host, "started": time.time()}, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass

    def _cleanup_pid() -> None:
        try:
            if pid_file.exists():
                pid_file.unlink(missing_ok=True)
        except OSError:
            pass

    import atexit
    atexit.register(_cleanup_pid)

    url = f"{scheme}://{shown}:{srv.server_port}"

    print(f"{APP_NAME} {VERSION} — {APP_TAGLINE}")
    print(f"Running at {url}")
    if config.settings.lan:
        print(f"School server: teachers on other PCs open {scheme}://{_lan_address()}:{srv.server_port}")
        if scheme == "http":
            print("WARNING: no HTTPS configured - passwords cross the network unencrypted. See docs/SCHOOL_SERVER.md")
    print("Close this window, or press Ctrl+C, to sign everyone out and stop Float.")

    if not args.no_browser:
        time.sleep(0.35)
        if args.tab:
            webbrowser.open(url)
        else:
            _open_window(url)

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nStopping Float.")


def _cmd_set_password(args: argparse.Namespace) -> None:
    config.ensure_dirs()
    db.init()
    email = (args.email or "").strip().lower()
    user = db.get_user_by_email(email)
    if user is None:
        print(f"No account for {args.email}.", file=sys.stderr)
        raise SystemExit(1)
    password = args.password or security.new_token(10)
    problems = security.password_problems(password)
    if problems:
        print(" ".join(problems), file=sys.stderr)
        raise SystemExit(1)
    db.set_password(int(user["id"]), password)
    db.update_user(int(user["id"]), must_change=1)
    db.end_all_sessions(int(user["id"]))
    print(f"New password for {args.email}: {password}")
    print("They'll be asked to set their own on next sign-in.")


def _cmd_make_admin(args: argparse.Namespace) -> None:
    config.ensure_dirs()
    db.init()
    email = (args.email or "").strip().lower()
    user = db.get_user_by_email(email)
    if user is None:
        print(f"No account for {args.email}.", file=sys.stderr)
        raise SystemExit(1)
    db.update_user(int(user["id"]), role="admin")
    print(f"{args.email} is now an admin.")


def _cmd_restore(args: argparse.Namespace) -> None:
    """python main.py restore            -> list backups
       python main.py restore <file>     -> put that backup back (Float must be closed)"""
    from float import maintenance

    backups = maintenance.list_backups()
    if not args.file:
        if not backups:
            print("There are no backups yet in", maintenance.backup_dir())
            return
        print("Backups (newest first). To restore one, CLOSE Float and run:")
        print("  python main.py restore <file name>\n")
        for p in backups:
            print("  ", p.name)
        return
    chosen = Path(args.file)
    if not chosen.exists():
        chosen = maintenance.backup_dir() / args.file
    if not chosen.exists():
        print(f"Could not find {args.file}. Run 'python main.py restore' to see the list.", file=sys.stderr)
        raise SystemExit(1)
    try:
        kept = maintenance.restore(chosen)
    except Exception as exc:  # noqa: BLE001
        print(f"Restore did not work, and your current data was left alone: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Restored {chosen.name}. Your previous data was kept as {kept.name}. Start Float again.")


def _is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            if handle:
                code = ctypes.c_ulong()
                kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
                kernel32.CloseHandle(handle)
                return code.value == 259  # STILL_ACTIVE
            return False
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def _kill_pid(pid: int) -> None:
    if sys.platform == "win32":
        import subprocess
        subprocess.run(["taskkill", "/PID", str(pid), "/F", "/T"],
                       capture_output=True, text=True)
    else:
        import signal
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            if _is_pid_running(pid):
                os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def _stop_windows_process_by_port(port: int) -> bool:
    import subprocess
    try:
        res = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True, timeout=5)
        for line in res.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5 and parts[3] == "LISTENING":
                local_addr = parts[1]
                if local_addr.endswith(f":{port}"):
                    pid = int(parts[4])
                    if pid > 0 and pid != os.getpid():
                        _kill_pid(pid)
                        return True
    except Exception:
        pass
    return False


def _cmd_stop(args: argparse.Namespace) -> None:
    pid_file = config.pid_path()
    pid_data = {}
    if pid_file.exists():
        try:
            pid_data = json.loads(pid_file.read_text(encoding="utf-8"))
        except Exception:
            pid_data = {}

    target_pid = pid_data.get("pid")
    port = getattr(args, "port", None) or pid_data.get("port") or config.settings.port
    host = getattr(args, "host", None) or "127.0.0.1"
    force = getattr(args, "force", False)

    stopped = False

    # 1. Graceful HTTP shutdown request
    scheme = "https" if config.tls_files() else "http"
    shutdown_url = f"{scheme}://{host}:{port}/api/system/shutdown"
    import ssl, urllib.request, urllib.error
    ctx = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(
            shutdown_url,
            data=b"{}",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=3, context=ctx) as resp:
            if resp.status == 200:
                stopped = True
    except Exception:
        pass

    # 2. Check if process is still running and wait
    if target_pid:
        start_wait = time.time()
        while time.time() - start_wait < 3.0:
            if not _is_pid_running(target_pid):
                stopped = True
                break
            time.sleep(0.2)

        if _is_pid_running(target_pid) and force:
            _kill_pid(target_pid)
            stopped = True

    # 3. On Windows, if still not stopped, try port-based process termination
    if not stopped and force and sys.platform == "win32":
        stopped = _stop_windows_process_by_port(port)

    # 4. Clean up PID file
    try:
        if pid_file.exists():
            pid_file.unlink(missing_ok=True)
    except OSError:
        pass

    if stopped:
        print(f"Float server on port {port} has been stopped.")
    else:
        print(f"Float does not appear to be running on port {port}.")


_KNOWN_COMMANDS = {"run", "stop", "set-password", "make-admin", "restore"}


def main() -> None:
    parser = argparse.ArgumentParser(prog="float", description=__doc__.split("\n\n")[0])
    parser.add_argument("--version", action="version", version=f"{APP_NAME} {VERSION}")
    sub = parser.add_subparsers(dest="command")

    run_p = sub.add_parser("run", help="Start Float (the default).")
    run_p.add_argument("--host", default=None)
    run_p.add_argument("--port", type=int, default=None)
    run_p.add_argument("--no-browser", action="store_true")
    run_p.add_argument("--lan", action="store_true", help="School-server mode: let other PCs on the network use this Float.")
    run_p.add_argument("--tab", action="store_true", help="Open in a normal browser tab instead of an app window.")
    run_p.set_defaults(func=_cmd_run)

    pass_p = sub.add_parser("set-password", help="Reset a teacher's password from the terminal.")
    pass_p.add_argument("email")
    pass_p.add_argument("--password", default=None, help="Omit to generate one.")
    pass_p.set_defaults(func=_cmd_set_password)

    admin_p = sub.add_parser("make-admin", help="Promote an existing account to admin.")
    admin_p.add_argument("email")
    admin_p.set_defaults(func=_cmd_make_admin)

    rest_p = sub.add_parser("restore", help="List backups, or restore one (close Float first).")
    rest_p.add_argument("file", nargs="?", default=None)
    rest_p.set_defaults(func=_cmd_restore)

    stop_p = sub.add_parser("stop", help="Stop a running Float server.")
    stop_p.add_argument("--port", type=int, default=None, help="Port to stop (defaults to active port or 8766).")
    stop_p.add_argument("--host", default="127.0.0.1", help="Host address (defaults to 127.0.0.1).")
    stop_p.add_argument("--force", "-f", action="store_true", help="Force terminate process if it does not exit promptly.")
    stop_p.set_defaults(func=_cmd_stop)

    # `python main.py [--host ...] [--port ...] [--no-browser]` with no
    # subcommand named should just start Float — that's the common case a
    # teacher or admin actually types.
    raw = sys.argv[1:]
    if not raw or raw[0] not in _KNOWN_COMMANDS:
        args = run_p.parse_args(raw)
        args.func = _cmd_run
    else:
        args = parser.parse_args(raw)

    args.func(args)


def _report_crash() -> None:
    """When launched invisibly (pythonw), a crash would vanish without a trace.
    Save the traceback next to main.py and, on Windows, show a popup."""
    import traceback
    from pathlib import Path

    text = traceback.format_exc()
    log = Path(__file__).resolve().parent / "float_error.log"
    try:
        log.write_text(text, encoding="utf-8")
    except OSError:
        pass
    sys.stderr = sys.stderr or sys.__stderr__
    if sys.stderr:
        print(text, file=sys.stderr)
    if sys.platform == "win32":
        try:
            import ctypes

            last = text.strip().splitlines()[-1][:300]
            ctypes.windll.user32.MessageBoxW(
                0,
                f"Float couldn't start.\n\n{last}\n\nFull details saved to:\n{log}",
                "Float",
                0x10,
            )
        except Exception:
            pass


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException:
        _report_crash()
        raise SystemExit(1)
