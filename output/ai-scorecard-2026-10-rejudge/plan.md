---
slug: ai-scorecard-2026-10-rejudge
report_type: ai_scorecard
topic: 2026-10 전부 재판단(v2.0)
request: 규칙 v2.0 으로 정성 판단 일곱 항목을 14개사 전부 다시 매긴다
output_type: scorecard
audience: intermediate
run_id: ai-scorecard-2026-10-rejudge
as_of: 2026-10-08
price_as_of: 2026-10-07
info_cutoff: 2026-10-08
rule_version: v2.0
rule_hash: 3bf9418cf3eb43f9b91152f7e11249808658d80d4944c15222217b72b4be3cc5
baseline_id: v1.5
companies:
  - alphabet
  - amazon
  - meta
  - microsoft
  - tsmc
  - alibaba
  - anthropic
  - apple
  - nvidia
  - palantir
  - spacex-xai
  - tesla
  - oracle
  - openai
created_at: 2026-10-08
assumptions:
  - 이전 실행 ai-scorecard-2026-10-rescore 의 관측·판단·출처를 그대로 이어받았다(observations 65ea6a0b225d…, judgments f319cc78cdef…). 이어받은 항목은 이번 실행에서 재검증되지 않았다
  - 이번 실행은 기업을 더하지 않았고 이전 실행의 입력을 그대로 쓴다
  - 가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)
  - 규칙이 이어받은 실행 이후 바뀌었다(0e4122094968… → 3bf9418cf3eb…) — 기존 기업 점수 불변은 diff 로 확인한다
---
# Planning Brief — 2026-10 전부 재판단(v2.0)

## 요청 해석

- 대상: AI 기업 14개사 9-factor 채점 (`report_type: ai_scorecard`)
- 요청 원문: 규칙 v2.0 으로 정성 판단 일곱 항목을 14개사 전부 다시 매긴다
- 산출물: `output/ai-scorecard-2026-10-rejudge/` 묶음(research.md·draft.md·review.md·report.html·audit.md)·`scorecard/history.csv`
- 흐름: plan → collect → research → calculate → draft → review → awaiting_user → build

## 분석 목적과 기준 시점

- 목적: 정기 실행 전부 재판단 원칙(rules.md 2.9)의 첫 적용. ① 네 질문, ② 세 경로, ③ 지표 단계를 처음으로 입력한다
- 분석 기준일 `as_of` 2026-10-08 · 가격 기준일 2026-10-07 · 정보 컷오프 2026-10-08 (C-17: 셋을 분리 기록)
- 규칙 `v2.0` (해시 `3bf9418cf3eb43f9…`) — 실행 중 규칙이 바뀌어도 이 실행은 이 해시를 유지한다

## 대상 기업과 연결 범위

| company_id | 표시명 | 유형 | 상장 | 평가 범위 |
| --- | --- | --- | --- | --- |
| alphabet | Alphabet / Google | 소비자 | 상장 | Alphabet 연결 |
| amazon | Amazon / AWS | 소비자·업무 | 상장 | Amazon 연결 |
| meta | Meta | 소비자 | 상장 | Meta 연결 |
| microsoft | Microsoft | 업무 | 상장 | Microsoft 연결 |
| tsmc | TSMC | 부품 | 상장 | TSMC 연결 (ADR 1주 = 보통주 5주, 재무 TWD) |
| alibaba | Alibaba | 소비자 | 상장 | Alibaba 연결 (ADS, 재무 CNY — EPS 통화 혼재 주의) |
| anthropic | Anthropic | 업무 | 비상장 | Anthropic 비상장 (2026-10 IPO 예상은 사실 확인 전까지 반영하지 않음) |
| apple | Apple | 소비자 | 상장 | Apple 연결 |
| nvidia | NVIDIA | 부품 | 상장 | NVIDIA 연결 |
| palantir | Palantir | 업무 | 상장 | Palantir 연결 |
| spacex-xai | SpaceX + xAI | 소비자·업무 | 상장 | SpaceX 단일 법인 연결 범위. 2026-06-12 SPCX 로 NASDAQ 상장(USD·보통주). xAI 는 주식교환으로 흡수된 SpaceX 내부 사업이며 별도 채점 대상이 아니다(Grok·Colossus·AI 세그먼트 매출·xAI DC capex 는 SpaceX 항목). Tesla 와는 분리(관계사) |
| tesla | Tesla | 소비자 | 상장 | Tesla 연결 (SpaceX 관계사 자산은 자체 자산으로 세지 않음) |
| oracle | Oracle | 업무 | 상장 | Oracle 연결 |
| openai | OpenAI | 소비자 | 비상장 | OpenAI 비상장 |

## 규칙 버전과 자동화 범위

| Factor | 자동화 모드 | 범위 | 관련 결정 |
| --- | --- | --- | --- |
| ① 락인 | lockin | 0~5 | — |
| ② 게임체인저 | paths | 2~5 | C-03 |
| ③ Last Mover | ladder | 1~5 | — |
| ④ 호황 이후 | manual | 0~5 | — |
| ⑤ 아군 | formula | 0~5 | — |
| ⑥ 가격 | parameters | -7~0 | C-12 |
| ⑦ 순환금융 | matrix | -2~0 | C-09 |
| ⑧ 비대칭 의존 | manual | -5~0 | — |
| ⑨ 적자 깊이 | gates | -4~0 | C-04, C-05, C-06, C-07, C-16 |

- 정성 판정(등급·경로·분류)은 사람이 입력하고 산식·사다리·구간 적용은 프로그램이 한다(D-03). 모르는 값은 0으로 치환하지 않는다(D-04).

## 기준선

- 이전 실행 `ai-scorecard-2026-10-rescore`(as_of 2026-10-06)의 관측 441건·판단 114건·출처 476건을 이어받았고, 점수 비교 기준선은 `v1.5` 를 유지한다. 판단·트리거가 인용한 근거 56건과 트리거 80건도 옮겼다
- 승계된 판단은 원검토일과 이번 실행 재검토 여부를 함께 표시한다. 기준선 점수는 새로 검증된 사실이 아니다(D-08).

## 미결 규칙 결정

| ID | 요약 | 영향 factor | 이번 실행 선택 |
| --- | --- | --- | --- |
| C-05 | G1 실패 뒤 G3·G4 를 추가 감점하는지 진단만 하는지 원문이 혼재 | F9 | apply |
| C-06 | 손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. [FIX-63 정정 · obsreg 9차 재무 계산 재판정 2회(Claude 독립 세션) medium] **BEP 후퇴의 우선순위는 미결이 아니다.** 사용자 결정 2026-09-17(C-29)로 `policies.f9.g1_bep_retreat_precedence` 에 명문화했다 — **C-20 비상장 경로가 먼저 서고**, 상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 **G1 통과·손실률 밴드 둘 다보다 앞서** `g1_bep_retreat_score` 를 준다. 점수도 -5 가 아니라 **-4** 다(C-06 재척도). **그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 다른 값이 나오고, **영업흑자여도 통과하지 못하고 하한을 받는다**(TEN-RA6-01). 남은 미결은 FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다 | F9 | proposed_v15_boundaries |
| C-16 | G4 판정 불가→하향 규칙과 Alibaba·SpaceX 보류 유지 사례가 다름 | F9 | downgrade |

- 미결 결정이 걸린 factor 는 `needs_rule_decision` 으로 남고 해당 기업은 공식 순위에서 제외된다. 실행 단위 선택은 `output/ai-scorecard-2026-10-rejudge/run.json` 의 `decisions` 에 근거·결정자와 함께 기록한다.

## 리뷰 기준

- 4개 검토 영역: 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 (설계 지침 10.1)
- 체크리스트 Q01~Q23 각 항목 pass / fail / not_applicable + 근거
- `uv run --frozen python -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-10-rejudge` 통과

## 완료/차단 조건

완료는 results.json 결정론 검증 통과, draft 와 review pass, 사용자 승인(approval.json) 해시 일치, HTML·history.csv 생성이다.

기업이 순위에 못 들어가는 사유는 factor 상태로 구분한다. 규칙 결정이 없으면 `needs_rule_decision`, 사람의 판정이 없으면 `needs_judgment`, 관측이 없거나 수집·파싱에 실패했으면 `pending_data` 다. 셋 다 0점으로 채우지 않고 공식 순위에서만 제외한다.

`awaiting_user` 는 이 셋과 다르다. 리뷰가 pass 이고 계산이 끝났는데 사용자 승인이 없거나, 승인 뒤 규칙·자료·판단·결과·초안 중 하나가 바뀌어 승인이 무효가 된 상태를 가리키며 build 단계에서만 나온다.
