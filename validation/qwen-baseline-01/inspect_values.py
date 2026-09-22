"""QWEN-BASELINE-01 v2b: 값 수준 추적 + 관측 인벤토리 + 트리거 내용 검토."""
import io
import json
import os
import re
from collections import Counter, OrderedDict, defaultdict

WORKER = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
BL = os.path.join(WORKER, "scorecard", "baseline", "v1.5")
RUN = os.path.join(WORKER, "scorecard", "runs", "ai-scorecard-2026-09-baseline")
ORIG = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
HERE = os.path.dirname(os.path.abspath(__file__))

load = lambda p: json.load(io.open(p, encoding="utf-8"))
read = lambda p: io.open(p, encoding="utf-8").read()

scores = load(os.path.join(BL, "scores.json"))
obs = load(os.path.join(BL, "observations.json"))["items"]
trg = load(os.path.join(BL, "triggers.json"))["items"]
rules = load(os.path.join(WORKER, "scorecard", "rules", "v1.5.json"))
BLC = OrderedDict((c["company_id"], c) for c in scores["companies"])
arr = load(os.path.join(HERE, "html-arrays.json"))

print("=" * 84)
print("[1] 관측 metric 인벤토리")
bym = defaultdict(list)
for o in obs:
    bym[o["metric"]].append(o)
for m in sorted(bym, key=lambda k: (-len(bym[k]), k)):
    lst = bym[m]
    print("  %-26s %3d건  unit=%-10s kind=%-9s 예=%r"
          % (m, len(lst), Counter(o["unit"] for o in lst).most_common(1)[0][0],
             Counter(o["kind"] for o in lst).most_common(1)[0][0],
             lst[0]["observation_id"]))

print("\n" + "=" * 84)
print("[2] source_id=SRC-v15-rule 인 관측 18건 (규칙 원문에서 온 값)")
for o in obs:
    if o["source_id"] == "SRC-v15-rule":
        print("  %-46s metric=%-22s value=%-14r unit=%-8s kind=%-8s note=%r"
              % (o["observation_id"], o["metric"], o["value"], o["unit"], o["kind"], (o.get("note") or "")[:40]))

print("\n" + "=" * 84)
print("[3] raw='raw 없음' 관측 (14건) 전체")
for o in obs:
    if o.get("raw") == "raw 없음":
        print("  " + json.dumps(o, ensure_ascii=False))

print("\n" + "=" * 84)
print("[4] ⑥ 구간표 재현 — ntm_per 관측 → rules band → scores.json F6")
bands = rules["policies"]["f6"]["bands"]


def band_score(per):
    for b in bands:
        if b["upper"] is None or per < b["upper"]:
            return b["score"]
    return None


for o in obs:
    if o["metric"] != "ntm_per":
        continue
    cid = o["company_id"]
    v = o["value"]
    fscore = BLC[cid]["scores"]["F6"]
    if isinstance(v, (int, float)):
        calc = band_score(v)
        ok = "OK" if calc == fscore else "MISMATCH"
        # 경계 ±3%
        warn = [b for b in (20, 29, 42, 62, 90) if abs(v - b) / b <= 0.03]
        print("  %-12s ntm_per=%-8s basis=%-58s band=%-4s F6=%-4s %s  경계⚠️=%s"
              % (cid, v, json.dumps(o.get("basis"), ensure_ascii=False)[:58], calc, fscore, ok, warn or "-"))
    else:
        print("  %-12s ntm_per=%r (비상장/텍스트) F6=%s status=%s kind=%s basis=%s"
              % (cid, v, fscore, o["status"], o["kind"], json.dumps(o.get("basis"), ensure_ascii=False)))

print("\n[4b] 비상장 F6 배수 관측 존재 여부 (anthropic/openai)")
for cid in ("anthropic", "openai"):
    rel = [o for o in obs if o["company_id"] == cid]
    print("  %s 관측 %d건: %s" % (cid, len(rel), sorted(set(o["metric"] for o in rel))))

print("\n" + "=" * 84)
print("[5] 벤치마크 관측 — 지수 버전/평가기관/평가일 필드 유무 (설계 지침 §4.3)")
bm = [o for o in obs if re.search(r"index|arena|bench|aa_|elo|gdpval|tau|hle|arc", o["metric"], re.I)]
print("  벤치마크성 관측: %d건" % len(bm))
for o in bm[:20]:
    print("    " + json.dumps(o, ensure_ascii=False)[:220])
verf = set()
for o in bm:
    verf |= set(k for k in o if "version" in k.lower() or "harness" in k.lower() or "evaluator" in k.lower())
print("  벤치마크 버전/하네스/평가기관 필드: %s" % (sorted(verf) or "없음"))

print("\n" + "=" * 84)
print("[6] ⑨ 원자료 값 수준 추적 — FIN/BORR 표와 observations 대조")
FIN = arr["FIN"]
BORR = arr["BORR"]
NAME2ID = {"Apple": "apple", "NVIDIA": "nvidia", "Microsoft": "microsoft", "Alphabet": "alphabet",
           "Meta": "meta", "TSMC": "tsmc", "Tesla": "tesla", "Palantir": "palantir",
           "Amazon": "amazon", "Alibaba": "alibaba", "SpaceX": "spacex-xai", "Oracle": "oracle",
           "Anthropic": "anthropic", "OpenAI": "openai"}


def clean(x):
    return re.sub(r"<[^>]+>", "", x or "").replace("**", "").replace("✱", "").strip()


def parse_money(s):
    s = clean(s)
    m = re.match(r"^([+\-−]?)\$([\d.]+)([TB]?)$", s)
    if not m:
        return None
    sign = -1 if m.group(1) in "-−" else 1
    v = float(m.group(2)) * (1e12 if m.group(3) == "T" else 1e9 if m.group(3) == "B" else 1)
    return sign * v


fin_by = {}
for r in FIN:
    cid = NAME2ID.get(clean(r[0]).replace("🆕", "").strip())
    if cid:
        fin_by[cid] = r
borr_by = {}
for r in BORR:
    cid = NAME2ID.get(clean(r[0]).replace("🆕", "").strip())
    if cid:
        borr_by[cid] = r
print("  FIN 행 매핑 %d, BORR 행 매핑 %d" % (len(fin_by), len(borr_by)))

MAP = [("cash", 1), ("ttm_fcf", 2), ("runway_years", 3), ("net_cash_debt", 4)]
mism = []
for cid, r in sorted(fin_by.items()):
    for metric, idx in MAP:
        want_txt = clean(r[idx])
        got = [o for o in obs if o["company_id"] == cid and o["metric"] == metric]
        if not got:
            mism.append((cid, metric, want_txt, "관측 없음"))
            continue
        o = got[0]
        wnum = parse_money(want_txt)
        if wnum is None:
            ok = (str(o["value"]) in ("None",) and o["status"] != "legacy_unverified") or \
                 (o["kind"] == "text" and (want_txt in str(o.get("raw")) or str(o.get("raw")) == want_txt))
            if not ok:
                mism.append((cid, metric, want_txt, "value=%r raw=%r status=%s" % (o["value"], o.get("raw"), o["status"])))
        else:
            if not isinstance(o["value"], (int, float)):
                mism.append((cid, metric, want_txt, "value=%r (숫자 아님)" % o["value"]))
            elif abs(o["value"] - wnum) > max(abs(wnum) * 0.005, 5e7):
                mism.append((cid, metric, want_txt, "value=%r (기대 %r)" % (o["value"], wnum)))
for cid, r in sorted(borr_by.items()):
    for metric, idx in [("net_borrowing_ttm", 1), ("capex_ttm", 2)]:
        want_txt = clean(r[idx])
        got = [o for o in obs if o["company_id"] == cid and o["metric"] == metric]
        if not got:
            mism.append((cid, metric, want_txt, "관측 없음"))
            continue
        o = got[0]
        wnum = parse_money(want_txt)
        if wnum is None:
            continue
        if not isinstance(o["value"], (int, float)):
            mism.append((cid, metric, want_txt, "value=%r" % o["value"]))
        elif abs(o["value"] - wnum) > max(abs(wnum) * 0.005, 5e7):
            mism.append((cid, metric, want_txt, "value=%r (기대 %r)" % (o["value"], wnum)))
print("  FIN/BORR 값 불일치·누락: %d건" % len(mism))
for x in mism:
    print("    - %-12s %-20s 원문=%-14s 기준선=%s" % x)

print("\n" + "=" * 84)
print("[7] 컴퓨트 약정 금액 — HANDOVER §2 ($300B / $338B+) vs observations")
for o in obs:
    if re.search(r"comput|contract|commit|offbal|lease|rpo|backlog", o["metric"], re.I):
        print("  %-48s metric=%-24s value=%-16r raw=%r" % (o["observation_id"], o["metric"], o["value"], (o.get("raw") or "")[:60]))
stale80 = [o for o in obs if isinstance(o.get("value"), (int, float)) and 7.5e10 <= o["value"] <= 8.5e10
           and re.search(r"comput|contract|commit", o["metric"], re.I)]
print("  낡은 $80B 값 잔존: %d건" % len(stale80))

print("\n" + "=" * 84)
print("[8] triggers.json 39건 — status/note 와 낡은 점수(C-14)·낡은 경계(C-10) 처리")
print("  status 분포: %s" % dict(Counter(t["status"] for t in trg)))
NOTE_PAT = re.compile(r"C-\d\d")
no_note = [t for t in trg if not NOTE_PAT.search(t.get("note") or "")]
print("  note 에 C-xx 결정 ID 없는 트리거: %d / %d" % (len(no_note), len(trg)))
OLD_SCORE = re.compile(r"[①②③④⑤⑥⑦⑧⑨]\s*-?\d\s*(→|->)\s*-?\d")
OLD_BOUND = re.compile(r"25선|35선|60선|20·25·35·60·90")
flagged_old = []
for t in trg:
    body = (t.get("impact_raw") or "") + (t.get("why") or "") + (t.get("title") or "")
    if OLD_SCORE.search(body) or OLD_BOUND.search(body):
        flagged_old.append(t)
print("  낡은 점수전이(⑥-3→-4 등) 또는 낡은 경계(25선/35선) 문구를 담은 트리거: %d건" % len(flagged_old))
for t in flagged_old:
    has = bool(NOTE_PAT.search(t.get("note") or ""))
    print("    - %-9s noteC=%-5s %s" % (t["trigger_id"], has, t["title"][:56]))
    if not has:
        print("        note=%r" % (t.get("note") or "")[:150])
print("\n  [8b] 트리거 note 표본 6건")
for t in trg[:6]:
    print("    %s | %s" % (t["trigger_id"], t["title"][:40]))
    print("       note: %s" % (t.get("note") or "")[:170])

print("\n" + "=" * 84)
print("[9] 점수 인용이 들어간 트리거 impact_raw (D-09/§9 '다른 기업 점수 인용 금지' 관련)")
cnt = 0
for t in trg:
    if re.search(r"[①②③④⑤⑥⑦⑧⑨]\s*-?\d", t.get("impact_raw") or ""):
        cnt += 1
print("  impact_raw 에 factor 점수 숫자가 하드코딩된 트리거: %d / %d" % (cnt, len(trg)))

print("\n" + "=" * 84)
print("[10] HANDOVER §1 검산값 재현 (⑥·⑨)")
expect = {("oracle", "F6"): 0, ("alphabet", "F6"): -1, ("apple", "F6"): -2,
          ("palantir", "F6"): -4, ("tsmc", "F6"): 0, ("anthropic", "F6"): -3,
          ("openai", "F6"): -4, ("oracle", "F9"): -3, ("spacex-xai", "F9"): -4,
          ("openai", "F9"): -5, ("amazon", "F9"): -2}
for (cid, f), want in expect.items():
    got = BLC[cid]["scores"][f]
    print("  %-12s %s 기대(HANDOVER)=%-3s 기준선=%-3s %s" % (cid, f, want, got, "OK" if got == want else "MISMATCH"))

print("\n" + "=" * 84)
print("[11] run 디렉터리 observations vs baseline observations 비교")
ro = load(os.path.join(RUN, "observations.json"))
ritems = ro["items"] if isinstance(ro, dict) and "items" in ro else ro
print("  run observations: %d건, baseline: %d건" % (len(ritems), len(obs)))
bset = {o["observation_id"]: o for o in obs}
rset = {o["observation_id"]: o for o in ritems}
only_r = set(rset) - set(bset)
only_b = set(bset) - set(rset)
print("  run 에만 있음: %d, baseline 에만 있음: %d" % (len(only_r), len(only_b)))
diff = []
for k in set(rset) & set(bset):
    a, b = rset[k], bset[k]
    for f in ("value", "unit", "status", "kind", "as_of", "source_id"):
        if a.get(f) != b.get(f):
            diff.append((k, f, b.get(f), a.get(f)))
print("  공통 항목 중 필드 차이: %d건" % len(diff))
for d in diff[:30]:
    print("    - %-46s %-10s baseline=%r run=%r" % d)
if ritems:
    print("  run 관측 status 분포: %s" % dict(Counter(o.get("status") for o in ritems)))
    print("  run 관측 sample: %s" % json.dumps(ritems[0], ensure_ascii=False)[:300])
