# 승인된 실행(기준선 제외)을 지금 코드로 다시 계산해도 저장된 결과와 같은지 잠근다 — 새 규칙 작업이 옛 실행을 바꾸지 않게
from __future__ import annotations

import copy
import dataclasses
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine  # noqa: E402

# 2026-10-14 규칙 v3.0 구현 계획 S0: test_rules_v18~v20 의 RecomputeTest 는 obsreg·test·rescore 만 봤다.
# 승인된 v2.0(rejudge)·v2.1(v21) 실행이 빠져 있어, 계산 코드를 고치다 그 결과가 바뀌어도 잡지 못했다.
# 기준선(baseline)은 알려진 차이가 있어 test_hash_binding 이 따로 본다.
APPROVED = (
    "ai-scorecard-2026-09-obsreg",
    "ai-scorecard-2026-10-test",
    "ai-scorecard-2026-10-rescore",
    "ai-scorecard-2026-10-rejudge",
    "ai-scorecard-2026-10-v21",
)


class ApprovedRecomputeTest(unittest.TestCase):
    def test_every_approved_run_recomputes_to_its_stored_hash(self):
        for slug in APPROVED:
            with self.subTest(slug=slug):
                ok, stored, fresh = engine.recompute_matches(slug)
                self.assertTrue(ok, f"{slug}: {stored} != {fresh}")

    def test_the_check_notices_a_changed_judgment(self):
        """검사가 실제로 판단 값을 읽는지 본다. 판단 하나의 판정 재료를 메모리에서 바꾸면 해시가 달라져야 한다."""
        slug = "ai-scorecard-2026-10-v21"
        ctx = engine.load_context(slug)
        stored = engine.load_results(slug)["results_hash"]
        judgments = copy.deepcopy(ctx.judgments)
        target = next(j for j in judgments if j["factor"] == "F7" and j["inputs"].get("own_money_returns") == "yes")
        target["inputs"]["own_money_returns"] = "no"
        changed = engine.compute(dataclasses.replace(ctx, judgments=judgments))
        self.assertNotEqual(changed["results_hash"], stored)


if __name__ == "__main__":
    unittest.main()
