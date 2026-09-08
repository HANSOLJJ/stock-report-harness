# 기준선 이관 보고 — v1.5

- 원본 HTML SHA-256: `fa66076cbcd675d3f36a11ab2d4f80c3b2242ece84929dcc2765290ff9d71858`
- 원본 MD SHA-256: `d28c5416786b5d93798520c060decda855f7a8e53917f623bade7886271aed30`
- 기업 14개, 관측 227건, 트리거 39건을 이관했다.
- 모든 관측은 `legacy_unverified` 상태다. 이번 실행에서 재검증된 사실이 아니며 점수 정정도 하지 않았다(D-08).

## HTML D ↔ MD 순위표 대조

| 기업 | 조정총점 | 대조 |
|---|---:|---|
| alphabet | 17 | match |
| amazon | 16 | match |
| meta | 16 | match |
| microsoft | 16 | match |
| tsmc | 14 | match |
| alibaba | 12 | match |
| anthropic | 12 | match |
| apple | 10 | match |
| nvidia | 10 | match |
| palantir | 6 | match |
| spacex-xai | 6 | match |
| tesla | 5 | match |
| oracle | 4 | match |
| openai | 2 | match |

## 불일치·주의

- 없음

## 파싱 실패(원문 보존)

- amazon.contracted_revenue.v15: 'AWS 백로그(수백 $B급) — 숫자 미공시'

## 이관 시 적용한 분류(규칙 원문 표에서 읽음)

- ⑥ NTM 방법: TSMC·Alibaba 는 `annual_weighted_proxy`(C-13), 나머지 상장사는 `vendor_forward_pe_verified_ntm`.
- 시총: HTML D.cap(표시용 반올림, 예: Alphabet 4.173T)은 3-1a 표(VAL, $4.12T)와 다르므로 관측으로 넣지 않았다. 원자료는 VAL 표 값만 이관한다.
- ⑨ G4: Oracle(리스 $250B / RPO $638B)·Amazon(미개시 리스 $106B / 백로그 숫자 미공시)은 규칙 표 값. Anthropic·OpenAI 의 ARR·컴퓨트 약정은 `incompatible_basis`(C-07).
- ⑨ G1: Anthropic·Alibaba 는 단일 분기 흑자(전환)라 TTM 부호 `unknown`(C-20). SpaceX 손실률 -14.9% 는 EARN 열에서 이관.
- ⑨ G4: coverage_comparable 은 검토 입력이라 Oracle 만 `yes`(RPO vs 리스, 원문 판정). Amazon·Alibaba·SpaceX 는 `unknown`(판단 대기), Anthropic·OpenAI 는 `no`(C-07).
- ③·⑤·⑦ 입력은 규칙 v1.5 판정표(③ 사다리, 별표 G, 별표 I)를 승계. Anthropic·OpenAI ⑦은 환류 축 근거가 없어 승계 점수(C-09).
