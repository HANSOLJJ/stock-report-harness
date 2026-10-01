# FIX-58 1단계 — 7차 리뷰 B·C·D 반영(순현금 시장성 지분증권 같은 잣대 · 태그 오독 · 기간 방어 · 기록)을 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.render_html import OBS_STATUS_LABELS, render_incomplete  # noqa: E402
from scorecard.render_md import STATUS_LABEL  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from tests._raw import require_raw  # noqa: E402
from tests.test_scorecard_f6_v17 import company, obs, run  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / SLUG
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"
SRC = ROOT / "scripts" / "scorecard"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


def facts(tick: str, tag: str, end: str) -> list[float]:
    d = json.loads((RAW / f"{tick}.companyfacts.json").read_text(encoding="utf-8"))
    return sorted({r["val"] for tax, tags in d["facts"].items() if tag in tags
                   for unit, rs in tags[tag]["units"].items() if unit == "USD"
                   for r in rs if r["end"] == end and not r.get("start")})


class Stage1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.run_json = load("run.json")

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 4, "oracle": 2})

    # ---------------------------------------------------------------- S1 시장성 지분증권
    @require_raw(RAW / "NVDA.companyfacts.json")
    def test_nvidia_marketable_equity_added(self):
        o = self.o["nvidia.net_cash.nc37"]
        comp = o["basis"]["components"]
        self.assertEqual(facts("NVDA", "EquitySecuritiesFvNi", "2026-07-26"), [42783000000.0])
        self.assertEqual(comp["marketable_equity_added"]["value"], 42783000000.0)
        self.assertEqual(comp["cash_and_marketable_securities"], 22443000000 + 34143000000 + 42783000000)
        self.assertEqual(o["value"], comp["cash_and_marketable_securities"] - comp["debt_incl_lease"])
        self.assertEqual(o["value"], 60509000000)
        p2 = self.res["nvidia"]["factors"]["F6"]["calc"]["parameters"]["P2"]
        self.assertEqual(p2["inputs"]["net_cash"], 60509000000)
        self.assertAlmostEqual(p2["value"], 17.6898, places=4)
        self.assertEqual((p2["score"], p2["band"]), (-1, "8~20"))       # 밴드 불변
        self.assertEqual(self.res["nvidia"]["factors"]["F6"]["score"], -2)

    @require_raw(RAW / "META.companyfacts.json", RAW / "GOOGL.companyfacts.json")
    def test_meta_and_alphabet_were_already_inside_the_line(self):
        """더하면 이중 계상이다 — 지시서 수치가 산술로는 맞지만 사실이 아니다."""
        self.assertEqual(facts("META", "EquitySecuritiesFvNi", "2026-06-30"), [3543000000.0])
        afs = facts("META", "DebtSecuritiesAvailableForSaleExcludingAccruedInterest", "2026-06-30")[0]
        mkt = facts("META", "MarketableSecuritiesCurrent", "2026-06-30")[0]
        self.assertEqual(afs + 3543000000.0, mkt)                       # 71,255 + 3,543 = 74,798
        self.assertEqual(self.o["meta.net_cash.nc37"]["basis"]["components"]["cash_and_marketable_securities"],
                         15462000000 + 74798000000)
        p2 = self.res["meta"]["factors"]["F6"]["calc"]["parameters"]["P2"]
        self.assertAlmostEqual(p2["value"], 6.7123, places=4)
        # alphabet 은 기준일 사실이 아예 없다(최신 2025-09-30).
        self.assertEqual(facts("GOOGL", "EquitySecuritiesFvNi", "2026-06-30"), [])
        self.assertEqual(facts("GOOGL", "EquitySecuritiesFvNi", "2025-09-30"), [7093000000.0])

    def test_sweep_covers_every_company_with_one_yardstick(self):
        sweep = self.o["nvidia.net_cash.nc37"]["basis"]["marketable_equity_sweep"]
        self.assertEqual(len(sweep["companies"]), 12)
        verdicts = {cid: v["verdict"] for cid, v in sweep["companies"].items()}
        self.assertEqual(verdicts["nvidia"], "added")
        self.assertEqual(verdicts["meta"], "already_included")
        self.assertEqual(verdicts["alphabet"], "already_included")
        self.assertEqual(verdicts["alibaba"], "already_included")
        self.assertEqual(verdicts["oracle"], "excluded_mixed")
        self.assertEqual(verdicts["tesla"], "crypto_excluded")
        self.assertEqual({cid for cid, v in verdicts.items() if v == "none"},
                         {"apple", "amazon", "microsoft", "palantir", "spacex-xai", "tsmc"})
        self.assertEqual(sum(v["delta"] for v in sweep["companies"].values()), 42783000000.0)
        self.assertIn("이중 계상", sweep["meta_note"])
        # 같은 기록이 세 관측에 같은 내용으로 있다.
        for oid in ("meta.net_cash.nc37", "oracle.net_cash.nc37"):
            self.assertEqual(self.o[oid]["basis"]["marketable_equity_sweep"], sweep)

    @require_raw(RAW / "ORCL.companyfacts.json")
    def test_oracle_mixed_tag_stays_out(self):
        self.assertEqual(facts("ORCL", "EquitySecuritiesFvNiAndWithoutReadilyDeterminableFairValue", "2026-05-31"),
                         [2300000000.0])
        self.assertEqual(facts("ORCL", "EquitySecuritiesFvNi", "2026-05-31"), [])   # 시장성만 가리키는 태그가 없다
        sweep = self.o["oracle.net_cash.nc37"]["basis"]["marketable_equity_sweep"]
        self.assertIn("혼합 줄", sweep["companies"]["oracle"]["why"])
        self.assertEqual(self.o["oracle.net_cash.nc37"]["basis"]["components"]["cash_and_marketable_securities"],
                         31894000000.0)
        self.assertAlmostEqual(self.res["oracle"]["factors"]["F6"]["calc"]["parameters"]["P2"]["value"], 8.5995, places=4)

    @require_raw(RAW / "TSLA.companyfacts.json")
    def test_tesla_crypto_gets_the_same_judgment_as_spacex(self):
        self.assertEqual(facts("TSLA", "CryptoAssetFairValueNoncurrent", "2026-06-30"), [674000000.0])
        tesla = self.o["tesla.net_cash.nc37"]["basis"]["components"]["excluded_nonmarketable_present"]
        spacex = self.o["spacex-xai.net_cash.nc37"]["basis"]["components"]["excluded_nonmarketable_present"]
        for ex in (tesla["us-gaap:CryptoAssetFairValueNoncurrent"], spacex["us-gaap:CryptoAssetFairValueNoncurrent"]):
            self.assertIn("암호자산은 유가증권이 아니다", ex["why"])
        self.assertEqual(self.o["tesla.net_cash.nc37"]["value"], 27444000000.0)     # 값 불변

    # ---------------------------------------------------------------- S2 oracle 태그 오독
    @require_raw(RAW / "ORCL.companyfacts.json")
    def test_undiscounted_excess_is_imputed_interest_not_a_commitment(self):
        """보존 원자료가 관계를 준다 — 지급총액 − 인식부채 = 할인차금."""
        pay = facts("ORCL", "LesseeOperatingLeaseLiabilityPaymentsDue", "2026-05-31")[0]
        liab = facts("ORCL", "OperatingLeaseLiability", "2026-05-31")[0]
        excess = facts("ORCL", "LesseeOperatingLeaseLiabilityUndiscountedExcessAmount", "2026-05-31")[0]
        self.assertEqual(pay - liab, excess)                                        # 41,867 − 30,190 = 11,677
        fin = (facts("ORCL", "FinanceLeaseLiabilityPaymentsDue", "2026-05-31")[0]
               - facts("ORCL", "FinanceLeaseLiability", "2026-05-31")[0])
        self.assertEqual(fin, facts("ORCL", "FinanceLeaseLiabilityUndiscountedExcessAmount", "2026-05-31")[0])
        b = self.o["oracle.offbalance_B.v15"]["basis"]
        what = {a["tag"]: a["what"] for a in b["disclosed_alternatives"]}
        excess_what = what["us-gaap:LesseeOperatingLeaseLiabilityUndiscountedExcessAmount"]
        self.assertIn("내재이자(할인차금)", excess_what)
        self.assertIn("B종(미개시 약정) 후보가 아니다", excess_what)
        self.assertIn("고 적은 것은 개념 이름의 `Excess` 를 미개시분으로 잘못 읽은 것이다", excess_what)   # 옛 문장은 인용으로만 남는다
        c26 = {d["id"]: d for d in RULES.payload["decisions"]}["C-26"]
        self.assertIn("내재이자(할인차금)", c26["recommendation"])
        self.assertIn("구매 약정", c26["recommendation"])
        self.assertIn("250,000M 의 출처는 여전히 확인되지 않는다", b["alternatives_caveat"])
        self.assertEqual(self.res["oracle"]["factors"]["F9"]["score"], -3)

    # ---------------------------------------------------------------- S3 G1 기간 방어
    def test_g1_fallback_refuses_mixed_periods(self):
        """12개월 손익을 한 분기 매출로 나누지 않는다 — 합성 입력으로 고정한다."""
        base = [obs("operating_income_ttm", -3732.0, basis={"period_basis": "ttm"}),
                obs("revenue_ttm", 7814.0, basis={"period_basis": "quarterly_yoy"}),
                obs("cash", 93522.0), obs("fcf_ttm", -32348.0)]
        gi = {"fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no",
              "direction_A": "unknown", "direction_B": "unknown", "coverage_comparable": "unknown",
              "operating_result_reviewed": "unknown"}
        judgments = JudgmentLookup([{"judgment_id": "acme.F9", "company_id": "acme", "factor": "F9",
                                     "kind": "gate_inputs", "score": None, "inputs": gi, "evidence": [],
                                     "counter_evidence": [], "note": None, "reviewer": "t",
                                     "reviewed_at": "2026-09-16", "status": "new", "source_ids": []}])
        r = compute_f9(company(), ObsLookup(base), judgments, RULES, run())
        skipped = next(p for p in r["calc"]["path"] if p.get("result") == "not_computed")
        self.assertEqual((skipped["operating_income_period_basis"], skipped["revenue_period_basis"]),
                         ("ttm", "quarterly_yoy"))
        self.assertTrue(any("기간 기준" in w for w in r["warnings"]))
        self.assertIsNone(r["score"])                                   # 비율을 만들지 않으니 G1 이 서지 않는다

    def test_g1_fallback_reads_the_full_year_revenue_metric(self):
        base = [obs("operating_income_ttm", -3732.0, basis={"period_basis": "ttm"}),
                obs("revenue_ttm", 7814.0, basis={"period_basis": "quarterly_yoy"}),
                obs("revenue_ttm_full", 23044.0, basis={"period_basis": "ttm"}),
                obs("cash", 93522.0), obs("fcf_ttm", -32348.0)]
        gi = {"fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no",
              "direction_A": "unknown", "direction_B": "unknown", "coverage_comparable": "unknown",
              "operating_result_reviewed": "unknown"}
        judgments = JudgmentLookup([{"judgment_id": "acme.F9", "company_id": "acme", "factor": "F9",
                                     "kind": "gate_inputs", "score": None, "inputs": gi, "evidence": [],
                                     "counter_evidence": [], "note": None, "reviewer": "t",
                                     "reviewed_at": "2026-09-16", "status": "new", "source_ids": []}])
        r = compute_f9(company(), ObsLookup(base), judgments, RULES, run())
        g1 = next(p for p in r["calc"]["path"] if p["gate"] == "G1")
        self.assertAlmostEqual(g1["operating_margin_ttm"], -3732.0 / 23044.0, places=9)
        self.assertEqual(g1["result"], "fail")                          # 12개월끼리 나눈 진짜 손실률이다

    def test_live_run_still_uses_the_stored_margin(self):
        """오늘은 이 경로를 타지 않는다 — 고친 것이 현재 점수를 건드리지 않았음을 확인한다."""
        g1 = next(p for p in self.res["spacex-xai"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G1")
        self.assertAlmostEqual(g1["operating_margin_ttm"], -0.161951, places=6)
        self.assertEqual(self.res["spacex-xai"]["factors"]["F9"]["score"], -3)

    # ---------------------------------------------------------------- S4 기록·표시
    def test_diagnostic_path_carries_the_same_keys_as_the_main_path(self):
        g3 = next(p for p in self.res["spacex-xai"]["factors"]["F9"]["calc"]["path"]
                  if p["gate"] == "G3" and p.get("mode") == "diagnostic")
        for key in ("runway_years", "buffer", "annual_burn", "step", "score", "boundary"):
            self.assertIn(key, g3)
        self.assertEqual(g3["buffer"], 93522000000.0 + 4355000000.0)
        g4 = next(p for p in self.res["spacex-xai"]["factors"]["F9"]["calc"]["path"]
                  if p["gate"] == "G4" and p.get("mode") == "diagnostic")
        self.assertIn("step", g4)                                       # 떼고 저장하지 않는다

    def test_nonop_current_block_describes_current_behaviour(self):
        cond = next(c for c in RULES.payload["policies"]["f6"]["p4"]["conditions"] if c["id"] == "nonop_share")
        cur = cond["stored_vs_recomputed"]["current"]
        self.assertIn("0.02", cur["which_is_used"])
        self.assertIn("pretax_income_ttm", cur["which_is_used"])
        self.assertIn("산출 자체를 하지 않는다", cur["where_it_does_decide"])
        self.assertIn("0.6124", cur["table_label_note"])
        code = (SRC / "calc_f6_params.py").read_text(encoding="utf-8")
        self.assertIn("abs(stored - value) > 0.02", code)
        # 선언과 결과가 같은지 결과에서 본다.
        sole = {c["company_id"]: (c["factors"]["F6"].get("calc") or {}).get("p4", {}).get("demotion_sole_cause")
                for c in self.results["companies"]}
        self.assertEqual({cid for cid, v in sole.items() if v == "nonop_share"}, {"amazon", "alphabet"})
        self.assertIsNone(sole["spacex-xai"])
        self.assertIsNone(self.res["spacex-xai"]["factors"]["F6"]["calc"]["p4"]["nonop_share"])

    def test_revenue_coalesce_has_a_consumer(self):
        rc = RULES.payload["policies"]["f6"]["revenue_coalesce"]
        self.assertIn("소비자를 붙였다", rc["consumer"])
        code = (ROOT / "validation" / "f6-spec-18" / "collect_ttm.py").read_text(encoding="utf-8")
        self.assertIn("revenue_coalesce", code)
        self.assertIn("_revenue_tags_from_rules", code)
        self.assertNotIn("\nREVENUE_TAGS = [\n", code)                  # 상수로 따로 적어 두지 않는다
        fallback = re.search(r"_REVENUE_TAGS_FALLBACK = \[(.*?)\]", code, re.S).group(1)
        for tag in rc["priority"]:
            self.assertIn(tag.split(":", 1)[1], fallback)

    def test_c24_choice_is_read_from_the_run(self):
        calc = self.res["spacex-xai"]["factors"]["F6"]["calc"]
        self.assertEqual(calc["c24_choice"]["choice"], "compute_p2_when_inputs_exist")
        self.assertEqual(calc["c24_choice"]["optional"], ["P2"])
        code = (SRC / "calc_f6_params.py").read_text(encoding="utf-8")
        self.assertIn('decision_choice(run, rules, "C-24")', code)
        c24 = {d["id"]: d for d in RULES.payload["decisions"]}["C-24"]
        self.assertEqual(c24["implementation_status"]["verdict"], "read_by_decision_choice")
        self.assertIn("정리 방식", c24["implementation_status"]["note"])

    def test_pending_rule_decisions_survive_an_empty_incomplete_list(self):
        class FakeRules:
            def decision(self, did):
                return {"summary": f"{did} 요약"}

        html = render_incomplete({"population": {"incomplete": []}, "pending_rule_decisions": ["C-26"]}, FakeRules())
        self.assertIn("필요한 규칙 결정", html)
        self.assertIn("C-26", html)
        self.assertEqual(render_incomplete({"population": {"incomplete": []}, "pending_rule_decisions": []}, FakeRules()), "")
        self.assertEqual(OBS_STATUS_LABELS["unavailable"], "산출 불가")
        self.assertEqual(STATUS_LABEL["unavailable"], "산출 불가")


if __name__ == "__main__":
    unittest.main()
