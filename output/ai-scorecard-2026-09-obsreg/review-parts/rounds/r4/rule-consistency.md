# rule-consistency — 규칙 일관성
검토자: Codex(GPT-5 계열), 독립 /root 세션, 2026-09-15 18:33 KST, 기준 커밋 ab5a053.
결과: needs_fix
요약: 현재 점수는 전부 범위 안이고 총점도 제시된 값과 일치한다(results.json:27, results.json:4180). 그러나 F3 partial 자격·TSMC 가속도·OpenAI 주채널·SpaceX 적대 판정에서 미등록 승계 문제를 발견해 승계 예외를 적용할 수 없다(judgments.json:467, judgments.json:856, judgments.json:1297, judgments.json:2224, judgments.json:2279, judgments.json:2847, AGENTS.md:71).

이 문서의 run.json·observations.json·judgments.json·results.json은 모두 scorecard/runs/ai-scorecard-2026-09-obsreg/ 아래 파일이다. v1.7.json은 scorecard/rules/v1.7.json이다. calc_qual.py·calc_f6.py·calc_f6_params.py·calc_f9.py·rules.py·schema.py·inputs.py·engine.py는 scripts/scorecard/ 아래 파일이다. AI기업_채점규칙_v1.5.md·AI기업_채점표_v1.5.md·AI기업_채점표_HANDOVER.md·AI기업_채점표_v1.5.html은 E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor/ 아래 원본이다.

검토 대상 결과 해시는 66493509c00acf01b3e6a4db20c825bc1dec6afe26393f68057b72924118807d이다(results.json:4301). 입력 해시 5개를 현재 파일 바이트와 대조해 모두 일치했고, 복사된 draft의 SHA-256도 템플릿의 9dcaebc89826a7deb107b7e227ee0f80af4b7ebe387b8882731b380d0f18c607과 일치했다(results.json:8, reviews/ai-scorecard-2026-09-obsreg.md:10). 아래 판정은 저장된 결과·입력·코드의 읽기 대조이며, 계산·승인·빌드 단계는 실행하지 않았다(scripts/scorecard/calc_qual.py:113, scripts/scorecard/calc_f6.py:267, scripts/scorecard/calc_f9.py:62).

## 결정 반영 대조

| 결정 | rules status | run.json | 코드 분기 | 결과 반영 | 판정 |
|---|---|---|---|---|---|
| C-02 | resolved(v1.7.json:1260) | 선택 항목 없음(run.json:30) | 정성 환산·F6·F9 분리(calc_qual.py:113, calc_f6.py:267, calc_f9.py:62) | 정성 승계와 computed가 구분됨(results.json:38, results.json:117, results.json:268) | pass |
| C-03 | resolved, paths_with_generation_gap_5(v1.7.json:1266) | 같은 선택(run.json:66) | decision_choice 조회 후 score 승계와 paths 환산 분리(calc_qual.py:39, calc_qual.py:45, calc_qual.py:97) | 14사 F2는 승계. 선택은 경고에 반영되고 경로 재판정·점수 변경은 하지 않음(results.json:51, results.json:3925) | pass |
| C-04 | pending(v1.7.json:1330) | 선택 없음(run.json:30) | 정책 exclude로 fallback. include_v15는 경고만 바꿈. G1 실패 진단에서는 조회도 없음(calc_f9.py:172, calc_f9.py:261, calc_f9.py:266) | 현재 G3는 현금+확정 여신. 등급 추정치를 더하는 산술은 없음(results.json:583, results.json:3233, results.json:3849) | pass |
| C-05 | pending(v1.7.json:1363) | apply(run.json:31) | 조회 2곳. 진단 보류 처리와 diag_score 적용(calc_f9.py:169, calc_f9.py:186) | SpaceX G1-after applied=true, -3. 현재 G3·G4 step은 0이라 diagnose_only와 숫자 차이는 없음(results.json:3233, results.json:3253) | pass |
| C-06 | pending. 손실률 밴드만 confirmed(v1.7.json:1377, v1.7.json:1102) | proposed_v15_boundaries(run.json:38) | 손실률 -10%·-30% 하한 포함. BEP는 선택 조회보다 앞선 별도 분기. 영업손익·FCF 0은 계속 미결(calc_f9.py:31, calc_f9.py:117, calc_f9.py:130, calc_f9.py:136, calc_f9.py:247) | SpaceX -16.1951%는 G1 -3. OpenAI BEP는 정책 -4. 현재 0 입력 경로는 없음(results.json:3223, results.json:4127) | pass |
| C-07 | pending(v1.7.json:1390) | 선택 없음(run.json:30) | decision_choice 호출 없음. unusable status와 coverage_comparable 분기가 차단(inputs.py:43, calc_f9.py:315) | Anthropic G4 incompatible, OpenAI는 G1 하한에서 생략. ARR/연환산 약정 비율로 G4를 채점하지 않음(results.json:2081, results.json:4127) | pass |
| C-08 | pending(v1.7.json:1425) | 선택 없음(run.json:30) | 호출 없음. F5는 입력 A/H만 합산(calc_qual.py:143) | 이탈 조건 모순은 정성 판단에 남음. 승계 Alphabet·Amazon·Meta·NVIDIA의 TEN-RC-03은 예외 적용 대상(v1.7.json:1751, judgments.json:102, judgments.json:310, judgments.json:515, judgments.json:1816) | fail |
| C-09 | pending(v1.7.json:1435) | 선택 없음(run.json:30) | 호출 없음. score 승계 우회와 matrix 경로 분리(calc_qual.py:156, calc_qual.py:164) | Anthropic·OpenAI -1은 두 축 산출이 아님. TEN-RC3-01로 등록. 변경된 large 칸은 두 회사가 필요로 하는 small 칸의 잣대를 바꾸지 않음(v1.7.json:168, v1.7.json:1880, results.json:2027, results.json:4095) | fail |
| C-11 | resolved, 사용자 확인 전(v1.7.json:1458, v1.7.json:1472) | block_carryover(run.json:73) | 호출 없음. F7 산술은 두 축만 읽음(calc_qual.py:159) | 산술 이월 경로는 원래 없음. 문언은 P4 전용인데 F7 근거에 고객사 영업외 비중 방증이 남아 있음(v1.7.json:619, judgments.json:349, judgments.json:1871) | fail |
| C-12 | pending. 정책에는 확정 기록(v1.7.json:1492, v1.7.json:743) | p2_with_capped_promotion(run.json:52) | 실제 조회. 다른 선택은 산출하지 않고 대기. kind 제한·require_all·상하한 적용(calc_f6_params.py:408, calc_f6_params.py:465, calc_f6_params.py:480) | 두 회사 P2 -4. run_rate 성장 조건 불인정으로 승격 0. Anthropic도 -4(results.json:1945, results.json:1972, results.json:4009, results.json:4042) | pass |
| C-13 | resolved, reject_proxy(v1.7.json:1506) | 같은 선택(run.json:80) | 조회는 bands 경로에만 있음. parameters는 앞서 반환(calc_f6.py:199, calc_f6.py:270) | 현재 F6에 NTM proxy를 쓰지 않음. decisions_applied에 적혀 있어도 현재 소비 증명이 아님(results.json:23, results.json:1307, results.json:1597, engine.py:130) | pass |
| C-16 | pending(v1.7.json:1552) | downgrade(run.json:45) | comparable=yes 이후 확인된 미공시만 조회·한 칸 하향(calc_f9.py:320, calc_f9.py:343, calc_f9.py:353) | Alibaba 계약수입 확인된 미공시로 G4 -1, F9 -3. 미수집·비교 불가를 같은 정책으로 깎지 않음(results.json:1750, observations.json:4096) | pass |
| C-20 | pending. 정책에는 확정 기록(v1.7.json:1584, v1.7.json:1117) | defer_to_private_g2(run.json:59) | 실제 조회. 비상장·확인된 TTM 영업손익 미공시만 G2로 보류 이송(calc_f9.py:286, calc_f9.py:299) | Anthropic G1 undetermined→G2 -2. OpenAI는 BEP 하한이 우선(results.json:2052, results.json:4127) | pass |

decision_choice 호출은 AST로 전수 확인한 9곳·8개 ID이다. C-03(calc_qual.py:39), C-04(calc_f9.py:261), C-05(calc_f9.py:169, calc_f9.py:186), C-06(calc_f9.py:136), C-12(calc_f6_params.py:408), C-13(calc_f6.py:199), C-16(calc_f9.py:353), C-20(calc_f9.py:299). C-08·C-09·C-11은 호출되지 않으며, results.decisions_applied는 run의 선택 목록을 복사한다(engine.py:130). C-01·C-10·C-14·C-15·C-17·C-18·C-19·C-21·C-22는 documented 항목이며 실행 선택 목록에 없다(v1.7.json:1254, v1.7.json:1452, v1.7.json:1540, v1.7.json:1566, v1.7.json:1599, run.json:30).

범위 대조 결과 14사×9 factor의 126개 점수에 범위 밖 값이 없다(v1.7.json:38, results.json:27, results.json:3901). F2 [2,5]의 직접 근거는 0경로→2인 확정 매핑이며, 3경로·세대 격차 없음은 여전히 대기다(v1.7.json:48, calc_qual.py:106). F3 [1,5]는 0통과점→1인 원문 사다리와 일치하며, 현재 최저 2라는 표본 사실이 1점 칸을 불가능하게 만들지는 않는다(v1.7.json:68, AI기업_채점규칙_v1.5.md:87, rules.py:311). F5 허용 조합의 끝값은 3+0-3=0과 3+2+0=5다(v1.7.json:124, rules.py:327). F6는 P1/P2/P3 하한 합 -7에 P4 한 칸을 적용한 후 트랙 하한으로 절단하고, 비상장은 [-5,-2]로 제한한다(v1.7.json:147, v1.7.json:698, calc_f6_params.py:344, calc_f6_params.py:491). F7 매트릭스는 현재 0/-1/-2/-2이고, F9 밴드·정책 레벨은 [-4,0]이며 추가 감점은 하한 -4로 절단된다(v1.7.json:168, v1.7.json:1087, calc_f9.py:27, schema.py:749).

F5의 엄격한 A 기준을 14사에 대조한 결과는 다음과 같다. 이 표에서 유지는 기존 점수와 같다는 뜻이며, 미결 이탈 조건을 새로 확정했다는 뜻은 아니다(AI기업_채점규칙_v1.5.md:192, v1.7.json:1764).

| 회사 | 현재 A / F5 | 엄격한 A 기준 대조 · 근거 |
|---|---|---|
| alphabet | +2 / 4 | 경쟁사 Meta를 자기 TPU에 편입한 둘째 조항. Meta 쪽 조달과 Google 쪽 판매 방향을 구분. 이탈 조건은 TEN-RC-03(judgments.json:102, AI기업_채점규칙_v1.5.md:215, AI기업_채점규칙_v1.5.md:286). |
| amazon | +2 / 4 | 자기 Bedrock에 경쟁사 모델을 편입한 둘째 조항. 이탈 조건은 TEN-RC-03(judgments.json:310, AI기업_채점표_v1.5.md:135, AI기업_채점규칙_v1.5.md:216). |
| microsoft | +2 / 4 | 카드의 OpenAI 27% 한 건만으로 복수 지분이라고 판단하지 않았다. 원문 별표 G 214행·H 288행이 MS→Anthropic 투자+유통도 명시하므로 MS 관점의 능동 지분 동맹 둘을 확인할 수 있다(judgments.json:711, AI기업_채점규칙_v1.5.md:214, AI기업_채점규칙_v1.5.md:288). |
| tsmc | +1 / 3 | 현재 새 판단 strict54. 고객은 NVIDIA의 경쟁사이며 TSMC의 경쟁사가 아니다. 고객 지분 투자도 없으므로 +2 두 조항 모두 불성립. 고객 동맹 자체는 인정(judgments.json:908, AI기업_채점표_v1.5.md:243, AI기업_채점규칙_v1.5.md:218, AI기업_채점규칙_v1.5.md:289). |
| anthropic | +1 / 4 | 받은 투자·구매 컴퓨트로 +2를 만들지 않고 남의 매대에 오른 유통을 +1로 분류. 받은 지분이 실제로 없어졌다는 뜻은 아님(judgments.json:1346, AI기업_채점규칙_v1.5.md:188, AI기업_채점규칙_v1.5.md:288). |
| openai | +1 / 1 | 받은 투자·Oracle $300B 조달 제외. Stargate는 합작 법인 하나로 집계하고 공동개발·정부 계약을 남김. 합작 참여사별 집계의 미규정은 TEN-RC-03에 명시(judgments.json:2961, AI기업_채점표_v1.5.md:759, v1.7.json:1808). |
| meta | +1 / 3 | 광고주 상업 약속. 무료 개발자·멀티벤더 조달 제외. 이탈 조건은 TEN-RC-03(judgments.json:515, AI기업_채점규칙_v1.5.md:219). |
| alibaba | +1 / 3 | 무료 파생모델 제외, Apple 독립 상업 계약 한 방향(judgments.json:1139, AI기업_채점규칙_v1.5.md:220). |
| apple | +1 / 3 | App Store 수수료 분배. Gemini 매입 제외. 원문 G의 Apple 행은 현재 입력과 일치(judgments.json:1622, AI기업_채점규칙_v1.5.md:221, AI기업_채점규칙_v1.5.md:293). |
| nvidia | +1 / 2 | Nemotron 공동개발. 무료 CUDA/HF 사용자·미완료 인수 제외. 투자처를 복수 지분 동맹으로 가점하는 해석은 기존 이탈 제외 기준과 TEN-RC-03에 걸림(judgments.json:1816, AI기업_채점규칙_v1.5.md:226, AI기업_채점규칙_v1.5.md:275). |
| palantir | +1 / 2 | 독립 상업 파트너는 있으나 복수 지분·자기 플랫폼 경쟁사 편입 근거는 없음(judgments.json:2074, AI기업_채점규칙_v1.5.md:223). |
| oracle | +1 / 3 | 판매자 관점의 고객·정부 클라우드 상업 관계. OpenAI 구매자 관점의 $300B 조달과 구분(judgments.json:2704, AI기업_채점규칙_v1.5.md:227, AI기업_채점규칙_v1.5.md:233). |
| spacex-xai | +1 / 3 | NASA·Space Force·DoD. Tesla 관계사 제외. A는 유지되나 H의 수 비교 논리는 RC4-03(judgments.json:2279, AI기업_채점규칙_v1.5.md:222). |
| tesla | 0 / 2 | SpaceX만으로 독립 아군을 만들지 않음. 관계사 언급이 있어도 A=0(judgments.json:2503, AI기업_채점규칙_v1.5.md:225). |

따라서 anthropic·openai에 적용한 +2 문언 읽기는 나머지 12사에도 대조됐고, 원문 +2였던 TSMC는 실제로 +1로 바뀌었다. 나머지 11사의 현재 A를 바꿔야 할 추가 근거는 이 대조에서 확인하지 못했다(judgments.json:908, judgments.json:1346, judgments.json:2961, AI기업_채점규칙_v1.5.md:212). 별표 H의 239행과 275~278행의 모순은 TEN-RC-03으로 보존돼 있으며, OpenAI의 G/H A+2 행은 현재 새 판단의 반대 증거로 남아 있다(v1.7.json:1764, judgments.json:2984). Apple의 G 행은 Gemini 조달을 이미 제외하므로 이번 수정 대상의 OpenAI 행과 상태가 다르다(AI기업_채점규칙_v1.5.md:221, AI기업_채점규칙_v1.5.md:224, AI기업_채점표_v1.5.html:858, AI기업_채점표_v1.5.html:945).

메모리 deepcopy 변조로 확인한 스키마 동작은 다음과 같다. 현재 규칙·360개 관측·114개 판단은 schema 검사를 통과했다(schema.py:229, schema.py:771, schema.py:896). 아래 검사에서는 디스크의 입력을 쓰지 않았다(schema.py:667, schema.py:734).

| 변조 | 실제 결과 | 근거 |
|---|---|---|
| scope_separation 삭제 | 거부 | schema.py:667 |
| two_axes 삭제 | 거부 | schema.py:670 |
| banned_word 삭제 | 거부 | schema.py:673 |
| 전역 immediacy 정의 삭제 | 거부 | schema.py:676 |
| 자리별 marketability 답 삭제 | 거부 | schema.py:694 |
| 두 자리 모두 metric=cash | 거부 | schema.py:699 |
| sites[1].counts에 환금성 삽입 | 거부 | schema.py:734 |
| sites[0].counts에 환금성 삽입 | 허용. 원문 인용 예외와 일치 | v1.7.json:985, schema.py:733 |
| 두 자리 지표를 arr/nonop_share로 교체 | 허용. 지정 지표 cash/net_cash까지 강제하지는 않음 | schema.py:688, schema.py:699 |
| anthropic.arr.v15의 kind를 run_rate→actual로 변경 | 허용. 의미 검증은 스키마가 담당하지 않음 | observations.json:3758, schema.py:806, docs/scorecard/open-items.md:87 |

동일 이름·다른 소비 범위는 다음과 같이 대조했다(v1.7.json:619, v1.7.json:845, v1.7.json:992, calc_f9.py:338).

| 이름 | 현재 정의·실제 소비 | 판정 |
|---|---|---|
| cash / net_cash | G3는 즉시 사용 가능 현금+확정 미인출 여신, P2는 시장성 금융자산−차입금−리스부채. 소비 코드도 각각 cash와 net_cash를 조회한다(v1.7.json:995, v1.7.json:1006, calc_f9.py:254, calc_f6_params.py:216). | 구분됨. 시장성/즉시성 자리의 지정 지표까지 강제되지 않는 한계는 메모리 변조 표에 남김(schema.py:688). |
| nonop_share의 F6 / F7 | F6 P4는 (세전이익−영업이익)/세전이익을 원자료에서 계산하고 저장된 완제품은 대조용으로만 읽음. 음수 세전이익·필수 원자료 결측이면 값을 만들지 않는다. F7 matrix는 해당 지표를 읽지 않음(calc_f6_params.py:50, calc_f6_params.py:76, calc_f6_params.py:84, calc_f6_params.py:95, calc_qual.py:159). | 산술 분리됨. 고객사 평가익 방증과 C-11 근거 이월 금지 문언의 충돌은 RC4-06(v1.7.json:1474, v1.7.json:1244). |
| not_disclosed / missing_type | status는 값의 사용 가능성을, missing_type은 미수집·확인된 미공시·해당 없음·판별 불가를 나눈다. 스키마는 missing_type이 붙으면 value=null을 강제하고, C-16은 comparable=yes 및 확인된 미공시만 받음. C-20은 비상장 영업손익의 확인된 미공시를 별도로 받음(inputs.py:43, schema.py:794, calc_f6_params.py:226, calc_f9.py:320, calc_f9.py:343, calc_f9.py:303). | status 하나로 C-16 감점을 적용하지 않음. 라벨의 사실성은 스키마 통과만으로 확정되지 않음(schema.py:795, observations.json:4127). |
| arr / run_rate | 현재 private arr 관측은 run_rate. 성장 보정은 actual만 허용하고, 자본효율은 사용자 결정 범위에 따라 run_rate를 계속 허용. P2 채점은 arr 배수 대신 ps_ratio를 읽음. G4는 숫자를 조회한 뒤 비교 가능성에서 거부하므로 ARR 대체 비율을 산출하지 않음(v1.7.json:840, v1.7.json:845, calc_f6_params.py:368, calc_f6_params.py:391, calc_f6_params.py:465, calc_f9.py:309, calc_f9.py:315). | 성장 조건의 변경된 잣대는 Anthropic·OpenAI 둘 다 적용됨. 자본효율에 같은 kind 금지를 조용히 확장하지 않았음(results.json:1972, results.json:4042, v1.7.json:845). |

## 체크리스트

| ID | 결과 | 근거(파일:행) · fail 이면 회사 |
|---|---|---|
| Q01 | fail | nvidia F5/F8의 고객 자체칩 이탈 반복은 TEN-RC-05, tesla F5/F8의 NHTSA 반복은 TEN-RC3-04. 두 쌍 모두 승계·해당 위험 잣대 불변·2026-11 재검토 등록으로 비차단. Alibaba 지정학은 F8로 분리됐고 G2/G4 미공시의 중복 처리도 분리됨(judgments.json:1816, judgments.json:1932, judgments.json:2503, judgments.json:2555, judgments.json:1139, v1.7.json:1811, v1.7.json:1928, calc_f9.py:217). |
| Q02 | fail | 새 발견은 meta·anthropic·spacex-xai F3 partial 자격(RC4-01), tsmc F3의 가이던스 가속도(RC4-04), openai F1의 거래 지표를 소비자 락인 한정에 사용(RC4-02). 등록된 승계 fail은 anthropic F1(TEN-RC-02), palantir·oracle F1(TEN-RC3-03), anthropic·openai F7(TEN-RC3-01), alibaba F3(TEN-RC3-05), microsoft·spacex-xai·tesla·oracle F3 가속도(TEN-RB-Q10)이다(judgments.json:467, judgments.json:856, judgments.json:1297, judgments.json:2224, judgments.json:2847, v1.7.json:1732, v1.7.json:1830, v1.7.json:1880, v1.7.json:1903, v1.7.json:1952). |
| Q03 | fail | 新 A 엄격 읽기는 14사 대조됐고 TSMC도 수정됨. 남은 전사 차이는 F3의 복제 가능 자산 partial 대 fail(RC4-01)·가이던스 대 실측(RC4-04), OpenAI/Anthropic의 주채널 대 보조채널 제한(RC4-02·TEN-RC-02), Palantir/Oracle의 업무 전환비용(TEN-RC3-03), C-08 이탈 조건(TEN-RC-03), 가속도 증거(TEN-RB-Q10), 복원되지 않은 F7 축(TEN-RC3-01). 회사별 구분은 아래 전사 표(judgments.json:52, judgments.json:257, judgments.json:467, judgments.json:856, judgments.json:908, judgments.json:1297, judgments.json:1985, judgments.json:2608, judgments.json:2847, v1.7.json:1751, AGENTS.md:71). |
| Q07 | pass | Amazon은 모델 미제작 자체를 배제하고 imitation=fail. Apple도 미움직임·지연을 가점하지 않고 fail. 나머지 12사 F3에도 미제작 자체를 가점한 근거는 확인하지 못함(judgments.json:257, judgments.json:1572, AI기업_채점규칙_v1.5.md:95). |
| Q08 | fail | spacex-xai가 동맹과 적의 수를 비교해 3점을 설명. RC4-03은 미등록 승계 발견. Apple·NVIDIA·Palantir·OpenAI는 비용형/구조형/다발형으로 구분됨(judgments.json:2291, judgments.json:1622, judgments.json:1816, judgments.json:2074, judgments.json:2961, AI기업_채점규칙_v1.5.md:201). |
| Q12 | pass | 전사 환산은 동일하며 imitation 완전 pass가 아니면 상한 3으로 제한한다. 현재 meta·anthropic·spacex-xai·alibaba의 partial 자격 문제는 Q02의 입력 판정 fail로 구분했고, 상한 게이트를 생략한 회사는 확인하지 못함(judgments.json:467, judgments.json:1297, judgments.json:2224, judgments.json:1087, AI기업_채점규칙_v1.5.md:64, rules.py:317, calc_qual.py:125). |
| Q13 | fail | alibaba는 회수 장치가 없다고 명시하면서 무료 오픈웨이트의 보완재 커모디티화를 imitation partial 근거로 남김. TEN-RC3-05는 경쟁사 수뿐 아니라 원문 102행의 회수장치 없음도 긴장 본문·출처에 적는다. 해당 기존 논리는 재검토 시점과 함께 등록됐으므로 비차단. Meta는 유료 클로즈드 API와 광고 회수 장치를 명시(judgments.json:1087, judgments.json:467, AI기업_채점규칙_v1.5.md:70, v1.7.json:1954, v1.7.json:1960, v1.7.json:1967). |
| Q15 | pass | Alibaba 무료 파생모델·NVIDIA 무료 개발자·Meta 무료 Glimmer 개발자를 F5 아군에서 제외. Apple은 소비자 자체가 아닌 수수료 분배 사업자. 나머지도 조직화된 상업 관계를 근거로 함(judgments.json:1139, judgments.json:1816, judgments.json:515, judgments.json:1622, AI기업_채점규칙_v1.5.md:298). |
| Q16 | fail | anthropic 업무 주채널을 개인 사용자 수로 제한한 TEN-RC-02는 예외 적용. openai 소비자 주채널을 보조 거래 채널의 가격·갈아타기 성격으로 제한한 RC4-02는 미등록. 부품 둘의 상한과 SpaceX 복수 채널 검토는 확인(judgments.json:1249, judgments.json:2847, judgments.json:811, judgments.json:1725, judgments.json:2175, AI기업_채점규칙_v1.5.md:400, v1.7.json:1732). |
| Q17 | pass | 원문 F2 세 경로와 확정 5점 자격을 대조. Oracle은 성능·표준 fail, 적응 partial로 0통과→2. Apple은 모델·배포 지연도 근거라 표준 하나만으로 2점을 만들지 않음. 나머지도 성능·적응·표준을 구분. 경로 판정을 이번 실행이 새로 산출한 것은 확인하지 못함(judgments.json:233, judgments.json:1547, judgments.json:2424, judgments.json:2630, judgments.json:2870, AI기업_채점규칙_v1.5.md:27, calc_qual.py:45). |
| Q18 | pass | Tesla A=0, SpaceX는 Tesla를 명시적으로 제외. 나머지 F5 A 근거에 자기 관계사를 독립 동맹으로 가점한 문언은 확인하지 못함(judgments.json:2503, judgments.json:2279, AI기업_채점규칙_v1.5.md:199). |
| Q19 | pass | 받은 투자 제거·내 매대 방향·복수 지분 문언을 전사 대조. MS의 Anthropic 투자는 자기 카드 외 원문 G/H에서 확인. TSMC A+1·Anthropic A+1·OpenAI A+1이 결과에 연결됨. Stargate 집계 단위 미규정은 확인 못 한 것에 남김(judgments.json:908, judgments.json:1346, judgments.json:2961, AI기업_채점규칙_v1.5.md:192, AI기업_채점규칙_v1.5.md:214, AI기업_채점규칙_v1.5.md:288, results.json:1292, results.json:1904, results.json:3974). |
| Q20 | fail | Alphabet·Amazon·Meta·NVIDIA에 공통 이탈 조건을 적용하면 기존 허용/제외가 모순. TEN-RC-03은 해당 carried_score의 기존 이탈 잣대 문제라 예외 적용. Apple Gemini·OpenAI Oracle $300B 구매는 제외. Oracle 판매자 관점은 구분(judgments.json:102, judgments.json:310, judgments.json:515, judgments.json:1816, judgments.json:1622, judgments.json:2961, judgments.json:2704, AI기업_채점규칙_v1.5.md:239, AI기업_채점규칙_v1.5.md:275, v1.7.json:1751). |
| Q21 | fail | NVIDIA 자체칩 이탈 반복(TEN-RC-05), Tesla NHTSA 반복(TEN-RC3-04)은 예외 적용. Anthropic 유통 확산과 외부 컴퓨트 대체 불가, Oracle 고객/JV 환류와 시설·현금 위험은 서로 다른 속성으로 구분. Palantir ICE 반복은 후보이며 중복 확정은 확인 못 함(judgments.json:1346, judgments.json:1456, judgments.json:2732, judgments.json:2786, judgments.json:2074, judgments.json:2125, v1.7.json:1811, v1.7.json:1928, AI기업_채점규칙_v1.5.md:262). |
| Q22 | pass | Alphabet 비고객 SpaceX 평가익은 F7 증거에서 제외. Amazon·NVIDIA는 고객사 영업외 항목을 방증으로 한정하고, matrix 입력은 투자 환류 자체다. 평가익만으로 환류를 판정한 입력은 확인하지 못함. C-11 P4 전용 문언과 방증 허용 문언의 충돌은 RC4-06(judgments.json:133, judgments.json:338, judgments.json:1850, calc_qual.py:159, AI기업_채점규칙_v1.5.md:730, v1.7.json:619). |

전사 적용 표의 pass는 해당 질문의 위반을 보존 입력·문언·분기 대조에서 확인하지 못했다는 판정이다. fail의 승계 예외 여부는 위 근거 칸과 발견 사항에 따로 명시했다(AGENTS.md:71, v1.7.json:1135).

| 회사 | Q01 | Q02 | Q03 | Q07 | Q08 | Q12 | Q13 | Q15 | Q16 | Q17 | Q18 | Q19 | Q20 | Q21 | Q22 | 해당 회사 대조 위치 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| alphabet | pass | pass | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | fail | pass | pass | judgments.json:7, results.json:27 |
| amazon | pass | pass | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | fail | pass | pass | judgments.json:211, results.json:319 |
| meta | pass | fail | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | fail | pass | pass | judgments.json:425, results.json:640 |
| microsoft | pass | fail | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:618, results.json:929 |
| tsmc | pass | fail | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:811, results.json:1218 |
| alibaba | pass | fail | fail | pass | pass | pass | fail | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:1043, results.json:1507 |
| anthropic | pass | fail | fail | pass | pass | pass | pass | pass | fail | pass | pass | pass | pass | pass | pass | judgments.json:1249, results.json:1831 |
| apple | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:1525, results.json:2122 |
| nvidia | fail | pass | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | fail | fail | pass | judgments.json:1725, results.json:2430 |
| palantir | pass | fail | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:1985, results.json:2717 |
| spacex-xai | pass | fail | fail | pass | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:2175, results.json:3025 |
| tesla | fail | fail | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | fail | pass | judgments.json:2403, results.json:3294 |
| oracle | pass | fail | fail | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | pass | judgments.json:2608, results.json:3583 |
| openai | pass | fail | fail | pass | pass | pass | pass | pass | fail | pass | pass | pass | pass | pass | pass | judgments.json:2847, results.json:3901 |

## 발견 사항

- [severity: high] RC4-01 · F3 partial 자격 — meta·anthropic·spacex-xai는 imitation=partial이지만, 원문 81행의 partial은 구조적으로 못 베끼는 자산이 있고 아직 앞서지 못한 경우다. Meta는 Google도 같은 전략이 가능하며 원문에는 Alibaba도 유사하다고 적는다. Anthropic은 MCP·저작권 우회 모두 따라 할 수 있다고 적는다. SpaceX는 Colossus가 자본이면 복제 가능하고 궤도 DC는 미실현이라고 적는다. 이 근거로 구조적 자산의 partial 자격을 충족하지 못한다. 원문 자체의 판정표 100·101·106행도 같은 partial을 부여하므로 원천 내부 모순을 승계한 문제다. Amazon·Alphabet·Microsoft·Apple·Oracle에는 모방 가능·설치기반 재탕으로 fail을 적용한 것과도 다르다. 같은 기존 잣대의 승계 모순이지만 이 세 회사의 이 사유는 open_tensions에 등록돼 있지 않아 예외 불가. Anthropic의 나머지 입력을 유지하며 imitation만 fail로 재판정한다면 통과점 1→F3 2로 한 칸 달라질 수 있다. 최종 재판정은 이번 리뷰에서 하지 않았다 — judgments.json:467, judgments.json:1297, judgments.json:2224, judgments.json:52, judgments.json:257, judgments.json:661, judgments.json:1572, judgments.json:2654, AI기업_채점규칙_v1.5.md:81, AI기업_채점규칙_v1.5.md:100, AI기업_채점규칙_v1.5.md:101, AI기업_채점규칙_v1.5.md:106, AI기업_채점표_v1.5.md:274, AI기업_채점표_v1.5.md:324, AI기업_채점표_v1.5.md:640, v1.7.json:1731, rules.py:311.
- [severity: medium] RC4-02 · openai F1 주채널 — 소비자 채널이 점수를 결정한다고 적고, 뒤의 제한 근거는 OpenRouter 저가·프리미엄 부재·쓴 만큼 내고 갈아타는 거래 채널이다. 원문은 얕은 채널이 깊은 채널을 깎지 못하게 하며 소비자의 가격 결정력은 가격 인상 후 이탈로 묻는다. 소비자 4점 자체가 틀렸다고 확정한 것이 아니라, 현재 4점을 제한하는 근거의 채널이 어긋난다. Anthropic F1의 유사 문제는 TEN-RC-02로 등록됐지만 OpenAI F1은 등록되지 않았다. 기존 잣대를 바꾸지 않은 승계 발견이므로 긴장 등록·재검토 시점 없이 예외 적용 불가 — judgments.json:2854, judgments.json:2855, judgments.json:2856, AI기업_채점규칙_v1.5.md:400, AI기업_채점규칙_v1.5.md:406, AI기업_채점규칙_v1.5.md:408, v1.7.json:1732, v1.7.json:1731, AGENTS.md:71.
- [severity: medium] RC4-03 · spacex-xai F5 H — 입력은 A+1/H-1인데 근거가 동맹이 적보다 확실히 많지 않음→3으로 수 비교를 쓴다. 별표 G는 적대 종류로 H를 정한다. NASA·Space Force 상업 관계는 A+1을 지지하지만 열거된 적대를 비용형/구조형/다발형 중 어디에 놓았는지는 이 문장으로 확인하지 못한다. A나 F5 3점의 대체 점수는 확정하지 않았다. 이 수 비교 사유는 규칙 긴장 목록에 없으므로 승계 예외 불가 — judgments.json:2285, judgments.json:2290, judgments.json:2291, AI기업_채점규칙_v1.5.md:201, AI기업_채점규칙_v1.5.md:205, AI기업_채점표_v1.5.md:653, v1.7.json:1731.
- [severity: medium] RC4-04 · tsmc F3 가속도 — acceleration=pass의 근거는 FY25 실적 +31.6%와 FY26 가이던스 +42.7%, EPS 성장률 하나다. 원문은 계획·포지션 0, 성장률 변화의 실측 비교를 요구한다. 가이던스는 다음 기간에 실제로 빨라졌다는 관측이 아니다. 원문 판정표 109행도 가이던스에 pass를 주므로 원천 내부 모순을 승계했다. TSMC의 이 사유는 TEN-RB-Q10의 judgment_ids·affected에 등록되지 않았다. 나머지 입력을 유지하며 acceleration을 fail로 재판정한다면 통과점 1→F3 2가 될 수 있으나, 새 실측 근거 확보·최종 재판정은 확인 못 함 — judgments.json:856, AI기업_채점표_v1.5.md:224, AI기업_채점규칙_v1.5.md:77, AI기업_채점규칙_v1.5.md:109, AI기업_채점규칙_v1.5.md:145, AI기업_채점규칙_v1.5.md:153, v1.7.json:1830, rules.py:311.
- [severity: low] RC4-05 · alibaba F3 회수 장치의 승계 예외 — 무료 오픈웨이트에는 회수 장치가 없고 다른 호스팅 사업자가 매출을 가져간다고 명시하지만, 보완재 커모디티화를 진짜 전략으로 읽어 imitation partial을 남긴다. 별도 커머스·클라우드 수익모델 pass와 무료 배포의 회수 장치는 별개의 질문이다. 다만 TEN-RC3-05는 경쟁사 두 곳이 한다는 사유와 함께 원문 102행의 회수장치 없음도 본문·출처에 적는다. 해당 판단의 기존 논리가 재검토 시점과 함께 등록됐으므로 Q13 fail을 pass 차단 사유로 세지 않았다. imitation을 fail로 바꿔도 현재 나머지 두 pass로 F3 3은 유지된다 — judgments.json:1087, AI기업_채점규칙_v1.5.md:70, AI기업_채점규칙_v1.5.md:102, AI기업_채점규칙_v1.5.md:721, v1.7.json:1954, v1.7.json:1960, v1.7.json:1967, rules.py:311.
- [severity: medium] RC4-06 · C-11+Q22 문언 — C-11·P4 scope는 F6 P4 전용, ⑦ 근거로 이월하지 않는다고 적지만 같은 규칙 checklist Q22는 고객사이면 방증을 허용한다. Amazon/NVIDIA F7 evidence에는 영업외 비중 방증이 실제 남는다. F7 코드가 두 축만 읽으므로 숫자 이월·추가 감점은 확인되지 않는다. 그렇다고 선언한 방증 금지가 근거란까지 구현됐다고 볼 수는 없다. 이월 금지가 산술 입력만 뜻하는지, 고객사 방증도 없애는지 문언을 일치시켜야 한다. 현재 점수의 이중 계상 확정 사유로 세지는 않았다 — v1.7.json:619, v1.7.json:1474, v1.7.json:1244, judgments.json:349, judgments.json:1871, calc_qual.py:159, docs/scorecard/open-items.md:86.
- [severity: low] C-11 scope의 승계 설명 — F7이 14개사 전부 carried라고 적지만 NVIDIA·Oracle은 새 matrix 판단 fix52를 결과가 사용한다. C-11이 계산 경로를 읽지 않는다는 설명은 맞아도 전사 승계라는 근거는 현재 결과와 일치하지 않는다. 두 회사의 -2 자체를 점수 결함으로 세지 않았다 — v1.7.json:1485, results.json:2635, results.json:3788.
- [severity: low] scope_separation 강제 범위 — 삭제·빈 축·동일 지표·예외 밖 금지어는 실제 거부한다. 다만 서로 다른 등록 지표 둘이라는 조건만 검사하므로 cash/net_cash를 arr/nonop_share로 바꿔도 메모리 변조가 통과했다. 현재 파일은 올바른 cash/net_cash를 쓰고, 실제 계산도 각각 다른 지표를 읽으므로 현재 점수 결함으로 세지 않았다 — schema.py:667, schema.py:688, schema.py:699, schema.py:734, v1.7.json:995, v1.7.json:1006, calc_f6_params.py:216, calc_f9.py:254.
- [severity: low] FIX-54 여신 등록·경계 — 확정 숫자 관측은 Amazon 37.5B, Alibaba 3.33B, SpaceX 4.355B이며 9개 상장사의 신규 미확인 관측은 null/unverified다. 비상장 둘에는 undrawn_credit 관측이 없다. 14사 조사 주장과 14사 확정 숫자 등록은 구분해야 한다. SpaceX의 확인 하한·신용장 전액 차감은 관측에 명시돼 있고, 결과 G3 3.025751년·step0·경계true·F9 -3·총점11은 그 하한과 맞는다. 미확인 나머지를 확정 0이라고 판정하지 않았다 — amazon.undrawn_credit.fix54, alibaba.undrawn_credit.fix53, spacex-xai.undrawn_credit.fix54, observations.json:12909, observations.json:13069, results.json:3233, results.json:3279, calc_f9.py:172.
- [severity: low] 승계 예외 적용 범위 — TEN-RC-02·TEN-RC-03·TEN-RC-05·TEN-RC3-01·TEN-RC3-03·TEN-RC3-04·TEN-RC3-05·TEN-RB-Q10은 위에서 지정한 기존 사유와 해당 승계 결과에만 적용했다. F5의 새 A 엄격 읽기는 예외로 넘기지 않고 14사를 재대조했으며, 신규 RC4-01~04는 아직 규칙 긴장으로 등록돼 있지 않다. F7 전체 재척도만을 이유로 small 칸의 옛 두 축 미복원 문제까지 새 잣대로 취급하지 않았다 — AGENTS.md:71, v1.7.json:168, v1.7.json:1732, v1.7.json:1751, v1.7.json:1811, v1.7.json:1830, v1.7.json:1880, v1.7.json:1903, v1.7.json:1928, v1.7.json:1952, judgments.json:908, results.json:2027, results.json:4095.

## 확인 못 한 것

- RC4-01~04의 최종 대체 판단·확정 점수는 확인 못 함. 위의 단일 입력 변경 산술은 조건부 영향 설명이며 현재 results를 수정하거나 다시 계산하지 않았다(judgments.json:467, judgments.json:856, judgments.json:1297, judgments.json:2224, judgments.json:2279, judgments.json:2847, rules.py:311).
- SpaceX의 LC 645M이 회전여신 5,000M 내부에서 발행됐는지는 확인 못 함. 현재 관측은 미확정 위치를 적고 전액 차감한 하한을 쓴다. facility 밖으로 읽어도 관측의 두 민감도 경우에서 G3 판정은 같다(spacex-xai.undrawn_credit.fix54).
- Anthropic·OpenAI의 undrawn_credit 확정액, 미확인 9개 상장사의 확정액은 확인 못 함. 해당 관측 부재·null을 0인 사실로 승격하지 않았다(observations.json:12909, observations.json:13069, calc_f9.py:259, calc_f9.py:266).
- F7 Anthropic 환류 여부는 확인 못 함. OpenAI Startup Fund 루프는 보존 원문의 후보를 찾았으나 활성 F7 입력 복원·범위 검토는 확인 못 함. SpaceX F7에 적힌 설명을 다른 소비자인 OpenAI F7의 검토된 입력으로 옮기지 않았다(judgments.json:1432, judgments.json:3053, judgments.json:2307, AI기업_채점표_v1.5.md:662, v1.7.json:1890).
- C-08의 계약상 이탈 가능·실질 이탈 유인 중 확정 잣대, Stargate의 합작 법인별/참여사별 동맹 집계 단위는 확인 못 함. 현재 한 합작 법인 집계와 그 미규정은 기록돼 있다(v1.7.json:1764, v1.7.json:1808, judgments.json:2961).
- Palantir F5의 ICE 관련 사업 정당성 적대와 F8의 ICE 논란 고객 전이 위험이 같은 속성을 실제로 몇 점 중복시켰는지는 확인 못 함. 정치적 적대와 고객·정권 의존을 다른 속성으로 배분했다는 명시도 없다. 따라서 중복 후보로 남기며 Q01/Q21 추가 fail 회사로 확정하지 않았다(judgments.json:2085, judgments.json:2086, judgments.json:2132, judgments.json:2134, AI기업_채점규칙_v1.5.md:262).
- arr kind 라벨을 actual로 바꾼 관측이 실질적으로 진짜 ARR인지 스키마는 확인하지 못한다. 메모리 변조는 통과했고 소비 코드는 선언된 kind를 믿는다. 현재 두 회사는 run_rate로 남아 성장 보정에서 거부된다(schema.py:806, calc_f6_params.py:465, results.json:1972, results.json:4042, docs/scorecard/open-items.md:87).
- F2의 세대 격차를 몇 축에서 요구할지, 3경로 통과·세대 격차 없음의 점수, C-06의 영업손익/FCF 0 및 추세·완충 잠식의 완전한 기계 정의는 확인 못 함. 이들은 현재 전사 입력이 직접 닿지 않거나 아직 명시적으로 대기하는 자리다(v1.7.json:1302, calc_qual.py:106, calc_f9.py:117, calc_f9.py:247, docs/scorecard/open-items.md:43).
- 생성 HTML·화면 동작 및 외부 사실의 최신성은 확인 못 함. 빌드·외부 조회를 수행하지 않았고 이 part는 보존 입력과 규칙 일관성에 한정한다(docs/scorecard/design-guideline.md:60).
