# MCAP-36: 총차입금 실측과 net_cash 정의 후보 대조. legacy 가 어느 정의였는지 역산한다.
# 개념은 추측하지 않고 discover_debt.py 로 탐색한 실제 태그를 쓴다.
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
LEG = json.load(io.open("C:/Users/noble/orca/workspaces/stock-report-harness/worker/"
                        "scorecard/runs/ai-scorecard-2026-09-baseline/observations.json",
                        encoding="utf-8"))["items"]
legacy = {o["company_id"]: o["value"] for o in LEG if o.get("metric") == "net_cash"}

# 총차입(리스 제외). 그룹 안은 우선순위 fallback, 그룹 간은 합산 — 이중계상을 피한다.
TOTAL_DIRECT = [("us-gaap", "DebtLongtermAndShorttermCombinedAmount"),
                ("us-gaap", "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities")]
LT = [("us-gaap", "LongTermDebtNoncurrent"), ("us-gaap", "LongTermNotesAndLoans"),
      ("us-gaap", "LongTermDebt"), ("us-gaap", "ConvertibleDebtNoncurrent")]
LT2 = [("us-gaap", "LongTermLoansFromBank")]      # BABA 는 전환사채와 은행차입이 별개 줄이다
ST = [("us-gaap", "LongTermDebtCurrent"), ("us-gaap", "DebtCurrent"),
      ("us-gaap", "NotesPayableCurrent"), ("us-gaap", "ShortTermBorrowings")]
CP = [("us-gaap", "CommercialPaper")]
FINLEASE = [("us-gaap", "FinanceLeaseLiability")]
OPLEASE = [("us-gaap", "OperatingLeaseLiability")]
OPLEASE_PARTS = ([("us-gaap", "OperatingLeaseLiabilityNoncurrent")],
                 [("us-gaap", "OperatingLeaseLiabilityCurrent")])
FINLEASE_PARTS = ([("us-gaap", "FinanceLeaseLiabilityNoncurrent")],
                  [("us-gaap", "FinanceLeaseLiabilityCurrent")])


def at(facts, cands, on, unit):
    for tax, cname in cands:
        b = facts.get(tax, {}).get(cname)
        if not b:
            continue
        hits = [e for u, es in (b.get("units") or {}).items() if u == unit
                for e in es if not e.get("start") and e.get("end") == on]
        if hits:
            hits.sort(key=lambda e: e.get("filed") or "")
            return hits[-1]["val"], "%s:%s" % (tax, cname)
    return None, None   # 결측이다. 0 과 구분한다 — 0 으로 접으면 조용히 틀린다.


rows = {}
print("%-12s %-4s %15s %15s %15s | %15s %15s" % (
    "company", "통화", "총차입(리스제외)", "리스부채", "차입+리스", "유동성버퍼", "순수현금"))
print("-" * 116)
for cid in SOURCES:
    d, _, _ = load(cid)
    f = d["facts"]
    c = cash13[cid]
    on, unit = c["balance_sheet_date"], c["currency"]
    direct, dc = at(f, TOTAL_DIRECT, on, unit)
    if direct is not None:
        debt, used = direct, [dc]
    else:
        a, ca = at(f, LT, on, unit)
        a2, ca2 = at(f, LT2, on, unit)
        b_, cb = at(f, ST, on, unit)
        p, cp = at(f, CP, on, unit)
        parts = [a, a2, b_, p]
        debt = sum(x for x in parts if x is not None) if any(x is not None for x in parts) else None
        used = [x for x in (ca, ca2, cb, cp) if x]
    ol, col = at(f, OPLEASE, on, unit)
    if ol is None:
        a1 = at(f, OPLEASE_PARTS[0], on, unit)[0]
        a2_ = at(f, OPLEASE_PARTS[1], on, unit)[0]
        ol = (a1 or 0) + (a2_ or 0) if (a1 is not None or a2_ is not None) else None
    fl, cfl = at(f, FINLEASE, on, unit)
    if fl is None:
        b1 = at(f, FINLEASE_PARTS[0], on, unit)[0]
        b2 = at(f, FINLEASE_PARTS[1], on, unit)[0]
        fl = (b1 or 0) + (b2 or 0) if (b1 is not None or b2 is not None) else None
    lease = None if (ol is None and fl is None) else (ol or 0) + (fl or 0)
    cash = c["cash"]
    # C-13 은 현지통화 회사에 _native 접미를 붙인다. 키 이름만 보고 0 으로 접으면 값이 사라진다.
    pure = cash.get("cash_and_cash_equivalents")
    if pure is None:
        pure = cash.get("cash_and_cash_equivalents_native")
    buf = cash.get("liquid_cash_buffer")
    allsec = cash.get("total_cash_and_all_securities")
    # 현지통화 회사는 C-13 이 버퍼·합계를 USD 로만 준다 → 현지통화 대조 불가로 표시
    buf_native_missing = buf is None
    allsec_native_missing = allsec is None
    rows[cid] = {
        "balance_sheet_date": on, "currency": unit,
        "debt_ex_lease": debt, "debt_concepts": used,
        "operating_lease": ol, "finance_lease": fl, "lease_total": lease,
        "debt_incl_lease": None if (debt is None or lease is None) else debt + lease,
        "cash_pure": pure, "cash_buffer": buf, "cash_all_securities": allsec,
        "cash_buffer_native_missing": buf_native_missing,
        "cash_allsec_native_missing": allsec_native_missing,
        "lease_missing": lease is None, "debt_missing": debt is None,
        "candidates": {
            "A_pure_minus_debt": (pure - debt) if (pure is not None and debt is not None) else None,
            "B_buffer_minus_debt": (buf - debt) if (buf is not None and debt is not None) else None,
            "C_allsec_minus_debt": (allsec - debt) if (allsec is not None and debt is not None) else None,
            "D_allsec_minus_debt_lease": (allsec - debt - lease) if (allsec is not None and debt is not None and lease is not None) else None,
            "E_buffer_no_debt": buf,
        },
        "legacy": legacy.get(cid),
    }
    def fm(x):
        return "결측" if x is None else "{:,.0f}".format(x)
    print("%-12s %-4s %15s %15s %15s | %15s %15s" % (
        cid, unit, fm(debt), fm(lease),
        fm(None if (debt is None or lease is None) else debt + lease), fm(buf), fm(pure)))

print()
print("=" * 116)
print("legacy net_cash 가 어느 정의인가 — USD 회사만(환산 불필요)")
print("=" * 116)
print("%-12s %14s | %13s %13s %13s %13s %13s" % (
    "company", "legacy", "A 순수-차입", "B 버퍼-차입", "C 전체-차입", "D C-리스", "E 버퍼"))
print("-" * 116)
score = {k: 0 for k in ("A_pure_minus_debt", "B_buffer_minus_debt", "C_allsec_minus_debt",
                        "D_allsec_minus_debt_lease", "E_buffer_no_debt")}
for cid, r in rows.items():
    if r["currency"] != "USD" or r["legacy"] is None:
        continue
    cand = r["candidates"]
    best = None
    line = []
    for k in score:
        v = cand[k]
        if v is None:
            line.append(None); continue
        d = abs(v - r["legacy"])
        line.append(v / 1e9)
        if best is None or d < best[1]:
            best = (k, d)
    if best is None:
        print("%-12s %14s | 후보 전부 산출 불가" % (cid, "{:,.1f}B".format(r["legacy"] / 1e9)))
        continue
    if best[1] <= max(abs(r["legacy"]) * 0.01, 2e8):
        score[best[0]] += 1
    print("%-12s %14s | %13s %13s %13s %13s %13s   ← %s" % (
        cid, "{:,.1f}B".format(r["legacy"] / 1e9),
        *[("—" if x is None else "{:,.1f}".format(x)) for x in line], best[0].split("_")[0]))
print()
print("정의별 적중(오차 5% 또는 $1B 이내):", json.dumps(score, ensure_ascii=False))

io.open(os.path.join(HERE, "netcash-final.json"), "w", encoding="utf-8").write(
    json.dumps(rows, ensure_ascii=False, indent=1))
print("\nsaved netcash-final.json")
