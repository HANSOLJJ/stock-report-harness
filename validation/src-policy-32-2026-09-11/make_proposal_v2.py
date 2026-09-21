# SRC-POLICY-32 v2: 검토에서 확정된 처리를 반영한다.
# 초판 제안은 Finnhub·FMP 를 allowed 에 남겼으나 설계진행이 세 원천을 내리기로 확정했다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
base = json.load(io.open(os.path.join(HERE, "proposal-sources-v1.7.json"), encoding="utf-8"))["sources"]
s = json.loads(json.dumps(base, ensure_ascii=False))
D = "2026-09-11"

# 내릴 host 의 기존 note 를 보존해 옮긴다
prior = {e["host"]: e.get("note", "") for e in s["allowed"]}
DEMOTE = {"finnhub.io", "financialmodelingprep.com"}
s["allowed"] = [e for e in s["allowed"] if e["host"] not in DEMOTE]

# policy_note 에 relist_condition 설명 추가
s["policy_note"] = s["policy_note"].replace(
    "unlisted 는 **검토를 마치고 안 넣기로 한 host** 만 담는다.",
    "unlisted 는 **검토를 마치고 안 넣기로 한 host** 만 담는다. 되살릴 조건이 있으면 relist_condition 에 적는다 — "
    "다음 사람이 '왜 뺐나' 를 되묻지 않게 하고, 조건이 바뀌었을 때만 다시 열게 한다.")

NEW = [
    {
        "host": "www.alphavantage.co",
        "reason_type": "both",
        "reason": ("기술 — 향후 분기 전망이 2개뿐이고 basis 4필드(currency·share_basis·accounting·asOf)가 응답에 없어 "
                   "F6 이 요구하는 미발표 4개 분기를 만들 수 없다. "
                   "약관 — ToS §2.a 무료 라이선스가 'for personal, non-commercial use' 이고 "
                   "'Usage falls under commercial use if any of the following criteria apply' 의 ii 가 법인 명의·대리 사용이다. "
                   "usage_scope.scopes 에 corporate_internal_only 가 있는 한 해당한다."),
        "decided_at": D,
        "evidence": "validation/av-source-11/REPORT.md (기술·약관), NTM SRC-POLICY-32 (범위 합집합 판정)",
        "relist_condition": ("둘 다 풀려야 한다. (1) 기술 — 향후 분기 4개와 basis 4필드가 확인돼야 한다. "
                             "(2) 약관 — usage_scope 를 personal_internal_only 전용으로 좁히거나 "
                             "premium@alphavantage.co 상업 계약을 맺어야 한다. 하나만 풀리면 여전히 부적격이다."),
        "note": "무료 키 발급 자체가 §2.a 범위 밖이므로 키부터 받고 보는 순서로 가지 않는다.",
    },
    {
        "host": "financialmodelingprep.com",
        "reason_type": "both",
        "reason": ("기술 — 무료 등급에서 period=quarter 가 유료 파라미터로 막혀 회계분기 컨센서스를 받을 수 없다(HTTP 402). "
                   "F6 이 필요로 하는 유일한 형태가 그것이라 12종목 0/12 다. "
                   "약관 — §2.2.1 이 'This license may only be used by a Customer who is an individual... "
                   "In no event may the Customer use this licence on behalf of a company' 로 법인 대리 사용을 배제한다. "
                   "scopes 가 합집합이라 personal_internal_only 를 더해도 이 조항은 철회되지 않는다."),
        "decided_at": D,
        "evidence": "validation/fmp-estimates-02/REPORT.md, validation/f6h-source-batch-10/REPORT.md, NTM SRC-POLICY-32",
        "relist_condition": ("둘 다 풀려야 한다. (1) 기술 — period=quarter 접근권. "
                             "(2) 약관 — usage_scope 를 personal_internal_only 전용으로 좁히거나 "
                             "§2.2 의 Order Form 경로로 법인 라이선스를 맺어야 한다."),
        "note": "이전 allowed note 보존: " + prior.get("financialmodelingprep.com", ""),
    },
    {
        "host": "finnhub.io",
        "reason_type": "both",
        "reason": ("기술 — basis 미확인으로 F6 채점에 쓸 수 없는 상태였다. "
                   "약관 — ToS 'Redistribution Rights and Personal Use' 가 "
                   "'Personal plan can't be used by any business even internally without a written approval' 로 "
                   "법인 내부 사용을 명시적으로 배제한다. 더해서 "
                   "'not redistribute or share access to data or derived results from the data ... without written approval' 로 "
                   "**파생 결과의 공유까지** 제한한다 — 우리 채점표·HTML 리포트가 바로 파생 결과다. "
                   "다른 둘은 사용 주체만 제한하는데 Finnhub 은 산출물의 유통까지 제한한다."),
        "decided_at": D,
        "evidence": ("NTM SRC-POLICY-32 — 2026-09-11 약관 원문 최초 조회·보존 "
                     "(validation/src-policy-32-2026-09-11/raw/finnhub-terms-of-service.html). "
                     "PRIV-ARR-17 표준(약관 문서는 확인 목적 조회 허용)을 적용했다."),
        "relist_condition": ("셋이 풀려야 한다. (1) 기술 — basis 확인. "
                             "(2) 약관·주체 — usage_scope 를 personal_internal_only 전용으로 좁히거나 written approval. "
                             "(3) **약관·유통 — 파생 결과 공유에 대한 written approval 을 별도로 받아야 한다.** "
                             "(3)은 다른 두 원천에 없는 조건이라 usage_scope 를 좁히는 것만으로는 해소되지 않는다."),
        "note": ("2026-09-11 이전까지 allowed 에 등재된 채 약관을 한 번도 확인하지 않은 상태였다. "
                 "robots.txt 의 'Disallow: /terms-of-service' 가 확인을 막는 구조였고 "
                 "PRIV-ARR-17 표준이 이미 그 경로를 열어 뒀으나 이 건에 연결되지 않았다. "
                 "이전 allowed note 보존: " + prior.get("finnhub.io", "")),
    },
]
s["unlisted"] = list(s.get("unlisted") or []) + NEW

io.open(os.path.join(HERE, "proposal-sources-v1.7-v2.json"), "w", encoding="utf-8").write(
    json.dumps({"_comment": ("SRC-POLICY-32 제안 v2. 검토 확정 반영본 — 세 원천을 allowed 에서 내려 unlisted 로. "
                             "초판 proposal-sources-v1.7.json 은 이 결정 이전에 만들어져 finnhub·fmp 를 allowed 에 "
                             "남겨 두었으므로 그대로 적용하면 확정과 어긋난다. 적용은 이 v2 를 쓴다."),
                "supersedes": "proposal-sources-v1.7.json",
                "sources": s}, ensure_ascii=False, indent=1))

print("allowed   :", [e["host"] for e in s["allowed"]])
print("not_adopted:", [e.get("host") for e in s["not_adopted"]])
print("unlisted  :", [e["host"] for e in s["unlisted"]])
print()
print("relist_condition 보유:", [e["host"] for e in s["unlisted"] if e.get("relist_condition")])
