# 리뷰 2차 중간 판정 — C·B 도착, A 진행 중, D 는 3차로

- 일시. 2026-09-15. 기준 해시 results `5e8ce6fc…` · draft `931f5632…`.

## C 규칙 일관성 (codex, `b2825ac`) — needs_fix

1차 결함(F7 범위·run_rate 승격·결정 연결) **해소 확인.** 새 발견 7건 검증 결과 전부 사실.

| # | 발견 | 성격 | 처리(사용자 범위 결정) |
|---|---|---|---|
| RC-06 high | 초안 렌더러가 `baseline.evidence` 를 찍음 → 이번 실행 갱신 판단 근거가 초안에 안 나옴 | 엔진 | FIX-53 1단계 |
| RC-01 medium | `net_cash` 블록 통째 삭제 시 스키마 통과 | 엔진 | FIX-53 1단계 |
| RC-07 medium | judgments.json CRLF — 리뷰 트리에서 원시 바이트 해시 재현 실패 | 엔진 | FIX-53 1단계 (`.gitattributes`) |
| RC-04 medium | TSMC A+2 근거가 "**NVIDIA 의** 적들까지" — 엄격 읽기를 안 댐 | **바꾼 잣대가 닿는 곳** | 비 Claude 병렬 재판정(J) |
| RC-02 high | anthropic F1 — 주채널 업무인데 개인 사용자 수로 5점 제한. 별표 A "가장 강한 락인" · MS 업무 5 와 불일치. **상향 방향** | 승계 | 긴장 → 2026-11 |
| RC-05 medium | nvidia 고객 자체 칩 이탈을 F5 H·F8 에 중복 | 승계 | 긴장 → 2026-11 |
| RC-03 high | C-08 이탈 기준 F5 전사 미통일 | 승계·미결 | 긴장 → 2026-11 |

## B 재무 계산 (codex, `11b2cf3`) — needs_fix

**F6·F9 산술 재계산 불일치 0건.**

| # | 발견 | 검증 | 처리 |
|---|---|---|---|
| high | **alibaba 확정 미인출 여신 $3.33B 관측 누락** | 20-F MD&A "US$3.33 billion revolving credit facility which we have not yet drawn as of March 31, 2026" · 주석 "has not yet been drawn down … amended from US$6.5 billion to US$3.33 billion" · "in compliance with all covenants". $3.17B 시설(미사용 약 $2.6B)과 별개. **사실** | 설계 지침 6.4 적용 — 새 결정 아님. 런웨이 2.6388→3.0996년(+3.3%, 경계 근접), G3 step -1→0, **F9 -4→-3, alibaba 총점 6→7.** $2.6B 포함 시 3.46년, 결론 동일. FIX-53 2단계 |
| medium | Q10 F3 가속도 — microsoft·spacex·tesla 단일 성장률로 acceleration=pass | 승계 | 긴장 → 2026-11 |
| medium | TSMC net_cash open_questions 가 "내역 없음" 이라 적는데 주석 35 에 담보 CD 129.40 NT$백만 | 문서 | FIX-53 2단계. P2 밴드 불변 |
| low | Meta·NVIDIA TTM 경로 1백만 차 | 기록 | 조치 없음 |

**"이미 저장소 안에 있었다" 일곱 번째.** 보존 20-F 에 한 문장으로 있었고, CASH-FCF-35 에서 cash 를 순수 현금으로 확정하며 6.4 를 인용했지만 같은 6.4 의 "확정 미인출 여신" 쪽은 아무도 찾지 않았다.

## D 출력·가독성 — 2차 건너뜀

RC-06 으로 초안 렌더러를 고치는 중이라 현재 draft 는 버려질 판본이다. **3차에서 처음 돈다.**

## 운영

- codex 가 part 를 PowerShell 기본 인코딩으로 먼저 써서 한글이 `?` 로 깨진 중간본이 한 번 보였다. 스스로 UTF-8 로 다시 쓰고 검증했다. 다음 프롬프트에 "UTF-8(BOM 없음)" 명시.
- A+2 재판정(J) codex 착수. qwen 은 A 끝난 뒤 J.
