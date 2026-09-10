## ENTRY-001: 검증기가 계산해 놓고 판정에 쓰지 않거나 한 행만 표본으로 삼는 패턴

**상황**
F6-H 공급원 검증 사이클에서 worker(`verify_window.py`)와 C-13(`verify_yahoo_evidence.py`) 두 워크트리의 검증 스크립트를 설계진행에서 독립 재검증함. 2026-09-09~09-10 사이 같은 부류가 5회 관측됨.

**증상**
다섯 건 모두 검증기가 "통과"를 냈으나 입력을 바꾸면 판정이 따라오지 않음.
1. C-13 R2-01. `comp["trade_cur"]` 상수를 쓰고 읽은 `basis_cur`를 무시해 `basis.currency`를 KRW로 바꿔도 `trade_currency=USD, currency_match=True` 출력함.
2. C-13 R2-02. `stage2`·`stage3` 출력의 `pass`가 `False` 고정이고 계산한 `quarter_window_verifiable`·`basis_verification_pass`를 쓰지 않음. SPCX 요약은 상수라 상세 `actual_count=2`인데 요약은 `1`로 모순됨.
3. worker W2. `sample = (a2 + e2)[0]["raw"]`로 창 4행 중 첫 행만 보고 basis를 판정함. 첫 행에만 `currency`·`share_basis`·`accounting`·`asOf`를 넣자 나머지 3행에 키가 없는데도 `basis_verified=True`, `score_ready=True`가 됨.
4. C-13 R3-01(R2-01 수정 후 재발). 새로 만든 `trade_currency_status`를 `stage3["pass"]`와 `scoring_eligible` 어디에도 연결하지 않음. 거래·전망 통화를 함께 KRW로 바꾸니 `trade_currency_status=conflict`인데 `currency_match=True`임.
5. C-13 R3-02. `has_period_end_in_dates`가 `earnings_dates[0].keys()`만, `has_concrete_period_in_est`가 `q0`만 봄. 첫 행에만 `period_end`를 넣자 `stage2 pass`가 True로 뒤집힘. 그 첫 행은 `Reported EPS: null`인 미발표 예정 행이라 `stage1`이 유효 실적에서 제외한 행임.

**원인**
결함이 현재 원자료에서 가려져 있음. 어느 행에도 해당 키가 없어 결과가 0/12로 나오므로 검사가 틀려도 최종 수치가 맞게 보임. 그래서 고정 출력에 맞춘 자체 테스트가 전원 PASS함. C-13 Test 6은 `stage2["pass"] == stage2["specific_fiscal_quarters_identifiable"]`를 단언하는데 같은 변수를 두 키에 넣은 것이라 절대 실패할 수 없는 동어반복임.

**해결**
검토 시 반드시 입력을 바꿔 판정이 따라오는지 본다. 임시 복사본에 (a) 양성 대조 — 라벨 불연속 주입처럼 반드시 X가 나와야 하는 변이, (b) 음성 대조 — 값을 실제로 읽는지 보는 변이, (c) 부분 부여 — 창의 일부 행에만 필드를 넣어 한 행 표본으로 전체를 판정하는지 보는 변이를 함께 건다. 재현 코드는 `설계진행/validation/recheck_f6h_batch10.py`와 `recheck_f6h_sources02_r2.py`이며 원본 워크트리를 건드리지 않도록 `git archive <커밋>`으로 임시 경로에 사본을 풀고 `importlib`로 함수만 로드한다. 대상 스크립트의 `__main__`이 다른 워크트리 절대경로에 결과를 덮어쓸 수 있으므로 `__main__`은 실행하지 않는다. 검증기가 낸 값 대신 원자료에서 직접 세어 대조한다.

**검증**
worker `194fd4b`은 사본 실행이 커밋된 `window-verification.txt`와 바이트 동일했고 2회 실행도 동일함. 그 상태에서 위 세 변이로 W1·W2·W3을 재현해 needs_fix로 회신함(커밋 `9d06eec`). C-13 `c9ce4d1`은 동일 입력 2회 일치와 요약 수치 11/12·0/12·11/12·0/12를 재현한 뒤 R2-01~04가 실제로 고쳐진 것을 확인했고, 같은 방식으로 R3-01·R3-02를 새로 재현해 needs_fix로 회신함(커밋 `21c7744`). `python scripts/validate_memory.py` 통과함.

**일자**
- 2026-09-10 최초 (관측 5회: C-13 R2-01·R2-02, worker W2, C-13 R3-01·R3-02)
