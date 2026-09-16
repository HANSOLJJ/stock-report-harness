# FIX-54 1단계 S4·S6 — alibaba F9 옛 점수 문구 정정, 3차 리뷰 긴장 등록(related_tensions 스키마 포함)을 고정한다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class TensionRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.t = {x["id"]: x for x in RULES.payload["open_tensions"]}

    def test_new_tensions_carry_recheck_and_judgments(self):
        expected = {"TEN-RC3-01": ["anthropic.F7", "openai.F7"], "TEN-RC3-03": ["palantir.F1", "oracle.F1"],
                    "TEN-RC3-04": ["tesla.F5", "tesla.F8"], "TEN-RC3-05": ["alibaba.F3"]}
        jids = {j["judgment_id"] for j in load("judgments.json")["items"]}
        for tid, judgments in expected.items():
            with self.subTest(tid=tid):
                self.assertEqual(self.t[tid]["judgment_ids"], judgments)
                self.assertEqual(self.t[tid]["recheck_at"], "2026-11")
                self.assertTrue(set(judgments) <= jids)
                self.assertEqual(self.t[tid]["score_impact_now"][:3], "없다.")

    def test_f7_uses_source_line_numbers(self):
        t = self.t["TEN-RC3-01"]
        self.assertEqual(t["decision_id"], "C-09")
        self.assertIn("채점규칙 321~322행", t["source_lines"])
        self.assertIn("채점규칙 338행", t["source_lines"])
        self.assertIn("anthropic 상향 가능(-1 → 0)", t["direction"])
        self.assertIn("비 Claude 세션", t["rechecker"])
        c09 = next(d for d in RULES.payload["decisions"] if d["id"] == "C-09")
        self.assertEqual(c09["pending_recheck"]["when"], "2026-11")

    def test_related_tensions_are_read_by_schema(self):
        self.assertEqual(self.t["TEN-RC3-03"]["related_tensions"], ["TEN-RC-02"])
        self.assertEqual(self.t["TEN-RC3-04"]["related_tensions"], ["TEN-RC-05"])
        bad = copy.deepcopy(RULES.payload)
        next(x for x in bad["open_tensions"] if x["id"] == "TEN-RC3-04")["related_tensions"] = ["TEN-NOPE"]
        with self.assertRaises(SchemaError):
            validate_rules(bad)

    def test_q10_gets_oracle_and_microsoft_candidate(self):
        q10 = self.t["TEN-RB-Q10"]
        # 2026-09-16 FIX-56 1단계에서 amazon.F3·palantir.F3 이 붙었다 — 이 단계가 세운 oracle.F3 이 첫 affected 로 남아 있는지 본다.
        self.assertEqual(q10["judgment_ids"][:3], ["microsoft.F3", "spacex-xai.F3", "tesla.F3"])
        self.assertEqual([a["judgment_id"] for a in q10["affected"]][0], "oracle.F3")
        self.assertIn("+77%", q10["affected"][0]["why"])
        self.assertIn("채점규칙 163행", q10["note"])
        self.assertIn("+500만→+1,000만", q10["note"])

    def test_alibaba_f3_fail_reading_keeps_three(self):
        self.assertIn("통과점 2 → F3 3", self.t["TEN-RC3-05"]["score_impact_now"])
        res = {c["company_id"]: c for c in load("results.json")["companies"]}
        self.assertEqual(res["alibaba"]["factors"]["F3"]["score"], 3)


class JudgmentTextTest(unittest.TestCase):
    def setUp(self) -> None:
        self.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}

    def test_alibaba_f9_old_score_phrase_struck_with_current_path(self):
        ev = self.j["alibaba.F9.obsreg25"]["evidence"]
        self.assertNotIn("그러나 -2 유지: CapEx RMB 67,678M(+75%)로 FCF -$6.6B", ev)
        struck = next(e for e in ev if "그러나 -2 유지" in e)
        self.assertTrue(struck.startswith("~~그러나 -2 유지~~ (superseded [FIX-54 1단계]"))
        path = ev[ev.index(struck) + 1]
        for part in ("US$-7,226M", "22,398M ÷ 7,226M", "C-16", "**-3**"):
            self.assertIn(part, path)
        res = {c["company_id"]: c for c in load("results.json")["companies"]}
        self.assertEqual(res["alibaba"]["factors"]["F9"]["score"], -3)

    def test_openai_f7_note_no_longer_claims_absence(self):
        note = self.j["openai.F7"]["note"]
        self.assertNotIn("환류 여부) 원문 없음", note)
        self.assertIn("채점표_v1.5.md 662행", note)
        self.assertEqual(self.j["openai.F7"]["inputs"], {})         # 입력 복원은 하지 않았다
        self.assertIn("TEN-RC3-01", self.j["anthropic.F7"]["note"])


if __name__ == "__main__":
    unittest.main()
