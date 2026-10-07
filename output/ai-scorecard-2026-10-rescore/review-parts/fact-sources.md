---
reviewer_agent: fact-checker
session: fc-opus55-20261007-rescore-r6 (근거 세 칸을 나눈 세션·서브에이전트와 다른 세션)
reviewed_at: 2026-10-07
round: 6
---
# fact-sources — 사실·출처
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션(이 실행을 만든 세션 아님, evidence-editor 관점 포함) · 2026-10-07 · 근거 세 칸 재분류 뒤
결과: needs_fix
요약: 판단 114개를 모두 읽었다. 이전 문장(`revision_history[-1].previous.evidence`)과 세 칸 문장을 나란히 놓고 대조했다. 세 칸 합이 담은 사실은 이전 문장과 같다. 숫자·영문 토큰 차이는 두 방향 모두 0건이다. 한글 어절 차이는 어미·조사·주어 보충뿐이다. 새로 생긴 사실과 빠진 사실은 찾지 못했다. 점수·순위·factor 점수·기업 요약은 round 5 와 같다. 사실을 바꾼 수정은 없고, needs_fix 는 1건이다. alphabet.F5 내릴 근거 첫 줄이 "직원 600명 이상의 반발은 시장의 적대가 아니다" 라는 결론 문장이라, 그 칸이 말하려는 방향과 반대로 읽힌다. 서브에이전트 수정이 반발의 대상('이에' = 계약 갱신·기밀 계약·안전 설정 완화)을 '안전 설정 완화' 하나로 좁혔다. 사실을 내릴 근거에 두고 결론은 판정 칸으로 옮긴다. counter_evidence 를 비운 3건 가운데 tsmc·openai 는 버린 내용이 기준선 판정표 행 번호와 인용 위치 메모뿐이라 잃은 사실이 없다. anthropic 은 '세 회사에서 컴퓨트를 사는 것은 조달이라 동맹이 아니다' 라는 지금도 유효한 판정 논리가 함께 버려졌다(점수 영향 없음, 다음 실행 과제). 렌더러가 openai.F2 의 벤치마크 이름 'AA-LCR' 을 작업 메모로 오인해 draft·리포트에 'SciCode·A' 로 싣는다. round 5 에도 있던 결함이다(다음 실행 과제, 출력 영역과 함께 본다).

검토 기준: results_hash `07814146bc1e8401…`, draft_hash `9461bade7e987939…`(review.md frontmatter 와 같음을 확인). 비교 기준은 round 5 커밋 `f019b73`, 재분류 커밋 `336738c` 다. 스크립트는 스크래치 `review6/dump.py`·`review6/tokdiff.py` 다.

## 확인 내용

- **바뀐 범위**: `f019b73` 뒤로 입력 가운데 judgments.json 만 바뀌었다. observations·sources·evidence·triggers 해시는 round 5 와 같다. results.json 은 judgments 해시와 results_hash 두 줄만 바뀌었다. draft 의 표·기업 머리줄·요약 377줄은 round 5 와 한 글자도 다르지 않다. 그래서 출처 URL·excerpt·SEC 원문 대조·기준일·트리거 carry 표는 round 1~5 의 확인이 그대로 유효하다. 이번에는 sec-get 을 쓰지 않았다.
- **판단 칸**: 114개 모두 `evidence`·`evidence_up`·`evidence_down`·`revision_history` 가 바뀌었다. `counter_evidence` 는 3건만 바뀌었다. kind·score·inputs·status·reviewer·reviewed_at·source_ids 는 하나도 바뀌지 않았다. `revision_history[-1].previous` 의 evidence·점수·판정 재료는 114개 모두 round 5 판단과 같다. 수정 경로는 제안 PRP-148~258(111건, accepted)과 judge 3건(tsmc.F5.strict54·anthropic.F5.impl48·openai.F5.impl48)이다. company_summaries 는 바뀌지 않았다.
- **사실 보존(기계)**: 세 칸 문장은 828개다. 이 가운데 385개는 이전 문장을 그대로 옮겼고, 443개는 나누거나 고친 문장이다. 숫자·금액·영문 토큰을 판단마다 이전 문장과 대조했다. 빠진 토큰과 새 토큰이 모두 0건이다. 한글 어절 차이 254줄은 모두 어미(‘~라’→‘~다’), 접속어(다만·그러나·반면) 삭제, 주어 보충('마이크로소프트는', 'TSMC 의 사업은')이다. 칸 사이 중복 0, 빈 판정 칸 0, 두 방향 칸이 함께 빈 판단 0, 남은 counter_evidence 0 이다.
- **사실 보존(전수 읽기)**: 114개 판단의 이전 문장, 세 칸 문장, 서브에이전트 `edits` 를 모두 읽었다. 뜻이 바뀐 수정은 두 곳이다. alphabet.F5 의 '이에 반발한' → '구글의 안전 설정 완화에 반발한' 은 반발 대상을 좁혔다(발견 1). palantir.F5 의 '실제 이탈은' → '구조형 적대로 인한 실제 이탈은' 은 원문에 없던 인과를 붙였다(low). 이 밖의 수정은 뜻이 같다. 예를 들어 alphabet.F7 '그 매출은' → 'Anthropic 에서 오는 매출은', openai.F2 '2~3점' → '2~3포인트', tsmc.F5 '미 정부가 10% 지분을 가진 Intel Foundry' → '미 정부가 Intel Foundry 의 10% 지분을 가지고 있다' 가 그렇다.
- **품질 단서**: 방향 칸으로 간 보도·벤더 발표·계획 문장은 약점 단서를 같은 줄에 그대로 갖고 있다. 예를 들어 nvidia.F2 Vera Rubin 은 '벤더 발표이고 독립 측정이 아니다', openai.F4 Jalapeño 는 '이해당사자인 OpenAI 의 발표', tesla.F4 13.7GWh 는 '공시 본문과 대조하지 않은 보도 제목 값', anthropic.F4 자체 칩은 '지금은 계획 단계다', nvidia.F3 전년 대비 성장률은 '(추론)' 을 달고 있다.
- **counter_evidence 3건**: tsmc.F5 에서 버린 것은 기준선 판정표 218행(A +2, 4점)과 '고객에 투자 안 함' 인용 행 번호(243행) 메모다. 'NVIDIA 경쟁 칩이 TSMC 공정에 들어와 있다' 와 'TSMC 는 고객에 투자하지 않는다' 는 각각 올릴 근거·내릴 근거에 이미 있다. openai.F5 에서 버린 것은 판정표 224행·276행 메모다. 'Oracle $300B·Amazon $50B·SoftBank·DoD' 는 판정 칸 둘째 줄에 있다. anthropic.F5 에서 버린 것은 판정표 214행 메모와 'Amazon 5GW + Google 5GW TPU + MS 1GW 는 사는 쪽의 컴퓨트 확보라 조달 ≠ 동맹에 걸리고 ⑧ 에서 센다' 다. 뒤의 것은 지금도 유효한 판정 논리인데 세 칸 어디에도 없다. 판정 칸은 '투자를 빼면 … 유통 하나가 남는다' 고만 적는다. A=+1 은 유통만으로 서므로 점수에는 닿지 않는다(다음 실행 과제 2). 'MS 1GW' 는 지금 판단 문장 어디에도 없는 옛 근거 숫자라 되살리지 않아도 된다.
- **참조 무결성**: 관측 525·판단 186·근거 72·트리거 187 참조가 모두 출처 210건 안에 있다. 빠진 참조는 0건이다.
- **draft 반영**: 세 칸 문장 828개 가운데 810개가 draft 에 글자 그대로 있다. 나머지 18개는 셋으로 갈린다. 첫째, anthropic.F6·openai.F6(16개)는 자동 산출 factor 라 판단이 카드에 연결되지 않는다. round 5 에도 이 판단 문장은 draft 에 없었다. 둘째, alibaba.F7 의 'P4' 는 이름 바꾸기로 '입력 신뢰도' 가 됐다. 셋째, openai.F2 내릴 근거의 'AA-LCR' 은 `render_common.split_worknote` 가 'A-LCR' 을 작업 메모로 떼어 'SciCode·A 이 2~3포인트' 로 실린다(draft 1542행). 마지막 결함은 round 5 draft 981행에도 있었다. 판단 문장 전체에서 split_worknote 에 걸리는 줄은 이 한 줄뿐이다.
- **금지 표현**: 새로 생긴 문장이 없고, 고친 문장에 매수·매도·목표주가·수익 보장 표현은 0건이다.

## 발견
| 등급 | 위치 | 발견 | 고칠 방향 | 점수 영향 |
| --- | --- | --- | --- | --- |
| needs_fix | judgments.json alphabet.F5 · evidence_down[0] "구글의 안전 설정 완화에 반발한 직원 600명 이상의 움직임은 내부 갈등이지 시장의 적대가 아니라고 판단했다." | 내릴 근거 칸에 결론 문장이 있다. 문장이 말하는 것은 '이 반발은 적대가 아니다', 곧 적대 등급을 깎지 않는 쪽이라 칸의 방향과 반대로 읽힌다. 서브에이전트 수정이 이전 문장의 '이에 반발한'(계약 갱신·$200M 기밀 계약·안전 설정 완화 셋)을 '안전 설정 완화에 반발한' 하나로 좁혔다. 원문에서 반발 대상을 가를 근거는 없다(기준선 원문도 '직원 600명+ 반발' 만 적는다). | 둘로 나눈다. 내릴 근거: "구글의 기밀 네트워크 사용 갱신·기밀 계약·안전 설정 완화에 직원 600명 이상이 반발했다." 판정 칸(적대 등급 문장 바로 뒤): "직원 반발은 내부 갈등이지 시장의 적대가 아니라고 판단했다." | 없음(H=−1 그대로) |
| low | judgments.json palantir.F5 · evidence_up[1] "구조형 적대로 인한 실제 이탈은 영국에서만 확인되고, …" | 수정이 '구조형 적대로 인한' 을 붙였다. 이전 문장은 '실제 이탈은 영국에서만 확인되고' 이고, 영국 경찰·NHS 이탈의 원인이 시민사회·의회의 적대라는 사실은 원문·근거에 없다. | '구조형 적대로 인한' 을 빼고 "실제 이탈은 영국에서만 확인되고, 최대 파트너인 미 정부와의 긴장은 보이지 않는다." 로 쓴다. | 없음 |
| low | judgments.json anthropic.F5.impl48 판정 칸 | counter_evidence 를 비우며 '세 회사에서 컴퓨트를 사는 것은 조달이라 동맹이 아니고 ⑧ 에서 센다' 는 판정 논리도 함께 버렸다. 판정 칸은 '투자를 빼면 세 회사와의 관계에는 유통 하나가 남는다' 고만 적어, 컴퓨트 구매 관계를 왜 세지 않는지 빠졌다. openai.F5 는 같은 잣대를 'Oracle 과의 $300B 컴퓨트 계약도 OpenAI 가 사는 쪽의 조달이라 동맹이 아니며' 로 적는다. | 판정 칸 둘째 줄 뒤에 "Anthropic 이 세 회사에서 컴퓨트를 사는 관계는 사는 쪽의 조달이라 동맹이 아니고, 그 의존은 ⑧ 에서 센다." 를 더한다. | 없음 |
| low | render_common.split_worknote · draft.md 1542행 · report.html | openai.F2 내릴 근거의 벤치마크 이름 'AA-LCR' 에서 'A-LCR' 을 작업 메모로 떼어 'τ³-Banking·SciCode·A 이 2~3포인트 퇴행' 으로 싣는다. 판단 파일 문장은 맞다. round 5 draft 981행에도 같은 결함이 있었다. | 작업 메모 패턴이 영문 낱말 안의 'A-LCR' 을 잡지 않게 고친다. 테스트에 'AA-LCR' 문장을 넣는다(출력 영역과 함께 본다). | 없음 |

판정 칸·방향 칸 분류가 갈릴 수 있는 줄과 칸을 건너가는 지시어는 사실이 바뀐 것이 아니라 「다음 실행 과제」 3~5 에 적었다. round 5 의 low 둘(oracle.F5 의 10-Q·10-K $2.4B 묶음, oracle.F7·openai.F5 의 Stargate $7B 지분)은 문장이 칸만 옮겨 그대로 남는다(oracle.F5 evidence_down[1], oracle.F7 evidence_down[1], openai.F5 evidence_up[0]·판정 칸 셋째 줄).

## 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 이해당사자 발표를 방향 칸으로 옮길 때 '벤더 발표이고 독립 측정이 아니다'(nvidia.F2), '이해당사자인 OpenAI 의 발표'(openai.F4), '자사 어댑터 하네스 점수라 쓰지 않는다'(openai.F2) 같은 단서를 같은 줄에 남겼다. 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | 계획 문장은 방향 칸에 두되 '계획이라 점수에 넣지 않는다' 를 같은 줄에 남겼다(anthropic.F4·F8 자체 칩, apple.F4 Baltra, alibaba.F4 증자, oracle.F9 추가 조달, tesla.F4 Optimus·Terafab, meta.F4 기업용 AI). tesla.F2 는 점수 표기('0점') 때문에 그 문장을 판정 칸에 두었다. |
| Q14 | pass | 진행 중인 사건(Hugging Face 종결 전, Starship 시험 비행 성격, 로보택시 확장 과제, Gemini 4·GPT-6.1 Sol 독립 측정 없음)은 나눈 뒤에도 미완으로 적혀 있다. |
| Q23 | pass | 하네스가 표기되지 않은 벤치마크(meta.F2 Tau3-Bench, alibaba.F2 HLE, anthropic.F2 ARC-AGI-3 30.2%, openai.F2 FrontierMath)는 '비교 근거로 쓰지 않는다' 단서를 같은 줄에 남겼다. 하네스가 다른 수치를 비교 근거로 쓴 줄은 없다. |

## 다음 실행 과제
1. (low) palantir.F5 evidence_up[1] 에서 '구조형 적대로 인한' 을 뺀다.
2. (low) anthropic.F5.impl48 판정 칸에 '세 회사에서 컴퓨트를 사는 관계는 조달이라 동맹이 아니고 ⑧ 에서 센다' 를 더한다(openai.F5 와 같은 잣대).
3. (low, 규칙 일관성 영역과 함께) 판정 문장이 방향 칸에 있거나 한 줄에 두 방향이 섞인 줄이다. alibaba.F3 up[0] '모방 불가능성을 부분으로 본 것은 … 판단 때문이다' 는 판정 칸으로 옮긴다. openai.F3 down[0] '퍼스트무버 함정에 머물러 있다고 본다' 는 판정 칸으로 옮긴다. meta.F1 up[2] '새 AI 앱의 사용자 지표는 이 점수를 움직이지 않는다' 도 판정 칸으로 옮긴다. alphabet.F2 up[2] Gemini 3.8 Flash 는 '속도·가격 경쟁력'(올릴 근거)과 '프론티어 순위 불변'(내릴 근거)으로 나눈다. tsmc.F5 down[0] 은 '고객에 투자하지 않는다'(내릴 근거)와 '고객이 선급금으로 캐파를 댄다'(올릴 근거)로 나눈다. anthropic.F8 판정 칸 'FTC 가 계약의 배타성을 검토하고 있다' 는 사실이라 방향 칸으로 옮긴다. 이전 문장을 통째로 옮겨 '~라고 판정했다/판단했다' 가 붙은 방향 칸 줄도 사실과 결론으로 나눈다. alphabet.F1 up[1], amazon.F8 up[0], meta.F1 up[0], palantir.F1 down[1], palantir.F8 down[0], oracle.F8 down[1], nvidia.F7 down[1] 이 그렇다(모두 방향은 맞다).
4. (low, Q03) '흑자 전환 목표 후퇴와 완충 잠식은 없음' 이 anthropic.F9·spacex-xai.F9·tesla.F9 에서는 올릴 근거, alibaba.F9 에서는 판정 칸에 있다. 판정 재료(bep_retreat·buffer_erosion) 문장이라 네 회사 모두 판정 칸으로 맞춘다. anthropic.F9 는 입력이 `no` 인데 문장이 '확인되지 않았다' 라 미확인처럼 읽히므로 '없다' 로 고친다.
5. (low, 출력 영역과 함께) 칸이 갈리며 지시 대상이 다른 칸으로 간 줄이다. microsoft.F5 up[1] '같은 주'(기준 보도는 내릴 근거), palantir.F1 down[0] '그 전환비용은', alibaba.F1 down[0] '이 락인은'(대상은 올릴 근거), nvidia.F7 판정 '이 보증들은'(대상은 내릴 근거), nvidia.F8 판정 '이 헤지는'(대상은 올릴 근거), tesla.F5 판정 '이런 규제 적대는', spacex-xai.F5 판정 '이 적대들을'(대상은 내릴 근거)을 주어를 밝힌 문장으로 다시 쓴다.
6. (low) `split_worknote` 가 'AA-LCR' 을 깎지 않게 고친다(발견 4).
7. (low) round 5 과제 1~4 를 유지한다. oracle.F7·openai.F5 의 Oracle Stargate $7B 지분, oracle.F5 의 $2.4B 문서별 표기, nvidia.F3 의 2026-04-26 10-Q 등록과 판단 source_ids·evidence_ids, 3차 과제 2~6 이다.

## 이전 리뷰 기록

아래는 5차(좁은 확인)와 그 안에 옮겨 둔 1~4차 리뷰를 지우지 않고 옮긴 것이다.

5차 검토자: Claude Opus 5.5 · 완결된 문장 재작성 뒤 1차 · 확인 리뷰 · 좁은 확인 · 2026-10-07
5차 결과: pass
5차 요약: 확인 리뷰의 needs_fix 2건이 닫혔다. (1) Oracle ⑤ 는 동맹 등급 +1 로 되돌아갔다(PRP-142). 새 문장의 사실은 원문과 맞는다. 지분 동맹은 TikTok USDS 합작법인 15% 하나이고(10-Q p.7), 10-Q·10-K 에 Stargate 는 0건이며, 비시장성 지분·채무 투자 합계는 10-Q 에 $2.4B 로 적혀 있다. 원문에 없던 'TikTok 합작법인의 클라우드를 맡는다' 는 빠졌다. (2) 기업 요약 14개의 총점·과점·함정·순위·공동 여부를 results 와 다시 대조했다. 모두 맞고, 고친 여섯(Microsoft·Meta·Alibaba·OpenAI·Oracle·Tesla)의 서술 사실도 각 판단과 맞는다. OpenAI ④ 3점 문장(PRP-143)의 사실은 모두 이전 판단 문장에 있던 것이고, 자체 칩을 근거에서 뺀 이유를 판정 지침으로 적었다. EV-tesla-008 relevance 와 TRG-030 recheck 의 테슬라 ④ 는 3점으로 맞춰졌고, EV-oracle-008 의 '동맹 등급 +1' 은 이제 맞는 값이다. 점수·순위·체크리스트를 바꾸는 발견은 남지 않았다. 남은 것은 다음 실행 과제뿐이다. 그중 Oracle ⑦·OpenAI ⑤ 에 남은 'Oracle 의 Stargate $7B 지분' 서술은 점수에 닿지 않는다.

5차 검토 기준: results_hash `e279d193d30137ee…`, draft_hash `1bbf20715c81cc01…`(review.md frontmatter 와 같음을 확인).

### 5차 — 확인 내용

- **Oracle ⑤ (PRP-142, A=+1·H=−1, 3점)**: 'TikTok USDS Joint Venture LLC … ownership interest of 15 %' 와 'non-marketable equity securities and debt investments totaled $ 2.4 billion … as of August 31, 2026' 는 10-Q(f456b723…) p.7 원문과 같다. 'Stargate' 는 10-Q·10-K(3fc9afc2…) 모두 0건이다. 문장이 "같은 10-Q 와 2026 회계연도 10-K 에는 … 합계가 $2.4B" 로 두 문서를 묶어 적는데, 10-K 의 합계는 2026-05-31 기준 $2.3B 다(아래 low). evidence_ids 는 EV-oracle-003(10-Q, confirmed)이다.
- **OpenAI ④ (PRP-143, 3점)**: InferenceX 1.7배·1.5배, Broadcom 배치 계획 0.1GW 미만·1.3GW·5GW 이상, Stargate Abilene GPU 20.2만 개(B200·B300 각 10.1만, H100 환산 약 50.9만)는 이전 openai.F4 문장과 같다. 'ChatGPT 와 API 가 실제 배포 사업' 은 openai.F1 문장과 맞는다. 새로 생긴 사실은 없다.
- **기업 요약 14개**: 총점·과점·함정·순위·공동 여부가 results 와 모두 맞는다. 공동 1위 Alphabet·Amazon, 공동 3위 Microsoft·Meta(13), 5위 TSMC, 공동 6위 Anthropic·SpaceX·NVIDIA, 9위 Apple, 10위 Palantir, 11위 Alibaba(단독), 공동 12위 Oracle·Tesla(4), 14위 OpenAI(3)다. 고친 여섯의 서술 사실도 판단과 맞는다. Microsoft ⑨ 는 '설비투자 증가로 분기 FCF 감소·−1' 로 microsoft.F9 와 같고, Tesla ④ 3 의 '차량·에너지 저장·소규모 로보택시' 는 tesla.F4 와, OpenAI ④ 3 은 '자체 칩 출하 미확인' 으로 openai.F4 와 같다.
- **근거·트리거**: EV-tesla-008 relevance 는 "테슬라 ④ 판단은 3점(차량·에너지 저장·소규모 로보택시, 배치 전인 Optimus·Terafab 은 폭에서 뺐다)" 이고, TRG-030 recheck.what 은 "지금 3" 이다. OpenAI·Oracle·Tesla 근거·트리거에 옛 점수('④ 4점', '동맹 등급 +2')는 남아 있지 않다.

### 5차 — 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| 닫힘 | oracle.F5 (확인 리뷰 needs_fix 1) | A +2 → +1 로 되돌렸고, 문장이 원문으로 확인되는 지분 동맹(TikTok 15%) 하나만 적는다. | — |
| 닫힘 | company_summaries (확인 리뷰 needs_fix 2) | 14개 모두 새 results 와 맞는다. | — |
| low | judgments.json oracle.F5 | "같은 10-Q 와 2026 회계연도 10-K 에는 … 비시장성 지분·채무 투자 합계가 $2.4B" 라고 두 문서를 묶어 적는다. $2.4B 는 10-Q(2026-08-31) 값이고, 10-K(2026-05-31)는 $2.3B 다. 결론(지분 동맹 하나)은 같다. | 없음 |
| low | judgments.json oracle.F7.fix52 · openai.F5.impl48 | 'Oracle 이 Stargate LLC 에 $7B 를 지분 출자' 라는 서술이 남아 있다. Oracle 10-Q·10-K 로 확인되지 않는 사실이다(Oracle ⑤ 를 되돌린 이유와 같다). Oracle ⑦ 은 가로축 '큼' 이라 세로축과 무관하게 −2 이고, OpenAI ⑤ 는 Stargate 하나만 지분 동맹으로 세고 Broadcom·국방부로 +1 이라 점수는 바뀌지 않는다. | 없음 |

4차(확인 리뷰)의 medium(nvidia.F3 의 2026-04-26 10-Q 미등록, 판단 source_ids 연결)과 low(EV-oracle-008·EV-tesla-008 relevance — 이번에 닫힘, microsoft.F9 분기 선택)는 위와 「다음 실행 과제」로 정리했다.

### 5차 — 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | Oracle ⑤ 는 발행사 공시(10-Q·10-K)로 지분 동맹을 확인했고, OpenAI ④ 는 이해당사자 발표(InferenceX)를 근거에서 뺐다. 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | OpenAI ④ 는 Jalapeño 배치 계획을, Tesla ④ 는 Optimus·Terafab 을 계획·미배치로 보아 점수에서 뺐다. |
| Q14 | pass | 출하 전 칩·미배치 사업·확인되지 않은 지분을 끝난 사실로 세지 않는다. |
| Q23 | not_applicable | 이번 묶음에 벤치마크 비교가 없다. |

### 5차 — 다음 실행 과제
1. (low) oracle.F7·openai.F5 의 'Oracle Stargate $7B 지분' 서술을 1차 자료로 확인하거나, Oracle 공시에 없다는 사실로 고친다(Oracle ⑦ 세로축 근거 문장, OpenAI ⑤ 의 Stargate 공동 지분 구성).
2. (low) oracle.F5 의 비시장성 투자 합계를 '10-Q $2.4B(2026-08-31)·10-K $2.3B(2026-05-31)' 로 문서별로 적는다.
3. (medium) nvidia.F3 가 인용한 2026-04-26 분기 10-Q(0001045810-26-000052)를 sources.json 에 등록한다. 판단의 source_ids·evidence_ids 를 문장이 인용한 확정 근거·SEC 출처(nvidia.F3·microsoft.F9·oracle.F5 의 10-K 포함)로 채운다.
4. (low) 3차 과제 2~6 을 유지한다. 연도 추정 일곱 곳, TRG-057 finding, F5 세 판단 counter_evidence, EV-anthropic-010·TRG-006·메타 건수, Oracle 관측 위치·건수·accessed_at·캐시 경합이다.

### 1~4차 리뷰 기록

아래는 4차(확인 리뷰)와 그 안에 옮겨 둔 1~3차 리뷰를 지우지 않고 옮긴 것이다.

4차 검토자: Claude Opus 5.5 · 확인 리뷰 · 2026-10-06
4차 결과: needs_fix
4차 요약: PRP-134~137 로 바뀐 판단 네 건의 사실을 원문과 대조했다. NVIDIA ③ 의 데이터센터 매출($75,246M·$89,023M, 직전 분기 대비 +21%·+18%, 전년 대비 +92%·+117%)과 전년 1분기 중국 Hopper $4.6B 는 10-Q 두 건 원문과 맞는다. Microsoft ⑨ 의 분기 FCF($15.8B·$19.6B 대 $20.3B·$25.6B, 설비투자 $35.8B 대 $17.1B, 회계연도 $71.6B→$67.0B)는 companyfacts 누계 차로 다시 계산한 값과 맞는다. Tesla ④ 의 근거(EV-tesla-007·008)도 맞다. 점수·순위를 바꾸는 발견은 두 건이다. (1) Oracle ⑤ 의 동맹 등급 +2 는 '지분이 걸린 동맹 둘' 에 기대는데, 둘째 동맹인 'Stargate LLC 에 $7B 지분 출자' 를 Oracle 원문이 받쳐 주지 않는다. 2026-08-31 10-Q 와 FY2026 10-K 에 'Stargate' 는 0건이다. 두 문서 모두 비시장성 지분·채무 투자 합계를 $2.4B(2026-08-31)·$2.3B(2026-05-31)로 적고, 그 "substantial majority" 가 TikTok USDS 합작법인(지분 15%)이라고 적는다. $7B 지분 보유와 양립하기 어렵고, 이 사실의 출처는 기준선 문서(SRC-v15-html)뿐이다. 이 판단이 서지 않으면 ⑤ 4→3, 총점 5→4 가 되고 순위도 바뀐다. (2) 기업 요약 넷이 새 점수를 따르지 않는다. Microsoft 는 '총점 14·3위·⑨ 0', Oracle 은 '4점·공동 13위', Tesla 는 '총점 5·공동 11위·④ 4', Meta 는 '4위' 로 적혀 있고, 이 문장이 draft 카드에 그대로 실려 같은 draft 의 순위표(Microsoft·Meta 공동 3위 13점, Oracle 공동 11위 5점, Tesla 공동 13위 4점)와 어긋난다. 이전 리뷰의 다음 실행 과제는 바뀐 것이 없어 그대로 남는다.

4차 검토 기준: results_hash `c11f5cc6b5eb3bf7…`, draft_hash `d522699cf7916b1d…`(review.md frontmatter 와 같음을 확인). 수정 커밋 `80fc1c4`·`3e1eea1`·`f5a54fa`.

### 4차 — 수행한 확인 (스크립트는 스크래치 `review/fs4_*.py`)

- **NVIDIA ③**: 캐시 10-Q 두 건의 sha256 이 index 와 같다(`7eee9866…-nvda-20260426.htm` 접수 0001045810-26-000052, `abcad314…-nvda-20260726.htm` 접수 0001045810-26-000075). 매출 분해표에 "Data Center $75,246 · $62,314 · $39,112 · 21% · 92%" 와 "Data Center $89,023 · $75,246 · $41,096 · 18% · 117%" 가 있다. 1분기 10-Q 에 "No shipments of Data Center Hopper products to China occurred during the quarter, compared with $4.6 billion in the first quarter of fiscal year 2026." 가 있다. 문장의 숫자와 위치가 모두 맞는다. '1분기 전년 대비 성장률이 눌려 있다' 는 문장 스스로 추론이라고 표시했다. 'Alphabet 이 TPU 를 Anthropic·Meta 에 판다' 는 alphabet.F5, 'CUDA 생태계는 ① 의 설치기반' 은 nvidia.F1 문장과 같다. 다만 1분기 10-Q(0001045810-26-000052)는 sources.json 에 등록돼 있지 않다.
- **Oracle ⑤**: 2026-08-31 10-Q(f456b723…) p.7 에 "The substantial majority of the non-marketable investments we held as of August 31, 2026 were with TikTok USDS Joint Venture LLC, an equity method investee in which we have an ownership interest of 15 %." 가 있다. 같은 쪽에 "Our non-marketable equity securities and debt investments totaled $ 2.4 billion and $ 2.3 billion as of August 31, 2026 and May 31, 2026" 가 있다. FY2026 10-K(3fc9afc2…)도 2026-05-31 합계를 $2.3B, TikTok 을 substantial majority 로 적는다. 두 문서에서 'Stargate'·'OpenAI'·'Crusoe' 는 0건이다. 후보 제목(시험·이번 실행)에도 Oracle 의 Stargate 지분을 다룬 제목이 없다. 'TikTok 합작법인의 클라우드를 맡는다' 도 10-Q 주석 1 에는 없다. 적대 근거(EV-oracle-008 의료 침해 2,000만 명)는 확정 근거와 맞는다.
- **Tesla ④**: CNBC 2026-10-03(EV-tesla-007, confirmed)와 13.7GWh·시장 예상 미달(EV-tesla-008·후보 제목)이 맞는다. Optimus 미배치와 Terafab 건설 단계는 이전 문장·트리거와 같다.
- **Microsoft ⑨**: `validation/f6-avail-15/_raw/MSFT.companyfacts.json` 에서 영업현금흐름·설비투자 누계(같은 회계연도 시작일)의 차로 여덟 분기를 다시 구했다. FY25 분기 FCF 는 19.26·6.49·20.30·25.57, FY26 은 25.66·5.88·15.80·19.64 이고, FY25 4분기 설비투자 17.08, FY26 4분기 35.80, 회계연도 FCF 71.61→66.99 다($B). 문장의 숫자와 같다. 문장은 FY26 3·4분기만 적는데, 1분기는 전년보다 +33%, 2분기는 −9% 다(재무·규칙 영역이 판정에 반영할지 본다). 판단 source_ids 는 SRC-v15-html 하나다.
- **기업 요약 14개**: 총점·과점·함정·순위·공동 여부를 새 results 와 다시 대조했다. 넷이 어긋난다(아래 발견 2). 나머지 열은 맞는다.
- **렌더러 문구**: draft 1086행 "Term Loan (unsecured delayed draw) $17.5B 는 2026-09-30 에 인출 시한이 끝나 미인출분이 소멸했다. 런웨이는 2026-06-30 공시 기준 약정으로 계산했다." 는 10-Q 원문("after which any undrawn commitments will automatically terminate")과 관측 as_of 에 맞는다.
- **바뀐 판단과 닿는 근거·트리거 문장**: EV-oracle-008 relevance 가 "Oracle ⑤ 판단은 동맹 등급 +1" 로, EV-tesla-008 relevance 가 "테슬라 ④ 판단은 4점(…Optimus·…Terafab…)" 으로 남아 있다.
- **참조 무결성**: 바뀐 판단의 evidence_ids(EV-oracle-003, EV-tesla-007·008)는 모두 confirmed 근거이고 source_ids 는 모두 sources.json 에 있다.

### 4차 — 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| high · needs_fix | judgments.json oracle.F5 (PRP-135, A=+2) | 동맹 등급 +2 의 둘째 근거 'Stargate LLC 에 $7B 를 지분 출자' 를 Oracle 원문이 받치지 않는다. 10-Q(2026-08-31)·10-K(FY2026)에 Stargate 는 0건이다. 비시장성 지분·채무 투자 합계는 $2.4B 이고 그 대부분이 TikTok USDS 합작법인이라, $7B 지분과 양립하기 어렵다. 이 사실의 출처는 기준선 문서뿐이고 확정 근거·후보에도 없다. 지분 동맹은 원문으로 TikTok 하나만 확인되므로 '지분이 걸린 동맹이 복수' 요건이 서지 않는다. 고치는 길은 둘이다. Stargate 지분을 1차 자료(Oracle·OpenAI·SoftBank 공시)로 확인해 출처를 붙이거나, A 를 +1 로 되돌린다. | 있음 — ⑤ 4→3, Oracle 총점 5→4, 순위(공동 11위→공동 13위) |
| high · needs_fix | judgments.json company_summaries(microsoft·oracle·tesla·meta) · draft.md 191·250·815·965행 | 요약 넷이 새 점수를 따르지 않는다. Microsoft 는 '총점 14점(과점 19, 함정 −5)·3위·⑨ 는 추세 안정이라 0' 인데 실제는 13점(19, −6)·공동 3위·⑨ −1(악화)이다. Oracle 은 '4점(과점 14)·공동 13위' 인데 5점(15)·공동 11위다. Tesla 는 '총점 5(과점 14)·공동 11위·④ 4 강점' 인데 4점(13)·공동 13위·④ 3 이다. Meta 는 '4위' 인데 공동 3위다. draft 카드가 같은 draft 의 순위표와 서로 다른 점수·순위를 싣는다. | 있음 — 화면에 실리는 점수·순위 진술이 틀림(계산값은 맞음) |
| medium | judgments.json nvidia.F3 · microsoft.F9 · sources.json | nvidia.F3 가 근거로 쓴 2026-04-26 분기 10-Q(0001045810-26-000052)는 sources.json 에 없다. 판단 source_ids 는 두 판단 모두 SRC-v15-html 하나라, 10-Q·companyfacts 숫자가 판단 단위로 출처에 이어지지 않는다(3차 medium 의 연장). | 없음 |
| low | judgments.json oracle.F5 | 'TikTok 합작법인의 클라우드를 맡는다' 를 10-Q 주석 1 출처로 묶어 적었으나, 주석 1 은 지분 15%·지분법만 적는다. | 없음 |
| low | evidence.json EV-oracle-008 · EV-tesla-008 relevance | 바뀌기 전 판정(Oracle ⑤ 동맹 +1, 테슬라 ④ 4점·Optimus·Terafab 포함)을 '지금 판단' 으로 적는다. | 없음 |
| low | judgments.json microsoft.F9 | 분기 FCF 악화를 FY26 3·4분기 둘로만 적는다. 같은 회계연도 1분기는 전년 대비 +33%, 2분기는 −9% 다. 사실 오류는 아니고, 이 사실을 판정에 어떻게 반영할지는 재무·규칙 영역이 본다. | 없음 |

이전 리뷰(3차) 발견의 처리는 다음과 같다. 판단 근거 출처 연결(medium)은 남는다. 연도 추정 일곱 곳은 판단이 바뀌지 않아 남는다. TRG-057 의 '9/14 8-K 미열람'·PRP-002 표현, 철회 트리거의 다른 트리거 번호 참조, F5 세 판단 counter_evidence 의 행 번호, EV-anthropic-010 꼬리표, TRG-006 날짜·메타 303건은 트리거·근거가 바뀌지 않아 모두 남는다. 아마존 여신 메모는 렌더러 수정 뒤에도 사실과 맞는다(닫힘 유지).

### 4차 — 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 이해당사자 출처를 사실의 상한으로 둔다(3차와 같음). 바뀐 판단 네 건은 10-Q·companyfacts·확정 근거를 쓴다. 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | Tesla ④ 는 배치 전 Optimus·Terafab 을 폭에서 뺐고, Microsoft ⑨ 는 2026 역년 설비투자 계획 하향을 추세 근거로 쓰지 않는다고 적었다. Oracle ⑤ 의 Stargate 지분은 계획 문제가 아니라 출처 문제라 발견 1 로 적었다. |
| Q14 | pass | 진행 중인 사건을 끝난 것으로 세지 않는다(3차와 같음). NVIDIA ③ 의 1분기 비교 기준 왜곡은 스스로 추론으로 표시했다. |
| Q23 | not_applicable | 바뀐 판단 네 건에 벤치마크 비교가 없다. |

### 4차 — 다음 실행 과제
1. (needs_fix 와 같은 묶음) oracle.F5 의 Stargate LLC 지분을 1차 자료로 확인해 출처를 붙인다. 확인되지 않으면 A 를 +1 로 되돌리는 제안을 올린다. 같은 사실을 쓰는 oracle.F7(세로축 '내 돈이 돌아옴')과 openai.F5(Stargate 공동 지분)도 같은 자료로 문장을 맞춘다. 두 판단의 점수에는 닿지 않는다(Oracle ⑦ 은 가로축 '큼' 이라 −2, OpenAI ⑤ 는 Broadcom·국방부로 +1 유지).
2. (needs_fix 와 같은 묶음) 기업 요약 넷(Microsoft·Oracle·Tesla·Meta)을 새 results 로 다시 쓴다. 요약이 총점·순위를 적는 이상 판단이 바뀔 때마다 요약도 같이 바뀌도록, 검증기가 요약 속 총점·과점·함정·순위를 results 와 대조하게 한다.
3. (medium) nvidia.F3 가 인용한 2026-04-26 분기 10-Q 를 sources.json 에 등록하고, 판단의 source_ids·evidence_ids 를 문장이 인용한 확정 근거·SEC 출처로 채운다(3차 과제 1 의 연장).
4. (low) EV-oracle-008·EV-tesla-008 relevance 의 '지금 판단' 서술을 새 판정으로 맞춘다. oracle.F5 의 TikTok 클라우드 서술에 맞는 출처를 붙이거나 출처 괄호 밖으로 뺀다.
5. (low) 3차 과제 2~6 을 유지한다. 연도 추정 일곱 곳, TRG-057 finding, F5 세 판단 counter_evidence, EV-anthropic-010·TRG-006·메타 건수, Oracle 관측 위치·건수·accessed_at·캐시 경합이다.

### 1~3차 리뷰 기록

아래는 3차(완결된 문장 재작성 뒤 1차)와 그 안에 옮겨 둔 1·2차 리뷰를 지우지 않고 옮긴 것이다. 세 리뷰 모두 결과는 pass 였다.

3차 검토자: Claude Opus 5.5 · 완결된 문장 재작성 뒤 1차 · 2026-10-06
3차 결과: pass
3차 요약: 다시 쓴 판단 114개(승계 102·새 판단 12)와 기업 요약 14개를 문장 단위로 전수 대조했다. 이전 문장(`revision_history[-1].previous.evidence`)·확정 근거·관측·results·트리거·후보 제목 어디에도 없는 새 사실은 찾지 못했다. 금액·숫자·고유명사·날짜를 스크립트로 뽑아 대조했고, 걸린 41문장은 모두 관측에서 계산한 비율·성분이거나 관측 basis·이전 문장에 있는 값이었다. 판단 문장 속 2026-09 이후 날짜 보도는 모두 같은 기업의 확정 근거와 ±1일 안에서 맞는다. 다만 연도 없이 'M/D'·'M월'로 적혀 있던 이전 사실 일곱 곳에 2026 을 붙였다(알파벳 ⑤ 4/28·5월, 아마존 ②·⑤ 와 마이크로소프트 ⑤ 의 8/28, 아마존 ② 의 Google 4월, Oracle ⑧ 의 S&P 7/9, 스페이스X ① 의 7/20). 원문으로 연도를 확인할 수 있는 것은 아니지만 2026 은 사실상 틀림없다. 이 밖에 이전 문장의 사실이 빠져 판정 재료의 근거가 약해진 곳은 없고, 빠진 것은 다른 기업 점수 비교·옛 판 수치·작업 표기였다. 요약 14개는 총점·과점·함정·순위·공동 여부·인용 수치(성장률·PER·EV/매출·영업외 비중·런웨이·커버리지)가 results 와 모두 맞는다. 고친 근거 28건·트리거 51건에도 새 사실이 없고, 상태·기한·출처 칸은 바뀌지 않았다. 참조 무결성은 그대로 0 누락이다. 아마존 지연인출 정기대출 $17.5B 의 소멸 조건은 10-Q 원문과 맞는다. 판단 문장은 '시한이 끝났다'로만 적고, 계산은 2026-06-30 기준 $37.5B 를 쓴다. 둘은 어긋나지 않으며 점수 영향도 없다(런웨이 8.0년·6.7년). 점수·순위·체크리스트를 바꾸는 발견은 없다. 남은 것은 medium 1건(판단 단위 출처 연결)과 low 들이다.

3차 검토 기준: results_hash `975fbe139afc3c37…`, draft_hash `7f21d3d4b2577789…`(review.md frontmatter 와 같음을 확인). 재작성 커밋 `6c5efaf`·`96d39b2`·`2a4b94b`·`9e336b6`. 판단 114·요약 14·근거 72·트리거 80·출처 210건이다.

#### 3차 — 수행한 검토 (스크립트는 스크래치 `review/fs3_*.py`)

- **새 사실 탐지(판단 114·요약 14)**: 문장마다 금액(달러·억·조 환산 포함, 오차 1.2%)·숫자·영문 고유명사를 뽑았다. 이것을 같은 기업의 이전 문장 전부(재작성 전 판단, `revision_history` 의 모든 previous, superseded 기록), 근거(재작성 전·후), 트리거, 관측 raw·basis, results, 후보 제목과 대조했다. 걸린 41문장을 하나씩 열어 보니 모두 계산값(영업이익률·영업외 비중·성장률·PER·EV/매출·런웨이 1.16년·커버리지 2.31배·RPO 증가폭 $26B)이거나 관측 basis·이전 표에 있는 값이었다. 예를 들면 알리바바 영업권 손상 RMB4,458M·EU DSA 충당(rs1006 note), 스페이스X 신용장 $645M·Spectrum $11.1B/$20.8B(관측 basis·이전 문장), 메타 영업현금흐름 $130.30B(관측 basis), 팔란티어 92.8%·$764M(이전 표)이다.
- **문장 전수 읽기**: 114개 판단의 이전·새 문장을 나란히 놓고 전부 읽었다. 새로 보이는 서술은 다시 원문과 대조했다. Vera Rubin 보도자료 날짜(2026-01-05·2026-03-16)는 이전 note 에 있다. CoreWeave NVL72(2026-09-30)·테슬라 에너지 저장 미달·크로아티아 FSD·Oracle 의료 침해 2,000만 명·Tencent 칩 10만 개·Palantir Armada·44,000건·WIRED 는 확정 근거·후보 제목에 있다. TSMC 2분기 +36%·가이던스 +30%→+40% 이상·GM 67.7%, 메타 2분기 $60.80B, 아마존 Interconnect 프리뷰, 알파벳 현금 $55.9B, 애플 현금 $39.5B, 알리바바 자본약정+기타약정은 이전 표·트리거·관측에 있다. 스페이스X ⑤ 의 'Google 은 자체 TPU 가 있어 떠날 수 있다'도 확정 근거 문장에 있다.
- **빠진 사실**: 판단마다 이전 문장에만 있는 숫자·고유명사를 뽑아 보았다(67개 판단). 빠진 것은 세 부류였다. 다른 기업 점수와의 비교(애플 ③2·NVIDIA ⑤2·Anthropic ④4·Palantir 비교 등), 대체된 옛 수치(아마존 미개시 리스 $106B, Oracle 순부채·Debt/EBITDA·Altman Z, 알리바바 −848M→15,161M), 작업·행 번호다. 판정 재료(③ 세 기준·⑤ A/H·⑦ 두 축·⑨ gate_inputs)를 받치는 사실이 빠진 곳은 없다. 아마존 ⑨ 의 G4 는 $496B ÷ $267.3B(미개시 리스 $137.2B + 구매약정 $130.1B)로 오히려 정확해졌다.
- **날짜**: 새 문장에서 연도가 붙은 날짜 가운데 같은 날짜가 연도와 함께 corpus 에 없는 것을 뽑았다. 확정 근거 발행일과 맞는 것(Anthropic 9/25·9/30·10/5, OpenAI 9/28·9/29·10/4·10/5, 마이크로소프트 9/25·9/29)은 문제가 없다. 후보 제목으로 2026 이 확인되는 것(알리바바 8/23 증자, 스페이스X 6/12 상장·8/14 Cursor, Qwen3.8-Max 8/12~13)도 문제가 없다. 이 둘을 빼면 아래 발견 2 의 일곱 곳이 남는다.
- **판단 속 보도 → 확정 근거**: 2026-09 이후 날짜를 단 보도 서술을 전부 같은 기업 확정 근거의 발행일(±1일)과 맞췄다. 맞지 않는 것은 기준선 시점(2026-09-02) 사실 4건뿐이다(알파벳 Gemini 3.8 Flash, 메타 AA 기사, NVIDIA HF 서명 — HF 는 EV-nvidia-009 8-K 2026-09-03 과 하루 차). 후보만 있고 확정되지 않은 보도를 인용한 문장은 없다.
- **요약 14개**: 총점·과점·함정·순위·공동 여부를 results 와 대조했다. 인용 수치도 results calc 와 맞췄다. 알리바바 성장 4.4%·영업외 70%(0.701), 아마존 0.47(0.466), 알파벳 0.51, 애플 성장 14.2%, 마이크로소프트 PER 29.2·EV/매출 11.9, 팔란티어 약 151배(150.87), 스페이스X −16.2%·95배(95.25)·런웨이 3.03년, 테슬라 393배·11.8%, Oracle −$28.72B·1.61년이 모두 맞다. 서술 사실(메타 30억, 애플 20억 대, Copilot 3,000만, ICE)도 각 판단에 있다.
- **근거 28건·트리거 51건**: 바뀐 칸은 근거 쪽 relevance 21·conditional_impact 11·counter_evidence 7·unverified 2 이고, 트리거 쪽 observation·condition·finding·recheck 다. 이전 판·관측·results·후보에 없는 새 토큰은 없다. 테슬라 $8.28B·$3.89B·$0.35B·$0.81B 는 관측 basis 의 백만 단위 값을 환산한 것이다. 근거의 excerpt·title·status·reviewer 와 트리거의 status·deadline·evidence_ids·source_ids 는 바뀌지 않았다.
- **아마존 미인출 여신**: 보존 10-Q(3cf9799:validation/offb-24/_raw/amzn-20260630.htm) 원문 "single draw on any business day on or prior to September 30, 2026, after which any undrawn commitments will automatically terminate" 와 판단 문장이 맞는다. 판단은 소멸이 아니라 '인출 시한이 끝났다'로 적는다(인출했는지는 원문으로 알 수 없다). 관측 as_of(2026-06-30)에는 세 시설 모두 유효했으므로 계산의 $37.5B 와 어긋나지 않는다. 15.0B 만 세면 8.0년, 현금만 세면 6.7년이라 G3 결론도 같다(관측 basis.sensitivity 와 일치).
- **참조 무결성**: 관측 525·판단 183·근거 72·트리거 187 참조가 모두 출처 210건 안에 있다. 판단의 evidence_ids 는 anthropic.F5.impl48(EV-anthropic-002·006, confirmed) 한 건이다.

#### 3차 — 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| medium | judgments.json 판단 전반(특히 새 판단 12개와 2026-09 이후 보도를 인용하는 판단) | 다시 쓴 문장이 확정 근거의 보도(예: 알파벳 ⑤ 의 EU·애드테크·영국·폴란드, 메타 ⑤ 의 10월 보도, 팔란티어 ⑤ 의 Armada·44,000건·WIRED, Oracle ⑤ 의 침해 사고, 아마존 ① 의 UBS)와 새 SEC 원문 숫자를 문장 안에서 날짜·매체로 인용한다. 그런데 판단의 `source_ids` 는 대부분 [SRC-v15-html·rule·md] 그대로이고 `evidence_ids` 는 한 건뿐이다. 사실은 모두 확정 근거·관측에 있어 추적은 되지만, 판단 단위로는 이어지지 않는다(지난 리뷰 medium 4 가 넓어진 것). | 없음 |
| low | alphabet.F5 · amazon.F2 · amazon.F5 · microsoft.F5 · oracle.F8 · spacex-xai.F1 · tesla.F3 | 이전 문장에 연도 없이 적혀 있던 날짜(4/28·5월·8/28·4월·7/9·7/20)에 2026 을 붙였다. 확정 근거·후보 제목으로 연도를 확인할 수 없다. 기준선 문서가 2026-09-02 시점의 '새 사실'로 적은 것이라 2026 이 사실상 맞지만 추정이다. TRG-051 observation 의 '2026-08-28 프리뷰' 도 같은 추정이다. | 없음 |
| low | triggers.json TRG-057 carry.finding | 끝에 "2026-09-14 8-K(Items 8.01·9.01)도 후보에 있으나 본문 미열람이다" 가 남아 있다(2차 low, 미해결). 같은 공시를 TRG-022 는 Ellison 10b5-1 계획 취소로 적는다. 같은 finding 에 'PRP-002'·'시험 실행 EV-oracle-002' 같은 작업·이전 판 표현도 남아 있다. research.md 에만 실리고 draft·report.html 에는 없다. | 없음 |
| low | triggers.json 철회 트리거 등 20건(TRG-044~076) · research.md | 'TRG-0NN 으로 이었다' 같은 다른 트리거 번호 참조가 carry.finding·condition 에 남아 research.md 에 19번 나온다. draft·report.html 에는 0번이다. 사실 오류는 아니다(출력 영역 판단 몫). | 없음 |
| low | judgments.json tsmc.F5.strict54 · anthropic.F5.impl48 · openai.F5.impl48 counter_evidence | 반대 근거 칸에 '원문 별표 G 판정표 218·214·224행', '채점표 945행 정정', 'worker 관찰' 같은 행 번호·작업 경위 문장이 그대로 있다. draft·report.html 에는 실리지 않는다. 사실은 맞다(1차에 원문 대조한 내용). | 없음 |
| low | evidence.json EV-anthropic-010 | excerpt 꼬리표 '- bbc.com' 과 raw_ref·출처 장부의 '- BBC' 가 다르다(1차 low, 미해결). | 없음 |
| low | triggers.json TRG-006 · TRG-010·011·012·056 | qz 보도일 10-06(후보 2026-10-05T19:35Z)과 메타 뉴스 303건(후보 307건)이 그대로다(1차 low, 미해결). | 없음 |

#### 3차 — 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 다시 쓴 문장도 이해당사자 발표를 사실의 상한으로 둔다. NVIDIA Vera Rubin 수치는 '벤더 발표이고 독립 측정이 아니다'로, OpenAI Jalapeño InferenceX 는 '이해당사자 발표라 1차 근거가 아니다'로 적었다. OpenAI ARC-AGI-3 99.9% 는 자사 하네스라 쓰지 않았다. Microsoft Copilot 블로그는 '독립 측정이 없어 반영하지 않았다'로 적었다. 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | 계획을 현재 점수에 넣지 않는다는 서술이 판단마다 사실과 맞다. 알리바바 8/23 증자, 메타 기업용 AI 출범, 테슬라 AI5·Optimus·Terafab, 애플 Baltra, Anthropic 자체 칩, OpenAI Jalapeño 배치 계획, TSMC CoWoS 14배 레티클, 아마존 $42B 사채 추진, Oracle 2026년 $45~50B 조달이 그렇다. 기준일 뒤 사건은 쓰지 않았다. |
| Q14 | pass | 진행 중인 사건(Hugging Face 종결 전, Anthropic 상장 전, OpenAI 라운드 협상, EU FSD 표결 12월, 새 Siri 미출시)은 미완으로 적었다. 아마존 지연인출 약정도 인출 여부를 단정하지 않는다. |
| Q23 | pass | 하네스가 다른 벤치마크 비교를 근거로 쓰지 않는다. 메타 Tau3-Bench, 알리바바 HLE, Anthropic ARC-AGI-3, OpenAI FrontierMath 는 하네스 미표기라 비교 근거에서 뺐고, 전원 자기 하네스인 Coding Agent Index 만 비교에 썼다. |

#### 3차 — 다음 실행 과제
1. (medium) 판단의 `source_ids`·`evidence_ids` 를 문장이 인용한 확정 근거와 새 SEC 출처로 채우는 판단 변경 제안을 올린다. 재작성 문장이 보도를 날짜·매체로 인용하므로, 해당 EV ID 를 기계로 붙일 수 있다(이번 스크립트로 2026-09 이후 보도는 모두 ±1일 확정 근거와 맞았다).
2. (low) 연도를 추정해 붙인 날짜 일곱 곳(알파벳 ⑤ 4/28·5월, 아마존 ② 4월·8/28, 아마존 ⑤·마이크로소프트 ⑤ 8/28, Oracle ⑧ 7/9, 스페이스X ①·테슬라 ③ 7/20)을 원문으로 확인하거나 '연도 미확인'으로 적는다.
3. (low) TRG-057 finding 의 '9/14 8-K 본문 미열람'을 Ellison 10b5-1 계획 취소로 고치고, 'PRP-002'·'시험 실행' 표현을 지운다. 철회 트리거들의 'TRG-0NN 으로 이었다' 를 완결된 문장으로 바꿀지는 출력 영역과 함께 정한다.
4. (low) tsmc.F5·anthropic.F5·openai.F5 의 counter_evidence 에 남은 행 번호·작업 경위 문장을 현재 상태 문장으로 다시 쓴다.
5. (low) EV-anthropic-010 excerpt 꼬리표, TRG-006 qz 날짜, 메타 뉴스 건수를 후보 원문 기준으로 맞춘다.
6. (low) oracle.net_cash.rs1006 리스 위치(p.12), oracle.undrawn_credit 'revolv' 건수(35), 출처 5건의 accessed_at(raw 수집 시각)을 고친다. sec-get 캐시 index 의 동시 기록 경합을 막는다.

#### 1·2차 리뷰 기록

아래는 확인 리뷰(2차)와 그 안에 옮겨 둔 1차 리뷰를 지우지 않고 옮긴 것이다. 두 리뷰 모두 결과는 pass 였다.

2차 검토자: Claude Opus 5.5 · 확인 리뷰(2차) · 2026-10-06
2차 결과: pass
2차 요약: 1차 medium 1~3(TRG-057 발동, TRG-078 의 SpaceX 몫 → TRG-080 발동, TRG-070 Cursor 4건)이 닫혔다. low 가운데 아마존 9/14 8-K, 알리바바 ⑨ '-3' 문구, preview 원인 분류도 닫혔다. 새 출처 3건은 sources.json 에 있다. URL·제목·발행일이 후보 원문과 같고, 아마존 8-K 는 원 submissions JSON 에서 접수번호·문서명까지 확인했다. 트리거 참조 187건 가운데 빠진 출처는 없다. 고친 트리거·근거 문장의 숫자(Oracle 런웨이 1.61년, 커버리지 2.66배, FCF −287억 달러, PER 22.83·EV/매출 7.858·성장 21.62%, TSMC P3 30.56%, £4.25B·£4.235B)는 관측·results·원문과 맞다. research.md 의 「이전 트리거 처리」 80행과 「발동 트리거 재검토 대상」 4행은 triggers.json 과 같고, 유지 이유가 finding 에 있다. 새로 보인 것은 low 두 건뿐이고 점수·순위·체크리스트에 닿지 않는다. medium 4(PRP 판단의 source_ids)는 지시대로 다음 실행 과제로 남긴다.

2차 검토 기준: results_hash `34248db45321ea0b…`, draft_hash `2af65e2f45bb0e34…`(review.md frontmatter 와 같음을 확인). 1차 뒤 커밋 `08bfc90`·`6ae2ac9`·`96d522f`. 트리거 80·출처 210·근거 72·판단 114건이다.

##### 2차 — 1차 발견 처리
| 1차 발견 | 상태 | 확인 내용 |
| --- | --- | --- |
| medium · TRG-057 expired | 닫힘 | status 가 `fired` 다. finding 에 발동 판정이 붙었다. Oracle ⑥ −2→−1 은 results 와 같다(P1 22.83·P2 7.858·P3 21.62%). ⑨ −3 은 그대로이고 런웨이는 1.61년이다. ⑦ 은 PRP-002 로 숫자만 고쳤다. ⑧ 은 10-Q 에 OpenAI 0건·고객 집중 서술 0건이라 유지했고, 이것은 1차에 원문으로 확인했다. research.md 「발동 트리거 재검토 대상」에 ⑦(수정함)·⑧(수정하지 않음) 행이 있다. |
| medium · TRG-078 의 SpaceX 몫 | 닫힘 | TRG-080 을 새로 만들었다(spacex-xai, ref baseline/v1.5:TRIG-029, fired, evidence EV-spacex-xai-007 = IBD 2026-09-28 'SpaceX Launches Starship Flight 14, Deploys Starlink Satellites', confirmed). '처음 궤도'는 후보 Moomoo 09-29 '첫 궤도 도달' 제목과 맞는다. 유지 이유(②는 비AI 귀속 원칙상 근거가 아니고, ④는 이미 5로 범위 맨 위)는 results 와 같다(SpaceX ④ 5, ② 4). TRG-078 은 테슬라 몫만 철회한다. research.md 의 TRIG-029 두 행(철회/TRG-078/Tesla, 발동/TRG-080/SpaceX)이 맞다. |
| medium · TRG-070 'Cursor 0건' | 닫힘 | finding 에 후보 4건을 적었다(cnbc·Reuters 06-16 인수 $60B, Reuters 07-07, a16z 08-14). 후보 제목과 같다. 결론(관찰 유지)은 제목상 전환이 확인되지 않아 지킬 수 있다. 새 source_ids 2건은 sources.json 에 있고, URL·제목·발행일이 후보와 같다. raw_ref `20261006T054447Z-9da267d9.xml` 에 URL 이 그대로 있다. |
| medium · PRP 판단 4건 source_ids | 다음 실행 과제 유지 | 이번 수정 대상이 아니다(조율자 지시). |
| low · alibaba.F9 '이번 실행 점수는 -3' | 닫힘 | PRP-005(사람 반영, revision_history 기록)로 '현재 점수와 경로는 다음 줄에 있다' 로 바뀌었다. 판정 재료는 그대로다. |
| low · amazon.F9 '$106B' | 다음 실행 과제 유지 | 바뀌지 않았다. draft 주의 표시는 그대로다. |
| low · EV-anthropic-010 매체 꼬리표 | 다음 실행 과제 유지 | 바뀌지 않았다. |
| low · TRG-005 아마존 9/14 8-K | 닫힘 | finding 에 £4.25B 네 종(2029·2032·2038·2045) 발행 완료, 순조달 약 £4.235B, 현금 기준일(2026-06-30) 뒤라는 사실을 적었다. 1차에 sec-get 으로 받은 원문 Item 8.01 과 같다. source_id `SRC-EDGAR-000110465926107526` 이 등록됐고 URL 은 후보와 같다. submissions JSON 에 접수번호 0001104659-26-107526·문서명 tm2624614d5_8k.htm 이 있다. |
| low · 이어받지 않은 EV 인용(EV-apple-003·EV-oracle-002) | 다음 실행 과제 유지 | 바뀌지 않았다. |
| low · oracle.net_cash 리스 위치 p.13, undrawn 'revolv' 건수 | 다음 실행 과제 유지 | 관측은 바뀌지 않았다. |
| low · sec 캐시 index 누락 | 닫힘(캐시) | 1차에 sec-get 으로 다시 받아 index 에 항목이 생겼다. 경합 방지는 다음 실행 과제다. |
| low · TRG-006 날짜, 메타 303건 | 다음 실행 과제 유지 | 바뀌지 않았다. |
| low · preview 알리바바 ⑨ 원인 '판단 수정' | 닫힘 | preview 가 '⑨ −3→−4 (📊 관측(가격·재무))' 다. ⑥ 은 '📐 규칙(트랙 listed_annual→listed_ttm)·📊 관측' 이고, 순위만 바뀐 Palantir·Tesla 행이 들어갔다. |
| low · oracle.F7·F9 의 v1.5 수치 표시 없음 | 다음 실행 과제 유지 | 바뀌지 않았다. |

##### 2차 — 바뀐 항목 확인
| 항목 | 결과 | 확인 내용 |
| --- | --- | --- |
| TRG-057 finding 숫자 | 맞음 | PER 431.93/18.92 = 22.83, EV/매출 (431.93+132.07)/71.78 = 7.858, 성장 71,776/59,018 − 1 = 21.62%. results oracle F6 P1·P2·P3 와 같다. |
| TRG-080 | 맞음 | ref·evidence(confirmed)·factors·deadline(=기준일)·fired 의 출처가 갖춰졌다. 사실은 후보 제목과 같다. |
| TRG-070 | 맞음 | 위와 같다. |
| TRG-017 | 맞음 | P3 = 141.552/108.422 − 1 = 30.56%(results tsmc F6 P3 0.3056, track listed_ttm). 'GM 3~4%p 희석 가이던스'는 기준선 TRIG-005 why 와 같다. HPC 66%·NVIDIA 19% 는 tsmc.F8 근거와 같다. |
| TRG-022 | 맞음 | 1.61년·2.66배는 관측과 같다. Oracle 9/14 8-K 가 Ellison 10b5-1 계획 취소라는 사실은 1차에 sec-get 으로 받은 원문 Item 8.01 과 같다. |
| TRG-005 | 맞음 | 위 표와 같다. |
| EV-oracle-003·004·006·007 | 맞음 | −287억 달러(−28.72B), 1.61년, 2.66배(664/250)는 rs1006 관측과 같다. '⑦ 판정표' 표기로 바뀌었다. excerpt·출처·status 칸은 바뀌지 않았다. |
| alibaba.F9 문구(PRP-005) | 맞음 | 위 표와 같다. |
| 참조 무결성 | 맞음 | 관측 525·판단 183·근거 72·트리거 187 참조가 모두 출처 210건 안에 있다. 트리거 evidence_ids 는 모두 confirmed 근거다. |
| research.md 트리거 표 | 맞음 | 「이전 트리거 처리」 80행의 결론·확인 내용이 triggers.json 80항목과 같다(TRIG-029 는 두 행). 「발동 트리거 재검토 대상」 4행. |

##### 2차 — 새로 보인 것
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| low | triggers.json TRG-057 carry.finding | 끝 문장 "2026-09-14 8-K(Items 8.01·9.01)도 후보에 있으나 본문 미열람이다" 가 남았다. 같은 공시를 TRG-022 finding 은 'Ellison 10b5-1 계획 취소' 로 확인해 적었다. 두 finding 의 서술이 어긋난다. | 없음 |
| low | sources.json SRC-NEWS-spacex-xai-20260616-86997696·20260707-4e501b19 (기존 3건 포함 5건) | raw_ref 는 2026-10-06 수집본(20261006T…)인데 accessed_at 은 2026-10-01T06:20:27Z 다. 기준일 안이라 점수와 무관하다. | 없음 |

##### 2차 — 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 1차와 같다. 새로 쓴 TRG-070·TRG-080 도 2차 매체 제목을 사실의 상한으로 두고, 전환·궤도 컴퓨트 같은 미확인 사실은 조건 미충족으로 남겼다. 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | 아마존 회사채 발행 완료분은 현금 기준일 뒤라 완충에 넣지 않았다고 적었다(TRG-005). $42B 추진은 계획으로 둔다. TRG-017 의 P3 경계 언급은 감시 이유이고 점수 입력이 아니다. |
| Q14 | pass | TRG-080 은 '페이로드 배치'라는 끝난 사건만 발동으로 세고, 궤도 데이터센터 컴퓨트·매출은 TRG-034 관찰로 남겼다. TRG-070 은 인수·협업을 모델 전환으로 세지 않았다. |
| Q23 | pass | 1차와 같다(바뀐 항목에 벤치마크 비교 없음). |

##### 2차 — 다음 실행 과제
1. (medium) PRP 판단 네 건(oracle.F9, oracle.F7.fix52, alibaba.F9.obsreg25, tsmc.F9)의 `source_ids` 에 새 SEC 출처(SRC-SEC-FACTS-ORCL-20261006, SRC-SEC-ORCL-10K-FY2026, SRC-SEC-TSM-6K-*, SRC-SEC-BABA-6K-*)를 더하는 제안을 올린다. Oracle·TSMC 문장에도 관측 ID(rs1006)를 적는다.
2. (low) TRG-057 finding 끝 문장의 9/14 8-K '본문 미열람' 을 TRG-022 와 같게 'Ellison 10b5-1 계획 취소' 로 고친다.
3. (low) amazon.F9.obsreg25 '미개시 리스 $106B', oracle.F7 '$167B', oracle.F9 의 Debt/EBITDA·이자보상·Altman Z 에 v1.5 표시를 붙이거나 현재 값으로 고친다.
4. (low) EV-anthropic-010 의 title·excerpt 를 raw_ref 표기("- BBC")로 맞춘다. 다음 선별부터 excerpt 를 raw_ref 의 제목에서 기계로 복사한다.
5. (low) 이어받지 않은 이전 근거(EV-apple-003·EV-oracle-002)를 인용하는 문장은 출처 ID 로 바꾸거나 그 사실을 적는다.
6. (low) oracle.net_cash.rs1006 리스 성분 위치를 p.12 로 고치고, oracle.undrawn_credit 의 'revolv' 건수(26→35)를 다시 센다. sec-get 캐시 index 의 동시 기록 경합을 막는다.
7. (low) TRG-006 의 qz 날짜(10-05)와 메타 뉴스 건수(307)를 후보 기준으로 맞춘다.
8. (low) raw_ref 가 2026-10-06 수집본인 출처 5건의 accessed_at 을 실제 수집 시각으로 맞춘다.

##### 1차 리뷰 기록

아래는 1차(round 1) 내용을 지우지 않고 옮긴 것이다. 1차 결과는 pass 였고, 아래 요약 문단 뒤 1차 검토 기준은 results_hash `1101644bc117e2a2…`, draft_hash `1168a515ee524414…` 였다.

1차 요약: 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 확인한 것은 다음과 같다. 참조 무결성(관측 525·판단 183·근거 72·트리거 183 참조가 모두 출처 207건 안에 있다), 근거 72건 전부 confirmed·검토자·검토일 있음, excerpt 71/72건이 후보 제목과 글자 그대로 같다, 기준일 뒤 자료 없음. 새 재무 관측 29건의 성분 값은 SEC 원문 캐시와 20-F 보존본에서 전부 찾았고, 산술·환율·인용문·쪽 위치도 재현했다(예외 1건). 부재 주장(알리바바 계약수입 확인된 미공시, TSMC 미인출 여신 unverified)도 원문으로 재현했다. PRP-001~004 판단 문장의 숫자는 확정 관측과 맞다. 트리거 79건의 carry 표는 triggers.json 과 79/79 일치하고, 인용한 매체·날짜·숫자는 후보 제목과 맞는다. medium 네 건이 남았다. 사건이 일어났는데 fired 로 처리하지 않은 트리거 두 건(TRG-057, TRG-078 의 SpaceX 몫), 부재 주장이 틀린 트리거 한 건(TRG-070 'Cursor 0건' — 실제로는 4건), 판단 단위 source_ids 에 새 SEC 출처가 빠진 것 한 건이다. 넷 다 점수에는 닿지 않아 결과를 막지 않는다. 다만 셋은 승인 전에 고칠 만하다(아래 「다음 실행 과제」 1~3).

1차 검토 기준: results_hash `1101644bc117e2a2…`, draft_hash `1168a515ee524414…`(review.md frontmatter 와 같음을 확인). 관측 440·판단 114(new 12)·근거 72·트리거 79·출처 207·후보 4,507건.

###### 1차 수행한 검토 (전수, 스크립트는 스크래치 `review/fs_*.py`)

- **참조 무결성**: 관측·판단·근거·트리거·제안의 `source_id`/`source_ids`/`evidence_ids` 를 재귀로 전부 모아 대조했다. 빠진 것 0건. draft.md 의 SRC 207·EV 56 참조도 모두 있다. research.md 에서는 EV 두 개가 이번 장부에 없다(발견 9).
- **근거 72건**: 38건은 이전 실행 근거와 모든 칸이 같고(reviewed_at 2026-10-01), 34건은 이번에 확정했다(noble, 2026-10-06). 상태는 전부 confirmed 다. `status: new` 판단 가운데 EV 를 인용한 것은 anthropic.F5.impl48(EV-anthropic-002·006, confirmed) 하나다. excerpt = 후보 제목인 것이 71건이고, 예외는 EV-anthropic-010 이다(발견 7). 가장 늦은 발행시각은 2026-10-05T23:09:19Z 다. 공시 9건은 published_at_utc 가 null 이고 filed_at 은 2026-06-10~10-02 이다. 후보 창은 2026-04-09~10-06 이다.
- **새 재무 관측 29건**: 성분 값을 원문에서 찾았다. Oracle 은 companyfacts(start·end·accn 까지 일치)와 10-Q·10-K 본문, TSMC 는 6-K 연간·반기 연결재무제표 4건, 알리바바는 20-F(`validation/offb-24/_raw`, sha256 은 CRLF 를 정규화하면 출처 장부와 같음)와 6-K 보도자료 2건이다. 알리바바 차입금 266,530 은 5개 행의 합이고, TSMC 상장주식 유동분 2,500,625 는 B/S 193,182,690 − 채무증권 190,682,065 로 나온다. 모두 재현했다. 성분 합계와 원통화÷환율도 29건 모두 관측값과 같다(TSMC 는 천 단위). 인용문은 Oracle RPO·제한현금·회전여신 주석 6·MD&A·약정 준수·CP, TSMC VIS 처분·주석 32·33g·33h, 알리바바 474,505 문단을 원문과 대조했다. 쪽 위치는 10-K p.53·65·68·85·86, 10-Q p.1·2·5·6·7·33, 20-F F-5·F-12 를 재현했다(10-Q p.13 은 예외, 발견 10). 환율은 TSMC 31.37 을 `git show f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` 에서(sha256 이 출처 장부와 같음), 알리바바 6.8980 을 20-F 에서 확인했다.
- **부재 주장**: alibaba.contracted_revenue.obsreg25(not_disclosed_confirmed)는 20-F F-21 'Practical expedients and exemptions' 문장이 있고 'remaining performance obligation' 은 0건이다. 2026 6월 분기 6-K 에도 RPO·backlog 는 0건이다. 이것이 알리바바 ⑨ −4 의 G4 근거다. tsmc.undrawn_credit.rs1006 은 missing_type=unverified 이고, 2026H1·2025H1 6-K 검색 건수 13개가 basis 와 정확히 같다. oracle.F7 의 '8월 말 OpenAI 몫 미공시'는 10-Q 본문에서 'OpenAI' 0건으로 확인했다.
- **판단 근거 숫자(14개사)**: 판단 근거 문장의 달러 금액을 모든 관측값과 대조해, 대체된 관측 값과 같고 현재 값과는 다른 것을 찾았다. FCF·순현금·현금·매출·영업이익·RPO·순이익 키워드 숫자도 results 가 쓴 관측과 대조했다(오차 3%). 걸린 것은 분기·부문 값이거나 v1.5 표시가 붙은 승계 문면뿐이고, 발견 5·6·16 만 남는다. PRP 네 판단은 다시 계산했다. Oracle 은 23,057/71,776=32.1%, 영업현금흐름 46,940, 설비투자 75,660, 런웨이 (36,369+10,000)/28,720=1.61년과 1.27년, 664/250=2.66, 332/71.78=4.6년, 선수금 제외 −40.08B 다. 알리바바는 30,323/1,044,971=2.90%, 24,048/11,102=2.17년, 254,198/6.898=36,851, 67,678/38,676=+75% 다. TSMC 는 FCF 36.45, 순현금 86.51(VIS 제외 84.06), 마진 56.1% 다. 모두 맞다.
- **다른 기업 점수 인용**: 판단 근거에서 다른 기업의 factor 점수를 인용한 것은 승계 판단 4줄뿐이다(microsoft.F3→애플 ③2, apple.F5→NVIDIA ⑤2, openai.F4→Anthropic ④4). 모두 잣대 비교이고 현재 results 값과 같다.
- **트리거 79건**: research.md 「이전 트리거 처리」 79행의 결론·확인 내용이 triggers.json 과 전부 같다. finding 이 인용한 매체+날짜 쌍을 후보 제목과 대조해 모두 찾았다(표기 차이 1건, 날짜 차이 1건은 발견 13). 숫자(464,391대·486,532대·13.7GWh·$518B·$664B·$42B·$8B·$30B·$84.5B·$920M·19개 중 13개·$100B/$2T mezha)도 후보 제목에 있다. 기업별 공시 목록(2026-09-02~10-06)도 각 finding 의 서술과 맞다. 0건 주장은 OpenRouter·Baltra·iOS 27·new Siri·SDLLMTK·CDS·credit default·interconnect 를 재현했고 Cursor 는 틀렸다(발견 3). finding 이 '본문 미열람'이라 적은 8-K 4건은 `sec-get` 으로 받아 확인했다. NVIDIA 2026-09-03 은 Hugging Face 확정 계약($11.9B, 2027 상반기 종결)이라 finding 의 추정과 맞다. Microsoft 2026-09-02 는 FY27 부문 변경이라 맞다. Oracle 2026-09-14 는 Ellison 의 10b5-1 매도 계획 취소라 TRG-022 조건과 무관하다. Amazon 2026-09-14 는 파운드화 회사채 발행 완료다(발견 8).
- **URL**: Google News 출처 163건은 수집 원문 RSS(raw_ref)에 URL 이 그대로 있다. EDGAR 공시 출처 26건은 원문 submissions JSON 에서 접수번호와 주문서명이 모두 확인된다. 새 SEC 출처 8건은 `data/_sec/docs` 캐시의 sha256 이 출처 장부와 같다. Oracle 10-K(SRC-SEC-ORCL-10K-FY2026)는 캐시 index 에 항목이 없어 오늘 `scorecard_cli.py sec-get` 으로 다시 받았고, sha256 517287f8… 이 장부와 같다(발견 12). url=null 은 6건이고 내부 기준선 4건과 재수집 금지 보도자료 2건이다. note 에 사유가 있다. SEC 요청은 sec-get 으로만 했다(5회). User-Agent 는 직접 만들지 않았다.
- **기준 시점**: 관측 as_of 와 observed_at, 출처 accessed_at 이 모두 기준일(2026-10-06) 이하다. 가격·시총 관측 24건은 2026-10-05(SRC-YF-2026-10-05)로 run.json price_as_of 와 같다.
- **근거 불릿(evidence-editor)**: relevance 는 '추론:' 이나 '사실:/추론:' 표시가 72건 모두 있다. 뉴스 63건은 모두 '제목만' 단서가 있다. conditional_impact·horizon·counter_evidence·unverified·channel 은 빈 칸이 없다. 매수·매도·목표주가·수익 보장·FOMO 같은 금지 표현은 근거와 draft 모두에서 0건이다(draft 1557행은 면책 문구다).

###### 1차 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| medium | triggers.json TRG-057 (baseline/v1.5:TRIG-011) | 사건(Oracle 2026-09-10 실적 8-K, 2026-09-11 10-Q)이 일어났고 수집됐다. 이 10-Q 로 관측을 갱신해 Oracle ⑥ 이 −2→−1 로 움직였다. 그런데 status 가 `expired` 다. guide.md 4.1 과 score-collect 규칙은 "사건이 일어났으면 fired" 이고 expired 는 "기한이 지나 의미가 없어졌다"는 뜻이다. 그래서 research.md 에 「발동 트리거 재검토 대상」 행(Oracle ⑦·⑧)이 없다. ⑦ 문장은 PRP-002 로 이미 고쳐졌고 ⑧ 은 10-Q 에 OpenAI 몫이 없어 유지 이유가 finding 에 있다. | 없음(점수는 관측에서 산출, ⑦⑧ 판정 재료 불변) |
| medium | triggers.json TRG-078 (baseline/v1.5:TRIG-029) | 기준선 항목은 'Optimus 생산 개시 · Starship 페이로드' 둘이다. SpaceX 몫(Starship 페이로드 실측, Flight 14 Starlink 배치, EV-spacex-xai-007)은 사건이 일어났다고 finding 이 스스로 적었다. 그런데 항목 전체를 `withdrawn`(이어받음)으로 닫았다. SpaceX 몫은 fired 로 두고 재검토 표에 "수정하지 않음 — ④ 이미 범위 맨 위, ② 는 비AI 귀속 원칙상 근거 아님" 을 적는 것이 규칙에 맞다(기업별 항목 분리는 guide.md 4.1 이 허용). | 없음 |
| medium | triggers.json TRG-070 (baseline/v1.5:TRIG-027) carry.finding · research.md 999행 | "전 기업 뉴스 후보 2026-04-09~10-06 제목 검색 'Cursor'·'Anysphere' 0건" 이 사실과 다르다. spacex-xai 후보에 4건이 있다. Reuters·CNBC 2026-06-16 'SpaceX locks in $60 billion Cursor deal'·'SpaceX to acquire … Cursor for $60 billion', Reuters 2026-07-07 'SpaceXAI plans to launch new model with Cursor', a16z 2026-08-14 이다. 제목만으로는 '기본 모델 Grok 전환·Claude 비중 축소'가 확인되지 않아 watching 결론 자체는 지킬 수 있다. 다만 부재 주장이 틀렸고 가장 가까운 사건이 빠졌다. | 없음(조건 미충족이면 판단 불변) |
| medium | judgments.json oracle.F9 · oracle.F7.fix52 · alibaba.F9.obsreg25 · tsmc.F9 (PRP-001~004) | 근거 문장을 새 SEC 원문 기반 숫자(2026-08-31·2026-06-30)로 바꿨다. 그런데 `source_ids` 는 [SRC-v15-html(·rule·md)] 그대로이고 새 출처 8건(SRC-SEC-FACTS-ORCL-20261006, SRC-SEC-ORCL-10K-FY2026, SRC-SEC-TSM-6K-*, SRC-SEC-BABA-6K-*)이 판단 단위에서 이어지지 않는다. 숫자 자체는 관측(rs1006)과 맞아 관측 경유로는 추적된다. alibaba 문장만 관측 ID 를 적는다. | 없음 |
| low | judgments.json alibaba.F9.obsreg25 · draft.md 802행 | 취소선 줄의 "(superseded … 이번 실행 점수는 -3)" 이 낡았다. 이번 실행 알리바바 ⑨ 는 −4 다(같은 판단 다음 줄과 results). | 없음 |
| low | judgments.json amazon.F9.obsreg25 (status new) | "게이트 4 ✅ 미개시 리스 $106B(매출 0.14배)" 는 v1.5 값이다. 같은 판단의 "미개시 리스만 쓰면 3.615"(496,000/3.615 ≈ $137B)와 B종 $267.3B 와 어긋난다. draft 는 '주의 — 원문 $106B 는 …$267.3B' 로 표시했다. | 없음 |
| low | evidence.json EV-anthropic-010 | title·excerpt 가 "… BBC told - bbc.com" 이다. 후보(raw_ref `data/anthropic/news/google/raw/20261006T054442Z-d3679f8b.xml`)와 출처 장부 제목은 "… BBC told - BBC" 다. excerpt 는 더 이른 수집본(043405Z·043614Z)의 표기와 같다. 본문 문언은 같고 매체 꼬리표만 다르다. | 없음 |
| low | triggers.json TRG-005 carry.finding | 2026-09-14 아마존 8-K 를 '본문 미열람' 으로 두고 회사채 발행을 '계획 단계' 로만 적었다. sec-get 으로 확인해 보니 Item 8.01 은 £4.25B 회사채 발행 완료(순조달 약 £4.235B)다. 조건(3분기 10-Q)과 ⑨ G3 통과(런웨이 9.95년)에는 영향이 없다. | 없음 |
| low | evidence.json EV-apple-005 relevance · TRG-057 finding | 이전 실행 근거 EV-apple-003·EV-oracle-002 를 인용한다. 이번 evidence.json 에는 없다(이전 확정 91건 중 38건만 이어받음). TRG-055·079 note 는 같은 사정을 밝혔고 EV-apple-005 는 밝히지 않았다. | 없음 |
| low | observations.json oracle.net_cash.rs1006 성분 operating_lease·finance_lease location | "10-Q 주석 6 p.13 `Total operating lease liabilities` (유동 4,027 + 비유동 30,594)" 로 적었는데, 그 줄은 p.12 보조 재무상태표에 있다. p.13 에 있는 것은 만기표의 `Total lease liability $34,621 $9,185` 다. 값은 같다. | 없음 |
| low | observations.json oracle.undrawn_credit.rs1006 basis.search.hit_counts_10k | 'revolv' 26건이라 적었으나 재현하면 35건이다(나머지 키워드 건수는 일치). 결론(약정 1건 $10.0B)은 같다. | 없음 |
| low | data/_sec/docs/index.json | SRC-SEC-ORCL-10K-FY2026 캐시 파일은 있는데 index 에 항목이 없었다(동시 기록 경합으로 보임). 오늘 sec-get 으로 다시 받아 항목이 생겼고 sha256 이 장부와 같다. | 없음 |
| low | triggers.json TRG-006 · TRG-010·011·012·056 | TRG-006 "qz 2026-10-06" 은 후보 발행이 2026-10-05T19:35Z 다. 메타 항목들의 "메타 뉴스 2026-09-03~10-06 303건" 은 후보 news 307건이다. | 없음 |
| low | preview.md 「이전 실행 대비」 | 알리바바 ⑨ −3→−4 의 원인이 "✍️ 판단 수정" 으로 적혀 있다. PRP-003 은 근거 문장만 바꿨고 gate_inputs 는 그대로다. 실제 원인은 관측 갱신(FCF·현금)이다. | 없음 |
| low | judgments.json oracle.F7.fix52 · oracle.F9 | 갱신된 2026-08-31 숫자 옆에 v1.5 값이 표시 없이 남아 있다. oracle.F7 의 '자체 부채 $167B'(현재 차입 $125.3B + 리스 $43.8B), oracle.F9 의 'Debt/EBITDA 5.03·이자보상 4.87·Altman Z 2.18' 이다. 게이트 입력은 아니다. | 없음 |

###### 1차 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 이해당사자 출처를 확정 사실로 쓰지 않았다. 벤더 발표 벤치마크(Gemini 4 Argon '19개 중 13개', NVIDIA 블로그의 Astra 가속, Microsoft 음성 모델)는 TRG-001·009·040·066 에서 방증으로만 다뤘다. 회사 주장('중국에서 가장 강력한')은 EV-alibaba-007 counter_evidence 에 적혔다. 출처 장부의 `conflict_of_interest` 표기는 AGENTS.md 「금지·주의」(2026-10-02)에 따라 점검하지 않았다. |
| Q09 | pass | 계획·발표는 점수 입력에 없다. 아마존 $42B 회사채 추진·$8B 칩 매각 추진(TRG-005), 알리바바 8월 증자(완충 제외, alibaba.F9), Anthropic 상장 목표(TRG-036), 테슬라 Optimus 계획(TRG-030)이 그렇다. 기준일 뒤 사건은 관측에 없다. Oracle 미인출 여신은 10-K 기준일 값이고 mixed_as_of 로 표시했다. 승계 문면의 계획 문장(oracle.F9 '$45~50B 추가 조달 예정', tsmc.F9 capex 가이던스)은 gate_inputs 에 닿지 않는다. |
| Q14 | pass | 진행 중인 사건은 끝난 것으로 세지 않았다. Anthropic S-1·상장, Hugging Face 종결(8-K 원문은 2027 상반기 종결 예정), OpenAI $30B 라운드, EU 표결, 영국 Palantir 계약은 모두 watching 이다. 알리바바 G4 는 '모름' 이 아니라 원문으로 확인한 미공시만 C-16 으로 보냈다. |
| Q23 | pass | 사실·출처 관점에서 서로 다른 하네스의 벤치마크 비교를 근거로 쓴 곳이 없다. TRG-040 은 같은 하네스 독립 측정을 조건으로 두고, 벤더 수치는 조건 미충족으로 처리했다. |

###### 1차 다음 실행 과제
1. (medium, 승인 전 고칠 만함) TRG-057 을 `fired` 로 바꾸고 「발동 트리거 재검토 대상」에 Oracle ⑦(PRP-002 로 근거 문장만 갱신)과 ⑧(10-Q 에 OpenAI 몫·고객 집중 서술 0건이라 수정하지 않음) 행을 넣는다.
2. (medium, 승인 전 고칠 만함) TRG-078 을 기업별로 나눈다. SpaceX 몫(Starship 페이로드 실측)은 `fired` + "수정하지 않음" 사유로 두고, 테슬라 몫(Optimus)은 TRG-030 으로 철회한다.
3. (medium, 승인 전 고칠 만함) TRG-070 finding 의 'Cursor 0건' 을 고친다. 2026-06-16 SpaceX 의 Cursor 인수($60B), 2026-07-07 'SpaceXAI·Cursor 새 모델 출시' 보도를 적고, 제목으로는 기본 모델 전환·Claude 비중 축소가 확인되지 않아 watching 을 유지한다고 적는다. 가능하면 Reuters 07-07 본문을 열어 전환 여부를 확인한다.
4. (medium) PRP 판단 네 건의 `source_ids` 에 새 SEC 출처를 더하는 판단 변경 제안을 올린다(사람 반영 필요). Oracle·TSMC 문장에 쓴 관측 ID(rs1006)를 alibaba 처럼 적는다.
5. (low) alibaba.F9.obsreg25 취소선 줄의 "이번 실행 점수는 -3" 과 amazon.F9.obsreg25 의 "미개시 리스 $106B" 를 현재 값과 맞추거나 v1.5 문면으로 표시한다. oracle.F7·F9 의 v1.5 수치($167B, Debt/EBITDA 등)에도 표시를 붙인다.
6. (low) EV-anthropic-010 의 title·excerpt 를 raw_ref 원문 표기("- BBC")로 맞춘다. 다음 선별부터 excerpt 를 raw_ref 의 제목에서 기계로 복사한다.
7. (low) '본문 미열람' 공시는 sec-get 으로 열어 finding 에 적는다. 이번에 열어 본 결과는 Amazon 09-14(파운드화 회사채 발행 완료), NVIDIA 09-03(HF 확정 계약), Microsoft 09-02(부문 변경), Oracle 09-14(Ellison 매도 계획 취소)다. TRG-005 finding 에 회사채 발행 완료 사실을 더한다.
8. (low) 이어받지 않은 이전 근거(EV-apple-003·EV-oracle-002 등)를 인용하는 문장은 출처 ID 로 바꾸거나 그 사실을 적는다.
9. (low) oracle.net_cash.rs1006 리스 성분 위치를 p.12 로 고치고, oracle.undrawn_credit 의 'revolv' 건수(26→35)를 다시 센다. sec-get 캐시 index 의 동시 기록 경합을 막는다(index 에 빠진 파일이 있었다).
10. (low) preview 의 변동 원인 분류가 '판단 수정' 을 gate_inputs·score 변경으로만 세게 한다. 근거 문장만 바꾼 제안은 원인으로 세지 않는다.
11. (low) 트리거 finding 의 날짜·건수 표기(TRG-006 qz 날짜, 메타 303건)를 후보 기준으로 맞춘다.
