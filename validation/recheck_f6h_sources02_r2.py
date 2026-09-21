# C-13 c9ce4d1 의 verify_yahoo_evidence.py R2-01~04 보완을 설계진행에서 독립 재현·역검증한다 (신규 네트워크 호출 없음)
"""사용:
    python validation/recheck_f6h_sources02_r2.py <추출된_f6-h-sources-02_경로> --raw <yahoo 스냅샷 경로> [--out out.json]

C-13 워크트리를 수정하지 않는다. `git archive c9ce4d1 validation/f6-h-sources-02` 로 임시 경로에 푼
사본을 대상으로 하고, 원자료는 worker 저장본을 복사한 스냅샷을 쓴다.
**모듈의 __main__ 은 실행하지 않는다.** 원본이 C-13 워크트리 절대경로에 결과 JSON 을 덮어쓰기 때문이다.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import math
from pathlib import Path


def load_module(script: Path):
    spec = importlib.util.spec_from_file_location("vye_recheck", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # __name__ 이 __main__ 이 아니므로 파일 쓰기가 돌지 않는다
    return mod


def one(mod, raw: Path, ticker: str, mutate=None) -> dict:
    data = json.loads((raw / f"{ticker}.json").read_text(encoding="utf-8"))
    if mutate:
        data = copy.deepcopy(data)
        mutate(data)
    comp = next(c for c in mod.COMPANIES if c["ticker"] == ticker)
    r = mod.parse_ticker_data(data, comp)
    s1, s2, s3, s4 = (r["stage1_raw_values"], r["stage2_quarter_window"],
                      r["stage3_basis_metadata"], r["stage4_scoring_status"])
    return {
        "ticker": ticker,
        "s1_pass": s1["pass"], "actual_count": s1["actual_count"],
        "unique_quarters": s1["unique_actual_quarters"], "estimate_count": s1["estimate_count"],
        "s2_pass": s2["pass"], "s2_notes": s2["notes"],
        "raw_trade_currency": s3["raw_trade_currency"], "ref_trade_currency": s3["ref_trade_currency"],
        "trade_currency_status": s3["trade_currency_status"],
        "estimate_currency": s3["estimate_currency"], "currency_match": s3["currency_match"],
        "s3_pass": s3["pass"], "scoring_eligible": s4["scoring_eligible"],
    }


def m_basis_krw(d):
    d["basis"]["currency"] = "KRW"


def m_basis_drop(d):
    d["basis"].pop("currency", None)


def m_all_krw(d):
    """거래 통화와 전망 통화를 함께 KRW 로 바꾼다 — 참조 통화(USD)와는 충돌한다."""
    d["basis"]["currency"] = "KRW"
    for k in ("0q", "+1q"):
        d["earnings_estimate"][k]["currency"] = "KRW"


def m_str_avg(d):
    d["earnings_estimate"]["0q"]["avg"] = "NOT_A_NUMBER"


def m_bool_avg(d):
    d["earnings_estimate"]["0q"]["avg"] = True


def m_nan_avg(d):
    d["earnings_estimate"]["0q"]["avg"] = float("nan")


def m_period_first_row_only(d):
    """회계기간 필드를 실적 첫 행과 0q 에만 넣는다 — 한 행만 보고 전체를 판정하는지 확인."""
    d["earnings_dates"][0]["period_end"] = "2026-09-30"
    d["earnings_estimate"]["0q"]["fiscal_period"] = "2026Q3"


def m_period_second_row_only(d):
    """첫 행을 건너뛴 두 번째 행에만 넣는다 — 첫 행만 보면 놓친다."""
    d["earnings_dates"][1]["period_end"] = "2026-06-30"
    d["earnings_estimate"]["0q"]["fiscal_period"] = "2026Q3"


def m_dup_row(d):
    row = next(r for r in d["earnings_dates"] if r.get("Reported EPS") is not None)
    d["earnings_dates"].append(copy.deepcopy(row))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path, help="추출된 validation/f6-h-sources-02 경로")
    ap.add_argument("--raw", type=Path, required=True, help="yahoo 원자료 스냅샷 경로")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    mod = load_module(args.src.resolve() / "verify_yahoo_evidence.py")
    raw = args.raw.resolve()

    base = mod.verify_yahoo_evidence(raw_dir=raw)
    again = mod.verify_yahoo_evidence(raw_dir=raw)
    deterministic = json.dumps(base, sort_keys=True) == json.dumps(again, sort_keys=True)

    probes = [
        ("P0 META 무변경(대조군)", "META", None),
        ("P1 META basis.currency=KRW", "META", m_basis_krw),
        ("P2 META basis.currency 삭제", "META", m_basis_drop),
        ("P3 META 거래·전망 통화 동시 KRW", "META", m_all_krw),
        ("P4 META 0q.avg 문자열", "META", m_str_avg),
        ("P5 META 0q.avg bool True", "META", m_bool_avg),
        ("P6 META 0q.avg NaN", "META", m_nan_avg),
        ("P7 META 회계기간 필드 첫 행에만", "META", m_period_first_row_only),
        ("P8 META 회계기간 필드 둘째 행에만", "META", m_period_second_row_only),
        ("P9 SPCX 실적행 복제", "SPCX", m_dup_row),
        ("P10 TSM 무변경", "TSM", None),
        ("P11 BABA 무변경", "BABA", None),
    ]
    rows = []
    for name, ticker, fn in probes:
        r = one(mod, raw, ticker, fn)
        r["probe"] = name
        rows.append(r)
        print(f"[{name}] s1={r['s1_pass']} s2={r['s2_pass']} cur_status={r['trade_currency_status']} "
              f"est={r['estimate_currency']} raw={r['raw_trade_currency']} match={r['currency_match']} "
              f"s3={r['s3_pass']} score={r['scoring_eligible']}")

    # 원자료의 financialCurrency 를 검증기가 보는가
    fin = {}
    for t in [c["ticker"] for c in mod.COMPANIES]:
        d = json.loads((raw / f"{t}.json").read_text(encoding="utf-8"))
        b = d.get("basis") or {}
        fin[t] = {"currency": b.get("currency"), "financialCurrency": b.get("financialCurrency"),
                  "est_currency": (d.get("earnings_estimate") or {}).get("0q", {}).get("currency")}
    src = (args.src.resolve() / "verify_yahoo_evidence.py").read_text(encoding="utf-8")
    reads_financial_currency = "financialCurrency" in src

    print()
    print("결정론적 2회 일치:", deterministic)
    print("검증기가 financialCurrency 를 읽는가:", reads_financial_currency)
    print(f"{'T':6}{'basis.currency':>16}{'financialCurrency':>20}{'0q.currency':>14}")
    for t, v in fin.items():
        print(f"{t:6}{str(v['currency']):>16}{str(v['financialCurrency']):>20}{str(v['est_currency']):>14}")
    print()
    print("요약:", {k: v for k, v in base["summary"].items() if k.endswith("_count")})

    if args.out:
        args.out.write_text(json.dumps({
            "target_commit": "c9ce4d1", "deterministic": deterministic,
            "reads_financial_currency": reads_financial_currency,
            "summary_counts": {k: v for k, v in base["summary"].items() if k.endswith("_count")},
            "currency_fields": fin, "probes": rows,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n증거 기록: {args.out}")


if __name__ == "__main__":
    main()
