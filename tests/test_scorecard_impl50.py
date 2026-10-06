# IMPL-50 C-11 영업외 비중 ⑦ 이월 차단 — 결정 등재와 양방향 선언을 고정한다
"""이 테스트가 지키는 계약 넷.

1. **C-11 은 block_carryover 로 풀렸고 결정자는 사용자 확인 전이다.** 밀린 안도 choices 에 남는다.
2. **양방향에 적는다.** F6 P4 쪽은 `⑦ 으로 이월하지 않는다`, F7 쪽은 `F7 입력이 아니다`.
3. **원문에 반대로 읽힐 자리(별표 I 347행)를 숨기지 않는다.**
4. **점수 무영향.** F7 은 전부 승계 판단 그대로다.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


def decision(did: str, rules=RULES) -> dict:
    return {x["id"]: x for x in rules.payload["decisions"]}[did]


class C11DecisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d = decision("C-11")

    def test_resolved_as_block_carryover_pending_user_confirmation(self):
        self.assertEqual(self.d["status"], "resolved")
        self.assertEqual(self.d["chosen"], "block_carryover")
        self.assertIn("allow_carryover", self.d["choices"])
        self.assertEqual(self.d["decided_by"], "설계진행 제안 · 사용자 확인 전")

    def test_reasons_cite_the_source_lines(self):
        text = " ".join(self.d["confirmed_model"]["reasons"])
        for line in ("351~356행", "438행", "319~322행"):
            self.assertIn(line, text)
        self.assertIn("L804", self.d["confirmed_model"]["blocked_text"])

    def test_line_347_is_on_record(self):
        """별표 I 347행이 영업외 이익 비중을 ⑦ 절 `측정 가능` 칸에 적는다 — 판정 입력 지정은 아니지만 숨기지 않는다."""
        self.assertIn("347행", self.d["confirmed_model"]["source_text_against"])
        self.assertIn("측정 가능성 분류", self.d["confirmed_model"]["source_text_against"])

    def test_v15_stays_pending(self):
        """v1.5 는 불변이다."""
        self.assertEqual(decision("C-11", load_rules("v1.5"))["status"], "pending")


class BothSidesTest(unittest.TestCase):
    def test_f6_side_says_no_carryover(self):
        cond = {c["id"]: c for c in RULES.payload["policies"]["f6"]["p4"]["conditions"]}["nonop_share"]
        # 2026-09-16 FIX-55 1단계(4차 리뷰 C RC4-06): 금지 범위를 C-11 의 문언과 맞추며 뒤에 참조를 붙였다.
        self.assertTrue(cond["scope"].startswith("F6 P4 전용. ⑦ 으로 이월하지 않는다"))
        self.assertIn("carryover_scope", cond["scope"])
        self.assertIn("438행", cond["scope_why"])

    def test_f6_note_no_longer_states_the_old_formula_as_current(self):
        """NONOP-44 가 formula 를 세전이익 기준으로 고치고 note 의 옛 산식을 남겨 두었다 — 취소선으로 정정."""
        cond = {c["id"]: c for c in RULES.payload["policies"]["f6"]["p4"]["conditions"]}["nonop_share"]
        self.assertTrue(cond["note"].startswith("|영업외 비중| >= 0.30. 영업외손익 = pretax_income_ttm"))
        self.assertIn("~~영업외손익 = net_income_ttm - operating_income_ttm~~", cond["note"])

    def test_f7_side_says_not_an_input_for_all_fourteen(self):
        jud = json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))["items"]
        f7 = [j for j in jud if j["factor"] == "F7"]
        self.assertEqual(len(f7), 14)
        for j in f7:
            with self.subTest(jid=j["judgment_id"]):
                self.assertIn("영업외 비중은 F7 입력이 아니다", j["note"])
                self.assertEqual(j["note"].count("[IMPL-50]"), 1)          # 재실행해도 한 번
                # 원래 14건 전부 carried 를 고정했다. FIX-52 가 매트릭스를 재척도하며 nvidia·oracle 을 새 판단으로
                # 교체했다 — IMPL-50 문장은 그 둘에도 승계돼 있어야 하고 나머지 12건은 carried 그대로다.
                expected = "new" if j["company_id"] in ("nvidia", "oracle") else "carried"
                self.assertEqual(j["status"], expected)

    def test_rules_doc_keeps_nonop_share_out_of_f7(self):
        # 2026-10-06 규칙 문서 재편: 이 검사는 design-guideline 11절 C-11 행의 낡음 표시를 봤다. 그 문서를 지웠으므로
        # 같은 결론(영업외 비중은 ⑥ 소관이고 ⑦ 입력이 아니다)이 사람용 규칙 문서에 적혀 있는지 본다.
        text = (ROOT / "docs" / "scorecard" / "rules.md").read_text(encoding="utf-8")
        f7 = text.split("### ⑦ ", 1)[1].split("\n### ", 1)[0]
        self.assertIn("지분 평가이익(⑥ 의 영업외 비중 소관", f7)
        self.assertIn("입력·점수에는 넣지 않는다", f7)


class NoScoreImpactTest(unittest.TestCase):
    def test_f7_scores_are_carried(self):
        """IMPL-50 자체는 점수를 바꾸지 않는다.

        원래 14개사 F7 전부 carried_score 를 고정했다. FIX-52 S1 재척도로 nvidia·oracle 이 이번 실행 검토(ok)가
        되었고 그 변경은 IMPL-50 이 아니라 FIX-52 의 것이다.
        """
        res = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        for c in res["companies"]:
            with self.subTest(cid=c["company_id"]):
                expected = "ok" if c["company_id"] in ("nvidia", "oracle") else "carried_score"
                self.assertEqual(c["factors"]["F7"]["status"], expected)


if __name__ == "__main__":
    unittest.main()
