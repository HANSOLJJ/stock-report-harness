# NTM 기간 판정에서 폐기된 회계연도 잔여개월수 계산을 차단하는 감사 스크립트
"""QWEN-NTM-DATA-03-R1 감사용 분석 진입점.

이전 버전의 회계연도 잔여개월수와 Forward PE 역산 가설은 §5.1 판정에 사용할 수
없으므로 재계산하지 않는다. 정정 결과는 fy-analysis-corrected.json에 보존되어 있다.
"""
from __future__ import annotations

import json
import argparse
from pathlib import Path


def validate(corrected_path: Path, evidence_path: Path) -> None:
    data = json.loads(corrected_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    companies = data.get("companies", {})
    evidence_companies = {row["company_id"]: row for row in evidence.get("companies", [])}
    assert len(companies) == 10
    assert set(companies) == set(evidence_companies)
    assert all(row.get("forward_pe_period") == "period_unknown" for row in companies.values())
    assert all(row.get("ntm_eligibility") == "unverified" for row in companies.values())
    assert all(row.get("quarterly_eps_required") == 4 for row in companies.values())
    assert all(0 <= row.get("quarterly_eps_obtained", -1) <= 4 for row in companies.values())
    assert all(row.get("quarterly_eps_eligible") == 0 for row in companies.values())
    assert all(row.get("quarterly_eps_obtained", 0) >= row.get("quarterly_eps_eligible", 0) for row in companies.values())
    for company_id, corrected in companies.items():
        observed = evidence_companies[company_id]
        verdict = observed.get("period_verdict", {})
        forecast = observed.get("forecast_period", {})
        assert verdict.get("forward_pe_period") == corrected["forward_pe_period"]
        assert verdict.get("ntm_eligibility") == corrected["ntm_eligibility"]
        assert observed.get("satisfied") is False
        assert forecast.get("yahoo_forward_quarters_free") == corrected["quarterly_eps_obtained"]
    print("R1 corrected analysis verified: 10 companies period_unknown/unverified; observed and eligible counts separated")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corrected", type=Path, default=Path(__file__).with_name("fy-analysis-corrected.json"))
    parser.add_argument("--evidence", type=Path, default=Path(__file__).with_name("evidence.json"))
    args = parser.parse_args()
    validate(args.corrected, args.evidence)


if __name__ == "__main__":
    main()
