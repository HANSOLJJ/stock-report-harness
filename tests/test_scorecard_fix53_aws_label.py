# FIX-53 3단계 보완 — `AWS $100B/10년` 라벨이 판단 근거란·트리거 초안 전부에서 같은 정정을 달고 있는지 고정한다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / SLUG
# 2026-09-17 FIX-77: 작업 번호는 감사 기록으로 내렸다. **정정이 붙어 있다**는 사실은 그대로다.
MARKER = "라벨 정정"


class AwsLabelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ctx = load_context(SLUG)
        results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        scores, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.lines = render_draft(ctx, results, scores, triggers).splitlines()
        cls.jud = {j["judgment_id"]: j for j in ctx.judgments}

    def test_every_active_label_carries_the_correction(self):
        """superseded 취소선 줄을 뺀 모든 `AWS $100B/10년` 줄에 정정이 한 번 붙는다."""
        hits = [x for x in self.lines if "AWS $100B/10년" in x and "~~" not in x]
        self.assertEqual(len(hits), 3)                                      # F8 · F9 · TRIG-015
        for line in hits:
            with self.subTest(line=line[:60]):
                self.assertEqual(line.count(MARKER), 1)
                self.assertIn("more than", line)
                self.assertIn("하한 기준 환산", line)

    def test_f9_gate4_and_trigger(self):
        f9 = next(e for e in self.jud["anthropic.F9"]["evidence"] if "AWS $100B/10년" in e)
        self.assertIn("커버리지는 1.3배보다 낮다", f9)
        trig = next(x for x in self.lines if x.startswith("| TRIG-015 |"))
        self.assertIn("HANDOVER 51행", trig)

    def test_f8_ratio_marked_lower_bound(self):
        text = " ".join(self.jud["anthropic.F8.f8anth33"]["evidence"])
        self.assertIn("4배는 AWS 약정 하한 $100B 기준 환산", text)

    def test_trigger_source_untouched(self):
        t = json.loads((ROOT / "scorecard" / "baseline" / "v1.5" / "triggers.json").read_text(encoding="utf-8"))["items"]
        why = next(x for x in t if x["trigger_id"] == "TRIG-015")["why"]
        self.assertNotIn(MARKER, why)

    def test_schema_requires_marker_inside_correction(self):
        payload = copy.deepcopy(load_rules("v1.7").payload)
        payload["source_text_corrections"][0]["marker"] = "없는 표식"
        with self.assertRaises(SchemaError):
            validate_rules(payload)


if __name__ == "__main__":
    unittest.main()
