# 판단 변경 제안(propose·proposal): 제안 쓰기, 반영·거부, 거부 사유 필수, 판단이 바뀐 뒤 반영 거부, 에이전트 세션 거부를 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict  # noqa: E402
from tests.test_approval_commands import FlowBase  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402


class ProposalBase(FlowBase):
    @property
    def ppath(self) -> Path:
        return self.paths.proposals

    def judgment(self, company_id: str = "nvidia", factor: str = "F5") -> dict:
        items = load_json_strict(self.box.run_dir / "judgments.json")["items"]
        return next(j for j in items if j["company_id"] == company_id and j["factor"] == factor)

    def propose(self, **kw) -> dict:
        kw.setdefault("company_id", "nvidia")
        kw.setdefault("factor", "F5")
        kw.setdefault("changes", {"H": -1})
        kw.setdefault("reason", "시험 제안")
        kw.setdefault("evidence_ids", ["EV-nvidia-001"])
        return stages.add_proposal(SLUG, **kw)

    def decide(self, pid: str = "PRP-001", **kw) -> dict:
        kw.setdefault("allow_agent_session", True)
        return stages.decide_proposal(SLUG, pid, **kw)


class AddProposalTest(ProposalBase):
    def test_writes_pending_with_snapshot_and_next_id(self):
        before = self.judgment()
        p = self.propose(evidence_after=["새 근거 문장"])
        self.assertEqual((p["proposal_id"], p["status"]), ("PRP-001", "pending"))
        self.assertEqual(p["before"]["inputs"], before["inputs"])
        self.assertEqual(p["before"]["evidence"], before["evidence"])
        self.assertEqual(self.propose(factor="F1", changes={"score": 3})["proposal_id"], "PRP-002")
        self.assertEqual(self.judgment(), before, "제안을 쓰는 것만으로 판단은 바뀌지 않는다")

    def test_refused_inputs(self):
        self.propose()
        cases = (
            (dict(), "결정 전 제안이 이미 있다"),
            (dict(factor="F3", changes={"score": 3}), "점수 칸은 고치지 않는다"),
            (dict(factor="F1", changes={"score": 3}, reason="  "), "사유"),
            (dict(factor="F1", changes={"score": 3}, evidence_ids=["EV-nvidia-009"]), "evidence.json 에 없는"),
            (dict(factor="F1", changes={}), "고칠 값"),
        )
        for kw, pattern in cases:
            with self.subTest(kw=kw), self.assertRaisesRegex(SchemaError, pattern):
                self.propose(**kw)

    def test_proposals_are_outside_the_input_hashes(self):
        hashes = stages.current_hashes(SLUG)
        self.propose()
        self.assertEqual(stages.current_hashes(SLUG), hashes)


class DecideProposalTest(ProposalBase):
    def test_accept_revises_judgment_and_cites_evidence(self):
        stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="사용자")
        self.propose(evidence_after=["적대 등급은 비용형이다(EV-nvidia-001)"])
        with human_env():
            out = self.decide(accept=True, by="사용자", note="원문 확인")
        j = self.judgment()
        self.assertEqual((j["inputs"]["H"], j["status"], j["reviewer"]), (-1, "new", "사용자"))
        self.assertEqual(j["evidence"], ["적대 등급은 비용형이다(EV-nvidia-001)"])
        self.assertIn("EV-nvidia-001", j["evidence_ids"])
        self.assertIn("제안 PRP-001 반영", j["revision_history"][-1]["reason"])
        self.assertEqual(j["revision_history"][-1]["session"], "human")
        p = load_json_strict(self.ppath)["items"][0]
        self.assertEqual((p["status"], p["decided_by"], p["decision_note"]), ("accepted", "사용자", "원문 확인"))
        self.assertTrue(out["accepted"])
        engine.load_context(SLUG)

    def test_reject_needs_a_reason_and_keeps_the_judgment(self):
        self.propose()
        before_file, before_j = self.ppath.read_bytes(), self.judgment()
        for note in (None, "  "):
            with self.subTest(note=note), self.assertRaisesRegex(SchemaError, "거부 사유"):
                self.decide(accept=False, note=note)
        self.assertEqual(self.ppath.read_bytes(), before_file)
        self.decide(accept=False, by="사용자", note="고객이 경쟁자라는 사실은 그대로다")
        p = load_json_strict(self.ppath)["items"][0]
        self.assertEqual((p["status"], p["decision_note"]), ("rejected", "고객이 경쟁자라는 사실은 그대로다"))
        self.assertEqual(self.judgment(), before_j)
        with self.assertRaisesRegex(SchemaError, "이미 결정됐다"):
            self.decide(accept=True)

    def test_stale_proposal_is_refused(self):
        self.propose()
        stages.revise_judgment(SLUG, company_id="nvidia", factor="F5", changes={"A": 2}, reason="사람이 직접 고침", by="사용자")
        self.assertTrue(stages.summary(SLUG)["proposals"][0]["stale"])
        with self.assertRaisesRegex(SchemaError, "판단이 바뀌었다"):
            self.decide(accept=True)

    def test_unconfirmed_citation_is_refused_and_restored(self):
        self.propose()   # EV-nvidia-001 은 아직 candidate
        before = (self.box.run_dir / "judgments.json").read_bytes()
        with self.assertRaisesRegex(SchemaError, "확정되지 않은 근거"):
            self.decide(accept=True)
        self.assertEqual((self.box.run_dir / "judgments.json").read_bytes(), before)
        self.assertEqual(load_json_strict(self.ppath)["items"][0]["status"], "pending")

    def test_agent_session_cannot_decide(self):
        self.propose()
        with human_env(CLAUDECODE="1"), self.assertRaisesRegex(SchemaError, "에이전트 세션"):
            stages.decide_proposal(SLUG, "PRP-001", accept=False, note="사유")


class ProposalCliTest(ProposalBase):
    def test_propose_and_reject_via_cli(self):
        with human_env(CLAUDECODE="1"):   # 에이전트도 제안은 쓴다
            out = self.cli("propose", SLUG, "--company", "nvidia", "--factor", "F5", "--set", "H=-1",
                           "--evidence", "새 근거", "--reason", "시험", "--cite", "EV-nvidia-001")
        self.assertIn("PRP-001", out)
        with human_env(CLAUDECODE="1"):
            self.assertIn("에이전트 세션", self.cli("proposal", SLUG, "--id", "PRP-001", "--reject", "--note", "x", code=1))
        with human_env():
            self.assertIn("거부 사유", self.cli("proposal", SLUG, "--id", "PRP-001", "--reject", code=1))
            self.assertIn("거부", self.cli("proposal", SLUG, "--id", "PRP-001", "--reject", "--note", "근거 부족", "--by", "사용자"))
        p = json.loads(self.ppath.read_text(encoding="utf-8"))["items"][0]
        self.assertEqual((p["status"], p["changes"], p["evidence_after"]), ("rejected", {"H": -1}, ["새 근거"]))


if __name__ == "__main__":
    unittest.main()
