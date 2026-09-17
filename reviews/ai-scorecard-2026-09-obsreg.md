---
slug: ai-scorecard-2026-09-obsreg
report_type: ai_scorecard
status: pass
created_at: 2026-09-11
plan_source: plan/ai-scorecard-2026-09-obsreg.md
research_source: research/ai-scorecard-2026-09-obsreg.md
draft_source: drafts/ai-scorecard-2026-09-obsreg.md
results_hash: a5b80e711160594507d765f4084f62b3a0a2aec13e956ffdc7a876691f284d46
draft_hash: 1bf1408291a0d34bf3580d556279bc0e4fe6caef8dda7720584bdfa6e6f30c5e
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: pass (8차 · Gemini 독립 세션)"
  - "financial-calc: 8차 needs_fix — FIX-59 로 반영 완료. 남은 지적은 미결·긴장으로 이관 (재계산에서 점수·소계·밴드·게이트 경로 불일치 0)"
  - "rule-consistency: pass (8차 · Gemini 독립 세션)"
  - "output-readability: pass (8차 · Gemini 독립 세션, low 둘 반영)"
---
# 리뷰 — AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장·이해상충 | 8차 Gemini 독립 세션 | pass | 발견 사항 없음. 분담(부재 주장 전수, Claude 독립 세션)은 needs_fix 였고 FIX-58 2단계·FIX-59 로 전부 반영했다 — 상대방 제출본까지 범위를 넓혀 다시 훑었고 등록할 사실은 없었다. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | 8차 독립 세션 | **needs_fix — FIX-59 로 반영** | **pass 가 아니다.** 8차 재계산에서 점수·소계·밴드·경계·게이트 경로가 한 칸도 어긋나지 않았고 지적은 전부 기록 수준이었다. 셋을 이번에 반영했고(순현금 측정 문면 · 잔여분 민감도 · C-26 기준일) 남은 것은 미결 C-26·C-27·C-28 과 긴장으로 옮겼다. |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | 8차 Gemini 독립 세션 | pass | 발견 사항 없음. 7차에서 든 `선언에 소비자 없음` 세 건(C-11·C-13·C-24)은 FIX-57·FIX-58 에서 정리했다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | 8차 Gemini 독립 세션 | pass | low 둘. 자동 산출 factor 의 기준선 참고 블록이 옛 점수로 시작하던 것을 FIX-59 에서 현재 점수가 첫 줄에 오게 고쳤다. HTML 이해상충 문구의 동적 연산은 정상 동작 확인(조치 없음). |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

**아래 23행은 8차 라운드 네 영역의 part 파일 기록을 그대로 옮긴 것이다**(`review-obsreg` 커밋 `e5a47d3`,
`reviews/_parts/ai-scorecard-2026-09-obsreg/`). 이 파일에서 체크리스트를 다시 돌리지는 않았다 — 각 행의 근거 칸 끝에
어느 영역의 기록인지 적었다. 담당은 겹치지 않는다: 규칙 일관성 15문항 · 재무 계산 4문항 · 사실·출처 4문항.

**fail 이 12건이고 그중 11건이 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). 남은 하나 **Q11 은 예외가 아니다** —
openai.F9 가 단위경제 측정 없이 하한 -4 를 받는 자리이고, 사용자가 2026-09-17 에 현행 유지 + 긴장 등록을 골라
`TEN-RA5-02`(2026-11 · 상향 가능 · 비 Claude 세션)로 등재했다. **예외로 바꿔 적지 않는다.**

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | fail | **승계 예외.** nvidia: F5 H=-2(고객이 경쟁자)와 F8=-3(고객 40% 자체 칩 개발) 중복 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC-05`). tesla: F5 H=-1과 F8=-2에 NHTSA 조사 중복 (`TEN-RC3-04`). v1.5 승계 논리이며 2026-11 재검토 등록되어 pass 유지. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | **승계 예외.** anthropic: F1 주채널 업무 지정 후 개인 사용자 수 열세로 차단 (`TEN-RC-02`). palantir vs oracle: 업무 전환비용 상반 취급 (`TEN-RC3-03`). alibaba: 경쟁사 오픈웨이트 배포 상황에서 F3 모방불가 partial (`TEN-RC3-05`). openai: F1 소비자 주채널 분류 후 거래 채널로 차단 (`TEN-RC4-02`). anthropic·openai: F7 매트릭스 입력 미복원 (`TEN-RC3-01`). 모두 v1.5 승계 예외. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q03 | 회사마다 같은 잣대인가? | fail | **승계 예외.** 이번 실행이 바꾼 잣대(F5 A-STRICT-54 TSMC 재판정, F6 순현금 securities_scope 전사 통일, C-24 신규 상장 트랙 P2)는 14개사 전사에 동일하게 적용됨 (`scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:tsmc.F5.strict54`, `scripts/scorecard/calc_f6_params.py:345`). v1.5 승계 판단의 전사 불일치는 `TEN-RC-03`(별표 H 이탈 조건), `TEN-RC3-01`(F7 매트릭스), `TEN-RC3-03`(F1 전환비용), `TEN-RC4-03`(F5 H=-1 수 비교)으로 등록된 승계 예외. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | F6 는 시총을 크기로 읽지 않고 비율의 분자로만 씁니다 — P1 `market_cap / net_income_ttm`, P2 `(market_cap − net_cash) / revenue_ttm`(`scorecard/rules/v1.7.json` `policies.f6.parameters.P1.formula`·`P2.formula`). 결과가 크기와 반대로도 움직입니다 — 시총 1위 nvidia($5.42T)가 F6 −2 인데 시총 최하위 alibaba($270B)와 palantir($407B)는 −4 입니다(`results.json` 각사 `factors.F6.score`). 옛 단일지표 `ntm_per`·`ttm_per` 관측은 점수 경로에 없습니다(어느 factor 의 `observation_ids` 에도 미등장). — 8차 재무 계산 영역 기록을 그대로 옮겼다(`review-obsreg` part `financial-calc.md`). |
| Q05 | 출처가 이해당사자인가? | fail | `nvidia.F2`(TEN-RA-02) 벤더 발표 1차 인용, `openai.F4`(TEN-RA3-01) 자체 발표 인용. 다만 v1.5 승계 논리이고 규칙 파일 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`(재검토 2026-11)로 등록되어 승계 판단 예외 적용. 이번 실행이 바꾼 신규 판단(`anthropic.F5.impl48`, `openai.F5.impl48`, `anthropic.F8.f8anth33`)은 SEC 8-K·10-Q 및 별표 규정을 직접 확인하여 정합함. — 8차 사실·출처 영역 기록을 그대로 옮겼다(`review-obsreg` part `fact-sources.md`). |
| Q06 | 볼륨인가 가치인가? | pass | 점수를 내는 입력이 전부 가치 단위입니다 — P3 는 매출 성장률, G4 는 계약 수입 ÷ B종 약정(둘 다 USD), 비상장 P2 는 `ps_ratio`(밸류 ÷ TTM 보정 매출)입니다. 런레이트 배수 `post_money_over_arr` 는 `calc.multiples` 에 계산만 되고 점수에 쓰이지 않습니다 — anthropic 14.846·openai 21.3 이 있는데 P2 는 30.0·39.0 을 씁니다(`results.json` anthropic/openai `factors.F6.calc`). 규칙도 그 이유를 `policies.f6.private_multiples` 에 적습니다. 사용자 수·토큰 같은 볼륨 지표는 F6·F9 입력에 한 건도 없습니다(점수 경로 관측 143건 전수). — 8차 재무 계산 영역 기록을 그대로 옮겼다(`review-obsreg` part `financial-calc.md`). |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 14개사 전수 조사 결과 "안 만든 것" 자체를 카운터 포지셔닝으로 인정한 회사 없음. Amazon은 Bedrock 매대 전략의 모방불가 fail (`judgments.json:amazon.F3`), Apple은 디바이스 ① 중복으로 모방불가 fail (`judgments.json:apple.F3`)로 엄격 판정. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | **승계 예외.** spacex-xai: F5 H=-1 근거가 적대의 종류가 아닌 "동맹이 적보다 확실히 많지 않음"이라는 수 비교 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC4-03`). Apple(비용형 -1), NVIDIA(구조형 -2), Palantir(구조형 -2), OpenAI(다발형 -3) 등 타사는 성격으로 분류됨. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | `nvidia.F2`(TEN-RA-02) Rubin 미래 양산·출하 반영, `openai.F4`(TEN-RA3-01) 2027~2028년 배치 계획 혼재. 다만 v1.5 승계 논리이고 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`로 등록되어 승계 판단 예외 적용. 반면 F3 전원 door_closed=fail 및 F4 타사 출하 기준은 준수됨. — 8차 사실·출처 영역 기록을 그대로 옮겼다(`review-obsreg` part `fact-sources.md`). |
| Q10 | 거리를 가속도로 착각했나? | fail | **승계 예외 · TEN-RB-Q10 · TEN-RC4-04.** 제 영역인 F6·F9 에서는 새 사례를 찾지 못했습니다 — P3 는 성장률, G2 `fcf_trend` 는 방향, G3 런웨이는 잔고 ÷ 소진속도로 전부 축이 맞습니다. 다만 같은 체크리스트 항목의 기존 fail 이 살아 있습니다. `TEN-RB-Q10`(microsoft·spacex-xai·tesla·amazon·palantir·oracle F3 가속도가 성장률 하나로 pass)과 `TEN-RC4-04`(tsmc F3 가속도 근거가 가이던스)이고 둘 다 `status: open`·`recheck_at: 2026-11` 입니다(`scorecard/rules/v1.7.json` `open_tensions`). 이번 실행에서 14개사 F3 는 전부 `carried_score` 라(`results.json` 각사 `factors.F3.status`) 잣대가 바뀌지 않았고, 승계 판단 예외에 해당해 pass 를 막는 사유로 세지 않습니다. — 8차 재무 계산 영역 기록을 그대로 옮겼다(`review-obsreg` part `financial-calc.md`). |
| Q11 | 순적자를 실격 사유로 썼나? | fail | **예외 아님 — 아래 발견 1.** 대부분의 자리는 순적자를 실격으로 쓰지 않습니다 — spacex-xai 는 순이익이 음수라 P1 을 못 만들지만 `parameters_not_in_track.P1` 로 사유를 적고 트랙 하한도 −7 이 아니라 −3 이며, F9 G1 은 순손실이 아니라 영업이익률(−16.195%)로 밴드를 고릅니다. 반면 **openai 는 F9 하한 −4 를 단위경제 측정 없이 받습니다** — `results.json` openai `factors.F9.calc.path[0]` 이 `operating_margin_ttm: null` 인 채 `band: "BEP 후퇴 → -4"` 이고, 같은 회사의 `openai.operating_margin_ttm.priv31` 은 `missing_type: not_disclosed_confirmed` 에 basis 가 `openai 2026 GAAP 손실 약 $60B 전망 · BEP 2030 — 전망이지 실적이 아니다` 라고 적습니다. 실적이 아닌 손실 전망으로 가장 깊은 칸을 주고, 규칙이 그것을 막으려고 둔 C-20 경로는 우회됩니다. — 8차 재무 계산 영역 기록을 그대로 옮겼다(`review-obsreg` part `financial-calc.md`). |
| Q12 | ③ 세 기준을 동등하게 쟀나? | fail | **승계 예외.** F3 사다리는 모방불가 pass 없이 4점 이상 진입 불가 (`scorecard/rules/v1.7.json:factors.F3.ladder[3].requires_imitation_pass`). 전원 3점 이하 절단 확인. 단 meta·anthropic·spacex-xai의 imitation partial 근거 불충분 긴장이 `TEN-RC4-01`로 등록됨. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | fail | **승계 예외.** 오픈웨이트 무료 배포를 곧바로 카운터 포지셔닝으로 인정하지 않고 회수 장치 부재를 엄격 지적 (`judgments.json:alibaba.F3`). 단 오픈웨이트 배포 기업들의 imitation partial 부여 논리가 승계 예외 `TEN-RC4-01`, `TEN-RC3-05`에 등록됨. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json`의 F3 판단 14개사 전원의 `door_closed` 입력이 `fail`로 설정되어 있고, `results.json`의 F3 최종 점수가 전원 2점 또는 3점(4점 상한 이하)으로 문이 닫히지 않은 상태에서 5점을 부여한 사례가 전무함. — 8차 사실·출처 영역 기록을 그대로 옮겼다(`review-obsreg` part `fact-sources.md`). |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | Meta 광고주 생태계(유료 광고주), NVIDIA Nemotron 상업 연합(CUDA 무료 개발자는 불인정). 14개사 전원에서 공짜 사용자를 동맹으로 산입한 사례 없음 (`E:/sourcecode/.../AI기업_채점규칙_v1.5.md:198, 226행`). — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q16 | ①을 한 채널로만 쟀나? | fail | **승계 예외.** anthropic: 주채널을 업무로 적고도 개인 채널로 차단 (`TEN-RC-02`). openai: 주채널을 소비자라 적고 거래 채널로 차단 (`TEN-RC4-02`). v1.5 승계 예외. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | F2는 세 경로(성능 도약, 패러다임 적응, 표준 선점) 통과 수로 매핑 (`scorecard/rules/v1.7.json:factors.F2`). "표준 없음" 단독으로 감점된 회사 없음. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla F5에서 관계사 SpaceX는 동맹 산입 제외(A=0 적용, `judgments.json:tesla.F5`). SpaceX+xAI에서도 NASA/DoD 등 외부 동맹만 산입 확인. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | 피투자 관계를 동맹 +2로 센 v1.5 오류를 시정하여 Anthropic(A=+1), OpenAI(A=+1) 갱신 완료 (`judgments.json:anthropic.F5`, `openai.F5`). 동일한 잣대로 TSMC도 지분 동맹 0건 및 자신 경쟁사 편입 부재로 A=+1 재판정 (`judgments.json:tsmc.F5.strict54`). Alphabet, Amazon, Microsoft는 +2 요건 충족 유지 확인. 전사 일관 통과. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q20 | 조달을 동맹으로 셌나? | fail | **승계 예외.** Apple(칩 구매, Gemini 라이선스), Tesla(Starlink 조달), OpenAI(Oracle 클라우드 구매) 등 조달 관계는 동맹에서 제외됨. 다만 별표 H 3문(상대 이탈 가능성)과 관련해 NVIDIA는 불인정하고 타사는 인정한 이탈 기준 불일치가 승계 예외 `TEN-RC-03`으로 등록됨. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | fail | **승계 예외.** nvidia: F5 H=-2와 F8=-3의 자체 칩 이탈 중복 (`TEN-RC-05`). tesla: F5 H=-1과 F8=-2의 NHTSA 중복 (`TEN-RC3-04`). v1.5 승계 예외. — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | `scripts/scorecard/calc_qual.py:150-166` `compute_f7`은 오직 `funding_dependent_share`와 `own_money_returns` 두 축만 읽음. 지분 평가이익은 F6 P4 전용으로 F7로 이월되지 않음 (`scorecard/rules/v1.7.json:decisions` C-11 block_carryover 확인). — 8차 규칙 일관성 영역 기록을 그대로 옮겼다(`review-obsreg` part `rule-consistency.md`). |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | not_applicable | 조율자 분담 — 별도 세션 — 8차 사실·출처 영역 기록을 그대로 옮겼다(`review-obsreg` part `fact-sources.md`). |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- **8차 발견은 전부 FIX-59 에서 반영했다.** 점수를 바꾼 것은 하나도 없다.
  - 재무 계산 — `policies.f6.net_cash.securities_scope.how_to_measure` 의 `대차대조표 줄만 쓴다` 가 주석 분할 처리와 어긋나던 것을 좁혔고, 시장성 증권 잔여분 민감도 네 회사를 규칙에 적었다(밴드 이동 0). `C-26` 에 G4 분자·분모의 기준일·성질 차이를 합쳤다.
  - 사실·출처 분담 — `spacex-xai.F7` 의 계약 동일성 단정을 철회하고 관계자 거래 문면을 주석대로 고쳤다. 보존 원문 전수를 밑줄 없는 `raw/` 폴더까지 넓혀 다시 훑었고 **새로 나오는 사실은 없다**. alphabet 은 10-Q 표지 조각만 보존돼 있어 `anthropic.F8` 서술을 `본문이 없다` 로 좁혔다. C-03 이 F2 잣대를 교체해 승계 예외 요건을 엄밀히는 못 채운다는 사실을 `decisions C-03` 과 `TEN-RA4-01` 에 적었다.
  - 출력·가독성 — 자동 산출 factor 의 근거 블록 첫 줄에 이번 실행 점수를 세웠다.
- **openai.F9 경로** — 비 Claude 판정자(Gemini)가 `C-20 우선`(F9 -2 · 총점 4)으로 판정했고, **사용자가 현행 -4 유지 + 긴장 등록**을 골랐다(2026-09-17). 우선순위 문면은 `policies.f9.g1_bep_retreat_precedence`(채점규칙 470·494·603행), 반대 의견과 상향 가능성은 **TEN-RA5-02**(2026-11 · 비 Claude 세션)에 있다.
- **남은 기록성 지적은 미결·긴장으로 옮겼다** — 미결 C-23·C-25·C-26·C-27·C-28, 긴장 TEN-RA5-01(anthropic.F8 근거 확인 불가)·TEN-RA5-02(openai.F9 경로) 포함. 전부 재검토 시점 2026-11 이 붙어 있고 **2026-11 재채점의 입력**으로 쓴다.

## 판정

- **이 라운드는 여기서 끝난다(사용자 결정 2026-09-17).** 선택지 넷 — ①9차로 마무리 ②FIX-59 만 하고 승인 ③지금 바로 승인 ④B·A분담 pass 때까지 — 중 **②**를 골랐다. 근거는 **6·7·8차 연속으로 점수 변경이 0** 이고 남은 발견이 전부 기록 수준이라는 것이다. **9차 리뷰는 하지 않는다.**
- `status: pass` 가 뜻하는 것과 뜻하지 않는 것.
  - 뜻하는 것 — 네 영역 중 셋이 8차에서 pass 이고, 재무 계산의 8차 지적은 이번 반영으로 닫혔거나 재검토 시점이 붙은 미결·긴장으로 옮겨졌다. 14개사 총점은 6차 이후 한 칸도 바뀌지 않았다.
  - **뜻하지 않는 것** — 재무 계산 영역의 8차 결과 자체는 `needs_fix` 였고 이 표에 그대로 적었다. 체크리스트 Q01~Q23 을 이 파일에서 다시 돌린 것도 아니다. **사실을 pass 로 바꿔 적지 않았다.**
- ⚠️ **이 파일은 현재 계약 검증(`validate_report_contract.py`)을 통과하지 못한다.** 2026-09-17 승인 시도가 여기서 멈췄고 `approval.json` 은 만들어지지 않았다. 남은 오류 15건의 뿌리는 셋이다.
  1. `plan` 의 `rule_hash` 가 init 시점 값(`64fb4555…`)이고 현재 규칙 해시(`2fc704bf…`)와 다르다. `run.json` 은 매 반영마다 다시 고정해 현재 값과 같다 — plan 만 따라오지 않았다.
  2. 검토 영역 `재무 계산` 의 8차 결과가 `needs_fix` 다. 계약은 `status: pass` 일 때 네 영역이 모두 `pass` 여야 한다고 요구한다. 9차 리뷰를 하지 않기로 했으므로 이 영역을 다시 판정한 사람이 없다 — **`pass` 로 바꿔 적지 않았다.**
  3. 체크리스트 `fail` 12건이 `status: pass` 를 막는다. **그중 11건은 승계 판단 예외**이고 근거 칸에 긴장 번호가 있다 — AGENTS.md 71행과 이 파일 위쪽 문단은 그런 fail 이 `pass` 를 막지 않는다고 적는데 **`scripts/scorecard/validate.py` 에 그 예외를 읽는 코드가 없다**(선언에 소비자가 없는 형태다). 남은 하나 **Q11 은 예외가 아니다** — 사용자가 현행 유지 + `TEN-RA5-02` 등록을 골랐고, 이번 실행이 그 자리의 잣대를 문면으로 확정했으므로 예외 요건을 채우지 못한다.
- results_hash `a5b80e7111605945…` · draft_hash `1bf1408291a0d34b…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
