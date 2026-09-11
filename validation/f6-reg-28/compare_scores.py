# 승인 실행과 새 실행의 14개사 전 factor 를 대조하고 변화를 결정·관측·규칙·TSM 최신화로 가른다
"""완료 조건 1·2. **차이가 났다는 것만으로는 부족하고 무엇 때문에 났는지를 갈라야 한다.**

    A  승인 실행     v1.5 · 승계 관측 · 결정 없음
    B  결정만        v1.5 · 승계 관측 · C-05 apply · C-06 · C-16 downgrade
    C  관측까지      v1.5 · 새 관측·판단 전부 · 결정
    D  새 실행       **v1.7** · 새 관측·판단 · 결정          ← 승인 대상

    A→B  결정 확정의 효과      B→C  관측 등록의 효과      C→D  규칙 v1.7 전환의 효과

`D` 안에서 **TSM FY2025 최신화**만 따로 떼어 낸다(`[4]`). FY2024 관측으로 되돌린 변형을
메모리에서 계산해 F6 가 어디서 움직였는지 본다. 합쳐 등록하되 효과는 갈라 보이게 한 이유다.

사용:
    python validation/f6-reg-28/compare_scores.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUNS = ROOT / "scorecard" / "runs"
BASE = RUNS / "ai-scorecard-2026-09-baseline"
NEW = RUNS / "ai-scorecard-2026-09-obsreg"
FACTORS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")

# TSM FY2024 되돌림용. companyfacts 값(TWD)과 FY2024 20-F 선언 환율 32.79.
TSM_FY2024 = {"revenue_ttm": (2_894_307_700_000, "2024-12-31"),
              "revenue_ttm_prior": (2_161_735_800_000, "2023-12-31"),
              "net_income_ttm": (1_157_523_900_000, "2024-12-31"),
              "operating_income_ttm": (1_322_053_000_000, "2024-12-31")}
TSM_FY2024_RATE = 32.79


def cell(f: dict) -> str:
    if f["status"] == "ok":
        return f"{f['score']:+d}" if f["score"] is not None else "ok?"
    if f["status"] == "carried_score":
        return f"{f['score']:+d}c" if f["score"] is not None else "carr"
    short = {"pending_data": "pend", "needs_judgment": "judg", "needs_rule_decision": "rule",
             "pending_rule_decision": "rule"}.get(f["status"], f["status"][:4])
    did = (f.get("pending") or {}).get("decision_id")
    return short + (f"({did})" if did else "")


def compute(run_dir: Path, *, rule_version: str | None = None, decisions: list | None = None,
            obs_patch=None):
    from scorecard.engine import compute_company
    from scorecard.inputs import JudgmentLookup, ObsLookup
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict

    companies = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    items = load_json_strict(run_dir / "observations.json")["items"]
    if obs_patch is not None:
        items = obs_patch(items)
    obs = ObsLookup(items)
    jud = JudgmentLookup(load_json_strict(run_dir / "judgments.json")["items"])
    run = load_json_strict(run_dir / "run.json")
    if rule_version:
        run = {**run, "rule_version": rule_version}
    if decisions is not None:
        run = {**run, "decisions": decisions}
    rules = load_rules(run["rule_version"])
    return {cid: compute_company(companies[cid], obs, jud, rules, run) for cid in run["companies"]}, companies


def totals(factors: dict):
    from scorecard.aggregate import COMPLETE_STATUSES
    if any(factors[f]["status"] not in COMPLETE_STATUSES or factors[f]["score"] is None for f in FACTORS):
        return None, None, None
    moat = sum(int(factors[f]["score"]) for f in ("F1", "F2", "F3", "F4", "F5"))
    trap = sum(int(factors[f]["score"]) for f in ("F6", "F7", "F8", "F9"))
    return moat, trap, moat + trap


def tsm_rollback(items: list[dict]) -> list[dict]:
    """TSM 의 F6 입력을 FY2024 로 되돌린다. 당해·전년에 같은 환율(32.79)을 쓰는 원칙은 유지한다."""
    out = []
    for o in items:
        if o["company_id"] == "tsmc" and o["metric"] in TSM_FY2024 and o["observation_id"].endswith(".f6reg28"):
            twd, end = TSM_FY2024[o["metric"]]
            o = {**o, "value": round(twd / TSM_FY2024_RATE, 0), "as_of": end,
                 "period": {"start": end[:4] + "-01-01", "end": end}}
        elif o["company_id"] == "tsmc" and o["metric"] == "operating_margin_ttm" and o["observation_id"].endswith(".f6reg28"):
            o = {**o, "value": round(1_322_053_000_000 / 2_894_307_700_000, 6), "as_of": "2024-12-31",
                 "period": {"start": "2024-01-01", "end": "2024-12-31"}}
        out.append(o)
    return out


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.schema import load_json_strict

    DEC = load_json_strict(NEW / "run.json")["decisions"]
    A, companies = compute(BASE)
    B, _ = compute(BASE, decisions=DEC)
    C, _ = compute(NEW, rule_version="v1.5")
    D, _ = compute(NEW)
    D_tsm24, _ = compute(NEW, obs_patch=tsm_rollback)

    bar = "=" * 118
    print(bar)
    print("F6-REG-28 — 14개사 전 factor 대조")
    print(bar)
    print("  A 승인 실행(v1.5·승계·결정 없음)  B 결정만  C 관측까지(v1.5)  D 새 실행(v1.7)  — 셀은 A>B>C>D")
    print()
    for cid in A:
        row = f"{cid:11}"
        for f in FACTORS:
            vals = [cell(S[cid][f]) for S in (A, B, C, D)]
            mark = " " if len(set(vals)) == 1 else "*"
            row += f"  {mark}{f}:" + ">".join(vals)
        print(row)

    for title, X, Y in (("[1] A→B  C-05·C-06·C-16 확정의 효과 (관측·규칙 동일)", A, B),
                        ("[2] B→C  관측 등록의 효과 (규칙·결정 동일, v1.5)", B, C),
                        ("[3] C→D  규칙 v1.7 전환의 효과 (관측·결정 동일)", C, D)):
        print()
        print(title)
        rows = [(cid, f, cell(X[cid][f]), cell(Y[cid][f])) for cid in X for f in FACTORS
                if cell(X[cid][f]) != cell(Y[cid][f])]
        print("  변화 없음" if not rows else "")
        for cid, f, x, y in rows:
            print(f"  {cid:11} {f}  {x:>22} -> {y}")

    print()
    print("[4] TSM FY2025 최신화만 떼어 낸 효과 (D 안에서 FY2024 로 되돌린 변형과 대조)")
    for f in FACTORS:
        a, b = cell(D_tsm24["tsmc"][f]), cell(D["tsmc"][f])
        if a != b:
            print(f"  tsmc        {f}  FY2024 {a:>8} -> FY2025 {b}")
    ma, _, ta = totals(D_tsm24["tsmc"])
    mb, _, tb = totals(D["tsmc"])
    print(f"  tsmc        총점  FY2024 {ta} -> FY2025 {tb}")
    d6 = (D_tsm24["tsmc"]["F6"].get("calc") or {}).get("parameters") or {}
    n6 = (D["tsmc"]["F6"].get("calc") or {}).get("parameters") or {}
    for pid in ("P1", "P2", "P3"):
        o, n = d6.get(pid) or {}, n6.get(pid) or {}
        if o.get("value") is not None and n.get("value") is not None:
            print(f"              {pid}  {o['value']:>10.3f}({o['score']:+d}) -> {n['value']:>10.3f}({n['score']:+d})")

    print()
    print("[5] 총점·순위")
    for label, S in (("A  승인 실행(v1.5)", A), ("D  새 실행(v1.7)", D)):
        rows = []
        for cid, fs in S.items():
            moat, trap, total = totals(fs)
            if total is not None:
                rows.append((total, moat, trap, cid))
        rows.sort(key=lambda r: (-r[0], -r[1], r[3]))
        print(f"  {label} — 완주 {len(rows)}/{len(S)}개사")
        prev, rank = None, 0
        for i, (total, moat, trap, cid) in enumerate(rows, 1):
            if total != prev:
                rank, prev = i, total
            print(f"    {rank:>2} {companies[cid]['display_name']:<20} 과점 {moat:>3} 함정 {trap:>3} 조정 {total:>3}")

    print()
    print("[6] 미완료 — D 새 실행")
    from scorecard.aggregate import COMPLETE_STATUSES
    for cid, fs in D.items():
        bad = [f for f in FACTORS if fs[f]["status"] not in COMPLETE_STATUSES]
        if bad:
            print(f"  {cid:11} " + "; ".join(
                f"{f} {fs[f]['status']}" + (f"({(fs[f].get('pending') or {}).get('decision_id')})"
                                            if (fs[f].get('pending') or {}).get('decision_id') else "")
                for f in bad))
            for f in bad:
                p = fs[f].get("pending")
                if p:
                    print(f"              {f}: {p['message'][:92]}")

    print()
    print("[7] 승인 실행 보존")
    appr = json.loads((BASE / "approval.json").read_text(encoding="utf-8"))["hashes"]
    from scorecard.stages import current_hashes
    cur, new = current_hashes(BASE.name), current_hashes(NEW.name)
    print(f"  {'대상':14} {'승인 baseline':>18} {'현재 baseline':>18} {'새 실행':>18}  보존")
    for k in ("rules", "observations", "judgments", "run", "results", "draft"):
        print(f"  {k:14} {appr[k][:16]:>18} {cur[k][:16]:>18} {new[k][:16]:>18}  {'예' if appr[k] == cur[k] else '아니오'}")
    for name in ("observations.json", "judgments.json", "run.json", "results.json"):
        h = hashlib.sha256((BASE / name).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        print(f"  baseline/{name:20} sha256(LF)={h[:24]}…")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
