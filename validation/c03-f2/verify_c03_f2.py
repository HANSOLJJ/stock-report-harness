# C03-F2 F2 경로 수 사다리 모델 vs 별표 F 세대격차 질 모델 14개사 실측 검증 테스트
import json
import os
import unittest

class TestC03F2MappingModels(unittest.TestCase):
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
        self.assertEqual(self.data.get("schema"), "scorecard_c03_f2_results_v2")
        self.assertEqual(self.data.get("task_id"), "C03-F2-38")
        self.assertEqual(self.data.get("factor"), "F2")
        self.assertIn("sources", self.data)
        self.assertIn("asterisk_f_evidence", self.data)
        self.assertIn("nvidia_market_share_analysis", self.data)
        self.assertIn("mapping_models", self.data)
        self.assertIn("missing_conditions", self.data)
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
        """[모델 1] HANDOVER 사다리 모델: 12개사 일치, 2개사 불일치(NVIDIA, TSMC 각 -2) 검증"""
        m1_summary = self.data["summary"]["model1_summary"]
        self.assertEqual(m1_summary["matched_count"], 12)
        self.assertEqual(m1_summary["mismatched_count"], 2)
        self.assertEqual(set(m1_summary["mismatched_companies"]), {"nvidia", "tsmc"})

        comp_map = {c["company_id"]: c for c in self.data["companies"]}
        for cid in ["nvidia", "tsmc"]:
            c = comp_map[cid]
            self.assertEqual(c["mapped_score_model1_ladder"], 3)
            self.assertEqual(c["inherited_score"], 5)
            self.assertEqual(c["model1_delta"], -2)
            self.assertFalse(c["model1_match"])

    def test_05_model2_quality_results(self):
        """[모델 2] 별표 F 세대격차 질 모델: 14개사 전수 일치(14/14) 검증"""
        m2_summary = self.data["summary"]["model2_summary"]
        self.assertEqual(m2_summary["matched_count"], 14)
        self.assertEqual(m2_summary["mismatched_count"], 0)

        for c in self.data["companies"]:
            self.assertTrue(
                c["model2_match"],
                f"Model 2 mismatch for {c['company_id']}"
            )
            self.assertEqual(
                c["mapped_score_model2_quality"],
                c["inherited_score"],
                f"Model 2 score calculation error for {c['company_id']}"
            )
            self.assertEqual(c["model2_delta"], 0)

    def test_06_asterisk_f_and_nvidia_analysis_present(self):
        """별표 F 예시 인용 및 NVIDIA 점유율 분석 존재 검증"""
        ast_f = self.data["asterisk_f_evidence"]
        self.assertIn("table", ast_f)
        self.assertTrue(any("NVIDIA" in row["v1_examples"] for row in ast_f["table"]))
        self.assertTrue(any("Anthropic" in row["v1_examples"] for row in ast_f["table"]))
        self.assertTrue(any("Meta" in row["v1_examples"] for row in ast_f["table"]))

        nv_analysis = self.data["nvidia_market_share_analysis"]
        self.assertEqual(nv_analysis["text"], "AI 가속기 점유율 70~75%")
        self.assertGreaterEqual(len(nv_analysis["reasons"]), 3)

    def test_07_explanatory_gaps_defined(self):
        """두 모델의 한계 및 설명 불가 영역 정의 검증"""
        gaps = self.data["summary"]["explanatory_gaps"]
        self.assertIn("model1_ladder_gap", gaps)
        self.assertIn("model2_quality_gap", gaps)
        self.assertIn("amazon", gaps["model2_quality_gap"]["ambiguous_companies"])

if __name__ == "__main__":
    unittest.main()
