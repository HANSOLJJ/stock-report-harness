# IMPL-50: C-11 — 영업외 비중을 ⑦ 근거로 이월한다는 채점표 범례 줄을 차단한다 (문서·규칙 note 만, 점수 무영향)
"""할 것 넷 (지시서 msg_a03a91c5a62e).

1. decisions C-11 → resolved · block_carryover · 결정자 `설계진행 제안 · 사용자 확인 전`.
2. p4 conditions[nonop_share] 에 scope — F6 P4 전용, ⑦ 으로 이월하지 않는다.
3. policies.f7 이 없어 F7 판단 14건 note 에 반대편 문장 — 영업외 비중은 F7 입력이 아니다.
4. 설계 지침 C-11 행에 낡음 표시 + 대체 문장.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(HASH-EOL).
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_rules  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
GUIDE = ROOT / "docs" / "scorecard" / "design-guideline.md"
DATE = "2026-09-14"
MARK = "[IMPL-50]"

F7_NOTE = (f"{MARK} **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~356행 `평가이익은 ⑦의 "
           "증거가 아니다 … ⑥ — TTM PER 무효 처리` · 438행 ⑦ `쓰지 않는 것` 의 `지분 평가이익(⑥ 소관)`. 채점표 3-1a 범례 "
           "L804 의 `→ ⑦ 근거로 이월` 은 C-11 block_carryover 로 차단됐다(설계진행 제안 · 사용자 확인 전).")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def write_text(p: Path, text: str, raw: str) -> None:
    nl = "\r\n" if "\r\n" in raw else "\n"
    io.open(p, "w", encoding="utf-8", newline="").write(text.replace("\r\n", "\n").replace("\n", nl))


def dump(p: Path, d: dict) -> None:
    raw = io.open(p, encoding="utf-8", newline="").read()
    out = json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    write_text(p, out, raw)


def update_rules(rules: dict) -> None:
    dec = {x["id"]: x for x in rules["decisions"]}["C-11"]
    keep = {k: dec[k] for k in ("id", "blocking", "affects", "summary", "recommendation")}
    dec.clear()
    dec.update({
        "id": "C-11",
        "status": "resolved",
        "blocking": keep["blocking"],
        "affects": keep["affects"],
        "summary": keep["summary"],
        "recommendation": keep["recommendation"],
        "choices": ["block_carryover", "allow_carryover"],
        "chosen": "block_carryover",
        "decided_at": DATE,
        "decided_by": "설계진행 제안 · 사용자 확인 전",
        "confirmed_model": {
            "rule": "영업외 비중은 **F6 P4 전용**이다. ⑦ 근거로 이월하지 않는다.",
            "blocked_text": ("채점표 3-1a 범례 L804 `| **영업외 비중** | (세전이익 − 영업이익) ÷ 세전이익. **30% 넘으면 TTM "
                             "무효** | ❌ → ⑦ 근거로 이월 |` 의 `→ ⑦ 근거로 이월`"),
            "reasons": [
                "별표 I 351~356행 `🔑 평가이익은 ⑦의 증거가 아니다` — 평가이익은 `⑥ — TTM PER 무효 처리`, 순환금융은 `⑦`. "
                "영업외 비중이 잡는 것의 큰 몫이 이 평가이익이다(채점표 각주 ᵃ NVIDIA 랩 지분 평가익)",
                "채점규칙 438행 ⑦ 행 `쓰지 않는 것` 에 `지분 평가이익(⑥ 소관)` · 437행 ⑥ 행이 `TTM PER(영업외 비중 30%+면 "
                "무효)` 로 이 지표를 ⑥ 에 둔다",
                "⑦ 판정은 별표 I 2축(319~322행: 조달 의존 고객 비중 × 내 돈이 돌아오는가)이다. 영업외 비중은 어느 축의 "
                "입력도 아니다. 같은 값을 ⑥ P4 와 ⑦ 에 둘 다 넣으면 별표 J 가 금지한 이중 계상 구조다(C-13 C09-C11-F7-41 판정)",
            ],
            "source_text_against": ("**원문에 반대로 읽힐 수 있는 자리가 하나 있다.** 별표 I 347행 `측정 가능 / 불가` 표의 "
                                    "`측정 가능 (재무제표·공시)` 칸이 `RPO ÷ 연매출 · 단일 고객 집중도 · 실행된 투자액 · "
                                    "영업외 이익 비중` 을 ⑦ 절 안에 적는다. 이 표는 **측정 가능성 분류**이고 판정 입력 지정이 "
                                    "아니다 — 판정은 2축 표(319~322행)이고 바로 아래 351~356행이 평가이익을 ⑥ 으로 보낸다. "
                                    "그래서 차단 판정은 서지만, 347행이 그 지표를 ⑦ 절에 적는다는 사실은 숨기지 않는다."),
            "what_changed": "문서·규칙 note 만. 차단 전에도 이 경로를 읽는 코드가 없었다.",
        },
        "scope": {
            "what_this_is": ("**문서와 규칙 note 의 차단이다.** F7 은 14개사 전부 carried(승계) 판단이고 C-11 을 읽는 "
                             "코드가 없어 이월 경로가 구현된 적이 없다."),
            "score_impact": "없다.",
            "user_confirmation": ("**사용자 확인 전.** 점수 무영향이라 설계진행 제안으로 미리 넣었다. 사용자가 "
                                  "allow_carryover 를 고르면 되돌린다."),
            "v15_untouched": "v1.5.json 의 C-11 은 pending 그대로다 — v1.5 는 불변.",
        },
    })

    cond = {c["id"]: c for c in rules["policies"]["f6"]["p4"]["conditions"]}["nonop_share"]
    cond["scope"] = "F6 P4 전용. ⑦ 으로 이월하지 않는다"
    cond["scope_why"] = ("별표 I 351~356행(평가이익은 ⑦ 증거가 아니고 ⑥ TTM PER 무효 처리) · 채점규칙 438행(⑦ `쓰지 않는 것` "
                         "지분 평가이익 ⑥ 소관). C-11 block_carryover.")
    # 자기 정정 — NONOP-44 에서 formula 를 세전이익 기준으로 고치고 이 note 의 옛 산식을 남겨 두었다.
    old_note = "|영업외 비중| >= 0.30. 영업외손익 = net_income_ttm - operating_income_ttm"
    if cond["note"] == old_note:
        cond["note"] = ("|영업외 비중| >= 0.30. 영업외손익 = pretax_income_ttm − operating_income_ttm (formula 참조) | "
                        "~~영업외손익 = net_income_ttm - operating_income_ttm~~ — NONOP-44(2026-09-14) 이전 산식. formula 는 "
                        "고쳤으나 이 note 가 남아 있었다(IMPL-50 에서 발견).")
    steps = cond["stored_vs_recomputed"]["next_steps"]
    for i, s in enumerate(steps):
        if s.startswith("C-11(") and MARK not in s:
            steps[i] = s + f" — {MARK} **해소: block_carryover(설계진행 제안 · 사용자 확인 전).** ⑦ 으로 이월하지 않는다"


def update_judgments(jud: dict) -> int:
    n = 0
    for j in jud["items"]:
        if j["factor"] != "F7":
            continue
        base = (j.get("note") or "").split(" | " + MARK)[0]
        j["note"] = (base + " | " + F7_NOTE) if base else F7_NOTE
        n += 1
    return n


def update_guideline() -> bool:
    raw = io.open(GUIDE, encoding="utf-8", newline="").read()
    s = raw.replace("\r\n", "\n")
    old = ("| C-11 | S-SCORE의 영업외 비중 설명은 F7로 이월이라고 하나 별표 I는 평가익 자체를 F7 근거로 금지 | "
           "손익의 질 참고로만 유지. 고객 자금 환류는 별도 근거 필요 |")
    new = ("| C-11 | ~~S-SCORE의 영업외 비중 설명은 F7로 이월이라고 하나 별표 I는 평가익 자체를 F7 근거로 금지~~ "
           "**[낡음 2026-09-14 IMPL-50] 해소 — block_carryover(설계진행 제안 · 사용자 확인 전).** 영업외 비중은 F6 P4 "
           "전용이며 F7 로 이월하지 않는다(별표 I 351~356행 · 채점규칙 438행). 채점표 3-1a 범례의 `→ ⑦ 근거로 이월` 은 "
           "차단됐다. | 손익의 질 참고로만 유지. 고객 자금 환류는 별도 근거 필요 |")
    if new in s:
        return False
    assert s.count(old) == 1, "설계 지침 C-11 행을 못 찾음"
    write_text(GUIDE, s.replace(old, new, 1), raw)
    return True


def main() -> int:
    rules = load(RULES)
    update_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    jpath = RUN / "judgments.json"
    jud = load(jpath)
    n = update_judgments(jud)
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    validate_judgments(jud, registry, rules, RUN_ID)
    dump(jpath, jud)

    g = update_guideline()

    run_path = RUN / "run.json"
    raw = io.open(run_path, encoding="utf-8", newline="").read()
    old = json.loads(raw)["rule_hash"]
    new = load_rules("v1.7").hash
    if old != new:
        io.open(run_path, "w", encoding="utf-8", newline="").write(raw.replace(old, new))

    print("1. C-11 resolved · block_carryover · 설계진행 제안 · 사용자 확인 전")
    print("2. p4 nonop_share scope 등재 (+ 옛 산식 note 자기 정정)")
    print(f"3. F7 판단 note {n}건")
    print(f"4. 설계 지침 C-11 행 {'낡음 표시' if g else '이미 반영됨'}")
    print(f"   run.json rule_hash {old[:12]} -> {new[:12]}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
