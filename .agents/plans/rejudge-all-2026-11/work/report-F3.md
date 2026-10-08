# ③ 판단 세션 보고 요약 (2026-10-08)

| 회사 | 모방 | 수익모델 | 가속도 | 문 닫힘 | 단계 | 성장률 | 통과점→점수 | 옛 |
|---|---|---|---|---|---|---|---|---|
| nvidia | fail | pass | fail | fail | b 데이터센터 | 0.21→0.18 | 1→2 | 2 |
| tsmc | pass | pass | partial | fail | b HPC | 0.20→0.20 | 2.5→4 | 3 |
| apple | fail | pass | fail(지연 조항, 재작성) | fail | e | — | 1→2 | 2 |
| alphabet | fail | pass | fail | fail | d Gemini MAU | 0.20→0.056 | 1→2 | 3 |
| amazon | fail | pass | partial | fail | c AWS | 0.28→0.37 | 1.5→3 | 3 |
| microsoft | fail | pass | pass | fail | b Copilot 좌석 | 0.333→0.5 | 2→3 | 3 |
| meta | fail | pass | unknown | fail | e | — | 점수 없음 | 3 |
| oracle | fail | pass | partial | fail | c OCI | 0.93→1.21 | 1.5→3 | 3 |
| palantir | fail | pass | partial | fail | c 미국 상업 | 1.33→1.49 | 1.5→3 | 3 |
| anthropic | fail | pass | fail | fail | a 연환산 매출 | 2.33→1.17 | 1→2 | 3 |
| openai | fail | pass | pass | fail | a 연환산 매출 | 0.0→0.2 | 2→3 | 2 |
| alibaba | fail | pass | partial | fail | c 클라우드 외부 | 0.40→0.45 | 1.5→3 | 3 |
| tesla | fail | pass | partial | fail | b FSD | 0.164→0.156 | 1.5→3 | 3 |
| spacex-xai | fail | pass | pass | fail | b AI 세그먼트 | 0.125→2.475 | 2→3 | 3 |

- 별도 수익모델은 규칙 문언(비모델 매출 또는 양의 단위경제, 2.5절 총이익률 양수)을 그대로 대어 TSMC(총마진 67.7%)·OpenAI(33%, 2차)·Palantir(85%) pass.
- 모방 불가능성 partial 은 정의에 맞는 회사가 없어 전부 fail 또는 pass(TSMC 만 pass: 점유율 72.5%, 2나노 수율 60~70% 대 Samsung 50% 중반). TEN-RC4-01·RC3-05 는 fail 쪽으로 닫힘.
- Tesla partial 은 가장 갈릴 수 있음(16.4%→15.6%, 반올림 범위 겹침). fail 이면 2점.
- Alibaba 는 b 가 성장률 둘을 못 만들어 c. b 라도 partial 이라 점수 같음.
- Meta 는 e·unknown → 점수 없음(측정 불가). Apple 은 e·fail(지연 조항)로 재작성 요청.
- 다른 회사 근거 인용: EV-nvidia-038(Alphabet·Microsoft·Alibaba), EV-oracle-032(Amazon), EV-openai-056(Anthropic).
- 확정하면 좋을 후보: EV-openai-002(연환산 약 $700억, 제목만).
