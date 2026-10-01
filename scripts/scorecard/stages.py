# scorecard 단계 실행: init(실행 생성) → collect → research → calculate(+preview) → draft → review-template → confirm·approve·revoke·summary. 순서·해시 결속·실행 잠금을 코드에서 강제한다.
from __future__ import annotations

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
from .schema import (APPROVAL_REQUIRED_HASHES, APPROVAL_VIA, FACTOR_IDS, SchemaError, load_json_strict, sha256_file, sha256_obj,
                     sha256_text, validate_approval, validate_observations, validate_run, validate_sources, write_json)


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
    # 2026-10-01 레인 H(F-1): 덮어쓰면 아래에서 approval.json 이 지워진다. 승인 파괴는 사람만 한다.
    if force and (d / "approval.json").is_file():
        markers = agent_session_markers()
        if markers:
            raise SchemaError(f"에이전트 세션({', '.join(markers)})에서는 승인된 실행 {rel(d)} 를 --force 로 덮어쓸 수 없다. "
                              "덮어쓰면 승인 기록이 지워진다 — 새 slug 로 init 하거나 사람이 한다")
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
    """가격·시총 관측을 observations.json 에 더하고 SRC-YF-<price_as_of> 를 sources.json 에 등록한다. 덮어쓰지 않는다."""
    price_as_of = run.get("price_as_of") or run["as_of"]
    source_id = f"SRC-YF-{price_as_of}"
    quotes = json.loads(Path(from_file).read_text(encoding="utf-8")) if from_file else None
    rows: list[dict[str, Any]] = []
    new_obs: list[dict[str, Any]] = []
    tickers: list[str] = []
    for cid in selected:
        company = registry[cid]
        ticker = company.get("ticker")
        if not company.get("listed") or not ticker:
            rows.append({"company_id": cid, "status": "skipped_unlisted"})
            continue
        if dry_run:
            rows.append({"company_id": cid, "status": "dry_run", "ticker": ticker, "price_as_of": price_as_of})
            continue
        try:
            if quotes is not None and ticker not in quotes:
                raise ValueError(f"{from_file} 에 {ticker} 시세가 없다")
            quote = quotes[ticker] if quotes is not None else fetch_quote(ticker, price_as_of)
            obs = price_observations(company, quote, source_id=source_id)
        except Exception as exc:  # noqa: BLE001 — 기업 하나의 실패로 나머지를 멈추지 않는다
            rows.append({"company_id": cid, "status": "failed", "error": str(exc)})
            continue
        new_obs += obs
        tickers.append(ticker)
        rows.append({"company_id": cid, "status": "collected", "close_date": obs[0]["as_of"],
                     "market_cap": obs[1]["status"], "method": obs[1]["basis"]["method"]})
    if dry_run or not new_obs:
        return rows

    d = run_dir(slug)
    observations = load_json_strict(d / "observations.json")
    taken = {(o["company_id"], o["metric"], o["as_of"]) for o in observations["items"]}
    taken_ids = {o["observation_id"] for o in observations["items"]}
    clash = [o["observation_id"] for o in new_obs
             if (o["company_id"], o["metric"], o["as_of"]) in taken or o["observation_id"] in taken_ids]
    if clash:
        raise SchemaError(f"같은 (기업, 지표, 기준일) 관측이 이미 있다 — 덮어쓰지 않는다: {clash}")
    observations["items"].extend(new_obs)
    validate_observations(observations, registry, slug)
    src_path = d / "sources.json"
    sources = load_json_strict(src_path) if src_path.is_file() else {"schema": "scorecard.sources/1", "run_id": slug, "items": []}
    upsert_sources(sources, [price_source_entry(price_as_of, tickers=tickers, accessed_at=now or utc_now_iso())])
    validate_sources(sources, slug)
    write_json(d / "observations.json", observations)
    write_json(src_path, sources)
    return rows


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

    summary: dict[str, Any] = {"run_id": slug, "window": {"since": since, "until": until}, "dry_run": dry_run,
                               "news": [], "filings": [], "prices": []}
    for cid in selected if "news" in kinds else []:
        try:
            res = collect_company_news(registry[cid], from_file=from_file, dry_run=dry_run, now=now, locale=locale)
            status = "dry_run" if dry_run else ("skipped_rate_limit" if res["skipped_rate_limit"] and not res["fetched"] else "collected")
            summary["news"].append({"company_id": cid, "status": status, "urls": res["urls"]})
        except Exception as exc:  # noqa: BLE001
            summary["news"].append({"company_id": cid, "status": "failed", "error": str(exc)})
    sec_ua = evidence_lib.sec_user_agent()
    for cid in selected if "filings" in kinds else []:
        company = registry[cid]
        if not company.get("cik"):
            summary["filings"].append({"company_id": cid, "status": "skipped_no_cik"})
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


# ------------------------------------------------------------------ 세션 판정·실행 잠금
# 2026-09-30 레인 F. 에이전트 터미널에만 있고 사람이 여는 일반 Orca 셸에는 없는 것을 두 셸의 환경변수를
# 직접 비교해 골랐다(validation/lane-F-approval/REPORT.md 의 표). `ORCA_*` 는 사람 셸에도 있어서 넣지 않는다.
AGENT_ENV_MARKERS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "ORCA_AGENT_LAUNCH_TOKEN", "AI_AGENT")
# 잠금을 검사하고 쓰는 단계. approve·revoke·build 는 사람 행위라 잠금을 요구하지도 쓰지도 않는다.
LOCK_STAGES = ("init", "collect", "research", "calculate", "draft", "review-template", "confirm")


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
    approval_id = sha256_text(f"{slug}:{hashes['results']}:{hashes['draft']}")[:16]
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
    if not path.is_file():
        raise SchemaError(f"취소할 승인이 없다: {rel(path)}")
    approval = validate_approval(load_json_strict(path), slug)
    entry = {"revoked_by": by.strip(), "revoked_at": utc_now_iso(), "note": note.strip(),
             "approval_id": approval["approval_id"], "hashes": approval["hashes"]}
    log = run_dir(slug) / "revocations.jsonl"
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    path.unlink()
    return log


# ------------------------------------------------------------------ confirm
# 2026-09-30 레인 F. 근거 확정은 승인이 아니다. 확정하면 evidence 해시가 바뀌어 calculate 부터 다시 밟고 사람이 다시 승인한다.
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
    except SchemaError:
        path.write_bytes(original)
        raise
    return {"confirmed": confirmed, "already_confirmed": already, "rejected": rejects, "reviewer": reviewer,
            "reviewed_at": reviewed_at, "evidence_hash": sha256_file(path)}


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
    hashes = current_hashes(slug)
    approval_path = paths.run_dir / "approval.json"
    if approval_path.is_file():
        approval = load_json_strict(approval_path)
        approval_out = {"exists": True, "valid": not approval_mismatches(approval.get("hashes") or {}, hashes),
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
                       "status": e.get("status", "candidate")} for e in evidence],
        },
        "triggers": [{"trigger_id": t["trigger_id"], "company_id": t["company_id"], "factors": list(t["factors"]),
                      "condition": t["condition"], "deadline": t["deadline"], "status": t["status"]} for t in triggers],
        "pending_rule_decisions": list((results or {}).get("pending_rule_decisions", [])),
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
    out["approval"] = (d / "approval.json").is_file()
    if out["approval"] and out["results"] and out["draft"]:
        approval = load_json_strict(d / "approval.json")
        out["approval_valid"] = not approval_mismatches(approval.get("hashes") or {}, current_hashes(slug))
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
