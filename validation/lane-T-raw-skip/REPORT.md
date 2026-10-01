# 레인 T — 원자료 없는 테스트 15건을 실패 대신 사유 있는 건너뛰기로 보고서 (2026-10-01)

지시서 `.agents/plans/evidence-layer-2026-09/dispatch/lane-T.md` 와 공통 규약 `README.md` 를 따랐다.
단언·기대값·테스트 순서는 바꾸지 않았으며, scripts·문서·그 밖의 테스트는 고치지 않았다.

## 커밋

| SHA | 내용 |
| --- | --- |
| `c2c3f98` | test(tests): 원자료 없는 테스트 15건을 사유 있는 건너뛰기로 변경 |
| 이 보고서 커밋 | docs(validation): 레인 T 원자료 건너뛰기 보고서 |

## 1. 한 일

1. **`tests/_raw.py` 도우미 모듈 생성**:
   - `require_raw(*paths)` 데코레이터를 구현했다. 첫 줄은 규약에 따라 한국어 한 줄 주석(`# 원자료 부재 시 테스트를 사유와 함께 건너뛰는 데코레이터 도우미`)을 달았다.
   - 지정된 원자료 경로 중 하나라도 존재하지 않으면 `unittest.skip("원자료 없음: <상대경로> (원본 폴더에서만 실행)")` 로 건너뛴다. 경로 표기는 `.as_posix()` 로 통일해 OS 간 슬래시 표기가 일치하게 했다.
   - 원자료가 모두 존재하면 `lambda fn: fn` 을 반환하여 기존 테스트 코드가 원본 그대로 실행된다.

2. **원자료 부재 대상 테스트 6개 파일 13개 메소드(총 15건 실패/오류)에 `@require_raw` 적용**:
   - `tests/test_scorecard_fix54_obs.py`:
     - `LeaseCompletenessTest.test_missing_component_is_not_summed_as_zero`: `@require_raw(RAW / "SPCX.companyfacts.json", RAW / "PLTR.companyfacts.json", RAW / "TSLA.companyfacts.json")` (서브테스트 2건 + 본 테스트 오류 해소)
     - `AppleWindowTest.test_collector_q4_starts_next_day`: `@require_raw(RAW / "AAPL.companyfacts.json")` (오류 1건 해소)
   - `tests/test_scorecard_fix55_stage2.py`:
     - `Stage2Test.test_broad_tag_sweep_finds_only_tesla`: `@require_raw(RAW / "TSLA.companyfacts.json")` (`RAW.glob` 원자료 부재로 빈 목록 비교 실패 1건 해소)
   - `tests/test_scorecard_fix57_stage1.py`:
     - `Stage1Test.test_oracle_rpo_registered_from_the_filing`: `@require_raw(RAW / "ORCL.companyfacts.json")` (오류 1건 해소)
     - `Stage1Test.test_oracle_offbalance_records_that_it_matches_no_filing`: `@require_raw(RAW / "ORCL.companyfacts.json")` (오류 1건 해소)
   - `tests/test_scorecard_fix58_stage1.py`:
     - `Stage1Test.test_nvidia_marketable_equity_added`: `@require_raw(RAW / "NVDA.companyfacts.json")` (오류 1건 해소)
     - `Stage1Test.test_meta_and_alphabet_were_already_inside_the_line`: `@require_raw(RAW / "META.companyfacts.json", RAW / "GOOGL.companyfacts.json")` (오류 1건 해소)
     - `Stage1Test.test_oracle_mixed_tag_stays_out`: `@require_raw(RAW / "ORCL.companyfacts.json")` (오류 1건 해소)
     - `Stage1Test.test_tesla_crypto_gets_the_same_judgment_as_spacex`: `@require_raw(RAW / "TSLA.companyfacts.json")` (오류 1건 해소)
     - `Stage1Test.test_undiscounted_excess_is_imputed_interest_not_a_commitment`: `@require_raw(RAW / "ORCL.companyfacts.json")` (오류 1건 해소)
   - `tests/test_scorecard_fix58_stage2.py`:
     - `Stage2Test.test_oracle_sweep_wording_is_scoped_to_the_regex`: `@require_raw(RAW / "ORCL.companyfacts.json")` (오류 1건 해소)
   - `tests/test_scorecard_obs_recency.py`:
     - `TestRestatementGeneration.test_msft_fy2016_is_held_using_real_facts`: `@require_raw(RAW / "MSFT.companyfacts.json")` (오류 1건 해소)
     - `TestCollectorConsumesTheRule.test_tesla_fy2024_net_income_is_held`: `@require_raw(RAW / "TSLA.companyfacts.json")` (오류 1건 해소)

## 2. 건너뛴 테스트 목록과 사유

| 테스트 식별자 | 원자료 경로 | 건너뛰기 사유 |
| --- | --- | --- |
| `tests.test_scorecard_fix54_obs.LeaseCompletenessTest.test_missing_component_is_not_summed_as_zero` | `validation/f6-avail-15/_raw/SPCX.companyfacts.json` 등 | 원자료 없음: validation/f6-avail-15/_raw/SPCX.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix54_obs.AppleWindowTest.test_collector_q4_starts_next_day` | `validation/f6-avail-15/_raw/AAPL.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/AAPL.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix55_stage2.Stage2Test.test_broad_tag_sweep_finds_only_tesla` | `validation/f6-avail-15/_raw/TSLA.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/TSLA.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix57_stage1.Stage1Test.test_oracle_rpo_registered_from_the_filing` | `validation/f6-avail-15/_raw/ORCL.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/ORCL.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix57_stage1.Stage1Test.test_oracle_offbalance_records_that_it_matches_no_filing` | `validation/f6-avail-15/_raw/ORCL.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/ORCL.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix58_stage1.Stage1Test.test_nvidia_marketable_equity_added` | `validation/f6-avail-15/_raw/NVDA.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/NVDA.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix58_stage1.Stage1Test.test_meta_and_alphabet_were_already_inside_the_line` | `validation/f6-avail-15/_raw/META.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/META.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix58_stage1.Stage1Test.test_oracle_mixed_tag_stays_out` | `validation/f6-avail-15/_raw/ORCL.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/ORCL.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix58_stage1.Stage1Test.test_tesla_crypto_gets_the_same_judgment_as_spacex` | `validation/f6-avail-15/_raw/TSLA.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/TSLA.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix58_stage1.Stage1Test.test_undiscounted_excess_is_imputed_interest_not_a_commitment` | `validation/f6-avail-15/_raw/ORCL.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/ORCL.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_fix58_stage2.Stage2Test.test_oracle_sweep_wording_is_scoped_to_the_regex` | `validation/f6-avail-15/_raw/ORCL.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/ORCL.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_obs_recency.TestRestatementGeneration.test_msft_fy2016_is_held_using_real_facts` | `validation/f6-avail-15/_raw/MSFT.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/MSFT.companyfacts.json (원본 폴더에서만 실행) |
| `tests.test_scorecard_obs_recency.TestCollectorConsumesTheRule.test_tesla_fy2024_net_income_is_held` | `validation/f6-avail-15/_raw/TSLA.companyfacts.json` | 원자료 없음: validation/f6-avail-15/_raw/TSLA.companyfacts.json (원본 폴더에서만 실행) |

## 3. 원자료 존재 시 건너뛰기 해제 검증

- 원본 폴더에는 아무것도 쓰지 않았으며, 워크트리 내에 임시 가짜 원자료 파일(`validation/f6-avail-15/_raw/ORCL.companyfacts.json`)을 생성하여 skip 이 풀리는지 확인했다.
- 실행 명령:
  `uv run --frozen python -X utf8 -m unittest -v tests.test_scorecard_fix57_stage1.Stage1Test.test_oracle_rpo_registered_from_the_filing`
- 결과:
  `test_oracle_rpo_registered_from_the_filing ... ok`
  `Ran 1 test in 0.021s, OK`
- 건너뛰기가 정상적으로 해제되고 테스트 본문이 실행되어 통과함을 확인한 직후, 임시 가짜 파일 및 디렉터리를 완전히 삭제했다.

## 4. 검증 결과

1. **unittest 전체 실행**:
   `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`
   - 결과: `Ran 1146 tests in 19.048s, FAILED (failures=2, skipped=13)`
   - 기존 원자료 부재로 인한 15건(실패 1건, 오류 14건)이 전부 해소되어 오류 0건이 되었다.
   - 남은 2건 실패는 아래 "소유 밖에서 발견한 문제" 항목의 `WiringSmokeTest` 환경 이슈다.

2. **pytest 실행**:
   `uv run --frozen pytest -q`
   - 결과: `2 failed, 1131 passed, 13 skipped, 2139 subtests passed in 20.79s`

3. **npm 스크립트 검증**:
   - `npm run check`: 통과 (`node --check server.js && uv run --frozen python -X utf8 -m compileall -q scripts`)
   - `npm run test:node`: 통과 (`15 pass, 0 fail`)
   - `npm run validate:memory`: 통과 (`Memory schema validation passed`)

## 5. 소유 밖에서 발견한 문제

- `tests/test_hooks.py` 내 `WiringSmokeTest` 2건 실패:
  - `test_dangerous_payload_exits_2`, `test_harmless_payload_exits_0`
  - 사유: Windows 환경에서 `shutil.which("bash")` 가 `C:\Windows\system32\bash.EXE`(WSL bash)를 반환하고, 해당 WSL 환경 내 PATH 에 `uv` 가 없어 `/bin/bash: line 1: uv: command not found` (exit code 127) 오류가 발생한다.
  - 레인 M 에서도 동일 관측이 있었으며(`.agents/plans/evidence-layer-2026-09/checklist.md` 86행), `tests/test_hooks.py` 는 레인 T 소유 밖 파일이므로 수정하지 않았다. 조율자 환경(Git bash 연결 환경)에서는 정상 통과한다.

## 6. 남긴 것

- 없음. 소유 파일 외 변경 0건.
