# QWEN-NTM-DATA-03 작업 지시 보존본

> 이 파일은 `/compress-fast` 등 컨텍스트 압축 후에도 작업 지시가 유실되지 않도록
> 원문 `msg_084a5c82912d` 를 그대로 보존한 것이다. 압축 후 이 파일을 다시 읽고 진행할 것.

## 메시지 메타

| 항목 | 값 |
|---|---|
| message id | `msg_084a5c82912d` |
| run_id | `run_1243c2a83479` |
| from_handle | `term_a3370266-4d39-4c5c-95a7-38ce1a1b744c` (설계진행, codex) |
| to_handle | `term_3c4739b1-418f-4dfa-aa95-6852cf5b1b2e` (scarpper, qwen-code) |
| subject | QWEN-NTM-DATA-03: 나머지 상장사 Forward PER 검증 및 원자료 확보 |
| type / priority | status / normal |
| thread_id | `null` (스레드 시작 메시지) |
| sequence | 31 |
| created_at | 2026-09-08T12:47:35Z |
| sender_pane_key | `297feb0c-2d90-43df-b435-c92f28fa3426:c2311e95-b233-496c-bffe-2bd4efc4b37f` |

## body 원문

사용자가 C-13 worktree와 scarpper에 병렬 자료 확보 검증을 맡겼습니다. 당신은 나머지 상장사의 NTM 자료를 맡습니다. TSMC·Alibaba는 C-13의 Antigravity가 별도로 조사합니다.

[배경 정정] 현재 worker의 vendor_forward_pe_verified_ntm는 StockAnalysis를 새로 조회하거나 4분기 EPS를 합산한 결과가 아니라 원본 HTML 설명을 승계한 method입니다. status는 legacy_unverified이며 실제 ntm_eps 관측은 기준선에 없습니다. 따라서 명칭만으로 검증 통과하지 마세요.

[대상] Meta, NVIDIA, Alphabet, Microsoft, Amazon, Apple, Oracle, Palantir, Tesla 및 레지스트리에 상장으로 기록된 SpaceX/xAI. 이 마지막 대상은 실제 평가 시점 상장/거래종목 존재와 ticker부터 확인하고 원본 가정을 사실로 믿지 마세요. 비상장 확인이면 공개시장 NTM 대상에서 제외하고 근거를 남깁니다.

[참조 읽기 전용] C:/Users/noble/orca/workspaces/stock-report-harness/worker/docs/scorecard/design-guideline.md, docs/scorecard/open-items.md, scripts/scorecard/baseline_import.py, scripts/scorecard/calc_f6.py, scorecard/companies.json, scorecard/baseline/v1.5/observations.json. 현재 worker 96d88bc.

[조사] 모든 대상의 공급사 원문 페이지와 정의 문서를 조회해 Forward PER이 향후12개월 NTM인지 다음회계연도 FY1인지 불명인지 구분하세요. StockAnalysis forecast 표의 연간 EPS와 Financial currency/adjusted 주석을 반드시 확인하세요. 가능한 향후4분기 EPS를 확보하거나 NTM 정의가 입증된 공급사 PER을 확보하고 회사별 충족표를 만드세요. 다음1분기 예상만 있거나 과거실적4개이면 미충족입니다. 주가/PER 역산만으로 분모의 기간은 증명되지 않습니다. 기업별 URL, 조회시각, 값/통화/주식단위, GAAP/조정, 전망 기간, 추정치 기준시각, 계산방법 근거, 무료/유료/차단 범위 및 자동수집 가능성을 남기세요. 현재 공개 접근 자료와 2026-09-02 기준 재현 가능 여부는 분리합니다. 현재 전망치를 과거로 소급하지 마세요. 유료가입/구매/계정변경 없이 공개 자료로 진행하고 확보 실패를 데이터 부재로 단정하지 마세요.

[산출물] 자기 validation/qwen-ntm-data-03/REPORT.md 및 evidence.json. 10개 대상 전부를 확보/일부확보/미확인/대상제외로 구분하고 재현 가능한 근거를 남기세요. 수집스크립트가 필요하면 자기 경로에서만 작성·테스트하고 새 소스 첫줄 한국어 주석, 커밋 trailer 금지. worker/원본/C-13 수정 금지, 점수/승인/정책 결정 금지.

[회신] 즉시 orca orchestration reply --id <이 메시지ID> --body <수신 확인과 착수> --json으로 회신하고 완료 시 같은 ID로 결과요약·보고서·커밋·미확보 이유를 전달하세요. reply는 run_1243c2a83479로 돌아옵니다. 기존 작업 전달이며 dispatch가 없으니 worker_done을 쓰지 마세요. 필요하면 orca skills get orchestration --json으로 문법 확인. 이전 입력창의 /compress-fast는 필요시 압축 후 진행하되 이 작업 지시는 보존하세요.

## 착수 시 체크리스트

- [ ] 수신 확인 reply 발송 (`--id msg_084a5c82912d`)
- [ ] worker HEAD 가 `96d88bc` 인지 확인 (이전 검증은 `ea1ecf0`)
- [ ] 참조 파일 6종 읽기 전용 확인 + 시작 해시 기록
- [ ] `companies.json` 에서 SpaceX/xAI 가 상장으로 기록돼 있는지 확인
- [ ] SpaceX/xAI 의 실제 상장·거래종목 존재와 ticker 우선 확인 (게이팅)
- [ ] 대상 10개사 각각 공급사 원문 페이지·정의 문서 조회
- [ ] StockAnalysis forecast 표의 연간 EPS + Financial currency/adjusted 주석 확인
- [ ] NTM(향후 12개월) / FY1(다음 회계연도) / 불명 구분
- [ ] 회사별 충족표 작성 (확보 / 일부확보 / 미확인 / 대상제외)
- [ ] evidence.json + REPORT.md 작성 (`validation/qwen-ntm-data-03/` 안에만)
- [ ] 종료 해시 기록해 대상 불변 확인
- [ ] 완료 reply 발송 (결과요약·보고서 경로·커밋·미확보 이유)

## 제약 요약

1. `worker/`, 원본(`E:\sourcecode\...`), C-13 worktree — **수정 금지** (읽기 전용)
2. 점수·승인·정책 결정 금지
3. 유료 가입·구매·계정 변경 없이 공개 자료만
4. 확보 실패를 데이터 부재로 단정 금지
5. 현재 전망치를 2026-09-02 로 소급 금지
6. 주가/PER 역산만으로 분모 기간 증명됐다고 주장 금지
7. `vendor_forward_pe_verified_ntm` 라는 명칭만으로 검증 통과 처리 금지
8. 수집 스크립트는 자기 경로에서만 작성·테스트, 새 소스 첫 줄 한국어 주석, 커밋 trailer 금지
9. dispatch 없음 → `worker_done` 등 lifecycle 메시지 금지
10. TSMC·Alibaba 는 범위 밖 (C-13 의 Antigravity 담당)
