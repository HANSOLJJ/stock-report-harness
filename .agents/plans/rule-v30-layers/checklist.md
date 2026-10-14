# 규칙 v3.0 체크리스트

설계는 `plan.md`(2026-10-14 대화의 설계안 사본), 구현 순서는 2026-10-14 Plan 에이전트 보고(context-notes 에 요약)를 따른다. 단계 하나가 커밋 하나다. 단계마다 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 를 돌린다.

## 문서
- [x] v2.2 초안의 커밋하지 않은 ②③ 수정과 context-notes 를 `draft/rules-v2.2` 에 기록용으로 커밋
- [x] `draft/rules-v3.0` 브랜치 생성
- [x] 계획 폴더(plan·checklist·context-notes) 생성
- [ ] S1b rules.md 를 v3.0 으로 절 단위 개정(머리말, 1 총점, 2 원칙에 시점 원칙·층 밖, 층과 단위, 3 ①~⑤, 4 ⑥~⑨, 5 합산, 7 체크리스트, 8 미결)

## 코드 (시험 실행까지 최소 경로)
- [ ] S0 승인된 rejudge(v2.0)·v21(v2.1) 실행을 재계산 해시 테스트에 넣기(main)
- [ ] S0b 승인 페이지의 중첩 재료 `[object Object]` 표시 고치기(main, 선택)
- [ ] S2 `scorecard/rules/v3.0.json` 과 스키마 수용(layers, unit, curve, 새 judgment kind)
- [ ] S3 연속 구간 도우미와 ⑥·⑨ 곡선, ⑦·⑧ ×4
- [ ] S4 판단 키에 layer·business, `JudgmentLookup` 확장
- [ ] S5 층·사업 판단 생성·수정 경로, init 단위 전환, CLI `--layer`·`--business`
- [ ] S6 ④ 보유표와 층 무게(`calc_layers.py`)
- [ ] S7 ②③ 층 계산
- [ ] S8 ① 사업 단위 계산(시장 자료 전)
- [ ] S9 ⑤ 동맹 세 부분·적대 띠
- [ ] S10 초안·미리보기 렌더 최소
- [ ] S11 structure·guide·score-research·score-review 문서

## 시험 실행
- [ ] 시범 `init ai-scorecard-2026-10-v30pilot --from-run ai-scorecard-2026-10-v21 --rule v3.0 --companies alphabet,apple,tsmc,spacex-xai,anthropic` 으로 draft 까지
- [ ] 전체 14개사 시험 실행

## 뒤로 미룸
- [ ] 시장 정의표 `scorecard/markets/`·`calc_market.py`·규칙 sha256 연결(그 전까지 ① D·E 는 정책 기본값 0)
- [ ] HTML 리포트(산점도 축·80점 선·방법 카드·층별 화면), 승인 페이지 층별 수정 화면
- [ ] AGENTS.md 문구(main)
