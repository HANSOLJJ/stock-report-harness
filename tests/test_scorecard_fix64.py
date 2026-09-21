# FIX-64 — 마지막 반영(bep_retreat 도달 범위 문면)과 승인·리포트 생성 결과를 고정한다
from __future__ import annotations

import copy
import csv
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import current_hashes  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
SRC = ROOT / "scripts" / "scorecard"
REVIEW = ROOT / "reviews" / f"{SLUG}.md"
HTML = ROOT / "output" / f"{SLUG}.html"
HISTORY = ROOT / "scorecard" / "history.csv"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Fix64Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.approval = load("approval.json")
        cls.ctx = load_context(SLUG)

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()}, TOTALS)

    # ---------------------------------------------------------------- 마지막 발견
    def test_bep_retreat_blocks_a_profitable_company_too(self):
        """문면이 적자 맥락만 적었는데 실제로는 흑자 회사의 G1 통과도 막는다."""
        obs = ObsLookup(self.ctx.observations)

        def with_bep(flag: str):
            js = copy.deepcopy(self.ctx.judgments)
            next(x for x in js if x["judgment_id"] == "microsoft.F9")["inputs"]["bep_retreat"] = flag
            r = compute_f9(self.ctx.companies["microsoft"], obs, JudgmentLookup(js), self.ctx.rules, self.ctx.run)
            return r["score"], r["calc"]["path"][0]

        score_no, g1_no = with_bep("no")
        score_yes, g1_yes = with_bep("yes")
        self.assertEqual((score_no, g1_no["result"]), (0, "pass"))
        self.assertEqual((score_yes, g1_yes["result"]), (-4, "fail"))
        # 양수 마진인 채로 `fail` 이 기록된다 — 그 자체가 서술이 좁았다는 증거다.
        self.assertGreater(g1_yes["operating_margin_ttm"], 0.46)
        self.assertEqual(g1_yes["band"], "BEP 후퇴 → -4")
        self.assertEqual(self.res["microsoft"]["factors"]["F9"]["score"], 0)   # 실행값은 no 쪽이다

    def test_all_four_places_now_say_the_wider_range(self):
        prec = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]
        note = prec["also_precedes_loss_band"]
        self.assertIn("**G1 통과와 손실률 밴드 둘 다보다 앞선다.**", note)
        self.assertIn("영업흑자 회사도 G1 을 통과하지 못하고", note)
        self.assertIn("+46.78%", note)
        self.assertIn("새로 생긴 결함이 아니다", note)          # 동작은 안 바꿨다

        c06 = {d["id"]: d for d in RULES.payload["decisions"]}["C-06"]
        self.assertIn("G1 통과·손실률 밴드 둘 다보다 앞서", c06["summary"])
        self.assertIn("영업흑자여도 통과하지 못하고 하한을 받는다", c06["summary"])

        # 2026-09-17 FIX-67: 표현이 바뀌었다. 지켜야 할 사실은 **흑자 회사도 걸린다**는 것이다.
        line = next(x for x in rc.method_lines(self.ctx, self.results) if "손실이 얕아도" in x)
        self.assertIn("영업이익이 나고 있어도 최저점이 된다", line)

        scope = {t["id"]: t for t in RULES.payload["open_tensions"]}["TEN-RA6-01"]["also_covers_listed"]
        self.assertIn("흑자 상장사도 이 범위다", scope)
        self.assertIn("적자 경우만 보면 흑자 경우가 판정되지 않고 남는다", scope)

    def test_the_code_comment_says_profit_enters_the_loss_branch(self):
        code = (SRC / "calc_f9.py").read_text(encoding="utf-8")
        self.assertIn("**흑자 회사도 여기로 들어온다**", code)
        # 동작은 그대로다 — 갈림 자체를 손대지 않았다.
        self.assertIn("g1_pass = (not bep_retreat) and (margin is None or margin > 0)", code)

    def test_the_score_payload_is_byte_identical_to_the_previous_commit(self):
        """문면만 고쳤다는 것을 리뷰어와 같은 방식으로 확인한다."""
        import hashlib
        import subprocess
        prev = json.loads(subprocess.run(
            ["git", "-C", str(ROOT), "show", f"f313060:scorecard/runs/{SLUG}/results.json"],
            capture_output=True, check=True).stdout.decode("utf-8"))

        def payload(d):
            return hashlib.sha256(json.dumps({k: d[k] for k in ("companies", "ranking")},
                                             ensure_ascii=False, sort_keys=True).encode()).hexdigest()

        self.assertEqual(payload(prev), payload(self.results))
        self.assertEqual(sorted(k for k in self.results if self.results[k] != prev.get(k)),
                         ["input_hashes", "results_hash"])
        self.assertEqual(self.results["warnings_count"], prev["warnings_count"])

    # ---------------------------------------------------------------- 리뷰 파일
    def test_four_areas_are_pass_with_the_history_written(self):
        review = REVIEW.read_text(encoding="utf-8")
        self.assertIn("status: pass", review)
        areas = [x for x in review.splitlines() if re.match(r"^\| (사실·출처|재무 계산|규칙 일관성|출력·가독성) \|", x)]
        self.assertEqual(len(areas), 4)
        for row in areas:
            with self.subTest(area=row.split(" | ")[0]):
                self.assertIn("| pass |", row)
                self.assertTrue(row.split(" | ")[2].strip(), "검토자 칸이 비었다")
        fin = next(x for x in areas if x.startswith("| 재무 계산 |"))
        self.assertIn("8차 needs_fix → FIX-59·61·63 반영 → 재판정 3회 끝에 pass", fin)
        self.assertIn("f313060", fin)

    def test_the_last_finding_and_the_carried_two_are_written(self):
        review = REVIEW.read_text(encoding="utf-8")
        self.assertIn("고치는 쪽을 고른 이유", review)
        self.assertIn("코드를 손대지 않아 점수가 바뀔 수 없다", review)
        self.assertIn("5ee4b01048acf647", review)                # 점수 페이로드 해시
        # 이월 두 건이 어디에 등록돼 있는지 적혀 있다.
        self.assertIn("**미결 `C-27`**", review)
        self.assertIn("**결정 `C-04`**", review)
        self.assertIn("+3.87%", review)
        self.assertIn("39,769M", review)

    # ---------------------------------------------------------------- 승인·빌드
    def test_approval_matches_the_current_inputs(self):
        self.assertEqual(self.approval["approved_by"], "사용자")
        # 2026-09-17 FIX-67: 방법 문장 재작성으로 초안이 바뀌어 승인이 무효가 됐다(의도된 결과).
        # 2026-09-21 재승인: 점수 쪽 다섯이 9월 17일 승인본과 같다는 것을 확인하고 draft 까지 맞물렸다.
        # 승인 날짜는 재승인마다 바뀌므로 고정하지 않고, **점수가 같다는 사실**을 승인 note 로 잠근다.
        self.assertEqual(self.approval["approved_at"], "2026-09-21")
        self.assertEqual(self.approval["approval_id"], "776a511bf0a9028f")
        self.assertIn("2026-09-17 승인본과 동일", self.approval["note"])
        self.assertIn("초안만 바뀌었다", self.approval["note"])
        self.assertEqual(self.approval["hashes"], current_hashes(SLUG))
        self.assertEqual(self.approval["hashes"]["rules"], RULES.hash)
        self.assertEqual(self.approval["hashes"]["results"], self.results["results_hash"])

    def test_contract_passes_with_no_errors(self):
        from validate_report_contract import validate_contract
        r = validate_contract(SLUG, require_html=False, check_html_if_present=False,
                              require_price_chart=False, check_price_chart_if_present=False)
        # 2026-09-17 FIX-67: 초안이 바뀌어 리뷰가 무효였다. 2026-09-21 재승인으로 닫혔다.
        self.assertEqual(r.errors, [], r.errors)
        # 경고 둘은 남는다 — 승계 예외 건수와 그 검사가 확인하지 않는 조건이다.
        self.assertTrue(any("승계 예외로 통과한 체크리스트 fail 11건" in w for w in r.warnings))
        self.assertTrue(any("리뷰어가 판정한다(AGENTS.md 71행)" in w for w in r.warnings))

    def test_html_carries_the_corrected_method_text(self):
        html = HTML.read_text(encoding="utf-8")
        # 2026-09-17 FIX-67: 결정 요약은 감사 기록으로, 방법 문장은 다시 쓴 글로 바뀌었다.
        self.assertIn("영업이익이 나고 있어도 최저점이 된다", html)
        self.assertNotIn("C-20 비상장 경로보다 앞서", html)
        self.assertIn(self.results["results_hash"], html)

    def test_history_has_the_approved_rows(self):
        every = [r for r in csv.DictReader(HISTORY.read_text(encoding="utf-8").splitlines())
                 if r["run_id"] == SLUG]
        # 2026-09-21 재승인: 초안 변경으로 무효였던 승인이 풀리면서 14행이 더 붙어 28행이 됐다.
        # 어느 승인 벌이든 14개사이고 총점과 results_hash 가 같다 — 재승인이 점수를 바꾸지 않았다는 뜻이다.
        self.assertEqual(len(every), 28)
        by_approval: dict[str, list] = {}
        for row in every:
            by_approval.setdefault(row["approval_id"], []).append(row)
        for approval_id, batch in by_approval.items():
            with self.subTest(approval=approval_id):
                self.assertEqual(len(batch), 14)
                self.assertEqual({r["company_id"]: int(r["total"]) for r in batch}, TOTALS)
                self.assertEqual({r["results_hash"] for r in batch}, {self.results["results_hash"]})
        self.assertIn(self.approval["approval_id"], by_approval)
        rows = by_approval[self.approval["approval_id"]]
        for r in rows:
            with self.subTest(cid=r["company_id"]):
                self.assertEqual(r["approval_id"], self.approval["approval_id"])
                self.assertEqual(r["rule_hash"], RULES.hash)
                self.assertEqual(r["results_hash"], self.results["results_hash"])
        self.assertEqual({r["company_id"]: int(r["rank"]) for r in rows}["openai"], 13)


if __name__ == "__main__":
    unittest.main()
