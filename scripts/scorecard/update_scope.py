# 실적 반영 실행의 갱신 범위와 막는 검사(규칙 v3.1, rules.md 2.9) — research 단계와 계약 검증이 같은 함수를 부른다
"""2026-10-22 사용자 결정 D1~D5. 실적이 나온 회사만 다시 매기되, 범위는 에이전트 재량이 아니라 기록이 정한다.

- 갱신 회사(run.continued_from.updated_companies)의 정성 판단은 전부 범위다.
- 이번 실행에서 새로 확정한 근거와 새로 발동한 트리거가 가리키는 (회사, 항목)은 범위다. "새로"는 이전 실행의 같은 ID 와
  견주어 가른다. 확정일 칸은 `confirm --reviewed-at` 으로 옛 날짜를 줄 수 있어 기준으로 쓰지 않는다.
- run.update_scope.extra 에 이유와 함께 선언한 (회사, 항목)은 범위다(리뷰가 같은 층 경쟁사에 새 잣대를 댈 때).

막는 검사는 둘이다. 가격 기준일까지 실적 공시를 낸 회사가 갱신 회사가 아니면 막고(D2), 마지막 전체 갱신일에서
나이 상한이 지난 회사가 갱신 회사가 아니면 막는다(D4). 실적 감지는 실행 폴더의 candidates.json 만 읽는다 —
gitignore 된 수집 캐시를 읽으면 다른 기계에서 계약 검증의 답이 달라진다(D7).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .engine import run_dir
from .paths import run_paths
from .schema import SchemaError, load_json_strict

# 옛 후보에는 items 칸이 없고 제목에만 "8-K 2026-10-21 · Items 2.02, 9.01" 로 남았다.
_TITLE_ITEMS_RE = re.compile(r"Items ([0-9., ]+)$")


@dataclass
class Scope:
    updated: list[str]
    touched: dict[tuple[str, str], list[str]] = field(default_factory=dict)
    extra: dict[tuple[str, str], str] = field(default_factory=dict)

    def why(self, company_id: str, factor: str) -> str | None:
        """이 (회사, 항목)이 범위인 이유. 범위 밖이면 None."""
        key = (company_id, factor)
        if company_id in self.updated:
            return "갱신 회사"
        if key in self.extra:
            return f"선언한 추가 항목 — {self.extra[key]}"
        if key in self.touched:
            refs = self.touched[key]
            return "새 근거·트리거가 닿음 — " + ", ".join(refs[:3]) + (f" 외 {len(refs) - 3}건" if len(refs) > 3 else "")
        return None


def _policy(ctx: Any) -> dict[str, Any]:
    from .validate import update_runs_policy
    policy = update_runs_policy(ctx.rules.payload)
    if policy is None:
        raise SchemaError(f"규칙 {ctx.rules.version} 에는 실적 반영 실행 정책(policies.rejudge.update_runs)이 없다")
    return policy


def _qualitative(ctx: Any) -> set[str]:
    return set((ctx.rules.payload["policies"].get("rejudge") or {}).get("qualitative_factors") or [])


def _prior_items(ctx: Any, name: str, key: str) -> dict[str, dict[str, Any]]:
    """이전 실행의 근거·트리거를 ID 로. 이전 실행 폴더가 없으면 무엇이 새것인지 가를 수 없으므로 멈춘다."""
    prior = (ctx.run.get("continued_from") or {}).get("run_id")
    if not prior or not run_dir(prior).is_dir():
        raise SchemaError(f"이전 실행 {prior} 의 폴더가 없어 이번 실행에서 새로 확정·발동한 것을 가를 수 없다")
    path = getattr(run_paths(prior), name)
    return {x[key]: x for x in load_json_strict(path).get("items", [])} if path.is_file() else {}


def new_confirmed_evidence(ctx: Any) -> list[dict[str, Any]]:
    """이번 실행에서 확정한 근거. 이전 실행에 없었거나 후보였던 것."""
    prior = _prior_items(ctx, "evidence", "evidence_id")
    return [e for e in ctx.evidence or [] if e.get("status") == "confirmed"
            and (prior.get(e["evidence_id"]) or {}).get("status") != "confirmed"]


def newly_fired_triggers(ctx: Any) -> list[dict[str, Any]]:
    """이번 실행에서 발동으로 판정한 트리거. 이전 실행에 없었거나 발동이 아니었던 것."""
    prior = _prior_items(ctx, "triggers", "trigger_id")
    return [t for t in ctx.triggers or [] if t["status"] == "fired"
            and (prior.get(t["trigger_id"]) or {}).get("status") != "fired"]


def compute(ctx: Any) -> Scope:
    """실적 반영 실행의 갱신 범위."""
    qual = _qualitative(ctx)
    sc = Scope(updated=list((ctx.run.get("continued_from") or {}).get("updated_companies") or []))
    for e in new_confirmed_evidence(ctx):
        for f in e.get("factors") or []:
            if f in qual:
                sc.touched.setdefault((e["company_id"], f), []).append(e["evidence_id"])
    for t in newly_fired_triggers(ctx):
        for f in (t.get("recheck") or {}).get("factors") or t.get("factors") or []:
            if f in qual:
                sc.touched.setdefault((t["company_id"], f), []).append(t["trigger_id"])
    for item in (ctx.run.get("update_scope") or {}).get("extra") or []:
        sc.extra[(item["company_id"], item["factor"])] = item["reason"]
    return sc


def _items_of(candidate: dict[str, Any]) -> list[str]:
    if "items" in candidate:
        return list(candidate.get("items") or [])
    m = _TITLE_ITEMS_RE.search(candidate.get("title") or "")
    return [x.strip() for x in m.group(1).split(",") if x.strip()] if m else []


def _base_form(form: str | None) -> str:
    return (form or "").split("/")[0]


def earnings_findings(ctx: Any) -> tuple[list[str], list[dict[str, Any]]]:
    """(막는 사유, 기계로 못 가르는 공시 목록). 갱신 회사가 아닌데 마지막 전체 갱신일 뒤·가격 기준일까지 실적 공시를 낸 회사를 잡는다.
    공시 목록이 가격 기준일 뒤에 받은 것이 아니면 감지가 눈을 감은 것이므로 그것도 막는다."""
    policy = _policy(ctx)
    updated = set((ctx.run.get("continued_from") or {}).get("updated_companies") or [])
    refreshed = ctx.run.get("refreshed_at") or {}
    price_day = ctx.run.get("price_as_of") or ctx.run["as_of"]
    path = run_paths(ctx.slug).candidates
    if not path.is_file():
        return [f"공시 후보 파일이 없다 — 실적 감지를 하려면 `collect {ctx.slug} --kind filings` 를 회사를 고르지 않고 돌린다"], []
    payload = load_json_strict(path)
    fetched = payload.get("filings_fetched_at") or {}
    out: list[str] = []
    for cid in ctx.run["companies"]:
        if cid in updated or not (ctx.companies.get(cid) or {}).get("cik"):
            continue
        got = fetched.get(cid)
        if not got or got[:10] < price_day:
            out.append(f"{cid}: 공시 목록을 가격 기준일 {price_day} 이후에 받지 않았다({got or '수집 기록 없음'}) — "
                       f"`collect {ctx.slug} --kind filings` 를 회사를 고르지 않고 돌린다")
    earnings = set(policy["earnings_forms"])
    items_8k = set(policy["earnings_8k_items"])
    manual_forms = set(policy["manual_check_forms"])
    manual: list[dict[str, Any]] = []
    for c in payload.get("items") or []:
        cid = c.get("company_id")
        if c.get("kind") != "filing" or cid in updated or cid not in refreshed:
            continue
        day = c.get("filed_at") or ""
        if not (refreshed[cid] < day <= price_day):
            continue
        form, items = _base_form(c.get("form")), _items_of(c)
        if form in earnings or (form == "8-K" and items_8k & set(items)):
            shown = f" Item {', '.join(items)}" if items else ""
            out.append(f"{cid}: {c.get('form')} {day}{shown} — 마지막 전체 갱신 {refreshed[cid]} 뒤·가격 기준일 {price_day} 까지 "
                       "실적을 냈으므로 갱신 회사여야 한다(rules.md 2.9)")
        elif form in manual_forms:
            manual.append({"company_id": cid, "form": c.get("form"), "filed_at": day, "title": c.get("title"), "url": c.get("url")})
    return out, sorted(manual, key=lambda m: (m["company_id"], m["filed_at"]))


def age_findings(ctx: Any) -> list[str]:
    """마지막 전체 갱신일에서 나이 상한이 지났는데 갱신 회사가 아닌 회사."""
    limit = _policy(ctx)["max_age_days"]
    updated = set((ctx.run.get("continued_from") or {}).get("updated_companies") or [])
    refreshed = ctx.run.get("refreshed_at")
    if not refreshed:
        return ["run.json 에 refreshed_at 이 없다 — 규칙 v3.1 이상으로 init 한 실행이어야 판단 나이를 잴 수 있다"]
    as_of = date.fromisoformat(ctx.run["as_of"])
    out = []
    for cid, day in sorted(refreshed.items()):
        age = (as_of - date.fromisoformat(day)).days
        if cid not in updated and age > limit:
            out.append(f"{cid}: 마지막 전체 갱신 {day} 로부터 {age}일 — {limit}일을 넘었으므로 갱신 회사여야 한다(rules.md 2.9)")
    return out


def blocking_findings(ctx: Any) -> list[str]:
    """research 와 계약 검증을 막는 사유(실적 감지 + 판단 나이)."""
    earnings, _manual = earnings_findings(ctx)
    return earnings + age_findings(ctx)
