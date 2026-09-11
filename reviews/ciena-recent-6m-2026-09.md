---
slug: ciena-recent-6m-2026-09
status: pass
reviewed_at: 2026-09-07
plan_source: plan/ciena-recent-6m-2026-09.md
research_source: research/ciena-recent-6m-2026-09.md
draft_source: drafts/ciena-recent-6m-2026-09.md
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - role: fact-checker
    model: claude-fable-5-1
    session: separate
  - role: content-editor
    model: claude-fable-5-1
    session: separate
  - role: report-designer
    model: claude-fable-5-1
    session: separate
  - role: codex-independent
    model: claude-fable-5-1 (general-purpose subagent, 독립 계약 점검)
    session: separate
---

# 4-Way Review: ciena-recent-6m-2026-09

네 리뷰어 모두 1차 결과는 `needs_fix`였다. 지적 항목을 모두 반영한 뒤 `python3 scripts/validate_report_contract.py ciena-recent-6m-2026-09`와 빌더 렌더 시뮬레이션으로 재검증해 `pass`로 확정했다.

## 1. Fact-Checker (separate subagent session)

- **pass** plan/research/draft/price-chart JSON/news JSON/holders JSON 모두 ticker `CIEN`, 기간 `2026-03-07`~`2026-09-07`, slug 일치. 가격 JSON 126행, 2026-03-09~2026-09-04 오름차순.
- **pass** 가격 수치 재계산: 시작 `$318.54`, 종료 `$321.00`, 수익률 +0.77%, 최고 `$627.00`(06-02), 최저 `$317.46`(09-03), 최대 낙폭 −49.37%, 종료가의 최고가 대비 −48.80%, 변동성 79.17%(모집단 표준편차), 급등·급락 상위 6일과 월말 종가 모두 일치.
- **pass** FY2026 FQ1~FQ3 실적 수치, 가이던스, 10% 고객 비중, 자사주, 부문 매출, 현금, CEO 인용, 전환사채 조건을 IR 원문(S1~S4)으로 확인. 2차 출처 S6·S7·S9~S17 원문 확인.
- **pass** 뉴스 100건 전부 Google News 중계 URL, `url_is_fallback: false`, 최신순 상위 5건이 draft와 일치.
- **pass** 미국 주식이므로 한국식 수급 섹션 없음. 투자 권유·목표주가 제시 없음.
- **fixed** 리스크 요인 "10% 넘게 움직인 날 여섯 번" → 가격 JSON 재계산 결과 8일로 수정하고 research 주가 데이터 메모에 해당 행을 추가했다.
- **fixed** 애널리스트 의견 인원 19명 → 투자의견 분포 합계 20명으로 draft/research 수정. `numberOfAnalystOpinions`(19)는 목표주가 제시 인원이라는 설명을 research에 추가했다.
- **fixed** research "4개월 전 대비" 문장을 JSON 구간(0m/−1m/−2m/−3m)에 맞게 "1개월 전 대비 보유 +1, 강력매도 소멸 / 3개월 전 대비 매도 계열 소멸"로 수정.
- **fixed** "다음 날 8개 증권사" → "발표 당일 저녁부터 다음 날에 걸쳐 8개 증권사"로 draft/research 수정(Needham은 09-03 당일).
- **fixed** research "6억달러 늘었고" → "6억달러 이상", 08-18 "8.0%" → "장중 8.0%"로 정확도 보강.

## 2. Content-Editor (separate subagent session)

- **pass** 문장 끝 콜론 없음. 메커니즘 중심 서술. 금지 표현 없음. 면책 문구 존재. H1 1개, 필수 섹션 모두 존재.
- **fixed** 변동성·낙폭 문장의 논리 오류("…는 …여섯 번 있었다는 뜻이다") → 사실 서술 두 문장으로 분리하고 8일로 수정.
- **fixed** 밸류에이션 배수(120배·77배·153배·71.97배)의 산출 기준 차이를 설명하는 단락을 메커니즘 1)에 추가.
- **fixed** "가이던스", "컨센서스", "밸류에이션" 정의를 개요 표 도입 문장에 추가.
- **fixed** 약어 풀이: 회계연도(FY), FQ1~FQ3 설명, ±50bp → ±0.5%포인트, 13F 공시 설명, GPU·CEO·CFO·CSO 풀이, 잉여현금흐름 정의, 코히어런트 설명.
- **fixed** 통화 표기 통일 "주당 1,000달러" → `$1,000`. 성장률 부호 표기(+70%, +111%, +215%, +271%, +50%, +30%).
- **fixed** 중복 제거: 리스크 요인 "공급 제약" 불릿을 메커니즘 2) 참조로 축약, 메커니즘 3)의 마진 수치 반복을 표 참조로 축약, "목표 주가를 제시하지 않는다" 반복 4회 → 2회.
- **fixed** 메타 문장에 붙은 무의미 표식([P1], [S3]) 삭제. 컨센서스 `$1.46`과 EPS 전년 대비 증가율을 research에 보강해 draft 근거를 확보.
- **fixed** 권장 사항 반영: 기업 개요를 제품명 나열 대신 범주로 단순화(약 8,900명), 전환사채 헤지 문장을 쉬운 말로 풀이, 본문 날짜를 `YYYY-MM-DD`로 통일, stat-card compare에 "종료 종가 기준" 명시, "여전히 긍정적이지만" → 중립 서술, Tier C 수치에 매체명 부착, 뉴스 시각을 KST로 변환, S5를 본문에서 인용.

## 3. Report-Designer (separate subagent session)

- **pass** H1 1개, 섹션 순서 개요→배경→메커니즘→최신 뉴스 5건→영향과 적용→핵심 정리→References→투자 유의사항. `price-chart` 블록 완전, `chart` JSON 유효(6개 라벨, ariaLabel 있음). stat-card 형식 정상.
- **pass** 히어로 v3 PNG 직접 확인: 광섬유 빛과 광모듈(수요) 대 추와 부품 더미(공급 병목·밸류에이션 부담)의 저울 구도. 텍스트·숫자·티커·로고·워터마크·UI 없음. 매니페스트 `complete`, `codex-cli-imagegen`, 선택 근거(점수 49>46>45) 타당.
- **pass** 초급 난이도 plan 일치. 토스 계약 요소(560px 셸, 고정 반투명 앱바, Pretendard, 토스 블루, 상승 빨강/하락 파랑, 8px 구분선, 히어로 카드, 우측 Y축, 면책 footer)를 `scripts/build_report.py` 코드로 확인.
- **fixed** 급등·급락 표와 실적 표의 `근거` 열이 빌드 후 빈 셀로 남는 문제 → `근거` 열 삭제, 표식을 마지막 텍스트 셀 끝으로 이동.
- **fixed** 최신 뉴스 5건 하위 불릿 3칸 들여쓰기 → 4칸으로 수정. 추가로 빌더의 공백 정리 정규식이 줄 앞 들여쓰기를 지워 중첩 목록이 풀리는 문제를 발견해 `report_contract_lib.strip_source_markers`를 수정했다.
- **fixed** `[H1]` 표식이 최종 HTML에 남는 문제 → `report_contract_lib.SOURCE_MARKER_RE`와 `build_report.SOURCE_MARKER_PREFIX_RE`를 훅과 같은 `S|N|P|H` 집합으로 확장.
- **deferred** 히어로 가격 표기(`$321`), 태그 휴리스틱, 차트 시각 확인은 stock-build 후 최종 HTML에서 확인한다.

## 4. Codex-Independent (separate subagent session)

- **pass** plan 필수 13개 키, draft 필수 11개 키, `plan_source`/`research_source` 경로 정확. 기간 184일(366일 이내), assumptions에 기본 6개월과 "향후 = 관찰 변수" 해석 기록.
- **pass** price-chart JSON(slug/ticker/period/rows/labels 오름차순/ariaLabel), 뉴스 100건 JSON(url·url_is_fallback), image-manifest(complete, 금지어 없음), selected-image JSON(실제 PNG 해석) 계약 충족.
- **pass** 한국식 수급 섹션 없음. `## 투자 유의사항`이 빌더 DISCLAIMER_SECTION_RE에 매칭되어 footer로 이동함을 시뮬레이션으로 확인.
- **fixed** draft가 research 범위를 넘던 주장 4건(10% 초과일 수, 기업 개요, 컨센서스 `$1.46`, EPS 전년 대비 증가율)을 research에 근거와 함께 추가.
- **fixed** `report_contract_lib.rel()`이 Windows에서 백슬래시 경로를 돌려줘 `plan_source` 비교가 항상 실패하던 버그 → `as_posix()`로 수정.
- **fixed** `strip_source_markers`가 개행을 삼켜 `::stat-card` 블록이 파싱되지 않던 버그 → 공백 정규식에서 개행 제외.

## Contract Validator and Simulation

- 빌더 `transform_body` 시뮬레이션: 잔존 표식 0개, stat-card 렌더 확인, 표 2개에 빈 셀 0개, 뉴스 5건 중첩 목록 렌더, 차트 2개(가격·뉴스 주제), 면책 섹션 본문 제거 확인.
- 가드레일 훅 `enforce-citations.sh`, `forbid-financial-advice.sh`를 수정 후 draft에 직접 실행: 차단 없음.
- `python3 scripts/validate_report_contract.py ciena-recent-6m-2026-09` 결과 `[PASS]`: frontmatter 정합, plan 필수 키, H1 1개, 필수 섹션, price-chart 블록, review pass, image manifest complete, selected PNG, price chart JSON 모두 ok. 경고는 빌드 전 HTML 부재 1건뿐이었다.
- 빌드 후 `--require-html --require-price-chart` 재검증도 `[PASS]`: Toss 셸 요소 11개, 마커 제거, 선택 히어로 참조까지 ok.

## Build Gate

통과: `/stock-build ciena-recent-6m-2026-09` 진행 가능. 히어로 이미지는 Codex CLI imagegen으로 생성된 v3를 사용한다.
