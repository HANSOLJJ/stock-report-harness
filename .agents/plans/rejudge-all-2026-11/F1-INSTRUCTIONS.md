# ① 락인과 가격결정력 판정 지시서 (v2.0)

규칙 원문은 `docs/scorecard/rules.md` 3절 ①, 기계 규칙은 `scorecard/rules/v2.0.json` `factors.F1` 이다. 공통 절차는 `REJUDGE-INSTRUCTIONS.md`.

## 입력 (판정 종류 `lockin`)

| 키 | 값 | 뜻 |
|---|---|---|
| `channel_consumer` / `channel_work` / `channel_trade` | yes / no | 매출·사용자 기여가 유의미한 실질 채널. 고객이 조직인 공급자(칩·파운드리·클라우드 인프라·기업 SW)는 `channel_work: yes` |
| `loop` | pass / partial / fail / unknown | 회수 루프. 사용자·개발자가 늘수록 기존 사용자 편익이 커지는가 |
| `switching` | pass / partial / fail / unknown | 전환비용. **pass = 비교 가능한 대체재가 있는데도 남는 것이 관측됨**(관계 수준). partial = 지금 설계·계약 동안만 묶이고 다음 선택에서 다시 고르며 대체재가 생기면 옮긴 사례가 있음. fail = 이탈 관측 |
| `substitutes` | pass / partial / fail / unknown | 대체 공급. fail = 대체재가 출하 중이고 격차가 좁음 |
| `pricing` | pass / partial / fail / unknown | 가격 실측. pass = 8개 분기 이상 인상된 가격이나 총마진이 유지되고 고객이 남음. 원가 요인과 가른 설명이 있어야 함 |
| `pricing_sustained_quarters` | 정수 | pricing 이 pass 면 필수, 8 이상 |
| `durability_discount` | yes / no / unknown | 10-K 공시 10% 이상 고객이 있고 그 고객의 자체 대체재가 **출하 중**이면 yes |
| `ai_monetized_in_channel` | yes / partial / no / unknown | 가장 강한 채널 안에서 AI 로 돈을 더 받고 있는가. 점수 밖, 표시용 |

사다리는 프로그램이 계산한다. 락인 강도(loop·switching 중 높은 것) pass 4 · partial 3 · fail 1, 채널 없음 0. pricing pass +1 · fail −1, substitutes fail −1, 할인 −1, 0~5 로 자름. loop·switching 둘 다 unknown 이면 점수 없음.

## 어디서 재는가

- **회수 루프**: 개발자·사용자 수 시계열(10-K Item 1, 실적 발표), 보완재 수(라이브러리·앱·IP), 양면 거래액. 한 시점 숫자만으로 pass 를 주지 않는다. 구조(두 변이 서로 끌어당김)와 성장이 둘 다 있어야 pass.
- **전환비용**: 계약 기간·RPO 12개월 내 인식 비중(`rpo_next12m_share`), 순매출 유지율(`nrr`), 고객 선급금(`customer_prepayments`), 이탈 보도. "대체재가 있는데도 남았다"를 보이려면 대체재의 존재(경쟁 제품 출하)와 고객 유지(갱신·좌석 유지)가 둘 다 근거여야 한다.
- **대체 공급**: 경쟁사 공시(AMD 데이터센터 매출, Broadcom AI 매출, Workspace 등), 독립 벤치마크, 고객사 전환 보도. 경쟁사 10-Q 도 EDGAR 에서 받는다.
- **가격 실측**: `gross_margin_ttm`·`gross_margin_ttm_prior` 관측, 정가 인상 공지와 그 뒤 좌석·구독자 수(`paid_seats`·`mau`), 광고 단가(10-Q 의 CPC·광고당 가격 변화율), 거래 채널의 단가 대 점유율(`token_share`·`price_per_m`). 총마진으로 pass 를 줄 때 "제품 구성·원가 변화가 아니다"라는 설명이 판정 칸에 있어야 한다. 8분기 조건은 분기 수를 세어 적는다.
- **지속성 할인**: `top_customer_share` 관측(10-K 고객 집중 공시)과 그 고객의 자체 대체재 **출하** 근거(발표가 아니라 출하).

## 같은 잣대 (경계 사례를 먼저 정한다)

열네 회사에 대기 전에 아래 쌍을 같은 기준으로 판정하고, 그 기준을 판정 칸 첫 문장에 적는다.

- **Oracle DB 전환비용 대 Palantir 전환비용 대 TSMC PDK 전환비용.** 셋 다 전환비용이다. Oracle 은 Postgres 가 수십 년 있었는데도 남으면 pass. Palantir 는 영국 경찰·NHS 이탈이 있으면 fail 또는 partial(이탈 규모 대 기반으로 가름). TSMC 는 노드마다 다시 고르고 Apple 이 Samsung 에서 옮겨 왔으며 NVIDIA 가 Ampere 소비자 GPU 를 Samsung 으로 냈다 돌아온 사례가 있으면 partial. 같은 종류의 사실에 같은 판정을 준다.
- **CUDA 회수 루프 대 Windows·M365 기본 탑재.** CUDA 는 개발자↔라이브러리↔구매자가 서로 끌어당기는 구조라 회수 루프 후보다. 기본 탑재는 배포 전략이지 회수 루프가 아니다. Microsoft 의 회수 루프는 Teams·GitHub 같은 다른 자산에서 찾는다.
- **Alphabet·Meta 가격 실측.** 소비자에게는 무료라 가격을 못 올리지만 광고주에게는 단가가 있다. 10-Q 의 CPC·광고당 가격 변화율이 8분기 이상 올랐고 광고 물량이 유지되면 pass 후보다. 거래 채널(모델 API)로는 재지 않는다. 가장 강한 채널(소비자)에 대해 잰다.
- **Anthropic·OpenAI 거래 채널.** 라우팅 서비스 토큰 점유율은 매출 점유율이 아니다(2.7). 단가 프리미엄을 유지하면서 점유율이 늘었으면 pass 후보, 단가를 내리며 점유율을 지켰으면 partial, 단가를 내렸는데 점유율도 줄었으면 fail. OpenAI 소비자 채널은 무료 사용자가 많아 switching 은 fail 쪽이고 pricing 은 Plus·Pro 요금과 구독자 수로 잰다.
- **Tesla.** 소비자 채널. 2023~2024 가격 인하와 그 뒤 판매량이 pricing 의 사실이다.

## 판정 칸에 반드시 적을 것

1. 어느 채널이 가장 강한 채널인지와 그 이유.
2. 네 질문의 판정과 한 줄 이유.
3. 할인 해당 여부와 근거.
4. AI 수익화 여부(어떤 AI 제품이 그 채널에서 돈을 받는가, 또는 못 받는가).
5. 못 잰 것(할인율, 업무당 비용, 이탈률)은 "미확인"으로.

## 하지 않는 것

- 채널 유형이 "부품"이라는 이유로 점수를 가두지 않는다. 그 상한은 없어졌다.
- 공급 부족에서 나온 가격 인상을 관계 수준 락인의 증거로 쓰지 않는다. 그건 pricing 칸의 사실이고 switching 칸의 사실이 아니다.
- 데이터 보유량, 토큰 볼륨, 상업 파트너 수(⑤ 소관), 시장 단가 지수를 근거로 쓰지 않는다.
