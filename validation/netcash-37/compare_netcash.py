# net_cash 실측 등록 전후로 14개사 전 factor 와 P2 내부값이 어떻게 바뀌는지 대조한다 (네트워크 없음)
"""**"점수가 안 바뀌었다" 는 주장은 대조표로만 성립한다.**

앞 열은 커밋된 결과(`git show HEAD:.../results.json`)이고 뒤 열은 지금 계산한 결과다. 같은 실행의
같은 파일을 시점만 달리 읽으므로 규칙·관측 변경의 효과가 그대로 드러난다.

P2 는 점수만 보면 안 된다. **밴드 안에서 값이 얼마나 움직였는지**를 같이 봐야 등록이 실제로
분자를 바꿨는지 알 수 있다. 그래서 EV/Sales 원값과 net_cash 를 함께 싣는다.

사용:
    python validation/netcash-37/compare_netcash.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
REL = f"scorecard/runs/{RUN_ID}/results.json"
FACTORS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")


def cell(f: dict[str, Any]) -> str:
    if f["status"] == "ok":
        return f"{f['score']:+d}" if f["score"] is not None else "ok?"
    if f["status"] == "carried_score":
        return f"{f['score']:+d}c" if f["score"] is not None else "carr"
    return {"pending_data": "pend", "needs_judgment": "judg",
            "pending_rule_decision": "rule"}.get(f["status"], f["status"][:4])


def head_results() -> dict[str, Any]:
    out = subprocess.run(["git", "show", f"HEAD:{REL}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"git show HEAD:{REL} 실패 — 커밋된 이전 결과가 없다")
    return json.loads(out.stdout.decode("utf-8", "replace"))


def p2_of(company: dict[str, Any]) -> dict[str, Any] | None:
    return ((company["factors"]["F6"].get("calc") or {}).get("parameters") or {}).get("P2")


def main() -> int:
    before = {c["company_id"]: c for c in head_results()["companies"]}
    after_doc = json.loads((ROOT / REL).read_text(encoding="utf-8"))
    after = {c["company_id"]: c for c in after_doc["companies"]}

    bar = "=" * 118
    print(bar)
    print("NETCASH-37 — net_cash 실측 등록 전후 대조 (앞=커밋된 결과, 뒤=지금 계산)")
    print(bar)

    print("\n[1] 14개사 전 factor")
    print(f"  {'회사':12} " + " ".join(f"{f:>9}" for f in FACTORS) + f" {'총점':>9} {'순위':>7}")
    changed: list[str] = []
    for cid in sorted(after):
        b, a = before.get(cid), after[cid]
        cells = []
        for fid in FACTORS:
            bc, ac = cell(b["factors"][fid]) if b else "—", cell(a["factors"][fid])
            cells.append(f"{ac:>9}" if bc == ac else f"{bc}→{ac:>4}")
            if bc != ac:
                changed.append(f"{cid}.{fid} {bc}→{ac}")
        bt, at = (b or {}).get("total"), a.get("total")
        br, ar = (b or {}).get("rank"), a.get("rank")
        tot = f"{at:>9}" if bt == at else f"{bt}→{at:>4}"
        rnk = f"{ar:>7}" if br == ar else f"{br}→{ar:>3}"
        print(f"  {cid:12} " + " ".join(cells) + f" {tot} {rnk}")
    print(f"\n  변화 {len(changed)}칸" + ("" if not changed else " — " + ", ".join(changed)))

    print("\n[2] P2 내부값 — **점수가 같아도 분자는 바뀌었다**")
    print(f"  {'회사':12} {'net_cash 전':>14} {'net_cash 후':>14} {'EV/S 전':>9} {'EV/S 후':>9} "
          f"{'P2':>5} {'상태':>8}")
    for cid in sorted(after):
        pb, pa = p2_of(before[cid]) if cid in before else None, p2_of(after[cid])
        if not pa or not pa.get("inputs"):
            print(f"  {cid:12} {'—':>14} {'—':>14} {'—':>9} {'—':>9} {'—':>5} P2 미산출")
            continue
        nb = (pb or {}).get("inputs", {}).get("net_cash")
        na = pa["inputs"].get("net_cash")
        vb, va = (pb or {}).get("value"), pa.get("value")
        state = "실측" if (pa.get("net_cash_definition") and na != nb) else "legacy 유지"
        print(f"  {cid:12} {(nb or 0)/1e9:>13,.1f}B {(na or 0)/1e9:>13,.1f}B "
              f"{(vb or 0):>9.3f} {(va or 0):>9.3f} {pa.get('score'):>+5d} {state:>10}")

    print("\n[3] 미검증 입력이 어떻게 줄었는가")
    for label, doc in (("전", head_results()), ("후", after_doc)):
        tally: dict[str, int] = {}
        for c in doc["companies"]:
            for metric in ((c["factors"]["F6"].get("calc") or {}).get("unverified_inputs") or {}):
                tally[metric] = tally.get(metric, 0) + 1
        print(f"  {label}: " + ", ".join(f"{m} {n}개사" for m, n in sorted(tally.items())))
    left = sorted(c["company_id"] for c in after_doc["companies"]
                  if "net_cash" in ((c["factors"]["F6"].get("calc") or {}).get("unverified_inputs") or {}))
    print(f"  남은 net_cash 미검증: {', '.join(left) or '없음'} — 등록하지 못한 3개사와 같아야 한다")

    print("\n[4] 완주·해시")
    pop = after_doc["population"]
    print(f"  채점 {pop['scored']}개사 · 미완료 {len(pop['incomplete'])}개사 · "
          f"미결 규칙 결정 {len(after_doc.get('pending_rule_decisions') or [])}건")
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.stages import current_hashes
    base = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
    appr = json.loads((base / "approval.json").read_text(encoding="utf-8"))["hashes"]
    now = current_hashes(base.name)
    same = now == appr
    print(f"  승인 대상 6종 보존: {'예' if same else '**아니오**'}")
    for key in sorted(appr):
        mark = "동일" if appr[key] == now.get(key) else "**다름**"
        print(f"    {key:14} {str(appr[key])[:16]}… {mark}")

    print()
    print(bar)
    ok = not changed and same and left == ["alibaba", "apple", "palantir"]
    print(f"판정: {'점수 불변 · 승인 보존 · 미검증 잔여가 미등록 3개사와 일치' if ok else '확인 필요'}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
