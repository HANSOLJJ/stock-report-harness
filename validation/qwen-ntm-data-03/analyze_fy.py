# NTM 기간 판정에서 폐기된 회계연도 잔여개월수 계산을 차단하는 감사 스크립트
"""QWEN-NTM-DATA-03-R1 감사용 분석 진입점.

이전 버전의 회계연도 잔여개월수와 Forward PE 역산 가설은 §5.1 판정에 사용할 수
없으므로 재계산하지 않는다. 정정 결과는 fy-analysis-corrected.json에 보존되어 있다.
"""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    path = Path(__file__).with_name("fy-analysis-corrected.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    companies = data.get("companies", {})
    assert len(companies) == 10
    assert all(row.get("forward_pe_period") == "period_unknown" for row in companies.values())
    assert all(row.get("ntm_eligibility") == "unverified" for row in companies.values())
    assert all(row.get("quarterly_eps_required") == 4 for row in companies.values())
    print("R1 corrected analysis verified: 10 companies period_unknown/unverified")


if __name__ == "__main__":
    main()
