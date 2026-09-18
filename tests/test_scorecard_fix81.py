# FIX-81 — 정정 꼬리·커밋 해시·References 의 리뷰 기록 블록을 본문에서 걷은 것을 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"
AUDIT = ROOT / "output" / f"{SLUG}-audit.md"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


def body_text(html: str) -> str:
    b = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", html, flags=re.S)
    b = re.sub(r'\s(?:href|id|class|data-\w+)="[^"]*"', "", b)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b))


class Fix81Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")
        cls.text = body_text(cls.html)
        cls.audit = AUDIT.read_text(encoding="utf-8")

    def test_no_task_numbers_hashes_or_review_rounds_in_the_body(self):
        self.assertEqual(re.findall(r"FIX-\d+", self.text), [])
        self.assertEqual(re.findall(r"needs_fix", self.text), [])
        # 글자가 하나는 섞인 7자리 — SEC URL 의 숫자(CIK·접수번호)는 해시가 아니다.
        self.assertEqual(re.findall(r"\b(?=[0-9]*[a-f])[0-9a-f]{7}\b", self.text), [])
        # 리뷰 라운드(`8차 · Gemini …`)는 0. `1차 자료`·`2차 출처` 같은 일반 어휘는 남는다.
        self.assertEqual(re.findall(r"\d차 ·|\d차 needs|\(\d차", self.text), [])
        self.assertIn("1차 자료", self.text)

    def test_correction_tails_keep_the_current_content(self):
        self.assertNotIn("[정정 2026-09-15", self.text)
        self.assertIn("보존 20-F 주석 35 PLEDGED ASSETS", self.text)
        self.assertIn("[라벨 정정: 10-Q Note 1 문면은", self.text)
        self.assertEqual(rc.strip_internal_refs("[FIX-53 3단계 라벨 정정: 문면은 더 크다]"), "[라벨 정정: 문면은 더 크다]")

    def test_correction_history_goes_to_the_audit(self):
        part = self.audit.split("## 정정 이력", 1)[1].split("\n## ", 1)[0]
        self.assertIn("[정정 2026-09-15 FIX-53]", part)
        self.assertIn("[FIX-53 3단계 라벨 정정:", part)

    def test_references_carry_one_review_line_read_from_the_review_file(self):
        refs = self.text[self.text.index("07 References"):]
        self.assertIn("네 영역(사실·출처 · 재무 계산 · 규칙 일관성 · 출력·가독성) 독립 검토를 거쳤다 — 모두 통과했다.", refs)
        self.assertIn("검토 기록은 감사 기록에 있다", refs)
        for gone in ("financial-calc", "separate-session-4way", "재판정 3회", "f313060"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, refs)

    def test_review_block_moved_whole_to_the_audit(self):
        part = self.audit.split("## 검토 기록", 1)[1].split("\n## ", 1)[0]
        for kept in ("separate-session-4way", "financial-calc: pass (9차", "f313060", "needs_fix", "FIX-61~64"):
            with self.subTest(kept=kept):
                self.assertIn(kept, part)

    def test_hash_paths_left_the_cards(self):
        for gone in ("3cf9799", "ff75add", "a01f127", "8ddb0ae", ":validation/"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, self.text)
        self.assertIn("보존 원문에서", self.text)
        hist = self.audit.split("## 기업·항목별 작업 이력", 1)[1].split("\n## ", 1)[0]
        self.assertIn("3cf9799:validation/", hist)

    def test_no_dangling_punctuation(self):
        for broken in ("( —", "( )", "(,", "**"):
            with self.subTest(broken=broken):
                self.assertNotIn(broken, re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", self.html.split("</style>", 1)[1])))

    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
