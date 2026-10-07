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

## 구현 중 결정 (2026-10-07, Opus 5.5 세션)

- **요약 JSON 은 새 키를 늘 낸다.** `tests/test_approval_commands.py` 의 SummaryShapeTest 가 키 구조를 fixture 와 **같음**으로 비교한다. 판단에는 `evidence_up`·`evidence_down`(없으면 빈 목록)과 `three_way`, 제안에는 `evidence_up_after`·`evidence_down_after`(없으면 null)와 `before.evidence_up/down` 을 늘 싣고 fixture 를 맞췄다.
- **빈 칸은 CLI 에서 `--up ""`(승인 페이지는 `--up=`)로 넘긴다.** argparse 의 append 로는 빈 목록을 표현할 수 없어, 빈 문자열만 준 경우를 '없음'으로 읽는다.
- **`revise_judgment` 의 v1.9 검사는 새 항목 전체에 댄다.** 판정 칸만 고치는 수정도 방향 칸이 없으면 막힌다. 그래서 지금 실행(v1.9)의 판단은 세 칸 제안으로만 바뀐다(6단계).
- **트리거 표 메타 칸의 근거 링크는 줄바꿈하지 않는다.** `a{overflow-wrap:anywhere}` 때문에 `EV-` 와 `alphabet-004` 사이가 꺾였다.
- **탭 바는 처음에 `hidden` 이고 JS 가 연다.** UA 기본값 `[hidden]{display:none}` 때문에 패널에 hidden 을 HTML 로 넣으면 JS 없이 볼 수 없다. 패널은 JS 가 숨긴다.
- **이동 대상에 scroll-margin-top 72px.** 고정 탭 바가 이동한 대상(인용 근거 행 등)을 가렸다.
- **서버가 승인 페이지를 연다(별건, 같은 날).** 사용자 요청. `node server.js --approvals` 가 파일이 가장 최근에 바뀐 채점 실행의 승인 페이지를 브라우저로 연다.

## 6단계 결과 (2026-10-07)

- **재분류**: 서브에이전트 5개(Opus) → 기계 대조(숫자·영문 토큰 동일, 한글 분량 90% 이상, 금지 표기·중복·두 칸 빔 0, 변조 사본 10종으로 검사 확인) → 제안 PRP-148~258 반영, counter_evidence 3건은 judge 로 비움. 예외: meta.F2 의 벤치마크 지수 점수(AA 62점 등)는 사실이라 올릴 근거에 둔다. 조율자 수정: tesla.F7 환류 금액 미확인 줄은 판정 칸.
- **counter_evidence 를 비우는 경로가 없었다.** 판단 수정이 그 칸을 `[]` 로 비우는 것만 받고 비우기 전 내용을 이력에 남기게 했다(커밋 `feat(judgments): 판단 수정이 counter_evidence 를 비우는 것만…`).
- **1차 리뷰(round 6)**: needs_fix 5건(tsmc.F9 설비투자 상향 방향, oracle.F8·openai.F7·oracle.F9 신용 지표 줄은 판정 칸 — 규칙 2.8, alphabet.F5 결론 분리·반발 대상 복원)과 렌더러 4건(AA-LCR 절단, 320px 탭 표시, 초안 ⑥ 머리줄, '앞서 매긴'). 제안 PRP-259~263 과 렌더러 수정으로 닫음.
- **확인 리뷰(round 7)**: 4영역 pass. 점수·순위·factor 점수는 재분류 전과 같다.
- **교훈**: 서브에이전트에게 "점수 표기는 판정 칸에만" 같은 보조 규칙을 주면, 사실(벤치마크 점수)을 판정 칸으로 옮기거나 '점'을 '포인트'로 바꾸는 우회가 생긴다. 다음에는 "우리 채점 점수 표기"로 범위를 좁혀 적는다.

## 마무리 (2026-10-07)

- 사람 승인 756c276e → 빌드 → `validate_report_contract --require-html` PASS → Playwright(탭 6개 × 320·768·1280 넘침 0, 세 칸 상자 112, 트리거 글 칸 83%, 탭 사이 앵커 동작).
- 승인 페이지가 500 을 냈다. summary --json 이 1.24MB 로 커져 execFile 기본 maxBuffer(1MB)를 넘었다. 64MB 로 늘렸다.
- 다음 실행 과제는 `output/ai-scorecard-2026-10-rescore/review-parts/` 네 파일의 「다음 실행 과제」에 있다(회사마다 칸이 갈린 같은 유형 사실, 320px 순위표 조정총점 열, Stargate 서술 등).
