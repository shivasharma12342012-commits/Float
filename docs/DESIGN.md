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
3. **19 Built-In Agentic Tools + Clean MCP Client**:
   - Native tools for quote arithmetic, document generation, fleet group sheets, rate item banks, web search, computer use, and Model Context Protocol (`stdio` and `http`/`sse`) servers.
4. **Single-Operator or Multi-Operator Branch LAN Server**:
   - Works out of the box for a single rental desk or scales to a full branch with role-based access control, audit logging, and encrypted shared API keys.
