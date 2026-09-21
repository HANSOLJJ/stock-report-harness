# MCAP-36: 복수 클래스 회사의 표지(R1.htm)에서 클래스별 발행주식수를 가져온다.
# companyfacts 는 차원(클래스) 사실을 버리므로 표지 렌더링을 직접 읽어야 한다.
import io
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "consensus-source-2026-09-09"))
from fetchlib import get as _get  # noqa: E402

# SEC 는 신원을 밝힌 User-Agent 를 요구한다(allowlist note 의 등재 조건).
# 브라우저 UA 로 www.sec.gov/Archives 를 부르면 403 이 난다.
SEC_UA = {"User-Agent": "stock-report-harness research contact: noreply@example.invalid"}


def get(url, **kw):
    time.sleep(0.2)   # SEC 요청 한도 준수
    kw.setdefault("hdrs", SEC_UA)
    return _get(url, **kw)

RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

CIK = {"meta": "0001326801", "alphabet": "0001652044", "palantir": "0001321655"}


def body(r):
    return r.get("text") or ""


def latest_filing(cik, forms=("10-Q", "10-K")):
    r = get("https://data.sec.gov/submissions/CIK%s.json" % cik)
    d = json.loads(body(r))
    rec = d["filings"]["recent"]
    best = None
    for i, f in enumerate(rec["form"]):
        if f in forms:
            row = {"accn": rec["accessionNumber"][i], "form": f,
                   "filed": rec["filingDate"][i], "report": rec["reportDate"][i]}
            if best is None or row["filed"] > best["filed"]:
                best = row
    return best


out = {}
for cid, cik in CIK.items():
    fl = latest_filing(cik)
    accn = fl["accn"].replace("-", "")
    base = "https://www.sec.gov/Archives/edgar/data/%d/%s" % (int(cik), accn)
    r = get(base + "/FilingSummary.xml")
    fs = body(r)
    # 표지(Cover) 보고서 찾기
    reports = re.findall(r"(?is)<Report[^>]*>(.*?)</Report>", fs)
    cover = None
    for rep in reports:
        name = re.search(r"(?is)<ShortName>(.*?)</ShortName>", rep)
        fname = re.search(r"(?is)<HtmlFileName>(.*?)</HtmlFileName>", rep)
        if name and fname and re.search(r"(?i)cover|document.*entity|entity.*information", name.group(1)):
            cover = (name.group(1).strip(), fname.group(1).strip())
            break
    if not cover:
        out[cid] = {"error": "표지 보고서를 못 찾음", "filing": fl}
        print("%-10s ★ 표지 못 찾음" % cid)
        continue
    rr = get(base + "/" + cover[1])
    html = body(rr)
    io.open(os.path.join(RAW, "cover-%s-%s.htm" % (cid, cover[1])), "w", encoding="utf-8").write(html)
    txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).replace("\u00a0", " ")
    # 행 단위 파싱
    rows = []
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", html):
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).replace("\u00a0", " ").strip()
                 for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        if cells:
            rows.append(cells)
    shares = [r for r in rows if re.search(r"(?i)shares outstanding|entity common stock", " ".join(r))]
    out[cid] = {"filing": fl, "cover_report": cover[0], "cover_file": cover[1],
                "base_url": base, "share_rows": shares,
                "class_headers": [r for r in rows[:6]]}
    print("=" * 96)
    print("%s | %s %s (report %s, filed %s) | %s" % (cid, fl["form"], fl["accn"], fl["report"], fl["filed"], cover[0]))
    for r in rows[:4]:
        print("   머리글:", r[:6])
    for r in shares:
        print("   ★", r[:6])

io.open(os.path.join(HERE, "covers.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved covers.json")
