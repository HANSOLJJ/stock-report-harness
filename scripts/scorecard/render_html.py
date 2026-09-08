# 승인된 실행 결과를 단일 파일 대시보드 HTML 로 렌더하고 history.csv 를 갱신하는 scorecard 빌더 (dashboard-design 스킬 기준 준수)
from __future__ import annotations

import html as html_lib
import json
import math
from pathlib import Path
from typing import Any

from report_contract_lib import OUTPUT_DIR, artifact_paths, rel

from .engine import HISTORY_CSV, load_context, load_results, run_dir
from .inputs import ObsLookup
from .render_csv import append_history, history_rows
from .render_md import DISCLAIMER, FACTOR_LABELS, REVIEW_AREAS, STATUS_LABEL, fmt_num, fmt_pct, fmt_score, fmt_usd
from .schema import FACTOR_IDS, MOAT_FACTORS, TRAP_FACTORS, SchemaError, load_json_strict, sha256_file, validate_approval
from .stages import current_hashes, load_baseline

GENERATOR = "stock-report-harness scorecard-builder"
SHORT = {"F1": "①", "F2": "②", "F3": "③", "F4": "④", "F5": "⑤", "F6": "⑥", "F7": "⑦", "F8": "⑧", "F9": "⑨"}
TYPE_CLASS = {"소비자": "consumer", "업무": "work", "거래": "trade", "부품": "part", "소비자·업무": "consumer", "혼합": "mix"}


def esc(value: Any) -> str:
    return html_lib.escape(str(value), quote=True)


# ------------------------------------------------------------------ 색 도우미

def score_class(score: int | None) -> str:
    if score is None:
        return "g0"
    return {5: "g5", 4: "g4", 3: "g3", 2: "g2", 1: "g1"}.get(score, "g0")


def trap_class(score: int | None) -> str:
    if score is None:
        return "g0"
    if score == 0:
        return "g5"
    if score >= -1:
        return "g4"
    if score >= -2:
        return "g3"
    if score >= -3:
        return "g2"
    return "g1"


def total_class(total: int | None) -> str:
    if total is None:
        return "g0"
    if total >= 15:
        return "g5"
    if total >= 12:
        return "g4"
    if total >= 6:
        return "g3"
    if total >= 1:
        return "g2"
    return "g1"


# ------------------------------------------------------------------ CSS

def css() -> str:
    return """
:root{
  --bg:#0e1116;--bg2:#161a22;--bg3:#1d222c;--line:#2b313d;
  --tx:#e6e9ee;--tx2:#a3abba;--tx3:#7c8595;
  --g5:#1eb287;--g4:#4ad39c;--g3:#e9be4a;--g2:#f08a47;--g1:#e04e52;--g0:#4c5566;
  --acc:#5ea6f6;--warn:#e6a23c;--dang:#e04e52;
  --acc-soft:rgba(94,166,246,.10);--acc-line:rgba(94,166,246,.30);--acc-text:#bcd6fa;
  --good-soft:rgba(74,211,156,.09);--good-line:rgba(74,211,156,.28);--good-text:#a9edd0;
  --bad-soft:rgba(224,78,82,.09);--bad-line:rgba(224,78,82,.28);--bad-text:#f4a5a7;
  --warn-soft:rgba(230,162,60,.10);--warn-line:rgba(230,162,60,.32);--warn-text:#f6d8a3;
  --cat-consumer:#5ea6f6;--cat-work:#4ad39c;--cat-trade:#b195f5;--cat-part:#f0a05c;--cat-mix:#f28cc0;
  --cat-trade-soft:rgba(177,149,245,.14);--cat-part-soft:rgba(240,160,92,.14);--cat-mix-soft:rgba(242,140,192,.14);
  --fs-xs:11px;--fs-sm:12px;--fs-md:13px;--fs-base:14px;--fs-lg:16px;--fs-xl:18px;--fs-2xl:22px;--fs-3xl:26px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{font-size:var(--fs-base)}
body{background:var(--bg);color:var(--tx);font-family:'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased;padding:0 0 64px;font-variant-numeric:tabular-nums}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
h1{font-size:clamp(24px,4vw,34px);font-weight:800;letter-spacing:-.02em;line-height:1.25}
h2{font-size:clamp(18px,2.4vw,24px);font-weight:700;margin:48px 0 8px;letter-spacing:-.01em}
h2 .num{color:var(--acc);margin-right:8px}
h3{font-size:var(--fs-xl);font-weight:700;margin:24px 0 8px}
p{font-size:var(--fs-base)}
.sub{color:var(--tx2);font-size:var(--fs-md)}
.mono{font-variant-numeric:tabular-nums}
.num-cell{text-align:right}
a{color:var(--acc);text-decoration:none;overflow-wrap:anywhere}
a:hover{text-decoration:underline}
header{background:var(--bg2);border-bottom:1px solid var(--line);padding:32px 0 24px;margin-bottom:8px}
.badge{display:inline-block;background:var(--acc-soft);color:var(--acc);border:1px solid var(--acc-line);padding:4px 10px;border-radius:99px;font-size:var(--fs-sm);font-weight:600;margin-bottom:12px}
.lede{color:var(--tx2);font-size:var(--fs-base);margin-top:10px;max-width:720px}
.notice{border:1px solid var(--warn-line);border-left:3px solid var(--warn);background:var(--warn-soft);border-radius:8px;padding:12px 14px;font-size:var(--fs-md);color:var(--warn-text);margin:16px 0}
.notice.info{border-color:var(--acc-line);border-left-color:var(--acc);background:var(--acc-soft);color:var(--acc-text)}
.notice.bad{border-color:var(--bad-line);border-left-color:var(--dang);background:var(--bad-soft);color:var(--bad-text)}
.notice.good{border-color:var(--good-line);border-left-color:var(--g4);background:var(--good-soft);color:var(--good-text)}
.notice b{color:inherit}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(178px,100%),1fr));gap:12px;margin:20px 0}
.kpi{background:var(--bg2);border:1px solid var(--line);border-radius:10px;padding:14px 16px;min-width:0}
.kpi .k{font-size:var(--fs-sm);color:var(--tx3);font-weight:600}
.kpi .v{font-size:var(--fs-3xl);font-weight:800;margin:4px 0 2px;letter-spacing:-.02em;overflow-wrap:anywhere}
.kpi .d{font-size:var(--fs-md);color:var(--tx2)}
.chartbox{background:var(--bg2);border:1px solid var(--line);border-radius:12px;padding:16px;margin:16px 0;min-width:0}
.chartbox svg{width:100%;height:auto;display:block}
.legend{display:flex;flex-wrap:wrap;gap:12px 16px;margin-top:12px;font-size:var(--fs-md);color:var(--tx2)}
.legend i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:middle}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--bg2)}
table{border-collapse:collapse;width:100%;font-size:var(--fs-md)}
th,td{padding:10px 8px;text-align:center;border-bottom:1px solid var(--line);white-space:nowrap;vertical-align:middle}
th{background:var(--bg3);font-weight:700;font-size:var(--fs-sm);color:var(--tx2)}
th.sort{cursor:pointer;user-select:none}
th.sort:hover{color:var(--tx)}
th[aria-sort="ascending"]::after{content:" ▲";font-size:var(--fs-xs)}
th[aria-sort="descending"]::after{content:" ▼";font-size:var(--fs-xs)}
th.name,td.name{text-align:left;padding-left:14px}
td.text,th.text{text-align:left;white-space:normal;min-width:180px;line-height:1.5}
tbody tr.row{cursor:pointer}
tbody tr.row:hover{background:var(--acc-soft)}
.rk{display:inline-flex;align-items:center;justify-content:center;min-width:24px;height:24px;padding:0 6px;border-radius:6px;background:var(--bg3);font-size:var(--fs-sm);font-weight:700;color:var(--tx2)}
.rk.top{background:var(--good-soft);color:var(--g4)}
.sc{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:24px;padding:0 4px;border-radius:6px;font-weight:700;font-size:var(--fs-md);color:#0b0d11}
.sc.g0{color:var(--tx)}
.bg-g5{background:var(--g5)}.bg-g4{background:var(--g4)}.bg-g3{background:var(--g3)}.bg-g2{background:var(--g2)}.bg-g1{background:var(--g1)}.bg-g0{background:var(--g0)}
.c-g5{color:var(--g5)}.c-g4{color:var(--g4)}.c-g3{color:var(--g3)}.c-g2{color:var(--g2)}.c-g1{color:var(--g1)}.c-g0{color:var(--tx3)}
.tot{font-weight:800;font-size:var(--fs-lg)}
.divider{border-left:2px solid var(--line)}
.pending-list{list-style:none;margin:12px 0 0}
.pending-list li{padding:8px 12px;border:1px solid var(--warn-line);background:var(--warn-soft);border-radius:8px;margin:6px 0;font-size:var(--fs-md);color:var(--warn-text)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(340px,100%),1fr));gap:12px;margin-top:14px}
.card{background:var(--bg2);border:1px solid var(--line);border-radius:12px;overflow:hidden;min-width:0}
.card[open]{grid-column:1/-1;border-color:var(--acc-line)}
.card>summary{padding:14px 16px;cursor:pointer;list-style:none;display:flex;align-items:flex-start;gap:12px;min-height:44px}
.card>summary::-webkit-details-marker{display:none}
.card[open]>summary{border-bottom:1px solid var(--line)}
.chead{flex:1;min-width:0}
.cname{font-weight:700;font-size:var(--fs-lg);display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.pill{font-size:var(--fs-xs);font-weight:700;padding:2px 7px;border-radius:99px;background:var(--bg3);color:var(--tx2)}
.pill.consumer{background:var(--acc-soft);color:var(--cat-consumer)}
.pill.work{background:var(--good-soft);color:var(--cat-work)}
.pill.trade{background:var(--cat-trade-soft);color:var(--cat-trade)}
.pill.part{background:var(--cat-part-soft);color:var(--cat-part)}
.pill.mix{background:var(--cat-mix-soft);color:var(--cat-mix)}
.pill.warn{background:var(--warn-soft);color:var(--warn-text)}
.ctag{font-size:var(--fs-md);color:var(--tx2);margin-top:4px;line-height:1.45}
.cscore{text-align:right;flex-shrink:0}
.cscore .t{font-size:var(--fs-3xl);font-weight:800;letter-spacing:-.03em;line-height:1}
.cscore .s{font-size:var(--fs-xs);color:var(--tx3);margin-top:3px;white-space:nowrap}
.cbody{padding:6px 16px 14px}
.card[open] .cbody{display:grid;grid-template-columns:1fr 1fr;gap:0 28px;align-items:start}
.cgrp{min-width:0}
.cgh{font-size:var(--fs-xs);font-weight:800;letter-spacing:.04em;padding:6px 0 2px}
.cgh.p{color:var(--g4)}.cgh.n{color:var(--g2)}
.frow{padding:10px 0;border-bottom:1px solid var(--line);font-size:var(--fs-md)}
.frow:last-child{border-bottom:none}
.fhead{display:flex;align-items:baseline;gap:8px;margin-bottom:4px;flex-wrap:wrap}
.flab{color:var(--tx2);font-weight:700;font-size:var(--fs-md);white-space:nowrap}
.fsc{font-weight:900;font-size:var(--fs-base);min-width:22px;white-space:nowrap}
.fst{color:var(--tx3);font-size:var(--fs-xs);flex:1 1 auto;min-width:0;line-height:1.4}
.fcalc{color:var(--tx3);font-size:var(--fs-sm);margin:2px 0 4px;overflow-wrap:anywhere}
.fpts{margin:0;padding-left:16px;color:var(--tx);line-height:1.55}
.fpts li{margin:2px 0}
.fpts li.warn{color:var(--warn-text)}
details.blk{background:var(--bg2);border:1px solid var(--line);border-radius:10px;margin:10px 0;overflow:hidden}
details.blk>summary{padding:12px 16px;cursor:pointer;font-weight:700;font-size:var(--fs-base);list-style:none;display:flex;justify-content:space-between;min-height:44px;align-items:center}
details.blk>summary::-webkit-details-marker{display:none}
details.blk>summary::after{content:'▾';color:var(--tx3)}
details.blk[open]>summary::after{content:'▴'}
details.blk .inner{padding:0 16px 14px}
ul.tight{margin:8px 0 0 18px;font-size:var(--fs-md);color:var(--tx)}
ul.tight li{margin:4px 0;overflow-wrap:anywhere}
footer{margin-top:48px;padding-top:20px;border-top:1px solid var(--line);color:var(--tx3);font-size:var(--fs-md)}
footer p{margin:6px 0;font-size:var(--fs-md)}
.w8{font-weight:800}.b{font-weight:700}.big{font-size:var(--fs-lg)}.narrow{min-width:0}
.mt-8{margin-top:8px}.mt-12{margin-top:12px}.mt-14{margin-top:14px}
tr.priv{opacity:.75}
.pill.legacy{background:var(--warn-soft);color:var(--warn-text);margin-right:4px}
.m-only{display:none}
@media(max-width:860px){.card[open] .cbody{grid-template-columns:1fr}}
@media(max-width:640px){
  .cards{grid-template-columns:1fr}
  .kpi .v{font-size:var(--fs-2xl)}
  .m-only{display:inline}
  #mainTable{border-collapse:separate;border-spacing:0}
  #mainTable th:not(.keep),#mainTable td:not(.keep){display:none}
  #mainTable th:first-child,#mainTable td:first-child{position:sticky;left:0;z-index:2;background:var(--bg2)}
  #mainTable th:first-child{background:var(--bg3)}
  #mainTable th.name,#mainTable td.name{position:sticky;left:46px;z-index:2;background:var(--bg2);max-width:132px;overflow:hidden;text-overflow:ellipsis}
  #mainTable th.name{background:var(--bg3)}
  #mainTable tbody tr.row:hover td{background:var(--bg2)}
}
""".strip()


# ------------------------------------------------------------------ JS

def js() -> str:
    return """
(function(){
  const table=document.getElementById('mainTable'); if(!table) return;
  const tbody=table.tBodies[0];
  const head=[...table.tHead.rows[0].cells];
  let sortKey='total',dir=-1;
  function val(tr,k){const cell=tr.querySelector('[data-k="'+k+'"]'); if(!cell) return null; const n=Number(cell.dataset.v); return Number.isFinite(n)?n:cell.textContent.trim();}
  function draw(){
    const rows=[...tbody.rows];
    rows.sort((a,b)=>{const x=val(a,sortKey),y=val(b,sortKey); if(typeof x==='string'||typeof y==='string') return dir*String(x).localeCompare(String(y)); return dir*(x-y);});
    rows.forEach(r=>tbody.appendChild(r));
    head.forEach(th=>{th.removeAttribute('aria-sort'); if(th.dataset.k===sortKey) th.setAttribute('aria-sort',dir<0?'descending':'ascending');});
  }
  head.forEach(th=>{ if(!th.dataset.k) return; th.classList.add('sort'); th.setAttribute('tabindex','0');
    const go=()=>{const k=th.dataset.k; dir=(sortKey===k)?-dir:-1; sortKey=k; draw();};
    th.addEventListener('click',go); th.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();go();}}); });
  tbody.addEventListener('click',e=>{const tr=e.target.closest('tr.row'); if(!tr) return; const card=document.getElementById('card-'+tr.dataset.company); if(!card) return; card.open=true; card.scrollIntoView({behavior:'smooth',block:'start'});});
  draw();
})();
""".strip()


# ------------------------------------------------------------------ 산점도 (Python 결정론적 배치)

def scatter_svg(results: dict[str, Any], caps: dict[str, float | None]) -> str:
    W, H = 900, 470
    M = {"t": 24, "r": 28, "b": 52, "l": 62}
    iw, ih = W - M["l"] - M["r"], H - M["t"] - M["b"]
    scored = [c for c in results["companies"] if c["complete"] and not c["reference"]]
    if not scored:
        return '<p class="sub">완료 기업이 없어 산점도를 그리지 않는다.</p>'
    xs = (min(12, min(c["moat"] for c in scored)), max(23, max(c["moat"] for c in scored)))
    ys = (min(-19, min(c["trap"] for c in scored)), 1)

    def X(v: float) -> float:
        return M["l"] + (v - xs[0]) / (xs[1] - xs[0]) * iw

    def Y(v: float) -> float:
        return M["t"] + (ys[1] - v) / (ys[1] - ys[0]) * ih

    parts = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="과점 factor 대비 함정 감점 산점도. 오른쪽일수록 과점 구조가 강하고 위일수록 함정이 얕다">']
    for v in range(int(math.floor(xs[0])), int(math.ceil(xs[1])) + 1, 2):
        parts.append(f'<line x1="{X(v):.1f}" y1="{M["t"]}" x2="{X(v):.1f}" y2="{M["t"] + ih}" style="stroke:var(--line)"/><text x="{X(v):.1f}" y="{M["t"] + ih + 22}" style="fill:var(--tx3)" font-size="12" text-anchor="middle">{v}</text>')
    v = 0
    while v >= ys[0]:
        parts.append(f'<line x1="{M["l"]}" y1="{Y(v):.1f}" x2="{M["l"] + iw}" y2="{Y(v):.1f}" style="stroke:var(--line)"/><text x="{M["l"] - 12}" y="{Y(v) + 4:.1f}" style="fill:var(--tx3)" font-size="12" text-anchor="end">{v}</text>')
        v -= 3
    parts.append(f'<line x1="{X(20):.1f}" y1="{M["t"]}" x2="{X(20):.1f}" y2="{M["t"] + ih}" style="stroke:var(--g5)" stroke-width="1.5" stroke-dasharray="5 4" opacity=".65"/><text x="{X(20) + 7:.1f}" y="{M["t"] + 14}" style="fill:var(--g5)" font-size="12" font-weight="600">과점 후보군 20점</text>')
    parts.append(f'<text x="{M["l"] + iw / 2:.1f}" y="{H - 10}" style="fill:var(--tx2)" font-size="13" text-anchor="middle" font-weight="600">과점 factor (높을수록 구조가 강함) →</text>')
    parts.append(f'<text transform="translate(17,{M["t"] + ih / 2:.1f}) rotate(-90)" style="fill:var(--tx2)" font-size="13" text-anchor="middle" font-weight="600">← 함정 감점 (위일수록 얕음)</text>')
    groups: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for c in scored:
        groups.setdefault((c["moat"], c["trap"]), []).append(c)
    entries = []
    for (moat, trap), group in sorted(groups.items()):
        sizes = [(caps.get(c["company_id"]) or 0.5e12) / 1e12 for c in group]
        r = max(7.0, min(30.0, 8 + math.sqrt(max(sizes)) * 9))
        color = f"var(--cat-{TYPE_CLASS.get(group[0]['type'], 'mix')})"
        names = " · ".join(short_name(c["display_name"]) for c in group)
        entries.append({"x": X(moat), "y": Y(trap), "r": r, "color": color, "names": names, "total": group[0]["total"], "group": group})
    placed = [{"x": e["x"], "y": e["y"], "w": e["r"] * 2 + 8, "h": e["r"] * 2 + 8} for e in entries]
    for e in entries:
        parts.append(f'<circle cx="{e["x"]:.1f}" cy="{e["y"]:.1f}" r="{e["r"]:.1f}" style="fill:{e["color"]}" opacity=".18"/><circle cx="{e["x"]:.1f}" cy="{e["y"]:.1f}" r="{e["r"]:.1f}" fill="none" style="stroke:{e["color"]}" stroke-width="2" opacity=".9"/>')
        if len(e["group"]) > 1:
            for k, c in enumerate(e["group"]):
                parts.append(f'<circle cx="{e["x"] + (k - (len(e["group"]) - 1) / 2) * 8:.1f}" cy="{e["y"]:.1f}" r="2.6" style="fill:var(--cat-{TYPE_CLASS.get(c["type"], "mix")})"/>')
        else:
            parts.append(f'<circle cx="{e["x"]:.1f}" cy="{e["y"]:.1f}" r="3" style="fill:{e["color"]}"/>')
    for e in sorted(entries, key=lambda x: x["y"]):
        label = f'{e["names"]}  {e["total"]}점'
        w, hh = len(label) * 7.4 + 10, 19
        sx = e["r"] + w / 2 + 8
        cands = [(0, -(e["r"] + 10)), (0, e["r"] + 20), (sx, 4), (-sx, 4), (0, -(e["r"] + 28)), (0, e["r"] + 38), (sx, -16), (-sx, 22), (sx, 26), (-sx, -20),
                 (0, -(e["r"] + 46)), (0, e["r"] + 56), (sx, -34), (-sx, 40), (sx, 44), (-sx, -38), (sx + 30, 4), (-sx - 30, 4), (0, -(e["r"] + 64)), (0, e["r"] + 74)]

        def clashes(x: float, y: float) -> int:
            n = sum(1 for b in placed if abs(b["x"] - x) < (b["w"] + w) / 2 + 5 and abs(b["y"] - (y - hh / 2 + 7)) < (b["h"] + hh) / 2 + 6)
            if x - w / 2 < M["l"] - 10 or x + w / 2 > W - 4 or y - hh < 10 or y > H - M["b"] + 6:
                n += 9
            return n

        px, py, best = e["x"], e["y"] - (e["r"] + 10), 10 ** 9
        for dx, dy in cands:
            n = clashes(e["x"] + dx, e["y"] + dy)
            if n == 0:
                px, py, best = e["x"] + dx, e["y"] + dy, 0
                break
            if n < best:
                best, px, py = n, e["x"] + dx, e["y"] + dy
        placed.append({"x": px, "y": py - hh / 2 + 7, "w": w, "h": hh})
        if math.hypot(px - e["x"], py - e["y"]) > e["r"] + 24:
            parts.append(f'<line x1="{e["x"]:.1f}" y1="{e["y"]:.1f}" x2="{px:.1f}" y2="{py + (5 if py < e["y"] else -11):.1f}" style="stroke:{e["color"]}" stroke-width="1" opacity=".4"/>')
        parts.append(f'<text x="{px:.1f}" y="{py:.1f}" text-anchor="middle" font-size="12" font-weight="700"><tspan style="fill:var(--tx)">{esc(e["names"])}</tspan> <tspan class="c-{total_class(e["total"])}" font-weight="800">{e["total"]}점</tspan></text>')
    parts.append("</svg>")
    return "".join(parts)


def market_caps(ctx: Any) -> dict[str, float | None]:
    obs = ObsLookup(ctx.observations)
    return {cid: obs.number(cid, "market_cap")[0] or obs.number(cid, "post_money_valuation")[0] for cid in ctx.run["companies"]}


def short_name(name: str) -> str:
    return name.replace(" / AWS", "").replace(" / Google", "").replace(" + xAI", "+xAI").replace("🍎 ", "")


# ------------------------------------------------------------------ 섹션 렌더

def render_kpis(results: dict[str, Any]) -> str:
    ranking = results["ranking"]
    if not ranking:
        return '<div class="notice bad">완료 기업이 없어 KPI 를 계산하지 않는다.</div>'
    top = [r for r in ranking if r["rank"] == 1]
    second = max((r["total"] for r in ranking if r["total"] < top[0]["total"]), default=None)
    moat_pool = [c for c in results["companies"] if not c["reference"] and c["moat"] is not None]
    max_moat = max(c["moat"] for c in moat_pool)
    moat_top = [c["display_name"] + ("" if c["complete"] else "(미완료)") for c in moat_pool if c["moat"] == max_moat]
    worst = min(ranking, key=lambda r: r["trap"])
    cands = [c for c in moat_pool if c["moat"] >= 20]
    pop = results["population"]
    lead = f"{len(top)}개사 공동" if len(top) > 1 else top[0]["display_name"]
    lead_d = " · ".join(r["display_name"] for r in top) if len(top) > 1 else (f"2위와 {top[0]['total'] - second}점 차" if second is not None else "단독")
    return "".join([
        f'<div class="kpi"><div class="k">{"공동" if len(top) > 1 else "단독"} 1위 (조정 {top[0]["total"]}점)</div><div class="v">{esc(lead)}</div><div class="d">{esc(lead_d)}</div></div>',
        f'<div class="kpi"><div class="k">과점 factor 최고</div><div class="v">{max_moat}점</div><div class="d">{esc(" · ".join(moat_top))}</div></div>',
        f'<div class="kpi"><div class="k">함정 최심 (완료 {pop["scored"]}개사 기준)</div><div class="v c-g1">{worst["trap"]}</div><div class="d">{esc(worst["display_name"])} — 조정 {worst["total"]}점</div></div>',
        f'<div class="kpi"><div class="k">과점 후보군</div><div class="v">{len(cands)}개사</div><div class="d">과점 20점 이상 · {esc(" · ".join(c["display_name"] + ("" if c["complete"] else "(미완료)") for c in cands))}</div></div>',
        f'<div class="kpi"><div class="k">모집단</div><div class="v">{pop["scored"]}개사</div><div class="d">미완료 {len(pop["incomplete"])}개사 순위 제외</div></div>',
    ])


def render_ranking(results: dict[str, Any]) -> str:
    rows = []
    by_id = {c["company_id"]: c for c in results["companies"]}
    for r in results["ranking"]:
        c = by_id[r["company_id"]]
        f = c["factors"]
        cells = [f'<td class="keep" data-k="rank" data-v="{r["rank"]}"><span class="rk{" top" if r["rank"] <= 3 else ""}">{r["rank"]}</span></td>',
                 f'<td class="name keep" data-k="name" data-v="{esc(r["display_name"])}"><b>{esc(r["display_name"])}</b></td>']
        for x in MOAT_FACTORS:
            s = f[x]["score"]
            cells.append(f'<td data-k="{x}" data-v="{s}"><span class="sc bg-{score_class(s)}">{fmt_score(s)}</span></td>')
        cells.append(f'<td class="divider mono keep" data-k="moat" data-v="{r["moat"]}"><b class="big">{r["moat"]}</b></td>')
        for x in TRAP_FACTORS:
            s = f[x]["score"]
            cells.append(f'<td data-k="{x}" data-v="{s}"><span class="mono c-{trap_class(s)}" >{fmt_score(s)}</span></td>')
        cells.append(f'<td class="mono keep b" data-k="trap" data-v="{r["trap"]}">{r["trap"]}</td>')
        cells.append(f'<td class="divider mono tot keep c-{total_class(r["total"])}" data-k="total" data-v="{r["total"]}">{r["total"]}</td>')
        rows.append(f'<tr class="row" data-company="{esc(r["company_id"])}">{"".join(cells)}</tr>')
    head = ('<tr><th class="keep" data-k="rank">#</th><th class="name keep" data-k="name">기업</th>'
            + "".join(f'<th data-k="{x}">{SHORT[x]}{esc(FACTOR_LABELS[x][2:])}</th>' for x in MOAT_FACTORS)
            + '<th class="divider keep" data-k="moat">과점</th>'
            + "".join(f'<th data-k="{x}">{SHORT[x]}{esc(FACTOR_LABELS[x][2:])}</th>' for x in TRAP_FACTORS)
            + '<th class="keep" data-k="trap">함정</th><th class="divider keep" data-k="total">조정총점</th></tr>')
    return f'<div class="tablewrap"><table id="mainTable"><thead>{head}</thead><tbody>{"".join(rows)}</tbody></table></div>'


def render_incomplete(results: dict[str, Any], rules: Any) -> str:
    items = results["population"]["incomplete"]
    if not items:
        return ""
    lis = []
    for i in items:
        reasons = "; ".join(f"{FACTOR_LABELS[p['factor']]} {STATUS_LABEL.get(p['status'], p['status'])}" + (f" ({p['decision_id']})" if p.get("decision_id") else "") for p in i["reasons"])
        lis.append(f'<li><b>{esc(i["display_name"])}</b> — {esc(reasons)}</li>')
    decisions = "".join(f'<li><b>{esc(d)}</b> {esc((rules.decision(d) or {}).get("summary", ""))}</li>' for d in results["pending_rule_decisions"])
    return (f'<div class="notice bad mt-14"><b>미완료 {len(items)}개사는 순위에서 제외했다.</b> 0점으로 채우지 않는다.</div>'
            f'<ul class="pending-list">{"".join(lis)}</ul>'
            + (f'<h3>필요한 규칙 결정</h3><ul class="tight">{decisions}</ul>' if decisions else ""))


def render_cards(results: dict[str, Any], baseline: dict[str, Any] | None, companies: dict[str, dict[str, Any]], observations: list[dict[str, Any]] | None = None) -> str:
    observations = observations or []
    base = {b["company_id"]: b for b in (baseline or {}).get("companies", [])}
    ordered = sorted(results["companies"], key=lambda c: (c["rank"] is None, c["rank"] or 0, -(c["moat"] or 0), c["company_id"]))
    out = []
    for c in ordered:
        b = base.get(c["company_id"], {})
        cls = TYPE_CLASS.get(c["type"], "mix")
        incompatible_g4 = any(o["company_id"] == c["company_id"] and o["metric"] in ("contracted_revenue", "offbalance_B") and o["status"] == "incompatible_basis" for o in observations)
        head = f'{c["rank"]}위' if c["rank"] else "미완료"
        groups = []
        for label, factors, klass, total in (("과점 — 더한다 (각 0~5)", MOAT_FACTORS, "p", c["moat"]), ("함정 — 뺀다 (각 0~-5)", TRAP_FACTORS, "n", c["trap"])):
            rows = []
            for f in factors:
                fr = c["factors"][f]
                score = fr["score"]
                color = f"c-{score_class(score) if f in MOAT_FACTORS else trap_class(score)}"
                evidence = b.get("evidence", {}).get(f, [])[:6]
                pts = [esc(e) for e in evidence]
                if evidence and f == "F9" and incompatible_g4:
                    pts.append("(원문 커버리지 계산은 ARR·연환산 약정 기반이라 C-07 로 이번 실행 미적용)")
                pts += [f'<li class="warn">⚠️ {esc(w)}</li>' for w in fr["warnings"][:4]]
                calc = factor_calc_text(f, fr)
                if evidence:
                    header = "기준선 근거(승계 판단)" if (fr["status"] == "carried_score" or fr["basis"] in ("manual", "carried")) else "기준선 서술(참고 — 이번 실행은 입력에서 자동 산출)"
                    calc = (calc + " · " if calc else "") + header
                body = ("<ul class=\"fpts\">" + "".join(p if p.startswith("<li") else f"<li>{p}</li>" for p in pts) + "</ul>") if pts else ""
                rows.append(f'<div class="frow"><div class="fhead"><span class="flab">{esc(FACTOR_LABELS[f])}</span><span class="fsc {color}">{fmt_score(score)}</span><span class="fst">{esc(STATUS_LABEL.get(fr["status"], fr["status"]))} · {esc(fr["basis"])}</span></div>{f"<div class=\"fcalc\">{esc(calc)}</div>" if calc else ""}{body}</div>')
            groups.append(f'<div class="cgrp"><div class="cgh {klass}">{esc(label)} · 합 {fmt_score(total)}</div>{"".join(rows)}</div>')
        out.append(
            f'<details class="card" id="card-{esc(c["company_id"])}" data-company="{esc(c["company_id"])}"><summary><div class="chead"><div class="cname">{esc(c["display_name"])}<span class="pill {cls}">{esc(c["type"])}</span>'
            + ("" if c["complete"] else '<span class="pill warn">미완료</span>')
            + f'</div><div class="ctag">' + (f'<span class="pill legacy">기준선 {esc(results["baseline_id"])} 요약 · 과거 기록</span> {esc(b.get("tag", ""))}' if b.get("tag") else "") + '</div></div><div class="cscore"><div class="t c-{total_class(c["total"])}">{fmt_score(c["total"])}</div><div class="s">{head} · 과점 {fmt_score(c["moat"])} / 함정 {fmt_score(c["trap"])}</div></div></summary>'
            f'<div class="cbody">{"".join(groups)}</div></details>'
        )
    return "".join(out)


def runway_text(c: dict[str, Any], obs: ObsLookup) -> str:
    value = runway_for(c, obs)
    if value is not None:
        return fmt_num(value)
    o = obs.get(c["company_id"], "runway_years")
    return esc((o.get("raw") or o["status"]) if o and o.get("value") is None else "—")


def runway_for(c: dict[str, Any], obs: ObsLookup) -> float | None:
    """G3 계산 런웨이가 있으면 그 값을, 없으면 승계 관측을 쓴다 (표와 계산이 갈라지지 않게)."""
    for p in (c["factors"]["F9"].get("calc") or {}).get("path", []):
        if p.get("gate") == "G3" and p.get("runway_years") is not None:
            return float(p["runway_years"])
    return obs.number(c["company_id"], "runway_years")[0]


def factor_calc_text(f: str, fr: dict[str, Any]) -> str:
    calc = fr.get("calc") or {}
    text = ""
    if f == "F6" and calc.get("ntm_per") is not None:
        text = f"NTM PER {fmt_num(calc['ntm_per'])} ({calc.get('method', '')}) → 구간 {calc.get('band', '')}"
        if (calc.get("boundary") or {}).get("flag"):
            text += " ⚠️ 경계 ±3%"
    elif f == "F6" and "valuation_over_arr" in calc:
        text = f"밸류÷ARR {fmt_num(calc['valuation_over_arr'])}x · ARR÷조달 {fmt_num(calc.get('arr_over_cumulative_raised'), 2)}"
    elif f == "F3" and "pass_points" in calc:
        text = f"통과점 {calc['pass_points']:g} — {calc.get('ladder_note', '')}"
    elif f == "F5" and "A" in calc:
        text = f"3 + A({calc['A']}) + H({calc['H']})"
    elif f == "F7" and "funding_dependent_share" in calc:
        text = f"조달 의존 비중 {calc['funding_dependent_share']} · 환류 {calc['own_money_returns']}"
    elif f == "F9" and calc.get("path"):
        text = " → ".join(f"{p['gate']} {p.get('result') or p.get('adjust') or p.get('mode') or ''}" + (f" {p['runway_years']:.1f}년" if "runway_years" in p else "") + (f" 커버리지 {p['coverage']:.2f}" if p.get("coverage") is not None else "") for p in calc["path"])
    pending = fr.get("pending") or {}
    if pending:
        text = (text + " · " if text else "") + pending.get("message", "")
    return text


def render_raw_tables(ctx: Any, results: dict[str, Any]) -> str:
    obs = ObsLookup(ctx.observations)
    val_rows, priv_rows, fin_rows, borr_rows = [], [], [], []
    for c in results["companies"]:
        cid, name = c["company_id"], c["display_name"]
        if c["listed"]:
            per, per_obs = obs.number(cid, "ntm_per")
            method = ((per_obs or {}).get("basis") or {}).get("method", "—")
            f6 = c["factors"]["F6"]
            flag = "⚠️" if ((f6.get("calc") or {}).get("boundary") or {}).get("flag") else "—"
            nonop = obs.number(cid, "nonop_share")[0]
            val_rows.append(f'<tr><td class="name"><b>{esc(name)}</b></td><td class="mono">{fmt_usd(obs.number(cid, "price")[0], 2)}</td><td class="mono">{fmt_usd(obs.number(cid, "market_cap")[0], 2)}</td><td class="mono w8">{fmt_num(per)}</td><td class="text narrow">{esc(method)}</td><td class="mono w8">{fmt_score(f6["score"])}</td><td>{flag}</td><td class="mono">{fmt_num(obs.number(cid, "ttm_per")[0])}</td><td class="mono{" c-g1" if (nonop or 0) >= 0.3 else ""}">{fmt_pct(nonop)}</td><td class="mono">{fmt_num(obs.number(cid, "ps_ratio")[0])}</td></tr>')
        else:
            calc = c["factors"]["F6"].get("calc") or {}
            priv_rows.append(f'<tr><td class="name"><i>{esc(name)}</i></td><td class="mono">{fmt_usd(obs.number(cid, "post_money_valuation")[0])}</td><td class="mono">{fmt_usd(obs.number(cid, "arr")[0])}</td><td class="mono">{fmt_num(calc.get("valuation_over_arr"))}x</td><td class="mono">{fmt_usd(obs.number(cid, "cumulative_raised")[0])}</td><td class="mono">{fmt_num(calc.get("arr_over_cumulative_raised"), 2)}</td><td class="mono w8">{fmt_score(c["factors"]["F6"]["score"])}</td></tr>')
        fcf, fcf_obs = obs.number(cid, "fcf_ttm")
        fcf_text = fmt_usd(fcf) if fcf is not None else esc((fcf_obs or {}).get("raw") or "—")
        fcf_cls = "c-g1" if (fcf or 0) < 0 else ("c-g5" if fcf else "c-g0")
        rating = (obs.get(cid, "credit_rating") or {}).get("value") or "—"
        note = (obs.get(cid, "offbalance_note") or {}).get("value") or "—"
        fin_rows.append(f'<tr{"" if c["listed"] else " class=\"priv\""}><td class="name"><b>{esc(name)}</b></td><td class="mono">{fmt_usd(obs.number(cid, "cash")[0])}</td><td class="mono w8 {fcf_cls}">{fcf_text}</td><td class="mono">{runway_text(c, obs)}</td><td class="mono">{fmt_usd(obs.number(cid, "net_cash")[0])}</td><td class="mono">{fmt_num(obs.number(cid, "debt_ebitda")[0], 2)}</td><td>{esc(rating)}</td><td class="text">{esc(note)}</td><td class="mono w8">{fmt_score(c["factors"]["F9"]["score"])}</td></tr>')
        nb, nb_obs = obs.number(cid, "net_borrowing_ttm")
        if nb_obs is not None:
            borr_rows.append(f'<tr><td class="name"><b>{esc(name)}</b></td><td class="mono">{fmt_usd(nb) if nb is not None else esc(nb_obs.get("raw") or "—")}</td><td class="mono">{fmt_usd(obs.number(cid, "capex_ttm")[0])}</td></tr>')
    parts = [
        '<h3>가격 — ⑥ 원자료</h3><div class="tablewrap"><table><thead><tr><th class="name">기업</th><th>주가</th><th>시총</th><th>NTM PER</th><th class="text narrow">산출 방법</th><th>⑥</th><th>경계</th><th>TTM PER</th><th>영업외 비중</th><th>P/S</th></tr></thead><tbody>' + "".join(val_rows) + "</tbody></table></div>",
        '<div class="notice info">NTM PER 만 ⑥ 점수에 개입한다. TTM PER·P/S·영업외 비중은 참고·왜곡 탐지용이며 영업외 30% 이상이면 TTM PER 은 무효로 본다.</div>',
    ]
    if priv_rows:
        parts.append('<h3>비상장 — ⑥ 배수</h3><div class="tablewrap"><table><thead><tr><th class="name">기업</th><th>post-money</th><th>ARR</th><th>밸류÷ARR</th><th>누적 조달</th><th>ARR÷조달</th><th>⑥</th></tr></thead><tbody>' + "".join(priv_rows) + "</tbody></table></div><p class=\"sub\" style=\"margin-top:8px\">비상장 배수는 상장사 PER 과 직접 비교할 수 없다. 점수는 정성 예외(C-12)이며 경계 표시를 적용하지 않는다.</p>")
    parts.append('<h3>재무 — ⑨ 원자료</h3><div class="tablewrap"><table><thead><tr><th class="name">기업</th><th>현금</th><th>TTM FCF</th><th>런웨이(년)</th><th>순현금/순부채</th><th>D/EBITDA</th><th>신용</th><th class="text">부외 약정(원문)</th><th>⑨</th></tr></thead><tbody>' + "".join(fin_rows) + "</tbody></table></div><p class=\"sub\" style=\"margin-top:8px\">신용등급·CDS 는 점수 입력이 아니라 교차검증 지표다(별표 J). 부외 약정은 A(개시 리스)/B(미개시 확정)/C(우발) 분류 후 B종만 G4 커버리지에 쓴다.</p>")
    if borr_rows:
        parts.append('<h3>TTM 순차입</h3><div class="tablewrap"><table><thead><tr><th class="name">기업</th><th>TTM 순차입</th><th>TTM capex</th></tr></thead><tbody>' + "".join(borr_rows) + "</tbody></table></div>")
    return "".join(parts)


def render_method(ctx: Any, results: dict[str, Any]) -> str:
    rules = ctx.rules
    rows = "".join(f'<tr><td class="name">{esc(FACTOR_LABELS[f])}</td><td>{esc(rules.factor(f)["mode"])}</td><td class="mono">{rules.factor(f)["range"][0]}~{rules.factor(f)["range"][1]}</td><td class="text narrow">{esc(", ".join(rules.factor(f).get("decision_ids", [])) or "—")}</td></tr>' for f in FACTOR_IDS)
    pending = [d for d in rules.pending_decisions() if d.get("blocking")]
    drows = "".join(f'<tr><td class="mono">{esc(d["id"])}</td><td class="text">{esc(d["summary"])}</td><td class="text">{esc(d.get("recommendation", ""))}</td><td>{esc(next((r["choice"] for r in ctx.run["decisions"] if r["id"] == d["id"]), "미결"))}</td></tr>' for d in pending)
    return (
        f'<ul class="tight"><li>규칙 <b>{esc(rules.version)}</b> · 해시 <code>{esc(rules.hash[:16])}…</code> · 원본 {esc(rules.payload["source"]["file"])}</li>'
        f'<li>기준일 {esc(ctx.run["as_of"])} · 가격 기준일 {esc(ctx.run.get("price_as_of") or ctx.run["as_of"])} · 정보 컷오프 {esc(ctx.run.get("info_cutoff") or ctx.run["as_of"])}</li>'
        f'<li>입력 해시: observations <code>{esc(ctx.hashes["observations"][:12])}…</code> · judgments <code>{esc(ctx.hashes["judgments"][:12])}…</code> · results <code>{esc(results["results_hash"][:12])}…</code></li>'
        f'<li>실행 단위 결정: {esc(", ".join(results["decisions_applied"]) or "없음")}</li></ul>'
        f'<div class="tablewrap mt-12"><table><thead><tr><th class="name">Factor</th><th>자동화</th><th>범위</th><th class="text narrow">관련 결정</th></tr></thead><tbody>{rows}</tbody></table></div>'
        '<ul class="tight"><li>⑥ 상장: NTM PER 20·29·42·62·90 반개방 구간, 경계 ±3% 는 표시만. 비상장: 배수 자동 계산·점수는 정성 예외.</li>'
        '<li>⑨: G1 본업(TTM 영업손익) → G2 현금(TTM FCF) → G3 런웨이(현금+확정 여신 ÷ 연 소진) → G4 약정 커버리지(계약 수입 ÷ B종). 하한 -5.</li>'
        '<li>③ 사다리, ⑤ 3 + A + H, ⑦ 2×2 매트릭스는 판정 입력에서 자동 환산. ①④⑧은 정성 점수. 모르는 값은 0으로 치환하지 않는다.</li></ul>'
        + (f'<h3>미결 규칙 결정</h3><div class="tablewrap"><table><thead><tr><th>ID</th><th class="text">요약</th><th class="text">권고</th><th>이번 실행</th></tr></thead><tbody>{drows}</tbody></table></div>' if drows else "")
    )


def render_triggers(triggers: list[dict[str, Any]]) -> str:
    if not triggers:
        return '<p class="sub">등록된 트리거 없음</p>'
    rows = "".join(f'<tr><td class="mono">{esc(t["trigger_id"])}</td><td class="text"><b>{esc(t["title"])}</b></td><td class="text">{esc(t["why"])}</td><td class="text">{esc(t["impact_raw"])}</td></tr>' for t in triggers)
    return f'<div class="tablewrap"><table><thead><tr><th>ID</th><th class="text">항목</th><th class="text">왜 중요한가</th><th class="text">영향(원문)</th></tr></thead><tbody>{rows}</tbody></table></div><p class="sub mt-8">영향 열의 예상 점수는 저장값이 아니라 원문 문장이다(C-14). 사건 확인 후 현재 규칙으로 재계산한다.</p>'


def render_references(ctx: Any, review_fm: dict[str, Any]) -> str:
    items = "".join(f'<li><b>{esc(s.get("source_id"))}</b> — {esc(s.get("title"))} · {esc(s.get("publisher") or "")} · {esc(s.get("accessed_at") or "")} · {esc(s.get("url") or "URL 미제공")}' + (f' · 이해상충: {esc(s["conflict_of_interest"])}' if s.get("conflict_of_interest") else "") + "</li>" for s in ctx.sources.get("items", []))
    reviewers = review_fm.get("reviewers") or []
    rv = ", ".join(str(r) for r in reviewers) if isinstance(reviewers, list) else str(reviewers)
    return f'<ul class="tight">{items}</ul><p class="sub" style="margin-top:10px">리뷰: {esc(review_fm.get("review_type", ""))} · {esc(rv)}</p>'


# ------------------------------------------------------------------ 문서

def render_document(ctx: Any, results: dict[str, Any], baseline: dict[str, Any] | None, triggers: list[dict[str, Any]], review_fm: dict[str, Any], approval: dict[str, Any]) -> str:
    run = ctx.run
    title = run["title"]
    subtitle = f"규칙 {ctx.rules.version} · 기준일 {run['as_of']} · {results['population']['scored']}개사 순위"
    legend = "".join(f'<span><i style="background:var(--cat-{cls})"></i>{esc(label)}</span>' for cls, label in (("consumer", "주채널: 소비자"), ("work", "주채널: 업무"), ("trade", "주채널: 거래"), ("part", "부품(① 상한 2점)"), ("mix", "혼합")))
    anthropic_note = ""
    for c in results["companies"]:
        if c["company_id"] == "anthropic":
            anthropic_note = f'<div class="notice">⚠️ <b>이해상충 고지</b> — 이 채점표는 Anthropic 이 만든 Claude 가 작성했으며 Anthropic 이 평가 대상에 포함된다(과점 factor {fmt_score(c["moat"])}점). 투자 판단에 사용할 경우 감안할 것.</div>'
    document = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="{GENERATOR}">
<meta name="report-slug" content="{esc(ctx.slug)}">
<meta name="results-hash" content="{esc(results["results_hash"])}">
<meta name="approval-id" content="{esc(approval["approval_id"])}">
<meta name="rule-version" content="{esc(ctx.rules.version)}">
<title>{esc(title)}</title>
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(subtitle)}">
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.min.css">
<style>{css()}</style>
</head>
<body>
<header><div class="wrap">
  <div class="badge">{esc(ctx.rules.version)} · 기준일 {esc(run["as_of"])} · {len(run["companies"])}개사 · 승인 {esc(approval["approval_id"][:8])}</div>
  <h1>{esc(title)}</h1>
  <p class="lede">AI 시대에 <b>누가 90년 과점을 만들 구조를 갖췄나</b>를 9개 항목으로 채점했다. <b>과점 factor 5개(각 0~5점)</b>에서 더하고 <b>함정 factor 4개(각 0~-5점)</b>에서 뺀다. 점수는 규칙과 입력에서 계산된 결과이며 손으로 고치지 않는다.</p>
  {anthropic_note}
</div></header>
<div class="wrap">
<div class="kpis" id="kpis">{render_kpis(results)}</div>
<h2><span class="num">01</span>과점 × 함정 지도</h2>
<div class="chartbox">{scatter_svg(results, market_caps(ctx))}<div class="legend">{legend}<span>원 크기 = 시총(승계 관측)</span></div></div>
<h2><span class="num">02</span>종합 순위표</h2>
<p class="sub">열 제목을 누르면 정렬되고, 행을 누르면 해당 기업 카드가 열린다.<span class="m-only"> 폰에서는 합계 열만 보이고 factor 별 점수는 카드에서 본다.</span></p>
{render_ranking(results)}
{render_incomplete(results, ctx.rules)}
<h2><span class="num">03</span>기업별 상세</h2>
<p class="sub">카드를 누르면 9개 factor 의 점수·상태·산식·근거가 펼쳐진다. 근거 불릿은 기준선 {esc(run["baseline_id"])} 에서 승계한 과거 기록이다.</p>
<div class="cards" id="cards">{render_cards(results, baseline, ctx.companies, ctx.observations)}</div>
<h2><span class="num">04</span>지표 원자료</h2>
{render_raw_tables(ctx, results)}
<h2><span class="num">05</span>방법과 규칙</h2>
{render_method(ctx, results)}
<h2><span class="num">06</span>다음 재채점 트리거</h2>
{render_triggers(triggers)}
<h2><span class="num">07</span>References</h2>
{render_references(ctx, review_fm)}
<footer id="disclaimer" aria-label="투자 유의사항">
<p>{esc(DISCLAIMER)}</p>
<p>정성적 평가이므로 1~3점 차이에 통계적 의미를 두지 않는다. 순위 자체보다 같은 규칙 버전 안에서 점수의 변화 방향을 추적하는 것이 목적이다.</p>
<p>단위 — $M / $B / $T · 실행 {esc(ctx.slug)} · 승인 {esc(approval["approved_by"])} {esc(approval["approved_at"])} · 생성기 {GENERATOR}</p>
</footer>
</div>
<script>{js()}</script>
</body>
</html>
"""
    return document.replace("<th>", '<th scope="col">').replace("<th ", '<th scope="col" ')


# ------------------------------------------------------------------ 빌드

def build_scorecard(slug: str) -> tuple[Path, list[Path], None]:
    from validate_report_contract import ValidationResult, print_result

    from .validate import validate_scorecard

    precheck = validate_scorecard(slug, require_html=False, check_html_if_present=False, result=ValidationResult(slug=slug))
    if not precheck.ok:
        print_result(precheck)
        raise SystemExit("Cannot build until pre-build contract errors are fixed")
    approval_path = run_dir(slug) / "approval.json"
    if not approval_path.is_file():
        raise SystemExit(f"awaiting_user: 사용자 승인 없음 — python scripts/scorecard_cli.py approve {slug} --by <name>")
    approval = validate_approval(load_json_strict(approval_path), slug)
    if approval["hashes"] != current_hashes(slug):
        raise SystemExit("awaiting_user: 승인 이후 규칙/자료/판단/결과/초안이 바뀌어 승인이 무효 — 다시 검토·승인")
    ctx = load_context(slug)
    results = load_results(slug)
    baseline, _obs, triggers = load_baseline(ctx.run["baseline_id"])
    paths = artifact_paths(slug)
    from report_contract_lib import read_markdown

    review_fm, _b, _r, _t = read_markdown(paths.review)
    document = render_document(ctx, results, baseline, triggers, review_fm, approval)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths.html.write_text(document, encoding="utf-8")
    rows = history_rows(results, approval, ctx.rules.hash, str(ctx.run.get("change_type") or "baseline-recompute"))
    added, skipped = append_history(HISTORY_CSV, rows)
    print(f"history.csv: +{added} rows (중복 {skipped} 건너뜀)")
    postcheck = validate_scorecard(slug, require_html=True, check_html_if_present=True, result=ValidationResult(slug=slug))
    print_result(postcheck)
    if not postcheck.ok:
        raise SystemExit("Build produced artifacts that failed contract validation")
    return paths.html, [HISTORY_CSV], None
