# QWEN-BASELINE-01 — AI 기업 scorecard 기준선(v1.5) 이관 충실성 독립 검증

- 검증일: 2026-09-08
- 검증자: scarpper worktree 의 Qwen (독립 세션)
- 성격: **로컬 원본 대조**. 최신 시장 조사·신규 수집기 구현은 범위 밖.
- 대상은 읽기 전용으로만 접근했다. worker 구현·원본 MD/HTML·기준선 JSON 을 수정·커밋·재생성·checkout·merge 하지 않았다.
- 검증 보조 스크립트와 원시 출력은 이 디렉터리(`scarpper/validation/qwen-baseline-01/`)에만 작성했다.
- 기존 `calc_f6` / `calc_f9` / `schema.py` 의 R01~R06 코드 수정은 Claude 담당이므로 그 코드 수정과 중복되는 작업은 하지 않았다. R01~R06 과 닿는 지점은 **데이터 쪽 보완 필요 사항**으로만 표시한다(P5).

## 0. 결론 요약

**기준선 이관 충실성(점수·합계·순위·원자료 수치)은 통과다.** 4중 원천 대조에서 점수 관련 값 불일치가 1건도 나오지 않았다.
반면 **현재 설계(설계 지침.md)와의 적합성**에서는 원자료·트리거 스키마 계약 미충족 10종이 나온다. 이들은 대부분 "이관을 잘못했다"가 아니라 "원본에 없는 추적 필드를 이관 단계에서 만들지 않았다"는 성격이다.

옛 기준선이 최신값이 아니라는 이유로 오류 처리한 항목은 없다. `legacy_unverified` 상태와 2026-09-02 기준일은 올바른 보존으로 판정했다.

| 구분 | 결과 |
|---|---|
| 확인한 검사 항목 | **약 1,094개** (아래 §1~§3) |
| 통과 | 점수·합계·순위·원자료 수치 대조 **전부 통과 (불일치 0)** |
| 문제 | **10종** (high 2 · medium 5 · low 3) |
| 미확인 | 6건 (§5) |

## 1. 대상 무결성 확인 (사전 검사)

원본 5종의 SHA-256 을 실측해 설계 지침 §2.1 기록값과 대조했다. **5/5 완전 일치** → 설계 지침 작성 이후 원본은 변경되지 않았다.

| 원본 ID | 파일 | 실측 SHA-256 | 설계 지침 기록 | 판정 |
|---|---|---|---|---|
| S-SCORE | AI기업_채점표_v1.5.md | `d28c5416786b5d93…6271aed30` | 동일 | pass |
| S-RULE | AI기업_채점규칙_v1.5.md | `57beb84ad8c291f3…2b3f7abb` | 동일 | pass |
| S-HAND | AI기업_채점표_HANDOVER.md | `3e5190c2cb4a4f8e…f63b7cc1` | 동일 | pass |
| S-PLAN | AI기업_채점자동화_구현계획.md | `b921372b7ee9a5d2…dea1ece3e` | 동일 | pass |
| S-AGENT | AGENTS.md | `0da9f593f4bf8ae2…4dbc4e5a` | 동일 | pass |
| (HTML) | AI기업_채점표_v1.5.html | `fa66076cbcd675d3…0ff9d71858` | scores.json / sources.json 기록과 동일 | pass |

- `runs/…/sources.json` 의 source_id 3건 sha256 → 실제 파일과 전부 일치.
- `scores.json` 의 `source.md_sha256` · `source.html_sha256` → 실제 원본과 일치.
- 검사 전후 대상 파일 수정시각: 기준선 4종 `2026-09-08T01:47:31Z`, companies.json `01:21:26Z`, rules `01:22:54Z`. 검증 중 변화 없음.

## 2. 통과 항목 (범위 1·4 중심)

### 2.1 F1~F9 · 합계 · 순위 — 4-way 대조 전부 일치

원천 4개를 독립 파싱해 대조했다.

- 원천 A: HTML `const D` 배열 14행 (`rank`, `cap`, `s[5]`, `t[4]`)
- 원천 B: MD §1 종합 순위표 14행 (14열)
- 원천 C: MD §2 기업별 상세 카드 14개 (`**①네트워크** · **5**` 행 + 헤더의 과점/함정/조정)
- 원천 D: `scores.json` companies 14건

**대조 값 182개(14사 × 9 factor + 14사 × 과점·함정·조정총점·순위) → 불일치 0건.**

추가 산술 검증 (182개, 전부 통과):
- `moat == ΣF1..F5` 14/14, `trap == ΣF6..F9` 14/14, `total == moat + trap` 14/14
- 순위 공식 `1 + (조정총점이 더 높은 기업 수)` 14/14. 동점·건너뜀 정상(2,2,2→5 / 6,6→8 / 8,8→10 / 10,10→12)
- factor 범위 `rules/v1.5.json` 준수 126/126. 특히 F7 하한 -3 위반 없음(최저 -3)
- `md_crosscheck: "match"` 14건 → 선언이 실제로 참임을 독립 확인

### 2.2 원자료 표에 내장된 점수와의 5·6번째 독립 대조 (전부 일치)

순위표·카드·D 배열과 **별도 원천**인 원자료 표의 점수 열과 대조했다.

| 대조 | 건수 | 결과 |
|---|---:|---|
| HTML `const VAL` ⑥열 ↔ `scores.json` F6 | 12 | 12/12 일치 |
| HTML `const EARN` ⑨게이트열 ↔ `scores.json` F9 | 14 | 14/14 일치 |
| MD §3-1a-2 신용표 '우리 함정' 열 ↔ `scores.json` trap | 13 | 13/13 일치 (범위 표기 `-2~-5`, `-7~-13`, `-14 / -9` 포함) |

### 2.3 ⑥ 구간표·⑨ 검산 재현

- `rules/v1.5.json` 의 활성 구간 20·29·42·62·90 으로 관측 `ntm_per` 12건을 재계산 → F6 12/12 일치.
  - TSMC 19.4·Alibaba 16.7 은 `basis.method = annual_weighted_proxy` 로 기록(C-13 권고대로 원본 방법 보존), 나머지 10건은 `vendor_forward_pe_verified_ntm`.
- S-HAND §1 검산값 11건 전부 재현: ⑥ Oracle 19.1→0 · Alphabet 25.3→-1 · Apple 35.5→-2 · Palantir 89.0→-4 · TSMC 19.4→0 · Anthropic -3 · OpenAI -4 / ⑨ Oracle -3 · SpaceX -4 · OpenAI -5 · Amazon -2.
- ⑨ G4 커버리지: Oracle `638B ÷ 250B = 2.552` → 원본·S-HAND 의 "2.6배" 재현.

### 2.4 원자료 값 수준 추적 (전부 일치)

- HTML `const FIN` 14행 × (현금·TTM FCF·런웨이·순현금/순부채) + `const BORR` 12행 × (TTM 순차입·TTM capex) = **74개 값 대조 → 불일치·누락 0건**.
- HTML `const VAL` 시총 ↔ `*.market_cap.v15` 관측 12건 → 일치.
- 관측 `raw` 문자열의 원본(MD+HTML+규칙) 전문 추적: **227 / 241 성공**. 실패 14건은 전부 `*.quarter_note.v15` 로, 원문 인용이 `raw` 대신 `value` 에 들어간 경우(P6).
- 컴퓨트 약정: Anthropic `$300B`, OpenAI `$338B+` 로 이관. S-HAND §2 가 지적한 **낡은 `$80B` 잔존 0건** (scores.json evidence 에 "v1.5 정정: ⑧에 $80B가 남아 있었음" 이 기록된 그 건이 실제로 정정 이관됨).

### 2.5 미수집→0 치환 · 승격 (범위 4) — 이상 없음

| 검사 | 결과 |
|---|---|
| `status == "verified"` 로 승격된 관측 | **0건** (legacy_unverified 212건 유지) |
| `value == 0` 인 관측 | **0건** → 미수집을 0 으로 치환한 사례 없음 (D-04 충족) |
| `value == null` 인 관측 25건 | 전부 사유 상태 보유 — not_disclosed 24 + parse_failed 1 |
| import-report 선언 파싱 실패 | `amazon.contracted_revenue.v15` → `value=null`, `status=parse_failed`, `raw='AWS 백로그(수백 $B급) — 숫자 미공시'` 로 원문 보존 ✓ |
| import-report 건수 선언 | 기업 14 / 관측 241 / 트리거 39 → 실측과 일치 |
| `runs/…/observations.json` ↔ `baseline/v1.5/observations.json` | 241건 ID 집합 동일, 공통 항목 필드 차이 **0건** |

status 분포: `legacy_unverified 212 · not_disclosed 24 · incompatible_basis 4 · parse_failed 1`.
`not_disclosed` 24건은 원문 표기(`미공시`·`∞`·`판정 불가`·`—`·`없음`·`미확인`·`적자`)를 그대로 raw 에 보존하고 value 를 null 로 둠 — 올바른 처리.

### 2.6 기업 ID · 단위 · 실적/전망/런레이트 구분 (범위 3) — 대체로 충족

- `company_id` 집합: companies.json = scores.json = observations(14곳) 일치. 미등록 ID·고아 ID 0건.
- `kind` 로 실적/전망/런레이트 구분됨(D-07): `actual 171 · estimate 12 · derived 14 · text 42 · run_rate 2`.
  - `ntm_per` 12건 전부 `estimate`, `arr` 2건(Anthropic·OpenAI) 전부 `run_rate` ✓
  - 전망/런레이트성 metric 이 `kind=actual` 로 잘못 표시된 사례 **0건**
- `unit` 체계 정합: `USD 110 · USD/share 12 · ratio 63 · years 14 · text 42`.
- `as_of` 3파일(scores/observations/companies) 모두 `2026-09-02` 일치.
- `basis` 에 통화·주식기준이 기록된 24건: `common/USD 10 · adr/USD 1(TSMC) · ads/USD 1(Alibaba) · annual_weighted_proxy 2 · vendor_forward_pe_verified_ntm 10`.
- `observation_id` 중복 0, `trigger_id` 중복 0.
- 트리거 39건은 HTML `const TRIG` 39행과 **1:1 완전 대응** (누락 0 · 추가 0).
- 트리거 39건 전부 `status=legacy` 이고 note 에 C-14("impact_raw 의 예상 점수는 저장값이 아니라 원문 문장, 사건 확인 후 현재 규칙으로 재계산") 명시 → 낡은 점수 전이(`⑦-3→-4` 등 18건)의 오염 위험은 표시됨.

## 3. 문제 목록

심각도는 **기준선 이관 충실성** 관점이 아니라 **현재 설계(설계 지침.md) 적합성** 관점이다. 점수 값을 잘못 이관한 사례는 없으므로 high 도 "점수가 틀렸다"는 뜻이 아니다.

### P1 · high — 원자료에 '기간(period)' 필드가 없어 TTM·분기·FY·전망이 구분되지 않음

- 위치: `observations.json` items[*] 241건 전부 (필드 목록 자체에 없음)
- 근거: 설계 지침 §7.1 원자료 필수 = "observation_id, company_id, 지표, 원값·정규화 값, 단위·통화, **기간**, 기준일·공시일·수집일, 실적/전망/런레이트, 연결/세그먼트, 회계·주식 기준, 출처 ID, 자료 상태". C-17 도 "price_as_of · 재무 기간 · info_cutoff 를 분리 기록" 권고.
- 기대값: `period_kind(ttm|quarter|fy|ytd|point)`, `period_end`, `disclosure_at`, `collected_at` 등이 관측마다 존재
- 실제값: 보유 필드는 `observation_id, company_id, metric, value, unit, as_of, kind, source_id, status, basis, raw, note` 뿐이며 `as_of` 는 **241건 전부 `2026-09-02` 단일값**
- 영향 예시: `alphabet.fcf_ttm.v15`(TTM) · `alphabet.quarter_note.v15`(Q2, 7/22 공시) · `alphabet.price.v15`(9/2 종가) · `tsmc.ntm_per.v15`(FY26·FY27 가중 전망) 가 모두 같은 `as_of` 하나로 뭉개진다. C-17 이 지적한 "기준일 9/2 인데 9/3~9/7 사건이 섞임" 문제를 데이터에서 가려낼 수 없다.
- 재현: `python -X utf8 validate_baseline2.py` → `[E] 관측의 기간 필드: 없음 / 관측 as_of 분포: {'2026-09-02': 241}`
- 참고: `quarter_note` 관측의 note 가 `"최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지"` 로 경고문을 넣어 둔 것은 좋은 완화다. 단 기계 검사 가능한 필드는 아니다.

### P2 · high — triggers.json 에 대상 기업·factor·근거 ID 필드가 없어 추적 연결이 불가

- 위치: `triggers.json` items[*] 39건
- 근거: 설계 지침 §7.1 트리거 필수 = "trigger_id, **대상 기업·factor**, 관찰 사실·**조건·기한**, **근거 ID**, 현재 상태, **재검토 대상**. 미래 점수를 직접 저장하지 않는다"
- 기대값: `company_id`, `factor`(F1~F9 또는 복수), `source_id` 또는 `observation_id`, `condition`, `due`, `review_target`
- 실제값: 보유 필드 `trigger_id, title, why, impact_raw, status, note` 6개뿐. 위 6개 필수 항목이 전부 없음
- 상세:
  - 기업명·factor 는 title/why/impact_raw 의 자연어(예 `"지분 비중 크면 ⑦-3→-4"`)로만 존재 → 기계 연결 불가
  - `impact_raw` 39건 중 **18건**이 factor 점수 숫자를 하드코딩. "미래 점수를 직접 저장하지 않는다"는 조항과 충돌하나, 39건 전부 note 에 C-14 로 "저장값이 아니라 원문 문장"임을 밝혀 두어 위험은 표시됨
  - 기한(`9/10`, `10/15`, `10월 예상`, `2027 상반기`, `2029~`)도 본문 문자열이라 임박 트리거 필터가 불가능 (S-HAND §6 "트리거 중 날짜 임박" 이 수작업으로만 유지되는 이유)
  - `source_id` 가 없어 39건 중 어느 것도 `sources.json` 과 연결되지 않는다. 관측 241건은 전부 연결되는 것과 대조적
- 재현: `validate_baseline2.py` → `[C] 트리거 추적 필드 누락 6건`; `inspect_values.py` → `[9] impact_raw 에 factor 점수 숫자가 하드코딩된 트리거: 18 / 39`

### P3 · medium — 시총 원천 충돌(9개사)을 `source_conflict` 로 표시하지 않고 이관 보고서도 "없음"으로 선언

- 위치: `scores.json` companies[*].cap_usd_t` · `observations.json` items[metric=market_cap]` · `import-report.md` `## 불일치·주의`
- 근거: 설계 지침 §7.2 `source_conflict` = "출처 충돌 → 값 선택·정정 근거 필요". §7.1 원자료 필수에 "자료 상태" 포함.
- 실제 원본 내부 충돌 (HTML `const D` 의 `cap` ↔ HTML `const VAL` · MD §3-1a 시총 열):

| company_id | HTML D `cap` ($T) | VAL / MD §3-1a | scores.json `cap_usd_t` | MD 행 |
|---|---:|---|---:|---:|
| alphabet | 4.173 | $4.12T | 4.173 | 813 |
| amazon | 2.82 | $2.75T | 2.82 | 815 |
| meta | 1.47 | $1.51T | 1.47 | 810 |
| microsoft | 3.60 | $3.69T | 3.60 | 814 |
| alibaba | 0.294 | $270B | 0.294 | 809 |
| apple | 4.43 | $4.74T | 4.43 | 816 |
| nvidia | 5.45 | $5.42T | 5.45 | 811 |
| palantir | 0.418 | $407B | 0.418 | 818 |
| oracle | 0.444 | $443.7B | 0.444 | 817 |

  (일치 3사: tsmc 2.15 · tesla 1.41 · spacex-xai 1.91)
- 기대값: 같은 company·metric·as_of 의 상충 값은 `source_conflict` 표시 또는 정본 선택 근거 기록, 그리고 이관 보고서에 공지
- 실제값: 두 값이 모두 관측으로 이관(`*.market_cap.d.v15` = D 값, `*.market_cap.v15` = VAL 값) 되었으나 **26건 전부 `status=legacy_unverified`**. `cap_usd_t` 는 D 값을 채택했고 채택 근거 미기록. `import-report.md` 는 `## 불일치·주의` 에 "- 없음" 으로 선언
- 점수 영향: **없음**. 시총은 F6 입력이 아니며(설계 지침 §5.1 "TTM PER, P/S, 영업외 이익 비중, 시가총액은 F6 의 추가 감점·가점 입력이 아니다") F6 12건은 전부 `ntm_per` 로 재현 확인됨(§2.3). 다만 Q04(시총 크기를 밸류 배수로 착각) 검사와 산점도 버블 크기(D.cap 기반)에는 영향.
- 부수 정합 문제: `scores.json` alibaba evidence 는 "증자 후 시총 **$270B**"(VAL 값)를 인용하는데 같은 회사의 `cap_usd_t` 는 **0.294**(D 값) → 기준선 안에서 두 값이 공존
- 재현: `validate_baseline2.py` → `[F]`; `inspect_values.py` → `[F] 상충 market_cap 기업: 9곳`

### P4 · medium — ⑥ 경계(±3% ⚠️) 표시가 이관되지 않음

- 위치: `observations.json` (경계 metric 부재) · `scores.json` (경계 필드 부재)
- 근거: 설계 지침 §5.1 "경계는 20·29·42·62·90 이며 `min(abs(PER - 경계) / 경계) <= 0.03` 이면 주의 표시한다. 경계값 자체도 주의 대상이다. 표시는 점수를 바꾸지 않는다." · T-02
- 기대값: 원본 HTML `VAL` 5열 / MD §3-1a '경계' 열의 값(`⚠️ 20선 −3%`, `29선 −5.2%`, `⚠️ 90선 −1.1%`)이 관측 또는 scores 필드로 보존
- 실제값: 경계 관련 metric(`bound*`, `warn*`, `edge*`, `distance*`) 0건, scores.json 경계 필드 0개
- 원본 값: TSMC `⚠️ 20선 −3%` · Palantir `⚠️ 90선 −1.1%` · Amazon `29선 −5.2%`(⚠️ 아님) · 나머지 9사 `—`
- 독립 재계산 검증: 관측 `ntm_per` 로 다시 계산하면 **원본 ⚠️ 표식과 12/12 일치** (TSMC 0.030000, Palantir 0.011111 만 ≤0.03). 즉 원본 표시는 활성 경계 기준으로도 정확하다.
- 구현 주의(재현 시 필요): TSMC 19.4 는 `abs(19.4-20)/20` 이 IEEE754 에서 `0.030000000000000006` → 단순 `<= 0.03` 비교는 ⚠️ 를 **놓친다**. 허용오차 비교 또는 원문 표식 보존이 필요하다.
- 점수 영향 없음(표시는 점수를 바꾸지 않음).
- 재현: `inspect_values3.py` → `[14]`

### P5 · medium — `incompatible_basis` 관측이 숫자값을 보유해 G4 커버리지 나눗셈이 성립

- 위치: `observations.json` items — `anthropic.contracted_revenue.v15`(65e9), `anthropic.offbalance_B.v15`(300e9), `openai.contracted_revenue.v15`(40e9), `openai.offbalance_B.v15`(338e9)
- 근거: 설계 지침 §7.2 `incompatible_basis` = "정의·기간 불일치 → **비교·합산 차단**". C-07 = "ARR 대체 금지. 동일 범위 계약 자료 미확보는 incompatible_basis 로 미완료 표시". §6.4 = "ARR/연환산 약정은 G4 커버리지가 아니다."
- 기대값: 차단 상태이므로 값을 null 로 두거나, 계산기가 `status` 를 보고 나눗셈을 거부하도록 `comparison_blocked` 류 플래그를 함께 둠
- 실제값: 두 쌍 모두 숫자라 `65/300 = 0.217`, `40/338 = 0.118` 이 즉시 계산됨. `raw` 에 "ARR $65B — 계약 수입 아님(C-07)" 로 의도는 기록되어 있으나 값 자체는 차단되어 있지 않음
- 대조(정당한 계산): Oracle 은 `legacy_unverified` 상태로 `638/250 = 2.552` → 원본 재현에 필요하므로 값을 가진 것이 맞다. Amazon·Alibaba·SpaceX 는 `not_disclosed`/`parse_failed` 로 null → 계산 불가로 정상 표시.
- R01~R06 과의 관계: **R02(`calc_f9.py` 가 `coverage_comparable=unknown` 인데 638/250 을 확정)는 Claude 담당 코드 수정**이므로 여기서는 코드를 지적하지 않는다. 이 항목은 **데이터 쪽에서도 방어층이 필요하다**는 지적이다 — 코드만 고치면 다른 계산기가 같은 데이터를 다시 나눌 수 있다.
- 재현: `inspect_values3.py` → `[15] incompatible_basis 4건`, `[16] 커버리지=0.217 / 0.118`

### P6 · medium — 원문 위치(note) 미기록 137건 + 원문 인용(raw) 비어 있음 14건

- 위치: `observations.json` items[*].note / items[*].raw
- 근거: 설계 지침 §7.1 출처 필수 = "source_id, 실제 URL 또는 **원문 위치**, 문서명·발행 주체·공시 식별자, **인용 위치**, 접근일, 원문 스냅샷 해시"
- 실제값:
  - `note` 빈 관측 **137 / 241건**. metric 분포: `price 12 · market_cap 12 · ntm_per 12 · ttm_per 11 · nonop_share 12 · ps_ratio 12 · cash 14 · fcf_ttm 12 · net_cash 14 · debt_ebitda 14 · capex_ttm 12`
    → 원문 위치가 HTML `VAL`/`FIN`/`BORR`(= MD §3-1a, §3-1a-3)임이 metric 이름으로만 유추됨
  - `note` 에 `D.`/`VAL.`/`EARN.`/`FIN.`/`BORR.`/`TRIG.` 표식이 있는 관측은 **15 / 241건**
  - `raw` 빈 관측 **14건** — 전부 `*.quarter_note.v15`. 원문 인용 문자열이 `raw` 가 아니라 `value` 에 들어있음(kind=text). 필드 용도 역전.
- 완화(실질 추적은 가능): 값 수준 대조에서 FIN/BORR 74개·VAL 12개가 전부 원문과 일치했고(§2.4), raw 추적도 227/241 성공했다. 즉 **사람이 따라갈 수는 있으나 기계가 자동 추적할 위치 표식이 없다**.
- 기대값: `note` 또는 별도 `locator` 필드에 `VAL[Alphabet][2]`, `FIN[Apple][1]`, `BORR[Amazon][2]`, `MD#3-1a` 형태의 행·열 위치
- 재현: `validate_baseline2.py` → `[C]`; `inspect_values3.py` → `[15]`

### P7 · medium — F2 벤치마크 원자료가 구조화 관측으로 이관되지 않음

- 위치: `observations.json` (벤치마크 관측 0건)
- 근거: 설계 지침 §4.3 "벤치마크에는 평가기관, 평가일, 모델·제품 버전, 지수 버전, 하네스·설정, 모집단, 순위, 측정값을 저장한다. 서로 다른 지수 버전의 절대값을 연결하지 않으며 순위도 모집단과 시점을 함께 제시한다."
- 실제값: metric 이 `index|arena|bench|aa_|elo|gdpval|tau|hle|arc` 와 매칭되는 관측 **0건**. 버전·하네스·평가기관 필드도 없음.
- 원본에는 AA Intelligence Index(Fable 5.1 max 66, v4.2 개편 후 57), Coding Agent Index(70 vs 67), Arena 카테고리 순위, GDPval-AA v2 Elo 1,754, Tau3-Bench Banking 52%, ARC-AGI-3 30.2%, HLE 43.6% 등이 있으나 전부 `scores.json` 의 evidence 자유문자로만 존재.
- S-HAND §6 도 이를 잔여 항목으로 명시: "AA Index 버전 혼재 — 카드마다 v4.1/v4.1.1/v4.2 값이 섞여 있다(Fable 5.1 66 또는 57). 자동화 시 **순위만 쓰거나 버전 필드 추가**."
- 판정: `rules/v1.5.json` 에서 F2 는 `mode=paths` + `C-03 pending(blocking)` 이라 신규 계산이 이미 차단되어 있으므로 **기준선 보존 상태로는 허용 가능**. 단 F2 를 활성화하려면 벤치마크 관측 신규 수집이 선행되어야 한다. MD §3-2(성능 벤치마크)·§3-3(토큰 지표)·§3-3a(클라우드 4사)·§3-4a(스펙트럼) 표는 관측으로 이관되지 않아 대조 대상 자체가 없다.
- 재현: `inspect_values.py` → `[5] 벤치마크성 관측: 0건`

### P8 · low — 이관 보고서의 "불일치·주의: 없음" 선언이 부정확

- 위치: `import-report.md` `## 불일치·주의` → `- 없음`
- 근거: 설계 지침 T-17 "14개사 기준선의 개별 점수와 합계를 보존하고 **불일치·누락 원본을 이관 보고서에 표시**한다."
- 실제 확인된 원본 내부 불일치·탈락 (점수에는 영향 없으나 미공지):

| # | 내용 | 기준선 처리 | 판정 |
|---|---|---|---|
| a | 시총: HTML D.cap vs HTML VAL/MD §3-1a — 9개사 상이 | D 값 채택, 미공지 | P3 참조 |
| b | ⑥ 경계 트리거: MD §5 line 1135 `📏 ⑥ 경계 ⚠️ **4개사** — MS(25선 +1.4%)·Alphabet(+1.2%)·Apple(35선 +1.4%)·Palantir(90선 -1.1%)` vs HTML TRIG `📏 ⑥ 경계 ⚠️ **2개사** — TSMC(20선 -3%)·Palantir(90선 -1.1%)` | HTML 판(TRIG-030) 채택 | **채택은 올바름**. 제 재계산으로도 활성 경계 기준 2개사만 ⚠️(P4). MD 판은 옛 경계 20·25·35·60·90 잔존 = C-10. 단 선택 사실 미공지 |
| c | MD §5 line 1140 `Menlo 2026년판 — 발행되어도 이해상충으로 참고만` 이 HTML TRIG 에 없어 **이관되지 않음** | 트리거 1건 탈락 | Menlo 는 `rules/v1.5.json` 체크리스트 **Q05**("출처가 이해당사자인가? — Menlo = Anthropic 지분 $14B 보유")에서 계속 참조되는 이해상충 항목이라 탈락 영향이 있음 |
| d | HTML vs MD 트리거 본문 문구 차이 **21건** | HTML 판 채택 | 대부분 어휘 차이이나 아래 3건은 의미 차이 |

- (d) 의 의미 차이 3건:
  - **TRIG-013(Meta 분기 FCF)** — HTML/JSON impact: `"분기 FCF 마이너스 전환 시 게이트 3 진입 → 커버리지 0배 → ⑨-1→-2"` / MD: `"**TTM** FCF 마이너스 전환 시 게이트 3 진입 → 커버리지 0배 → ⑨-1→-2(분기는 추세 수식어일 뿐 — 규칙 게이트 2)"`. 규칙 §6.2 G2 는 TTM 기준이므로 **MD 판이 규칙에 부합**하고 이관된 HTML 판이 의미상 틀리다. C-15 와도 닿는 항목.
  - **TRIG-031(Apple iOS 27 Siri)** — JSON: `"출시 시 ③2→3 후보 · 연기면 고착"` / MD: `"출시 시 ③2→3 후보 · 또 연기면 **현행 15점** 고착"`. 점수 인용이 줄어든 것은 §9("다른 기업 점수를 인용하지 말 것") 관점에서 오히려 개선.
  - **TRIG-038(SDLLMTK)** — JSON why: `"8/15 $1.02, 5월 대비 -20%"`(구체 수치) / MD why: `"모델 기업 마진 압박"`. JSON impact `"모델 기업 ⑨ 확대"` / MD `"Anthropic·OpenAI ⑨ 확대"`. 정보량은 HTML 판이 많으나 대상 기업이 좁혀진 MD 판이 더 정확.
- 기대값: D-08(과거 기록 보존)에 따라 점수를 고치지는 않더라도, 원본 내부 불일치와 채택 선택을 이관 보고서에 목록화
- 재현: `inspect_triggers.py` → `[1]~[4]`; `inspect_triggers3.py` → `[A] JSON≠HTML 3건 · [B] HTML≠MD 21건`
- 트리거 집합 대조 상세: MD §5 37행 / HTML TRIG 39행 / triggers.json 39건. triggers.json ↔ HTML TRIG 는 1:1 완전 일치. 공통 35행, MD 전용 2행(경계 4개사, Menlo), HTML 전용 4행(경계 2개사, `🔑 Apple Baltra 양산`, `🔑 분기별 성장률 시계열 확보`, `🔑 Anthropic 자체 칩 진척`).

### P9 · low — companies.json ↔ scores.json 표시명·배열 순서 불일치

- 위치: `companies.json` companies[*].display_name / 배열 순서 ↔ `scores.json` companies[*].display_name_raw / 배열 순서
- 표시명: apple 만 상이 — companies.json `"Apple"` vs scores.json `"🍎 Apple"`.
  → S-HAND §3-2 "기업명 별칭: `🍎 Apple`(**HTML만 이모지**) · CSV 는 `Apple`(이모지 없음)" 과 부합하므로 의도된 정제로 보인다. 단 scores.json 의 `display_name_raw` 가 원본 표기를 보존하는 필드라는 정의가 파일 어디에도 없어 근거가 암묵적.
- 배열 순서: companies.json 은 MD 순위표 순(`…meta, microsoft…alibaba, anthropic…`), scores.json 은 HTML D 순(`…microsoft, meta…anthropic, alibaba…`). 두 쌍이 swapped.
  → 점수·순위 계산 영향 없음(순위는 total 로 재계산 검증됨, §2.1). 원본 자체가 MD 순위표 / MD §2 카드 / HTML D 세 가지 순서를 가지므로 원본 내부 불일치이기도 하다.
- 재현: `validate_baseline2.py` → `[E]`

### P10 · low — `parse_failed` 상태명이 §7.2 상태 계약 목록에 없음

- 위치: `observations.json` items[`amazon.contracted_revenue.v15`].status = `"parse_failed"` (1건)
- 근거: 설계 지침 §7.2 상태 목록 = `verified · legacy_unverified · not_disclosed · collection_failed · source_conflict · incompatible_basis · needs_judgment · needs_rule_decision`
- §7.2 가 "상태 이름은 구조 문서에서 바꿀 수 있으나 위 의미를 합치지 않는다"고 하므로 신규 이름 자체가 위반은 아니다. 다만 `rules/v1.5.json` 이나 docs 어디에도 `parse_failed` 정의가 없어 계약 추적이 안 된다. 의미상 `collection_failed`(재수집·수동 입력 대상) 계열.
- 값 처리는 올바름: `value=null` + `raw` 원문 보존 → D-04 충족. 이 항목은 **좋은 처리**이고 상태명 등록만 누락.
- 재현: `validate_baseline2.py` → `[D] status 분포`

## 4. 문제 요약표

| ID | 심각도 | 영역 | 위치 | 한 줄 |
|---|---|---|---|---|
| P1 | high | 원자료 계약 | observations.json items[*] | 기간(period)·공시일·수집일 필드 부재, as_of 단일값 241건 |
| P2 | high | 트리거 계약 | triggers.json items[*] 39건 | 대상 기업·factor·근거 ID·조건·기한·재검토 대상 필드 부재 |
| P3 | medium | 출처 충돌 | scores.json cap_usd_t / observations market_cap | D.cap vs VAL 시총 9개사 충돌, source_conflict 미표시·미공지 |
| P4 | medium | ⑥ 경계 표시 | observations / scores | VAL '경계' 열 미이관 (TSMC ⚠️ 20선 −3% 등). 부동소수점 함정 포함 |
| P5 | medium | 결측 정책 | observations 4건 (anthropic·openai) | incompatible_basis 인데 숫자 보유 → G4 나눗셈 성립 |
| P6 | medium | 출처 위치 | observations note 137건 / raw 14건 | 원문 행·열 위치 미기록, quarter_note 는 raw/value 용도 역전 |
| P7 | medium | F2 원자료 | observations (벤치마크 0건) | AA Index·Arena·GDPval 등이 구조화 관측으로 없음. 버전 필드 부재 |
| P8 | low | 이관 보고 | import-report.md `## 불일치·주의` | "없음" 선언. 실제 불일치 4종(시총·경계 트리거·Menlo 탈락·본문 21건) |
| P9 | low | ID 정합 | companies.json ↔ scores.json | apple 표시명, 배열 순서 2쌍 상이 |
| P10 | low | 상태 계약 | observations 1건 | `parse_failed` 가 §7.2 목록·규칙 파일에 미정의 |

## 5. 미확인 (검증하지 못한 것)

1. **`AI기업_채점표_운영이력.md` · `채점이력.csv` · `check_채점표.py` 가 원본 폴더에 없다** (설계 지침 §2.2 와 동일한 관찰). MD 최상단 "채점 전 필독 순서"와 S-HAND §4·§5 가 참조하는 버전 이력·기존 검사기 통과 여부·MD/HTML/CSV 동기화는 대조할 원본이 없어 검증 불가. → 기준선이 "과거 이력을 완전히 이관했다"고 선언하려면 누락 원본 확보 또는 이력 불완전 상태 명시가 필요하다(설계 지침 §2.2).
2. **HTML 렌더링·화면 검증 미수행.** 산점도 버블 크기(D.cap 기반), FIN/BORR 표 `<th>`/`<td>` 개수, 카드 템플릿 태그 균형 등 S-HAND §5 가 언급한 항목과 설계 지침 T-19 는 이번 범위(로컬 원본 대조) 밖.
3. **원본 숫자의 시장 사실 여부 미검증.** 실적·상장 여부·모델 성능·뉴스를 외부 자료로 재확인하지 않았다. 기준선이 `legacy_unverified` 로 표시한 것은 올바르며, 이번 검증은 "원본 → 기준선 이관이 충실한가"만 다룬다.
4. **scores.json evidence 불릿의 전수 문장 대조 미수행.** 14사 × 9 factor 근거 불릿은 raw 추적(227/241)과 VAL/FIN/BORR/EARN 값 대조 수준에서 확인했고, 문장 단위 의미 모순 통독(설계 지침 §10.1, S-HAND §5 "분기마다 한 번은 통독")은 수행하지 않았다.
5. **MD §3-2·§3-3·§3-3a·§3-4a·§3-4 표는 관측으로 이관되지 않아(P7) 대조 대상 자체가 없다.** 이들 표의 값이 기준선에 빠진 것인지 원래 관측 대상이 아닌 것인지는 구조 문서 판단 사항.
6. **설계 지침 §2.1 의 원본 줄 수 표기(1,145 / 734 / 134 / 285 / 171)는 제 실측(1,146 / 722 / 127 / 280 / 158)과 다르다.** 그러나 SHA-256 이 5/5 완전 일치하므로 내용은 동일하며, 줄 수 세는 방식(개행·BOM·에디터 기준) 차이로 판단한다. 기준선 오류 아님.

## 6. 재현 방법

scarpper worktree 에서 실행한다. 모든 스크립트는 대상 파일을 **읽기 전용**으로만 연다.

```powershell
cd C:\Users\noble\orca\workspaces\stock-report-harness\scarpper\validation\qwen-baseline-01

python -X utf8 parse_html.py          # 원본 HTML 의 const D/VAL/EARN/FIN/BORR/TRIG 추출 -> html-arrays.json
python -X utf8 validate_baseline2.py  # [A] 점수 4-way [B] 산술·범위·순위 [C] 출처·해시 [D] 상태·승격 [E] 정합 [F] 시총 충돌
python -X utf8 inspect_values.py      # 관측 인벤토리, ⑥ 구간 재현, F9 검산, run vs baseline 비교
python -X utf8 inspect_values3.py     # FIN/BORR 값 추적, VAL ⑥·EARN ⑨ 대조, 신용표, ⑥ 경계, 결측 정책, G4 커버리지
python -X utf8 inspect_triggers.py    # 트리거 3-way 건수·제목 대조, 신용표 전체 매핑
python -X utf8 inspect_triggers3.py   # 트리거 본문 3-way (JSON vs HTML / HTML vs MD) -> 원본 불일치와 이관 변경 구분
```

산출물: `findings2.json`(44건) · `findings3.json`(8건) · `html-arrays.json` · `run-output.txt` · `run2~6-output.txt`.

한글이 콘솔에서 깨져 보이면 cmd 코드페이지 문제일 뿐 파일은 UTF-8 로 정상이다. `> run-output.txt 2>&1` 로 담아 `read_file` 로 보는 방식을 사용했다.

### 6.1 산출물 인벤토리와 권위 구분

| 파일 | 역할 | 권위 |
|---|---|---|
| `REPORT.md` | 이 보고서 | 최종 |
| `parse_html.py` → `html-arrays.json` | 원본 HTML 의 `const D/VAL/EARN/FIN/BORR/TRIG` 추출 | 이후 스크립트의 입력이므로 **먼저 실행** |
| `validate_baseline2.py` → `findings2.json`, `run2-output.txt` | [A] 점수 4-way · [B] 산술·범위·순위 · [C] 출처·해시 · [D] 상태·승격 · [E] 정합 · [F] 시총 충돌 | **권위 있음** |
| `inspect_values.py` → `run3-output.txt` | 관측 metric 인벤토리 · ⑥ 구간 재현 · HANDOVER 검산 · run 대 baseline 비교 | 권위 있음 |
| `inspect_values3.py` → `findings3.json`, `run4-output.txt` | FIN/BORR 값 추적 · VAL ⑥/EARN ⑨ 대조 · 신용표 · ⑥ 경계 · 결측 정책 · G4 커버리지 | 권위 있음 |
| `inspect_triggers.py` → `run5-output.txt` | 트리거 건수·제목 3-way · 신용표 전체 매핑 | 권위 있음 |
| `inspect_triggers3.py` → `run6-output.txt` | 트리거 본문 3-way(JSON 대 HTML 대 MD) → 원본 불일치와 이관 변경 구분 | 권위 있음 |
| `verify_hashes.py` → `run7-hashes.txt` | 대상 14개 파일의 읽기 전후 해시·mtime 비교 | 권위 있음 |
| `inspect_schema.py` → `schema-dump.txt` | 초기 스키마 파악용 | 참고용 |
| `validate_baseline.py` → `findings.json`, `run-output.txt` | **v1 초안. 폐기 대상** | **권위 없음** |

⚠️ `validate_baseline.py`(v1)는 MD 순위표의 열 인덱스를 잘못 읽어(14열 표에서 과점 열을 ⑥ 으로 인식) **370건의 거짓 양성**을 냈다. `findings.json` 과 `run-output.txt` 은 이 보고서의 근거가 아니며 참고·재현에 쓰지 말 것. 수정본이 `validate_baseline2.py` 이고 이 보고서의 모든 수치는 v2 이후 스크립트에서만 나왔다. v1 을 남긴 것은 시행착오 기록 목적이다.

### 6.2 읽기 전후 무결성 확인 결과

`verify_hashes.py` 로 대상 14개 파일을 검증 시작 시점과 종료 시점에 각각 측정했다. **변경 감지 0건.**

| 파일 | SHA-256(앞 16) | mtime (UTC) | 판정 |
|---|---|---|---|
| baseline/v1.5/scores.json | `daa46f7b26e4ee3c` | 2026-09-08T01:47:31Z | UNCHANGED |
| baseline/v1.5/observations.json | `8f1b932850ba51e0` | 2026-09-08T01:47:31Z | UNCHANGED |
| baseline/v1.5/triggers.json | `9784a48331021415` | 2026-09-08T01:47:31Z | UNCHANGED |
| baseline/v1.5/import-report.md | `3ac20e1050fcfe20` | 2026-09-08T01:47:31Z | UNCHANGED |
| scorecard/companies.json | `2bd6baf36ca1b361` | 2026-09-08T01:21:26Z | UNCHANGED |
| scorecard/rules/v1.5.json | `d671f22d309b2826` | 2026-09-08T01:22:54Z | UNCHANGED |
| runs/…/sources.json | `e901166be58181bf` | 2026-09-08T01:47:34Z | 사전 기록 없음(1회 측정) |
| runs/…/observations.json | `7843969ee18eb155` | 2026-09-08T01:47:34Z | 사전 기록 없음(1회 측정) |
| AI기업_채점표_v1.5.md | `d28c5416786b5d93` | 2026-09-07T02:50:05Z | UNCHANGED |
| AI기업_채점표_v1.5.html | `fa66076cbcd675d3` | 2026-09-07T02:50:05Z | 사전 기록 없음. 단 sources.json·scores.json 기록값과 일치 |
| AI기업_채점규칙_v1.5.md | `57beb84ad8c291f3` | 2026-09-07T02:50:49Z | UNCHANGED |
| AI기업_채점표_HANDOVER.md | `3e5190c2cb4a4f8e` | 2026-09-08T00:32:41Z | UNCHANGED |
| AI기업_채점자동화_구현계획.md | `b921372b7ee9a5d2` | 2026-09-07T08:07:13Z | UNCHANGED |
| AI_company_analysis_factor/AGENTS.md | `0da9f593f4bf8ae2` | 2026-09-04T03:02:53Z | UNCHANGED |

대상 변경이 없으므로 §3 의 finding 중 재확인이 필요한 항목은 없다.

작업 범위 확인:
- `git status --porcelain` (scarpper) → `?? validation/` (이 검증 산출물) 과 세션 이전부터 있던 `?? package-lock.json` 뿐. 그 외 변경 없음.
- `git status --porcelain` (worker) → `.claude/hooks/enforce-citations.sh`, `.claude/hooks/enforce-plan.sh`, `scripts/build_report.py`, `scripts/report_contract_lib.py`, `scripts/validate_report_contract.py` 에 ` M` 이 보이고 `scorecard/`, `scripts/scorecard/`, `tests/`, `docs/scorecard/` 등이 untracked 다. **이는 전부 이번 검증 이전부터 있던 Claude 의 작업 중 상태이며 이번 검증이 만든 변경이 아니다.** 특히 위 ` M` 5개 파일은 scorecard 기준선과 무관한 기존 stock 계약 파일이다. 이 검증은 worker 에서 어떤 파일도 쓰지 않았다.
- 원본 폴더 `E:\sourcecode\…\AI_company_analysis_factor` 는 읽기만 했다.


### 6.3 Orca 전달 기록

- `orca skills get orchestration` 으로 문법을 확인한 뒤 `orca orchestration send` 를 사용했다(`--to` · `--type status` · `--subject` · `--body` · `--json`, `--from` 생략).
- 수신 확인: `msg_080ee0f1828e` (2026-09-08T02:56:35Z, ok)
- 최종 검증 결과: `msg_de8bc92d5689` (2026-09-08T03:00:58Z, ok, `--report-path` 로 이 보고서를 payload.reportPath 에 첨부)
- 수신 터미널 `term_a3370266-4d39-4c5c-95a7-38ce1a1b744c` 는 `run:run_1243c2a83479` mailbox 로 해석되어 배달됐다.
- 최초 발송 시 본문이 cmd 명령줄 길이 제한(8,191자)을 넘어 `The command line is too long` 으로 실패했다. 본문을 압축하고 상세는 `--report-path` 로 대체해 재발송했다. `orca orchestration send` 에는 `--body-file` 옵션이 없다.
- 기존 세션에 대한 작업 전달이고 Task/Dispatch preamble 이 없으므로 `worker_done` 등 lifecycle 메시지는 보내지 않았다.


## 7. 판단 근거 구분 — 이관 충실성 vs 현재 설계 적합성

요청대로 두 가지를 분리해 판정했다.

- **이관 충실성 (원본 → 기준선): 통과.** 점수·합계·순위 182개 값, 원자료 125개 값(FIN/BORR/VAL/EARN/신용표), ⑥ 구간 12건, S-HAND 검산 11건, 관측 241건·트리거 39건 건수, 해시 6건 — 전부 일치. 미수집을 0 으로 치환하거나 `legacy_unverified` 를 `verified` 로 승격시킨 사례 0건. D-08(과거 기록 보존) 준수.
- **현재 설계 적합성 (기준선 ↔ 설계 지침.md): P1~P10.** 대부분 "원본에 없던 추적 필드(기간·기업·factor·근거 ID·경계·벤치마크 버전)를 이관 단계에서 새로 만들지 않았다"는 성격이며, 이관자가 원본을 잘못 읽어서 생긴 오류는 아니다. P3·P8 만 이관자의 선택(어느 원천을 정본으로 삼았는가)을 기록하지 않은 문제다.
- **옛 기준선이 최신값이 아니라는 이유로 오류 처리한 항목은 없다.** `cap_usd_t` 의 D 값 채택, `ntm_per` 의 annual_weighted_proxy 2건, 낡은 경계 문구를 담은 트리거, 2026-09-02 기준일, `legacy_unverified` 상태는 모두 보존이 맞다고 판정했고, 문제는 "값이 옛것"이 아니라 "충돌·선택·위치가 기록되지 않음"에 대해서만 제기했다.
