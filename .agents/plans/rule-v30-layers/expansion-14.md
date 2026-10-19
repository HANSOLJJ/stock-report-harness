# 규칙 v3.0 14개사 확장 실행

## 왜

시범 5개사(Alphabet·Apple·TSMC·SpaceX + xAI·Anthropic)는 pilot10 으로 승인·빌드됐다. 나머지 9개사(Amazon·Microsoft·Meta·NVIDIA·Oracle·Tesla·Palantir·Alibaba·OpenAI)를 v3.0 층·사업 단위로 매겨 14개사 채점표를 만든다(2026-10-19 사용자 "진행해봐"). 9개사용 시장 정의표 넷은 823d3ec 에서 규칙에 묶었다.

## 실행 모양

- slug `ai-scorecard-2026-10-v30full`, `init --from-run ai-scorecard-2026-10-v30pilot10 --add-companies amazon,microsoft,meta,nvidia,oracle,tesla,palantir,alibaba,openai --change-type company-add`. 기준일·정보 컷오프 2026-10-14, 가격 기준일 2026-10-09 를 이어받는다.
- 기업 추가 실행이라 재판단 검사는 더한 9개사만 본다. 시범 5개사 판단은 그대로 넘어간다. 예외는 새 정의표가 닿는 연결이다. `ai_models_api` 는 모델을 파는 회사의 API 사업을 재므로 OpenAI 와 함께 Anthropic API 사업·xAI AI 솔루션 사업에도 같은 정의로 잇는다(같은 시장은 같은 정의).
- 층 단위 규칙이라 `diff` 로 기존 기업 불변을 증명하지 못한다. 리뷰는 14개사 전체 4영역이다. 시범 5개사 점수가 pilot10 과 같은지는 결과 비교로 보인다(새 시장을 이은 Anthropic·xAI 는 바뀐 이유를 적는다).
- `--add-companies` 는 9개사의 관측·판단·트리거를 가져오지 않는다(pilot10 에 없음). v21 에서 같은 규칙(`_inputs_from_run` 의 회사 단위 ①②③ 버림·v3.0 모양 충돌 판단 carried)으로 옮기는 스크래치 스크립트를 쓴다. 시장 관측·출처는 `data/_market/<id>/` 의 넷을 더한다.

## 단계

| # | 할 일 | 확인 |
|---|---|---|
| E1 | init | 실행 폴더, 이어받은 건수 |
| E2 | 9개사 관측·판단·트리거 v21 에서 옮기기, 시장 관측 넷 더하기 | 스키마·교차 참조 검증 통과 |
| E3 | 9개사 collect(뉴스·공시, 창 기본) | 후보 파일 |
| E4 | research 1회(검증만 보고 막힌 곳 정리) | 9개사 carried 판단만 재판단 대상으로 남음 |
| E5 | 판단 세션 1단계(Opus high, 회사마다 한 세션, 5 + 4 두 묶음): 스크래치에 근거·판단 제안·트리거 초안과 사건 교차표 | 9개 보고 |
| E6 | 조율자 대조: 사건 교차표·미확인 방향·근거 등급을 14개사로 맞춤, 고칠 점을 세션에 돌려보냄 | 어긋남 목록 0 |
| E7 | 판단 세션 2단계(한 번에 한 세션씩 반영) + Anthropic·xAI 의 `ai_models_api` 연결 | 맡은 회사 ①~⑨ 계산 |
| E8 | research → calculate → draft | 판정 대기 0, 미결 결정 0 |
| E9 | 4영역 리뷰(14개사) → 수정 한 묶음 → 확인 리뷰 1회 → 계약 검증 | review.md pass |
| E10 | 사람 승인 대기 보고 | — |

## 판단 세션 운영

- 지시서는 pilot2 지시서를 바탕으로 `<scratch>\full-brief.md` 에 쓴다. 바뀐 점: 실행 이름, 기업 추가 실행(9개사는 v21 판단이 carried 로 들어와 모두 새로 매김), 새 시장 넷과 미확인으로 정한 사업(Meta Reality Labs·Tesla 에너지·Xbox·전자상거래), 근거·트리거 번호 구간, 앱 안 브라우저는 자기 탭을 새로 열어 탭 번호를 지정해 씀(다른 세션이 같은 탭을 옮긴 일이 있음).
- 회사 사이 기준은 시범 5개사 판단이다. 같은 층 경쟁사 쌍: OpenAI–Anthropic–xAI(모델), Microsoft–Amazon–Alphabet–Oracle–Alibaba(클라우드), NVIDIA–TSMC(칩·파운드리), Meta–Alphabet(광고·소셜), Tesla–(자동차 단독), Palantir(기업 응용).
- 동시 다섯을 넘기지 않는다(세션 한도 429).

## 위험

- 9개사 판단량이 시범의 두 배 가까이다. 2단계 반영을 한 세션씩 하므로 시간이 걸린다.
- 새 회사 판단이 시범 5개사 판단과 어긋나면(같은 사건을 다른 성격으로 읽음) 기존 회사를 고쳐야 할 수 있다. 그때는 그 회사도 다시 매기고 바뀐 이유를 남긴다.
- 리뷰 범위가 14개사라 리뷰어 토큰이 크다. 영역마다 회사를 나눠 띄운다.
