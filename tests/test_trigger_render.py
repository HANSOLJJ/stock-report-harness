# 초안·HTML 트리거 절이 triggers.json 이 있으면 그것을, 없으면 기준선 트리거를 그리는지와 기존 실행 초안의 트리거 절 불변을 잠근다
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, render_html, render_md, stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import write_json  # noqa: E402
from tests.test_approval_commands import FlowBase, cover_previous_triggers  # noqa: E402

OBSREG = "ai-scorecard-2026-09-obsreg"


def trigger_section(draft: str) -> str:
    """초안의 `## 트리거` 절(다음 `## ` 앞까지)."""
    start = draft.index("\n## 트리거\n")
    end = draft.index("\n## ", start + 1)
    return draft[start:end]


class WithTriggersTest(FlowBase):
    def add_fired(self) -> None:
        payload = {"schema": "scorecard.triggers/2", "run_id": self.box.slug, "items": [
            {"trigger_id": "TRG-001", "company_id": "nvidia", "factors": ["F1"], "observation": "소프트웨어 플랫폼 발표",
             "condition": "엔터프라이즈 채택 공시", "deadline": "2027-06-30", "evidence_ids": ["EV-nvidia-001"],
             "source_ids": [self.cand["source_id"]], "status": "watching", "recheck": {"factors": ["F1"], "what": "업무 채널 형성 여부"}},
            {"trigger_id": "TRG-002", "company_id": "openai", "factors": ["F9"], "observation": "자금 조달",
             "condition": "라운드 종결", "deadline": "2026-12-31", "evidence_ids": [], "source_ids": [self.cand["source_id"]],
             "status": "fired", "recheck": {"factors": ["F9"], "what": "런웨이"}}]}
        write_json(run_paths(self.box.slug).triggers, payload)
        # 2026-10-01 발동 트리거는 근거·출처가 필수이고, 이전 트리거는 철회로 처리돼 '그 밖의 상태' 에 함께 센다.
        self.others = 1 + cover_previous_triggers(self.box.slug)

    def test_draft_draws_triggers_json(self):
        self.add_fired()
        stages.research(self.box.slug)
        stages.calculate(self.box.slug)
        section = trigger_section(stages.draft(self.box.slug).read_text(encoding="utf-8"))
        for text in ("| ID | 기업 | Factor | 관찰 사실 | 조건 | 기한 | 근거 | 재검토 |", "TRG-001", "엔터프라이즈 채택 공시", "EV-nvidia-001",
                     "업무 채널 형성 여부", f"그 밖의 상태(fired·expired·withdrawn) {self.others}건", "미래 점수를 저장하지 않는다(C-14)"):
            self.assertIn(text, section)
        self.assertNotIn("TRG-002", section)            # 감시 중인 것만 표에 싣는다
        self.assertNotIn("왜 중요한가(v1.5 원문)", section)

    def test_research_and_draft_share_columns(self):
        stages.research(self.box.slug)
        stages.calculate(self.box.slug)
        research = run_paths(self.box.slug).research.read_text(encoding="utf-8")
        draft = stages.draft(self.box.slug).read_text(encoding="utf-8")
        row = next(line for line in research.splitlines() if line.startswith("| TRG-001 |"))
        self.assertIn(row, trigger_section(draft))

    def test_html_draws_triggers_json(self):
        self.add_fired()
        ctx = engine.load_context(self.box.slug)
        _scores, _obs, legacy = stages.load_baseline(ctx.run["baseline_id"])
        html = render_html.render_triggers(ctx, legacy)
        for text in ("TRG-001", "관찰 사실", "엔터프라이즈 채택 공시", f"그 밖의 상태(fired·expired·withdrawn) {self.others}건", "C-14"):
            self.assertIn(text, html)
        self.assertNotIn("TRG-002", html)
        self.assertNotIn("기준선 원문", html)

    def test_no_watching_trigger(self):
        write_json(run_paths(self.box.slug).triggers, {"schema": "scorecard.triggers/2", "run_id": self.box.slug, "items": []})
        ctx = engine.load_context(self.box.slug)
        self.assertIn("감시 중인 트리거 없음", render_html.render_triggers(ctx, []))
        self.assertIn("- 감시 중인 트리거 없음", "\n".join(render_md._active_trigger_lines(ctx)))


class WithoutTriggersTest(FlowBase):
    def test_draft_and_html_fall_back_to_baseline_triggers(self):
        run_paths(self.box.slug).triggers.unlink()
        stages.research(self.box.slug)
        stages.calculate(self.box.slug)
        section = trigger_section(stages.draft(self.box.slug).read_text(encoding="utf-8"))
        self.assertIn("왜 중요한가(v1.5 원문)", section)
        ctx = engine.load_context(self.box.slug)
        self.assertIsNone(ctx.triggers)
        _scores, _obs, legacy = stages.load_baseline(ctx.run["baseline_id"])
        self.assertTrue(legacy)
        html = render_html.render_triggers(ctx, legacy)
        self.assertIn("기준선 원문", html)
        self.assertIn(legacy[0]["trigger_id"], html)


class ExistingRunTest(unittest.TestCase):
    def test_obsreg_trigger_section_is_byte_identical_to_stored_draft(self):
        """기존 두 실행은 triggers.json 이 없으므로 트리거 절이 저장된 초안과 같아야 한다. 초안 전체는 다시 렌더하지 않는다
        (frontmatter 경로가 레이아웃 이동으로 달라 전체 바이트는 원래 다르다)."""
        ctx = engine.load_context(OBSREG)
        self.assertIsNone(ctx.triggers)
        scores, _obs, legacy = stages.load_baseline(ctx.run["baseline_id"])
        rendered = render_md.render_draft(ctx, engine.load_results(OBSREG), scores, legacy)
        stored = run_paths(OBSREG).draft.read_bytes().decode("utf-8")
        self.assertEqual(trigger_section(rendered).encode("utf-8"), trigger_section(stored).encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
