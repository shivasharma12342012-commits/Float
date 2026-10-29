# Float – Test Report 3

- **Date:** 2026-10-02
- **Done with AI assistance** (Claude). Results below are from commands actually run in this session.
- **Environment:** Linux sandbox, Python 3.12.3, stdlib only, temporary `FLOAT_DATA_DIR` and `HOME` per run, server started with `serve("127.0.0.1", 0)`. Any non-loopback connection was blocked by the tests; the AI provider was a stub. No real network calls were made.

## What was tested
1. Admin routes: overview, add / deactivate / activate / reset password / change role, org settings, notice, audit, export; 403 for a operator (and 401 when signed out) on every admin route.
2. Artifacts: list, download, save to (temporary) Desktop, wrong owner, `../../etc/passwd` as a file name, tampered stored path.
3. Toolkit and conversations: create, read, rename, delete; operator B cannot read, rename or delete operator A's conversation or post into it.
4. API keys: add, list, delete; plaintext key searched for in every endpoint response and every file in the data folder; org-key replacement.
5. Password change, PIN set / sign-in / removal, admin-created users (`must_change`).
6. `web/*.html` references, `/api/...` strings in the JS against the route table, `node --check` on JS.
7. Static traversal: 16 variants (`..`, `%2e%2e`, `%5c`, double-encoded, `%00`, `//etc/passwd`, …).
8. Chat with a stub provider: text, one tool call, second round, SSE frames, saved messages, provider error, cross-user conv_id.
9. 5-minute mixed load, 8 threads (`tests/stress_float.py`).
10. HTTP layer: bad / huge Content-Length, oversized body, wrong Host, bad JSON, 70 KB request line and header, garbage bytes, stalled client, session expiry and idle timeout, sign-in rate limit.

## Results
| Run | Tests | Result |
|---|---|---|
| Baseline (original code, `tests/test_float.py`) | 25 | 25 pass |
| New tests on original code (first run, output was truncated) | 20 new | several failed (see bugs); two of those were mistakes in my own tests and were corrected |
| Final run 1 (`python -m unittest discover -s tests`) | 45 | **45 pass, 0 fail** |
| Final run 2 | 45 | **45 pass, 0 fail** |
| Stress, 300 s, 8 threads, signin/signout/chat/CRUD/static/bad requests | 24,195 requests | 200: 20,188 · 404: 3,287 · 403: 662 · 429: 58 · **5xx: 0** · transport errors: 0 · "database is locked": 0 · server tracebacks: 0 · threads 3 → 2 after stop |

Stress memory samples (RSS, MB, every 30 s): 184, 163, 197, 154, 154, 168, 143, 131, 224, 197. It moves up and down with no steady climb, but five minutes cannot rule out a slow leak.
The stress run was made before the last one-line fix (notice `retire`); the unit suite was run twice after it.

## Bugs fixed
| Bug | File | Fix |
|---|---|---|
| Non-numeric or huge IDs in URLs (`/api/conversations/abc`) gave 500 | float/server.py | `*_id` route params match digits only, so they return 404 |
| Toolkit run with non-object `values` gave 500 | float/server.py | Non-dict treated as empty |
| Admin add user: unknown role gave 500 (DB constraint); admin-typed weak password accepted | float/server.py | Validate role and password |
| Saving the school (org) key twice created duplicate rows (SQL UNIQUE ignores NULL), so a rotated key might not take effect | float/db.py | Delete old org row on save; read newest |
| `%00` in a static path gave 500; folder check used a string prefix | float/server.py, float/artifacts.py | 404 for NUL; `is_relative_to` |
| `Content-Length: abc` gave 500; oversize body left unread on a kept-alive connection | float/server.py | 400 and close the connection |
| No socket timeout: a stalled client held a server thread forever | float/server.py | `timeout = 30` (verified: stalled connection is closed) |
| Tampered artifact path gave 500 | float/server.py | 404 |
| `serve(host, 0)` ignored port 0 and used the default port | float/server.py | `None` check |
| Notice `retire` with a non-number gave 500 | float/server.py | 400 |
| **Needs your decision:** `login.js` posts to `/api/auth/google/setup`, but no such route existed, so the Google setup form could never save | float/server.py | Added the route, calling the existing `config.save_google`. Allowed only on first run (no users) or for an admin; otherwise 403 |

## Passed with no change needed
Operator 403 / anonymous 401 on all 7 admin routes checked; cross-user conversation and file access (404); file-name traversal (name sanitised); plaintext key absent from all responses and the data folder; PIN and password flows; expired and idle sessions rejected; sign-in rate limit (429); web file references and JS syntax; stub chat loop and SSE.

## NOT tested
- Windows launcher (`.bat` / `.vbs`)
- "Use the computer" (mouse / keyboard control)
- Real AI provider answers, and real key verification (`verify_key` was stubbed). The OpenRouter key supplied in the request was **not used**, because the rules forbid real network calls. Because it was pasted in plain text, consider revoking it.
- Google sign-in and Drive upload (flow itself)
- Browser behaviour: the JS was only syntax-checked and its API paths matched to routes; no page was rendered

## Known issues / limitations
- **Forced password change is advisory only.** The server returns `must_change` and the page opens Settings, but a temporary password keeps full API access until changed. Fixing it needs front-end changes, so it was left alone.
- Session tokens are also accepted in the URL (`?token=`); they can end up in browser history or proxy logs. Not changed.
- No CORS / CSRF testing; only the Host-header check was exercised.
- Rate limits exist for sign-in, chat and unlock only; sign-up and admin routes were not rate-limited and not tested for it.
- The stress test is 5 minutes with 8 users on one machine: not a capacity or long-term leak test.
- This report does not claim the app is free of bugs.
