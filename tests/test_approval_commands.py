# summary --json 의 키 구조(승인 페이지 계약), confirm 의 근거 ID 검증·해시 변화, approve --via 기록, revoke 기록과 승인 파일 삭제를 잠근다
from __future__ import annotations

import io
import json
import os
import re
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorecard_cli  # noqa: E402
from scorecard import engine, stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_approval, write_json  # noqa: E402
from tests.test_collect_stage import RSS, SLUG, Sandbox  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402

FIXTURE = ROOT / "tests" / "node" / "fixtures" / "summary.sample.json"
EXISTING = ("ai-scorecard-2026-09-baseline", "ai-scorecard-2026-09-obsreg")
NOW = "2026-09-30T00:00:00Z"


def key_paths(node, prefix: str = "") -> set[str]:
    """dict 키 경로 집합. 리스트는 `[]` 로 적고 모든 원소의 키를 합친다. 값은 보지 않는다."""
    out: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            path = f"{prefix}.{key}" if prefix else key
            out.add(path)
            out |= key_paths(value, path)
    elif isinstance(node, list):
        for value in node:
            out |= key_paths(value, prefix + "[]")
    return out


def cover_previous_triggers(slug: str = SLUG) -> int:
    """2026-10-01 research 는 이전 트리거마다 처리 기록(carry)을 요구한다. 시험 실행은 이전 트리거를 철회로 처리해 둔다.
    덧붙인 항목 수를 돌려준다."""
    run = load_json_strict(engine.run_dir(slug) / "run.json")
    path = run_paths(slug).triggers
    payload = load_json_strict(path)
    previous = stages.previous_triggers(run)
    for i, prev in enumerate(previous, start=len(payload["items"]) + 1):
        payload["items"].append({
            "trigger_id": f"TRG-{i:03d}", "company_id": "nvidia", "factors": ["F1"], "observation": prev["title"],
            "condition": "시험용", "deadline": "2027-06-30", "evidence_ids": [], "source_ids": [], "status": "withdrawn",
            "recheck": {"factors": ["F1"], "what": "시험용"},
            "carry": {"ref": prev["ref"], "checked_at": run["created_at"][:10], "finding": "시험 실행이라 철회로 처리"}})
    write_json(path, payload)
    return len(previous)


class FlowBase(unittest.TestCase):
    """샌드박스 실행 하나를 근거·트리거와 함께 리뷰 pass 까지 만든다. 정본 실행은 읽기만 한다."""

    def setUp(self) -> None:
        self.box = Sandbox(("nvidia", "openai"))
        self.addCleanup(self.box.close)
        self.paths = run_paths(SLUG)
        stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
        self.cand = [c for c in load_json_strict(self.paths.candidates)["items"] if c["company_id"] == "nvidia"][0]
        self.write_evidence()
        write_json(self.paths.triggers, {"schema": "scorecard.triggers/2", "run_id": SLUG, "items": [
            {"trigger_id": "TRG-001", "company_id": "nvidia", "factors": ["F1"], "observation": "소프트웨어 플랫폼 발표",
             "condition": "엔터프라이즈 채택 공시", "deadline": "2027-06-30", "evidence_ids": ["EV-nvidia-001"],
             "source_ids": [self.cand["source_id"]], "status": "watching", "recheck": {"factors": ["F1"], "what": "업무 채널 형성 여부"}}]})
        cover_previous_triggers(SLUG)
        stages.register_evidence_sources(SLUG)   # research 가 하는 출처 등록. confirm 의 전체 검증이 출처 장부를 본다

    def evidence_item(self, eid: str = "EV-nvidia-001", **kw) -> dict:
        item = {"evidence_id": eid, "company_id": "nvidia", "factors": ["F1"], "kind": "news",
                "source_id": self.cand["source_id"], "published_at_utc": self.cand["published_at_utc"], "title": self.cand["title"],
                "excerpt": self.cand["title"], "relevance": "개발자 생태계 확장 신호", "channel": "secondary",
                "conditional_impact": None, "horizon": "2027H1", "counter_evidence": [], "unverified": [],
                "change_vs_previous": "new", "status": "candidate"}
        item.update(kw)
        return item

    def write_evidence(self, *extra: dict) -> None:
        write_json(self.paths.evidence, {"schema": "scorecard.evidence/1", "run_id": SLUG, "items": [self.evidence_item(), *extra]})

    def ready(self) -> None:
        stages.research(SLUG)
        stages.calculate(SLUG)
        stages.draft(SLUG)
        stages.review_template(SLUG)
        text = self.paths.review.read_text(encoding="utf-8").replace("status: needs_fix", "status: pass", 1)
        text = re.sub(r"\|  \| pending \|  \|$", "| 시험 검토자 | pass | 확인 |", text, flags=re.M)
        text = re.sub(r"\| pending \|  \|$", "| pass | 확인 |", text, flags=re.M)
        self.paths.review.write_text(text, encoding="utf-8", newline="\n")

    def cli(self, *argv: str, code: int = 0) -> str:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            got = scorecard_cli.main([str(a) for a in argv])
        self.assertEqual(got, code, f"{argv}\n{out.getvalue()}\n{err.getvalue()}")
        return out.getvalue() + err.getvalue()

    @property
    def approval_path(self) -> Path:
        return self.box.run_dir / "approval.json"


class SummaryShapeTest(FlowBase):
    def test_key_structure_equals_fixture(self):
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)
        # 2026-10-01 판단 변경 제안도 요약 계약에 든다. 제안은 입력 해시 밖이라 승인은 그대로다.
        stages.add_proposal(SLUG, company_id="nvidia", factor="F5", changes={"H": -1}, reason="시험 제안",
                            evidence_ids=["EV-nvidia-001"], evidence_after=["시험 근거 문장"])
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(sorted(key_paths(stages.summary(SLUG))), sorted(key_paths(fixture)))

    def test_cli_json_is_the_same_dict_with_raw_korean(self):
        self.ready()
        out = self.cli("summary", SLUG, "--json")
        self.assertEqual(json.loads(out), stages.summary(SLUG))
        self.assertIn("시험 검토자", out)          # ensure_ascii=False
        self.assertNotIn("\\u", out)

    def test_without_review_or_evidence(self):
        for path in (self.paths.evidence, self.paths.triggers, self.paths.candidates):
            path.unlink()
        s = stages.summary(SLUG)
        self.assertIsNone(s["review"])
        self.assertEqual(s["evidence"], {"candidates": 0, "selected": 0, "confirmed": 0, "items": []})
        self.assertEqual((s["triggers"], s["companies"]), ([], []))
        self.assertEqual(s["approval"], {"exists": False, "valid": False, "approved_by": None, "approved_at": None})


class ApprovalReadinessTest(FlowBase):
    """2026-10-01 사용자 요청: 승인할 수 없는 상태를 승인 버튼을 누르기 전에 알린다."""

    def test_blocked_before_review_and_ready_after(self):
        r = stages.summary(SLUG)["approval_ready"]
        self.assertFalse(r["ready"])
        self.assertTrue(r["blockers"])
        self.ready()
        self.assertEqual(stages.summary(SLUG)["approval_ready"], {"ready": True, "blockers": []})


class ExistingRunsTest(unittest.TestCase):
    def test_summary_runs_and_approval_is_valid(self):
        fixture_paths = key_paths(json.loads(FIXTURE.read_text(encoding="utf-8")))
        for slug in EXISTING:
            with self.subTest(slug=slug):
                s = stages.summary(slug)
                self.assertEqual(s["approval"]["exists"], True)
                self.assertEqual(s["approval"]["valid"], True)
                self.assertEqual(s["review"]["status"], "pass")
                self.assertTrue(key_paths(s) <= fixture_paths, sorted(key_paths(s) - fixture_paths))
                self.assertEqual(set(s), {p for p in fixture_paths if "." not in p and "[" not in p})
                self.assertTrue(stages.status(slug)["approval_valid"])

    def test_existing_approval_files_unchanged_and_valid(self):
        for slug in EXISTING:
            with self.subTest(slug=slug):
                approval = validate_approval(load_json_strict(engine.run_dir(slug) / "approval.json"), slug)
                self.assertNotIn("approved_via", approval)
        proc = subprocess.run(["git", "status", "--porcelain", "--", *(f"output/{s}" for s in EXISTING)],
                              cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.stdout.strip(), "")


class ConfirmTest(FlowBase):
    def test_bad_format_rejected_and_file_untouched(self):
        before = self.paths.evidence.read_bytes()
        for bad in ("EV-001", "--evidence", "--EV-nvidia-001", "ev-nvidia-001", "EV-Nvidia-001", "EV-nvidia-01", "EV-nvidia-0011", ""):
            with self.subTest(bad=bad), self.assertRaisesRegex(SchemaError, "형식"):
                stages.confirm(SLUG, evidence_ids=[bad])
            with self.subTest(bad=bad, reject=True), self.assertRaisesRegex(SchemaError, "형식"):
                stages.confirm(SLUG, reject_ids=[bad])
        self.assertEqual(self.paths.evidence.read_bytes(), before)

    def test_cli_rejects_value_starting_with_dashes(self):
        self.assertIn("형식", self.cli("confirm", SLUG, "--evidence=--x", code=1))

    def test_unknown_id_rejected(self):
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-999"):
            stages.confirm(SLUG, evidence_ids=["EV-nvidia-999"])

    def test_needs_some_id_and_no_overlap(self):
        with self.assertRaises(SchemaError):
            stages.confirm(SLUG)
        with self.assertRaisesRegex(SchemaError, "확정하면서 거부"):
            stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reject_ids=["EV-nvidia-001"])

    def test_confirm_changes_only_the_evidence_hash(self):
        self.ready()
        before = stages.current_hashes(SLUG)
        out = stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="user", reviewed_at="2026-09-30")
        after = stages.current_hashes(SLUG)
        self.assertEqual(sorted(k for k in before if before[k] != after.get(k)), ["evidence"])
        self.assertEqual(out["evidence_hash"], after["evidence"])
        item = load_json_strict(self.paths.evidence)["items"][0]
        self.assertEqual((item["status"], item["reviewer"], item["reviewed_at"]), ("confirmed", "user", "2026-09-30"))
        # 다시 확정하면 아무것도 바꾸지 않는다.
        again = stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="other")
        self.assertEqual((again["confirmed"], again["already_confirmed"]), ([], ["EV-nvidia-001"]))
        self.assertEqual(stages.current_hashes(SLUG)["evidence"], after["evidence"])

    def test_reviewer_defaults_to_scorecard_agent(self):
        with mock.patch.dict(os.environ, {"SCORECARD_AGENT": "agent-x"}):
            self.assertEqual(stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"])["reviewer"], "agent-x")

    def test_reject_removes_item(self):
        self.write_evidence(self.evidence_item("EV-nvidia-002"))
        stages.confirm(SLUG, reject_ids=["EV-nvidia-002"])
        self.assertEqual([e["evidence_id"] for e in load_json_strict(self.paths.evidence)["items"]], ["EV-nvidia-001"])

    def test_reject_of_cited_evidence_restores_the_file(self):
        before = self.paths.evidence.read_bytes()
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-001"):
            stages.confirm(SLUG, reject_ids=["EV-nvidia-001"])   # TRG-001 이 인용한다
        self.assertEqual(self.paths.evidence.read_bytes(), before)

    def test_cli_prints_rerun_hint(self):
        with human_env():
            out = self.cli("confirm", SLUG, "--evidence", "EV-nvidia-001", "--by", "user")
        self.assertIn("research → calculate → draft → review 를 다시 돌린다", out)

    def test_lock_is_checked_only_in_agent_sessions(self):
        lock = stages.lock_path(SLUG)
        lock.write_text(json.dumps({"owner": "other", "started_utc": NOW, "stage": "draft"}), encoding="utf-8")
        before = lock.read_bytes()
        with human_env(SCORECARD_AGENT="human"):   # 승인 페이지(사람 셸)의 confirm 은 잠금과 무관하다
            self.cli("confirm", SLUG, "--evidence", "EV-nvidia-001")
        self.assertEqual(lock.read_bytes(), before)
        self.write_evidence()
        with human_env(CLAUDECODE="1", SCORECARD_AGENT="me"):
            self.assertIn("--take-lock", self.cli("confirm", SLUG, "--evidence", "EV-nvidia-001", code=1))
            self.cli("confirm", SLUG, "--evidence", "EV-nvidia-001", "--take-lock")
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8"))["owner"], "me")


class ApproveRevokeTest(FlowBase):
    def test_end_to_end(self):
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)
        approval = validate_approval(load_json_strict(self.approval_path), SLUG)
        self.assertEqual(approval["approved_via"], "browser")
        self.assertEqual(sorted(approval["hashes"]), sorted(stages.current_hashes(SLUG)))
        self.assertTrue(stages.summary(SLUG)["approval"]["valid"])

        with human_env():   # 유효 승인 실행의 근거 확정은 사람 세션만 한다(2026-10-01 레인 N, V2-1)
            stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="user")
        self.assertEqual(stages.summary(SLUG)["approval"], {"exists": True, "valid": False, "approved_by": "user", "approved_at": approval["approved_at"]})

        log = stages.revoke(SLUG, by="user", note="근거 확정으로 해시가 바뀜", allow_agent_session=True)
        self.assertFalse(self.approval_path.exists())
        lines = log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        entry = json.loads(lines[0])
        self.assertEqual(sorted(entry), ["approval_id", "hashes", "note", "revoked_at", "revoked_by"])
        self.assertEqual((entry["approval_id"], entry["hashes"], entry["revoked_by"]), (approval["approval_id"], approval["hashes"], "user"))
        self.assertRegex(entry["revoked_at"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
        self.assertFalse(stages.summary(SLUG)["approval"]["exists"])

    def test_via_default_and_invalid(self):
        self.ready()
        stages.approve(SLUG, approved_by="user", allow_agent_session=True)
        self.assertEqual(load_json_strict(self.approval_path)["approved_via"], "terminal")
        with self.assertRaisesRegex(SchemaError, "via"):
            stages.approve(SLUG, approved_by="user", via="agent", allow_agent_session=True)
        base = load_json_strict(self.approval_path)
        with self.assertRaises(SchemaError):
            validate_approval({**base, "approved_via": "agent"}, SLUG)

    def test_cli_approve_via_browser_in_human_shell(self):
        self.ready()
        with human_env(ORCA_TERMINAL_HANDLE="term_human"):
            self.cli("approve", SLUG, "--by", "user", "--via", "browser")
        self.assertEqual(load_json_strict(self.approval_path)["approved_via"], "browser")

    def test_revoke_needs_note_and_existing_approval(self):
        with self.assertRaisesRegex(SchemaError, "취소할 승인이 없다"):
            stages.revoke(SLUG, by="user", note="n", allow_agent_session=True)
        self.ready()
        stages.approve(SLUG, approved_by="user", allow_agent_session=True)
        for by, note in (("user", ""), ("user", "  "), ("", "n")):
            with self.subTest(by=by, note=note), self.assertRaises(SchemaError):
                stages.revoke(SLUG, by=by, note=note, allow_agent_session=True)
        self.assertTrue(self.approval_path.exists())
        self.assertFalse((self.box.run_dir / "revocations.jsonl").exists())

    def test_cli_revoke_refused_in_agent_session(self):
        self.ready()
        stages.approve(SLUG, approved_by="user", allow_agent_session=True)
        with human_env(ORCA_AGENT_LAUNCH_TOKEN="x"):
            out = self.cli("revoke", SLUG, "--by", "user", "--note", "n", code=1)
        self.assertIn("에이전트 세션", out)
        self.assertTrue(self.approval_path.exists())
        with human_env():
            self.cli("revoke", SLUG, "--by", "user", "--note", "n")
        self.assertFalse(self.approval_path.exists())


if __name__ == "__main__":
    unittest.main()
