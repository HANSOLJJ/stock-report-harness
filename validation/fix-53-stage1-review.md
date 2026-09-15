# FIX-53 1단계 검토 — pass

- 일시. 2026-09-15. 대상 worker `fb394f9…0c151ba`. 점수 무영향 단계.

## 재현

```
테스트 416 OK · 총점 14개사 FIX-52 와 동일 · results_hash 31652692…
활성 판단 114건 id 전부 초안에 등장 · anthropic.F5.impl48 근거 등장 · meta F2 옛 문장 ~~…~~ (superseded)
net_cash 블록 통째 삭제 → 스키마 거부
open_tensions TEN-RC-02(상향 가능) · TEN-RC-03(방향 미정) · TEN-RC-05(중복 폭 미확인), 전부 recheck 2026-11
```

## 줄끝 — 조율자 독립 새 checkout 재현

임시 `git worktree add` (autocrlf=true 시스템 기본) 에서:

```
obsreg   run · observations · judgments · rules  원시 바이트 == results.input_hashes   전부 True
baseline rules · observations · judgments · run  원시 바이트 == approval.hashes        전부 True
baseline results  approval.hashes.results == results_hash(sha256_obj) 0942c342…         True
```

**내가 처음 baseline results 를 False 로 봤다 — 승인 파일의 `results` 는 파일 바이트가 아니라 `results_hash`(정규 직렬화)인데 파일 sha256 과 비교했다.** 대조 방식 오류였고 worker 주장이 맞다.

## 지시와 다른 점 — worker 가 맞다

- **baseline 만 `eol=crlf` 예외.** 승인 해시가 CRLF 바이트에 묶여 있어 LF 로 바꾸면 baseline 승인이 깨지고 재승인은 사용자 행위다. 예외로 둔 결과 **baseline 승인이 이제 플랫폼 무관하게 재현된다**(전에는 autocrlf=true checkout 에서만).
- **생성기 `write_json`·`write_text` 에 `newline="\n"`.** 텍스트 모드 기본값이 Windows 에서 CRLF 를 써서, 속성만 걸었으면 계산 한 번에 되돌아갔다. 지시에 없던 근본 원인.
- 범위를 한 번 넓게 잡아 주식 리포트 18개 줄끝을 바꿨다가 내용 차이 0 확인 후 되돌리고 좁힌 것을 스스로 보고했다.
- 해시 함수 정규화는 제안만. 바꾸면 기존 승인 여섯 종이 전부 달라져 이중 경로(`hash_scheme`)가 필요하다는 판단까지 타당.

## 다음

2단계 재료 대기 — qwen 리뷰 A 2차 · qwen A+2 독립 판정 · codex 판정 대조(MS 원문 충돌 보류 중) · alibaba 미인출 여신 $3.33B.
