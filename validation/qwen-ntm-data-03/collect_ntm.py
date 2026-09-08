"""QWEN-NTM-DATA-03 수집기: 대상 상장사의 StockAnalysis 공개 페이지를 받아 evidence.json 을 만든다.

설계 지침 §5.1 의 NTM 계약(다음 4개 미발표 회계분기 EPS 컨센서스)을 공개 무료로 확보할 수 있는지,
그리고 공급사 Forward PE 의 분모 기간이 NTM 인지 FY1 인지 불명인지를 판별하는 것이 목적이다.

제약:
  - 유료 가입·구매·계정 변경 없이 공개 페이지 GET 만 수행한다.
  - worker·원본·C-13 은 읽기·쓰기 모두 하지 않는다. 산출물은 이 폴더에만 쓴다.
  - 주가/PER 역산은 '참고 계산'으로만 기록하고 분모 기간의 증명으로 쓰지 않는다.
"""
import io
import json
import os
import re
import time
from datetime import datetime, timezone

from probe_fetch import get

HERE = os.path.dirname(os.path.abspath(__file__))

# company_id -> (ticker, StockAnalysis slug). companies.json 레지스트리 기준.
# spacex-xai 는 레지스트리에 ticker=None 이지만 실제 Nasdaq SPCX 로 확인되어 슬러그를 사용한다.
TARGETS = [
    ("meta", "META", "meta"),
    ("nvidia", "NVDA", "nvda"),
    ("alphabet", "GOOGL", "googl"),
    ("microsoft", "MSFT", "msft"),
    ("amazon", "AMZN", "amzn"),
    ("apple", "AAPL", "aapl"),
    ("oracle", "ORCL", "orcl"),
    ("palantir", "PLTR", "pltr"),
    ("tesla", "TSLA", "tsla"),
    ("spacex-xai", "SPCX", "spcx"),
]

# 기준선이 2026-09-02 에 기록한 ntm_per / price (원본 HTML VAL 표). 소급 비교용 참조값.
BASELINE = {
    "alibaba": (16.7, 111.76), "meta": (17.9, 592.85), "nvidia": (18.0, 224.41),
    "tsmc": (19.4, 415.50), "alphabet": (25.3, 337.12), "microsoft": (25.4, 496.82),
    "amazon": (27.5, 254.98), "apple": (35.5, 324.96), "oracle": (19.1, 154.04),
    "palantir": (89.0, 169.46), "spacex-xai": (111.0, 140.71), "tesla": (187.5, 357.01),
}

NUM = r"([-+]?\d[\d,]*\.?\d*)"


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def after_label(html, label, window=900):
    """라벨 문자열 뒤 window 안에서 첫 숫자 값을 뽑는다."""
    i = html.find(label)
    if i < 0:
        return None
    seg = html[i + len(label): i + len(label) + window]
    m = re.search(r">\s*" + NUM + r"\s*(?:<|\s)", seg)
    if not m:
        m = re.search(NUM, strip_tags(seg))
    return m.group(1).replace(",", "") if m else None


def to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parse_overview(html):
    out = {}
    out["price"] = to_float(after_label(html, "Stock Price"))
    if out["price"] is None:
        m = re.search(r"\$\s*([\d,]+\.\d\d)", strip_tags(html[:6000]))
        out["price"] = to_float(m.group(1).replace(",", "")) if m else None
    for key, label in [("market_cap", "Market Cap"), ("pe_ratio", "PE Ratio"),
                       ("forward_pe", "Forward PE"), ("eps_ttm", "EPS"),
                       ("shares_out", "Shares Out"), ("revenue_ttm", "Revenue")]:
        out[key] = after_label(html, label)
    m = re.search(r"At close:\s*([^<]{4,40})", html)
    out["price_date_label"] = m.group(1).strip() if m else None
    m = re.search(r"Last updated:\s*</span>\s*<span[^>]*>([^<]+)<", html)
    if not m:
        m = re.search(r"Last updated:?\s*</[^>]+>\s*<[^>]*>([^<]{4,30})<", html)
    out["last_updated"] = m.group(1).strip() if m else None
    m = re.search(r"([A-Z]+):\s*([A-Z.]+)\s*&middot;|NASDAQ:\s*([A-Z.]+)|NYSE:\s*([A-Z.]+)", html)
    out["exchange_hint"] = m.group(0) if m else None
    out["nongaap_note"] = "non-GAAP" in html
    return out


def parse_forecast(html):
    out = {}
    out["eps_this_year"] = to_float(after_label(html, "EPS This Year"))
    out["eps_next_year"] = to_float(after_label(html, "EPS Next Year"))
    out["fy_labels"] = re.findall(r"FY\s*(20\d\d)", html)
    out["upgrade_count"] = len(re.findall(r"Upgrade", html))
    out["nongaap_footnote"] = None
    m = re.search(r"EPS and Forward PE are based on non-GAAP adjusted numbers\.", html)
    if m:
        out["nongaap_footnote"] = m.group(0)
    # 분기 라벨 존재 여부 — §5.1 의 '다음 4개 미발표 회계분기' 확보 가능 판별의 핵심
    out["quarter_labels_Q"] = re.findall(r"\bQ[1-4]\s*20\d\d\b", html)
    out["quarter_labels_mon"] = re.findall(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?20\d\d\b", html)
    out["has_quarterly_toggle"] = ">Quarterly<" in html or "Quarterly</button>" in html
    m = re.search(r"Last updated:\s*</span>\s*<span[^>]*>([^<]+)<", html)
    out["last_updated"] = m.group(1).strip() if m else None
    # 연간 EPS 표 (FY 라벨 옆 값) — Upgrade 가 아닌 실제 값만
    rows = []
    for m in re.finditer(r"FY\s*(20\d\d)", html):
        seg = strip_tags(html[m.end(): m.end() + 300])
        vals = re.findall(r"(Upgrade|Pro|-|" + NUM + r")", seg)
        rows.append({"fy": m.group(1), "first_values": vals[:6]})
    out["fy_rows"] = rows
    # 애널리스트 수
    m = re.search(r"No\.\s*Analysts", html)
    out["has_analyst_count_row"] = bool(m)
    return out


def main():
    evidence = {
        "task": "QWEN-NTM-DATA-03",
        "collected_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reference_date_of_baseline": "2026-09-02",
        "contract": {
            "source": "worker/docs/scorecard/design-guideline.md §5.1",
            "ntm_definition": "NTM EPS = 다음 4개 미발표 회계분기 EPS 컨센서스 합; NTM PER = 주가 / NTM EPS",
            "requirements": [
                "기준 시점에 이용 가능했던 다음 4개 미발표 회계분기 EPS 컨센서스 확보",
                "각 분기의 기간과 추정치 스냅샷 시점 저장",
                "통화·보통주/ADR·분할조정·GAAP/조정 기준 일치, 네 분기 중복 없이 연속",
                "가격은 유효한 양수; EPS 합 0 이하 또는 기준 미확보 시 점수 보류",
                "공급사 필드명 forwardPE 만으로 NTM 인정 금지",
            ],
            "not_satisfied_if": "다음 1분기 예상만 있거나 과거 실적 4개인 경우",
        },
        "sources_policy": "유료 가입·구매·계정 변경 없이 공개 페이지 GET 만 사용",
        "companies": [],
    }

    for cid, ticker, slug in TARGETS:
        rec = {
            "company_id": cid,
            "ticker_used": ticker,
            "registry_ticker": None if cid == "spacex-xai" else ticker,
            "baseline_ntm_per_2026_09_02": BASELINE.get(cid, (None, None))[0],
            "baseline_price_2026_09_02": BASELINE.get(cid, (None, None))[1],
            "fetches": [],
        }
        for kind, url in [
            ("overview", "https://stockanalysis.com/stocks/%s/" % slug),
            ("forecast", "https://stockanalysis.com/stocks/%s/forecast/" % slug),
            ("statistics", "https://stockanalysis.com/stocks/%s/statistics/" % slug),
        ]:
            try:
                r = get(url)
                parsed = (parse_overview(r["text"]) if kind == "overview"
                          else parse_forecast(r["text"]) if kind == "forecast"
                          else parse_overview(r["text"]))
                rec[kind] = parsed
                rec["fetches"].append({
                    "url": url, "final_url": r["final_url"], "status": r["status"],
                    "bytes": r["bytes"], "content_type": r["ctype"],
                    "fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "elapsed_s": r["elapsed"],
                })
                if kind == "forecast":
                    with io.open(os.path.join(HERE, "raw-%s-forecast.html" % cid), "w",
                                 encoding="utf-8") as f:
                        f.write(r["text"])
                if kind == "overview":
                    with io.open(os.path.join(HERE, "raw-%s-overview.html" % cid), "w",
                                 encoding="utf-8") as f:
                        f.write(r["text"])
            except Exception as exc:
                rec[kind] = {"error": "%s: %s" % (type(exc).__name__, exc)}
                rec["fetches"].append({"url": url, "status": "ERROR",
                                       "error": "%s: %s" % (type(exc).__name__, exc),
                                       "fetched_at_utc": datetime.now(timezone.utc).strftime(
                                           "%Y-%m-%dT%H:%M:%SZ")})
            time.sleep(1.0)

        # 참고 계산 — 분모 기간의 증명으로 쓰지 않는다
        ov, fc = rec.get("overview") or {}, rec.get("forecast") or {}
        price = to_float(ov.get("price"))
        fpe = to_float(ov.get("forward_pe"))
        rec["backcalc"] = {
            "disclaimer": "주가/PER 역산만으로 분모의 기간은 증명되지 않는다(작업 지시·§5.1). 참고 기록일 뿐.",
            "price": price,
            "forward_pe": fpe,
            "implied_denominator_eps": round(price / fpe, 4) if (price and fpe) else None,
            "eps_this_year": fc.get("eps_this_year"),
            "eps_next_year": fc.get("eps_next_year"),
            "pe_if_this_year": round(price / fc["eps_this_year"], 4)
            if (price and fc.get("eps_this_year")) else None,
            "pe_if_next_year": round(price / fc["eps_next_year"], 4)
            if (price and fc.get("eps_next_year")) else None,
            "trailing_check_price_over_eps_ttm": round(price / to_float(ov.get("eps_ttm")), 4)
            if (price and to_float(ov.get("eps_ttm"))) else None,
            "pe_ratio_reported": ov.get("pe_ratio"),
        }
        evidence["companies"].append(rec)
        print("[%s] price=%s fwdPE=%s epsTTM=%s | epsThisYr=%s epsNextYr=%s | Q라벨=%d/%d Upgrade=%d"
              % (cid, price, fpe, ov.get("eps_ttm"), fc.get("eps_this_year"),
                 fc.get("eps_next_year"), len(fc.get("quarter_labels_Q") or []),
                 len(fc.get("quarter_labels_mon") or []), fc.get("upgrade_count")))

    path = os.path.join(HERE, "evidence.json")
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=1)
    print("\n저장: %s" % path)


if __name__ == "__main__":
    main()
