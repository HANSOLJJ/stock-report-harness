# v1.7 F6 가 요구하는 입력 4종을 12개사에 등록하고 TSM FY2025·C-16·AMZN 근거 보강을 함께 반영한다
"""**승인된 실행은 건드리지 않는다.** 대상은 `ai-scorecard-2026-09-obsreg` 뿐이다.

## 통화를 어떻게 다뤘나 — 이번 과제의 핵심 판단

지표 단위가 `USD` 로 고정돼 있어 TWD·CNY 를 그대로 둘 자리가 없다. 그런데 **공시 USD 환산치를
두 해 그대로 쓰면 안 된다.** 두 해의 convenience translation 환율이 서로 다른 20-F 에서 오기
때문이다. `verify_inputs.py` 가 실측으로 보인다.

    alibaba  현지통화 +2.74%(밴드 -3)  ·  공시 USD 그대로 +8.09%(밴드 -2)   ← 한 칸 뜬다
    tsmc     현지통화 +33.89%(밴드 0)  ·  공시 USD 그대로 +25.03%(밴드 -1)  ← 한 칸 뜬다

규칙이 P3 에 "현지통화로 계산한다"고 적어 둔 이유가 이것이다(`parameters.P3.currency_note`).
그래서 **당해와 전년을 같은 환율로 환산한다.** 환율이 분자·분모에서 상쇄돼 성장률이 현지통화와
같아지고, 동시에 P2 는 USD 시총과 같은 단위가 된다. 환산하지 않으면 TSM 의 P2 가 -2 에서 0 으로
두 칸 뜬다(EV/Sales 23.5 → 0.72).

환율은 **20-F 가 스스로 선언한 값**을 쓴다. 외부 환율 출처를 새로 끌어오지 않는다.

## 왜 SPCX 만 quarterly_yoy 인가

SPCX 는 현재 TTM 은 복원되지만(S-1/A FY2025 + 10-Q 상반기) **전년 TTM 은 복원되지 않는다** —
2024년 상반기 사실이 어느 문서에도 없다. P3 는 전년이 있어야 성립하므로 `listed_ttm` 으로 두면
F6 가 미완료가 된다. 반면 분기 전년 동기는 10-Q 에 둘 다 있다. `listed_newly` 트랙이 정확히 이
상황을 위해 있고(`select`: 연간 기간 사실이 없어 P1·P2 가 성립하지 않는 기업), `short_history`
로 한 칸 내린다. **자료가 없다고 무른 트랙으로 내려보내는 것이 아니라, 전년 대조가 성립하지
않는다는 구조적 사실이 트랙을 정한다.**

다만 `operating_margin_ttm`·`operating_income_ttm`·`net_income_ttm` 은 TTM 으로 등록한다.
F9 G1 이 그것을 요구하고 TTM 이 실제로 복원되기 때문이다. 매출 쌍만 분기 기준이고, `listed_newly`
트랙은 매출과 손익을 함께 쓰는 계산(P2)을 하지 않으므로 기준이 섞여 계산되는 자리는 없다.

사용:
    python validation/f6-reg-28/apply_f6_inputs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
SPEC18 = ROOT / "validation" / "f6-spec-18" / "_derived" / "ttm_inputs.json"

OBSERVED_AT = "2026-09-11"          # 우리가 원자료를 연 날. 자료 기준일(as_of)과 다른 축이다.

# 20-F 가 스스로 선언한 convenience translation 환율. 당해·전년에 **같은 값**을 쓴다.
FX = {
    "alibaba": {"currency": "CNY", "rate": 6.8980, "as_of": "2026-03-31",
                "declared_in": "FY2026 20-F 'Exchange Rate Information' — RMB6.8980 to US$1.00, "
                               "the exchange rate on March 31, 2026 set forth in the H.10 statistical "
                               "release of the Federal Reserve Board"},
    "tsmc": {"currency": "TWD", "rate": 31.37, "as_of": "2025-12-31",
             "declared_in": "FY2025 20-F Note 3 'U.S. DOLLAR AMOUNTS' (F-13) — NT$31.37 to US$1.00, "
                            "the exchange rate set forth in the H.10 statistical release of the "
                            "Federal Reserve Board on December 31, 2025"},
}

# G1-FILL-27 이 낸 TTM(설계진행 재현 확인). revenue_ttm·operating_income_ttm 의 기준값이다.
# TSM 은 아래 TSM_FY2025 가 덮어쓴다.
G1_BLOB = ("1badc57", "validation/g1-fill-27/g1_fill_27_results.json")

# TSM FY2025 — companyfacts 미등재로 EDGAR 원문 우회 (C-13 TSM-EDGAR-29, f14a235)
TSM_FY2025 = {
    "accession": "0001628280-26-025362", "form": "20-F", "filed": "2026-04-16",
    "period": {"start": "2025-01-01", "end": "2025-12-31"},
    "statement": "CONSOLIDATED STATEMENTS OF PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME (F-6)",
    "column": "표는 2023·2024·2025 **오름차순**이고 최신은 **셋째 NT$ 열**이다(그 오른쪽이 US$ (Note 3) 열). "
              "열을 잘못 읽으면 FY2023 값을 최신으로 등록하게 된다.",
    "revenue_twd": 3_809_054_300_000,
    "operating_income_twd": 1_936_091_700_000,
    "net_income_twd": 1_695_124_900_000,
    "prior_revenue_twd": 2_894_307_700_000,          # FY2024, 같은 표 둘째 열
    "filed_usd": {"revenue": 121_423_500_000, "operating_income": 61_717_900_000,
                  "net_income": 54_036_500_000},
    "bypass": {
        "why": "SEC companyfacts 에 accession 0001628280-26-025362 의 ifrs-full 재무 사실이 미등재다. "
               "**회사 미공시가 아니라 데이터셋 결측이다** — 20-F 는 2026-04-16 에 제출됐다.",
        "authorized_by": "F6-FX-16 우회 3조건",
        "conditions_met": [
            "(1) 우회 사실을 관측에 기록한다 — 이 basis.bypass 가 그것이다",
            "(2) FY2024 를 두 경로로 검산해 일치를 확인한다 — companyfacts 2,894,307,700,000 / "
            "1,322,053,000,000 과 원문 2,894,307.7 / 1,322,053.0 백만이 정확히 일치한다(C-13 재현, "
            "나 자신도 원문 F-6 표에서 재확인)",
            "(3) companyfacts 에 반영되면 원천을 되돌린다 — 아래 rollback",
        ],
        "rollback": "SEC companyfacts 에 accession 0001628280-26-025362 의 ifrs-full 태그가 반영되면 "
                    "이 관측을 companyfacts 원천으로 다시 뽑아 교체한다. 값이 다르면 보고한다.",
        "raw_sha256": "c3ebd05cd8fb383f53fc21a0ac497ee12cf908b709c380f9bec4f39c4916647b",
        "raw_preserved": "C-13 f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm",
    },
}

SOURCES = [
    {"source_id": "SRC-SEC-FACTS-F6", "title": "SEC XBRL companyfacts 12개사 (F6 TTM 입력 재구성)",
     "publisher": "SEC EDGAR", "url": "https://data.sec.gov/api/xbrl/companyfacts/",
     "accessed_at": "2026-09-10", "sha256": None, "conflict_of_interest": None,
     "note": "원문 보존 validation/f6-avail-15/_raw/*.companyfacts.json (2026-09-10 수집). "
             "이번 과제에서 신규 호출 없음. 재구성 절차는 validation/f6-spec-18/collect_ttm.py"},
    {"source_id": "SRC-SEC-TSM-20F-FY2025",
     "title": "TSMC Form 20-F (FY2025, 2025-12-31) — 연결손익계산서 F-6 · 환율 Note 3 (F-13)",
     "publisher": "SEC EDGAR",
     "url": "https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/tsm-20251231.htm",
     "accessed_at": "2026-09-11",
     "sha256": "c3ebd05cd8fb383f53fc21a0ac497ee12cf908b709c380f9bec4f39c4916647b",
     "conflict_of_interest": None,
     "note": "접수번호 0001628280-26-025362(2026-04-16). **companyfacts 미등재 우회 건**이다 — "
             "F6-FX-16 3조건 충족. 원문 보존 C-13 f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm"},
]


def load_g1() -> dict:
    import subprocess
    out = subprocess.run(["git", "show", f"{G1_BLOB[0]}:{G1_BLOB[1]}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit("G1-FILL-27 blob 을 읽지 못했다")
    return {it["company_id"]: it for it in json.loads(out.stdout.decode("utf-8", "replace"))["items"]}


def usd(value: float, cid: str) -> float:
    """현지통화를 **선언 환율**로 환산한다. 당해·전년에 같은 값을 써야 성장률이 왜곡되지 않는다."""
    return round(value / FX[cid]["rate"], 0)


def fx_basis(cid: str, local_value: float, cross_check: float | None = None) -> dict:
    f = FX[cid]
    out = {"original_currency": f["currency"], "original_value": local_value,
           "fx_rate": f["rate"], "fx_quote": f"{f['currency']} per USD", "fx_rate_as_of": f["as_of"],
           "fx_rate_source": f["declared_in"],
           "fx_uniform_rate_note": "**당해와 전년에 같은 환율을 쓴다.** 공시 USD 환산치는 두 해가 서로 다른 "
                                   "20-F 에서 와 환율이 다르고, 그대로 쓰면 P3 성장률 밴드가 한 칸 뜬다"
                                   "(verify_inputs.py [3]). 같은 환율이면 분자·분모에서 상쇄돼 현지통화 "
                                   "성장률과 같아진다."}
    if cross_check is not None:
        got = local_value / f["rate"]
        out["cross_check_filed_usd"] = {"filed": cross_check, "recomputed": round(got, 0),
                                        "rel_diff": abs(got - cross_check) / abs(cross_check)}
    return out


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_judgments, validate_observations, write_json

    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    g1 = load_g1()
    spec18 = {x["company_id"]: x for x in json.loads(SPEC18.read_text(encoding="utf-8"))}

    bar = "=" * 118
    print(bar)
    print(f"F6-REG-28 — {RUN_ID} 에 F6 입력 등록 (승인 실행 미변경 · 신규 네트워크 없음)")
    print(bar)

    new_obs: list[dict] = []

    def add(cid: str, metric: str, value, *, as_of: str, period: dict | None, basis: dict,
            source_id: str, raw: str, note: str, kind: str = "actual"):
        new_obs.append({
            "observation_id": f"{cid}.{metric}.f6reg28", "company_id": cid, "metric": metric,
            "value": None if value is None else float(value),
            "unit": {"operating_margin_ttm": "ratio"}.get(metric, "USD"),
            "as_of": as_of, "observed_at": OBSERVED_AT, "kind": kind, "source_id": source_id,
            "status": "verified", **({"period": period} if period else {}),
            "basis": basis, "raw": raw, "note": note,
        })

    # ---------------------------------------------------------------- 12개사 F6 입력
    for cid in sorted(g1):
        it = g1[cid]
        m = spec18[cid]["metrics"]
        local = cid in FX
        period = {"start": it["period_start"], "end": it["period_end"]}
        pb = "annual" if it["period_basis"].startswith("annual") else (
            "quarterly_yoy" if cid == "spacex-xai" else "ttm")

        if cid == "tsmc":
            # FY2025 로 갱신한다. companyfacts 는 FY2024 까지뿐이라 EDGAR 원문 우회 건이다.
            t = TSM_FY2025
            period = t["period"]
            src = "SRC-SEC-TSM-20F-FY2025"
            common = {"statement": t["statement"], "column": t["column"], "accession": t["accession"],
                      "form": t["form"], "filed": t["filed"], "bypass": t["bypass"],
                      "period_basis": "annual",
                      "months_since_period_end": 8,
                      "staleness_note": "기준일 2026-09-02 대비 8개월 경과. FY2024 를 쓰면 20개월이었다."}
            add(cid, "revenue_ttm", usd(t["revenue_twd"], cid), as_of=period["end"], period=period,
                basis={**common, **fx_basis(cid, t["revenue_twd"], t["filed_usd"]["revenue"])},
                source_id=src, raw=f"FY2025 매출 NT${t['revenue_twd']/1e6:,.1f}백만 (US${t['filed_usd']['revenue']/1e6:,.1f}백만)",
                note="F6-REG-28 / TSM-EDGAR-29. **EDGAR 원문 우회 건**이다 — basis.bypass 에 사유·검산·복귀 조건을 남겼다")
            add(cid, "revenue_ttm_prior", usd(t["prior_revenue_twd"], cid),
                as_of="2024-12-31", period={"start": "2024-01-01", "end": "2024-12-31"},
                basis={**common, **fx_basis(cid, t["prior_revenue_twd"]),
                       "same_rate_as_current": True,
                       "why_not_filed_usd": "FY2024 20-F 의 공시 USD 70,598.8 은 그 해 환율 30.62 로 환산된 값이다. "
                                            "그대로 쓰면 성장률이 +33.89% 대신 +25.03% 가 되어 밴드가 한 칸 뜬다."},
                source_id=src, raw=f"FY2024 매출 NT${t['prior_revenue_twd']/1e6:,.1f}백만 (같은 표 둘째 열)",
                note="F6-REG-28. **당해와 같은 환율 31.37 로 환산**했다. 공시 USD 를 그대로 쓰지 않았다")
            add(cid, "net_income_ttm", usd(t["net_income_twd"], cid), as_of=period["end"], period=period,
                basis={**common, **fx_basis(cid, t["net_income_twd"], t["filed_usd"]["net_income"])},
                source_id=src, raw=f"FY2025 순이익 NT${t['net_income_twd']/1e6:,.1f}백만",
                note="F6-REG-28 / TSM-EDGAR-29. 손익계산서 NET INCOME 행")
            add(cid, "operating_income_ttm", usd(t["operating_income_twd"], cid), as_of=period["end"],
                period=period,
                basis={**common, **fx_basis(cid, t["operating_income_twd"], t["filed_usd"]["operating_income"])},
                source_id=src, raw=f"FY2025 영업이익 NT${t['operating_income_twd']/1e6:,.1f}백만",
                note="F6-REG-28 / TSM-EDGAR-29. INCOME FROM OPERATIONS 행. "
                     "MD&A 반올림 1,936,092 가 아니라 **감사 손익계산서 본문 1,936,091.7** 이다")
            margin = t["operating_income_twd"] / t["revenue_twd"]
            add(cid, "operating_margin_ttm", round(margin, 6), as_of=period["end"], period=period,
                basis={**common, "formula": "INCOME FROM OPERATIONS / NET REVENUE (같은 통화·같은 기간)",
                       "numerator_twd": t["operating_income_twd"], "denominator_twd": t["revenue_twd"],
                       "currency_note": "비율이라 통화가 상쇄된다"},
                source_id=src, kind="derived", raw=f"FY2025 영업이익률 +{margin*100:.2f}%",
                note="F6-REG-28 / TSM-EDGAR-29. FY2024 45.68% 에서 +5.15%p")
            continue

        src = "SRC-SEC-FACTS-F6"
        base = {"period_basis": pb, "reconstruction": it["reconstruction_status"],
                "method": (it.get("components") or {}).get("method"),
                "components": it.get("components")}
        if cid == "spacex-xai":
            # 매출 쌍만 분기 기준이다. 전년 TTM 이 복원되지 않는다.
            q = m["revenue_ttm"]; qp = m["revenue_ttm_prior"]
            why = ("전년 TTM(2024-07-01~2025-06-30)은 복원되지 않는다 — FY2024 + H1'25 - H1'24 인데 "
                   "**H1'24 사실이 어느 문서에도 없다**(S-1/A 는 연간 3개년과 1분기만, 10-Q 는 2025·2026 "
                   "상반기만 준다). P3 는 전년이 있어야 성립하므로 분기 전년 동기로 간다 — listed_newly 트랙이 "
                   "정확히 이 상황을 위해 있고 short_history 로 한 칸 내린다.")
            add(cid, "revenue_ttm", q["value"], as_of=q["period"]["end"], period=q["period"],
                basis={"period_basis": "quarterly_yoy", "why_not_ttm": why,
                       "ttm_is_constructible": {"value": 23_044_000_000,
                                                "method": "S-1/A FY2025 18,674 + 10-Q H1'26 12,508 - H1'25 8,138",
                                                "note": "당해 TTM 은 만들 수 있으나 전년이 없어 P3 가 성립하지 않는다"},
                       "tag": q["tag"], "accession": "0001628280-26-052535", "form": "10-Q"},
                source_id=src, raw="2026 Q2 매출 $7,814M", note="F6-REG-28. **분기 전년 동기 기준이다**")
            add(cid, "revenue_ttm_prior", qp["value"], as_of=qp["period"]["end"], period=qp["period"],
                basis={"period_basis": "quarterly_yoy", "tag": qp["tag"],
                       "accession": "0001628280-26-052535", "form": "10-Q"},
                source_id=src, raw="2025 Q2 매출 $4,071M", note="F6-REG-28. 같은 분기 전년 동기")
            # 손익은 TTM 으로 등록한다. F9 G1 이 그것을 요구하고 실제로 복원된다.
            ttm_note = ("S-1/A 감사 손익계산서 FY2025 + 10-Q 2026 상반기 - 10-Q 2025 상반기. "
                        "**매출 쌍(분기)과 기준이 다르다.** listed_newly 트랙은 매출과 손익을 함께 쓰는 "
                        "계산(P2)을 하지 않으므로 기준이 섞여 계산되는 자리는 없다.")
            tt = {"start": "2025-07-01", "end": "2026-06-30"}
            for metric, val, comp in (("operating_income_ttm", -3_732_000_000, (-2_589, -2_086, -943)),
                                      ("net_income_ttm", -8_218_000_000, (-4_937, -4_817, -1_536))):
                add(cid, metric, val, as_of=tt["end"], period=tt, kind="derived",
                    basis={"period_basis": "ttm", "method": "FY2025 + H1'2026 - H1'2025",
                           "components": {"fy2025_s1a": comp[0] * 1_000_000,
                                          "h1_2026_10q": comp[1] * 1_000_000,
                                          "h1_2025_10q": comp[2] * 1_000_000},
                           "sources": {"fy2025": "S-1/A 0001628280-26-040364 연결손익계산서",
                                       "half_years": "10-Q 0001628280-26-052535 companyfacts"},
                           "basis_mismatch_note": ttm_note},
                    source_id=src, raw=f"TTM {val/1e6:,.0f}백만", note="F6-REG-28. " + ttm_note)
            margin = -3_732_000_000 / 23_044_000_000
            add(cid, "operating_margin_ttm", round(margin, 6), as_of=tt["end"], period=tt, kind="derived",
                basis={"period_basis": "ttm", "formula": "TTM 영업손익 / TTM 매출",
                       "numerator": -3_732_000_000, "denominator": 23_044_000_000,
                       "method": "FY2025 + H1'2026 - H1'2025 (양쪽 다)",
                       "replaces": "spacex-xai.operating_margin_ttm.v15 (-0.149, legacy_unverified)",
                       "delta_vs_legacy_pp": round((margin - (-0.149)) * 100, 2)},
                source_id=src, raw=f"TTM 영업손실률 {margin*100:.3f}%",
                note="F6-REG-28. 승계 legacy -14.9% 를 실측 -16.195% 로 교체한다. "
                     "재척도 밴드에서 둘 다 -3 이라 점수는 안 바뀌고 근거가 legacy 에서 실측으로 바뀐다")
            continue

        if local:   # alibaba — revenue_ttm·operating_income_ttm 은 OBS-REG-25 에서 이미 등록했다
            for metric, key, filed in (("net_income_ttm", "net_income_ttm", 15_018_000_000),
                                       ("revenue_ttm_prior", "revenue_ttm_prior", None)):
                mm = m[key]
                extra = {}
                if metric == "revenue_ttm_prior":
                    extra = {"same_rate_as_current": True,
                             "why_not_filed_usd": "FY2025 20-F 의 공시 USD 137,300 은 그 해 환율 7.2567 로 환산된 "
                                                  "값이다. 그대로 쓰면 성장률이 +2.74% 대신 +8.09% 가 되어 밴드가 "
                                                  "한 칸 뜬다."}
                add(cid, metric, usd(mm["value"], cid), as_of=mm["period"]["end"], period=mm["period"],
                    basis={"period_basis": "annual", "tag": mm["tag"], "accession": "0001193125-26-231755",
                           "form": "20-F", **fx_basis(cid, mm["value"], filed), **extra},
                    source_id="SRC-SEC-BABA-FACTS",
                    raw=f"{mm['period']['start']}~{mm['period']['end']} {mm['value']:,} CNY",
                    note="F6-REG-28. **당해와 같은 환율 6.8980 으로 환산**했다")
            continue

        for metric, value in (("revenue_ttm", it["revenue_ttm"]),
                              ("operating_income_ttm", it["operating_income_ttm"]),
                              ("net_income_ttm", (m.get("net_income_ttm") or {}).get("value")),
                              ("revenue_ttm_prior", (m.get("revenue_ttm_prior") or {}).get("value"))):
            if value is None:
                print(f"  ! {cid} {metric} 값 없음 — 등록하지 않는다")
                continue
            mm = m.get(metric) or {}
            per = mm.get("period") or period
            b = dict(base)
            if metric in ("revenue_ttm", "operating_income_ttm"):
                b["cross_check_f6_spec_18"] = {"value": (m.get(metric) or {}).get("value"),
                                               "diff": value - ((m.get(metric) or {}).get("value") or value),
                                               "note": "두 조사의 복원 방법이 다르다. meta·nvidia 는 회사 자체 XBRL 의 "
                                                       "분기 합과 YTD 태그가 1백만 어긋나 그만큼 갈린다(0.0004%). "
                                                       "밴드를 가르지 않는다"}
            else:
                b = {"period_basis": mm.get("period_basis", pb), "tag": mm.get("tag"),
                     "taxonomy": mm.get("taxonomy"),
                     "source_procedure": "validation/f6-spec-18/collect_ttm.py — 분기 시계열 복원 후 4분기 합. "
                                         "복원 Q4 는 재작성 세대 검사를 통과한 것만 쓴다"}
            add(cid, metric, value, as_of=per["end"], period=per, basis=b, source_id=src,
                kind="derived" if "reconstructed" in str(it["reconstruction_status"]) else "actual",
                raw=f"{per['start']}~{per['end']} {value:,.0f}",
                note="F6-REG-28. " + ("G1-FILL-27 기준값" if metric in ("revenue_ttm", "operating_income_ttm")
                                      else "F6-SPEC-18 수집기"))

    # ---------------------------------------------------------------- 반영
    obs = load_json_strict(RUN / "observations.json")
    by_id = {o["observation_id"]: o for o in obs["items"]}
    superseded = {
        "spacex-xai.operating_margin_ttm.v15": "spacex-xai.operating_margin_ttm.f6reg28",
        "alibaba.revenue_ttm.obsreg25": None,           # 유지 — TSM 과 달리 교체 대상 아님
    }
    print(f"\n[1] 관측 {len(new_obs)}건 등록")
    print(f"  {'회사':11} {'metric':22} {'값':>20} {'basis':14} {'as_of':11}")
    for item in new_obs:
        pb = (item["basis"] or {}).get("period_basis", "-")
        print(f"  {item['company_id']:11} {item['metric']:22} {item['value']:>20,.0f} {pb:14} {item['as_of']}")
        obs["items"].append(item)
    for old_id, new_id in superseded.items():
        if new_id and old_id in by_id and not str(by_id[old_id].get("note") or "").startswith("[F6-REG-28"):
            by_id[old_id]["note"] = f"[F6-REG-28 대체됨 → {new_id}] " + (by_id[old_id].get("note") or "")
            print(f"  대체  {old_id} → {new_id}")

    # TSM 은 OBS-REG-25 에서 등록한 것이 없다. alibaba 의 revenue_ttm 은 그대로 쓴다(같은 20-F·같은 환율).
    validate_observations(obs, registry, RUN_ID)

    # ---------------------------------------------------------------- AMZN 근거 보강
    amzn = by_id.get("amazon.offbalance_B.obsreg25")
    if amzn is not None:
        ex = amzn["basis"]["excluded"][0]
        ex["reason"] = ("제외 확정(설계진행 2026-09-11). 사유 셋이다. (1) 자산제거의무는 **이미 인식된 부채**라 "
                        "G4 분모에 넣으면 재무제표에 이미 선 것을 다시 센다. (2) build-to-suit 임차료는 각주 1 의 "
                        "Leases not yet commenced 137,214 와 **겹칠 수 있다**. (3) 디지털 콘텐츠 약정은 각주 2 의 "
                        "license digital media content 와 **겹칠 수 있다**. 설계 지침 6.4 가 겹치지 않도록 계약 "
                        "식별자를 남기라고 하는데 이 항목은 성격이 섞여 있고 **공시가 분해를 주지 않는다**.")
        ex["if_included_coverage"] = {"denominator": 285_645_000_000, "coverage": 1.736,
                                      "note": "포함해도 1 이상이라 **G4 판정은 갈리지 않는다**. "
                                              "제외 결정이 점수를 만들지 않는다는 뜻이다"}
        print("\n[2] AMZN offbalance_B 근거란 보강 — 제외 사유 셋과 포함 시 커버리지 1.736")

    # ---------------------------------------------------------------- C-16 downgrade
    run = load_json_strict(RUN / "run.json")
    if not any(d["id"] == "C-16" for d in run["decisions"]):
        run["decisions"].append({
            "id": "C-16", "choice": "downgrade",
            "rationale": "확인된 미공시(not_disclosed_confirmed)로 G4 가 판정 불가면 한 칸 내린다. "
                         "G2 가 이미 g2_private_not_disclosed -2 로 같은 성질을 벌하고 있어 G4 에서 안 벌하면 "
                         "규칙이 어긋난다. hold 는 공시하고 커버리지가 나쁜 쪽만 깎고 아예 안 하는 쪽은 안 깎아 "
                         "불투명을 보상한다. MISS-LABEL-23 이 _g4 를 not_disclosed_confirmed 하나만 C-16 으로 "
                         "보내게 만든 뒤라 근거 없는 감점이 생기지 않는다. 설계진행 2026-09-11 확정(1d39409).",
            "decided_by": "설계진행", "decided_at": "2026-09-11"})
        print("[3] run.decisions 에 C-16 downgrade 추가")

    run["assumptions"] = [a for a in run["assumptions"] if "F6 입력" not in a] + [
        "F6 v1.7 입력 4종은 보존된 companyfacts 재구성(F6-SPEC-18)과 G1-FILL-27 을 대조해 등록했다. 신규 네트워크 수집 없음",
        "TSM·alibaba 는 현지통화 공시라 20-F 가 스스로 선언한 환율로 환산했고 **당해와 전년에 같은 환율**을 썼다. "
        "공시 USD 환산치를 두 해 그대로 쓰면 P3 밴드가 한 칸 뜬다(F6-REG-28 verify_inputs.py [3])",
        "TSM FY2025 는 companyfacts 미등재로 EDGAR 원문을 우회해 읽었다. F6-FX-16 3조건을 충족했고 복귀 조건을 관측에 남겼다",
        "SPCX 매출 쌍만 분기 전년 동기 기준이다. 전년 TTM 이 복원되지 않기 때문이며 손익은 TTM 으로 등록했다",
    ]

    write_json(RUN / "observations.json", obs)
    write_json(RUN / "run.json", run)
    sources = load_json_strict(RUN / "sources.json")
    have = {s["source_id"] for s in sources["items"]}
    added = [s for s in SOURCES if s["source_id"] not in have]
    sources["items"].extend(added)
    write_json(RUN / "sources.json", sources)
    jud = load_json_strict(RUN / "judgments.json")
    validate_judgments(jud, registry, load_rules(run["rule_version"]).payload, RUN_ID)
    print(f"\n[4] 저장 — 관측 {len(obs['items'])}건 · 출처 {len(sources['items'])}건 · 결정 {len(run['decisions'])}건")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
