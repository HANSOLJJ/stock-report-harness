# FIX-78 — 상태 칸 표기 통일, 경고문 우리말화, 방법 절의 출처 표기를 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import STATUS_LABEL  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"
DRAFT = ROOT / "drafts" / f"{SLUG}.md"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


def strip_tags(x: str) -> str:
    return re.sub(r"<[^>]+>", "", re.sub(r'\s(?:href|id|class|data-\w+)="[^"]*"', "", x))


class Fix78Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        raw = HTML.read_text(encoding="utf-8")
        cls.body = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", raw, flags=re.S)
        i = cls.body.index('<div class="cards"')
        cls.cards = cls.body[i:cls.body.index("<h2", i)]
        cls.method = cls.body[cls.body.index('<span class="num">05</span>'):cls.body.index('id="c-glossary"')]
        cls.draft = DRAFT.read_text(encoding="utf-8")

    # ------------------------------------------------- S1 상태 칸
    def test_status_and_the_evidence_header_use_the_same_words(self):
        """`상태 승계` 와 `사용자의 판단` 이 같은 화면에 있어 둘이 다른 것처럼 읽혔다."""
        self.assertEqual(STATUS_LABEL["carried_score"], "사용자의 판단")
        self.assertEqual(STATUS_LABEL["ok"], "이번 실행 산출")
        text = strip_tags(self.cards)
        flat = text.replace(" ", "")
        self.assertIn("상태사용자의판단", flat)
        self.assertIn("상태이번실행산출", flat)
        self.assertNotIn("상태승계", flat)

    def test_the_header_does_not_repeat_the_status(self):
        """상태 칸이 누구 판단인지 말하므로 머리줄은 언제인지만 더한다."""
        carried = next(j for j in self.ctx.judgments if j["status"] == "carried")
        self.assertEqual(rc.reviewer_label(carried, with_owner=False), f"원검토 {carried['reviewed_at']}")
        self.assertEqual(rc.reviewer_label(carried), f"사용자의 판단 · {carried['reviewed_at']}")
        self.assertIn("근거 · 원검토 2026-09-02 · 판단 기록", strip_tags(self.cards))

    def test_the_index_status_entry_matches(self):
        idx = self.body[self.body.index('id="ix-status"'):self.body.index('id="ix-basis"')]
        self.assertIn("사용자가 앞서 매긴 판단", idx)
        self.assertIn("숫자만 승계", idx)          # 판정 입력이 남았는지는 근거 칸이 갈라 말한다
        self.assertNotIn(">승계<", idx)
        # 설명 줄은 `inline_html` 을 거친다 — 날 태그를 쓰면 글자로 노출된다.
        self.assertNotIn("&lt;b&gt;", self.body)

    def test_remaining_carried_words_are_not_status_labels(self):
        """남은 `승계` 는 관측·근거 층의 말이거나 사용자가 쓴 근거 원문이다 — 상태 칸에는 없다."""
        for m in re.finditer(r'<span class="fst">(.*?)</span>\s*</div>', self.cards, re.S):
            with self.subTest(cell=strip_tags(m.group(1))[:40]):
                self.assertNotIn("상태승계", strip_tags(m.group(1)).replace(" ", ""))
        # 근거 칸의 `숫자만 승계` 는 판정 입력이 없다는 **다른 층**의 정보라 남는다.
        self.assertIn("숫자만 승계", strip_tags(self.cards))

    # ------------------------------------------------- S2 경고문
    def test_engine_warnings_are_readable(self):
        text = strip_tags(self.cards)
        for gone in ("승계 점수를 사용", "legacy_unverified", "legacy 역산", "policies.f6"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, text)
        self.assertIn("앞서 매긴 점수를 그대로 쓴다", text)
        self.assertIn("기준선에서 거꾸로 세운 정의", text)
        self.assertIn("⑥ 순현금 정의 규칙", text)

    def test_readable_warning_does_not_touch_the_data(self):
        """표시할 때만 옮겨 그린다 — `results.json` 의 원문은 그대로다."""
        raw = [w for c in self.results["companies"] for f in c["factors"].values()
               for w in (f.get("warnings") or [])]
        self.assertTrue(any("승계 점수를 사용" in w for w in raw))
        self.assertTrue(any("legacy_unverified" in w for w in raw))
        self.assertEqual(rc.readable_warning("C-09: 매트릭스 입력이 복원되지 않아 승계 점수를 기준선 표시로 사용"),
                         "C-09: 매트릭스 입력이 복원되지 않아 앞서 매긴 점수를 참고 표시로만 쓴다")

    def test_no_broken_josa_anywhere(self):
        """이름 뒤 조사를 이름표 전체로 훑는다(FIX-68 에서 고쳤던 종류)."""
        names = [n for n in set(rc.TERM_NAMES.values()) | set(rc.CODE_NAMES.values()) if len(n) >= 2]
        broken = []
        for text in (strip_tags(self.body), self.draft):
            for nm in names:
                for m in re.finditer(re.escape(nm) + r" ([이가은는을를와과])(?=[\s,.·)]|$)", text):
                    want = rc.fix_josa(nm, " ", m.group(1))
                    if want.replace(" ", "") != m.group(0).replace(" ", ""):
                        broken.append((m.group(0), want))
        self.assertEqual(broken, [], f"조사 깨짐 {len(broken)}건")

    # ------------------------------------------------- S3 방법 절
    def test_method_section_names_its_sources(self):
        text = strip_tags(self.method)
        self.assertNotIn("HANDOVER", text)
        self.assertNotIn("pending_recheck", text)
        self.assertIn("인수인계 문서", text)
        self.assertIn("사용자 원본 채점표", text)
        self.assertEqual(rc.source_names("(채점표 1100행 · HANDOVER 120행)"),
                         "(사용자 원본 채점표 · 인수인계 문서)")

    def test_method_section_decision_numbers_are_countable(self):
        """`TEN-RC-02` 의 꼬리를 `C-02` 로 세면 안 된다 — 실제 결정 번호만 센다."""
        text = strip_tags(self.method)
        loose = re.findall(r"C-\d+", text)
        tight = re.findall(r"(?<![A-Za-z-])C-\d+", text)
        self.assertGreater(len(loose), len(tight), "TEN-RC-0x 오탐이 있어야 정상이다")
        self.assertEqual(len(tight), 11)

    # ------------------------------------------------- 점수 불변
    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
