# 2026-10-01 시험 실행 출력·가독성 리뷰 지적 렌더러 수정 가운데 단위로 잴 수 있는 것을 잠근다(판단 출처 표시)
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402


class ReviewerLabelTest(unittest.TestCase):
    def test_new_judgment_from_a_prior_run_is_not_this_run(self):
        j = {"status": "new", "reviewer": "설계진행(C-13 A-GRADE-45)", "reviewed_at": "2026-09-14"}
        self.assertEqual(rc.reviewer_label(j, with_owner=False, run_created="2026-10-01"), "이전 실행에서 매김 · 설계진행 · 2026-09-14")

    def test_judgment_revised_in_this_run(self):
        j = {"status": "new", "reviewer": "noble", "reviewed_at": "2026-10-01"}
        self.assertEqual(rc.reviewer_label(j, with_owner=False, run_created="2026-10-01"), "이번 실행에서 다시 매김 · noble · 2026-10-01")

    def test_without_run_date_keeps_the_old_label(self):
        j = {"status": "new", "reviewer": "x", "reviewed_at": "2026-09-14"}
        self.assertEqual(rc.reviewer_label(j, with_owner=False), "이번 실행에서 다시 매김 · x · 2026-09-14")

    def test_carried_is_unchanged(self):
        j = {"status": "carried", "reviewer": "legacy:v1.5", "reviewed_at": "2026-09-02"}
        self.assertEqual(rc.reviewer_label(j, with_owner=False, run_created="2026-10-01"), "원검토 2026-09-02")


class SourceRegistrationTest(unittest.TestCase):
    """2026-10-01 사실·출처 리뷰: 새 출처의 이해상충(Q05)과 트리거가 가리키는 출처 등록."""

    def test_conflict_of_interest_text(self):
        from scorecard.stages import source_conflict_of_interest

        self.assertIsNone(source_conflict_of_interest("nvidia", frozenset({"press"})))
        self.assertIn("자체 발표", source_conflict_of_interest("nvidia", frozenset({"company_statement"})))
        self.assertIn("Anthropic 투자자", source_conflict_of_interest("amazon"))
        both = source_conflict_of_interest("anthropic", frozenset({"company_statement"}))
        self.assertIn("자체 발표", both)
        self.assertIn("당사자", both)


class TriggerSourceRegistrationTest(unittest.TestCase):
    def test_trigger_source_ids_are_registered_with_conflict(self):
        from tests.test_collect_stage import RSS, NOW, SLUG, Sandbox
        from scorecard import stages
        from scorecard.paths import run_paths
        from scorecard.schema import load_json_strict, write_json

        box = Sandbox(("nvidia", "openai"))
        self.addCleanup(box.close)
        paths = run_paths(SLUG)
        stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
        cands = load_json_strict(paths.candidates)["items"]
        nv = [c for c in cands if c["company_id"] == "nvidia"]
        oa = [c for c in cands if c["company_id"] == "openai"]
        self.assertTrue(nv and oa)
        write_json(paths.evidence, {"schema": "scorecard.evidence/1", "run_id": SLUG, "items": [{
            "evidence_id": "EV-nvidia-001", "company_id": "nvidia", "factors": ["F1"], "kind": "news", "source_id": nv[0]["source_id"],
            "published_at_utc": nv[0]["published_at_utc"], "title": nv[0]["title"], "excerpt": nv[0]["title"], "relevance": "r",
            "channel": "company_statement", "conditional_impact": None, "horizon": "short", "counter_evidence": [], "unverified": [],
            "change_vs_previous": "new", "status": "candidate"}]})
        write_json(paths.triggers, {"schema": "scorecard.triggers/2", "run_id": SLUG, "items": [{
            "trigger_id": "TRG-001", "company_id": "openai", "factors": ["F6"], "observation": "o", "condition": "c", "deadline": "2027-01-01",
            "evidence_ids": [], "source_ids": [oa[0]["source_id"]], "status": "watching", "recheck": {"factors": ["F6"], "what": "w"}}]})
        added = stages.register_evidence_sources(SLUG)
        self.assertEqual(sorted(added), sorted({nv[0]["source_id"], oa[0]["source_id"]}))
        by = {s["source_id"]: s for s in load_json_strict(box.run_dir / "sources.json")["items"]}
        self.assertIn("자체 발표", by[nv[0]["source_id"]]["conflict_of_interest"])
        self.assertIn("직접 경쟁사", by[oa[0]["source_id"]]["conflict_of_interest"])


if __name__ == "__main__":
    unittest.main()
