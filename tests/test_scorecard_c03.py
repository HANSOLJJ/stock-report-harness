# C-03 확정(혼합 모델) 등재와 F2 점수 불변을 고정한다 (C03-IMPL-43)
"""이 테스트가 지키는 계약 넷.

1. **확정된 결정은 무엇을 골랐고 무엇을 밀어냈는지를 같이 들어야 한다.** 고른 것만 남기면 다음
   사람이 밀린 안을 다시 들고 온다.
2. **HANDOVER 는 규칙이 아니다.** 그 표가 판단을 조회로 바꾼 경위가 등재돼 있어야 한다.
3. **미규정은 미규정이라고 적는다.** 세대 격차가 몇 축에서 서야 하는지는 원문이 안 정한다.
4. **이 결정은 F2 를 자동 산출로 바꾸지 않는다.** F2 는 carried_score 로 남고 점수가 안 바뀐다.
"""
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


def decision(did: str = "C-03") -> dict:
    return {x["id"]: x for x in RULES.payload["decisions"]}[did]


class C03DecisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d = decision()

    def test_resolved_with_the_chosen_model(self):
        self.assertEqual(self.d["status"], "resolved")
        self.assertEqual(self.d["chosen"], "paths_with_generation_gap_5")
        self.assertIn("세대 격차", self.d["confirmed_model"]["mapping"])

    def test_only_the_five_rung_changed(self):
        """**사다리의 5점 칸 하나만 교체한다.** 0·1·2개 칸은 그대로다."""
        self.assertEqual(RULES.payload["factors"]["F2"]["path_mapping"], {"0": 2, "1": 3, "2": 4})
        self.assertTrue(RULES.payload["factors"]["F2"]["score5_requires_generation_gap"])
        self.assertIn("5점 칸 하나만", self.d["confirmed_model"]["what_changed"])

    def test_superseded_choice_is_kept_with_its_reason(self):
        """밀린 안을 지우면 다음 사람이 그것을 다시 들고 온다."""
        self.assertIn("activate_candidate_mapping", self.d["choices"])
        sup = self.d["superseded_choice"]
        self.assertEqual(sup["name"], "activate_candidate_mapping")
        self.assertIn("nvidia", sup["why_not"])
        self.assertIn("12", sup["why_not"])

    def test_chosen_must_be_one_of_the_choices(self):
        payload = copy.deepcopy(RULES.payload)
        {x["id"]: x for x in payload["decisions"]}["C-03"]["chosen"] = "made_up"
        with self.assertRaises(SchemaError) as cm:
            validate_rules(payload)
        self.assertIn("choices 에 없음", str(cm.exception))

    def test_handover_is_recorded_as_not_the_rule(self):
        """**HANDOVER 22행이 스스로 손실 경위를 적는다.** 그 사실이 등재돼야 한다."""
        w = self.d["why_the_source_wins_over_handover"]
        self.assertIn("기계화 재고표", w["handover_is_not_the_rule"])
        self.assertIn("성능 경로는 AA 순위로 기계화 가능", w["it_records_its_own_loss"])
        self.assertIn("NVIDIA", w["source_gives_one_path_five"])

    def test_source_location_says_it_is_not_in_this_worktree(self):
        self.assertIn("worker 워크트리에 없다",
                      self.d["why_the_source_wins_over_handover"]["source_location"])

    def test_unspecified_axis_count_is_recorded_as_unspecified(self):
        """**미규정을 임의로 채우지 않는다.**"""
        g = self.d["generation_gap_constraints"]
        self.assertIn("원문이 정하지 않는다", g["unspecified"])
        self.assertIn("임의로 채우지 않는다", g["unspecified"])
        self.assertIn("두 축이 갈리면 둘 다 적는다", g["two_axes_must_both_be_written"])
        self.assertIn("독립 측정을 우선한다", g["vendor_benchmark_is_not_primary"])

    def test_anthropic_recheck_is_flagged_with_trigger_and_date(self):
        r = self.d["pending_recheck"]
        self.assertIn("5→4", r["what"])
        self.assertIn("에이전트 실무", r["trigger"])
        self.assertEqual(r["when"], "2026-11 재채점 (채점표 1100행 · HANDOVER 120행)")


class F2StaysCarriedTest(unittest.TestCase):
    """**규칙 확정이지 자동 산출 전환이 아니다.**"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))

    def test_f2_is_carried_for_every_company(self):
        for c in self.results["companies"]:
            with self.subTest(cid=c["company_id"]):
                self.assertEqual(c["factors"]["F2"]["status"], "carried_score")

    def test_f2_scores_are_unchanged(self):
        got = {c["company_id"]: c["factors"]["F2"]["score"] for c in self.results["companies"]}
        self.assertEqual(got, {
            "alphabet": 4, "amazon": 4, "anthropic": 5, "apple": 2, "meta": 4, "microsoft": 3,
            "nvidia": 5, "openai": 4, "oracle": 2, "palantir": 3, "spacex-xai": 4, "tesla": 3,
            "tsmc": 5, "alibaba": 4})

    def test_scope_says_it_is_not_an_automation_switch(self):
        self.assertIn("자동 산출로 바꾸는 것이 아니다", decision()["scope"]["what_this_is"])


class F2RangeNoteTest(unittest.TestCase):
    """범위 하한 0 이 장치가 만들 수 있는 값이 아니라는 것을 규칙이 알고 있어야 한다."""

    def test_range_note_names_where_the_zero_came_from(self):
        note = RULES.payload["factors"]["F2"]["range_note"]
        self.assertIn("채점규칙 17행", note)
        self.assertIn("경로 0개", note)
        self.assertIn("다른 축", note)

    def test_it_points_at_the_proposal_and_says_it_is_not_applied(self):
        note = RULES.payload["factors"]["F2"]["range_note"]
        self.assertIn("PROPOSAL.md", note)
        self.assertIn("규칙에 적용하지 않았다", note)

    def test_f3_is_the_one_matched_to_its_ladder(self):
        """**예외는 F2 가 아니라 F3 다.** 넷은 일괄 선언에서, F3 만 사다리에서 왔다."""
        f = RULES.payload["factors"]
        self.assertEqual(f["F3"]["range"], [1, 5])
        self.assertEqual(f["F3"]["ladder"][0]["score"], 1)      # 사다리 최저 칸 = 범위 하한
        for fid in ("F1", "F2", "F4", "F5"):
            self.assertEqual(f[fid]["range"], [0, 5])

    def test_f5_is_the_only_device_that_reaches_zero(self):
        """F5 는 3 + A + H 로 0 에 정확히 닿는다. F2 의 장치는 2 가 최저다."""
        f5 = RULES.payload["factors"]["F5"]
        self.assertEqual(3 + min(f5["A_allowed"]) + min(f5["H_allowed"]), 0)
        self.assertEqual(3 + max(f5["A_allowed"]) + max(f5["H_allowed"]), 5)
        self.assertEqual(min(RULES.payload["factors"]["F2"]["path_mapping"].values()), 2)


if __name__ == "__main__":
    unittest.main()
