# Float — Architecture & Design

Float is a **zero-dependency, local-first AI operations workspace** engineered for **car rental agencies, fleet managers, and rental counter operators**.

## Core Principles

1. **Zero External Runtime Dependencies**: Runs on Python 3.10+ standard library (`http.server`, `sqlite3`, `ssl`, `urllib`, `zipfile`). No `pip install` required.
2. **Instant Rental Counter Workflows**:
   - **Rental Quote & Tariff Calculator** (`calculate_quote` tool with GST, extra km, extra hour, driver allowance, weekend surge, and discount support)
   - **Rental Agreement & T&C Generator** (`.docx` & `.pdf` export)
   - **Vehicle Handover & Return Inspection Checklists**
   - **Damage Assessment & Security Deposit Deduction Notice**
   - **Fleet Availability & Booking Ledger Analyzer** (`.xlsx` & SVG chart generation)
3. **6 Core Native Agentic Tools + Clean MCP Client**:
   - Deterministic tools (`calculate_quote`, `create_file`, `look_up_class`, `save_task`, `read_my_day`, `use_computer`) plus Model Context Protocol (`stdio` and `http`/`sse`) tool discovery.
4. **Single-Operator or Multi-Operator Branch LAN Server**:
   - Works out of the box for a single rental desk (`127.0.0.1:8766`) or scales to a full branch (`0.0.0.0:8766`) with fixed-desk IP session binding (`desk_ip`), role-based access control, audit logging, and encrypted shared API keys.

## Module Breakdown

- `server.py`: Standard library `ThreadingHTTPServer` (default port `8766`) with a bounded 24-worker `ThreadPoolExecutor`, O(1) static route table, in-memory `ETag` cache, SSE chat streaming, and cookie/session auth.
- `db.py`: SQLite storage layer (`data/float.sqlite3` in WAL mode) with automatic schema migration, user accounts, fixed-desk IP session binding (`desk_ip`), fleet groups, shift tasks, chat history, and token usage metering.
- `tools.py` & `artifacts.py`: Deterministic Indian GST (`5%` / `18%` CGST + SGST), extra km/hour tariff engine, deposit settlement math, and zero-dependency `.docx`, `.xlsx`, and `.pdf` document builders.
- `computer.py` & `desktop.py`: Optional operator-confirmed local desktop automation and window discovery on Windows (`ctypes` Win32/UIA) and macOS (`screencapture`, `osascript`, Quartz).
- `web/`: Single-page vanilla HTML/CSS/JS frontend (`index.html`, `login.html`, `admin.html`, `app.js`, `app.css`, `secure.js`) with zero build step, autofill suppression, and interactive pixel mascot.
