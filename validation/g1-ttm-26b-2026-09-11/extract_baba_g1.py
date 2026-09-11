# G1-TTM-26B: BABA 의 FY2026 연간 영업손익·매출을 보존된 SEC companyfacts 에서 복원한다.
# 밖에서 찾기 전에 손에 있는 스냅샷부터 연다. 분기 행 부재는 전제하지 않고 직접 센다.
import datetime as dt
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# 내 워크트리에 F6-FX-16 에서 받아 둔 스냅샷
MINE = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw", "sec-BABA-companyfacts.json")

d = json.load(io.open(MINE, encoding="utf-8"))
print("출처 파일: %s" % os.path.relpath(MINE, HERE))
print("entityName=%s  cik=%s" % (d.get("entityName"), d.get("cik")))
facts = d["facts"]

print()
print("=" * 88)
print("A. taxonomy 확인 (전제하지 않고 직접 센다)")
print("=" * 88)
for tax, concepts in facts.items():
    units = {}
    for c, body in concepts.items():
        for u in (body.get("units") or {}):
            units[u] = units.get(u, 0) + 1
    print("  %-12s 개념 %4d  단위 %s" % (tax, len(concepts), units))

TARGETS = [("Revenues", "매출"), ("OperatingIncomeLoss", "영업손익"),
           ("CostOfRevenue", "매출원가"), ("GrossProfit", "매출총이익")]


def rows(tax, cname, unit):
    body = facts.get(tax, {}).get(cname)
    if not body:
        return []
    out = []
    for e in (body.get("units") or {}).get(unit, []):
        s, en = e.get("start"), e.get("end")
        if not s or not en:
            continue
        days = (dt.date.fromisoformat(en) - dt.date.fromisoformat(s)).days
        out.append({"start": s, "end": en, "days": days, "val": e.get("val"),
                    "fy": e.get("fy"), "fp": e.get("fp"), "form": e.get("form"),
                    "filed": e.get("filed"), "accn": e.get("accn"), "frame": e.get("frame")})
    return out


print()
print("=" * 88)
print("B. 기간 길이 분포 — 분기 행이 실제로 0건인가")
print("=" * 88)
summary = {}
for cname, label in TARGETS:
    for unit in ("CNY", "USD"):
        rs = rows("us-gaap", cname, unit)
        if not rs:
            continue
        buckets = {}
        for r in rs:
            k = ("분기(80~100일)" if 80 <= r["days"] <= 100 else
                 "반기(170~190일)" if 170 <= r["days"] <= 190 else
                 "9개월(265~285일)" if 265 <= r["days"] <= 285 else
                 "연간(350~380일)" if 350 <= r["days"] <= 380 else
                 "기타(%d일)" % r["days"])
            buckets[k] = buckets.get(k, 0) + 1
        print("  %-22s %-4s  %s" % (cname, unit, json.dumps(buckets, ensure_ascii=False)))
        summary.setdefault(cname, {})[unit] = buckets

print()
print("=" * 88)
print("C. FY2026 (2025-04-01 ~ 2026-03-31) 연간 값")
print("=" * 88)
found = {}
for cname, label in TARGETS:
    for unit in ("CNY", "USD"):
        rs = [r for r in rows("us-gaap", cname, unit)
              if 350 <= r["days"] <= 380 and r["end"] == "2026-03-31"]
        # 같은 기간 중복은 최신 제출본
        rs.sort(key=lambda r: r["filed"])
        if not rs:
            print("  %-22s %-4s  없음" % (cname, unit))
            continue
        r = rs[-1]
        found.setdefault(cname, {})[unit] = r
        print("  %-22s %-4s  %s ~ %s (%d일)  val=%s  form=%s filed=%s accn=%s"
              % (cname, unit, r["start"], r["end"], r["days"],
                 "{:,}".format(r["val"]), r["form"], r["filed"], r["accn"]))

print()
print("=" * 88)
print("D. 영업이익률 계산 — 통화별로 따로 계산해 환율 약분을 실증한다")
print("=" * 88)
res = {}
for unit in ("CNY", "USD"):
    rev = (found.get("Revenues") or {}).get(unit)
    op = (found.get("OperatingIncomeLoss") or {}).get(unit)
    if not rev or not op:
        print("  %-4s 계산 불가 (매출 %s / 영업손익 %s)" % (
            unit, "있음" if rev else "없음", "있음" if op else "없음"))
        continue
    if rev["start"] != op["start"] or rev["end"] != op["end"]:
        print("  %-4s 기간 불일치 — 계산하지 않음" % unit)
        continue
    m = op["val"] / rev["val"]
    res[unit] = {"revenue": rev["val"], "operating_income": op["val"],
                 "operating_margin": m, "period": "%s~%s" % (rev["start"], rev["end"]),
                 "accn_revenue": rev["accn"], "accn_operating": op["accn"]}
    print("  %-4s 매출 %18s  영업손익 %16s  영업이익률 %.6f  (%.4f%%)"
          % (unit, "{:,}".format(rev["val"]), "{:,}".format(op["val"]), m, m * 100))

if "CNY" in res and "USD" in res:
    diff = abs(res["CNY"]["operating_margin"] - res["USD"]["operating_margin"])
    print()
    print("  두 통화 영업이익률 차이 = %.10f" % diff)
    print("  → 환율 약분 실증: %s" % ("일치(차이 1e-6 미만)" if diff < 1e-6 else "불일치"))
    if res["USD"]["revenue"]:
        print("  내재환율(매출 기준) = %.4f" % (res["CNY"]["revenue"] / res["USD"]["revenue"]))

io.open(os.path.join(HERE, "baba-g1-extract.json"), "w", encoding="utf-8").write(
    json.dumps({"source_file": "validation/f6-fx-16-2026-09-10/raw/sec-BABA-companyfacts.json",
                "entity": d.get("entityName"), "cik": d.get("cik"),
                "period_length_buckets": summary, "fy2026": found, "margins": res},
               ensure_ascii=False, indent=1, default=str))
print("\nsaved baba-g1-extract.json")
