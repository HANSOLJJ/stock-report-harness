# 수집한 TTM 과 기존 시총·순현금 관측을 v1.7 규칙에 넣어 F6 를 산출하고 검산 기준과 대조한다 (네트워크 없음)
"""`collect_ttm.py` 산출 + 기존 관측(`market_cap`·`net_cash`·`nonop_share`)을 합쳐
**실제 계산기(`compute_f6`)를 그대로 태워** F6 를 낸다. 손으로 다시 계산하지 않는다.

검산 기준은 설계진행이 SEC 원자료로 직접 계산한 값이다. **정답으로 전제하지 않는다.**
그쪽 TTM 복원 로직도 검증된 것이 아니므로 불일치가 나오면 어느 쪽이 틀렸는지 가린다.

사용:
    python score_check.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"

# 검산 기준. 2026-09-11 재검토(F6-FIX-21)에서 oracle 이 -4 에서 **-3 으로 정정**됐다.
# TTM 창 끝점을 [A](복원 Q4 포함 최신 확보 분기)로 확정했고 설계진행 기준표와 C-13 검증기가 둘 다 틀렸다.
EXPECTED = {"tesla": -5, "oracle": -3, "apple": -4, "palantir": -4, "alphabet": -3,
            "microsoft": -3, "amazon": -2, "nvidia": -2, "meta": -1}
EXPECTED_P3 = {"nvidia": 0.834, "palantir": 0.789, "tsmc": 0.339, "meta": 0.277, "alphabet": 0.201,
               "microsoft": 0.179, "amazon": 0.158, "oracle": 0.1735, "apple": 0.142, "tesla": 0.118,
               "alibaba": 0.027}


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.calc_f6 import compute_f6                      # noqa: E402
    from scorecard.inputs import JudgmentLookup, ObsLookup        # noqa: E402
    from scorecard.rules import load_rules                        # noqa: E402
    from scorecard.schema import load_json_strict                 # noqa: E402

    rules = load_rules("v1.7")
    companies = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    base_obs = load_json_strict(RUN / "observations.json")["items"]
    run = load_json_strict(RUN / "run.json")
    ttm = {r["company_id"]: r for r in json.loads((HERE / "_derived" / "ttm_inputs.json").read_text(encoding="utf-8"))
           if r.get("loaded")}

    # 기존 관측에서 계산에 쓰는 것만 남기고, 수집한 TTM 을 관측 형태로 얹는다.
    keep = {"market_cap", "net_cash", "nonop_share", "post_money_valuation", "arr", "cumulative_raised"}
    obs_items = [o for o in base_obs if o["metric"] in keep]
    for cid, rec in ttm.items():
        for metric, m in rec["metrics"].items():
            if m.get("value") is None:
                continue
            obs_items.append({
                "observation_id": f"{cid}.{metric}.f6spec18", "company_id": cid, "metric": metric,
                "value": float(m["value"]), "unit": m.get("unit", "USD"), "as_of": "2026-09-10",
                "kind": "derived", "source_id": "SRC-sec-companyfacts", "status": "verified",
                "period": m.get("period"),
                "basis": {"period_basis": m["period_basis"], "taxonomy": m.get("taxonomy"), "tag": m.get("tag"),
                          "currency": m.get("unit")},
                "raw": None, "note": "F6-SPEC-18 수집기 산출",
            })
    obs = ObsLookup(obs_items)
    judgments = JudgmentLookup([])

    print("=" * 118)
    print("F6-SPEC-18 — v1.7 계산기로 F6 산출 후 검산 기준과 대조 (네트워크 없음)")
    print("=" * 118)
    print(f"\n{'회사':14} {'트랙':14} {'P1':>7} {'P2':>7} {'P3':>8} {'P4':>4} {'F6':>4} {'기준':>4} {'판정'}")

    results: dict[str, dict] = {}
    mismatch: list[str] = []
    for cid, company in companies.items():
        res = compute_f6(company, obs, judgments, rules, run)
        results[cid] = res
        calc = res["calc"]
        params = calc.get("parameters") or {}

        def cell(pid: str) -> str:
            e = params.get(pid) or {}
            v, s = e.get("value"), e.get("score")
            if v is None:
                return "-"
            return f"{v:.2f}({s})" if pid != "P3" else f"{v * 100:.1f}%({s})"

        p4 = (calc.get("p4") or {}).get("demotion_steps", 0)
        score = res["score"]
        want = EXPECTED.get(cid)
        if want is None:
            verdict = "기준 없음"
        elif score == want:
            verdict = "일치"
        else:
            verdict = "**불일치**"
            mismatch.append(cid)
        print(f"{cid:14} {str(calc.get('track','-')):14} {cell('P1'):>7} {cell('P2'):>7} {cell('P3'):>8} "
              f"{-p4:>4} {str(score):>4} {str(want):>4} {verdict}")

    print("\n[P3 대조] 성장률 자체를 검산 기준과 맞춰 본다")
    print(f"{'회사':14} {'내 산출':>10} {'기준':>10} {'차이':>10}  기간")
    for cid, res in results.items():
        e = ((res["calc"].get("parameters") or {}).get("P3") or {})
        v = e.get("value")
        w = EXPECTED_P3.get(cid)
        if v is None or w is None:
            continue
        rec = ttm.get(cid, {})
        per = (rec.get("metrics", {}).get("revenue_ttm", {}).get("period") or {})
        flag = "" if abs(v - w) < 0.005 else "  <-- 차이"
        print(f"{cid:14} {v * 100:>9.2f}% {w * 100:>9.1f}% {(v - w) * 100:>9.2f}%p  "
              f"{per.get('start','?')}~{per.get('end','?')}{flag}")

    print("\n[미산출] 점수를 만들지 않은 기업과 사유")
    for cid, res in results.items():
        if res["score"] is None:
            print(f"  {cid:14} {res['status']:22} {(res.get('pending') or {}).get('message', '')[:78]}")

    print("\n" + "=" * 118)
    scored = sum(1 for r in results.values() if r["score"] is not None)
    print(f"  점수 산출 {scored}/{len(results)} · 검산 기준 대조 {len(EXPECTED) - len(mismatch)}/{len(EXPECTED)} 일치")
    if mismatch:
        print(f"  불일치: {mismatch} — 어느 쪽이 틀렸는지 보고서에서 가린다")
    print("=" * 118)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
