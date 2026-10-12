# recheck 리뷰 결과(1차 다섯·확인 2·3차)를 review.md 양식에 채운다
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "output" / "ai-scorecard-2026-10-recheck"

REVIEWERS = """reviewers:
  - "fact-sources: fact-checker fs-a-recheck-20261012-r1 → needs_fix → 수정 → pass · fs-b-recheck-20261012-r1 → pass"
  - "financial-calc: general-purpose fc-recheck-20261012-r1 → needs_fix → 수정 → pass"
  - "rule-consistency: general-purpose rc-recheck-20261012-rule → needs_fix → 수정 → pass"
  - "output-readability: report-designer or-recheck-20261012-r1 → pass(빌드 전 문장 9곳 수정)"
  - "confirm: general-purpose confirm-r2 → blocked 1건(Microsoft ⑧ 고객 축) → 수정"
  - "confirm: general-purpose confirm-r3 → pass"
"""
AREAS = {
    "사실·출처": ("fact-checker ×2 (fs-a·fs-b-recheck-20261012-r1) + 확인 general-purpose (confirm-r2·r3)", "pass",
              "14사 판단 98건의 올릴·내릴 근거 921줄과 그 줄이 가리키는 근거 640건을 전수로 원문과 대조해 발췌를 모두 찾았다. 이어받은 제목뿐 근거 30건은 "
              "원문 발췌로 바뀌었고, 판정 칸의 '제목만' 사유는 0건이다. 1차 needs_fix(Alphabet ⑧ 약정 범위, Microsoft ⑦·⑧ 의 OpenAI 약정)는 회사 1차 발표와 "
              "공시를 근거로 등록해 고쳤고(EV-microsoft-045~048, EV-alphabet-075), Palantir ⑤ 의 프랑스·독일 문장은 원문 본문대로 고쳤다."),
    "재무 계산": ("general-purpose (fc-recheck-20261012-r1) + 확인 general-purpose (confirm-r2·r3)", "pass",
              "⑥ 상장 12사·비상장 P/S·⑨ 게이트·③ 성장률·⑧ 약정 배수를 원값으로 다시 계산해 맞았고, 엔진 재계산이 results_hash 를 그대로 낸다. Alibaba ⑥ −5 는 "
              "2026-10-09 종가로 PER 이 25배를 넘은 결과다. needs_fix 1건(⑧ 약정 분자 정의가 회사마다 다름)은 공유 정의대로 OpenAI −3(구속력 확인 몫 7.8~13.8배)·"
              "Alphabet −3(총액 2.02배)으로 맞췄다."),
    "규칙 일관성": ("general-purpose (rc-recheck-20261012-rule) + 확인 general-purpose (confirm-r2·r3, 사건 교차표·미확인 방향표·근거 등급표)", "pass",
                "98칸 판정 입력이 규칙 판정표와 맞고 모두 새 판단이다. 회사를 가로지르는 표 셋과 경쟁사 쌍 비교를 만들었다. 1차 Q03 fail(Microsoft ⑦ 이 회사 1차 "
                "발표인 OpenAI Azure $250B 를 빼고 작음)과 확인 2차 C1(Microsoft ⑧ 고객 축을 다른 판단에 없는 방식으로 폄)을 공유 문장대로 고쳐 Q02·Q03 이 "
                "pass 로 돌아왔다. ⑦·⑧ 의 OpenAI 계약 사용은 규칙 ⑦ 의 '서로 독립' 대로 다른 속성이다."),
    "출력·가독성": ("report-designer (or-recheck-20261012-r1) + 확인 general-purpose (confirm-r2·r3)", "pass",
                "초안 순위표·카드·요약 상자·요약 속 숫자를 results 와 스크립트로 대조해 어긋남 0 이고, 값을 바꾼 사본으로 검사가 값을 읽는지 확인했다. 트리거·판단·요약의 "
                "낡은 기준일·옛 점수·'제목 기준' 표현 10곳을 고쳤다. HTML 은 승인 뒤 빌드에서 확인한다."),
}
FINDINGS = """## 발견 사항

- 1차 리뷰 다섯(`review-parts/rule-consistency.md`, `fact-sources-a.md`, `fact-sources-b.md`, `financial-calc.md`, `output-readability.md`)의 needs_fix 는
  Microsoft ⑦(OpenAI Azure $250B), ⑧ 약정 분자 정의(OpenAI·Alphabet), Microsoft ⑧ 고객 축이었다. 수정 한 묶음(`.agents/plans/oct-recheck-2026-10/work/make_fix1.py`)
  뒤 확인 리뷰 2차(`confirm-r2.md`)가 Microsoft ⑧ 고객 축의 연환산 방식을 C1 으로 막았고, 공유 지표대로 고친 뒤(`make_fix2.py`) 확인 리뷰 3차(`confirm-r3.md`)가 pass 했다.
- 점수에 닿지 않는 발견과 다음 실행 과제는 각 리뷰 파일의 「다음 실행 과제」 절에 있다.

## 리뷰 경위

- 2026-10-12 1차 4영역 리뷰 다섯 세션. 사실·출처 A·B 는 사용량 한도로 중간에 끊겼다가 같은 세션을 이어서 끝냈다.
- 수정 한 묶음: 근거 3건 추가, 판단 8건(Microsoft ⑦ −2, OpenAI ⑧ −3, Alphabet ⑧ −3, Microsoft ⑧ 고객 축, 문장 4건), 트리거 9건, 기업 요약 6건.
- 확인 리뷰 2차 blocked 1건(C1) → 근거 2건 추가, Microsoft ⑧ −3, 문장·위치 결함 7건 수정, 기업 요약 3건.
- 확인 리뷰 3차 pass. 승인자가 알아야 할 민감도: ⑧ 의 '몇 배(−3)'와 '1배 안팎(−2)'을 가르는 2배 경계는 판단 문장이 좁힌 해석이고 rules.md 에 없다
  (Alphabet 2.02배·Meta 2.75배가 이 경계로 −3). Microsoft ⑧ 고객 축 34~37% 는 기간 미공시 계약을 보수적으로 편 값이라 하한이 아니다.
"""


def main() -> int:
    p = RUN / "review.md"
    t = p.read_text(encoding="utf-8")
    t = t.replace("status: needs_fix", "status: pass", 1)
    t = re.sub(r"reviewers:\n(?:  - .*\n)+", REVIEWERS, t, count=1)
    for area, (who, res, summary) in AREAS.items():
        t, n = re.subn(rf"^\| {re.escape(area)} \| ([^|]+) \|  \| pending \|  \|$", rf"| {area} | \1 | {who} | {res} | {summary} |", t, flags=re.M)
        if n != 1:
            raise SystemExit(f"영역 행을 못 찾음: {area}")
    rows = {m.group(1): m.group(0) for m in re.finditer(r"^\| (Q\d\d) \|.*$", (RUN / "review-parts" / "confirm-r3.md").read_text(encoding="utf-8"), re.M)}
    for qid, row in rows.items():
        t, n = re.subn(rf"^\| {qid} \|.*\| pending \|  \|$", row, t, flags=re.M)
        if n != 1:
            raise SystemExit(f"체크리스트 행을 못 찾음: {qid}")
    t = t.replace("## 발견 사항\n\n- (파일·섹션 단위로 기록)\n", FINDINGS, 1)
    if "pending" in t:
        raise SystemExit("pending 이 남았다")
    p.write_text(t, encoding="utf-8", newline="\n")
    print("review.md 채움")
    return 0


if __name__ == "__main__":
    sys.exit(main())
