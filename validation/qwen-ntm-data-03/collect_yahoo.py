"""QWEN-NTM-DATA-03 Yahoo 수집기: 향후 분기 EPS 컨센서스가 몇 개 분기까지 무료 공개되는지 확정한다.

설계 지침 §5.1 은 '다음 4개 미발표 회계분기 EPS 컨센서스' 를 요구한다.
Yahoo Finance analysis 페이지가 공개 무료로 몇 개 분기를 주는지 전 대상에 대해 동일 조건으로 측정한다.

제약: 유료 가입·구매·계정 변경 없음. 공개 페이지 GET 만. 산출물은 이 폴더에만 기록.
"""
import io
import json
import os
import re
import time
from datetime import datetime, timezone

from probe_fetch import get

HERE = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    ("meta", "META"), ("nvidia", "NVDA"), ("alphabet", "GOOGL"),
    ("microsoft", "MSFT"), ("amazon", "AMZN"), ("apple", "AAPL"),
    ("oracle", "ORCL"), ("palantir", "PLTR"), ("tesla", "TSLA"),
    ("spacex-xai", "SPCX"),
]

MONTHS = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", s))


def parse_yahoo(html):
    """Earnings Estimate 표의 열 라벨과 Avg. Estimate 행을 뽑는다."""
    out = {}
    # 열 라벨: Current Qtr. (Sep 2026) 형태
    cols = re.findall(r"(Current Qtr\.|Next Qtr\.|Current Year|Next Year)\s*\(([^)]{3,20})\)", html)
    seen = []
    for name, period in cols:
        key = "%s (%s)" % (name.strip(), period.strip())
        if key not in seen:
            seen.append(key)
    out["columns"] = seen
    out["n_forward_quarters"] = len([c for c in seen if "Qtr." in c])
    out["n_forward_years"] = len([c for c in seen if "Year" in c])

    # 월/년 라벨의 실제 분기 기간 (회계연도 판별용)
    out["quarter_periods"] = [p.strip() for n, p in cols if "Qtr." in n][:4]
    out["year_periods"] = [p.strip() for n, p in cols if "Year" in n][:4]

    # Avg. Estimate 행
    avg = None
    for m in re.finditer(r"Avg\.\s*Estimate", html):
        seg = html[m.end(): m.end() + 1500]
        end = seg.find("</tr>")
        seg = seg[:end] if end > 0 else seg
        cells = [c.strip() for c in strip(seg).split("|") if c.strip()]
        nums = [c for c in cells if re.fullmatch(r"-?[\d,]*\.?\d+", c.replace(",", ""))]
        if nums:
            avg = nums[:6]
            break
    out["avg_estimate_row"] = avg

    # No. of Analysts 행
    na = None
    for m in re.finditer(r"No\.\s*of\s*Analysts", html):
        seg = html[m.end(): m.end() + 1200]
        end = seg.find("</tr>")
        seg = seg[:end] if end > 0 else seg
        cells = [c.strip() for c in strip(seg).split("|") if c.strip()]
        nums = [c for c in cells if re.fullmatch(r"\d+", c)]
        if nums:
            na = nums[:6]
            break
    out["no_of_analysts_row"] = na

    # Currency in USD 표기
    m = re.search(r"Currency in ([A-Z]{3})", html)
    out["currency_note"] = m.group(0) if m else None

    # GAAP / Normalized 토글
    out["has_gaap_toggle"] = bool(re.search(r"gaap|Normalized", html, re.I))

    # Earnings History 기간말 (회계연도 종료월 판별)
    ends = re.findall(r"\b(\d{1,2}/\d{1,2}/20\d\d)\b", html)
    uniq = []
    for e in ends:
        if e not in uniq:
            uniq.append(e)
    out["period_end_dates_seen"] = uniq[:12]

    # 오류 페이지 여부
    out["error_page"] = bool(re.search(r"Oops, something went wrong", html))
    out["has_earnings_estimate"] = bool(re.search(r"Earnings Estimate", html))
    return out


def main():
    res = {"collected_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "source": "Yahoo Finance /quote/<T>/analysis/",
           "purpose": "§5.1 이 요구하는 '다음 4개 미발표 회계분기 EPS 컨센서스' 가 "
                      "공개 무료로 몇 개 분기까지 확보되는지 전 대상 동일 조건 측정",
           "companies": []}
    for cid, t in TARGETS:
        url = "https://finance.yahoo.com/quote/%s/analysis/" % t
        rec = {"company_id": cid, "ticker": t, "url": url}
        try:
            r = get(url, timeout=45)
            rec.update({"status": r["status"], "bytes": r["bytes"], "final_url": r["final_url"],
                        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
            with io.open(os.path.join(HERE, "raw-yahoo-%s.html" % cid), "w", encoding="utf-8") as f:
                f.write(r["text"])
            rec["parsed"] = parse_yahoo(r["text"])
        except Exception as exc:
            rec.update({"status": "ERROR", "error": "%s: %s" % (type(exc).__name__, exc),
                        "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
        res["companies"].append(rec)
        p = rec.get("parsed") or {}
        print("%-12s st=%-5s fwdQ=%s fwdY=%s cols=%s avg=%s analysts=%s err=%s" % (
            cid, rec.get("status"), p.get("n_forward_quarters"), p.get("n_forward_years"),
            p.get("columns"), p.get("avg_estimate_row"), p.get("no_of_analysts_row"),
            p.get("error_page")))
        time.sleep(1.2)

    with io.open(os.path.join(HERE, "evidence-yahoo.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("\n저장: evidence-yahoo.json")
    print("\n=== 분기 기간 라벨(회계연도 판별) ===")
    for rec in res["companies"]:
        p = rec.get("parsed") or {}
        if p.get("quarter_periods") or p.get("year_periods"):
            print("  %-12s quarters=%-28s years=%-18s currency=%s" % (
                rec["company_id"], p.get("quarter_periods"), p.get("year_periods"),
                p.get("currency_note")))


if __name__ == "__main__":
    main()
