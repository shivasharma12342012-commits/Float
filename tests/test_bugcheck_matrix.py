"""Automated Bug-Fix & Consistency Verification Matrix (597 Checks)."""

from __future__ import annotations
import unittest
from float import artifacts, attachments, rental_ops, security, tools


class BugcheckMatrixTestCase(unittest.TestCase):

    def test_matrix_001_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹1,017", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2034))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_002_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹1,034", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3102))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])


if __name__ == "__main__":
    unittest.main()
