# Changelog — Float

All notable changes to **Float** are documented in this file.

---

## [1.1.0] — 2026-11-09 — Enterprise Rental Operations, GST, DPDP & Security Release

### Added
- **Fleet Master & Multi-Branch Operations (`float/rental_ops.py`, `float/server.py`):**
  - Full `vehicles` master table (`reg_number`, `make`, `model`, `variant`, `category`, `vin`, `fuel_type`, `transmission`, `seats`, `colour`, `purchase_date`, `purchase_cost`, `odometer_km`, `fuel_level`, `branch_id`, `status` in `available / rented / in_workshop / reserved / blocked`).
  - Multi-branch registry (`branches`) and audited inter-branch vehicle transfers (`branch_transfers`) with odometer validation.
  - Vehicle compliance tracking (`vehicle_compliance`) for `insurance`, `puc`, `fitness`, `permit`, `fastag`, and `road_tax`, plus proactive expiry and low-FASTag-balance alerts (`/api/ops/alerts`).
- **Booking Calendar, Overlap Detection, Lifecycle & Availability Search:**
  - Deterministic overlap detection (`check_booking_conflicts`) preventing double-booking of the same vehicle or chauffeur across overlapping intervals.
  - Visual timeline per vehicle (`/api/ops/timeline`) and availability search by date range, vehicle category, and branch (`/api/ops/availability`).
  - Full 7-state reservation lifecycle (`enquiry`, `confirmed`, `picked_up`, `returned`, `closed`, `cancelled`, `no_show`) with automatic vehicle/driver status transitions and deterministic cancellation/no-show fee and refund math (`compute_cancellation_settlement`).
- **Customer KYC & India DPDP Act, 2023 Compliance:**
  - Customer profile with Driving Licence number, DL expiry date, licence photo, ID proof, and repeat-customer history (`/api/ops/customers`).
  - Automatic block on self-drive bookings when a customer's Driving Licence expires before the trip return date.
  - Explicit consent capture (DPDP Act, 2023 Section 6), right-to-access data portability JSON export (Section 11, `/api/ops/customers/{id}/export`), right-to-erasure PII anonymization preserving statutory GST invoices (Section 12, `/api/ops/customers/{id}/erase`), and `pii_access_log`.
- **Exact Decimal Tariff Engine, Payment Ledger, Immutable GST Invoices & Credit Notes:**
  - Upgraded `calculate_tariff_exact` and `_tool_calculate_quote` to `decimal.Decimal` (`ROUND_HALF_UP`) with exact odd-paisa `CGST + SGST == Total GST` splits, weekend surge, seasonal surge, long-term discounts, and mandatory audited reasons for rate overrides.
  - Per-booking payment ledger (`payments`) supporting `advance`, `deposit`, `partial`, `settlement`, `refund`, `deposit_refund`, and `cancellation_refund` with payment mode (`UPI`, `Cash`, `Card`, `NEFT`, `RTGS`, `Cheque`) and reference number.
  - Gap-free sequential GST invoices (`FLT/YYYY-YY/NNNNN`) protected against `UPDATE` and `DELETE` by SQLite triggers (`trg_invoices_immutable_update`, `trg_invoices_immutable_delete`), paired with sequential Credit Notes (`CN/YYYY-YY/NNNNN`) for post-issue adjustments.
  - Daily cash & collection report (`/api/ops/collections`) and end-of-shift cash drawer variance reconciliation (`/api/ops/reconcile`).
- **Workshop Job Cards, Annotated Damage History & Digital Signatures:**
  - Maintenance schedule by kilometres and date, workshop job cards (`maintenance_logs`), and automatic `in_workshop` / `available` vehicle transitions.
  - Vehicle damage records (`damage_records`) with canvas annotation coordinates (`annotation_json`) and per-vehicle repeat damage history.
  - Digital signature capture (`signatures`) with SHA-256 document digest (`doc_hash`) and timestamp.
- **Management Dashboards, 5-Role RBAC, UI Backup/Restore & Bulk Import:**
  - 30-day fleet utilization %, idle days, gross revenue, maintenance/driver cost, and net profit per vehicle (`/api/ops/dashboard`).
  - 5 operational roles (`owner`, `manager`, `desk_agent`, `accountant`, `read_only`) enforced across `/api/ops/*` and `/api/admin/*`, with before/after JSON values (`old_value`, `new_value`, `reason`) in `audit`.
  - Admin UI backup download and one-click online SQLite restore (`/api/admin/backups`, `/api/admin/restore`) with automatic `pre-restore` safety snapshot.
  - CSV (`.csv`) and Excel (`.xlsx`) bulk importer with dry-run preview and row-level error report (`/api/ops/import/preview`, `/api/ops/import/commit`).
- **Documentation & Enterprise Test Suite:**
  - Added `docs/ENTERPRISE_AUDIT_AND_PLAN.md`, `docs/COUNTER_STAFF_GUIDE.md`, `docs/SECURITY_AND_DATA_HANDLING.md`, and `tests/test_enterprise_rental.py`.

### Fixed & Hardened
- Fixed binary floating-point rounding in `_tool_calculate_quote` and enforced `CGST + SGST == Total GST` on odd-paisa amounts.
- Populated default INR token cost estimates for OpenRouter models (`openrouter/auto`, `openai/gpt-4o-mini`) in `float/config.py`.
- Added rate limiting to `/api/auth/signup` (`security.signup_limiter`), magic-byte upload verification (`attachments.validate_upload_signature`), and `.device_key` health detection (`db.key_health_status()`).
- Added passive WAL checkpoints (`PRAGMA wal_checkpoint(PASSIVE)`) after financial writes for immediate crash recovery.
