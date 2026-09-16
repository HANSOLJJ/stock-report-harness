# FIX-57 1단계: 6차 리뷰 B 반영 — 점수 경로 선언 정정 · oracle G4 입력 실측 · 경계 사례 기록 · 인용 정정 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- ORCL companyfacts `validation/f6-avail-15/_raw/ORCL.companyfacts.json` (RPO 638,000M · 리스·약정 세 태그)
- META·NVDA companyfacts 같은 디렉터리 (TTM 복원 두 경로 대조)
- v1.5 원문 `E:/…/AI_company_analysis_factor/` (채점규칙 328·543·546·564·579행 · 채점표 549·575·871행)

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
M = "FIX-57 1단계"
REVIEW_B = "obsreg 6차 리뷰 B(financial-calc, review-obsreg b6b8a3a)"
REVIEW_A = "obsreg 6차 리뷰 A(fact-sources, review-obsreg)"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 점수 경로 선언

ON_SCORE_PATH = (
    "**점수 경로 안.** [{m} 정정 · {rb} medium] 전에는 `점수 경로 밖 … P1·P2 가 이 값을 쓰지 않는다` 였다. "
    "FIX-56 1단계(C-24)가 `listed_newly` 트랙의 P2 를 켜면서 **이 값이 P2 의 분자로 들어간다** — "
    "P2 = (시총 1,910,000M − 순현금 60,301M) ÷ TTM 매출 23,044M = 80.27, 밴드 -2. 같은 실행의 results.json 이 "
    "`parameters.P2.inputs.market_cap` 과 `unverified_inputs: {{\"market_cap\": [\"P2\"]}}` 로 그것을 적는다. "
    "SRC-TRACE-47 의 점수 경로 market_cap 은 11건이 아니라 **12건이고 이 관측이 그 12번째**다. "
    "**그리고 12건 전부가 `legacy_unverified` 다** — 상장 12개사의 시총이 하나도 실측되지 않은 채 P1·P2 밑에 있다. "
    "점수를 깎지는 않는다(calc.unverified_inputs 로 드러낸다). 상류는 같은 절(L819)이라 같이 표시한다."
).format(m=M, rb=REVIEW_B)

TRACE_PRIOR = ("validation/src-trace-47 (NTM SRC-TRACE-47) — 점수 경로 legacy 25쌍 중 market_cap 11건의 상류가 "
               "채점표 L794 절 제목으로 StockAnalysis 확정")
TRACE_PRIOR_NEW = (
    "validation/src-trace-47 (NTM SRC-TRACE-47) — 점수 경로 legacy 25쌍 중 market_cap 11건의 상류가 "
    "채점표 L794 절 제목으로 StockAnalysis 확정. "
    f"[{M} 정정 · {REVIEW_B} medium] **점수 경로 market_cap 은 이제 12건이다** — FIX-56 1단계(C-24)가 "
    "`listed_newly` 트랙의 P2 를 켜면서 spacex-xai 시총이 점수 경로에 들어왔다. 상장 12개사의 시총 관측 "
    "전부가 점수 경로이고 전부 `legacy_unverified` 다.")

TRACE_NOTE_OLD = ("걸리는 legacy 관측: market_cap 12건(점수 경로 11 + spacex-xai) · ntm_per 10건(tsmc·alibaba 는 직접 계산) · "
                  "net_cash apple·palantir 2건(공시 혼합).")
TRACE_NOTE_NEW = (f"걸리는 legacy 관측: market_cap 12건(**[{M}] 12건 전부가 점수 경로다** — 전에는 `점수 경로 11 + spacex-xai` 였고 "
                  "spacex-xai 가 C-24 로 들어왔다) · ntm_per 10건(tsmc·alibaba 는 직접 계산) · "
                  "net_cash apple·palantir 2건(공시 혼합).")


# ------------------------------------------------------------------ S2 oracle G4 입력

ORACLE_RPO = {
    "observation_id": "oracle.contracted_revenue.fix57",
    "company_id": "oracle",
    "metric": "contracted_revenue",
    "value": 638000000000.0,
    "unit": "USD",
    "as_of": "2026-05-31",
    "observed_at": DATE,
    "kind": "actual",
    "source_id": "SRC-SEC-FACTS-F6",
    "status": "verified",
    "basis": {
        "measured_as_of": "2026-05-31",
        "tag": "us-gaap:RevenueRemainingPerformanceObligation",
        "accession": "0001193125-26-277521",
        "form": "10-K",
        "preserved": "validation/f6-avail-15/_raw/ORCL.companyfacts.json",
        "matches_legacy": {
            "legacy_id": "oracle.contracted_revenue.v15",
            "legacy_value": 638000000000.0,
            "diff": 0,
            "note": "v1.5 의 `RPO $638B` 와 **정확히 같다.** 승계값이 맞았음을 실측이 확인한 것이고 점수는 바뀌지 않는다.",
        },
        "time_series": {
            "2025-08-31": 455300000000,
            "2025-11-30": 523300000000,
            "2026-02-28": 552600000000,
            "2026-05-31": 638000000000,
        },
        "asof_gap": ("실행 기준일은 2026-09-02 이고 이 사실은 FY2026 결산일 2026-05-31 이다. oracle 은 회계연도가 한 달 어긋나 "
                     "이것이 보존 자료의 최신 공시다."),
        "replaces": "oracle.contracted_revenue.v15 — 같은 값을 공시 사실로 세운다",
        "why_now": f"[{M}] {REVIEW_B} medium — G4 를 가르는 분자가 basis 도 없는 legacy 로 남아 있었다.",
    },
    "raw": "RPO 638,000M (2026-05-31, 10-K)",
    "note": f"{M}. G4 분자 실측 등록. 값·커버리지·step 불변.",
}

ORACLE_OFFB_BASIS = {
    "legacy_only": True,
    "why_kept": (
        f"[{M} · {REVIEW_B} medium] **이 수가 어느 공시 사실과도 맞지 않는다.** 보존 ORCL companyfacts 에서 "
        "2.30e11~2.70e11 구간의 USD 사실은 `Assets`·`LiabilitiesAndStockholdersEquity`(총자산 261,759M) 둘뿐이고 "
        "리스·약정 계열에는 250,000M 이 없다. **값을 지어내지 않고 legacy 를 그대로 둔다.**"),
    "v15_wording": ("v1.5 자신도 이 수를 공시 인용으로 적지 않는다 — 채점표 871행이 부외 약정 칸을 두고 "
                    "`셀사이드 추정이 공개되지 않아서` 라고 적으며 `Meta $628B·Alphabet $707B·Oracle $250B` 를 같은 줄에 든다. "
                    "다만 alphabet 의 $707B 는 공시 태그(`LongTermPurchaseCommitmentAmount` end=2026-06-30)와 정확히 맞는데 "
                    "oracle 의 $250B 는 대응하는 사실이 없다. 채점규칙 564·579행 · 채점표 549·575행이 같은 수를 쓴다."),
    "disclosed_alternatives": [
        {"tag": "us-gaap:LesseeOperatingLeaseLiabilityPaymentsDue", "value": 41867000000.0, "as_of": "2026-05-31",
         "what": "개시된 운용리스의 **할인 전** 지급 총액. 같은 기준일 대차대조표 리스부채(`OperatingLeaseLiability` 30,190M)의 할인 전 판본이라 부외가 아니다."},
        {"tag": "us-gaap:LesseeOperatingLeaseLiabilityUndiscountedExcessAmount", "value": 11677000000.0, "as_of": "2026-05-31",
         "what": "**미개시** 리스 약정. B종(미개시 약정)의 성격에 가장 가깝다."},
        {"tag": "us-gaap:UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount", "value": 13309000000.0, "as_of": "2026-05-31",
         "what": "장부 미기재 무조건 구매 약정."},
    ],
    "alternatives_sum": 66853000000.0,
    "alternatives_caveat": ("셋의 합 66,853M 을 대체값으로 **등록하지 않았다.** 41,867 은 개시분이라 이미 FCF·대차대조표에 있고"
                            "(채점규칙 546행 `개시된 리스는 이미 FCF 에 있고 더하면 이중 계상`), B종 정의와 범위가 다르다. "
                            "범위를 정하는 것은 규칙 결정이지 이 관측의 일이 아니다."),
    "coverage_either_way": {
        "legacy_250000": {"coverage": 2.552, "g4_step": 0},
        "disclosed_sum_66853": {"coverage": 9.543326, "g4_step": 0},
        "threshold": "policies.f9.g4_coverage_keep = 1.0",
        "conclusion": "**어느 쪽이든 커버리지가 1 을 넘어 G4 step 0 이다.** oracle F9 -3 · 총점 2 는 갈리지 않는다.",
    },
    "open_item": "규칙 decisions C-26 — oracle B종 약정의 출처와 범위를 정한다.",
    "recorded_at": DATE,
}

C26 = {
    "id": "C-26",
    "status": "pending",
    "blocking": False,
    "affects": ["F9"],
    "summary": "oracle B종 약정 250,000M 이 어느 공시 사실과도 맞지 않는다 — 출처와 범위를 정해야 한다",
    "recommendation": (
        "이번 실행은 값을 바꾸지 않는다. legacy 를 그대로 두고 `basis` 에 사실과 공시 대안 세 태그를 남겼다. "
        "다음 라운드에서 (1) legacy 를 유지할지, (2) 미개시 약정만 세는 좁은 정의로 바꿀지, (3) B종을 oracle 에 대해 "
        "미확인으로 내릴지 정한다. **오늘은 어느 쪽이든 G4 step 0 이라 점수가 갈리지 않는다**(2.552 대 9.543, 임계 1.0)."),
    "choices": ["keep_legacy_250000", "narrow_to_undisclosed_commitments", "mark_unverified"],
    "implementation_status": {
        "verdict": "not_implemented",
        "checked_at": DATE,
        "checked_by": f"worker ({M})",
        "evidence": [
            "calc_f9._g4 는 offbalance_B 관측값을 그대로 분모로 쓴다 — 출처 성격을 읽지 않는다",
            "oracle.offbalance_B.v15 는 status=legacy_unverified 이고 이번에 basis 만 채웠다(값 불변)",
            "보존 ORCL companyfacts 에 250,000M 에 대응하는 리스·약정 사실이 없다",
        ],
    },
    "pending_recheck": {
        "what": "oracle B종 약정의 출처와 범위.",
        "why": f"{REVIEW_B} medium — G4 분모가 근거 없는 승계값이다.",
        "trigger": "B종 범위 결정이 서거나, 커버리지가 임계 1.0 근처로 내려와 step 을 가를 때",
        "when": "2026-11",
    },
}

C27 = {
    "id": "C-27",
    "status": "pending",
    "blocking": False,
    "affects": ["F6", "F9"],
    "summary": "경계 표시 허용폭 3% 가 적정한지 — 도입 계기였던 alibaba 사례(+3.32%)가 폭 밖이라 표시되지 않는다",
    "recommendation": (
        "이번 실행은 폭을 바꾸지 않는다. **표시 폭은 점수와 무관하지만 기준을 손대면 같은 잣대 문제가 된다** — "
        "F6 P1~P4 와 F9 G3 가 같은 tolerance 를 쓰고 있어 한 자리만 넓힐 수 없다. 거리 자체는 초안이 늘 보여 주므로"
        "(`임계 3년 대비 +3.3%`) 읽는 사람이 놓치지 않는다. 다음 라운드에서 폭을 정한다."),
    "choices": ["keep_0_03", "widen_to_0_05", "per_gate_tolerance"],
    "implementation_status": {
        "verdict": "working_as_designed",
        "checked_at": DATE,
        "checked_by": f"worker ({M})",
        "evidence": [
            "alibaba 런웨이 3.0996년 · 임계 3년 대비 distance_ratio 0.0332134 · tolerance 0.03 → flag false",
            "장치는 선언한 폭대로 동작한다 — 어긋난 것은 calc_f9._runway_boundary 의 도입 주석이었고 그것을 고쳤다",
            "초안·HTML 은 flag 와 무관하게 거리를 표시한다",
        ],
    },
    "pending_recheck": {
        "what": "경계 표시 허용폭(F6·F9 공통 tolerance 0.03)을 유지할지.",
        "why": f"{REVIEW_B} medium — 도입 계기 사례가 폭 밖이라 표시되지 않는다.",
        "trigger": "경계 근처 사례가 더 쌓이거나 폭 밖 사례가 점수를 가를 때",
        "when": "2026-11",
    },
}

C28 = {
    "id": "C-28",
    "status": "pending",
    "blocking": False,
    "affects": ["F6"],
    "summary": "listed_ttm·listed_annual 에서 순손실 기업이 나오면 P2·P3 를 산출해 놓고도 F6 가 pending_data 가 된다",
    "recommendation": (
        "이번 실행은 고치지 않는다. P1 이 `requires_positive`(net_income_ttm > 0)를 못 넘으면 `missing` 에 들어가고, "
        "`missing` 이 하나라도 있으면 compute_listed 가 P2·P3 점수를 버리고 `pending_data` 를 돌려준다. "
        "`listed_newly` 는 C-24 가 넣은 `optional_parameters` 로 이 경로를 피한다. **오늘 상장 적자 기업이 "
        "listed_ttm·listed_annual 에 없어 점수가 갈리지 않는다** — 12개사 전부 P1 이 성립한다. "
        "다음 라운드에서 두 트랙에도 같은 장치를 둘지 정한다. 체크리스트 Q11 이 경고하는 자리다."),
    "choices": ["keep_pending_data", "optional_parameters_for_all_listed_tracks", "explicit_loss_track"],
    "implementation_status": {
        "verdict": "not_implemented",
        "checked_at": DATE,
        "checked_by": f"worker ({M})",
        "evidence": [
            "calc_f6_params.compute_listed: value is None 이고 optional 이 아니면 missing 에 넣고 pending_data 로 끝낸다",
            "listed_ttm·listed_annual 에는 optional_parameters 가 없다",
            "이번 실행 12개 상장사 전부 net_income_ttm > 0 이라 해당 기업이 없다(spacex-xai 는 listed_newly)",
        ],
    },
    "pending_recheck": {
        "what": "순손실 상장사가 listed_ttm·listed_annual 에 들어올 때 P2·P3 를 살릴지.",
        "why": f"{REVIEW_B} low — C-24 가 한 트랙에만 장치를 둬 트랙별로 잣대가 다르다.",
        "trigger": "listed_ttm·listed_annual 트랙에 순손실 기업이 들어올 때",
        "when": "2026-11",
    },
}

TTM_PATHS = {
    "rule": ("TTM 은 두 경로로 복원된다. **어느 쪽인지 관측 basis 가 적는다.** "
             "(1) `collect_ttm` 네 분기 합 — 분기 시계열을 복원해 더한다(revenue_ttm_prior·net_income_ttm·pretax_income_ttm 18건). "
             "(2) 누계 형식 `당기 누계 + 전기 FY − 전기 동일 누계` — revenue_ttm·operating_income_ttm 14건. "
             "(3) 회계연도가 곧 TTM 인 경우 `direct_fy_is_ttm` 4건(microsoft·oracle)."),
    "why_two": ("두 경로는 같은 12개월을 다르게 조립한다. (1)은 분기 사실을, (2)는 누계 사실을 읽는다. "
                "발행사 XBRL 에서 분기 합과 누계 태그가 반올림 때문에 어긋나는 회사가 있어 결과가 갈릴 수 있다."),
    "measured_divergence": {
        "checked_at": DATE,
        "how": "F6-REG-28 관측 18건의 basis.cross_check_f6_spec_18 과, 두 경로를 직접 계산한 두 건을 대조했다.",
        "max_abs_diff_usd": 1000000,
        "max_rel_diff": 0.0000044,
        "cases": [
            {"observation_id": "meta.revenue_ttm.f6reg28", "stored": 228247000000, "other_path": 228248000000},
            {"observation_id": "meta.operating_income_ttm.f6reg28", "stored": 86926000000, "other_path": 86927000000},
            {"observation_id": "nvidia.revenue_ttm.f6reg28", "stored": 302970000000, "other_path": 302969000000},
            {"observation_id": "meta.revenue_ttm_prior.f6reg28", "stored": 178805000000, "other_path": 178804000000,
             "other_path_detail": "89,830(2025 상반기 누계) + 164,501(FY2024) − 75,527(2024 상반기 누계) = 178,804"},
            {"observation_id": "nvidia.net_income_ttm.f6reg28", "stored": 192879000000, "other_path": 192880000000,
             "other_path_detail": "118,010(FY2027 상반기 누계) + 120,067(FY2026) − 45,197(FY2026 상반기 누계) = 192,880"},
        ],
        "all_other_diffs_zero": "나머지 15건은 차 0 이다(alphabet·amazon·apple·microsoft·oracle·palantir·tesla·nvidia 영업이익).",
        "score_effect": "없다. 최대 $1M · 상대 0.0004% 로 어느 밴드도 가르지 않는다.",
    },
    "recorded_at": DATE,
    "review": f"{REVIEW_B} low",
}

FX_LINE_OLD = "환율 선택이 점수를 가르는지도 확인했다. TSM P2 는 32.79 로 23.485, 31.37 로 22.468 이고 **둘 다 -2** 다."
FX_LINE_NEW = (
    f"환율 선택이 점수를 가르는지도 확인했다. [{M} 인용 갱신 · {REVIEW_B} low] 전에 적은 `32.79 로 23.485, 31.37 로 22.468, 둘 다 -2` 는 "
    "**FY2024 매출과 legacy 순현금(77,000M) 기준**이라 이번 실행 입력과 다르다. 현재 입력(FY2025 매출 NT$3,809,054.3M · "
    "검증 순현금 NT$2,171,587.1M · 시총 2,150,000M)으로 다시 계산하면 **31.37 로 17.1365, 32.79 로 17.9380 이고 둘 다 -1** 이다"
    "(매출과 순현금을 같은 환율로 환산한다 — 둘 다 TWD 원값이다). **결론은 그대로다: 환율 선택이 밴드를 가르지 않는다.**")


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    sa = find(rules["sources"]["not_adopted"], "name", "StockAnalysis")
    if sa["prior_investigation"] == TRACE_PRIOR:
        sa["prior_investigation"] = TRACE_PRIOR_NEW
        out.append("sources.not_adopted StockAnalysis: 점수 경로 market_cap 11 → 12건")
    if sa["note"].endswith(TRACE_NOTE_OLD):
        sa["note"] = sa["note"][: -len(TRACE_NOTE_OLD)] + TRACE_NOTE_NEW
        out.append("sources.not_adopted StockAnalysis: note 의 `점수 경로 11 + spacex-xai` 정정")

    fx = rules["policies"]["f6"]["fx"]
    for key in ("why_issuer_declared_first",):
        arr = fx.get(key)
        if isinstance(arr, list) and FX_LINE_OLD in arr:
            arr[arr.index(FX_LINE_OLD)] = FX_LINE_NEW
            out.append(f"policies.f6.fx.{key}: TSM P2 인용 수치를 현재 입력으로")
    tw = rules["policies"]["f6"]["ttm_window"]
    if tw.get("reconstruction_paths") != TTM_PATHS:
        tw["reconstruction_paths"] = json.loads(json.dumps(TTM_PATHS))
        out.append("policies.f6.ttm_window: reconstruction_paths (두 경로와 측정한 차이)")

    decisions = rules["decisions"]
    for spec in (C26, C27, C28):
        cur = [d for d in decisions if d["id"] == spec["id"]]
        if not cur:
            decisions.append(json.loads(json.dumps(spec)))
            out.append(f"+ decisions {spec['id']} (pending)")
        elif cur[0] != spec:
            decisions[decisions.index(cur[0])] = json.loads(json.dumps(spec))

    c24 = find(decisions, "id", "C-24")
    old_impact = ("**spacex-xai F6 -1 → -3, 총점 11 → 9.** P2 = (1,910,000 − 60,301) ÷ 23,044 = 80.27 → 밴드 -2, "
                  "P3 0, 소계 -2, P4 short_history 한 칸 → -3, 트랙 바닥 -3. 다른 13개사는 불변이다.")
    new_impact = ("**spacex-xai F6 -1 → -3, 총점 11 → 9.** P2 = (1,910,000 − 60,301) ÷ 23,044 = 80.27 → 밴드 -2, "
                  "P3 0, 소계 -2, **P4 한 칸**(조건은 `period_basis_not_ttm`·`short_history` 둘이 걸리고 강등은 상한 한 칸) → -3, "
                  f"트랙 바닥 -3. 다른 13개사는 불변이다. [{M} 문구 정정 · {REVIEW_B} low — 전에 `P4 short_history 한 칸` 이라 "
                  "적어 조건이 하나인 것처럼 읽혔다. 칸 수가 같아 점수는 그대로다.]")
    if c24["scope"]["score_impact"] == old_impact:
        c24["scope"]["score_impact"] = new_impact
        out.append("decisions C-24: score_impact 의 P4 조건 문구 정정")
    return out


# ------------------------------------------------------------------ 관측

SPACEX_ASOF = {
    "what": ("**P2 입력의 기준일이 갈린다.** 시총은 2026-09-02(실행 기준일)이고 순현금·TTM 매출은 2026-06-30(10-Q 결산일)이다. "
             "그 사이 두 달의 주가 변동과 현금 흐름이 한 비율 안에 섞여 있다."),
    "sensitivity": {
        "as_reported": {"market_cap": 1910000000000.0, "net_cash": 60301000000.0, "revenue_ttm_full": 23044000000.0,
                        "ev_sales": 80.26813921194237, "band": "20+", "score": -2},
        "band_change_needs": ("밴드가 -2 에서 -1 이 되려면 EV/매출이 20 미만이어야 한다. 시총이 그대로면 **순현금이 "
                              "1,449,120M 을 넘어야** 하고(1,910,000 − 20 × 23,044), 순현금이 그대로면 **시총이 "
                              "521,181M 아래로** 내려와야 한다(60,301 + 20 × 23,044). 둘 다 현재 값과 자릿수가 다르다."),
        "conclusion": "기준일 차이로 밴드가 갈리지 않는다. 사실만 남긴다.",
    },
    "same_form_as": "alibaba.market_cap.v15.basis.p2_asof_mismatch — 같은 형식으로 적는다.",
    "why_not_corrected": "기준일을 맞춘 시총 실측이 보존 자료에 없다. 추정치를 관측으로 세우지 않는다.",
    "recorded_at": DATE,
    "review": f"{REVIEW_B} low",
}

ALIBABA_FX_MIX = {
    "what": ("**분자와 분모가 서로 다른 환율을 거쳐 왔다.** 세전이익은 CNY 원값을 20-F 선언 환율 6.8980 으로 환산했고"
             "(`alibaba.pretax_income_ttm.nonop44`), 영업이익은 20-F 가 실은 USD 환산치를 그대로 썼다"
             "(`alibaba.operating_income_ttm.obsreg25` — RMB50,150M / US$7,270M 이라 **내재 환율 6.8982**)."),
    "cause": "공시 USD 칸이 백만 단위로 반올림돼 있어 역산 환율이 선언 환율과 소수 넷째 자리에서 갈린다(상대차 2.9e-5).",
    "effect": {
        "nonop_share_as_computed": 0.6124150030528569,
        "nonop_share_if_both_at_6_898": 0.6124031007823914,
        "abs_diff": 1.1902270465e-05,
        "rel_diff": 1.943e-05,
        "threshold": 0.30,
        "condition_hit": True,
        "conclusion": ("두 값 다 임계 0.30 의 두 배를 넘어 P4 `nonop_share` 조건이 **걸린다.** 2e-5 의 차이로는 그 판정이 "
                       "뒤집히지 않는다 — 뒤집히려면 0.31 배로 줄어야 한다. 점수 불변."),
    },
    "why_not_corrected": ("공시 USD 를 쓰는 것은 **발행사 자신의 환산을 우선한다**는 규칙(policies.f6.fx)과 맞는다. "
                          "두 입력의 환산 경로가 다르다는 사실만 남긴다."),
    "recorded_at": DATE,
    "review": f"{REVIEW_B} low",
}

ALIBABA_CREDIT_DEPENDENCE = (
    f"[{M} · {REVIEW_B} medium] **alibaba 총점 7 이 이 관측 하나에 달려 있다.** 이 3,330M 을 완충에서 빼면 런웨이가 "
    "3.0996년 → **2.6388년**(19,068M ÷ 7,226M)이 되어 G3 step 0 → **-1**, F9 -3 → **-4**(하한), 총점 7 → **6** 이다. "
    "엔진으로 재계산해 확인했다. 등록 그대로 두는 근거는 관측 basis 의 조건 확인이고, 이 의존을 여기 드러낸다.")


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []

    mc = find(items, "observation_id", "spacex-xai.market_cap.v15")
    if mc["basis"]["on_score_path"] != ON_SCORE_PATH:
        mc["basis"]["on_score_path"] = ON_SCORE_PATH
        out.append("spacex-xai.market_cap.v15: on_score_path 를 결과에 맞게 (점수 경로 안 · 12건)")
    if mc["basis"].get("p2_asof_mismatch") != SPACEX_ASOF:
        mc["basis"]["p2_asof_mismatch"] = json.loads(json.dumps(SPACEX_ASOF))
        out.append("spacex-xai.market_cap.v15: P2 기준일 어긋남과 민감도 (alibaba 와 같은 형식)")

    if not any(x["observation_id"] == ORACLE_RPO["observation_id"] for x in items):
        anchor = items.index(find(items, "observation_id", "oracle.contracted_revenue.v15"))
        items.insert(anchor + 1, json.loads(json.dumps(ORACLE_RPO)))
        out.append("+ oracle.contracted_revenue.fix57 = 638,000M verified (G4 분자 실측, 값 불변)")
    else:
        idx = items.index(find(items, "observation_id", ORACLE_RPO["observation_id"]))
        items[idx] = json.loads(json.dumps(ORACLE_RPO))

    offb = find(items, "observation_id", "oracle.offbalance_B.v15")
    if offb["basis"] != ORACLE_OFFB_BASIS:
        offb["basis"] = json.loads(json.dumps(ORACLE_OFFB_BASIS))
        out.append("oracle.offbalance_B.v15: 250,000M 이 공시와 맞지 않는 사실 · 대안 세 태그 · 두 커버리지 (값 불변)")

    ali_credit = find(items, "observation_id", "alibaba.undrawn_credit.fix53")
    if ali_credit["basis"].get("score_dependence") != ALIBABA_CREDIT_DEPENDENCE:
        ali_credit["basis"]["score_dependence"] = ALIBABA_CREDIT_DEPENDENCE
        out.append("alibaba.undrawn_credit.fix53: 총점 7 이 이 관측에 달려 있다는 사실")

    pre = find(items, "observation_id", "alibaba.pretax_income_ttm.nonop44")
    if pre["basis"].get("fx_path_mismatch") != ALIBABA_FX_MIX:
        pre["basis"]["fx_path_mismatch"] = json.loads(json.dumps(ALIBABA_FX_MIX))
        out.append("alibaba.pretax_income_ttm.nonop44: nonop_share 의 환율 혼합 사실과 크기")

    tsm = find(items, "observation_id", "tsmc.revenue_ttm.f6reg28")
    bs = tsm["basis"]["band_sensitivity"]
    want_used = {"rate": 31.37, "value": 17.1365, "band": -1}
    want_alt = {"rate": 32.79, "label": "FY2024 20-F 선언 환율", "value": 17.938, "band": -1}
    if bs["used"] != want_used or bs["alternative"] != want_alt:
        bs["used"] = dict(want_used)
        bs["alternative"] = dict(want_alt)
        bs["net_cash_basis"] = (
            f"[{M} 정정 · {REVIEW_B} low] 전 값(17.072 · 17.845)은 **legacy 순현금 77,000M** 기준이라 엔진이 쓰는 "
            "검증 순현금과 달랐다. 엔진 P2 는 `tsmc.net_cash.nc37` 69,224.96M(NT$2,171,587.1M ÷ 31.37)을 쓴다. "
            "대체 환율 칸도 **매출과 순현금을 같은 32.79 로** 환산해 다시 계산했다 — 둘 다 TWD 원값이라 한쪽만 바꾸면 "
            "섞인 기준이 된다(32.79 기준 매출 116,165.12M · 순현금 66,227.11M).")
        out.append("tsmc.revenue_ttm.f6reg28: band_sensitivity 를 검증 순현금 기준으로 (17.1365 · 17.9380, 둘 다 -1)")
    return out


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    a = run["assumptions"]
    line = (f"[{M} · {REVIEW_B} medium] **상장 12개사의 시총 관측 12건이 전부 점수 경로이고 전부 `legacy_unverified` 다.** "
            "FIX-56 1단계(C-24)가 spacex-xai 의 P2 를 켜면서 11건에서 12건이 됐다. P1·P2 가 그 위에 서고 상류는 "
            "StockAnalysis(원천 장부 `not_adopted · legacy_upstream`)다. 점수를 깎지 않고 calc.unverified_inputs 와 "
            "경고로 드러낸다 — 수집 공백을 기업 위험으로 바꾸지 않는다.")
    if line not in a:
        a.append(line)
        out.append("+ assumptions 시총 12건 전부 점수 경로·미검증")
    return out


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    doc = load(RUN / "observations.json")
    oc = fix_observations(doc)
    validate_observations(doc, registry, RUN_ID)
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
