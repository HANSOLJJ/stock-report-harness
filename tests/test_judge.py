# 판단 수정(judge): 판정 종류별 수정과 거부, revision_history 보존, 해시·승인 무효, 수정한 판단으로 calculate 가 새 점수를 내는지를 잠근다
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

DAY = "2026-10-01"


class JudgeBase(FlowBase):
    @property
    def jpath(self) -> Path:
        return self.box.run_dir / "judgments.json"

    def item(self, company_id: str, factor: str) -> dict:
        return next(j for j in load_json_strict(self.jpath)["items"] if j["company_id"] == company_id and j["factor"] == factor)

    def judge(self, company_id: str, factor: str, changes: dict, **kw) -> dict:
        kw.setdefault("reason", "시험 수정")
        kw.setdefault("by", "사용자")
        kw.setdefault("revised_at", DAY)
        return stages.revise_judgment(SLUG, company_id=company_id, factor=factor, changes=changes, **kw)

    def assert_refused(self, company_id: str, factor: str, changes: dict, pattern: str, **kw) -> None:
        before = self.jpath.read_bytes()
        with self.assertRaisesRegex(SchemaError, pattern):
            self.judge(company_id, factor, changes, **kw)
        self.assertEqual(self.jpath.read_bytes(), before, "거부되면 judgments.json 은 한 바이트도 바뀌지 않는다")


class EditKindsTest(JudgeBase):
    def test_score_and_evidence_for_f1_f4_f8(self):
        old = self.item("nvidia", "F1")
        out = self.judge("nvidia", "F1", {"score": 3, "evidence": ["CUDA 개발자 생태계가 업무 채널로 자리 잡았다"]})
        new = self.item("nvidia", "F1")
        self.assertEqual((new["kind"], new["score"], new["evidence"]), ("score", 3, ["CUDA 개발자 생태계가 업무 채널로 자리 잡았다"]))
        self.assertEqual((new["status"], new["reviewer"], new["reviewed_at"]), ("new", "사용자", DAY))
        self.assertEqual(new["carried_from"], old["carried_from"])   # 출처는 지우지 않는다
        self.assertEqual(out["previous"]["score"], old["score"])
        for factor, score in (("F4", 1), ("F8", -2)):
            with self.subTest(factor=factor):
                self.judge("nvidia", factor, {"score": score})
                self.assertEqual(self.item("nvidia", factor)["score"], score)

    def test_criteria_grade_matrix_gate_inputs(self):
        cases = (("F3", {"imitation": "pass"}), ("F5", {"A": 2, "H": -1}),
                 ("F7", {"own_money_returns": "no"}), ("F9", {"coverage_comparable": "yes", "fcf_trend": "deteriorating"}))
        for factor, changes in cases:
            with self.subTest(factor=factor):
                old = self.item("nvidia", factor)
                self.judge("nvidia", factor, changes)
                new = self.item("nvidia", factor)
                self.assertEqual(new["kind"], old["kind"])
                self.assertIsNone(new["score"])
                self.assertEqual(new["inputs"], {**old["inputs"], **changes})   # 준 키만 바뀐다
                self.assertEqual(new["evidence"], old["evidence"])

    def test_carried_score_f7_becomes_matrix(self):
        self.assertEqual(self.item("openai", "F7")["kind"], "score")
        self.assert_refused("openai", "F7", {"own_money_returns": "no"}, "funding_dependent_share")   # 키가 다 있어야 한다
        self.judge("openai", "F7", {"funding_dependent_share": "large", "own_money_returns": "no"})
        new = self.item("openai", "F7")
        self.assertEqual((new["kind"], new["score"]), ("matrix", None))
        self.assertEqual(new["revision_history"][0]["previous"]["kind"], "score")


class RefusalTest(JudgeBase):
    def test_score_cell_of_rule_computed_factors_is_refused(self):
        for factor, changes in (("F3", {"score": 3}), ("F5", {"score": 2}), ("F7", {"score": 1}), ("F9", {"score": 0})):
            with self.subTest(factor=factor):
                self.assert_refused("nvidia", factor, changes, "점수 칸은 고치지 않는다")

    def test_factors_outside_scope_are_refused(self):
        self.assert_refused("nvidia", "F2", {"score": 4}, "고치지 않는다")
        self.assert_refused("openai", "F6", {"score": 1}, "고치지 않는다")

    def test_bad_values_write_nothing(self):
        cases = (("F1", {"score": 9}, "범위"), ("F1", {"score": "높음"}, "정수"), ("F5", {"A": 5}, "A 는"),
                 ("F3", {"imitation": "yes"}, "imitation"), ("F9", {"fcf_trend": "up"}, "fcf_trend"),
                 ("F3", {"moat": "pass"}, "고칠 수 없는 키"), ("F1", {"evidence": []}, "evidence"),
                 ("F1", {"evidence": ["  "]}, "evidence"))
        for factor, changes, pattern in cases:
            with self.subTest(factor=factor, changes=changes):
                self.assert_refused("nvidia", factor, changes, pattern)

    def test_reason_by_change_and_target_required(self):
        self.assert_refused("nvidia", "F1", {"score": 3}, "사유", reason="  ")
        self.assert_refused("nvidia", "F1", {"score": 3}, "수정자", by="")
        self.assert_refused("nvidia", "F1", {}, "고칠 값")
        self.assert_refused("nvidia", "F1", {"score": self.item("nvidia", "F1")["score"]}, "바뀐 값이 없다")
        self.assert_refused("tsmc", "F1", {"score": 3}, "판단이 없다")   # 실행에 없는 기업

    def test_unconfirmed_evidence_citation_restores_the_file(self):
        """새 판단은 확정 근거만 인용한다. 교차 참조가 막으면 쓴 파일을 되돌린다."""
        payload = load_json_strict(self.jpath)
        for j in payload["items"]:
            if (j["company_id"], j["factor"]) == ("nvidia", "F1"):
                j["evidence_ids"] = ["EV-nvidia-001"]   # 승계 판단은 후보를 인용해도 된다
        self.jpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        self.assert_refused("nvidia", "F1", {"score": 3}, "확정되지 않은 근거")
        stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="사용자")
        self.judge("nvidia", "F1", {"score": 3})
        self.assertEqual(self.item("nvidia", "F1")["status"], "new")


class HistoryAndHashTest(JudgeBase):
    def test_revision_history_keeps_every_previous_value(self):
        first = self.item("nvidia", "F5")
        self.judge("nvidia", "F5", {"A": 2}, reason="첫 수정", by="갑")
        self.judge("nvidia", "F5", {"H": 0, "evidence": ["정부 계약이 아군 신호다"]}, reason="둘째 수정", by="을", revised_at="2026-10-02")
        hist = self.item("nvidia", "F5")["revision_history"]
        self.assertEqual([(h["revised_by"], h["reason"], h["revised_at"]) for h in hist],
                         [("갑", "첫 수정", DAY), ("을", "둘째 수정", "2026-10-02")])
        self.assertEqual(hist[0]["previous"], {k: first[k] for k in ("kind", "score", "inputs", "evidence", "status", "reviewer", "reviewed_at")})
        self.assertEqual((hist[1]["previous"]["inputs"]["A"], hist[1]["previous"]["status"], hist[1]["previous"]["reviewer"]), (2, "new", "갑"))
        self.assertEqual(hist[1]["previous"]["evidence"], first["evidence"])

    def test_bad_revision_history_is_rejected_by_schema(self):
        payload = load_json_strict(self.jpath)
        payload["items"][0]["revision_history"] = [{"revised_at": DAY, "revised_by": "갑", "reason": "", "previous": {}}]
        self.jpath.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(SchemaError, "revision_history"):
            engine.load_context(SLUG)

    def test_only_judgments_hash_moves_and_approval_becomes_invalid(self):
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)
        before = stages.current_hashes(SLUG)
        with human_env():   # 유효 승인 실행의 판단 수정은 승인 페이지(사람 세션)만 한다(2026-10-01 레인 N, V2-1)
            out = self.judge("nvidia", "F3", {"imitation": "pass"})
        after = stages.current_hashes(SLUG)
        self.assertEqual(sorted(k for k in before if before[k] != after.get(k)), ["judgments"])
        self.assertEqual(out["judgments_hash"], after["judgments"])
        self.assertFalse(stages.summary(SLUG)["approval"]["valid"])
        self.assertTrue(self.approval_path.exists())   # 승인 파일은 지우지 않는다. 무효일 뿐이다

    def test_calculate_scores_the_revised_judgment(self):
        self.ready()
        old = stages.calculate(SLUG)[2]
        nv = lambda r: next(c for c in r["companies"] if c["company_id"] == "nvidia")  # noqa: E731
        self.assertEqual((nv(old)["factors"]["F1"]["score"], nv(old)["factors"]["F1"]["status"]), (2, "carried_score"))
        self.judge("nvidia", "F1", {"score": 1})   # nvidia 는 부품형이라 F1 상한 2
        self.judge("nvidia", "F5", {"A": 0, "H": -3})
        new = stages.calculate(SLUG)[2]
        self.assertEqual((nv(new)["factors"]["F1"]["score"], nv(new)["factors"]["F1"]["status"]), (1, "ok"))
        self.assertNotEqual(nv(new)["factors"]["F5"]["score"], nv(old)["factors"]["F5"]["score"])
        self.assertNotEqual(new["results_hash"], old["results_hash"])
        with self.assertRaisesRegex(SchemaError, "calculate 를 다시"):   # 판단이 바뀐 뒤 옛 결과로 draft 를 만들지 않는다
            self.judge("nvidia", "F4", {"score": 1})
            stages.draft(SLUG)


class SummaryJudgmentsTest(JudgeBase):
    def test_lists_every_judgment_with_inputs_as_pairs(self):
        self.judge("nvidia", "F3", {"imitation": "pass"})
        rows = stages.summary(SLUG)["judgments"]
        self.assertEqual(len(rows), len(load_json_strict(self.jpath)["items"]))
        f3 = next(r for r in rows if (r["company_id"], r["factor"]) == ("nvidia", "F3"))
        self.assertEqual((f3["kind"], f3["edit_kind"], f3["status"], f3["revisions"], f3["display_name"]),
                         ("criteria", "criteria", "new", 1, "NVIDIA"))
        self.assertIn({"key": "imitation", "value": "pass"}, f3["inputs"])
        f2 = next(r for r in rows if (r["company_id"], r["factor"]) == ("nvidia", "F2"))
        self.assertIsNone(f2["edit_kind"])
        self.assertEqual(stages.summary(SLUG)["judgment_choices"]["grade"], {"A": [0, 1, 2], "H": [0, -1, -2, -3]})


class JudgeCliTest(JudgeBase):
    def test_set_evidence_and_json(self):
        with human_env():
            out = self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F5", "--set", "A=2", "--set", "H=-1",
                           "--evidence", "-로 시작하는 근거도 받는다", "--evidence=둘째 근거", "--reason", "CLI 시험", "--by", "사용자")
        self.assertIn("research → calculate → draft → review", out)
        new = self.item("nvidia", "F5")
        self.assertEqual((new["inputs"]["A"], new["inputs"]["H"], new["evidence"]), (2, -1, ["-로 시작하는 근거도 받는다", "둘째 근거"]))
        payload = self.box.dir / "changes.json"
        payload.write_text(json.dumps({"door_closed": "pass", "evidence": ["파일로 준 근거"]}, ensure_ascii=False), encoding="utf-8")
        with human_env():
            self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F3", "--json", payload, "--reason", "파일", "--by", "사용자")
        self.assertEqual(self.item("nvidia", "F3")["inputs"]["door_closed"], "pass")

    def test_cli_errors_exit_1(self):
        with human_env():
            self.assertIn("점수 칸", self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F3", "--set", "score=3",
                                            "--reason", "r", "--by", "u", code=1))
            self.assertIn("key=value", self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F3", "--set", "imitation",
                                                "--reason", "r", "--by", "u", code=1))

    def test_lock_is_checked_only_in_agent_sessions(self):
        lock = stages.lock_path(SLUG)
        lock.write_text(json.dumps({"owner": "other", "started_utc": "2026-09-30T00:00:00Z", "stage": "draft"}), encoding="utf-8")
        before = lock.read_bytes()
        args = ("judge", SLUG, "--company", "nvidia", "--factor", "F1", "--set", "score=3", "--reason", "r", "--by", "사용자")
        with human_env(SCORECARD_AGENT="human"):   # 승인 페이지(사람 셸)의 judge 는 잠금과 무관하다
            self.cli(*args)
        self.assertEqual(lock.read_bytes(), before)
        with human_env(CLAUDECODE="1", SCORECARD_AGENT="me"):
            self.assertIn("--take-lock", self.cli(*args[:7], "score=4", *args[8:], code=1))
            self.cli(*args[:7], "score=4", *args[8:], "--take-lock")
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8"))["owner"], "me")
        self.assertEqual(self.item("nvidia", "F1")["reviewer"], "사용자")   # reviewer 는 --by 다


if __name__ == "__main__":
    unittest.main()
