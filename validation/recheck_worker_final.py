# worker 수정 7건과 기준선·승인본·결정 분기를 읽기 전용으로 재검증한다.
from __future__ import annotations

import copy
import difflib
import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import recheck_cli_doc as cli
import recheck_qwen as baseline
from scorecard import stages
from scorecard.baseline_import import import_baseline
from scorecard.engine import compute, load_context, load_results
from scorecard.render_html import render_document
from scorecard.render_md import render_plan
from scorecard.schema import SchemaError, validate_observations
from scorecard.validate import UNRENDERED_RE
from report_contract_lib import read_markdown
from validate_report_contract import validate_contract

HERE, WORKER, SLUG = cli.HERE, cli.WORKER, cli.SLUG


def snapshot():
    paths = []
    for folder in ("scripts", "tests", "scorecard", "docs/scorecard"):
        paths.extend(p for p in (WORKER / folder).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    for folder, suffix in (("plan", "md"), ("research", "md"), ("drafts", "md"),
                           ("reviews", "md"), ("output", "html")):
        paths.append(WORKER / folder / f"{SLUG}.{suffix}")
    return {str(p.relative_to(WORKER)): cli.sha(p) for p in paths if p.is_file()}


def head():
    return subprocess.check_output(["git", "-C", str(WORKER), "rev-parse", "HEAD"], text=True).strip()


def schema_outcome(item, companies):
    try:
        validate_observations({"schema": "scorecard.observations/1", "run_id": "audit", "items": [item]}, companies, "audit")
        return "accepted"
    except SchemaError as exc:
        return str(exc)


def audit():
    start_head, before = head(), snapshot()
    b, c = baseline.audit(), cli.audit()
    assert not b["verified_fcf_without_period_accepted"]
    assert all(x["schema"] != "accepted" for x in c["approval_schema_cases"][1:])
    assert c["current_contract"]["ok"]
    assert not any("review 4-area + checklist structure" in x for x in c["missing_q07_in_memory"]["checks"])
    ctx, stored = load_context(SLUG), load_results(SLUG)
    assert compute(ctx) == stored

    # 쓰기 함수를 감시해 잘못된 승인자가 검증·파일 쓰기 전에 거부되는지 확인한다.
    approval_rejections = []
    for value in ("", "   ", None, 7):
        with patch.object(stages, "write_json") as write, patch.object(stages, "current_hashes") as hashes:
            try:
                stages.approve(SLUG, approved_by=value)
            except SchemaError as exc:
                approval_rejections.append(str(exc))
            else:
                raise AssertionError(f"invalid approver accepted: {value!r}")
            write.assert_not_called()
            hashes.assert_not_called()

    # 과거 보고서 수치를 수정하지 않고 최신 기준선 증거를 별도로 만든다.
    base_obs = cli.load(baseline.BASE / "observations.json")["items"]
    na = [o for o in base_obs if o["status"] == "not_applicable"]
    assert len(na) == 8 and all(o["metric"] == "runway_years" and o["value"] is None and o["note"] for o in na)
    assert b["statuses"] == {"legacy_unverified": 198, "not_disclosed": 16,
                            "not_applicable": 8, "incompatible_basis": 4, "parse_failed": 1}
    with tempfile.TemporaryDirectory(prefix="baseline-audit-", dir=HERE) as temp:
        target = Path(temp)
        import_baseline(baseline.SOURCE / "AI기업_채점표_v1.5.html",
                        baseline.SOURCE / "AI기업_채점표_v1.5.md", target, ctx.companies)
        for filename in ("scores.json", "observations.json", "triggers.json"):
            assert cli.load(target / filename) == cli.load(baseline.BASE / filename), filename
        assert (target / "import-report.md").read_text(encoding="utf-8") == (baseline.BASE / "import-report.md").read_text(encoding="utf-8")

    sample = copy.deepcopy(next(o for o in base_obs if o["metric"] == "fcf_ttm" and o["value"] is not None))
    sample["status"] = "verified"
    periods = {}
    for name, period in (("missing", None), ("valid", {"start": "2025-07-01", "end": "2026-06-30"}),
                         ("reversed", {"start": "2026-06-30", "end": "2025-07-01"})):
        periods[name] = schema_outcome({**sample, "period": period}, ctx.companies)
    assert periods["missing"] != "accepted" and periods["valid"] == "accepted"

    scenarios = {}
    options = {"none": [], "reject": [("C-13", "reject_proxy")],
               "accept": [("C-13", "accept_proxy_with_flag")],
               "c06_apply": [("C-06", "proposed_v15_boundaries"), ("C-05", "apply")],
               "c06_diagnose": [("C-06", "proposed_v15_boundaries"), ("C-05", "diagnose_only")]}
    for name, choices in options.items():
        scenario = copy.deepcopy(ctx)
        # 실행·승인 파일에는 쓰지 않는 계산 분기 검증용 가상 결정이다.
        scenario.run["decisions"] = [{"id": did, "choice": choice, "rationale": "in-memory branch test",
                                      "decided_by": "test-fixture", "decided_at": "2026-09-08"} for did, choice in choices]
        result = compute(scenario)
        selected = {co["company_id"]: {"complete": co["complete"], "F6": co["factors"]["F6"],
                                      "F9": co["factors"]["F9"]}
                    for co in result["companies"] if co["company_id"] in ("tsmc", "spacex-xai")}
        scenarios[name] = {"scored": result["population"]["scored"],
                           "pending": result["pending_rule_decisions"], "selected": selected}
    assert "C-13" not in scenarios["reject"]["pending"]
    assert scenarios["reject"]["selected"]["tsmc"]["F6"]["status"] == "pending_data"

    approval = cli.load(ctx.dir / "approval.json")
    review_fm, *_ = read_markdown(WORKER / f"reviews/{SLUG}.md")
    scores, _, triggers = stages.load_baseline(ctx.run["baseline_id"])
    html = render_document(ctx, stored, scores, triggers, review_fm, approval)
    existing_html = (WORKER / f"output/{SLUG}.html").read_text(encoding="utf-8")
    html_diff = list(difflib.unified_diff(existing_html.splitlines(), html.splitlines(),
                                        fromfile="stored", tofile="fresh", n=1))
    assert not UNRENDERED_RE.findall(html)
    plan = render_plan(ctx.run, ctx.rules, ctx.companies, request="audit", baseline_note="audit")
    assert all(word in plan for word in ("pending_data", "needs_judgment", "needs_rule_decision", "awaiting_user"))
    contract = validate_contract(SLUG, require_html=True)
    assert contract.ok, contract.errors
    end_head, after = head(), snapshot()
    changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    assert start_head == end_head and not changed, (start_head, end_head, changed)
    return {"worker_head": start_head, "baseline_audit": b, "cli_audit": c,
            "approval_write_rejections": approval_rejections, "period_cases": periods,
            "baseline_reimport_equal": True, "stored_results_recompute_equal": True,
            "stored_html_rerender_equal": html == existing_html, "html_diff": html_diff,
            "contract_checks": contract.checks,
            "baseline_statuses": dict(Counter(o["status"] for o in base_obs)),
            "approved_snapshot_statuses": dict(Counter(o["status"] for o in ctx.observations)),
            "scenarios": scenarios, "watched_files": len(before), "input_hashes": before,
            "changed_during_check": changed}


if __name__ == "__main__":
    evidence = audit()
    (HERE / "worker-final-recheck-evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: evidence[k] for k in ("worker_head", "baseline_statuses", "approved_snapshot_statuses",
                      "period_cases", "contract_checks", "watched_files", "changed_during_check")}, ensure_ascii=False, indent=2))
    print(json.dumps({k: {"scored": v["scored"], "pending": v["pending"],
                         "spacex_complete": v["selected"]["spacex-xai"]["complete"]}
                      for k, v in evidence["scenarios"].items()}, ensure_ascii=False, indent=2))
