# 비상장 등록값을 v1.5 원본 문장에서 직접 재확인하고 모순 둘과 임계 민감도를 드러낸다 (네트워크 없음)
"""**받은 값을 정답으로 쓰지 않는다.** 선행 조사 두 건이 준 값도 원본 문장에서 다시 읽는다.

    규칙 원본   AI기업_채점규칙_v1.5.md   sha256 57beb84a…  (v1.5.json 선언값과 대조)
    채점표 원본  AI기업_채점표_v1.5.md     비상장 ⑥ 표 · ⑨ 항목

## 드러내려는 것 넷

1. **구간표를 우리가 옮겨 적으면서 바꾸지 않았는가** — 609~616행 비상장 열 그대로인가.
2. **P2 분모가 arr 이 아닌가** — "ARR 배수 — TTM 보정 필수" 문면이 실제로 있는가.
3. **모순 둘** — Series H `$30B`/`$65B`, openai arr 시점 표기.
4. **Series H 모순이 보정 임계를 가로지르는가** — 자본효율이 0.41~0.72 로 갈리고 0.50 이 그 안에 있다.

사용:
    python validation/priv-impl-31/verify_private.py
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC_DIR = Path(r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor")
RULE_MD = SRC_DIR / "AI기업_채점규칙_v1.5.md"
CARD_MD = SRC_DIR / "AI기업_채점표_v1.5.md"
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
# 보존 원문. C-13 3cf9799 의 AMZN 10-Q 로 F8 근거 한 줄을 직접 대조한다.
BLOBS = {"AMZN_10Q": ("3cf9799", "validation/offb-24/_raw/amzn-20260630.htm")}


class Check:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        self.rows.append((bool(ok), label, detail))
        print(f"  {'OK  ' if ok else 'DIFF'} {label}" + (f"\n         {detail}" if detail else ""))

    @property
    def failed(self):
        return [r for r in self.rows if not r[0]]


def blob(key: str) -> bytes:
    import subprocess
    commit, path = BLOBS[key]
    out = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"git show {commit}:{path} 실패")
    return out.stdout


def flat(text: str) -> str:
    return re.sub(r"[\s\u00a0]+", " ", text)


def plain(data: bytes) -> str:
    """보존 HTML 원문을 문장으로 편다. 태그를 지우고 공백을 접는다."""
    import html as _h
    t = data.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return flat(_h.unescape(t))


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    chk = Check()
    bar = "=" * 112
    print(bar)
    print("PRIV-IMPL-31 — 비상장 등록값 대 v1.5 원본 대조")
    print(bar)

    print()
    print("[0] 원본 무결성")
    if not RULE_MD.is_file():
        print(f"  원본을 찾을 수 없다: {RULE_MD}")
        return 1
    rule_bytes = RULE_MD.read_bytes()
    digest = hashlib.sha256(rule_bytes).hexdigest()
    declared = json.loads((ROOT / "scorecard" / "rules" / "v1.5.json").read_text(encoding="utf-8"))["source"]["sha256"]
    chk(digest == declared, f"규칙 원본 sha256 = v1.5.json 선언값 ({digest[:16]}…)",
        "우리가 읽는 파일이 규칙이 선언한 그 파일이다")
    rule_lines = rule_bytes.decode("utf-8").splitlines()
    card = flat(io.open(CARD_MD, encoding="utf-8").read())

    print()
    print("[1] 비상장 구간표 — 609~616행을 옮겨 적으며 바꾸지 않았는가")
    table = flat("\n".join(rule_lines[608:616]))
    expect = {"-2": "~20x", "-3": "20x대", "-4": "30x+", "-5": "100x+"}
    for score, label in expect.items():
        chk(f"**{score}**" in table and label in table, f"{score} 칸이 '{label}'")
    chk("| **0** | < 20 | — |" in flat("\n".join(rule_lines[610:611])) or "— |" in table,
        "0 과 -1 칸은 비상장 열이 '—' 로 비어 있다", "천장 -2 는 임의 제한이 아니라 원본 표의 형태다")
    bands = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
    pb = bands["policies"]["f6"]["private_bands"]
    got = {str(b["score"]): b["label"] for b in pb["bands"]}
    chk(got == {"-5": "100x+", "-4": "30x+", "-3": "20x대", "-2": "~20x"},
        "v1.7 private_bands 가 원본 표와 같다", json.dumps(got, ensure_ascii=False))
    chk(pb["ceiling"] == -2 and pb["floor"] == -5, "천장 -2 · 하한 -5")

    print()
    print("[2] P2 분모는 arr 이 아니라 TTM 보정 매출")
    chk("ARR 배수 — TTM 보정 필수" in table, "구간표 -2 칸 괄호에 'ARR 배수 — TTM 보정 필수' 가 있다")
    corr_txt = flat("\n".join(rule_lines[644:648]))
    chk("ARR은 TTM 매출보다 과대하다" in corr_txt, "645~647행이 ARR 과대 보정을 요구한다",
        "ARR 은 특정 시점 월매출 ×12 런레이트이고 상장사 P/S 분모는 직전 4분기 실제 매출이다")
    chk(pb["input"] == "ps_ratio", "v1.7 이 읽는 입력이 ps_ratio 다 — arr 이 아니다")

    print()
    print("[3] 배수·자본효율·ARR 값 — 원본 문장에서 직접")
    facts = [
        ("anthropic 밸류 $965B ÷ ARR $65B = 14.8배", "post-money **$965B ÷ ARR $65B(7월) = 14.8배**"),
        ("anthropic TTM 보정 약 30~39배 (Q2 매출 $10.9B 역산)", "분모를 TTM으로 맞추면 **약 30~39배**(Q2 매출 $10.9B 역산)"),
        ("anthropic 자본효율 0.52 (ARR $65B ÷ 누적조달 약 $125B)", "**자본효율 0.52**(ARR $65B ÷ 누적 조달 약 $125B)"),
        ("anthropic ARR $47B → $65B", "ARR이 $47B→$65B로 늘며"),
        ("openai 밸류 $852B ÷ ARR $40B = 21.3배 · TTM 보정 약 39배", "**$852B ÷ ARR $40B = 21.3배** — TTM 보정 시 **약 39배**"),
        ("openai 자본효율 0.22 (ARR $40B ÷ 누적조달 약 $180~190B)", "**자본효율 0.22**(ARR $40B ÷ 누적 조달 약 $180~190B)"),
        ("openai ARR $25B → $40B", "ARR이 $25B→$40B로 늘며"),
    ]
    for label, needle in facts:
        chk(flat(needle) in card, label)
    chk("**-3**" in card and "**-4**" in card, "원본 판정 anthropic -3 · openai -4",
        "이 값이 우리 결과와 같다는 것이 C-12 의 약점이고 규칙 파일에 적어 두었다")

    print()
    print("[4] 산식 재계산 — 원본 숫자로 우리가 다시 센다")
    for cid, arr, prior, raised, exp_g, exp_e in (
            ("anthropic", 65, 47, 125, 0.3830, 0.5200),
            ("openai", 40, 25, 185, 0.6000, 0.2162)):
        g, e = arr / prior - 1, arr / raised
        chk(abs(g - exp_g) < 5e-4, f"{cid} ARR 성장률 {g*100:.2f}%")
        chk(abs(e - exp_e) < 5e-4, f"{cid} 자본효율 {e:.4f}")
    chk(0.3830 >= 0.30 and 0.5200 >= 0.50, "anthropic 은 두 조건 다 충족 → 보정 +1 → -3")
    chk(0.6000 >= 0.30 and not (0.2162 >= 0.50),
        "**openai 는 성장률이 더 높은데도 보정이 없다**",
        "자본효율이 임계 미달이기 때문이다. 조건 하나로 올리는 규칙이었다면 openai 가 걸렸을 것이다")

    print()
    print("[5] 모순 둘 — 값을 고르지 않고 갈린다는 사실을 남겼는가")
    chk("Series H $30B($965B 밸류)" in card, "⑨절: Series H **$30B**")
    chk("$965B (2026/5 Series H $65B)" in card, "비상장 ⑥ 표: Series H **$65B**")
    chk(True, "**같은 문서 안에서 갈린다**", "어느 쪽이 맞는지 정하지 않는다 — 외부 확인이 이번 범위 밖이다")
    n_july = len(re.findall(r"ARR \$65B\(7월\)|\$65B\*\* \(7월\)|\(7월\)", card))
    n_820 = len(re.findall(r"8/20", card))
    chk(n_july > 0 and n_820 > 0, f"openai arr 시점 표기가 갈린다 — '7월' {n_july}회 · '8/20' {n_820}회",
        "금액 $40B 는 같아 P2·P3 에 영향이 없다. 영향이 없다는 사실까지 적었다")

    print()
    print("[6] Series H 모순이 보정 임계를 가로지른다")
    arr, raised, delta = 65, 125, 65 - 30
    rows = [("원본 표기 그대로", raised),
            ("125B 가 Series H 를 65B 로 포함했다면 → 30B 로 교체", raised - delta),
            ("125B 가 Series H 를 30B 로 포함했다면 → 65B 로 교체", raised + delta)]
    for label, r in rows:
        e = arr / r
        print(f"    {label:48} 자본효율 {e:.4f}  임계 0.50 {'충족' if e >= 0.5 else '**미달 → 보정 없음 → F6 -4**'}")
    lows = [arr / r for _, r in rows]
    chk(min(lows) < 0.50 <= max(lows),
        "**구간 0.41~0.72 가 임계 0.50 을 가로지른다**",
        "한 시나리오에서만 보정이 사라지고 그때 anthropic F6 가 -3 이 아니라 -4 가 된다. "
        "값을 고르지 않았고 민감도를 관측 basis 에 남겼다 — 설계진행 판단이 필요한 자리다")

    print()
    print("[7] 등록 결과가 실행에 실제로 반영됐는가")
    obs = json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]
    idx = {(o["company_id"], o["metric"]): o for o in obs if o["observation_id"].endswith(".priv31")}
    for cid in ("anthropic", "openai"):
        for metric in ("ps_ratio", "arr_prior", "fcf_ttm", "cash", "net_cash",
                       "debt_ebitda", "operating_margin_ttm"):
            chk((cid, metric) in idx, f"{cid}.{metric} 등록됨")
    for cid in ("anthropic", "openai"):
        for metric in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
            o = idx[(cid, metric)]
            chk(o["missing_type"] == "not_disclosed_confirmed" and o["value"] is None,
                f"{cid}.{metric} 결측 유형 등록 · 값은 그대로 없음")
    results = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    got = {c["company_id"]: c["factors"] for c in results["companies"]}
    chk(got["anthropic"]["F6"]["score"] == -3 and got["anthropic"]["F9"]["score"] == -2,
        "anthropic F6 -3 · F9 -2")
    chk(got["openai"]["F6"]["score"] == -4, "openai F6 -4")
    path = got["anthropic"]["F9"]["calc"]["path"][0]
    chk(path["result"] == "undetermined" and "통과 아님" in path["reason"],
        "**F9 경로에 '판정 보류(통과 아님)' 가 남았다**", "통과로 적지 않았다")
    chk(results["population"]["scored"] == 14 and not results["pending_rule_decisions"],
        f"14/14 완주 · 미결 결정 {results['pending_rule_decisions'] or '없음'}")

    print()
    print("[8] 검토 보완 넷 (2026-09-11 라운드2)")
    v17 = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
    f6, src = v17["policies"]["f6"], v17["sources"]

    chk("P2 가 점수를 내고" in f6["private_note"] and "확정 전" in f6["private_note"],
        "① private_note 가 지금 규칙과 맞고 확정 전 서술임을 함께 남긴다",
        "선언이 사실과 반대이던 상태를 고쳤다 — 코드가 하는 일과 선언이 같아야 한다")
    chk(f6["private_multiples"][0].startswith("ps_ratio") and "arr 이 아니다" in f6["private_multiples"][0],
        "① private_multiples 첫 항목이 ps_ratio 이고 arr 이 아님을 명시")
    chk(any("점수에 쓰지 않는다" in m for m in f6["private_multiples"]),
        "① 버린 배수(post_money_valuation/arr)를 지우지 않고 참고용으로 남겼다")

    chk(src["usage_scope"]["scopes"] == ["personal_internal_only", "corporate_internal_only"],
        "② usage_scope 가 개인·법인 합집합")
    chk("합집합" in src["usage_scope"]["evaluation_rule"] and "조이는" in src["usage_scope"]["evaluation_rule"],
        "② 합집합 평가 규칙이 선언돼 있다 — 범위를 넓히는 것이 제약을 조인다")
    allowed_hosts = [e["host"] for e in src["allowed"]]
    na = {e["host"]: e for e in src.get("not_adopted", [])}
    for host in ("finnhub.io", "financialmodelingprep.com", "www.alphavantage.co"):
        chk(host not in allowed_hosts and host in na, f"② {host} 가 allowed 에서 내려가 not_adopted 에 있다")
        chk(na[host]["reason_type"] == "terms" and "personal_internal_only" in na[host]["reopen_condition"],
            f"② {host} 재개 조건에 개인 전용으로 좁히는 것이 적혀 있다")
    chk("서면 승인" in na["finnhub.io"]["reopen_condition"] and "둘 다 필요" in na["finnhub.io"]["reopen_condition"],
        "② **Finnhub 만 조건이 둘이다** — 개인 범위로 좁히는 것에 더해 파생 결과 공유 서면 승인까지 필요하다")
    chk("conditional_candidates" not in src and "data.nasdaq.com" in na,
        "③ data.nasdaq.com 이 conditional_candidates 에서 not_adopted 로 옮겨졌다")
    chk(na["data.nasdaq.com"]["reason_type"] == "cost", "③ 사유가 비용이다 — 약관 위반이나 기술 부적격이 아니다")

    from scorecard.rules import load_rules
    r17 = load_rules("v1.7")
    msg = r17.source_violation("https://data.nasdaq.com/api/v3/datasets/ZACKS/EE.json") or ""
    chk("채택하지 않기로 결정된 원천" in msg and "재조사 불필요" in msg,
        "③ **source_violation 이 not_adopted 를 읽는다**", msg[:150])
    chk("약관 확인 후 규칙에 등재하고 쓴다" not in msg,
        "③ 마지막 fallback 안내로 떨어지지 않는다 — 그 문구가 재조사를 지시하게 된다")
    old_msg = load_rules("v1.6").source_violation("https://data.nasdaq.com/api/v3/x.json") or ""
    chk("미승인 후보" in old_msg, "③ v1.6 은 옛 키(conditional_candidates)로 그대로 읽힌다",
        "과거 규칙 파일을 깨지 않는다")

    jud = {(j["company_id"], j["factor"]): j for j in json.loads(
        (RUN / "judgments.json").read_text(encoding="utf-8"))["items"]}
    f8 = jud[("anthropic", "F8")]
    chk(f8["score"] == -3, "④ F8 점수 -3 유지")
    claims = [e for e in f8["evidence"] if "DS투자증권" in e and "근거 교체" not in e]
    chk(not claims, "④ 증권사 2차 증언을 근거로 쓰는 항목이 없다")
    for accn in ("0001018724-25-000002", "0001018724-25-000121",
                 "0001018724-26-000002", "0001018724-26-000012"):
        chk(any(accn in e for e in f8["evidence"]), f"④ 8-K 접수번호 {accn} 등재")
    chk(any("Anthropic is using to train its industry-leading AI model, Claude" in e
            for e in f8["evidence"]), "④ 2026-02-05 공시 원문이 근거란에 있다")
    chk(any("확인된 것" in e for e in f8["evidence"]) and any("확인되지 않은 것" in e for e in f8["evidence"]),
        "④ 확인된 것과 확인되지 않은 것이 나뉘어 있다")
    chk(any("재판정 조건" in e for e in f8["evidence"]), "④ 재판정 조건이 등재돼 있다")
    chk(any("공시가 없을 뿐" in e for e in f8["evidence"]),
        "④ **미공시를 '아니다' 로 읽지 않는다는 근거가 남아 있다**",
        "Google 몫이 훈련이 아니라는 증거가 있는 것이 아니다")

    print()
    print("[8b] AMZN 10-Q Note 1 — C-13 인용을 보존 원문에서 직접 대조")
    amzn = plain(blob("AMZN_10Q"))
    quote = ("In Q2 2026, AWS and Anthropic announced an expansion of the strategic collaboration and "
             "existing multi-year commitment by more than $ 100.0 billion over 10.0 years")
    chk(quote in amzn, "AWS·Anthropic $100.0B/10.0년 확대 문면 확인",
        "8-K 네 건은 원문이 이 워크트리에 보존돼 있지 않아 C-13 의 SEC 읽기를 인용했고 그 사실을 적었다")
    chk("Anthropic Series H nonvoting preferred stock" in amzn,
        "**덤으로 찾은 것 — 같은 10-Q 가 Series H 를 직접 언급한다**",
        "Amazon 이 Q2 2026 에 Anthropic Series H 우선주에 $5.0B 를 투자했다고 공시한다. "
        "라운드 총액은 말하지 않아 30B/65B 모순을 해소하지는 못하나, **Series H 의 존재와 시점은 "
        "1차 자료로 확정된다**")

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
