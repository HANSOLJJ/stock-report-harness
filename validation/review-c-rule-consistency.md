# 리뷰 C 규칙 일관성 (codex, 독립 세션) — 검증

- 일시. 2026-09-15 12:38. part `review-obsreg/reviews/_parts/…/rule-consistency.md` 19.5KB. 결과 **needs_fix** (fail 5 · 발견 13 · 미확인 3).
- 조율자 판정. **동의.** high 6건 전부 원자료에서 사실로 확인. 아래는 내가 직접 확인한 것.

## 확인된 것 — 점수에 닿는 둘

| # | 발견 | 확인 | 영향 |
|---|---|---|---|
| H1 | F7 range `[-2,0]` 인데 NVIDIA·Oracle F7 = **-3** (`large|yes`) | `factors.F7.range=[-2,0]` · 두 회사 `carried_score -3` · `policies.f7` 비어 있음 · schema 는 F6·F9 정책만 검사 | **범위 밖 점수 2건.** F7 을 -2 로 자르면 nvidia 8→9, oracle 1→2 |
| H6 | anthropic F6 승격이 `run_rate` 를 ARR 로 씀 | `arr`/`arr_prior` kind=`run_rate`·legacy_unverified · `arr_growth 0.383 ≥ 0.30 → met` · `kind_notes` 에 "ARR 이 아니라 런레이트" 기록하고 그대로 사용 | **anthropic F6 -3 vs -4 (총점 11 vs 10)** |

**F9 에서 잡은 range/floor 불일치를 F7 에서 놓쳤다.** v1.7 함정 재배분(F6 -5→-7, F7 -3→-2, F9 -5→-4)에서 F7 매트릭스와 승계 점수는 안 따라갔다.

## 확인된 것 — 점수 무영향, 코드·문서 결함

| # | 발견 | 확인 |
|---|---|---|
| H4 | C-03 `resolved` 인데 코드가 폐기된 `activate_candidate_mapping` 만 받고 삭제된 `path_mapping_candidate` 를 읽음 | `calc_qual.py:47-60` · 키 부재 확인. F2 가 전부 carried 라 안 터졌을 뿐. **내가 C03-IMPL-43 을 pass 하며 코드 쪽을 안 봤다** |
| H5 | C-12 가 `decisions_applied` 에 있으나 `compute_private(company, obs, judgment, rules)` 가 `run` 을 안 받음 | `calc_f6.py:273`. 라벨이 실제와 다름 — C-04 `include_v15` 와 같은 "읽는 척" 계열 |
| M1 | `scope_separation`·`two_axes`·`banned_word` 블록을 지워도 스키마 통과 | 셋 다 메모리 변조로 확인. **나는 주입만 시험했고 삭제는 안 했다** |
| H2 | 설계 지침 85~95행 범위표가 v1.7 과 네 곳 다름 | F2 0~5/[2,5] · F6 -5/[-7] · F7 -3/[-2] · F9 -5/[-4] |
| H3 | schema 가 F7 매트릭스 출력 ∈ range 를 검사 안 함 | `_validate_f6_policy`·`_validate_f9_policy` 만 있음 |
| L1 | F9 경로 문자열에 `-5` 잔존 | C-06 재척도 때 문자열 미갱신 |

## codex 가 못 확인한 것 3 → 하나는 내 쪽 결함

`drafts/ai-scorecard-2026-09-obsreg.md` 가 review-obsreg 에 없었다 — **`plan/*`·`drafts/*` 가 gitignore 라 새 워크트리에 안 따라온다.** worker 에서 복사했고 sha256 이 템플릿 `draft_hash a19beb99…` 와 일치. D 리뷰 전에 잡혀서 다행이다.

## 처리

- **fix 필요 → 결과 해시 변경 → 네 리뷰 전부 재실행.** B·D 1차 발송은 보류. A(qwen)는 이미 진행 중이라 마치게 둔다 — 관측·판단 인용 검증은 fix 와 무관하게 유효.
- H1·H6 은 사용자 결정. 나머지는 worker 수정 과제 — **worker 터미널이 세션 재시작 후 목록에 없어 다시 열어야 배정 가능.**
- codex part 는 지정 형식에서 해시 두 줄을 머리에 안 적었다(검토자·결과·요약만). 화면에서 "리뷰 템플릿 일치 여부 확인" 은 봤다. 합칠 때 내가 채운다.
