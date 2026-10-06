# 변경 미리보기의 '이전 실행 대비' 표가 변동 원인(판단 수정·트랙 변경·관측)과 순위만 움직인 기업을 바르게 보이는지 잠근다
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine  # noqa: E402
from scorecard.render_md import render_preview  # noqa: E402

FACTORS = [f"F{i}" for i in range(1, 10)]


def company(cid: str, scores: dict[str, int], total: int, rank: int, f6_track: str = "listed_ttm") -> dict:
    factors = {f: {"score": scores.get(f, 0), "calc": {}} for f in FACTORS}
    factors["F6"]["calc"] = {"track": f6_track}
    return {"company_id": cid, "display_name": cid.upper(), "factors": factors, "total": total, "rank": rank,
            "carried_factors": [], "pending": []}


def judgment(cid: str, factor: str, inputs: dict, previous_inputs: dict, revised_at: str = "2026-10-06") -> dict:
    return {"company_id": cid, "factor": factor, "inputs": inputs, "score": None,
            "revision_history": [{"revised_at": revised_at, "previous": {"inputs": previous_inputs, "score": None}}]}


class PreviewCauseTest(unittest.TestCase):
    def render(self, prev: list[dict], now: list[dict], judgments: list[dict]) -> str:
        ctx = SimpleNamespace(slug="ai-scorecard-t", judgments=judgments, rules=SimpleNamespace(decision=lambda d: {}),
                              run={"baseline_id": "v1.5", "created_at": "2026-10-06",
                                   "continued_from": {"run_id": "ai-scorecard-prev"}})
        with mock.patch.object(engine, "load_results", return_value={"companies": prev}):
            return render_preview(ctx, {"companies": now, "pending_rule_decisions": []}, None)

    def test_evidence_only_revision_is_not_judgment_change(self):
        """근거 문장만 바꾼 수정(판정 재료 그대로)은 판단 수정이 아니라 관측 변화로 분류한다."""
        same = {"fcf_trend": "unknown"}
        text = self.render([company("baba", {"F9": -3}, 7, 10)], [company("baba", {"F9": -4}, 6, 11)],
                           [judgment("baba", "F9", same, dict(same))])
        self.assertIn("⑨", text)
        self.assertIn("📊 관측(가격·재무)", text)
        self.assertNotIn("✍️ 판단 수정", text)

    def test_material_revision_is_judgment_change(self):
        text = self.render([company("baba", {"F9": -3}, 7, 10)], [company("baba", {"F9": -4}, 6, 11)],
                           [judgment("baba", "F9", {"fcf_trend": "declining"}, {"fcf_trend": "unknown"})])
        self.assertIn("✍️ 판단 수정", text)

    def test_track_change_names_rule(self):
        text = self.render([company("tsmc", {"F6": -5}, 8, 8, "listed_annual")],
                           [company("tsmc", {"F6": -2}, 11, 5, "listed_ttm")], [])
        self.assertIn("📐 규칙(트랙 listed_annual→listed_ttm)·📊 관측", text)

    def test_rank_only_move_is_listed(self):
        text = self.render([company("pltr", {}, 6, 11)], [company("pltr", {}, 6, 10)], [])
        self.assertIn("PLTR", text)
        self.assertIn("factor 같음(순위만 이동)", text)


if __name__ == "__main__":
    unittest.main()
