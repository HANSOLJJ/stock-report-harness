# FIX-60 — 계획 해시 재고정과 검증기의 승계 판단 예외 구현을 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from report_contract_lib import frontmatter_value, read_markdown  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.validate import _carried_exception  # noqa: E402
from validate_report_contract import validate_contract  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
PLAN = ROOT / "plan" / f"{SLUG}.md"
REVIEW = ROOT / "reviews" / f"{SLUG}.md"
INIT_HASH = "64fb45557c9d40eb0ca9bfd3ed9e18cc53e6ff064dba43458bca25be2744d926"


def tensions() -> dict[str, dict]:
    return {t["id"]: t for t in RULES.payload["open_tensions"]}


class PlanRuleHashTest(unittest.TestCase):
    def test_plan_is_repinned_to_the_current_rules(self):
        fm, _body, _raw, _text = read_markdown(PLAN)
        self.assertEqual(frontmatter_value(fm, "rule_hash"), RULES.hash)
        run = json.loads((ROOT / "scorecard" / "runs" / SLUG / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(run["rule_hash"], RULES.hash)      # 셋이 같은 값을 가리킨다

    def test_the_init_pin_is_kept_not_erased(self):
        """규칙이 바뀐 채로 같은 실행을 이어 왔다는 사실 자체는 지우지 않는다."""
        text = PLAN.read_text(encoding="utf-8")
        self.assertIn("rule_hash_history:", text)
        self.assertIn(INIT_HASH, text)                      # init 값이 남아 있다
        self.assertIn("pinned_at: 2026-09-11", text)
        self.assertIn("pinned_at: 2026-09-17", text)
        self.assertIn("규칙이 바뀐 채로 같은 실행을 이어 왔다는 사실 자체는 지우지 않는다", text)
        self.assertIn("34번 바뀌었다", text)
        # 지켜지지 않은 원래 문장도 인용으로 남는다.
        self.assertIn("이 줄의 원래 문장은 지켜지지 않았다", text)

    def test_score_touching_changes_are_summarised(self):
        text = PLAN.read_text(encoding="utf-8")
        for frag in ("규칙·자료 변경이 점수에 닿은 자리", "IMPL-46", "fc59da5", "bb3c37c", "f78f944", "d33afd8",
                     "nvidia·oracle ⑦ -3 → -2", "anthropic ⑥ -3 → -4", "총점 11 → 9"):
            with self.subTest(frag=frag):
                self.assertIn(frag, text)
        # FIX-54 자리는 규칙이 아니라 자료 변경이었다 — 그 구분을 적었다.
        self.assertIn("**자료** — spacex-xai 확정 미인출 여신", text)
        self.assertIn("6·7·8차 리뷰 라운드(FIX-57·58·59)에서는 점수 변경이 0", text)


class CarriedExceptionTest(unittest.TestCase):
    """선언(AGENTS.md 71행)대로 구현됐는지 — 등록된 긴장 + 재검토 시점일 때만 예외다."""

    def test_registered_tension_with_recheck_passes(self):
        ok, cited, why = _carried_exception("v1.5 승계 논리이고 `TEN-RC-02` 로 등록됐다", tensions())
        self.assertTrue(ok)
        self.assertEqual(cited, ["TEN-RC-02"])
        self.assertEqual(why, "")

    def test_no_tension_number_is_blocked(self):
        ok, cited, why = _carried_exception("승계 판단이라 예외로 본다", tensions())
        self.assertFalse(ok)
        self.assertEqual(cited, [])
        self.assertIn("긴장 번호(TEN-…)가 없음", why)

    def test_unknown_tension_number_is_blocked(self):
        """문자열만 보고 통과시키면 오타가 예외를 만든다."""
        ok, _cited, why = _carried_exception("`TEN-RC-99` 로 등록됐다", tensions())
        self.assertFalse(ok)
        self.assertIn("규칙 open_tensions 에 없는 긴장 번호", why)
        self.assertIn("TEN-RC-99", why)

    def test_tension_without_recheck_at_is_blocked(self):
        fake = {"TEN-RC-02": {"id": "TEN-RC-02", "recheck_at": ""}}
        ok, _cited, why = _carried_exception("`TEN-RC-02`", fake)
        self.assertFalse(ok)
        self.assertIn("recheck_at 이 없음", why)

    def test_duplicates_are_counted_once(self):
        ok, cited, _why = _carried_exception("`TEN-RC-02` … 다시 `TEN-RC-02` … `TEN-RC-03`", tensions())
        self.assertTrue(ok)
        self.assertEqual(cited, ["TEN-RC-02", "TEN-RC-03"])

    def test_every_cited_tension_in_the_review_really_exists(self):
        """리뷰 파일이 인용한 번호가 전부 규칙에 있는지 — 오타를 여기서도 잡는다."""
        body = REVIEW.read_text(encoding="utf-8")
        cited = set()
        for line in body.splitlines():
            m = re.match(r"^\| (Q\d\d) \| .*? \| fail \| (.*) \|$", line)
            if m:
                cited |= set(re.findall(r"TEN-[A-Z0-9-]+", m.group(2)))
        self.assertTrue(cited)
        self.assertEqual(cited - set(tensions()), set())
        for tid in cited:
            self.assertTrue((tensions()[tid].get("recheck_at") or "").strip(), tid)


class ContractTest(unittest.TestCase):
    def test_remaining_errors_are_the_two_we_expect(self):
        r = validate_contract(SLUG, require_html=False, check_html_if_present=False)
        # 2026-09-17 FIX-61: 반영이 더 있으면 리뷰 파일의 results_hash·draft_hash 가 낡는다 — 템플릿을 다시
        # 만들 때까지는 그 둘이 더 뜬다. **뿌리는 아래 둘**이고 그것만 남는지를 본다.
        # 2026-09-17 FIX-64: 네 영역이 pass 로 오면서 이 테스트가 세운 뿌리 셋
        # (plan 해시 · 승계 예외 미구현 · 영역 결과)이 전부 닫혔다.
        # 2026-09-17 FIX-67: 방법 문장을 다시 써 초안이 바뀌었고 **리뷰와 승인이 무효가 됐다**(의도된 결과).
        # 2026-09-21 재승인: 리뷰의 draft_hash 를 갱신하고 다시 승인해 그 둘도 닫혔다.
        # 이제 **오류가 하나도 없다** — 뿌리 셋과 마지막 둘이 전부 닫힌 상태다.
        self.assertEqual(r.errors, [], r.errors)

    def test_carried_exceptions_are_counted_in_a_warning(self):
        """조용히 넘어가지 않는다 — 몇 건을 어느 긴장으로 통과시켰는지 남긴다.

        2026-09-17 FIX-63: 이 검사는 `status: pass` 일 때만 돈다. 리뷰 파일이 `needs_fix` 인 동안에는
        경고가 서지 않으므로, 여기서는 **파일이 예외를 세울 준비가 돼 있는지**를 대신 본다.
        """
        r = validate_contract(SLUG, require_html=False, check_html_if_present=False)
        # 2026-09-17 FIX-64: status 가 pass 로 돌아와 경고가 다시 선다. Q11 이 pass 라 12 → 11 건이다.
        warn = next(w for w in r.warnings if "승계 예외로 통과한 체크리스트 fail" in w)
        self.assertIn("11건", warn)
        for qid in ("Q01", "Q02", "Q03", "Q05", "Q08", "Q09", "Q12", "Q13", "Q16", "Q20", "Q21"):
            self.assertIn(qid, warn)
        self.assertNotIn("Q11", warn)                        # 리뷰어가 pass 로 재판정했다
        review = REVIEW.read_text(encoding="utf-8")
        for row in [x for x in review.splitlines() if re.match(r"^\| Q\d\d \| [^|]+ \| fail \|", x)]:
            with self.subTest(qid=row.split(" | ")[0]):
                excepted, cited, why = _carried_exception(row, tensions())
                self.assertTrue(excepted, why)
                self.assertTrue(cited)
        # 이 검사가 무엇을 확인하지 **않는지**도 남긴다.
        self.assertTrue(any("리뷰어가 판정한다(AGENTS.md 71행)" in w for w in r.warnings))

    def test_review_area_requirement_untouched(self):
        """검토 영역 pass 요건은 건드리지 않았다 — 재무 계산은 리뷰어가 재판정한다."""
        src = (ROOT / "scripts" / "scorecard" / "validate.py").read_text(encoding="utf-8")
        self.assertIn('elif status == "pass" and res != "pass":', src)
        self.assertIn("리뷰 영역 {label} 결과가 pass 가 아님", src)

    def test_approval_still_absent(self):
        # 2026-09-17 FIX-64: 네 영역 pass 뒤 사용자 승인이 났다. 이 자리가 승인을 막던 사유는 전부 닫혔다.
        approval = json.loads((ROOT / "scorecard" / "runs" / SLUG / "approval.json").read_text(encoding="utf-8"))
        self.assertEqual(approval["approved_by"], "사용자")
        self.assertEqual(approval["hashes"]["rules"], RULES.hash)


if __name__ == "__main__":
    unittest.main()
