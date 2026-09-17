# FIX-76 — factor 개념 설명(원본 02 절) 복원과 작업 메모 분리, 표·카드 중복 제거를 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard import render_html as rh  # noqa: E402
from scorecard.engine import load_context  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"
AUDIT = ROOT / "output" / f"{SLUG}-audit.md"
CONCEPTS = ROOT / "scorecard" / "factor-concepts.json"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}

# 본문에 실리면 안 되는 작업 메모. `별표 A` 같은 출처 표기는 대상이 아니다.
WORKNOTES = ("HANDOVER", "carried_score", "pending_rule_decision", "needs_rule_decision")


def flatten(text: str) -> str:
    """태그·공백·강조 표시를 지운다. 같은 문장이 마크다운과 HTML 로 갈려 있어도 견줄 수 있다."""
    return re.sub(r"\s+", "", re.sub(r"<[^>]+>", "", text).replace("**", ""))


class Fix76Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")
        cls.audit = AUDIT.read_text(encoding="utf-8")
        # 원본 문장과 견줄 때는 태그·공백·강조 표시를 지우고 본다.
        cls.flat = flatten(cls.html)

    def assert_in_body(self, needle: str, what: str) -> None:
        """실패 메시지에 HTML 전문을 싣지 않는다 — 찾던 것만 보인다."""
        self.assertTrue(flatten(needle) in self.flat, f"{what} 가 본문에 없다: {needle[:50]}")

    # ------------------------------------------------- S1 개념 설명이 돌아왔다
    def test_every_factor_has_the_source_concept(self):
        """사용자 원본 `02 9가지 factor 뜯어보기` 가 통째로 빠져 있었다."""
        items = json.loads(CONCEPTS.read_text(encoding="utf-8"))["items"]
        self.assertEqual(len(items), 9)
        for fid in rh.FACTOR_IDS:
            with self.subTest(factor=fid):
                con = rc.factor_concept(self.ctx, fid)
                self.assertTrue(con.get("definition"), "한 줄 정의가 없다")
                self.assertTrue(con.get("question"), "핵심 질문이 없다")
                # 정의와 질문은 접지 않고 화면에 나온다.
                self.assert_in_body(con["definition"], f"{fid} 한 줄 정의")

    def test_the_concept_text_is_copied_not_written(self):
        """문장을 새로 짓지 않았다 — 원본 파일에 그대로 있어야 한다."""
        src = Path(r"C:/Users/noble/Documents/Claude/Projects/자산 포트폴리오/AI기업_채점표_v1.5.html")
        if not src.is_file():
            self.skipTest("원본 파일이 이 기기에 없다")
        # 추출할 때 `<b>` 를 `**` 로 옮겼으므로 강조 표시를 뺀 뒤 견준다.
        raw = flatten(src.read_text(encoding="utf-8"))
        for fid in rh.FACTOR_IDS:
            con = rc.factor_concept(self.ctx, fid)
            for field in ("definition", "question", "metrics"):
                with self.subTest(factor=fid, field=field):
                    got = flatten(str(con.get(field) or ""))
                    self.assertTrue(got and got in raw, f"{fid}.{field} 가 원본에 없다: {got[:40]}")

    def test_renamed_and_stale_places_are_marked(self):
        """원본과 지금 규칙이 다른 자리는 지금 것을 적고 달라진 사실을 덧붙인다."""
        con = rc.factor_concept(self.ctx, "F6")
        self.assertEqual(con["renamed"]["now"], str(self.ctx.rules.factor("F6")["label"]))
        self.assertIn("현재 가격의 정도", con["renamed"]["source"])
        self.assertIn("NTM", con["stale"]["text"])
        self.assert_in_body("지금 규칙은 NTM 을 쓰지 않는다", "낡은 서술 표시")
        # 낡은 서술이 있는 자리마다 표시가 붙는다.
        self.assertEqual(set(con["stale"]["fields"]), {"question", "metrics"})
        self.assertGreaterEqual(self.flat.count(flatten("지금 규칙은 NTM 을 쓰지 않는다")), 2)

    def test_concept_layer_is_separate_from_scoring_layer(self):
        """원본이 `무엇을 재는가` 와 `어떻게 매기는가` 를 나눈 이유가 있다."""
        for head in ("무엇을 재는가", "무엇을 보고 매기는가", "점수를 어떻게 만드는가"):
            with self.subTest(head=head):
                self.assertEqual(self.html.count(f"<h4>{head}"), len(rh.FACTOR_IDS))

    # ------------------------------------------------- S2 작업 메모를 내렸다
    def test_criteria_carry_no_worknotes(self):
        for fid in rh.FACTOR_IDS:
            for line in rc.factor_criteria(self.ctx, fid):
                with self.subTest(factor=fid):
                    self.assertNotRegex(line, r"C-\d+|FIX-\d+")
                    for w in WORKNOTES:
                        self.assertNotIn(w, line)

    def test_strip_worknotes_keeps_the_source_marker(self):
        """`별표 A` 는 읽는 사람이 원문을 찾아가는 표시라 남긴다."""
        self.assertIn("별표 A", rc.factor_criteria(self.ctx, "F1")[0])
        self.assertIn("별표 D", rc.factor_criteria(self.ctx, "F4")[0])
        got = rc.strip_worknotes("세 경로 통과 수 → 0개 2(C-03 확정, 2026-09-14). F2 는 carried_score 다")
        self.assertNotIn("C-03", got)
        self.assertNotIn("carried_score", got)

    def test_rule_notes_moved_to_the_audit_file(self):
        self.assertIn("## 규칙 파일의 항목 메모", self.audit)
        for fid in rh.FACTOR_IDS:
            note = str(self.ctx.rules.factor(fid).get("note") or "")
            if note:
                with self.subTest(factor=fid):
                    self.assertTrue(flatten(note[:60]) in flatten(self.audit), f"{fid} note 가 감사 기록에 없다")
        # 그 원문이 본문으로 돌아오지 않는다.
        self.assertNotIn(flatten("HANDOVER 사다리"), self.flat)

    # ------------------------------------------------- S3 같은 말을 두 번 하지 않는다
    def test_the_table_and_the_card_head_do_not_repeat(self):
        table = self.html[self.html.index("채점 방법과 규칙"):self.html.index('class="fcards"')]
        self.assertIn("점수의 출처", table)
        # 방식·범위·출처는 표에만 있고 카드 머리에는 번호·이름·한 줄 정의만 남는다.
        heads = re.findall(r'<summary><span class="fnum">.*?</summary>', self.html, re.S)
        self.assertEqual(len(heads), len(rh.FACTOR_IDS))
        for h in heads:
            with self.subTest(head=h[:40]):
                self.assertNotIn("fbadge", h)
                self.assertNotIn("범위", h)
                self.assertIn("fdef", h)

    def test_the_source_column_tells_four_things_apart(self):
        """`사람 판단` 한 마디로는 여덟 항목이 같은 말이 되고 방식 칸과도 겹쳤다."""
        got = set(re.findall(r'class="fbadge[^"]*">([^<]+)<', self.html))
        self.assertEqual(got, {"사람이 점수를 적음", "사람이 판정을 적음",
                               "관측에서 계산", "관측 + 사람 판정"})
        # ⑨ 는 섞이고 ⑥ 만 순수 측정이다 — FIX-74 가 세운 사실과 같아야 한다.
        table = self.html[self.html.index("채점 방법과 규칙"):self.html.index('class="fcards"')]
        rows = re.findall(r'<tr><td class="name">.*?</tr>', table, re.S)
        self.assertIn("관측에서 계산", next(r for r in rows if "⑥" in r))
        self.assertIn("관측 + 사람 판정", next(r for r in rows if "⑨" in r))

    # ------------------------------------------------- 제목과 점수
    def test_the_section_is_called_scoring_method(self):
        self.assertIn("채점 방법과 규칙", self.html)
        self.assertNotIn(">방법과 규칙<", self.html)

    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
