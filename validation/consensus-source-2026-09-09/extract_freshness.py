# NTM-SOURCE-05: a74c15e 스냅샷의 StockAnalysis trust 블록에서 추정 갱신시각을 정확히 복원한다.
import datetime as dt
import io
import json
import os

import devalue

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
CIDS = ["meta", "nvidia", "alphabet", "microsoft", "amazon", "apple",
        "oracle", "palantir", "tesla", "spacex-xai"]


def ms(v):
    if not isinstance(v, (int, float)):
        return None
    return dt.datetime.fromtimestamp(v / 1000.0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


out = {}
for cid in CIDS:
    fn = os.path.join(RAW, "sa-%s-forecast-data.json" % cid)
    t = io.open(fn, encoding="utf-8").read()
    rec = {"snapshot_file": "raw/sa-%s-forecast-data.json" % cid}
    for i in range(6):
        try:
            d = devalue.node_data(t, i)
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("trust"), dict):
            tr = d["trust"]
            rec["freshness_lag"] = tr.get("freshnessLag")
            rec["last_updated_epoch_ms"] = tr.get("lastUpdated")
            rec["last_checked_epoch_ms"] = tr.get("lastChecked")
            rec["last_updated_utc"] = ms(tr.get("lastUpdated"))
            rec["last_checked_utc"] = ms(tr.get("lastChecked"))
            rec["topic"] = tr.get("topic")
            srcs = tr.get("sources") or []
            rec["declared_sources"] = [s.get("name") for s in srcs if isinstance(s, dict)]
            summ = tr.get("summary")
            if isinstance(summ, dict):
                rec["summary_text"] = summ.get("text")
            break
    out[cid] = rec
    print("%-11s lag=%-6s lastUpdated=%s lastChecked=%s src=%s" % (
        cid, rec.get("freshness_lag"), rec.get("last_updated_utc"),
        rec.get("last_checked_utc"), rec.get("declared_sources")))

io.open(os.path.join(HERE, "freshness-05.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsummary_text (nvidia):", out["nvidia"].get("summary_text"))
