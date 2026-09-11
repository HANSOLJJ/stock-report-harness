# 비상장 2사 v1.5 원본 F6 입력 지표(arr, arr_prior, 밸류, 누적조달) 추출 검증기
import unittest
import json
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_JSON = os.path.join(BASE_DIR, "priv_arr_30_results.json")

E_FOLDER = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
RULES_FILE = os.path.join(E_FOLDER, "AI기업_채점규칙_v1.5.md")
SCORES_FILE = os.path.join(E_FOLDER, "AI기업_채점표_v1.5.md")


class TestPrivArrExtraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_01_results_json_structure(self):
        """결과 JSON 구조 및 필수 항목 존재 검증"""
        self.assertEqual(self.data.get("task_id"), "PRIV-ARR-30")
        self.assertEqual(self.data.get("status"), "completed")
        self.assertIn("network_call_count", self.data)
        self.assertIn("source_files", self.data)
        self.assertIn("extracted_companies", self.data)
        self.assertIn("key_findings", self.data)
        self.assertIn("c12_recommendation", self.data)

    def test_02_zero_network_calls(self):
        """네트워크 호출 0건 엄격 준수 검증"""
        self.assertEqual(self.data.get("network_call_count"), 0)
        self.assertIn("STRICT_ZERO_CALLS", self.data.get("network_policy", ""))

    def test_03_source_files_sha256(self):
        """v1.5 원본 파일 2개의 실제 디스크 sha256 해시 검증"""
        self.assertTrue(os.path.exists(RULES_FILE), f"Missing: {RULES_FILE}")
        self.assertTrue(os.path.exists(SCORES_FILE), f"Missing: {SCORES_FILE}")

        with open(RULES_FILE, "rb") as f:
            rules_hash = hashlib.sha256(f.read()).hexdigest()
        with open(SCORES_FILE, "rb") as f:
            scores_hash = hashlib.sha256(f.read()).hexdigest()

        # Rules file starts with 57beb84a
        self.assertTrue(rules_hash.startswith("57beb84a"), f"Rules hash mismatch: {rules_hash}")
        self.assertEqual(rules_hash, self.data["source_files"]["rules_file"]["sha256"])

        # Scores file hash
        self.assertEqual(scores_hash, "d28c5416786b5d93798520c060decda855f7a8e53917f623bade7886271aed30")
        self.assertEqual(scores_hash, self.data["source_files"]["scores_file"]["sha256"])

    def test_04_anthropic_metrics(self):
        """Anthropic 4대 지표 수치 정확성 검증"""
        ant = self.data["extracted_companies"]["anthropic"]["metrics"]
        self.assertEqual(ant["arr"]["value_usd"], 65_000_000_000)
        self.assertEqual(ant["arr_prior"]["value_usd"], 47_000_000_000)
        self.assertEqual(ant["post_money_valuation"]["value_usd"], 965_000_000_000)
        self.assertEqual(ant["cumulative_raised"]["value_usd"], 125_000_000_000)

    def test_05_anthropic_period_labels(self):
        """Anthropic 기간 라벨 검증: arr는 7월, arr_prior는 시점 미명시(안 밝혔다)"""
        ant = self.data["extracted_companies"]["anthropic"]["metrics"]
        self.assertIn("7월", ant["arr"]["period_label"])
        self.assertIn("시점 미명시", ant["arr_prior"]["period_label"])
        self.assertEqual(ant["arr_prior"]["period_status"], "unspecified (원문 시점 미명시)")
        self.assertIn("2026/5", ant["post_money_valuation"]["period_label"])
        self.assertIn("2021년~", ant["cumulative_raised"]["period_label"])

    def test_06_openai_metrics(self):
        """OpenAI 4대 지표 수치 정확성 검증"""
        oai = self.data["extracted_companies"]["openai"]["metrics"]
        self.assertEqual(oai["arr"]["value_usd"], 40_000_000_000)
        self.assertEqual(oai["arr_prior"]["value_usd"], 25_000_000_000)
        self.assertEqual(oai["post_money_valuation"]["value_usd"], 852_000_000_000)
        self.assertIn("180", str(oai["cumulative_raised"]["value_usd"]))

    def test_07_openai_period_labels(self):
        """OpenAI 기간 라벨 검증: arr는 7월(또는 8/20), arr_prior는 2~4월 정체"""
        oai = self.data["extracted_companies"]["openai"]["metrics"]
        self.assertIn("7월", oai["arr"]["period_label"])
        self.assertIn("2~4월", oai["arr_prior"]["period_label"])
        self.assertIn("2026/3", oai["post_money_valuation"]["period_label"])

    def test_08_p2_valuation_multiple(self):
        """P2 밸류 배수(valuation / arr) 계산 검증"""
        ant_p2 = self.data["extracted_companies"]["anthropic"]["f6_derived_parameters"]["P2_valuation_multiple"]
        self.assertAlmostEqual(ant_p2["exact"], 965 / 65, places=4)
        self.assertEqual(ant_p2["table_rounded"], 14.8)

        oai_p2 = self.data["extracted_companies"]["openai"]["f6_derived_parameters"]["P2_valuation_multiple"]
        self.assertAlmostEqual(oai_p2["exact"], 852 / 40, places=4)
        self.assertEqual(oai_p2["table_rounded"], 21.3)

    def test_09_p3_growth_rate(self):
        """P3 직전 대비 arr 증가율 계산 검증"""
        ant_p3 = self.data["extracted_companies"]["anthropic"]["f6_derived_parameters"]["P3_growth_rate_pct"]
        expected_ant_growth = ((65 - 47) / 47) * 100
        self.assertAlmostEqual(ant_p3["exact"], expected_ant_growth, places=4)

        oai_p3 = self.data["extracted_companies"]["openai"]["f6_derived_parameters"]["P3_growth_rate_pct"]
        expected_oai_growth = ((40 - 25) / 25) * 100
        self.assertAlmostEqual(oai_p3["exact"], expected_oai_growth, places=4)
        self.assertEqual(expected_oai_growth, 60.0)

    def test_10_p4_capital_efficiency(self):
        """P4 자본효율(arr / cumulative_raised) 계산 검증"""
        ant_p4 = self.data["extracted_companies"]["anthropic"]["f6_derived_parameters"]["P4_capital_efficiency"]
        self.assertAlmostEqual(ant_p4["exact"], 65 / 125, places=4)
        self.assertEqual(ant_p4["display"], "0.52")

        oai_p4 = self.data["extracted_companies"]["openai"]["f6_derived_parameters"]["P4_capital_efficiency"]
        self.assertEqual(oai_p4["table_value"], 0.22)

    def test_11_arr_runrate_nature(self):
        """ARR이 연환산 런레이트이며 TTM 대비 과대하다는 규정 검증"""
        arr_rule = self.data["key_findings"]["arr_vs_runrate"]
        self.assertEqual(arr_rule["status"], "런레이트 확인 완료")
        self.assertIn("런레이트", arr_rule["rule_statement"])

    def test_12_line_citations_live_match(self):
        """원문 파일에 인용된 줄 번호 및 텍스트의 실제 존재 검증"""
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            scores_lines = f.readlines()
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules_lines = f.readlines()

        # Check line 930 in scores: Anthropic $965B Series H
        l930 = scores_lines[929]
        self.assertIn("Anthropic", l930)
        self.assertIn("$965B", l930)
        self.assertIn("$65B", l930)

        # Check line 931 in scores: OpenAI $852B $40B
        l931 = scores_lines[930]
        self.assertIn("OpenAI", l931)
        self.assertIn("$852B", l931)
        self.assertIn("$40B", l931)

        # Check line 666 in rules: Anthropic $125B $65B 0.52
        l666 = rules_lines[665]
        self.assertIn("Anthropic", l666)
        self.assertIn("$125B", l666)
        self.assertIn("0.52", l666)


if __name__ == "__main__":
    unittest.main()
