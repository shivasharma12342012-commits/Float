# Float — Test Report 4 (Teacher's Numbers Audit)

- **Date:** 2 October 2026
- **Method:** Run with AI assistance (Claude). Every number below is from commands actually run. A script (`teacher_math_test.py`) acted like a Class 8 maths teacher using the live server, and a second part measured the code itself.
- **Environment:** Linux sandbox, Python 3.12.3, standard library only, fresh empty database, loopback only, no AI provider calls (no API key).
- **Test class:** 8B Mathematics, 40 students (Hindi and English names), seeded random marks (seed 7) so the run can be repeated.

## 1. Headline

| Item | Result |
|---|---|
| Unit tests on the zip **exactly as uploaded** | **Fail**. Only 13 of 25 tests run, 1 import error (see Bug 1) |
| Unit tests after renaming `Attachments.py` → `attachments.py` | 25 / 25 pass, run 1 (2.19 s) and run 2 (2.14 s) |
| Teacher session checks (class, marks, attendance, AI class lookup) | 7 / 7 pass |
| Server errors during the 300-request read test | 0 |

## 2. Bugs found

| # | Problem | Severity | Suggested fix |
|---|---|---|---|
| 1 | File is named `float/Attachments.py` but the code imports `attachments`. On Linux and macOS (case-sensitive) the server will not start. Windows hides this. | **High** (app won't run off Windows) | Rename the file to lowercase `attachments.py` |
| 2 | A mark of `NaN` returns **HTTP 500** instead of a 400 message | Low (a browser cannot send NaN, only direct API calls) | Reject non-finite numbers with `math.isfinite()` |
| 3 | Impossible marks are **accepted** (HTTP 200): 55 out of 50, −5 out of 50, 3 out of 0, 1e308 | Medium for a marks app | Check `0 ≤ score ≤ max_score` and `max_score > 0` in `marks_add` |

Edge-case marks table (HTTP status): 55/50 → 200 · −5/50 → 200 · 3/0 → 200 · "42" (text) → 200 (converted) · "abc" → 400 · null → 400 · 1e308 → 200 · NaN → **500**.

Bug 3 matters because a mark with max 0 can cause a divide-by-zero in a percentage later. I did not test AI report generation, so that is a risk, not a confirmed failure.

## 3. The class maths: does Float return what a teacher would calculate?

40 marks out of 50 saved, then read back and compared with a manual calculation.

| Statistic | Value |
|---|---|
| Mean | 32.86 / 50 (**65.7 %**) |
| Median | 33.65 |
| Std. deviation | 7.21 (population), 7.30 (sample) |
| Lowest / highest | 17.3 / 48.5 |
| Pass (≥ 33 %) | 40 / 40 (100 %) |
| Mean recomputed from server data | 32.86 — **exact match** |
| Marks round-trip | 40 saved, 40 returned, identical |

CBSE-style grade bands (my own cut-offs, applied to the data): A1 = 1, A2 = 5, B1 = 11, B2 = 8, C1 = 9, C2 = 3, D = 3 (total 40).

**Attendance**, 5 school days × 40 students = 200 possible:

| Date | Present | Absent |
|---|---|---|
| 28 Sep | 36 | 4 |
| 29 Sep | 34 | 6 |
| 30 Sep | 37 | 3 |
| 1 Oct | 39 | 1 |
| 2 Oct | 35 | 5 |
| **Total** | **181** | **19** |

Attendance = 181 / 200 = **90.5 %**. Float's stored counts matched on every day.

Note: Float stores marks and attendance but has no built-in average, percentage or grade screen that I could find. The statistics above come from my calculation on Float's stored data. The AI tool `look_up_class` returned all 40 scores in the right format.

## 4. Speed

300 sequential reads of the class page: median **5.2 ms**, 95th percentile 7.3 ms, 99th percentile 8.8 ms, slowest 12.1 ms, mean 5.7 ms. Fine for one teacher on one laptop.

## 5. Money: what would AI cost a teacher?

Assumption (mine): each request uses 3,000 tokens in and 1,000 out; 40 requests a day; 26 working days a month. Float's `estimate_paise()` matched my hand formula for every model.

| Model | Per request (paise) | Per month (₹) |
|---|---|---|
| Gemini 2.0 Flash | 5.7 | 59 |
| GPT-4o mini | 8.6 | 89 |
| GPT-4.1 mini | 23.1 | 240 |
| Gemini 2.5 Flash | 28.5 | 296 |
| Claude Haiku 4.5 | 64 | 666 |
| GPT-4.1 / Gemini 2.5 Pro | 115.5 | 1,201 |
| GPT-4o | 147 | 1,529 |
| Claude Sonnet 4.5 | 200 | 2,080 |
| Claude Opus 4.1 | 1,000 | 10,400 |
| OpenRouter models | 0 (not priced) | 0 (**not real cost**) |

Two cautions. The price list is typed into `config.py` and goes out of date, and OpenRouter shows ₹0, which a teacher may read as "free". The 40-requests-a-day figure is a guess; real use will differ.

## 6. Security numbers

| Measure | Value |
|---|---|
| Password hashing | scrypt, N = 2^15, r = 8, p = 1 |
| Time per sign-in check | **118 ms** (measured, average of 5) |
| Memory per check | 32 MiB working, 64 MiB cap |
| Guesses per day, one CPU core | about 731,583 |
| Worst case to try all 8-letter lowercase passwords (26^8 ≈ 2.09 × 10^11) | about 782 years on one core |
| Wrong-password limit | 10 tries → first 7 got 401, last 3 got **429** (matches the limit of 7) |
| Upload limit | 12 MB |

The 782-year figure is for one core and one password style. An attacker with many machines or GPUs is faster, and teachers who choose weak passwords are guessed far sooner. It shows the hashing is sensibly slow, not that accounts are unbreakable.

Also checked: the "own work share" figure. 300 AI characters and 100 own characters gave 25 %, which is correct (100 ÷ 400).

## 7. Code size and complexity

| Measure | Value |
|---|---|
| Python files / lines (`float/` + `main.py`) | 16 / 6,951 |
| Whole project including web files and tests | 10,901 lines |
| Functions | 319 |
| API routes | 46 |
| Toolkit templates | 19 in 5 groups |
| AI tool schemas | 5 |
| Models listed | 12 |
| Cyclomatic complexity (my rough count) | mean 4.68, median 3, max 30 |
| Functions above 15 | 15 of 319 (4.7 %) |
| Most complex | `agent.run` 30, `computer.act` 27, `artifacts.build_html` 24, `artifacts.build_pdf` 23, `greeting.build` 21 |

Most of the code is simple. The few complicated functions are the ones that handle the AI chat loop, computer control and document building, so they are where future bugs are most likely.

## 8. Not tested

- Real AI answers, and whether the maths in AI-written report cards is correct (no API key)
- A person using the browser screens, admin panel, or Windows launcher
- Marks entered through the screens (I used the API directly)
- "Use the computer" feature, file downloads, long-running use, an independent security audit
- Tests for the lowercase-rename fix on a real Windows machine

## 9. Limitations

I did not change your files; the rename was applied only in my scratch copy. The student marks are synthetic. The cost table rests on my usage guess. This report is not a guarantee the software is free of defects. AI-generated content inside Float must be reviewed by a teacher before use.
