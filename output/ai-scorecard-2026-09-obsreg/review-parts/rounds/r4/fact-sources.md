# fact-sources — 사실·출처
검토자: qwen (Qwen Code CLI 세션, 2026-09-15T19:xx KST)
결과: pass
요약: verified 관측 105건 전수를 companyfacts 원자료·산술·통화환산으로 대조했고, legacy_unverified 24건의 source_vendor 표시를 v1.5 채점표 794행·HANDOVER 33~45행과 확인했으며, judgments 인용 행 번호 12건을 원문에서 검증했다. 점수 경로에 닿는 사실 오류를 찾지 못했다.

## 체크리스트
| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q05 | pass | 승계 판단 2건(nvidia.F2 벤더 보도자료, openai.F4 OpenAI 발표)이 이해당사자 출처를 쓰나, 판단 note 에서 명시적으로 flag 하고 TEN-RA-02·TEN-RA3-01 로 등록됨(v1.7.json:1730~ open_tensions). 새 관측·판단 중 미flag 이해당사자 출처 없음. verified 105건 전부 SEC 공시(중립 규제 원천) 또는 StockAnalysis(제3자). |
| Q09 | pass | nvidia.F2 Vera Rubin(미래 제품)·openai.F4 배치 계획이 근거에 포함되나 `(발표)`·`(계획)` 라벨 부착됨(judgments.json openai.F4 evidence 마지막 항). anthropic.F8 은 2028~2030 칩 계획을 점수에 넣지 않고 "당분간 −3 유지"로 명시(judgments.json anthropic.F8.f8anth33 evidence). TEN-RA-02·TEN-RA3-01 등록. |
| Q14 | pass | F3 점수 전수 2~3(results.json companies[].factors.F3.score). 상한 4 규칙(v1.7.json checklist Q14 case "문이 닫힌 증거 없으면 상한 4점") 위반 없음. TEN-RB-Q10·TEN-RC3-05 등록으로 F3 측정 한계 문서화. |
| Q23 | not_applicable | 조율자 분담 — 별도 세션 |

## 발견 사항
- [severity: low] observations.json legacy_unverified — 과제 지시는 "25쌍"을 언급하나 실제 `source_vendor` 표시가 있는 legacy_unverified 관측은 24건(StockAnalysis 20 + author_computed 4). 12개사 × 2개 지표(market_cap, ntm_per) = 24 로 전수 일치하며, 25번째 후보를 특정하지 못함. 점수 경로 영향 없음(v1.7 parameters 모드는 ntm_per 를 읽지 않음 — alibaba.ntm_per.v15 basis.not_read_by_engine).
- [severity: low] judgments.json anthropic.F8.f8anth33 — SEC 8-K accession 4건(0001018724-25-000002 등)을 인용하나 이 accession 은 AMZN companyfacts 에 없음(8-K 는 XBRL 재무데이터 미포함, 예상된 동작). 보존 원문 `3cf9799:validation/offb-24/_raw/amzn-20260630.htm` 은 이 트리에 없어 인용 문면("Trainium2 powers Project Rainier…")의 원문 대조 불가. 판단 자체는 Amazon 10-Q Note 1 공시(보존 원본 존재)와 독립적으로 정합.

## 확인 못 한 것
- anthropic.F8 판단이 인용한 SEC 8-K 원문 문면(보존 파일이 이 트리에 없고 외부 조회 금지)
- spacex-xai S-1/A 연결재무제표 값(companyfacts 에 XBRL 미등재 — S-1/A 는 IPO 전 서류)
- tsmc 20-F IFRS 항목 일부(ifrs-full 네임스페이스가 companyfacts 에 부분적으로만 존재)
- legacy_unverified "25쌍" 중 25번째 항목의 정체(24건은 전부 확인)
