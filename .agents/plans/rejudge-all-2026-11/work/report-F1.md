# ① 판단 세션 보고 요약 (2026-10-08)

| 회사 | 가장 강한 채널 (소비/업무/거래) | 회수 루프 | 전환비용 | 대체 공급 | 가격 실측(분기) | 할인 | AI 수익화 | 점수 | 옛 |
|---|---|---|---|---|---|---|---|---|---|
| nvidia | 업무 (n/y/n) | pass | partial | partial | partial | unknown | yes | 4 | 2 |
| tsmc | 업무 (n/y/n) | unknown | partial | partial | partial | no | yes | 3 | 2 |
| apple | 소비 (y/n/n) | pass | unknown | unknown | partial | no | no | 4 | 5 |
| alphabet | 소비 (y/y/y) | partial | pass | partial | pass(8) | no | partial | 5 | 5 |
| amazon | 소비 (y/y/n) | pass | pass | partial | pass(10) | no | no | 5 | 5 |
| microsoft | 업무 (y/y/n) | unknown | pass | partial | pass(16) | no | yes | 5 | 5 |
| meta | 소비 (y/n/n) | pass | unknown | partial | pass(8) | no | yes | 5 | 5 |
| oracle | 업무 (n/y/n) | fail | pass | partial | partial | no | partial | 4 | 3 |
| palantir | 업무 (n/y/n) | fail | partial | partial | partial | no | partial | 3 | 2 |
| anthropic | 거래 (y/y/y) | fail | partial | fail | fail | unknown | yes | 1 | 4 |
| openai | 소비 (y/y/y) | fail | unknown | fail | partial | unknown | yes | 0 | 4 |
| tesla | 소비 (y/y/n) | fail | pass | fail | fail | no | yes | 2 | 2 |
| spacex-xai | 소비 (y/y/n) | partial | fail | partial | fail | unknown | partial | 2 | 3 |
| alibaba | 소비 (y/y/y) | partial | partial | partial | partial | no | unknown | 3 | 4 |

## 같은 잣대(판정 칸 첫 문장)
- 전환비용 pass = 다시 고를 계기(갱신·가격 인상·쉬운 해지)가 있었는데도 비교 가능한 대체재로 안 옮기고 남음, 또는 대체재 출하 중 점유율 유지. partial = 계약·설계 기간만 묶이고 다음 선택에서 일부 이동. fail = 기반 대비 큰 이탈. **자사 사용자 증가만으로는 pass 가 아님**(신규와 잔존을 못 가름) → Meta·Apple·OpenAI switching unknown.
- CUDA 는 회수 루프 pass(개발자 590만→750만, 10-K 가 루프를 서술). Microsoft 기본 탑재는 루프가 아니고 Teams·GitHub 시계열 없음 → unknown.
- 광고 단가 pass = 8분기 연속 광고 단가 YoY 상승 + 물량 증가. Meta 8분기 직접, Alphabet 6분기 직접 + 2분기 추정(판정 칸에 명시).
- Anthropic 은 거래 채널로 판정: 정가 인하 + 토큰 점유율 0.1169→0.0389 → pricing fail. OpenAI 는 소비자 채널로 판정(거래 채널은 partial).
- Tesla 2023~2025 가격 인하 + 인도 감소 → pricing fail.

## 경계 사례
- **OpenAI 0**: loop fail(사용자 가치가 서로 무관, 데이터 보유량은 제외), switching unknown(Pro 200 축소 뒤 유지 미관측 — fail 로 해도 같은 0), substitutes fail(Gemini 앱 9.5억, 지수 동점 53). 사용자 증가를 switching pass 로 읽으면 3.
- **Anthropic 1**: substitutes fail(지수 격차 58 대 53·53·52, 코딩 68 대 64·63), switching partial(Microsoft 축소는 소규모, $1M 이상 고객 두 배).
- Tesla switching pass(S&P 충성도 4년 연속, 재구매율은 근거 없음, Supercharger 개방은 내릴 근거).
- SpaceX switching fail(X EU 사용자 감소, Starlink 이탈률 비공시 — unknown 이어도 점수 같음).
- 채널 규칙: 조직 고객 공급자는 업무 채널. NVIDIA 게이밍 GPU 는 AIB 를 거쳐 별도 소비자 채널로 안 셈. 거래 채널 = 자사 모델 API 판매. Azure·Bedrock 재판매는 업무 채널.

## 추가 확정
- Amazon Prime 현재 요금 $139 — Amazon 공식 페이지를 EV-amazon-060 으로 확정(조율자). 
- OpenRouter 점유율·단가는 관측만 있고 근거 항목 없음(판정 칸에만 씀). Palantir 해지 조항은 관측 note 에만. TSMC 의 Apple·NVIDIA 파운드리 이동 사례와 Samsung SF2 대량 출하 1차 자료 없음.
