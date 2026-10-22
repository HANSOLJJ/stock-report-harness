# 규칙 v3.1(실적 반영 실행 정책) — 점수 규칙이 v3.0 과 같고, 새 정책 키를 스키마가 잠그며, v3.0 파일과 v30full 확인이 그대로인지 본다
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_rules  # noqa: E402
from scorecard.stages import approval_mismatches, current_hashes  # noqa: E402

V30 = load_rules("v3.0")
V31 = load_rules("v3.1")
V30FULL = "ai-scorecard-2026-10-v30full"


def payload() -> dict:
    return copy.deepcopy(V31.payload)


class SameScoringTest(unittest.TestCase):
    def test_only_version_note_and_rejudge_policy_differ(self):
        a, b = V30.payload, V31.payload
        self.assertEqual(sorted(k for k in a if a[k] != b.get(k)), ["note", "policies", "rule_version"])
        self.assertEqual(sorted(k for k in a["policies"] if a["policies"][k] != b["policies"][k]), ["rejudge"])
        old = {k: v for k, v in a["policies"]["rejudge"].items() if k != "note"}
        new = {k: v for k, v in b["policies"]["rejudge"].items() if k not in ("note", "update_runs")}
        self.assertEqual(old, new)
        self.assertEqual(set(b), set(a))

    def test_update_runs_policy(self):
        spec = V31.payload["policies"]["rejudge"]["update_runs"]
        self.assertEqual(spec["max_age_days"], 120)
        self.assertEqual(spec["earnings_forms"], ["10-Q", "10-K", "20-F"])
        self.assertEqual(spec["earnings_8k_items"], ["2.02"])
        self.assertEqual(spec["manual_check_forms"], ["6-K"])
        self.assertEqual(spec["price_refresh"], "all_companies")
        self.assertNotIn("update_runs", V30.payload["policies"]["rejudge"])


class ConfirmedRunUntouchedTest(unittest.TestCase):
    def test_v30full_confirmation_still_valid(self):
        """v3.0.json 을 고치면 v30full 확인 기록의 rules 해시가 어긋난다. v3.1 을 따로 만든 이유다."""
        approval = load_json_strict(ROOT / "output" / V30FULL / "approval.json")
        self.assertEqual(approval["hashes"]["rules"], V30.hash)
        self.assertEqual(approval_mismatches(approval["hashes"], current_hashes(V30FULL)), [])


class UpdateRunsSchemaTest(unittest.TestCase):
    def reject(self, mutate, needle: str):
        p = payload()
        mutate(p["policies"]["rejudge"]["update_runs"])
        with self.assertRaises(SchemaError) as cm:
            validate_rules(p)
        self.assertIn(needle, str(cm.exception))

    def test_accepts_declared_policy(self):
        validate_rules(payload())

    def test_rejects_non_positive_or_bool_age(self):
        self.reject(lambda s: s.update(max_age_days=0), "max_age_days")
        self.reject(lambda s: s.update(max_age_days=True), "max_age_days")
        self.reject(lambda s: s.update(max_age_days=120.0), "max_age_days")

    def test_rejects_empty_earnings_forms(self):
        self.reject(lambda s: s.update(earnings_forms=[]), "earnings_forms")

    def test_rejects_non_string_items(self):
        self.reject(lambda s: s.update(earnings_8k_items=[2.02]), "earnings_8k_items")
        self.reject(lambda s: s.update(manual_check_forms="6-K"), "manual_check_forms")

    def test_rejects_other_price_refresh(self):
        self.reject(lambda s: s.update(price_refresh="updated_only"), "price_refresh")

    def test_rejects_missing_or_unknown_key(self):
        self.reject(lambda s: s.pop("max_age_days"), "max_age_days")
        self.reject(lambda s: s.update(max_age=120), "max_age")


if __name__ == "__main__":
    unittest.main()
