# 맥락 메모 — 근거 세 칸 · 트리거 표 · 탭

결정과 그 이유, 조사에서 확인한 제약을 적는다. 구현 중 내린 결정은 아래에 날짜와 함께 덧붙인다.

## 사용자 결정 (2026-10-07)

- **근거를 세 칸으로 나눈다.** 계기는 아마존 ① 판단이다. 점수와 반대 방향인 사실(메타 Muse 차단, UBS 챗봇 추천 조사)이 5점을 받치는 근거 사이에 섞여 읽혔다. 사용자: "근거에 점수를 높게 줄 근거, 낮게 줄 근거 이렇게 나누는 게 맞지 않겠어?"
- **애매한 문장은 판정 칸이 받는다.** 결론·저울질·미확인은 판정 칸, 방향이 분명한 사실만 올릴·내릴 칸. 표는 plan.md 「분류 기준」.
- **지금 실행에 적용한다.** 재승인 비용을 설명했고 사용자가 "지금 실행에 적용"을 골랐다. 이어서 "어차피 다시 채점할 거라서 채점할 때마다 제대로 근거 분류가 되게 작성해야 함" — 형식을 한 번 바꾸는 것이 아니라 **쓰는 시점(judge·propose)과 검증기가 강제**해야 한다는 뜻이다.
- **트리거 표는 두 덩어리.** 사용자가 열 폭 조정·카드 목록 대신 "열을 합쳐 두 덩어리"를 골랐다.
- **첫 탭은 요약 카드와 순위표만.** 지도(산점도)는 요약 탭 맨 아래에 둔다(Fable 세션 판단, 사용자가 계획 승인으로 수용).
- **구현은 Sonnet 5.5 또는 Opus 세션이 한다.** Fable 5.1 세션은 조사·설계·계획 파일까지만 했다.
- **역할(같은 날 먼저 적용됨):** 근거 확정과 제안 반영·거부는 에이전트가 한다. `stages.decide_proposal`·`undo_proposal` 의 에이전트 세션 거부를 사용자가 직접 주석 처리했고 AGENTS.md·guide.md·스킬에 반영했다(커밋 `feat(control): …`). 승인·승인 취소(`approve`·`revoke`)의 거부와 훅 차단은 그대로다.

## 설계 선택과 이유

- **`evidence` 를 판정 칸으로 남기고 `evidence_up`·`evidence_down` 을 더한다.** `evidence` 를 객체로 바꾸면 `j["evidence"][0]`·`" ".join(j["evidence"])` 를 쓰는 테스트 수십 개와 승인 페이지 textarea·node fixture 가 전부 바뀌고, 옛 실행 네 개의 파일 바이트 해시가 묶여 있어 옛 모양도 계속 읽어야 한다. 선택 키 둘을 더하는 쪽이 옛 실행과 공존하면서 가장 적게 바뀐다. 지금 실행 114개 중 100개가 이미 첫 줄이 판정 문장이라 판정 칸으로 자연스럽다.
- **`counter_evidence` 를 재사용하지 않는다.** "counter" 는 판단에 반대한다는 뜻이라 낮은 점수에서는 올릴 근거가 되어 방향이 뒤집힌다. 방향 키(`up`/`down`)가 분명하다. v1.9 이상에서는 비어 있어야 한다.
- **정확한 키 집합을 요구하는 검사는 완화한다.** `_validate_revision_history` 의 `previous` 는 7키 정확 일치, 제안 스냅숏은 4키 정확 일치다. 10-test 4건·rescore 114건의 옛 이력과 proposals 147건이 그 모양이라, "필수 + 선택 up/down" 으로 바꾼다. `JUDGMENT_REVISION_FIELDS`·`PROPOSAL_SNAPSHOT_KEYS` 자체는 바꾸지 않는다.
- **규칙 버전 v1.9 로 켠다.** `self_contained` 검사가 이미 `_rule_at_least(ctx.rules.version, (1, 9))` 로 켜진다(validate.py 150-151, 187-194). 같은 방식. 규칙 내용이 바뀌는 것이 아니라 v1.10 을 만들지 않는다(사용자: 문서 늘리지 말 것).
- **쓰기 시점 강제는 `revise_judgment` 안에서 한다.** judge·propose 반영이 모두 이 함수를 지난다(structure.md 162행). 규칙 버전은 `run.json` 의 `rule_version` 으로 읽는다.
- **마크다운 트리거 표는 그대로 둔다.** `tests/test_trigger_render.py:44,55` 가 열 문자열을 고정하고, obsreg 초안 트리거 절은 바이트 일치 테스트(91-100)가 있다. HTML 만 두 덩어리로 바꾼다.
- **탭은 JS 없이도 읽히게 한다.** `html.js` 클래스가 있을 때만 `hidden` 패널을 숨긴다. 인쇄는 전부 펼친다.

## 조사에서 확인한 제약 (2026-10-07, 세 Explore 세션)

### 판단 자료 구조
- `validate_judgments`(schema.py 1119-1199): 필수 `judgment_id, company_id, factor, kind, score, inputs, evidence, reviewer, reviewed_at, status`, 선택 `counter_evidence, source_ids, carried_from, note, previous_judgment_id, superseded, evidence_ids, revision_history`. `_expect_keys` 는 모르는 키를 거부하므로 새 키는 반드시 optional 에 올린다.
- `evidence` 제약은 "공백 아닌 문자열이 하나 이상인 리스트"뿐이고 계산(results)에는 들어가지 않는다. `SCORE_TEXT_RE`(1223)는 evidence.json 의 `conditional_impact` 에만 쓴다. 판정 칸에는 "5점" 같은 표기가 있으므로 그 검사를 판정 칸에 대면 안 된다.
- `revise_judgment`(stages.py 1118-1180): `previous = {k: … for k in JUDGMENT_REVISION_FIELDS}`, `new["evidence"] = [...]`, 바뀜 비교는 `(kind, score, inputs, evidence)`, evidence_only 면 status·reviewer 유지. 쓰기 전 `validate_judgments`, 쓴 뒤 `load_context`, 실패 시 원파일 복원.
- `undo_proposal`(1353-1412) 복원은 `for k in JUDGMENT_REVISION_FIELDS: new[k] = prev[k]` 라 키를 늘리면 옛 `applied.previous` 에서 KeyError 가 난다 → `get`/`pop` 으로.
- judgments 해시는 **파일 바이트**(engine.py `input_hashes`)다. 옛 실행 파일은 바꿀 수 없고, `init --from-run` 은 항목을 그대로 복사한다.
- 지금 실행: 판단 114개 전부 `revision_history` 있음, `counter_evidence` 비어 있지 않은 3건(`tsmc.F5.strict54`, `anthropic.F5.impl48`, `openai.F5.impl48`, 옛 감사 문면 "별표 G" 등), `superseded` 5건, proposals 147건 모두 accepted.
- 옛 실행 현황: baseline v1.5(carried 114), obsreg v1.7(carried 105/new 9, 승인·빌드·보호 경로), 10-test v1.8(revision_history 4건, 승인), rescore v1.9(승인 2026-10-07, 빌드됨).

### 승인 보호
- `protect_approved_run`(stages.py 810-836): 승인이 유효한 실행에서 **에이전트 세션은 거부**, 사람 세션은 경고 후 진행. 부르는 곳: collect prices, research, calculate, draft, review-template --force, confirm, judge(revise_judgment), 기업 요약 수정, 제안 번복. 그래서 6단계 전에 사용자의 승인 취소가 필요하다.
- 승인 전 검증 버그를 2026-10-07 에 고쳤다(`validate.py` 승인 여부 검사가 `check_html_if_present=False` 일 때 돌지 않게). 옛 `report.html` 이 남은 실행에서 재승인이 막히던 문제다.

### 렌더러·HTML
- `render_document`(render_html.py 1667-1761) 절 순서: header → `#kpis` → 01 지도 → 02 순위표 `#mainTable` → 03 카드 `#cards` → 04 원자료 → (05 자료 확보 `#availability`, data_availability.json 있을 때) → 방법·규칙(+`GLOSSARY_SLOT` → 용어 색인 `#code-index`·감사 기록 링크) → 트리거 → References(`CITED_SLOT` → `#cited-evidence`) → `footer#disclaimer`. 번호는 01~04 하드코딩, 그 뒤 `n = 5 if avail else 4`.
- CSS 는 `css()`(79-368) 한 블록, JS 는 `js()`(373-408) 한 블록. 외부 리소스는 Pretendard CDN 스타일시트 하나.
- 절 사이 앵커: 트리거 「근거」 → `#ev-…`(59건), 원자료 현금 정의 고지 → `#idx-F9`·`#idx-F6`(2건), References 의 `SRC-SEC-FACTS-F6` → `#idx-F6`(1건, `TERM_RE` 버그), 순위표 행 클릭(JS) → `#card-*`(14건), 머리말 `survey_note` → `#availability`(조건부). `#ix-…` 는 가리키는 곳이 없다.
- 표 CSS: `th,td{white-space:nowrap}`, `td.text,th.text{min-width:180px;white-space:normal}`(139), `.narrow{min-width:0}`(219, 효과 없음). 앞 열 sticky 는 `#mainTable`·`#availTable` 에만. 반응형 구간 1180·860·640·520px, 320px 전용 쿼리 없음. 트리거 표에는 모바일 처리가 없다.
- 트리거: `TRIGGER_COLUMNS`(render_md.py 171) 8열, `active_trigger_rows` 가 watching 만. 지금 실행 watching 56·withdrawn 22·fired 2. 관찰 사실 107~468자(중앙값 225), 조건 20~756자, 재검토 26~330자, 근거 EV 0~5개.
- `_validate_html`(validate.py 353-376)은 출처 마커·생성기·results 해시 meta·투자 유의 문구·미렌더 f-string·viewport·`data-company` 만 본다. 구조는 보지 않는다.
- 지금 빌드 `report.html`: 517,439바이트, `<h2>` 7, 카드 14, script 1, 트리거 56행.

### 테스트 지형
- **빌드된 obsreg `report.html` 을 그대로 읽는 테스트**(fix64·65·66·74·76·77·78·79·80·81)는 렌더러를 바꿔도 영향이 없다. 단 fix66(76-94, 175-179)·fix78(47-48)·fix76(61-65)·fix65(95-97, 151)·fix79(117-119)는 빌드 파일을 **지금 코드의 상수·함수 결과**와 비교하므로 라벨 상수를 바꾸면 깨진다.
- **메모리에서 다시 렌더하는 테스트**(fix54_render·fix66 mem_html·add04a·fix61~63·fix55/56 stage2·trigger_render·hash_binding 임시 사본 빌드)는 새 렌더러를 지난다. fix54_render 는 `id="card-{cid}"`~`</details>` 로 카드를 자르고 `evidence_block` 의 `lines[-1][1]` 로 초안·HTML 일치를 본다. hash_binding 은 obsreg 사본을 실제로 빌드해 승인 검사까지 통과해야 한다(옛 모양 렌더 보호).
- **evidence 를 문자열 목록으로 전제하는 테스트**: test_proposals·test_judge·test_self_contained(위치 표기 `"nvidia.F5 근거[0]"`)·node approvals.test.js(480-481, 592-612)·fixture summary.sample.json. `tests/test_approval_commands.py:113-120` 의 `key_paths` 는 리스트 안 문자열을 무시하므로 새 키는 fixture 에 더해야 한다.
- 샌드박스: `tests/test_collect_stage.py:47-75` `Sandbox`(slug `ai-scorecard-2026-09-evidence`, `init_run` 이 v1.8), `FlowBase`(approval_commands 61-109), `ProposalBase`, `human_env`(run_lock 25-32).
- 실행 명령: `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`(지금 1280개)와 `npm run test:node`(21개).

## 범위 밖으로 둔 것
- `TERM_RE`(render_html.py 1511) lookbehind 버그, Pretendard CDN, 방법 절 ⑨ "조달 여력은 신용등급으로"(사용자 원본 문장), 리뷰 영역 파일의 「다음 실행 과제」, `protect_approved_run` 의 에이전트 거부 해제.
