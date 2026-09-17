# FIX-64: bep_retreat 의 도달 범위를 문면이 실제보다 좁게 적던 네 자리를 넓힌다 (점수 불변)
"""9차 재무 계산 재판정 3회 `review-obsreg ce0fd57:reviews/_parts/…/financial-calc.md` 의 새 발견 low.

네 자리가 `손실률 밴드보다 앞선다` 로 **적자 맥락에서만** 서술하는데, 실제 코드는
`g1_pass = (not bep_retreat) and (margin is None or margin > 0)` 이라 **흑자 회사도 통과시키지 않는다.**
동작 자체는 채점규칙 470행의 OR 조건 읽기와 어긋나지 않고 FIX-59 때부터 같다 — 서술만 좁았다.

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
M = "FIX-64"

WIDER = (
    f"**[{M} 보강 · 9차 재무 계산 재판정 3회(Claude 독립 세션) low] 적자 맥락만이 아니다.** "
    "`calc_f9.compute_f9` 의 `g1_pass = (not bep_retreat) and (margin is None or margin > 0)` 이라 "
    "`bep_retreat: yes` 면 **영업흑자 회사도 G1 을 통과하지 못하고** 영업적자 구간으로 내려가 하한을 받는다. "
    "리뷰어가 시뮬레이션으로 확인했고 우리도 재현했다 — microsoft(상장 · 측정 영업이익률 **+46.78%**)에 "
    "`bep_retreat` 만 `yes` 로 바꾸면 F9 가 **0 에서 -4 로** 떨어지고 경로에 `result: fail` 이 **양수 마진과 함께** "
    "기록된다. **새로 생긴 결함이 아니다** — 이 동작은 채점규칙 470행의 OR 조건 읽기와 어긋나지 않고 FIX-59 "
    "때부터 같다. 좁았던 것은 서술이다. 오늘 상장사 중 `bep_retreat: yes` 가 한 곳도 없어 점수 영향은 0 이다."
)


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []

    # 1) 우선순위 블록 — 제목을 넓히고 흑자 경우를 덧붙인다.
    prec = rules["policies"]["f9"]["g1_bep_retreat_precedence"]
    note = prec["also_precedes_loss_band"]
    old_head = "**손실률 밴드보다 앞선다.**"
    new_head = "**G1 통과와 손실률 밴드 둘 다보다 앞선다.**"
    if old_head in note:
        note = note.replace(old_head, new_head, 1)
    assert new_head in note, "우선순위 제목이 예상 밖"
    if WIDER not in note:
        note = note.rstrip() + " " + WIDER
    if note != prec["also_precedes_loss_band"]:
        prec["also_precedes_loss_band"] = note
        out.append("g1_bep_retreat_precedence.also_precedes_loss_band: 흑자 경우까지 범위를 넓힘")

    # 2) C-06 summary — 빌드 HTML 방법 표에 실린다. 짧게 넓힌다.
    c06 = find(rules["decisions"], "id", "C-06")
    s = c06["summary"]
    pairs = [
        ("BEP 후퇴가 손실률 밴드보다 앞서 `g1_bep_retreat_score` 를 준다",
         "BEP 후퇴가 **G1 통과·손실률 밴드 둘 다보다 앞서** `g1_bep_retreat_score` 를 준다"),
        ("**그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 "
         "다른 값이 나온다(TEN-RA6-01).",
         "**그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 "
         "다른 값이 나오고, **영업흑자여도 통과하지 못하고 하한을 받는다**(TEN-RA6-01)."),
    ]
    for old, new in pairs:
        if old in s:
            s = s.replace(old, new, 1)
    assert "G1 통과·손실률 밴드 둘 다보다 앞서" in s and "영업흑자여도 통과하지 못하고" in s, "C-06 문면이 예상 밖"
    if s != c06["summary"]:
        c06["summary"] = s
        out.append("decisions C-06.summary: 같음(HTML 방법 표에 실린다)")

    # 3) TEN-RA6-01 — 11월에 흑자 경우가 같이 판정되게 범위에 넣는다.
    t6 = find(rules["open_tensions"], "id", "TEN-RA6-01")
    scope = t6["also_covers_listed"]
    add = (
        f"**[{M}] 흑자 상장사도 이 범위다.** 앞 문장이 `측정된 영업손실률 밴드를 전망이 덮어쓴다` 로 적자 경우만 "
        "적었는데, `bep_retreat: yes` 는 **영업흑자 회사의 G1 통과까지 막는다**(microsoft 시뮬레이션에서 "
        "+46.78% 인데 F9 0 → -4). 11월에 470행과 별표 D 중 하나를 고를 때 **적자 경우만 보면 흑자 경우가 "
        "판정되지 않고 남는다** — 같은 조항이 만드는 같은 문제다."
    )
    if add not in scope:
        t6["also_covers_listed"] = scope.rstrip() + " " + add
        out.append("TEN-RA6-01.also_covers_listed: 흑자 경우를 11월 범위에 넣음")
    return out


RUN_ASSUMPTION = (
    f"[{M} · obsreg 9차 재무 계산 재판정 3회] **재무 계산 영역이 pass 로 왔고 네 영역이 모두 pass 다.** 리뷰어가 "
    "FIX-63 을 직접 다시 훑어 잔존 0건을 확인했고 재계산도 14개사 불일치 0 이다. 마지막 새 발견 low 하나를 이번에 "
    "닫는다 — **`bep_retreat` 가 미치는 범위를 문면이 실제보다 좁게 적었다.** 네 자리가 `손실률 밴드보다 앞선다` 로 "
    "적자 맥락만 서술했으나 실제로는 **영업흑자 회사의 G1 통과도 막는다**(microsoft +46.78% 에서 F9 0 → -4). "
    "동작은 470행 OR 조건대로이고 FIX-59 때부터 같아 **새 결함이 아니라 서술이 좁았던 것**이며, 코드는 손대지 않아 "
    "**점수가 한 칸도 바뀌지 않는다.** 넘기지 않고 고친 이유는 TEN-RA6-01 이 흑자 경우를 빠뜨린 채 11월에 판정될 "
    "위험을 리뷰어가 그대로 지적했기 때문이다."
)


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    if RUN_ASSUMPTION not in run["assumptions"]:
        run["assumptions"].append(RUN_ASSUMPTION)
        out.append("+ assumptions 네 영역 pass 와 마지막 발견 처리")
    return out


def main() -> int:
    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("규칙", rc), ("실행", runc)):
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
