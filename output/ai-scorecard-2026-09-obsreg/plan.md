---
slug: ai-scorecard-2026-09-obsreg
report_type: ai_scorecard
topic: AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)
request: OBS-REG-25 + F6-REG-28 + PRIV-IMPL-31 + SCOPE-34 + CASH-FCF-35
output_type: scorecard
audience: intermediate
run_id: ai-scorecard-2026-09-obsreg
as_of: 2026-09-02
price_as_of: 2026-09-02
info_cutoff: 2026-09-02
rule_version: v1.7
rule_hash: 345c3353372d0f95d98eef5ed918c31e7a3f7878185a24f1e4edfa9870d58d21
rule_hash_history:
  - hash: 64fb45557c9d40eb0ca9bfd3ed9e18cc53e6ff064dba43458bca25be2744d926
    pinned_at: 2026-09-11
    by: init
    note: 실행 생성 시점 규칙 해시. 규칙 커밋 `3b90fde`(CASH-FCF-35) 시점 파일이다.
  - hash: 2fc704bff291655c3b96f0b9f49a510ea6e9c32868bdadae1397c5f629a6368d
    pinned_at: 2026-09-17
    by: FIX-60 (설계진행 지시 · 사용자 결정 2026-09-17)
    note: >-
      이 실행은 2026-09-11 에 시작해 리뷰 8라운드 동안 FIX-52~59 로 규칙을 고쳐 왔고 그때마다 run.json 의
      rule_hash 는 다시 고정했으나 계획 파일은 따라오지 않았다. init 이후 규칙 파일이 34번 바뀌었다.
      **규칙이 바뀐 채로 같은 실행을 이어 왔다는 사실 자체는 지우지 않는다** — 그래서 init 값을 위에 남기고
      이 줄에 재고정 시점과 사유를 적는다. 승인 전 계약 검증이 이 불일치로 막혀 있었다(2026-09-17 승인 시도).
  - hash: 7447b2685c9dc136b7d0e36795b4c1c93469f5cd85b8687dcef2cccc0d75c8c4
    pinned_at: 2026-09-17
    by: FIX-61 (9차 재판정 반영)
    note: >-
      FIX-60 이 고정한 `2fc704bff291655c…` 이 같은 날 FIX-61 로 다시 어긋났다 — 9차 재판정이 문면 모순 셋과
      순손실 트랙 경로를 고치라고 해서 규칙을 또 바꿨기 때문이다. **이 자리는 규칙이 바뀔 때마다 다시
      고정해야 한다** — 계약 검증이 계획의 해시를 현재 규칙 파일과 직접 비교하고 `run.json` 을 보지 않는다.
      승인 직전에 마지막으로 확인할 것.
  - hash: d60d72aaa2a7d560e6afd975ee06065d41697b76953ef05ea494fd7daa35982e
    pinned_at: 2026-09-17
    by: FIX-62 (openai.F9 경로 뒤집기 · 사용자 결정 2026-09-17)
    note: >-
      같은 날 세 번째 재고정이다. 사용자가 openai.F9 를 C-20 비상장 경로로 보내기로 결정해(C-29) 규칙의
      `policies.f9.g1_bep_retreat_precedence` 와 `decisions`, `open_tensions` 가 바뀌었다. **앞줄에 적은
      구조적 사실이 하루 만에 두 번 더 확인됐다** — 리뷰 반영이 규칙을 건드리는 한 이 자리는 계속 어긋난다.
      이번 재고정은 점수를 바꾼 변경을 따른 것이다(openai 총점 2 → 4).
  - hash: 21e120ae065eee29ec8991f821d20dee0c3ee6b38f242aed5ed977ba0c866e3b
    pinned_at: 2026-09-17
    by: FIX-63 (9차 재판정 2회 반영 — 규칙 자기모순 둘)
    note: >-
      같은 날 네 번째 재고정이다. FIX-61·FIX-62 가 남긴 규칙 자기모순 둘을 고치면서 decisions C-06·C-07·C-29 와
      policies.f9.g1_bep_retreat_precedence, 긴장 둘이 바뀌었다. **이번에는 아래 결정 표도 같이 다시 만들었다** —
      머리말 해시만 손으로 고쳐 오는 동안 본문 표가 세 세대 전 문면(`BEP 후퇴→-5 … 명문화만 미결`)으로 남아
      있었다. 계획이 현재 규칙 해시를 주장하면서 옛 규칙 문면을 보여 주던 자리다(9차 재판정 2회 low).
      점수는 바뀌지 않았다.
  - hash: 345c3353372d0f95d98eef5ed918c31e7a3f7878185a24f1e4edfa9870d58d21
    pinned_at: 2026-09-17
    by: FIX-64 (최종 반영 — 네 영역 pass · 승인 직전)
    note: >-
      같은 날 다섯 번째이자 **마지막 재고정**이다. 9차 재무 계산 재판정 3회가 낸 새 발견 low 하나를 닫으면서
      `policies.f9.g1_bep_retreat_precedence` 와 decisions C-06, TEN-RA6-01 의 문면을 넓혔다 — `bep_retreat` 가
      영업흑자 회사의 G1 통과까지 막는다는 사실이 네 자리에서 빠져 있었다. **코드는 손대지 않아 점수가 한 칸도
      바뀌지 않았고**, 점수 페이로드가 `f313060` 과 바이트 동일인 것을 확인했다. 이 뒤로 승인·리포트 생성이
      이어지므로 규칙 파일은 여기서 동결된다.
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
created_at: 2026-09-11
assumptions:
  - 원자료와 정성 판단은 기준선 v1.5(2026-09-02)에서 승계했으며 이번 실행에서 재검증되지 않았다(legacy_unverified)
  - 미결 규칙 결정(C-xx)은 run.json.decisions 에 명시된 것만 적용한다
  - 가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)
---
# Planning Brief — AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)

## 요청 해석

- 대상: AI 기업 14개사 9-factor 채점 (`report_type: ai_scorecard`)
- 요청 원문: OBS-REG-25 + F6-REG-28 + PRIV-IMPL-31 + SCOPE-34 + CASH-FCF-35
- 산출물: `research/`·`drafts/`·`reviews/`·`output/ai-scorecard-2026-09-obsreg.html`·`scorecard/history.csv`
- 흐름: plan → research → calculate → draft → review → awaiting_user → build

## 분석 목적과 기준 시점

- 목적: v1.7 파라미터 모드로 14개사 전부를 산출하고 확정된 규칙 결정과 SEC 실측 관측을 반영한다
- 분석 기준일 `as_of` 2026-09-02 · 가격 기준일 2026-09-02 · 정보 컷오프 2026-09-02 (C-17: 셋을 분리 기록)
- 규칙 `v1.7` (해시 `2fc704bff291655c…`, 2026-09-17 재고정) — **이 줄의 원래 문장은 지켜지지 않았다.**
  init 시점 계획은 `실행 중 규칙이 바뀌어도 이 실행은 이 해시를 유지한다`(해시 `64fb45557c9d40eb…`)고 적었으나,
  리뷰 8라운드 동안 규칙을 고치는 지시가 반복돼 **규칙 파일이 34번 바뀌었고** 그때마다 `run.json` 의 `rule_hash`
  를 다시 고정했다. 계획만 따라오지 않아 승인 전 계약 검증이 막혔고, 2026-09-17 사용자 결정으로 여기서 다시
  고정했다. 이력은 머리말 `rule_hash_history` 에 있다.

### 규칙·자료 변경이 점수에 닿은 자리 (2026-09-17 정리)

점수를 바꾼 것은 아래 일곱이고 나머지 변경은 기록·서술이다. 전체 이력은
`git log -- scorecard/rules/v1.7.json` 이다.

| 시점 | 무엇이 바뀌었나 | 점수 영향 |
| --- | --- | --- |
| IMPL-46 `82d0aa8` | **규칙** — ⑥ 정본을 `parameters` 모드로 · F2 range `[2,5]` · openai F5 조달 배제 | ⑥ 을 14개사 전부 재산출 |
| FIX-52 `fc59da5` | **규칙** — ⑦ 매트릭스 `large\|yes` 를 -3 → -2 로 재척도 | nvidia·oracle ⑦ -3 → -2 |
| FIX-52 `bb3c37c` | **규칙** — 비상장 승격 조건이 진짜 ARR 만 받게 | anthropic ⑥ -3 → -4 |
| FIX-53 2단계 `f78f944` | **규칙·자료** — tsmc F5 A 가점 +2 → +1 · alibaba 확정 미인출 여신 US$3.33B 등록 | tsmc ⑤ · alibaba ⑨ -4 → -3 |
| FIX-54 1단계 | **자료** — spacex-xai 확정 미인출 여신 US$4.355B 등록(규칙 변경 아님) | spacex-xai ⑨ -4 → -3, 총점 10 → 11 |
| FIX-56 1단계 `d33afd8` | **규칙** — C-24 로 `listed_newly` 트랙이 P2 를 계산 | spacex-xai ⑥ -1 → -3, 총점 11 → 9 |
| FIX-62 | **규칙** — C-29 로 openai.F9 가 C-20 비상장 경로로(사용자가 같은 날 앞선 결정을 뒤집음) | openai ⑨ -4 → -2, 총점 2 → 4 |

**6·7·8차 리뷰 라운드(FIX-57·58·59)에서는 점수 변경이 0 이다.** 그 사실이 사용자가 2026-09-17 에
`FIX-59 만 하고 승인` 을 고른 근거다. **9차 재판정(FIX-61)도 점수 변경이 0 이었고**, 뒤이은 FIX-62 만
점수를 바꿨다. 그것은 리뷰 지적이 아니라 **사용자가 openai.F9 경로 결정을 직접 뒤집은 것**이다.

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
| ① 네트워크 | manual | 0~5 | — |
| ② 게임체인저 | paths | 0~5 | C-03 |
| ③ Last Mover | ladder | 1~5 | — |
| ④ 호황 이후 | manual | 0~5 | — |
| ⑤ 아군 | formula | 0~5 | — |
| ⑥ 가격 | parameters | -7~0 | C-12 |
| ⑦ 순환금융 | matrix | -2~0 | C-09 |
| ⑧ 비대칭 의존 | manual | -5~0 | — |
| ⑨ 적자 깊이 | gates | -4~0 | C-04, C-05, C-06, C-07, C-16 |

- 정성 판정(등급·경로·분류)은 사람이 입력하고 산식·사다리·구간 적용은 프로그램이 한다(D-03). 모르는 값은 0으로 치환하지 않는다(D-04).

## 기준선

- 기준선 `v1.5` (2026-09-02, HTML `fa66076cbcd6…`)의 점수·판정표·원자료를 승계
- 승계된 판단은 원검토일과 이번 실행 재검토 여부를 함께 표시한다. 기준선 점수는 새로 검증된 사실이 아니다(D-08).

## 미결 규칙 결정

| ID | 요약 | 영향 factor | 이번 실행 선택 |
| --- | --- | --- | --- |
| C-05 | G1 실패 뒤 G3·G4 를 추가 감점하는지 진단만 하는지 원문이 혼재 | F9 | apply |
| C-06 | 손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. [FIX-63 정정 · obsreg 9차 재무 계산 재판정 2회(Claude 독립 세션) medium] **BEP 후퇴의 우선순위는 미결이 아니다.** 사용자 결정 2026-09-17(C-29)로 `policies.f9.g1_bep_retreat_precedence` 에 명문화했다 — **C-20 비상장 경로가 먼저 서고**, 상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 **G1 통과·손실률 밴드 둘 다보다 앞서** `g1_bep_retreat_score` 를 준다. 점수도 -5 가 아니라 **-4** 다(C-06 재척도). **그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 다른 값이 나오고, **영업흑자여도 통과하지 못하고 하한을 받는다**(TEN-RA6-01). 남은 미결은 FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다 | F9 | proposed_v15_boundaries |
| C-16 | G4 판정 불가→하향 규칙과 Alibaba·SpaceX 보류 유지 사례가 다름 | F9 | downgrade |

- 미결 결정이 걸린 factor 는 `needs_rule_decision` 으로 남고 해당 기업은 공식 순위에서 제외된다. 실행 단위 선택은 `scorecard/runs/ai-scorecard-2026-09-obsreg/run.json` 의 `decisions` 에 근거·결정자와 함께 기록한다.

## 리뷰 기준

- 4개 검토 영역: 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 (설계 지침 10.1)
- 체크리스트 Q01~Q23 각 항목 pass / fail / not_applicable + 근거
- `python scripts/validate_report_contract.py ai-scorecard-2026-09-obsreg` 통과

## 완료/차단 조건

완료는 results.json 결정론 검증 통과, draft 와 review pass, 사용자 승인(approval.json) 해시 일치, HTML·history.csv 생성이다.

기업이 순위에 못 들어가는 사유는 factor 상태로 구분한다. 규칙 결정이 없으면 `needs_rule_decision`, 사람의 판정이 없으면 `needs_judgment`, 관측이 없거나 수집·파싱에 실패했으면 `pending_data` 다. 셋 다 0점으로 채우지 않고 공식 순위에서만 제외한다.

`awaiting_user` 는 이 셋과 다르다. 리뷰가 pass 이고 계산이 끝났는데 사용자 승인이 없거나, 승인 뒤 규칙·자료·판단·결과·초안 중 하나가 바뀌어 승인이 무효가 된 상태를 가리키며 build 단계에서만 나온다.
