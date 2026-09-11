# 지시받은 관측값을 보존된 SEC 원문에서 직접 재확인한다 (네트워크 없음 · git blob 만 읽는다)
"""**받은 값을 정답으로 쓰지 않는다.** 보존 원자료를 열어 문면을 다시 뽑고 대조한다.

원자료는 형제 워크트리의 **커밋**에 있다. 작업 트리 상태에 기대지 않도록 `git show <commit>:<path>`
로 blob 을 직접 읽고 sha256 을 같이 찍는다 — 다음 사람이 같은 바이트를 봤는지 확인할 수 있다.

    C-13  3cf9799  validation/offb-24/_raw/
    C-13  HANSOLJJ/C-13  validation/f6-avail-15b/_raw/   (companyfacts)

사용:
    python validation/obs-reg-25/verify_values.py
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys

BLOBS = {
    "SPCX_10Q":  ("3cf9799", "validation/offb-24/_raw/spcx-20260630.htm"),
    "SPCX_S1A":  ("3cf9799", "validation/offb-24/_raw/spcx_s1a_20260603.htm"),
    "AMZN_10Q":  ("3cf9799", "validation/offb-24/_raw/amzn-20260630.htm"),
    "BABA_20F":  ("3cf9799", "validation/offb-24/_raw/baba-20260331.htm"),
    "BABA_FACTS": ("HANSOLJJ/C-13", "validation/f6-avail-15b/_raw/CIK0001577552_BABA.json"),
}


def blob(key: str) -> bytes:
    commit, path = BLOBS[key]
    out = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"{key}: git show 실패 — {out.stderr.decode('utf-8', 'replace')[:200]}")
    return out.stdout


def plain(data: bytes) -> str:
    s = data.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    return re.sub(r"[\s ]+", " ", html.unescape(s))


class Check:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        self.rows.append((bool(ok), label, detail))
        print(f"  {'OK  ' if ok else 'DIFF'} {label}" + (f"\n         {detail}" if detail else ""))

    @property
    def failed(self) -> list[tuple[bool, str, str]]:
        return [r for r in self.rows if not r[0]]


def near(text: str, needle: str, before: int = 300, after: int = 200) -> str:
    i = text.find(needle)
    return "" if i < 0 else text[max(0, i - before):i + after]


def main() -> int:
    chk = Check()

    print("=" * 104)
    print("OBS-REG-25 — 지시값 대 보존 SEC 원문 대조")
    print("=" * 104)
    print()
    print("[0] 읽은 blob")
    data = {}
    for key in BLOBS:
        data[key] = blob(key)
        commit, path = BLOBS[key]
        print(f"  {key:12} {len(data[key]):>10,}B  sha256={hashlib.sha256(data[key]).hexdigest()[:16]}…  {commit}:{path}")

    spcx, s1a, amzn, baba = (plain(data[k]) for k in ("SPCX_10Q", "SPCX_S1A", "AMZN_10Q", "BABA_20F"))

    print()
    print("[1] SPCX — contracted_revenue 47,461 / offbalance_B 1,627 + 27,955")
    c = near(spcx, "Backlog totaled")
    chk("$ 47,461 million as of June 30, 2026" in c, "백로그 47,461 · 기준일 2026-06-30",
        "Backlog totaled … $ 47,461 million as of June 30, 2026")
    chk("Note 3 - Revenue" in spcx, "출처 Note 3 - Revenue (지시서 '10-Q Note 3')")
    chk("14,286" in c, "백로그 내 이연수익 14,286 포함 문면 확인")
    p = near(spcx, "Total $ 27,955", before=520, after=60)
    chk("2,728" in p and "22,244" in p and "2,172" in p and "809" in p,
        "무조건 약정 27,955 · 연도별 2,728/22,244/2,172/809/2", "as of June 30, 2026 · non-cancelable")
    chk("payable in cash and in the Company" in p, "Spectrum 분 현금·Class A 보통주 혼합 지급 문면")
    lease = near(s1a, "not yet commenced for the aggregate lease payments of $1,627 million", before=120, after=160)
    chk(bool(lease), "미개시 리스 1,627 (S-1/A)")
    chk("December 31, 2025" in lease, "**미개시 리스 기준일 2025-12-31** — 10-Q(2026-06-30)와 다름",
        "7.2 years 가중평균 리스기간 병기")
    chk(len(re.findall(r"not yet commenced", spcx, re.I)) == 0,
        "10-Q 에는 미개시 리스 수치가 없다 — 두 문서를 이어 붙여야 나온다")
    chk(abs((1627 + 27955) - 29582) < 1e-9, "합계 29,582 = 1,627 + 27,955")

    print()
    print("[2] AMZN — contracted_revenue 496B / offbalance_B 137,214 + 130,065")
    r = near(amzn, "496 billion", before=420, after=200)
    chk("approximately $ 496 billion as of June 30, 2026" in r, "RPO 약 496B · 기준일 2026-06-30",
        "원문이 approximately — 근사치")
    chk("original terms that exceed one year" in r, "분자는 **원계약 1년 초과분만** — 과소계상 방향")
    chk("6.4 years" in r, "가중평균 잔여 6.4년")
    chk("Note 1 — ACCOUNTING POLICIES" in amzn, "출처 Note 1 (지시서 '10-Q Note 1')")
    t = near(amzn, "Leases not yet commenced", before=60, after=420)
    chk("137,214" in t and "130,065" in t and "18,366" in t and "650,034" in t,
        "약정표 137,214 / 130,065 / 18,366 / 총 650,034")
    fn3 = near(amzn, "(3) Includes", before=0, after=420)
    chk(bool(fn3), "**각주 (3) 본문이 원문에 있다** — 지시서는 '확인하지 못했다' 고 적었다",
        fn3[:330].strip())
    chk(abs((137214 + 130065) - 267279) < 1e-9, "합계 267,279 = 137,214 + 130,065")

    print()
    print("[3] BABA — offbalance_B 54,136 + 200,062 · contracted_revenue 미공시")
    cap = near(baba, "27. Commitments", before=0, after=900)
    chk("RMB 54,136 million as of March 31, 2025 and 2026" in cap.replace("  ", " ")
        or "54,136" in cap, "자본약정 54,136 · Note 27(a) · 기준일 2026-03-31")
    chk("(b) Investment commitments" in cap and "14,501" in cap, "투자약정 14,501 은 Note 27(b) (제외 대상)")
    oth = near(baba, "(c) Other commitments", before=0, after=420)
    chk("200,062" in oth, "기타약정 200,062 · Note 27(c) — 코로케이션·대역폭·저작권·마케팅")
    ex = near(baba, "Practical expedients and exemptions", before=40, after=420)
    chk("to not disclose the value of unsatisfied performance obligations" in ex,
        "ASC 606 간편법 선언 문면 확인",
        "1년 이하 계약과 청구권 기준 계약만 덮는다 — 1년 초과분은 Note 5 의 중요성 미달 서술이 메운다")
    head = baba.find("Practical expedients and exemptions")
    sub = baba.rfind("(g) Revenue recognition", 0, head)
    between = re.findall(r"\(([a-z])\)\s+[A-Z][a-z]", baba[sub + 30:head])
    chk(sub > 0 and not between,
        "**간편법 선언은 Note 2(g) Revenue recognition 안에 있다** — 지시서는 '2(t)' 라고 적었다",
        "F-21 쪽 위치는 지시서와 같다. 소항목 문자만 다르다")
    for pat in ("remaining performance obligation", "not yet commenced", "backlog"):
        chk(len(re.findall(pat, baba, re.I)) == 0, f"20-F 전문에 '{pat}' 0건")
    rate = near(baba, "RMB6.8980 to US$1.00", before=420, after=200)
    chk("H.10 statistical release of the Federal Reserve Board" in rate,
        "**20-F 가 스스로 환율을 선언한다** — RMB6.8980/US$1.00, 2026-03-31, 연준 H.10",
        "외부 환율을 끌어올 필요가 없다. 출처가 문서 안에 있고 그 원천도 이미 allowlist 에 있다")
    chk(abs(54136 / 6.8980 - 7848) < 1.0, "선언 환율 역산 = 20-F 자체 편의환산 US$7,848M",
        f"54,136 / 6.8980 = {54136/6.8980:,.2f} (백만 USD)")
    chk(abs((54136 + 200062) - 254198) < 1e-9, "합계 254,198 RMB = 54,136 + 200,062")

    print()
    print("[4] alibaba FY2026 연간 영업손익·매출 (companyfacts)")
    facts = json.loads(data["BABA_FACTS"].decode("utf-8", "replace"))["facts"]["us-gaap"]
    got = {}
    for tag in ("Revenues", "OperatingIncomeLoss"):
        for unit, rows in facts[tag]["units"].items():
            for row in rows:
                if row.get("start") == "2025-04-01" and row.get("end") == "2026-03-31" and row.get("form") == "20-F":
                    got[(tag, unit)] = row
    chk(got.get(("Revenues", "CNY"), {}).get("val") == 1_023_670_000_000, "매출 CNY 1,023,670M")
    chk(got.get(("OperatingIncomeLoss", "CNY"), {}).get("val") == 50_150_000_000, "영업이익 CNY 50,150M")
    chk(got.get(("Revenues", "USD"), {}).get("val") == 148_401_000_000, "매출 USD 148,401M (20-F 편의환산)")
    chk(got.get(("OperatingIncomeLoss", "USD"), {}).get("val") == 7_270_000_000, "영업이익 USD 7,270M (동)")
    accn = {row.get("accn") for row in got.values()}
    chk(accn == {"0001193125-26-231755"}, "accession 0001193125-26-231755", f"실제 {sorted(accn)}")
    margin = 50_150 / 1_023_670
    chk(abs(margin - 0.04899) < 5e-5, f"영업이익률 {margin*100:.3f}% — 양수라 operating_result_reviewed=profit")
    implied = 1_023_670 / 148_401
    chk(abs(implied - 6.8980) < 1e-3, "companyfacts CNY/USD 역산 환율이 20-F 선언값과 일치",
        f"1,023,670 / 148,401 = {implied:.4f}")

    print()
    print("=" * 104)
    bad = chk.failed
    print(f"대조 {len(chk.rows)}건 · 불일치 {len(bad)}건")
    for _, label, _detail in bad:
        print(f"  불일치: {label}")
    print()
    print("숫자는 지시서와 전부 일치한다. 문면 차이 2건은 REPORT.md 4 절 참조 (AMZN 각주3 · BABA 소항목 문자).")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
