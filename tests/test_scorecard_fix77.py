# FIX-77 — 기업 카드의 작업 메모 분리와 `사용자의 판단` 표기 전환을 고정한다
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
DRAFT = ROOT / "drafts" / f"{SLUG}.md"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


def cards_section(html: str) -> str:
    """기업 카드 구역만 자른다. 스타일·스크립트의 주석에도 같은 말이 있어 먼저 걷어낸다."""
    body = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", html, flags=re.S)
    i = body.index('<div class="cards"')
    return body[i:body.index("<h2", i)]


class Fix77Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")
        cls.audit = AUDIT.read_text(encoding="utf-8")
        cls.draft = DRAFT.read_text(encoding="utf-8")
        cls.cards = cards_section(cls.html)

    # ------------------------------------------------- 작업 메모가 본문에서 내려갔다
    def test_company_cards_carry_no_task_codes(self):
        """사용자 지적의 본체 — 기업 카드에 과제 번호·지시서 번호가 실렸다."""
        text = re.sub(r"<[^>]+>", "", self.cards)
        for pat in (r"FIX-\d+", r"OBS-[A-Z]+-\d+", r"HANDOVER", r"F\d-[A-Z]+-\d+"):
            with self.subTest(pattern=pat):
                self.assertEqual(re.findall(pat, text), [], f"카드에 작업 표기가 남았다: {pat}")

    def test_the_draft_is_cleaned_too(self):
        """초안과 HTML 은 같은 표시 규칙을 쓴다 — 한쪽만 고치면 둘이 갈린다."""
        block = self.draft[self.draft.index("## 기업별 상세"):self.draft.index("## 지표 원자료")]
        for pat in (r"FIX-\d+", r"OBS-[A-Z]+-\d+", r"F\d-[A-Z]+-\d+"):
            with self.subTest(pattern=pat):
                self.assertEqual(re.findall(pat, block), [], f"초안에 작업 표기가 남았다: {pat}")

    def test_the_evidence_itself_is_kept(self):
        """사용자가 고른 것은 `메모만 걷어내기` 다 — 근거 내용과 출처는 남는다."""
        text = re.sub(r"<[^>]+>", "", self.cards)
        for kept in ("체크리스트 19(채점규칙 727행)",        # 출처 표기
                     "라벨 정정",                          # 정정 사실
                     "매트릭스 large|yes 칸이 -3 → -2 로 바뀌었다",     # 재척도 내용(백틱은 태그가 된다)
                     "하네스 미표기"):                      # 검토 결과
            with self.subTest(kept=kept):
                self.assertTrue(kept in text, f"근거가 사라졌다: {kept}")

    def test_split_worknote_keeps_content_inside_the_bracket(self):
        got, note = rc.split_worknote("[FIX-53 3단계 라벨 정정: 10-Q Note 1 문면은 more than 이다]")
        self.assertIn("라벨 정정: 10-Q Note 1 문면은 more than 이다", got)
        self.assertNotIn("FIX-53", got)
        self.assertIn("FIX-53", note)
        # 대괄호 안이 작업 표기뿐이면 통째로 내린다.
        got2, note2 = rc.split_worknote("앞 근거 [FIX-56 2단계] 뒤 근거")
        self.assertEqual(got2, "앞 근거 뒤 근거")
        self.assertIn("FIX-56", note2)

    # ------------------------------------------------- 내린 것은 감사 기록에 있다
    def test_history_is_findable_by_company_and_factor(self):
        self.assertIn("## 기업·항목별 작업 이력", self.audit)
        rows = [x for x in self.audit.splitlines() if x.startswith("| `") and "FIX-" in x]
        self.assertGreater(len(rows), 10)
        # 본문에서 내린 것이 그 기업·항목 줄에서 찾아진다.
        self.assertTrue(any("`nvidia`" in r and "⑦ 순환금융" in r and "FIX-52" in r for r in rows))
        self.assertTrue(any("`alibaba`" in r and "⑨ 적자 깊이" in r for r in rows))

    # ------------------------------------------------- 승계 → 사용자의 판단
    def test_carried_judgments_read_as_the_users_own(self):
        self.assertTrue("승계된 판단 — 원검토일" not in self.html, "HTML 에 옛 표기가 남았다")
        self.assertTrue("승계된 판단 — 원검토일" not in self.draft, "초안에 옛 표기가 남았다")
        carried = [j for j in self.ctx.judgments if j["status"] == "carried"]
        self.assertEqual(len(carried), 105)
        self.assertEqual(rc.reviewer_label(carried[0]),
                         f"사용자의 판단 · {carried[0]['reviewed_at']}")

    def test_this_run_rejudged_ones_are_told_apart(self):
        """뭉뚱그리면 거짓이다 — 이번 실행에서 다시 매긴 것은 따로 보인다."""
        fresh = [j for j in self.ctx.judgments if j["status"] != "carried"]
        self.assertEqual(len(fresh), 9)
        self.assertEqual({j["judgment_id"] for j in fresh},
                         {"amazon.F9.obsreg25", "alibaba.F9.obsreg25", "spacex-xai.F9.obsreg25",
                          "tsmc.F5.strict54", "anthropic.F5.impl48", "openai.F5.impl48",
                          "anthropic.F8.f8anth33", "nvidia.F7.fix52", "oracle.F7.fix52"})
        for j in fresh:
            with self.subTest(jid=j["judgment_id"]):
                label = rc.reviewer_label(j)
                self.assertTrue(label.startswith("이번 실행에서 다시 매김"))
                self.assertIn(j["reviewed_at"], label)
                # 검토자 칸의 작업 표기는 이름만 남는다.
                self.assertNotRegex(label, r"C-\d+|[0-9a-f]{7}|A-[A-Z]+-\d+")
        # 색인에도 같은 말이 한 번 나온다. 카드 구역에서만 센다.
        self.assertEqual(self.cards.count("이번 실행에서 다시 매김"), 9)

    def test_the_index_says_the_same_thing(self):
        self.assertTrue("사용자가 앞서 매긴 판단" in self.html, "색인 설명이 다르다: 사용자가 앞서 매긴 판단")
        self.assertTrue("사용자의 판단 · 원검토일" in self.html, "색인 설명이 다르다: 사용자의 판단 · 원검토일")
        self.assertTrue("이번 실행에서 다시 매김" in self.html, "색인 설명이 다르다: 이번 실행에서 다시 매김")

    def test_judgment_ids_stay_for_tracing(self):
        """판단 식별자는 작업 메모가 아니라 데이터 식별자다 — 추적성을 지킨다."""
        linked = {fr["judgment_id"] for c in self.results["companies"]
                  for fr in c["factors"].values() if fr.get("judgment_id")}
        for jid in linked:
            with self.subTest(jid=jid):
                self.assertTrue(f"판단 기록 <code>{jid}</code>" in self.html, f"{jid} 추적이 끊겼다")

    # ------------------------------------------------- 그림 표시
    def test_picture_marks_are_spelled_out_or_dropped(self):
        text = re.sub(r"<[^>]+>", "", self.cards)
        for mark in ("📐", "🆕", "🔧"):
            with self.subTest(mark=mark):
                self.assertTrue(mark not in text, f"그림 표시가 남았다: {mark}")
        # `⚠️` 는 뜻이 있어 글자로 밝힌다.
        self.assertTrue("주의" in text, "경고 라벨이 없다")
        self.assertTrue('<b class="wk">주의</b>' in self.cards, "경고 배지가 없다")

    def test_english_marker_is_renamed(self):
        self.assertTrue("superseded" not in re.sub(r"<[^>]+>", "", self.html), "영어 표기가 남았다")
        self.assertTrue("(대체됨)" in re.sub(r"<[^>]+>", "", self.html), "대체 표기가 없다")

    # ------------------------------------------------- C-번호는 눌러서 본다
    def test_decision_numbers_are_clickable(self):
        plain = re.sub(r'\s(?:href|id|class|data-\w+)="[^"]*"', "", self.cards)
        total = len(re.findall(r"C-\d+", re.sub(r"<[^>]+>", "", plain)))
        linked = len(re.findall(r'<a class="ccode"', self.cards))
        self.assertGreater(total, 0)
        self.assertEqual(total, linked, "카드의 C-번호는 전부 눌러 뜻을 볼 수 있어야 한다")

    # ------------------------------------------------- 점수 불변
    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
