# 완결된 문장 원칙(2026-10-06 사용자 지시): 기업 요약 제안(SUMMARY)의 반영·번복·카드 표시, 일괄 반영, 검증기의 금지 표기 검사를 잠근다
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict  # noqa: E402
from scorecard.validate import self_contained_violations  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_proposals import ProposalBase  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402


class SummaryProposalTest(ProposalBase):
    def summaries(self) -> list[dict]:
        return load_json_strict(self.box.run_dir / "judgments.json").get("company_summaries") or []

    def propose_summary(self, text: str = "NVIDIA 는 데이터센터 GPU 와 소프트웨어 생태계로 AI 학습 시장의 기본값이다.", **kw) -> dict:
        return stages.add_proposal(SLUG, company_id="nvidia", factor="SUMMARY", evidence_after=[text],
                                   reason=kw.pop("reason", "현재 상태 요약"), **kw)

    def test_accept_writes_summary_and_context_reads_it(self):
        p = self.propose_summary()
        self.assertEqual(p["before"]["evidence"], [])
        with human_env():
            self.decide(p["proposal_id"], accept=True, by="사용자")
        s = self.summaries()
        self.assertEqual([(x["company_id"], x["text"], x["reviewer"]) for x in s],
                         [("nvidia", "NVIDIA 는 데이터센터 GPU 와 소프트웨어 생태계로 AI 학습 시장의 기본값이다.", "사용자")])
        self.assertEqual(engine.load_context(SLUG).company_summaries["nvidia"]["text"], s[0]["text"])

    def test_second_summary_keeps_history_and_undo_restores(self):
        with human_env():
            self.decide(self.propose_summary("첫 요약 문장이다.")["proposal_id"], accept=True, by="사용자")
            pid = self.propose_summary("둘째 요약 문장이다.")["proposal_id"]
            self.decide(pid, accept=True, by="사용자")
            s = self.summaries()[0]
            self.assertEqual(s["text"], "둘째 요약 문장이다.")
            self.assertEqual(s["revision_history"][-1]["previous"], "첫 요약 문장이다.")
            stages.undo_proposal(SLUG, pid, by="사용자", allow_agent_session=True)
        self.assertEqual(self.summaries()[0]["text"], "첫 요약 문장이다.")

    def test_undo_first_summary_removes_it(self):
        with human_env():
            pid = self.propose_summary()["proposal_id"]
            self.decide(pid, accept=True, by="사용자")
            stages.undo_proposal(SLUG, pid, by="사용자", allow_agent_session=True)
        self.assertEqual(self.summaries(), [])

    def test_refused_shapes(self):
        for kw, pattern in (
            (dict(company_id="nvidia", factor="SUMMARY", evidence_after=["한 문장.", "두 문장."], reason="r"), "요약 문장 하나"),
            (dict(company_id="nvidia", factor="SUMMARY", changes={"score": 3}, evidence_after=["한 문장."], reason="r"), "요약 문장 하나"),
            (dict(company_id="nobody", factor="SUMMARY", evidence_after=["한 문장."], reason="r"), "알 수 없는 company_id"),
        ):
            with self.subTest(kw=kw), self.assertRaisesRegex(SchemaError, pattern):
                stages.add_proposal(SLUG, **kw)

    def test_draft_card_uses_summary_not_baseline(self):
        with human_env():
            self.decide(self.propose_summary()["proposal_id"], accept=True, by="사용자")
        self.ready()
        draft = self.paths.draft.read_text(encoding="utf-8")
        self.assertIn("> NVIDIA 는 데이터센터 GPU 와 소프트웨어 생태계로 AI 학습 시장의 기본값이다.", draft)
        self.assertNotIn("한 줄 요약(과거 기록)", draft)

    def test_all_pending_accepts_everything(self):
        stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="사용자")   # 판단 제안이 인용하는 근거는 확정 근거여야 한다
        self.propose_summary()
        self.propose(evidence_after=["적대 등급은 비용형이다."])
        with human_env():
            self.cli("proposal", SLUG, "--all-pending", "--accept", "--by", "사용자")
        statuses = [p["status"] for p in load_json_strict(self.ppath)["items"]]
        self.assertEqual(statuses, ["accepted", "accepted"])
        self.assertTrue(self.summaries())


class EvidenceOnlyRevisionTest(ProposalBase):
    """근거 문장만 바꾸는 제안은 판정 종류·점수·판정 재료·상태·검토자를 건드리지 않는다(승계는 승계로 남는다). ②·⑥ 도 대상이다."""

    def test_carried_f2_and_f1_stay_carried(self):
        for factor in ("F2", "F1"):
            with self.subTest(factor=factor):
                before = self.judgment(factor=factor)
                self.assertEqual(before["status"], "carried")
                p = stages.add_proposal(SLUG, company_id="nvidia", factor=factor,
                                        evidence_after=[f"NVIDIA {factor} 근거를 완결된 현재 상태 문장으로 다시 썼다."], reason="문장 정리")
                with human_env():
                    self.decide(p["proposal_id"], accept=True, by="사용자")
                after = self.judgment(factor=factor)
                for key in ("kind", "score", "inputs", "status", "reviewer", "reviewed_at"):
                    self.assertEqual(after.get(key), before.get(key), key)
                self.assertEqual(after["evidence"], [f"NVIDIA {factor} 근거를 완결된 현재 상태 문장으로 다시 썼다."])
                self.assertEqual(after["revision_history"][-1]["previous"]["evidence"], before["evidence"])

    def test_f2_cannot_change_score(self):
        with self.assertRaisesRegex(SchemaError, "고치지 않는다"):
            stages.add_proposal(SLUG, company_id="nvidia", factor="F2", changes={"score": 3}, reason="r")


class ValidatorTest(unittest.TestCase):
    def ctx(self, **kw) -> SimpleNamespace:
        base = dict(judgments=[], company_summaries={}, evidence=[], triggers=[])
        base.update(kw)
        return SimpleNamespace(**base)

    def test_clean_text_passes(self):
        ctx = self.ctx(
            judgments=[{"judgment_id": "nvidia.F5", "evidence": ["NVIDIA 는 Mistral 과 기초 모델을 공동 개발한다."]}],
            company_summaries={"nvidia": {"text": "NVIDIA 는 AI 학습 시장의 기본값이다."}},
            triggers=[{"trigger_id": "TRG-001", "observation": "3분기 실적이 10월 15일에 나온다.", "condition": "실적이 나오면",
                       "recheck": {"what": "매출 성장"}, "carry": {"finding": "TRG-017 로 이었다(감사 기록이라 검사하지 않는다)"}}])
        self.assertEqual(self_contained_violations(ctx), [])

    def test_banned_markers_are_caught_everywhere(self):
        ctx = self.ctx(
            judgments=[{"judgment_id": "nvidia.F5", "evidence": ["(v1.5: 📈 1→2 — 별표 G 동맹등급) 근거", "~~옛 문장~~ (superseded [FIX-54 1단계])"]}],
            company_summaries={"nvidia": {"text": "기준선 원문은 다르게 적었다."}},
            evidence=[{"evidence_id": "EV-1", "relevance": "시험 실행에서 미확인으로 적었다", "conditional_impact": "지금은 유지:",
                       "counter_evidence": ["obsreg 리뷰가 지적했다"], "unverified": []}],
            triggers=[{"trigger_id": "TRG-002", "observation": "기준선 트리거 TRIG-005 를 흡수했다", "condition": "TRG-034 가 관찰한다",
                       "recheck": {"what": "위 줄 참조"}}])
        found = self_contained_violations(ctx)
        joined = "\n".join(found)
        for why in ("규칙 버전 표기", "변경 표시 기호", "폐지된 별표 이름", "취소선", "대체 표시", "작업 번호",
                    "다른 판·다른 문장 참조", "다른 트리거 참조"):
            with self.subTest(why=why):
                self.assertIn(why, joined)
        for where in ("nvidia.F5 근거[0]", "nvidia 기업 요약", "EV-1.relevance", "EV-1.counter_evidence[0]",
                      "TRG-002.observation", "TRG-002.condition", "TRG-002.recheck.what"):
            with self.subTest(where=where):
                self.assertIn(where, joined)

    def test_old_rule_runs_are_not_checked(self):
        """규칙 v1.9 미만 승인 실행은 그때 문면 그대로 둔다(검증기는 v1.9 이상에만 댄다)."""
        from scorecard.validate import SELF_CONTAINED_MIN_RULE, _rule_at_least
        self.assertFalse(_rule_at_least("v1.8", SELF_CONTAINED_MIN_RULE))
        self.assertTrue(_rule_at_least("v1.9", SELF_CONTAINED_MIN_RULE))
        self.assertTrue(_rule_at_least("v1.10", SELF_CONTAINED_MIN_RULE))


if __name__ == "__main__":
    unittest.main()
