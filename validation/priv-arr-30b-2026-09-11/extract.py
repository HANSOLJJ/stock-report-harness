# PRIV-ARR-30B: 비상장 2사의 F6 입력 4종을 v1.5 원본에서 추출하고 기존 관측과 역대조한다.
# 네트워크 호출 0건. 출처 파일을 열어 인용 줄을 실제 본문에서 재확인한다.
import hashlib
import io
import json
import os

SRC = "E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor"
RULE = os.path.join(SRC, "AI기업_채점규칙_v1.5.md")
TABLE = os.path.join(SRC, "AI기업_채점표_v1.5.md")
OBS = ("C:/Users/noble/orca/workspaces/stock-report-harness/worker/scorecard/runs/"
       "ai-scorecard-2026-09-baseline/observations.json")
HERE = os.path.dirname(os.path.abspath(__file__))


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lines(p):
    return io.open(p, encoding="utf-8").read().split("\n")


RL, TL = lines(RULE), lines(TABLE)
FILES = {"rule": (os.path.basename(RULE), RL), "table": (os.path.basename(TABLE), TL)}


def cite(which, lineno, must):
    """인용 위치를 실제로 열어 대조한다. 해당 줄에 must 가 없으면 실패시킨다."""
    name, arr = FILES[which]
    body = arr[lineno - 1]
    ok = all(m in body for m in must)
    return {"file": name, "line": lineno, "verified": ok,
            "text": body.strip()[:300], "missing": [m for m in must if m not in body]}


# ---- 추출값. value 는 원문 표기를 그대로 옮기고 period 는 원문이 말하는 시점만 적는다 ----
EX = {
 "anthropic": {
  "arr": {"value": 65e9, "raw": "$65B", "period_label": "7월",
          "period_stated": True, "kind": "run_rate",
          "cites": [cite("table", 338, ["$965B", "ARR $65B(7월)", "14.8배"]),
                    cite("table", 911, ["런레이트 $65B(7월)"]),
                    cite("table", 930, ["$65B", "(7월)", "14.8x"])]},
  "arr_prior": {"value": 47e9, "raw": "$47B", "period_label": None,
                "period_stated": False, "kind": "run_rate",
                "cites": [cite("table", 341, ["$47B", "$65B"]),
                          cite("rule", 147, ["ARR $9B→$47B"])]},
  "post_money_valuation": {"value": 965e9, "raw": "$965B", "period_label": "2026/5 Series H",
                           "period_stated": True, "kind": "actual",
                           "cites": [cite("table", 930, ["$965B", "2026/5 Series H"]),
                                     cite("table", 338, ["$965B"])]},
  "cumulative_raised": {"value": 125e9, "raw": "약 $125B", "period_label": "2021년~",
                        "period_stated": True, "kind": "actual",
                        "cites": [cite("rule", 666, ["약 $125B(2021년~)", "0.52"]),
                                  cite("table", 925, ["약 $125B", "0.52"])]},
 },
 "openai": {
  "arr": {"value": 40e9, "raw": "$40B / $40B+", "period_label": "7월 과 8/20 이 원문에서 갈림",
          "period_stated": True, "kind": "run_rate",
          "cites": [cite("rule", 165, ["$25B 정체", "7월", "$40B"]),
                    cite("table", 745, ["$25B에서 정체", "7월", "$40B"]),
                    cite("table", 917, ["런레이트 $40B+(8/20)"]),
                    cite("table", 931, ["$40B", "(8/20)", "21.3x"]),
                    cite("table", 781, ["연매출 $40B(7월)"])]},
  "arr_prior": {"value": 25e9, "raw": "$25B", "period_label": "2~4월(정체 구간)",
                "period_stated": True, "kind": "run_rate",
                "cites": [cite("rule", 165, ["$25B 정체", "(2~4월)"]),
                          cite("table", 745, ["2~4월", "$25B에서 정체"]),
                          cite("table", 771, ["$25B→$40B"])]},
  "post_money_valuation": {"value": 852e9, "raw": "$852B", "period_label": "2026/3 $122B 조달",
                           "period_stated": True, "kind": "actual",
                           "cites": [cite("table", 931, ["$852B", "2026/3 $122B 조달"]),
                                     cite("table", 768, ["$852B"])]},
  "cumulative_raised": {"value": None, "raw": "약 $180~190B", "period_label": None,
                        "period_stated": False, "kind": "actual",
                        "range": [180e9, 190e9],
                        "cites": [cite("rule", 667, ["약 $180~190B", "0.22"]),
                                  cite("table", 926, ["약 $180~190B", "0.22"])]},
 },
}

print("=" * 100)
print("1. 출처 해시 (직접 계산)")
print("=" * 100)
hashes = {}
for label, p in (("규칙", RULE), ("채점표", TABLE)):
    h = sha256(p)
    hashes[os.path.basename(p)] = h
    print("   %-6s %-28s %s" % (label, os.path.basename(p), h))
DECL = "57beb84ad8c291f3086a4b06483cebd1f614befa6e93daeb92657e522b3f7abb"
print("   v1.5.json 선언값 일치(규칙):", hashes[os.path.basename(RULE)] == DECL)

print()
print("=" * 100)
print("2. 인용 위치 대조 — 적은 줄을 실제로 열어 확인")
print("=" * 100)
bad = []
for cid, ms in EX.items():
    for m, d in ms.items():
        for c in d["cites"]:
            if not c["verified"]:
                bad.append((cid, m, c))
            print("   %-9s %-22s %-6s L%-5d %s" % (
                cid, m, c["file"][:6], c["line"], "OK" if c["verified"] else "실패 " + str(c["missing"])))
print("\n   인용 위치 실패 %d건" % len(bad))

print()
print("=" * 100)
print("3. 기존 관측과 역대조")
print("=" * 100)
obs = json.load(io.open(OBS, encoding="utf-8"))["items"]
idx = {(o["company_id"], o["metric"]): o for o in obs
       if o.get("company_id") in EX}
for cid, ms in EX.items():
    for m, d in ms.items():
        o = idx.get((cid, m))
        if not o:
            print("   %-9s %-22s 기존 관측 없음 → 신규 제안" % (cid, m))
            continue
        same = (o.get("value") == d["value"])
        print("   %-9s %-22s 기존 %-16s 원문 %-16s %s | kind=%s status=%s" % (
            cid, m,
            "{:,.0f}".format(o["value"]) if o.get("value") is not None else "None",
            "{:,.0f}".format(d["value"]) if d["value"] is not None else "범위",
            "일치" if same else ("범위" if d["value"] is None else "불일치"),
            o.get("kind"), o.get("status")))
        d["existing"] = {"observation_id": o["observation_id"], "value": o.get("value"),
                         "raw": o.get("raw"), "kind": o.get("kind"),
                         "status": o.get("status"), "matches": same}

out = {"sources": {"files": hashes, "declared_sha256_rule": DECL,
                   "declared_match": hashes[os.path.basename(RULE)] == DECL,
                   "network_calls": 0},
       "extracted": EX, "cite_failures": len(bad)}
io.open(os.path.join(HERE, "priv-arr-extract.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved priv-arr-extract.json")
