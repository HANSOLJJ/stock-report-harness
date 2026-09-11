# HANDOFF — Codex → Claude 세션 인수인계

> **읽는 사람에게.** 이 문서는 `설계진행` 워크트리에서 조율(coordinator) 역할로 돌던 Codex 세션이
> 사용량 한도로 중단되면서, 그 세션의 맥락을 다음 에이전트에게 넘기기 위해 만든 것이다.
> **작업 규칙·컨벤션은 `AGENTS.md`가 우선이다. 이 문서는 "지금 무슨 일이 어디까지 진행됐는가"만 담는다.**

---

## 0. 세션 메타

| 항목 | 값 |
|---|---|
| 원본 에이전트 | Codex CLI (Orca TUI 탭) |
| Codex thread id | `01a08151-6708-7d83-9750-169738be3388` |
| 워크트리 (cwd) | `C:\Users\noble\orca\workspaces\stock-report-harness\설계진행` |
| 세션 기간 | 2026-09-08 23:00 ~ 2026-09-10 09:30 (KST) |
| 규모 | 유저 메시지 120, 커맨드 실행 574, 컨텍스트 압축 5회 |
| 중단 사유 | `usageLimitExceeded` — "You've hit your usage limit … try again at **Sep 15th, 2026 2:46 PM**" |
| 중단 시각 | 2026-09-10 09:30 KST, 마지막 턴 `failed` |
| 인수 문서 작성 | 2026-09-10 (Codex `thread_history` 원본에서 복원) |

한도 해제 예정이 9/15이므로, 그때까지는 이 워크트리의 조율 작업을 Claude가 이어받는다.

---

## 1. 역할 구조 (이걸 먼저 이해할 것)

`stock-report-harness` 저장소는 Orca 워크트리로 역할이 나뉘어 있다.

| 워크트리 | 역할 |
|---|---|
| **설계진행** | **조율자(coordinator)**. 직접 구현하지 않는다. 과제를 배정하고, 완료 보고를 **독립 재검증**한 뒤 `pass` / `needs_fix`를 판정하고, 판정 기록을 `설계진행/validation/*-review.md`로 남긴다. |
| **worker** | 구현·조사 담당 A |
| **C-13** | 구현·조사 담당 B (worker와 **병렬 독립 검증**을 시킨다. 한쪽 오류를 다른 쪽이 잡게 하는 구조) |
| NTM-전망치조사, scarpper | 보조 조사 워크트리 |

통신은 Orca orchestration 메시지로 한다.

```
orca orchestration check --run run_1243c2a83479 [--peek] [--json]
orca orchestration reply --id <msg_id> --body '...' --json
orca terminal list --json
orca terminal read  --terminal <term_id> --screen --json
orca terminal send  --terminal <term_id> --text '...' --enter --json
```

- 조율 작업에는 `orca-cli`, `orchestration` 스킬을 사용한다.
- 완료 보고를 받으면 **보고서를 믿지 말고 저장 원자료·코드로 직접 재현**한다. 이 세션에서 실제로 여러 번, 보고서가 통과라고 쓴 것이 하드코딩이거나 검증되지 않은 판정이었다.
- 작업 지시 후에는 대상 터미널에 실행 안내까지 제출하고, `orca terminal read`로 착수를 확인한다. (메시지가 수신함에 도착하지 않은 사례가 최소 2건 있었다.)

---

## 2. 지금 붙잡고 있는 문제 — 한 문단 요약

AI 기업 채점 프레임워크의 **F6(밸류에이션 factor)** 을 자동 산출할 수 없는 상태다.
F6은 원래 **NTM PER = 주가 ÷ (향후 4개 회계분기 EPS 컨센서스 합)** 인데, 무료·허용 원천 중 12개사 전부에 대해
4개 분기 컨센서스를 같은 기준으로 주는 곳이 **하나도 없다**. 그래서 (a) 2분기 실제 + 2분기 전망을 섞는
**F6-H(2A+2E)** 대안과 (b) Reverse DCF 대안을 검토했고, **현재 결론은 둘 다 정식 점수로는 미채택**이다.
9/10 오전에는 worker·C-13 양쪽 보고서의 "확보율 11/12, 9/12"가 실제로는 **채점 가능(score-ready) 0/12**
였다는 것이 드러난 참이다. 즉 **F6은 아직 한 종목도 채점할 수 없다.**

---

## 3. 확정된 정책 — 바꾸지 말 것

이건 사용자 승인까지 끝난 결정이다. 새로 논의하지 말고 전제로 삼는다.

1. **`api.nasdaq.com`(무료 공개 API)은 생산 원천에서 최종 배제.**
   자동 수집, 관측 등록, F6 점수 계산, HTML 근거 — 전부 금지. `robots.txt` 전면 Disallow + 이용약관이
   automated/manual data capture를 금지하기 때문. 이미 받아둔 4종목 샘플은 `non-production reference`로만 보존.
   Nasdaq 9/12 수치는 **채택 가능한 공급원 성과로 해석하지 않는다.**
2. **Nasdaq Data Link `ZACKS/EE`·`ZACKS/EEH`** 는 `candidate_not_approved`. 서면 계약(특히 **가공 결과의 공개 배포 허용 여부**)이
   확정될 때만 재검토. 실제 문의는 아직 발송되지 않았고, 법인 정보·배포 범위 확정 + 사용자 승인 전에는 발송 금지.
3. **`2Q × 2` proxy 금지, 연환산(annual) proxy 정식 점수 금지.** 코드에 경로 자체를 만들지 않았다.
   근거: 백테스트 오차 중앙값 8.9%/최대 23.3%, F6 밴드 전환 확률 23%→56%, 그리고 **상승 추세 기업이 계통적으로 마이너스 편향**
   (NVDA −16.7%, PLTR −23.3%, TSM −14.3%) — 평가 축과 상관된 편향이라 표본을 늘려도 상쇄되지 않음.
4. **yfinance는 가격 데이터 용도만 유지.** EPS 컨센서스 수집으로 확대 금지 (상류 Yahoo API가 personal use only).
   Yahoo는 v1.6 allowlist에 **일부러 넣지 않았다.**
5. **종목별 공급원 혼합 금지.** 한 실행에서는 전체 기업에 **같은 공급원 + 같은 모드**를 적용한다.
   일부만 F6-N, 나머지는 F6-H로 계산하면 순위 비교가 깨진다.
6. **`accept_proxy_with_flag`** 는 관측만 보존하고 점수는 생성하지 않는다 (규칙 파일 선택지와 코드 동작이 어긋난 상태 → v1.6/v1.7에서 정리 필요).
7. **`vendor_forward_pe_verified_ntm`** 은 v1.5 기준선 보존용으로만 유지. 새 실행에서는 레거시로 제외.
   (막으면 상장 10개사 점수가 바뀌어 승인 해시가 깨지므로 의도적으로 유지 중.)
8. **SpaceX 기업 범위**: 합병 후 **SpaceX 단일 법인**, 티커 `SPCX`(NASDAQ, IPO 2026-06-12, USD 보통주, ADR 아님).
   xAI는 별도 점수를 만들지 않고 내부 사업·합병 구성요소로만 기록. 다만 기존 `spacex-xai` 승인 실행은
   **해시 보존을 위해 동결**하고, 새 실행에서 `spacex` 정규 ID + `spacex-xai` 별칭으로 연결한다. (`company_id` 개명 금지 — 승인 해시 6종 중 5개에 들어 있음.)
9. **기존 승인 자료 불변**: v1.5 기준선 점수, `results.json` 해시 `4eb8c7d7`, HTML 바이트, 승인 해시 6종은 건드리지 않는다.
   규칙 변경은 v1.5를 고치지 않고 새 버전 파일(`scorecard/rules/v1.6.json` draft)로 만든다.

---

## 4. 데이터 확보 현황 (F6 입력)

| 원천 | 확인 결과 | 현재 처리 |
|---|---|---|
| FMP (무료) | `period=quarter`가 유료 파라미터. REST 402 / MCP ACCESS DENIED. 전 종목 차단 | 사용 불가 (0/12) |
| Finnhub | 값은 오지만 `asOf`·회계기준·통화·주식기준·표본수·min/max를 **하나도 제공하지 않음**. 최대 3/4분기 | 단일 공급원 후보(11/12)로 보류 |
| SEC | 전망 필드 자체가 없음 | 0/12 (실적·회계캘린더·단위 검증 용도로만 사용) |
| Yahoo / yfinance | 2/4분기 수준. 통화는 명시함(BABA 전망 CNY vs ADS USD 불일치를 드러냄) | allowlist 미등재, 가격 용도만 |
| Nasdaq 공개 API | 4분기 값 기술적으로 확인됨 (SPCX 0.09/0.29/0.37/0.41, 합 1.16) | **정책상 배제** |
| Nasdaq Data Link ZACKS | 정식 유료 계약 경로 | 라이선스 미확정, 보류 |

**단위·기준이 공급사마다 갈리는 문제(해결 안 됨):**

- **TSM**: SEC는 IFRS·보통주 기준(`ifrs-full`로 조회해야 함). 공급사는 Finnhub=TWD 보통주 / FMP=TWD ADR / Yahoo·Nasdaq=USD ADR — 세 조합.
- **BABA**: SEC만 보통주, 공급사 넷은 전부 ADS. 한 공급사 안에서도 `epsActual`은 ADS인데 `shareOutstanding`은 보통주라 곱하면 8배 틀림.
- **회계연도 어긋남**: NVDA 결산 01-31, ORCL 05-31. `period` 값이 회계종료일이 아님이 확정됨(SEC 회계종료일 일치 0건, 달력분기말 일치 3건씩). **창 연결은 회계 라벨 `(year, quarter)`로만 한다.**
- Finnhub의 `stock/earnings`와 `calendar/earnings`는 **공통 날짜 축이 없다** (전자에 period 없음, 후자에 발표일 없음). 두 endpoint 회계분기 중복은 12개사 전부 공집합.

---

## 5. F6 대안 검토 결과

**F6-H (2A+2E: 최근 확정 2분기 실제 EPS + 향후 2분기 컨센서스)**

- C-13 재검증: 합산 APE 중앙값 **4.35%**, 평균 11.13%, F6-N과 순위 상관 **0.8545**.
- worker 자체 재검토: 합산 오차 중앙값 **2.68%**, 분기별 2E 오차 중앙값 5.29%.
- worker가 바로잡은 핵심: F6-N과 F6-H는 **서로 다른 12개월 구간**을 측정한다 → 정확도 문제가 아니라 **"어떤 기간을 factor로 측정할 것인가"라는 정책 문제**.
- 전용 밴드 후보 `[27.8, 40.3, 58.4, 86.2, 125.1]`는 표본 EPS 비율(1.3897)을 기존 밴드에 곱한 것일 뿐 **독립 검증 안 됨 → 미채택**.
- 판정: 분석은 유효 / 보조·실험 지표로 사용 가능 / **공식 순위·승인 점수 사용은 보류**.

**F6-H 정식 활성화 조건 — 현재 전부 미충족**

| 조건 | 상태 |
|---|---|
| 전체 기업 2A+2E 확보 | 불충족 (SPCX 실적 부족) |
| 동일 공급원 | 불충족 |
| 회계 기준 통일 (GAAP 실제 vs BNRI/조정 전망) | 불충족 |
| 통화 기준 통일 | 불충족 (TWD/CNY/USD 혼재) |
| ADR·ADS 기준 통일 | 불충족 (TSM 5:1, BABA 8:1) |
| 전체 동일 모드 적용 | 불충족 |
| F6-H 전용 점수 곡선 | 불충족 (후보 단계) |
| 과거 시점 재현성 | 불충족 (`asOf` 이력 없음) |

**Reverse DCF — 자동 점수 미채택**

- 전망치를 없애는 게 아니라 **가정으로 옮길 뿐**. 한 기업의 implied growth가 가정 격자에서 움직이는 폭(중앙값 38.1%p)이 12개사 전체가 벌어진 폭(27.7%p)보다 크다.
- WACC 1%p당 g가 2.4%p 이동. 인접 기업 격차 중앙값 3.7%p / 최소 0.4%p → **WACC가 1.56%p만 달라도 순위가 뒤집힌다.**
- 커버리지 8/12. FCF 음수 4개사가 하필 AI 설비투자 최전선 기업들.
- 백테스트 기준 B1·B4 불합격, B5는 이력 부재로 수행 불가.
- 결론: 계산 가능한 8개사에 한해 **가정과 함께 참고 표시만**. F6 대안은 F6-H를 우선한다.

**SPCX 예외**: 2026-06 신규 상장이라 확정 회계분기가 부족 → `new_listing_insufficient_history`로 `pending_data`.
상장 전 실적은 주식 수·법인 범위·합병 시점 기준이 검증되지 않는 한 F6-H에 사용하지 않는다.
(단, SEC에 상장 전 분기 EPS −0.34가 **비교치로 존재**한다는 점은 worker가 확인했으므로 "상장 전 실적이 없다"는 단정은 철회됨.)

---

## 6. 코드/규칙 현재 상태

- **F6 구현** (worker 커밋 `55e031f`): 분기 EPS 관측 도입, 2Q·3Q는 coverage 보존하되 `pending_data`,
  `2Q×2` 경로 미구현, **4분기 채점 관문 9개** 신설(공급사 혼합 금지·GAAP 기준 확정·ADR/ADS basis 검산 포함),
  `requires_reapproval` 표식. 테스트 54 → 73건 전부 통과.
- **원천 정책** (worker 커밋 `2fab64a`): `scorecard/rules/v1.6.json`을 **draft로 신설**, v1.5 채점 규칙을 그대로 복사하고 원천 정책만 추가.
  v1.5와 동일한지 5블록을 테스트로 고정. `api.nasdaq.com` = denied(사유·scope 명시), ZACKS = candidate_not_approved(5대 서면 조건),
  allowed = SEC 2종 + Finnhub + FMP. **검증기는 정책이 없는 v1.5 실행은 건너뛴다.** 테스트 73 → 91건 전부 통과, contract 8개 PASS,
  results 해시 불변, HTML 바이트 동일, 생산 입력의 nasdaq 참조 0건.
- **v1.6에는 원천 정책만 있고 채점 규칙 개정은 아직 없다.** F6-H 계산 방식을 넣을 때는 `v1.7.json`을 새로 만든다.
- **기준선 결과**: `worker/output/ai-scorecard-2026-09-baseline.html` — 14개 기업 중 9개 채점, 5개 미완료.
  현재 점수 상당수는 v1.5 기준선의 `carried_score` 이관값이고, **최신 자료로 전부 재산출한 최종 결과가 아니다.**

---

## 7. 중단 시점의 in-flight 작업 (중요)

Codex가 09:30에 죽었을 때 공중에 떠 있던 것들:

**(A) C-13 — F6H-SOURCES-02-R2 보완 요청: 회신 완료, 결과 대기 중**

09:29에 `msg_40b0518293b5`로 **needs_fix** 회신을 이미 보냈다. 요구한 보완 4건:

- `R2-01` META의 `basis.currency`만 KRW로 바꿔도 출력이 `trade_currency=USD / currency_match=True`.
  `comp.trade_cur` 상수를 쓰고 읽은 `basis_cur`를 무시함 → 원자료/참조 통화 분리, 누락·충돌은 unknown 처리.
- `R2-02` stage2/3 출력 `pass=False` 고정, 계산 변수 미사용, stage4 조건 불일치.
  SPCX 실적행 복제 시 상세 `actual_count=2` / 요약 `1` 모순 재현됨 → SPCX·BABA 요약 상수 제거하고 상세에서 산출.
- `R2-03` META `0q.avg="NOT_A_NUMBER"` 문자열도 stage1 PASS → 유한수 검증 + 중복행/분기 구분 추가. **단 음수 자체를 결측 처리하지 말 것.**
- `R2-04` REPORT 3절에 철회된 Nasdaq 9/12·통화 10/12·StockAnalysis 0/12 수치가 남아 있음 → 철회/미검증 처리.
  "SPCX 상장 때문에 실적 1건"이라는 인과 단정은 "저장 자료 내 1건"으로 축소. BABA는 값 존재와 통화 미확인을 분리.
  Yahoo 미등재 사실은 유지하되 개인사용/상업배포 혼동 금지.
- 상세 검토 기록: `설계진행/validation/f6-h-sources-02-r1-review.md`
- 조건: 새 네트워크 호출·점수·규칙·승인 변경 없이 테스트로만 보완, 원자료 보존.

**(B) worker — F6H-BATCH-10-R1 검토: 검토 중단, 회신 미발송** ← **이어서 할 일**

worker 커밋 `194fd4b` (`worker/validation/f6h-source-batch-10/REPORT-R1.md`, `verify_window.py`, `window-verification.txt`).
worker 보고 요지:

- `na>=2 / ne>=2`는 창 검증이 아니었음을 인정하고 판정을 넷으로 분리 →
  **raw-availability 11/12, window-verified 11/12, basis-verified 0/12, score-ready 0/12. 채점 가능 기업 0개사.**
- NVDA `period 2026-09-30`이 수집 시점보다 뒤인데 actual이 있음. SEC 대조 결과 `period`는 회계종료일이 아님(정확한 정의는 미확정).
- basis는 키 자체가 없어 12개사 unknown. 추측 통과시키지 않음.
- 철회 2건: SPCX 상장 전 실적 부재 단정 철회, FMP/SEC 차단이 SPCX와 무관하다는 점 정정.
- 확인 6건 / 미확인 7건 분리. **다음 확인 1순위 = 회계기준, 그리고 두 endpoint 기준 일치.**

Codex는 09:30에 `verify_window.py`를 직접 재현 실행(카운트 재계산, 반복 실행 동일성, 커밋된 stdout 대조,
`load_finnhub` 몽키패치로 입력 변경 반응 확인)하던 중 죽었다. **`orca orchestration reply --id msg_ca637f412da9` 회신이 아직 나가지 않았다.**

**(C) 설계진행 터미널**: `term_02ca0522-142d-462e-ae85-6b623ce528d6`에 사용성 설문이 떠 있어 `0` + Enter로 건너뛴 상태.

---

## 8. 이어받는 사람이 할 일 (순서대로)

1. `orca orchestration check --run run_1243c2a83479 --peek --json`으로 수신함부터 확인. (B)와 (A)의 회신이 와 있는지 본다.
2. **(B) 완결**: worker `194fd4b`의 `verify_window.py`를 직접 재현하고 — 특히 "window-verified 11/12"가
   **공급사 회계 라벨 연결만 확인한 것인지, 실제 분석 기준일에 맞는 분기까지 확인한 것인지** 구분해서 —
   `orca orchestration reply --id msg_ca637f412da9`로 판정 회신. 검토 기록을 `설계진행/validation/`에 남기고 커밋.
3. **(A) 수령**: C-13의 R2 보완이 오면 4건이 실제로 고쳐졌는지 임시 복사본으로 재현 검증.
4. **F6 남은 관문 정리**: 현재 `score-ready 0/12`의 병목은 **basis(회계기준·통화·주식단위) 미확인**이다.
   worker가 지목한 1순위 — Finnhub 회계기준 + 두 endpoint 기준 일치 — 는 **Finnhub에 직접 문의**해야 풀린다.
   이 문의를 진행할지가 사용자에게 물어볼 결정 사항이다.
5. **사용자에게 남아 있는 미결 결정**:
   - v1.6 채점 규칙 개정 여부 / v1.6 활성화 시점
   - Yahoo를 allowlist에 등재할지 (약관 검토 선행 조건)
   - Nasdaq Data Link 문의를 실제로 진행할지
   - C-06 (F9 자본잠식·영업손실 구간): 권고는 `proposed_v15_boundaries` + `diagnose_only` — **미결**
   - C-13 (F6 proxy 정책): 권고는 `reject_proxy` — **미결**
   - F6이 `pending_data`일 때 전체 AI 점수 처리: 제안은 "F6 제외 임시 총점은 참고용으로만 표시하고 공식 순위·승인에는 넣지 않음"

---

## 9. 참고 파일 인덱스

**설계진행 (판정 기록)** — `설계진행/validation/`

| 파일 | 내용 |
|---|---|
| `f6-h-sources-02-r1-review.md` | C-13 R1 검토, **needs_fix 4건** (가장 최신, 09-10) |
| `f6-h-sources-02-review.md` | 공급원별 12개사 일괄 조사 검토 |
| `f6-h-backtest-01-review.md` / `-02-review.md` | F6-H 백테스트 1차/재검증 판정 |
| `f6-implement-06-review.md` | F6 구현(`55e031f`) 검토, 커밋 `b978d36` |
| `f6-policy-decision-05-review.md` | 2Q proxy 금지·yfinance 제한 결정 |
| `nasdaq-public-endpoint-decision.md` | **api.nasdaq.com 배제 결정**, 커밋 `11fe94f` |
| `nasdaq-license-c13-01-review.md` / `-r2-review.md` | Nasdaq 라이선스 조사 판정 (미확정) |
| `spacex-*-review.md` (3건) | SPCX 티커·합병 범위·EPS 원천 |
| `fincept-consensus-01-review.md`, `fmp-estimates-02-review.md`, `finnhub-earnings-03-review.md` | 공급사별 조사 판정 |
| `consensus-research-method.md` | Valley 화면 참고한 수집·검증 방식 |
| `ntm-policy-review.md`, `ntm-handoff-review.md` | NTM 정책 초기 검토 |
| `memory/_daily/2026-09-10.md` | 9/10 오전 정정 기록 (하드코딩 판정 철회, 재현성 범위 정정) |

**worker** — `worker/validation/`: `f6h-source-batch-10/` (REPORT-R1.md, verify_window.py, window-verification.txt),
`f6-implement-06/`, `source-allowlist-07/`, `reverse-dcf-09/`, `f6-policy-decision-05/`, `spacex-*/`, `fmp-estimates-02/`, `finnhub-earnings-03/`, `fincept-consensus-01/`
**C-13** — `C-13/validation/`: `f6-h-sources-02/` (REPORT.md, verify_yahoo_evidence.py, yahoo_evidence_verification.json, run_source_comparison.py, raw_source_comparison.json), `f6-h-backtest-01/`, `nasdaq-license-c13-01/`, `consensus-source-2026-09-09/`

**주요 커밋**: `55e031f`(F6 구현) · `2fab64a`(v1.6 원천 정책) · `11fe94f`(Nasdaq 배제 결정) · `194fd4b`(worker R1, **검토 미완**) · `0c21074`(C-13 R1, needs_fix) · `da571bc`(C-13 Nasdaq 정정) · `bc92cfb`(F6-H 재검증) · `d054e32`(Reverse DCF)

---

## 10. 이 세션에서 반복적으로 터진 함정

이어받는 에이전트가 같은 실수를 반복하지 않도록 남긴다.

1. **보고서의 "PASS"를 그대로 믿지 말 것.** C-13의 "9/12 확보"는 원자료를 읽어 계산한 게 아니라 코드에 넣어둔 하드코딩 판정이었고, 이걸 통과로 처리한 리뷰를 나중에 정정해야 했다.
2. **"값이 있다"와 "채점 가능하다"는 다른 층이다.** raw-availability / window-verified / basis-verified / score-ready 네 단계로 분리해서 말한다.
3. **검증기 자체를 검증할 것.** 입력 통화를 KRW로 바꿔도 USD로 판정하는 등, 검증 코드가 상수를 쓰고 읽은 값을 무시하는 사례가 계속 나왔다.
4. **"조사 완료"와 "허가 획득"을 구분할 것.** 라이선스 문의 초안 작성을 라이선스 확인으로 잘못 보고해서 사용자에게 지적당했다.
5. **JSON으로 열린다 ≠ 사용 권한이 있다.** 전송 형식과 이용 약관은 별개다.
6. 사용자는 **"그래서 지금 뭐가 어떻게 된 건데"** 를 자주 묻는다. 장황한 절차 설명보다 **현재 상태 / 막힌 지점 / 남은 결정**을 먼저 짧게 답할 것.

---
---

# 부록 A — 중단 직전 대화 원문

Codex `thread_history_1.sqlite`에서 복원한 원문이다. `[숫자]`는 rollout ordinal, 시각은 KST.
`USER`는 사용자 입력 + Orca가 중계한 worker·C-13 완료 보고를 모두 포함한다.


### [6660] 09-09 23:11 · **CODEX**

맞습니다. 종목별로 공급원을 섞으면 기준이 달라지므로, **사이트별 공급원 단위로 12개사 전체를 일괄 조회한 뒤 비교**하는 방식이 맞습니다. worker와 C-13에 같은 조건으로 독립 조사를 맡기고, 공급원별 커버리지·회계·통화·ADR/ADS·시점 기준을 비교하도록 전달하겠습니다.

---

### [6686] 09-09 23:12 · **CODEX**

worker와 C-13 양쪽에 공급원별 일괄 조사를 전달했습니다.

각 에이전트는 종목마다 다른 사이트를 선택하지 않고, 후보 사이트별로 12개사를 한 번에 조회해 다음을 비교합니다.

- 2A+2E 확보율.
- 동일 공급원 여부.
- 회계 기준.
- 통화 기준.
- ADR·ADS 및 주식 단위.
- `asOf`와 point-in-time 가능 여부.
- 결측·음수 EPS.
- 약관과 재배포 조건.

메시지는 다음과 같습니다.

- worker: `msg_17dca6fbb7a0`
- C-13: `msg_9c9b44bc73ee`

두 터미널 모두 실행 안내를 받았고 현재 작업 중입니다. 결과가 나오면 **어느 사이트가 12개사 전체에 동일 기준으로 F6-H를 제공할 수 있는지**를 공급원별로 비교해 결정하겠습니다.

---

### [6695] 09-09 23:14 · **USER**

F6-H 사이트별 12개사 일괄 확보 및 기준 비교 조사 완료 알림: 메시지 msg_2223a8137fa4(스레드 msg_9c9b44bc73ee)를 확인하고 validation/f6-h-sources-02/REPORT.md, run_source_comparison.py, raw_source_comparison.json(커밋 2bc6274)의 6대 공급원별 일괄 확보율(최고 75.0%), ADR/ADS 단위 불일치 및 SPCX 결측 병목 분석 결과를 재검토해 주세요. 완료 회신은 Orca 스레드로 보내주시면 됩니다.

---

### [6698] 09-09 23:14 · **CODEX**

C-13의 공급원별 12개사 일괄 조사 커밋 `2bc6274`를 확인해 최고 75% 확보율과 단위·SPCX 병목이 실제로 F6-H 조건을 충족하는지 재검토하겠습니다.

---

### [6731] 09-09 23:15 · **CODEX**

C-13의 공급원별 조사 결과를 검토했고 회신했습니다(`msg_a1f2db433980`).

결론은 다음과 같습니다.

- 최고 확보율은 Nasdaq과 Finnhub의 **9/12, 75%**.
- 12개사 전체를 동일 기준으로 충족하는 공급원은 없음.
- Nasdaq은 TSMC·Alibaba ADR/통화 기준과 SPCX 실적 부족 문제가 있음.
- Finnhub도 동일한 단위 문제와 SPCX 결측이 있음.
- 모든 공급원에서 `asOf`와 외부 재배포 권한이 확정되지 않음.
- 종목별로 사이트를 섞는 방식은 배제.

따라서 **단일 공급원이 12개사 전체의 2A+2E 조건을 충족할 때까지 F6-H 자동 점수 활성화는 보류**합니다. 검토 기록은 [f6-h-sources-02-review.md](C:/Users/noble/orca/workspaces/stock-report-harness/설계진행/validation/f6-h-sources-02-review.md)입니다.

---

### [6740] 09-09 23:15 · **USER**

근데 아마 SPCX는 상장한지 얼마 안되서 그럴껄??

---

### [6743] 09-09 23:15 · **CODEX**

맞습니다. SPCX의 결측은 공급원 자체의 문제라기보다 **2026년 6월 상장으로 최근 확정 회계분기가 2개 미만인 신규 상장사 문제**일 가능성이 큽니다.

하지만 F6-H에는 여전히 중요한 제약입니다.

- F6-H는 최근 실제 2개 분기가 필요함.
- SPCX는 상장 전 실적을 현재 상장 주식 기준과 바로 연결하기 어려움.
- 상장 전 EPS를 억지로 이어 붙이면 주식 수, 법인 범위, 합병 시점 기준이 달라질 수 있음.
- 따라서 SPCX를 포함한 고정 12개사 전체에서는 F6-H 100% 커버리지가 불가능함.

정책은 이렇게 나누는 것이 합리적입니다.

1. SPCX는 `new_listing_insufficient_history`로 표시하고 2개 확정 분기가 쌓일 때까지 `pending_data`.
2. 상장 전 실적은 주식 기준과 법인 범위가 검증되지 않는 한 F6-H에 사용하지 않음.
3. 공식 F6 비교 대상은 “최근 2개 실제 분기가 확보된 상장사 universe”로 별도 정의.
4. 그 eligible universe에서는 하나의 공급원과 하나의 F6-H 모드를 전체 기업에 동일하게 적용.
5. 고정 12개사 리포트에서는 SPCX F6을 미산출로 표시하고, 임시 점수로 채우지 않음.

즉, SPCX를 제외하면 공급원별 커버리지가 9/12보다 높아질 수 있지만, **SPCX를 포함한 현재 전체 universe의 F6-H 조건이 충족된 것은 아닙니다.** 신규 상장사 예외 규칙을 별도로 두는 것이 맞습니다.

---

### [6752] 09-09 23:16 · **USER**

자 근데 지금 C-13은 nasdaq에서 다 뽑아왔네. 뭐여 쓰면 안된다며

---

### [6755] 09-09 23:16 · **CODEX**

맞습니다. 여기서 제가 지시를 섞었습니다. `api.nasdaq.com`은 생산 원천에서 배제하기로 했는데, 공급원 비교 조사에서 C-13이 기존 Nasdaq 샘플을 참고용으로 사용했습니다. **그 자료는 점수 입력이 아니라 비교용 증거**였지만, 배제 결정 이후 새 조회를 시키지 말았어야 했습니다. 이 부분을 즉시 정정하겠습니다.

---

### [6769] 09-09 23:16 · **CODEX**

맞습니다. C-13은 Nasdaq 데이터를 **공급원 비교용으로 다시 사용했습니다.** 그 자료를 생산 점수에 넣지는 않았지만, 제가 “Nasdaq 배제” 이후에도 비교 조사에서 조회하도록 지시한 것은 잘못입니다.

정확한 상태는 다음입니다.

- Nasdaq 샘플: 이미 확보된 참고용 검증 자료.
- 생산 입력·관측 등록·F6 점수·HTML 근거: 사용 금지.
- Nasdaq 9/12 수치: 채택 가능한 공급원 성과로 해석하지 않음.
- 배제 결정 이후 추가 `api.nasdaq.com` 조회: 중단.
- C-13에 보고서와 원자료를 `non-production reference`로 명시하도록 정정 지시 완료.

정정 메시지는 `msg_83604a546618`로 보냈고, C-13 터미널에도 실행 안내를 제출했습니다.

---

### [6778] 09-09 23:18 · **USER**

실행 안내 제출한거 맞어?c-13이 일 안하는데 지금

---

### [6781] 09-09 23:18 · **CODEX**

C-13 터미널의 실제 입력·실행 상태를 확인해, 안내가 접수됐는지와 작업이 멈춘 이유를 구분하겠습니다.

---

### [6790] 09-09 23:18 · **CODEX**

실행 안내 자체는 제출됐습니다.

- 메시지: `msg_83604a546618`
- 터미널 입력: `accepted: true`
- C-13 터미널 상태: `running`

다만 방금 터미널 화면을 다시 확인하니 C-13은 아직 이전 수신함과 기존 보고서를 확인하는 작업을 처리 중이고, `msg_83604a546618` 정정 작업을 실제로 시작한 화면까지는 나오지 않았습니다. 즉 **안내 제출은 됐지만 착수 완료로 볼 수는 없습니다.**

현재 C-13에 남아 있는 작업은 다음입니다.

- Nasdaq 기존 샘플을 `non-production reference`로 표시.
- 추가 `api.nasdaq.com` 조회 중단.
- 공급원 비교 보고서에서 Nasdaq을 생산 후보로 해석하지 않도록 정정.
- 기존 점수와 승인 자료 보존.

착수와 완료 회신이 확인되기 전까지는 작업 중이라고 단정하지 않겠습니다.

---

### [6799] 09-09 23:20 · **USER**

F6H-SOURCE-BATCH-10 완료 보고가 수신함에 있습니다. msg_17dca6fbb7a0 스레드를 확인해 주세요. 커밋 eb12dcb 이고 원자료 48건과 재현 스크립트 2종을 함께 커밋했습니다. 결론은 어느 공급원도 12개사 전부를 통과시키지 못한다는 것입니다. Finnhub 11/12, FMP 무료 0/12, SEC 0/12, Yahoo 11/12(미등재)이고 막히는 종목은 넷 다 SPCX 하나로 같습니다. FMP 는 period=quarter 가 유료 파라미터라 전 종목 402 이고 SEC 는 전망 필드 자체가 없습니다. 커버리지보다 중요한 것은 Finnhub 이 asOf 회계기준 통화 주식기준 표본수 minmax 를 하나도 제공하지 않는다는 점입니다. 값은 오지만 그 값이 무엇인지 공급원이 말하지 않습니다. Yahoo 는 통화를 명시해 BABA 전망이 CNY 인데 ADS 는 USD 로 거래되는 불일치를 드러냈는데 Finnhub 에서는 조용히 지나갑니다. 권고는 Finnhub 단일 공급원에 SPCX 는 pending_data 이고 종목별 혼합은 배제했습니다. 채택 전 선결 조건 넷은 회계기준, 두 endpoint 기준 일치, 통화·주식 기준, 추정 시각이며 앞의 둘은 Finnhub 문의가 필요합니다. 참고로 f6-implement-06 의 4분기 관문이 이 상태의 자료를 자동 거부하므로 정책은 의도대로 작동합니다. 검토 결과는 orca orchestration reply --id msg_17dca6fbb7a0 로 회신해 주세요.

---

### [6802] 09-09 23:20 · **CODEX**

worker의 공급원별 배치 조사 커밋 `eb12dcb`를 검토해 Finnhub 단일 공급원 권고가 F6-H 관문을 실제로 통과할 수 있는지 확인하겠습니다. 커버리지와 데이터 의미론을 분리해 판단하겠습니다.

---

### [6818] 09-09 23:21 · **CODEX**

worker의 공급원별 조사 결과를 검토했고 회신했습니다(`msg_ed8264ecbe66`).

결론은 다음과 같습니다.

- Finnhub: **11/12**. SPCX 신규 상장으로 2A 부족.
- Yahoo: **11/12**지만 약관 검토 전이라 후보에서 제외.
- FMP 무료: `period=quarter` 유료로 **0/12**.
- SEC: 전망 필드가 없어 **0/12**.
- Finnhub은 커버리지는 높지만 `asOf`, 회계 기준, 통화·주식 기준, 표본 수·min/max를 제공하지 않음.
- Finnhub의 실제값 endpoint와 전망 endpoint가 동일 기준인지도 확인되지 않음.
- BABA는 통화·ADS 기준 불일치 가능성이 확인됨.

따라서 Finnhub은 **11개사 단일 공급원 후보**로만 보류하고, SPCX는 신규 상장 이력 부족으로 `pending_data` 처리합니다. Finnhub 문의로 네 가지 기준을 확정하기 전에는 F6-H 자동 점수를 활성화하지 않습니다. 종목별 공급원 혼합도 계속 금지합니다.

---

### [6827] 09-09 23:21 · **USER**

Nasdaq 공개 샘플 비생산 참고용 정정 완료 알림: 메시지 msg_062aab116fdc(스레드 msg_83604a546618)를 확인하고 validation/f6-h-sources-02/REPORT.md, run_source_comparison.py, raw_source_comparison.json(커밋 da571bc)에 반영된 api.nasdaq.com 생산 배제 정책, non-production reference 표기 및 생산 후보 제외 정정 결과를 확인해 주세요.

---

### [6830] 09-09 23:21 · **CODEX**

C-13의 Nasdaq 샘플 정정 커밋 `da571bc`를 확인해 공개 API가 생산 입력에서 완전히 제외됐는지, 기존 샘플이 참고용으로만 표시됐는지 재검토하겠습니다.

---

### [6846] 09-09 23:22 · **CODEX**

C-13의 정정 커밋 `da571bc`를 확인했고 승인 회신했습니다(`msg_3dd48f97bd63`).

확인 내용:

- `api.nasdaq.com`은 `Denied`.
- 자동 수집·관측 등록·F6 점수·HTML 근거 사용 모두 금지.
- 기존 Nasdaq 샘플은 `non-production reference`로만 보존.
- 배제 결정 이후 추가 조회 없음.
- Nasdaq 9/12 수치는 기술 비교용으로만 남고 생산 후보에서 제외.
- 기존 점수와 승인 자료는 불변.

---

### [6864] 09-10 09:17 · **USER**

자 이제 마저 진행해보자

---

### [6865] 09-10 09:17 · **CODEX**

최신 수신함과 worker·C-13 산출물을 확인하겠습니다. 두 보고서의 확보율이 9/12와 11/12로 다른 이유를 원자료와 코드로 대조한 뒤, F6-H 채점에 실제로 남은 조건을 정리하겠습니다. Orca 조율에는 `orca-cli`와 `orchestration` 스킬을 사용하겠습니다.

---

### [6917] 09-10 09:20 · **CODEX**

검토 중 중요한 오류를 찾았습니다. C-13의 ‘9/12 확보’는 원자료를 읽어 계산한 결과가 아니라 코드에 넣어 둔 판정이었습니다. 이를 검증 통과로 처리한 이전 리뷰는 정정하겠습니다.

worker의 ‘11/12’는 저장된 응답으로 재현됐지만, 필요한 분기의 연속성과 EPS 기준까지 확인한 수치는 아닙니다. 이제 원자료에 값이 있는지와 실제 채점 가능한지를 구분해 보완하겠습니다.

---

### [6974] 09-10 09:22 · **CODEX**

보완 작업을 사이트별로 나눠 전달했고, 두 터미널에 실행 안내도 제출했습니다. worker는 Finnhub의 분기 연결을, C-13은 기존 판정 정정과 Yahoo 자료를 맡습니다.

이번에는 원천을 더 늘리지 않고 저장된 자료로 확인합니다. 핵심은 ‘최근 실적 2분기 + 다음 전망 2분기’를 같은 기준으로 연결할 수 있는지입니다. 일부 종목이 미달이라는 이유만으로 전체 방식을 불가능하다고 단정하지 않겠습니다.

---

### [6983] 09-10 09:24 · **USER**

아 그리고 이제 결과값 산출이 일관되는지도 확인은 당연히 하지? 예를 들어 동일한 DB(사이트)에서 추출/동일한 기준

---

### [6984] 09-10 09:24 · **CODEX**

응. **값을 확보했는지뿐 아니라, 같은 기준으로 비교·계산되는지도 확인해야 해.** 이번 검증에도 포함했어.

- **동일 공급원** — 종목별로 Finnhub·Yahoo를 섞지 않음. 같은 사이트라도 실적·전망 데이터의 기준이 같은지 확인.
- **동일 기간 규칙** — 분석 기준일을 고정하고, 기업별 최근 발표 실적 2분기와 바로 이어지는 미발표 전망 2분기를 연결.
- **동일 EPS 기준** — GAAP/조정 EPS, 기본/희석 EPS, 통화, 보통주/ADR·ADS, 주식분할 반영 여부를 맞춤.
- **동일 계산·점수 규칙** — 같은 버전의 산식과 점수 곡선 적용. 누락 종목은 다른 방식으로 대체하지 않고 미완료로 표시.
- **재현성** — 저장한 입력과 규칙이 같으면 재실행해도 같은 계산값과 점수가 나와야 함.

사이트가 같다는 것만으로 기준까지 같다고 인정하지는 않아. **현재 11/12는 값이 있다는 확인이고, 이 일관성 검증까지 통과했다는 뜻은 아니야.**

---

### [6993] 09-10 09:25 · **USER**

F6H-SOURCES-02-R1 보완 완료 알림: 회신 메시지 msg_40b0518293b5(스레드 msg_609ace096b37)를 확인해 주세요. 커밋 0c21074로 (1) 하드코딩 판정 철회 및 증거 수준 표기, (2) worker 저장원자료(_raw/yahoo 12건)의 SHA-256 해시 기록 및 4단계 분리 검증(값존재 11/12, 분기창 특정불가 0/12, 기준미달 0/12, 채점불가 0/12), (3) Yahoo와 Valley 분리, (4) 단일공급원 다중엔드포인트 허용 및 미검증 분리 등을 validation/f6-h-sources-02/REPORT.md와 yahoo_evidence_verification.json, verify_yahoo_evidence.py에 반영했습니다. python validation/f6-h-sources-02/verify_yahoo_evidence.py로 5대 검증 테스트를 재현할 수 있습니다.

---

### [6994] 09-10 09:25 · **CODEX**

C-13의 보완 회신과 커밋을 확인하겠습니다. 저장된 원자료에서 판정이 산출되는지, 같은 입력으로 결과가 재현되는지 직접 검증하겠습니다. Orca 회신에는 `orca-cli`와 `orchestration` 스킬을 사용합니다.

---

### [7038] 09-10 09:26 · **CODEX**

기존 자료로 5개 테스트가 통과했고, 두 번 실행한 결과와 커밋된 결과도 일치했습니다. 입력 파일 12개의 해시도 맞았습니다.

다만 말씀하신 ‘동일 기준’ 검증에서 오류를 찾았습니다. 임시 복사본의 거래 통화를 USD에서 KRW로 바꿔도 코드가 USD로 판단합니다. SPCX의 실적 행수를 바꾸면 상세 결과와 요약 건수도 달라집니다. 현재 자료의 재현성은 확인됐지만, 검증기 보완은 아직 필요합니다.

---

### [7069] 09-10 09:29 · **USER**

F6H-BATCH-10-R1 분기창 검증 보완 완료 보고가 수신함에 있습니다. msg_ca637f412da9 스레드를 orca orchestration check 로 확인해 주세요. 커밋 194fd4b 이고 파일은 worker/validation/f6h-source-batch-10/REPORT-R1.md, verify_window.py, window-verification.txt 입니다. 신규 네트워크·API 호출 없이 저장 원자료만 읽었고 원자료·점수·승인·규칙은 보존했습니다. 지적하신 대로 na>=2/ne>=2 는 창 검증이 아니었습니다. 판정을 넷으로 분리하니 raw-availability 11/12, window-verified 11/12, basis-verified 0/12, score-ready 0/12 입니다. 채점 가능한 기업은 0개사입니다. NVDA period 2026-09-30 이 수집 시점보다 뒤인데 actual 이 있는 것을 확인했고, 저장 SEC 와 대조해 회계연도가 달력과 어긋난 NVDA·AAPL·ORCL 에서 SEC 회계종료일 일치 0건, 달력분기말 일치 3건씩임을 산출했습니다. period 가 회계종료일이 아니라는 것만 확정하고 정확한 정의는 미확정으로 남겼으며 창 연결은 회계 라벨 (year, quarter) 로만 합니다. 두 endpoint 간 회계분기 중복은 12개사 전부 공집합이고, stock/earnings 에 발표일이 calendar/earnings 에 period 가 없어 공통 날짜 축이 존재하지 않습니다. basis 는 키 자체가 없어 12개사 unknown 이며 추측 통과시키지 않았습니다. 철회 두 건도 반영했습니다. SPCX 는 SEC 에 상장 전 분기 EPS -0.34 가 비교치로 존재하므로 상장 전 실적이 없다는 단정을 철회했고, FMP 는 유료 파라미터로 SEC 는 전망 필드 부재로 막히므로 SPCX 와 무관하다는 점을 바로잡았습니다. 확인 6건과 미확인 7건을 분리했고 다음 확인 1순위는 회계기준과 두 endpoint 기준 일치입니다. C-13 담당인 Yahoo·하드코딩 비교 철회는 중복 조사하지 않았고 Nasdaq 은 호출하지 않았습니다. 검토 결과는 orca orchestration reply --id msg_ca637f412da9 로 회신해 주세요. 진행 중인 작업이나 입력은 지우지 마세요.

---

### [7072] 09-10 09:29 · **CODEX**

worker의 완료 보고도 이어서 검토하겠습니다. 특히 ‘분기창 11/12 통과’가 공급사의 회계 라벨 연결만 확인한 것인지, 실제 분석 기준일에 맞는 분기까지 확인한 것인지 구분하겠습니다.

C-13에는 발견한 오류와 보완 요청을 보냈습니다. 현재 터미널에 사용성 설문이 떠 있어, 설문을 건너뛴 뒤 실행 안내를 제출하겠습니다.

---

> **[7086] 09-10 09:30 — 여기서 세션이 `usageLimitExceeded`로 종료됨.**
> Codex는 worker의 `verify_window.py`를 재현 실행하던 중이었고, `msg_ca637f412da9` 회신은 발송되지 않았다.
