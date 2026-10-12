# 규칙 v2.1 테스트: v2.0 대비 차이(① 5점 AI 수익화 조건과 판정 재료)와 계산·스키마·교차 참조·화면 문장을 잠근다
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f1  # noqa: E402
from scorecard.engine import COMPANIES_PATH  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.render_common import _lockin_trace, lockin_calc_text  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import (SchemaError, load_json_strict, validate_companies, validate_cross_refs,  # noqa: E402
                              validate_judgments)
from scorecard.stages import _check_judgment_changes  # noqa: E402

V20, V21 = load_rules("v2.0"), load_rules("v2.1")
COMPANIES = validate_companies(load_json_strict(COMPANIES_PATH))

MONETIZED = {"ai_monetized_channel": "work", "ai_monetized_measure": "seats", "ai_monetized_share": 0.62,
             "ai_monetized_period": "2026-04-01~2026-06-30", "ai_separate_billing_evidence": ["EV-nvidia-001"],
             "ai_price_uplift_evidence": ["EV-nvidia-002"]}


def rules_json(name: str) -> dict:
    return json.loads((ROOT / "scorecard" / "rules" / f"{name}.json").read_text(encoding="utf-8"))


def company() -> dict:
    return {"company_id": "acme", "display_name": "Acme", "aliases": [], "type": "업무", "listed": True, "ticker": "ACME",
            "exchange": "NASDAQ", "share_basis": "common", "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}


def lockin(cid: str = "acme", status: str = "new", **inputs) -> dict:
    base = {"channel_consumer": "no", "channel_work": "yes", "channel_trade": "no",
            "loop": "pass", "switching": "pass", "substitutes": "pass", "pricing": "pass", "pricing_sustained_quarters": 8,
            "durability_discount": "no", "ai_monetized_in_channel": "unknown"}
    base.update(inputs)
    return {"judgment_id": f"{cid}.F1", "company_id": cid, "factor": "F1", "kind": "lockin", "score": None,
            "inputs": base, "evidence": ["시험"], "reviewer": "tester", "reviewed_at": "2026-10-12", "status": status}


def validate(*items: dict, rules=V21) -> list[dict]:
    return validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": list(items)}, COMPANIES, rules.payload)


class DiffTest(unittest.TestCase):
    """v2.0 과 v2.1 의 차이가 선언한 자리에만 있다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v20, cls.v21 = rules_json("v2.0"), rules_json("v2.1")

    def test_v20_file_unchanged(self):
        # 승인된 rejudge(v2.0) 실행의 rules 해시. 이 값이 바뀌면 그 승인이 깨진다.
        digest = hashlib.sha256((ROOT / "scorecard" / "rules" / "v2.0.json").read_bytes()).hexdigest()
        approved = json.loads((ROOT / "output" / "ai-scorecard-2026-10-rejudge" / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(digest, approved["input_hashes"]["rules"])

    def test_top_level_differs_only_where_declared(self):
        self.assertEqual(set(self.v20), set(self.v21))
        changed = {k for k in self.v21 if self.v21[k] != self.v20[k]}
        self.assertEqual(changed, {"rule_version", "note", "factors"})
        self.assertEqual(self.v21["rule_version"], "v2.1")
        self.assertTrue(self.v21["note"].startswith(self.v20["note"] + " | v2.1: "))

    def test_only_f1_changed_so_far(self):
        changed = {f for f in self.v21["factors"] if self.v21["factors"][f] != self.v20["factors"][f]}
        self.assertEqual(changed, {"F1"})

    def test_f1_gate_and_evidence_spec(self):
        f1 = self.v21["factors"]["F1"]
        gate = f1["ladder"]["top_score_requires_ai_monetized"]
        self.assertEqual((gate["input"], gate["requires"], gate["cap"]), ("ai_monetized_in_channel", "yes", 4))
        self.assertEqual(f1["monetization_evidence"]["share_min_exclusive"], 0.5)
        self.assertEqual(set(f1["monetization_evidence"]["inputs"]),
                         {"ai_monetized_channel", "ai_monetized_measure", "ai_monetized_share", "ai_monetized_period",
                          "ai_separate_billing_evidence", "ai_price_uplift_evidence"})
        old = self.v20["factors"]["F1"]
        self.assertEqual({k: v for k, v in f1["ladder"].items() if k != "top_score_requires_ai_monetized"}, old["ladder"])


class F1GateTest(unittest.TestCase):
    def score(self, rules, **inputs) -> dict:
        return compute_f1(company(), JudgmentLookup([lockin(**inputs)]), rules)

    def test_five_needs_yes(self):
        for value in ("partial", "no", "unknown"):
            with self.subTest(value=value):
                r = self.score(V21, ai_monetized_in_channel=value)
                self.assertEqual(r["score"], 4)
                self.assertTrue(r["calc"]["ai_monetization_gate"]["applied"])
                self.assertIn("AI 수익화", " ".join(r["warnings"]))
        r = self.score(V21, ai_monetized_in_channel="yes", **MONETIZED)
        self.assertEqual(r["score"], 5)
        self.assertFalse(r["calc"]["ai_monetization_gate"]["applied"])

    def test_four_and_below_untouched(self):
        # 가격 실측이 미확인이면 사다리는 4 다. 상한 4 는 아무것도 바꾸지 않는다.
        r = self.score(V21, pricing="unknown", ai_monetized_in_channel="no")
        self.assertEqual(r["score"], 4)
        self.assertFalse(r["calc"]["ai_monetization_gate"]["applied"])
        r = self.score(V21, loop="fail", switching="fail", pricing="fail", ai_monetized_in_channel="no")
        self.assertEqual(r["score"], 0)

    def test_v20_has_no_gate(self):
        r = self.score(V20, ai_monetized_in_channel="no")
        self.assertEqual(r["score"], 5)
        self.assertNotIn("ai_monetization_gate", r["calc"])


class MonetizationSchemaTest(unittest.TestCase):
    def test_yes_needs_all_inputs_in_v21(self):
        with self.assertRaisesRegex(SchemaError, "판정 재료"):
            validate(lockin("nvidia", ai_monetized_in_channel="yes"))
        validate(lockin("nvidia", ai_monetized_in_channel="yes", **MONETIZED))

    def test_share_must_be_majority(self):
        for share in (0.5, 0.07):
            with self.subTest(share=share), self.assertRaisesRegex(SchemaError, "과반"):
                validate(lockin("nvidia", ai_monetized_in_channel="yes", **{**MONETIZED, "ai_monetized_share": share}))

    def test_both_evidence_lists_needed(self):
        for key in ("ai_separate_billing_evidence", "ai_price_uplift_evidence"):
            with self.subTest(key=key), self.assertRaisesRegex(SchemaError, key):
                validate(lockin("nvidia", ai_monetized_in_channel="yes", **{**MONETIZED, key: []}))

    def test_channel_must_be_a_real_channel(self):
        with self.assertRaisesRegex(SchemaError, "실질 채널"):
            validate(lockin("nvidia", ai_monetized_in_channel="yes", **{**MONETIZED, "ai_monetized_channel": "consumer"}))

    def test_value_domains(self):
        bads = {"ai_monetized_measure": "users", "ai_monetized_share": 1.2, "ai_monetized_period": " ",
                "ai_separate_billing_evidence": ["nvidia-001"], "ai_price_uplift_evidence": "EV-nvidia-002"}
        for key, value in bads.items():
            with self.subTest(key=key), self.assertRaisesRegex(SchemaError, key):
                validate(lockin("nvidia", ai_monetized_in_channel="partial", **{**MONETIZED, key: value}))

    def test_partial_needs_nothing(self):
        validate(lockin("nvidia", ai_monetized_in_channel="partial"))

    def test_v20_does_not_require_inputs(self):
        validate(lockin("nvidia", ai_monetized_in_channel="yes"), rules=V20)


class MonetizationCrossRefTest(unittest.TestCase):
    SRC = [{"source_id": "S"}]

    def ev(self, eid: str, status: str = "confirmed") -> dict:
        return {"evidence_id": eid, "source_id": "S", "status": status}

    def test_evidence_must_exist_and_be_confirmed(self):
        j = validate(lockin("nvidia", ai_monetized_in_channel="yes", **MONETIZED))
        with self.assertRaisesRegex(SchemaError, "AI 수익화 근거"):
            validate_cross_refs([], j, [self.ev("EV-nvidia-001")], self.SRC)
        with self.assertRaisesRegex(SchemaError, "확정되지 않았다"):
            validate_cross_refs([], j, [self.ev("EV-nvidia-001"), self.ev("EV-nvidia-002", "candidate")], self.SRC)
        validate_cross_refs([], j, [self.ev("EV-nvidia-001"), self.ev("EV-nvidia-002")], self.SRC)


class ChangeShapeTest(unittest.TestCase):
    def test_cli_only_monetization_shapes(self):
        self.assertEqual(_check_judgment_changes("F1", {"ai_monetized_share": 0.6, "ai_separate_billing_evidence": ["EV-a-001"],
                                                        "ai_monetized_channel": "work"}, V21), "lockin")
        bads = ({"ai_monetized_share": "0.6"}, {"ai_separate_billing_evidence": "EV-a-001"}, {"ai_monetized_period": ""},
                {"ai_price_uplift_evidence": [3]})
        for bad in bads:
            with self.subTest(bad=bad), self.assertRaisesRegex(SchemaError, "모양"):
                _check_judgment_changes("F1", bad, V21)

    def test_growth_rates_shape_still_checked(self):
        with self.assertRaisesRegex(SchemaError, "숫자 목록"):
            _check_judgment_changes("F3", {"acceleration_growth_rates": ["a", "b"]}, V21)


class TraceTextTest(unittest.TestCase):
    def test_gate_is_named_not_called_a_clip(self):
        r = compute_f1(company(), JudgmentLookup([lockin(ai_monetized_in_channel="no")]), V21)
        text = _lockin_trace(r["calc"])
        self.assertIn("상한 4 = 4", text)
        self.assertNotIn("로 자름", text)
        vals = dict(lockin(ai_monetized_in_channel="no")["inputs"])
        self.assertIn("(5점 조건)", lockin_calc_text(V21, r, vals))
        r20 = compute_f1(company(), JudgmentLookup([lockin(ai_monetized_in_channel="no")]), V20)
        self.assertIn("(점수 밖 표시)", lockin_calc_text(V20, r20, vals))

    def test_share_shown_with_measure(self):
        j = lockin(ai_monetized_in_channel="yes", **MONETIZED)
        r = compute_f1(company(), JudgmentLookup([j]), V21)
        self.assertIn("좌석 62%(5점 조건)", lockin_calc_text(V21, r, dict(j["inputs"])))


if __name__ == "__main__":
    unittest.main()
