# FIX-80 — 옛 문구 중복·v1.5 참고 문단·내부 참조(긴장·리뷰·행 번호·판단 ID)·`승계` 를 본문에서 걷은 것을 고정한다
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
RUN_DIR = ROOT / "output" / SLUG
HTML = ROOT / "output" / SLUG / "report.html"
AUDIT = ROOT / "output" / SLUG / "audit.md"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}
# 조율자가 세라고 한 일곱 패턴. 목표는 본문 0 이다.
PATTERNS = {"TEN-": r"TEN-", "RC-숫자": r"RC-\d", "Q숫자": r"(?<![A-Za-z0-9])Q\d\d", "행 번호": r"\d+행",
            "AGENTS.md": r"AGENTS\.md", "판단 ID": r"(?<![\w.])[a-z][a-z0-9-]*\.F\d", "승계": r"승계"}


def body_text(html: str) -> str:
    b = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", html, flags=re.S)
    b = re.sub(r'\s(?:href|id|class|data-\w+)="[^"]*"', "", b)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", b))


def row(html: str, cid: str, label: str) -> str:
    card = re.search(rf'<details class="card" id="card-{cid}".*?</details>', html, re.S).group(0)
    return re.search(rf'<span class="flab">{label}</span>.*?(?=<div class="frow">|</div></div><div class="cgrp">|$)',
                     card, re.S).group(0)


class Fix80Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")
        cls.text = body_text(cls.html)
        cls.audit = AUDIT.read_text(encoding="utf-8")

    # ------------------------------------------------- S1 옛 문구 중복
    def test_price_line_says_input_trust_only_once(self):
        """산식 줄 꼬리와 감점 사유가 같은 말을 두 번 했다 — 앞의 것은 사용자가 뜻을 모르겠다던 형태였다."""
        self.assertNotIn("하나가 강등을 정한다", self.text)
        self.assertNotIn("입력 신뢰도 -1(", self.text)
        for cid in ("alphabet", "amazon", "tsmc", "alibaba", "spacex-xai"):
            with self.subTest(cid=cid):
                r = body_text(row(self.html, cid, "⑥ 가격"))
                self.assertEqual(r.count("입력 신뢰도"), 1)
                self.assertIn("감점 사유 입력 신뢰도 −1", r)

    def test_alphabet_price_card_reads_straight_through(self):
        r = body_text(row(self.html, "alphabet", "⑥ 가격"))
        self.assertIn("= 소계 -2 감점 사유 입력 신뢰도 −1", r)
        self.assertIn("걸린 조건은 이 하나다", r)
        self.assertIn("점수는 -3", r)

    # ------------------------------------------------- S2 v1.5 참고 문단
    def test_auto_factor_reference_paragraph_left_the_card(self):
        # 절 안내문의 `옛 참고 서술을 싣지 않는다` 는 그 사실을 알리는 말이라 제외하고 문단 머리로 센다.
        for gone in ("참고 서술 —", "점수 근거가 아니다", "NTM PER 25.3", "20~29 구간"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, self.text)
        self.assertIn("v1.5 참고 문면", self.audit)
        self.assertIn("NTM PER 25.3", self.audit)

    def test_human_judgment_evidence_stays(self):
        """사람 판단의 근거 문장은 점수 근거라 남는다."""
        r = body_text(row(self.html, "alphabet", "① 네트워크"))
        self.assertIn("Gemini 앱 MAU 9.5억", r)

    # ------------------------------------------------- S3·S4 내부 참조와 `승계`
    def test_seven_patterns_are_zero_in_the_body(self):
        for name, pat in PATTERNS.items():
            with self.subTest(pattern=name):
                self.assertEqual(re.findall(pat, self.text), [], name)

    def test_tensions_are_said_in_words_with_when(self):
        self.assertIn("2026-11 에 다시 본다", self.text)
        self.assertIn("Anthropic ⑧ 이 -4 로 내려가지 않는 유일한 근거", self.text)
        self.assertNotIn('id="ix-ten"', self.html)

    def test_rejudged_one_says_what_changed_without_review_ids(self):
        r = body_text(row(self.html, "tsmc", "⑤ 아군"))
        self.assertIn("이번 실행에서 다시 매김", r)
        self.assertIn("A+2 엄격 읽기", r)
        self.assertIn("대체된 판단 TSMC ⑤", r)

    def test_removed_refs_are_findable_in_the_audit_by_company_and_factor(self):
        hist = self.audit.split("## 기업·항목별 작업 이력", 1)[1].split("\n## ", 1)[0]
        for cid, factor, frag in (("alphabet", "⑦ 순환금융", "판단 기록 alphabet.F7"),
                                  ("tsmc", "⑤ 아군", "2차 리뷰 C RC-04"),
                                  ("tsmc", "⑤ 아군", "체크리스트 Q03"),
                                  ("tsmc", "⑤ 아군", "채점규칙 192·193행"),
                                  ("anthropic", "② 게임체인저", "TEN-RA4-01")):
            with self.subTest(frag=frag):
                self.assertIn(f"| `{cid}` | {factor} | {frag} |", hist)
        self.assertIn("## 다시 볼 것(긴장)", self.audit)
        self.assertIn("| `TEN-RC-02` |", self.audit)

    def test_strip_keeps_bold_pairs(self):
        """번호만 굵게 쓴 자리를 떼면서 강조 짝이 깨져 `**` 가 새어 나왔다."""
        got = rc.strip_internal_refs("재검토는 **TEN-RA5-01**(2026-11 · 조건). 다음 **1순위**는")
        self.assertEqual(got.count("**") % 2, 0)
        self.assertNotIn("TEN-", got)
        self.assertNotIn("**", re.sub(r"<[^>]+>", "", self.html.split("</style>", 1)[1]))

    # ------------------------------------------------- 점수 불변
    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
