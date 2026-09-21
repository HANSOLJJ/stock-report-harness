# 상장 12개사 SEC 원자료 기반 현금(cash) 및 FCF_TTM 실측 복원 정합성을 검증하는 독립 테스트 스위트
import json
import os
import unittest

class TestCashFcfVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.results_path = os.path.join(cls.base_dir, "cash_fcf_35_results.json")
        
        with open(cls.results_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)
            
        cls.items_by_ticker = {it["ticker"]: it for it in cls.data["items"]}

    def test_01_all_12_companies_surveyed(self):
        """12개 상장 기업 전수 조사 및 미공시 0건 검증."""
        expected_tickers = ["AAPL", "MSFT", "AMZN", "NVDA", "TSLA", "PLTR", "META", "ORCL", "GOOGL", "SPCX", "TSM", "BABA"]
        self.assertEqual(self.data["summary_metrics"]["total_companies"], 12)
        self.assertEqual(len(self.data["items"]), 12)
        for t in expected_tickers:
            self.assertIn(t, self.items_by_ticker, f"Ticker {t} 누락")
        self.assertEqual(self.data["summary_metrics"]["not_disclosed_count"], 0)
        self.assertEqual(self.data["summary_metrics"]["verified_sec_raw_count"], 12)

    def test_02_cash_integrity_and_positive(self):
        """순수 현금 및 유동성 버퍼 자산의 양수성 및 정합성 검증."""
        for t, it in self.items_by_ticker.items():
            cash_info = it["cash"]
            if t in ["TSM", "BABA"]:
                cash_pure = cash_info["cash_and_cash_equivalents_usd"]
            else:
                cash_pure = cash_info["cash_and_cash_equivalents"]
            self.assertGreater(cash_pure, 0, f"{t} 순수 현금이 0 이하")
            
            # 유동성 버퍼 >= 순수 현금
            if "liquid_cash_buffer" in cash_info:
                self.assertGreaterEqual(cash_info["liquid_cash_buffer"], cash_info["cash_and_cash_equivalents"])
            elif "liquid_cash_buffer_usd" in cash_info:
                self.assertGreaterEqual(cash_info["liquid_cash_buffer_usd"], cash_info["cash_and_cash_equivalents_usd"])

    def test_03_reconstructed_7_companies_ocf_and_capex_math(self):
        """7개 미국 분기 공시 기업의 TTM OCF 및 CapEx 복원 산식 검증."""
        recon_tickers = ["AAPL", "AMZN", "NVDA", "TSLA", "PLTR", "META", "GOOGL"]
        for t in recon_tickers:
            it = self.items_by_ticker[t]
            cf = it["cash_flows"]
            
            # OCF 검증
            if "ocf_components" in cf and "curr_ytd_9m" in cf["ocf_components"]:
                c = cf["ocf_components"]
                derived_tail = c["prior_fy_12m"] - c["prior_ytd_9m"]
                self.assertEqual(c["tail_derived_3m"], derived_tail)
                expected_ocf = c["curr_ytd_9m"] + derived_tail
                self.assertEqual(cf["ocf_ttm"], expected_ocf)
            elif "ocf_components" in cf and "curr_ytd_6m" in cf["ocf_components"]:
                c = cf["ocf_components"]
                derived_tail = c["prior_fy_12m"] - c["prior_ytd_6m"]
                self.assertEqual(c["tail_derived_6m"], derived_tail)
                expected_ocf = c["curr_ytd_6m"] + derived_tail
                self.assertEqual(cf["ocf_ttm"], expected_ocf)
                
            # CapEx 검증
            if "capex_components" in cf and "curr_ytd_9m" in cf["capex_components"]:
                c = cf["capex_components"]
                derived_tail = c["prior_fy_12m"] - c["prior_ytd_9m"]
                self.assertEqual(c["tail_derived_3m"], derived_tail)
                expected_capex = c["curr_ytd_9m"] + derived_tail
                self.assertEqual(cf["capex_ttm"], expected_capex)
            elif "capex_components" in cf and "curr_ytd_6m" in cf["capex_components"]:
                c = cf["capex_components"]
                derived_tail = c["prior_fy_12m"] - c["prior_ytd_6m"]
                self.assertEqual(c["tail_derived_6m"], derived_tail)
                expected_capex = c["curr_ytd_6m"] + derived_tail
                self.assertEqual(cf["capex_ttm"], expected_capex)

    def test_04_direct_fy_and_annual_filers(self):
        """MSFT, ORCL(10-K 직전연간) 및 TSM, BABA(20-F 연간) 직접 공시치 검증."""
        # MSFT
        msft = self.items_by_ticker["MSFT"]
        self.assertEqual(msft["cash_flows"]["ocf_ttm"], 182935000000)
        self.assertEqual(msft["cash_flows"]["capex_ttm"], 115948000000)
        self.assertEqual(msft["cash_flows"]["fcf_ttm"], 66987000000)
        
        # ORCL
        orcl = self.items_by_ticker["ORCL"]
        self.assertEqual(orcl["cash_flows"]["ocf_ttm"], 31977000000)
        self.assertEqual(orcl["cash_flows"]["capex_ttm"], 55663000000)
        self.assertEqual(orcl["cash_flows"]["fcf_ttm"], -23686000000)
        
        # TSM
        tsm = self.items_by_ticker["TSM"]
        self.assertEqual(tsm["cash_flows"]["ocf_ttm_native"], 2274975600000)
        self.assertEqual(tsm["cash_flows"]["capex_ttm_native"], 1272410500000)
        self.assertEqual(tsm["cash_flows"]["fcf_ttm_native"], 1002565100000)
        self.assertEqual(tsm["cash_flows"]["fcf_ttm_usd"], 31959300000)
        
        # BABA
        baba = self.items_by_ticker["BABA"]
        self.assertEqual(baba["cash_flows"]["ocf_ttm_native"], 76213000000)
        self.assertEqual(baba["cash_flows"]["capex_ttm_native"], 126063000000)
        self.assertEqual(baba["cash_flows"]["fcf_ttm_native"], -49850000000)
        self.assertEqual(baba["cash_flows"]["fcf_ttm_usd"], -7226000000)

    def test_05_spcx_h1_and_s1a_reconstruction(self):
        """SPCX의 Form 10-Q(상반기) 및 Form S-1/A(FY2025) 결합 TTM 복원 검증."""
        spcx = self.items_by_ticker["SPCX"]
        cf = spcx["cash_flows"]
        
        # OCF TTM = 3,466 + (6,785 - 351) = 9,900
        c_ocf = cf["ocf_components"]
        self.assertEqual(c_ocf["tail_derived_6m"], 6785000000 - 351000000)
        self.assertEqual(cf["ocf_ttm"], 3466000000 + c_ocf["tail_derived_6m"])
        self.assertEqual(cf["ocf_ttm"], 9900000000)
        
        # CapEx TTM = 28,476 + (20,737 - 6,965) = 42,248
        c_capex = cf["capex_components"]
        self.assertEqual(c_capex["tail_derived_6m"], 20737000000 - 6965000000)
        self.assertEqual(cf["capex_ttm"], 28476000000 + c_capex["tail_derived_6m"])
        self.assertEqual(cf["capex_ttm"], 42248000000)
        
        # FCF TTM = 9,900 - 42,248 = -32,348
        self.assertEqual(cf["fcf_ttm"], -32348000000)

    def test_06_fcf_definition_holds_all_12(self):
        """12개사 전체에서 표준 FCF 공식 (OCF - CapEx) 완전 성립 검증."""
        for t, it in self.items_by_ticker.items():
            cf = it["cash_flows"]
            if t in ["TSM", "BABA"]:
                expected_fcf_native = cf["ocf_ttm_native"] - cf["capex_ttm_native"]
                self.assertEqual(cf["fcf_ttm_native"], expected_fcf_native)
                expected_fcf_usd = cf["ocf_ttm_usd"] - cf["capex_ttm_usd"]
                self.assertEqual(cf["fcf_ttm_usd"], expected_fcf_usd)
            else:
                expected_fcf = cf["ocf_ttm"] - cf["capex_ttm"]
                self.assertEqual(cf["fcf_ttm"], expected_fcf)

    def test_07_cash_burners_runway_calculation(self):
        """적자 4개사(AMZN, ORCL, SPCX, BABA)의 런웨이 공식 및 수치 검증."""
        burners = ["AMZN", "ORCL", "SPCX", "BABA"]
        self.assertEqual(self.data["summary_metrics"]["negative_fcf_count"], 4)
        for t in burners:
            it = self.items_by_ticker[t]
            self.assertEqual(it["cash_flows"]["fcf_result"], "negative")
            self.assertIn("runway", it)
            rw = it["runway"]
            self.assertIn("runway_years_pure_cash", rw)
            self.assertGreater(rw["runway_years_pure_cash"], 0)

    def test_08_legacy_delta_and_reconciliation(self):
        """레거시 기준값 대조 및 주요 기업 오차 범위 검증."""
        # 1. AAPL FCF 차이 0.1% 미만
        aapl = self.items_by_ticker["AAPL"]
        self.assertLess(abs(aapl["legacy_comparison"]["fcf_diff_pct"]), 0.1)
        
        # 2. MSFT FCF 차이 0.1% 미만
        msft = self.items_by_ticker["MSFT"]
        self.assertLess(abs(msft["legacy_comparison"]["fcf_diff_pct"]), 0.1)
        
        # 3. AMZN FCF 차이 1.0% 미만
        amzn = self.items_by_ticker["AMZN"]
        self.assertLess(abs(amzn["legacy_comparison"]["fcf_diff_pct"]), 1.0)
        
        # 4. ORCL FCF 차이 0.1% 미만
        orcl = self.items_by_ticker["ORCL"]
        self.assertLess(abs(orcl["legacy_comparison"]["fcf_diff_pct"]), 0.1)
        
        # 5. SPCX FCF 차이 1.0% 미만
        spcx = self.items_by_ticker["SPCX"]
        self.assertLess(abs(spcx["legacy_comparison"]["fcf_diff_pct"]), 1.0)

    def test_09_f9_g3_policy_simulation(self):
        """F9 G3 런웨이 정책 임계값(3.0년/1.0년)에 따른 판정 영향 검증."""
        # BABA: 순수 현금 2.64년(<3년) -> 감점 -1단계 / 유동성 버퍼 5.75년(>=3년) -> 감점 0
        baba = self.items_by_ticker["BABA"]
        self.assertLess(baba["runway"]["runway_years_pure_cash"], 3.0)
        self.assertGreaterEqual(baba["runway"]["runway_years_pure_cash"], 1.0)
        self.assertEqual(baba["runway"]["g3_step_impact_pure_cash"], -1)
        self.assertGreaterEqual(baba["runway"]["runway_years_with_liquid_buffer"], 3.0)
        self.assertEqual(baba["runway"]["g3_step_impact_liquid_buffer"], 0)
        
        # SPCX: 순수 현금 2.89년(<3년) -> 감점 -1단계 대상
        spcx = self.items_by_ticker["SPCX"]
        self.assertLess(spcx["runway"]["runway_years_pure_cash"], 3.0)
        self.assertGreaterEqual(spcx["runway"]["runway_years_pure_cash"], 1.0)
        self.assertEqual(spcx["runway"]["g3_step_impact_pure_cash"], -1)

if __name__ == "__main__":
    unittest.main()
