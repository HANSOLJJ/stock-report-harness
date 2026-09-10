# 저장된 companyfacts 만 읽어 F6 재정의에 필요한 태그가 있는지·원하는 기간으로 뽑히는지 판정한다 (신규 호출 없음)
"""F6-AVAIL-15 의 판정 단계다. **값을 뽑는 것이 아니라 있는지만 본다.**

`collect_facts.py` 가 `_raw/` 에 받아 둔 것만 읽는다. 네트워크를 쓰지 않는다.

## 확인 항목과 이 스크립트의 대응

    1 매출     : 후보 개념 중 **실제 값이 있는 것**을 회사별로 찾는다. 후보 목록 밖 개념을
                 놓치지 않도록 taxonomy 전체에서 매출류 태그를 함께 훑어 출력한다.
    2 순이익   : NetIncomeLoss 존재
    3 영업이익 : OperatingIncomeLoss 존재
    4 전년 동기: **개념이 있다는 것과 원하는 기간으로 뽑힌다는 것은 다르다.**
                 최근 분기 4개와 그 전년 동기 4개가 **같은 개념으로** 잡히는지 따로 센다.
                 TTM 이 필요하므로 회계 4분기 직접 태깅 여부와 연간−(Q1+Q2+Q3) 복원 가능성도 본다.
                 개념이 중간에 바뀐 회사는 개념별 연도 구간으로 드러난다.

**추측으로 채우지 않는다.** 없으면 `없음` 으로 적는다.

사용:
    python inventory.py            # inventory-output.txt 와 같은 결과
    python inventory.py --json     # 파생 인벤토리를 _derived/inventory.json 으로 저장
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"
DERIVED = HERE / "_derived"

TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]

# 매출 최상단 후보. 과제가 지목한 셋에 실무에서 쓰이는 형제 개념을 더했다.
REVENUE_CANDIDATES = [
    ("us-gaap", "Revenues"),
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"),
    ("us-gaap", "SalesRevenueNet"),
    ("us-gaap", "SalesRevenueGoodsNet"),
    ("us-gaap", "SalesRevenueServicesNet"),
    ("ifrs-full", "Revenue"),
]
NET_INCOME = [("us-gaap", "NetIncomeLoss"), ("ifrs-full", "ProfitLoss")]
OPERATING_INCOME = [("us-gaap", "OperatingIncomeLoss"), ("ifrs-full", "ProfitLossFromOperatingActivities")]

# 매출류로 **읽힐 수 있는** 태그를 훑을 때 최상단이 아닌 것을 걸러 낸다. 판정이 아니라 표시용이다.
NOT_TOPLINE = ("Cost", "Deferred", "IncreaseDecrease", "Unearned", "Remaining", "Contract",
               "Receivable", "Percentage", "Member", "Expense", "Tax", "Threshold")
DAY_TOL = 10          # 같은 분기로 볼 종료일 허용 오차
UNKNOWN = "없음"


def _d(s: str) -> date:
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def period_kind(days: int) -> str:
    """기간 길이로 분기·반기·3분기·연간을 가른다."""
    if 80 <= days <= 100:
        return "Q"
    if 170 <= days <= 195:
        return "H"
    if 260 <= days <= 285:
        return "3Q"
    if 350 <= days <= 380:
        return "FY"
    return "other"


def load(ticker: str) -> dict | None:
    p = RAW / f"{ticker}.companyfacts.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def concept(doc: dict, taxonomy: str, tag: str) -> dict | None:
    return (doc.get("facts", {}).get(taxonomy) or {}).get(tag)


def periods(node: dict) -> dict[str, list[dict]]:
    """단위별로 기간 사실을 정리한다. 같은 (start,end) 는 최신 filed 하나만 남긴다."""
    out: dict[str, list[dict]] = {}
    for unit, rows in node.get("units", {}).items():
        best: dict[tuple[str, str], dict] = {}
        for r in rows:
            s, e = r.get("start"), r.get("end")
            if not s or not e:
                continue                       # 시점(instant) 사실은 기간 지표가 아니다
            key = (s, e)
            prev = best.get(key)
            if prev is None or str(r.get("filed", "")) >= str(prev.get("filed", "")):
                best[key] = r
        rows2 = []
        for (s, e), r in best.items():
            days = (_d(e) - _d(s)).days
            rows2.append({**r, "_days": days, "_kind": period_kind(days)})
        out[unit] = sorted(rows2, key=lambda r: r["end"])
    return out


def summarize(node: dict | None) -> dict:
    """태그 하나의 존재·단위·기간 축 요약. 값은 담지 않는다."""
    if node is None:
        return {"present": False}
    per = periods(node)
    res: dict = {"present": True, "label": node.get("label"), "units": sorted(per.keys()), "by_unit": {}}
    for unit, rows in per.items():
        kinds = defaultdict(int)
        for r in rows:
            kinds[r["_kind"]] += 1
        q = [r for r in rows if r["_kind"] == "Q"]
        fy = [r for r in rows if r["_kind"] == "FY"]
        res["by_unit"][unit] = {
            "n": len(rows), "kinds": dict(kinds),
            "first_end": rows[0]["end"] if rows else None,
            "last_end": rows[-1]["end"] if rows else None,
            "n_q": len(q), "n_fy": len(fy),
            "last_q_end": q[-1]["end"] if q else None,
            "last_fy_end": fy[-1]["end"] if fy else None,
            "forms": sorted({r.get("form") for r in rows if r.get("form")}),
            "fy_years": sorted({int(r["end"][:4]) for r in rows}),
        }
    return res


def prior_year_check(node: dict, unit: str, n: int = 4) -> dict:
    """**같은 개념으로** 최근 분기 n개와 그 전년 동기가 각각 잡히는지 센다.

    개념이 있다는 것과 원하는 기간으로 뽑힌다는 것은 다르다. 여기가 그 차이를 재는 자리다.
    """
    rows = [r for r in periods(node).get(unit, []) if r["_kind"] == "Q"]
    if not rows:
        return {"n_recent": 0, "matched": 0, "pairs": [], "note": "분기 사실 없음"}
    ends = [_d(r["end"]) for r in rows]
    recent = ends[-n:]
    pairs = []
    for e in recent:
        want = date(e.year - 1, e.month, min(e.day, 28)) if e.month == 2 else date(e.year - 1, e.month, e.day)
        hit = next((x for x in ends if abs((x - want).days) <= DAY_TOL), None)
        pairs.append({"quarter_end": e.isoformat(), "prior_wanted": want.isoformat(),
                      "prior_found": hit.isoformat() if hit else None})
    return {"n_recent": len(recent), "matched": sum(1 for p in pairs if p["prior_found"]), "pairs": pairs}


def ttm_check(node: dict, unit: str) -> dict:
    """TTM 을 만들 수 있는가. 회계 4분기가 직접 태깅되는 곳은 드물어 연간−(Q1+Q2+Q3) 복원이 필요하다."""
    rows = periods(node).get(unit, [])
    q = [r for r in rows if r["_kind"] == "Q"]
    fy = [r for r in rows if r["_kind"] == "FY"]
    if not q:
        return {"consecutive_4q": False, "note": "분기 사실 없음", "fy_minus_3q": False}
    ends = sorted({_d(r["end"]) for r in q})
    last4 = ends[-4:]
    ok = len(last4) == 4 and all(70 <= (last4[i + 1] - last4[i]).days <= 110 for i in range(3))
    # 연간 − (Q1+Q2+Q3) 복원 가능성 — 최신 연간 구간 안에 분기 3개가 있는가
    recover = False
    detail = None
    if fy:
        f = fy[-1]
        fs, fe = _d(f["start"]), _d(f["end"])
        inside = [r for r in q if fs <= _d(r["start"]) and _d(r["end"]) <= fe]
        recover = len(inside) >= 3
        detail = {"fy": f"{f['start']}~{f['end']}", "quarters_inside": len(inside)}
    return {"consecutive_4q": ok,
            "last4_ends": [d.isoformat() for d in last4],
            "fy_minus_3q": recover, "fy_detail": detail}


def revenue_pick(doc: dict) -> list[dict]:
    """실제 값이 있는 매출 개념을 전부 찾는다. 하나를 고르지 않고 회사별 사용 개념을 그대로 낸다."""
    found = []
    for tax, tag in REVENUE_CANDIDATES:
        node = concept(doc, tax, tag)
        if node is None:
            continue
        s = summarize(node)
        for unit, u in s["by_unit"].items():
            found.append({"taxonomy": tax, "tag": tag, "unit": unit, **u})
    return found


def other_revenue_tags(doc: dict) -> dict[str, list[str]]:
    """후보 목록 밖에서 매출로 읽힐 수 있는 태그. **판정이 아니라 놓친 개념이 없는지 보려는 표시다.**"""
    out: dict[str, list[str]] = {}
    named = {tag for _, tag in REVENUE_CANDIDATES}
    for tax, tags in doc.get("facts", {}).items():
        hits = [t for t in tags
                if ("Revenue" in t or t.startswith("Sales")) and t not in named
                and not any(k in t for k in NOT_TOPLINE)]
        if hits:
            out[tax] = sorted(hits)
    return out


def build(ticker: str) -> dict:
    doc = load(ticker)
    if doc is None:
        return {"ticker": ticker, "loaded": False}
    res: dict = {"ticker": ticker, "loaded": True, "entity": doc.get("entityName"),
                 "taxonomies": {k: len(v) for k, v in doc.get("facts", {}).items()},
                 "revenue": revenue_pick(doc), "revenue_other_tags": other_revenue_tags(doc)}
    for name, cands in (("net_income", NET_INCOME), ("operating_income", OPERATING_INCOME)):
        hits = []
        for tax, tag in cands:
            node = concept(doc, tax, tag)
            if node is not None:
                s = summarize(node)
                for unit, u in s["by_unit"].items():
                    hits.append({"taxonomy": tax, "tag": tag, "unit": unit, **u})
        res[name] = hits

    # 항목 4 — **현행** 매출 개념으로 기간 축을 본다. 고르는 기준이 두 번 틀렸던 자리다.
    #   (1) 사실 개수로 고르면 폐기된 개념이 뽑힌다 — MSFT·AMZN·AAPL 의 SalesRevenueNet 은 2018 에 끝났다.
    #   (2) 마지막 보고 시점으로 고르면 **연간만 최신인** 개념이 뽑힌다 — ORCL 의 Revenues 는
    #       연간이 2026-05-31 까지 있으나 분기는 2022-05-31 에서 끊긴다.
    # 항목 4 가 묻는 것은 분기 축이므로 **마지막 분기 종료일**을 1순위로 둔다.
    usable = [r for r in res["revenue"] if r["n_q"] > 0] or res["revenue"]
    if usable:
        main = max(usable, key=lambda r: (r["last_q_end"] or "", r["last_end"] or "", r["n_q"]))
        node = concept(doc, main["taxonomy"], main["tag"])
        res["revenue_main"] = {"taxonomy": main["taxonomy"], "tag": main["tag"], "unit": main["unit"]}
        res["prior_year"] = prior_year_check(node, main["unit"])
        res["ttm"] = ttm_check(node, main["unit"])
    else:
        res["revenue_main"] = None
        res["prior_year"] = {"note": "매출 개념 없음"}
        res["ttm"] = {"note": "매출 개념 없음"}
    return res


def fmt_units(hits: list[dict]) -> str:
    if not hits:
        return UNKNOWN
    return " / ".join(f"{h['tag']}[{h['unit']}] n={h['n']} Q={h['n_q']} FY={h['n_fy']}" for h in hits)


def main(save_json: bool = False) -> int:
    meta = json.loads((RAW / "meta.json").read_text(encoding="utf-8"))
    rows = [build(t) for t in TICKERS]

    print("=" * 118)
    print(f"F6-AVAIL-15 — SEC companyfacts 태그 가용성 인벤토리 (수집 {meta['collected_at_utc']}, 신규 호출 없음)")
    print("=" * 118)

    print("\n[0] 수집 결과")
    print(f"{'티커':6} {'CIK':>10} {'HTTP':>5}  entityName")
    for r in rows:
        t = r["ticker"]
        print(f"{t:6} {meta['ciks'].get(t, '-'):>10} {str(meta['http'].get(t)):>5}  {r.get('entity') or UNKNOWN}")

    print("\n[1] 매출 — 회사별 실제 사용 개념 (값이 있는 것만)")
    print(f"{'티커':6} {'taxonomy':10} {'개념':52} {'unit':6} {'분기':>5} {'연간':>5}  연도 구간")
    for r in rows:
        if not r["revenue"]:
            print(f"{r['ticker']:6} {UNKNOWN}")
            continue
        for h in r["revenue"]:
            yrs = h["fy_years"]
            span = f"{yrs[0]}~{yrs[-1]}" if yrs else "-"
            print(f"{r['ticker']:6} {h['taxonomy']:10} {h['tag'][:52]:52} {h['unit']:6} "
                  f"{h['n_q']:>5} {h['n_fy']:>5}  {span}")

    print("\n[1b] 후보 목록 밖 매출류 태그 — 놓친 개념이 없는지 보는 표시 항목 (판정 아님)")
    for r in rows:
        other = r.get("revenue_other_tags") or {}
        flat = [f"{tax}:{t}" for tax, ts in other.items() for t in ts]
        print(f"  {r['ticker']:6} {', '.join(flat) if flat else '(없음)'}")

    print("\n[2] 순이익 · [3] 영업이익")
    print(f"{'티커':6} {'NetIncomeLoss 계열':62} {'OperatingIncomeLoss 계열'}")
    for r in rows:
        print(f"{r['ticker']:6} {fmt_units(r['net_income'])[:62]:62} {fmt_units(r['operating_income'])[:60]}")

    print("\n[4] 전년 동기를 **같은 개념으로** 뽑을 수 있는가 — 매출 주 개념 기준")
    print(f"{'티커':6} {'주 개념':50} {'전년동기':>8} {'최근4Q연속':>10} {'FY-3Q복원':>10}")
    for r in rows:
        m = r.get("revenue_main")
        if not m:
            print(f"{r['ticker']:6} {UNKNOWN}")
            continue
        py, tt = r["prior_year"], r["ttm"]
        matched = f"{py.get('matched', 0)}/{py.get('n_recent', 0)}"
        print(f"{r['ticker']:6} {m['tag'][:50]:50} {matched:>8} "
              f"{('O' if tt.get('consecutive_4q') else 'X'):>10} {('O' if tt.get('fy_minus_3q') else 'X'):>10}")

    print("\n[4a] 매출 개념별 마지막 보고 시점 — 개념이 바뀐 회사가 여기서 드러난다")
    print("     현행은 **마지막 분기 종료일**로 고른다. 사실 개수로 고르면 폐기된 개념이,")
    print("     마지막 연간으로 고르면 분기가 끊긴 개념이 뽑힌다(ORCL Revenues).")
    print(f"{'티커':6} {'개념':52} {'unit':5} {'마지막 분기':>11} {'마지막 연간':>11}  상태")
    for r in rows:
        if not r["revenue"]:
            print(f"{r['ticker']:6} {UNKNOWN}")
            continue
        m = r.get("revenue_main") or {}
        newest_q = max((h["last_q_end"] or "") for h in r["revenue"])
        newest_fy = max((h["last_end"] or "") for h in r["revenue"])
        for h in sorted(r["revenue"], key=lambda x: (x["last_q_end"] or "", x["last_end"] or "")):
            same_q = newest_q and (h["last_q_end"] or "") == newest_q
            if h["tag"] == m.get("tag") and h["unit"] == m.get("unit"):
                mark = "**현행**"
            elif same_q or (not newest_q and (h["last_end"] or "") == newest_fy):
                # 최신 시점이 같으면 폐기가 아니라 **같은 기간에 함께 태깅**된 것이다.
                mark = "병행(같은 기간 함께 태깅)"
            elif (h["last_end"] or "") == newest_fy:
                # 연간만 최신인 경우다. ORCL 의 Revenues 가 여기다 — 분기는 2022 에서 끊긴다.
                mark = "연간만 최신(분기 끊김)"
            else:
                mark = "폐기"
            print(f"{r['ticker']:6} {h['tag'][:52]:52} {h['unit']:5} "
                  f"{str(h['last_q_end']):>11} {str(h['last_end']):>11}  {mark}")

    print("\n[4b] 전년 동기 대조 상세 — 최근 4개 분기 각각")
    for r in rows:
        py = r.get("prior_year") or {}
        if not py.get("pairs"):
            print(f"  {r['ticker']:6} {py.get('note', UNKNOWN)}")
            continue
        for p in py["pairs"]:
            mark = p["prior_found"] or "없음"
            print(f"  {r['ticker']:6} {p['quarter_end']}  전년 기대 {p['prior_wanted']}  →  {mark}")

    print("\n[4c] TTM 구성 근거 — 최근 4분기 종료일과 연간 구간 안의 분기 수")
    for r in rows:
        tt = r.get("ttm") or {}
        if "last4_ends" not in tt:
            print(f"  {r['ticker']:6} {tt.get('note', UNKNOWN)}")
            continue
        det = tt.get("fy_detail") or {}
        print(f"  {r['ticker']:6} 최근4Q {tt['last4_ends']}  연간 {det.get('fy', UNKNOWN)} 안의 분기 {det.get('quarters_inside', 0)}개")

    print("\n" + "=" * 118)
    n = len(rows)
    have_rev = sum(1 for r in rows if r["revenue"])
    have_ni = sum(1 for r in rows if r["net_income"])
    have_oi = sum(1 for r in rows if r["operating_income"])
    have_py = sum(1 for r in rows if (r.get("prior_year") or {}).get("matched", 0) >= 4)
    have_ttm = sum(1 for r in rows if (r.get("ttm") or {}).get("consecutive_4q"))
    have_rec = sum(1 for r in rows if (r.get("ttm") or {}).get("fy_minus_3q"))
    have_ni_gaap = sum(1 for r in rows if any(h["tag"] == "NetIncomeLoss" for h in r["net_income"]))
    have_oi_gaap = sum(1 for r in rows if any(h["tag"] == "OperatingIncomeLoss" for h in r["operating_income"]))
    for label, v in (("매출 개념 존재", have_rev),
                     ("순이익 존재(계열 포함)", have_ni), ("  그중 us-gaap:NetIncomeLoss", have_ni_gaap),
                     ("영업이익 존재(계열 포함)", have_oi), ("  그중 us-gaap:OperatingIncomeLoss", have_oi_gaap),
                     ("전년 동기 4/4", have_py),
                     ("최근 4분기 연속(직접)", have_ttm), ("FY-(Q1+Q2+Q3) 복원 가능", have_rec)):
        print(f"  {label:28} {v}/{n}")
    print("=" * 118)

    if save_json:
        DERIVED.mkdir(exist_ok=True)
        (DERIVED / "inventory.json").write_text(
            json.dumps({"collected_at_utc": meta["collected_at_utc"], "companies": rows},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n_derived/inventory.json 저장")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main(save_json="--json" in sys.argv))
