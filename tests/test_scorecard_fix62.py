# FIX-62 — openai.F9 를 C-20 비상장 경로로 보낸 사용자 결정(C-29)과 그 뒤집힌 기록을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
SRC = ROOT / "scripts" / "scorecard"
V15 = Path("E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor/AI기업_채점규칙_v1.5.md")


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Fix62Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.run_json = load("run.json")
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(cls.ctx.run["baseline_id"])
        cls.md = render_draft(cls.ctx, cls.results, base, triggers)

    # ---------------------------------------------------------------- S2 점수와 순위
    def test_totals(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 4, "oracle": 2})
        # openai 단독 13위 · oracle 단독 14위. 나머지 12개사 순위는 건드리지 않았다.
        self.assertEqual((self.res["openai"]["rank"], self.res["oracle"]["rank"]), (13, 14))
        self.assertEqual([c for c, r in self.res.items() if r["rank"] == 13], ["openai"])
        self.assertEqual([c for c, r in self.res.items() if r["rank"] == 14], ["oracle"])

    # ---------------------------------------------------------------- S1 경로
    def test_c20_detection_stands_before_bep_retreat(self):
        path = self.res["openai"]["factors"]["F9"]["calc"]["path"]
        self.assertEqual([p["gate"] for p in path], ["G1", "G2", "G3", "G4"])
        g1 = path[0]
        self.assertEqual((g1["result"], g1["decision_id"]), ("undetermined", "C-20"))
        self.assertIn("판정 보류(통과 아님)", g1["reason"])
        # BEP 후퇴 기록은 그대로이나 경로를 막지 않는다는 사실을 경로에 남긴다.
        self.assertIn("C-29", g1["bep_retreat_not_applied"])
        self.assertEqual(self.j["openai.F9"]["inputs"]["bep_retreat"], "yes")
        self.assertEqual(self.res["openai"]["factors"]["F9"]["score"], -2)
        self.assertEqual(path[1]["score"], -2)               # G2 비상장 조항이 점수를 낸다

    def test_anthropic_route_is_untouched(self):
        """anthropic 은 `bep_retreat: no` 라 전에도 C-20 경로였다 — 이 결정으로 바뀌는 것이 없다."""
        ant = self.res["anthropic"]["factors"]["F9"]
        self.assertEqual(ant["score"], -2)
        self.assertEqual(self.res["anthropic"]["total"], 10)
        g1 = ant["calc"]["path"][0]
        self.assertEqual((g1["result"], g1["decision_id"]), ("undetermined", "C-20"))
        self.assertNotIn("bep_retreat_not_applied", g1)      # 후퇴 기록이 없으니 그 줄도 없다
        self.assertEqual(self.j["anthropic.F9"]["inputs"]["bep_retreat"], "no")

    def test_bep_retreat_still_scores_where_c20_does_not_reach(self):
        """상장사이거나 구조적 미공시가 아니면 BEP 후퇴 점수가 그대로 선다 — 뒤집기는 순서만 바꿨다."""
        code = (SRC / "calc_f9.py").read_text(encoding="utf-8")
        self.assertIn("_private_undisclosed_operating(company, obs, rules, run)", code)
        self.assertNotIn("if margin is None and not bep_retreat:", code)
        f9 = RULES.payload["policies"]["f9"]
        self.assertEqual(f9["g1_bep_retreat_score"], f9["floor"])   # 점수값 자체는 손대지 않았다

    # ---------------------------------------------------------------- S1 기록
    def test_c29_records_both_choices_and_who_decided(self):
        c29 = {d["id"]: d for d in RULES.payload["decisions"]}["C-29"]
        self.assertEqual((c29["decided_by"], c29["decided_at"]), ("사용자", "2026-09-17"))
        self.assertEqual(c29["chosen"], "c20_private_route_first")
        self.assertEqual(sorted(c29["choices"]), ["bep_retreat_first", "c20_private_route_first"])
        self.assertEqual(c29["superseded_choice"], "bep_retreat_first")
        # 버린 쪽의 근거를 지우지 않았다 — v1.5 470·494·603행이 그대로 인용돼 있다.
        sup = c29["confirmed_model"]["superseded_reasons"]
        for frag in ("470행", "494·603행", "FIX-59"):
            with self.subTest(frag=frag):
                self.assertIn(frag, sup["what_was_argued"])
        self.assertIn("별표 D 와 충돌한다", sup["why_not_chosen"])
        self.assertIn("TEN-RA6-01", sup["why_not_chosen"])
        self.assertIn("openai F9 -4 → -2, 총점 2 → 4", c29["confirmed_model"]["score_impact"])

    def test_the_old_precedence_is_superseded_not_deleted(self):
        prec = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]
        self.assertEqual(prec["status"], "superseded")
        self.assertEqual(prec["superseded_at"], "2026-09-17")
        self.assertIn("C-29", prec["superseded_by"])
        # 언제·무엇을 근거로·누가 정했는지가 남아 있다.
        old = prec["superseded_record"]
        self.assertIn("**`bep_retreat: yes` 가 C-20 비상장 판정보다 앞선다.**", old["rule"])
        self.assertEqual(old["decided_by"], "사용자 (2026-09-17)")
        self.assertEqual(len(old["source_lines"]), 3)
        self.assertIn("~~", prec["what_it_said"])            # 옛 문면을 취소선으로 남겼다
        self.assertIn("**C-20 이 앞선다.**", prec["what_is_true_now"])
        self.assertIn("세 번째로 같은 길을 돌지 않는다", prec["kept_why"])
        # 손실률 밴드와의 순서는 뒤집히지 않아 최상위에 남는다.
        self.assertIn("손실률 밴드보다도 앞선다", prec["also_precedes_loss_band"])
        self.assertNotIn("also_precedes_loss_band", old)

    def test_ra5_02_is_resolved_with_a_conclusion(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA5-02"]
        self.assertEqual((t["status"], t["resolved_at"]), ("resolved", "2026-09-17"))
        self.assertIn("해소됐다", t["resolution"])
        self.assertIn("총점 2 → **4**", t["resolution"])
        self.assertEqual(t["decision_id"], "C-29")
        self.assertIn("TEN-RA6-01", t["related_tensions"])
        # 해소와 어긋나는 옛 문면을 같이 고쳤다(FIX-61 이 잡은 종류의 모순).
        self.assertNotIn("이번 실행은 현행을 유지한다", t["direction"])
        self.assertIn("반영됐다", t["score_impact_now"])
        self.assertIn("이행됐다", t["rechecker"])
        self.assertIn("같은 날 그 결정을 뒤집었다", t["note"])

    def test_the_v15_conflict_itself_stays_open_for_november(self):
        """이번 결정은 충돌을 없앤 것이 아니라 한쪽을 골랐을 뿐이다."""
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA6-01"]
        self.assertEqual((t["status"], t["recheck_at"]), ("open", "2026-11"))
        self.assertEqual(t["judgment_ids"], ["openai.F9"])
        self.assertEqual(t["third_party_recheck"], "committed")
        self.assertEqual(t["decision_id"], "C-29")
        self.assertIn("470행", t["tension"])
        self.assertIn("별표 D 388~390행", t["tension"])
        self.assertIn("한쪽을 골랐을 뿐", t["note"])
        self.assertIn("없다", t["score_impact_now"])
        self.assertIn("TEN-RA5-02", t["related_tensions"])
        # 인용한 v1.5 두 자리가 실제로 그 문장인지 원문에서 확인한다.
        if V15.is_file():
            lines = V15.read_text(encoding="utf-8").splitlines()
            self.assertIn("BEP 목표가 후퇴", lines[469])
            self.assertIn("계획·발표·포지션은 0점", lines[389])

    def test_resolved_tension_must_carry_a_conclusion(self):
        """결론 없이 `resolved` 로 바꾸면 긴장이 조용히 사라진다 — 스키마가 막는다."""
        import copy
        payload = copy.deepcopy(RULES.payload)
        t = next(x for x in payload["open_tensions"] if x["id"] == "TEN-RA5-02")
        t.pop("resolution")
        with self.assertRaises(SchemaError):
            validate_rules(payload)
        payload2 = copy.deepcopy(RULES.payload)
        t2 = next(x for x in payload2["open_tensions"] if x["id"] == "TEN-RA6-01")
        t2["resolution"] = "열린 긴장에 결론을 적었다"
        with self.assertRaises(SchemaError):
            validate_rules(payload2)

    # ---------------------------------------------------------------- S2 초안
    def test_the_draft_says_the_new_route(self):
        line = next(x for x in rc.method_lines(self.ctx) if "BEP 후퇴" in x)
        self.assertIn("**C-20 비상장 경로가 먼저 선다**", line)
        self.assertIn("앞선 결정을 뒤집음", line)
        self.assertIn(line if line.startswith("  - ") else f"- {line}", self.md)
        # openai ⑨ 근거란이 새 경로와 새 점수를 말한다.
        ev = self.j["openai.F9"]["evidence"]
        self.assertIn("**F9 = -2** 다", ev[0])
        self.assertIn("G1 판정 보류(C-20 비상장 경로)", ev[0])
        self.assertIn("SRC-v15-rule", self.j["openai.F9"]["source_ids"])
        self.assertIn("⚠️ C-29: BEP 후퇴가 기록돼 있으나 **C-20 이 앞선다**", self.md)
        self.assertIn("| OpenAI | 2 / 14 | 4 / 13 |", (RUN_DIR / "preview.md").read_text(encoding="utf-8"))

    def test_resolved_tension_leaves_the_promise_count(self):
        lines = rc.conflict_lines(self.ctx)
        head = next(x for x in lines if "제3자 재검토 약속" in x)
        self.assertIn("**확정**된 긴장 5건", head)          # 해소분이 빠지고 새 긴장이 들어와 건수가 같다
        self.assertIn("TEN-RA6-01(openai.F9, 2026-11)", head)
        self.assertNotIn("TEN-RA5-02", head)
        done = next(x for x in lines if "이미 해소된 긴장" in x)
        self.assertIn("TEN-RA5-02(openai.F9, 2026-09-17)", done)

    # ---------------------------------------------------------------- 기록
    def test_run_records_the_reversal(self):
        d = {x["id"]: x for x in self.run_json["decisions"]}["C-29"]
        self.assertEqual((d["choice"], d["decided_by"]), ("c20_private_route_first", "사용자"))
        self.assertIn("앞선 결정", d["rationale"])
        a = next(x for x in self.run_json["assumptions"] if "openai.F9 경로를 뒤집었다" in x)
        self.assertIn("총점 2 → **4**", a)
        self.assertIn("TEN-RA6-01", a)
        self.assertIn("anthropic 은 전부터 C-20 경로라 불변이다", a)
        self.assertEqual(self.run_json["rule_hash"], RULES.hash)

    def test_plan_is_repinned_again(self):
        text = (ROOT / "plan" / f"{SLUG}.md").read_text(encoding="utf-8")
        self.assertIn(f"rule_hash: {RULES.hash}", text)
        self.assertIn("by: FIX-62 (openai.F9 경로 뒤집기 · 사용자 결정 2026-09-17)", text)
        self.assertIn("openai ⑨ -4 → -2, 총점 2 → 4", text)
        self.assertIn("점수를 바꾼 것은 아래 일곱이고", text)

    def test_q11_and_approval_untouched(self):
        review = (ROOT / "reviews" / f"{SLUG}.md").read_text(encoding="utf-8")
        q11 = next(x for x in review.splitlines() if x.startswith("| Q11 "))
        self.assertIn("| fail |", q11)
        self.assertIn("예외 아님", q11)
        self.assertFalse((RUN_DIR / "approval.json").exists())


if __name__ == "__main__":
    unittest.main()
