# FIX-79 — 카드 사유·참고 문구를 값·기준·이유로 다시 쓴 것과 결정 번호를 본문에서 걷은 것을 고정한다
from __future__ import annotations

import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"
AUDIT = ROOT / "output" / f"{SLUG}-audit.md"
DRAFT = ROOT / "drafts" / f"{SLUG}.md"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


def visible(html: str) -> str:
    body = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", "", html, flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", body))


class Fix79Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.html = HTML.read_text(encoding="utf-8")
        cls.text = visible(cls.html)
        cls.audit = AUDIT.read_text(encoding="utf-8")
        cls.draft = DRAFT.read_text(encoding="utf-8")

    def notes(self, cid: str, fid: str) -> list[dict]:
        return rc.factor_notes(self.ctx, fid, self.res[cid]["factors"][fid])

    # ------------------------------------------------- S1 값·기준·이유
    def test_alphabet_price_card_explains_minus_three(self):
        """사용자가 짚은 줄 — `입력 신뢰도 보정 한 칸 — 조건 영업외 비중` 만으로는 뜻이 읽히지 않았다."""
        fr = self.res["alphabet"]["factors"]["F6"]
        p4 = fr["calc"]["p4"]
        cut = [n for n in self.notes("alphabet", "F6") if n["kind"] == "cut"]
        self.assertEqual(len(cut), 1)
        text = cut[0]["text"]
        self.assertIn(f"**{p4['nonop_share']:.0%}**", text)                     # 값
        self.assertIn("기준 30%", text)                                         # 기준
        self.assertIn("PER 이 실제보다 싸 보일 수 있다", text)                     # 이유
        self.assertIn(f"소계 {fr['calc']['subtotal_before_p4']} 에서 한 칸 낮춰 점수는 **{fr['score']}**", text)
        self.assertEqual((fr["calc"]["subtotal_before_p4"], fr["score"]), (-2, -3))

    def test_values_are_read_from_calc_not_written_in(self):
        fr = copy.deepcopy(self.res["alphabet"]["factors"]["F6"])
        fr["calc"]["p4"]["nonop_share"] = 0.42
        text = next(n["text"] for n in rc.factor_notes(self.ctx, "F6", fr) if n["kind"] == "cut")
        self.assertIn("**42%**", text)

    def test_every_condition_has_a_reason(self):
        tsmc = next(n["text"] for n in self.notes("tsmc", "F6") if n["kind"] == "cut")
        self.assertIn("회계연도 값을 썼다 — 기간이 어긋나", tsmc)
        spacex = next(n["text"] for n in self.notes("spacex-xai", "F6") if n["kind"] == "cut")
        self.assertIn("비교할 전년 1년치 실적이 없다", spacex)
        self.assertIn("조건이 여럿 걸려도 한 칸까지만 깎는다", spacex)

    def test_cuts_caps_and_notes_are_told_apart(self):
        """점수를 깎은 사유와 참고용 경고가 같은 `주의` 딱지로 섞여 있었다."""
        self.assertIn('<b class="wk">감점 사유</b>', self.html)
        self.assertIn('<b class="wk">점수 상한</b>', self.html)
        self.assertIn('<b class="wk">참고</b>', self.html)
        self.assertNotIn('<b class="wk">주의</b>', self.html)
        cap = self.notes("tsmc", "F1")
        self.assertEqual([n["kind"] for n in cap], ["cap"])
        self.assertIn("최고 2점까지", cap[0]["text"])

    def test_why_it_did_not_cut_is_said(self):
        runway = next(n["text"] for n in self.notes("spacex-xai", "F9") if "런웨이" in n["text"])
        self.assertIn("3.03년", runway)
        self.assertIn("기준을 넘었으므로 이 관문에서 더 깎지 않았다", runway)
        unv = next(n["text"] for n in self.notes("alphabet", "F6") if n["kind"] == "note")
        self.assertIn("사용자 원본 값이고 이번에 다시 확인하지 않았다", unv)
        self.assertIn("회사의 성질이 아니라서 점수는 깎지 않았다", unv)

    def test_no_observation_id_or_engine_label_on_screen(self):
        for gone in ("legacy_unverified", "anthropic.arr.v15", "amazon.offbalance_B.obsreg25",
                     "P4 보정", "입력 신뢰도 보정 한 칸 — 조건", "승계 입력 시가총액"):
            with self.subTest(gone=gone):
                self.assertNotIn(gone, self.text)
        self.assertEqual(rc.OBS_ID_RE.findall(self.text), [])
        # 판단 기록 식별자는 추적용으로 남는다(FIX-77).
        self.assertIn("판단 기록 openai.F5.impl48", self.text)

    def test_observation_ids_go_to_the_audit(self):
        self.assertIn("anthropic.arr.v15", self.audit)
        self.assertIn("amazon.offbalance_B.obsreg25", self.audit)

    def test_no_truncated_warnings(self):
        """`[:4]` 로 잘려 비상장 둘의 경고 뒤쪽이 사라졌다."""
        unv = next(n["text"] for n in self.notes("anthropic", "F6") if "다시 확인하지 않았다" in n["text"])
        for name in ("투자 후 기업가치", "연간 반복 매출(ARR)", "1년 전 연간 반복 매출", "누적 조달액",
                     "매출 대비 기업가치 배수"):
            with self.subTest(name=name):
                self.assertIn(name, unv)

    def test_common_net_cash_note_is_said_once_in_the_method(self):
        self.assertEqual(self.text.count("순현금은 아직 확정되지 않은 작업 정의로 잰다"), 1)

    def test_draft_uses_the_same_sentences(self):
        text = next(n["text"] for n in self.notes("alphabet", "F6") if n["kind"] == "cut")
        self.assertIn(f"감점 사유 — {text}", self.draft)

    # ------------------------------------------------- S2 결정 번호
    def test_body_has_no_decision_numbers(self):
        self.assertEqual(re.findall(r"(?<![A-Za-z-])C-\d+", self.text), [])
        self.assertNotIn('class="ccode"', self.html)
        self.assertNotIn('<details class="mdec"', self.html)
        self.assertNotIn('id="c-glossary"', self.html)

    def test_numbers_became_words_not_holes(self):
        for kept in ("② 기준이 확정되기 전 잣대", "확정된 ② 기준(혼합 모델)", "제안된 손실률 구간을 적용해",
                     "확인된 미공시 처리 결정으로 한 칸 강등", "수주잔고 기준과 달라 이번 실행에는 쓰지 않았다"):
            with self.subTest(kept=kept):
                self.assertIn(kept, self.text)
        for broken in ("대체된 것이 다", "적용 로", "주의 — —", "( , ", "(, "):
            with self.subTest(broken=broken):
                self.assertNotIn(broken, self.text)

    def test_path_prefix_and_unknown_codes_are_left_alone(self):
        self.assertEqual(rc.strip_decision_codes("C-13/validation/report.md"), "C-13/validation/report.md")
        self.assertEqual(rc.strip_decision_codes("TEN-RC-03 은 긴장 번호다"), "TEN-RC-03 은 긴장 번호다")

    def test_decision_record_moved_to_audit_without_repeating_itself(self):
        self.assertIn("## 결정 기록", self.audit)
        rows = [x for x in self.audit.split("## 결정 기록", 1)[1].splitlines() if x.startswith("| `C-")]
        self.assertEqual(len(rows), len(self.ctx.rules.payload["decisions"]))
        self.assertNotIn("무엇에 대한 결정인가", self.audit)
        # 이번 실행에서 고른 선택은 이름과 식별자가 함께 있다.
        self.assertTrue(any("`C-03`" in r and "경로 수 매핑 + 세대 격차 최고점" in r for r in rows))

    def test_index_points_to_the_audit(self):
        self.assertIn("결정 기록은 감사 기록의 결정 기록 절에 있다", self.text)

    # ------------------------------------------------- 점수 불변
    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
