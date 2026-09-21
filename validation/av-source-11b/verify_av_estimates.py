# Alpha Vantage EARNINGS_ESTIMATES 스키마 및 F6 요구조건 정밀 검증 스크립트
"""
Alpha Vantage EARNINGS_ESTIMATES 엔드포인트 응답과 1:1 F6 기준 정밀 대조 검증기.
원자료 JSON을 동적으로 파싱하여 10개 평가 항목을 산출하고 검증합니다.
"""

import json
import os
import sys
from datetime import datetime


def evaluate_estimates_data(data: dict, reference_date_str: str = "2026-09-10") -> dict:
    """Alpha Vantage EARNINGS_ESTIMATES JSON 응답을 10개 F6 기준으로 평가합니다."""
    symbol = data.get("symbol")
    estimates = data.get("estimates", [])

    # 1. 12개사 커버리지
    # 데모 키 환경에서는 IBM만 조회 가능하며, 타 종목은 비데모 키 필요
    is_demo_single = (symbol == "IBM" and len(estimates) > 0)
    coverage_status = "unknown_demo_restricted" if is_demo_single else "unverified"

    # 분기/연간 분리
    quarterly_entries = [e for e in estimates if e.get("horizon") == "fiscal quarter"]
    yearly_entries = [e for e in estimates if e.get("horizon") == "fiscal year"]

    # 2. 향후 분기 수 (reference_date_str 이후 종료되는 분기 수)
    ref_date = datetime.strptime(reference_date_str, "%Y-%m-%d")
    future_quarters = []
    for q in quarterly_entries:
        q_date_str = q.get("date")
        if q_date_str:
            try:
                q_dt = datetime.strptime(q_date_str, "%Y-%m-%d")
                if q_dt >= ref_date:
                    future_quarters.append(q)
            except ValueError:
                pass

    forward_quarter_count = len(future_quarters)
    forward_quarters_meet_4 = (forward_quarter_count >= 4)

    # 3. 회계분기 식별 필드 (Q1, Q2, fiscalQuarter 등 명시적 분기 번호)
    has_explicit_quarter_field = False
    quarter_keys = {"fiscalQuarter", "quarter", "fiscal_quarter", "fiscal_period", "period"}
    for q in quarterly_entries:
        for k in quarter_keys:
            if k in q:
                has_explicit_quarter_field = True
                break

    # 4. 통화 (currency)
    has_currency = False
    currency_keys = {"currency", "financialCurrency", "reportCurrency", "currency_code"}
    if any(k in data for k in currency_keys):
        has_currency = True
    for e in estimates:
        if any(k in e for k in currency_keys):
            has_currency = True
            break

    # 5. 주식 기준 (share_basis: diluted vs basic)
    has_share_basis = False
    share_keys = {"share_basis", "diluted", "basic", "shareBasis"}
    for e in estimates:
        if any(k in e for k in share_keys):
            has_share_basis = True
            break

    # 6. 회계 기준 (accounting: GAAP vs Non-GAAP)
    has_accounting = False
    accounting_keys = {"accounting", "gaap", "non_gaap", "standard"}
    for e in estimates:
        if any(k in e for k in accounting_keys):
            has_accounting = True
            break

    # 7. asOf 스냅샷 시점
    has_as_of = False
    as_of_keys = {"asOf", "as_of", "snapshot_date", "last_updated", "updated_at"}
    if any(k in data for k in as_of_keys):
        has_as_of = True
    for e in estimates:
        if any(k in e for k in as_of_keys):
            has_as_of = True
            break

    # 8. 표본수 (sample size / analyst count)
    has_analyst_count = False
    sample_values = []
    for e in quarterly_entries:
        cnt = e.get("eps_estimate_analyst_count")
        if cnt is not None:
            try:
                val = float(cnt)
                if val > 0:
                    sample_values.append(val)
            except ValueError:
                pass
    has_analyst_count = (len(sample_values) > 0)

    # 9. min / max
    has_min_max = False
    min_max_found = 0
    for e in quarterly_entries:
        low = e.get("eps_estimate_low")
        high = e.get("eps_estimate_high")
        if low is not None and high is not None:
            try:
                float(low)
                float(high)
                min_max_found += 1
            except ValueError:
                pass
    has_min_max = (min_max_found > 0)

    # 10. 과거 시점 재현성 (Point-in-time)
    # API 파라미터 수준에서 as_of 쿼리 파라미터 부재 및 고정 시계열만 제공
    point_in_time_reproducible = False

    # 11. 단기 컨센서스 이동 및 리비전 데이터 (7/30/60/90일 전 평균치 및 7/30일 리비전)
    has_consensus_drift_90d = False
    drift_keys = [
        "eps_estimate_average_7_days_ago",
        "eps_estimate_average_30_days_ago",
        "eps_estimate_average_60_days_ago",
        "eps_estimate_average_90_days_ago"
    ]
    drift_found = 0
    for e in quarterly_entries:
        if all(k in e and e[k] is not None for k in drift_keys):
            drift_found += 1
    has_consensus_drift_90d = (drift_found > 0)

    return {
        "symbol": symbol,
        "total_estimates": len(estimates),
        "quarterly_count": len(quarterly_entries),
        "yearly_count": len(yearly_entries),
        "forward_quarter_count": forward_quarter_count,
        "forward_quarter_dates": [q.get("date") for q in future_quarters],
        "forward_quarters_meet_4": forward_quarters_meet_4,
        "has_explicit_quarter_field": has_explicit_quarter_field,
        "has_currency": has_currency,
        "has_share_basis": has_share_basis,
        "has_accounting": has_accounting,
        "has_as_of": has_as_of,
        "has_analyst_count": has_analyst_count,
        "has_min_max": has_min_max,
        "point_in_time_reproducible": point_in_time_reproducible,
        "has_consensus_drift_90d": has_consensus_drift_90d,
        "coverage_status": coverage_status,
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "_raw", "av_earnings_estimates_ibm_demo.json")

    print("[TEST 1] Raw IBM Demo Response Dynamic Evaluation")
    if not os.path.exists(raw_path):
        print(f"FAIL: raw file not found at {raw_path}")
        sys.exit(1)

    with open(raw_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    res = evaluate_estimates_data(raw_data, reference_date_str="2026-09-10")
    print(f" - Symbol: {res['symbol']}")
    print(f" - Total entries: {res['total_estimates']} (Quarterly: {res['quarterly_count']}, Yearly: {res['yearly_count']})")
    print(f" - Forward Quarters: {res['forward_quarter_count']} {res['forward_quarter_dates']}")
    print(f" - Forward Quarters >= 4: {res['forward_quarters_meet_4']} (Expected: False, only 2 future quarters)")
    print(f" - Explicit Quarter Identifier: {res['has_explicit_quarter_field']} (Expected: False, only date provided)")
    print(f" - Currency Field: {res['has_currency']} (Expected: False)")
    print(f" - Share Basis: {res['has_share_basis']} (Expected: False)")
    print(f" - Accounting Standard: {res['has_accounting']} (Expected: False)")
    print(f" - asOf Snapshot Timestamp: {res['has_as_of']} (Expected: False)")
    print(f" - Analyst Sample Size: {res['has_analyst_count']} (Expected: True)")
    print(f" - Min/Max Estimates: {res['has_min_max']} (Expected: True)")
    print(f" - Point-in-Time PIT Reproducibility: {res['point_in_time_reproducible']} (Expected: False)")

    assert res["symbol"] == "IBM", "Symbol must match IBM"
    assert res["forward_quarter_count"] == 2, f"Expected 2 forward quarters, got {res['forward_quarter_count']}"
    assert res["forward_quarters_meet_4"] is False, "Should not meet 4 forward quarters"
    assert res["has_explicit_quarter_field"] is False, "Explicit quarter identifier should be missing"
    assert res["has_currency"] is False, "Currency field should be missing"
    assert res["has_share_basis"] is False, "Share basis field should be missing"
    assert res["has_accounting"] is False, "Accounting standard field should be missing"
    assert res["has_as_of"] is False, "asOf timestamp should be missing"
    assert res["has_analyst_count"] is True, "Analyst count should be present"
    assert res["has_min_max"] is True, "Min/max estimates should be present"
    assert res["has_consensus_drift_90d"] is True, "90d consensus drift fields should be present"
    print("PASS: Test 1 (Real IBM Raw Evaluation passed all assertions)\n")

    print("[TEST 2] Positive Control (Synthetic Ideal Response)")
    synthetic_ideal = {
        "symbol": "IDEAL",
        "currency": "USD",
        "asOf": "2026-09-10T00:00:00Z",
        "estimates": [
            {
                "date": "2026-09-30",
                "fiscalQuarter": "Q3-2026",
                "horizon": "fiscal quarter",
                "eps_estimate_average": "1.00",
                "eps_estimate_low": "0.90",
                "eps_estimate_high": "1.10",
                "eps_estimate_analyst_count": "15",
                "eps_estimate_average_7_days_ago": "1.00",
                "eps_estimate_average_30_days_ago": "0.98",
                "eps_estimate_average_60_days_ago": "0.95",
                "eps_estimate_average_90_days_ago": "0.90",
                "share_basis": "diluted",
                "accounting": "non-gaap"
            },
            {
                "date": "2026-12-31",
                "fiscalQuarter": "Q4-2026",
                "horizon": "fiscal quarter",
                "eps_estimate_average": "1.10",
                "eps_estimate_low": "1.00",
                "eps_estimate_high": "1.20",
                "eps_estimate_analyst_count": "15",
                "eps_estimate_average_7_days_ago": "1.10",
                "eps_estimate_average_30_days_ago": "1.08",
                "eps_estimate_average_60_days_ago": "1.05",
                "eps_estimate_average_90_days_ago": "1.00",
                "share_basis": "diluted",
                "accounting": "non-gaap"
            },
            {
                "date": "2027-03-31",
                "fiscalQuarter": "Q1-2027",
                "horizon": "fiscal quarter",
                "eps_estimate_average": "1.20",
                "eps_estimate_low": "1.10",
                "eps_estimate_high": "1.30",
                "eps_estimate_analyst_count": "15",
                "eps_estimate_average_7_days_ago": "1.20",
                "eps_estimate_average_30_days_ago": "1.18",
                "eps_estimate_average_60_days_ago": "1.15",
                "eps_estimate_average_90_days_ago": "1.10",
                "share_basis": "diluted",
                "accounting": "non-gaap"
            },
            {
                "date": "2027-06-30",
                "fiscalQuarter": "Q2-2027",
                "horizon": "fiscal quarter",
                "eps_estimate_average": "1.30",
                "eps_estimate_low": "1.20",
                "eps_estimate_high": "1.40",
                "eps_estimate_analyst_count": "15",
                "eps_estimate_average_7_days_ago": "1.30",
                "eps_estimate_average_30_days_ago": "1.28",
                "eps_estimate_average_60_days_ago": "1.25",
                "eps_estimate_average_90_days_ago": "1.20",
                "share_basis": "diluted",
                "accounting": "non-gaap"
            }
        ]
    }
    ideal_res = evaluate_estimates_data(synthetic_ideal, reference_date_str="2026-09-10")
    assert ideal_res["forward_quarter_count"] == 4, "Ideal should have 4 quarters"
    assert ideal_res["forward_quarters_meet_4"] is True, "Ideal should pass forward_quarters_meet_4"
    assert ideal_res["has_explicit_quarter_field"] is True, "Ideal should pass has_explicit_quarter_field"
    assert ideal_res["has_currency"] is True, "Ideal should pass has_currency"
    assert ideal_res["has_share_basis"] is True, "Ideal should pass has_share_basis"
    assert ideal_res["has_accounting"] is True, "Ideal should pass has_accounting"
    assert ideal_res["has_as_of"] is True, "Ideal should pass has_as_of"
    assert ideal_res["has_consensus_drift_90d"] is True, "Ideal should pass has_consensus_drift_90d"
    print("PASS: Test 2 (Positive Control passed all assertions)\n")

    print("[TEST 3] Negative Mutation Control (Removing analyst count, min/max, and drift)")
    mutated = json.loads(json.dumps(synthetic_ideal))
    for q in mutated["estimates"]:
        del q["eps_estimate_analyst_count"]
        del q["eps_estimate_low"]
        del q["eps_estimate_high"]
        del q["eps_estimate_average_7_days_ago"]

    mutated_res = evaluate_estimates_data(mutated, reference_date_str="2026-09-10")
    assert mutated_res["has_analyst_count"] is False, "Mutated should detect missing analyst count"
    assert mutated_res["has_min_max"] is False, "Mutated should detect missing min/max"
    assert mutated_res["has_consensus_drift_90d"] is False, "Mutated should detect missing drift fields"
    print("PASS: Test 3 (Negative Mutation Control passed all assertions)\n")

    print("ALL 3 VALIDATION TESTS PASSED DYNAMICALLY.")


if __name__ == "__main__":
    main()
