# 레인 T — 원자료 없는 테스트 15건을 실패 대신 사유 있는 건너뛰기로

에이전트: Antigravity. 의존: 레인 J 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. 레인 K(문서)·L(`tests/fixtures/evidence/`)이 동시에 일한다. 소유가 겹치지 않는다. **판단 과제가 아니라 기계적 변경이다. 테스트가 검사하는 내용은 바꾸지 않는다.**

## 배경

워크트리에서 unittest 1146건 중 실패 1·오류 14 가 늘 난다. 전부 gitignore 되지 않았지만 커밋되지도 않은 원자료(`validation/*/_raw/…`, 예: `validation/f6-avail-15/_raw/*.companyfacts.json`)가 워크트리에 없어서 난다. 원본 폴더에는 그 파일이 있어 거기서는 통과한다. 워커마다 "기준선 15건" 을 따로 설명해야 하는 비용을 없앤다.

대상(지금 실패·오류 목록): `tests/test_scorecard_fix54_obs.py`, `test_scorecard_fix55_stage2.py`, `test_scorecard_fix57_stage1.py`, `test_scorecard_fix58_stage1.py`, `test_scorecard_fix58_stage2.py`, `test_scorecard_obs_recency.py` 의 해당 테스트. 먼저 전체 테스트를 돌려 정확한 목록을 확인한다.

## 할 일

1. 각 실패·오류 테스트가 읽는 원자료 경로를 코드에서 찾는다.
2. 그 경로가 없을 때만 건너뛰게 한다. `unittest.skipUnless(<경로>.exists(), "원자료 없음: <상대경로> (원본 폴더에서만 실행)")` 를 테스트 함수나 클래스에 붙인다. 공통 도우미가 필요하면 `tests/_raw.py` 하나에 `require_raw(*paths)` 같은 함수로 둔다(첫 줄 한국어 주석).
3. 원자료가 있으면 지금과 똑같이 실행되어야 한다. 단언·기대값·테스트 순서를 바꾸지 않는다.
4. `load_facts` 가 None 을 돌려 실패하는 1건(`test_broad_tag_sweep_finds_only_tesla`)도 원인이 원자료 부재인지 확인하고 같은 방식으로 처리한다. 원자료 부재가 아니면 고치지 말고 보고서에 적는다.

## 소유 파일

위 테스트 파일들과 새 `tests/_raw.py`(필요 시), 보고서. `scripts/**`·문서·그 밖의 테스트는 고치지 않는다.

## 검증

- 이 워크트리에서 unittest 결과가 "실패 0·오류 0·건너뛰기 5+15 안팎" 이 된다. 건너뛴 테스트 목록과 사유를 보고서에 붙인다.
- 원자료가 있을 때 실행되는지 확인한다. 원본 폴더(`E:/sourcecode/01_side_project/stock-report-harness`)의 `validation/f6-avail-15/_raw` 같은 파일을 **읽기만** 해서 이 워크트리의 임시 위치에 복사하지 말고, 대신 원자료 경로를 임시로 만든 가짜 파일로 채운 경우 skip 이 풀리는지 한 테스트로 확인한다(가짜 파일은 테스트가 끝나면 지운다). 원본 폴더에는 아무것도 쓰지 않는다.
- `npm run check` 통과. pytest 도 같은 결과.
- 보고서 `validation/lane-T-raw-skip/REPORT.md` 를 커밋에 포함. 한국어 커밋, Co-Authored-By 금지, git push 금지, git stash 금지. 통합 브랜치 merge 가 거부되면 보고만.
- 완료는 preamble 의 `worker_done`(--outcome 명시) 뒤 조율자 터미널 `term_be1eaaf8-815c-4231-a858-7229d925e5fe` 에 한 줄 안내.
