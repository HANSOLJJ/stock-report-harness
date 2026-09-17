# FIX-55 1단계 — 4차 리뷰 C·B·D 반영(긴장 다섯 · C-11 문언 · P4 관측 판정 · 서술 정정)을 고정한다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f3  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class OneJudgment:
    def __init__(self, judgment: dict) -> None:
        self.j = judgment

    def get(self, cid: str, fid: str) -> dict:
        return self.j


class Stage1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.t = {x["id"]: x for x in RULES.payload["open_tensions"]}
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.md = render_draft(ctx, cls.results, base, triggers)
        cls.run_json = load("run.json")   # TestCase.run 을 가리지 않게 이름을 다르게 둔다

    def test_totals_unchanged(self):
        # 2026-09-16 FIX-56 1단계: spacex-xai 11 → 9 (C-24 로 listed_newly 트랙이 P2 를 계산 — F6 -1 → -3). 다른 13개사는 불변이다.
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "spacex-xai": 9, "tsmc": 10, "anthropic": 10,
                          "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5, "openai": 4, "oracle": 2})

    # S1 — 긴장 다섯
    def test_new_tensions(self):
        expect = {"TEN-RC4-01": ["meta.F3", "anthropic.F3", "spacex-xai.F3"], "TEN-RC4-02": ["openai.F1"],
                  "TEN-RC4-03": ["spacex-xai.F5"], "TEN-RC4-04": ["tsmc.F3"]}
        for tid, jids in expect.items():
            with self.subTest(tid=tid):
                t = self.t[tid]
                self.assertEqual((t["judgment_ids"], t["recheck_at"], t["status"]), (jids, "2026-11", "open"))
                self.assertIn(tid.replace("TEN-", ""), t["review_finding"])
                self.assertTrue(set(jids) <= set(self.j))
        self.assertIn("비 Claude 세션", self.t["TEN-RC4-01"]["rechecker"])
        self.assertEqual(self.t["TEN-RC4-02"]["related_tensions"], ["TEN-RC-02", "TEN-RC3-03"])
        self.assertEqual(self.t["TEN-RC4-04"]["related_tensions"], ["TEN-RB-Q10"])

    def test_tension_score_claims_match_engine(self):
        """긴장에 적은 `F3 3 → 2` 는 엔진 산술이어야 한다. 판정이 아니라 재현 가능한 계산이다."""
        cases = {"anthropic.F3": ("imitation", 2), "tsmc.F3": ("acceleration", 2),
                 "meta.F3": ("imitation", 3), "spacex-xai.F3": ("imitation", 3), "alibaba.F3": ("imitation", 3)}
        for jid, (key, expected) in cases.items():
            with self.subTest(jid=jid):
                alt = copy.deepcopy(self.j[jid])
                alt["inputs"][key] = "fail"
                got = compute_f3({"company_id": alt["company_id"]}, OneJudgment(alt), RULES)
                self.assertEqual(got["score"], expected)
                self.assertEqual(self.res[alt["company_id"]]["factors"]["F3"]["score"], 3)
        self.assertIn("F3 3 → 2", self.t["TEN-RC4-01"]["direction"])
        self.assertIn("F3 3 → 2", self.t["TEN-RC4-04"]["direction"])

    def test_alibaba_tension_gets_second_reason(self):
        t = self.t["TEN-RC3-05"]
        self.assertIn("채점규칙 70행", t["source_lines"])
        self.assertIn("회수 장치가", t["tension"])

    # S2 — 문언·코드
    def test_c11_and_q22_wording_agree(self):
        c11 = next(d for d in RULES.payload["decisions"] if d["id"] == "C-11")
        scope = c11["confirmed_model"]["carryover_scope"]
        self.assertIn("두 축 입력", scope)
        self.assertIn("Q22", scope)
        q22 = next(q for q in RULES.payload["checklist"] if q["id"] == "Q22")
        self.assertIn("carryover_scope", q22["case"])
        cond = next(c for c in RULES.payload["policies"]["f6"]["p4"]["conditions"] if c["id"] == "nonop_share")
        self.assertIn("carryover_scope", cond["scope"])
        for jid in ("amazon.F7", "nvidia.F7.fix52"):   # 근거란의 방증 문구는 그대로 둔다
            self.assertTrue(any("출처가 고객사라 방증" in e for e in self.j[jid]["evidence"]))

    def test_p4_period_basis_judged_from_observation(self):
        cond = next(c for c in RULES.payload["policies"]["f6"]["p4"]["conditions"] if c["id"] == "period_basis_not_ttm")
        self.assertEqual(cond["judged_from"], "observation.basis.period_basis (calc_f6_params._p4)")
        self.assertNotIn("auto_p4_conditions", RULES.payload["policies"]["f6"]["tracks"]["listed_annual"])
        p4 = {c: (self.res[c]["factors"]["F6"]["calc"] or {}).get("p4") for c in self.res}
        self.assertEqual(p4["spacex-xai"]["conditions_hit"], ["period_basis_not_ttm", "short_history"])
        self.assertIsNone(p4["spacex-xai"]["demotion_sole_cause"])
        self.assertEqual(p4["spacex-xai"]["demotion_steps"], 1)
        # 2026-09-16 FIX-56 1단계: P2 가 붙어 소계가 -2 라 F6 는 -3 이다. **P4 는 두 조건에도 한 칸 상한 그대로**다.
        self.assertEqual(self.res["spacex-xai"]["factors"]["F6"]["score"], -3)
        self.assertEqual(p4["tsmc"]["conditions_hit"], ["period_basis_not_ttm"])        # 연간 트랙은 관측으로도 같은 결과
        self.assertEqual(p4["tsmc"]["demotion_sole_cause"], "period_basis_not_ttm")
        self.assertEqual(p4["alphabet"]["period_basis"], "ttm")

    def test_schema_rejects_auto_list_for_observation_judged_condition(self):
        bad = copy.deepcopy(RULES.payload)
        bad["policies"]["f6"]["tracks"]["listed_annual"]["auto_p4_conditions"] = ["period_basis_not_ttm"]
        with self.assertRaises(SchemaError):
            validate_rules(bad)

    def test_scope_separation_checks_consumers(self):
        for swap in ("cash", "net_cash"):
            with self.subTest(metric=swap):
                bad = copy.deepcopy(RULES.payload)
                sites = bad["policies"]["f6"]["net_cash"]["scope_separation"]["sites"]
                next(s for s in sites if s["metric"] == swap)["metric"] = "arr"
                with self.assertRaises(SchemaError):
                    validate_rules(bad)

    # S3 — 서술 정정
    def test_spacex_f9_head_line_current(self):
        head = self.j["spacex-xai.F9.obsreg25"]["evidence"][0]
        self.assertIn("런웨이 3.03년", head)
        self.assertIn("~~런웨이 2.89년(G3 계산)~~", head)
        self.assertIn("F9 -3", head)
        self.assertIn("런웨이 3.03년", self.md)

    def test_alibaba_non_gaap_runway(self):
        note = self.o["alibaba.fcf_ttm.cashfcf35"]["basis"]["non_gaap_variant"]["note"]
        self.assertIn("3.31년", note)
        self.assertIn("둘 다 3년 이상", note)
        self.assertIn("~~런웨이가 2.64년에서 2.82년이 되나 둘 다 3년 미만~~", note)

    def test_tsmc_cross_check_uses_registered_net_income(self):
        cc = self.o["tsmc.pretax_income_ttm.nonop44"]["basis"]["cross_check_ni_plus_tax"]
        self.assertEqual(cc["net_income_source"], "tsmc.net_income_ttm.f6reg28")
        self.assertEqual(cc["ni_ttm_usd"], self.o["tsmc.net_income_ttm.f6reg28"]["value"])
        self.assertAlmostEqual(cc["relative_gap"], 0.0012142601782700385, places=9)
        self.assertEqual(self.res["tsmc"]["factors"]["F6"]["score"], -3)

    def test_credit_open_items(self):
        c23 = next(d for d in RULES.payload["decisions"] if d["id"] == "C-23")
        self.assertEqual((c23["status"], c23["affects"]), ("pending", ["F9"]))
        self.assertEqual(c23["implementation_status"]["verdict"], "not_implemented")
        self.assertIn("C-23", self.o["amazon.undrawn_credit.fix54"]["basis"]["residual_term_open_item"])
        self.assertIn("다음 수집 1순위", self.o["oracle.undrawn_credit.fix54"]["basis"]["next_collection_priority"])
        self.assertTrue(any("비상장 anthropic·openai 는 관측을 만들지 않았다" in a for a in self.run_json["assumptions"]))
        self.assertNotIn("anthropic.undrawn_credit", {o["observation_id"].rsplit(".", 1)[0] for o in load("observations.json")["items"]})

    def test_demotion_sole_cause_is_named(self):
        self.assertIn("`nonop_share` 하나가 강등을 정한다", self.md)
        self.assertIn("`period_basis_not_ttm` 하나가 강등을 정한다", self.md)
        # 조건이 둘이면 단독 원인이 없으므로 그 문구도 없다
        spacex = next(line for line in self.md.splitlines() if "P4 -1(period_basis_not_ttm, short_history)" in line)
        self.assertNotIn("하나가 강등을 정한다", spacex)


if __name__ == "__main__":
    unittest.main()
