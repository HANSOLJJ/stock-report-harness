# 결정 메모 — 중계 주소·제목뿐인 근거 막기

- 2026-10-12 풀기 방식: Google News 기사 페이지(`/rss/articles/<id>`)의 `data-n-a-sg`(서명)·`data-n-a-ts`(시각)로
  `/_/DotsSplashUi/data/batchexecute` 에 `Fbv4je` 요청을 보내면 원문 URL 이 돌아온다. 표준 라이브러리만으로 되고, 도구 식별 UA 로도
  된다(Axios·Reuters·The Information 세 건 시험). 외부 패키지(googlenewsdecoder)는 설치하지 않는다.
- 수집 단계에서 일괄로 풀지 않는다. 후보 5,412건 × 요청 2회라 무겁고, 근거로 올리는 것은 실행당 150건 안팎이다.
- 제목뿐 판정은 기존 `citable_evidence_violation` 과 같은 정규화(공백 접기·대소문자 무시)를 쓴다. 따로 길이 기준을 두지 않는다.
- 확정(confirm) 검사도 v2.0 이상에만 건다. 처음에 모든 실행에 걸었더니 v1.x 시험 64건이 깨졌다(시험 자료가 중계 주소·제목 발췌).
  v2.0 시험은 V19Base.setUp 에 확정 전 단계(before_confirm)를 두고 V20Base 가 후보·출처 주소를 example.com 으로 바꾼다.
- '제목만' 판단 문장은 쓰는 시점(revise_judgment, judge·proposal 공용)과 research 에서 막는다. 계약 검증(validate_scorecard)에는
  넣지 않았다 — 넣으면 10월 승인본(OpenAI ③ 등 6건)이 깨진다.
- 10월 실행에 대면 83건: 중계 주소 47, 제목뿐 30, '제목만' 판단 6(alphabet·amazon·microsoft·nvidia·palantir ⑤, openai ③).
  앞서 대화에서 센 38건은 길이 기준을 섞은 느슨한 셈이었고, 코드 기준(정규화 후 같음)으로는 30건이다.
- research 검사는 규칙 v2.0 이상에만 건다. v1.9 이하 고정 실행과 시험 자료를 깨지 않기 위해서다. 10월 승인본은 v2.0 이지만
  research 를 다시 돌지 않는다(protect_approved_run).
