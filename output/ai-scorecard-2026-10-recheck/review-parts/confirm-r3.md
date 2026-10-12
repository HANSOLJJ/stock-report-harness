---
reviewer_agent: general-purpose (확인 리뷰 3차)
session: cf-recheck-20261012-r3
reviewed_at: 2026-10-12
round: 3
---
# confirm-r3 — 확인 리뷰 3차(확인 리뷰 2차 C1·R1~R7 수정 처리 확인)
검토자: Claude Opus 5.5 · 확인 리뷰 독립 세션(이 실행을 만든 세션도, 1차·2차 리뷰 세션도, 수정 세션도 아님) · 2026-10-12 · 3차
결과: pass
요약: C1 은 (가) 문장 그대로 들어갔다. microsoft ⑧ 은 −3 이고 J6·J8·J12 와 새 근거 둘(EV-microsoft-047 10-K 주석 12, EV-microsoft-048 FY26 4분기 콜)이 원문 그 위치에 글자 그대로 있다. R1~R7 도 모두 반영됐다(R3 은 권고 문장 끝의 '54쪽 가변 조건 계약 문장 포함' 괄호만 빠졌고 위치는 맞다). 엔진을 메모리에서 다시 돌리면 results_hash `1a433c38…` 가 저장값과 같고, 2차 상태(HEAD~1, `90671057…`) 대비 바뀐 칸은 microsoft ⑧(−2 → −3)과 그에 따른 microsoft 함정·조정(−8·13 → −9·12), alphabet 순위(3 → 공동 2)뿐이다. 순위는 Amazon 14(1), Microsoft·Alphabet 12(공동 2), NVIDIA·TSMC 9, Apple 7, Oracle 6, Alibaba·Tesla 5, SpaceX + xAI·Palantir 4, Anthropic·OpenAI 1(공동 12), Meta 미완료다. microsoft ⑦(조달 의존 고객 몫 큼)과 ⑧(고객 집중 −3)은 규칙 ⑦ "⑦ 은 숫자의 진위를, ⑧ 은 생존의 취약성을 잰다. 서로 독립이다" 대로 다른 속성을 세며, 같은 계약을 두 칸에 쓰는 방식은 SpaceX + xAI(Anthropic 계약: ⑦ 큼 65.1%, ⑧ −3 65%)와 같다. ⑧ 고객 축의 잣대는 Amazon·SpaceX·Palantir·Oracle·NVIDIA·TSMC 와 같은 쪽으로 맞춰졌다. 초안 순위표 13행·카드 머리 13개·카드 factor 표 117칸·요약 상자 13개·요약 속 숫자·microsoft ⑧ 세 칸이 results·judgments 와 어긋남 0 이다. 체크리스트 Q01~Q23 은 모두 pass 다. 점수·순위·체크리스트를 바꾸는 발견은 남지 않았다. 다만 microsoft ⑧ −3 은 기간이 공시되지 않은 OpenAI 몫을 보수적으로 편 결과이고, 회사가 밝힌 12개월 인식 비율을 분해하면 OpenAI 몫이 평균보다 늦게 인식된다는 정황이 있어 사람이 승인할 때 알아야 할 민감도로 7절에 적었다.
검토 기준: results_hash `1a433c3842adb967a8b6bc4d816955c65d90a4936bf681bf9a5b85742b4ba1ea`, draft_hash `dd22fc0714ce46de52b01580f35b38bf78c7b6b7c6d6725155ef5cd29843aba5`. `review.md` frontmatter 와 같다. results_hash 는 `engine.recompute_matches` 로 다시 냈고, draft_hash 는 `draft.md` 바이트의 sha256 과 같다. 2차 상태는 git `HEAD~1` 의 실행 파일이다. 이 리뷰는 이 파일 하나만 썼고 `scorecard_cli.py` 는 부르지 않았다. SEC 원문은 이미 받아 둔 `data/_sec/docs/` 캐시만 읽었고, 실적 콜·블로그는 Playwright 로 열었다. `validate_report_contract.py` 는 리뷰 상태 한 줄 말고 모두 통과한다(실행 뒤 작업 트리 변경 없음).

## 1. 수정 반영 확인

### 바뀐 범위(HEAD~1 → HEAD)
- 판단: microsoft.F8(score −2 → −3, evidence 세 줄 교체, evidence_up 한 줄·evidence_down 한 줄 추가, evidence_ids 에 047·048), alphabet.F8(J7·J8 교체), amazon.F9.obsreg25(evidence_down 셋째 줄 표지). 기업 요약: microsoft·alphabet·openai. 트리거: TRG-092 observation. 근거: EV-microsoft-045·EV-alphabet-075 locator, 새 근거 EV-microsoft-047·048. 관측·run·출처는 바뀌지 않았다(출처 해시 같음, 새 근거의 출처 SRC-EDGAR-000119312526323660·SRC-WEB-microsoft-001 은 장부에 이미 있다).
- 바뀐 판단·요약의 revision_history 에 이전 값과 제안 번호(PRP-127~132)가 남았고 검토일은 2026-10-12, 상태는 `new` 다.

### 지시 대비
| 항목 | 지시(confirm-r2) | 지금 | 판정 |
| --- | --- | --- | --- |
| C1 (가) | microsoft ⑧ −3, J6·J8·J12 문장, D3 유지, 10-K 문장을 새 근거로 등록해 내릴 근거에 추가, 요약 둘 | J6·J8·J12 가 (가) 문장과 글자 그대로 같다. D3(EV-microsoft-046) 그대로, 그 바로 뒤에 "2026-06-30 상업 RPO 는 $678B … [EV-microsoft-047]" 추가. 요약 둘이 (가) 문장과 같다. 그 밖에 올릴 근거에 "2026 회계연도 4분기 상업 RPO 의 직전 분기 대비 증가는 모두 프론티어 모델 회사 밖 고객의 약정에서 왔다. [EV-microsoft-048]" 이 더해졌다 — J12 의 근거이고, OpenAI 몫을 줄이는 쪽이라 올릴 근거 칸이 맞다 | 맞음 |
| R1 | TRG-092 둘째 문장 | 권고 문장 그대로 | 맞음 |
| R2 | EV-microsoft-045 locator 아홉째 항목 | 권고 문장 그대로. 블로그를 다시 열어 "What has evolved:" 목록 11개 가운데 9번째가 그 문장임을 확인했다 | 맞음 |
| R3 | EV-alphabet-075 locator 절 이름 | "Liquidity and Material Cash Requirements 절의 Purchase Commitments and Other Contractual Obligations 문단" — 절 이름은 원문과 맞다. 권고 끝의 "(54쪽 가변 조건 계약 문장 포함)" 은 빠졌다. 그 문장은 판단 J8 이 인용하고 원문 54쪽에 있다(캐시 대조) | 맞음(괄호 생략은 점수 무관) |
| R4 | alphabet ⑧ J7 | 권고 문장 그대로 | 맞음 |
| R5 | alphabet ⑧ J8 | 권고 문장 그대로. "1년 넘는 고정·보장 약정 $707.0B" 는 10-Q 주석 10 의 "contracts with remaining terms greater than one year … fixed or guaranteed commitments … $707.0 billion" 과 맞고, "가변 조건 계약의 해지 불가 의무를 최소 수량까지만" 은 54쪽 "we do not estimate the non-cancelable obligation beyond any minimum quantities" 와 맞다 | 맞음 |
| R6 | OpenAI 요약 | 권고 문장 그대로. ($38B + $100.0B + $250B) ÷ $50B = 7.76배(약 8배), Oracle $300B 를 더하면 13.76배(약 14배) | 맞음 |
| R7 | amazon ⑨ 표지에 EV-amazon-002 | 권고 문장 그대로 | 맞음 |
| 요약 셋 | Microsoft·Alphabet 공동 2위, OpenAI 근거 등급 | `summaries_r3.py` 문장과 judgments 의 요약이 같다 | 맞음 |

### 새 근거 둘(원문 대조)
| 근거 | 원문을 연 방법 | 발췌 | 위치 | 판정 |
| --- | --- | --- | --- | --- |
| EV-microsoft-047 | SEC 캐시 `f6fe718fc495159d-msft-20260630.htm`(10-K FY2026, 출처 SRC-EDGAR-000119312526323660 과 같은 제출본) | "Revenue allocated to remaining performance obligations related to the commercial portion of revenue was $ 678 billion as of June 30, 2026, with a weighted average duration of approximately 2.3 years. We expect to recognize approximately 30 % of both our total company … over the next 12 months and the remainder thereafter." 가 글자 그대로 있다(공백 표기까지 같다) | "NOTE 12 — UNEARNED REVENUE" 의 마지막 문단이고 바로 뒤가 "NOTE 13 — LEASES" 다. locator "Part II Item 8, Note 12 Unearned Revenue 마지막 문단" 과 맞다 | 맞음 |
| EV-microsoft-048 | FY26 4분기 실적 콜 페이지(SRC-WEB-microsoft-001), Playwright(직접 받기는 403) | "Commercial remaining performance obligation grew 84% to $678 billion. All sequential commercial RPO growth was driven by commitments from customers outside of frontier model companies. And RPO increased 25% when excluding OpenAI." 가 글자 그대로 있다 | CFO 의 "Now, to our commercial results." 뒤 둘째 문단. locator "CFO 발언 중 commercial remaining performance obligation 문단" 과 맞다 | 맞음 |

### 판단 문장의 숫자
- J8: $625B × 45% = $2,812.5억. ÷ 2.5년 = $1,125억(매출 $3,318.39억의 33.9%), ÷ 2.3년 = $1,222.8억(36.8%) → "약 $1,125억~$1,223억 … 약 34~37%" 맞음. $250B ÷ $3,318.39억 = 75.3% → "약 75%" 맞음. $24.1B ÷ $331.8B = 7.3% → "약 7%" 맞음.
- J6: 약정 축 $5,578억 ÷ $3,318.39억 = 1.68배, −2 — 2차 리뷰에서 대조한 값 그대로.
- J12 "6-30 의 OpenAI 몫이 12-31 보다 크지 않다": 4분기 콜 문장은 3-31 → 6-30 의 증가만 말한다. 12-31 → 3-31 구간은 FY26 3분기 콜("Commercial remaining performance obligation grew 26% … when excluding OpenAI. RPO increased to $627 billion and was up 99% year-over-year")의 전년 대비 수치로 따지면 3-31 의 OpenAI 몫이 약 $2,300억~$2,600억으로 12-31 의 $2,813억보다 작아(추론 계산), 결론은 맞다. 근거가 4분기 콜 하나로만 적힌 것은 점수 무관(다음 실행 과제 N3).

## 2. 엔진 재계산과 바뀐 칸

- `engine.recompute_matches("ai-scorecard-2026-10-recheck")` → 저장값 `1a433c38…` 와 새로 낸 값이 같다.
- HEAD~1 results 와 14사 × 9칸·과점·함정·조정·순위·완료 여부를 칸 단위로 견주면 바뀐 것은 아래뿐이다. 입력 해시는 judgments·evidence·triggers 셋이 바뀌었고 observations·sources·run·rules 는 같다.

| 칸 | 2차 상태 | 지금 |
| --- | --- | --- |
| microsoft ⑧ | −2 | −3 |
| microsoft 함정·조정·순위 | −8 · 13 · 2 | −9 · 12 · 2(공동) |
| alphabet 순위 | 3 | 2(공동) |

- 순위: Amazon 14(1), Microsoft·Alphabet 12(공동 2), NVIDIA·TSMC 9(공동 4), Apple 7(6), Oracle 6(7), Alibaba·Tesla 5(공동 8), SpaceX + xAI·Palantir 4(공동 10), Anthropic·OpenAI 1(공동 12). Meta 는 순위 밖(함정 부분합 −7). 지시된 결과와 같다. confirm-r2 의 모의 계산(microsoft ⑧ −3 이면 Microsoft·Alphabet 12 공동 2위)과도 같다.

## 3. ⑦·⑧ 이중 계산(Q01·Q21)과 ⑧ 고객 축 잣대(Q03)

### 같은 속성을 두 번 셌나
- 규칙 2.2 의 금지선은 같은 관계가 아니라 같은 속성이다. 규칙 ⑦ 판정 지침은 "⑦ 은 숫자의 진위(이 매출이 진짜 수요인가)를, ⑧ 은 생존의 취약성(끊기면 멈추는가)을 잰다. 서로 독립이다" 라고 적고, ⑧ 공유 다섯째 줄은 "고객이 대금을 조달로 마련하는지는 ⑦ 에서" 센다고 나눈다.
- microsoft ⑦ 은 OpenAI 가 투자 유치로 대금을 내는 고객이라는 속성(대금의 원천)을, ⑧ 은 OpenAI 한 곳이 끊기면 매출의 30% 이상이 흔들린다는 속성(집중)을 센다. ⑧ 판정 칸은 OpenAI 가 조달로 대금을 내는지를 재료로 쓰지 않고, ⑦ 판정 칸은 집중의 크기를 −2 의 이유로 쓰지 않는다(⑦ 은 가로축 큼으로 −2, 세로축은 비중이 큰 쪽에서 점수를 가르지 않는다).
- 같은 계약을 두 칸에 쓰는 처리가 다른 회사와 같다. SpaceX + xAI 는 Anthropic 계약을 ⑦ 가로축(65.1%, 큼)과 ⑧ 고객 축(65%, −3)에 함께 쓰고, Oracle 은 OpenAI 계약을 ⑦ 가로축(2차 보도, 큼)에 쓰되 ⑧ 고객 축은 공시·1차 자료가 없어 재지 않았다. 판정: Q01·Q21 pass.

### ⑧ 고객 축 — 회사를 가로지른 잣대
| 회사 | 고객 축 재료(등급) | 연환산 방식 | 비율 | 고객 축 | ⑧ |
| --- | --- | --- | --- | --- | --- |
| Microsoft | 상업 RPO 의 약 45% 가 OpenAI(회사 1차), 기간 미공시 | 회사 공시 상업 RPO 가중평균 잔여 기간(2.5년·2.3년), 한 해 상한을 함께 적음 | 34~37%(상한 75%) | −3 | −3 |
| SpaceX + xAI | Anthropic 월 $1.25B·Google 월 $920M(S-1/A 공시) | 월액 × 12 | 65%·48% | −3(재배정 경로로 −4 아님) | −3 |
| Amazon | OpenAI $100.0B/8년·Anthropic $100.0B 초과/10년(10-Q) | 계약액 ÷ 공시 기간 | 2% 미만 | 0 | −1(공급 축) |
| Palantir | 미 정부 매출 약 42%(10-Q 인식 매출) | 인식 매출 | 42% | −3 | −3 |
| NVIDIA | 직접 고객 22%·14%(10-K/10-Q) | 인식 매출 | 22% | −2 | −4(공급·지정학) |
| TSMC | 최대 고객 19%(20-F) | 인식 매출 | 19% | −2 | −4(지정학) |
| Oracle | OpenAI $300B/5년(2차 보도), 고객별 RPO 미공시 | 재지 않음 | — | 미확인 | −3(약정 축) |
| Alphabet | Anthropic $200B·백로그 40%(2차 보도) | 재지 않음, 10% 이상 고객 없음(공시) | — | −1 이하 | −3(약정 축) |

- 같은 입력(⑧ 고객 축의 집중)에 공시나 회사 1차 자료만 쓰고 2차 보도는 재지 않는다는 등급 잣대가 여덟 회사에 같게 섰다(AGENTS 2026-10-09).
- 30% 이상이면 물량을 돌릴 경로가 있어도 −3 이고 경로는 −4 를 막는 데만 쓴다는 잣대가 Microsoft·SpaceX·Palantir 에 같다. ⑧ 사다리의 −3 은 "매출의 30% 이상**이나** 핵심 제품 하나가 멈추고" 로 둘 가운데 하나면 된다.
- 연환산: 계약 기간이 공시된 곳(Amazon)은 공시 기간으로, 월액이 공시된 곳(SpaceX)은 월액으로, 기간이 공시되지 않은 곳(Microsoft)은 미확인을 감점 완화 쪽으로 풀지 않는 두 방식(회사 평균 잔여 기간, 한 해 상한)으로 쟀고 둘 다 30% 를 넘는다. microsoft ⑦ J7 의 한 해 상한(84.4%)과 ⑧ J8 의 상한(75%)이 같은 공유 줄을 따른다. 2차 리뷰의 사건 교차표 1행(같은 계약이 ⑦ 은 상한, ⑧ 은 평균 인식 비율)은 해소됐다.
- 남은 어긋남 하나(점수 무관): amazon ⑧ J8 고객 축은 기간이 공시되지 않은 OpenAI 기존 약정 $38.0B 를 분자에서 뺐다(amazon ⑦ J7 은 한 해 상한으로 넣음). Microsoft 와 같은 방식으로 넣으면 ($12.5B + $38.0B) ÷ $775.7B = 6.5% 로 10% 미만이라 고객 축은 많아야 −1 이고, Amazon ⑧ 은 공급 축 −1 이 정하므로 점수가 같다(다음 실행 과제 N2).
- 판정: Q02·Q03 pass(2차 fail 사유 C1 해소).

### 이번 수정이 닿은 행의 회사 가로지르는 표

#### 사건 교차표
| # | 사건 | 등장하는 판단과 읽은 성격 | 갈린 이유 | 판정 |
| --- | --- | --- | --- | --- |
| 1 | OpenAI 의 Azure $250B 추가 구매 계약(EV-microsoft-045, 회사 1차) | microsoft ⑦ J7: 조달 의존 고객 약정, 한 해 상한 84.4% → 큼 · microsoft ⑧ J8: OpenAI 몫(상업 RPO 45%)의 고객 집중, 평균 잔여 기간 34~37%·한 해 상한 75% → −3 · openai ⑧ J7: 공급 축 약정에 전액 → 7.8~13.8배 −3 · microsoft·openai 요약 | ⑦ 대금 원천, ⑧ 집중, openai ⑧ 공급 약정 — 속성이 다르고 연환산은 같은 공유 줄 | 통과 |
| 2 | OpenAI 의 클라우드 구매 약정 전체 | oracle ⑦: 2차 $300B 로 큼 · amazon ⑦: 10-Q 약정 한 해 상한 7.8% 로 작음 · microsoft ⑦: 1차 $250B 로 큼 · amazon ⑧ 고객 축: 공시 기간으로 펴 2% 미만(기존 $38B 뺌) · microsoft ⑧ 고객 축: −3 · oracle ⑧ 고객 축: 2차라 미측정 | ⑦ 은 같은 공유 줄. ⑧ 고객 축의 amazon $38B 누락은 넣어도 같은 점수 | 통과(N2) |

#### 미확인 방향표
| 판단·줄 | 미확인 | 해소 | 방향 | 판정 |
| --- | --- | --- | --- | --- |
| microsoft ⑧ J12 | OpenAI 몫의 계약 기간·6-30 금액 | 회사 평균 잔여 기간과 한 해 상한으로 펴 30% 이상, −3 | 내림 | 통과 — 감점 완화 쪽으로 풀지 않았다. 다시 볼 조건(30% 아래라는 공시·1차 자료)이 적혀 있다. 7절 민감도 참조 |
| alphabet ⑧ | 없음 | 10-Q 가 해지할 수 없는 의무로 적은 총액 | — | 통과 |

#### 결정적 사실의 근거 등급표
| 칸(입력) | 회사 | 결정적 사실과 등급 | 판정 |
| --- | --- | --- | --- |
| ⑧ 고객 축 | microsoft | OpenAI 상업 RPO 45%(실적 콜, 회사 1차), $678B·2.3년·30%(10-K 공시), 4분기 RPO 증가가 모두 프론티어 모델 회사 밖(실적 콜, 회사 1차) | 통과 |
| ⑧ 고객 축 | amazon · spacex-xai · palantir · nvidia · tsmc | 10-Q·S-1/A·20-F 공시 | 통과 |
| ⑧ 고객 축 | oracle · alphabet | 2차 보도라 재지 않음 | 통과 |

#### 직접 경쟁사 쌍(바뀐 칸)
| 쌍 | 항목 | 점수 | 한 줄 이유 |
| --- | --- | --- | --- |
| Alphabet–Microsoft–Amazon | ⑧ | −3 · −3 · −1 | Alphabet 은 약정 2.02배(약정 축), Microsoft 는 OpenAI 몫의 연환산이 매출의 30% 이상(고객 축, 회사 1차·공시), Amazon 은 약정 0.34배·고객 2% 미만이라 공급 축 −1 |

## 4. 초안·요약 대조와 금지 표현

- 스크립트로 초안 순위표 13행(순위·①~⑤·과점·⑥~⑨·함정·조정), 카드 머리 13개(순위·조정·과점·함정), 카드 factor 표 117칸, 요약 상자 13개(judgments `company_summaries` 와 글자 그대로), 요약 문장 속 숫자(①~⑨ 점수, 과점·함정·조정, 밸류에이션·적자 깊이, 순위와 공동 여부), microsoft ⑧ 세 칸 전 줄이 초안에 그대로 실렸는지를 results·judgments 와 대조했다. 어긋남 0 이다.
- 검사가 값을 읽는지 사본으로 확인했다. 순위표 Microsoft ⑧ −3→−2, Alphabet 카드 머리 2위→3위, Microsoft 카드 ⑧ −3→−2, Microsoft 요약 '공동 2위다'→'2위다'·'⑧ −3'→'⑧ −2', microsoft ⑧ 내릴 근거 표지 변경을 각각 넣으면 모두 잡힌다. 요약 숫자 검사는 가짜 문장('⑧ −2 … 함정 −8 … 조정 13점')으로 세 곳을 다 잡는 것을 확인했다.
- 카드 머리의 순위는 공동 순위를 '2위' 로 적는다. NVIDIA·TSMC(4위)·Alibaba·Tesla(8위) 등 다른 공동 순위와 같은 렌더러 표기이고 순위표·요약은 공동을 밝힌다.
- 개요 다섯 줄(1위 Amazon 14, 과점 최고 Microsoft 21, 함정 최심 Alibaba −12, 과점 후보군 셋, 13개사·미완료 1개사)이 results 와 같다. 초안 frontmatter·방법 절의 results_hash·judgments 해시가 지금 값이다. preview.md 의 Microsoft·Alphabet 행도 12/2 로 맞다.
- 금지 표현: 고친 문장 88개(microsoft·alphabet ⑧, amazon ⑨ 의 세 칸, 요약 셋, TRG-092 의 관찰·조건·메모, EV-microsoft-045·047·048·EV-alphabet-075 의 발췌·위치·relevance·conditional_impact)에서 버전 표기, 이전 판 참조(이전 실행·지난 실행·기준선·종전·이번 실행에서·다시 매기·위 줄·정정), 제목 표기, 변경 표시(~~·superseded·이모지), 작업 번호(FIX-·IMPL-·PRP-·obsreg), 변경 서술(올렸다·내렸다·점으로), 리뷰 표지(확인 리뷰·C1·R1~R7)가 0 건이다. "직전 분기 대비" 는 분기 비교이고 "다시 잰다" 는 다시 볼 조건이다.
- 초안·트리거에 microsoft ⑧ 의 옛 값을 가리키는 문장(`21~28%`·`12개월 인식분`·`조정 13`·`Alphabet … 3위`)은 없다. judgments 안의 해당 문자열은 revision_history 의 이전 값뿐이다. research.md 의 "OpenAI ⑧ 판단은 지금 −4" 두 곳은 「이전 트리거 처리」 절의 이전 실행 트리거 원문(1924행)과 EV-openai-061 의 relevance(1761행)이고 초안에는 실리지 않는다(N4).
- `validate_report_contract.py ai-scorecard-2026-10-recheck`: plan frontmatter, 엄격 스키마, 표시 문장 자기완결, 판단 근거 세 칸, 방향 줄 원문 표지, 정기 실행 전부 new, research 입력 해시 결합, results 결정적 재계산, 초안 순위표, 리뷰 4영역·체크리스트 구조가 ok 이고, 남은 error 는 `review.md` status 가 pass 가 아니라는 한 줄이다.

## 5. 체크리스트(최종)

정기 실행이라 승계 판단 예외는 없다. 1차 규칙 일관성 리뷰의 fail(Q03: microsoft ⑦ N1, ⑧ 약정 분자, alphabet ⑧ 범위)과 2차 확인 리뷰의 fail(Q02·Q03: C1)이 모두 해소됐다.

| ID | 질문 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | OpenAI 계약은 microsoft ⑦(대금 원천)·⑧(고객 집중)에서 규칙 ⑦ 의 '서로 독립' 대로 다른 속성을 센다(SpaceX + xAI 의 Anthropic 계약과 같은 처리). 1260H·대만 집중은 ⑧ 에서만, 고객 자체 칩·정당성 공격은 ⑤ 에서만 센다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | microsoft ⑧ 고객 축이 공유 J2 의 '한 고객의 연환산 계약액 ÷ 최근 1년 매출' 로 돌아왔다(C1 해소). ⑧ 약정 축 분자는 아홉 회사가 같은 정의이고 Microsoft 열린 구매 주문·NVIDIA 지분 투자 약정은 정의보다 넓으나 구간이 같다 |
| Q03 | 회사마다 같은 잣대인가? | pass | ⑧ 고객 축은 공시·회사 1차만 재고, 30% 이상이면 재배정 경로가 있어도 −3 이며, 기간 미공시는 감점 완화 쪽으로 풀지 않는다는 잣대가 Microsoft·SpaceX·Palantir·Amazon·Oracle·Alphabet 에 같다. microsoft ⑦ 과 ⑧ 이 같은 한 해 상한 줄을 따른다. amazon ⑧ 의 $38B 누락은 넣어도 점수가 같다(N2) |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 바뀐 판단에 시가총액 크기를 재료로 쓴 문장이 없다. 1차 판정 그대로 |
| Q05 | 출처가 이해당사자인가? | pass | 새 근거는 10-K 공시와 회사 1차(실적 콜)이고 줄마다 등급을 적었다. 이해상충 표기는 판정 사유로 보지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | 1차 판정 그대로. 토큰 점유율을 매출 점유율로 읽은 문장이 없다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 1차 판정 그대로 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 공유 다섯째 줄대로 성격으로 센다. palantir ⑤ 는 다발형 요건으로 성격을 갈랐다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Broadcom 칩 조달 협의(TRG-092)는 논의 단계라 점수 밖이고, OpenAI $1.4T 의 구속력 미확인 몫도 넣지 않았다 |
| Q10 | 거리를 가속도로 착각했나? | pass | 1차 판정 그대로 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 1차 판정 그대로 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 1차 판정 그대로. 4점은 TSMC 하나이고 모방 불가능성 완전 통과다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | 1차 판정 그대로 |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 1차 판정 그대로. ③ 5점 없음 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 1차 판정 그대로 |
| Q16 | ①을 한 채널로만 쟀나? | pass | 1차 판정 그대로 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 1차 판정 그대로 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 1차 판정 그대로. Tesla↔SpaceX + xAI 를 양쪽에서 뺀다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | 1차 판정 그대로 |
| Q20 | 조달을 동맹으로 셌나? | pass | 1차 판정 그대로 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | microsoft(OpenAI)는 ⑤ 동맹·⑦ 대금 원천·⑧ 고객 집중을 나눠 세고, ⑧ 판정 칸은 조달 여부를, ⑦ 판정 칸은 집중 크기를 쓰지 않는다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | 1차 판정 그대로 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 1차 판정 그대로 |

## 6. 발견

### 점수·순위·체크리스트 판정을 바꾸는 발견
없음.

### 이번 수정이 남긴 점수 무관 결함
- EV-alphabet-075 locator 에 권고의 "(54쪽 가변 조건 계약 문장 포함)" 이 빠졌다. 절·문단 이름은 맞고 그 문장은 판단 J8 이 인용한다. 빌드를 막지 않는다.
- 계획 폴더 `context-notes.md` 의 "Microsoft ⑧ 고객 축은 … 21~28% → −2" 메모가 C1 결정 뒤 갱신되지 않았다(실행 산출물이 아니고 초안에 실리지 않는다). 결정 경위(공유 J2 대로 계약 기간으로 펴 −3)를 한 줄 덧붙이는 것이 좋다.
- EV-microsoft-047·048 등록과 R2·R3 locator 수정은 `work/` 스크립트에 남지 않고 evidence.json 의 git 변경으로만 추적된다.

## 7. 사람이 승인할 때 알아야 할 민감도 — microsoft ⑧ −3

- Microsoft 단독 2위(13)와 Microsoft·Alphabet 공동 2위(12)를 가르는 칸이다. 지금 −3 은 규칙대로다: OpenAI 몫의 계약 기간은 공시되지 않았고(미확인), AGENTS 2026-10-09·규칙 2.1 은 미확인을 감점 완화 쪽으로 풀지 못하게 하며, ⑦ 공유 셋째 줄의 한 해 상한(75%)과 회사 평균 잔여 기간(34~37%) 둘 다 30% 를 넘는다.
- 다만 회사가 밝힌 12개월 인식 비율을 분해하면 OpenAI 몫이 평균보다 늦게 인식된다는 정황이 있다. 2025-06-30(OpenAI $250B 계약 전) 회사 전체 RPO 기준 약 40% 이던 12개월 인식 비율이 2025-12-31 상업 RPO 기준 25% 로 내려갔다(10-K FY2025 주석 12, FY26 2분기 콜. FY26 4분기 콜도 6-30 의 30% 가 전년 대비 37% 늘었다고 적어 전년 값이 약 40% 임을 뒷받침한다). OpenAI 밖 몫이 40% 를 유지했다고 두면 OpenAI 몫의 12개월 인식은 ($1,562.5억 − 40% × $3,437.5억) ÷ $2,812.5억 ≈ 7% 에 그친다(추론 계산). 이 경우 OpenAI 몫의 잔여 기간은 평균 2.5년보다 길어, OpenAI 밖 몫의 기간이 약 2.2년 아래면 OpenAI 몫의 연환산은 30% 아래로 내려간다(추론 계산).
- 이 분해는 공시되지 않은 가정(OpenAI 밖 몫의 인식 비율·잔여 기간)에 기대므로 감점을 덜어 주는 근거로 쓸 수 없고, 점수를 바꾸지 않는다. 그러나 판정 칸 J8 의 "회사가 밝힌 상업 RPO 가중평균 잔여 기간으로 펴면 … 34~37%" 는 하한이 아니며, −3 을 받치는 것은 '기간 미공시 → 보수적으로 편다' 는 규칙 적용이라는 사실을 승인자가 알고 있어야 한다. confirm-r2 다음 실행 과제 N1(기간이 공시되지 않은 고객 계약의 연환산 규칙)을 이번 판단이 순위를 가른다는 사실과 함께 올린다.

## 8. 다음 실행 과제

1차 리뷰 다섯 파일과 confirm-r2 의 다음 실행 과제(confirm-r2 N1~N6)는 처리되지 않은 채 이어받는다. 아래가 이 리뷰의 새 과제다.

- N1. confirm-r2 N1 에 덧붙인다: ⑧ 고객 축에서 기간이 공시되지 않은 고객 계약의 연환산을 `rules.md` ⑧ 에 적을 때, 회사 평균 잔여 기간을 쓰는 경우 그 고객 몫이 평균보다 길거나 짧다는 정황(12개월 인식 비율의 변화)을 판정 칸에 함께 적게 한다. microsoft ⑧ J8 에는 "회사가 밝힌 12개월 인식 비율이 OpenAI 계약 뒤 약 40% 에서 25% 로 내려가 OpenAI 몫은 평균보다 늦게 인식되는 것으로 보이며, 평균 잔여 기간으로 편 값은 하한이 아니다(추론)" 를 더한다.
- N2. amazon ⑧ J8 고객 축에 기간이 공시되지 않은 OpenAI 기존 약정 $38.0B 를 microsoft ⑧ 과 같은 방식(한 해 상한)으로 넣는다: ($12.5B + $38.0B) ÷ $775.7B ≈ 6.5% 로 고객 축은 많아야 −1, ⑧ 점수는 같다.
- N3. microsoft ⑧ J12 의 "6-30 의 OpenAI 몫이 12-31 보다 크지 않다" 는 4분기 콜(3-31 → 6-30 증가)만 근거로 적었다. 12-31 → 3-31 구간을 받칠 FY26 3분기 콜 문장("grew 26% … when excluding OpenAI. RPO increased to $627 billion")을 근거로 등록하거나 문장을 4분기 구간으로 좁힌다.
- N4. 1차 출력 N4 에 덧붙인다: 근거 `relevance` 에 남은 "<회사> <항목> 판단은 N" 가운데 지금 results 와 다른 것을 고친다. EV-openai-061 "OpenAI ⑧ 판단은 지금 −4"(지금 −3), EV-oracle-004 "Oracle ⑧ 판단은 -4"(지금 −3), EV-anthropic-011 "Anthropic ① 판단은 4"(지금 1), EV-microsoft-002 "마이크로소프트 ② 판단은 3점"(지금 4) 등을 스크립트로 전수 대조한다(초안에는 실리지 않고 research.md 근거 절에 실린다).
- N5. EV-alphabet-075 locator 끝에 "(54쪽 가변 조건 계약 문장 포함)" 을 더한다.
- N6. 근거를 직접 등록·수정한 단계(EV-microsoft-045~048, locator 수정)를 `work/` 스크립트로 남겨 수정 묶음을 다시 돌릴 수 있게 한다.
