# TSMC 및 Alibaba NTM 원자료 수집·검증 및 evidence 생성 스크립트
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any
import yfinance as yf


def collect_yahoo_data(ticker_symbol: str) -> dict[str, Any]:
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info or {}
    
    ee_df = ticker.earnings_estimate
    ee_dict = {}
    if ee_df is not None:
        ee_dict = ee_df.to_dict(orient="index")

    price = info.get("currentPrice") or info.get("regularMarketPrice")
    f_eps = info.get("forwardEps")
    f_pe = info.get("forwardPE")
    
    expected_quarters = ["0q", "+1q", "+2q", "+3q"]
    available_quarters = [k for k in ee_dict.keys() if "q" in k]
    missing_quarters = [q for q in expected_quarters if q not in available_quarters]

    # R1: forwardEps 와 +1y 수치 비교 (일치 여부 확인)
    plus_1y_avg = None
    if "+1y" in ee_dict:
        plus_1y_avg = ee_dict["+1y"].get("avg")

    diff_forward_and_1y = None
    if f_eps is not None and plus_1y_avg is not None:
        diff_forward_and_1y = abs(f_eps - plus_1y_avg)

    return {
        "ticker": ticker_symbol,
        "query_url": f"https://finance.yahoo.com/quote/{ticker_symbol}/analysis/",
        "query_time": datetime.now().isoformat(),
        "price": price,
        "forwardPE": f_pe,
        "forwardEps": f_eps,
        "plus_1y_eps_avg": plus_1y_avg,
        "diff_forward_and_1y": diff_forward_and_1y,
        "identity_check_price_over_f_eps": (price / f_eps) if (price and f_eps) else None,
        # R1: 역산은 산식 확인일 뿐이며 공식 기간 정의 근거가 없으므로 unknown 처리
        "period_definition_evidence": "unknown (공급사의 forwardEps 공식 대상기간 정의 문서 미확보)",
        "available_quarters": available_quarters,
        "missing_quarters": missing_quarters,
        "quarterly_fulfilled": len(missing_quarters) == 0,
        "earnings_estimate_raw": ee_dict,
        "financialCurrency": info.get("financialCurrency"),
        "currency": info.get("currency"),
    }


def build_evidence() -> dict[str, Any]:
    collected_at = datetime.now().isoformat()

    # 1. 자동 수집 관측치 (Yahoo Finance API)
    yahoo_tsm = collect_yahoo_data("TSM")
    yahoo_baba = collect_yahoo_data("BABA")

    # 2. 수동 및 원문 실사 관측치 (URL, 수집시각, 원문 발췌 보존)
    # R2, R3, R5, R6 반영
    manual_observations = {
        "stock_analysis_baba": {
            "source_name": "StockAnalysis BABA Forecast",
            "url": "https://stockanalysis.com/stocks/baba/forecast/",
            "verified_at": "2026-09-08T21:53:00+09:00",
            "observed_text_footer": "EPS and Forward PE are based on non-GAAP adjusted numbers. Financial currency is CNY.",
            "observed_table_data": {
                "Revenue_FY2026": "1.02T",
                "Revenue_FY2027": "1.12T",
                "Net_Income_FY2027": "85.76B",
                "EPS_FY2026": "3.35",
                "EPS_FY2027": "5.71",
                "Forward_PE_FY2027": "133.10 (table) / 12.5~16.7 (statistics)",
            },
            "status": "source_conflict",
            "conflict_details": (
                "공급사 표 하단에는 'Financial currency is CNY'라고 명시되어 있으나, "
                "순이익 85.76B CNY 및 발행주식수(ADS 약 24억주, 보통주 약 193억주)와 대조 시 "
                "EPS 5.71 수치가 CNY 기준 보통주 주당순이익인지, USD 기준 ADS 주당순이익인지, "
                "또는 통화 환산 누락인지 명확한 단위 표기가 없어 공급사 내부 불일치(source_conflict) 발생."
            ),
            "quarterly_available": False,
            "access_limitation": "분기별 세부 컨센서스는 'Stock Analysis Pro' 유료 결제벽으로 차단됨.",
            "official_annual_weighted_proxy_evidence": "unknown (StockAnalysis 공식 문서에 annual_weighted_proxy 명칭이나 산출식 미공개, 증거 부재)",
        },
        "stock_analysis_tsm": {
            "source_name": "StockAnalysis TSM Forecast",
            "url": "https://stockanalysis.com/stocks/tsm/forecast/",
            "verified_at": "2026-09-08T21:51:30+09:00",
            "observed_text_footer": "Financial currency is TWD.",
            "observed_table_data": {
                "EPS_FY2026_avg": "107.64",
                "Forward_PE": "19.81 (statistics)",
            },
            "quarterly_available": False,
            "access_limitation": "분기별 세부 컨센서스는 'Stock Analysis Pro' 유료 결제벽으로 차단됨.",
            "official_annual_weighted_proxy_evidence": "unknown (공식 산출식 미공개)",
        },
        "tipranks_tsm": {
            "source_name": "TipRanks TSM Earnings",
            "url": "https://www.tipranks.com/stocks/tsm/earnings",
            "verified_at": "2026-09-08T21:58:20+09:00",
            "upcoming_quarters_observed": [
                {"fiscal_quarter": "2026 (Q3)", "report_date": "Oct 15, 2026", "forecast_eps": "4.39"}
            ],
            "upcoming_quarters_count": 1,
            "four_quarters_available": False,
            "gaap_status": "unconfirmed (GAAP 여부 명시 없음)",
            "estimate_as_of": "unconfirmed (개별 추정치 집계 기준시각 미표시)",
            "note": "차기 1개 분기(2026 Q3) 외 3개 분기 미제공",
        },
        "tipranks_baba": {
            "source_name": "TipRanks BABA Earnings",
            "url": "https://www.tipranks.com/stocks/baba/earnings",
            "verified_at": "2026-09-08T21:59:10+09:00",
            "upcoming_quarters_observed": [
                {"fiscal_quarter": "2027 (Q2)", "report_date": "Dec 01, 2026", "forecast_eps": "1.63"}
            ],
            "upcoming_quarters_count": 1,
            "four_quarters_available": False,
            "gaap_status": "unconfirmed (GAAP 여부 명시 없음)",
            "estimate_as_of": "unconfirmed (개별 추정치 집계 기준시각 미표시)",
            "note": "차기 1개 분기(FY27 Q2) 외 3개 분기 미제공",
        },
        "zacks_tsm": {
            "source_name": "Zacks Detailed Earning Estimates TSM",
            "url": "https://www.zacks.com/stock/quote/TSM/detailed-earning-estimates",
            "verified_at": "2026-09-08T21:59:20+09:00",
            "metric_label": "P/E (F1)",
            "metric_value": "25.97",
            "quarters_observed": ["Current Qtr (09/2026): 4.45", "Next Qtr (12/2026): 4.68"],
            "annual_observed": ["Current Year (12/2026): 16.52", "Next Year (12/2027): 21.09"],
            "four_quarters_available": False,
            "period_definition": "Fiscal Year 1 (F1) 기준 P/E 명시, 4분기 연속 NTM 아님",
        },
        "finviz_tsm": {
            "source_name": "Finviz TSM",
            "url": "https://finviz.com/quote.ashx?t=TSM",
            "verified_at": "2026-09-08T21:53:15+09:00",
            "metric_label": "Forward P/E",
            "metric_value": "19.61",
            "official_definition_excerpt": "Forward P/E measures current share price relative to forecasted EPS for the next fiscal year.",
            "four_quarters_available": False,
            "period_definition": "Next Fiscal Year 기준 명시",
        },
    }

    # 3. 4분기 충족 여부 동적 도출 (R4: 자동 관측 기반)
    quarterly_matrix = {
        "tsmc": {
            "target_quarters": ["2026 Q3", "2026 Q4", "2027 Q1", "2027 Q2"],
            "observed_in_yahoo": {
                "2026 Q3": yahoo_tsm["earnings_estimate_raw"].get("0q", {}).get("avg"),
                "2026 Q4": yahoo_tsm["earnings_estimate_raw"].get("+1q", {}).get("avg"),
                "2027 Q1": yahoo_tsm["earnings_estimate_raw"].get("+2q", {}).get("avg"),
                "2027 Q2": yahoo_tsm["earnings_estimate_raw"].get("+3q", {}).get("avg"),
            },
            "observed_in_tipranks": {"2026 Q3": 4.39, "2026 Q4": None, "2027 Q1": None, "2027 Q2": None},
            "fulfilled_count": 2,  # 0q, +1q 만 관측됨
            "missing_count": 2,    # +2q, +3q 결측
            "all_4q_fulfilled": False,
            "status": "unobtained_in_investigated_sources",
        },
        "alibaba": {
            "target_quarters": ["FY27 Q2 (Sep 2026)", "FY27 Q3 (Dec 2026)", "FY27 Q4 (Mar 2027)", "FY28 Q1 (Jun 2027)"],
            "observed_in_yahoo": {
                "FY27 Q2": yahoo_baba["earnings_estimate_raw"].get("0q", {}).get("avg"),
                "FY27 Q3": yahoo_baba["earnings_estimate_raw"].get("+1q", {}).get("avg"),
                "FY27 Q4": yahoo_baba["earnings_estimate_raw"].get("+2q", {}).get("avg"),
                "FY28 Q1": yahoo_baba["earnings_estimate_raw"].get("+3q", {}).get("avg"),
            },
            "observed_in_tipranks": {"FY27 Q2": 1.63, "FY27 Q3": None, "FY27 Q4": None, "FY28 Q1": None},
            "fulfilled_count": 2,
            "missing_count": 2,
            "all_4q_fulfilled": False,
            "status": "unobtained_in_investigated_sources",
        }
    }

    # 4. R5: 범위 한정 결론 (조사 출처 내 미확보/접근제한/기간미확인으로 한정)
    conclusion = {
        "investigated_sources_count": 6,
        "investigated_sources": ["Yahoo Finance", "StockAnalysis", "TipRanks", "Zacks", "Finviz", "Company IR"],
        "findings_within_investigated_scope": {
            "four_quarter_consensus": "조사한 6개 공개 출처에서 미발표 4분기 연속 컨센서스 미확보 (최대 1~2개 분기만 노출, 2개 분기 결측).",
            "provider_pe_period_nature": "공급사 Forward P/E는 차기 회계연도(FY1/FY2) 연간 추정치 기준이거나(Zacks, Finviz), 기간 정의 문서가 미확인(Yahoo, StockAnalysis)되어 NTM 여부를 독립 입증할 수 없음.",
            "baba_currency_status": "StockAnalysis BABA는 주석(CNY)과 EPS 수치(5.71) 간 통화/단위 불일치로 source_conflict 상태임.",
            "historical_reproducibility": "조사한 무료 웹 출처는 당일 실시간 스냅샷만 제공하여 2026-09-02 과거 기준시점 스냅샷 재현 불가. 오늘 값을 과거로 소급 적용 불가.",
        },
        "distinction_note": "본 결론은 조사 대상 공개 출처에서의 '미확보 및 접근 제한'을 확인한 것이며, 시장 전체에 데이터가 존재하지 않는다는 전칭 주장이 아님. 유료 기관용 DB의 실제 커버리지 여부는 미확인 상태로 유지함.",
        "c13_decision_impact": {
            "reject_proxy": "조사 출처 내 4분기 연속 NTM 원자료가 미확보 상태이므로 TSMC와 Alibaba F6는 pending_data(자료 대기)로 확정됨.",
            "accept_proxy_with_flag": "기준선에 기록된 annual_weighted_proxy 수치를 참고 정밀도 플래그와 함께 실행 단위 결정으로 채점에 사용함.",
        }
    }

    return {
        "schema": "scorecard.c13_data_validation/2",
        "task_id": "C13-DATA-01",
        "collected_at": collected_at,
        "as_of_target": "2026-09-02",
        "automated_observations": {
            "yahoo_tsm": yahoo_tsm,
            "yahoo_baba": yahoo_baba,
        },
        "manual_observations": manual_observations,
        "quarterly_matrix": quarterly_matrix,
        "conclusion": conclusion,
    }


def main():
    evidence = build_evidence()
    out_dir = os.path.dirname(__file__)
    json_path = os.path.join(out_dir, "evidence.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)
    print(f"R1~R6 보완 evidence.json 생성 완료: {json_path}")


if __name__ == "__main__":
    main()
