# 리포트 "지금 시장" 탭 계획

## 왜
점수를 매긴 뒤 시장(금리·신용·GPU 임대료·토큰 단가)이 어떻게 움직였는지 리포트 한 화면에서 보고, 다시 매길 계기인지 판단한다(2026-11-15 사용자 요청, "한방에 보는 게 좋다").

## 모양
- 리포트 HTML 에 "지금 시장" 탭을 더한다. 다른 탭은 그대로 확인 시점의 고정본이다.
- 표는 지표 · 이 리포트 기준일 값 · 지금 값 · 변화 네 칸이다.
  - 기준일 값: 실행의 collect 가 그날 값을 관측(시장 지표, 점수 밖)으로 찍는다. 입력 해시와 확인 기록에 묶인다. 찍지 않은 옛 실행은 "이 실행은 기록하지 않았다".
  - 지금 값: 갱신 버튼을 누르면 맥미니 리포트 서버(server.js)의 엔드포인트가 원천에서 받아 약 1시간 캐시한다. 받은 시각을 적는다. 결과는 어떤 실행 파일에도 쓰지 않는다.
- 점수·순위에는 쓰지 않는다. 기준일 값의 변화는 트리거 조건으로만 쓴다(rules.md 국면 지표와 같은 원칙).

## 1단계 지표
| 지표 | 원천 |
|---|---|
| 미국채 10년물 | yfinance `^TNX` 또는 FRED DGS10 |
| 회사채 스프레드(투자등급·하이일드) | FRED ICE BofA 지수 |
| GPU 임대료(H100·B200 시간당 중간값) | 공개 장터 호가(vast.ai 등). 계산식을 고정한다 |
| 토큰 단가 | OpenRouter 공개 모델 가격으로 계산. 지금 손으로 넣는 token_price_index 를 대신할지 정한다 |

## 뺀 것
- HBM 현물: 장기 계약으로만 팔려 현물 시장이 없다. 실적 발표의 평균판매단가 언급이 대신이다.
- AI 기업 CDS: 무료 원천이 없다(Markit·Bloomberg). 필요하면 발행사 회사채 스프레드로 대신한다.
- D램 현물: TrendForce 공개 표. 약관을 확인한 뒤 2단계로.

## 구현 (2026-11-15 "일단 만들어봐")
확인한 사실: 공개 사이트는 맥미니의 finance 서버(HANSOLJJ/finance, pm2, 127.0.0.1:8787)가 내보내고, 같은 서버에 화이트리스트 프록시 `/api/proxy` 가 있으며 FRED 키를 서버가 주입한다. 리포트와 같은 주소라 리포트 스크립트가 그 프록시를 부를 수 있다. OpenRouter 는 CORS `*` 라 직접 부른다. vast.ai 는 CORS 가 없고 프록시 목록에도 없다(finance 저장소는 이 작업 범위 밖이라 고치지 않는다).

1. 정의와 계산을 한 곳에: `scripts/scorecard/market_now.py`(받기·계산·관측 만들기)와 `scripts/scorecard/assets/market_live.js`(브라우저 계산). 같은 고정 자료로 두 구현이 같은 값을 내는지 테스트한다.
   - 미국채 10년물 DGS10, 투자등급 스프레드 BAMLC0A0CM, 하이일드 스프레드 BAMLH0A0HYM2: 가격 기준일 이하의 가장 최근 값(FRED 의 "." 는 건너뜀). 스냅숏은 fredgraph.csv(키 없음), 지금 값은 프록시의 FRED API.
   - GPU 임대료: vast.ai 대여 가능 on-demand 호가, GPU 종류별(H100 SXM·H200·B200) GPU 한 장 시간당 단가의 GPU 수 가중 중간값과 GPU 수.
   - 토큰 단가: OpenRouter 에서 연구소 목록(openai·anthropic·google·x-ai·deepseek·qwen·moonshotai)마다 최근 180일 안에 나온 비배치 유료 모델 가운데 혼합 단가(입력 3 : 출력 1, 100만 토큰당)가 가장 높은 것을 고르고 그 중간값. 고른 모델을 함께 보인다.
2. 스키마: 시장 지표 다섯(`ust10y_yield`·`ig_oas`·`hy_oas` 단위 percent, `gpu_rent_hourly` 단위 USD/GPU-hour + basis.gpu, `token_blended_price` 단위 USD/1M tokens + basis.picks)을 `_market` 에 둔다.
3. `collect --kind market`: 관측과 출처(SRC-FRED-·SRC-VAST-·SRC-OPENROUTER-<날짜>)를 쓴다. `all` 에 들어간다.
4. diff: 시장 스냅숏 지표는 어느 실행 종류에서든 더해져도 위반이 아니다(점수 밖).
5. 렌더: render_common `market_view` → 초안 국면 절과 HTML 국면 탭에 표. HTML 은 지금 값·변화 칸과 갱신 버튼을 더한다. 스냅숏이 없는 실행은 표가 없다(옛 실행 렌더 바이트 불변).
6. 문서·스킬(score-collect, guide.md, structure.md).

## 정할 것
- 언제 만들지(실적 반영 실행 전·후).
- 원천마다 원천 장부(sources) 등록 방식, 원천이 막혔을 때 칸 표시.

## 추이(2026-11-15 2차 결정)

사용자는 지금 값 하나가 아니라 추이를 원한다. 역사가 긴 지표는 10년까지 본다.

### 원천과 기간

| 지표 | 원천 | 기간 |
|---|---|---|
| 미국채 10년물 | FRED DGS10 | 2015-01 이후 일별(10년) |
| 회사채 Baa−10년물(무디스) | FRED BAA10Y | 2015-01 이후 일별(10년). 긴 추이용으로 새로 더한다 |
| 투자등급·하이일드 OAS | FRED BAMLC0A0CM·BAMLH0A0HYM2 | FRED 가 최근 3년만 준다 |
| GPU 임대료(우리 정의) | vast.ai on-demand, GPU 수 가중 중간값 | 2026-11-15 부터 매일 쌓는다 |
| GPU 임대료(외부) | GetDeploying 주간 중간값(CC BY 4.0, 출처 표기) | 최근 53주. 정의가 달라 우리 선과 잇지 않는다 |
| 토큰 혼합 단가 | OpenRouter, 우리 정의 | 2026-11-15 부터 매일 쌓는다 |
| 토큰 혼합 단가(재구성) | OpenRouter 지금 목록을 과거 날짜에 대입 | 2025-07 이후 주별. 사라진 모델·가격 인하가 빠지는 치우침을 표시한다 |

### 구조

- finance 서버(맥미니)가 하루 한 번 위 원천을 받아 `data/market-series.json`(gitignore)에 쓴다. 매일 쌓는 값은 날짜별로 덧붙이고, FRED·GetDeploying·재구성은 받을 때마다 통째로 새로 만든다.
- 공개 경로 `/reports/market-series.json` 로 내보낸다. `/api/*` 는 Cloudflare Access 로그인이 필요해 공개 리포트에서 부를 수 없다. 그래서 리포트가 `/api/proxy` 를 부르던 1차 설계를 버리고, vast.ai 프록시 허용 목록 수정도 하지 않는다.
- 계산 정의(GPU 가중 중간값, 토큰 모델 고르기)는 하네스 `scripts/scorecard/assets/market_live.js` 하나다. finance 서버는 옆 폴더의 그 파일을 `createRequire` 로 불러 쓴다(`/reports` 가 이미 옆 폴더 clone 에 기대고 있다).
- 리포트 버튼("추이 받기")은 그 JSON 하나를 받아 지표마다 작은 선 차트를 그린다. 기간 1년·3년·10년, 기준일에 점, 지금 값·변화 칸은 시계열 마지막 점으로 채운다.
- 하네스 collect --kind market 은 BAA10Y 를 기준일 값으로 더 찍는다(`baa_spread`).

## 회사채·D램·토큰 카드(2026-11-15 3차 결정)

사용자 지시: 회사채는 하이일드 묶음이 아니라 개별 회사(특히 CoreWeave 같은 네오클라우드)의 채권을 본다. D램 현물가 추이도 본다. 국면 탭에 홀로 남은 토큰 단가 지수 카드를 정리한다.

### 원천

| 지표 | 원천 | 기간 | 공개 |
|---|---|---|---|
| 개별 회사채 가산금리·수익률 | BondTerminal API `/bonds/{isin}/history`(무료 개인 키, 하루 200 읽기 단위, 한 번 10 단위) | 채권 발행 이후 일별 | 로그인한 사람만 |
| D램 현물(DDR5 16Gb 4800/5600 하루 평균) | DRAMeXchange 첫 화면 표 | 2026-11-15 부터 매일 쌓는다(과거 차트는 유료 회원 전용) | 로그인한 사람만 |
| D램 수출물가지수(달러 기준, 2020=100) | 한국은행 ECOS `402Y016` 항목 `30911201AA`·`D` | 2015-01 이후 월별 | 공개 |

- BondTerminal 에 실린 대상은 CoreWeave(선순위채 4종)·Oracle·Meta 뿐이다. Nebius·Applied Digital·IREN·Cipher·TeraWulf·xAI·Meta Hyperion SPV(Beignet)는 없다.
- 회사마다 대표 채권 하나의 국채 대비 가산금리를 그린다. CoreWeave 9.25% 2030, Oracle 2.875% 2031, Meta 4.95% 2033.

### 구조

- 공개 시계열(`/reports/market-series.json`)에 D램 수출물가지수를 더한다. 표에 없는 시계열은 제목·단위를 JSON 에 실어 차트만 그린다.
- 게시가 제한된 원천(BondTerminal·DRAMeXchange)은 finance `data/market-private.json` 에 따로 쌓고 `/api/market-private` 로만 낸다. Access 로그인과 서버의 JWT 검증을 둘 다 지나야 한다. 리포트는 그 주소를 불러 보고, 실패하면(로그인하지 않은 방문자) 그 절을 그리지 않는다.
- 키(`BONDTERMINAL_API_KEY`·`ECOS_API_KEY`)는 사용자가 맥미니 `~/.finance/env` 에 넣는다. 키가 없으면 그 원천만 건너뛰고 실패로 세지 않는다.
- 토큰 단가 지수(Silicon Data, 수동 관측)는 시장 지표 절이 있는 리포트에서 큰 카드를 없애고 표의 한 줄(기준일 값만)로 넣는다. 시장 지표 관측이 없는 옛 실행은 지금 모양 그대로 둔다.
