# 실적 반영 실행의 출력(계획 U5) — 초안·HTML 의 회사별 반영 기준일, research 의 갱신 범위 절, 확인된 실행의 초안 불변을 잠근다
from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard import render_common as rc  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.render_html import render_audit_md, render_cards, render_method  # noqa: E402
from scorecard.render_md import render_draft, render_research  # noqa: E402
from scorecard.schema import load_json_strict  # noqa: E402
from tests.test_collect_stage import Sandbox  # noqa: E402
from tests.test_update_scope import SEC, filing  # noqa: E402

V30FULL = "ai-scorecard-2026-10-v30full"
NEW = "ai-scorecard-2026-10-q3t"
AS_OF = "2026-10-22"


class UpdateRenderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(init=False)
        self.addCleanup(self.box.close)
        src = ROOT / "output" / V30FULL
        if not src.is_dir():
            self.skipTest(f"{V30FULL} 실행이 없다")
        shutil.copytree(src, engine.run_dir(V30FULL))

    def make_update_run(self) -> None:
        stages.init_run(NEW, from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="3분기 실적 반영",
                        update_companies=["alphabet", "spacex-xai"], update_reason="Alphabet·SpaceX-xAI 3분기 실적")
        engine.write_results(NEW, engine.compute(engine.load_context(NEW)))
        path = run_paths(NEW).candidates
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"schema": "scorecard.candidates/1", "run_id": NEW, "window": {"since": "2026-04-25", "until": AS_OF},
                                    "filings_fetched_at": {c: f"{AS_OF}T09:00:00Z" for c in SEC},
                                    "items": [filing("tsmc", "6-K", "2026-10-15")]}, ensure_ascii=False), encoding="utf-8")

    def test_confirmed_run_draft_is_unchanged(self):
        before = run_paths(V30FULL).draft.read_bytes()
        stages.draft(V30FULL)
        self.assertEqual(run_paths(V30FULL).draft.read_bytes(), before, "refreshed_at 이 없는 확인된 실행의 초안은 그대로다")

    def test_draft_and_html_show_refreshed_dates(self):
        self.make_update_run()
        ctx = engine.load_context(NEW)
        results = engine.load_results(NEW)
        scores, _obs, triggers = stages.load_baseline(ctx.run["baseline_id"])
        draft = render_draft(ctx, results, scores, triggers)
        self.assertRegex(draft, r"### Alphabet[^\n]* · 반영 기준 2026-10-22\n")
        self.assertRegex(draft, r"### Tesla[^\n]* · 반영 기준 2026-10-14\n")
        self.assertIn("- 이 실행은 실적 반영 실행이다(Alphabet·SpaceX-xAI 3분기 실적). Alphabet / Google, SpaceX + xAI 의 판단은", draft)
        html = render_cards(results, scores, ctx.companies, ctx.observations, ctx.judgments, rc.replacements(ctx), ctx)
        self.assertIn("개사 기준) · 반영 기준 2026-10-22</div>", html[html.index('id="card-alphabet"'):])
        self.assertIn("개사 기준) · 반영 기준 2026-10-14</div>", html[html.index('id="card-tesla"'):])
        self.assertIn("실적 반영 실행이다", render_method(ctx, results))
        audit = render_audit_md(ctx, results, None)
        self.assertIn("회사별 마지막 전체 갱신일: alibaba 2026-10-14, alphabet 2026-10-22", audit)

    def test_research_has_scope_section(self):
        self.make_update_run()
        stages.declare_scope_extra(NEW, [("meta", "F3")], reason="Alphabet ③ 의 새 잣대가 닿는다")
        ctx = engine.load_context(NEW)
        text = render_research(ctx, hashes=ctx.hashes, legacy_triggers=[], previous_triggers=[])
        section = text[text.index("## 갱신 범위"):text.index("## 근거")]
        for needle in ("갱신 회사 Alphabet / Google, SpaceX + xAI 의", "| Meta | ③", "선언한 추가 항목 — Alphabet ③ 의 새 잣대가 닿는다",
                       "### 회사별 마지막 전체 갱신일", "| Alphabet / Google | 2026-10-22 | 0 | 갱신 |", "| Tesla | 2026-10-14 | 8 | 이어받음 |",
                       "### 리뷰가 확인할 공시", "| TSMC | 6-K | 2026-10-15 |"):
            with self.subTest(needle=needle):
                self.assertIn(needle, section)

    def test_regular_run_has_no_scope_section_but_keeps_dates(self):
        stages.init_run("ai-scorecard-2026-10-reg", from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="정기")
        ctx = engine.load_context("ai-scorecard-2026-10-reg")
        text = render_research(ctx, hashes=ctx.hashes, legacy_triggers=[], previous_triggers=[])
        self.assertNotIn("## 갱신 범위", text)
        self.assertIsNone(rc.update_run_sentence(ctx))
        self.assertEqual(rc.refreshed_label(ctx, "tesla"), "반영 기준 2026-10-22")


if __name__ == "__main__":
    unittest.main()
