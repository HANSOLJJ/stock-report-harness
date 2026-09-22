# fact-sources — 사실·출처
검토자: Gemini 3.8 Flash (독립 세션, 2026-09-16T15:58:00+09:00)
결과: pass
요약: verified 관측 106건 전수와 점수 경로 legacy_unverified 25쌍, judgments 내 주요 인용을 1차 원문 및 v1.5 상류와 대조한 결과 값·단위·기준일·기업 귀속 및 인용 위치가 모두 정확하게 부합함을 확인했습니다. 승계 판단에 기인한 긴장 사항들은 open_tensions에 재검토 시점과 함께 적절히 등록되어 있어 승계 판단 예외를 적용합니다.

## 체크리스트
| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q05 | pass | scorecard/runs/ai-scorecard-2026-09-obsreg/sources.json:items (비상장 2사 보도자료 COI 명시), scorecard/rules/v1.7.json:open_tensions (TEN-RA-02, TEN-RA3-01, TEN-RA4-01 등록으로 승계 판단 예외 적용) |
| Q09 | pass | scorecard/rules/v1.7.json:open_tensions (TEN-RC4-04 tsmc 가이던스, TEN-RA-02 nvidia Rubin 발표, TEN-RA3-01 openai F4 배치 계획 등 승계 판단 예외 적용) |
| Q14 | pass | scorecard/runs/ai-scorecard-2026-09-obsreg/results.json:companies (14개사 전원 F3 점수 2~3점, 4점 또는 5점 부여 사례 전무) |
| Q23 | not_applicable | 조율자 분담 — 별도 세션 |

## 발견 사항
- 없음 (검토 과정에서 확인된 긴장 및 한계점은 모두 open_tensions 15건에 정상 등재되어 승계 판단 예외 요건을 충족함).

## 확인 못 한 것
- Q23 하네스 일관성 비교 및 부재 주장(미공시·missing_type) 전수 재검색, 전사 이해상충(COI) 심층 검증은 지시서 분담 규칙에 따라 별도 세션 담당으로 위임되어 본 검토에서 제외했습니다.
- Amazon SEC 8-K 4건(0001018724-25-000002 등)은 저장소 내에 HTML 파일이 보존되어 있지 않아 C-13 선행 검증 기록(8ddb0ae)을 인용했음을 확인했습니다. 단, 10-Q Note 1 및 기타 1차 자료는 보존 원문에서 전수 직접 대조를 완료했습니다.
