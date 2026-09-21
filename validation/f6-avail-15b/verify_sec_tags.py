# SEC EDGAR 상장 12개사 companyfacts 태그 인벤토리 및 가용성 동적 검증 스크립트
"""
상장 12개사(META, NVDA, GOOGL, MSFT, AMZN, AAPL, ORCL, PLTR, TSLA, SPCX, TSM, BABA)의
SEC companyfacts 원자료 JSON을 파싱하여 매출 개념, 순이익, 영업이익, 전년 동기 비교 가능성을 검증합니다.
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime


def _parse_date(d_str: str):
    """YYYY-MM-DD 형식 문자열을 date 객체로 파싱합니다."""
    try:
        return datetime.strptime(d_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def evaluate_company_sec_facts(data: dict) -> dict:
    """단일 회사의 SEC companyfacts JSON을 파싱하여 4대 평가 항목을 산출합니다."""
    cik = str(data.get("cik", "")).zfill(10)
    entity_name = data.get("entityName", "")
    facts = data.get("facts", {})
    us_gaap = facts.get("us-gaap", {})
    ifrs_full = facts.get("ifrs-full", {})

    us_gaap_present = bool(us_gaap)
    ifrs_present = bool(ifrs_full)

    if not us_gaap_present:
        return {
            "cik": cik,
            "entity_name": entity_name,
            "us_gaap_present": False,
            "ifrs_present": ifrs_present,
            "ifrs_concept_count": len(ifrs_full),
            "primary_revenue_concept": None,
            "has_net_income": False,
            "has_operating_income": False,
            "has_yoy_comparable_revenue": False,
            "yoy_concept_consistent": False,
            "has_revenues_tag": False,
            "consecutive_4q": False,
            "fy_minus_3q": False,
            "note": "IFRS 전용 공시 (us-gaap 택소노미 부재)"
        }

    has_revenues_tag = ("Revenues" in us_gaap)

    # 1. 매출 태그 존재 및 실제 사용 개념 (최근 2024-2026 공시 기준)
    rev_candidates = [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet"
    ]
    
    candidate_latest = {}
    candidate_q = defaultdict(list)
    candidate_fy = defaultdict(list)
    
    for rc in rev_candidates:
        if rc in us_gaap:
            units = us_gaap[rc].get("units", {})
            for u_key, items in units.items():
                for it in items:
                    st = _parse_date(it.get("start"))
                    en = _parse_date(it.get("end"))
                    if not st or not en:
                        continue
                    days = (en - st).days
                    if 70 <= days <= 110:
                        candidate_q[rc].append(it)
                    elif 340 <= days <= 380:
                        candidate_fy[rc].append(it)
                filings = [it for it in items if it.get("form") in ("10-Q", "10-K", "20-F")]
                filings.sort(key=lambda x: (x.get("end") or "", x.get("filed") or ""))
                if filings:
                    candidate_latest[rc] = filings[-1].get("end")

    # 주 사용 개념 판별
    primary_concept = None
    if "RevenueFromContractWithCustomerExcludingAssessedTax" in candidate_latest and "Revenues" in candidate_latest:
        latest_contract = candidate_latest["RevenueFromContractWithCustomerExcludingAssessedTax"]
        latest_rev = candidate_latest["Revenues"]
        if latest_contract == latest_rev:
            primary_concept = "Both_Revenues_and_Contract"
        elif latest_contract > latest_rev:
            primary_concept = "RevenueFromContractWithCustomerExcludingAssessedTax"
        else:
            primary_concept = "Revenues"
    elif "RevenueFromContractWithCustomerExcludingAssessedTax" in candidate_latest:
        primary_concept = "RevenueFromContractWithCustomerExcludingAssessedTax"
    elif "Revenues" in candidate_latest:
        primary_concept = "Revenues"
    elif "SalesRevenueNet" in candidate_latest:
        primary_concept = "SalesRevenueNet"

    # 2. 순이익 (NetIncomeLoss)
    has_net_income = False
    net_income_count = 0
    if "NetIncomeLoss" in us_gaap:
        units = us_gaap["NetIncomeLoss"].get("units", {})
        u_key = list(units.keys())[0] if units else None
        items = units.get(u_key, []) if u_key else []
        net_income_count = len(items)
        has_net_income = (net_income_count > 0)

    # 3. 영업이익 (OperatingIncomeLoss)
    has_operating_income = False
    op_income_count = 0
    if "OperatingIncomeLoss" in us_gaap:
        units = us_gaap["OperatingIncomeLoss"].get("units", {})
        u_key = list(units.keys())[0] if units else None
        items = units.get(u_key, []) if u_key else []
        op_income_count = len(items)
        has_operating_income = (op_income_count > 0)

    # 4. 전년 동기를 동일 개념으로 추출 가능한지 (YoY 일관성 검증)
    test_concept = "RevenueFromContractWithCustomerExcludingAssessedTax" if primary_concept in (
        "RevenueFromContractWithCustomerExcludingAssessedTax", "Both_Revenues_and_Contract"
    ) else "Revenues"

    has_yoy_comparable_revenue = False
    yoy_concept_consistent = False

    if test_concept in us_gaap:
        units = us_gaap[test_concept].get("units", {})
        u_key = list(units.keys())[0] if units else None
        items = units.get(u_key, []) if u_key else []
        
        # 최신 filed 날짜의 filing 항목 추출
        by_accn = defaultdict(list)
        latest_filed = ""
        latest_accn = None
        for it in items:
            f = it.get("filed", "")
            accn = it.get("accn")
            if accn and f:
                by_accn[accn].append(it)
                if f > latest_filed:
                    latest_filed = f
                    latest_accn = accn
        
        if latest_accn and latest_accn in by_accn:
            latest_items = by_accn[latest_accn]
            distinct_ends = set(x.get("end") for x in latest_items if x.get("end"))
            if len(distinct_ends) >= 2:
                has_yoy_comparable_revenue = True
                yoy_concept_consistent = True

    # 5. TTM 조립 가능성 검증:
    # 5-1) 직접 4개 분기 연속 태깅 여부 (Q4 직접 태깅)
    # 현행 활성 개념 선정: 최근 분기가 존재하는 개념 우선
    best_concept = None
    best_q_end = ""
    best_end = ""
    for rc in rev_candidates:
        if rc in candidate_latest:
            q_ends = [it["end"] for it in candidate_q[rc]]
            max_q = max(q_ends) if q_ends else ""
            max_end = candidate_latest[rc]
            if (max_q, max_end) > (best_q_end, best_end):
                best_q_end = max_q
                best_end = max_end
                best_concept = rc

    active_eval_concept = best_concept or test_concept
    q_rows = candidate_q[active_eval_concept] if active_eval_concept else []
    fy_rows = candidate_fy[active_eval_concept] if active_eval_concept else []

    ends = sorted(set(_parse_date(it["end"]) for it in q_rows if _parse_date(it.get("end"))))
    last4 = ends[-4:]
    consecutive_4q = len(last4) == 4 and all(70 <= (last4[i + 1] - last4[i]).days <= 110 for i in range(3))

    # 5-2) FY - (Q1+Q2+Q3) 복원 가능성: 최신 연간(FY) 구간 안에 분기 3개 이상 존재
    fy_minus_3q = False
    if fy_rows:
        fy_rows.sort(key=lambda x: x["end"])
        latest_fy = fy_rows[-1]
        fs = _parse_date(latest_fy.get("start"))
        fe = _parse_date(latest_fy.get("end"))
        if fs and fe:
            inside = [it for it in q_rows if fs <= (_parse_date(it.get("start")) or fs) and (_parse_date(it.get("end")) or fe) <= fe]
            distinct_inside = set(it["end"] for it in inside if it.get("end"))
            fy_minus_3q = (len(distinct_inside) >= 3)

    return {
        "cik": cik,
        "entity_name": entity_name,
        "us_gaap_present": True,
        "ifrs_present": ifrs_present,
        "primary_revenue_concept": primary_concept,
        "candidate_latest": candidate_latest,
        "has_net_income": has_net_income,
        "net_income_count": net_income_count,
        "has_operating_income": has_operating_income,
        "op_income_count": op_income_count,
        "has_yoy_comparable_revenue": has_yoy_comparable_revenue,
        "yoy_concept_consistent": yoy_concept_consistent,
        "has_revenues_tag": has_revenues_tag,
        "consecutive_4q": consecutive_4q,
        "fy_minus_3q": fy_minus_3q,
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_dir = os.path.join(base_dir, "_raw")

    tickers_ciks = [
        ("META", "0001326801"),
        ("NVDA", "0001045810"),
        ("GOOGL", "0001652044"),
        ("MSFT", "0000789019"),
        ("AMZN", "0001018724"),
        ("AAPL", "0000320193"),
        ("ORCL", "0001341439"),
        ("PLTR", "0001321655"),
        ("TSLA", "0001318605"),
        ("SPCX", "0001181412"),
        ("TSM", "0001046179"),
        ("BABA", "0001577552")
    ]

    print("[TEST 1] 상장 12개사 SEC EDGAR companyfacts 원자료 전수 동적 검증")
    results = {}
    for ticker, cik in tickers_ciks:
        filename = f"CIK{cik}_{ticker}.json"
        filepath = os.path.join(raw_dir, filename)
        assert os.path.exists(filepath), f"Raw file missing: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            raw_json = json.load(f)
        res = evaluate_company_sec_facts(raw_json)
        results[ticker] = res
        print(f" - {ticker:5s} | US-GAAP: {str(res['us_gaap_present']):5s} | 4Q-dir: {str(res['consecutive_4q']):5s} | FY-3Q: {str(res['fy_minus_3q']):5s} | Has-Rev: {str(res['has_revenues_tag']):5s} | Rev: {res['primary_revenue_concept']}")

    # 1) TSM: US-GAAP 부재 및 IFRS 존재 확인
    assert results["TSM"]["us_gaap_present"] is False, "TSM must have no us-gaap"
    assert results["TSM"]["ifrs_present"] is True, "TSM must have ifrs-full"

    # 2) 11개 미국/외국 상장사: US-GAAP 존재, NetIncomeLoss 존재, OperatingIncomeLoss 존재
    us_gaap_tickers = [t for t in results if t != "TSM"]
    assert len(us_gaap_tickers) == 11, "Should have 11 US-GAAP filers"
    for t in us_gaap_tickers:
        r = results[t]
        assert r["us_gaap_present"] is True, f"{t} must have us-gaap"
        assert r["has_net_income"] is True, f"{t} must have NetIncomeLoss"
        assert r["has_operating_income"] is True, f"{t} must have OperatingIncomeLoss"
        assert r["has_yoy_comparable_revenue"] is True, f"{t} must have YoY comparable revenue in same filing"

    # 3) 개념별 실제 사용 분류 확인
    assert results["META"]["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert results["NVDA"]["primary_revenue_concept"] == "Revenues"
    assert results["GOOGL"]["primary_revenue_concept"] == "Revenues"
    assert results["MSFT"]["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert results["AMZN"]["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert results["AAPL"]["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert results["PLTR"]["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert results["SPCX"]["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    assert results["BABA"]["primary_revenue_concept"] == "Revenues"
    assert results["ORCL"]["primary_revenue_concept"] == "Both_Revenues_and_Contract"
    assert results["TSLA"]["primary_revenue_concept"] == "Both_Revenues_and_Contract"

    # 4) TTM 조립 가능성 및 Revenues 부재 정밀 단언 (재검토 반영)
    # 4-1) Q4 직접 연속 태깅: 0/12 (최신 연도 10-K 연간만 공시)
    assert sum(1 for r in results.values() if r["consecutive_4q"]) == 0, "Direct 4 consecutive quarters must be 0/12"

    # 4-2) FY - (Q1+Q2+Q3) 복원 경로: 정확히 9/12 (SPCX, TSM, BABA 제외 9개사)
    assert sum(1 for r in results.values() if r["fy_minus_3q"]) == 9, "TTM reconstruction via FY-(Q1+Q2+Q3) must be exactly 9/12"
    reconstructible = sorted([t for t, r in results.items() if r["fy_minus_3q"]])
    assert reconstructible == ["AAPL", "AMZN", "GOOGL", "META", "MSFT", "NVDA", "ORCL", "PLTR", "TSLA"]

    # 4-3) US-GAAP 기업 중 Revenues 태그 완전 부재: 정확히 3개사 (AMZN, PLTR, SPCX)
    missing_revenues = sorted([t for t, r in results.items() if r["us_gaap_present"] and not r["has_revenues_tag"]])
    assert missing_revenues == ["AMZN", "PLTR", "SPCX"], f"Missing Revenues must be AMZN, PLTR, SPCX (got {missing_revenues})"
    print("PASS: Test 1 (12개사 원자료 전수 검증 통과: Q4직접 0/12, TTM복원 9/12, Revenues부재 3사 확인)\n")

    print("[TEST 2] 양성 대조 (합성 이상적 companyfacts 검증)")
    synthetic_ideal = {
        "cik": 9999999,
        "entityName": "Synthetic Ideal Corp",
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {
                        "USD": [
                            {"start": "2025-01-01", "end": "2025-03-31", "val": 900, "form": "10-Q", "filed": "2025-05-01", "accn": "0001-25-01"},
                            {"start": "2025-04-01", "end": "2025-06-30", "val": 1000, "form": "10-Q", "filed": "2025-08-01", "accn": "0001-25-02"},
                            {"start": "2025-07-01", "end": "2025-09-30", "val": 1100, "form": "10-Q", "filed": "2025-11-01", "accn": "0001-25-03"},
                            {"start": "2025-01-01", "end": "2025-12-31", "val": 4200, "form": "10-K", "filed": "2026-02-15", "accn": "0001-26-01"},
                            {"start": "2025-04-01", "end": "2025-06-30", "val": 1000, "form": "10-Q", "filed": "2026-08-01", "accn": "0001-26-02"},
                            {"start": "2026-04-01", "end": "2026-06-30", "val": 1200, "form": "10-Q", "filed": "2026-08-01", "accn": "0001-26-02"}
                        ]
                    }
                },
                "Revenues": {
                    "units": {
                        "USD": [{"val": 4200, "end": "2025-12-31"}]
                    }
                },
                "NetIncomeLoss": {
                    "units": {"USD": [{"val": 200, "end": "2026-06-30"}]}
                },
                "OperatingIncomeLoss": {
                    "units": {"USD": [{"val": 300, "end": "2026-06-30"}]}
                }
            }
        }
    }
    ideal_res = evaluate_company_sec_facts(synthetic_ideal)
    assert ideal_res["us_gaap_present"] is True
    assert ideal_res["has_net_income"] is True
    assert ideal_res["has_operating_income"] is True
    assert ideal_res["has_yoy_comparable_revenue"] is True
    assert ideal_res["has_revenues_tag"] is True
    assert ideal_res["fy_minus_3q"] is True, "Synthetic ideal must support FY-(Q1+Q2+Q3) reconstruction"
    assert ideal_res["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    print("PASS: Test 2 (양성 대조 통과: FY-3Q 복원 양성 확인)\n")

    print("[TEST 3] 음성 변이 대조 (태그 제거 및 단일 기간 변이)")
    mutated = json.loads(json.dumps(synthetic_ideal))
    del mutated["facts"]["us-gaap"]["NetIncomeLoss"]
    del mutated["facts"]["us-gaap"]["OperatingIncomeLoss"]
    del mutated["facts"]["us-gaap"]["Revenues"]
    # 전기 분기 및 연간 항목을 삭제하여 복원 불가 단일 행만 남김
    mutated["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"] = [
        {"start": "2026-04-01", "end": "2026-06-30", "val": 1200, "form": "10-Q", "filed": "2026-08-01", "accn": "0001-26-02"}
    ]
    mutated_res = evaluate_company_sec_facts(mutated)
    assert mutated_res["has_net_income"] is False, "Mutated must detect missing NetIncomeLoss"
    assert mutated_res["has_operating_income"] is False, "Mutated must detect missing OperatingIncomeLoss"
    assert mutated_res["has_yoy_comparable_revenue"] is False, "Mutated must detect lack of YoY comparative period"
    assert mutated_res["has_revenues_tag"] is False, "Mutated must detect missing Revenues tag"
    assert mutated_res["fy_minus_3q"] is False, "Mutated must detect lack of FY-(Q1+Q2+Q3) reconstruction"
    print("PASS: Test 3 (음성 변이 대조 통과: 태그 결손 및 복원 불가 감지)\n")

    print("ALL 3 VALIDATION TESTS PASSED DYNAMICALLY.")


if __name__ == "__main__":
    main()
