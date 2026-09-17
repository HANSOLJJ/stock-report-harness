# FIX-56 1단계 — 5차 리뷰 B·D 반영(spacex-xai P2 산출 · 긴장 둘 · 감사 경로)을 고정한다
from __future__ import annotations

import copy
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
from scorecard.schema import SchemaError, validate_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402
from tests.test_scorecard_f6_v17 import company, f6obs, run  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Stage1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(cls.ctx.run["baseline_id"])
        cls.md = render_draft(cls.ctx, cls.results, base, triggers)

    def test_totals(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 4, "oracle": 2})

    # ---------------------------------------------------------------- S1 TTM 매출 · P2
    def test_ttm_revenue_registered_as_its_own_metric(self):
        """분기값 `revenue_ttm` 과 이름을 나눈다 — 같은 이름에 두 뜻을 담지 않는다."""
        o = self.o["spacex-xai.revenue_ttm_full.fix56"]
        self.assertEqual((o["metric"], o["value"], o["status"]), ("revenue_ttm_full", 23044000000.0, "verified"))
        self.assertEqual(o["period"], {"start": "2025-07-01", "end": "2026-06-30"})
        self.assertEqual(o["basis"]["period_basis"], "ttm")
        parts = {c["label"].split(" ")[0]: (c["value"], c["sign"], c["accession"]) for c in o["basis"]["components"]}
        self.assertEqual(parts["FY2025"], (18674000000.0, "+", "0001628280-26-040364"))
        self.assertEqual(parts["H1'2026"], (12508000000.0, "+", "0001628280-26-052535"))
        self.assertEqual(parts["H1'2025"], (8138000000.0, "-", "0001628280-26-052535"))
        self.assertEqual(sum(c["value"] * (1 if c["sign"] == "+" else -1) for c in o["basis"]["components"]),
                         o["value"])
        # 분기 관측은 그대로 있고 트랙을 정하는 자리도 그대로다.
        q = self.o["spacex-xai.revenue_ttm.f6reg28"]
        self.assertEqual((q["value"], q["basis"]["period_basis"]), (7814000000.0, "quarterly_yoy"))
        self.assertIn("spacex-xai.revenue_ttm_full.fix56", q["basis"]["ttm_is_constructible"]["registered_as"])

    def test_listed_newly_track_now_computes_p2(self):
        track = RULES.payload["policies"]["f6"]["tracks"]["listed_newly"]
        self.assertEqual(track["parameters"], ["P2", "P3"])
        self.assertEqual(track["optional_parameters"], ["P2"])
        self.assertNotIn("P1·P2 입력이 성립하지 않는", track["select"])
        self.assertIn("basis.period_basis", track["select"])
        self.assertIn("requires_positive", track["parameters_excluded_note"])
        self.assertEqual(track["floor"], -3)                            # 바닥은 이번에 건드리지 않는다 (C-25 미결)
        alt = RULES.f6_parameters()["P2"]["input_alternatives"]
        self.assertEqual(alt, {"revenue_ttm": ["revenue_ttm_full"]})

    def test_spacex_p2_value_band_subtotal_and_floor(self):
        calc = self.res["spacex-xai"]["factors"]["F6"]["calc"]
        p2 = calc["parameters"]["P2"]
        self.assertEqual(p2["inputs"]["market_cap"], 1910000000000.0)
        self.assertEqual(p2["inputs"]["net_cash"], 60301000000.0)
        self.assertEqual(p2["inputs"]["revenue_ttm"], 23044000000.0)
        self.assertEqual(p2["inputs"]["input_alternatives_used"]["revenue_ttm"]["metric"], "revenue_ttm_full")
        self.assertAlmostEqual(p2["value"], (1910000 - 60301) / 23044, places=6)
        self.assertAlmostEqual(p2["value"], 80.268139, places=6)
        self.assertEqual((p2["score"], p2["band"]), (-2, "20+"))
        self.assertEqual(calc["parameters"]["P3"]["score"], 0)
        self.assertEqual(calc["subtotal_before_p4"], -2)
        self.assertEqual(calc["p4"]["demotion_steps"], 1)
        self.assertEqual(self.res["spacex-xai"]["factors"]["F6"]["score"], -3)
        # 바닥과 같지만 **절단된 것은 아니다** — 절단이 일어나면 C-25 를 다시 볼 자리다.
        self.assertNotIn("floor_applied", calc)
        self.assertIn("spacex-xai.revenue_ttm_full.fix56", self.res["spacex-xai"]["factors"]["F6"]["observation_ids"])

    def test_p1_stays_out_with_a_recorded_reason(self):
        """트랙에서 뺀 것과 입력이 없어 못 만드는 것을 가른다."""
        p1 = self.res["spacex-xai"]["factors"]["F6"]["calc"]["parameters_not_in_track"]["P1"]
        self.assertFalse(p1["would_compute"])
        self.assertIn("requires_positive", p1["why"])
        self.assertEqual(p1["inputs"]["net_income_ttm"], -8218000000.0)

    def test_optional_parameter_missing_does_not_pend_the_factor(self):
        """입력이 없으면 만들지 않는다 — 없다고 F6 전체를 pending 으로 세우지 않는다."""
        obs = f6obs(market_cap=1000.0, net_cash=None, net_income=-50.0, revenue=100.0,
                    revenue_prior=80.0, period_basis="quarterly_yoy")
        r = compute_f6(company(), obs, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["calc"]["track"], "listed_newly")
        self.assertEqual(r["status"], "ok")
        self.assertNotIn("P2", r["calc"]["parameters"])
        self.assertIn("P2 입력 net_cash 관측 없음", r["calc"]["parameters_optional_unmet"]["P2"]["why"])

    def test_schema_requires_optional_parameters_to_be_used_by_the_track(self):
        bad = copy.deepcopy(RULES.payload)
        bad["policies"]["f6"]["tracks"]["listed_newly"]["optional_parameters"] = ["P1"]
        with self.assertRaises(SchemaError):
            validate_rules(bad)

    def test_schema_requires_alternative_metric_to_share_the_unit(self):
        bad = copy.deepcopy(RULES.payload)
        bad["policies"]["f6"]["parameters"]["P2"]["input_alternatives"] = {"revenue_ttm": ["ps_ratio"]}
        with self.assertRaises(SchemaError):
            validate_rules(bad)

    def test_other_listed_companies_keep_their_f6(self):
        """12개 상장사 중 spacex-xai 만 바뀐다 — 대체 지표가 없는 회사는 `revenue_ttm` 을 그대로 읽는다."""
        for cid, want in (("alphabet", -3), ("amazon", -2), ("meta", -1), ("microsoft", -3), ("tsmc", -3),
                          ("nvidia", -2), ("apple", -4), ("alibaba", -4), ("palantir", -4), ("tesla", -5),
                          ("oracle", -3)):
            with self.subTest(cid=cid):
                calc = self.res[cid]["factors"]["F6"]["calc"]
                self.assertEqual(self.res[cid]["factors"]["F6"]["score"], want)
                self.assertNotIn("input_alternatives_used", calc["parameters"]["P2"]["inputs"])

    def test_floor_open_item_registered(self):
        c25 = {d["id"]: d for d in RULES.payload["decisions"]}["C-25"]
        self.assertEqual(c25["status"], "pending")
        self.assertIn("바닥", c25["summary"])
        self.assertEqual(c25["implementation_status"]["verdict"], "not_implemented")
        c24 = {d["id"]: d for d in RULES.payload["decisions"]}["C-24"]
        self.assertEqual((c24["status"], c24["chosen"], c24["decided_by"]),
                         ("resolved", "compute_p2_when_inputs_exist", "사용자"))
        self.assertIn("C-24", [d["id"] for d in load("run.json")["decisions"]])

    # ---------------------------------------------------------------- S2 긴장
    def test_amazon_and_palantir_f3_join_q10(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RB-Q10"]
        self.assertEqual(sorted(t["judgment_ids"]),
                         ["amazon.F3", "microsoft.F3", "palantir.F3", "spacex-xai.F3", "tesla.F3"])
        affected = {a["judgment_id"]: a for a in t["affected"]}
        self.assertIn("수치가 없다", affected["amazon.F3"]["why"])
        self.assertIn("가속도를 말하는 줄이 아예 없다", affected["palantir.F3"]["why"])
        for jid in ("amazon.F3", "palantir.F3"):
            self.assertEqual(affected[jid]["source_lines"], ["채점규칙 145행", "채점규칙 153행"])
            self.assertEqual(self.j[jid]["inputs"]["acceleration"], "pass")     # 판정은 바꾸지 않았다
        self.assertEqual(self.res["amazon"]["factors"]["F3"]["score"], 3)
        self.assertEqual(self.res["palantir"]["factors"]["F3"]["score"], 3)

    # ---------------------------------------------------------------- S3 감사 경로
    def test_p4_inputs_are_in_the_f6_audit_trail(self):
        """P4 `nonop_share` 입력 관측 id 가 F6 observation_ids 에 있어야 한다 — 14개사 전부."""
        for c in self.results["companies"]:
            f6 = c["factors"]["F6"]
            p4 = (f6.get("calc") or {}).get("p4") or {}
            ids = p4.get("nonop_share_observation_ids")
            with self.subTest(cid=c["company_id"]):
                if not c["listed"]:
                    self.assertIsNone(ids)                     # 비상장은 P4 가 자본효율이라 이 경로가 없다
                    continue
                self.assertTrue(ids)
                for oid in ids:
                    self.assertIn(oid, f6["observation_ids"])
                self.assertEqual(len(f6["observation_ids"]), len(set(f6["observation_ids"])))
        alphabet = self.res["alphabet"]["factors"]["F6"]
        self.assertEqual(alphabet["calc"]["p4"]["demotion_sole_cause"], "nonop_share")
        self.assertIn("alphabet.pretax_income_ttm.nonop44", alphabet["observation_ids"])

    def test_conflict_count_is_by_source_not_by_wording(self):
        flagged = [s for s in self.ctx.sources["items"] if s.get("conflict_of_interest")]
        self.assertEqual(len(flagged), 6)
        self.assertEqual(len({s["conflict_of_interest"] for s in flagged}), 5)      # v15 둘의 문구가 같다
        line = next(x for x in rc.conflict_lines(self.ctx) if "이해상충" in x)
        self.assertIn("표기된 출처가 6건", line)
        self.assertIn("표기된 출처가 6건", self.md)

    def test_spacex_crypto_asset_judgment_recorded(self):
        excluded = self.o["spacex-xai.net_cash.nc37"]["basis"]["components"]["excluded_nonmarketable_present"]
        crypto = excluded["us-gaap:CryptoAssetFairValueNoncurrent"]
        self.assertEqual((crypto["value"], crypto["as_of"]), (1098000000.0, "2026-06-30"))
        self.assertIn("유가증권이 아니다", crypto["why"])
        self.assertIn("61,399", crypto["if_included"])
        self.assertIn("밴드 -2 는 그대로", crypto["if_included"])
        # 제외가 유지돼야 60,301 이 서고 S1 계산이 성립한다.
        self.assertEqual(self.o["spacex-xai.net_cash.nc37"]["value"], 60301000000.0)
        kept = self.o["spacex-xai.net_cash.nc37"]["basis"]["completeness"]["why_value_kept"]
        self.assertIn("이제 점수에 닿는다", kept)
        self.assertIn("1,449,120M", kept)

    def test_alibaba_lease_row_has_line_and_quote(self):
        rows = self.o["alibaba.net_cash.nc37"]["basis"]["components"]["rows"]
        lease = next(r for r in rows if r["kind"] == "lease")
        self.assertEqual(lease["rmb_million"], 21726.0)
        self.assertIn("Total operating lease liabilities (Note 19) 21,726", lease["quote"])
        self.assertIn("4,318", lease["cross_check"]["note_19"])
        self.assertIn("17,408", lease["cross_check"]["note_19"])
        self.assertTrue(lease["cross_check"]["matched"])
        self.assertEqual(self.o["alibaba.net_cash.nc37"]["basis"]["components"]["lease_total"], 21726.0)
        for r in rows:
            self.assertIn("line", r)

    def test_openai_f9_evidence_reads_the_current_scale(self):
        ev = self.j["openai.F9"]["evidence"]
        self.assertIn("현재 척도는 -4 다", ev[0])            # 하한 재척도는 그대로다
        self.assertTrue(any("~~-5~~" in e for e in ev))
        self.assertTrue(any("~~-5(바닥)~~" in e for e in ev))
        # 2026-09-17 FIX-62: 경로가 C-20 으로 바뀌어 하한을 받지 않는다. 표시 줄이 그 사실까지 말해야 한다.
        self.assertIn("**F9 = -2** 다", ev[0])
        self.assertIn("~~엔진 경로는 `G1 BEP 후퇴 → -4`", ev[0])
        self.assertEqual(self.res["openai"]["factors"]["F9"]["score"], -2)
        self.assertEqual(self.j["openai.F9"]["inputs"]["bep_retreat"], "yes")       # 판정 입력은 그대로
        self.assertIn("현재 척도는 -4 다", self.md)

    def test_alibaba_p2_asof_mismatch_and_sensitivity(self):
        s = self.o["alibaba.market_cap.v15"]["basis"]["p2_asof_mismatch"]
        self.assertIn("2026-09-02", s["what"])
        self.assertIn("2026-03-31", s["what"])
        self.assertAlmostEqual(s["sensitivity"]["as_reported"]["ev_sales"], 1.4835570590243028, places=6)
        self.assertAlmostEqual(s["sensitivity"]["plus_august_raise_10_2b"]["ev_sales"], 1.4148506697030425, places=6)
        self.assertEqual(s["sensitivity"]["plus_august_raise_10_2b"]["score"], 0)
        p2 = self.res["alibaba"]["factors"]["F6"]["calc"]["parameters"]["P2"]
        self.assertAlmostEqual(p2["value"], s["sensitivity"]["as_reported"]["ev_sales"], places=9)
        self.assertEqual(p2["score"], 0)

    def test_amazon_364_day_facility_note(self):
        b = self.o["amazon.undrawn_credit.fix54"]["basis"]
        self.assertIn("2026-10 만기", b["short_term_facility_note"])
        self.assertIn("approval by the lenders", b["short_term_facility_note"])
        self.assertIn("6.73년", b["short_term_facility_note"])
        self.assertEqual(b["sensitivity"]["ex_364_day_only"]["g3_step"], 0)
        self.assertAlmostEqual(b["sensitivity"]["ex_364_day_only"]["runway_years"], (78213 + 32500) / 11625, places=6)
        self.assertAlmostEqual(b["sensitivity"]["none"]["runway_years"], 6.728, places=3)
        self.assertEqual(self.res["amazon"]["factors"]["F9"]["score"], -2)


if __name__ == "__main__":
    unittest.main()
