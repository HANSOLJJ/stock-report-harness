# 실행 입력을 읽어 9개 factor 를 계산하고 결정론적 results.json(해시 포함)을 만드는 엔진
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from report_contract_lib import OUTPUT_DIR, ROOT

from . import SCHEMA_VERSION
from .aggregate import rank_companies, summarize_company
from .calc_f6 import compute_f6
from .calc_f9 import compute_f9
from .calc_qual import compute_f1, compute_f2, compute_f3, compute_f5, compute_f7, compute_manual
from .inputs import JudgmentLookup, ObsLookup
from .rules import RuleSet, load_rules
from .schema import (
    SchemaError,
    load_json_strict,
    sha256_file,
    sha256_obj,
    validate_companies,
    validate_company_summaries,
    validate_cross_refs,
    validate_evidence,
    validate_judgments,
    validate_observations,
    validate_run,
    validate_sources,
    validate_triggers,
    write_json,
)

SCORECARD_DIR = ROOT / "scorecard"
COMPANIES_PATH = SCORECARD_DIR / "companies.json"
BASELINE_DIR = SCORECARD_DIR / "baseline"
HISTORY_CSV = SCORECARD_DIR / "history.csv"


def run_dir(slug: str) -> Path:
    """실행 묶음 폴더 `output/<slug>/`. 테스트는 이 모듈의 OUTPUT_DIR 를 바꿔 샌드박스로 돌린다."""
    return OUTPUT_DIR / slug


@dataclass
class RunContext:
    slug: str
    run: dict[str, Any]
    rules: RuleSet
    companies: dict[str, dict[str, Any]]
    observations: list[dict[str, Any]]
    judgments: list[dict[str, Any]]
    sources: dict[str, Any]
    hashes: dict[str, str]
    # 2026-09-30 레인 E: 파일이 없으면 None. 없는 것을 빈 목록으로 바꾸지 않는다(선별 전과 선별 결과 0건은 다르다).
    evidence: list[dict[str, Any]] | None = None
    triggers: list[dict[str, Any]] | None = None
    # 2026-10-06 사용자 지시: 카드의 한 줄 요약(판단 파일 최상위 company_summaries). 없으면 비어 있고 기준선 원문으로 채우지 않는다.
    company_summaries: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def dir(self) -> Path:
        return run_dir(self.slug)


def load_companies() -> dict[str, dict[str, Any]]:
    return validate_companies(load_json_strict(COMPANIES_PATH))


def input_hashes(slug: str) -> dict[str, str]:
    from .paths import run_paths  # paths 가 engine 을 import 하므로 여기서 부른다

    d = run_dir(slug)
    out = {
        "run": sha256_file(d / "run.json"),
        "observations": sha256_file(d / "observations.json"),
        "judgments": sha256_file(d / "judgments.json"),
        "sources": sha256_file(d / "sources.json") if (d / "sources.json").is_file() else "",
    }
    # 2026-09-30 레인 E: 근거·트리거는 **파일이 있을 때만** 키를 더한다. 없는 실행(기존 두 실행)의
    # results.input_hashes 와 results_hash 가 그대로 남아야 한다. 근거를 고치면 calculate 부터 다시 밟는다.
    paths = run_paths(slug)
    for key, path in (("evidence", paths.evidence), ("triggers", paths.triggers)):
        if path.is_file():
            out[key] = sha256_file(path)
    return out


def load_context(slug: str) -> RunContext:
    d = run_dir(slug)
    run = validate_run(load_json_strict(d / "run.json"), slug)
    rules = load_rules(run["rule_version"])
    if run.get("rule_hash") and run["rule_hash"] != rules.hash:
        raise SchemaError(
            f"run.json rule_hash {run['rule_hash'][:12]}… 와 규칙 파일 해시 {rules.hash[:12]}… 불일치 — 규칙이 바뀌었으면 새 실행을 만든다"
        )
    companies = load_companies()
    unknown = [cid for cid in run["companies"] if cid not in companies]
    if unknown:
        raise SchemaError(f"run.json companies 에 알 수 없는 기업 {unknown}")
    # 2026-09-16 FIX-57 2단계: `확인된 미공시` 라벨이 규칙이 선언한 경로를 채우는지 여기서 함께 본다.
    observations = validate_observations(load_json_strict(d / "observations.json"), companies, slug,
                                         missing_policy=rules.payload["policies"].get("missing_types"))
    judgments_payload = load_json_strict(d / "judgments.json")
    judgments = validate_judgments(judgments_payload, companies, rules.payload, slug)
    summaries = validate_company_summaries(judgments_payload.get("company_summaries") or [], companies)
    sources = load_json_strict(d / "sources.json") if (d / "sources.json").is_file() else {"schema": "scorecard.sources/1", "run_id": slug, "items": []}
    # 2026-09-30 레인 E: 출처는 항상, 근거·트리거는 파일이 있을 때만 검증하고 셋을 교차 대조한다.
    source_items = validate_sources(sources, slug)
    source_ids = {s["source_id"] for s in source_items}
    from .paths import run_paths  # paths 가 engine 을 import 하므로 여기서 부른다

    paths = run_paths(slug)
    evidence = (validate_evidence(load_json_strict(paths.evidence), companies, source_ids, slug)
                if paths.evidence.is_file() else None)
    triggers = (validate_triggers(load_json_strict(paths.triggers), companies,
                                  {e["evidence_id"] for e in evidence or []}, source_ids, slug)
                if paths.triggers.is_file() else None)
    validate_cross_refs(observations, judgments, evidence, source_items)
    hashes = input_hashes(slug)
    hashes["rules"] = rules.hash
    return RunContext(slug, run, rules, companies, observations, judgments, sources, hashes, evidence, triggers,
                      company_summaries=summaries)


def compute_company(company: dict[str, Any], obs: ObsLookup, judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    # 2026-10-08 규칙 v2.0: ① 이 lockin 모드면 네 질문 사다리로 계산한다. v1.9 이하(manual)는 지금 경로 그대로다.
    f1 = (compute_f1(company, judgments, rules) if rules.factor("F1").get("mode") == "lockin"
          else compute_manual("F1", company, judgments, rules))
    return {
        "F1": f1,
        "F2": compute_f2(company, judgments, rules, run),
        "F3": compute_f3(company, judgments, rules),
        "F4": compute_manual("F4", company, judgments, rules),
        "F5": compute_f5(company, judgments, rules),
        "F6": compute_f6(company, obs, judgments, rules, run),
        "F7": compute_f7(company, judgments, rules),
        "F8": compute_manual("F8", company, judgments, rules),
        "F9": compute_f9(company, obs, judgments, rules, run),
    }


def compute(ctx: RunContext) -> dict[str, Any]:
    obs = ObsLookup(ctx.observations)
    judgments = JudgmentLookup(ctx.judgments)
    summaries: list[dict[str, Any]] = []
    for cid in ctx.run["companies"]:
        company = ctx.companies[cid]
        factors = compute_company(company, obs, judgments, ctx.rules, ctx.run)
        summaries.append(summarize_company(company, factors))
    ranked = rank_companies(summaries)
    pending_decisions = sorted(
        {
            p["decision_id"]
            for s in summaries
            for p in s["pending"]
            if p.get("decision_id")
        }
    )
    warnings_count = sum(len(f["warnings"]) for s in summaries for f in s["factors"].values())
    results: dict[str, Any] = {
        "schema": "scorecard.results/1",
        "engine": SCHEMA_VERSION,
        "run_id": ctx.slug,
        "as_of": ctx.run["as_of"],
        "rule_version": ctx.rules.version,
        "baseline_id": ctx.run["baseline_id"],
        "input_hashes": dict(ctx.hashes),
        "decisions_applied": [d["id"] + ":" + d["choice"] for d in ctx.run.get("decisions", [])],
        "companies": summaries,
        "ranking": ranked["ranking"],
        "population": ranked["population"],
        "pending_rule_decisions": pending_decisions,
        "warnings_count": warnings_count,
    }
    results["results_hash"] = sha256_obj({k: v for k, v in results.items() if k != "results_hash"})
    return results


def results_path(slug: str) -> Path:
    return run_dir(slug) / "results.json"


def write_results(slug: str, results: dict[str, Any]) -> Path:
    path = results_path(slug)
    write_json(path, results)
    return path


def load_results(slug: str) -> dict[str, Any]:
    payload = load_json_strict(results_path(slug))
    if payload.get("schema") != "scorecard.results/1":
        raise SchemaError("results.json schema 불일치")
    expected = sha256_obj({k: v for k, v in payload.items() if k != "results_hash"})
    if payload.get("results_hash") != expected:
        raise SchemaError("results.json results_hash 불일치 — 파일이 손으로 수정됐거나 손상됨")
    return payload


def recompute_matches(slug: str) -> tuple[bool, str, str]:
    """저장된 results 와 현재 입력으로 다시 계산한 결과의 해시 비교 (결정론·입력 변경 감지)."""
    stored = load_results(slug)
    fresh = compute(load_context(slug))
    return stored["results_hash"] == fresh["results_hash"], stored["results_hash"], fresh["results_hash"]
