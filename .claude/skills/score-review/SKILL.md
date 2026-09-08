---
name: score-review
description: scorecard 4-way 리뷰 게이트. 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 네 영역과 체크리스트 Q01~Q23 을 별도 세션 리뷰어로 수행하고 reviews/<slug>.md 를 pass|needs_fix|blocked 로 기록한다.
---

# 채점 리뷰 스킬

## 절차

1. `python scripts/scorecard_cli.py review-template <slug>` 로 `reviews/<slug>.md` 뼈대를 만든다(이미 있으면 `--force` 는 리뷰를 새로 시작할 때만).
2. 네 영역을 가급적 별도 Task/서브에이전트 세션에서 수행한다. 각 리뷰어에게 읽을 파일과 출력 형식(RESULT / FINDINGS / CHECKLIST)을 지정한다.
   - 사실·출처: `fact-checker` — 숫자·기업 귀속·기준 시점·출처·부재 주장·이해상충.
   - 재무 계산: EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호. results.json 의 calc.path 대조.
   - 규칙 일관성: 판정 입력↔규칙 판정표, 승계 표시, 미결 결정 처리, 체크리스트 Q01~Q23 전체.
   - 출력·가독성: `report-designer` — draft·HTML(있으면) 숫자 일치, 낡은 비교 문장(C-19), dashboard-design 기준. 토스 셸 요건은 이 유형에 적용하지 않는다.
3. 리뷰 파일의 "검토 영역" 표에 검토자·결과·요약을, "체크리스트" 표에 Q01~Q23 결과와 근거를 채운다. not_applicable 도 사유를 쓴다. 수행하지 않은 검토를 pass 로 쓰지 않는다.
4. 네 영역 모두 pass 이고 fail 항목이 없을 때만 frontmatter `status: pass`. 하나라도 needs_fix 면 `needs_fix` 로 두고 상위 단계(research/calculate/draft/렌더러)로 돌아가 수정 후 재생성·재리뷰한다. 자료·규칙·판단·초안이 바뀌면 리뷰는 무효이므로 템플릿의 `results_hash`·`draft_hash` 를 갱신한다(`review-template --force` 후 다시 채움).
5. `python scripts/validate_report_contract.py <slug>` 를 실행해 통과를 확인한다.

## 상태

- `pass`: 승인 요청 가능.
- `needs_fix`: 생성 단계에서 고칠 수 있는 문제.
- `blocked`: 같은 차단 이슈 3회 반복 또는 외부 자료·권한 한계.

## 완료 보고

리뷰 상태, 영역별 결과, 수정 목록, pass 이면 사용자에게 `/score-approve <slug>` 결정을 요청한다. 자동으로 승인하지 않는다.
