# 비상장 2사 자료 출처 — 수집 불필요. v1.5 원본을 쓴다

- 결정일. 2026-09-11.
- 선행. `priv-arr-17-review.md`(`bcafb42`)

## 결정

**anthropic.com·openai.com 수집을 하지 않는다.** `v1.5` 원본 문서에서 가져온다.

```
E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\
  AI기업_채점규칙_v1.5.md    sha256 57beb84a… = v1.5.json 선언값과 일치
  AI기업_채점표_v1.5.md
```

## 경위 — 사용자가 수집 허용(C)을 골랐고, 배정하려다 원본에서 찾았다

```
Anthropic   ARR $9B → $47B → $65B(7월)     월 증가율 +58% → +57% → +14%
OpenAI      "ARR이 2~4월 $25B 에서 정체하다 7월 $40B 로 MoM +20% 복귀"   (14위 OpenAI 절)
```

**`arr_prior` 를 만들 재료가 두 기업 다 있다.** 네트워크도 약관 판단도 정책 등재도 필요 없다.

## 설계진행이 약관을 양쪽으로 다 잘못 말했다

| | 내가 말한 것 | 원문 확인 결과 |
|---|---|---|
| **anthropic.com** | "약관이 프로그램 수집을 금지한다" | **금지 조항 없음.** 보존된 `Commercial Terms of Service`(2025-06-17) 전문에 `scrape`·`crawl`·`programmatic`·`extract` **0건**. `robots.txt` `Allow: /` |
| **openai.com** | "조항은 있으나 `Services` 범위에 다툼의 여지" | **다툼 없음.** ToU 정의가 `ChatGPT, DALL·E, and OpenAI's other services for individuals, along with any associated software applications **and websites** (all together, "Services")` 라 **웹사이트가 정의 안에 있다.** `Automatically or programmatically extract data` 가 그대로 걸린다 |

**한쪽은 없는 금지를 만들었고 다른 쪽은 있는 금지를 흐렸다.** 둘 다 **정의를 안 열어 본 탓**이다. `guardrails` ENTRY-003 이 오늘 기록한 그 패턴이 **값·주석 번호에 이어 약관 정의에서 세 번째로 재발했다.**

## 오늘 세 번째 — "밖에서 찾기 전에 저장소 안을 본다"

| 라운드 | "없다/못 구한다" | 실제 위치 |
|---|---|---|
| `OFFB-24` | SPCX `offbalance_B` `not_disclosed`/"미확인" | **전날 커밋된 `companyfacts` 에 XBRL 태깅** |
| `G1-FILL-27` | SPCX 연간 재무 "회사가 공시하지 않았다" | **C-13 자신이 커밋한 S-1/A** |
| **오늘** | **비상장 ARR 이력 "약관이 막는다"** | **프로젝트 안 v1.5 원본** |

`missing-label-finding.md` 에 적은 문장이 그대로 돌아온다 — **결측 라벨을 사실로 읽지 않는다. 이미 보유한 원자료를 먼저 본다.**

**그리고 이번에는 워커가 아니라 설계진행이 그 실수를 했다.** 게다가 `PRIV-ARR-17` 검토에서 **"v1.5 원본 확보가 가장 쌉니다. 네트워크도 약관 판단도 필요 없습니다"** 라는 worker 제안을 내가 "이번 라운드에서 가장 값진 제안" 이라고 칭찬해 놓고, **같은 자리에서 다시 밖을 봤다.**

## 남은 제약 — 기간 기준이 서로 다르다

```
anthropic   $47B → $65B      시점 라벨이 "7월" 뿐
openai      $25B → $40B      "2~4월 정체" → "7월"
```

**두 회사의 "직전" 이 같은 간격이 아니다.** `PRIV-ARR-17` 에서 사용자가 기간 기준 차이를 감수하기로 했고 **`P4` 보정("기간 단위가 TTM 아님")이 잡도록** 해 뒀다. 다만 **관측에 기간 라벨을 정확히 남긴다.**

## 후속

| 건 | 처리 |
|---|---|
| **`PRIV-ARR-30`** | C-13·NTM 병렬 독립. v1.5 원본에서 추출 |
| **C-12** | 자료 확보 후 결정 — 밴드를 만들 것인가, 정성 예외로 갈 것인가 |
| `openai.com` 정책 | **배제 유지.** 약관 정의가 웹사이트를 포함한다 |
| `anthropic.com` 정책 | 금지 조항 없음이 확인됐으나 **이번에 쓸 일이 없어 등재하지 않는다** |
