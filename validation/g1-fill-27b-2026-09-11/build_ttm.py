# G1-FILL-27B: 상장 12개사의 TTM 매출·영업손익을 보존된 SEC companyfacts 에서 복원한다.
# 규약 넷을 전제하지 않고 영업손익에 적용되는지 검증하며 진행한다. 통화는 현지통화.
import datetime as dt
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
MINE = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw")
# C-13 의 _raw 는 SEC 원본 스냅샷이라 원천으로만 읽는다. 상대의 보고서·파생물은 열지 않는다.
C13 = os.path.join(HERE, "..", "..", "..", "C-13", "validation", "f6-avail-15b", "_raw")

SOURCES = {
    "tsmc": (os.path.join(MINE, "sec-TSM-companyfacts.json"), "내 워크트리 F6-FX-16"),
    "alibaba": (os.path.join(MINE, "sec-BABA-companyfacts.json"), "내 워크트리 F6-FX-16"),
    "apple": (os.path.join(C13, "CIK0000320193_AAPL.json"), "C-13 _raw (SEC 원본)"),
    "microsoft": (os.path.join(C13, "CIK0000789019_MSFT.json"), "C-13 _raw (SEC 원본)"),
    "amazon": (os.path.join(C13, "CIK0001018724_AMZN.json"), "C-13 _raw (SEC 원본)"),
    "nvidia": (os.path.join(C13, "CIK0001045810_NVDA.json"), "C-13 _raw (SEC 원본)"),
    "spacex-xai": (os.path.join(C13, "CIK0001181412_SPCX.json"), "C-13 _raw (SEC 원본)"),
    "tesla": (os.path.join(C13, "CIK0001318605_TSLA.json"), "C-13 _raw (SEC 원본)"),
    "palantir": (os.path.join(C13, "CIK0001321655_PLTR.json"), "C-13 _raw (SEC 원본)"),
    "meta": (os.path.join(C13, "CIK0001326801_META.json"), "C-13 _raw (SEC 원본)"),
    "oracle": (os.path.join(C13, "CIK0001341439_ORCL.json"), "C-13 _raw (SEC 원본)"),
    "alphabet": (os.path.join(C13, "CIK0001652044_GOOGL.json"), "C-13 _raw (SEC 원본)"),
}

# 규약 3: 개념 Coalesce 는 회사별 선택이 아니라 기간별 fallback. 우선순위 순서대로 시도한다.
REV_CANDIDATES = [
    ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax"),
    ("us-gaap", "Revenues"),
    ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax"),
    ("ifrs-full", "RevenueFromContractsWithCustomers"),
    ("ifrs-full", "Revenue"),
]
OP_CANDIDATES = [
    ("us-gaap", "OperatingIncomeLoss"),
    ("ifrs-full", "ProfitLossFromOperatingActivities"),
    ("ifrs-full", "OperatingIncomeLoss"),
]


def days(s, e):
    return (dt.date.fromisoformat(e) - dt.date.fromisoformat(s)).days


def load(cid):
    path, origin = SOURCES[cid]
    d = json.load(io.open(path, encoding="utf-8"))
    return d, origin, os.path.relpath(path, HERE)


def local_unit(facts):
    """현지통화 = 매출·영업손익 개념이 실제로 표시된 통화 중 관측이 가장 많은 것.
    전체 facts 로 세면 EUR 표시 부채 등에 끌려간다(초판 버그: MSFT·ORCL 이 EUR 로 잡혔다)."""
    seen = {}
    for tax, cname in REV_CANDIDATES + OP_CANDIDATES:
        body = facts.get(tax, {}).get(cname)
        if not body:
            continue
        for u, entries in (body.get("units") or {}).items():
            if "/" in u or u in ("shares", "pure"):
                continue
            seen[u] = seen.get(u, 0) + len(entries)
    if not seen:
        return None
    return max(seen.items(), key=lambda kv: kv[1])[0]


def series(facts, cands, unit):
    """기간별 Coalesce. (start,end) -> {'val','concept','taxonomy','form','filed','accn'}
    우선순위가 높은 개념이 그 기간에 값을 가지면 그것을 쓰고, 없으면 다음 개념으로 내려간다."""
    out = {}
    for tax, cname in cands:
        body = facts.get(tax, {}).get(cname)
        if not body:
            continue
        for e in (body.get("units") or {}).get(unit, []):
            s, en = e.get("start"), e.get("end")
            if not s or not en:
                continue
            k = (s, en)
            if k in out:
                continue  # 이미 상위 개념이 채움
            out[k] = {"val": e["val"], "concept": cname, "taxonomy": tax,
                      "form": e.get("form"), "filed": e.get("filed"),
                      "accn": e.get("accn"), "fy": e.get("fy"), "fp": e.get("fp")}
    # 같은 기간이 여러 제출본에 있으면 최신 제출본
    latest = {}
    for tax, cname in cands:
        body = facts.get(tax, {}).get(cname)
        if not body:
            continue
        for e in (body.get("units") or {}).get(unit, []):
            s, en = e.get("start"), e.get("end")
            if not s or not en:
                continue
            k = (s, en)
            cur = latest.get(k)
            if cur is None or (e.get("filed") or "") > (cur.get("filed") or ""):
                if k in out and out[k]["concept"] != cname:
                    continue  # Coalesce 우선순위 유지
                latest[k] = {"val": e["val"], "concept": cname, "taxonomy": tax,
                             "form": e.get("form"), "filed": e.get("filed"),
                             "accn": e.get("accn"), "fy": e.get("fy"), "fp": e.get("fp")}
    for k, v in latest.items():
        out[k] = v
    return out


def split(s):
    q = {k: v for k, v in s.items() if 80 <= days(*k) <= 100}
    a = {k: v for k, v in s.items() if 350 <= days(*k) <= 380}
    return q, a


def build(cid):
    d, origin, relpath = load(cid)
    facts = d["facts"]
    unit = local_unit(facts)
    rec = {"company_id": cid, "entity": d.get("entityName"), "cik": d.get("cik"),
           "source_file": relpath, "source_origin": origin, "currency": unit,
           "taxonomies": {t: len(c) for t, c in facts.items()}}

    rev = series(facts, REV_CANDIDATES, unit)
    op = series(facts, OP_CANDIDATES, unit)
    rq, ra = split(rev)
    oq, oa = split(op)
    rec["counts"] = {"revenue_quarterly": len(rq), "revenue_annual": len(ra),
                     "operating_quarterly": len(oq), "operating_annual": len(oa)}
    rec["concepts_used"] = {
        "revenue": sorted({v["taxonomy"] + ":" + v["concept"] for v in rev.values()}),
        "operating": sorted({v["taxonomy"] + ":" + v["concept"] for v in op.values()}),
    }
    return rec, {"rev": rev, "op": op, "rq": rq, "ra": ra, "oq": oq, "oa": oa}


if __name__ == "__main__":
    out = {}
    print("%-12s %-6s %-28s %-9s %-9s %-9s %-9s" % (
        "company", "통화", "taxonomy(개념수)", "매출Q", "매출A", "영업Q", "영업A"))
    print("-" * 96)
    for cid in SOURCES:
        rec, _ = build(cid)
        out[cid] = rec
        tx = ", ".join("%s(%d)" % (t, n) for t, n in rec["taxonomies"].items()
                       if t in ("us-gaap", "ifrs-full"))
        c = rec["counts"]
        print("%-12s %-6s %-28s %-9d %-9d %-9d %-9d" % (
            cid, rec["currency"], tx, c["revenue_quarterly"], c["revenue_annual"],
            c["operating_quarterly"], c["operating_annual"]))
    io.open(os.path.join(HERE, "inventory.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("\nsaved inventory.json")
