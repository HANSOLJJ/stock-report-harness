# pretax_income_ttm 을 등록한다 — nonop_share 산식 정정의 입력 (보존 원자료만, 네트워크 없음)
"""**저장값이 옳고 재계산이 틀렸다.** 오늘까지 반대로 알고 있었다.

    저장 `nonop_share` = 영업외손익 ÷ 세전이익
    엔진 (정정 전)     = (순이익 − 영업이익) ÷ 순이익

두 군데가 다르고 **분자 쪽이 부호를 뒤집는다** — 영업외 항목이 없는 흑자 납세 기업은 순이익이
영업이익보다 작아 값이 늘 음수가 된다. 분모 쪽은 크기만 바꾼다.

정정 산식은 `(세전 − 영업이익) / 세전` 이고 **세전이익 하나만** 새로 들이면 된다.

사용:
    python validation/nonop-44/apply_pretax.py      # 여러 번 돌려도 같은 결과
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
SUFFIX = ".nonop44"
OBSERVED_AT = "2026-09-14"
SRC_FACTS = "SRC-SEC-FACTS-F6"
SRC_TSM = "SRC-SEC-TSM-20F-FY2025"
SRC_BABA = "SRC-SEC-BABA-FACTS"

sys.path.insert(0, str(HERE))
from measure_pretax import cross_check, pretax_ttm  # noqa: E402


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_observations, write_json

    rules = load_rules("v1.7")
    registry = {c["company_id"]: c
                for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    obs = load_json_strict(RUN / "observations.json")

    bar = "=" * 112
    print(bar)
    print(f"NONOP-44 — pretax_income_ttm 등록 · nonop_share 산식 정정 입력")
    print(bar)

    before = len(obs["items"])
    obs["items"] = [o for o in obs["items"] if not o["observation_id"].endswith(SUFFIX)]
    print(f"\n[0] 이전 회차 {before - len(obs['items'])}건 제거 — 멱등")

    by = {(o["company_id"], o["metric"]): o for o in obs["items"]}
    new: list[dict[str, Any]] = []
    skipped: list[tuple[str, str]] = []

    print(f"\n[1] 세전이익 TTM")
    print(f"  {'회사':11} {'세전(USD)':>18} {'검산 NI+tax':>12}  경로")
    for cid in sorted(registry):
        ni_obs = by.get((cid, "net_income_ttm"))
        oi_obs = by.get((cid, "operating_income_ttm"))
        if ni_obs is None or oi_obs is None or ni_obs.get("value") is None:
            skipped.append((cid, "net_income_ttm·operating_income_ttm 관측 없음(비상장)"))
            continue
        period = ni_obs.get("period") or {}
        r = pretax_ttm(cid, period["start"], period["end"])
        if r["pretax_usd"] is None:
            skipped.append((cid, "세전이익을 보존 원자료에서 복원하지 못함"))
            print(f"  {cid:11} {'복원 불가':>18} {'—':>12}")
            continue
        chk = cross_check(r["pretax_usd"], ni_obs["value"], r["tax_usd"])
        basis = {
            "measured_as_of": period["end"],
            "concept": r["concept"],
            "how_reconstructed": r["how"],
            "why_this_metric": "`nonop_share` 를 `(세전 − 영업이익) / 세전` 으로 고치기 위한 입력이다. "
                               "법인세를 순이익에 되더하는 대신 세전이익을 직접 들이면 지표 하나로 끝난다.",
            "cross_check_ni_plus_tax": {
                "tax_ttm_usd": r["tax_usd"], "tax_concept": r.get("tax_concept"),
                "relative_gap": chk,
                "note": "`세전 = 순이익 + 법인세` 가 성립해야 한다. 지분법 손익·비지배지분이 세전 **아래**에 "
                        "오는 회사는 어긋나고 그 크기가 여기 남는다.",
            },
        }
        if r["fx"] != 1.0:
            basis.update({"original_currency": r["unit"], "fx_rate": r["fx"],
                          "fx_rate_source": "20-F 자체 선언 편의환산 환율 (F6-REG-28 등록값과 동일)",
                          "pretax_native": r["pretax_native"]})
        src = {"tsmc": SRC_TSM, "alibaba": SRC_BABA}.get(cid, SRC_FACTS)
        new.append({
            "observation_id": f"{cid}.pretax_income_ttm{SUFFIX}", "company_id": cid,
            "metric": "pretax_income_ttm", "value": float(r["pretax_usd"]), "unit": "USD",
            "as_of": period["end"], "observed_at": OBSERVED_AT, "kind": "derived",
            "source_id": src, "status": "verified", "period": dict(period), "basis": basis,
            "raw": f"세전이익 TTM {r['pretax_usd']/1e9:,.1f}B USD",
            "note": "NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다",
        })
        print(f"  {cid:11} {r['pretax_usd']:>18,.0f} "
              f"{(f'{chk:+.6f}' if chk is not None else '—'):>12}  {str(r['how'])[:52]}")

    print(f"\n[2] 미등록 {len(skipped)}개사 — **왜 못 하는지 남긴다**")
    for cid, why in skipped:
        print(f"  {cid:11} {why}")

    for item in new:
        obs["items"].append(item)
    validate_observations(obs, registry, RUN_ID)

    run = load_json_strict(RUN / "run.json")
    run["rule_hash"] = rules.hash
    tag = "[NONOP-44] "
    run["assumptions"] = [a for a in run["assumptions"] if not a.startswith(tag)] + [tag + a for a in (
        "`nonop_share` 는 **영업외손익 ÷ 세전이익** 이다. 엔진이 쓰던 `(순이익 − 영업이익) ÷ 순이익` 은 "
        "분자에서 법인세를 안 되더하고 분모가 세전이 아니라 두 군데가 틀렸다. **저장값이 옳고 재계산이 "
        "틀렸다** — 보존 companyfacts 12건으로 역산해 11개사 중 9개가 맞는 것을 확인했다",
        "정정해도 P4 조건의 hit 여부가 한 곳도 안 바뀐다. 다만 amazon 이 임계 +2.4% 에서 +55.3% 로 "
        "멀어져 **경계 우려가 산식 정정으로 해소된다** — 경계 표시 자체는 유지한다",
        "spacex-xai 는 세전이익을 복원하지 못해 nonop_share 를 산출하지 않는다. 강등은 short_history 가 "
        "유지하므로 점수는 그대로다. 순이익·영업이익이 둘 다 음수라 **정정해도 부호 규약이 서지 않는다**",
    )]
    write_json(RUN / "observations.json", obs)
    write_json(RUN / "run.json", run)
    print(f"\n[3] 저장 — 관측 {len(obs['items'])}건 (신규 {len(new)})")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
