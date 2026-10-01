# 체크리스트 — 근거 수집 계층 도입 (2026-09-30 시작)

계획: `plan.md`. 결정 기록: `context-notes.md`. 통합 브랜치 `HANSOLJJ/revision_checker`.

## 0단계 환경·위생 (조율자 직접)
- [x] 0.1 uv 전환: pyproject.toml, .python-version, uv.lock, package.json, memory 훅 2개 (커밋 308ead4)
- [x] 0.2 memory validator 오류 3건 수정 (커밋 620f0ab)
- [x] 0.4 .agents/plans 3종 생성
- [x] 테스트 기준선: 원본 폴더 866건 OK. 이 워크트리는 757건 실행·실패 7·오류 30(plan/·drafts/ 부재). 2.2 이동 커밋 뒤 여기서도 전부 통과해야 함. 목록 `dispatch/baseline-failures.txt`
- [x] 0.5 워커 지시서 5종(`dispatch/lane-{S,A,B,C,D}.md`)과 공통 규약 `dispatch/README.md`. `.agents/plans/` 추적, `data/`·`node_modules/` 무시, `tests/fixtures/** -text`

## 디스패치 현황 (Orca orchestration)
- Run id: `run_f124df1dad47` (2026-09-30 17:03 KST). 조율자 handle `term_be1eaaf8-815c-4231-a858-7229d925e5fe`
- [x] 레인 S (Sonnet) 디스패치 완료 → 검증 → 병합. task `task_0d621b4175f7`, dispatch `ctx_ebddd407600b`, 워크트리 `…/lane-S`, 터미널 `term_2aefbd6b-2029-4088-af26-7151e665f394`
- [x] 레인 B (Muse) 디스패치 완료 → 검증 → 병합. task `task_4e19dbd18cc4`, dispatch `ctx_f2bafe443416`, 워크트리 `…/lane-B`, 터미널 `term_863653f9-0bf1-44ae-a2ab-9dbc77faa543` (turn_started 관측 불가 에이전트)
- [x] 레인 C (Sonnet) 디스패치 완료 → 검증 → 병합 → 조율자가 output-spec 문서 삭제. task `task_ece7f8798677`, dispatch `ctx_e00fb51c41a0`, 워크트리 `…/lane-C`, 터미널 `term_fd89feaf-abfe-4e5a-8a0a-dcd173956894` (첫 시도는 조율자 훅이 spec 안의 보호 경로 문구와 꺾쇠를 차단해 재시도)
- [x] 레인 D (Antigravity) 디스패치 완료 → 검증 → 병합. task `task_d12890631f47`, dispatch `ctx_f43a7972fc93`, 워크트리 `…/lane-D`, 터미널 `term_76969e8e-cff7-4d73-8d1c-4f2c82998c81`
- [x] 통합 브랜치 재현(S·C·D·B 병합 뒤): unittest 859건, 실패·오류 집합 기준선과 동일. node 9건 통과. npm run check 통과
- [x] 레인 A 조율자 재현(병합 뒤 checkout 파일): 원본 폴더 대비 12개 파일 sha256 일치, 두 실행 `approval_valid: true`, recompute obsreg True·baseline 기존 False 유지, unittest 974건 중 실패 1·오류 14(전부 `validation/f6-avail-15/_raw` 등 원자료 부재, 원본 폴더에는 있음), node 9 통과
- [x] 레인 A (Opus) 디스패치 완료 → 검증(해시 보존은 조율자 직접) → 병합. task `task_fd767d2777a0`, dispatch `ctx_9dfd3e4490c9`, 워크트리 `…/lane-A`, 터미널 `term_92109605-09f8-401a-b004-8fab6fcc3879`. 완료 조건 정정 메시지 `msg_2161aab10d56`(baseline recompute 는 기존 불일치)

## 후속 과제에 넣을 발견 사항 (레인 검증 중)
- [x] 3.4: `collect_prices` 의 vendor market_cap·shares_outstanding 은 조회 시점 값인데 종가 날짜(as_of)로 기록된다. 과거 기준일이면 dated 발행주식수로 price×shares 를 쓰거나 조회일=기준일일 때만 vendor 값 사용. ADR(TSM·BABA) 시총 기준 확인. 미사용 인자 `price_as_of` 정리
- [x] 3.4: SEC 픽스처 2종은 합성 — 레인 M 이 실응답으로 교체. `SEC_UA` 확보 뒤 실제 응답으로 교체
- [x] 3.4 또는 A 병합 뒤: yfinance import 고정 테스트 범위를 `scripts/scorecard` 에서 `scripts/` 전체로 넓힌다(A 가 build_report 의 yfinance 를 지운 뒤)
- [x] 4.3: `confirm`·`approve`·`revoke` 가 근거 ID(`EV-<cid>-<NNN>`)·이름 형식을 Python 쪽에서 검증. 승인 페이지 일회용 코드는 시도 횟수 제한 없음(루프백 한정이라 낮음) — 실패 5회면 서버 종료 검토
- [x] 4.6: README 훅 표(`protect-sensitive-files.sh` 등 옛 이름·output-spec) 갱신. AGENTS 에서 레인 S 가 지운 "plan 없이 research 금지 / review 없이 build 금지" 는 채점표에도 맞는 일반 규칙이므로 채점표 단계 이름으로 되살린다
- [x] baseline 실행 recompute 불일치 — 그대로 두기로(차이는 설명 기록 3곳, 점수 동일)(amazon·oracle·openai F9 calc 경로 기록)는 원본 폴더에서도 같은 기존 상태. 별도 과제로 원인 기록 여부 결정
- [x] 후속 직렬(Opus): 3.1·3.4 는 레인 E 로 디스패치(task `task_886a8483f9d2`, dispatch `ctx_ef9a127fce02`, 터미널 `term_ceb10bfe-fbe6-4320-aaa3-a59083939d17`). 4.2 → 4.3 은 E 병합 뒤
- [x] 문서(Sonnet): 4.5 → 4.6

## 1단계 정리·재활용
- [x] 1.1 stock-research 문구 → score-collect 초안, content-editor → evidence-editor (레인 S)
- [x] 1.2 종목 파일 git rm (훅 파일 제외) (레인 S)
- [x] 1.3 build_report·validate_report_contract·report_contract_lib 축소 (레인 A)
- [x] 1.4 AGENTS·README·memory-system 종목 서술 제거 (레인 S)

## 2단계 묶음 배치 (레인 A)
- [x] 2.1 scripts/scorecard/paths.py, engine/stages/render/validate 경로 통일
- [x] 2.2 기존 실행 2개 output/<id>/ 이동 + .gitattributes 동시 갱신 → status approval_valid true 확인
- [x] 2.3 테스트 49개 경로, server.js 경로 함수, 훅 매핑
- [x] 2.4 sync_outputs.py 제거

## 3단계 근거 계층
- [x] 3.1 schema: validate_sources/evidence/triggers/cross_refs, companies cik·news_queries (후속 Opus)
- [x] 3.2 rules v1.8: sources 블록 제거 (레인 B)
- [x] 3.3 evidence_lib·collect_news·collect_filings·collect_prices·resolve-cik + 픽스처 (레인 B)
- [x] 3.4 stages.collect, research 근거 등록·렌더, 해시 결속 (후속 Opus)

## 4단계 훅·승인·스킬
- [x] 4.1 scripts/hooks/guard.py + tests/test_hooks.py + 배선(Claude·Codex) + PowerShell 매처 + remind-review 경고화 + output-spec 보호 해제 (레인 C)
- [x] 4.2 approve 명령·approval.json·이동 실행 폴더·규칙 파일·history.csv 보호(protect 목록 확대), 잠금 파일, approve CLI 의 에이전트 환경변수 거부 (후속 Opus, A 병합 뒤)
- [x] 4.3 summary·confirm·approve --via·revoke 명령 (후속 Opus)
- [x] 4.4 server.js --approvals 승인 페이지 (레인 D)
- [x] 4.5 score-collect 완성, score-* 개정, 리뷰어 에이전트 재작성 (Sonnet)
- [x] 4.6 AGENTS·README·structure.md 반영 (Sonnet)
- [ ] (운영) Antigravity·Muse 배선: 차단 표현·필드 이름·작업 디렉터리 확인 뒤

## 사용자 준비 항목
- [x] SEC_UA 환경변수 (원본 폴더 루트 로컬 설정 파일, 2026-10-01)
- [ ] SPCX CIK 확인 (1181412 후보)
- [ ] 옛 obsreg `report.html` 은 감사 기록 링크가 `<slug>-audit.md` 라 묶음에서 깨진다. 승인이 유효하므로 빌드를 다시 돌리면 `audit.md` 링크로 재생성된다(사용자 확인 뒤)
- [x] 남은 unittest 15건은 `validation/f6-avail-15/_raw` 등 원자료가 워크트리에 없어서 난다. main 병합 뒤 원본 폴더에서 전부 통과하는지 확인
- [x] 레인 E 조율자 재현(병합 뒤): 두 실행 approval_valid true, recompute obsreg True·baseline 기존 값 불변, output/·scorecard/ 변경 0, unittest 1030건 중 실패 1·오류 14(원자료 부재 집합과 동일), node 9·check 통과
- [x] 4.3: 초안(`render_draft`)과 HTML 의 트리거 절이 `triggers.json` 이 있으면 그것을 그리게 한다(지금은 research 만). 계획 3단계 "렌더러는 이 파일이 있으면 legacy 39건 대신 그린다"
- [ ] baseline 은 기존 recompute 불일치로 재빌드가 멈춘다(승인 검사는 통과). 감사 링크 재빌드는 obsreg 만 해당
- [x] 레인 F (Opus) 4.2·4.3 디스패치 완료 → 검증 → 병합. task `task_c39a130db79b`, dispatch `ctx_3a3d42bdc422`, 워크트리 `…/lane-F`, 터미널 `term_6d0d6fec-989e-4175-b8e9-bafee8ff8ff0`
- [x] 레인 F 조율자 재현(병합 뒤): 두 실행 approval_valid true, output/·scorecard/ 변경 0, summary 계약 키 일치, unittest 1085건 중 실패 1·오류 14(원자료 부재 집합), node 10·check 통과, 훅 스모크에서 승인 명령(PowerShell)·승인 파일 쓰기·이동 실행 수정·v1.7 수정 모두 exit 2, confirm 통과
- [x] 4.5·4.6: 터미널 승인 명령 안내가 남은 곳(score-approve 스킬, README, build 의 awaiting_user 메시지)을 승인 페이지 안내로 바꾼다
- [ ] PowerShell cmdlet(Set-Content·Remove-Item·Out-File) 변경은 보호 훅의 _MUTATING 에 없어 지나간다. 리다이렉션은 잡는다. 별도 과제
- [ ] baseline 초안 재렌더는 render_common.method_sections 가 v1.5(bands) 실행에서 KeyError. obsreg 초안도 지금 코드로 다시 렌더하면 네 줄이 달라진다(저장본은 승인본이라 그대로 둔다)
- [ ] 에이전트 표지 환경변수는 Claude Code 세션 하나만 조사했다. Codex·Antigravity·Muse 세션은 운영 단계 배선 때 확인
- [x] 레인 G (Sonnet) 4.5·4.6 디스패치 완료 → 검증 → 병합. task `task_39b14e9bae11`, dispatch `ctx_2e2d5d341c32`, 워크트리 `…/lane-G`, 터미널 `term_ef689690-3b13-42c5-b514-5d9caea97241`
- [x] 최종 통합 재현(레인 G 병합 뒤): 두 실행 approval_valid true, unittest 1085건 중 실패 1·오류 14와 pytest 실패 15(전부 원자료 부재 같은 집합), node 10·check·validate:memory 통과, 소유 문서 옛 경로 0건, 에이전트 승인 지시 문구 0건
- [x] main 병합과 fork push — main 병합 완료(2026-10-01, fast-forward 1d574e5). push 는 미실시 (사용자 확인 뒤)
- [x] 레인 V (Fable) 독립 검증 완료·보고서 병합. 새 결함 7건(medium 3: init --force 가 승인 실행 파괴, 승인 거부가 CLI 계층에만 있어 stages 함수 import 로 우회, scorecard/baseline 이 승인 해시·보호 밖 재빌드 입력 / low 4: locale 매핑, CLI 다음 안내·plan 템플릿 흐름·python 접두, 문서 드리프트, 읽기 전용 명령 오탐). 하드 블록 없음
- [x] 레인 V 발견 F-1~F-7 수정 여부 사용자 결정 — 전부 수정(2026-10-01)
- [x] 레인 H (Opus) F-1·F-2·F-3·F-4·F-7. task `task_bbe840d2d970`, dispatch `ctx_0cde83d7b3e9`, 터미널 `term_519514ec-7c3f-4b70-98b7-32d37d11bf53`
- [x] 레인 I (Sonnet) F-5·F-6. task `task_6070a52b7d13`, dispatch `ctx_0be5f663c395`, 터미널 `term_d194302d-eb6a-4258-9e23-04611838551a`
- [x] 레인 I 조율자 재현(병합 뒤): unittest 1093건 중 실패 1·오류 14(원자료 부재 집합), check 통과
- [ ] open-items D-06(python 표기 혼용)은 npm 스크립트·훅이 모두 uv 로 통일돼 사실상 해소. 닫을지 사용자 확인
- [x] SEC_UA: 사용자가 원본 폴더 루트 로컬 설정 파일에 기입(2026-10-01), 워크트리에서 원본 루트를 읽도록 코드 보완. 값은 기록하지 않음
- [x] 레인 M (Muse) 실제 수집 시험·SEC 실응답 픽스처·환경변수 조사. task `task_b1a5b14fe556`, dispatch `ctx_d49bf5bd9724`, 터미널 `term_e1a0a173-83e2-434d-8729-da4d294496a9`
- [x] 레인 H 조율자 재현(병합 뒤): unittest 1115건 중 실패 1·오류 14(원자료 부재 집합), 두 실행 approval_valid true, check·node 10 통과. 훅 스모크: 승인 실행 init --force·baseline 쓰기·승인 파일 쓰기·python 승인 파일 쓰기 exit 2, 새 slug init --force·승인 파일 읽기 exit 0
- [ ] 레인 H 가 남긴 것: 소유 밖 문서(AGENTS·README·structure.md)의 첫 방어선 위치 문구, render_md.py 130행 uv 없는 python, validation/recheck_worker_final.py 의 승인 함수 호출, 계약 밖 쓰기 형태(PowerShell cmdlet·find -delete·xargs·글롭)
- [x] 레인 M 조율자 재현(병합 뒤): unittest 1115건 중 실패 1·오류 14(원자료 부재 집합, Muse 가 본 훅 배선 2건은 Muse 환경의 bash 에 uv 가 없어서 생긴 것으로 이 환경에서는 통과), 보고서·픽스처에 연락처 없음
- [x] 실제 수집 재시도(조율자, 임시 DATA_ROOT): SEC_UA 영문화 뒤 뉴스 14개사 99~200건 수집·발행일 결측 0, SEC company_tickers 조회 성공(SPCX 1181412 등재). 가격은 9/29 기준 12개사 정상, 9/30 은 야후 일봉 종가 미확정(NaN)
- [x] 레인 J: 판단 수정 기능 (task `task_ae3a1a74216f`, dispatch `ctx_79ab07e8848b`, 터미널 `term_8c16cca4-3da4-4158-a9aa-4c535c8a3ec7`) + 수집기 수정(NaN 종가·회사별 실패·resolve-cik --json·SEC_UA 영문 검사·일반 단어 회사 news_queries·CIK 기입) + 정리(훅 쓰기 형태·render_md 130행·Muse 표지)
- [ ] 레인 K: 문서(첫 방어선 위치 문구, 판단 수정 사용법)
- [x] 레인 J 조율자 재현(병합 뒤): unittest 1146건 중 실패 1·오류 14(원자료 부재), 두 실행 approval_valid true·recompute 불변, companies.json 변경은 12개사 cik 와 meta·oracle·apple news_queries 뿐, check·node 15 통과
- [x] 레인 K (Sonnet) 문서. dispatch `ctx_a06adb492d13`, 터미널 `term_5ae329e4-4d55-4d61-855f-dea7ace943c6`
- [x] 레인 L (Muse) 근거 평가 표본. dispatch `ctx_b79e5dabdabb`, 터미널 `term_c3babed2-dcd6-4cac-8201-c0e64d8e6a5c` (기동 뒤 붙여넣기로 멈춰 조율자가 Enter 별도 전송)
- [x] 레인 T (Antigravity) 원자료 테스트 건너뛰기. dispatch `ctx_969631797a3d`, 터미널 `term_4294af58-662b-4bef-8e31-d77deae20a0c`
- [x] 끝난 레인 워크트리 13개(S·A·B·C·D·E·F·G·V·H·I·M·J) 정리: 병합 안 된 커밋 0·미커밋 파일 0 확인, 사용자 확인 대기
- [x] 레인 K 병합. score-research 스킬의 judge 안내는 지시서 소유 목록 누락이라 조율자가 보완
- [x] README 「지금 상태」 표(테스트 797건, 재승인 대기)가 2026-09-21 값이라 낡음. 마지막 레인(T·L) 병합 뒤 실제 수치로 갱신
- [x] 레인 T 병합: 테스트 파일 변경은 import 와 require_raw 데코레이터 추가뿐(지운 줄 0). unittest 1146건 OK(건너뛰기 13), pytest 1133 통과·13 건너뛰기. 워크트리에서 처음으로 전부 통과
- [x] 레인 L 병합: 라벨 시트 38건(14개사 2~3건, 관련 없음 제안 15건, 라벨 칸 비어 있음, 위험 표현 0). unittest 1146건 OK(건너뛰기 13)
- [ ] 사용자: tests/fixtures/evidence/labeling-2026-10.csv 라벨 작성(correct·wrong·irrelevant)
- [x] 끝난 레인 16개(S·A·B·C·D·E·F·G·V·H·I·M·J·K·T·L) 워크트리 삭제(2026-10-01, 사용자 지시). orca worktree rm 이 브랜치까지 지워, 병합 커밋의 둘째 부모로 16개 브랜치를 되살림(워커 보고 SHA 와 일치)
- [x] 레인 V2 (Fable) 독립 재검증 완료·보고서 병합. 첫 검증 F-1~F-7 해소(F-3 일부). 새 발견 13건(medium 4: V2-1 단계 명령이 승인 실행의 승인을 무효·삭제, V2-2 근거 인용 판단의 이어받기 실패, V2-3 대소문자 다른 승인 파일 이름, V2-4 보호 훅 재작성 뒤 변수·중첩 셸 쓰기 통과 / low 9). 하드 블록 없음. 병합 전 권고 V2-1·V2-4·V2-2, V2-3 함께
- [x] 레인 V2 발견 수정 범위 사용자 결정 — V2-1~V2-4 는 Opus(레인 N), V2-5 문서는 Antigravity(레인 P), 나머지 low 는 병합 뒤
- [x] 레인 N (Opus) V2-1~V2-4. dispatch `ctx_2a662c2cf922`, 터미널 `term_5e9bbb89-be9c-4dbe-a24f-d8c757f344c8`
- [x] 레인 P (Antigravity) V2-5 문서. dispatch `ctx_85c30b73f736`, 터미널 `term_ad8d68ca-079e-4b2a-837c-9b8d93403e3e`
- [ ] 레인 V2 low 나머지(V2-6~V2-13)는 main 병합 뒤 별도 과제
- [x] 레인 P 병합: 문서·스킬 9곳 재실행 순서 수정, 조율자 재검색으로 open-items 54행 1곳 추가 수정(소유 목록 누락)
- [x] 레인 N 조율자 재현(병합 뒤): unittest 1168건 OK(건너뛰기 13), 두 실행 approval_valid true·recompute 불변, check·node 15 통과. 훅 스모크: 승인 실행 calculate·judge, 대문자 승인 파일 쓰기, 변수·bash -c·PowerShell 변수 쓰기 모두 exit 2. 미승인 실행 calculate·승인 파일 읽기는 통과. 조율자 세션 훅도 보호 경로를 담은 python 명령을 막음(규칙 작동 확인)
- [ ] main 병합 뒤 별도 과제: 레인 V2 low(V2-6~V2-13), 레인 N 소유 밖 발견 4건(build_report 의 SchemaError 추적 출력, baseline_import 본체 무검사, compare.approval_state 가 임의 approval_id 에 diff 전체 실패, init --force 승인 삭제 미기록)과 훅의 경로 조각 결합 한계
- [x] 원본 폴더 정리(사용자 지시): plan·drafts·output 의 중복 사본과 옛 빌드, Ciena 종목 산출물 19개, backup/2026-09-21-integrate(57개), .omx, docs/개선점.md 삭제. memory_context.py 서식 수정분은 패치로 보관 뒤 되돌림
- [x] 원본 폴더 main 병합 뒤 검증: 두 실행 approval_valid true, unittest 1168건 OK(건너뛰기 0, 원자료 테스트까지 실행), pytest 1168 통과, check·node 15·validate:memory 통과
- [ ] fork(origin) main push — 사용자 확인 대기. Orca 새 워크트리는 origin/main 기준이라 push 해야 다음 워크트리가 이번 결과에서 시작
