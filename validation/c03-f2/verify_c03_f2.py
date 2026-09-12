# C03-F2 F2 경로 수→점수 매핑 재현 및 14개사 실측 대조 단위 테스트
import json
import os
import unittest

class TestC03F2Mapping(unittest.TestCase):
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
        self.assertEqual(self.data.get("schema"), "scorecard_c03_f2_results_v1")
        self.assertEqual(self.data.get("task_id"), "C03-F2-38")
        self.assertEqual(self.data.get("factor"), "F2")
        self.assertIn("sources", self.data)
        self.assertIn("mapping_ladder", self.data)
        self.assertIn("missing_conditions", self.data)
        self.assertIn("aa_definition", self.data)
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

    def test_03_mapping_ladder_values(self):
        """HANDOVER 22행 기반 매핑 사다리 수치 검증"""
        ladder = self.data["mapping_ladder"]
        self.assertEqual(ladder["0"], 2)
        self.assertEqual(ladder["1"], 3)
        self.assertEqual(ladder["2"], 4)
        self.assertEqual(ladder["aa_top1"], 5)

    def test_04_baseline_inherited_scores_match(self):
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

    def test_05_path_counting_and_mapping_arithmetic(self):
        """각 기업의 경로 수 및 매핑 산식 계산 일관성 검증"""
        for c in self.data["companies"]:
            cnt = c["path_count"]
            aa_top = c["aa_top1_qualified"]
            
            if aa_top:
                expected_mapped = 5
            elif cnt == 0:
                expected_mapped = 2
            elif cnt == 1:
                expected_mapped = 3
            elif cnt >= 2:
                expected_mapped = 4
            else:
                self.fail(f"Invalid path count {cnt} for {c['company_id']}")
                
            self.assertEqual(
                c["mapped_score"],
                expected_mapped,
                f"Mapped score calculation error for {c['company_id']}"
            )
            self.assertEqual(
                c["delta"],
                c["mapped_score"] - c["inherited_score"],
                f"Delta mismatch for {c['company_id']}"
            )
            self.assertEqual(
                c["match"],
                (c["mapped_score"] == c["inherited_score"]),
                f"Match boolean flag error for {c['company_id']}"
            )

    def test_06_mismatches_exactly_nvidia_and_tsmc(self):
        """불일치 기업이 정확히 NVIDIA와 TSMC 2개사이며 각각 3 vs 5(-2)인지 검증"""
        mismatches = self.data["summary"]["mismatched_companies"]
        self.assertEqual(set(mismatches), {"nvidia", "tsmc"})
        self.assertEqual(self.data["summary"]["mismatched_count"], 2)
        self.assertEqual(self.data["summary"]["matched_count"], 12)
        
        comp_map = {c["company_id"]: c for c in self.data["companies"]}
        for target in ["nvidia", "tsmc"]:
            info = comp_map[target]
            self.assertEqual(info["mapped_score"], 3)
            self.assertEqual(info["inherited_score"], 5)
            self.assertEqual(info["delta"], -2)
            self.assertFalse(info["match"])
            self.assertIsNotNone(info["mismatch_reason"])

    def test_07_missing_conditions_defined(self):
        """0점, 1점, 하드웨어 5점 결측 확인 검증"""
        missing = self.data["missing_conditions"]
        self.assertIn("score_0", missing)
        self.assertIn("score_1", missing)
        self.assertIn("hardware_foundry_5", missing)

if __name__ == "__main__":
    unittest.main()
