# FIX-61 — 9차 재판정 반영(FIX-59 문면 모순 셋 · 순손실 상장사 트랙 경로 · 기록)을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402
from tests.test_scorecard_f6_v17 import company, f6obs, run  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / SLUG
SRC = ROOT / "scripts" / "scorecard"
LISTED_TRACKS = ("listed_ttm", "listed_annual")


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Fix61Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
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

    # ---------------------------------------------------------------- S1 문면 모순 셋
    def test_no_place_still_calls_the_precedence_undecided(self):
        """FIX-59 가 확정한 것을 세 자리가 `결정 대기`·`미결` 이라고 적었다."""
        for name in ("calc_f9.py", "render_common.py"):
            with self.subTest(name=name):
                text = (SRC / name).read_text(encoding="utf-8")
                self.assertNotIn("우선순위 명문화는 결정 대기", text)
                self.assertNotIn("손실률 경계·우선순위 명문화만 미결", text)
        # 2026-09-17 FIX-67: 방법 문장을 다시 쓰면서 `우선순위는 확정됐다` 는 표현이 빠졌다.
        # 지켜야 할 사실은 **미결이 아닌 것을 미결이라 적지 않는 것**이고 그것은 그대로다.
        self.assertIn("**우선순위는 확정됐다**", (SRC / "calc_f9.py").read_text(encoding="utf-8"))
        c06 = {d["id"]: d for d in RULES.payload["decisions"]}["C-06"]
        # 2026-09-17 FIX-63: 같은 문장이 뒤집힌 순서를 반대로 적고 있어 다시 썼다. 요지는 같다.
        self.assertIn("우선순위는 미결이 아니다", c06["summary"])
        self.assertIn("C-20 비상장 경로가 먼저 서고", c06["summary"])
        self.assertNotIn("BEP 후퇴→-5", c06["summary"])
        # C-06 의 나머지 미결은 그대로다.
        self.assertEqual(c06["status"], "pending")
        for frag in ("FCF/영업손익 0", "완충 잠식", "G2 안정/악화의 기계 정의 부재"):
            self.assertIn(frag, c06["summary"])

    def test_corrected_sentence_reaches_the_draft(self):
        # 2026-09-17 FIX-67: 문장을 다시 썼다. 사실 셋이 그대로 있는지를 본다.
        lines = rc.method_lines(self.ctx, self.results)
        undecided = next(x for x in lines if "아직 정하지 못한 것" in x)
        for frag in ("수치가 정확히 0", "현금 완충", "현금흐름 추세"):
            with self.subTest(frag=frag):
                self.assertIn(frag, undecided)
        self.assertFalse(any("미결이다" in x for x in lines))
        # 경고 문구도 같이 고쳤다. 2026-09-17 FIX-62 로 openai 가 C-20 경로로 옮겨가 이 실행에서는
        # C-06 경고가 서지 않는다 — 문면은 코드에서 확인하고, 실행에는 뒤집기 경고가 대신 선다.
        code = (SRC / "calc_f9.py").read_text(encoding="utf-8")
        self.assertIn("**우선순위는 확정됐다**", code)
        self.assertNotIn("우선순위 명문화는 결정 대기", code)
        w = next(x for x in self.res["openai"]["factors"]["F9"]["warnings"] if "BEP 후퇴" in x)
        self.assertIn("C-20 이 앞선다", w)
        self.assertNotIn("결정 대기", w)

    def test_precedence_records_that_it_precedes_the_loss_band(self):
        """2026-09-17 FIX-63: 이 테스트는 `순서가 관측되지 않는다` 를 이름으로 걸고 **전제만** 확인했다.
        전제(`bep_retreat 점수 == 최심 밴드 == floor`)는 참이지만 결론은 거짓이다 — 두 순서가 실제로
        같은 점수를 내는지는 아무 테스트도 대지 않았다. 사실 확인은 test_scorecard_fix63.py 가 한다."""
        prec = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]
        note = prec["also_precedes_loss_band"]
        self.assertIn("G1 통과와 손실률 밴드 둘 다보다 앞선다", note)   # FIX-64 가 범위를 넓혔다
        # 2026-09-17 FIX-62: C-20 과의 순서만 뒤집혔고 손실률 밴드와의 순서는 그대로다.
        self.assertIn("C-20 자체보다는 뒤로 밀렸다", note)
        # 2026-09-17 FIX-63: 틀린 닫음을 되살리지 않는다.
        self.assertNotIn("어느 쪽을 먼저 보든 점수가 -4 다", note)
        self.assertIn("이 닫음은 틀렸다", note)
        f9 = RULES.payload["policies"]["f9"]
        deepest = min(b["score"] for b in f9["g1_bands_proposed"])
        self.assertEqual(f9["g1_bep_retreat_score"], deepest)
        self.assertEqual(f9["g1_bep_retreat_score"], f9["floor"])
        # 전제가 참이어도 순서가 관측되지 않는다는 결론은 서지 않는다 — 밴드가 더 얕을 수 있다.
        self.assertTrue(any(b["score"] > deepest for b in f9["g1_bands_proposed"]))

    # ---------------------------------------------------------------- S2 순손실 상장사 트랙
    def test_loss_making_listed_company_keeps_p2_p3(self):
        """합성 순손실 상장사 — 소계가 P2·P3 로 나오고 pending_data 가 아니어야 한다."""
        obs = f6obs(market_cap=1000.0, net_cash=100.0, net_income=-50.0, revenue=100.0,
                    revenue_prior=80.0, period_basis="ttm")
        r = compute_f6(company(), obs, JudgmentLookup([]), RULES, run())
        calc = r["calc"]
        self.assertEqual(calc["track"], "listed_ttm")
        self.assertEqual(r["status"], "ok")                          # pending_data 가 아니다
        self.assertNotIn("P1", calc["parameters"])
        self.assertIn("net_income_ttm 이 0 이하", calc["parameters_optional_unmet"]["P1"]["why"])
        self.assertEqual(sorted(calc["parameters"]), ["P2", "P3"])
        self.assertEqual(calc["subtotal_before_p4"],
                         calc["parameters"]["P2"]["score"] + calc["parameters"]["P3"]["score"])
        self.assertIsNotNone(r["score"])

    def test_the_same_loss_used_to_pend_the_whole_factor(self):
        """고치기 전 동작을 대조로 남긴다 — 선택 목록이 비면 예전처럼 pending_data 다."""
        import copy
        from scorecard.rules import RuleSet
        payload = copy.deepcopy(RULES.payload)
        payload["policies"]["f6"]["tracks"]["listed_ttm"].pop("optional_parameters")
        old = RuleSet.__new__(RuleSet)
        old.__dict__.update(RULES.__dict__)
        old.payload = payload
        obs = f6obs(market_cap=1000.0, net_cash=100.0, net_income=-50.0, revenue=100.0,
                    revenue_prior=80.0, period_basis="ttm")
        r = compute_f6(company(), obs, JudgmentLookup([]), old, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIsNone(r["score"])

    def test_missing_net_income_still_pends_on_the_listed_tracks(self):
        """**순손실은 그 기업의 성질이고 결측은 우리 문제다.** 사유를 가른다."""
        obs = f6obs(market_cap=1000.0, net_cash=100.0, net_income=None, revenue=100.0,
                    revenue_prior=80.0, period_basis="ttm")
        r = compute_f6(company(), obs, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")                # 관측이 없으면 예전처럼 막힌다
        self.assertNotIn("parameters_optional_unmet", r["calc"])
        for tid in LISTED_TRACKS:
            self.assertEqual(RULES.payload["policies"]["f6"]["tracks"][tid]["optional_parameters_causes"],
                             {"P1": ["requires_positive"]})
        # 소유 범위 불일치는 어느 트랙에서도 넘기지 않는다(FC-04 가드).
        from scorecard.schema import OPTIONAL_CAUSES
        self.assertNotIn("scope_mismatch", OPTIONAL_CAUSES)

    def test_live_run_unchanged_for_both_listed_tracks(self):
        seen = 0
        for c in self.results["companies"]:
            calc = c["factors"]["F6"].get("calc") or {}
            if calc.get("track") not in LISTED_TRACKS:
                continue
            seen += 1
            with self.subTest(cid=c["company_id"]):
                self.assertEqual(c["factors"]["F6"]["status"], "ok")
                self.assertIn("P1", calc["parameters"])              # 순이익이 양수라 그대로 산출된다
                self.assertNotIn("parameters_optional_unmet", calc)
                self.assertGreater(calc["parameters"]["P1"]["inputs"]["net_income_ttm"], 0)
        self.assertEqual(seen, 11)

    def test_c24_scope_did_not_leak_to_the_other_tracks(self):
        """C-24 는 신규 상장 트랙의 P2 만 가리키는 결정이다."""
        for c in self.results["companies"]:
            calc = c["factors"]["F6"].get("calc") or {}
            with self.subTest(cid=c["company_id"]):
                if calc.get("track") == "listed_newly":
                    self.assertEqual(calc["c24_choice"]["optional"], ["P2"])
                else:
                    self.assertNotIn("c24_choice", calc)
        self.assertIn('tid == "listed_newly" and "P2" in optional_pids',
                      (SRC / "calc_f6_params.py").read_text(encoding="utf-8"))

    def test_c28_is_closed_with_the_remaining_question(self):
        c28 = {d["id"]: d for d in RULES.payload["decisions"]}["C-28"]
        self.assertEqual((c28["status"], c28["chosen"]), ("resolved", "optional_parameters_for_all_listed_tracks"))
        self.assertEqual(c28["implementation_status"]["verdict"], "implemented")
        self.assertIn("C-25 와 함께 본다", c28["remaining_question"])
        self.assertNotIn("pending_recheck", c28)
        for tid in LISTED_TRACKS:
            track = RULES.payload["policies"]["f6"]["tracks"][tid]
            self.assertEqual(track["optional_parameters"], ["P1"])
            self.assertIn("C-28 닫음", track["optional_parameters_note"])
        self.assertTrue(any("미결 C-28 닫음" in a for a in self.run_json["assumptions"]))

    # ---------------------------------------------------------------- S3 기록
    def test_arr_growth_period_is_recorded_as_unknown(self):
        b = self.o["anthropic.arr_prior.priv31"]["basis"]
        self.assertIsNone(b["period_label"])                          # 지어내지 않았다
        note = b["period_unknown_blocks_growth"]
        self.assertIn("몇 개월치인지 알 수 없다", note)
        self.assertIn("kind: run_rate", note)
        self.assertIn("기간을 먼저 정해야 한다", note)
        self.assertEqual(self.res["anthropic"]["factors"]["F6"]["score"], -4)

    def test_oracle_p1_joins_the_boundary_sample(self):
        p1 = self.res["oracle"]["factors"]["F6"]["calc"]["parameters"]["P1"]
        self.assertAlmostEqual(p1["value"], 25.967109, places=6)
        self.assertEqual(p1["score"], -1)
        self.assertFalse(p1["boundary"]["flag"])
        self.assertAlmostEqual(p1["boundary"]["distance_ratio"], 0.0386843, places=6)
        c27 = {d["id"]: d for d in RULES.payload["decisions"]}["C-27"]
        self.assertIn("+3.87%", c27["recommendation"])
        self.assertIn("총점 2 와 3 을 가른다", c27["recommendation"])
        self.assertIn("alibaba G3(+3.32%)", c27["recommendation"])

    def test_oracle_undrawn_null_counts_as_zero(self):
        note = self.o["oracle.undrawn_credit.fix54"]["basis"]["null_counts_as_zero"]
        self.assertIn("설계대로다", note)
        self.assertIn("39,769M", note)
        g3 = next(p for p in self.res["oracle"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G3")
        self.assertAlmostEqual(g3["runway_years"], 31289 / 23686, places=9)
        self.assertEqual(g3["buffer"], 31289000000.0)                 # 여신이 0 으로 들어갔다
        self.assertAlmostEqual(3 * 23686 - 31289, 39769, places=6)

    # ---------------------------------------------------------------- S4 Q11 은 그대로
    def test_q11_untouched(self):
        review = (ROOT / "output" / SLUG / "review.md").read_text(encoding="utf-8")
        q11 = next(x for x in review.splitlines() if x.startswith("| Q11 "))
        # 2026-09-17 FIX-63·64: 리뷰어가 재판정 2회에서 pass 로 바꾸고 최종 판정에서 유지했다.
        self.assertIn("| pass |", q11)
        self.assertIn("순적자 때문에 점수를 못 받거나 실격된 기업이 없다", q11)
        self.assertTrue((RUN_DIR / "approval.json").exists())   # FIX-64 에서 승인됐다


if __name__ == "__main__":
    unittest.main()
