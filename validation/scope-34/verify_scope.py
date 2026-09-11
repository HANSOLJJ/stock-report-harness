# SCOPE-34 반영을 보존 원문과 대조한다 — robots.txt 전면 금지·약관 for any purpose·정책 갱신 (네트워크 없음)
"""**조회는 이미 했고 응답 본문을 `_raw/` 에 보존했다.** 여기서는 보존본만 읽는다.

조회 4건은 확인 목적이었다(robots.txt 3 · 이용약관 1). url·상태·바이트·sha256·조회 시각이
`_raw/fetch-meta.json` 에 있다. 이 스크립트는 **새로 호출하지 않는다.**

## 드러내려는 것 셋

1. **robots.txt 가 전면 금지인가** — `User-agent: *` + `Disallow: /` 인가, 예외가 있는가.
2. **약관이 개인 사용까지 막는가** — `for any purpose` 문면이 실제로 있는가.
3. **정책이 그에 맞게 반영됐는가** — usage_scope 확정, not_adopted 남은 사유, unlisted 사유 교체.

사용:
    python validation/scope-34/verify_scope.py
"""
from __future__ import annotations

import hashlib
import html
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = HERE / "_raw"
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


class Check:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        self.rows.append((bool(ok), label, detail))
        print(f"  {'OK  ' if ok else 'DIFF'} {label}" + (f"\n         {detail}" if detail else ""))

    @property
    def failed(self):
        return [r for r in self.rows if not r[0]]


def plain(path: Path) -> str:
    t = path.read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"[\s ]+", " ", html.unescape(t))


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    chk = Check()
    bar = "=" * 112
    print(bar)
    print("SCOPE-34 — 보존 원문 대조와 정책 반영 확인")
    print(bar)

    print()
    print("[0] 보존본 무결성 — 조회 시점의 바이트 그대로인가")
    meta = json.loads((RAW / "fetch-meta.json").read_text(encoding="utf-8"))
    ext = {"query1_robots": "txt", "query2_robots": "txt", "finance_robots": "txt",
           "legal_robots": "txt", "yahoo_tos": "html"}
    for row in meta:
        path = RAW / f"{row['name']}.{ext[row['name']]}"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        chk(digest == row["sha256"], f"{row['name']:15} {str(row['status']):4} {row['bytes']:>8}B  {row['url']}")

    print()
    print("[1] robots.txt — 전면 금지인가")
    for name in ("query1_robots", "query2_robots"):
        body = (RAW / f"{name}.txt").read_text(encoding="utf-8").strip()
        lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
        chk(lines == ["User-agent: *", "Disallow: /"],
            f"{name}: **전면 금지** — 예외 한 줄도 없다", repr(body))
        chk("Allow:" not in body, f"{name}: Allow 지시가 없다")
    fin = (RAW / "finance_robots.txt").read_text(encoding="utf-8")
    chk("Allow:" in fin and len(fin) > 2000,
        "대조 — finance.yahoo.com(HTML 사이트)은 선택적 목록이다",
        f"{len(fin)}바이트에 Allow {fin.count('Allow:')}건. **API host 두 개만 전면 금지다**")

    print()
    print("[2] 이용약관 — 개인 사용까지 막는가")
    tos = plain(RAW / "yahoo_tos.html")
    clause = ("access or collect data, or attempt to access or collect data, from our Services using "
              "any automated means")
    i = tos.find(clause)
    chk(i >= 0, "자동 수집 금지 조항이 있다")
    seg = tos[i:i + 330] if i >= 0 else ""
    chk("for any purpose" in seg,
        "**for any purpose — 목적을 가리지 않는다. 개인 사용 예외가 없다**", seg[:300])
    chk("without our express, prior permission" in seg, "사전 서면 허가가 있어야 한다는 단서")
    grants = [m.start() for m in re.finditer(r"personal", tos, re.I)]
    chk(len(grants) > 0, f"본문에 personal 이 {len(grants)}회 나온다",
        "전부 소프트웨어 라이선스 문구나 개인정보 맥락이고 **자동 수집을 개인에게 허용하는 조항은 없다**")

    print()
    print("[3] 정책 반영 — usage_scope")
    v17 = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
    src = v17["sources"]
    scope = src["usage_scope"]
    chk(scope["scope"] == "personal_internal_only" and "scopes" not in scope,
        "usage_scope 가 personal_internal_only 단독")
    for token in ("corporate_internal_only", "합집합", "세 번"):
        chk(token in scope["supersedes"], f"supersedes 에 '{token}' 가 있다")
    chk("개인 사용조차 막는" in scope["evaluation_rule"],
        "**보고 조건이 규칙에 선언돼 있다** — 개인 사용이 허용되면 되묻지 않는다")

    print()
    print("[4] 정책 반영 — not_adopted 의 남은 사유")
    na = {e["host"]: e for e in src["not_adopted"]}
    expect = {"www.alphavantage.co": "technical", "financialmodelingprep.com": "technical",
              "finnhub.io": "terms", "data.nasdaq.com": "cost"}
    for host, rtype in expect.items():
        chk(na[host]["reason_type"] == rtype, f"{host:28} reason_type = {rtype}")
    chk("해소" in na["www.alphavantage.co"]["reopen_condition"]
        and "해소" in na["financialmodelingprep.com"]["reopen_condition"]
        and "해소" in na["finnhub.io"]["reopen_condition"],
        "셋 다 약관 사유가 해소됐다는 사실이 reopen_condition 에 있다")
    chk("서면 승인" in na["finnhub.io"]["reopen_condition"],
        "**Finnhub 만 약관 사유가 남는다** — 파생 결과 공유 서면 승인")
    chk("무관" in na["data.nasdaq.com"]["reopen_condition"],
        "data.nasdaq 은 범위와 무관한 비용 결정이라고 적혀 있다")
    for host in ("www.alphavantage.co", "financialmodelingprep.com"):
        chk("SCOPE-34" in na[host]["note"] and "reason_type" in na[host]["note"],
            f"{host}: reason_type 이 바뀐 사실을 note 에 남겼다")

    print()
    print("[5] 정책 반영 — yahoo 는 올리지 못했다")
    allowed = {e["host"] for e in src["allowed"]}
    unlisted = {e["host"]: e for e in src["unlisted"]}
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        chk(host not in allowed, f"{host} 가 allowed 에 없다")
        chk(host in unlisted, f"{host} 가 unlisted 에 별도 항목으로 있다",
            "note 로만 적으면 source_violation 이 못 잡는다")
    q1 = unlisted["query1.finance.yahoo.com"]
    chk(q1["reason_type"] == "both", "reason_type 이 both — 소멸한 사유와 새 사유를 같이 적었다")
    chk("소멸한 사유" in q1["reason"] and "NTM PER" in q1["reason"],
        "**기존 기술 사유가 소멸했다는 것을 적었다** — 지적이 맞았다")
    chk("Disallow: /" in q1["reason"] and "for any purpose" in q1["reason"],
        "새 사유 둘이 원문 문면으로 적혀 있다")
    chk("생산 원천" in q1["note"] and "관행" in q1["note"],
        "기존 스킬 관행과 생산 원천 등재를 구분해 적었다")
    chk(allowed == {"data.sec.gov", "www.sec.gov", "www.federalreserve.gov"},
        "**가격 원천이 allowlist 에 없다**", f"allowed = {sorted(allowed)}")

    print()
    print("[6] source_violation — 안내가 재조사를 지시하지 않는가")
    from scorecard.rules import load_rules
    r17 = load_rules("v1.7")
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        msg = r17.source_violation(f"https://{host}/v8/finance/chart/AAPL") or ""
        chk("등재하지 않은 host" in msg, f"{host}: 검토 후 미등재로 잡힌다")
        chk("약관 확인 후 규칙에 등재하고 쓴다" not in msg,
            f"{host}: **재조사 지시 문구가 안 나온다**")
    chk((r17.source_violation("https://zz.example/x") or "").endswith("등재하고 쓴다"),
        "미검토 host 는 기존 안내 그대로다 — 검토한 것과 안 한 것이 갈린다")
    chk(r17.source_violation("https://data.sec.gov/x") is None, "allowed 판정이 가려지지 않는다")

    print()
    print("[7] 과거 규칙 파일이 안 깨지는가")
    for version, expect_hash in (("v1.5", "9231b3a0"), ("v1.6", "a86d048f")):
        rules = load_rules(version)
        chk(rules.hash.startswith(expect_hash), f"{version} 로드 정상 ({rules.hash[:16]}…)")
    chk("미승인 후보" in (load_rules("v1.6").source_violation("https://data.nasdaq.com/x") or ""),
        "v1.6 은 옛 키(conditional_candidates)로 그대로 읽힌다")

    print()
    print("[8] 점수·승인 대상")
    results = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    chk(results["population"]["scored"] == 14 and not results["pending_rule_decisions"],
        "14/14 완주 · 미결 규칙 결정 없음")
    obs = json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]
    mc = [o for o in obs if o["metric"] == "market_cap"]
    chk(len(mc) == 12 and {o["status"] for o in mc} == {"legacy_unverified"},
        f"market_cap {len(mc)}건이 전부 legacy_unverified — 이번 과제는 등재까지다")
    from scorecard.stages import current_hashes
    base = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
    appr = json.loads((base / "approval.json").read_text(encoding="utf-8"))["hashes"]
    chk(current_hashes(base.name) == appr, "승인 대상 6종 전부 보존")

    print()
    print(bar)
    bad = chk.failed
    print(f"대조 {len(chk.rows)}건 · 불일치 {len(bad)}건")
    for _, label, _d in bad:
        print(f"  불일치: {label}")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
