# rule-consistency — 규칙 일관성
검토자: codex · GPT-5 · 독립 세션 /root · 2026-09-15 15:09 KST (UTC+09:00).
results_hash: 5e8ce6fcf3b812a29ada6b51d89e822f5923da436e887f23431b75ebc709fe79
draft_hash: 931f5632affd4742cb35e46f9798598ef1e6d246be282bc3386da009b75f6490
결과: needs_fix
요약: F7 범위 조정, 비상장 F6의 런레이트 승격 차단, 실행 단위 결정 연결은 확인됐다. 그러나 채널 원칙·F5 동일 기준·중복 감점 근거·초안의 현재 판단 연결·입력 바이트 해시에 문제가 남는다(발견 RC-01~RC-07).

## 결정 반영 대조

아래 경로는 실행 트리 기준이다. `원규칙`은 `E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor/AI기업_채점규칙_v1.5.md`, `원채점표`는 같은 폴더의 `AI기업_채점표_v1.5.md`를 뜻한다. 판단 id는 `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json`의 항목을 가리킨다.

템플릿 frontmatter 두 해시가 지정값과 일치한다(reviews/ai-scorecard-2026-09-obsreg.md:9). 결과의 내장 해시와 정규 JSON 해시도 지정 results_hash와 일치하며, 초안의 원시 바이트 SHA-256도 지정 draft_hash와 일치한다(scripts/scorecard/schema.py:118, scripts/scorecard/engine.py:137). 단, 판단 파일의 원시 바이트 결속은 별도로 실패한다(RC-07, results.json:11).

| 결정 | rules status | run.json | 코드 분기 | 결과 반영 | 판정 |
|---|---|---|---|---|---|
| C-02 | resolved | 선택 없음 | calc_f6.py:270, calc_f6_params.py:349, calc_f9.py:188 | 비상장 F6는 자동 P2·보정, F9는 게이트. factor 내부 분리로 구현됨 | pass |
| C-03 | resolved, paths_with_generation_gap_5 | 같은 선택 | calc_qual.py:39, :52, :75. score 입력은 :40에서 승계 | 14개사 F2 모두 carried_score. 확정 선택 경고가 붙음. 현재 14개사의 세대 격차를 새로 판정한 결과는 아님 | pass. 초안 설명은 RC-06 |
| C-04 | pending | 선택 없음 | calc_f9.py:247. 정책 exclude로 분기. include_v15도 :252 산식은 같고 경고만 다름 | 현 실행은 현금+확정 미인출 여신. 등급 관측을 F9 점수 입력으로 사용하지 않음 | pass, 현 선택 범위. 대안은 계산에 반영되는 선택지가 아님 |
| C-05 | pending, 실행 단위 확정 | apply | calc_f9.py:158, :172 | spacex-xai F9 G1 -3 뒤 G3 -1 적용, 최종 -4. openai는 이미 하한이라 후속 게이트 생략 | pass |
| C-06 | pending, 경계 정책 확정 | proposed_v15_boundaries | calc_f9.py:125. BEP는 :120 정책값, 0은 :106·:233에서 대기 | spacex-xai -16.1951%가 -3 밴드. openai BEP 후퇴 -4와 문자열이 일치. 선택 하나로 영업손익/FCF 0 등의 묶음 전체를 해소하지 않음 | pass, 적용 경계 범위 |
| C-07 | pending | 선택 없음 | inputs.py:43, calc_f9.py:296 | incompatible_basis를 숫자로 사용하지 않음. anthropic G4 incompatible, openai G4 생략 | pass, ARR 대체 차단. anthropic은 G4 미완료인데도 F9 -2 ok인 예외를 calc_f9.py:202에서 명시함 |
| C-08 | pending | 선택 없음 | decision_choice 호출 없음. calc_qual.py:131이 A/H만 환산 | 이탈 가능성의 서로 다른 문언 해석이 F5 등급 입력에 남음 | fail, RC-03 |
| C-09 | pending | 선택 없음 | decision_choice 호출 없음. calc_qual.py:150이 score 승계를 허용 | anthropic·openai F7 -1은 축 입력 없는 승계. 나머지 12사는 matrix. 해당 예외를 경고로 표시 | pass, 승계 표시 계약. 축 사실은 확인 못 함 |
| C-11 | resolved, 사용자 확인 전 | block_carryover | decision_choice 호출 없음. calc_qual.py:153은 두 축만 읽음 | nonop_share를 F7 수치 입력으로 쓰는 경로 없음. 실행 목록의 등재는 선택 소비의 증명이 아님(engine.py:130) | pass, 현 차단 구조. allow_carryover 구현은 없음 |
| C-12 | pending, 실행 단위 확정 | p2_with_capped_promotion | calc_f6_params.py:397, :399 | 두 비상장사 calc.c12_choice 일치. arr_growth 입력 kind를 :454에서 검사. 두 회사 모두 승격 0칸, F6 -4 | pass |
| C-13 | resolved | reject_proxy | calc_f6.py:199은 bands 경로. :270 parameters 경로가 우선 | 현 실행에서 NTM proxy는 F6 입력 아님. 결정 등재와 실제 점수 영향이 구분돼야 함 | pass, 현 모드에서 영향 없음 |
| C-16 | pending, 실행 단위 확정 | downgrade | calc_f9.py:335. :325는 미수집·미분류를 먼저 차단 | alibaba G4 contracted_revenue의 not_disclosed_confirmed에 -1 적용, F9 -4 | pass |
| C-20 | pending, 실행 단위 확정 | defer_to_private_g2 | calc_f9.py:281, :283 | anthropic G1은 통과가 아닌 undetermined, 이후 G2 미공시 -2. openai는 BEP 실패 경로 | pass |
| C-01·C-10·C-14~C-15·C-17~C-19·C-21~C-22 | documented | 선택 없음 | 선택 소비를 요구하는 점수 분기 아님(rules v1.7.json decisions) | 과거 기록·기간·모집단·합산·유형 분기 설명. 이를 별도 실행 선택으로 보지 않음 | not_applicable, 결정 선택 소비 검사에 한함 |

`decision_choice` 호출 전수는 9곳이다. calc_qual.py:39(C-03), calc_f6.py:199(C-13), calc_f6_params.py:397(C-12), calc_f9.py:125(C-06), :158·:172(C-05), :247(C-04), :281(C-20), :335(C-16). helper 정의는 rules.py:357이며 규칙의 chosen을 자동 채택하지 않는다. C-08·C-09·C-11은 호출이 없고, C-04의 대안은 읽어도 산식을 바꾸지 않는다. 이 사실을 현재 run의 선택이 모두 실제 계산에 쓰였다는 주장으로 바꾸지 않았다(engine.py:130).

126개 현재 점수는 모두 factors.*.range 안이다(results.json companies[].factors, rules v1.7.json:37). F2 [2,5]는 0경로→2 사다리와 사용자 확정이 근거이고, F3 [1,5]는 원규칙:87의 0통과점→1 및 :91의 문 닫힘→5가 근거다. F3의 현재 실측 최저가 2라는 사실은 1점 칸을 삭제할 근거가 아니다(rules v1.7.json:65, 원규칙:87).

F6 P1/P2/P3 하한 합 -7, 트랙별 절단, 비상장 [-5,-2], F9 [-4,0], F5 허용 12조합의 0~5 및 F7 네 셀의 [-2,0]을 대조했다(rules v1.7.json factors·policies, schema.py:418·:470·:485·:659, rules.py:327). nvidia·oracle F7은 새 matrix 판단에서 -2이고, 두 판단은 carried가 아니라 new다(nvidia.F7.fix52, oracle.F7.fix52). C-11 scope의 “F7은 14개사 전부 carried”는 이 상태와 다르다(rules v1.7.json:1409).

메모리 복사본에 대한 validate_rules 검사에서 scope_separation 삭제, two_axes 삭제, banned_word 삭제, 두 site의 metric 동일화, site의 marketability 삭제, 예외 밖 환금성 삽입, F7 large|yes=-3을 각각 거부했다(schema.py:244·:585·:598·:610·:631). 상위 net_cash 전체 삭제는 통과했다(RC-01). 현재 판단 114개는 validate_judgments의 구조 검사를 통과하지만, 이 검사는 F5 A/H의 의미나 감점 속성 분리를 입증하지 않는다(schema.py validate_judgments, calc_qual.py:137).

### 14개사 동일 기준 대조

F1·F2·F3·F4·F5·F7·F8의 점수/판정/근거를 회사별로 읽었다. 아래 id 묶음의 접두 회사는 모두 같은 judgments.json을 가리키며, 산술은 현재 결과와 입력을 대조했을 뿐 계산 단계를 실행하지 않았다(calc_qual.py:16·:33·:107·:131·:144).

| 회사 | F5 A/H → F5 | 동일 A 기준을 적용한 대조 | 나머지 정성 factor 근거와 남는 문제 |
|---|---|---|---|
| alphabet | 2/-1 → 4 | 받은 투자 없이도 경쟁사 Meta의 TPU 편입 근거가 남음(alphabet.F5) | alphabet.F1·F2·F3·F4·F7·F8. 검색 자산의 F3 재탕을 제외. C-08의 이탈 기준은 별도 미확정 |
| amazon | 2/-1 → 4 | 경쟁사 OpenAI 등의 재판매권이 남음. Anthropic 투자를 빼도 A+2의 둘째 조항 근거 있음(amazon.F5) | amazon.F1·F2·F3·F4·F7·F8. 매대 자체를 모방불가로 불인정. Bedrock 이탈 예외는 RC-03 |
| meta | 1/-1 → 3 | 무료 개발자·멀티벤더 구매 제외, 광고주 상업 약속만 남김(meta.F5) | meta.F1·F2·F3·F4·F7·F8. 광고 회수 장치와 F3 상한은 구분됨. 광고주 이탈 예외는 RC-03 |
| microsoft | 2/-1 → 4 | F5 문언에는 OpenAI 지분 한 관계+Anthropic Azure 약정. 둘째 조항은 Foundry 매대와 자체 MAI를 함께 봐야 설명됨(microsoft.F5, amazon.F3, 원채점표:1032). 복수 지분이라는 이유만으로 +2라고 단정할 수 없음 | microsoft.F1·F2·F3·F4·F7·F8. Windows F3 재탕 제외. 같은 +2가 서는 대체 근거와 판단 문언을 연결할 필요 |
| tsmc | 2/-1 → 4 | “NVIDIA의 경쟁사까지 고객”과 “TSMC 자신의 경쟁사까지 편입”은 다른 주장. 새 2사 재판정과 같은 해석으로 +2가 유지되는지는 미확정(tsmc.F5, RC-04) | tsmc.F1·F2·F3·F4·F7·F8. 부품 상한 2, 모방불가 pass지만 통과점 2라 F3 3 |
| alibaba | 1/-1 → 3 | 무료 파생모델 제외, Apple 상업 계약 하나(alibaba.F5) | alibaba.F1·F2·F3·F4·F7·F8. 지정학을 F6/F9의 직접 감점 입력으로 사용하지 않음 |
| anthropic | 1/0 → 4 | 피투자 지분·컴퓨트 구매 제외, 남의 매대에 오른 유통은 한 방향이므로 A+1. 원규칙:214 A+2를 반증으로 보존(anthropic.F5.impl48) | anthropic.F1·F2·F3·F4·F7·F8.f8anth33. F1의 약한 소비자 채널로 최고점 제한은 RC-02. F7 축·Google 훈련 비중은 확인 못 함 |
| apple | 1/-1 → 3 | Gemini 구매 제외, App Store 수수료 분배만 동맹. 원규칙:221과 현재 판단이 일치(apple.F5) | apple.F1·F2·F3·F4·F7·F8. 디바이스 설치기반을 F3에서 다시 세지 않음. 법적 전선 수 대신 비용형을 사용 |
| nvidia | 1/-2 → 2 | 무료 CUDA/HF 개발자·미완료 인수 제외, Nemotron 공동개발만 A+1(nvidia.F5) | nvidia.F1·F2·F3·F4·F7.fix52·F8. 고객 자체 칩 위험의 F5/F8 중복 근거는 RC-05 |
| palantir | 1/-2 → 2 | NVIDIA·SAP·Accenture 상업 제휴, 적대는 정당성 표적(palantir.F5) | palantir.F1·F2·F3·F4·F7·F8. 단순 전환비용을 네트워크 폭증으로 보지 않음 |
| spacex-xai | 1/-1 → 3 | Tesla 관계사 제외, NASA·Space Force 등의 독립 계약(spacex-xai.F5) | spacex-xai.F1·F2·F3·F4·F7·F8. 비AI 사업을 F2에서 제외하고 F3 수익모델에서 구분 |
| tesla | 0/-1 → 2 | SpaceX 관계사를 A에 넣지 않음(tesla.F5) | tesla.F1·F2·F3·F4·F7·F8. Starlink 관계사 자산으로 모방불가 pass를 주지 않음 |
| oracle | 1/-1 → 3 | 파는 쪽 OpenAI 계약·NVIDIA·정부 등의 상업 관계. 구매자인 OpenAI의 Oracle 계약과 방향이 다름(oracle.F5, openai.F5.impl48) | oracle.F1·F2·F3·F4·F7.fix52·F8. 자기 DC 투자를 F7 환류와 분리, Stargate JV 투자는 환류로 분류 |
| openai | 1/-3 → 1 | 받은 투자·Oracle $300B 구매 제외. Stargate 지분 JV·Broadcom 공동개발·DoD는 남김. JV를 하나로 세는 단위는 별도 확인 못 함(openai.F5.impl48) | openai.F1·F2·F3·F4·F7·F8. H -3 승계와 A 재판정이 구분됨. F7 환류 축은 미복원 |

전 회사의 F3는 같은 pass=1/partial=0.5/fail=0 사다리와 모방불가 pass 게이트를 적용한다. 14개사 모두 door_closed=fail이고 F3는 2 또는 3이다(각 회사.F3, calc_qual.py:114, rules.py:311). F1·F2·F4·F8의 승계는 원검토일과 carried_from을 보존하며, 이것만으로 그 정성 판단이 같은 의미 기준을 만족한다고 보지 않았다(각 회사 해당 판단, inputs.py:97).

## 체크리스트

각 행은 위 14개사 대조 전체를 적용 범위로 삼는다. fail은 잘못된 점수의 정확한 대체값을 산출했다는 뜻이 아니라 해당 질문의 검증을 통과하지 못했다는 뜻이다.

| ID | 결과 | 근거(파일:행) · fail 이면 회사 |
|---|---|---|
| Q01 | fail | nvidia. 고객 40%+자체 칩 이탈을 F5 H -2와 F8 -3의 근거에 함께 사용하며 속성 분리를 설명하지 않음(nvidia.F5, nvidia.F8, judgments.json:1792·:1902). alibaba 지정학과 F6/F9, F9 미공시 중복 방지는 분리됨(calc_f9.py:202). RC-05 |
| Q02 | fail | anthropic의 F1 최고점 제한이 다른 채널의 규모에 의존(judgments.json:1227). tsmc의 F5 경쟁사 기준 주체 미확정(:918). net_cash 정의 삭제를 스키마가 허용(schema.py:523). meta 초안 F2는 폐기한 최고점 지표 유지(draft:218). RC-01·02·04·06 |
| Q03 | fail | tsmc·anthropic·openai의 A+2 해석 범위 일치가 미확정(judgments.json:918·:1328·:2938). amazon·meta·nvidia의 이탈 가능성에 다른 예외 사용(원규칙:239·:275·:277·:278). 다른 11개사를 포함한 전체 대조는 위 표. RC-03·04 |
| Q07 | pass | 전 14개사 F3. amazon·apple 모방불가 fail, “안 만들었다” 자체를 pass로 주지 않음(amazon.F3, apple.F3, 원규칙:52, calc_qual.py:119) |
| Q08 | pass | 전 14개사 F5 H. apple -1은 전선 수가 아닌 비용형, nvidia -2는 고객 경쟁화, palantir -2는 정당성, openai -3은 복수 구조형+파트너 긴장(각 회사.F5, 원규칙:203). 중복 속성 여부는 Q01/Q21에서 fail로 분리 |
| Q12 | pass | 전 14개사 F3. tsmc를 제외한 imitation은 완전 pass가 아니며, alibaba·spacex-xai 2.5통과점도 상한 3. 계산 사다리에 핵심 게이트 있음(각 회사.F3, rules.py:317) |
| Q13 | pass | 전 14개사 F3. alibaba의 회수장치 부재와 meta 광고 회수를 명시. 무료 배포만으로 imitation 완전 pass나 F3 4를 부여하지 않음(alibaba.F3, meta.F3, 원규칙:70, rules.py:317). partial의 타당성까지 새 실측으로 입증한 것은 아님 |
| Q15 | pass | 전 14개사 F5. meta 무료 개발자·alibaba 파생모델·nvidia 무료 개발자 제외. apple은 개인 사용자가 아닌 개발자 수수료 관계(각 회사.F5, 원규칙:198·:298) |
| Q16 | fail | anthropic. 업무를 주채널로 정의하고도 개인 사용자 수 열세로 5점 불가를 선언(judgments.json:1224·:1227). “얕은 채널이 깊은 채널을 깎지 않는다”와 불일치(원규칙:400, design-guideline.md 4.2). RC-02 |
| Q17 | pass | 전 14개사 F2. amazon 두 경로 4, nvidia·tsmc 성능 경로 5, alibaba 성능/적응 4, oracle 통과 0으로 2. 표준 부재만으로 일괄 감점하는 코드 없음(각 회사.F2, calc_qual.py:48·:91). 세대 격차 재판정 자체는 확인 못 함 |
| Q18 | pass | 전 14개사 F5. tesla A=0, spacex-xai는 Tesla를 명시적으로 제외. 관계사 조달품도 tesla F3 자체 자산에서 제외(tesla.F5, spacex-xai.F5, tesla.F3, 원규칙:199) |
| Q19 | pass | 전 14개사 F5의 받은 투자 직결 여부. anthropic·openai의 새 A는 피투자 관계를 명시적으로 제외(judgments.json:1325·:2935). 다른 12사의 동맹 근거는 위 표이며, 투자를 받은 사실만으로 +2라고 하지 않음. 특히 tsmc +2의 다른 기준 문제는 Q02/Q03 fail로 남김 |
| Q20 | fail | amazon·meta·nvidia·anthropic·openai. 단순 구매의 제외는 적용되지만 별표 H 이탈 조건의 허용/제외 기준이 통일되지 않음(원규칙:239·:273·:275·:276·:277·:278, rules v1.7.json:1362). A/H만 저장·환산하는 엔진이 이를 해결하지 않음(calc_qual.py:137). RC-03 |
| Q21 | fail | nvidia. 같은 고객 경쟁화 속성이 두 감점 근거에 중복돼 있음(judgments.json:1792·:1902). anthropic의 연동이익과 외부 컴퓨트 의존, apple의 개발자 수수료와 조달은 별개 속성으로 구분됨(anthropic.F5.impl48, anthropic.F8.f8anth33, apple.F5). RC-05 |
| Q22 | pass | 전 14개사 F7. nonop_share는 F6 P4 재계산 입력이고 F7 matrix는 두 축만 읽음(calc_f6_params.py:50, calc_qual.py:153). alphabet 평가익은 명시적으로 제외, amazon·nvidia는 고객 출처 방증으로만 표기(각 회사.F7). C-11의 allow 선택은 구현되지 않았지만 현 실행에는 차단 선택이 기록됨 |

## 발견 사항

- [severity: medium] RC-01 · scripts/scorecard/schema.py:523 — 상위 net_cash 블록 삭제로 범위 구분 검사를 우회한다. 메모리에서 `x=deepcopy(rules); x['policies']['f6'].pop('net_cash'); validate_rules(x)`가 통과했다. FIX-52는 working_definition 내부 세 블록 삭제를 막지만, 호출 자체가 `if net_cash` 아래다(:524). P2는 계속 net_cash 지표를 선언하고, 계산기는 정의가 없으면 정의 설명·작업 정의 경고만 생략한다(calc_f6_params.py:298). 현 파일에는 정의가 있으므로 현재 점수 오류라고 단정하지 않는다.
- [severity: high] RC-02 · judgments.json:1227, anthropic.F1 — 업무를 가장 강한 채널로 명시하면서 개인 사용자 수가 OpenAI보다 적다는 이유로 5점 자격을 제한한다. 원규칙:400 및 design-guideline.md 4.2의 가장 강한 채널 원칙에 어긋난다. 4가 옳은지 5가 옳은지는 별도 판단이지만, 현재 제한 근거는 교체 또는 재검토가 필요하다.
- [severity: high] RC-03 · rules v1.7.json:1356, 원규칙:239 — C-08이 현재 F5 입력의 동일 기준 문제에 계속 닿는다. 본문은 상대가 떠날 수 있으면 동맹 제외인데, NVIDIA 행(:275)은 제외, OpenAI(:276)·Bedrock(:277)·광고주(:278)는 떠날 수 있어도 가점한다. 새 OpenAI 판정은 Oracle 구매를 제거하고 새 Anthropic 판정은 지분 투자를 제거했지만, 어떤 이탈 기준으로 남은 제휴를 허용하는지는 전체 기업에 통일하지 않았다(judgments.json:1326·:2937). `decision_choice` 미호출이 의미상의 무영향을 보장하지 않는다(calc_qual.py:137).
- [severity: medium] RC-04 · judgments.json:918, tsmc.F5 — 새 2사 판정은 A+2 둘째 조항을 “경쟁사까지 내 플랫폼에 편입”으로 엄격히 읽지만(:1328·:2939), TSMC 승계 근거는 NVIDIA의 경쟁사 편입이다. TSMC 자신의 경쟁사인 Intel/Samsung 편입이나 복수 지분 동맹을 이 판단은 제시하지 않는다. 원규칙:218은 바로 그 근거로 TSMC +2를 주므로, 기준표(:192)와 예시표를 어느 의미로 통일할지 미확정이다. “나머지 12개사는 같은 잣대에서도 결과 불변”을 이 상태로 확정할 수 없다. +2가 틀렸다고 수치 정정하지 않고, 경쟁사의 주체·편입 범위 정의와 소급 대조를 요구한다.
- [severity: medium] RC-05 · judgments.json:1792·:1902, nvidia.F5/F8 — 주요 고객 40%가 자체 칩으로 이탈한다는 같은 속성이 F5 H -2와 F8 -3의 판정 근거에 반복된다. 원규칙:262의 금지선은 같은 관계가 아니라 같은 속성이며, 다른 이유를 덧붙이는 것만으로 분리가 입증되지는 않는다. F5는 구조형 적대, F8은 독립적인 집중/대체 불가/공급 약정 위험으로 분리해 설명해야 한다. -3에서 그 속성이 실제로 몇 점을 만들었는지는 현재 수동 판단에 배분이 없어 확인 못 함이다.
- [severity: high] RC-06 · scripts/scorecard/render_md.py:308, drafts/ai-scorecard-2026-09-obsreg.md:218·:423·:919 — 초안의 근거 불릿은 현재 judgments가 아니라 baseline evidence를 최대 6개 출력한다(:315). Meta의 폐기된 “AA 종합 1위가 5점 기준”은 현재 판단에 superseded로 처리됐는데도 초안에는 활성 문장처럼 남는다(meta.F2). Anthropic/OpenAI 새 F5의 지분·조달 제외 및 A+1 결정 근거(:1323·:2933)는 초안에 실리지 않고, 원문 판단 미적용이라는 캡션 아래 과거 동맹 서술만 나온다. 특히 OpenAI는 제외한 받은 투자를 다시 지분 동맹으로 읽을 수 있는 원문만 보여준다(draft:925). 과거 기록 보존과 현재 점수의 정성 판단 설명을 함께 제공해야 한다. 원규칙 Apple :221은 현재 apple.F5에서 App Store와 조달을 구분해 유지하지만 OpenAI :224·:276은 새 판단과 불일치하므로, 원문 예시가 현재 결과를 재현한다고 취급할 수 없다.
- [severity: medium] RC-07 · results.json:11, scripts/scorecard/schema.py:130 — 현재 judgments.json 바이트 해시는 `57a35c9086e6edaf664eb4b17fd3c31a6ba0e80e7ff71dffb5a8f9969b2a3d84`, 결과의 입력 해시는 `a485bfd5db0ff07581730b1c6b7926b68aa6d6120485c730347278045a79e2a0`이다. CRLF를 LF로 정규화하면 후자와 정확히 일치하므로 내용 차이가 아니라 줄끝 차이다. 그러나 엔진의 입력 결속은 정규화하지 않은 원시 바이트다(engine.py:65). 나머지 run/observations/sources/rules 입력 해시와 초안 해시는 원시 바이트 그대로 일치했다(results.json:8, reviews 템플릿:9). HASH-EOL로 이미 기록된 문제지만 이 리뷰 트리의 결정론적 바이트 재현은 실패한다(docs/scorecard/open-items.md:85). 이번 검토는 이를 숨기지 않으며 파일은 수정하지 않았다.

## 확인 못 한 것

- anthropic·openai F7의 실제 own_money_returns 축과 동일 matrix에 넣을 최종 점수. score 승계 입력에는 축이 없고 C-09가 미복원을 명시한다(anthropic.F7, openai.F7, rules v1.7.json:1372). spacex-xai.F7의 Startup Fund 서술만으로 OpenAI의 축을 확정하지 않았다.
- anthropic F8의 Google 몫 훈련/서빙 구분과 -4 재판정 여부. 현 판단이 1차 확인 범위와 미공시를 구분하고 있으나 그 공백을 메우는 자료는 판단에 없다(anthropic.F8.f8anth33).
- A+2의 경쟁사 주체·지분 동맹 집계 단위를 통일했을 때 나머지 12사와 OpenAI Stargate JV의 정확한 점수 영향. JV 법인 하나를 동맹 하나로 셀지 여러 독립 공동투자 관계로 셀지 원규칙:192가 정하지 않는다(openai.F5.impl48, tsmc.F5, RC-04). 이미 있는 점수를 정답으로 삼아 뜻을 확정하지 않았다.
- nvidia F8 -3이 F5에서 센 고객 경쟁화 속성을 제외해도 독립 근거만으로 유지되는지. 수동 judgment는 근거별 배점이나 반사실 판정을 제공하지 않는다(nvidia.F8, calc_qual.py:21). 따라서 중복 근거 발견과 정확한 중복 감점 폭을 구분했다.
- 전체 계산 경로의 실행 재현과 신규 F2 세대 격차 판정. 계산 단계와 compute 함수는 실행하지 않았고 코드·입력·저장 결과만 대조했다(engine.py:104). 원문도 세대 격차가 몇 축에서 성립해야 하는지 정하지 않으므로 14개사 F2 불변을 독립 실측으로 재입증하지 않았다(rules v1.7.json:1233).
