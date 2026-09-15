# FIX-53 2단계 기록

## Meta·NVIDIA TTM 1백만 경로차 (2차 리뷰 B, low — 기록만)

`revenue_ttm` 을 두 경로(G1-FILL-27 분기 태그 합 · F6-SPEC-18 YTD 태그)로 재구성하면 meta·nvidia 만 1백만 차이가 난다. 원인은 회사 XBRL 안의 분기 태그 합과 상반기 YTD 태그가 이미 1백만 다르기 때문이며(`validation/f6-reg-28/REPORT.md` 1.1절 · 관측 `basis.cross_check_f6_spec_18`), 점수에 닿지 않는다. 고치지 않는다.

## G3 경계 표시 — alibaba 는 허용폭 밖

지시는 alibaba 런웨이(기준 3년 대비 +3.3%)에 G3 경계 표시를 붙이라는 것이었다. P4 와 같은 방식(`rules.f6_threshold_boundary_flag`, `boundary_tolerance` 0.03)을 G3 에 붙였고, **alibaba 는 `distance_ratio` +0.0332 로 허용폭 ±3% 밖이라 flag 가 false** 다. 허용폭을 자리마다 달리하지 않는다는 원칙(rules.py 주석)대로 두고, 초안 ⑨ 산식 칸에 `런웨이 3.10년(임계 3년 대비 +3.3%)` 로 거리를 보이게 했다. spacex-xai 는 -3.6% 로 역시 허용폭 밖이다.

## 인용 정정 — `고객에 투자 안 함`

Gemini 판정문·지시서는 채점표 945행으로 적었으나 문구는 `AI기업_채점표_v1.5.md` **243행**에 있다(945행은 기타(Astra) 벤치마크 표 행). tsmc.F5.strict54 는 243행을 인용한다.
