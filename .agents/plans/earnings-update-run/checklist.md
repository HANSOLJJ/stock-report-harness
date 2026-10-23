# 실적 반영 실행 체크리스트

## 결정
- [x] D1 실행 종류 A
- [x] D2 가격 전부 새로
- [x] D3 범위는 자료가 정한다
- [x] D4 판단 나이 상한 120일
- [x] D5 리뷰 범위
- [x] 흐름 문서(guide.md mermaid·workflow.html) 커밋 01d7009
- [x] 계획 사용자 확인 (2026-10-22 "좋아")

## U1 규칙 v3.1
- [x] v3.1.json (v3.0 + policies.rejudge.update_runs)
- [x] schema.validate_rules 새 키 (`_validate_update_runs_policy`)
- [x] rules.md 머리말·2.9 (개정 이력 절은 없다 — 경위는 커밋에 남긴다)
- [x] 테스트: v3.0 해시 불변·v30full 확인 유효, v3.1 점수 규칙 동일, 문서 대조 (1,818개 통과)
- [x] 커밋
- [ ] 선언한 키의 소비자: price_refresh(U4 diff)·manual_check_forms(U3·U5)·나머지(U3) — 끝까지 읽는 코드가 없으면 뺀다

## U2 실행 선언
- [x] init --update-companies --update-reason (from-run 필수, add·companies 와 배타, v3.1 이상, 기준일은 이전보다 뒤, 가격일·컷오프는 물려받지 않음)
- [x] run.json continued_from.updated_companies, refreshed_at(v3.1 이상 모든 실행), update_scope{reason, extra}
- [x] validate_run, is_update_run, update_runs_policy, refreshed_here(set-as-of 도 갱신일을 옮긴다)
- [x] 리뷰 승계 예외는 기업 추가 실행에만 (실적 반영 실행도 막음)
- [x] 테스트 (test_update_run_init 18개 + test_v20_validate 1개, 전체 1,837개)
- [x] 커밋
- [ ] U4 에서: `_inputs_from_run` 의 규칙 변경 경고("층·사업 단위 규칙이라 diff 로 견주지 못하므로…")를 diff 지원에 맞게 고친다

## U3 범위 계산과 검사
- [x] update_scope.py (필수 판단, 추가 항목, 실적 감지, 나이). "새로 확정·발동"은 이전 실행의 같은 ID 와 견준다
- [x] 공시 후보에 items·report_period, 후보 파일에 회사별 공시 목록 수집 시각(filings_fetched_at)
- [x] rejudge_findings·research·계약 검증·previous_triggers 연결. 계약 검증은 범위 계산 예외를 오류 한 줄로 남긴다
- [x] v3.1 재판단 기준 강화: 이전 실행 판단과 내용이 다르고 검토·재확인일 ≥ 생성일 (v30full 판단이 기준일 뒤에 매겨져 옛 기준이 이어받기만 한 판단을 통과시키던 구멍)
- [x] scorecard_cli.py scope (+ --add), stages.declare_scope_extra, 잠금 단계·훅(scope --add 만 막음)
- [x] 테스트 (test_update_scope 21개, 훅 2건, 전체 1,858개)
- [x] 커밋 → 이정표 1 보고
- [ ] U6 에서: scripts/hooks/README.md 단계 목록에 scope --add

## U4 diff
- [x] 층 규칙 가드 해제 (v3.0 기업 추가 쌍을 견준다, 층 판단 수정을 1층이 잡는다)
- [x] 실적 반영 실행 모드: 갱신 회사 전부·범위 판단·모든 회사 가격 관측 허용, 범위 밖은 ⑥ 만 움직여도 됨, 이어받은 실행과만 견줌
- [x] init 의 규칙 변경 경고를 "판단 단위가 바뀐 실행"에만 diff 안내 제외로 고침
- [x] 테스트 (test_update_diff 8개, 전체 1,866개)
- [x] 커밋

## U5 출력
- [x] research.md 갱신 범위 절(범위 항목·회사별 마지막 전체 갱신일·리뷰가 확인할 6-K)
- [x] 초안 회사 제목·HTML 카드의 "반영 기준 YYYY-MM-DD", 개요·방법·감사 기록의 실적 반영 문장
- [x] history.csv change_type 은 init 이 earnings-update 로 적는다(U2)
- [x] 테스트 (test_update_render 4개, v30full 초안 바이트 불변, 전체 1,870개)
- [x] 커밋 → 이정표 2 보고

## 실제 실행 상황 (2026-10-22)
- 출력 폴더에 `ai-scorecard-2026-10-q3`(갱신 회사 alphabet·spacex-xai)를 만들고 공시 목록을 14개사 전부 받았다.
- 실적 감지: Meta 8-K 2.02(10-21), Tesla 8-K 2.02(10-21), SpaceX 8-K 2.02(10-20) 막힘, TSMC 6-K(10-15, 보고 기간 09-30) 리뷰 목록. Alphabet 은 EDGAR 에 아직 없다(마지막 실적 공시 07-22).
- 사용자 결정: Alphabet 공시가 잡힐 때까지 하루 기다렸다가 다섯(alphabet·spacex-xai·meta·tesla·tsmc)으로 진행한다. 내일 `collect --kind filings` 를 다시 받고 `init --force --update-companies` 로 다시 만든다.

## U6 리뷰·문서·스킬
- [x] score-review 실적 반영 실행 범위, score-diff 갱신
- [x] score-update 스킬
- [x] AGENTS.md(실행 세 종류·스킬 13개), guide.md(실행 종류 표·명령표·명세 표), structure.md(run.json 스키마·실적 반영 갈래·carried), hooks README(scope --add), workflow.html
- [x] .agents/skills 동기화
- [x] 커밋

## P 첫 실적 반영 실행
- [x] init (v30full → q3a, v3.1, 갱신 회사 spacex-xai·meta·tesla·tsmc, Alphabet 은 공시 전이라 제외)
- [x] 가격·공시 전부 수집, 뉴스·재무는 넷만, scope 통과(범위 58건 → 근거 확정 뒤 Alphabet ⑤⑧·Anthropic ⑤⑦⑧·Apple ⑧·NVIDIA ⑧ 포함)
- [x] 1단계(Sonnet 넷 병렬, 조각 → merge.py) → 근거 137건 확정
- [x] 2단계 판단 세션(Opus high 다섯, judge_spec → apply.py) 58건 + SpaceX 후속 2건
- [x] research → calculate → draft → diff 통과(범위 밖은 ⑥ 만 변화)
- [x] 리뷰 (D5 범위) 네 영역 → 수정 한 묶음(⑨ 4, TSMC 문장 9, ⑤ 5 + Apple ⑤ scope --add, 근거 5, 가격 10-22) → 확인 리뷰 pass, 계약 검증 전 항목 ok
- [x] 확인 대기 보고 → 이정표 3 보고
- [x] 10-22 종가로 가격 다시 받기(14개사 벤더 시가총액, TSMC·Alibaba 해소)
- [x] 사람이 확인 페이지에서 확인(10-23 12:14) → 빌드 → HTML 검증(--require-html) 전 항목 ok → 커밋 8c737f8 → main push → 맥미니 pull → https://fin.hansoljj.com/reports/ai-scorecard-2026-10-q3a/ 200
- [ ] 기존 `output/ai-scorecard-2026-10-q3` 폴더(untracked, 첫 선언) 정리는 사용자에게 묻는다

## q3b: ⑤ 받은 투자 절충안 적용 (2026-10-23)
- [x] rules.md ⑤ 절충안(367f7f5)·좁은 헤지 읽기(553186f)
- [x] init q3b(갱신 회사 anthropic·openai) → 공시 전부·뉴스 둘 수집 → scope 범위 18건
- [x] 판단 세션 Opus 둘 + 트리거·후보 Sonnet → 근거 16건 확정, 트리거 29건 carry + 새 4건
- [x] 적용: anthropic 9(⑤ 는 좁은 읽기 후속), openai 9 → research·calculate·draft·diff 통과(Anthropic ⑤ 4→7, 나머지 불변)
- [x] 리뷰 4영역 띄움. 재무·출력 pass(발견: TRG-163 문장, EV-172·165·169 문장, 개요 문구 → 고침)
- [ ] 사실·규칙 리뷰 보고 → 수정 묶음 → 10-24 아침 가격(10-23 종가) → research·calculate·draft → 확인 리뷰 → review.md pass → 확인 대기 → 빌드·배포
