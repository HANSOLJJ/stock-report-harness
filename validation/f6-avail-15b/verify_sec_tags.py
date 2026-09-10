# SEC EDGAR 상장 12개사 companyfacts 태그 인벤토리 및 가용성 동적 검증 스크립트
"""
상장 12개사(META, NVDA, GOOGL, MSFT, AMZN, AAPL, ORCL, PLTR, TSLA, SPCX, TSM, BABA)의
SEC companyfacts 원자료 JSON을 파싱하여 매출 개념, 순이익, 영업이익, 전년 동기 비교 가능성을 검증합니다.
"""

import json
import os
import sys
from collections import defaultdict


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
            "note": "IFRS 전용 공시 (us-gaap 택소노미 부재)"
        }

    # 1. 매출 태그 존재 및 실제 사용 개념 (최근 2024-2026 공시 기준)
    rev_candidates = [
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "SalesRevenueNet"
    ]
    
    candidate_latest = {}
    candidate_counts = {}
    for rc in rev_candidates:
        if rc in us_gaap:
            units = us_gaap[rc].get("units", {})
            u_key = list(units.keys())[0] if units else None
            items = units.get(u_key, []) if u_key else []
            # form 10-Q, 10-K, 20-F 필터링
            filings = [it for it in items if it.get("form") in ("10-Q", "10-K", "20-F")]
            filings.sort(key=lambda x: (x.get("end") or "", x.get("filed") or ""))
            if filings:
                candidate_latest[rc] = filings[-1].get("end")
                candidate_counts[rc] = len(filings)

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
    # 최신 공시 제출건(accession)에서 당기와 전년 동기 기간이 동일 개념으로 보고되었는지 확인
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
            # 최신 공시에 당기 및 전기(전년 동기)가 2개 이상 포함되면 YoY 동일 개념 추출 가능
            if len(distinct_ends) >= 2:
                has_yoy_comparable_revenue = True
                yoy_concept_consistent = True

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
        print(f" - {ticker:5s} | US-GAAP: {res['us_gaap_present']} | Rev: {res['primary_revenue_concept']} | NetInc: {res['has_net_income']} | OpInc: {res['has_operating_income']} | YoY: {res['has_yoy_comparable_revenue']}")

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
    print("PASS: Test 1 (12개사 원자료 전수 검증 통과)\n")

    print("[TEST 2] 양성 대조 (합성 이상적 companyfacts 검증)")
    synthetic_ideal = {
        "cik": 9999999,
        "entityName": "Synthetic Ideal Corp",
        "facts": {
            "us-gaap": {
                "RevenueFromContractWithCustomerExcludingAssessedTax": {
                    "units": {
                        "USD": [
                            {"end": "2025-06-30", "val": 1000, "form": "10-Q", "filed": "2026-08-01", "accn": "0001-26-01"},
                            {"end": "2026-06-30", "val": 1200, "form": "10-Q", "filed": "2026-08-01", "accn": "0001-26-01"}
                        ]
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
    assert ideal_res["primary_revenue_concept"] == "RevenueFromContractWithCustomerExcludingAssessedTax"
    print("PASS: Test 2 (양성 대조 통과)\n")

    print("[TEST 3] 음성 변이 대조 (태그 제거 및 단일 기간 변이)")
    mutated = json.loads(json.dumps(synthetic_ideal))
    del mutated["facts"]["us-gaap"]["NetIncomeLoss"]
    del mutated["facts"]["us-gaap"]["OperatingIncomeLoss"]
    # 전기(2025-06-30) 항목을 삭제하여 단일 기간만 남김
    mutated["facts"]["us-gaap"]["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"] = [
        {"end": "2026-06-30", "val": 1200, "form": "10-Q", "filed": "2026-08-01", "accn": "0001-26-01"}
    ]
    mutated_res = evaluate_company_sec_facts(mutated)
    assert mutated_res["has_net_income"] is False, "Mutated must detect missing NetIncomeLoss"
    assert mutated_res["has_operating_income"] is False, "Mutated must detect missing OperatingIncomeLoss"
    assert mutated_res["has_yoy_comparable_revenue"] is False, "Mutated must detect lack of YoY comparative period"
    print("PASS: Test 3 (음성 변이 대조 통과)\n")

    print("ALL 3 VALIDATION TESTS PASSED DYNAMICALLY.")


if __name__ == "__main__":
    main()
