# 수집기 테스트 픽스처

- `google_news_rss.sample.xml`. 2026-09-30 실제 조회 1회(질의 `NVIDIA`) 결과를 item 5개로 줄인 것이다. 실측이다.
- `edgar_submissions.CIK0001045810.sample.json`. 합성, 실제 응답으로 교체 필요. `SEC_UA`가 환경에 없어 실제 조회하지 않았다. SEC submissions 형식(`filings.recent` 병렬 배열)을 따르며 10건을 담았다. `DEFAULT_FORMS` 밖 형식(`S-8`) 1건을 포함해 거름망을 검사한다.
- `company_tickers.sample.json`. 합성, 실제 응답으로 교체 필요. SEC `company_tickers.json` 형식(일련 키에 `cik_str`·`ticker`·`title`)을 따르며 상장 11개사 티커를 담았다. SPCX는 뺐다. `resolve`의 `not_found` 경로를 검사한다.
- `yfinance_quotes.sample.json`. `fetch_quote` 반환 형식(`close`·`close_date`·`market_cap`·`shares_outstanding`·`currency`)으로 상장 12개사 값을 담았다. NVDA 1건만 2026-09-29 실측(종가 227.210007, 시총 5486440032119.751, 발행주식 24147000000, USD)이고 나머지는 합성이다. SPCX는 시총·발행주식을 null로 두어 `collection_failed` 경로를 검사한다.
