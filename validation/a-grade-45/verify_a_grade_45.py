# 체크리스트 19 피투자 제외 후 별표 G A 기준 재판정 검증 테스트
import unittest
import json
import os

class TestAGrade45(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        json_path = os.path.join(os.path.dirname(__file__), 'a_grade_45_results.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            cls.data = json.load(f)

    def test_json_structure(self):
        self.assertEqual(self.data['task'], 'A-GRADE-45')
        self.assertEqual(self.data['checklist_item'], 19)
        self.assertIn('+2', self.data['criterion_table'])
        self.assertIn('+1', self.data['criterion_table'])
        self.assertIn('0', self.data['criterion_table'])
        self.assertIn('anthropic', self.data['reassessments'])
        self.assertIn('openai', self.data['reassessments'])

    def test_anthropic_reassessment(self):
        anth = self.data['reassessments']['anthropic']
        self.assertEqual(anth['legacy_A'], 2)
        self.assertEqual(anth['legacy_f5'], 5)
        self.assertEqual(len(anth['excluded_items']), 3)
        self.assertEqual(anth['reassessed_A'], 1)
        self.assertEqual(anth['reassessed_H'], 0)
        self.assertEqual(anth['reassessed_f5'], 4)
        self.assertEqual(anth['grade_delta'], -1)
        # 3 questions answered
        analysis = anth['analysis']
        self.assertEqual(analysis['question_1_equity_alliance']['answer'], '불가 (순환 논법)')
        self.assertEqual(analysis['question_2_platform_inclusion']['answer'], '불성립 (벡터 방향 반대)')
        self.assertIn('정당한 양면 평가', analysis['question_3_double_counting_vs_two_sided']['answer'])

    def test_openai_reassessment(self):
        oa = self.data['reassessments']['openai']
        self.assertEqual(oa['legacy_A'], 2)
        self.assertEqual(oa['legacy_f5'], 2)
        self.assertEqual(oa['legacy_H'], -3)
        self.assertEqual(len(oa['excluded_items']), 5)
        self.assertEqual(len(oa['retained_items']), 3)
        self.assertEqual(oa['reassessed_A'], 1)
        self.assertEqual(oa['reassessed_H'], -3)
        self.assertEqual(oa['reassessed_f5'], 1)
        self.assertEqual(oa['grade_delta'], -1)
        analysis = oa['analysis']
        self.assertEqual(analysis['question_1_reassessment_against_appendix_g']['answer'], '+1')
        self.assertEqual(analysis['question_2_comparison_with_ntm']['answer'], '일치 (동일 결론)')

    def test_score_formula_reproduction(self):
        # ⑤ = 3 + A + H
        for comp_key, comp in self.data['reassessments'].items():
            calc_legacy = 3 + comp['legacy_A'] + comp['legacy_H']
            self.assertEqual(calc_legacy, comp['legacy_f5'])
            calc_reassessed = 3 + comp['reassessed_A'] + comp['reassessed_H']
            self.assertEqual(calc_reassessed, comp['reassessed_f5'])

if __name__ == '__main__':
    unittest.main()
