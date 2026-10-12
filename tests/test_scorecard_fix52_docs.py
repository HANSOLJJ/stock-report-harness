# FIX-52 문서 정합 — 설계 지침 범위표가 v1.7 range 와 같고 Meta·OpenAI F2 근거란의 옛 잣대가 superseded 표시됐는지 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


class GuidelineRangeTableTest(unittest.TestCase):
    # 2026-10-06 규칙 문서 재편: 이 검사는 design-guideline 4.1절 범위표에 붙인 낡음 표시를 봤다. 그 문서를 지우고
    # 사람용 규칙은 rules.md 하나가 됐으므로, **사람용 문서의 범위가 규칙 JSON 과 같은지**를 rules.md 에서 본다.
    def test_rules_doc_ranges_match_the_rule_file(self):
        text = (ROOT / "docs" / "scorecard" / "rules.md").read_text(encoding="utf-8")
        # 2026-10-12 규칙 v2.1: 고정 버전(v1.8)이 아니라 rules.md 머리말이 현행이라고 적은 버전의 JSON 과 대조한다.
        version = re.search(r"\*\*규칙 버전 (v\d+\.\d+)\.\*\*", text).group(1)
        current = load_rules(version).payload["factors"]
        marks = {"F2": "②", "F6": "⑥", "F7": "⑦", "F8": "⑧", "F9": "⑨"}
        spans = {}
        for fid, mark in marks.items():
            with self.subTest(fid=fid):
                lo, hi = current[fid]["range"]
                spans[fid] = f"{lo}~{hi}".replace("-", "−")
                self.assertIn(f"### {mark} ", text)
                self.assertIn(f"({spans[fid]},", text.split(f"### {mark} ", 1)[1].splitlines()[0])
        # 1절 총점 표의 함정 행도 같은 범위를 적어야 한다(옛 범위가 현행처럼 남지 않게).
        row = f"⑥ {spans['F6']}, ⑦ {spans['F7']}, ⑧ {spans['F8']}, ⑨ {spans['F9']}"
        self.assertIn(row, text)


class F2OldYardstickTest(unittest.TestCase):
    def test_meta_and_openai_mark_aa_first_place_as_superseded(self):
        jud = json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))["items"]
        res = {c["company_id"]: c for c in json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))["companies"]}
        for cid in ("meta", "openai"):
            with self.subTest(cid=cid):
                j = next(x for x in jud if x["company_id"] == cid and x["factor"] == "F2")
                text = " ".join(j["evidence"])
                self.assertRegex(text, re.compile(r"~~[^~]*AA 종합 1위[^~]*~~ \(superseded"))
                self.assertIn("세대 격차", j["evidence"][-1])
                self.assertEqual((j["score"], j["status"]), (4, "carried"))
                self.assertEqual(res[cid]["factors"]["F2"]["score"], 4)


if __name__ == "__main__":
    unittest.main()
