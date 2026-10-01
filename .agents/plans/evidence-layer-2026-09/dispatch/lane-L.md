# 레인 L — 근거 선별 평가 표본: 실제 뉴스로 라벨 시트 만들기

에이전트: Muse. 의존: 레인 J 병합 완료(수집기 결함 수정 포함). 공통 규약: `README.md` 를 먼저 읽는다. 레인 K(Sonnet)가 동시에 루트 문서를 고친다. 소유가 겹치지 않는다.

## 목적

계획 5단계는 "사람이 라벨을 붙인 근거 표본으로 선별 정확도를 잰다" 이다. 그 표본이 아직 없다. 실제 뉴스에서 후보를 골라, 사용자가 "맞음 / 틀림 / 관련 없음" 만 표시하면 평가 표본이 되는 시트를 만든다. 다음 정기 채점에서 에이전트가 근거를 고르는 품질을 이 표본으로 잰다.

## 할 일

1. **수집.** 저장소 밖 임시 폴더를 `SCORECARD_DATA_ROOT` 로 두고 14개사 뉴스를 실제로 한 번 수집한다(`scripts/scorecard/collect_news.collect_company_news`, 질의는 `companies.json` 의 `news_queries` 가 있으면 그것). 실행 묶음(`output/`)을 만들지 않는다. 하루 한도(질의당 4회)를 지킨다. 오늘 이미 1~2회 썼다.
2. **선별.** 기업마다 2~3건, 모두 30~40건을 고른다. 고르는 기준을 섞는다. factor 와 관련이 분명해 보이는 것, 애매한 것, 관련이 없어 보이는 것을 함께 넣는다(평가 표본은 쉬운 정답만 있으면 쓸모가 없다). 같은 사건의 중복 기사는 하나만.
3. **에이전트 제안.** 건마다 Muse 가 제안을 적는다. 관련 factor(F1~F9, 없으면 없음), 이유 한두 문장, 확신(높음·중간·낮음), 채널(disclosure·press·company_statement·secondary). factor 정의는 `docs/scorecard/design-guideline.md` 와 `scorecard/rules/v1.8.json` 을 읽고 따른다. **다른 기업의 점수를 근거로 쓰지 않는다. 미래 점수를 적지 않는다.** 투자 권유 표현을 쓰지 않는다.
4. **시트.** `tests/fixtures/evidence/labeling-2026-10.csv`(UTF-8 BOM, 엑셀에서 열리게)와 같은 내용의 `.json` 을 만든다. 열은 `sample_id, company_id, title, source_name, url, published_at_utc, excerpt(원문 그대로 ≤300자), proposed_factors, proposed_reason, proposed_confidence, proposed_channel, label(빈칸), label_factors(빈칸), label_note(빈칸)`. `label` 은 사용자가 `correct`·`wrong`·`irrelevant` 중 하나를 넣는다. `tests/fixtures/evidence/README.md` 에 라벨 방법과 이 표본의 쓰임새를 한국어로 적는다.
5. **보고서.** `validation/lane-L-eval-sample/REPORT.md` 에 수집 결과(기업별 기사 수), 선별 기준과 분포(기업·factor·확신별 건수), 질의를 바꾼 meta·oracle·apple 의 기사 품질 관찰(회사와 무관한 기사가 섞였는지)을 적는다.

## 소유 파일

`tests/fixtures/evidence/**`(새 폴더), `validation/lane-L-eval-sample/REPORT.md`. 그 밖은 고치지 않는다. 수집기 결함을 찾으면 고치지 말고 보고서에 위치와 고치는 방향을 적는다.

## 금지

- `SEC_UA` 값을 출력·기록하지 않는다. 로컬 설정 파일을 만들거나 고치지 않는다.
- 임시 수집 폴더와 `data/` 를 커밋하지 않는다. 기사 본문을 가져오지 않는다(제목·요약·URL 만).
- 한국어 커밋, Co-Authored-By 금지, git push 금지, git stash 금지. 통합 브랜치 merge 가 거부되면 보고만.

## 검증

- 시트의 행 수 30~40, 모든 행에 url·published_at_utc·excerpt, `label` 열은 비어 있음.
- 테스트 기준(unittest 1146건 중 실패 1·오류 14, 전부 원자료 부재)에서 증가 없음. 새 폴더가 테스트를 깨지 않는다.
- 완료는 preamble 의 `worker_done`(--outcome 명시) 뒤 조율자 터미널 `term_be1eaaf8-815c-4231-a858-7229d925e5fe` 에 한 줄 안내.
