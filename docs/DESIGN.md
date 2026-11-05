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
   - Works out of the box for a single rental desk or scales to a full branch with role-based access control, audit logging, and encrypted shared API keys.
