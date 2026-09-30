# scorecard 단계 실행: init(실행 생성) → research → calculate(+preview) → draft → review-template → approve. 순서·해시 결속을 코드에서 강제한다.
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from report_contract_lib import read_markdown, rel

from .baseline_import import BASELINE_AS_OF, SRC_HANDOVER, SRC_HANDOVER_SHA256, SRC_HTML, SRC_MD, SRC_RULE, baseline_judgments
from .engine import BASELINE_DIR, RunContext, compute, input_hashes, load_companies, load_context, load_results, results_path, run_dir, write_results
from .paths import run_paths
from .render_md import render_draft, render_plan, render_preview, render_research, render_review_template
from .rules import load_rules
from .schema import SchemaError, load_json_strict, sha256_file, sha256_text, validate_approval, validate_observations, validate_run, write_json


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


@dataclass
class _Inputs:
    """`init` 이 만드는 입력 묶음. 기준선에서 새로 만들 때와 이전 실행에서 이어받을 때 이것만 갈린다."""

    observations: dict[str, Any]
    judgments: dict[str, Any]
    sources: dict[str, Any]
    assumptions: list[str]
    baseline_note: str
    continued_from: dict[str, Any] | None = None


def _inputs_from_baseline(slug: str, *, baseline_id: str, selected: list[str], as_of: str, created: str,
                          rules: Any, registry: dict[str, dict[str, Any]], scores: dict[str, Any],
                          base_obs: dict[str, Any]) -> _Inputs:
    """기준선 v1.5 에서 입력을 만든다. 2026-09-21 ADD-03 이전의 `init_run` 본문을 그대로 옮긴 것이다."""
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
            # 2026-09-16 FIX-57 2단계: 판단이 HANDOVER 행 번호를 인용하므로 생성 목록에 있어야 한다(없으면 새 실행에서 인용 대상이 사라진다).
            {"source_id": SRC_HANDOVER, "title": "AI기업_채점표_HANDOVER.md (자동화 핸드오버 — 원자료 출처표·기계화 재고·작성자 이해상충)", "publisher": "내부 기준선", "url": None, "accessed_at": created, "sha256": SRC_HANDOVER_SHA256, "conflict_of_interest": "작성자 Claude=Anthropic — HANDOVER 75행 `3-7. 작성자 이해상충. Claude=Anthropic` (긴장 #4·#11)", "note": "저장소에 커밋되지 않고 v1.5 원본 셋과 같은 곳에 보존돼 있다"},
        ],
    }
    assumptions = [
        f"원자료와 정성 판단은 기준선 {baseline_id}({scores['as_of']})에서 승계했으며 이번 실행에서 재검증되지 않았다(legacy_unverified)",
        "미결 규칙 결정(C-xx)은 run.json.decisions 에 명시된 것만 적용한다",
        "가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)",
    ]
    note = f"기준선 `{baseline_id}` ({scores['as_of']}, HTML `{scores['source']['html_sha256'][:12]}…`)의 점수·판정표·원자료를 승계"
    return _Inputs(observations, judgments, sources, assumptions, note)


def _load_prior_run(prior_slug: str) -> dict[str, Any]:
    path = run_dir(prior_slug) / "run.json"
    if not path.is_file():
        raise SchemaError(f"이어받을 실행이 없다: {rel(path)}")
    return validate_run(load_json_strict(path), prior_slug)


def _inputs_from_run(prior_slug: str, prior_run: dict[str, Any], *, slug: str, selected: list[str],
                     added: list[str], as_of: str, baseline_id: str, rules: Any,
                     registry: dict[str, dict[str, Any]]) -> _Inputs:
    """이전 실행의 관측·판단·출처를 그대로 이어받는다.

    2026-09-21 ADD-03. 기준선에서 다시 만들면 9라운드에 걸쳐 고친 것이 전부 사라진다.
    **판단 항목에는 아무 표시도 찍지 않는다** — `status: carried` 는 `calc_qual._status_for` 가 읽어
    factor 를 `carried_score` 로 내리고 `inputs.carried_note` 가 경고를 붙이는 값이다. 재작성하면
    기존 기업의 점수 상태가 움직인다. 이어받았다는 사실은 `run.continued_from` 에만 적는다.
    """
    d = run_dir(prior_slug)
    prior_obs = load_json_strict(d / "observations.json")
    prior_jud = load_json_strict(d / "judgments.json")
    src_path = d / "sources.json"
    if not src_path.is_file():
        raise SchemaError(f"이어받을 실행에 sources.json 이 없다: {rel(src_path)} — 관측이 인용한 출처가 장부에서 사라진다")

    observations = {
        "schema": "scorecard.observations/1",
        "run_id": slug,
        "as_of": as_of,
        "note": f"이전 실행 {prior_slug} 관측 이어받기. 새 관측은 status=verified 와 출처 ID 를 붙여 추가한다",
        "items": [o for o in prior_obs["items"] if o["company_id"] in selected],
    }
    validate_observations(observations, registry, slug)
    judgments = {
        "schema": "scorecard.judgments/1",
        "run_id": slug,
        "note": f"이전 실행 {prior_slug} 판단 이어받기 — 항목은 한 글자도 바꾸지 않았다. 신규 기업 판단만 추가한다",
        "items": [j for j in prior_jud["items"] if j["company_id"] in selected],
    }
    # 출처는 **통째로** 옮긴다. 기준선 4건으로 덮으면 실행 도중 늘어난 출처가 사라져
    # 관측의 `source_id` 가 장부에서 사라진다.
    sources = {**load_json_strict(src_path), "run_id": slug}

    hashes = input_hashes(prior_slug)
    approval_path = d / "approval.json"
    approval = validate_approval(load_json_strict(approval_path), prior_slug) if approval_path.is_file() else None
    assumptions = [
        f"이전 실행 {prior_slug} 의 관측·판단·출처를 그대로 이어받았다"
        f"(observations {hashes['observations'][:12]}…, judgments {hashes['judgments'][:12]}…)."
        f" 이어받은 항목은 이번 실행에서 재검증되지 않았다",
        (f"이번 실행이 새로 조사한 대상은 {', '.join(registry[c]['display_name'] for c in added)} 뿐이다"
         if added else "이번 실행은 기업을 더하지 않았고 이전 실행의 입력을 그대로 쓴다"),
        "가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)",
    ]
    prior_rule_hash = prior_run.get("rule_hash")
    if prior_rule_hash and prior_rule_hash != rules.hash:
        moved = f"규칙이 이어받은 실행 이후 바뀌었다({prior_rule_hash[:12]}… → {rules.hash[:12]}…)"
        print(f"[경고] {moved} — 기존 기업 점수 불변은 diff 로 확인한다")
        assumptions.append(f"{moved} — 기존 기업 점수 불변은 diff 로 확인한다")
    if approval is None:
        assumptions.append(f"이전 실행 {prior_slug} 에는 승인 기록이 없다. 승인되지 않은 상태에서 이어받았다")
    else:
        # `draft` 는 뺀다. 이어받는 것은 입력이지 문서가 아니다.
        current = current_hashes(prior_slug)
        differing = [k for k in ("rules", "observations", "judgments", "run", "results")
                     if approval["hashes"].get(k) != current.get(k)]
        if differing:
            assumptions.append(f"이전 실행 {prior_slug} 의 승인이 무효다(달라진 것: {', '.join(differing)}). 그 상태에서 이어받았다")

    note = (f"이전 실행 `{prior_slug}`(as_of {prior_run['as_of']})의 관측 {len(observations['items'])}건·"
            f"판단 {len(judgments['items'])}건·출처 {len(sources.get('items') or [])}건을 이어받았고, "
            f"점수 비교 기준선은 `{baseline_id}` 를 유지한다")
    continued_from = {
        "run_id": prior_slug,
        "as_of": prior_run["as_of"],
        # 옛 해시를 옮기면 `engine.load_context` 가 규칙 파일과의 등호 검사에서 막는다. 현재 규칙에서 다시 센다.
        "rule_hash": prior_rule_hash or rules.hash,
        "hashes": {k: hashes[k] for k in ("run", "observations", "judgments", "sources")},
        "results_hash": load_results(prior_slug)["results_hash"] if results_path(prior_slug).is_file() else None,
        "approval_id": approval["approval_id"] if approval else None,
        "added_companies": list(added),
    }
    return _Inputs(observations, judgments, sources, assumptions, note, continued_from)


def init_run(
    slug: str,
    *,
    as_of: str | None = None,
    title: str | None = None,
    request: str | None = None,
    purpose: str | None = None,
    companies: list[str] | None = None,
    baseline_id: str | None = None,
    rule_version: str | None = None,
    decisions: list[dict[str, Any]] | None = None,
    price_as_of: str | None = None,
    info_cutoff: str | None = None,
    force: bool = False,
    from_run: str | None = None,
    add_companies: list[str] | None = None,
    carry_decisions: bool = True,
) -> dict[str, Path]:
    if not slug.startswith("ai-scorecard-"):
        raise SchemaError("scorecard slug 는 `ai-scorecard-` 로 시작해야 한다 (예: ai-scorecard-2026-09-baseline)")
    d = run_dir(slug)
    if d.exists() and not force:
        raise SchemaError(f"실행 디렉터리가 이미 있음: {rel(d)} (--force 로 덮어쓰기)")
    registry = load_companies()

    prior_run: dict[str, Any] | None = None
    if from_run is not None:
        if from_run == slug:
            raise SchemaError("자기 자신을 이어받을 수 없다")
        prior_run = _load_prior_run(from_run)
    elif add_companies:
        raise SchemaError("--add-companies 는 --from-run 과 함께 쓴다 — 기준선에서 새로 만들 때는 --companies 로 대상을 정한다")

    # 기본값은 이전 실행에서 온다. `--rule` 을 안 주면 v1.5 로 떨어져 규칙이 뒷걸음질하는 것을 막는다.
    baseline_id = baseline_id or (prior_run["baseline_id"] if prior_run else "v1.5")
    rule_version = rule_version or (prior_run["rule_version"] if prior_run else "v1.5")
    as_of = as_of or (prior_run["as_of"] if prior_run else None)
    if not as_of:
        raise SchemaError("--as-of 가 필요하다 (--from-run 이면 이전 실행의 기준일을 그대로 쓴다)")
    title = title or (prior_run["title"] if prior_run else None)
    if not title:
        raise SchemaError("--title 이 필요하다")
    request = request or (f"이전 실행 {from_run} 이어받기" if prior_run else None)
    if not request:
        raise SchemaError("--request 가 필요하다")
    purpose = purpose or (prior_run["purpose"] if prior_run else "기준선 승계 재계산과 규칙·자료·판단의 일관성 확인")
    price_as_of = price_as_of or (prior_run.get("price_as_of") if prior_run else None)
    info_cutoff = info_cutoff or (prior_run.get("info_cutoff") if prior_run else None)

    rules = load_rules(rule_version)
    scores = base_obs = None
    if prior_run is None:
        scores, base_obs, _triggers = load_baseline(baseline_id)
        selected = list(companies or [c["company_id"] for c in scores["companies"]])
        added: list[str] = []
    else:
        selected = list(companies or prior_run["companies"])
        added = [c for c in (add_companies or []) if c not in selected]
        selected += added
    unknown = [c for c in selected if c not in registry]
    if unknown:
        raise SchemaError(f"알 수 없는 기업 {unknown}")
    if prior_run is not None:
        carried = prior_run["decisions"] if carry_decisions else []
        overridden = {r["id"] for r in (decisions or [])}
        decisions = [r for r in carried if r["id"] not in overridden] + list(decisions or [])
    created = today()
    inputs = (
        _inputs_from_baseline(slug, baseline_id=baseline_id, selected=selected, as_of=as_of, created=created,
                              rules=rules, registry=registry, scores=scores, base_obs=base_obs)
        if prior_run is None else
        _inputs_from_run(from_run, prior_run, slug=slug, selected=selected, added=added, as_of=as_of,
                         baseline_id=baseline_id, rules=rules, registry=registry)
    )
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
        "assumptions": inputs.assumptions,
    }
    if inputs.continued_from is not None:
        run["continued_from"] = inputs.continued_from
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "run.json", run)
    write_json(d / "observations.json", inputs.observations)
    write_json(d / "judgments.json", inputs.judgments)
    write_json(d / "sources.json", inputs.sources)
    for stale in ("results.json", "preview.md", "approval.json"):
        if (d / stale).exists():
            (d / stale).unlink()
    plan_text = render_plan(run, rules, registry, request=request, baseline_note=inputs.baseline_note)
    plan_path = run_paths(slug).plan
    plan_path.write_text(plan_text, encoding="utf-8", newline="\n")
    return {"plan": plan_path, "run": d / "run.json", "observations": d / "observations.json", "judgments": d / "judgments.json", "sources": d / "sources.json"}


# ------------------------------------------------------------------ research

def research(slug: str) -> Path:
    paths = run_paths(slug)
    _require_file(paths.plan, "plan")
    ctx = load_context(slug)
    text = render_research(ctx, hashes=ctx.hashes)
    path = paths.research
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ calculate

def calculate(slug: str) -> tuple[Path, Path, dict[str, Any]]:
    paths = run_paths(slug)
    _require_file(paths.plan, "plan")
    _require_file(paths.research, "research")
    ctx = load_context(slug)
    results = compute(ctx)
    path = write_results(slug, results)
    scores, _obs, _trig = load_baseline(ctx.run["baseline_id"])
    preview_path = paths.preview
    preview_path.write_text(render_preview(ctx, results, scores), encoding="utf-8", newline="\n")
    stale_approval = run_dir(slug) / "approval.json"
    if stale_approval.exists():
        approval = load_json_strict(stale_approval)
        if approval.get("hashes", {}).get("results") != results["results_hash"]:
            stale_approval.unlink()
    return path, preview_path, results


# ------------------------------------------------------------------ draft

def draft(slug: str) -> Path:
    paths = run_paths(slug)
    _require_file(paths.plan, "plan")
    _require_file(paths.research, "research")
    _require_file(results_path(slug), "results.json (calculate 먼저)")
    ctx = load_context(slug)
    results = load_results(slug)
    if results["input_hashes"] != ctx.hashes:
        raise SchemaError("입력(run/observations/judgments/rules)이 results.json 계산 이후 바뀜 — calculate 를 다시 실행")
    scores, _obs, triggers = load_baseline(ctx.run["baseline_id"])
    text = render_draft(ctx, results, scores, triggers)
    path = paths.draft
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ review template

def review_template(slug: str, *, force: bool = False) -> Path:
    paths = run_paths(slug)
    draft_path = paths.draft
    _require_file(draft_path, "draft")
    path = paths.review
    if path.exists() and not force:
        raise SchemaError(f"리뷰 파일이 이미 있음: {rel(path)} (--force 로 템플릿 재생성)")
    ctx = load_context(slug)
    results = load_results(slug)
    text = render_review_template(ctx, results, draft_hash=sha256_file(draft_path))
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ approve

def current_hashes(slug: str) -> dict[str, str]:
    ctx_hashes = input_hashes(slug)
    run = load_json_strict(run_dir(slug) / "run.json")
    rules = load_rules(run["rule_version"])
    draft_path = run_paths(slug).draft
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

    result = validate_contract(slug, require_html=False, check_html_if_present=False)
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
    paths = run_paths(slug)
    d = paths.run_dir
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
