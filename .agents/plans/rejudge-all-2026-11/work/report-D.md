# 묶음 D 보고 요약 (anthropic·openai, 2026-10-08)

출처 30, 근거 27(전부 본문 확인), 이전 트리거 10(관찰 7·발동 3: TRG-040 GPT-6.1 Sol 독립 측정 등재, TRG-065 OpenRouter 실측, TRG-066 ① 부분), 새 트리거 6, 관측 12.

## ② 공통 근거 (2026-10-08 같은 날짜 순위표, Artificial Analysis)
| 축 | 1위 | 다른 회사 최고 |
|---|---|---|
| 종합 지수 4.3.2판 | Opus 5.5 58 | GPT-6 Astra·Gemini 4 Argon 53, Muse Spark 1.3 48, Qwen3.8 Max(0902) 45 |
| GDPval-AA 2.1판 | Opus 5.5 1866 | Grok 4.7 1712(8위, 원문 재확인), Muse 1684, Qwen 1671, Gemini 1626 |
| Coding Agent Index 1.5판 | Sonnet 5.5 68 | Gemini 64, GPT-6.1 Sol 63 |
- Opus 5.5 종합 1위는 2026-09-22 성립 → 세대 격차 아직 1개월 미만(6개월 임계 미달).
- ARC-AGI-2·3 은 GPT-6 Astra 1위(95.0%, 표준 하네스 62.7%). Opus 5.5 ARC-AGI-3 N/A.
- OpenAI GDPval: GPT-6 Astra 1542, GPT-6.1 Sol 1575(둘 다 GPT-5.6 Sol 1611 보다 낮음).
- SWE-bench Verified 최신 항목이 2026-02 라 쓰지 않음. OpenRouter 벤치마크 절의 Qwen3.8 Max 53.4 는 AA 자체 값 45 와 달라 주의.

## 관측
- `token_share` 3시점(주간 7/13·8/31·9/28): Anthropic 0.1169→0.0494→0.0389, OpenAI 0.0684→0.1605→0.1136.
- `price_per_m` 2시점(9/8~9/30, 10/1~10/7): Anthropic $1.2393→$1.0178, OpenAI $0.3476→$0.3604.
- `gross_margin_ttm` 두 회사 모두 값 없음(회사 비공개. 규칙의 비상장 구조 결측 목록에 없어 missing_type 은 비움).
- 못 찾음: nrr·rpo_next12m_share·developer_count, top_customer_share(공개 제출본 없음), 4월 이후 Anthropic 고객 수, 업무당 비용 독립 비교, 9월 이전 OpenRouter 지출.

## 판단 세션에 알릴 것
- **anthropic ① 거래 채널**: 정가 인하(Opus −20%, Haiku −90%, Sonnet 캐시 −50%). 평균 단가 하락, 토큰 점유율 7월 11.7% 에서 크게 하락. 반대로 10/1~7 지출 점유율 31.7% 로 9월(26.6%)보다 높음. 소비자 채널은 YipitData 결제 기준 47개 주에서 OpenAI 가 앞섬. 매출의 1/4 이 고객 두 곳(유출 S-1, 이름 비보도). SpaceXAI Grok Bot 이 Claude Opus 5.5 채택(⑤ 후보).
- **openai ①**: GPT-6 Astra 정가 $10/$50 유지, OpenRouter OpenAI 모델 중 지출 1위. Pro $200 은 가격 유지하고 사용량 축소(실질 인상, 기존 가입자 10-29 적용) — 그 뒤 유지 여부 미관측. Plus $20. 주간 사용자 9억(03-31)→12억(09-29), OpenAI 는 주간만 공개. 광고 2월 시작, 초기.
- **총마진(2차 보도, The Information 인용)**: Anthropic 2024 −94% → 2025 40%(전망), OpenAI 2024 40% → 2025 33%. 원인은 추론 비용.
- 조율자 결정 사항: 비상장 `gross_margin_ttm` 결측 유형은 규칙 목록 밖이라 비움(규칙 v2.1 과제). OpenAI 는 `mau`·`paid_seats` 등록 안 함(주간 사용자·소비자 구독은 정의가 다름). 후보 출처 URL 은 구글 리다이렉트 그대로이고 실제 주소는 note 에.
