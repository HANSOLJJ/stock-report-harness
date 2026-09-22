# fact-sources — 사실·출처
검토자: Gemini (antigravity-cli, conversation 902e9389-18cd-4e9c-920e-c2c5c50a2137, 2026-09-17)
결과: pass
요약: verified 관측 108건 전수와 legacy_unverified 점수 경로 26건, judgments 인용 1차 공시 및 원문 행 번호 대조에서 불일치가 없었습니다. 체크리스트 Q05·Q09는 v1.7.json에 등록된 승계 판단 예외(TEN-RA-02, TEN-RA3-01)에 해당하여 pass를 차단하지 않습니다.

## 체크리스트
| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q05 | fail | `nvidia.F2`(TEN-RA-02) 벤더 발표 1차 인용, `openai.F4`(TEN-RA3-01) 자체 발표 인용. 다만 v1.5 승계 논리이고 규칙 파일 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`(재검토 2026-11)로 등록되어 승계 판단 예외 적용. 이번 실행이 바꾼 신규 판단(`anthropic.F5.impl48`, `openai.F5.impl48`, `anthropic.F8.f8anth33`)은 SEC 8-K·10-Q 및 별표 규정을 직접 확인하여 정합함. |
| Q09 | fail | `nvidia.F2`(TEN-RA-02) Rubin 미래 양산·출하 반영, `openai.F4`(TEN-RA3-01) 2027~2028년 배치 계획 혼재. 다만 v1.5 승계 논리이고 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`로 등록되어 승계 판단 예외 적용. 반면 F3 전원 door_closed=fail 및 F4 타사 출하 기준은 준수됨. |
| Q14 | pass | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json`의 F3 판단 14개사 전원의 `door_closed` 입력이 `fail`로 설정되어 있고, `results.json`의 F3 최종 점수가 전원 2점 또는 3점(4점 상한 이하)으로 문이 닫히지 않은 상태에서 5점을 부여한 사례가 전무함. |
| Q23 | not_applicable | 조율자 분담 — 별도 세션 |

## 발견 사항
- [severity: low] `scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json` (`anthropic.fcf_ttm.priv31` 등 basis.counterparty_filings) — 상대방 제출본 검색에서 확인된 SpaceX S-1/A(3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm)의 Anthropic 클라우드 계약($1.25B/월, 약 325,000 GPU)은 '90일 전 서면 통지로 해지 가능' 조항이 명시되어 있어 무조건 약정(B종) 요건에 미달함을 확인했고, 부외 약정 미등록 사유가 타당하게 기록되었습니다.
- [severity: low] `scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json` (`openai.arr_prior.priv31` basis.primary_source_link) — 보존 원자료(ffaf318:validation/priv-arr-17b/_raw/external_reporting_raw.json)의 "공식 발표문에는 매출 수치가 일체 포함되어 있지 않음"이라는 잘못된 부재 주장을 이번 실행이 배제하고, 실제 발표문 문장과의 직접 인용 부재로 사유를 분리·기록한 조치가 정확함을 확인했습니다.
- [severity: low] `scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json` (`nvidia.net_cash.nc37`, `meta.net_cash.nc37` 등) — 12개 상장사 대상 `marketable_equity_sweep` 전수 검토 결과, nvidia의 시장성 지분증권 42,783M은 `DebtSecuritiesCurrent`와 별개 태그(`EquitySecuritiesFvNi`)로 분리되어 순현금에 정확히 반영되었고, meta의 경우 이미 `MarketableSecuritiesCurrent` 74,798M 안에 지분 3,543M이 포함되어 있어 추가 시 이중계상됨을 검산하여 배제한 판단이 정확합니다.

## 확인 못 한 것
- Alphabet(GOOGL) 및 Microsoft(MSFT)의 전체 10-K/10-Q 원문 htm 파일은 저장소 `validation/**/_raw/` 어느 곳에도 보존되어 있지 않아(companyfacts json만 존재), 상대방 제출본 검색 시 Alphabet과 Microsoft 제출본 본문을 훑는 작업은 직접 확인하지 못했습니다(긴장 `TEN-RA5-01` 및 관측 basis에 동일하게 미보존 사실 명시됨).
- 조율자 분담 규칙에 따라 부재 주장(미공시·missing_type) 전수 재검색과 이해상충(Q23)은 본 세션의 검토 범위에서 제외되어 확인하지 않았습니다.
