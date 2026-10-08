# ② 신기술 게임체인저 판정 지시서 (v2.0)

규칙 원문은 `docs/scorecard/rules.md` 3절 ②, 기계 규칙은 `scorecard/rules/v2.0.json` `factors.F2`. 공통 절차는 `REJUDGE-INSTRUCTIONS.md`.

지금 14개사 ② 는 전부 점수 숫자만 있고 세 경로 입력이 없다. 이번에 처음으로 입력을 만든다.

## 입력 (판정 종류 `paths`)

| 키 | 값 | 뜻 |
|---|---|---|
| `performance_leap` | pass / partial / fail / unknown | 성능 도약. 벤치마크에서 세대 격차를 만들었나 |
| `paradigm_adaptation` | pass / partial / fail / unknown | 패러다임 적응. 남이 바꾼 판(에이전트·추론·코딩)에 빨리 올라탔나 |
| `standard_capture` | pass / partial / fail / unknown | 표준 선점. 산업 인터페이스를 정의했나 |
| `top_rank` | yes / no / unknown | 옛 입력. `no` 로 둔다(5점 자격이 아니다) |
| `generation_gap` | yes / no / unknown | 성능 도약이 세대 격차 수준인가 |
| `generation_gap_months` | 정수 | `generation_gap: yes` 면 필수. 2위가 그 수준에 도달하는 데 걸린 개월 수 |
| `leap_independent` | yes / no / unknown | 성능 도약의 근거가 독립 측정인가. `performance_leap: pass` 면 필수 |

점수는 통과 경로 수로 계산한다(0개 2 · 1개 3 · 2개 4). 성능 도약 pass 이고 `generation_gap: yes` 이고 개월 수가 임계(모델 6, 부품형 12) 이상이면 5. `leap_independent` 가 yes 가 아니면 성능 도약을 부분으로 계산한다. 미확인이 있으면 점수 없음.

## 경로별 판정 기준

- **성능 도약**: 세 축(종합 지능·에이전트 실무·코딩)을 따로 본다. 하드 벤치마크(AA 종합 지수·HLE·ARC-AGI·SWE-bench 류) 1차, 사용자 투표형(Arena)은 참고. 같은 하네스끼리만 비교. 지수 버전·평가일·모델 버전을 근거에 적는다. pass = 두 축 이상에서 독립 측정 1위. partial = 한 축 1위 또는 벤더 발표만 있음. fail = 어느 축에서도 선두권이 아님. 칩·파운드리는 MLPerf(칩)·독립 분석의 전력당 성능(공정)으로 재고, 벤더 발표(Vera Rubin 5배 같은 것)만 있으면 `leap_independent: no`.
- **세대 격차**: 두 축 1위가 성립한 날부터 2위가 같은 수준에 도달한 날까지의 개월 수. 아직 도달하지 않았으면 1위 성립일부터 기준일까지의 개월 수. 그 수가 임계 미만이면 `generation_gap: no`. 모델 6개월, 부품형 12개월(대량 출하 기준 — 2위가 같은 세대를 매출 비중이 공시될 만큼 출하한 시점).
- **패러다임 적응**: 그 패러다임(에이전트·추론·코딩)의 제품을 **출시했고 채택 지표가 있는가**. 출시만 있고 채택 지표가 없으면 partial. 선두 대비 출시 지연 개월 수를 근거에 적는다.
- **표준 선점**: **다른 회사가** 그 인터페이스를 채택했다는 사실. MCP 채택 벤더 수, OpenAI API 호환 선언 경쟁사 수, CUDA 위에서만 도는 라이브러리 수. 자사 제품 안에서만 쓰이는 형식은 표준이 아니다.

## 같은 잣대

- NVIDIA 의 성능 도약은 MLPerf 결과가 있어야 `leap_independent: yes`. 없으면 지금 5점은 4점이 된다. 그 결과를 숨기지 않는다.
- TSMC 의 세대 격차는 Samsung 2nm·Intel 18A 의 **대량 출하** 시점으로 잰다. 발표·시험 생산은 도달이 아니다.
- Meta·Alphabet·Anthropic·OpenAI·Alibaba(모델 기업)는 같은 지수 버전·같은 평가일의 순위표 한 장으로 성능 도약을 가른다. 회사마다 다른 날짜의 순위를 쓰지 않는다.
- Apple·Oracle·Palantir·Tesla·SpaceX·Amazon·Microsoft 는 세 경로를 같은 질문으로 보되, 모델이 없다는 사실 자체는 성능 도약 fail 이지 다른 경로의 fail 이 아니다(Q17).
