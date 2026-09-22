"""HTML D / VAL / EARN / FIN / BORR / TRIG 배열 추출 (읽기 전용)."""
import io
import json
import re
import os

SRC = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.html"
s = io.open(SRC, encoding="utf-8").read()
lines = s.split("\n")


def block(name):
    i = next(k for k, l in enumerate(lines) if re.match(r"^const %s\s*=" % name, l))
    depth = 0
    out = []
    for k in range(i, len(lines)):
        out.append(lines[k])
        depth += lines[k].count("[") - lines[k].count("]")
        if name in ("D", "HIST") and lines[k].rstrip().endswith("];") and k > i:
            break
        if depth <= 0 and k > i:
            break
    return i + 1, "\n".join(out)


# D 배열: 객체 리터럴이므로 정규식으로 필드 추출
di, dblock = block("D")
print("=== const D (line %d) ===" % di)
recs = re.findall(
    r"\{rank:(-?\d+),name:'([^']*)',type:'([^']*)',cap:([0-9.]+),tag:'(.*?)',s:\[([^\]]*)\],t:\[([^\]]*)\]",
    dblock, re.S)
print("D 레코드 수:", len(recs))
D = []
for rank, name, typ, cap, tag, sv, tv in recs:
    D.append(dict(rank=int(rank), name=name.strip(), type=typ.strip(), cap=float(cap),
                  s=[int(x) for x in sv.split(",")], t=[int(x) for x in tv.split(",")],
                  tag=tag))
for d in D:
    print("  rank=%-3s cap=%-7s s=%-16s t=%-14s %s"
          % (d["rank"], d["cap"], d["s"], d["t"], d["name"]))


def rows(name):
    i, b = block(name)
    r = re.findall(r"^\s*\[(.*?)\],?\s*$", b, re.M)
    parsed = []
    for line in r:
        cells = re.findall(r"'((?:[^'\\]|\\.)*)'|(-?[\d.]+)", line)
        vals = [(a if a != "" else bb) for a, bb in cells]
        parsed.append(vals)
    print("=== const %s (line %d) rows=%d ===" % (name, i, len(parsed)))
    return parsed


VAL = rows("VAL")
for v in VAL:
    print("  ", v[:4])
EARN = rows("EARN")
FIN = rows("FIN")
BORR = rows("BORR")
TRIG = rows("TRIG")
for t in TRIG[:5]:
    print("  TRIG:", [x[:60] for x in t])

out = dict(D=D, VAL=VAL, EARN=EARN, FIN=FIN, BORR=BORR, TRIG=TRIG)
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html-arrays.json")
with io.open(p, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("\n저장:", p)
print("counts: D=%d VAL=%d EARN=%d FIN=%d BORR=%d TRIG=%d"
      % (len(D), len(VAL), len(EARN), len(FIN), len(BORR), len(TRIG)))
