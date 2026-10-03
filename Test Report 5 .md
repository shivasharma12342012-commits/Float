# Float — Test Report 5 (Average Teacher + New Admin Panel)

- **Date:** 3 October 2026
- **Method:** Run with AI assistance (Claude). Every result below comes from commands actually run against the live server. A script (`teacher_test.py`) played three people in order: a **principal** (admin), **Mrs. Sunita Sharma** (Class 8B Maths teacher) and **Mr. Rajesh Kumar** (a second teacher, used to check privacy between teachers).
- **Environment:** Linux sandbox, Python 3.12.3, standard library only, fresh empty database, loopback only, **no AI provider key** (so no real AI answers were generated).
- **What was new this time:** the Fairness & privacy admin work (equal monthly limits, usage bands, audited exports and exceptions) was tested together with everyday teacher tasks.

## 1. Headline

| Item | Result |
|---|---|
| Live checks (teacher + admin + security + speed) | **64 of 65 pass** on first run (the 1 flagged item was Bug 1). **65 of 65 pass** after the fixes in section 8. |
| Unit tests, zip exactly as uploaded | 13 of 26 run, **1 import error** (Linux/macOS only, see Bug 2). Not an issue on Windows. |
| Unit tests with the file name lowercased | **26 of 26 pass** |
| Server errors / tracebacks in the server log | **0** |
| Another teacher could read, change or delete Sunita's data | **No.** Reads and writes were refused, and a delete attempt left the data intact. |
| Both Report 4 bugs (NaN mark crash, impossible marks accepted) | **Fixed.** Re-tested and pass. |

## 2. Bugs and gaps found

| # | Problem | Severity | Suggested fix |
|---|---|---|---|
| 1 | A teacher deleting **another teacher's** class, task or conversation gets **HTTP 200 "ok"** even though nothing is deleted. I confirmed afterwards that the class, task and chat were all still intact. The data is safe, but the reply is wrong, and the same happens for ids that don't exist. | Low | In `classes_delete`, `tasks_delete` and the conversation delete route, check ownership first (`owns_class` already exists) and return 404 like the marks and attendance routes do |
| 2 | `float/Attachments.py` is imported as `attachments`. Fails on Linux/macOS (case-sensitive), hidden on Windows. Carried over from Report 4. | Low for you (Windows only) | Rename to lowercase if you ever move off Windows |
| 3 | The app already receives each teacher's monthly limit (`usage.cap_paise`, `usage.month_paise`) but `app.js` doesn't show it. A teacher only learns about a limit when she is stopped. | Medium for fairness | Add a small "your share this month" line next to the existing "answers / estimated" line in the app |
| 4 | The monthly limit counts only the school-key spend that Float estimates from published rates. It is a fair-share guide, not an invoice. | Info | Keep the wording "estimated" in the UI |

## 3. Teacher's day: did Float behave like a staff-room tool?

| Moment | What I did | Result |
|---|---|---|
| First login | Principal creates Sunita with a temporary password | Works. Sunita is asked to change it. "password" is refused, a proper one accepted. |
| Typing the email carelessly | `SUNITA@DPS.EDU.IN ` (capitals plus a trailing space) | Signs in fine |
| Class set-up | Paste a 45-name list (numbered `1,` and `2.` styles, two blank lines, Hindi name आर्यन गुप्ता, names with `Mohd.` and `D'Souza`) | All 45 saved; blank lines ignored; Devanagari intact |
| Marks | 45 marks out of 50, then 55/50, −5/50, 3/0, NaN, a student from another class | Good marks saved. All bad ones refused with a 400, none crashed. |
| Attendance | 4 absent, then an id outside the class | First saved, second refused |
| Tasks and timetable | Add a task, a blank task, a period | Saved; blank task refused |
| AI chat with no key | Asked for a 10-question worksheet | Calm message, no crash. Real AI answers were **not** tested. |

## 4. New admin features: fairness and privacy

| Check | Result |
|---|---|
| Equal ₹100 monthly limit set for every teacher | Works; non-numeric limit refused |
| Sunita goes over her ₹100 share | Stopped with a kind message ("resets on the 1st…") |
| Rajesh, who is under the limit, at the same moment | **Not** blocked by Sunita's use |
| Capped teacher can still open classes and marks | Yes |
| Extra limit for a head of department **without a reason** | Refused |
| Same, **with** a reason | Accepted; Sunita unblocked; reason appears in the audit log |
| Admin list order | Alphabetical, no ranking |
| Default admin view | Usage **bands** only; exact calls, tokens and ₹ are hidden |
| Admin data contains class names, marks, chat text | **No** |
| Usage export (.xlsx) | Opens correctly, contains **no email addresses**; the download is logged |
| Teacher calling admin routes (overview, audit, export, make-admin, school settings) | All blocked with 403 |
| "Exact numbers" mode | Works when the admin chooses it; invalid mode refused |

## 5. Security and speed

- **Sign-in guessing:** 12 wrong passwords in a row led to rate-limiting (HTTP 429).
- **Sessions:** a token stops working after sign-out; a deactivated teacher is thrown out immediately; a forged token gets 401.
- **Odd input:** a 3 MB message did not crash the server; an SQL-style class name was harmless; path-traversal URLs returned 404.
- **Screen safety (code read, not clicked):** the admin table escapes names and emails. I created a teacher named `<img onerror=…>` and the server stored it as plain text. The browser display of that name was **not** checked by eye.
- **Speed:** 300 requests from 30 simultaneous users: 0 errors; median 11 ms, p95 1032 ms, max 1445 ms.

## 6. All 65 live checks

| Area | Check | Result | Detail |
|---|---|---|---|
| Setup | weak password 12345678 rejected | ✅ Pass | 400 |
| Setup | first account created (becomes admin) | ✅ Pass | 200 |
| Privacy | random person cannot self-sign-up when off | ✅ Pass | 403 |
| Admin | add teacher Sunita Sharm | ✅ Pass | 200 |
| Admin | add teacher Rajesh Kumar | ✅ Pass | 200 |
| Admin | add teacher <img src=x o | ✅ Pass | 200 |
| Admin | duplicate teacher email rejected | ✅ Pass | 409 |
| Teacher | signs in with temporary password | ✅ Pass | 200 |
| Teacher | asked to change password (must_change) | ✅ Pass | True |
| Teacher | 'password' as new password rejected | ✅ Pass | 400 |
| Teacher | sets own strong password | ✅ Pass | 200 |
| Teacher | signs in with new password | ✅ Pass | 200 |
| Teacher | email in CAPS with space still works | ✅ Pass | 200 |
| Class | create 8B with pasted 45-name roster | ✅ Pass | 200 students=45 |
| Class | Hindi (Devanagari) name stored intact | ✅ Pass | 45 |
| Class | blank lines in roster ignored | ✅ Pass | 45 |
| Class | empty class name gives friendly 400 | ✅ Pass | Give the class a name, like '8B'. |
| Marks | save 45 marks out of 50 | ✅ Pass | 200 |
| Marks | impossible mark rejected: 55 out of 50 | ✅ Pass | HTTP 400 |
| Marks | impossible mark rejected: -5 out of 50 | ✅ Pass | HTTP 400 |
| Marks | impossible mark rejected: 3 out of 0 | ✅ Pass | HTTP 400 |
| Marks | NaN mark does not crash (no 500) | ✅ Pass | HTTP 400 |
| Marks | mark for student not in class rejected | ✅ Pass | 400 |
| Attendance | save attendance (4 absent) | ✅ Pass | 200 |
| Attendance | absent id outside class rejected | ✅ Pass | 400 |
| Tasks | add task | ✅ Pass | 200 |
| Tasks | blank task rejected | ✅ Pass | 400 |
| Timetable | save a period | ✅ Pass | 200 |
| AI chat | no API key: calm, readable message (no crash) | ✅ Pass | HTTP 200: b'data: {"type": "start", "conv_id": 1, "title": "Make a 10- |
| Privacy | Rajesh cannot read Sunita's class list | ✅ Pass | 404 |
| Privacy | Rajesh cannot write marks to Sunita's class | ✅ Pass | 404 |
| Privacy | Rajesh cannot delete Sunita's class | ⚠️ Flagged (see Bug 1) | 200 |
| Privacy | Rajesh's class list does not include 8B | ✅ Pass | 0 |
| Privacy | teacher blocked from /api/admin/overview | ✅ Pass | 403 |
| Privacy | teacher blocked from /api/admin/audit | ✅ Pass | 403 |
| Privacy | teacher blocked from /api/admin/export | ✅ Pass | 403 |
| Privacy | teacher cannot promote self to admin | ✅ Pass | 403 |
| Privacy | teacher cannot change school settings | ✅ Pass | 403 |
| Privacy | no token -> 401 | ✅ Pass | 401 |
| Privacy | forged token -> 401 | ✅ Pass | 401 |
| Privacy | admin list is alphabetical (no ranking) | ✅ Pass | ['<img src', 'Mrs. Mee', 'Rajesh K', 'Sunita S'] |
| Privacy | default view shows bands, hides exact numbers | ✅ Pass | {'id': 4, 'name': '<img src=x onerror=alert(1)>', 'email': 'x@dps.edu. |
| Privacy | no chat/class/marks content in admin payload | ✅ Pass |  |
| Fairness | fairness block present (aggregate only) | ✅ Pass | {'accounts': 4, 'not_started': 3, 'top_fifth_share': 0, 'near_cap': 0, |
| Privacy | export opens as xlsx, has no email addresses | ✅ Pass | 2571 |
| Privacy | export download is logged in audit | ✅ Pass | ['admin.export', 'chat.error', 'auth.signin', 'auth.signin', 'auth.sig |
| Equity | non-numeric cap rejected | ✅ Pass | 400 |
| Equity | set equal cap ₹100 for all teachers | ✅ Pass | 200 |
| Equity | Sunita over her ₹100 share is stopped kindly | ✅ Pass | 429 You've used your share of the school's AI budget for this month. I |
| Equity | Rajesh (under cap) is NOT blocked by Sunita's use | ✅ Pass | 200 |
| Equity | teacher can still open classes/marks when capped | ✅ Pass | 200 |
| Equity | extra limit WITHOUT a reason refused | ✅ Pass | 400 |
| Equity | extra limit with reason accepted | ✅ Pass | 200 |
| Equity | Sunita unblocked after approved exception | ✅ Pass | 200 |
| Equity | exception + reason visible in audit log | ✅ Pass |  |
| Equity | teacher is told their own limit (cap_paise in app data) | ✅ Pass | {'tin': 1, 'tout': 1, 'paise': 12000.0, 'calls': 3, 'month_paise': 120 |
| Security | 12 wrong passwords -> rate-limited (429) | ✅ Pass | [401, 401, 401, 401, 401, 401, 401, 429, 429, 429, 429, 429] |
| Security | token dead after sign-out | ✅ Pass | 401 |
| Security | deactivated teacher kicked out immediately | ✅ Pass | 401 |
| Security | 3 MB message does not crash server | ✅ Pass | HTTP 200 |
| Security | SQL-injection style class name harmless | ✅ Pass | 200 |
| Admin | invalid usage_detail rejected | ✅ Pass | 400 |
| Admin | 'exact' mode shows real numbers when admin chooses | ✅ Pass |  |
| Speed | 300 requests / 30 parallel users: 0 errors | ✅ Pass | errors=0 |
| Speed | slowest request under 2 s | ✅ Pass | median 11 ms, p95 1032 ms, max 1445 ms |

Checks per area: 

| Area | Checks | Passed |
|---|---|---|
| Setup | 2 | 2 |
| Privacy | 17 | 16 |
| Admin | 6 | 6 |
| Teacher | 6 | 6 |
| Class | 4 | 4 |
| Marks | 6 | 6 |
| Attendance | 2 | 2 |
| Tasks | 2 | 2 |
| Timetable | 1 | 1 |
| AI chat | 1 | 1 |
| Fairness | 1 | 1 |
| Equity | 10 | 10 |
| Security | 5 | 5 |
| Speed | 2 | 2 |

## 7. What was NOT tested

- Real AI answers (worksheets, lesson plans, reports): no API key was used, so quality, cost estimates and the over-limit behaviour with real spending are untested. The limit was triggered with an inserted usage record.
- The Windows launcher (`Start Float.bat` / `.vbs`), tray behaviour and the "use the computer" tool, since this ran on Linux.
- Google sign-in, PIN sign-in, saving a teacher's own API key (own-key teachers should be exempt from limits, tested in code only).
- Looking at the screens in a browser: layout on a school laptop, the new Fairness & privacy tab's appearance, Hindi text rendering on screen.
- Generated files (Word, PDF, Excel worksheets) and attaching a PDF to a chat.

## 7b. Verdict

For an everyday teacher workflow, Float held up. Nothing crashed, nobody could see another teacher's classes, and the admin panel exposes accounts and bands, not what teachers write. Fix Bug 1 (small) and show teachers their own limit (Bug 3) before a school-wide rollout.

## 8. Re-test after fixes (same day)

| Bug | Fix | Re-test result |
|---|---|---|
| 1. Deleting or editing someone else's class, task or chat said "ok" | `server.py` now checks ownership first and returns 404 (class delete, task edit, task delete, chat delete) | Other teacher: all four return **404**. The owner's own delete and edit still return **200**. |
| 3. Teacher could not see their own monthly limit | `app.js` Settings now shows "Your share this month: ₹X of ₹Y (Z%)", a progress bar, an early warning at 80%, and a note that their own API key is never counted | Data reaches the app (`cap_paise: 10000` confirmed). JavaScript passes a syntax check. **Not yet looked at in a browser.** |

Full re-run: **65 of 65** live checks pass, **26 of 26** unit tests pass, 0 tracebacks in the server log. Bug 2 (`Attachments.py` case) is unchanged because it only affects Linux/macOS.
