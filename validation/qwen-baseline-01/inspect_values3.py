"""QWEN-BASELINE-01 v3: 값 수준 추적(수정) + 원자료 표 내장 점수 독립 대조 + 결측 정책."""
import io
import json
import os
import re
from collections import Counter, OrderedDict, defaultdict

WORKER = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
BL = os.path.join(WORKER, "scorecard", "baseline", "v1.5")
HERE = os.path.dirname(os.path.abspath(__file__))
load = lambda p: json.load(io.open(p, encoding="utf-8"))
read = lambda p: io.open(p, encoding="utf-8").read()

scores = load(os.path.join(BL, "scores.json"))
obs = load(os.path.join(BL, "observations.json"))["items"]
trg = load(os.path.join(BL, "triggers.json"))["items"]
rules = load(os.path.join(WORKER, "scorecard", "rules", "v1.5.json"))
BLC = OrderedDict((c["company_id"], c) for c in scores["companies"])
OBS = defaultdict(dict)
for o in obs:
    OBS[o["company_id"]].setdefault(o["metric"], []).append(o)

html = load(os.path.join(HERE, "html-arrays.json"))
NAME2ID = {"Apple": "apple", "NVIDIA": "nvidia", "Microsoft": "microsoft", "Alphabet": "alphabet",
           "Meta": "meta", "TSMC": "tsmc", "Tesla": "tesla", "Palantir": "palantir",
           "Amazon": "amazon", "Alibaba": "alibaba", "SpaceX": "spacex-xai", "Oracle": "oracle",
           "Anthropic": "anthropic", "OpenAI": "openai", "SpaceX + xAI": "spacex-xai",
           "Amazon / AWS": "amazon", "Alphabet / Google": "alphabet"}


def clean(x):
    x = re.sub(r"<[^>]+>", "", str(x) if x is not None else "")
    return x.replace("**", "").replace("✱", "").replace("🆕", "").strip()


def money(s):
    s = clean(s)
    m = re.match(r"^([+\-])?\$([\d.]+)([TBM]?)$", s)
    if not m:
        return None
    sign = -1 if m.group(1) == "-" else 1
    mult = {"T": 1e12, "B": 1e9, "M": 1e6, "": 1}[m.group(3)]
    return sign * float(m.group(2)) * mult


def num(s):
    s = clean(s).replace("년", "").replace("⚠️", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


FIND = []


def add(fid, sev, area, loc, exp, act, ev, repro, note=""):
    FIND.append(OrderedDict(id=fid, severity=sev, area=area, location=loc, expected=exp,
                            actual=act, evidence=ev, repro=repro, note=note))


# ---------------------------------------------------------------- [6'] FIN/BORR 값 추적
print("=" * 88)
print("[6'] FIN/BORR 원자료 표 ↔ observations 값 대조 (metric 이름 수정)")
FINMAP = [(1, "cash", money), (2, "fcf_ttm", money), (3, "runway_years", num), (4, "net_cash", money)]
BORRMAP = [(1, "net_borrowing_ttm", money), (2, "capex_ttm", money)]
n6 = bad6 = 0
for r in html["FIN"]:
    cid = NAME2ID.get(clean(r[0]))
    if not cid:
        print("   [WARN] FIN 행 기업명 미해석: %r" % r[0])
        continue
    for idx, metric, conv in FINMAP:
        if idx >= len(r):
            continue
        txt = clean(r[idx])
        got = OBS[cid].get(metric, [])
        n6 += 1
        if not got:
            bad6 += 1
            add("G-FINMISS-%s-%s" % (cid, metric), "high", "원자료 값 누락",
                "observations.json (company=%s metric=%s)" % (cid, metric),
                "HTML const FIN[%d] = %r 이 관측으로 이관됨" % (idx, txt), "관측 0건",
                "AI기업_채점표_v1.5.html const FIN 행 '%s'" % clean(r[0]), "inspect_values3.py [6']")
            print("   MISS %-12s %-18s 원문=%r" % (cid, metric, txt))
            continue
        o = got[0]
        w = conv(txt)
        if txt in ("∞", "—", "-", "미공시", "판정 불가", ""):
            ok = (o["value"] is None) or (o["kind"] == "text") or (txt in str(o.get("raw", "")))
            if not ok:
                bad6 += 1
                add("G-FINTEXT-%s-%s" % (cid, metric), "medium", "비숫자 원문 치환 의심",
                    "observations.json items[%s]" % o["observation_id"],
                    "원문 %r 은 비숫자 → null+사유상태 또는 text 보존" % txt,
                    "value=%r status=%s" % (o["value"], o["status"]),
                    json.dumps(o, ensure_ascii=False), "inspect_values3.py [6']")
            continue
        if w is None:
            continue
        if not isinstance(o["value"], (int, float)):
            bad6 += 1
            add("G-FINTYPE-%s-%s" % (cid, metric), "high", "값 유형 불일치",
                "observations.json items[%s].value" % o["observation_id"],
                "원문 %r → %r" % (txt, w), "value=%r" % o["value"],
                json.dumps(o, ensure_ascii=False), "inspect_values3.py [6']")
        elif abs(o["value"] - w) > max(abs(w) * 0.006, 5e7):
            bad6 += 1
            add("G-FINVAL-%s-%s" % (cid, metric), "high", "원자료 값 불일치",
                "observations.json items[%s].value" % o["observation_id"],
                "HTML FIN %r = %r" % (txt, w), "value=%r" % o["value"],
                json.dumps(o, ensure_ascii=False), "inspect_values3.py [6']")
            print("   DIFF %-12s %-18s 원문=%r 기대=%r 실제=%r" % (cid, metric, txt, w, o["value"]))
for r in html["BORR"]:
    cid = NAME2ID.get(clean(r[0]))
    if not cid:
        continue
    for idx, metric, conv in BORRMAP:
        if idx >= len(r):
            continue
        txt = clean(r[idx])
        got = OBS[cid].get(metric, [])
        n6 += 1
        if not got:
            bad6 += 1
            add("G-BORRMISS-%s-%s" % (cid, metric), "high", "원자료 값 누락",
                "observations.json (company=%s metric=%s)" % (cid, metric),
                "HTML const BORR[%d] = %r 이 관측으로 이관됨" % (idx, txt), "관측 0건",
                "AI기업_채점표_v1.5.html const BORR", "inspect_values3.py [6']")
            print("   MISS %-12s %-18s 원문=%r" % (cid, metric, txt))
            continue
        o = got[0]
        w = conv(txt)
        if w is None:
            continue
        if not isinstance(o["value"], (int, float)) or abs(o["value"] - w) > max(abs(w) * 0.006, 5e7):
            bad6 += 1
            add("G-BORRVAL-%s-%s" % (cid, metric), "high", "원자료 값 불일치",
                "observations.json items[%s].value" % o["observation_id"],
                "HTML BORR %r = %r" % (txt, w), "value=%r" % o["value"],
                json.dumps(o, ensure_ascii=False), "inspect_values3.py [6']")
print("   FIN/BORR 대조 %d개, 문제 %d건" % (n6, bad6))

# ---------------------------------------------------------------- [12] VAL/EARN 내장 점수 대조
print("\n" + "=" * 88)
print("[12] 원자료 표에 내장된 점수 독립 대조 — VAL ⑥열, EARN ⑨게이트열 vs scores.json")
n12 = bad12 = 0
for r in html["VAL"]:
    cid = NAME2ID.get(clean(r[0]))
    if not cid:
        print("   [WARN] VAL 행 미해석 %r" % r[0])
        continue
    n12 += 1
    want = int(clean(r[4]))
    got = BLC[cid]["scores"]["F6"]
    if want != got:
        bad12 += 1
        add("H-VAL-F6-%s" % cid, "high", "⑥ 원자료 표 점수 불일치",
            "scores.json companies[%s].scores.F6" % cid, "HTML VAL ⑥열 = %d" % want, "%d" % got,
            "HTML const VAL 행 '%s' / MD §3-1a" % clean(r[0]), "inspect_values3.py [12]")
    # VAL 시총 vs observations market_cap(비-D)
    cap = money(r[2])
    lst = [o for o in OBS[cid].get("market_cap", []) if ".d." not in o["observation_id"]]
    n12 += 1
    if cap is not None and lst and abs(lst[0]["value"] - cap) > max(cap * 0.006, 5e7):
        bad12 += 1
        add("H-VALCAP-%s" % cid, "high", "VAL 시총 ↔ 관측 불일치",
            "observations.json items[%s].value" % lst[0]["observation_id"],
            "HTML VAL 시총 %r = %r" % (clean(r[2]), cap), "%r" % lst[0]["value"],
            "HTML const VAL / MD §3-1a 시총 열", "inspect_values3.py [12]")
for r in html["EARN"]:
    cid = NAME2ID.get(clean(r[0]))
    if not cid:
        print("   [WARN] EARN 행 미해석 %r" % r[0])
        continue
    n12 += 1
    want = int(clean(r[-1]))
    got = BLC[cid]["scores"]["F9"]
    if want != got:
        bad12 += 1
        add("H-EARN-F9-%s" % cid, "high", "⑨ 게이트 열 점수 불일치",
            "scores.json companies[%s].scores.F9" % cid, "HTML EARN ⑨게이트열 = %d" % want, "%d" % got,
            "HTML const EARN 행 '%s' / MD §3-1b" % clean(r[0]), "inspect_values3.py [12]")
print("   VAL 12행 ⑥ + 시총, EARN 14행 ⑨ 대조 %d개, 문제 %d건" % (n12, bad12))

# ---------------------------------------------------------------- [13] 신용표 함정 대조
print("\n" + "=" * 88)
print("[13] MD §3-1a-2 신용 지표 표의 '우리 함정' 열 vs scores.json trap")
md = read(r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.md")
mdlines = md.split("\n")
i0 = next(k for k, l in enumerate(mdlines) if l.startswith("### 3-1a-2"))
i1 = next(k for k, l in enumerate(mdlines) if l.startswith("### 3-1a-3"))
n13 = bad13 = 0
for k in range(i0, i1):
    if not mdlines[k].startswith("|"):
        continue
    c = [x.strip() for x in mdlines[k].strip().strip("|").split("|")]
    if len(c) < 6 or c[0] in ("기업", "") or set(c[0]) <= set("-: "):
        continue
    names = re.findall(r"[A-Za-z][A-Za-z ·+]+", clean(c[0]))
    trap_txt = clean(c[4])
    vals = [int(x) for x in re.findall(r"-?\d+", trap_txt)]
    cids = [NAME2ID[n.strip()] for n in names if n.strip() in NAME2ID]
    for cid in cids:
        n13 += 1
        t = BLC[cid]["trap"]
        if len(vals) == 1:
            ok = (t == vals[0])
        elif len(vals) == 2:
            ok = min(vals) <= t <= max(vals)
        else:
            ok = True
        if not ok:
            bad13 += 1
            add("I-CREDIT-%s" % cid, "medium", "신용 교차검증 표 함정 불일치",
                "scores.json companies[%s].trap" % cid,
                "MD §3-1a-2 '우리 함정' 열 %r" % trap_txt, "trap=%d" % t,
                "MD line %d" % (k + 1), "inspect_values3.py [13]")
    print("   %-34s 우리함정=%-10s 매핑=%s" % (clean(c[0])[:34], trap_txt, cids))
print("   대조 %d개, 문제 %d건" % (n13, bad13))

# ---------------------------------------------------------------- [14] ⑥ 경계 표시 이관
print("\n" + "=" * 88)
print("[14] ⑥ 경계(±3% ⚠️) 표시 이관 여부 — 설계 지침 §5.1 · T-02")
bmetrics = set(o["metric"] for o in obs)
has_b = any(re.search(r"bound|border|warn|edge|distance", m, re.I) for m in bmetrics)
print("   경계 관련 metric 존재: %s" % has_b)
print("   scores.json 에 경계 필드 존재: %s"
      % any("bound" in k.lower() or "warn" in k.lower() for k in scores["companies"][0].keys()))
md_bound = {}
for r in html["VAL"]:
    cid = NAME2ID.get(clean(r[0]))
    if cid:
        md_bound[cid] = clean(r[5])
flagged = {k: v for k, v in md_bound.items() if "⚠️" in v}
print("   원본 VAL 경계열: %s" % json.dumps(md_bound, ensure_ascii=False))
print("   원본에서 ⚠️ 표시된 기업: %s" % flagged)
# 재계산(부동소수점 안전하게 round)
BND = [20, 29, 42, 62, 90]
recalc = {}
for cid, lst in OBS.items():
    for o in lst.get("ntm_per", []):
        if isinstance(o["value"], (int, float)):
            d = min((abs(o["value"] - b) / b, b) for b in BND)
            recalc[cid] = (round(d[0], 6), d[1], round(d[0], 6) <= 0.03)
print("   관측 ntm_per 로 재계산한 경계 거리: %s"
      % json.dumps({k: v for k, v in recalc.items()}, ensure_ascii=False))
mism14 = []
for cid, txt in md_bound.items():
    orig_flag = "⚠️" in txt
    rc = recalc.get(cid)
    calc_flag = rc[2] if rc else None
    if orig_flag != calc_flag:
        mism14.append((cid, txt, rc))
print("   원본 ⚠️ 와 재계산 ⚠️ 불일치: %s" % mism14)
if not has_b:
    add("J-BOUND", "medium", "⑥ 경계 표시 미이관",
        "observations.json / scores.json (경계 필드 부재)",
        "설계 지침 §5.1 '경계는 20·29·42·62·90이며 min(|PER-경계|/경계)<=0.03 이면 주의 표시' · T-02."
        " 원본 HTML VAL 5열(경계)과 MD §3-1a '경계' 열이 이관되어야 함",
        "경계 metric/필드 없음. 원본 ⚠️ 표식(%s)이 기준선에 보존되지 않음"
        % json.dumps(flagged, ensure_ascii=False),
        "HTML const VAL[5] / MD §3-1a 경계 열", "inspect_values3.py [14]",
        "점수는 바꾸지 않는 표시 정보이나, 재계산 시 TSMC 19.4 는 |19.4-20|/20=0.030000000000000006"
        " 으로 부동소수점 때문에 ⚠️ 를 놓침 → 원문 보존 또는 허용오차 비교가 필요")

# ---------------------------------------------------------------- [15] 결측 정책 상태
print("\n" + "=" * 88)
print("[15] incompatible_basis / not_disclosed / parse_failed 관측 전체 목록")
for st in ("incompatible_basis", "not_disclosed", "parse_failed"):
    lst = [o for o in obs if o["status"] == st]
    print("   --- %s : %d건" % (st, len(lst)))
    for o in lst:
        print("       %-48s metric=%-20s value=%-16r raw=%r"
              % (o["observation_id"], o["metric"], o["value"], (o.get("raw") or "")[:56]))
        if o["value"] is not None and st != "parse_failed":
            add("K-STVAL-%s" % o["observation_id"], "medium", "차단 상태인데 값 보유",
                "observations.json items[%s]" % o["observation_id"],
                "%s 상태는 계산 입력 차단(설계 지침 §7.2) → 값은 참조용으로만" % st,
                "value=%r (숫자)" % o["value"], json.dumps(o, ensure_ascii=False),
                "inspect_values3.py [15]",
                "incompatible_basis 는 비교·합산 차단이므로 G4 커버리지 계산에 쓰이면 안 됨(C-07)")

# raw 비어 있는 관측
noraw = [o for o in obs if not (o.get("raw") or "").strip()]
print("   --- raw 비어 있는 관측: %d건" % len(noraw))
for o in noraw:
    print("       %-46s metric=%-16s value=%r note=%r" % (o["observation_id"], o["metric"], o["value"], o.get("note")))
if noraw:
    add("K-NORAW", "medium", "원문 인용(raw) 없는 관측",
        "observations.json items[*].raw (%d건)" % len(noraw),
        "설계 지침 §7.1 원자료 필수 = '원값·정규화 값' + 출처의 '인용 위치'. raw 는 원문 인용 문자열",
        "%d건이 raw 빈 문자열 (metric=%s)" % (len(noraw), sorted(set(o['metric'] for o in noraw))),
        "observations.json 전문", "inspect_values3.py [15]",
        "quarter_note 는 HTML EARN 의 분기 표기인데 raw 가 비어 원문 추적이 불가")

# note 비어 있는 관측
nonote = [o for o in obs if not (o.get("note") or "").strip()]
print("   --- note(원문 위치) 비어 있는 관측: %d건" % len(nonote))
print("       metric 분포: %s" % dict(Counter(o["metric"] for o in nonote)))

# ---------------------------------------------------------------- [16] G4 커버리지 재현
print("\n" + "=" * 88)
print("[16] ⑨ 게이트4 커버리지 재현 (contracted_revenue / offbalance_B)")
for cid in sorted(OBS):
    cr = OBS[cid].get("contracted_revenue", [])
    ob = OBS[cid].get("offbalance_B", [])
    if not (cr or ob):
        continue
    crv = cr[0]["value"] if cr else None
    crs = cr[0]["status"] if cr else None
    obv = ob[0]["value"] if ob else None
    obs_ = ob[0]["status"] if ob else None
    cov = (crv / obv) if isinstance(crv, (int, float)) and isinstance(obv, (int, float)) and obv else None
    print("   %-12s 수입=%-16s(%-19s) B종=%-16s(%-19s) 커버리지=%s"
          % (cid, crv, crs, obv, obs_, ("%.3f" % cov) if cov else "계산 불가"))
    if cov is not None and crs == "incompatible_basis":
        add("L-G4-%s" % cid, "medium", "차단 상태로 커버리지 계산 가능",
            "observations.json items[%s.contracted_revenue]" % cid,
            "incompatible_basis 는 비교·합산 차단(§7.2, C-07) → 커버리지 산출 불가로 표시",
            "값이 숫자라 %s ÷ %s = %.3f 가 계산됨" % (crv, obv, cov),
            json.dumps(cr[0], ensure_ascii=False), "inspect_values3.py [16]",
            "R02(calc_f9 coverage_comparable) 와 관련 — 데이터 쪽에서도 비교 불가 표시가 필요")

# ---------------------------------------------------------------- [17] triggers 경계/낡은값
print("\n" + "=" * 88)
print("[17] triggers.json 에서 ⑥ 경계 트리거(C-10) 처리 확인")
for t in trg:
    if "경계" in t["title"] or "25선" in (t.get("why") or "") or "35선" in (t.get("why") or ""):
        print("   %s | %s" % (t["trigger_id"], t["title"]))
        print("      why   : %s" % (t.get("why") or "")[:200])
        print("      impact: %s" % (t.get("impact_raw") or "")[:160])
        print("      note  : %s" % (t.get("note") or "")[:200])
        if "25선" in (t.get("why") or "") or "35선" in (t.get("why") or ""):
            if "C-10" not in (t.get("note") or ""):
                add("M-TRG-C10-%s" % t["trigger_id"], "medium", "낡은 ⑥ 경계 미표시",
                    "triggers.json items[%s]" % t["trigger_id"],
                    "활성 경계 20·29·42·62·90 기준으로 표시하거나 note 에 C-10 명시(설계 지침 C-10)",
                    "why/impact 에 옛 경계 25선·35선 문구, note=%r" % (t.get("note") or "")[:80],
                    "S-SCORE §5 트리거 표 / rules/v1.5.json decisions C-10", "inspect_values3.py [17]")

print("\n" + "=" * 88)
print("[결과 v3] finding %d건 · 심각도 %s" % (len(FIND), dict(Counter(f["severity"] for f in FIND))))
for a, c in Counter(f["area"] for f in FIND).most_common():
    print("   %-32s %d" % (a, c))
with io.open(os.path.join(HERE, "findings3.json"), "w", encoding="utf-8") as f:
    json.dump(FIND, f, ensure_ascii=False, indent=2)
print("저장:", os.path.join(HERE, "findings3.json"))
