---
slug: ai-scorecard-2026-09-obsreg
report_type: ai_scorecard
status: pass
created_at: 2026-09-11
plan_source: plan/ai-scorecard-2026-09-obsreg.md
research_source: research/ai-scorecard-2026-09-obsreg.md
draft_source: drafts/ai-scorecard-2026-09-obsreg.md
results_hash: 4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b
draft_hash: 7eddab49d6adf56fe8ffd5becdd063ee075f2378370da9e33cd207d73ef4a782
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: pass (8차 · Gemini 독립 세션)"
  - "financial-calc: pass (9차 · Claude 독립 세션 · 재판정 3회 · 최종 기준 커밋 f313060) — 8차 needs_fix 에서 FIX-59·61·63 반영을 거쳐 pass. 잔존 전수 0건 · 재계산 14개사 불일치 0 · 점수 페이로드 96afd80 과 바이트 동일"
  - "rule-consistency: pass (8차 · Gemini 독립 세션 — FIX-61~64 의 규칙 문면 변경은 미검토)"
  - "output-readability: pass (8차 · Gemini 독립 세션, low 둘 반영 — HTML 은 build 에서 재생성)"
---
# 리뷰 — AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장·이해상충 | 8차 · Gemini 독립 세션 | pass | 발견 사항 없음. 분담(부재 주장 전수, Claude 독립 세션)은 needs_fix 였고 FIX-58 2단계·FIX-59 로 전부 반영했다 — 상대방 제출본까지 범위를 넓혀 다시 훑었고 등록할 사실은 없었다. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | 9차 · Claude 독립 세션(NTM-전망치조사 워크트리) · **재판정 3회** · 최종 기준 커밋 `f313060` | pass | **8차 needs_fix → FIX-59·61·63 반영 → 재판정 3회 끝에 pass.** 경과가 길었던 이유는 반영이 매번 새 문면 모순을 남겼기 때문이다 — 8차는 지적이 기록 수준이었고, 9차는 FIX-59 가 확정한 것을 세 자리가 `미결` 이라 적는 것과 순손실 상장사 트랙을 잡았으며(FIX-61), 재판정 2회는 FIX-61·62 가 남긴 자기모순 둘을 잡았다(FIX-63). **마지막 판정에서 리뷰어가 고쳤다는 주장을 믿지 않고 직접 다시 훑었다** — 정규식 다섯 갈래로 산출물 10곳·코드 19파일·문서 전체를 독립 전수해 **살아 있는 잔존 0건**을 확인했고, 재계산 14개사 불일치 0 · 새 해시 직접 계산 일치 · 점수 페이로드가 `96afd80` 과 **바이트 동일**인 것도 기계로 확인했다. 새 발견 low 하나(`bep_retreat` 의 도달 범위를 문면이 좁게 적음)는 **FIX-64 에서 닫았다** — 아래 판정 절에 적었다. |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | 8차 · Gemini 독립 세션 | pass | 발견 사항 없음. 7차에서 든 `선언에 소비자 없음` 세 건(C-11·C-13·C-24)은 FIX-57·FIX-58 에서 정리했다. **FIX-61~64 가 바꾼 규칙 문면은 이 영역이 아직 보지 않았다** — 재무 계산 영역이 자기 범위(F9 우선순위 서술·C-06·C-07·C-29·TEN-RA6-01)만 확인했다고 밝혔고, 그 밖의 변경은 전부 기록·서술이며 점수에 닿지 않는다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | 8차 · Gemini 독립 세션 | pass | low 둘 반영. 자동 산출 factor 의 기준선 참고 블록이 옛 점수로 시작하던 것을 FIX-59 에서 현재 점수가 첫 줄에 오게 고쳤고, HTML 이해상충 문구의 동적 연산은 정상 동작을 확인했다(조치 없음). **HTML 은 이 승인 뒤 build 단계에서 새로 만들어진다** — C-06 `summary` 가 방법 표에 실리므로 이번 라운드에 고친 문면이 그때 들어간다. |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

**체크리스트 23행의 출처가 둘이다.** Q04·Q06·Q10·Q11 넷은 **9차 재무 계산 최종 판정**(재판정 3회,
`review-obsreg` 커밋 `ce0fd57`)의 기록이고, 나머지 19행은 **8차 라운드** 네 영역 part 기록(같은 저장소 `e5a47d3`)을
그대로 옮긴 것이다. 이 파일에서 체크리스트를 다시 돌리지는 않았다 — 각 행의 근거 칸 끝에 어느 기록인지 적혀 있다.
담당은 겹치지 않는다: 규칙 일관성 15문항 · 재무 계산 4문항 · 사실·출처 4문항.

**fail 이 11건이고 전부 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). **Q11 은 9차 fail 에서 pass 로 바뀌었다** —
리뷰어가 C-28·C-29 반영을 합성 관측과 시뮬레이션으로 재현해 확인했고, 그 판정은 리뷰어의 것이지 우리가 고쳐 적은
것이 아니다.

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | fail | **승계 예외.** nvidia: F5 H=-2(고객이 경쟁자)와 F8=-3(고객 40% 자체 칩 개발) 중복 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC-05`). tesla: F5 H=-1과 F8=-2에 NHTSA 조사 중복 (`TEN-RC3-04`). v1.5 승계 논리이며 2026-11 재검토 등록되어 pass 유지. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | **승계 예외.** anthropic: F1 주채널 업무 지정 후 개인 사용자 수 열세로 차단 (`TEN-RC-02`). palantir vs oracle: 업무 전환비용 상반 취급 (`TEN-RC3-03`). alibaba: 경쟁사 오픈웨이트 배포 상황에서 F3 모방불가 partial (`TEN-RC3-05`). openai: F1 소비자 주채널 분류 후 거래 채널로 차단 (`TEN-RC4-02`). anthropic·openai: F7 매트릭스 입력 미복원 (`TEN-RC3-01`). 모두 v1.5 승계 예외. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q03 | 회사마다 같은 잣대인가? | fail | **승계 예외.** 이번 실행이 바꾼 잣대(F5 A-STRICT-54 TSMC 재판정, F6 순현금 securities_scope 전사 통일, C-24 신규 상장 트랙 P2)는 14개사 전사에 동일하게 적용됨 (`scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:tsmc.F5.strict54`, `scripts/scorecard/calc_f6_params.py:345`). v1.5 승계 판단의 전사 불일치는 `TEN-RC-03`(별표 H 이탈 조건), `TEN-RC3-01`(F7 매트릭스), `TEN-RC3-03`(F1 전환비용), `TEN-RC4-03`(F5 H=-1 수 비교)으로 등록된 승계 예외. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 시총이 점수에 들어가는 자리는 비율의 분자뿐이다(`v1.7.json` P1·P2 `formula` · `calc_f6_params.py:280~285`). 규모를 재는 밴드가 F6·F9 어디에도 없고 결과가 그것을 보여 준다 — 최대 시총 nvidia(약 $5.42T)가 F6 -2 로 상위, 훨씬 작은 palantir 가 -4 · tesla 가 -5 다. 비상장도 `private_bands.input` 이 `ps_ratio` 다 — 9차 재무 계산 최종 판정 · 재판정 3회(`review-obsreg` `ce0fd57`). |
| Q05 | 출처가 이해당사자인가? | fail | `nvidia.F2`(TEN-RA-02) 벤더 발표 1차 인용, `openai.F4`(TEN-RA3-01) 자체 발표 인용. 다만 v1.5 승계 논리이고 규칙 파일 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`(재검토 2026-11)로 등록되어 승계 판단 예외 적용. 이번 실행이 바꾼 신규 판단(`anthropic.F5.impl48`, `openai.F5.impl48`, `anthropic.F8.f8anth33`)은 SEC 8-K·10-Q 및 별표 규정을 직접 확인하여 정합함. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q06 | 볼륨인가 가치인가? | pass | 관측 단위가 `USD`·`USD/share`·`ratio`·`text`·`years` 넷뿐이고 볼륨 지표가 363건 중 0건이다. P3 는 매출 성장률, G4 는 계약 수입 대 약정으로 둘 다 금액 기준이다. `private_correction.conditions[arr_growth].accepted_kinds:["actual"]` 가 런레이트를 ARR 로 세지 않아 anthropic 0.382979 · openai 0.600000 이 임계를 넘고도 불충족이다 — 9차 재무 계산 최종 판정 · 재판정 3회(`review-obsreg` `ce0fd57`). |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 14개사 전수 조사 결과 "안 만든 것" 자체를 카운터 포지셔닝으로 인정한 회사 없음. Amazon은 Bedrock 매대 전략의 모방불가 fail (`judgments.json:amazon.F3`), Apple은 디바이스 ① 중복으로 모방불가 fail (`judgments.json:apple.F3`)로 엄격 판정. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | **승계 예외.** spacex-xai: F5 H=-1 근거가 적대의 종류가 아닌 "동맹이 적보다 확실히 많지 않음"이라는 수 비교 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC4-03`). Apple(비용형 -1), NVIDIA(구조형 -2), Palantir(구조형 -2), OpenAI(다발형 -3) 등 타사는 성격으로 분류됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | `nvidia.F2`(TEN-RA-02) Rubin 미래 양산·출하 반영, `openai.F4`(TEN-RA3-01) 2027~2028년 배치 계획 혼재. 다만 v1.5 승계 논리이고 `scorecard/rules/v1.7.json:2217,2333`에 각각 `TEN-RA-02`, `TEN-RA3-01`로 등록되어 승계 판단 예외 적용. 반면 F3 전원 door_closed=fail 및 F4 타사 출하 기준은 준수됨. — 8차 part 기록(`review-obsreg` `e5a47d3`). |
| Q10 | 거리를 가속도로 착각했나? | pass | P3 는 `revenue_ttm / revenue_ttm_prior - 1` 로 변화율이고 누적이 아니다. G3 런웨이는 수준을 수준으로, G2 는 `fcf_trend` 로 방향만 받는다. 누적 성과를 성장률 자리에 넣은 곳을 F6·F9 에서 찾지 못했다. `arr_prior` 기간 미상은 `basis.period_unknown_blocks_growth` 에 적혀 있고 여전히 점수에 닿지 않는다 — 9차 재무 계산 최종 판정 · 재판정 3회(`review-obsreg` `ce0fd57`). |
| Q11 | 순적자를 실격 사유로 썼나? | pass | **직전 판정에서 fail → pass 로 바꾼 것을 유지한다.** 근거 둘이 그대로 닫혀 있다 — C-28 `resolved` 로 순손실 상장사가 P2·P3 로 채점되고(합성 관측 재현: `score=-3 · status=ok` · `cause=requires_positive`), 수집 공백과 소유 범위 불일치는 여전히 `pending_data` 로 막힌다. C-29 로 openai 가 anthropic 과 같은 C-20 경로를 타 `g2_private_not_disclosed` -2 를 받고, 전망으로 하한을 주던 자리가 없다. 이번 실행에서 순적자 때문에 점수를 못 받거나 실격된 기업이 없다 — 유일한 순손실 상장사 spacex-xai 는 측정된 단위경제로만 채점된다(P2 80.27 · P3 +91.9% · G1 -16.195% · G3 3.03년 · G4 1.60) — 9차 재무 계산 최종 판정 · 재판정 3회(`review-obsreg` `ce0fd57`). |
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

- **9라운드에 걸친 리뷰가 여기서 끝난다.** 네 영역이 모두 pass 이고 마지막 발견까지 닫았다.
- **마지막 판정의 새 발견 하나를 FIX-64 에서 고쳤다**(아래 판정 절에 판단 근거를 적었다).
- **이월 두 건은 이미 등록돼 있다.** 리뷰어가 `이월, 등록됨` 으로 분류한 것이고 새로 할 일이 없다.
  - oracle F6 P1 = 25.967109 가 밴드 경계 25 에서 **+3.87%** 로 허용폭 3% 밖이라 경계 표시가 안 붙는다. 이 한 칸이 oracle 총점 2 와 3 을 가른다. **미결 `C-27`** 에 alibaba G3(+3.32%)와 함께 **표본 둘**로 적혀 있다.
  - `oracle.undrawn_credit.fix54` 가 null 인데 `calc_f9._runway` 의 `undrawn or 0.0` 이 0 으로 센다. **결정 `C-04`** 가 완충을 `현금 + 확정 미인출 여신` 으로 좁혀 **설계대로**이고, 뒤집히려면 39,769M 이상이 필요하다는 크기까지 관측 `basis.null_counts_as_zero` 에 적혀 있다. 보존 ORCL companyfacts 에 해당 태그 사실이 없어 `unverified` 라벨도 맞다.
- **리뷰어가 확인하지 못한 것 여섯**이 최종 part 에 그대로 남아 있다 — oracle B종 약정 250,000M 의 출처(C-26) · alibaba `nonop_share` 저장값과 재계산의 차 · tsmc 20-F 원문 직접 대조 · `market_cap`·`ntm_per` 각 12건의 실측 · 비상장 2사의 `ps_ratio` · **FIX-61~64 가 바꾼 규칙 문면의 규칙 일관성 검토**. 어느 것도 이번 점수를 가르지 않는다.
- **리뷰어의 이해상충 고지**(그대로 옮긴다) — `openai F9 의 경로를 내가 고른 것이 아니다. 나는 9차에 체크리스트 Q11 을 fail 로 보고 승계 예외가 안 선다고만 적었고 점수는 건드리지 않았다. 이번에도 엔진이 사용자 결정(C-29)을 제대로 수행했는지만 확인했다. 결과가 Anthropic 경쟁사의 총점을 올리는 방향(2 → 4)이라는 점도 판정에 넣지 않았다.`
- **작성자 이해상충** — 이 채점표를 Anthropic 이 만든 Claude 가 작성했고 Anthropic 이 채점 대상에 들어 있다(채점규칙 384행). Anthropic 점수에 걸린 긴장은 비 Claude 세션이 재판정한다(TEN-RC-02 · TEN-RC3-01 · TEN-RA4-01 · TEN-RA5-01).

## 초안 변경 기록 (2026-09-17 FIX-67)

**이 리뷰 뒤에 초안이 바뀌었다.** 아래 `draft_hash` 는 검토 당시 값이고 현재 초안은 `917bb9809a5dca62a57096c8cbc430380c25f9957854f4fc3ba7f26aceebebef` 다.
계약 검증이 `초안이 바뀌었으므로 리뷰 무효` 로 막는 것이 정상이며, **해시 갱신은 재검토가 붙은 뒤에 한다.**

무엇이 바뀌었나.

- **방법 절 문장을 전면 재작성했다.** 규칙을 만들며 주고받은 기록이라 결정 번호를 아는 사람만 읽을 수 있던 문장을, 뜻을 그대로 둔 채 읽는 사람을 위한 글로 옮겼다. 결정 번호는 문장에서 빼 `관련 결정` 줄로 보냈고, 누가 언제 뒤집었다는 기록은 결정 항목이 이미 들고 있어 뺐다.
- **본문에서 `P1`·`G3` 같은 번호를 쓰지 않고 이름을 쓴다**(PER · EV/매출 · 매출 성장 · 입력 신뢰도 / 본업 · 현금 · 런웨이 · 약정 커버리지). `results.json` 안의 번호는 그대로이고 **표시할 때 옮겨 그린다.**
- **해시·입력 지문·실행 단위 선택·미결 결정 표를 감사 기록(`output/<slug>-audit.md`)으로 옮겼다.**
- 관측 지표·상태·조건의 내부 이름도 한국어로 옮겼다(`market_cap` → 시가총액 등).
- **[FIX-68]** 런웨이·약정 커버리지 문장이 규칙과 달라 고쳤고(1~3년 구간 누락 · 1년 밑 두 칸 · 1배 미만 감점 누락), 근거 값과 방식 값을 한국어로 옮겼으며 이름 뒤 조사를 받침에 맞게 골랐다.
- **[FIX-69]** 독립 검토가 방법 문장에서 규칙과 어긋나는 곳 여덟을 찾아 고쳤다. 둘은 실제 회사에 걸렸다 — 넷째 관문의 `확인된 미공시` 분기가 빠져 alibaba 의 -3 을 설명할 수 없었고, 비상장 승격의 `실측만 인정` 제한이 빠져 anthropic 이 문장대로면 -3 이 나왔다(실제 -4). 나머지 여섯은 지시 대상 모호·진단 경로·여신 문장·절댓값 부등호·기간 단위 범위·② 누락이다. **점수는 그대로다.**
- **[FIX-70]** 앞 지적에서 틀린 절을 지우기만 하고 대신할 문장을 넣지 않아, 기업 카드의 `생략`·`진단` 이 설명 없이 남아 있었다. 관문이 어떻게 이어지는지와 두 말의 뜻을 넣었고 첫째 관문에서 막힌 뒤 계산한 값을 점수에 넣는지(아직 정해지지 않은 규칙)를 실행 선택에서 읽어 쓴다. **점수는 그대로다.**
- **[FIX-71]** 최종 대조가 앞 반영이 새로 만든 오류 넷을 찾아 고쳤다 — 카드에 없는 `진단` 을 있다고 적은 것(경로 표시가 `mode` 를 읽지 않았다), 첫째 관문 실패 뒤 둘째까지 계산한다고 읽히는 서술, ②가 규칙의 방식으로 매겨진 회사가 한 곳도 없다는 사실 누락, 상장 안에서 트랙이 갈린다는 말 누락이다. 잔여 셋(`매출` 의 세 뜻 · 칸 수 조립 · 하드코딩)도 함께 닫았고 내부 코드 `G1-after` 를 이름으로 바꿨다. **점수는 그대로다.**
- **[FIX-72]** 3차 대조가 둘을 더 찾았다 — ⑥ `매출 성장` 이 신규 상장 트랙의 분기 대 전년 동기를 설명하지 못한 것과, 앞 라운드가 `cap_steps` 를 인라인 인덱싱으로 바꿔 값에 따라 렌더가 죽을 수 있던 것이다. 칸 수를 세는 표를 한 곳으로 모았고 첫째 관문의 `방향 완화` 도 설명에 넣었다. **점수는 그대로다.**
- **[FIX-73]** 결정 선택지 이름이 경고 문구에 영어로 실리던 마지막 잔재를 옮겨 그렸다(`paths_with_generation_gap_5` 18회 · `proposed_v15_boundaries` 3회). 뜻은 규칙 `decisions` 의 권고·요약·확정 모델에서 가져왔고 식별자는 결정 사전과 감사 기록에 대조용으로 남는다. 전수 조사에서 `G3/G4` 가 `런웨이/G4` 로 반쪽만 바뀌던 것도 함께 고쳤다(복합 단계 이름을 낱개 번호보다 먼저 치환한다). **`results.json` 은 손대지 않았고 점수도 그대로다.**
- **[FIX-74]** 사람 판단과 기계 계산의 경계를 사실대로 다시 그었다. 사다리·산식·조합표를 기계 계산처럼 적고 ①④⑧ 만 판단인 것처럼 갈라 놓았는데, `judgments.json` 의 `kind` 를 세어 보면 **①~⑤·⑦·⑧ 일곱이 전부 사람 판단에서 나온다.** 엔진이 무엇을 환산하는지는 그대로 적고 그 입력이 사람 판단이라는 사실을 앞에 세웠다. ⑨ 에 들어가는 사람 판단 입력을 판단 기록에서 읽어 나열했고, ⑥ 하나만 관측에서 나온다는 사실을 적었다. 색인의 방식·근거 설명도 같이 고쳤다. **점수는 그대로다.**

**점수·규칙·관측·판단은 그대로다.** `results_hash` 가 `4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b` 로 불변이고 14개사 총점도 같다. **영역 판정은 검토자의 것이므로 이 파일에서 바꾸지 않았다.**

## 판정

- **네 영역이 모두 pass 이고 체크리스트 fail 11건은 전부 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). `status: pass` 의 요건을 갖췄다.
- **마지막 새 발견(low)을 넘기지 않고 이번에 고쳤다.** 리뷰어 지적은 `bep_retreat` 가 미치는 범위를 문면이 실제보다 좁게 적는다는 것이었다 — 네 자리가 `손실률 밴드보다 앞선다` 로 **적자 맥락만** 서술하는데, `g1_pass = (not bep_retreat) and (margin is None or margin > 0)` 이라 실제로는 **영업흑자 회사의 G1 통과도 막는다.** 재현했다: microsoft(상장 · 측정 영업이익률 **+46.78%**)에 `bep_retreat` 만 `yes` 로 바꾸면 F9 가 **0 에서 -4 로** 떨어지고 경로에 `result: fail` 이 양수 마진과 함께 기록된다.
  - **고치는 쪽을 고른 이유** — 넘기면 리뷰어가 지적한 위험(`TEN-RA6-01` 이 흑자 경우를 빠뜨린 채 2026-11 에 판정된다)이 그대로 남는다. 반대로 고치는 비용은 문면 네 자리뿐이고 **코드를 손대지 않아 점수가 바뀔 수 없다.**
  - **고친 자리 넷** — `policies.f9.g1_bep_retreat_precedence.also_precedes_loss_band`(제목을 `G1 통과와 손실률 밴드 둘 다보다 앞선다` 로) · `decisions` C-06 `summary`(빌드 HTML 방법 표에 실린다) · `render_common.method_lines`(초안·HTML) · `TEN-RA6-01.also_covers_listed`(11월 재판정 범위에 흑자 경우를 넣었다). `calc_f9.py` 의 `영업적자 구간` 주석에도 흑자가 들어온다는 사실을 적었다.
  - **동작은 바꾸지 않았다.** 이 처리는 채점규칙 470행의 OR 조건 읽기와 어긋나지 않고 FIX-59 때부터 같다 — **새로 생긴 결함이 아니라 서술이 좁았던 것**이다. 근본 질문(전망이 측정된 실적을 덮어써도 되는가)은 `TEN-RA6-01`(open · 2026-11 · 비 Claude 재판정 확정)이 그대로 들고 있다.
  - **점수 불변을 두 겹으로 확인했다** — 14개사 총점이 그대로이고, `results.json` 의 `companies`·`ranking` 정렬 JSON 해시가 `f313060` 과 **동일**하다(`5ee4b01048acf647`). 바뀐 최상위 키는 `input_hashes`·`results_hash` 둘뿐이고 `warnings_count` 도 165 그대로다.
- **이월 두 건은 새로 할 일이 없다** — oracle F6 P1 경계 +3.87% 는 미결 `C-27` 의 표본으로, oracle 미인출 여신 null 을 0 으로 세는 것은 결정 `C-04` 의 설계대로로 각각 등록돼 있다(위 발견 사항).
- **9라운드 동안 점수를 바꾼 것은 일곱 자리뿐이다**(계획의 `규칙·자료 변경이 점수에 닿은 자리` 표). 나머지 반영은 전부 기록·서술이었고, 재무 계산 영역이 세 번 연속 잡은 것도 모두 문면이 코드보다 늦게 따라온 자리였다.
- results_hash `4a3f6c05b206ef81…` · draft_hash `7eddab49d6adf56f…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트**의 sha256 이다(`stages.sha256_file`). 승인 해시 대조는 `stages.current_hashes` 가 같은 규약으로 다시 계산해 비교한다.
- **`status: pass` 가 뜻하지 않는 것.** 체크리스트 Q01~Q23 을 이 파일에서 다시 돌린 것이 아니다 — 8차·9차 part 기록을 출처를 밝혀 옮겼다. 승계 판단 11건은 **긴장 등록과 재검토 시점만 기계로 확인**한 것이고, `이번 실행이 잣대를 바꾸지 않았다`는 조건은 리뷰어가 판정했다(AGENTS.md 71행).
