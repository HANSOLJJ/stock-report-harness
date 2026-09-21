"""QWEN-NTM-DATA-03: 저장된 forecast 원문에서 FY 라벨·EPS 행·Upgrade 장벽을 회사별로 뽑는다.

추가 네트워크 요청 없이 raw-*.html 만 읽는다. 회계연도 라벨이 회사마다 다른지,
다음 회계연도 열이 무료 공개인지 유료 장벽인지 판별하는 것이 목적이다.
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


def rows_of(html, rowlabel):
    """Financial Forecast 표에서 주어진 행 라벨의 셀 값을 순서대로 뽑는다."""
    for m in re.finditer(re.escape(rowlabel), html):
        seg = html[m.end(): m.end() + 1400]
        end = seg.find("</tr>")
        seg = seg[:end] if end > 0 else seg
        cells = [c.strip() for c in strip(seg).split("|") if c.strip()]
        if cells:
            return cells
    return []


out = {}
print("%-12s %-28s %-11s %-30s %s" % ("company", "FY 라벨(페이지 순)", "EPS 행 값", "Next FY(2027) 공개?", "분기라벨"))
for cid in CIDS:
    p = os.path.join(HERE, "raw-%s-forecast.html" % cid)
    if not os.path.isfile(p):
        print("%-12s (원문 없음)" % cid)
        continue
    h = io.open(p, encoding="utf-8").read()
    fys = []
    for y in re.findall(r"FY\s*(20\d\d)", h):
        if y not in fys:
            fys.append(y)
    eps_row = rows_of(h, ">EPS<")
    if not eps_row:
        eps_row = rows_of(h, "EPS")
    q_labels = len(re.findall(r"\bQ[1-4]\s*20\d\d\b", h))
    mon_labels = len(re.findall(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?\d\d\b", h))
    # 2027 열이 Upgrade/Pro 인가
    idx = fys.index("2027") if "2027" in fys else None
    nxt = eps_row[idx] if (idx is not None and idx < len(eps_row)) else None
    out[cid] = dict(fy_labels=fys, eps_row=eps_row[:10], fy2027_eps_cell=nxt,
                    quarter_labels_Q=q_labels, quarter_labels_mon=mon_labels,
                    upgrade_count=len(re.findall(r"Upgrade", h)),
                    nongaap=("EPS and Forward PE are based on non-GAAP adjusted numbers." in h))
    print("%-12s %-28s %-11s %-30s Q=%d Mon=%d" % (
        cid, ",".join(fys), str(eps_row[:6]), repr(nxt), q_labels, mon_labels))

print()
print("=== 상세 ===")
for cid, d in out.items():
    print("\n--- %s ---" % cid)
    print("  FY 라벨      : %s" % d["fy_labels"])
    print("  EPS 행       : %s" % d["eps_row"])
    print("  FY2027 EPS 셀: %r  (Upgrade/Pro 이면 다음 회계연도 무료 공개 아님)" % d["fy2027_eps_cell"])
    print("  분기 라벨    : Q# YYYY = %d건, Mon 'YY = %d건" % (d["quarter_labels_Q"], d["quarter_labels_mon"]))
    print("  Upgrade 표식 : %d건" % d["upgrade_count"])
    print("  non-GAAP 각주: %s" % d["nongaap"])

with io.open(os.path.join(HERE, "fy-labels.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n저장: fy-labels.json")
