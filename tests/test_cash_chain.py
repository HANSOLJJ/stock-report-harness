# 현금 연결표(규칙 v2.1 2-E, 점수 없음)의 계산·OCF − 설비투자 대조·규칙 선언 검증·렌더를 잠그는 테스트
from __future__ import annotations

import copy
import dataclasses
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.cash_chain import cash_chain_rows, cash_chain_spec, fcf_check  # noqa: E402
from scorecard.inputs import ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

V20, V21 = load_rules("v2.0"), load_rules("v2.1")
SPEC = cash_chain_spec(V21)
SLUG = "ai-scorecard-2026-10-recheck"


def ob(cid: str, metric: str, value: float, *, status: str = "verified", end: str = "2026-06-30",
       as_of: str | None = None, period: bool = True, oid: str | None = None) -> dict:
    o = {"observation_id": oid or f"{cid}.{metric}.{status}.{end}", "company_id": cid, "metric": metric, "value": value,
         "unit": "count" if metric == "shares_diluted" else "USD", "as_of": as_of or end, "kind": "actual",
         "source_id": "SRC-T", "status": status}
    if period and metric != "shares_diluted":
        o["period"] = {"start": "2025-07-01", "end": end}
    return o


def full(cid: str = "acme", **override) -> list[dict]:
    vals = {"revenue_ttm": 1000.0, "operating_income_ttm": 300.0, "ocf_ttm": 400.0, "capex_ttm": 150.0, "fcf_ttm": 250.0,
            "sbc_ttm": 50.0, "shares_diluted": 100.0, **override}
    return [ob(cid, m, v) for m, v in vals.items() if v is not None]


def row(observations: list[dict]) -> dict:
    return cash_chain_rows(observations, [{"company_id": "acme", "display_name": "Acme"}], SPEC)[0]


class SpecTest(unittest.TestCase):
    def test_declared_only_in_v21_and_unscored(self):
        self.assertIsNone(cash_chain_spec(V20))
        self.assertIs(SPEC["scored"], False)

    def test_rules_validator_rejects_scored_or_bad_tolerance(self):
        base = json.loads((ROOT / "scorecard" / "rules" / "v2.1.json").read_text(encoding="utf-8"))
        for key, value in (("scored", True), ("fcf_check_tolerance", 0), ("fcf_check_tolerance", 0.5)):
            with self.subTest(key=key, value=value):
                bad = copy.deepcopy(base)
                bad["policies"]["diagnostics"]["cash_chain"][key] = value
                with self.assertRaises(SchemaError):
                    validate_rules(bad)
        validate_rules(base)


class CheckTest(unittest.TestCase):
    ENDS = {"ocf_ttm": "2026-06-30", "capex_ttm": "2026-06-30", "fcf_ttm": "2026-06-30"}

    def check(self, ocf, capex, fcf, ends=None):
        return fcf_check({"ocf_ttm": ocf, "capex_ttm": capex, "fcf_ttm": fcf}, ends or self.ENDS, 0.01)

    def test_match_boundary_and_mismatch(self):
        self.assertEqual(self.check(400, 150, 250)["status"], "match")
        self.assertEqual(self.check(402.5, 150, 250)["status"], "match")       # 차이 2.5 = FCF 의 1% — 경계는 일치
        r = self.check(403, 150, 250)
        self.assertEqual((r["status"], r["diff"], r["derived"]), ("mismatch", 3, 253))

    def test_period_and_missing(self):
        self.assertEqual(self.check(400, 150, 250, {**self.ENDS, "fcf_ttm": "2026-08-31"})["status"], "period_mismatch")
        self.assertEqual(self.check(400, 150, 250, {**self.ENDS, "capex_ttm": None}),
                         {"status": "period_unknown", "missing": ["capex_ttm"]})
        self.assertEqual(self.check(None, 150, 250), {"status": "unavailable", "missing": ["ocf_ttm"]})


class RowsTest(unittest.TestCase):
    def test_per_share_before_and_after_sbc(self):
        r = row(full())
        self.assertEqual((r["fcf_per_share"], r["fcf_less_sbc_per_share"], r["check"]["status"]), (2.5, 2.0, "match"))

    def test_check_follows_capex_input(self):
        """입력을 바꾸면 판정이 따라오는지 본다."""
        self.assertEqual(row(full(capex_ttm=170.0))["check"]["status"], "mismatch")

    def test_missing_values_stay_none(self):
        r = row(full(sbc_ttm=None, ocf_ttm=None))
        self.assertIsNone(r["values"]["sbc_ttm"])
        self.assertEqual(r["fcf_per_share"], 2.5)
        self.assertIsNone(r["fcf_less_sbc_per_share"])
        self.assertEqual(r["check"]["status"], "unavailable")
        self.assertIsNone(row(full(shares_diluted=0.0))["fcf_per_share"])     # 0 으로 나누지 않는다

    def test_periodless_legacy_flow_is_not_dated_by_as_of(self):
        obs = [o for o in full() if o["metric"] != "capex_ttm"] + [ob("acme", "capex_ttm", 150.0, status="legacy_unverified",
                                                                      as_of="2026-09-02", period=False)]
        r = row(obs)
        self.assertIsNone(r["ends"]["capex_ttm"])
        self.assertEqual(r["check"]["status"], "period_unknown")

    def test_uses_the_same_fcf_observation_as_f9(self):
        """⑨(calc_f9)는 ObsLookup.number 로 fcf_ttm 을 읽는다. 연결표도 같은 관측을 고른다 — verified 가 더 최신 옛 관측을 이긴다."""
        obs = full() + [ob("acme", "fcf_ttm", 999.0, status="legacy_unverified", end="2026-09-02", oid="acme.fcf_ttm.legacy")]
        self.assertEqual(row(obs)["values"]["fcf_ttm"], ObsLookup(obs).number("acme", "fcf_ttm")[0])
        self.assertEqual(row(obs)["values"]["fcf_ttm"], 250.0)


@unittest.skipUnless((ROOT / "output" / SLUG / "results.json").is_file(), "recheck 실행 없음")
class RenderTest(unittest.TestCase):
    """v2.1 규칙이면 초안·HTML ⑨ 원자료 뒤에 연결표가 붙고, 진단 선언이 없는 규칙이면 붙지 않는다."""

    @classmethod
    def setUpClass(cls):
        from scorecard.engine import load_context
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((ROOT / "output" / SLUG / "results.json").read_text(encoding="utf-8"))

    def test_draft_and_html_sections(self):
        from scorecard.render_html import render_raw_tables
        from scorecard.render_md import _raw_tables
        v21 = dataclasses.replace(self.ctx, rules=V21)
        md = "\n".join(_raw_tables(v21, self.results))
        self.assertIn("### 현금 연결표 — 점수 없음", md)
        self.assertIn("| 기업 | 매출 | 영업이익 | 영업현금흐름 |", md)
        self.assertIn("AI 가 이 현금 가운데 얼마를 만들었는지는 공시로 가를 수 없어 비워 둔다", md)
        self.assertIn("<h3>현금 연결표 — 점수 없음</h3>", render_raw_tables(v21, self.results))
        self.assertNotIn("현금 연결표", "\n".join(_raw_tables(self.ctx, self.results)))
        self.assertNotIn("현금 연결표", render_raw_tables(self.ctx, self.results))


if __name__ == "__main__":
    unittest.main()
