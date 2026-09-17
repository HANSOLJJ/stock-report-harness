# FIX-63: FIX-61·62 가 남긴 규칙 자기모순 둘과 낡은 문면 셋 정리 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- 9차 재판정 2회 `review-obsreg 6878e79:reviews/_parts/ai-scorecard-2026-09-obsreg/financial-calc.md`
- 직전 판정문 같은 폴더 `financial-calc-r9-prev.md`

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
M = "FIX-63"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 C-06 자기모순

# 이 문자열은 render_html.render_method 가 방법 표에 그대로 찍는다 — 짧고 정확해야 한다.
C06_SUMMARY = (
    "손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. "
    f"[{M} 정정 · obsreg 9차 재무 계산 재판정 2회(Claude 독립 세션) medium] "
    "**BEP 후퇴의 우선순위는 미결이 아니다.** 사용자 결정 2026-09-17(C-29)로 "
    "`policies.f9.g1_bep_retreat_precedence` 에 명문화했다 — **C-20 비상장 경로가 먼저 서고**, "
    "상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 손실률 밴드보다 앞서 "
    "`g1_bep_retreat_score` 를 준다. 점수도 -5 가 아니라 **-4** 다(C-06 재척도). "
    "**그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 "
    "다른 값이 나온다(TEN-RA6-01). 남은 미결은 FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다"
)

# ------------------------------------------------------------------ S2 틀린 닫음

ALSO_PRECEDES = (
    f"[FIX-61 · obsreg 9차 재무 계산 재판정 medium → {M} 정정 · 같은 세션의 재판정 2회 medium] "
    "**손실률 밴드보다 앞선다.** C-20 비상장 경로 다음 자리에서는 `bep_retreat` 를 손실률 밴드보다 "
    "먼저 본다(C-20 자체보다는 뒤로 밀렸다 — C-29). `margin` 값이 있어도 BEP 후퇴가 기록되면 밴드를 "
    "고르지 않는다. "
    "**~~다만 두 경로가 만나도 결과는 같다 — 순서가 관측되지 않는다.~~ 이 닫음은 틀렸다.** "
    "`calc_f9.compute_f9` 의 `if bep_retreat:` 가 밴드를 **아예 보지 않고 단락시키므로**, 손실률이 "
    "최심 밴드가 아니면 두 순서의 결과가 다르다. 리뷰어가 시뮬레이션으로 확인했고 우리도 재현했다 — "
    "spacex-xai(상장 · 측정 영업손실률 -16.1951% · 밴드 -3)에 `bep_retreat` 만 `yes` 로 바꾸면 F9 가 "
    "**-3 에서 -4 로 내려간다**(경로 기록도 `band: proposed_v15_boundaries` 에서 `band: BEP 후퇴 → -4` 로 "
    "바뀐다). 앞 주장이 성립하는 것은 손실률이 이미 -30% 초과일 때뿐이다. "
    "**이번 실행에는 해당 기업이 없다** — 상장사 중 `bep_retreat: yes` 가 한 곳도 없어 점수 영향이 0 이다. "
    "**틀린 닫음은 안 적은 것보다 나쁘다.** 이 순서가 옳은지, 곧 전망이 측정된 손실률을 덮어써도 되는지는 "
    "**TEN-RA6-01 이 같은 질문으로 다룬다**(아래 `why_no_new_pending_decision`)."
)

WHY_NO_NEW_PENDING = (
    f"[{M}] **새 미결로 등재하지 않는다.** 재판정 2회가 `이 자리를 미결로 등재할지 판단하라` 고 했고 "
    "등재하지 않는 쪽으로 판단했다. 이유 셋이다. "
    "① **순서 자체는 미정이 아니다** — 채점규칙 470행이 `손실률 -30% 초과 **또는** BEP 목표가 후퇴` 로 "
    "OR 조건을 적고 코드가 그대로 구현한다. 미결은 정해지지 않은 것에 다는 표시이지 정해진 것이 마음에 "
    "들지 않을 때 다는 표시가 아니다. "
    "② **진짜 질문은 이미 등록돼 있다** — `전망(BEP 목표 후퇴)이 측정된 실적(영업손실률)을 덮어써도 "
    "되는가` 는 470행 대 별표 D 388~390행 충돌과 **같은 질문**이고 그것이 TEN-RA6-01 이다. "
    "③ **갈라 두면 11월에 따로 판정될 위험이 있다** — 같은 충돌을 미결 하나와 긴장 하나로 나누면 한쪽만 "
    "닫히고 다른 쪽이 남는다. 대신 TEN-RA6-01 의 범위에 **상장사 자리**를 명시해 넣었다."
)

# ------------------------------------------------------------------ S3 재배열 범위

C29_WHAT_CHANGED = (
    "calc_f9.compute_f9 의 G1 갈림 — C-20 탐지를 `bep_retreat` 보다 앞에 둔다. "
    f"**[{M} 보강 · 9차 재판정 2회 low] 재배열이 문서보다 한 칸 더 갔다.** 옛 코드는 "
    "`reviewed_sign == \"profit\"` 을 C-20 보다 먼저 봤는데 새 코드는 C-20 을 **그것보다도 앞**에 둔다. "
    "비상장이고 영업손익이 구조적 미공시이면서 `operating_result_reviewed: profit` 인 회사가 옛 코드는 "
    "G1 통과, 새 코드는 C-20 판정 보류로 갈린다. **이 순서가 맞다** — C-20 자신이 `단일 분기 영업흑자를 "
    "G1 통과 근거로 쓰지 않는다` 고 적고, 그런 회사는 TTM 영업손익이 `not_disclosed_confirmed` 라 "
    "`profit` 이라는 부호가 TTM 밖에서 왔을 수밖에 없다. 코드는 그대로 두고 문면을 맞췄다. "
    "이번 실행에 해당 기업은 없다(anthropic `unknown` · openai `loss`). "
    "**바뀐 것이 옳아도 안 적힌 것은 안 적힌 것이다.**"
)

# ------------------------------------------------------------------ S1 전수에서 더 찾은 것

C07_ROUTE_OPENAI = (
    "~~**G4 에 아예 닿지 않는다.** G1 에서 BEP 후퇴로 실패해 하한 -4 에 걸리고 G3·G4 가 skipped 된다.~~ "
    f"**[{M} 정정 2026-09-17] C-29 뒤로 anthropic 과 같은 경로다** — C-20 판정 보류 → G2 비상장 FCF "
    "확인된 미공시 -2 → G3 생략 → G4 `incompatible`(G2 에서 이미 깎아 추가 감점 없음). F9 는 ok **-2** 다. "
    "옛 문면은 `verdict: already_implemented` 를 적은 2026-09-12 기준 기록이었다. "
    "**C-07 의 판정 자체는 바뀌지 않는다** — openai 가 이제 G4 에 닿아도 `coverage_comparable=no` 라 "
    "숫자를 읽기 전에 빠지고, 두 겹 차단은 anthropic 과 똑같이 선다."
)

# TEN-RA5-02 는 해소된 긴장이라 본문이 **당시 상황 기술**이다. 현재형이 오해를 부르므로 시제만 밝힌다.
RA5_02_TENSION_PREFIX = "[해소 전 기술 · 2026-09-17 C-29 로 뒤집히기 전의 현행 동작을 적은 것이다] "
RA5_02_WHY_CARRIED = (
    "[해소 전 기술] 승계 판단이지만 **이번 실행이 이 자리의 잣대를 문면으로 확정했다**"
    "(policies.f9.g1_bep_retreat_precedence 신설). 그래서 예외로 넘기지 않고 정식 긴장으로 뒀다. "
    f"[{M}] 그 확정은 같은 날 C-29 로 뒤집혔고 이 긴장은 해소됐다 — 남은 충돌은 TEN-RA6-01 이 잇는다."
)

RA6_01_LISTED_SCOPE = (
    f"[{M} · 9차 재판정 2회 medium] **상장사 자리까지 이 긴장의 범위다.** C-29 는 비상장·구조적 미공시 "
    "경로만 뒤집었고, **상장사에 `bep_retreat: yes` 가 들어오면 측정된 영업손실률 밴드를 전망이 "
    "덮어쓰는 경로가 그대로 남아 있다.** 순서가 결과를 가른다는 것도 확인됐다 — spacex-xai 로 "
    "시뮬레이션하면 밴드 -3 이 BEP -4 로 바뀐다(`g1_bep_retreat_precedence.also_precedes_loss_band`). "
    "**오늘 그런 회사가 없어 점수 영향은 0 이다.** 11월에 470행과 별표 D 중 하나를 고를 때 비상장 경로만 "
    "보지 말고 이 자리도 같이 판정해야 한다 — 같은 충돌이고 따로 닫으면 한쪽이 남는다."
)

RUN_ASSUMPTION = (
    f"[{M} · obsreg 9차 재무 계산 재판정 2회] **Q11 이 pass 로 바뀌었다**(리뷰어 재판정 — C-28·C-29 반영을 "
    "합성 관측과 시뮬레이션으로 재현해 확인했고 재계산도 14개사 불일치 0). 영역은 여전히 `needs_fix` 이고 "
    "사유는 **FIX-61·FIX-62 가 9차 지적을 고치면서 남긴 새 모순 둘**이다. 이번 반영으로 닫는다 — "
    "① C-06 `summary` 가 뒤집힌 우선순위를 반대로 적어 규칙이 스스로 모순됐다(빌드 HTML 방법 표에 실린다). "
    "② `also_precedes_loss_band` 의 `순서가 관측되지 않는다` 가 **사실이 아니다** — 손실률이 최심 밴드가 "
    "아니면 순서가 결과를 가른다(spacex-xai 로 재현). **점수는 한 칸도 닿지 않는다.** "
    "전수로 훑어 같은 계열을 둘 더 고쳤다(C-07 `routes.openai` · `render_common.method_lines`)."
)


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    decisions = rules["decisions"]

    c06 = find(decisions, "id", "C-06")
    assert "C-20 비상장 경로보다 앞서" in c06["summary"] or c06["summary"] == C06_SUMMARY, "C-06 문면이 예상 밖"
    if c06["summary"] != C06_SUMMARY:
        c06["summary"] = C06_SUMMARY
        out.append("decisions C-06.summary: 뒤집힌 우선순위를 현재 사실로 (S1)")
    assert c06["status"] == "pending", "C-06 의 나머지 미결은 그대로여야 한다"

    prec = rules["policies"]["f9"]["g1_bep_retreat_precedence"]
    if prec.get("also_precedes_loss_band") != ALSO_PRECEDES:
        prec["also_precedes_loss_band"] = ALSO_PRECEDES
        out.append("g1_bep_retreat_precedence.also_precedes_loss_band: 틀린 닫음 정정 (S2)")
    if prec.get("why_no_new_pending_decision") != WHY_NO_NEW_PENDING:
        prec["why_no_new_pending_decision"] = WHY_NO_NEW_PENDING
        out.append("+ g1_bep_retreat_precedence.why_no_new_pending_decision: 미결 등재 판단 (S2)")

    c29 = find(decisions, "id", "C-29")
    if c29["scope"]["what_changed"] != C29_WHAT_CHANGED:
        c29["scope"]["what_changed"] = C29_WHAT_CHANGED
        out.append("decisions C-29.scope.what_changed: reviewed_sign 보다도 앞선다는 사실 (S3)")

    c07 = find(decisions, "id", "C-07")
    if c07["implementation_status"]["routes"]["openai"] != C07_ROUTE_OPENAI:
        c07["implementation_status"]["routes"]["openai"] = C07_ROUTE_OPENAI
        out.append("decisions C-07.implementation_status.routes.openai: 낡은 경로 정정 (전수 조사)")

    t5 = find(rules["open_tensions"], "id", "TEN-RA5-02")
    if not t5["tension"].startswith(RA5_02_TENSION_PREFIX):
        t5["tension"] = RA5_02_TENSION_PREFIX + t5["tension"]
        out.append("TEN-RA5-02.tension: 해소 전 기술임을 밝힘 (전수 조사)")
    if t5["why_carried_exception"] != RA5_02_WHY_CARRIED:
        t5["why_carried_exception"] = RA5_02_WHY_CARRIED
        out.append("TEN-RA5-02.why_carried_exception: 같음")

    t6 = find(rules["open_tensions"], "id", "TEN-RA6-01")
    if t6.get("also_covers_listed") != RA6_01_LISTED_SCOPE:
        t6["also_covers_listed"] = RA6_01_LISTED_SCOPE
        out.append("+ TEN-RA6-01.also_covers_listed: 상장사 자리까지 범위 확대 (S2)")
    return out


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    if RUN_ASSUMPTION not in run["assumptions"]:
        run["assumptions"].append(RUN_ASSUMPTION)
        out.append("+ assumptions Q11 전환과 이번 반영의 사유")
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
