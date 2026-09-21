"""[실행하지 않고 폐기 — QWEN-NTM-DATA-03-R1] 이 스크립트는 한 번도 실행되지 않았다.

폐기 사유: 재검토 요청 msg_2463526bb807 이 '회계연도 추론 범위를 늘리지 말고 공식 근거와
요청한 오류 정정에 한정하라' 고 지정했고, 'Current Qtr=FY Q1 일반화 금지, 공식 회계기간/발표일을
사용하세요' 라고 명시했다. 이 스크립트는 StockAnalysis 의 'Period End' 행에서 회계연도 말일을
추론하려는 것이므로 그 지시에 반한다.

대체물: 공식 근거만 사용한다 —
  microsoft : https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast
              (FY26 Q4, 발표 2026-07-29, 회계기간말 2026-06-30) — 내가 직접 HTTP 200 확인
  oracle    : Oracle IR FY27Q1 발표일 공지 (2026-09-10) — 재검토 요청자의 공식 근거 인용 채택.
              내 접근은 403 Forbidden 이었음을 밝힌다. Yahoo Earnings History 기간말
              8/31/2025·11/30/2025·2/28/2026·5/31/2026 으로 회계연도 5월 말 종료를 독립 확인.
  spacex-xai: https://www.nasdaq.com/newsroom/spacex-ipo-rocket-company-launches-historic-ipo
              (SPCX, Nasdaq + Nasdaq Texas, 거래개시 2026-06-12) — 내가 직접 HTTP 200 확인

감사 추적을 위해 파일은 삭제하지 않고 보존한다.

probe_fyend_direct.py 가 'Period End' 라벨의 존재만 확인했으므로, 그 라벨이 속한 표 행의
셀 값을 순서대로 추출한다. 값이 있으면 FY 라벨(FY 2026 등) 과 열이 대응되어
회사별 회계연도 말일이 직접 증거로 확정된다.
"""
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CIDS = ["meta", "nvidia", "alphabet", "microsoft", "amazon",
        "apple", "oracle", "palantir", "tesla", "spacex-xai"]


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", s))


out = {}
for cid in CIDS:
    p = os.path.join(HERE, "raw-%s-forecast.html" % cid)
    if not os.path.isfile(p):
        continue
    h = io.open(p, encoding="utf-8").read()
    # FY 라벨 순서 (표 열 순서)
    fys = []
    for y in re.findall(r"FY\s*(20\d\d)", h):
        if y not in fys:
            fys.append(y)
    # 'Period End' 가 속한 행의 셀
    cells = None
    for m in re.finditer(r"Period End", h):
        seg = h[m.end(): m.end() + 2000]
        end = seg.find("</tr>")
        seg = seg[:end] if end > 0 else seg[:600]
        raw = [c.strip() for c in strip(seg).split("|") if c.strip()]
        # HTML 조각·클래스명 제거: 날짜/월 라벨 형태만 남긴다
        clean = [c for c in raw if re.fullmatch(
            r"[A-Z][a-z]{2}\s+'?\d\d(?:\s*'?\d\d)?|\d{1,2}/\d{1,2}/20\d\d|20\d\d|Upgrade|Pro|-|—", c)]
        if clean:
            cells = clean
            break
    out[cid] = {"fy_labels": fys, "period_end_row": cells}
    print("%-12s FY=%-34s PeriodEnd=%s" % (cid, ",".join(fys), cells))

print()
print("=== FY 라벨과 Period End 대응 ===")
for cid, d in out.items():
    fy, pe = d["fy_labels"], d["period_end_row"]
    if not pe:
        print("  %-12s Period End 값 추출 실패 → 간접 근거 유지" % cid)
        continue
    if len(pe) == len(fy):
        pairs = list(zip(fy, pe))
        print("  %-12s %s" % (cid, "  ".join("FY%s=%s" % (a, b) for a, b in pairs)))
    else:
        print("  %-12s 열 수 불일치 FY=%d PeriodEnd=%d → %s / %s"
              % (cid, len(fy), len(pe), fy, pe))

with io.open(os.path.join(HERE, "fy-period-end.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n저장: fy-period-end.json")
