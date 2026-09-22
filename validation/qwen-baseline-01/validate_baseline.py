"""QWEN-BASELINE-01: AI 기업 scorecard 기준선(v1.5) 이관 충실성 독립 검증.

대상(읽기 전용):
  worker/scorecard/baseline/v1.5/{scores,observations,triggers}.json, import-report.md
  worker/scorecard/companies.json
  worker/scorecard/runs/ai-scorecard-2026-09-baseline/sources.json
원본(읽기 전용):
  E:/sourcecode/.../AI_company_analysis_factor/AI기업_채점표_v1.5.md  (S-SCORE)

이 스크립트는 어떤 대상 파일도 수정하지 않는다. 결과는 stdout + findings.json.
"""
import io
import json
import os
import re
import sys
from collections import Counter, OrderedDict

WORKER = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
BL = os.path.join(WORKER, "scorecard", "baseline", "v1.5")
RUN = os.path.join(WORKER, "scorecard", "runs", "ai-scorecard-2026-09-baseline")
SRC_MD = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.md"

CIRC = "①②③④⑤⑥⑦⑧⑨"
FKEY = {c: "F%d" % (i + 1) for i, c in enumerate(CIRC)}

FINDINGS = []


def add(fid, sev, area, path, expected, actual, evidence, repro, note=""):
    FINDINGS.append(OrderedDict(
        id=fid, severity=sev, area=area, location=path,
        expected=expected, actual=actual, evidence=evidence,
        repro=repro, note=note))


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- 원본 파싱
md = read(SRC_MD)
md_lines = md.split("\n")


def find_line(pat, start=0):
    for i in range(start, len(md_lines)):
        if re.search(pat, md_lines[i]):
            return i
    return -1


# 1절 종합 순위표
NAME2ID = OrderedDict([
    ("Alphabet / Google", "alphabet"),
    ("Amazon / AWS", "amazon"),
    ("Microsoft", "microsoft"),
    ("Meta", "meta"),
    ("TSMC", "tsmc"),
    ("Anthropic", "anthropic"),
    ("Alibaba", "alibaba"),
    ("Apple", "apple"),
    ("NVIDIA", "nvidia"),
    ("Palantir", "palantir"),
    ("SpaceX + xAI", "spacex-xai"),
    ("Tesla", "tesla"),
    ("Oracle", "oracle"),
    ("OpenAI", "openai"),
])

md_table = OrderedDict()
i = find_line(r"^## 1\. 종합 순위표")
j = find_line(r"^## 2\. 기업별 상세", i)
for ln in md_lines[i:j]:
    if not ln.startswith("|"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) < 13:
        continue
    if cells[0] in ("순위", "") or set(cells[0]) <= set("-: "):
        continue
    raw_name = cells[1].replace("**", "").strip()
    if raw_name not in NAME2ID:
        print("[WARN] 순위표에서 못 읽은 기업명: %r" % raw_name)
        continue

    def num(s):
        s = s.replace("**", "").replace("⚠️", "").strip()
        return int(s)

    md_table[NAME2ID[raw_name]] = OrderedDict(
        rank=num(cells[0]),
        display=raw_name,
        scores=OrderedDict((FKEY[CIRC[k]], num(cells[2 + k])) for k in range(9)),
        moat=num(cells[7]), trap=num(cells[11]), total=num(cells[12]),
        row_line=md_lines.index(ln) + 1,
    )

# 2절 기업 카드
md_cards = OrderedDict()
card_heads = [k for k in range(len(md_lines)) if re.match(r"^### .+ · 조정 ", md_lines[k])]
card_heads.append(find_line(r"^## 3\. 지표 원자료"))
for a, b in zip(card_heads, card_heads[1:]):
    head = md_lines[a]
    m = re.match(r"^### (.+?) · 조정 (-?\d+)점 \(과점 (-?\d+) / 함정 (-?\d+)\)", head)
    if not m:
        print("[WARN] 카드 헤더 파싱 실패: %r" % head)
        continue
    raw_name = m.group(1)
    raw_name = re.sub(r"^[🥇🥈🥉]\s*", "", raw_name)
    raw_name = re.sub(r"^(1위|공동 \d+위|\d+위)\s*—\s*", "", raw_name).strip()
    if raw_name not in NAME2ID:
        print("[WARN] 카드 기업명 미매핑: %r (헤더 %r)" % (raw_name, head))
        continue
    cid = NAME2ID[raw_name]
    sc = OrderedDict()
    for k in range(a + 1, b):
        fm = re.match(r"^\*\*([①②③④⑤⑥⑦⑧⑨])([^*]*)\*\*\s*·\s*\*\*(-?\d+)\*\*", md_lines[k])
        if fm:
            sc[FKEY[fm.group(1)]] = int(fm.group(3))
    md_cards[cid] = OrderedDict(
        display=raw_name, head_line=a + 1, scores=sc,
        moat=int(m.group(3)), trap=int(m.group(4)), total=int(m.group(2)),
        head_raw=head,
    )

# 5절 트리거
md_trig_start = find_line(r"^## 5\. 다음 분기")
md_trig_lines = md_lines[md_trig_start:]

print("=" * 78)
print("원본 파싱: 순위표 %d개 기업, 카드 %d개 기업, MD 총 %d줄"
      % (len(md_table), len(md_cards), len(md_lines)))
print("트리거 섹션 시작줄:", md_trig_start + 1)

# ---------------------------------------------------------------- 기준선 적재
scores = load(os.path.join(BL, "scores.json"))
obsdoc = load(os.path.join(BL, "observations.json"))
trgdoc = load(os.path.join(BL, "triggers.json"))
comp = load(os.path.join(WORKER, "scorecard", "companies.json"))
srcs = load(os.path.join(RUN, "sources.json"))

bl = OrderedDict((c["company_id"], c) for c in scores["companies"])
obs = obsdoc["items"]
trg = trgdoc["items"]

print("기준선: 기업 %d, 관측 %d, 트리거 %d, companies.json %d, sources %d"
      % (len(bl), len(obs), len(trg), len(comp["companies"]), len(srcs["items"])))

# ================================================================ 검사 A: 점수
print("\n" + "=" * 78)
print("[A] F1~F9 · 합계 · 순위 대조 (원본 순위표 vs 원본 카드 vs scores.json)")

n_checked = 0
for cid in NAME2ID.values():
    t = md_table.get(cid)
    c = md_cards.get(cid)
    b = bl.get(cid)
    if not (t and c and b):
        add("A-MISS-%s" % cid, "high", "점수 대조",
            "scores.json/companies[%s]" % cid,
            "원본 순위표·카드·기준선 모두 존재",
            "table=%s card=%s baseline=%s" % (bool(t), bool(c), bool(b)),
            "S-SCORE 순위표/카드 vs scores.json", "python validate_baseline.py")
        continue
    for f in ["F%d" % k for k in range(1, 10)]:
        n_checked += 1
        vt, vc, vb = t["scores"][f], c["scores"].get(f), b["scores"][f]
        if vc is None:
            add("A-CARDMISS-%s-%s" % (cid, f), "medium", "점수 대조",
                "S-SCORE 카드 %s %s (line %d)" % (cid, f, c["head_line"]),
                "카드에 %s 점수 행 존재" % f, "카드에서 %s 점수를 못 읽음" % f,
                "S-SCORE line %d" % c["head_line"], "validate_baseline.py [A]")
        elif vc != vt:
            add("A-TBL-CARD-%s-%s" % (cid, f), "info", "원본 내부 불일치",
                "S-SCORE %s %s" % (cid, f),
                "순위표와 카드 점수 일치 (순위표=%d)" % vt, "카드=%d" % vc,
                "순위표 line %d / 카드 line %d" % (t["row_line"], c["head_line"]),
                "validate_baseline.py [A]",
                "원본 자체 불일치 — 기준선 이관 오류는 아님(D-08)")
        if vb != vt:
            add("A-SCORE-%s-%s" % (cid, f), "high", "점수 이관 오류",
                "scores.json companies[%s].scores.%s" % (cid, f),
                "원본 순위표 %d" % vt, "기준선 %d" % vb,
                "S-SCORE line %d (순위표), 카드 line %d=%s"
                % (t["row_line"], c["head_line"], vc),
                "validate_baseline.py [A]")
    for lbl, key in [("과점", "moat"), ("함정", "trap"), ("조정총점", "total"), ("순위", "rank")]:
        n_checked += 1
        vt = t[key]
        vb = b["rank_raw"] if key == "rank" else b[key]
        if vb != vt:
            add("A-%s-%s" % (key.upper(), cid), "high", "합계/순위 이관 오류",
                "scores.json companies[%s].%s" % (cid, key if key != "rank" else "rank_raw"),
                "원본 %s %d" % (lbl, vt), "기준선 %d" % vb,
                "S-SCORE line %d" % t["row_line"], "validate_baseline.py [A]")
    # 카드 헤더의 과점/함정/조정 vs 순위표
    for lbl, k in [("과점", "moat"), ("함정", "trap"), ("조정", "total")]:
        if c[k] != t[k]:
            add("A-CARDHEAD-%s-%s" % (cid, k), "info", "원본 내부 불일치",
                "S-SCORE 카드 헤더 line %d" % c["head_line"],
                "순위표 %s=%d" % (lbl, t[k]), "카드 헤더 %s=%d" % (lbl, c[k]),
                c["head_raw"], "validate_baseline.py [A]", "원본 자체 불일치")

print("   대조한 값: %d개 (14사 × 9 factor + 4 합계/순위)" % n_checked)

# ================================================================ 검사 B: 산술
print("\n" + "=" * 78)
print("[B] 기준선 내부 산술 · 순위 공식 재계산")

for cid, b in bl.items():
    s = b["scores"]
    moat = sum(s["F%d" % k] for k in range(1, 6))
    trap = sum(s["F%d" % k] for k in range(6, 10))
    total = moat + trap
    if moat != b["moat"]:
        add("B-MOAT-%s" % cid, "high", "산술 오류", "scores.json companies[%s].moat" % cid,
            "F1..F5 합 = %d" % moat, "저장값 %d" % b["moat"], str(s), "validate_baseline.py [B]")
    if trap != b["trap"]:
        add("B-TRAP-%s" % cid, "high", "산술 오류", "scores.json companies[%s].trap" % cid,
            "F6..F9 합 = %d" % trap, "저장값 %d" % b["trap"], str(s), "validate_baseline.py [B]")
    if total != b["total"]:
        add("B-TOTAL-%s" % cid, "high", "산술 오류", "scores.json companies[%s].total" % cid,
            "과점+함정 = %d" % total, "저장값 %d" % b["total"], str(s), "validate_baseline.py [B]")

totals = {cid: b["total"] for cid, b in bl.items()}
for cid, b in bl.items():
    expect_rank = 1 + sum(1 for v in totals.values() if v > b["total"])
    if expect_rank != b["rank_raw"]:
        add("B-RANK-%s" % cid, "high", "순위 공식 오류",
            "scores.json companies[%s].rank_raw" % cid,
            "1 + (더 높은 총점 수) = %d" % expect_rank, "저장값 %d" % b["rank_raw"],
            "총점 분포 %s" % sorted(totals.values(), reverse=True), "validate_baseline.py [B]")

# factor 범위 검사 (rules/v1.5.json)
rules = load(os.path.join(WORKER, "scorecard", "rules", "v1.5.json"))
for cid, b in bl.items():
    for f, spec in rules["factors"].items():
        lo, hi = spec["range"]
        v = b["scores"][f]
        if not (lo <= v <= hi):
            add("B-RANGE-%s-%s" % (cid, f), "high", "규칙 범위 위반",
                "scores.json companies[%s].scores.%s" % (cid, f),
                "%s 허용 범위 [%s, %s]" % (f, lo, hi), "값 %d" % v,
                "rules/v1.5.json factors.%s.range" % f, "validate_baseline.py [B]")

# md_crosscheck 선언 검증
for cid, b in bl.items():
    if b.get("md_crosscheck") != "match":
        add("B-XCHK-%s" % cid, "medium", "crosscheck 표시",
            "scores.json companies[%s].md_crosscheck" % cid, "match", repr(b.get("md_crosscheck")),
            "scores.json", "validate_baseline.py [B]")

print("   산술·순위·범위·crosscheck 검사 완료 (14사)")

# ================================================================ 검사 C: 출처
print("\n" + "=" * 78)
print("[C] 관측/트리거 출처 ID · 원문 위치 추적")

src_ids = set(s["source_id"] for s in srcs["items"])
obs_src = Counter(o["source_id"] for o in obs)
print("   sources.json source_id: %s" % sorted(src_ids))
print("   observations source_id 분포: %s" % dict(obs_src))
for sid, cnt in obs_src.items():
    if sid not in src_ids:
        add("C-SRCID-%s" % sid, "high", "출처 미해결",
            "observations.json items[source_id=%s] (%d건)" % (sid, cnt),
            "source_id 가 sources.json 에 등록됨", "등록되지 않은 source_id",
            "runs/ai-scorecard-2026-09-baseline/sources.json", "validate_baseline.py [C]")

# sources.json 자체: url=None 이면 원문 위치라도 있어야 함
for s in srcs["items"]:
    if not s.get("url") and not s.get("sha256"):
        add("C-SRCDEF-%s" % s["source_id"], "high", "출처 정의 불충분",
            "sources.json items[%s]" % s["source_id"], "url 또는 원문 위치/해시",
            "둘 다 없음", json.dumps(s, ensure_ascii=False), "validate_baseline.py [C]")

# sources.json 의 sha256 vs 실제 원본 파일 해시
import hashlib


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


ORIG_DIR = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
actual = {
    "SRC-v15-md": sha256(os.path.join(ORIG_DIR, "AI기업_채점표_v1.5.md")),
    "SRC-v15-html": sha256(os.path.join(ORIG_DIR, "AI기업_채점표_v1.5.html")),
    "SRC-v15-rule": sha256(os.path.join(ORIG_DIR, "AI기업_채점규칙_v1.5.md")),
}
for s in srcs["items"]:
    a = actual.get(s["source_id"])
    if a and s.get("sha256") and a != s["sha256"]:
        add("C-HASH-%s" % s["source_id"], "high", "출처 해시 불일치",
            "sources.json items[%s].sha256" % s["source_id"],
            "실제 파일 %s" % a, "기록값 %s" % s["sha256"],
            os.path.join(ORIG_DIR, "원본"), "Get-FileHash")

# scores.json source 해시
for k, want in [("md_sha256", actual["SRC-v15-md"]), ("html_sha256", actual["SRC-v15-html"])]:
    got = scores["source"].get(k)
    if got != want:
        add("C-BLHASH-%s" % k, "high", "기준선 출처 해시 불일치",
            "scores.json source.%s" % k, "실제 원본 %s" % want, "기록값 %s" % got,
            "Get-FileHash 원본 MD/HTML", "validate_baseline.py [C]")

# observation 원문 위치(note) 가 실제 원문에 있는지 표본 추적
loc_pat = re.compile(r"(D|VAL|EARN|FIN|BORR|TRIG|HIST)\.")
no_loc = [o for o in obs if not loc_pat.search(o.get("note") or "")]
print("   note 에 원문 위치 표식(D./VAL./EARN./FIN./BORR./TRIG.) 없는 관측: %d / %d"
      % (len(no_loc), len(obs)))
for o in no_loc:
    add("C-LOC-%s" % o["observation_id"], "medium", "원문 위치 추적 불가",
        "observations.json items[%s].note" % o["observation_id"],
        "원문 위치 표식(예: EARN.ttm_revenue) 또는 검증 가능한 인용 위치",
        "note=%r" % (o.get("note"),),
        "design 지침 §7.1 출처 필수: '실제 URL 또는 원문 위치, 인용 위치'",
        "validate_baseline.py [C]")

# basis 필드 (연결/세그먼트, 회계·주식 기준)
basis_null = [o for o in obs if o.get("basis") in (None, "")]
print("   basis 비어 있는 관측: %d / %d" % (len(basis_null), len(obs)))

# raw 값이 실제 MD 본문에 존재하는지 표본 검사
def norm(s):
    return re.sub(r"\s+", "", s or "")

md_norm = norm(md)
missing_raw = []
for o in obs:
    r = o.get("raw")
    if not r:
        missing_raw.append((o["observation_id"], "raw 없음"))
        continue
    toks = [t for t in re.split(r"[\s,()/]+", r) if len(t) >= 4]
    hit = any(norm(t) in md_norm for t in toks)
    if not hit:
        missing_raw.append((o["observation_id"], r))
print("   raw 문자열이 원본 MD 본문에서 추적되지 않는 관측: %d / %d" % (len(missing_raw), len(obs)))
for oid, r in missing_raw[:40]:
    print("      - %s : %r" % (oid, r))

# 트리거: 회사/factor/근거ID 연결성
trg_keys = Counter()
for t in trg:
    trg_keys.update(t.keys())
print("   트리거 필드: %s" % dict(trg_keys))
need = ["company_id", "factor", "source_id"]
for f in need:
    if trg_keys.get(f, 0) == 0:
        add("C-TRG-%s" % f, "high", "트리거 추적 필드 누락",
            "triggers.json items[*].%s" % f,
            "design 지침 §7.1 트리거 필수: trigger_id, 대상 기업·factor, 근거 ID, 현재 상태, 재검토 대상",
            "39건 전부에 %s 필드 없음 (보유 필드: %s)" % (f, sorted(trg_keys)),
            "설계 지침.md §7.1 '트리거' 행", "validate_baseline.py [C]")

# ================================================================ 검사 D: 상태
print("\n" + "=" * 78)
print("[D] 자료 상태 · 미수집→0 치환 · 승격 검사")

st = Counter(o["status"] for o in obs)
kd = Counter(o["kind"] for o in obs)
un = Counter(str(o["unit"]) for o in obs)
print("   status 분포: %s" % dict(st))
print("   kind   분포: %s" % dict(kd))
print("   unit   분포: %s" % dict(un))

ALLOWED_STATUS = {"verified", "legacy_unverified", "not_disclosed", "collection_failed",
                  "source_conflict", "incompatible_basis", "needs_judgment",
                  "needs_rule_decision"}
for s, c in st.items():
    if s not in ALLOWED_STATUS:
        add("D-STATUS-%s" % s, "medium", "자료 상태 계약 위반",
            "observations.json items[status=%s] (%d건)" % (s, c),
            "설계 지침 §7.2 상태 목록: %s" % sorted(ALLOWED_STATUS), "status=%r" % s,
            "설계 지침.md §7.2", "validate_baseline.py [D]")

# legacy_unverified → verified 승격
promoted = [o for o in obs if o["status"] == "verified"]
print("   verified 로 승격된 관측: %d건" % len(promoted))
for o in promoted:
    add("D-PROMO-%s" % o["observation_id"], "high", "legacy→verified 승격",
        "observations.json items[%s].status" % o["observation_id"],
        "이관 관측은 legacy_unverified 유지 (import-report.md 선언, D-08)",
        "verified", json.dumps(o, ensure_ascii=False), "validate_baseline.py [D]")

# 미수집/미공시가 0으로 치환된 사례
zero = [o for o in obs if isinstance(o.get("value"), (int, float)) and o["value"] == 0]
print("   value==0 관측: %d건" % len(zero))
for o in zero:
    add("D-ZERO-%s" % o["observation_id"], "high", "미수집→0 치환 의심",
        "observations.json items[%s].value" % o["observation_id"],
        "미공시/미수집이면 null + status=not_disclosed|collection_failed (D-04)",
        "value=0, status=%s, raw=%r" % (o["status"], o.get("raw")),
        json.dumps(o, ensure_ascii=False), "validate_baseline.py [D]")

nullv = [o for o in obs if o.get("value") is None]
print("   value==null 관측: %d건" % len(nullv))
for o in nullv:
    if o["status"] not in ("not_disclosed", "collection_failed", "incompatible_basis",
                           "needs_judgment", "needs_rule_decision"):
        add("D-NULLST-%s" % o["observation_id"], "medium", "null 값 상태 부적절",
            "observations.json items[%s].status" % o["observation_id"],
            "값이 없으면 not_disclosed/collection_failed 등 사유 상태",
            "value=null 인데 status=%s" % o["status"],
            json.dumps(o, ensure_ascii=False), "validate_baseline.py [D]")

# import-report 가 선언한 파싱 실패 항목 실재 확인
m = re.search(r"파싱 실패.*?\n\n- (\S+): '(.+?)'", read(os.path.join(BL, "import-report.md")), re.S)
if m:
    oid, rawtxt = m.group(1), m.group(2)
    hit = [o for o in obs if o["observation_id"] == oid]
    if not hit:
        add("D-PARSE-%s" % oid, "high", "파싱 실패 항목 누락",
            "observations.json items[%s]" % oid,
            "import-report.md 가 선언한 파싱 실패 관측이 원문 보존됨",
            "관측 목록에 없음", "import-report.md '파싱 실패(원문 보존)' 절",
            "validate_baseline.py [D]")
    else:
        o = hit[0]
        print("   파싱실패 보존 항목 %s -> value=%r status=%s raw=%r"
              % (oid, o.get("value"), o["status"], o.get("raw")))
        if isinstance(o.get("value"), (int, float)):
            add("D-PARSEZERO-%s" % oid, "high", "파싱 실패가 숫자로 치환됨",
                "observations.json items[%s].value" % oid,
                "숫자 미공시이므로 null + 사유 상태", "value=%r" % o.get("value"),
                json.dumps(o, ensure_ascii=False), "validate_baseline.py [D]")

# counts vs import-report
ir = read(os.path.join(BL, "import-report.md"))
mc = re.search(r"기업 (\d+)개, 관측 (\d+)건, 트리거 (\d+)건", ir)
if mc:
    decl = (int(mc.group(1)), int(mc.group(2)), int(mc.group(3)))
    real = (len(bl), len(obs), len(trg))
    if decl != real:
        add("D-COUNT", "medium", "이관 보고 건수 불일치", "import-report.md",
            "기업 %d / 관측 %d / 트리거 %d" % real, "선언 %s" % (decl,),
            "import-report.md 첫 절", "validate_baseline.py [D]")

# ================================================================ 검사 E: 정합
print("\n" + "=" * 78)
print("[E] 기업 ID · 기간 · 단위 · 통화 · 실적/전망/런레이트 구분")

cids_comp = [c["company_id"] for c in comp["companies"]]
cids_score = [c["company_id"] for c in scores["companies"]]
cids_obs = sorted(set(o["company_id"] for o in obs))
print("   companies.json: %d, scores.json: %d, observations distinct: %d"
      % (len(cids_comp), len(cids_score), len(cids_obs)))
if cids_comp != cids_score:
    add("E-IDORDER", "low", "기업 ID 목록/순서 불일치", "companies.json vs scores.json",
        "동일한 14개 company_id", "companies=%s scores=%s" % (cids_comp, cids_score),
        "두 파일 companies 배열", "validate_baseline.py [E]")
for cid in set(cids_obs) - set(cids_comp):
    add("E-ORPHAN-%s" % cid, "high", "등록되지 않은 company_id",
        "observations.json items[company_id=%s]" % cid,
        "companies.json 에 등록된 company_id", "미등록", "companies.json", "validate_baseline.py [E]")
for cid in set(cids_comp) - set(cids_obs):
    add("E-NOOBS-%s" % cid, "medium", "관측이 없는 기업",
        "observations.json (company_id=%s)" % cid, "기업별 원자료 관측 존재",
        "관측 0건", "observations.json", "validate_baseline.py [E]")

# companies.json display_name vs scores.json display_name_raw
scomp = OrderedDict((c["company_id"], c) for c in comp["companies"])
for cid, b in bl.items():
    if cid in scomp and scomp[cid]["display_name"] != b["display_name_raw"]:
        add("E-DISP-%s" % cid, "low", "표시명 불일치",
            "companies.json[%s].display_name vs scores.json[%s].display_name_raw" % (cid, cid),
            "동일 표시명", "%r vs %r" % (scomp[cid]["display_name"], b["display_name_raw"]),
            "두 파일 대조", "validate_baseline.py [E]")

# as_of 일관성
asof = Counter()
asof["scores.json"] = scores.get("as_of")
asof["observations.json"] = obsdoc.get("as_of")
asof["companies.json"] = comp.get("as_of")
asof["triggers.json(baseline_id)"] = trgdoc.get("baseline_id")
print("   as_of: %s" % dict(asof))
obs_asof = Counter(o.get("as_of") for o in obs)
print("   관측 as_of 분포: %s" % dict(obs_asof))

# 기간(period) 필드 부재 — 설계 지침 §7.1 원자료 필수
period_fields = set()
for o in obs:
    period_fields |= set(k for k in o.keys() if "period" in k.lower())
print("   관측의 기간 관련 필드: %s" % (sorted(period_fields) or "없음"))
if not period_fields:
    add("E-PERIOD", "high", "원자료 기간 필드 누락",
        "observations.json items[*]",
        "설계 지침 §7.1 원자료 필수: '기간'(TTM/FY/분기), 실적/전망/런레이트, 연결/세그먼트, 회계·주식 기준",
        "보유 필드 = %s (period_* 없음)" % sorted(obs[0].keys()),
        "설계 지침.md §7.1 '원자료' 행", "validate_baseline.py [E]")

# kind: 실적/전망/런레이트 구분
print("   kind 값: %s" % dict(kd))
if not any(k in ("forecast", "run_rate", "guidance", "estimate") for k in kd):
    add("E-KIND", "high", "실적/전망/런레이트 구분 불가",
        "observations.json items[*].kind",
        "설계 지침 §7.1·D-07: 실적(actual)/전망(forecast)/런레이트(run_rate) 구분",
        "kind 값이 %s 뿐" % sorted(kd),
        "설계 지침.md §7.1 '원자료' 행, D-07", "validate_baseline.py [E]")

# 런레이트/전망 성격 관측이 actual 로 잘못 표시된 사례 (metric 이름 기반)
RUNRATE_METRIC = re.compile(r"run_rate|runrate|arr|guidance|forecast|consensus|ntm|forward|estimate|target|plan", re.I)
mis = [o for o in obs if RUNRATE_METRIC.search(o.get("metric") or "") and o.get("kind") == "actual"]
print("   metric 이 런레이트/전망성인데 kind=actual 인 관측: %d건" % len(mis))
for o in mis[:30]:
    print("      - %s metric=%s kind=%s value=%r" % (o["observation_id"], o["metric"], o["kind"], o.get("value")))
for o in mis:
    add("E-KINDMIS-%s" % o["observation_id"], "medium", "실적/전망 구분 오류",
        "observations.json items[%s].kind" % o["observation_id"],
        "metric=%s 은 전망/런레이트 성격 → kind != actual (D-07)" % o["metric"],
        "kind='actual'", json.dumps(o, ensure_ascii=False), "validate_baseline.py [E]")

# 통화/단위
print("   unit 값: %s" % dict(un))
CUR = {"USD", "TWD", "CNY", "KRW", "EUR"}
for u, c in un.items():
    if u not in CUR and not re.match(r"^(USD|TWD|CNY)", u):
        pass

# observation_id 중복
dup = [k for k, v in Counter(o["observation_id"] for o in obs).items() if v > 1]
print("   observation_id 중복: %s" % (dup or "없음"))
for d in dup:
    add("E-DUPID-%s" % d, "high", "observation_id 중복", "observations.json items[%s]" % d,
        "고유 observation_id", "%d회 중복" % Counter(o['observation_id'] for o in obs)[d],
        "observations.json", "validate_baseline.py [E]")
dupt = [k for k, v in Counter(t["trigger_id"] for t in trg).items() if v > 1]
print("   trigger_id 중복: %s" % (dupt or "없음"))

# (company, metric, as_of) 중복 — 동일 속성 중복 계상 위험(D-05)
cm = Counter((o["company_id"], o["metric"], str(o.get("as_of"))) for o in obs)
dupcm = [k for k, v in cm.items() if v > 1]
print("   (company,metric,as_of) 중복 조합: %d개" % len(dupcm))
for k in dupcm[:25]:
    print("      - %s x%d" % (k, cm[k]))

# ================================================================ 결과
print("\n" + "=" * 78)
print("[결과] 총 finding %d건" % len(FINDINGS))
bysev = Counter(f["severity"] for f in FINDINGS)
print("   심각도: %s" % dict(bysev))
byarea = Counter(f["area"] for f in FINDINGS)
for a, c in byarea.most_common():
    print("   %-24s %d" % (a, c))

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "findings.json")
with io.open(out, "w", encoding="utf-8") as f:
    json.dump(FINDINGS, f, ensure_ascii=False, indent=2)
print("\nfindings 저장: %s" % out)
