# 규칙 문서 재편 영향 전수 조사 (muse)

- 조사: muse (Muse Code, Muse Spark) · 조사 시각: 2026-10-02 UTC · 기준 커밋: `da765c2`
- 지시서: `.agents/plans/rules-restructure-2026-10/survey-brief.md` · 프로젝트 지침: 저장소 루트 `AGENTS.md` (세션 시작 시 전문 읽음)
- 방법: 읽기 전용. `muse.search`(정규식 모드)와 `rg --count-matches`(읽기 전용 계수), `read_file`로 함수·주변부 확인. 테스트·빌드·수집·승인 명령 미실행, `git commit` 미실행, 다른 에이전트 survey 파일 미열람. 제외 폴더(`node_modules`, `.venv`, `data`, `validation/*/_raw`, `evidence/candidates.json`)는 검색 범위에서 뺌. 아래 건수는 `rg --count-matches`의 매치 수(한 줄에 2건이면 2로 셈)이며, 행 번호는 `rg -n` 기준 1-based다.
- 핵심 결론: 별표 체계 폐기+행 번호 전면 변경 시 **반드시 고쳐야 하는 곳은 코드·테스트·스킬·승인 페이지의 현행 규칙 용어 출력 20여 건과 v1.5.md 실측 행을 단언하는 테스트 2건**이다. 승인된 실행 묶음·기준선·구규칙 JSON 안의 참조는 얼리므로 손대지 않는다.

## Q1. 코드와 테스트의 별표 참조 (전수, `scripts/`+`server/`+`tests/` = 64매치)

### 코드 36매치

- `scripts/scorecard/baseline_import.py` — 8매치.
  - 28행 `# 규칙 v1.5 ⑨ 게이트 3·4 적용표(별표)에서 읽은 B종 약정…` (다) 주석, **고치면 안 됨** (v1.5 원문에서 읽었다는 과거 사실 기록).
  - 71행 `# ⑤ 별표 G 판정표 — (A, H)`, 77행 `# ⑦ 별표 I 판정표 — …` (다) 주석, **고치면 안 됨** (이관 출처 표기).
  - 438행 `note="별표 J 교차검증 전용 — 점수 입력 아님"` (가) 출력 문구이나 v1.5 기준선 이관용 고정 문장, **고치면 안 됨** (v1.5 문서가 얼어 참조가 계속 유효).
  - 533행 `note "규칙 v1.5 별표 G 판정표"`, 538행 `note "규칙 v1.5 별표 I 판정표"` (가) 출력 문구이나 v1.5 판정표 지목, **고치면 안 됨** (같은 이유).
  - 587행 `"…규칙 v1.5 판정표(③ 사다리, 별표 G, 별표 I)를 승계…"` (가) 출력 문구이나 과거 승계 기록, **고치면 안 됨**.
- `scripts/scorecard/calc_f9.py` — 2매치.
  - 136행 주석 `(채점규칙 별표 D 388~390행 …)`, 152행 경고 문자열 `"(별표 D 388~390행)"` (다)/(가). **고치면 안 됨**. v1.5 내부 충돌(470행 대 별표 D)을 설명하는 역사적 인용이며 v1.5.md는 얼어 행 번호가 유지된다.
- `scripts/scorecard/calc_qual.py` — 2매치.
  - 142행 `pending "동맹 A 등급·적대 H 등급 입력 필요(별표 G)"`, 155행 `pending "…판정 필요(별표 I)"` (나) 판정 로직이 내는 사용자 안내 문구. **필수 수정**. 판단이 없을 때 사람에게 보이는 현행 규칙 용어라 새 절 이름으로 바꿔야 한다.
- `scripts/scorecard/render_common.py` — 5매치.
  - 319행 `INTERNAL_REF_RE` 정규식 `별표 [A-Z]` (나) 본문 내부참조 탐지. **선택 수정**. 승계 문구의 옛 참조를 걷어내는 데 여전히 필요하고, 새 절 표기 탐지는 추가 여부를 정해야 한다.
  - 982행 `CREDIT_NOTE = "…(별표 J)."` (가) 리포트·초안에 출력되는 문구. **필수 수정**.
  - 1220행·1230행 주석 `출처 표기(별표 A)는 남긴다`, 1292행 주석 `기준은 별표 원문에서 가져오고` (다) 방침 주석. **선택 수정** (동작 불변, 방침 서술만 어긋남).
- `scripts/scorecard/render_html.py` — 3매치.
  - 1015행·1023행 주석 `본문은 별표 원문을 쓰고…` (다) 방침 주석, **선택 수정**.
  - 1122행 `'채점규칙 별표의 지표다.'` (가) 방법 카드에 출력되는 문자열. **필수 수정**.
- `scripts/scorecard/stages.py` — 3매치.
  - 90행 `conflict_of_interest "…채점규칙 384행 이해상충 고지…"` (가) 새 실행의 `sources.json`에 들어가는 문구이나 v1.5 원문 지목, **고치면 안 됨**.
  - 577행 주석 `⑤ 판정표(별표 G)가 적은 것만 쓴다…` (다) 과거 판정 경위, **고치면 안 됨**.
- `server/approvals.js` — 13매치.
  - 37행 주석 (다), **선택 수정**.
  - 41~50행 `GLOSSARY`의 `term: '별표 A'~'별표 J'` 10건 (가) 승인 페이지 참조표 출력. **필수 수정** (아래 Q5 경로로 승인된 실행의 옛 문구와 함께 보임).
  - 62행 주석·63행 `TERM_RE`의 `별표\s*([A-J])` (나) 용어 링크 로직. **선택 수정**. 옛 문구 링크에는 여전히 필요하고, 새 용어 탐지 추가가 선택이다. 파일 39행 `RULES_DOC` 경로 상수는 Q6에 정리.

### 테스트 28매치

- `tests/fixtures/evidence/labeling-2026-10.csv` 5행·11행·18행·21행·22행, `labeling-2026-10.json` 62행·158행·270행·318행·334행, `tests/fixtures/evidence/README.md` 18행 (라) 과거 라벨링 표본과 그 설명. **고치면 안 됨** (2026-10-01 표본 기록).
- `tests/node/approvals.test.js` 151행·155행 (라) 용어 링크·참조표 단언. **필수 수정** (`GLOSSARY`를 고치면 함께 고쳐야 함).
- `tests/node/fixtures/summary.sample.json` 76행·252행 (라) 링크 대상 표본 문장. **고치면 안 됨** (옛 문구 링크 동작을 계속 보장하는 fixture).
- `tests/test_scorecard_f5_impl48.py` 6행·7행(독스트링의 계약 선언) (라). **고치면 안 됨** (재판정 당시 계약 기록).
- `tests/test_scorecard_fix52_citations.py` 4행(독스트링)·31행(정규식 `별표 [A-J]`) (라)/(나). 31행 정규식은 동결된 obsreg 판단을 검사하는 검증 조건이라 **고치면 안 됨**. 단 새 용어로 쓴 미래 판단은 이 검사에 걸리지 않는 공백이 생긴다(Q7).
- `tests/test_scorecard_fix59.py` 77행, `tests/test_scorecard_fix62.py` 95행·137행, `tests/test_scorecard_fix76.py` 27행(주석)·108행·109행·110행, `tests/test_scorecard_impl50.py` 6행(독스트링)·46행 (라). fix76 108~110행은 **살아 있는** `factor-concepts.json` 값을 단언하므로 개념 파일을 고치면 **필수 수정**. 나머지는 동결 입력(v1.7.json·obsreg 묶음) 단언이라 **고치면 안 됨**.

## Q2. 별표 이름이 동작을 바꾸는 곳

별표 이름을 키·조건으로 쓰는 판정·검증 로직은 **없다**. 점수 계산(`calc_qual.py` 143~144행 `A`·`H` 정수, `rules.f5_formula`, `f7_matrix`)은 별표 문자열을 읽지 않는다. 별표가 동작에 닿는 자리는 표시용 탐지 4건뿐이다.

- `scripts/scorecard/render_common.py` 317~321행 `INTERNAL_REF_RE`: `별표 [A-Z]`+숫자+`행` 패턴을 본문에서 걷어낸다. 이름을 바꾸면 옛 승계 문구의 정리는 그대로 되고, 새 절 표기는 걷어내지 않는다(표시 차이만, 점수 무영향).
- `server/approvals.js` 63행 `TERM_RE` + 66~80행 `linkTerms`: `별표\s*([A-J])`를 잡아 `star-A`~`star-J` 용어집으로 연결한다. 이름을 바꾸면 옛 문구는 링크가 안 붙고(조용히 텍스트 유지), `GLOSSARY`의 한글 설명은 옛 정의라 함께 고쳐야 한다. 크래시는 없다.
- `tests/test_scorecard_fix52_citations.py` 31행: 판단문에 `별표 [A-J]`가 있으면 `SRC-v15-rule` 인용을 강제한다. 새 용어 문장에는 이 검사가 걸리지 않는다(검증 공백, Q7).
- `scripts/scorecard/schema.py`·`validate.py`·`rules.py`에는 `별표` 문자열 분기가 없다(확인 검색어로 `별표` 전수 조회, 해당 파일 0건).

## Q3. 규칙 문서의 행 번호 참조 (전수)

행 번호는 전부 **v1.5 판**(`AI기업_채점규칙_v1.5.md`, `AI기업_채점표_v1.5.md`, `AI기업_채점표_HANDOVER.md`)을 가리킨다. 근거: 실측 대조로 `384행 이해상충 고지`·`별표 D 388~390행`이 v1.5 실물과 일치함을 확인했고(`docs/scorecard/rules/AI기업_채점규칙_v1.5.md` 384행·388~390행 직접 열람), 같은 내용이 v1.7에서는 491행·495~497행으로 밀려 있다(직접 열람). `470·494·603행`(⑨ 적용표)도 v1.5에만 있는 배치다.

### 코드 20매치 (`server/` 0건)

- `scripts/scorecard/calc_f6_params.py` 467행 `v1.5 645~654행` 취지 인용. v1.5 명시. (다) 주석, **고치면 안 됨**.
- `scripts/scorecard/calc_f9.py` 136행(별표 D 388~390행+470·494·603행)·152행(별표 D 388~390행)·176행(470행). v1.5. (다)/(가), **고치면 안 됨** (v1.5 내부 충돌의 역사적 인용).
- `scripts/scorecard/render_common.py` 270행(채점규칙 22행)·516행(HANDOVER 120행)·732행(채점규칙 22행)·1600행(채점규칙 384행)·1617행(HANDOVER 120행). v1.5/HANDOVER. 주석·문자열, **고치면 안 됨**.
- `scripts/scorecard/render_html.py` 336행(주석의 `14행`)은 v1.5와 무관한 CSS 메모. 분류 외, 무시.
- `scripts/scorecard/render_md.py` 359행 `채점규칙 384행 · HANDOVER 75행`(v1.5). (가) 초안 이해상충 고지 문구이나 v1.5 지목, **고치면 안 됨**.
- `scripts/scorecard/schema.py` 1196행 `design-guideline 272행`(C-14 근거). 현행 설계 문서 지목. **필수 수정** (설계 문서를 재편하면 행이 어긋남).
- `scripts/scorecard/stages.py` 85행·90행(채점규칙 384행) v1.5, 92행(HANDOVER 75행). (가)/(다), **고치면 안 됨**.
- `scripts/scorecard/validate.py` 54행·259행·262행 `"AGENTS.md 71행"`. **이미 어긋난 참조**. 현 루트 `AGENTS.md` 71행은 원자료 조사 규율(값이 없으면 같은 원문에서 왜 없는지 검색)이고, 승계 판단 예외는 22~23행에 있다. 옛 `AGENTS.md`(S-AGENT, 171행 시절) 기준 번호로 보인다. **필수 수정** (번호 갱신 또는 절 이름 지목으로 교체).

### 테스트 71매치 (전수)

- `tests/fixtures/README.md` 5행 `10431행`(데이터 행 수, 규칙 참조 아님). 분류 외.
- `tests/test_scorecard_c03.py` 63행(HANDOVER 22행)·85행(채점표 1100행·HANDOVER 120행)·117행·122행(채점규칙 17행). v1.5/HANDOVER/채점표 v1.5. (라) 동결·과거 문언 단언, **고치면 안 됨**.
- `tests/test_scorecard_f5_impl48.py` 8행(214·224행)·87행(727행)·88행(188~195행)·92행(262·264·266·288행)·99행(276행)·100행(759행)·105행(214행)·106행(224행). v1.5. (라) 동결 판단문 단언, **고치면 안 됨**.
- `tests/test_scorecard_fix52_citations.py` 6행(75행·384행)·76행(75행)·80행(384행). v1.5/HANDOVER. (라) 동결 sources 단언, **고치면 안 됨**.
- `tests/test_scorecard_fix53_aws_label.py` 48행(HANDOVER 51행). (라), **고치면 안 됨**.
- `tests/test_scorecard_fix53_draft.py` 38행(채점규칙 727행)·55행(채점표_v1.5.md 671·673행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix53_rules.py` 62행(398행)·67행(262행)·73행(239행)·74행(273~278행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix53_stage2.py` 43행(192·193·218·289·243행)·45행(945행)·108행(192행). v1.5/채점표 v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix53_stage3.py` 131행(916행)·155행(188·198·350행·217행). (라), **고치면 안 됨**.
- `tests/test_scorecard_fix54_tensions.py` 42행(321~322행)·43행(338행)·63행(163행)·90행(662행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix55_stage1.py` 86행(채점규칙 70행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix56_stage1.py` 154행(145행·153행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix56_stage2.py` 116행·119행(채점규칙 384행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix57_stage2.py` 71행(채점규칙 22행)·86행(HANDOVER 75행). (라), **고치면 안 됨**.
- `tests/test_scorecard_fix58_stage2.py` 192행(채점규칙 384행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix59.py` 77행(별표 D 388~390행, 살아 있는 v1.7 긴장문 단언). v1.5 지목. Q7에 정리.
- `tests/test_scorecard_fix60.py` 60행·138행(AGENTS.md 71행). 위 validate.py와 같은 어긋남. **필수 수정**.
- `tests/test_scorecard_fix62.py` 90행·92행(470·494·603행)·136행(470행)·137행(별표 D 388~390행). v1.5. (라), **고치면 안 됨**.
- `tests/test_scorecard_fix64.py` 159행(AGENTS.md 71행, 같은 어긋남 **필수 수정**)·171행(14행·28행, 리뷰 생성물 행 수. 분류 외).
- `tests/test_scorecard_fix65.py` 173행(14행, 같은 성격. 분류 외).
- `tests/test_scorecard_fix78.py` 120행(채점표 1100행·HANDOVER 120행). (라), **고치면 안 됨**.
- `tests/test_scorecard_fix80.py` 101행(채점규칙 192·193행). (라), **고치면 안 됨**. 24행 `PATTERNS`의 `\d+행`은 행 번호 탐지 정규식(메타, 동작 무영향).
- `tests/test_scorecard_impl50.py` 6행(독스트링, 별표 I 347행)·41행(351~356행·438행·319~322행)·46행·47행(347행)·61행(438행). v1.5. (라) 살아 있는 v1.7 결정문 단언. Q7에 정리.

### 규칙 JSON·개념·스킬·에이전트·문서

- `scorecard/rules/v1.7.json`·`v1.8.json` 각 206매치(전부 v1.5/HANDOVER/채점표 v1.5 지목, Q4에 정리). v1.7과 v1.8은 `rule_version`·`note`·`sources` 외 동일함이 `test_rules_v18.py` 25~34행으로 고정돼 있다.
- `scorecard/factor-concepts.json` 0건. `.agents/skills/`·`.claude/skills/`·`.claude/agents/` 0건(해당 없음, `S-HAND` 등 약칭도 없음).
- `docs/scorecard/rules/*.md` 0건(자기 행 번호 인용 없음). `docs/scorecard/design-guideline.md` 435행 2매치(별표 I 351~356행·채점규칙 438행, v1.5). **선택 수정**. `docs/scorecard/structure.md` 176행 `체크리스트 23행` 1매치(어느 판인지 판별 불가, 두 판 다 23개). **선택 수정**.

## Q4. 규칙 JSON과 공유 정의

### 별표·행 번호 참조

- `scorecard/rules/v1.8.json` 별표 45매치(5·46·122·180·434·630·1266·1401·1406·1411·1416·1426·1438·1477·1478·1524·1534·1536·1544·1619·1652·1665·1666·1667·1669·1686·2032·2038·2039·2061·2067·2086·2092·2143·2211·2234·2240·2257·2283·2306·2332·2384·2408·2457·2539·2564행 근처, `note`·`tension`·`source_text_against`·`case` 키). 행 번호 206매치(전수 줄 목록은 `rg -n "[0-9]행" scorecard/rules/v1.8.json`으로 재현, 분포는 `decisions`(C-03 17행·C-06 BEP·C-11 351~356·438행 등)와 `open_tensions`(TEN-RA6-01 470행 대 별표 D 388~390행, TEN-RC-02 398·400행, TEN-RC-03 239·273~278행 등)에 집중). 전부 v1.5/HANDOVER/채점표 v1.5 지목. v1.5.json·v1.6.json은 별표 각 14매치·행 번호 0건.
- `scorecard/factor-concepts.json` 별표 6매치(20행 별표 A·50행 별표 D·56행 별표 G·58행 별표 G·H·96행 별표 I), 행 번호 0건. F6 항목은 `stale`(71~82행)로 NTM 서술의 낡음을 이미 표시한다.

### `rule_hash` 계산과 설명 문구 변경의 영향

- `rule_hash`는 파일 바이트 해시다. `scripts/scorecard/rules.py` 20행 `self.hash = sha256_file(path)`, `scripts/scorecard/schema.py` 165~166행 `hashlib.sha256(path.read_bytes()).hexdigest()`. 따라서 `note` 한 글자만 고쳐도 해시가 바뀐다(줄끝 포함, `docs/scorecard/structure.md` 151행 경고).
- 승인 해시는 `scripts/scorecard/schema.py` 1541~1542행 필수 6키(`rules`·`observations`·`judgments`·`run`·`results`·`draft`, 선택 `sources`·`evidence`·`triggers`)이며, `scripts/scorecard/stages.py` 917~948행 `current_hashes`·`approval_mismatches`가 대조한다. 규칙 JSON을 고치면 `rules` 해시가 어긋나 승인이 무효가 되고 `build`는 `awaiting_user`로 멈춘다. `engine.load_context`(`scripts/scorecard/engine.py` 90~93행)도 `run.json rule_hash` 불일치 시 실행 자체를 거부한다.
- `ai-scorecard-2026-10-test`에 대하여: 이 워크트리 `output/ai-scorecard-2026-10-test/`에는 `approval.json`이 없다(`ls` 실측). baseline·obsreg에는 있다. 즉 이 워크트리에서 승인 전제는 성립하지 않으며, 승인된 사본이 다른 곳에 있다면 위 무효화 경로가 그대로 적용된다.

### `factor-concepts.json`의 소비처와 승인 해시

- 읽는 코드: `scripts/scorecard/render_common.py` 1247~1258행 `factor_concepts()`(경로 `scorecard/factor-concepts.json`) → `factor_concept()`·`factor_criteria()`를 거쳐 `scripts/scorecard/render_html.py` 1095~1122행 방법 카드(`무엇을 재는가`·`무엇을 보고 매기는가`+`'채점규칙 별표의 지표다.'`)로 출력된다. 읽는 테스트: `tests/test_scorecard_fix76.py` 21행 `CONCEPTS` 경로 상수 + 55~90행 본문 대조.
- 승인 해시에 들어가지 않는다(위 6키+선택 3키에 없음). 개념 파일만 고치면 승인은 유지되지만 리포트 표시가 바뀌고 fix76(특히 108~110행 별표 A·D 단언)이 실패한다.

## Q5. 고칠 수 없는 참조 (동결 묶음, 파일별 건수)

`rg --count-matches` 실측. 별표 건수 / 행 번호(`[0-9]행`) 건수 순.

- `output/ai-scorecard-2026-09-baseline/`: draft 22/0, judgments 43/0, observations 14/0, report.html 24/0, research 42/0, review 5/0, sources 2/0, run 0/0. `approval.json` 있음.
- `output/ai-scorecard-2026-09-obsreg/`: draft 40/46, judgments 83/90, observations 14/65, report.html 55/1, research 51/5, results 1/3, review 4/7, run 1/6, sources 2/6, review-parts 합계 별표 약 120·행 번호 약 400(최대 파일: `rounds/r2/validation__a2-strict-54__gemini.md` 행 177, `rounds/r3/validation__fact-sources-split__codex.md` 파일명 67). `approval.json` 있음.
- `output/ai-scorecard-2026-10-test/`: draft 45/45, judgments 87/97, observations 14/65, evidence/evidence.json 39/0, proposals 14/28, report.html 60/1, research 86/5, results 1/3, review 6/7, review-parts 4개 파일 합 37/87, triggers 9/0, run 1/1, sources 2/6. `approval.json` 없음(이 워크트리 기준).
- `scorecard/baseline/v1.5/`: import-report 2/0, observations 14/0, scores 17/0, triggers 5/0.
- `scorecard/rules/v1.5.json` 별표 14·행 0, `v1.6.json` 별표 14·행 0, `v1.7.json` 별표 45·행 206.

### 리포트·초안·승인 페이지 출력 경로 (있음)

- 리포트 HTML: 동결 판단문의 별표 문구가 `inline_html`→`strip_internal_refs`를 통과한다. 행 번호가 붙은 형태(`별표 G 214행`류)만 `INTERNAL_REF_RE`(`render_common.py` 317~321행)로 걷히고, 행 번호 없는 `별표 G`·`별표 J` 등은 그대로 출력된다. `CREDIT_NOTE`(별표 J)와 `factor_concept` 지표(별표 A·D·G·H·I)도 방법 카드에 실린다. obsreg `report.html` 별표 55건이 그 증거다.
- 초안: `render_md.py` 553행 `CREDIT_NOTE` + 판단문 그대로. baseline `draft.md` 22건이 증거다.
- 승인 페이지: `server/approvals.js` 66~80행 `linkTerms`가 동결 판단문의 `별표 [A-J]`를 `GLOSSARY`(41~50행) 참조표로 연결한다. 옛 문구는 옛 정의로 링크된다.

### `init --from-run` 승계 (그대로 넘어온다)

- `scripts/scorecard/stages.py` 111~119행 `_inputs_from_run`: 이전 실행의 관측·판단·출처를 그대로 이어받고 판단 항목에 표시를 찍지 않는다(`continued_from`에만 기록). 옛 별표 이름이 든 판단 문구는 정제 없이 다음 실행으로 넘어간다.

## Q6. 문서 파일 이름과 경로 참조

### `AI기업_채점규칙_v1.5.md`·`v1.7.md` (파일명 언급 15곳)

- (가) 코드가 실제로 읽는다: 없음. `server/approvals.js` 39행 `RULES_DOC`는 표시용 문자열(87행 안내 문구)이며 `readFile` 대상이 아니다. `stages.py` 90행 등은 제목·해시 문자열만 쓴다. 규칙 JSON 자체는 `rules.py` 12행 `RULES_DIR`에서 읽는다.
- (나) 테스트가 내용·존재를 검사한다: `tests/test_rules_v18.py` 17행(노트 접미사에 v1.7.md 경로 문자열 단언)·34행, `tests/test_scorecard_fix59.py` 25행·67~72행(V15 실물 행 내용 단언: 470·494·603·390행), `tests/test_scorecard_fix62.py` 23행·142~145행(같은 V15 실측 단언). **v1.5.md를 고치면 fix59·fix62가 실패한다.**
- (다) 문구 언급: `.claude/skills/score-collect/SKILL.md` 38행, `docs/scorecard/design-guideline.md`, `docs/scorecard/rules/AI기업_채점규칙_v1.7.md` 12행, `docs/scorecard/source/` 2개 md, `scorecard/rules/*.json`(4개), `tests/fixtures/evidence/README.md` 18행, `tests/test_scorecard_fix59.py`·`fix62.py`(위 (나) 외 주석), `server/approvals.js` 18·38행 주석. 동결 묶음의 파일명 언급은 draft·research·sou
rces·report에 실행당 2~3건(Q5 계수에 포함).

### 구현계획·HANDOVER·채점표 v1.5(.md/.html) (24개 파일 + 동결 묶음)

- (가) 코드가 실제로 읽는다: `scripts/scorecard/baseline_import.py` 12~14행(`docs/scorecard/source/AI기업_채점표_v1.5.html`·`.md` 기본 입력). 파일을 옮기면 이관기 기본값이 깨진다. `stages.py`의 `SRC_HANDOVER_SHA256`(26행)은 상수라 파일 이동과 무관.
- (나) 테스트: `tests/test_scorecard_fix53_stage3.py`(채점표 행 단언 등 Q3 목록), `tests/test_scorecard_fix76.py` 69행(외부 원본 경로, 부재 시 skip).
- (다) 문구 언급: `docs/scorecard/design-guideline.md`, `scorecard/rules/*.json`(4개), `scripts/scorecard/{render_common,render_html,render_md,stages}.py`, 위 Q3 테스트군. 동결 묶음 언급 건수(실측): obsreg `observations.json` 42, `validation__fact-sources-split__codex.md`(r3) 67, `validation__a2-strict-54__gemini.md`(r2) 36, `rule-consistency.md`(r4) 14, `openai-f9-route__gemini.md`(r8) 13, 기타 draft·research·sources·review에 실행당 1~7건.

### `design-guideline.md`·`structure.md`·`guide.md`

- 언급 파일: `.claude/agents/report-designer.md` 6·13행(판정 기준, 다), `docs/scorecard/design-guideline.md`(자기 언급), `docs/scorecard/guide.md`(Q3 검색에서 해시·승인 절차 언급, 다), `scorecard/rules/*.json`(4개, 설계 지침 행 인용 포함), `scripts/hooks/guard.py` 274행(별도 문체 지침 언급), `tests/test_hooks.py` 96행, `tests/test_scorecard_fix54_code.py` 57~58행((나) `structure.md` 실물을 읽어 단언).
- (가) 읽는 코드: `test_fix54_code.py`뿐이며, `structure.md`를 옮기면 이 테스트가 깨진다. `guard.py`는 목록 문자열만 다룬다.

### 약칭 `S-RULE`·`S-HAND`·`S-SCORE`·`S-PLAN`·`S-AGENT`

- 출현: `docs/scorecard/design-guideline.md` 34~47행(정의·해시)·115·195·223·297·322·341·349·372·389행·425~446행(C-01~C-22)·471행, `validation/` 보고서 8건(f9-decide-20, f9-decide-20b-2026-09-11, impl-50 스크립트, qwen-baseline-01 일체). `scripts/`·`server/`·`tests/`·스킬·에이전트 정의에는 0건. (다) 문구 언급이며, 약칭 자체는 파일명과 무관해 재편과 무관. 단 C-11 인용(`S-SCORE … F7로 이월`)은 별표 I 체계와 묶여 있어 design-guideline 435행과 함께 봐야 한다.

## Q7. 변경 순서와 테스트 영향

### 반드시 고쳐야 하는 위치 (파일·행·이유)

1. `scripts/scorecard/calc_qual.py` 142·155행 — 판단 부재 시 사람에게 보이는 현행 용어(별표 G·I). 새 절 이름으로 교체.
2. `scripts/scorecard/render_common.py` 982행 `CREDIT_NOTE`(별표 J) — 리포트·초안 출력 문구. 새 근거 표현으로 교체.
3. `scripts/scorecard/render_html.py` 1122행 `'채점규칙 별표의 지표다.'` — 방법 카드 출력 문자열. 교체.
4. `server/approvals.js` 41~50행 `GLOSSARY` — 승인 페이지 참조표 10개 정의. 새 체계 정의로 교체(동결 판단문의 옛 링크는 `TERM_RE` 유지로 계속 동작).
5. `tests/node/approvals.test.js` 151·155행 — 위 용어집 단언. 함께 교체.
6. `tests/test_scorecard_fix76.py` 108~110행 — 개념 파일의 별표 A·D 잔류를 단언. 개념 파일 재편 시 함께 교체.
7. `scripts/scorecard/validate.py` 54·259·262행 + `tests/test_scorecard_fix60.py` 60·138행 + `tests/test_scorecard_fix64.py` 159행 — `AGENTS.md 71행`은 이미 어긋남(현 71행은 무관 내용). 절 이름 지목으로 교체(재편과 별개로 이미 고장).
8. `scripts/scorecard/schema.py` 1196행 `design-guideline 272행` — 설계 문서 재편 시 함께 갱신.
9. `.claude/skills/score-collect/SKILL.md` 38~51행 — 선별 기준의 별표 A~J·H·C·G·D 지침과 v1.7.md 경로. 새 문서·새 절로 교체(동작은 사람+프롬프트 층이라 깨지지 않으나 지침이 옛 체계라 필수).
10. `scorecard/factor-concepts.json` 20·50·56·58·96행 — 별표 문구 6건. 새 체계 문구로 교체(승인 해시 밖이라 승인 유지, fix76과 함께).
11. `scorecard/rules/v1.8.json`(→ 신규 버전) — 별표 45·행 206매치의 `note`·`tension`·`source_text_against`는 v1.5 역사 인용이라 **내용은 유지**하되, 해시가 바뀌므로 버전 상향+재승인 절차가 필요. `note` 서두의 v1.7.md 참조도 새 문서명으로 갱신.

### 규칙 문서를 고치면 실패할 테스트

- **직접 실패**: `tests/test_scorecard_fix59.py` 67~72행(V15 실물의 470·494·603·390행 문장 단언), `tests/test_scorecard_fix62.py` 142~145행(470·390행 문장 단언). v1.5.md 행이 바뀌면 실패. `if V15.is_file()` 가드라 파일 삭제 시에는 조용히 통과(검사 상실).
- **개념·용어집을 고치면 실패**: `tests/test_scorecard_fix76.py` 107~113행, `tests/node/approvals.test.js` 151~155행.
- **규칙 JSON을 고치면 실패**(행 재편이 JSON 문구까지 닿을 때): `tests/test_scorecard_impl50.py` 39~48행(C-11 문구), `tests/test_scorecard_fix59.py` 74~83행(TEN-RA5-02 문구), `tests/test_scorecard_fix62.py` 129~145행(TEN-RA6-01 문구), `tests/test_rules_v18.py` 25~40행(v1.7·v1.8 동일성·해시).
- **.md만 고치면 깨지지 않음**: 위 V15 실측 2건을 제외하고 .md 실물을 읽는 테스트는 없다. 해시 결속 테스트군(`test_hash_binding`, `test_approval_commands`, `test_lane_n_fixes`, `test_scorecard_continue_run`, `test_judge`)은 JSON 바이트에만 반응한다.

### 권장 변경 순서

1. 새 규칙 문서 작성 + `AGENTS.md 71행` 어긋남 별도 정정(재편과 무관한 기존 고장).
2. 코드 출력 문자열(위 1~4) + 스킬 지침(위 9) 교체.
3. `factor-concepts.json`(위 10) 교체 + fix76 해당 단언 갱신 → 승인 페이지 용어집과 함께 리뷰.
4. 규칙 JSON은 신규 버전으로만 변경하고 `research → calculate → draft → review` 후 사람 승인.
5. `INTERNAL_REF_RE`·`TERM_RE`의 옛 패턴은 승계 문구가 살아 있는 동안 유지(삭제 금지).
6. 동결 묶음·기준선·구버전 JSON은 손대지 않음.

### 확인하지 못한 것과 이유

- `output/*/review-parts/`와 `validation/` 안의 행 번호 전수 행 목록: 건수는 `rg --count-matches`로 전수 계수했으나(Q5), 리뷰 보조 기록이라 한 줄씩 나열하지 않았다(재현 명령: `rg -n "[0-9]행" output/ai-scorecard-2026-09-obsreg output/ai-scorecard-2026-10-test`).
- 테스트 함수 전체가 아니라 단언 줄과 그 주변부·로드 대상까지만 읽은 것: `fix53_*`, `fix54~58`, `fix64`, `fix65`, `fix78`, `fix80`, `f5_impl48`의 나머지 본문. 분류(라·동결 단언)는 로드 경로로 확정했고, 단언 본문 추가 확인은 `npm run test:node`·`unittest` 실행이 금지돼 수행하지 않았다.
- `ai-scorecard-2026-10-test`의 승인 상태: 이 워크트리에는 `approval.json`이 없어 승인 영향은 조건부로만 기술했다. 승인된 사본이 다른 worktree에 있다면 Q4 무효화 경로가 적용된다.
- 스킬 12종·에이전트 3종의 행 번호 0건은 `rg "[0-9]행"` 전수 검색의 빈 결과로 확인했고, 약칭 `S-*`도 코드·테스트·스킬·에이전트에 없음을 저장소 전역 검색으로 확인했다.

