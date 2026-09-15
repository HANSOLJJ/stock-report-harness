# FIX-53 3단계 — 리뷰 A 2차 반영(초안 legacy 값 · 관측 설명 정정 · spacex 세전이익 · 판단 근거란 · nvidia.F2 긴장)을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


def obs_by_id() -> dict:
    return {o["observation_id"]: o for o in load("observations.json")["items"]}


class TotalsUnchangedTest(unittest.TestCase):
    def test_totals_same_as_stage2(self):
        res = {c["company_id"]: c["total"] for c in load("results.json")["companies"]}
        self.assertEqual(res, {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                               "spacex-xai": 10, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                               "openai": 2, "oracle": 2})


class DraftLegacyValuesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ctx = load_context(SLUG)
        results = load("results.json")
        scores, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.lines = render_draft(ctx, results, scores, triggers).splitlines()

    def test_amazon_offbalance_cell_uses_verified(self):
        row = next(x for x in self.lines if x.startswith("| Amazon / AWS | $78.2B"))
        self.assertIn("$267.3B B종(verified)", row)
        self.assertIn("~~미개시 리스 $106B~~ (superseded)", row)

    def test_amazon_f9_narrative_marks_replaced_value(self):
        line = next(x for x in self.lines if "게이트 4 ✅ 미개시 리스 $106B" in x)
        self.assertIn("⚠️ 원문 $106B 는 이번 실행 실측 $267.3B(amazon.offbalance_B.obsreg25", line)

    def test_companies_without_verified_offbalance_keep_legacy_text(self):
        row = next(x for x in self.lines if x.startswith("| Meta |") and "리스 $279B" in x)
        self.assertIn("$628B", row)


class ObservationCorrectionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.o = obs_by_id()

    def test_alibaba_contracted_revenue_two_branch_exemption(self):
        o = self.o["alibaba.contracted_revenue.obsreg25"]
        self.assertEqual(o["missing_type"], "not_disclosed_confirmed")          # 분류 유지
        self.assertIn("두 갈래", o["basis"]["exemption_scope"])
        self.assertIn("1년 초과 계약 전부가 여기 든다는 근거는 없다", o["basis"]["exemption_scope"])
        self.assertIn("remaining performance obligation", o["basis"]["absence_by_full_text_search"])
        self.assertNotIn("찾아도 없을 것이 선언돼 있다. C-16", o["note"])
        self.assertIn("찾아도 없을 것이", o["basis"]["note_superseded"]["text"])

    def test_spacex_pretax_registered_and_closes(self):
        p = self.o["spacex-xai.pretax_income_ttm.fix53"]
        self.assertEqual((p["value"], p["status"]), (-7623000000.0, "verified"))
        c = p["basis"]["components"]
        self.assertEqual(c["fy2025_s1a"] + c["h1_2026_10q"] - c["h1_2025_10q"], p["value"])
        ni = self.o["spacex-xai.net_income_ttm.f6reg28"]["value"]
        self.assertEqual(p["value"] - p["basis"]["cross_check_tax"]["tax_ttm"], ni)
        self.assertEqual(self.o["spacex-xai.nonop_share.v15"]["status"], "incompatible_basis")

    def test_spacex_p4_short_history_only(self):
        c = next(x for x in load("results.json")["companies"] if x["company_id"] == "spacex-xai")
        p4 = c["factors"]["F6"]["calc"]["p4"]
        self.assertIsNone(p4["nonop_share"])
        self.assertEqual(p4["nonop_share_source"], "incompatible_basis")
        self.assertEqual(p4["conditions_hit"], ["short_history"])

    def test_negative_pretax_is_not_computed_in_engine(self):
        """세전이익이 음수면 값을 돌려주지 않는다 — 전에는 경고만 붙이고 값을 줘 P4 조건이 걸릴 수 있었다."""
        from tests.test_scorecard_f6_v17 import RULES_V17, company, f6obs, run
        r = compute_f6(company(), f6obs(pretax=-100.0, operating_income=-40.0), JudgmentLookup([]), RULES_V17, run())
        p4 = r["calc"]["p4"]
        self.assertIsNone(p4["nonop_share"])
        self.assertEqual(p4["nonop_share_source"], "incompatible_basis")
        self.assertNotIn("nonop_share", p4["conditions_hit"])
        self.assertTrue(any("부호 규약" in w for w in r["warnings"]))

    def test_spacex_cash_buffer_and_legacy_split(self):
        b = self.o["spacex-xai.cash.cashfcf35"]["basis"]
        self.assertEqual(b["preserved_wider_definitions"]["components"]["short_term_marketable_securities"], 6487000000)
        self.assertEqual(b["preserved_wider_definitions"]["liquid_cash_buffer"], 100009000000.0)
        self.assertEqual(b["legacy_comparison"]["legacy_equaled"], "유동성 버퍼")
        self.assertEqual(self.o["spacex-xai.cash.cashfcf35"]["value"], 93522000000.0)
        split = [((o.get("basis") or {}).get("legacy_comparison") or {}).get("legacy_equaled")
                 for k, o in self.o.items() if o["metric"] == "cash" and k.endswith("cashfcf35")]
        self.assertEqual((split.count("유동성 버퍼"), split.count("총계(비유동 포함)"), split.count("어느 쪽도 아님")), (8, 3, 1))
        run = load("run.json")
        self.assertTrue(any("8개사는 유동성 버퍼" in a for a in run["assumptions"]))

    def test_straddle_note_no_longer_claims_score_split(self):
        b = self.o["anthropic.cumulative_raised.priv31"]["basis"]
        self.assertIn("세 시나리오 모두 anthropic F6 = -4", b["straddle_note"])

    def test_small_corrections(self):
        self.assertIn("이중 태깅", self.o["oracle.net_cash.nc37"]["basis"]["components"]["excluded_nonmarketable_present"]
                      ["us-gaap:EquitySecuritiesWithoutReadilyDeterminableFairValueAmount"]["why"])
        self.assertIn("TTM 아님", self.o["spacex-xai.revenue_ttm.f6reg28"]["basis"]["period_label"])
        self.assertIn("148건", self.o["palantir.lease_liabilities.nc37"]["basis"]["why_not_unverified"])
        self.assertNotIn("916행", self.o["tsmc.pretax_income_ttm.nonop44"]["basis"]["how_reconstructed"])
        self.assertIn("RestrictedCashNoncurrent",
                      json.dumps(self.o["tesla.net_cash.nc37"]["basis"]["components"]["excluded_nonmarketable_present"]))


class JudgmentCorrectionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}

    def test_anthropic_f2_old_yardstick_struck(self):
        ev = self.j["anthropic.F2"]["evidence"]
        self.assertIn("~~+ Artificial Analysis Index 1위~~ (superseded", ev[0])
        self.assertTrue(ev[1].startswith("(superseded"))
        self.assertEqual((self.j["anthropic.F2"]["score"], self.j["anthropic.F2"]["status"]), (5, "carried"))

    def test_f2_notes_say_c03_confirmed(self):
        for jid, j in self.j.items():
            if j["factor"] == "F2":
                with self.subTest(jid=jid):
                    self.assertIn("C-03 확정(paths_with_generation_gap_5)", j["note"])

    def test_f8anth33_label_and_document_split(self):
        text = " ".join(self.j["anthropic.F8.f8anth33"]["evidence"])
        self.assertIn("more than $100.0 billion", text)
        self.assertIn("채점표_v1.5.md 188·198·350행 · 채점규칙_v1.5.md 217행", text)
        # 3단계 보완에서 `4배` 줄에도 같은 표식을 붙였다 — 라벨 줄 자체에는 한 번만 붙는지 본다.
        label_line = next(e for e in self.j["anthropic.F8.f8anth33"]["evidence"] if "AWS $100B/10년" in e)
        self.assertEqual(label_line.count("FIX-53 3단계 라벨 정정"), 1)

    def test_nvidia_f2_tension(self):
        n = self.j["nvidia.F2"]
        self.assertTrue(n["evidence"][0].startswith("(발표 — NVIDIA 보도자료)"))
        self.assertIn("TRIG-016", n["note"])
        self.assertIn("출처가 없다", n["note"])
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA-02"]
        self.assertEqual((t["judgment_ids"], t["recheck_at"]), (["nvidia.F2"], "2026-11"))
        self.assertIn("하향 가능", t["direction"])
        self.assertIn("#11", t["note"])


if __name__ == "__main__":
    unittest.main()
