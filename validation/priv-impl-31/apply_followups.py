# 검토 보완 넷 중 관측·판단에 닿는 것을 새 실행에 반영한다 — anthropic F8 근거란 교체 (네트워크 없음)
"""**승인된 실행은 건드리지 않는다.** 대상은 `ai-scorecard-2026-09-obsreg` 뿐이다.

보완 넷 중 하나·둘·셋은 규칙 파일과 코드(`v1.7.json`·`schema.py`·`rules.py`)라 여기서 다루지 않는다.
이 스크립트는 **넷째 — anthropic F8 근거란 교체** 만 한다.

## 무엇을 바꾸나

승계 근거란이 AWS 집중을 **2차 증언**(증권사 자료)으로 적고 있었다. 실제로는 **Amazon 이 SEC 8-K 로
직접 공시한 사실**이다. 2차 증언을 1차 공시로 바꾸고, **확인된 것과 확인되지 않은 것을 나누고**,
재판정 조건을 등재한다.

**점수는 −3 유지다.** Google 몫이 훈련이 아니라는 증거가 있는 것이 아니라 **공시가 없을 뿐**이고,
미공시를 '아니다' 로 읽지 않는다 — 오늘 하루 종일 고친 것이 그 종류다.

사용:
    python validation/priv-impl-31/apply_followups.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID

# C-13 F8-ANTH-33 (8ddb0ae) 이 SEC 에서 읽은 Amazon 8-K 네 건.
AMZN_8K = [
    ("0001018724-25-000002", "2025-02-06",
     "Project Rainier: A collaboration with Anthropic using hundreds of thousands of Trainium2 chips "
     "to build the world's largest AI compute cluster."),
    ("0001018724-25-000121", "2025-10-30",
     "Launched Project Rainier, a massive AI compute cluster containing nearly 500,000 Trainium2 chips, "
     "to build and deploy Anthropic's leading Claude AI models."),
    ("0001018724-26-000002", "2026-02-05",
     "Trainium2 powers Project Rainier, the world's largest operational AI compute cluster with "
     "500,000+ Trainium2 chips, which Anthropic is using to train its industry-leading AI model, Claude."),
    ("0001018724-26-000012", "2026-04-29",
     "Announced that Anthropic will secure up to five gigawatts (GW) of current and future generations "
     "of Amazon's Trainium chips to train and power their advanced AI models."),
]

NEW_EVIDENCE = [
    "컴퓨트 100% 외부 + 공급자 3사가 전부 경쟁자 — Google(Gemini) · Amazon(Nova) · "
    "Microsoft(OpenAI 지분 27% 보유). **OpenAI 27% 는 Microsoft 의 OpenAI 지분율**이지 "
    "Anthropic 의 컴퓨트 배분이 아니다(v1.5 원본 188·198·217·350행에서 확인).",

    "🔧 컴퓨트 약정 $300B — Google Cloud $200B/5년(연 ~$40B) + AWS $100B/10년(연 ~$10B) + Azure $30B. "
    "AWS 분은 **Amazon 10-Q Note 1 에 직접 공시돼 있다**: \"In Q2 2026, AWS and Anthropic announced an "
    "expansion of the strategic collaboration and existing multi-year commitment by more than $100.0 billion "
    "over 10.0 years, which includes contractual obligations related to the performance of AWS chips.\" "
    "(보존 원문 C-13 3cf9799:validation/offb-24/_raw/amzn-20260630.htm 에서 worker 직접 대조)",

    "📐 **[근거 교체 2026-09-11] AWS 훈련 집중은 증권사 2차 증언이 아니라 Amazon 의 1차 공시다.** "
    "승계 근거란은 이것을 DS투자증권 9/7 자료로 적고 있었으나, 실제로는 Amazon 이 SEC Form 8-K "
    "(Ex 99.1) 네 건으로 직접 공시한 사실이다(C-13 F8-ANTH-33, 8ddb0ae). "
    + " · ".join(f"{accn}({date})" for accn, date, _ in AMZN_8K) + ". "
    "2026-02-05 공시 원문: \"Trainium2 powers Project Rainier, the world's largest operational AI compute "
    "cluster with 500,000+ Trainium2 chips, which Anthropic is using to train its industry-leading AI model, "
    "Claude.\" 증권사 자료는 이 공시 사실에 질적 해석을 얹은 2차 출처였다.",

    "✅ **확인된 것** — (1) Project Rainier 의 실체와 규모(2025-10 nearly 500,000 → 2026-02 500,000+ "
    "Trainium2). (2) Anthropic 이 그 클러스터로 Claude 를 **훈련(train)** 한다는 Amazon 의 명시. "
    "(3) 2026-04-29 공시의 최대 5GW Trainium 확보와 train and power 문면. "
    "(4) AWS 약정 $100B/10년과 칩 성능 연계 의무(10-Q Note 1).",

    "❓ **확인되지 않은 것** — (1) **Google 몫의 훈련/서빙 구분.** Alphabet 10-K(FY2025)·10-Q(2026 Q1·Q2) "
    "본문에 'Anthropic' 이 **0건**이다. 계약 존재·금액·기간·용도가 전부 회사 미공시다. Google Cloud 는 "
    "고객사 다중 기가와트 TPU 계약을 백로그로 포괄 기술할 뿐이다. (2) AWS $100B+ 안의 훈련용/서빙용 "
    "금액 구분도 미공시다. (3) 따라서 **돈은 Google 이 4배인데 성능 원천은 AWS** 라는 긴장(#10)은 "
    "해소되지 않고 실증 상태만 갱신됐다.",

    "⚖️ **점수 −3 유지.** 하향하지 않는 이유는 **Google 몫이 훈련이 아니라는 증거가 있는 것이 아니라 "
    "공시가 없을 뿐**이기 때문이다. 미공시를 '아니다' 로 읽으면 우리가 못 찾은 것을 그 기업의 구조로 "
    "둔갑시키게 된다(MISS-LABEL-23 이 세운 원칙). 장부상 3사 분산은 성립하고, 물리적 훈련 집중은 "
    "AWS 쪽에서만 1차 확인됐다.",

    "🔁 **재판정 조건 (−4 재검토)** — 셋 중 **하나라도** 1차 자료로 확인되면 −4 를 재검토한다. "
    "(1) Alphabet 이 고객사별로 분리 공시해 Anthropic 계약의 규모·용도가 드러나거나, "
    "(2) Anthropic 이 훈련 컴퓨트 구성을 공시하거나, "
    "(3) Google 몫이 **서빙 전용**임이 1차 자료로 확인되는 경우. "
    "셋 다 '미공시가 해소되는' 방향이고, 추측으로는 재판정하지 않는다.",

    "FTC 가 계약 배타성 검토",

    "자체 칩이 이 항목의 구조적 해법이지만 2028~2030년 양산이라 당분간 −3 유지",

    "🆕 제로 데이터 보존 약속(9/2) — 기업 고객의 규제 의존 완화 방향, 단 \"고객이 직접 검증해야\" 조건부",
]


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_judgments, write_json

    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    jud = load_json_strict(RUN / "judgments.json")
    run = load_json_strict(RUN / "run.json")

    bar = "=" * 112
    print(bar)
    print(f"PRIV-IMPL-31 보완 — {RUN_ID} anthropic F8 근거란 교체 (승인 실행 미변경)")
    print(bar)

    target = next(j for j in jud["items"] if j["company_id"] == "anthropic" and j["factor"] == "F8")
    before_score, before_n = target["score"], len(target["evidence"])
    stale = [e for e in target["evidence"] if "DS투자증권" in e]

    print(f"\n[1] 교체 전 — score {before_score} · evidence {before_n}건")
    for e in stale:
        print(f"  제거: {e[:110]}…")

    target["evidence"] = list(NEW_EVIDENCE)
    target["previous_judgment_id"] = target["judgment_id"]
    target["judgment_id"] = "anthropic.F8.f8anth33"
    target["status"] = "new"
    target["reviewer"] = "worker(HANSOLJJ) — C-13 F8-ANTH-33 8ddb0ae 기반"
    target["reviewed_at"] = "2026-09-11"
    target.pop("carried_from", None)
    target["note"] = (
        "F8-ANTH-33 반영(2026-09-11). **점수 -3 은 바뀌지 않았고 근거란만 바뀌었다.** "
        "2차 증언(증권사 자료)을 1차 공시(Amazon SEC 8-K 4건 + 10-Q Note 1)로 교체하고, "
        "확인된 것과 확인되지 않은 것을 나누고, 재판정 조건을 등재했다. "
        "Google 몫의 훈련/서빙 구분은 Alphabet 공시에 Anthropic 이 0건이라 확인 불가이며, "
        "**미공시를 '아니다' 로 읽지 않기 때문에** 하향하지 않는다.")
    target.setdefault("source_ids", [])
    for sid in ("SRC-SEC-AMZN-10Q-2026Q2",):
        if sid not in target["source_ids"]:
            target["source_ids"].append(sid)

    print(f"\n[2] 교체 후 — score {target['score']} · evidence {len(target['evidence'])}건 · "
          f"status {target['status']} · previous {target['previous_judgment_id']}")
    # 증권사 자료는 '주장' 에서 사라지고 '무엇을 무엇으로 바꿨는지' 의 기록으로만 남아야 한다.
    claim = [e for e in target["evidence"] if "DS투자증권" in e and "근거 교체" not in e]
    record = [e for e in target["evidence"] if "DS투자증권" in e and "근거 교체" in e]
    print(f"  증권사 2차 증언을 근거로 쓰는 항목: {len(claim)}건 (0 이어야 한다)")
    print(f"  교체 이력으로만 언급하는 항목: {len(record)}건")
    print(f"  8-K 접수번호 등재: {sum(any(a in e for a, _, _ in AMZN_8K) for e in target['evidence'])}건")
    print(f"  재판정 조건 등재: {sum('재판정 조건' in e for e in target['evidence'])}건")

    validate_judgments(jud, registry, load_rules(run["rule_version"]).payload, RUN_ID)
    write_json(RUN / "judgments.json", jud)

    run["assumptions"] = list(run["assumptions"]) + [
        "anthropic F8 근거란은 2026-09-11 에 2차 증언에서 1차 공시로 교체했다(C-13 F8-ANTH-33). 점수 -3 은 "
        "바뀌지 않았고, Google 몫의 훈련/서빙 구분은 Alphabet 공시에 Anthropic 이 0건이라 확인 불가다. "
        "미공시를 아니다로 읽지 않아 하향하지 않았고 재판정 조건을 근거란에 등재했다",
        "원천 정책을 SRC-POLICY-32 결론으로 개정했다. usage_scope 는 개인·법인 내부 사용의 합집합이고, "
        "라이선스가 원소를 전부 허용해야 적격이라 alphavantage·financialmodelingprep·finnhub 셋이 "
        "allowed 에서 not_adopted 로 내려갔다. 셋 다 실제로 쓰이지 않아 점수 영향이 없다(F6·F9 는 SEC 만 쓴다)",
    ]
    write_json(RUN / "run.json", run)
    print(f"\n[3] 저장 — 판단 {len(jud['items'])}건")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
