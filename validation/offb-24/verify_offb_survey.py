# SPCX, BABA, AMZN의 미개시 B종 약정 및 계약수입 SEC 공시 실측 조사 독립 검증 스위트
import unittest
import os
import json
import re


class TestOffBSurvey(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.raw_dir = os.path.join(base_dir, "_raw")
        cls.results_file = os.path.join(base_dir, "offb_survey_results.json")
        cls.excerpts_file = os.path.join(cls.raw_dir, "extracted_excerpts.json")
        
        with open(cls.results_file, "r", encoding="utf-8") as f:
            cls.results = json.load(f)
        with open(cls.excerpts_file, "r", encoding="utf-8") as f:
            cls.excerpts = json.load(f)

    def test_01_spcx_unconditional_obligations_10q(self):
        """Test 1: SPCX 10-Q Note 16 discloses $27,955M unconditional obligations with detailed schedule."""
        fpath = os.path.join(self.raw_dir, "spcx-20260630.htm")
        self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        # Verify Note 16 and exact total
        self.assertIn("Note 16 - Commitments and Contingencies", content)
        self.assertIn("27,955", content)
        self.assertIn("22,244", content)  # 2027 payment
        self.assertIn("2,728", content)   # 2026 remaining
        
        # Check structured result
        spcx_offb = self.results["survey_findings"]["SPCX"]["offbalance_B"]
        self.assertEqual(spcx_offb["components"]["unconditional_noncancelable_purchase_obligations"]["amount_usd"], 27955000000)

    def test_02_spcx_uncommenced_leases_s1a(self):
        """Test 2: SPCX S-1/A Note 11 discloses $1,627M uncommenced operating leases (term 7.2 years)."""
        fpath = os.path.join(self.raw_dir, "spcx_s1a_20260603.htm")
        self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("Leases not yet commenced", content)
        self.assertIn("1,627", content)
        self.assertIn("7.2", content)
        
        spcx_offb = self.results["survey_findings"]["SPCX"]["offbalance_B"]
        self.assertEqual(spcx_offb["components"]["uncommenced_operating_leases"]["amount_usd"], 1627000000)
        self.assertEqual(spcx_offb["components"]["uncommenced_operating_leases"]["weighted_average_term_years"], 7.2)

    def test_03_spcx_backlog_rpo_10q(self):
        """Test 3: SPCX 10-Q Note 3 discloses backlog of $47,461M ($47.461B)."""
        fpath = os.path.join(self.raw_dir, "spcx-20260630.htm")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("47,461", content)
        self.assertIn("14,286", content)  # deferred revenue portion
        
        spcx_rev = self.results["survey_findings"]["SPCX"]["contracted_revenue"]
        self.assertEqual(spcx_rev["found_value_usd"], 47461000000)
        self.assertEqual(spcx_rev["deferred_revenue_included_usd"], 14286000000)

    def test_04_baba_uncommenced_leases_absence_20f(self):
        """Test 4: BABA 20-F Note 6 discloses operating leases (RMB 26,837M) but NO uncommenced leases."""
        fpath = os.path.join(self.raw_dir, "baba-20260331.htm")
        self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("26,837", content)  # undiscounted operating lease liability
        self.assertIn("21,726", content)  # discounted PV
        # Verify absence of uncommenced lease disclosure
        self.assertNotIn("leases not yet commenced", content.lower())
        self.assertNotIn("uncommenced lease", content.lower())
        
        baba_offb = self.results["survey_findings"]["BABA"]["offbalance_B"]
        self.assertIn("공시 없음 (중요성 미달 가능)", baba_offb["three_way_classification"])

    def test_05_baba_commitments_disclosed_20f(self):
        """Test 5: BABA 20-F Note 27 discloses capital commitments of RMB 54,136M and other commitments of RMB 200,062M."""
        fpath = os.path.join(self.raw_dir, "baba-20260331.htm")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("54,136", content)
        self.assertIn("200,062", content)
        
        baba_details = self.results["survey_findings"]["BABA"]["offbalance_B"]["disclosed_commitments_detail"]
        self.assertEqual(baba_details["capital_commitments_contracted"]["amount_rmb"], 54136000000)
        self.assertEqual(baba_details["other_commitments_bandwidth_colocation"]["amount_rmb"], 200062000000)

    def test_06_baba_rpo_practical_expedient_20f(self):
        """Test 6: BABA 20-F Note 2(t) explicitly applies ASC 606 practical expedient, not disclosing RPO."""
        fpath = os.path.join(self.raw_dir, "baba-20260331.htm")
        self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("practical expedient", content)
        self.assertIn("unsatisfied performance obligations for contracts with an original expected duration of one year or less", content)
        
        baba_rev = self.results["survey_findings"]["BABA"]["contracted_revenue"]
        self.assertIsNone(baba_rev["found_value"])
        self.assertIn("not_disclosed_by_company", baba_rev["three_way_classification"])

    def test_07_amzn_rpo_numeric_disclosure_10k(self):
        """Test 7: AMZN 10-K Note 1 discloses AWS performance obligations of $244 billion as of 2025-12-31."""
        fpath = os.path.join(self.raw_dir, "amzn-20251231.htm")
        self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("244", content)
        self.assertIn("4.1", content)
        self.assertIn("commitments in customer contracts for future services that we expect to fulfill", content)
        
        amzn_rev = self.results["survey_findings"]["AMZN"]["contracted_revenue"]
        self.assertEqual(amzn_rev["found_value_usd_20251231"], 244000000000)

    def test_08_amzn_rpo_numeric_disclosure_10q(self):
        """Test 8: AMZN 10-Q Note 1 discloses AWS performance obligations of $496 billion as of 2026-06-30."""
        fpath = os.path.join(self.raw_dir, "amzn-20260630.htm")
        self.assertTrue(os.path.exists(fpath), f"File {fpath} must exist")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("496", content)
        self.assertIn("6.4", content)
        self.assertIn("OpenAI", content)
        self.assertIn("Anthropic", content)
        
        amzn_rev = self.results["survey_findings"]["AMZN"]["contracted_revenue"]
        self.assertEqual(amzn_rev["found_value_usd_20260630"], 496000000000)
        self.assertIn("disclosed_but_not_parsed", amzn_rev["three_way_classification"])

    def test_09_amzn_uncommenced_leases_10q(self):
        """Test 9: AMZN 10-Q Note 4 discloses uncommenced leases of $137,214M ($137.214B)."""
        fpath = os.path.join(self.raw_dir, "amzn-20260630.htm")
        with open(fpath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        self.assertIn("137,214", content)
        self.assertIn("Leases not yet commenced", content)
        
        amzn_offb = self.results["survey_findings"]["AMZN"]["offbalance_B_comparison"]
        self.assertEqual(amzn_offb["survey_status_20260630_uncommenced_leases_usd"], 137214000000)

    def test_10_three_way_classification_and_host_compliance(self):
        """Test 10: Strict three-way classification is maintained and only allowed SEC hosts were used."""
        allowed_hosts = ["data.sec.gov", "www.sec.gov"]
        compliance = self.results["data_source_host_compliance"]
        self.assertEqual(compliance["disallowed_hosts_used"], [])
        for host in compliance["all_hosts_used"]:
            self.assertIn(host, allowed_hosts)

        # Classification check across the 3 companies
        spcx_offb_class = self.results["survey_findings"]["SPCX"]["offbalance_B"]["three_way_classification"]
        baba_offb_class = self.results["survey_findings"]["BABA"]["offbalance_B"]["three_way_classification"]
        baba_rev_class = self.results["survey_findings"]["BABA"]["contracted_revenue"]["three_way_classification"]
        amzn_rev_class = self.results["survey_findings"]["AMZN"]["contracted_revenue"]["three_way_classification"]

        self.assertIn("공시했는데 우리가 못 찾았다", spcx_offb_class)
        self.assertIn("공시 없음 (중요성 미달 가능)", baba_offb_class)
        self.assertIn("회사가 공시하지 않았다", baba_rev_class)
        self.assertIn("공시했는데 우리가 못 찾았다", amzn_rev_class)

        # Provisional coverage checks
        spcx_cov = self.results["survey_findings"]["SPCX"]["provisional_coverage"]
        self.assertEqual(spcx_cov["status"], "provisional")
        self.assertEqual(spcx_cov["ratio"], 1.604)

        amzn_cov = self.results["survey_findings"]["AMZN"]["provisional_coverage"]
        self.assertEqual(amzn_cov["status"], "provisional")
        self.assertEqual(amzn_cov["ratio_uncommenced_leases_only"], 3.615)


if __name__ == "__main__":
    unittest.main()
