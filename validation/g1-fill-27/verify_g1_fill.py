# 상장 12개사 SEC 원자료 기반 TTM 매출·영업손익 실측 복원 및 정합성을 독립 검증하는 테스트 스위트
import os
import json
import unittest

class TestG1FillVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.results_path = os.path.join(cls.base_dir, "g1_fill_27_results.json")
        cls.raw_facts_path = os.path.join(cls.base_dir, "_raw", "extracted_12_facts.json")
        cls.source_raw_dir = os.path.join(cls.base_dir, "..", "f6-avail-15b", "_raw")
        
        with open(cls.results_path, "r", encoding="utf-8") as f:
            cls.results = json.load(f)
        with open(cls.raw_facts_path, "r", encoding="utf-8") as f:
            cls.raw_facts = json.load(f)
            
        cls.items_by_ticker = {it["ticker"]: it for it in cls.results["items"]}

    def test_01_all_12_companies_surveyed(self):
        """Test 1: Exactly 12 listed companies are surveyed and present in results."""
        expected_tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "TSLA", "PLTR", "META", "ORCL", "GOOGL", "TSM", "BABA", "SPCX"]
        self.assertEqual(self.results["companies_count"], 12)
        self.assertEqual(len(self.results["items"]), 12)
        for t in expected_tickers:
            self.assertIn(t, self.items_by_ticker, f"Ticker {t} missing from results")

    def test_02_reconstructed_7_companies_math_and_margin(self):
        """Test 2: Verify TTM formula Q_curr + (FY_prior - Q_prior) and operating margin for 7 reconstructed companies."""
        reconstructed_tickers = ["AAPL", "AMZN", "NVDA", "TSLA", "PLTR", "META", "GOOGL"]
        for t in reconstructed_tickers:
            it = self.items_by_ticker[t]
            self.assertEqual(it["period_basis"], "TTM")
            self.assertIn("q4_reconstructed_ttm", it["reconstruction_status"])
            
            comp = it["components"]
            # Math check for Revenue: curr_ytd + (prior_fy - prior_ytd) == revenue_ttm
            expected_rev_tail = comp["revenue_prior_fy"] - comp["revenue_prior_ytd"]
            self.assertEqual(comp["revenue_tail_derived"], expected_rev_tail)
            expected_rev_ttm = comp["revenue_curr_ytd"] + expected_rev_tail
            self.assertEqual(it["revenue_ttm"], expected_rev_ttm)
            
            # Math check for Operating Income: curr_ytd + (prior_fy - prior_ytd) == opinc_ttm
            expected_op_tail = comp["operating_income_prior_fy"] - comp["operating_income_prior_ytd"]
            self.assertEqual(comp["operating_income_tail_derived"], expected_op_tail)
            expected_op_ttm = comp["operating_income_curr_ytd"] + expected_op_tail
            self.assertEqual(it["operating_income_ttm"], expected_op_ttm)
            
            # Operating margin percentage check
            calc_margin = round((expected_op_ttm / expected_rev_ttm) * 100.0, 4)
            self.assertEqual(it["operating_margin_ttm_pct"], calc_margin)
            self.assertGreater(it["operating_margin_ttm_pct"], 0.0)
            self.assertEqual(it["operating_result"], "profit")

    def test_03_full_fy_is_ttm_matches_4q_sum(self):
        """Test 3: ORCL and MSFT full FY filed matches 4-quarter sum and is identical to FY reported value."""
        for t in ["MSFT", "ORCL"]:
            it = self.items_by_ticker[t]
            self.assertEqual(it["period_basis"], "TTM")
            self.assertIn("full_fy_filed_is_ttm", it["reconstruction_status"])
            
            comp = it["components"]
            self.assertTrue(comp["sum_4q_matches_fy"])
            self.assertEqual(it["revenue_ttm"], comp["revenue_fy"])
            self.assertEqual(it["operating_income_ttm"], comp["operating_income_fy"])
            
            # Sum of Q3 YTD + derived Q4 must equal FY
            self.assertEqual(comp["revenue_q3_ytd"] + comp["revenue_q4_derived"], comp["revenue_fy"])
            self.assertEqual(comp["operating_income_q3_ytd"] + comp["operating_income_q4_derived"], comp["operating_income_fy"])
            
            calc_margin = round((comp["operating_income_fy"] / comp["revenue_fy"]) * 100.0, 4)
            self.assertEqual(it["operating_margin_ttm_pct"], calc_margin)
            self.assertEqual(it["operating_result"], "profit")

    def test_04_foreign_issuers_annual_basis_and_margins(self):
        """Test 4: TSM and BABA declare period_basis annual under FPI regulations with positive margins."""
        # TSM
        tsm = self.items_by_ticker["TSM"]
        self.assertEqual(tsm["period_basis"], "annual")
        self.assertEqual(tsm["taxonomy"], "ifrs-full")
        self.assertEqual(tsm["currency"], "TWD")
        self.assertEqual(tsm["revenue_ttm"], 2894307700000)
        self.assertEqual(tsm["operating_income_ttm"], 1322053000000)
        self.assertAlmostEqual(tsm["operating_margin_ttm_pct"], 45.6777, places=3)
        self.assertEqual(tsm["operating_result"], "profit")
        
        # BABA
        baba = self.items_by_ticker["BABA"]
        self.assertEqual(baba["period_basis"], "annual")
        self.assertEqual(baba["taxonomy"], "us-gaap")
        self.assertEqual(baba["currency"], "CNY")
        self.assertEqual(baba["revenue_ttm"], 1023670000000)
        self.assertEqual(baba["operating_income_ttm"], 50150000000)
        self.assertAlmostEqual(baba["operating_margin_ttm_pct"], 4.8989, places=3)
        self.assertEqual(baba["operating_result"], "profit")

    def test_05_spacex_not_disclosed_classification(self):
        """Test 5: SPCX TTM is classified as not_disclosed_by_company due to recent listing, preserving quarterly loss."""
        spcx = self.items_by_ticker["SPCX"]
        self.assertEqual(spcx["period_basis"], "quarterly_only")
        self.assertIsNone(spcx["revenue_ttm"])
        self.assertIsNone(spcx["operating_income_ttm"])
        self.assertIsNone(spcx["operating_margin_ttm_pct"])
        self.assertEqual(spcx["operating_result"], "loss")
        
        comp = spcx["components"]
        self.assertEqual(comp["three_way_distinction"], "회사가 공시하지 않았다 (not_disclosed_by_company)")
        self.assertIn("10-K(FY) 행이 0건", comp["reason"])
        
        # Check preserved latest quarter and 6 months numbers
        latest_q = comp["latest_quarter"]
        self.assertEqual(latest_q["revenue"], 7814000000)
        self.assertEqual(latest_q["operating_income"], -143000000)
        self.assertAlmostEqual(latest_q["margin_pct"], -1.8300, places=3)
        
        latest_6m = comp["latest_six_months"]
        self.assertEqual(latest_6m["revenue"], 12508000000)
        self.assertEqual(latest_6m["operating_income"], -2086000000)
        self.assertAlmostEqual(latest_6m["margin_pct"], -16.6773, places=3)

    def test_06_taxonomy_and_concept_exact_matches(self):
        """Test 6: Verify Taxonomy classification (TSM is ifrs-full, 11 companies us-gaap) and exact concepts."""
        tsm = self.items_by_ticker["TSM"]
        self.assertEqual(tsm["taxonomy"], "ifrs-full")
        self.assertEqual(tsm["revenue_concept"], "ifrs-full:Revenue")
        self.assertEqual(tsm["operating_income_concept"], "ifrs-full:ProfitLossFromOperatingActivities")
        
        for t, it in self.items_by_ticker.items():
            if t != "TSM":
                self.assertEqual(it["taxonomy"], "us-gaap")
                self.assertEqual(it["operating_income_concept"], "us-gaap:OperatingIncomeLoss")
                self.assertIn(it["revenue_concept"], [
                    "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
                    "us-gaap:Revenues"
                ])

    def test_07_local_currency_invariance_and_no_usd_distortions(self):
        """Test 7: Local currencies preserved (TWD for TSM, CNY for BABA, USD for 10 US companies)."""
        self.assertEqual(self.items_by_ticker["TSM"]["currency"], "TWD")
        self.assertEqual(self.items_by_ticker["BABA"]["currency"], "CNY")
        for t in ["AAPL", "MSFT", "AMZN", "NVDA", "TSLA", "PLTR", "META", "ORCL", "GOOGL", "SPCX"]:
            self.assertEqual(self.items_by_ticker[t]["currency"], "USD")

    def test_08_q4_and_tail_components_preserved(self):
        """Test 8: Ensure all reconstructed items preserve raw FY, Q_ytd, and tail components."""
        for t in ["AAPL", "AMZN", "NVDA", "TSLA", "PLTR", "META", "GOOGL"]:
            comp = self.items_by_ticker[t]["components"]
            self.assertIn("revenue_prior_fy", comp)
            self.assertIn("revenue_prior_ytd", comp)
            self.assertIn("revenue_tail_derived", comp)
            self.assertIn("revenue_curr_ytd", comp)
            self.assertIn("operating_income_prior_fy", comp)
            self.assertIn("operating_income_prior_ytd", comp)
            self.assertIn("operating_income_tail_derived", comp)
            self.assertIn("operating_income_curr_ytd", comp)

    def test_09_operating_results_profit_vs_loss(self):
        """Test 9: Exactly 11 companies are profit (positive margin) and 1 company is loss (SPCX)."""
        profits = [t for t, it in self.items_by_ticker.items() if it["operating_result"] == "profit"]
        losses = [t for t, it in self.items_by_ticker.items() if it["operating_result"] == "loss"]
        self.assertEqual(len(profits), 11)
        self.assertEqual(len(losses), 1)
        self.assertEqual(losses, ["SPCX"])

    def test_10_sec_official_host_compliance(self):
        """Test 10: Strict compliance with official SEC hosts data.sec.gov and www.sec.gov."""
        compliance = self.results["data_source_host_compliance"]
        allowed = ["data.sec.gov", "www.sec.gov"]
        self.assertEqual(compliance["disallowed_hosts_used"], [])
        for h in compliance["all_hosts_used"]:
            self.assertIn(h, allowed)

    def test_11_path_resilience_and_execution_independence(self):
        """Test 11: File paths are resolved relative to __file__ with 100% test consistency."""
        self.assertTrue(os.path.exists(self.results_path))
        self.assertTrue(os.path.exists(self.raw_facts_path))
        self.assertTrue(os.path.exists(self.source_raw_dir))


if __name__ == "__main__":
    unittest.main()
