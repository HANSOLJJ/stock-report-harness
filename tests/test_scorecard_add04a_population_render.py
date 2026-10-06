# ADD-04A·04D — 실행 모집단과 F2 승계 수는 실제 결과·판단에서 읽는다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard import render_html  # noqa: E402
from scorecard import render_md  # noqa: E402
from scorecard.engine import load_context  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / SLUG


class Add04aPopulationRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))

    @staticmethod
    def line(lines: list[str], needle: str) -> str:
        return next(line for line in lines if needle in line)

    def test_incomplete_fifteenth_company_changes_population_wording(self):
        extended = copy.deepcopy(self.results)
        extended["population"]["incomplete"].append({"company_id": "new-company"})

        lines = rc.method_lines(self.ctx, extended)
        self.assertIn("이번 15개사 중 한 곳이 그 경우다", self.line(lines, "분기끼리 견준다"))
        self.assertIn("이번 15개사 중 이 조항이 걸린 회사는 없다", self.line(lines, "손실이 얕아도"))
        self.assertIn("이번 실행 15개사 중 14곳이", self.line(lines, "사람 판단에서 나온다"))

    def test_result_details_drive_track_and_bep_counts(self):
        extended = copy.deepcopy(self.results)
        company = copy.deepcopy(next(c for c in extended["companies"] if c["company_id"] == "spacex-xai"))
        company["company_id"] = "new-company"
        company["factors"]["F9"]["calc"]["path"] = [
            {"gate": "G1", "result": "fail", "band": "BEP 후퇴 → -4", "score": -4}
        ]
        extended["companies"].append(company)
        extended["population"]["scored"] = 15

        lines = rc.method_lines(self.ctx, extended)
        self.assertIn("이번 15개사 중 두 곳이 그 경우다", self.line(lines, "분기끼리 견준다"))
        self.assertIn("이번 15개사 중 이 조항이 걸린 회사는 한 곳이다", self.line(lines, "손실이 얕아도"))

    def test_v15_baseline_rank_wording_stays_fourteen(self):
        baseline = {"companies": [{"company_id": "alphabet", "rank_raw": 1, "evidence": {}}]}
        draft = render_md.render_draft(self.ctx, self.results, baseline, [])

        # 2026-10-06 사용자 지시: 기준선 순위 비교 안내와 기업 카드의 기준선 순위를 싣지 않는다.
        self.assertNotIn("기준선 v1.5 의 14사 순위", draft)
        self.assertNotIn("기준선 v1.5 1위(14사)", draft)
        self.assertIn("② 판단 14개사 모두 어느 경로를 통과했는지 판정 입력이 기록돼 있지 않아 사람이 매긴 점수를 그대로 쓴다", draft)

    def test_f2_all_carried_count_is_dynamic(self):
        ctx = copy.deepcopy(self.ctx)
        judgment = copy.deepcopy(next(j for j in ctx.judgments if j["factor"] == "F2"))
        judgment.update({"judgment_id": "new-company.F2", "company_id": "new-company"})
        ctx.judgments.append(judgment)

        line = self.line(rc.method_lines(ctx, self.results), "규칙 방식으로 계산하지 않았다")
        self.assertIn("② 판단 15개사 모두", line)

    def test_f2_mixed_judgments_report_both_execution_paths(self):
        ctx = copy.deepcopy(self.ctx)
        judgment = copy.deepcopy(next(j for j in ctx.judgments if j["factor"] == "F2"))
        judgment.update({
            "judgment_id": "new-company.F2", "company_id": "new-company", "kind": "paths", "score": None,
            "status": "new",
            "inputs": {
                "performance_leap": "pass", "paradigm_adaptation": "fail", "standard_capture": "pass",
                "top_rank": "no", "generation_gap": "no",
            },
        })
        judgment.pop("carried_from", None)
        ctx.judgments.append(judgment)

        line = self.line(rc.method_lines(ctx, self.results), "두 방식이 함께 쓰였다")
        self.assertIn("② 판단 15개사 중 14곳은", line)
        self.assertIn("나머지 1곳은 경로 판정을 입력으로 규칙 방식에 따라 계산했다", line)
        self.assertNotIn("이번 실행에서는 규칙 방식으로 계산하지 않았다", line)

    def test_f2_without_carried_scores_omits_the_succession_note(self):
        ctx = copy.deepcopy(self.ctx)
        for judgment in ctx.judgments:
            if judgment["factor"] == "F2":
                judgment.update({
                    "kind": "paths", "score": None, "status": "new",
                    "inputs": {
                        "performance_leap": "pass", "paradigm_adaptation": "fail", "standard_capture": "pass",
                        "top_rank": "no", "generation_gap": "no",
                    },
                })
                judgment.pop("carried_from", None)

        line = self.line(rc.method_lines(ctx, self.results), "규칙은 조건을 몇 개 통과했는지")
        self.assertNotIn("기준선 점수", line)
        self.assertNotIn("이번 실행에서는", line)

    def test_html_method_uses_the_same_dynamic_population(self):
        extended = copy.deepcopy(self.results)
        extended["population"]["incomplete"].append({"company_id": "new-company"})

        method = render_html.render_method(self.ctx, extended)
        self.assertIn("이번 15개사 중 한 곳이 그 경우다", method)
        self.assertIn("이번 실행 15개사 중 14곳이", method)
        self.assertIn("1번째 관문", render_html.render_code_index(self.ctx, extended))

    def test_private_company_counts_are_not_fixed_at_two(self):
        ctx = copy.deepcopy(self.ctx)
        ctx.companies["alphabet"]["listed"] = False
        conflict = self.line(rc.conflict_lines(ctx), "이해상충")
        self.assertIn("비상장 3사의 수치", conflict)

        results = copy.deepcopy(self.results)
        next(c for c in results["companies"] if c["company_id"] == "alphabet")["listed"] = False
        draft = render_md.render_draft(self.ctx, results, None, [])
        self.assertIn("비상장 3사의 수치는 이해당사자 1차 발표에서 온다", draft)


if __name__ == "__main__":
    unittest.main()
