"""Float — keeping the database healthy: backups, restore, pruning, error log.

Everything here is best-effort and must never stop Float from starting, except
the backup taken just before a database upgrade (see ``db.init``).
"""

from __future__ import annotations

import datetime as dt
import shutil
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any

from . import config

KEEP_BACKUPS = 14
AUDIT_MONTHS = 12
USAGE_MONTHS = 24
BATCH = 500

_backup_lock = threading.Lock()


def error_log_path() -> Path:
    return config.DATA_DIR / "float_errors.log"


def log_error(text: str) -> None:
    try:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(error_log_path(), "a", encoding="utf-8") as fh:
            fh.write(f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {text}\n")
    except OSError:
        pass


def backup_dir() -> Path:
    return config.DATA_DIR / "backups"


def list_backups() -> list[Path]:
    """Newest first."""
    try:
        files = [p for p in backup_dir().glob("float-*.sqlite3") if p.is_file()]
    except OSError:
        return []
    return sorted(files, key=lambda p: (p.stat().st_mtime, p.name), reverse=True)


def backup_now(tag: str = "") -> Path:
    """Copy the live database with SQLite's backup API (safe while Float is running).

    Written to a temporary name, checked, then renamed, so a half-written file is
    never mistaken for a good backup. Raises on failure; callers decide what that means.
    """
    with _backup_lock:
        src_path = Path(config.DB_PATH)
        if not src_path.exists():
            raise FileNotFoundError("There is no database to back up yet.")
        backup_dir().mkdir(parents=True, exist_ok=True)
        clean_tag = "".join(c for c in (tag or "") if c.isalnum() or c in "-_")[:24]
        name = f"float-{dt.date.today():%Y-%m-%d}{('-' + clean_tag) if clean_tag else ''}.sqlite3"
        final = backup_dir() / name
        tmp = backup_dir() / (name + ".part")
        tmp.unlink(missing_ok=True)
        src = sqlite3.connect(src_path, timeout=15)
        dst = sqlite3.connect(tmp)
        try:
            src.backup(dst)
            ok = dst.execute("PRAGMA quick_check").fetchone()[0] == "ok"
        finally:
            dst.close()
            src.close()
        if not ok:
            tmp.unlink(missing_ok=True)
            raise sqlite3.DatabaseError("The new backup failed its own integrity check, so it was discarded.")
        tmp.replace(final)
        _trim_backups()
        return final


def _trim_backups() -> None:
    for old in list_backups()[KEEP_BACKUPS:]:
        try:
            old.unlink()
        except OSError:
            pass


def safe_backup(tag: str = "") -> Path | None:
    """Like ``backup_now`` but logs instead of raising."""
    try:
        return backup_now(tag)
    except Exception as exc:  # noqa: BLE001 - a backup problem must never stop Float
        log_error(f"Backup failed: {exc!r}")
        return None


def last_backup() -> dict[str, Any]:
    files = list_backups()
    if not files:
        return {"last": "", "count": 0}
    stamp = dt.datetime.fromtimestamp(files[0].stat().st_mtime)
    return {"last": f"{stamp:%d %b %Y, %H:%M}", "count": len(files), "file": files[0].name}


def start_daily_backups(check_every: int = 3600) -> None:
    """One backup now, then at most one per calendar day while Float stays open."""
    def loop() -> None:
        last_day = None
        while True:
            today = dt.date.today()
            if today != last_day:
                if safe_backup() is not None:
                    last_day = today
            time.sleep(check_every)

    threading.Thread(target=loop, daemon=True, name="float-backup").start()


def restore(source: Path) -> Path:
    """Replace the live database with a backup. Float must be closed.

    The current database is kept as ``float-before-restore.sqlite3`` first.
    """
    source = Path(source)
    check = sqlite3.connect(source)
    try:
        if check.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise sqlite3.DatabaseError("That backup file is damaged, so it was not used.")
    finally:
        check.close()
    live = Path(config.DB_PATH)
    kept = live.with_name("float-before-restore.sqlite3")
    if live.exists():
        shutil.copy2(live, kept)
    for ext in ("-wal", "-shm"):
        Path(str(live) + ext).unlink(missing_ok=True)
    shutil.copy2(source, live)
    return kept


# ---------------------------------------------------------------------------
# Pruning: audit 12 months, usage 24 months, in small batches.
# ---------------------------------------------------------------------------
def _months_ago(months: int) -> float:
    """Start of the calendar month `months` ago, so whole months are pruned together."""
    now = dt.datetime.now()
    idx = now.year * 12 + (now.month - 1) - months
    return dt.datetime(idx // 12, idx % 12 + 1, 1).timestamp()


def prune(connect=None, audit_months: int = AUDIT_MONTHS, usage_months: int = USAGE_MONTHS,
          batch: int = BATCH, pause: float = 0.0) -> dict[str, int]:
    """Delete old audit and usage rows. Chats, classes, marks and accounts are never touched.

    Before usage rows go, their totals are folded into ``usage_monthly`` in the same
    transaction, so cost history stays correct.
    """
    from . import db

    batch = max(1, int(batch))
    conn = (connect or db._connect)()
    removed = {"audit": 0, "usage": 0}
    try:
        cut = _months_ago(audit_months)
        while True:
            cur = conn.execute("DELETE FROM audit WHERE id IN "
                               "(SELECT id FROM audit WHERE created_at<? LIMIT ?)", (cut, batch))
            removed["audit"] += cur.rowcount
            if cur.rowcount < batch:
                break
            time.sleep(pause)
        cut = _months_ago(usage_months)
        while True:
            conn.execute("BEGIN IMMEDIATE")
            try:
                ids = [r[0] for r in conn.execute(
                    "SELECT id FROM usage WHERE created_at<? ORDER BY id LIMIT ?", (cut, batch))]
                if ids:
                    marks = ",".join("?" * len(ids))
                    conn.execute(f"""
                        INSERT INTO usage_monthly(month,user_id,provider,model,calls,tokens_in,tokens_out,paise)
                        SELECT strftime('%Y-%m',created_at,'unixepoch','localtime'),user_id,provider,model,
                               COUNT(*),SUM(tokens_in),SUM(tokens_out),SUM(paise)
                        FROM usage WHERE id IN ({marks}) GROUP BY 1,2,3,4
                        ON CONFLICT(month,user_id,provider,model) DO UPDATE SET
                          calls=calls+excluded.calls, tokens_in=tokens_in+excluded.tokens_in,
                          tokens_out=tokens_out+excluded.tokens_out, paise=paise+excluded.paise""", ids)
                    deleted = conn.execute(f"DELETE FROM usage WHERE id IN ({marks})", ids).rowcount
                else:
                    deleted = 0
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
            removed["usage"] += deleted
            if deleted < batch:      # nothing (or the last few) left; also stops a loop that can't make progress
                break
            time.sleep(pause)
    finally:
        conn.close()
    return removed


def prune_in_background() -> None:
    def run() -> None:
        try:
            prune(pause=0.05)
        except Exception as exc:  # noqa: BLE001
            log_error(f"Pruning failed: {exc!r}")

    threading.Thread(target=run, daemon=True, name="float-prune").start()
