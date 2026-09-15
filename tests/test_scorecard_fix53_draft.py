# FIX-53 RC-06 — 초안 근거가 기준선 v1.5 서술이 아니라 현재 활성 판단 evidence 를 먼저 찍는지, 리뷰 템플릿이 승계 판단 예외를 적는지 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft, render_review_template  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


class CurrentJudgmentEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        scores, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.text = render_draft(ctx, cls.results, scores, triggers)
        cls.ctx = ctx
        cls.lines = cls.text.splitlines()

    def block(self, header_fragment: str, n: int = 25) -> str:
        i = next(k for k, line in enumerate(self.lines) if header_fragment in line)
        return "\n".join(self.lines[i:i + n])

    def test_anthropic_and_openai_f5_show_impl48_reasoning(self):
        for cid in ("anthropic", "openai"):
            with self.subTest(cid=cid):
                blk = self.block(f"근거(이번 실행 판단 `{cid}.F5.impl48`")
                self.assertIn("체크리스트 19(채점규칙 727행)", blk)
                self.assertIn("A=+1", blk)
                self.assertIn(f"대체된 판단 `{cid}.F5` (superseded 2026-09-14)", blk)

    def test_openai_received_investment_is_not_active_alliance(self):
        """제외한 받은 투자가 활성 문장으로 읽히면 안 된다 — 옛 줄은 취소선 아래에만 있다."""
        blk = self.block("근거(이번 실행 판단 `openai.F5.impl48`", 30)
        line = next(x for x in blk.splitlines() if "Amazon $50B 투자(3월" in x)
        self.assertIn("~~", line)
        self.assertIn("(superseded)", line)

    def test_meta_f2_old_yardstick_is_struck(self):
        line = next(x for x in self.lines if "AA 종합 1위(Anthropic)가 5의 기준" in x)
        self.assertIn("~~②5는 불가 — AA 종합 1위(Anthropic)가 5의 기준이고 Spark 1.3은 3위~~ (superseded", line)

    def test_spacex_f9_label_reaches_draft(self):
        """FIX-52 가 근거란에 붙인 라벨이 이전 렌더러에서는 초안에 안 나왔다."""
        self.assertIn("(v1.5 인용 · 채점표_v1.5.md 671·673행)", self.text)
        self.assertIn("이 실행의 verified 값", self.text)

    def test_every_active_judgment_header_is_present(self):
        for j in self.ctx.judgments:
            with self.subTest(jid=j["judgment_id"]):
                self.assertIn(f"`{j['judgment_id']}`", self.text)

    def test_auto_factor_keeps_baseline_reference_label(self):
        self.assertIn("기준선 v1.5 서술(참고 — 이번 실행은 입력에서 자동 산출", self.text)


class ReviewTemplateWordingTest(unittest.TestCase):
    def test_carried_exception_and_tension_number(self):
        ctx = load_context(SLUG)
        results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        text = render_review_template(ctx, results, draft_hash="0" * 64)
        self.assertIn("승계 판단 예외", text)
        self.assertIn("open_tensions", text)
        self.assertIn("긴장 번호", text)
        self.assertIn("이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다", text)


if __name__ == "__main__":
    unittest.main()
