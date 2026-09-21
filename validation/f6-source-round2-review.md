# F6 원천 2차 라운드 재검토 — DATALINK-14 · AV-SOURCE-11 · AV-SOURCE-11B(A1~A5)

- 검토일. 2026-09-10.
- 대상. NTM `95b97a7` / worker `81107de`·`3f4f9a7` / C-13 `a201a2f`.
- 판정. **세 건 모두 pass.** 셋 다 임시 사본에서 재현했고 조사 결론이 저장 원자료와 일치한다. 다만 **DATALINK-14 의 사용자 결정 항목이 셋이 아니라 다섯이다.** 아래 D1·D2 를 추가한다.

---

# 1. DATALINK-14 (NTM `95b97a7`) — pass

## 재현

`git archive 95b97a7` 로 임시 사본을 풀어 확인했다. 인용된 약관 조항 **1.1·1.2·1.4(e)·6.1·8 전부 원문과 일치**한다. 상품 페이지 두 건에 `Contact Sales` 문자열이 0건인 것도 확인했다. 계정 생성 직전에 멈춘 판단이 맞다.

## 이게 F6 를 푼다 — 관문이 전부 닫힌다

`ZEEH` 필드 정의를 원문에서 확인했다. **그동안 막혀 있던 모든 관문에 대응하는 필드가 있다.**

| F6 관문 | 그동안 | ZACKS/EE·EEH |
|---|---|---|
| 향후 4분기 | Finnhub 3 · Yahoo 2 · AV 2 | **최대 4년치 미래 분기** |
| 회계분기 식별 | Finnhub `period` 의미 미확정 · Yahoo 상대 오프셋 | **`per_fisc_year`·`per_fisc_qtr`** (달력은 `per_cal_*` 로 **별도 제공**) |
| 통화 | 전부 부재 | **`currency_code`** |
| 회계기준 | 전부 부재 | **BNRI** 문서화 (2008년부터 SBC 를 경상 항목으로 처리한다는 단서까지) |
| asOf · 과거 시점 | Finnhub 부재 · 무료 nasdaq 12개사 전부 `null` | **`obs_date`** — 필터이자 기본키. 1979년부터 |
| 표본수 · min/max | Finnhub 부재 | 제공 + **표준편차**까지 |

여기에 더해 `ZACKS/EE` 에 이 정의가 있다.

> `eps_mean_est_fwd12m` … Earnings per share (EPS) mean estimate for the next 12 months. **This is the sum of the individual mean estimates for the next four quarters.**

**F6 의 NTM EPS 분모를 공급사가 이미 계산해 준다.** 우리가 4분기를 합산할 필요조차 없다. 지적대로 이것이 무료 API 값과 같은 계산이라는 증명은 아니고 별개 상품이라는 단서도 정확하다.

## 관문 1:1 대조표 — 타당하다

표 자체에 이견 없다. 다만 두 줄 보강을 권한다. `currency_code` 를 `ZEE` 에서 확인했는데 **`ZEEH` 에도 있는지는 별도로 확인**해야 한다. 과거 시점 재현은 EEH 로 하므로 EEH 쪽 통화 필드가 없으면 백테스트에서 다시 통화 미확인이 된다. 그리고 `per_fisc_qtr` 와 `per_cal_qtr` 가 나뉘어 있다는 사실은 **Finnhub `period` 를 끝내 못 밝힌 문제의 해답**이므로 표에 명시적으로 적어 두라.

## 약관 해석 — 1.2 는 통과, 1.4(e) 가 문제다

**1.2 Derived Data — 우리 쓰임에 부합한다.** 파생 데이터 생성은 (a) 원자료로 역산 불가, (b) Licensor 서비스의 대체물이 아닐 것을 조건으로 허용된다. NTM EPS 합산과 F6 점수는 둘 다 충족한다. 걸리는 것은 이 문장뿐이다.

> provided such Derived Data **cannot be distributed outside of Client** except as otherwise detailed in the Order Form or without Licensor's prior written approval

**personal/internal only 전제에서는 이 조건이 문제되지 않는다.** 외부 배포를 안 하므로 그대로 부합한다. 오히려 사용 범위를 확정해 둔 것이 여기서 정확히 값을 한다.

**1.4(e) 는 이 프로젝트에 직접 걸린다.** 지적이 맞고, 생각보다 무겁다.

> (e) use the Data in any time sharing service bureau, software-as-a-service, **cloud or other technology service**

로컬 파이썬 계산은 걸리지 않는다. 문제는 **이 저장소의 작업 방식 자체**다. 지금 이 조율과 조사는 Claude·Gemini·Codex 라는 **외부 클라우드 LLM 서비스**를 거쳐 수행된다. 라이선스 Data 를 에이전트 프롬프트에 넣는 순간 그 자료는 Client 통제를 벗어나 제3자 클라우드로 나간다. 이걸 1.4(e) 가 말하는 cloud or other technology service 로 읽을 여지가 충분하다.

여기에 8절이 겹친다.

> Client shall allow Licensor or its designee access to any of the **premises, computers (including, but not limited to, hardware, software and network services) and personnel** of Client at reasonable times

연 1회, 30일 사전 통지, 계약 종료 후 1년까지 존속한다. **감사 대상에 network services 가 명시돼 있다.** 개인 자격이면 premises 는 자택이다.

조사로 풀 사안이 아니라 사용자 결정 사안이므로 아래 D1 로 올린다.

## 추가 사용자 결정 항목 — 셋이 아니라 다섯이다

**D1. LLM 에이전트 경유가 1.4(e) 에 걸리는지.** 위 분석대로다. 실무 선택지는 셋이다. (a) 라이선스 Data 를 에이전트에 넣지 않고 로컬 계산만으로 격리, (b) Order Form 에 해당 사용을 명시해 허가받기, (c) 이 경로 포기. **(a) 는 지금 작업 방식의 전면 변경을 뜻한다.** 조사·검증을 에이전트가 하고 있기 때문이다.

**D2. 두 경로가 서로 반대되는 신분을 요구한다.** 이게 가장 중요하다.

| | 요구 신분 |
|---|---|
| **Alpha Vantage 무료** | ToS 2.a.ii — **법인이거나 법인을 대리하면 commercial use**. 개인 자격이어야 함 |
| **Nasdaq Data Link** | 1.1 — **Client or Client business** 가 Order Form 에 서명, **internal business purposes only** |

Data Link 약관에는 개인 티어 언어 자체가 없다. **하나를 만족하면 다른 하나가 깨진다.** 우리가 써 온 `personal / internal only` 라는 표현이 두 뜻을 한 단어에 담고 있었고, 이 두 경로가 그 애매함을 정확히 반대 방향으로 가른다. 사용자가 **개인 자격인지 법인 내부 사용인지**를 먼저 정해야 두 경로 중 어느 쪽이 살아 있는지가 정해진다.

## 정책 일관성 문제 하나

`data.nasdaq.com` 의 `robots.txt` 를 원문에서 확인했다.

```
disallow: /api/*.json*
disallow: /api/v3/databases/*/data
```

**우리 `v1.6` 은 `api.nasdaq.com` 을 robots.txt Disallow 를 근거로 denied 했다.** 같은 규칙을 기계적으로 적용하면 `data.nasdaq.com` 의 **API 데이터 경로도 disallow 대상**이 된다. 정식 라이선스를 사도 정책이 자기 발목을 잡는다.

실질적으로는 구분된다. `robots.txt` 는 인증 없는 크롤러를 대상으로 하고, Order Form 과 API 키로 접근하는 라이선스 클라이언트는 계약이 규율한다. **다만 그 구분이 지금 정책 파일에 한 줄도 없다.** 승격 시 명문화해야 한다. worker 의 `POLICY-12` 후속으로 넘긴다.

## 사소한 것

`raw/dl-terms-clean.txt` 와 `dl-terms-rendered.txt` 가 바이트 단위로 완전히 같다. 같은 파일 2부다. 한쪽을 지우거나 파일명이 뜻하는 차이를 만들라.

---

# 2. AV-SOURCE-11 / POLICY-12 (worker `81107de`·`3f4f9a7`) — pass

## 재현

- `analyze_demo.py` 재실행 결과가 커밋된 `analysis-output.txt` 와 **파일 크기·sha256 줄을 빼고 전부 일치**한다. 그 줄이 갈리는 이유는 아래 해시 항목에서 다룬다.
- 약관 키워드 부재 주장을 **직접 세어 확인**했다. `scrap`·`crawl`·`robot`·`spider`·`derivative`·`derived`·`redistribut`·`resell`·`cache`·`store`·`retention` 전부 **0건**, `automat` **1건**이다. 정확하다.
- `python -m unittest discover -s tests -q` **104건 통과**.
- `194fd4b..3f4f9a7` 에서 `scorecard/results.json`·`approval.json`·`rules/v1.5.json`·`output/` diff **공집합**. 불변 주장 확인.

## 분석 품질 — C-13 보다 세 지점에서 낫다

독립 병렬이 제대로 작동했다. 같은 결론에 도달하면서 다음이 더 정확하다.

1. **NVDA 로 2차 프로브를 해서** demo 키가 문서 예시 심볼 외에는 안내문만 준다는 것을 실증했다. C-13 은 같은 말을 실증 없이 했다.
2. **연간은 2개 나오는데 분기는 그렇지 않다, 분기 지평이 짧은 것이지 자료가 없는 것이 아니다** — 원인과 현상을 가른 서술이다.
3. **`date` 가 상대 오프셋이 아니라 절대 날짜**라는 점을 짚고 Finnhub·Yahoo 보다 낫다고 적었다. C-13 은 이걸 `unknown / 부재` 로만 처리했다. IBM 이 달력연도 결산사라 회계·달력 두 가설이 갈리지 않는다는 것까지 정확히 적었다.
4. 과거 시점 재현을 **부분적**으로 판정했다. 설계진행이 C-13 에 A5 로 지적한 내용에 독립적으로 도달했다.

## 질문 다섯에 답한다

**(1) 예시 URL 2회 호출을 수집 전 범위로 본 판단 — 동의한다.** 근거 넷이 함께 성립한다. 약관·`robots.txt` 확인이 선행됐고, `robots.txt` 가 부재(404)이며, 호출 대상이 **공급사가 문서에 게시한 예시 URL** 이고, 유니버스 종목 수집이 아니다.

**선은 여기에 긋는다 — 유니버스 종목을 대상으로 한 반복 호출의 개시.** 문서 예시로 응답 스키마를 확인하는 것은 약관 검토의 일부이고, 우리 12개사를 돌기 시작하는 순간이 수집이다. 이 기준을 `POLICY-12` 보고서에 한 줄로 명문화하라. 다음에 같은 질문이 반드시 또 나온다.

**(2) ii·iv 를 사용자 사실관계로 두고 unknown 유지 — 맞다.** 에이전트가 판정할 사항이 아니다. **무료 키 발급 양식이 `Organization` 을 필수로 받는다는 관측이 중요하다.** 공급사 자신이 가입자를 조직 단위로 식별한다는 뜻이라 2.a.ii 쪽으로 기우는 신호다. 판정으로 쓰지 말고 관측으로 그대로 남기라. C-13 도 독립적으로 같은 결론에 도달했다.

**(3) 조항 없음을 unknown 으로 둔 것 — 맞다.** 침묵을 허가로도 금지로도 읽지 않는 것이 이 프로젝트 기준이다. 다만 **약관 전문이 9,945자로 짧다는 사실을 함께 적으라.** 조항이 없는 것과 문서가 얇은 것은 다르고, 별도 EULA·프리미엄 약관이 따로 있을 수 있다. 이 문서에는 없다와 허용 조건이 없다를 구분하라.

**(4) `sources.unlisted` 신설 — 찬성한다.** 미등재 사유를 `technical`/`terms`/`both` 로 가르게 한 것이 특히 좋다. Yahoo 를 약관 때문에 뺀 것처럼 읽히던 문제를 구조로 막는다. 조건 둘을 단다. 첫째, **`source_violation()` 이 읽지 않는다는 사실을 주석이 아니라 테스트로 고정**하라. 둘째, `unlisted` 는 지금 **검토했고 안 넣기로 함**만 담는다. **아직 검토 안 함**은 담지 않는다는 점을 `note` 에 적으라. 안 그러면 목록에 없는 host 의 의미가 두 가지로 갈린다.

**(5) Alpha Vantage 를 정책에 넣지 않은 판단 — 동의한다.** 미채택 권고 상태에서 등재하면 사용자 결정을 앞질러 못박는 셈이다. 다만 **`policy-12` 보고서에 왜 Yahoo 는 `unlisted` 인데 AV 는 없는가를 한 줄 남기라.** Yahoo 는 판정이 끝났고 AV 는 사용자 결정이 열려 있다는 차이다. 적어 두지 않으면 다음 세션에서 반드시 되묻는다.

## 해시 정정을 받아들인다

**설계진행이 틀렸다.** `results.json 4eb8c7d7` 을 승인 해시로 반복 인용해 왔는데, 그건 **작업 트리(CRLF) 파일 바이트 sha256** 이다. 승인 대조가 실제로 쓰는 값은 `approval.json` 의 `results_hash` 필드 `0942c342` 이고, 같은 내용이 커밋 blob(LF) 에서는 `6182cdb1` 이 된다. 앞으로 승인 불변을 말할 때는 `results_hash` 를 인용하겠다.

**이 지적은 그쪽 산출물에도 그대로 적용된다.** `analyze_demo.py` 를 커밋 트리에서 돌리면 `_raw` 파일들의 크기와 sha256 이 달라진다. 실제로 재현할 때 `documentation.html` 이 1,059,116 → 1,079,968 바이트로 갈렸다. 같은 내용인데 개행 처리 때문이다. 자기 출력에 기록하는 해시도 **개행을 정규화하거나 git blob 해시를 쓰라.** 지금 형태로는 재현자가 원자료가 바뀌었나로 오해한다.

---

# 3. AV-SOURCE-11B A1~A5 (C-13 `a201a2f`) — pass

다섯 건 모두 반영됐다. 추가 요구 없다.

- **A1.** SPCX 를 SpaceX 보통주로 정정하고 ETF·구조적 결측 단정을 삭제했다. 타 11개사와 같이 `unknown` 이다.
- **A2.** 2.a.ii 를 판정 항목으로 세우고 커밋 도메인 정황과 `premium@alphavantage.co` 문의 필요를 적었다. 개인의 personal 은 2.a 에 부합하나 법인의 조직적 internal 은 2.a.ii 에 저촉될 위험이라는 서술이 정확하다. **위 D2 와 같은 지점에 독립적으로 도달했다.**
- **A3.** `robots.txt` 404 기록과 요금표 원문을 보존했다. 기록 파일의 타임스탬프가 `2026-09-10T11:51` 로 최초 조사 시각이라 **재수집이 아님을 확인**했다. 조건 위반 없다. 다만 이 파일은 실제 응답 본문이 아니라 사후 전사다. worker 가 같은 404 의 **응답 본문 자체**를 보존했으므로 사실은 양쪽으로 확인됐다.
- **A4.** 표 2번 행을 `IBM 1종목 기준 2개 (12개사 일반화 미확인, 키 발급 후 확인 1순위)` 로 좁혔다.
- **A5.** 11번 항목을 신설해 90일 컨센서스 이동을 고유 강점으로 세우고, 검증기에 `has_consensus_drift_90d` 단언을 추가했다.

---

# 종합

**F6 의 기술적 답은 나왔다. `ZACKS/EE`·`EEH` 가 모든 관문을 닫는다.** 남은 것은 전부 권리와 신분 문제다.

| 결정 | 내용 |
|---|---|
| **D1** | LLM 에이전트 경유가 1.4(e) 에 걸리는지. 걸린다면 작업 방식 전면 변경 또는 Order Form 명시 |
| **D2** | **개인 자격인가 법인 내부 사용인가.** 두 경로가 반대 신분을 요구하므로 이걸 먼저 정해야 함 |
| D3 | 무료 계정 생성을 허용할지 (Data Link 셀프서비스 확인의 다음 단계) |
| D4 | Order Form · 1년 자동갱신 · 연 1회 감사권을 감수할지 |
| D5 | 2026-11-01 약관 개정 예정 — 계속 사용이 개정 수락으로 간주됨 |

D2 가 먼저다. **개인이면** Alpha Vantage 무료가 살고 Data Link 는 신분이 안 맞는다. **법인이면** Data Link 가 정상 경로이고 Alpha Vantage 무료는 commercial 로 분류돼 유료 문의가 필요하다.

세 조사 모두 결제·가입·메일 발송을 하지 않았고 `api.nasdaq.com` 을 호출하지 않았다. 점수·규칙·승인·원자료 불변을 확인했다. 이 재검토로 어떤 원천도 F6 에 승인하지 않으며 F6-H 산식·밴드·새 점수도 승인하지 않는다.
