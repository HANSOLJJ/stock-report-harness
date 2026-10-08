# 규칙 v2.0 판단 수정·제안: 이어받은 score 판단을 lockin·paths·matrix 로 바꾸는 judge·propose→proposal 경로와 승인 페이지 payload 를 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_evidence_three_way import DOWN, UP, V19Base  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402

DAY = "2026-10-08"
LOCKIN = {"channel_consumer": "no", "channel_work": "yes", "channel_trade": "no", "loop": "pass", "switching": "partial",
          "substitutes": "partial", "pricing": "pass", "pricing_sustained_quarters": 9, "durability_discount": "yes",
          "ai_monetized_in_channel": "yes"}
PATHS = {"performance_leap": "pass", "paradigm_adaptation": "pass", "standard_capture": "fail", "top_rank": "unknown",
         "generation_gap": "no", "leap_independent": "yes"}
MATRIX = {"funding_dependent_share": "large", "own_money_returns": "yes"}
TEXT = {"evidence": ["네 질문을 이번 실행의 근거로 다시 판정했다"], "evidence_up": UP, "evidence_down": DOWN}


class V20Base(V19Base):
    """규칙 v2.0 샌드박스 실행. 기준선에서 만들었으므로 ①②⑦ 의 score 판단이 이어받은(carried) 상태로 들어 있다."""

    RULE = "v2.0"

    @property
    def jpath(self) -> Path:
        return self.box.run_dir / "judgments.json"

    def judge(self, company_id: str, factor: str, changes: dict, **kw) -> dict:
        kw.setdefault("reason", "v2.0 재판단")
        kw.setdefault("by", "판단자")
        kw.setdefault("revised_at", DAY)
        return stages.revise_judgment(SLUG, company_id=company_id, factor=factor, changes=changes, **kw)

    def assert_refused(self, company_id: str, factor: str, changes: dict, pattern: str) -> None:
        before = self.jpath.read_bytes()
        with self.assertRaisesRegex(SchemaError, pattern):
            self.judge(company_id, factor, changes)
        self.assertEqual(self.jpath.read_bytes(), before, "거부되면 judgments.json 은 한 바이트도 바뀌지 않는다")

    def factor_result(self, company_id: str, factor: str) -> dict:
        results = engine.compute(engine.load_context(SLUG))
        return next(c for c in results["companies"] if c["company_id"] == company_id)["factors"][factor]


class KindSwitchTest(V20Base):
    def test_carried_score_kinds_load_and_are_incomplete(self):
        for cid, factor in (("nvidia", "F1"), ("nvidia", "F2"), ("openai", "F7")):
            with self.subTest(factor=factor):
                j = self.judgment(cid, factor)
                self.assertEqual((j["kind"], j["status"]), ("score", "carried"))
                self.assertEqual(self.factor_result(cid, factor)["status"], "needs_judgment")

    def test_f1_score_to_lockin_needs_every_key(self):
        partial = {k: v for k, v in LOCKIN.items() if k != "ai_monetized_in_channel"}
        self.assert_refused("nvidia", "F1", {**partial, **TEXT}, "필수 키 누락")
        old = self.judgment("nvidia", "F1")
        out = self.judge("nvidia", "F1", {**LOCKIN, **TEXT})
        new = self.judgment("nvidia", "F1")
        self.assertEqual((new["kind"], new["score"], new["inputs"]), ("lockin", None, LOCKIN))
        self.assertEqual((new["status"], new["reviewer"], new["reviewed_at"]), ("new", "판단자", DAY))
        self.assertEqual((out["previous"]["kind"], out["previous"]["score"], out["previous"]["status"]), ("score", old["score"], "carried"))
        self.assertEqual(new["revision_history"][-1]["previous"]["kind"], "score")
        r = self.factor_result("nvidia", "F1")
        # 강도 pass 4 + 가격 실측 +1 + 대체 공급 partial 0 + 지속성 할인 −1 = 4
        self.assertEqual((r["basis"], r["status"], r["score"], r["calc"]["steps"]),
                         ("lockin", "ok", 4, {"base": 4, "pricing": 1, "substitutes": 0, "durability_discount": -1}))

    def test_f1_pricing_pass_below_threshold_is_refused(self):
        self.assert_refused("nvidia", "F1", {**LOCKIN, "pricing_sustained_quarters": 7, **TEXT}, "8분기 이상")

    def test_f1_score_cell_is_not_editable_in_v20(self):
        self.assert_refused("nvidia", "F1", {"score": 3}, "점수 칸은 고치지 않는다")

    def test_f2_score_to_paths(self):
        no_flag = {k: v for k, v in PATHS.items() if k != "leap_independent"}
        self.assert_refused("nvidia", "F2", {**no_flag, **TEXT}, "leap_independent")
        self.assert_refused("nvidia", "F2", {"performance_leap": "pass", **TEXT}, "필수 키 누락")
        self.judge("nvidia", "F2", {**PATHS, **TEXT})
        new = self.judgment("nvidia", "F2")
        self.assertEqual((new["kind"], new["score"], new["inputs"], new["status"], new["reviewed_at"]),
                         ("paths", None, PATHS, "new", DAY))
        self.assertEqual(self.factor_result("nvidia", "F2")["basis"], "paths")

    def test_f7_score_to_matrix(self):
        self.assert_refused("openai", "F7", {"own_money_returns": "yes", **TEXT}, "funding_dependent_share")
        self.judge("openai", "F7", {**MATRIX, **TEXT})
        new = self.judgment("openai", "F7")
        self.assertEqual((new["kind"], new["score"], new["inputs"], new["status"]), ("matrix", None, MATRIX, "new"))
        r = self.factor_result("openai", "F7")
        self.assertEqual((r["score"], r["status"]), (-2, "ok"))

    def test_f3_tier_and_growth_rates_through_cli_json(self):
        path = self.box.dir / "f3.json"
        path.write_text(json.dumps({"acceleration_tier": "b", "acceleration": "pass", "acceleration_growth_rates": [0.21, 0.34],
                                    **TEXT}, ensure_ascii=False), encoding="utf-8")
        with human_env():
            self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F3", "--json", path, "--reason", "단계 기록", "--by", "판단자")
        new = self.judgment("nvidia", "F3")
        self.assertEqual((new["inputs"]["acceleration_tier"], new["inputs"]["acceleration_growth_rates"], new["status"]),
                         ("b", [0.21, 0.34], "new"))
        self.assert_refused("nvidia", "F3", {"acceleration_growth_rates": ["0.2", "0.3"]}, "숫자 목록")
        self.assert_refused("nvidia", "F3", {"acceleration_tier": "c", "acceleration": "pass"}, "최대 partial")


class ProposalKindSwitchTest(V20Base):
    def test_propose_json_then_accept_switches_f1_to_lockin(self):
        path = self.box.dir / "f1.json"
        path.write_text(json.dumps({"changes": LOCKIN, "evidence_after": TEXT["evidence"], "evidence_up_after": UP,
                                    "evidence_down_after": DOWN}, ensure_ascii=False), encoding="utf-8")
        with human_env():
            self.cli("propose", SLUG, "--company", "nvidia", "--factor", "F1", "--json", path, "--reason", "네 질문 재판정",
                     "--cite", "EV-nvidia-001", "--by", "에이전트")
            self.cli("proposal", SLUG, "--id", "PRP-001", "--accept", "--by", "에이전트")
        new = self.judgment("nvidia", "F1")
        self.assertEqual((new["kind"], new["score"], new["inputs"], new["status"]), ("lockin", None, LOCKIN, "new"))
        self.assertIn("EV-nvidia-001", new["evidence_ids"])
        self.assertEqual(load_json_strict(self.ppath)["items"][0]["status"], "accepted")

    def test_f2_paths_proposal_is_allowed_and_summarized(self):
        p = self.propose(factor="F2", changes=PATHS, evidence_after=TEXT["evidence"], evidence_up_after=UP, evidence_down_after=DOWN)
        self.assertEqual(p["factor"], "F2")
        row = next(r for r in stages.summary(SLUG)["proposals"] if r["proposal_id"] == p["proposal_id"])
        self.assertEqual(row["edit_kind"], "paths")
        self.decide(p["proposal_id"], accept=True, by="에이전트")
        self.assertEqual(self.judgment("nvidia", "F2")["kind"], "paths")


class SummaryPayloadTest(V20Base):
    def test_factor_labels_and_rule_based_edit_kind(self):
        s = stages.summary(SLUG)
        self.assertEqual(s["factor_labels"]["F1"], "① 락인과 가격결정력")
        self.assertEqual(sorted(s["factor_labels"]), ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"])
        kinds = {(r["company_id"], r["factor"]): r["edit_kind"] for r in s["judgments"]}
        self.assertEqual((kinds[("nvidia", "F1")], kinds[("nvidia", "F2")], kinds[("openai", "F7")], kinds[("nvidia", "F4")]),
                         ("lockin", "paths", "matrix", "score"))
        self.assertIn("lockin", s["judgment_choices"])
        self.assertIn("acceleration_tier", s["judgment_choices"]["criteria"])


if __name__ == "__main__":
    unittest.main()
