# 규칙 v2.0 rejudge 정책 검증: 정기 실행의 승계 판단·옛 검토일 거부, 재확인 기록, 기업 추가 실행의 기존 기업 승계 허용, 정기 실행 리뷰의 승계 예외 거부를 잠근다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, write_json  # noqa: E402
from scorecard.validate import is_regular_run, rejudge_violations, validate_scorecard  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_evidence_three_way import V19Base  # noqa: E402
from tests.test_v20_judge import LOCKIN, MATRIX, PATHS, V20Base  # noqa: E402
from validate_report_contract import ValidationResult  # noqa: E402

PRIOR_AS_OF = "2026-10-01"
QUALITATIVE = ("F1", "F2", "F3", "F4", "F5", "F7", "F8")
REJUDGE_ERROR = "정기 실행은 정성 판단을 모두 다시 매긴다"
NO_EXCEPTION = "정기 실행에는 승계 판단 예외를 적용하지 않는다"


def cont(added: list[str] | None = None) -> dict:
    return {"run_id": "ai-scorecard-2026-10-rescore", "as_of": PRIOR_AS_OF, "rule_hash": "0" * 64,
            "hashes": {k: "0" * 64 for k in ("run", "observations", "judgments", "sources")},
            "results_hash": None, "approval_id": None, "added_companies": list(added or [])}


def j(cid: str, factor: str, status: str = "new", reviewed_at: str = "2026-10-08", **extra) -> dict:
    return {"judgment_id": f"{cid}.{factor}", "company_id": cid, "factor": factor, "status": status,
            "reviewed_at": reviewed_at, **extra}


def ctx(judgments: list[dict], run: dict | None = None, rule: str = "v2.0") -> SimpleNamespace:
    return SimpleNamespace(rules=load_rules(rule), run=run or {}, judgments=judgments)


class RejudgeViolationsTest(unittest.TestCase):
    def test_regular_run_definition(self):
        self.assertTrue(is_regular_run({}))
        self.assertTrue(is_regular_run({"continued_from": cont()}))
        self.assertFalse(is_regular_run({"continued_from": cont(["meta"])}))

    def test_carried_in_regular_run_is_refused(self):
        bad = rejudge_violations(ctx([j("nvidia", "F1", "carried"), j("nvidia", "F4")]))
        self.assertEqual(len(bad), 1)
        self.assertIn("nvidia.F1", bad[0])
        self.assertIn("정기 실행에 승계 판단", bad[0])

    def test_non_qualitative_factors_are_not_checked(self):
        self.assertEqual(rejudge_violations(ctx([j("openai", "F6", "carried"), j("nvidia", "F9", "carried")])), [])

    def test_reviewed_at_must_be_after_prior_as_of(self):
        run = {"continued_from": cont()}
        bad = rejudge_violations(ctx([j("nvidia", "F4", reviewed_at=PRIOR_AS_OF), j("nvidia", "F8", reviewed_at="2026-09-02")], run))
        self.assertEqual([b.split(":")[0] for b in bad], ["nvidia.F4", "nvidia.F8"])
        self.assertIn("이번 실행에서 다시 매기지 않은 판단", bad[0])
        self.assertEqual(rejudge_violations(ctx([j("nvidia", "F4", reviewed_at="2026-10-02")], run)), [])

    def test_reconfirmed_counts_as_rereading(self):
        run = {"continued_from": cont()}
        again = [{"at": "2026-10-08", "by": "판단자", "evidence_ids": ["EV-nvidia-001"]}]
        self.assertEqual(rejudge_violations(ctx([j("nvidia", "F4", reviewed_at="2026-09-02", reconfirmed=again)], run)), [])
        stale = [{"at": "2026-09-20", "by": "판단자", "evidence_ids": ["EV-nvidia-001"]}]
        self.assertEqual(len(rejudge_violations(ctx([j("nvidia", "F4", reviewed_at="2026-09-02", reconfirmed=stale)], run))), 1)

    def test_extend_run_requires_new_only_for_added_companies(self):
        run = {"continued_from": cont(["meta"])}
        judgments = [j("nvidia", "F1", "carried", "2026-09-02"), j("nvidia", "F4", reviewed_at="2026-09-02"),
                     j("meta", "F1", "carried", "2026-09-02"), j("meta", "F4", reviewed_at="2026-09-02"),
                     j("meta", "F5")]
        bad = rejudge_violations(ctx(judgments, run))
        self.assertEqual([b.split(":")[0] for b in bad], ["meta.F1", "meta.F4"])
        self.assertIn("기업 추가 실행의 신규 기업", bad[0])

    def test_rules_without_policy_check_nothing(self):
        self.assertEqual(rejudge_violations(ctx([j("nvidia", "F1", "carried", "2026-09-02")], {"continued_from": cont()}, "v1.9")), [])


def validate(slug: str = SLUG) -> ValidationResult:
    return validate_scorecard(slug, check_html_if_present=False, result=ValidationResult(slug=slug))


def review_text(fail_basis: str) -> str:
    rows = "\n".join(f"| Q{i:02d} | 초점 | {'fail' if i == 2 else 'pass'} | {fail_basis if i == 2 else '확인'} |" for i in range(1, 24))
    return ("---\nstatus: pass\nreview_type: separate-session-4way\nreview_execution: separate_subagent_sessions\n---\n"
            "# 리뷰\n\n## 검토 영역\n\n| 영역 | 범위 | 검토자 | 결과 |\n|---|---|---|---|\n"
            "| 사실·출처 | - | 검토자 | pass |\n| 재무 계산 | - | 검토자 | pass |\n| 규칙 일관성 | - | 검토자 | pass |\n"
            "| 출력·가독성 | - | 검토자 | pass |\n\n## 체크리스트\n\n| ID | 초점 | 결과 | 근거 |\n|---|---|---|---|\n" + rows + "\n")


class SandboxMixin:
    def set_continued_from(self, added: list[str] | None) -> None:
        path = self.box.run_dir / "run.json"
        run = load_json_strict(path)
        if added is None:
            run.pop("continued_from", None)
        else:
            run["continued_from"] = cont(added)
        write_json(path, run)

    def write_review(self, fail_basis: str = "TEN-RC-03 재검토 시점에 다시 본다") -> None:
        engine.write_results(SLUG, engine.compute(engine.load_context(SLUG)))
        paths = run_paths(SLUG)
        paths.draft.write_text("---\nresults_hash: x\n---\n# 초안\n", encoding="utf-8", newline="\n")
        paths.review.write_text(review_text(fail_basis), encoding="utf-8", newline="\n")

    def rejudge_errors(self, result: ValidationResult) -> list[str]:
        return [e for e in result.errors if REJUDGE_ERROR in e]


def rejudge_all(jpath: Path) -> None:
    """시험용: 정성 판단 전부를 이번 실행의 새 판단으로 바꾼다(규칙 v2.0 의 kind 와 입력으로)."""
    payload = load_json_strict(jpath)
    for x in payload["items"]:
        if x["factor"] not in QUALITATIVE:
            continue
        x.update(status="new", reviewed_at="2026-10-08", reviewer="판단자")
        if x["factor"] == "F1":
            x.update(kind="lockin", score=None, inputs=copy.deepcopy(LOCKIN))
        elif x["factor"] == "F2":
            x.update(kind="paths", score=None, inputs=copy.deepcopy(PATHS))
        elif x["factor"] == "F7":
            x.update(kind="matrix", score=None, inputs=copy.deepcopy(MATRIX))
        elif x["factor"] == "F3":
            x["inputs"].update(acceleration_tier="e", acceleration="unknown")
    write_json(jpath, payload)


class ValidateScorecardTest(SandboxMixin, V20Base):
    def ids_of(self, company_id: str) -> set[str]:
        return {x["judgment_id"] for x in load_json_strict(self.jpath)["items"] if x["company_id"] == company_id}

    def rejudge_all(self) -> None:
        rejudge_all(self.jpath)

    def test_regular_run_with_carried_judgments_is_refused(self):
        result = validate()
        errors = self.rejudge_errors(result)
        carried = [x for x in load_json_strict(self.jpath)["items"] if x["factor"] in QUALITATIVE and x["status"] == "carried"]
        self.assertTrue(carried)
        self.assertEqual(len(errors), min(len(carried), 20) + (1 if len(carried) > 20 else 0))
        self.assertNotIn("rejudge policy: all qualitative judgments are new for this run", result.checks)

    def test_all_rejudged_passes(self):
        self.set_continued_from([])
        self.rejudge_all()
        result = validate()
        self.assertEqual(self.rejudge_errors(result), [])
        self.assertIn("rejudge policy: all qualitative judgments are new for this run", result.checks)

    def test_old_reviewed_at_is_refused_and_reconfirmed_passes(self):
        self.set_continued_from([])
        self.rejudge_all()
        payload = load_json_strict(self.jpath)
        target = next(x for x in payload["items"] if (x["company_id"], x["factor"]) == ("nvidia", "F4"))
        target["reviewed_at"] = "2026-09-02"
        write_json(self.jpath, payload)
        errors = self.rejudge_errors(validate())
        self.assertEqual(len(errors), 1)
        self.assertIn(f"{target['judgment_id']}: 이번 실행에서 다시 매기지 않은 판단", errors[0])
        target["reconfirmed"] = [{"at": "2026-10-08", "by": "판단자", "evidence_ids": ["EV-nvidia-001"]}]
        write_json(self.jpath, payload)
        result = validate()
        self.assertEqual(self.rejudge_errors(result), [])
        self.assertIn("rejudge policy: all qualitative judgments are new for this run", result.checks)

    def test_extend_run_allows_carried_for_existing_companies(self):
        self.set_continued_from(["openai"])
        result = validate()
        flagged = {e.split(" — ", 1)[1].split(":")[0] for e in self.rejudge_errors(result)}
        self.assertTrue(flagged)
        self.assertTrue(flagged <= self.ids_of("openai"), flagged - self.ids_of("openai"))

    def test_regular_run_review_fail_has_no_carried_exception(self):
        self.set_continued_from([])
        self.write_review()
        result = validate()
        self.assertTrue(any("체크리스트 Q02 가 fail" in e and NO_EXCEPTION in e for e in result.errors), result.errors)

    def test_extend_run_review_keeps_carried_exception(self):
        self.set_continued_from(["openai"])
        self.write_review()
        result = validate()
        self.assertFalse(any("체크리스트 Q02" in e for e in result.errors), [e for e in result.errors if "Q02" in e])
        self.assertTrue(any("승계 예외로 통과한 체크리스트 fail 1건" in w for w in result.warnings))


class V19UnaffectedTest(SandboxMixin, V19Base):
    """정책이 없는 규칙(v1.9)은 정기 실행이어도 승계 판단과 승계 예외를 그대로 둔다."""

    def test_no_rejudge_check_and_exception_still_applies(self):
        self.write_review()
        result = validate()
        self.assertEqual(self.rejudge_errors(result), [])
        self.assertFalse(any(c.startswith("rejudge policy") for c in result.checks))
        self.assertFalse(any("체크리스트 Q02" in e for e in result.errors))
        self.assertTrue(any("승계 예외로 통과한 체크리스트 fail 1건" in w for w in result.warnings))


if __name__ == "__main__":
    unittest.main()
