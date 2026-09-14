# 4영역 별도 세션 리뷰 착수 — ai-scorecard-2026-09-obsreg

- 착수. 2026-09-14. 사용자 결정 "별도 세션 넷".
- 기준 해시 (worker `af6d2f7` 템플릿 frontmatter).
  - results_hash `cc696e35b4a66e408a866ee8bad69b25a07b1d971b487cc49f80b93e10b8a40c`
  - draft_hash `a19beb99659afc3738f20ce9ae4055842a43126d081ab5a7b09178de513fee52`
- scorecard/ 동결. worker 큐 비어 있음.

## 세션 넷 — 서로 독립, 조율자 컨텍스트 미공유(fork 아님)

| 영역 | 프롬프트 | 체크리스트 | part 파일 |
|---|---|---|---|
| fact-sources | `scratchpad/review-prompts/A-fact-sources.md` | Q05 Q09 Q14 Q23 | `worker/reviews/_parts/ai-scorecard-2026-09-obsreg/fact-sources.md` |
| financial-calc | `B-financial-calc.md` | Q04 Q06 Q10 Q11 | `…/financial-calc.md` |
| rule-consistency | `C-rule-consistency.md` | Q01 Q02 Q03 Q07 Q08 Q12 Q13 Q15~Q22 (15문) | `…/rule-consistency.md` |
| output-readability | `D-output-readability.md` | (없음) 항목 5 | `…/output-readability.md` |

## 공통 규칙 (프롬프트에 박음)

읽기 전용 · 유일 쓰기 = 자기 part · 빌드/승인/계산 실행 금지 · 외부 조회 금지 · 모든 단정에 파일:행 · 못 확인은 "확인 못 함" · 기존 점수를 정답으로 쓰지 않음 · 다른 part 열지 않음 · **조율자 판단에 맞추지 않음 — 어긋나면 그대로**.

## 합치기 (넷이 끝나면)

1. 네 part 의 기준 해시가 위와 같은지 확인. 다르면 그 part 무효.
2. `reviews/ai-scorecard-2026-09-obsreg.md` 의 검토 영역 표·체크리스트 표·발견 사항·판정을 part 로 채움. `reviewers:` 에 실제 수행자 기재.
3. 네 영역 전부 pass 이고 체크리스트 fail 0 일 때만 `status: pass`. 하나라도 needs_fix 면 worker 에 수정 과제 → 재계산 → 해시 바뀜 → **리뷰 재실행**(해당 영역만이 아니라 넷 다 — 해시가 기준이므로).
4. 검증기 `validate_report_contract.py <slug>` 통과 확인 → 사용자 승인.

## 훅 주의

`enforce-plan.sh` 가 Bash 명령 문자열을 훑는다. 프롬프트 본문의 `build_report.py <slug>` 인용문에 걸려 첫 발송이 통째로 차단됐다. 긴 본문은 Write 로.
