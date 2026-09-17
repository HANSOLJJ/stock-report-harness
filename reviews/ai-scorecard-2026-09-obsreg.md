---
slug: ai-scorecard-2026-09-obsreg
report_type: ai_scorecard
status: needs_fix
created_at: 2026-09-11
plan_source: plan/ai-scorecard-2026-09-obsreg.md
research_source: research/ai-scorecard-2026-09-obsreg.md
draft_source: drafts/ai-scorecard-2026-09-obsreg.md
results_hash: dda69e881f3f4c3be0e35b49395f688c9a68818a9c8c4f7907c9b8149b49c1ce
draft_hash: 9ac09ce39c5b980ec99ce8737513baf97cfa2747e7cc1d58e7810f74d55eb752
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: pass (8차 · Gemini 독립 세션 — 그 뒤 반영이 이 영역 대상을 바꾸지 않았다)"
  - "financial-calc: 9차 재판정 2회 needs_fix — Q11 은 fail 에서 pass 로. 영역 사유는 FIX-61·62 가 남긴 규칙 자기모순 둘이고 FIX-63 으로 반영했다(리뷰어 재확인 예정). 재계산 14개사 불일치 0"
  - "rule-consistency: pass (8차 · Gemini 독립 세션 — FIX-61~63 의 규칙 변경은 아직 안 봤다)"
  - "output-readability: pass (8차 · Gemini 독립 세션, low 둘 반영 — HTML 재빌드는 build 단계)"
---
# 리뷰 — AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장·이해상충 | 8차 Gemini 독립 세션 | pass | 8차 결과를 그대로 둔다 — 그 뒤 반영(FIX-59~63)이 이 영역의 대상을 바꾸지 않았다. 분담(부재 주장 전수, Claude 독립 세션)은 needs_fix 였고 FIX-58 2단계·FIX-59 로 전부 반영했다. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | 9차 재판정 2회 · Claude 독립 세션(NTM-전망치조사 워크트리) · 기준 커밋 `96afd80` | **needs_fix — FIX-63 으로 반영, 리뷰어 재확인 예정** | **pass 가 아니다.** 재계산은 14개사 전부 불일치 0 이고 `results_hash`·`draft_hash` 도 리뷰어가 직접 계산해 맞췄다. **체크리스트 Q11 은 9차 fail 에서 pass 로 바뀌었다** — C-28·C-29 반영을 합성 관측과 시뮬레이션으로 재현해 확인했다. 그런데도 영역이 `needs_fix` 인 것은 **FIX-61·FIX-62 가 9차 지적을 고치면서 새 모순 둘을 남겼기 때문**이다(C-06 `summary` 의 자기모순 · `also_precedes_loss_band` 의 틀린 닫음). **이번 반영(FIX-63)으로 둘 다 고쳤고 전수로 훑어 같은 계열을 둘 더 고쳤다** — 그 결과를 리뷰어가 다시 볼 예정이며, 이 칸은 그때까지 재판정 2회의 결과를 그대로 적는다. |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | 8차 Gemini 독립 세션 | pass | 8차 결과를 그대로 둔다. 7차에서 든 `선언에 소비자 없음` 세 건(C-11·C-13·C-24)은 FIX-57·FIX-58 에서 정리했다. **이 영역이 다시 볼 자리가 생겼다** — FIX-61~63 이 규칙 파일을 세 번 더 고쳤고 그중 자기모순 둘은 재무 계산 영역이 잡았다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | 8차 Gemini 독립 세션 | pass | 8차 결과를 그대로 둔다. low 둘은 FIX-59 에서 반영했다. **빌드 HTML 은 이번 반영 뒤 다시 만들지 않았다** — C-06 `summary` 가 방법 표에 실리므로 build 단계에서 새 문면이 들어간다. |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

**체크리스트 23행의 출처가 둘이다.** Q04·Q06·Q10·Q11 넷은 **9차 재무 계산 재판정 2회**(`review-obsreg`
커밋 `6878e79`, `reviews/_parts/ai-scorecard-2026-09-obsreg/financial-calc.md`)의 기록이고, 나머지 19행은 **8차 라운드**
네 영역 part 기록(같은 저장소 `e5a47d3`)을 그대로 옮긴 것이다. 이 파일에서 체크리스트를 다시 돌리지는 않았다 —
각 행의 근거 칸 끝에 어느 기록인지 적혀 있다. 담당은 겹치지 않는다: 규칙 일관성 15문항 · 재무 계산 4문항 ·
사실·출처 4문항.

**fail 이 11건이고 전부 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). **Q11 은 9차 fail 에서 pass 로 바뀌었다** —
리뷰어가 C-28·C-29 반영을 합성 관측과 시뮬레이션으로 재현해 확인했고, 그 판정은 리뷰어의 것이지 우리가 고쳐 적은
것이 아니다. 바뀐 범위는 아래 발견 사항에 리뷰어의 문장 그대로 적었다.

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | fail | **승계 예외.** nvidia: F5 H=-2(고객이 경쟁자)와 F8=-3(고객 40% 자체 칩 개발) 중복 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC-05`). tesla: F5 H=-1과 F8=-2에 NHTSA 조사 중복 (`TEN-RC3-04`). v1.5 승계 논리이며 2026-11 재검토 등록되어 pass 유지. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | **승계 예외.** anthropic: F1 주채널 업무 지정 후 개인 사용자 수 열세로 차단 (`TEN-RC-02`). palantir vs oracle: 업무 전환비용 상반 취급 (`TEN-RC3-03`). alibaba: 경쟁사 오픈웨이트 배포 상황에서 F3 모방불가 partial (`TEN-RC3-05`). openai: F1 소비자 주채널 분류 후 거래 채널로 차단 (`TEN-RC4-02`). anthropic·openai: F7 매트릭스 입력 미복원 (`TEN-RC3-01`). 모두 v1.5 승계 예외. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q03 | 회사마다 같은 잣대인가? | fail | **승계 예외.** 이번 실행이 바꾼 잣대(F5 A-STRICT-54 TSMC 재판정, F6 순현금 securities_scope 전사 통일, C-24 신규 상장 트랙 P2)는 14개사 전사에 동일하게 적용됨 (`scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:tsmc.F5.strict54`, `scripts/scorecard/calc_f6_params.py:345`). v1.5 승계 판단의 전사 불일치는 `TEN-RC-03`(별표 H 이탈 조건), `TEN-RC3-01`(F7 매트릭스), `TEN-RC3-03`(F1 전환비용), `TEN-RC4-03`(F5 H=-1 수 비교)으로 등록된 승계 예외. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 시총이 점수에 들어가는 자리는 비율의 분자뿐이다(`v1.7.json` P1·P2 `formula`, `calc_f6_params.py:280~285`). 규모 자체를 재는 밴드가 F6·F9 어디에도 없고 결과가 그것을 보여 준다 — 표 전체 최대 시총인 nvidia(약 $5.42T)가 F6 -2 로 상위이고, 훨씬 작은 palantir 가 -4 · tesla 가 -5 다. 비상장도 `private_bands.input` 이 `ps_ratio` 라 밸류 절대액이 아니다 — 9차 재무 계산 재판정 2회(`review-obsreg` `6878e79`). |
| Q05 | 출처가 이해당사자인가? | fail | `nvidia.F2`(TEN-RA-02) 벤더 발표 1차 인용, `openai.F4`(TEN-RA3-01) 자체 발표 인용. 다만 v1.5 승계 논리이고 규칙 파일 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`(재검토 2026-11)로 등록되어 승계 판단 예외 적용. 이번 실행이 바꾼 신규 판단(`anthropic.F5.impl48`, `openai.F5.impl48`, `anthropic.F8.f8anth33`)은 SEC 8-K·10-Q 및 별표 규정을 직접 확인하여 정합함. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q06 | 볼륨인가 가치인가? | pass | 관측 단위가 `USD`·`USD/share`·`ratio`·`text`·`years` 넷뿐이고 토큰 수·사용자 수 같은 볼륨 지표가 363건 중 한 건도 없다. P3 는 매출 성장률, G4 는 계약 수입 대 약정으로 둘 다 금액 기준이다. 볼륨과 가치를 가르는 장치도 실제로 문다 — `private_correction.conditions[arr_growth].accepted_kinds:["actual"]` 가 런레이트를 ARR 로 세지 않아 anthropic 0.382979 · openai 0.600000 이 임계를 넘고도 불충족이다 — 9차 재무 계산 재판정 2회(`review-obsreg` `6878e79`). |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 14개사 전수 조사 결과 "안 만든 것" 자체를 카운터 포지셔닝으로 인정한 회사 없음. Amazon은 Bedrock 매대 전략의 모방불가 fail (`judgments.json:amazon.F3`), Apple은 디바이스 ① 중복으로 모방불가 fail (`judgments.json:apple.F3`)로 엄격 판정. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | **승계 예외.** spacex-xai: F5 H=-1 근거가 적대의 종류가 아닌 "동맹이 적보다 확실히 많지 않음"이라는 수 비교 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC4-03`). Apple(비용형 -1), NVIDIA(구조형 -2), Palantir(구조형 -2), OpenAI(다발형 -3) 등 타사는 성격으로 분류됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | `nvidia.F2`(TEN-RA-02) Rubin 미래 양산·출하 반영, `openai.F4`(TEN-RA3-01) 2027~2028년 배치 계획 혼재. 다만 v1.5 승계 논리이고 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`로 등록되어 승계 판단 예외 적용. 반면 F3 전원 door_closed=fail 및 F4 타사 출하 기준은 준수됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q10 | 거리를 가속도로 착각했나? | pass | 거리(수준)와 가속(변화율)을 쓰는 자리가 갈려 있다. P3 는 `revenue_ttm / revenue_ttm_prior - 1` 로 변화율이고 누적 매출이 아니다. G3 런웨이는 수준을 수준으로, G2 는 `fcf_trend` 로 방향만 받는다. F6·F9 안에서 누적 성과를 성장률 자리에 넣은 곳을 찾지 못했다. 9차에 든 `arr_prior` 기간 미상은 FIX-61 이 `basis.period_unknown_blocks_growth` 로 적었고 여전히 점수에 닿지 않는다 — 9차 재무 계산 재판정 2회(`review-obsreg` `6878e79`). |
| Q11 | 순적자를 실격 사유로 썼나? | **pass** (9차 fail 에서 바뀜) | **근거 둘이 다 닫혔다.** **(1)** C-28 이 `resolved`(`chosen: optional_parameters_for_all_listed_tracks`, `v1.7.json:1981`)이고 세 트랙이 `optional_parameters: [P1]` · `optional_parameters_causes: {P1:[requires_positive]}` 를 갖는다. **합성 관측으로 직접 재현했다** — tesla 의 `net_income_ttm` 만 음수로 뒤집으면 이제 `score=-3 · status=ok`(P2 -1 + P3 -2)이고 `parameters_optional_unmet.P1.cause=requires_positive` 다. 9차에는 같은 입력이 `score=None · pending_data` 였다. alibaba(`listed_annual`)로도 같게 나온다(-4). **가드 둘도 그대로다**: 순이익 관측이 아예 없으면 여전히 `pending_data`(수집 공백을 조용히 넘기지 않는다), 소유 범위가 어긋나도 여전히 `pending_data`(FC-04). 대조군은 원값 -5·-4 를 정확히 재현했다. **1999년 아마존이 이제 ⑥ 을 받는다.** **(2)** C-29(`v1.7.json:2012`, 사용자 결정 2026-09-17, 앞선 결정 뒤집음)로 openai 가 C-20 경로를 타고 F9 -2 를 받는다. 그 -2 는 `g2_private_not_disclosed` 즉 **공시 여부**에서 나오지 순적자에서 나오지 않고, `bep_retreat: no` 인 anthropic 이 같은 -2 를 받아 **두 비상장사의 처리가 같다.** 전망(BEP 2030 후퇴)으로 가장 깊은 칸을 주던 자리가 사라졌다. **이번 실행에서 순적자 때문에 점수를 못 받거나 실격된 기업이 없다** — 유일한 순손실 상장사 spacex-xai 는 측정된 단위경제로만 채점된다(P2 80.27 · P3 +91.9% · G1 손실률 -16.195% · G3 런웨이 3.03년 · G4 커버리지 1.60). 남는 잠재는 아래 발견 사항에 적었고 TEN-RA6-01 로 등록돼 있다 — 9차 재무 계산 재판정 2회(`review-obsreg` `6878e79`). |
| Q12 | ③ 세 기준을 동등하게 쟀나? | fail | **승계 예외.** F3 사다리는 모방불가 pass 없이 4점 이상 진입 불가 (`scorecard/rules/v1.7.json:factors.F3.ladder[3].requires_imitation_pass`). 전원 3점 이하 절단 확인. 단 meta·anthropic·spacex-xai의 imitation partial 근거 불충분 긴장이 `TEN-RC4-01`로 등록됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | fail | **승계 예외.** 오픈웨이트 무료 배포를 곧바로 카운터 포지셔닝으로 인정하지 않고 회수 장치 부재를 엄격 지적 (`judgments.json:alibaba.F3`). 단 오픈웨이트 배포 기업들의 imitation partial 부여 논리가 승계 예외 `TEN-RC4-01`, `TEN-RC3-05`에 등록됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json`의 F3 판단 14개사 전원의 `door_closed` 입력이 `fail`로 설정되어 있고, `results.json`의 F3 최종 점수가 전원 2점 또는 3점(4점 상한 이하)으로 문이 닫히지 않은 상태에서 5점을 부여한 사례가 전무함. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | Meta 광고주 생태계(유료 광고주), NVIDIA Nemotron 상업 연합(CUDA 무료 개발자는 불인정). 14개사 전원에서 공짜 사용자를 동맹으로 산입한 사례 없음 (`E:/sourcecode/.../AI기업_채점규칙_v1.5.md:198, 226행`). — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q16 | ①을 한 채널로만 쟀나? | fail | **승계 예외.** anthropic: 주채널을 업무로 적고도 개인 채널로 차단 (`TEN-RC-02`). openai: 주채널을 소비자라 적고 거래 채널로 차단 (`TEN-RC4-02`). v1.5 승계 예외. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | F2는 세 경로(성능 도약, 패러다임 적응, 표준 선점) 통과 수로 매핑 (`scorecard/rules/v1.7.json:factors.F2`). "표준 없음" 단독으로 감점된 회사 없음. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla F5에서 관계사 SpaceX는 동맹 산입 제외(A=0 적용, `judgments.json:tesla.F5`). SpaceX+xAI에서도 NASA/DoD 등 외부 동맹만 산입 확인. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | 피투자 관계를 동맹 +2로 센 v1.5 오류를 시정하여 Anthropic(A=+1), OpenAI(A=+1) 갱신 완료 (`judgments.json:anthropic.F5`, `openai.F5`). 동일한 잣대로 TSMC도 지분 동맹 0건 및 자신 경쟁사 편입 부재로 A=+1 재판정 (`judgments.json:tsmc.F5.strict54`). Alphabet, Amazon, Microsoft는 +2 요건 충족 유지 확인. 전사 일관 통과. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q20 | 조달을 동맹으로 셌나? | fail | **승계 예외.** Apple(칩 구매, Gemini 라이선스), Tesla(Starlink 조달), OpenAI(Oracle 클라우드 구매) 등 조달 관계는 동맹에서 제외됨. 다만 별표 H 3문(상대 이탈 가능성)과 관련해 NVIDIA는 불인정하고 타사는 인정한 이탈 기준 불일치가 승계 예외 `TEN-RC-03`으로 등록됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | fail | **승계 예외.** nvidia: F5 H=-2와 F8=-3의 자체 칩 이탈 중복 (`TEN-RC-05`). tesla: F5 H=-1과 F8=-2의 NHTSA 중복 (`TEN-RC3-04`). v1.5 승계 예외. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | `scripts/scorecard/calc_qual.py:150-166` `compute_f7`은 오직 `funding_dependent_share`와 `own_money_returns` 두 축만 읽음. 지분 평가이익은 F6 P4 전용으로 F7로 이월되지 않음 (`scorecard/rules/v1.7.json:decisions` C-11 block_carryover 확인). — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | not_applicable | 조율자 분담 — 별도 세션 — 8차 part 기록(`review-obsreg` `e5a47d3`). |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- **9차 재판정 2회의 발견 다섯 중 넷을 FIX-63 에서 반영했다.** 점수를 바꾼 것은 하나도 없다.
  - **[medium] 규칙이 스스로 모순됐다** — decisions C-06 `summary` 가 `BEP 후퇴가 … C-20 비상장 경로보다 앞선다` 로 적혀 있었다. FIX-61 이 그렇게 고쳐 넣었고 **같은 날 FIX-62 가 그 순서를 뒤집었다**(C-29). `policies.f9.g1_bep_retreat_precedence.what_is_true_now` 와 정반대였고, **이 문자열은 빌드 HTML 의 방법 표에 실린다**(`render_html.render_method`). 현재 사실로 고쳤다.
  - **[medium] `also_precedes_loss_band` 의 `순서가 관측되지 않는다` 가 사실이 아니었다** — `calc_f9.py` 의 `if bep_retreat:` 가 밴드를 아예 보지 않고 단락시켜, 손실률이 최심 밴드가 아니면 두 순서의 결과가 다르다. 리뷰어가 시뮬레이션으로 확인했고 우리도 재현했다(spacex-xai 에 `bep_retreat` 만 `yes` 로 바꾸면 F9 -3 → -4). 문면을 사실로 고치고 **틀린 주장을 굳혀 놓았던 테스트**(`tests/test_scorecard_fix61.py`)도 같이 고쳤다. **미결로 새로 등재하지 않고** TEN-RA6-01 의 범위에 상장사 자리를 명시해 넣었다(사유는 `g1_bep_retreat_precedence.why_no_new_pending_decision`).
  - **[low] FIX-62 의 재배열이 문서보다 한 칸 더 갔다** — 새 코드는 C-20 탐지를 `reviewed_sign == "profit"` 보다도 앞에 둔다. 리뷰어가 **새 순서가 더 맞다**고 봤으므로 코드는 그대로 두고 C-29 `scope.what_changed` 에 이 변화를 적었다. 이번 실행에 해당 기업은 없다.
  - **[low] 계획의 결정 표가 세 세대 전 문면이었다** — 머리말 해시만 손으로 고쳐 오는 동안 본문 표가 `BEP 후퇴→-5 … 명문화만 미결` 로 남아 있었다. 표를 현재 규칙에서 다시 만들었고(C-05·C-06·C-16 셋), `rule_hash_history` 와 손으로 쌓은 절은 유지했다.
  - **[low] 이 파일의 frontmatter 가 8차 값이었다** — 이번 재생성으로 맞췄다.
- **전수 조사에서 리뷰어가 짚지 않은 자리를 둘 더 찾아 고쳤다.** 재판정 2회가 `같은 종류를 전수로 훑으라` 고 해서 규칙·코드·문서에서 `bep_retreat`·`C-20`·우선순위를 말하는 문장을 모두 대조했다.
  - decisions **C-07** `implementation_status.routes.openai` 가 `G4 에 아예 닿지 않는다 — G1 에서 BEP 후퇴로 실패해 하한 -4` 로 적었다. C-29 뒤로 openai 는 anthropic 과 같은 경로이고 F9 는 -2 다. C-07 의 판정 자체는 바뀌지 않는다(`coverage_comparable=no` 로 두 겹 차단이 그대로 선다).
  - `render_common.method_lines` 가 `두 경로가 만나도 결과는 같다` 를 그대로 말해 초안·HTML 까지 흘렀다. 위 medium 둘째와 같은 오추론이다.
- **Q11 이 pass 로 바뀐 범위**(리뷰어 문장) — `실현된 노출이 없어졌다는 뜻이고 조항이 가리키는 자리가 전부 사라졌다는 뜻은 아니다. 상장사에 bep_retreat: yes 가 들어오면 측정된 손실률 밴드를 전망이 덮어쓰는 경로가 남아 있다. 오늘 그런 회사가 없고, 조항 충돌 자체는 TEN-RA6-01(open · recheck_at 2026-11 · 비 Claude 재판정 확정)로 등록돼 있다.`
- **리뷰어의 이해상충 고지**(그대로 옮긴다) — `openai F9 의 경로를 내가 고른 것이 아니다. 나는 9차에 체크리스트 Q11 을 fail 로 보고 승계 예외가 안 선다고만 적었고 점수는 건드리지 않았다. 이번에도 엔진이 사용자 결정(C-29)을 제대로 수행했는지만 확인했다. 결과가 Anthropic 경쟁사의 총점을 올리는 방향(2 → 4)이라는 점도 판정에 넣지 않았다.`
- **리뷰어가 확인하지 못한 것 여섯**이 part 에 그대로 남아 있다(oracle B종 약정 250,000M 의 출처 · alibaba `nonop_share` 저장값과 재계산의 차 · tsmc 20-F 원문 직접 대조 · `market_cap`·`ntm_per` 각 12건의 실측 · 비상장 2사의 `ps_ratio` · openai `operating_result_reviewed: loss` 의 근거). 어느 것도 이번 점수를 가르지 않는다.

## 판정

- **재무 계산 영역은 아직 pass 가 아니다.** 9차 재판정 2회가 `needs_fix` 로 판정했고 사유였던 모순 둘을 이번 반영으로 고쳤다. **그 결과를 리뷰어가 다시 볼 예정이고, 그때까지 이 표의 결과를 바꿔 적지 않는다.**
- `status` 가 `needs_fix` 인 이유가 그것 하나다. 체크리스트 fail 11건은 전부 승계 판단 예외이고(근거 칸에 긴장 번호가 있다), **9차 fail 이던 Q11 은 리뷰어 재판정으로 pass 가 됐다.**
- **점수는 이번 반영에서 한 칸도 바뀌지 않았다.** 14개사 총점이 alphabet 15 · amazon 15 · meta 15 · microsoft 14 · anthropic 10 · tsmc 10 · spacex-xai 9 · nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · openai 4 · oracle 2 그대로다.
- **같은 실수가 세 번째였다.** 8차·9차·재판정 2회가 연달아 `확정한 것을 미결이라고 적는다`·`뒤집은 것을 반대로 적는다`·`틀린 근거로 닫는다` 를 잡았다. 셋 다 규칙 문면이 코드보다 늦게 따라온 자리이고, **점수에는 한 번도 닿지 않았다.** 이번에는 전수로 훑어 리뷰어가 짚지 않은 둘을 더 찾았다.
- results_hash `dda69e881f3f4c3b…` · draft_hash `9ac09ce39c5b980e…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트**의 sha256 이다(`stages.sha256_file`). 승인 해시 대조는 `stages.current_hashes` 가 같은 규약으로 다시 계산해 비교한다.
- `approval.json` 은 아직 만들어지지 않았다. **승인은 리뷰어 재확인 뒤에 간다.**
