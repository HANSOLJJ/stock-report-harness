# SRC-TRACE-47: 25쌍의 상류 원천을 v1.5 원본 문면으로 추적하고 원천 정책 등재 여부를 판정한다.
# 문면이 없으면 미기재로 두고 추정하지 않는다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(io.open(os.path.join(HERE, "targets-25.json"), encoding="utf-8"))["items"]

# 원본 위치와 상류 문면. 절 제목에 박힌 출처가 그 절 전체 표의 상류다.
SRC = {
  "market_cap": dict(
    loc="채점표 L794 절 제목 + L807~820 표",
    quote="### 3-1a. 가격 — ⑥ 원자료 (StockAnalysis · 2026-09-02 종가 · 단일 출처)",
    upstream="StockAnalysis", policy="없음"),
  "net_cash": dict(
    loc="채점표 L848 절 제목 + L851~ 표 '순현금/순부채' 열",
    quote="### 3-1a-3. 통합 재무 전수표 — ⑨ 게이트 원자료 (StockAnalysis 9/2 + 공시)",
    upstream="StockAnalysis 9/2 + 공시", policy="혼합"),
  "ps_ratio": dict(
    loc="규칙 L649~651 'TTM 매출 배수 추정' 표 · 채점표 L930~931",
    quote="(출처 표기 없음 — 밸류÷ARR 을 TTM 으로 보정한 유도값)",
    upstream="미기재", policy="판정 불가"),
  "arr": dict(
    loc="규칙 L664~667 자본효율 표 · 채점표 L923~926",
    quote="(출처 표기 없음)", upstream="미기재", policy="판정 불가"),
  "arr_prior": dict(
    loc="채점표 L341(anthropic) · 규칙 L165·채점표 L745(openai)",
    quote="(출처 표기 없음)", upstream="미기재", policy="판정 불가"),
  "cumulative_raised": dict(
    loc="규칙 L666~667 · 채점표 L925~926",
    quote="(출처 표기 없음)", upstream="미기재", policy="판정 불가"),
  "post_money_valuation": dict(
    loc="채점표 L930~931 밸류÷ARR 표",
    quote="(출처 표기 없음 — 괄호는 라운드 설명이지 출처가 아님)",
    upstream="미기재", policy="판정 불가"),
  "offbalance_B": dict(
    loc="규칙 L543·L564·L579 · 상류는 HANDOVER L44 레지스트리",
    quote="| **부외 약정** | 10-K/10-Q 주석(리스 약정·구매 약정) · 셀사이드(Morgan Stanley) |",
    upstream="10-K/10-Q 주석 · 셀사이드(Morgan Stanley)", policy="혼합"),
  "contracted_revenue": dict(
    loc="채점표 L543 · 상류는 HANDOVER L45 레지스트리",
    quote="| RPO · 백로그 | 실적 발표 | Remaining Performance Obligation |",
    upstream="실적 발표", policy="귀속 불명"),
}
# 개별 예외 — 직접 계산이라고 원문이 밝힌 둘
DIRECT = {
  ("market_cap", "tsmc"): "채점표 L822 ✱ 'TSMC는 전부 직접 계산 — ADR 5.19B주 × $415.5 = $2.15T'. "
                          "주가 $415.50 은 같은 절(StockAnalysis) 표에서 온다",
  ("market_cap", "alibaba"): "채점표 L823 ✱ '시총은 8/26 증자(710M주) 완료 반영, ADS 24.2억 주'. "
                             "주가 $111.76 은 같은 절(StockAnalysis) 표에서 온다",
}

rows = []
for t in T:
    s = SRC[t["metric"]]
    note = DIRECT.get((t["metric"], t["company_id"]))
    rows.append({**t, "source_location": s["loc"], "upstream_quote": s["quote"],
                 "upstream": s["upstream"], "policy_status": s["policy"],
                 "direct_calc_note": note})

io.open(os.path.join(HERE, "trace-25.json"), "w", encoding="utf-8").write(
    json.dumps({"count": len(rows), "items": rows}, ensure_ascii=False, indent=1))

print("%-20s %-11s %-38s %s" % ("metric", "company", "상류 원천(문면)", "등재"))
print("-" * 96)
for r in rows:
    print("%-20s %-11s %-38s %s%s" % (r["metric"], r["company_id"], r["upstream"][:38],
                                      r["policy_status"], " ★직접계산" if r["direct_calc_note"] else ""))
from collections import Counter
print()
print("등재 판정 분포:", dict(Counter(r["policy_status"] for r in rows)))
print("상류 분포   :", dict(Counter(r["upstream"] for r in rows)))
