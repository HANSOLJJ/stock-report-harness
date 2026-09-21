# 두 실행을 견주어 **기존 기업이 안 움직였음**을 기계로 증명한다(점수 투영 해시 기준)
"""2026-09-21 ADD-02. 기업을 더한 새 실행이 기존 기업을 건드리지 않았는지 사람이 눈으로 볼 수 없다.

**불변 판정은 점수 투영(projection) 해시로 한다.** 기업별 subtree 해시를 쓰면 안 된다 —
`run.as_of` 만 옮겨도 `factors.F6.calc.p4.stale_asof.as_of` 에 날짜가 박혀(`calc_f6_params._stale_asof`)
상장사들의 subtree 해시가 전부 달라지는데 **점수는 하나도 바뀌지 않는다.** subtree 차이는 참고로만 낸다.

비교 로직을 새로 쓰지 않는다 — `engine.load_results`(results_hash 자가검증) · `schema.sha256_obj` ·
`stages.current_hashes` · `schema.validate_approval` · `aggregate.COMPLETE_STATUSES` 를 그대로 쓴다.
"""
from __future__ import annotations

from typing import Any

from .engine import load_context, load_results, run_dir
from .schema import FACTOR_IDS, SchemaError, load_json_strict, sha256_obj, validate_approval
from .stages import current_hashes

# 1층에서 견주는 입력 장부. `sources` 항목에는 `company_id` 가 없다 — 귀속을 따질 수 없으므로
# **지워진 것만** 위반으로 보고 더해진 것은 목록으로만 낸다.
INPUT_FILES = {"observations": "observations.json", "judgments": "judgments.json", "sources": "sources.json"}
SUBTREE_NOTE = ("subtree 해시 차이는 실패 조건이 아니다 — `as_of` 만 바꿔도 달라진다"
                "(`factors.F6.calc.p4.stale_asof.as_of`). 불변은 점수 투영으로 판정한다.")


def score_projection(company: dict[str, Any]) -> dict[str, Any]:
    """점수에 닿는 것만 뽑는다. **`rank` 는 넣지 않는다** — 신규 기업이 끼면 기존 기업이 정당하게 밀린다."""
    return {
        "moat": company.get("moat"),
        "trap": company.get("trap"),
        "total": company.get("total"),
        "complete": company.get("complete"),
        "factors": {f: {"score": company["factors"][f]["score"], "status": company["factors"][f]["status"]}
                    for f in FACTOR_IDS},
    }


def projection_hash(company: dict[str, Any]) -> str:
    return sha256_obj(score_projection(company))


def _items(slug: str, name: str) -> list[dict[str, Any]]:
    path = run_dir(slug) / INPUT_FILES[name]
    if not path.is_file():
        return []
    payload = load_json_strict(path)
    items = payload.get("items") if isinstance(payload, dict) else payload
    return list(items or [])


def _item_id(name: str, item: dict[str, Any]) -> str:
    for key in ("observation_id", "judgment_id", "source_id"):
        if key in item:
            return str(item[key])
    return f"{name}[?]"


def compare_inputs(slug: str, prior_slug: str, new_companies: set[str]) -> dict[str, Any]:
    """1층 — 입력 가법성. 기존 항목이 사라지거나 바뀌지 않았고, 더해진 것은 신규 기업 것이어야 한다."""
    out: dict[str, Any] = {"violations": [], "by_file": {}}
    for name in INPUT_FILES:
        prior = {sha256_obj(x): x for x in _items(prior_slug, name)}
        new = {sha256_obj(x): x for x in _items(slug, name)}
        gone = [prior[h] for h in prior.keys() - new.keys()]
        added = [new[h] for h in new.keys() - prior.keys()]
        # 같은 식별자가 양쪽에 있으면 지워진 것이 아니라 **내용이 고쳐진** 것이다. 둘은 사유가 다르다.
        new_ids = {_item_id(name, x) for x in new.values()}
        edited = [x for x in gone if _item_id(name, x) in new_ids]
        removed = [x for x in gone if _item_id(name, x) not in new_ids]
        added = [x for x in added if _item_id(name, x) not in {_item_id(name, y) for y in edited}]
        unattributed = [x for x in added if x.get("company_id") and x["company_id"] not in new_companies]
        no_company = [x for x in added if not x.get("company_id")]
        out["by_file"][name] = {
            "prior": len(prior), "new": len(new),
            "removed": [_item_id(name, x) for x in removed],
            "edited": [_item_id(name, x) for x in edited],
            "added": [_item_id(name, x) for x in added],
            "added_for_new_companies": [_item_id(name, x) for x in added
                                        if x.get("company_id") in new_companies],
            "added_for_existing_companies": [_item_id(name, x) for x in unattributed],
            "added_without_company": [_item_id(name, x) for x in no_company],
        }
        if removed:
            out["violations"].append(f"{name}: 기존 항목 {len(removed)}건이 사라졌다 "
                                     f"({', '.join(sorted(_item_id(name, x) for x in removed)[:5])}"
                                     f"{' 외' if len(removed) > 5 else ''})")
        if edited:
            out["violations"].append(f"{name}: 기존 항목 {len(edited)}건의 내용이 고쳐졌다 "
                                     f"({', '.join(sorted(_item_id(name, x) for x in edited)[:5])}"
                                     f"{' 외' if len(edited) > 5 else ''})")
        if unattributed:
            out["violations"].append(f"{name}: 신규 기업이 아닌 곳에 {len(unattributed)}건이 더해졌다 "
                                     f"({', '.join(sorted(_item_id(name, x) for x in unattributed)[:5])}"
                                     f"{' 외' if len(unattributed) > 5 else ''})")
    out["ok"] = not out["violations"]
    return out


def compare_scores(slug: str, prior_slug: str, new_companies: set[str]) -> dict[str, Any]:
    """2층 — 점수 불변. 기업별 투영 해시를 견준다."""
    new = {c["company_id"]: c for c in load_results(slug)["companies"]}
    prior = {c["company_id"]: c for c in load_results(prior_slug)["companies"]}
    shared = sorted(set(prior) & set(new))
    changed: list[dict[str, Any]] = []
    for cid in shared:
        before, after = score_projection(prior[cid]), score_projection(new[cid])
        if sha256_obj(before) == sha256_obj(after):
            continue
        diffs = [f"{k}: {before.get(k)} → {after.get(k)}" for k in ("moat", "trap", "total", "complete")
                 if before.get(k) != after.get(k)]
        diffs += [f"{f} {key}: {before['factors'][f][key]} → {after['factors'][f][key]}"
                  for f in FACTOR_IDS for key in ("score", "status")
                  if before["factors"][f][key] != after["factors"][f][key]]
        changed.append({"company_id": cid, "diffs": diffs})
    return {
        "ok": not changed,
        "compared": len(shared),
        "dropped": sorted(set(prior) - set(new)),
        "added": sorted(set(new) - set(prior)),
        "changed": changed,
        "violations": ([f"{c['company_id']}: {'; '.join(c['diffs'])}" for c in changed]
                       + ([f"이전 실행에 있던 기업이 빠졌다: {', '.join(sorted(set(prior) - set(new)))}"]
                          if set(prior) - set(new) else [])),
    }


def compare_ranking(slug: str, prior_slug: str, new_companies: set[str]) -> dict[str, Any]:
    """3층 — 순위 이동(정보). 신규 기업을 뺀 순서를 견준다. 달라져도 실패가 아니다."""
    def order(s: str) -> list[str]:
        return [r["company_id"] for r in load_results(s)["ranking"] if r["company_id"] not in new_companies]
    before, after = order(prior_slug), order(slug)
    return {"same_order": before == after, "prior": before, "new": after}


def _diff_paths(before: Any, after: Any, prefix: str = "") -> list[str]:
    """값이 갈린 leaf 경로를 모은다. 어디가 달라졌는지 말해 주지 않으면 참고 출력이 쓸모가 없다."""
    if isinstance(before, dict) and isinstance(after, dict):
        out: list[str] = []
        for key in sorted(set(before) | set(after)):
            if key in before and key in after:
                out += _diff_paths(before[key], after[key], f"{prefix}.{key}" if prefix else key)
            else:
                out.append(f"{prefix}.{key}" if prefix else key)
        return out
    return [] if before == after else [prefix]


def compare_subtrees(slug: str, prior_slug: str) -> dict[str, Any]:
    """참고 — 기업별 subtree 해시. **실패 조건이 아니다.**"""
    new = {c["company_id"]: c for c in load_results(slug)["companies"]}
    prior = {c["company_id"]: c for c in load_results(prior_slug)["companies"]}
    differing = []
    for cid in sorted(set(prior) & set(new)):
        if sha256_obj(prior[cid]) == sha256_obj(new[cid]):
            continue
        paths = _diff_paths(prior[cid], new[cid])
        only_as_of = bool(paths) and all(p.endswith("stale_asof.as_of") for p in paths)
        differing.append({
            "company_id": cid, "path_count": len(paths), "paths": paths[:8],
            "reason": "기준일(`as_of`) 이동뿐이다 — 점수와 무관하다" if only_as_of else "관측·판단 내용이 달라졌다",
        })
    return {
        "differing": [d["company_id"] for d in differing],
        "detail": differing,
        "as_of": {"prior": load_results(prior_slug).get("as_of"), "new": load_results(slug).get("as_of")},
        "note": SUBTREE_NOTE,
    }


def approval_state(slug: str) -> dict[str, Any]:
    """덤 — 그 실행의 승인이 아직 유효한가. 무엇이 달라서 무효인지까지 적는다."""
    path = run_dir(slug) / "approval.json"
    if not path.is_file():
        return {"exists": False, "valid": False, "differing": [], "note": "승인 기록 없음"}
    approval = validate_approval(load_json_strict(path), slug)
    current = current_hashes(slug)
    differing = sorted(k for k in set(approval["hashes"]) | set(current)
                       if approval["hashes"].get(k) != current.get(k))
    return {"exists": True, "valid": not differing, "differing": differing,
            "approved_by": approval.get("approved_by"), "approved_at": approval.get("approved_at"),
            "approved_results_hash": approval["hashes"].get("results"),
            "current_results_hash": current.get("results")}


def compare_runs(slug: str, prior_slug: str) -> dict[str, Any]:
    """세 층으로 견준다. 1층·2층 위반이 하나라도 있으면 `ok` 가 거짓이다."""
    if slug == prior_slug:
        raise SchemaError("같은 실행끼리는 견줄 수 없다")
    new_ids = set(load_context(slug).run["companies"])
    prior_ids = set(load_context(prior_slug).run["companies"])
    new_companies = new_ids - prior_ids
    inputs = compare_inputs(slug, prior_slug, new_companies)
    scores = compare_scores(slug, prior_slug, new_companies)
    # 신규 기업이 0곳이면 이 명령이 겨냥한 사례가 아니다. 그래도 검사는 그대로 돌린다 —
    # 같은 기업을 다시 조사한 실행이라면 1층·2층이 갈리는 것이 정상이고, 그 사실을 보이는 편이 낫다.
    note = ("신규 기업이 없다 — 이 비교는 **기업 추가** 사례가 아니라 같은 기업을 다시 조사한 사례로 보인다. "
            "아래 위반은 재조사에서는 당연히 나온다." if not new_companies else None)
    return {
        "slug": slug,
        "prior_slug": prior_slug,
        "new_companies": sorted(new_companies),
        "note": note,
        "inputs": inputs,
        "scores": scores,
        "ranking": compare_ranking(slug, prior_slug, new_companies),
        "subtrees": compare_subtrees(slug, prior_slug),
        "prior_approval": approval_state(prior_slug),
        "ok": inputs["ok"] and scores["ok"],
    }


# ------------------------------------------------------------------ 기준일 판정

def _quarter(end: str) -> tuple[int, int]:
    year, month = int(end[:4]), int(end[5:7])
    return year, (month - 1) // 3 + 1


def _revenue_period_ends(slug: str) -> dict[str, str]:
    """기업별 마지막 반영 분기. 실적 발표일을 따로 추적하지 않아도 관측의 `period.end` 가 그것을 말한다."""
    out: dict[str, str] = {}
    for item in _items(slug, "observations"):
        if item.get("metric") != "revenue_ttm":
            continue
        end = (item.get("period") or {}).get("end")
        cid = item["company_id"]
        if end and end > out.get(cid, ""):   # 한 기업에 관측이 여럿이면 가장 최근 분기를 본다
            out[cid] = end
    return out


def period_gap(slug: str, prior_slug: str) -> dict[str, Any]:
    """신규 기업이 기존 기업보다 앞선 분기를 보고 있는지 본다. **권고이고 종료 코드를 바꾸지 않는다.**

    결산월이 달라 `period.end` 가 여러 갈래라 날짜 하나로 자르지 않고 기업별로 본다.
    """
    ctx = load_context(slug)
    new_ids = set(ctx.run["companies"])
    prior_ids = set(load_context(prior_slug).run["companies"])
    new_companies = sorted(new_ids - prior_ids)
    ends = _revenue_period_ends(slug)
    existing = {cid: end for cid, end in ends.items() if cid in prior_ids}
    incoming = {cid: end for cid, end in ends.items() if cid in new_companies}
    missing = sorted((new_ids & prior_ids) - set(existing)) + [c for c in new_companies if c not in incoming]

    ahead: list[dict[str, Any]] = []
    if existing and incoming:
        newest_existing = max(_quarter(e) for e in existing.values())
        ahead = [{"company_id": cid, "period_end": end, "quarter": f"{_quarter(end)[0]}Q{_quarter(end)[1]}"}
                 for cid, end in sorted(incoming.items()) if _quarter(end) > newest_existing]

    if not new_companies:
        verdict = "해당 없음"
        advice = "두 실행의 기업 구성이 같다. 더해진 기업이 없으니 견줄 기준일도 없다."
    elif not incoming:
        verdict = "판정 불가"
        advice = "신규 기업의 `revenue_ttm` 관측이 아직 없다. 조사한 뒤 다시 본다."
    elif not existing:
        verdict = "판정 불가"
        advice = "기존 기업의 `revenue_ttm` 관측이 없어 견줄 기준이 없다. 지표 이름이 바뀌지 않았는지 확인한다."
    elif ahead:
        verdict = "전체 재조사 권고"
        advice = ("신규 기업이 기존 기업보다 앞선 분기를 본다 — 그 사이 기존 기업도 실적이 새로 나왔다는 뜻이다. "
                  "전체를 다시 조사하기를 권고한다(권고이고 막지는 않는다).")
    else:
        verdict = "새 기업만 넣어도 된다"
        advice = ("신규 기업이 기존 기업과 같은 분기 안에 있다. 다만 시가총액·주가는 분기와 무관하게 매일 "
                  "움직이므로 **시장 수치는 전 기업 갱신**한다.")
    return {
        "slug": slug, "prior_slug": prior_slug, "new_companies": new_companies,
        "existing": dict(sorted(existing.items())), "incoming": dict(sorted(incoming.items())),
        "quarters": {cid: f"{_quarter(e)[0]}Q{_quarter(e)[1]}" for cid, e in sorted(ends.items())},
        "ahead": ahead, "missing_period": missing, "verdict": verdict, "advice": advice,
        # 비상장사는 분기 실적을 내지 않으므로 기간이 없는 것이 결함이 아니다. 읽는 사람이 헷갈리지 않게 갈라 둔다.
        "missing_unlisted": [c for c in missing if not ctx.companies.get(c, {}).get("listed", True)],
    }
