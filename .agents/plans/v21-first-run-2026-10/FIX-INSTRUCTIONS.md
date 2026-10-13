# 수정 판단 세션 지시서 (2026-10 규칙 v2.1 첫 실행, 1차 리뷰 뒤 수정 한 묶음)

실행 `ai-scorecard-2026-10-v21`(기준일·정보 마감 2026-10-12, 규칙 v2.1)의 1차 리뷰가 끝났다. 판단을 다시 세워야 하는 발견을 이 세션 하나가 모두 맡는다.
공통 절차와 파일 모양은 `.agents/plans/v21-first-run-2026-10/JUDGE-INSTRUCTIONS.md` 와 거기서 가리키는 `.agents/plans/rejudge-all-2026-11/REJUDGE-INSTRUCTIONS.md` 를 그대로 따른다
(세 칸 문장, 줄마다 `[EV-…]`, 사건 교차표, 근거 등급, 미확인 처리, 완결된 현재 상태 문장). 항목 기준은 `docs/scorecard/rules.md` 가 원본이다.

## 맡을 일

각 판단은 `output/ai-scorecard-2026-10-v21/judgments.json` 의 지금 판단에서 출발해 **판단 전체**(changes·evidence_after·evidence_up_after·evidence_down_after·cite·reason)를 한 파일에 다시 쓴다.
고칠 것이 없으면 파일을 만들지 않고 마지막 답변에 그 이유를 적는다.

1. **⑦ 세로축 세 건**(리뷰 파일 `output/ai-scorecard-2026-10-v21/review-parts/fact-sources-b.md` 「FINDINGS」 1~3).
   - Palantir: 10-Q(2026-06-30)·10-K(2025) Item 1A 의 투자 계약(Investment Agreements)과 묶어 체결한 상업 계약(Strategic Commercial Contracts, 누적 매출 인식 $325M). 이 문단을 담은 확정 근거가 없으므로 새 근거로 올린다(아래 「새 근거·트리거」).
   - Alibaba: 20-F Item 7.B 의 투자 대상 클라우드 매출(RMB9,415M, 매출의 0.9%)이 확정 근거 EV-alibaba-089 발췌에 이미 있다. 'investees' 가 알리바바가 돈을 넣은 지분인지(Ant Group 처럼 받은 지분과 구분) 20-F 지분투자 주석으로 가른다.
   - OpenAI: Startup Fund 의 Cursor 시드 주도(TechCrunch 2023-10-11)와 YC 스타트업 API 토큰·지분 교환 제안(2026-05 보도). Startup Fund 의 돈이 OpenAI 자신의 돈인지(출자자 구성)를 원문으로 확인하고, 토큰 크레딧을 현금으로 볼지는 Anthropic ⑦ 이 스타트업 크레딧을 할인으로 읽은 것과 같은 잣대로 정한다.
   - **세 건은 다른 회사의 투자 구조를 읽은 방식과 맞춘다.** 14개사 ⑦ 판정 칸의 세로축 문장(Microsoft–OpenAI, NVIDIA–고객 출자, Alphabet·Amazon–Anthropic, Oracle, Tesla–SpaceX 등)을 한 표로 놓고, 같은 구조면 같은 칸을 준다. 미확인은 감점 완화 쪽으로 풀지 않는다(규칙 2.1).
2. **Microsoft ⑤ 판정 칸**(`fact-sources-a.md` 「F1」). "Anthropic 지분 투자는 확인하지 못했다(미확인)" 는 틀렸다. FY26 4분기 실적 콜(SRC-WEB-microsoft-001)에 "$3.2 billion gain from our investment in Anthropic" 이 있다. 그 문장이 확정 근거의 발췌에 있는지 먼저 보고, 없으면 새 근거로 올린다. 동맹 등급은 이미 +2 라 점수는 같다.
3. **Meta ⑧ 약정 축**(`fact-sources-a.md` 「F2」). 분기 뒤 체결 리스 $68B 를 넣어 3.05배(−3)로 두었고, NVIDIA 의 분기 뒤 SB Energy 보증 $105B 는 관측 값에서 뺐다. rules.md ⑧ 절의 약정 축 정의(기간 뒤 약정과 우발 의무의 처리)에 비춰 두 처리가 같은 잣대인지 판정한다. 같은 잣대면 Meta ⑧ 판정 칸에 구분 이유를 한 문장으로 적고, 다르면 고친다.
4. **Apple ④ 모델 칸**(`fact-sources-a.md` 「F3」). 모델 칸 '판매' 의 근거는 EV-apple-051("users can upgrade to iCloud+ to get higher limits")이고, Apple ① 은 EV-apple-037 각주("available for a fee in the future")를 계획으로 처리했다. 두 원문을 열어 지금 유료 한도 상향이 실제로 팔리는지 정하고 ① 과 ④ 가 같은 사실을 같은 성격으로 읽게 한다. **판매 칸이 하나도 남지 않으면 `primary_layer` 에 `null` 을 적고** 판정 칸에 "판매 칸이 없어 비교 그룹이 없다" 를 적는다. 검증기와 렌더러는 조율자가 고친다.
5. **Alphabet ②·Meta ② 판정 칸**(`fact-sources-a.md` 「F4」). "2026-10-08 뒤의 새 평가가 회사별 최고 모델을 바꾸지 않았다" 는 Artificial Analysis 변경 기록의 12 Oct Muse Wonder(52) 와 어긋난다. 원문을 열어 확인하고 문장을 다시 쓴다. 정보 마감(2026-10-12) 뒤의 값은 쓰지 않는다. 숫자를 근거로 쓰려면 새 근거로 올린다.
6. **Microsoft Maia 발표 반영**(사용자 지시 2026-10-13, "이것도 이제 트래킹 해야함"). 조율자가 Microsoft 공식 블로그(2026-10-12 Scott Guthrie)를 원문으로 확정했다. EV-microsoft-070(2027년부터 다기가와트, 주력 추론 시스템, 계획), 071(Maia 200 이 Copilot 등 생산 작업 처리, OpenAI·MAI·오픈소스 모델 구동), 072(미국·유럽·호주 배치, 와트당 토큰 1.7배는 회사 측정), 073(Maia 300 예상 성능). CNBC 보도는 접근 거부라 근거로 쓰지 않는다.
   - Microsoft ②④⑧ 과 NVIDIA ①⑧ 판단에서 이 사실이 닿는 문장을 찾아 맞춘다(예: Microsoft ② 의 "Maia 200 배포 물량 미확인", ④ 칩 칸의 자체 사용 근거, ⑧ 공급 축, NVIDIA ① 대체 공급). 계획(2027년 다기가와트)은 점수에 넣지 않는다. 다른 하이퍼스케일러 자체 칩(TPU·Trainium·MTIA)을 NVIDIA 판단에서 어떻게 읽었는지와 같은 성격으로 읽는다.
   - **추적 트리거를 새로 둔다.** 먼저 `triggers.json` 에 같은 조건의 관찰 중 트리거가 있는지 본다. 없으면 Microsoft 쪽(예: Maia 배치 규모·추론 몫이 실적 자료로 확인되거나 외부 고객 판매가 시작되면 ④ 칩 칸·⑧ 공급 축 재판정)과 NVIDIA 쪽(예: 최대 고객의 주력 추론이 자체 칩으로 옮겨 간 사실이 확인되면 ① 대체 공급·⑧ 고객 축 재판정)을 둔다. 미래 점수를 적지 않는다.
7. **이미 준비된 파일.** `work/judge-fix1/F4-palantir.json`(Palantir ④ AI 무관 몫 1.0, 규칙 일관성 N1)은 조율자가 원문 대조를 끝냈다. 고치지 않는다. Palantir ⑦ 을 고치며 ④ 문장과 겹치는 사실이 있으면 마지막 답변에 적는다.

## 새 근거·트리거

- 새 출처·근거·트리거는 `work/judge-fix1/items-fix1.json` 한 파일에 적는다. 모양은 `work/add_fix_items.py` 머리말과 같다(`sources`·`evidence`·`new_triggers`, 항목마다 `key`). 근거는 원문을 직접 열어 본문 문장을 글자 그대로 `excerpt` 에 옮기고 `locator` 에 위치(공시는 항목·쪽, 기사는 문단)를 적는다. 예시는 `work/items-maia.json` 이다.
- 판단 파일에서는 새 근거를 `[NEW:<key>]`, 새 트리거를 `"NEW:<key>"` 로 가리키고 `cite` 에도 `"NEW:<key>"` 를 적는다. 조율자가 번호를 붙이고 원문을 대조해 확정한 뒤 반영한다.
- SEC 원문은 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <SEC 주소>` 로만 받는다. Google News 중계 주소는 `scorecard_cli.py resolve-urls --url <주소>` 로 푼다. **접근이 막힌 페이지는 User-Agent 를 바꾸거나 다른 우회로 열지 않는다.** 막혔다는 사실을 적고 미확인으로 둔다.
- 상태를 바꾸는 CLI(propose·proposal·judge·confirm·research·calculate 등)는 부르지 않는다. 출력 파일만 쓴다.
- 큰 파일(judgments.json·evidence.json·triggers.json)은 grep/sed·짧은 python 으로 필요한 부분만 읽는다.

## 출력

- 판단 파일: `.agents/plans/v21-first-run-2026-10/work/judge-fix1/<F>-<company_id>.json`. `reason` 에 리뷰 발견 번호를 적는다.
- 마지막 답변(한국어, 짧게): 바뀐 판단 표(회사·항목·바뀐 입력·계산될 점수 가늠·이유), ⑦ 세로축 교차표(14개사), Maia 사건 교차표(회사·항목·읽은 성격), 새 근거·트리거 key 목록, 고치지 않은 항목과 이유.
- 판단 문장은 완결된 현재 상태 문장으로 쓴다. 규칙 버전·변경 표시·작업 번호·이전 판 참조("리뷰가 지적해", "직전 실행에서는")를 쓰지 않는다. 이해상충을 이유로 멈추거나 되묻지 않는다. 투자 권유 표현을 쓰지 않는다.
