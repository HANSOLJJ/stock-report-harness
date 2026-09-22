"""QWEN-BASELINE-01 v2: AI 기업 scorecard 기준선(v1.5) 이관 충실성 독립 검증.

대상(읽기 전용):
  worker/scorecard/baseline/v1.5/{scores,observations,triggers}.json, import-report.md
  worker/scorecard/companies.json, worker/scorecard/rules/v1.5.json
  worker/scorecard/runs/ai-scorecard-2026-09-baseline/sources.json
원본(읽기 전용):
  AI기업_채점표_v1.5.md (S-SCORE), AI기업_채점표_v1.5.html (D/VAL/EARN/FIN/BORR/TRIG)

이 스크립트는 대상 파일을 수정·생성하지 않는다(읽기 전용). 결과는 stdout + findings.json.
"""
import hashlib
import io
import json
import os
import re
from collections import Counter, OrderedDict, defaultdict

WORKER = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
BL = os.path.join(WORKER, "scorecard", "baseline", "v1.5")
RUN = os.path.join(WORKER, "scorecard", "runs", "ai-scorecard-2026-09-baseline")
ORIG = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
SRC_MD = os.path.join(ORIG, "AI기업_채점표_v1.5.md")
SRC_HTML = os.path.join(ORIG, "AI기업_채점표_v1.5.html")
SRC_RULE = os.path.join(ORIG, "AI기업_채점규칙_v1.5.md")
HERE = os.path.dirname(os.path.abspath(__file__))

CIRC = "①②③④⑤⑥⑦⑧⑨"
FK = ["F%d" % i for i in range(1, 10)]

FIND = []
STATS = OrderedDict()


def add(fid, sev, area, loc, expected, actual, evidence, repro, note=""):
    FIND.append(OrderedDict(id=fid, severity=sev, area=area, location=loc,
                            expected=expected, actual=actual,
                            evidence=evidence, repro=repro, note=note))


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def strip_html(x):
    return re.sub(r"<[^>]+>", "", x or "")


def norm(x):
    return re.sub(r"\s+", "", strip_html(x))


NAME2ID = OrderedDict([
    ("Alphabet / Google", "alphabet"), ("Amazon / AWS", "amazon"),
    ("Microsoft", "microsoft"), ("Meta", "meta"), ("TSMC", "tsmc"),
    ("Anthropic", "anthropic"), ("Alibaba", "alibaba"), ("Apple", "apple"),
    ("NVIDIA", "nvidia"), ("Palantir", "palantir"), ("SpaceX + xAI", "spacex-xai"),
    ("Tesla", "tesla"), ("Oracle", "oracle"), ("OpenAI", "openai"),
])
# 표시명 별칭 → company_id (이모지·🆕 포함)
ALIAS = {}
for nm, cid in NAME2ID.items():
    ALIAS[nm] = cid
    for part in re.split(r"\s*/\s*|\s*\+\s*", nm):
        ALIAS[part.strip()] = cid
ALIAS.update({"🍎 Apple": "apple", "SpaceX": "spacex-xai", "xAI": "spacex-xai",
              "Google": "alphabet", "Alphabet": "alphabet", "AWS": "amazon"})


def resolve(name):
    n = strip_html(name).replace("**", "").strip()
    n = re.sub(r"🆕", "", n).strip()
    if n in ALIAS:
        return ALIAS[n]
    for k, v in ALIAS.items():
        if k and k in n:
            return v
    return None


# ================================================================= 원본 파싱
md = read(SRC_MD)
md_lines = md.split("\n")
html = read(SRC_HTML)
hlines = html.split("\n")


def ln_of(pat, lines, start=0):
    for i in range(start, len(lines)):
        if re.search(pat, lines[i]):
            return i
    return -1


def to_int(s):
    return int(s.replace("**", "").replace("⚠️", "").replace("📏", "").strip())


# --- MD 1절 순위표 (14열: 순위|기업|①..⑤|과점|⑥..⑨|함정|조정총점)
MDT = OrderedDict()
a = ln_of(r"^## 1\. 종합 순위표", md_lines)
b = ln_of(r"^## 2\. 기업별 상세", md_lines, a)
for k in range(a, b):
    ln = md_lines[k]
    if not ln.startswith("|"):
        continue
    c = [x.strip() for x in ln.strip().strip("|").split("|")]
    if len(c) < 14 or c[0] in ("순위", "") or set(c[0]) <= set("-: "):
        continue
    cid = resolve(c[1])
    if not cid:
        print("[WARN] 순위표 기업명 미해석: %r (line %d)" % (c[1], k + 1))
        continue
    MDT[cid] = OrderedDict(
        rank=to_int(c[0]),
        scores=OrderedDict(zip(FK[:5], [to_int(x) for x in c[2:7]])),
        moat=to_int(c[7]),
    )
    for i, f in enumerate(FK[5:]):
        MDT[cid]["scores"][f] = to_int(c[8 + i])
    MDT[cid]["trap"] = to_int(c[12])
    MDT[cid]["total"] = to_int(c[13])
    MDT[cid]["line"] = k + 1

# --- MD 2절 카드
MDC = OrderedDict()
heads = [k for k in range(len(md_lines)) if re.match(r"^### .+ · 조정 ", md_lines[k])]
heads.append(ln_of(r"^## 3\. 지표 원자료", md_lines))
for x, y in zip(heads, heads[1:]):
    m = re.match(r"^### (.+?) · 조정 (-?\d+)점 \(과점 (-?\d+) / 함정 (-?\d+)\)", md_lines[x])
    if not m:
        print("[WARN] 카드 헤더 파싱 실패 line %d: %r" % (x + 1, md_lines[x]))
        continue
    cid = resolve(m.group(1))
    if not cid:
        print("[WARN] 카드 기업명 미해석 line %d: %r" % (x + 1, m.group(1)))
        continue
    sc = OrderedDict()
    for k in range(x + 1, y):
        fm = re.match(r"^\*\*([①②③④⑤⑥⑦⑧⑨])([^*]*)\*\*\s*·\s*\*\*(-?\d+)\*\*", md_lines[k])
        if fm:
            sc["F%d" % (CIRC.index(fm.group(1)) + 1)] = int(fm.group(3))
    MDC[cid] = OrderedDict(scores=sc, moat=int(m.group(3)), trap=int(m.group(4)),
                           total=int(m.group(2)), head_line=x + 1, head_raw=md_lines[x])

# --- MD 3-1a 시총 표
MD_CAP = {}
i0 = ln_of(r"^### 3-1a\. 가격", md_lines)
i1 = ln_of(r"^### 3-1a-2", md_lines, i0)
for k in range(i0, i1):
    if not md_lines[k].startswith("|"):
        continue
    c = [x.strip() for x in md_lines[k].strip().strip("|").split("|")]
    if len(c) < 9 or c[0] in ("기업", "") or set(c[0]) <= set("-: "):
        continue
    cid = resolve(c[0])
    if not cid:
        continue
    raw_cap = c[2].replace("**", "").replace("✱", "").strip()
    mm = re.match(r"\$([\d.]+)([TB])", raw_cap)
    if mm:
        v = float(mm.group(1))
        MD_CAP[cid] = (v / 1000.0 if mm.group(2) == "B" else v, raw_cap, k + 1)

# --- MD 5절 트리거 표
MD_TRIG = []
t0 = ln_of(r"^## 5\. 다음 분기", md_lines)
for k in range(t0, len(md_lines)):
    ln = md_lines[k]
    if not ln.startswith("|"):
        continue
    c = [x.strip() for x in ln.strip().strip("|").split("|")]
    if len(c) < 3 or c[0] in ("항목", "") or set(c[0]) <= set("-: "):
        continue
    MD_TRIG.append(OrderedDict(item=strip_html(c[0]).replace("**", "").strip(),
                               why=strip_html(c[1]), impact=strip_html(c[2]), line=k + 1))

# --- HTML 배열
def html_block(name):
    i = next(k for k, l in enumerate(hlines) if re.match(r"^const %s\s*=" % name, l))
    out, depth = [], 0
    for k in range(i, len(hlines)):
        out.append(hlines[k])
        depth += hlines[k].count("[") - hlines[k].count("]")
        if k > i and depth <= 0:
            break
    return i + 1, "\n".join(out)


_, DBLK = html_block("D")
HD = []
for rank, name, typ, cap, tag, sv, tv in re.findall(
        r"\{rank:(-?\d+),name:'([^']*)',type:'([^']*)',cap:([0-9.]+),tag:'(.*?)',s:\[([^\]]*)\],t:\[([^\]]*)\]",
        DBLK, re.S):
    HD.append(OrderedDict(rank=int(rank), name=name.strip(), type=typ.strip(),
                          cap=float(cap), tag=tag,
                          s=[int(x) for x in sv.split(",")],
                          t=[int(x) for x in tv.split(",")]))
HD_BY = OrderedDict()
for d in HD:
    cid = resolve(d["name"])
    if cid:
        HD_BY[cid] = d
    else:
        print("[WARN] HTML D 기업명 미해석: %r" % d["name"])


def html_rows(name):
    _, blk = html_block(name)
    out = []
    for line in blk.split("\n"):
        line = line.strip()
        if not (line.startswith("[") and (line.endswith("],") or line.endswith("];") or line.endswith("]"))):
            continue
        body = line.rstrip(";").rstrip(",").strip()
        body = body[1:-1] if body.endswith("]") else body[1:]
        cells = re.findall(r"'((?:[^'\\]|\\.)*)'|(-?[\d.]+)(?=[,\]])", body)
        vals = [(x if x != "" else y) for x, y in cells]
        if vals:
            out.append(vals)
    return out


HVAL = html_rows("VAL")
HFIN = html_rows("FIN")
HBORR = html_rows("BORR")
HEARN = html_rows("EARN")
HTRIG = html_rows("TRIG")

# ================================================================= 기준선
scores = load(os.path.join(BL, "scores.json"))
obsdoc = load(os.path.join(BL, "observations.json"))
trgdoc = load(os.path.join(BL, "triggers.json"))
comp = load(os.path.join(WORKER, "scorecard", "companies.json"))
rules = load(os.path.join(WORKER, "scorecard", "rules", "v1.5.json"))
srcs = load(os.path.join(RUN, "sources.json"))
imp = read(os.path.join(BL, "import-report.md"))

BLC = OrderedDict((c["company_id"], c) for c in scores["companies"])
OBS = obsdoc["items"]
TRG = trgdoc["items"]
COMP = OrderedDict((c["company_id"], c) for c in comp["companies"])

print("=" * 84)
print("원본 파싱 결과")
print("  MD 순위표 %d / MD 카드 %d / HTML D %d / VAL %d / EARN %d / FIN %d / BORR %d"
      % (len(MDT), len(MDC), len(HD), len(HVAL), len(HEARN), len(HFIN), len(HBORR)))
print("  MD 트리거 표 행 %d / HTML TRIG %d / triggers.json %d" % (len(MD_TRIG), len(HTRIG), len(TRG)))
print("  MD 3-1a 시총 행 %d / 기준선 기업 %d / 관측 %d" % (len(MD_CAP), len(BLC), len(OBS)))
STATS["원본_순위표_기업"] = len(MDT)
STATS["원본_카드_기업"] = len(MDC)
STATS["기준선_기업"] = len(BLC)
STATS["기준선_관측"] = len(OBS)
STATS["기준선_트리거"] = len(TRG)

# ============================================================ A. 점수 4-way 대조
print("\n" + "=" * 84)
print("[A] F1~F9·합계·순위 4-way 대조 (HTML D ↔ MD 순위표 ↔ MD 카드 ↔ scores.json)")
nA = 0
for cid in NAME2ID.values():
    hd, mt, mc, bs = HD_BY.get(cid), MDT.get(cid), MDC.get(cid), BLC.get(cid)
    if not (hd and mt and mc and bs):
        add("A-MISS-%s" % cid, "high", "대조 대상 누락", cid,
            "4개 원천 모두 존재", "htmlD=%s mdTable=%s mdCard=%s scores=%s"
            % (bool(hd), bool(mt), bool(mc), bool(bs)), "원본 vs scores.json", "validate_baseline2.py [A]")
        continue
    for i, f in enumerate(FK):
        nA += 1
        v_html = hd["s"][i] if i < 5 else hd["t"][i - 5]
        v_tbl, v_card, v_bl = mt["scores"][f], mc["scores"].get(f), bs["scores"][f]
        vals = {"htmlD": v_html, "md순위표": v_tbl, "md카드": v_card, "scores.json": v_bl}
        if len(set(v for v in vals.values() if v is not None)) > 1:
            sev = "high" if v_bl not in (v_tbl, v_html) else "info"
            area = "점수 이관 오류" if sev == "high" else "원본 내부 불일치(기준선은 원본과 일치)"
            add("A-%s-%s" % (cid, f), sev, area,
                "scores.json companies[%s].scores.%s" % (cid, f),
                "MD 순위표=%s, HTML D=%s" % (v_tbl, v_html), "scores.json=%s / MD 카드=%s" % (v_bl, v_card),
                "MD line %d(순위표) · 카드 line %d · HTML const D" % (mt["line"], mc["head_line"]),
                "validate_baseline2.py [A]", json.dumps(vals, ensure_ascii=False))
    for lbl, k, hv in [("과점", "moat", sum(hd["s"])), ("함정", "trap", sum(hd["t"])),
                       ("조정총점", "total", sum(hd["s"]) + sum(hd["t"])), ("순위", "rank_raw", hd["rank"])]:
        nA += 1
        src_k = "rank" if k == "rank_raw" else k
        vt = mt[src_k]
        vc = mc["total"] if k == "total" else (mc[src_k] if src_k in mc else None)
        vb = bs[k]
        peers = [v for v in (vt, vc, vb, hv) if v is not None]
        if len(set(peers)) > 1:
            sev = "high" if vb != vt or vb != hv else "info"
            add("A-%s-%s" % (k, cid), sev,
                "합계/순위 이관 오류" if sev == "high" else "원본 내부 불일치(기준선은 원본과 일치)",
                "scores.json companies[%s].%s" % (cid, k),
                "MD 순위표 %s=%s" % (lbl, vt),
                "scores.json=%s / MD 카드=%s / HTML D 계산=%s" % (vb, vc, hv),
                "MD line %d · 카드 line %d · HTML const D" % (mt["line"], mc["head_line"]),
                "validate_baseline2.py [A]")
print("  대조 값: %d개" % nA)
STATS["A_대조값"] = nA

# ============================================================ B. 산술·범위·순위
print("\n" + "=" * 84)
print("[B] 기준선 내부 산술 · factor 범위 · 순위 공식")
nB = 0
for cid, x in BLC.items():
    s = x["scores"]
    nB += 3
    mo = sum(s[f] for f in FK[:5])
    tr = sum(s[f] for f in FK[5:])
    if mo != x["moat"]:
        add("B-MOAT-%s" % cid, "high", "산술 오류", "scores.json companies[%s].moat" % cid,
            "F1..F5 합 %d" % mo, "%d" % x["moat"], str(s), "validate_baseline2.py [B]")
    if tr != x["trap"]:
        add("B-TRAP-%s" % cid, "high", "산술 오류", "scores.json companies[%s].trap" % cid,
            "F6..F9 합 %d" % tr, "%d" % x["trap"], str(s), "validate_baseline2.py [B]")
    if mo + tr != x["total"]:
        add("B-TOTAL-%s" % cid, "high", "산술 오류", "scores.json companies[%s].total" % cid,
            "과점+함정 %d" % (mo + tr), "%d" % x["total"], str(s), "validate_baseline2.py [B]")
    for f, spec in rules["factors"].items():
        nB += 1
        lo, hi = spec["range"]
        if not (lo <= s[f] <= hi):
            add("B-RANGE-%s-%s" % (cid, f), "high", "규칙 범위 위반",
                "scores.json companies[%s].scores.%s" % (cid, f),
                "rules/v1.5.json %s range [%s,%s]" % (f, lo, hi), "%d" % s[f],
                "rules/v1.5.json factors.%s" % f, "validate_baseline2.py [B]")
tot = {c: x["total"] for c, x in BLC.items()}
for cid, x in BLC.items():
    nB += 1
    exp = 1 + sum(1 for v in tot.values() if v > x["total"])
    if exp != x["rank_raw"]:
        add("B-RANK-%s" % cid, "high", "순위 공식 오류", "scores.json companies[%s].rank_raw" % cid,
            "1 + (총점이 더 높은 기업 수) = %d" % exp, "%d" % x["rank_raw"],
            "총점 %s" % sorted(tot.values(), reverse=True), "validate_baseline2.py [B]")
    if x.get("md_crosscheck") != "match":
        add("B-XCHK-%s" % cid, "medium", "crosscheck 표시", "scores.json companies[%s].md_crosscheck" % cid,
            "match", repr(x.get("md_crosscheck")), "scores.json", "validate_baseline2.py [B]")
print("  검사 값: %d개" % nB)
STATS["B_검사값"] = nB

# ============================================================ C. 출처 추적
print("\n" + "=" * 84)
print("[C] 출처 ID · 해시 · 원문 위치 추적")
SRC_IDS = set(s["source_id"] for s in srcs["items"])
obs_src = Counter(o["source_id"] for o in OBS)
print("  sources.json: %s" % sorted(SRC_IDS))
print("  observations source_id: %s" % dict(obs_src))
nC = len(OBS)
for sid, c in obs_src.items():
    if sid not in SRC_IDS:
        add("C-SRCID-%s" % sid, "high", "출처 미해결", "observations.json items[source_id=%s] %d건" % (sid, c),
            "sources.json 등록 source_id", "미등록 %r" % sid,
            "runs/ai-scorecard-2026-09-baseline/sources.json", "validate_baseline2.py [C]")

ACT = {"SRC-v15-md": sha256(SRC_MD), "SRC-v15-html": sha256(SRC_HTML), "SRC-v15-rule": sha256(SRC_RULE)}
print("  실제 원본 SHA-256:")
for k, v in ACT.items():
    print("    %-14s %s" % (k, v))
for s in srcs["items"]:
    nC += 1
    got, want = s.get("sha256"), ACT.get(s["source_id"])
    if want and got != want:
        add("C-HASH-%s" % s["source_id"], "high", "출처 해시 불일치",
            "sources.json items[%s].sha256" % s["source_id"], "실제 %s" % want, "기록 %s" % got,
            "Get-FileHash -Algorithm SHA256 <원본>", "validate_baseline2.py [C]")
    if not s.get("url") and not s.get("sha256"):
        add("C-SRCDEF-%s" % s["source_id"], "medium", "출처 정의 불충분",
            "sources.json items[%s]" % s["source_id"], "URL 또는 원문 위치 + 해시", "둘 다 없음",
            json.dumps(s, ensure_ascii=False), "validate_baseline2.py [C]",
            "내부 기준선이라 URL 없음은 정당. 해시로 대체 추적 가능")
for k, want in [("md_sha256", ACT["SRC-v15-md"]), ("html_sha256", ACT["SRC-v15-html"])]:
    nC += 1
    got = scores["source"].get(k)
    if got != want:
        add("C-BLHASH-%s" % k, "high", "기준선 출처 해시 불일치", "scores.json source.%s" % k,
            "실제 원본 %s" % want, "기록 %s" % got, "Get-FileHash 원본", "validate_baseline2.py [C]")

# 원문 위치 표식
CORPUS = norm(md) + norm(html) + norm(read(SRC_RULE))
LOC = re.compile(r"\b(D|VAL|EARN|FIN|BORR|TRIG|HIST)\b")
no_loc = [o for o in OBS if not LOC.search(o.get("note") or "")]
print("  note 에 원문 위치 표식 없는 관측: %d / %d" % (len(no_loc), len(OBS)))
print("  note 표본(위치 표식 없음):")
for o in no_loc[:12]:
    print("     %-46s note=%r" % (o["observation_id"], (o.get("note") or "")[:60]))
if no_loc:
    add("C-LOC", "medium", "원문 위치 표식 부분 누락",
        "observations.json items[*].note (%d/%d건)" % (len(no_loc), len(OBS)),
        "설계 지침 §7.1 출처 필수 = '실제 URL 또는 원문 위치, 인용 위치'",
        "%d건은 note 에 D./VAL./EARN./FIN./BORR./TRIG. 표식 없음" % len(no_loc),
        "예: %s" % ", ".join(o["observation_id"] for o in no_loc[:5]), "validate_baseline2.py [C]",
        "raw 문자열 추적(C-RAW)으로 부분 보완되는지 함께 볼 것")

# raw 추적
def raw_tokens(r):
    ts = [t for t in re.split(r"[\s,;:()/·—\-+]+", r or "") if len(t) >= 3]
    return ts


untrace = []
for o in OBS:
    nC += 1
    r = o.get("raw")
    if not r:
        untrace.append((o["observation_id"], "raw 없음"))
        continue
    ts = raw_tokens(r)
    if not ts:
        continue
    if not any(norm(t) in CORPUS for t in ts):
        untrace.append((o["observation_id"], r))
print("  raw 가 원본(MD+HTML+규칙)에서 추적 안 되는 관측: %d / %d" % (len(untrace), len(OBS)))
for oid, r in untrace[:25]:
    print("     - %-46s raw=%r" % (oid, r))
for oid, r in untrace:
    add("C-RAW-%s" % oid, "medium", "원문 추적 불가",
        "observations.json items[%s].raw" % oid,
        "raw 문자열의 숫자/토큰이 원본 MD·HTML 어딘가에 존재",
        "추적 실패 raw=%r" % r,
        "S-SCORE MD + HTML(D/VAL/EARN/FIN/BORR) 정규화 전문 검색", "validate_baseline2.py [C]")

# basis
bn = [o for o in OBS if o.get("basis") in (None, "")]
print("  basis 비어 있는 관측: %d / %d" % (len(bn), len(OBS)))
bc = Counter(str(o.get("basis")) for o in OBS)
print("  basis 값 분포: %s" % dict(list(bc.items())[:12]))
if bn:
    add("C-BASIS", "medium", "회계·주식 기준(basis) 미기록",
        "observations.json items[*].basis (%d/%d건 null)" % (len(bn), len(OBS)),
        "설계 지침 §7.1 원자료 필수 = '연결/세그먼트, 회계·주식 기준'",
        "%d건이 basis=null (필드는 존재하나 값 없음)" % len(bn),
        "observations.json 전문", "validate_baseline2.py [C]",
        "TSMC(ADR/TWD)·Alibaba(ADS/CNY) 처럼 기준이 점수에 영향 주는 항목 우선 확인 필요")

# 트리거 추적 필드
tk = Counter()
for t in TRG:
    tk.update(t.keys())
print("  triggers.json 필드: %s" % sorted(tk))
for f, req in [("company_id", "대상 기업"), ("factor", "대상 factor"), ("source_id", "근거 ID"),
               ("condition", "조건"), ("due", "기한"), ("review_target", "재검토 대상")]:
    nC += 1
    if tk.get(f, 0) == 0:
        add("C-TRG-%s" % f, "high" if f in ("company_id", "factor", "source_id") else "medium",
            "트리거 추적 필드 누락", "triggers.json items[*].%s" % f,
            "설계 지침 §7.1 트리거 필수 = trigger_id, %s, 관찰 사실·조건·기한, 근거 ID, 현재 상태, 재검토 대상" % req,
            "39건 전부에 %s 필드 없음 (보유: %s)" % (f, sorted(tk)),
            "설계 지침.md §7.1 '트리거' 행", "validate_baseline2.py [C]",
            "제목/why 본문에 기업명·factor가 자연어로만 있어 기계 연결 불가")

# 트리거 내용 추적
tset_md = set(norm(re.sub(r"^[🆕🔑📏🔧⚠️\s]+", "", t["item"])) for t in MD_TRIG)
tset_html = set(norm(strip_html(t[0])) for t in HTRIG)
notrace_t = []
for t in TRG:
    nC += 1
    key = norm(re.sub(r"^[🆕🔑📏🔧⚠️\s]+", "", t["title"]))
    hit = any(key in x or x in key for x in tset_md | tset_html if x)
    if not hit:
        notrace_t.append(t["trigger_id"] + " | " + t["title"][:50])
print("  triggers.json title 이 MD 5절·HTML TRIG 에서 추적 안 되는 건: %d / %d" % (len(notrace_t), len(TRG)))
for x in notrace_t[:15]:
    print("     -", x)
for x in notrace_t:
    add("C-TRGTRACE-%s" % x.split(" ")[0], "medium", "트리거 원문 추적 불가",
        "triggers.json items[%s].title" % x.split(" ")[0],
        "MD 5절 트리거 표 또는 HTML const TRIG 의 항목과 대응", "대응 항목을 찾지 못함: %s" % x,
        "S-SCORE §5 (line %d~) / HTML const TRIG(39행)" % (t0 + 1), "validate_baseline2.py [C]")

# ============================================================ D. 상태·승격
print("\n" + "=" * 84)
print("[D] 자료 상태 · 미수집→0 치환 · 승격")
st = Counter(o["status"] for o in OBS)
kd = Counter(o["kind"] for o in OBS)
un = Counter(str(o["unit"]) for o in OBS)
print("  status: %s" % dict(st))
print("  kind  : %s" % dict(kd))
print("  unit  : %s" % dict(un))
ALLOW = {"verified", "legacy_unverified", "not_disclosed", "collection_failed",
         "source_conflict", "incompatible_basis", "needs_judgment", "needs_rule_decision"}
for s, c in st.items():
    nC += 1
    if s not in ALLOW:
        add("D-STATUS-%s" % s, "low", "자료 상태 이름 비표준",
            "observations.json items[status=%s] %d건" % (s, c),
            "설계 지침 §7.2 상태: %s" % sorted(ALLOW), "status=%r" % s,
            "설계 지침.md §7.2 표", "validate_baseline2.py [D]",
            "의미상 collection_failed/not_disclosed 계열로 보이나 이름이 계약에 없음. 값은 null로 보존돼 D-04는 충족")
prom = [o for o in OBS if o["status"] == "verified"]
print("  verified 승격 관측: %d건" % len(prom))
for o in prom:
    add("D-PROMO-%s" % o["observation_id"], "high", "legacy→verified 승격",
        "observations.json items[%s].status" % o["observation_id"],
        "이관 관측은 legacy_unverified 유지(import-report 선언, D-08)", "verified",
        json.dumps(o, ensure_ascii=False), "validate_baseline2.py [D]")
zero = [o for o in OBS if isinstance(o.get("value"), (int, float)) and not isinstance(o.get("value"), bool) and o["value"] == 0]
print("  value==0 관측: %d건" % len(zero))
for o in zero:
    add("D-ZERO-%s" % o["observation_id"], "high", "미수집→0 치환 의심",
        "observations.json items[%s].value" % o["observation_id"],
        "미공시/미수집이면 null + 사유 상태(D-04)", "value=0 status=%s raw=%r" % (o["status"], o.get("raw")),
        json.dumps(o, ensure_ascii=False), "validate_baseline2.py [D]")
nulls = [o for o in OBS if o.get("value") is None]
print("  value==null 관측: %d건 (status 분포 %s)"
      % (len(nulls), dict(Counter(o["status"] for o in nulls))))
for o in nulls:
    nC += 1
    if o["status"] not in ("not_disclosed", "collection_failed", "incompatible_basis",
                           "needs_judgment", "needs_rule_decision", "parse_failed"):
        add("D-NULLST-%s" % o["observation_id"], "medium", "null 값에 사유 상태 없음",
            "observations.json items[%s].status" % o["observation_id"],
            "값이 없으면 사유 상태(not_disclosed 등)", "value=null, status=%s" % o["status"],
            json.dumps(o, ensure_ascii=False), "validate_baseline2.py [D]")
m = re.search(r"파싱 실패[^\n]*\n\n- (\S+): '(.+?)'", imp, re.S)
if m:
    oid = m.group(1)
    hit = [o for o in OBS if o["observation_id"] == oid]
    nC += 1
    if not hit:
        add("D-PARSE-%s" % oid, "high", "파싱 실패 항목 누락", "observations.json items[%s]" % oid,
            "import-report 선언 항목이 원문 보존됨", "관측 목록에 없음",
            "import-report.md '파싱 실패(원문 보존)'", "validate_baseline2.py [D]")
    else:
        o = hit[0]
        print("  파싱실패 보존: %s value=%r status=%s raw=%r" % (oid, o.get("value"), o["status"], o.get("raw")))
        if isinstance(o.get("value"), (int, float)):
            add("D-PARSEZERO-%s" % oid, "high", "파싱 실패가 숫자로 치환", "observations.json items[%s].value" % oid,
                "숫자 미공시 → null + 사유 상태", "value=%r" % o.get("value"),
                json.dumps(o, ensure_ascii=False), "validate_baseline2.py [D]")
mc = re.search(r"기업 (\d+)개, 관측 (\d+)건, 트리거 (\d+)건", imp)
if mc:
    nC += 1
    decl, real = (int(mc.group(1)), int(mc.group(2)), int(mc.group(3))), (len(BLC), len(OBS), len(TRG))
    if decl != real:
        add("D-COUNT", "medium", "이관 보고 건수 불일치", "import-report.md",
            "실제 기업 %d/관측 %d/트리거 %d" % real, "선언 %s" % (decl,),
            "import-report.md 첫 절", "validate_baseline2.py [D]")
    else:
        print("  import-report 건수 선언 일치: 기업 %d / 관측 %d / 트리거 %d" % real)

# ============================================================ E. 정합성
print("\n" + "=" * 84)
print("[E] 기업 ID · 기간 · 단위 · 통화 · 실적/전망/런레이트")
ids_c, ids_s = list(COMP.keys()), list(BLC.keys())
nC += 1
if set(ids_c) != set(ids_s):
    add("E-IDSET", "high", "기업 ID 집합 불일치", "companies.json vs scores.json",
        "동일 14개 company_id", "차집합 %s" % (set(ids_c) ^ set(ids_s)), "두 파일", "validate_baseline2.py [E]")
if ids_c != ids_s:
    add("E-IDORDER", "low", "기업 ID 순서 불일치", "companies.json vs scores.json",
        "동일 순서(원본 순위표 순)", "companies=%s scores=%s" % (ids_c, ids_s), "두 파일 배열 순서",
        "validate_baseline2.py [E]", "표시 순서 문제이며 점수 영향 없음")
obs_ids = set(o["company_id"] for o in OBS)
for cid in obs_ids - set(ids_c):
    add("E-ORPHAN-%s" % cid, "high", "미등록 company_id", "observations.json items[company_id=%s]" % cid,
        "companies.json 등록 ID", "미등록", "companies.json", "validate_baseline2.py [E]")
for cid in set(ids_c) - obs_ids:
    nC += 1
    add("E-NOOBS-%s" % cid, "medium", "관측 0건 기업", "observations.json (company_id=%s)" % cid,
        "기업별 원자료 관측 존재", "0건", "observations.json", "validate_baseline2.py [E]")
for cid, x in BLC.items():
    nC += 1
    if cid in COMP and COMP[cid]["display_name"] != x["display_name_raw"]:
        add("E-DISP-%s" % cid, "low", "표시명 불일치",
            "companies.json[%s].display_name vs scores.json[%s].display_name_raw" % (cid, cid),
            "동일 표시명(원본은 이모지 포함 '🍎 Apple')",
            "%r vs %r" % (COMP[cid]["display_name"], x["display_name_raw"]), "두 파일 대조",
            "validate_baseline2.py [E]", "scores.json 이 원본 표기를 보존한 쪽 — companies.json 이 별칭 처리")
print("  as_of: scores=%s observations=%s companies=%s" % (scores.get("as_of"), obsdoc.get("as_of"), comp.get("as_of")))
print("  관측 as_of 분포: %s" % dict(Counter(o.get("as_of") for o in OBS)))
nC += 1
if scores.get("as_of") != obsdoc.get("as_of"):
    add("E-ASOF", "medium", "as_of 불일치", "scores.json vs observations.json",
        "동일 기준일", "%s vs %s" % (scores.get("as_of"), obsdoc.get("as_of")), "두 파일", "validate_baseline2.py [E]")

pf = set()
for o in OBS:
    pf |= set(k for k in o if "period" in k.lower() or k in ("period_start", "period_end", "fiscal_period"))
print("  관측의 기간 필드: %s" % (sorted(pf) or "없음"))
nC += 1
if not pf:
    add("E-PERIOD", "high", "원자료 기간 필드 누락", "observations.json items[*]",
        "설계 지침 §7.1 원자료 필수 = '기간'(TTM/FY/분기/YTD), 기준일·공시일·수집일 분리",
        "보유 필드 %s 에 기간 필드 없음. as_of=%s 단일값 241건" % (sorted(OBS[0].keys()), sorted(set(o['as_of'] for o in OBS))),
        "설계 지침.md §7.1 '원자료' 행 · C-17(기준일/재무기간/정보컷오프 분리)", "validate_baseline2.py [E]",
        "TTM FCF·분기 매출·FY 가이던스가 전부 as_of=2026-09-02 하나로 뭉개져 기간 재현 불가")

print("  kind 분포: %s" % dict(kd))
nC += 1
if not ({"run_rate"} & set(kd) and {"estimate"} & set(kd)):
    add("E-KIND", "high", "실적/전망/런레이트 구분 불가", "observations.json items[*].kind",
        "actual/forecast(run_rate)/estimate 구분(D-07)", "kind=%s" % sorted(kd),
        "설계 지침.md §7.1, D-07", "validate_baseline2.py [E]")
RR = re.compile(r"run_rate|runrate|arr|guidance|forecast|consensus|ntm|forward|estimate|target|plan|expected", re.I)
mis = [o for o in OBS if RR.search(o.get("metric") or "") and o.get("kind") == "actual"]
print("  전망/런레이트성 metric 인데 kind=actual: %d건" % len(mis))
for o in mis[:20]:
    print("     - %-46s metric=%s kind=%s value=%r" % (o["observation_id"], o["metric"], o["kind"], o.get("value")))
for o in mis:
    nC += 1
    add("E-KINDMIS-%s" % o["observation_id"], "medium", "실적/전망 구분 오류",
        "observations.json items[%s].kind" % o["observation_id"],
        "metric=%s 은 전망/런레이트 → kind != 'actual' (D-07)" % o["metric"], "kind='actual'",
        json.dumps(o, ensure_ascii=False), "validate_baseline2.py [E]")

dup = [k for k, v in Counter(o["observation_id"] for o in OBS).items() if v > 1]
print("  observation_id 중복: %s" % (dup or "없음"))
for d in dup:
    add("E-DUPID-%s" % d, "high", "observation_id 중복", "observations.json items[%s]" % d,
        "고유 ID", "%d회" % Counter(o['observation_id'] for o in OBS)[d], "observations.json", "validate_baseline2.py [E]")
dupt = [k for k, v in Counter(t["trigger_id"] for t in TRG).items() if v > 1]
print("  trigger_id 중복: %s" % (dupt or "없음"))
cm = Counter((o["company_id"], o["metric"], str(o.get("as_of"))) for o in OBS)
dupcm = OrderedDict((k, v) for k, v in cm.items() if v > 1)
print("  (company,metric,as_of) 중복 조합: %d개" % len(dupcm))
for k, v in list(dupcm.items())[:20]:
    print("     - %s x%d" % (k, v))

# ============================================================ F. 시총 충돌
print("\n" + "=" * 84)
print("[F] 시총(cap) 원천 간 충돌 — HTML D vs VAL/MD 3-1a vs scores.json")
cap_conf = []
for cid, x in BLC.items():
    nC += 1
    d = HD_BY.get(cid)
    v = MD_CAP.get(cid)
    dcap = d["cap"] if d else None
    vcap = v[0] if v else None
    blcap = x["cap_usd_t"]
    if vcap is None:
        continue
    agree_dv = abs(dcap - vcap) < 0.005 if dcap is not None else None
    if agree_dv is False:
        cap_conf.append((cid, dcap, vcap, blcap, v[1], v[2]))
        add("F-CAP-%s" % cid, "medium", "원본 내부 시총 충돌 미표시",
            "scores.json companies[%s].cap_usd_t" % cid,
            "원본 내 두 시총(D.cap=%s T vs VAL/MD 3-1a=%s) 충돌을 source_conflict 로 표시하거나 이관보고에 공지"
            % (dcap, v[1]),
            "cap_usd_t=%s (D 값 채택) · 충돌 미기록 · import-report '불일치·주의: 없음'" % blcap,
            "HTML const D cap:%s / MD §3-1a line %d '%s' / HTML const VAL" % (dcap, v[2], v[1]),
            "validate_baseline2.py [F]",
            "시총은 F6 입력이 아니라 점수 영향 없음. 단 D-05·§7.2 source_conflict 정책과 Q04 관련")
print("  D.cap ≠ VAL/MD 시총 인 상장사: %d개" % len(cap_conf))
for cid, dc, vc, bc, raw, line in cap_conf:
    print("     %-12s D=%-7s VAL/MD=%-10s scores.json=%-7s (MD line %d)" % (cid, dc, raw, bc, line))
if cap_conf:
    nC += 1
    if "없음" in imp and "불일치·주의" in imp:
        add("F-IMPORT", "medium", "이관 보고의 불일치 선언 부정확",
            "import-report.md '## 불일치·주의'",
            "원본 내부 시총 충돌 %d건(D.cap vs VAL/MD 3-1a)을 공지" % len(cap_conf),
            "'- 없음' 으로 선언",
            "HTML const D cap vs MD §3-1a 시총 열", "validate_baseline2.py [F]")

# obs 의 market_cap 중복값
mcaps = defaultdict(list)
for o in OBS:
    if o["metric"] == "market_cap":
        mcaps[o["company_id"]].append(o)
print("  observations market_cap 관측: %d건, 기업 %d곳" % (sum(len(v) for v in mcaps.values()), len(mcaps)))
conf_obs = 0
for cid, lst in sorted(mcaps.items()):
    vals = set(o["value"] for o in lst)
    if len(lst) > 1:
        note = " | ".join("%s=%s(%s,%s)" % (o["observation_id"], o["value"], o["status"], (o.get("note") or "")[:22]) for o in lst)
        print("     %-12s %d건 값%s" % (cid, len(lst), " 일치" if len(vals) == 1 else " 상이"))
        print("        %s" % note)
        if len(vals) > 1:
            conf_obs += 1
            nC += 1
            add("F-MCOBS-%s" % cid, "medium", "동일 지표 상충값 무표시",
                "observations.json items[company_id=%s, metric=market_cap]" % cid,
                "같은 company·metric·as_of 의 상충 값은 source_conflict 표시 또는 단일 정본 선택 근거 기록(§7.2)",
                "서로 다른 값 %s 이 모두 status=%s" % (sorted(vals), set(o["status"] for o in lst)),
                note, "validate_baseline2.py [F]")
print("  상충 market_cap 기업: %d곳" % conf_obs)

# ============================================================ 결과
print("\n" + "=" * 84)
print("[결과] 검사 항목 %d개 · finding %d건" % (nC + nA + nB, len(FIND)))
print("  심각도: %s" % dict(Counter(f["severity"] for f in FIND)))
for a, c in Counter(f["area"] for f in FIND).most_common():
    print("  %-34s %d" % (a, c))

with io.open(os.path.join(HERE, "findings2.json"), "w", encoding="utf-8") as f:
    json.dump(OrderedDict(stats=STATS, checked=nC + nA + nB, findings=FIND), f,
              ensure_ascii=False, indent=2)
print("\n저장: %s" % os.path.join(HERE, "findings2.json"))
