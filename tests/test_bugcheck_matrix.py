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

    def test_matrix_167_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹3,839", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(53746))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_168_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹3,856", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(3856))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_169_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹3,873", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(7746))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_170_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹3,890", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(11670))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_171_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹3,907", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(15628))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_172_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹3,924", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(19620))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_173_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹3,941", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(23646))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_174_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹3,958", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(27706))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_175_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹3,975", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(31800))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_176_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹3,992", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(35928))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_177_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹4,009", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(40090))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_178_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹4,026", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(44286))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_179_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹4,043", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(48516))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_180_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹4,060", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(52780))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_181_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹4,077", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(57078))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_182_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹4,094", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(4094))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_183_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹4,111", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8222))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_184_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹4,128", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(12384))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_185_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹4,145", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(16580))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_186_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹4,162", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(20810))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_187_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 6, "daily_rate": "₹4,179", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(25074))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_188_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 7, "daily_rate": "₹4,196", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(29372))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_189_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 8, "daily_rate": "₹4,213", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(33704))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_190_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 9, "daily_rate": "₹4,230", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(38070))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_191_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 10, "daily_rate": "₹4,247", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(42470))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_192_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 11, "daily_rate": "₹4,264", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(46904))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_193_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 12, "daily_rate": "₹4,281", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(51372))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_194_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 13, "daily_rate": "₹4,298", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(55874))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_195_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 14, "daily_rate": "₹4,315", "gst_percent": 18, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(60410))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_196_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 1, "daily_rate": "₹4,332", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(4332))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_197_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 2, "daily_rate": "₹4,349", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(8698))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_198_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 3, "daily_rate": "₹4,366", "gst_percent": 5, "inter_state": True, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(13098))
        if True:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_199_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 4, "daily_rate": "₹4,383", "gst_percent": 18, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(17532))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_200_tariff_and_gst_split(self) -> None:
        q = rental_ops.calculate_tariff_exact({"days": 5, "daily_rate": "₹4,400", "gst_percent": 5, "inter_state": False, "security_deposit": 5000})
        self.assertEqual(q["base_rent"], float(22000))
        if False:
            self.assertEqual(q["igst_amount"], q["gst_amount"])
            self.assertEqual(q["cgst_amount"], 0.0)
        else:
            self.assertEqual(round(q["cgst_amount"] + q["sgst_amount"], 2), q["gst_amount"])

    def test_matrix_201_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 2 ab 1001")
        self.assertEqual(plate, "DL-02-AB-1001")
        user = {"id": 1, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_202_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 3 ab 1002")
        self.assertEqual(plate, "KA-03-AB-1002")
        user = {"id": 2, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_203_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 4 ab 1003")
        self.assertEqual(plate, "TN-04-AB-1003")
        user = {"id": 3, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_204_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 5 ab 1004")
        self.assertEqual(plate, "GJ-05-AB-1004")
        user = {"id": 4, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_205_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 6 ab 1005")
        self.assertEqual(plate, "TS-06-AB-1005")
        user = {"id": 5, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_206_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 7 ab 1006")
        self.assertEqual(plate, "UP-07-AB-1006")
        user = {"id": 6, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_207_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 8 ab 1007")
        self.assertEqual(plate, "RJ-08-AB-1007")
        user = {"id": 7, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_208_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 9 ab 1008")
        self.assertEqual(plate, "WB-09-AB-1008")
        user = {"id": 8, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_209_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 10 ab 1009")
        self.assertEqual(plate, "KL-10-AB-1009")
        user = {"id": 9, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_210_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 11 ab 1010")
        self.assertEqual(plate, "MH-11-AB-1010")
        user = {"id": 10, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_211_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 12 ab 1011")
        self.assertEqual(plate, "DL-12-AB-1011")
        user = {"id": 11, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_212_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 13 ab 1012")
        self.assertEqual(plate, "KA-13-AB-1012")
        user = {"id": 12, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_213_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 14 ab 1013")
        self.assertEqual(plate, "TN-14-AB-1013")
        user = {"id": 13, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_214_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 15 ab 1014")
        self.assertEqual(plate, "GJ-15-AB-1014")
        user = {"id": 14, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_215_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 16 ab 1015")
        self.assertEqual(plate, "TS-16-AB-1015")
        user = {"id": 15, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_216_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 17 ab 1016")
        self.assertEqual(plate, "UP-17-AB-1016")
        user = {"id": 16, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_217_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 18 ab 1017")
        self.assertEqual(plate, "RJ-18-AB-1017")
        user = {"id": 17, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_218_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 19 ab 1018")
        self.assertEqual(plate, "WB-19-AB-1018")
        user = {"id": 18, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_219_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 20 ab 1019")
        self.assertEqual(plate, "KL-20-AB-1019")
        user = {"id": 19, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_220_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 21 ab 1020")
        self.assertEqual(plate, "MH-21-AB-1020")
        user = {"id": 20, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_221_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 22 ab 1021")
        self.assertEqual(plate, "DL-22-AB-1021")
        user = {"id": 21, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_222_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 23 ab 1022")
        self.assertEqual(plate, "KA-23-AB-1022")
        user = {"id": 22, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_223_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 24 ab 1023")
        self.assertEqual(plate, "TN-24-AB-1023")
        user = {"id": 23, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_224_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 25 ab 1024")
        self.assertEqual(plate, "GJ-25-AB-1024")
        user = {"id": 24, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_225_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 26 ab 1025")
        self.assertEqual(plate, "TS-26-AB-1025")
        user = {"id": 25, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_226_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 27 ab 1026")
        self.assertEqual(plate, "UP-27-AB-1026")
        user = {"id": 26, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_227_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 28 ab 1027")
        self.assertEqual(plate, "RJ-28-AB-1027")
        user = {"id": 27, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_228_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 29 ab 1028")
        self.assertEqual(plate, "WB-29-AB-1028")
        user = {"id": 28, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_229_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 30 ab 1029")
        self.assertEqual(plate, "KL-30-AB-1029")
        user = {"id": 29, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_230_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 31 ab 1030")
        self.assertEqual(plate, "MH-31-AB-1030")
        user = {"id": 30, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_231_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 32 ab 1031")
        self.assertEqual(plate, "DL-32-AB-1031")
        user = {"id": 31, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_232_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 33 ab 1032")
        self.assertEqual(plate, "KA-33-AB-1032")
        user = {"id": 32, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_233_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 34 ab 1033")
        self.assertEqual(plate, "TN-34-AB-1033")
        user = {"id": 33, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_234_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 35 ab 1034")
        self.assertEqual(plate, "GJ-35-AB-1034")
        user = {"id": 34, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_235_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 36 ab 1035")
        self.assertEqual(plate, "TS-36-AB-1035")
        user = {"id": 35, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_236_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 37 ab 1036")
        self.assertEqual(plate, "UP-37-AB-1036")
        user = {"id": 36, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_237_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 38 ab 1037")
        self.assertEqual(plate, "RJ-38-AB-1037")
        user = {"id": 37, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_238_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 39 ab 1038")
        self.assertEqual(plate, "WB-39-AB-1038")
        user = {"id": 38, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_239_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 40 ab 1039")
        self.assertEqual(plate, "KL-40-AB-1039")
        user = {"id": 39, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_240_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 41 ab 1040")
        self.assertEqual(plate, "MH-41-AB-1040")
        user = {"id": 40, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_241_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 42 ab 1041")
        self.assertEqual(plate, "DL-42-AB-1041")
        user = {"id": 41, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_242_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 43 ab 1042")
        self.assertEqual(plate, "KA-43-AB-1042")
        user = {"id": 42, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_243_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 44 ab 1043")
        self.assertEqual(plate, "TN-44-AB-1043")
        user = {"id": 43, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_244_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 45 ab 1044")
        self.assertEqual(plate, "GJ-45-AB-1044")
        user = {"id": 44, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_245_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 46 ab 1045")
        self.assertEqual(plate, "TS-46-AB-1045")
        user = {"id": 45, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_246_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 47 ab 1046")
        self.assertEqual(plate, "UP-47-AB-1046")
        user = {"id": 46, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_247_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 48 ab 1047")
        self.assertEqual(plate, "RJ-48-AB-1047")
        user = {"id": 47, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_248_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 49 ab 1048")
        self.assertEqual(plate, "WB-49-AB-1048")
        user = {"id": 48, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_249_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 50 ab 1049")
        self.assertEqual(plate, "KL-50-AB-1049")
        user = {"id": 49, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_250_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 1 ab 1050")
        self.assertEqual(plate, "MH-01-AB-1050")
        user = {"id": 50, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_251_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 2 ab 1051")
        self.assertEqual(plate, "DL-02-AB-1051")
        user = {"id": 51, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_252_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 3 ab 1052")
        self.assertEqual(plate, "KA-03-AB-1052")
        user = {"id": 52, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_253_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 4 ab 1053")
        self.assertEqual(plate, "TN-04-AB-1053")
        user = {"id": 53, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_254_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 5 ab 1054")
        self.assertEqual(plate, "GJ-05-AB-1054")
        user = {"id": 54, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_255_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 6 ab 1055")
        self.assertEqual(plate, "TS-06-AB-1055")
        user = {"id": 55, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_256_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 7 ab 1056")
        self.assertEqual(plate, "UP-07-AB-1056")
        user = {"id": 56, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_257_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 8 ab 1057")
        self.assertEqual(plate, "RJ-08-AB-1057")
        user = {"id": 57, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_258_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 9 ab 1058")
        self.assertEqual(plate, "WB-09-AB-1058")
        user = {"id": 58, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_259_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 10 ab 1059")
        self.assertEqual(plate, "KL-10-AB-1059")
        user = {"id": 59, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_260_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 11 ab 1060")
        self.assertEqual(plate, "MH-11-AB-1060")
        user = {"id": 60, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_261_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 12 ab 1061")
        self.assertEqual(plate, "DL-12-AB-1061")
        user = {"id": 61, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_262_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 13 ab 1062")
        self.assertEqual(plate, "KA-13-AB-1062")
        user = {"id": 62, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_263_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 14 ab 1063")
        self.assertEqual(plate, "TN-14-AB-1063")
        user = {"id": 63, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_264_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 15 ab 1064")
        self.assertEqual(plate, "GJ-15-AB-1064")
        user = {"id": 64, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_265_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 16 ab 1065")
        self.assertEqual(plate, "TS-16-AB-1065")
        user = {"id": 65, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_266_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 17 ab 1066")
        self.assertEqual(plate, "UP-17-AB-1066")
        user = {"id": 66, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_267_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 18 ab 1067")
        self.assertEqual(plate, "RJ-18-AB-1067")
        user = {"id": 67, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_268_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 19 ab 1068")
        self.assertEqual(plate, "WB-19-AB-1068")
        user = {"id": 68, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_269_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 20 ab 1069")
        self.assertEqual(plate, "KL-20-AB-1069")
        user = {"id": 69, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_270_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 21 ab 1070")
        self.assertEqual(plate, "MH-21-AB-1070")
        user = {"id": 70, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_271_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 22 ab 1071")
        self.assertEqual(plate, "DL-22-AB-1071")
        user = {"id": 71, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_272_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 23 ab 1072")
        self.assertEqual(plate, "KA-23-AB-1072")
        user = {"id": 72, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_273_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 24 ab 1073")
        self.assertEqual(plate, "TN-24-AB-1073")
        user = {"id": 73, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_274_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 25 ab 1074")
        self.assertEqual(plate, "GJ-25-AB-1074")
        user = {"id": 74, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_275_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 26 ab 1075")
        self.assertEqual(plate, "TS-26-AB-1075")
        user = {"id": 75, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_276_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 27 ab 1076")
        self.assertEqual(plate, "UP-27-AB-1076")
        user = {"id": 76, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_277_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 28 ab 1077")
        self.assertEqual(plate, "RJ-28-AB-1077")
        user = {"id": 77, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_278_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 29 ab 1078")
        self.assertEqual(plate, "WB-29-AB-1078")
        user = {"id": 78, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_279_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 30 ab 1079")
        self.assertEqual(plate, "KL-30-AB-1079")
        user = {"id": 79, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_280_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 31 ab 1080")
        self.assertEqual(plate, "MH-31-AB-1080")
        user = {"id": 80, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_281_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 32 ab 1081")
        self.assertEqual(plate, "DL-32-AB-1081")
        user = {"id": 81, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_282_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 33 ab 1082")
        self.assertEqual(plate, "KA-33-AB-1082")
        user = {"id": 82, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_283_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 34 ab 1083")
        self.assertEqual(plate, "TN-34-AB-1083")
        user = {"id": 83, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_284_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 35 ab 1084")
        self.assertEqual(plate, "GJ-35-AB-1084")
        user = {"id": 84, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_285_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 36 ab 1085")
        self.assertEqual(plate, "TS-36-AB-1085")
        user = {"id": 85, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_286_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 37 ab 1086")
        self.assertEqual(plate, "UP-37-AB-1086")
        user = {"id": 86, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_287_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 38 ab 1087")
        self.assertEqual(plate, "RJ-38-AB-1087")
        user = {"id": 87, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_288_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 39 ab 1088")
        self.assertEqual(plate, "WB-39-AB-1088")
        user = {"id": 88, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_289_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 40 ab 1089")
        self.assertEqual(plate, "KL-40-AB-1089")
        user = {"id": 89, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_290_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 41 ab 1090")
        self.assertEqual(plate, "MH-41-AB-1090")
        user = {"id": 90, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_291_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 42 ab 1091")
        self.assertEqual(plate, "DL-42-AB-1091")
        user = {"id": 91, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_292_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 43 ab 1092")
        self.assertEqual(plate, "KA-43-AB-1092")
        user = {"id": 92, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_293_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 44 ab 1093")
        self.assertEqual(plate, "TN-44-AB-1093")
        user = {"id": 93, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_294_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 45 ab 1094")
        self.assertEqual(plate, "GJ-45-AB-1094")
        user = {"id": 94, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_295_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 46 ab 1095")
        self.assertEqual(plate, "TS-46-AB-1095")
        user = {"id": 95, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_296_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 47 ab 1096")
        self.assertEqual(plate, "UP-47-AB-1096")
        user = {"id": 96, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_297_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 48 ab 1097")
        self.assertEqual(plate, "RJ-48-AB-1097")
        user = {"id": 97, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_298_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 49 ab 1098")
        self.assertEqual(plate, "WB-49-AB-1098")
        user = {"id": 98, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_299_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 50 ab 1099")
        self.assertEqual(plate, "KL-50-AB-1099")
        user = {"id": 99, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_300_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 1 ab 1100")
        self.assertEqual(plate, "MH-01-AB-1100")
        user = {"id": 100, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_301_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 2 ab 1101")
        self.assertEqual(plate, "DL-02-AB-1101")
        user = {"id": 101, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_302_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 3 ab 1102")
        self.assertEqual(plate, "KA-03-AB-1102")
        user = {"id": 102, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_303_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 4 ab 1103")
        self.assertEqual(plate, "TN-04-AB-1103")
        user = {"id": 103, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_304_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 5 ab 1104")
        self.assertEqual(plate, "GJ-05-AB-1104")
        user = {"id": 104, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_305_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 6 ab 1105")
        self.assertEqual(plate, "TS-06-AB-1105")
        user = {"id": 105, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_306_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 7 ab 1106")
        self.assertEqual(plate, "UP-07-AB-1106")
        user = {"id": 106, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_307_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 8 ab 1107")
        self.assertEqual(plate, "RJ-08-AB-1107")
        user = {"id": 107, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_308_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 9 ab 1108")
        self.assertEqual(plate, "WB-09-AB-1108")
        user = {"id": 108, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_309_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 10 ab 1109")
        self.assertEqual(plate, "KL-10-AB-1109")
        user = {"id": 109, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_310_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 11 ab 1110")
        self.assertEqual(plate, "MH-11-AB-1110")
        user = {"id": 110, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_311_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 12 ab 1111")
        self.assertEqual(plate, "DL-12-AB-1111")
        user = {"id": 111, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_312_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 13 ab 1112")
        self.assertEqual(plate, "KA-13-AB-1112")
        user = {"id": 112, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_313_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 14 ab 1113")
        self.assertEqual(plate, "TN-14-AB-1113")
        user = {"id": 113, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_314_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 15 ab 1114")
        self.assertEqual(plate, "GJ-15-AB-1114")
        user = {"id": 114, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_315_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 16 ab 1115")
        self.assertEqual(plate, "TS-16-AB-1115")
        user = {"id": 115, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_316_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 17 ab 1116")
        self.assertEqual(plate, "UP-17-AB-1116")
        user = {"id": 116, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_317_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 18 ab 1117")
        self.assertEqual(plate, "RJ-18-AB-1117")
        user = {"id": 117, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_318_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 19 ab 1118")
        self.assertEqual(plate, "WB-19-AB-1118")
        user = {"id": 118, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_319_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 20 ab 1119")
        self.assertEqual(plate, "KL-20-AB-1119")
        user = {"id": 119, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_320_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 21 ab 1120")
        self.assertEqual(plate, "MH-21-AB-1120")
        user = {"id": 120, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_321_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 22 ab 1121")
        self.assertEqual(plate, "DL-22-AB-1121")
        user = {"id": 121, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_322_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 23 ab 1122")
        self.assertEqual(plate, "KA-23-AB-1122")
        user = {"id": 122, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_323_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 24 ab 1123")
        self.assertEqual(plate, "TN-24-AB-1123")
        user = {"id": 123, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_324_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 25 ab 1124")
        self.assertEqual(plate, "GJ-25-AB-1124")
        user = {"id": 124, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_325_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 26 ab 1125")
        self.assertEqual(plate, "TS-26-AB-1125")
        user = {"id": 125, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_326_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 27 ab 1126")
        self.assertEqual(plate, "UP-27-AB-1126")
        user = {"id": 126, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_327_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 28 ab 1127")
        self.assertEqual(plate, "RJ-28-AB-1127")
        user = {"id": 127, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_328_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 29 ab 1128")
        self.assertEqual(plate, "WB-29-AB-1128")
        user = {"id": 128, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_329_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 30 ab 1129")
        self.assertEqual(plate, "KL-30-AB-1129")
        user = {"id": 129, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_330_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 31 ab 1130")
        self.assertEqual(plate, "MH-31-AB-1130")
        user = {"id": 130, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_331_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 32 ab 1131")
        self.assertEqual(plate, "DL-32-AB-1131")
        user = {"id": 131, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_332_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 33 ab 1132")
        self.assertEqual(plate, "KA-33-AB-1132")
        user = {"id": 132, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_333_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 34 ab 1133")
        self.assertEqual(plate, "TN-34-AB-1133")
        user = {"id": 133, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_334_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 35 ab 1134")
        self.assertEqual(plate, "GJ-35-AB-1134")
        user = {"id": 134, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_335_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 36 ab 1135")
        self.assertEqual(plate, "TS-36-AB-1135")
        user = {"id": 135, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_336_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 37 ab 1136")
        self.assertEqual(plate, "UP-37-AB-1136")
        user = {"id": 136, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_337_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 38 ab 1137")
        self.assertEqual(plate, "RJ-38-AB-1137")
        user = {"id": 137, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_338_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 39 ab 1138")
        self.assertEqual(plate, "WB-39-AB-1138")
        user = {"id": 138, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_339_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 40 ab 1139")
        self.assertEqual(plate, "KL-40-AB-1139")
        user = {"id": 139, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_340_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 41 ab 1140")
        self.assertEqual(plate, "MH-41-AB-1140")
        user = {"id": 140, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_341_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("dl 42 ab 1141")
        self.assertEqual(plate, "DL-42-AB-1141")
        user = {"id": 141, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_342_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ka 43 ab 1142")
        self.assertEqual(plate, "KA-43-AB-1142")
        user = {"id": 142, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_343_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("tn 44 ab 1143")
        self.assertEqual(plate, "TN-44-AB-1143")
        user = {"id": 143, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_344_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("gj 45 ab 1144")
        self.assertEqual(plate, "GJ-45-AB-1144")
        user = {"id": 144, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_345_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("ts 46 ab 1145")
        self.assertEqual(plate, "TS-46-AB-1145")
        user = {"id": 145, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_346_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("up 47 ab 1146")
        self.assertEqual(plate, "UP-47-AB-1146")
        user = {"id": 146, "role": "teacher", "ops_role": "manager"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_347_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("rj 48 ab 1147")
        self.assertEqual(plate, "RJ-48-AB-1147")
        user = {"id": 147, "role": "teacher", "ops_role": "desk_agent"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_348_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("wb 49 ab 1148")
        self.assertEqual(plate, "WB-49-AB-1148")
        user = {"id": 148, "role": "teacher", "ops_role": "accountant"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_349_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("kl 50 ab 1149")
        self.assertEqual(plate, "KL-50-AB-1149")
        user = {"id": 149, "role": "teacher", "ops_role": "read_only"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), False)

    def test_matrix_350_plate_normalization_and_rbac(self) -> None:
        plate = rental_ops.normalize_reg_plate("mh 1 ab 1150")
        self.assertEqual(plate, "MH-01-AB-1150")
        user = {"id": 150, "role": "teacher", "ops_role": "owner"}
        self.assertEqual(rental_ops.has_permission(user, "booking.write"), True)

    def test_matrix_351_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_1..\\bad/1", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0001abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_352_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_2..\\bad/2", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0002abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_353_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_3..\\bad/3", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0003abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_354_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_4..\\bad/4", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0004abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_355_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_5..\\bad/5", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0005abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_356_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_6..\\bad/6", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0006abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_357_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_7..\\bad/7", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0007abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_358_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_8..\\bad/8", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0008abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_359_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_9..\\bad/9", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0009abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_360_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_10..\\bad/10", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0010abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_361_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_11..\\bad/11", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0011abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_362_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_12..\\bad/12", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0012abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_363_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_13..\\bad/13", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0013abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_364_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_14..\\bad/14", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0014abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_365_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_15..\\bad/15", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0015abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_366_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_16..\\bad/16", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0016abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_367_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_17..\\bad/17", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0017abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_368_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_18..\\bad/18", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0018abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_369_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_19..\\bad/19", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0019abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_370_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_20..\\bad/20", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0020abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_371_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_21..\\bad/21", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0021abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_372_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_22..\\bad/22", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0022abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_373_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_23..\\bad/23", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0023abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_374_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_24..\\bad/24", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0024abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_375_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_25..\\bad/25", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0025abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_376_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_26..\\bad/26", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0026abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_377_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_27..\\bad/27", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0027abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_378_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_28..\\bad/28", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0028abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_379_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_29..\\bad/29", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0029abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_380_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_30..\\bad/30", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0030abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_381_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_31..\\bad/31", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0031abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_382_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_32..\\bad/32", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0032abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_383_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_33..\\bad/33", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0033abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_384_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_34..\\bad/34", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0034abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_385_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_35..\\bad/35", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0035abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_386_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_36..\\bad/36", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0036abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_387_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_37..\\bad/37", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0037abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_388_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_38..\\bad/38", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0038abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_389_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_39..\\bad/39", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0039abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_390_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_40..\\bad/40", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0040abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_391_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_41..\\bad/41", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0041abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_392_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_42..\\bad/42", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0042abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_393_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_43..\\bad/43", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0043abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_394_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_44..\\bad/44", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0044abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_395_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_45..\\bad/45", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0045abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_396_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_46..\\bad/46", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0046abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_397_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_47..\\bad/47", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0047abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_398_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_48..\\bad/48", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0048abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_399_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_49..\\bad/49", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0049abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_400_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_50..\\bad/50", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0050abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_401_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_51..\\bad/51", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0051abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_402_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_52..\\bad/52", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0052abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_403_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_53..\\bad/53", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0053abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_404_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_54..\\bad/54", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0054abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_405_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_55..\\bad/55", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0055abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_406_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_56..\\bad/56", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0056abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_407_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_57..\\bad/57", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0057abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_408_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_58..\\bad/58", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0058abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_409_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_59..\\bad/59", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0059abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_410_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_60..\\bad/60", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0060abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_411_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_61..\\bad/61", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0061abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_412_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_62..\\bad/62", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0062abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_413_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_63..\\bad/63", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0063abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_414_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_64..\\bad/64", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0064abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_415_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_65..\\bad/65", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0065abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_416_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_66..\\bad/66", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0066abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_417_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_67..\\bad/67", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0067abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_418_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_68..\\bad/68", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0068abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_419_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_69..\\bad/69", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0069abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_420_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_70..\\bad/70", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0070abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_421_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_71..\\bad/71", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0071abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_422_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_72..\\bad/72", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0072abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_423_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_73..\\bad/73", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0073abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_424_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_74..\\bad/74", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0074abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_425_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_75..\\bad/75", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0075abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_426_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_76..\\bad/76", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0076abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_427_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_77..\\bad/77", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0077abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_428_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_78..\\bad/78", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0078abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_429_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_79..\\bad/79", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0079abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_430_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_80..\\bad/80", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0080abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_431_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_81..\\bad/81", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0081abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_432_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_82..\\bad/82", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0082abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_433_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_83..\\bad/83", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0083abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_434_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_84..\\bad/84", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0084abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_435_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_85..\\bad/85", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0085abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_436_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_86..\\bad/86", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0086abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_437_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_87..\\bad/87", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0087abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_438_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_88..\\bad/88", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0088abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_439_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_89..\\bad/89", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0089abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_440_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_90..\\bad/90", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0090abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_441_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_91..\\bad/91", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0091abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_442_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_92..\\bad/92", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0092abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_443_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_93..\\bad/93", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0093abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_444_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_94..\\bad/94", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0094abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_445_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_95..\\bad/95", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0095abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_446_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_96..\\bad/96", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0096abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_447_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_97..\\bad/97", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0097abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_448_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_98..\\bad/98", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0098abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_449_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_99..\\bad/99", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0099abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_450_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_100..\\bad/100", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0100abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_451_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_101..\\bad/101", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0101abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_452_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_102..\\bad/102", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0102abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_453_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_103..\\bad/103", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0103abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_454_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_104..\\bad/104", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0104abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_455_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_105..\\bad/105", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0105abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_456_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_106..\\bad/106", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0106abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_457_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_107..\\bad/107", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0107abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_458_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_108..\\bad/108", ".pdf")
        self.assertTrue(cleaned.endswith(".pdf"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0108abcd")
        self.assertNotIn("secretkey", masked)

    def test_matrix_459_security_and_safe_filename(self) -> None:
        cleaned = artifacts.safe_name("Invoice_109..\\bad/109", ".xlsx")
        self.assertTrue(cleaned.endswith(".xlsx"))
        self.assertNotIn("..", cleaned)
        masked = security.mask_key("sk-proj-secretkey0109abcd")
        self.assertNotIn("secretkey", masked)


if __name__ == "__main__":
    unittest.main()
