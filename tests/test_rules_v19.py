# 규칙 v1.9 테스트(v1.8 대비 ⑥ 트랙 판정만 다름: 예탁증서 상장사도 관측 기간으로 트랙을 가른다)
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.engine import recompute_matches  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from tests.test_scorecard_f6_v17 import company, f6obs  # noqa: E402

V18_SHA256 = "7e215b55c516cca4ccf0ce4d6d1d0a94014b4ecaf01f3bc523127f29009c59c4"


def rules(name: str) -> dict:
    return json.loads((ROOT / "scorecard" / "rules" / f"{name}.json").read_text(encoding="utf-8"))


def run(version: str) -> dict:
    return {"run_id": "t", "rule_version": version, "decisions": []}


class DiffTest(unittest.TestCase):
    def test_only_track_policy_differs(self):
        v18, v19 = rules("v1.8"), rules("v1.9")
        self.assertEqual(set(v18), set(v19))
        for key in v19:
            if key in ("rule_version", "note", "policies"):
                continue
            self.assertEqual(v19[key], v18[key], f"v1.9.{key}가 v1.8과 다름")
        self.assertEqual(v19["rule_version"], "v1.9")
        self.assertTrue(v19["note"].startswith(v18["note"] + " | v1.9: "))

        p18, p19 = v18["policies"], v19["policies"]
        self.assertEqual({k: v for k, v in p19.items() if k != "f6"}, {k: v for k, v in p18.items() if k != "f6"})
        f18, f19 = p18["f6"], p19["f6"]
        self.assertEqual(set(f19) - set(f18), {"track_by_period_basis", "track_by_period_basis_note"})
        self.assertIs(f19["track_by_period_basis"], True)
        for key in f18:
            if key == "tracks":
                continue
            self.assertEqual(f19[key], f18[key], f"v1.9.policies.f6.{key}가 v1.8과 다름")
        for tid, spec in f18["tracks"].items():
            changed = {k for k in spec if spec[k] != f19["tracks"][tid][k]}
            self.assertEqual(changed, {"select"} if tid in ("listed_ttm", "listed_annual") else set(), tid)

    def test_v18_untouched(self):
        digest = hashlib.sha256((ROOT / "scorecard" / "rules" / "v1.8.json").read_bytes()).hexdigest()
        self.assertEqual(digest, V18_SHA256)


class TrackTest(unittest.TestCase):
    """예탁증서 상장사의 트랙. v1.9 는 관측 기간으로, v1.8 은 연간에 고정한다."""

    def compute(self, version: str, period_basis: str):
        c = company(cid="tsmc", share_basis="adr")
        return compute_f6(c, f6obs("tsmc", period_basis=period_basis), JudgmentLookup([]), load_rules(version), run(version))

    def test_v19_adr_ttm_is_listed_ttm(self):
        r = self.compute("v1.9", "ttm")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["calc"]["track"], "listed_ttm")
        self.assertNotIn("period_basis_not_ttm", r["calc"]["p4"]["conditions_hit"])

    def test_v19_adr_annual_stays_annual(self):
        r = self.compute("v1.9", "annual")
        self.assertEqual(r["calc"]["track"], "listed_annual")
        self.assertIn("period_basis_not_ttm", r["calc"]["p4"]["conditions_hit"])

    def test_v18_adr_ttm_still_pending(self):
        """키가 없는 규칙은 지금처럼 연간 트랙에 고정하고, ttm 관측은 기준 불일치로 멈춘다."""
        r = self.compute("v1.8", "ttm")
        self.assertEqual(r["calc"]["track"], "listed_annual")
        self.assertEqual(r["status"], "pending_data")

    def test_common_share_unaffected(self):
        r = compute_f6(company(), f6obs(), JudgmentLookup([]), load_rules("v1.9"), run("v1.9"))
        self.assertEqual(r["calc"]["track"], "listed_ttm")


class RecomputeTest(unittest.TestCase):
    def test_approved_runs_unchanged(self):
        for slug in ("ai-scorecard-2026-09-obsreg", "ai-scorecard-2026-10-test"):
            ok, stored, fresh = recompute_matches(slug)
            self.assertTrue(ok, f"{slug}: {stored} != {fresh}")


if __name__ == "__main__":
    unittest.main()
