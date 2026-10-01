# 판단 변경 제안 흐름 (2026-10-01)

사용자 요청: research 뒤 에이전트가 바꾸고 싶은 판단을 "제안" 으로 써 두면, 사람은 승인 페이지에서 반영·거부만 누른다.
사람이 상시로 고치는 전체 판단 표(8절)는 따로 둔다. 일회용 코드는 승인·취소에만 남긴다.

## 계약

- 파일: `output/<run_id>/proposals.json`, schema `scorecard.proposals/1`.
- 항목: `proposal_id`(PRP-NNN), `company_id`, `factor`, `changes`(judge 가 받는 키: score 또는 판정 재료 키),
  `evidence_after`(제안 뒤 근거 문장 전체 목록, 없으면 근거는 그대로), `reason`, `evidence_ids`(인용 근거, evidence.json 에 있어야 함),
  `proposed_by`, `proposed_at`, `status`(pending|accepted|rejected), 결정 뒤 `decided_by`·`decided_at`·`decision_note`.
- 제안 파일은 입력 해시에 들지 않는다. 반영하면 judge(revise_judgment)를 거쳐 judgments 해시가 바뀐다.
- 반영: CLI `proposal <run_id> --id PRP-NNN --accept|--reject [--by NAME] [--note]`. accept 는 revise_judgment 를 부르고
  status 를 accepted 로 쓴다. 판단이 제안 뒤 바뀌었으면(제안 시점 값과 다르면) 반영을 거부한다.
- 에이전트는 제안 파일을 쓸 수 있고 반영·거부는 사람이 승인 페이지에서 한다(CLI 는 에이전트 세션이면 거부).

## 화면

- 새 절 "판단 변경 제안": 카드마다 기업·factor, 지금 값 → 제안 값(한국어), 근거 문장 바뀌는 줄(뺀 줄·더한 줄), 사유,
  인용 근거 링크, [반영]·[거부] 버튼. 결정된 제안은 결과 배지.
- 8절은 "전체 판단 표" 로 이름을 바꾸고 그대로 둔다.
- 일회용 코드: confirm·judge·proposal POST 에서 뺀다. approve·revoke 는 유지(에이전트가 승인을 누르는 것을 막는 유일한 장치).

## 검증

- Python: 스키마, 반영·거부, 판단이 바뀐 뒤 반영 거부, 에이전트 세션 거부, summary 계약 픽스처.
- node: 제안 카드 렌더, POST 인자, 코드 없이 confirm·judge·proposal 처리, approve 는 여전히 코드 필요.
- 원본 폴더 전체 테스트.
