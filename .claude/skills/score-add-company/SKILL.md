---
name: score-add-company
description: AI 기업 채점표 레지스트리에 기업을 등록한다. /score-add-company <id> --name ... 처럼 사용하며 scorecard/companies.json 에 기업을 등록만 한다.
---

# 기업 등록 스킬

`scorecard/companies.json` 레지스트리에 새 기업을 등록한다.

## 절차

1. 요청에서 기업 정보를 파싱한다: `company_id`, 표시명, 유형('소비자', '업무', '거래', '부품', '소비자·업무', '혼합'), 평가 범위, 상장 여부.
2. 실행한다:
   ```
   python scripts/scorecard_cli.py add-company <id> --name "<표시명>" --type <유형> --scope "<평가범위>" (--listed --ticker <티커> --exchange <거래소> | --private) [--alias <별칭> ...] [--share-basis adr|ads --adr-ratio <비율>] [--currency <통화>]
   ```
3. 등록만 하고 멈춘다 (research 나 채점으로 진행하지 않는다).

## 제약

- `company_id` 는 안정된 식별자다. 한번 정하면 바꾸지 않는다. 나중에 개명하면 관측·판단·점수·초안 네 곳에 걸쳐 승인이 무효가 된다.
- 상장사는 `--listed --ticker --exchange`, 비상장사는 `--private` 를 쓴다. ADR·ADS 면 `--share-basis adr|ads` 와 `--adr-ratio` 가 함께 필요하다.
- 표시명·별칭이 기존 기업과 겹치면 명령이 거부한다.
- 등록은 채점이 아니다. 등록만 한 기업은 관측·판단이 없어 아홉 항목이 전부 대기 상태가 되고 순위에서 빠진다.

## 완료 보고

등록된 기업 수, 다음 명령 `/score-extend`.
