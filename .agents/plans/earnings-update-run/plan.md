# 실적 반영 실행 계획

## 왜

실적이 하나 나올 때마다 14개사 정성 판단 191건을 전부 다시 매기고 4영역 리뷰를 실행 전체로 하는 것은 무겁다(2026-10-21 사용자). 실적을 낸 회사와 그 사건이 닿는 곳만 다시 매기고, 나머지는 이어받되 움직이지 않았음을 코드로 증명하는 세 번째 실행 종류를 만든다. 결정 D1~D5 와 이유는 `context-notes.md` 에 있다.

## 무엇이 달라지나

| | 정기 실행 | 기업 추가 실행 | **실적 반영 실행 (새로)** |
|---|---|---|---|
| 다시 매기는 판단 | 14개사 전부 | 더한 회사 | 갱신 회사 전부 + 닿은 (회사, 항목) + 선언한 추가 항목 |
| 가격 | 전부 새로 | 이어받음 | 전부 새로 (D2) |
| 이전 트리거 확인 | 전부 | 전부 | 갱신 회사 것 + 기한이 지난 것 |
| 리뷰 | 실행 전체 | 신규 기업 + 잣대 + `diff` | 갱신 범위 전수 + 같은 층 경쟁사 비교 + `diff` (D5) |
| 막는 검사 | 재판단 누락 | 신규 기업 재판단 누락 | 범위 재판단 누락, 가격일까지 실적 낸 회사 빠짐, 판단 나이 120일 초과 (D2·D4) |

## 설계

- **규칙 v3.1.** `scorecard/rules/v3.1.json` = v3.0 점수 규칙 그대로 + `policies.rejudge.update_runs`(나이 상한 120일, 실적 공시 형식). `rules.md` 2.9절에 세 번째 실행 종류를 적는다. v3.0.json 을 고치지 않는 이유는 그 해시가 v30full 확인 기록에 묶여 있기 때문이다(D6).
- **실행 선언.** `init <slug> --from-run <이전> --update-companies a,b --update-reason "…"`. `run.json` 에 `continued_from.updated_companies` 와 회사별 마지막 전체 갱신일 `refreshed_at` 을 둔다. `refreshed_at` 은 이전 실행 값을 잇고(없으면 이전 실행 기준일), 갱신 회사는 이번 기준일로 바꾼다.
- **범위 계산** (새 모듈 `scripts/scorecard/update_scope.py`, research 와 계약 검증이 같이 부른다).
  - 다시 매겨야 하는 판단 = 갱신 회사의 정성 판단 전부 ∪ 이번 실행에서 새로 확정한 근거·발동한 트리거가 가리키는 (회사, 항목)의 판단 전부 ∪ 선언한 추가 항목(`run.json` `update_scope.extra`, 이유 필수).
  - 추가 항목 선언은 `scorecard_cli.py scope <run_id> --add company:F5 --reason "…"`. 리뷰가 같은 층 경쟁사에 새 잣대를 대야 한다고 보면 이 명령으로 넣는다(D5, Q03).
  - 실적 감지: 갱신 회사가 아닌데 마지막 전체 갱신일 뒤, 가격 기준일까지 8-K Item 2.02·10-Q·10-K·20-F 를 낸 회사가 있으면 막는다. `candidates.json` 공시 후보에 `items`·`report_period` 를 남겨(이미 `collect_filings` 가 읽는다) 실행 폴더 안에서 판정한다. 6-K 만 내는 TSMC·Alibaba 는 기계로 못 가르므로 research.md 에 기간 안 6-K 목록을 싣고 리뷰가 본다.
  - 나이: `as_of − refreshed_at > 120일` 인 회사가 갱신 회사가 아니면 막는다(D4).
- **검사 연결.** `validate.rejudge_findings` 가 실적 반영 실행이면 범위의 판단만 본다. 범위 밖 승계 판단은 허용한다. 이전 트리거 확인은 갱신 회사 것만 요구하고, 기한이 지난 관찰 트리거는 회사와 무관하게 지금처럼 막는다.
- **`diff`.** 1층(입력 가법성)과 2층(점수 투영)은 판단 ID·회사 단위라 v3.0 판단도 견줄 수 있다. 층 규칙에서 멈추는 가드를 걷고 v3.0 실행으로 시험한다. 실적 반영 실행 모드를 더한다: 허용 = 갱신 회사의 모든 입력, 범위 판단의 수정, 모든 회사의 가격 관측(price·market_cap), 출처 추가. 2층은 범위 밖 회사의 항목 점수가 ⑥ 을 빼고 같아야 한다(합계·순위는 참고).
- **출력.** research.md 에 갱신 범위 절(갱신 회사·닿은 항목·추가 항목·회사별 나이·기간 안 6-K). 초안과 HTML 의 회사 카드에 "반영 기준 YYYY-MM-DD"(`refreshed_at`). `history.csv` 의 `change_type` 은 `earnings-update`.
- **리뷰·문서.** `score-review` 에 실적 반영 실행의 리뷰 범위(D5)를 적고, 새 스킬 `score-update` 를 둔다. AGENTS.md·guide.md·structure.md·workflow.html 에 세 번째 실행 종류를 넣는다.

## 단계 (단계 하나 = 커밋 하나)

| # | 할 일 | 주로 고칠 곳 | 검증 |
|---|---|---|---|
| U1 | 규칙 v3.1 | `scorecard/rules/v3.1.json`, `docs/scorecard/rules.md`(머리말·2.9·개정 이력), `schema.validate_rules`(새 정책 키) | v3.0.json 해시 그대로, v3.1 로 v30full 입력을 계산하면 점수가 같다, 문서 대조 테스트 |
| U2 | 실행 선언 | `stages.init_run`·`_inputs_from_run`, `schema.validate_run`, `scorecard_cli.py init`, `validate.is_regular_run`·`is_update_run` | `--update-companies` 가 `run.json` 에 남고 `refreshed_at` 이 이어진다, `--add-companies` 와 같이 주면 거부 |
| U3 | 범위 계산과 검사 | 새 `update_scope.py`, `validate.rejudge_findings`, `stages.research`·`previous_triggers`, `collect_filings` 후보 필드, `scorecard_cli.py scope` | 갱신 회사 판단 하나만 안 고치면 그 판단을 지목, 범위 밖 승계는 통과, 다른 회사 근거를 새로 확정하면 그 (회사, 항목)이 범위가 된다, 8-K 2.02 를 낸 회사가 빠지면 막힘, 나이 121일 막힘·120일 통과 |
| U4 | `diff` | `compare.py`, `scorecard_cli.py diff` | v3.0 기업 추가 쌍을 견줄 수 있다, 범위 밖 회사의 ⑥ 만 바뀌면 통과·① 이 바뀌면 위반, 범위 밖 회사에 가격 아닌 관측이 더해지면 위반 |
| U5 | 출력 | `render_md`(research 범위 절, 초안 반영 기준일), `render_html` 회사 카드, `render_csv` change_type | v30full 을 다시 그려도 초안 해시가 그대로(정기·추가 실행은 표시가 안 바뀐다), 합성 실적 반영 실행에 범위 절·반영 기준일이 보인다 |
| U6 | 리뷰·문서·스킬 | `.claude/skills/score-review`, 새 `.claude/skills/score-update`, AGENTS.md, guide.md, structure.md, workflow.html | 문서만. `.agents/skills` 사본 동기화 |
| P | 첫 실적 반영 실행 | `init ai-scorecard-2026-10-q3a --from-run ai-scorecard-2026-10-v30full --rule v3.1 --update-companies alphabet,spacex-xai,…` → 가격 전부·공시 전부 수집 → 실적 감지로 범위 확정 → 판단 → research → calculate → draft → `diff` → 리뷰 | 확인 대기에서 멈춘다. 확인은 사람이 한다 |

모든 단계에서 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 를 돌린다. 커밋에 공동 작성자 줄을 넣지 않는다. 이정표마다(U1~U3, U4~U5, U6~P) 사용자에게 보고한다.

## 위험

- **확인 해시.** v3.0.json 과 기존 실행 파일을 건드리지 않는다. 새 동작은 `updated_companies` 가 있는 실행에서만 탄다. 기존 실행 재계산 테스트(`RecomputeTest`)가 모든 단계에서 통과해야 한다.
- **범위 누락.** 범위는 근거·트리거 기록에서 계산하므로, 다른 회사에 닿는 사실을 근거로 올리지 않으면 범위에서 빠진다. 사실·출처 리뷰가 갱신 회사 공시에서 다른 회사에 닿는 사실을 놓쳤는지 본다.
- **6-K 회사.** TSMC·Alibaba 의 실적 6-K 는 기계로 못 가른다. research.md 목록과 리뷰로 메운다.
- **diff 가드 해제.** v3.0 판단 ID 가 층·사업까지 담아(`alphabet.F2.cloud`, `alphabet.F1.search`) 유일한지 테스트로 먼저 확인한다.
