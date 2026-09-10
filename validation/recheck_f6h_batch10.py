# worker 194fd4b 의 verify_window.py 판정을 설계진행에서 독립 재현·역검증한다 (신규 네트워크 호출 없음)
"""사용:
    python validation/recheck_f6h_batch10.py <추출된_f6h-source-batch-10_경로> [--sec <f6h-feasibility-08/_raw>]

worker 워크트리를 수정하지 않는다. `git archive 194fd4b validation/f6h-source-batch-10` 으로
임시 경로에 푼 사본을 대상으로 실행한다. 결과는 stdout 과 --out JSON 이다.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path


def load_verifier(batch: Path):
    spec = importlib.util.spec_from_file_location("vw", batch / "verify_window.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def independent_counts(batch: Path) -> dict:
    """worker 코드를 쓰지 않고 원자료 JSON 에서 직접 세어 본다."""
    tickers = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
    collected = json.loads((batch / "_raw" / "meta.json").read_text(encoding="utf-8"))["collected_at_utc"][:10]
    out = {"collected": collected, "tickers": {}}
    for t in tickers:
        rec = json.loads((batch / "_raw" / "finnhub" / f"{t}.json").read_text(encoding="utf-8"))
        past = json.loads(rec["past"]["body"])
        fut = json.loads(rec["future"]["body"])["earningsCalendar"]
        a = sorted((r["year"], r["quarter"], r["actual"]) for r in past if r.get("actual") is not None)
        e = sorted((r["year"], r["quarter"], r["epsEstimate"], r.get("date"))
                   for r in fut if r.get("epsEstimate") is not None and r.get("epsActual") is None)
        out["tickers"][t] = {
            "n_actual": len(a),
            "n_forecast": len(e),
            "endpoint_overlap": sorted({(y, q) for y, q, _ in a} & {(y, q) for y, q, _, _ in e}),
            "a2": [f"{y}Q{q}" for y, q, _ in a[-2:]],
            "a2_values": [v for _, _, v in a[-2:]],
            "e2": [f"{y}Q{q}" for y, q, _, _ in e[:2]],
            # 전망으로 뽑힌 행의 발표 예정일이 수집 시점보다 앞서면 이미 지난 분기다
            "stale_forecast_dates": [d for *_, d in e[:2] if d and d <= collected],
            "surprise_percent": [r.get("surprisePercent") for r in past],
        }
    return out


def probe(mod, batch: Path, name: str, mutate) -> dict:
    """META 원자료 사본을 바꿔 넣고 판정이 실제로 따라 움직이는지 본다."""
    tmp = batch / "_recheck_mut"
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(batch / "_raw" / "finnhub", tmp)
    if mutate:
        rec = json.loads((tmp / "META.json").read_text(encoding="utf-8"))
        mutate(rec)
        (tmp / "META.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    base = mod.FINNHUB
    mod.FINNHUB = tmp
    try:
        r = mod.verify("META")
    finally:
        mod.FINNHUB = base
        shutil.rmtree(tmp)
    return {
        "probe": name,
        "a2": [f"{x['y']}Q{x['q']}={x['val']}" for x in r["a2"]],
        "e2": [f"{x['y']}Q{x['q']}={x['val']}" for x in r["e2"]],
        "raw_availability": r["raw_availability"],
        "window_verified": r["window_verified"],
        "basis_verified": r["basis_verified"],
        "score_ready": r["score_ready"],
        "issues": r["issues"],
        "basis_fields": r["basis_fields"],
    }


def m_stale(rec):
    """최신 실적 1행을 전망 목록으로 옮긴다 — 이미 지난 분기를 전망으로 위장."""
    past = json.loads(rec["past"]["body"])
    dropped = past.pop(0)
    rec["past"]["body"] = json.dumps(past)
    fut = json.loads(rec["future"]["body"])
    fut["earningsCalendar"].append({"symbol": "META", "date": "2026-07-29", "hour": "amc",
                                    "quarter": dropped["quarter"], "year": dropped["year"],
                                    "epsEstimate": dropped["estimate"], "epsActual": None,
                                    "revenueEstimate": 0, "revenueActual": None})
    rec["future"]["body"] = json.dumps(fut)


def m_basis_one_row(rec):
    """창 4행 중 첫 행에만 basis 필드를 준다."""
    past = json.loads(rec["past"]["body"])
    for r in past:
        if (r["year"], r["quarter"]) == (2026, 1):
            r.update({"currency": "USD", "share_basis": "ordinary",
                      "accounting": "GAAP", "asOf": "2026-09-09"})
    rec["past"]["body"] = json.dumps(past)


def m_basis_all_rows(rec):
    """4행 전부에 KRW/IFRS 를 준다 — 상수가 아니라 읽은 값을 쓰는지 확인."""
    past = json.loads(rec["past"]["body"])
    fut = json.loads(rec["future"]["body"])
    tag = {"currency": "KRW", "share_basis": "ordinary", "accounting": "IFRS", "asOf": "2026-09-09"}
    for r in past:
        r.update(tag)
    for r in fut["earningsCalendar"]:
        r.update(tag)
    rec["past"]["body"] = json.dumps(past)
    rec["future"]["body"] = json.dumps(fut)


def m_gap(rec):
    """회계 라벨에 구멍을 낸다 — 연속성 검사가 실제로 도는지 확인하는 양성 대조."""
    past = json.loads(rec["past"]["body"])
    for r in past:
        if (r["year"], r["quarter"]) == (2026, 1):
            r["year"], r["quarter"] = 2025, 1
    rec["past"]["body"] = json.dumps(past)


def m_non_numeric(rec):
    """실적 값을 비수치 문자열로 바꾼다."""
    past = json.loads(rec["past"]["body"])
    past[0]["actual"] = "NOT_A_NUMBER"
    rec["past"]["body"] = json.dumps(past)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("batch", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    batch = args.batch.resolve()
    mod = load_verifier(batch)

    probes = [
        probe(mod, batch, "T0 무변경(대조군)", None),
        probe(mod, batch, "T1 지난 분기를 전망으로 위장", m_stale),
        probe(mod, batch, "T2 basis 를 4행 중 1행에만 부여", m_basis_one_row),
        probe(mod, batch, "T3 라벨 불연속 주입(양성 대조)", m_gap),
        probe(mod, batch, "T4 실적 값이 비수치 문자열", m_non_numeric),
        probe(mod, batch, "T5 basis 4행 전부 부여(KRW/IFRS)", m_basis_all_rows),
    ]
    counts = independent_counts(batch)

    evidence = {"target_commit": "194fd4b", "batch_path": str(batch),
                "independent_counts": counts, "verifier_probes": probes}

    for p in probes:
        print(f"[{p['probe']}] raw={p['raw_availability']} window={p['window_verified']} "
              f"basis={p['basis_verified']} score={p['score_ready']} 2A={p['a2']} 2E={p['e2']} {p['issues']}")
    print()
    for t, v in counts["tickers"].items():
        print(f"{t:6} nA={v['n_actual']} nE={v['n_forecast']} 교집합={v['endpoint_overlap'] or 'φ'} "
              f"2A={v['a2']}{v['a2_values']} 지난전망={v['stale_forecast_dates'] or '-'}")

    if args.out:
        args.out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n증거 기록: {args.out}")


if __name__ == "__main__":
    sys.exit(main())
