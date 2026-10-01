# 이전 트리거마다 확인할 수집 후보(candidates.json)를 자동으로 붙여 주는 확인 보조
"""발동 여부를 판정하지 않는다. 이전 트리거 문구와 같은 기업 후보 제목의 겹친 토큰만 보여준다.

입력 파일은 읽기만 하며 아무것도 쓰지 않는다(입력 해시 불변). 네트워크 호출은 없다.
"""
from __future__ import annotations

import re
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9]+")

# 불용어는 최소한으로 둔다. 기능어만 뺀다.
STOPWORDS = frozenset({
    "the", "and", "for", "with", "from", "that", "this", "these", "those",
    "are", "was", "were", "has", "have", "had", "will", "would", "should",
    "could", "can", "its", "our", "their", "your", "you", "all", "any",
    "but", "not", "out", "about", "into", "over", "after", "before",
    "between", "more", "most", "such", "than", "then", "also",
})

DEFAULT_LIMIT = 5
SCHEMA = "scorecard.trigger_candidates/1"


def tokenize(text: str | None) -> set[str]:
    """영문·숫자 토큰(소문자). 3자 이상 또는 숫자 포함(Q1·FY27·10-Q의 10)만 남긴다."""
    out: set[str] = set()
    for tok in TOKEN_RE.findall((text or "").lower()):
        if (len(tok) >= 3 or any(ch.isdigit() for ch in tok)) and tok not in STOPWORDS:
            out.add(tok)
    return out


def name_tokens(text: str | None) -> set[str]:
    """기업 이름 대조용 토큰. 길이 제한 없이 소문자 영숫자 묶음만 본다(MS 같은 짧은 별칭도 살린다)."""
    return set(TOKEN_RE.findall((text or "").lower()))


def company_name_keys(company: dict[str, Any]) -> set[str]:
    """레지스트리 속성에서 기업을 가리키는 말(company_id·표시명·티커·별칭)을 토큰으로 푼다."""
    keys: set[str] = set()
    raws: list[Any] = [company.get("company_id"), company.get("display_name"), company.get("ticker")]
    raws.extend(company.get("aliases") or [])
    for raw in raws:
        if raw:
            keys |= name_tokens(str(raw))
    return keys


def trigger_text(trigger: dict[str, Any], extra: str = "") -> str:
    """트리거 문구. 이전 항목의 제목과 이번 실행 watching 항목의 관찰·조건을 합친다."""
    return " ".join(x for x in [trigger.get("title"), trigger.get("observation"),
                                trigger.get("condition"), extra] if x)


def estimate_companies(title: str | None, companies: dict[str, dict[str, Any]]) -> list[str]:
    """제목 토큰에 레지스트리 이름 키가 겹치는 기업. 레지스트리 순서라 결정적이다."""
    words = name_tokens(title)
    return [cid for cid, item in companies.items() if company_name_keys(item) & words]


def resolve_trigger_companies(trigger: dict[str, Any],
                              companies: dict[str, dict[str, Any]]) -> tuple[list[str], str]:
    """트리거 대상 기업과 출처(company_id|estimated|all). 셋 다 ([기업], 출처)다."""
    cid = trigger.get("company_id")
    if cid and cid in companies:
        return ([cid], "company_id")
    hits = estimate_companies(trigger.get("title"), companies)
    if hits:
        return (hits, "estimated")
    return (sorted(companies), "all")


def candidate_day(candidate: dict[str, Any]) -> str:
    """게시일(공시는 제출일)의 YYYY-MM-DD. 없으면 빈 문자열."""
    return str(candidate.get("published_at_utc") or candidate.get("filed_at") or "")[:10]


def candidate_sort_key_value(candidate: dict[str, Any]) -> str:
    """게시일 내림차순용 값. 원문 문자열 그대로라 형식 섞여도 결정적이다."""
    return str(candidate.get("published_at_utc") or candidate.get("filed_at") or "")


def match_trigger(trigger: dict[str, Any], candidates: list[dict[str, Any]],
                  company_ids: list[str], trigger_tokens: set[str],
                  deadline: str | None, limit: int) -> list[dict[str, Any]]:
    """같은 기업 후보 중 트리거 토큰과 겹치는 것만 점수 내림차순→게시일 내림차순→ID 오름차순으로 상위 limit건."""
    wanted = set(company_ids)
    rows: list[dict[str, Any]] = []
    for cand in candidates:
        if cand.get("company_id") not in wanted:
            continue
        overlap = sorted(trigger_tokens & tokenize(cand.get("title")))
        if not overlap:
            continue
        day = candidate_day(cand)
        rows.append({
            "candidate_id": cand.get("candidate_id"),
            "company_id": cand.get("company_id"),
            "kind": cand.get("kind"),
            "title": cand.get("title"),
            "url": cand.get("url"),
            "published_at_utc": cand.get("published_at_utc"),
            "filed_at": cand.get("filed_at"),
            "date": day,
            "score": len(overlap),
            "overlap_tokens": overlap,
            "after_deadline": bool(deadline and day and day > deadline),
        })
    rows.sort(key=lambda r: str(r["candidate_id"]))
    rows.sort(key=lambda r: candidate_sort_key_value(
        {"published_at_utc": r["published_at_utc"], "filed_at": r["filed_at"]}), reverse=True)
    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows[:limit]


def collect_trigger_candidates(previous: list[dict[str, Any]], candidates: list[dict[str, Any]],
                               companies: dict[str, dict[str, Any]],
                               current_watching: list[dict[str, Any]] | tuple = (),
                               limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
    """이전 트리거마다 볼 후보를 붙인다. 이번 실행 watching 항목은 carry.ref 로 이어진 것만 텍스트·기한에 보탠다."""
    by_ref: dict[str, list[dict[str, Any]]] = {}
    for item in current_watching:
        carry = item.get("carry") or {}
        if carry.get("ref"):
            by_ref.setdefault(carry["ref"], []).append(item)
    out: list[dict[str, Any]] = []
    for prev in previous:
        carriers = sorted(by_ref.get(prev.get("ref", ""), []), key=lambda t: t.get("trigger_id", ""))
        extra = " ".join(x for t in carriers for x in [t.get("observation"), t.get("condition")] if x)
        deadline = prev.get("deadline") or next(
            (t.get("deadline") for t in carriers if t.get("deadline")), None)
        company_ids, source = resolve_trigger_companies(prev, companies)
        tokens = tokenize(trigger_text(prev, extra))
        out.append({
            "ref": prev.get("ref"),
            "title": prev.get("title"),
            "company_ids": company_ids,
            "company_source": source,
            "company_guess_failed": source == "all",
            "deadline": deadline,
            "carried_by": [t.get("trigger_id") for t in carriers],
            "candidates": match_trigger(prev, candidates, company_ids, tokens, deadline, limit),
        })
    return out


def trigger_candidates_for_run(slug: str, *, limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """실행 하나를 읽어 이전 트리거별 후보 묶음을 낸다. 파일 쓰기·네트워크 없이 읽기만 한다."""
    from . import engine
    from .paths import run_paths
    from .schema import load_json_strict
    from .stages import previous_triggers

    run = load_json_strict(engine.run_dir(slug) / "run.json")
    companies = engine.load_companies()
    paths = run_paths(slug)
    items: list[dict[str, Any]] = []
    if paths.candidates.is_file():
        items = load_json_strict(paths.candidates).get("items", [])
    watching: list[dict[str, Any]] = []
    if paths.triggers.is_file():
        watching = [t for t in load_json_strict(paths.triggers).get("items", [])
                    if t.get("status") == "watching"]
    return {"schema": SCHEMA, "run_id": slug, "limit": limit,
            "items": collect_trigger_candidates(previous_triggers(run), items, companies,
                                                current_watching=watching, limit=limit)}


def render_text(data: dict[str, Any], companies: dict[str, dict[str, Any]]) -> str:
    """사람용 출력. 트리거별 ref·제목·추정 기업·후보(제목, 게시일, URL, 겹친 토큰)."""
    lines = [f"trigger-candidates: {data['run_id']} (트리거 {len(data['items'])}건, 건당 상위 {data['limit']}건)"]
    for entry in data["items"]:
        names = ", ".join(companies[c]["display_name"] if c in companies else c
                          for c in entry["company_ids"])
        if entry["company_guess_failed"]:
            names += " — 기업 추정 실패(전 기업 대상)"
        elif entry["company_source"] == "estimated":
            names += " (제목에서 추정)"
        lines.append(f"{entry['ref']} | {entry['title']}")
        lines.append(f"  기업: {names} · 기한: {entry['deadline'] or '—'}"
                     + (f" · 이어받음: {', '.join(entry['carried_by'])}" if entry["carried_by"] else ""))
        if not entry["candidates"]:
            lines.append("  볼 후보 없음(겹친 토큰 없음)")
            continue
        for cand in entry["candidates"]:
            lines.append(f"  - [점수 {cand['score']}] {cand['date'] or '날짜 없음'} {cand['title']}")
            lines.append(f"    {cand['url'] or 'URL 없음'} · 겹침: {', '.join(cand['overlap_tokens'])}"
                         + (" · 기한 이후 소식" if cand["after_deadline"] else ""))
    return "\n".join(lines) + "\n"
