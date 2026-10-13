# Float — Test Report 8 (Final readiness check)

- **Date:** 13 October 2026
- **Method:** Run with AI assistance (Claude). Everything marked "run" was actually executed in this session. Anything not run is listed under "NOT tested" — it is unknown, not passed.
- **Environment:** Linux sandbox, Python 3.12, loopback only, temporary data folder, no AI provider key, no browser, no Windows.

## What changed since Report 7

| Change | Files |
|---|---|
| New opening screen showing the Float logo (`float.ico`), once per app open, 1.2 s minimum, auto-hides after 8 s at most | `float/web/splash.js` (new), `index.html`, `login.html`, `admin.html` |
| Server now serves `/float.ico` from the project root; browser tab icon is now the Float logo | `float/server.py` |
| Removed an unused import and an unused variable | `float/server.py` |

## Results (run)

| Check | Result |
|---|---|
| All test files (`python -m unittest discover -s tests -p "*.py"`) | **65 / 65 pass** |
| Code check (pyflakes) on `server.py`, JS syntax check on `splash.js` | Clean |
| Pages `/`, `/login`, `/admin` load and each contains the splash script | **Pass** |
| `/float.ico` is served as a real ICO file | **Pass** |
| Path-traversal attempts (`/../main.py`, `/%2e%2e/main.py`) | **Blocked (404)** |
| Soak: 8 parallel clients × 300 requests (2,400) | **0 errors, 2.3 s** |

Note: the tests only ran after I copied `Attachments.py` to `attachments.py`. See problem 1 below.

## Problems found

| # | Problem | Severity for a paying teacher |
|---|---|---|
| 1 | **The zip contains `float/Attachments.py` (capital A) again.** Report 7 fixed this, but it has come back. Windows is saved by a runtime rename in `main.py`, but any copy that skips that step fails to start. | Medium. Rename the file to `attachments.py`. |
| 2 | **No backup.** Accounts, classes, marks and chat history live in one `data/float.sqlite3` file. A deleted folder, a disk fault or a reinstall loses everything. | **High** |
| 3 | **No database upgrade path.** There is no schema version or migration code. A future update that changes a table can break an existing teacher's data. | **High** (for the first update you ship) |
| 4 | **Usage and audit records are never pruned.** The database grows without limit. For one school this is slow, not sudden, but nothing manages it. | Low–Medium |
| 5 | **Class statistics (average, standard deviation, "more than one SD below") are worked out by the AI, not by code.** A model can give a wrong number with full confidence. | **High** if a teacher reports these marks to parents |
| 6 | **Cost figures depend on a price table in `config.py`.** If providers change prices, the rupee estimates and monthly limits become wrong until someone edits the table. | Medium |

## NOT tested (unknown)

- **A real browser:** the new loading screen has never been seen on a screen. Layout, animation and dark mode are untested.
- **Windows:** `Start Float.bat`, `Start Float.vbs`, app-window mode, the hidden runtime.
- **Real AI answers** with a real API key: quality, errors, rate limits, long answers, all 19 toolkit tools.
- **"Use the computer"** (mouse and keyboard control) on a real desktop. This feature can click things in the wrong place, and it is the highest-risk feature in the app.
- **Google sign-in, Drive, Calendar, Gmail.**
- **Real long use:** weeks or months of daily use, thousands of chats, a database of many megabytes, several teachers at once on different machines.
- **Different computers:** slow laptops, small screens, antivirus software blocking the app, Hindi and other Indic text in documents.

## Verdict: is Float ready to sell, with no bugs in long-term use?

**No. I cannot honestly say that, and nobody could for any software.**

What I can say:

- **Sound foundation:** 65 of 65 tests pass, the server handled 2,400 parallel requests with no errors, and security basics (passwords, sessions, path traversal, temporary passwords) held up in every check I ran.
- **Not proven in real use:** the things a teacher touches every day (a real browser, real AI answers, Windows, Google, computer control) have not been tested in this report. A paying customer would be the first to test them.
- **Two problems would hurt a teacher in the long run:** no backup (problem 2) and no safe update path (problem 3). A teacher losing a year of marks and classes is the kind of failure that ends a sale and a reputation.

**Recommendation:** do not sell it as finished yet. It is ready for a **small, free or discounted pilot with 2–3 friendly teachers**, with a warning that it is early software, and with you taking a copy of their `data/` folder weekly. Before charging general customers, do these in order:

1. Rename `Attachments.py` to `attachments.py` (problem 1).
2. Add an automatic backup of `data/float.sqlite3` (problem 2).
3. Add a database version number and upgrade steps (problem 3).
4. Compute average and standard deviation in Python and give the results to the AI (problem 5).
5. Test on a real Windows PC, in a real browser, with a real API key, for at least two weeks of daily use, and write Report 9 from what happens.
