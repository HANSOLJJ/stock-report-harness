# 레인 I 보고서: 독립 검증 발견 F-5·F-6 수정

## 한 일

- F-5: `scripts/scorecard/collect_news.py` 에 `LANG_DEFAULT_REGION`(en→US, ko→KR, ja→JP, zh→CN, de→DE, fr→FR)과 `split_locale()` 을 추가했다. 하이픈 없는 locale 은 표로 국가를 정하고, 표에 없으면 `ValueError("locale 은 xx-YY 형식으로 준다")` 를 낸다. `xx-YY` 는 그대로다. `ceid` 는 `<국가>:<언어>` 이다. `tests/test_collect_news.py` 에 테스트 3건(`ko`→`gl=KR`·`ceid=KR:ko`, `en-US` 불변, 모르는 언어 예외)을 더했다.
- F-6: 아래 표의 각 위치를 고쳤다.

## F-6 재확인 (Grep)

| 위치 | 고친 내용 | 재확인 |
| --- | --- | --- |
| `docs/scorecard/open-items.md` 5·26·54·103행 | `scorecard/runs/<slug>/`·`reviews/<slug>.md` 를 `output/<run_id>/…`·`output/<run_id>/review.md` 로, 맨 `python` 을 `uv run --frozen python -X utf8` 로 | `scorecard/runs/`·`reviews/<slug>` 검색 결과 없음 |
| `open-items.md` 68행 (D-06) | "훅이 python3 별칭을 요구" 전제를 지금 배선(npm 스크립트·훅 모두 uv)으로 고침. 열린 문제의 의미(python 표기 혼용)는 유지 | 남은 `python3` 언급은 이 항목 한 곳뿐이고 현황 서술임 |
| `README.md` 훅 표 | protect 목록을 레인 H 계약대로(`.github/workflows/`, `docs/finance-style-guide.md`, `scorecard/baseline/**`, 두 승인 실행 묶음 포함), 셸 쓰기 대상 판정·인터프리터 규칙·`init --force` 차단 서술. `forbid_financial_advice` 에 셸 실행 후 배선 추가(`.claude/settings.json` 78~82행, `guard.py` 355행의 전체 재검사 동작 기준). `enforce_memory` 를 `memory/_daily/`·`memory/topics/` 로. 첫 방어선 한계 한 문장 추가 | README 103·105·107·112행에서 확인 |
| `docs/scorecard/structure.md` 4행 | "저장소 밖 읽기 전용" 을 "읽기 전용 참고 자료, git 이 6개 파일 추적" 으로 | 검색 결과 `저장소 밖 읽기` 없음 |
| `structure.md` 11행 | 제거된 `report_type_for()` 를 가리키던 서술을 "함수는 제거됨, `report_type` 은 frontmatter 키 목록에만 남음" 으로 | 보고서 188행이 F-6 에 포함시킨 잔재 |
| `docs/scorecard/design-guideline.md` 30행 | 같은 폴더 서술에 "지금은 git 이 6개 파일 추적" 보충 | 확인 |
| `design-guideline.md` 353행 | `finalize/build` 를 `approve → build` 로 (README 48~49행의 단계명) | `finalize` 검색 결과 없음 |
| `AGENTS.md`·`docs/memory-system.md` | 실재 topic 은 `guardrails.md` 하나이고 목록은 주입 훅이 찾는 이름이며 없는 파일은 관측이 생길 때 만든다고 적음 | 각 83행·84행 |
| `AGENTS.md` 통제 절 | "첫 방어선에도 한계가 있다" 한 줄 추가 | 40행 부근 |

판단한 것 하나. `open-items.md` D-06 은 항목 의미를 지키라는 지시를 따라 "열린 문제" 로 남겼다. 다만 npm 스크립트는 이미 전부 uv 로 통일돼 있어 항목이 사실상 해소된 상태이니, 조율자가 닫을지 정하면 된다.

## 검증

- `uv run --frozen python -X utf8 -m unittest tests.test_collect_news`: 12건 OK.
- unittest 전체: 1093건 실행, 실패 1·오류 14. 기준(1090건 중 실패 1·오류 14)에서 증가 없음. 늘어난 3건은 이번에 추가한 locale 테스트이고 모두 통과한다. 실패·오류 15건은 전부 gitignore 된 `validation/f6-avail-15/_raw/*.companyfacts.json` 부재가 원인이다.
- pytest: 15 failed, 1080 passed. 같은 집합이다.
- `npm run check`: 통과.

## 소유 밖에서 발견한 문제

없음. 레인 H 소유 파일은 건드리지 않았다.

## 남긴 것

- D-06 항목을 닫을지 여부(위).
- 통합 브랜치 merge: 앞선 커밋은 plan 문서 하나(`2370dbe`)다. 커밋 뒤 merge 하고 결과를 아래에 적는다.

## 커밋

- `4101437` fix(collect): 언어만 준 locale 의 국가 코드 매핑
- 문서·보고서 커밋은 이 파일을 포함해 바로 뒤에 이어진다(SHA 는 `git log` 로 확인).
