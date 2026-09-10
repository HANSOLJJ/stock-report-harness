# 비상장 2사의 arr 계열 관측을 저장소 안에서만 추적해 값의 정체와 출처 사슬을 드러낸다 (네트워크 없음)
"""PRIV-ARR-17 의 저장소 추적 단계다. **네트워크를 쓰지 않는다.**

외부 수집은 약관 게이트에서 멈췄다(REPORT.md 1 절). 그래서 답할 수 있는 것은
저장소 안에 있는 것뿐이고, 실제로 항목 1·2·4 의 상당 부분이 여기서 끝난다.

이 스크립트가 드러내는 것.

    1 arr 관측의 kind 가 run_rate 라는 것 — 추정이 아니라 자료가 그렇게 적고 있다
    2 period 가 null 이라는 것
    3 같은 숫자가 contracted_revenue 에도 들어가 incompatible_basis 로 표시된다는 것
    4 출처 사슬이 URL 없는 v1.5 문서에서 끊긴다는 것
    5 arr_prior 가 스키마에 없다는 것

**값을 만들지 않는다.** 저장된 것을 그대로 보여 주고, 없으면 없다고 찍는다.

사용:
    python trace_repo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                      # worker/
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
COMPANIES = ("anthropic", "openai")
ARR_METRICS = ("arr", "contracted_revenue", "post_money_valuation", "cumulative_raised")
UNKNOWN = "없음"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard import schema                                    # noqa: E402

    obs = load(RUN / "observations.json")["items"]
    src = load(RUN / "sources.json")
    src_items = src.get("items") or src.get("sources") or []
    rules = load(ROOT / "scorecard" / "rules" / "v1.5.json")

    print("=" * 110)
    print("PRIV-ARR-17 — 비상장 2사 arr 계열 저장소 추적 (네트워크 없음)")
    print("=" * 110)

    print("\n[1] arr 계열 관측 원본 — kind 와 raw 를 그대로 낸다")
    print(f"{'회사':10} {'metric':22} {'value':>18} {'kind':>10} {'period':>8} {'status':>20}")
    rows = [o for o in obs if o["company_id"] in COMPANIES and o["metric"] in ARR_METRICS]
    for o in rows:
        v = f"{o['value']:,.0f}" if isinstance(o["value"], (int, float)) else str(o["value"])
        print(f"{o['company_id']:10} {o['metric']:22} {v:>18} {str(o['kind']):>10} "
              f"{str(o.get('period')):>8} {o['status']:>20}")
    print("\n  raw 원문 — 이관 시점의 표현이다. 여기에 '런레이트' 가 적혀 있다.")
    for o in rows:
        print(f"    {o['company_id']:10} {o['metric']:22} {o['raw']!r}")

    print("\n[2] kind 가 정식 종류인가 — 이름과 종류의 불일치를 가른다")
    print(f"  OBSERVATION_KINDS = {sorted(schema.OBSERVATION_KINDS)}")
    for o in rows:
        if o["metric"] == "arr":
            ok = o["kind"] in schema.OBSERVATION_KINDS
            print(f"  {o['company_id']:10} arr.kind = {o['kind']!r} → 스키마 정식 종류 {'맞음' if ok else '아님'}")
    print("  → metric 이름은 arr 인데 종류는 run_rate 다. 소비하는 쪽이 kind 를 안 보면 ARR 로 오독한다.")

    print("\n[3] 같은 숫자가 두 metric 에 들어갔는가")
    for c in COMPANIES:
        a = next((o for o in rows if o["company_id"] == c and o["metric"] == "arr"), None)
        k = next((o for o in rows if o["company_id"] == c and o["metric"] == "contracted_revenue"), None)
        if a and k:
            same = a["value"] == k["value"]
            print(f"  {c:10} arr {a['value']:,.0f} vs contracted_revenue {k['value']:,.0f} → "
                  f"{'같은 값' if same else '다른 값'} · contracted_revenue.status = {k['status']}")

    print("\n[4] 출처 사슬 — 어디서 끊기는가")
    used = sorted({o["source_id"] for o in rows})
    for sid in used:
        s = next((x for x in src_items if x.get("source_id") == sid), None)
        url = (s or {}).get("url")
        title = (s or {}).get("title") or (s or {}).get("note")
        print(f"  {sid:16} url={url if url else UNKNOWN:8}  {title}")
    print("  → URL 이 없으면 회사 공식 발표인지 2차 인용인지 가릴 수 없다. 등급을 매길 수 없다.")

    print("\n[5] 전년 비교에 필요한 것이 있는가")
    for want in ("arr_prior", "revenue_ttm_prior"):
        print(f"  스키마에 {want:20} {'있음' if want in schema.METRICS else UNKNOWN}")
    dates = sorted({o["as_of"] for o in obs if o["company_id"] in COMPANIES})
    print(f"  두 회사 관측의 as_of 집합: {dates} → 단일 시점이라 시계열이 없다")
    n = {c: sum(1 for o in obs if o["company_id"] == c) for c in COMPANIES}
    print(f"  관측 건수: {n}")

    print("\n[6] 관련 규칙 결정")
    for did in ("C-07", "C-12"):
        d = next((x for x in rules["decisions"] if x["id"] == did), None)
        if d:
            print(f"  {did} [{d['status']}] {d['summary']}")
            print(f"        권고: {d.get('recommendation', UNKNOWN)}")

    print("\n[7] 기준 대조 — 분기 매출과 런레이트가 같은 기준인가")
    note = next((o for o in obs if o["company_id"] == "anthropic" and o["metric"] == "quarter_note"), None)
    print(f"  anthropic quarter_note = {note['value']!r}" if note else f"  quarter_note {UNKNOWN}")
    q, rr = 10.9, 65.0                       # 위 note 문자열에서 읽은 값. 관측이 아니라 텍스트다.
    print(f"  Q2 {q}B → 월 {q / 3:.2f}B · 단순 연환산 {q * 4:.1f}B")
    print(f"  7월 런레이트 {rr}B → 월 {rr / 12:.2f}B")
    print(f"  월 환산 배수 {(rr / 12) / (q / 3):.2f}배 → 두 값을 같은 기준으로 다룰 수 없다")
    on = next((o for o in obs if o["company_id"] == "openai" and o["metric"] == "quarter_note"), None)
    print(f"  openai quarter_note = {on['value']!r}" if on else "")
    print("  → openai 는 분기 자리가 '—' 다. 분기 실적 수치가 아예 없다.")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
