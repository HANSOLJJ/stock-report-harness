# 실행 묶음 output/<run_id>/ 경로 도우미와 옮긴 기존 실행의 옛 frontmatter 문자열 허용 범위를 잠근다
from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from report_contract_lib import frontmatter_value, read_markdown  # noqa: E402
from scorecard import engine, stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.validate import LEGACY_RUNS, source_matches  # noqa: E402

SLUG = "ai-scorecard-2026-09-layout"


class RunPathsTest(unittest.TestCase):
    def test_every_path_is_inside_the_bundle(self):
        p = run_paths(SLUG)
        self.assertEqual(p.run_dir, ROOT / "output" / SLUG)
        expected = {
            "plan": "plan.md", "research": "research.md", "draft": "draft.md", "preview": "preview.md",
            "review": "review.md", "review_parts": "review-parts", "html": "report.html", "audit": "audit.md",
            "evidence_dir": "evidence", "evidence": "evidence/evidence.json",
            "candidates": "evidence/candidates.json", "triggers": "triggers.json",
        }
        for field, name in expected.items():
            with self.subTest(field=field):
                self.assertEqual(p.rel(getattr(p, field)), f"output/{SLUG}/{name}")

    def test_run_dir_matches_engine(self):
        self.assertEqual(run_paths(SLUG).run_dir, engine.run_dir(SLUG))


class LegacySourceStringTest(unittest.TestCase):
    """옛 문자열은 옮긴 두 실행에만 허용한다. 다른 실행에서 나오면 불일치다."""

    def test_the_two_moved_runs_accept_old_and_new_strings(self):
        self.assertEqual(LEGACY_RUNS, {"ai-scorecard-2026-09-baseline", "ai-scorecard-2026-09-obsreg"})
        for slug in sorted(LEGACY_RUNS):
            p = run_paths(slug)
            for kind, old in (("plan", f"plan/{slug}.md"), ("research", f"research/{slug}.md"), ("draft", f"drafts/{slug}.md")):
                with self.subTest(slug=slug, kind=kind):
                    self.assertTrue(source_matches(p, kind, old))
                    self.assertTrue(source_matches(p, kind, f"output/{slug}/{kind}.md"))
                    self.assertFalse(source_matches(p, kind, f"output/{slug}/other.md"))

    def test_other_runs_refuse_old_strings(self):
        p = run_paths(SLUG)
        for kind, old in (("plan", f"plan/{SLUG}.md"), ("research", f"research/{SLUG}.md"), ("draft", f"drafts/{SLUG}.md")):
            with self.subTest(kind=kind):
                self.assertFalse(source_matches(p, kind, old))
                self.assertTrue(source_matches(p, kind, f"output/{SLUG}/{kind}.md"))

    def test_moved_draft_really_carries_the_old_strings(self):
        """허용이 실제로 쓰이는지 본다. 옛 문자열이 없어지면 이 예외는 지울 수 있다."""
        fm, _b, _r, _t = read_markdown(run_paths("ai-scorecard-2026-09-obsreg").draft)
        self.assertEqual(frontmatter_value(fm, "plan_source"), "plan/ai-scorecard-2026-09-obsreg.md")
        self.assertEqual(frontmatter_value(fm, "research_source"), "research/ai-scorecard-2026-09-obsreg.md")


class InitRunMakesBundleTest(unittest.TestCase):
    """init·research 가 output/<slug>/ 한 폴더에만 쓰는지 임시 OUTPUT_DIR 로 확인한다."""

    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.saved = engine.OUTPUT_DIR
        engine.OUTPUT_DIR = self.dir / "output"
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        engine.OUTPUT_DIR = self.saved
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_init_and_research_write_into_the_bundle(self):
        out = stages.init_run(SLUG, as_of="2026-09-02", title="묶음 확인", request="묶음 확인", purpose="묶음 확인")
        research_path = stages.research(SLUG)
        bundle = self.dir / "output" / SLUG
        self.assertEqual(out["plan"], bundle / "plan.md")
        self.assertEqual(research_path, bundle / "research.md")
        for name in ("plan.md", "research.md", "run.json", "observations.json", "judgments.json", "sources.json"):
            with self.subTest(name=name):
                self.assertTrue((bundle / name).is_file())
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), ["output"])
        self.assertEqual(sorted(p.name for p in (self.dir / "output").iterdir()), [SLUG])
        fm, _b, _r, _t = read_markdown(research_path)
        self.assertEqual(frontmatter_value(fm, "plan_source"), f"output/{SLUG}/plan.md")


if __name__ == "__main__":
    unittest.main()
