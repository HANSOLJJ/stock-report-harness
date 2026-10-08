# 새 관측 수집 지시서 (2026-10 v2.0 재실행)

① 네 질문과 ③ 지표 단계에 쓸 숫자 관측을 공시에서 읽어 등록한다. 회사 묶음(A nvidia·tsmc·apple / B alphabet·amazon·microsoft / C meta·oracle·palantir / D anthropic·openai / E alibaba·tesla·spacex-xai)마다 한 세션이 맡는다. 10월 실행에서 Oracle·TSMC·Alibaba 재무 관측 29건을 만든 방식과 같다(`.agents/plans/rescore-2026-10/context-notes.md` 2026-10-06 "재무 관측 갱신").

## 지표

| metric | 단위 | 어디서 | 대상 |
|---|---|---|---|
| `gross_margin_ttm`, `gross_margin_ttm_prior` | ratio | 10-Q·10-K 손익계산서(매출총이익 ÷ 매출, 최근 1년과 그 전 1년). TSMC·Alibaba 는 6-K/20-F | 상장 12사 |
| `top_customer_share` | ratio | 10-K 고객 집중 공시(매출 10% 이상 고객 중 최대) | 공시하는 회사 |
| `rpo_next12m_share` | ratio | 10-K 수익 인식 주석(RPO 중 12개월 내 인식 비중) | 상장 |
| `nrr` | ratio | 실적 자료(순매출 유지율) | Palantir 등 공개하는 회사 |
| `customer_prepayments` | USD | 재무상태표(고객으로부터의 임시 수령액·선급금) | TSMC 등 |
| `paid_seats` | count | 실적 발표(Copilot 유료 좌석 등) | Microsoft 등 |
| `mau` | count | 실적 발표(Gemini 앱·Meta AI 월간 사용자). **시계열로 둘 이상** | Alphabet·Meta 등 |
| `developer_count` | count | 10-K Item 1·개발자 행사 공식 발표(CUDA 개발자 수) | NVIDIA 등 |
| `token_share`, `price_per_m` | ratio, USD | OpenRouter 공개 통계(모델별 토큰 점유율·$/M). 두 시점 이상 | Anthropic·OpenAI·Alphabet·Alibaba 모델 |
| `fsd_subscribers` | count | 실적 발표 | Tesla |
| `shares_diluted`, `sbc_ttm` | count, USD | 10-Q·10-K | 상장 12사(자본 효율 진단 예비) |

## 규율 (AGENTS.md 「원자료 조사 규율」)

- 밖에서 찾기 전에 `data/_sec/docs/` 캐시를 먼저 연다. 없으면 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <SEC 주소>` 로 받는다. SEC_UA 값을 다른 데 쓰지 않는다.
- 값·문언·인용 위치를 셋 다 확인한다. `raw` 에 원문 발췌, `note` 에 페이지·표 이름을 적는다.
- 재무표는 열 머리글에서 축을 먼저 확정한다. 최신이 맨 왼쪽이라고 가정하지 않는다.
- 같은 제출본 안에서 수치가 갈리면 감사 재무제표 본문을 우선한다.
- 없는 것은 세 갈래로 가른다. 회사가 공시하지 않음이 확인되면 `status: not_disclosed` 와 `missing_type`, 우리가 못 찾았으면 등록하지 않고 보고에 적는다. 0 으로 채우지 않는다.
- 추세용 지표(`mau`·`token_share`·`gross_margin_ttm`)는 `as_of` 가 다른 관측을 둘 이상 등록한다. 한 시점 숫자는 가속도·회수 루프 판정에 못 쓴다.
- 출처는 `sources.json` 에 등록하고(`source_id`, URL, sha256, 접근일) 관측이 그 ID 를 가리킨다. 실적 콜 자료는 회사 IR 사이트 URL 로.

## 출력

스크래치 `work/obs-<묶음>.json` 에 `observations.json` 항목 모양 그대로(`observation_id`, `company_id`, `metric`, `value`, `unit`, `as_of`, `kind: actual`, `source_id`, `status: verified`, `raw`, `note`)와 새 출처 목록을 낸다. 조율자가 독립 검산(성분 부호·환산·원문 존재) 뒤 합친다. 마지막 답변에 회사별로 등록한 지표, 공시 없음으로 확인한 지표, 못 찾은 지표를 표로 적는다.
