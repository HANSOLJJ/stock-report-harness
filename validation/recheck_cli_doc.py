# 문서와 CLI 검토 지적을 승인 파일 생성 없이 메모리와 읽기 전용 조회로 재현한다.
from __future__ import annotations

import ast
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
WORKER = HERE.parents[1] / "worker"
SLUG = "ai-scorecard-2026-09-baseline"
sys.path.insert(0, str(WORKER / "scripts"))

import scorecard_cli
from scorecard import validate as score_validate
from scorecard.schema import SchemaError, validate_approval, validate_run
from validate_report_contract import ValidationResult, validate_contract


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    watched = [WORKER / p for p in ("README.md", "AGENTS.md", "package.json", "docs/scorecard/structure.md",
               "scripts/scorecard_cli.py", "scripts/report_contract_lib.py", "scripts/validate_report_contract.py")]
    for relative in ("scripts/scorecard/*.py", "tests/*.py", "scorecard/rules/*.json",
                     ".claude/commands/score-*.md", ".claude/skills/score-*/SKILL.md"):
        watched.extend(WORKER.glob(relative))
    watched.extend(WORKER.glob(f"scorecard/runs/{SLUG}/*.json"))
    watched.extend(WORKER / f"{folder}/{SLUG}.md" for folder in ("plan", "research", "drafts", "reviews"))
    before = {str(p.relative_to(WORKER)): sha(p) for p in watched if p.is_file()}
    head = subprocess.check_output(["git", "-C", str(WORKER), "rev-parse", "HEAD"], text=True).strip()
    run = load(WORKER / f"scorecard/runs/{SLUG}/run.json")
    rules = load(WORKER / "scorecard/rules/v1.5.json")
    base = {"schema": "scorecard.approval/1", "run_id": SLUG, "approval_id": "audit-only",
            "approved_at": "2026-09-08", "hashes": {k: "0" * 64 for k in
            ("rules", "observations", "judgments", "run", "results", "draft")}}
    approval_cases = []
    for value in ("reviewer", "", "   ", None, 7):
        try:
            validate_approval({**base, "approved_by": value}, SLUG)
            outcome = "accepted"
        except SchemaError as exc:
            outcome = str(exc)
        approval_cases.append({"value": value, "schema": outcome})
    parser_cases = []
    for value in ("reviewer", "", "   "):
        captured = []
        # 실제 parser를 사용하되 쓰기 단계는 대체한다. 승인 자체는 수행하지 않는다.
        with patch.object(scorecard_cli, "cmd_approve", side_effect=lambda args: captured.append(args.by) or 0):
            code = scorecard_cli.main(["approve", SLUG, "--by", value])
        parser_cases.append({"value": value, "exit": code, "captured": captured})

    normal = validate_contract(SLUG, check_html_if_present=False, check_price_chart_if_present=False)
    read_md = score_validate.read_markdown
    def missing_q07(path):
        fm, body, raw, text = read_md(path)
        if Path(path).parent.name == "reviews":
            body = "\n".join(line for line in body.splitlines() if not line.startswith("| Q07 |"))
        return fm, body, raw, text
    with patch.object(score_validate, "read_markdown", side_effect=missing_q07):
        broken = score_validate.validate_scorecard(SLUG, check_html_if_present=False, result=ValidationResult(slug=SLUG))

    try:
        validate_run({**copy.deepcopy(run), "change_type": "data-update"}, SLUG)
        change_type = "accepted"
    except SchemaError as exc:
        change_type = str(exc)
    tests = []
    for path in (WORKER / "tests").glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tests.extend(n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
    help_result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(WORKER / "scripts/scorecard_cli.py"),
                                  "init", "--help"], capture_output=True, text=True, encoding="utf-8")
    plan = (WORKER / f"plan/{SLUG}.md").read_text(encoding="utf-8")
    after = {str(p.relative_to(WORKER)): sha(p) for p in watched if p.is_file()}
    result = {
        "worker_head": head, "input_hashes": before,
        "changed_files": sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k)),
        "approval_schema_cases": approval_cases, "approval_parser_only_cases": parser_cases,
        "current_contract": {"ok": normal.ok, "errors": normal.errors, "checks": normal.checks},
        "missing_q07_in_memory": {"ok": broken.ok, "errors": broken.errors, "checks": broken.checks},
        "change_type_schema": change_type, "test_methods": tests,
        "init_help": help_result.stdout, "init_help_exit": help_result.returncode,
        "plan_awaiting_lines": [line for line in plan.splitlines() if "awaiting_user" in line],
        "dates": {k: run.get(k) for k in ("as_of", "price_as_of", "info_cutoff")},
        "decision_C20": next(d for d in rules["decisions"] if d["id"] == "C-20"),
        "npm_scripts": load(WORKER / "package.json")["scripts"],
    }
    assert not result["changed_files"], result["changed_files"]
    assert help_result.returncode == 0
    assert approval_cases[0]["schema"] == "accepted"
    assert any("Q07" in e for e in broken.errors), broken.errors
    return result


if __name__ == "__main__":
    result = audit()
    (HERE / "cli-doc-recheck-evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    keys = ("worker_head", "approval_schema_cases", "approval_parser_only_cases", "current_contract",
            "missing_q07_in_memory", "change_type_schema", "decision_C20", "changed_files")
    print(json.dumps({k: result[k] for k in keys}, ensure_ascii=False, indent=2))
