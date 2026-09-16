# FIX-55 2단계: 4차 리뷰 A 분담(NTM) 반영 — tesla 여신 5,000M 등록 · 비상장 보도자료 출처 등재 · anthropic.F2 긴장 · 결측 서술 정정
"""보존 원자료만 읽는다. 신규 조회 없음.

- validation/f6-avail-15/_raw/*.companyfacts.json — 여신 태그 광역 정규식 주사(Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility)
- ffaf318:validation/priv-arr-17b/_raw/ 두 보도자료 — 출처 등재·검색 범위 서술
- 3cf9799:validation/offb-24/_raw/ · f14a235:validation/tsm-edgar-29/_raw/ — 원문 문면
- 채점규칙 v1.5 22·384·731행 — 하네스·이해상충

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"
DATE = "2026-09-16"
M = "FIX-55 2단계"
REVIEW_A = "obsreg 4차 리뷰 A 분담(NTM Claude 독립 세션, 기준 ab5a053 · review 0752b05)"
CREDIT_TAG_RE = re.compile(r"Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility", re.I)
ANTH_SRC = "SRC-ANTHROPIC-SERIESH-2026"
OAI_SRC = "SRC-OPENAI-FUNDING-2026"
PRIV_METRICS = ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ S1 여신 광역 주사

def sweep_credit_tags() -> dict[str, list[dict]]:
    """보존 companyfacts 14개(=파일 12개)를 **고정 후보가 아니라 정규식**으로 훑는다.

    AGENTS.md 117행 — 고정 후보 목록으로 태그를 찾으면 체계가 다른 발행사가 0 으로 나온다.
    FIX-54 S2 가 `LineOfCreditFacility…` 계열만 봐서 tesla 의 `DebtInstrumentUnusedBorrowingCapacityAmount` 를 놓쳤다.
    """
    out: dict[str, list[dict]] = {}
    for path in sorted(RAW.glob("*.companyfacts.json")):
        ticker = path.name.split(".")[0]
        doc = json.loads(path.read_text(encoding="utf-8"))
        rows = []
        for taxonomy, tags in doc["facts"].items():
            for tag, node in tags.items():
                if not CREDIT_TAG_RE.search(tag):
                    continue
                for unit, facts in node["units"].items():
                    instants = [r for r in facts if not r.get("start")]
                    if not instants:
                        continue
                    latest = max(instants, key=lambda r: r["end"])
                    rows.append({"taxonomy": taxonomy, "tag": tag, "unit": unit, "end": latest["end"],
                                 "val": latest["val"], "form": latest.get("form"), "accn": latest.get("accn")})
        out[ticker] = sorted(rows, key=lambda r: r["end"], reverse=True)
    return out


TESLA = {
    "observation_id": "tesla.undrawn_credit.fix55",
    "company_id": "tesla",
    "metric": "undrawn_credit",
    "value": 5000000000.0,
    "unit": "USD",
    "as_of": "2026-06-30",
    "observed_at": DATE,
    "kind": "actual",
    "source_id": "SRC-SEC-FACTS-F6",
    "status": "verified",
    "basis": {
        "measured_as_of": "2026-06-30",
        "taxonomy": "us-gaap",
        "tag": "DebtInstrumentUnusedBorrowingCapacityAmount",
        "tag_definition": "Amount of unused borrowing capacity under the long-term financing arrangement that is available to the entity as of the balance sheet date.",
        "why_no_arithmetic": ("**태그 자체가 미인출액이다.** 한도 − 인출액을 우리가 계산하지 않았다 — 발행사가 `unused … available to the entity` 를 "
                              "그대로 태깅한다. 설계 지침 6.4 의 `조건이 확인된 확정 미인출 여신` 에 그대로 대응한다."),
        "form": "10-Q",
        "accession": "0001628280-26-049270",
        "filed": "2026-07-23",
        "series": {"2025-09-30": 7387000000, "2025-12-31": 6429000000, "2026-03-31": 5000000000, "2026-06-30": 5000000000,
                   "note": "직전 분기(2026-03-31)도 같은 5,000M 이다. 값이 한 분기만 튀는 것이 아니다."},
        "why_missed_before": ("FIX-54 S2 가 `LineOfCreditFacilityMaximumBorrowingCapacity` 계열 고정 후보만 훑어 체계가 다른 이 태그를 놓쳤다"
                              f"({REVIEW_A} high). AGENTS.md 117행 `고정 후보 목록으로 태그를 찾으면 체계가 다른 발행사가 0 으로 나온다` 가 그대로 재현됐다."),
        "engine_effect": ("**점수에 닿지 않는다** — tesla 는 TTM FCF +5,762M 로 G2 에서 끝나고 G3(런웨이)가 계산되지 않는다. "
                          "F9 -1(G1 통과 → G2 흑자·추세 악화)은 그대로다."),
        "supersedes": "tesla.undrawn_credit.fix54(미확인). 그 관측은 지우지 않고 대체 표시만 남긴다.",
        "sweep": "광역 정규식 주사 결과는 validation/fix-55/credit-tag-sweep.md",
    },
    "raw": "us-gaap:DebtInstrumentUnusedBorrowingCapacityAmount 2026-06-30 = 5,000,000,000 USD",
    "note": f"{M} · {REVIEW_A} high. 확정 미인출 여신 실측 등록 — 태그 정의가 미인출액이라 별도 계산이 없다.",
}


# ------------------------------------------------------------------ S2 출처·긴장

SOURCES = [
    {
        "source_id": ANTH_SRC,
        "title": "Anthropic 보도자료 `Anthropic raises $65B in Series H funding at $965B post-money valuation` (2026-05-28)",
        "publisher": "Anthropic (회사 뉴스룸)",
        "url": None,
        "accessed_at": "2026-09-10",
        "sha256": "cf15b1bb07faef65e7838aea5d292dc6075b842ec4c0b40922cbd24e42f65e82",
        "conflict_of_interest": ("**회사 자체 발표다** — 이해당사자 1차 발표치이고 감사받지 않는다. 채점규칙 382행 `벤더 발표 벤치마크는 1차 근거가 아니다` "
                                 "와 같은 성격이라 수치는 방증·부재 확인 범위로만 쓴다. 더해 이 실행의 작성자(Claude)가 Anthropic 모델이다(채점규칙 384행 · 긴장 #4·#11)."),
        "note": ("원문 위치 ffaf318:validation/priv-arr-17b/_raw/anthropic_series_h_official_2026-05-28.html (주소 https://www.anthropic.com/news/series-h, "
                 "PRIV-ARR-17B 에서 1회 수집·보존, robots.txt `Allow: /` 도 같은 커밋에 보존). **새로 받지 않는다** — host 는 생산 원천 정책에 등재되지 않았다"
                 f"(rules.sources.unlisted). 쓰임: anthropic.arr_prior.priv31 의 run-rate $47B 와 비상장 부재 주장 5건의 검색 범위. [{M}]"),
    },
    {
        "source_id": OAI_SRC,
        "title": "OpenAI 보도자료 `OpenAI raises $122 billion to accelerate the next phase of AI` (2026-03-31)",
        "publisher": "OpenAI (회사 뉴스룸)",
        "url": None,
        "accessed_at": "2026-09-10",
        "sha256": "060fcb9d8ca3c2a6f1be13bea033d9d02c7f21f4c14ef74bed8d27680a36d174",
        "conflict_of_interest": ("**회사 자체 발표다** — 이해당사자 1차 발표치이고 감사받지 않는다. 채점규칙 382행과 같은 성격이라 수치는 방증·부재 확인 범위로만 쓴다. "
                                 "이 실행의 작성자(Claude)는 Anthropic 모델이고 OpenAI 는 그 경쟁사다 — 하향·상향 어느 쪽으로도 이해상충이 있다."),
        "note": ("원문 위치 ffaf318:validation/priv-arr-17b/_raw/openai_accelerating_official_2026-03-31.html (주소 "
                 "https://openai.com/index/accelerating-the-next-phase-ai/, PRIV-ARR-17B 에서 1회 수집·보존, robots.txt 도 같은 커밋에 보존). "
                 f"**새로 받지 않는다**(rules.sources.unlisted). 쓰임: 비상장 부재 주장 5건의 검색 범위. [{M}]"),
    },
]

UNLISTED = [
    {
        "host": "www.anthropic.com",
        "reason_type": "terms",
        "reason": ("PRIV-ARR-17B(2026-09-10)에서 보도자료 1건과 robots.txt 를 보존 목적으로 한 번 받았고 그 보존본만 쓴다. **생산 원천으로 등재 검토를 한 적이 없다** — "
                   "약관의 개인 내부 사용 허용 여부를 확인하지 않았다. robots.txt 는 `Allow: /` 이지만 robots 와 라이선스는 다르다(policy_note)."),
        "decided_at": DATE,
        "note": f"[{M}] 회사 자체 발표라 이해당사자 자료다. 새 수집 없이 보존본만 참조한다 — sources.json {ANTH_SRC}.",
    },
    {
        "host": "openai.com",
        "reason_type": "terms",
        "reason": ("PRIV-ARR-17B(2026-09-10)에서 보도자료 1건과 robots.txt 를 보존 목적으로 한 번 받았고 그 보존본만 쓴다. 생산 원천 등재 검토는 하지 않았다 — "
                   "약관 확인 전이다."),
        "decided_at": DATE,
        "note": f"[{M}] 같은 사유. sources.json {OAI_SRC}.",
    },
]

TEN_RA4_01 = {
    "id": "TEN-RA4-01",
    "status": "open",
    "recheck_at": "2026-11",
    "review_finding": f"RA4-01(medium) · {REVIEW_A} · 체크리스트 Q23 관련",
    "judgment_ids": ["anthropic.F2"],
    "decision_id": "C-03",
    "subject": "anthropic F2 5점의 성능 근거에 하네스 표기가 없고 저장소에 받치는 자료가 없다",
    "tension": ("anthropic.F2(승계 5점) 근거 `Opus 5 ARC-AGI-3 30.2%(직전 최고 약 8%)` 에 어느 하네스로 잰 값인지 적혀 있지 않고 저장소에 그 측정을 받치는 자료가 없다. "
                "같은 실행의 openai.F2 는 `ARC-AGI-3 SOTA(표준 하네스 62.7%)` 로 하네스를 명시하고 벤더 어댑터 99.9% 를 배제한 이유까지 적는다. 채점규칙 22행 "
                "`비교는 같은 하네스끼리만(체크리스트 23)` · 731행 체크리스트 23 · 384행 이해상충 고지(`이 규칙은 OpenAI의 ARC-AGI 하네스 문제를 다루다 나왔고 … "
                "결과적으로 Anthropic ②5를 지켰다 … 다음 분기에 제3자 관점으로 재검토한다`)와 어긋난다."),
    "direction": "하향 가능(5 → 4 검토). 같은 하네스의 독립 측정이 확인되면 5 유지. **이 등록은 점수를 바꾸지 않는다.**",
    "rechecker": "**비 Claude 세션이 재판정한다** — Anthropic 점수이고 채점규칙 384행이 제3자 재검토를 약속한 바로 그 자리다.",
    "trigger": "독립 기관이 같은 하네스로 잰 ARC-AGI-3(또는 대체 에이전트 실무 축) 측정이 확보될 때. C-03 pending_recheck 의 발동 조건과 같다.",
    "why_carried_exception": ("승계 판단의 기존 논리이고 이번 실행이 F2 의 잣대를 바꾸지 않았다(C-03 확정 뒤에도 세대 격차 판정은 하지 않았다). 재검토 시점과 함께 "
                             "등록했으므로 AGENTS.md 리뷰 범위 — 승계 판단 예외에 해당한다."),
    "score_impact_now": "없다.",
    "source_lines": ["채점규칙 22행", "채점규칙 384행", "채점규칙 731행"],
    "related_tensions": ["TEN-RA-02", "TEN-RA3-01"],
    "note": (f"[{M}] 재검토 약속 자체는 decisions C-03.pending_recheck 에 있었으나 리뷰 계약이 예외 요건으로 지목하는 자리는 open_tensions 다. "
             "같은 고지의 다른 축인 anthropic.F5.impl48 은 TEN-RC-03 에 이미 있다. 근거란에 하네스 미표기 사실을 적었다."),
}


def fix_judgments(jud: dict) -> list[str]:
    by = {j["judgment_id"]: j for j in jud["items"]}
    changed = []
    j = by["anthropic.F2"]
    if "SRC-v15-rule" not in j["source_ids"]:
        # 근거란이 채점규칙 22·384·731행을 인용하게 됐다 — 인용한 문서를 source_ids 에도 올린다(FIX-52 인용 계약).
        j["source_ids"] = j["source_ids"] + ["SRC-v15-rule"]
        changed.append("anthropic.F2 source_ids + SRC-v15-rule")
    ev = by["anthropic.F2"]["evidence"]
    old = "Opus 5 ARC-AGI-3 30.2%(직전 최고 약 8%)"
    new = (f"Opus 5 ARC-AGI-3 30.2%(직전 최고 약 8%) ⚠️ [{M}] **하네스 미표기** — 어느 하네스로 잰 값인지 원문이 적지 않고 저장소에 이 측정을 받치는 자료가 없다"
           "(채점규칙 22행 `비교는 같은 하네스끼리만`). 같은 실행의 openai.F2 는 `표준 하네스 62.7%` 로 표기한다. 점수 5 는 승계 그대로이고 재검토는 TEN-RA4-01(2026-11).")
    if old in ev:
        ev[ev.index(old)] = new
        changed.append("anthropic.F2 evidence (하네스 미표기 표시)")
    return changed


# ------------------------------------------------------------------ S3 관측·서술

def fix_observations(doc: dict, sweep: dict[str, list[dict]]) -> list[str]:
    by = {o["observation_id"]: o for o in doc["items"]}
    changed = []

    # S1 tesla
    if "tesla.undrawn_credit.fix55" not in by:
        doc["items"].append(json.loads(json.dumps(TESLA)))
        by = {o["observation_id"]: o for o in doc["items"]}
        changed.append("tesla.undrawn_credit.fix55 등록(verified 5,000M)")
    elif by["tesla.undrawn_credit.fix55"] != TESLA:
        doc["items"][[o["observation_id"] for o in doc["items"]].index("tesla.undrawn_credit.fix55")] = json.loads(json.dumps(TESLA))
        by = {o["observation_id"]: o for o in doc["items"]}
        changed.append("tesla.undrawn_credit.fix55 갱신")
    old = by["tesla.undrawn_credit.fix54"]
    sup = {"by": "tesla.undrawn_credit.fix55", "at": DATE,
           "why": (f"보존 companyfacts 에 기준일 값이 있었다 — us-gaap:DebtInstrumentUnusedBorrowingCapacityAmount 2026-06-30 5,000M. "
                   f"`미확인` 은 고정 후보 목록만 훑은 결과였다({REVIEW_A} high).")}
    if old["basis"].get("superseded_by") != sup:
        old["basis"]["superseded_by"] = sup
        old["note"] = old["note"] + f" | [{M} 대체됨 → tesla.undrawn_credit.fix55] 광역 태그 주사에서 실측값을 찾았다."
        changed.append("tesla.undrawn_credit.fix54 대체 표시")

    # 광역 주사 결과를 census 주장과 함께 관측에 남긴다(oracle 은 여전히 없다).
    oracle = by["oracle.undrawn_credit.fix54"]
    orcl_rows = sweep.get("ORCL", [])
    sweep_note = (f"[{M}] 광역 정규식 주사(`Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility`)를 보존 companyfacts 12개 파일에 다시 돌렸다. "
                  f"oracle 은 해당 태그 사실이 **{len(orcl_rows)}건**이다. 기준일 이후 값이 있는 회사는 tesla 하나뿐이었다 — oracle 은 그대로 미등록이고 점수도 그대로다.")
    if oracle["basis"].get("broad_tag_sweep") != sweep_note:
        oracle["basis"]["broad_tag_sweep"] = sweep_note
        changed.append("oracle.undrawn_credit.fix54 광역 주사 기록")

    # S3 palantir 부외 표기
    o = by["palantir.offbalance_note.v15"]
    if o["value"] == "없음":
        o["value"] = "미확인 — v1.5 원표기 `없음`"
        o["basis"] = {
            "label_correction": {
                "was": "없음", "is": "미확인 — v1.5 원표기 `없음`", "corrected_at": DATE, "review": f"{REVIEW_A} medium",
                "why": ("다른 회사는 같은 자료 상태를 `미확인` 으로 적는데 palantir 만 확정 부재로 적혀 있었다. 보존 PLTR companyfacts 에는 기준일 2026-06-30 의 "
                        "부외 약정 태그 사실이 없고 최신값은 2024-12-31 의 0 이다. HANDOVER 69행 `\"미등재·없음\"은 검색 없이 쓰면 틀린다` · AGENTS.md 117행 "
                        "`0 이 나오면 부재인지 탐색 실패인지 가른다`."),
                "score_path": "offbalance_note 는 표시용 텍스트다. palantir 의 coverage_comparable 은 unknown 이라 G4 도 판정하지 않는다 — 점수에 닿지 않는다.",
            },
        }
        changed.append("palantir.offbalance_note.v15 값 → 미확인")

    # S3 tsmc 여신 기간 불일치 · 신용장 기준
    o = by["tsmc.undrawn_credit.fix54"]
    mismatch = (f"[{M} · {REVIEW_A} low] **기간이 어긋난다.** as_of 는 2026-06-30 인데 부재를 확인한 원문은 FY2025(2025-12-31 기준) 20-F 다. "
                "그 사이 분기 보고가 없어(20-F 제출사) 더 최신 원문이 없다. 라벨은 `unverified` 라 과장은 없다.")
    guide = ("다음 수집 지침 — 같은 20-F 에 `unused letters of credit … NT$ 438.7 million` 이 있다. **신용장은 약정 여신이 아니다** — 지급 보증 수단이고 "
             "인출 가능한 한도가 아니다. spacex-xai 에서는 신용장 645M 을 미인출액에서 **빼는** 방향으로 썼다(보수적 하한). 수집할 때 (1) 회전여신·기간대출 "
             "약정 한도와 인출액, (2) 신용장·보증 잔액을 따로 적고 (2)를 (1)의 미인출액에 더하지 않는다.")
    if o["basis"].get("period_mismatch") != mismatch or o["basis"].get("next_collection_guide") != guide:
        o["basis"]["period_mismatch"] = mismatch
        o["basis"]["next_collection_guide"] = guide
        changed.append("tsmc.undrawn_credit.fix54 기간 불일치·신용장 기준")

    # S3 amazon RPO 표현
    o = by["amazon.contracted_revenue.obsreg25"]
    raw = "those commitments not yet recognized were approximately $496 billion (2026-06-30)"
    if o["raw"] != raw:
        o["basis"]["raw_correction"] = {
            "was": o["raw"], "is": raw, "corrected_at": DATE, "review": f"{REVIEW_A} low",
            "why": ("`RPO` 는 우리가 붙인 이름이다. 보존 10-Q 문면은 `those commitments not yet recognized were approximately $ 496 billion as of June 30, 2026` "
                    "이고 `remaining performance obligation` 은 전문에서 0건이다. 값·기준일은 그대로다."),
        }
        o["raw"] = raw
        changed.append("amazon.contracted_revenue.obsreg25 raw 원문 표현")

    # S3 openai 검색 범위 서술
    for metric in PRIV_METRICS:
        o = by[f"openai.{metric}.priv31"]
        scope = o["basis"]["checked_scope"]
        fixed = ("ffaf318:validation/priv-arr-17b/_raw/openai_accelerating_official_2026-03-31.html — `cash` 1건은 `more revenue and more cashflow` 서술로 "
                 "수치가 아니다. `free cash` · `debt` · `EBITDA` · `operating income` · `operating margin` 0건. **매출 수치는 여럿 있다**"
                 "(`$1B in revenue` · `$1B per quarter` · `$2B in revenue per month` · `enterprise … more than 40% of our revenue`) — 현금·FCF·부채·"
                 f"TTM 영업손익 수치가 없다는 판정만 이 자료로 선다. [{M} 범위 서술 정정, {REVIEW_A} low]")
        if scope.get("preserved_release") != fixed:
            scope["preserved_release"] = fixed
            changed.append(f"openai.{metric}.priv31 checked_scope 범위 서술")

    # S2 보도자료 출처를 관측과 잇는다
    for cid, sid in (("anthropic", ANTH_SRC), ("openai", OAI_SRC)):
        for metric in PRIV_METRICS:
            o = by[f"{cid}.{metric}.priv31"]
            if o["basis"]["checked_scope"].get("preserved_release_source_id") != sid:
                o["basis"]["checked_scope"]["preserved_release_source_id"] = sid
                changed.append(f"{cid}.{metric}.priv31 checked_scope.preserved_release_source_id")
    o = by["anthropic.arr_prior.priv31"]
    if o["source_id"] != ANTH_SRC:
        o["basis"]["source_correction"] = {
            "was": o["source_id"], "is": ANTH_SRC, "corrected_at": DATE, "review": f"{REVIEW_A} medium",
            "why": ("값 $47B 를 받치는 1차 문면이 회사 보도자료다 — `Since our Series G in February, adoption has continued to grow across global enterprise "
                    "customers, and our run-rate revenue crossed $47 billion earlier this month.` v1.5 서술은 이 발표를 옮긴 것이다. 출처가 등재되지 않아 "
                    "이해당사자 발표라는 성격이 References 에 드러나지 않았다."),
            "quote": "our run-rate revenue crossed $47 billion earlier this month",
            "still_legacy": "status 는 legacy_unverified 그대로다 — 값 자체를 이번 실행이 재측정한 것이 아니다.",
        }
        o["source_id"] = ANTH_SRC
        changed.append("anthropic.arr_prior.priv31 source_id → " + ANTH_SRC)

    # S3 spacex 신용장·제한현금 이중 계산 아님
    o = by["spacex-xai.undrawn_credit.fix54"]
    dbl = (f"[{M} · {REVIEW_A} 확인 못 한 것] **이중 계산이 아니다.** 신용장 645M 은 `collateralized by restricted cash` 이지만 런웨이 분자의 현금 관측 "
           "spacex-xai.cash.cashfcf35 93,522M 은 `us-gaap:CashAndCashEquivalentsAtCarryingValue` **순수 현금**이고 제한현금 830M(RestrictedCashCurrent 210 + "
           "Noncurrent 620)은 거기서 빠져 있다(그 관측 basis 의 제외 목록). 따라서 신용장 전액 차감은 같은 돈을 두 번 빼는 것이 아니라 미인출액 쪽만 보수적으로 "
           "좁힌 하한이다. 다음 리뷰가 같은 질문을 반복하지 않게 여기 적는다.")
    if o["basis"].get("no_double_count_with_restricted_cash") != dbl:
        o["basis"]["no_double_count_with_restricted_cash"] = dbl
        changed.append("spacex-xai.undrawn_credit.fix54 이중 계산 아님 기록")
    return changed


def fix_sources(sources: dict) -> list[str]:
    by = {s["source_id"]: s for s in sources["items"]}
    changed = []
    for src in SOURCES:
        if by.get(src["source_id"]) != src:
            sources["items"] = [s for s in sources["items"] if s["source_id"] != src["source_id"]] + [json.loads(json.dumps(src))]
            changed.append(f"sources {src['source_id']}")
    return changed


def fix_rules(rules: dict, v15_counts: dict[str, int]) -> list[str]:
    changed = []
    note = rules["sources"]["note"]
    tail = (f" | [{M}] anthropic.arr_prior.priv31 의 source_id 를 회사 보도자료({ANTH_SRC})로 옮겨 SRC-v15-* 관측이 "
            f"{sum(v15_counts.values())}건이 됐다(html {v15_counts.get('SRC-v15-html', 0)} + rule {v15_counts.get('SRC-v15-rule', 0)} + "
            f"md {v15_counts.get('SRC-v15-md', 0)}). 새 출처 둘은 url 이 null 이라 정책 검사 밖인 것은 같고, host 는 sources.unlisted 에 적었다.")
    if tail not in note:
        rules["sources"]["note"] = note + tail
        changed.append("sources.note 관측 수 갱신")
    ids = {t["id"]: t for t in rules["open_tensions"]}
    if ids.get("TEN-RA4-01") != TEN_RA4_01:
        rules["open_tensions"] = [t for t in rules["open_tensions"] if t["id"] != "TEN-RA4-01"] + [TEN_RA4_01]
        changed.append("open_tensions TEN-RA4-01")
    unlisted = {u["host"]: u for u in rules["sources"].get("unlisted", [])}
    for entry in UNLISTED:
        if unlisted.get(entry["host"]) != entry:
            rules["sources"]["unlisted"] = [u for u in rules["sources"].get("unlisted", []) if u["host"] != entry["host"]] + [entry]
            changed.append(f"sources.unlisted {entry['host']}")
    return changed


def fix_run(run: dict) -> list[str]:
    changed = []
    old = ("apple·palantir 는 리스부채 태깅 공백으로 net_cash 를 등록하지 못했다. 값을 만들지 않고 lease_liabilities 결측 관측에 "
           "missing_type=not_disclosed_confirmed 를 붙여 **왜 막혔는지**를 남겼고 F6 calc.unverified_blocked_by 로 산출물에 드러난다")
    new = ("apple·palantir 는 리스부채 태깅 공백으로 net_cash 를 등록하지 못했다. 값을 만들지 않고 lease_liabilities 결측 관측에 "
           "**missing_type=unverified**(FIX-54 2단계 정정 — 확인한 것은 보존 companyfacts 표준 태그뿐이고 10-Q 전문은 검색하지 않았다)를 붙여 "
           "**왜 막혔는지**를 남겼고 F6 calc.unverified_blocked_by 로 산출물에 드러난다")
    for i, line in enumerate(run["assumptions"]):
        if old in line:
            run["assumptions"][i] = line.replace(old, new)
            changed.append(f"run.json assumptions[{i}] 리스 라벨")
    return changed


SWEEP_MD = """# FIX-55 2단계 — 확정 미인출 여신 태그 광역 주사

`validation/f6-avail-15/_raw/*.companyfacts.json` 12개 파일(상장 12개사)을 정규식
`Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility` 로 훑어 **시점형(instant) 사실이 있는 태그**를 전부 모았다.
FIX-54 S2 는 `LineOfCreditFacilityMaximumBorrowingCapacity` 계열 고정 후보만 봤고, 그래서 tesla 의
`DebtInstrumentUnusedBorrowingCapacityAmount` 를 놓쳤다(4차 리뷰 A 분담 high · AGENTS.md 117행).

| 티커 | 태그 수 | 가장 최신 사실 | 값 | 제출본 |
|---|---|---|---|---|
{rows}

**기준일(2026 회계 분기) 이후 값이 있는 회사는 TSLA 하나다.** 나머지는 최신 사실이 2013~2021년이고, AAPL·BABA·ORCL·SPCX·TSM 은
해당 태그 자체가 없다. **oracle 에는 없다** — G3 가 점수를 내는 유일한 미등록 기업이라 이 주사로도 값이 생기지 않았고 점수는 그대로다.

비상장 2사(anthropic·openai)는 companyfacts 가 없어 이 주사의 대상이 아니다. 관측을 만들지 않는 이유는 run.json 가정문에 있다.
다만 openai 보도자료(2026-03-31)에 `We have also expanded our existing revolving credit facility to approximately $4.7 billion` 이 있다 —
**시설 규모이고 미인출액이 아니며** 회사 자체 발표라 등록하지 않았다. G3 는 C-20 경로로 생략되어 점수에도 닿지 않는다.
"""


def write_sweep_md(sweep: dict[str, list[dict]]) -> list[str]:
    rows = []
    for ticker, hits in sorted(sweep.items()):
        if hits:
            top = hits[0]
            rows.append(f"| {ticker} | {len(hits)} | `{top['tag']}` {top['end']} | {top['val']:,.0f} {top['unit']} | {top['form']} {top['accn']} |")
        else:
            rows.append(f"| {ticker} | 0 | — | — | — |")
    text = SWEEP_MD.format(rows="\n".join(rows))
    path = ROOT / "validation" / "fix-55" / "credit-tag-sweep.md"
    if not path.is_file() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8", newline="\n")
        return ["validation/fix-55/credit-tag-sweep.md"]
    return []


def fix_census() -> list[str]:
    path = ROOT / "validation" / "fix-54" / "undrawn-credit-census.md"
    text = path.read_text(encoding="utf-8")
    old_head = "보존 원문만 봤다(3cf9799 offb-24 · f14a235 tsm-edgar-29 · validation/f6-avail-15 companyfacts). 새로 받지 않았다."
    new_head = (old_head + "\n**[정정 2026-09-16 FIX-55 2단계]** 이 표의 `전수` 는 **고정 후보 태그 목록** 기준이었다. 광역 정규식 주사"
                "(`Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility`)를 다시 돌려 **tesla 5,000M**(us-gaap:DebtInstrumentUnusedBorrowingCapacityAmount, "
                "2026-06-30, 10-Q 0001628280-26-049270)을 찾았다 — 아래 tesla 행을 고쳤다. 주사 결과는 validation/fix-55/credit-tag-sweep.md 에 있고, "
                "기준일 이후 값이 있는 회사는 tesla 하나였다(oracle 은 없다).")
    old_row = ("| tesla | 본문 없음 | 여신 한도 태그 최신 2016-12-31 · 신용장 556M(2025-12-31) | — | — | not_disclosed · unverified | FCF 양수 | -1 |")
    new_row = ("| tesla | companyfacts 태그 | `DebtInstrumentUnusedBorrowingCapacityAmount` 2026-06-30 — 태그 자체가 미인출액 | 5,000M | 태그 정의가 "
               "`unused … available to the entity` | **verified 5,000M**(FIX-55 2단계) | FCF 양수 — G3 없음 | -1 불변 |")
    changed = []
    if old_head in text and "[정정 2026-09-16 FIX-55 2단계]" not in text:
        text = text.replace(old_head, new_head, 1)
        changed.append("census 머리말(전수 → 주사 방식)")
    if old_row in text:
        text = text.replace(old_row, new_row, 1)
        changed.append("census tesla 행")
    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")
    return changed


def main() -> int:
    sweep = sweep_credit_tags()
    print("광역 태그 주사 — 기준일(2026) 이후 값이 있는 회사:")
    for ticker, hits in sorted(sweep.items()):
        recent = [h for h in hits if h["end"] >= "2026-01-01"]
        if recent:
            for h in recent:
                print(f"  {ticker}: {h['tag']} {h['end']} = {h['val']:,.0f} {h['unit']} ({h['form']} {h['accn']})")
    assert [t for t, hits in sweep.items() if any(h["end"] >= "2026-01-01" for h in hits)] == ["TSLA"], sweep.keys()
    assert not sweep["ORCL"], sweep["ORCL"]

    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    jud = load(RUN / "judgments.json")
    jc = fix_judgments(jud)
    from scorecard.schema import validate_judgments
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    dump(RUN / "judgments.json", jud)

    doc = load(RUN / "observations.json")
    oc = fix_observations(doc, sweep)
    validate_observations(doc, registry, RUN_ID)
    dump(RUN / "observations.json", doc)

    sources = load(RUN / "sources.json")
    sc = fix_sources(sources)
    dump(RUN / "sources.json", sources)

    import collections
    v15_counts = collections.Counter(o["source_id"] for o in doc["items"] if o["source_id"].startswith("SRC-v15-"))
    rules = load(RULES)
    rc = fix_rules(rules, v15_counts)
    validate_rules(rules)
    dump(RULES, rules)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    docs = write_sweep_md(sweep) + fix_census()
    for title, items in (("판단", jc), ("관측", oc), ("출처", sc), ("규칙", rc), ("실행", runc), ("문서", docs)):
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
