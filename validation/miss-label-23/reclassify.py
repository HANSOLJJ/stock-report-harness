# 값이 없는 관측을 결측 유형 4종으로 재분류하고 점수가 바뀌지 않는지 실제 엔진으로 확인한다 (네트워크 없음)
"""`not_disclosed` 한 라벨이 네 뜻으로 쓰이던 것을 `missing_type` 으로 가른다.

## 승인 대상은 건드리지 않는다

`observations.json` 은 **승인 해시 대상**이다(`approval.json.hashes.observations`).
그래서 재분류를 파일에 쓰지 않고 **제안**으로 내고, 효과는 메모리에서 적용해 확인한다.
실제 반영은 새 실행과 승인을 거쳐야 하며 그것은 사용자 결정이다.

## 보수 원칙

**`raw` 가 '미확인' 인 것을 '미공시' 로 승격하지 않는다.** 판단이 서지 않으면 `unverified` 로 둔다.
틀리는 방향의 비용이 다르기 때문이다.

    unverified 로 잘못 두면   → 안 찾아도 될 것을 더 찾는다. 점수는 틀리지 않는다
    미공시로 잘못 올리면       → **우리가 안 찾은 것이 그 기업의 위험으로 둔갑한다**

사용:
    python reclassify.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
OUT = HERE / "_derived"

NOT_APPLICABLE_RAW = {"∞", "적자"}
CONFIRMED_RAW = {"미공시"}
UNVERIFIED_RAW = {"미확인"}

# 공시 의무가 없는 기업(비상장)에 적용하는 **구조 기준** (MISS-LABEL-23 보완, 설계진행 확정 문구).
#
#   "공시 의무가 없는 기업의 지표가 감사 재무제표 항목이거나 그로부터만 도출되는 값이면
#    not_disclosed_confirmed 로 두고 그 외에는 raw 문구를 따른다."
#
# 근거는 우리의 탐색량이 아니라 **구조**다. 감사 재무제표를 제출할 의무가 없는 기업의
# 재무제표 항목은 정의상 공개된 적이 없다. 그래서 '우리가 안 찾아서' 가 아니라
# '있을 수 없어서' 없는 것이고, 승격 금지 원칙(문서 상단)에 걸리지 않는다.
#
# 반대로 **상장사에는 이 논거가 성립하지 않는다.** 정기보고서에 있을 수 있으므로
# palantir.net_borrowing_ttm(raw='없음') 같은 것은 계속 unverified 로 남는다.
AUDITED_STATEMENT_METRICS = {
    # 재무제표 본문 항목
    "revenue_ttm", "revenue_ttm_prior", "operating_income_ttm", "net_income_ttm",
    "ocf_ttm", "capex_ttm", "cash", "undrawn_credit", "net_borrowing_ttm",
    # 본문 항목에서만 도출되는 값
    "fcf_ttm", "net_cash", "debt_ebitda", "operating_margin_ttm", "nonop_share", "runway_years",
    # 감사 재무제표의 **주석** 공시 항목 (ASC 606 잔여 수행의무·부외 약정)
    "contracted_revenue", "offbalance_B",
}
# 제외 — 시장가·컨센서스·자금조달 발표가 섞여 재무제표에서만 도출되지 않는다.
#   price, market_cap, ttm_per, ps_ratio, ntm_*, credit_rating, cds_5y_bp,
#   post_money_valuation, arr, ttm_revenue_est, cumulative_raised
G4_METRICS = {"contracted_revenue", "offbalance_B"}
# NTM 조사(OFFB-24) 결과가 아직 미검증이라 이 셋은 **잠정**이다. 설계진행 회신 전까지 확정하지 않는다.
PROVISIONAL = {("spacex-xai", "offbalance_B"), ("alibaba", "offbalance_B"),
               ("amazon", "contracted_revenue")}


def classify(o: dict, company: dict) -> tuple[str, str]:
    """(결측 유형, 사유). **애매하면 unverified 다.**"""
    raw = (o.get("raw") or "").strip()
    status = o["status"]

    # (1) 개념상 값이 없는 것이 먼저다. 구조 기준은 '미공시냐 미확인이냐' 를 가르는 규칙이지,
    #     '정의되지 않음'·'산출 불가' 를 미공시로 바꾸는 규칙이 아니다.
    #     그래서 비상장 runway_years(raw='판정 불가') 는 구조 기준 대상 지표여도 indeterminate 로 남는다.
    if raw == "∞":
        return "not_applicable", "FCF 양수라 런웨이가 개념상 정의되지 않는다(설계 지침 6.2)"
    if raw == "적자":
        return "not_applicable", "적자라 PER·영업외 비중이 개념상 정의되지 않는다"
    if raw == "판정 불가":
        return "indeterminate", "선행 입력(현금·FCF)이 결측이라 산출할 수 없다"

    # (2) 구조 기준 — 공시 의무 자체가 없으면 재무제표 항목은 정의상 공개된 적이 없다.
    if not company["listed"] and o["metric"] in AUDITED_STATEMENT_METRICS:
        return "not_disclosed_confirmed", ("비상장이라 감사 재무제표 제출 의무가 없고 이 지표는 그 재무제표 "
                                           f"항목이거나 그로부터만 도출된다(raw={raw!r}) — 구조적으로 확인된 미공시")

    # (3) 그 외에는 raw 문구를 따른다.
    if raw in UNVERIFIED_RAW:
        return "unverified", "raw 가 '미확인' — 우리가 확인하지 않았다. 승격 금지 대상"
    if raw in CONFIRMED_RAW:
        return "unverified", "raw 는 '미공시' 이나 상장사라 정기보고서에 있을 수 있다 — 확인 전까지 보류"
    if status == "parse_failed":
        return "unverified", "파싱 실패는 확인이 아니다 — 재파싱 대상(C-13 담당)"
    return "unverified", f"raw={raw!r} 로는 미공시인지 미확인인지 갈리지 않는다 — 보수적으로 미확인"


def scores(obs_items: list[dict], companies: dict, judgments, rules, run) -> dict[str, dict]:
    """실제 엔진(compute_company)으로 factor 점수를 낸다. 손으로 다시 계산하지 않는다."""
    from scorecard.engine import compute_company
    from scorecard.inputs import ObsLookup

    lookup = ObsLookup(obs_items)
    out = {}
    for cid, c in companies.items():
        factors = compute_company(c, lookup, judgments, rules, run)
        out[cid] = {fid: (f["score"], f["status"]) for fid, f in factors.items()}
    return out


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.inputs import JudgmentLookup
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict

    companies = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    obs_items = load_json_strict(RUN / "observations.json")["items"]
    judgments = JudgmentLookup(load_json_strict(RUN / "judgments.json")["items"])
    run = load_json_strict(RUN / "run.json")
    rules = load_rules(run["rule_version"])

    bar = "=" * 112
    print(bar)
    print("MISS-LABEL-23 — 결측 라벨 재분류 (승인 대상 미변경 · 네트워크 없음)")
    print(bar)

    nulls = [o for o in obs_items if o["value"] is None]
    print()
    print(f"[1] 값이 없는 관측 {len(nulls)}건 / 전체 {len(obs_items)}건")
    print(f"{'회사':12} {'metric':22} {'status':16} {'raw':14} -> {'결측 유형':24} 사유")
    proposal: dict[str, dict] = {}
    for o in sorted(nulls, key=lambda x: (x["company_id"], x["metric"])):
        mtype, why = classify(o, companies[o["company_id"]])
        prov = (o["company_id"], o["metric"]) in PROVISIONAL
        proposal[o["observation_id"]] = {"company_id": o["company_id"], "metric": o["metric"],
                                         "status": o["status"], "raw": o.get("raw"),
                                         "missing_type": mtype, "reason": why,
                                         "provisional": prov,
                                         "provisional_reason": "NTM OFFB-24 조사 결과 미검증 — 설계진행 회신 대기" if prov else None}
        print(f"{o['company_id']:12} {o['metric']:22} {o['status']:16} {str(o.get('raw'))[:14]:14} -> "
              f"{mtype:24} {'[잠정] ' if prov else ''}{why[:40]}")

    print()
    print("[2] 재분류 전후 — 한 라벨이 몇 갈래로 갈렸나")
    before: dict[str, int] = {}
    after: dict[str, int] = {}
    for o in nulls:
        before[o["status"]] = before.get(o["status"], 0) + 1
        mt = proposal[o["observation_id"]]["missing_type"]
        after[mt] = after.get(mt, 0) + 1
    print("  전: " + ", ".join(f"{k}={v}" for k, v in sorted(before.items())))
    print("  후: " + ", ".join(f"{k}={v}" for k, v in sorted(after.items())))

    print()
    print("[3] C-16 진입 대상 — 확인된 미공시만 들어간다")
    print("    **가정: coverage_comparable = yes.** _g4() 는 그 판단이 yes 가 아니면 결측 유형을 보기 전에")
    print("    먼저 undetermined 로 빠져나간다. 아래 숫자는 그 관문을 통과했다고 놓았을 때의 수다.")
    before_c16: set[str] = set()
    after_c16: set[str] = set()
    by_company: dict[str, list] = {}
    for o in nulls:
        if o["metric"] in G4_METRICS:
            by_company.setdefault(o["company_id"], []).append(o)
    for cid, items in sorted(by_company.items()):
        old_ok = all(o["status"] == "not_disclosed" for o in items)
        new_ok = all(proposal[o["observation_id"]]["missing_type"] == "not_disclosed_confirmed" for o in items)
        if old_ok:
            before_c16.add(cid)
        if new_ok:
            after_c16.add(cid)
        marks = ", ".join(f"{o['metric']}={proposal[o['observation_id']]['missing_type']}" for o in items)
        cov = (judgments.get(cid, "F9") or {}).get("inputs", {}).get("coverage_comparable")
        print(f"  {cid:12} 전 {'진입' if old_ok else '제외':4} -> 후 {'진입' if new_ok else '제외':4}"
              f"  (coverage_comparable={cov})  ({marks})")
    dropped = sorted(before_c16 - after_c16)
    print(f"  -> 가정하의 C-16 진입 대상 {len(before_c16)}개사 -> {len(after_c16)}개사"
          + (f" · 빠짐: {dropped}" if dropped else ""))

    # 실제로 이번 실행에서 C-16 에 도달한 기업 수 — 가정을 걷어낸 숫자다.
    cov_counts: dict[str, int] = {}
    real_before = []
    for cid in sorted(companies):
        cov = (judgments.get(cid, "F9") or {}).get("inputs", {}).get("coverage_comparable")
        cov_counts[str(cov)] = cov_counts.get(str(cov), 0) + 1
        if cov == "yes" and cid in before_c16:
            real_before.append(cid)
    print(f"  -> 실제 도달: {len(real_before)}개사 (coverage_comparable 분포 "
          + ", ".join(f"{k}={v}" for k, v in sorted(cov_counts.items())) + ")")
    print("     이 변경 이전에도 C-16 에 실제로 닿는 기업은 0개사였다. 2 -> 0 은 '2개사가 빠졌다' 가 아니라")
    print("     '검토 입력이 채워졌을 때 들어갔을 2개사가 이제는 들어가지 않는다' 는 뜻이다.")

    print()
    print("[3b] 잠정 표시 — NTM OFFB-24 조사 결과가 미검증인 셋")
    for oid, v in sorted(proposal.items()):
        if v["provisional"]:
            print(f"  {v['company_id']:12} {v['metric']:22} {v['missing_type']:24} {v['provisional_reason']}")
    print("  이 셋은 확정이 아니다. 조사 결과에 따라 not_disclosed_confirmed 로 올라갈 수 있다.")

    print()
    print("[4] 점수 불변 확인 — 재분류를 메모리에서 적용해 실제 엔진으로 재계산")
    base = scores(obs_items, companies, judgments, rules, run)
    patched = []
    for o in obs_items:
        if o["observation_id"] in proposal:
            o = {**o, "missing_type": proposal[o["observation_id"]]["missing_type"]}
        patched.append(o)
    after_scores = scores(patched, companies, judgments, rules, run)
    changed = []
    for cid in base:
        for fid in base[cid]:
            if base[cid][fid] != after_scores[cid][fid]:
                changed.append([cid, fid, list(base[cid][fid]), list(after_scores[cid][fid])])
    if changed:
        print("  **점수가 바뀐 항목**")
        for cid, fid, b, a in changed:
            print(f"    {cid:12} {fid}  {b} -> {a}")
    else:
        print(f"  {len(base)}개사 전 factor 점수·상태 불변")

    OUT.mkdir(exist_ok=True)
    (OUT / "reclassification.json").write_text(json.dumps({
        "note": "제안이다. observations.json 은 승인 해시 대상이라 반영은 새 실행·승인을 거친다.",
        "run_id": run.get("run_id"), "count": len(proposal),
        "score_changes": changed, "items": proposal,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(f"_derived/reclassification.json 저장 — {len(proposal)}건 제안")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
