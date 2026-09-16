# scorecard 단계 실행: init(실행 생성) → research → calculate(+preview) → draft → review-template → approve. 순서·해시 결속을 코드에서 강제한다.
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from report_contract_lib import DRAFT_DIR, PLAN_DIR, RESEARCH_DIR, REVIEW_DIR, artifact_paths, read_markdown, rel

from .baseline_import import BASELINE_AS_OF, SRC_HTML, SRC_MD, SRC_RULE, baseline_judgments
from .engine import BASELINE_DIR, RunContext, compute, input_hashes, load_companies, load_context, load_results, results_path, run_dir, write_results
from .render_md import render_draft, render_plan, render_preview, render_research, render_review_template
from .rules import load_rules
from .schema import SchemaError, load_json_strict, sha256_file, sha256_text, validate_observations, write_json


def today() -> str:
    return date.today().isoformat()


def load_baseline(baseline_id: str) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    d = BASELINE_DIR / baseline_id
    scores = load_json_strict(d / "scores.json")
    observations = load_json_strict(d / "observations.json")
    triggers = load_json_strict(d / "triggers.json")["items"] if (d / "triggers.json").is_file() else []
    if scores.get("schema") != "scorecard.baseline/1":
        raise SchemaError(f"기준선 {baseline_id} scores.json schema 불일치")
    return scores, observations, triggers


# ------------------------------------------------------------------ init

def init_run(
    slug: str,
    *,
    as_of: str,
    title: str,
    request: str,
    purpose: str,
    companies: list[str] | None = None,
    baseline_id: str = "v1.5",
    rule_version: str = "v1.5",
    decisions: list[dict[str, Any]] | None = None,
    price_as_of: str | None = None,
    info_cutoff: str | None = None,
    force: bool = False,
) -> dict[str, Path]:
    if not slug.startswith("ai-scorecard-"):
        raise SchemaError("scorecard slug 는 `ai-scorecard-` 로 시작해야 한다 (예: ai-scorecard-2026-09-baseline)")
    d = run_dir(slug)
    if d.exists() and not force:
        raise SchemaError(f"실행 디렉터리가 이미 있음: {rel(d)} (--force 로 덮어쓰기)")
    registry = load_companies()
    rules = load_rules(rule_version)
    scores, base_obs, _triggers = load_baseline(baseline_id)
    baseline_ids = [c["company_id"] for c in scores["companies"]]
    selected = companies or baseline_ids
    unknown = [c for c in selected if c not in registry]
    if unknown:
        raise SchemaError(f"알 수 없는 기업 {unknown}")
    created = today()
    run = {
        "schema": "scorecard.run/1",
        "run_id": slug,
        "report_type": "ai_scorecard",
        "title": title,
        "as_of": as_of,
        "price_as_of": price_as_of or as_of,
        "info_cutoff": info_cutoff or as_of,
        "rule_version": rule_version,
        "rule_hash": rules.hash,
        "baseline_id": baseline_id,
        "companies": selected,
        "reference_companies": [],
        "decisions": decisions or [],
        "created_at": created,
        "purpose": purpose,
        "assumptions": [
            f"원자료와 정성 판단은 기준선 {baseline_id}({scores['as_of']})에서 승계했으며 이번 실행에서 재검증되지 않았다(legacy_unverified)",
            "미결 규칙 결정(C-xx)은 run.json.decisions 에 명시된 것만 적용한다",
            "가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)",
        ],
    }
    observations = {
        "schema": "scorecard.observations/1",
        "run_id": slug,
        "as_of": as_of,
        "note": f"기준선 {baseline_id} 관측 승계. 새 관측은 status=verified 와 출처 ID 를 붙여 추가한다",
        "items": [dict(o) for o in base_obs["items"] if o["company_id"] in selected],
    }
    validate_observations(observations, registry, slug)
    judgments = {
        "schema": "scorecard.judgments/1",
        "run_id": slug,
        "note": f"기준선 {baseline_id} 판정표 승계(status=carried). 신규 판단은 status=new 로 교체한다",
        "items": [j for j in baseline_judgments(scores, slug, registry) if j["company_id"] in selected],
    }
    sources = {
        "schema": "scorecard.sources/1",
        "run_id": slug,
        # 2026-09-16 FIX-56 2단계(5차 리뷰 A 분담): SRC_RULE 만 None 이라 새 실행을 만들면 채점규칙 384행 고지가 다시 비었다.
        # 지금 값은 FIX-52 가 데이터만 고친 결과다 — 생성 코드에 넣어야 다음 실행에도 남는다.
        "items": [
            {"source_id": SRC_HTML, "title": f"AI기업_채점표_{baseline_id}.html (D·VAL·EARN·FIN·BORR·TRIG)", "publisher": "내부 기준선", "url": None, "accessed_at": created, "sha256": scores["source"]["html_sha256"], "conflict_of_interest": "작성자 Claude=Anthropic (긴장 #4·#11)", "note": "과거 기록"},
            {"source_id": SRC_MD, "title": f"AI기업_채점표_{baseline_id}.md (순위표·원자료)", "publisher": "내부 기준선", "url": None, "accessed_at": created, "sha256": scores["source"]["md_sha256"], "conflict_of_interest": "작성자 Claude=Anthropic (긴장 #4·#11)", "note": "과거 기록"},
            {"source_id": SRC_RULE, "title": "AI기업_채점규칙_v1.5.md (③ 사다리·별표 G·별표 I·⑨ 적용표·⑥ 비상장)", "publisher": "내부 규칙", "url": None, "accessed_at": created, "sha256": rules.payload["source"]["sha256"], "conflict_of_interest": "작성자 Claude=Anthropic — 채점규칙 384행 이해상충 고지(ARC-AGI 하네스 규칙이 결과적으로 Anthropic ②5 를 지켰다, 운영이력 긴장 #4·#11, 제3자 재검토 예정)", "note": "규칙 원문 판정표"},
        ],
    }
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "run.json", run)
    write_json(d / "observations.json", observations)
    write_json(d / "judgments.json", judgments)
    write_json(d / "sources.json", sources)
    for stale in ("results.json", "preview.md", "approval.json"):
        if (d / stale).exists():
            (d / stale).unlink()
    plan_text = render_plan(run, rules, registry, request=request, baseline_note=f"기준선 `{baseline_id}` ({scores['as_of']}, HTML `{scores['source']['html_sha256'][:12]}…`)의 점수·판정표·원자료를 승계")
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    plan_path = PLAN_DIR / f"{slug}.md"
    plan_path.write_text(plan_text, encoding="utf-8", newline="\n")
    return {"plan": plan_path, "run": d / "run.json", "observations": d / "observations.json", "judgments": d / "judgments.json", "sources": d / "sources.json"}


# ------------------------------------------------------------------ research

def research(slug: str) -> Path:
    _require_file(PLAN_DIR / f"{slug}.md", "plan")
    ctx = load_context(slug)
    text = render_research(ctx, hashes=ctx.hashes)
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    path = RESEARCH_DIR / f"{slug}.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ calculate

def calculate(slug: str) -> tuple[Path, Path, dict[str, Any]]:
    _require_file(PLAN_DIR / f"{slug}.md", "plan")
    _require_file(RESEARCH_DIR / f"{slug}.md", "research")
    ctx = load_context(slug)
    results = compute(ctx)
    path = write_results(slug, results)
    scores, _obs, _trig = load_baseline(ctx.run["baseline_id"])
    preview_path = run_dir(slug) / "preview.md"
    preview_path.write_text(render_preview(ctx, results, scores), encoding="utf-8", newline="\n")
    stale_approval = run_dir(slug) / "approval.json"
    if stale_approval.exists():
        approval = load_json_strict(stale_approval)
        if approval.get("hashes", {}).get("results") != results["results_hash"]:
            stale_approval.unlink()
    return path, preview_path, results


# ------------------------------------------------------------------ draft

def draft(slug: str) -> Path:
    _require_file(PLAN_DIR / f"{slug}.md", "plan")
    _require_file(RESEARCH_DIR / f"{slug}.md", "research")
    _require_file(results_path(slug), "results.json (calculate 먼저)")
    ctx = load_context(slug)
    results = load_results(slug)
    if results["input_hashes"] != ctx.hashes:
        raise SchemaError("입력(run/observations/judgments/rules)이 results.json 계산 이후 바뀜 — calculate 를 다시 실행")
    scores, _obs, triggers = load_baseline(ctx.run["baseline_id"])
    text = render_draft(ctx, results, scores, triggers)
    DRAFT_DIR.mkdir(parents=True, exist_ok=True)
    path = DRAFT_DIR / f"{slug}.md"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ review template

def review_template(slug: str, *, force: bool = False) -> Path:
    draft_path = DRAFT_DIR / f"{slug}.md"
    _require_file(draft_path, "draft")
    path = REVIEW_DIR / f"{slug}.md"
    if path.exists() and not force:
        raise SchemaError(f"리뷰 파일이 이미 있음: {rel(path)} (--force 로 템플릿 재생성)")
    ctx = load_context(slug)
    results = load_results(slug)
    text = render_review_template(ctx, results, draft_hash=sha256_file(draft_path))
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ approve

def current_hashes(slug: str) -> dict[str, str]:
    ctx_hashes = input_hashes(slug)
    run = load_json_strict(run_dir(slug) / "run.json")
    rules = load_rules(run["rule_version"])
    draft_path = DRAFT_DIR / f"{slug}.md"
    return {
        "rules": rules.hash,
        "observations": ctx_hashes["observations"],
        "judgments": ctx_hashes["judgments"],
        "run": ctx_hashes["run"],
        "results": load_results(slug)["results_hash"] if results_path(slug).is_file() else "",
        "draft": sha256_file(draft_path) if draft_path.is_file() else "",
    }


def approve(slug: str, *, approved_by: str, note: str | None = None) -> Path:
    from validate_report_contract import validate_contract

    # 승인자는 사람의 식별자다. 빈 값이나 자동 생성 이름으로 승인 기록을 만들지 않는다 (D-02).
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise SchemaError("승인자(--by)는 비어 있지 않은 문자열이어야 한다. 임의의 승인자를 만들지 말고 실제 사용자 식별자를 쓴다")
    approved_by = approved_by.strip()

    result = validate_contract(slug, require_html=False, require_price_chart=False, check_html_if_present=False, check_price_chart_if_present=False)
    if not result.ok:
        raise SchemaError("승인 전 계약 검증 실패: " + "; ".join(result.errors[:5]))
    hashes = current_hashes(slug)
    approval_id = sha256_text(f"{slug}:{hashes['results']}:{hashes['draft']}")[:16]
    payload = {
        "schema": "scorecard.approval/1",
        "run_id": slug,
        "approval_id": approval_id,
        "approved_by": approved_by,
        "approved_at": today(),
        "hashes": hashes,
        "note": note,
    }
    path = run_dir(slug) / "approval.json"
    write_json(path, payload)
    return path


# ------------------------------------------------------------------ status

def status(slug: str) -> dict[str, Any]:
    paths = artifact_paths(slug)
    d = run_dir(slug)
    out: dict[str, Any] = {"slug": slug}
    out["plan"] = paths.plan.is_file()
    out["run_inputs"] = all((d / name).is_file() for name in ("run.json", "observations.json", "judgments.json"))
    out["research"] = paths.research.is_file()
    out["results"] = results_path(slug).is_file()
    out["draft"] = paths.draft.is_file()
    out["review"] = paths.review.is_file()
    if out["review"]:
        fm, _body, _raw, _text = read_markdown(paths.review)
        out["review_status"] = fm.get("status")
    out["approval"] = (d / "approval.json").is_file()
    if out["approval"] and out["results"] and out["draft"]:
        approval = load_json_strict(d / "approval.json")
        out["approval_valid"] = approval.get("hashes") == current_hashes(slug)
    out["html"] = paths.html.is_file()
    if out["results"]:
        results = load_results(slug)
        out["pending_rule_decisions"] = results["pending_rule_decisions"]
        out["scored"] = results["population"]["scored"]
        out["incomplete"] = [i["company_id"] for i in results["population"]["incomplete"]]
    return out


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise SchemaError(f"선행 산출물 없음: {label} ({rel(path)})")
