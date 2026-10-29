# Float — Test Report 6 (New Opening Screen + Regression)

- **Date:** 4 October 2026
- **Method:** Run with AI assistance (Claude). Every result below comes from commands actually run: the 26 unit tests, a script that started the real server and made 52 live requests (a principal and two operators), and a simulated-browser run (jsdom) of the new home screen's code.
- **Environment:** Linux sandbox, Python 3.12, standard library only, fresh empty database, loopback only, **no AI provider key** (no real AI answers were generated).
- **What was new:** the redesigned opening screen (top-left icons, Claude-style colours, new composer, Drive/Calendar/Gmail starters, menus, dictation, back/forward, app-window launcher). The rest was re-tested to make sure nothing broke.

## 1. Headline

| Item | Result |
|---|---|
| Live checks (pages, login, privacy, marks, tasks, chat, security, speed) | **51 of 52 pass.** The 1 miss is Gap 2 below. |
| Unit tests | 13 of 26 run on the zip as uploaded (the Linux-only name problem, Gap 1). **26 of 26 pass** with the file name lowercased. |
| New home-screen code in a simulated browser | **Loads with 0 script errors.** Greeting, model label, sidebar toggle, both menus and the starters all worked. |
| Every element id used by `app.js` exists in `index.html` | **Yes, none missing**, no duplicate ids. |
| JS syntax (`app.js`, `login.js`, `admin.js`) and `main.py` | **All clean.** |
| Server errors / tracebacks | **0** |
| Another operator could read, change or delete data | **No.** Reads and writes were refused. |
| Report 5 bug (deleting someone else's class/task returned "ok") | **Fixed.** It now returns 404 and the data is untouched. |

## 2. Bugs and gaps found

| # | Problem | Severity | Suggested fix |
|---|---|---|---|
| 1 | `float/Attachments.py` is imported as `attachments`. Fails on Linux/macOS, hidden on Windows. Carried over from Reports 4 and 5. | Low for you (Windows only) | Rename the file to `attachments.py` |
| 2 | **No limit on the length of text fields (fixed, see section 7).** A class name of 3 MB was accepted and stored. Only the overall upload cap (45 MB) applies, and a 50 MB request is correctly refused. | Low | Cap names/titles at around 200 characters in `classes_add`, `tasks_add`, and the profile route |
| 3 | The Drive / Calendar / Gmail chips only start a sentence. Float cannot read Drive, Calendar or Gmail (it can only save files to Drive), so the answer depends on computer control. | Medium (expectation gap) | Build real Google read access, or relabel the chips until then |

No crashes, wrong data, or security holes were found in the new screen's server side.

## 3. New opening screen: what was checked

| Check | Result |
|---|---|
| Home page contains: menu, sidebar toggle, back, forward, + button, model label, mic, 3 starters | Pass |
| Home page contains none of the crossed-out items (sparkle logo, Free plan / Upgrade, Write, Learn, waveform) | Pass |
| Greeting comes from the server (about 12 ms) and respects language (Hindi greeting returned after switching) | Pass |
| Sidebar starts folded and the toggle opens it | Pass |
| Top-left menu lists: New conversation, Toolkit, Classes, To do, Files, Settings, light/dark, Admin (admin only), Sign out | Pass |
| + menu lists: Add a photo or file, Open the toolkit | Pass |
| Clicking a starter fills the box and shows the send button | Pass |
| Back and forward start greyed out | Pass |
| Theme and language change through `/api/me` | Pass |

## 4. Regression results (live)

| Area | Result |
|---|---|
| Pages `/`, `/app.css`, `/app.js`, `/login`, `/admin` served | Pass |
| First account becomes admin; open sign-up blocked afterwards; bad email rejected | Pass |
| Admin adds operators; operators sign in; wrong password gives 401 | Pass |
| No token / garbage token give 401; operators refused on admin routes | Pass |
| Class with roster; marks saved; marks above max, negative, NaN, and max 0 all rejected | Pass |
| Second operator cannot read the roster, write marks, or delete the class or task (404, data intact) | Pass |
| Empty class name rejected; malformed JSON gives 400, not 500 | Pass |
| Chat with no key fails politely with no traceback; chat without login blocked | Pass |
| Path traversal (two forms) blocked; server source files not served | Pass |
| SQL-style and script-style text stored harmlessly | Pass |
| 12 rapid wrong sign-ins hit the rate limit (429 from the 8th) | Pass |
| Sign out ends the session | Pass |
| Speed: 20 `bootstrap` calls averaged 44 ms | Pass |

## 5. What was NOT tested

- **Real browser appearance.** I could not open Edge or Chrome here, so colours, spacing, fonts and the dark/light look are unverified. Please eyeball the home screen once.
- The `--app` window launcher (needs Windows with Edge or Chrome), and the mic (needs browser speech recognition and microphone permission).
- Real AI answers, "use the computer" control, Google sign-in and Drive save (no key or Google client was available).
- Phone-sized layouts, and the admin panel visually.

## 6. Verdict

The new opening screen loads cleanly, its buttons work, and nothing from earlier reports regressed. There are no serious bugs. Two minor gaps (field length limits, the Linux file name) and one expectation gap (the three starter chips) remain. The next step is to look at the screen in your own window and send me anything that looks off.

## 7. Re-test after fixes (same day)

| Gap | What was changed | Re-test |
|---|---|---|
| 1. `Attachments.py` capital letter | Renamed to `float/attachments.py` | Unit tests on the real project: **26 of 26 pass** (no workaround needed) |
| 2. No limit on text length | Limits now enforced in `db.py`, so every route and AI tool is covered: class name 80, grade/section 20, subject 60, board 40, student name 120, roll 20, notes 500, task title 300, due 40, timetable label 80 / room 40, user name 120, email 254, school 160. At most 500 students and 80 timetable rows per request. `server.py` also tells the operator plainly when a class name is over 80 characters. | 3 MB class name refused (400); 81 characters refused, 80 accepted; roster of 700 stores 500; a 5,000-character task title is trimmed to 300 |
| 3. Drive/Calendar/Gmail chips | Prompts now say "Using my computer, open my Google …". If computer control is off, the chip shows an explanation instead of filling the box. | Code checked; behaviour needs a real window with computer control on |

**Live checks after the fixes: 55 of 55 pass** (the 52 from before plus 3 new ones for the limits). No server errors.
