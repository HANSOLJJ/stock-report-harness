# Anthropic ②게임체인저 5점 제3자 재검토 및 긴장 #11 발동 요건 검증 테스트
import unittest
import json
import os
import re

class TestAnthF242(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        cls.results_path = os.path.join(cls.base_dir, 'validation', 'anth-f2-42', 'anth_f2_42_results.json')
        with open(cls.results_path, 'r', encoding='utf-8') as f:
            cls.results = json.load(f)

        cls.rules_md = r'E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점규칙_v1.5.md'
        cls.table_md = r'E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.md'
        cls.handover_md = r'E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_HANDOVER.md'

    def test_01_three_axes_classification(self):
        """Anthropic 3대 축 지표 분류 및 독립 측정/벤더 발표 구분 검증"""
        axes = self.results['three_axes_census_for_anthropic']
        self.assertIn('1_general_intelligence', axes)
        self.assertIn('2_coding_agent', axes)
        self.assertIn('3_practical_agent_work', axes)

        # 종합 지능 독립 측정 검증
        gen_intel = axes['1_general_intelligence']
        aa_intel = [b for b in gen_intel if 'AA Intelligence Index' in b['benchmark']]
        self.assertTrue(len(aa_intel) >= 1)
        self.assertEqual(aa_intel[0]['source_type'], 'independent')
        self.assertTrue(aa_intel[0]['is_primary_evidence'])

        # 코딩 에이전트 독립 측정 검증
        coding = axes['2_coding_agent']
        aa_coding = [b for b in coding if 'AA Coding Agent Index' in b['benchmark']]
        self.assertEqual(len(aa_coding), 1)
        self.assertEqual(aa_coding[0]['source_type'], 'independent')
        self.assertTrue(aa_coding[0]['is_primary_evidence'])

        # 에이전트 실무 축 독립 측정 부재 검증
        practical = axes['3_practical_agent_work']
        indep_practical = [b for b in practical if b['source_type'] == 'independent']
        self.assertEqual(len(indep_practical), 0)

        # AutomationBench / Agents' Last Exam은 OpenAI 발표치(벤더 발표) 검증
        vendor_practical = [b for b in practical if b['source_type'] == 'vendor_announcement']
        self.assertEqual(len(vendor_practical), 2)
        for vp in vendor_practical:
            self.assertFalse(vp['is_primary_evidence'])
            self.assertIn('OpenAI 발표치', vp['institution'])

    def test_02_meta_three_metrics_comparison(self):
        """에이전트 실무 축에서 Meta 3건 독립 수치 및 Anthropic 결측 대조 검증"""
        cross = self.results['practical_agent_work_cross_comparison']['table']
        self.assertEqual(len(cross), 5)
        
        # Meta 3건 수치 확인
        tau3 = [r for r in cross if 'Tau3-Bench' in r['benchmark']][0]
        self.assertIn('52%', tau3['meta'])
        self.assertIn('원문 부재', tau3['anthropic'])

        gdpval = [r for r in cross if 'GDPval' in r['benchmark']][0]
        self.assertIn('1,754 Elo', gdpval['meta'])
        self.assertIn('원문 부재', gdpval['anthropic'])

        terminal = [r for r in cross if 'Terminal-Bench' in r['benchmark']][0]
        self.assertIn('86%', terminal['meta'])
        self.assertIn('원문 부재', terminal['anthropic'])

        # 원문 채점표 264행과 문면 일치 대조
        with open(self.table_md, 'r', encoding='utf-8') as f:
            t_text = f.read()
        self.assertIn("Tau3-Bench Banking 52%로 전 모델 1위", t_text)
        self.assertIn("GDPval-AA v2 1,754 Elo", t_text)
        self.assertIn("Terminal-Bench 2.1 86%", t_text)

    def test_03_tension_11_dual_readings(self):
        """긴장 #11의 두 가지 읽기(A/B) 및 원문 미규정 판정 검증"""
        dual = self.results['tension_11_dual_reading_analysis']
        self.assertIn('reading_A', dual)
        self.assertIn('reading_B', dual)
        self.assertIn('미발동', dual['reading_A']['ruling'])
        self.assertIn('발동 가능', dual['reading_B']['ruling'])
        
        # 원문이 두 읽기 중 어느 쪽인지 가려주지 않음 검증
        self.assertFalse(dual['adjudication_in_source_text']['does_text_decide'])

    def test_04_secondary_protection_structural_tension(self):
        """독립 측정 우선 규칙의 2차 보호 효과 및 긴장 등록 검증"""
        sec = self.results['secondary_protection_structural_tension']
        self.assertTrue(sec['registered_as_tension'])
        self.assertTrue(len(sec['mechanism_analysis']) >= 4)
        
        # 이해상충 고지 원문 확인
        with open(self.rules_md, 'r', encoding='utf-8') as f:
            r_text = f.read()
        self.assertIn("결과적으로 Anthropic ②5를 지켰다", r_text)

    def test_05_score_5_defense_and_hybrid_model(self):
        """혼합 모델 하에서 Anthropic ②5 성립 검증"""
        defense = self.results['factor_2_score_defense']
        self.assertEqual(defense['path_1_performance_leap']['status'], 'pass')
        self.assertTrue(defense['path_1_performance_leap']['is_generation_leap'])
        self.assertEqual(defense['path_2_standard_preemption']['status'], 'pass')

        hybrid = defense['hybrid_model_evaluation']
        self.assertEqual(hybrid['anthropic_paths_count'], 2)
        self.assertTrue(hybrid['has_generation_leap'])
        self.assertEqual(hybrid['calculated_score'], 5)
        self.assertEqual(hybrid['carried_score'], 5)
        self.assertTrue(hybrid['match'])

    def test_06_equal_standard_14_companies(self):
        """14개사 전수 동일 잣대 감사: 점수 변경 기업 없음 검증"""
        audit = self.results['all_14_companies_equal_standard_audit']
        self.assertEqual(len(audit), 14)
        scores = {c['company_id']: c['score'] for c in audit}
        self.assertEqual(scores['nvidia'], 5)
        self.assertEqual(scores['tsmc'], 5)
        self.assertEqual(scores['anthropic'], 5)
        self.assertEqual(scores['openai'], 4)
        self.assertEqual(scores['meta'], 4)

if __name__ == '__main__':
    unittest.main()
