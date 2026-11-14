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


if __name__ == "__main__":
    unittest.main()
