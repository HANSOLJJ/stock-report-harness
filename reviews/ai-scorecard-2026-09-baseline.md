---
slug: ai-scorecard-2026-09-baseline
report_type: ai_scorecard
status: pass
created_at: 2026-09-08
plan_source: plan/ai-scorecard-2026-09-baseline.md
research_source: research/ai-scorecard-2026-09-baseline.md
draft_source: drafts/ai-scorecard-2026-09-baseline.md
results_hash: 0942c342f010781ea41f2cec51a5082c5f5f58cdfe76078bb7c3e5b29bbffec0
draft_hash: 574841bc7c26f225fc34704e0182ba81c1b51e93fb03874b86515c0f846fdd8b
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: pass (fact-checker 서브에이전트 (별도 세션, 1차·2차))"
  - "financial-calc: pass (general-purpose 서브에이전트 (별도 세션, 1차·2차))"
  - "rule-consistency: pass (general-purpose 서브에이전트 (별도 세션, 1차·2차))"
  - "output-readability: pass (report-designer 서브에이전트 (별도 세션, 1차) + 수정 검증은 main 세션 Playwright 실측)"
---
# 리뷰 — AI 기업 9-factor 채점표 — v1.5 기준선 재계산

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장·이해상충 | fact-checker 서브에이전트 (별도 세션, 1차·2차) | pass | 1차 finding 11건 중 high 1·medium 5·low 3 을 2차에서 해소 확인, 잔여 low 2건도 이후 반영 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | general-purpose 서브에이전트 (별도 세션, 1차·2차) | pass | ⑥ 구간·경계와 ⑨ 게이트 경로·합산·순위·단위를 원자료와 대조해 일치하고 재계산 해시가 저장값과 같음. 2차 지적 2건도 반영 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | general-purpose 서브에이전트 (별도 세션, 1차·2차) | pass | 1차 지적 9건 반영 확인, 14사 판정 입력과 완료 9사 조정총점이 원본 규칙·판정표를 그대로 재현 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer 서브에이전트 (별도 세션, 1차) + 수정 검증은 main 세션 Playwright 실측 | pass | 1차 지적 7건 반영 후 320·768·769·1280px 가로 넘침 0, 탭 대상 위반 0, 승계 배지·scope·버블 크기 확인 |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | Alibaba 지정학은 ⑧에만, Oracle 선투자는 ⑧⑨·별표 J, NVIDIA 우발 보증은 ⑦에만. 비상장 미공시 중복은 calc_f9 가 reason_id 로 차단 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | ⑥ 점수는 NTM PER 만 사용(P/S·시총·TTM 은 참고), ①은 별표 A 채널 지표로 판정. Tesla G2 근거는 원문 선택이며 C-06 대상으로 기록 |
| Q03 | 회사마다 같은 잣대인가? | pass | 완료 9사 동일 구간·산식·게이트. 단일 분기 흑자는 Anthropic·Alibaba 모두 unknown(C-20)으로 통일, G4 결측은 수집 실패·판단 대기·미공시로 유형 분리해 수집 실패가 감점되지 않음 |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | NVIDIA ⑥0 은 NTM PER 18.0 구간 산출이고 시총 $5.42T·P/S 17.9 는 calc 참고 필드에만 존재 |
| Q05 | 출처가 이해당사자인가? | pass | 개요와 References 에 작성자 이해상충(Claude=Anthropic, 긴장 #4·#11) 고지. 점수 근거에 이해당사자 출처를 1차 근거로 쓴 곳 없음 |
| Q06 | 볼륨인가 가치인가? | pass | Anthropic ① 토큰 12%·매출 46%, OpenAI ① 토큰 9.8%·매출 8.0% 등 볼륨이 아니라 가치로 판정 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | Amazon·Apple ③ 모방불가 fail — 모델을 안 만든 것 자체를 카운터 포지셔닝으로 세지 않음 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | Apple H=-1(비용형), NVIDIA H=-2(고객이 곧 경쟁자), Palantir H=-2(정당성 표적), OpenAI H=-3(다발형) — 별표 G 유형 기준 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Apple ③ 가속도 fail(2년 지연), Anthropic ④4(2028 칩은 계획), NVIDIA HF 인수는 클로징 전 불인정 |
| Q10 | 거리를 가속도로 착각했나? | pass | Alphabet·Anthropic ③ 근거가 누적 성과를 이동 거리로 명시해 가속도에서 배제 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | OpenAI·SpaceX·Anthropic 모두 순적자로 실격되지 않고 ⑨ 4단계 게이트로 판정. SpaceX 근거에 아마존 효과 명시 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | rules F3 requires_imitation_pass 로 Alibaba·SpaceX 통과점 2.5 를 3 으로 상한. 14사 통과점과 점수가 원본 판정표와 일치 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | Alibaba ③ 모방불가 partial 근거가 오픈웨이트 회수 장치 부재, Meta 는 광고가 받치는 저가 API 를 회수 장치로 구분 |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 14사 door_closed 전부 fail 이고 F3 5점 없음. score5_requires_door_closed 로 문 닫힘 증거 없이는 5 를 주지 않음 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | NVIDIA 개발자 1,800만·Alibaba 파생모델 15만·Meta Glimmer 개발자를 공짜 사용자로 배제하고 A 등급은 상업적 약속으로만 판정 |
| Q16 | ①을 한 채널로만 쟀나? | pass | OpenAI·Anthropic·SpaceX 모두 실질 채널 전체를 보고 가장 강한 락인으로 판정. 부품형 상한 2 는 계산기가 검사 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | Alibaba ②4 는 표준 부재와 프론티어 미달 복합 근거, Oracle ②2 는 세 경로 전부 미통과. 표준 없음만으로 깎은 곳 없음 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla A=0(유일 아군이 관계사 SpaceX), Tesla ③ 모방불가 fail(Starlink V5 는 SpaceX 조달품) |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | OpenAI A+2 는 Stargate JV 지분·Broadcom 공동개발 등 능동 동맹으로 판정하고 Oracle 계약은 조달로 배제. 원문 별표 G·H 긴장은 rules C-08 요약에 기록 |
| Q20 | 조달을 동맹으로 셌나? | pass | Apple Gemini·TSMC 칩, Meta 멀티벤더, OpenAI→Oracle 을 조달로 처리. NVIDIA Nemotron 연합만 별표 H 통과로 동맹 인정 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | Anthropic 3사 관계를 ⑤ 연동과 ⑧ 대체 불가로 갈라 세고 같은 속성을 양쪽에 넣지 않음 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | Alphabet ⑦ 근거가 평가익을 ⑥ 소관으로 넘기고, calc_f6 가 영업외 30% 이상에 TTM PER 참고 무효 경고. C-11 의 ⑦ 이월 문구 없음 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | not_applicable | 이번 실행은 기준선 승계 재계산이라 벤치마크 신규 비교가 없고 F2 는 14사 전부 승계(C-03). 초안의 벤치마크 문장은 과거 기록 표시가 붙은 원문이며 하네스 비교 가능성을 이번 실행에서 재검증하지 않음 |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- [해소] 사실·출처 high — 이해상충 고지 부재: 개요와 References 에 작성자 Claude=Anthropic 고지와 출처별 sha256 을 추가했다.
- [해소] 사실·출처 medium — 시총 출처 혼입: HTML D.cap 표시용 시총 관측 14건을 이관에서 제거해 3-1a(VAL) 값만 남기고, schema 가 같은 기업·지표·시점의 값 충돌을 거부한다. import-report 불일치 절에 기록.
- [해소] 사실·출처 medium — 트리거 TRIG-019 본문 절단: 표의 문자열 슬라이싱을 제거해 전문을 싣는다.
- [해소] 사실·출처 medium — 기준 시점 미분리(C-17): frontmatter 에 price_as_of·info_cutoff 를 넣고 개요에 컷오프 이후 사건 포함 사실을 적었다.
- [해소] 사실·출처 medium — 과점 최고·후보군 오귀속: 과점이 완결된 전 기업 기준으로 집계하고 미완료 기업에 꼬리표를 붙였다.
- [해소] 사실·출처 medium — 원자료 상태 미표기: 표 머리말에 legacy_unverified 건수와 ADR·ADS 기준을 적고, 부재는 원문 상태(미공시·적자·∞·판정 불가)를 그대로 출력한다.
- [해소] 규칙 일관성 medium — 자동 산출 factor 에 승계 헤더: 승계 판단과 자동 산출을 근거 헤더로 구분한다.
- [해소] 규칙 일관성 medium — G4 결측 유형 미구분: coverage_comparable 미확인은 판단 대기, 범위 불일치는 자료 대기(C-07), 수집·파싱 실패는 자료 대기, 확인된 미공시만 C-16 정책 대상으로 분리했다.
- [해소] 규칙 일관성 medium — Alibaba G1 잣대 불일치: 단일 분기 흑자를 Anthropic 과 같이 TTM 부호 unknown(C-20)으로 통일해 ⑨가 자료 대기로 바뀌었다.
- [해소] 출력·가독성 high — 카드 요약의 낡은 비교 숫자: 요약문 앞에 기준선 과거 기록 배지를 붙이고 factor 행에 승계·자동 산출 라벨을 넣었다.
- [해소] 출력·가독성 medium — KPI 과점 집계 충돌: 과점이 완결된 전 기업 기준으로 바꾸고 함정 최심에 완료 기업 수를 한정어로 붙였다.
- [해소] 재무 계산 medium — G1 실패 뒤 현금 관측 부재 시 런웨이 진단 무음 생략: 경로에 기록하고 C-05 가 diagnose_only 가 아니면 자료 대기로 멈춘다.
- [해소] 재무 계산 low — 영업이익률 0, 음수 지출 지표, 중복 관측, 런웨이 표시값 불일치를 각각 규칙 대기·스키마 거부·계산값 우선으로 처리했다.
- [잔여 low] scorecard/baseline/v1.5/import-report.md 의 시총 상이 항목은 불일치 절로 옮겼으나, 같은 내용이 분류 절에도 남아 중복 서술이다. 추적에는 영향이 없다.
- [해소] 재무 계산 2차 medium — G1 실패 뒤 TTM FCF 관측 자체가 없거나 수집 실패면 런웨이 진단이 무음 생략되던 경로: 소진율·완충 어느 쪽이 없어도 경로에 기록하고 자료 대기로 멈춘다(회귀 테스트 추가).
- [해소] 재무 계산 2차 low — 산점도 범례가 비상장 post-money 를 시총으로 부르던 문구: '원 크기 = 시총(비상장은 최근 post-money)' 로 고쳤다.
- [검토 수행 위치] 사실·출처·재무 계산·규칙 일관성은 1차·2차 모두 별도 서브에이전트 세션에서 수행했다. 출력·가독성은 1차를 별도 세션에서 needs_fix 로 받았고 지적 7건의 수정 검증은 main 세션의 Playwright 실측(320·768·769·1280px 넘침 0, 탭 대상 위반 0, 승계 배지 14개, th scope 55/55, 산점도 버블 크기 차등)으로 확인했다. 해당 영역의 2차 서브에이전트 재검증은 세션 사용량 한도로 중단됐으며 결과가 도착하면 이 파일에 반영한다.

## 판정

- results_hash `0942c342f010781e…` · draft_hash `574841bc7c26f225…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- 완료 9개사만 공식 순위에 포함하고 미완료 5개사(Amazon 판단 대기, TSMC·Alibaba C-13, Alibaba·Anthropic 자료 대기, SpaceX C-06)는 0점으로 채우지 않고 제외했다.
- 미결 규칙 결정 C-06·C-13 이 남아 있으며 승인은 이 상태를 알고 내리는 것이다. 결정을 내리면 run.json 의 decisions 에 근거와 함께 기록하고 다시 계산한다.
- 설계진행 검증 담당(Codex)의 독립 재현 R01~R06 10건과 저장소 테스트 31건이 통과한 상태다.
