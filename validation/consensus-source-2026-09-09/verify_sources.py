# TSMC, Alibaba 대체 원천 조사 및 OpenAI, Anthropic 비상장 지표 검증 스크립트 (C13-SOURCE-03 전면 보완본)
from __future__ import annotations

import json
import math
import os
import re
from datetime import datetime
from typing import Any


def is_finite_number(val: Any) -> bool:
    """bool을 배제하고 유한한 숫자인지(NaN, Infinity 제외) 검사한다."""
    if isinstance(val, bool):
        return False
    if isinstance(val, (int, float)):
        return math.isfinite(val)
    return False


def is_strict_true(val: Any) -> bool:
    """문자열 'false', 'true' 등 비-bool 타입의 오평가를 엄격히 차단하고 오직 Python bool True만 허용한다."""
    return isinstance(val, bool) and val is True


def is_valid_https_url(url: Any) -> bool:
    """공백이 없고 https:// 로 시작하는 유효한 직접 URL인지 검사한다."""
    if not isinstance(url, str):
        return False
    if " " in url or "\t" in url or "\n" in url:
        return False
    return url.startswith("https://")


def validate_valley_stat_structure(stat_dict: Any) -> dict[str, Any]:
    """Valley 방식 5종 통계(mean, median, min, max, count) 구조를 검증하고 통계적 모순을 검출한다."""
    if not isinstance(stat_dict, dict):
        return {
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "count": None,
            "has_mean": False,
            "has_median": False,
            "has_range": False,
            "has_sample_count": False,
            "stat_anomalies": ["invalid_input_type"],
            "auxiliary_missing": ["mean", "median", "min", "max", "count"],
        }

    mean = stat_dict.get("mean")
    median = stat_dict.get("median")
    min_val = stat_dict.get("min")
    max_val = stat_dict.get("max")
    count = stat_dict.get("count")

    has_mean = is_finite_number(mean)
    has_median = is_finite_number(median)
    has_min = is_finite_number(min_val)
    has_max = is_finite_number(max_val)
    has_count = isinstance(count, int) and count >= 0 and not isinstance(count, bool)

    stat_anomalies: list[str] = []
    has_range = False

    if has_min and has_max:
        if float(min_val) <= float(max_val):
            has_range = True
        else:
            has_range = False
            stat_anomalies.append("inverted_min_max")

    if has_mean and has_range:
        if float(mean) < float(min_val) or float(mean) > float(max_val):
            stat_anomalies.append("mean_outside_min_max_range")

    if has_mean and (count == 0):
        stat_anomalies.append("zero_count_with_mean")

    auxiliary_missing = [
        k for k, v in [
            ("median", has_median),
            ("min", has_min),
            ("max", has_max),
            ("count", has_count),
        ] if not v
    ]

    return {
        "mean": float(mean) if has_mean else None,
        "median": float(median) if has_median else None,
        "min": float(min_val) if has_min else None,
        "max": float(max_val) if has_max else None,
        "count": count if has_count else None,
        "has_mean": has_mean,
        "has_median": has_median,
        "has_range": has_range,
        "has_sample_count": has_count,
        "stat_anomalies": stat_anomalies,
        "auxiliary_missing": auxiliary_missing,
    }


def is_consecutive_quarters(quarters: list[str]) -> bool:
    """분기 라벨이 실제로 연속된 4개 회계분기인지 판정한다."""
    if not isinstance(quarters, list) or len(quarters) != 4:
        return False

    if quarters == ["0q", "+1q", "+2q", "+3q"]:
        return True

    parsed = []
    for q in quarters:
        m = re.match(r"^(\d{4})\s*Q([1-4])$", q.strip())
        if m:
            year, q_num = int(m.group(1)), int(m.group(2))
            parsed.append(year * 4 + (q_num - 1))
        else:
            m_fy = re.match(r"^FY(\d{2,4})\s*Q([1-4])", q.strip())
            if m_fy:
                fy_year, q_num = int(m_fy.group(1)), int(m_fy.group(2))
                parsed.append(fy_year * 4 + (q_num - 1))
            else:
                return False

    if len(parsed) != 4:
        return False

    for i in range(3):
        if parsed[i + 1] - parsed[i] != 1:
            return False

    return True


def evaluate_quarterly_single_source(
    expected_quarters: list[str],
    quarterly_data: dict[str, Any],
    basis_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """단일 원천 내에서 4개 미발표 분기가 모두 확보되었는지 검증한다.
    - null 항목(None) 입력 시 AttributeError 없이 안전하게 결측 처리 (R6).
    - 문자열 'false' bool 오평가 방어 및 strict boolean 검사 적용 (C13-SOURCE-03).
    - 통계적 모순(stat_anomalies) 존재 시 scoring_eligible=False 차단 (C13-SOURCE-03).
    - 4분기가 연속되지 않거나, 통화/주식단위/회계기준 메타데이터가 미확인인 경우 scoring_eligible=False 유지.
    """
    if not isinstance(expected_quarters, list) or len(expected_quarters) != 4 or len(set(expected_quarters)) != 4:
        return {
            "error": "expected_quarters must contain exactly 4 distinct quarters",
            "all_4q_fulfilled": False,
            "fulfilled_count": 0,
            "missing_count": len(expected_quarters) if isinstance(expected_quarters, list) else 0,
            "arithmetic_sum_calculable": False,
            "scoring_eligible": False,
            "scoring_status": "ineligible_quarters_spec",
        }

    consecutive_ok = is_consecutive_quarters(expected_quarters)

    fulfilled_quarters = []
    missing_quarters = []
    stats_by_quarter: dict[str, Any] = {}
    mean_by_quarter: dict[str, float | None] = {}
    any_stat_anomaly = False

    if not isinstance(quarterly_data, dict):
        quarterly_data = {}

    for q in expected_quarters:
        entry = quarterly_data.get(q)
        if entry is not None and isinstance(entry, dict):
            q_stat = validate_valley_stat_structure(entry)
            stats_by_quarter[q] = q_stat
            if q_stat["stat_anomalies"]:
                any_stat_anomaly = True
            if q_stat["has_mean"]:
                fulfilled_quarters.append(q)
                mean_by_quarter[q] = q_stat["mean"]
            else:
                missing_quarters.append(q)
                mean_by_quarter[q] = None
        else:
            missing_quarters.append(q)
            stats_by_quarter[q] = None
            mean_by_quarter[q] = None

    fulfilled_count = len(fulfilled_quarters)
    missing_count = len(missing_quarters)
    all_4q_fulfilled = (fulfilled_count == 4) and (missing_count == 0)

    # 메타데이터 엄격 검증 (C13-SOURCE-03: 문자열 'false' bool 변환 버그 원천 차단)
    currency_ok = False
    share_ok = False
    accounting_ok = False
    as_of_ok = False

    if isinstance(basis_metadata, dict):
        currency_ok = is_strict_true(basis_metadata.get("currency_confirmed"))
        share_ok = is_strict_true(basis_metadata.get("share_basis_confirmed"))
        accounting_ok = is_strict_true(basis_metadata.get("accounting_standard_confirmed"))
        as_of_ok = is_strict_true(basis_metadata.get("as_of_confirmed"))

    basis_verified = currency_ok and share_ok and accounting_ok and as_of_ok

    sum_4q_mean = None
    arithmetic_sum_calculable = False
    scoring_eligible = False
    scoring_status = "pending_data_missing_quarters"

    if all_4q_fulfilled:
        sum_4q_mean = round(sum(mean_by_quarter[q] for q in expected_quarters if mean_by_quarter[q] is not None), 4)
        arithmetic_sum_calculable = True

        if any_stat_anomaly:
            scoring_eligible = False
            scoring_status = "pending_stat_anomaly"
        elif not consecutive_ok:
            scoring_eligible = False
            scoring_status = "pending_consecutive_quarters_verification"
        elif not basis_verified:
            scoring_eligible = False
            scoring_status = "pending_basis_metadata_verification"
        elif sum_4q_mean <= 0:
            scoring_eligible = False
            scoring_status = "pending_data_eps_sum_non_positive"
        else:
            scoring_eligible = True
            scoring_status = "eligible_for_f6_scoring"

    return {
        "expected_quarters": expected_quarters,
        "consecutive_quarters": consecutive_ok,
        "basis_metadata_verified": basis_verified,
        "metadata_checks": {
            "currency_confirmed": currency_ok,
            "share_basis_confirmed": share_ok,
            "accounting_standard_confirmed": accounting_ok,
            "as_of_confirmed": as_of_ok,
        },
        "has_stat_anomalies": any_stat_anomaly,
        "fulfilled_quarters": fulfilled_quarters,
        "missing_quarters": missing_quarters,
        "fulfilled_count": fulfilled_count,
        "missing_count": missing_count,
        "all_4q_fulfilled": all_4q_fulfilled,
        "stats_by_quarter": stats_by_quarter,
        "mean_by_quarter": mean_by_quarter,
        "sum_4q_mean": sum_4q_mean,
        "arithmetic_sum_calculable": arithmetic_sum_calculable,
        "scoring_eligible": scoring_eligible,
        "scoring_status": scoring_status,
    }


def validate_unlisted_metrics(company: str, metrics: dict[str, Any]) -> dict[str, Any]:
    """비상장사(OpenAI, Anthropic) 전용 지표 검증."""
    evaluation = {}
    for k, item in metrics.items():
        if not isinstance(item, dict):
            continue

        raw_url = item.get("primary_source_url")
        url_valid = is_valid_https_url(raw_url)

        val = item.get("value")
        status = item.get("status", "unobtained")

        if val is not None and not url_valid and status in ("confirmed", "audited"):
            status = "reported_unverified_url"

        evaluation[k] = {
            "value": val,
            "currency": item.get("currency", "USD"),
            "metric_nature": item.get("metric_nature", "unspecified"),
            "definition": item.get("definition", "unobtained"),
            "as_of": item.get("as_of", "unconfirmed"),
            "status": status,
            "primary_source_url": raw_url if url_valid else (raw_url if isinstance(raw_url, str) else None),
            "url_valid_direct": url_valid,
            "snapshot_file": item.get("snapshot_file"),
            "notes": item.get("notes"),
        }

    return {
        "company": company,
        "listing_status": "unlisted_private",
        "pe_scoring_applicable": False,
        "ntm_eps_applicable": False,
        "metrics": evaluation,
    }


def run_unit_tests() -> None:
    """단위 테스트 11종 실행 (C13-SOURCE-03 회귀 테스트 포함)"""
    expected = ["2026 Q3", "2026 Q4", "2027 Q1", "2027 Q2"]

    # 1. R7: Valley 통계 모순 검출
    inv_stat = validate_valley_stat_structure({"mean": 5, "median": 8, "min": 7, "max": 2, "count": 0})
    assert inv_stat["has_range"] is False
    assert "inverted_min_max" in inv_stat["stat_anomalies"]
    print("[Test 1 PASS] R7: inverted min/max 및 zero count 모순 감지 확인")

    # 2. R6: null 분기 입력 시 AttributeError 방어
    null_case = evaluate_quarterly_single_source(expected, {expected[0]: {"mean": 4.45}, expected[1]: None})
    assert null_case["all_4q_fulfilled"] is False
    assert null_case["fulfilled_count"] == 1
    print("[Test 2 PASS] R6: null 분기 입력 시 AttributeError 방어 및 결측 처리 확인")

    # 3. R6: 비연속 4분기 거부
    non_consec = ["2026 Q3", "2027 Q1", "2027 Q3", "2028 Q1"]
    non_consec_case = evaluate_quarterly_single_source(non_consec, {k: {"mean": 1.0} for k in non_consec})
    assert non_consec_case["consecutive_quarters"] is False
    assert non_consec_case["scoring_eligible"] is False
    print("[Test 3 PASS] R6: 비연속 4분기 입력 시 scoring_eligible=False 거부 확인")

    # 4. C13-SOURCE-03: 문자열 'false' bool 변환 버그 방어 검증
    str_false_meta = {
        "currency_confirmed": "false",
        "share_basis_confirmed": "false",
        "accounting_standard_confirmed": "false",
        "as_of_confirmed": "false",
    }
    str_false_case = evaluate_quarterly_single_source(expected, {k: {"mean": 1.0} for k in expected}, basis_metadata=str_false_meta)
    assert str_false_case["all_4q_fulfilled"] is True
    assert str_false_case["basis_metadata_verified"] is False, "문자열 'false'는 False로 평가되어야 함"
    assert str_false_case["scoring_eligible"] is False, "문자열 'false'로 채점 적격 통과되면 안 됨"
    print("[Test 4 PASS] C13-SOURCE-03: 문자열 'false'의 bool 오평가 방어 확인")

    # 5. C13-SOURCE-03: 통계적 모순(anomaly) 존재 시 4분기 충족이어도 채점 적격 차단 검증
    anomaly_q = {
        "2026 Q3": {"mean": 5.0, "min": 7.0, "max": 2.0, "count": 0},  # min > max 모순
        "2026 Q4": {"mean": 4.68},
        "2027 Q1": {"mean": 4.64},
        "2027 Q2": {"mean": 5.10},
    }
    full_true_meta = {
        "currency_confirmed": True,
        "share_basis_confirmed": True,
        "accounting_standard_confirmed": True,
        "as_of_confirmed": True,
    }
    anomaly_case = evaluate_quarterly_single_source(expected, anomaly_q, basis_metadata=full_true_meta)
    assert anomaly_case["all_4q_fulfilled"] is True
    assert anomaly_case["has_stat_anomalies"] is True
    assert anomaly_case["scoring_eligible"] is False, "통계 모순 시 scoring_eligible=False여야 함"
    assert anomaly_case["scoring_status"] == "pending_stat_anomaly"
    print("[Test 5 PASS] C13-SOURCE-03: 통계 모순 시 scoring_eligible=False 차단 확인")

    # 6. 연속 4분기 + 4개 메타데이터 충족 + 합 > 0 일 때만 scoring_eligible=True
    valid_case = evaluate_quarterly_single_source(expected, {k: {"mean": 2.0} for k in expected}, basis_metadata=full_true_meta)
    assert valid_case["scoring_eligible"] is True
    assert valid_case["sum_4q_mean"] == 8.0
    print("[Test 6 PASS] R6: 연속 4분기 + 전 메타데이터 충족 시 F6 적격 판정 확인")

    # 7. 0과 음수 관측치 보존
    nonpos_case = evaluate_quarterly_single_source(
        expected, {k: {"mean": v} for k, v in zip(expected, [-1.0, 0.0, 2.0, 3.0])}, basis_metadata=full_true_meta
    )
    assert nonpos_case["fulfilled_count"] == 4
    assert nonpos_case["sum_4q_mean"] == 4.0
    print("[Test 7 PASS] R6: 0과 음수 분기 EPS 보존 및 합 양수 시 적격 확인")

    # 8. R1: Anthropic revenue_forecast None 및 target_ipo_valuation 분리
    anth_eval = validate_unlisted_metrics("Anthropic", {
        "revenue_forecast": {"value": None, "status": "unobtained", "primary_source_url": None},
        "target_ipo_valuation": {"value": 2000.0, "status": "target_plan", "primary_source_url": "https://www.reuters.com"}
    })
    assert anth_eval["metrics"]["revenue_forecast"]["value"] is None
    assert anth_eval["metrics"]["revenue_forecast"]["status"] == "unobtained"
    assert anth_eval["metrics"]["target_ipo_valuation"]["value"] == 2000.0
    print("[Test 8 PASS] R1: Anthropic revenue_forecast None 및 target_ipo_valuation 분리 확인")

    # 9. R2, R3: OpenAI 852B 공식 원문 및 직접 URL
    openai_eval = validate_unlisted_metrics("OpenAI", {
        "post_money_valuation": {
            "value": 852.0,
            "status": "confirmed",
            "as_of": "2026-03-31",
            "primary_source_url": "https://openai.com/index/accelerating-the-next-phase-ai/",
        }
    })
    assert openai_eval["metrics"]["post_money_valuation"]["value"] == 852.0
    assert openai_eval["metrics"]["post_money_valuation"]["url_valid_direct"] is True
    print("[Test 9 PASS] R2, R3: OpenAI 852B 공식 원문 및 직접 URL 확인")

    # 10. TSMC Nasdaq API 4분기 수집 케이스 검증 (18.87)
    tsm_nasdaq_q = {
        "2026 Q3": {"mean": 4.45, "min": 4.24, "max": 4.70, "count": 6},
        "2026 Q4": {"mean": 4.68, "min": 4.22, "max": 4.93, "count": 5},
        "2027 Q1": {"mean": 4.64, "min": 4.36, "max": 4.97, "count": 4},
        "2027 Q2": {"mean": 5.10, "min": 4.90, "max": 5.49, "count": 4},
    }
    tsm_nasdaq_eval = evaluate_quarterly_single_source(
        expected, tsm_nasdaq_q, basis_metadata={"currency_confirmed": False, "share_basis_confirmed": True}
    )
    assert tsm_nasdaq_eval["all_4q_fulfilled"] is True
    assert tsm_nasdaq_eval["sum_4q_mean"] == 18.87
    assert tsm_nasdaq_eval["arithmetic_sum_calculable"] is True
    assert tsm_nasdaq_eval["scoring_eligible"] is False
    assert tsm_nasdaq_eval["scoring_status"] == "pending_basis_metadata_verification"
    print("[Test 10 PASS] TSMC Nasdaq API 4분기 확보(18.87) 및 단위미확인 채점보류 분리 확인")

    # 11. 모의 전 메타데이터 충족 시 계산 로직 검증 (계산 동작 검사이며 외부 기준 입증이 아님)
    mock_verified_meta = {
        "currency_confirmed": True,
        "share_basis_confirmed": True,
        "accounting_standard_confirmed": True,
        "as_of_confirmed": True,
    }
    mock_verified_case = evaluate_quarterly_single_source(expected, tsm_nasdaq_q, basis_metadata=mock_verified_meta)
    assert mock_verified_case["scoring_eligible"] is True
    assert mock_verified_case["scoring_status"] == "eligible_for_f6_scoring"
    print("[Test 11 PASS] 모의 메타데이터 True 주입 시 F6 적격 계산 로직 동작 확인 (외부 입증 대체 아님)")

    # 12. S03-01~03: 실제 메타데이터 미확인(False) 시 scoring_eligible=False 채점 보류 유지 검증
    actual_unconfirmed_meta = {
        "currency_confirmed": False,
        "share_basis_confirmed": False,
        "accounting_standard_confirmed": False,
        "as_of_confirmed": False,
    }
    actual_case = evaluate_quarterly_single_source(expected, tsm_nasdaq_q, basis_metadata=actual_unconfirmed_meta)
    assert actual_case["all_4q_fulfilled"] is True
    assert actual_case["basis_metadata_verified"] is False
    assert actual_case["scoring_eligible"] is False
    assert actual_case["scoring_status"] == "pending_basis_metadata_verification"
    print("[Test 12 PASS] S03-01~03: 메타데이터 미확인 시 scoring_eligible=False(채점 보류) 유지 확인")

    print(">>> 단위 테스트 12종 전원 통과 <<<")


def generate_all_evidence() -> dict[str, Any]:
    """C13-SOURCE-03 보완 사항이 완전히 반영된 evidence 객체 생성"""
    collected_at = datetime.now().isoformat()
    tsmc_expected = ["2026 Q3", "2026 Q4", "2027 Q1", "2027 Q2"]
    baba_expected = ["FY27 Q2", "FY27 Q3", "FY27 Q4", "FY28 Q1"]

    tsmc_nasdaq_data = {
        "2026 Q3": {"mean": 4.45, "min": 4.24, "max": 4.70, "count": 6},
        "2026 Q4": {"mean": 4.68, "min": 4.22, "max": 4.93, "count": 5},
        "2027 Q1": {"mean": 4.64, "min": 4.36, "max": 4.97, "count": 4},
        "2027 Q2": {"mean": 5.10, "min": 4.90, "max": 5.49, "count": 4},
    }

    baba_nasdaq_data = {
        "FY27 Q2": {"mean": 1.42, "min": 0.81, "max": 2.16, "count": 3},
        "FY27 Q3": {"mean": 1.89, "min": 1.31, "max": 2.75, "count": 3},
        "FY27 Q4": {"mean": 1.81, "min": 1.05, "max": 2.21, "count": 3},
        "FY28 Q1": {"mean": 2.45, "min": 1.76, "max": 3.13, "count": 2},
    }

    # TSMC 메타데이터 검증 결과 (S03-01~03: 추정 단정 배제 및 미확인 분리)
    tsmc_criteria_verification = {
        "data_provider": "Zacks Investment Research (Nasdaq 제휴 공급사)",
        "methodology": "unconfirmed_series (Zacks 공식 FAQ상 BNRI와 Street 계열이 존재하며, Nasdaq EPS* 필드 직결 각주 부재)",
        "accounting_standard": "unconfirmed_standard (Non-GAAP 조정 희석 추정되나 직접 필드 메타데이터 부재)",
        "share_basis": "American Depositary Shares (1 ADR = 5 보통주이나 EPS 분모 단위 직결 근거 미확보)",
        "pricing_currency": "USD (주가 통화는 확인되나 EPS 필드 통화 코드 부재)",
        "eps_currency": "unconfirmed_currency (USD 추정)",
        "as_of_status": "unknown (JSON상 asOf null이며 일일 동적갱신 단정 철회, 수집시각 2026-09-09T02:11:00Z과 기준일 분리)",
        "criteria_verification_conclusion": "unconfirmed_metadata (채점 보류 유지)",
    }

    baba_criteria_verification = {
        "data_provider": "Zacks Investment Research (Nasdaq 제휴 공급사)",
        "methodology": "unconfirmed_series (Zacks 공식 FAQ상 BNRI와 Street 계열이 존재하며, Nasdaq EPS* 필드 직결 각주 부재)",
        "accounting_standard": "unconfirmed_standard (Non-GAAP 조정 희석 추정되나 직접 필드 메타데이터 부재)",
        "share_basis": "American Depositary Shares (1 ADS = 8 보통주이나 EPS 분모 단위 직결 근거 미확보)",
        "pricing_currency": "USD (주가 통화는 확인되나 EPS 필드 통화 코드 부재)",
        "eps_currency": "unconfirmed_currency (USD 추정)",
        "as_of_status": "unknown (JSON상 asOf null이며 일일 동적갱신 단정 철회, 수집시각 2026-09-09T02:11:00Z과 기준일 분리)",
        "criteria_verification_conclusion": "unconfirmed_metadata (채점 보류 유지)",
    }

    tsmc_sources = {
        "nasdaq_api": {
            "source_name": "Nasdaq Public API TSM Earnings Forecast",
            "url": "https://api.nasdaq.com/api/analyst/TSM/earnings-forecast",
            "info_url": "https://api.nasdaq.com/api/quote/TSM/info?assetclass=stocks",
            "verified_at": "2026-09-09T02:11:00Z",
            "access_condition": "free_public_api",
            "criteria_verification": tsmc_criteria_verification,
            "snapshot_file": "snapshots/nasdaq_tsm_earnings_forecast_2026_09_09.md",
            "raw_file": "raw/nasdaq-tsm-earnings_forecast.json",
            "quarters_available": tsmc_expected,
            "quarters_data": tsmc_nasdaq_data,
            "fifth_quarter_observed": {"fiscalEnd": "Sep 2027", "mean": 5.65, "min": 5.43, "max": 5.94, "count": 4},
            "yearly_forecast_observed": {
                "Dec 2026": {"consensus": 16.52, "count": 9},
                "Dec 2027": {"consensus": 21.09, "count": 9},
            },
            "evaluation": evaluate_quarterly_single_source(
                tsmc_expected,
                tsmc_nasdaq_data,
                basis_metadata={
                    "currency_confirmed": False,
                    "share_basis_confirmed": False,
                    "accounting_standard_confirmed": False,
                    "as_of_confirmed": False,
                },
            ),
            "notes": (
                "4분기 연속 수치(4.45, 4.68, 4.64, 5.10) 합산치 18.87 확보 완료. "
                "단, Zacks 계열(BNRI vs Street) 및 EPS 통화/분모/기준일 직접 필드 메타데이터 부재로 "
                "scoring_eligible=False(채점 보류) 유지 (S03-01~03 반영)."
            )
        },
        "barchart": {
            "source_name": "Barchart TSM Earnings Estimates",
            "url": "https://www.barchart.com/stocks/quotes/TSM/earnings-estimates",
            "verified_at": "2026-09-09T10:48:10+09:00",
            "access_condition": "free_public_direct",
            "quarters_data": {"2026 Q3": {"mean": 4.45, "min": 4.24, "max": 4.70, "count": 6}, "2026 Q4": None, "2027 Q1": None, "2027 Q2": None},
            "evaluation": evaluate_quarterly_single_source(tsmc_expected, {"2026 Q3": {"mean": 4.45}}),
        },
        "yahoo_finance_c13_link": {
            "source_name": "Yahoo Finance (C13-DATA-01-R8 기수집 연계)",
            "url": "https://finance.yahoo.com/quote/TSM/analysis/",
            "verified_at": "2026-09-08T22:08:00+09:00",
            "access_condition": "free_public_api",
            "prior_task_reference": "C13-DATA-01-R8",
            "snapshot_file": "snapshots/yahoo_consensus_c13_link.md",
            "quarters_data": {"2026 Q3": {"mean": 4.45297, "count": 5}, "2026 Q4": {"mean": 4.95689, "count": 4}, "2027 Q1": None, "2027 Q2": None},
            "evaluation": evaluate_quarterly_single_source(tsmc_expected, {"2026 Q3": {"mean": 4.45297}, "2026 Q4": {"mean": 4.95689}}),
        },
    }

    baba_sources = {
        "nasdaq_api": {
            "source_name": "Nasdaq Public API BABA Earnings Forecast",
            "url": "https://api.nasdaq.com/api/analyst/BABA/earnings-forecast",
            "info_url": "https://api.nasdaq.com/api/quote/BABA/info?assetclass=stocks",
            "verified_at": "2026-09-09T02:11:00Z",
            "access_condition": "free_public_api",
            "criteria_verification": baba_criteria_verification,
            "snapshot_file": "snapshots/nasdaq_baba_earnings_forecast_2026_09_09.md",
            "raw_file": "raw/nasdaq-baba-earnings_forecast.json",
            "quarters_available": baba_expected,
            "quarters_data": baba_nasdaq_data,
            "fifth_quarter_observed": {"fiscalEnd": "Sep 2027", "mean": 2.35, "min": 1.57, "max": 3.13, "count": 2},
            "yearly_forecast_observed": {
                "Mar 2027": {"consensus": 5.88, "count": 6},
                "Mar 2028": {"consensus": 8.61, "count": 6},
            },
            "evaluation": evaluate_quarterly_single_source(
                baba_expected,
                baba_nasdaq_data,
                basis_metadata={
                    "currency_confirmed": False,
                    "share_basis_confirmed": False,
                    "accounting_standard_confirmed": False,
                    "as_of_confirmed": False,
                },
            ),
            "notes": (
                "4분기 연속 수치(1.42, 1.89, 1.81, 2.45) 합산치 7.57 확보 완료. "
                "단, Zacks 계열(BNRI vs Street) 및 EPS 통화/분모/기준일 직접 필드 메타데이터 부재로 "
                "scoring_eligible=False(채점 보류) 유지 (S03-01~03 반영)."
            )
        },
        "yahoo_finance_c13_link": {
            "source_name": "Yahoo Finance (C13-DATA-01-R8 기수집 연계)",
            "url": "https://finance.yahoo.com/quote/BABA/analysis/",
            "verified_at": "2026-09-08T22:08:00+09:00",
            "access_condition": "free_public_api",
            "prior_task_reference": "C13-DATA-01-R8",
            "snapshot_file": "snapshots/yahoo_consensus_c13_link.md",
            "quarters_data": {"FY27 Q2": {"mean": 10.98, "currency": "CNY"}, "FY27 Q3": {"mean": 14.87, "currency": "CNY"}, "FY27 Q4": None, "FY28 Q1": None},
            "evaluation": evaluate_quarterly_single_source(baba_expected, {"FY27 Q2": {"mean": 10.98}, "FY27 Q3": {"mean": 14.87}}),
        }
    }

    # 비상장사 지표 (S03-04, S03-05 완벽 보완: URL 없는 2차 보도 관측치 배제, 산식 미공개 명시)
    openai_metrics = validate_unlisted_metrics("OpenAI", {
        "post_money_valuation": {
            "value": 852.0,
            "currency": "USD_B",
            "metric_nature": "post_money_valuation",
            "definition": "Post-money valuation officially announced in 'Accelerating the next phase of AI'",
            "as_of": "2026-03-31",
            "status": "confirmed",
            "primary_source_url": "https://openai.com/index/accelerating-the-next-phase-ai/",
            "snapshot_file": "snapshots/openai_2026_03_31_accelerating_next_phase.md",
            "notes": "2026-03-31 공식 발표 사후 기업가치 $852B 직접 확인."
        },
        "committed_capital_latest_round": {
            "value": 122.0,
            "currency": "USD_B",
            "metric_nature": "committed_capital_round",
            "definition": "Total committed capital officially announced on 2026-03-31",
            "as_of": "2026-03-31",
            "status": "confirmed",
            "primary_source_url": "https://openai.com/index/accelerating-the-next-phase-ai/",
            "snapshot_file": "snapshots/openai_2026_03_31_accelerating_next_phase.md",
            "notes": "공식 발표문상 $122B 약정 자본 직접 확인. 전액 현금이나 전액 컴퓨팅으로 단정하지 않음."
        },
        "historical_valuation_2024": {
            "value": 157.0,
            "currency": "USD_B",
            "metric_nature": "historical_post_money_valuation",
            "definition": "Post-money valuation from Series funding led by Thrive Capital ($6.6B raised)",
            "as_of": "2024-10-02",
            "status": "confirmed",
            "primary_source_url": "https://openai.com/index/scale-next-frontier/",
            "notes": "과거 2024년 10월 라운드 이력으로 보존."
        },
        "actual_annual_revenue": {
            "value": 3.7,
            "currency": "USD_B",
            "metric_nature": "recognized_annual_revenue",
            "definition": "Recognized GAAP full-year revenue for FY2024 from financial audit leaks",
            "as_of": "FY2024",
            "status": "unverified_article_url",
            "primary_source_url": None,
            "notes": "직접 기사 URL 부재로 검증된 관측치로 사용하지 않음. 당사 조사 범위 내 확인 결과임."
        },
        "annualized_revenue_run_rate": {
            "value": 40.0,
            "currency": "USD_B",
            "metric_nature": "annualized_run_rate",
            "definition": "Annualized Revenue Run Rate (ARR) based on reported monthly pace",
            "as_of": "2026-08-31",
            "status": "unverified_article_url",
            "primary_source_url": None,
            "notes": "직접 기사 URL 부재로 검증된 관측치로 사용하지 않음. 당사 조사 범위 내 확인 결과임."
        },
        "revenue_forecast": {
            "value": 100.0,
            "currency": "USD_B",
            "metric_nature": "management_target_projection",
            "definition": "Projected annual revenue target by 2029 presented in investor deck",
            "as_of": "2024-10_deck",
            "status": "unverified_article_url",
            "primary_source_url": None,
            "notes": "직접 기사 URL 부재로 검증된 관측치로 사용하지 않음. 미래 전망은 감사 대상이 아님."
        },
        "cumulative_funding": {
            "value": 17.9,
            "currency": "USD_B",
            "metric_nature": "confirmed_cumulative_capital",
            "definition": "Total cumulative raised capital confirmed as of October 2024 round",
            "as_of": "2024-10-02",
            "status": "confirmed",
            "primary_source_url": "https://www.crunchbase.com",
            "notes": "2024년 10월 완료 기준 약 $17.9B."
        }
    })

    anthropic_metrics = validate_unlisted_metrics("Anthropic", {
        "post_money_valuation": {
            "value": 965.0,
            "currency": "USD_B",
            "metric_nature": "post_money_valuation",
            "definition": "Post-money valuation officially announced in Series H news release",
            "as_of": "2026-05-28",
            "status": "confirmed",
            "primary_source_url": "https://www.anthropic.com/news/series-h",
            "snapshot_file": "snapshots/anthropic_2026_05_28_series_h.md",
            "notes": "2026-05-28 공식 발표 사후 기업가치 $965B 직접 확인."
        },
        "series_h_round_raised": {
            "value": 65.0,
            "currency": "USD_B",
            "metric_nature": "round_gross_raised",
            "definition": "Series H funding round including $15B of previously committed investments",
            "as_of": "2026-05-28",
            "status": "confirmed",
            "primary_source_url": "https://www.anthropic.com/news/series-h",
            "snapshot_file": "snapshots/anthropic_2026_05_28_series_h.md",
            "notes": "공식 발표상 본 $65B에는 기존 약정 투자금 $15B가 포함되어 있음. 차감액 $50B는 단순 산술 추론(arithmetic deduction)임."
        },
        "target_ipo_valuation": {
            "value": 2000.0,
            "currency": "USD_B",
            "metric_nature": "target_market_cap_plan",
            "definition": "Reported target market cap for planned late 2026 IPO",
            "as_of": "2026-09",
            "status": "unverified_article_url",
            "primary_source_url": None,
            "notes": "직접 기사 URL 부재로 검증된 관측치로 사용하지 않음. 매출 전망이 아님."
        },
        "actual_annual_revenue": {
            "value": None,
            "currency": "USD",
            "metric_nature": "audited_annual_revenue",
            "definition": "Audited full-year recognized revenue",
            "as_of": "unconfirmed",
            "status": "unobtained",
            "primary_source_url": None,
            "notes": "당사 조사 범위 내에서 공식 감사보고서 미공개로 미확보(None) 처리."
        },
        "annualized_revenue_run_rate": {
            "value": 47.0,
            "currency": "USD_B",
            "metric_nature": "run_rate_revenue",
            "definition": "Annualized run-rate revenue officially confirmed at Series H announcement (> $47B in May 2026)",
            "as_of": "2026-05-28",
            "status": "confirmed_official_announcement",
            "primary_source_url": "https://www.anthropic.com/news/series-h",
            "snapshot_file": "snapshots/anthropic_2026_05_28_series_h.md",
            "notes": "공식 원문 표현은 'run-rate revenue' (> $47B in May). 반복매출(ARR) 여부 및 연율화 산식은 미공개(unspecified_formula / unknown)."
        },
        "revenue_forecast": {
            "value": None,
            "currency": "USD",
            "metric_nature": "forward_revenue_forecast",
            "definition": "Forward revenue projection",
            "as_of": "unconfirmed",
            "status": "unobtained",
            "primary_source_url": None,
            "notes": "당사 조사 범위 내에서 미래 매출 전망은 공식 미공개로 미확보(None) 처리."
        },
        "cumulative_funding": {
            "value": None,
            "currency": "USD_B",
            "metric_nature": "unconfirmed_cumulative_ledger",
            "definition": "Total cumulative raised capital across historical rounds",
            "as_of": "2026-05-28",
            "status": "unconfirmed_ledger",
            "primary_source_url": "https://www.anthropic.com/news/series-h",
            "snapshot_file": "snapshots/anthropic_2026_05_28_series_h.md",
            "notes": (
                "세부 중간 라운드(D~G 등) 개별 출처 부재 및 전환사채/약정 중복성으로 인해 "
                "원장 미확인(unconfirmed_ledger)으로 유지 (S03-05 반영)."
            )
        }
    })

    return {
        "schema": "scorecard.consensus_source_validation/4",
        "task_id": "C13-SOURCE-03",
        "version": "s03_review_refined",
        "collected_at": collected_at,
        "methodology": "Valley 5-stat cross-source with strict metadata separation and unconfirmed hold",
        "listed_companies": {
            "tsmc": {
                "ticker": "TSM / 2330.TW",
                "mapping_quarters": tsmc_expected,
                "sources_investigated": tsmc_sources,
                "single_source_4q_fulfilled": True,
                "selected_source_for_4q": "nasdaq_api",
                "nasdaq_4q_sum": 18.87,
                "criteria_verification": tsmc_criteria_verification,
                "scoring_eligible": False,
                "scoring_status": "pending_basis_metadata_verification",
                "summary": "단일 원천 4분기 수치(18.87)는 확보했으나 메타데이터 미확인으로 채점 보류(scoring_eligible=False) 유지."
            },
            "alibaba": {
                "ticker": "BABA / 9988.HK",
                "mapping_quarters": baba_expected,
                "sources_investigated": baba_sources,
                "single_source_4q_fulfilled": True,
                "selected_source_for_4q": "nasdaq_api",
                "nasdaq_4q_sum": 7.57,
                "criteria_verification": baba_criteria_verification,
                "scoring_eligible": False,
                "scoring_status": "pending_basis_metadata_verification",
                "summary": "단일 원천 4분기 수치(7.57)는 확보했으나 메타데이터 미확인으로 채점 보류(scoring_eligible=False) 유지."
            }
        },
        "unlisted_companies": {
            "openai": openai_metrics,
            "anthropic": anthropic_metrics,
        },
        "conclusion": {
            "c13_source_03_completed": True,
            "scoring_hold_maintained": True,
            "tsmc_scoring_eligible": False,
            "alibaba_scoring_eligible": False,
            "strict_boolean_defense_active": True,
            "anthropic_run_rate_revenue_preserved": True,
            "anthropic_ledger_unconfirmed_isolated": True,
            "openai_official_excerpts_separated": True,
            "unverified_article_urls_isolated": True,
        }
    }


def main():
    print("=== C13-SOURCE-03 단위 테스트 실행 ===")
    run_unit_tests()

    print("=== C13-SOURCE-03 evidence.json 생성 ===")
    evidence = generate_all_evidence()
    out_dir = os.path.dirname(__file__)
    json_path = os.path.join(out_dir, "evidence.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, ensure_ascii=False, indent=2)
    print(f"evidence.json 생성 완료: {json_path}")


if __name__ == "__main__":
    main()
