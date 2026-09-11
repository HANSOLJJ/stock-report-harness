# MCAP-36 후속: apple·palantir 의 리스 태깅 공백이 부재인지 태깅 체계 차이인지 가른다.
# 고정 후보 목록으로 찾지 않는다 — 체계가 다른 발행사가 0 으로 나온다.
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import load  # noqa: E402

C13 = ("C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/"
       "cash-fcf-35/cash_fcf_35_results.json")
cash13 = {it["company_id"]: it for it in json.load(io.open(C13, encoding="utf-8"))["items"]}

LEASEPAT = re.compile(r"(?i)lease")
DEBTPAT = re.compile(r"(?i)debt|borrow|notespayable|bonds|loans|commercialpaper")


def instants(facts, pat, unit):
    """단위가 맞는 시점(잔고) 사실을 개념별로 모은다. 날짜를 고정하지 않는다."""
    out = {}
    for tax, cs in facts.items():
        for cname, body in cs.items():
            if not pat.search(cname):
                continue
            rows = [(e.get("end"), e.get("val"), e.get("form"), e.get("fp"))
                    for u, es in (body.get("units") or {}).items() if u == unit
                    for e in es if not e.get("start")]
            if rows:
                out["%s:%s" % (tax, cname)] = sorted(rows)
    return out


for cid in ("apple", "palantir"):
    d, _, _ = load(cid)
    f = d["facts"]
    c = cash13[cid]
    on, unit = c["balance_sheet_date"], c["currency"]
    print("=" * 108)
    print("%s | C-13 기준 대차대조표일 %s | 통화 %s" % (cid, on, unit))
    print("=" * 108)
    for label, pat in (("리스", LEASEPAT), ("차입", DEBTPAT)):
        found = instants(f, pat, unit)
        # 잔고성만 남긴다 — 만기 스케줄·ROU 자산은 부채 잔고가 아니다
        bal = {k: v for k, v in found.items()
               if re.search(r"(?i)liability|liabilities|debt|borrow|notespayable|loans|commercialpaper", k)
               and not re.search(r"(?i)PaymentsDue|MaturitiesRepayments|RightOfUse|UndiscountedExcess|"
                                 r"Securities|InstrumentFaceAmount|UnusedBorrowing|Unamortized|"
                                 r"AccumulatedGross|SalesType|NetInvestment", k)}
        print("  [%s] 잔고성 개념 %d개" % (label, len(bal)))
        for k, rows in sorted(bal.items()):
            ends = [r[0] for r in rows]
            at_on = [r for r in rows if r[0] == on]
            forms = sorted({r[2] for r in rows})
            print("     %-58s 총 %-3d 최신 %s  기준일 존재 %-5s  form=%s" % (
                k[:58], len(rows), ends[-1], bool(at_on), ",".join(forms)))
        print()
    # 기준일에 제출된 form 이 무엇인지
    print("  이 기준일(%s)에 잔고를 실은 form 을 역으로 본다" % on)
    seen = {}
    for tax, cs in f.items():
        for cname, body in cs.items():
            for u, es in (body.get("units") or {}).items():
                for e in es:
                    if not e.get("start") and e.get("end") == on:
                        seen[e.get("form")] = seen.get(e.get("form"), 0) + 1
    print("     ", json.dumps(seen, ensure_ascii=False))
    print()
