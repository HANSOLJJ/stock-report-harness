# output-readability — 출력·가독성
검토자: Gemini 3.8 Flash (High) · be7f6de6 · 2026-09-16
결과: pass
요약: 초안(`drafts/ai-scorecard-2026-09-obsreg.md`)의 14개사 순위·총점·Factor별 126건 점수가 `results.json`과 전수 일치하며, F5·F7·F6 등 최근 반영 사항이 정합하게 서술되어 있습니다. `render_common.py`를 통한 단일 표시 규칙으로 승계 판단·미검증 관측·공급사 정책 외 원천(†)·이해상충 등 불확실성이 투명하게 노출되고 모바일 반응형 및 면책 문구 스펙을 충족하여 pass로 판정합니다.

## 항목
| # | 항목 | 결과 | 근거(파일:행) |
|---|---|---|---|
| 1 | 초안↔결과 일치 | pass | `drafts/ai-scorecard-2026-09-obsreg.md:24-51`, `drafts/ai-scorecard-2026-09-obsreg.md:57-1162`, `drafts/ai-scorecard-2026-09-obsreg.md:1170-1215`, `scorecard/runs/ai-scorecard-2026-09-obsreg/results.json:25-4315` |
| 2 | 렌더 매핑 | pass | `scripts/scorecard/render_common.py:189-215`, `scripts/scorecard/render_common.py:235-270`, `scripts/scorecard/render_html.py:402-479`, `scripts/scorecard/render_md.py:197-281` |
| 3 | 불확실성 노출 | pass | `drafts/ai-scorecard-2026-09-obsreg.md:30`, `drafts/ai-scorecard-2026-09-obsreg.md:1166-1187`, `drafts/ai-scorecard-2026-09-obsreg.md:1218`, `drafts/ai-scorecard-2026-09-obsreg.md:1270-1277`, `scripts/scorecard/render_common.py:350-404`, `scripts/scorecard/render_common.py:483-521` |
| 4 | 낡은 비교 문장 | pass | `drafts/ai-scorecard-2026-09-obsreg.md:28`, `drafts/ai-scorecard-2026-09-obsreg.md:401-402`, `drafts/ai-scorecard-2026-09-obsreg.md:773`, `drafts/ai-scorecard-2026-09-obsreg.md:1133`, `drafts/ai-scorecard-2026-09-obsreg.md:1306`, `drafts/ai-scorecard-2026-09-obsreg.md:1324` |
| 5 | 출력 스펙 | pass | `scripts/scorecard/render_html.py:220-242`, `scripts/scorecard/render_html.py:751-806`, `scripts/build_report.py:397-400`, `scripts/build_report.py:898-905`, `drafts/ai-scorecard-2026-09-obsreg.md:1342` |

## 발견 사항
- [severity: low] `drafts/ai-scorecard-2026-09-obsreg.md:1275` (알려진 한계) 및 `scripts/scorecard/render_common.py:483-486` — 알려진 한계 본문에 "이해상충이 표기된 출처가 5종이고"라고 적혀 있으나, References에 등록된 이해상충 표기 출처 항목은 실제 6건(SRC-v15-html, SRC-v15-md, SRC-v15-rule, SRC-v15-handover, SRC-ANTHROPIC-SERIESH-2026, SRC-OPENAI-FUNDING-2026)입니다. 이는 `render_common.py:483`에서 `conflict_of_interest` 문자열 집합(`set`)의 크기가 5개(SRC-v15-html과 SRC-v15-md의 고지 문언 동일)이기 때문이며, 독자에게 출처 건수와 혼동을 줄 수 있으나 정보 누락이나 판단 왜곡은 없는 경미한 표현 이슈입니다. — `drafts/ai-scorecard-2026-09-obsreg.md:1275`, `drafts/ai-scorecard-2026-09-obsreg.md:1328-1340`, `scripts/scorecard/render_common.py:483-486`

## 확인 못 한 것
- 승인 전 상태이므로 `python scripts/build_report.py ai-scorecard-2026-09-obsreg`를 실제로 실행하여 파일시스템에 최종 HTML을 생성하는 빌드 실행은 수행하지 않았습니다 (승인 전 빌드 금지 계약 준수). 소스 코드 정적 분석 및 메모리 상 `render_document` 호출 결과만 검증했습니다.
