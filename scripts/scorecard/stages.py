# scorecard 단계 실행: init(실행 생성) → collect → research → calculate(+preview) → draft → review-template → confirm·approve·revoke·summary. 순서·해시 결속·실행 잠금을 코드에서 강제한다.
from __future__ import annotations

import copy
import getpass
import json
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from report_contract_lib import read_markdown, rel

from . import evidence_lib
from .baseline_import import BASELINE_AS_OF, SRC_HANDOVER, SRC_HANDOVER_SHA256, SRC_HTML, SRC_MD, SRC_RULE, baseline_judgments
from .collect_filings import DEFAULT_FORMS, collect_company_filings
from .collect_news import collect_company_news
from .collect_prices import fetch_quote, price_observations, price_source_entry
from .engine import BASELINE_DIR, RunContext, compute, input_hashes, load_companies, load_context, load_results, results_path, run_dir, write_results
from .evidence_lib import source_entry, upsert_sources, utc_now_iso
from .paths import run_paths
from .render_md import REVIEW_AREAS, render_draft, render_plan, render_preview, render_research, render_review_template
from .rules import load_rules
from .schema import (APPROVAL_REQUIRED_HASHES, APPROVAL_VIA, FACTOR_IDS, JUDGMENT_EDIT_KIND, JUDGMENT_INPUT_CHOICES,
                     JUDGMENT_REVISION_FIELDS, SchemaError, approval_file_present, approval_id_for, load_json_strict,
                     sha256_file, sha256_obj, validate_approval, validate_cross_refs, validate_evidence, validate_judgments,
                     validate_observations, validate_proposals, validate_run, validate_sources, validate_triggers, write_json)


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
    evidence: dict[str, Any] | None = None   # 이어받기만. 판단·트리거가 인용한 근거(2026-10-01 레인 N, V2-2)
    triggers: dict[str, Any] | None = None


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
    # 2026-10-01 레인 N(V2-2): 트리거와, 판단·트리거가 인용한 근거 항목을 함께 옮긴다. 옮기지 않으면 출처 장부에는 근거의
    # 출처가 있는데 근거 항목만 없어 다음 실행의 모든 단계가 교차 참조에서 멈춘다. 근거는 확정 상태 그대로 옮긴다.
    prior_paths = run_paths(prior_slug)
    triggers = evidence = None
    if prior_paths.triggers.is_file():
        prior_trg = load_json_strict(prior_paths.triggers)
        items = [t for t in prior_trg.get("items", []) if t.get("company_id") in selected]
        triggers = {**prior_trg, "run_id": slug, "items": items} if items else None
    cited = {e for j in judgments["items"] for e in (j.get("evidence_ids") or [])}
    cited |= {e for t in (triggers or {}).get("items", []) for e in (t.get("evidence_ids") or [])}
    if prior_paths.evidence.is_file():
        prior_ev = load_json_strict(prior_paths.evidence)
        items = [e for e in prior_ev.get("items", []) if e.get("evidence_id") in cited]
        evidence = {**prior_ev, "run_id": slug, "items": items} if items else None

    hashes = input_hashes(prior_slug)
    approval = validate_approval(load_json_strict(d / "approval.json"), prior_slug) if approval_file_present(d) else None
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
    if evidence or triggers:
        note += (f". 판단·트리거가 인용한 근거 {len((evidence or {}).get('items', []))}건과 "
                 f"트리거 {len((triggers or {}).get('items', []))}건도 옮겼다")
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
    return _Inputs(observations, judgments, sources, assumptions, note, continued_from, evidence, triggers)


def _check_carried_refs(prior_slug: str, slug: str, inputs: _Inputs, registry: dict[str, dict[str, Any]]) -> None:
    """이어받은 입력의 교차 참조를 쓰기 전에 돌린다(2026-10-01 레인 N, V2-2). 맞지 않으면 아무것도 쓰지 않고 멈춘다 —
    조용히 성공한 뒤 다음 실행의 research·calculate·judge 가 멈추는 일을 없앤다."""
    try:
        source_items = validate_sources(inputs.sources, slug)
        source_ids = {s["source_id"] for s in source_items}
        ev_items = validate_evidence(inputs.evidence, registry, source_ids, slug) if inputs.evidence else None
        if inputs.triggers:
            validate_triggers(inputs.triggers, registry, {e["evidence_id"] for e in ev_items or []}, source_ids, slug)
        validate_cross_refs(inputs.observations["items"], inputs.judgments["items"], ev_items, source_items)
    except SchemaError as exc:
        raise SchemaError(f"init --from-run {prior_slug}: 이어받은 입력의 교차 참조가 맞지 않아 실행을 만들지 않았다 — {exc}. "
                          f"이전 실행의 evidence/evidence.json·triggers.json·sources.json 을 확인한다") from exc


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
    # 2026-10-01 레인 H(F-1): 덮어쓰면 아래에서 approval.json 이 지워진다. 승인 파괴는 사람만 한다.
    # 2026-10-01 레인 N(V2-1): 다른 단계와 같은 함수로 판정한다. init 은 무효 승인도 지우므로 파일 존재만 본다.
    if force:
        protect_approved_run(slug, "--force 로 재생성", any_approval=True)
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
        _check_carried_refs(from_run, slug, inputs, registry)
    d.mkdir(parents=True, exist_ok=True)
    write_json(d / "run.json", run)
    write_json(d / "observations.json", inputs.observations)
    write_json(d / "judgments.json", inputs.judgments)
    write_json(d / "sources.json", inputs.sources)
    carried_files: dict[str, Path] = {}
    if inputs.evidence is not None:
        carried_files["evidence"] = run_paths(slug).evidence
        write_json(carried_files["evidence"], inputs.evidence)
    if inputs.triggers is not None:
        carried_files["triggers"] = run_paths(slug).triggers
        write_json(carried_files["triggers"], inputs.triggers)
    for stale in ("results.json", "preview.md", "approval.json"):
        if (d / stale).exists():
            (d / stale).unlink()
    plan_text = render_plan(run, rules, registry, request=request, baseline_note=inputs.baseline_note)
    plan_path = run_paths(slug).plan
    plan_path.write_text(plan_text, encoding="utf-8", newline="\n")
    return {"plan": plan_path, "run": d / "run.json", "observations": d / "observations.json", "judgments": d / "judgments.json",
            "sources": d / "sources.json", **carried_files}


# ------------------------------------------------------------------ collect
# 2026-09-30 레인 E. research 앞에서만 돈다. build 는 재수집하지 않는다(D-02).
# 뉴스·공시는 수집 캐시(DATA_ROOT)를 갱신하고 후보 파일만 쓴다 — sources.json 은 선별된 근거가
# research 에서 등록될 때 바뀐다. 가격만 계산 입력이라 여기서 관측과 출처를 바로 등록한다.

COLLECT_KINDS = ("news", "filings", "prices")
CANDIDATE_WINDOW_DAYS = 180


def _cache_items(company_id: str, kind: str) -> list[dict[str, Any]]:
    base = evidence_lib.DATA_ROOT / company_id
    path = base / "news" / "google" / "normalized.json" if kind == "news" else base / "filings" / "index.json"
    return json.loads(path.read_text(encoding="utf-8")).get("items", []) if path.is_file() else []


def candidate_items(company_ids: list[str], *, since: str, until: str) -> list[dict[str, Any]]:
    """수집 캐시에서 창(since ≤ 발행일 ≤ until, C-17) 안의 후보를 고른다. 발행일이 없는 기사는 창을 판정할 수 없어 뺀다.

    시각 필드(first_seen·updated)는 넣지 않는다. 같은 캐시면 같은 목록이다.
    """
    items: list[dict[str, Any]] = []
    for cid in sorted(set(company_ids)):
        for a in _cache_items(cid, "news"):
            day = (a.get("published_at_utc") or "")[:10]
            if day and since <= day <= until:
                items.append({"candidate_id": a["article_id"], "company_id": cid, "kind": "news", "title": a["title"],
                              "url": a["url"], "published_at_utc": a["published_at_utc"], "source": dict(a["source"]),
                              "raw_ref": a["raw_ref"], "content_hash": a["content_hash"], "source_id": a["source_id"]})
        for f in _cache_items(cid, "filings"):
            day = f.get("filed_at") or ""
            if day and since <= day <= until:
                stable = {k: f.get(k) for k in ("accession", "form", "filed_at", "report_period", "primary_document", "items")}
                items_text = f" · Items {', '.join(f['items'])}" if f.get("items") else ""
                # 공시는 제출일만 있다. 시각을 지어내지 않으므로 published_at_utc 는 null 이고 날짜는 filed_at 에 둔다.
                items.append({"candidate_id": f["filing_id"], "company_id": cid, "kind": "filing",
                              "title": f"{f['form']} {day}{items_text}", "url": f["primary_doc_url"],
                              "published_at_utc": None, "filed_at": day, "form": f["form"],
                              "raw_ref": f["raw_ref"], "content_hash": sha256_obj(stable), "source_id": f["source_id"]})
    return sorted(items, key=lambda x: (x["company_id"], x["kind"], x["candidate_id"]))


def write_candidates(slug: str, *, since: str, until: str, company_ids: list[str]) -> Path:
    payload = {"schema": "scorecard.candidates/1", "run_id": slug, "window": {"since": since, "until": until},
               "items": candidate_items(company_ids, since=since, until=until)}
    path = run_paths(slug).candidates
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return path


def _collect_prices(slug: str, run: dict[str, Any], registry: dict[str, dict[str, Any]], selected: list[str], *,
                    from_file: str | None, dry_run: bool, now: str | None) -> list[dict[str, Any]]:
    """가격·시총 관측을 observations.json 에 더하고 SRC-YF-<price_as_of> 를 sources.json 에 등록한다. 덮어쓰지 않는다.

    2026-10-01 레인 J(F-M-2): 회사 하나의 실패가 전체를 막지 않는다. 조회·관측 생성·중복·스키마 검증을 회사 단위로 하고,
    실패한 회사는 `failed` 로 남기고 나머지만 기록한다.
    """
    price_as_of = run.get("price_as_of") or run["as_of"]
    source_id = f"SRC-YF-{price_as_of}"
    quotes = json.loads(Path(from_file).read_text(encoding="utf-8")) if from_file else None
    rows: list[dict[str, Any]] = []
    new_obs: list[dict[str, Any]] = []
    tickers: list[str] = []
    d = run_dir(slug)
    observations = None if dry_run else load_json_strict(d / "observations.json")
    for cid in selected:
        company = registry[cid]
        ticker = company.get("ticker")
        if not company.get("listed") or not ticker:
            rows.append({"company_id": cid, "status": "skipped_unlisted"})
            continue
        if dry_run:
            rows.append({"company_id": cid, "status": "dry_run", "ticker": ticker, "price_as_of": price_as_of})
            continue
        # 2026-10-01 V2-7: 같은 출처로 이미 기록된 회사는 다시 조회하지 않고 실패와 구분되는 상태로 낸다.
        if any(o["company_id"] == cid and o.get("source_id") == source_id for o in observations["items"]):
            rows.append({"company_id": cid, "status": "skipped_existing", "source_id": source_id})
            continue
        try:
            if quotes is not None and ticker not in quotes:
                raise ValueError(f"{from_file} 에 {ticker} 시세가 없다")
            quote = quotes[ticker] if quotes is not None else fetch_quote(ticker, price_as_of)
            obs = price_observations(company, quote, source_id=source_id)
            taken = {(o["company_id"], o["metric"], o["as_of"]) for o in observations["items"]}
            taken_ids = {o["observation_id"] for o in observations["items"]}
            clash = [o["observation_id"] for o in obs
                     if (o["company_id"], o["metric"], o["as_of"]) in taken or o["observation_id"] in taken_ids]
            if clash:
                raise SchemaError(f"같은 (기업, 지표, 기준일) 관측이 이미 있다 — 덮어쓰지 않는다: {clash}")
            # 이 회사의 관측까지 더한 상태로 검증한다. 실패하면 이 회사만 빠진다.
            validate_observations({**observations, "items": [*observations["items"], *obs]}, registry, slug)
        except Exception as exc:  # noqa: BLE001 — 기업 하나의 실패로 나머지를 멈추지 않는다
            rows.append({"company_id": cid, "status": "failed", "error": str(exc)})
            continue
        observations["items"].extend(obs)
        new_obs += obs
        tickers.append(ticker)
        row = {"company_id": cid, "status": "collected", "close_date": obs[0]["as_of"],
               "market_cap": obs[1]["status"], "method": obs[1]["basis"]["method"]}
        if quote.get("skipped_nonfinite_close"):
            row["skipped_nonfinite_close"] = list(quote["skipped_nonfinite_close"])
        rows.append(row)
    if dry_run or not new_obs:
        return rows

    validate_observations(observations, registry, slug)
    src_path = d / "sources.json"
    sources = load_json_strict(src_path) if src_path.is_file() else {"schema": "scorecard.sources/1", "run_id": slug, "items": []}
    _merge_price_source(sources, price_source_entry(price_as_of, tickers=tickers, accessed_at=now or utc_now_iso()))
    validate_sources(sources, slug)
    write_json(d / "observations.json", observations)
    write_json(src_path, sources)
    return rows


def _merge_price_source(sources: dict[str, Any], entry: dict[str, Any]) -> None:
    """SRC-YF 출처를 등록한다. 같은 id 가 이미 있으면 새 티커 주소를 publisher_url 에 덧붙이고 재조회 시각을 note 에 남긴다.

    2026-10-01 V2-7: 부분 실패 뒤 다시 수집한 회사의 관측이 자기 시세 주소가 없는 출처를 가리키던 것을 막는다.
    처음 조회 시각(accessed_at)과 첫 주소(url)는 바꾸지 않는다.
    """
    items = sources.setdefault("items", [])
    for item in items:
        if item["source_id"] != entry["source_id"]:
            continue
        urls = list(item.get("publisher_url") or [item["url"]])
        added = [u for u in (entry.get("publisher_url") or [entry["url"]]) if u not in urls]
        if added:
            item["publisher_url"] = urls + added
            more = f"재조회 {entry['accessed_at']}: " + ", ".join(u.rsplit("/", 1)[-1] for u in added)
            item["note"] = f"{item['note']} · {more}" if item.get("note") else more
        return
    items.append(entry)


def collect(
    slug: str,
    *,
    companies: list[str] | None = None,
    kinds: tuple[str, ...] | list[str] = COLLECT_KINDS,
    since: str | None = None,
    forms: list[str] | None = None,
    locale: str = "en-US",
    from_file: str | None = None,
    dry_run: bool = False,
    now: str | None = None,
) -> dict[str, Any]:
    """근거 후보를 모은다. `now` 는 테스트가 수집 시각을 고정할 때만 준다."""
    run = validate_run(load_json_strict(run_dir(slug) / "run.json"), slug)
    registry = load_companies()
    selected = list(companies or run["companies"])
    outside = [c for c in selected if c not in run["companies"]]
    if outside:
        raise SchemaError(f"run.companies 에 없는 기업 {outside}")
    kinds = tuple(kinds)
    unknown = [k for k in kinds if k not in COLLECT_KINDS]
    if unknown or not kinds:
        raise SchemaError(f"--kind 는 {list(COLLECT_KINDS)} 중에서 고른다 ({list(kinds)})")
    if from_file is not None and len(kinds) != 1:
        raise SchemaError("--from-file 은 --kind 하나와 함께 쓴다(파일 형식이 종류마다 다르다)")
    until = run.get("info_cutoff") or run["as_of"]
    try:
        since = since or (date.fromisoformat(run["as_of"]) - timedelta(days=CANDIDATE_WINDOW_DAYS)).isoformat()
        date.fromisoformat(since)
    except ValueError as exc:
        raise SchemaError(f"--since 는 YYYY-MM-DD ({since!r})") from exc
    if since > until:
        raise SchemaError(f"후보 창이 비어 있다: since {since} > info_cutoff {until}")
    if "prices" in kinds and not dry_run:   # 가격만 관측·출처(승인 해시 대상)를 바로 쓴다
        protect_approved_run(slug, "가격 수집(collect --kind prices)")

    summary: dict[str, Any] = {"run_id": slug, "window": {"since": since, "until": until}, "dry_run": dry_run,
                               "news": [], "filings": [], "prices": []}
    for cid in selected if "news" in kinds else []:
        try:
            res = collect_company_news(registry[cid], from_file=from_file, dry_run=dry_run, now=now, locale=locale)
            status = "dry_run" if dry_run else ("skipped_rate_limit" if res["skipped_rate_limit"] and not res["fetched"] else "collected")
            summary["news"].append({"company_id": cid, "status": status, "urls": res["urls"]})
        except Exception as exc:  # noqa: BLE001
            summary["news"].append({"company_id": cid, "status": "failed", "error": str(exc)})
    # 2026-10-01 레인 J(F-M-1): 공시를 모을 때만 SEC_UA 를 읽는다. 영문이 아니면 요청 전에 회사별 failed 로 남긴다.
    sec_ua, sec_ua_error = "", None
    if "filings" in kinds:
        try:
            sec_ua = evidence_lib.sec_user_agent()
        except RuntimeError as exc:
            sec_ua_error = str(exc)
    for cid in selected if "filings" in kinds else []:
        company = registry[cid]
        if not company.get("cik"):
            summary["filings"].append({"company_id": cid, "status": "skipped_no_cik"})
            continue
        if from_file is None and not dry_run and sec_ua_error:
            summary["filings"].append({"company_id": cid, "status": "failed", "error": sec_ua_error})
            continue
        if from_file is None and not dry_run and not sec_ua:
            # 전체를 실패시키지 않는다. 나머지 종류와 기업은 계속 돈다.
            summary["filings"].append({"company_id": cid, "status": "skipped_no_user_agent"})
            continue
        try:
            res = collect_company_filings(company, from_file=from_file, dry_run=dry_run, since=since,
                                          forms=set(forms) if forms else DEFAULT_FORMS, now=now)
            summary["filings"].append({"company_id": cid, "status": "dry_run" if dry_run else "collected", "urls": res["urls"]})
        except Exception as exc:  # noqa: BLE001
            summary["filings"].append({"company_id": cid, "status": "failed", "error": str(exc)})
    if not dry_run:
        summary["candidates"] = write_candidates(slug, since=since, until=until, company_ids=run["companies"])
    if "prices" in kinds:
        summary["prices"] = _collect_prices(slug, run, registry, selected, from_file=from_file, dry_run=dry_run, now=now)
    return summary


# ------------------------------------------------------------------ research

def _candidate_source_entry(candidate: dict[str, Any]) -> dict[str, Any]:
    """선별된 후보 하나의 sources.json 항목. 원문 해시는 캐시에 남은 raw 파일에서 센다(없으면 null)."""
    raw_ref = candidate["raw_ref"]
    raw = evidence_lib.DATA_ROOT / raw_ref.split("/", 1)[1] if raw_ref.startswith("data/") else evidence_lib.DATA_ROOT / raw_ref
    kind = "news" if candidate["kind"] == "news" else "filings"
    key = "article_id" if kind == "news" else "filing_id"
    cached = next((x for x in _cache_items(candidate["company_id"], kind) if x.get(key) == candidate["candidate_id"]), {})
    item: dict[str, Any] = {"source_id": candidate["source_id"], "title": candidate["title"], "url": candidate["url"],
                            "company_id": candidate["company_id"], "raw_ref": raw_ref}
    if kind == "news":
        item.update(publisher=candidate["source"].get("name") or "Google News",
                    publisher_url=candidate["source"].get("url") or None,
                    published_at_utc=candidate["published_at_utc"],
                    note="Google News RSS 후보에서 선별. url 은 Google 리다이렉트 링크다")
    else:
        item.update(publisher="SEC EDGAR", note=f"{candidate['form']} 제출일 {candidate['filed_at']}")
    return source_entry(item, kind="news" if kind == "news" else "filing",
                        raw_sha256=sha256_file(raw) if raw.is_file() else None,
                        accessed_at=cached.get("first_seen_utc") or utc_now_iso())


def register_evidence_sources(slug: str) -> list[str]:
    """evidence.json 이 인용한 후보의 출처를 sources.json 에 **추가만** 한다. 기존 id 는 건드리지 않는다.

    후보 파일에 없는 source_id 는 등록하지 않는다 — 그대로 두면 이어지는 엄격 검증이 장부에 없다고 막는다.
    """
    paths = run_paths(slug)
    if not paths.evidence.is_file():
        return []
    cited = sorted({e.get("source_id") for e in load_json_strict(paths.evidence).get("items", []) if e.get("source_id")})
    src_path = run_dir(slug) / "sources.json"
    sources = load_json_strict(src_path) if src_path.is_file() else {"schema": "scorecard.sources/1", "run_id": slug, "items": []}
    have = {s["source_id"] for s in sources.get("items", [])}
    need = [sid for sid in cited if sid not in have]
    if not need:
        return []
    candidates = load_json_strict(paths.candidates).get("items", []) if paths.candidates.is_file() else []
    by_sid = {c["source_id"]: c for c in candidates}
    entries = [_candidate_source_entry(by_sid[sid]) for sid in need if sid in by_sid]
    if not entries:
        return []
    upsert_sources(sources, entries)
    validate_sources(sources, slug)
    write_json(src_path, sources)
    return [e["source_id"] for e in entries]


def research(slug: str, *, register: bool = True) -> Path:
    paths = run_paths(slug)
    _require_file(paths.plan, "plan")
    protect_approved_run(slug, "research 재생성")
    if register:
        register_evidence_sources(slug)
    ctx = load_context(slug)
    _scores, _obs, legacy_triggers = load_baseline(ctx.run["baseline_id"])
    text = render_research(ctx, hashes=ctx.hashes, legacy_triggers=legacy_triggers)
    path = paths.research
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ calculate

def calculate(slug: str) -> tuple[Path, Path, dict[str, Any]]:
    paths = run_paths(slug)
    _require_file(paths.plan, "plan")
    _require_file(paths.research, "research")
    was_valid = protect_approved_run(slug, "재계산(calculate)")
    ctx = load_context(slug)
    results = compute(ctx)
    path = write_results(slug, results)
    scores, _obs, _trig = load_baseline(ctx.run["baseline_id"])
    preview_path = paths.preview
    preview_path.write_text(render_preview(ctx, results, scores), encoding="utf-8", newline="\n")
    if approval_file_present(run_dir(slug)):
        stale_approval = run_dir(slug) / "approval.json"
        approval = load_json_strict(stale_approval)
        approved_results = (approval.get("hashes") or {}).get("results")
        if approved_results != results["results_hash"]:
            # 2026-10-01 레인 N(V2-1): 지운 사실을 출력하고 revocations.jsonl 에 남긴다. 원인은 revoked_by·note 로 가린다.
            reason = ("유효했던 승인을 재계산 결과가 바꿔 지웠다" if was_valid
                      else "무효 승인 정리: 승인 뒤 입력이 바뀐 실행을 재계산해 결과가 달라졌다")
            _append_revocation(slug, approval, by="calculate",
                               note=f"{reason}(승인 results {str(approved_results)[:16]}… → 지금 {results['results_hash'][:16]}…)")
            stale_approval.unlink()
            print(f"[알림] 재계산 결과 해시가 승인과 달라 approval.json 을 지웠다({reason}). "
                  f"기록: {rel(run_dir(slug) / 'revocations.jsonl')}. 다시 리뷰한 뒤 사람이 승인 페이지에서 승인한다")
    return path, preview_path, results


# ------------------------------------------------------------------ draft

def draft(slug: str) -> Path:
    paths = run_paths(slug)
    _require_file(paths.plan, "plan")
    _require_file(paths.research, "research")
    _require_file(results_path(slug), "results.json (calculate 먼저)")
    protect_approved_run(slug, "초안 재생성(draft)")
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
    if force:
        protect_approved_run(slug, "리뷰 템플릿 재생성(review-template --force)")
    ctx = load_context(slug)
    results = load_results(slug)
    text = render_review_template(ctx, results, draft_hash=sha256_file(draft_path))
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ 세션 판정·실행 잠금
# 2026-09-30 레인 F. 에이전트 터미널에만 있고 사람이 여는 일반 Orca 셸에는 없는 것을 두 셸의 환경변수를
# 직접 비교해 골랐다(validation/lane-F-approval/REPORT.md 의 표). `ORCA_*` 는 사람 셸에도 있어서 넣지 않는다.
# 2026-10-01 레인 J: Muse 세션 표지 `MUSE_TOOL_USE_ID`(도구 호출 때만 생기는 값, validation/lane-M-live-collection/REPORT.md §4).
# `MUSE_RELEASE_INFO` 는 사람 셸과 비교하지 못해 넣지 않는다.
AGENT_ENV_MARKERS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "ORCA_AGENT_LAUNCH_TOKEN", "AI_AGENT", "MUSE_TOOL_USE_ID")
# 잠금을 검사하고 쓰는 단계. approve·revoke·build 는 사람 행위라 잠금을 요구하지도 쓰지도 않는다.
LOCK_STAGES = ("init", "collect", "research", "calculate", "draft", "review-template", "confirm", "judge")


def agent_session_markers(env: Mapping[str, str] | None = None) -> list[str]:
    """지금 프로세스가 에이전트 세션이면 그 근거가 된 변수 이름들. 빈 목록이면 사람 세션이다. **판정은 여기 한 곳이다.**"""
    env = os.environ if env is None else env
    return [key for key in AGENT_ENV_MARKERS if (env.get(key) or "").strip()]


def refuse_agent_session(action: str, *, allow_agent_session: bool = False) -> None:
    """승인·취소는 사람 행위다. 에이전트 세션이면 거부한다. 2026-10-01 레인 H(F-2): CLI 가 아니라 stage 함수 본체에서
    부른다 — import 로 함수를 직접 부르는 호출자도 같은 판정을 거친다. `allow_agent_session` 은 테스트 전용이고 CLI 는 노출하지 않는다."""
    markers = agent_session_markers()
    if markers and not allow_agent_session:
        raise SchemaError(f"에이전트 세션({', '.join(markers)})에서는 {action}할 수 없다. "
                          "사람이 `node server.js --approvals` 승인 페이지에서 한다")


def protect_approved_run(slug: str, action: str, *, any_approval: bool = False) -> bool:
    """승인된 실행의 입력·산출물을 바꾸는 단계 앞에서 부른다. 2026-10-01 레인 N(V2-1): 승인 파괴는 사람만 한다.

    유효한 승인이 있으면 에이전트 세션은 거부하고 사람 세션은 경고를 낸 뒤 진행한다. 무효 승인은 막지 않는다 — 사람이 승인
    페이지에서 판단을 고친 뒤 에이전트가 research → calculate → draft → review 를 다시 돌리는 흐름이다. 유효성을 판정하지
    못하면 에이전트는 거부한다. `any_approval` 은 `init --force` 처럼 무효 승인까지 지우는 단계가 쓴다(파일 존재만 본다).
    세션 판정은 `agent_session_markers` 한 곳이고, 돌려주는 값은 유효한(any_approval 이면 있던) 승인을 지나쳤는지다."""
    d = run_dir(slug)
    if any_approval:
        if not (d / "approval.json").is_file():
            return False
        state = "승인된"
    else:
        if not approval_file_present(d):
            return False
        try:
            if not approval_is_valid(slug, load_json_strict(d / "approval.json")):
                return False
            state = "승인이 유효한"
        except SchemaError as exc:
            state = f"승인 유효성을 판정할 수 없는({exc})"
    markers = agent_session_markers()
    if markers:
        raise SchemaError(f"에이전트 세션({', '.join(markers)})에서는 {state} 실행 {rel(d)} 에서 {action}할 수 없다. "
                          "승인 기록이 지워진다(또는 무효가 된다) — 새 slug 로 init(--from-run) 하거나 사람이 한다")
    print(f"[경고] {state} 실행 {rel(d)} 에서 {action}한다. 승인 기록이 지워지거나 무효가 된다 — 다시 리뷰한 뒤 사람이 승인 페이지에서 승인한다")
    return True


def protect_baseline_consumers(baseline_id: str) -> list[str]:
    """기준선을 다시 이관하기 전에 부른다. 2026-10-01 레인 N(V2-1). 기준선은 승인 해시 밖의 재빌드 입력이라 바꿔도 승인이
    유효한 채 남고 재빌드 리포트만 달라진다. 그 기준선을 쓰는 유효 승인 실행이 있으면 에이전트 세션은 거부하고 사람 세션은
    경고한다. 세션 판정은 `agent_session_markers` 한 곳이다. 돌려주는 값은 그 실행들이다."""
    out_dir = run_dir("_").parent
    consumers = []
    for d in sorted(p for p in out_dir.iterdir() if p.is_dir()) if out_dir.is_dir() else []:
        if not approval_file_present(d) or not (d / "run.json").is_file():
            continue
        try:
            uses = load_json_strict(d / "run.json").get("baseline_id") == baseline_id
            valid = uses and approval_is_valid(d.name, load_json_strict(d / "approval.json"))
        except SchemaError:
            valid = uses = True   # 판정하지 못하면 소비하는 유효 승인으로 본다
        if uses and valid:
            consumers.append(d.name)
    if not consumers:
        return []
    markers = agent_session_markers()
    if markers:
        raise SchemaError(f"에이전트 세션({', '.join(markers)})에서는 기준선 {baseline_id} 를 다시 이관할 수 없다. "
                          f"이 기준선을 쓰는 승인 실행 {consumers} 의 재빌드 리포트가 승인 없이 바뀐다 — 사람이 한다")
    print(f"[경고] 기준선 {baseline_id} 를 쓰는 승인 실행 {consumers} 가 있다. 승인 해시는 기준선을 담지 않아 승인이 유효한 채 "
          "재빌드 리포트가 바뀔 수 있다 — 바뀐 기준선을 git 으로 확인한다")
    return consumers


def lock_owner(env: Mapping[str, str] | None = None) -> str:
    """잠금 소유자: `SCORECARD_AGENT`, 없으면 `ORCA_TERMINAL_HANDLE`, 없으면 OS 사용자명. 훅(guard.lock_owner)도 같은 규칙이다."""
    env = os.environ if env is None else env
    for key in ("SCORECARD_AGENT", "ORCA_TERMINAL_HANDLE"):
        value = (env.get(key) or "").strip()
        if value:
            return value
    return getpass.getuser()


def lock_path(slug: str) -> Path:
    return run_dir(slug) / ".lock"


def read_lock(slug: str) -> dict[str, Any] | None:
    """잠금이 없으면 None. 읽을 수 없는 잠금은 소유자를 모르는 잠금으로 본다(누구의 것도 아니므로 인수해야 한다)."""
    path = lock_path(slug)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"owner": ""}
    return data if isinstance(data, dict) else {"owner": ""}


def claim_lock(slug: str, stage: str, *, take_lock: bool = False, env: Mapping[str, str] | None = None,
               write: bool = True) -> Path | None:
    """단계 앞에서 부른다. 다른 소유자의 잠금이면 거부하고 `take_lock` 이면 인수한다.

    단계가 끝나도 잠금은 남긴다 — 한 에이전트가 실행을 끝까지 맡는다. 실행 폴더가 없으면 쓰지 않는다
    (그 단계가 스스로 선행 산출물 오류를 낸다). `write=False` 는 `init` 처럼 폴더를 만들기 전에 검사만 할 때 쓴다.
    """
    if stage not in LOCK_STAGES:
        raise SchemaError(f"잠금 대상 단계가 아니다: {stage}")
    me = lock_owner(env)
    held = read_lock(slug)
    if held is not None and held.get("owner") != me and not take_lock:
        raise SchemaError(f"{rel(lock_path(slug))}: 다른 소유자({held.get('owner') or '알 수 없음'}, "
                          f"{held.get('stage') or '?'} 단계, {held.get('started_utc') or '?'})가 이 실행을 맡고 있다 — 인수하려면 --take-lock")
    if not write or not run_dir(slug).is_dir():
        return None
    started = held.get("started_utc") if held is not None and held.get("owner") == me else None
    path = lock_path(slug)
    path.write_text(json.dumps({"owner": me, "started_utc": started or utc_now_iso(), "stage": stage}, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8", newline="\n")
    return path


# ------------------------------------------------------------------ approve

def current_hashes(slug: str) -> dict[str, str]:
    ctx_hashes = input_hashes(slug)
    run = load_json_strict(run_dir(slug) / "run.json")
    rules = load_rules(run["rule_version"])
    draft_path = run_paths(slug).draft
    out = {
        "rules": rules.hash,
        "observations": ctx_hashes["observations"],
        "judgments": ctx_hashes["judgments"],
        "run": ctx_hashes["run"],
        "results": load_results(slug)["results_hash"] if results_path(slug).is_file() else "",
        "draft": sha256_file(draft_path) if draft_path.is_file() else "",
        # 2026-09-30 레인 E: 출처 장부도 승인 대상이다. 근거·트리거는 파일이 있을 때만 키가 생긴다.
        "sources": ctx_hashes["sources"],
    }
    for key in ("evidence", "triggers"):
        if key in ctx_hashes:
            out[key] = ctx_hashes[key]
    return out


def approval_mismatches(approved: dict[str, str], current: dict[str, str]) -> list[str]:
    """승인 해시와 현재 해시가 어긋나는 키. 빈 목록이면 승인이 유효하다. **대조 규칙은 여기 한 곳이다.**

    2026-09-30 레인 E. 승인에 있는 키만 현재와 대조한다 — 기존 두 실행의 승인은 6키이고 sources 를
    담지 않으므로, sources 는 승인에 있을 때만 본다. 다만 근거·트리거 파일이 지금 있는데 승인에 그 키가
    없으면 승인 뒤에 근거가 생긴 것이므로 무효다. 새 승인(`approve`)은 `current_hashes` 전체를 담는다.
    """
    differing = {k for k, v in approved.items() if current.get(k) != v}
    differing |= {k for k in APPROVAL_REQUIRED_HASHES if k not in approved}
    differing |= {k for k in ("evidence", "triggers") if k in current and k not in approved}
    return sorted(differing)


def approval_is_valid(slug: str, approval: Any, current: dict[str, str] | None = None) -> bool:
    """승인 기록이 형식(approval_id 재계산 포함)을 지키고 해시가 지금과 같은가. 2026-10-01 레인 N(V2-3): 해시만 대조하면
    손으로 쓴 승인(임의 approval_id)도 유효로 보였다. 빌드(`validate_approval`)와 같은 기준으로 본다."""
    try:
        validate_approval(approval, slug)
    except SchemaError:
        return False
    return not approval_mismatches(approval["hashes"], current if current is not None else current_hashes(slug))


def approve(slug: str, *, approved_by: str, note: str | None = None, via: str = "terminal",
            allow_agent_session: bool = False) -> Path:
    from validate_report_contract import validate_contract

    refuse_agent_session("승인", allow_agent_session=allow_agent_session)
    # 승인자는 사람의 식별자다. 빈 값이나 자동 생성 이름으로 승인 기록을 만들지 않는다 (D-02).
    if not isinstance(approved_by, str) or not approved_by.strip():
        raise SchemaError("승인자(--by)는 비어 있지 않은 문자열이어야 한다. 임의의 승인자를 만들지 말고 실제 사용자 식별자를 쓴다")
    approved_by = approved_by.strip()
    if via not in APPROVAL_VIA:
        raise SchemaError(f"승인 경로(--via)는 {list(APPROVAL_VIA)} 중 하나 ({via!r})")

    result = validate_contract(slug, require_html=False, check_html_if_present=False)
    if not result.ok:
        raise SchemaError("승인 전 계약 검증 실패: " + "; ".join(result.errors[:5]))
    hashes = current_hashes(slug)
    approval_id = approval_id_for(slug, hashes)
    payload = {
        "schema": "scorecard.approval/1",
        "run_id": slug,
        "approval_id": approval_id,
        "approved_by": approved_by,
        "approved_at": today(),
        "hashes": hashes,
        "note": note,
        # 2026-09-30 레인 F: 승인 페이지(browser)인지 터미널인지. 기존 두 실행의 승인에는 없는 선택 키다.
        "approved_via": via,
    }
    path = run_dir(slug) / "approval.json"
    write_json(path, payload)
    return path


# ------------------------------------------------------------------ revoke

def revoke(slug: str, *, by: str, note: str, allow_agent_session: bool = False) -> Path:
    """승인을 취소한다. `approval.json` 을 지우고 `revocations.jsonl` 에 한 줄을 더한다(지우기 전 승인의 id·해시를 남긴다)."""
    refuse_agent_session("승인 취소", allow_agent_session=allow_agent_session)
    if not isinstance(by, str) or not by.strip():
        raise SchemaError("취소자(--by)는 비어 있지 않은 문자열이어야 한다")
    if not isinstance(note, str) or not note.strip():
        raise SchemaError("취소 사유(--note)는 비어 있으면 안 된다")
    path = run_dir(slug) / "approval.json"
    if not approval_file_present(path.parent):
        raise SchemaError(f"취소할 승인이 없다: {rel(path)}")
    approval = validate_approval(load_json_strict(path), slug)
    log = _append_revocation(slug, approval, by=by.strip(), note=note.strip())
    path.unlink()
    return log


def _append_revocation(slug: str, approval: dict[str, Any], *, by: str, note: str) -> Path:
    """`revocations.jsonl` 에 한 줄을 더한다. 사람의 취소(`revoke`)와 재계산의 승인 삭제(`calculate`)가 같은 형식을 쓴다."""
    entry = {"revoked_by": by, "revoked_at": utc_now_iso(), "note": note,
             "approval_id": approval.get("approval_id"), "hashes": approval.get("hashes")}
    log = run_dir(slug) / "revocations.jsonl"
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return log


# ------------------------------------------------------------------ confirm
# 2026-09-30 레인 F. 근거 확정은 승인이 아니다. 확정하면 evidence 해시가 바뀌어 research 부터 다시 밟고 사람이 다시 승인한다.
EVIDENCE_ID_RE = re.compile(r"^EV-[a-z0-9-]+-\d{3}$")


def confirm(slug: str, *, evidence_ids: list[str] | tuple[str, ...] = (), reject_ids: list[str] | tuple[str, ...] = (),
            reviewer: str | None = None, reviewed_at: str | None = None) -> dict[str, Any]:
    """근거를 확정(`status: confirmed`·`reviewer`·`reviewed_at`)하거나 거부(항목 삭제)한다. 쓴 뒤 실행 전체를 다시 검증하고,
    검증이 실패하면 원래 파일로 되돌린다(거부한 근거를 트리거·판단이 인용하면 여기서 멈춘다)."""
    ids, rejects = list(evidence_ids), list(reject_ids)
    bad = [e for e in ids + rejects if not isinstance(e, str) or not EVIDENCE_ID_RE.match(e)]
    if bad:
        raise SchemaError(f"근거 ID 형식이 아니다(EV-<기업>-NNN): {bad}")
    if not ids and not rejects:
        raise SchemaError("확정(--evidence)하거나 거부(--reject)할 근거 ID 가 필요하다")
    both = sorted(set(ids) & set(rejects))
    if both:
        raise SchemaError(f"같은 근거를 확정하면서 거부할 수 없다: {both}")
    path = run_paths(slug).evidence
    if not path.is_file():
        raise SchemaError(f"근거 파일이 없다: {rel(path)}")
    original = path.read_bytes()
    payload = load_json_strict(path)
    have = {e["evidence_id"] for e in payload["items"]}
    unknown = [e for e in ids + rejects if e not in have]
    if unknown:
        raise SchemaError(f"evidence.json 에 없는 근거 ID: {unknown}")
    protect_approved_run(slug, "근거 확정·거부(confirm)")
    reviewer = (reviewer or "").strip() or (os.environ.get("SCORECARD_AGENT") or "").strip() or getpass.getuser()
    reviewed_at = reviewed_at or utc_now_iso()[:10]   # UTC 날짜
    confirmed, already = [], []
    for item in payload["items"]:
        if item["evidence_id"] not in ids:
            continue
        if item.get("status") == "confirmed":
            already.append(item["evidence_id"])
            continue
        item.update(status="confirmed", reviewer=reviewer, reviewed_at=reviewed_at)
        confirmed.append(item["evidence_id"])
    payload["items"] = [e for e in payload["items"] if e["evidence_id"] not in rejects]
    write_json(path, payload)
    try:
        load_context(slug)
    except BaseException:   # 2026-10-01 V2-10: 형식 오류가 아닌 예외에서도 검증 안 된 파일을 남기지 않는다
        path.write_bytes(original)
        raise
    return {"confirmed": confirmed, "already_confirmed": already, "rejected": rejects, "reviewer": reviewer,
            "reviewed_at": reviewed_at, "evidence_hash": sha256_file(path)}


# ------------------------------------------------------------------ judge
# 2026-10-01 레인 J(사용자 결정). 사람이 승인 페이지에서 정성 판단 **입력**을 고친다. results.json 의 점수를 덮어쓰지 않는다 —
# 재계산이 수정을 지우고 입력과 점수가 갈라진다. 고치면 judgments 해시가 바뀌어 research → calculate → draft → review 를 다시 거친 뒤
# 사람이 승인한다. 승인이 아니므로 에이전트도 부를 수 있고, reviewer 는 받은 이름(`by`)이다.

def _check_judgment_changes(factor: str, changes: Mapping[str, Any]) -> str:
    """판단 수정·제안이 받는 값의 형식 검사. 돌려주는 값은 판정 종류(edit kind)다. 2026-10-01 제안 흐름과 함께 쓰려고 뽑았다."""
    if factor not in JUDGMENT_EDIT_KIND:
        raise SchemaError(f"{factor} 판단은 승인 페이지에서 고치지 않는다(대상 {sorted(JUDGMENT_EDIT_KIND)})")
    if not isinstance(changes, Mapping) or not changes:
        raise SchemaError("고칠 값이 없다(--set key=value 또는 --evidence)")
    kind = JUDGMENT_EDIT_KIND[factor]
    allowed = {"score", "evidence"} if kind == "score" else {*JUDGMENT_INPUT_CHOICES[kind], "evidence"}
    unknown = sorted(set(changes) - allowed)
    if "score" in unknown:
        raise SchemaError(f"{factor} 의 점수는 규칙이 판정 재료에서 계산한다 — 점수 칸은 고치지 않는다. 고칠 수 있는 것: {sorted(allowed)}")
    if unknown:
        raise SchemaError(f"{factor}({kind}) 에서 고칠 수 없는 키 {unknown}. 고칠 수 있는 것: {sorted(allowed)}")
    if "evidence" in changes and not (isinstance(changes["evidence"], list)
                                      and all(isinstance(e, str) and e.strip() for e in changes["evidence"])):
        raise SchemaError("evidence 는 비어 있지 않은 문장 목록이어야 한다")
    # 2026-10-01 V2-10: 허용값은 모두 문자열·정수다. 중첩 값이 스키마의 `in` 비교까지 가서 추적 출력으로 끝나지 않게 먼저 거른다.
    bad_type = sorted(k for k, v in changes.items() if k != "evidence" and (isinstance(v, bool) or not isinstance(v, (str, int))))
    if bad_type:
        raise SchemaError(f"{factor} 의 값은 문자열이나 정수여야 한다: {bad_type}")
    return kind


def revise_judgment(slug: str, *, company_id: str, factor: str, changes: Mapping[str, Any], reason: str, by: str,
                    revised_at: str | None = None, cite_evidence_ids: list[str] | None = None) -> dict[str, Any]:
    """`judgments.json` 의 (기업, factor) 판단 하나를 고친다. 이전 값은 그 항목의 `revision_history` 에 남긴다.

    F1·F4·F8 은 `score`·`evidence`, F3·F5·F7·F9 는 판정 재료(inputs 키)·`evidence` 만 받는다. 그 factor 들의 점수 칸은
    규칙이 계산하므로 받지 않는다. 형식은 쓰기 전에 스키마로 검증하고, 실행 전체 검증(교차 참조)이 실패하면 원래 파일로 되돌린다.
    `cite_evidence_ids` 는 판단의 `evidence_ids` 에 더할 근거다(2026-10-01 제안 반영). 새 판단이라 확정 근거만 받는다.
    """
    if factor not in JUDGMENT_EDIT_KIND:
        raise SchemaError(f"{factor} 판단은 승인 페이지에서 고치지 않는다(대상 {sorted(JUDGMENT_EDIT_KIND)})")
    if not isinstance(by, str) or not by.strip():
        raise SchemaError("수정자(--by)는 비어 있지 않은 문자열이어야 한다")
    if not isinstance(reason, str) or not reason.strip():
        raise SchemaError("수정 사유(--reason)는 비어 있으면 안 된다")
    kind = _check_judgment_changes(factor, changes)

    protect_approved_run(slug, "판단 수정(judge)")
    path = run_dir(slug) / "judgments.json"
    original = path.read_bytes()
    payload = load_json_strict(path)
    idx = next((i for i, j in enumerate(payload["items"]) if j["company_id"] == company_id and j["factor"] == factor), None)
    if idx is None:
        raise SchemaError(f"judgments.json 에 {company_id} {factor} 판단이 없다")
    item = payload["items"][idx]
    previous = {k: copy.deepcopy(item.get(k)) for k in JUDGMENT_REVISION_FIELDS}
    new = dict(item)
    if kind == "score":
        if "score" in changes:
            new["score"] = changes["score"]
    else:
        # F7 승계 항목 둘은 kind 가 score 다. 판정 재료를 고치면 matrix 로 바뀌고 점수는 규칙이 계산한다(키가 다 있어야 한다).
        inputs = dict(item["inputs"]) if item["kind"] == kind else {}
        inputs.update({k: v for k, v in changes.items() if k != "evidence"})
        new.update(kind=kind, score=None, inputs=inputs)
    if "evidence" in changes:
        new["evidence"] = [e.strip() for e in changes["evidence"]]
    if cite_evidence_ids:
        new["evidence_ids"] = sorted({*(item.get("evidence_ids") or []), *cite_evidence_ids})
    if all(new.get(k) == item.get(k) for k in ("kind", "score", "inputs", "evidence")):
        raise SchemaError(f"{company_id} {factor}: 바뀐 값이 없다")
    revised_at = revised_at or utc_now_iso()[:10]   # UTC 날짜
    new.update(status="new", reviewer=by.strip(), reviewed_at=revised_at)
    # 2026-10-01 V2-11: --by 는 확인할 수 없는 이름이다. 누가 고쳤는지 가리도록 세션 종류를 함께 남긴다.
    session = "agent" if agent_session_markers() else "human"
    new["revision_history"] = [*item.get("revision_history", []),
                               {"revised_at": revised_at, "revised_by": by.strip(), "reason": reason.strip(), "previous": previous,
                                "session": session}]
    payload["items"][idx] = new

    run = validate_run(load_json_strict(run_dir(slug) / "run.json"), slug)
    validate_judgments(payload, load_companies(), load_rules(run["rule_version"]).payload, slug)   # 쓰기 전에 형식 검증
    write_json(path, payload)
    try:
        load_context(slug)
    except BaseException:   # 2026-10-01 V2-10: 형식 오류가 아닌 예외에서도 검증 안 된 파일을 남기지 않는다
        path.write_bytes(original)
        raise
    return {"judgment_id": new["judgment_id"], "company_id": company_id, "factor": factor, "kind": new["kind"],
            "previous": previous, "current": {k: new.get(k) for k in JUDGMENT_REVISION_FIELDS},
            "judgments_hash": sha256_file(path)}


# ------------------------------------------------------------------ proposals
# 2026-10-01 사용자 요청. research 뒤 에이전트가 바꾸고 싶은 판단을 제안으로 써 두면 사람이 승인 페이지에서 반영·거부만 한다.
# 제안을 쓰는 것은 에이전트도 한다. 반영·거부는 사람 행위라 에이전트 세션이면 거부한다. 거부는 사유가 필수다.

def _judgment_snapshot(j: Mapping[str, Any]) -> dict[str, Any]:
    return {"kind": j["kind"], "score": j.get("score"), "inputs": copy.deepcopy(j.get("inputs") or {}),
            "evidence": list(j.get("evidence") or [])}


def _load_proposals(slug: str) -> dict[str, Any]:
    paths = run_paths(slug)
    if not paths.proposals.is_file():
        return {"schema": "scorecard.proposals/1", "run_id": slug, "items": []}
    payload = load_json_strict(paths.proposals)
    ev_ids = {e["evidence_id"] for e in load_json_strict(paths.evidence).get("items", [])} if paths.evidence.is_file() else set()
    validate_proposals(payload, load_companies(), ev_ids, slug)
    return payload


def _find_judgment(slug: str, company_id: str, factor: str) -> dict[str, Any]:
    items = load_json_strict(run_dir(slug) / "judgments.json")["items"]
    j = next((x for x in items if x["company_id"] == company_id and x["factor"] == factor), None)
    if j is None:
        raise SchemaError(f"judgments.json 에 {company_id} {factor} 판단이 없다")
    return j


def add_proposal(slug: str, *, company_id: str, factor: str, changes: Mapping[str, Any] | None = None,
                 evidence_after: list[str] | None = None, reason: str, evidence_ids: list[str] | tuple[str, ...] = (),
                 by: str | None = None, proposed_at: str | None = None) -> dict[str, Any]:
    """판단 변경 제안 하나를 proposals.json 에 더한다. 지금 판단 값(before)을 함께 적어 두어, 반영 시점에 판단이 그사이
    바뀌었는지 가린다. 같은 (기업, factor) 에 결정 전 제안이 이미 있으면 거부한다."""
    changes = dict(changes or {})
    if evidence_after is not None:
        evidence_after = [s.strip() for s in evidence_after]
    _check_judgment_changes(factor, {**changes, **({"evidence": evidence_after} if evidence_after is not None else {})})
    if not isinstance(reason, str) or not reason.strip():
        raise SchemaError("제안 사유(--reason)는 비어 있으면 안 된다")
    current = _find_judgment(slug, company_id, factor)
    payload = _load_proposals(slug)
    if any(p["status"] == "pending" and p["company_id"] == company_id and p["factor"] == factor for p in payload["items"]):
        raise SchemaError(f"{company_id} {factor} 에 결정 전 제안이 이미 있다 — 그 제안을 먼저 반영하거나 거부한다")
    nums = [int(p["proposal_id"][4:]) for p in payload["items"]]
    item = {
        "proposal_id": f"PRP-{(max(nums) + 1 if nums else 1):03d}",
        "company_id": company_id,
        "factor": factor,
        "changes": changes,
        "evidence_after": evidence_after,
        "reason": reason.strip(),
        "evidence_ids": sorted(set(evidence_ids)),
        "before": _judgment_snapshot(current),
        "proposed_by": (by or "").strip() or (os.environ.get("SCORECARD_AGENT") or "").strip() or getpass.getuser(),
        "proposed_at": proposed_at or utc_now_iso()[:10],
        "status": "pending",
    }
    payload["items"].append(item)
    ev_ids = {e["evidence_id"] for e in load_json_strict(run_paths(slug).evidence).get("items", [])} if run_paths(slug).evidence.is_file() else set()
    validate_proposals(payload, load_companies(), ev_ids, slug)
    write_json(run_paths(slug).proposals, payload)
    return item


def decide_proposal(slug: str, proposal_id: str, *, accept: bool, by: str | None = None, note: str | None = None,
                    allow_agent_session: bool = False) -> dict[str, Any]:
    """제안을 반영하거나 거부한다. 사람 행위라 에이전트 세션이면 거부한다(`allow_agent_session` 은 테스트 전용).
    반영은 revise_judgment 로 판단을 고치고 인용 근거를 판단의 evidence_ids 에 더한다. 거부는 사유가 필수다."""
    refuse_agent_session("판단 변경 제안 반영·거부", allow_agent_session=allow_agent_session)
    payload = _load_proposals(slug)
    item = next((p for p in payload["items"] if p["proposal_id"] == proposal_id), None)
    if item is None:
        raise SchemaError(f"proposals.json 에 {proposal_id} 가 없다")
    if item["status"] != "pending":
        raise SchemaError(f"{proposal_id} 는 이미 결정됐다({item['status']})")
    by = (by or "").strip() or getpass.getuser()
    note = (note or "").strip() or None
    decided_at = utc_now_iso()[:10]
    out: dict[str, Any] = {"proposal_id": proposal_id, "accepted": accept}
    if not accept:
        if not note:
            raise SchemaError("거부 사유(--note)를 적어야 한다. 다음 실행에서 같은 제안이 올라올 때 참고한다")
        item.update(status="rejected", decided_by=by, decided_at=decided_at, decision_note=note)
    else:
        current = _find_judgment(slug, item["company_id"], item["factor"])
        if _judgment_snapshot(current) != item["before"]:
            raise SchemaError(f"{proposal_id} 를 쓴 뒤 {item['company_id']} {item['factor']} 판단이 바뀌었다 — "
                              "이 제안은 거부하고 지금 판단을 기준으로 다시 제안받는다")
        changes = dict(item["changes"])
        if item["evidence_after"] is not None:
            changes["evidence"] = list(item["evidence_after"])
        reason = f"제안 {proposal_id} 반영: {item['reason']}" + (f" (메모: {note})" if note else "")
        out["judgment"] = revise_judgment(slug, company_id=item["company_id"], factor=item["factor"], changes=changes,
                                          reason=reason, by=by, cite_evidence_ids=list(item["evidence_ids"]))
        item.update(status="accepted", decided_by=by, decided_at=decided_at, decision_note=note)
    write_json(run_paths(slug).proposals, payload)
    out["proposal"] = item
    return out


def _pairs(d: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    return [{"key": k, "value": v} for k, v in (d or {}).items()]


def _summary_proposals(slug: str, registry: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """승인 페이지의 제안 절. 기업·판정 재료 이름을 키로 쓰지 않는다(요약 계약은 키 구조를 비교한다)."""
    payload = _load_proposals(slug)
    if not payload["items"]:
        return []
    judgments = {(j["company_id"], j["factor"]): j for j in load_json_strict(run_dir(slug) / "judgments.json")["items"]}
    out = []
    for p in payload["items"]:
        j = judgments.get((p["company_id"], p["factor"]))
        before = p["before"]
        out.append({
            "proposal_id": p["proposal_id"],
            "company_id": p["company_id"],
            "display_name": (registry.get(p["company_id"]) or {}).get("display_name") or p["company_id"],
            "factor": p["factor"],
            "edit_kind": JUDGMENT_EDIT_KIND[p["factor"]],
            "changes": _pairs(p["changes"]),
            "evidence_after": p["evidence_after"],
            "reason": p["reason"],
            "evidence_ids": list(p["evidence_ids"]),
            "before": {"kind": before["kind"], "score": before["score"], "inputs": _pairs(before["inputs"]),
                       "evidence": list(before["evidence"])},
            # 결정 전 제안인데 그사이 판단이 바뀌었으면 반영할 수 없다
            "stale": p["status"] == "pending" and (j is None or _judgment_snapshot(j) != before),
            "proposed_by": p["proposed_by"],
            "proposed_at": p["proposed_at"],
            "status": p["status"],
            "decided_by": p.get("decided_by"),
            "decided_at": p.get("decided_at"),
            "decision_note": p.get("decision_note"),
        })
    return out


# ------------------------------------------------------------------ summary
# 2026-09-30 레인 F. 승인 페이지(server/approvals.js)가 읽는다. 키 구조는 tests/node/fixtures/summary.sample.json 그대로다.

def _pending_text(p: dict[str, Any]) -> str:
    return f"{p['factor']}: {p['status']}" + (f" ({p['decision_id']})" if p.get("decision_id") else "")


def _summary_companies(results: dict[str, Any] | None, baseline: dict[str, Any]) -> list[dict[str, Any]]:
    base = {b["company_id"]: b for b in baseline.get("companies", [])}
    out = []
    for c in (results or {}).get("companies", []):
        b = base.get(c["company_id"])
        changed = []
        for f in FACTOR_IDS:
            old = (b or {}).get("scores", {}).get(f)
            new = c["factors"][f]["score"]
            if b and old is not None and new is not None and old != new:
                changed.append({"factor": f, "from": old, "to": new})
        out.append({
            "company_id": c["company_id"],
            "display_name": c["display_name"],
            "baseline": {"total": (b or {}).get("total"), "rank": (b or {}).get("rank_raw")},
            "current": {"total": c["total"], "rank": c["rank"]},
            "changed_factors": changed,
            "carried_factors": list(c["carried_factors"]),
            "pending": [_pending_text(p) for p in c["pending"]],
        })
    return out


def _part_field(part: Path, label: str) -> str | None:
    if not part.is_file():
        return None
    m = re.search(rf"^{label}:\s*(.+?)\s*$", part.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def _summary_review(paths: Any) -> dict[str, Any] | None:
    """`review.md` 의 frontmatter·검토 영역 표·체크리스트. 영역 칸이 비었거나 pending 이면 `review-parts/<영역>.md` 를 읽는다."""
    if not paths.review.is_file():
        return None
    from .validate import _section, _table_rows

    fm, body, _raw, _text = read_markdown(paths.review)
    rows = {cells[0]: cells for cells in _table_rows(_section(body, "검토 영역")) if len(cells) >= 4}
    areas = []
    for key, label, _scope in REVIEW_AREAS:
        cells = rows.get(label)
        reviewer = cells[2] if cells and cells[2] else None
        result = cells[3] if cells and cells[3] and cells[3] != "pending" else None
        part = paths.review_parts / f"{key}.md"
        areas.append({"area": key,
                      "reviewer": reviewer or _part_field(part, "검토자"),
                      "result": result or _part_field(part, "결과") or (cells[3] if cells else None)})
    fails = sum(1 for cells in _table_rows(_section(body, "체크리스트")) if len(cells) >= 3 and cells[2] == "fail")
    return {"status": fm.get("status"), "areas": areas, "checklist_fail": fails}


def _summary_judgments(slug: str, rules: Any) -> list[dict[str, Any]]:
    """2026-10-01 레인 J. 기업×factor 판단 입력. inputs 는 키 구조가 판정 종류마다 달라 `{key, value}` 목록으로 낸다."""
    path = run_dir(slug) / "judgments.json"
    if not path.is_file():
        return []
    registry = load_companies()
    out = []
    for j in load_json_strict(path).get("items", []):
        out.append({
            "company_id": j["company_id"],
            "display_name": (registry.get(j["company_id"]) or {}).get("display_name") or j["company_id"],
            "factor": j["factor"],
            "kind": j["kind"],
            "score": j["score"],
            "score_range": list(rules.payload["factors"][j["factor"]]["range"]),
            "inputs": [{"key": k, "value": v} for k, v in j["inputs"].items()],
            "evidence": list(j["evidence"]),
            "status": j["status"],
            "reviewer": j["reviewer"],
            "reviewed_at": j["reviewed_at"],
            "edit_kind": JUDGMENT_EDIT_KIND.get(j["factor"]),
            "revisions": len(j.get("revision_history") or []),
            # 2026-10-01 V2-11: 마지막 수정이 에이전트 세션이었는지. 이력이 없거나 기록 전 수정이면 null.
            "last_revision_session": ((j.get("revision_history") or [{}])[-1]).get("session"),
        })
    return sorted(out, key=lambda x: (x["factor"], x["company_id"]))


def summary(slug: str) -> dict[str, Any]:
    """승인 페이지가 한 화면에 싣는 요약. 값은 status·render_md 가 이미 쓰는 데이터를 다시 읽는다. 없는 파일은 0·빈 목록·null 이다."""
    paths = run_paths(slug)
    run = validate_run(load_json_strict(paths.run_dir / "run.json"), slug)
    results = load_results(slug) if results_path(slug).is_file() else None
    baseline, _obs, _legacy = load_baseline(run["baseline_id"])
    src_path = paths.run_dir / "sources.json"
    urls = {s["source_id"]: s.get("url") for s in (load_json_strict(src_path).get("items", []) if src_path.is_file() else [])}
    candidates = load_json_strict(paths.candidates).get("items", []) if paths.candidates.is_file() else []
    evidence = load_json_strict(paths.evidence).get("items", []) if paths.evidence.is_file() else []
    triggers = load_json_strict(paths.triggers).get("items", []) if paths.triggers.is_file() else []
    registry = load_companies()
    hashes = current_hashes(slug)
    if approval_file_present(paths.run_dir):
        approval = load_json_strict(paths.run_dir / "approval.json")
        approval_out = {"exists": True, "valid": approval_is_valid(slug, approval, hashes),
                        "approved_by": approval.get("approved_by"), "approved_at": approval.get("approved_at")}
    else:
        approval_out = {"exists": False, "valid": False, "approved_by": None, "approved_at": None}
    return {
        "run_id": slug,
        "as_of": run["as_of"],
        "rule_version": run["rule_version"],
        "companies": _summary_companies(results, baseline),
        "review": _summary_review(paths),
        "evidence": {
            "candidates": len(candidates),
            "selected": len(evidence),
            "confirmed": sum(1 for e in evidence if e.get("status") == "confirmed"),
            "items": [{"evidence_id": e["evidence_id"], "company_id": e["company_id"], "factors": list(e["factors"]),
                       "kind": e["kind"], "title": e["title"], "url": urls.get(e["source_id"]),
                       "published_at_utc": e["published_at_utc"], "excerpt": e["excerpt"],
                       "status": e.get("status", "candidate"),
                       # 2026-10-01 사용자 요청(가독성): 사람이 확정 여부를 가를 판단 재료를 함께 싣는다
                       "relevance": e["relevance"], "channel": e["channel"], "conditional_impact": e["conditional_impact"],
                       "horizon": e["horizon"], "counter_evidence": list(e["counter_evidence"]),
                       "unverified": list(e["unverified"])} for e in evidence],
        },
        "triggers": [{"trigger_id": t["trigger_id"], "company_id": t["company_id"], "factors": list(t["factors"]),
                      "observation": t["observation"], "condition": t["condition"], "deadline": t["deadline"],
                      "status": t["status"], "recheck_what": t["recheck"]["what"]} for t in triggers],
        # 2026-10-01 사용자 요청(가독성): 화면이 company_id 대신 표시명을 쓴다
        "company_names": [{"company_id": cid, "display_name": (registry.get(cid) or {}).get("display_name") or cid}
                          for cid in run["companies"]],
        "pending_rule_decisions": list((results or {}).get("pending_rule_decisions", [])),
        "judgments": _summary_judgments(slug, load_rules(run["rule_version"])),
        "proposals": _summary_proposals(slug, registry),
        "judgment_choices": copy.deepcopy(JUDGMENT_INPUT_CHOICES),
        "hashes": hashes,
        "approval": approval_out,
    }


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
    out["approval"] = approval_file_present(d)
    if out["approval"] and out["results"] and out["draft"]:
        approval = load_json_strict(d / "approval.json")
        out["approval_valid"] = approval_is_valid(slug, approval)
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
