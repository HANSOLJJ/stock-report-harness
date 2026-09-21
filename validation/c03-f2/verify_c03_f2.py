# C03-F2 F2 사다리·질·혼합 3대 모델 실측 및 이해상충·신설절 검증 테스트
import json
import os
import unittest

class TestC03F2Models(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(__file__)
        cls.json_path = os.path.join(cls.base_dir, "c03_f2_results.json")
        cls.baseline_path = os.path.abspath(
            os.path.join(cls.base_dir, "..", "f9-decide-20", "_raw", "baseline_judgments.json")
        )
        
        with open(cls.json_path, "r", encoding="utf-8") as f:
            cls.data = json.load(f)
            
        with open(cls.baseline_path, "r", encoding="utf-8") as f:
            cls.baseline = json.load(f)

    def test_01_file_and_schema_structure(self):
        """결과 JSON 파일의 필수 메타데이터 및 스키마 구조 검증"""
        self.assertEqual(self.data.get("schema"), "scorecard_c03_f2_results_v3")
        self.assertEqual(self.data.get("task_id"), "C03-F2-38")
        self.assertEqual(self.data.get("factor"), "F2")
        self.assertIn("sources", self.data)
        self.assertIn("asterisk_f_evidence", self.data)
        self.assertIn("agent_practice_axis_evidence", self.data)
        self.assertIn("conflict_of_interest_and_tensions", self.data)
        self.assertIn("nvidia_market_share_analysis", self.data)
        self.assertIn("models", self.data)
        self.assertIn("companies", self.data)
        self.assertIn("summary", self.data)

    def test_02_total_14_companies_census(self):
        """14개사 전수 조사 여부 및 중복 없는 고유성 검증"""
        companies = self.data["companies"]
        self.assertEqual(len(companies), 14)
        cids = [c["company_id"] for c in companies]
        self.assertEqual(len(set(cids)), 14)
        
        expected_cids = {
            "alphabet", "amazon", "meta", "microsoft", "tsmc",
            "alibaba", "anthropic", "apple", "nvidia", "palantir",
            "spacex-xai", "tesla", "oracle", "openai"
        }
        self.assertEqual(set(cids), expected_cids)

    def test_03_baseline_inherited_scores_match(self):
        """결과 JSON의 승계 점수가 baseline_judgments.json과 100% 일치하는지 검증"""
        baseline_items = {
            it["company_id"]: it["score"]
            for it in self.baseline.get("items", [])
            if it.get("factor") == "F2"
        }
        self.assertEqual(len(baseline_items), 14)
        
        for c in self.data["companies"]:
            cid = c["company_id"]
            self.assertIn(cid, baseline_items)
            self.assertEqual(
                c["inherited_score"],
                baseline_items[cid],
                f"Inherited score mismatch for {cid}"
            )

    def test_04_model1_ladder_results(self):
        """[모델 1] 사다리 모델: 12개사 일치, 2개사 불일치(NVIDIA, TSMC 각 -2) 검증"""
        summary = self.data["summary"]
        self.assertEqual(summary["model1_matched_count"], 12)
        self.assertEqual(summary["model1_mismatched_count"], 2)

        comp_map = {c["company_id"]: c for c in self.data["companies"]}
        for cid in ["nvidia", "tsmc"]:
            c = comp_map[cid]
            self.assertEqual(c["mapped_score_model1_ladder"], 3)
            self.assertEqual(c["inherited_score"], 5)
            self.assertFalse(c["model1_match"])

    def test_05_model2_and_model3_100_percent_matches(self):
        """[모델 2] 질 모델 및 [모델 3] 혼합 모델: 14개사 전수 일치(14/14) 검증"""
        summary = self.data["summary"]
        self.assertEqual(summary["model2_matched_count"], 14)
        self.assertEqual(summary["model2_mismatched_count"], 0)
        self.assertEqual(summary["model3_matched_count"], 14)
        self.assertEqual(summary["model3_mismatched_count"], 0)

        for c in self.data["companies"]:
            self.assertTrue(c["model2_match"])
            self.assertTrue(c["model3_match"])
            self.assertEqual(c["mapped_score_model2_quality"], c["inherited_score"])
            self.assertEqual(c["mapped_score_model3_hybrid"], c["inherited_score"])

    def test_06_agent_practice_axis_and_conflict_of_interest_quotes(self):
        """에이전트 실무 축, 이해상충 고지, 긴장 #4 및 #11 인용 검증"""
        agent_axis = self.data["agent_practice_axis_evidence"]
        self.assertIn("종합 지능", [a["axis"] for a in agent_axis["three_axes_table"]])
        self.assertIn("🆕 에이전트 실무", [a["axis"] for a in agent_axis["three_axes_table"]])
        self.assertIn("코딩", [a["axis"] for a in agent_axis["three_axes_table"]])
        self.assertIn("독립 측정을 우선한다", agent_axis["vendor_vs_independent_rule"])

        coi = self.data["conflict_of_interest_and_tensions"]
        self.assertIn("이해상충 고지", coi["conflict_of_interest_notice"]["text"])
        self.assertIn("Anthropic ②5를 지켰다", coi["conflict_of_interest_notice"]["text"])
        self.assertIn("긴장 #4", coi["tension_4"]["text_1"])
        self.assertIn("긴장 #11", coi["tension_11"]["text_1"])
        self.assertEqual(coi["next_quarter_timeline"]["target_timeline"], "2026년 11월 (2026-11)")

    def test_07_nvidia_market_share_analysis(self):
        """NVIDIA 점유율 70~75% 분석 검증"""
        nv_analysis = self.data["nvidia_market_share_analysis"]
        self.assertEqual(nv_analysis["text"], "AI 가속기 점유율 70~75%")
        self.assertGreaterEqual(len(nv_analysis["reasons"]), 3)

if __name__ == "__main__":
    unittest.main()
