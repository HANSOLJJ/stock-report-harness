# SRC-POLICY-32: sources 블록 제안본을 현재 v1.7 에서 파생해 생성한다.
# worker 가 v1.7.json 을 미커밋 수정 중이므로 적용하지 않고 제안 파일로만 낸다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "C:/Users/noble/orca/workspaces/stock-report-harness/worker/scorecard/rules/v1.7.json"
cur = json.load(io.open(SRC, encoding="utf-8"))["sources"]
s = json.loads(json.dumps(cur, ensure_ascii=False))  # deep copy

D = "2026-09-11"

# ---- 1. usage_scope: 단일 scope → scopes 배열 --------------------------------
old_note = s["usage_scope"].get("note", "")
s["usage_scope"] = {
    "scopes": ["personal_internal_only", "corporate_internal_only"],
    "decided_at": D,
    "statement": (
        "이 저장소의 산출물(점수·판정·HTML 리포트·파생 자료)은 개인 투자 참고 열람과 "
        "사용자가 대표로 있는 회사의 내부 업무에 모두 쓰인다. 둘 다 실제 사용이므로 둘 다 선언한다. "
        "외부 일반 대중 배포는 여전히 전제하지 않는다."),
    "condition": (
        "산출물을 외부에 배포하면 이 전제가 깨진다. 그때는 원천별로 재배포 라이선스를 다시 확보해야 하고 "
        "allowed·denied·not_adopted 를 전부 재검토해야 한다. 배포 여부가 바뀌면 이 선언을 먼저 고친다."),
    "evaluation_rule": (
        "scopes 는 합집합이다. 어떤 원천이 적격이려면 그 라이선스가 scopes 의 **모든** 원소를 허용해야 한다. "
        "하나라도 금지하면 부적격이다. 따라서 범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다. "
        "개인 사용을 더해도 corporate_internal_only 가 범위에 남아 있는 한 법인 금지 조항은 그대로 적용된다."),
    "note": (
        "2026-09-11 에 단일 scope 에서 scopes 배열로 바꿨다(SRC-POLICY-32, 사용자 확정). "
        "이전 값은 corporate_internal_only 단일이었다. 과거 파일 호환을 위해 단일 scope 키도 계속 읽는다 — "
        "읽을 때 1원소 집합으로 승격한다. v1.5 는 sources 블록 자체가 없어 영향이 없다. "
        "이 선언은 원천별 이용 조건을 대체하지 않는다. 각 host 의 robots.txt 와 이용약관이 여전히 우선하고, "
        "법인이든 개인이든 robots.txt 의 전면 Disallow 를 무르지 않는다 — denied 의 api.nasdaq.com 을 보라. "
        "이전 note 보존: " + old_note),
}

# ---- 2. allowed 의 finnhub·fmp note 갱신 -------------------------------------
FINNHUB = (
    "API 키 발급 기반. 무료 등급 분당 60콜 | **약관 확인 완료(2026-09-11, NTM SRC-POLICY-32). "
    "확인 결과 우리 사용 형태가 무료·개인 플랜 범위 밖이다.** ToS 'Redistribution Rights and Personal Use' 가 "
    "'All plan listed on Finnhub website is strictly for personal use unless explicitly stated otherwise. "
    "Personal plan can't be used by any business even internally without a written approval.' 로 "
    "**법인 내부 사용을 명시적으로 배제**한다('even internally'). 같은 절의 부적격 사유 목록도 "
    "'You are using this data for your business or registering under your business name regardless of the industry' 를 든다. "
    "또 'not redistribute or share access to data or derived results from the data ... without written approval' 로 "
    "**파생 결과의 공유까지** 제한한다. usage_scope 가 corporate_internal_only 를 포함하므로 무료 등급 전제가 깨진다. "
    "쓰려면 written approval 경로다. robots.txt 는 'Disallow: /terms-of-service' 이나 PRIV-ARR-17 표준에 따라 "
    "약관 확인 목적 조회로 열람했고 원문을 보존했다(validation/src-policy-32-2026-09-11/raw/). "
    "현재 F6 재정의에서는 쓰지 않는다 — SEC 만 쓴다.")
FMP = (
    "API 키 발급 기반. 무료 등급 250콜/일 | 상태 고지(2026-09-11 갱신, NTM SRC-POLICY-32). "
    "약관 §2.2.1 이 'This license may only be used by a Customer who is an individual... "
    "In no event may the Customer use this licence on behalf of a company' 로 법인 대리 사용을 배제한다. "
    "**usage_scope 에 personal_internal_only 를 더해도 이 사유는 철회되지 않는다** — scopes 가 합집합이라 "
    "corporate_internal_only 가 남아 있는 한 'In no event' 조항이 그대로 적용된다. "
    "§2.2 본문이 Order Form·계정에 명시된 라이선스를 말하므로 유료 등급은 다른 조건일 수 있어 host 자체가 "
    "부적격이라는 뜻은 아니다. 강등하지 않고 상태만 기록한다(사용자 결정). 현재 F6 재정의에서는 쓰지 않는다 — SEC 만 쓴다.")
for e in s["allowed"]:
    if e["host"] == "finnhub.io":
        e["note"] = FINNHUB
    elif e["host"] == "financialmodelingprep.com":
        e["note"] = FMP

# ---- 3. data.nasdaq.com: conditional_candidates → not_adopted ----------------
cc = s.pop("conditional_candidates", [])
closed = []
for e in cc:
    if e.get("host") == "data.nasdaq.com":
        closed.append({
            "name": e.get("name"),
            "host": "data.nasdaq.com",
            "status": "not_adopted",
            "decided_at": D,
            "decided_by": "사용자",
            "reason_type": "cost",
            "reason": ("구독가 연 1,200 달러가 확인돼 사용자가 채택을 접었다. 약관 위반이나 기술적 부적격이 아니라 "
                       "비용 대비 효용 판단이다. denied 와 성격이 다르다 — denied 는 우리가 쓸 자격이 없는 것이고 "
                       "not_adopted 는 쓸 수 있으나 안 쓰기로 한 것이다."),
            "reopen_condition": ("가격이 바뀌거나 사용자가 예산을 승인하면 그때 다시 연다. "
                                 "그 전에는 D1~D5 를 다시 조사하지 않는다 — 조건이 미충족인 것이 아니라 결정이 끝났다."),
            "prior_investigation": "validation/datalink-14-2026-09-10/REPORT.md (NTM DATALINK-14, 2026-09-10)",
            "note": e.get("note", ""),
        })
    else:
        closed.append(e)
s["not_adopted"] = closed

# policy_note 에 not_adopted 설명 추가
s["policy_note"] = s["policy_note"].replace(
    "unlisted 는 문서 항목이고 source_violation() 은 읽지 않는다",
    "not_adopted 는 **검토를 마치고 안 쓰기로 결정한 host** 다. conditional_candidates 를 대체한다 — "
    "'조건만 갖추면 쓸 수 있다' 로 읽혀 같은 조사가 반복됐기 때문이다. 결정 일자와 결정 주체와 재개 조건을 함께 적는다. "
    "denied 와 다르다 — denied 는 자격이 없는 것이고 not_adopted 는 자격은 있으나 안 쓰기로 한 것이다. "
    "unlisted 는 문서 항목이고 source_violation() 은 읽지 않는다")

io.open(os.path.join(HERE, "proposal-sources-v1.7.json"), "w", encoding="utf-8").write(
    json.dumps({"_comment": "SRC-POLICY-32 제안본. 적용하지 않음 — worker PRIV-IMPL-31 충돌 회피.",
                "sources": s}, ensure_ascii=False, indent=1))

print("제안본 생성됨. 구조 변경 요약")
print("  usage_scope.scope(단일) → usage_scope.scopes(배열) + evaluation_rule 신설")
print("  conditional_candidates → not_adopted (status/decided_at/decided_by/reason_type/reopen_condition)")
print("  allowed[finnhub].note  → 약관 확인 완료 + 법인 내부 사용 배제 확인")
print("  allowed[fmp].note      → 철회 안 됨 사유 명시")
print()
print("키 비교")
print("  이전:", sorted(cur.keys()))
print("  제안:", sorted(s.keys()))
