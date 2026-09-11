# F9-DECIDE-20B: F9 게이트 판정에 필요한 입력이 14개사 자료에 실제로 있는지 확인한다.
# 읽기 전용. worker 원자료를 수정하지 않는다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..", "..", "..", "worker", "scorecard")

obs = json.load(io.open(os.path.join(W, "runs", "ai-scorecard-2026-09-baseline",
                                     "observations.json"), encoding="utf-8"))
comp = json.load(io.open(os.path.join(W, "companies.json"), encoding="utf-8"))

items = obs["items"]
companies = comp["companies"] if isinstance(comp, dict) and "companies" in comp else comp
cids = [c["company_id"] if isinstance(c, dict) else c for c in companies]

# F9 계약(design-guideline 6.1~6.4)이 요구하는 입력
G1_NEED = ["operating_margin_ttm", "revenue_ttm", "operating_income_ttm"]
G2_NEED = ["fcf_ttm"]
G3_NEED = ["cash", "runway_years", "undrawn_credit_facility"]
G4_NEED = ["contracted_revenue", "offbalance_B"]
EXTRA = ["net_cash", "credit_rating", "capex_ttm", "net_borrowing_ttm",
         "debt_ebitda", "arr", "quarter_note", "offbalance_note"]

by = {}
for it in items:
    by.setdefault(it["company_id"], {}).setdefault(it["metric"], []).append(it)

print("대상 기업 %d개: %s" % (len(cids), ", ".join(cids)))
print()
hdr = ["company"] + G1_NEED + G2_NEED + G3_NEED + G4_NEED
print("== F9 게이트 필수 입력 보유 현황 (값 또는 '-') ==")
print("%-12s %-22s %-12s %-18s %-9s %-8s %-13s %-24s %-19s %-12s" % tuple(
    ["company", "operating_margin_ttm", "revenue_ttm", "operating_income_ttm",
     "fcf_ttm", "cash", "runway_years", "undrawn_credit_facility",
     "contracted_revenue", "offbalance_B"]))

rows = {}
for cid in cids:
    m = by.get(cid, {})
    r = {}
    for k in hdr[1:]:
        lst = m.get(k)
        if not lst:
            r[k] = None
        else:
            r[k] = lst[0].get("value")
    rows[cid] = r
    def f(k):
        v = r[k]
        return "-" if v is None else (str(v)[:20])
    print("%-12s %-22s %-12s %-18s %-9s %-8s %-13s %-24s %-19s %-12s" % (
        cid, f("operating_margin_ttm"), f("revenue_ttm"), f("operating_income_ttm"),
        f("fcf_ttm"), f("cash"), f("runway_years"), f("undrawn_credit_facility"),
        f("contracted_revenue"), f("offbalance_B")))

print()
print("== 지표별 보유 기업 수 (14개사 기준) ==")
for k in hdr[1:] + EXTRA:
    have = [c for c in cids if by.get(c, {}).get(k)]
    print("  %-26s %2d/%d  %s" % (k, len(have), len(cids),
                                  "" if len(have) == len(cids) else "결측: " + ",".join(
                                      c for c in cids if c not in have)))

io.open(os.path.join(HERE, "f9-input-inventory.json"), "w", encoding="utf-8").write(
    json.dumps({"companies": cids, "rows": rows}, ensure_ascii=False, indent=1))
print("\nsaved f9-input-inventory.json")
