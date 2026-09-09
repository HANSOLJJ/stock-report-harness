# evidence.json 에서 REPORT.md 본문에 넣을 표를 생성한다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ev = json.load(io.open(os.path.join(HERE, "evidence.json"), encoding="utf-8"))

L = []

L.append("### 표 A. 담당 10개사 다음 4개 미발표 회계분기 EPS 컨센서스 (원천: Nasdaq API 단일 원천)\n")
L.append("| 기업 | 티커 | 분기(공급사 라벨) | 분기말(대조) | 평균 | 최소 | 최대 | 중간값 | 전망치 수 | 4주 상향/하향 |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for c in ev["companies"]:
    nq = c["sources"]["nasdaq_api"]
    for i, o in enumerate(nq["observations"]):
        L.append("| %s | %s | %s | %s | %s | %s | %s | 미제공 | %s | %s/%s |" % (
            c["company_id"] if i == 0 else "", c["ticker"] if i == 0 else "",
            o["period_label_vendor"], o["period_end_stockanalysis"] or "미확보",
            o["mean"], o["min"], o["max"], o["estimate_count"],
            o["revisions_up_4w"], o["revisions_down_4w"]))

L.append("\n### 표 B. 확보 현황과 채점 사용 가능 여부\n")
L.append("| 기업 | 상장 확인 | 마지막 발표 분기 | 4분기 평균 확보 | 최소/최대/표본수 | 중간값 | 평균 4분기 합 | 2원천 커버 | 2원천 합치 | 채점 사용 |")
L.append("|---|---|---|---|---|---|---|---|---|---|")
for c in ev["companies"]:
    nq = c["sources"]["nasdaq_api"]
    a = c["acquisition"]
    rb = c["reported_boundary"]
    L.append("| %s | %s %s | %s (실적 %s) | %s | %s | 미확보 | %s | %d/4 | %d/4 | 불가(미검증) |" % (
        c["company_id"], c["listing"]["exchange"], c["listing"]["last_sale_price"],
        rb["last_reported_quarter_vendor_label"], rb["last_reported_actual_eps"],
        a["next_4_quarter_eps_mean"], a["min_max_count"],
        nq["mean_sum_4q"], a["quarters_covered_by_second_source"],
        a["quarters_second_source_agrees_within_5pct"]))

L.append("\n### 표 C. 원천별 접근 조건과 확보 분기 수\n")
L.append("| 원천 | 접근 조건 | 분기 통계 제공 | 확보 분기 수 | 한계 |")
L.append("|---|---|---|---|---|")
L.append("| Nasdaq `api.nasdaq.com` | 공개 JSON GET, 로그인·구독 없음 | 평균·최소·최대·전망치 수·4주 수정 건수 | 10개사 전부 4/4 (5분기까지 노출) | 중간값 미제공, `asOf`=null 로 추정 시점 미확인, 별표 회계 기준 정의 미공개 |")
L.append("| StockAnalysis `__data.json` | 공개. 3분기째부터 `[PRO]` 구독 구간 | 평균(조정·GAAP 열), 전망치 수 | 10개사 2/4 (SPCX 포함) | 최소·최대·중간값 미제공, 3·4분기 유료 |")
L.append("| Yahoo Finance (2026-09-08 기존 조사 재사용) | 공개, 무료는 2개 분기 | 평균 | 10개사 2/4 | 재수집하지 않음. 3·4분기 미제공 |")
L.append("| TradingView 스캐너 | 공개 JSON GET | 다음 1분기 평균, 직전 분기 실적·컨센서스, 다음 발표일 | 10개사 1/4 | 최소·최대·중간값·표본수 미제공 |")
L.append("| Zacks 종목 페이지 | 공개 | 평균(현재/다음 분기), 30·60·90일 전 추이 | 2/4 | 3·4분기 미노출. Nasdaq 분기값과 동일 확인(NVDA) |")
L.append("| Valley `valley.town` | 로그인 필요 | 최소·평균·중간값·최대·전망치 수 | 로그인 없이 0/4 | 이번 조사에서 미로그인 접근으로는 표를 얻지 못함 |")
L.append("| Investing.com / GuruFocus / Fintel / SimplyWallSt / AlphaSpread | 공개 페이지이나 봇 차단(403) | 미확인 | 0/4 | 차단 회피를 시도하지 않음. 자료 부재의 증명이 아님 |")
L.append("| FMP / MarketWatch / WSJ / Yahoo quoteSummary | 키·구독·인증 필요(401) | 미확인 | 0/4 | 결제·가입 없이 보류. 자료 부재의 증명이 아님 |")

L.append("\n### 표 D. 같은 분기 확정 실적 EPS 의 원천 간 차이 (회계 기준 진단)\n")
L.append("| 기업 | 마지막 발표 분기 | 기간 일치 | Nasdaq | TradingView | StockAnalysis 조정 | StockAnalysis GAAP 열 | 최대 격차 |")
L.append("|---|---|---|---|---|---|---|---|")
for c in ev["companies"]:
    b = c["basis_divergence_last_reported_quarter"]
    L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
        c["company_id"], b["period_label_nasdaq"],
        "예" if b["periods_match_within_7d"] else "아니오",
        b["actual_eps_nasdaq"], b["actual_eps_tradingview"],
        b["actual_eps_stockanalysis_adjusted"], b["actual_eps_stockanalysis_gaap_column"],
        b["max_abs_gap"]))

L.append("\n### 표 E. 첫 미발표 분기 평균의 원천 간 격차\n")
L.append("| 기업 | 분기 | Nasdaq | StockAnalysis | Yahoo(09-08) | TradingView | 최대 상대격차 |")
L.append("|---|---|---|---|---|---|---|")
for c in ev["companies"]:
    s = c["checks"]["q1_vendor_spread"]
    o = c["sources"]["nasdaq_api"]["observations"]
    L.append("| %s | %s | %s | %s | %s | %s | %s%% |" % (
        c["company_id"], o[0]["period_label_vendor"] if o else "-",
        s["nasdaq"], s["stockanalysis"], s["yahoo_2026_09_08"], s["tradingview"],
        s["max_rel_gap_vs_nasdaq_pct"]))

L.append("\n### 표 F. 계산 후보 (검증 대기, 채점 입력 아님)\n")
L.append("| 기업 | 주가 | 주가 시점 라벨 | 4분기 평균 EPS 합 | 주가÷EPS합 | 상태 |")
L.append("|---|---|---|---|---|---|")
for c in ev["companies"]:
    p = c["per_candidate"]
    L.append("| %s | %s | %s | %s | %s | %s |" % (
        c["company_id"], p["price"], p["price_label"], p["eps_sum_4q"],
        p["price_div_eps_sum"] if p["price_div_eps_sum"] is not None else "보류", p["status"]))

txt = "\n".join(L)
io.open(os.path.join(HERE, "tables.md"), "w", encoding="utf-8").write(txt)
print(txt)
