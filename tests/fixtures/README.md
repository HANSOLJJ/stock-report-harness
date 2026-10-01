# 수집기 테스트 픽스처

- `google_news_rss.sample.xml`. 2026-09-30 실제 조회 1회(질의 `NVIDIA`) 결과를 item 5개로 줄인 것이다. 실측이다.
- `edgar_submissions.CIK0001045810.sample.json`. 실응답(조회일 2026-10-01, `filings.recent` 1000건 중 앞 20건으로 줄임, 키 구조 그대로). 앞 20건에 `DEFAULT_FORMS` 밖 형식(`4`·`144`·`3`·`N-PX`)이 있어 거름망을 검사한다. `parse_submissions` 결과는 2건(8-K·10-Q)이다.
- `company_tickers.sample.json`. 실응답(조회일 2026-10-01, 10431행 중 12개사 행만 남겨 줄임, 키 구조 그대로). SPCX는 실응답에 등재되어 있어 포함한다(CIK 1181412).
- `yfinance_quotes.sample.json`. `fetch_quote` 반환 형식(`close`·`close_date`·`market_cap`·`shares_outstanding`·`currency`)으로 상장 12개사 값을 담았다. NVDA 1건만 2026-09-29 실측(종가 227.210007, 시총 5486440032119.751, 발행주식 24147000000, USD)이고 나머지는 합성이다. SPCX는 시총·발행주식을 null로 두어 `collection_failed` 경로를 검사한다.
