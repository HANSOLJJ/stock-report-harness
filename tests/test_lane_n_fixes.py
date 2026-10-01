# 레인 N(재검증 V2-1~V2-3) 수정을 잠근다: 승인 파일 이름·approval_id 재계산, 승인 실행 보호, 이어받기의 근거·트리거
from __future__ import annotations

import inspect
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_approval_commands import EXISTING, NOW, ROOT, SLUG, FlowBase
from tests.test_collect_stage import RSS
from tests.test_hooks import guard, shell
from tests.test_run_lock import human_env
import scorecard_cli
from scorecard import engine, stages
from scorecard.schema import SchemaError, approval_file_present, approval_id_for, load_json_strict, validate_approval, write_json


def rename_case(path, new_name: str) -> None:
    """Windows 는 대소문자만 다른 이름으로 바로 바꾸지 못할 때가 있어 두 번 옮긴다."""
    tmp = path.with_name(path.name + ".tmp")
    os.replace(path, tmp)
    os.replace(tmp, path.with_name(new_name))


class ApprovalFileNameTest(FlowBase):
    """V2-3. 승인은 이름이 정확히 approval.json 인 파일만이고, approval_id 는 다시 계산해 대조한다."""

    def setUp(self) -> None:
        super().setUp()
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)

    def test_case_variant_file_is_not_an_approval(self):
        rename_case(self.approval_path, "Approval.json")
        self.assertFalse(approval_file_present(self.box.run_dir))
        with self.assertRaisesRegex(SchemaError, "정확히 approval.json"):
            load_json_strict(self.approval_path)
        self.assertFalse(stages.status(SLUG)["approval"])
        self.assertEqual(stages.summary(SLUG)["approval"]["exists"], False)
        with self.assertRaises(SchemaError):
            stages.revoke(SLUG, by="user", note="x", allow_agent_session=True)

    def test_arbitrary_approval_id_is_rejected(self):
        approval = load_json_strict(self.approval_path)
        self.assertEqual(approval["approval_id"], approval_id_for(SLUG, approval["hashes"]))
        write_json(self.approval_path, {**approval, "approval_id": "0000000000000000"})
        with self.assertRaisesRegex(SchemaError, "다시 계산한 값"):
            validate_approval(load_json_strict(self.approval_path), SLUG)
        self.assertFalse(stages.status(SLUG)["approval_valid"])
        self.assertFalse(stages.summary(SLUG)["approval"]["valid"])


class ApprovedRunStageTest(FlowBase):
    """V2-1. 유효 승인 실행의 입력·산출물을 바꾸는 단계는 에이전트 세션이면 거부하고, 사람 세션은 경고 뒤 진행한다."""

    def setUp(self) -> None:
        super().setUp()
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)
        self.review_text = self.paths.review.read_text(encoding="utf-8")

    def snapshot(self) -> dict:
        return {p.name: p.read_bytes() for p in self.box.run_dir.rglob("*") if p.is_file() and p.name != ".lock"}

    def test_agent_session_refuses_every_changing_stage(self):
        prices = self.box.dir / "quotes.json"
        prices.write_text("{}", encoding="utf-8")
        calls = {
            "judge": lambda: stages.revise_judgment(SLUG, company_id="nvidia", factor="F1", changes={"score": 1}, reason="r", by="u"),
            "confirm": lambda: stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="u"),
            "calculate": lambda: stages.calculate(SLUG),
            "draft": lambda: stages.draft(SLUG),
            "research": lambda: stages.research(SLUG),
            "review_template": lambda: stages.review_template(SLUG, force=True),
            "collect prices": lambda: stages.collect(SLUG, kinds=("prices",), from_file=str(prices)),
            "init --force": lambda: stages.init_run(SLUG, as_of="2026-09-29", title="t", request="r", companies=["nvidia"],
                                                    rule_version="v1.8", force=True),
        }
        before = self.snapshot()
        for name, call in calls.items():
            with self.subTest(stage=name), human_env(CLAUDECODE="1"):
                with self.assertRaisesRegex(SchemaError, "에이전트 세션\\(CLAUDECODE\\).*승인 기록이 지워진다"):
                    call()
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(stages.status(SLUG)["approval_valid"])

    def test_agent_session_may_run_what_does_not_touch_approved_files(self):
        with human_env(CLAUDECODE="1"):
            stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
            stages.collect(SLUG, kinds=("prices",), dry_run=True)
            stages.summary(SLUG)
            stages.status(SLUG)
        self.assertTrue(stages.status(SLUG)["approval_valid"])

    def test_human_judge_then_agent_rerun_cleans_invalid_approval_with_record(self):
        with human_env():
            out = self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F1", "--set", "score=1", "--reason", "r", "--by", "사람")
        self.assertIn("[경고] 승인이 유효한 실행", out)
        self.assertFalse(stages.status(SLUG)["approval_valid"])
        # 승인이 무효가 된 뒤에는 에이전트가 research → calculate → draft → review 를 다시 돌린다.
        with human_env(CLAUDECODE="1", SCORECARD_AGENT="me"):
            self.cli("research", SLUG, "--take-lock")
            out = self.cli("calculate", SLUG)
            self.cli("draft", SLUG)
        self.assertIn("[알림] 재계산 결과 해시가 승인과 달라 approval.json 을 지웠다", out)
        self.assertFalse(approval_file_present(self.box.run_dir))
        lines = (self.box.run_dir / "revocations.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertEqual(entry["revoked_by"], "calculate")
        self.assertTrue(entry["note"].startswith("무효 승인 정리"), entry["note"])
        self.assertEqual(sorted(entry), ["approval_id", "hashes", "note", "revoked_at", "revoked_by"])

    def test_human_session_warns_and_runs(self):
        with human_env():
            out = self.cli("draft", SLUG)
        self.assertIn("[경고] 승인이 유효한 실행", out)
        self.assertTrue(stages.status(SLUG)["approval_valid"])   # 같은 입력이면 같은 초안이라 승인이 그대로 유효하다

    def test_baseline_consumers(self):
        with human_env(CLAUDECODE="1"):
            with self.assertRaisesRegex(SchemaError, "에이전트 세션.*기준선 v1.5"):
                stages.protect_baseline_consumers("v1.5")
            self.assertEqual(stages.protect_baseline_consumers("v9.9"), [])
        with human_env():
            self.assertEqual(stages.protect_baseline_consumers("v1.5"), [SLUG])
        self.assertIn("protect_baseline_consumers", inspect.getsource(scorecard_cli.cmd_import_baseline))


class HookStageCommandTest(unittest.TestCase):
    """V2-1. 훅은 단계 명령이 유효 승인 실행을 가리키면 막는다. 맨 실행 이름도 폴더로 푼다."""

    CLI = "uv run --frozen python -X utf8 scripts/scorecard_cli.py"

    def kind(self, cmd: str, tool: str = "Bash", root=ROOT):
        return guard.protect_sensitive_files(shell(tool, cmd), root=root)

    def test_changing_stages_on_existing_runs_blocked(self):
        for slug in EXISTING:
            for args in (f"judge {slug} --company nvidia --factor F1 --set score=5 --reason x --by y", f"calculate {slug}",
                         f"draft {slug}", f"research {slug}", f"review-template {slug} --force", f"review-template {slug} --fo",
                         f"confirm {slug} --evidence EV-nvidia-001", f"collect {slug}", f"collect {slug} --kind prices",
                         f"collect {slug} --k=all", f"calculate {slug}/"):
                for tool in ("Bash", "PowerShell"):
                    with self.subTest(args=args, tool=tool):
                        d = self.kind(f"{self.CLI} {args}", tool)
                        self.assertEqual(d.kind, "block")
                        self.assertIn("승인이 유효한 실행", d.text)
        self.assertEqual(self.kind(f"python scripts\\scorecard_cli.py calculate {EXISTING[0]}", "PowerShell").kind, "block")

    def test_reading_or_unrelated_stage_commands_pass(self):
        for slug in EXISTING:
            for args in (f"status {slug}", f"summary {slug} --json", f"diff {slug} --against {EXISTING[0]}",
                         f"collect {slug} --kind news", f"collect {slug} --dry-run", f"review-template {slug}",
                         "calculate ai-scorecard-2026-10-absent"):
                with self.subTest(args=args):
                    self.assertEqual(self.kind(f"{self.CLI} {args}").kind, "allow")

    def test_import_baseline_always_blocked(self):
        for tool in ("Bash", "PowerShell"):
            self.assertEqual(self.kind(f"{self.CLI} import-baseline", tool).kind, "block")
            self.assertEqual(self.kind(f"{self.CLI} import-baseline --html a.html --md a.md", tool).kind, "block")

    def test_undecidable_validity_blocks_inside_the_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "output" / "ai-scorecard-2026-10-x").mkdir(parents=True)
            (root / "output" / "ai-scorecard-2026-10-x" / "approval.json").write_text("{}", encoding="utf-8")
            d = self.kind(f"{self.CLI} calculate ai-scorecard-2026-10-x", root=root)
            self.assertEqual(d.kind, "block")
            self.assertIn("판정하지 못함", d.text)
        with mock.patch.object(guard, "_approval_is_valid", side_effect=ValueError("boom")):
            d = self.kind(f"{self.CLI} calculate {EXISTING[1]}")
        self.assertEqual((d.kind, "boom" in d.text), ("block", True))

    def test_main_returns_block_exit_code_when_validity_fails(self):
        with mock.patch.object(guard, "_approval_is_valid", side_effect=RuntimeError("boom")):
            out = io.StringIO()
            code = guard.main(["protect_sensitive_files"], stdin=io.StringIO(json.dumps(shell("Bash", f"{self.CLI} draft {EXISTING[0]}"))),
                              stdout=out, root=ROOT)
        self.assertEqual(code, 2)


class HookInvalidApprovalTest(FlowBase):
    """V2-1. 무효 승인(사람이 판단을 고친 뒤)은 훅도 막지 않는다. 유효하면 막는다."""

    def test_valid_blocks_invalid_passes(self):
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)
        root = self.box.dir
        cmd = f"uv run python scripts/scorecard_cli.py calculate {SLUG}"
        self.assertEqual(guard.protect_sensitive_files(shell("Bash", cmd), root=root).kind, "block")
        with human_env():
            stages.revise_judgment(SLUG, company_id="nvidia", factor="F1", changes={"score": 1}, reason="r", by="사람")
        self.assertEqual(guard.protect_sensitive_files(shell("Bash", cmd), root=root).kind, "allow")


class ContinueWithEvidenceTest(FlowBase):
    """V2-2. 근거를 인용한 판단이 있는 실행을 init --from-run 으로 이어받으면 근거·트리거도 옮겨져 다음 실행이 돈다."""

    NEW = "ai-scorecard-2026-10-continued"

    def setUp(self) -> None:
        super().setUp()
        self.write_evidence(self.evidence_item("EV-nvidia-002", title="인용되지 않은 근거"))
        stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="사람")
        jp = self.box.run_dir / "judgments.json"
        payload = load_json_strict(jp)
        for j in payload["items"]:
            if (j["company_id"], j["factor"]) == ("nvidia", "F1"):
                j["evidence_ids"] = ["EV-nvidia-001"]
        write_json(jp, payload)
        stages.revise_judgment(SLUG, company_id="nvidia", factor="F1", changes={"score": 1}, reason="근거 반영", by="사람")
        stages.load_context(SLUG)

    def test_cited_evidence_and_triggers_move_and_next_run_proceeds(self):
        out = stages.init_run(self.NEW, from_run=SLUG, title="이어받기")
        self.assertEqual(sorted(out), ["evidence", "judgments", "observations", "plan", "run", "sources", "triggers"])
        new = engine.run_dir(self.NEW)
        ev = load_json_strict(new / "evidence" / "evidence.json")
        self.assertEqual(ev["run_id"], self.NEW)
        self.assertEqual([(e["evidence_id"], e["status"]) for e in ev["items"]], [("EV-nvidia-001", "confirmed")])
        trg = load_json_strict(new / "triggers.json")
        self.assertEqual((trg["run_id"], [t["trigger_id"] for t in trg["items"]]), (self.NEW, ["TRG-001"]))
        nv = next(j for j in load_json_strict(new / "judgments.json")["items"] if (j["company_id"], j["factor"]) == ("nvidia", "F1"))
        self.assertEqual((nv["score"], nv["evidence_ids"], len(nv["revision_history"])), (1, ["EV-nvidia-001"], 1))
        stages.research(self.NEW)
        results = stages.calculate(self.NEW)[2]
        f1 = next(c for c in results["companies"] if c["company_id"] == "nvidia")["factors"]["F1"]
        self.assertEqual(f1["score"], 1)

    def test_broken_cross_reference_stops_init_and_writes_nothing(self):
        write_json(self.paths.evidence, {"schema": "scorecard.evidence/1", "run_id": SLUG, "items": []})
        with self.assertRaisesRegex(SchemaError, "init --from-run .*교차 참조.*EV-nvidia-001"):
            stages.init_run(self.NEW, from_run=SLUG, title="깨진 이어받기")
        self.assertFalse(engine.run_dir(self.NEW).exists())


class ExistingApprovalIdTest(unittest.TestCase):
    def test_existing_runs_approval_id_equals_recomputed(self):
        for slug in EXISTING:
            with self.subTest(slug=slug):
                approval = load_json_strict(engine.run_dir(slug) / "approval.json")
                self.assertEqual(approval["approval_id"], approval_id_for(slug, approval["hashes"]))
                validate_approval(approval, slug)
                self.assertTrue(stages.status(slug)["approval_valid"])


if __name__ == "__main__":
    unittest.main()
