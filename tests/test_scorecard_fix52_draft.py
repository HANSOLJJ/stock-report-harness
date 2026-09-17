# FIX-52 초안 원천 — 지표 원자료 캡션·현금 두 정의·트리거 대체 수치·방법 절 숫자·spacex F9 인용 라벨을 고정한다
"""초안은 생성물이라 손으로 고치지 않는다. 이 테스트는 **렌더러와 판단 원천**이 맞는 문장을 내는지 본다."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


class DraftSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ctx = load_context(SLUG)
        results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        scores, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.text = render_draft(ctx, results, scores, triggers)

    def test_caption_no_longer_claims_everything_is_legacy(self):
        self.assertNotIn("모든 값은 기준선", self.text)
        self.assertIn("표마다 실측(verified)과 승계가 섞여 있다", self.text)
        self.assertIn("현금 검증 완료 12", self.text)

    def test_cash_two_definitions_note(self):
        self.assertIn("**현금 두 정의**", self.text)
        self.assertIn("policies.f6.net_cash.scope_separation", self.text)

    def test_trig024_shows_replaced_value(self):
        row = next(line for line in self.text.splitlines() if line.startswith("| TRIG-024 |"))
        self.assertIn("원문 -14.9% 는 이번 실행 실측 -16.195%", row)
        self.assertIn("왜 중요한가(v1.5 원문)", self.text)

    def test_method_section_reads_policy_numbers(self):
        self.assertIn("최저점은 -4 이며", self.text)
        self.assertIn("흑자 전환 시점을 뒤로 미뤘다고 밝히면", self.text)
        self.assertNotIn("NTM PER 20·29·42·62·90", self.text)


class SpacexF9EvidenceTest(unittest.TestCase):
    def test_v15_numbers_are_labeled_and_verified_header_added(self):
        j = next(x for x in json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))["items"]
                 if x["judgment_id"] == "spacex-xai.F9.obsreg25")
        self.assertIn("-16.195%", j["evidence"][0])
        self.assertIn("2.89년", j["evidence"][0])
        for e in j["evidence"]:
            if "-14.9%" in e or "$100B" in e or "-$32.5B" in e:
                with self.subTest(e=e[:40]):
                    self.assertTrue(e.startswith("(v1.5 인용") or e.startswith("📐"))


if __name__ == "__main__":
    unittest.main()
