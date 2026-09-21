# BABA FY2026 연간 영업손익·매출·영업이익률 SEC 공시 실측 독립 검증 스위트
import unittest
import os
import json
import re


class TestBabaG1TTM(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.results_file = os.path.join(base_dir, "baba_g1_results.json")
        cls.evidence_file = os.path.join(base_dir, "_raw", "extracted_baba_ttm.json")
        cls.cik_file = os.path.join(base_dir, "..", "f6-avail-15b", "_raw", "CIK0001577552_BABA.json")
        cls.html_20f = os.path.join(base_dir, "..", "offb-24", "_raw", "baba-20260331.htm")
        
        with open(cls.results_file, "r", encoding="utf-8") as f:
            cls.results = json.load(f)
        with open(cls.evidence_file, "r", encoding="utf-8") as f:
            cls.evidence = json.load(f)

    def test_01_operating_income_values_and_concept(self):
        """Test 1: Operating income is RMB 50,150M ($7,270M) under us-gaap:OperatingIncomeLoss."""
        op_res = self.results["survey_findings"]["operating_income"]
        self.assertEqual(op_res["concept"], "us-gaap:OperatingIncomeLoss")
        self.assertEqual(op_res["amount_rmb"], 50150000000)
        self.assertEqual(op_res["amount_usd_convenience"], 7270000000)
        self.assertIn("50,150", op_res["amount_rmb_formatted"])
        self.assertIn("7,270", op_res["amount_usd_formatted"])
        self.assertEqual(op_res["three_way_classification"], "공시되어 있었고 확인됨 (disclosed_and_found)")

    def test_02_revenue_values_and_concept(self):
        """Test 2: Revenues are RMB 1,023,670M ($148,401M) under us-gaap:Revenues."""
        rev_res = self.results["survey_findings"]["revenue"]
        self.assertEqual(rev_res["concept"], "us-gaap:Revenues")
        self.assertEqual(rev_res["amount_rmb"], 1023670000000)
        self.assertEqual(rev_res["amount_usd_convenience"], 148401000000)
        self.assertIn("1,023,670", rev_res["amount_rmb_formatted"])
        self.assertIn("148,401", rev_res["amount_usd_formatted"])
        self.assertEqual(rev_res["three_way_classification"], "공시되어 있었고 확인됨 (disclosed_and_found)")

    def test_03_operating_margin_and_cancellation(self):
        """Test 3: Operating margin is 4.90% with exchange rate cancellation verified."""
        margin_res = self.results["survey_findings"]["operating_margin"]
        self.assertAlmostEqual(margin_res["rmb_percentage"], 4.898998691, places=5)
        self.assertAlmostEqual(margin_res["usd_percentage"], 4.898888821, places=5)
        self.assertEqual(margin_res["formatted"], "4.90%")
        self.assertIn("약분", margin_res["exchange_rate_cancellation"])

    def test_04_html_income_statement_table_match(self):
        """Test 4: 20-F HTML contains exact Income from operations and Revenue row items."""
        self.assertTrue(os.path.exists(self.html_20f), f"File {self.html_20f} must exist")
        with open(self.html_20f, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        self.assertIn("ALIBABA GROUP HOLDING LIMITED", content)
        self.assertIn("1,023,670", content)
        self.assertIn("50,150", content)
        self.assertIn("Income from operations", content)

    def test_05_convenience_translation_rate_note_2a(self):
        """Test 5: Note 2(a) discloses convenience translation exchange rate US$1.00 = RMB 6.8980."""
        with open(self.html_20f, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        self.assertIn("6.8980", content)
        self.assertIn("Federal Reserve Board", content)
        
        note_res = self.results["convenience_translation_basis"]
        self.assertEqual(note_res["rate_usd_to_rmb"], 6.8980)

    def test_06_absence_of_10q_and_quarterly_entries(self):
        """Test 6: CIK0001577552_BABA.json contains 0 Form 10-Q entries and 0 recent quarterly fps."""
        self.assertTrue(os.path.exists(self.cik_file), f"File {self.cik_file} must exist")
        with open(self.cik_file, "r", encoding="utf-8") as f:
            cik_data = json.load(f)
        
        facts = cik_data.get("facts", {}).get("us-gaap", {})
        # Check OperatingIncomeLoss and Revenues entries
        for concept in ["OperatingIncomeLoss", "Revenues"]:
            entries = facts.get(concept, {}).get("units", {}).get("CNY", [])
            recent_entries = [e for e in entries if any(y in e.get("end", "") for y in ["2024", "2025", "2026"])]
            for e in recent_entries:
                self.assertEqual(e.get("form"), "20-F", "Recent entries must be Form 20-F")
                self.assertEqual(e.get("fp"), "FY", "Recent entries must have fiscal period FY")

    def test_07_declared_period_basis_annual(self):
        """Test 7: Declared period_basis is annual with structural rationale."""
        basis_res = self.results["period_basis"]
        self.assertEqual(basis_res["declared_basis"], "annual")
        self.assertIn("Foreign Private Issuer", basis_res["structural_reason"])
        self.assertIn("10-Q", basis_res["structural_reason"])

    def test_08_taxonomy_is_us_gaap(self):
        """Test 8: Taxonomy used is us-gaap and not ifrs-full."""
        tax = self.results["taxonomy"]
        self.assertEqual(tax["used"], "us-gaap")
        self.assertEqual(tax["operating_income_concept"], "us-gaap:OperatingIncomeLoss")
        self.assertEqual(tax["revenue_concept"], "us-gaap:Revenues")

    def test_09_f9_g1_impact_profit(self):
        """Test 9: F9 G1 gate impact is profit due to positive operating income."""
        g1_impact = self.results["f9_g1_impact"]
        self.assertEqual(g1_impact["operating_result_reviewed"], "profit")
        self.assertIn("흑자", g1_impact["rationale"])

    def test_10_sec_host_compliance(self):
        """Test 10: Strict SEC official host compliance with zero disallowed hosts."""
        compliance = self.results["data_source_host_compliance"]
        allowed = ["data.sec.gov", "www.sec.gov"]
        self.assertEqual(compliance["disallowed_hosts_used"], [])
        for h in compliance["all_hosts_used"]:
            self.assertIn(h, allowed)


if __name__ == "__main__":
    unittest.main()
