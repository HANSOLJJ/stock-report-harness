---
reviewer_agent: report-designer
session: rd-opus55-20261001-c
reviewed_at: 2026-10-01
---
# output-readability — 출력·가독성
검토자: Claude Opus 5.5 · report-designer 독립 세션(3차 확인, 이 실행을 만든 세션 아님) · 2026-10-01
결과: pass
요약: 1차 high 두 건(함정 최심 동점, TRG-037 의 옛 적대 등급 0)과 medium 여섯 건이 닫혔다. 2차에서 남았던 M1(HTML 근거 ID 대응)은 ab896b9 로 닫혔다. "이번 실행에서 다시 매김" 은 이번 실행에서 고친 판단 네 개(anthropic ⑤, amazon ⑤, amazon ⑨, oracle ⑨)에만 붙는다. 이 네 개는 proposals.json 의 accepted 일곱 건(PRP-001~007)과 맞는다. amazon ⑨ 는 PRP-002·004·007, oracle ⑨ 는 PRP-003·006 이다. 3차 입력 변경(PRP-006·007 숫자 반영, 출처 이해상충 보강) 뒤에도 순위표 14행, 카드 머리줄 14개, 카드 factor 126칸, 미리보기 14행이 results.json 과 모두 같고, 순위·점수는 2차와 같다. 남은 것은 low 뿐이다. report.html 은 아직 없다. HTML 시각 검증은 빌드 뒤 `uv run --frozen python -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-10-test --require-html` 와 Playwright 실측으로 미룬다.

검토 기준 파일(sha256 은 파일 바이트 기준): draft.md `30135ffb15ac1be6…`(review.md 의 draft_hash 와 같다) · preview.md `a8018c8532ec4c3f…` · research.md `f5cf23acb1e18325…` · triggers.json `84da4998e571df56…` · evidence/evidence.json `e320bcedde518f00…` · results_hash `d82fcfa1fa3148ce…`(results.json 의 내부 해시이고 파일 바이트 해시가 아니다). 렌더러 기준은 `scripts/scorecard/render_html.py` @ ab896b9 이다.

## 3차 확인(2차 pass 이후 입력 변경)

- PRP-006(oracle ⑨): draft 1048행이 `최근 1년 영업이익 $20.61B ÷ 매출 $67.36B, 마진 30.6% — 2026-05-31 관측` 이다. 이는 observations 의 verified `operating_income_ttm` 20,606M·`revenue_ttm` 67,357M(20.606/67.357 = 30.6%)과 같다. 옛 `$22.39B, 마진 33.2%` 는 취소선 "(대체됨)" 으로만 남는다.
- PRP-007(amazon ⑨): draft 182행이 `순부채 -$119.3B(2026-06-30 관측)` 이다. 이는 verified `net_cash` -119,332M 과 ⑨ 원자료 표(-$119.3B)와 같다. 옛 `-$128.7B` 는 취소선으로만 남는다.
- 바뀐 줄에 순위·최고·최저 같은 비교 문장은 없다. oracle ⑨ 의 "표 전체 최단" 은 런웨이 1.32년이 results 의 런웨이 가운데 가장 짧다는 현재 사실과 맞는다.
- 출처 이해상충: 개요의 "이해상충이 표기된 출처 69건" 이 References 에서 이해상충 문구가 붙은 줄 수(69)와 같다.
- M1 코드 확인: `render_html.link_cited_evidence` 를 읽고, 빌드하지 않고 메모리로 render_document 를 돌려 보았다(산출은 스크래치패드에만 썼다). References 아래 "인용 근거" 절에 38행이 나오고, 본문 근거 ID 링크 40개가 모두 그 행 앵커(`#ev-…`)로 이어진다. 링크가 안 걸린 근거 ID 는 0개, 중첩 `<a>` 는 0개다. 인라인 스크립트(js())는 바뀌지 않았고, SVG `<title>` 에는 근거 ID 가 없다. 제목 칸은 원문 링크를, 상태 칸은 "확정" 을 보인다. 공시 6건의 발행일 `—` 는 draft 와 같은 원인이다(L5).

## 1차 발견 재확인

| 1차 등급 | 항목 | 상태 | 확인 내용 |
| --- | --- | --- | --- |
| high | 개요 "함정 최심" 이 동점 셋 가운데 하나만 적음 | 닫힘 | draft 26행이 `-11점 — Alibaba(조정 7점) · OpenAI(조정 4점) · Oracle(조정 3점) — 공동` 이다. `render_html.render_kpis` 를 현재 results.json 으로 돌려 보니 KPI 타일에도 세 기업이 모두 나온다. |
| high | TRG-037 이 적대 등급을 "지금 0" 으로 적음(C-19) | 닫힘 | triggers.json·draft 트리거 절의 TRG-037 이 "선별 당시 0(최소)이었고, 이번 실행에서 사람이 반영한 제안 PRP-001 로 -1(비용형)이 됐다" 로 바뀌었다. 조건 칸에도 미래 점수가 없다. |
| medium | EV-anthropic-002·006 관련성이 옛 상태(4점)를 지금처럼 적음 | 닫힘 | 두 건의 `relevance`·`conditional_impact` 가 "선별 당시 … 4점이었고 … PRP-001 반영으로 적대 등급 -1(비용형), 3점이 됐다" 로 바뀌었다. 상태는 confirmed(noble, 2026-10-01)다. |
| medium | research.md Anthropic ⑤ 판단 비고가 `A +2→+1, F5 5→4` | 남음(low 로 낮춤) | research.md 565행 비고는 그대로다(judgments.json `anthropic.F5.impl48.note`). draft 와 HTML 은 판단 note 를 싣지 않으므로(render_md 244행만 사용) 독자용 산출물에는 나오지 않는다. 아래 L1 로 옮긴다. |
| medium | 이전 실행 판단에 "이번 실행에서 다시 매김" 이 붙음 | 닫힘(상태 칸 일부 남음) | 근거 머리줄의 "이번 실행에서 다시 매김" 은 155·176·400·1046행 네 곳뿐이고, 모두 이번 실행 proposals 의 accepted 판단이다. 나머지 일곱 건(TSMC ⑤, Anthropic ⑧, SpaceX ⑨, NVIDIA ⑦, Alibaba ⑨, OpenAI ⑤, Oracle ⑦)은 "이전 실행에서 매김" 이다. 다만 카드 표 상태 칸은 Anthropic ⑧(사람 판단, 2026-09-11)을 여전히 "이번 실행 산출" 로 적는다. 아래 L2 로 옮긴다. |
| medium | Amazon ⑨ 런웨이 10.6년(카드 불릿·TRG-005) | 닫힘 | 카드 불릿이 `런웨이 9.95년 — 완충 $115.7B(현금 $78.2B + 확정 미인출 여신 $37.5B)` 이고, 옛 10.6년 문장은 취소선 "(대체됨)" 으로만 남는다. TRG-005 도 9.95년이다. results `amazon.F9.calc.runway_years` 는 9.954 다. |
| medium | draft 에 EV ID → 링크 대응 없음 | 닫힘(draft·HTML) | draft 에 "## 인용 근거" 절(1262행)이 생겼다. 본문 인용 EV ID 38개와 표 38행이 빠짐없이 일치하고, 모두 제목 링크·상태(확정)가 있다. HTML 은 ab896b9 의 `link_cited_evidence` 로 같은 대응을 갖췄다(위 3차 확인). |
| medium | 미리보기 "변동 원인" 고정 문장이 틀림, 이전 실행 대비가 없음 | 닫힘 | preview 에 "이전 실행 `ai-scorecard-2026-09-obsreg` 대비" 표가 생겼다. Meta ⑥ -1→-3, Anthropic ⑤ 4→3, Oracle ⑥ -3→-2 세 건과 그 원인(관측/판단 수정)이 두 실행의 results.json 비교와 같다. 원인 문장은 "추정한 분류" 라고 밝힌다. |
| low | research.md 관련성 열 "(추론)" 접두가 겹침 | 남음 | "(추론) 추론: …" 16건 이상이 그대로다. |
| low | 카드 기준선 한 줄 요약의 비교어 | 남음 | Anthropic "과점 21점 최고점"(366행), Meta "함정 -2로 14사 중 가장 얕다"(246행), Microsoft "함정은 표에서 두 번째로 얕고" 가 그대로다. "과거 기록" 표지는 있다. |
| low | 근거 본문 속 커밋 해시·작업 기록 | 남음(HTML 확인 대상) | Anthropic ⑤ `C-13(a01f127)과 NTM(1aab1f2)` 등. HTML 본문에서 audit.md 로 빠지는지는 빌드 뒤에 확인한다. |
| low | 방법과 규칙의 빈 바깥 불릿 | 남음 | `-   - ` 형태 19줄이 그대로다. |
| low | 알려진 한계 "anthropic F2 가 5→4 가 될 수 있다" | 남음 | 1213행. 트리거가 아니라 C-14 위반은 아니다. |

## 발견 사항

- [medium → 닫힘] M1 `scripts/scorecard/render_html.py` — 2차 지적은 HTML 에 근거 ID→링크 대응이 없다는 것이었다. ab896b9 의 `link_cited_evidence` 가 본문 근거 ID 를 References 아래 "인용 근거" 행 앵커로 연결한다. 메모리 렌더 확인 결과는 위 3차 확인에 적었다. 320px 에서 이 표의 긴 제목이 `tablewrap` 안에서만 스크롤되는지는 빌드 뒤 Playwright 실측에서 본다.
- [low] L1 research.md 판단 입력 표 Anthropic ⑤ 비고(565행, judgments.json `anthropic.F5.impl48.note`) — `A +2→+1, F5 5→4` 가 같은 행의 입력 `A=1, H=-1`(→3)과 어긋난다. 1차 medium 에서 낮췄다. draft·HTML 에는 나오지 않기 때문이다. render_md 판단 입력 표가 `revision_history` 가 있으면 최신 수정 사유를 note 앞에 보이게 하거나 "(수정 전 비고)" 표지를 단다. note 자체를 고치려면 `scorecard_cli.py judge` 로 한다.
- [low] L2 draft.md 카드 표 상태 칸 — Anthropic ⑧(377행)이 `이번 실행 산출 | 사람 판단` 인데, 바로 아래 근거 머리줄(430행)은 `이전 실행에서 매김 · 작업자 · 2026-09-11` 이다. results 의 status 가 `ok`·basis `manual` 인 유일한 칸이라 STATUS_LABEL["ok"] 가 그대로 나온 것이다. 등급·조합표 산출 칸(⑤·⑦)은 이번 실행에서 프로그램이 계산했으므로 "이번 실행 산출" 이 맞다. 사람이 점수를 직접 적은 `manual` 칸만 `reviewer_label` 과 같은 실행 생성일 기준으로 "이전 실행 판단" 으로 표시한다(render_md 카드 표와 render_html 카드 표 둘 다).
- [low] L3 draft.md "기업별 상세" 머리 문단(55행) — 근거 머리줄 라벨 세 가지 가운데 "원검토"(사용자의 판단)와 "이번 실행에서 다시 매김" 만 설명하고, 새로 생긴 "이전 실행에서 매김" 은 설명하지 않는다. 어느 실행인지(`ai-scorecard-2026-09-obsreg`)도 draft 어디에도 없다. 머리 문단에 "이전 실행에서 매김 = `continued_from` 실행에서 사람이 매긴 판단, 이번에 다시 보지 않음" 한 줄을 render_md 가 넣는다.
- [low] L4 preview.md "이전 실행 대비" 표 — factor 가 바뀐 세 기업만 보인다. Microsoft 4→3위, NVIDIA·SpaceX + xAI 7→6위처럼 다른 기업이 움직여 순위만 바뀐 경우는 보이지 않는다. 표 아래에 "순위만 바뀐 기업: …" 한 줄을 render_md 가 붙인다.
- [low] L5 draft.md "인용 근거" 표 — 공시 근거 6건(EV-amazon-001·002, EV-meta-001, EV-oracle-003, EV-tesla-001·003)의 발행일이 `—` 이다. evidence.json `published_at_utc` 가 비어 있기 때문이다. 제목에는 제출일(예: `10-Q 2026-07-31`)이 있으므로 렌더러가 filing 이면 그 제출일로 칸을 채우거나, 근거 선별 단계가 `published_at_utc` 를 채운다.
- [low] L6 draft.md 지표 원자료 † 각주(1086행) — "표에서는 엔진이 실제로 고른 칸에만 † 를 붙인다" 다음에 "† 는 참고 열(NTM PER 등)에만 남는다" 가 온다. parameters 모드에서 NTM PER 은 엔진이 고르지 않는 참고 열이라 두 문장이 서로 어긋나게 읽힌다. `render_common.vendor_policy_note` 의 첫 문장을 "† 는 원천 정책 밖 값이 들어간 칸에 붙인다" 로 바꾸거나, 조건 분기 쪽 문장만 남긴다.
- [low] L7 draft.md 지표 원자료 ⑥ 표 — TTM PER 열(Alphabet 16.9)은 기준선 참고값이고, 카드의 실제 점수 입력은 PER 17.2·EV/매출 9.2x·성장 20.1% 이다. 표 아래 문장이 "참고값이고 점수는 원자료에서 다시 계산한다" 고 밝히지만, 같은 이름의 수가 두 개 보인다. ⑨ 표 Amazon 런웨이 `10.0`(9.954 를 소수 첫째 자리로 반올림)과 카드 `9.95년` 의 자릿수도 다르다. render_md·render_html 원자료 표에 엔진 입력 P1~P3 열을 더하고 런웨이 자릿수를 카드와 맞추는 것을 권한다.
- [low] 1차 low 다섯 건(관련성 "(추론)" 겹침, 기준선 요약 비교어, 본문 진행 기록, 빈 바깥 불릿, 알려진 한계의 숫자 미래 점수)은 위 표대로 남아 있다. 고칠 자리는 1차와 같다.

## 확인한 것(통과)

- 구조: draft H1 은 하나다(20행 `# v1.8 근거 계층 시험 실행`). 개요·종합 순위표·기업별 상세·지표 원자료·방법과 규칙·References 가 모두 있고, 알려진 한계·트리거·인용 근거 절도 있다.
- 숫자 일치(스크립트 전수 대조): 순위표 14행의 순위·①~⑨·과점·함정·조정총점, 카드 머리줄 14개(순위·조정·과점·함정), 카드 factor 표 126칸, preview 기준선 대비 표 14행의 "이번 조정/순위" 가 results.json 과 모두 같다. 이전 실행 대비 표 3행은 obsreg results.json 과 비교해 맞았다.
- 개요 "조정총점 1위: Alphabet / Google · Amazon / AWS (15점) — 공동", "과점 factor 최고 … (21점)" 도 results 와 같다.
- C-19: "Meta 1위", "3사 공동 1위", "Anthropic 5위" 같은 옛 순위 문장이 없다. Amazon ⑤ 근거의 "이번 실행에서 적대 등급 0 인 기업은 없다" 는 results 의 F5 H 값 14개(모두 -1 이하)와 맞다. 기준선 한 줄 요약의 비교어는 "과거 기록" 표지가 있어 위반으로 보지 않는다(low 유지).
- 트리거: 40건 모두 관찰·조건·기한·근거·재검토 열이 있다. triggers.json 키에 점수 필드가 없다. 관찰 문장에 나온 "지금 N점" 21곳을 results 와 대조했고 모두 현재 점수와 같다. 미래 점수는 없다. 절 끝에 C-14 문장이 있다.
- 근거: evidence.json 91건이 모두 `confirmed` 다. 인용 근거 표 38행이 모두 링크와 "확정" 을 보인다. Anthropic 두 건의 `relevance` 는 "사실:/추론:" 으로 사실과 추론을 나눠 적는다.
- 면책·금지 표현: draft 끝(1439행)에 면책 문구("매수·매도를 권유하지 않으며 투자 자문이 아닙니다")가 있다. 개요에 이해상충 고지가 있다. 매수·매도 권유나 목표가 문구는 없다. 970행 "목표가" 는 "손익분기 목표가 2030년으로 후퇴" 라는 사업 서술이다.
- 렌더러 변경(8191b5d): `render_html.render_kpis` 의 함정 최심 동점 처리와 `render_cards` → `evidence_block(run_created=…)` 전달을 읽었다. `tests.test_render_review_fixes` 6건이 통과한다.

## 수행하지 않은 확인

- report.html 이 없어 6절 대시보드 검사를 하지 않았다. 대상은 generator 메타(`scorecard-builder`), `results-hash` 메타, viewport, 면책 footer, 순위표 `data-company` 행, source marker 없음, 320/768/1280px 넘침, 24px 탭 대상, 모바일 합계 열·첫 두 열 sticky·행 탭 카드, 차트·산점도 aria-label, 다크 모드·대비, 본문에 해시·결정 번호·리뷰 기록이 없고 audit.md 링크가 동작하는지다. 빌드 뒤 `validate_report_contract.py ai-scorecard-2026-10-test --require-html` 와 Playwright 실측으로 확인한다. 그때 "인용 근거" 표의 320px 표시와 1차 low(본문 진행 기록이 audit.md 로 빠지는지)도 함께 본다.
- 근거·출처 링크가 실제로 열리는지는 사실·출처 영역 몫이라 보지 않았다.

## 체크리스트 기여

- Q05 이해당사자 출처: pass(출력 표기 측면만). 개요에 이해상충 고지가 있고, References 출처 줄과 Anthropic 근거 관련성 칸에 이해상충 문구가 있다. 출처 판정 자체는 사실·출처 영역이 본다.
- Q09 미래 계획을 현재 점수에 넣었나: 이 영역에서 판정하지 않음. 출력 측면에서는 트리거가 미래 점수를 저장하지 않는다는 것만 확인했다. 점수 반영 여부는 규칙 일관성 영역이 본다.
- 그 밖의 Q01~Q04, Q06~Q08, Q10~Q23 은 not_applicable 이다. 판단·규칙 영역 소관이라 출력·가독성 영역에서 판정하지 않았다.
