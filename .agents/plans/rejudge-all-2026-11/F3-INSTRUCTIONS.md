# ③ Last Mover 판정 지시서 (v2.0)

규칙 원문은 `docs/scorecard/rules.md` 3절 ③, 기계 규칙은 `scorecard/rules/v2.0.json` `factors.F3`. 공통 절차는 `REJUDGE-INSTRUCTIONS.md`.

## 입력 (판정 종류 `criteria`)

| 키 | 값 | 뜻 |
|---|---|---|
| `imitation` | pass / partial / fail / unknown | 모방 불가능성. 경쟁사가 구조적으로 못 베끼는 자산이 있고 그 덕에 실제로 앞서 있어야 pass |
| `revenue_model` | pass / partial / fail / unknown | 별도 수익모델. 전략을 먹여 살리는 비모델 매출 또는 양의 단위경제 |
| `acceleration` | pass / partial / fail / unknown | 후발 가속도. AI 귀속 지표의 성장률이 오르는가 |
| `door_closed` | pass / fail / unknown | 문 닫힘. 선두의 가격 결정력 붕괴나 점유율 실측 역전 |
| `acceleration_tier` | a / b / c / d / e | 가속도에 쓴 지표의 단계. 필수 |
| `acceleration_growth_rates` | [숫자, 숫자] | 같은 정의의 성장률 두 개(이른 것, 늦은 것). 단계 e 가 아니면 필수 |

## 지표 단계

| 단계 | 지표 | 허용 |
|---|---|---|
| a | 매출 전부가 AI 인 회사의 매출·ARR(Anthropic·OpenAI) | pass 가능 |
| b | AI 지배 세그먼트·제품선. 데이터센터 매출(NVIDIA), Copilot 유료 시트(Microsoft), FSD 구독(Tesla), AI 제품 매출(Alibaba), xAI 세그먼트(SpaceX), TSMC 의 HPC·AI 가속기 매출 비중. 비AI 비중을 판정 칸에 적는다 | pass 가능 |
| c | 클라우드 전체 매출 같은 대리 지표(Alphabet 클라우드, Oracle OCI). b 가 가능한 회사에는 쓰지 않는다 | **최대 partial** |
| d | AI 제품 사용량 시계열(Meta AI 월간 사용자, Gemini 앱 월간 사용자) | pass 가능 |
| e | 없음 | unknown, 점수 없음 |

가속도는 성장률의 변화다. 같은 정의의 성장률 두 개를 비교해 올랐으면 pass, 유지면 partial, 내렸으면 fail. 수준값이 셋 미만이면 "N분기 만의 최고 성장률" 같은 명시적 진술로 대신할 수 있되 그 사실을 판정 칸에 적는다. 거리(누적 성과, "N년 만에 격차 회수", ARR 증가 폭)는 가속도가 아니다(Q10). 지연은 감속이다.

## 같은 잣대

- **TSMC** 는 전체 매출 성장률을 쓰지 않는다. HPC 플랫폼 비중이나 AI 가속기 매출 비중(실적 발표)이 있으면 b, 없으면 c(전체 매출은 c 로 적고 최대 partial).
- **Meta** 는 Meta AI 월간 사용자 시계열(실적 콜)이 있으면 d. Muse 주간 사용자 한 시점 수치로 partial 을 주지 않는다. 시계열이 없으면 e 이고 점수 없음을 그대로 둔다.
- **Alphabet** 은 Gemini 앱 월간 사용자 시계열이 있으면 d, 없으면 클라우드로 c(최대 partial).
- **Oracle** 은 OCI 가 c 다. RPO 는 수준값이라 가속도 근거가 아니다.
- **Palantir** 는 전체 매출이 아니라 AIP 귀속 지표가 있으면 b, 없으면 미국 상업 매출을 c 로 적는다(Gotham·Foundry 가 섞임).
- **모방 불가능성**: 개발자 생태계(CUDA)는 ① 회수 루프에서 세므로 여기서 세지 않는다. 공급 쪽 자산(수율·규모·공정 우위)은 여기서 센다. ① 의 설치기반도 여기서 세지 않는다.
- **문 닫힘**: 선두의 가격 결정력 붕괴나 점유율 실측 역전이 검토됐을 때만 pass. 없으면 unknown 이 아니라 fail 로 적는다(검토했는데 증거가 없음).
