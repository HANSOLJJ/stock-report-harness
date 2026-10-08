# 정기 실행 전부 재판단 체크리스트

## 0. 결정 (사용자, 2026-10-08 전부 확정)
- [x] 정기 실행은 정성 판단 전부를 다시 매긴다. 돌아가며 하지 않는다
- [x] 승계는 기업 추가 실행에만 남긴다. 정기 실행에서는 검증기가 거부한다
- [x] ① 사다리 **A**: 락인 강도(회수 루프·전환비용 중 높은 쪽) pass 4 / partial 3 / fail 1 / 채널 없음 0, 둘 다 unknown 이면 점수 없음. 가격 실측 pass +1·fail −1, 대체 공급 fail −1, 지속성 할인 −1, 0~5 로 자름. 가격 실측 pass 는 **8개 분기 이상 지속**. 전환비용 pass 는 **대체재가 있는데도 남은 것**(관계 수준), partial 은 설계·계약 수준
- [x] 부품 채널 일괄 상한 2 **삭제**. 지속성 할인 = 10-K 공시 10% 이상 고객이 있고 그 고객의 자체 대체재가 **출하 중**
- [x] ① 이름을 "네트워크 효과" → **"락인과 가격결정력"** 으로. 네트워크 효과는 회수 루프 입력으로 내린다
- [x] ② 세대 격차 = **시간**: 세 축 중 두 축 독립 측정 1위 + 2위가 도달하는 데 모델 **6개월**·하드웨어 **12개월**(대량 출하 기준) 이상. 벤더 발표만 있으면 부분 통과
- [x] ③ 가속도 지표 단계 a~e. 대리 지표(c)는 **최대 partial**, 사용량 시계열(d)은 매출과 같은 자격, 없음(e)은 점수 없음. 성장률 **두 개**(수준값 세 개)를 입력에 저장
- [x] ① `ai_monetized_in_channel` 구조 필드(yes/partial/no/unknown), 점수 밖, 표에 열로 표시
- [x] 첫 화면 요약 상자는 **10월 승인본에도 지금** 그린다(렌더러만 바뀌므로 승인 유지)

## 0.5 지금 할 것 (v2.0 과 독립)
- [x] 렌더러: 첫 화면 요약 상자(`render_judgment_status`, 요약 탭 KPI 아래). 승계 칸 수·항목별 분포·검토일, 기준선 이후 재판단 칸과 이번 실행 기간 재판단 칸, 숫자만 남은 칸, 지난 실행 대비 변경 칸 목록, 재검토로 넘긴 쟁점 수와 시점
- [x] 검증기: 상자 존재와 `data-carried` = results carried_score 칸 수
- [x] 테스트(Python 1320·Node 21 통과) → rescore·test 재빌드(승인 유지, 계약 PASS) → 커밋 3개(렌더러·출력·계획)
- [ ] push → 맥미니 3단계 갱신 (사용자 지시: 모든 단계가 끝난 뒤 한 번에)
- [ ] ① 시범: Microsoft·NVIDIA·Palantir·TSMC 네 회사에 네 입력을 스크래치에서 채워 본다. 빈 칸 비율과 사다리 A 결과를 context-notes 에 적는다. 점수 파일은 건드리지 않는다

## 1. 규칙 v2.0
- [x] `rules.md` 2.9절 "정기 실행은 모든 정성 판단을 다시 매긴다" (전부 다시 매김, `reconfirmed`, 승계는 기업 추가 실행만, 리뷰 예외도 기업 추가 실행만)
- [x] `rules.md` ① 절 재작성: "① 락인과 가격결정력", 채널 소비자·업무·거래(조직 고객은 업무), 네 질문 표(전환비용 pass = 대체재 있는데도 남음, 가격 실측 8분기), 지속성 할인, 사다리 표, AI 수익화 표시, 중복 금지, 상한 금지
- [x] `rules.md` ② 절: 세대 격차 시간 정의(`generation_gap_months`, 모델 6·하드웨어 12), 벤더 발표 = 부분(`leap_independent`)
- [x] `rules.md` ③ 절: 지표 단계 a~e 표(`acceleration_tier`), 성장률 두 개(`acceleration_growth_rates`)
- [x] `rules.md` 1절 표·6절 가짜 해자 표·8절 미결 표(세대 격차 행 삭제)·8절 승계 문장
- [x] `scorecard/rules/v2.0.json` (스크래치 `make_v20.py` 로 v1.9 에서 생성, `load_rules('v2.0')` 통과, 해시 3bf9418cf3eb…): F1 lockin 선언·사다리, F2 세대 격차·독립 측정, F3 지표 단계, F7 judgment_kinds, policies.rejudge, C-30, TEN-RC-02·RC3-03·RC4-02 resolved, 나머지 open 14건 recheck_at 2026-10
- [x] AGENTS.md: 정기 실행 재판단 항목 추가, 「리뷰 범위 — 승계 판단 예외」를 기업 추가 실행 한정으로
- [ ] `score-review`·`score-research`·`score-plan` 스킬 문구 (서브에이전트 C)

## 2. 스키마·엔진
- [ ] `schema.py`: ① 새 kind(가칭 `lockin`) — inputs: channels[], loop·switching·substitutes·pricing(pass/partial/fail/unknown), durability_discount(yes/no), ai_monetized_in_channel. F1 허용 kind 에서 `score` 제거(v2.0 이상)
- [ ] `schema.py`: ③ criteria inputs 에 `acceleration_tier`(a~e)·`acceleration_growth_rates`(두 개) 추가, c 단계면 acceleration ≤ partial 검증
- [ ] `schema.py`: ② paths inputs 에 `generation_gap_months` 와 독립 측정 여부 — 벤더 발표만이면 leap ≤ partial 검증
- [ ] `schema.py`: 판단 `reconfirmed` 선택 키 [{at, by, evidence_ids}] 검증
- [ ] `schema.py`/`stages.py`: 정기 실행(run.json 에 add_companies 없음)에서 `status: carried` 를 거부. 기업 추가 실행은 기존 회사만 허용
- [ ] `calc_qual.py`: ① 사다리 계산, 지속성 할인, `basis` 라벨
- [ ] `render_html.py`/`render_common.py`: ① 판정 입력 표시, BASIS_DOC 갱신
- [ ] 승인 페이지 `judge`: ① 입력란(JUDGMENT_EDIT_KIND·JUDGMENT_INPUT_CHOICES)
- [ ] 테스트: ① 사다리 경계값, 정기 실행 carried 거부, reconfirmed 검증, 기존 T-01~T-12·R01~R06 통과
- [ ] 10월 이하 실행(v1.9)은 그대로 열리는지 (규칙 버전별 kind 허용)

## 3. 리포트 (요약 상자는 0.5 절에서 먼저)
- [ ] ① 칸에 네 입력과 할인 표시, `ai_monetized_in_channel` 열
- [ ] ③ 칸에 지표 단계 표시
- [ ] 판단일 분포(항목별 최종 `reviewed_at`)

## 3.5 새 관측 metric (11월 수집)
- [ ] `gross_margin_ttm` 상장 12사 (10-Q·10-K, TSMC·Alibaba 는 6-K/20-F)
- [ ] `top_customer_share` 공시하는 회사 (NVIDIA·TSMC·Broadcom 류)
- [ ] `rpo_next12m_share` 상장
- [ ] 회사별 있는 것만: `nrr`(Palantir), `paid_seats`(Microsoft Copilot), `mau`(Gemini·Meta AI 시계열), `token_share`·`price_per_m`(OpenRouter, 모델 기업), `customer_prepayments`(TSMC), `fsd_subscribers`(Tesla)
- [ ] 사건 근거: 가격 인상 공지·보도, 이탈 보도, 경쟁사 출하(경쟁사 10-Q 도 EDGAR 로), 가격 페이지 스냅샷

## 4. 10월 v2.0 재실행 (11월을 기다리지 않는다 — 2026-10-08 사용자 결정)
- [x] 실행 `ai-scorecard-2026-10-rejudge` 생성(`init --from-run ai-scorecard-2026-10-rescore --rule v2.0 --as-of 2026-10-08 --price-as-of 2026-10-07 --info-cutoff 2026-10-08`). 규칙 해시 변경 경고는 예상된 것
- [x] collect(all, since 2026-09-02): 후보 5,427건(10-06 이후 뉴스 1,510건, 공시 15건), 가격·시총 12사 2026-10-07 종가
- [x] 작업 분할 확정: 수집·트리거·관측은 회사 묶음 5개(A nvidia·tsmc·apple / B alphabet·amazon·microsoft / C meta·oracle·palantir / D anthropic·openai / E alibaba·tesla·spacex-xai, `GROUP-INSTRUCTIONS.md`), 판단은 항목별 7세션. 산출물은 `work/out-<G>.json`, 합치기는 `work/merge_group_outputs.py`
- [x] 묶음 5개 산출물 합침(근거 +140, 트리거 56/56 이어받음 + 새 21, 관측 +108, 출처 +109) → `confirm` 138건(검토자 claude, 사용자 위임) → 근거 741 확정·2 후보, load_context 통과. 묶음 보고는 `work/report-A~E.md`
- [x] init 결함 수정(표지 인용 근거 누락) 커밋, 재실행 근거 603건 복원
- [ ] 판단 세션 7개(①②③④⑤⑦⑧, opus) 동시 실행 중 → `work/judge/<F>-<company>.json` → `apply_judgments.py` 로 propose → `proposal --all-pending --accept`
- [ ] 10월 미해결 12건(Q02·Q03·Q05·Q08·Q09·Q10·Q12·Q13·Q16·Q19·Q20·Q23) 처리
- [ ] research → `diff --against ai-scorecard-2026-10-rescore` → calculate → draft
- [ ] review (승계 예외 없이) → 승인 대기 보고

## 5. 마무리
- [ ] TODO.md 5번(①②④⑧ 질문 분해)에서 ①·② 완료 반영, ④⑧ 은 남김
- [ ] context-notes 에 11월 점수 변화와 순위 변화 기록
