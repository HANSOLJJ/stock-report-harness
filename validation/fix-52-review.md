# FIX-52 검토 — pass, 2차 리뷰 착수

- 일시. 2026-09-15. 대상 worker `fc59da5…8305d8a` (커밋 7개). 판정 **pass.**

## 재현

```
테스트 400 OK
총점 14개사 전부 예상 일치 — alphabet·amazon·meta 15 · microsoft 14 · tsmc 11 · anthropic·spacex-xai 10
                              nvidia 9 · apple 8 · alibaba·palantir 6 · tesla 5 · openai·oracle 2
템플릿 results_hash 5e8ce6fc… == results.json · draft_hash 931f5632… == draft sha256
F7 matrix {small|no 0, small|yes -1, large|no -2, large|yes -2} · range [-2,0]
.claude/settings.json (사용자가 켠 플러그인) 커밋 제외 확인
```

## 선언에 소비자가 있는지 — 변조로 확인

```
arr_growth accepted_kinds ["actual"]              → anthropic F6 -4
메모리에서 ["actual","run_rate"] 로 넓힘           → anthropic F6 -3
```

엔진이 선언을 실제로 읽는다.

## 지시와 다른 점 — 전부 worker 가 맞다

| 다른 점 | 판정 |
|---|---|
| `accepted_kinds: ["actual"]` (지시는 `["arr"]`) | **내 지시가 틀렸다.** `arr` 은 지표 이름이고 kind 어휘(actual·estimate·run_rate·derived·text)에 없다. 그대로 넣었으면 어떤 관측도 충족 못 하는 죽은 선언. 스키마가 kind 어휘 검사 + `["arr"]` 거부 테스트까지 넣었다 |
| 관측 source_id 26건(리뷰 A 는 28건) | 인용 패턴으로 센 수. credit_rating 14건은 용도 규정이라 제외 — 타당 |
| F9 문자열 네 곳(지시는 둘) | 같은 줄 하드코딩 전부 |
| 방법 절 `하한 -5`·NTM PER 경계값 | 지시 밖 같은 결함을 같이 고침 |

## 남긴 것 — 사용자 판단 후보

- **`capital_efficiency`(arr / cumulative_raised) 도 같은 run_rate arr 을 읽는다.** 결정 범위가 arr_growth 라 안 건드렸다. `require_all` 이라 지금은 arr_growth 만으로 승격이 막혀 **현재 점수 무영향.** arr_growth 가 나중에 충족되면 이 조건이 run_rate 로 통과할 수 있다.
- F2 판단 14건 note 가 여전히 `C-03: 경로 매핑 미확정 — 승계 점수`. 지시 밖.
- 원자료 커밋 제안: cbada75 의 `f6-avail-15b/_raw/` 12개 34MB 를 main 으로, 재구성 스크립트 경로를 15b 규약으로. 적용 안 함.

## 2차 리뷰 착수

- 1차 part 보존: 브랜치 `HANSOLJJ/review-obsreg-r1` (17015a1).
- review-obsreg → `8305d8a` reset. `_parts` 비움.
- gitignore 대상 복사: `plan/`·`drafts/`(sha256 = draft_hash) · `validation/f6-avail-15/_raw/*.json` 14개(worker 사본과 바이트 동일, 15b 와도 동일).
- 프롬프트 넷에 2차 헤더(FIX-52 변경 범위·현재 총점·"고쳤다는 주장을 믿지 말고 확인")와 **해시 두 줄을 part 머리에 적으라**는 지시 추가.
- 새 대화: qwen `/clear` · codex `/new`. **첫 시도는 Git Bash 가 `/clear` 를 `C:/Program Files/Git/clear` 로 바꿔 실패** — `MSYS_NO_PATHCONV=1` 로 재발송. codex 는 `/new` 직후 재초기화 중 첫 텍스트가 버려져 한 번 더 보냄.
- 발송: A → qwen · C → codex. 둘 다 Working 확인.
