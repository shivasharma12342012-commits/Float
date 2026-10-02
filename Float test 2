# Float — Teacher-Session Stress Test Report

**Date:** 2 October 2026  
**Environment:** Python 3.12.3, Linux sandbox, fresh empty database each run  
**Method:** A script (`teacher_session_test.py`) acts like teachers and an admin using the live server. Written and run with AI assistance; results below are real output.

## What the script simulates
Admin signs up and adds two teachers. A teacher signs in, opens the dashboard, creates a class with Hindi and awkward names (including an SQL-injection string), enters marks and attendance, adds a task and timetable, then tries messy input, a second teacher's access, wrong passwords, and a burst of 720 requests from 6 parallel users.

## Bugs found and fixed (all in `float/server.py`)
| # | Problem found | Fix |
|---|---|---|
| 1 | A non-numeric score crashed the server (HTTP 500) | Marks are validated; clear 400 error returned |
| 2 | Bad attendance ids crashed the server (HTTP 500) | Attendance ids validated; clear 400 error returned |
| 3 | A teacher could save marks against students from a class that was not theirs | Marks and attendance now accepted only for students in that class |
| 4 | After a chat reply finished, the connection stayed open, so the browser could wait forever | Stream connection now closes when the reply ends |

## Results after fixes (2 runs)
| Check | Run 1 | Run 2 |
|---|---|---|
| Teacher-session script | 26 / 26 passed | 26 / 26 passed |
| Existing unit tests | 25 / 25 passed | 25 / 25 passed |
| Burst: 720 requests, 6 parallel users | 0 server errors (about 3 s) | 0 server errors |

Also confirmed: other teachers cannot read or write a class that isn't theirs; teachers cannot use admin functions; fake and signed-out tokens are rejected; repeated wrong passwords are locked out; chat without an API key gives a clear message instead of failing.

## Not tested
- A real person using it for 10 minutes. This was a compressed simulation through the server's API, not the browser screens.
- Real AI answers (no live API key), Windows launcher, "use the computer" feature, file downloads, and the admin panel screens
- Long-running (hours or days) use, or an independent security audit

## Limitations
This report covers only the checks listed. It does not guarantee the software is free of defects. AI-generated content inside Float must be reviewed by a teacher before use.
