"""Comprehensive Enterprise Car Rental Operations, GST, DPDP, Security & RBAC Tests."""

from __future__ import annotations

import datetime as dt
import io
import json
import sqlite3
import tempfile
import unittest
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from float import attachments, config, db, maintenance, rental_ops, security, server


def _build_minimal_xlsx(rows: list[list[str]]) -> bytes:
    """Create a valid minimal .xlsx zip archive in memory using stdlib zipfile."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            "</Types>",
        )
        sheet_rows = []
        for r_idx, row in enumerate(rows, start=1):
            cells = []
            for c_idx, val in enumerate(row):
                col = chr(ord("A") + c_idx)
                cells.append(f'<c r="{col}{r_idx}" t="inlineStr"><is><t>{val}</t></is></c>')
            sheet_rows.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
        sheet_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            f'<sheetData>{"".join(sheet_rows)}</sheetData>'
            "</worksheet>"
        )
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml)
    return buf.getvalue()


class EnterpriseRentalTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="float-ent-")
        tmp_path = Path(self._tmp.name)
        self.orig_paths = (
            config.DATA_DIR,
            config.DB_PATH,
            config.FILES_DIR,
            config.LOG_PATH,
            config.DEVICE_KEY_PATH,
        )
        config.DATA_DIR = tmp_path
        config.DB_PATH = tmp_path / "float.sqlite3"
        config.FILES_DIR = tmp_path / "files"
        config.LOG_PATH = tmp_path / "float.log"
        config.DEVICE_KEY_PATH = tmp_path / ".device_key"
        security._DEVICE_KEY = None
        db._initialised = False
        config.ensure_dirs()
        db.init()

        self.owner = {"id": 1, "email": "owner@agency.in", "name": "Agency Owner", "role": "admin", "ops_role": "owner", "branch_id": 1}
        self.manager = {"id": 2, "email": "manager@agency.in", "name": "Branch Manager", "role": "teacher", "ops_role": "manager", "branch_id": 1}
        self.desk = {"id": 3, "email": "desk@agency.in", "name": "Desk Agent", "role": "teacher", "ops_role": "desk_agent", "branch_id": 1}
        self.accountant = {"id": 4, "email": "acct@agency.in", "name": "Accountant", "role": "teacher", "ops_role": "accountant", "branch_id": 1}
        self.viewer = {"id": 5, "email": "audit@agency.in", "name": "Auditor", "role": "teacher", "ops_role": "read_only", "branch_id": 1}
        with db.cursor() as conn:
            for u in (self.owner, self.manager, self.desk, self.accountant, self.viewer):
                conn.execute(
                    """INSERT INTO users(id, email, name, password_hash, role, ops_role, branch_id, active, created_at)
                       VALUES(?,?,?,?,?,?,?,1,1700000000)""",
                    (u["id"], u["email"], u["name"], "pbkdf2_sha256$310000$aa$bb", u["role"], u["ops_role"], u["branch_id"]),
                )

    def tearDown(self) -> None:
        (
            config.DATA_DIR,
            config.DB_PATH,
            config.FILES_DIR,
            config.LOG_PATH,
            config.DEVICE_KEY_PATH,
        ) = self.orig_paths
        security._DEVICE_KEY = None
        db._initialised = False
        self._tmp.cleanup()

    # ------------------------------------------------------------------
    # 1. Exact Tariff Math & GST Split
    # ------------------------------------------------------------------
    def test_exact_tariff_math_and_odd_paisa_gst_split(self) -> None:
        # ₹1,001.00 taxable at 5% GST = ₹50.05 total GST -> CGST ₹25.02 + SGST ₹25.03 == ₹50.05
        q = rental_ops.calculate_tariff_exact({
            "vehicle": "Sedan",
            "days": 1,
            "daily_rate": 1001,
            "included_km_per_day": 250,
            "actual_km": 200,
            "gst_percent": 5,
            "inter_state": False,
            "security_deposit": 5000,
        })
        self.assertEqual(q["taxable_subtotal"], 1001.00)
        self.assertEqual(q["gst_amount"], 50.05)
        self.assertEqual(q["cgst_amount"], 25.02)
        self.assertEqual(q["sgst_amount"], 25.03)
        self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])
        self.assertEqual(q["igst_amount"], 0.00)
        self.assertEqual(q["grand_total"], 1051.05)
        self.assertEqual(q["payable_with_deposit"], 6051.05)

        # Inter-state IGST + weekend surge + seasonal surge + long-term discount + reimbursements
        q2 = rental_ops.calculate_tariff_exact({
            "vehicle": "Innova Hycross",
            "days": 10,
            "daily_rate": 4000,
            "weekend_days": 2,
            "weekend_surge_pct": 10,     # 2 * 4000 * 10% = 800
            "seasonal_surge_pct": 5,     # 40000 * 5% = 2000 -> gross base = 42800
            "long_term_discount_pct": 10,  # 10% of 42800 = 4280 -> net base = 38520
            "included_km_per_day": 250,  # 2500 included
            "actual_km": 2700,           # 200 extra km * 15 = 3000
            "extra_km_rate": 15,
            "extra_hours": 2,            # 2 * 250 = 500
            "extra_hour_rate": 250,
            "driver_allowance_per_day": 500,  # 10 * 500 = 5000
            "discount_amount": 520,      # taxable = 38520 + 3000 + 500 + 5000 - 520 = 46500
            "toll_parking": 1200,
            "fuel_charge": 800,
            "damage_charge": 0,
            "gst_percent": 12,           # 12% of 46500 = 5580 IGST
            "inter_state": True,
            "security_deposit": 10000,
        })
        self.assertEqual(q2["base_rent"], 40000.00)
        self.assertEqual(q2["weekend_surge_amount"], 800.00)
        self.assertEqual(q2["seasonal_surge_amount"], 2000.00)
        self.assertEqual(q2["long_term_discount_amount"], 4280.00)
        self.assertEqual(q2["extra_km"], 200.0)
        self.assertEqual(q2["extra_km_cost"], 3000.00)
        self.assertEqual(q2["extra_hr_cost"], 500.00)
        self.assertEqual(q2["driver_cost"], 5000.00)
        self.assertEqual(q2["taxable_subtotal"], 46500.00)
        self.assertEqual(q2["igst_amount"], 5580.00)
        self.assertEqual(q2["cgst_amount"], 0.00)
        self.assertEqual(q2["sgst_amount"], 0.00)
        self.assertEqual(q2["non_taxable_reimbursement"], 2000.00)
        self.assertEqual(q2["grand_total"], 54080.00)

    # ------------------------------------------------------------------
    # 2. Fleet Master, Multi-Branch Transfer & Compliance Alerts
    # ------------------------------------------------------------------
    def test_fleet_master_branch_transfer_and_compliance_alerts(self) -> None:
        pune = rental_ops.create_branch(
            {"code": "PNQ", "name": "Pune Airport", "city": "Pune", "state": "Maharashtra"},
            user=self.owner,
        )
        veh = rental_ops.create_vehicle(
            {
                "reg_number": "mh 01 ab 1234",
                "make": "Toyota",
                "model": "Innova Hycross",
                "variant": "ZX Hybrid",
                "category": "MPV",
                "vin": "MBJ12345678901234",
                "fuel_type": "Hybrid",
                "seats": 7,
                "colour": "Pearl White",
                "purchase_date": "2025-01-15",
                "odometer_km": 14500,
                "daily_rate": 4500,
                "service_interval_km": 10000,
                "last_service_km": 5000,
            },
            user=self.manager,
        )
        self.assertEqual(veh["reg_number"], "MH-01-AB-1234")
        self.assertEqual(veh["branch_id"], 1)

        # Transfer to Pune branch requires odometer >= current
        with self.assertRaises(ValueError):
            rental_ops.transfer_vehicle_branch(veh["id"], pune["id"], odometer_km=14000, user=self.manager)

        tr = rental_ops.transfer_vehicle_branch(
            veh["id"], pune["id"], odometer_km=14660, notes="Convoy to Pune", user=self.manager
        )
        self.assertEqual(tr["vehicle"]["branch_id"], pune["id"])
        self.assertEqual(tr["vehicle"]["odometer_km"], 14660.0)

        # Compliance alerts: expiring insurance + low FASTag wallet + due service (14660 >= 15000 - 500)
        soon = (dt.date.today() + dt.timedelta(days=10)).isoformat()
        rental_ops.upsert_vehicle_compliance(
            veh["id"],
            {"doc_type": "insurance", "doc_number": "ICICI-991", "expiry_date": soon},
            user=self.desk,
        )
        rental_ops.upsert_vehicle_compliance(
            veh["id"],
            {"doc_type": "fastag", "doc_number": "FT-8821", "wallet_balance": 250},
            user=self.desk,
        )
        alerts = rental_ops.compliance_and_expiry_alerts(days_ahead=30)
        self.assertGreaterEqual(len(alerts["vehicle_compliance_alerts"]), 2)
        self.assertGreaterEqual(len(alerts["maintenance_alerts"]), 1)

    # ------------------------------------------------------------------
    # 3. Customer KYC, DL Expiry Enforcement & India DPDP Act 2023
    # ------------------------------------------------------------------
    def test_customer_dpdp_consent_export_and_erasure(self) -> None:
        # Must reject customer profile without DPDP Act 2023 consent
        with self.assertRaises(ValueError):
            rental_ops.create_customer(
                {"full_name": "No Consent User", "phone": "9876543210", "dpdp_consent": False},
                user=self.desk,
            )

        cust = rental_ops.create_customer(
            {
                "full_name": "Rohan Kulkarni",
                "phone": "9876543210",
                "email": "rohan@example.in",
                "dl_number": "MH1220180099887",
                "dl_expiry": "2029-12-31",
                "id_proof_type": "Passport",
                "id_proof_number": "Z9988776",
                "dpdp_consent": True,
            },
            user=self.desk,
        )
        self.assertEqual(cust["dpdp_consent"], 1)

        pkg = rental_ops.export_customer_dpdp_package(cust["id"], user=self.desk)
        self.assertIn("Digital Personal Data Protection Act, 2023", pkg["statute"])
        self.assertGreaterEqual(len(pkg["pii_access_log"]), 2)

        # Desk agent cannot erase PII (owner-only permission)
        with self.assertRaises(PermissionError):
            rental_ops.erase_customer_pii(cust["id"], "Customer request", user=self.desk)

        erased = rental_ops.erase_customer_pii(cust["id"], "Customer Section 12 withdrawal", user=self.owner)
        self.assertEqual(erased["dpdp_erased"], 1)
        self.assertEqual(erased["dl_number"], "REDACTED")
        self.assertEqual(erased["phone"], "")

    # ------------------------------------------------------------------
    # 4. Booking Overlap, Rate Override Audit, Lifecycle & Cancellation
    # ------------------------------------------------------------------
    def test_booking_overlap_lifecycle_and_cancellation_math(self) -> None:
        veh = rental_ops.create_vehicle(
            {"reg_number": "MH-02-CD-5566", "make": "Hyundai", "model": "Creta", "daily_rate": 3000},
            user=self.owner,
        )
        cust = rental_ops.create_customer(
            {
                "full_name": "Priya Nair",
                "phone": "9123456789",
                "dl_number": "MH0220200011223",
                "dl_expiry": "2028-05-20",
                "dpdp_consent": True,
            },
            user=self.desk,
        )

        # Rate override without reason must fail
        with self.assertRaises(ValueError):
            rental_ops.create_booking(
                {
                    "vehicle_id": veh["id"],
                    "customer_id": cust["id"],
                    "pickup_at": "2027-03-10T09:00",
                    "return_at": "2027-03-13T09:00",
                    "daily_rate": 2500,
                },
                user=self.desk,
            )

        b1 = rental_ops.create_booking(
            {
                "vehicle_id": veh["id"],
                "customer_id": cust["id"],
                "pickup_at": "2027-03-10T09:00",
                "return_at": "2027-03-13T09:00",
                "daily_rate": 2700,
                "rate_override_reason": "Corporate loyalty rate",
                "rate_approved_by": "Branch Manager",
            },
            user=self.desk,
        )
        self.assertEqual(b1["status"], "confirmed")

        # Overlapping booking on same vehicle must be rejected
        with self.assertRaises(ValueError):
            rental_ops.create_booking(
                {
                    "vehicle_id": veh["id"],
                    "customer_id": cust["id"],
                    "pickup_at": "2027-03-12T10:00",
                    "return_at": "2027-03-15T10:00",
                },
                user=self.desk,
            )

        # Availability search excludes veh during 2027-03-11..2027-03-12
        avail = rental_ops.search_available_vehicles("2027-03-11T09:00", "2027-03-12T18:00")
        self.assertEqual([v["id"] for v in avail], [])

        # Adjacent booking starting exactly at 2027-03-13T09:00 succeeds
        b2 = rental_ops.create_booking(
            {
                "vehicle_id": veh["id"],
                "customer_id": cust["id"],
                "pickup_at": "2027-03-13T09:00",
                "return_at": "2027-03-15T09:00",
            },
            user=self.desk,
        )
        # Record advance + deposit on b2 and cancel < 24h before pickup (50% of 1 day fee)
        rental_ops.record_payment(
            {"booking_id": b2["id"], "kind": "advance", "mode": "UPI", "amount": 3000, "reference_no": "UPI-1"},
            user=self.desk,
        )
        rental_ops.record_payment(
            {"booking_id": b2["id"], "kind": "deposit", "mode": "UPI", "amount": 5000, "reference_no": "UPI-2"},
            user=self.desk,
        )
        cancelled = rental_ops.transition_booking_status(
            b2["id"],
            "cancelled",
            {"cancelled_at": "2027-03-12T18:00", "cancel_reason": "Flight cancelled"},
            user=self.desk,
        )
        self.assertEqual(cancelled["cancellation_fee"], 1500.00)
        self.assertEqual(cancelled["refund_due"], 6500.00)

        # DL expiry before trip return must fail
        expired_cust = rental_ops.create_customer(
            {
                "full_name": "Expiring DL",
                "phone": "9988776655",
                "dl_number": "MH0120100001111",
                "dl_expiry": "2027-03-18",
                "dpdp_consent": True,
            },
            user=self.desk,
        )
        with self.assertRaises(ValueError):
            rental_ops.create_booking(
                {
                    "vehicle_id": veh["id"],
                    "customer_id": expired_cust["id"],
                    "pickup_at": "2027-03-16T09:00",
                    "return_at": "2027-03-20T09:00",
                },
                user=self.desk,
            )

    # ------------------------------------------------------------------
    # 5. Payment Ledger, Deposit Settlement, Immutable GST Invoices & Credit Notes
    # ------------------------------------------------------------------
    def test_payment_settlement_and_immutable_gst_invoices(self) -> None:
        veh = rental_ops.create_vehicle(
            {"reg_number": "MH-04-EF-9001", "make": "Maruti", "model": "Ertiga", "daily_rate": 2500},
            user=self.owner,
        )
        cust = rental_ops.create_customer(
            {"full_name": "Vikram Joshi", "phone": "9811122233", "dl_number": "MH042019001", "dl_expiry": "2031-01-01", "dpdp_consent": True},
            user=self.desk,
        )
        booking = rental_ops.create_booking(
            {
                "vehicle_id": veh["id"],
                "customer_id": cust["id"],
                "pickup_at": "2027-04-01T09:00",
                "return_at": "2027-04-03T09:00",
                "odometer_out": 10000,
                "security_deposit": 5000,
            },
            user=self.desk,
        )
        rental_ops.record_payment(
            {"booking_id": booking["id"], "kind": "advance", "mode": "UPI", "amount": 2000, "reference_no": "UTR101"},
            user=self.desk,
        )
        rental_ops.record_payment(
            {"booking_id": booking["id"], "kind": "deposit", "mode": "Cash", "amount": 5000},
            user=self.desk,
        )
        rental_ops.transition_booking_status(booking["id"], "picked_up", {"odometer_out": 10000}, user=self.desk)
        rental_ops.transition_booking_status(booking["id"], "returned", {"odometer_in": 10400}, user=self.desk)

        settlement = rental_ops.booking_settlement_summary(booking["id"])
        # 2 days * 2500 = 5000 + 5% GST (250) = 5250. Net received = 7000 -> refund due to customer = 1750
        self.assertEqual(settlement["bill_total"], 5250.00)
        self.assertEqual(settlement["net_received"], 7000.00)
        self.assertEqual(settlement["refund_due_to_customer"], 1750.00)

        inv1 = rental_ops.issue_gst_invoice(booking["id"], {"fy": "2027-28"}, user=self.desk)
        inv2 = rental_ops.issue_gst_invoice(booking["id"], {"fy": "2027-28"}, user=self.desk)
        self.assertEqual(inv1["invoice_number"], "FLT/2027-28/00001")
        self.assertEqual(inv2["invoice_number"], "FLT/2027-28/00002")

        # SQLite BEFORE UPDATE and BEFORE DELETE triggers must block tampering
        with db.cursor() as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("UPDATE invoices SET grand_total=100 WHERE id=?", (inv1["id"],))
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM invoices WHERE id=?", (inv1["id"],))

        # Credit Note must be sequential and also immutable
        cn = rental_ops.issue_credit_note(inv1["id"], "Goodwill discount", 1000.0, user=self.accountant)
        self.assertEqual(cn["credit_note_number"], "CN/2027-28/00001")
        self.assertEqual(cn["total_reversal"], 1050.00)

        with db.cursor() as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("DELETE FROM credit_notes WHERE id=?", (cn["id"],))

        # End-of-shift cash reconciliation
        shift = rental_ops.close_shift_reconciliation(
            {"opening_cash": 1000, "actual_closing_cash": 6000, "notes": "All cash matched"},
            user=self.desk,
        )
        self.assertEqual(shift["expected_closing_cash"], 6000.00)
        self.assertEqual(shift["cash_variance"], 0.00)

    # ------------------------------------------------------------------
    # 6. Workshop Job Cards, Annotated Damage, Signatures, Bulk Import & Security
    # ------------------------------------------------------------------
    def test_workshop_damage_signatures_import_and_upload_security(self) -> None:
        # CSV & XLSX bulk import preview + commit
        csv_bytes = (
            b"reg_number,make,model,category,fuel_type,daily_rate\n"
            b"MH-14-GH-2211,Kia,Carens,MPV,Diesel,3200\n"
            b"BAD,Kia,Seltos,SUV,Petrol,3000\n"
        )
        prev = rental_ops.preview_bulk_import("vehicles", csv_bytes, "fleet.csv")
        self.assertEqual(prev["valid_count"], 1)
        self.assertEqual(prev["error_count"], 1)
        committed = rental_ops.commit_bulk_import("vehicles", prev["valid_rows"], user=self.manager)
        self.assertEqual(committed["imported_count"], 1)
        veh = committed["records"][0]

        # XLSX customer import
        xlsx_bytes = _build_minimal_xlsx([
            ["full_name", "phone", "email", "dl_number", "dl_expiry"],
            ["Meera Iyer", "9822011223", "meera@example.in", "MH142021001", "2032-08-01"],
        ])
        c_prev = rental_ops.preview_bulk_import("customers", xlsx_bytes, "customers.xlsx")
        self.assertEqual(c_prev["valid_count"], 1)
        c_comm = rental_ops.commit_bulk_import("customers", c_prev["valid_rows"], user=self.manager)
        cust = c_comm["records"][0]

        # Workshop job card lifecycle
        jc = rental_ops.create_maintenance_job_card(
            {"vehicle_id": veh["id"], "service_type": "Brake Pad Replacement", "parts_cost": 3500, "labour_cost": 1000, "status": "in_progress"},
            user=self.desk,
        )
        self.assertEqual(rental_ops.list_vehicles(status="in_workshop")[0]["id"], veh["id"])
        rental_ops.update_maintenance_job(jc["id"], {"status": "completed"}, user=self.desk)
        self.assertEqual(rental_ops.list_vehicles(status="available")[0]["id"], veh["id"])

        # Annotated damage record
        dmg = rental_ops.create_damage_record(
            {
                "vehicle_id": veh["id"],
                "panel_location": "Rear Left Door",
                "severity": "dent",
                "estimated_cost": 2800,
                "annotation_json": [{"x": 45, "y": 80, "note": "2cm crease"}],
            },
            user=self.desk,
        )
        self.assertEqual(len(rental_ops.list_damage_records(veh["id"])), 1)
        self.assertIn("2cm crease", dmg["annotation_json"])

        # Booking + Digital signature SHA-256 verification + Profitability dashboard
        bk = rental_ops.create_booking(
            {
                "vehicle_id": veh["id"],
                "customer_id": cust["id"],
                "pickup_at": "2027-05-01T09:00",
                "return_at": "2027-05-06T09:00",
            },
            user=self.desk,
        )
        sig = rental_ops.capture_digital_signature(
            {
                "booking_id": bk["id"],
                "doc_kind": "agreement",
                "signer_role": "customer",
                "signer_name": "Meera Iyer",
                "signature_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            },
            user=self.desk,
        )
        self.assertEqual(len(sig["doc_hash"]), 64)

        dash = rental_ops.fleet_profitability_dashboard(window_days=30)
        self.assertEqual(dash["fleet_count"], 1)
        self.assertEqual(dash["total_gross_revenue"], 16000.00)
        self.assertEqual(dash["total_maintenance_cost"], 4500.00)
        self.assertEqual(dash["total_net_profit"], 11500.00)

        # Magic-byte upload validation
        with self.assertRaises(ValueError):
            attachments.validate_upload_signature("invoice.pdf", b"MZ\x90\x00executable")
        with self.assertRaises(ValueError):
            attachments.validate_upload_signature("photo.png", b"not-a-png-header")
        attachments.validate_upload_signature("contract.pdf", b"%PDF-1.7\n...")

        # Online backup & restore + key health check
        b_path = maintenance.backup_now()
        self.assertIsNotNone(b_path)
        restored = maintenance.restore(b_path.name)
        self.assertEqual(restored.name, "float-before-restore.sqlite3")
        kh = db.key_health_status()
        self.assertTrue(kh["device_key_present"])
        self.assertEqual(kh["unreadable_keys"], 0)

    # ------------------------------------------------------------------
    # 7. End-to-End HTTP API & RBAC Enforcement
    # ------------------------------------------------------------------
    def test_http_ops_endpoints_and_rbac(self) -> None:
        srv = server.serve("127.0.0.1", 0)
        port = srv.server_address[1]
        base = f"http://127.0.0.1:{port}"
        try:
            owner_tok = db.create_session(self.owner["id"], "127.0.0.1", "unittest")
            viewer_tok = db.create_session(self.viewer["id"], "127.0.0.1", "unittest")

            def req(path: str, token: str, body: dict | None = None) -> tuple[int, dict]:
                data = json.dumps(body).encode("utf-8") if body is not None else None
                headers = {"Authorization": f"Bearer {token}"}
                if data is not None:
                    headers["Content-Type"] = "application/json"
                r = urllib.request.Request(
                    base + path,
                    data=data,
                    headers=headers,
                    method="POST" if data is not None else "GET",
                )
                try:
                    with urllib.request.urlopen(r, timeout=5) as resp:
                        return resp.status, json.loads(resp.read().decode("utf-8"))
                except urllib.error.HTTPError as exc:
                    return exc.code, json.loads(exc.read().decode("utf-8"))

            status, summary = req("/api/ops/summary", owner_tok)
            self.assertEqual(status, 200)
            self.assertIn("branches", summary)

            # Read-only viewer cannot create a vehicle (403 Forbidden)
            status, err = req(
                "/api/ops/vehicles",
                viewer_tok,
                {"reg_number": "MH-01-ZZ-0001", "make": "Tata", "model": "Nexon", "daily_rate": 2200},
            )
            self.assertEqual(status, 403)

            # Owner creates vehicle via HTTP
            status, v_res = req(
                "/api/ops/vehicles",
                owner_tok,
                {"reg_number": "MH-01-ZZ-0001", "make": "Tata", "model": "Nexon", "daily_rate": 2200},
            )
            self.assertEqual(status, 200)
            self.assertTrue(v_res["ok"])

            # Admin backups list endpoint
            status, b_res = req("/api/admin/backups", owner_tok)
            self.assertEqual(status, 200)
            self.assertIn("backups", b_res)
        finally:
            srv.shutdown()
            srv.server_close()


if __name__ == "__main__":
    unittest.main()
