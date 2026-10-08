# 규칙 v2.0 재확인 경로(judge·propose·proposal 의 reconfirmed)와 research 단계의 rejudge 정책 정지를 잠근다
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import stages  # noqa: E402
from scorecard.evidence_lib import utc_now_iso  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, write_json  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_evidence_three_way import DOWN, UP  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402
from tests.test_v20_judge import V20Base  # noqa: E402
from tests.test_v20_validate import rejudge_all  # noqa: E402

AGAIN = {"reconfirmed": {"evidence_ids": ["EV-nvidia-001"]}}


class ReconfirmBase(V20Base):
    def setUp(self) -> None:
        super().setUp()
        # 옛 형식(판정 칸 하나) 판단은 세 칸이 없어 v2.0 에서 새 판단이 될 수 없다. 근거 칸만 먼저 채운다(승계는 그대로).
        self.judge("nvidia", "F4", {"evidence_up": UP, "evidence_down": DOWN}, revised_at="2026-10-08")
        self.judge("nvidia", "F5", {"evidence_up": UP, "evidence_down": DOWN}, revised_at="2026-10-08")

    def put_candidate(self, eid: str) -> None:
        payload = load_json_strict(self.paths.evidence)
        payload["items"].append(self.evidence_item(eid))
        write_json(self.paths.evidence, payload)
        stages.register_evidence_sources(SLUG)


class JudgeReconfirmTest(ReconfirmBase):
    def test_reconfirm_alone_turns_carried_into_new_today(self):
        before = self.judgment("nvidia", "F4")
        self.assertEqual(before["status"], "carried")
        out = stages.revise_judgment(SLUG, company_id="nvidia", factor="F4", changes=AGAIN, reason="원문을 다시 읽었다", by="판단자")
        new = self.judgment("nvidia", "F4")
        today = utc_now_iso()[:10]
        self.assertEqual((new["status"], new["reviewer"], new["reviewed_at"]), ("new", "판단자", today))
        self.assertEqual(new["reconfirmed"], [{"at": today, "by": "판단자", "evidence_ids": ["EV-nvidia-001"]}])
        for key in ("kind", "score", "inputs", "evidence", "evidence_up", "evidence_down"):
            self.assertEqual(new[key], before[key], key)   # 값은 그대로다
        last = new["revision_history"][-1]
        self.assertEqual((last["reason"], last["revised_by"], last["previous"]["status"]), ("원문을 다시 읽었다", "판단자", "carried"))
        self.assertNotIn("reconfirmed", last["previous"], "재확인이 없던 판단의 이력에는 그 칸이 없다")
        self.assertEqual(out["current"]["reconfirmed"], new["reconfirmed"])

    def test_second_reconfirm_appends(self):
        self.judge("nvidia", "F4", AGAIN, revised_at="2026-10-08")
        self.judge("nvidia", "F4", AGAIN, revised_at="2026-10-09", by="둘째")
        new = self.judgment("nvidia", "F4")
        self.assertEqual([(r["at"], r["by"]) for r in new["reconfirmed"]], [("2026-10-08", "판단자"), ("2026-10-09", "둘째")])
        self.assertEqual(len(new["revision_history"][-1]["previous"]["reconfirmed"]), 1)

    def test_empty_or_malformed_reconfirm_is_refused(self):
        for bad in ({"reconfirmed": {"evidence_ids": []}}, {"reconfirmed": {"evidence_ids": ["nvidia-001"]}},
                    {"reconfirmed": ["EV-nvidia-001"]}, {"reconfirmed": {"evidence_ids": ["EV-nvidia-001"], "at": "x"}}):
            with self.subTest(changes=bad):
                self.assert_refused("nvidia", "F4", bad, "재확인")

    def test_unknown_or_unconfirmed_evidence_is_refused(self):
        self.assert_refused("nvidia", "F4", {"reconfirmed": {"evidence_ids": ["EV-nvidia-009"]}}, "evidence.json 에 없음")
        self.put_candidate("EV-nvidia-002")
        self.assert_refused("nvidia", "F4", {"reconfirmed": {"evidence_ids": ["EV-nvidia-002"]}}, "확정되지 않은 근거")

    def test_reconfirm_with_input_change(self):
        self.judge("nvidia", "F5", {"H": -1, **AGAIN})
        new = self.judgment("nvidia", "F5")
        self.assertEqual((new["inputs"]["H"], new["status"], len(new["reconfirmed"])), (-1, "new", 1))

    def test_obsolete_kind_cannot_be_reconfirmed_alone(self):
        """이어받은 ① score 판단은 재확인만으로 새 판단이 되지 않는다 — v2.0 의 새 판단은 네 질문 입력이다."""
        self.judge("nvidia", "F1", {"evidence_up": UP, "evidence_down": DOWN})
        self.assert_refused("nvidia", "F1", AGAIN, "새 판단은 kind")

    def test_unchanged_values_without_reconfirm_still_refused(self):
        self.assert_refused("nvidia", "F5", {"H": self.judgment("nvidia", "F5")["inputs"]["H"]}, "--reconfirm")

    def test_cli_reconfirm(self):
        with human_env():
            out = self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F4", "--reconfirm", "EV-nvidia-001",
                           "--reason", "다시 읽음", "--by", "판단자")
            self.assertIn("재확인", out)
            self.assertIn("재확인", self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F5", "--reconfirm", "",
                                           "--reason", "r", "--by", "판단자", code=1))
        self.assertEqual(self.judgment("nvidia", "F4")["reconfirmed"][0]["evidence_ids"], ["EV-nvidia-001"])
        self.assertEqual(self.judgment("nvidia", "F5")["status"], "carried")


class ProposalReconfirmTest(ReconfirmBase):
    def test_propose_reconfirm_accept_and_undo(self):
        before = self.judgment("nvidia", "F4")
        with human_env():
            self.cli("propose", SLUG, "--company", "nvidia", "--factor", "F4", "--reconfirm", "EV-nvidia-001",
                     "--reason", "다시 읽었으나 같다", "--by", "에이전트")
            self.cli("proposal", SLUG, "--id", "PRP-001", "--accept", "--by", "에이전트")
        new = self.judgment("nvidia", "F4")
        self.assertEqual((new["status"], new["reviewer"], new["score"]), ("new", "에이전트", before["score"]))
        self.assertEqual(new["reconfirmed"][0]["evidence_ids"], ["EV-nvidia-001"])
        self.assertEqual(load_json_strict(self.ppath)["items"][0]["applied"]["after"]["reconfirmed"], new["reconfirmed"])
        stages.undo_proposal(SLUG, "PRP-001", by="에이전트")
        undone = self.judgment("nvidia", "F4")
        self.assertEqual(undone["status"], "carried")
        self.assertNotIn("reconfirmed", undone)

    def test_proposal_refuses_unknown_reconfirm_evidence(self):
        with self.assertRaisesRegex(SchemaError, "evidence.json 에 없음"):
            self.propose(factor="F4", changes={"reconfirmed": {"evidence_ids": ["EV-nvidia-009"]}})
        with self.assertRaisesRegex(SchemaError, "하나 이상"):
            self.propose(factor="F4", changes={"reconfirmed": {"evidence_ids": []}})

    def test_reconfirm_between_propose_and_accept_makes_proposal_stale(self):
        self.propose(factor="F5", changes={"H": -1}, evidence_ids=["EV-nvidia-001"])
        self.judge("nvidia", "F5", AGAIN)
        with self.assertRaisesRegex(SchemaError, "판단이 바뀌었다"):
            self.decide(accept=True, by="에이전트")


class ResearchRejudgeTest(V20Base):
    def test_regular_v20_research_stops_on_carried(self):
        carried = sorted(j["judgment_id"] for j in load_json_strict(self.jpath)["items"]
                         if j["factor"] in ("F1", "F2", "F3", "F4", "F5", "F7", "F8") and j["status"] == "carried")
        with self.assertRaises(SchemaError) as cm:
            stages.research(SLUG)
        msg = str(cm.exception)
        self.assertIn("정기 실행은 정성 판단 전부를 다시 매긴다(rules.md 2.9)", msg)
        self.assertIn(f"{len(carried)}건", msg)
        self.assertIn(carried[0], msg)
        self.assertFalse(run_paths(SLUG).research.is_file())

    def test_research_passes_when_all_rejudged(self):
        rejudge_all(self.jpath)
        path = stages.research(SLUG)
        self.assertTrue(path.is_file())

    def test_calculate_does_not_check_the_policy(self):
        """calculate 자체는 정책을 보지 않는다. research 뒤 승계 판단이 다시 생겨도 계산은 돌고 그 칸은 승계로 나온다.
        (research.md 가 없으면 calculate 는 선행 산출물 검사에서 먼저 멈춘다.)"""
        rejudge_all(self.jpath)
        stages.research(SLUG)
        payload = load_json_strict(self.jpath)
        target = next(j for j in payload["items"] if (j["company_id"], j["factor"]) == ("nvidia", "F4"))
        target.update(status="carried", carried_from="baseline:v1.5")
        write_json(self.jpath, payload)
        results = stages.calculate(SLUG)[2]
        nv = next(c for c in results["companies"] if c["company_id"] == "nvidia")
        self.assertEqual(nv["factors"]["F4"]["status"], "carried_score")


if __name__ == "__main__":
    unittest.main()
