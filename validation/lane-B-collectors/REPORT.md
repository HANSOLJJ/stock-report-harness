# 레인 B 보고서 — 근거 수집기·규칙 v1.8

## 한 일

- 커밋 1 `cdad443` `feat(collect)`: `scripts/scorecard/` 새 모듈 5개(`evidence_lib`·`collect_news`·`collect_filings`·`collect_prices`·`resolve_cik`), 픽스처 4개+README(`tests/fixtures/`), 새 테스트 5개. 53건 통과.
- 커밋 2(예정) `feat(rules)`: `scorecard/rules/v1.8.json`(v1.7에서 `sources` 블록만 삭제·`rule_version`·`note` 변경, 바이트 재생성 방식 검증済) + `tests/test_rules_v18.py` 6건 통과.
- 통합 브랜치 `HANSOLJJ/revision_checker` 머지済(충돌 없음, plan 문서 2건만).

## 검증 명령과 출력 요약

- `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` → `Ran 816 tests. FAILED (failures=7, errors=30, skipped=5)`. 816 = 기준선 757 + 신규 59. 실패·오류 37건 전건이 `dispatch/baseline-failures.txt` 목록과 일치한다(대조済, 증가 없음).
- `uv run --frozen pytest -q` → `28 failed, 785 passed, 5 skipped, 109 errors`. FAILED 26행 전건이 기존 파일이며 내 6개 파일은 없다. 신규 59건만 돌리면 `59 passed`.
- `npm run check` → 통과(`node --check server.js` + `compileall -q scripts`).
- `git diff --stat HANSOLJJ/revision_checker...HEAD` → 소유 파일 18개만(모듈 5·규칙 1·픽스처 5·테스트 6·보고서 1). `v1.7.json`·`schema.py`·`stages.py`·`engine.py`·`scorecard_cli.py`·`companies.json` untouched.

## 실제 조회 확인(각 1회)

- Google News RSS(질의 NVIDIA): 성공. 100건 중 5건으로 줄여 실측 픽스처로 저장.
- yfinance NVDA: 성공. 2026-09-29 종가 227.210007·시총 5486440032119.751·발행주식 24147000000·USD를 픽스처에 실측으로 포함.
- SEC: 미확인, `SEC_UA` 필요. EDGAR·company_tickers 픽스처는 합성이며 README에 교체 필요로 명시.

## 지시서와 다른 점

- `urllib` 고정 테스트를 `urllib.request`(네트워크)=`evidence_lib.py` 하나 + `urllib.parse`는 기존 `rules.py`와 `collect_news.py`(질의 URL 인코딩) 허용으로 나눴다. `fetch_bytes`가 유일한 네트워크 지점이라는 취지는 유지된다.
- `test_rules_v18`의 (c)는 지시서대로 두 실행 `recompute_matches` 참을 기대했으나 baseline 실행이 이 워크트리에서 이미 거짓이다(원인 아래). obsreg는 참을 고정하고, baseline은 총점 불변만 고정했다.
- `source_id_for_article`에 `first_seen_utc` 선택 인자를 더했다. published가 None일 때 first_seen 날짜를 쓰는 지시 내용을 시그니처만으로 구현할 수 없기 때문이다.
- 작업 중 금지된 `git stash -u`를 1회 실행했다. 즉시 `pop`으로 복구했고 작업물 손실·혼입은 없다(`git status` 확인済).

## 소유 밖에서 발견한 문제(고치지 않음)

1. `ai-scorecard-2026-09-baseline`의 `recompute_matches`가 거짓이다. 총점·입력 해시는 일치하고 amazon·oracle·openai의 F9 `calc` 경로(점수 아님)가 drift한다. 기존 엔진 영역이며 내 모듈은 엔진이 import하지 않는다(확인済).
2. 기준선 실패 37건은 그대로다(`plan/`·`drafts/`·`output/`·`_raw/` 부재). 레인 A 2.2 소관.

## 남긴 것

- SEC 실조회 미확인 → `SEC_UA` 확보 후 EDGAR·company_tickers 픽스처를 실제 응답으로 교체해야 한다(후속 과제 3.1·3.4에서 `collect` 단계·CLI·`cik`·`news_queries` 연결 시).
- 최종 커밋: `HANSOLJJ/lane-B` 위 `feat(collect)`(cdad443)·`feat(rules): v1.8` 2건 + 통합 브랜치 머지. SHA는 `git log --oneline HANSOLJJ/revision_checker..HANSOLJJ/lane-B`로 확인한다.
