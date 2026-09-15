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
RUN_DIR = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


class GuidelineRangeTableTest(unittest.TestCase):
    def test_changed_rows_show_v17_range_first_and_keep_old(self):
        text = (ROOT / "docs" / "scorecard" / "design-guideline.md").read_text(encoding="utf-8")
        for fid, old in (("F2", "0~5"), ("F6", "-5~0"), ("F7", "-3~0"), ("F9", "-5~0")):
            with self.subTest(fid=fid):
                row = next(line for line in text.splitlines() if line.startswith(f"| {fid} |"))
                lo, hi = RULES.payload["factors"][fid]["range"]
                self.assertIn(f"**{lo}~{hi}** (v1.7)", row)
                self.assertIn(f"낡음: {old}", row)
        self.assertIn("[낡음 표시 2026-09-15 FIX-52]", text)


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
