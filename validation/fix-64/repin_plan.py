# FIX-64: 계획의 규칙 해시를 다시 고정하고 결정 표를 현재 규칙에서 다시 만든다
"""FIX-63 이 세운 방식 그대로다 — 전체 재생성은 손으로 쌓은 `rule_hash_history` 와
`규칙·자료 변경이 점수에 닿은 자리` 절을 잃으므로 **결정 표만** 다시 만든다.

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context, load_companies  # noqa: E402
from scorecard.render_md import render_plan  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
PLAN = ROOT / "plan" / f"{SLUG}.md"
PREV = "21e120ae065eee29ec8991f821d20dee0c3ee6b38f242aed5ed977ba0c866e3b"   # FIX-63 이 고정한 값

HISTORY_ANCHOR = """      있었다. 계획이 현재 규칙 해시를 주장하면서 옛 규칙 문면을 보여 주던 자리다(9차 재판정 2회 low).
      점수는 바뀌지 않았다.
"""


def table(text: str) -> re.Match[str]:
    m = re.search(r"(## 미결 규칙 결정\n\n)(\|.*?\n)(?=\n)", text, re.S)
    assert m, "결정 표를 찾지 못했다"
    return m


def main() -> int:
    ctx = load_context(SLUG)
    regen = render_plan(ctx.run, ctx.rules, load_companies(), request="", baseline_note="")
    text = PLAN.read_text(encoding="utf-8")
    out: list[str] = []

    old_m, new_m = table(text), table(regen)
    if old_m.group(2) != new_m.group(2):
        text = text[:old_m.start(2)] + new_m.group(2) + text[old_m.end(2):]
        out.append("결정 표를 현재 규칙에서 다시 만듦")

    h = load_rules("v1.7").hash
    if f"rule_hash: {h}" not in text:
        text = text.replace(f"rule_hash: {PREV}", f"rule_hash: {h}", 1)
        assert HISTORY_ANCHOR in text, "이력 마지막 항목을 찾지 못했다"
        text = text.replace(HISTORY_ANCHOR, HISTORY_ANCHOR + f"""  - hash: {h}
    pinned_at: 2026-09-17
    by: FIX-64 (최종 반영 — 네 영역 pass · 승인 직전)
    note: >-
      같은 날 다섯 번째이자 **마지막 재고정**이다. 9차 재무 계산 재판정 3회가 낸 새 발견 low 하나를 닫으면서
      `policies.f9.g1_bep_retreat_precedence` 와 decisions C-06, TEN-RA6-01 의 문면을 넓혔다 — `bep_retreat` 가
      영업흑자 회사의 G1 통과까지 막는다는 사실이 네 자리에서 빠져 있었다. **코드는 손대지 않아 점수가 한 칸도
      바뀌지 않았고**, 점수 페이로드가 `f313060` 과 바이트 동일인 것을 확인했다. 이 뒤로 승인·리포트 생성이
      이어지므로 규칙 파일은 여기서 동결된다.
""", 1)
        out.append(f"rule_hash 재고정 {h[:12]}")

    PLAN.write_text(text, encoding="utf-8", newline="\n")
    print(f"계획 변경 {len(out)}")
    for c in out:
        print("  " + c)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
