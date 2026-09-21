# ADD-04A — 실행 모집단 수는 결과에서 읽고 v1.5 기준선 14사는 고정 사실로 보존한다
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
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


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

        self.assertIn("기준선 v1.5 의 14사 순위", draft)
        self.assertIn("기준선 v1.5 1위(14사)", draft)
        self.assertIn("기준선에서 넘어오지 않아 14개사 모두 기준선 점수를 그대로 쓴다", draft)

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
