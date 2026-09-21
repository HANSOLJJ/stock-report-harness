# F7 순환금융 별표 I 매트릭스 14개사 전수 및 C-09, C-11 원문 검증 테스트
import unittest
import json
import os
import re

class TestC09C11F7(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        cls.results_path = os.path.join(cls.base_dir, 'validation', 'c09-c11-f7', 'c09_c11_f7_results.json')
        with open(cls.results_path, 'r', encoding='utf-8') as f:
            cls.results = json.load(f)

        cls.rules_md = r'E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점규칙_v1.5.md'
        cls.table_md = r'E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.md'
        cls.table_html = r'E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.html'
        cls.rules_json = os.path.join(cls.base_dir, 'validation', 'f9-decide-20', '_raw', 'rules_v15.json')
        cls.judgments_json = os.path.join(cls.base_dir, 'validation', 'f9-decide-20', '_raw', 'baseline_judgments.json')

    def test_01_matrix_spec_appendix_I(self):
        """별표 I 2x2 매트릭스 구조 및 배점 검증"""
        matrix = self.results['appendix_I_verbatim']['matrix_table']
        self.assertEqual(matrix['small_no']['score'], 0)
        self.assertEqual(matrix['small_yes']['score'], -1)
        self.assertEqual(matrix['large_no']['score'], -2)
        self.assertEqual(matrix['large_yes']['score'], -3)

        with open(self.rules_json, 'r', encoding='utf-8') as f:
            rdata = json.load(f)
        f7 = rdata['factors']['F7']
        self.assertEqual(f7['range'], [-3, 0])
        self.assertEqual(f7['matrix']['small|no'], 0)
        self.assertEqual(f7['matrix']['small|yes'], -1)
        self.assertEqual(f7['matrix']['large|no'], -2)
        self.assertEqual(f7['matrix']['large|yes'], -3)

    def test_02_14_companies_census(self):
        """14개사 전수 매트릭스 적용값 및 승계 점수 일치 여부 검증"""
        census = self.results['census_14_companies']
        self.assertEqual(len(census), 14)

        matching = [c for c in census if c['match'] is True]
        unmatched = [c for c in census if c['match'] is False]

        self.assertEqual(len(matching), 12)
        self.assertEqual(len(unmatched), 2)

        # 0점 6개사
        zeros = [c['company_id'] for c in matching if c['matrix_score'] == 0]
        self.assertEqual(set(zeros), {'meta', 'alibaba', 'apple', 'tsmc', 'palantir', 'spacex-xai'})

        # -1점 4개사 (일치)
        minus_ones = [c['company_id'] for c in matching if c['matrix_score'] == -1]
        self.assertEqual(set(minus_ones), {'alphabet', 'amazon', 'microsoft', 'tesla'})

        # -3점 2개사
        minus_threes = [c['company_id'] for c in matching if c['matrix_score'] == -3]
        self.assertEqual(set(minus_threes), {'nvidia', 'oracle'})

        # 미결 2개사 (Anthropic, OpenAI)
        unmatched_ids = [c['company_id'] for c in unmatched]
        self.assertEqual(set(unmatched_ids), {'anthropic', 'openai'})
        for u in unmatched:
            self.assertIsNone(u['matrix_score'])
            self.assertEqual(u['carried_score'], -1)
            self.assertIn("원문 부재", u['vertical_input'])

    def test_03_c09_unlisted_input_absence(self):
        """C-09: Anthropic·OpenAI의 세로축 입력 부재 및 kind='score' 검증"""
        with open(self.judgments_json, 'r', encoding='utf-8') as f:
            jdata = json.load(f)

        f7_items = {it['company_id']: it for it in jdata['items'] if it.get('factor') == 'F7'}
        self.assertEqual(f7_items['anthropic']['kind'], 'score')
        self.assertEqual(f7_items['anthropic']['inputs'], {})
        self.assertEqual(f7_items['anthropic']['score'], -1)

        self.assertEqual(f7_items['openai']['kind'], 'score')
        self.assertEqual(f7_items['openai']['inputs'], {})
        self.assertEqual(f7_items['openai']['score'], -1)

        with open(self.rules_md, 'r', encoding='utf-8') as f:
            rules_content = f.read()
        self.assertIn("매출은 일반 사용자·기업이 낸 진짜 돈", rules_content)
        self.assertIn("AI 스타트업 고객 일부만 조달 의존", rules_content)

    def test_04_c11_citations_and_conflict(self):
        """C-11: 영업외 비중 F7 이월 서술 출처 및 별표 I 충돌 검증"""
        with open(self.table_md, 'r', encoding='utf-8') as f:
            t_md = f.read()
        self.assertIn("| **영업외 비중** | (세전이익 − 영업이익) ÷ 세전이익. **30% 넘으면 TTM 무효** | ❌ → ⑦ 근거로 이월 |", t_md)

        with open(self.table_html, 'r', encoding='utf-8') as f:
            t_html = f.read()
        self.assertIn("30% 넘으면 TTM 무효·⑦ 근거로 이월", t_html)

        with open(self.rules_md, 'r', encoding='utf-8') as f:
            r_md = f.read()
        self.assertIn("평가이익은 ⑦의 증거가 아니다", r_md)
        self.assertIn("**지분 평가이익**(⑥ 소관)", r_md)
        self.assertIn("평가익은 **손익의 질**(⑥ 소관)이지 순환의 증거가 아니다", r_md)

    def test_05_line_330_perspective(self):
        """채점규칙 330행 설계 관점 원문 검증"""
        with open(self.rules_md, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        line_330 = lines[329]
        self.assertIn("배점 범위를 0~-3으로 좁힌 이유", line_330)
        self.assertIn("세그먼트 공시로 분리 자체가 불가능", line_330)
        self.assertIn("측정 가능성에 비례해 배점 범위를 준다", line_330)

if __name__ == '__main__':
    unittest.main()
