# SRC-FLAG-49: legacy 관측의 상류가 StockAnalysis 라는 사실을 관측 basis 와 원천 장부에 표시한다 (점수 무영향)
"""할 것 넷 (지시서 msg_7c19064c60e3).

1. market_cap 관측 basis 에 상류 StockAnalysis 표시. tsmc·alibaba 는 원문이 직접 계산했다고 적는다.
2. sources.not_adopted 에 stockanalysis.com — **되살리는 것이 아니라 장부에 이름을 올리는 것.**
3. net_cash apple·palantir basis 에 StockAnalysis + 공시 혼합 표시.
4. sources.note — 관측 source_id 는 원천 정책 검사를 받지 않는다.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(해시가 바이트에 걸린다 — HASH-EOL).
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_observations, validate_rules  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-14"
HOST = "stockanalysis.com"

# 채점표 3-1a 표의 행. 절 제목 L794 `⑥ 원자료 (StockAnalysis · 2026-09-02 종가 · 단일 출처)`.
MC_ROW = {"alibaba": 809, "meta": 810, "nvidia": 811, "tsmc": 812, "alphabet": 813, "microsoft": 814,
          "amazon": 815, "apple": 816, "oracle": 817, "palantir": 818, "spacex-xai": 819, "tesla": 820}

AUTHOR_COMPUTED = {
    "tsmc": {
        "citation": "채점표 L822",
        "text": "`TSMC는 전부 직접 계산 — ADR 1주 = 보통주 5주, 재무는 TWD. StockAnalysis가 시총 $1.95T·PER 27.9 등 "
                "환산이 섞여 있어 ADR 5.19B주 × $415.5 = $2.15T`",
        "vendor_value_rejected": "StockAnalysis 시총 $1.95T (ADR·TWD 환산 혼재)",
        "arithmetic": "5.19B × $415.50 = $2,156.4B → 표기 $2.15T",
        "narrowing": None,
    },
    "alibaba": {
        "citation": "채점표 L823",
        "text": "`시총은 8/26 증자(710M주) 완료 반영, ADS 24.2억 주.` (같은 ✱ 각주 안 — 앞 문장이 `Alibaba NTM은 직접 계산`)",
        "vendor_value_rejected": None,
        "arithmetic": "24.2억 ADS × $111.76 = $270.5B → 표기 $270B",
        "narrowing": ("**원문은 시총을 `직접 계산` 이라고 적지 않는다.** 같은 각주가 NTM 을 `직접 계산` 이라 적고 시총은 "
                      "`증자 완료 반영, ADS 24.2억 주` 라고만 적는다. 표 L809 시총 칸에는 ✱ 가 없다(TSMC L812 는 있다). "
                      "주식 수 × 주가 산술이 표기값과 맞아 직접 계산으로 읽었다 — StockAnalysis 가 어떤 값을 줬는지는 "
                      "원문에 없다."),
    },
}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    raw = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    out = json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if raw.endswith(("\n", "\r\n")) else "")
    io.open(p, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))


POLICY_STATUS = ("**not_adopted 에 legacy_upstream 으로 올라 있다(SRC-FLAG-49, 2026-09-14).** 채택 검토를 거친 등재가 "
                 "아니라 이 관측이 어디서 왔는지 가리키려고 장부에 이름을 올린 것이다. allowed 에는 없다.")


def stamp_market_cap(obs: dict) -> list[str]:
    done = []
    for o in obs["items"]:
        if o["metric"] != "market_cap" or o["status"] != "legacy_unverified":
            continue
        cid = o["company_id"]
        b = {k: v for k, v in (o.get("basis") or {}).items()
             if not k.startswith(("source_", "vendor_", "price_input_", "author_", "on_score_path"))}
        if cid in AUTHOR_COMPUTED:
            a = AUTHOR_COMPUTED[cid]
            b["source_vendor"] = "author_computed"
            b["author_computed"] = "직접 계산, 주가 입력은 같은 절 (L822·L823)"
            b["author_computed_citation"] = a["citation"]
            b["author_computed_text"] = a["text"]
            b["author_computed_arithmetic"] = a["arithmetic"]
            if a["vendor_value_rejected"]:
                b["vendor_value_rejected"] = a["vendor_value_rejected"]
            if a["narrowing"]:
                b["author_computed_narrowing"] = a["narrowing"]
            b["price_input_vendor"] = "StockAnalysis"
            b["price_input_citation"] = f"채점표 L794 절 제목 · 주가 L{MC_ROW[cid]}"
        else:
            b["source_vendor"] = "StockAnalysis"
        b["source_citation"] = f"채점표 L794 절 제목 · 행 L{MC_ROW[cid]}"
        b["vendor_not_in_source_policy"] = True
        b["vendor_policy_status"] = POLICY_STATUS
        if cid == "spacex-xai":
            b["on_score_path"] = ("**점수 경로 밖.** spacex-xai 는 F6 `listed_newly` 트랙이라 P3 만 읽고 P1·P2 가 이 "
                                  "값을 쓰지 않는다. SRC-TRACE-47 의 점수 경로 11건에 안 들고 이 12번째 건이다. 상류는 "
                                  "같은 절(L819)이라 같이 표시한다.")
        o["basis"] = b
        done.append(cid)
    return done


def stamp_net_cash(obs: dict) -> list[str]:
    done = []
    for o in obs["items"]:
        if o["metric"] != "net_cash" or o["company_id"] not in ("apple", "palantir") or o["status"] != "legacy_unverified":
            continue
        b = dict(o.get("basis") or {})
        row = {"apple": 854, "palantir": 861}[o["company_id"]]
        b["source_mixed"] = "StockAnalysis 9/2 + 공시 (채점표 L848 · HANDOVER L41)"
        b["source_mixed_text"] = ("채점표 L848 절 제목 `3-1a-3. 통합 재무 전수표 — ⑨ 게이트 원자료 (StockAnalysis 9/2 + 공시)` "
                                  f"· 행 L{row} · HANDOVER L41 `TTM FCF · 현금 · 순차입 · D/EBITDA | StockAnalysis "
                                  "Financials | … Cash & ST Inv …`")
        b["not_sec"] = "**SEC 관측이 아니다.** 어느 칸이 StockAnalysis 이고 어느 칸이 공시인지 원문이 행 단위로 가르지 않는다."
        b["vendor_not_in_source_policy"] = True
        b["vendor_policy_status"] = POLICY_STATUS
        o["basis"] = b
        done.append(o["company_id"])
    return done


def update_ntm_per(obs: dict) -> int:
    """IMPL-46 이 적은 `네 목록 어디에도 없다` 는 그때 사실이었다. 지우지 않고 뒤에 바뀐 상태를 붙인다."""
    n = 0
    for o in obs["items"]:
        b = o.get("basis") or {}
        if o["metric"] == "ntm_per" and "vendor_policy_check" in b:
            b["vendor_policy_status"] = POLICY_STATUS + " 위 vendor_policy_check 는 IMPL-46 시점 기록이다."
            n += 1
    return n


def register_source(rules: dict) -> None:
    src = rules["sources"]
    src["not_adopted"] = [e for e in src["not_adopted"] if e["host"] != HOST]
    src["not_adopted"].append({
        "name": "StockAnalysis",
        "host": HOST,
        "status": "not_adopted",
        "decided_at": DATE,
        "decided_by": "설계진행(SRC-FLAG-49 지시) — 장부 등재. 채택 검토 결정이 아니다",
        "reason_type": "legacy_upstream",
        "reason": "v1.5 legacy 관측의 상류. 원천 정책 수립 전 자료. 재조회하지 않는다. 약관 미검토.",
        "reopen_condition": ("없음 — 재조회하지 않는다. legacy 관측을 대체할 때는 allowed 원천에서 새로 관측한다. "
                             "**이 등재는 약관 검토가 아니며 '확인 후 등재하고 쓴다' 로 읽지 않는다.**"),
        "prior_investigation": ("validation/src-trace-47 (NTM SRC-TRACE-47) — 점수 경로 legacy 25쌍 중 market_cap 11건의 "
                                "상류가 채점표 L794 절 제목으로 StockAnalysis 확정"),
        "note": ("**되살리는 것이 아니다.** 관측이 어디서 왔는지 가리키려고 이름을 올린다. 올리기 전에는 네 목록 어디에도 "
                 "없어 IMPL-46 이 ntm_per 12건에 `vendor_not_in_source_policy` 를 달았다. 걸리는 legacy 관측: "
                 "market_cap 12건(점수 경로 11 + spacex-xai) · ntm_per 10건(tsmc·alibaba 는 직접 계산) · "
                 "net_cash apple·palantir 2건(공시 혼합)."),
    })
    src["note"] = ("[SRC-FLAG-49 2026-09-14] **관측 source_id 는 원천 정책 검사를 받지 않는다.** `source_violation(url)` 은 "
                   "`validate.check_source_allowlist` 가 sources.json 항목의 url 을 볼 때만 불린다. SRC-v15-html·md·rule "
                   "세 항목은 url 이 null 이라 검사를 그대로 통과하고, 그 source_id 를 단 이관 관측 242건(obsreg 기준 "
                   "209+18+15)은 정책 검사 밖이다. 상류는 관측 basis(source_vendor·source_mixed)로만 추적한다. | 지시서 "
                   "문구는 `fetch 시점 URL 검사` 였다 — 코드상 호출 지점은 fetch 가 아니라 sources.json 검증이라 그렇게 적었다.")


def main() -> int:
    rules = load(RULES)
    register_source(rules)
    validate_rules(rules)
    dump(RULES, rules)

    obs_path = RUN / "observations.json"
    obs = load(obs_path)
    mc = stamp_market_cap(obs)
    nc = stamp_net_cash(obs)
    ntm = update_ntm_per(obs)
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    validate_observations(obs, registry, RUN_ID)
    dump(obs_path, obs)

    # 규칙이 바뀌었으니 실행의 rule_hash 를 다시 고정한다. 작업 트리 바이트 기준(HASH-EOL).
    run_path = RUN / "run.json"
    raw = io.open(run_path, encoding="utf-8", newline="").read()
    old = json.loads(raw)["rule_hash"]
    new = load_rules("v1.7").hash
    if old != new:
        io.open(run_path, "w", encoding="utf-8", newline="").write(raw.replace(old, new))

    print(f"1. market_cap {len(mc)}건: {', '.join(mc)}")
    print(f"   author_computed: {', '.join(c for c in mc if c in AUTHOR_COMPUTED)}")
    print(f"2. sources.not_adopted += {HOST} (legacy_upstream)")
    print(f"3. net_cash source_mixed {len(nc)}건: {', '.join(nc)}")
    print(f"   ntm_per vendor_policy_status 갱신 {ntm}건")
    print("4. sources.note 등재")
    print(f"   run.json rule_hash {old[:12]} -> {new[:12]}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
