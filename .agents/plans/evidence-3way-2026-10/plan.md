# 판단 근거 세 칸 분류 · 트리거 표 두 덩어리 · 리포트 탭 — 10월 재채점 실행에 적용

구현 세션 메모: 이 계획은 Fable 5.1 세션이 조사·설계했고, **구현은 Sonnet 5.5 또는 Opus 세션이 한다**(2026-10-07 사용자 지시). 구현 세션은 0단계부터 순서대로 간다. 사용자 결정은 아래 「결정 사항」에 전부 있으니 다시 묻지 않는다.

## Context

- **문제 1 (근거).** 판단(`judgments.json` 항목)의 `evidence` 는 문장 목록 하나다. 그래서 아마존 ① 처럼 점수와 반대 방향인 사실(Muse 차단, UBS 챗봇 조사)이 5점을 받치는 근거 사이에 섞여 읽힌다. 사용자는 근거를 **판정 / 올릴 근거 / 내릴 근거** 세 칸으로 나누고, **채점할 때마다 그 형식으로 쓰도록 하네스가 강제**하기를 원한다("어차피 다시 채점할 거라서 채점할 때마다 제대로 근거 분류가 되게 작성해야 함").
- **문제 2 (트리거 표).** 리포트 「다음 재채점 트리거」 표에서 ID·기업·Factor·기한·근거 열이 넓고 관찰 사실·조건 열이 좁다. 원인은 CSS 한 줄이다. `td.text{min-width:180px}`(render_html.py:139)가 일곱 열 모두에 걸려 최소 폭 합 1,260px 이 본문 폭 1,148px 을 넘고, 브라우저가 모든 열을 같은 폭으로 줄인다. `.narrow{min-width:0}`(219행)는 `td.text` 보다 구체성이 낮아 효과가 없다.
- **문제 3 (긴 페이지).** 리포트가 7개 절(517KB)이 한 페이지에 이어져 길다. 상단 탭으로 나눈다.

## 결정 사항 (2026-10-07, 사용자)

| 항목 | 결정 |
|---|---|
| 세 칸 적용 시점 | **지금 실행(`ai-scorecard-2026-10-rescore`)에 적용**하고 다시 승인한다. 이후 모든 실행은 쓰는 시점에 강제한다 |
| 애매한 문장 처리 | 아래 「분류 기준」표. 판정 칸이 결론·저울질·미확인을 받는다 |
| 트리거 표 | **열을 합쳐 두 덩어리**: 왼쪽 좁은 칸에 ID·기업·Factor·기한·근거를 세로로, 오른쪽 넓은 칸에 관찰 사실·조건·재검토 |
| 첫 탭 | **요약 카드와 순위표만**. 지도(산점도)는 요약 탭 맨 아래 |
| 역할 | 근거 확정·제안 반영·거부는 에이전트가 한다. 사람은 승인 취소와 최종 승인만 한다(2026-10-07 적용 완료) |

### 분류 기준 (guide.md 5.5 에 그대로 옮긴다)

기준은 하나다. **"이 사실 하나만 놓고 보면 점수가 오르는가, 내리는가?"** 답할 수 있으면 올릴·내릴 근거, 답할 수 없으면 판정 칸.

| 유형 | 예 | 처리 |
|---|---|---|
| 판정 재료 문장(기준 통과·실패, 관문 결과, 점수 문장) | "③ 모방 불가능성은 실패다", "⑨ 는 0 에서 끝난다" | 판정 칸 |
| 한 사실이 양쪽으로 읽힘 | Microsoft ⑤: 경쟁 제품 출시 + 같은 주 협력 지속 | 사실 둘로 쪼개 각 칸으로. 저울질 결론은 판정 칸 |
| 지표끼리 결론이 갈림 | NVIDIA ③: 전년 대비 가속, 직전 분기 대비 감속 | 각 칸으로. 판정 칸에 "규칙이 직전 분기 대비를 먼저 쓰므로 감속" |
| 사실은 있는데 품질이 약함 | Tesla ④: 13.7GWh(보도 제목 값, 예상 미달) | 방향(올림) 칸에 두고 약점을 같은 줄 단서로 |
| 계획·발표(규칙상 점수 미반영) | OpenAI 칩 2027년 1.3GW 계획 | 방향 칸에 두고 "계획이라 점수에 넣지 않는다"를 같은 줄에 |
| 아직 판정 못 한 것 | Oracle ⑨ FCF 추세 '모름' | 판정 칸에 "미확인"과 이유. 어느 방향 칸에도 넣지 않는다(모름 ≠ 0) |

점수 방향은 숫자 기준이다. 함정 항목(⑥~⑨, 음수)에서 "올릴 근거"는 함정이 얕다는 사실, "내릴 근거"는 함정이 깊다는 사실이다. 한 칸이 비면 빈 목록으로 두고 화면에는 "없음"으로 나온다. 두 방향 칸이 모두 비면 안 된다.

## 0단계 — 구현 세션 준비 (코드 전 10분)

1. `git log --oneline -3` 로 마지막 커밋이 `docs(plans): 10월 재채점 승인·빌드 완료…` 인지 확인한다. 작업 트리의 `validation/**/_raw` 변경은 건드리지 않는다(원래 있던 것).
2. `.agents/plans/evidence-3way-2026-10/` 에 `plan.md`(이 파일 내용), `checklist.md`(아래 단계를 체크박스로), `context-notes.md`(결정 사항 + 조사에서 확인한 제약)를 만들고 커밋한다. 이후 결정은 context-notes.md 에 계속 덧붙인다.
3. **사용자에게 승인 취소를 요청한다.** `protect_approved_run`(scripts/scorecard/stages.py:810-836)이 승인이 유효한 실행에서 에이전트 세션의 판단 수정·research·calculate·draft 를 거부한다. 사용자가 `node server.js --approvals` → `http://127.0.0.1:3000/approve/ai-scorecard-2026-10-rescore` 에서 승인 취소(6자리 코드)를 한다. 새 slug 로 `init --from-run` 하지 않는 이유: `scorecard/history.csv` 에 10월 실행이 둘이 된다. 코드 작업(1~5단계)은 승인 취소 전에도 할 수 있으니 기다리지 않는다.

## 1단계 — 자료 구조·검증·CLI·승인 페이지 (한 커밋 + node 한 커밋)

### 자료 모양
- `evidence: list[str]` 는 그대로 두고 **판정 칸**으로 쓴다(114개 중 100개가 이미 첫 줄이 판정 문장). 새 선택 키 `evidence_up: list[str]`, `evidence_down: list[str]` 를 더한다. 옛 실행(v1.5~v1.8)은 두 키가 없고 그대로 읽힌다.
- `counter_evidence` 는 v1.9 이상에서 비어 있어야 한다(내릴 근거로 대체). 지금 실행에 내용이 있는 3건(`tsmc.F5.strict54`, `anthropic.F5.impl48`, `openai.F5.impl48`)은 옛 감사 문면이라 6단계 재분류 때 비운다.
- 바꾸지 않는 것: `JUDGMENT_REVISION_FIELDS`(7키), `PROPOSAL_SNAPSHOT_KEYS`(4키), judgments 파일 바이트 해시 방식. 10-test 4건·rescore 114건의 옛 `revision_history` 와 proposals 147건 스냅숏이 그 모양이라 **정확히 그 키를 요구하는 검사는 "필수 7키(4키) + 선택 up/down"으로 완화**한다.

### `scripts/scorecard/schema.py`
- `JUDGMENT_DIRECTION_FIELDS = ("evidence_up", "evidence_down")` 추가.
- `validate_judgments`(1119-1199): 항목 optional 에 두 키 추가. 있으면 `list[str]`, 각 원소는 공백 아닌 문자열(빈 목록 허용).
- `_validate_revision_history`(1083-1094): `previous` 는 7키 필수 + `evidence_up`·`evidence_down` 선택.
- `validate_proposals`(1413-1463): `evidence_up_after`·`evidence_down_after` 선택(null 또는 `list[str]`, 빈 목록 허용 = 그 칸을 비움). `before`·`applied.after` 는 4키 필수 + 두 키 선택.
- `superseded` 안의 `evidence` 는 손대지 않는다.

### `scripts/scorecard/stages.py`
- `_judgment_snapshot`(1187): 항목에 up/down 이 있으면 스냅숏에도 넣는다.
- `_check_judgment_changes`(1087): `set(changes) ⊆ {"evidence","evidence_up","evidence_down"}` 이면 `"evidence_only"`. up/down 은 공백 아닌 문자열 목록(빈 목록 허용).
- `revise_judgment`(1118): `previous` 에 up/down 이 항목에 있으면 함께 보존. 세 칸 각각 교체. 바뀐 값 없음 비교에 두 키 포함. **v1.9 이상 실행이면 쓰기 전에 `three_way_item_violations(new)`(아래 validate.py)를 돌려 위반이면 `SchemaError`** — 쓰는 시점에 강제한다. 규칙 버전은 `load_json_strict(run_paths(slug).run)["rule_version"]` 로 읽는다.
- `undo_proposal`(1389-1390): 7키는 지금처럼, up/down 은 `prev` 에 있으면 복원, 없으면 `new.pop(k, None)`.
- `add_proposal`·`decide_proposal`: `evidence_up_after`·`evidence_down_after` 를 받아 `changes` 로 넘긴다. `_summary_proposals`·`_summary_judgments` 가 두 키를 내보낸다.
- `baseline_judgments`(baseline_import.py) 는 손대지 않는다. v1.9 이상 실행을 기준선에서 새로 만들면 검증기가 세 칸 없음을 잡아 research 가 막히고, 에이전트가 제안으로 채운다(의도된 동작, guide 에 적는다).

### `scripts/scorecard/validate.py`
- `THREE_WAY_MIN_RULE = (1, 9)`. `three_way_item_violations(item) -> list[str]`: `evidence_up`·`evidence_down` 키가 둘 다 있어야 하고, 합이 1개 이상, `counter_evidence` 는 비어 있어야 한다. `three_way_violations(ctx)` 가 전 판단에 돌린다.
- `self_contained_violations`(120-147): up/down 줄도 검사한다(위치 표기 `"{jid} 올릴 근거[{i}]"`, `"{jid} 내릴 근거[{i}]"`).
- `validate_scorecard`: self_contained 와 같은 자리(187-194)에 `_rule_at_least(ctx.rules.version, THREE_WAY_MIN_RULE)` 이면 `three_way_violations` 를 오류로, 통과하면 `result.check("judgment evidence is three-way")`.

### `scripts/scorecard_cli.py`
- `propose`(676-687, 326-350)·`judge`(701-711, 290-323): `--up`·`--down`(repeatable) 추가. `--evidence` 는 판정 칸(도움말에 "판정 칸" 명시). `--json`: propose 는 `evidence_up_after`/`evidence_down_after`, judge 는 `evidence_up`/`evidence_down`. judge 출력 "N문장 → M문장"에 세 칸 수를 적는다.

### `server/approvals.js` + node 테스트
- 판단 수정 폼(350-361): textarea 세 개(판정 / 올릴 근거 / 내릴 근거) + hidden 원본 세 개. `buildJudgeArgs`(564-567): 바뀐 칸만 `--evidence=`/`--up=`/`--down=` 줄 단위.
- `proposalEvidenceDiffHtml`(409-420): 칸별 −/+ 비교. 판단 카드(511-524): 세 묶음으로 표시. up/down 이 없는 옛 실행은 지금 모양.
- `tests/node/fixtures/summary.sample.json`: judgments 에 `evidence_up`·`evidence_down`, proposals 에 `evidence_up_after`·`evidence_down_after`·`before.evidence_up/down` 추가(`tests/test_approval_commands.py:113-120` 의 `key_paths` 비교가 fixture 를 상한으로 쓴다. 옛 실행 요약은 부분집합이라 통과). `tests/node/approvals.test.js` 480-481·592-612 를 세 칸으로.

### 테스트 (`tests/test_evidence_three_way.py` 신규)
- `tests/test_collect_stage.py` 47-75 `Sandbox` 의 `init_run` 에 `rule_version` 인자를 더해(기본 v1.8 유지) v1.9 박스를 만든다.
- 케이스: propose/judge 에 up/down → 반영 후 항목·`previous`(9키)·snapshot 확인 / evidence_only 라 `status: carried` 유지 / undo 가 up/down 복원·제거 / 옛 7키 `previous` 와 4키 스냅숏이 그대로 통과 / v1.8 박스는 up/down 없어도 통과, v1.9 박스는 없으면 오류·둘 다 빈 목록이면 오류·`counter_evidence` 비어 있지 않으면 오류·up 줄에 금지 표기(`기준선`)면 오류 / `revise_judgment` 가 v1.9 에서 세 칸 위반을 쓰기 전에 거부 / CLI `--up`·`--down`·`--json`.

## 2단계 — 렌더러: 카드와 초안의 세 칸 (한 커밋)

- `scripts/scorecard/render_common.py` `evidence_block`(819-841): 반환에 `verdict`(= 지금 `lines`), `up`, `down` 목록을 더한다. `lines` 는 호환으로 판정 줄을 그대로 둔다(`tests/test_scorecard_fix54_render.py:72-97` 이 `lines[-1][1]` 로 초안·HTML 일치를 본다). `_split_block` 의 작업 메모 분리를 세 목록 모두에 적용.
- `scripts/scorecard/render_html.py` `render_cards`(694-699): up/down 이 있으면 `<ul class="fpts">`(판정) 아래 `<div class="fdir"><div class="fup"><b class="wk">올릴 근거</b><ul>…</ul></div><div class="fdown"><b class="wk">내릴 근거</b><ul>…</ul></div></div>`. 빈 칸은 `<p class="sub">없음</p>`. CSS: 860px 이상 두 열, 아래는 세로. 없으면 지금 마크업 그대로(옛 실행 재빌드 보호, `tests/test_hash_binding.py:130-142`).
- `scripts/scorecard/render_md.py` 383-411: `- **F1** {header}:` 아래 `  - 판정` / `  - 올릴 근거` / `  - 내릴 근거` 소제목 뒤에 깊이 2 로 줄을 찍는다(깊이 들여쓰기는 이미 지원). 옛 모양은 그대로(`tests/test_trigger_render.py:91-100` obsreg 초안 바이트 일치).
- `scripts/scorecard/render_html.py` 색인 `BASIS_DOC`·`render_code_index` 에 "근거 세 칸" 설명 한 줄(판정·올릴·내릴의 뜻).
- 테스트: `test_evidence_three_way.py` 에 v1.9 박스 판단으로 `render_draft`·`render_document` 를 렌더해 세 라벨과 "없음", 옛 박스(v1.8)는 라벨이 없음을 확인.

## 3단계 — 트리거 표 두 덩어리 (한 커밋)

- `scripts/scorecard/render_html.py` `_render_active_triggers`(1573-1583): 머리 `<th>트리거</th><th class="text">관찰 사실 · 조건 · 재검토</th>`. 행마다 `<td class="tmeta"><div class="mono">TRG-001</div><div>Alphabet / Google</div><div>② 게임체인저</div><div>기한 2026-11-15</div><div>EV-alphabet-007</div></td><td class="text"><p><b class="wk">관찰 사실</b> …</p><p><b class="wk">조건</b> …</p><p><b class="wk">재검토</b> …</p></td>`. 근거 없음은 "—". `link_cited_evidence`(1650)가 EV 를 링크로 바꾸는 것은 그대로. 표에 `class="trig"` 를 준다.
- `TRIGGER_COLUMNS`·초안·research 의 마크다운 표는 바꾸지 않는다(`tests/test_trigger_render.py:44,55` 고정).
- CSS(`css()` 79-368): `.trig td.tmeta{width:200px;min-width:0;white-space:normal;text-align:left;vertical-align:top;line-height:1.6}`; `.trig td.text p{margin:0 0 8px}`; `@media(max-width:640px){.trig td.tmeta,.trig td.text{display:block;width:auto} .trig td.tmeta{border-bottom:0;padding-bottom:0}}`. `.narrow{min-width:0}`(219)를 `td.text.narrow,th.text.narrow{min-width:0}` 로 고쳐 실제로 듣게 한다 — 원자료 표·자료 확보 표에도 적용되니 빌드 뒤 화면으로 확인한다.
- 테스트: `tests/test_trigger_render.py:58-66` 유지(라벨 "관찰 사실" 남음) + `class="tmeta"` 있음, `<th class="text">기한</th>` 없음 추가.

## 4단계 — 탭 (한 커밋)

- `render_document`(render_html.py:1667-1761) 절을 `<section class="tabpanel" id="tab-…" role="tabpanel">` 로 묶는다. 머리(`<header>` 배지·h1·리드·고지)는 탭 위에 항상 보이고, `<footer id="disclaimer">` 는 탭 아래 항상 보인다. 절 번호는 새 순서로 카운터로 매긴다.

| 탭 id | 라벨 | 들어가는 것 |
|---|---|---|
| `tab-summary` | 요약 | 요약 카드 `#kpis` → 종합 순위표 `#mainTable`(+미완료) → 과점×함정 지도(맨 아래) |
| `tab-companies` | 기업 상세 | `div.cards#cards` |
| `tab-raw` | 원자료 | 지표 원자료 (+ 자료 확보 현황 `#availability` 가 있을 때) |
| `tab-triggers` | 트리거 | 다음 재채점 트리거 |
| `tab-method` | 방법·규칙 | 채점 방법과 규칙, 9가지 factor 뜯어보기, 알려진 한계, 용어 색인 `#code-index`, 감사 기록 링크 |
| `tab-sources` | 출처 | 인용 근거 `#cited-evidence`, References, 리뷰 줄 |

- 탭 바: `<nav class="tabs" role="tablist" aria-label="리포트 구역">` 안에 `<button type="button" role="tab" data-tab="tab-…" aria-controls="…" aria-selected>` 6개. 머리 아래 sticky, 좁은 화면에서 가로 스크롤.
- JS(`js()` 373-408): `document.documentElement.classList.add('js')` 를 맨 앞에 두고 CSS 는 `.js .tabpanel[hidden]{display:none}` 로만 숨긴다(JS 없으면 전부 보임). `activate(id)`: 패널 `hidden` 토글, `aria-selected`, `history.replaceState` 로 `#tab-id`. 초기 탭: 해시가 `#tab-…` 이면 그것, 해시가 요소를 가리키면 `el.closest('.tabpanel')`, 아니면 요약. **절 사이 앵커 세 갈래**를 모두 처리한다 — (1) `document.addEventListener('click', …, true)` 캡처 단계에서 `a[href^="#"]` 의 대상 요소가 속한 패널을 먼저 `activate` 한 뒤 기본 이동을 둔다(트리거 → 인용 근거 59건, 원자료 → 색인 2건, 머리말 → `#availability`); (2) `hashchange` 의 `openHash`(393-407)도 스크롤 전에 패널 활성화; (3) 순위표 행 클릭(390)은 `activate('tab-companies')` 뒤 카드 열기. `:target` 강조는 기본 이동이 남아 있어 그대로 된다.
- 인쇄: `@media print{.tabpanel[hidden]{display:block!important}.tabs{display:none}}`.
- `_validate_html`(validate.py:353-376)은 구조를 보지 않아 그대로다. `data-company` 행은 요약 탭 안에 그대로 있다.
- 테스트(`tests/test_report_tabs.py` 신규, obsreg 를 메모리 렌더): 탭 버튼 6개와 `aria-controls` 대상 id 존재, 문서 안 모든 `href="#…"` 의 대상 id 존재(앵커 무결성), 각 패널에 표지(`id="mainTable"`, `class="cards"`, `class="trig"`, `id="code-index"`, `id="cited-evidence"`), 패널 밖에 `<h2>` 없음. 기존 메모리 렌더 테스트(`fix54_render`, `fix66` mem_html, `add04a`, `hash_binding`)는 통과해야 한다. 빌드된 obsreg 파일을 읽는 테스트는 영향 없다.

## 5단계 — 문서·스킬 (한 커밋)

- `docs/scorecard/guide.md` 5.5: 「근거 세 칸」 절 — 정의, 위 분류 기준 표, 빈 칸 규칙, `--evidence/--up/--down` 예, v1.9 이상에서 judge·propose·검증기가 막는다는 것, 기준선에서 새로 만든 v1.9 실행은 제안으로 채운다는 것.
- `docs/scorecard/structure.md` 63행(judgments 필드)·162행(수정 경로)에 두 키와 proposal 키.
- `AGENTS.md` 「금지·주의」 완결된 문장 항목 바로 뒤에 한 줄: "판단 근거는 판정·올릴 근거·내릴 근거 세 칸으로 쓴다(2026-10-07 사용자 지시, 기준은 guide.md 5.5). 규칙 v1.9 이상 실행은 쓰는 시점(judge·propose)과 검증기가 막는다."
- 스킬 `score-research`(3번)·`score-review`·`score-approve`(판단 표 설명)에 한 줄씩, `.agents/skills` 사본 동기화(`diff -rq .agents/skills .claude/skills` 빈 출력).
- `rules.md` 는 바꾸지 않는다(채점 규칙이 아니라 기록 형식).

## 6단계 — 지금 실행의 판단 114개 재분류 → 리뷰 → 승인 대기

전제: 0단계 3 의 승인 취소가 끝나야 반영·research 가 된다(`protect_approved_run`).

1. 지시서 `.agents/plans/evidence-3way-2026-10/SPLIT-INSTRUCTIONS.md`: 분류 기준 표, 금지(사실·숫자 추가·삭제 금지, 문장 쪼개기만 허용, 완결된 문장·금지 표기·다른 트리거 참조 금지, 추론은 "(추론)" 유지), 판정 칸 첫 줄은 점수·판정 문장, 출력은 판단마다 `{"company","factor","evidence_after","evidence_up_after","evidence_down_after"}` JSON 한 파일(기업 묶음별). `counter_evidence` 가 있던 3건은 그 내용을 버리거나 내릴 근거로 현재 문장으로 다시 쓴다.
2. 서브에이전트 5개(기업 2~3개씩, 2026-10-06 재작성과 같은 묶음)가 JSON 을 낸다.
3. 조율자 기계 검사 스크립트(스크래치, 변조 사본으로 걸리는지 확인): 세 칸 합집합의 숫자·영문 고유명사 토큰 집합 == 원문 집합(사실 보존), 금지 표기 0, up+down ≥ 1, `SCORE_TEXT_RE` 류 점수 표기는 판정 칸에만 허용, 세 칸 사이 중복 문장 0.
4. `propose --json` 으로 114건 올리고 `proposal --all-pending --accept`(에이전트). 반영 뒤 `three_way_violations` 0 확인.
5. `research → calculate → draft`. **점수·순위 14개사 불변** 확인(바뀌면 중단하고 원인 보고). `review-template --force`.
6. 4영역 리뷰(별도 세션 4개, 모델은 구현 세션과 같은 계열): 사실·출처는 판단 114개 전수로 "세 칸 합 = 이전 문장 사실, 새 사실 0", 규칙은 분류가 판정 재료와 맞는지와 방향 오류(올릴·내릴 뒤바뀜), 재무는 숫자 전수, 출력은 카드 세 칸·탭·트리거 표·Playwright(320·768·1280 넘침 0, 탭 전환, 트리거 EV 링크 → 출처 탭 이동, 순위표 행 → 기업 탭 카드 열림). 1차 → 수정 한 묶음 → 확인 1회. `review.md` pass → `validate_report_contract.py` → **"승인 대기" 보고**.
7. 사람 승인 뒤 `scripts/build_report.py` → `validate_report_contract.py --require-html` → Playwright 재확인 → 커밋. push 는 사용자 지시 때만.

## 범위 밖 (보고만)

- `TERM_RE`(render_html.py:1511) lookbehind 가 `-` 를 안 막아 `SRC-SEC-FACTS-F6` 의 `F6` 이 링크되는 버그, Pretendard CDN 의존, 방법 절 ⑨ "조달 여력은 신용등급으로"(사용자 원본 문장), 리뷰 영역 파일의 「다음 실행 과제」 — 이번에 고치지 않는다.
- `protect_approved_run` 의 에이전트 거부를 푸는 것 — 사용자 결정 없이 바꾸지 않는다(승인 취소는 사람 행위).

## 검증 (각 단계 끝과 마지막)

- `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 전부 통과(지금 1280 + 신규, node 21 + 신규).
- 승인된 옛 실행 재현: `uv run --frozen python -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-10-test` 와 `ai-scorecard-2026-09-obsreg` 가 "results deterministic recompute" 통과. `tests/test_hash_binding.py` 가 obsreg 임시 사본 빌드를 통과(옛 모양 렌더 보호).
- 6단계 5 에서 14개사 total·rank 가 재분류 전과 같다.
- 빌드 뒤 Playwright: 320·768·1280px 가로 넘침 0, 탭 6개 전환, 트리거 표 오른쪽 칸이 1280px 에서 본문 폭의 60% 이상, 절 사이 앵커 세 갈래 동작, 리포트 본문에 `원검토|이전 실행에서|다시 매김|앞서 매긴` 0건.
- `diff -rq .agents/skills .claude/skills` 빈 출력. `rg "evidence_after" docs/ .claude/skills` 로 문서의 CLI 예가 새 인자를 포함.
