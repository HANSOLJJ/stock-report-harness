# 문장 치환 목록 지시서 (2026-10 규칙 v2.1 첫 실행, 1차 리뷰 뒤 수정 한 묶음)

실행 `ai-scorecard-2026-10-v21` 의 1차 리뷰가 고치라고 한 트리거 문장과 근거 문장을 **정확한 치환 목록**으로 만든다. 파일은 고치지 않는다. 조율자가 목록을 검증해 적용한다.

## 대상

1. 트리거 12건: `output/ai-scorecard-2026-10-v21/review-parts/output-readability.md` 「B1」 표(TRG-006·007·012·015·019·021·026·030·034·058·071·102). 트리거가 "지금 판단" 으로 적은 점수가 `results.json` 과 다르다.
2. 트리거 2건: 같은 파일 B1 표 아래 TRG-025·027 의 "다섯 자리" 표현(옛 ④ 사다리 말이다. 지금 ④ 는 층별 보유표의 수직계열화·다각화 두 축이다).
3. 트리거 1건: TRG-017 의 옛 P3 경계 문장. 지금 ⑥ 은 성장 조정 PER(P1′)이고 그 회사의 지금 값과 가까운 경계(1.0 선)를 `results.json` 의 F6 calc 에서 확인해 적는다.
4. 근거 12건: `review-parts/evidence-bullets.md` 「A. 사실 오류」 7건(EV-tsmc-086·anthropic-076·tesla-063·openai-114·nvidia-112·openai-149·microsoft-058)과 「B. 낡은 점수·규칙 서술」 5건(EV-alibaba-007·meta-002·meta-004·nvidia-004·nvidia-083).

## 만드는 법

- 원본 문장은 `output/ai-scorecard-2026-10-v21/triggers.json`·`evidence/evidence.json` 에서 읽는다. 큰 파일이라 python 한 줄이나 grep 으로 그 ID 만 꺼낸다.
- 고칠 문장은 **그 문장 전체**를 새 문장으로 바꾼다. 옛 문장 옆에 정정을 덧붙이지 않는다.
- 새 문장의 숫자·점수는 확정 값과 대조한다. 점수는 `results.json` 의 `companies[].factors.<F>.score`, 관측은 `observations.json`, 원문 사실은 그 근거의 `excerpt`·`locator` 가 기준이다. 원문 대조가 필요한 사실 오류는 근거의 출처를 열어 확인한다(SEC 는 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <주소>` 로만 받는다. 막힌 페이지를 User-Agent 를 바꿔 열지 않는다).
- 완결된 현재 상태 문장으로 쓴다. 규칙 버전 표기, 변경 표시, 작업 번호, 이전 판·다른 트리거를 가리키는 표현("직전 실행", "TRG-0NN 으로 이었다")을 쓰지 않는다.
- 트리거의 조건·재검토 칸과 근거의 `conditional_impact` 에 미래 점수나 점수 이동("−3→−4", "+2점")을 적지 않는다.
- **조율자가 같은 묶음에서 다음 판단을 다시 세운다.** Palantir ④⑦, Alibaba ⑦, OpenAI ⑦, Apple ④, Meta ⑧, Microsoft ②④⑤⑧, NVIDIA ①⑧. 이 칸의 점수를 적는 문장은 지금 `results.json` 값으로 쓰고 `depends_on` 에 그 칸(예: `"palantir.F7"`)을 적는다.

## 출력

`.agents/plans/v21-first-run-2026-10/work/subst-fix1.json`

```json
{"items": [
  {"file": "triggers", "id": "TRG-006", "field": "observation", "old": "<지금 값 안에 정확히 한 번 나오는 부분 문자열>", "new": "<새 문장>",
   "finding": "출력 B1", "checked": "<새 숫자를 무엇과 대조했는지 한 줄>", "depends_on": []}
]}
```

- `file` 은 `triggers` 나 `evidence`. `field` 는 점 경로다(`observation`, `condition`, `recheck.what`, `relevance`, `counter_evidence[0]`, `unverified[1]`).
- `old` 는 그 칸의 지금 값 안에 **정확히 한 번** 나오는 문자열이어야 한다. 칸 값 전체를 바꿀 때는 칸 값 전체를 `old` 에 넣는다.
- 한 ID 에 고칠 자리가 여럿이면 항목을 여러 개 만든다.

마지막 답변(한국어, 짧게): 만든 항목 수, 리뷰가 고치라고 했지만 원문 대조 결과 고치지 않은 것과 이유, `depends_on` 이 있는 항목 목록.
