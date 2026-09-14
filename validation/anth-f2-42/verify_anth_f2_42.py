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

    def test_02_tension_11_not_triggered(self):
        """긴장 #11 발동 요건(독립 기관의 에이전트 실무 축 측정) 미충족 및 미발동 검증"""
        t11 = self.results['tension_11_trigger_evaluation']
        self.assertFalse(t11['evaluation']['has_independent_measurement_for_anthropic'])
        self.assertFalse(t11['evaluation']['is_tension_11_triggered'])
        self.assertIn('아니오', t11['evaluation']['one_sentence_ruling'])

    def test_03_score_5_defense_and_hybrid_model(self):
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

    def test_04_equal_standard_14_companies(self):
        """14개사 전수 동일 잣대 감사: 점수 변경 기업 없음 검증"""
        audit = self.results['all_14_companies_equal_standard_audit']
        self.assertEqual(len(audit), 14)
        scores = {c['company_id']: c['score'] for c in audit}
        self.assertEqual(scores['nvidia'], 5)
        self.assertEqual(scores['tsmc'], 5)
        self.assertEqual(scores['anthropic'], 5)
        self.assertEqual(scores['openai'], 4)
        self.assertEqual(scores['meta'], 4)
        self.assertEqual(scores['amazon'], 4)
        self.assertEqual(scores['alphabet'], 4)
        self.assertEqual(scores['alibaba'], 4)
        self.assertEqual(scores['spacex-xai'], 4)
        self.assertEqual(scores['microsoft'], 3)
        self.assertEqual(scores['palantir'], 3)
        self.assertEqual(scores['tesla'], 3)
        self.assertEqual(scores['apple'], 2)
        self.assertEqual(scores['oracle'], 2)

    def test_05_source_citations(self):
        """원문 3대 문서의 핵심 인용 문언 검증"""
        with open(self.rules_md, 'r', encoding='utf-8') as f:
            rules_text = f.read()
        self.assertIn("벤더 발표 벤치마크는 1차 근거가 아니다 — 독립 측정을 우선한다", rules_text)
        self.assertIn("이해상충 고지", rules_text)
        self.assertIn("결과적으로 Anthropic ②5를 지켰다", rules_text)
        self.assertIn("제3자 관점으로 재검토", rules_text)

        with open(self.handover_md, 'r', encoding='utf-8') as f:
            handover_text = f.read()
        self.assertIn("독립 기관의 에이전트 실무 축 측정(② 5→4 조건)", handover_text)

        with open(self.table_md, 'r', encoding='utf-8') as f:
            table_text = f.read()
        self.assertIn("Artificial Analysis Index 1위", table_text)
        self.assertIn("MCP 표준 선점", table_text)
        self.assertIn("Opus 5 ARC-AGI-3 30.2%", table_text)

if __name__ == '__main__':
    unittest.main()
