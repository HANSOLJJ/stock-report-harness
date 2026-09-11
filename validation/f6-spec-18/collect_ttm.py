# SEC companyfacts 에서 F6 v1.7 이 요구하는 TTM 4종을 복원해 관측 초안을 만든다 (기본은 저장 원자료 재사용)
"""`revenue_ttm` · `revenue_ttm_prior` · `net_income_ttm` · `operating_income_ttm` 을 만든다.

## 회계 Q4 는 아무도 태깅하지 않는다

`F6-AVAIL-15` 에서 확인된 사실이다 — 최신 회계연도 Q4 를 분기로 직접 태깅하는 회사가
**0/12** 다. 10-K 에 연간만 싣기 때문이다. 그래서 TTM 은 단순 4분기 합으로 만들 수 없고
**`Q4 = FY − (Q1+Q2+Q3)`** 복원을 거친다.

복원값은 파생이므로 **원자료(FY·Q1·Q2·Q3)를 함께 남긴다.** `ttm_per`·`ps_ratio`·`nonop_share`
가 원자료 없이 완제품으로만 들어와 재계산도 검증도 안 되던 상태를 반복하지 않는다.

## 기간 기준을 관측에 선언한다

세 가지가 나온다. 이름이 `revenue_ttm` 이어도 **실제 기준은 `basis.period_basis` 가 말한다.**

    ttm            분기 4개 합 (복원 Q4 포함). 일반 상장사
    annual         연간 그대로. 20-F 제출사라 분기 기간 사실이 아예 없다
    quarterly_yoy  분기 YoY. 연간 사실이 없는 신규 상장사

`arr` 이 `kind=run_rate` 인데 이름만 ARR 이라 오독을 부른 일(PRIV-ARR-17)이 있었다.
같은 실수를 반복하지 않도록 **소비하는 쪽(`calc_f6_params`)이 이 필드를 실제로 읽어
트랙을 정하고, 기대와 다르면 `pending_data` 로 세운다.**

입력은 기본적으로 `../f6-avail-15/_raw/` 의 저장 원자료다. **신규 네트워크 호출이 없다.**
없을 때만 `--fetch` 로 SEC 를 부른다.

사용:
    python collect_ttm.py            # 저장 원자료 재사용
    python collect_ttm.py --fetch    # 원자료가 없을 때만 SEC 조회
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
AVAIL_RAW = HERE.parent / "f6-avail-15" / "_raw"
RAW = HERE / "_raw"
OUT = HERE / "_derived"

TICKER_TO_ID = {
    "META": "meta", "NVDA": "nvidia", "GOOGL": "alphabet", "MSFT": "microsoft",
    "AMZN": "amazon", "AAPL": "apple", "ORCL": "oracle", "PLTR": "palantir",
    "TSLA": "tesla", "SPCX": "spacex-xai", "TSM": "tsmc", "BABA": "alibaba",
}

# 회사마다 쓰는 개념이 다르다. F6-AVAIL-15 에서 확인한 현행 개념을 coalesce 순서로 둔다.
REVENUE_TAGS = [
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "Revenues"),
    ("ifrs-full", "Revenue"),
    ("ifrs-full", "RevenueFromContractsWithCustomers"),
]
NET_INCOME_TAGS = [("us-gaap", "NetIncomeLoss"), ("ifrs-full", "ProfitLoss")]
OPERATING_TAGS = [("us-gaap", "OperatingIncomeLoss"), ("ifrs-full", "ProfitLossFromOperatingActivities")]

METRIC_TAGS = {
    "revenue_ttm": REVENUE_TAGS,
    "net_income_ttm": NET_INCOME_TAGS,
    "operating_income_ttm": OPERATING_TAGS,
}
DAY_TOL = 10          # 52/53주 회계연도. 근거는 f6-avail-15/REPORT.md 4.1
# P3 는 현지통화로 계산한다. 공시 USD 환산치는 연도별 기말환율이 달라 성장률을 왜곡한다(F6-FX-16).
REPORTING_CURRENCY = {"tsmc": "TWD", "alibaba": "CNY"}


def _d(s: str) -> date:
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def load_facts(ticker: str) -> dict | None:
    for base in (AVAIL_RAW, RAW):
        p = base / f"{ticker}.companyfacts.json"
        if p.is_file():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


def periods(doc: dict, taxonomy: str, tag: str) -> dict[str, list[dict]]:
    node = (doc.get("facts", {}).get(taxonomy) or {}).get(tag)
    if node is None:
        return {}
    out: dict[str, list[dict]] = {}
    for unit, rows in node.get("units", {}).items():
        best: dict[tuple[str, str], dict] = {}
        for r in rows:
            s, e = r.get("start"), r.get("end")
            if not s or not e:
                continue
            key = (s, e)
            prev = best.get(key)
            # 재작성이 있으면 같은 기간에 값이 여럿이다. 가장 최근 filed 하나만 남긴다.
            if prev is None or str(r.get("filed", "")) >= str(prev.get("filed", "")):
                best[key] = r
        rows2 = []
        for (s, e), r in best.items():
            days = (_d(e) - _d(s)).days
            kind = "Q" if 80 <= days <= 100 else ("FY" if 350 <= days <= 380 else "other")
            rows2.append({"start": s, "end": e, "val": r["val"], "days": days, "kind": kind,
                          "form": r.get("form"), "filed": r.get("filed")})
        out[unit] = sorted(rows2, key=lambda r: r["end"])
    return out


def pick_unit(doc: dict, tags: list[tuple[str, str]], reporting_currency: str | None) -> str | None:
    """단위를 먼저 고른다. **현지통화가 기준이다.**

    20-F 제출사는 현지통화와 USD 환산치를 함께 태깅한다. 각 연도가 그 해 기말환율로
    환산되므로 공시 USD 로 성장률을 계산하면 왜곡된다(F6-FX-16).
    """
    units: set[str] = set()
    for tax, tag in tags:
        units |= set(periods(doc, tax, tag).keys())
    if not units:
        return None
    if reporting_currency and reporting_currency in units:
        return reporting_currency
    return sorted(units)[0]


def coalesce_series(doc: dict, tags: list[tuple[str, str]], unit: str) -> tuple[list[dict], dict]:
    """여러 개념을 **하나의 기간 축으로 합친다.** 개념 전환으로 생긴 구멍을 메운다.

    확정 규칙의 "매출 태그 Coalesce" 다. 혼합은 허용하되 조건 둘을 단다(F6-AVAIL-15 4.4).
    혼합 사실을 기록하고, **겹치는 기간이 있으면 두 개념의 값이 일치하는지 검산한다.**
    """
    # 우선순위 — 마지막 분기 종료일이 늦은 개념이 현행이다.
    ranked = []
    for tax, tag in tags:
        rows = periods(doc, tax, tag).get(unit)
        if not rows:
            continue
        q = [r for r in rows if r["kind"] == "Q"]
        ranked.append(((q[-1]["end"] if q else "", rows[-1]["end"], len(q)), tax, tag, rows))
    ranked.sort(key=lambda x: x[0], reverse=True)

    merged: dict[tuple[str, str], dict] = {}
    used: dict[str, int] = {}
    conflicts: list[dict] = []
    for _, tax, tag, rows in ranked:
        for r in rows:
            if r["kind"] == "other":
                continue
            key = (r["start"], r["end"])
            if key in merged:
                prev = merged[key]
                if prev["val"] != r["val"]:
                    base = max(abs(prev["val"]), 1)
                    conflicts.append({"period": f"{r['start']}~{r['end']}",
                                      "kept": {"tag": prev["tag"], "val": prev["val"]},
                                      "other": {"tag": tag, "val": r["val"]},
                                      "rel_diff": abs(prev["val"] - r["val"]) / base})
                continue
            merged[key] = {**r, "taxonomy": tax, "tag": tag}
            used[tag] = used.get(tag, 0) + 1
    series = sorted(merged.values(), key=lambda r: r["end"])
    meta = {"unit": unit, "concepts_used": used, "mixed": len(used) > 1,
            "priority": [f"{tax}:{tag}" for _, tax, tag, _ in ranked],
            "overlap_conflicts": conflicts}
    return series, meta


def quarter_series(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """(분기 시계열, 복원 근거). 회계 Q4 는 FY − (Q1+Q2+Q3) 로 만든다."""
    q = [r for r in rows if r["kind"] == "Q"]
    fy = [r for r in rows if r["kind"] == "FY"]
    derived: list[dict] = []
    series = list(q)
    for f in fy:
        fs, fe = _d(f["start"]), _d(f["end"])
        inside = [r for r in q if fs <= _d(r["start"]) and _d(r["end"]) <= fe]
        if len(inside) != 3:
            continue
        covered = sum(r["val"] for r in inside)
        last_end = max(_d(r["end"]) for r in inside)
        if any(_d(r["end"]) == fe for r in inside):
            continue                       # 이미 Q4 가 태깅돼 있으면 복원하지 않는다
        # 복원값도 어느 개념에서 왔는지 남긴다. FY 와 분기가 서로 다른 개념일 수 있다(기간별 fallback).
        tags = sorted({f.get("tag", "?")} | {r.get("tag", "?") for r in inside})
        item = {"start": last_end.isoformat(), "end": f["end"], "val": f["val"] - covered,
                "days": (fe - last_end).days, "kind": "Q4_derived", "form": f["form"], "filed": f["filed"],
                "taxonomy": f.get("taxonomy"), "tag": "+".join(tags) if len(tags) > 1 else tags[0]}
        derived.append({"fy": f"{f['start']}~{f['end']}", "fy_val": f["val"], "fy_tag": f.get("tag"),
                        "quarters_used": [{"end": r["end"], "val": r["val"], "tag": r.get("tag")} for r in inside],
                        "q4_derived": item["val"], "mixed_concepts": len(tags) > 1})
        series.append(item)
    return sorted(series, key=lambda r: r["end"]), derived


def trailing(series: list[dict], offset: int = 0) -> dict | None:
    """뒤에서 offset 만큼 물러난 지점의 직전 4개 분기 합. 연속하지 않으면 만들지 않는다."""
    end = len(series) - offset
    win = series[end - 4:end]
    if len(win) != 4:
        return None
    for a, b in zip(win, win[1:]):
        gap = (_d(b["start"]) - _d(a["end"])).days
        if not -2 <= gap <= 5:             # 경계일 포함/제외 표기 차이만 허용한다
            return None
    return {"value": sum(r["val"] for r in win), "start": win[0]["start"], "end": win[-1]["end"],
            "quarters": [{"end": r["end"], "val": r["val"], "kind": r["kind"], "tag": r.get("tag")} for r in win]}


def fy_agreement(rows: list[dict], window: dict) -> dict | None:
    """4분기 합이 같은 기간 FY 태깅값과 맞는지 본다.

    맞으면 그 TTM 은 **복원값이 아니라 공시값 그 자체**다(v1.7 `f6.ttm_window.verification`).
    끝점 규약 [A] 가 옳다는 근거가 이 일치다. 매번 확인해 근거로 남긴다.
    """
    for f in rows:
        if f["kind"] == "FY" and f["start"] == window["start"] and f["end"] == window["end"]:
            diff = window["value"] - f["val"]
            return {"fy_val": f["val"], "diff": diff, "matches": diff == 0,
                    "period": f"{f['start']}~{f['end']}"}
    return None


def build(ticker: str) -> dict:
    doc = load_facts(ticker)
    if doc is None:
        return {"ticker": ticker, "loaded": False}
    res: dict = {"ticker": ticker, "company_id": TICKER_TO_ID[ticker], "loaded": True,
                 "entity": doc.get("entityName"), "metrics": {}, "evidence": {}}
    currency = REPORTING_CURRENCY.get(TICKER_TO_ID[ticker])
    for metric, tags in METRIC_TAGS.items():
        unit = pick_unit(doc, tags, currency)
        if unit is None:
            res["metrics"][metric] = {"value": None, "reason": "개념 없음"}
            continue
        rows, mix = coalesce_series(doc, tags, unit)
        res.setdefault("coalesce", {})[metric] = mix
        if not rows:
            res["metrics"][metric] = {"value": None, "reason": "기간 사실 없음"}
            continue
        tax = rows[-1]["taxonomy"]
        tag = "+".join(mix["concepts_used"]) if mix["mixed"] else rows[-1]["tag"]
        series, derived = quarter_series(rows)
        fy = [r for r in rows if r["kind"] == "FY"]
        common = {"taxonomy": tax, "tag": tag, "unit": unit}
        cur = trailing(series)
        prev = trailing(series, offset=4)
        if cur is not None:
            res["metrics"][metric] = {"value": cur["value"], "period_basis": "ttm",
                                      "period": {"start": cur["start"], "end": cur["end"]}, **common}
            res["evidence"][metric] = {"quarters": cur["quarters"], "q4_reconstruction": derived[-2:],
                                       "fy_agreement": fy_agreement(rows, cur)}
            if metric == "revenue_ttm" and prev is not None:
                res["metrics"]["revenue_ttm_prior"] = {"value": prev["value"], "period_basis": "ttm",
                                                       "period": {"start": prev["start"], "end": prev["end"]}, **common}
                res["evidence"]["revenue_ttm_prior"] = {"quarters": prev["quarters"]}
        elif len(fy) >= 1:
            res["metrics"][metric] = {"value": fy[-1]["val"], "period_basis": "annual",
                                      "period": {"start": fy[-1]["start"], "end": fy[-1]["end"]}, **common}
            res["evidence"][metric] = {"annual": fy[-1]}
            if metric == "revenue_ttm" and len(fy) >= 2:
                res["metrics"]["revenue_ttm_prior"] = {"value": fy[-2]["val"], "period_basis": "annual",
                                                       "period": {"start": fy[-2]["start"], "end": fy[-2]["end"]}, **common}
                res["evidence"]["revenue_ttm_prior"] = {"annual": fy[-2]}
        else:
            q = [r for r in series if r["kind"] == "Q"]
            if q:
                # 연간 사실이 없는 신규 상장. 이름은 ttm 이지만 기준은 분기 YoY 라고 선언한다.
                res["metrics"][metric] = {"value": q[-1]["val"], "period_basis": "quarterly_yoy",
                                          "period": {"start": q[-1]["start"], "end": q[-1]["end"]}, **common}
                res["evidence"][metric] = {"quarter": q[-1]}
                if metric == "revenue_ttm":
                    want = _d(q[-1]["end"])
                    prior = next((r for r in q if abs((_d(r["end"]) - date(want.year - 1, want.month, want.day)).days) <= DAY_TOL), None)
                    if prior is not None:
                        res["metrics"]["revenue_ttm_prior"] = {"value": prior["val"], "period_basis": "quarterly_yoy",
                                                               "period": {"start": prior["start"], "end": prior["end"]}, **common}
                        res["evidence"]["revenue_ttm_prior"] = {"quarter": prior}
            else:
                res["metrics"][metric] = {"value": None, "reason": "분기·연간 기간 사실 없음"}
    return res


def main(argv: list[str]) -> int:
    if "--fetch" in argv:
        print("--fetch 는 저장 원자료가 없을 때만 쓴다. 지금은 f6-avail-15/_raw 재사용을 먼저 시도한다.")
    rows = [build(t) for t in TICKER_TO_ID]
    print("=" * 116)
    print("F6-SPEC-18 — SEC companyfacts 에서 TTM 4종 복원 (저장 원자료 재사용, 신규 호출 없음)")
    print("=" * 116)
    print(f"\n{'회사':14} {'기준':14} {'revenue_ttm':>18} {'prior':>18} {'net_income':>16} {'operating':>16}")
    for r in rows:
        if not r.get("loaded"):
            print(f"{r['ticker']:14} 원자료 없음")
            continue
        m = r["metrics"]
        def cell(k):
            v = (m.get(k) or {}).get("value")
            return f"{v:,.0f}" if isinstance(v, (int, float)) else "없음"
        basis = (m.get("revenue_ttm") or {}).get("period_basis", "없음")
        print(f"{r['company_id']:14} {basis:14} {cell('revenue_ttm'):>18} {cell('revenue_ttm_prior'):>18} "
              f"{cell('net_income_ttm'):>16} {cell('operating_income_ttm'):>16}")

    print("\n[혼합·검산] 개념을 섞었는가, 겹치는 기간의 값이 맞는가")
    for r in rows:
        if not r.get("loaded"):
            continue
        mix = (r.get("coalesce") or {}).get("revenue_ttm") or {}
        used = list(mix.get("concepts_used") or {})
        conf = mix.get("overlap_conflicts") or []
        recent = [c for c in conf if c["period"][-10:] >= "2019-01-01"]
        worst = f" · 최대 상대오차 {max(c['rel_diff'] for c in conf):.5f}" if conf else ""
        print(f"  {r['company_id']:14} {'혼합' if mix.get('mixed') else '단일':4} {used}")
        print(f"                 겹침 불일치 {len(conf)}건 · 2019년 이후 {len(recent)}건{worst}")

    print("\n[끝점 검산] 4분기 합이 같은 기간 FY 태깅값과 맞는가 — 맞으면 복원값이 아니라 공시값이다")
    for r in rows:
        if not r.get("loaded"):
            continue
        agree = ((r.get("evidence") or {}).get("revenue_ttm") or {}).get("fy_agreement")
        if agree is None:
            print(f"  {r['company_id']:14} 대조할 FY 없음 (창이 회계연도와 겹치지 않거나 연간·분기 트랙)")
        else:
            mark = "일치" if agree["matches"] else f"차이 {agree['diff']:,}"
            print(f"  {r['company_id']:14} {agree['period']} FY {agree['fy_val']:>18,}  {mark}")

    print("\n[기간별 fallback] 창 4개 분기를 어느 태그가 공급했는가")
    for r in rows:
        if not r.get("loaded"):
            continue
        qs = ((r.get("evidence") or {}).get("revenue_ttm") or {}).get("quarters") or []
        if not qs:
            continue
        tags = [f"{q['end']}:{(q.get('tag') or '?').replace('RevenueFromContractWithCustomerExcludingAssessedTax', 'RFCW')}" for q in qs]
        print(f"  {r['company_id']:14} {' | '.join(tags)}")

    print("\n[개념·기간] 어느 태그를 어느 기간으로 썼는가")
    for r in rows:
        if not r.get("loaded"):
            continue
        m = (r["metrics"].get("revenue_ttm") or {})
        p = m.get("period") or {}
        print(f"  {r['company_id']:14} {m.get('taxonomy','?')}:{m.get('tag','?')[:46]:46} "
              f"[{m.get('unit','?')}] {p.get('start','?')}~{p.get('end','?')}")

    OUT.mkdir(exist_ok=True)
    (OUT / "ttm_inputs.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n_derived/ttm_inputs.json 저장 — 복원 근거(FY·Q1·Q2·Q3)를 함께 담았다")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(sys.argv[1:]))
