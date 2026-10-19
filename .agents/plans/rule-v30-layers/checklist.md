# 규칙 v3.0 체크리스트

설계는 `plan.md`(2026-10-14 대화의 설계안 사본, 규칙 문언의 원본은 rules.md), 구현 순서는 `implementation.md`(2026-10-14 승인된 구현 계획)를 따른다. 단계 하나가 커밋 하나다. 이정표(기반 S0~S5, 계산 S6~S9, 출력·시범 S10~P1)마다 사용자에게 보고한다. 단계마다 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 를 돌린다.

## 문서
- [x] v2.2 초안의 커밋하지 않은 ②③ 수정과 context-notes 를 `draft/rules-v2.2` 에 기록용으로 커밋
- [x] `draft/rules-v3.0` 브랜치 생성
- [x] 계획 폴더(plan·checklist·context-notes) 생성
- [x] S1b rules.md 를 v3.0 으로 절 단위 개정(머리말, 1 총점, 2.10 층과 단위·2.11 끝난 싸움, 3 ①~⑤, 4 ⑥~⑨, 5 합산, 7 체크리스트 Q24·Q25, 8 미결). `test_scorecard_fix52_docs` 는 v3.0.json 이 생길 때(S2)까지 빨강

## 코드 (시험 실행까지 최소 경로)
### 이정표 1: 기반
- [x] S0 승인된 rejudge(v2.0)·v21(v2.1) 실행을 재계산 해시 테스트에 넣기(main e1e4d30, `tests/test_approved_runs_recompute.py`)
- [x] S0b 승인 페이지의 중첩 재료 `[object Object]` 표시 고치기(main 29e1167)
- [x] main 을 `draft/rules-v3.0` 에 병합
- [x] S2 `scorecard/rules/v3.0.json` 과 스키마 수용(layers, unit, curve, 새 judgment kind, 체크리스트 Q24·Q25). v2.1.json 을 출발점으로 생성했고 함정 구간표는 ×4 값을 함께 둔다. 계산은 아직 옛 경로(S3~S9 에서 붙임)
- [x] S3 연속 구간 도우미와 ⑥·⑨ 곡선, ⑦·⑧ ×4. 비상장 기업가치가 범위면 `policies.f6.estimate_range_end`(low·high·mid)가 정할 때만 점수, 없으면 needs_rule_decision(P0 에서 정함)
- [x] S4 판단 키에 layer·business, 다섯 판정 재료의 모양 검사, 매출 줄 교차 검사, `JudgmentLookup.units`, 중첩 근거 교차 참조, 제안의 layer·business 키(`rejudge_findings` 는 이미 판단 ID 단위라 테스트로만 잠금)
- [x] S5 층·사업 판단 생성·수정 경로, init 단위 전환, 트리거·근거 교차 참조 처리(다른 회사 근거 인용 결함 수정), CLI `--layer`·`--business`, v3.0 실행의 `diff` 거부, 승인 페이지 카드 id 와 층·사업 판단 읽기 전용
- [x] 이정표 1 보고(2026-10-14, ④ 부문 이익률 미공시·기업용 소프트웨어 결정 받음)
### 이정표 2: 계산
- [x] S6 ④ 보유표와 층 무게(`calc_layers.py`). 로켓 발사의 그 분야 순위 비교는 시장 정의표가 생긴 뒤(경고만)
- [x] S7 ②③ 층 계산(`calc_layers._layered`·`compute_f2_layers`·`compute_f3_layers`). 미확인 경로는 판정 대기, ③ 가속도 결측만 0 + 자료 없음
- [x] S8 ① 사업 단위 계산(시장 자료 전, D·E 는 미확인 1.6 씩). AI 상한 16 은 시장 자료 전에는 걸릴 수 없다(최고 15.2)
- [x] S9 ⑤ 동맹 세 부분·적대 띠(`calc_qual.compute_f5_alliance`). 긴장·구제 조치 미확인은 나쁜 쪽에서 40% 간 값
- [x] 이정표 2 보고
### 이정표 3: 출력·문서·시범 실행
- [x] S10 초안·미리보기 렌더 최소(층 표, 층·사업 판단 근거, v3.0 방법 절, 연속값 안내, 미리보기 척도 환산 참고값). v21·rejudge 초안·미리보기는 바이트 그대로
- [x] S11 structure·guide·score-research·score-review 문서(`.claude/skills` 원본만. `.agents/skills` Codex 사본은 v2.1 부터 뒤처져 있어 별도 과제)
- [x] P0 시범 init 전 규칙 값 확정 — 비상장 범위는 가운데 배수(`estimate_range_end: mid`). 나머지(④ 문턱, ⑥ P2·5% 절벽·신규 상장 P4, 기준선 80·56)는 시범 결과를 보고 정한다(사용자 결정)

## 시험 실행
- [ ] P1 시범 `init ai-scorecard-2026-10-v30pilot --from-run ai-scorecard-2026-10-v21 --rule v3.0 --companies alphabet,apple,tsmc,spacex-xai,anthropic` 으로 draft 까지
  - [x] Alphabet 판단 세션(판단 29건, 판정 대기 없음)
  - [x] 기준일 10-14 로 이동(`set-as-of`), 확정 근거 회사 무관 이월, init diff 안내 수정
  - [x] 규칙 빈틈 넷(개발 플랫폼, 몫 0 층, 가속도 20%, 정부 계약) 사용자 결정 반영 → `ai-scorecard-2026-10-v30pilot2` 로 이어받기(모양 맞지 않는 판단 제외)
  - [x] 다섯 세션 1단계(조사·초안, 병렬) → 사건 교차 대조 → 2단계(반영, 한 회사씩), Antigravity 사건 추가(사용자 지시)
  - [x] research 트리거 검사 결함·조정총점 부동소수·초안 표시 셋 수정
  - [x] research → calculate → draft(`ai-scorecard-2026-10-v30pilot2`, 5개사 완료·판정 대기 0)
  - [x] 보고 뒤: 남은 규칙 값 결정(④ 문턱, ⑥ P2·5% 절벽·신규 상장 P4, 기준선 80·56) + 시범에서 나온 규칙 빈칸(① B, ③ 모방, ② 표준의 층) — bee640b
  - [x] `ai-scorecard-2026-10-v30pilot3` 으로 이어받아 판단 19건 갱신(PRP-001~019), research → calculate → draft
  - [ ] 리뷰(4영역)는 사용자 지시 뒤에(시장 정의표 전이라 순위 판단에는 쓰지 않는다)
- [ ] 전체 14개사 시험 실행

## 시장 정의표 (계획 `market-tables.md`, 2026-10-15 착수)
- [x] 사용자 결정: 소비자 기기 출하 대수, 시장 범위는 조사기관 단위 우선(없으면 회사가 꼽은 경쟁자), 공시 없는 시장은 참고만
- [x] rules.md 8절 "묶음 안 시장 없는 구성 → 0" 행 정리(미확인 1.6)
- [x] 정의표 스키마·검증, 규칙 JSON 해시 연결(57bb146)
- [x] `calc_market.py` 와 `compute_f1_business` 연결, 테스트(57bb146), 상위 목록 밖 D 0·사용량 단위(0ed4959)
- [x] 초안 렌더(9efecb0)
- [x] 시범 시장 자료 수집(Sonnet 셋), 정의표 일곱 개(df78efd). 소셜 광고는 같은 단위 공시가 없어 만들지 않음
- [x] `ai-scorecard-2026-10-v30pilot4` 로 이어받아 시장 관측 96건, 사업 판단 21건 연결(PRP-001~021), research → calculate → draft
- [x] 미확인 사업 가운데 기준에 맞는 두 시장 추가: YouTube → Nielsen The Gauge(미국 TV 시청 배급사별, 분기 = 세 달 평균), X 광고 → StatCounter 소셜 미디어 유입(분기) — 6338da4, pilot5
- [x] 한 회사의 여러 구성 회사를 합쳐 재는 계산(95f20c4)과 소셜 미디어 Meta 표시(60355db) — pilot6
- [x] 정의표 9개 원문 재대조(fact-checker, Sonnet) — 값 146건 일치, 순위 판정 결함·기록 넷 수정, pilot7
- [x] 나머지 9개사 매출 줄별 시장·무료 정기 출처 조사(Sonnet) → 새 정의표 목록과 사용자 결정 거리 정리(`market-survey-9.md`)
- [x] 조사 결정 거리 사용자 결정(Windows→데스크톱 OS, Amazon 구독→TV 시청, Tesla 행 바로잡음, Gartner·StatCounter·OpenRouter 씀, ARTW 제외, 5개사 리뷰 먼저)
- [x] 부분 반영 계산(사용자 제안): 덮는 비율을 알면 그 비율, 모르면 50%, 간접 자료 50%, 둘이면 곱함. 소셜·TV 시청을 간접 자료로 표시
- [x] 새 정의표: AI 챗봇(StatCounter) 넣음. AI 모델 API(OpenRouter)는 1년 전 값·시험 모델 문제로 14개사 확장 때 다시 봄
- [x] pilot8: 덮는 비율 partial(Google Cloud·Apple 웨어러블·xAI AI 솔루션), 판정 문장 여섯 건(PRP-001~006) → research → calculate → draft
- [x] 5개사 4영역 1차 리뷰(영역 넷 + 회사별 사실·출처 다섯 + 근거 불릿)
- [x] 수정 묶음(코드 다섯 커밋, 판단 PRP-007~041, 자료 수정) → research → calculate → draft
- [x] 확인 리뷰 1회(남은 발견 C-1 은 사용자 결정으로 PRP-042) → review.md pass → 계약 검증 통과
- [x] 승인(2026-10-19 사용자, 승인 페이지) — approval_valid true
- [ ] 빌드: v3.0 HTML 렌더가 없어 불가(뒤로 미룸 항목)
- [ ] 14개사 확장 때: desktop_os·Tesla BEV(행 바로잡음)·Gartner 반도체(NVIDIA 58%)·Amazon 구독 연결·cloud_infra Omdia 설명 정정
- [ ] 보고 뒤: 리뷰(4영역) 또는 14개사 확장

## v3.0 HTML 리포트 (계획 `html-report.md`, 2026-10-19 착수)
- [x] 고치기 전 v21·rejudge·pilot8 HTML 을 스크래치에 그려 두기(바이트 대조 기준)
- [x] 1 기업 카드: 층 표(몫 있는 층만, 몫 0 판매 층은 한 줄)·시장 표, ①②③ 층·사업 판단 근거 접는 블록
- [x] 2 "참고" 줄의 층·사업 ID 와 이름 목록을 읽히는 이름으로(HTML 만, 초안·결과는 승인 대상이라 그대로)
- [x] 3 요약: 열한 층 보유표(칸 글자 + 매출 몫, 층 밖 사업·주 층·AI 무관 매출·④) 와 비교 그룹 안 순위
- [x] 4 산점도: 과점 기준선 80·56(잠정), v3 축·눈금, 열한 층 점 색과 범례(25점 척도의 '20점' 선이 v3 에 그려지던 결함도 고침)
- [x] 5 방법 절: 방식 표·색인의 v3.0 다섯 방식 설명, "무엇을 보고 매기는가"를 v3.0 판정 재료로
- [x] 6 감사 기록 점검(항목 메모 안내문을 v3.0 에 맞춤. 규칙 JSON 의 source 파일명·open_tensions 는 다음 규칙 변경 때)
- [x] 항목 점수 정수 반올림(사용자 결정) → pilot9(판정 첫 문장 일곱 건 PRP-001~007, 순위 그대로 43·31·24·−1·−12)
- [x] 7a 검증: 테스트·옛 실행 바이트 대조·화면 폭, pilot9 출력 확인 리뷰(발견 다섯 고침: 렌더 셋 커밋·PRP-008·트리거 문장), review.md pass, 계약 통과
- [ ] 7b 사람 승인 → pilot9 빌드(계약 --require-html), history.csv 행 커밋 여부 묻기

## 뒤로 미룸
- [ ] HTML 리포트(산점도 축·80점 선·방법 카드·층별 화면), 승인 페이지 층별 수정 화면
- [ ] AGENTS.md 문구(main)
