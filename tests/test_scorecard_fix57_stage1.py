# FIX-57 1단계 — 6차 리뷰 B 반영(점수 경로 선언 · oracle G4 입력 · 경계 사례 · 인용 정정)을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"
SRC = ROOT / "scripts" / "scorecard"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Stage1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.run_json = load("run.json")
        cls.ctx = load_context(SLUG)

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 2, "oracle": 2})

    # ---------------------------------------------------------------- S1 점수 경로
    def test_market_cap_on_score_path_is_twelve_and_all_unverified(self):
        """선언이 결과와 같은 것을 결과에서 세어 확인한다 — 문장만 고치면 또 어긋난다."""
        on_path = set()
        for c in self.results["companies"]:
            for fr in c["factors"].values():
                for oid in fr.get("observation_ids") or []:
                    if self.o.get(oid, {}).get("metric") == "market_cap":
                        on_path.add(oid)
        self.assertEqual(len(on_path), 12)
        self.assertIn("spacex-xai.market_cap.v15", on_path)
        self.assertEqual({self.o[oid]["status"] for oid in on_path}, {"legacy_unverified"})
        decl = self.o["spacex-xai.market_cap.v15"]["basis"]["on_score_path"]
        self.assertTrue(decl.startswith("**점수 경로 안.**"))
        self.assertIn("12건이고 이 관측이 그 12번째", decl)
        self.assertIn("전에는 `점수 경로 밖 … P1·P2 가 이 값을 쓰지 않는다` 였다", decl)   # 옛 문장은 인용으로만 남는다
        p2 = self.res["spacex-xai"]["factors"]["F6"]["calc"]["parameters"]["P2"]
        self.assertEqual(p2["inputs"]["market_cap"], 1910000000000.0)
        self.assertEqual(self.res["spacex-xai"]["factors"]["F6"]["calc"]["unverified_inputs"], {"market_cap": ["P2"]})

    def test_src_trace_record_matches_the_same_count(self):
        sa = next(x for x in RULES.payload["sources"]["not_adopted"] if x["name"] == "StockAnalysis")
        self.assertIn("점수 경로 market_cap 은 이제 12건이다", sa["prior_investigation"])
        self.assertIn("12건 전부가 점수 경로다", sa["note"])
        self.assertNotIn("점수 경로 11 + spacex-xai)", sa["note"])
        self.assertTrue(any("시총 관측 12건이 전부 점수 경로" in a for a in self.run_json["assumptions"]))

    # ---------------------------------------------------------------- S2 oracle G4
    def test_oracle_rpo_registered_from_the_filing(self):
        o = self.o["oracle.contracted_revenue.fix57"]
        self.assertEqual((o["value"], o["status"], o["as_of"]), (638000000000.0, "verified", "2026-05-31"))
        self.assertEqual(o["basis"]["tag"], "us-gaap:RevenueRemainingPerformanceObligation")
        self.assertEqual(o["basis"]["accession"], "0001193125-26-277521")
        self.assertEqual(o["basis"]["matches_legacy"]["diff"], 0)
        # 보존 원자료에서 같은 값을 다시 읽는다.
        facts = json.loads((RAW / "ORCL.companyfacts.json").read_text(encoding="utf-8"))["facts"]
        rows = [r for tax, tags in facts.items() for tag, node in tags.items()
                if tag == "RevenueRemainingPerformanceObligation"
                for unit, rs in node["units"].items() for r in rs if r["end"] == "2026-05-31"]
        self.assertEqual({r["val"] for r in rows}, {638000000000})
        self.assertIn("oracle.contracted_revenue.fix57", self.res["oracle"]["factors"]["F9"]["observation_ids"])

    def test_oracle_offbalance_records_that_it_matches_no_filing(self):
        b = self.o["oracle.offbalance_B.v15"]["basis"]
        self.assertEqual(self.o["oracle.offbalance_B.v15"]["value"], 250000000000.0)   # 값을 지어내지 않는다
        self.assertIn("어느 공시 사실과도 맞지 않는다", b["why_kept"])
        tags = {a["tag"]: a["value"] for a in b["disclosed_alternatives"]}
        self.assertEqual(tags, {"us-gaap:LesseeOperatingLeaseLiabilityPaymentsDue": 41867000000.0,
                                "us-gaap:LesseeOperatingLeaseLiabilityUndiscountedExcessAmount": 11677000000.0,
                                "us-gaap:UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount": 13309000000.0})
        self.assertEqual(b["alternatives_sum"], sum(tags.values()))
        facts = json.loads((RAW / "ORCL.companyfacts.json").read_text(encoding="utf-8"))["facts"]
        seen = {tag: r["val"] for tax, tg in facts.items() for tag, node in tg.items()
                for unit, rs in node["units"].items() for r in rs
                if r["end"] == "2026-05-31" and not r.get("start") and f"us-gaap:{tag}" in tags}
        self.assertEqual({f"us-gaap:{k}": float(v) for k, v in seen.items()}, tags)

    def test_oracle_g4_step_is_zero_either_way(self):
        g4 = next(p for p in self.res["oracle"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G4")
        self.assertEqual((g4["coverage"], g4["step"]), (2.552, 0))
        keep = float(RULES.f9["g4_coverage_keep"])
        self.assertEqual(keep, 1.0)
        alt = 638000000000.0 / 66853000000.0
        self.assertAlmostEqual(alt, 9.543326, places=5)
        self.assertGreaterEqual(min(2.552, alt), keep)                 # 어느 쪽이든 step 0
        rec = self.o["oracle.offbalance_B.v15"]["basis"]["coverage_either_way"]
        self.assertEqual(rec["legacy_250000"]["g4_step"], 0)
        self.assertEqual(rec["disclosed_sum_66853"]["g4_step"], 0)
        self.assertAlmostEqual(rec["disclosed_sum_66853"]["coverage"], alt, places=5)
        self.assertEqual(self.res["oracle"]["factors"]["F9"]["score"], -3)

    # ---------------------------------------------------------------- S3 경계·의존
    def test_boundary_comment_no_longer_claims_it_caught_alibaba(self):
        g3 = next(p for p in self.res["alibaba"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G3")
        self.assertFalse(g3["boundary"]["flag"])
        self.assertAlmostEqual(g3["boundary"]["distance_ratio"], 0.033213396, places=8)
        self.assertGreater(g3["boundary"]["distance_ratio"], g3["boundary"]["tolerance"])
        text = (SRC / "calc_f9.py").read_text(encoding="utf-8")
        self.assertIn("그 도입 사례 자체에는 표시가 붙지 않는다", text)
        self.assertNotIn("3년 임계 바로 위(+3.3%)가 되어 드러났다", text)
        c27 = {d["id"]: d for d in RULES.payload["decisions"]}["C-27"]
        self.assertEqual((c27["status"], c27["implementation_status"]["verdict"]), ("pending", "working_as_designed"))

    def test_alibaba_total_depends_on_the_credit_line(self):
        note = self.o["alibaba.undrawn_credit.fix53"]["basis"]["score_dependence"]
        for frag in ("2.6388", "G3 step 0 → **-1**", "총점 7 → **6**"):
            self.assertIn(frag, note)
        company = {c["company_id"]: c for c in self.ctx.companies.values()}["alibaba"]
        items = [o for o in self.ctx.observations
                 if not (o["company_id"] == "alibaba" and o["metric"] == "undrawn_credit")]
        r = compute_f9(company, ObsLookup(items), JudgmentLookup(self.ctx.judgments), self.ctx.rules, self.ctx.run)
        g3 = next(p for p in r["calc"]["path"] if p["gate"] == "G3")
        self.assertEqual((r["score"], g3["step"]), (-4, -1))
        self.assertAlmostEqual(g3["runway_years"], 2.6388, places=4)
        self.assertEqual(self.res["alibaba"]["factors"]["F9"]["score"], -3)     # 등록된 실제 결과는 그대로

    # ---------------------------------------------------------------- S4 인용·기록
    def test_fx_citation_uses_current_inputs(self):
        line = next(x for x in RULES.payload["policies"]["f6"]["fx"]["why_issuer_declared_first"]
                    if "환율 선택이 점수를 가르는지" in x)
        self.assertIn("31.37 로 17.1365, 32.79 로 17.9380 이고 둘 다 -1", line)
        self.assertIn("전에 적은 `32.79 로 23.485, 31.37 로 22.468, 둘 다 -2`", line)
        p2 = self.res["tsmc"]["factors"]["F6"]["calc"]["parameters"]["P2"]
        self.assertAlmostEqual(p2["value"], 17.1365, places=4)
        self.assertEqual(p2["score"], -1)

    def test_tsmc_band_sensitivity_uses_the_verified_net_cash(self):
        bs = self.o["tsmc.revenue_ttm.f6reg28"]["basis"]["band_sensitivity"]
        self.assertEqual(bs["used"], {"rate": 31.37, "value": 17.1365, "band": -1})
        self.assertEqual(bs["alternative"]["value"], 17.938)
        self.assertEqual(bs["alternative"]["band"], -1)
        self.assertFalse(bs["band_differs"])
        self.assertIn("legacy 순현금 77,000M", bs["net_cash_basis"])
        # 두 값을 원자료에서 다시 만든다 — 매출·순현금을 같은 환율로 환산한다.
        mcap, rev_twd, nc_twd = 2_150_000e6, 3_809_054.3e6, 2_171_587.1e6
        for rate, want in ((31.37, 17.1365), (32.79, 17.938)):
            self.assertAlmostEqual((mcap - nc_twd / rate) / (rev_twd / rate), want, places=3)
        self.assertAlmostEqual(self.o["tsmc.net_cash.nc37"]["value"], nc_twd / 31.37, places=2)

    def test_spacex_p2_asof_mismatch_recorded(self):
        s = self.o["spacex-xai.market_cap.v15"]["basis"]["p2_asof_mismatch"]
        self.assertIn("2026-09-02", s["what"])
        self.assertIn("2026-06-30", s["what"])
        self.assertIn("1,449,120M", s["sensitivity"]["band_change_needs"])
        self.assertEqual(s["sensitivity"]["as_reported"]["score"], -2)
        self.assertIn("p2_asof_mismatch", self.o["alibaba.market_cap.v15"]["basis"])    # 같은 형식이 둘 다 있다

    def test_loss_making_listed_track_is_an_open_item(self):
        c28 = {d["id"]: d for d in RULES.payload["decisions"]}["C-28"]
        self.assertEqual(c28["status"], "pending")
        self.assertIn("optional_parameters", c28["recommendation"])
        for track in ("listed_ttm", "listed_annual"):
            self.assertNotIn("optional_parameters", RULES.payload["policies"]["f6"]["tracks"][track])
        self.assertIn("optional_parameters", RULES.payload["policies"]["f6"]["tracks"]["listed_newly"])
        # 오늘 해당 기업이 없다는 사실도 결과에서 확인한다.
        for c in self.results["companies"]:
            calc = c["factors"]["F6"].get("calc") or {}
            if calc.get("track") in ("listed_ttm", "listed_annual"):
                with self.subTest(cid=c["company_id"]):
                    self.assertGreater(calc["parameters"]["P1"]["inputs"]["net_income_ttm"], 0)

    def test_c24_score_impact_names_both_p4_conditions(self):
        c24 = {d["id"]: d for d in RULES.payload["decisions"]}["C-24"]
        impact = c24["scope"]["score_impact"]
        self.assertIn("period_basis_not_ttm", impact)
        self.assertIn("강등은 상한 한 칸", impact)
        p4 = self.res["spacex-xai"]["factors"]["F6"]["calc"]["p4"]
        self.assertEqual(p4["conditions_hit"], ["period_basis_not_ttm", "short_history"])
        self.assertEqual(p4["demotion_steps"], 1)

    def test_ttm_reconstruction_paths_recorded_with_measured_divergence(self):
        rp = RULES.payload["policies"]["f6"]["ttm_window"]["reconstruction_paths"]
        self.assertEqual(rp["measured_divergence"]["max_abs_diff_usd"], 1000000)
        cases = {c["observation_id"]: c for c in rp["measured_divergence"]["cases"]}
        for oid, case in cases.items():
            with self.subTest(oid=oid):
                self.assertEqual(self.o[oid]["value"], float(case["stored"]))
                self.assertEqual(abs(case["stored"] - case["other_path"]), 1000000)
        # 기록한 두 건은 원자료에서 반대 경로를 직접 계산해 맞춘다.
        self.assertEqual(89_830 + 164_501 - 75_527, cases["meta.revenue_ttm_prior.f6reg28"]["other_path"] // 10**6)
        self.assertEqual(118_010 + 120_067 - 45_197, cases["nvidia.net_income_ttm.f6reg28"]["other_path"] // 10**6)
        # 나머지 F6-REG-28 관측의 대조 차는 0 이다.
        diffs = [(o["observation_id"], (o["basis"] or {})["cross_check_f6_spec_18"]["diff"])
                 for o in self.o.values() if (o.get("basis") or {}).get("cross_check_f6_spec_18")]
        self.assertEqual(len(diffs), 18)
        self.assertEqual(sorted({abs(d) for _oid, d in diffs}), [0, 1000000])

    def test_alibaba_nonop_fx_path_recorded(self):
        fx = self.o["alibaba.pretax_income_ttm.nonop44"]["basis"]["fx_path_mismatch"]
        self.assertIn("내재 환율 6.8982", fx["what"])
        p4 = self.res["alibaba"]["factors"]["F6"]["calc"]["p4"]
        self.assertAlmostEqual(p4["nonop_share"], fx["effect"]["nonop_share_as_computed"], places=12)
        self.assertAlmostEqual(fx["effect"]["rel_diff"], 1.943e-05, places=8)
        self.assertLess(fx["effect"]["rel_diff"], 1e-4)
        # 조건은 **걸린다**(0.612 ≥ 0.30). 환율 경로가 갈려도 그 판정이 뒤집히지 않는다는 것이 요점이다.
        self.assertIn("nonop_share", p4["conditions_hit"])
        self.assertTrue(fx["effect"]["condition_hit"])
        for value in (fx["effect"]["nonop_share_as_computed"], fx["effect"]["nonop_share_if_both_at_6_898"]):
            self.assertGreaterEqual(value, fx["effect"]["threshold"])

    def test_review_template_explains_the_two_hashes(self):
        text = (SRC / "render_md.py").read_text(encoding="utf-8")
        self.assertIn("두 해시의 뜻이 다르다", text)
        self.assertIn("engine.sha256_obj", text)
        self.assertIn("파일 바이트 sha256 과 다르다", text)


if __name__ == "__main__":
    unittest.main()
