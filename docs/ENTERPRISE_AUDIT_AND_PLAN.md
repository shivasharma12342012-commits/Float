# Float — Step 1: Enterprise Audit & Prioritized Implementation Plan

**Repository:** `shivasharma12342012-commits/Float`  
**Audit Date:** 9 November 2026  
**Scope:** Full review of `README.md`, `docs/DESIGN.md`, `docs/AGENCY_SERVER.md`, `Agency Server.md`, all 8 Test Reports (`Float Test Report.md`, `Float test 2.md`, `Flaot test 3.md`, `Float Test Report 4.md`, `Test Report 5 .md`, `Test Report 6.md`, `Test Report 7.md`, `Test Report 8.md`), backend Python modules (`float/*.py`, `main.py`), frontend web assets (`float/web/*`), and the 500-test suite (`tests/*.py`).

---

## Section (A): Bugs, Code Findings & Status of Every Test-Report Issue

### A.1 Complete Inventory of Issues from All 8 Test Reports

| Report | Issue Mentioned in Report | Current Status in Code (`float/`) | Verification Detail |
| :--- | :--- | :--- | :--- |
| **Report 1** (`Float Test Report.md`) | Secure string comparison failing on non-ASCII text; shared rate limit between unlock and sign-in; built-in passphrase in code. | **Resolved** | `security.same()` encodes UTF-8 before `hmac.compare_digest`; `sign_in_limiter`, `chat_limiter`, and `unlock_limiter` are separate in `security.py`. |
| **Report 2** (`Float test 2.md`) | Non-numeric score or bad attendance IDs caused HTTP 500; cross-class mark writes allowed; SSE stream stayed open after completion. | **Resolved** | Validated in `server.py` (`marks_add`, `attendance_save`); ownership checked via `db.owns_class()`; `_send_sse()` sets `Connection: close` and `self.close_connection = True`. |
| **Report 3** (`Flaot test 3.md`) | Non-numeric route IDs (`500`); non-dict toolkit `values` (`500`); duplicate `org` API keys (`UNIQUE` on `NULL`); `%00` in static path; missing socket timeout; missing `/api/auth/google/setup` route. | **Resolved** | Route regex uses `\d{1,18}` for `*_id`; `db.put_key()` deletes prior `org` row before insert; `\x00` rejected with `404`; `is_relative_to()` enforced; `/api/auth/google/setup` implemented. |
| **Report 3** (`Flaot test 3.md`) | **Open item in Report 3:** Rate limits exist for sign-in, chat, and unlock only; `signup` and `admin` mutation routes are not rate-limited. | **Still Unresolved** | `POST /api/auth/signup` (when `self_signup="1"`) and `/api/admin/*` endpoints do not pass through a `RateLimiter`. |
| **Report 4** (`Float Test Report 4.md`) | `float/Attachments.py` uppercase filename broke Linux/macOS imports; `NaN` or out-of-range marks (`55/50`, `-5/50`, `3/0`) accepted. | **Resolved** | Tracked in Git as lowercase `float/attachments.py`; `math.isfinite()` and `0 <= score <= max_score` (`max_score > 0`) enforced in `server.py`. |
| **Report 4 & 8** (`Float Test Report 4.md`, `Test Report 8.md`) | **Open item in Report 4 & 8:** OpenRouter models have `cost_in = 0, cost_out = 0` in `config.py`, so rupee spend estimates and monthly caps show `₹0.00` for OpenRouter calls unless manually overridden in `/admin`. | **Partially Unresolved** | `/admin` now includes a Model Prices editor (`addPricesPanel` in `float/web/admin.js` and `/api/admin/prices`), and warns when prices are stale, but `config.py` still defaults OpenRouter models to `0.0, 0.0` paise, meaning default fair-share caps do not meter OpenRouter out-of-the-box. |
| **Report 5** (`Test Report 5 .md`) | Deleting another operator's class/task/conversation returned `200 OK`; operators could not see their own monthly cap (`cap_paise`). | **Resolved** | Ownership checks return `404` in `server.py`; `app.js` displays monthly cap usage and progress bar in Settings. |
| **Report 6** (`Test Report 6.md`) | Unbounded text field lengths (3 MB class name accepted); Drive/Calendar/Gmail starter chips implied direct read APIs. | **Resolved** | Field length limits enforced in `db.py` and `server.py`; starter chips updated. |
| **Report 7** (`Test Report 7.md`) | Advisory-only `must_change` password flag; `?token=` accepted in URL query string; raw tracebacks shown on 500; corrupt file downloaded on error. | **Resolved** | `_MUST_CHANGE_ALLOWED` blocks API access until password is changed; `_bearer()` reads `Authorization` header only; `_log_unexpected()` logs to `data/float_errors.log` with a short ref ID. |
| **Report 8** (`Test Report 8.md`) | Problem 1 (`Attachments.py` case), Problem 2 (No backup), Problem 3 (No DB schema migration), Problem 4 (Unpruned usage/audit rows), Problem 5 (Stats computed by AI instead of Python), Problem 6 (Hardcoded model prices). | **Resolved (with 2 caveats below)** | `float/attachments.py` is lowercase; `float/maintenance.py` runs daily + pre-migration SQLite backups (`keep=14`) and prunes old audit/usage rows into `usage_monthly`; `float/db.py` has `MIGRATIONS` with `PRAGMA user_version`; `float/stats.py` computes statistics deterministically in Python. |

---

### A.2 Additional Code Bugs & Technical Debt Found During Code Audit

1. **Per-Operator Isolation Instead of Shared Branch Fleet & Bookings (`float/db.py:137-176`)**:
   - Currently, the underlying tables (`klasses`, `students`, `marks`, `attendance`) are scoped to `user_id` (a holdover from when each teacher owned their own private class).
   - **Why this is a critical bug for a car rental agency:** If Desk Agent A registers a vehicle or records a booking/handover on Counter 1, Desk Agent B on Counter 2 and the Fleet Manager cannot see that vehicle's status or booking! In a real rental branch, vehicles, bookings, customers, and invoices belong to the **branch/agency**, not an individual operator's private silo.
2. **Rounding & Odd-GST Split in `calculate_quote` (`float/tools.py:420-440`)**:
   - Line 440 prints `CGST ₹{gst_amount/2:,.2f} + SGST ₹{gst_amount/2:,.2f}`. When `gst_amount` has an odd number of paise (for example `₹105.05` at 5% GST on `₹2,101`), `gst_amount / 2` is `52.525`, which formats to `₹52.52 + ₹52.52 = ₹105.04` (1 paisa discrepancy against the printed `₹105.05` total). Invoice math should use `Decimal` (`ROUND_HALF_UP`) with exact `cgst + sgst == gst_total` (or `igst` for inter-state supplies).
   - Also, `calculate_quote` does not validate negative inputs (`days < 0`, `daily_rate < 0`, `actual_km < 0`, `discount_amount < 0`) and applies flat rates without supporting weekend/seasonal surge multipliers or long-term tier discounts.
3. **UI Restore Action Missing for Backups (`float/web/admin.js:216-217`, `float/server.py`)**:
   - `/admin` lets an admin click **Back up now** (`POST /api/admin/backup`), which creates a backup in `data/backups/`, and `maintenance.py` has `restore_backup()`, but there is **no UI list of backups, no UI download of a `.sqlite3` backup file, and no UI restore button** in `/admin` (it tells the admin to close Float and run `python main.py restore` in a terminal).
4. **SQLite `synchronous=NORMAL` Durability Window (`float/db.py:236`)**:
   - For financial ledgers and sequential GST invoices, `PRAGMA synchronous=NORMAL` in WAL mode is crash-safe against app crashes, but on sudden power loss at a counter PC, the last transaction before a WAL checkpoint can roll back unless critical financial commits checkpoint or use `FULL` synchronization.

---

## Section (B): Security, Reliability & Data-Protection Gaps (India DPDP Act 2023)

### B.1 Authentication, Transport, and Session Security Gaps

1. **Transport Encryption Fallback When `cryptography` Is Not Installed (`float/transport.py:31-38`, `float/server.py:1734-1736`)**:
   - Float is designed to run with zero `pip` dependencies. However, `float/transport.py` relies on `from cryptography.hazmat...` for ECDH P-256 envelope encryption (`AVAILABLE = False` on pure stdlib Python), and `config.tls_files()` only enables HTTPS if cert/key PEM files are manually provisioned or generated.
   - When running on pure stdlib Python without `cryptography` and without TLS certificates, `/api/auth/signin` fails unless `FLOAT_ALLOW_PLAINTEXT=1` is set.
   - **Fix needed:** Document this transparently in the IT Security Statement, auto-generate a self-signed localhost/LAN TLS certificate via `openssl` CLI when available on Windows/macOS, and provide a pure-stdlib challenge-response or PBKDF2/HMAC-SHA256 pre-shared transport fallback when `cryptography` is absent.
2. **Encryption-at-Rest Key Handling (`data/.device_key` in `float/security.py:130-143`)**:
   - API keys (and any encrypted secrets) are encrypted using a 32-byte key stored in `data/.device_key` right next to `data/float.sqlite3` inside the same `data/` folder.
   - **Risk 1:** Anyone who copies the entire `data/` folder copies both `float.sqlite3` and `.device_key`.
   - **Risk 2:** Conversely, if an admin backs up only `float.sqlite3` (from `data/backups/`) and restores it on a new PC after a hardware failure, `.device_key` is different on the new PC, so `security.decrypt_secret()` silently returns `""` and all stored API keys stop working without a clear warning.
   - **Fix needed:** Explain this clearly in the IT Security Statement, detect key-mismatch after restore and show a clear admin banner ("Database restored on a new machine — re-enter your agency API key"), and allow optional master-passphrase wrapping of `.device_key`.
3. **Role-Based Access Control (RBAC) Granularity (`float/db.py:34`)**:
   - `users.role` currently has `CHECK(role IN ('teacher','admin'))` — only two roles exist (`admin` and `teacher` representing desk operator).
   - **Gap:** A car rental company needs **5 distinct roles**:
     1. `owner` (full control, branch/financial configuration, data deletion, role management)
     2. `manager` (branch fleet, tariff overrides, refund/discount approvals, maintenance & compliance)
     3. `desk_agent` (legacy `'teacher'` alias — bookings, handovers, returns, checklists, standard quotes, payments)
     4. `accountant` (GST invoices, credit notes, payment ledger, daily cash reconciliation, financial exports)
     5. `read_only` (auditor/viewer — can view dashboards, bookings, and reports, zero write permissions)
4. **Before/After Field-Level Audit Logging (`float/db.py:125-135`)**:
   - The `audit` table currently stores only `(user_id, actor, action, detail, ip, level, created_at)` with a free-text `detail` string.
   - **Gap:** Management and financial auditors require structured `entity_type`, `entity_id`, `old_value` (JSON), `new_value` (JSON), and `reason` for every sensitive action (tariff override, discount, deposit deduction, refund, credit note, vehicle status change, or record deletion).
5. **File Upload Validation (`float/attachments.py`, `float/server.py`)**:
   - Uploaded files (base64 in chat or future licence/damage photos) are size-capped, but need strict MIME/magic-byte verification (`%PDF-`, `PK\x03\x04`, `\x89PNG`, `\xff\xd8\xff` JPEG), filename sanitization, and per-route upload size limits so arbitrary executables or polyglot files cannot be stored.

### B.2 India Digital Personal Data Protection Act, 2023 (DPDP Act) Gaps

A car rental business in India collects sensitive personal data (**Driving Licence number, Aadhaar/Passport/Voter ID proof, phone number, email, home address, licence photos, and trip history**). Under the **Digital Personal Data Protection Act, 2023 (DPDP Act)**:
1. **No Consent Capture (`Sec. 6, DPDP Act 2023`)**: There is no customer consent timestamp, purpose notice (e.g., *"Collected for vehicle rental KYC, insurance verification, and traffic challan liability"*), or record of who captured consent at the counter.
2. **No Right to Access / Data Portability Export (`Sec. 11, DPDP Act 2023`)**: There is no one-click export of all personal data and rental history held for a specific customer.
3. **No Right to Erasure / Anonymization (`Sec. 12, DPDP Act 2023`)**: There is no workflow to erase/redact a customer's PII (name, phone, DL number, ID proof, photos) upon request while preserving anonymized financial/GST invoice totals required by the CGST Act, 2017 (which mandates retaining tax invoice records for 72 months / 6 years).
4. **No PII Access Log & Retention Policy (`Sec. 8, DPDP Act 2023`)**: Viewing or downloading a customer's ID/Driving Licence or exporting customer lists is not logged in a dedicated PII access trail, and there is no configurable retention policy to flag inactive customer KYC records for purging.

---

## Section (C): Missing Features Compared to Competing Car Rental Software

Currently, Float has a strong **AI document/chat workspace** and a **stateless GST calculator (`calculate_quote`)**, plus basic legacy tables (`klasses`/`students`/`marks`/`attendance`). However, compared to commercial car rental management systems (such as RentWorks, EasyRentPro, Fleetio, or HQ Rental Software), a buying car rental company will look for a **true relational operational database and counter UI** for the following 5 pillars:

### C.1 Fleet & Booking Engine
1. **Vehicle Master Registry (`vehicles` table & UI)**:
   - Missing structured fields: Registration Number (`MH-02-AB-1234`, unique), Make, Model, Variant, Vehicle Category, VIN / Chassis Number, Engine Number, Fuel Type (`Petrol`, `Diesel`, `CNG`, `EV`, `Hybrid`), Transmission (`Manual`, `Automatic`), Seats, Colour, Purchase Date, Purchase Cost, Current Odometer (km), Fuel Level (eighths/percentage), Home Branch ID, Current Branch ID, Daily/Weekly/Monthly Base Rates, Included km/day, Extra km/hr rates, and Live Status (`available`, `rented`, `in_workshop`, `reserved`, `blocked`).
2. **Booking Calendar & Overlap Detection (`bookings` table & Visual Timeline)**:
   - Currently, Float has no `bookings` table that locks a specific `vehicle_id` between `pickup_at` and `return_at`. The same registration plate can be quoted or promised to two customers for overlapping dates without warning.
   - Needs deterministic interval overlap prevention:
     $$\text{Overlap} \iff (\text{start}_A < \text{end}_B + \text{turnaround\_buffer}) \land (\text{end}_A > \text{start}_B)$$
   - Needs a visual per-vehicle horizontal timeline / Gantt calendar in the UI.
3. **Reservation Lifecycle & Cancellation / No-Show Engine**:
   - Needs state machine enforcement: `enquiry` $\rightarrow$ `confirmed` $\rightarrow$ `picked_up` $\rightarrow$ `returned` $\rightarrow$ `closed`, plus `cancelled` and `no_show` transitions.
   - Needs configurable cancellation rules (e.g., $>48\text{h}$ before pickup: 100% advance refund; $24\text{–}48\text{h}$: 50% fee; $<24\text{h}$ or `no_show`: 1 day tariff forfeiture, 100% security deposit refund) computed deterministically.
4. **Availability Search by Date Range, Class & Branch**:
   - Instant filter showing all vehicles that are (a) in the requested branch and category, (b) `status == 'available'`, (c) have no overlapping `confirmed` or `picked_up` booking in `[start_dt, end_dt]`, and (d) have no expired insurance/PUC/fitness or overdue maintenance block.
5. **Multi-Branch Operations (`branches` & `branch_transfers`)**:
   - Ability to define branches (e.g., *Mumbai Airport T2*, *Pune Station*, *Bengaluru Indiranagar*), assign vehicles and staff to branches, support one-way inter-branch drop-offs, and log inter-branch vehicle transfers with odometer/fuel checks.

### C.2 Compliance & Customer Records
1. **Customer Master & Repeat History (`customers` table)**:
   - Full profile: Name, Phone, Email, Address, GSTIN (for B2B corporate rentals), Driving Licence Number, DL Expiry Date, DL Issuing State, DL Photo / Scan attachment, ID Proof Type (`Passport`, `Voter ID`, `PAN`, `Masked Aadhaar`), ID Proof Number, DPDP Consent Timestamp, Blacklist/Notes flag, and lifetime booking/damage/payment history.
2. **Proactive Expiry Alerts (Customer DL & Vehicle Compliance)**:
   - Block or warn at booking pickup if the customer's Driving Licence expires before `return_at`.
3. **Vehicle Compliance Tracker (`vehicle_compliance` table)**:
   - Track **Comprehensive Insurance**, **PUC (Pollution Under Control)**, **Fitness Certificate (FC)**, **All-India / State Tourist Permit**, **Road Tax**, and **FASTag Wallet Balance / Status** per vehicle, with 30-day / 7-day / expired dashboard alerts.
4. **India DPDP Act 2023 Compliance Controls**:
   - Consent checkbox & purpose statement on customer creation, Customer Data Export (`.json` / `.pdf`), Customer PII Anonymization/Deletion on request (retaining locked GST invoice ledgers), and PII access audit logging.

### C.3 Money, Payments & GST Invoicing
1. **Payment Ledger (`payments` table)**:
   - Track every transaction per booking: `advance`, `security_deposit`, `part_payment`, `final_settlement`, `deposit_refund`, `cancellation_refund`.
   - Record Payment Mode (`UPI`, `Card`, `Cash`, `NEFT/RTGS`, `Cheque`), Reference / UTR Number, timestamp, and receiving operator.
   - Real-time calculation of **Total Collected**, **Deposit Held**, **Refund Due**, and **Net Balance Due**.
2. **Immutable Sequential GST Invoices & Credit Notes (`invoices` & `credit_notes` tables)**:
   - Sequential, gap-free financial-year invoice numbering (e.g., `FLT/2026-27/00001`) generated inside an immediate SQLite transaction (`BEGIN IMMEDIATE`).
   - Once issued, an invoice row is **immutable** (`UPDATE` and `DELETE` forbidden at the application and SQLite trigger level).
   - Any post-issue adjustment requires issuing a linked, sequentially numbered **Credit Note (`CN/2026-27/00001`)** with a mandatory reason and audit trail.
   - Supports SAC code (`996601` / `997311`), customer GSTIN, place of supply, and exact `CGST + SGST` (intra-state) or `IGST` (inter-state) split.
3. **Daily Cash & Collection Report + End-of-Shift Reconciliation (`shift_handovers` table)**:
   - Breakdown of cash vs. UPI vs. card vs. bank transfers collected and refunded during a shift, opening/closing cash drawer count, variance calculation, and operator sign-off.
4. **Dynamic Pricing & Audited Overrides**:
   - Seasonal and weekend surge multipliers, weekly (7+ days) and monthly (30+ days) discount tiers, and a mandatory **Rate Override Reason + Approving Manager/Owner** audit record whenever a desk agent changes the standard tariff or grants an extra discount.

### C.4 Fleet Operations (Maintenance, Damage, Signatures, Chauffeurs)
1. **Maintenance Schedule & Workshop Job Cards (`maintenance_logs` table)**:
   - Track service intervals by both **odometer km** (e.g. every 10,000 km) and **date** (e.g. every 6 months).
   - Workshop job cards with vendor name, odometer in/out, itemized parts & labour cost, downtime days, and automatic vehicle status transition (`in_workshop` $\leftrightarrow$ `available`).
2. **Vehicle Damage History & Annotated Photo Records (`damage_records` table)**:
   - Per-vehicle damage log linked to booking/handover, panel location (`Front Bumper`, `Left Rear Door`, `Windshield`, etc.), severity (`Scratch`, `Dent`, `Crack`, `Major`), photo upload with HTML5 canvas annotation (circle/arrow markup saved as PNG/data URL), estimated repair cost, deposit deduction amount, and historical view so repeat/pre-existing scratches are never double-charged.
3. **Digital Signature Capture on Agreements & Checklists (`signatures` table)**:
   - Built-in HTML5 Canvas touch/mouse signature pad for both **Customer** and **Desk Operator**, storing the stroke PNG, signer name, IP/device info, SHA-256 document hash, and ISO timestamp, embedded directly into the generated `.pdf` / `.docx` / `.html` handover & agreement record.
4. **Chauffeur Roster & Driver Assignment (`drivers` table)**:
   - Driver master (name, phone, badge/DL number, DL expiry, languages spoken, daily batta rate, status) and assignment to chauffeur-driven bookings with shift conflict detection.

### C.5 Management Analytics, RBAC, Backup/Restore & Bulk Import
1. **Executive Fleet Dashboards**:
   - **Fleet Utilization %** (rented days $\div$ available fleet-days), **Revenue per Vehicle**, **Idle Days per Vehicle**, and **Net Profitability per Vehicle** (Gross Rental Revenue minus Maintenance/Workshop Costs and Chauffeur Batta).
2. **5-Role RBAC + Before/After Audit Trail**:
   - Enforce `owner`, `manager`, `desk_agent` (backward-compatible with `'teacher'`), `accountant`, and `read_only` across all routes and UI views, with old/new JSON diffs in `audit`.
3. **UI Backup & Restore**:
   - List all backups in `/admin`, download a backup `.sqlite3` file directly from the browser, and trigger a verified safe restore from the UI (creating a pre-restore safety snapshot first).
4. **Excel / CSV Bulk Importer with Preview & Validation Report**:
   - Upload `.csv` or `.xlsx` files for **Vehicles** and **Customers**, preview parsed rows in a staging table, highlight row-level errors (invalid registration format, duplicate plate, missing phone, invalid date), and commit valid rows in one click.

---

## Prioritized Implementation Plan (For Your Approval)

All new features will be built using **100% Python standard library (`sqlite3`, `decimal`, `csv`, `zipfile`, `hashlib`, `hmac`, `datetime`) and vanilla HTML/CSS/JS**, preserving every existing test and API contract.

### Phase 1: Security, Durability & RBAC Foundation (Step 3 Core)
1. **Database Migration v3 (`float/db.py`)**:
   - Add schema migration `v3` creating the enterprise relational tables (`branches`, `vehicles`, `vehicle_compliance`, `customers`, `drivers`, `bookings`, `payments`, `invoices`, `credit_notes`, `maintenance_logs`, `damage_records`, `signatures`, `shift_reconciliations`, `branch_transfers`) + SQLite triggers preventing `UPDATE`/`DELETE` on issued `invoices`.
   - Expand `users.role` support to `owner`, `manager`, `desk_agent` (keeping `'teacher'` and `'admin'` 100% compatible), `accountant`, and `read_only`.
   - Upgrade `audit` table with `entity_type`, `entity_id`, `old_value`, `new_value`, and `reason` columns.
2. **Security & Crash-Safety Hardening (`float/security.py`, `float/server.py`, `float/attachments.py`)**:
   - Add rate limiting to `/api/auth/signup` and sensitive `/api/admin/*` endpoints.
   - Add magic-byte / MIME validation for file and image uploads.
   - Add WAL checkpoint / `FULL` sync around invoice & payment ledger writes so power loss mid-write cannot corrupt or lose financial records.
   - Add realistic default INR token pricing for OpenRouter models in `config.py` so monthly caps work out-of-the-box.

### Phase 2: Fleet Master, Multi-Branch, Booking Calendar & Compliance (Step 2A & 2B)
1. **Fleet Operations Module (`float/rental_ops.py` & REST endpoints in `float/server.py`)**:
   - Multi-branch CRUD + inter-branch vehicle transfer workflow.
   - Vehicle Master CRUD + compliance tracker (Insurance, PUC, Fitness, Permit, FASTag) with automatic expiry alerts.
   - Customer Master CRUD with Driving Licence expiry checks, ID proof metadata, repeat history, and **DPDP Act 2023** consent capture, data export, and PII anonymization/erasure.
   - Chauffeur/Driver roster and booking assignment with overlap check.
   - Booking lifecycle engine (`enquiry`, `confirmed`, `picked_up`, `returned`, `closed`, `cancelled`, `no_show`) with strict interval overlap prevention, cancellation refund rules, and availability search by date range, class, and branch.

### Phase 3: Money, Immutable GST Invoicing, Operations & Analytics (Step 2C, 2D & 2E)
1. **Financial & GST Engine (`float/rental_ops.py`, `float/tools.py`)**:
   - Exact `Decimal`-based tariff math (`calculate_quote` + booking billing) with weekend/seasonal surge rates, weekly/monthly discounts, audited rate overrides (requiring reason + manager/owner approval), and exact `CGST + SGST = Total GST` rounding.
   - Payment ledger per booking (`advance`, `deposit`, `partial`, `refund`, `dues`) with mode and reference number.
   - Gap-free sequential GST invoice generator (`FLT/YYYY-YY/NNNNN`) and Credit Note issuer (`CN/YYYY-YY/NNNNN`).
   - Daily cash & collection report and end-of-shift reconciliation.
2. **Maintenance, Annotated Damage Photos, Digital Signatures & Dashboards**:
   - Maintenance schedule by km/date + workshop job cards.
   - Damage records with photo annotation canvas and per-vehicle damage history.
   - Digital signature capture (Canvas + SHA-256 timestamp) on agreements and handover checklists.
   - Fleet profitability & utilization dashboard (Utilization %, Revenue/Vehicle, Idle Days, Net Profit/Vehicle).
   - Excel/CSV bulk import with dry-run preview and row-level error report, plus UI backup download/restore in `/admin`.
3. **Frontend Workspace Integration (`float/web/index.html`, `float/web/app.js`, `float/web/app.css`, `float/web/admin.js`)**:
   - Add a clean, fast **Fleet & Counter Ops Hub** drawer/view inside the existing Float interface (Vehicle Master, Visual Booking Timeline, Customer & DPDP KYC, GST Invoices & Payments, Workshop & Damage, Shift Cash Reconciliation, Bulk CSV/XLSX Import, and Profitability Dashboard) without cluttering the existing chat workflow.

### Phase 4: Verification Test Suite & Deployment Documentation (Step 3 & Step 4)
1. **Comprehensive Unit & Integration Tests (`tests/test_enterprise_rental.py`)**:
   - Exact tests for tariff math, odd-paise GST splits, weekend/long-term rates, deposit settlement, booking overlap rejection, cancellation refunds, gap-free invoice numbering, invoice immutability, credit notes, DPDP customer erasure/export, RBAC permissions, and crash-safe DB recovery.
   - Run the complete test suite (`python -W error -m unittest discover -s tests -p "*.py"`) and report actual output.
2. **Deployment Readiness Documents**:
   - `docs/COUNTER_STAFF_GUIDE.md` — Non-technical counter staff installation & daily shift guide.
   - `docs/SECURITY_AND_DATA_HANDLING.md` — One-page IT & DPDP Act 2023 security and encryption statement (including `.device_key` machine-migration behavior).
   - `CHANGELOG.md` and version bump in `float/config.py`.

---

*Awaiting your approval to proceed to Steps 2, 3, and 4.*
