# Qwen의 기준선 검증 지적을 원본과 현재 계산기 동작에 대조해 재검토 증거를 만든다.
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKER = HERE.parents[1] / "worker"
SOURCE = Path("E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor")
BASE = WORKER / "scorecard/baseline/v1.5"
sys.path.insert(0, str(WORKER / "scripts"))

from scorecard.baseline_import import extract_js_array, strip_html
from scorecard.inputs import ObsLookup
from scorecard.rules import load_rules
from scorecard.schema import OBSERVATION_STATUSES, SchemaError, validate_observations


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit():
    watched = sorted(BASE.glob("*")) + sorted(SOURCE.glob("*.md"))
    watched += [SOURCE / "AI기업_채점표_v1.5.html"]
    watched += sorted((WORKER / "scripts/scorecard").glob("*.py"))
    watched += [WORKER / "scorecard/rules/v1.5.json", WORKER / "scorecard/companies.json"]
    before = {str(p): digest(p) for p in watched}
    observations = read_json(BASE / "observations.json")
    items = observations["items"]
    scores = read_json(BASE / "scores.json")
    triggers = read_json(BASE / "triggers.json")["items"]
    registry = {c["company_id"]: c for c in read_json(WORKER / "scorecard/companies.json")["companies"]}
    html = (SOURCE / "AI기업_채점표_v1.5.html").read_text(encoding="utf-8")
    md = (SOURCE / "AI기업_채점표_v1.5.md").read_text(encoding="utf-8")
    arrays = {key: extract_js_array(html, key) for key in ("D", "VAL", "TRIG")}
    lookup = ObsLookup(items)
    rules = load_rules("v1.5")

    # 독립 MD 열 매핑으로 factor·합계·순위를 대조한다.
    section = md.split("## 1. 종합 순위표", 1)[1].split("\n## ", 1)[0]
    md_rows = {}
    for line in section.splitlines():
        cells = [c.strip().replace("**", "") for c in line.strip().strip("|").split("|")]
        if len(cells) != 14 or not cells[0].isdigit():
            continue
        md_rows[cells[1]] = [int(re.match(r"^-?\d+", c).group()) for c in [cells[0], *cells[2:]]]
    mismatches = []
    for c in scores["companies"]:
        expected = [c["rank_raw"], *[c["scores"][f"F{i}"] for i in range(1, 6)],
                    c["moat"], *[c["scores"][f"F{i}"] for i in range(6, 10)], c["trap"], c["total"]]
        name = registry[c["company_id"]]["display_name"]
        if md_rows.get(name) != expected:
            mismatches.append({"company_id": c["company_id"], "md": md_rows.get(name), "baseline": expected})

    conflicts = []
    for cid in registry:
        caps = lookup.all(cid, "market_cap")
        if len({o["value"] for o in caps}) > 1:
            conflicts.append({"company_id": cid, "observations": caps,
                              "selected_id": lookup.get(cid, "market_cap")["observation_id"]})
    incompatible = [{"id": o["observation_id"], "preserved": o["value"],
                     "usable": lookup.number(o["company_id"], o["metric"])[0]}
                    for o in items if o["status"] == "incompatible_basis"]
    boundary = {str(per): rules.f6_boundary_flag(per) for per in (19.4, 89.0, 27.5)}
    sample = dict(next(o for o in items if o["metric"] == "fcf_ttm" and o["value"] is not None))
    sample["status"] = "verified"
    sample.pop("period", None)
    try:
        accepted = bool(validate_observations({"schema": "scorecard.observations/1", "run_id": "audit", "items": [sample]}, registry, "audit"))
        period_error = None
    except SchemaError as exc:
        accepted, period_error = False, str(exc)
    source_map = read_json(WORKER / "scorecard/runs/ai-scorecard-2026-09-baseline/sources.json")
    report = {
        "md_ranking_rows": len(md_rows), "score_mismatches": mismatches,
        "counts": {"companies": len(scores["companies"]), "observations": len(items), "triggers": len(triggers)},
        "statuses": dict(Counter(o["status"] for o in items)),
        "missing_period": sum(not o.get("period") for o in items),
        "verified_fcf_without_period_accepted": bool(accepted),
        "verified_fcf_without_period_error": period_error,
        "trigger_keys": sorted(set().union(*(set(t) for t in triggers))),
        "trigger_html_match": all([t["title"], t["why"], t["impact_raw"]] == [strip_html(str(c)) for c in row]
                                  for t, row in zip(triggers, arrays["TRIG"])) and len(triggers) == len(arrays["TRIG"]),
        "market_cap_differences": conflicts, "incompatible_lookup": incompatible,
        "computed_boundary": boundary, "parse_failed_registered": "parse_failed" in OBSERVATION_STATUSES,
        "not_disclosed_values": [{"id": o["observation_id"], "raw": o["raw"], "note": o["note"]}
                                  for o in items if o["status"] == "not_disclosed"],
        "sources": source_map,
        "trigger_original_lines": [line for line in md.splitlines() if line.startswith("|") and ("Meta 분기 FCF" in line or "Menlo 2026" in line)],
        "meta_trigger": [t for t in triggers if "Meta" in t["title"] and "FCF" in t["title"]],
        "changed_during_check": [str(p) for p in watched if digest(p) != before[str(p)]],
        "input_sha256": before,
    }
    assert len(md_rows) == 14 and not mismatches, mismatches
    assert all(o["usable"] is None for o in incompatible) and len(incompatible) == 4
    assert boundary["19.4"]["flag"] and boundary["89.0"]["flag"] and not boundary["27.5"]["flag"]
    assert report["trigger_html_match"]
    assert not report["changed_during_check"]
    return report


if __name__ == "__main__":
    result = audit()
    (HERE / "qwen-recheck-evidence.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("counts", "score_mismatches", "statuses", "missing_period",
                     "verified_fcf_without_period_accepted", "incompatible_lookup", "computed_boundary",
                     "parse_failed_registered", "not_disclosed_values", "changed_during_check")}, ensure_ascii=False, indent=2))
