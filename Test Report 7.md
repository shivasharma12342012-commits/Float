# Float — Test Report 7 (Reliability pass)

- **Date:** 6 October 2026
- **Method:** Run with AI assistance (Claude). Results are from commands actually run: the unit suite, and a check that each new test fails when its bug is put back.
- **Environment:** Linux sandbox, Python 3.12, standard library only, loopback only, no AI provider key.

## What was found and changed

| # | Problem | Change |
|---|---|---|
| 1 | The zip still contained `float/Attachments.py` (capital A) while the code imports `attachments`. Only 13 of 26 tests could run off Windows. | Renamed to `attachments.py`; a test now checks every internal import against the real file name. |
| 2 | A temporary password kept full access until changed. Only the browser asked for a new one, and a page reload skipped it. | The server now allows only: load the app, change password, sign out. Everything else returns 403 with a plain message. The browser reads `must_change` from the server, so a reload no longer skips it. |
| 3 | Session tokens were accepted in the URL (`?token=`), where they can land in history and logs. The app never used this. | Removed. Tokens are read from the `Authorization` header only. |
| 4 | An unexpected server error showed the raw exception text to the operator, and with no console window the error vanished (and logging itself could fail when there is no stderr). | Operator sees a calm message with a short reference. The real traceback goes to `data/float_errors.log` (size-capped). Logging can no longer raise. |
| 5 | When Float was not reachable (window closed, laptop asleep) operators saw "Failed to fetch". | One plain sentence in the app, admin panel and sign-in page. |
| 6 | The Download button saved an error response as if it were the document (a corrupt file). | It checks the response first and shows a message if it failed. |
| 7 | If the app failed to start, the screen had nothing to click. | Added a "Try again" button. |
| 8 | Unhandled errors in the page failed silently. | One safety net shows a friendly message. |
| 9 | Admin panel said "Admins only" to an admin on a temporary password. | Now says to set a password first. |

## New tests (7)

Import names match file names exactly; every element id `app.js` looks up exists in `index.html`; every `/api/...` path the front end calls has a server route; token in URL is refused; temporary password is limited, then unlocked by a real one; an unexpected crash is calm, logged, leaks nothing and the server stays healthy; logging never raises.

## Results

| Run | Result |
|---|---|
| Unit tests (`python -m unittest discover -s tests`) | **33 / 33 pass** (26 existing + 7 new) |
| Each new test with its bug put back | **Fails, as it should** (4 of 4 mutations checked) |

## NOT tested

- A real browser (layout, colours, the new messages as they look on screen).
- Windows launchers (`.bat`, `.vbs`) and window mode.
- Real AI answers, "use the computer", Google sign-in and Drive.
- The live 65-check run from earlier reports was not repeated.
