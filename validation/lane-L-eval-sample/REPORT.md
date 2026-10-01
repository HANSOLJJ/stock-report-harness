# 레인 L 보고서 — 근거 선별 평가 표본 (2026-10-01)

## 한 일

- 저장소 밖 임시 폴더(`%TEMP%/laneL-data`)를 `SCORECARD_DATA_ROOT`로 두고 14개사 뉴스를
  실제 수집했다. `collect_company_news`를 기업별로 직접 호출했으며 실행 묶음(`output/`)은
  만들지 않았다. 질의는 `companies.json`의 `news_queries`(meta·oracle·apple)와
  그 밖 기업의 표시명·티커 기본값을 그대로 썼다. 질의당 1회만 요청해 하루 한도(4회)를 지켰다.
- 기업마다 2~3건, 모두 38건의 라벨 시트를 만들었다.
  `tests/fixtures/evidence/labeling-2026-10.csv`(UTF-8 BOM)와 같은 내용의 `.json`,
  라벨 방법 `tests/fixtures/evidence/README.md`를 함께 넣었다.
- 건마다 관련 factor(F1~F9, 없으면 빈칸), 이유, 확신(높음·중간·낮음),
  채널(press·company_statement·secondary)을 제안했다.
  factor 정의는 `docs/scorecard/design-guideline.md` 4절과 v1.8 규칙을 따랐다.
  다른 기업의 점수를 근거로 쓰지 않았고, 미래 점수와 투자 권유 표현을 넣지 않았다.

## 수집 결과 (기업별 기사 수, 질의별)

| 기업 | 합계 | 질의별 |
|---|---|---|
| alphabet | 178 | Alphabet / Google 78, GOOGL 100 |
| amazon | 178 | Amazon / AWS 78, AMZN 100 |
| microsoft | 200 | Microsoft 98, MSFT 102 |
| meta | 173 | Meta Platforms 73, META stock 100 |
| tsmc | 188 | TSMC 88, TSM 100 |
| anthropic | 98 | Anthropic 98 |
| alibaba | 185 | Alibaba 85, BABA 100 |
| apple | 177 | Apple Inc 77, AAPL 100 |
| nvidia | 196 | NVIDIA 94, NVDA 102 |
| palantir | 182 | Palantir 82, PLTR 100 |
| spacex-xai | 199 | SpaceX + xAI 99, SPCX 100 |
| tesla | 195 | Tesla 93, TSLA 102 |
| oracle | 173 | Oracle Corporation 73, ORCL 100 |
| openai | 101 | OpenAI 101 |

수집 14개사 전부 성공, 건너뜀(rate limit) 없음. 티커 질의가 보통 100건 안팎으로 더 많이
걷히며, 이름 질의는 70~99건이다. anthropic·openai는 티커가 없어 1개 질의이다.

## 선별 기준과 분포

- 기준. factor와 관련이 분명한 것(예: Anthropic Opus 5.5 1차 발표→F2),
  애매한 것(예: Alphabet EU 검색 데이터 분쟁→F3 후보, Oracle 불가항력→F9 후보),
  무관한 것(예: 옵션 체인 기계 페이지, CEO 사유지, 티커 혼동)을 섞었다.
  같은 사건의 중복 기사는 하나만 골랐다.
- 기업별. 3건 10개사(alphabet·amazon·meta·anthropic·alibaba·apple·nvidia·spacex-xai·tesla·openai),
  2건 4개사(microsoft·tsmc·palantir·oracle). 합 38건.
- factor별. F2 7, F4 5, F9 5, F1 3, F5 2, F3 1, 없음 15.
- 확신별. 높음 13, 중간 19, 낮음 6.
- 채널별. press 21, secondary 12, company_statement 5. 공시(disclosure) 건은 이번 표본에 없다.

## 질의 품질 관찰 (meta·oracle·apple)

- `news_queries`를 바꾼 3개사 모두 회사와 무관한 기사는 질의 오염 수준이 아니다.
  meta("Meta Platforms"·"META stock")와 oracle("Oracle Corporation"·"ORCL")은
  관련 기사가 주류였고, apple("Apple Inc"·"AAPL")은 관련 기사가 주류이나
  "AAPL" 질의에 MarketBeat 기관 보유 기계글(예: L022)이 대량으로 섞였다.
  이는 무관 표본으로 1건 채택했다.
- 오히려 질의를 바꾸지 않은 쪽에서 오염이 컸다. alibaba의 "BABA" 질의에
  인도 영화 'Neem Karoli Baba' 관련 기사가 대량으로 섞였고(무관 표본 L018로 채택),
  nvidia의 "NVDA" 질의에 Navitas Semiconductor 기사를 NVIDIA로 묶은 건이 있었다
  (무관 표본 L025로 채택, 티커 혼동 사례). 일반 단어·두문자 질의의 함정으로,
  수집기보다 질의 설계 쪽 문제라 수집기는 고치지 않았다.
- "GOOGL"/"SPCX" 질의에는 옵션 체인·시세 기계 페이지가 섞였고 각각 무관 표본으로 채택했다
  (L003, L030).

## 검증 명령과 출력 요약

- `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`.
  1146건 중 실패 3·오류 14. 오류 14는 전부 `validation/f6-avail-15/_raw` 원자료 부재
  (FileNotFoundError 13, 원자료 None 1)이며, 실패 1건(fix55 tag sweep)도 같은 원자료 부재
  계열이다. 나머지 실패 2건은 `test_hooks` WiringSmokeTest로,
  테스트가 띄운 `/bin/bash`에 `uv`가 없어(returncode 127) 생긴 환경 이슈이며
  체크리스트에 기록된 기존 현상이다. 새 폴더(`tests/fixtures/evidence/`)를 참조하는
  테스트는 없어 내 변경으로 실패 집합이 늘지 않았다.
- `uv run --frozen pytest -q`. 1131 통과·17 실패로 실패 집합이 unittest와 동일하다
  (subtest 분리 집계). 전부 같은 원자료 부재·환경 이슈이다.
- `npm run check`. 통과. `npm run test:node`. 15건 전부 통과.
- 시트 자체 검증. 38행(30~40 범위), 전 행 url·published_at_utc·excerpt 보유,
  발췌문 최대 203자(≤300), `label` 38행 전부 빈칸, CSV BOM(239,187,191) 확인.
- 금지 준수. 임시 수집 폴더와 `data/`를 커밋하지 않았고(작업 트리에 없음),
  기사 본문을 가져오지 않았으며(제목·요약·URL만), SEC_UA를 출력·기록하지 않았다.
  로컬 설정 파일을 만들거나 고치지 않았고, `scripts/`를 고치지 않았다.

## 소유 밖에서 발견한 문제

- `BABA`·`NVDA` 질의 오염(위 3절). 질의 설계 문제이며 수집기 결함이 아니라 고치지 않았다.
- `test_hooks` WiringSmokeTest 2건은 `/bin/bash`에 `uv`가 없어 실패한다.
  소유 밖이며 환경 이슈라 고치지 않았다.

## 남긴 것

- `label` 열이 빈 38건 표본. 사람이 `correct`·`wrong`·`irrelevant`를 표시하면 평가 표본이 된다.
- 임시 폴더(`%TEMP%/laneL-data`, `laneL-titles`, `laneL-*.py`, `laneL-selected.json`)는
  저장소 밖에 두었고 커밋하지 않았다. 재수집 시 같은 방식으로 다시 만들 수 있다.

## 커밋

- `dfe51db` chore: 통합 브랜치 병합(체크리스트 동기화)
- `bdb667a` feat: 근거 선별 평가 표본 38건과 라벨 방법 추가(시트·README·보고서 초판)
- 이 줄을 고친 docs 커밋이 최종이며 SHA는 조율자 터미널 안내에 적는다.
