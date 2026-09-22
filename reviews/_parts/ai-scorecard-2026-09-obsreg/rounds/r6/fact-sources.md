# fact-sources — 사실·출처
검토자: Gemini 3.8 Flash (High) · 독립 리뷰어 세션 · 2026-09-16
결과: pass
요약: observations.json 내 107건의 verified 관측을 SEC EDGAR 및 보존 공시 원자료와 전수 대조한 결과 값·단위·기준일·기업 귀속이 완전 일치함을 확인했다. legacy_unverified 25쌍의 출처 벤더 및 정책 외 표시, judgments.json 내 근거 인용(행 번호 및 공시 접수번호) 또한 상류 원문과 정확히 일치하며 Q05·Q09의 fail 항목은 v1.7 규정에 등록된 승계 판단 예외(TEN-RA-02, TEN-RA3-01)로 확인되어 사실·출처 영역 검토를 pass로 판정한다.

## 체크리스트
| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q05 | fail (승계 판단 예외 — TEN-RA-02, TEN-RA3-01) | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:521` (nvidia.F2 벤더 발표 5점 근거) 및 `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:710` (openai.F4 자체 발표 근거). v1.5 승계 논리이고 잣대 불변이며 규칙 파일 `scorecard/rules/v1.7.json:2018`(TEN-RA-02), `scorecard/rules/v1.7.json:2134`(TEN-RA3-01)에 재검토 시점(2026-11)과 함께 긴장으로 등록되어 승계 판단 예외에 해당함. 이번 실행의 신규·정정 판단(anthropic.F5, openai.F5, anthropic.F8, spacex-xai.P2 등)에는 미검증 이해당사자 발표 단독 인용 없음. |
| Q09 | fail (승계 판단 예외 — TEN-RA-02, TEN-RA3-01) | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:521` (nvidia.F2 Vera Rubin 양산 미발동 미래 사건 혼재) 및 `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:712` (openai.F4 Broadcom 2027~2028년 배치 계획 혼재). v1.5 승계 논리이고 규칙 파일 `scorecard/rules/v1.7.json:2018`(TEN-RA-02), `scorecard/rules/v1.7.json:2134`(TEN-RA3-01)에 등록된 승계 판단 예외에 해당함. 이번 실행의 신규/정정 판단에서 미래 계획을 현재 가점으로 반영한 사실 없음. |
| Q14 | pass | `scorecard/runs/ai-scorecard-2026-09-obsreg/results.json:1` 전수 검토 결과 14개사 중 F3(Last Mover)에서 5점(문이 닫힌 상태 필수) 또는 4점을 받은 기업은 0개사임(11개사 3점, 3개사 2점). 라스트무버 문이 닫히지 않은 경쟁 상태에서 조기 종결로 과다 가점한 사례 없음. |
| Q23 | not_applicable | 조율자 분담 — 별도 세션. |

## 발견 사항
- [severity: low] `reviews/ai-scorecard-2026-09-obsreg.md:9` — 템플릿 frontmatter의 `results_hash`가 `20945e2af302fc047415ec0ebe6620949b9c7e4cd576e49da39b00ea19e8cbe5`로 표기되어 있으나, FIX-56 반영 후 현재 `scorecard/runs/ai-scorecard-2026-09-obsreg/results.json`의 실제 sha256은 `299fba2d1553693b4ae86be0ffa332e445958081b424c3708cc4b98ad30ce79d`임 (`drafts/ai-scorecard-2026-09-obsreg.md`의 draft_hash는 일치함).

## 확인 못 한 것
- 조율자 분담 지침에 따라 본 세션 검토 범위에서 제외된 부재 주장(미공시·`missing_type`) 전수 재검색 및 이해상충(Q23) 심층 비교는 별도 세션 담당으로 확인하지 않음.
