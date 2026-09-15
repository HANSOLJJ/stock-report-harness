# FIX-52 S2: 비상장 승격 조건 arr_growth 가 진짜 ARR 만 받게 한다 — 런레이트 arr 로 anthropic 이 승격받던 것을 막는다
"""리뷰 C(codex) Q02 발견. `calc_f6_params.py` 가 `arr` 관측이 `kind=run_rate` 인 것을 `kind_notes` 에 적고도
`arr_growth` 조건에 그대로 써서 anthropic 이 F6 -4 → -3 승격을 받았다. 사용자 결정은 **진짜 ARR 만 인정**이다.

**지시서 문구와 다른 점 하나.** 지시서는 `accepted_kinds: ["arr"]` 였다. 그러나 관측 kind 어휘
(schema.OBSERVATION_KINDS)는 actual·estimate·run_rate·derived·text 이고 `arr` 은 kind 가 아니라 **지표 이름**이다.
`["arr"]` 로 두면 어떤 관측도 그 kind 를 가질 수 없어 조건이 영원히 불충족인 선언이 된다. 공시된 진짜 ARR 은
`metric=arr · kind=actual` 로 등록되므로 `["actual"]` 로 둔다. 현재 데이터에서 결과는 같다(anthropic·openai 의
arr·arr_prior 넷이 전부 run_rate).

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
from scorecard.schema import validate_rules  # noqa: E402

RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    raw = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    out = json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(p, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))


def main() -> int:
    rules = load(RULES)
    corr = rules["policies"]["f6"]["private_correction"]
    cond = {c["id"]: c for c in corr["conditions"]}["arr_growth"]
    cond["accepted_kinds"] = ["actual"]
    cond["accepted_kinds_decision"] = {
        "decided_at": DATE,
        "decided_by": "사용자 (리뷰 C codex Q02 발견 · FIX-52)",
        "rule": "**진짜 ARR 만 인정한다.** 입력 arr·arr_prior 중 하나라도 kind 가 actual 이 아니면 조건 불충족이다.",
        "why": ("엔진이 arr 관측의 kind=run_rate 를 kind_notes 에 적고도 이 조건에 그대로 써서 anthropic 이 "
                "0.383 ≥ 0.30 으로 F6 -4 → -3 승격을 받았다. 이름은 arr 이지만 런레이트는 ARR 이 아니다(PRIV-ARR-17)."),
        "wording_vs_instruction": ("지시서 문구는 `accepted_kinds: [\"arr\"]` 였다. `arr` 은 관측 kind 어휘가 아니라 지표 "
                                   "이름이라 그대로 두면 어떤 관측도 충족할 수 없는 선언이 된다. 공시된 ARR 은 "
                                   "`metric=arr · kind=actual` 로 등록되므로 `[\"actual\"]` 로 옮겼다. 현재 결과는 같다."),
        "consumer": "calc_f6_params.compute_private — 불충족이면 calc.correction.conditions.arr_growth.reason 에 사유를 남긴다.",
        "effect": "anthropic F6 -3 → -4. openai 는 capital_efficiency 0.22 로 이미 미충족이라 변동 없다.",
        "not_changed": ("capital_efficiency(arr / cumulative_raised)도 같은 run_rate arr 을 읽는다. 사용자 결정 범위가 "
                        "arr_growth 라 이 조건에는 kind 제한을 두지 않았다. require_all 이라 지금은 arr_growth 불충족만으로 "
                        "승격이 막힌다."),
    }
    cond["note"] = (cond.get("note", "") + " | [FIX-52] accepted_kinds 로 kind 를 제한한다 — 런레이트는 이 조건을 충족하지 못한다.")
    validate_rules(rules)
    dump(RULES, rules)

    run_path = RUN / "run.json"
    raw = io.open(run_path, encoding="utf-8", newline="").read()
    old = json.loads(raw)["rule_hash"]
    new = load_rules("v1.7").hash
    if old != new:
        io.open(run_path, "w", encoding="utf-8", newline="").write(raw.replace(old, new))
    print("arr_growth.accepted_kinds =", cond["accepted_kinds"])
    print(f"rule_hash {old[:12]} -> {new[:12]}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
