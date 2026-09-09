# 사이트별 후보 공급원의 12개사 F6-H(2A+2E) 일괄 확보율, 단위 정합성 및 라이선스 제약을 비교하는 스크립트

import os
import sys
import json
import glob
import re

def run_comparison():
    # 12 listed companies in the scorecard
    tickers_12 = [
        {"id": "apple", "ticker": "AAPL", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "microsoft", "ticker": "MSFT", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "alphabet", "ticker": "GOOGL", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "amazon", "ticker": "AMZN", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "meta", "ticker": "META", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "nvidia", "ticker": "NVDA", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "tesla", "ticker": "TSLA", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "oracle", "ticker": "ORCL", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "palantir", "ticker": "PLTR", "market": "US", "basis": "common", "curr": "USD"},
        {"id": "spacex-xai", "ticker": "SPCX", "market": "US", "basis": "common", "curr": "USD", "ipo": "2026-06-12"},
        {"id": "tsmc", "ticker": "TSM", "market": "TW_ADR", "basis": "adr", "curr": "TWD", "ratio": 5},
        {"id": "alibaba", "ticker": "BABA", "market": "CN_ADS", "basis": "ads", "curr": "CNY", "ratio": 8}
    ]
    
    # 6 Candidate Sources evaluated independently (Strictly NO cherry-picking / mixing)
    sources = {
        "nasdaq": {
            "name": "Nasdaq (api.nasdaq.com - 비생산 참고용 검증 증거)",
            "vendor": "Zacks Investment Research",
            "accounting": "Zacks BNRI (Non-GAAP Adjusted Diluted EPS, excludes non-recurring, includes SBC)",
            "endpoint_type": "JSON Web Backend (REST)",
            "production_status": "denied_non_production_reference",
            "production_eligible": False,
            "can_batch_query": False,  # 생산 추가 쿼리 금지
            "has_as_of": False,  # asOf: null on public endpoint
            "point_in_time": False,
            "has_sample_size": True,  # noOfEstimates provided
            "has_min_max": True,  # highEPSForecast, lowEPSForecast
            "tos_status": "생산 원천 배제 (robots.txt Disallow / 및 약관상 자동 수집 금지, 공식 연동 시 Data Link B2B 서면 계약 필수)",
            "redistribution_terms": "생산 채택 제외 (기존 샘플은 비생산 참고용 검증 증거로만 보존)",
            "note": "api.nasdaq.com 생산 배제 정책에 따라 생산 입력·관측 등록·점수 계산 불가, 참고용 검증 증거(non-production reference)로만 보존",
            "coverage_eval": {}
        },
        "stockanalysis": {
            "name": "StockAnalysis (__data.json)",
            "vendor": "S&P Global Market Intelligence (spg) + TipRanks",
            "accounting": "S&P Global Normalized Non-GAAP Diluted EPS",
            "endpoint_type": "SvelteKit SSR Internal JSON",
            "can_batch_query": False,  # anti-bot / SSR internal
            "has_as_of": True,  # lastUpdated timestamp provided
            "point_in_time": False,  # snapshot only, no historical revisions
            "has_sample_size": True,  # analysts count provided
            "has_min_max": True,  # low/high in charts
            "tos_status": "스크래핑 금지, S&P Global 지재권 보호, 자동화 파이프라인 차단 위험",
            "redistribution_terms": "상업적 재배포 엄격 금지 (S&P Global 라이선스 필요)",
            "coverage_eval": {}
        },
        "finnhub": {
            "name": "Finnhub (calendar/earnings)",
            "vendor": "Finnhub Aggregation",
            "accounting": "미확정 (GAAP/Non-GAAP 미표기, 종목별 혼재)",
            "endpoint_type": "Public REST API (Free Key)",
            "can_batch_query": True,
            "has_as_of": False,  # only calendar dates
            "point_in_time": False,
            "has_sample_size": False,  # eps-estimate endpoint is 403 Paid
            "has_min_max": False,
            "tos_status": "무료 분당 60콜 허용, 단 전용 컨센서스(stock/eps-estimate) 403 차단",
            "redistribution_terms": "무료 데이터의 상업적 재배포 제한",
            "coverage_eval": {}
        },
        "fmp": {
            "name": "Financial Modeling Prep (FMP)",
            "vendor": "FMP Data Feed",
            "accounting": "미확정 (annual 기준)",
            "endpoint_type": "REST API / MCP",
            "can_batch_query": False,  # period=quarter is 402 Paid
            "has_as_of": False,
            "point_in_time": False,
            "has_sample_size": True,  # numAnalystsEps (annual only)
            "has_min_max": True,  # epsLow, epsHigh (annual only)
            "tos_status": "무료 등급 period=quarter 호출 차단 (HTTP 402 / ACCESS DENIED)",
            "redistribution_terms": "유료 상업 라이선스 필요",
            "coverage_eval": {}
        },
        "tradingview": {
            "name": "TradingView (Quote Fundamentals)",
            "vendor": "FactSet / TradingView",
            "accounting": "Normalized Diluted EPS",
            "endpoint_type": "Web Internal JSON",
            "can_batch_query": False,
            "has_as_of": False,
            "point_in_time": False,
            "has_sample_size": False,  # no analyst count in quote
            "has_min_max": False,
            "tos_status": "내부 엔드포인트 무단 스크래핑 금지",
            "redistribution_terms": "재배포 엄격 금지",
            "coverage_eval": {}
        },
        "yahoo_valley": {
            "name": "Valley / Yahoo Finance (Legacy Baseline)",
            "vendor": "LSEG / Refinitiv (I/B/E/S) or Legacy Valley Table",
            "accounting": "Refinitiv Non-GAAP / Static Valley",
            "endpoint_type": "Scraped HTML or Static Legacy Table",
            "can_batch_query": False,  # Yahoo API is 401 Crumb Error
            "has_as_of": False,
            "point_in_time": False,
            "has_sample_size": True,  # 44 (NVDA legacy)
            "has_min_max": False,  # only forward PE
            "tos_status": "Yahoo 공식 API 차단 (401), yfinance 사용 금지, Valley는 v1.5 보존용",
            "redistribution_terms": "상업적 재배포 불가",
            "coverage_eval": {}
        }
    }
    
    # Evaluate each source across the 12 companies
    for s_key, s_info in sources.items():
        cov = {
            "2a_available_count": 0,
            "2e_available_count": 0,
            "both_2a_2e_count": 0,
            "unit_consistent_count": 0,
            "eligible_for_f6h_count": 0,
            "ticker_details": {}
        }
        
        for comp in tickers_12:
            cid = comp["id"]
            ticker = comp["ticker"]
            basis = comp["basis"]
            curr = comp["curr"]
            
            has_2a = False
            has_2e = False
            unit_ok = False
            reason = ""
            
            if s_key == "nasdaq":
                # Nasdaq: US 10 companies have 4 previous (2A OK) and 4 forward (2E OK)
                if basis == "common":
                    has_2a = True
                    has_2e = True
                    unit_ok = True
                    if cid == "spacex-xai":
                        # SpaceX IPO recent: 2A has 0.0 actuals, anomalous
                        has_2a = False
                        reason = "신규 상장으로 2A 확정 실적 미축적 (2A=0.00)"
                elif basis in ["adr", "ads"]:
                    has_2e = True  # has 4Q in USD/ADR
                    has_2a = False  # 2A is in local TWD/CNY without uniform historical ADR feed
                    unit_ok = False
                    reason = f"ADR/ADS 단위 불일치 (2E는 USD/{basis.upper()}, 2A는 로컬 {curr})"
                    
            elif s_key == "stockanalysis":
                # StockAnalysis: forecast endpoint provides 2E for most US equities, but lacks 2A past quarters in same endpoint
                if basis == "common" and cid != "spacex-xai":
                    has_2e = True
                    has_2a = False  # requires scraping separate financials page, not in forecast __data.json
                    unit_ok = False
                    reason = "단일 엔드포인트 내 2A 과거 실적 부재 (다중 페이지 크롤링 필요)"
                else:
                    reason = "SPCX/ADR 데이터 불완전 또는 2A 부재"
                    
            elif s_key == "finnhub":
                # Finnhub: calendar/earnings provides 2E (future 3Q) and 2A (past epsActual)
                if basis == "common" and cid != "spacex-xai":
                    has_2a = True
                    has_2e = True
                    unit_ok = True  # USD common
                elif cid == "spacex-xai":
                    has_2a = False
                    has_2e = False
                    unit_ok = False
                    reason = "SPCX 티커 미지원으로 데이터 전무"
                elif basis in ["adr", "ads"]:
                    has_2a = True
                    has_2e = True
                    unit_ok = False
                    reason = f"통화/주식단위 왜곡 (TSM은 대만 보통주 TWD, BABA는 CNY/ADS 혼재)"
                    
            elif s_key == "fmp":
                # FMP: period=quarter is 402 Paid
                has_2a = False
                has_2e = False
                unit_ok = False
                reason = "무료 등급 period=quarter 전면 차단 (HTTP 402 / ACCESS DENIED)"
                
            elif s_key == "tradingview":
                # TradingView: only provides 1 past quarter (fq), missing 2A
                if basis == "common" and cid != "spacex-xai":
                    has_2e = True
                    has_2a = False  # only 1 past quarter provided
                    unit_ok = False
                    reason = "과거 확정 실적이 1개 분기(fq)만 제공되어 2A 구성 불가"
                else:
                    reason = "2A 결측 및 SPCX/ADR 미지원"
                    
            elif s_key == "yahoo_valley":
                # Yahoo / Valley: 401 Crumb error / Valley is static forward PE only
                has_2a = False
                has_2e = False
                unit_ok = False
                reason = "분기별 2A+2E 시계열 미제공 (Valley는 연간 정적 PER, Yahoo는 401 차단)"
                
            is_eligible = (has_2a and has_2e and unit_ok)
            
            if has_2a: cov["2a_available_count"] += 1
            if has_2e: cov["2e_available_count"] += 1
            if has_2a and has_2e: cov["both_2a_2e_count"] += 1
            if unit_ok: cov["unit_consistent_count"] += 1
            if is_eligible: cov["eligible_for_f6h_count"] += 1
            
            cov["ticker_details"][cid] = {
                "ticker": ticker,
                "basis": basis,
                "has_2a": has_2a,
                "has_2e": has_2e,
                "unit_consistent": unit_ok,
                "eligible_f6h": is_eligible,
                "reason": reason if not is_eligible else "단일 경로 2A+2E 일괄 확보 완료"
            }
            
        cov["f6h_eligible_rate_pct"] = round(cov["eligible_for_f6h_count"] / 12 * 100, 1)
        s_info["coverage_eval"] = cov

    # Overall Summary Matrix
    summary_matrix = []
    for s_key, s_info in sources.items():
        cov = s_info["coverage_eval"]
        summary_matrix.append({
            "source_key": s_key,
            "source_name": s_info["name"],
            "vendor": s_info["vendor"],
            "accounting": s_info["accounting"],
            "eligible_count_12": f"{cov['eligible_for_f6h_count']}/12",
            "eligible_rate_pct": f"{cov['f6h_eligible_rate_pct']}%",
            "has_2a_count": f"{cov['2a_available_count']}/12",
            "has_2e_count": f"{cov['2e_available_count']}/12",
            "unit_consistent_count": f"{cov['unit_consistent_count']}/12",
            "as_of_point_in_time": s_info["has_as_of"] and s_info["point_in_time"],
            "sample_size_provided": s_info["has_sample_size"],
            "tos_compliance": s_info["tos_status"],
            "production_status": s_info.get("production_status", "not_approved"),
            "single_source_f6h_viable": False  # 전 공급원 단일 채택 불가
        })
        
    return {
        "analysis_date": "2026-09-09",
        "task_id": "F6-H 사이트별 독립 공급원 비교 조사",
        "rule_strictness": "종목별 사이트 체리피킹(혼합) 배제, 단일 공급원 일괄 12개사 확보 검증",
        "sources": sources,
        "summary_matrix": summary_matrix,
        "key_findings": {
            "universal_100_percent_viable": False,
            "nasdaq_policy_status": "api.nasdaq.com 생산 배제 확정. 기존 표본은 비생산 참고용 검증 증거(non-production reference)로만 보존되며, 생산 입력·관측 등록·점수 계산에 사용 불가. Nasdaq 9/12 수치는 채택 후보가 아님.",
            "best_coverage_source": "finnhub (9/12, 단 403 차단 및 단위 왜곡으로 불가) / nasdaq (비생산 참고용 9/12, 생산 후보에서 전면 제외)",
            "adr_bottleneck": "모든 무료/공개 공급원에서 TSMC(TWD) 및 Alibaba(CNY)의 ADR/ADS 단위가 통일되지 않고 왜곡됨",
            "spcx_bottleneck": "신규 상장(2026-06)으로 인해 2A 확정 실적이 전 공급원에서 결측되거나 왜곡됨",
            "recommendation": "단일 무료 공급원으로 12개사 100% F6-H 통일은 기술적으로 불가능하며, F6를 정식 채점 입력으로 열기 위해서는 상용 B2B 유료 라이선스(Data Link 또는 S&P Global) 체결 및 ADR 단위 변환 게이트 정립이 선행되어야 함"
        }
    }

if __name__ == "__main__":
    res = run_comparison()
    out_dir = "C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "raw_source_comparison.json")
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(res, fp, ensure_ascii=False, indent=2)
    print(f"Source comparison complete. Saved to {out_file}")
    for row in res["summary_matrix"]:
        print(f"{row['source_name'][:25]:25s} | Eligible: {row['eligible_count_12']:6s} ({row['eligible_rate_pct']:5s}) | 2A: {row['has_2a_count']:5s} | 2E: {row['has_2e_count']:5s} | UnitOK: {row['unit_consistent_count']:5s} | Sample: {str(row['sample_size_provided']):5s}")
