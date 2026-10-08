# 전부 재판단 공통 지시서 (2026-10 v2.0 재실행)

정기 실행은 ①②③④⑤⑦⑧ 판단을 14개사 전부 그 실행의 근거로 다시 매긴다(`docs/scorecard/rules.md` 2.9절). 이 지시서는 항목 하나를 맡은 판단 세션이 공통으로 지키는 절차다. 항목별 판정 기준은 `F1-INSTRUCTIONS.md`·`F2-INSTRUCTIONS.md`·`F3-INSTRUCTIONS.md` 와 규칙 3·4절이다.

## 역할 분담

- 근거 수집·확정은 회사 묶음(A nvidia·tsmc·apple / B alphabet·amazon·microsoft / C meta·oracle·palantir / D anthropic·openai / E alibaba·tesla·spacex-xai)이 먼저 끝낸다. 판단 세션은 확정된 근거만 쓴다.
- 판단은 **항목별로 한 세션이 14개사 전부** 맡는다. 한 회사에 댄 잣대를 열네 회사에 똑같이 댄다(규칙 2.3, 체크리스트 Q03). 회사마다 다른 세션이 매기면 잣대가 갈린다.
- 판단자는 opus 세션이다. 조율자는 제안을 모아 반영하고 `research → calculate → draft → review` 를 돌린다.

## 절차

1. 실행 폴더 `output/<slug>/` 의 `judgments.json`(이어받은 옛 판단, 전부 `status: carried`), `evidence/evidence.json`(확정 근거), `observations.json`, `sources.json` 을 읽는다. 옛 판단은 참고일 뿐 출발점이 아니다. 네 질문·세 경로·세 기준을 **처음부터** 근거로 채운다.
2. 회사마다 판정 입력을 정하고 근거를 세 칸으로 쓴다(`docs/scorecard/guide.md` 5.6). 판정 칸에는 결론·저울질·미확인, 올릴 근거와 내릴 근거에는 그 사실 하나만 보면 점수가 오르는지 내리는지로 가른 문장. 올릴·내릴 근거의 줄마다 끝에 `[EV-…]` 표지(5.7). 표지가 가리키는 근거는 `confirmed` 이고 URL·본문 발췌·`locator` 가 있어야 한다.
3. 원문을 못 찾은 사실은 방향 칸에서 빼고 판정 칸에 "미확인"으로 둔다. 회사가 공시하지 않음을 확인한 것(`not_disclosed`)과 우리가 못 찾은 것(`unverified`)을 섞지 않는다. 미확인을 실패로 적지 않는다.
4. 숫자는 원문을 연 뒤 적는다. 다른 판단 문장의 숫자를 옮겨 적지 않는다(2026-10-07 Oracle ⑤ 교훈). 공시 원문은 `data/_sec/docs/` 캐시에 있고, 없으면 `scorecard_cli.py sec-get <SEC 주소>` 로 받는다.
5. 회사마다 파일 하나를 쓴다. **CLI(`propose`·`judge`)는 부르지 않는다** — 판단 세션 일곱이 동시에 부르면 실행 잠금이 충돌한다. 조율자가 `work/apply_judgments.py` 로 순서대로 `propose` → `proposal --accept` 한다.
   파일: `.agents/plans/rejudge-all-2026-11/work/judge/<F>-<company_id>.json`
   ```json
   {
     "changes": {"<판정 입력 키>": "값", …},
     "evidence_after": ["판정 칸 문장", …],
     "evidence_up_after": ["올릴 근거 문장 … [EV-…]", …],
     "evidence_down_after": ["내릴 근거 문장 … [EV-…]", …],
     "cite": ["EV-…", …],
     "reconfirm": ["EV-…", …],
     "reason": "제안 사유 한 문장"
   }
   ```
   `changes` 에는 점수 칸이 없다(④⑧ 만 `score`). ①은 lockin 입력 전부, ②는 paths 입력 전부(옛 판단이 score 라 키를 다 줘야 한다), ③은 criteria 입력 전부와 `acceleration_tier`·`acceleration_growth_rates`, ⑤는 `A`·`H`, ⑦은 `funding_dependent_share`·`own_money_returns`. `cite` 는 올릴·내릴 근거가 가리키는 확정 근거 ID 전부. 판정 입력이 지난 판단과 전부 같다면 `changes` 를 비우고 `reconfirm` 에 다시 읽은 근거 ID 를 적는다(그래도 세 칸 문장은 새로 쓴다). `evidence_up_after`·`evidence_down_after` 는 비어 있어도 된다(없음).
6. 열네 회사가 끝나면 마지막 답변에 회사별 입력 요약표(입력 값과 계산될 점수의 가늠), 미확인으로 남긴 것, 자료가 없어 `unknown` 으로 둔 칸, 같은 잣대를 대면서 어려웠던 경계 사례, 조율자가 더 확정해야 할 근거(후보 상태인데 꼭 필요한 것)를 적는다.

## 완결된 문장 (AGENTS.md 「금지·주의」)

판단 문장은 그 자체로 읽히는 현재 상태 문장이다. 규칙 버전 표기, 변경 표시, 작업 번호, 이전 판·다른 문장을 가리키는 표현("기준선 원문은", "지난 실행에서는")을 쓰지 않는다. 고칠 때는 문장 전체를 다시 쓴다. 검증기가 `v1.`·이모지·취소선·`superseded`·`FIX-` 류를 막는다.

## 재확인 기록

다시 읽었는데 판정 입력이 지난 판단과 같다면 그래도 새 판단이다(`status: new`, 검토일은 오늘). 다시 읽은 근거 ID 를 `reconfirmed` 에 적는다. "안 바뀌었으니 넘어간다"는 없다.

## 하지 않는 것

- 점수를 직접 적지 않는다. ①②③⑤⑦ 은 입력에서 계산되고 ④⑧ 만 점수 입력이다.
- 근거 후보(`candidate`)를 인용하지 않는다. 확정 전 근거가 필요하면 조율자에게 확정을 요청한다.
- 이해상충을 이유로 멈추거나 되묻지 않는다(AGENTS.md).
- 승인·빌드·`history.csv`·규칙 파일을 건드리지 않는다.
