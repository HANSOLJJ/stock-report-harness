# 원문 연결 확인 리뷰 지시서 (2026-10-07, round 9)

1차 리뷰(round 8, `REVIEW-INSTRUCTIONS.md`) 뒤 수정 한 묶음이 needs_fix 를 닫았는지, 수정이 새 문제를 만들지 않았는지 본다. 한 번으로 끝난다. 원칙은 `REVIEW-INSTRUCTIONS.md` 와 같다.

리뷰 기준 해시: results_hash `cdbacbdb94c32012…`, draft_hash `c2919e6763a50814…`(`review.md` frontmatter 와 같은지 먼저 확인). 수정 커밋은 `git log -1 --stat` 의 "round 8 리뷰 발견을 한 묶음으로 고친다" 이고, 근거·제안 경위는 `proposals.json` 의 PRP-378~389 다.

## 수정 묶음

1. 판단(PRP-378~387, 에이전트 반영)
   - **spacex-xai.F7**: ⑦ 가로축 '작음 → 큼'(연간 약정 ÷ 최근 1년 매출: Anthropic 연 약 $15B ÷ $23.0B ≈ 65%). ⑦ 0 → −2, 총점 9 → 7, 순위 6위 → 9위. 내릴 근거에 10-Q 고객 집중(EV-spacex-xai-060). **이번 실행의 유일한 점수 변화다.**
   - spacex-xai.F8: 고객 집중(고객 A 18.3%, 고객 B 19.5%)을 내릴 근거에 더하고 −3 유지.
   - palantir.F8: ICE 이탈 가능성 줄을 빼고 속성 분리 문장(⑤ 에서만)으로.
   - amazon.F2: Trainium3 수치의 주체(144칩 서버 합계), 성능 도약 근거를 실측(Anthropic 의 Trainium2 학습)으로, OpenAI 학습 공개 근거 없음은 내릴 근거로.
   - amazon.F7: 'Anthropic 매출 미미' 를 판정 칸 미확인으로, 가로축 판단(연간 약정 ÷ 최근 1년 매출)을 판정 칸에.
   - oracle.F2: 10-K '고객이 고른 LLM'(EV-oracle-035)으로 내릴 근거.
   - oracle.F9: 게이트 4 문장을 $322.15B·2.06배로(EV-oracle-036).
   - nvidia.F7: '$40B 약정', 라운드 세부·자기모순 해석을 판정 칸으로.
   - spacex-xai.F2: 표지에서 EV-spacex-xai-009 를 뺐다.
   - anthropic.F6: Q2 매출 전망치 표기, 미확인 대상을 누적 조달로 좁혔다.
2. 기업 요약(PRP-388·389): apple(8위, 25억 대 넘는 설치기반), spacex-xai(총점 7·함정 −11·9위·⑦ 이유).
3. 근거: 새 3건(EV-spacex-xai-060·EV-oracle-035·036, 공시 원문에서 기계로 발췌), EV-oracle-003·004·007 의 커버리지 2.06배, EV-nvidia-012 의 비중, Oracle 10-Q 근거 발행일 2026-09-11.
4. 관측: `oracle.offbalance_B.link26` 구매 약정 성분을 10-Q 2026-08-31 $34.15B 로(합계 $322.15B, 기준일 섞임 없음).
5. 트리거: TRG-020·022·033·041·065·079 의 옛 값·옛 판정.
6. 렌더: `.cite` 표지의 nowrap 을 ID 링크에만(조율자가 320·1280px 에서 근거 ID 759개 잘림 0·겹침 0 을 쟀다).

## 영역별로 볼 것

- **사실·출처** (세션 하나, `review-parts/fact-sources.md`): 1차 세 묶음 파일(`fact-sources-a·b·c.md`)의 needs_fix 4건이 닫혔는지, 새 근거 3건의 발췌가 원문 그 자리에 있는지, 수정한 줄이 원문과 맞는지. 그리고 세 묶음 파일의 결과를 `fact-sources.md` 하나로 합친다(세 파일의 범위·수치·다음 실행 과제를 요약해 싣고 세 파일을 가리킨다. round 7 내용은 「이전 리뷰 기록」으로).
- **재무 계산** (`financial-calc.md`): needs_fix 5건이 닫혔는지, link26 과 G4 커버리지(엔진 값), SpaceX ⑦ 변경 뒤 총점·순위가 엔진 재계산과 같은지(메모리 재계산으로 results_hash 대조).
- **규칙 일관성** (`rule-consistency.md`): needs_fix 5건(N1~N5)이 닫혔는지. **N1 의 잣대(연간 약정 ÷ 최근 1년 매출)가 ⑦ 을 매긴 14개사 모두에 같은 결론을 주는지** 회사별로 표로 확인한다(Q03). 체크리스트 Q01~Q23 을 다시 채운다(round 8 표를 출발점으로).
- **출력·가독성** (`output-readability.md`): needs_fix 1건(표지 잘림)이 닫혔는지 메모리 렌더로 320·768·1280px 실측. 순위표·카드·요약의 SpaceX 9위·Apple 8위가 results 와 같은지. 금지어 0건.

메모리 렌더와 서버는 `REVIEW-INSTRUCTIONS.md` 와 같고 포트는 3962 를 쓴다.

## 출력

자기 영역 파일을 고친다. frontmatter `round: 9`, `reviewed_at: 2026-10-07`, 「검토자:」 줄 끝에 "· 원문 연결 뒤 · 확인 리뷰", `결과:`·`요약:`·`검토 기준:`(새 해시)을 새로 쓰고 round 8 내용은 「이전 리뷰 기록」으로 옮긴다. 1차 발견마다 닫힘·남음을 적는다. 마지막 답변에는 결과, needs_fix 발견, 다음 실행 과제 수만 짧게 적는다.
