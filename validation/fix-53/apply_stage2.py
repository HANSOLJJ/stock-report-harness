# FIX-53 2단계: TSMC F5 A +2→+1 (A-STRICT-54 두 판정 일치) · alibaba 확정 미인출 여신 등록 · TSMC net_cash 설명 · 긴장 보강
"""점수가 바뀌는 것 둘(S3 tsmc F5, S4 alibaba F9)과 문서·긴장 보강. Alphabet·Amazon·Microsoft 판단은 건드리지 않는다.

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다(.gitattributes eol=lf).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_observations, validate_rules  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"
BABA_SRC = "SRC-SEC-BABA-20F-FY2026"
BABA_RAW = "3cf9799:validation/offb-24/_raw/baba-20260331.htm"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ S3 tsmc.F5
def restore(item: dict) -> dict:
    if "superseded" not in item:
        return item
    sup = item["superseded"]
    old = {"judgment_id": sup["judgment_id"], "company_id": item["company_id"], "factor": item["factor"],
           "kind": item["kind"], "score": sup.get("score"), "inputs": sup["inputs"], "evidence": sup["evidence"],
           "counter_evidence": sup.get("counter_evidence", []), "note": sup.get("note"),
           "reviewer": sup["reviewer"], "reviewed_at": sup["reviewed_at"], "status": sup.get("status", "carried")}
    for key in ("carried_from", "source_ids"):
        if key in sup:
            old[key] = sup[key]
    return old


def s3_tsmc(jud: dict) -> None:
    i, item = next((i, x) for i, x in enumerate(jud["items"]) if x["company_id"] == "tsmc" and x["factor"] == "F5")
    old = restore(item)
    sup = {k: copy.deepcopy(old[k]) for k in ("judgment_id", "score", "inputs", "evidence", "reviewer", "reviewed_at",
                                              "status", "carried_from", "note", "counter_evidence", "source_ids") if k in old}
    sup["superseded_at"] = DATE
    sup["why"] = ("A+2 엄격 읽기를 +2 회사 전부에 댄 재판정(2차 리뷰 C RC-04 · AGENTS.md 리뷰 범위 — 이번 실행이 바꾼 잣대는 "
                  "같은 잣대가 닿는 모든 회사에). codex(GPT)·Gemini 가 서로 모르게 판정해 둘 다 +1.")
    jud["items"][i] = {
        "judgment_id": "tsmc.F5.strict54",
        "company_id": "tsmc",
        "factor": "F5",
        "kind": "grade",
        "score": None,
        "inputs": {"A": 1, "H": -1},
        "evidence": [
            "📐 **[A-STRICT-54 재판정 2026-09-15] A+2 엄격 읽기** — anthropic·openai 에 댄 별표 G A 기준표(채점규칙 192·193행)의 "
            "문언 읽기를 같은 잣대로 TSMC 에 댄다(체크리스트 Q03 · 2차 리뷰 C RC-04)",
            "+2 첫 조항 불성립 — **지분이 걸린 동맹 0건.** 채점표_v1.5.md 243행 `고객에 투자 안 함. 역방향 — 고객이 선급금으로 "
            "TSMC 캐파를 댄다`",
            "+2 둘째 조항 불성립 — 채점규칙 218행 `고객 전부 아군 — NVIDIA의 적들까지` 에서 편입된 것은 **NVIDIA 의 경쟁사**"
            "(Trainium·TPU·Maia·Baltra)다. TSMC 자신의 경쟁사(Intel Foundry·Samsung 파운드리)가 TSMC 공정에 들어온 근거는 없다",
            "0 불성립 — 채점규칙 289행 `TSMC ← 고객 전부 | 매매지만 공정 락인 | ✅ | 불가 — 고객은 팹을 못 짓는다 | 동맹` 이 "
            "고객 동맹 자체를 인정한다 → **A=+1**",
            "H=-1 근거는 승계 — 적대: Intel Foundry(미 정부 10% 지분) · 관세 1/14 포고령 25%, 미국 투자 시 캐파 2.5배 무관세 = 강요된 "
            "$165B (v1.5, 이번 과제의 재검토 대상 아님)",
            "✅ 3 + A +1 + H -1 = **3** (4 → 3)",
        ],
        "counter_evidence": [
            "원문 별표 G 판정표 218행은 `TSMC | +2 | 고객 전부 아군 — NVIDIA의 적들까지 | -1 | … | 4` 로 적는다. 이 재판정은 같은 규칙서의 "
            "A 기준표(192행) 문언으로 그 행의 A 를 뒤집은 것이다 — 원문 판정표와 지금 판단이 다르다는 사실을 남긴다",
            "판정 원문 인용 정정 — Gemini 판정문과 지시서는 `고객에 투자 안 함` 을 채점표 945행으로 적었으나 그 문구는 "
            "채점표_v1.5.md **243행**에 있다(945행은 기타(Astra) 벤치마크 표). 이 판단은 243행을 인용한다",
        ],
        "note": ("[A-STRICT-54] 비 Claude 두 판정 일치 — codex(GPT) validation/a2-strict-54/codex.md · Gemini "
                 "validation/a2-strict-54/gemini.md (HANSOLJJ/review-obsreg, 5e5aa3c 까지), 조율자 대조 설계진행 "
                 "validation/a2-strict-54-verdict.md. 같은 재판정에서 Alphabet·Amazon·Microsoft 는 +2 유지(판단 변경 없음). "
                 "옛 판단은 superseded 에 있다."),
        "reviewer": "설계진행(A-STRICT-54 codex·Gemini 독립 일치)",
        "reviewed_at": DATE,
        "status": "new",
        "source_ids": ["SRC-v15-rule", "SRC-v15-md"],
        "previous_judgment_id": old["judgment_id"],
        "superseded": sup,
    }


# ------------------------------------------------------------------ S4 alibaba undrawn_credit
def s4_alibaba(obs: dict) -> None:
    ids = {"alibaba.undrawn_credit.fix53", "alibaba.undrawn_credit_approx.fix53"}
    obs["items"] = [o for o in obs["items"] if o["observation_id"] not in ids]
    obs["items"].append({
        "observation_id": "alibaba.undrawn_credit.fix53",
        "company_id": "alibaba",
        "metric": "undrawn_credit",
        "value": 3330000000.0,
        "unit": "USD",
        "as_of": "2026-03-31",
        "observed_at": DATE,
        "kind": "actual",
        "source_id": BABA_SRC,
        "status": "verified",
        "basis": {
            "form": "20-F",
            "accession": "0001193125-26-231755",
            "measured_as_of": "2026-03-31",
            "original_currency": "USD",
            "definition": "설계 지침 6.4 런웨이 분자의 `조건이 확인된 확정 미인출 여신`",
            "primary": {
                "location": "감사 연결재무제표 주석 21 Bank borrowings — (iii) 항 뒤 문단",
                "raw_line": 25431,
                "quote": ("As of March 31, 2026, the Company is in compliance with all covenants in relation to bank borrowings. "
                          "As of March 31, 2025 and 2026, the Company had a revolving credit facility provided by certain "
                          "financial institutions which has not yet been drawn down. In September 2025, the Company amended "
                          "the terms of the revolving credit facility agreement. The size of the credit facility was amended "
                          "from US$ 6.5 billion to US$ 3.33 billion"),
            },
            "cross_check": {
                "location": "Item 5 MD&A 유동성",
                "raw_line": 4274,
                "quote": "as well as a US$3.33 billion revolving credit facility which we have not yet drawn as of March 31, 2026",
            },
            "conditions_confirmed": ("미인출(주석·MD&A 둘 다) · 약정 준수(`in compliance with all covenants in relation to bank "
                                     "borrowings`) · 만기 2028-09-30(연장 옵션) · 금리 SOFR/HIBOR +66bp. 원문 보존 " + BABA_RAW),
            "statement_body_first": "감사 재무제표 주석을 1차 근거로, MD&A 를 교차 확인으로 둔다.",
            "excluded_other_facility": "US$3.17B 회전여신(주석 21 (ii))의 미사용 약정 `approximately US$ 2.6 billion` 은 합산하지 "
                                       "않았다 — alibaba.undrawn_credit_approx.fix53 참조.",
            "runway_effect": "런웨이 (19,068 + 3,330) / 7,226 = 3.0996년 (등록 전 19,068 / 7,226 = 2.6388년). G3 step -1 → 0.",
            "why_now": ("설계 지침 6.4 가 런웨이 분자에 확정 미인출 여신을 넣으라고 정해 두었는데 alibaba 에 undrawn_credit 관측이 "
                        "없었다(2차 리뷰 B 발견). 새 결정이 아니라 빠진 관측의 등록이다."),
        },
        "raw": "미인출 회전여신 US$3.33B (2026-03-31, 20-F 주석 21)",
        "note": "FIX-53 2단계. 감사 주석 1차 · MD&A 교차. 런웨이 분자에 들어간다.",
    })
    obs["items"].append({
        "observation_id": "alibaba.undrawn_credit_approx.fix53",
        "company_id": "alibaba",
        "metric": "undrawn_credit",
        "value": 2600000000.0,
        "unit": "USD",
        "as_of": "2026-03-31",
        "observed_at": DATE,
        "kind": "estimate",
        "source_id": BABA_SRC,
        "status": "incompatible_basis",
        "basis": {
            "form": "20-F",
            "accession": "0001193125-26-231755",
            "facility": "US$3.17B 회전여신(부수 시설 포함) — 3.33B 시설과 **별개**",
            "primary": {
                "location": "감사 연결재무제표 주석 21 Bank borrowings (ii)",
                "raw_line": 25431,
                "quote": ("As of March 31, 2026, the Company had a total outstanding borrowing amount of RMB 3.9 billion under the "
                          "ancillary facility arrangement by way of short-term loan facilities, and the unutilized commitment of "
                          "this revolving credit facility was approximately US$ 2.6 billion."),
            },
            "cross_check": {"location": "Item 5 MD&A", "quote": "unutilised commitment of approximately US$2.6 billion"},
            "why_not_in_runway": ("**런웨이에 넣지 않는다.** 원문이 `approximately` 라 확정 수치가 아니다. status 를 사용 가능 "
                                  "상태가 아닌 incompatible_basis(확정 금액 기준과 맞지 않음), kind 를 estimate 로 두어 엔진이 읽지 "
                                  "않게 했다."),
            "sensitivity": "넣었다면 런웨이 (19,068 + 3,330 + 2,600) / 7,226 = 3.4595년 — 3년 이상이라 G3 step 0 으로 결론은 같다.",
        },
        "raw": "미사용 약정 approximately US$2.6B (3.17B 시설, 런웨이 제외)",
        "note": "FIX-53 2단계. 근사치라 런웨이 분자에서 뺀다. 결론 민감도는 basis.sensitivity.",
    })


# ------------------------------------------------------------------ TSMC net_cash 설명
OLD_Q = "tsmc `Other financial assets` 59,702.9 NT$백만(US$1,903.2M)의 성격."
NEW_Q = ("~~tsmc `Other financial assets` 의 제한 여부는 20-F 가 내역을 주지 않는다~~ **[정정 2026-09-15 FIX-53]** 보존 20-F 주석 35 "
         "PLEDGED ASSETS 가 담보로 제공한 예금증서를 적는다 — `certificate of deposits recorded in other financial assets as "
         "collateral mainly for building lease agreements … NT$ 129.40 million` (2025-12-31, f14a235:validation/tsm-edgar-29/_raw/"
         "tsm-20251231.htm). 59,702.9 NT$백만 중 담보는 129.40 NT$백만(0.2%)이다. **민감도** — 제외하면 순현금 (2,171,587.1 − 129.40) "
         "/ 31.37 = US$69.2208B(현재 69.2250B)이고 P2 밴드 -1 은 같다. 이것은 P2 의 시장성 기준 설명이지 G3 즉시성 제약을 P2 로 "
         "상속하라는 뜻이 아니다. 지금은 넣어 둔 채로 둔다 — 다른 회사의 자금운용 예금을 시장성 증권으로 세면서 tsmc 만 빼면 기준이 "
         "어긋나기 때문이다.")


def fix_tsmc_net_cash(rules: dict, obs: dict) -> None:
    q = rules["policies"]["f6"]["net_cash"]["open_questions"]
    for i, text in enumerate(q):
        if text.startswith(OLD_Q) or text.startswith("~~tsmc `Other financial assets`"):
            q[i] = NEW_Q
    o = next(x for x in obs["items"] if x["observation_id"] == "tsmc.net_cash.nc37")
    b = o["basis"]
    b["open_item_correction"] = {
        "corrected_at": DATE, "task": "FIX-53 2단계 (2차 리뷰 B 발견)",
        "pledged_assets_note_35": "NT$ 129.40 million 예금증서 담보(주로 건물 임대차 계약) — 2025-12-31",
        "sensitivity": {"excluding_pledged_usd": 69220838381, "current_usd": o["value"], "p2_band_unchanged": True},
        "scope": "P2 시장성 기준의 설명. G3 즉시성 제약을 P2 로 상속하지 않는다.",
    }
    b["open_item"] = ("~~" + b["open_item"].split("~~")[-1].strip() + "~~ → open_item_correction 참조"
                      if not b["open_item"].startswith("~~") else b["open_item"])


# ------------------------------------------------------------------ 긴장
def fix_tensions(rules: dict) -> None:
    tens = rules["open_tensions"]
    rc03 = next(t for t in tens if t["id"] == "TEN-RC-03")
    rc03["affected"] = [
        {"company_id": "alphabet", "judgment_id": "alphabet.F5",
         "why": "Meta 가 TPU 를 떠날 수 있음 — 239행 이탈 조건과 286행 `Meta → AMD·Google TPU 멀티벤더 | 매매 | … | 조달` 사이에서 "
                "Alphabet 의 경쟁사 편입 근거가 흔들린다",
         "source_lines": ["채점규칙 239행", "채점규칙 286행"]},
        {"company_id": "amazon", "judgment_id": "amazon.F5",
         "why": "Bedrock 입점사는 떠날 수 있음(다른 매대)인데 A+2", "source_lines": ["채점규칙 277행"]},
        {"company_id": "meta", "judgment_id": "meta.F5",
         "why": "광고주는 떠날 수 있음(분산)인데 A+1", "source_lines": ["채점규칙 278행"]},
        {"company_id": "nvidia", "judgment_id": "nvidia.F5",
         "why": "투자처·하이퍼스케일러가 자체 칩으로 떠날 수 있어 불인정", "source_lines": ["채점규칙 275행"]},
    ]
    rc03["note"] = ("[FIX-53 2단계] A-STRICT-54 재판정에서 이 긴장에 기대는 모호함이 회사별로 드러나 affected 에 적었다. **별건 — "
                    "OpenAI Stargate:** 합작 법인 하나를 지분 동맹 하나로 셀지 참여사(Oracle·SoftBank·MGX)별로 셀지 채점규칙 192행이 "
                    "정하지 않는다. openai.F5.impl48 은 하나로 셌다.")
    tens[:] = [t for t in tens if t["id"] != "TEN-RB-Q10"]
    tens.append({
        "id": "TEN-RB-Q10",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": "RB-Q10(체크리스트 Q10) · obsreg 2차 리뷰 B(codex)",
        "judgment_ids": ["microsoft.F3", "spacex-xai.F3", "tesla.F3"],
        "subject": "F3 가속도가 단일 성장률 하나로 pass — 성장률의 변화(가속)를 재현할 수 없다",
        "tension": ("microsoft.F3 `Copilot 유료 시트 3,000만, 분기 +50%` · spacex-xai.F3 `AI 세그먼트 Q2 $2.56B, +247% YoY` · "
                    "tesla.F3 `FSD 활성 구독 148만(+56% YoY)` 가 각각 성장률 하나로 가속도 pass 다. 같은 정의의 비교 쌍(직전 기간의 "
                    "성장률)이 없어 **가속**인지 **성장**인지 가를 수 없다."),
        "direction": "하향 가능(가속도 pass → partial·fail 검토). 판정하지 않는다.",
        "rechecker": "2026-11 재채점 때 판단자.",
        "why_carried_exception": "승계 판단의 기존 논리이고 이번 실행이 F3 가속도 잣대를 바꾸지 않았다.",
        "score_impact_now": "없다.",
    })


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    rules = load(RULES)
    jud = load(RUN / "judgments.json")
    obs = load(RUN / "observations.json")

    s3_tsmc(jud)
    s4_alibaba(obs)
    fix_tsmc_net_cash(rules, obs)
    fix_tensions(rules)

    validate_rules(rules)
    validate_judgments(jud, registry, rules, RUN_ID)
    validate_observations(obs, registry, RUN_ID)
    dump(RULES, rules)
    dump(RUN / "judgments.json", jud)
    dump(RUN / "observations.json", obs)

    run_path = RUN / "run.json"
    run = load(run_path)
    run["rule_hash"] = load_rules("v1.7").hash
    dump(run_path, run)
    print("S3 tsmc.F5 → tsmc.F5.strict54 A=1 · S4 alibaba.undrawn_credit 3.33B verified + 2.6B incompatible_basis")
    print("TSMC net_cash open_question 정정 · TEN-RC-03 affected · TEN-RB-Q10 등록 · rule_hash", run["rule_hash"][:12])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
