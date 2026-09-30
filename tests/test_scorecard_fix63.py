# FIX-63 — FIX-61·62 가 남긴 규칙 자기모순 둘과 낡은 문면 셋을 고친 결과를 고정한다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
SRC = ROOT / "scripts" / "scorecard"
PLAN = ROOT / "plan" / f"{SLUG}.md"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


def decisions() -> dict[str, dict]:
    return {d["id"]: d for d in RULES.payload["decisions"]}


def tensions() -> dict[str, dict]:
    return {t["id"]: t for t in RULES.payload["open_tensions"]}


class Fix63Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.run_json = load("run.json")
        cls.ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(cls.ctx.run["baseline_id"])
        cls.md = render_draft(cls.ctx, cls.results, base, triggers)

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 4, "oracle": 2})

    # ---------------------------------------------------------------- S1 규칙 자기모순
    def test_c06_no_longer_contradicts_the_precedence_block(self):
        """규칙이 스스로 모순됐다 — 한쪽은 `C-20 이 앞선다`, C-06 은 그 반대였다."""
        c06 = decisions()["C-06"]
        prec = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]
        self.assertIn("**C-20 이 앞선다.**", prec["what_is_true_now"])
        self.assertIn("C-20 비상장 경로가 먼저 서고", c06["summary"])
        self.assertNotIn("C-20 비상장 경로보다 앞서", c06["summary"])
        self.assertNotIn("BEP 후퇴→-5", c06["summary"])
        # C-06 의 나머지 미결은 그대로다.
        self.assertEqual(c06["status"], "pending")
        for frag in ("FCF/영업손익 0", "완충 잠식", "G2 안정/악화의 기계 정의 부재"):
            with self.subTest(frag=frag):
                self.assertIn(frag, c06["summary"])

    def test_the_contradiction_reached_the_built_html(self):
        """이 문자열은 render_html.render_method 가 방법 표에 그대로 찍는다 — 고친 값이 실린다."""
        # 2026-09-17 FIX-67: 미결 결정 표를 감사 기록으로 옮겼다. 이 문자열은 이제 그쪽에 실린다.
        from scorecard.render_html import render_audit_md, render_method
        audit = render_audit_md(self.ctx, self.results)
        self.assertIn("C-20 비상장 경로가 먼저 서고", audit)
        self.assertNotIn("C-20 비상장 경로보다 앞서", audit)
        self.assertNotIn("C-20 비상장 경로보다 앞서", render_method(self.ctx, self.results))

    def test_no_place_in_the_rules_still_says_the_old_order(self):
        """전수 조사 — 규칙 전체에서 옛 순서를 현재 사실로 적는 문장이 없어야 한다."""
        def strings(node, path=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    yield from strings(v, f"{path}.{k}")
            elif isinstance(node, list):
                for i, v in enumerate(node):
                    yield from strings(v, f"{path}[{i}]")
            elif isinstance(node, str):
                yield path, node

        # 보존 기록·해소된 긴장의 당시 기술은 예외다 — 지우지 않기로 한 자리이기 때문이다.
        preserved = ("superseded_record", "what_it_said", "superseded_reasons", "open_tensions[16]")
        bad = [(p, s) for p, s in strings(RULES.payload)
               if "C-20 비상장 판정보다 앞선다" in s or "C-20 비상장 경로보다 앞서" in s]
        leaked = [p for p, _ in bad if not any(k in p for k in preserved)]
        self.assertEqual(leaked, [], bad)
        # 해소된 긴장의 당시 기술에는 시제가 붙어 있다.
        self.assertTrue(tensions()["TEN-RA5-02"]["tension"].startswith("[해소 전 기술"))

    def test_c07_route_for_openai_is_current(self):
        """전수 조사에서 더 찾은 자리 — C-07 이 openai 를 아직 BEP 후퇴 경로로 적었다."""
        route = decisions()["C-07"]["implementation_status"]["routes"]["openai"]
        self.assertIn("~~", route)                                   # 옛 문면을 지우지 않았다
        self.assertIn("anthropic 과 같은 경로다", route)
        self.assertIn("F9 는 ok **-2** 다", route)
        # 실제 경로와 맞는지 대조한다.
        oai = self.res["openai"]["factors"]["F9"]
        self.assertEqual([p["gate"] for p in oai["calc"]["path"]], ["G1", "G2", "G3", "G4"])
        self.assertEqual(oai["score"], -2)
        self.assertEqual(decisions()["C-07"]["status"], "pending")   # 판정 자체는 안 건드렸다

    # ---------------------------------------------------------------- S2 틀린 닫음
    def test_the_order_actually_changes_the_result(self):
        """`순서가 관측되지 않는다` 가 틀렸다는 것을 시뮬레이션으로 고정한다."""
        comp = self.ctx.companies["spacex-xai"]
        obs = ObsLookup(self.ctx.observations)

        def with_bep(flag: str):
            js = copy.deepcopy(self.ctx.judgments)
            next(x for x in js if x["judgment_id"] == "spacex-xai.F9.obsreg25")["inputs"]["bep_retreat"] = flag
            r = compute_f9(comp, obs, JudgmentLookup(js), self.ctx.rules, self.ctx.run)
            return r["score"], r["calc"]["path"][0]["band"]

        self.assertEqual(with_bep("no"), (-3, "proposed_v15_boundaries"))
        self.assertEqual(with_bep("yes"), (-4, "BEP 후퇴 → -4"))      # 같은 손실률, 다른 점수
        self.assertEqual(self.res["spacex-xai"]["factors"]["F9"]["score"], -3)   # 실행값은 no 쪽이다

    def test_no_listed_company_carries_bep_retreat(self):
        """그래서 이번 실행 점수 영향이 0 이다 — 상장사 중 bep_retreat: yes 가 없다."""
        flagged = [j["judgment_id"] for j in self.ctx.judgments
                   if j["factor"] == "F9" and (j.get("inputs") or {}).get("bep_retreat") == "yes"]
        self.assertEqual(flagged, ["openai.F9"])
        self.assertFalse(self.ctx.companies["openai"]["listed"])

    def test_the_wrong_closure_is_corrected_not_erased(self):
        note = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]["also_precedes_loss_band"]
        self.assertIn("~~다만 두 경로가 만나도 결과는 같다", note)   # 옛 주장을 취소선으로 남겼다
        self.assertIn("이 닫음은 틀렸다", note)
        self.assertIn("-3 에서 -4 로 내려간다", note)
        self.assertIn("틀린 닫음은 안 적은 것보다 나쁘다", note)
        self.assertIn("점수 영향이 0", note)
        # 초안까지 고친 사실이 흘러간다. 2026-09-17 FIX-67 로 표현이 바뀌었고 사실은 그대로다 —
        # 손실이 얕아도 최저점이 된다는 것이 `순서가 결과를 가른다` 와 같은 말이다.
        line = next(x for x in rc.method_lines(self.ctx, self.results) if "손실이 얕아도" in x)
        self.assertIn("최저점", line)
        self.assertFalse(any("두 경로가 만나도 결과는 같다" in x for x in rc.method_lines(self.ctx, self.results)))
        self.assertIn(line if line.startswith("  ") else f"- {line}", self.md)

    def test_no_new_pending_decision_and_why(self):
        """미결 등재 판단 — 등재하지 않고 TEN-RA6-01 의 범위를 넓혔다."""
        why = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]["why_no_new_pending_decision"]
        self.assertIn("새 미결로 등재하지 않는다", why)
        for frag in ("순서 자체는 미정이 아니다", "진짜 질문은 이미 등록돼 있다", "따로 판정될 위험"):
            with self.subTest(frag=frag):
                self.assertIn(frag, why)
        self.assertEqual(sorted(d["id"] for d in RULES.payload["decisions"])[-1], "C-29")   # C-30 은 없다
        scope = tensions()["TEN-RA6-01"]["also_covers_listed"]
        self.assertIn("상장사 자리까지 이 긴장의 범위다", scope)
        self.assertIn("전망이", scope + tensions()["TEN-RA6-01"]["tension"])
        self.assertEqual(tensions()["TEN-RA6-01"]["status"], "open")

    # ---------------------------------------------------------------- S3 재배열 범위
    def test_c29_now_records_that_it_also_precedes_reviewed_profit(self):
        what = decisions()["C-29"]["scope"]["what_changed"]
        self.assertIn('`reviewed_sign == "profit"`', what)
        self.assertIn("그것보다도 앞", what)
        self.assertIn("이 순서가 맞다", what)
        self.assertIn("바뀐 것이 옳아도 안 적힌 것은 안 적힌 것이다", what)
        # 코드가 실제로 그 순서다.
        code = (SRC / "calc_f9.py").read_text(encoding="utf-8")
        c20 = code.index("_private_undisclosed_operating(company, obs, rules, run)")
        profit = code.index('reviewed_sign == "profit"')
        self.assertLess(c20, profit)

    # ---------------------------------------------------------------- S4 낡은 문면
    def test_plan_decision_table_is_rebuilt_from_the_current_rules(self):
        text = PLAN.read_text(encoding="utf-8")
        table = text.split("## 미결 규칙 결정")[1].split("- 미결 결정이")[0]
        row = next(x for x in table.splitlines() if x.startswith("| C-06 |"))
        self.assertIn("C-20 비상장 경로가 먼저 서고", row)
        self.assertNotIn("BEP 후퇴→-5", row)
        self.assertIn("| F9 | downgrade |", table)                   # C-16 의 실행 선택이 반영됐다
        # blocking 인 미결만 표에 선다 — C-03·C-13 은 빠진다.
        self.assertEqual([x.split(" | ")[0].strip("| ") for x in table.splitlines() if x.startswith("| C-")],
                         ["C-05", "C-06", "C-16"])
        # 재고정과 이력은 유지된다.
        self.assertIn(f"rule_hash: {RULES.hash}", text)
        self.assertIn("by: FIX-63 (9차 재판정 2회 반영 — 규칙 자기모순 둘)", text)
        self.assertIn("by: FIX-64 (최종 반영 — 네 영역 pass · 승인 직전)", text)
        self.assertIn("64fb45557c9d40eb0ca9bfd3ed9e18cc53e6ff064dba43458bca25be2744d926", text)
        self.assertEqual(text.count("pinned_at:"), 6)   # FIX-64 가 마지막으로 재고정했다
        self.assertEqual(self.run_json["rule_hash"], RULES.hash)

    # ---------------------------------------------------------------- S5 템플릿 재생성
    def test_review_template_is_regenerated_with_the_current_hashes(self):
        from scorecard.stages import current_hashes
        review = (ROOT / "reviews" / f"{SLUG}.md").read_text(encoding="utf-8")
        h = current_hashes(SLUG)
        self.assertIn(f"results_hash: {h['results']}", review)
        # 2026-09-17 FIX-67: 초안이 바뀌어 리뷰의 draft_hash 가 낡았다. 갱신은 재검토 뒤에 한다.
        self.assertIn("draft_hash: ", review)
        # 2026-09-17 FIX-64: 최종 판정이 와서 reviewers 네 줄이 다시 갱신됐다.
        self.assertIn("financial-calc: pass (9차 · Claude 독립 세션 · 재판정 3회", review)
        self.assertNotIn("financial-calc: 8차", review)

    def test_q11_is_pass_by_the_reviewer_and_so_is_the_area_now(self):
        """리뷰어가 판정한 것만 옮긴다. 2026-09-17 FIX-64: 영역도 리뷰어가 pass 로 바꿔 왔다."""
        review = (ROOT / "reviews" / f"{SLUG}.md").read_text(encoding="utf-8")
        q11 = next(x for x in review.splitlines() if x.startswith("| Q11 "))
        self.assertIn("| pass |", q11)
        self.assertIn("9차 재무 계산 최종 판정", q11)                   # 출처를 밝힌다
        area = next(x for x in review.splitlines() if x.startswith("| 재무 계산 |"))
        self.assertIn("| pass |", area)
        self.assertIn("재판정 3회 끝에 pass", area)                     # 경과를 적었다
        self.assertIn("status: pass", review)
        self.assertTrue((RUN_DIR / "approval.json").exists())
        # 체크리스트 fail 은 11건이고 전부 긴장 번호를 단다.
        import re
        fails = [x for x in review.splitlines() if re.match(r"^\| Q\d\d \| [^|]+ \| fail \|", x)]
        self.assertEqual(len(fails), 11)
        self.assertTrue(all("TEN-" in x for x in fails))

    def test_only_one_contract_error_remains(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        from validate_report_contract import validate_contract
        r = validate_contract(SLUG, require_html=False, check_html_if_present=False)
        # 2026-09-17 FIX-67: 방법 문장을 다시 써 초안이 바뀌었고 리뷰와 승인이 무효가 됐다(의도된 결과).
        # 2026-09-21 재승인: draft_hash 를 갱신하고 다시 승인해 **오류가 하나도 남지 않았다.**
        self.assertEqual(r.errors, [], r.errors)

    def test_run_records_the_round(self):
        a = next(x for x in self.run_json["assumptions"] if "Q11 이 pass 로 바뀌었다" in x)
        self.assertIn("영역은 여전히 `needs_fix`", a)
        self.assertIn("점수는 한 칸도 닿지 않는다", a)
        self.assertIn("C-07", a)


if __name__ == "__main__":
    unittest.main()
