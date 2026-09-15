# FIX-53 RC-01·긴장 등록 — net_cash 블록 통째 삭제 거부와 open_tensions 스키마·등록 내용을 고정한다
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

RULES = load_rules("v1.7")


class NetCashBlockRequiredTest(unittest.TestCase):
    def test_deleting_whole_block_is_rejected_while_p2_consumes_it(self):
        payload = copy.deepcopy(RULES.payload)
        payload["policies"]["f6"].pop("net_cash")
        with self.assertRaises(SchemaError) as cm:
            validate_rules(payload)
        self.assertIn("P2 가 net_cash 를 입력으로 쓰므로", str(cm.exception))

    def test_empty_block_is_rejected(self):
        payload = copy.deepcopy(RULES.payload)
        payload["policies"]["f6"]["net_cash"] = {}
        with self.assertRaises(SchemaError):
            validate_rules(payload)

    def test_block_optional_when_no_parameter_consumes_net_cash(self):
        payload = copy.deepcopy(RULES.payload)
        payload["policies"]["f6"].pop("net_cash")
        p2 = payload["policies"]["f6"]["parameters"]["P2"]
        p2["inputs"] = [m for m in p2["inputs"] if m != "net_cash"]
        validate_rules(payload)


class OpenTensionsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.t = {x["id"]: x for x in RULES.payload["open_tensions"]}

    def test_three_registered_for_2026_11(self):
        # 1단계는 셋이었다. FIX-53 2단계가 TEN-RB-Q10(리뷰 B)을 더했다 — 1단계 셋이 그대로 있는지를 본다.
        self.assertLessEqual({"TEN-RC-02", "TEN-RC-03", "TEN-RC-05"}, set(self.t))
        self.assertIn("TEN-RB-Q10", self.t)
        for t in self.t.values():
            with self.subTest(tid=t["id"]):
                self.assertEqual(t["recheck_at"], "2026-11")
                self.assertEqual(t["status"], "open")
                self.assertIn(t["id"].replace("TEN-", ""), t["review_finding"])

    def test_rc02_anthropic_f1_upward_and_non_claude(self):
        t = self.t["TEN-RC-02"]
        self.assertEqual(t["judgment_ids"], ["anthropic.F1"])
        self.assertIn("상향 가능", t["direction"])
        self.assertIn("비 Claude 세션", t["rechecker"])
        self.assertIn("398행", t["tension"])

    def test_rc05_nvidia_same_attribute_width_unknown(self):
        t = self.t["TEN-RC-05"]
        self.assertEqual(t["judgment_ids"], ["nvidia.F5", "nvidia.F8"])
        self.assertIn("262행", t["tension"])
        self.assertIn("중복 폭을 확인하지 못했다", t["direction"])

    def test_rc03_is_c08(self):
        t = self.t["TEN-RC-03"]
        self.assertEqual(t["decision_id"], "C-08")
        self.assertIn("239행", t["tension"])
        self.assertIn("273~278행", " ".join(t["source_lines"]))

    def test_schema_requires_recheck_time_and_judgments(self):
        for key, bad in (("recheck_at", "11월"), ("judgment_ids", []), ("direction", "")):
            with self.subTest(key=key):
                payload = copy.deepcopy(RULES.payload)
                payload["open_tensions"][0][key] = bad
                with self.assertRaises(SchemaError):
                    validate_rules(payload)

    def test_schema_rejects_unknown_decision(self):
        payload = copy.deepcopy(RULES.payload)
        payload["open_tensions"][1]["decision_id"] = "C-99"
        with self.assertRaises(SchemaError):
            validate_rules(payload)


if __name__ == "__main__":
    unittest.main()
