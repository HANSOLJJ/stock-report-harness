# F6-FX-16: 같은 기간의 현지통화 값과 USD 값에서 내재 환율을 역산해
# 연도별로 서로 다른 환율이 쓰였는지(=각 20-F 가 자기 해 최신연도만 환산했는지)를 판별한다.
import io
import json
import os
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

CASES = [
    ("TSM", "ifrs-full", "Revenue", "TWD"),
    ("TSM", "ifrs-full", "ProfitLoss", "TWD"),
    ("BABA", "us-gaap", "Revenues", "CNY"),
    ("BABA", "us-gaap", "NetIncomeLoss", "CNY"),
]


def annual(entries):
    out = []
    for e in entries:
        s, en = e.get("start"), e.get("end")
        if not s or not en:
            continue
        d = (dt.date.fromisoformat(en) - dt.date.fromisoformat(s)).days
        if 350 <= d <= 380:
            out.append(e)
    return out


report = {}
for tk, tax, cname, loc in CASES:
    d = json.load(io.open(os.path.join(RAW, "sec-%s-companyfacts.json" % tk), encoding="utf-8"))
    units = d["facts"][tax][cname]["units"]
    # (start,end) -> {통화: (val, accn, filed, form)}
    table = {}
    for u in (loc, "USD"):
        for e in annual(units.get(u, [])):
            k = (e["start"], e["end"])
            table.setdefault(k, {})[u] = (e["val"], e.get("accn"), e.get("filed"), e.get("form"))
    rows = []
    for k in sorted(table):
        v = table[k]
        if loc in v and "USD" in v and v["USD"][0]:
            rate = v[loc][0] / v["USD"][0]
            rows.append({
                "period": "%s~%s" % k,
                "local_val": v[loc][0], "usd_val": v["USD"][0],
                "implied_rate_local_per_usd": round(rate, 6),
                "usd_from_accession": v["USD"][1], "usd_filed": v["USD"][2],
                "usd_form": v["USD"][3],
            })
    report["%s/%s" % (tk, cname)] = rows
    print("=" * 82)
    print("%s  %s  (%s per USD)" % (tk, cname, loc))
    for r in rows:
        print("  %-25s %18s %14s  내재환율 %10.4f  출처 %s (%s)" % (
            r["period"], "{:,}".format(r["local_val"]), "{:,}".format(r["usd_val"]),
            r["implied_rate_local_per_usd"], r["usd_from_accession"], r["usd_filed"]))
    if len(rows) >= 2:
        rates = [r["implied_rate_local_per_usd"] for r in rows]
        same = max(rates) - min(rates) < 1e-4
        print("  -> 모든 연도 동일 환율인가: %s (min %.4f / max %.4f)" % (
            "예" if same else "아니오", min(rates), max(rates)))

io.open(os.path.join(HERE, "implied-rates.json"), "w", encoding="utf-8").write(
    json.dumps(report, ensure_ascii=False, indent=1))
print("\nsaved implied-rates.json")
