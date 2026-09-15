# FIX-53 3단계 보완: anthropic F9·F8 근거란과 TRIG-015 에 남은 `AWS $100B/10년` 라벨을 공시 문면(기존 약정 위 증액·하한)에 맞춘다
"""점수·게이트 판정 불변. TRIG-015 원천은 불변인 scorecard/baseline/v1.5/triggers.json 이라 고치지 않고, 규칙
source_text_corrections 에 정정을 두어 렌더러가 트리거 문구 끝에 붙인다. superseded 로 이미 취소선인 줄은 두었다.

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"
MARKER = "FIX-53 3단계 라벨 정정"
QUOTE = ("10-Q Note 1 문면은 `expansion of … existing multi-year commitment by more than $100.0 billion over 10.0 years` — 기존 "
         "다년 약정 **위의 증액**이고 `more than` 이라 **하한**이다. $100B/10년은 약정 총액이 아니다. $300B 합계는 v1.5 기준선 값"
         "(HANDOVER 51행)")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    jud = load(RUN / "judgments.json")
    by = {j["judgment_id"]: j for j in jud["items"]}
    changed = []

    f9 = by["anthropic.F9"]
    for i, e in enumerate(f9["evidence"]):
        if "AWS $100B/10년" in e and MARKER not in e and not e.startswith("~~"):
            f9["evidence"][i] = (e + f" [{MARKER}: {QUOTE}. `연 환산 약 $50B`·`ARR $65B 의 77%`·`커버리지 1.3배` 는 이 라벨에서 나온 "
                                 "**약정 하한 기준 환산**이다 — 약정이 더 크면 연 환산은 $50B 보다 크고 커버리지는 1.3배보다 낮다. 게이트 4 판정은 "
                                 "승계 그대로다]")
            changed.append(f"anthropic.F9 evidence[{i}]")
    if changed and f"[{MARKER}]" not in (f9.get("note") or ""):
        f9["note"] = (f9.get("note") or "") + f" | [{MARKER}] AWS $100B 라벨을 공시 문면(기존 약정 위 증액·하한)에 맞추고 파생 환산을 하한 기준으로 표시했다. 점수·게이트 불변."

    f8 = by["anthropic.F8.f8anth33"]
    for i, e in enumerate(f8["evidence"]):
        if "$300B 합계는 v1.5 기준선 값(HANDOVER 51행)]" in e:
            f8["evidence"][i] = e.replace("$300B 합계는 v1.5 기준선 값(HANDOVER 51행)]",
                                          "$300B 합계는 v1.5 기준선 값(HANDOVER 51행). `(연 ~$10B)` 는 이 라벨에서 나온 **약정 하한 기준 "
                                          "환산**이다]", 1)
            changed.append(f"anthropic.F8.f8anth33 evidence[{i}] (환산 표시)")
        e = f8["evidence"][i]
        if "(2) AWS $100B+ 안의 훈련용/서빙용 금액 구분도 미공시다" in e and "4배는 AWS 약정 하한" not in e:
            f8["evidence"][i] = e.replace(
                "**돈은 Google 이 4배인데 성능 원천은 AWS**",
                "**돈은 Google 이 4배인데 성능 원천은 AWS**(4배는 AWS 약정 하한 $100B 기준 환산 — AWS 증액이 더 크면 배수는 줄어든다, "
                f"{MARKER})", 1)
            changed.append(f"anthropic.F8.f8anth33 evidence[{i}] (4배 하한 기준)")
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    dump(RUN / "judgments.json", jud)

    rules = load(RULES)
    corr = {
        "id": "STC-AWS-100B",
        "match": "AWS $100B/10년",
        "correction": (f"⚠️ [{MARKER}: {QUOTE}. `연 ~$50B`·`ARR $65B의 77%`·`커버리지 1.3배` 는 약정 하한 기준 환산 — 약정이 더 "
                       "크면 커버리지는 1.3배보다 낮다]"),
        "marker": MARKER,
        "applies_to": ["triggers"],
        "why": ("TRIG-015 원천은 scorecard/baseline/v1.5/triggers.json(v1.5 불변)이라 고치지 않는다. anthropic F8·F9 근거란은 판단 파일에서 "
                "고쳤고 트리거만 원천이 불변이라 렌더러가 덧붙인다. 같은 초안 안에서 두 표기가 갈리지 않게 한다."),
        "decided_at": DATE,
        "note": "FIX-53 3단계 보완(msg_da0ec25d3846). 소비자: render_md._apply_text_corrections(트리거 표).",
    }
    items = [c for c in rules.get("source_text_corrections", []) if c["id"] != corr["id"]]
    rules["source_text_corrections"] = items + [corr]
    validate_rules(rules)
    dump(RULES, rules)

    run = load(RUN / "run.json")
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)
    print("판단 변경:", changed or "없음(이미 반영)")
    print("rules.source_text_corrections STC-AWS-100B · rule_hash", run["rule_hash"][:12])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
