# F6H-SOURCES-02-R2 재검토

- 검토일. 2026-09-10.
- 대상. C-13 `c9ce4d1bc250662795f05a9e9104ae3f395cf801`.
- 회신. 완료 보고 `msg_b074697891ae`, 원 요청 `msg_8fd06ac3ff02`, 스레드 `msg_609ace096b37`.
- 판정. **needs_fix**. **요청한 R2-01~04 는 네 건 모두 실제로 고쳐졌고 임시 사본에서 재현했다.** 다만 보완 과정에서 같은 부류의 결함이 새로 생겼다. 신규 5건을 R3-01~R3-05 로 남긴다.

## 재현한 범위

C-13 워크트리를 수정하지 않았다. `git archive c9ce4d1 validation/f6-h-sources-02` 로 임시 경로에 사본을 풀고, 원자료는 worker 저장본 `_raw/yahoo/` 를 스냅샷으로 복사해 썼다. **`__main__` 은 실행하지 않았다.** 모듈 `__main__` 이 C-13 워크트리 절대경로에 결과 JSON 을 덮어쓰기 때문에 `importlib` 로 함수만 로드했다. 재검증 코드는 `validation/recheck_f6h_sources02_r2.py`, 산출은 `validation/f6h-sources-02-r2-review-evidence.json` 이다.

- 동일 입력 2회 실행 결과 완전 일치.
- 요약 수치 재현. stage1 11/12, stage2 0/12, stage3 통화일치 11/12, stage4 0/12.

## 통과 확인 — R2-01~04

**R2-01 원자료 거래 통화 무시. 고쳐졌다.** `basis.currency` 를 파싱해 `raw_trade_currency` 로 두고 상수는 `ref_trade_currency` 로 분리했다. META `basis.currency` 를 KRW 로 바꾸자 `trade_currency_status=conflict`, `currency_match=False` 였고, 키를 삭제하자 `UNKNOWN` / `missing` / `False` 였다. 이전에 KRW 로 바꿔도 USD 일치로 나오던 결함은 재현되지 않는다.

**R2-02 단계 간 판정 불일치와 요약 상수. 고쳐졌다.** stage2·3·4 의 `pass` 가 계산 변수에 연결됐다. SPCX 실적행을 복제하자 상세가 `actual_count=2`·`unique_actual_quarters=1`·`duplicate_row_count=1`·`has_2a=False`, 요약 `spcx_details` 도 같은 값으로 동적 산출됐다. 이전의 상세 2 대 요약 1 모순은 재현되지 않는다.

**R2-03 비수치 값 통과. 고쳐졌다.** `is_finite_number()` 가 문자열·`bool`·NaN·Inf 를 기각한다. `0q.avg` 를 `"NOT_A_NUMBER"`·`True`·`NaN` 으로 바꾼 세 경우 모두 stage1 이 FAIL 로 뒤집혔다. **음수는 유지된다.** SPCX `-0.09` 가 유효 실적 1건으로 남는다.

**R2-04 철회 주장 잔존. 고쳐졌다.** Nasdaq 9/12·통화 10/12·StockAnalysis 0/12 가 비교표에서 빠지고 철회·미검증 표기로만 남았다. SPCX 는 "상장으로 인해"가 사라지고 저장자료 관측 1건으로 좁혀졌다. BABA 는 1단계 통과와 3단계 통화 불일치가 분리됐다. Yahoo 는 allowlist 미등재 사실과 개인 사용 권리 검토가 구분됐다.

## R3-01. conflict 를 계산해 놓고 어느 판정에도 쓰지 않는다

R2-01 로 만든 `trade_currency_status` 가 `stage3_basis_metadata["pass"]` 에도 `scoring_eligible` 에도 들어가지 않는다. 두 곳 모두 `currency_match` 만 본다.

재현. META 의 `basis.currency` 와 `0q`·`+1q` 의 `currency` 를 함께 KRW 로 바꿨다. 결과는 `trade_currency_status=conflict` 인데 `currency_match=True` 다. 원자료가 참조 통화와 충돌해도 자기들끼리만 맞으면 통화 검사를 통과한다.

지금 결과가 가려져 있는 이유는 `has_accounting_standard` 와 `has_as_of` 가 항상 False 라 stage3 이 어차피 못 넘어가기 때문이다. **R2-02 에서 지적한 "계산해 놓고 출력에 쓰지 않는다"가 통화 쪽에서 다시 생겼다.** `conflict` 와 `missing` 을 stage3 판정에 연결하라.

## R3-02. 회계기간 근거를 첫 행 하나로 판정한다

`has_period_end_in_dates` 는 `ed[0].keys()` 만 보고, `has_concrete_period_in_est` 는 `q0` 만 본다. 나머지 행과 `+1q` 는 보지 않는다.

재현. META `earnings_dates[0]` 에만 `period_end` 를, `0q` 에만 `fiscal_period` 를 넣자 `stage2 pass` 가 **True 로 뒤집혔다.** 반대로 두 번째 행에만 넣으면 잡지 못한다.

더 구체적으로, META 의 `ed[0]` 은 `Reported EPS: null` 인 **미발표 예정 행**이다. stage1 이 유효 실적에서 제외한 행을 stage2 가 회계기간 근거의 표본으로 삼는다. 현재 0/12 인 것은 어느 행에도 키가 없어서일 뿐 검사가 옳아서가 아니다. worker `verify_window.py` 에 낸 W2 와 같은 부류이므로 같은 기준을 적용한다. 창에 쓰는 행 전부에서 읽고, 행 간 불일치는 통과가 아니라 `conflict` 로 낸다.

## R3-03. `financialCurrency` 를 읽지 않아 TSM 이 통화 일치로 집계된다

원자료 `basis` 에는 통화 필드가 둘인데 검증기는 `currency` 만 파싱한다. 소스에 `financialCurrency` 문자열 자체가 없다.

| 티커 | `basis.currency` | `basis.financialCurrency` | `0q.currency` | 현재 `currency_match` |
|---|---|---|---|---|
| **TSM** | USD | **TWD** | USD | **True** |
| **BABA** | USD | **CNY** | CNY | False |
| 나머지 10개사 | USD | USD | USD | True |

BABA 는 전망이 CNY 로 라벨돼 걸리지만, **TSM 은 본사 재무 통화가 TWD 인데 전망이 USD 로 라벨돼 있어 그대로 통과한다.** ADR 5:1 과 TWD→USD 환산이 실제로 반영됐는지는 공급사 라벨 외에 근거가 없다. 보고서 `basis_notes` 에 "ADR 5:1 미표기" 문구는 있으나 `stage3_currency_match_count 11/12` 에는 반영되지 않는다.

`financialCurrency` 를 함께 파싱하고, `currency` 와 다르면 환산 근거 미확인 항목으로 별도 출력하라. TSM 을 통화 일치로 세지 않는다.

## R3-04. 2A 쪽 통화는 검사 대상이 아니다

`currency_match` 는 전망 통화(`0q`·`+1q`)와 거래 통화만 비교한다. `earnings_dates` 의 `Reported EPS` 에는 통화 필드가 아예 없고 검증기도 묻지 않는다. 이름은 창 전체의 통화 정합을 보증하는 것처럼 읽히는데 실제로는 2E 쪽만 본다. 이름을 `estimate_currency_match` 로 좁히거나, 2A 통화 미확인을 별도 항목으로 출력하라.

부수적으로 stage1 의 `has_2a_values` 는 `unique_actual_quarters >= 2` 라 전체 이력에 확정 분기가 2개 이상 있으면 참이다. BABA 는 24 분기다. "최근 확정 2개 분기"가 아니라 "확정 분기가 2개 이상 존재"다. stage2 가 0/12 로 막고 있어 결론은 바뀌지 않지만 표기는 구분하라.

## R3-05. stage2 notes 가 계산 결과와 무관한 고정 문자열이다

`quarter_window_notes` 는 입력과 상관없이 항상 같은 세 문장을 출력한다. R3-02 재현에서 `pass=True` 인데도 notes 는 여전히 "회계기간 종료일 미표기 / 회계분기 레이블 부재 / 특정 불가"라고 찍혔다. R2-02 가 요구한 연결이 `pass` 필드에만 적용되고 notes 에는 적용되지 않았다.

## 부수 지적 — 재현 환경과 자체 테스트

**두 절대경로.** `get_raw_dir()` 이 worker 워크트리 절대경로를 하드코딩하고, `__main__` 이 C-13 워크트리 절대경로에 결과 JSON 을 덮어쓴다. 임시 사본에서 무심코 실행하면 C-13 산출물이 덮어써진다. 원자료 경로는 인자로 받고 출력 경로는 스크립트 위치 기준 상대경로로 두라.

**Test 6 은 동어반복이다.** `stage2["pass"] == stage2["specific_fiscal_quarters_identifiable"]` 는 같은 변수를 두 키에 넣은 것이라 실패할 수 없다. stage3 도 출력 필드로 같은 식을 다시 계산한다. 하드코딩 False 는 잡지만 판정이 입력에 반응한다는 증거는 아니다. 입력을 바꾸는 Test 3·4 쪽이 실제 증거다. R3-01·R3-02 를 그 방식으로 테스트하라.

## 다음 완료 조건

새 네트워크·API 수집 없이 저장 원자료만으로 R3-01~R3-05 를 보완한다. 통화 동시 변경, 회계기간 필드를 행마다 다르게 부여, `financialCurrency` 불일치 세 가지를 입력 변경 테스트로 남긴다. 원자료·점수·규칙·승인은 변경하지 않고 worker 담당인 Finnhub 검증은 중복 조사하지 않는다.

**R2-01~04 는 통과로 확정하며 다시 요구하지 않는다.** R3 5건은 현재 수치를 바꾸지 않는다. stage1 11/12·stage2 0/12·stage4 0/12 와 Yahoo 가 allowlist 미등재로 공식 채점 후보가 아니라는 결론은 유지된다. 이번 재검토로 F6-H 산식·밴드·새 점수를 승인하지 않는다.
