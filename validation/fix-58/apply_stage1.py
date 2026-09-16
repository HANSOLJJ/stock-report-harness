# FIX-58 1단계: 7차 리뷰 B·C·D 반영 — 순현금 시장성 지분증권 같은 잣대 · oracle 태그 오독 정정 · 기록 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- 12개사 companyfacts `validation/f6-avail-15/_raw/` (지분증권·암호자산 태그 전수)
- ORCL companyfacts (리스 할인차금 관계 검산)

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-16"
M = "FIX-58 1단계"
REVIEW_B = "obsreg 7차 리뷰 B(financial-calc, review-obsreg 4906a27)"
REVIEW_C = "obsreg 7차 리뷰 C(rule-consistency, review-obsreg 4906a27)"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 시장성 지분증권 전수

SWEEP = {
    "checked_at": DATE,
    "review": f"{REVIEW_B} medium — 같은 잣대",
    "how": ("보존 companyfacts 12개사에서 `EquitySecurit|MarketableEquity|TradingSecurities|CryptoAsset` 정규식으로 "
            "**각 회사의 측정 기준일 시점 사실**을 전부 훑었다(가격 조정 누계 태그는 제외). 회사마다 기준일이 다르므로 "
            "회사별 기준일로 본다 — nvidia 2026-07-26 · oracle 2026-05-31 · alibaba 2026-03-31 · tsmc 2025-12-31 · 나머지 6월 말."),
    "rule": "policies.f6.net_cash.securities_scope.include 의 `상장 지분증권` 을 그대로 적용하되, **시장성을 증명한 금액만** 넣는다.",
    "companies": {
        "alphabet": {"verdict": "already_included",
                     "why": ("시장성 지분증권이 대차대조표 줄 `MarketableSecuritiesCurrent` 186,563M 안에 이미 있다 — "
                             "186,563 − AFS 채무증권 99,500(`AvailableForSaleSecuritiesDebtSecurities`) = 87,063 이 지분 쪽이다. "
                             "`EquitySecuritiesFvNi` 는 **기준일 2026-06-30 사실이 없다**(최신 2025-09-30 7,093M) — "
                             "9개월 전 값이라 대차대조 합산에 섞지 않는다."),
                     "delta": 0},
        "meta": {"verdict": "already_included",
                 "why": ("`EquitySecuritiesFvNi` 3,543M 이 이미 `MarketableSecuritiesCurrent` 74,798M **안에 있다.** "
                         "검산: AFS 채무증권(미수이자 제외) 71,255 + 지분 3,543 = **74,798** 로 정확히 맞는다. "
                         "따로 더하면 이중 계상이다."),
                 "delta": 0},
        "nvidia": {"verdict": "added",
                   "why": ("**빠져 있었다.** 이 회사가 쓰는 줄은 `DebtSecuritiesCurrent` 34,143M 이라 채무증권만 담고, "
                           "시장성 지분증권 `EquitySecuritiesFvNi` 42,783M(2026-07-26)은 어느 쪽에도 없었다. "
                           "비시장성 `EquitySecuritiesWithoutReadilyDeterminableFairValueAmount` 47,898M 과 별개 태그라 "
                           "주석이 둘을 갈라 준다 — alibaba 가 상장주식 100,594 를 주석 분할로 넣은 것과 같은 처리다."),
                   "delta": 42783000000.0},
        "oracle": {"verdict": "excluded_mixed",
                   "why": ("`EquitySecuritiesFvNiAndWithoutReadilyDeterminableFairValue` **2,300M 하나뿐이고 시장성과 "
                           "비시장성을 한 수에 담는다.** 비시장성분 605M 을 빼면 1,695M 이 나오지만 그 뺄셈을 쓰지 않는다 — "
                           "같은 파일의 시계열이 어긋난다(2025-05-31 combined 2,100 대 비시장성 417 · 2025-11-30 combined 416). "
                           "**시장성을 증명하지 못한 혼합 줄**이라 넣지 않는다(securities_scope.exclude 의 alibaba "
                           "`Debt securities and loan investments` 10,880 과 같은 사유)."),
                   "delta": 0},
        "alibaba": {"verdict": "already_included",
                    "why": "주석 11 분할로 `Listed equity securities` 100,594 RMB백만을 이미 포함하고 있다.", "delta": 0},
        "tesla": {"verdict": "crypto_excluded",
                  "why": ("시장성 지분증권은 없다. 대신 `CryptoAssetFairValueNoncurrent` **674M(2026-06-30)** 이 포함·제외 "
                          "어느 목록에도 없었다 — spacex-xai 가 FIX-56 1단계에서 받은 것과 같은 판단을 댄다(암호자산은 "
                          "유가증권이 아니고 회사가 비유동으로만 태그했다). **제외.**"),
                  "delta": 0},
        "apple": {"verdict": "none", "why": "기준일 2026-06-27 에 지분증권·암호자산 태그가 없다(net_cash 는 리스 결측으로 미등록).", "delta": 0},
        "amazon": {"verdict": "none", "why": "비시장성 `EquitySecuritiesWithoutReadilyDeterminableFairValueAmount` 122,300M 뿐이고 이미 제외 목록에 있다.", "delta": 0},
        "microsoft": {"verdict": "none", "why": "비시장성 12,400M 뿐이고 이미 제외 목록에 있다.", "delta": 0},
        "palantir": {"verdict": "none", "why": "비시장성 167M 뿐이다(net_cash 는 리스 결측으로 미등록).", "delta": 0},
        "spacex-xai": {"verdict": "none", "why": "비시장성 237M 과 암호자산 1,098M 둘 다 이미 제외 목록에 있다(FIX-56 1단계).", "delta": 0},
        "tsmc": {"verdict": "none", "why": "IFRS 제출사. 비공개거래 지분·전환우선주·SAFE 를 이미 제외 목록에 적었고 시장성 지분 줄은 없다.", "delta": 0},
    },
    "score_effect": ("**밴드가 갈리는 회사가 없다.** nvidia P2 17.8311 → 17.6898(둘 다 `8~20`, -1). 나머지 11개사는 값이 "
                     "바뀌지 않는다. 14개사 총점 불변."),
    "meta_note": (f"[{M}] 지시서는 meta 도 3,543 을 더해 P2 6.7123 → 6.6968 이 된다고 봤다. **더하면 이중 계상이다** — "
                  "71,255 + 3,543 = 74,798 로 이미 쓰는 줄 안에 있다. 산술은 맞지만 사실이 아니라 더하지 않았다."),
}

NVIDIA_EQUITY = {
    "tag": "us-gaap:EquitySecuritiesFvNi",
    "value": 42783000000.0,
    "as_of": "2026-07-26",
    "what": ("시장성 지분증권(공정가치-당기손익). 규칙 `securities_scope.include` 의 `상장 지분증권` 이다. "
             "이 회사의 대차대조표 증권 줄은 `DebtSecuritiesCurrent` 34,143M 로 채무증권만 담아 이 금액이 빠져 있었다."),
    "not_double_counted": ("`DebtSecuritiesCurrent` 34,143 은 정의상 채무증권만이고, 비시장성 지분 47,898 은 별개 태그로 "
                           "제외 목록에 있다. 만기 버킷 `AvailableForSaleSecuritiesDebtMaturitiesWithinOneYearFairValue` "
                           "41,000 은 예전처럼 쓰지 않는다(대차대조표 줄이 아니다)."),
    "asof_difference": ("이 회사의 기준일은 **2026-07-26** 으로 다른 회사(2026-06-30)와 다르다. 회계분기 끝이 달라서이고 "
                        "net_cash 의 다른 성분도 전부 같은 2026-07-26 이라 관측 안에서는 기준이 섞이지 않는다. "
                        "회사 간 비교에서는 한 달 차가 남는다."),
    "added_at": DATE,
    "review": f"{REVIEW_B} medium",
}

TESLA_CRYPTO = {
    "value": 674000000.0,
    "as_of": "2026-06-30",
    "why": ("**암호자산은 유가증권이 아니다.** 정의가 더하는 것은 `현금및현금성자산 + 시장성 유가증권` 이고 암호자산은 "
            "ASU 2023-08 이후 따로 세우는 별개 자산군이다. 회사도 **비유동**으로만 태그했다"
            "(`CryptoAssetFairValueNoncurrent` 674 · 유동 태그 0건). spacex-xai 1,098M 과 같은 판단이다(FIX-56 1단계)."),
    "if_included": "넣으면 순현금이 27,444 → 28,118M 이 되고 P2 는 13.3427 → 13.3161 로 움직인다. **밴드 `8~20` 은 그대로다.**",
    "decided_at": DATE,
    "review": f"{REVIEW_B} medium — 같은 잣대 전수에서 드러났다",
}


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []

    # --- S1 nvidia 포함
    nv = find(items, "observation_id", "nvidia.net_cash.nc37")
    comp = nv["basis"]["components"]
    if not any(c.get("tag") == NVIDIA_EQUITY["tag"] for c in comp["cash_and_marketable_securities_concepts"]):
        comp["cash_and_marketable_securities_concepts"].append(
            {"tag": NVIDIA_EQUITY["tag"], "value": NVIDIA_EQUITY["value"]})
        comp["cash_and_marketable_securities"] = round(comp["cash_and_marketable_securities"] + NVIDIA_EQUITY["value"], 2)
        nv["value"] = round(comp["cash_and_marketable_securities"] - comp["debt_incl_lease"], 2)
        comp["marketable_equity_added"] = json.loads(json.dumps(NVIDIA_EQUITY))
        nv["raw"] = (f"현금 22.4B + 채무증권 34.1B + 시장성 지분증권 42.8B = 99.4B − 차입 38.9B = "
                     f"{nv['value'] / 1e9:.1f}B")
        nv["basis"]["legacy_comparison"] = {
            "legacy_net_cash": 23600000000.0,
            "diff": round(nv["value"] - 23600000000.0, 2),
            "matched": False,
            "note": (f"[{M}] 전에도 맞지 않았다(17,726 대 23,600, 차 -5,874M). 시장성 지분증권을 넣어 60,509M 이 되면서 "
                     "차가 +36,909M 으로 더 커진다. **legacy 와 맞추려고 규칙을 좁히지 않는다** — 규칙이 상장 지분증권을 "
                     "포함으로 적고 주석이 금액을 갈라 준다. legacy 가 이 줄을 어떻게 다뤘는지는 basis 가 없어 알 수 없다."),
        }
        out.append(f"nvidia.net_cash.nc37: 시장성 지분증권 42,783M 포함 — 순현금 17,726M → {nv['value'] / 1e6:,.0f}M")

    # --- S1 tesla 암호자산 제외 판단
    ts = find(items, "observation_id", "tesla.net_cash.nc37")
    tc = ts["basis"]["components"].setdefault("excluded_nonmarketable_present", {})
    if tc.get("us-gaap:CryptoAssetFairValueNoncurrent") != TESLA_CRYPTO:
        tc["us-gaap:CryptoAssetFairValueNoncurrent"] = json.loads(json.dumps(TESLA_CRYPTO))
        out.append("tesla.net_cash.nc37: 암호자산 674M 제외 판단 기록 (spacex-xai 와 같은 잣대)")

    # --- S1 전수 기록을 세 관측에 남긴다(같은 잣대를 어디에 댔는지 한 곳에서 읽히게)
    for oid in ("nvidia.net_cash.nc37", "meta.net_cash.nc37", "oracle.net_cash.nc37"):
        o = find(items, "observation_id", oid)
        if o["basis"].get("marketable_equity_sweep") != SWEEP:
            o["basis"]["marketable_equity_sweep"] = json.loads(json.dumps(SWEEP))
            out.append(f"{oid}: 시장성 지분증권 12개사 전수 기록")

    # --- S2 oracle 부외 대안 태그 오독 정정
    orc = find(items, "observation_id", "oracle.offbalance_B.v15")
    alts = orc["basis"]["disclosed_alternatives"]
    target = next(a for a in alts if a["tag"] == "us-gaap:LesseeOperatingLeaseLiabilityUndiscountedExcessAmount")
    fixed = ("**미개시 약정이 아니다 — 이미 인식된 운용리스부채의 내재이자(할인차금)다.** "
             f"[{M} 정정 · {REVIEW_B} medium] 보존 원자료가 관계를 정확히 준다: 할인 전 지급총액 "
             "`LesseeOperatingLeaseLiabilityPaymentsDue` 41,867 − 대차대조표 리스부채 `OperatingLeaseLiability` 30,190 "
             "= **11,677**. 금융리스도 같은 관계다(11,460 − 7,701 = 3,759). 따라서 **B종(미개시 약정) 후보가 아니다** — "
             "장래 유출이 아니라 이미 인식된 부채의 할인 요소다. 전에 `미개시 리스 약정 … B종 성격에 가장 가깝다` 고 적은 것은 "
             "개념 이름의 `Excess` 를 미개시분으로 잘못 읽은 것이다.")
    if target["what"] != fixed:
        target["what"] = fixed
        out.append("oracle.offbalance_B.v15: 할인차금 태그 오독 정정 (B종 후보 아님)")
    caveat = (f"[{M} 정정] 셋의 합 66,853M 은 **더 이상 B종 후보 합이 아니다.** 41,867 은 개시분 지급총액이라 "
              "대차대조표 30,190 과 겹치고, 11,677 은 그 둘의 차인 할인차금이라 셋을 더하면 같은 부채를 두 번 세는 셈이다. "
              "**남는 B종 후보는 구매 약정 `UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount` 13,309M 계열 "
              "하나다.** 그래도 250,000M 의 출처는 여전히 확인되지 않는다 — 범위를 정하는 것은 규칙 결정이다(C-26).")
    if orc["basis"]["alternatives_caveat"] != caveat:
        orc["basis"]["alternatives_caveat"] = caveat
        out.append("oracle.offbalance_B.v15: 대안 합 66,853M 의 성격을 정정")
    cov = orc["basis"]["coverage_either_way"]
    if "disclosed_sum_66853" in cov:
        cov.pop("disclosed_sum_66853")
        cov["purchase_obligation_13309"] = {"coverage": 47.937486, "g4_step": 0}
        cov["conclusion"] = ("**어느 쪽이든 커버리지가 1 을 넘어 G4 step 0 이다.** legacy 250,000M 기준 2.552, "
                             f"남는 B종 후보 13,309M 기준 47.937. oracle F9 -3 · 총점 2 는 갈리지 않는다. "
                             f"[{M}] 전에 적은 66,853M(9.543)은 할인차금·개시분을 섞어 센 값이라 뺐다.")
        out.append("oracle.offbalance_B.v15: 커버리지 대안을 구매 약정 13,309M 으로 (step 0 불변)")

    # --- S4 spacex-xai 순현금 성분 라벨
    sx = find(items, "observation_id", "spacex-xai.net_cash.nc37")
    sc = sx["basis"]["components"]
    labels = {
        "debt_ex_lease_label": ("**이름과 달리 금융리스를 이미 포함한다.** 39,364 는 "
                                "`LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` 총액 태그이고 "
                                "`LongTermDebt` 38,285 와의 차 1,079 가 금융리스다(basis.corrections 참조). "
                                f"[{M} 라벨 정정 · {REVIEW_B} low] 키 이름이 `_ex_lease` 라 리스를 뺀 값으로 읽혔다."),
        "lease_total_label": ("**운용리스 유동분만이다.** 344 는 10-Q `Operating lease liabilities, current` 이고 "
                              "비유동분 개념이 이 기준일에 없다(basis.completeness). 금융리스는 위 39,364 에 이미 들어 있다."),
        "sum_is_right": "라벨과 무관하게 합계는 맞는다 — 39,364 + 344 = 39,708 이고 100,009 − 39,708 = 60,301 이다. 값 불변.",
    }
    if {k: sc.get(k) for k in labels} != labels:
        sc.update(labels)
        out.append("spacex-xai.net_cash.nc37: 성분 라벨을 사실에 맞게 (값 불변)")
    return out


# ------------------------------------------------------------------ S2·S4 규칙

C26_UPDATE = {
    "recommendation": (
        "이번 실행은 값을 바꾸지 않는다. legacy 를 그대로 두고 `basis` 에 사실과 공시 대안을 남겼다. "
        f"[{M} 정정 · {REVIEW_B} medium] 전에 B종 후보로 든 셋 중 둘이 후보가 아니다 — "
        "`LesseeOperatingLeaseLiabilityPaymentsDue` 41,867 은 **개시분**의 할인 전 지급총액이라 이미 대차대조표 "
        "리스부채 30,190 으로 인식돼 있고, `LesseeOperatingLeaseLiabilityUndiscountedExcessAmount` 11,677 은 그 둘의 "
        "차인 **내재이자(할인차금)** 다(금융리스도 11,460 − 7,701 = 3,759 로 같은 관계). "
        "**남는 B종 후보는 구매 약정 `UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount` 13,309M 계열 하나다.** "
        "다음 라운드에서 (1) legacy 를 유지할지, (2) 구매 약정만 세는 좁은 정의로 바꿀지, (3) B종을 oracle 에 대해 "
        "미확인으로 내릴지 정한다. **오늘은 어느 쪽이든 G4 step 0 이라 점수가 갈리지 않는다**(2.552 대 47.937, 임계 1.0)."),
    "choices": ["keep_legacy_250000", "narrow_to_purchase_obligations", "mark_unverified"],
}

NONOP_CURRENT_ADD = {
    "which_is_used": (
        f"[{M} · {REVIEW_B} low] **현행 동작이다.** 재계산값을 쓴다 — `calc_f6_params._nonop_share` 가 "
        "`pretax_income_ttm` 과 `operating_income_ttm` 을 읽어 `(세전 − 영업이익) / 세전` 으로 만든다. "
        "저장값과 **0.02** 넘게 다르면 경고를 남긴다. 세전이익이 없거나 0 이면 값을 만들지 않고 저장값으로 "
        "되돌아가지도 않는다. 최상위 `which_is_used` 는 2026-09-11 옛 산식(`net_income_ttm` 기준·임계 0.01)의 "
        "기록이라 현행과 다르다."),
    "where_it_does_decide": (
        f"[{M} · {REVIEW_B} low] **현행 산식 기준.** 이 조건이 혼자 강등을 정하는 기업은 둘이다 — "
        "amazon(소계 −1 → −2)과 alphabet(−2 → −3). 두 회사만 `demotion_sole_cause` 가 `nonop_share` 다. "
        "alibaba 는 `period_basis_not_ttm` 이 같이 걸려 이 조건이 빠져도 강등이 그대로이고, "
        "**spacex-xai 는 세전이익이 음수라 산출 자체를 하지 않는다**(`nonop_share_source: incompatible_basis`) — "
        "조건에 걸리지 않으므로 `conditions_hit` 은 `period_basis_not_ttm`·`short_history` 둘이고 "
        "`demotion_sole_cause` 는 **null** 이다. 최상위 `where_it_does_decide` 의 `spacex-xai 도 걸리지만` 은 "
        "옛 산식 시절의 기록이다."),
    "table_label_note": (
        f"[{M} · {REVIEW_B} low] 세 곳에 alibaba 재계산값이 다르게 적혀 있다. 어느 시점 값인지로 갈린다 — "
        "최상위 `table` 의 **0.5159** 는 2026-09-11 옛 산식 `(NI − OI) / NI`, "
        "`remaining_mismatch` 계열의 **0.6247** 은 정정 직후 중간 검산값, "
        "`current.table` 의 **0.6124** 가 이 실행 엔진 값이다(results.json `calc.p4.nonop_share` = 0.6124150). "
        "최상위 `table` 의 열 이름 `재계산값` 은 **옛 산식 결과**라는 뜻이고 현행 값이 아니다."),
}

REVENUE_COALESCE_CONSUMER = (
    f"[{M} · {REVIEW_B} low] **소비자를 붙였다.** 전에는 수집기 `validation/f6-spec-18/collect_ttm.py` 가 같은 네 태그를 "
    "상수로 따로 적어 두고 이 선언을 읽지 않았다 — 선언에 행동을 바꾸는 소비자가 없는 형태였다(C-11 계열). "
    "이제 수집기가 `REVENUE_TAGS` 를 이 `priority` 에서 읽고, 규칙과 기본값이 다르면 멈춘다. "
    "엔진(calc_f6·calc_f9)은 완성된 관측을 읽으므로 이 순서를 직접 쓰지 않는다 — 소비자는 수집 단계다.")

C24_CONSUMER_NOTE = (
    f"[{M} · {REVIEW_C} low] **선택을 코드가 읽는다.** 전에는 `calc_f6_params` 가 규칙의 `optional_parameters` 만 보고 "
    "run.json 의 C-24 선택을 감지하지 못했다. 이제 `decision_choice(run, rules, 'C-24')` 를 읽어 `p3_only_v17` 이면 "
    "선택 파라미터를 만들지 않고, 어느 쪽이든 고른 값을 결과 `calc.c24_choice` 에 남긴다. "
    "**정리 방식** — 실행 단위 결정이 코드 분기를 가지면 `decision_choice` 로 읽고 고른 값을 calc 에 찍는다. "
    "분기가 없으면 그 사실을 `implementation_status` 에 적는다(C-11 `declared_without_consumer` · "
    "C-13 `branch_not_reached_in_parameters_mode` 가 그 형태다).")


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    f6 = rules["policies"]["f6"]

    c26 = find(rules["decisions"], "id", "C-26")
    for key, value in C26_UPDATE.items():
        if c26.get(key) != value:
            c26[key] = value
            out.append(f"decisions C-26: {key} (할인차금 오독 정정)")

    cond = find(f6["p4"]["conditions"], "id", "nonop_share")
    cur = cond["stored_vs_recomputed"]["current"]
    for key, value in NONOP_CURRENT_ADD.items():
        if cur.get(key) != value:
            cur[key] = value
            out.append(f"p4.nonop_share.stored_vs_recomputed.current: {key}")

    rc = f6["revenue_coalesce"]
    if rc.get("consumer") != REVENUE_COALESCE_CONSUMER:
        rc["consumer"] = REVENUE_COALESCE_CONSUMER
        out.append("policies.f6.revenue_coalesce: consumer (수집기가 규칙을 읽는다)")

    c24 = find(rules["decisions"], "id", "C-24")
    if (c24.get("implementation_status") or {}).get("verdict") != "read_by_decision_choice":
        c24["implementation_status"] = {
            "verdict": "read_by_decision_choice",
            "checked_at": DATE,
            "checked_by": f"worker ({M})",
            "evidence": [
                "calc_f6_params.compute_listed 가 decision_choice(run, rules, 'C-24') 를 읽는다",
                "`p3_only_v17` 이면 optional_parameters 를 비우고 calc.c24_choice 에 억제 사실을 적는다",
                "이 실행은 `compute_p2_when_inputs_exist` 라 spacex-xai 가 P2 를 만든다",
            ],
            "note": C24_CONSUMER_NOTE,
        }
        out.append("decisions C-24: implementation_status (선택을 코드가 읽는다 · 정리 방식)")
    return out


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    line = (f"[{M} · {REVIEW_B} medium] 순현금의 **시장성 지분증권**을 12개사 전수로 다시 훑었다. nvidia 42,783M 하나가 "
            "빠져 있어 넣었고(순현금 17,726M → 60,509M · P2 17.8311 → 17.6898 · 밴드 `8~20` 불변), meta 3,543M 과 "
            "alphabet 87,063M 은 이미 쓰는 대차대조표 줄 안에 있어 더하면 이중 계상이라 그대로 뒀다. oracle 2,300M 은 "
            "시장성과 비시장성을 한 수에 담은 혼합 태그라 넣지 않았다. tesla 암호자산 674M 은 spacex-xai 와 같은 판단으로 "
            "제외했다. **14개사 총점 불변.**")
    if line not in run["assumptions"]:
        run["assumptions"].append(line)
        out.append("+ assumptions 시장성 지분증권 전수 결과")
    return out


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)
    policy = load_rules("v1.7").payload["policies"].get("missing_types")

    doc = load(RUN / "observations.json")
    oc = fix_observations(doc)
    validate_observations(doc, registry, RUN_ID, missing_policy=policy)
    dump(RUN / "observations.json", doc)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("규칙", rc), ("관측", oc), ("실행", runc)):
        print(f"{title} 변경 {len(items)}")
        for c in items:
            print("  " + c)
    print("rule_hash", run["rule_hash"][:12])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
