# 세전이익 TTM 을 보존 원자료에서 복원한다 — nonop_share 산식 정정의 입력 (네트워크 없음)
"""**저장값이 옳고 재계산이 틀렸다.** 저장 `nonop_share` 는 `영업외손익 ÷ 세전이익` 이고
엔진은 `(순이익 − 영업이익) ÷ 순이익` 을 썼다. 두 군데가 다르다 — 분자에서 법인세를 안 되더하고
분모가 세전이익이 아니다.

정정하려면 **세전이익 하나만** 있으면 된다. `(세전 − 영업이익) / 세전` 이 곧 영업외손익 비중이고
법인세를 따로 들이지 않아도 된다.

## 복원 방법

1. 창은 `net_income_ttm` 관측의 `period` 를 그대로 쓴다.
2. 직접 태그를 먼저 본다. 창과 같은 12개월 공시가 있으면 그것.
3. 없으면 `당기 누계 + 전기 연간 − 전기 동일 누계`. 회계 Q4 를 직접 태깅하지 않는 회사가 많아
   분기 조각을 이어 붙이면 12개월을 못 덮는다.
4. 그래도 없으면 **국내·해외 세전이익의 합**. oracle 이 이 경우다.
5. tsmc 는 companyfacts 에 2025 금액 사실이 0건이라 보존 20-F 손익계산서에서 읽는다.

## 검산

`세전 = 순이익 + 법인세` 가 성립해야 한다. 지분법 손익·비지배지분이 세전 아래에 오는 회사는
어긋나며 그 크기를 같이 남긴다(alibaba).
"""
from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "validation" / "netcash-37"))
import measure  # noqa: E402

PRETAX = ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
          "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"]
PRETAX_SPLIT = ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic",
                "IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign"]
TAX = ["IncomeTaxExpenseBenefit", "IncomeTaxExpenseBenefitContinuingOperations"]
NATIVE = {"alibaba": ("CNY", 6.8980), "tsmc": ("TWD", 31.37)}
TOL_DAYS = 4
# 보존 20-F 916행 INCOME BEFORE INCOME TAX · 918행 INCOME TAX EXPENSE (NT$ 백만)
TSMC_20F = {"pretax": 2_041_654.7e6, "tax": 346_529.8e6,
            "how": "보존 20-F 916행 INCOME BEFORE INCOME TAX 2,041,654.7 NT$백만"}


def _rows(cid: str, tag: str, unit: str) -> list[dict[str, Any]]:
    node = measure.facts(cid).get("us-gaap", {}).get(tag)
    return [] if not node else [r for r in node["units"].get(unit, []) if r.get("start") and r.get("end")]


def _days(a: str, b: str) -> int:
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def _pick(rows, *, end=None, near=None, lo=0, hi=400):
    c = [r for r in rows if lo <= _days(r["start"], r["end"]) <= hi]
    if end:
        c = [r for r in c if r["end"] == end]
    if near:
        c = [r for r in c if abs(_days(near, r["end"])) <= TOL_DAYS]
    return max(c, key=lambda r: (_days(r["start"], r["end"]), str(r.get("filed", "")))) if c else None


def _ttm(cid: str, tags: list[str], s: str, e: str, unit: str):
    prev = (date.fromisoformat(s) - timedelta(days=1)).isoformat()
    for tag in tags:
        rows = _rows(cid, tag, unit)
        if not rows:
            continue
        one = _pick(rows, end=e, lo=330)
        if one and abs(_days(one["start"], s)) <= TOL_DAYS:
            return one["val"], tag, f"단일 12개월 {one['start']}~{one['end']}"
        ytd, yprev = _pick(rows, end=e, lo=1), _pick(rows, near=prev, lo=1)
        fy = None
        if yprev:
            same = [r for r in rows if r["start"] == yprev["start"]
                    and 330 <= _days(r["start"], r["end"]) <= 400]
            fy = max(same, key=lambda r: str(r.get("filed", ""))) if same else None
        if ytd and fy and yprev:
            return (ytd["val"] + fy["val"] - yprev["val"], tag,
                    f"당기누계 {ytd['end']} + 전기연간 {fy['end']} − 전기동일누계 {yprev['end']}")
    return None, None, None


def pretax_ttm(cid: str, start: str, end: str) -> dict[str, Any]:
    """세전이익 TTM. 어느 경로로 나왔는지와 `순이익 + 법인세` 검산을 같이 돌려준다."""
    unit, fx = NATIVE.get(cid, ("USD", 1.0))
    if cid == "tsmc":
        return {"pretax_native": TSMC_20F["pretax"], "pretax_usd": TSMC_20F["pretax"] / fx,
                "tax_native": TSMC_20F["tax"], "tax_usd": TSMC_20F["tax"] / fx,
                "concept": "20-F 손익계산서", "how": TSMC_20F["how"], "unit": unit, "fx": fx}
    val, tag, how = _ttm(cid, PRETAX, start, end, unit)
    if val is None:
        # 국내·해외 분리 공시만 있는 경우. oracle 이 그렇다.
        parts = [_ttm(cid, [t], start, end, unit) for t in PRETAX_SPLIT]
        if all(p[0] is not None for p in parts):
            val = sum(p[0] for p in parts)
            tag = " + ".join(PRETAX_SPLIT)
            how = "국내·해외 세전이익 합 — " + " / ".join(f"{p[1].split('Taxes')[-1]} {p[0]:,.0f}" for p in parts)
    tax, tax_tag, _ = _ttm(cid, TAX, start, end, unit)
    return {"pretax_native": val, "pretax_usd": None if val is None else val / fx,
            "tax_native": tax, "tax_usd": None if tax is None else tax / fx,
            "concept": tag, "how": how, "tax_concept": tax_tag, "unit": unit, "fx": fx}


def cross_check(pretax_usd, ni, tax_usd):
    """`세전 = 순이익 + 법인세` 상대오차. 지분법·비지배지분이 세전 아래면 어긋난다."""
    if pretax_usd is None or tax_usd is None or not pretax_usd:
        return None
    return (ni + tax_usd - pretax_usd) / abs(pretax_usd)
