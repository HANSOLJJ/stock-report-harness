# FIX-56 2단계: 5차 리뷰 A 분담·C 반영 — 하네스 표기 같은 잣대 · 실행 가정문 정정 · 검색 범위 · 미결 소비자 기록 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- v1.5 원문 `E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor/` (채점표 264·375·732행 · 채점규칙 22·384행)
- openai 보도자료 `ffaf318:validation/priv-arr-17b/_raw/openai_accelerating_official_2026-03-31.html`
- anthropic 보도자료 `ffaf318:validation/priv-arr-17b/_raw/anthropic_series_h_official_2026-05-28.html`
- amazon 10-Q `3cf9799:validation/offb-24/_raw/amzn-20260630.htm`
- tsmc 20-F `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm`
- PLTR·GOOGL companyfacts `validation/f6-avail-15/_raw/`

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-16"
M = "FIX-56 2단계"
REVIEW_A = "obsreg 5차 리뷰 A 분담(review-obsreg · validation/fact-sources-split/ntm.md)"
REVIEW_C = "obsreg 5차 리뷰 C(review-obsreg · rule-consistency)"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


def replace_once(items: list[str], old: str, new: str, label: str, out: list[str]) -> None:
    """이미 고쳐졌으면 넘어간다. 옛 문장이 없고 새 문장도 없으면 원문이 바뀐 것이므로 멈춘다."""
    if any(new == x for x in items):
        return
    hits = [i for i, x in enumerate(items) if x == old]
    assert len(hits) == 1, f"{label}: 옛 문장 {len(hits)}건"
    items[hits[0]] = new
    out.append(label)


# ------------------------------------------------------------------ S1 하네스 표기 (점수 불변)

HARNESS_HEAD = f"⚠️ [{M}] **하네스 미표기**"
HARNESS_TAIL = (
    "어느 하네스로 잰 값인지 원문이 적지 않는다(채점규칙 22행 `비교는 같은 하네스끼리만`). "
    f"이번 실행이 anthropic.F2 에 댄 것과 같은 표기이며, **모델 간 비교를 하는 줄에 같은 잣대로** 단다({REVIEW_A} medium — "
    "자사 판단에만 대면 같은 잣대가 아니다). 하네스 사실을 새로 판정하지 않았고 점수는 그대로다."
)


def harness_mark(detail: str) -> str:
    return f"{HARNESS_HEAD} — {detail} {HARNESS_TAIL}"


META_OLD_FRAG = "🆕 Tau3-Bench Banking 52%로 전 모델 1위"
META_NEW_FRAG = (META_OLD_FRAG + " " + harness_mark(
    "`전 모델 1위` 는 여러 모델을 한 줄에 세우는 비교인데 채점표 264행 원문에도 하네스 표기가 없다."))

ALIBABA_OLD = "단 표준 주도력이 비어 있고 HLE 43.6%로 프론티어 미달"
ALIBABA_NEW = (ALIBABA_OLD + " " + harness_mark(
    "`프론티어 미달` 은 프론티어 모델과의 비교인데 채점표 375행 원문에 하네스 표기가 없다. "
    "같은 지표를 모아 놓은 채점표 943행도 모델별 수치만 적는다."))

OPENAI_OLD = "FrontierMath Tier 4 v2 97.6%(Fable 5.1 87.8%)"
OPENAI_NEW = (OPENAI_OLD + " " + harness_mark(
    "**한 줄에서 두 모델을 직접 비교**하는데 채점표 732행 원문에 하네스 표기가 없다. "
    "같은 근거란의 ARC-AGI-3 줄은 `표준 하네스 62.7%` 로 적어 두 줄의 기준이 다르다."))

ANTHROPIC_OLD_TAIL = "점수 5 는 승계 그대로이고 재검토는 TEN-RA4-01(2026-11)."
ANTHROPIC_NEW_TAIL = (ANTHROPIC_OLD_TAIL +
                      f" [{M}] 같은 표기를 meta.F2·alibaba.F2·openai.F2 의 모델 간 비교 줄에도 댔다 — "
                      "이 표기는 anthropic 한 곳에만 대는 잣대가 아니다.")


def fix_judgments(doc: dict) -> list[str]:
    out: list[str] = []
    items = doc["items"]

    # meta.F2 — 긴 한 줄 안의 조각을 바꾼다
    meta = find(items, "judgment_id", "meta.F2")
    if not any(HARNESS_HEAD in e for e in meta["evidence"]):
        idx = [i for i, e in enumerate(meta["evidence"]) if META_OLD_FRAG in e]
        assert len(idx) == 1, "meta.F2 Tau3-Bench 줄"
        meta["evidence"][idx[0]] = meta["evidence"][idx[0]].replace(META_OLD_FRAG, META_NEW_FRAG)
        out.append("meta.F2: Tau3-Bench 비교 줄에 하네스 미표기")

    ali = find(items, "judgment_id", "alibaba.F2")
    replace_once(ali["evidence"], ALIBABA_OLD, ALIBABA_NEW, "alibaba.F2: HLE 비교 줄에 하네스 미표기", out)

    oai = find(items, "judgment_id", "openai.F2")
    replace_once(oai["evidence"], OPENAI_OLD, OPENAI_NEW, "openai.F2: FrontierMath 비교 줄에 하네스 미표기", out)

    ant = find(items, "judgment_id", "anthropic.F2")
    idx = [i for i, e in enumerate(ant["evidence"]) if ANTHROPIC_OLD_TAIL in e and ANTHROPIC_NEW_TAIL not in e]
    if idx:
        ant["evidence"][idx[0]] = ant["evidence"][idx[0]].replace(ANTHROPIC_OLD_TAIL, ANTHROPIC_NEW_TAIL)
        out.append("anthropic.F2: 같은 표기를 셋에 더 댔다는 사실")

    # 하네스 표기가 채점규칙 22행·채점표 원문 행을 인용하므로 그 문서를 source_ids 에 등재한다
    # (FIX-52 인용 규약 — 근거란이 문서를 인용하면 판단이 그 문서를 출처로 들어야 한다).
    for jid, needed in (("meta.F2", ("SRC-v15-rule", "SRC-v15-md")),
                        ("alibaba.F2", ("SRC-v15-rule", "SRC-v15-md")),
                        ("openai.F2", ("SRC-v15-rule", "SRC-v15-md"))):
        j = find(items, "judgment_id", jid)
        for sid in needed:
            if sid not in j["source_ids"]:
                j["source_ids"].append(sid)
                out.append(f"{jid}: source_ids += {sid} (인용한 문서 등재)")

    # S5 G2 근거 라벨을 관측 id 와 구별되게
    for cid in ("anthropic", "openai"):
        j = find(items, "judgment_id", f"{cid}.F9")
        cur = j["inputs"].get("fcf_not_disclosed_reason")
        want = f"reason:{cid}.fcf_not_disclosed"
        if cur == f"{cid}.fcf_not_disclosed":
            j["inputs"]["fcf_not_disclosed_reason"] = want
            out.append(f"{cid}.F9: fcf_not_disclosed_reason 을 `reason:` 라벨로 (관측 id 와 구별)")
    return out


# ------------------------------------------------------------------ S2 실행 가정문

CREDIT_OLD = ("확정 미인출 여신(FIX-54 S2)은 **상장 12개사만 관측으로 남겼다.** 비상장 anthropic·openai 는 관측을 만들지 않았다 — "
              "인용할 보존 원문·source_id 가 없어 `미확인` 조차 어느 자료를 봤는지 적을 수 없기 때문이다. 두 회사는 C-20 경로라 "
              "G3 가 생략돼 점수에 닿지 않는다. 근거는 validation/fix-54/undrawn-credit-census.md 에 있다 "
              "[FIX-55 1단계 · 4차 리뷰 B low — 처리 통일]")
CREDIT_NEW = (
    "확정 미인출 여신(FIX-54 S2)은 **상장 12개사만 관측으로 남겼다.** 비상장 anthropic·openai 는 관측을 만들지 않았다. "
    f"[{M} 사유 정정 · {REVIEW_A} high] 전에 적은 `인용할 보존 원문·source_id 가 없어서` 는 **더 이상 성립하지 않는다** — "
    "FIX-55 2단계가 두 회사의 보도자료를 `SRC-ANTHROPIC-SERIESH-2026`·`SRC-OPENAI-FUNDING-2026` 으로 등재했다. "
    "**실제 사유는 자료의 성질이다.** anthropic 보도자료에는 여신 관련 표현이 광역 검색으로도 0건이고, openai 보도자료에는 "
    "`expanded our existing revolving credit facility to approximately $4.7 billion … The facility remains undrawn at close` 가 "
    "있으나 (1) 금액이 `approximately` 이고 (2) `at close` 는 대차대조 기준일이 아니라 측정 시점을 세울 수 없으며 (3) 약정 조건이 "
    "적혀 있지 않고 (4) 감사받지 않은 회사 자체 발표다. 설계 지침 6.4 의 `조건이 확인된 확정 미인출 여신` 요건을 채우지 못한다 — "
    "상장 12개사는 전부 기준일이 붙은 공시 사실이라 같은 잣대가 아니다. 두 회사는 C-20 경로라 G3 가 생략돼 어차피 점수에 닿지 않는다. "
    "근거는 validation/fix-54/undrawn-credit-census.md · validation/fix-55/credit-tag-sweep.md 에 있다 "
    "[FIX-55 1단계 · 4차 리뷰 B low — 처리 통일]")

PRIV_OLD = ("비상장 2사의 F6·F9 입력은 v1.5 원본(AI기업_채점규칙_v1.5.md sha256 57beb84a… · AI기업_채점표_v1.5.md)에서 직접 읽었다. "
            "선행 조사가 준 값도 원문 문장으로 다시 대조했다(validation/priv-impl-31/verify_private.py)")
PRIV_NEW = (
    "비상장 2사의 F6·F9 입력은 v1.5 원본(AI기업_채점규칙_v1.5.md sha256 57beb84a… · AI기업_채점표_v1.5.md)에서 직접 읽었다. "
    "선행 조사가 준 값도 원문 문장으로 다시 대조했다(validation/priv-impl-31/verify_private.py). "
    f"[{M} 보완 · {REVIEW_A} low] **한 건은 v1.5 원본이 아니라 회사 자체 발표를 가리킨다** — `anthropic.arr_prior.priv31`(ARR $47B)의 "
    "source_id 를 FIX-55 2단계가 `SRC-ANTHROPIC-SERIESH-2026`(Anthropic 2026-05-28 Series H 보도자료)으로 옮겼다. "
    "**이해당사자의 감사받지 않은 1차 발표가 F6 P3 입력에 들어가 있다**는 뜻이고, 그 출처의 `conflict_of_interest` 에 성격을 적었다. "
    "status 는 legacy_unverified 그대로이고 값도 바뀌지 않았다")

OPENAI_CREDIT_ASSUMPTION = (
    f"[{M} · {REVIEW_A} medium] openai 보도자료에 회전여신 문장이 있다 — "
    "`We have also expanded our existing revolving credit facility to approximately $4.7 billion … "
    "The facility is supported by a global syndicate including JPMorgan Chase, Citi, Goldman Sachs, … "
    "The facility remains undrawn at close.` **관측으로 등록하지 않았다.** 금액이 `approximately` 이고 `at close` 가 "
    "대차대조 기준일이 아니라 측정 시점을 세울 수 없으며, 약정 조건이 없고 감사받지 않은 회사 자체 발표다. "
    "openai 는 C-20 경로라 F9 가 G2 에서 G4 로 건너뛰고 **G3(런웨이)를 계산하지 않으므로** 이 값이 들어갈 자리 자체가 없다. "
    "부재 주장 5건의 checked_scope 검색 범위를 여신 어휘까지 넓혀 이 문장을 적었다")


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    a = run["assumptions"]
    replace_once(a, CREDIT_OLD, CREDIT_NEW, "assumptions: 비상장 여신 미등록 사유를 사실에 맞게 정정", out)
    replace_once(a, PRIV_OLD, PRIV_NEW, "assumptions: 비상장 입력 중 회사 자체 발표가 섞인 사실", out)
    if OPENAI_CREDIT_ASSUMPTION not in a:
        a.append(OPENAI_CREDIT_ASSUMPTION)
        out.append("+ assumptions openai 회전여신 $4.7B — 등록하지 않은 사유와 점수 경로")
    return out


# ------------------------------------------------------------------ S3·S4·S5 관측

OPENAI_SCOPE = (
    "ffaf318:validation/priv-arr-17b/_raw/openai_accelerating_official_2026-03-31.html — "
    "`cash` 2건은 `more revenue and more cashflow` 한 문장이 본문과 페이지 데이터에 두 번 실린 것이고 수치가 아니다. "
    "`free cash` · `debt` · `EBITDA` · `operating income` · `operating margin` · `profit` 0건. "
    "**매출 수치는 여럿 있다**(`$1B in revenue` · `$1B per quarter` · `$2B in revenue per month` · "
    "`enterprise … more than 40% of our revenue`). "
    f"[{M} 범위 확대 · {REVIEW_A} medium] 여신 어휘를 넣지 않아 놓친 문장이 있었다 — 태그를 걷은 본문 기준 "
    "`credit` 2 · `revolving` 2 · `facility` 6 · `undrawn` 2 · `syndicate` 2 건이고 "
    "**`expanded our existing revolving credit facility to approximately $4.7 billion` · "
    "`The facility remains undrawn at close`** 한 문단이다(본문과 페이지 데이터에 중복 게재). "
    "`unused` · `borrow` · `loan` 0건. **그래도 여신 관측을 만들지 않았다** — 금액이 `approximately` 이고 `at close` 가 "
    "대차대조 기준일이 아니며 약정 조건이 없고 감사받지 않은 회사 자체 발표다(run.json assumptions). "
    "현금·FCF·부채·TTM 영업손익 수치가 없다는 판정은 그대로 이 자료로 선다. "
    "[FIX-55 2단계 범위 서술 정정, obsreg 4차 리뷰 A 분담(NTM Claude 독립 세션, 기준 ab5a053 · review 0752b05) low]")

ANTHROPIC_SCOPE = (
    "ffaf318:validation/priv-arr-17b/_raw/anthropic_series_h_official_2026-05-28.html — "
    "본문에서 `cash` · `free cash` · `debt` · `EBITDA` · `operating income` · `operating margin` 0건. "
    f"[{M} 정정 · {REVIEW_C} low] `profit` 은 **원시 파일 7건 · 태그를 걷은 본문 6건**이고 전부 `Nonprofit(s)` 계열이다"
    "(상단 메뉴·바닥글 링크·검색 추천어 · 차이 1건은 `<a href>` 속성 안). 재무 용어로서의 `profit` 은 0건이다 — "
    "앞서 적은 `1건` 은 화면에 보이는 메뉴 항목만 센 것이라 파일 출현 횟수와 달랐다. "
    f"[{M} 범위 확대 · {REVIEW_A} medium 와 같은 잣대] openai 쪽에서 놓쳤던 여신 어휘로 다시 훑었다 — "
    "`credit` · `facility` · `revolving` · `undrawn` · `unused` · `borrow` · `loan` · `syndicate` **전부 0건**이다. "
    "수치는 조달액·밸류·run-rate 뿐이다")


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []

    # --- S3 검색 범위
    for cid, scope in (("openai", OPENAI_SCOPE), ("anthropic", ANTHROPIC_SCOPE)):
        changed = 0
        for metric in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
            o = find(items, "observation_id", f"{cid}.{metric}.priv31")
            if o["basis"]["checked_scope"]["preserved_release"] != scope:
                o["basis"]["checked_scope"]["preserved_release"] = scope
                changed += 1
        if changed:
            out.append(f"{cid} priv31 {changed}건: 검색 범위를 여신 어휘까지 넓히고 결과를 적음")

    # --- S4 palantir 리스 라벨 단정 철회
    pal = find(items, "observation_id", "palantir.lease_liabilities.nc37")
    old_why = ("`OperatingLeaseLiabilityNoncurrent` 211,400천은 있으나 `...Current` 도 상위 합계 `OperatingLeaseLiability` 도 없다. "
               "유동 리스부채는 대차대조표 면에 별도 줄이 없고 `AccruedLiabilitiesCurrent` 504,070천에 묻혀 있다. "
               "**발행사가 따로 공시하지 않는다.**")
    new_why = ("`OperatingLeaseLiabilityNoncurrent` 211,400천은 있으나 `...Current` 도 상위 합계 `OperatingLeaseLiability` 도 없다. "
               "유동 리스부채는 대차대조표 면에 별도 줄이 없고 `AccruedLiabilitiesCurrent` 504,070천에 묻혀 있다. "
               "**데이터셋의 표준 태그 결측이지 발행사 미공시 확인이 아니다** — basis.label_correction.")
    if pal["basis"]["why"] == old_why:
        pal["basis"]["why"] = new_why
        pal["basis"]["why_superseded"] = (
            f"~~{old_why}~~ (superseded [{M}] — 같은 관측의 label_correction 이 `not_disclosed_confirmed` 를 "
            f"`unverified` 로 내리며 그 단정을 이미 철회했는데 이 줄만 단정으로 남아 있었다. 짝인 apple 쪽은 "
            f"FIX-54 2단계에서 같은 문면으로 고쳐졌다. {REVIEW_A} medium)")
        out.append("palantir.lease_liabilities.nc37: 단정 철회 — apple 과 같은 문면으로")

    # --- S5 amazon 재무 약정 문장 좁히기
    amzn = find(items, "observation_id", "amazon.undrawn_credit.fix54")
    old_note = ("세 시설 모두 기준일 미인출이다. 364일 여신(2026-10 만기)과 지연인출 약정(2026-09-30 까지 단일 인출)은 "
                "기준일·정보 컷오프(2026-09-02) 현재 유효한 약정이지만 만기가 가깝다. 재무 약정(covenant) 문장은 원문에 없다.")
    new_note = ("세 시설 모두 기준일 미인출이다. 364일 여신(2026-10 만기)과 지연인출 약정(2026-09-30 까지 단일 인출)은 "
                "기준일·정보 컷오프(2026-09-02) 현재 유효한 약정이지만 만기가 가깝다. "
                f"**여신 시설의** 재무 약정(covenant) 문장은 원문에 없다 — [{M} 정정 · {REVIEW_A} low] 보존 10-Q 에 covenant 는 "
                "한 번 나오고 그것은 사채 이야기다(`We are not subject to any financial covenants under the Notes.`, Note 5 Debt). "
                "`원문에 없다` 를 시설 범위로 좁힌다.")
    if amzn["basis"]["conditions_note"] == old_note:
        amzn["basis"]["conditions_note"] = new_note
        out.append("amazon.undrawn_credit.fix54: `재무 약정 문장 없음` 을 여신 시설 범위로 좁힘")

    # --- S5 tsmc 검색어 확대
    tsmc = find(items, "observation_id", "tsmc.undrawn_credit.fix54")
    old_t = ("보존 20-F(f14a235)는 있으나 `credit facilit`·`unused credit`·`lines of credit`·`unutilized` 전문 검색 0건이다. "
             "FCF 양수라 G3 에 닿지 않는다.")
    new_t = (
        "보존 20-F(f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm) 전문 검색이다. "
        f"[{M} 검색어 확대 · {REVIEW_A} low] 처음 쓴 네 어휘(`credit facilit`·`unused credit`·`lines of credit`·`unutilized`)는 "
        "전부 0건인데 **그 목록이 좁아 실제로 있는 문장을 놓쳤다.** 넓혀 다시 훑은 결과 — "
        "`credit facilit` 0 · `unused credit` 0 · `lines of credit` 0 · `line of credit` 0 · `unutilized` 0 · `undrawn` 0 · "
        "`revolving` 0 · `borrowing capacity` 0 · `unused` 2 · `letters of credit` 2 · `available under` 1 건이다. "
        "`unused` 2건 중 하나는 `unused tax losses`(이연법인세)이고, 나머지 한 자리가 약정 주석 g 항 "
        "`Amounts available under unused letters of credit as of December 31, 2024 and 2025 were NT$ 489.9 million and "
        "NT$ 438.7 million, respectively.` 다. 바로 아래 h 항은 이행보증(`performance guarantees`)이다. "
        "**결론은 그대로다 — 확정 미인출 여신은 확인되지 않았다.** 신용장과 이행보증은 지급 보증 수단이라 인출 가능한 약정 한도가 "
        "아니기 때문이다(basis.next_collection_guide). FCF 양수라 G3 에 닿지도 않는다.")
    if tsmc["basis"]["why"] == old_t:
        tsmc["basis"]["why"] = new_t
        out.append("tsmc.undrawn_credit.fix54: 검색어를 넓히고 신용장·이행보증 구분을 남김 (결론 불변)")

    # --- S5 palantir 부외 정정 근거 넓히기
    pof = find(items, "observation_id", "palantir.offbalance_note.v15")
    lc = pof["basis"]["label_correction"]
    old_w = lc["why"]
    marker = f"[{M} 근거 확대]"
    if marker not in old_w:
        lc["why"] = (old_w.replace(
            "보존 PLTR companyfacts 에는 기준일 2026-06-30 의 부외 약정 태그 사실이 없고 최신값은 2024-12-31 의 0 이다.",
            "보존 PLTR companyfacts 에는 기준일 2026-06-30 의 부외 약정 태그 사실이 없다. "
            f"{marker} `최신값은 2024-12-31 의 0` 은 **한 태그(`UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount`, "
            "시점형 2건) 기준**이었다. 같은 파일에 `LongTermPurchaseCommitmentAmount` 가 있고 값은 "
            "US$1,950,000,000(10-K `0001321655-25-000022`)인데 **기간형 사실(start 2023-09-01 · end 2023-09-30)이라 "
            "기준일 잔고가 아니다.** 같은 태그가 alphabet 에서는 end=2026-06-30 US$707,000,000,000 으로 "
            "`alphabet.offbalance_note.v15` 의 `총 약정 $707B` 와 정확히 맞는다 — 태그가 부외 약정을 담는다는 뜻이다. "
            "**결론은 그대로 `미확인` 이다**: 두 태그 어느 쪽도 palantir 의 2026-06-30 잔고를 주지 않는다."))
        out.append("palantir.offbalance_note.v15: 정정 근거를 두 태그로 넓힘 (결론 `미확인` 불변)")
    return out


# ------------------------------------------------------------------ 규칙

THIRD_PARTY = {
    "TEN-RC-02": ("committed", None),
    "TEN-RC-03": ("committed", None),
    "TEN-RC3-01": ("committed", None),
    "TEN-RA4-01": ("committed", None),
    "TEN-RC4-01": ("partial", ["anthropic.F3"]),
    "TEN-RC-05": ("recommended", None),
    "TEN-RC3-03": ("recommended", None),
    "TEN-RA3-01": ("recommended", None),
}

# C-04 는 **이미 기록돼 있다** — implementation_status.include_v15_reads_but_does_not_use 가 두 갈래의 산식이 같다고 적는다.
# 5차 리뷰 C 가 다시 든 것은 그 사실이 **코드에는 없어서** 코드만 읽으면 안 보이기 때문이다. 기존 기록을 덮지 않고
# 코드에 주석을 넣은 사실과 낡은 행 번호만 고친다.
C04_PATCH = {
    "include_v15_reads_but_does_not_use": (
        "코드가 선택지를 **읽기는 읽는다** — calc_f9 267행이 decision_choice(run, rules, 'C-04') 로 가져오고 269·271행이 "
        "경고 문자열만 붙이며 **272행 계산이 양쪽 분기에서 같다.** 안 읽는 것(죽은 선언)과 읽고 안 쓰는 것은 다른 결함이고 "
        "**후자가 더 나쁘다** — 실행 기록에 `C-04: include_v15` 가 남아 선택이 반영된 것처럼 보인다(설계진행 지적). "
        f"[{M} · {REVIEW_C} low] 행 번호를 현재 파일에 맞췄고(전에는 237·239·242행) **같은 사실을 코드 주석으로도 남겼다** "
        "— 규칙 파일을 열지 않고 코드만 읽는 사람에게는 보이지 않았다."),
}
C13_IMPL = {
    "verdict": "branch_not_reached_in_parameters_mode",
    "checked_at": DATE,
    "checked_by": f"worker ({M})",
    "evidence": [
        "calc_f6.compute_f6 는 policies.f6.mode 가 `parameters` 면 calc_f6_params 로 갈라진다",
        "C-13 을 읽는 분기(calc_f6 proxy_methods)는 bands 모드 경로 안에 있어 이번 실행에서 호출되지 않는다",
        "이번 실행의 F6 는 14개사 전부 parameters 모드다(results calc.mode)",
    ],
    "why_recorded": f"[{M} · {REVIEW_C} low] 실행 단위 결정 목록에 C-13 이 있어 소비된 것처럼 보인다. 이번 모드에서는 닿지 않는다.",
}
C11_IMPL = {
    "verdict": "declared_without_consumer",
    "checked_at": DATE,
    "checked_by": f"worker ({M})",
    "evidence": [
        "C-11 을 읽는 코드가 없다 — decision_choice(run, rules, 'C-11') 호출부가 저장소 전체에 0건이다",
        "calc_qual 의 F7 은 별표 I 두 축(조달 의존 고객 비중 · 내 돈이 돌아오는가)만 읽는다",
        "차단 대상인 `영업외 비중 → ⑦ 이월` 경로는 구현된 적이 없다",
    ],
    "why_recorded": (f"[{M} · {REVIEW_C} low] **선언만 있고 소비자가 없는 형태**다. 규칙과 문서의 차단이며 코드 분기가 아니다. "
                     "나중에 F7 이 입력을 늘릴 때 이 선언을 읽는 자리를 만들어야 한다 — 그러지 않으면 차단이 글로만 남는다."),
}
F3_RANGE_NOTE = (
    f"[{M} · {REVIEW_C} low] `range` 하한 1 은 **사다리가 낼 수 있는 값**이고 이번 실행의 실측 최저는 2 다. "
    "1 은 통과점 0(세 기준 전부 fail)일 때 나오는데 14개사 중 그런 회사가 없었을 뿐이다 — 규칙과 결과의 불일치가 아니다. "
    "`range` 는 관측된 구간이 아니라 규칙이 허용하는 구간이라는 뜻을 여기 적는다."
)


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    for t in rules["open_tensions"]:
        spec = THIRD_PARTY.get(t["id"])
        if spec is None:
            continue
        kind, scope = spec
        if t.get("third_party_recheck") != kind:
            t["third_party_recheck"] = kind
            out.append(f"{t['id']}: third_party_recheck = {kind}")
        if scope is None:
            t.pop("third_party_scope", None)
        elif t.get("third_party_scope") != scope:
            t["third_party_scope"] = scope
            out.append(f"{t['id']}: third_party_scope = {scope}")

    decisions = {d["id"]: d for d in rules["decisions"]}
    for did, impl in (("C-13", C13_IMPL), ("C-11", C11_IMPL)):
        d = decisions.get(did)
        assert d is not None, did
        if d.get("implementation_status") != impl:
            d["implementation_status"] = json.loads(json.dumps(impl))
            out.append(f"decisions {did}: implementation_status ({impl['verdict']})")
    c04 = decisions["C-04"]["implementation_status"]
    for key, value in C04_PATCH.items():
        if c04.get(key) != value:
            c04[key] = value
            out.append(f"decisions C-04: {key} 행 번호·코드 주석 반영 (기존 기록 유지)")

    f3 = rules["factors"]["F3"]
    if f3.get("range_note") != F3_RANGE_NOTE:
        f3["range_note"] = F3_RANGE_NOTE
        out.append("factors.F3: range_note (하한 1 과 실측 최저 2 의 관계)")
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

    jud = load(RUN / "judgments.json")
    jc = fix_judgments(jud)
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    dump(RUN / "judgments.json", jud)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("규칙", rc), ("관측", oc), ("판단", jc), ("실행", runc)):
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
