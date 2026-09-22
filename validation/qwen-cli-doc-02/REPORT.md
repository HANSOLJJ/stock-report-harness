# QWEN-CLI-DOC-02 — scorecard 문서와 실제 CLI 정합성 독립 검증

- 검증일: 2026-09-08
- 검증자: scarpper worktree 의 Qwen (독립 세션)
- 대상 worktree: `C:\Users\noble\orca\workspaces\stock-report-harness\worker` (**읽기 전용**)
- 시작 HEAD: `ea1ecf095c66cb92a563c4ee785a2f5ae0e67143` (`ea1ecf0 docs: /score-* 명령·스킬 추가와 README·AGENTS scorecard 계약, memory daily 기록`), 브랜치 `HANSOLJJ/worker`
- 작업트리: 깨끗함. untracked 3건(`package-lock.json`, `research/ai-scorecard-2026-09-baseline.md`, `reviews/ai-scorecard-2026-09-baseline.md`)은 검증 이전부터 존재.
- 이 검증은 **문서·CLI 정합성**만 다룬다. QWEN-BASELINE-01 의 기준선 데이터 재검증과 Claude 의 4-way 리뷰를 대신하지 않으며, `설계진행/validation/qwen-recheck.md` 에서 기각·부분채택으로 판정된 항목(P4 경계 저장, P5 incompatible_basis 값 보유, P9 이름·배열 순서, P10 parse_failed)은 재논쟁하지 않는다.
- 최신 worker 기준 관측 **227건**을 전제했다(실측 `scorecard/baseline/v1.5/observations.json` = 93,381 bytes / 3,259 줄, `f22e9415e1dbe056…`). 예전 241건을 가정하지 않았다.

## 0. 결론 요약

| 구분 | 결과 |
|---|---|
| 검토 파일 | 24종 (문서 8 · 명령 8 · 스킬 8 · CLI/코드 9 · package.json · 훅 2) |
| 문서↔CLI 일치 확인 | **24개 항목 통과** (§2) |
| 문제 | **13건** — high 2 · medium 4 · low 7 |
| 미확인 | 8건 (§6) |

핵심 2건은 둘 다 **사용자에게 보이는 문장/산출물이 실제 동작과 다른** 경우다.

- **D-01** 생성되는 `plan/<slug>.md` 의 "차단 조건"이 `awaiting_user` 를 자료 부족·규칙 미결의 결과로 서술하나, 실제 `awaiting_user` 는 승인 게이트에서만 발생한다. 커밋된 실물 plan 112행에서 확인.
- **D-02** `approve --by` 값이 어디에서도 검증되지 않아 빈 문자열·공백·`None`·숫자까지 승인이 성립하고, 그 값이 최종 HTML footer 에 박힌다. 격리 실행으로 확인.

나머지는 문서가 CLI 옵션을 빠뜨리거나(D-03), 테스트 커버리지를 과장하거나(D-04), 검증기가 실패한 검사에 `ok -` 줄을 붙이거나(D-05), Windows 인터프리터 이름이 문서와 npm 스크립트에서 모순되는(D-06) 류다.

## 1. 검사 범위와 방법

### 1.1 실제로 실행한 것 (전부 읽기 전용)

| # | 명령 | 목적 |
|---|---|---|
| E1 | `git rev-parse HEAD` / `git status --porcelain` / `git log --oneline -6` / `git branch --show-current` | 시작·종료 상태 고정 |
| E2 | `python -B -X utf8 scripts/scorecard_cli.py --help` | 서브커맨드 집합·usage 본문 확인 |
| E3 | `python -B -X utf8 scripts/scorecard_cli.py <stage> --help` × 8 (init·approve·review-template·import-baseline·research·calculate·draft·status) | argparse 필수/선택·기본값 확정 |
| E4 | `python -B -X utf8 scripts/scorecard_cli.py status ai-scorecard-2026-09-baseline` | 선행 산출물·review 상태·미결 결정·미완료 기업 실측 |
| E5 | `python -B -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-09-typo` | plan 부재 시 `report_type` 폴백 진단 확인 |
| E6 | `python -B -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-09-baseline` | scorecard 분기·차단 조건 실측 |
| E7 | `python -B -X utf8 scarpper/validation/qwen-cli-doc-02/isolated_approve_test.py` | `--by ""` argparse 통과 + `schema.validate_approval` 의 빈 승인자 허용 여부를 **worker 밖에 격리**해 확인 |
| E8 | `where python3` / `where python` / `python3 --version` | Windows 인터프리터 별칭 실재 확인 |
| E9 | `git cat-file -e 0df7d6e:scripts/scorecard_cli.py` 등 | structure.md 선언 기준 커밋 내용 확인 |
| E10 | `python -B -X utf8 inspect_rules.py` | `rules/v1.5.json` 체크리스트·결정·factor 모드 인벤토리 |

`-B` 를 붙여 `__pycache__` 생성을 막았다. E7 은 worker 모듈을 `import` 하고 `validate_approval()` 을 호출만 하며 파일을 쓰지 않는다(호출 대상은 메모리 dict).

### 1.2 실행하지 않은 것 (지시 또는 부작용 때문에 정적 확인만)

- 금지 목록: `import-baseline`, `init`, `research`, `calculate`, `draft`, `review-template`, `approve`, `build`, `npm test` → **코드 읽기로만 확인**. 이들 출력 문자열은 `scorecard_cli.py`·`stages.py`·`render_html.py` 의 리터럴을 인용했다.
- `npm run check` 도 실행하지 않았다. `package.json:8` 의 `python3 -m compileall -q scripts` 가 worker/scripts 에 `__pycache__` 를 **쓰므로** 읽기 전용 제약에 어긋나기 때문이다. 따라서 D-06 의 "python3 없는 Windows 에서 실패"는 **정적 추론**이다.
- 네트워크 조사·설치·새 에이전트 생성 없음. worker 수정·커밋·checkout·merge 없음.
- 동작 실험이 필요했던 E7 만 `scarpper/validation/qwen-cli-doc-02/` 안의 최소 fixture 로 격리했고 worker 경로를 바꾸지 않았다.

### 1.3 검토 파일과 시작 해시

전체 목록은 `inv-start.txt` · `hashes-start.json` 참조. 핵심만:

| 파일 | bytes | 줄 | SHA-256[:16] |
|---|---:|---:|---|
| README.md | 12,634 | 240 | `ea313e4bacf79100` |
| AGENTS.md | 9,700 | 90 | `6afb005d0f42a19e` |
| docs/scorecard/structure.md | 10,784 | 116 | `e6ea3fb0a6f10eff` |
| scripts/scorecard_cli.py | 7,218 | 181 | `867c6e930a880f27` |
| scripts/scorecard/stages.py | 12,174 | 258 | `c95e7a0e5fe56807` |
| scripts/scorecard/validate.py | 13,228 | 252 | `222daf9bec8a649f` |
| scripts/scorecard/engine.py | 6,243 | 166 | `b171a9894ef43922` |
| scripts/scorecard/schema.py | 23,211 | 414 | `b0c7f7f069bf3fb5` |
| scripts/scorecard/render_md.py | 32,050 | 476 | `df056404a1bd5632` |
| scripts/scorecard/render_html.py | 45,395 | 612 | `024df37f10c95378` |
| scripts/scorecard/baseline_import.py | 30,390 | 562 | `71dfec112370f4c0` |
| scripts/build_report.py | 44,161 | 888 | `515112f3345cc5dc` |
| scripts/validate_report_contract.py | 20,823 | 486 | `8f5f72d289b8155d` |
| scripts/report_contract_lib.py | 10,094 | 311 | `cd5c9d068a511698` |
| package.json | 731 | 20 | `c34464fafc5b0c99` |
| scorecard/rules/v1.5.json | 19,210 | 597 | `9231b3a05ba5c766` |
| scorecard/baseline/v1.5/observations.json | 93,381 | 3,259 | `f22e9415e1dbe056` |
| tests/test_scorecard_calc.py | 27,659 | 456 | `3a111001470dc391` |
| `.claude/commands/score-*.md` 8개 | 각 ~500 | 각 12 | `dump-commands.txt` |
| `.claude/skills/score-*/SKILL.md` 8개 | 1,105~2,344 | 23~31 | `dump-skills.txt` |

## 2. 통과 — 문서와 CLI 가 일치하는 24개 항목

### 2.1 `/score-*` 명령 ↔ Python CLI 대응 (8개 전부)

| 명령 | 문서가 가리키는 실행기 | 실제 | 판정 |
|---|---|---|---|
| `/score-plan` | `score-plan/SKILL.md:17` `scorecard_cli.py init …` (+ `:14` 기준선 없으면 `import-baseline`) | `init` 서브파서 `scorecard_cli.py:135-149` | pass |
| `/score-research` | `score-research/SKILL.md:17` `… research <slug>` | `:157-160` | pass |
| `/score-calculate` | `score-calculate/SKILL.md:10` `… calculate <slug>` | `:157-160` | pass |
| `/score-draft` | `score-draft/SKILL.md:10` `… draft <slug>` | `:157-160` | pass |
| `/score-review` | `score-review/SKILL.md:10` `… review-template <slug>` + `:18` `validate_report_contract.py <slug>` | `:162-165`, `validate_report_contract.py:470-471` | pass |
| `/score-approve` | `score-approve/SKILL.md:14` `… approve <slug> --by "<이름>" [--note …]` | `:167-171` | pass (단 D-02·D-07) |
| `/score-build` | `score-build/SKILL.md:10` `build_report.py <slug>` (scorecard_cli 에 build 없음) | `build_report.py:392-396` 이 `build_scorecard(slug)` 로 위임 | pass |
| `/score-goal` | CLI 없음 — `score-goal/SKILL.md:15` "Skill 도구로 하위 스킬을 호출하지 않는다. 각 score-* SKILL.md 의 절차를 인라인으로 수행" | 오케스트레이션 전용 | pass |

CLI 독스트링 `scorecard_cli.py:15` "build 는 기존 명령 `python scripts/build_report.py <slug>` 가 report_type 으로 분기한다" ↔ `structure.md:13` ↔ `score-build/SKILL.md:10` ↔ `AGENTS.md:62` 4곳 일치.

CLI 에만 있고 명령이 없는 서브커맨드: `import-baseline`(→D-08), `status`(→D-09).

### 2.2 나머지 일치 확인

3. **`init` 필수값** — argparse 실측(E3) `--as-of`·`--title`·`--request` required ↔ `README.md:223`·`score-plan/SKILL.md:17`·CLI 독스트링 `:5` 모두 세 개를 필수로 표기.
4. **slug 규칙** — `stages.py:52-53` 이 `ai-scorecard-` 접두를 `SchemaError` 로 강제 ↔ `score-plan/SKILL.md:13` "`ai-scorecard-<YYYY-MM>-<label>`" ↔ `README.md:231`·`AGENTS.md:60`·`structure.md:10` 일치. 오류 문구에 예시까지 들어 있다.
5. **`init` 산출물 5개** — `stages.py:124` 반환 `{plan, run, observations, judgments, sources}` ↔ `score-plan/SKILL.md:8` "`plan/<slug>.md` 와 `scorecard/runs/<slug>/{run,observations,judgments,sources}.json`" ↔ `README.md:223` ↔ `structure.md:73` 전부 일치.
6. **선행 산출물 게이트와 메시지** — 아래 표. 문서의 "확인한다/먼저" 서술과 코드의 `_require_file`(`stages.py:256-258`) 이 단계별로 정확히 대응.

| 단계 | 코드 | 실제 오류 문구 | 문서 |
|---|---|---|---|
| research | `stages.py:129` plan | `선행 산출물 없음: plan (…)` | `score-research/SKILL.md:12` ✓ |
| calculate | `stages.py:140-141` plan+research | 동일 형식 | 파이프라인 순서로 충족 ✓ |
| draft | `stages.py:152-154` plan+research+results | `선행 산출물 없음: results.json (calculate 먼저)` | ✓ |
| review-template | `stages.py:165-169` draft + 기존 파일 시 `--force` | `리뷰 파일이 이미 있음: … (--force 로 템플릿 재생성)` | `score-review/SKILL.md:10` "이미 있으면 `--force` 는 리뷰를 새로 시작할 때만" ✓ |
| approve | `stages.py:207-209` | `승인 전 계약 검증 실패: …` | `score-approve/SKILL.md:12` ✓ |
| build | `render_html.py:583-593` | `Cannot build until pre-build contract errors are fixed` / `awaiting_user` 2종 | `score-build/SKILL.md:11` "`awaiting_user` 메시지가 나오면 승인이 없거나 무효다" ✓ (두 조건과 정확 대응) |

7. **리뷰 템플릿 기본 status** — `render_md.py:429` `("status", "needs_fix")` ↔ `structure.md:81` "review-template ──► reviews/<slug>.md (4 영역 + Q01~Q23, status: needs_fix)" ✓
8. **체크리스트 Q01~Q23** — `rules/v1.5.json` 실측(E10) 23개, ID Q01~Q23 연속·중복·결번 없음 ↔ `AGENTS.md:67`·`score-review/SKILL.md:3,14,16`·`structure.md:29,81,108` ✓
9. **검토 영역 4개** — `validate.py:161-176` 이 `REVIEW_AREAS` 4라벨을 요구하고 `status == "pass"` 일 때 검토자 공란을 `수행하지 않은 검토를 pass 로 표시할 수 없음` 으로 차단 ↔ `score-review/SKILL.md:11-16` 의 4영역(fact-checker / 재무 계산 / 규칙 일관성 / report-designer) ↔ `structure.md:108` T-13 ✓
10. **승인 해시 6종** — `stages.py:191-203` `current_hashes` = rules·observations·judgments·run·results·draft ↔ `AGENTS.md:68` "승인 해시(rules/observations/judgments/run/results/draft)" ↔ `structure.md:38` approval.json 필수 필드 ↔ `schema.py:412` `_expect_keys(... hashes ...)` 6키 — **4곳 완전 일치**.
11. **승인 자동 무효화** — `stages.py:147-151` calculate 가 results_hash 불일치 시 이전 `approval.json` 을 삭제 ↔ `structure.md:75` "입력 해시가 바뀌면 이전 approval.json 자동 무효" ↔ `score-approve/SKILL.md:19` "승인 뒤 자료·규칙·판단·초안이 바뀌면 승인은 무효다" ✓
12. **미결 결정이 승인·빌드를 막지 않는다** — `validate.py` 전문에 `pending_rule_decisions`·`population.incomplete` 검사가 없음 ↔ `score-approve/SKILL.md:20` "미결 규칙 결정이 남아 있어도 승인할 수 있다(미완료 기업은 순위 제외로 표시됨)". **실행 증거(E4)**: 현재 slug 가 `pending_rule_decisions: ["C-06","C-13"]`, `incomplete: 5개사` 인데 **실행 증거(E6)** 의 검증 오류는 review status 1건뿐 → 미결 결정은 오류를 만들지 않았다. ✓ (단 생성된 plan 본문은 반대로 서술 → D-01)
13. **리뷰 미완료 차단** — `validate.py:151-152` `status != "pass"` 면 오류. **실행 증거(E6)**: `error - reviews\ai-scorecard-2026-09-baseline.md review status 가 pass 가 아님: 'needs_fix'` → `score-approve/SKILL.md:12`·`score-review/SKILL.md:22` 의 "pass 일 때만 승인 요청 가능" 과 일치 ✓
14. **draft 결속 검사** — `validate.py:120-129` results_hash·plan_source·research_source·순위표 행 대조. **실행 증거(E6)**: `ok - results deterministic recompute`, `ok - draft ranking table matches results` ✓
15. **`score-draft/SKILL.md:13` 의 "리뷰 파일이 없으면 그 오류만 남는 것이 정상이다"** — `validate.py:147-149` 가 review 부재 시 오류 1건만 남기고 `return result` 하는 것과 일치 ✓ (E6 에서는 review 가 존재하고 needs_fix 라 오류 1건)
16. **관측 status 목록** — `structure.md:34` 가 `verified / legacy_unverified / not_disclosed / collection_failed / source_conflict / incompatible_basis / parse_failed` 7개 ↔ `score-research/SKILL.md:13-14` 가 `verified`(새 자료)·`collection_failed`·`not_disclosed`·`incompatible_basis` 를 안내. 모순 없음 ✓ (`parse_failed` 가 구조 문서에 등록되어 QWEN-BASELINE-01 P10 의 문서 보완이 반영된 것을 확인. 재논쟁하지 않는다.)
17. **판단 kind** — `structure.md:35` `score/grade/criteria/matrix/paths/gate_inputs` ↔ `AGENTS.md:65` "③ criteria, ⑤ A/H, ⑦ 매트릭스, ⑨ gate_inputs, ①④⑧ score" ↔ `score-research/SKILL.md:16` "F3 criteria, F5 grade, F7 matrix, F9 gate_inputs" — 모순 없음 ✓
18. **draft 필수 섹션 (stock 과 혼동 없음)** — `validate.py:25` `["개요","종합 순위표","기업별 상세","지표 원자료","방법과 규칙","References"]` + H1 1개 ↔ `score-draft/SKILL.md:12` 정확히 같은 6섹션 + `# 제목` 1개 ↔ `structure.md:76` ✓. stock 의 `["개요","배경","메커니즘","영향과 적용","References"]`(`report_contract_lib.py:48`) 와 완전히 분리돼 있어 **기존 stock 섹션 요구가 scorecard 에 섞이지 않는다**.
19. **hero 이미지·뉴스 100건·price-chart 면제** — `validate_report_contract.py:408-411` 이 ai_scorecard 를 `validate_scorecard` 로 위임하면서 `require_price_chart`·`check_price_chart_if_present` 를 **전달하지 않음** ↔ `AGENTS.md:67` "hero 이미지·뉴스 100건 요건은 적용하지 않는다" ↔ `structure.md:12,14` ✓. `stages.py:207` approve 가 `require_price_chart=False` 등을 넘기지만 ai_scorecard 분기는 두 인자를 받지 않아 무해.
20. **훅 면제가 문서 주장대로 구현됨** — `structure.md:99` "enforce-plan.sh(scorecard 이미지 면제, review pass 는 유지), enforce-citations.sh(scorecard draft 건너뜀)" ↔ 실코드 `.claude/hooks/enforce-plan.sh:176-177` "ai_scorecard 는 hero 이미지·뉴스 요건이 없다(설계 지침 9절). review pass 요건은 두 유형 모두 유지" + `scorecard = report_type(slug) == 'ai_scorecard'`, `.claude/hooks/enforce-citations.sh:50-51` "ai_scorecard draft 는 results.json 해시로 결속된 생성물이라 … stock draft 만 마커를 요구" + `paths = [p for p in paths if report_type(Path(p).stem) != 'ai_scorecard']` ✓
21. **`--require-html` 플래그 실재** — `validate_report_contract.py:471` ↔ `score-build/SKILL.md:12`·`.claude/commands/score-build.md:11` ✓
22. **`node server.js <slug>`** — `server.js:9` `process.argv[2] || process.env.REPORT_SLUG || process.env.REPORT` ↔ `score-build/SKILL.md:13` ↔ `README.md:205-208` ↔ `README.md:243` `npm start -- <slug>` ↔ `package.json:7` `"start": "node server.js"` ✓
23. **`--decision` 형식과 동반 필수값** — `scorecard_cli.py:48-53` 이 `ID=choice` 형식을 강제하고 `--rationale`·`--by` 를 동시 요구(`--decision 을 쓰면 --rationale 과 --by 가 필요하다`) ↔ CLI 독스트링 `:5` `[--decision C-16=hold --rationale "..." --by NAME]` ↔ `score-plan/SKILL.md:19` "`--decision` 은 사용자가 근거와 함께 명시적으로 지시했을 때만 넣는다. 기본은 미결" ↔ `structure.md:36` `decisions[{id, choice, rationale, decided_by, decided_at}]` ✓
24. **미결 결정 목록 (blocking 5개)** — `rules/v1.5.json` 실측(E10): 결정 22개(C-01~C-22) 중 `status=pending & blocking=true` 는 **C-03, C-05, C-06, C-13, C-16** 5개 ↔ `README.md:233` "(C-03/05/06/13/16)" ↔ `AGENTS.md:66` "(C-03, C-05, C-06, C-13, C-16)" ↔ `structure.md:61` "status == pending 이고 blocking: true 인 항목(C-03, C-05, C-06, C-13, C-16)" — **3곳 정확 일치** ✓ (단 D-13)
25. **Windows 경로 비교 방어** — `validate.py:31-33` `prel()` 이 frontmatter 의 POSIX 경로와 Windows `rel()` 백슬래시를 정규화해 비교 ↔ **실행 증거(E6)** 에서 `ok - research bound to input hashes`, `ok - draft ranking table matches results` 가 Windows 에서 정상 통과 ✓
26. **`score-goal` 의 승인 정지가 4곳에서 일관** — `score-goal/SKILL.md:18` "review pass 뒤 **멈춘다**. 승인은 사용자 행위다. approve/build 를 자동 실행하지 않는다" ↔ `.claude/commands/score-goal.md:11` "승인(approve)과 빌드는 사용자 결정 뒤에만 진행" ↔ `score-approve/SKILL.md:8` "에이전트가 스스로 승인하거나 `score-goal` 안에서 자동 실행하지 않는다" ↔ `AGENTS.md:68` ✓ (단 실효성은 D-02)

## 3. 문제

각 항목에 **정적 추론**인지 **실제 실행 결과**인지 표시했다.

---

### D-01 · high — 생성되는 plan 의 "차단 조건"이 실제 차단 조건과 다르다

- **문서 위치**: 생성 산출물 `plan/<slug>.md` 의 `## 완료/차단 조건`. 원천은 `scripts/scorecard/render_md.py:149`
  ```
  - 차단: 외부 자료 미확보가 반복되거나 규칙 결정이 필요한데 사용자 결정이 없는 경우 `awaiting_user`
  ```
- **실제 코드 위치**:
  - `awaiting_user` 가 발생하는 곳은 **정확히 두 군데**뿐: `scripts/scorecard/render_html.py:590`(승인 파일 없음) 과 `:593`(승인 해시 ≠ 현재 해시). 검증기 쪽 대응 문구는 `scripts/scorecard/validate.py:195`·`:202`.
  - 자료 부족 → `pending_data` (`scripts/scorecard/inputs.py:62`, `calc_f9.py:21-23`) → `aggregate` 가 `incomplete` 로 분류 → 공식 순위 제외. calculate·draft·build 어디에서도 `awaiting_user` 를 일으키지 않는다.
  - 규칙 미결 → `needs_rule_decision` (`calc_qual.py:52,58`, `calc_f6.py:96`, `calc_f9.py:99,114,170,208`) → 동일하게 순위 제외일 뿐.
- **재현 명령·출력 (실제 실행)**:
  ```
  $ python -B -X utf8 scripts/scorecard_cli.py status ai-scorecard-2026-09-baseline
    "review_status": "needs_fix", "approval": false, "html": false,
    "pending_rule_decisions": ["C-06", "C-13"],
    "scored": 9, "incomplete": ["amazon","tsmc","alibaba","anthropic","spacex-xai"]
  ```
  → 미결 결정 2건과 미완료 5개사가 있는데도 파이프라인은 draft·review 까지 진행됐고 `awaiting_user` 는 발생하지 않았다.
  ```
  $ grep -n "차단" plan/ai-scorecard-2026-09-baseline.md
    109:## 완료/차단 조건
    112:- 차단: 외부 자료 미확보가 반복되거나 규칙 결정이 필요한데 사용자 결정이 없는 경우 `awaiting_user`
  ```
  → 커밋된 실물 plan 에 문제의 문구가 그대로 들어 있다.
- **교차 모순 (문서 3곳이 코드와 같은 편)**:
  - `.claude/skills/score-approve/SKILL.md:20` "미결 규칙 결정이 남아 있어도 승인할 수 있다(미완료 기업은 순위 제외로 표시됨)"
  - `.claude/skills/score-goal/SKILL.md:16` "규칙 결정(C-xx)이 필요하면 사용자에게 묻지 말고 미결 상태 그대로 계산한다. 미완료 기업은 순위에서 제외되며 preview.md 에 필요한 결정이 남는다"
  - `docs/scorecard/structure.md:85` "`자료 부족 pending_data`, `판단 부족 needs_judgment`, `규칙 미결 needs_rule_decision`, `승인 필요 awaiting_user`(**빌더 메시지**), `검토 미완 needs_fix`" — 5개 상태를 정확히 분리 정의
- **기대 동작**: plan 의 완료/차단 조건은 실제 게이트를 서술해야 한다. 자료 부족·규칙 미결은 "차단"이 아니라 "해당 기업 순위 제외 + 상태로 표시 + 파이프라인 계속"이고, `awaiting_user` 는 승인 게이트 전용이다.
- **최소 수정안**: `render_md.py:149` 한 줄 교체.
  ```
  - 제외: 외부 자료 미확보는 `pending_data`, 규칙 결정 미결은 `needs_rule_decision` 으로 표시되고 해당 기업은 공식 순위에서 빠진다. 파이프라인은 계속 진행된다.
  - 차단: `awaiting_user` 는 승인 게이트 전용이다 — approval.json 이 없거나 승인 이후 규칙·자료·판단·결과·초안이 바뀌어 해시가 어긋나면 빌더가 멈춘다.
  ```
  (렌더러 수정이므로 plan/draft 재생성이 필요. 이 검증에서는 worker 를 수정하지 않았다.)
- **심각도 근거**: plan 은 "이후 단계의 단일 기준 문서"(`README.md:15`, `AGENTS.md:5`)다. 사용자와 에이전트 모두가 이 문장을 읽고 "미결 결정이 있으면 멈춘다"고 오해하면, 실제로는 5개사가 조용히 순위에서 빠진 채 build 까지 성공한다. `score-goal` 은 review 까지 한 턴에 연속 실행하므로(`SKILL.md:14`) 중간에 사용자가 알아차릴 지점도 없다.
- **판정 방식**: 코드 정적 확인 + **실제 실행**(E4, plan 파일 grep)

---

### D-02 · high — `approve --by` 값이 검증되지 않아 승인 주체가 빈 값·공백·`None`·숫자여도 통과한다

- **문서 위치 (승인은 사용자 행위라고 반복해서 선언)**:
  - `.claude/skills/score-approve/SKILL.md:8` "승인은 사용자 행위다. 에이전트가 스스로 승인하거나 `score-goal` 안에서 자동 실행하지 않는다."
  - `.claude/skills/score-approve/SKILL.md:14` `python scripts/scorecard_cli.py approve <slug> --by "<사용자 이름>" [--note "..."]`
  - `.claude/commands/score-approve.md:2` "사용자의 명시적 지시로만 실행합니다", `:11` "승인은 사용자 행위이므로 사용자가 이 명령을 직접 내렸을 때만 `approve`를 실행하고"
  - `AGENTS.md:68` "승인(`approve`)은 사용자 행위다."
  - `README.md:228` "`approve <slug> --by <이름>` (사용자 행위)"
- **실제 코드 위치**:
  - `scripts/scorecard_cli.py:169` `p.add_argument("--by", required=True)` — `required=True` 는 **플래그의 존재**만 요구하고 값은 검사하지 않는다.
  - `scripts/scorecard_cli.py:117` → `stages.py:205,217` `"approved_by": approved_by` — 받은 값을 그대로 기록.
  - `scripts/scorecard/schema.py:406-413` `validate_approval()` → `_expect_keys(...)`(`:128-136`) 는 **키 존재와 미등록 키**만 본다. `approved_by` 의 자료형·길이·공백 검사가 없다. `_expect_date` 는 `approved_at` 에만 적용(`:412`).
  - `scripts/scorecard/render_html.py:567` `승인 {esc(approval["approved_by"])} {esc(approval["approved_at"])}` → **최종 공개 HTML footer** 에 렌더링.
- **재현 명령·출력 (실제 실행, worker 밖 격리)**:
  ```
  $ python -B -X utf8 scarpper/validation/qwen-cli-doc-02/isolated_approve_test.py
  ACCEPT  argv=['s', '--by', '홍길동']  -> by='홍길동' (len=3, strip_len=3)
  ACCEPT  argv=['s', '--by', '']        -> by=''       (len=0, strip_len=0)
  ACCEPT  argv=['s', '--by', '   ']     -> by='   '    (len=3, strip_len=0)
  REJECT  argv=['s']                    -> SystemExit(2)  # error: the following arguments are required: --by
  PASS-SCHEMA  approved_by='홍길동'  -> 검증 통과
  PASS-SCHEMA  approved_by=''       -> 검증 통과
  PASS-SCHEMA  approved_by='   '    -> 검증 통과
  PASS-SCHEMA  approved_by=None     -> 검증 통과
  PASS-SCHEMA  approved_by=7        -> 검증 통과
  FAIL-SCHEMA  approved_by 키 없음 -> approval.json: 필수 키 누락 ['approved_by']
  ```
  (1번 실험은 `scorecard_cli.py:167-171` 과 동일한 argparse 정의를 격리 재현. 2번은 worker 의 `scorecard.schema.validate_approval` 을 import 해 메모리 dict 에 호출 — 파일 쓰기 없음. worker 의 `approve` 자체는 실행하지 않았다.)
- **기대 동작**: 승인 주체는 감사 기록의 핵심이므로 빈 값·공백-only 를 거부하고, 스킬은 "사용자가 이름을 주지 않으면 묻고 에이전트가 이름을 지어내지 않는다"를 명시.
- **최소 수정안**:
  1. `schema.py:validate_approval` 에 한 줄 — `_require(isinstance(payload["approved_by"], str) and bool(payload["approved_by"].strip()), "approval.json.approved_by: 빈 승인자 이름")`
  2. `score-approve/SKILL.md:14` 앞에 한 줄 — "승인자 이름(`--by`)은 사용자가 직접 알려준 값만 쓴다. 없으면 묻고, 에이전트 이름이나 임의 문자열·빈 값을 넣지 않는다."
- **심각도 근거**: `approval.json` 은 rules·observations·judgments·run·results·draft 6개 해시와 결합된 감사 기록이고(`AGENTS.md:68`, `structure.md:38`), 그 승인자명이 최종 HTML 에 공개된다. "승인은 사용자 행위"라는 통제가 4개 문서에 반복돼 있지만 **기술적으로는 아무것도 강제되지 않는다** — 지시문이 요청한 "승인 주체를 에이전트가 대신 입력하도록 오해시키는 안내"의 실체가 여기 있다. 스킬 문구가 에이전트에게 `--by "<사용자 이름>"` 을 채우라고 지시하는 형태라, 사용자 이름을 모르는 에이전트가 자리표시자나 빈 값으로 채워도 전 파이프라인이 통과한다.
- **판정 방식**: **실제 실행**(E7) + 코드 정적 확인

---

### D-03 · medium — `init` 의 `--price-as-of`·`--info-cutoff` 가 어떤 문서에도 없어 C-17 분리가 사실상 불가능하다

- **실제 argparse (실행 E3)**:
  ```
  usage: scorecard_cli.py init [-h] --as-of AS_OF --title TITLE --request REQUEST
        [--purpose PURPOSE] [--companies COMPANIES] [--baseline BASELINE] [--rule RULE]
        [--decision DECISION] [--rationale RATIONALE] [--by BY]
        [--price-as-of PRICE_AS_OF] [--info-cutoff INFO_CUTOFF] [--force] slug
  ```
  기본값(`scorecard_cli.py:141-142`): `--baseline v1.5`, `--rule v1.5`. `--price-as-of`·`--info-cutoff` 는 기본값 없음.
- **문서 누락**:
  - `scripts/scorecard_cli.py:5` 모듈 독스트링 usage 행 — `--baseline`·`--rule`·`--price-as-of`·`--info-cutoff` **4개 없음** (`--force` 는 있음). 이 독스트링이 `argparse.RawDescriptionHelpFormatter`(`:130`) 때문에 **`--help` 본문으로 그대로 출력된다**(E2 에서 확인).
  - `.claude/skills/score-plan/SKILL.md:17` — 위 4개 + `--force` **5개 없음**
  - `README.md:223` — `--as-of --title --request` 만
- **코드 동작**: `stages.py:71-72` `"price_as_of": price_as_of or as_of`, `"info_cutoff": info_cutoff or as_of` → 문서대로만 실행하면 **세 값이 항상 동일**.
- **그런데 산출물은 "분리 기록"을 주장한다**:
  - `stages.py:80` run.json `assumptions` 에 `"가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)"`
  - `render_md.py:95` plan frontmatter 에 `price_as_of`·`info_cutoff`, `:116`·`:248`·`:272` 본문에 "분석 기준일 X · 가격 기준일 Y · 정보 컷오프 Z (C-17: 셋을 분리 기록)"
  - `structure.md:36` run.json 필수 필드에 `price_as_of`, `info_cutoff` 포함
- **재현 명령·출력 (실제 실행)**:
  ```
  $ grep -n "가격 기준일" plan/ai-scorecard-2026-09-baseline.md
    34:  - 가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)
    48:- 분석 기준일 `as_of` 2026-09-02 · 가격 기준일 2026-09-02 · 정보 컷오프 2026-09-02 (C-17: 셋을 분리 기록)
  ```
  → 세 날짜가 모두 `2026-09-02` 로 같으면서 "셋을 분리 기록"한다고 써 있다.
- **추가 (검증도 안 됨)**: `report_contract_lib.py:52-66` `REQUIRED_SCORECARD_PLAN_FRONTMATTER` 14개 키(slug, report_type, topic, request, output_type, audience, run_id, as_of, rule_version, rule_hash, baseline_id, companies, created_at, assumptions) 에 `price_as_of`·`info_cutoff` 가 **없다**. plan frontmatter 에 렌더링은 되지만(`render_md.py:95`) 검증되지 않는다.
- **기대 동작**: C-17(기준일 9/2 인데 9/3~9/7 사건이 섞이는 문제 — `rules/v1.5.json` C-17 `status=documented`)을 실제로 분리하려면 옵션이 문서에 있어야 한다.
- **최소 수정안**: `scorecard_cli.py:5` usage 행과 `score-plan/SKILL.md:17` 명령 블록에 `[--price-as-of YYYY-MM-DD] [--info-cutoff YYYY-MM-DD] [--baseline v1.5] [--rule v1.5]` 추가. SKILL 1번 단계("요청을 파싱한다…분석 기준일")에 "가격 기준일·정보 컷오프가 기준일과 다르면 `--price-as-of`·`--info-cutoff` 로 분리 기록한다(C-17)" 한 줄 추가. (검증 강화 — `REQUIRED_SCORECARD_PLAN_FRONTMATTER` 에 두 키 추가 — 는 설계 판단이므로 별도.)
- **판정 방식**: **실제 실행**(E2, E3, plan grep) + 코드 정적 확인

---

### D-04 · medium — 문서 3곳이 T-01~T-12 커버리지를 주장하나 T-08 테스트가 없다

- **문서 위치**:
  - `README.md:234` "테스트: `npm run test:scorecard` (T-01~T-12, R01~R06)."
  - `AGENTS.md:70` "테스트: `python -X utf8 -m unittest discover -s tests -t .`(T-01~T-12, R01~R06). 코드 변경 후 반드시 실행한다."
  - `docs/scorecard/structure.md:107` (§8 회귀·수용 기준 매핑) "| T-01~T-12 | `tests/test_scorecard_calc.py` |"
- **T-08 정의**: `docs/scorecard/design-guideline.md:444`
  "| T-08 | YTD/분기 혼재·정정 공시·연결/세그먼트 혼재 | 검증된 변환만 허용하고 중복 TTM 차단 |"
- **실제 코드 위치**: `tests/test_scorecard_calc.py` (456줄) — grep 결과 `test_t08*` **없음**, `T-08` 문자열 **없음**. 존재하는 테스트 이름:
  `test_t01_band_boundaries_half_open`(:84), `test_t01_display_rounding_does_not_change_band`(:97), `test_t02_boundary_flag_only_warns`(:102), `test_t03_missing_or_bad_eps_blocks`(:111), `test_t04_f3_all_combinations`(:157), `test_t05_f5_grades`(:182), `test_t06_f7_matrix`(:193), `test_t07_fcf_sign_normalization`(:238), `test_t09_runway_boundaries`(:253), `test_t10_g1_requires_decision_then_bands`(:268), `test_t11_coverage_rules`(:302), `test_t12_ties_and_incomplete`(:352) + R01~R06(:375,384,390,395,400,406,414,446).
  테스트 파일은 이것 하나뿐이다(`tests/` = `__init__.py` + `test_scorecard_calc.py`, 인벤토리 실측).
- **내부 모순**: `structure.md:40-55` (§3 요구→모듈→테스트 매핑 표) 자체에도 **T-08 행이 없다**. 표가 참조하는 T-xx 는 T-01·T-02·T-03(:49), T-04·T-05·T-06·T-07·T-09·T-10·T-11(:43-51), T-12(:52), T-17(:54), T-03·T-05·T-06·R05·R06(:55). 즉 같은 문서의 §3 은 T-08 을 빼놓고 §8(:107) 은 T-01~T-12 를 주장한다.
- **부분 완충 (과장 방지)**: `test_r01_duplicate_or_nonconsecutive_quarters`(:375) 가 중복·비연속 분기를 다루므로 T-08 의 "중복 TTM 차단" 일부와 겹친다. 그러나 **"정정 공시(restatement)"와 "연결/세그먼트 혼재"는 어떤 테스트에서도 다뤄지지 않는다.**
- **재현 명령**:
  ```
  $ grep -nE "t08|T-08" tests/test_scorecard_calc.py     # 결과 없음
  $ grep -nE "test_t[0-9]+" tests/test_scorecard_calc.py  # t01,t01,t02,t03,t04,t05,t06,t07,t09,t10,t11,t12
  ```
  (`npm run test:scorecard` 는 실행하지 않았다 — 금지 목록.)
- **기대 동작**: 문서가 주장하는 커버리지와 실제 테스트 집합이 일치.
- **최소 수정안**: (a) 문서 3곳을 "T-01~T-07, T-09~T-12 (T-08 미구현)" 으로 정정하고 `structure.md` §3 표에 T-08 행을 "미구현" 으로 추가, 또는 (b) `test_t08_*` 추가. (b) 는 구현 담당 범위.
- **판정 방식**: 정적 확인 (grep). 테스트 실행은 금지 목록이라 하지 않았다.

---

### D-05 · medium — 검증기가 실패한 검사에도 `ok -` 줄을 출력한다

- **재현 명령·출력 (실제 실행 E6)**:
  ```
  $ python -B -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-09-baseline
  [FAIL] report contract: ai-scorecard-2026-09-baseline
    ok - scorecard plan frontmatter
    ok - run.json/observations/judgments strict schema
    ok - research bound to input hashes
    ok - results deterministic recompute
    ok - draft ranking table matches results
    ok - review 4-area + checklist structure
    error - reviews\ai-scorecard-2026-09-baseline.md review status 가 pass 가 아님: 'needs_fix'
  ```
- **실제 코드 위치**:
  - `scripts/validate_report_contract.py:104-105` `def check(self, message): self.checks.append(message)` — **조건 없음**.
  - `:456-463` `print_result()` 는 `result.ok` 와 무관하게 `checks` 를 전부 `ok - ` 로 출력. (`ok` 프로퍼티 `:95-96` 은 `not self.errors`.)
  - `scripts/scorecard/validate.py` 에서 `result.check(...)` 는 해당 블록에서 `result.error(...)` 가 이미 호출됐어도 무조건 실행된다:
    - `:73` `check("scorecard plan frontmatter")` — `:63`(필수 키 누락), `:66`(report_type), `:68`(run_id), `:70`(없음) 에서 error 가능
    - `:88` `check("run.json/observations/judgments strict schema")` — `:82`(rule_version), `:84`(rule_hash), `:86`(as_of) 에서 error 가능
    - `:129` `check("draft ranking table matches results")` — for-else 구조라 순위표 행 누락 시 error 후에도 도달하지 않지만, `:118`(H1), `:121`(섹션), `:123`(results_hash), `:125`(source) 의 error 와 무관하게 출력
    - `:186` `check("review 4-area + checklist structure")` — `:152`(status), `:155`(source 3종), `:157`(review_type), `:159`(review_execution), `:161`(results_hash), `:164`(draft_hash), `:170`(영역 누락), `:172`(영역 결과), `:176`(검토자 미기재), `:181-185`(체크리스트 4종) 에서 error 가능
- **영향**: 위 실행 예에서 review status 가 `needs_fix` 인데도 `ok - review 4-area + checklist structure` 가 함께 출력된다. 이번에는 우연히 영역·체크리스트 구조가 실제로 정상이었지만, 예컨대 체크리스트 Q07 행이 누락돼 `error - 체크리스트 Q07 행 누락` 이 나도 같은 `ok -` 줄이 옆에 붙는다. `structure.md:108` (§8 T-13) 이 "검증기: 체크리스트 23행·4 영역·검토자 없는 pass 차단" 을 바로 이 check 라벨로 추적하므로, **라벨이 자기 영역의 실패를 가린다.**
- **기대 동작**: `ok -` 줄은 그 블록에서 error 가 없을 때만 출력.
- **최소 수정안**: 각 블록 시작에서 `before = len(result.errors)` 를 잡고 끝에서 `if len(result.errors) == before: result.check("…")` 로 감싼다 (4곳). `ValidationResult.check` 자체를 `if not self.errors:` 조건부로 만들면 기존 stock 검증 경로(`:413-455`)의 출력까지 바뀌므로 전자(블록 단위)를 권장.
- **판정 방식**: **실제 실행**(E6) + 코드 정적 확인

---

### D-06 · medium — `structure.md` 의 "Windows 는 `python3` 를 가정하지 않는다"가 package.json·README·AGENTS 와 모순

- **문서 위치**: `docs/scorecard/structure.md:101` (§7)
  "Windows: `python` 실행 파일로 동작하며 `python3` 를 가정하지 않는다. 훅은 Git Bash + python3 별칭 환경에서 동작한다."
- **모순 대상 (실측)**:

| 위치 | 내용 | 인터프리터 |
|---|---|---|
| `package.json:8` | `"check": "node --check server.js && python3 -m compileall -q scripts"` | `python3` |
| `package.json:9` | `"validate:memory": "python3 scripts/validate_memory.py"` | `python3` |
| `package.json:10` | `"validate:report": "python3 scripts/validate_report_contract.py"` | `python3` |
| `package.json:11` | `"build:report": "python3 scripts/build_report.py"` | `python3` |
| `package.json:12` | `"test": "npm run check && npm run validate:memory && npm run test:scorecard"` | → **python3 요구** |
| `package.json:13` | `"test:scorecard": "python -X utf8 -m unittest discover -s tests -t ."` | `python` |
| `package.json:14` | `"scorecard": "python scripts/scorecard_cli.py"` | `python` |
| `README.md:95,120,127,130,147,165,166,172,178,179,185,191` | stock 계약·보조 명령 전부 | `python3` |
| `README.md:223-234` | scorecard 표 | `python` |
| `AGENTS.md:38,53,54,57,88` | stock 계약·memory | `python3` |
| `AGENTS.md:62` 등 scorecard 절 | scorecard | `python` |

- **실측 (E8)**: 이 머신에는 **둘 다 있다** — `where python3` → `D:\python3121\python3.exe`, `where python` → `D:\python3121\python.exe`, `python3 --version` → `Python 3.12.1`. 따라서 여기서는 `npm test` 가 동작한다.
- **판정**: **이 머신에서의 고장은 아니다.** 그러나 (a) 문서의 일반 주장이 저장소 자신의 npm 스크립트와 모순되고, (b) `python3` 별칭이 없는 Windows(기본 설치는 `python`/`py` 만 제공) 에서는 `npm test`·`npm run check`·`npm run build:report`·`npm run validate:*` 가 전부 실패한다. 같은 `package.json` 안에서 `test`(python3 경유) 와 `test:scorecard`(python) 가 섞여 있어 어느 한쪽만 있는 환경에서는 `npm test` 가 반드시 깨진다. 문체 취향이 아니라 실행 가능성 문제다.
- **재현 명령 (정적)**: `findstr /n "python" package.json` — 위 표와 동일. `npm test` 는 실행하지 않았다(금지 목록 + `compileall` 이 worker 에 `__pycache__` 를 씀).
- **최소 수정안**: `package.json` 의 `python3` 4곳(`:8,9,10,11`)을 `python` 으로 통일 → 그러면 `structure.md:101` 의 주장이 참이 되고 `npm test` 체인이 한 인터프리터로 일관된다. 또는 문서를 정정: "scorecard CLI 는 `python` 으로 동작한다. npm 스크립트(`check`·`validate:*`·`build:report`)와 훅은 `python3` 별칭을 요구한다."
- **판정 방식**: 정적 확인 + **실제 실행**(E8, 인터프리터 존재 확인)

---

### D-07 · low — `/score-approve` 의 `argument-hint` 가 필수 `--by` 를 선택 인자처럼 표시

- **문서 위치**: `.claude/commands/score-approve.md:3` `argument-hint: "<slug> [--by 이름]"` — 대괄호는 관례적으로 선택 인자.
- **실제 코드 위치**: `scripts/scorecard_cli.py:169` `p.add_argument("--by", required=True)`
- **재현 명령·출력 (실제 실행 E3 + E7)**:
  ```
  $ python -B -X utf8 scripts/scorecard_cli.py approve --help
  usage: scorecard_cli.py approve [-h] --by BY [--note NOTE] slug
  ```
  (`--by` 가 대괄호 밖 = 필수)
  ```
  # 격리 argparse 재현 (isolated_approve_test.py)
  REJECT  argv=['s'] -> SystemExit(2)   # error: the following arguments are required: --by
  ```
- **영향**: `/score-approve <slug>` 만 입력하면 argparse 오류로 실패. 단 `.claude/skills/score-approve/SKILL.md:14` 는 `--by "<사용자 이름>"` 을 대괄호 없이 정확히 보여주므로, 스킬까지 읽는 에이전트는 해소된다. 명령 파일의 hint 만 틀렸다.
- **최소 수정안**: `score-approve.md:3` → `argument-hint: "<slug> --by <이름> [--note \"...\"]"`
- **판정 방식**: **실제 실행**(E3, E7)

---

### D-08 · low — `import-baseline` 의 기본 경로가 저장소 밖 머신 고유 절대경로인데 README 에 전제가 없다

- **실제 코드 위치**: `scripts/scorecard/baseline_import.py:11-13`
  ```python
  DEFAULT_SOURCE_DIR = Path(r"E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor")
  DEFAULT_HTML = DEFAULT_SOURCE_DIR / "AI기업_채점표_v1.5.html"
  DEFAULT_MD   = DEFAULT_SOURCE_DIR / "AI기업_채점표_v1.5.md"
  ```
  `scorecard_cli.py:31-32` 가 `--html`·`--md` 미지정 시 이 기본값을 사용.
- **문서 위치**: `README.md:232` "기준선 v1.5 는 `python scripts/scorecard_cli.py import-baseline` 으로 원본 HTML/MD 에서 이관하며 `scorecard/baseline/v1.5/import-report.md` 에 대조 결과가 남습니다." — 원본이 저장소 **밖**이라는 사실, 기본 경로가 특정 머신의 `E:` 드라이브라는 사실, 경로가 다르면 `--html`/`--md` 가 필요하다는 사실이 없다.
- **부분 완화**: `.claude/skills/score-plan/SKILL.md:14` 는 "(원본 HTML/MD 경로가 다르면 `--html`, `--md`)" 로 안내한다. `structure.md:4` 는 "원본(`AI_company_analysis_factor/`)은 저장소 밖 읽기 전용" 이라고 하나 경로는 밝히지 않는다.
- **영향 제한**: `scorecard/baseline/v1.5/` 의 `scores.json`·`observations.json`·`triggers.json`·`import-report.md` 가 **git 에 커밋돼 있음**(인벤토리 실측). 따라서 일반적인 초기 실행은 `import-baseline` 없이 `init` 부터 진행되고, 이 결함은 기준선을 재생성하려 할 때만 드러난다.
- **재현**: 실행하지 않았다(금지 목록). 정적 확인만.
- **최소 수정안**: `README.md:232` 뒤에 추가 — "원본은 저장소 밖 `AI_company_analysis_factor/` 에 있어야 하며 기본 경로는 `scripts/scorecard/baseline_import.py:11` 의 `DEFAULT_SOURCE_DIR` 입니다. 경로가 다르면 `--html`·`--md` 를 넘기세요. 기준선 JSON 은 저장소에 커밋돼 있어 이관 없이도 파이프라인을 실행할 수 있습니다."
- **판정 방식**: 정적 확인

---

### D-09 · low — `status` 서브커맨드가 어떤 문서·slash 명령에도 없다

- **실제 코드 위치**: `scripts/scorecard_cli.py:157-160` 서브파서 등록, `:113-117` `cmd_status`, `stages.py:229-253` `status()` 구현. `--help` 출력에 노출됨(E2 실측: `{import-baseline,init,research,calculate,draft,status,review-template,approve}`).
- **문서 부재**:
  - `README.md:221-229` scorecard 단계 표 7행에 없음
  - `AGENTS.md:62` "`/score-plan`, …, `/score-goal`. 실행기는 `python scripts/scorecard_cli.py <stage> <slug>`" — 8개 slash 명령 목록에 대응 없음
  - `.claude/commands/` 에 `score-status.md` 없음 (실측: score-approve·build·calculate·draft·goal·plan·research·review 8개뿐)
  - 8개 `SKILL.md` 어디에도 `status` 언급 없음 (덤프 전문 확인)
- **왜 문제인가**: `status` 는 이번 검증에서 가장 유용한 **읽기 전용** 조회였다. 선행 산출물 존재(plan·run_inputs·research·results·draft·review), `review_status`, `approval` 존재, **`approval_valid`**(`stages.py:246-248` — 승인 해시가 현재 입력과 같은지 읽기 전용으로 판정), `pending_rule_decisions`, `scored`, `incomplete` 를 한 번에 준다. `score-build/SKILL.md:11` 의 "`awaiting_user` 메시지가 나오면 승인이 없거나 무효다" 를 **빌드 실패 전에** 미리 확인할 수 있는 유일한 비파괴 수단인데 문서화돼 있지 않다.
- **최소 수정안**: `README.md` scorecard 표에 행 추가 — "| 상태 조회 | `python scripts/scorecard_cli.py status <slug>` | (읽기 전용, 산출물 없음) 단계 충족·review 상태·승인 유효성·미결 결정·미완료 기업 |". `score-build/SKILL.md` 1번 앞에 "먼저 `status <slug>` 로 `approval_valid` 를 확인한다" 한 줄. `/score-status` 명령 추가는 선택.
- **판정 방식**: **실제 실행**(E2, E4) + 문서 정적 확인

---

### D-10 · low — history.csv 의 "변동 원인"(`change_type`) 열을 설정할 수단이 없어 항상 `baseline-recompute`

- **실제 코드 위치**:
  - `scripts/scorecard/render_html.py:604` `rows = history_rows(results, approval, ctx.rules.hash, str(ctx.run.get("change_type") or "baseline-recompute"))`
  - `scripts/scorecard/render_csv.py:12` history.csv 열 목록에 `"change_type"` 포함, `:16` 인자, `:34` 기록
  - 그러나 `stages.py:65-84` `init_run` 이 만드는 run.json 에 `change_type` 키가 **없고**, `scorecard_cli.py` 의 어느 서브커맨드에도 `--change-type` 옵션이 **없으며**, `structure.md:36` run.json 필수 필드 목록에도 **없다**.
- **문서 위치**: `docs/scorecard/structure.md:27` (§2 파일 소유권 표) "| `scorecard/history.csv` | 빌드 | git | 승인본 이력 (run_id, approval_id, 기업, F1~F9, 합계, 순위, **변동 원인**) |"
- **영향**: "변동 원인" 열이 모든 행에서 같은 상수값이라 이력의 목적(왜 점수가 바뀌었는가)을 수행하지 못한다. 사용자가 run.json 에 수동으로 `change_type` 을 추가할 수 있는지도 불확실하다 — `schema.py:134-135` 의 `_expect_keys` 는 **미등록 키를 거부**하므로, run.json 스키마가 `change_type` 을 optional 로 허용하지 않으면 수동 추가조차 `SchemaError` 가 된다. (**미확인** — §6-4)
- **재현**: `build`·`init` 미실행(금지). 정적 확인만.
- **최소 수정안**: (a) `init` 에 `--change-type` 옵션 추가 + run.json 스키마 optional 키 등록 + `structure.md:36` 필드 목록에 추가, 또는 (b) `structure.md:27` 의 "변동 원인" 을 빼고 "`change_type` 은 현재 `baseline-recompute` 고정" 으로 정정.
- **판정 방식**: 정적 확인

---

### D-11 · low — `AGENTS.md` 의 `## Review 계약` 제목이 `ㅁ` 한 글자로 손상돼 있다

- **문서 위치**: `AGENTS.md:46` — `ㅁ` 단독 행.
- **실측 (heading grep)**: `AGENTS.md` 의 `##` 제목은 3 `## 목적`, 7 `## 명령과 기본 순서`, 13 `## Plan 계약`, 19 `## Research 계약`, 27 `## Draft 계약`, 36 `## Image 계약`, **51 `## Build 계약`**, 59 `## AI Scorecard 계약`, 72 `## 금지·주의`, 80 `## 주요 산출물과 참조 문서`, 84 `## Memory System` — **`## Review 계약` 이 없다.** 46행의 `ㅁ` 바로 뒤 47~49행이 리뷰 frontmatter(`status: pass | needs_fix | blocked`, `review_type: separate-session-4way` 등)·검증기 실행·needs_fix 처리 bullet 이다.
- **대조**: `README.md:114` 은 `### Review` 제목 아래 같은 내용을 정상적으로 가진다. 즉 내용은 있고 제목만 손상됐다.
- **판정**: scorecard CLI 와 무관한 기존 stock 문서 결함이다. 문체 취향이 아니라 **제목 손상**이라 목차·앵커·`grep '^## '` 기반 자동 파싱이 Review 계약 절을 찾지 못한다. 에이전트 지침 파일에서 절 하나가 목록에 안 보이는 실질 효과가 있다.
- **미확인**: 언제 섞여 들어갔는지 blame 하지 않았다(§6-6).
- **최소 수정안**: `AGENTS.md:46` 의 `ㅁ` → `## Review 계약`
- **판정 방식**: 정적 확인 (heading grep + README 대조)

---

### D-12 · low — plan 이 없을 때 `report_type` 이 `stock_report` 로 폴백해 scorecard slug 오타가 stock 진단을 받는다

- **실제 코드 위치**: `scripts/report_contract_lib.py:194-202` `report_type_for()` — 독스트링 "plan 이 없거나 키가 없으면 stock_report. 알 수 없는 값은 ValueError."
- **재현 명령·출력 (실제 실행 E5)**:
  ```
  $ python -B -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-09-typo
  [FAIL] report contract: ai-scorecard-2026-09-typo
    error - 필수 파일 없음: plan\ai-scorecard-2026-09-typo.md
    error - 필수 파일 없음: research\ai-scorecard-2026-09-typo.md
    error - 필수 파일 없음: drafts\ai-scorecard-2026-09-typo.md
    error - 필수 파일 없음: reviews\ai-scorecard-2026-09-typo.md
  ```
  → scorecard 분기(`validate_report_contract.py:408-411`)가 아니라 **stock 분기**(`:413-424` 의 4필수 마크다운 로드)를 탄다.
- **대조**: `stages.py:52-53` `init_run` 은 "scorecard slug 는 `ai-scorecard-` 로 시작해야 한다 (예: ai-scorecard-2026-09-baseline)" 며 접두를 **강제**한다. 즉 접두는 scorecard 의 신뢰 가능한 신호인데, 검증기는 그 신호를 진단에 쓰지 않는다.
- **판정**: 폴백 자체는 `structure.md:10` (§1) "plan frontmatter `report_type` 없음 → stock_report" 로 **문서화된 설계 선택**이다. 버그가 아니라 **진단 품질** 문제 — `ai-scorecard-` 접두 slug 에 plan 이 없으면 "`scorecard_cli.py init` 으로 plan 을 먼저 생성" 힌트가 없어, 사용자가 stock 파이프라인 산출물(hero 이미지·price-chart)을 만들어야 한다고 오해할 수 있다.
- **최소 수정안**: `validate_contract` 진입부(`validate_report_contract.py:402-411`)에서 `slug.startswith("ai-scorecard-") and not paths.plan.is_file()` 이면 error 문구에 힌트를 덧붙인다. 또는 `report_type_for` 가 접두와 frontmatter 가 모순일 때 ValueError.
- **판정 방식**: **실제 실행**(E5)

---

### D-13 · low — README·AGENTS 의 미결 결정 목록이 blocking 5개만 나열해, 선택 가능한 결정이 5개뿐인 것처럼 읽힌다

- **실측 (E10, `rules/v1.5.json`)**: 결정 22개(C-01~C-22).
  - `status=pending & blocking=true` → **C-03, C-05, C-06, C-13, C-16** (5개)
  - `status=pending & blocking=false` → **C-04, C-07, C-08, C-09, C-11, C-12, C-20** (7개)
  - `status=documented` → C-01, C-10, C-14, C-15, C-17, C-18, C-19, C-21, C-22 (9개)
  - `status=resolved` → C-02 (1개)
- **문서**:
  - `README.md:233` "미결 규칙 결정(C-03/05/06/13/16)은 `run.json.decisions` 로만 적용하고, 결정 전 기업은 순위에서 제외됩니다."
  - `AGENTS.md:66` "미결 규칙 결정(C-03, C-05, C-06, C-13, C-16)은 `run.json.decisions` 로만 실행 단위에서 선택한다."
  - → 두 문서의 5개 목록은 **blocking 5개와 정확히 일치한다 (통과)**.
  - 단 `structure.md:59-69` (§4) 의 "계산기 동작" 표는 C-03, **C-04**, C-05, C-06, C-13, C-16, **C-20** 7개를 서술한다. C-04·C-20 도 `run.json.decisions` 로 선택 가능하지만(blocking=false) README·AGENTS 목록에는 없다.
- **판정**: README·AGENTS 가 **틀린 것은 아니다** — "결정 전 기업은 순위에서 제외"되는 것은 blocking 5개뿐이다. 다만 "미결 규칙 결정 = 저 5개"로 읽혀, C-04(G3 완충 include_v15)·C-20(Anthropic TTM 부호) 같은 non-blocking 미결도 실행 단위 결정으로 해소할 수 있다는 정보가 빠진다. `structure.md` §4 가 가장 정확하다.
- **최소 수정안**: `README.md:233`·`AGENTS.md:66` 에 괄호 추가 — "(순위 제외를 일으키는 blocking 미결 5개. C-04·C-20 등 blocking=false 미결도 `run.json.decisions` 로 선택 가능하며 `docs/scorecard/structure.md` §4 참조)".
- **판정 방식**: **실제 실행**(E10) + 문서 정적 대조

## 4. 문제 요약표

| ID | 심각도 | 문서 위치 | 실제 코드 위치 | 한 줄 | 판정 방식 |
|---|---|---|---|---|---|
| D-01 | high | 생성 plan `## 완료/차단 조건` (`render_md.py:149`, 실물 `plan/ai-scorecard-2026-09-baseline.md:112`) | `render_html.py:590,593` / `validate.py:195,202` | 자료 부족·규칙 미결을 `awaiting_user` 차단으로 서술하나 실제로는 순위 제외일 뿐 | 실행 + 정적 |
| D-02 | high | `score-approve/SKILL.md:8,14` · `score-approve.md:2,11` · `AGENTS.md:68` · `README.md:228` | `scorecard_cli.py:169` / `schema.py:406-413` / `render_html.py:567` | `--by` 값 미검증 → 빈 값·공백·None·숫자 승인 성립, HTML footer 에 노출 | 실행 |
| D-03 | medium | `scorecard_cli.py:5` · `score-plan/SKILL.md:17` · `README.md:223` | `scorecard_cli.py:143-148` / `stages.py:71-72,80` / `render_md.py:95,116` | `--price-as-of`·`--info-cutoff`(외 3개) 미문서화 → C-17 분리가 문서화된 경로로 불가, plan 은 "분리 기록" 주장 | 실행 + 정적 |
| D-04 | medium | `README.md:234` · `AGENTS.md:70` · `structure.md:107` (+ §3 표 40-55) | `tests/test_scorecard_calc.py` | T-01~T-12 커버리지 주장하나 `test_t08*` 없음. §3 매핑 표에도 T-08 행 없음 | 정적(grep) |
| D-05 | medium | `structure.md:108` (T-13 추적 라벨) | `validate_report_contract.py:104-105,456-463` / `scorecard/validate.py:73,88,129,186` | 실패한 검사에도 `ok -` 줄 출력 | 실행 + 정적 |
| D-06 | medium | `structure.md:101` | `package.json:8,9,10,11,12,13,14` · `README.md` stock 절 · `AGENTS.md` stock 절 | "python3 를 가정하지 않는다" vs npm 스크립트 4개가 python3 요구, 같은 파일 안에서 혼용 | 실행 + 정적 |
| D-07 | low | `.claude/commands/score-approve.md:3` | `scorecard_cli.py:169` | `argument-hint` 의 `[--by 이름]` 이 필수 인자를 선택처럼 표시 | 실행 |
| D-08 | low | `README.md:232` | `baseline_import.py:11-13` | `import-baseline` 기본 경로가 `E:/sourcecode/...` 머신 고유 절대경로, 미공지 | 정적 |
| D-09 | low | `README.md:221-229` · `AGENTS.md:62` · `.claude/commands/` | `scorecard_cli.py:113-117,157-160` / `stages.py:229-253` | `status`(유일한 비파괴 상태·승인유효성 조회) 미문서화, `/score-status` 없음 | 실행 + 정적 |
| D-10 | low | `structure.md:27` | `render_html.py:604` / `render_csv.py:12,34` | history.csv "변동 원인" 열을 설정할 수단 없음 → 항상 `baseline-recompute` | 정적 |
| D-11 | low | `AGENTS.md:46` | (문서 결함) | `## Review 계약` 제목이 `ㅁ` 으로 손상 | 정적 |
| D-12 | low | `structure.md:10` (폴백은 문서화됨) | `report_contract_lib.py:194-202` | plan 부재 시 stock_report 폴백 → scorecard slug 오타가 stock 진단, `ai-scorecard-` 접두 힌트 없음 | 실행 |
| D-13 | low | `README.md:233` · `AGENTS.md:66` vs `structure.md:59-69` | `rules/v1.5.json` decisions 22개 | 미결 목록이 blocking 5개만 → non-blocking 7개(C-04·C-20 등)도 결정 가능함이 빠짐 | 실행 + 정적 |

## 5. 경미 — 버그로 보고하지 않는 항목

지시("일반적 문체 취향은 버그로 보고하지 말 것")에 따라 결함으로 분류하지 않은 관찰:

1. `--help` 의 서브커맨드 나열 순서 `{import-baseline,init,research,calculate,draft,status,review-template,approve}` 가 독스트링 usage 순서(status 가 마지막)와 다르다. argparse 가 등록 순서대로 출력하는데 `status` 는 `scorecard_cli.py:157` 의 루프에서 `research/calculate/draft` 와 함께 등록돼 먼저 나온다. 기능 영향 없음.
2. `score-research/SKILL.md:16` 이 판단 kind 6종 중 4종(criteria/grade/matrix/gate_inputs)만 예시로 들고 F1/F4/F8 의 `score`, F2 의 `paths` 는 생략한다. `AGENTS.md:65` 와 `structure.md:35` 가 보완하므로 모순이 아니고 오동작 유도도 없다.
3. `README.md` 도입부(`:1-17`)가 stock 파이프라인만 설명하고 scorecard 는 `:209` 부터 별도 절이다. 두 파이프라인이 `plan/ research/ drafts/ reviews/ output/` 을 공유하지만 `report_type` 으로 분기한다는 사실은 `structure.md:10`·`AGENTS.md:60`·`README.md:231` 에 명시돼 있다. 구성 선택.
4. `validate.py` 가 오류 메시지에서 `prel()`(frontmatter 비교용, POSIX 정규화)과 `rel()`(단순 표시용)을 섞어 써서 표시 경로가 백슬래시로 나온다(E5·E6 출력의 `plan\ai-scorecard-…md`). Windows 에서 정상이며 비교 로직은 `prel()` 로 정확하다(E6 에서 source·hash 검사 전부 ok).
5. `stages.py:207` approve 가 `require_price_chart=False, check_price_chart_if_present=False` 를 넘기지만 ai_scorecard 분기(`validate_report_contract.py:408-411`)는 두 인자를 받지 않는다. 무해한 방어적 인자.
6. `.claude/skills/score-*/agents/openai.yaml` 8개는 `interface.display_name`·`short_description` 만 있는 3줄 파일이다(실측: score-plan → "Score Plan" / "Help with Score Plan tasks"). SKILL.md 의 description 과 중복되지 않는 자동 생성 문구로 보인다.
7. `/stock-*` 명령을 scorecard slug 에 쓰거나 그 반대의 경우: `build_report.py:392-396` 과 `validate_report_contract.py:402-411` 이 **plan 의 report_type 으로 분기**하므로 어느 쪽 명령을 쓰든 실제 실행기는 slug 의 유형을 따른다. 즉 잘못된 조합이 조용히 잘못된 산출물을 내지 않는다(scorecard slug 에 stock 빌더 → 승인 요구에서 정지, stock slug 에 scorecard 빌더 → hero 이미지 부재로 실패). 혼선 위험은 D-12 의 plan 부재 경우로 제한된다.
8. `AGENTS.md:7-11` "명령과 기본 순서"가 `/stock-*` 6개만 나열하고 `/score-*` 는 `:62` 의 전용 절에 둔다. 전용 절이 존재하므로 결함으로 보지 않는다.

## 6. 미확인

1. **`npm test`·`npm run check` 를 실행하지 않았다** (금지 목록 + `package.json:8` 의 `python3 -m compileall -q scripts` 가 `worker/scripts` 에 `__pycache__` 를 써서 읽기 전용 제약에 어긋남). 따라서 D-06 의 "python3 별칭 없는 Windows 에서 npm test 실패"는 **정적 추론**이며, 이 머신에서는 `python3` 가 존재해(E8) 실패하지 않는다. 실제 테스트 통과 여부(T-01~T-12, R01~R06)도 미확인 — D-04 는 테스트 **이름의 존재 여부**만 grep 으로 확인한 것이다.
2. **금지된 8개 서브커맨드(import-baseline·init·research·calculate·draft·review-template·approve·build)의 실제 출력 문자열을 보지 못했다.** 이들의 메시지·반환값은 `scorecard_cli.py`·`stages.py`·`render_html.py`·`render_md.py` 의 리터럴을 읽어 확인한 **정적 추론**이다. D-01·D-03 의 plan 문구는 예외적으로 **이미 커밋된 실물** `plan/ai-scorecard-2026-09-baseline.md`(48·112행) 에서 직접 확인했다.
3. **`scorecard/history.csv` 의 실제 내용을 보지 못했다.** 인벤토리 실측 결과 `scorecard/history.csv` 는 저장소에 **존재하지 않는다**(build 미실행 상태와 일치 — `status` 의 `html: false`, `approval: false`). D-10 은 `render_csv.py` 의 열 정의와 `render_html.py:604` 의 호출부로만 판단했다.
4. **`change_type` 을 run.json 에 수동 추가했을 때 `schema.py` 가 허용하는지** 확인하지 않았다. `_expect_keys`(`schema.py:134-135`)가 미등록 키를 거부하는 것은 확인했으나, run.json 검증 함수가 `change_type` 을 optional 로 등록했는지는 읽지 않았고 `init` 을 실행해 확인하지도 않았다. D-10 의 "수동 추가도 불가할 수 있다"는 조건부 추정이다.
5. **`structure.md:3-4` 가 선언한 "기준 커밋 `0df7d6e`, 브랜치 `HANSOLJJ/worker`"의 의도**를 확정하지 않았다. 실측(E1, E9): `0df7d6e` = `origin/main` = `HANSOLJJ/scarpper` HEAD 이며, 그 커밋에는 `scripts/scorecard_cli.py` 도 `docs/scorecard/structure.md` 도 **없다**(`git cat-file -e` 가 둘 다 `exists on disk, but not in '0df7d6e'`). 커밋 사슬은 `0df7d6e` → `a826cf0`(structure.md·design-guideline.md 추가) → `6bddc22`(계산 framework·테스트) → `0e6e6a8`(기준선 이관·첫 실행) → `167640e`(단계 CLI·렌더러·검증기·분기) → `ea1ecf0`(HEAD, `/score-*` 명령·스킬). 즉 `0df7d6e` 는 **브랜치 분기점**으로 읽으면 자연스럽고 그 경우 결함이 아니다. 다만 structure.md 는 `a826cf0` 시점에 이미 §7(`:100`) 에서 `ea1ecf0` 에 추가된 `/score-*` 명령 8개를 나열하고 있어, 문서는 구현보다 먼저 쓰였다. HEAD 기준으로는 내용이 정확하므로 결함으로 분류하지 않는다.
6. **`AGENTS.md:46` 의 `ㅁ` 이 언제 섞였는지** `git log -L`·`git blame` 으로 추적하지 않았다 (D-11).
7. **체크리스트 Q01~Q23 의 내용**이 `design-guideline.md` 의 Q 정의와 일치하는지는 대조하지 않았다. 이번 범위는 명령·옵션·차단 조건의 정합성이므로 `rules/v1.5.json` 의 **개수(23)·ID 연속성(Q01~Q23, 중복·결번 없음)** 만 확인했다(E10).
8. **`render_html.py` 의 대시보드 접근성 요구**(320px 리플로우, 탭 대상 ≥24px, sticky 첫 열, Pretendard, 산점도 라벨 배치)는 `structure.md:83` 이 "Playwright 실측(2026-09-08): 320/768/769/1280 넘침 0건, 탭 대상 위반 0건" 이라고 주장하나, 이번 범위에서 재실측하지 않았다. `score-build/SKILL.md:14` 의 "가능하면 Playwright 로 … 실측한다"와 문서는 일치한다.
9. **`structure.md:56` (§3) 이 참조하는 `validation/test_scorecard_review.py`**(R01~R06, 10건)는 worker 가 아니라 **설계진행 worktree** 에 있다(실측: `설계진행/validation/` 에 `test_scorecard_review.py`, `qwen-recheck.md`, `qwen-recheck-evidence.json`, `recheck_qwen.py`, `scorecard-review.md` 존재). worker-only checkout 에서는 이 상대경로가 해석되지 않는다. 문서가 어느 worktree 기준인지 밝히지 않으나, "설계진행 검증 담당의 독립 재현"이라고 주체를 명시하고 있어 결함으로 분류하지 않았다. 실행하지 않았다.

## 7. 산출물과 재현

모두 `scarpper/validation/qwen-cli-doc-02/` 에 있다. worker 에는 아무것도 쓰지 않았다.

| 파일 | 역할 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `inventory.py` → `inv-start.txt`, `hashes-start.json` / `inv-end.txt`, `hashes-end.json` | 검토 대상 인벤토리 + 시작·종료 해시·HEAD·git status (§8) |
| `dump.py` → `dump-commands.txt`, `dump-skills.txt` | `.claude/commands/score-*.md` 8개·`.claude/skills/score-*/SKILL.md` 8개·`package.json` 행번호 덤프 (인용 행 번호의 근거) |
| `inspect_rules.py` → `rules-dump.txt` | `rules/v1.5.json` 체크리스트 23개·결정 22개 상태/blocking·factor 모드 (D-13, §2-8·2-24 근거) |
| `isolated_approve_test.py` → `approve-test.txt` | **격리 실험** — `--by ""` argparse 통과 + `validate_approval` 의 빈 승인자 허용 (D-02, D-07 근거). worker 파일 쓰기 없음 |

재현 순서:

```powershell
cd C:\Users\noble\orca\workspaces\stock-report-harness\scarpper\validation\qwen-cli-doc-02
python -B -X utf8 inventory.py start        # -> hashes-start.json, inv-start.txt
python -B -X utf8 dump.py ".claude/commands/score-*.md" "package.json" > dump-commands.txt
python -B -X utf8 dump.py ".claude/skills/score-*/SKILL.md" > dump-skills.txt
python -B -X utf8 inspect_rules.py          > rules-dump.txt
python -B -X utf8 isolated_approve_test.py  > approve-test.txt

cd C:\Users\noble\orca\workspaces\stock-report-harness\worker
python -B -X utf8 scripts/scorecard_cli.py --help
python -B -X utf8 scripts/scorecard_cli.py init --help      # D-03
python -B -X utf8 scripts/scorecard_cli.py approve --help   # D-07
python -B -X utf8 scripts/scorecard_cli.py status ai-scorecard-2026-09-baseline        # D-01, D-09
python -B -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-09-typo        # D-12
python -B -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-09-baseline    # D-05
git cat-file -e 0df7d6e:scripts/scorecard_cli.py                                       # §6-5
```

한글이 콘솔에서 깨져 보이면 cmd 코드페이지 문제일 뿐 파일은 UTF-8 로 정상이다. `-X utf8` 을 붙이고 `> file 2>&1` 로 담아 읽는 방식을 썼다. `python3`·`python` 둘 다 `D:\python3121` 에 있다(E8).

## 8. 시작·종료 무결성

`inventory.py start` / `inventory.py end` 로 74개 파일의 SHA-256·크기·줄 수와 worker HEAD·`git status --porcelain` 을 각각 기록했다. 결과는 §8.1 표와 `hashes-start.json`·`hashes-end.json` 참조.

- 시작 HEAD: `ea1ecf095c66cb92a563c4ee785a2f5ae0e67143`
- 시작 `git status --porcelain`: `?? package-lock.json`, `?? research/ai-scorecard-2026-09-baseline.md`, `?? reviews/ai-scorecard-2026-09-baseline.md` (3건, 전부 검증 이전부터 존재)
- scarpper 쪽 `git status --porcelain`: `?? package-lock.json`(기존), `?? validation/`(QWEN-BASELINE-01 + 이번 산출물) 뿐 — worker·원본에 쓰기 없음.

### 8.1 종료 비교 결과 (실제 실행)

```
HEAD start ea1ecf095c66 end ea1ecf095c66 SAME
status same: True ['?? package-lock.json', '?? research/ai-scorecard-2026-09-baseline.md',
                   '?? reviews/ai-scorecard-2026-09-baseline.md']
files 74 74
CHANGED FILES: NONE
added: NONE removed: NONE
```

**worker 의 74개 검토 대상 파일 전부 SHA-256 동일, HEAD 동일, git status 동일, 추가·삭제 없음.** 검증 중에 대상이 바뀌지 않았으므로 §3 의 문제 중 재확인이 필요한 항목은 없다. `python -B` 를 사용해 `__pycache__` 도 생성하지 않았다(added: NONE 가 이를 뒷받침).


## 9. 범위 준수 확인

- worker 는 읽기 전용으로만 접근. 수정·커밋·재생성·checkout·merge 없음.
- 금지된 8개 서브커맨드와 `npm test` 미실행. `npm run check` 도 `__pycache__` 쓰기 때문에 미실행.
- 실행한 것은 `--help` 9회, 읽기 전용 조회 `status` 1회·`validate_report_contract.py` 2회, git 조회, grep, 그리고 worker 밖에 격리한 argparse/schema 실험 1회. 전부 `-B` 로 바이트코드 생성 차단.
- 네트워크 조사·설치·새 에이전트 생성 없음.
- 자신의 scarpper checkout 을 구현 기준으로 사용하지 않았다 — 모든 코드 인용은 `worker/` 경로에서 했다.
- QWEN-BASELINE-01 의 데이터 재검증을 반복하지 않았고, `qwen-recheck.md` 에서 기각된 P4·P5·P9·P10 을 재논쟁하지 않았다. P10 의 문서 보완(`parse_failed` 가 `structure.md:34` 에 등록)이 반영된 것만 사실로 기록했다.
- `worker_done` 등 lifecycle 메시지 미발송 (Task/Dispatch preamble 없는 기존 세션 작업 전달).
- 입력창의 미제출 `/compress-fast` 는 자동 실행하지 않았다.
