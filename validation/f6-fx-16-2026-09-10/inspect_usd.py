# F6-FX-16: USD 로 태그된 관측이 어느 기간에 붙어 있는지 확인한다.
# convenience translation 은 보통 최신 1개 회계연도에만 붙으므로 그 범위를 본다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

TARGETS = {
    "TSM": [("ifrs-full", "Revenue"),
            ("ifrs-full", "ProfitLoss"),
            ("ifrs-full", "ProfitLossAttributableToOwnersOfParent"),
            ("ifrs-full", "ProfitLossFromOperatingActivities"),
            ("ifrs-full", "GrossProfit")],
    "BABA": [("us-gaap", "Revenues"),
             ("us-gaap", "NetIncomeLoss"),
             ("us-gaap", "ProfitLoss"),
             ("us-gaap", "OperatingIncomeLoss")],
}


def annual_rows(entries):
    """연간(약 350~380일) 관측만 추린다."""
    import datetime as dt
    out = []
    for e in entries:
        s, en = e.get("start"), e.get("end")
        if not s or not en:
            continue
        days = (dt.date.fromisoformat(en) - dt.date.fromisoformat(s)).days
        if 350 <= days <= 380:
            out.append(e)
    out.sort(key=lambda e: (e["end"], e.get("filed") or ""))
    return out


report = {}
for tk, concepts in TARGETS.items():
    fn = os.path.join(RAW, "sec-%s-companyfacts.json" % tk)
    d = json.load(io.open(fn, encoding="utf-8"))
    facts = d["facts"]
    rec = {}
    print("=" * 78)
    print(tk, d.get("entityName"))
    for tax, cname in concepts:
        body = facts.get(tax, {}).get(cname)
        if not body:
            print("  %-45s 없음" % cname)
            continue
        units = body.get("units", {})
        info = {"label": body.get("label"), "units": {}}
        print("  %s" % cname)
        for u, entries in units.items():
            ann = annual_rows(entries)
            # 중복 제거: 같은 (start,end) 는 마지막 제출본만
            seen = {}
            for e in ann:
                seen[(e["start"], e["end"])] = e
            rows = sorted(seen.values(), key=lambda e: e["end"])
            info["units"][u] = [
                {"start": r["start"], "end": r["end"], "val": r["val"],
                 "form": r.get("form"), "fy": r.get("fy"), "filed": r.get("filed")}
                for r in rows[-6:]]
            per = ", ".join("%s(%s)" % (r["end"], r.get("form")) for r in rows[-6:])
            print("     %-5s 연간관측 %2d건  최근: %s" % (u, len(rows), per))
        rec[cname] = info
    report[tk] = rec

io.open(os.path.join(HERE, "usd-coverage.json"), "w", encoding="utf-8").write(
    json.dumps(report, ensure_ascii=False, indent=1))
print("\nsaved usd-coverage.json")
