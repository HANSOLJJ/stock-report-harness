# MCAP-36: (1) 표지 HTML 에서 클래스 라벨과 주식수를 짝지어 뽑는다 (2) net_cash 태그를 특정한다.
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import SOURCES, load  # noqa: E402

print("=" * 100)
print("1. 클래스별 발행주식수 (표지 dei, 차원 태깅)")
print("=" * 100)
classes = {}
for p in sorted(glob.glob(os.path.join(HERE, "raw", "cover-*.htm"))):
    cid = os.path.basename(p).split("-")[1]
    html = io.open(p, encoding="utf-8").read()
    scale = 1_000_000 if re.search(r"(?i)shares in Millions", html) else 1
    cur = None
    rows = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", html):
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).replace("\u00a0", " ").strip()
                 for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        if not cells:
            continue
        label = cells[0]
        # 클래스 구분자 행: 값 없이 클래스 이름만 있는 행
        if re.search(r"(?i)class [a-f]|common stock", label) and not re.search(r"(?i)shares outstanding", label):
            cur = label
        if re.search(r"(?i)Entity Common Stock, Shares Outstanding", label):
            num = None
            for c in cells[1:]:
                cc = c.replace(",", "").strip()
                if re.fullmatch(r"\d+(\.\d+)?", cc):
                    num = float(cc) * scale
            if num:
                rows.append({"class_label": cur, "shares": num})
    classes[cid] = {"scale": scale, "rows": rows, "total": sum(r["shares"] for r in rows)}
    print("  %s (단위 배율 %s)" % (cid, "{:,}".format(scale)))
    for r in rows:
        print("     %-46s %18s" % ((r["class_label"] or "(라벨 미상)")[:46], "{:,.0f}".format(r["shares"])))
    print("     %-46s %18s" % ("합계", "{:,.0f}".format(classes[cid]["total"])))
    # 무차원 us-gaap 값과 대조
    d, _, _ = load(cid)
    b = d["facts"].get("us-gaap", {}).get("CommonStockSharesOutstanding")
    if b:
        vals = sorted([(e.get("end"), e.get("val")) for u, es in b["units"].items() for e in es])
        print("     %-46s %18s  (%s, 무차원)" % ("us-gaap:CommonStockSharesOutstanding 최신",
                                               "{:,.0f}".format(vals[-1][1]), vals[-1][0]))
        diff = classes[cid]["total"] - vals[-1][1]
        print("     %-46s %18s  → %s" % ("차이", "{:,.0f}".format(diff),
                                        "합계와 일치(무차원이 전 클래스 합)" if abs(diff) < max(2e6, vals[-1][1] * 0.005)
                                        else "불일치 — 무차원이 전 클래스 합이 아님"))
    print()

print("=" * 100)
print("2. net_cash 성분 태그 — 회사별 존재 여부")
print("=" * 100)
CASH = [("us-gaap", "CashAndCashEquivalentsAtCarryingValue"),
        ("us-gaap", "ShortTermInvestments"),
        ("us-gaap", "MarketableSecuritiesCurrent"),
        ("us-gaap", "OtherShortTermInvestments"),
        ("ifrs-full", "CashAndCashEquivalents"),
        ("ifrs-full", "OtherFinancialAssets")]
DEBT = [("us-gaap", "LongTermDebtNoncurrent"), ("us-gaap", "LongTermDebtCurrent"),
        ("us-gaap", "LongTermDebt"), ("us-gaap", "ShortTermBorrowings"),
        ("us-gaap", "DebtCurrent"), ("us-gaap", "OperatingLeaseLiabilityNoncurrent"),
        ("us-gaap", "FinanceLeaseLiabilityNoncurrent"),
        ("ifrs-full", "Borrowings"), ("ifrs-full", "LeaseLiabilities")]
hdr = "%-12s " + " ".join(["%-5s"] * 6) + "  | " + " ".join(["%-5s"] * 9)
print("%-12s %s | %s" % ("company", " ".join("C%d" % i for i in range(1, 7)),
                         " ".join("D%d" % i for i in range(1, 10))))
netcash = {}
for cid in SOURCES:
    d, _, _ = load(cid)
    f = d["facts"]

    def has(tax, cname):
        b = f.get(tax, {}).get(cname)
        return len([e for u, es in (b.get("units") or {}).items() for e in es]) if b else 0
    c = [has(t, n) for t, n in CASH]
    dd = [has(t, n) for t, n in DEBT]
    netcash[cid] = {"cash": dict(zip(["%s:%s" % x for x in CASH], c)),
                    "debt": dict(zip(["%s:%s" % x for x in DEBT], dd))}
    print("%-12s %s | %s" % (cid, " ".join("%-3d" % x for x in c), " ".join("%-3d" % x for x in dd)))
print()
print("  C1 CashAndCashEquivalentsAtCarryingValue  C2 ShortTermInvestments  C3 MarketableSecuritiesCurrent")
print("  C4 OtherShortTermInvestments  C5 ifrs:CashAndCashEquivalents  C6 ifrs:OtherFinancialAssets")
print("  D1 LongTermDebtNoncurrent D2 LongTermDebtCurrent D3 LongTermDebt D4 ShortTermBorrowings")
print("  D5 DebtCurrent D6 OperatingLeaseLiabilityNoncurrent D7 FinanceLeaseLiabilityNoncurrent")
print("  D8 ifrs:Borrowings D9 ifrs:LeaseLiabilities")

io.open(os.path.join(HERE, "classes-netcash.json"), "w", encoding="utf-8").write(
    json.dumps({"classes": classes, "netcash_tags": netcash}, ensure_ascii=False, indent=1))
print("\nsaved classes-netcash.json")
