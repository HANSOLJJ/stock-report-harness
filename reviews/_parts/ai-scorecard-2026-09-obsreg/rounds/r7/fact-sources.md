# fact-sources — 사실·출처
검토자: Gemini 3.8 Flash (High) · 7차 라운드 obsreg 사실·출처 독립 리뷰 · 2026-09-16T18:47:00+09:00
결과: pass
요약: `observations.json`의 verified 관측 108건 전수와 점수 경로 상의 legacy_unverified 25쌍(26건), judgments.json의 근거 인용(행 번호·접수번호)을 원문 및 상류 문서와 전수 대조한 결과 일치함을 확인했다. 체크리스트 Q05·Q09는 규칙 파일 open_tensions에 등록된 승계 판단 예외(TEN-RA-02, TEN-RA3-01)에 해당하여 pass를 저해하지 않는다.

## 체크리스트
| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q05 | fail | `scorecard/rules/v1.7.json:2205` (TEN-RA-02), `scorecard/rules/v1.7.json:2321` (TEN-RA3-01). nvidia.F2(Vera Rubin 보도자료, 채점규칙 382행 위반)와 openai.F4(OpenAI 자체 발표 InferenceX 결과, 채점규칙 382행 위반)가 이해당사자 발표를 1차 근거로 사용한다. 단 둘 다 v1.5 승계 판단 논리이고 이번 실행이 잣대를 바꾸지 않았으며 open_tensions에 재검토 시점(2026-11)과 함께 등록되어 AGENTS.md 승계 판단 예외를 충족한다. 이번 실행의 신규 108건 verified 관측 및 F5 재판정은 SEC 1차 공시(10-K/10-Q/20-F) 기반으로 이해당사자 출처가 없다. |
| Q09 | fail | `scorecard/rules/v1.7.json:2205` (TEN-RA-02), `scorecard/rules/v1.7.json:2321` (TEN-RA3-01). nvidia.F2(2026-09 기준 미출하인 Rubin 양산 계획 반영, research/ 0건) 및 openai.F4(Broadcom 2027~2028년 1.3GW~5GW+ 배치 계획 혼재)에서 미래 계획이 점수 근거에 포함되어 있다. v1.5 승계 논리이고 잣대 불변이며 open_tensions에 2026-11 재검토로 등록되어 승계 판단 예외가 적용된다. |
| Q14 | pass | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json` (alphabet.F3~openai.F3), `scorecard/rules/v1.7.json:106`. 14개사 전원의 F3 판정에서 `door_closed: fail`로 확인되었고, 규칙 `score5_requires_door_closed: true`에 따라 F3 5점을 받은 기업이 전무하여 문이 닫히지 않은 승부를 끝난 것으로 채점하지 않았다. |
| Q23 | not_applicable | 조율자 분담 — 별도 세션 (부재 주장 전수 재검색 및 하네스 검증 분담). |

## 발견 사항
- [severity: low] `scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:tsmc.pretax_income_ttm.nonop44` — basis의 how_reconstructed_superseded에 `보존 20-F 916행`이 언급되어 있으나, location_correction에서 보존 htm이 6줄 단축본임을 명시하고 표 제목(`CONSOLIDATED STATEMENTS OF PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME`)과 행 이름(`INCOME BEFORE INCOME TAX`)으로 특정하여 원문 재현이 보장되도록 정정 완료되어 있다 — `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm`.

## 확인 못 한 것
- 부재 주장(미공시, `missing_type`) 전수 재검색과 이해상충(Q23) — 조율자 지침에 따라 별도 독립 세션이 분담하여 본 검토 범위에서 제외했다.
- 비상장 2사(anthropic, openai)의 비공시 내부 재무제표 — 공개 1차 공시(Form 8-K, 10-Q 및 공식 약관) 외 비공개 원자료는 부재하여 확인하지 못했다.
