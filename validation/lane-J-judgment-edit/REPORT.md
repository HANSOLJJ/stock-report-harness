# 레인 J — 판단 수정 기능, 수집기 실측 결함 수정, 남은 정리 보고서 (2026-10-01)

지시서 `.agents/plans/evidence-layer-2026-09/dispatch/lane-J.md` 를 따랐다. 문서(루트 README·AGENTS·docs)는 고치지 않았다(레인 K).
`SEC_UA` 값은 어디에도 출력·기록하지 않았다(있음·영문 여부만 확인). 수집 빈도 상수는 바꾸지 않았다.

## 커밋

| SHA | 내용 |
| --- | --- |
| `96bb152` | feat(scorecard): 승인 페이지에서 사람이 정성 판단 입력을 고치는 judge (A1~A4) |
| `c55f7f2` | fix(collect): NaN 종가 건너뛰고 직전 유한 종가 사용 (B1) |
| `ed8a1fa` | fix(collect): 가격 수집 회사별 실패 (B2) |
| `5f8eb16` | feat(cli): resolve-cik --json (B3) |
| `713542b` | fix(collect): SEC_UA 영문 사전 검사 (B4) |
| `2ab25ac` | chore(registry): meta·oracle·apple 뉴스 질의 (B5) |
| `135d077` | chore(registry): 상장 12개사 cik 기입 (B6) |
| `9097800` | fix(hooks): PowerShell cmdlet·find -delete·xargs·글롭·상위 폴더 삭제 판정 (C1) |
| `63482f9` | fix(scorecard): plan.md 계약 검증 안내 uv 형식 (C2) |
| `76efe1d` | fix(scorecard): 에이전트 표지 MUSE_TOOL_USE_ID (C3) |
| `9b49f3a` | merge: `HANSOLJJ/revision_checker`(문서 커밋 1건, 충돌 없음) |
| 이 보고서 커밋 | docs(validation): 레인 J 보고서 |

## A. 판단 수정 기능

- `stages.revise_judgment(slug, *, company_id, factor, changes, reason, by)` 와 CLI
  `judge <run_id> --company <id> --factor F1..F9 (--set key=value … | --evidence "문장" … | --json 파일) --reason "…" --by <이름>`.
  - F1·F4·F8: `score`·`evidence`. F3 `criteria`·F5 `grade`(A·H)·F7 `matrix`·F9 `gate_inputs` 는 판정 재료 키와 `evidence` 만 받는다.
    이 factor 들에 `score` 를 주면 "점수 칸은 고치지 않는다" 로 거부한다. F2·F6 은 대상 밖이라 거부한다.
  - 쓴 뒤 `status: new`, `reviewer: <by>`, `reviewed_at: 오늘(UTC)`. 이전 값 7키(kind·score·inputs·evidence·status·reviewer·reviewed_at)는
    항목 안 `revision_history` 에 `{revised_at, revised_by, reason, previous}` 로 쌓는다. `carried_from` 은 지우지 않는다.
  - 형식은 쓰기 **전에** `validate_judgments` 로 검증해 틀리면 아무것도 쓰지 않는다. 쓴 뒤 `load_context` 의 교차 참조(새 판단은 확정 근거만 인용)가
    실패하면 원래 바이트로 되돌린다. 바뀐 값이 없으면 거부한다.
  - 잠금은 `confirm` 과 같다(에이전트 세션일 때만 검사·기록, `LOCK_STAGES` 에 `judge`). reviewer 는 `--by` 값이다.
  - F7 승계 판단 둘(anthropic·openai)은 kind 가 `score` 다. 판정 재료를 주면 `matrix` 로 바뀌고 점수는 규칙이 계산한다(두 키가 다 있어야 한다).
    지시서에 이 경우가 명시돼 있지 않아 내린 판단이다.
  - 근거 문장(`evidence`)은 F3·F5·F7·F9 에서도 고칠 수 있게 했다. 판정 재료만 바뀌고 ✅❌ 근거 문장이 옛 판정을 말하면 서로 어긋나기 때문이다.
- `schema.py`: `revision_history` 선택 키와 검증, 수정 대상 표 `JUDGMENT_EDIT_KIND`·`JUDGMENT_INPUT_CHOICES`.
- `summary --json`: `judgments`(기업×factor 판단. `inputs` 는 판정 종류마다 키가 달라 `[{key, value}]` 목록, `edit_kind`·`revisions`·`score_range` 포함)와
  `judgment_choices`. 픽스처 `tests/node/fixtures/summary.sample.json` 에 같은 키를 더했고 Python 키 구조 테스트(샌드박스=픽스처, 기존 두 실행⊆픽스처)가 통과한다.
- 승인 페이지 `server/approvals.js` 8절 "정성 판단 수정"(승인·취소 절은 9절로 밀림). `?factor=F3` 이면 그 factor 의 모든 기업 판단을 나란히(Q03),
  `&company=<id>` 면 판정 종류에 맞는 입력란(점수 또는 선택 목록)·근거 문장·사유·이름·코드. `POST /approve/<run_id>/judge` 는 일회용 코드 필수,
  기업 id·factor·판정 재료 키를 정규식으로 거르고 CLI `judge` 를 `execFile` 로 부른다. 근거·사유·이름은 `--opt=value` 로 넘겨 `-` 로 시작해도 옵션으로 읽히지 않는다.
  근거 문장은 원래 값과 다를 때만 넘긴다. 성공하면 "판단 해시가 바뀌었다 — 에이전트에게 다시 계산·리뷰를 시킨 뒤 새로고침해 승인한다" 를 보인다.
  루프백·코드 실패 5회 잠금·이스케이프·run_id 정규식은 기존 경로를 그대로 탄다.

## B. 수집기 실측 결함

1. NaN 종가: `fetch_quote` 가 유한하지 않은 종가 행을 건너뛰고 기준일 이하 마지막 유한 종가와 그 날짜를 쓴다. 건너뛴 날짜(쓴 종가보다 뒤)는
   `skipped_nonfinite_close` 로 반환하고 collect 요약 행에도 싣는다. 전부 NaN 이면 건너뛴 행 수를 담은 오류다.
2. 회사별 실패: `_collect_prices` 가 조회·관측 생성·중복·스키마 검증을 회사 단위로 한다. 실패한 회사는 `failed` 행, 나머지만 기록한다.
   **중복(같은 기업·지표·기준일)도 회사 단위 failed 로 바꿨다**(이전에는 명령 전체 SchemaError). 부분 실패 뒤 다시 돌리면 빠진 회사만 기록되게 하려는 것이다.
   기존 테스트 `test_same_observation_twice_is_refused` 의 기대를 이에 맞췄다(파일 무변경은 그대로 단언).
3. `resolve-cik --json`: JSON 한 줄 `{rows, applied}`. rows 는 모듈 행에 `current_cik` 를 더한 것.
4. `SEC_UA` 사전 검사: `evidence_lib.sec_user_agent()` 가 영문 밖 글자면 "SEC_UA 는 영문으로 적는다(HTTP 머리글 제약) …" RuntimeError(값 미포함).
   뉴스 UA(`user_agent_for("news")`)도 이 함수를 거친다. `collect` 는 공시를 모을 때만 SEC_UA 를 읽고 회사별 failed 로 남긴다(가격은 영향 없음).
   파일에서 읽는 뉴스(`--from-file`)는 UA 를 거치지 않는다.
5. 뉴스 질의: `registry.set_company_field` 로 meta(`Meta Platforms`, `META stock`)·oracle(`Oracle Corporation`, `ORCL`)·apple(`Apple Inc`, `AAPL`). 3줄만 바뀌었다.
6. CIK 기입: `resolve-cik --apply` 를 실응답으로 1회. 결과는 아래 표.

### B-6 CIK 기입 결과 (2026-10-01 SEC `company_tickers.json` 실응답)

| company_id | ticker | cik | status |
| --- | --- | --- | --- |
| alphabet | GOOGL | 1652044 | resolved |
| amazon | AMZN | 1018724 | resolved |
| microsoft | MSFT | 789019 | resolved |
| meta | META | 1326801 | resolved |
| tsmc | TSM | 1046179 | resolved |
| alibaba | BABA | 1577552 | resolved |
| apple | AAPL | 320193 | resolved |
| nvidia | NVDA | 1045810 | resolved |
| palantir | PLTR | 1321655 | resolved |
| spacex-xai | SPCX | 1181412 | resolved (사용자 후보와 일치) |
| tesla | TSLA | 1318605 | resolved |
| oracle | ORCL | 1341439 | resolved |
| anthropic·openai | — | — | unlisted (쓰지 않음) |

12건 모두 레인 M 표와 같다. 실제 레지스트리에 cik 가 생겨 "cik 없음" 을 전제한 샌드박스 테스트 7건이 깨졌다. 샌드박스가 레지스트리를 복사할 때
수집기 전용 키(cik·news_queries)를 빼고 시작하게 했고(`tests/test_collect_stage.copy_registry_without_collector_keys`),
`test_real_registry_is_untouched` 는 "실제 cik 가 픽스처 매핑과 같다" 는 `test_real_registry_has_the_resolved_ciks` 로 바꿨다.

### 실제 조회 확인 (각 1회, 임시 실행 `ai-scorecard-livecheck-lane-j`·수집 캐시는 저장소 밖 임시 폴더, 커밋 없음)

- 가격(as_of 2026-10-01, 가장 최근 거래일 09-30): 원시 일봉 꼬리를 직접 보니 **이번 조회 시점에는 12개사 모두 09-30 종가가 채워져 있어 NaN 행이 없었다.**
  collect 결과 12개사 `collected`, `close_date 2026-09-30`, `vendor_market_cap`, 비상장 2개사 `skipped_unlisted`. 따라서 NaN 대체 경로는
  실데이터로 재현하지 못했고, yfinance 스텁 테스트(`test_nonfinite_latest_close_falls_back_to_last_finite`)와 NaN 관측 파일을 쓴
  회사별 실패 테스트(`test_invalid_observation_fails_that_company_only`)로만 확인했다.
- 뉴스(질의를 바꾼 3개사, SEC_UA 영문 UA): 3개사 `collected`. meta `Meta Platforms` 73건·`META stock` 100건, oracle `Oracle Corporation` 73건·`ORCL` 100건,
  apple `Apple Inc` 75건·`AAPL` 102건. 발행일 없는 기사 0건. 후보 창 2026-04-04~10-01 안 후보 523건. 레인 M 의 F-M-1(latin-1 오류)은 재현되지 않았다.
- CIK: 위 표.

## C. 남은 정리

1. 보호 훅(`scripts/hooks/guard.py`, README 표 갱신). 레인 H 의 "쓰기 대상일 때만 막고 읽기는 통과" 를 유지하며 더했다.
   - PowerShell `Set-Content`·`Add-Content`·`Out-File`·`Remove-Item`·`Move-Item`·`Copy-Item`·`New-Item`·`Rename-Item`·`Clear-Content` 와 기본 별칭의 경로 인자
     (`-Path x`, `-Path:x`, 위치 인자).
   - 지우기·옮기기의 원본은 보호 경로를 품은 상위 폴더도 대상이다(`rm -rf output`, `rm -rf .`, 승인 파일이 든 실행 폴더).
   - `find … -delete`·`-exec <변경 동사>`: 시작 경로가 보호 경로를 품으면 막는다. 경로 없는 `find . -name x -delete` 는 저장소 전체라 막힌다(보수적).
   - `xargs <변경 동사>`: 명령 전체의 보호 경로 언급과, 같은 명령의 다른 명령이 받은 경로가 보호 경로를 품는지를 본다.
   - 글롭: 보호 경로(없는 파일 포함)와 조각 단위로 대조하고 파일 시스템 전개 결과도 본다. `*` 는 `/` 를 넘지 않는다.
   - **동작 변경 하나**: `cp`·`install`·`Copy-Item` 은 목적지만 쓰기 대상이다. 이전에는 원본이 보호 경로여도 막았다(`cp -r output/<보호 실행> /tmp/x`).
     레인 H 규칙(읽기는 통과)에 맞춘 것이다. 목적지가 보호 경로면 계속 막는다.
   - 실제 저장소에서 판정 시간은 0.05초 이하였다(`rm -rf .venv` 0.048초).
2. `render_md.py` 130행: `uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id>`.
3. `AGENT_ENV_MARKERS` 에 `MUSE_TOOL_USE_ID`. `MUSE_RELEASE_INFO` 는 넣지 않았다.
4. `validation/recheck_worker_final.py`(고치지 않음): 66행이 `stages.approve(SLUG, approved_by=…)` 를 부른다. 지금은 `approve` 본체 첫 줄의
   `refuse_agent_session` 이 에이전트 세션을 거부하므로, 에이전트 세션에서 이 스크립트의 "잘못된 승인자 거부" 검사는 승인자 검증이 아니라
   에이전트 세션 거부 메시지로 채워진다(검사 의도와 다른 이유로 통과). 확인을 위해 `stages.approve` 를 담은 명령을 실행하려 하자 보호 훅이 막았고,
   우회하지 않았다. 위 판단은 코드 판독 결과다.

## 승인 페이지 수동 확인 (레인 D 방식)

`SCORECARD_CLI="node tests/node/fake_scorecard_cli.js" PORT=3917 node server.js --approvals` (가짜 CLI, 픽스처).

1. `GET /approve/ai-scorecard-2026-11-x?factor=F3&company=nvidia` → 200, NVIDIA·OpenAI 의 F3 판단이 나란히, NVIDIA 입력란(imitation·revenue_model·
   acceleration·door_closed 선택 목록, 현재값 선택), 근거 문장의 `<b>` 는 글자로 보인다.
2. `POST …/judge` 코드 000000 → 403.
3. 브라우저(Playwright)로 imitation=pass, 근거 두 줄(둘째 줄은 `-` 로 시작), 사유·이름(한글)·터미널 코드 입력 후 제출 → 200, 종료 코드 0,
   가짜 CLI 가 받은 인자 `judge ai-scorecard-2026-11-x --company nvidia --factor F3 --set imitation=pass --set revenue_model=pass --set acceleration=fail
   --set door_closed=fail --evidence=✅모방 불가능성 — CUDA 생태계 전환 비용 --evidence=- 하이픈으로 시작하는 둘째 문장 --reason=잣대 맞춤(Q03) --by=홍길동`,
   해시 변경 안내 표시. 360px 폭에서 입력란이 화면 안에 들어온다.
   (같은 POST 를 Windows `curl --data-urlencode` 로 보내면 한글 인자가 깨졌다. curl 이 인자를 cp949 로 보낸 탓이고 브라우저에서는 그대로다.)
4. 실제 CLI 경로는 Python 테스트(`tests/test_judge.py` CLI 3건)가 덮는다. 진짜 실행에 대한 judge 는 하지 않았다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` (merge 뒤) | 1146건, 실패 1·오류 14. 기준선(1115건 중 실패 1·오류 14, 전부 원자료 부재)과 **실패·오류 집합이 같다**. 늘어난 31건은 이번 테스트 |
| `uv run --frozen pytest -q` (merge 뒤) | 15 failed, 1133 passed. 실패 테스트 13개(서브테스트 포함 15)가 위 집합과 같다 |
| `npm run check` | 종료 코드 0 |
| `npm run test:node` | tests 15·pass 15·fail 0 (판단 수정 5건 추가) |
| 기존 두 실행 | baseline·obsreg `approval_valid: true`. 저장 `results_hash` baseline `0942c342…`·obsreg `4a3f6c05…` 이고, 재계산 해시(baseline `200d7b01…`, obsreg `4a3f6c05…`)가 companies.json 변경 전후로 같다. baseline 의 저장·재계산 불일치는 context-notes 의 기존 결정("그대로 둔다") 사항이다 |
| `git status --short output/` | 변경 없음 |
| `git diff --stat HANSOLJJ/revision_checker...HEAD` | 소유 파일 22개만(scripts/scorecard 7·CLI·hooks 2·server/approvals.js·companies.json·tests 10) |
| `git merge HANSOLJJ/revision_checker` | 성공(문서 커밋 1건, 충돌 없음), 위 테스트는 merge 뒤 결과 |

## 소유 밖에서 발견한 문제 (고치지 않음)

- 루트 문서(README·AGENTS·docs)에 judge 명령·판단 수정 절·`resolve-cik --json`·훅의 새 판정이 아직 없다. 레인 K 몫이다.
- `validation/recheck_worker_final.py` 는 위 C-4 대로 에이전트 세션에서 의도와 다른 이유로 통과한다.

## 남긴 것

- NaN 대체 경로의 실데이터 재현(야후가 최근 일봉 종가를 비워 두는 시간대에 다시 조회해야 한다).
- 승인 페이지의 F 번호 옆 factor 이름 표시(요약에 factor 라벨이 없어 F1~F9 와 판정 종류 이름만 보인다).
- F1 부품형 상한(v1.8 `component_only_cap` 2, 예: nvidia)은 judge 가 아니라 calculate 가 `error` 로 잡는다. judge 는 범위(0~5)만 본다.
- 최종 커밋 SHA 는 이 보고서 커밋이다(worker_done 본문에 적는다).
