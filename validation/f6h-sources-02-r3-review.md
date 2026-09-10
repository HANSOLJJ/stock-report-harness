# F6H-SOURCES-02-R3 재검토

- 검토일. 2026-09-10.
- 대상. C-13 `710f148cf750456f376ea6409d7ffdb8d4caed0b`.
- 회신. 완료 보고 `msg_b69c6b033771`, 원 요청 `msg_734e6968ba5f`, 스레드 `msg_609ace096b37`.
- 판정. **pass**. R3-01~R3-05 다섯 건 모두 임시 사본에서 입력을 바꿔 재현했고 판정이 따라 움직였다. R2-01~04 회귀도 유지된다. 새로 생긴 같은 부류의 결함은 없다.

## 재현한 범위

C-13 워크트리를 수정하지 않았다. `git archive 710f148 validation/f6-h-sources-02` 로 임시 경로에 사본을 풀고, 원자료는 worker 저장본 `_raw/yahoo/` 를 스냅샷으로 복사해 `importlib` 로 함수만 로드했다. 동일 입력 2회 실행 결과가 완전 일치했다.

요약 수치가 R2 대비 하나 바뀌었고 하나 늘었다.

| 단계 | R2 (`c9ce4d1`) | R3 (`710f148`) |
|---|---|---|
| stage1 값 존재 | 11/12 | 11/12 |
| stage2 회계분기창 | 0/12 | 0/12 |
| **stage3 종합 통화 일치** | **11/12** | **10/12** |
| stage3 전망 통화 일치 | (항목 없음) | 11/12 |
| stage4 채점 가능 | 0/12 | 0/12 |

## R3-01. conflict 를 판정에 연결했다 — 확인

`currency_match` 가 `trade_currency_status == "matched"` 를 요구하고, `basis_verification_pass` 와 `scoring_reasons` 에도 들어갔다.

재현. META 의 `basis.currency`·`basis.financialCurrency`·`0q`·`+1q` 통화를 **모두 KRW** 로 바꿨다. R2 에서는 `conflict` 인데 `currency_match=True` 였다. R3 는 `trade_currency_status=conflict`, `currency_match=False` 다. 원자료끼리만 맞고 참조 통화와 어긋나는 경우가 더는 통과하지 않는다.

## R3-02. 창에 쓰는 행 전부를 본다 — 확인

`actual_rows_with_period` 를 `valid_reported_rows` 전체에서 세고, 미발표 행은 `unannounced_rows_with_period` 로 분리했다. 전망은 `0q`·`+1q` 양쪽을 본다.

| 변이 | `actual_period_status` | stage2 |
|---|---|---|
| 미발표 행(`Reported EPS: null`)에만 기간 부여 | `conflict_unannounced_row_only` | **False** |
| 확정 실적행 **일부**에만 기간 부여 | `conflict_partial_missing` | **False** |
| 확정 실적행 **전부** + `0q` 만 | `present` / 전망 `conflict_partial_missing` | **False** |
| 확정 실적행 **전부** + `0q`·`+1q` 둘 다 | `present` / `present` | **True** |

마지막 줄이 양성 대조다. **stage2 가 0/12 로 고정된 것이 아니라 근거가 갖춰지면 실제로 True 로 넘어간다.** R2 에서 첫 행 하나로 뒤집히던 결함은 재현되지 않는다.

## R3-03. `financialCurrency` 를 파싱한다 — 확인, TSM 10/12 정정 타당

| 티커 | `basis.currency` | `financialCurrency` | `0q.currency` | `financial_currency_status` | `estimate_currency_match` | `currency_match` |
|---|---|---|---|---|---|---|
| TSM | USD | **TWD** | USD | `differs_unverified_conversion` | True | **False** |
| BABA | USD | **CNY** | CNY | `differs_unverified_conversion` | False | False |
| 나머지 10개사 | USD | USD | USD | `matched` | True | True |

TSM 이 통화 일치에서 빠져 11/12 → **10/12** 가 됐다. 환산 근거가 페이로드에 없으므로 불일치로 두는 것이 맞다. `financialCurrency` 키를 삭제하면 `missing` 으로 떨어지는 것도 확인했다.

## R3-04. 2E 전용 지표를 분리했다 — 확인

`estimate_currency_match`(11/12)가 `currency_match`(10/12)와 별도 항목으로 나오고 요약에도 `stage3_estimate_currency_match_count` 로 실린다. `Reported EPS` 통화는 `actual_currency_status="unspecified_in_payload"` 로 명시된다. stage1 문구도 "이력 내 확정 실적 N개 분기(2개 이상 존재)"로 바뀌어 최근 2개 분기 창과 구분된다.

## R3-05. notes 가 입력 상태를 따라간다 — 확인

R2 에서는 입력과 무관하게 항상 같은 세 문장이었다. R3 는 `missing` / `conflict_unannounced_row_only` / `conflict_partial_missing` / `present` 각각에 다른 문구가 나오고, 양성 대조에서는 "연속 회계분기창(2A+2E) 객관적 특정 완료"로 바뀐다.

## R2-01~04 회귀 — 유지

| 변이 | 결과 |
|---|---|
| `basis.currency` = KRW | `conflict` / `currency_match=False` |
| `basis.currency` 삭제 | `UNKNOWN` / `missing` / False |
| `0q.avg` 문자열 · `bool` · NaN | stage1 FAIL 세 경우 모두 |
| SPCX `-0.09` | 유효 실적으로 유지 |
| SPCX 실적행 복제 | 상세·요약 모두 2행 · 1분기 · 중복 1건 |

## 자체 테스트 — 동어반복 해소 확인

R2 의 Test 6 은 같은 변수를 두 키에 넣고 비교하는 동어반복이라 실패할 수 없었다. R3 는 그 자리를 실제 입력 변이(미발표 행에만 부여 / 일부 행에만 부여)와 원본 대비 notes 차이 단언으로 바꿨다. Test 7 도 TSM `financialCurrency` 실측과 10/12·11/12 카운트를 함께 단언한다.

## 남는 지적 — 차단 사유 아님

1. `get_raw_dir()` 후보 목록 네 번째에 `C:/Users/noble/...` 절대경로가 남아 있다. `--raw` 인자와 스크립트 기준 상대경로가 앞서므로 동작에는 영향이 없으나, 커밋된 스크립트에 특정 머신 경로가 남는다. 다음 손볼 때 지운다.
2. 자체 테스트에 stage2 가 **True 로 넘어가는** 양성 대조가 없다. 음성 두 가지만 있다. 이번엔 설계진행이 외부에서 확인했으므로 통과시키되, 다음 수정 때 추가한다.
3. REPORT 에 `통화 10/12` 라는 표현이 두 뜻으로 쓰인다. 철회된 Nasdaq 수치와 이번 Yahoo 종합 통화 일치가 같은 숫자·같은 라벨이다. 혼동 소지가 있으니 한쪽 라벨을 구분한다.

## 결론

R3 보완은 통과다. **다만 이 통과가 Yahoo 채택을 뜻하지 않는다.** stage2 0/12·stage4 0/12 이고 Yahoo 는 v1.6 allowlist 미등재다. F6-H 산식·밴드·새 점수는 승인하지 않는다. F6 의 병목은 여전히 basis(회계기준·통화·주식단위) 미확인이며, worker 담당 Finnhub 쪽 W1~W6 보완이 남아 있다.
