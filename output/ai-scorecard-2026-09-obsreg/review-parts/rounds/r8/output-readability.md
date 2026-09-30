# output-readability — 출력·가독성
검토자: Gemini 3.8 Flash (8차 라운드 독립 리뷰 세션 · 2026-09-17)
결과: pass
요약: 초안과 결과 JSON의 14개사 순위·점수·산식·근거 헤더 126개가 100% 일치하며, 렌더러 소스 매핑 및 불확실성 노출(승계·미검증·정책밖원천·이해상충), 낡은 비교 문장 부재, 단일 HTML·모바일 반응형 스펙이 모두 규격에 부합합니다.

## 항목
| # | 항목 | 결과 | 근거(파일:행) |
|---|---|---|---|
| 1 | 초안↔결과 일치 | pass | 종합 순위표 14개사 순위·팩터·소계·총점 전수 일치(`drafts/ai-scorecard-2026-09-obsreg.md:38-51` vs `scorecard/runs/ai-scorecard-2026-09-obsreg/results.json:28-200`). 14개사 126개 factor의 점수·상태·basis·산식 텍스트 전수 일치(`drafts:61-1149` vs `results.json:33-4450`). F5 2건(anthropic `drafts:334`, `results.json:1946-1961` / openai `drafts:976`, `results.json:4165-4180`), F7 2건(nvidia `drafts:614`, `results.json:2688-2701` / oracle `drafts:1089`, `results.json:3870-3883`), anthropic F6(-4점, `drafts:335`, `results.json:1962-2057`) 및 근거 블록 헤더 126건 전수 일치 확인. |
| 2 | 렌더 매핑 | pass | `carried_score`의 승계 라벨 및 경고 4건 매핑(`scripts/scorecard/render_html.py:468-472`, `scripts/scorecard/render_md.py:13`), `pending` 메시지 산식 결합 및 미결 결정 노출(`scripts/scorecard/render_common.py:292-295, 314-317`, `render_html.py:424-437`), `unavailable` 라벨 사전 등록(`render_html.py:30`), `superseded` 판단의 취소선 및 교체 사유 매핑(`render_common.py:64, 202-207`), `boundary` 3% 경계 플래그의 표·산식 매핑(`render_common.py:235-241, 254, 265`, `render_html.py:513`), P4 `demotion_sole_cause` 강등 원인 명시(`render_common.py:262-263`)가 모두 정상 작동함. |
| 3 | 불확실성 노출 | pass | 승계 판단의 기준선·원검토일·미재검증 경고 노출(`render_common.py:198-200`, `drafts:77, 84`), `legacy_unverified` 203건 건수 및 열별 상태 요약(`render_common.py:329-345, 356-362`, `drafts:1171, 1190, 1222`), 원천 정책 밖 공급사 값 26건의 `†` 마크 및 P1·P2 실측 전 안내(`render_common.py:350-354, 381-393`, `render_html.py:515, 535`, `drafts:1192`), 채점규칙 384행 이해상충 고지 및 제3자 재검토 약속 4건·일부2건·권장3건·C-03 발동 조건 공개(`scorecard/rules/v1.7.json:384`, `drafts:30, 1280-1284`, `render_html.py:741-744`, `render_common.py:477-517`), `stored_vs_recomputed` 영업외 비중 차이(`render_common.py:523-531`, `drafts:1276`), `open_questions` 순현금 남은 질문 3건(`render_common.py:532-540`, `drafts:1277-1279`)이 온전히 노출됨. |
| 4 | 낡은 비교 문장 | pass | 초안·연구·계획 문서 전수 대조 결과 현재 결과와 모순되는 과거 점수·순위 문장 없음. 기준선 v1.5 순위 14개사 병기 수치가 `scorecard/baseline/v1.5/companies.json`의 `rank_raw`와 전수 일치(`drafts:57-1081`). 점수 변경 5건(anthropic F5 4점, openai F5 1점, nvidia F7 -2점, oracle F7 -2점, anthropic F6 -4점)과 nvidia P2 변경(17.7x)이 개요·본문·원자료에 온전히 반영됨(`drafts:24-27, 334-335, 613-614, 660-661, 976, 1026-1037, 1089, 1138-1139`). 연구 문서(`research/ai-scorecard-2026-09-obsreg.md:12-654`)는 정형 테이블로 구성되어 충돌 서술 없음. |
| 5 | 출력 스펙 | pass | 면책·투자 유의 문구가 표준 상수로 정의되어 초안 및 HTML 푸터에 온전히 반영됨(`render_html.py:801-805`, `render_md.py:39`, `drafts:1331-1332`). 외부 JS 의존성 없는 단일 파일 HTML 대시보드 구조(`render_html.py:755-815`). 모바일 반응형 뷰포트, KPI auto-fit, 1180px 이하 sticky 헤더/첫두열 고정 가로 스크롤, 640px 모바일 전용 비필수 열 숨김 및 카드 안내 처리 완비(`render_html.py:78-285`). AI Scorecard 계약에 따른 hero 이미지 비필수 처리 준수(`AGENTS.md:AI Scorecard 계약`, `scripts/build_report.py:902-905`, `render_html.py:732-815`). |

## 발견 사항
- [severity: low] drafts/ai-scorecard-2026-09-obsreg.md:381-385 — Anthropic F6 상세 불릿 첫 머리에 `기준선 v1.5 서술(참고 — 이번 실행은 입력에서 자동 산출, 원문 판단은 미적용):` 라벨과 함께 과거 서술인 `-3 (v1.5: ARR 보정 + 자본효율 반영)` 문구가 표시됩니다. 이는 judgment_id가 없는 자동 산출 팩터에 대해 과거 기준선 서술을 참고용으로 인용하는 렌더 규칙(`scripts/scorecard/render_common.py:190-195`)에 따른 정상 동작이며 상단 표(`drafts:335`)에는 `-4`가 정확히 명시되어 있으나, 독자가 서술문의 과거 수치(-3)와 현재 산출 점수(-4)를 혼동하지 않도록 라벨이 기능하고 있음을 확인했습니다.
- [severity: low] scripts/scorecard/render_html.py:741-744 — HTML 상단 헤더의 Anthropic 이해상충 알림 문구에서 `과점 factor {fmt_score(c["moat"])}점`으로 동적 연산하여 현재 과점 점수인 20점(`drafts:27`과 동일)이 정확히 노출되도록 구현되어 있음을 확인했습니다.

## 확인 못 한 것
- 빌드 스크립트 실행 금지 및 사전 승인 전 규칙에 따라 `python scripts/build_report.py ai-scorecard-2026-09-obsreg`를 실제로 구동하여 생성된 `output/ai-scorecard-2026-09-obsreg.html` 파일의 브라우저 시각 렌더링 화면을 직접 육안으로 확인하지는 않았습니다. 이는 렌더러 소스 코드 정적 분석 및 가상 데이터 매핑 대조로 전수 검증했습니다.
