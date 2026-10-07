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
