# FIX-53 2단계 — TSMC F5 A+1 재판정 · alibaba 확정 미인출 여신 등록 · G3 경계 표시 · TSMC net_cash 설명 · 긴장 보강을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class ExpectedTotalsTest(unittest.TestCase):
    def test_totals_match_instruction(self):
        res = {c["company_id"]: c["total"] for c in load("results.json")["companies"]}
        self.assertEqual(res, {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                               "spacex-xai": 10, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                               "openai": 2, "oracle": 2})


class TsmcStrictReadingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.jud = {(j["company_id"], j["factor"]): j for j in load("judgments.json")["items"]}

    def test_tsmc_a_plus_one_with_old_kept(self):
        j = self.jud[("tsmc", "F5")]
        self.assertEqual(j["judgment_id"], "tsmc.F5.strict54")
        self.assertEqual(j["inputs"], {"A": 1, "H": -1})
        self.assertEqual(j["reviewer"], "설계진행(A-STRICT-54 codex·Gemini 독립 일치)")
        self.assertEqual(j["superseded"]["inputs"], {"A": 2, "H": -1})
        text = " ".join(j["evidence"])
        for line in ("192·193행", "218행", "289행", "243행"):
            self.assertIn(line, text)
        self.assertIn("945행", " ".join(j["counter_evidence"]))       # 인용 정정 기록

    def test_other_plus_two_companies_untouched(self):
        for cid in ("alphabet", "amazon", "microsoft"):
            with self.subTest(cid=cid):
                j = self.jud[(cid, "F5")]
                self.assertEqual(j["judgment_id"], f"{cid}.F5")
                self.assertEqual((j["inputs"]["A"], j["status"]), (2, "carried"))


class AlibabaUndrawnCreditTest(unittest.TestCase):
    def setUp(self) -> None:
        self.obs = {o["observation_id"]: o for o in load("observations.json")["items"]}
        res = {c["company_id"]: c for c in load("results.json")["companies"]}
        self.f9 = res["alibaba"]["factors"]["F9"]

    def test_registered_from_audited_note(self):
        o = self.obs["alibaba.undrawn_credit.fix53"]
        self.assertEqual((o["value"], o["status"], o["as_of"]), (3330000000.0, "verified", "2026-03-31"))
        self.assertIn("주석 21", o["basis"]["primary"]["location"])
        self.assertIn("has not yet been drawn down", o["basis"]["primary"]["quote"])
        self.assertIn("MD&A", o["basis"]["cross_check"]["location"])

    def test_approximate_facility_is_recorded_but_not_used(self):
        o = self.obs["alibaba.undrawn_credit_approx.fix53"]
        self.assertEqual((o["value"], o["kind"], o["status"]), (2600000000.0, "estimate", "incompatible_basis"))
        self.assertIn("approximately", o["basis"]["primary"]["quote"])
        self.assertIn("3.4595", o["basis"]["sensitivity"])
        self.assertIn("alibaba.undrawn_credit.fix53", self.f9["observation_ids"])
        self.assertNotIn("alibaba.undrawn_credit_approx.fix53", self.f9["observation_ids"])

    def test_runway_and_score(self):
        g3 = next(p for p in self.f9["calc"]["path"] if p["gate"] == "G3")
        self.assertAlmostEqual(g3["runway_years"], 22398 / 7226, places=6)
        self.assertEqual(g3["step"], 0)
        self.assertEqual(self.f9["score"], -3)

    def test_g3_boundary_uses_same_tolerance(self):
        """**허용폭을 자리마다 달리하지 않는다.** alibaba 는 +3.32% 라 ±3% 밖이고 flag 는 false 다."""
        g3 = next(p for p in self.f9["calc"]["path"] if p["gate"] == "G3")
        b = g3["boundary"]
        self.assertEqual(b["nearest_boundary"], 3.0)
        self.assertEqual(b["tolerance"], RULES.payload["policies"]["f6"]["boundary_tolerance"])
        self.assertAlmostEqual(b["distance_ratio"], 22398 / 7226 / 3 - 1, places=9)
        self.assertFalse(b["flag"])

    def test_g3_boundary_flags_inside_tolerance(self):
        from scorecard.calc_f9 import _runway_boundary
        self.assertTrue(_runway_boundary(3.05, RULES)["flag"])
        self.assertFalse(_runway_boundary(3.2, RULES)["flag"])


class TsmcNetCashAndTensionsTest(unittest.TestCase):
    def test_pledged_cd_note_35_and_sensitivity(self):
        q = " ".join(RULES.payload["policies"]["f6"]["net_cash"]["open_questions"])
        self.assertIn("NT$ 129.40 million", q)
        self.assertIn("69.2208B", q)
        o = next(x for x in load("observations.json")["items"] if x["observation_id"] == "tsmc.net_cash.nc37")
        self.assertTrue(o["basis"]["open_item_correction"]["sensitivity"]["p2_band_unchanged"])

    def test_rc03_affected_and_stargate(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RC-03"]
        self.assertEqual({a["company_id"] for a in t["affected"]}, {"alphabet", "amazon", "meta", "nvidia"})
        self.assertIn("192행", t["note"])
        self.assertIn("Stargate", t["note"])

    def test_rb_q10_registered(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RB-Q10"]
        self.assertEqual(t["judgment_ids"], ["microsoft.F3", "spacex-xai.F3", "tesla.F3"])
        self.assertEqual(t["recheck_at"], "2026-11")
        self.assertIn("하향 가능", t["direction"])


if __name__ == "__main__":
    unittest.main()
