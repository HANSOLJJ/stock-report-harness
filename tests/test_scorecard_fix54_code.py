# FIX-54 1단계 S7 — two_axes 정의 키 강제(RC3-07)와 v1.7 에서 옛 C-03 선택지를 오류로 막는 것(RC3-09)을 고정한다
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f2  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402
from tests.test_scorecard_calc import company, decision, judgment, run  # noqa: E402

RULES_V17 = load_rules("v1.7")
RULES_V15 = load_rules("v1.5")


class TwoAxesDefinitionRequiredTest(unittest.TestCase):
    def test_dict_with_only_banned_word_is_rejected(self):
        for axis in ("immediacy", "marketability"):
            with self.subTest(axis=axis):
                payload = copy.deepcopy(RULES_V17.payload)
                payload["policies"]["f6"]["net_cash"]["scope_separation"]["two_axes"].pop(axis)
                with self.assertRaises(SchemaError) as cm:
                    validate_rules(payload)
                self.assertIn(f"two_axes.{axis}", str(cm.exception))

    def test_blank_definition_is_rejected(self):
        payload = copy.deepcopy(RULES_V17.payload)
        payload["policies"]["f6"]["net_cash"]["scope_separation"]["two_axes"]["marketability"] = "  "
        with self.assertRaises(SchemaError):
            validate_rules(payload)


class SupersededC03ChoiceTest(unittest.TestCase):
    PATHS = {"performance_leap": "pass", "paradigm_adaptation": "fail", "standard_capture": "pass", "top_rank": "no"}

    def test_v17_candidate_mapping_is_explicit_error(self):
        self.assertNotIn("path_mapping_candidate", RULES_V17.factor("F2"))
        r = compute_f2(company(), JudgmentLookup([judgment("F2", "paths", self.PATHS)]), RULES_V17,
                       run([decision("C-03", "activate_candidate_mapping")]))
        self.assertEqual((r["status"], r["score"]), ("error", None))
        self.assertIn("path_mapping_candidate", r["pending"]["message"])

    def test_v15_candidate_mapping_still_works(self):
        r = compute_f2(company(), JudgmentLookup([judgment("F2", "paths", self.PATHS)]), RULES_V15,
                       run([decision("C-03", "activate_candidate_mapping")]))
        self.assertEqual(r["score"], 4)


class DocumentedLimitsTest(unittest.TestCase):
    def test_rc3_06_and_08_are_recorded(self):
        text = (ROOT / "docs" / "scorecard" / "open-items.md").read_text(encoding="utf-8")
        self.assertIn("| RC3-06 |", text)
        self.assertIn("**소비 증명이 아니다.**", text)
        self.assertIn("| RC3-08 |", text)
        self.assertIn("accepted_kinds", text)


if __name__ == "__main__":
    unittest.main()
