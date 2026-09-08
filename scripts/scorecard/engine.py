# 실행 입력을 읽어 9개 factor 를 계산하고 결정론적 results.json(해시 포함)을 만드는 엔진
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from report_contract_lib import ROOT

from . import SCHEMA_VERSION
from .aggregate import rank_companies, summarize_company
from .calc_f6 import compute_f6
from .calc_f9 import compute_f9
from .calc_qual import compute_f2, compute_f3, compute_f5, compute_f7, compute_manual
from .inputs import JudgmentLookup, ObsLookup
from .rules import RuleSet, load_rules
from .schema import (
    SchemaError,
    load_json_strict,
    sha256_file,
    sha256_obj,
    validate_companies,
    validate_judgments,
    validate_observations,
    validate_run,
    write_json,
)

SCORECARD_DIR = ROOT / "scorecard"
COMPANIES_PATH = SCORECARD_DIR / "companies.json"
RUNS_DIR = SCORECARD_DIR / "runs"
BASELINE_DIR = SCORECARD_DIR / "baseline"
HISTORY_CSV = SCORECARD_DIR / "history.csv"


def run_dir(slug: str) -> Path:
    return RUNS_DIR / slug


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

    @property
    def dir(self) -> Path:
        return run_dir(self.slug)


def load_companies() -> dict[str, dict[str, Any]]:
    return validate_companies(load_json_strict(COMPANIES_PATH))


def input_hashes(slug: str) -> dict[str, str]:
    d = run_dir(slug)
    return {
        "run": sha256_file(d / "run.json"),
        "observations": sha256_file(d / "observations.json"),
        "judgments": sha256_file(d / "judgments.json"),
        "sources": sha256_file(d / "sources.json") if (d / "sources.json").is_file() else "",
    }


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
    observations = validate_observations(load_json_strict(d / "observations.json"), companies, slug)
    judgments = validate_judgments(load_json_strict(d / "judgments.json"), companies, rules.payload, slug)
    sources = load_json_strict(d / "sources.json") if (d / "sources.json").is_file() else {"schema": "scorecard.sources/1", "items": []}
    hashes = input_hashes(slug)
    hashes["rules"] = rules.hash
    return RunContext(slug, run, rules, companies, observations, judgments, sources, hashes)


def compute_company(company: dict[str, Any], obs: ObsLookup, judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "F1": compute_manual("F1", company, judgments, rules),
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
