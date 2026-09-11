# TSM FY2025 Form 20-F 원문 우회 실측 및 FY2024 교차 검증 검증기
import unittest
import json
import os
import re
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

RESULTS_JSON = os.path.join(BASE_DIR, "tsm_edgar_29_results.json")
RAW_HTML = os.path.join(BASE_DIR, "_raw", "tsm-20251231.htm")
HTTP_META = os.path.join(BASE_DIR, "_raw", "http_metadata.json")
COMPANYFACTS_TSM = os.path.join(REPO_ROOT, "validation", "f6-avail-15b", "_raw", "CIK0001046179_TSM.json")


class TestTsmEdgarBypass(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            cls.results = json.load(f)

    def test_01_results_json_structure(self):
        """결과 JSON 파일 필수 필드 구조 검증"""
        self.assertEqual(self.results.get("task_id"), "TSM-EDGAR-29")
        self.assertEqual(self.results.get("status"), "completed")
        self.assertIn("company", self.results)
        self.assertIn("edgar_filing", self.results)
        self.assertIn("dual_path_cross_validation_fy2024", self.results)
        self.assertIn("fy2025_extracted_data", self.results)
        self.assertIn("convenience_translation_usd", self.results)
        self.assertIn("observation_proposal", self.results)

    def test_02_raw_filing_and_sha256(self):
        """다운로드된 Form 20-F 원문 HTML 존재 및 해시 무결성 검증"""
        self.assertTrue(os.path.exists(RAW_HTML), f"Raw HTML file not found: {RAW_HTML}")
        file_bytes = os.path.getsize(RAW_HTML)
        self.assertEqual(file_bytes, self.results["edgar_filing"]["raw_file_bytes"])
        
        with open(RAW_HTML, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(h, self.results["edgar_filing"]["raw_file_sha256"])

    def test_03_http_metadata_sec_compliance(self):
        """공식 SEC 호스트(www.sec.gov) 및 HTTP 200 메타데이터 검증"""
        self.assertTrue(os.path.exists(HTTP_META), f"HTTP metadata not found: {HTTP_META}")
        with open(HTTP_META, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertIsInstance(meta, list)
        self.assertEqual(len(meta), 1)
        item = meta[0]
        self.assertEqual(item["status"], 200)
        self.assertTrue(item["url"].startswith("https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/"))
        self.assertEqual(item["accession"], "0001628280-26-025362")

    def test_04_companyfacts_baseline_fy2024(self):
        """companyfacts 원자료에 등재된 TSM FY2024 수치 검증"""
        self.assertTrue(os.path.exists(COMPANYFACTS_TSM), f"Companyfacts file not found: {COMPANYFACTS_TSM}")
        with open(COMPANYFACTS_TSM, "r", encoding="utf-8") as f:
            cf = json.load(f)
        ifrs = cf["facts"]["ifrs-full"]
        
        # Revenue
        rev_units = ifrs["RevenueFromContractsWithCustomers"]["units"]["TWD"]
        rev_2024 = [x for x in rev_units if x.get("fy") == 2024 and x.get("form") == "20-F" and x.get("end") == "2024-12-31"]
        self.assertTrue(len(rev_2024) >= 1)
        self.assertEqual(rev_2024[-1]["val"], 2894307700000)

        # Operating Profit
        op_units = ifrs["ProfitLossFromOperatingActivities"]["units"]["TWD"]
        op_2024 = [x for x in op_units if x.get("fy") == 2024 and x.get("form") == "20-F" and x.get("end") == "2024-12-31"]
        self.assertTrue(len(op_2024) >= 1)
        self.assertEqual(op_2024[-1]["val"], 1322053000000)

    def test_05_fy2024_dual_path_exact_match(self):
        """F6-FX-16 제2조건: FY2024 두 경로 100% 일치(불일치 0건) 검증"""
        dual = self.results["dual_path_cross_validation_fy2024"]
        p1 = dual["path_1_companyfacts"]
        p2 = dual["path_2_form_20f_raw"]
        disc = dual["discrepancy"]

        self.assertEqual(p1["revenue_twd"], 2894307700000)
        self.assertEqual(p2["revenue_scaled_twd"], 2894307700000)
        self.assertEqual(disc["revenue_diff_twd"], 0)

        self.assertEqual(p1["operating_profit_twd"], 1322053000000)
        self.assertEqual(p2["operating_profit_scaled_twd"], 1322053000000)
        self.assertEqual(disc["operating_profit_diff_twd"], 0)

        self.assertAlmostEqual(p1["operating_margin_pct"], p2["operating_margin_pct"], places=4)
        self.assertEqual(disc["match_rate_pct"], 100.0)
        self.assertEqual(dual["evaluation"], "PASS_EXACT_MATCH")

    def test_06_fy2025_extracted_figures(self):
        """FY2025 원문 실측치(매출, 영업손익, 영업이익률) 검증"""
        fy25 = self.results["fy2025_extracted_data"]
        rev = fy25["revenue"]
        op = fy25["operating_profit"]
        margin = fy25["operating_margin"]

        # Revenue: NT$ 3,809,054.3M -> 3,809,054,300,000 TWD
        self.assertEqual(rev["table_val_million_twd"], 3809054.3)
        self.assertEqual(rev["scaled_val_twd"], 3809054300000)

        # Operating Profit: NT$ 1,936,091.7M -> 1,936,091,700,000 TWD
        self.assertEqual(op["table_val_million_twd"], 1936091.7)
        self.assertEqual(op["scaled_val_twd"], 1936091700000)

        # Operating Margin: 1936091.7 / 3809054.3 = 50.82867...% -> 50.83%
        expected_margin = (1936091700000 / 3809054300000) * 100
        self.assertAlmostEqual(margin["margin_exact_pct"], expected_margin, places=5)
        self.assertEqual(margin["margin_rounded_2dp_pct"], 50.83)

    def test_07_raw_html_ixbrl_tags(self):
        """HTML 원문 내 iXBRL 태그 직접 검증"""
        with open(RAW_HTML, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        # FY2025 Revenue tag (context c-1, unit twd)
        pattern_rev = r'<ix:nonFraction[^>]*\bcontextRef="c-1"[^>]*\bname="ifrs-full:RevenueFromContractsWithCustomers"[^>]*>([\d\.,]+)</ix:nonFraction>|<ix:nonFraction[^>]*\bname="ifrs-full:RevenueFromContractsWithCustomers"[^>]*\bcontextRef="c-1"[^>]*>([\d\.,]+)</ix:nonFraction>'
        m_rev = re.search(pattern_rev, content)
        self.assertIsNotNone(m_rev, "FY2025 Revenue iXBRL tag not found")
        val_rev = m_rev.group(1) or m_rev.group(2)
        self.assertEqual(val_rev, "3,809,054.3")

        # FY2025 Operating Profit tag (context c-1, unit twd)
        pattern_op = r'<ix:nonFraction[^>]*\bcontextRef="c-1"[^>]*\bname="ifrs-full:ProfitLossFromOperatingActivities"[^>]*>([\d\.,]+)</ix:nonFraction>|<ix:nonFraction[^>]*\bname="ifrs-full:ProfitLossFromOperatingActivities"[^>]*\bcontextRef="c-1"[^>]*>([\d\.,]+)</ix:nonFraction>'
        m_op = re.search(pattern_op, content)
        self.assertIsNotNone(m_op, "FY2025 Operating Profit iXBRL tag not found")
        val_op = m_op.group(1) or m_op.group(2)
        self.assertEqual(val_op, "1,936,091.7")

    def test_08_convenience_translation_note3(self):
        """편의 환산 USD 수치 및 Note 3 환율(NT$ 31.37) 검증"""
        conv = self.results["convenience_translation_usd"]
        self.assertEqual(conv["exchange_rate_ntd_per_usd"], 31.37)
        self.assertEqual(conv["revenue_table_million_usd"], 121423.5)
        self.assertEqual(conv["operating_profit_table_million_usd"], 61717.9)
        self.assertIn("Note 3", conv["footnote_location"])
        self.assertIn("Federal Reserve", conv["source_authority"])

    def test_09_observation_proposal(self):
        """F6-FX-16 3조건 부합 관측 제안(worker 소관) 검증"""
        prop = self.results["observation_proposal"]
        self.assertEqual(prop["proposal_id"], "obs.tsm.edgar_bypass.fy2025")
        self.assertEqual(prop["target_ticker"], "TSM")
        self.assertEqual(prop["verified_metrics"]["operating_margin_pct"], 50.83)
        self.assertIn("worker", prop["worker_registration_status"])
        self.assertIn("rollback_trigger", prop)

    def test_10_status_distinction_3way(self):
        """공시 없음 서술 규율 3대 구분 검증 (회사 미공시가 아니라 SEC 팩트 미반영)"""
        dist = self.results["status_distinction_3way"]
        self.assertEqual(dist["company_disclosure_status"], "공시 완료 (회사 미공시가 아님)")
        self.assertEqual(dist["researcher_status"], "발견 및 원문 확보 완료 (조사자 미발견이 아님)")
        self.assertIn("companyfacts", dist["cause_of_companyfacts_omission"])

    def test_11_impact_assessment(self):
        """F6 20개월->8개월 격차 해소 및 F9 G1 마진 영향 검증"""
        impact = self.results["impact_assessment"]
        self.assertIn("20개월", impact["f6_impact"]["previous_latency"])
        self.assertIn("8개월", impact["f6_impact"]["updated_latency"])
        self.assertIn("50.83%", impact["f9_impact"]["g1_test"])


if __name__ == "__main__":
    unittest.main()
