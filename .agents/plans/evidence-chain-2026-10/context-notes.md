# 진행 기록 — 근거 사슬(URL)

## 2026-10-07 착수
- 외부 분석 주장 확인: evidence.json 72건 confirmed, 72건 모두 excerpt == title, `limitations` 필드 없음. judgments 114개 source_ids 분포 — `SRC-v15-html` 단독 72, `SRC-v15-html`+`SRC-v15-rule` 19, evidence_ids 있는 판단 3.
- v1.5 원본: `git show 71c40b2^:docs/scorecard/source/AI기업_채점표_v1.5.html` (sha256 fa66076c… 등록값과 일치). HTML·MD 모두 URL 두 개(openrouter.ai, arena.ai). 사실별 출처는 원래 없었다.
- 사용자 답: "URL 이 있어야 하지 않겠냐" → 모든 사실 문장에 URL 근거. 지금 실행에 적용(3번 범위 질문의 답으로 해석).
- 규모: 판정 칸 416줄, 올릴 235줄, 내릴 179줄. 판단 status carried 98 · new 16. run as_of 2026-10-06, rule v1.9.
- anthropic.F2 · meta.F2 · nvidia.F2 · tsmc.F2 · openai.F2 는 모두 kind score, inputs 없음. 점수 직접 칸이라 propose `--set score=` 로 바꾼다.
- 근거 입력 경로: evidence.json 은 에이전트가 쓰고 `confirm` 으로 확정, research 가 인용 후보의 출처를 sources.json 에 자동 등록한다. 수동 근거는 sources.json 에 출처를 직접 등록한다.
- 결정: 인용 단위는 EV 하나. 공시 숫자도 filing EV 로. 표지는 줄 끝 `[EV-…]`. 판정 칸은 표지 불요. 게이트 rule ≥ 1.9.
- A단계: 문서(흐름도·시퀀스·근거 계층·스킬 셋·11월 예시)와 리드 범위 표기·⑥ 설명 커밋(0d57b9b 외).
- B단계: 표지 검사 장치 커밋. 표지는 줄 끝 `[EV-…]`(괄호 안 언급은 표지 아님). 인용 근거 표에 본문 발췌·위치 칸(HTML 항상, 초안은 v1.9 이상만 — 옛 승인 실행의 draft 바이트 보호). Python 1316·node 통과.
- C단계: 사용자가 승인 756c276e 를 취소했다(revocations.jsonl).
- F2 는 revise_judgment 대상이 아니다(structure.md 판단 수정 절). anthropic.F2 를 고치는 길은 E단계에서 따로 찾는다.
- D단계 묶음: (openai, palantir) (nvidia, meta) (oracle, microsoft) (spacex-xai, apple) (tsmc, alphabet) (amazon, tesla) (alibaba, anthropic). 방향 칸 414줄. 근거 company_id 는 판단의 기업, 새 출처 ID 는 SRC-SEC-<cid>-<accession>·SRC-WEB-<cid>-NNN.
- **anthropic.F2 정정 방향 변경(2026-10-07)**: v1.5 원 규칙 문서 33행(`git show 71c40b2^:docs/scorecard/rules/AI기업_채점규칙_v1.5.md`)이 성능 도약 예시로 "NVIDIA ②5 · Anthropic ②5 (Opus 5 ARC-AGI 8%→30.2%) · Meta ②4" 를 든다. 두 점수는 같은 잣대(세대 격차 판단)로 매긴 승계 점수이고, 틀린 것은 anthropic.F2·meta.F2 판정 칸의 "세대 격차인지 아직 판정하지 않았다" 문장이다. 점수는 바꾸지 않고 문장을 "세대 격차 판단에서 나온 점수, 축 수는 규칙 미결(rules.md 7절 마지막 표), 현재 벤치마크로 다시 검증하지 않았다" 로 고친다. F2 는 paths 로 바꾸면 generation_gap unknown 이 pending 을 만들어 순위에서 빠지므로 그 길을 쓰지 않는다. 사용자에게 처음 보고한 "4점으로 고치면" 은 틀린 권고였다고 보고한다.
- **TEN-RC-05(nvidia F5·F8) 판정**: 규칙 2.2·⑧ 지침과 ⑤ H −2 정의("주요 고객이 곧 경쟁자")에 따라 고객 자체 칩 속성은 ⑤ 에서만 센다. ⑧ 은 매출 40% 고객 집중의 크기·공급 take-or-pay 약정(2022 재고 상각 선례)·중국 우회 조사로 매기고 −3 유지. ⑧ 내릴 근거에서 "자체 칩 → 의존 방향 악화" 를 빼고 판정 칸에 속성 분리를 적는다.
- **TEN-RC3-04(tesla F5·F8) 판정**: NHTSA 조사는 ⑤ H −1 비용형 정의(규제 조사)에 해당해 ⑤ 에서만 센다. ⑧ 은 머스크 개인 의존·중국 의존으로 −2 유지. ⑧ 에서 NHTSA 를 뺀다.
- 규칙 파일 v1.9 의 open_tensions 는 고치지 않는다(plan rule_hash 가 바뀌면 검증기가 막는다). 11월 실행에서 닫는다. 판단 문장의 "규칙 긴장 목록에 2026-11 재검토 대상" 줄은 판정 내용으로 바꾼다.
- oracle·microsoft 연결 결과(검사 통과, oracle.F7 사라진 토큰 SoftBank·MGX·19 는 원문을 못 찾은 Stargate 세부라 허용).
- **연결 뒤 후속 수정 목록(반영 단계에서 한 번에)**
  1. oracle.F7: 세로축 '돌아옴' 근거였던 Stargate 출자가 미확인으로 빠졌다. 내릴 근거에 "TikTok 미국 합작법인 지분법 투자 + TikTok 이 OCI 대형 고객" [EV-oracle-009, EV-oracle-030] 을 더하고 판정 칸에 세로축 근거를 적는다. 입력 own_money_returns yes 유지(가로축 large 라 점수 −2 그대로).
  2. microsoft.F9: 올릴 근거 셋째 줄(설비투자 예상치 변경, 회사는 리스 분류 효과라 밝힘)은 방향이 없어 판정 칸으로 옮긴다.
  3. microsoft.F7: OpenAI 상대 매출 $24.1B(매출의 약 7%)로 정정됐다. 조달 의존 비중 '작음' 유지(규칙은 수치 임계를 두지 않는다. Oracle 은 RPO 절반).
  4. 관측 oracle.offbalance_B.v15 ($250B, legacy_unverified, 공시 사실 없음) → 10-Q(2026-08-31) 미개시 리스 $288B 로 교체 검토. 게이트 4 커버리지 1 초과라 점수 불변.
  5. anthropic.F2·meta.F2 판정 칸 문장, nvidia.F8·tesla.F8 속성 분리(위 판정), F5 의 긴장 언급 줄.
- nvidia·meta·spacex-xai·apple 연결 결과 검사 통과(문제 0).
  6. nvidia.F2 판정 칸 "추론: Rubin 출하와 독립 측정이 확인되기 전까지 …" — 10-Q(2026-08-26)가 Vera Rubin 양산 출하 시작을 적는다. 출하는 확인, 독립 측정은 미확인으로 고친다. 점수 5 유지(세대 격차 판단은 승계).
  7. meta.F3 판정 칸 "OpenRouter 채택 증거도 아직 없다" → "OpenRouter 에 공개했으나(2026-07-29 실적 콜) 채택 지표는 없다".
  8. apple.F3 판정 칸 "새 Siri 가 출시되고 …" → "새 Siri 는 2026-09-14 베타로 나왔으나 사용·채택 지표가 없어 가속도 판정을 바꾸지 않는다". apple.F2(2점)·F5(H −1, DOJ 반독점·특허 패소)는 유지.
  9. nvidia F5·F8 하이퍼스케일러 비중은 10-Q Note 13 으로 '약 절반'($48.7B/$96.2B)으로 정정됐다. 속성 분리 문장에 이 값을 쓴다.
- openai·palantir 결과. openai.F2 "인간 기준선"(human baseline)이 금지어에 걸려 "인간 기준치"로 바꿨다(출력 파일 직접 수정).
- **웹 검색 한도(세션 200회) 소진**: openai·palantir·apple 묶음이 중간에 WebSearch 를 못 썼다. 한도 때문에 못 찾은 줄은 '우리가 못 찾음'이지 원문 부재가 아니다. 남은 묶음이 끝나면 한도 탓 unfound 만 모아 2차 탐색(WebFetch·Playwright)을 한다. 특히 score_bearing: openai.F1(OpenRouter 단가·점유율), openai.F5(다발형 적대 핵심 줄: MDL 3143·Apple·머스크·MS).
  10. openai.F5 판정 칸 "Oracle 의 Stargate $7B 지분은 동맹으로 남는다" → 원문(DCD 2025-01-23)은 "Oracle·MGX 합산 $7B 출자 예정". Oracle 이 Stargate 초기 출자자라는 것은 OpenAI 발표로 확인. "$7B 지분" 단정을 고친다.
  11. openai.F4 판정 칸 "출하량이나 독립 측정이 확인되면 다시 본다" — Broadcom 이 2026-09-02 Jalapeño 출하를 밝혔다(물량 미공개). 출하는 확인, 물량 미공개라 판정 유지 문장으로.
  12. openai.F2: AA 값이 게시물(09-04)과 기사(09-09)에서 갈린다(근거 unverified 에 기록). 두 값 모두 "Astra 가 1위 모델과 동점 이하"라 5점 아님 판정은 같다 — 확인 필요.
- amazon·tesla 결과 검사 통과. amazon.F2 4점 유지(성능 도약 근거는 Trainium3 다년 약정 채택. '실제 학습'만 미확인). tesla.F1 2점 유지(올릴 근거 빔, 내릴 근거 ASP 하락 확인). amazon.F7 "OpenAI $50B·Anthropic $100B 집행 미확인" 은 10-Q 로 사실 정정됐고 ⑦ 판정 입력엔 넣지 않는 서술 유지.
- 2차 탐색: retry-a(40항목 → found 18·partial 5·not_found 9·is_analysis 9), retry-b(18 → 4·4·5·5). 반영 결정은 scratchpad merge_retry.py DECISIONS(31건). oracle.F7 Stargate 새 줄(예정 보도 + 추론)은 방향 칸에 넣지 않고 판정 칸 문장만 원문대로 고쳤다.
- 최종 병합본 `link/final/`(1차 + 2차 + 후속 수정 22건). 구조 문제 0, 토큰·판정 칸 차이 41건은 모두 조율자 확인 차이.
- 2차에서도 못 찾은 점수 근거: openai.F1 OpenRouter 단가·점유율(기준일 이전 원문 없음), alphabet.F7 Anthropic 매출 '미미'(반대 방향 약정 $200B·백로그 40% 초과를 내릴 근거로 넣고 '작음' 유지 근거를 판정 칸에), anthropic.F6 자본효율 0.52(누적 조달 원문이 $120B~$130B+ 로 갈림). openai.F1·anthropic.F6 점수 영향은 재계산 뒤 확인.
- round 8 리뷰 결과 수집 중.
  - 출력·가독성 needs_fix 1: `.cite` 전체 nowrap → 표지가 카드 밖으로 잘림. 고침(`.cite a` 에만 nowrap), 320·1280px 실측 잘림 0·겹침 0(759개). 커밋함.
  - 사실·출처 a needs_fix 1: amazon.F2 Trainium3 "362 PFLOPS" 는 144칩 UltraServer FP8 합계, 칩당 2.52 PFLOPS(EV-amazon-034). 수정 묶음에 넣는다.
  - 사실·출처 a low 중 바로 고칠 것: anthropic.F6 판정 칸 "ARR $65B 원문을 찾지 못해" → 올릴 근거가 EV-anthropic-040 으로 확인했으므로 미확인 대상을 누적 조달로 좁힌다.
  - 사실·출처 c needs_fix 1: spacex-xai.F2 올릴 근거[3](Starship 궤도 비행) 표지 EV-spacex-xai-009 는 Google 컴퓨트 계약 발췌 → 표지를 [EV-spacex-xai-022, EV-spacex-xai-007] 로.
  - 사실·출처 b needs_fix 2(nvidia.F7): 내릴 근거[1] "$40B 넘게 넣었고(실측)" → 원문은 약정(commitments), Anthropic Series G·$10B·xAI Series E 는 원문에 없다 → '약정'으로 고치고 라운드 세부는 판정 칸 미확인으로. 내릴 근거[3] "담보(Grace Blackwell)" 전제는 원문 없음 → 판정 칸 (추론)으로 옮긴다.
