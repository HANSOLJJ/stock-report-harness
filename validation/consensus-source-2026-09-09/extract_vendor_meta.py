# NTM-SOURCE-05: 저장된 StockAnalysis __data.json 에서 공급사 표기·통화·CIK·ADR 제수·갱신시각을 추출한다.
# 기존 a74c15e 스냅샷을 읽기만 하고 수정하지 않는다.
import io
import json
import os
import re

import devalue

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

CIDS = ["meta", "nvidia", "alphabet", "microsoft", "amazon", "apple",
        "oracle", "palantir", "tesla", "spacex-xai"]

out = {}
for cid in CIDS:
    fn = os.path.join(RAW, "sa-%s-forecast-data.json" % cid)
    if not os.path.exists(fn):
        out[cid] = {"error": "snapshot 없음"}
        continue
    text = io.open(fn, encoding="utf-8").read()
    rec = {"snapshot_file": "raw/sa-%s-forecast-data.json" % cid}

    # 노드별로 복원해 필요한 필드를 찾는다.
    for i in range(6):
        try:
            d = devalue.node_data(text, i)
        except Exception:
            continue
        if not isinstance(d, dict):
            continue
        info = d.get("info") if isinstance(d.get("info"), dict) else None
        if info:
            rec["cik"] = info.get("cik")
            rec["exchange"] = info.get("exchange")
            rec["name_full"] = info.get("nameFull")
            rec["currency_declared"] = info.get("curr")
            rec["ipo_date"] = info.get("ipoDate")
        if "estimates" in d:
            rec["estimates_source_code"] = d.get("estimatesSource")
            tr = d.get("trust") or {}
            srcs = tr.get("sources") if isinstance(tr, dict) else None
            if srcs:
                rec["declared_data_sources"] = [
                    {"name": s.get("name"), "url": s.get("url")} for s in srcs if isinstance(s, dict)]
            rec["trust_freshness"] = (tr.get("freshnessLabel") or tr.get("freshness")
                                      if isinstance(tr, dict) else None)
            meta = d.get("meta") or {}
            if isinstance(meta, dict):
                rec["exchange_rate"] = meta.get("exchangeRate")
                rec["adr_price_divisor"] = meta.get("adrPriceDivisor")
            pt = d.get("priceTargets") or {}
            if isinstance(pt, dict):
                rec["price_target_source"] = pt.get("source")
                rec["price_target_currency"] = pt.get("currency")

    # 원문 텍스트에서 갱신 표기를 직접 찾는다(복원 대상 밖에 있을 수 있음).
    m = re.search(r'estimatesSource"?\s*:\s*"([a-z]+)"', text)
    if m:
        rec.setdefault("estimates_source_code", m.group(1))
    for pat, key in ((r'"S&P Global Market Intelligence"', "spg_named"),
                     (r'"TipRanks"', "tipranks_named"),
                     (r'adrPriceDivisor', "adr_divisor_field_present")):
        rec[key] = bool(re.search(pat, text))
    ups = sorted(set(re.findall(r'updated:"(\d{4}-\d{2}-\d{2})"', text)))
    rec["updated_labels_in_snapshot"] = ups
    out[cid] = rec

io.open(os.path.join(HERE, "vendor-meta-05.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

for cid, r in out.items():
    print("%-11s cik=%-11s curr=%s src=%s adrDiv=%s updated=%s" % (
        cid, r.get("cik"), (r.get("currency_declared") or {}).get("financial")
        if isinstance(r.get("currency_declared"), dict) else r.get("currency_declared"),
        r.get("estimates_source_code"), r.get("adr_price_divisor"),
        r.get("updated_labels_in_snapshot")))
print("\ndeclared_data_sources (nvidia):", out.get("nvidia", {}).get("declared_data_sources"))
