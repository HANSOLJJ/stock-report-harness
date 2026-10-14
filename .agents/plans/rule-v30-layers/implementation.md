# 규칙 v3.0 구현 계획

## Context

- **왜**: v2.x 채점은 회사를 한 덩어리로 봐서 여러 층에 걸친 회사를 제대로 재지 못했고, 점수 칸이 거칠어 14곳이 몇 개 값에 몰렸다. 2026-10-14 사용자 결정으로 층 정의부터 점수까지 다시 짠 규칙 v3.0 을 만든다.
- **지금까지 한 것**: rules.md 를 v3.0 초안으로 고쳐 `draft/rules-v3.0` 에 커밋했다(1014e74). 설계 사본·체크리스트·결정 기록은 `.agents/plans/rule-v30-layers/` 에 있다(9f598a1). `draft/rules-v2.2` 에 v2.2 초안의 남은 수정을 기록용으로 커밋했다. 푸시하지 않았다.
- **이 계획의 목표**: 기계용 규칙 `scorecard/rules/v3.0.json` 과 계산 코드를 만들어, 5개사 시범 실행이 `init → research → calculate → draft` 까지 가게 한다. build·승인은 HTML 렌더가 끝난 뒤의 일이다.
- **원본**: 규칙 문언은 `docs/scorecard/rules.md`(v3.0 초안)가 원본이다. 이 계획은 구현 순서와 검증만 담는다. 단계 구성은 2026-10-14 Plan 에이전트 보고를 바탕으로 했고, 아래 「검토에서 더한 것」을 보탰다.

## 지금 상태

- 파이썬 테스트 1,617개 가운데 1개 실패: `test_scorecard_fix52_docs` 가 rules.md 머리말의 v3.0 으로 `v3.0.json` 을 찾는데 아직 없다. S2 에서 풀린다. Node 테스트 24개 통과.
- 승인된 10월 실행 둘(`ai-scorecard-2026-10-rejudge` v2.0, `ai-scorecard-2026-10-v21` v2.1)은 지금 재계산하면 저장값과 같지만, 재계산 테스트(`tests/test_rules_v20.py` `RecomputeTest`)에는 빠져 있다.
- `validate_rules`(scripts/scorecard/schema.py 446\~452줄)는 최상위 키를 정해진 목록과 선택 목록(note, sources, open_tensions, source_text_corrections)으로만 받는다.
- 판단을 새로 만드는 길이 없다. `revise_judgment`·`add_proposal`·`_find_judgment`(stages.py 1374·1570·1515줄)는 기존 (회사, 항목) 판단만 다룬다.
- 시장 정의표(`scorecard/markets/`)와 `calc_market.py` 는 구현되지 않았다.

## 검토에서 더한 것 (이전 계획과의 차이)

1. **정기 실행 재판단 검사를 층·사업 키로 넓힌다.** `validate.rejudge_findings`(validate.py 280줄)는 (회사, 항목) 단위로 "다시 매겼나"를 본다. 층·사업 판단도 같은 검사를 받아야 시범 실행의 research 가 통과한다(S4·S5).
2. **트리거 이월.** init 이 v21 의 회사 단위 ①②③ 판단을 옮기지 않으면, 그 판단을 가리키는 트리거·근거의 교차 참조가 끊길 수 있다. `trigger_carry_gaps`(stages.py 848줄)와 교차 참조 검증이 빠진 판단을 어떻게 다룰지 S5 에서 정한다(제안: 트리거는 회사·항목으로 이어 붙이고, 층 판단이 생기면 그 판단을 다시 가리키게 한다).
3. **체크리스트 Q24·Q25.** rules.md 7절에 더한 두 문항을 v3.0.json `checklist` 에 넣고, review-template·`validate_report_contract` 가 25개를 받는지 확인한다(S2).
4. **`diff` 명령.** 기업 추가 실행의 입력 가법성·점수 투영 검사(`scorecard_cli.py diff`)는 (회사, 항목) 단위다. 시범 실행은 정기 실행이라 쓰지 않으므로 뒤로 미루되, v3.0 실행에서 부르면 명확히 거부하게 한다(S5).
5. **main 반영 순서.** S0·S0b 는 v3.0 과 무관해 main 에서 커밋하고, 곧바로 `draft/rules-v3.0` 에 `git merge main` 으로 가져온다.
6. **이정표마다 보고한다.** 단계가 열둘이라, 아래 세 이정표가 끝날 때마다 테스트 결과와 함께 사용자에게 보고하고 다음으로 간다.
7. **탁상 어림 숫자 정정.** 설계 사본의 OpenAI 가속도 0.8 은 산식(3.1 ÷ 3.3 = 0.939 → 1.18)과 어긋난다. 테스트 기대값은 산식으로 잡는다.

## 구현 전에 정할 것

**사용자가 정할 규칙 값 (rules.md 8절).** S2 의 v3.0.json 에는 rules.md 의 "초안의 처리"를 그대로 넣고, 시범 실행 init 전에 사용자와 확정한다. init 뒤에 바꾸면 `init --force` 로 실행을 다시 만들어야 한다(승인 전이라 가능).

| 언제까지 | 항목 |
|---|---|
| S6 전 | ④ AI 무관 부문 이익 미공시 처리, ④ 기업용 소프트웨어 매출 분류 |
| S7 전 | ③ "상대"의 범위, ③ 층 안을 사업으로 나눌지, ② 층 밖 사업의 AI 관련성 |
| S8 전 | ① B·C 미확인 값, ① 지속성 할인 |
| 시범 init 전 | ④ 만점 문턱(수직 7, 다각화 50%, 힘 20%), ⑥ P2 20\~40배·5% 절벽·신규 상장 P4·비상장 범위 끝, 기준선 80·56, 반올림 |
| 뒤로 미뤄도 됨 | 의미 없는 차이 폭, 표준 2년 절벽, 클라우드·데이터 플랫폼 측정 확정, ③ 기기 층 지표, 지연 조항 |

**내가 정하는 기술 선택 (Plan 에이전트 제안을 기본값으로 쓴다).**
- 매출 줄 금액은 ④ 판단 안에 근거 ID 와 함께 둔다. 층 무게의 원천은 ④ 판단이고 ①②③ 이 그것을 읽는다.
- 2년 창의 기준일은 실행의 `as_of`, 날짜는 일 단위.
- ⑤ "한 관계는 한 부분에서만" 배정은 프로그램이 점수가 최대가 되게 정한다(동점은 상대 이름순).
- 무게 0 판매 층의 판단 누락은 계산은 막지 않고 계약 검증에서 막는다.
- 반올림은 항목 점수를 Decimal 로 소수 둘째 자리에서 한 번만 하고, 총점은 반올림한 값의 합.

## 단계 (단계 하나 = 커밋 하나)

모든 단계에서 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 를 돌린다. 커밋은 `git add <경로>` 로 파일을 지정한다(`validation/`·회사 이름 폴더·`docs/ai_7.md`·PDF 제외). Co-Authored-By 줄을 넣지 않는다. 새 동작은 모두 v3.0 규칙의 새 키(mode·unit·curve·score_multiplier·layers)가 있을 때만 탄다. `factor_result` 최상위 키와 `SCHEMA_VERSION` 은 바꾸지 않는다.

### 이정표 1: 기반 (S0\~S5)

| # | 브랜치 | 할 일 | 고칠 곳 | 재사용 | 검증 |
|---|---|---|---|---|---|
| S0 | main | 승인된 rejudge·v21 실행을 재계산 테스트에 넣는다 | `tests/test_rules_v20.py` `RecomputeTest` 목록 | `engine.recompute_matches` | 둘 다 일치. 메모리에서 판단 하나를 바꾸면 불일치로 잡힌다 |
| S0b | main (선택) | 승인 페이지가 중첩 판정 재료를 `[object Object]` 로 보이는 기존 버그 | `server/approvals.js` `valueText`·`judgmentValueHtml` | — | ④ 보유표·⑧ 축에서 `[object Object]` 가 안 나옴, 스칼라 표시는 그대로 |
| — | draft | `git merge main` | — | — | 충돌 없음, 테스트 그대로 |
| S2 | draft | v3.0.json 과 스키마 수용 | 새 `scorecard/rules/v3.0.json`(v2.1.json 을 출발점으로 decisions·checklist·f6 트랙 복사, Q24·Q25 추가) · `schema.validate_rules` 선택 키 `layers`, factor `unit`·`curve`, `_validate_layers`·`_validate_curve` · `FACTOR_JUDGMENT_KINDS`·`JUDGMENT_KINDS`·`JUDGMENT_INPUT_CHOICES` 에 새 kind(business, layer_paths, layer_cp, holdings, alliance) · `RuleSet.layers`·`unit()` | `_expect_keys`, `_validate_f6_bands` | 새 `tests/test_rules_v30.py`: 층 id 오타·곡선 기준점 역순·기준점 점수가 범위 밖·unit=layer 인데 layers 없음은 거부, v1.5\~v2.1 로드와 v2.1 파일 해시는 그대로, 문서 대조 테스트 통과 |
| S3 | draft | 연속 구간 도우미와 ⑥·⑨ 곡선, ⑦·⑧ ×4 | `rules.piecewise`(x_transform log2 포함), `RuleSet.curve` · `calc_f6_params`(곡선일 때만 `int()` 제거, P4 −4, 비상장) · ⑨ 계산기(`_runway_step`·`_coverage_step`·G4 감점을 규칙 키로) · `compute_f8` `score_multiplier` · 반올림 도우미 | 기존 트랙·게이트 흐름 | 기준점: P1 x=1·2·4·8 → 0·−4·−8·−12, P2 8·14·20·30·40 → 0·−2·−4·−6·−8, 비상장 x=1 → −8, ⑨ 손실률 15% → −12, 런웨이 2년 → −2, 커버리지 0.5 → −2, ⑦ 큼·돌아옴 → −12, ⑧ −3 칸 → −12. 같은 입력을 v2.1 로 계산하면 옛 정수 |
| S4 | draft | 판단 키에 layer·business | `schema.validate_judgments`(유일 키 = 회사·항목·층·사업, unit 검사, 옛 규칙에선 두 키 금지) · `_validate_judgment_inputs` 새 kind · `validate_cross_refs` · `validate_proposals` · `inputs.JudgmentLookup`(`judgment_key()`·`layers()`·`units()`) · **`validate.rejudge_findings` 를 판단 키 단위로** | `_expect_keys`, `EVIDENCE_ID_RE` | 같은 (회사, F2, 층) 두 건 거부, 서로 다른 층 두 건 통과, v2.1 규칙에 layer 키 거부, 14건 중 7번째만 틀리면 그 항목을 지목, 기존 실행 일곱 개 검증 통과 |
| S5 | draft | 층·사업 판단 생성·수정 경로와 init 단위 전환 | stages `_find_judgment`·`revise_judgment`·`add_proposal`·`decide_proposal`·`undo_proposal` 에 layer·business, 없으면 생성(`before: null`) · `_inputs_from_run`: unit 이 company 가 아닌 항목의 회사 단위 판단은 옮기지 않고 assumptions 에 남김 · **트리거·근거 교차 참조 처리** · `scorecard_cli.py` judge·propose 에 `--layer`·`--business` · **`diff` 는 v3.0 실행에서 거부** · approvals.js 카드 id | `judgment_rule_conflict`, `validate.cited_ids` | 제안 반영으로 새 항목 생성, 번복하면 파일 해시 복원, v21 을 복제해 `init --rule v3.0` 하면 F1\~F3 회사 단위는 빠지고 F4·F5 는 carried, F7·F8 은 그대로 |

### 이정표 2: 계산 (S6\~S9)

| # | 할 일 | 고칠 곳 | 검증 |
|---|---|---|---|
| S6 | ④ 보유표와 층 무게 | 새 `scripts/scorecard/calc_layers.py`(`layer_weights`·`weighted`·`compute_f4_holdings`) · `engine.compute_company` 를 mode 로 분기 | 40/30/30 → 0.7/0.3, 로켓 줄은 분모 밖, 층 밖 줄은 몫과 AI 무관에 들고 수직에서 빠짐, AI 사슬 조건 미충족 칸은 수직 0 이지만 무게 유지, 칸 합 7 → 8, AI 무관 25% → 4, 이익률 10% → 2 |
| S7 | ②③ 층 계산 | `calc_layers.compute_f2_layers`·`compute_f3_layers` | 벤치마크 없는 층은 (4+3)×2 = 14, 표준 최근 신규 채택 25개월 전 → 0·23개월 → 점수, TSMC 1.409 → 1.480 → 4.51, NVIDIA 2.180 → 2.166 → 2.81, 13/9 → 6, 단계 c 최고 3, 값 없음 → 0 + 자료 없음, 가속도 2.9 → 층 최고 12, 모방 5 → 최고 15, 문 닫힘 증거 없음 → 최고 18, 진행 중 아님 → 수익모델·모방 0 |
| S8 | ① 사업 단위(시장 자료 전) | `calc_layers.compute_f1_business` | 12·16·10 예 → 층 13.71·회사 12.6, 묶음은 A\~C 공유·D·E 구성마다, AI 수익화 '예'가 아니면 사업 최고 16, D·E 자료 없음 → 0 + 정책 기본값, A 두 효과 모두 미확인 → 판정 대기, 매출 줄이 어느 사업에도 없으면 판정 대기 |
| S9 | ⑤ 동맹 세 부분·적대 띠 | `compute_f5` mode alliance | Amazon: Anthropic 편입 3 + OpenAI 지분 2, Alphabet: 편입 3·지분 0, 비용형 + 조치 + 관할 3곳 → −6, 구조형 전선 둘 → −10, 끝난 사건만 있으면 최소 |

### 이정표 3: 출력·문서·시범 실행 (S10\~S11, P)

| # | 할 일 | 고칠 곳 | 검증 |
|---|---|---|---|
| S10 | 초안·미리보기 최소 렌더 | `render_common.factor_calc_text` 새 basis, `evidence_block` 다중 판단, `render_md`(층 표, 기준선을 `rules.scoring` 에서 읽기, D·E 정책 기본값 안내), `render_preview`(척도가 다르면 × 환산 참고) | v3.0 합성 실행 초안에 층 표·80점 문구, v21 초안을 다시 그려도 승인 해시의 draft 와 같음 |
| S11 | 문서·스킬 | `structure.md`·`guide.md`, `.claude/skills/score-research`(보유표 → 층 → 사업 순서의 판단 세션 지시서), `score-review`(같은 층 경쟁사 교차표, Q24·Q25) | 문서만 |
| P0 | 규칙 값 확정 | 「구현 전에 정할 것」의 시범 init 전 항목을 사용자와 정하고 v3.0.json·rules.md 에 반영 | 테스트 통과 |
| P1 | 시범 실행 | `init ai-scorecard-2026-10-v30pilot --from-run ai-scorecard-2026-10-v21 --rule v3.0 --companies alphabet,apple,tsmc,spacex-xai,anthropic` → 보유표·층·사업 판단(Opus 판단 세션) → ⑦⑧ 재확인 → 트리거 처리 → research → calculate → draft | draft 가 나오고, 층 표·판정 대기 사유가 보임. 결과는 순위 판단에 쓰지 않는다(D·E 0) |

## 뒤로 미룸

- 시장 정의표 `scorecard/markets/` + `calc_market.py` + 규칙의 sha256 연결. 그 전까지 ① D·E 는 정책 기본값 0 이라 ① 이 낮게 나온다.
- HTML 리포트(산점도 축·80점 선·방법 카드·층별 화면). 이것이 끝나야 build·승인이 된다.
- 승인 페이지의 층별 수정 화면과 `--layer` 를 넘기는 judge POST.
- 기업 추가 실행용 `diff` 의 층 단위 지원.
- 전체 14개사 시험 실행, AGENTS.md 문구(main), history.csv 의 규칙 변경 기록.

## 위험

- **승인 해시.** 분기를 v3.0 키에만 묶고 S0 테스트로 v1.7\~v2.1 재계산을 지킨다.
- **(회사, 항목) 가정이 널리 퍼져 있다**(stages·렌더·validate·CLI·approvals.js). `judgment_key()` 하나로 모으고 일부 행에만 넣은 값으로 테스트한다. `JudgmentLookup._by_pair` 는 지금 중복을 조용히 덮어쓴다.
- **판단량.** 시범 5개사도 층·사업 판단이 수십 건이다. 판단 세션은 Opus(노력 high), 판단 세션 지시서(S11)가 먼저 있어야 한다.
- **연속값 부동소수.** 반올림을 한 곳으로 모은다.
- **⑧ 표시.** 판단은 칸(0\~−5)을 고르고 결과에서 ×4 한다. 리포트의 칸 표시와 점수 표시를 섞지 않는다.

## 검증 (전체)

1. 단계마다 파이썬·Node 전체 테스트. 새 테스트는 걸려야 하는 값·걸리면 안 되는 값·일부 행에만 넣은 값을 각각 넣는다.
2. S0 의 재계산 테스트가 모든 단계에서 통과(승인된 실행 불변).
3. S2 뒤 `test_scorecard_fix52_docs` 통과.
4. P1 시범 실행이 draft 까지 가고, `validate_report_contract` 는 build 전 단계 기준으로 통과.
5. 이정표마다 사용자에게 테스트 결과와 남은 결정을 보고한다.
