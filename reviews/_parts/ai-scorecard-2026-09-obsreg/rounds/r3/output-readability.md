# output-readability — 출력·가독성
검토자: Gemini 3.8 Flash (High) · session e7b9a9c8 · 2026-09-15T16:53:00+09:00
결과: needs_fix
요약: 14개사의 총점·순위 및 종합 순위표의 숫자는 results.json과 완전히 일치한다. 그러나 render_html.py의 활성 판단 근거 및 F6 parameters 산식 매핑 누락, 초안 내 비상장 F6 승계 evidence 오매핑(-4 vs -3), alibaba F9 불릿 점수 모순(-3 vs -2 유지), 그리고 vendor_not_in_source_policy·stored_vs_recomputed 등 핵심 불확실성의 독자 노출 누락이 확인되어 needs_fix로 판정한다.

## 항목
| # | 항목 | 결과 | 근거(파일:행) |
|---|---|---|---|
| 1 | 초안↔결과 일치 | needs_fix | drafts/ai-scorecard-2026-09-obsreg.md:380, 762, 970 / scorecard/runs/ai-scorecard-2026-09-obsreg/results.json:344, 400 |
| 2 | 렌더 매핑 | needs_fix | scripts/scorecard/render_html.py:447, 467, 509-551, 563 / scripts/scorecard/render_md.py:324-326 |
| 3 | 불확실성 노출 | needs_fix | scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:44, 76 / scorecard/rules/v1.7.json:333-370, 901-905 |
| 4 | 낡은 비교 문장 | needs_fix | drafts/ai-scorecard-2026-09-obsreg.md:380, 762 / scripts/scorecard/render_html.py:580, 582, 603 |
| 5 | 출력 스펙 | pass | scripts/scorecard/render_html.py:787, 829-833 / scripts/build_report.py:397-400 |

## 발견 사항
- [severity: high] scripts/scorecard/render_html.py:447, 467, 818 — HTML 기업 상세 카드에서 이번 실행의 활성 판단 evidence 및 superseded 판단이 완전히 소실됨.
  `render_cards` 함수는 인자로 `judgments`를 전달받지 않으며, 카드 내부의 근거 불릿을 오직 기준선 baseline 데이터(`b.get("evidence", {}).get(f, [])[:6]`, 467행)에서만 읽어온다. 그 결과 이번 실행에서 새로 판정된 판단(`tsmc.F5.strict54`, `anthropic.F5.impl48`, `openai.F5.impl48`, `nvidia.F7.fix52`, `oracle.F7.fix52`, `anthropic.F8.f8anth33`, `alibaba.F9.obsreg25` 등)의 핵심 근거 불릿과 대체된 옛 판단(superseded) 내역이 HTML 카드에서 완전히 사라지고 과거 v1.5 기준선 서술만 노출된다. 또한 817행의 안내문(`<p class="sub">...근거 불릿은 기준선 v1.5 원문을 그대로 옮긴 과거 기록이며 이번 실행에서 재검증하지 않았다</p>`) 역시 이번 실행 판단이 반영되지 않은 결함을 정당화하는 왜곡된 서술로 남게 된다.

- [severity: high] scripts/scorecard/render_html.py:509-551, 562-565, 582, 603 — HTML 렌더러의 v1.7 F6 parameters 모드 미지원 및 낡은 v1.5 구간표 하드코딩.
  `factor_calc_text` 함수가 F6에 대해 `ntm_per` 또는 `valuation_over_arr`만 검사하고 v1.7 상장사 정본인 `parameters` 모드(`P1`, `P2`, `P3`, `p4`) 분기를 처리하지 않는다. 이로 인해 상장사 F6의 카드 산식 텍스트(`fcalc`)가 공백으로 누락된다. 또한 경계 플래그 검사(563행)가 parameters 하위의 각 지표 boundary를 탐색하지 못해 표의 경계 열(⚠️)이 항상 `—`로 표시된다. 더불어 582행("NTM PER 만 ⑥ 점수에 개입한다...")과 603행("⑥ 상장: NTM PER 20·29·42·62·90 반개방 구간...")에 낡은 v1.5 기준의 설명이 하드코딩되어 v1.7 채점 결과와 모순된다.

- [severity: high] scripts/scorecard/render_md.py:324-326, drafts/ai-scorecard-2026-09-obsreg.md:379-388, 969-979 — 비상장 F6 자동 산출 점수와 불릿 승계 evidence 간 충돌 및 유령 판단 매핑.
  `render_md.py`의 324행이 factor 결과의 `judgment_id`를 검증하지 않고 `judgments.json`에 `(company_id, factor)`가 존재하기만 하면 judgment evidence를 출력하도록 작성되어 있다. 이로 인해 v1.7 C-12에 따라 자동 산출(`basis: computed`, `judgment_id: None`)되어 점수 `-4`가 매겨진 Anthropic과 OpenAI의 F6에 대해, 과거 v1.5에서 넘어와 남아 있던 carried judgment의 evidence가 그대로 출력되었다. 그 결과 Anthropic F6는 표의 점수가 `-4`인데 불릿 첫 머리에 `- -3 (v1.5: ARR 보정 + 자본효율 반영)`이 찍히고 헤더에 `(승계 판단 anthropic.F6...)`라는 잘못된 지시어가 붙었으며, OpenAI F6 역시 불릿 헤더에 `(승계 판단 openai.F6...)`가 붙어 실제 산출 경로와 정면 충돌한다.

- [severity: medium] drafts/ai-scorecard-2026-09-obsreg.md:762, scorecard/runs/ai-scorecard-2026-09-obsreg/results.json:344 — Alibaba F9 불릿 내 낡은 점수 서술 잔존.
  Alibaba F9는 확정 미인출 여신 US$3.33B 반영으로 런웨이 3.10년이 확보되어 최종 결과 점수가 `-3`으로 산출되었다. 그러나 초안 762행의 불릿 두 번째 줄에 `- 그러나 -2 유지: CapEx RMB 67,678M(+75%)로 FCF -$6.6B`라는 낡은 점수 문구가 그대로 남아 있어 종합 순위표 및 기업 헤더의 점수(-3)와 불릿 서술(-2 유지)이 모순된다.

- [severity: medium] scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:44, 76 등 26건, drafts/ai-scorecard-2026-09-obsreg.md, scripts/scorecard/render_html.py — `vendor_not_in_source_policy` 불확실성 노출 누락.
  market_cap 12건, ntm_per 12건 등 주요 관측 자료 26건의 basis에 `vendor_not_in_source_policy: true`가 명시되어 있으나, 초안(draft), 리서치(research), HTML 대시보드 어디에도 이 플래그나 해당 관측들이 출처 정책 외 공급사 관측이라는 사실이 독자에게 노출되지 않는다.

- [severity: medium] scorecard/rules/v1.7.json:333-370, 901-905, drafts/ai-scorecard-2026-09-obsreg.md, scripts/scorecard/render_html.py — `stored_vs_recomputed` 및 `open_questions` 불확실성 노출 누락.
  규칙 파일 v1.7.json에 등록된 `stored_vs_recomputed`(nonop_share의 완제품 저장값과 재계산값 간의 11/12 불일치, 6건 부호 반전, alibaba 미해명 등)와 `policies.f6.net_cash.open_questions`(amazon·nvidia·tsmc·alibaba 차이 원인, alibaba 채무증권 비중 등)의 중대한 한계가 초안 및 HTML에 구체적으로 안내되지 않고 단순 1줄 경고로만 축약되어 독자에게 정보가 은폐된다.

- [severity: low] scripts/scorecard/render_html.py:547, scripts/scorecard/render_md.py:223-226 — HTML 렌더러의 F9 G3 런웨이 boundary 플래그 누락.
  `render_md.py`에는 FIX-53 2단계로 G3 런웨이가 임계에 근접할 때 `⚠️ 경계` 및 거리 비율을 표시하도록 추가되었으나, `render_html.py:547`의 `factor_calc_text`에는 G3의 boundary 플래그 렌더링 로직이 누락되어 대시보드에 반영되지 않는다.

- [severity: low] scripts/scorecard/render_html.py:580, drafts/ai-scorecard-2026-09-obsreg.md:1158 — HTML 지표 원자료 섹션의 부정확한 관측 출처 설명.
  초안 1158행에서는 "표마다 실측(verified)과 승계가 섞여 있다"고 바로잡았으나, HTML 580행은 여전히 "모든 값은 기준선 v1.5 승계 관측이며 이번 실행에서 재검증되지 않았다"고 서술하여 실제 포함된 다수의 SEC 실측 관측(CASH-FCF-35, NETCASH-37, F6-REG-28 등)을 가리고 있다.

## 확인 못 한 것
- HTML 빌드 산출물의 실제 브라우저 렌더링 화면 및 JS 정렬·인터랙션 동작 (승인 전 빌드 금지 및 HTML 파일 임의 생성 금지 규칙에 따라 빌드 스크립트를 실행하지 않고 소스 코드 정적 분석으로만 검증함).
