---
slug: ai-scorecard-2026-09-baseline
report_type: ai_scorecard
topic: AI 기업 9-factor 채점표 — v1.5 기준선 재계산
request: AI 기업 14개사 9-factor 채점표를 framework 로 재계산하고 규칙·자료·판단의 일관성을 검증한다
output_type: scorecard
audience: intermediate
run_id: ai-scorecard-2026-09-baseline
as_of: 2026-09-02
price_as_of: 2026-09-02
info_cutoff: 2026-09-02
rule_version: v1.5
rule_hash: 9231b3a05ba5c7661dbc91190c66bcf73ab3617643e274698a2690c4b16de6ba
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
created_at: 2026-09-08
assumptions:
  - 원자료와 정성 판단은 기준선 v1.5(2026-09-02)에서 승계했으며 이번 실행에서 재검증되지 않았다(legacy_unverified)
  - 미결 규칙 결정(C-xx)은 run.json.decisions 에 명시된 것만 적용한다
  - 가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)
---
# Planning Brief — AI 기업 9-factor 채점표 — v1.5 기준선 재계산

## 요청 해석

- 대상: AI 기업 14개사 9-factor 채점 (`report_type: ai_scorecard`)
- 요청 원문: AI 기업 14개사 9-factor 채점표를 framework 로 재계산하고 규칙·자료·판단의 일관성을 검증한다
- 산출물: `research/`·`drafts/`·`reviews/`·`output/ai-scorecard-2026-09-baseline.html`·`scorecard/history.csv`
- 흐름: plan → research → calculate → draft → review → awaiting_user → build

## 분석 목적과 기준 시점

- 목적: v1.5 기준선을 승계해 자동 산출 factor 를 재계산하고 미결 규칙 결정을 드러낸다
- 분석 기준일 `as_of` 2026-09-02 · 가격 기준일 2026-09-02 · 정보 컷오프 2026-09-02 (C-17: 셋을 분리 기록)
- 규칙 `v1.5` (해시 `9231b3a05ba5c766…`) — 실행 중 규칙이 바뀌어도 이 실행은 이 해시를 유지한다

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
| spacex-xai | SpaceX + xAI | 소비자·업무 | 상장 | SpaceX + xAI 합산 평가 범위. Tesla 와는 분리(관계사). 2026-06 상장 기록이나 티커·거래소는 원문에 없어 미확인 |
| tesla | Tesla | 소비자 | 상장 | Tesla 연결 (SpaceX 관계사 자산은 자체 자산으로 세지 않음) |
| oracle | Oracle | 업무 | 상장 | Oracle 연결 |
| openai | OpenAI | 소비자 | 비상장 | OpenAI 비상장 |

## 규칙 버전과 자동화 범위

| Factor | 자동화 모드 | 범위 | 관련 결정 |
| --- | --- | --- | --- |
| ① 네트워크 | manual | 0~5 | — |
| ② 게임체인저 | paths | 0~5 | C-03 |
| ③ Last Mover | ladder | 1~5 | — |
| ④ 호황 이후 | manual | 0~5 | — |
| ⑤ 아군 | formula | 0~5 | — |
| ⑥ 가격 | per_band | -5~0 | C-12, C-13 |
| ⑦ 순환금융 | matrix | -3~0 | C-09 |
| ⑧ 비대칭 의존 | manual | -5~0 | — |
| ⑨ 적자 깊이 | gates | -5~0 | C-04, C-05, C-06, C-07, C-16 |

- 정성 판정(등급·경로·분류)은 사람이 입력하고 산식·사다리·구간 적용은 프로그램이 한다(D-03). 모르는 값은 0으로 치환하지 않는다(D-04).

## 기준선

- 기준선 `v1.5` (2026-09-02, HTML `fa66076cbcd6…`)의 점수·판정표·원자료를 승계
- 승계된 판단은 원검토일과 이번 실행 재검토 여부를 함께 표시한다. 기준선 점수는 새로 검증된 사실이 아니다(D-08).

## 미결 규칙 결정

| ID | 요약 | 영향 factor | 이번 실행 선택 |
| --- | --- | --- | --- |
| C-03 | F2 경로 수→점수 매핑(0→2, 1→3, 2→4, AA 1위→5)이 완결되지 않았고 NVIDIA·TSMC 5점을 재현하지 못함 | F2 | 미결 |
| C-05 | G1 실패 뒤 G3·G4 를 추가 감점하는지 진단만 하는지 원문이 혼재 | F9 | 미결 |
| C-06 | 손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. BEP 후퇴→-5 는 원문 OR 조건 그대로 활성(경고 표시)이며 손실률 경계와의 우선순위 명문화만 미결 | F9 | 미결 |
| C-13 | TSMC·Alibaba 는 연간 EPS 가중 근사를 NTM 으로 사용. 신규 계약은 정확한 4분기만 허용 | F6 | 미결 |
| C-16 | G4 판정 불가→하향 규칙과 Alibaba·SpaceX 보류 유지 사례가 다름 | F9 | 미결 |

- 미결 결정이 걸린 factor 는 `needs_rule_decision` 으로 남고 해당 기업은 공식 순위에서 제외된다. 실행 단위 선택은 `scorecard/runs/ai-scorecard-2026-09-baseline/run.json` 의 `decisions` 에 근거·결정자와 함께 기록한다.

## 리뷰 기준

- 4개 검토 영역: 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 (설계 지침 10.1)
- 체크리스트 Q01~Q23 각 항목 pass / fail / not_applicable + 근거
- `python scripts/validate_report_contract.py ai-scorecard-2026-09-baseline` 통과

## 완료/차단 조건

완료는 results.json 결정론 검증 통과, draft 와 review pass, 사용자 승인(approval.json) 해시 일치, HTML·history.csv 생성이다.

기업이 순위에 못 들어가는 사유는 factor 상태로 구분한다. 규칙 결정이 없으면 `needs_rule_decision`, 사람의 판정이 없으면 `needs_judgment`, 관측이 없거나 수집·파싱에 실패했으면 `pending_data` 다. 셋 다 0점으로 채우지 않고 공식 순위에서만 제외한다.

`awaiting_user` 는 이 셋과 다르다. 리뷰가 pass 이고 계산이 끝났는데 사용자 승인이 없거나, 승인 뒤 규칙·자료·판단·결과·초안 중 하나가 바뀌어 승인이 무효가 된 상태를 가리키며 build 단계에서만 나온다.
