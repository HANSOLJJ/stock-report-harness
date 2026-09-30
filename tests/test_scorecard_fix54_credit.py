# FIX-54 1단계 S1·S2 — spacex-xai 확정 미인출 여신 하한 등록(F9 -3)과 14개사 전수 표시를 고정한다
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class UndrawnCreditCensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.obs = {o["observation_id"]: o for o in load("observations.json")["items"]}
        cls.res = {c["company_id"]: c for c in load("results.json")["companies"]}

    def g3(self, cid):
        return next(p for p in self.res[cid]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G3")

    def test_spacex_lower_bound_and_score(self):
        o = self.obs["spacex-xai.undrawn_credit.fix54"]
        self.assertEqual((o["value"], o["status"]), (4355000000.0, "verified"))
        self.assertIn("확인된 하한", o["basis"]["narrowing"])
        self.assertTrue(o["basis"]["sensitivity"]["if_lc_outside_5000"]["boundary_flag"])
        self.assertIn("commitment to $ 0", o["basis"]["excluded"][0]["why"])
        g3 = self.g3("spacex-xai")
        self.assertAlmostEqual(g3["runway_years"], (93522 + 4355) / 32348, places=6)
        self.assertEqual(g3["step"], 0)
        self.assertTrue(g3["boundary"]["flag"])
        # 2026-09-16 FIX-56 1단계: 총점이 11 → 9 로 바뀐 것은 F6(P2 산출) 때문이고 **이 관측이 서는 F9 는 -3 그대로**다.
        self.assertEqual((self.res["spacex-xai"]["factors"]["F9"]["score"], self.res["spacex-xai"]["total"]), (-3, 9))

    def test_amazon_registered_score_unchanged(self):
        o = self.obs["amazon.undrawn_credit.fix54"]
        self.assertEqual(o["value"], 37500000000.0)
        self.assertEqual(sum(c["capacity"] for c in o["basis"]["components"]), 37500000000)
        self.assertEqual(self.res["amazon"]["factors"]["F9"]["score"], -2)

    def test_every_listed_company_has_a_credit_record(self):
        listed = ["alphabet", "amazon", "microsoft", "meta", "tsmc", "alibaba", "apple", "nvidia", "palantir",
                  "spacex-xai", "tesla", "oracle"]
        for cid in listed:
            with self.subTest(cid=cid):
                recs = [o for o in self.obs.values() if o["company_id"] == cid and o["metric"] == "undrawn_credit"]
                self.assertTrue(recs)
                for o in recs:
                    if o["value"] is None:
                        self.assertEqual(o["missing_type"], "unverified")
                        self.assertTrue(o["basis"]["why"])

    def test_oracle_gap_is_named(self):
        self.assertIn("G3 가 점수에 닿는다", self.obs["oracle.undrawn_credit.fix54"]["basis"]["why"])


if __name__ == "__main__":
    unittest.main()
