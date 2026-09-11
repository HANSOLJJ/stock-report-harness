# 관측 최신성 키(observed_at) 분리와 TTM 재작성 세대 조건 고정 테스트 (F6-REG-28)
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.inputs import ObsLookup, recency_key  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_observations  # noqa: E402

RAW = ROOT / "validation" / "f6-avail-15" / "_raw"


def company_map() -> dict:
    return {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}


def obs(**over) -> dict:
    item = {
        "observation_id": "alibaba.contracted_revenue.x", "company_id": "alibaba",
        "metric": "contracted_revenue", "value": None, "unit": "USD", "as_of": "2026-09-02",
        "kind": "actual", "source_id": "SRC-t", "status": "not_disclosed",
    }
    item.update(over)
    return item


class TestRecencyKeySeparated(unittest.TestCase):
    """`as_of` 는 자료 기준일이고 `observed_at` 은 관측 시점이다. 한 필드가 두 뜻을 갖지 않게 한다."""

    def test_falls_back_to_as_of(self):
        """승계 관측에는 observed_at 이 없다. 과거 실행의 선택 결과가 바뀌면 안 된다."""
        self.assertEqual(recency_key(obs()), "2026-09-02")

    def test_observed_at_wins_when_present(self):
        self.assertEqual(recency_key(obs(as_of="2026-03-31", observed_at="2026-09-11")), "2026-09-11")

    def test_value_less_replacement_beats_carried(self):
        """**이 과제가 막는 바로 그 사고다.**

        값이 없는 교체 관측은 status 등급이 0 이라 승계 관측(같은 0)을 최신성으로만 이겨야 한다.
        `as_of` 에 공시 기준일(더 이른 날짜)을 적으면 승계가 이기고, 새로 붙인 `missing_type` 이
        엔진에 닿지 않는다. OBS-REG-25 에서 실제로 겪었다.
        """
        carried = obs(observation_id="alibaba.contracted_revenue.v15", as_of="2026-09-02", raw="—")
        replacement = obs(observation_id="alibaba.contracted_revenue.obsreg25",
                          as_of="2026-03-31", observed_at="2026-09-11",
                          missing_type="not_disclosed_confirmed")
        for order in ([carried, replacement], [replacement, carried]):
            picked = ObsLookup(order).get("alibaba", "contracted_revenue")
            self.assertEqual(picked["observation_id"], "alibaba.contracted_revenue.obsreg25",
                             "값 없는 교체 관측이 승계를 이겨야 한다 — 파일 순서와도 무관해야 한다")
            self.assertEqual(picked.get("missing_type"), "not_disclosed_confirmed")

    def test_regression_if_observed_at_removed(self):
        """observed_at 을 지우면 다시 승계가 이긴다. 검사가 살아 있는지 본다."""
        carried = obs(observation_id="carried", as_of="2026-09-02")
        replacement = obs(observation_id="replacement", as_of="2026-03-31")   # observed_at 없음
        picked = ObsLookup([carried, replacement]).get("alibaba", "contracted_revenue")
        self.assertEqual(picked["observation_id"], "carried")

    def test_verified_still_beats_by_status_first(self):
        """등급이 최신성보다 먼저다. 값 있는 새 관측은 날짜와 무관하게 승계를 이긴다."""
        carried = obs(observation_id="carried", value=1.0, status="legacy_unverified", as_of="2026-09-02")
        fresh = obs(observation_id="fresh", value=2.0, status="verified",
                    as_of="2026-06-30", observed_at="2026-09-11")
        self.assertEqual(ObsLookup([carried, fresh]).get("alibaba", "contracted_revenue")["observation_id"],
                         "fresh")

    def test_schema_accepts_and_orders_dates(self):
        payload = {"schema": "scorecard.observations/1", "run_id": "r",
                   "items": [obs(as_of="2026-06-30", observed_at="2026-09-11")]}
        validate_observations(payload, company_map(), "r")
        bad = {"schema": "scorecard.observations/1", "run_id": "r",
               "items": [obs(as_of="2026-09-11", observed_at="2026-06-30")]}
        with self.assertRaises(SchemaError):
            validate_observations(bad, company_map(), "r")

    def test_approved_run_has_no_observed_at(self):
        """승인된 실행은 건드리지 않았다."""
        items = load_json_strict(ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
                                 / "observations.json")["items"]
        self.assertFalse(any("observed_at" in o for o in items))


class TestRestatementGeneration(unittest.TestCase):
    """FY − (Q1+Q2+Q3) 복원은 네 성분이 같은 재작성 세대에서 올 때만 유효하다."""

    def setUp(self):
        self.rules = load_rules("v1.7")

    def test_declared_in_v17(self):
        spec = self.rules.f6_ttm_window().get("restatement_generation")
        self.assertIsNotNone(spec, "v1.7 ttm_window 에 restatement_generation 선언이 있어야 한다")
        self.assertEqual(spec["on_mixed"], "hold")
        self.assertIn("MSFT FY2016", spec["why"])

    def test_v15_and_v16_skip_the_check(self):
        """과거 규칙 파일을 깨지 않는다."""
        for version in ("v1.5", "v1.6"):
            out = load_rules(version).f6_q4_restatement_check([{"label": "FY", "tag": "X"}])
            self.assertFalse(out["checked"])
            self.assertTrue(out["ok"])

    def test_single_concept_passes(self):
        parts = [{"label": lbl, "tag": "RFCW", "restated": False} for lbl in ("FY", "Q1", "Q2", "Q3")]
        self.assertTrue(self.rules.f6_q4_restatement_check(parts, [])["ok"])

    def test_renamed_tag_with_agreeing_values_passes(self):
        """alphabet 사례. 이름이 다른 것과 기준이 다른 것은 다르다."""
        parts = [{"label": "FY", "tag": "RFCW", "restated": False}]
        parts += [{"label": f"Q{i}", "tag": "Revenues", "restated": False} for i in (1, 2, 3)]
        out = self.rules.f6_q4_restatement_check(parts, [])       # 겹침 불일치 없음
        self.assertTrue(out["ok"])
        self.assertIn("값이 일치", out["reason"])

    def test_restated_and_original_mixed_is_held(self):
        parts = [{"label": "FY", "tag": "RFCW", "restated": True}]
        parts += [{"label": f"Q{i}", "tag": "RFCW", "restated": False} for i in (1, 2, 3)]
        out = self.rules.f6_q4_restatement_check(parts, [])
        self.assertFalse(out["ok"])
        self.assertEqual(out["action"], "hold")

    def test_msft_fy2016_is_held_using_real_facts(self):
        """**원자료로 본다.** 손으로 지어낸 입력이 아니라 보존된 companyfacts 에서 뽑는다.

        FY2016 매출이 두 값으로 있다. ASC 606 재작성치 91,154 와 원래 ASC 605 공시 85,320 이다.
        재작성 FY 에서 원래 기준 9개월 누계를 빼면 Q4 가 26,448 로 나오는데 같은 세대끼리 빼면
        20,614 다. 5,834(28.3%) 차이이고 어느 분기에도 존재한 적 없는 값이다.
        """
        facts = json.loads((RAW / "MSFT.companyfacts.json").read_text(encoding="utf-8"))["facts"]["us-gaap"]

        def val(tag, start, end):
            for rows in facts[tag]["units"].values():
                for r in rows:
                    if r.get("start") == start and r.get("end") == end:
                        return r["val"]
            return None

        fy606 = val("RevenueFromContractWithCustomerExcludingAssessedTax", "2015-07-01", "2016-06-30")
        fy605 = val("SalesRevenueNet", "2015-07-01", "2016-06-30")
        ytd605 = val("SalesRevenueNet", "2015-07-01", "2016-03-31")
        self.assertEqual((fy606, fy605, ytd605), (91_154_000_000, 85_320_000_000, 64_706_000_000))
        self.assertEqual(fy606 - ytd605, 26_448_000_000)
        self.assertEqual(fy605 - ytd605, 20_614_000_000)

        conflicts = [{"period": "2015-07-01~2016-06-30",
                      "kept": {"tag": "RevenueFromContractWithCustomerExcludingAssessedTax", "val": fy606},
                      "other": {"tag": "SalesRevenueNet", "val": fy605},
                      "rel_diff": abs(fy606 - fy605) / fy606}]
        parts = [{"label": "FY2016", "tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                  "restated": False}]
        parts += [{"label": f"Q{i}", "tag": "SalesRevenueNet", "restated": False} for i in (1, 2, 3)]
        out = self.rules.f6_q4_restatement_check(parts, conflicts)
        self.assertFalse(out["ok"], "회계기준이 다른 두 수를 빼게 두면 안 된다")
        self.assertEqual(out["action"], "hold")
        self.assertIn("회계기준이 다르다", out["reason"])


class TestCollectorConsumesTheRule(unittest.TestCase):
    """선언에 소비자가 있어야 한다. 수집기가 실제로 이 검사를 부르는지 본다."""

    def test_collector_calls_the_check(self):
        src = (ROOT / "validation" / "f6-spec-18" / "collect_ttm.py").read_text(encoding="utf-8")
        self.assertIn("f6_q4_restatement_check", src)
        self.assertIn("overlap_conflicts", src)

    def test_collector_output_records_generation(self):
        """복원 근거에 세대 판정 결과가 남아야 한다."""
        derived = json.loads((ROOT / "validation" / "f6-spec-18" / "_derived"
                              / "ttm_inputs.json").read_text(encoding="utf-8"))
        checked = [(row["company_id"], rec) for row in derived
                   for ev in (row.get("evidence") or {}).values()
                   for rec in (ev.get("q4_reconstruction") or [])
                   if rec.get("restatement", {}).get("checked")]
        self.assertTrue(checked, "복원 근거에 restatement 판정이 하나도 없다 — 수집기를 다시 돌려야 한다")

    def test_tesla_fy2024_net_income_is_held(self):
        """**규칙이 실제로 잡은 두 번째 사례다.** 이것은 지어낸 입력이 아니다.

        TSLA 2024년 분기 순이익은 2025년 10-Q 들에서 재작성됐는데(9개월 누계 4,774 → 4,963)
        FY2024 7,091 은 두 10-K 에서 모두 그대로다. 재작성 분기를 원래 FY 에서 빼면 Q4 가
        2,128 로 나오고 같은 세대끼리 빼면 2,317 이다. **189백만, Q4 의 8.2% 차이다.**
        MSFT 처럼 회계기준이 바뀐 것이 아니라 같은 개념 안에서 값이 다시 매겨진 경우이고,
        그래서 세대 키에 `restated` 가 필요하다.
        """
        facts = json.loads((RAW / "TSLA.companyfacts.json").read_text(encoding="utf-8"))["facts"]["us-gaap"]
        rows = [r for units in facts["NetIncomeLoss"]["units"].values() for r in units]

        def vals(start, end):
            return sorted({r["val"] for r in rows if r.get("start") == start and r.get("end") == end})

        self.assertEqual(vals("2024-01-01", "2024-12-31"), [7_091_000_000], "FY2024 는 재작성되지 않았다")
        self.assertEqual(vals("2024-01-01", "2024-09-30"), [4_774_000_000, 4_963_000_000],
                         "9개월 누계는 재작성됐다")
        self.assertEqual(7_091_000_000 - 4_963_000_000, 2_128_000_000)   # 섞은 복원
        self.assertEqual(7_091_000_000 - 4_774_000_000, 2_317_000_000)   # 같은 세대 복원

        derived = json.loads((ROOT / "validation" / "f6-spec-18" / "_derived"
                              / "ttm_inputs.json").read_text(encoding="utf-8"))
        tsla = next(r for r in derived if r["company_id"] == "tesla")
        held = [rec for ev in (tsla.get("evidence") or {}).values()
                for rec in (ev.get("q4_reconstruction") or [])
                if rec.get("held") and rec["fy"].startswith("2024-01-01")]
        self.assertTrue(held, "수집기가 TSLA FY2024 순이익 Q4 복원을 보류해야 한다")
        self.assertIn("재작성된 성분과 아닌 성분이 섞였다", held[0]["restatement"]["reason"])
        self.assertIsNone(held[0]["q4_derived"], "보류했으면 값을 만들지 않는다")
