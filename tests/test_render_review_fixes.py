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


if __name__ == "__main__":
    unittest.main()
