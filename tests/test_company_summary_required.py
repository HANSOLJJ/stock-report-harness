# 규칙 v3.0 이상 실행에서 기업 한 줄 요약이 빠진 회사를 계약 검증이 잡는지 잠근다(2026-10-24 사용자 지적)
from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.validate import SUMMARY_EXEMPT_RUNS, missing_summaries, validate_scorecard  # noqa: E402
from tests.test_collect_stage import Sandbox  # noqa: E402
from validate_report_contract import ValidationResult  # noqa: E402

V30FULL = "ai-scorecard-2026-10-v30full"
NEW = "ai-scorecard-2026-10-q3s"
COMPANIES = ["alphabet", "microsoft", "tesla"]


def ctx(rule: str, run_id: str = NEW, summaries: dict | None = None) -> SimpleNamespace:
    return SimpleNamespace(rules=load_rules(rule), run={"run_id": run_id, "companies": COMPANIES},
                           company_summaries={cid: {"text": "요약"} for cid in (summaries or {})})


class MissingSummariesTest(unittest.TestCase):
    def test_all_missing_are_listed_in_run_order(self):
        self.assertEqual(missing_summaries(ctx("v3.1")), COMPANIES)

    def test_only_the_missing_row_is_listed(self):
        self.assertEqual(missing_summaries(ctx("v3.1", summaries={"alphabet": 1, "tesla": 1})), ["microsoft"])

    def test_none_missing(self):
        self.assertEqual(missing_summaries(ctx("v3.0", summaries=dict.fromkeys(COMPANIES))), [])

    def test_older_rules_are_not_checked(self):
        self.assertEqual(missing_summaries(ctx("v2.1")), [])

    def test_confirmed_runs_without_summaries_are_exempt(self):
        for run_id in SUMMARY_EXEMPT_RUNS:
            with self.subTest(run_id=run_id):
                self.assertEqual(missing_summaries(ctx("v3.1", run_id=run_id)), [])


class ContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(init=False)
        self.addCleanup(self.box.close)
        src = ROOT / "output" / V30FULL
        if not src.is_dir():
            self.skipTest(f"{V30FULL} 실행이 없다")
        shutil.copytree(src, engine.run_dir(V30FULL))
        stages.init_run(NEW, from_run=V30FULL, rule_version="v3.1", as_of="2026-10-24", title="요약 검사",
                        update_companies=["microsoft"], update_reason="Microsoft 3분기 실적")

    def summary_errors(self) -> list[str]:
        result = validate_scorecard(NEW, check_html_if_present=False, result=ValidationResult(slug=NEW))
        return [e for e in result.errors if "기업 한 줄 요약이 없다" in e]

    def test_contract_names_missing_companies_until_all_written(self):
        companies = engine.load_context(NEW).run["companies"]
        errors = self.summary_errors()
        self.assertEqual(len(errors), 1)
        self.assertIn(", ".join(companies), errors[0])
        for cid in companies[:-1]:
            stages.set_company_summary(NEW, company_id=cid, text=f"{cid} 는 이번 실행에서 매긴 점수로 요약한다.",
                                       reason="시험", by="시험")
        errors = self.summary_errors()
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith(f"기업 한 줄 요약이 없다 — {companies[-1]}."), errors[0])
        stages.set_company_summary(NEW, company_id=companies[-1], text=f"{companies[-1]} 는 이번 실행에서 매긴 점수로 요약한다.",
                                   reason="시험", by="시험")
        self.assertEqual(self.summary_errors(), [])


if __name__ == "__main__":
    unittest.main()
