# SRC-POLICY-32: usage_scope 를 허용 범위로 바꾸는 제안을 프로토타입으로 검증한다.
# worker 가 같은 파일을 미커밋 수정 중이므로 worker 워크트리는 읽기만 하고 여기서 시험한다.
import copy
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
W = "C:/Users/noble/orca/workspaces/stock-report-harness/worker"
RULES = os.path.join(W, "scorecard", "rules")

# ---- 제안 형태 -------------------------------------------------------------
# scope(단일 문자열) 대신 scopes(배열)를 정본으로 두고, 읽을 때 단일값을 1원소로 승격한다.
SCOPE_VALUES = {"personal_internal_only", "corporate_internal_only", "external_distribution"}


def normalize_scope(block):
    """과거·신규 두 형태를 모두 받아 집합으로 정규화한다.
    v1.5 는 sources 자체가 없고, v1.6·v1.7 은 scope 단일 문자열이다."""
    if block is None:
        return None
    if "scopes" in block:
        vals = block["scopes"]
        if not isinstance(vals, list) or not vals:
            raise ValueError("scopes 는 비어 있지 않은 배열이어야 함")
        form = "scopes"
    elif "scope" in block:
        vals = [block["scope"]]
        form = "scope(legacy)"
    else:
        raise ValueError("scope 또는 scopes 중 하나가 필요함")
    bad = [v for v in vals if v not in SCOPE_VALUES]
    if bad:
        raise ValueError("알 수 없는 scope 값 %r" % bad)
    if len(set(vals)) != len(vals):
        raise ValueError("scopes 에 중복이 있음")
    return {"values": set(vals), "form": form}


print("=" * 96)
print("1. 하위호환 — 기존 규칙 파일이 그대로 읽히는가")
print("=" * 96)
for v in ("v1.5", "v1.6", "v1.7"):
    d = json.load(io.open(os.path.join(RULES, v + ".json"), encoding="utf-8"))
    block = (d.get("sources") or {}).get("usage_scope")
    try:
        n = normalize_scope(block)
    except Exception as e:
        print("   %-5s ★실패: %s" % (v, e)); continue
    if n is None:
        print("   %-5s sources 블록 없음 → usage_scope 없음 (정책 미적용 버전, 그대로 통과)" % v)
    else:
        print("   %-5s form=%-15s values=%s" % (v, n["form"], sorted(n["values"])))

print()
print("=" * 96)
print("2. 새 형태(scopes 배열)도 읽히는가")
print("=" * 96)
new = {"scopes": ["personal_internal_only", "corporate_internal_only"],
       "decided_at": "2026-09-11", "statement": "...", "condition": "..."}
print("   신규형:", sorted(normalize_scope(new)["values"]), "form=", normalize_scope(new)["form"])
for bad in ({"scopes": []}, {"scopes": ["nope"]}, {"scopes": ["personal_internal_only"] * 2}, {}):
    try:
        normalize_scope(bad); print("   ★거부됐어야 함:", bad)
    except Exception as e:
        print("   거부 OK  %-46s → %s" % (json.dumps(bad, ensure_ascii=False), e))

print()
print("=" * 96)
print("3. 범위를 넓히면 제약이 넓어진다 — 라이선스 적격 판정의 방향")
print("=" * 96)
# 각 원천 라이선스가 '금지하는' scope
LICENSE_BARS = {
    "alphavantage.co":        {"corporate_internal_only", "external_distribution"},
    "financialmodelingprep.com": {"corporate_internal_only", "external_distribution"},
    "finnhub.io":             {"corporate_internal_only", "external_distribution"},
    "data.sec.gov":           set(),
    "www.sec.gov":            set(),
    "www.federalreserve.gov": set(),
}
for label, scopes in (("이전(법인만)", {"corporate_internal_only"}),
                      ("확정(개인+법인)", {"personal_internal_only", "corporate_internal_only"}),
                      ("가정(개인만)", {"personal_internal_only"})):
    print("   %-16s %s" % (label, sorted(scopes)))
    for host, bars in sorted(LICENSE_BARS.items()):
        hit = scopes & bars
        print("      %-28s %s" % (host, ("적격" if not hit else "부적격 — 우리 범위 중 %s 를 금지" % sorted(hit))))
    print()
print("   핵심: 범위는 합집합이라 라이선스는 우리 범위의 '전부' 를 허용해야 한다.")
print("   개인 사용을 더해도 법인 내부 사용이 범위에 남아 있으면 법인 금지 조항은 그대로 문다.")
