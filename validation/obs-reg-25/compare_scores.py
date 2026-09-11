# 승인 실행과 새 실행의 14개사 전 factor 를 대조하고 변화의 원인을 관측 쪽과 규칙 쪽으로 가른다
"""과제 4. **차이가 났다는 것만으로는 부족하고 무엇 때문에 났는지를 갈라야 한다.**

네 열을 놓는다. 바꾼 것이 셋(결정·관측·규칙)이라 한 번에 비교하면 원인이 섞인다.

    A   승인 실행       v1.5 규칙 · 승계 관측 · 결정 없음      scorecard/runs/ai-scorecard-2026-09-baseline
    A'  결정만 얹은 것   v1.5 규칙 · 승계 관측 · C-05·C-06     메모리 계산
    B   관측까지 바꾼 것 v1.5 규칙 · **새 관측·판단** · 결정   메모리 계산
    C   새 실행         **v1.7 규칙** · 새 관측·판단 · 결정    scorecard/runs/ai-scorecard-2026-09-obsreg

    A→A'  C-05·C-06 확정의 효과
    A'→B  **관측 등록·coverage_comparable 판정의 효과**
    B→C   규칙 v1.7 전환의 효과

한 열만 놓으면 "관측을 넣었더니 F6 가 전부 미완료가 됐다" 처럼 읽힌다. 실제 원인은 규칙 쪽이다.

사용:
    python validation/obs-reg-25/compare_scores.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNS = ROOT / "scorecard" / "runs"
BASE = RUNS / "ai-scorecard-2026-09-baseline"
NEW = RUNS / "ai-scorecard-2026-09-obsreg"
FACTORS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")


def cell(f: dict) -> str:
    if f["status"] == "ok":
        return f"{f['score']:+d}" if f["score"] is not None else "ok?"
    if f["status"] == "carried_score":
        return f"{f['score']:+d}c" if f["score"] is not None else "carr"
    short = {"pending_data": "pend", "needs_judgment": "judg", "needs_rule_decision": "rule",
             "pending_rule_decision": "rule"}.get(f["status"], f["status"][:4])
    did = (f.get("pending") or {}).get("decision_id")
    return f"{short}" + (f"({did})" if did else "")


def compute(run_dir: Path, rule_version: str | None = None, decisions: list | None = None):
    """실제 엔진으로 계산한다. rule_version·decisions 를 주면 갈아 끼워 돌린다(파일은 쓰지 않는다)."""
    from scorecard.engine import compute_company
    from scorecard.inputs import JudgmentLookup, ObsLookup
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict

    companies = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    obs = ObsLookup(load_json_strict(run_dir / "observations.json")["items"])
    jud = JudgmentLookup(load_json_strict(run_dir / "judgments.json")["items"])
    run = load_json_strict(run_dir / "run.json")
    if rule_version:
        run = {**run, "rule_version": rule_version}
    if decisions is not None:
        run = {**run, "decisions": decisions}
    rules = load_rules(run["rule_version"])
    out = {}
    for cid in run["companies"]:
        out[cid] = compute_company(companies[cid], obs, jud, rules, run)
    return out, companies


def totals(factors: dict) -> tuple[int | None, int | None, int | None]:
    """(과점, 함정, 조정). 엔진과 같은 기준으로 센다 — 미완료면 부분 합계를 만들지 않는다."""
    from scorecard.aggregate import COMPLETE_STATUSES

    if any(factors[f]["status"] not in COMPLETE_STATUSES or factors[f]["score"] is None for f in FACTORS):
        return None, None, None
    moat = sum(int(factors[f]["score"]) for f in ("F1", "F2", "F3", "F4", "F5"))
    trap = sum(int(factors[f]["score"]) for f in ("F6", "F7", "F8", "F9"))
    return moat, trap, moat + trap


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))

    from scorecard.schema import load_json_strict
    DECISIONS = load_json_strict(NEW / "run.json")["decisions"]

    A, companies = compute(BASE)                                        # v1.5 · 승계 관측 · 결정 없음
    A2, _ = compute(BASE, decisions=DECISIONS)                          # v1.5 · 승계 관측 · 결정
    B, _ = compute(NEW, rule_version="v1.5")                            # v1.5 · 새 관측 · 결정
    C, _ = compute(NEW)                                                 # v1.7 · 새 관측 · 결정

    bar = "=" * 118
    print(bar)
    print("OBS-REG-25 — 14개사 전 factor 대조")
    print(bar)
    print("  A 승인 실행 · A' 결정만 · B 관측까지 · C 규칙까지(v1.7).  셀은 A>A'>B>C, 변화가 있으면 * 표시")
    print()
    for cid in A:
        row = f"{cid:12}"
        for f in FACTORS:
            vals = [cell(S[cid][f]) for S in (A, A2, B, C)]
            mark = " " if len(set(vals)) == 1 else "*"
            row += f"  {mark}{f}:" + ">".join(vals)
        print(row)

    steps = [("[1] A→A'  C-05·C-06 확정의 효과 (관측·규칙 동일)", A, A2),
             ("[2] A'→B  관측 등록·coverage_comparable 판정의 효과 (규칙·결정 동일)", A2, B),
             ("[3] B→C   규칙 v1.7 전환의 효과 (관측·결정 동일)", B, C)]
    for title, X, Y in steps:
        print()
        print(title)
        rows = [(cid, f, cell(X[cid][f]), cell(Y[cid][f])) for cid in X for f in FACTORS
                if cell(X[cid][f]) != cell(Y[cid][f])]
        if not rows:
            print("  변화 없음")
        for cid, f, x, y in rows:
            print(f"  {cid:12} {f}  {x:>22} -> {y}")

    print()
    print("[4] 총점·순위")
    for label, S in (("A  승인 실행(v1.5·승계·결정 없음)", A), ("A' 결정만(v1.5·승계·C-05·C-06)", A2),
                     ("B  관측까지(v1.5·새 관측)", B), ("C  새 실행(v1.7·새 관측)", C)):
        rows = []
        for cid, fs in S.items():
            moat, trap, total = totals(fs)
            if total is not None:
                rows.append((total, moat, trap, cid))
        rows.sort(reverse=True)
        print(f"  {label} — 완주 {len(rows)}/{len(S)}개사")
        for rank, (total, moat, trap, cid) in enumerate(rows, 1):
            print(f"    {rank:>2} {companies[cid]['display_name']:<20} 과점 {moat:>3} 함정 {trap:>3} 조정 {total:>3}")
        if not rows:
            print("    (완주 0개사 — 순위를 만들지 않는다)")

    print()
    print("[5] 미완료 사유 — C 새 실행")
    for cid, fs in C.items():
        from scorecard.aggregate import COMPLETE_STATUSES
        reasons = [f"{f} {fs[f]['status']}" + (f"({(fs[f].get('pending') or {}).get('decision_id')})"
                                               if (fs[f].get("pending") or {}).get("decision_id") else "")
                   for f in FACTORS if fs[f]["status"] not in COMPLETE_STATUSES]
        if reasons:
            print(f"  {cid:12} " + "; ".join(reasons))
            for f in FACTORS:
                p = C[cid][f].get("pending")
                if p and f in ("F6", "F9"):
                    print(f"               {f}: {p['message'][:96]}")

    print()
    print("[6] 승인 실행 보존 확인")
    import hashlib
    for name in ("observations.json", "judgments.json", "run.json", "results.json"):
        h = hashlib.sha256((BASE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        print(f"  baseline/{name:20} sha256(LF)={h[:32]}…")
    res = json.loads((BASE / "results.json").read_text(encoding="utf-8"))
    print(f"  baseline results_hash 필드 = {res['results_hash'][:16]}…  (승인 해시 0942c342… 와 대조)")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
