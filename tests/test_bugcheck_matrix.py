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

    def test_matrix_003_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹1,051", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(4204))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_004_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹1,068", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(5340))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_005_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹1,085", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(6510))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_006_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹1,102", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7714))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_007_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹1,119", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8952))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_008_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹1,136", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10224))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_009_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹1,153", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(11530))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_010_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹1,170", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12870))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_011_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹1,187", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(14244))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_012_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹1,204", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(15652))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_013_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹1,221", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(17094))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_014_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹1,238", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(1238))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_015_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹1,255", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2510))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_016_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹1,272", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3816))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_017_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹1,289", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(5156))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_018_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹1,306", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(6530))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_019_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹1,323", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7938))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_020_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹1,340", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(9380))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_021_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹1,357", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10856))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_022_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹1,374", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12366))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_023_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹1,391", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(13910))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_024_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹1,408", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(15488))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_025_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹1,425", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(17100))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_026_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹1,442", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(18746))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_027_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹1,459", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(20426))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_028_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹1,476", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(1476))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_029_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹1,493", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2986))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_030_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹1,510", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(4530))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_031_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹1,527", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(6108))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_032_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹1,544", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7720))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_033_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹1,561", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(9366))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_034_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹1,578", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(11046))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_035_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹1,595", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12760))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_036_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹1,612", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(14508))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_037_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹1,629", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16290))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_038_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹1,646", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(18106))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_039_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹1,663", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(19956))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_040_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹1,680", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(21840))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_041_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹1,697", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(23758))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_042_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹1,714", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(1714))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_043_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹1,731", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3462))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_044_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹1,748", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(5244))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_045_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹1,765", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7060))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_046_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹1,782", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8910))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_047_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹1,799", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10794))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_048_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹1,816", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12712))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_049_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹1,833", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(14664))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_050_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹1,850", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16650))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_051_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹1,867", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(18670))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_052_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹1,884", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(20724))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_053_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹1,901", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(22812))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_054_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹1,918", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(24934))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_055_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹1,935", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(27090))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_056_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹1,952", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(1952))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_057_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹1,969", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3938))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_058_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹1,986", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(5958))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_059_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹2,003", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8012))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_060_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹2,020", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10100))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_061_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹2,037", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12222))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_062_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹2,054", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(14378))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_063_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹2,071", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16568))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_064_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹2,088", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(18792))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_065_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹2,105", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(21050))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_066_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹2,122", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(23342))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_067_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹2,139", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(25668))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_068_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹2,156", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(28028))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_069_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹2,173", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(30422))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_070_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹2,190", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2190))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_071_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹2,207", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(4414))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_072_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹2,224", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(6672))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_073_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹2,241", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8964))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_074_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹2,258", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(11290))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_075_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹2,275", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(13650))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_076_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹2,292", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16044))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_077_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹2,309", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(18472))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_078_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹2,326", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(20934))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_079_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹2,343", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(23430))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_080_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹2,360", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(25960))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_081_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹2,377", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(28524))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_082_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹2,394", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(31122))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_083_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹2,411", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(33754))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_084_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹2,428", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2428))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_085_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹2,445", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(4890))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_086_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹2,462", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7386))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_087_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹2,479", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(9916))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_088_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹2,496", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12480))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_089_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹2,513", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(15078))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_090_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹2,530", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(17710))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_091_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹2,547", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(20376))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_092_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹2,564", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(23076))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_093_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹2,581", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(25810))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_094_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹2,598", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(28578))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_095_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹2,615", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(31380))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_096_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹2,632", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(34216))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_097_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹2,649", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(37086))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_098_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹2,666", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2666))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_099_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹2,683", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(5366))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_100_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹2,700", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8100))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_101_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹2,717", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10868))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_102_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹2,734", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(13670))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_103_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹2,751", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16506))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_104_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹2,768", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(19376))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_105_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹2,785", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(22280))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_106_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹2,802", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(25218))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_107_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹2,819", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(28190))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_108_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹2,836", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(31196))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_109_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹2,853", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(34236))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_110_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹2,870", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(37310))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_111_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹2,887", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(40418))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_112_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹2,904", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(2904))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_113_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹2,921", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(5842))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_114_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹2,938", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8814))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_115_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹2,955", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(11820))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_116_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹2,972", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(14860))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_117_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹2,989", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(17934))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_118_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹3,006", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(21042))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_119_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹3,023", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(24184))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_120_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹3,040", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(27360))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_121_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹3,057", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(30570))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_122_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹3,074", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(33814))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_123_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹3,091", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(37092))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_124_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹3,108", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(40404))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_125_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹3,125", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(43750))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_126_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹3,142", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3142))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_127_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹3,159", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(6318))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_128_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹3,176", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(9528))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_129_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹3,193", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12772))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_130_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹3,210", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16050))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_131_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹3,227", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(19362))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_132_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹3,244", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(22708))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_133_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹3,261", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(26088))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_134_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹3,278", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(29502))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_135_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹3,295", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(32950))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_136_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹3,312", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(36432))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_137_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹3,329", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(39948))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_138_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹3,346", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(43498))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_139_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹3,363", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(47082))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_140_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹3,380", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3380))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_141_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹3,397", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(6794))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_142_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹3,414", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10242))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_143_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹3,431", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(13724))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_144_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹3,448", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(17240))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_145_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹3,465", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(20790))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_146_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹3,482", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(24374))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_147_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹3,499", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(27992))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_148_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹3,516", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(31644))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_149_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹3,533", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(35330))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_150_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹3,550", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(39050))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_151_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹3,567", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(42804))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_152_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹3,584", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(46592))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_153_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹3,601", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(50414))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_154_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹3,618", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3618))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_155_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹3,635", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7270))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_156_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹3,652", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(10956))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_157_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹3,669", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(14676))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_158_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹3,686", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(18430))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_159_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹3,703", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(22218))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_160_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹3,720", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(26040))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_161_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹3,737", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(29896))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_162_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹3,754", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(33786))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_163_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹3,771", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(37710))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_164_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹3,788", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(41668))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_165_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹3,805", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(45660))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_166_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹3,822", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(49686))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])


if __name__ == "__main__":
    unittest.main()
