# TSMC 및 Alibaba NTM 원자료 수집·검증, 자료 확보와 채점 적격성 분리 및 R8 회귀 테스트 스크립트
from __future__ import annotations

import json
import math
import os
from datetime import datetime
from typing import Any
import yfinance as yf


def is_finite_number(val: Any) -> bool:
    """bool을 배제하고 유한한 숫자인지(NaN, Infinity 제외) 검사한다."""
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return math.isfinite(val)
    return False


def evaluate_quarterly_fulfillment(expected_quarters: list[str], observed_q_data: dict[str, Any]) -> dict[str, Any]:
    """관측 데이터로부터 4개 분기 자료 확보 여부와 채점 적격성을 분리하여 판정한다.
    
    1. expected_quarters는 정확히 4개의 서로 다른 고유 분기여야 한다 (빈 목록, 2개, 중복 거부).
    2. 개별 분기 EPS는 유한한 숫자이면 0과 음수도 정상 관측치로 유효하게 보존한다 (자료 확보 성공).
    3. bool, NaN, 양/음의 Infinity, 문자열 등 비숫자는 결측으로 처리한다.
    4. 4분기 자료 확보 완료(all_4q_fulfilled=True)와 채점 적격성(scoring_eligible: 4분기 합 > 0)을 엄격히 구분한다.
    """
    # R8-3: expected_quarters 검증 (정확히 4개의 고유 분기 필요)
    if not isinstance(expected_quarters, list) or len(expected_quarters) != 4 or len(set(expected_quarters)) != 4:
        return {
            "expected_quarters": expected_quarters if isinstance(expected_quarters, list) else [],
            "error": "expected_quarters must contain exactly 4 distinct quarters",
            "fulfilled_quarters": [],
            "missing_quarters": expected_quarters if isinstance(expected_quarters, list) else [],
            "fulfilled_count": 0,
            "missing_count": len(expected_quarters) if isinstance(expected_quarters, list) else 0,
            "all_4q_fulfilled": False,
            "values_by_quarter": {},
            "sum_4q_eps": None,
            "scoring_eligible": False,
            "scoring_status": "ineligible_quarters_spec",
        }

    fulfilled_quarters: list[str] = []
    missing_quarters: list[str] = []
    values_by_quarter: dict[str, float | None] = {}

    for q in expected_quarters:
        val = None
        if q in observed_q_data:
            raw_entry = observed_q_data[q]
            if isinstance(raw_entry, dict):
                val = raw_entry.get("avg")
            elif isinstance(raw_entry, (int, float)) and not isinstance(raw_entry, bool):
                val = raw_entry
        
        # R8-1, R8-2: 0과 음수도 유효한 숫자면 보존, bool/NaN/Inf 배제
        if is_finite_number(val):
            fulfilled_quarters.append(q)
            values_by_quarter[q] = float(val)
        else:
            missing_quarters.append(q)
            values_by_quarter[q] = None

    fulfilled_count = len(fulfilled_quarters)
    missing_count = len(missing_quarters)
    all_4q_fulfilled = (fulfilled_count == 4) and (missing_count == 0)

    # R8-1: 4분기 합 계산 및 채점 적격성 분리
    sum_4q_eps = None
    scoring_eligible = False
    scoring_status = "pending_data_missing_quarters"

    if all_4q_fulfilled:
        sum_4q_eps = sum(values_by_quarter[q] for q in expected_quarters if values_by_quarter[q] is not None)
        if sum_4q_eps > 0:
            scoring_eligible = True
            scoring_status = "eligible_for_f6_scoring"
        else:
            scoring_eligible = False
            scoring_status = "pending_data_eps_sum_non_positive"  # 네 분기 합 <= 0 채점 보류

    return {
        "expected_quarters": expected_quarters,
        "fulfilled_quarters": fulfilled_quarters,
        "missing_quarters": missing_quarters,
        "fulfilled_count": fulfilled_count,
        "missing_count": missing_count,
        "all_4q_fulfilled": all_4q_fulfilled,
        "values_by_quarter": values_by_quarter,
        "sum_4q_eps": sum_4q_eps,
        "scoring_eligible": scoring_eligible,
        "scoring_status": scoring_status,
    }


def run_offline_fixture_tests() -> None:
    """R8 재검증 요구사항 반영 오프라인 fixture 8종 테스트"""
    expected = ["0q", "+1q", "+2q", "+3q"]

    # 재현 1: [-1, 0, 2, 3] -> 4건 확보, 합 4.0, 채점 적격
    q_data_1 = {"0q": -1.0, "+1q": 0.0, "+2q": 2.0, "+3q": 3.0}
    res_1 = evaluate_quarterly_fulfillment(expected, q_data_1)
    assert res_1["fulfilled_count"] == 4, f"Expected 4, got {res_1['fulfilled_count']}"
    assert res_1["missing_count"] == 0
    assert res_1["all_4q_fulfilled"] is True
    assert res_1["values_by_quarter"]["0q"] == -1.0
    assert res_1["values_by_quarter"]["+1q"] == 0.0
    assert res_1["sum_4q_eps"] == 4.0
    assert res_1["scoring_eligible"] is True
    assert res_1["scoring_status"] == "eligible_for_f6_scoring"
    print("[Fixture 1 통과] 재현1: [-1, 0, 2, 3] 4건 정상확보, 0과 음수 보존 확인")

    # 재현 2: [True, Infinity, 2, 3] -> bool 및 Infinity 제외, 2건만 확보
    q_data_2 = {"0q": True, "+1q": float("inf"), "+2q": 2.0, "+3q": 3.0}
    res_2 = evaluate_quarterly_fulfillment(expected, q_data_2)
    assert res_2["fulfilled_count"] == 2, f"Expected 2, got {res_2['fulfilled_count']}"
    assert res_2["missing_count"] == 2
    assert res_2["all_4q_fulfilled"] is False
    assert res_2["fulfilled_quarters"] == ["+2q", "+3q"]
    assert res_2["values_by_quarter"]["0q"] is None
    assert res_2["values_by_quarter"]["+1q"] is None
    print("[Fixture 2 통과] 재현2: [True, Inf, 2, 3] bool/Infinity 배제 확인")

    # 재현 3: expected_quarters=[] 또는 불완전 목록 -> all_4q_fulfilled=False
    res_3_empty = evaluate_quarterly_fulfillment([], q_data_1)
    assert res_3_empty["all_4q_fulfilled"] is False
    assert "error" in res_3_empty

    res_3_dup = evaluate_quarterly_fulfillment(["0q", "0q", "+1q", "+2q"], q_data_1)
    assert res_3_dup["all_4q_fulfilled"] is False
    assert "error" in res_3_dup

    res_3_two = evaluate_quarterly_fulfillment(["0q", "+1q"], q_data_1)
    assert res_3_two["all_4q_fulfilled"] is False
    print("[Fixture 3 통과] 재현3: expected_quarters 빈목록/2개/중복 all_4q_fulfilled=False 처리 확인")

    # 재현 4: 자료 4건 확보 성공했으나 네 분기 합 <= 0 (F6 채점 보류 대상)
    q_data_zero_sum = {"0q": -2.0, "+1q": -1.0, "+2q": 1.0, "+3q": 2.0}  # 합 = 0.0
    res_zero = evaluate_quarterly_fulfillment(expected, q_data_zero_sum)
    assert res_zero["fulfilled_count"] == 4
    assert res_zero["all_4q_fulfilled"] is True  # 자료 4건 확보는 성공!
    assert res_zero["sum_4q_eps"] == 0.0
    assert res_zero["scoring_eligible"] is False  # 합이 0이므로 F6 채점은 보류!
    assert res_zero["scoring_status"] == "pending_data_eps_sum_non_positive"

    q_data_neg_sum = {"0q": -3.0, "+1q": -2.0, "+2q": 1.0, "+3q": 1.0}  # 합 = -3.0
    res_neg = evaluate_quarterly_fulfillment(expected, q_data_neg_sum)
    assert res_neg["all_4q_fulfilled"] is True
    assert res_neg["sum_4q_eps"] == -3.0
    assert res_neg["scoring_eligible"] is False
    print("[Fixture 4 통과] 재현4: 합 0/음수 시 자료 4건 확보 성공 vs F6 채점 보류 분리 확인")

    # 재현 5: NaN, -Infinity, 문자열 배제
    q_data_nan = {"0q": float("nan"), "+1q": float("-inf"), "+2q": "invalid", "+3q": None}
    res_nan = evaluate_quarterly_fulfillment(expected, q_data_nan)
    assert res_nan["fulfilled_count"] == 0
    assert res_nan["missing_count"] == 4
    assert res_nan["all_4q_fulfilled"] is False
    print("[Fixture 5 통과] 재현5: NaN/-Inf/문자열 배제 확인")

    # Fixture 6: 현재 Yahoo Finance 실측 상황 (0q, +1q만 수신)
    q_data_actual = {
        "0q": {"avg": 4.45297},
        "+1q": {"avg": 4.95689},
        "+2q": None,
        "+3q": None,
    }
    res_actual = evaluate_quarterly_fulfillment(expected, q_data_actual)
    assert res_actual["fulfilled_count"] == 2
    assert res_actual["missing_count"] == 2
    assert res_actual["all_4q_fulfilled"] is False
    assert res_actual["fulfilled_quarters"] == ["0q", "+1q"]
    assert res_actual["missing_quarters"] == ["+2q", "+3q"]
    print("[Fixture 6 통과] 실측 상황: 2개 분기 확보, 2개 분기 결측 판정 확인")

    # Fixture 7: 정상 4분기 양수 케이스
    q_data_all_pos = {
        "0q": {"avg": 4.45},
        "+1q": {"avg": 4.96},
        "+2q": {"avg": 5.10},
        "+3q": {"avg": 5.30},
    }
    res_all_pos = evaluate_quarterly_fulfillment(expected, q_data_all_pos)
    assert res_all_pos["all_4q_fulfilled"] is True
    assert res_all_pos["sum_4q_eps"] == 19.81
    assert res_all_pos["scoring_eligible"] is True
    print("[Fixture 7 통과] 정상 4분기 양수: 확보 완료 및 채점 적격 확인")

    print(">>> 오프라인 Fixture 7종 회귀 검증 전원 통과 <<<")


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
    dynamic_eval = evaluate_quarterly_fulfillment(expected_quarters, ee_dict)

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
        "period_definition_evidence": "unknown (공급사의 forwardEps 공식 대상기간 정의 문서 미확보)",
        "fulfillment_evaluation": dynamic_eval,
        "earnings_estimate_raw": ee_dict,
        "financialCurrency": info.get("financialCurrency"),
        "currency": info.get("currency"),
    }


def build_evidence() -> dict[str, Any]:
    collected_at = datetime.now().isoformat()

    # 1. 자동 수집 관측치 (Yahoo Finance API)
    yahoo_tsm = collect_yahoo_data("TSM")
    yahoo_baba = collect_yahoo_data("BABA")

    # 2. 수동 및 원문 실사 관측치
    manual_observations = {
        "stock_analysis_baba": {
            "source_name": "StockAnalysis BABA Forecast",
            "url": "https://stockanalysis.com/stocks/baba/forecast/",
            "verified_at": "2026-09-08T21:53:00+09:00",
            "observed_text_footer": "EPS and Forward PE are based on non-GAAP adjusted numbers. Financial currency is CNY.",
            "observed_table_data": {
                "Revenue_FY2026": "1.02T",
                "Revenue_FY2027": "1.12T",
                "Operating_Income_FY2026": "62.98B",
                "Net_Income_FY2026": "103.59B",
                "Net_Income_FY2027": "85.76B",
                "EPS_FY2026": "3.35",
                "EPS_FY2027": "5.71",
                "Forward_PE_FY2027": "133.10 (table) / 12.5~16.7 (statistics)",
            },
            "status": "currency_or_share_basis_unconfirmed",
            "status_reason": (
                "표 하단 각주에 'Financial currency is CNY'라고 명시되어 있으나, "
                "EPS 5.71 수치가 CNY 보통주 주당순이익인지, USD ADS 주당순이익인지, "
                "또는 통화 환산 누락인지 개별 필드 통화 및 보통주/ADS 배율이 원문에 명시되지 않음. "
                "GAAP vs non-GAAP 조정 내역, 희석/가중평균주식수, 집계 표본 일치 근거가 없으므로 "
                "충돌을 단정하지 않고 '통화 및 주식단위 미확인(currency_or_share_basis_unconfirmed)'으로 처리함."
            ),
            "quarterly_status": "browser_path_unverified (정적 HTML 파싱만 수행하여 Quarterly 토글 클릭 후 실제 데이터 렌더링 또는 차단 여부 미실사)",
            "official_annual_weighted_proxy_evidence": "unobtained_definition_document (조사 범위 내 공급사 공식 산출 정의 문서 미확보)",
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
            "quarterly_status": "browser_path_unverified (정적 HTML 파싱만 수행하여 Quarterly 토글 클릭 후 실제 데이터 렌더링 또는 차단 여부 미실사)",
            "official_annual_weighted_proxy_evidence": "unobtained_definition_document (조사 범위 내 공급사 공식 산출 정의 문서 미확보)",
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
            "gaap_status": "unconfirmed (GAAP 여부 미기재)",
            "estimate_as_of": "unconfirmed (개별 추정치 집계 기준시각 미표시)",
            "scope_note": "차기 1개 분기(2026 Q3) 외 이후 3개 분기 미제공",
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
            "gaap_status": "unconfirmed (GAAP 여부 미기재)",
            "estimate_as_of": "unconfirmed (개별 추정치 집계 기준시각 미표시)",
            "scope_note": "차기 1개 분기(FY27 Q2) 외 이후 3개 분기 미제공",
        },
        "zacks_tsm": {
            "source_name": "Zacks Detailed Earning Estimates TSM",
            "url": "https://www.zacks.com/stock/quote/TSM/detailed-earning-estimates",
            "verified_at": "2026-09-08T21:59:20+09:00",
            "metric_label": "P/E (F1)",
            "metric_value": "25.97",
            "period_nature": "Current Fiscal Year (F1, 12/2026 연간 추정치 $16.52 기준, 차기 연도가 아님)",
            "quarters_observed": ["Current Qtr (09/2026): 4.45", "Next Qtr (12/2026): 4.68"],
            "annual_observed": ["Current Year (12/2026, F1): 16.52", "Next Year (12/2027, F2): 21.09"],
            "four_quarters_available": False,
        },
        "finviz_tsm": {
            "source_name": "Finviz TSM",
            "url": "https://finviz.com/quote.ashx?t=TSM",
            "verified_at": "2026-09-08T21:53:15+09:00",
            "metric_label": "Forward P/E",
            "metric_value": "19.61",
            "period_nature": "Next Fiscal Year (차기 회계연도 연간 추정치 기준, Current Fiscal Year 인 Zacks F1 과 다름)",
            "official_definition_excerpt": "Forward P/E measures current share price relative to forecasted EPS for the next fiscal year.",
            "four_quarters_available": False,
        },
    }

    # 3. 4분기 충족 여부 및 채점 적격성 분리 객체
    tsm_mapping_basis = "TSMC 회계연도 종료 12월 31일 기준, 직전 확정 실적 2026 Q2(06/30). 미발표 차기 4분기는 2026 Q3, 2026 Q4, 2027 Q1, 2027 Q2 로 매핑됨."
    baba_mapping_basis = "Alibaba 회계연도 종료 3월 31일 기준, 직전 확정 실적 FY27 Q1(2026-06-30). 미발표 차기 4분기는 FY27 Q2(09/30), FY27 Q3(12/31), FY27 Q4(03/31), FY28 Q1(06/30) 로 매핑됨."

    tsm_eval = yahoo_tsm["fulfillment_evaluation"]
    baba_eval = yahoo_baba["fulfillment_evaluation"]

    quarterly_matrix = {
        "tsmc": {
            "mapping_basis": tsm_mapping_basis,
            "target_quarters_labels": ["2026 Q3", "2026 Q4", "2027 Q1", "2027 Q2"],
            "expected_period_keys": ["0q", "+1q", "+2q", "+3q"],
            "fulfilled_quarters": tsm_eval["fulfilled_quarters"],
            "missing_quarters": tsm_eval["missing_quarters"],
            "fulfilled_count": tsm_eval["fulfilled_count"],
            "missing_count": tsm_eval["missing_count"],
            "all_4q_fulfilled": tsm_eval["all_4q_fulfilled"],
            "values_observed": tsm_eval["values_by_quarter"],
            "sum_4q_eps": tsm_eval["sum_4q_eps"],
            "scoring_eligible": tsm_eval["scoring_eligible"],
            "scoring_status": tsm_eval["scoring_status"],
            "status": "unobtained_in_investigated_sources",
        },
        "alibaba": {
            "mapping_basis": baba_mapping_basis,
            "target_quarters_labels": ["FY27 Q2 (Sep 2026)", "FY27 Q3 (Dec 2026)", "FY27 Q4 (Mar 2027)", "FY28 Q1 (Jun 2027)"],
            "expected_period_keys": ["0q", "+1q", "+2q", "+3q"],
            "fulfilled_quarters": baba_eval["fulfilled_quarters"],
            "missing_quarters": baba_eval["missing_quarters"],
            "fulfilled_count": baba_eval["fulfilled_count"],
            "missing_count": baba_eval["missing_count"],
            "all_4q_fulfilled": baba_eval["all_4q_fulfilled"],
            "values_observed": baba_eval["values_by_quarter"],
            "sum_4q_eps": baba_eval["sum_4q_eps"],
            "scoring_eligible": baba_eval["scoring_eligible"],
            "scoring_status": baba_eval["scoring_status"],
            "status": "unobtained_in_investigated_sources",
        }
    }

    # 4. 결론 객체
    conclusion = {
        "investigated_sources_count": 6,
        "investigated_sources": ["Yahoo Finance", "StockAnalysis", "TipRanks", "Zacks", "Finviz", "Company IR"],
        "findings_within_investigated_scope": {
            "four_quarter_consensus": "조사 대상 6개 공개 출처에서 미발표 4분기 연속 컨센서스 미확보 (Yahoo 2개 분기 관측, 2개 분기 결측; TipRanks 1개 분기 관측).",
            "separation_of_collection_and_scoring": "4분기 자료 확보 여부(개별 분기 0/음수 허용)와 F6 채점 적격성(4분기 합 > 0)을 엄격히 분리 평가함.",
            "provider_pe_period_nature": "공급사 Forward P/E는 Current Fiscal Year 기준(Zacks F1)이거나 Next Fiscal Year 기준(Finviz)이며, Yahoo Finance와 StockAnalysis는 기간 정의 문서가 미확보(unobtained_definition_document)되어 NTM 적격 여부를 입증할 수 없음.",
            "baba_currency_status": "StockAnalysis BABA는 각주(CNY)와 EPS 수치(5.71) 간 통화·주식단위가 미확인(currency_or_share_basis_unconfirmed) 상태임.",
            "stock_analysis_quarterly_status": "Quarterly 토글 경로는 브라우저 경로 미검증(browser_path_unverified) 상태임.",
            "historical_reproducibility": "조사한 무료 웹 출처는 실시간 유동 스냅샷만 제공하여 2026-09-02 과거 기준시점 스냅샷 재현 불가. 오늘 값을 과거로 소급 적용 불가.",
        },
        "distinction_note": "본 결론은 조사 대상 공개 출처에서의 '미확보 및 접근 제한'을 확인한 것이며, 시장 전체에 데이터가 부재하다는 전칭 주장이 아님. 유료 기관용 DB의 실제 커버리지 여부는 미확인 상태로 유지함.",
        "c13_decision_impact": {
            "reject_proxy": "조사 출처 내 4분기 연속 NTM 원자료가 미확보 상태이므로 TSMC와 Alibaba F6는 pending_data(자료 대기)로 확정됨.",
            "accept_proxy_with_flag": "기준선에 기록된 annual_weighted_proxy 수치를 참고 정밀도 플래그와 함께 실행 단위 결정으로 채점에 사용함.",
        }
    }

    return {
        "schema": "scorecard.c13_data_validation/4",
        "task_id": "C13-DATA-01",
        "version": "R8-refined",
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
    print("=== 오프라인 Fixture 회귀 테스트 실행 ===")
    run_offline_fixture_tests()

    print("=== 실측 데이터 evidence.json 생성 ===")
    evidence = build_evidence()
    out_dir = os.path.dirname(__file__)
    json_path = os.path.join(out_dir, "evidence.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)
    print(f"R8 정정 evidence.json 생성 완료: {json_path}")


if __name__ == "__main__":
    main()
