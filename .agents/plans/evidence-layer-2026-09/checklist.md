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
- [ ] 레인 S (Sonnet) 디스패치 완료 → 검증 → 병합. task `task_0d621b4175f7`, dispatch `ctx_ebddd407600b`, 워크트리 `…/lane-S`, 터미널 `term_2aefbd6b-2029-4088-af26-7151e665f394`
- [ ] 레인 B (Muse) 디스패치 완료 → 검증 → 병합. task `task_4e19dbd18cc4`, dispatch `ctx_f2bafe443416`, 워크트리 `…/lane-B`, 터미널 `term_863653f9-0bf1-44ae-a2ab-9dbc77faa543` (turn_started 관측 불가 에이전트)
- [ ] 레인 C (Sonnet) 디스패치 완료 → 검증 → 병합 → 조율자가 output-spec 문서 삭제. task `task_ece7f8798677`, dispatch `ctx_e00fb51c41a0`, 워크트리 `…/lane-C`, 터미널 `term_fd89feaf-abfe-4e5a-8a0a-dcd173956894` (첫 시도는 조율자 훅이 spec 안의 보호 경로 문구와 꺾쇠를 차단해 재시도)
- [ ] 레인 D (Antigravity) 디스패치 완료 → 검증 → 병합. task `task_d12890631f47`, dispatch `ctx_f43a7972fc93`, 워크트리 `…/lane-D`, 터미널 `term_76969e8e-cff7-4d73-8d1c-4f2c82998c81`
- [ ] 레인 A (Opus) 디스패치(S 의 1.2 병합 뒤) → 검증(해시 보존은 조율자 직접) → 병합
- [ ] 후속 직렬(Opus): 3.1 → 3.4 → 4.2 → 4.3 지시서 작성·디스패치(A·B 병합 뒤)
- [ ] 문서(Sonnet): 4.5 → 4.6

## 1단계 정리·재활용
- [ ] 1.1 stock-research 문구 → score-collect 초안, content-editor → evidence-editor (레인 S)
- [ ] 1.2 종목 파일 git rm (훅 파일 제외) (레인 S)
- [ ] 1.3 build_report·validate_report_contract·report_contract_lib 축소 (레인 A)
- [ ] 1.4 AGENTS·README·memory-system 종목 서술 제거 (레인 S)

## 2단계 묶음 배치 (레인 A)
- [ ] 2.1 scripts/scorecard/paths.py, engine/stages/render/validate 경로 통일
- [ ] 2.2 기존 실행 2개 output/<id>/ 이동 + .gitattributes 동시 갱신 → status approval_valid true 확인
- [ ] 2.3 테스트 49개 경로, server.js 경로 함수, 훅 매핑
- [ ] 2.4 sync_outputs.py 제거

## 3단계 근거 계층
- [ ] 3.1 schema: validate_sources/evidence/triggers/cross_refs, companies cik·news_queries (후속 Opus)
- [ ] 3.2 rules v1.8: sources 블록 제거 (레인 B)
- [ ] 3.3 evidence_lib·collect_news·collect_filings·collect_prices·resolve-cik + 픽스처 (레인 B)
- [ ] 3.4 stages.collect, research 근거 등록·렌더, 해시 결속 (후속 Opus)

## 4단계 훅·승인·스킬
- [ ] 4.1 scripts/hooks/guard.py + tests/test_hooks.py + 배선(Claude·Codex) + PowerShell 매처 + remind-review 경고화 + output-spec 보호 해제 (레인 C)
- [ ] 4.2 approve 명령·approval.json·이동 실행 폴더·규칙 파일·history.csv 보호(protect 목록 확대), 잠금 파일, approve CLI 의 에이전트 환경변수 거부 (후속 Opus, A 병합 뒤)
- [ ] 4.3 summary·confirm·approve --via·revoke 명령 (후속 Opus)
- [ ] 4.4 server.js --approvals 승인 페이지 (레인 D)
- [ ] 4.5 score-collect 완성, score-* 개정, 리뷰어 에이전트 재작성 (Sonnet)
- [ ] 4.6 AGENTS·README·structure.md 반영 (Sonnet)
- [ ] (운영) Antigravity·Muse 배선: 차단 표현·필드 이름·작업 디렉터리 확인 뒤

## 사용자 준비 항목
- [ ] SEC_UA 환경변수
- [ ] SPCX CIK 확인 (1181412 후보)
