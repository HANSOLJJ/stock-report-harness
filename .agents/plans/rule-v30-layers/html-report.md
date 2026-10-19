# 규칙 v3.0 HTML 리포트

## 왜

pilot8 이 승인됐지만 v3.0 실행은 HTML 리포트를 제대로 그리지 못해 빌드할 수 없다(2026-10-19 사용자: "일단 1번 해봐봐"). 지금 렌더러(`scripts/scorecard/render_html.py`)는 오류 없이 돌지만 v3.0 내용이 빠지거나 옛 규칙 문장이 실린다.

## 지금 빠지거나 틀린 것 (pilot8 을 스크래치에 그려 확인)

| 자리 | 문제 |
|---|---|
| 기업 카드 ①②③ | 층·사업 판단의 근거(판정·올릴 근거·내릴 근거)가 하나도 실리지 않는다. 초안은 `rc.unit_judgments` 로 판단마다 싣는다 |
| 기업 카드 | 층 표(층·층 매출 몫·①②③)와 시장 표(구성 사업·시장·순위·점유율·변화·반영·D·E)가 없다. 초안에는 있다 |
| 기업 카드 "참고" 줄 | `['chip_design', …]` 같은 파이썬 목록과 사업 내부 ID 가 그대로 보인다 |
| 요약 산점도 | 과점 기준선 80·56(잠정) 표시가 없다 |
| 요약 | 열한 층 보유표(층별 화면)가 없다. 기존 `render_layers` 는 v2.1 여섯 층 보유표용이다 |
| 방법 절 방식 열 | `business`·`layer_paths` 같은 내부 이름이 나온다(초안은 `rc.MODE_LABELS`) |
| 방법 카드 "무엇을 보고 매기는가" | v3.0 다섯 방식(business·layer_paths·layer_cp·holdings·alliance)에 규칙 값 문장이 없어 사용자 원본의 옛 지표 문장(① 부품 상한, ③ ✅·❌ 통과점)이 실린다 |

## 지킬 것

- **pilot8 승인을 깨지 않는다.** 승인 해시는 규칙·입력·판단·결과·초안을 묶는다. 바꾸는 코드는 HTML 렌더(`render_html.py`)와 HTML 에서만 쓰는 `render_common` 함수로 한정하고, 계산·초안(`render_md`)·규칙 JSON 은 건드리지 않는다. 단계마다 `status` 의 `approval_valid` 를 확인한다.
- **승인된 v2.x 실행의 HTML 을 바꾸지 않는다.** v3.0 분기는 `rc.is_layered(rules)` 일 때만 탄다. 고치기 전에 v21·rejudge 를 스크래치에 그려 두고 단계마다 바이트로 대조한다.
- 대시보드 디자인 규칙(dashboard-design): 표 숫자 열 우측 정렬, 320px 에서 본문 가로 넘침 없음(표는 자기 상자 안에서 스크롤), 색만으로 정보를 전하지 않음, 다크 모드 토큰.

## 단계 (단계 하나 = 커밋 하나)

1. 기업 카드에 층 표·시장 표, ①②③ 층·사업 판단 근거 블록(초안과 같은 순서·문장).
2. "참고" 줄의 층 ID 목록·사업 ID 를 이름으로 바꾸기(HTML 표시만).
3. 요약에 열한 층 보유표(회사 × 층, 판매·자체 사용·준비 중·없음과 층 매출 몫).
4. 산점도에 과점 기준선 80·56 과 잠정 표시(규칙 `scoring.baseline_note` 가 있을 때).
5. 방법 절: 방식 열 이름, v3.0 다섯 방식의 "무엇을 보고 매기는가"를 규칙 값으로.
6. 감사 기록(audit.md)의 v3.0 표시 점검.
7. 검증: 테스트(v3.0 합성 실행 HTML, 옛 실행 바이트 불변), 320·768·1280px 가로 넘침, 계약 검증 `--require-html`, pilot8 빌드.

## 검증

- `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`, `npm run test:node`.
- 스크래치 렌더로 v21·rejudge HTML 바이트 대조, pilot8 의 `approval_valid`.
- 앱 안 브라우저로 pilot8 HTML 을 320·768·1280px 에서 보고 `scrollWidth > clientWidth` 검사, 다섯 탭 모두.
- 마지막에 pilot8 을 빌드한다. 빌드는 `scorecard/history.csv` 에 행을 더하므로 그 행을 커밋할지 사용자에게 묻는다.
