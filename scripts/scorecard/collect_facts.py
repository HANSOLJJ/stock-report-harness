# SEC companyfacts 에서 현금흐름·법인세의 최근 1년 값을 누계 산식으로 복원해 관측으로 만드는 수집기
"""`collect --kind facts` 의 계산부. 네트워크는 부르지 않는다(받기는 `stages._collect_facts` 가 `sec_get` 으로 한다).

## 현금흐름표는 누계로만 태깅된다

손익 항목은 분기(3개월) 사실이 있지만 현금흐름 항목은 10-Q 에 **회계연도 시작부터의 누계**(3·6·9개월)만 실린다. 그래서 최근 1년 값은
분기 넷의 합이 아니라 **당기 누계 + 직전 연간 − 전기 같은 누계**로 만든다. 끝이 가장 늦은 사실이 연간(회계연도 말)이면 그 값을 그대로 쓴다.
recheck 의 fcf_ttm 15건(CASH-FCF-35)이 같은 산식이고, 그 basis 성분과 이 계산이 같은지 테스트가 대조한다.

## 지키는 것

- 제출일(filed)이 정보 기준일 뒤인 사실은 버린다. companyfacts 는 받는 날의 전체 이력이라 늦게 받으면 기준일 뒤 공시가 섞인다.
- 같은 기간에 값이 여럿이면(재작성) 가장 늦게 제출된 값을 쓰고 `restated` 로 표시한다.
- 회사가 개념을 바꾼 지표(Amazon·NVIDIA 설비투자는 `PaymentsToAcquireProductiveAssets`)는 마지막 사실이 가장 늦은 개념을 고른다.
- USD 로 보고하는 회사만 다룬다. 20-F 현지통화 회사(TSMC·Alibaba)는 수동 USD 환산 관측을 쓴다.
- 자료가 모자라면 값을 만들지 않고 이유를 돌려준다. 0 으로 채우지 않는다.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
TAXONOMY = "us-gaap"
UNIT = "USD"

# 지표 → 후보 개념(앞이 우선, 단 마지막 사실이 더 늦은 개념이 있으면 그것). fcf_ttm 은 내지 않는다 — ⑨ 입력은 수동·공시 관측(SpaceX
# S-1, TSMC·Alibaba 환산 등)이 섞여 있어 수집기가 덮지 않고, 현금 연결표가 OCF − 설비투자를 그 fcf_ttm 과 따로 대조한다.
FACT_METRICS: dict[str, tuple[str, ...]] = {
    "ocf_ttm": ("NetCashProvidedByUsedInOperatingActivities",),
    "capex_ttm": ("PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets"),
    # 규칙 v2.1 ⑥ 이익 조정의 실효세율 분자. 세전이익과 같은 연결 범위다.
    "income_tax_ttm": ("IncomeTaxExpenseBenefit",),
}

FY_DAYS = (350, 380)     # 회계연도 하나의 길이(종료일 − 시작일). 52/53주 회계연도를 받는다
START_TOL = 3            # 누계 시작일과 직전 연간 종료일 다음 날의 허용 차이
DAY_TOL = 10             # 전기 같은 누계를 찾을 때 종료일·길이의 허용 차이(52/53주)

FORMULAS = {
    "fy_direct": "회계연도 연간 값 그대로(끝이 회계연도 말)",
    "ytd": "당기 누계 + 직전 연간 − 전기 같은 누계",
}


def _d(s: str) -> date:
    return date.fromisoformat(s)


def _year_back(d: date) -> date:
    try:
        return d.replace(year=d.year - 1)
    except ValueError:      # 2월 29일
        return d.replace(year=d.year - 1, day=28)


def duration_facts(doc: dict[str, Any], tag: str, *, filed_until: str) -> list[dict[str, Any]]:
    """한 개념의 기간 사실. (시작, 종료)마다 제출일이 기준일 이하인 것 가운데 가장 늦게 제출된 하나를 남긴다."""
    node = ((doc.get("facts") or {}).get(TAXONOMY) or {}).get(tag) or {}
    rows = (node.get("units") or {}).get(UNIT) or []
    best: dict[tuple[str, str], dict[str, Any]] = {}
    values: dict[tuple[str, str], set] = {}
    for r in rows:
        start, end, filed, val = r.get("start"), r.get("end"), str(r.get("filed") or ""), r.get("val")
        if not start or not end or not filed or filed > filed_until:
            continue
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        key = (start, end)
        values.setdefault(key, set()).add(val)
        prev = best.get(key)
        if prev is None or (filed, str(r.get("accn") or "")) > (str(prev["filed"]), str(prev.get("accn") or "")):
            best[key] = r
    out = []
    for (start, end), r in best.items():
        out.append({"start": start, "end": end, "val": r["val"], "days": (_d(end) - _d(start)).days,
                    "accession": r.get("accn"), "form": r.get("form"), "filed": r.get("filed"),
                    "restated": len(values[(start, end)]) > 1})
    return sorted(out, key=lambda x: (x["end"], x["start"]))


def pick_concept(doc: dict[str, Any], tags: tuple[str, ...], *, filed_until: str) -> tuple[str | None, list[dict[str, Any]]]:
    """후보 개념 가운데 마지막 사실의 종료일이 가장 늦은 것. 같으면 앞의 후보."""
    best: tuple[str, str, list[dict[str, Any]]] | None = None
    for tag in tags:
        rows = duration_facts(doc, tag, filed_until=filed_until)
        if not rows:
            continue
        last = rows[-1]["end"]
        if best is None or last > best[0]:
            best = (last, tag, rows)
    return (best[1], best[2]) if best else (None, [])


def _part(role: str, r: dict[str, Any]) -> dict[str, Any]:
    part = {"role": role, "start": r["start"], "end": r["end"], "val": r["val"],
            "accession": r["accession"], "form": r["form"], "filed": r["filed"]}
    if r["restated"]:
        part["restated"] = True
    return part


def ttm(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """최근 1년 값. {value, period, formula, components} 또는 {value: None, reason}."""
    if not rows:
        return {"value": None, "reason": "기간 사실이 없다"}
    end = rows[-1]["end"]
    at_end = [r for r in rows if r["end"] == end and r["days"] <= FY_DAYS[1]]
    if not at_end:
        return {"value": None, "reason": f"{end} 에 끝나는 1년 이하 기간 사실이 없다"}
    cur = max(at_end, key=lambda r: r["days"])
    if cur["days"] >= FY_DAYS[0]:
        return {"value": cur["val"], "period": {"start": cur["start"], "end": end}, "formula": "fy_direct",
                "components": [_part("fy", cur)]}
    fy_end = _d(cur["start"]) - timedelta(days=1)
    fys = [r for r in rows if FY_DAYS[0] <= r["days"] <= FY_DAYS[1] and abs((_d(r["end"]) - fy_end).days) <= START_TOL]
    if not fys:
        return {"value": None, "reason": f"누계 {cur['start']}~{end} 직전 회계연도의 연간 값이 없다"}
    prior_fy = min(fys, key=lambda r: abs((_d(r["end"]) - fy_end).days))
    want = _year_back(_d(end))
    priors = [r for r in rows
              if abs((_d(r["start"]) - _d(prior_fy["start"])).days) <= START_TOL
              and abs((_d(r["end"]) - want).days) <= DAY_TOL
              and abs(r["days"] - cur["days"]) <= DAY_TOL]
    if not priors:
        return {"value": None, "reason": f"전기 같은 누계({prior_fy['start']} 시작, {want.isoformat()} 무렵 종료)가 없다"}
    prior = min(priors, key=lambda r: abs((_d(r["end"]) - want).days))
    value = cur["val"] + prior_fy["val"] - prior["val"]
    start = (_d(prior["end"]) + timedelta(days=1)).isoformat()
    return {"value": value, "period": {"start": start, "end": end}, "formula": "ytd",
            "components": [_part("curr_ytd", cur), _part("prior_fy", prior_fy), _part("prior_ytd", prior)]}


def fact_observations(company: dict[str, Any], doc: dict[str, Any], *, source_id: str, observed_at: str,
                      filed_until: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """(관측, 지표별 결과). 결과는 값을 만들지 못한 지표의 이유도 담는다."""
    cid = company["company_id"]
    observations: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for metric, tags in FACT_METRICS.items():
        tag, rows = pick_concept(doc, tags, filed_until=filed_until)
        if tag is None:
            results.append({"metric": metric, "status": "no_concept", "reason": f"{TAXONOMY} {'/'.join(tags)} [{UNIT}] 사실이 없다"})
            continue
        res = ttm(rows)
        if res["value"] is None:
            results.append({"metric": metric, "status": "insufficient", "concept": tag, "reason": res["reason"]})
            continue
        end = res["period"]["end"]
        observations.append({
            "observation_id": f"{cid}.{metric}.sec{end.replace('-', '')}",
            "company_id": cid,
            "metric": metric,
            "value": res["value"],
            "unit": UNIT,
            "as_of": end,
            "observed_at": observed_at,
            "kind": "actual" if res["formula"] == "fy_direct" else "derived",
            "source_id": source_id,
            "status": "verified",
            "period": res["period"],
            "basis": {"period_basis": "ttm", "concept": f"{TAXONOMY}:{tag}", "formula": FORMULAS[res["formula"]],
                      "components": res["components"], "filed_until": filed_until, "collector": "collect --kind facts"},
        })
        results.append({"metric": metric, "status": "collected", "concept": tag, "value": res["value"], "period": res["period"]})
    return observations, results


def facts_source_entry(company: dict[str, Any], fetched: dict[str, Any], *, filed_until: str, from_file: bool) -> dict[str, Any]:
    """sources.json 항목. 회사·받은 날마다 하나다(SRC-SEC-FACTS-<티커>-<YYYYMMDD>)."""
    cik = int(company["cik"])
    day = fetched["fetched_at"][:10]
    where = f"파일 {fetched['path']}" if from_file else f"원문 캐시 data/_sec/docs/{fetched['path'].replace(chr(92), '/').rsplit('/', 1)[-1]}(gitignore)"
    return {
        "source_id": f"SRC-SEC-FACTS-{str(company['ticker']).upper()}-{day.replace('-', '')}",
        "title": f"SEC XBRL companyfacts CIK{cik:010d} ({company.get('display_name') or company['company_id']}, {day} 수집)",
        "publisher": "SEC EDGAR",
        "url": COMPANYFACTS_URL.format(cik=cik),
        "accessed_at": fetched["fetched_at"],
        "sha256": fetched["sha256"],
        "conflict_of_interest": None,
        "note": f"collect --kind facts. {where}. 제출일 {filed_until} 이하 사실만 썼다",
        "kind": "filing",
        "company_id": company["company_id"],
    }
