# 승인 실행과 새 실행의 14개사 전 factor 를 대조하고 C-12·C-20 효과만 따로 떼어 낸다
"""완료 조건 1~3.

    A  승인 실행    v1.5 · 승계 관측 · 결정 없음
    B  C-12·C-20 이전   새 실행에서 두 결정과 비상장 관측을 뺀 변형(메모리 계산)
    C  새 실행      v1.7 · 전체 반영                        ← 승인 대상

`B→C` 가 **이번 과제의 몫**이다. `A→C` 는 누적 효과이고 앞 과제들이 섞여 있다.

사용:
    python validation/priv-impl-31/compare_private.py
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
        return f"{f['score']:+d}"
    if f["status"] == "carried_score":
        return f"{f['score']:+d}c"
    return {"pending_data": "pend", "needs_judgment": "judg",
            "needs_rule_decision": "rule"}.get(f["status"], f["status"][:4]) + (
        f"({(f.get('pending') or {}).get('decision_id')})" if (f.get("pending") or {}).get("decision_id") else "")


def compute(run_dir: Path, *, drop_decisions=(), drop_obs_suffix=None):
    from scorecard.engine import compute_company
    from scorecard.inputs import JudgmentLookup, ObsLookup
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict

    companies = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    items = load_json_strict(run_dir / "observations.json")["items"]
    if drop_obs_suffix:
        items = [o for o in items if not o["observation_id"].endswith(drop_obs_suffix)]
    run = load_json_strict(run_dir / "run.json")
    if drop_decisions:
        run = {**run, "decisions": [d for d in run["decisions"] if d["id"] not in drop_decisions]}
    rules = load_rules(run["rule_version"])
    obs, jud = ObsLookup(items), JudgmentLookup(load_json_strict(run_dir / "judgments.json")["items"])
    return {cid: compute_company(companies[cid], obs, jud, rules, run) for cid in run["companies"]}, companies


def totals(factors: dict):
    from scorecard.aggregate import COMPLETE_STATUSES
    if any(factors[f]["status"] not in COMPLETE_STATUSES or factors[f]["score"] is None for f in FACTORS):
        return None, None, None
    moat = sum(int(factors[f]["score"]) for f in ("F1", "F2", "F3", "F4", "F5"))
    trap = sum(int(factors[f]["score"]) for f in ("F6", "F7", "F8", "F9"))
    return moat, trap, moat + trap


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    A, companies = compute(BASE)
    B, _ = compute(NEW, drop_decisions=("C-12", "C-20"), drop_obs_suffix=".priv31")
    C, _ = compute(NEW)

    bar = "=" * 110
    print(bar)
    print("PRIV-IMPL-31 — 14개사 전 factor 대조")
    print(bar)
    print("  A 승인 실행(v1.5)   B C-12·C-20 이전   C 새 실행   — 셀은 A>B>C, 같으면 하나만")
    print()
    for cid in A:
        row = f"{cid:11}"
        for f in FACTORS:
            vals = [cell(S[cid][f]) for S in (A, B, C)]
            row += ("  " + f + ":" + (vals[0] if len(set(vals)) == 1 else ">".join(vals)))
        print(row)

    print()
    print("[1] B→C — C-12·C-20 과 비상장 관측 등록의 효과 *(이번 과제의 몫)*")
    rows = [(cid, f, cell(B[cid][f]), cell(C[cid][f])) for cid in B for f in FACTORS
            if cell(B[cid][f]) != cell(C[cid][f])]
    print("  변화 없음" if not rows else "")
    for cid, f, x, y in rows:
        print(f"  {cid:11} {f}  {x:>22} -> {y}")

    print()
    print("[2] 비상장 2사 산출 근거")
    for cid in ("anthropic", "openai"):
        calc = C[cid]["F6"]["calc"]
        p2 = calc["parameters"]["P2"]
        corr = calc["correction"]
        print(f"  {cid}")
        print(f"    P2  ps_ratio {p2['value']}  →  {p2['band']}  {p2['score']:+d}"
              + (f"   (구간 {p2['estimate_range']['low']}~{p2['estimate_range']['high']}, "
                 f"밴드 갈림 {p2['estimate_range']['spans_bands']})" if "estimate_range" in p2 else ""))
        for name, row in corr["conditions"].items():
            print(f"    {name:20} {row['value']:.4f}  임계 {row['threshold']}  충족 {row['met']}")
        print(f"    보정 {corr['promotion_steps']:+d}  →  F6 {calc['score']:+d}   F9 {C[cid]['F9']['score']:+d}")
        print(f"    F9 첫 관문: {C[cid]['F9']['calc']['path'][0].get('result')}")

    print()
    print("[3] 총점·순위")
    for label, S in (("A  승인 실행(v1.5)", A), ("C  새 실행(v1.7)", C)):
        rows2 = []
        for cid, fs in S.items():
            moat, trap, total = totals(fs)
            if total is not None:
                rows2.append((total, moat, trap, cid))
        rows2.sort(key=lambda r: (-r[0], -r[1], r[3]))
        print(f"  {label} — 완주 {len(rows2)}/{len(S)}개사")
        prev, rank = None, 0
        for i, (total, moat, trap, cid) in enumerate(rows2, 1):
            if total != prev:
                rank, prev = i, total
            print(f"    {rank:>2} {companies[cid]['display_name']:<20} 과점 {moat:>3} 함정 {trap:>3} 조정 {total:>3}")

    print()
    print("[4] 승인 실행 보존")
    from scorecard.stages import current_hashes
    appr = json.loads((BASE / "approval.json").read_text(encoding="utf-8"))["hashes"]
    cur, new = current_hashes(BASE.name), current_hashes(NEW.name)
    print(f"  {'대상':14} {'승인 baseline':>18} {'현재 baseline':>18} {'새 실행':>18}  보존")
    for k in ("rules", "observations", "judgments", "run", "results", "draft"):
        print(f"  {k:14} {appr[k][:16]:>18} {cur[k][:16]:>18} {new[k][:16]:>18}  {'예' if appr[k] == cur[k] else '아니오'}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
