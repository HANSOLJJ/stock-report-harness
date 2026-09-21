"""[폐기됨 — QWEN-NTM-DATA-03-R1] 이 스크립트의 출력은 어떤 결론에도 쓰지 않는다.

폐기 사유 (재검토 요청 msg_2463526bb807 및 자체 검증):
  1. 'Current Qtr. = 회계연도 1분기' 라는 가정을 전사에 일반화했다. 이 가정은 성립하지 않는다.
     역년 회사에서 2026-09 는 회계연도 3분기이며, 비역년 회사(nvidia 의 Oct 2026) 도 마찬가지다.
     재검토 요청이 명시적으로 'Current Qtr=FY Q1 일반화 금지, 공식 회계기간/발표일을 사용' 하라고 지적했다.
  2. 자체 검증에서 결함이 드러났다 — 10건 중 3건만 Yahoo 연도 라벨과 일치했고,
     nvidia 는 유도값 2027-07-31 이 실제 말일 2027-01-31 과 다른데도 연도(2027) 만 우연히 일치해
     오탐(OK) 으로 표시됐다. 7건은 MISMATCH.
  3. 이 스크립트가 계산한 '회계연도 말일까지의 남은 개월수' 는 설계 지침 §5.1 의 요건
     ('다음 4개 미발표 회계분기') 과 다른 척도이므로 비NTM 증명이 될 수 없다.

대체물: apply_r1_corrections.py → fy-analysis-corrected.json (공식 회계기간·발표일만 사용).
감사 추적을 위해 파일과 fy-end-derived.json 은 삭제하지 않고 보존한다.

원래 목적: QWEN-NTM-DATA-03: Yahoo 의 분기 종료월 라벨과 연도 라벨로 회계연도 말일을 직접 유도한다.

기존 analyze_fy.py 는 microsoft 의 회계연도 말일을 'FY 라벨이 2029 까지 확장되는 구조' 라는
간접 근거로 판별해 보고서 §9-6 에서 그 약점을 밝힌 바 있다. 이 스크립트는 Yahoo 가 실제로
반환한 열 라벨만으로 말일을 유도해 그 간접 근거를 직접 근거로 대체한다.

유도 논리:
  Yahoo 는 분기 열을 '분기 종료월' 로 라벨링한다 (예: Current Qtr. (Sep 2026)).
  Current Qtr. 와 Next Qtr. 는 연속 분기이므로, 이 둘이 속한 회계연도의 4개 분기 종료월은
  Current Qtr. 부터 3개 분기 뒤까지다. 회계연도 말일 = Current Qtr. 종료월 + 9개월의 월말.
  그 회계연도의 라벨 연도가 Yahoo 의 'Current Year (YYYY)' 와 일치하면 유도가 검증된다.
"""
import io
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
yh = json.load(io.open(os.path.join(HERE, "evidence-yahoo.json"), encoding="utf-8"))

MON = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
PRICE_DATE = date(2026, 9, 4)


def month_end(y, m):
    if m == 12:
        return date(y, 12, 31)
    return date(y, m + 1, 1).replace(day=1) - __import__("datetime").timedelta(days=1)


def parse_period(s):
    """'Sep 2026' -> (2026, 9) / 'Oct 2026' -> (2026, 10)"""
    parts = s.strip().split()
    if len(parts) != 2:
        return None
    mon = MON.get(parts[0][:3])
    if not mon:
        return None
    try:
        return int(parts[1]), mon
    except ValueError:
        return None


rows = []
print("%-12s %-16s %-16s %-10s %-10s %-12s %8s %s" % (
    "company", "CurrentQtr", "NextQtr", "CurrYear", "NextYear", "유도 FY말일", "개월", "연도검증"))
for rec in yh["companies"]:
    cid = rec["company_id"]
    p = rec.get("parsed") or {}
    qp = p.get("quarter_periods") or []
    yp = p.get("year_periods") or []
    if len(qp) < 2 or len(yp) < 1:
        print("%-12s 라벨 부족 %s / %s" % (cid, qp, yp))
        continue
    cq = parse_period(qp[0])
    nq = parse_period(qp[1])
    if not cq or not nq:
        print("%-12s 라벨 파싱 실패 %s" % (cid, qp))
        continue
    cy, cm = cq
    ny, nm = nq
    # 연속 분기 검증
    consecutive = ((ny - cy) * 12 + (nm - cm)) == 3
    # 회계연도 말일 = Current Qtr. 종료월 + 9개월 (Q1 이 Current Qtr. 인 경우)
    fy_end_y = cy + (cm + 9 - 1) // 12
    fy_end_m = (cm + 9 - 1) % 12 + 1
    fy_end = month_end(fy_end_y, fy_end_m)
    fy_label_year = fy_end_y if fy_end_m == 12 else fy_end_y
    yahoo_cy = yp[0].strip()
    # Yahoo 는 회계연도 말일이 속한 해를 라벨로 쓴다
    label_match = str(fy_end.year) == yahoo_cy
    months = (fy_end - PRICE_DATE).days / 30.4375
    rows.append(dict(company_id=cid, current_qtr=qp[0], next_qtr=qp[1],
                     current_year_label=yahoo_cy, next_year_label=(yp[1].strip() if len(yp) > 1 else None),
                     quarters_consecutive=consecutive,
                     derived_fy_end=fy_end.isoformat(),
                     derived_fy_end_matches_yahoo_year_label=label_match,
                     months_price_date_to_fy_end=round(months, 2),
                     fy_shorter_than_12m=months < 11.5))
    print("%-12s %-16s %-16s %-10s %-10s %-12s %8.2f %s" % (
        cid, qp[0], qp[1], yp[0], (yp[1] if len(yp) > 1 else "-"),
        fy_end.isoformat(), months,
        "OK" if label_match else ("MISMATCH(라벨 %s)" % yahoo_cy)))

print()
print("=== 유도 결과 검증 ===")
ok = [r for r in rows if r["derived_fy_end_matches_yahoo_year_label"]]
bad = [r for r in rows if not r["derived_fy_end_matches_yahoo_year_label"]]
print("  Yahoo 연도 라벨과 일치: %d / %d" % (len(ok), len(rows)))
print("  불일치: %s" % ([r["company_id"] for r in bad] or "없음"))
print("  분기 연속성 검증 통과: %d / %d" % (len([r for r in rows if r["quarters_consecutive"]]), len(rows)))
print("  회계연도 말일이 12개월 미만: %d / %d  → %s" % (
    len([r for r in rows if r["fy_shorter_than_12m"]]), len(rows),
    [r["company_id"] for r in rows if r["fy_shorter_than_12m"]]))

print()
print("=== 기존 analyze_fy.py 의 가정과 대조 ===")
fa = json.load(io.open(os.path.join(HERE, "fy-analysis.json"), encoding="utf-8"))
for r in rows:
    prev = (fa["companies"].get(r["company_id"]) or {}).get("fy_end")
    same = prev == r["derived_fy_end"]
    print("  %-12s 이전가정=%-12s 신규유도=%-12s %s" % (
        r["company_id"], prev, r["derived_fy_end"], "일치" if same else "차이 → 신규 유도 채택"))

with io.open(os.path.join(HERE, "fy-end-derived.json"), "w", encoding="utf-8") as f:
    json.dump({"price_date": PRICE_DATE.isoformat(),
               "derivation": "Yahoo 분기 종료월 라벨 Current Qtr. + 9개월 = 회계연도 말일. "
                             "Yahoo 'Current Year (YYYY)' 라벨 연도와 일치하는지 검증.",
               "companies": rows}, f, ensure_ascii=False, indent=1)
print("\n저장: fy-end-derived.json")
