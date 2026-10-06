조사 에이전트: agy (Antigravity) | 모델: Gemini 3.8 Flash | 조사 시각: 2026-10-02 12:52 KST | 기준 커밋: da765c2

# 규칙 문서 재편 시 수정 대상 전수 조사 보고서

## 개요

사람이 읽는 채점 규칙 문서(`docs/scorecard/rules/AI기업_채점규칙_v1.7.md`) 재편 작업과 관련하여 다음 세 가지 변경 시 수정해야 하는 위치를 워크트리 전체에서 전수 조사했습니다.
1. 별표 A~J 체계 폐지 및 ①~⑨ 항목별 절/공통 원칙 절로의 통합.
2. 행 번호 참조 전면 변경.
3. 문서 파일 생성/삭제/역할 변경(v1.5 규칙 문서 및 `docs/scorecard/source/` 삭제, `design-guideline.md` 삭제 제안 검토, 새 규칙 문서 등).

조율자 후속 지시(msg_cf97b33eb26c) 및 사용자 정정 사항에 따라, v1.5 규칙 문서와 `docs/scorecard/source` 폴더의 문서(구현계획, HANDOVER, 채점표 v1.5)는 삭제 예정으로, `design-guideline.md`는 조율자 제안 상태(사용자 확정 전, 삭제될 수 있는 문서)로 분류하여 보고서를 작성했습니다.

---

## Q1. 코드와 테스트의 별표 참조

`scripts/`, `server/`, `tests/` 디렉터리에서 `별표` 문자열이 등장하는 위치의 전수 목록입니다.

### 1. 디렉터리 및 파일별 건수 요약
- `scripts/`: 6개 파일, 21건
  - `scripts/scorecard/baseline_import.py`: 7건
  - `scripts/scorecard/calc_qual.py`: 2건
  - `scripts/scorecard/calc_f9.py`: 2건
  - `scripts/scorecard/render_common.py`: 5건
  - `scripts/scorecard/render_html.py`: 3건
  - `scripts/scorecard/stages.py`: 2건
- `server/`: 1개 파일, 13건
  - `server/approvals.js`: 13건
- `tests/`: 9개 파일, 20건
  - `tests/node/approvals.test.js`: 2건
  - `tests/node/fixtures/summary.sample.json`: 2건
  - `tests/test_scorecard_f5_impl48.py`: 2건
  - `tests/test_scorecard_fix52_citations.py`: 2건
  - `tests/test_scorecard_fix59.py`: 1건
  - `tests/test_scorecard_fix62.py`: 2건
  - `tests/test_scorecard_fix76.py`: 4건
  - `tests/test_scorecard_impl50.py`: 2건
  - `tests/fixtures/evidence/README.md`: 1건
  - `tests/fixtures/evidence/labeling-2026-10.json`: 5건
  - `tests/fixtures/evidence/labeling-2026-10.csv`: 5건
- 총합: 16개 파일, 54건

### 2. 전수 상세 목록

#### (1) `scripts/` (21건)
1. `scripts/scorecard/baseline_import.py:28`
   - 문구: `# 규칙 v1.5 ⑨ 게이트 3·4 적용표(별표)에서 읽은 B종 약정·계약 수입...`
   - 분류: (다) 주석·docstring
   - 처리: 선택 수정. v1.5 기준선 과거 이관 로직 주석이므로 기능 영향 없음.
2. `scripts/scorecard/baseline_import.py:71`
   - 문구: `# ⑤ 별표 G 판정표 — (A, H)`
   - 분류: (다) 주석·docstring
   - 처리: 선택 수정. 기준선 데이터 상수 정의 주석.
3. `scripts/scorecard/baseline_import.py:77`
   - 문구: `# ⑦ 별표 I 판정표 — (조달 의존 비중, 자기 자금 환류)...`
   - 분류: (다) 주석·docstring
   - 처리: 선택 수정. 기준선 데이터 상수 정의 주석.
4. `scripts/scorecard/baseline_import.py:438`
   - 문구: `note="별표 J 교차검증 전용 — 점수 입력 아님"`
   - 분류: (가) 화면·리포트에 출력되는 문구
   - 처리: 고치면 안 됨. v1.5 기준선 이관 관측의 설명 메모이며, 이미 확정된 기준선(`scorecard/baseline/v1.5/observations.json`)에 들어가 있음.
5. `scripts/scorecard/baseline_import.py:533`
   - 문구: `add("F5", "grade", {"A": A, "H": H}, None, "규칙 v1.5 별표 G 판정표")`
   - 분류: (가) 화면·리포트에 출력되는 문구
   - 처리: 고치면 안 됨. v1.5 기준선 판단 생성 시 출처 표기이며 과거 기준선 데이터 보존 대상.
6. `scripts/scorecard/baseline_import.py:538`
   - 문구: `add("F7", "matrix", {"funding_dependent_share": share, "own_money_returns": returns}, None, "규칙 v1.5 별표 I 판정표")`
   - 분류: (가) 화면·리포트에 출력되는 문구
   - 처리: 고치면 안 됨. v1.5 기준선 판단 생성 시 출처 표기.
7. `scripts/scorecard/baseline_import.py:587`
   - 문구: `"- ③·⑤·⑦ 입력은 규칙 v1.5 판정표(③ 사다리, 별표 G, 별표 I)를 승계..."`
   - 분류: (가) 화면·리포트에 출력되는 문구
   - 처리: 고치면 안 됨. `import-report.md` 생성 템플릿의 과거 이관 기록.
8. `scripts/scorecard/calc_qual.py:142`
   - 문구: `pending=pending_info("judgment", "동맹 A 등급·적대 H 등급 입력 필요(별표 G)")`
   - 분류: (가) 화면·리포트에 출력되는 문구
   - 처리: 필수 수정. F5 판단 누락 시 사용자 및 리포트에 미결 사유로 노출되는 문구이므로 새 규칙 명칭(예: ⑤ 절 판정표)으로 갱신 필요.
9. `scripts/scorecard/calc_qual.py:155`
   - 문구: `pending=pending_info("judgment", "조달 의존 고객 비중(큼/작음)·자기 자금 환류(예/아니오) 판정 필요(별표 I)")`
   - 분류: (가) 화면·리포트에 출력되는 문구
   - 처리: 필수 수정. F7 판단 누락 시 미결 사유로 노출되므로 새 규칙 명칭(예: ⑦ 절 매트릭스)으로 갱신 필요.
10. `scripts/scorecard/calc_f9.py:136`
    - 문구: `# 같은 이유를 든다(채점규칙 별표 D 388~390행 계획·발표·포지션은 0점)...`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. 코드 내 판정 결정(C-29) 배경 설명 주석.
11. `scripts/scorecard/calc_f9.py:152`
    - 문구: `warnings.append("... — 전망·목표로 손실을 단정하지 않는다(별표 D 388~390행)")`
    - 분류: (가) 화면·리포트에 출력되는 문구
    - 처리: 필수 수정. C-29 판정 시 계산 결과의 warnings 배열에 포함되어 draft/HTML/audit에 노출되는 문구이므로 새 규칙의 공통 원칙 명칭으로 갱신 필요.
12. `scripts/scorecard/render_common.py:319`
    - 문구: `r"|(?:채점규칙|채점표(?:_v1\.5\.md)?|별표 [A-Z]|HANDOVER)\s*\d+(?:[·~,]\d+)*행"`
    - 분류: (나) 판정·검증 로직이 쓰는 문자열
    - 처리: 필수 수정. 본문에서 내부 참조를 걷어내는 정규식(`INTERNAL_REF_RE`)으로, 과거 승계 문언 처리를 위해 기존 패턴은 유지하되 새 규칙의 참조 형식(예: `규칙 NNN행` 등)을 추가 지원해야 함.
13. `scripts/scorecard/render_common.py:982`
    - 문구: `CREDIT_NOTE = "신용등급·CDS 는 점수 입력이 아니라 교차검증 지표다(별표 J)."`
    - 분류: (가) 화면·리포트에 출력되는 문구
    - 처리: 필수 수정. 재무상태 표 아래 캡션으로 모든 리포트 HTML에 출력되는 문구이므로 새 규칙 명칭으로 갱신 필요.
14. `scripts/scorecard/render_common.py:1220`
    - 문구: `# 내부 상태값이다. 출처 표기(별표 A)는 남긴다 — 읽는 사람이 원문을 찾아갈 수 있어야 한다.`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. `strip_worknotes` 함수 설명 주석.
15. `scripts/scorecard/render_common.py:1230`
    - 문구: `가리키는 것이 없어 틀린 말이 된다. 별표 A 같은 **출처 표기는 남긴다.**`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. `strip_worknotes` 함수의 docstring.
16. `scripts/scorecard/render_common.py:1292`
    - 문구: `# ... 기준은 별표 원문에서 가져오고 규칙 note 는 감사 기록으로 보낸다.`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. `factor_criteria` 함수 설명 주석.
17. `scripts/scorecard/render_html.py:1015`
    - 문구: `# 본문은 별표 원문을 쓰고, 이 원문 메모는 감사·대조용으로 여기 모은다.`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. `render_audit_markdown` 함수 설명 주석.
18. `scripts/scorecard/render_html.py:1023`
    - 문구: `"리포트 본문의 무엇을 보고 매기는가 는 채점규칙 별표에서 가져온다. 이 표는 규칙 JSON 의 "`
    - 분류: (가) 화면·리포트에 출력되는 문구
    - 처리: 필수 수정. `audit.md` 및 리포트 HTML 감사 탭에 렌더링되는 문구.
19. `scripts/scorecard/render_html.py:1122`
    - 문구: `secs.append(('무엇을 보고 매기는가', ..., '채점규칙 별표의 지표다.'))`
    - 분류: (가) 화면·리포트에 출력되는 문구
    - 처리: 필수 수정. 리포트 HTML의 9개 factor 카드 헤더 서브타이틀로 직접 출력되는 고정 문구이므로 새 규칙 구조(예: '채점규칙 항목별 지표다.')에 맞게 수정 필요.
20. `scripts/scorecard/stages.py:90`
    - 문구: `{"source_id": SRC_RULE, "title": "AI기업_채점규칙_v1.5.md (③ 사다리·별표 G·별표 I·⑨ 적용표·⑥ 비상장)", ...}`
    - 분류: (가) 화면·리포트에 출력되는 문구
    - 처리: 필수 수정. 새 실행을 생성할 때 `sources.json`에 기록되어 리포트 출처 표에 표시되는 제목 문자열임. 새 규칙 문서 명칭으로 갱신 필요.
21. `scripts/scorecard/stages.py:577`
    - 문구: `# ⑤ 판정표(별표 G)가 적은 것만 쓴다 — Alphabet·Amazon·Microsoft 는 Anthropic 지분 투자...`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. `ANTHROPIC_RELATION` 상수 정의 주석.

#### (2) `server/` (13건)
22. `server/approvals.js:37`
    - 문구: `// 2026-10-01 사용자 요청: 근거 문장의 규칙 용어(별표·잣대·게이트·체크리스트)를 설명 없이 두지 않는다.`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. 개발 주석.
23~32. `server/approvals.js:41~50` (10건)
    - 문구: `'star-A'`부터 `'star-J'`까지 `term: '별표 A'` ~ `'별표 J'` 및 해당 해설 정의.
    - 분류: (가) 화면·리포트에 출력되는 문구
    - 처리: 필수 수정. 승인 페이지 렌더러가 용어 링크의 툴팁 및 페이지 하단 참조표(`GLOSSARY`)로 출력하는 정본 사전 객체임. 별표 체계가 폐지되면 새 용어 체계로 교체되어야 함.
33. `server/approvals.js:62`
    - 문구: `// 별표 X · P1~P4 · G1~G4 · 게이트 N · 체크리스트 N · QNN · 긴장 #N · <company>.F<n>`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. 정규식 설명 주석.
34. `server/approvals.js:63`
    - 문구: `const TERM_RE = /별표\s*([A-J])|\bP([1-4])\b|\bG([1-4])\b|게이트\s*([1-4])|체크리스트\s*(\d{1,2})|\bQ(\d{2})\b|긴장\s*#?(\d{1,2})|\b([a-z][a-z-]*)\.F([1-9])\b/g;`
    - 분류: (나) 판정·검증 로직이 쓰는 문자열
    - 처리: 필수 수정. 승인 페이지에서 근거 문장 내 용어를 링크로 변환하는 정규식임. 새 규칙 체계의 용어를 매칭하도록 패턴 수정 필요.

#### (3) `tests/` (20건)
35. `tests/node/approvals.test.js:151`
    - 문구: `assert.match(res.body, /<a class="term" href="#ref-star-F"[^>]*>별표 F<\/a>/);`
    - 분류: (라) 테스트의 기대값
    - 처리: 필수 수정. 승인 페이지 용어 링크 렌더링 테스트이며, `server/approvals.js` 수정 시 함께 수정해야 함.
36. `tests/node/approvals.test.js:155`
    - 문구: `assert.match(res.body, /<dt id="ref-star-G">별표 G<\/dt>/, '참조표가 있어야 함');`
    - 분류: (라) 테스트의 기대값
    - 처리: 필수 수정. 승인 페이지 하단 참조표 렌더링 테스트.
37. `tests/node/fixtures/summary.sample.json:76`
    - 문구: `"relevance": "추론: Blackwell 출하 확대는 별표 F 의 성능 도약 경로로 nvidia.F2 를 다시 볼 계기다..."`
    - 분류: (라) 테스트의 기대값 / 픽스처 데이터
    - 처리: 필수 수정. `approvals.test.js`가 사용하는 샘플 픽스처로, 151행 assertion과 연동됨.
38. `tests/node/fixtures/summary.sample.json:252`
    - 문구: `"evidence_after": ["적대 등급은 비용형이다 — 시험용 <b>태그</b> 문장(EV-nvidia-001, 별표 G)"]`
    - 분류: (라) 테스트의 기대값 / 픽스처 데이터
    - 처리: 선택 수정. 태그 테스트용 샘플 데이터.
39. `tests/test_scorecard_f5_impl48.py:6`
    - 문구: `3. **근거는 행번호로 원문을 가리킨다.** 체크리스트 19(727) · 별표 G A 기준표(188~195)...`
    - 분류: (다) 주석·docstring
    - 처리: 고치면 안 됨. 과거 실행(`ai-scorecard-2026-09-obsreg`) 판단을 검증하는 불변 테스트의 docstring.
40. `tests/test_scorecard_f5_impl48.py:7`
    - 문구: `   (262·264·266) · 별표 H(anthropic 288 / openai 276) · 채점표 759(openai).`
    - 분류: (다) 주석·docstring
    - 처리: 고치면 안 됨. 불변 테스트의 docstring.
41. `tests/test_scorecard_fix52_citations.py:4`
    - 문구: `1. **행 번호를 인용하면 그 문서의 source_id 가 붙는다.** 채점규칙·별표·체크리스트 → SRC-v15-rule, ...`
    - 분류: (다) 주석·docstring
    - 처리: 고치면 안 됨. 과거 실행 검증 테스트 docstring.
42. `tests/test_scorecard_fix52_citations.py:31`
    - 문구: `if re.search(r"채점규칙|별표 [A-J]|체크리스트\s*\d+", text):`
    - 분류: (나) 판정·검증 로직이 쓰는 문자열
    - 처리: 고치면 안 됨. 과거 실행 `ai-scorecard-2026-09-obsreg`의 `judgments.json`이 규칙 출처 ID를 올바르게 인용했는지 검사하는 불변 회귀 테스트 로직임.
43. `tests/test_scorecard_fix59.py:77`
    - 문구: `self.assertIn("별표 D 388~390행", t["tension"])`
    - 분류: (라) 테스트의 기대값
    - 처리: 고치면 안 됨. `v1.7.json`의 open_tensions 항목("TEN-RA5-02") 문자열을 검증하는 테스트.
44. `tests/test_scorecard_fix62.py:95`
    - 문구: `self.assertIn("별표 D 와 충돌한다", sup["why_not_chosen"])`
    - 분류: (라) 테스트의 기대값
    - 처리: 고치면 안 됨. C-29 결정 레코드의 문자열 검증.
45. `tests/test_scorecard_fix62.py:137`
    - 문구: `self.assertIn("별표 D 388~390행", t["tension"])`
    - 분류: (라) 테스트의 기대값
    - 처리: 고치면 안 됨. `v1.7.json`의 open_tensions 항목("TEN-RA6-01") 문자열 검증.
46. `tests/test_scorecard_fix76.py:27`
    - 문구: `# 본문에 실리면 안 되는 작업 메모. 별표 A 같은 출처 표기는 대상이 아니다.`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. 작업 메모 필터링 주석.
47. `tests/test_scorecard_fix76.py:108`
    - 문구: `"""별표 A 는 읽는 사람이 원문을 찾아가는 표시라 남긴다."""`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. 테스트 메소드 docstring.
48. `tests/test_scorecard_fix76.py:109`
    - 문구: `self.assertIn("별표 A", rc.factor_criteria(self.ctx, "F1")[0])`
    - 분류: (라) 테스트의 기대값
    - 처리: 필수 수정. `factor-concepts.json`의 F1 metrics 문자열을 검증하는 테스트로, `factor-concepts.json`에서 별표 A를 수정할 경우 단독 실패함.
49. `tests/test_scorecard_fix76.py:110`
    - 문구: `self.assertIn("별표 D", rc.factor_criteria(self.ctx, "F4")[0])`
    - 분류: (라) 테스트의 기대값
    - 처리: 필수 수정. `factor-concepts.json`의 F4 metrics 문자열 검증 테스트로, `factor-concepts.json` 수정 시 동기화 필요.
50. `tests/test_scorecard_impl50.py:6`
    - 문구: `3. **원문에 반대로 읽힐 자리(별표 I 347행)를 숨기지 않는다.**`
    - 분류: (다) 주석·docstring
    - 처리: 고치면 안 됨. 과거 C-11 결정 검증 테스트 docstring.
51. `tests/test_scorecard_impl50.py:46`
    - 문구: `"""별표 I 347행이 영업외 이익 비중을 ⑦ 절 측정 가능 칸에 적는다 — 판정 입력 지정은 아니지만 숨기지 않는다."""`
    - 분류: (다) 주석·docstring
    - 처리: 고치면 안 됨. 테스트 메소드 docstring.
52. `tests/fixtures/evidence/README.md:18`
    - 문구: `... factor 정의와 별표를 대어 다시 썼다.`
    - 분류: (다) 주석·docstring
    - 처리: 선택 수정. 픽스처 설명 문서.
53. `tests/fixtures/evidence/labeling-2026-10.json` (5건: 62, 158, 270, 318, 334행)
    - 문구: `proposed_reason` 내 "별표 H", "별표 D", "별표 C" 인용.
    - 분류: (라) 테스트의 기대값 / 픽스처 데이터
    - 처리: 선택 수정. 수집 선별 품질 평가용 레이블링 데이터.
54. `tests/fixtures/evidence/labeling-2026-10.csv` (5건: 5, 11, 18, 21, 22행)
    - 문구: 제안 이유 내 "별표 H", "별표 D", "별표 C" 인용.
    - 분류: (라) 테스트의 기대값 / 픽스처 데이터
    - 처리: 선택 수정. 수집 선별 품질 평가용 CSV 데이터.

---

## Q2. 별표 이름이 동작을 바꾸는 곳

별표 이름을 문자열 비교, 정규식, 딕셔너리 키, 검증 조건으로 사용하는 위치와 동작 영향 분석입니다.

### 1. `server/approvals.js` (승인 서버 라우터 및 렌더러)
- 사용 위치:
  - 40~50행 `GLOSSARY` 객체의 키(`'star-A'` ~ `'star-J'`).
  - 63행 `TERM_RE` 정규식: `/별표\s*([A-J])|\bP([1-4])\b|.../g`.
  - 67~76행 `linkTerms()` 함수:
    ```javascript
    if (star) key = `star-${star}`;
    ...
    if (key) {
      const ref = GLOSSARY[key];
      return `<a class="term" href="#ref-${key}" title="${escapeHtml(ref.term)}: ${escapeHtml(ref.text)}">${m}</a>`;
    }
    ```
  - 86행 하단 참조표 렌더러: `Object.keys(GLOSSARY).map(...)`.
- 동작 영향:
  - 근거 문장이나 판단 메모에 "별표 A"~"별표 J"가 나타나면 정규식으로 감지하여 `<a class="term" href="#ref-star-X">` 태그로 변환하고 툴팁으로 해설을 표시합니다.
  - 별표 체계를 없애고 규칙을 재편한 뒤, 만약 `server/approvals.js`를 수정하지 않는다면:
    1. 새 규칙 문맥에서 작성된 판단/근거 텍스트(예: "① 절 락인 원칙", "⑤ 절 동맹 기준" 등)가 자동 하이퍼링크 및 툴팁 설명으로 연결되지 않습니다.
    2. 승인 페이지 최하단의 용어 참조표(`ref-list`)에 더 이상 사용되지 않는 낡은 별표 A~J 정의 10개가 계속 노출됩니다.
    3. `tests/node/approvals.test.js`의 151행(`별표 F`), 155행(`별표 G`) 검증이 실패하거나 낡은 정의에 의존하게 됩니다.

### 2. `scripts/scorecard/render_common.py` (공통 리포트 렌더러)
- 사용 위치:
  - 317~321행 `INTERNAL_REF_RE` 정규식:
    `r"|(?:채점규칙|채점표(?:_v1\.5\.md)?|별표 [A-Z]|HANDOVER)\s*\d+(?:[·~,]\d+)*행"`
  - 337행 `strip_internal_refs()` 함수:
    리포트 본문 문장에서 내부 상태값 및 작업 메모, 특정 행 번호 참조를 지우고 감사 기록으로 보낼 때 사용.
- 동작 영향:
  - `별표 [A-Z] \d+행` 패턴에 매칭되는 문장을 본문에서 걷어냅니다.
  - 새 규칙에서 별표 체계가 폐지되어 새로운 참조 형식(예: `규칙 NNN행` 등)이 쓰일 경우, 이 정규식에 반영되지 않으면 해당 내부 참조가 리포트 본문 문장에서 걸러지지 않고 그대로 노출될 위험이 있습니다.

### 3. `tests/test_scorecard_fix52_citations.py` (출처 인용 검증 테스트)
- 사용 위치:
  - 31행 `if re.search(r"채점규칙|별표 [A-J]|체크리스트\s*\d+", text):`
- 동작 영향:
  - `ai-scorecard-2026-09-obsreg` 실행의 판단 문구에 `별표 [A-J]`가 있을 때 `source_ids`에 `SRC-v15-rule`이 등록되어 있는지를 검사합니다. 과거 실행 검증용이므로 새 규칙에 직접 영향을 주지는 않습니다.

### 4. 채점 및 계산 로직 (`scripts/scorecard/calc_*.py`)
- 확인 결과: **계산 엔진 코드(`calc_*.py`) 내에서 별표 이름을 분기 조건, 딕셔너리 키, 정규식 등으로 사용하는 곳은 전혀 없습니다.**
- 근거:
  - `calc_qual.py`의 142행과 155행에 `pending_info` 메시지 문자열 리터럴로 `"동맹 A 등급·적대 H 등급 입력 필요(별표 G)"`가 사용된 것이 전부이며, 점수 산출 로직은 오직 구조화된 입력 키(`judgment["inputs"]`)와 숫자 값에 의해서만 결정론적으로 계산됩니다.

---

## Q3. 규칙 문서의 행 번호 참조

`NNN행`, `NNN~NNN행` 형태로 규칙 문서나 다른 문서의 행을 가리키는 참조 전수 목록입니다.

### 1. 대상 문서 및 판본별 분류
- **`AI기업_채점규칙_v1.5.md` 참조**:
  - 17행(점수 하한 일괄 선언), 22행(Tau3-Bench 등 하네스 표기 부재), 70행, 145행, 153행, 163행, 188~195행(별표 G 동맹 A 기준표), 192·193행(TSMC 동맹), 201행(별표 C·G 적대 등급 H 정의), 205행, 214행(Anthropic A=+2), 217행, 224행(OpenAI A=+2), 239행(별표 H 3문 이탈 조건), 262행·264행·266행(이중계상 금지선), 273~278행(별표 H 예시표), 288행(Anthropic), 319~322행(별표 I 2축 판정표), 338행, 347행(별표 I 측정 가능/불가 표), 351~356행(별표 I 평가이익 F7 제외), 384행(Claude=Anthropic 이해상충 및 제3자 재검토 약속), 388~390행(별표 D 계획·발표·포지션 0점), 398행(별표 A 강한 락인), 400행(별표 A 얕은 채널), 438행(영업외 비중 F7 이월 차단), 470행(⑨ 적용표 손실률 -30% 초과 또는 BEP 목표 후퇴), 494행·603행(OpenAI BEP 후퇴 적용), 645~647행(비상장 P/S 사용 근거), 649~654행(⑥ 가격 항목), 727행·731행(체크리스트 19).
- **`AI기업_채점표_v1.5.md` 참조**:
  - 188행, 198행, 264행(Tau3-Bench), 350행, 375행(HLE 미달), 662행, 671·673행(v1.5 인용), 732행(FrontierMath), 759행(OpenAI Stargate), 943행(지표 표), 1100행(재채점 시점).
- **`AI기업_채점표_HANDOVER.md` 참조**:
  - 22행(F2 손실 경위), 40행(TTM PER 및 영업외 비중 출처), 51행(약정 합계 $300B), 75행(3-7 작성자 이해상충), 120행(재채점 일정).
- **`docs/scorecard/design-guideline.md` 참조**:
  - 272행(C-14 트리거 미래 점수 저장 금지).
- **`AGENTS.md` 참조**:
  - 71행(승계 판단 예외 규정).
- **기타(규칙 문서 아님)**:
  - `render_html.py:336`, `test_scorecard_fix64.py:171`, `test_scorecard_fix65.py:173`의 '14행' (UI 레이아웃의 기업 수 14행).
  - `tests/fixtures/README.md:5`의 '10431행' (SEC 티커 원자료 줄 수).

### 2. 위치별 건수 및 상세 목록
- `scripts/`: 6개 파일, 18건
  - `calc_f9.py`: 136행(`388~390행`, `470·494·603행`), 152행(`388~390행`), 176행(`470행`).
  - `calc_f6_params.py`: 467행(`645~647행`).
  - `schema.py`: 1196행(`design-guideline 272행`).
  - `validate.py`: 54행, 259행, 262행 (`AGENTS.md 71행`).
  - `render_common.py`: 270행(`22행`), 319행(정규식 패턴), 516행(`120행`), 732행(`22행`), 1600행(`384행`), 1617행(`120행`).
  - `render_md.py`: 359행(`채점규칙 384행 · HANDOVER 75행`).
  - `stages.py`: 85행(`384행`), 90행(`채점규칙 384행`), 92행(`HANDOVER 75행`).
- `server/`: 0건 (확인 검색어: `\d+행`, 검색 결과 없음).
- `tests/`: 20개 파일, 70건
  - `test_scorecard_c03.py`: 63, 85, 117, 122행.
  - `test_scorecard_f5_impl48.py`: 8, 87, 88, 92, 99, 100, 105, 106행.
  - `test_scorecard_fix52_citations.py`: 6, 76, 80행.
  - `test_scorecard_fix53_aws_label.py`: 48행.
  - `test_scorecard_fix53_stage2.py`: 43, 45, 108행.
  - `test_scorecard_fix53_rules.py`: 62, 67, 73, 74행.
  - `test_scorecard_fix53_draft.py`: 38, 55행.
  - `test_scorecard_fix53_stage3.py`: 131, 155행.
  - `test_scorecard_fix55_stage1.py`: 86행.
  - `test_scorecard_fix54_tensions.py`: 42, 43, 63, 90행.
  - `test_scorecard_fix56_stage1.py`: 154행.
  - `test_scorecard_fix56_stage2.py`: 116, 119행.
  - `test_scorecard_fix57_stage2.py`: 71, 86행.
  - `test_scorecard_fix58_stage2.py`: 192행.
  - `test_scorecard_fix59.py`: 77행.
  - `test_scorecard_fix60.py`: 60, 138행.
  - `test_scorecard_fix62.py`: 90, 92, 136, 137행.
  - `test_scorecard_fix64.py`: 159행.
  - `test_scorecard_fix78.py`: 120행.
  - `test_scorecard_fix80.py`: 101행.
  - `test_scorecard_impl50.py`: 6, 41, 46, 47, 61행.
- `scorecard/`:
  - `scorecard/rules/v1.7.json`: 136건.
  - `scorecard/rules/v1.8.json`: 136건.
  - `scorecard/factor-concepts.json`: 0건 (확인 검색어: `\d+행`, 일치 0건).
  - `scorecard/baseline/`: 0건.
- `docs/`: 2개 파일, 2건
  - `docs/scorecard/design-guideline.md:435`: `별표 I 351~356행 · 채점규칙 438행`.
  - `docs/scorecard/structure.md:176`: `체크리스트 23행`.
- `.claude/skills/`, `.agents/skills/`, `.claude/agents/`: 0건 (확인 검색어: `\d+행`, 일치 0건).

---

## Q4. 규칙 JSON 과 공유 정의

### 1. `scorecard/rules/v1.8.json` 및 `scorecard/factor-concepts.json` 내 참조 현황
- `scorecard/rules/v1.8.json`:
  - `별표` 참조: 37건 (별표 A, 별표 C, 별표 D, 별표 G, 별표 H, 별표 I, 별표 J 인용).
  - `\d+행` 참조: 136건 (v1.5 규칙 문서 및 채점표, HANDOVER 행 번호 인용).
- `scorecard/factor-concepts.json`:
  - `별표` 참조: 5건
    - 20행 (F1 metrics): `지표 — **채널별로 다르게 잰다(별표 A)** ...`
    - 50행 (F4 metrics): `... 계획·발표·포지션은 0점(별표 D) — 출하·매출·채택률처럼 지금 측정되는 것만 센다`
    - 56행 (F5 question): `판정은 별표 G — 3 + 동맹등급 + 적대등급`
    - 58행 (F5 examples): `판정은 두 축이다(별표 G) ... 조달과 동맹의 구분(별표 H) ...`
    - 96행 (F7 metrics): `등급 판정은 **별표 I** — 기준은 "본업의 루프 의존도" ...`
  - `\d+행` 참조: **0건** (행 번호 참조 없음).

### 2. 코드 확인 답변

#### (1) `rule_hash` 는 무엇으로 계산하는가? 설명 문구(`note` 등)만 고쳐도 해시가 바뀌는가?
- 계산 방식:
  `scripts/scorecard/rules.py` 20행:
  ```python
  self.hash: str = sha256_file(path)
  ```
  규칙 파일(`scorecard/rules/<version>.json`) 전체 바이트의 SHA-256 해시를 계산합니다.
- 설명 문구 수정 영향:
  **네, 완전히 바뀝니다.** 파일 전체 내용의 암호화 해시이므로, `note`나 설명 문구 등 단 한 글자만 고쳐도 `rules.hash`가 달라집니다.

#### (2) 해시가 바뀌면 승인된 실행 `ai-scorecard-2026-10-test` 에 어떤 영향이 있는가?
- 현재 상태 확인:
  `output/ai-scorecard-2026-10-test/run.json`은 `"rule_version": "v1.8"`, `"rule_hash": "7e215b55c516cca4ccf0ce4d6d1d0a94014b4ecaf01f3bc523127f29009c59c4"`를 기록하고 있습니다. 리뷰(`review.md`)는 `status: pass`이지만 아직 사람이 승인하지 않아 `approval.json` 파일은 존재하지 않습니다.
- 불일치 발생 시 영향:
  1. `scripts/scorecard/engine.py` 90~93행:
     ```python
     if run.get("rule_hash") and run["rule_hash"] != rules.hash:
         raise RuntimeError(
             f"run.json rule_hash {run['rule_hash'][:12]}… 와 규칙 파일 해시 {rules.hash[:12]}… 불일치 — 규칙이 바뀌었으면 새 실행을 만든다"
         )
     ```
     `v1.8.json`의 해시가 바뀌면 `load_context("ai-scorecard-2026-10-test")`를 호출하는 모든 명령(계산, 초안, 리뷰 검증, 승인, 빌드 등)이 즉시 `RuntimeError`를 발생시키며 중단됩니다.
  2. `scripts/scorecard/validate.py` 129~130행:
     `plan.md`의 `rule_hash`와 불일치하여 계약 검증 실패 에러가 발생합니다.
  3. 결론적으로 `v1.8.json`을 수정하면 `ai-scorecard-2026-10-test`는 승인할 수 없게 되며, 새 실행으로 다시 만들거나 해당 실행의 입력을 갱신해야 합니다. 따라서 규칙 개정 시에는 기존 `v1.8.json`을 직접 수정하지 않고 새 버전(예: `v1.9.json`)을 생성해야 합니다.

#### (3) `factor-concepts.json` 은 어느 코드가 읽고 어디에 출력하는가? 승인 해시에 들어가는가?
- 읽는 코드:
  `scripts/scorecard/render_common.py`의 `factor_concepts()`(1247행) 및 `factor_concept()`(1261행)에서 유일하게 파일을 읽습니다.
- 출력 위치:
  `scripts/scorecard/render_html.py`의 `_factor_card()`(1095행)에서 호출되어, 리포트 HTML(`report.html`)의 9개 항목 카드 내 '무엇을 재는가'(definition, question), '무엇을 보고 매기는가'(metrics) 섹션에 렌더링됩니다. 채점 계산 엔진(`calc_*.py`)이나 마크다운 초안(`draft.md`)에는 전혀 출력되지 않습니다.
- 승인 해시 포함 여부:
  **포함되지 않습니다.**
  `scripts/scorecard/engine.py`의 `input_hashes()`는 `run.json`, `observations.json`, `judgments.json`, `sources.json`, `evidence.json`, `triggers.json`만 해시하며, `stages.py`의 `current_hashes()` 역시 `rules`, `observations`, `judgments`, `run`, `results`, `draft`, `sources`만 포함합니다. `factor-concepts.json`은 승인 해시 대상에서 완전히 제외되어 있습니다. 따라서 이 파일의 별표 문구를 고쳐도 승인 해시나 `rule_hash`는 깨지지 않습니다.

---

## Q5. 고칠 수 없는 참조

과거 기준선, 승인된 과거 실행 묶음, 구버전 규칙 JSON의 참조 현황 및 전파 경로 분석입니다.

### 1. 파일별 건수 목록
- `scorecard/baseline/v1.5/`:
  - `scores.json`: 별표 16건, 행 번호 0건
  - `observations.json`: 별표 14건, 행 번호 0건
  - `triggers.json`: 별표 5건, 행 번호 0건
  - `import-report.md`: 별표 1건, 행 번호 0건
- `output/ai-scorecard-2026-09-baseline/`:
  - `judgments.json`: 별표 42건, 행 번호 0건
  - `observations.json`: 별표 14건, 행 번호 0건
  - `draft.md`: 별표 20건, 행 번호 0건
  - `research.md`: 별표 41건, 행 번호 0건
  - `sources.json`: 별표 1건, 행 번호 0건
  - `review.md`: 별표 5건, 행 번호 0건
  - `report.html`: 별표 5건, 행 번호 0건
- `output/ai-scorecard-2026-09-obsreg/`:
  - `judgments.json`: 별표 63건, 행 번호 48건
  - `observations.json`: 별표 14건, 행 번호 36건
  - `draft.md`: 별표 37건, 행 번호 32건
  - `research.md`: 별표 38건, 행 번호 4건
  - `audit.md`: 별표 12건, 행 번호 28건
  - `sources.json`: 별표 1건, 행 번호 5건
  - `run.json`: 별표 1건, 행 번호 5건
  - `results.json`: 별표 1건, 행 번호 3건
  - `review.md`: 별표 4건, 행 번호 7건
  - `report.html`: 별표 6건, 행 번호 1건
  - `review-parts/` 산하 파일: 별표 49건, 행 번호 172건
- `output/ai-scorecard-2026-10-test/`:
  - `judgments.json`: 별표 67건, 행 번호 52건
  - `observations.json`: 별표 14건, 행 번호 36건
  - `evidence/evidence.json`: 별표 36건, 행 번호 0건
  - `triggers.json`: 별표 9건, 행 번호 0건
  - `draft.md`: 별표 42건, 행 번호 31건
  - `research.md`: 별표 70건, 행 번호 4건
  - `proposals.json`: 별표 14건, 행 번호 16건
  - `audit.md`: 별표 12건, 행 번호 27건
  - `sources.json`: 별표 1건, 행 번호 5건
  - `run.json`: 별표 1건, 행 번호 1건
  - `results.json`: 별표 1건, 행 번호 3건
  - `review.md`: 별표 4건, 행 번호 6건
  - `report.html`: 별표 6건, 행 번호 1건
  - `review-parts/` 산하 파일: 별표 8건, 행 번호 55건
- 규칙 JSON:
  - `scorecard/rules/v1.5.json`: 별표 12건, 행 번호 0건
  - `scorecard/rules/v1.6.json`: 별표 12건, 행 번호 0건
  - `scorecard/rules/v1.7.json`: 별표 37건, 행 번호 136건

### 2. 출력 경로 및 렌더링 함수 분석
이 문구들이 리포트 HTML, 초안, 승인 페이지에 그대로 출력되는 실제 경로는 다음과 같습니다.
1. `draft.md`:
   - 함수: `scripts/scorecard/render_md.py`의 `render_draft()` 및 `_render_company_section()`.
   - 경로: 이전 실행에서 승계된 판단(`carried`)의 `evidence`, `note`, `counter_evidence` 텍스트를 마크다운 기업별 섹션에 그대로 옮겨 적습니다.
   - 또한 359행의 작성자 이해상충 고지 `(채점규칙 384행 · HANDOVER 75행 · 운영이력 긴장 #4·#11)`가 매번 초안에 고정 렌더링됩니다.
2. `report.html`:
   - 함수: `scripts/scorecard/render_html.py`의 `_factor_card()`, `render_report_html()`.
   - 경로: `factor-concepts.json`의 metrics 텍스트와 1122행의 `'채점규칙 별표의 지표다.'` 서브타이틀이 항목 카드로 직접 출력됩니다.
   - 함수: `scripts/scorecard/render_common.py`의 982행 `CREDIT_NOTE` 문자열(`별표 J`)이 재무상태 표 아래 캡션으로 출력됩니다.
   - 함수: `scripts/scorecard/render_html.py`의 `render_audit_markdown()`. 규칙의 `factors.*.note` 및 내부 표기들이 감사 파일(`audit.md`) 및 리포트 HTML 감사 탭에 출력됩니다.
3. 승인 페이지:
   - 함수: `server/approvals.js`의 `renderApprovalsPage()`, `renderJudgmentEditForm()`.
   - 경로: 이전 실행의 `judgments.json` 내 `evidence`와 `note`를 그대로 화면에 표시합니다. 이때 66행 `linkTerms()`가 정규식 `TERM_RE`로 텍스트 내 "별표 X"를 감지하여 `<a class="term" href="#ref-star-X">`로 변환하고 툴팁을 답니다. 페이지 하단에는 `GLOSSARY` 객체의 별표 A~J 목록이 고정 렌더링됩니다.

### 3. `init --from-run` 승계 시 이전 문구 전달 여부
- **네, 그대로 넘어옵니다.**
- 근거:
  `scripts/scorecard/stages.py`의 `_load_from_prior_run()`(145~201행)은 이전 실행 디렉터리의 `judgments.json`을 읽어 새 실행의 `judgments.json`에 그대로 복사합니다.
  판단 항목의 `evidence`, `note`, `counter_evidence`, `superseded` 필드가 한 글자도 변경되지 않고 승계되므로, 과거 실행에서 작성된 "별표 G", "별표 D 388~390행", "채점규칙 727행" 등의 문구가 새 실행의 판단 파일로 고스란히 이관됩니다.

---

## Q6. 문서 파일 이름과 경로 참조

대상 문서 9종 및 약칭 5종에 대한 전수 참조 위치 및 분류 목록입니다.

### 1. 전수 목록 및 분류

#### (1) `AI기업_채점규칙_v1.5.md`
- (나) 테스트가 내용/존재 검사: 2건
  - `tests/test_scorecard_fix59.py:25, 67~72`: `test_openai_f9_route_reversal()`에서 `V15 = ROOT / "docs" / "scorecard" / "rules" / "AI기업_채점규칙_v1.5.md"` 파일이 존재하면 읽어서 470행("BEP 목표가 후퇴"), 494행("OpenAI"), 603행("BEP 자체가 후퇴"), 390행("계획·발표·포지션은 0점") 문구가 정확히 일치하는지 검사.
  - `tests/test_scorecard_fix62.py:23, 142~145`: `test_the_v15_conflict_itself_stays_open_for_november()`에서 동일하게 `V15`를 읽어 470행, 390행을 검사.
  *(참고: 두 테스트 모두 `if V15.is_file():` 가드가 있어 파일이 삭제되면 검사를 조용히 건너뛰지만, 파일 내용이 변경되거나 줄 번호가 바뀌면 테스트가 실패함).*
- (다) 문구 언급:
  - `scripts/scorecard/stages.py:90`: `SRC_RULE` 제목에 파일명 포함(새 실행의 `sources.json` 생성).
  - `scorecard/rules/v1.5.json:5, 7`, `v1.6.json:5, 7`, `v1.7.json:5, 7`, `v1.8.json:5`: `source.file` 및 `note`에 명시.
  - `docs/scorecard/rules/AI기업_채점규칙_v1.7.md:12`: 출발점 문서 표.
  - `docs/scorecard/source/AI기업_채점자동화_구현계획.md:52`.
  - `docs/scorecard/source/AI기업_채점표_v1.5.md:21`.
  - `docs/scorecard/design-guideline.md:44` (S-RULE).

#### (2) `AI기업_채점규칙_v1.7.md`
- (나) 테스트가 내용 검사: 1건
  - `tests/test_rules_v18.py:17`: `V18_NOTE_SUFFIX` 상수에 `docs/scorecard/rules/AI기업_채점규칙_v1.7.md` 파일명이 포함되어 있고, `v1.8.json`의 `note` 끝부분과 일치하는지 검사.
- (다) 문구 언급:
  - `server/approvals.js:39`: `const RULES_DOC = 'docs/scorecard/rules/AI기업_채점규칙_v1.7.md';` (87행에서 승인 페이지 하단 안내문으로 출력).
  - `.claude/skills/score-collect/SKILL.md:38`: `docs/scorecard/rules/AI기업_채점규칙_v1.7.md` 언급.
  - `scorecard/rules/v1.8.json:5`: `note`에 프로즈 참조로 명시.
  - `tests/fixtures/evidence/README.md:18`: 설명 문구.

#### (3) `AI기업_채점표_v1.5.html`
- (가) 코드가 실제로 읽음: 1건
  - `scripts/scorecard/baseline_import.py:13`: `DEFAULT_HTML = DEFAULT_SOURCE_DIR / "AI기업_채점표_v1.5.html"` 상수로 선언되고, `import_baseline()` 함수(376행)에서 `html_path.read_text(encoding="utf-8")`로 실제 파일을 읽어 파싱함.
- (나) 테스트가 내용 검사: 1건
  - `tests/test_scorecard_fix76.py:69`: `test_the_concept_text_is_copied_not_written()`에서 외부 절대경로(`C:/Users/noble/.../AI기업_채점표_v1.5.html`)가 존재하면 읽어 개념 텍스트와 대조 검사.
- (다) 문구 언급:
  - `scorecard/factor-concepts.json:3, 5`: `source.file`로 명시.
  - `scorecard/baseline/v1.5/scores.json:7`: 원본 HTML 파일명 및 SHA-256 기록.
  - `scripts/scorecard/stages.py:88`: `SRC_HTML` 제목에 포함.
  - `docs/scorecard/source/AI기업_채점자동화_구현계획.md:55`.

#### (4) `AI기업_채점표_v1.5.md`
- (가) 코드가 실제로 읽음: 1건
  - `scripts/scorecard/baseline_import.py:14`: `DEFAULT_MD = DEFAULT_SOURCE_DIR / "AI기업_채점표_v1.5.md"` 상수로 선언되고, `import_baseline()` 함수(378행)에서 `md_path.read_text(encoding="utf-8")`로 읽어 순위표 총점을 교차 검증함.
- (다) 문구 언급:
  - `scorecard/baseline/v1.5/scores.json:9`: 원본 MD 파일명 및 SHA-256 기록.
  - `scripts/scorecard/stages.py:89`: `SRC_MD` 제목에 포함.
  - `docs/scorecard/design-guideline.md:38` (S-SCORE).
  - `docs/scorecard/source/AI기업_채점자동화_구현계획.md:54`.
  - `docs/scorecard/source/AI기업_채점표_v1.5.md:21`.
  - `scorecard/rules/v1.7.json:492`, `v1.8.json:492`: 영업외 비중 출처 설명.

#### (5) `AI기업_채점자동화_구현계획.md`
- (가) 코드 읽기: 없음.
- (나) 테스트 검사: 없음.
- (다) 문구 언급:
  - `docs/scorecard/design-guideline.md:36` (S-PLAN).
  - `docs/scorecard/source/AI기업_채점자동화_구현계획.md:1`.

#### (6) `AI기업_채점표_HANDOVER.md`
- (가) 코드 상수 및 메타데이터 정의: 1건
  - `scripts/scorecard/baseline_import.py:25~26`: `SRC_HANDOVER_SHA256` 상수로 해시가 고정되어 있으며, `scripts/scorecard/stages.py:92`에서 새 실행의 `sources.json` 생성 시 `SRC_HANDOVER` 제목으로 등록됨.
- (나) 테스트가 내용 검사: 2건
  - `tests/test_scorecard_fix52_citations.py:76`: `sources.json`의 `SRC-v15-handover` 항목 내 `conflict_of_interest`에 "75행"이 포함되어 있는지 검사.
  - `tests/test_scorecard_fix57_stage2.py:86`: `stages.py` 코드 문자열에 "HANDOVER 75행"이 포함되어 있는지 검사.
- (다) 문구 언급:
  - `docs/scorecard/design-guideline.md:37` (S-HAND).
  - `scorecard/rules/v1.7.json:493, 1478`, `v1.8.json:493, 1478`.

#### (7) `design-guideline.md`
- (가) 코드 읽기: 없음 (`scripts/scorecard/schema.py:1196` 주석에만 언급).
- (나) 테스트가 내용/존재 검사: 2건
  - `tests/test_scorecard_fix52_docs.py:21`: `GuidelineRangeTableTest.test_changed_rows_show_v17_range_first_and_keep_old()`에서 `(ROOT / "docs" / "scorecard" / "design-guideline.md").read_text()`로 파일을 직접 열어 F2, F6, F7, F9의 v1.7 밴드 표기 및 `[낡음 표시 2026-09-15 FIX-52]` 문자열을 검사. 파일 부재 시 `FileNotFoundError` 발생.
  - `tests/test_scorecard_impl50.py:83`: `BothSidesTest.test_guideline_row_is_marked_stale()`에서 동일하게 파일을 직접 열어 `| C-11 |` 행의 취소선 및 `[낡음 2026-09-14 IMPL-50]` 문자열을 검사. 파일 부재 시 `FileNotFoundError` 발생.
- (다) 문구 언급:
  - 저장소 루트 `AGENTS.md:7`: `도메인 명세는 docs/scorecard/design-guideline.md`.
  - `README.md:231`: `도메인 명세는 docs/scorecard/design-guideline.md`.
  - `scorecard/rules/v1.5.json:5`, `v1.6.json:5`, `v1.7.json:5`, `v1.8.json:5`: `note`에 참조 문서로 명시.
- 분류 상태: **조율자 제안 상태이며 사용자 확정 전인 '삭제될 수 있는 문서'임.** 만약 삭제 시 위 두 테스트의 수정이 선행되어야 함.

#### (8) `structure.md`
- (가) 코드 읽기: 없음.
- (나) 테스트가 내용/존재 검사: 1건
  - `tests/test_scorecard_fix54_code.py:58`: `DocumentedLimitsTest.test_rc3_06_and_08_are_recorded()`에서 `(ROOT / "docs" / "scorecard" / "structure.md").read_text()`로 파일을 직접 열어 9절의 `| RC3-06 |`, `**소비 증명이 아니다.**`, `| RC3-08 |`, `accepted_kinds` 문구를 검사.
- (다) 문구 언급:
  - `AGENTS.md:7`: `구조 지침은 docs/scorecard/structure.md`.
  - `README.md:231`: `구조 지침은 docs/scorecard/structure.md`.
  - `.claude/agents/report-designer.md:6, 13`.
  - 규칙 JSON 4개 파일의 decisions 항목.

#### (9) `guide.md`
- (가) 코드 읽기: 없음.
- (나) 테스트 검사: 없음.
- (다) 문구 언급:
  - `README.md:39`: `docs/scorecard/guide.md 에 정리돼 있습니다.`

#### (10) 약칭 `S-RULE`, `S-HAND`, `S-SCORE`, `S-PLAN`, `S-AGENT`
- (가) 코드 읽기: 없음.
- (나) 테스트 검사: 1건
  - `tests/test_scorecard_impl50.py:85`: `design-guideline.md`의 C-11 행 내 `~~S-SCORE의 영업외 비중 설명은...` 문자열 존재 검사.
- (다) 문구 언급:
  - `docs/scorecard/design-guideline.md` 36~38행, 43~47행, 115행, 195행, 223행, 297행, 322행, 341행, 349행, 372행, 389행, 425행, 426행, 428행, 433행, 434행, 435행, 437행, 438행, 441행, 442행, 443행, 444행, 445행, 446행, 471행.

---

## Q7. 변경 순서와 테스트 영향

### 1. 반드시 고쳐야 하는 위치 목록
| 파일 경로 | 행 번호 | 분류 | 수정 이유 |
|---|---:|---|---|
| `server/approvals.js` | 39 | (다) | `RULES_DOC` 경로를 새 규칙 문서 경로로 갱신해야 함. |
| `server/approvals.js` | 40~50 | (가) | `GLOSSARY`의 별표 A~J를 새 규칙 체계의 용어로 개편해야 함. |
| `server/approvals.js` | 63, 67~77 | (나) | `TERM_RE` 정규식 및 링크 생성 로직이 새 규칙 용어를 매칭하도록 수정해야 함. |
| `scripts/scorecard/render_html.py` | 1122 | (가) | HTML factor 카드 서브타이틀 `'채점규칙 별표의 지표다.'`를 새 규칙 구조에 맞게 변경해야 함. |
| `scripts/scorecard/render_html.py` | 1023 | (가) | 감사 기록 표 설명 `'리포트 본문의 무엇을 보고 매기는가는 채점규칙 별표에서 가져온다'` 문구 갱신. |
| `scripts/scorecard/render_common.py` | 982 | (가) | `CREDIT_NOTE` 내 `'교차검증 지표다(별표 J)'` 문구 갱신. |
| `scripts/scorecard/render_common.py` | 1600 | (가) | 리포트 open tensions 요약 내 `'제3자 재검토 약속(채점규칙 384행)'` 행 번호 갱신. |
| `scripts/scorecard/render_md.py` | 359 | (가) | 초안 이해상충 고지 내 `'(채점규칙 384행 · HANDOVER 75행)'` 인용 문구 갱신. |
| `scripts/scorecard/stages.py` | 90, 92 | (가) | 새 실행의 `sources.json` 생성 시 삭제 예정인 v1.5 규칙 문서, HANDOVER 문서 및 옛 행 번호 인용 차단/대체. |
| `scripts/scorecard/calc_qual.py` | 142, 155 | (가) | 미결 판단 사유 문구 내 `'(별표 G)'`, `'(별표 I)'` 명칭 갱신. |
| `scripts/scorecard/calc_f9.py` | 152 | (가) | 계산 warnings 배열 내 `'(별표 D 388~390행)'` 인용 문구 갱신. |
| `scorecard/factor-concepts.json` | 20, 50, 56, 58, 96 | (가) | 리포트 HTML factor 카드로 노출되는 별표 A, D, G, H, I 문구 개편. |
| `tests/node/approvals.test.js` | 151, 155 | (라) | `server/approvals.js` 수정에 따라 실패하는 별표 F, 별표 G assertion 갱신. |
| `tests/node/fixtures/summary.sample.json` | 76 | (라) | 노드 승인 테스트 픽스처 내 별표 F 문구 갱신. |
| `tests/test_scorecard_fix76.py` | 109, 110 | (라) | `factor-concepts.json` 내 별표 제거 시 실패하는 `별표 A`, `별표 D` assertion 갱신. |
| `.claude/skills/score-collect/SKILL.md` | 38~51 | (다) | 에이전트 지침 내 `AI기업_채점규칙_v1.7.md` 및 별표 A~J 인용 갱신. |

### 2. 규칙 문서를 고치거나 삭제하면 실패할 테스트 목록
1. `tests/test_scorecard_fix52_docs.py` (21행)
   - 검사 내용: `docs/scorecard/design-guideline.md` 파일을 직접 읽어 F2, F6, F7, F9의 v1.7 밴드 표기 및 `[낡음 표시 2026-09-15 FIX-52]` 문자열을 검사함.
   - 실패 원인: `design-guideline.md`가 삭제되면 `FileNotFoundError` 발생. 내용 변경 시 `AssertionError` 발생.
2. `tests/test_scorecard_impl50.py` (83행)
   - 검사 내용: `docs/scorecard/design-guideline.md` 파일을 직접 읽어 C-11 결정 행의 취소선 및 `[낡음 2026-09-14 IMPL-50]` 문자열을 검사함.
   - 실패 원인: `design-guideline.md`가 삭제되면 `FileNotFoundError` 발생.
3. `tests/test_scorecard_fix76.py` (109~110행)
   - 검사 내용: `factor_criteria()`가 반환하는 F1, F4 기준 문구 내에 `"별표 A"`, `"별표 D"`가 존재하는지 검사함.
   - 실패 원인: `scorecard/factor-concepts.json`에서 별표 문자열을 제거하면 `AssertionError` 발생.
4. `tests/node/approvals.test.js` (151행, 155행)
   - 검사 내용: 승인 페이지 HTML 본문 내에 `<a class="term" ...>별표 F</a>` 링크 및 `<dt id="ref-star-G">별표 G</dt>`가 존재하는지 검사함.
   - 실패 원인: `server/approvals.js`의 `GLOSSARY` 및 `TERM_RE`에서 별표를 제거하면 `AssertionError` 발생.
5. `tests/test_rules_v18.py` (26~41행)
   - 검사 내용: `v1.7.json`의 SHA-256 해시가 고정값(`345c3353...`)과 같은지, `v1.8.json`의 내용이 `v1.7.json`과 지정된 차이점만 갖는지 검사함.
   - 실패 원인: `v1.7.json`이나 `v1.8.json`을 직접 수정하면 해시 불일치로 테스트 실패.
6. `tests/test_scorecard_fix59.py` (67~72행) 및 `tests/test_scorecard_fix62.py` (142~145행)
   - 검사 내용: `AI기업_채점규칙_v1.5.md` 파일이 존재할 경우 특정 행 번호(470, 494, 603, 390행)의 문구를 검사함.
   - 영향: 파일이 삭제되면 `is_file()`에 의해 검사가 건너뛰어지지만, 파일이 존재하는 상태에서 내용/행이 바뀌면 즉시 실패함.

### 3. 권장 변경 순서
1. **1단계: 규칙 문서 작성 및 새 규칙 버전(v1.9) 생성**
   - 새 규칙 문서를 작성하고(예: `AI기업_채점규칙_v1.9.md`), 행 번호와 항목별 절 구조를 확정합니다.
   - 기존 `v1.7.json`과 `v1.8.json`은 과거 실행의 불변성을 위해 직접 수정하지 않고, 새 규칙 문서의 구조와 정본 원칙을 반영한 `scorecard/rules/v1.9.json`을 신규 생성합니다.
2. **2단계: 공유 정의 및 승인 서버 갱신**
   - `scorecard/factor-concepts.json` 내 별표 언급을 새 규칙 용어로 갱신합니다.
   - `server/approvals.js`의 `GLOSSARY` 및 `TERM_RE`, `RULES_DOC`를 새 규칙 체계로 개편합니다.
   - `tests/node/approvals.test.js`와 `tests/node/fixtures/summary.sample.json`, `tests/test_scorecard_fix76.py`를 동시에 갱신합니다.
3. **3단계: 생성 및 렌더링 코드 갱신**
   - `scripts/scorecard/render_html.py`, `render_common.py`, `render_md.py`의 화면/초안 출력 고정 문구('채점규칙 별표의 지표다.', `CREDIT_NOTE` 등)를 갱신합니다.
   - `scripts/scorecard/stages.py`의 `_baseline_inputs`에서 새 실행의 `sources.json` 생성 시 새 규칙 문서를 가리키도록 수정합니다.
   - `scripts/scorecard/calc_qual.py`, `calc_f9.py`의 미결 및 경고 문구를 새 규칙 용어로 갱신합니다.
4. **4단계: 테스트 및 문서 삭제 영향 정리**
   - `design-guideline.md` 삭제가 사용자로부터 최종 확정되면, 해당 문서를 읽는 테스트(`test_scorecard_fix52_docs.py`, `test_scorecard_impl50.py`)의 검사 대상을 새 규칙 문서나 `structure.md`로 마이그레이션합니다.
   - `AI기업_채점규칙_v1.5.md` 및 `docs/scorecard/source/` 문서를 삭제하고, `baseline_import.py`의 기본 경로 의존성을 정리합니다.
5. **5단계: 상위 문서 및 스킬 지침 갱신**
   - `README.md` 및 `.claude/skills/score-collect/SKILL.md` 등의 문서 경로 참조를 새 규칙 문서로 갱신합니다.
   - `AGENTS.md`의 규칙 참조는 프로젝트 공통 규칙에 따라 `main` 브랜치에서 선별 반영한 뒤 머지합니다.
6. **6단계: 전체 테스트 및 신규 실행 검증**
   - `npm run test:node` 및 Python unittest 전체를 실행하여 회귀 오류가 없음을 확인합니다.

### 4. 확인하지 못한 것과 그 이유
1. `output/*/evidence/candidates.json`:
   - 지시서 규칙("검색에서 제외하는 폴더: candidates.json")에 따라 검색 대상에서 제외했습니다. 수집된 후보 원자료의 raw 텍스트에 포함된 별표나 행 번호는 집계에 포함되지 않았습니다.
2. `data/` 원문 캐시 및 `validation/*/_raw`:
   - 지시서 규칙에 따라 검색에서 제외했습니다.
3. `design-guideline.md`의 최종 삭제 확정 여부:
   - 조율자의 제안 상태이고 사용자 확정 전이므로, 확정 결과에 따른 단일 분기 처리를 확정하지 않고 양방향 영향(삭제 시 테스트 실패 위치 및 보존 시 유지 방안)으로 조사했습니다.
