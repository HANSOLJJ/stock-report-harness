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
- [ ] 3.4: SEC 픽스처 2종은 합성. `SEC_UA` 확보 뒤 실제 응답으로 교체
- [x] 3.4 또는 A 병합 뒤: yfinance import 고정 테스트 범위를 `scripts/scorecard` 에서 `scripts/` 전체로 넓힌다(A 가 build_report 의 yfinance 를 지운 뒤)
- [x] 4.3: `confirm`·`approve`·`revoke` 가 근거 ID(`EV-<cid>-<NNN>`)·이름 형식을 Python 쪽에서 검증. 승인 페이지 일회용 코드는 시도 횟수 제한 없음(루프백 한정이라 낮음) — 실패 5회면 서버 종료 검토
- [ ] 4.6: README 훅 표(`protect-sensitive-files.sh` 등 옛 이름·output-spec) 갱신. AGENTS 에서 레인 S 가 지운 "plan 없이 research 금지 / review 없이 build 금지" 는 채점표에도 맞는 일반 규칙이므로 채점표 단계 이름으로 되살린다
- [ ] baseline 실행 recompute 불일치(amazon·oracle·openai F9 calc 경로 기록)는 원본 폴더에서도 같은 기존 상태. 별도 과제로 원인 기록 여부 결정
- [x] 후속 직렬(Opus): 3.1·3.4 는 레인 E 로 디스패치(task `task_886a8483f9d2`, dispatch `ctx_ef9a127fce02`, 터미널 `term_ceb10bfe-fbe6-4320-aaa3-a59083939d17`). 4.2 → 4.3 은 E 병합 뒤
- [ ] 문서(Sonnet): 4.5 → 4.6

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
- [ ] 4.5 score-collect 완성, score-* 개정, 리뷰어 에이전트 재작성 (Sonnet)
- [ ] 4.6 AGENTS·README·structure.md 반영 (Sonnet)
- [ ] (운영) Antigravity·Muse 배선: 차단 표현·필드 이름·작업 디렉터리 확인 뒤

## 사용자 준비 항목
- [ ] SEC_UA 환경변수
- [ ] SPCX CIK 확인 (1181412 후보)
- [ ] 옛 obsreg `report.html` 은 감사 기록 링크가 `<slug>-audit.md` 라 묶음에서 깨진다. 승인이 유효하므로 빌드를 다시 돌리면 `audit.md` 링크로 재생성된다(사용자 확인 뒤)
- [ ] 남은 unittest 15건은 `validation/f6-avail-15/_raw` 등 원자료가 워크트리에 없어서 난다. main 병합 뒤 원본 폴더에서 전부 통과하는지 확인
- [x] 레인 E 조율자 재현(병합 뒤): 두 실행 approval_valid true, recompute obsreg True·baseline 기존 값 불변, output/·scorecard/ 변경 0, unittest 1030건 중 실패 1·오류 14(원자료 부재 집합과 동일), node 9·check 통과
- [x] 4.3: 초안(`render_draft`)과 HTML 의 트리거 절이 `triggers.json` 이 있으면 그것을 그리게 한다(지금은 research 만). 계획 3단계 "렌더러는 이 파일이 있으면 legacy 39건 대신 그린다"
- [ ] baseline 은 기존 recompute 불일치로 재빌드가 멈춘다(승인 검사는 통과). 감사 링크 재빌드는 obsreg 만 해당
- [x] 레인 F (Opus) 4.2·4.3 디스패치 완료 → 검증 → 병합. task `task_c39a130db79b`, dispatch `ctx_3a3d42bdc422`, 워크트리 `…/lane-F`, 터미널 `term_6d0d6fec-989e-4175-b8e9-bafee8ff8ff0`
- [x] 레인 F 조율자 재현(병합 뒤): 두 실행 approval_valid true, output/·scorecard/ 변경 0, summary 계약 키 일치, unittest 1085건 중 실패 1·오류 14(원자료 부재 집합), node 10·check 통과, 훅 스모크에서 승인 명령(PowerShell)·승인 파일 쓰기·이동 실행 수정·v1.7 수정 모두 exit 2, confirm 통과
- [ ] 4.5·4.6: 터미널 승인 명령 안내가 남은 곳(score-approve 스킬, README, build 의 awaiting_user 메시지)을 승인 페이지 안내로 바꾼다
- [ ] PowerShell cmdlet(Set-Content·Remove-Item·Out-File) 변경은 보호 훅의 _MUTATING 에 없어 지나간다. 리다이렉션은 잡는다. 별도 과제
- [ ] baseline 초안 재렌더는 render_common.method_sections 가 v1.5(bands) 실행에서 KeyError. obsreg 초안도 지금 코드로 다시 렌더하면 네 줄이 달라진다(저장본은 승인본이라 그대로 둔다)
- [ ] 에이전트 표지 환경변수는 Claude Code 세션 하나만 조사했다. Codex·Antigravity·Muse 세션은 운영 단계 배선 때 확인
