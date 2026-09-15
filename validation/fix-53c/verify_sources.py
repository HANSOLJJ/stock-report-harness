# FIX-53 3단계: 리뷰 A 2차 발견을 보존 원자료에서 다시 재현한다 — apply_stage3.py 가 쓴 문장의 근거
"""git 보존 사본(3cf9799·f14a235)과 작업 트리 companyfacts(validation/f6-avail-15/_raw, 15b 와 바이트 동일)를 읽는다.
신규 네트워크 호출 없음."""
from __future__ import annotations

import collections
import html
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HANDOVER = Path("E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor/AI기업_채점표_HANDOVER.md")


def blob_text(spec: str) -> str:
    raw = subprocess.run(["git", "show", spec], capture_output=True, cwd=ROOT).stdout.decode("utf-8", "replace")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def facts(tk: str) -> dict:
    return json.loads((ROOT / "validation" / "f6-avail-15" / "_raw" / f"{tk}.companyfacts.json").read_text(encoding="utf-8"))


def usd(tk: str, tag: str) -> list[dict]:
    return facts(tk)["facts"]["us-gaap"].get(tag, {}).get("units", {}).get("USD", [])


def main() -> int:
    baba = blob_text("3cf9799:validation/offb-24/_raw/baba-20260331.htm")
    print("[alibaba 20-F] 전문 검색")
    for pat in ("practical expedient to not disclose", "unsatisfied performance obligation", "remaining performance obligation", "backlog"):
        print(f"  {pat!r}: {len(re.findall(pat, baba, re.I))}건")
    i = baba.find("practical expedient to not disclose")
    print("  면제 문장:", baba[i - 20:i + 330])

    spcx = blob_text("3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm")
    m = next(m for m in re.finditer(r"Income \(loss\) before income taxes", spcx) if "4,219" in spcx[m.start():m.start() + 120])
    print("[spacex-xai S-1/A]", spcx[m.start():m.start() + 150])
    pre = {(f.get("start"), f["end"]): f["val"] for f in usd("SPCX", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest")}
    tax = {(f.get("start"), f["end"]): f["val"] for f in usd("SPCX", "IncomeTaxExpenseBenefit")}
    h1_26, h1_25 = pre[("2026-01-01", "2026-06-30")], pre[("2025-01-01", "2025-06-30")]
    t26, t25 = tax[("2026-01-01", "2026-06-30")], tax[("2025-01-01", "2025-06-30")]
    ttm = -4219e6 + h1_26 - h1_25
    tax_ttm = 718e6 + t26 - t25
    print(f"  TTM 세전 {ttm:,.0f} · TTM 세금 {tax_ttm:,.0f} · 세전−세금 {ttm - tax_ttm:,.0f} (net_income_ttm -8,218,000,000)")
    for tag in ("MarketableSecuritiesCurrent", "MarketableSecuritiesNoncurrent", "RestrictedCashCurrent", "RestrictedCashNoncurrent", "CashAndCashEquivalentsAtCarryingValue"):
        print(f"  {tag} 2026-06-30:", [f["val"] for f in usd("SPCX", tag) if f["end"] == "2026-06-30"])

    print("[oracle] 이중 태깅 후보")
    for tag in ("EquitySecuritiesWithoutReadilyDeterminableFairValueAmount", "AvailableForSaleSecuritiesDebtSecuritiesCurrent"):
        print(f"  {tag}:", [(f["end"], f["val"], f["accn"]) for f in usd("ORCL", tag) if f["end"] in ("2025-05-31", "2026-05-31")])

    cnt = collections.Counter()
    tags = set()
    for tax_ in facts("PLTR")["facts"].values():
        for tag, c in tax_.items():
            for unit in c["units"].values():
                for f in unit:
                    if f["end"] == "2026-06-30":
                        cnt["all"] += 1
                        if "start" not in f:
                            cnt["instant"] += 1
                            tags.add(tag)
    print(f"[palantir] end=2026-06-30 사실 {cnt['all']}건 · 시점형 {cnt['instant']}건 · 시점형 태그 {len(tags)}종")

    tsm = blob_text("f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm")
    j = tsm.find("INCOME BEFORE INCOME TAX 979,316.5")
    print("[tsmc] 행:", tsm[j:j + 70], "· 보존 htm 줄 수:",
          subprocess.run(["git", "show", "f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm"], capture_output=True, cwd=ROOT).stdout.count(b"\n") + 1)

    print("[net_cash 제한현금 누락] 2026-06-30")
    for tk, tag in (("AMZN", "RestrictedCashNoncurrent"), ("AMZN", "RestrictedCashAndInvestments"),
                    ("META", "RestrictedCashAndCashEquivalentsAtCarryingValue"), ("META", "RestrictedCashAndCashEquivalentsNoncurrent"),
                    ("TSLA", "RestrictedCashNoncurrent"), ("SPCX", "RestrictedCashNoncurrent")):
        print(f"  {tk} {tag}:", [f["val"] for f in usd(tk, tag) if f["end"] == "2026-06-30"])

    lines = HANDOVER.read_text(encoding="utf-8").splitlines()
    print("[HANDOVER] $300B 행:", [(n + 1, l[:80]) for n, l in enumerate(lines) if "Anthropic $300B" in l])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
