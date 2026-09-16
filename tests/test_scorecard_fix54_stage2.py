# FIX-54 2단계 — 3차 리뷰 A 반영(openai F4 긴장 · Spectrum 구성 · 결측 라벨 · 설명 정정 · 1단계에서 남긴 셋)을 고정한다
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
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Stage2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.res = {c["company_id"]: c for c in load("results.json")["companies"]}
        ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.ctx = ctx
        cls.md = render_draft(ctx, load("results.json"), base, triggers)

    def test_totals_same_as_stage1(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "spacex-xai": 11, "tsmc": 10, "anthropic": 10,
                          "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5, "openai": 2, "oracle": 2})

    # 1. openai F4
    def test_openai_f4_tension_and_marks(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA3-01"]
        self.assertEqual((t["judgment_ids"], t["recheck_at"], t["related_tensions"]), (["openai.F4"], "2026-11", ["TEN-RA-02"]))
        self.assertIn("하향 가능(4 → 3)", t["direction"])
        ev = self.j["openai.F4"]["evidence"]
        self.assertIn("(발표 — OpenAI)", ev[0])
        self.assertTrue(ev[2].startswith("(계획) 배치 계획"))
        self.assertEqual((self.j["openai.F4"]["score"], self.j["openai.F4"]["status"]), (4, "carried"))
        self.assertIn("OpenAI 공개 InferenceX 결과(발표 — OpenAI)에서", self.md)

    # 2. Spectrum
    def test_spectrum_note_corrected_value_kept(self):
        o = self.o["spacex-xai.offbalance_B.obsreg25"]
        self.assertEqual(o["value"], 29582000000.0)
        comp = o["basis"]["components"][1]
        self.assertNotIn("미공시", comp["note"])
        self.assertIn("분해가 미공시다", comp["note_superseded"]["text"])
        sp = o["basis"]["spectrum"]
        self.assertIn("approximately $11.1 billion in equity", sp["consideration_quote"])
        self.assertIn("정하지 않는다", sp["b_type_definition_check"]["finding"])
        self.assertTrue(all(v["coverage"] >= 1 for k, v in sp["sensitivity"].items() if isinstance(v, dict) and "coverage" in v))
        g4 = next(p for p in self.res["spacex-xai"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G4")
        self.assertEqual(g4["mode"], "diagnostic")
        self.assertEqual(self.res["spacex-xai"]["factors"]["F9"]["score"], -3)
        self.assertIn("~~판정 근거 2 — 무조건 약정 중 Spectrum 분은 현금과 Class A 보통주 혼합 지급이고 분해가 미공시다~~", self.md)
        self.assertIn("총 약 $19.6B = 주식 약 $11.1B", self.md)

    # 3. 결측 라벨
    def test_private_labels_kept_with_scope(self):
        for cid in ("anthropic", "openai"):
            for m in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
                o = self.o[f"{cid}.{m}.priv31"]
                with self.subTest(oid=o["observation_id"]):
                    self.assertEqual(o["missing_type"], "not_disclosed_confirmed")
                    self.assertIn("구조적 미공시", o["basis"]["label_meaning"])
                    self.assertIn("ffaf318:", o["basis"]["checked_scope"]["preserved_release"])
        self.assertEqual(self.res["anthropic"]["factors"]["F9"]["score"], -2)

    def test_lease_labels_match_data_scope(self):
        for cid in ("apple", "palantir"):
            o = self.o[f"{cid}.lease_liabilities.nc37"]
            self.assertEqual(o["missing_type"], "unverified")
            self.assertEqual(o["basis"]["label_correction"]["was"], "not_disclosed_confirmed")
        self.assertIn("2020-06-27 까지는 분기말 사실도", self.o["apple.lease_liabilities.nc37"]["basis"]["why"])

    def test_legacy_null_relabels(self):
        want = {"spacex-xai.ttm_per.v15": ("not_applicable", "not_applicable"), "anthropic.runway_years.v15": ("not_disclosed", "indeterminate"),
                "openai.runway_years.v15": ("not_disclosed", "indeterminate"), "palantir.net_borrowing_ttm.v15": ("not_disclosed", "unverified"),
                "alibaba.offbalance_B.v15": ("not_disclosed", "unverified"), "spacex-xai.offbalance_B.v15": ("not_disclosed", "unverified")}
        for oid, (status, mtype) in want.items():
            with self.subTest(oid=oid):
                self.assertEqual((self.o[oid]["status"], self.o[oid]["missing_type"]), (status, mtype))

    # 4. 설명 정정
    def test_descriptions(self):
        self.assertIn("과거에 이행한 의무에서 당기에 인식한 매출", self.o["alibaba.contracted_revenue.obsreg25"]["basis"]["limit"])
        row = next(r for r in self.o["alibaba.net_cash.nc37"]["basis"]["components"]["rows"] if r["label"] == "Debt securities and loan investments")
        for part in ("RMB2,989M", "RMB4,764M", "RMB5,845M", "완전한 시장성 분할은 없다"):
            self.assertIn(part, row["why"])
        tsmc = self.o["tsmc.revenue_ttm_prior.f6reg28"]["basis"]["why_not_filed_usd"]
        self.assertIn("88,268.0M", tsmc)
        self.assertNotIn("70,598.8", tsmc)
        self.assertIn("TTM 아님", self.o["spacex-xai.revenue_ttm_prior.f6reg28"]["basis"]["period_label"])

    # 5. 1단계에서 남긴 셋 + amazon 지연인출
    def test_stage1_leftovers(self):
        self.assertNotIn("선택에 따라 런웨이가 달라질 수 있다", self.md)
        self.assertIn("include_v15 를 골라도 경고 문구만 바뀌고 G3 산술은 같다", self.md)
        self.assertIn("~~완충 약 $41B로 확대~~ (superseded [FIX-54 2단계]", self.md)
        cur = next(c for c in RULES.payload["policies"]["f6"]["p4"]["conditions"] if c["id"] == "nonop_share")["stored_vs_recomputed"]["current"]
        self.assertEqual(cur["formula"], "(pretax_income_ttm - operating_income_ttm) / pretax_income_ttm")
        self.assertAlmostEqual(cur["table"]["alibaba"][1], 0.6124, places=4)
        self.assertIn("옛 순이익 기준 산식", cur["note"])
        self.assertIn("Term Loan (unsecured delayed draw) $17.5B 는 2026-09-30 까지 인출하지 않으면 미인출분이 소멸한다 — 기준일(2026-09-02) 28일 뒤", self.md)
        # 2026-09-16 FIX-55 2단계: tesla 5,000M 이 등록돼 여신 줄이 넷이 됐다(alibaba·spacex-xai·amazon·tesla).
        self.assertEqual(len(rc.credit_lines(self.ctx, load("results.json"))), 4)


if __name__ == "__main__":
    unittest.main()
