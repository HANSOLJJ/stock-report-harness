# (2026-10 v2.1 첫 실행) 1차 리뷰 여섯과 확인 리뷰 1차의 결과를 review.md 양식에 채운다
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "output" / "ai-scorecard-2026-10-v21"
# 2026-10-13: 막혔던 원문을 다시 열어 판단을 고친 뒤 확인 리뷰 2차가 최종 판정이다.
CONFIRM = RUN / "review-parts" / "confirm-r3.md"   # 2026-10-13 Meta ③ 사용자 확정 뒤 확인 리뷰 3차

REVIEWERS = """reviewers:
  - "fact-sources: fact-checker fs-a-v21-20261013-r1 → pass · fs-b-v21-20261013-r1 → needs_fix 3건(⑦ 세로축) → 수정 → pass · evidence-editor ev-v21-20261013-r1 → pass"
  - "financial-calc: general-purpose(Sonnet) fc-v21-20261013-r1 → pass"
  - "rule-consistency: general-purpose(Opus high) rc-v21-20261013-rule → needs_fix 1건(Palantir ④) → 수정 → pass"
  - "output-readability: report-designer or-v21-20261013-r1 → pass(트리거 점수 문장·렌더러 설명 수정)"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r1 → pass"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r2 → 막혔던 원문 재열람 뒤 변경분 확인 → pass"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r3 → 승인 취소·Meta ③ 사용자 확정 뒤 변경분 확인"
"""

FINDINGS = """## 발견 사항

- 1차 리뷰 여섯(`review-parts/rule-consistency.md`, `fact-sources-a.md`, `fact-sources-b.md`, `financial-calc.md`, `output-readability.md`, `evidence-bullets.md`)의
  needs_fix 는 넷이었다. Palantir ④ AI 무관 몫(규칙 일관성 N1), ⑦ 세로축 Palantir·Alibaba·OpenAI(사실·출처 b 1~3). 수정 한 묶음
  (`.agents/plans/v21-first-run-2026-10/FIX-INSTRUCTIONS.md`, `work/judge-fix1/`) 뒤 확인 리뷰 1차(`confirm-r1.md`)가 pass 했다.
- 점수에 닿지 않는 발견과 다음 실행 과제는 각 리뷰 파일의 「다음 실행 과제」 절에 있다. 리포트에 보이는 표시 결함 셋(TRG-023 의 Oracle ⑦ 옛 점수,
  ② 변경을 못 따라온 TRG-091·097)도 거기에 있다.

## 리뷰 경위

- 2026-10-13 1차 리뷰 여섯 세션(규칙 일관성·판단 검증은 Opus high, 사실·출처·재무·근거 불릿·출력은 Sonnet). 사실·출처 a 는 사용량 한도로 늦어져 같은 세션을 이어서 끝냈다.
- 수정 한 묶음: 판단 19건(점수가 바뀐 칸은 Palantir ④ 2→4.5·⑦ 0→−1, Alibaba ⑦ 0→−1. 나머지는 문장·근거 정정), 새 근거 16건(원문 대조 뒤 확정),
  새 트리거 2건, 트리거·근거 문장 치환 76항목, 기업 요약 4건. 조정 총점은 Palantir 5→6.5(10위→8위), Alibaba 7→6(8위→9위)이고 Tesla 는 9위→10위다.
- 사용자 지시(2026-10-13): CNBC 'Microsoft will mainly use its Maia chips for AI inference'(2026-10-12)를 추적한다. CNBC 본문은 접근 거부라 1차 발표인
  Microsoft 공식 블로그(2026-10-12)를 원문으로 근거 4건(EV-microsoft-070~073)과 트리거 TRG-121(Microsoft ④⑧)·TRG-122(NVIDIA ①⑧)를 두었다.
  2027년 다기가와트·주력 추론은 계획이라 점수에 넣지 않았다.
- Apple ④ 는 모델 칸의 유료 한도 확대가 계획이라 판매 칸이 없어 비교 그룹이 없다. 이 경우를 받도록 검증기·렌더러를 고쳤다(커밋 59d59e3).
- ② 는 정보 마감 당일 Artificial Analysis 의 Muse Wonder 평가를 2026-10-08 순위표에 더해 14개사를 같은 시점으로 비교한다(점수 불변).
- 경계 사례: Oracle ⑦ 의 TikTok 합작 연결은 추론으로 선 '돌아옴'(무거운 쪽)이다. 돌아오지 않음으로 읽으면 Oracle 은 −3→−2, 조정 8.5(7위)다.
- 사용자 결정(2026-10-13): 스크립트 요청이 403 이면 실제 브라우저로 다시 열고, 거기서도 막히면 우회하지 않는다(AGENTS.md 「원자료 조사 규율」). 이 규칙 이전에
  스크립트만 막혀 2차 기사로 대신했던 원문 아홉 건을 다시 열었다(`.agents/plans/v21-first-run-2026-10/work/reopen1/report.md`). 사용자가 USA TODAY 소장 PDF 와
  Seeking Alpha 본문을 직접 줬다. 원문 근거 12건을 확정하고 판단 9건의 문장·근거 표지와 근거 메모 16건을 고쳤다. 점수·순위는 바뀌지 않았다.
  확인 리뷰 2차(`confirm-r2.md`)가 이 변경분을 봤다.
- 2026-10-13 사용자가 승인한 뒤 승인을 취소하고, 승인 페이지에서 Meta ③ 의 후발 가속도를 unknown 에서 fail 로 직접 고쳤다(지표 단계 e, 사유 "일단 2점 확정 후 보기 위함").
  판정 칸 문장·기업 요약 12건·트리거와 근거의 옛 서술 6곳을 맞췄고, Meta 가 13점으로 Alphabet·Amazon 과 공동 1위가 되어 14개사가 모두 순위에 들었다.
  지표가 없는 회사의 가속도 처리는 TODO.md 「나-4」에서 규칙 문장으로 정한다. 확인 리뷰 3차(`confirm-r3.md`)가 이 변경분을 봤다.
"""


def main() -> int:
    p = RUN / "review.md"
    t = p.read_text(encoding="utf-8")
    c = CONFIRM.read_text(encoding="utf-8")
    if "\n결과: pass\n" not in c:
        raise SystemExit("확인 리뷰가 pass 가 아니다")
    t = t.replace("status: needs_fix", "status: pass", 1)
    t = re.sub(r"reviewers:\n(?:  - .*\n)+", REVIEWERS, t, count=1)
    area_block = c.split("## 검토 영역 표에 넣을 줄", 1)[1].split("\n## ", 1)[0]
    for m in re.finditer(r"^\| (사실·출처|재무 계산|규칙 일관성|출력·가독성) \| ([^|]+) \| (pass) \| (.+) \|$", area_block, re.M):
        area, who, res, summary = (g.strip() for g in m.groups())
        t, n = re.subn(rf"^\| {re.escape(area)} \| ([^|]+) \|  \| pending \|  \|$",
                       lambda mm: f"| {area} | {mm.group(1)} | {who} | {res} | {summary} |", t, flags=re.M)
        if n != 1:
            raise SystemExit(f"영역 행을 못 찾음: {area}")
    check_block = c.split("## 체크리스트", 1)[1].split("\n## ", 1)[0]
    rows = {m.group(1): (m.group(2).strip(), m.group(3).strip())
            for m in re.finditer(r"^\| (Q\d\d) \| (pass|fail|not_applicable) \| (.+) \|$", check_block, re.M)}
    if len(rows) != 23:
        raise SystemExit(f"체크리스트 행이 23개가 아니다({len(rows)})")
    for qid, (res, why) in rows.items():
        t, n = re.subn(rf"^\| {qid} \| ([^|]+) \| pending \|  \|$", lambda mm: f"| {qid} | {mm.group(1)} | {res} | {why} |", t, flags=re.M)
        if n != 1:
            raise SystemExit(f"체크리스트 행을 못 찾음: {qid}")
    t = t.replace("## 발견 사항\n\n- (파일·섹션 단위로 기록)\n", FINDINGS, 1)
    if "pending" in t:
        raise SystemExit("pending 이 남았다")
    p.write_text(t, encoding="utf-8", newline="\n")
    print("review.md 채움")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
