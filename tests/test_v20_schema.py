# 규칙 v2.0 판단 스키마: ① lockin 입력, ② 독립 측정·세대 격차 개월, ③ 지표 단계, reconfirmed 모양, judgment_kinds(새 판단만), edit kind·입력란·관측 지표를 잠근다
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import COMPANIES_PATH  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import (JUDGMENT_INPUT_CHOICES, METRICS, PERIOD_REQUIRED_METRICS, SchemaError,  # noqa: E402
                              judgment_edit_kind, load_json_strict, validate_companies, validate_cross_refs,
                              validate_judgments, validate_observations, validate_rules)

COMPANIES = validate_companies(load_json_strict(COMPANIES_PATH))
V20 = load_rules("v2.0")
V19 = load_rules("v1.9")

LOCKIN = {"channel_consumer": "no", "channel_work": "yes", "channel_trade": "no", "loop": "pass", "switching": "partial",
          "substitutes": "pass", "pricing": "unknown", "durability_discount": "no", "ai_monetized_in_channel": "partial"}
PATHS = {"performance_leap": "partial", "paradigm_adaptation": "pass", "standard_capture": "fail", "top_rank": "unknown"}
CRITERIA = {"imitation": "pass", "revenue_model": "pass", "acceleration": "partial", "door_closed": "unknown",
            "acceleration_tier": "b", "acceleration_growth_rates": [0.21, 0.34]}


def item(factor: str, kind: str, inputs: dict | None = None, *, score=None, status: str = "new", cid: str = "nvidia", **extra) -> dict:
    out = {"judgment_id": f"{cid}.{factor}", "company_id": cid, "factor": factor, "kind": kind, "score": score,
           "inputs": copy.deepcopy(inputs) if inputs is not None else {}, "evidence": ["시험 근거"], "reviewer": "tester",
           "reviewed_at": "2026-10-08", "status": status}
    if status == "carried":
        out["carried_from"] = "run:ai-scorecard-2026-10-rescore"
    out.update(extra)
    return out


def validate(*items: dict, rules=V20) -> list[dict]:
    return validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": list(items)}, COMPANIES, rules.payload)


class LockinInputTest(unittest.TestCase):
    def test_valid_lockin_passes(self):
        validate(item("F1", "lockin", LOCKIN))

    def test_allowed_values(self):
        cases = (("channel_work", "unknown"), ("loop", "yes"), ("pricing", "maybe"), ("durability_discount", "partial"),
                 ("ai_monetized_in_channel", "pass"))
        for key, value in cases:
            with self.subTest(key=key):
                with self.assertRaisesRegex(SchemaError, key):
                    validate(item("F1", "lockin", {**LOCKIN, key: value}))

    def test_required_keys(self):
        for key in LOCKIN:
            with self.subTest(key=key):
                bad = {k: v for k, v in LOCKIN.items() if k != key}
                with self.assertRaisesRegex(SchemaError, "필수 키 누락"):
                    validate(item("F1", "lockin", bad))
        with self.assertRaisesRegex(SchemaError, "알 수 없는 키"):
            validate(item("F1", "lockin", {**LOCKIN, "network_effect": "pass"}))

    def test_pricing_pass_needs_eight_quarters(self):
        with self.assertRaisesRegex(SchemaError, "pricing_sustained_quarters"):
            validate(item("F1", "lockin", {**LOCKIN, "pricing": "pass"}))
        with self.assertRaisesRegex(SchemaError, "8분기 이상"):
            validate(item("F1", "lockin", {**LOCKIN, "pricing": "pass", "pricing_sustained_quarters": 7}))
        validate(item("F1", "lockin", {**LOCKIN, "pricing": "pass", "pricing_sustained_quarters": 8}))
        validate(item("F1", "lockin", {**LOCKIN, "pricing": "partial", "pricing_sustained_quarters": 3}))

    def test_quarters_must_be_non_negative_int(self):
        for bad in (-1, 2.5, True, "8"):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(SchemaError, "pricing_sustained_quarters"):
                    validate(item("F1", "lockin", {**LOCKIN, "pricing_sustained_quarters": bad}))

    def test_v19_accepts_lockin_kind_but_not_the_rule_check(self):
        """F1 허용 kind 를 넓혔다. 규칙이 사다리를 모르는 v1.9 는 분기 임계를 보지 않는다."""
        validate(item("F1", "lockin", {**LOCKIN, "pricing": "pass"}), rules=V19)


class JudgmentKindsTest(unittest.TestCase):
    """규칙의 judgment_kinds 는 새 판단에만 건다. 이어받은 판단은 옛 kind 로 읽혀야 재실행이 하나씩 바꿀 수 있다."""

    def test_new_score_kinds_are_refused_in_v20(self):
        for factor, score in (("F1", 3), ("F2", 4), ("F7", -2)):
            with self.subTest(factor=factor):
                with self.assertRaisesRegex(SchemaError, "새 판단은 kind"):
                    validate(item(factor, "score", score=score))

    def test_carried_score_kinds_still_read_in_v20(self):
        validate(item("F1", "score", score=2, status="carried"),
                 item("F2", "score", score=5, status="carried"),
                 item("F7", "score", score=-2, status="carried"))

    def test_v19_keeps_old_kinds(self):
        validate(item("F1", "score", score=3), item("F2", "score", score=5, status="carried"), rules=V19)

    def test_rules_must_declare_known_kinds(self):
        payload = copy.deepcopy(V20.payload)
        payload["factors"]["F2"]["judgment_kinds"] = ["lockin"]
        with self.assertRaisesRegex(SchemaError, "judgment_kinds"):
            validate_rules(payload)


class PathsInputTest(unittest.TestCase):
    def test_leap_pass_needs_independence_flag(self):
        with self.assertRaisesRegex(SchemaError, "leap_independent"):
            validate(item("F2", "paths", {**PATHS, "performance_leap": "pass", "generation_gap": "no"}))
        validate(item("F2", "paths", {**PATHS, "performance_leap": "pass", "generation_gap": "no", "leap_independent": "no"}))

    def test_generation_gap_yes_needs_months(self):
        base = {**PATHS, "performance_leap": "pass", "leap_independent": "yes", "generation_gap": "yes"}
        with self.assertRaisesRegex(SchemaError, "generation_gap_months"):
            validate(item("F2", "paths", base))
        validate(item("F2", "paths", {**base, "generation_gap_months": 7}))
        for bad in (-1, 3.5, True):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(SchemaError, "generation_gap_months"):
                    validate(item("F2", "paths", {**base, "generation_gap_months": bad}))

    def test_independence_value_domain(self):
        with self.assertRaisesRegex(SchemaError, "leap_independent"):
            validate(item("F2", "paths", {**PATHS, "leap_independent": "vendor"}))

    def test_v19_does_not_require_new_keys(self):
        validate(item("F2", "paths", {**PATHS, "performance_leap": "pass", "generation_gap": "yes"}), rules=V19)


class CriteriaInputTest(unittest.TestCase):
    def test_valid_tier_b(self):
        validate(item("F3", "criteria", CRITERIA))

    def test_tier_required_in_v20(self):
        bad = {k: v for k, v in CRITERIA.items() if k != "acceleration_tier"}
        with self.assertRaisesRegex(SchemaError, "acceleration_tier"):
            validate(item("F3", "criteria", bad))

    def test_tier_c_caps_at_partial(self):
        with self.assertRaisesRegex(SchemaError, "최대 partial"):
            validate(item("F3", "criteria", {**CRITERIA, "acceleration_tier": "c", "acceleration": "pass"}))
        validate(item("F3", "criteria", {**CRITERIA, "acceleration_tier": "c", "acceleration": "partial"}))

    def test_tier_e_is_unknown(self):
        with self.assertRaisesRegex(SchemaError, "unknown"):
            validate(item("F3", "criteria", {**CRITERIA, "acceleration_tier": "e", "acceleration": "partial"}))
        no_rates = {k: v for k, v in CRITERIA.items() if k != "acceleration_growth_rates"}
        validate(item("F3", "criteria", {**no_rates, "acceleration_tier": "e", "acceleration": "unknown"}))

    def test_tiers_a_b_d_need_two_growth_rates(self):
        no_rates = {k: v for k, v in CRITERIA.items() if k != "acceleration_growth_rates"}
        for tier in ("a", "b", "d"):
            with self.subTest(tier=tier):
                with self.assertRaisesRegex(SchemaError, "성장률 2개"):
                    validate(item("F3", "criteria", {**no_rates, "acceleration_tier": tier}))
                validate(item("F3", "criteria", {**no_rates, "acceleration_tier": tier, "acceleration": "unknown"}))

    def test_growth_rates_shape(self):
        for bad in ([0.1], [0.1, 0.2, 0.3], [0.1, "0.2"], "0.1,0.2", [0.1, True]):
            with self.subTest(value=bad):
                with self.assertRaisesRegex(SchemaError, "acceleration_growth_rates"):
                    validate(item("F3", "criteria", {**CRITERIA, "acceleration_growth_rates": bad}))

    def test_tier_value_domain(self):
        with self.assertRaisesRegex(SchemaError, "acceleration_tier"):
            validate(item("F3", "criteria", {**CRITERIA, "acceleration_tier": "f"}))

    def test_carried_criteria_without_tier_still_reads(self):
        """이어받은 ③ 판단은 단계 없이 읽힌다. 정기 실행에 남는 것은 rejudge 정책이 막는다."""
        old = {k: v for k, v in CRITERIA.items() if k not in ("acceleration_tier", "acceleration_growth_rates")}
        validate(item("F3", "criteria", old, status="carried"))

    def test_v19_does_not_require_tier(self):
        old = {k: v for k, v in CRITERIA.items() if k not in ("acceleration_tier", "acceleration_growth_rates")}
        validate(item("F3", "criteria", old), rules=V19)


class ReconfirmedTest(unittest.TestCase):
    GOOD = [{"at": "2026-10-08", "by": "판단자", "evidence_ids": ["EV-nvidia-001"]}]

    def test_shape(self):
        validate(item("F4", "score", score=4, reconfirmed=self.GOOD))
        bads = ([], [{"at": "2026/10/08", "by": "a", "evidence_ids": ["EV-nvidia-001"]}],
                [{"at": "2026-10-08", "by": "  ", "evidence_ids": ["EV-nvidia-001"]}],
                [{"at": "2026-10-08", "by": "a", "evidence_ids": []}],
                [{"at": "2026-10-08", "by": "a", "evidence_ids": ["nvidia-001"]}],
                [{"at": "2026-10-08", "by": "a", "evidence_ids": "EV-nvidia-001"}],
                [{"at": "2026-10-08", "by": "a", "evidence_ids": ["EV-nvidia-001"], "note": "x"}],
                {"at": "2026-10-08"})
        for bad in bads:
            with self.subTest(value=bad):
                with self.assertRaisesRegex(SchemaError, "reconfirmed"):
                    validate(item("F4", "score", score=4, reconfirmed=bad))

    def test_cross_refs_require_confirmed_evidence(self):
        j = validate(item("F4", "score", score=4, reconfirmed=self.GOOD))
        ev = {"evidence_id": "EV-nvidia-001", "source_id": "S", "status": "candidate"}
        src = [{"source_id": "S"}]
        with self.assertRaisesRegex(SchemaError, "evidence.json 에 없음"):
            validate_cross_refs([], j, [], src)
        with self.assertRaisesRegex(SchemaError, "확정되지 않은 근거"):
            validate_cross_refs([], j, [ev], src)
        validate_cross_refs([], j, [{**ev, "status": "confirmed"}], src)


class EditKindTest(unittest.TestCase):
    def test_rule_based_edit_kind(self):
        got = {f: judgment_edit_kind(V20.payload, f) for f in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")}
        self.assertEqual(got, {"F1": "lockin", "F2": "paths", "F3": "criteria", "F4": "score", "F5": "grade", "F6": None,
                               "F7": "matrix", "F8": "score", "F9": "gate_inputs"})
        self.assertEqual((judgment_edit_kind(V19.payload, "F1"), judgment_edit_kind(V19.payload, "F2")), ("score", None))
        # RuleSet·factors 표·None 도 받는다
        self.assertEqual(judgment_edit_kind(V20, "F1"), "lockin")
        self.assertEqual(judgment_edit_kind(V20.payload["factors"], "F2"), "paths")
        self.assertEqual(judgment_edit_kind(None, "F2"), None)

    def test_input_choices(self):
        lk = JUDGMENT_INPUT_CHOICES["lockin"]
        self.assertEqual(set(lk), {"channel_consumer", "channel_work", "channel_trade", "loop", "switching", "substitutes",
                                   "pricing", "durability_discount", "ai_monetized_in_channel", "pricing_sustained_quarters"})
        self.assertEqual(lk["channel_work"], ["yes", "no"])
        self.assertEqual(lk["pricing_sustained_quarters"], list(range(0, 25)))
        self.assertEqual(lk["ai_monetized_in_channel"], ["yes", "partial", "no", "unknown"])
        p = JUDGMENT_INPUT_CHOICES["paths"]
        self.assertEqual(p["leap_independent"], ["yes", "no", "unknown"])
        self.assertEqual(p["generation_gap_months"], list(range(0, 37)))
        self.assertEqual(JUDGMENT_INPUT_CHOICES["criteria"]["acceleration_tier"], ["a", "b", "c", "d", "e"])
        self.assertNotIn("acceleration_growth_rates", JUDGMENT_INPUT_CHOICES["criteria"])   # CLI 로만 받는다


class NewMetricsTest(unittest.TestCase):
    """2026-10-08 재실행에서 수집할 관측 지표가 카탈로그에 있고 관측 검증을 통과한다."""

    NEW = {"gross_margin_ttm": "ratio", "gross_margin_ttm_prior": "ratio", "top_customer_share": "ratio",
           "rpo_next12m_share": "ratio", "nrr": "ratio", "customer_prepayments": "USD", "token_share": "ratio",
           "price_per_m": "USD", "paid_seats": "count", "mau": "count", "developer_count": "count",
           "fsd_subscribers": "count", "shares_diluted": "count", "sbc_ttm": "USD"}

    def obs(self, metric: str, value, **extra) -> dict:
        out = {"observation_id": f"nvidia.{metric}", "company_id": "nvidia", "metric": metric, "value": value,
               "unit": METRICS[metric]["unit"], "as_of": "2026-10-08", "kind": "actual", "source_id": "S", "status": "verified"}
        if metric in PERIOD_REQUIRED_METRICS:
            out["period"] = {"start": "2025-10-01", "end": "2026-09-30"}
        out.update(extra)
        return out

    def validate(self, *items: dict) -> list[dict]:
        return validate_observations({"schema": "scorecard.observations/1", "run_id": "t", "items": list(items)}, COMPANIES)

    def test_registered_with_units(self):
        self.assertEqual({m: METRICS[m]["unit"] for m in self.NEW}, self.NEW)
        self.validate(*(self.obs(m, 0.5 if self.NEW[m] == "ratio" else 1200) for m in self.NEW))

    def test_unit_must_match_catalog(self):
        with self.assertRaisesRegex(SchemaError, "unit"):
            self.validate(self.obs("paid_seats", 100, unit="USD"))

    def test_ttm_flows_need_period_and_counts_are_non_negative(self):
        with self.assertRaisesRegex(SchemaError, "period"):
            self.validate({k: v for k, v in self.obs("gross_margin_ttm", 0.7).items() if k != "period"})
        with self.assertRaisesRegex(SchemaError, "음수"):
            self.validate(self.obs("mau", -1))
        self.validate(self.obs("gross_margin_ttm", -0.05))   # 매출총이익률은 음수가 될 수 있다


if __name__ == "__main__":
    unittest.main()
