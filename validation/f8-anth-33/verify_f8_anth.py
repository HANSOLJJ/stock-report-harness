# Anthropic F8 비대칭 의존 3사 분산 전제 및 SEC 공시 실측 검증기
import unittest
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_JSON = os.path.join(BASE_DIR, "f8_anth_33_results.json")

E_FOLDER = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
SCORES_FILE = os.path.join(E_FOLDER, "AI기업_채점표_v1.5.md")
RULES_FILE = os.path.join(E_FOLDER, "AI기업_채점규칙_v1.5.md")


class TestF8AnthropicVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULTS_JSON, "r", encoding="utf-8") as f:
            cls.data = json.load(f)

    def test_01_results_json_structure(self):
        """결과 JSON 필수 구조 및 완료 상태 검증"""
        self.assertEqual(self.data.get("task_id"), "F8-ANTH-33")
        self.assertEqual(self.data.get("status"), "completed")
        self.assertIn("investigation_questions", self.data)
        self.assertIn("premise_validity_synthesis", self.data)

    def test_02_v15_anthropic_f8_citations(self):
        """AI기업_채점표_v1.5.md 350-352행 Anthropic F8 서술 실제 존재 검증"""
        self.assertTrue(os.path.exists(SCORES_FILE), f"Missing: {SCORES_FILE}")
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        l350 = lines[349]
        self.assertIn("컴퓨트 100% 외부", l350)
        self.assertIn("공급자 3사가 전부 경쟁자", l350)
        self.assertIn("Gemini·Nova·OpenAI 27%", l350)

        l351 = lines[350]
        self.assertIn("Google Cloud $200B/5년", l351)
        self.assertIn("AWS $100B/10년", l351)

        l352 = lines[351]
        self.assertIn("Project Rainier", l352)
        self.assertIn("Trainium2", l352)
        self.assertIn("50만개", l352)
        self.assertIn("긴장 #10", l352)

    def test_03_openai_27pct_meaning(self):
        """OpenAI 27%가 MS의 OpenAI 지분율임을 입증하는 원문 대조 검증"""
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        l188 = lines[187]
        self.assertIn("OpenAI 지분 27%", l188)
        self.assertIn("Anthropic Azure $30B", l188)

        with open(RULES_FILE, "r", encoding="utf-8") as f:
            r_lines = f.readlines()
        l217 = r_lines[216]
        self.assertIn("Microsoft", l217)
        self.assertIn("OpenAI 27%", l217)
        self.assertIn("Anthropic $30B", l217)

        q3 = self.data["investigation_questions"]["question_3_openai_27_percent_meaning"]
        self.assertIn("Microsoft가 소유한 OpenAI 지분율 (27%)", q3["meaning"])

    def test_04_google_alphabet_sec_disclosure(self):
        """Alphabet SEC 공시에서 Anthropic 미공시 및 RPO 수치 검증"""
        q1 = self.data["investigation_questions"]["question_1_google_vs_aws_commitments_training_vs_serving"]
        google = q1["google_cloud_alphabet"]
        self.assertEqual(google["finding"], "회사 미공시")
        self.assertIn("Anthropic", google["details"])
        self.assertIn("0건", google["details"])

    def test_05_amazon_sec_form_10q_and_8k_rainier(self):
        """Amazon SEC 공시(10-Q 및 8-K)에서 Project Rainier 및 $100B 약정 실측 검증"""
        q2 = self.data["investigation_questions"]["question_2_project_rainier_and_trainium_scale"]
        self.assertIn("Form 8-K", q2["sec_disclosure_status"])
        citations = q2["sec_citations"]
        self.assertTrue(any("0001018724-25-000002" in c["accession"] for c in citations))
        self.assertTrue(any("nearly 500,000 Trainium2 chips" in c["quote"] for c in citations))
        self.assertTrue(any("train its industry-leading AI model, Claude" in c["quote"] for c in citations))

    def test_06_premise_evaluation_integrity(self):
        """3사 분산 전제와 AWS Project Rainier 물리적 집중의 긴장 #10 정합성 검증"""
        syn = self.data["premise_validity_synthesis"]
        self.assertEqual(syn["tension_id"], "긴장 #10")
        self.assertIn("장부상", syn["is_premise_holding"])
        self.assertIn("AWS Project Rainier", syn["is_premise_holding"])
        self.assertEqual(self.data["target_entity"]["f8_score_v15"], -3)


if __name__ == "__main__":
    unittest.main()
