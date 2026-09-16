# 승인된 실행 결과를 단일 파일 대시보드 HTML 로 렌더하고 history.csv 를 갱신하는 scorecard 빌더 (dashboard-design 스킬 기준 준수)
from __future__ import annotations

import html as html_lib
import json
import math
import re
from pathlib import Path
from typing import Any

from report_contract_lib import OUTPUT_DIR, artifact_paths, rel

from .engine import HISTORY_CSV, load_context, load_results, run_dir
from .inputs import ObsLookup
from .render_csv import append_history, history_rows
from . import render_common as rc
from .render_common import GATE_LABELS, METHOD_LABELS, SHARE_LABELS, YESNO_LABELS, factor_calc_text, inline_html  # noqa: F401 — 테스트·호환용 재노출
from .render_md import DISCLAIMER, FACTOR_LABELS, REVIEW_AREAS, STATUS_LABEL, fmt_num, fmt_pct, fmt_score, fmt_usd
from .schema import FACTOR_IDS, MOAT_FACTORS, TRAP_FACTORS, SchemaError, load_json_strict, sha256_file, validate_approval
from .stages import current_hashes, load_baseline

GENERATOR = "stock-report-harness scorecard-builder"
SHORT = {"F1": "①", "F2": "②", "F3": "③", "F4": "④", "F5": "⑤", "F6": "⑥", "F7": "⑦", "F8": "⑧", "F9": "⑨"}
TYPE_CLASS = {"소비자": "consumer", "업무": "work", "거래": "trade", "부품": "part", "소비자·업무": "mix", "혼합": "mix"}
OBS_STATUS_LABELS = {
    "verified": "검증 완료", "legacy_unverified": "기준선 승계·미검증", "not_applicable": "해당 없음",
    "not_disclosed": "미공시", "collection_failed": "수집 실패", "source_conflict": "출처 충돌",
    "incompatible_basis": "기준 비교 불가", "parse_failed": "파싱 실패",
    # 2026-09-16 FIX-58 1단계(7차 리뷰 D): 스키마에 있는데 라벨 사전에만 없어 원문 키가 그대로 나왔다.
    "unavailable": "산출 불가",
}
DECISION_STATUS = {"pending": "미결", "resolved": "확정", "documented": "문서화"}
CODE_RE = re.compile(r"C-\d{2}(?![\d\w/-])")
GLOSSARY_SLOT = "<!--scorecard:glossary-->"
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
  --fs-sm:12px;--fs-md:13px;--fs-base:14px;--fs-lg:16px;--fs-2xl:22px;--fs-3xl:26px;
}
*{box-sizing:border-box;margin:0;padding:0}
html{font-size:var(--fs-base)}
body{background:var(--bg);color:var(--tx);font-family:'Pretendard Variable','Pretendard',-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic',sans-serif;line-height:1.6;-webkit-font-smoothing:antialiased;padding:0 0 64px;font-variant-numeric:tabular-nums}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
h1{font-size:clamp(26px,4vw,34px);font-weight:800;letter-spacing:-.02em;line-height:1.25}
h2{font-size:clamp(18px,2.4vw,24px);font-weight:700;margin:48px 0 8px;letter-spacing:-.01em}
h2 .num{color:var(--acc);margin-right:8px}
h3{font-size:var(--fs-lg);font-weight:700;margin:24px 0 8px}
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
th,td{padding:12px 8px;text-align:center;border-bottom:1px solid var(--line);white-space:nowrap;vertical-align:middle}
th{background:var(--bg3);font-weight:700;font-size:var(--fs-sm);line-height:20px;color:var(--tx2)}
th.sort{cursor:pointer;user-select:none}
th.sort:hover{color:var(--tx)}
th[aria-sort="ascending"]::after{content:" ▲";font-size:var(--fs-sm)}
th[aria-sort="descending"]::after{content:" ▼";font-size:var(--fs-sm)}
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
.card>summary{padding:14px 16px;cursor:pointer;list-style:none;display:flex;align-items:flex-start;gap:8px 12px;min-height:44px;flex-wrap:wrap}
.card>summary::-webkit-details-marker{display:none}
.card[open]>summary{border-bottom:1px solid var(--line)}
/* 이름 쪽이 최소 190px 을 요구하게 해서, 점수 칸이 길어져도 기업명이 한두 글자 폭으로 접히지 않고
   점수 칸이 다음 줄로 내려가게 한다. min-width:0 은 자기 줄에서의 축소만 허용한다. */
.chead{flex:1 1 190px;min-width:0}
.cname{font-weight:700;font-size:var(--fs-lg);display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.pill{font-size:var(--fs-sm);font-weight:700;padding:2px 7px;border-radius:99px;background:var(--bg3);color:var(--tx2)}
.pill.consumer{background:var(--acc-soft);color:var(--cat-consumer)}
.pill.work{background:var(--good-soft);color:var(--cat-work)}
.pill.trade{background:var(--cat-trade-soft);color:var(--cat-trade)}
.pill.part{background:var(--cat-part-soft);color:var(--cat-part)}
.pill.mix{background:var(--cat-mix-soft);color:var(--cat-mix)}
.pill.warn{background:var(--warn-soft);color:var(--warn-text)}
/* 카드에서 먼저 읽혀야 하는 것은 한 줄 요약이다. 출처 표시는 그 아래 작은 캡션으로 내린다. */
.cquote{font-size:var(--fs-base);color:var(--tx2);margin-top:6px;padding-left:10px;border-left:2px solid var(--acc-line);line-height:1.55}
.cprov{font-size:var(--fs-sm);color:var(--tx3);margin-top:4px;line-height:1.4}
.cscore{text-align:right;flex:1 1 auto;min-width:0}
.cscore .t{font-size:var(--fs-3xl);font-weight:800;letter-spacing:-.03em;line-height:1}
.cscore .s{font-size:var(--fs-sm);color:var(--tx3);margin-top:3px}
.crank{font-size:var(--fs-sm);color:var(--tx3);margin-top:4px;line-height:1.45}
.cbody{padding:6px 16px 14px}
.card[open] .cbody{display:grid;grid-template-columns:1fr 1fr;gap:0 28px;align-items:start}
.cgrp{min-width:0}
.cgh{font-size:var(--fs-sm);font-weight:800;letter-spacing:.04em;padding:6px 0 2px}
.cgh.p{color:var(--g4)}.cgh.n{color:var(--g2)}
.frow{padding:10px 0;border-bottom:1px solid var(--line);font-size:var(--fs-md)}
.frow:last-child{border-bottom:none}
.fhead{display:flex;align-items:baseline;gap:8px;margin-bottom:4px;flex-wrap:wrap}
.flab{color:var(--tx2);font-weight:700;font-size:var(--fs-md);white-space:nowrap}
.fsc{font-weight:900;font-size:var(--fs-base);min-width:22px;white-space:nowrap}
/* flex:1 1 auto + min-width:0 이면 남은 폭이 20px 이어도 줄바꿈 없이 눌려서 한두 글자씩 접힌다.
   basis 를 주면 그 폭이 안 나올 때 아예 다음 줄로 내려간다. */
.fst{color:var(--tx3);font-size:var(--fs-sm);flex:1 1 160px;min-width:0;line-height:1.4}
.fcalc{color:var(--tx3);font-size:var(--fs-sm);margin:2px 0 4px;overflow-wrap:anywhere}
.fsrc{color:var(--tx3);font-size:var(--fs-sm);margin:4px 0 2px}
.figures td.mono,.figures th:not(.name):not(.text){text-align:right}
.fpts{margin:0;padding-left:16px;color:var(--tx);line-height:1.55}
.fpts li{margin:2px 0}
.fpts li.warn{color:var(--warn-text)}
.fpts li.d2{margin-left:14px;color:var(--tx2);list-style:circle}
.fpts del{color:var(--tx3)}
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
.pill.no{background:var(--bad-soft);color:var(--bad-text)}
/* C-번호는 hover 가 없는 터치에서도 눌러서 뜻을 볼 수 있어야 한다. 앵커 링크라 키보드 Tab 으로도 닿는다. */
.ccode{display:inline-block;min-height:24px;line-height:24px;padding:0 5px;border-radius:5px;background:var(--acc-soft);border:1px solid var(--acc-line);color:var(--acc-text);font-weight:700;font-variant-numeric:tabular-nums;text-decoration:none;white-space:nowrap}
.ccode:hover,.ccode:focus-visible{background:var(--acc-line);color:var(--tx);text-decoration:none}
.cdec{background:var(--bg2);border:1px solid var(--line);border-radius:10px;margin:8px 0;overflow:hidden;scroll-margin-top:16px}
.cdec:target{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc-line)}
.cdec>summary{padding:12px 14px;cursor:pointer;list-style:none;display:flex;align-items:center;gap:10px;flex-wrap:wrap;min-height:44px;font-size:var(--fs-md)}
.cdec>summary::-webkit-details-marker{display:none}
.cdec>summary::after{content:'▾';color:var(--tx3);margin-left:auto}
.cdec[open]>summary::after{content:'▴'}
.cdec>summary .id{font-weight:800;font-variant-numeric:tabular-nums;color:var(--acc-text)}
.cdec>summary .ttl{color:var(--tx2);flex:1 1 200px;min-width:0;line-height:1.45}
.cdec .inner{padding:0 14px 14px;border-top:1px solid var(--line);margin-top:-1px}
.dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;font-size:var(--fs-md);margin-top:12px}
.dl dt{color:var(--tx3);font-weight:700;white-space:nowrap}
.dl dd{color:var(--tx);min-width:0;overflow-wrap:anywhere;line-height:1.55}
@media(max-width:520px){.dl{grid-template-columns:1fr;gap:2px}.dl dd{margin-bottom:8px}}
.m-only{display:none}
@media(max-width:860px){.card[open] .cbody{grid-template-columns:1fr}}
@media(max-width:1180px){
  /* 표가 가로로 스크롤되는 폭이면 행 이름을 놓치지 않게 첫 두 열을 고정한다.
     sticky 는 border-collapse:collapse 에서 테두리를 못 끌고 오므로 separate 로 바꾼다. */
  #mainTable{border-collapse:separate;border-spacing:0}
  #mainTable th:first-child,#mainTable td:first-child{position:sticky;left:0;z-index:2;background:var(--bg2);width:48px;min-width:48px}
  #mainTable th:first-child{background:var(--bg3)}
  #mainTable th.name,#mainTable td.name{position:sticky;left:48px;z-index:2;background:var(--bg2)}
  #mainTable th.name{background:var(--bg3)}
  #mainTable tbody tr.row:hover td{background:var(--bg2)}
  /* 자료 확보 표도 가로로 스크롤되므로 기업명을 고정한다. 열은 숨기지 않는다 — 모든 항목이 그대로 남아야 한다. */
  #availTable{border-collapse:separate;border-spacing:0}
  #availTable th.name,#availTable td.name{position:sticky;left:0;z-index:2;background:var(--bg2);max-width:132px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  #availTable th.name{background:var(--bg3)}
  #availTable td.text{min-width:150px}
}
@media(max-width:640px){
  .cards{grid-template-columns:1fr}
  .kpi .v,.cscore .t{font-size:var(--fs-2xl)}
  .m-only{display:inline}
  #mainTable th:not(.keep),#mainTable td:not(.keep){display:none}
  #mainTable th.name,#mainTable td.name{max-width:132px;overflow:hidden;text-overflow:ellipsis}
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
(function(){
  // C-번호를 누르면 사전 항목으로 이동하는 데서 그치지 않고 그 자리에서 펼친다.
  // details 는 :target 만으로 열리지 않으므로 open 을 직접 세운다. hover 에는 의존하지 않는다.
  function openHash(smooth){
    const id=decodeURIComponent(location.hash.slice(1)); if(!id) return;
    const el=document.getElementById(id); if(!el||el.tagName!=='DETAILS') return;
    el.open=true; el.scrollIntoView({behavior:smooth?'smooth':'auto',block:'start'});
  }
  document.addEventListener('click',e=>{
    const a=e.target.closest('a.ccode'); if(!a) return;
    const el=document.getElementById(a.getAttribute('href').slice(1)); if(el) el.open=true;
  });
  addEventListener('hashchange',()=>openHash(true));
  openHash(false);
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
        desc = " · ".join(f'{c["display_name"]} 주채널 {c["type"]} · 과점 {c["moat"]} 함정 {c["trap"]} 조정 {c["total"]}' for c in e["group"])
        parts.append(f'<g><title>{esc(desc)}</title><circle cx="{e["x"]:.1f}" cy="{e["y"]:.1f}" r="{e["r"]:.1f}" style="fill:{e["color"]}" opacity=".18"/><circle cx="{e["x"]:.1f}" cy="{e["y"]:.1f}" r="{e["r"]:.1f}" fill="none" style="stroke:{e["color"]}" stroke-width="2" opacity=".9"/></g>')
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
    decisions = "".join(f'<li><b>{esc(d)}</b> {esc((rules.decision(d) or {}).get("summary", ""))}</li>' for d in results["pending_rule_decisions"])
    # 2026-09-16 FIX-58 1단계(7차 리뷰 D): 미완료가 0건이면 조기 반환해 **미결 규칙 결정이 HTML 에서 사라졌다.**
    # 둘은 다른 사실이다 — 미완료 기업이 없어도 미결 결정은 남을 수 있다.
    if not items:
        return (f'<h3>필요한 규칙 결정</h3><ul class="tight">{decisions}</ul>') if decisions else ""
    lis = []
    for i in items:
        reasons = "; ".join(f"{FACTOR_LABELS[p['factor']]} {STATUS_LABEL.get(p['status'], p['status'])}" + (f" ({p['decision_id']})" if p.get("decision_id") else "") for p in i["reasons"])
        lis.append(f'<li><b>{esc(i["display_name"])}</b> — {esc(reasons)}</li>')
    return (f'<div class="notice bad mt-14"><b>미완료 {len(items)}개사는 순위에서 제외했다.</b> 0점으로 채우지 않는다.</div>'
            f'<ul class="pending-list">{"".join(lis)}</ul>'
            + (f'<h3>필요한 규칙 결정</h3><ul class="tight">{decisions}</ul>' if decisions else ""))


def render_cards(results: dict[str, Any], baseline: dict[str, Any] | None, companies: dict[str, dict[str, Any]],
                 observations: list[dict[str, Any]] | None = None, judgments: list[dict[str, Any]] | None = None,
                 reps: list[dict[str, Any]] | None = None) -> str:
    """2026-09-15 FIX-54 1단계 S3: 기준선 evidence 만 읽던 카드를 초안과 같은 근거 블록(render_common.evidence_block)으로."""
    observations = observations or []
    judgments_by_id = {j["judgment_id"]: j for j in (judgments or [])}
    baseline_n = len((baseline or {}).get("companies", [])) or len(results["companies"])
    base = {b["company_id"]: b for b in (baseline or {}).get("companies", [])}
    ordered = sorted(results["companies"], key=lambda c: (c["rank"] is None, c["rank"] or 0, -(c["moat"] or 0), c["company_id"]))
    out = []
    for c in ordered:
        b = base.get(c["company_id"], {})
        cls = TYPE_CLASS.get(c["type"], "mix")
        incompatible_g4 = rc.g4_incompatible(observations, c["company_id"])
        base_rank = f" · 기준선 {results['baseline_id']} {b['rank_raw']}위({baseline_n}사)" if b.get("rank_raw") else ""
        rank_text = f"{c['rank']}위(완료 {results['population']['scored']}개사 기준){base_rank}" if c["rank"] else f"미완료{base_rank}"
        score_text = f"과점 {fmt_score(c['moat'])} / 함정 {fmt_score(c['trap'])}"
        groups = []
        for label, factors, klass, total in (("과점 — 더한다 (각 0~5)", MOAT_FACTORS, "p", c["moat"]), ("함정 — 뺀다 (각 0~-5)", TRAP_FACTORS, "n", c["trap"])):
            rows = []
            for f in factors:
                fr = c["factors"][f]
                score = fr["score"]
                color = f"c-{score_class(score) if f in MOAT_FACTORS else trap_class(score)}"
                block = rc.evidence_block(fr, judgments_by_id, b.get("evidence", {}).get(f, []), results["baseline_id"], c["company_id"], reps)
                pts = [f'<li{" class=\"d2\"" if depth > 1 else ""}>{inline_html(text)}</li>' for depth, text in (block or {}).get("lines", [])]
                if block is not None and f == "F9" and incompatible_g4:
                    pts.append(f"<li>{esc(rc.G4_INCOMPATIBLE_NOTE)}</li>")
                pts += [f'<li class="warn">⚠️ {esc(w)}</li>' for w in fr["warnings"][:4]]
                calc = factor_calc_text(f, fr)
                src = f'<div class="fsrc">{inline_html(block["header"])}</div>' if block is not None else ""
                body = (src + '<ul class="fpts">' + "".join(pts) + "</ul>") if pts else ""
                rows.append(f'<div class="frow"><div class="fhead"><span class="flab">{esc(FACTOR_LABELS[f])}</span><span class="fsc {color}">{fmt_score(score)}</span><span class="fst">{esc(STATUS_LABEL.get(fr["status"], fr["status"]))} · {esc(fr["basis"])}</span></div>{f"<div class=\"fcalc\">{esc(calc)}</div>" if calc else ""}{body}</div>')
            groups.append(f'<div class="cgrp"><div class="cgh {klass}">{esc(label)} · 합 {fmt_score(total)}</div>{"".join(rows)}</div>')
        out.append(
            f'<details class="card" id="card-{esc(c["company_id"])}" data-company="{esc(c["company_id"])}"><summary><div class="chead"><div class="cname">{esc(c["display_name"])}<span class="pill {cls}">{esc(c["type"])}</span>'
            + ("" if c["complete"] else '<span class="pill warn">미완료</span>')
            + "</div>"
            + (f'<div class="cquote">{esc(b["tag"])}</div>' if b.get("tag") else "")
            + f'<div class="crank">{esc(rank_text)}</div>'
            + (f'<div class="cprov">요약은 기준선 {esc(results["baseline_id"])} 원문 · 미재검증</div>' if b.get("tag") else "")
            + f'</div><div class="cscore"><div class="t c-{total_class(c["total"])}">{fmt_score(c["total"])}</div><div class="s">{esc(score_text)}</div></div></summary>'
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


def render_raw_tables(ctx: Any, results: dict[str, Any]) -> str:
    """2026-09-15 FIX-54 1단계 S3: 초안 `_raw_tables` 와 같은 캡션·경계·부외 칸·관측 상태·현금 정의를 render_common 에서 읽는다."""
    obs = ObsLookup(ctx.observations)
    val_rows, priv_rows, fin_rows, borr_rows = [], [], [], []
    for c in results["companies"]:
        cid, name = c["company_id"], c["display_name"]
        if c["listed"]:
            per, per_obs = obs.number(cid, "ntm_per")
            method = ((per_obs or {}).get("basis") or {}).get("method", "—")
            f6 = c["factors"]["F6"]
            flag = "⚠️" if rc.f6_boundary_flag(f6.get("calc") or {}) else "—"
            nonop = obs.number(cid, "nonop_share")[0]
            val_rows.append(f'<tr><td class="name"><b>{esc(name)}</b></td><td class="mono">{fmt_usd(obs.number(cid, "price")[0], 2)}</td><td class="mono">{fmt_usd(obs.number(cid, "market_cap")[0])}{rc.vendor_mark(obs, cid, "market_cap")}</td><td class="mono w8">{fmt_num(per)}{rc.vendor_mark(obs, cid, "ntm_per")}</td><td class="text narrow">{esc(METHOD_LABELS.get(method, method))}</td><td class="mono w8">{fmt_score(f6["score"])}</td><td>{flag}</td><td class="mono">{fmt_num(obs.number(cid, "ttm_per")[0])}</td><td class="mono{" c-g1" if (nonop or 0) >= 0.3 else ""}">{fmt_pct(nonop)}</td><td class="mono">{fmt_num(obs.number(cid, "ps_ratio")[0])}</td></tr>')
        else:
            v_arr, arr_raised = rc.private_multiples(c["factors"]["F6"].get("calc") or {})
            priv_rows.append(f'<tr><td class="name"><i>{esc(name)}</i></td><td class="mono">{fmt_usd(obs.number(cid, "post_money_valuation")[0])}</td><td class="mono">{fmt_usd(obs.number(cid, "arr")[0])}</td><td class="mono">{fmt_num(v_arr)}x</td><td class="mono">{fmt_usd(obs.number(cid, "cumulative_raised")[0])}</td><td class="mono">{fmt_num(arr_raised, 2)}</td><td class="mono w8">{fmt_score(c["factors"]["F6"]["score"])}</td></tr>')
        fcf, fcf_obs = obs.number(cid, "fcf_ttm")
        fcf_text = fmt_usd(fcf) if fcf is not None else esc((fcf_obs or {}).get("raw") or "—")
        fcf_cls = "c-g1" if (fcf or 0) < 0 else ("c-g5" if fcf else "c-g0")
        rating = (obs.get(cid, "credit_rating") or {}).get("value") or "—"
        fin_rows.append(f'<tr{"" if c["listed"] else " class=\"priv\""}><td class="name"><b>{esc(name)}</b></td><td class="mono">{fmt_usd(obs.number(cid, "cash")[0])}</td><td class="mono w8 {fcf_cls}">{fcf_text}</td><td class="mono">{runway_text(c, obs)}</td><td class="mono">{fmt_usd(obs.number(cid, "net_cash")[0])}{rc.vendor_mark(obs, cid, "net_cash")}</td><td class="mono">{fmt_num(obs.number(cid, "debt_ebitda")[0], 2)}</td><td>{esc(rating)}</td><td class="text">{inline_html(rc.offbalance_cell(obs, cid))}</td><td class="mono w8">{fmt_score(c["factors"]["F9"]["score"])}</td></tr>')
        nb, nb_obs = obs.number(cid, "net_borrowing_ttm")
        if nb_obs is not None:
            borr_rows.append(f'<tr><td class="name"><b>{esc(name)}</b></td><td class="mono">{fmt_usd(nb) if nb is not None else esc(nb_obs.get("raw") or "—")}</td><td class="mono">{fmt_usd(obs.number(cid, "capex_ttm")[0])}</td></tr>')
    cids = [c["company_id"] for c in results["companies"]]
    listed = [c["company_id"] for c in results["companies"] if c["listed"]]
    vendor = rc.vendor_policy_note(ctx)
    parts = [
        f'<p class="sub mt-8">{inline_html(rc.raw_caption(ctx))}</p>',
        '<h3>가격 — ⑥ 원자료</h3><div class="tablewrap"><table class="figures"><thead><tr><th class="name">기업</th><th>주가</th><th>시총</th><th>NTM PER</th><th class="text narrow">산출 방법</th><th>⑥</th><th>경계</th><th>TTM PER</th><th>영업외 비중</th><th>P/S</th></tr></thead><tbody>' + "".join(val_rows) + "</tbody></table></div>",
        f'<p class="sub mt-8">열별 관측 상태: {esc(rc.status_summary(obs, listed, rc.PRICE_STATUS_COLUMNS))}</p>',
        f'<div class="notice info">{inline_html(rc.price_notice(ctx))}</div>',
        f'<div class="notice">{inline_html(vendor)}</div>' if vendor else "",
    ]
    if priv_rows:
        parts.append('<h3>비상장 — ⑥ 배수</h3><div class="tablewrap"><table class="figures"><thead><tr><th class="name">기업</th><th>post-money</th><th>ARR</th><th>밸류÷ARR</th><th>누적 조달</th><th>ARR÷조달</th><th>⑥</th></tr></thead><tbody>' + "".join(priv_rows) + f'</tbody></table></div><p class="sub mt-8">{inline_html(rc.private_notice(ctx))}</p>')
    parts.append(f'<h3>재무 — ⑨ 원자료</h3><div class="tablewrap"><table class="figures"><thead><tr><th class="name">기업</th><th>현금</th><th>TTM FCF</th><th>런웨이(년)</th><th>순현금/순부채</th><th>D/EBITDA</th><th>신용</th><th class="text">{esc(rc.OFFBALANCE_HEADER)}</th><th>⑨</th></tr></thead><tbody>' + "".join(fin_rows) + "</tbody></table></div>"
                 f'<p class="sub mt-8">열별 관측 상태: {esc(rc.status_summary(obs, cids, rc.FIN_STATUS_COLUMNS))}</p>'
                 f'<div class="notice info">{inline_html(rc.cash_definition_note(ctx))}</div>'
                 + "".join(f'<p class="sub mt-8">{inline_html(x)}</p>' for x in rc.credit_lines(ctx, results)) +
                 f'<p class="sub mt-8">{esc(rc.CREDIT_NOTE)} 부외 약정은 A(개시 리스)/B(미개시 확정)/C(우발) 분류 후 B종만 G4 커버리지에 쓴다.</p>')
    if borr_rows:
        parts.append('<h3>TTM 순차입</h3><div class="tablewrap"><table class="figures"><thead><tr><th class="name">기업</th><th>TTM 순차입</th><th>TTM capex</th></tr></thead><tbody>' + "".join(borr_rows) + "</tbody></table></div>")
    return "".join(parts)


def render_method(ctx: Any, results: dict[str, Any]) -> str:
    rules = ctx.rules
    rows = "".join(f'<tr><td class="name">{esc(FACTOR_LABELS[f])}</td><td>{esc(rules.factor(f)["mode"])}</td><td class="mono">{rules.factor(f)["range"][0]}~{rules.factor(f)["range"][1]}</td><td class="text narrow">{esc(", ".join(rules.factor(f).get("decision_ids", [])) or "—")}</td></tr>' for f in FACTOR_IDS)
    pending = [d for d in rules.pending_decisions() if d.get("blocking")]
    drows = "".join(f'<tr><td class="mono">{esc(d["id"])}</td><td class="text">{esc(d["summary"])}</td><td class="text">{esc(d.get("recommendation", ""))}</td><td>{esc(next((r["choice"] for r in ctx.run["decisions"] if r["id"] == d["id"]), "미결"))}</td></tr>' for d in pending)
    return (
        f'<ul class="tight"><li>규칙 <b>{esc(rules.version)}</b> · 해시 <code>{esc(rules.hash[:16])}…</code> · 원본 {esc(rules.payload["source"]["file"])}</li>'
        f'<li>기준일 {esc(ctx.run["as_of"])} · 가격 기준일 {esc(ctx.run.get("price_as_of") or ctx.run["as_of"])} · 정보 컷오프 {esc(ctx.run.get("info_cutoff") or ctx.run["as_of"])} — 승계 근거와 트리거에는 컷오프 이후 사건이 원문 그대로 남아 있으며 이번 실행에서 재검증하지 않았다(C-17)</li>'
        f'<li>입력 해시: observations <code>{esc(ctx.hashes["observations"][:12])}…</code> · judgments <code>{esc(ctx.hashes["judgments"][:12])}…</code> · results <code>{esc(results["results_hash"][:12])}…</code></li>'
        f'<li>실행 단위 결정: {esc(", ".join(results["decisions_applied"]) or "없음")}</li></ul>'
        f'<div class="tablewrap mt-12"><table><thead><tr><th class="name">Factor</th><th>자동화</th><th>범위</th><th class="text narrow">관련 결정</th></tr></thead><tbody>{rows}</tbody></table></div>'
        # 2026-09-15 FIX-54 1단계 S3: v1.5 문구(NTM PER 구간 · 하한 -5)가 박혀 있었다. 초안과 같은 목록을 쓴다.
        '<ul class="tight">' + "".join(f"<li>{inline_html(x)}</li>" for x in [rc.c04_line(ctx)] + rc.method_lines(ctx)) + '</ul>'
        '<h3>알려진 한계</h3>' + render_limitations(ctx)
        + (f'<h3>미결 규칙 결정</h3><div class="tablewrap"><table><thead><tr><th>ID</th><th class="text">요약</th><th class="text">권고</th><th>이번 실행</th></tr></thead><tbody>{drows}</tbody></table></div>' if drows else "")
    )


def render_limitations(ctx: Any) -> str:
    """2026-09-15 FIX-54 1단계 S4: 초안 `## 알려진 한계` 와 같은 목록. 들여쓴 줄은 바로 앞 항목의 하위 목록이다."""
    groups: list[tuple[str, list[str]]] = []
    for x in rc.limitations(ctx):
        if x.startswith("  - ") and groups:
            groups[-1][1].append(x[4:])
        else:
            groups.append((x, []))
    lis = "".join(f"<li>{inline_html(t)}" + (f'<ul class="tight">{"".join(f"<li>{inline_html(q)}</li>" for q in subs)}</ul>' if subs else "") + "</li>"
                  for t, subs in groups)
    return f'<ul class="tight">{lis}</ul>'


def load_availability(slug: str) -> dict[str, Any] | None:
    """실행 디렉터리의 자료 확보 현황 기록을 읽는다. 채점 입력이 아니라 표시용이라 승인 해시 대상이 아니다."""
    path = run_dir(slug) / "data_availability.json"
    return load_json_strict(path) if path.is_file() else None


def render_availability(avail: dict[str, Any], ctx: Any, results: dict[str, Any]) -> str:
    obs = ObsLookup(ctx.observations)
    surveyed_at = avail["surveyed_at"]
    surveys = avail.get("surveys", {})
    by_id = {c["company_id"]: c for c in results["companies"]}
    rows = []
    reflected_n = 0
    for entry in avail["companies"]:
        cid = entry["company_id"]
        c = by_id.get(cid)
        if c is None:
            continue
        o = obs.get(cid, "ntm_per") or {}
        # 이번 조사보다 이전 기준일의 관측이면 조사 결과가 점수에 들어가지 않았다는 뜻이다.
        reflected = bool(o.get("as_of")) and str(o["as_of"]) >= surveyed_at
        reflected_n += 1 if reflected else 0
        used = f'{fmt_num(o.get("value"))} · {esc(o.get("as_of") or "—")} · {esc(o.get("source_id") or "—")}' if o else "관측 없음"
        state = f'{esc(OBS_STATUS_LABELS.get(o.get("status"), o.get("status") or "—"))} · {esc(METHOD_LABELS.get((o.get("basis") or {}).get("method"), (o.get("basis") or {}).get("method") or "—"))}' if o else "—"
        quarters = " · ".join(esc(q) for q in entry["quarter_ends"])
        level = f'{entry["secured_quarters"]}/{avail["required_quarters"]}분기'
        badge = '<span class="pill no">미반영</span>' if not reflected else '<span class="pill">반영</span>'
        rows.append(
            f'<tr><td class="name"><b>{esc(c["display_name"])}</b></td><td class="mono">{quarters}</td>'
            f'<td class="mono w8 c-g2">{esc(level)}</td><td class="text narrow">{esc(entry["missing"])}</td>'
            f'<td class="text narrow">{esc(surveys.get(entry["survey"], entry["survey"]))}</td>'
            f'<td class="text narrow">{used}</td><td class="text narrow">{state}</td><td>{badge}</td></tr>'
        )
    outside = [c for c in results["companies"] if c["company_id"] not in {e["company_id"] for e in avail["companies"]}]
    for c in outside:
        rows.append(
            f'<tr class="priv"><td class="name"><i>{esc(c["display_name"])}</i></td><td class="mono">—</td><td class="mono">—</td>'
            f'<td class="text narrow">이번 조사 범위 밖</td><td class="text narrow">{"비상장 — ⑥ 은 정성 예외(C-12)" if not c["listed"] else "조사 대상 아님"}</td>'
            f'<td class="text narrow">—</td><td class="text narrow">—</td><td><span class="pill">해당 없음</span></td></tr>'
        )
    mat = "".join(
        f'<tr><td class="name"><b>{esc(m["item"])}</b></td><td class="text">{esc(m["secured"])}</td>'
        f'<td class="text">{esc(m["missing"])}</td><td class="text">{esc(m["usable"])}</td></tr>' for m in avail["materials"]
    )
    src = "".join(
        f'<tr><td class="name"><b>{esc(s["name"])}</b></td><td class="text">{esc(s["secured"])}</td><td class="text">{esc(s["limit"])}</td></tr>'
        for s in avail["sources"]
    )
    cautions = "".join(f"<li>{esc(x)}</li>" for x in avail.get("cautions", []))
    refs = "".join(f'<li>{esc(r["label"])} — <code>{esc(r["path"])}</code></li>' for r in avail.get("references", []))
    return "".join([
        f'<div class="notice bad"><b>이 조사는 점수를 바꾸지 않았다.</b> {esc(avail["headline"])} {esc(avail["score_effect"])}</div>',
        f'<div class="notice">{esc(avail["not_re_surveyed"])}</div>',
        f'<p class="sub mt-8">조사일 {esc(surveyed_at)} · 조사 범위 {esc(avail["scope"])} · 4분기 충족 {avail["companies_with_full_quarters"]}개사 · '
        f'조사 결과가 점수 입력에 반영된 기업 {reflected_n}개사. {esc(avail["collection_note"])}</p>',
        '<h3>기업별 확보 현황</h3>',
        '<div class="tablewrap"><table class="figures" id="availTable"><thead><tr><th class="name">기업</th><th>확보 분기(종료월)</th><th>확보 수준</th>'
        '<th class="text narrow">부족 자료</th><th class="text narrow">조사 원천</th><th class="text narrow">채점에 쓰인 NTM PER 관측</th>'
        f'<th class="text narrow">관측 상태·산출 방법</th><th>이번 조사 반영</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>',
        '<p class="sub mt-8">「채점에 쓰인 NTM PER 관측」은 값 · 관측 기준일 · 원천이다. 이 열의 기준일이 조사일보다 앞서면 점수는 기준선 관측으로 계산된 것이며 이번 조사와 무관하다.</p>',
        f'<details class="blk"><summary>자료 종류별 확보·부족<span></span></summary><div class="inner"><div class="tablewrap"><table class="figures"><thead><tr>'
        f'<th class="name">자료</th><th class="text">확보한 것</th><th class="text">부족하거나 미검증인 것</th><th class="text">현재 사용 가능 범위</th></tr></thead><tbody>{mat}</tbody></table></div></div></details>',
        f'<details class="blk"><summary>원천별 확보 범위와 한계<span></span></summary><div class="inner"><div class="tablewrap"><table class="figures"><thead><tr>'
        f'<th class="name">원천·접근 방식</th><th class="text">확보 또는 관측</th><th class="text">한계</th></tr></thead><tbody>{src}</tbody></table></div>'
        + (f'<h3>해석 주의</h3><ul class="tight">{cautions}</ul>' if cautions else "")
        + (f'<h3>근거 파일</h3><ul class="tight">{refs}</ul>' if refs else "")
        + '</div></details>',
    ])


def render_glossary(ctx: Any, results: dict[str, Any], used_ids: list[str]) -> str:
    """화면에 노출된 C-번호마다 제목·의미·현재 결정·점수 영향을 펼쳐 보게 한다 (hover 의존 없음)."""
    blocks = []
    for did in used_ids:
        d = ctx.rules.decision(did)
        if d is None:
            continue
        choice = next((r["choice"] for r in ctx.run.get("decisions", []) if r["id"] == did), None)
        status = DECISION_STATUS.get(d["status"], d["status"])
        hits = [(c["display_name"], p["factor"], p["status"]) for c in results["companies"] for p in c["pending"] if p.get("decision_id") == did]
        if choice:
            state = f"이번 실행에서 <b>{esc(choice)}</b> 로 결정해 적용했다."
        elif did in results["pending_rule_decisions"]:
            state = "이번 실행에서 <b>결정하지 않았다</b>. 해당 factor 는 점수를 만들지 않고 대기 상태로 남는다."
        elif d["status"] == "pending":
            state = "규칙 파일에서 미결이지만 이번 실행의 채점 경로에는 걸리지 않았다."
        else:
            state = "규칙 파일에 이미 반영된 항목이라 실행 단위 선택이 필요하지 않다."
        if hits:
            impact = " · ".join(f"{esc(n)} {esc(FACTOR_LABELS[f])} {esc(STATUS_LABEL.get(s, s))}" for n, f, s in hits)
            impact = f"{impact} — 이 기업들은 순위에서 제외되며 0 점으로 채우지 않는다."
        elif choice:
            impact = "적용한 선택이 채점 경로에 반영되었다."
        else:
            impact = "이번 실행의 점수에는 영향을 주지 않았다."
        rows = [("무엇에 대한 결정인가", esc(d["summary"])), ("권고", esc(d.get("recommendation") or "—")),
                ("선택지", ", ".join(esc(x) for x in d.get("choices", [])) or "규칙 파일에 선택지 정의 없음"),
                ("영향 factor", ", ".join(esc(FACTOR_LABELS.get(f, f)) for f in d.get("affects", [])) or "—"),
                ("이번 실행 상태", state), ("점수 영향", impact)]
        dl = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows)
        head = esc(d["summary"][:60] + ("…" if len(d["summary"]) > 60 else ""))
        blocks.append(
            f'<details class="cdec" id="dec-{esc(did)}"><summary><span class="id">{esc(did)}</span>'
            f'<span class="pill{" warn" if d["status"] == "pending" else ""}">{esc(status)}</span>'
            f'<span class="ttl">{head}</span></summary><div class="inner"><dl class="dl">{dl}</dl></div></details>'
        )
    if not blocks:
        return ""
    return ('<h3 id="c-glossary">C-번호 사전</h3>'
            '<p class="sub">본문의 C-번호를 누르면 이 목록의 해당 항목으로 이동한다. 항목을 누르면 뜻과 현재 상태가 펼쳐진다.</p>'
            + "".join(blocks))


def link_decision_codes(document: str, known: set[str], placeholder: str) -> str:
    """본문 텍스트의 C-번호를 사전 항목 앵커로 바꾼다. 태그 속성·style·script 는 건드리지 않는다."""
    def sub_text(m: re.Match[str]) -> str:
        text = m.group(1)
        if "C-" not in text:
            return m.group(0)
        return ">" + CODE_RE.sub(lambda c: f'<a class="ccode" href="#dec-{c.group(0)}">{c.group(0)}</a>' if c.group(0) in known else c.group(0), text) + "<"

    parts = re.split(r"(<style>.*?</style>|<script>.*?</script>)", document, flags=re.S)
    for i in range(0, len(parts), 2):
        if placeholder in parts[i]:
            before, _, after = parts[i].partition(placeholder)
            parts[i] = re.sub(r">([^<>]*)<", sub_text, before) + placeholder + re.sub(r">([^<>]*)<", sub_text, after)
        else:
            parts[i] = re.sub(r">([^<>]*)<", sub_text, parts[i])
    return "".join(parts)


def render_triggers(ctx: Any, triggers: list[dict[str, Any]]) -> str:
    """2026-09-15 FIX-54 1단계 S3: 초안과 같은 `왜 중요한가` 칸(대체 수치 ⚠️ · source_text_corrections)과 각주."""
    if not triggers:
        return '<p class="sub">등록된 트리거 없음</p>'
    reps = rc.replacements(ctx)
    rows = "".join(f'<tr><td class="mono">{esc(t["trigger_id"])}</td><td class="text"><b>{esc(t["title"])}</b></td><td class="text">{inline_html(rc.trigger_why(ctx, t, reps))}</td><td class="text">{esc(t["impact_raw"])}</td></tr>' for t in triggers)
    return ('<div class="notice"><span class="pill legacy">기준선 원문 · 과거 기록</span> 이 표는 기준선에서 그대로 옮긴 문장이며 이번 실행에서 재검증하지 않았다. '
            '따라서 표 안의 비교 문장과 경계 언급은 위 04 지표 원자료의 이번 실행 산출과 다를 수 있다.</div>'
            f'<div class="tablewrap"><table><thead><tr><th>ID</th><th class="text">항목</th><th class="text">왜 중요한가(v1.5 원문)</th><th class="text">영향(원문)</th></tr></thead><tbody>{rows}</tbody></table></div>'
            + "".join(f'<p class="sub mt-8">{inline_html(x)}</p>' for x in rc.trigger_notes(ctx)))


def render_references(ctx: Any, review_fm: dict[str, Any]) -> str:
    items = "".join(f'<li><b>{esc(s.get("source_id"))}</b> — {esc(s.get("title"))} · {esc(s.get("publisher") or "")} · {esc(s.get("accessed_at") or "")} · {esc(s.get("url") or "URL 미제공")}' + (f' · 이해상충: {esc(s["conflict_of_interest"])}' if s.get("conflict_of_interest") else "") + "</li>" for s in ctx.sources.get("items", []))
    reviewers = review_fm.get("reviewers") or []
    rv = ", ".join(str(r) for r in reviewers) if isinstance(reviewers, list) else str(reviewers)
    return f'<ul class="tight">{items}</ul><p class="sub" style="margin-top:10px">리뷰: {esc(review_fm.get("review_type", ""))} · {esc(rv)}</p>'


# ------------------------------------------------------------------ 문서

def render_document(ctx: Any, results: dict[str, Any], baseline: dict[str, Any] | None, triggers: list[dict[str, Any]], review_fm: dict[str, Any], approval: dict[str, Any], avail: dict[str, Any] | None = None) -> str:
    run = ctx.run
    title = run["title"]
    subtitle = f"규칙 {ctx.rules.version} · 기준일 {run['as_of']} · {results['population']['scored']}개사 순위"
    present: list[str] = []
    for c in results["companies"]:
        if c["complete"] and not c["reference"] and c["type"] not in present:
            present.append(c["type"])
    legend = "".join(f'<span><i style="background:var(--cat-{TYPE_CLASS.get(t, "mix")})"></i>{esc(t)}{" (① 상한 2점)" if t == "부품" else ""}</span>' for t in present)
    anthropic_note = ""
    for c in results["companies"]:
        if c["company_id"] == "anthropic":
            anthropic_note = f'<div class="notice">⚠️ <b>이해상충 고지</b> — 이 채점표는 Anthropic 이 만든 Claude 가 작성했으며 Anthropic 이 평가 대상에 포함된다(과점 factor {fmt_score(c["moat"])}점). 투자 판단에 사용할 경우 감안할 것.</div>'
    survey_note = ""
    if avail:
        survey_note = (
            f'<div class="notice info"><b>점수의 출처를 먼저 밝힌다.</b> 이 표의 점수는 기준선 {esc(run["baseline_id"])} 입력을 규칙 '
            f'{esc(ctx.rules.version)} 로 다시 계산한 결과다. {esc(avail["surveyed_at"])} NTM 자료 조사는 미발표 4개 분기 컨센서스를 채우지 못해'
            f'(대상 {len(avail["companies"])}개사 모두 {avail["required_quarters"]}분기 미충족) 점수 입력으로 들어가지 않았다. '
            f'무엇을 확보했고 무엇이 없는지는 <a href="#availability">05 자료 확보 현황</a>에 있다.</div>'
        )
    availability = (f'<h2 id="availability"><span class="num">05</span>자료 확보 현황</h2>{render_availability(avail, ctx, results)}') if avail else ""
    n = 5 if avail else 4
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
  <div class="badge">{esc(ctx.rules.version)} · 기준일 {esc(run["as_of"])} · 채점 {len(run["companies"])}개사 · 순위 {results["population"]["scored"]}개사 · 승인 {esc(approval["approval_id"][:8])}</div>
  <h1>{esc(title)}</h1>
  <p class="lede">AI 시대에 <b>누가 90년 과점을 만들 구조를 갖췄나</b>를 9개 항목으로 채점했다. <b>과점 factor 5개(각 0~5점)</b>에서 더하고 <b>함정 factor 4개(각 0~-5점)</b>에서 뺀다. 점수는 규칙과 입력에서 계산된 결과이며 손으로 고치지 않는다.</p>
  {survey_note}
  {anthropic_note}
</div></header>
<div class="wrap">
<div class="kpis" id="kpis">{render_kpis(results)}</div>
<h2><span class="num">01</span>과점 × 함정 지도</h2>
<div class="chartbox">{scatter_svg(results, market_caps(ctx))}<div class="legend">{legend}<span>원 크기 = 시총(비상장은 최근 post-money)</span></div><p class="sub mt-8">완료 {results["population"]["scored"]}개사만 표시한다. 미완료 {len(results["population"]["incomplete"])}개사는 함정 합계가 확정되지 않아 좌표가 없다.</p></div>
<h2><span class="num">02</span>종합 순위표</h2>
<p class="sub">열 제목을 누르면 정렬되고, 행을 누르면 해당 기업 카드가 열린다.<span class="m-only"> 폰에서는 합계 열만 보이고 factor 별 점수는 카드에서 본다.</span></p>
{render_ranking(results)}
{render_incomplete(results, ctx.rules)}
<h2><span class="num">03</span>기업별 상세</h2>
<p class="sub">카드를 누르면 9개 factor 의 점수·상태·산식·근거가 펼쳐진다. {inline_html(rc.card_evidence_note(run["baseline_id"]))}</p>
<div class="cards" id="cards">{render_cards(results, baseline, ctx.companies, ctx.observations, ctx.judgments, rc.replacements(ctx))}</div>
<h2><span class="num">04</span>지표 원자료</h2>
{render_raw_tables(ctx, results)}
{availability}
<h2><span class="num">0{n + 1}</span>방법과 규칙</h2>
{render_method(ctx, results)}
{GLOSSARY_SLOT}
<h2><span class="num">0{n + 2}</span>다음 재채점 트리거</h2>
{render_triggers(ctx, triggers)}
<h2><span class="num">0{n + 3}</span>References</h2>
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
    document = re.sub(r"<th(?=[ >])", '<th scope="col"', document)
    used = sorted({m.group(0) for m in CODE_RE.finditer(document) if ctx.rules.decision(m.group(0)) is not None})
    document = link_decision_codes(document, set(used), GLOSSARY_SLOT)
    return document.replace(GLOSSARY_SLOT, render_glossary(ctx, results, used))


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
    document = render_document(ctx, results, baseline, triggers, review_fm, approval, load_availability(slug))
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
