# Float — Test Report

**Date:** 2 October 2026  
**Environment:** Python 3.12.3, Linux (sandbox), clean temporary data folder each run  
**Method:** Automated tests, run twice. Tests were run with AI assistance (Claude); the results below are the actual output of those runs.

## Results

| Check | Run 1 | Run 2 |
|---|---|---|
| Unit tests (`tests/test_float.py`) | 25 / 25 passed | 25 / 25 passed |
| Live server start-up | Pass | Pass |
| Login page loads (`GET /` → 200) | Pass | Pass |
| Auth state endpoint (→ 200) | Pass | Pass |
| Unlock endpoint rejects anonymous user (→ 401) | Pass | Pass |
| Profile endpoint rejects anonymous user (→ 401) | Pass | Pass |

**Overall: 2 runs, 0 failures.**

## Changes verified in this version
- Secure string comparison no longer fails on non-English text.
- Unlock attempts use their own rate limit, separate from sign-in.
- No built-in passphrase ships in the code.

## Not tested
- Windows launcher (`Start Float.bat` / `.vbs`)
- Browser interface (sign-up, chat, admin panel) by a human
- Real AI provider calls with live API keys
- "Use the computer" feature
- Load, performance and independent security audit
- Real use by teachers over time

## Limitations
This report covers only the checks listed above. It is not a guarantee that the software is free of defects. AI-generated output inside Float must be reviewed by a teacher before use.
