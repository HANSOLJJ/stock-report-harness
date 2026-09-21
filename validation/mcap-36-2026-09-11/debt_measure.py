# MCAP-36: 12개사 총차입금을 SEC 원자료에서 실측하고 net_cash 정의 후보를 대조한다.
# cash 성분은 C-13 CASH-FCF-35(커밋 4074894)를 쓴다(설계진행 지시). 중복 조사하지 않는다.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import SOURCES, load  # noqa: E402

C13 = ("C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/"
       "cash-fcf-35/cash_fcf_35_results.json")
cash13 = {it["company_id"]: it for it in json.load(io.open(C13, encoding="utf-8"))["items"]}

# 차입금 후보. 기간별 Coalesce 로 풀되 '겹치지 않는 합' 이 되도록 그룹을 나눈다.
# 그룹 안에서는 우선순위 fallback, 그룹 사이에서는 더한다.
DEBT_GROUPS = {
    "long_term": [("us-gaap", "LongTermDebtNoncurrent"),
                  ("us-gaap", "LongTermDebtAndCapitalLeaseObligations"),
                  ("ifrs-full", "NoncurrentPortionOfNoncurrentBondsIssued")],
    "short_term": [("us-gaap", "LongTermDebtCurrent"),
                   ("us-gaap", "DebtCurrent"),
                   ("us-gaap", "ShortTermBorrowings"),
                   ("ifrs-full", "CurrentPortionOfNoncurrentBondsIssued")],
    "commercial_paper": [("us-gaap", "CommercialPaper")],
}
LEASE_GROUPS = {
    "lease_nc": [("us-gaap", "OperatingLeaseLiabilityNoncurrent"),
                 ("ifrs-full", "LeaseLiabilities")],
    "lease_c": [("us-gaap", "OperatingLeaseLiabilityCurrent")],
    "finlease_nc": [("us-gaap", "FinanceLeaseLiabilityNoncurrent")],
    "finlease_c": [("us-gaap", "FinanceLeaseLiabilityCurrent")],
}


def instant_at(facts, cands, on, unit):
    """시점(instant) 사실 중 기준 대차대조표일과 같은 날짜의 값. 개념 우선순위 fallback."""
    for tax, cname in cands:
        b = facts.get(tax, {}).get(cname)
        if not b:
            continue
        hits = []
        for u, es in (b.get("units") or {}).items():
            if u != unit:
                continue
            for e in es:
                if e.get("start"):      # 기간 사실은 잔고가 아니다
                    continue
                if e.get("end") == on:
                    hits.append(e)
        if hits:
            hits.sort(key=lambda e: e.get("filed") or "")
            return {"val": hits[-1]["val"], "concept": "%s:%s" % (tax, cname),
                    "form": hits[-1].get("form"), "filed": hits[-1].get("filed")}
    return None


out = {}
print("%-12s %-12s %-4s %16s %16s %16s %16s" % (
    "company", "기준일", "통화", "장기차입", "단기차입", "CP", "총차입(리스제외)"))
print("-" * 116)
for cid in SOURCES:
    d, _, _ = load(cid)
    facts = d["facts"]
    c13 = cash13.get(cid)
    if not c13:
        print("%-12s C-13 cash 자료 없음" % cid)
        continue
    on = c13["balance_sheet_date"]
    unit = c13["currency"]
    rec = {"balance_sheet_date": on, "currency": unit, "components": {}, "missing": []}
    for g, cands in list(DEBT_GROUPS.items()) + list(LEASE_GROUPS.items()):
        r = instant_at(facts, cands, on, unit)
        if r:
            rec["components"][g] = r
        else:
            rec["missing"].append(g)
    dv = {g: rec["components"].get(g, {}).get("val", 0) for g in DEBT_GROUPS}
    lv = {g: rec["components"].get(g, {}).get("val", 0) for g in LEASE_GROUPS}
    rec["debt_ex_lease"] = sum(dv.values())
    rec["lease_total"] = sum(lv.values())
    rec["debt_incl_lease"] = rec["debt_ex_lease"] + rec["lease_total"]
    rec["cash_c13"] = {k: c13["cash"].get(k) for k in
                       ("cash_and_cash_equivalents", "short_term_marketable_securities",
                        "liquid_cash_buffer", "noncurrent_marketable_securities",
                        "total_cash_and_all_securities", "restricted_cash")}
    out[cid] = rec
    print("%-12s %-12s %-4s %16s %16s %16s %16s" % (
        cid, on, unit,
        "{:,.0f}".format(dv["long_term"]), "{:,.0f}".format(dv["short_term"]),
        "{:,.0f}".format(dv["commercial_paper"]), "{:,.0f}".format(rec["debt_ex_lease"])))

io.open(os.path.join(HERE, "debt-measure.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved debt-measure.json")
