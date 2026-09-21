# Yahoo 저장 원자료의 12개사 2A+2E 값 존재, 회계분기창, 기준 정합성 및 채점 가능 상태를 분리 검증하는 스크립트

import os
import sys
import json
import copy
import hashlib
import argparse
from pathlib import Path

# 12 listed scorecard companies
COMPANIES = [
    {"ticker": "META", "name": "Meta Platforms", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "NVDA", "name": "NVIDIA", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "GOOGL", "name": "Alphabet", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "MSFT", "name": "Microsoft", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "AMZN", "name": "Amazon", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "AAPL", "name": "Apple", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "ORCL", "name": "Oracle", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "PLTR", "name": "Palantir", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "TSLA", "name": "Tesla", "type": "US Common", "trade_cur": "USD"},
    {"ticker": "SPCX", "name": "SpaceX", "type": "US Common (IPO 2026-06-12)", "trade_cur": "USD"},
    {"ticker": "TSM", "name": "TSMC", "type": "TW ADR (5:1)", "trade_cur": "USD"},
    {"ticker": "BABA", "name": "Alibaba", "type": "CN ADS (8:1)", "trade_cur": "USD"}
]

def get_raw_dir(custom_path: Path | str | None = None) -> Path:
    if custom_path:
        p = Path(custom_path).resolve()
        if p.is_dir():
            return p
        raise FileNotFoundError(f"Specified raw directory not found: {custom_path}")

    # Candidate locations relative to this script
    script_dir = Path(__file__).resolve().parent
    cands = [
        script_dir / "_raw" / "yahoo",
        script_dir.parent / "f6h-source-batch-10" / "_raw" / "yahoo",
        script_dir.parents[3] / "worker" / "validation" / "f6h-source-batch-10" / "_raw" / "yahoo",
        Path("C:/Users/noble/orca/workspaces/stock-report-harness/worker/validation/f6h-source-batch-10/_raw/yahoo")
    ]
    for c in cands:
        if c.is_dir():
            return c
    raise FileNotFoundError(f"Worker _raw/yahoo directory not found. Checked: {[str(c) for c in cands]}")

def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fp:
        while chunk := fp.read(65536):
            h.update(chunk)
    return h.hexdigest()

import math

def is_finite_number(val) -> bool:
    """None, 문자열, 불리언(True/False), NaN, Inf는 거부하고 실제 유한 숫자(int, float)만 인정한다. 음수 EPS는 유효함."""
    if isinstance(val, bool):  # Python에서 bool은 int의 서브클래스이므로 엄격히 제외
        return False
    if isinstance(val, (int, float)):
        return not (math.isnan(val) or math.isinf(val))
    return False

def parse_ticker_data(data: dict, comp: dict, file_path: Path = None, sha256: str = None) -> dict:
    """단일 티커의 데이터를 파싱하고 4단계 검증 결과를 산출한다."""
    ticker = comp["ticker"]
    allowlisted = data.get("allowlisted", False)
    provider_note = data.get("note", "")
    
    # --- Stage 1: 원자료 값 존재 검증 (Raw Value Existence) ---
    ee = data.get("earnings_estimate") or {}
    q0 = ee.get("0q") or {}
    q1 = ee.get("+1q") or {}
    
    q0_avg = q0.get("avg") if isinstance(q0, dict) else None
    q1_avg = q1.get("avg") if isinstance(q1, dict) else None
    has_est_0q = is_finite_number(q0_avg)
    has_est_1q = is_finite_number(q1_avg)
    estimate_rows_count = int(has_est_0q) + int(has_est_1q)
    has_2e_values = (estimate_rows_count >= 2)
    
    ed = data.get("earnings_dates") or []
    # 유한 숫자인 Reported EPS만 유효 실적으로 인정 (문자열, None, NaN 거부, 음수는 유효 인정)
    valid_reported_rows = [
        r for r in ed 
        if isinstance(r, dict) and is_finite_number(r.get("Reported EPS"))
    ]
    
    # 발표일자 기준 중복 제거 및 분기 구분
    seen_dates = set()
    unique_reported_rows = []
    duplicate_row_count = 0
    for r in valid_reported_rows:
        d_key = r.get("Earnings Date")
        if d_key in seen_dates:
            duplicate_row_count += 1
        else:
            seen_dates.add(d_key)
            unique_reported_rows.append(r)
            
    actual_rows_count = len(valid_reported_rows)
    unique_actual_quarters = len(unique_reported_rows)
    # R3-04: 이력 내 확정 분기수 2개 이상 존재 여부
    has_2a_values = (unique_actual_quarters >= 2)
    
    value_existence_pass = (has_2a_values and has_2e_values)
    value_notes = []
    if not has_2a_values:
        value_notes.append(f"이력 내 확정 실적 분기 부족 (총 {actual_rows_count}행, 중복제외 {unique_actual_quarters}분기, 2A 최소 2분기 요건 미달)")
    else:
        value_notes.append(f"이력 내 확정 실적 {unique_actual_quarters}개 분기(2개 이상 존재) 및 전망 2E 유효 수치 충족")
    if not has_2e_values:
        value_notes.append(f"유효 전망 분기 부족 (유한수치 {estimate_rows_count}개, 2E 요건 미달)")
    if duplicate_row_count > 0:
        value_notes.append(f"중복 실적행 {duplicate_row_count}건 감지")
        
    # 음수 실적 확인 (음수는 유효 실적임)
    negative_actuals = [r["Reported EPS"] for r in unique_reported_rows if r["Reported EPS"] < 0]
    if negative_actuals:
        value_notes.append(f"음수 실적 {len(negative_actuals)}건 ({negative_actuals[:2]})")
        
    # --- Stage 2: 회계분기창 특정 검증 (Fiscal Quarter Window Specificity: R3-02 & R3-05) ---
    # 2A 대상 확정 실적행 전체와 2E(0q, +1q) 전체의 회계기간 필드를 교차 검증
    PERIOD_KEYS = {"period_end", "period_end_date", "fiscal_period", "fiscal_quarter", "quarter", "quarter_end"}
    EST_PERIOD_KEYS = {"fiscal_period", "quarter_label", "calendar_quarter", "period_end", "quarter"}
    
    # 2A 실적행의 기간 필드 검사 (Reported EPS가 유효한 확정 실적 행들 대상)
    actual_rows_with_period = sum(
        1 for r in valid_reported_rows 
        if any(k.lower() in PERIOD_KEYS for k in r.keys())
    )
    # 미발표 예정행(Reported EPS null)에 기간 필드가 있는지 별도 검사
    unannounced_rows_with_period = sum(
        1 for r in ed 
        if isinstance(r, dict) and not is_finite_number(r.get("Reported EPS")) and any(k.lower() in PERIOD_KEYS for k in r.keys())
    )
    
    if len(valid_reported_rows) < 2:
        actual_period_status = "insufficient_actual_rows"
    elif actual_rows_with_period == 0:
        if unannounced_rows_with_period > 0:
            actual_period_status = "conflict_unannounced_row_only"
        else:
            actual_period_status = "missing"
    elif actual_rows_with_period < len(valid_reported_rows):
        actual_period_status = "conflict_partial_missing"
    else:
        actual_period_status = "present"
        
    # 2E 전망행의 기간 필드 검사 (0q 및 +1q 양쪽 모두 검사)
    q0_has_period = bool(isinstance(q0, dict) and any(k.lower() in EST_PERIOD_KEYS for k in q0.keys()))
    q1_has_period = bool(isinstance(q1, dict) and any(k.lower() in EST_PERIOD_KEYS for k in q1.keys()))
    
    if q0_has_period and q1_has_period:
        estimate_period_status = "present"
    elif q0_has_period or q1_has_period:
        estimate_period_status = "conflict_partial_missing"
    else:
        estimate_period_status = "missing"
        
    quarter_window_verifiable = bool(
        actual_period_status == "present" and 
        estimate_period_status == "present" and 
        unique_actual_quarters >= 2
    )
    
    # R3-05: 입력 상태에 따른 동적 notes 생성
    quarter_window_notes = []
    if actual_period_status == "conflict_unannounced_row_only":
        quarter_window_notes.append("실적 발표 예정 행(Reported EPS null)에만 기간 표기되고 확정 실적행에는 부재 (conflict)")
    elif actual_period_status == "conflict_partial_missing":
        quarter_window_notes.append("실적(2A) 일부 행에만 기간 표기되고 타 행에 누락됨 (conflict)")
    elif actual_period_status == "missing":
        quarter_window_notes.append("earnings_dates는 실적 발표일(Announcement Date)이며 회계기간 종료일(Period End) 미표기")
    elif actual_period_status == "insufficient_actual_rows":
        quarter_window_notes.append(f"확정 실적행 부족({len(valid_reported_rows)}건)으로 회계분기창 특정 불가")
    elif actual_period_status == "present":
        quarter_window_notes.append("실적(2A) 확정 행 전반에 회계기간 종료일/분기 레이블 표기 확인")
        
    if estimate_period_status == "conflict_partial_missing":
        quarter_window_notes.append("전망치(2E) 0q와 +1q 간 회계기간 필드 불일치/누락 감지 (conflict)")
    elif estimate_period_status == "missing":
        quarter_window_notes.append("0q/+1q는 상대적 오프셋이며 페이로드 내 구체적 회계분기 레이블(예: FY2026Q3) 부재")
    elif estimate_period_status == "present":
        quarter_window_notes.append("전망치(2E: 0q, +1q)에 구체적 회계분기 레이블 표기 확인")
        
    if not quarter_window_verifiable:
        quarter_window_notes.append("외부 회계캘린더(결산월 매핑) 없이는 Yahoo 단독으로 회계분기창 특정 불가")
    else:
        quarter_window_notes.append("연속 회계분기창(2A+2E) 객관적 특정 완료")
        
    # --- Stage 3: 기준 검증 (Basis, Accounting & Currency Alignment: R3-01, R3-03, R3-04) ---
    accounting_standard = "Unspecified (GAAP/Non-GAAP 미표기)"
    has_accounting_standard = False
    has_as_of = False
    
    basis_info = data.get("basis") or {}
    raw_trade_currency = basis_info.get("currency")
    ref_trade_currency = comp.get("trade_cur")
    
    # 거래 통화 상태 판정
    if not raw_trade_currency or not isinstance(raw_trade_currency, str) or not raw_trade_currency.strip():
        raw_trade_currency = "UNKNOWN"
        trade_currency_status = "missing"
    elif raw_trade_currency != ref_trade_currency:
        trade_currency_status = "conflict"
    else:
        trade_currency_status = "matched"
        
    effective_trade_currency = raw_trade_currency
    
    # R3-03: basis.financialCurrency 파싱
    raw_financial_currency = basis_info.get("financialCurrency")
    if not raw_financial_currency or not isinstance(raw_financial_currency, str) or not raw_financial_currency.strip():
        raw_financial_currency = "UNKNOWN"
        financial_currency_status = "missing"
    elif raw_financial_currency != raw_trade_currency:
        financial_currency_status = "differs_unverified_conversion"
    else:
        financial_currency_status = "matched"
    
    # 2E 전망 통화
    est_cur_0q = q0.get("currency") if isinstance(q0, dict) else None
    est_cur_1q = q1.get("currency") if isinstance(q1, dict) else None
    est_currency = est_cur_0q if (est_cur_0q == est_cur_1q and est_cur_0q is not None) else f"{est_cur_0q}/{est_cur_1q}"
    
    # R3-04: 전망치 통화와 거래통화 매칭 여부 (estimate_currency_match)
    estimate_currency_match = (
        isinstance(est_cur_0q, str) and isinstance(est_cur_1q, str) and
        est_cur_0q == est_cur_1q and
        effective_trade_currency != "UNKNOWN" and
        est_cur_0q == effective_trade_currency
    )
    
    # R3-01 & R3-03: 종합 통화 일치 (currency_match)
    # 1) 거래통화가 참조통화(USD)와 충돌(conflict)하거나 누락(missing)되지 않아야 함
    # 2) 전망 통화가 거래통화와 일치해야 함
    # 3) 본사 재무통화(financialCurrency)가 거래통화와 일치하거나 환산 근거가 검증되어야 함 (TSM은 TWD!=USD이므로 불일치)
    currency_match = bool(
        trade_currency_status == "matched" and
        estimate_currency_match and
        financial_currency_status == "matched"
    )
    
    basis_notes = []
    if trade_currency_status == "conflict":
        basis_notes.append(f"원자료 거래 통화({raw_trade_currency})와 참조 통화({ref_trade_currency}) 충돌 (conflict)")
    elif trade_currency_status == "missing":
        basis_notes.append("원자료 거래 통화(basis.currency) 누락 (UNKNOWN)")
        
    if financial_currency_status == "differs_unverified_conversion":
        basis_notes.append(f"본사 재무통화({raw_financial_currency})와 거래통화({raw_trade_currency}) 불일치 및 환산 근거 미확인")
    elif financial_currency_status == "missing":
        basis_notes.append("본사 재무통화(basis.financialCurrency) 누락 (UNKNOWN)")
        
    if not estimate_currency_match:
        basis_notes.append(f"전망 통화({est_currency})와 거래 통화({effective_trade_currency}) 불일치")
        
    # R3-04: 2A 통화 미표기 명시
    basis_notes.append("earnings_dates Reported EPS 통화 필드 부재(미표기)")
    
    if comp["type"].startswith("TW ADR"):
        basis_notes.append("ADR 5:1 보통주 변환 비율 및 본사 통화(TWD) 환산 근거 미확인")
    if comp["type"].startswith("CN ADS"):
        basis_notes.append("ADS 8:1 보통주 변환 비율 및 본사 통화(CNY) 환산 근거 미확인")
    if comp["type"].startswith("US Common"):
        basis_notes.append("일반주 unit_ok 자동 참 지정 금지 (발행주식수 및 기준 미확인)")
        
    # 표본 수 및 min/max
    has_analyst_n = bool(
        isinstance(q0, dict) and isinstance(q1, dict) and
        is_finite_number(q0.get("numberOfAnalysts")) and is_finite_number(q1.get("numberOfAnalysts"))
    )
    has_min_max = bool(
        isinstance(q0, dict) and isinstance(q1, dict) and
        is_finite_number(q0.get("low")) and is_finite_number(q0.get("high")) and
        is_finite_number(q1.get("low")) and is_finite_number(q1.get("high"))
    )
    
    # R3-01: basis_verification_pass에 trade_currency_status 및 financial_currency_status 반영
    basis_verification_pass = bool(
        currency_match and 
        trade_currency_status == "matched" and 
        financial_currency_status == "matched" and 
        has_accounting_standard and 
        has_as_of
    )
    
    # --- Stage 4: 채점 가능 상태 (Scoring Eligibility) ---
    scoring_eligible = bool(
        value_existence_pass and 
        quarter_window_verifiable and 
        basis_verification_pass and 
        allowlisted
    )
    
    scoring_reasons = []
    if not allowlisted:
        scoring_reasons.append("Yahoo는 v1.6 allowlist 미등재 원천 (Personal use only, 상용 약관 선행 검토 미완료)")
    if not value_existence_pass:
        scoring_reasons.append(f"값 행수 요건 미달 (실적 {unique_actual_quarters}분기, 전망 {estimate_rows_count}분기)")
    if not quarter_window_verifiable:
        scoring_reasons.append("단독 페이로드로 회계분기창 특정 불가")
    if trade_currency_status != "matched":
        scoring_reasons.append(f"원자료 거래통화 충돌/누락 ({trade_currency_status})")
    if financial_currency_status != "matched":
        scoring_reasons.append(f"본사 재무통화 환산 근거 미확인 ({raw_financial_currency} != {raw_trade_currency})")
    if not estimate_currency_match:
        scoring_reasons.append(f"전망 통화 불일치 ({est_currency} != {effective_trade_currency})")
    if not has_accounting_standard:
        scoring_reasons.append("회계기준(GAAP/Non-GAAP) 미표기")
    if not has_as_of:
        scoring_reasons.append("asOf 시점 타임스탬프 부재")
        
    return {
        "ticker": ticker,
        "company_name": comp["name"],
        "company_type": comp["type"],
        "raw_file": {
            "rel_path": f"_raw/yahoo/{ticker}.json",
            "abs_path": str(file_path) if file_path else "in_memory",
            "sha256": sha256 or "in_memory"
        },
        "stage1_raw_values": {
            "actual_count": actual_rows_count,
            "unique_actual_quarters": unique_actual_quarters,
            "estimate_count": estimate_rows_count,
            "duplicate_row_count": duplicate_row_count,
            "has_2a": has_2a_values,
            "has_2a_in_history": has_2a_values,
            "has_2e": has_2e_values,
            "pass": value_existence_pass,
            "notes": "; ".join(value_notes)
        },
        "stage2_quarter_window": {
            "dates_type": "Announcement Date (발표일자)",
            "estimate_keys_type": "Relative Offset (0q, +1q)",
            "actual_period_status": actual_period_status,
            "estimate_period_status": estimate_period_status,
            "has_explicit_fiscal_period": (actual_period_status == "present"),
            "specific_fiscal_quarters_identifiable": quarter_window_verifiable,
            "pass": quarter_window_verifiable,
            "notes": "; ".join(quarter_window_notes)
        },
        "stage3_basis_metadata": {
            "accounting_standard": accounting_standard,
            "as_of_timestamp": None,
            "raw_trade_currency": raw_trade_currency,
            "ref_trade_currency": ref_trade_currency,
            "trade_currency_status": trade_currency_status,
            "raw_financial_currency": raw_financial_currency,
            "financial_currency_status": financial_currency_status,
            "estimate_currency": est_currency,
            "estimate_currency_match": estimate_currency_match,
            "actual_currency_status": "unspecified_in_payload",
            "currency_match": currency_match,
            "sample_size_provided": has_analyst_n,
            "sample_size_details": f"0q: {q0.get('numberOfAnalysts')}명, +1q: {q1.get('numberOfAnalysts')}명" if has_analyst_n else "미제공",
            "min_max_provided": has_min_max,
            "min_max_details": f"0q: [{q0.get('low')}, {q0.get('high')}], +1q: [{q1.get('low')}, {q1.get('high')}]" if has_min_max else "미제공",
            "pass": basis_verification_pass,
            "notes": "; ".join(basis_notes)
        },
        "stage4_scoring_status": {
            "allowlisted": allowlisted,
            "scoring_eligible": scoring_eligible,
            "verdict": "PASS" if scoring_eligible else "FAIL",
            "blocking_reasons": scoring_reasons
        }
    }

def verify_yahoo_evidence(raw_dir: Path = None, ticker_overrides: dict = None) -> dict:
    if raw_dir is None:
        raw_dir = get_raw_dir()
    else:
        raw_dir = Path(raw_dir).resolve()
        
    results = []
    for comp in COMPANIES:
        ticker = comp["ticker"]
        if ticker_overrides and ticker in ticker_overrides:
            data = ticker_overrides[ticker]
            file_path = None
            sha256 = "override_in_memory"
        else:
            file_path = raw_dir / f"{ticker}.json"
            if not file_path.is_file():
                results.append({
                    "ticker": ticker,
                    "file_exists": False,
                    "error": f"File not found: {file_path}"
                })
                continue
            sha256 = compute_sha256(file_path)
            with open(file_path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                
        res = parse_ticker_data(data, comp, file_path, sha256)
        results.append(res)
        
    total_companies = len(COMPANIES)
    stage1_passes = sum(1 for r in results if r.get("stage1_raw_values", {}).get("pass"))
    stage2_passes = sum(1 for r in results if r.get("stage2_quarter_window", {}).get("pass"))
    currency_passes = sum(1 for r in results if r.get("stage3_basis_metadata", {}).get("currency_match"))
    estimate_currency_passes = sum(1 for r in results if r.get("stage3_basis_metadata", {}).get("estimate_currency_match"))
    stage4_passes = sum(1 for r in results if r.get("stage4_scoring_status", {}).get("scoring_eligible"))
    
    # R2-02: SPCX 및 BABA 상세에서 동적으로 요약 산출 (하드코딩 상수 제거)
    spcx_res = next((r for r in results if r["ticker"] == "SPCX"), None)
    summary_spcx = {}
    if spcx_res and "stage1_raw_values" in spcx_res:
        summary_spcx = {
            "actual_count": spcx_res["stage1_raw_values"]["actual_count"],
            "unique_actual_quarters": spcx_res["stage1_raw_values"]["unique_actual_quarters"],
            "estimate_count": spcx_res["stage1_raw_values"]["estimate_count"],
            "duplicate_rows": spcx_res["stage1_raw_values"]["duplicate_row_count"],
            "stage1_pass": spcx_res["stage1_raw_values"]["pass"],
            "status": spcx_res["stage1_raw_values"]["notes"]
        }
        
    baba_res = next((r for r in results if r["ticker"] == "BABA"), None)
    summary_baba = {}
    if baba_res and "stage1_raw_values" in baba_res:
        summary_baba = {
            "stage1_pass": baba_res["stage1_raw_values"]["pass"],
            "estimate_currency": baba_res["stage3_basis_metadata"]["estimate_currency"],
            "raw_trade_currency": baba_res["stage3_basis_metadata"]["raw_trade_currency"],
            "ref_trade_currency": baba_res["stage3_basis_metadata"]["ref_trade_currency"],
            "currency_match": baba_res["stage3_basis_metadata"]["currency_match"],
            "status": baba_res["stage3_basis_metadata"]["notes"]
        }

    summary = {
        "task_id": "F6H-SOURCES-02-R1",
        "description": "Yahoo 저장 원자료 12개사 4단계 정밀 검증 (R3 보완: 통화 충돌·financialCurrency·전 행 분기창·동적notes 반영)",
        "raw_source_path": str(raw_dir),
        "total_companies": total_companies,
        "stage1_raw_value_pass_count": f"{stage1_passes}/{total_companies}",
        "stage2_quarter_window_pass_count": f"{stage2_passes}/{total_companies}",
        "stage3_currency_match_count": f"{currency_passes}/{total_companies}",
        "stage3_estimate_currency_match_count": f"{estimate_currency_passes}/{total_companies}",
        "stage4_scoring_eligible_count": f"{stage4_passes}/{total_companies}",
        "spcx_details": summary_spcx,
        "baba_details": summary_baba,
        "retraction_confirmations": [
            "Yahoo 전면 401 차단 및 0/12 단정 공식 철회 (저장자료에서 11/12 값 존재 확인)",
            "하드코딩 분기문 판정 공식 철회 (worker 저장 원응답 직접 파싱)",
            "Yahoo와 Valley를 별도 원천으로 분리 (Valley는 v1.5 정적 기준선, Yahoo는 yfinance 저장 원자료)",
            "단일 공급원의 다중 엔드포인트 허용 (동일 발행 주체의 복수 endpoint 조회 허용)",
            "일반주 unit_ok=True 자동 지정 철회 (발행주식수 및 기준 미확인 상태로 분류)",
            "IPO 상장 전 실적 부재 단정 및 유료 B2B만 가능하다는 단정 철회 (미검증으로 분류)"
        ]
    }
    
    return {
        "summary": summary,
        "results": results
    }

def run_self_verification_tests(output: dict):
    """설계진행 R3-01~05 지침에 맞춰 입력 변화 대응 및 결함 수정 여부를 포괄 검증한다."""
    results = output["results"]
    summary = output["summary"]
    raw_dir = Path(summary["raw_source_path"])
    
    # [Test 1] 12개사 전체 파일 존재 및 SHA256 해시 생성 검증
    assert len(results) == 12, "12개사 전체 결과가 생성되어야 함"
    for r in results:
        assert r["raw_file"]["sha256"] and len(r["raw_file"]["sha256"]) == 64, f"{r['ticker']} SHA256 해시 오류"
    print("[Direct Test 1 PASS] 12개사 전체 원자료 파일 존재 및 SHA-256 해시 기록 확인 완료")
    
    # [Test 2] 동일 입력 반복 2회 실행 결과 완전 일치 검증 (결정론적 재현성)
    out2 = verify_yahoo_evidence(raw_dir=raw_dir)
    assert json.dumps(output, sort_keys=True) == json.dumps(out2, sort_keys=True), "동일 입력 2회 실행 결과가 바이트 단위로 일치해야 함"
    print("[Direct Test 2 PASS] 동일 입력 반복 2회 실행 결과 완전 일치(결정론적 재현성) 확인 완료")
    
    # [Test 3: R2-01 & R3-01] 통화 변경 및 누락 입력 변이 대응 검증
    meta_path = raw_dir / "META.json"
    with open(meta_path, "r", encoding="utf-8") as fp:
        meta_data_orig = json.load(fp)
        
    # (3-1) META basis.currency를 KRW로 변경 시 conflict 및 match=False 검증
    meta_krw = copy.deepcopy(meta_data_orig)
    meta_krw["basis"]["currency"] = "KRW"
    res_krw = parse_ticker_data(meta_krw, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_krw["stage3_basis_metadata"]["raw_trade_currency"] == "KRW", "raw_trade_currency가 KRW로 파싱되어야 함"
    assert res_krw["stage3_basis_metadata"]["trade_currency_status"] == "conflict", "참조통화(USD)와 충돌(conflict)이어야 함"
    assert res_krw["stage3_basis_metadata"]["currency_match"] is False, "KRW와 USD는 불일치(False)여야 함"
    assert res_krw["stage3_basis_metadata"]["pass"] is False, "Stage 3 pass도 False여야 함"
    
    # (3-2) META basis.currency 누락 시 UNKNOWN 및 match=False 검증
    meta_missing_cur = copy.deepcopy(meta_data_orig)
    meta_missing_cur["basis"].pop("currency", None)
    res_missing = parse_ticker_data(meta_missing_cur, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_missing["stage3_basis_metadata"]["raw_trade_currency"] == "UNKNOWN", "누락 시 UNKNOWN이어야 함"
    assert res_missing["stage3_basis_metadata"]["trade_currency_status"] == "missing", "status가 missing이어야 함"
    assert res_missing["stage3_basis_metadata"]["currency_match"] is False, "UNKNOWN 통화는 match=False여야 함"
    assert res_missing["stage3_basis_metadata"]["pass"] is False, "Stage 3 pass도 False여야 함"
    
    # (3-3: R3-01 핵심) META 거래·전망 통화를 함께 KRW로 변경 시: conflict 감지 및 currency_match=False
    meta_all_krw = copy.deepcopy(meta_data_orig)
    meta_all_krw["basis"]["currency"] = "KRW"
    for k in ("0q", "+1q"):
        meta_all_krw["earnings_estimate"][k]["currency"] = "KRW"
    res_all_krw = parse_ticker_data(meta_all_krw, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_all_krw["stage3_basis_metadata"]["trade_currency_status"] == "conflict", "참조통화(USD)와 충돌(conflict)이어야 함"
    assert res_all_krw["stage3_basis_metadata"]["currency_match"] is False, "원자료가 참조통화와 conflict이면 currency_match는 False여야 함"
    assert res_all_krw["stage3_basis_metadata"]["pass"] is False, "Stage 3 pass는 False여야 함"
    assert res_all_krw["stage4_scoring_status"]["scoring_eligible"] is False, "Stage 4 scoring_eligible도 False여야 함"
    print("[Direct Test 3 PASS] R2-01 & R3-01: 통화 변경/누락 및 거래·전망 동시 KRW 변이 시 conflict/match=False 검증 완료")
    
    # [Test 4: R2-03] 비수치 값(문자열, None, NaN) 거부 및 음수 EPS 정상 인정 검증
    meta_str = copy.deepcopy(meta_data_orig)
    meta_str["earnings_estimate"]["0q"]["avg"] = "NOT_A_NUMBER"
    res_str = parse_ticker_data(meta_str, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_str["stage1_raw_values"]["has_2e"] is False, "NOT_A_NUMBER 문자열은 2E로 인정되지 않아야 함"
    assert res_str["stage1_raw_values"]["pass"] is False, "문자열 avg 입력 시 Stage 1 FAIL이어야 함"
    
    meta_bool = copy.deepcopy(meta_data_orig)
    meta_bool["earnings_estimate"]["0q"]["avg"] = True
    res_bool = parse_ticker_data(meta_bool, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_bool["stage1_raw_values"]["pass"] is False, "bool True avg 입력 시 Stage 1 FAIL이어야 함"
    
    meta_nan = copy.deepcopy(meta_data_orig)
    meta_nan["earnings_estimate"]["0q"]["avg"] = float("nan")
    res_nan = parse_ticker_data(meta_nan, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_nan["stage1_raw_values"]["pass"] is False, "NaN avg 입력 시 Stage 1 FAIL이어야 함"
    
    # 음수 EPS 검증: SPCX의 -0.09는 유효 숫자로 카운트되어야 함
    spcx_path = raw_dir / "SPCX.json"
    with open(spcx_path, "r", encoding="utf-8") as fp:
        spcx_data = json.load(fp)
    res_spcx = parse_ticker_data(spcx_data, next(c for c in COMPANIES if c["ticker"] == "SPCX"))
    assert res_spcx["stage1_raw_values"]["actual_count"] == 1, "음수 EPS(-0.09)는 결측되지 않고 1개로 유효 카운트되어야 함"
    assert is_finite_number(-0.09) is True, "음수는 유한 숫자로 판정되어야 함"
    assert is_finite_number("NOT_A_NUMBER") is False, "문자열은 거부되어야 함"
    assert is_finite_number(float("nan")) is False, "NaN은 거부되어야 함"
    assert is_finite_number(True) is False, "bool True는 숫자로 인정되지 않아야 함"
    print("[Direct Test 4 PASS] R2-03: 비수치 문자열/bool/NaN 거부 및 음수 EPS 정상 유효 인정 검증 완료")
    
    # [Test 5: R2-02] 중복 행 감지 및 요약-상세 동적 일치 검증
    spcx_dup = copy.deepcopy(spcx_data)
    actual_row = next(r for r in spcx_dup["earnings_dates"] if r.get("Reported EPS") is not None)
    spcx_dup["earnings_dates"].append(copy.deepcopy(actual_row))
    
    out_dup = verify_yahoo_evidence(raw_dir=raw_dir, ticker_overrides={"SPCX": spcx_dup})
    spcx_dup_res = next(r for r in out_dup["results"] if r["ticker"] == "SPCX")
    assert spcx_dup_res["stage1_raw_values"]["actual_count"] == 2, "행수는 2여야 함"
    assert spcx_dup_res["stage1_raw_values"]["unique_actual_quarters"] == 1, "중복 제거 후 분기수는 1이어야 함"
    assert spcx_dup_res["stage1_raw_values"]["duplicate_row_count"] == 1, "중복행 1건 감지되어야 함"
    assert spcx_dup_res["stage1_raw_values"]["has_2a"] is False, "중복으로 2행이 되어도 2A(서로 다른 2분기) 미달이어야 함"
    
    summary_spcx = out_dup["summary"]["spcx_details"]
    assert summary_spcx["actual_count"] == 2, "요약의 actual_count도 상세와 동일하게 2로 동적 산출되어야 함"
    assert summary_spcx["unique_actual_quarters"] == 1, "요약의 unique_actual_quarters도 1이어야 함"
    print("[Direct Test 5 PASS] R2-02: 중복 행 감지 및 요약-상세 동적 일치(상수 모순 제거) 검증 완료")
    
    # [Test 6: R3-02 & R3-05] 회계기간 필드 부분 부여(P7/P8) 및 동적 notes 검증
    # (6-1: P7) ed[0](Reported EPS null)에만 period_end, 0q에만 fiscal_period -> s2_pass는 False여야 함
    meta_p7 = copy.deepcopy(meta_data_orig)
    meta_p7["earnings_dates"][0]["period_end"] = "2026-09-30"
    meta_p7["earnings_estimate"]["0q"]["fiscal_period"] = "2026Q3"
    res_p7 = parse_ticker_data(meta_p7, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_p7["stage2_quarter_window"]["pass"] is False, "P7: 미발표행에만 period_end가 있고 +1q에 누락 시 stage2는 False여야 함"
    assert "conflict" in res_p7["stage2_quarter_window"]["notes"], "P7 notes에 conflict가 반영되어야 함"
    
    # (6-2: P8) ed[1]에만 period_end, 0q에만 fiscal_period -> s2_pass는 False여야 함
    meta_p8 = copy.deepcopy(meta_data_orig)
    meta_p8["earnings_dates"][1]["period_end"] = "2026-06-30"
    meta_p8["earnings_estimate"]["0q"]["fiscal_period"] = "2026Q3"
    res_p8 = parse_ticker_data(meta_p8, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert res_p8["stage2_quarter_window"]["pass"] is False, "P8: 일부 행에만 period_end가 있으면 stage2는 False여야 함"
    assert "conflict" in res_p8["stage2_quarter_window"]["notes"], "P8 notes에 conflict가 반영되어야 함"
    
    # (6-3: R3-05) 원본 notes와 P7 notes가 서로 달라야 함 (고정 문자열 탈피)
    meta_orig_res = parse_ticker_data(meta_data_orig, next(c for c in COMPANIES if c["ticker"] == "META"))
    assert meta_orig_res["stage2_quarter_window"]["notes"] != res_p7["stage2_quarter_window"]["notes"], "notes가 입력에 따라 동적으로 달라져야 함"
    print("[Direct Test 6 PASS] R3-02 & R3-05: 회계기간 부분 부여 입력(P7/P8) 대응 및 동적 notes 검증 완료")
    
    # [Test 7: R3-03, R3-04 & R2-04] financialCurrency 불일치(TSM), 2A 통화미표기, 12개사 실측 검증
    # (7-1: R3-03) TSM: basis.currency=USD, financialCurrency=TWD -> currency_match=False
    tsm = next(r for r in results if r["ticker"] == "TSM")
    assert tsm["stage3_basis_metadata"]["raw_trade_currency"] == "USD", "TSM 거래통화는 USD"
    assert tsm["stage3_basis_metadata"]["raw_financial_currency"] == "TWD", "TSM 재무통화는 TWD"
    assert tsm["stage3_basis_metadata"]["financial_currency_status"] == "differs_unverified_conversion", "TSM은 환산근거 미확인"
    assert tsm["stage3_basis_metadata"]["currency_match"] is False, "TSM은 통화 불일치로 집계되어야 함"
    
    # (7-2) BABA: financialCurrency=CNY, 0q=CNY -> currency_match=False, stage1=True
    baba = next(r for r in results if r["ticker"] == "BABA")
    assert baba["stage1_raw_values"]["pass"] is True, "BABA는 1단계 값 존재 PASS"
    assert baba["stage3_basis_metadata"]["currency_match"] is False, "BABA는 3단계 통화 불일치 FAIL"
    
    # (7-3: R3-04) 2A 통화 필드 부재 상태 확인
    assert tsm["stage3_basis_metadata"]["actual_currency_status"] == "unspecified_in_payload"
    assert tsm["stage3_basis_metadata"]["estimate_currency_match"] is True, "전망치-거래통화는 일치"
    
    # (7-4) 12개사 요약 카운트 검증
    assert summary["stage1_raw_value_pass_count"] == "11/12", "Stage 1은 11/12 통과"
    assert summary["stage2_quarter_window_pass_count"] == "0/12", "Stage 2는 0/12 통과"
    assert summary["stage3_currency_match_count"] == "10/12", "Stage 3 통화 일치는 TSM/BABA 제외 10/12"
    assert summary["stage3_estimate_currency_match_count"] == "11/12", "전망치 기준 단순 일치는 11/12"
    assert summary["stage4_scoring_eligible_count"] == "0/12", "Stage 4 채점 가능은 0/12"
    print("[Direct Test 7 PASS] R3-03, R3-04: TSM financialCurrency 불일치, 2A 통화미표기 분리 및 10/12 실측 검증 완료")
    print(">>> F6H-SOURCES-02-R1 R3-01~05 직접 관련 7대 검증 테스트 모두 PASS <<<")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Yahoo 저장 원자료 4단계 정밀 검증")
    parser.add_argument("--raw", type=Path, default=None, help="yahoo 원자료 경로")
    parser.add_argument("--out", type=Path, default=None, help="결과 JSON 저장 경로")
    args, _ = parser.parse_known_args()
    
    raw_path = args.raw if args.raw else get_raw_dir()
    out = verify_yahoo_evidence(raw_dir=raw_path)
    
    # Save output JSON (스크립트 기준 상대경로 기본값)
    out_file = args.out if args.out else Path(__file__).resolve().parent / "yahoo_evidence_verification.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(out, fp, ensure_ascii=False, indent=2)
    print(f"Yahoo evidence verification written to {out_file}")
    
    # Print formatted summary table
    print("\n" + "=" * 135)
    print("F6H-SOURCES-02-R1 Yahoo 저장 원자료 12개사 4단계 정밀 분리 검증 결과 (R3 보완)")
    print("=" * 135)
    print(f"{'티커':6s} | {'종목구분':15s} | {'1.값존재(2A/2E)':16s} | {'2.회계분기창':12s} | {'3.통화(거래/재무/전망)':26s} | {'표본/MinMax':12s} | {'4.채점가능':10s} | 비고")
    print("-" * 135)
    for r in out["results"]:
        s1 = f"{r['stage1_raw_values']['unique_actual_quarters']}A / {r['stage1_raw_values']['estimate_count']}E ({'O' if r['stage1_raw_values']['pass'] else 'X'})"
        s2 = "특정불가(X)" if not r['stage2_quarter_window']['pass'] else "특정(O)"
        s3_meta = r['stage3_basis_metadata']
        s3_cur = f"{s3_meta['raw_trade_currency']}/{s3_meta['raw_financial_currency']}/{s3_meta['estimate_currency']} ({'O' if s3_meta['currency_match'] else 'X'})"
        s3_extra = f"n:{'O' if s3_meta['sample_size_provided'] else 'X'}, mm:{'O' if s3_meta['min_max_provided'] else 'X'}"
        s4 = r['stage4_scoring_status']['verdict']
        notes = []
        if not r['stage1_raw_values']['pass']:
            notes.append(r['stage1_raw_values']['notes'])
        if not s3_meta['currency_match']:
            notes.append("통화 불일치")
        print(f"{r['ticker']:6s} | {r['company_type'][:15]:15s} | {s1:16s} | {s2:12s} | {s3_cur:26s} | {s3_extra:12s} | {s4:10s} | {'; '.join(notes)}")
    print("=" * 135)
    print(f"요약: [Stage 1 값존재] {out['summary']['stage1_raw_value_pass_count']} | [Stage 2 분기창] {out['summary']['stage2_quarter_window_pass_count']} | [Stage 3 통화일치(TSM/BABA제외)] {out['summary']['stage3_currency_match_count']} | [Stage 4 채점가능] {out['summary']['stage4_scoring_eligible_count']}")
    print("-" * 135)
    
    # Run self verification tests
    run_self_verification_tests(out)
