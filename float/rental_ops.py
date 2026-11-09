"""Float — Enterprise Car Rental Operations, Compliance, GST & Fleet Engine.

100% Python standard library (sqlite3, decimal, datetime, csv, hashlib, json).
Implements:
- Multi-branch registry and inter-branch vehicle transfers
- Vehicle master (registration plate, make/model/variant, VIN, fuel, seats, colour,
  purchase date, odometer, status: available / rented / in_workshop / reserved / blocked)
- Vehicle compliance tracker (Insurance, PUC, Fitness, Permit, FASTag, Road Tax) + expiry alerts
- Customer master with Driving Licence expiry alerts, ID proof, repeat history, and
  India Digital Personal Data Protection Act, 2023 (DPDP Act) consent capture,
  data portability export, PII erasure/anonymization, and PII access logging
- Chauffeur / driver roster and conflict-checked shift/booking assignment
- Booking calendar with deterministic interval overlap prevention, visual timeline data,
  reservation lifecycle (enquiry -> confirmed -> picked_up -> returned -> closed / cancelled / no_show),
  and cancellation / refund calculation
- Availability search by date range, vehicle category, and branch
- Exact Decimal tariff & GST calculation (weekend/seasonal surge, long-term discounts,
  logged rate overrides with reason & approver, exact CGST + SGST / IGST rounding)
- Payment ledger per booking (advance, deposit, partial, settlement, refund) with mode & reference
- Gap-free sequential GST invoices (FLT/YYYY-YY/NNNNN) locked by SQLite immutability triggers,
  plus sequential Credit Notes (CN/YYYY-YY/NNNNN) for audited post-issue adjustments
- Daily cash & collection report and end-of-shift drawer reconciliation
- Maintenance schedules by km and date, workshop job cards, and service history
- Damage records with photo & canvas annotation history per vehicle
- Digital signature capture with SHA-256 document digest and timestamp
- Executive dashboards (utilization %, revenue/vehicle, idle days, net profitability/vehicle)
- 5-role RBAC (owner, manager, desk_agent, accountant, read_only) & before/after audit logging
- Excel (.xlsx) and CSV bulk importer with dry-run preview and row-level error report
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import io
import json
import re
import sqlite3
import time
from decimal import Decimal, InvalidOperation, ROUND_FLOOR, ROUND_HALF_UP
from typing import Any

from . import attachments, db

VALID_VEHICLE_STATUSES = ("available", "rented", "in_workshop", "reserved", "blocked")
VALID_BOOKING_STATUSES = (
    "enquiry",
    "confirmed",
    "picked_up",
    "returned",
    "closed",
    "cancelled",
    "no_show",
)
VALID_PAYMENT_KINDS = (
    "advance",
    "deposit",
    "partial",
    "settlement",
    "refund",
    "deposit_refund",
    "cancellation_refund",
)
VALID_PAYMENT_MODES = ("UPI", "Cash", "Card", "NEFT", "RTGS", "Cheque")
VALID_COMPLIANCE_TYPES = ("insurance", "puc", "fitness", "permit", "fastag", "road_tax")
VALID_OPS_ROLES = ("owner", "manager", "desk_agent", "accountant", "read_only")
ROLES = VALID_OPS_ROLES


class RentalOpsError(ValueError):
    """Domain validation error in car rental operations."""


# Role permission matrix (supports both underscore and dotted permission names)
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "owner": {
        "read", "write_booking", "write_customer", "write_payment", "write_vehicle",
        "write_maintenance", "write_damage", "approve_override", "issue_invoice",
        "issue_credit_note", "reconcile_shift", "delete_record", "manage_branches",
        "dpdp_erase", "import_data", "admin",
        "fleet.read", "fleet.write", "branch.write", "branch.transfer", "compliance.write",
        "customer.read", "customer.write", "customer.export", "customer.erase",
        "booking.read", "booking.write", "booking.override_rate", "booking.approve_discount",
        "payment.read", "payment.write", "payment.refund",
        "invoice.read", "invoice.issue", "credit_note.issue", "shift.reconcile",
        "maintenance.read", "maintenance.write", "damage.read", "damage.write",
        "signature.write", "dashboard.read", "import.write", "backup.restore", "user.manage",
    },
    "manager": {
        "read", "write_booking", "write_customer", "write_payment", "write_vehicle",
        "write_maintenance", "write_damage", "approve_override", "issue_invoice",
        "issue_credit_note", "reconcile_shift", "manage_branches", "import_data",
        "fleet.read", "fleet.write", "branch.write", "branch.transfer", "compliance.write",
        "customer.read", "customer.write", "customer.export",
        "booking.read", "booking.write", "booking.override_rate", "booking.approve_discount",
        "payment.read", "payment.write", "payment.refund",
        "invoice.read", "invoice.issue", "credit_note.issue", "shift.reconcile",
        "maintenance.read", "maintenance.write", "damage.read", "damage.write",
        "signature.write", "dashboard.read", "import.write",
    },
    "desk_agent": {
        "read", "write_booking", "write_customer", "write_payment",
        "write_maintenance", "write_damage", "issue_invoice", "reconcile_shift",
        "fleet.read", "compliance.write",
        "customer.read", "customer.write", "customer.export",
        "booking.read", "booking.write",
        "payment.read", "payment.write",
        "invoice.read", "invoice.issue", "shift.reconcile",
        "maintenance.read", "maintenance.write", "damage.read", "damage.write",
        "signature.write",
    },
    "accountant": {
        "read", "write_payment", "issue_invoice", "issue_credit_note", "reconcile_shift",
        "fleet.read", "customer.read", "customer.export", "booking.read",
        "payment.read", "payment.write", "payment.refund",
        "invoice.read", "invoice.issue", "credit_note.issue", "shift.reconcile",
        "maintenance.read", "damage.read", "dashboard.read",
    },
    "read_only": {
        "read", "fleet.read", "customer.read", "booking.read", "payment.read",
        "invoice.read", "maintenance.read", "damage.read", "dashboard.read",
    },
}


def effective_ops_role(user: dict[str, Any] | None) -> str:
    """Resolve one of the 5 enterprise roles from a user row."""
    if not user:
        return "read_only"
    ops_role = str(user.get("ops_role") or "").strip().lower()
    if ops_role in VALID_OPS_ROLES:
        # If legacy role is 'admin' and ops_role was left at default 'desk_agent', treat as 'owner'
        if user.get("role") == "admin" and ops_role == "desk_agent":
            return "owner"
        return ops_role
    if user.get("role") == "admin":
        return "owner"
    return "desk_agent"


effective_role = effective_ops_role


def has_permission(user: dict[str, Any] | None, perm: str) -> bool:
    role = effective_ops_role(user)
    return perm in ROLE_PERMISSIONS.get(role, set())


def require_permission(user: dict[str, Any] | None, perm: str) -> str:
    role = effective_ops_role(user)
    if perm not in ROLE_PERMISSIONS.get(role, set()):
        raise PermissionError(
            f"Your role ('{role}') does not have permission for '{perm}'."
        )
    return role


# ---------------------------------------------------------------------------
# Database Schema Migration v3
# ---------------------------------------------------------------------------
ENTERPRISE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS branches (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    code       TEXT NOT NULL UNIQUE COLLATE NOCASE,
    name       TEXT NOT NULL,
    city       TEXT NOT NULL DEFAULT '',
    state      TEXT NOT NULL DEFAULT 'Maharashtra',
    gstin      TEXT NOT NULL DEFAULT '',
    address    TEXT NOT NULL DEFAULT '',
    phone      TEXT NOT NULL DEFAULT '',
    active     INTEGER NOT NULL DEFAULT 1,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS branch_transfers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id     INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    from_branch_id INTEGER NOT NULL REFERENCES branches(id),
    to_branch_id   INTEGER NOT NULL REFERENCES branches(id),
    odometer_km    REAL NOT NULL DEFAULT 0,
    fuel_level     TEXT NOT NULL DEFAULT 'Full',
    notes          TEXT NOT NULL DEFAULT '',
    transferred_by TEXT NOT NULL DEFAULT '',
    created_at     REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS vehicles (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_number            TEXT NOT NULL UNIQUE COLLATE NOCASE,
    make                  TEXT NOT NULL,
    model                 TEXT NOT NULL,
    variant               TEXT NOT NULL DEFAULT '',
    category              TEXT NOT NULL DEFAULT 'Compact SUV',
    vin                   TEXT NOT NULL DEFAULT '',
    fuel_type             TEXT NOT NULL DEFAULT 'Petrol',
    transmission          TEXT NOT NULL DEFAULT 'Manual',
    seats                 INTEGER NOT NULL DEFAULT 5,
    colour                TEXT NOT NULL DEFAULT 'White',
    purchase_date         TEXT NOT NULL DEFAULT '',
    purchase_cost         REAL NOT NULL DEFAULT 0,
    odometer_km           REAL NOT NULL DEFAULT 0,
    fuel_level            TEXT NOT NULL DEFAULT 'Full',
    branch_id             INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    daily_rate            REAL NOT NULL DEFAULT 2000,
    weekly_rate           REAL NOT NULL DEFAULT 12600,
    monthly_rate          REAL NOT NULL DEFAULT 45000,
    included_km_per_day   REAL NOT NULL DEFAULT 250,
    extra_km_rate         REAL NOT NULL DEFAULT 12,
    extra_hour_rate       REAL NOT NULL DEFAULT 200,
    security_deposit      REAL NOT NULL DEFAULT 5000,
    service_interval_km   REAL NOT NULL DEFAULT 10000,
    last_service_km       REAL NOT NULL DEFAULT 0,
    next_service_due_date TEXT NOT NULL DEFAULT '',
    status                TEXT NOT NULL DEFAULT 'available'
                          CHECK(status IN ('available','rented','in_workshop','reserved','blocked')),
    notes                 TEXT NOT NULL DEFAULT '',
    created_at            REAL NOT NULL,
    updated_at            REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_vehicles_branch_status ON vehicles(branch_id, status);

CREATE TABLE IF NOT EXISTS vehicle_compliance (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id     INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    doc_type       TEXT NOT NULL CHECK(doc_type IN ('insurance','puc','fitness','permit','fastag','road_tax')),
    doc_number     TEXT NOT NULL DEFAULT '',
    provider       TEXT NOT NULL DEFAULT '',
    issue_date     TEXT NOT NULL DEFAULT '',
    expiry_date    TEXT NOT NULL DEFAULT '',
    wallet_balance REAL NOT NULL DEFAULT 0,
    alert_days     INTEGER NOT NULL DEFAULT 30,
    notes          TEXT NOT NULL DEFAULT '',
    updated_at     REAL NOT NULL,
    UNIQUE(vehicle_id, doc_type)
);
CREATE INDEX IF NOT EXISTS idx_compliance_expiry ON vehicle_compliance(expiry_date);

CREATE TABLE IF NOT EXISTS customers (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name            TEXT NOT NULL,
    phone                TEXT NOT NULL DEFAULT '',
    email                TEXT NOT NULL DEFAULT '',
    address              TEXT NOT NULL DEFAULT '',
    company_name         TEXT NOT NULL DEFAULT '',
    gstin                TEXT NOT NULL DEFAULT '',
    dl_number            TEXT NOT NULL DEFAULT '',
    dl_expiry            TEXT NOT NULL DEFAULT '',
    dl_state             TEXT NOT NULL DEFAULT '',
    dl_photo_data        TEXT NOT NULL DEFAULT '',
    id_proof_type        TEXT NOT NULL DEFAULT '',
    id_proof_number      TEXT NOT NULL DEFAULT '',
    id_photo_data        TEXT NOT NULL DEFAULT '',
    dpdp_consent         INTEGER NOT NULL DEFAULT 0,
    dpdp_consent_purpose TEXT NOT NULL DEFAULT '',
    dpdp_consent_at      REAL NOT NULL DEFAULT 0,
    dpdp_consent_by      TEXT NOT NULL DEFAULT '',
    dpdp_erased          INTEGER NOT NULL DEFAULT 0,
    dpdp_erased_at       REAL NOT NULL DEFAULT 0,
    retention_until      TEXT NOT NULL DEFAULT '',
    notes                TEXT NOT NULL DEFAULT '',
    created_at           REAL NOT NULL,
    updated_at           REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers(phone);
CREATE INDEX IF NOT EXISTS idx_customers_dl ON customers(dl_number);

CREATE TABLE IF NOT EXISTS pii_access_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    user_id     INTEGER,
    actor       TEXT NOT NULL DEFAULT '',
    action      TEXT NOT NULL,
    purpose     TEXT NOT NULL DEFAULT '',
    ip          TEXT NOT NULL DEFAULT '',
    created_at  REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pii_log_cust ON pii_access_log(customer_id, created_at DESC);

CREATE TABLE IF NOT EXISTS drivers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    phone           TEXT NOT NULL DEFAULT '',
    dl_number       TEXT NOT NULL DEFAULT '',
    dl_expiry       TEXT NOT NULL DEFAULT '',
    badge_number    TEXT NOT NULL DEFAULT '',
    languages       TEXT NOT NULL DEFAULT 'Hindi, English',
    daily_allowance REAL NOT NULL DEFAULT 600,
    branch_id       INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    status          TEXT NOT NULL DEFAULT 'available'
                    CHECK(status IN ('available','on_trip','off_duty','inactive')),
    created_at      REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_ref              TEXT NOT NULL UNIQUE,
    branch_id                INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    return_branch_id         INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    vehicle_id               INTEGER NOT NULL REFERENCES vehicles(id),
    customer_id              INTEGER NOT NULL REFERENCES customers(id),
    driver_id                INTEGER REFERENCES drivers(id),
    service_mode             TEXT NOT NULL DEFAULT 'Self-Drive Daily',
    status                   TEXT NOT NULL DEFAULT 'enquiry'
                             CHECK(status IN ('enquiry','confirmed','picked_up','returned','closed','cancelled','no_show')),
    pickup_at                TEXT NOT NULL,
    return_at                TEXT NOT NULL,
    actual_pickup_at         TEXT NOT NULL DEFAULT '',
    actual_return_at         TEXT NOT NULL DEFAULT '',
    odometer_out             REAL NOT NULL DEFAULT 0,
    odometer_in              REAL NOT NULL DEFAULT 0,
    fuel_out                 TEXT NOT NULL DEFAULT 'Full',
    fuel_in                  TEXT NOT NULL DEFAULT 'Full',
    daily_rate               REAL NOT NULL DEFAULT 0,
    weekend_days             REAL NOT NULL DEFAULT 0,
    weekend_surge_pct        REAL NOT NULL DEFAULT 0,
    seasonal_surge_pct       REAL NOT NULL DEFAULT 0,
    long_term_discount_pct   REAL NOT NULL DEFAULT 0,
    discount_amount          REAL NOT NULL DEFAULT 0,
    rate_override_reason     TEXT NOT NULL DEFAULT '',
    rate_approved_by         TEXT NOT NULL DEFAULT '',
    included_km_per_day      REAL NOT NULL DEFAULT 250,
    extra_km_rate            REAL NOT NULL DEFAULT 12,
    extra_hours              REAL NOT NULL DEFAULT 0,
    extra_hour_rate          REAL NOT NULL DEFAULT 200,
    driver_allowance_per_day REAL NOT NULL DEFAULT 0,
    toll_parking             REAL NOT NULL DEFAULT 0,
    fuel_charge              REAL NOT NULL DEFAULT 0,
    damage_charge            REAL NOT NULL DEFAULT 0,
    gst_percent              REAL NOT NULL DEFAULT 5,
    inter_state              INTEGER NOT NULL DEFAULT 0,
    security_deposit         REAL NOT NULL DEFAULT 5000,
    cancellation_fee         REAL NOT NULL DEFAULT 0,
    refund_due               REAL NOT NULL DEFAULT 0,
    cancel_reason            TEXT NOT NULL DEFAULT '',
    notes                    TEXT NOT NULL DEFAULT '',
    created_by               INTEGER,
    created_at               REAL NOT NULL,
    updated_at               REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bookings_vehicle_dates ON bookings(vehicle_id, status, pickup_at, return_at);
CREATE INDEX IF NOT EXISTS idx_bookings_customer ON bookings(customer_id);

CREATE TABLE IF NOT EXISTS payments (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id       INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    branch_id        INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    kind             TEXT NOT NULL
                     CHECK(kind IN ('advance','deposit','partial','settlement','refund','deposit_refund','cancellation_refund')),
    amount           REAL NOT NULL,
    mode             TEXT NOT NULL CHECK(mode IN ('UPI','Cash','Card','NEFT','RTGS','Cheque')),
    reference_no     TEXT NOT NULL DEFAULT '',
    notes            TEXT NOT NULL DEFAULT '',
    recorded_by      INTEGER,
    recorded_by_name TEXT NOT NULL DEFAULT '',
    created_at       REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_payments_booking ON payments(booking_id, created_at);

CREATE TABLE IF NOT EXISTS invoice_counters (
    fy          TEXT PRIMARY KEY,
    last_seq    INTEGER NOT NULL DEFAULT 0,
    last_cn_seq INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS invoices (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number     TEXT NOT NULL UNIQUE,
    fy                 TEXT NOT NULL,
    seq_no             INTEGER NOT NULL,
    booking_id         INTEGER NOT NULL REFERENCES bookings(id),
    customer_id        INTEGER NOT NULL REFERENCES customers(id),
    branch_id          INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    customer_name      TEXT NOT NULL,
    customer_gstin     TEXT NOT NULL DEFAULT '',
    place_of_supply    TEXT NOT NULL DEFAULT 'Maharashtra',
    sac_code           TEXT NOT NULL DEFAULT '996601',
    vehicle_reg        TEXT NOT NULL DEFAULT '',
    taxable_amount     REAL NOT NULL,
    gst_percent        REAL NOT NULL,
    cgst_amount        REAL NOT NULL,
    sgst_amount        REAL NOT NULL,
    igst_amount        REAL NOT NULL,
    non_taxable_amount REAL NOT NULL DEFAULT 0,
    grand_total        REAL NOT NULL,
    line_items_json    TEXT NOT NULL DEFAULT '[]',
    issued_by          INTEGER,
    issued_by_name     TEXT NOT NULL DEFAULT '',
    issued_at          REAL NOT NULL,
    UNIQUE(fy, seq_no)
);

CREATE TRIGGER IF NOT EXISTS trg_invoices_no_update
BEFORE UPDATE ON invoices
BEGIN
    SELECT RAISE(ABORT, 'GST invoices are immutable after issue. Issue a Credit Note for adjustments.');
END;

CREATE TRIGGER IF NOT EXISTS trg_invoices_no_delete
BEFORE DELETE ON invoices
BEGIN
    SELECT RAISE(ABORT, 'GST invoices cannot be deleted after issue. Issue a Credit Note instead.');
END;

CREATE TABLE IF NOT EXISTS credit_notes (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    credit_note_number TEXT NOT NULL UNIQUE,
    fy                 TEXT NOT NULL,
    seq_no             INTEGER NOT NULL,
    invoice_id         INTEGER NOT NULL REFERENCES invoices(id),
    invoice_number     TEXT NOT NULL,
    reason             TEXT NOT NULL,
    taxable_reversal   REAL NOT NULL,
    gst_percent        REAL NOT NULL,
    cgst_reversal      REAL NOT NULL,
    sgst_reversal      REAL NOT NULL,
    igst_reversal      REAL NOT NULL,
    total_reversal     REAL NOT NULL,
    approved_by        TEXT NOT NULL DEFAULT '',
    issued_by          INTEGER,
    issued_by_name     TEXT NOT NULL DEFAULT '',
    issued_at          REAL NOT NULL,
    UNIQUE(fy, seq_no)
);

CREATE TRIGGER IF NOT EXISTS trg_cn_no_update
BEFORE UPDATE ON credit_notes
BEGIN
    SELECT RAISE(ABORT, 'Credit notes are immutable after issue.');
END;

CREATE TRIGGER IF NOT EXISTS trg_cn_no_delete
BEFORE DELETE ON credit_notes
BEGIN
    SELECT RAISE(ABORT, 'Credit notes cannot be deleted after issue.');
END;

CREATE TABLE IF NOT EXISTS maintenance_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    job_card_no    TEXT NOT NULL UNIQUE,
    vehicle_id     INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    branch_id      INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    service_type   TEXT NOT NULL DEFAULT 'Periodic Service',
    workshop_name  TEXT NOT NULL DEFAULT '',
    odometer_km    REAL NOT NULL DEFAULT 0,
    scheduled_date TEXT NOT NULL DEFAULT '',
    completed_date TEXT NOT NULL DEFAULT '',
    next_due_km    REAL NOT NULL DEFAULT 0,
    next_due_date  TEXT NOT NULL DEFAULT '',
    parts_cost     REAL NOT NULL DEFAULT 0,
    labour_cost    REAL NOT NULL DEFAULT 0,
    total_cost     REAL NOT NULL DEFAULT 0,
    status         TEXT NOT NULL DEFAULT 'scheduled'
                   CHECK(status IN ('scheduled','in_progress','completed','cancelled')),
    notes          TEXT NOT NULL DEFAULT '',
    created_by     INTEGER,
    created_at     REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_maint_vehicle ON maintenance_logs(vehicle_id, status);

CREATE TABLE IF NOT EXISTS damage_records (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_id            INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    booking_id            INTEGER REFERENCES bookings(id) ON DELETE SET NULL,
    panel_location        TEXT NOT NULL,
    severity              TEXT NOT NULL DEFAULT 'scratch'
                          CHECK(severity IN ('scratch','dent','crack','interior','mechanical','major')),
    description           TEXT NOT NULL DEFAULT '',
    photo_data            TEXT NOT NULL DEFAULT '',
    annotation_json       TEXT NOT NULL DEFAULT '[]',
    annotated_photo_data  TEXT NOT NULL DEFAULT '',
    estimated_cost        REAL NOT NULL DEFAULT 0,
    deducted_from_deposit REAL NOT NULL DEFAULT 0,
    status                TEXT NOT NULL DEFAULT 'open'
                          CHECK(status IN ('open','repaired','waived','charged')),
    logged_by             TEXT NOT NULL DEFAULT '',
    created_at            REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_damage_vehicle ON damage_records(vehicle_id, created_at DESC);

CREATE TABLE IF NOT EXISTS signatures (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id     INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    doc_kind       TEXT NOT NULL CHECK(doc_kind IN ('agreement','handover','return','damage_notice')),
    signer_role    TEXT NOT NULL CHECK(signer_role IN ('customer','operator','driver','manager')),
    signer_name    TEXT NOT NULL,
    signature_data TEXT NOT NULL,
    doc_hash       TEXT NOT NULL,
    ip             TEXT NOT NULL DEFAULT '',
    signed_at      REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sig_booking ON signatures(booking_id);

CREATE TABLE IF NOT EXISTS shift_reconciliations (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_id             INTEGER NOT NULL DEFAULT 1 REFERENCES branches(id),
    shift_date            TEXT NOT NULL,
    operator_id           INTEGER,
    operator_name         TEXT NOT NULL DEFAULT '',
    opening_cash          REAL NOT NULL DEFAULT 0,
    cash_collected        REAL NOT NULL DEFAULT 0,
    cash_refunded         REAL NOT NULL DEFAULT 0,
    expected_closing_cash REAL NOT NULL DEFAULT 0,
    actual_closing_cash   REAL NOT NULL DEFAULT 0,
    cash_variance         REAL NOT NULL DEFAULT 0,
    upi_collected         REAL NOT NULL DEFAULT 0,
    card_collected        REAL NOT NULL DEFAULT 0,
    bank_collected        REAL NOT NULL DEFAULT 0,
    total_refunds         REAL NOT NULL DEFAULT 0,
    notes                 TEXT NOT NULL DEFAULT '',
    closed_at             REAL NOT NULL
);
"""


def _exec_ddl_preserve_tx(conn: sqlite3.Connection, script: str) -> None:
    """Execute a multi-statement SQL DDL script without calling conn.executescript(),
    because executescript() issues an implicit COMMIT in Python's sqlite3 module."""
    buf: list[str] = []
    in_trigger = False
    for line in script.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        upper = stripped.upper()
        if upper.startswith("CREATE TRIGGER"):
            in_trigger = True
        buf.append(line)
        if in_trigger:
            if upper == "END;" or upper.endswith(" END;"):
                conn.execute("\n".join(buf))
                buf.clear()
                in_trigger = False
        elif stripped.endswith(";"):
            conn.execute("\n".join(buf))
            buf.clear()
    if buf:
        conn.execute("\n".join(buf))


def migrate_v3(conn: sqlite3.Connection) -> None:
    """Migration 3: Enterprise Car Rental Fleet, Booking, Compliance, GST & Audit tables."""
    _exec_ddl_preserve_tx(conn, ENTERPRISE_SCHEMA_SQL)
    user_cols = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "ops_role" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN ops_role TEXT NOT NULL DEFAULT 'desk_agent'")
        conn.execute("UPDATE users SET ops_role='owner' WHERE role='admin'")
    if "branch_id" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN branch_id INTEGER NOT NULL DEFAULT 1")

    audit_cols = {r[1] for r in conn.execute("PRAGMA table_info(audit)").fetchall()}
    for col in ("entity_type", "entity_id", "old_value", "new_value", "reason"):
        if col not in audit_cols:
            conn.execute(f"ALTER TABLE audit ADD COLUMN {col} TEXT NOT NULL DEFAULT ''")

    conn.execute(
        """INSERT OR IGNORE INTO branches(id, code, name, city, state, gstin, address, phone, active, created_at)
           VALUES(1, 'HQ-MAIN', 'Main Branch / Airport Counter', 'Mumbai', 'Maharashtra', '', '', '', 1, ?)""",
        (time.time(),),
    )


# ---------------------------------------------------------------------------
# Decimal Money & Exact GST / Tariff Math
# ---------------------------------------------------------------------------
TWO_PLACES = Decimal("0.01")
ONE_PLACE = Decimal("0.1")


def _dec(val: Any, default: str = "0.00") -> Decimal:
    if val is None or val == "" or isinstance(val, bool):
        return Decimal(default)
    try:
        d = Decimal(str(val))
        if not d.is_finite():
            return Decimal(default)
        return d
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


def money(val: Any) -> Decimal:
    return _dec(val).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def calculate_tariff_exact(payload: dict[str, Any]) -> dict[str, Any]:
    """Deterministic, Decimal-exact rental tariff, GST (CGST+SGST / IGST), and deposit engine.

    Rejects negative inputs when ``strict=True`` is passed; clamps to >= 0 otherwise for
    backward compatibility with legacy chat tool calls.
    """
    strict = bool(payload.get("strict", False))
    numeric_fields = (
        "days", "daily_rate", "included_km_per_day", "actual_km", "extra_km_rate",
        "extra_hours", "extra_hour_rate", "driver_allowance_per_day", "toll_parking",
        "fuel_charge", "damage_charge", "discount_amount", "gst_percent",
        "security_deposit", "weekend_days", "weekend_surge_pct", "seasonal_surge_pct",
        "long_term_discount_pct",
    )
    if strict:
        for k in numeric_fields:
            if k in payload and payload[k] not in (None, ""):
                d = _dec(payload[k], "NaN")
                if d < Decimal("0"):
                    raise ValueError(f"'{k}' cannot be negative ({payload[k]}).")

    vehicle = str(payload.get("vehicle") or "Vehicle").strip() or "Vehicle"
    days = max(Decimal("0"), _dec(payload.get("days"), "1"))
    daily_rate = max(Decimal("0"), _dec(payload.get("daily_rate"), "0"))
    inc_km_day = max(Decimal("0"), _dec(payload.get("included_km_per_day"), "250"))
    actual_km = max(Decimal("0"), _dec(payload.get("actual_km"), "0"))
    extra_km_rate = max(Decimal("0"), _dec(payload.get("extra_km_rate"), "12"))
    extra_hours = max(Decimal("0"), _dec(payload.get("extra_hours"), "0"))
    extra_hour_rate = max(Decimal("0"), _dec(payload.get("extra_hour_rate"), "200"))
    driver_day = max(Decimal("0"), _dec(payload.get("driver_allowance_per_day"), "0"))
    toll_parking = max(Decimal("0"), _dec(payload.get("toll_parking"), "0"))
    fuel_charge = max(Decimal("0"), _dec(payload.get("fuel_charge"), "0"))
    damage_charge = max(Decimal("0"), _dec(payload.get("damage_charge"), "0"))
    discount = max(Decimal("0"), _dec(payload.get("discount_amount"), "0"))
    gst_pct = min(Decimal("100"), max(Decimal("0"), _dec(payload.get("gst_percent"), "5")))
    deposit = max(Decimal("0"), _dec(payload.get("security_deposit"), "5000"))

    weekend_days = min(days, max(Decimal("0"), _dec(payload.get("weekend_days"), "0")))
    weekend_surge_pct = min(
        Decimal("200"),
        max(Decimal("0"), _dec(payload.get("weekend_surge_pct") or payload.get("weekend_surge_percent"), "0")),
    )
    seasonal_surge_pct = min(
        Decimal("200"),
        max(Decimal("0"), _dec(payload.get("seasonal_surge_pct") or payload.get("seasonal_surge_percent"), "0")),
    )
    long_term_disc_pct = min(
        Decimal("100"),
        max(Decimal("0"), _dec(payload.get("long_term_discount_pct") or payload.get("long_term_discount_percent"), "0")),
    )
    inter_state = bool(payload.get("inter_state", False))

    override_rate_raw = payload.get("override_daily_rate")
    if override_rate_raw not in (None, ""):
        override_reason = str(payload.get("override_reason") or payload.get("rate_override_reason") or "").strip()
        approved_by = str(payload.get("approved_by") or payload.get("rate_approved_by") or "").strip()
        if not override_reason or not approved_by:
            raise RentalOpsError("Rate override requires both 'override_reason' and 'approved_by'.")
        daily_rate = max(Decimal("0"), _dec(override_rate_raw, "0"))

    base_rent = (days * daily_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    weekend_surge_amount = (
        weekend_days * daily_rate * (weekend_surge_pct / Decimal("100"))
    ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    seasonal_surge_amount = (
        base_rent * (seasonal_surge_pct / Decimal("100"))
    ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    long_term_discount_amount = (
        (base_rent + weekend_surge_amount + seasonal_surge_amount)
        * (long_term_disc_pct / Decimal("100"))
    ).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    included_km = (days * inc_km_day).quantize(ONE_PLACE, rounding=ROUND_HALF_UP)
    extra_km = (
        max(Decimal("0.0"), (actual_km - included_km).quantize(ONE_PLACE, rounding=ROUND_HALF_UP))
        if actual_km > Decimal("0")
        else Decimal("0.0")
    )
    extra_km_cost = (extra_km * extra_km_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    extra_hr_cost = (extra_hours * extra_hour_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    driver_cost = (days * driver_day).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    gross_taxable = (
        base_rent
        + weekend_surge_amount
        + seasonal_surge_amount
        + extra_km_cost
        + extra_hr_cost
        + driver_cost
        - long_term_discount_amount
        - discount
    )
    taxable_sub = max(Decimal("0.00"), gross_taxable.quantize(TWO_PLACES, rounding=ROUND_HALF_UP))
    gst_amount = (taxable_sub * (gst_pct / Decimal("100"))).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    if inter_state:
        cgst_amount = Decimal("0.00")
        sgst_amount = Decimal("0.00")
        igst_amount = gst_amount
    else:
        # Exact paisa split: cgst + sgst ALWAYS equals gst_amount
        cgst_amount = (gst_amount / Decimal("2")).quantize(TWO_PLACES, rounding=ROUND_FLOOR)
        sgst_amount = (gst_amount - cgst_amount).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        igst_amount = Decimal("0.00")

    non_tax_reimb = (toll_parking + fuel_charge + damage_charge).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    grand_total = (taxable_sub + gst_amount + non_tax_reimb).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    net_after_deposit = (grand_total - deposit).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return {
        "vehicle": vehicle,
        "days": float(days),
        "daily_rate": float(daily_rate),
        "effective_daily_rate": float(daily_rate),
        "base_rent": float(base_rent),
        "weekend_days": float(weekend_days),
        "weekend_surge_pct": float(weekend_surge_pct),
        "weekend_surge_percent": float(weekend_surge_pct),
        "weekend_surge_amount": float(weekend_surge_amount),
        "weekend_surge": float(weekend_surge_amount),
        "seasonal_surge_pct": float(seasonal_surge_pct),
        "seasonal_surge_percent": float(seasonal_surge_pct),
        "seasonal_surge_amount": float(seasonal_surge_amount),
        "seasonal_surge": float(seasonal_surge_amount),
        "long_term_discount_pct": float(long_term_disc_pct),
        "long_term_discount_percent": float(long_term_disc_pct),
        "long_term_discount_amount": float(long_term_discount_amount),
        "long_term_discount": float(long_term_discount_amount),
        "included_km_per_day": float(inc_km_day),
        "included_km": float(included_km),
        "actual_km": float(actual_km),
        "extra_km": float(extra_km),
        "extra_km_rate": float(extra_km_rate),
        "extra_km_cost": float(extra_km_cost),
        "extra_hours": float(extra_hours),
        "extra_hour_rate": float(extra_hour_rate),
        "extra_hr_cost": float(extra_hr_cost),
        "extra_hour_cost": float(extra_hr_cost),
        "driver_allowance_per_day": float(driver_day),
        "driver_cost": float(driver_cost),
        "discount_amount": float(discount),
        "taxable_subtotal": float(taxable_sub),
        "gst_percent": float(gst_pct),
        "inter_state": inter_state,
        "gst_amount": float(gst_amount),
        "cgst_amount": float(cgst_amount),
        "sgst_amount": float(sgst_amount),
        "igst_amount": float(igst_amount),
        "toll_parking": float(toll_parking),
        "fuel_charge": float(fuel_charge),
        "damage_charge": float(damage_charge),
        "non_taxable_reimbursement": float(non_tax_reimb),
        "non_taxable_total": float(non_tax_reimb),
        "grand_total": float(grand_total),
        "security_deposit": float(deposit),
        "payable_with_deposit": float(grand_total + deposit),
        "total_payable_at_handover": float(grand_total + deposit),
        "net_after_deposit": float(net_after_deposit),
        "balance_payable": float(max(Decimal("0.00"), net_after_deposit)),
        "refund_due": float(max(Decimal("0.00"), -net_after_deposit)),
    }


# ---------------------------------------------------------------------------
# Structured Audit Logging (with Old & New Values + Reason)
# ---------------------------------------------------------------------------
def log_sensitive_action(
    action: str = "",
    *,
    user: dict[str, Any] | None = None,
    entity_type: str = "",
    entity_id: str | int = "",
    old_value: Any = None,
    new_value: Any = None,
    old_val: Any = None,
    new_val: Any = None,
    reason: str = "",
    detail: str = "",
    ip: str = "",
    level: str = "warn",
) -> None:
    ov = old_value if old_value is not None else old_val
    nv = new_value if new_value is not None else new_val
    old_json = json.dumps(ov, default=str) if ov is not None else ""
    new_json = json.dumps(nv, default=str) if nv is not None else ""
    uid = int(user["id"]) if user and user.get("id") is not None else None
    actor = str(user.get("name") or user.get("email") or "system") if user else "system"
    summary = detail or (f"{entity_type}#{entity_id}" + (f" ({reason})" if reason else ""))
    with db.cursor() as conn:
        conn.execute(
            """INSERT INTO audit(user_id, actor, action, detail, ip, level, created_at,
                                 entity_type, entity_id, old_value, new_value, reason)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                uid,
                actor[:120],
                action[:80],
                summary[:500],
                ip[:64],
                level[:16],
                time.time(),
                str(entity_type)[:60],
                str(entity_id)[:60],
                old_json[:4000],
                new_json[:4000],
                str(reason)[:500],
            ),
        )


def checkpoint_wal() -> None:
    """Force a passive/full WAL checkpoint after critical financial writes so crash recovery is immediate."""
    with db.cursor() as conn:
        try:
            conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
        except sqlite3.Error:
            pass


# ---------------------------------------------------------------------------
# Branches & Multi-Branch Transfers
# ---------------------------------------------------------------------------
def list_branches(active_only: bool = False) -> list[dict[str, Any]]:
    sql = "SELECT * FROM branches"
    if active_only:
        sql += " WHERE active=1"
    sql += " ORDER BY id"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql).fetchall()]


def create_branch(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "manage_branches")
    code = str(data.get("code") or "").strip().upper()[:24]
    name = str(data.get("name") or "").strip()[:120]
    if not code or not name:
        raise ValueError("Branch code and branch name are required.")
    now = time.time()
    with db.cursor() as conn:
        cur = conn.execute(
            """INSERT INTO branches(code, name, city, state, gstin, address, phone, active, created_at)
               VALUES(?,?,?,?,?,?,?,1,?)""",
            (
                code,
                name,
                str(data.get("city") or "").strip()[:80],
                str(data.get("state") or "Maharashtra").strip()[:80],
                str(data.get("gstin") or "").strip().upper()[:20],
                str(data.get("address") or "").strip()[:300],
                str(data.get("phone") or "").strip()[:30],
                now,
            ),
        )
        bid = int(cur.lastrowid)
        row = dict(conn.execute("SELECT * FROM branches WHERE id=?", (bid,)).fetchone())
    log_sensitive_action("branch.create", user=user, entity_type="branch", entity_id=bid, new_value=row, ip=ip, level="info")
    return row


def transfer_vehicle_branch(
    vehicle_id: int,
    to_branch_id: int,
    odometer_km: float | None = None,
    fuel_level: str = "Full",
    notes: str = "",
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "manage_branches")
    now = time.time()
    with db.cursor() as conn:
        veh = conn.execute("SELECT * FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone()
        if not veh:
            raise ValueError("Vehicle not found.")
        target_branch = conn.execute("SELECT * FROM branches WHERE id=? AND active=1", (int(to_branch_id),)).fetchone()
        if not target_branch:
            raise ValueError("Destination branch not found or inactive.")
        old_veh = dict(veh)
        from_branch_id = int(veh["branch_id"])
        new_odo = float(odometer_km) if odometer_km is not None else float(veh["odometer_km"])
        if new_odo < float(veh["odometer_km"]):
            raise ValueError("Transfer odometer cannot be less than current vehicle odometer.")
        conn.execute(
            "UPDATE vehicles SET branch_id=?, odometer_km=?, fuel_level=?, updated_at=? WHERE id=?",
            (int(to_branch_id), new_odo, str(fuel_level)[:20], now, int(vehicle_id)),
        )
        cur = conn.execute(
            """INSERT INTO branch_transfers(vehicle_id, from_branch_id, to_branch_id, odometer_km,
                                            fuel_level, notes, transferred_by, created_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (
                int(vehicle_id),
                from_branch_id,
                int(to_branch_id),
                new_odo,
                str(fuel_level)[:20],
                str(notes)[:300],
                str((user or {}).get("name") or "admin"),
                now,
            ),
        )
        transfer = dict(conn.execute("SELECT * FROM branch_transfers WHERE id=?", (int(cur.lastrowid),)).fetchone())
        updated_veh = dict(conn.execute("SELECT * FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone())
    log_sensitive_action(
        "vehicle.transfer",
        user=user,
        entity_type="vehicle",
        entity_id=vehicle_id,
        old_value={"branch_id": from_branch_id, "odometer_km": old_veh["odometer_km"]},
        new_value={"branch_id": int(to_branch_id), "odometer_km": new_odo},
        reason=notes,
        ip=ip,
    )
    return {"transfer": transfer, "vehicle": updated_veh}


# ---------------------------------------------------------------------------
# Vehicle Master & Compliance Tracking
# ---------------------------------------------------------------------------
_REG_RE = re.compile(r"^[A-Z]{2}[-\s]?\d{1,2}[-\s]?[A-Z]{0,3}[-\s]?\d{1,4}$", re.IGNORECASE)


def normalize_reg_number(reg: str) -> str:
    cleaned = re.sub(r"[\s\-]+", "-", str(reg or "").strip().upper())
    if not cleaned or len(cleaned) < 5:
        raise ValueError("Registration number is required (e.g. MH-02-AB-1234).")
    return cleaned[:24]


def create_vehicle(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "write_vehicle")
    reg = normalize_reg_number(str(data.get("reg_number") or ""))
    make = str(data.get("make") or "").strip()[:60]
    model = str(data.get("model") or "").strip()[:60]
    if not make or not model:
        raise ValueError("Vehicle make and model are required.")
    status = str(data.get("status") or "available").strip().lower()
    if status not in VALID_VEHICLE_STATUSES:
        raise ValueError(f"Invalid vehicle status '{status}'. Must be one of {VALID_VEHICLE_STATUSES}.")
    now = time.time()
    daily_rate = float(money(data.get("daily_rate", 2000)))
    weekly_rate = float(money(data.get("weekly_rate", daily_rate * 6.3)))
    monthly_rate = float(money(data.get("monthly_rate", daily_rate * 22.5)))
    with db.cursor() as conn:
        cur = conn.execute(
            """INSERT INTO vehicles(
                reg_number, make, model, variant, category, vin, fuel_type, transmission,
                seats, colour, purchase_date, purchase_cost, odometer_km, fuel_level,
                branch_id, daily_rate, weekly_rate, monthly_rate, included_km_per_day,
                extra_km_rate, extra_hour_rate, security_deposit, service_interval_km,
                last_service_km, next_service_due_date, status, notes, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                reg,
                make,
                model,
                str(data.get("variant") or "").strip()[:60],
                str(data.get("category") or "Compact SUV").strip()[:60],
                str(data.get("vin") or "").strip().upper()[:40],
                str(data.get("fuel_type") or "Petrol").strip()[:30],
                str(data.get("transmission") or "Manual").strip()[:30],
                max(1, min(60, int(float(data.get("seats") or 5)))),
                str(data.get("colour") or "White").strip()[:30],
                str(data.get("purchase_date") or "").strip()[:20],
                float(money(data.get("purchase_cost", 0))),
                max(0.0, float(_dec(data.get("odometer_km", 0)))),
                str(data.get("fuel_level") or "Full").strip()[:20],
                int(data.get("branch_id") or 1),
                daily_rate,
                weekly_rate,
                monthly_rate,
                max(0.0, float(_dec(data.get("included_km_per_day", 250)))),
                max(0.0, float(money(data.get("extra_km_rate", 12)))),
                max(0.0, float(money(data.get("extra_hour_rate", 200)))),
                max(0.0, float(money(data.get("security_deposit", 5000)))),
                max(1000.0, float(_dec(data.get("service_interval_km", 10000)))),
                max(0.0, float(_dec(data.get("last_service_km", 0)))),
                str(data.get("next_service_due_date") or "").strip()[:20],
                status,
                str(data.get("notes") or "").strip()[:500],
                now,
                now,
            ),
        )
        vid = int(cur.lastrowid)
        row = dict(conn.execute("SELECT * FROM vehicles WHERE id=?", (vid,)).fetchone())
    log_sensitive_action("vehicle.create", user=user, entity_type="vehicle", entity_id=vid, new_value=row, ip=ip, level="info")
    return row


def update_vehicle(vehicle_id: int, data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "write_vehicle")
    allowed = {
        "make", "model", "variant", "category", "vin", "fuel_type", "transmission",
        "seats", "colour", "purchase_date", "purchase_cost", "odometer_km", "fuel_level",
        "branch_id", "daily_rate", "weekly_rate", "monthly_rate", "included_km_per_day",
        "extra_km_rate", "extra_hour_rate", "security_deposit", "service_interval_km",
        "last_service_km", "next_service_due_date", "status", "notes",
    }
    updates: dict[str, Any] = {}
    for k, v in data.items():
        if k not in allowed:
            continue
        if k == "status":
            s = str(v).strip().lower()
            if s not in VALID_VEHICLE_STATUSES:
                raise ValueError(f"Invalid vehicle status '{s}'.")
            updates[k] = s
        elif k in {"daily_rate", "weekly_rate", "monthly_rate", "extra_km_rate", "extra_hour_rate", "security_deposit", "purchase_cost"}:
            updates[k] = float(money(v))
        elif k in {"odometer_km", "included_km_per_day", "service_interval_km", "last_service_km"}:
            updates[k] = max(0.0, float(_dec(v)))
        elif k in {"seats", "branch_id"}:
            updates[k] = int(v)
        else:
            updates[k] = str(v).strip()

    with db.cursor() as conn:
        old_row = conn.execute("SELECT * FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone()
        if not old_row:
            raise ValueError("Vehicle not found.")
        old_dict = dict(old_row)
        if updates:
            updates["updated_at"] = time.time()
            cols = ", ".join(f"{k}=?" for k in updates)
            conn.execute(f"UPDATE vehicles SET {cols} WHERE id=?", (*updates.values(), int(vehicle_id)))
        new_dict = dict(conn.execute("SELECT * FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone())
    log_sensitive_action(
        "vehicle.update",
        user=user,
        entity_type="vehicle",
        entity_id=vehicle_id,
        old_value=old_dict,
        new_value=new_dict,
        reason=str(data.get("reason") or ""),
        ip=ip,
    )
    return new_dict


def list_vehicles(branch_id: int | None = None, status: str = "", category: str = "") -> list[dict[str, Any]]:
    sql = """SELECT v.*, b.name AS branch_name, b.code AS branch_code
             FROM vehicles v
             LEFT JOIN branches b ON b.id = v.branch_id
             WHERE 1=1"""
    args: list[Any] = []
    if branch_id is not None:
        sql += " AND v.branch_id=?"
        args.append(int(branch_id))
    if status:
        sql += " AND v.status=?"
        args.append(status.strip().lower())
    if category:
        sql += " AND LOWER(v.category)=LOWER(?)"
        args.append(category.strip())
    sql += " ORDER BY v.reg_number"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def upsert_vehicle_compliance(
    vehicle_id: int,
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "compliance.write")
    doc_type = str(data.get("doc_type") or "").strip().lower()
    if doc_type not in VALID_COMPLIANCE_TYPES:
        raise ValueError(f"doc_type must be one of {VALID_COMPLIANCE_TYPES}.")
    now = time.time()
    with db.cursor() as conn:
        veh = conn.execute("SELECT id, reg_number FROM vehicles WHERE id=?", (int(vehicle_id),)).fetchone()
        if not veh:
            raise ValueError("Vehicle not found.")
        conn.execute(
            """INSERT INTO vehicle_compliance(
                vehicle_id, doc_type, doc_number, provider, issue_date, expiry_date,
                wallet_balance, alert_days, notes, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(vehicle_id, doc_type) DO UPDATE SET
                doc_number=excluded.doc_number,
                provider=excluded.provider,
                issue_date=excluded.issue_date,
                expiry_date=excluded.expiry_date,
                wallet_balance=excluded.wallet_balance,
                alert_days=excluded.alert_days,
                notes=excluded.notes,
                updated_at=excluded.updated_at""",
            (
                int(vehicle_id),
                doc_type,
                str(data.get("doc_number") or "").strip()[:80],
                str(data.get("provider") or "").strip()[:120],
                str(data.get("issue_date") or "").strip()[:20],
                str(data.get("expiry_date") or "").strip()[:20],
                float(money(data.get("wallet_balance", 0))),
                max(1, int(data.get("alert_days") or 30)),
                str(data.get("notes") or "").strip()[:300],
                now,
            ),
        )
        row = dict(
            conn.execute(
                "SELECT * FROM vehicle_compliance WHERE vehicle_id=? AND doc_type=?",
                (int(vehicle_id), doc_type),
            ).fetchone()
        )
    log_sensitive_action(
        "compliance.upsert",
        user=user,
        entity_type="vehicle_compliance",
        entity_id=f"{vehicle_id}:{doc_type}",
        new_value=row,
        ip=ip,
        level="info",
    )
    return row


def list_vehicle_compliance(vehicle_id: int | None = None) -> list[dict[str, Any]]:
    sql = """SELECT c.*, v.reg_number, v.make, v.model
             FROM vehicle_compliance c
             JOIN vehicles v ON v.id = c.vehicle_id"""
    args: list[Any] = []
    if vehicle_id is not None:
        sql += " WHERE c.vehicle_id=?"
        args.append(int(vehicle_id))
    sql += " ORDER BY c.expiry_date ASC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


# ---------------------------------------------------------------------------
# Customer Master, Driving Licence Expiry & India DPDP Act 2023 Compliance
# ---------------------------------------------------------------------------
DEFAULT_DPDP_PURPOSE = (
    "Collected with explicit customer consent under Section 6 of the Digital Personal Data Protection Act, 2023 "
    "(India) for vehicle rental KYC verification, driving licence validation, insurance coverage, "
    "FASTag/traffic challan settlement, and statutory GST invoicing."
)


def create_customer(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "write_customer")
    full_name = str(data.get("full_name") or "").strip()[:120]
    if not full_name:
        raise ValueError("Customer full_name is required.")
    dpdp_consent = 1 if data.get("dpdp_consent", True) else 0
    if not dpdp_consent:
        raise ValueError(
            "Customer consent is required under the Digital Personal Data Protection Act, 2023 (DPDP Act) "
            "before storing Driving Licence and ID proof records."
        )
    now = time.time()
    retention_days = int(data.get("retention_days") or 1095)  # 3 years default operational KYC retention
    retention_until = (dt.date.today() + dt.timedelta(days=retention_days)).isoformat()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")
    with db.cursor() as conn:
        cur = conn.execute(
            """INSERT INTO customers(
                full_name, phone, email, address, company_name, gstin,
                dl_number, dl_expiry, dl_state, dl_photo_data,
                id_proof_type, id_proof_number, id_photo_data,
                dpdp_consent, dpdp_consent_purpose, dpdp_consent_at, dpdp_consent_by,
                retention_until, notes, created_at, updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                full_name,
                str(data.get("phone") or "").strip()[:30],
                str(data.get("email") or "").strip().lower()[:120],
                str(data.get("address") or "").strip()[:400],
                str(data.get("company_name") or "").strip()[:120],
                str(data.get("gstin") or "").strip().upper()[:20],
                str(data.get("dl_number") or "").strip().upper()[:40],
                str(data.get("dl_expiry") or "").strip()[:20],
                str(data.get("dl_state") or "").strip()[:40],
                str(data.get("dl_photo_data") or ""),
                str(data.get("id_proof_type") or "").strip()[:40],
                str(data.get("id_proof_number") or "").strip()[:60],
                str(data.get("id_photo_data") or ""),
                dpdp_consent,
                str(data.get("dpdp_consent_purpose") or DEFAULT_DPDP_PURPOSE)[:500],
                now,
                actor[:120],
                retention_until,
                str(data.get("notes") or "").strip()[:500],
                now,
                now,
            ),
        )
        cid = int(cur.lastrowid)
        conn.execute(
            """INSERT INTO pii_access_log(customer_id, user_id, actor, action, purpose, ip, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (cid, (user or {}).get("id"), actor, "customer.create_with_consent", "KYC onboarding", ip, now),
        )
        row = dict(conn.execute("SELECT * FROM customers WHERE id=?", (cid,)).fetchone())
    return row


def get_customer_profile(customer_id: int, user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "read")
    now = time.time()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")
    with db.cursor() as conn:
        cust = conn.execute("SELECT * FROM customers WHERE id=?", (int(customer_id),)).fetchone()
        if not cust:
            raise ValueError("Customer not found.")
        conn.execute(
            """INSERT INTO pii_access_log(customer_id, user_id, actor, action, purpose, ip, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (int(customer_id), (user or {}).get("id"), actor, "customer.view_profile", "Counter lookup", ip, now),
        )
        bookings = [
            dict(r)
            for r in conn.execute(
                """SELECT b.*, v.reg_number, v.make, v.model
                   FROM bookings b
                   JOIN vehicles v ON v.id = b.vehicle_id
                   WHERE b.customer_id=?
                   ORDER BY b.pickup_at DESC""",
                (int(customer_id),),
            ).fetchall()
        ]
        damages = [
            dict(r)
            for r in conn.execute(
                """SELECT d.*, v.reg_number
                   FROM damage_records d
                   JOIN vehicles v ON v.id = d.vehicle_id
                   JOIN bookings b ON b.id = d.booking_id
                   WHERE b.customer_id=?
                   ORDER BY d.created_at DESC""",
                (int(customer_id),),
            ).fetchall()
        ]
    out = dict(cust)
    out["repeat_bookings_count"] = len(bookings)
    out["bookings"] = bookings
    out["damage_history"] = damages
    return out


def list_customers(include_erased: bool = False) -> list[dict[str, Any]]:
    sql = """SELECT c.id, c.full_name, c.phone, c.email, c.company_name, c.gstin,
                    c.dl_number, c.dl_expiry, c.dl_state, c.id_proof_type,
                    c.dpdp_consent, c.dpdp_consent_at, c.dpdp_erased, c.retention_until,
                    (SELECT COUNT(*) FROM bookings b WHERE b.customer_id=c.id) AS total_bookings
             FROM customers c"""
    if not include_erased:
        sql += " WHERE c.dpdp_erased=0"
    sql += " ORDER BY c.full_name COLLATE NOCASE"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql).fetchall()]


def export_customer_dpdp_package(customer_id: int, user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    """DPDP Act, 2023 (Section 11) — Right to access & data portability export."""
    require_permission(user, "read")
    now = time.time()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")
    with db.cursor() as conn:
        cust = conn.execute("SELECT * FROM customers WHERE id=?", (int(customer_id),)).fetchone()
        if not cust:
            raise ValueError("Customer not found.")
        conn.execute(
            """INSERT INTO pii_access_log(customer_id, user_id, actor, action, purpose, ip, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (int(customer_id), (user or {}).get("id"), actor, "dpdp.data_export", "DPDP Section 11 portability request", ip, now),
        )
        bookings = [dict(r) for r in conn.execute("SELECT * FROM bookings WHERE customer_id=?", (int(customer_id),)).fetchall()]
        invoices = [dict(r) for r in conn.execute("SELECT * FROM invoices WHERE customer_id=?", (int(customer_id),)).fetchall()]
        access_logs = [dict(r) for r in conn.execute("SELECT * FROM pii_access_log WHERE customer_id=? ORDER BY created_at DESC", (int(customer_id),)).fetchall()]
    log_sensitive_action("dpdp.export", user=user, entity_type="customer", entity_id=customer_id, ip=ip, level="info")
    return {
        "statute": "Digital Personal Data Protection Act, 2023 (India) — Section 11 Data Summary",
        "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "customer": dict(cust),
        "bookings": bookings,
        "invoices": invoices,
        "pii_access_log": access_logs,
    }


def erase_customer_pii(
    customer_id: int,
    reason: str,
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    """DPDP Act, 2023 (Section 12) — Right to erasure / PII anonymization.

    Refuses erasure if the customer has an active ('confirmed' or 'picked_up') booking.
    Preserves immutable GST invoice rows (required for 72 months under CGST Act, 2017)
    while scrubbing all personal identifiers, licence numbers, and uploaded ID photos.
    """
    require_permission(user, "dpdp_erase")
    if not str(reason or "").strip():
        raise ValueError("A reason is required to process a DPDP erasure request.")
    now = time.time()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "owner")
    with db.cursor() as conn:
        cust = conn.execute("SELECT * FROM customers WHERE id=?", (int(customer_id),)).fetchone()
        if not cust:
            raise ValueError("Customer not found.")
        active = conn.execute(
            "SELECT id, booking_ref FROM bookings WHERE customer_id=? AND status IN ('confirmed','picked_up')",
            (int(customer_id),),
        ).fetchone()
        if active:
            raise ValueError(
                f"Cannot erase customer while booking {active['booking_ref']} is active. Close or cancel the booking first."
            )
        old_summary = {"full_name": cust["full_name"], "phone": cust["phone"], "dl_number": cust["dl_number"]}
        redacted_name = f"REDACTED-CUSTOMER-{customer_id}"
        conn.execute(
            """UPDATE customers SET
                full_name=?, phone='', email='', address='',
                dl_number='REDACTED', dl_photo_data='',
                id_proof_type='', id_proof_number='REDACTED', id_photo_data='',
                dpdp_erased=1, dpdp_erased_at=?, notes=?, updated_at=?
               WHERE id=?""",
            (redacted_name, now, f"Erased under DPDP Act 2023: {reason[:200]}", now, int(customer_id)),
        )
        conn.execute(
            """INSERT INTO pii_access_log(customer_id, user_id, actor, action, purpose, ip, created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (int(customer_id), (user or {}).get("id"), actor, "dpdp.pii_erased", reason[:200], ip, now),
        )
        updated = dict(conn.execute("SELECT * FROM customers WHERE id=?", (int(customer_id),)).fetchone())
    log_sensitive_action(
        "dpdp.erase_customer",
        user=user,
        entity_type="customer",
        entity_id=customer_id,
        old_value=old_summary,
        new_value={"full_name": redacted_name, "dpdp_erased": 1},
        reason=reason,
        ip=ip,
    )
    return updated


# ---------------------------------------------------------------------------
# Compliance & Expiry Alerts (DL + Insurance + PUC + Fitness + Permit + FASTag + Maintenance)
# ---------------------------------------------------------------------------
def compliance_and_expiry_alerts(days_ahead: int = 30, reference_date: str = "") -> dict[str, Any]:
    ref = dt.date.fromisoformat(reference_date) if reference_date else dt.date.today()
    horizon = (ref + dt.timedelta(days=max(0, int(days_ahead)))).isoformat()
    ref_iso = ref.isoformat()

    vehicle_alerts: list[dict[str, Any]] = []
    customer_dl_alerts: list[dict[str, Any]] = []
    driver_dl_alerts: list[dict[str, Any]] = []
    maintenance_alerts: list[dict[str, Any]] = []

    with db.cursor() as conn:
        comp_rows = conn.execute(
            """SELECT c.*, v.reg_number, v.make, v.model
               FROM vehicle_compliance c
               JOIN vehicles v ON v.id = c.vehicle_id
               WHERE (c.expiry_date <> '' AND c.expiry_date <= ?)
                  OR (c.doc_type = 'fastag' AND c.wallet_balance < 500)
               ORDER BY c.expiry_date ASC""",
            (horizon,),
        ).fetchall()
        for r in comp_rows:
            item = dict(r)
            exp = str(r["expiry_date"] or "")
            if r["doc_type"] == "fastag" and float(r["wallet_balance"]) < 500:
                item["severity"] = "low_balance"
            elif exp and exp < ref_iso:
                item["severity"] = "expired"
            else:
                item["severity"] = "expiring_soon"
            vehicle_alerts.append(item)

        cust_rows = conn.execute(
            """SELECT id, full_name, phone, dl_number, dl_expiry
               FROM customers
               WHERE dpdp_erased=0 AND dl_expiry <> '' AND dl_expiry <= ?
               ORDER BY dl_expiry ASC""",
            (horizon,),
        ).fetchall()
        for r in cust_rows:
            item = dict(r)
            item["severity"] = "expired" if str(r["dl_expiry"]) < ref_iso else "expiring_soon"
            customer_dl_alerts.append(item)

        drv_rows = conn.execute(
            """SELECT id, full_name, phone, dl_number, dl_expiry
               FROM drivers
               WHERE status <> 'inactive' AND dl_expiry <> '' AND dl_expiry <= ?
               ORDER BY dl_expiry ASC""",
            (horizon,),
        ).fetchall()
        for r in drv_rows:
            item = dict(r)
            item["severity"] = "expired" if str(r["dl_expiry"]) < ref_iso else "expiring_soon"
            driver_dl_alerts.append(item)

        veh_rows = conn.execute("SELECT * FROM vehicles").fetchall()
        for v in veh_rows:
            due_km = float(v["last_service_km"]) + float(v["service_interval_km"])
            cur_km = float(v["odometer_km"])
            due_date = str(v["next_service_due_date"] or "")
            if cur_km >= due_km - 500 or (due_date and due_date <= horizon):
                maintenance_alerts.append({
                    "vehicle_id": v["id"],
                    "reg_number": v["reg_number"],
                    "make": v["make"],
                    "model": v["model"],
                    "odometer_km": cur_km,
                    "service_due_km": due_km,
                    "next_service_due_date": due_date,
                    "overdue": cur_km >= due_km or (bool(due_date) and due_date < ref_iso),
                })

    return {
        "reference_date": ref_iso,
        "days_ahead": days_ahead,
        "vehicle_compliance_alerts": vehicle_alerts,
        "customer_dl_alerts": customer_dl_alerts,
        "driver_dl_alerts": driver_dl_alerts,
        "maintenance_alerts": maintenance_alerts,
        "total_alerts": (
            len(vehicle_alerts)
            + len(customer_dl_alerts)
            + len(driver_dl_alerts)
            + len(maintenance_alerts)
        ),
    }


# ---------------------------------------------------------------------------
# Drivers / Chauffeurs
# ---------------------------------------------------------------------------
def create_driver(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "write_vehicle")
    name = str(data.get("full_name") or "").strip()[:120]
    if not name:
        raise ValueError("Driver full_name is required.")
    now = time.time()
    with db.cursor() as conn:
        cur = conn.execute(
            """INSERT INTO drivers(full_name, phone, dl_number, dl_expiry, badge_number,
                                   languages, daily_allowance, branch_id, status, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                name,
                str(data.get("phone") or "").strip()[:30],
                str(data.get("dl_number") or "").strip().upper()[:40],
                str(data.get("dl_expiry") or "").strip()[:20],
                str(data.get("badge_number") or "").strip()[:40],
                str(data.get("languages") or "Hindi, English").strip()[:120],
                float(money(data.get("daily_allowance", 600))),
                int(data.get("branch_id") or 1),
                str(data.get("status") or "available").strip().lower(),
                now,
            ),
        )
        row = dict(conn.execute("SELECT * FROM drivers WHERE id=?", (int(cur.lastrowid),)).fetchone())
    return row


def list_drivers(branch_id: int | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM drivers"
    args: list[Any] = []
    if branch_id is not None:
        sql += " WHERE branch_id=?"
        args.append(int(branch_id))
    sql += " ORDER BY full_name COLLATE NOCASE"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


# ---------------------------------------------------------------------------
# Booking Calendar, Overlap Detection, Lifecycle & Availability Search
# ---------------------------------------------------------------------------
def _parse_iso_dt(value: str, field_name: str = "timestamp") -> dt.datetime:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError(f"{field_name} is required (ISO format YYYY-MM-DD or YYYY-MM-DDTHH:MM).")
    if len(raw) == 10:
        raw += "T09:00:00"
    raw = raw.replace(" ", "T")
    if raw.endswith("Z"):
        raw = raw[:-1]
    try:
        return dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"Invalid {field_name} '{value}'. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM.") from exc


def check_booking_conflicts(
    conn: sqlite3.Connection,
    vehicle_id: int,
    pickup_iso: str,
    return_iso: str,
    *,
    driver_id: int | None = None,
    exclude_booking_id: int | None = None,
) -> list[dict[str, Any]]:
    """Return any overlapping active bookings ('confirmed' or 'picked_up') for the vehicle or driver."""
    sql = """SELECT id, booking_ref, vehicle_id, driver_id, status, pickup_at, return_at
             FROM bookings
             WHERE status IN ('confirmed', 'picked_up')
               AND pickup_at < ?
               AND return_at > ?"""
    args: list[Any] = [return_iso, pickup_iso]
    if exclude_booking_id is not None:
        sql += " AND id <> ?"
        args.append(int(exclude_booking_id))
    rows = conn.execute(sql, args).fetchall()
    conflicts: list[dict[str, Any]] = []
    for r in rows:
        if int(r["vehicle_id"]) == int(vehicle_id):
            conflicts.append({"kind": "vehicle", **dict(r)})
        elif driver_id is not None and r["driver_id"] is not None and int(r["driver_id"]) == int(driver_id):
            conflicts.append({"kind": "driver", **dict(r)})
    return conflicts


def search_available_vehicles(
    pickup_at: str,
    return_at: str,
    *,
    category: str = "",
    branch_id: int | None = None,
) -> list[dict[str, Any]]:
    p_dt = _parse_iso_dt(pickup_at, "pickup_at")
    r_dt = _parse_iso_dt(return_at, "return_at")
    if r_dt <= p_dt:
        raise ValueError("return_at must be after pickup_at.")
    p_iso, r_iso = p_dt.isoformat(timespec="minutes"), r_dt.isoformat(timespec="minutes")
    ret_date = r_dt.date().isoformat()

    with db.cursor() as conn:
        sql = """SELECT v.*, b.name AS branch_name
                 FROM vehicles v
                 LEFT JOIN branches b ON b.id = v.branch_id
                 WHERE v.status IN ('available', 'reserved')"""
        args: list[Any] = []
        if branch_id is not None:
            sql += " AND v.branch_id=?"
            args.append(int(branch_id))
        if category:
            sql += " AND LOWER(v.category)=LOWER(?)"
            args.append(category.strip())
        sql += " ORDER BY v.daily_rate ASC, v.reg_number ASC"
        candidates = [dict(r) for r in conn.execute(sql, args).fetchall()]

        available: list[dict[str, Any]] = []
        for veh in candidates:
            vid = int(veh["id"])
            if check_booking_conflicts(conn, vid, p_iso, r_iso):
                continue
            # Also flag if any mandatory compliance document expires before return_date
            expired_comp = conn.execute(
                """SELECT doc_type, expiry_date FROM vehicle_compliance
                   WHERE vehicle_id=? AND doc_type IN ('insurance','puc','fitness','permit')
                     AND expiry_date <> '' AND expiry_date < ?""",
                (vid, ret_date),
            ).fetchall()
            veh["compliance_warnings"] = [dict(c) for c in expired_comp]
            available.append(veh)
    return available


def create_booking(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "write_booking")
    vehicle_id = int(data.get("vehicle_id") or 0)
    customer_id = int(data.get("customer_id") or 0)
    if not vehicle_id or not customer_id:
        raise ValueError("vehicle_id and customer_id are required.")

    p_dt = _parse_iso_dt(str(data.get("pickup_at") or ""), "pickup_at")
    r_dt = _parse_iso_dt(str(data.get("return_at") or data.get("expected_return_at") or ""), "return_at")
    if r_dt <= p_dt:
        raise ValueError("return_at must be strictly after pickup_at.")
    p_iso = p_dt.isoformat(timespec="minutes")
    r_iso = r_dt.isoformat(timespec="minutes")

    status = str(data.get("status") or "confirmed").strip().lower()
    if status not in VALID_BOOKING_STATUSES:
        raise ValueError(f"Invalid booking status '{status}'.")

    driver_id = int(data["driver_id"]) if data.get("driver_id") not in (None, "", 0, "0") else None
    now = time.time()

    with db.cursor() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            veh = conn.execute("SELECT * FROM vehicles WHERE id=?", (vehicle_id,)).fetchone()
            if not veh:
                raise ValueError("Vehicle not found.")
            if veh["status"] in ("in_workshop", "blocked") and status in ("confirmed", "picked_up"):
                raise ValueError(f"Vehicle {veh['reg_number']} is currently '{veh['status']}' and cannot be booked.")

            cust = conn.execute("SELECT * FROM customers WHERE id=?", (customer_id,)).fetchone()
            if not cust:
                raise ValueError("Customer not found.")
            if cust["dpdp_erased"]:
                raise ValueError("Customer PII has been erased; create a new customer profile with consent.")

            # Driving licence expiry validation for self-drive bookings
            service_mode = str(data.get("service_mode") or "Self-Drive Daily").strip()
            if "chauffeur" not in service_mode.lower() and cust["dl_expiry"]:
                if str(cust["dl_expiry"]) < r_dt.date().isoformat():
                    raise ValueError(
                        f"Customer Driving Licence ({cust['dl_number']}) expires on {cust['dl_expiry']}, "
                        f"before the trip return date ({r_dt.date().isoformat()})."
                    )

            if status in ("confirmed", "picked_up"):
                conflicts = check_booking_conflicts(conn, vehicle_id, p_iso, r_iso, driver_id=driver_id)
                if conflicts:
                    c = conflicts[0]
                    raise ValueError(
                        f"Overlap detected: {c['kind']} is already booked on {c['booking_ref']} "
                        f"({c['pickup_at']} to {c['return_at']})."
                    )

            std_rate = float(veh["daily_rate"])
            req_rate = float(money(data.get("daily_rate", std_rate)))
            discount = float(money(data.get("discount_amount", 0)))
            override_reason = str(data.get("rate_override_reason") or "").strip()
            approved_by = str(data.get("rate_approved_by") or "").strip()

            if (abs(req_rate - std_rate) > 0.01 or discount > 0) and not override_reason:
                raise ValueError(
                    "A rate_override_reason (and approving manager/owner) is required when overriding the vehicle's standard daily rate or applying a manual discount."
                )

            seq = int(conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]) + 1
            booking_ref = str(data.get("booking_ref") or f"BK-{dt.date.today().strftime('%Y%m')}-{seq:04d}")
            branch_id = int(data.get("branch_id") or veh["branch_id"] or 1)
            return_branch_id = int(data.get("return_branch_id") or branch_id)

            cur = conn.execute(
                """INSERT INTO bookings(
                    booking_ref, branch_id, return_branch_id, vehicle_id, customer_id, driver_id,
                    service_mode, status, pickup_at, return_at, odometer_out, fuel_out,
                    daily_rate, weekend_days, weekend_surge_pct, seasonal_surge_pct,
                    long_term_discount_pct, discount_amount, rate_override_reason, rate_approved_by,
                    included_km_per_day, extra_km_rate, extra_hours, extra_hour_rate,
                    driver_allowance_per_day, toll_parking, fuel_charge, damage_charge,
                    gst_percent, inter_state, security_deposit, notes, created_by, created_at, updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    booking_ref,
                    branch_id,
                    return_branch_id,
                    vehicle_id,
                    customer_id,
                    driver_id,
                    service_mode,
                    status,
                    p_iso,
                    r_iso,
                    float(_dec(data.get("odometer_out", veh["odometer_km"]))),
                    str(data.get("fuel_out") or veh["fuel_level"] or "Full"),
                    req_rate,
                    float(_dec(data.get("weekend_days", 0))),
                    float(_dec(data.get("weekend_surge_pct", 0))),
                    float(_dec(data.get("seasonal_surge_pct", 0))),
                    float(_dec(data.get("long_term_discount_pct", 0))),
                    discount,
                    override_reason[:300],
                    approved_by[:120],
                    float(_dec(data.get("included_km_per_day", veh["included_km_per_day"]))),
                    float(money(data.get("extra_km_rate", veh["extra_km_rate"]))),
                    float(_dec(data.get("extra_hours", 0))),
                    float(money(data.get("extra_hour_rate", veh["extra_hour_rate"]))),
                    float(money(data.get("driver_allowance_per_day", 0))),
                    float(money(data.get("toll_parking", 0))),
                    float(money(data.get("fuel_charge", 0))),
                    float(money(data.get("damage_charge", 0))),
                    float(_dec(data.get("gst_percent", 5))),
                    1 if data.get("inter_state") else 0,
                    float(money(data.get("security_deposit", veh["security_deposit"]))),
                    str(data.get("notes") or "").strip()[:500],
                    (user or {}).get("id"),
                    now,
                    now,
                ),
            )
            bid = int(cur.lastrowid)
            if status == "picked_up":
                conn.execute("UPDATE vehicles SET status='rented', updated_at=? WHERE id=?", (now, vehicle_id))
            row = dict(conn.execute("SELECT * FROM bookings WHERE id=?", (bid,)).fetchone())
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    if override_reason:
        log_sensitive_action(
            "booking.rate_override",
            user=user,
            entity_type="booking",
            entity_id=bid,
            old_value={"standard_daily_rate": std_rate, "discount_amount": 0},
            new_value={"daily_rate": req_rate, "discount_amount": discount, "approved_by": approved_by},
            reason=override_reason,
            ip=ip,
        )
    else:
        log_sensitive_action("booking.create", user=user, entity_type="booking", entity_id=bid, new_value=row, ip=ip, level="info")
    return row


def compute_cancellation_settlement(
    booking: dict[str, Any],
    new_status: str,
    cancelled_at_iso: str = "",
    advance_paid: float = 0.0,
    deposit_paid: float = 0.0,
) -> dict[str, float]:
    """Calculate cancellation or no-show fee and refund due deterministically.

    Rules:
    - 'no_show': 100% of 1 day tariff fee (capped at advance paid); 100% of security deposit refunded.
    - 'cancelled' >= 48h before pickup: ₹0 fee; 100% advance + deposit refunded.
    - 'cancelled' 24h..48h before pickup: 25% of 1 day tariff fee; remainder refunded.
    - 'cancelled' < 24h before pickup: 50% of 1 day tariff fee; remainder refunded.
    """
    one_day = money(booking.get("daily_rate", 0))
    adv = money(advance_paid)
    dep = money(deposit_paid)
    total_paid = adv + dep

    if new_status == "no_show":
        fee = min(total_paid, one_day)
    else:
        p_dt = _parse_iso_dt(booking["pickup_at"], "pickup_at")
        c_dt = _parse_iso_dt(cancelled_at_iso, "cancelled_at") if cancelled_at_iso else dt.datetime.now()
        hours_before = (p_dt - c_dt).total_seconds() / 3600.0
        if hours_before >= 48.0:
            fee = Decimal("0.00")
        elif hours_before >= 24.0:
            fee = (one_day * Decimal("0.25")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        else:
            fee = (one_day * Decimal("0.50")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        fee = min(total_paid, fee)

    refund = max(Decimal("0.00"), (total_paid - fee).quantize(TWO_PLACES, rounding=ROUND_HALF_UP))
    return {"cancellation_fee": float(fee), "refund_due": float(refund), "total_paid": float(total_paid)}


def transition_booking_status(
    booking_id: int,
    new_status: str,
    data: dict[str, Any] | None = None,
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "write_booking")
    data = data or {}
    target = str(new_status or "").strip().lower()
    if target not in VALID_BOOKING_STATUSES:
        raise ValueError(f"Invalid booking status '{target}'.")

    allowed_transitions: dict[str, set[str]] = {
        "enquiry": {"confirmed", "cancelled"},
        "confirmed": {"picked_up", "cancelled", "no_show"},
        "picked_up": {"returned"},
        "returned": {"closed"},
        "closed": set(),
        "cancelled": set(),
        "no_show": set(),
    }
    now = time.time()
    now_iso = dt.datetime.now().isoformat(timespec="minutes")

    with db.cursor() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute("SELECT * FROM bookings WHERE id=?", (int(booking_id),)).fetchone()
            if not row:
                raise ValueError("Booking not found.")
            old_booking = dict(row)
            cur_status = old_booking["status"]
            if target != cur_status and target not in allowed_transitions.get(cur_status, set()):
                raise ValueError(f"Cannot transition booking from '{cur_status}' to '{target}'.")

            vid = int(old_booking["vehicle_id"])
            if target in ("confirmed", "picked_up"):
                conflicts = check_booking_conflicts(
                    conn,
                    vid,
                    old_booking["pickup_at"],
                    old_booking["return_at"],
                    driver_id=old_booking["driver_id"],
                    exclude_booking_id=int(booking_id),
                )
                if conflicts:
                    raise ValueError(f"Vehicle overlap with booking {conflicts[0]['booking_ref']}.")

            updates: dict[str, Any] = {"status": target, "updated_at": now}
            if target == "picked_up":
                updates["actual_pickup_at"] = str(data.get("actual_pickup_at") or now_iso)
                if "odometer_out" in data:
                    updates["odometer_out"] = float(_dec(data["odometer_out"]))
                if "fuel_out" in data:
                    updates["fuel_out"] = str(data["fuel_out"])[:20]
                conn.execute("UPDATE vehicles SET status='rented', updated_at=? WHERE id=?", (now, vid))
                if old_booking["driver_id"]:
                    conn.execute("UPDATE drivers SET status='on_trip' WHERE id=?", (int(old_booking["driver_id"]),))

            elif target in ("returned", "closed"):
                if target == "returned":
                    updates["actual_return_at"] = str(data.get("actual_return_at") or now_iso)
                if "odometer_in" in data:
                    odo_in = float(_dec(data["odometer_in"]))
                    if odo_in < float(old_booking["odometer_out"]):
                        raise ValueError("Return odometer_in cannot be less than pickup odometer_out.")
                    updates["odometer_in"] = odo_in
                    conn.execute(
                        "UPDATE vehicles SET odometer_km=?, branch_id=?, status='available', updated_at=? WHERE id=?",
                        (odo_in, int(old_booking["return_branch_id"]), now, vid),
                    )
                else:
                    conn.execute(
                        "UPDATE vehicles SET branch_id=?, status='available', updated_at=? WHERE id=?",
                        (int(old_booking["return_branch_id"]), now, vid),
                    )
                for k in ("fuel_in", "extra_hours", "toll_parking", "fuel_charge", "damage_charge"):
                    if k in data:
                        updates[k] = str(data[k])[:20] if k == "fuel_in" else float(money(data[k]))
                if old_booking["driver_id"]:
                    conn.execute("UPDATE drivers SET status='available' WHERE id=?", (int(old_booking["driver_id"]),))

            elif target in ("cancelled", "no_show"):
                paid_rows = conn.execute(
                    "SELECT kind, amount FROM payments WHERE booking_id=?", (int(booking_id),)
                ).fetchall()
                adv_paid = sum(float(r["amount"]) for r in paid_rows if r["kind"] in ("advance", "partial", "settlement"))
                dep_paid = sum(float(r["amount"]) for r in paid_rows if r["kind"] == "deposit")
                settlement = compute_cancellation_settlement(
                    old_booking,
                    target,
                    cancelled_at_iso=str(data.get("cancelled_at") or ""),
                    advance_paid=adv_paid,
                    deposit_paid=dep_paid,
                )
                updates["cancellation_fee"] = settlement["cancellation_fee"]
                updates["refund_due"] = settlement["refund_due"]
                updates["cancel_reason"] = str(data.get("cancel_reason") or target)[:300]
                conn.execute("UPDATE vehicles SET status='available', updated_at=? WHERE id=?", (now, vid))
                if old_booking["driver_id"]:
                    conn.execute("UPDATE drivers SET status='available' WHERE id=?", (int(old_booking["driver_id"]),))

            cols = ", ".join(f"{k}=?" for k in updates)
            conn.execute(f"UPDATE bookings SET {cols} WHERE id=?", (*updates.values(), int(booking_id)))
            updated = dict(conn.execute("SELECT * FROM bookings WHERE id=?", (int(booking_id),)).fetchone())
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    log_sensitive_action(
        f"booking.{target}",
        user=user,
        entity_type="booking",
        entity_id=booking_id,
        old_value={"status": old_booking["status"]},
        new_value={"status": target, "cancellation_fee": updated["cancellation_fee"], "refund_due": updated["refund_due"]},
        reason=str(data.get("cancel_reason") or ""),
        ip=ip,
    )
    return updated


def booking_settlement_summary(booking_id: int) -> dict[str, Any]:
    with db.cursor() as conn:
        b = conn.execute(
            """SELECT b.*, v.reg_number, v.make, v.model, c.full_name AS customer_name, c.gstin AS customer_gstin
               FROM bookings b
               JOIN vehicles v ON v.id = b.vehicle_id
               JOIN customers c ON c.id = b.customer_id
               WHERE b.id=?""",
            (int(booking_id),),
        ).fetchone()
        if not b:
            raise ValueError("Booking not found.")
        payments = [dict(r) for r in conn.execute("SELECT * FROM payments WHERE booking_id=? ORDER BY created_at", (int(booking_id),)).fetchall()]

    p_dt = _parse_iso_dt(b["pickup_at"])
    r_dt = _parse_iso_dt(b["return_at"])
    days = max(1.0, math.ceil((r_dt - p_dt).total_seconds() / 86400.0)) if hasattr(dt, "datetime") else 1.0
    actual_km = max(0.0, float(b["odometer_in"]) - float(b["odometer_out"])) if float(b["odometer_in"]) > float(b["odometer_out"]) else 0.0

    quote = calculate_tariff_exact({
        "vehicle": f"{b['reg_number']} ({b['make']} {b['model']})",
        "days": days,
        "daily_rate": b["daily_rate"],
        "weekend_days": b["weekend_days"],
        "weekend_surge_pct": b["weekend_surge_pct"],
        "seasonal_surge_pct": b["seasonal_surge_pct"],
        "long_term_discount_pct": b["long_term_discount_pct"],
        "included_km_per_day": b["included_km_per_day"],
        "actual_km": actual_km,
        "extra_km_rate": b["extra_km_rate"],
        "extra_hours": b["extra_hours"],
        "extra_hour_rate": b["extra_hour_rate"],
        "driver_allowance_per_day": b["driver_allowance_per_day"],
        "toll_parking": b["toll_parking"],
        "fuel_charge": b["fuel_charge"],
        "damage_charge": b["damage_charge"],
        "discount_amount": b["discount_amount"],
        "gst_percent": b["gst_percent"],
        "inter_state": bool(b["inter_state"]),
        "security_deposit": b["security_deposit"],
    })

    collected = Decimal("0.00")
    deposit_held = Decimal("0.00")
    refunded = Decimal("0.00")
    for p in payments:
        amt = money(p["amount"])
        if p["kind"] in ("advance", "partial", "settlement"):
            collected += amt
        elif p["kind"] == "deposit":
            deposit_held += amt
        elif p["kind"] in ("refund", "deposit_refund", "cancellation_refund"):
            refunded += amt

    bill_total = money(b["cancellation_fee"]) if b["status"] in ("cancelled", "no_show") else money(quote["grand_total"])
    net_received = collected + deposit_held - refunded
    net_due = (bill_total - net_received).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    return {
        "booking": dict(b),
        "quote": quote,
        "payments": payments,
        "advance_and_payments_collected": float(collected),
        "deposit_collected": float(deposit_held),
        "total_refunded": float(refunded),
        "net_received": float(net_received),
        "bill_total": float(bill_total),
        "balance_due_from_customer": float(max(Decimal("0.00"), net_due)),
        "refund_due_to_customer": float(max(Decimal("0.00"), -net_due)),
    }


import math


def list_bookings(branch_id: int | None = None, status: str = "", vehicle_id: int | None = None) -> list[dict[str, Any]]:
    sql = """SELECT b.*, v.reg_number, v.make, v.model, v.category,
                    c.full_name AS customer_name, c.phone AS customer_phone
             FROM bookings b
             JOIN vehicles v ON v.id = b.vehicle_id
             JOIN customers c ON c.id = b.customer_id
             WHERE 1=1"""
    args: list[Any] = []
    if branch_id is not None:
        sql += " AND b.branch_id=?"
        args.append(int(branch_id))
    if status:
        sql += " AND b.status=?"
        args.append(status.strip().lower())
    if vehicle_id is not None:
        sql += " AND b.vehicle_id=?"
        args.append(int(vehicle_id))
    sql += " ORDER BY b.pickup_at DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def booking_timeline_by_vehicle(branch_id: int | None = None) -> list[dict[str, Any]]:
    vehicles = list_vehicles(branch_id=branch_id)
    bookings = list_bookings(branch_id=branch_id)
    by_veh: dict[int, list[dict[str, Any]]] = {int(v["id"]): [] for v in vehicles}
    for b in bookings:
        vid = int(b["vehicle_id"])
        if vid in by_veh:
            by_veh[vid].append({
                "booking_id": b["id"],
                "booking_ref": b["booking_ref"],
                "customer_name": b["customer_name"],
                "status": b["status"],
                "pickup_at": b["pickup_at"],
                "return_at": b["return_at"],
            })
    return [
        {
            "vehicle_id": v["id"],
            "reg_number": v["reg_number"],
            "make": v["make"],
            "model": v["model"],
            "category": v["category"],
            "status": v["status"],
            "slots": by_veh.get(int(v["id"]), []),
        }
        for v in vehicles
    ]


# ---------------------------------------------------------------------------
# Payment Ledger, Immutable Sequential GST Invoices & Credit Notes
# ---------------------------------------------------------------------------
def record_payment(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    require_permission(user, "write_payment")
    booking_id = int(data.get("booking_id") or 0)
    kind = str(data.get("kind") or "advance").strip().lower()
    if kind not in VALID_PAYMENT_KINDS:
        raise ValueError(f"Payment kind must be one of {VALID_PAYMENT_KINDS}.")
    mode = str(data.get("mode") or "UPI").strip()
    if mode not in VALID_PAYMENT_MODES:
        raise ValueError(f"Payment mode must be one of {VALID_PAYMENT_MODES}.")
    amount = float(money(data.get("amount", 0)))
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")

    now = time.time()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")
    with db.cursor() as conn:
        b = conn.execute("SELECT id, branch_id, booking_ref FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if not b:
            raise ValueError("Booking not found.")
        cur = conn.execute(
            """INSERT INTO payments(booking_id, branch_id, kind, amount, mode, reference_no,
                                    notes, recorded_by, recorded_by_name, created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (
                booking_id,
                int(data.get("branch_id") or b["branch_id"] or 1),
                kind,
                amount,
                mode,
                str(data.get("reference_no") or "").strip()[:80],
                str(data.get("notes") or "").strip()[:300],
                (user or {}).get("id"),
                actor[:120],
                now,
            ),
        )
        pid = int(cur.lastrowid)
        row = dict(conn.execute("SELECT * FROM payments WHERE id=?", (pid,)).fetchone())
    checkpoint_wal()
    log_sensitive_action(
        f"payment.{kind}",
        user=user,
        entity_type="payment",
        entity_id=pid,
        new_value=row,
        reason=str(data.get("notes") or ""),
        ip=ip,
        level="warn" if "refund" in kind else "info",
    )
    return row


def current_indian_fy(for_date: dt.date | None = None) -> str:
    d = for_date or dt.date.today()
    start_year = d.year if d.month >= 4 else d.year - 1
    end_yy = (start_year + 1) % 100
    return f"{start_year}-{end_yy:02d}"


def issue_gst_invoice(
    booking_id: int,
    data: dict[str, Any] | None = None,
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    """Issue a sequential, gap-free, immutable GST invoice for a booking."""
    require_permission(user, "issue_invoice")
    data = data or {}
    summary = booking_settlement_summary(booking_id)
    b = summary["booking"]
    q = summary["quote"]
    fy = str(data.get("fy") or current_indian_fy())
    now = time.time()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")

    line_items = [
        {"description": f"Vehicle Rental ({q['vehicle']}) — {q['days']:g} day(s)", "amount": q["base_rent"]},
    ]
    if q["weekend_surge_amount"] > 0:
        line_items.append({"description": "Weekend Surge", "amount": q["weekend_surge_amount"]})
    if q["seasonal_surge_amount"] > 0:
        line_items.append({"description": "Seasonal Surge", "amount": q["seasonal_surge_amount"]})
    if q["extra_km_cost"] > 0:
        line_items.append({"description": f"Extra Distance ({q['extra_km']:g} km)", "amount": q["extra_km_cost"]})
    if q["extra_hr_cost"] > 0:
        line_items.append({"description": f"Extra Hours ({q['extra_hours']:g} hr)", "amount": q["extra_hr_cost"]})
    if q["driver_cost"] > 0:
        line_items.append({"description": "Chauffeur Allowance", "amount": q["driver_cost"]})
    if q["long_term_discount_amount"] > 0:
        line_items.append({"description": "Long-Term Discount", "amount": -q["long_term_discount_amount"]})
    if q["discount_amount"] > 0:
        line_items.append({"description": "Approved Discount", "amount": -q["discount_amount"]})

    with db.cursor() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            conn.execute(
                "INSERT OR IGNORE INTO invoice_counters(fy, last_seq, last_cn_seq) VALUES(?, 0, 0)",
                (fy,),
            )
            conn.execute(
                "UPDATE invoice_counters SET last_seq = last_seq + 1 WHERE fy=?",
                (fy,),
            )
            seq_no = int(
                conn.execute("SELECT last_seq FROM invoice_counters WHERE fy=?", (fy,)).fetchone()[0]
            )
            inv_number = f"FLT/{fy}/{seq_no:05d}"

            cur = conn.execute(
                """INSERT INTO invoices(
                    invoice_number, fy, seq_no, booking_id, customer_id, branch_id,
                    customer_name, customer_gstin, place_of_supply, sac_code, vehicle_reg,
                    taxable_amount, gst_percent, cgst_amount, sgst_amount, igst_amount,
                    non_taxable_amount, grand_total, line_items_json, issued_by, issued_by_name, issued_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    inv_number,
                    fy,
                    seq_no,
                    int(booking_id),
                    int(b["customer_id"]),
                    int(b["branch_id"]),
                    str(b["customer_name"]),
                    str(data.get("customer_gstin") or b.get("customer_gstin") or "").strip().upper()[:20],
                    str(data.get("place_of_supply") or "Maharashtra").strip()[:60],
                    str(data.get("sac_code") or "996601").strip()[:16],
                    str(b["reg_number"]),
                    q["taxable_subtotal"],
                    q["gst_percent"],
                    q["cgst_amount"],
                    q["sgst_amount"],
                    q["igst_amount"],
                    q["non_taxable_reimbursement"],
                    q["grand_total"],
                    json.dumps(line_items),
                    (user or {}).get("id"),
                    actor[:120],
                    now,
                ),
            )
            iid = int(cur.lastrowid)
            row = dict(conn.execute("SELECT * FROM invoices WHERE id=?", (iid,)).fetchone())
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    checkpoint_wal()
    log_sensitive_action("invoice.issue", user=user, entity_type="invoice", entity_id=inv_number, new_value=row, ip=ip, level="info")
    return row


def issue_credit_note(
    invoice_id: int,
    reason: str | dict[str, Any],
    taxable_reversal: float | dict[str, Any] | None = None,
    approved_by: str = "",
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    """Issue a sequential Credit Note linked to an immutable GST invoice."""
    if isinstance(reason, dict):
        payload = reason
        if isinstance(taxable_reversal, dict) and user is None:
            user = taxable_reversal
        if isinstance(approved_by, str) and not ip and approved_by.count(".") >= 1:
            ip = approved_by
            approved_by = ""
        reason_str = str(payload.get("reason") or "")
        rev_val = payload.get("taxable_reversal", payload.get("amount", 0))
        approved_by = str(payload.get("approved_by") or approved_by or "")
    else:
        reason_str = str(reason or "")
        rev_val = taxable_reversal if taxable_reversal is not None else 0

    require_permission(user, "issue_credit_note")
    if not reason_str.strip():
        raise ValueError("A reason is mandatory to issue a GST Credit Note.")
    rev_taxable = money(rev_val)
    if rev_taxable <= Decimal("0.00"):
        raise ValueError("taxable_reversal must be greater than zero.")

    now = time.time()
    actor = str((user or {}).get("name") or (user or {}).get("email") or "accountant")
    with db.cursor() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            inv = conn.execute("SELECT * FROM invoices WHERE id=?", (int(invoice_id),)).fetchone()
            if not inv:
                raise ValueError("Original GST invoice not found.")
            if rev_taxable > money(inv["taxable_amount"]):
                raise ValueError("Credit note taxable reversal cannot exceed invoice taxable amount.")

            fy = str(inv["fy"])
            conn.execute("UPDATE invoice_counters SET last_cn_seq = last_cn_seq + 1 WHERE fy=?", (fy,))
            cn_seq = int(conn.execute("SELECT last_cn_seq FROM invoice_counters WHERE fy=?", (fy,)).fetchone()[0])
            cn_number = f"CN/{fy}/{cn_seq:05d}"

            gst_pct = _dec(inv["gst_percent"])
            gst_rev = (rev_taxable * (gst_pct / Decimal("100"))).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
            if float(inv["igst_amount"]) > 0:
                cgst_rev = Decimal("0.00")
                sgst_rev = Decimal("0.00")
                igst_rev = gst_rev
            else:
                cgst_rev = (gst_rev / Decimal("2")).quantize(TWO_PLACES, rounding=ROUND_FLOOR)
                sgst_rev = (gst_rev - cgst_rev).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
                igst_rev = Decimal("0.00")
            total_rev = (rev_taxable + gst_rev).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

            cur = conn.execute(
                """INSERT INTO credit_notes(
                    credit_note_number, fy, seq_no, invoice_id, invoice_number, reason,
                    taxable_reversal, gst_percent, cgst_reversal, sgst_reversal, igst_reversal,
                    total_reversal, approved_by, issued_by, issued_by_name, issued_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    cn_number,
                    fy,
                    cn_seq,
                    int(invoice_id),
                    str(inv["invoice_number"]),
                    reason_str.strip()[:300],
                    float(rev_taxable),
                    float(gst_pct),
                    float(cgst_rev),
                    float(sgst_rev),
                    float(igst_rev),
                    float(total_rev),
                    str(approved_by or actor)[:120],
                    (user or {}).get("id"),
                    actor[:120],
                    now,
                ),
            )
            cn_id = int(cur.lastrowid)
            row = dict(conn.execute("SELECT * FROM credit_notes WHERE id=?", (cn_id,)).fetchone())
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    checkpoint_wal()
    log_sensitive_action(
        "credit_note.issue",
        user=user,
        entity_type="credit_note",
        entity_id=cn_number,
        old_value={"invoice_number": inv["invoice_number"], "invoice_grand_total": inv["grand_total"]},
        new_value=row,
        reason=reason_str,
        ip=ip,
    )
    return row


def list_invoices(branch_id: int | None = None, booking_id: int | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM invoices WHERE 1=1"
    args: list[Any] = []
    if branch_id is not None:
        sql += " AND branch_id=?"
        args.append(int(branch_id))
    if booking_id is not None:
        sql += " AND booking_id=?"
        args.append(int(booking_id))
    sql += " ORDER BY id DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def list_payments(booking_id: int | None = None, branch_id: int | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM payments WHERE 1=1"
    args: list[Any] = []
    if booking_id is not None:
        sql += " AND booking_id=?"
        args.append(int(booking_id))
    if branch_id is not None:
        sql += " AND branch_id=?"
        args.append(int(branch_id))
    sql += " ORDER BY created_at DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def list_credit_notes(invoice_id: int | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM credit_notes"
    args: list[Any] = []
    if invoice_id is not None:
        sql += " WHERE invoice_id=?"
        args.append(int(invoice_id))
    sql += " ORDER BY id DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


# ---------------------------------------------------------------------------
# Daily Cash & Collection Report + End-of-Shift Reconciliation
# ---------------------------------------------------------------------------
def daily_collection_report(date_str: str = "", branch_id: int | None = None) -> dict[str, Any]:
    target_date = date_str or dt.date.today().isoformat()
    start_dt = dt.datetime.fromisoformat(f"{target_date}T00:00:00")
    end_dt = start_dt + dt.timedelta(days=1)
    start_ts, end_ts = start_dt.timestamp(), end_dt.timestamp()

    sql = "SELECT * FROM payments WHERE created_at >= ? AND created_at < ?"
    args: list[Any] = [start_ts, end_ts]
    if branch_id is not None:
        sql += " AND branch_id=?"
        args.append(int(branch_id))
    sql += " ORDER BY created_at ASC"

    with db.cursor() as conn:
        rows = [dict(r) for r in conn.execute(sql, args).fetchall()]

    cash_in = Decimal("0.00")
    cash_out = Decimal("0.00")
    upi_in = Decimal("0.00")
    card_in = Decimal("0.00")
    bank_in = Decimal("0.00")
    total_refunds = Decimal("0.00")

    for r in rows:
        amt = money(r["amount"])
        is_refund = r["kind"] in ("refund", "deposit_refund", "cancellation_refund")
        if is_refund:
            total_refunds += amt
            if r["mode"] == "Cash":
                cash_out += amt
        else:
            if r["mode"] == "Cash":
                cash_in += amt
            elif r["mode"] == "UPI":
                upi_in += amt
            elif r["mode"] == "Card":
                card_in += amt
            else:
                bank_in += amt

    return {
        "date": target_date,
        "branch_id": branch_id,
        "cash_collected": float(cash_in),
        "cash_refunded": float(cash_out),
        "net_cash": float(cash_in - cash_out),
        "upi_collected": float(upi_in),
        "card_collected": float(card_in),
        "bank_collected": float(bank_in),
        "total_refunds": float(total_refunds),
        "gross_collections": float(cash_in + upi_in + card_in + bank_in),
        "net_collections": float(cash_in + upi_in + card_in + bank_in - total_refunds),
        "transactions": rows,
    }


def close_shift_reconciliation(
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "reconcile_shift")
    shift_date = str(data.get("shift_date") or dt.date.today().isoformat())[:10]
    branch_id = int(data.get("branch_id") or 1)
    report = daily_collection_report(shift_date, branch_id=branch_id)

    opening = money(data.get("opening_cash", 0))
    actual_closing = money(data.get("actual_closing_cash", 0))
    cash_in = money(report["cash_collected"])
    cash_out = money(report["cash_refunded"])
    expected_closing = (opening + cash_in - cash_out).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    variance = (actual_closing - expected_closing).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)

    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")
    now = time.time()
    with db.cursor() as conn:
        cur = conn.execute(
            """INSERT INTO shift_reconciliations(
                branch_id, shift_date, operator_id, operator_name, opening_cash,
                cash_collected, cash_refunded, expected_closing_cash, actual_closing_cash,
                cash_variance, upi_collected, card_collected, bank_collected, total_refunds,
                notes, closed_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                branch_id,
                shift_date,
                (user or {}).get("id"),
                actor[:120],
                float(opening),
                float(cash_in),
                float(cash_out),
                float(expected_closing),
                float(actual_closing),
                float(variance),
                report["upi_collected"],
                report["card_collected"],
                report["bank_collected"],
                report["total_refunds"],
                str(data.get("notes") or "").strip()[:300],
                now,
            ),
        )
        rid = int(cur.lastrowid)
        row = dict(conn.execute("SELECT * FROM shift_reconciliations WHERE id=?", (rid,)).fetchone())
    checkpoint_wal()
    log_sensitive_action(
        "shift.reconcile",
        user=user,
        entity_type="shift_reconciliation",
        entity_id=rid,
        new_value=row,
        reason=str(data.get("notes") or ""),
        ip=ip,
        level="warn" if abs(float(variance)) > 0.01 else "info",
    )
    return row


# ---------------------------------------------------------------------------
# Maintenance Job Cards, Annotated Damage Records & Digital Signatures
# ---------------------------------------------------------------------------
def create_maintenance_job_card(
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "write_maintenance")
    vehicle_id = int(data.get("vehicle_id") or 0)
    if not vehicle_id:
        raise ValueError("vehicle_id is required.")
    status = str(data.get("status") or "in_progress").strip().lower()
    if status not in ("scheduled", "in_progress", "completed", "cancelled"):
        raise ValueError("Invalid maintenance status.")

    parts = money(data.get("parts_cost", 0))
    labour = money(data.get("labour_cost", 0))
    total = (parts + labour).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    now = time.time()

    with db.cursor() as conn:
        veh = conn.execute("SELECT * FROM vehicles WHERE id=?", (vehicle_id,)).fetchone()
        if not veh:
            raise ValueError("Vehicle not found.")
        seq = int(conn.execute("SELECT COUNT(*) FROM maintenance_logs").fetchone()[0]) + 1
        jc_no = str(data.get("job_card_no") or f"JC-{dt.date.today().strftime('%Y%m')}-{seq:04d}")
        odo = float(_dec(data.get("odometer_km", veh["odometer_km"])))
        next_km = float(_dec(data.get("next_due_km", odo + float(veh["service_interval_km"]))))
        next_date = str(
            data.get("next_due_date") or (dt.date.today() + dt.timedelta(days=180)).isoformat()
        )[:20]

        cur = conn.execute(
            """INSERT INTO maintenance_logs(
                job_card_no, vehicle_id, branch_id, service_type, workshop_name,
                odometer_km, scheduled_date, completed_date, next_due_km, next_due_date,
                parts_cost, labour_cost, total_cost, status, notes, created_by, created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                jc_no,
                vehicle_id,
                int(data.get("branch_id") or veh["branch_id"] or 1),
                str(data.get("service_type") or "Periodic Service").strip()[:80],
                str(data.get("workshop_name") or "").strip()[:120],
                odo,
                str(data.get("scheduled_date") or dt.date.today().isoformat())[:20],
                str(data.get("completed_date") or (dt.date.today().isoformat() if status == "completed" else ""))[:20],
                next_km,
                next_date,
                float(parts),
                float(labour),
                float(total),
                status,
                str(data.get("notes") or "").strip()[:400],
                (user or {}).get("id"),
                now,
            ),
        )
        if status == "in_progress":
            conn.execute("UPDATE vehicles SET status='in_workshop', updated_at=? WHERE id=?", (now, vehicle_id))
        elif status == "completed":
            conn.execute(
                """UPDATE vehicles SET status='available', odometer_km=MAX(odometer_km, ?),
                          last_service_km=?, next_service_due_date=?, updated_at=?
                   WHERE id=?""",
                (odo, odo, next_date, now, vehicle_id),
            )
        row = dict(conn.execute("SELECT * FROM maintenance_logs WHERE id=?", (int(cur.lastrowid),)).fetchone())
    log_sensitive_action("maintenance.job_card", user=user, entity_type="maintenance", entity_id=row["id"], new_value=row, ip=ip, level="info")
    return row


def list_maintenance_logs(vehicle_id: int | None = None) -> list[dict[str, Any]]:
    sql = """SELECT m.*, v.reg_number, v.make, v.model
             FROM maintenance_logs m
             JOIN vehicles v ON v.id = m.vehicle_id"""
    args: list[Any] = []
    if vehicle_id is not None:
        sql += " WHERE m.vehicle_id=?"
        args.append(int(vehicle_id))
    sql += " ORDER BY m.created_at DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def create_damage_record(
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "write_damage")
    vehicle_id = int(data.get("vehicle_id") or 0)
    panel = str(data.get("panel_location") or "").strip()[:80]
    if not vehicle_id or not panel:
        raise ValueError("vehicle_id and panel_location are required.")
    severity = str(data.get("severity") or "scratch").strip().lower()
    if severity not in ("scratch", "dent", "crack", "interior", "mechanical", "major"):
        raise ValueError("Invalid damage severity.")
    annotations = data.get("annotation_json")
    if isinstance(annotations, (list, dict)):
        ann_str = json.dumps(annotations)
    else:
        ann_str = str(annotations or "[]")

    est_cost = float(money(data.get("estimated_cost", 0)))
    deducted = float(money(data.get("deducted_from_deposit", 0)))
    actor = str((user or {}).get("name") or (user or {}).get("email") or "operator")
    now = time.time()

    with db.cursor() as conn:
        veh = conn.execute("SELECT id FROM vehicles WHERE id=?", (vehicle_id,)).fetchone()
        if not veh:
            raise ValueError("Vehicle not found.")
        cur = conn.execute(
            """INSERT INTO damage_records(
                vehicle_id, booking_id, panel_location, severity, description,
                photo_data, annotation_json, annotated_photo_data,
                estimated_cost, deducted_from_deposit, status, logged_by, created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                vehicle_id,
                int(data["booking_id"]) if data.get("booking_id") else None,
                panel,
                severity,
                str(data.get("description") or "").strip()[:500],
                str(data.get("photo_data") or ""),
                ann_str,
                str(data.get("annotated_photo_data") or ""),
                est_cost,
                deducted,
                str(data.get("status") or "open").strip().lower(),
                actor[:120],
                now,
            ),
        )
        did = int(cur.lastrowid)
        row = dict(conn.execute("SELECT * FROM damage_records WHERE id=?", (did,)).fetchone())
    log_sensitive_action(
        "damage.record",
        user=user,
        entity_type="damage_record",
        entity_id=did,
        new_value={"vehicle_id": vehicle_id, "panel_location": panel, "deducted_from_deposit": deducted},
        reason=str(data.get("description") or ""),
        ip=ip,
    )
    return row


def list_damage_records(vehicle_id: int | None = None) -> list[dict[str, Any]]:
    sql = """SELECT d.*, v.reg_number, v.make, v.model
             FROM damage_records d
             JOIN vehicles v ON v.id = d.vehicle_id"""
    args: list[Any] = []
    if vehicle_id is not None:
        sql += " WHERE d.vehicle_id=?"
        args.append(int(vehicle_id))
    sql += " ORDER BY d.created_at DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def capture_digital_signature(
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "write_booking")
    booking_id = int(data.get("booking_id") or 0)
    doc_kind = str(data.get("doc_kind") or "agreement").strip().lower()
    signer_role = str(data.get("signer_role") or "customer").strip().lower()
    signer_name = str(data.get("signer_name") or "").strip()[:120]
    sig_data = str(data.get("signature_data") or "").strip()
    if not booking_id or not signer_name or not sig_data:
        raise ValueError("booking_id, signer_name, and signature_data are required.")
    if doc_kind not in ("agreement", "handover", "return", "damage_notice"):
        raise ValueError("Invalid doc_kind.")
    if signer_role not in ("customer", "operator", "driver", "manager"):
        raise ValueError("Invalid signer_role.")

    now = time.time()
    payload_to_hash = f"{booking_id}|{doc_kind}|{signer_role}|{signer_name}|{sig_data}|{now:.3f}"
    doc_hash = hashlib.sha256(payload_to_hash.encode("utf-8")).hexdigest()

    with db.cursor() as conn:
        b = conn.execute("SELECT id FROM bookings WHERE id=?", (booking_id,)).fetchone()
        if not b:
            raise ValueError("Booking not found.")
        cur = conn.execute(
            """INSERT INTO signatures(booking_id, doc_kind, signer_role, signer_name,
                                      signature_data, doc_hash, ip, signed_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (booking_id, doc_kind, signer_role, signer_name, sig_data, doc_hash, ip[:64], now),
        )
        row = dict(conn.execute("SELECT * FROM signatures WHERE id=?", (int(cur.lastrowid),)).fetchone())
    log_sensitive_action("signature.capture", user=user, entity_type="signature", entity_id=row["id"], new_value={"booking_id": booking_id, "signer_name": signer_name, "doc_hash": doc_hash}, ip=ip, level="info")
    return row


# ---------------------------------------------------------------------------
# Executive Dashboards (Utilization %, Revenue/Vehicle, Idle Days, Net Profitability)
# ---------------------------------------------------------------------------
def fleet_profitability_dashboard(branch_id: int | None = None, window_days: int = 30) -> dict[str, Any]:
    window_days = max(1, int(window_days))
    vehicles = list_vehicles(branch_id=branch_id)

    with db.cursor() as conn:
        bookings = [dict(r) for r in conn.execute("SELECT * FROM bookings WHERE status IN ('confirmed','picked_up','returned','closed')").fetchall()]
        maint = [dict(r) for r in conn.execute("SELECT * FROM maintenance_logs WHERE status <> 'cancelled'").fetchall()]

    per_vehicle: list[dict[str, Any]] = []
    total_rev = Decimal("0.00")
    total_maint = Decimal("0.00")
    total_driver_cost = Decimal("0.00")
    total_rented_days = 0.0

    for v in vehicles:
        vid = int(v["id"])
        v_bookings = [b for b in bookings if int(b["vehicle_id"]) == vid]
        v_maint = [m for m in maint if int(m["vehicle_id"]) == vid]

        rented_days = 0.0
        rev = Decimal("0.00")
        drv_cost = Decimal("0.00")
        for b in v_bookings:
            p_dt = _parse_iso_dt(b["pickup_at"])
            r_dt = _parse_iso_dt(b["return_at"])
            d = max(1.0, math.ceil((r_dt - p_dt).total_seconds() / 86400.0))
            rented_days += d
            actual_km = max(0.0, float(b["odometer_in"]) - float(b["odometer_out"])) if float(b["odometer_in"]) > float(b["odometer_out"]) else 0.0
            q = calculate_tariff_exact({
                "days": d,
                "daily_rate": b["daily_rate"],
                "weekend_days": b["weekend_days"],
                "weekend_surge_pct": b["weekend_surge_pct"],
                "seasonal_surge_pct": b["seasonal_surge_pct"],
                "long_term_discount_pct": b["long_term_discount_pct"],
                "included_km_per_day": b["included_km_per_day"],
                "actual_km": actual_km,
                "extra_km_rate": b["extra_km_rate"],
                "extra_hours": b["extra_hours"],
                "extra_hour_rate": b["extra_hour_rate"],
                "driver_allowance_per_day": b["driver_allowance_per_day"],
                "discount_amount": b["discount_amount"],
                "gst_percent": 0,
            })
            rev += money(q["taxable_subtotal"])
            drv_cost += money(q["driver_cost"])

        m_cost = sum((money(m["total_cost"]) for m in v_maint), Decimal("0.00"))
        profit = (rev - m_cost - drv_cost).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        capped_rented = min(float(window_days), rented_days)
        idle_days = max(0.0, float(window_days) - capped_rented)
        utilization_pct = round((capped_rented / float(window_days)) * 100.0, 1)

        total_rev += rev
        total_maint += m_cost
        total_driver_cost += drv_cost
        total_rented_days += capped_rented

        per_vehicle.append({
            "vehicle_id": vid,
            "reg_number": v["reg_number"],
            "make": v["make"],
            "model": v["model"],
            "category": v["category"],
            "status": v["status"],
            "bookings_count": len(v_bookings),
            "rented_days": round(rented_days, 1),
            "idle_days": round(idle_days, 1),
            "utilization_pct": utilization_pct,
            "gross_revenue": float(rev),
            "maintenance_cost": float(m_cost),
            "driver_cost": float(drv_cost),
            "net_profit": float(profit),
        })

    fleet_count = len(vehicles)
    fleet_capacity_days = max(1.0, float(fleet_count * window_days))
    fleet_util = round((total_rented_days / fleet_capacity_days) * 100.0, 1) if fleet_count else 0.0

    return {
        "window_days": window_days,
        "fleet_count": fleet_count,
        "fleet_utilization_pct": fleet_util,
        "total_gross_revenue": float(total_rev),
        "total_maintenance_cost": float(total_maint),
        "total_driver_cost": float(total_driver_cost),
        "total_net_profit": float(total_rev - total_maint - total_driver_cost),
        "vehicles": per_vehicle,
    }


# ---------------------------------------------------------------------------
# Excel (.xlsx) & CSV Bulk Importer with Dry-Run Preview & Error Report
# ---------------------------------------------------------------------------
def _parse_tabular_bytes(raw: bytes, filename: str) -> list[dict[str, str]]:
    name_lower = (filename or "upload.csv").strip().lower()
    if name_lower.endswith(".xlsx"):
        text = attachments.xlsx_text(raw)
        lines = [ln for ln in text.splitlines() if ln.strip() and not ln.startswith("# ")]
        reader = csv.DictReader(io.StringIO("\n".join(lines)), delimiter="\t")
        return [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in reader]

    decoded = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(decoded))
    return [{(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in reader]


def preview_bulk_import(
    entity_type: str,
    raw_bytes_or_filename: bytes | str,
    filename_or_content: str | bytes = "import.csv",
) -> dict[str, Any]:
    kind = str(entity_type or "").strip().lower()
    if kind not in ("vehicles", "customers"):
        raise ValueError("entity_type must be 'vehicles' or 'customers'.")

    import base64
    if isinstance(raw_bytes_or_filename, bytes):
        raw_bytes = raw_bytes_or_filename
        filename = str(filename_or_content or "import.csv")
    elif isinstance(raw_bytes_or_filename, str) and raw_bytes_or_filename.lower().endswith((".csv", ".xlsx")):
        filename = raw_bytes_or_filename
        if isinstance(filename_or_content, bytes):
            raw_bytes = filename_or_content
        else:
            content_str = str(filename_or_content or "")
            if content_str.startswith("data:") and ";base64," in content_str:
                raw_bytes = base64.b64decode(content_str.split(";base64,", 1)[1])
            elif filename.lower().endswith(".xlsx"):
                raw_bytes = base64.b64decode(content_str)
            else:
                raw_bytes = content_str.encode("utf-8")
    else:
        raw_bytes = str(raw_bytes_or_filename or "").encode("utf-8")
        filename = str(filename_or_content or "import.csv")

    rows = _parse_tabular_bytes(raw_bytes, filename)
    valid_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    with db.cursor() as conn:
        existing_regs = {r[0].upper() for r in conn.execute("SELECT reg_number FROM vehicles").fetchall()}

    for idx, r in enumerate(rows, start=2):
        if kind == "vehicles":
            reg_raw = r.get("reg_number") or r.get("registration") or r.get("plate") or ""
            make = r.get("make") or ""
            model = r.get("model") or ""
            row_errs: list[str] = []
            try:
                reg = normalize_reg_number(reg_raw)
                if not _REG_RE.match(reg):
                    row_errs.append(f"Invalid Indian registration format '{reg_raw}'.")
                if reg in existing_regs or reg in seen_keys:
                    row_errs.append(f"Duplicate registration number '{reg}'.")
                seen_keys.add(reg)
            except ValueError as exc:
                reg = reg_raw
                row_errs.append(str(exc))
            if not make:
                row_errs.append("Missing 'make'.")
            if not model:
                row_errs.append("Missing 'model'.")
            daily_rate = _dec(r.get("daily_rate") or "2000", "-1")
            if daily_rate <= 0:
                row_errs.append("Invalid 'daily_rate' (must be > 0).")

            if row_errs:
                errors.append({"row": idx, "data": r, "errors": row_errs})
            else:
                valid_rows.append({
                    "reg_number": reg,
                    "make": make,
                    "model": model,
                    "variant": r.get("variant", ""),
                    "category": r.get("category", "Compact SUV") or "Compact SUV",
                    "fuel_type": r.get("fuel_type", "Petrol") or "Petrol",
                    "transmission": r.get("transmission", "Manual") or "Manual",
                    "seats": int(float(r.get("seats") or 5)),
                    "colour": r.get("colour", "White") or "White",
                    "odometer_km": float(_dec(r.get("odometer_km") or 0)),
                    "daily_rate": float(daily_rate),
                })
        else:
            name = r.get("full_name") or r.get("name") or ""
            phone = r.get("phone") or r.get("mobile") or ""
            dl = r.get("dl_number") or r.get("licence") or ""
            row_errs = []
            if not name:
                row_errs.append("Missing 'full_name'.")
            if not phone or len(re.sub(r"\D", "", phone)) < 10:
                row_errs.append(f"Invalid 10-digit phone number '{phone}'.")
            if row_errs:
                errors.append({"row": idx, "data": r, "errors": row_errs})
            else:
                valid_rows.append({
                    "full_name": name,
                    "phone": phone,
                    "email": r.get("email", ""),
                    "dl_number": dl.upper(),
                    "dl_expiry": r.get("dl_expiry", ""),
                    "id_proof_type": r.get("id_proof_type", ""),
                    "id_proof_number": r.get("id_proof_number", ""),
                    "dpdp_consent": True,
                })

    return {
        "entity_type": kind,
        "filename": filename,
        "total_rows": len(rows),
        "valid_count": len(valid_rows),
        "error_count": len(errors),
        "valid_rows": valid_rows,
        "errors": errors,
    }


def commit_bulk_import(
    entity_type: str,
    valid_rows: list[dict[str, Any]],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "import_data")
    kind = str(entity_type or "").strip().lower()
    created: list[dict[str, Any]] = []
    for row in valid_rows[:500]:
        if kind == "vehicles":
            created.append(create_vehicle(row, user=user, ip=ip))
        elif kind == "customers":
            row["dpdp_consent"] = True
            created.append(create_customer(row, user=user, ip=ip))
        else:
            raise ValueError("entity_type must be 'vehicles' or 'customers'.")
    return {"ok": True, "imported_count": len(created), "records": created}


# ---------------------------------------------------------------------------
# Route-level convenience wrappers & aliases
# ---------------------------------------------------------------------------
def transfer_vehicle(
    vehicle_id: int,
    to_branch_id: int,
    odometer_km: float | None = None,
    reason: str = "",
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    res = transfer_vehicle_branch(
        vehicle_id,
        to_branch_id,
        odometer_km=odometer_km if odometer_km and odometer_km > 0 else None,
        notes=reason,
        user=user,
        ip=ip,
    )
    return res["vehicle"]


def add_vehicle_compliance(
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    vid = int(data.get("vehicle_id") or 0)
    return upsert_vehicle_compliance(vid, data, user=user, ip=ip)


def get_compliance_alerts(days_ahead: int = 30, reference_date: str = "") -> dict[str, Any]:
    return compliance_and_expiry_alerts(days_ahead=days_ahead, reference_date=reference_date)


def get_customer(customer_id: int, user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any] | None:
    try:
        return get_customer_profile(customer_id, user=user, ip=ip)
    except ValueError:
        return None


def export_customer_data_dpdp(customer_id: int, user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    return export_customer_dpdp_package(customer_id, user=user, ip=ip)


def erase_customer_pii_dpdp(
    customer_id: int,
    reason: str,
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    cust = erase_customer_pii(customer_id, reason, user=user, ip=ip)
    return {"ok": True, "customer": cust}


def get_vehicle_timeline(branch_id: int | None = None) -> list[dict[str, Any]]:
    return booking_timeline_by_vehicle(branch_id=branch_id)


def transition_booking(
    booking_id: int,
    new_status: str,
    data: dict[str, Any] | None = None,
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    updated = transition_booking_status(booking_id, new_status, data=data, user=user, ip=ip)
    return {
        "booking": updated,
        "cancellation_fee": updated.get("cancellation_fee", 0.0),
        "refund_due": updated.get("refund_due", 0.0),
    }


def get_booking_settlement(booking_id: int) -> dict[str, Any]:
    return booking_settlement_summary(booking_id)


def get_daily_collection_report(on_date: str = "", branch_id: int | None = None) -> dict[str, Any]:
    return daily_collection_report(date_str=on_date, branch_id=branch_id)


def reconcile_shift(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    return close_shift_reconciliation(data, user=user, ip=ip)


def list_maintenance_jobs(vehicle_id: int | None = None, status: str = "") -> list[dict[str, Any]]:
    rows = list_maintenance_logs(vehicle_id=vehicle_id)
    if status:
        rows = [r for r in rows if r.get("status") == status.strip().lower()]
    return rows


def create_maintenance_job(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    return create_maintenance_job_card(data, user=user, ip=ip)


def update_maintenance_job(
    job_id: int,
    data: dict[str, Any],
    user: dict[str, Any] | None = None,
    ip: str = "",
) -> dict[str, Any]:
    require_permission(user, "write_maintenance")
    now = time.time()
    with db.cursor() as conn:
        job = conn.execute("SELECT * FROM maintenance_logs WHERE id=?", (int(job_id),)).fetchone()
        if not job:
            raise ValueError("Maintenance job card not found.")
        status = str(data.get("status") or job["status"]).strip().lower()
        parts = money(data.get("parts_cost", job["parts_cost"]))
        labour = money(data.get("labour_cost", job["labour_cost"]))
        total = (parts + labour).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        completed_date = str(
            data.get("completed_date")
            or (dt.date.today().isoformat() if status == "completed" else job["completed_date"])
        )[:20]
        conn.execute(
            """UPDATE maintenance_logs
               SET status=?, parts_cost=?, labour_cost=?, total_cost=?, completed_date=?, notes=?
               WHERE id=?""",
            (
                status,
                float(parts),
                float(labour),
                float(total),
                completed_date,
                str(data.get("notes") or job["notes"])[:400],
                int(job_id),
            ),
        )
        vid = int(job["vehicle_id"])
        if status == "completed":
            conn.execute(
                """UPDATE vehicles SET status='available',
                          last_service_km=MAX(last_service_km, ?),
                          next_service_due_date=?, updated_at=?
                   WHERE id=?""",
                (float(job["odometer_km"]), str(job["next_due_date"]), now, vid),
            )
        elif status == "in_progress":
            conn.execute("UPDATE vehicles SET status='in_workshop', updated_at=? WHERE id=?", (now, vid))
        updated = dict(conn.execute("SELECT * FROM maintenance_logs WHERE id=?", (int(job_id),)).fetchone())
    log_sensitive_action("maintenance.update", user=user, entity_type="maintenance", entity_id=job_id, old_value=dict(job), new_value=updated, ip=ip, level="info")
    return updated


def add_damage_record(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    return create_damage_record(data, user=user, ip=ip)


def list_signatures(booking_id: int | None = None) -> list[dict[str, Any]]:
    sql = "SELECT * FROM signatures"
    args: list[Any] = []
    if booking_id is not None:
        sql += " WHERE booking_id=?"
        args.append(int(booking_id))
    sql += " ORDER BY signed_at DESC"
    with db.cursor() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def capture_signature(data: dict[str, Any], user: dict[str, Any] | None = None, ip: str = "") -> dict[str, Any]:
    return capture_digital_signature(data, user=user, ip=ip)


def get_fleet_dashboard(days: int = 30, branch_id: int | None = None) -> dict[str, Any]:
    return fleet_profitability_dashboard(branch_id=branch_id, window_days=days)

