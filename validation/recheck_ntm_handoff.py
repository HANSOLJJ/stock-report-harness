# scarpper 인수본의 판정 일치와 과거·현재 참조 해시를 읽기 전용으로 재검증한다.
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCARPPER = ROOT.parent / "scarpper"
DATA = SCARPPER / "validation/qwen-ntm-data-03"
WORKER = ROOT.parent / "worker"


def run(args, cwd=SCARPPER):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def main():
    evidence = json.loads((DATA / "evidence.json").read_text(encoding="utf-8"))
    corrected = json.loads((DATA / "fy-analysis-corrected.json").read_text(encoding="utf-8"))
    expected = {"meta", "nvidia", "alphabet", "microsoft", "amazon", "apple",
                "oracle", "palantir", "tesla", "spacex-xai"}
    assert {r["company_id"] for r in evidence["companies"]} == expected
    assert set(corrected["companies"]) == expected
    count_discrepancies = []
    for row in evidence["companies"]:
        verdict = row["period_verdict"]
        assert verdict["forward_pe_period"] == "period_unknown"
        assert verdict["ntm_eligibility"] == "unverified"
        assert verdict["is_ntm_proven"] is False
        assert verdict["is_not_ntm_proven"] is False
        assert row["satisfied"] is False
        cid = row["company_id"]
        observed = row["forecast_period"]["yahoo_forward_quarters_free"]
        reported = corrected["companies"][cid]["quarterly_eps_obtained"]
        if observed != reported:
            count_discrepancies.append({"company": cid, "yahoo_observed": observed,
                                        "corrected_obtained": reported})
    analysis = run([sys.executable, "-X", "utf8", "-B", str(DATA / "analyze_fy.py")])
    # 비교기는 결과 파일을 쓰므로 임시 복사본에서 실행한다. 원본 증거는 덮어쓰지 않는다.
    with tempfile.TemporaryDirectory(prefix="ntm-handoff-") as folder:
        temp = Path(folder)
        for name in ("compare_hashes.py", "hashes-start.json", "hashes-end.json"):
            shutil.copyfile(DATA / name, temp / name)
        comparison = run([sys.executable, "-X", "utf8", "-B", str(temp / "compare_hashes.py")], temp)
    historical = json.loads((DATA / "hashes-end.json").read_text(encoding="utf-8"))
    current = []
    for ref in historical["refs"]:
        digest = hashlib.sha256((WORKER / ref["rel"]).read_bytes()).hexdigest()
        current.append({"path": ref["rel"], "historical_sha256": ref["sha256"],
                        "current_sha256": digest, "unchanged": digest == ref["sha256"]})
    snapshots = sorted({*DATA.glob("raw-*.html"), DATA / "meta-forecast-raw.html"})
    raw = []
    for path in snapshots:
        rel = path.relative_to(SCARPPER).as_posix()
        committed = run(["git", "rev-parse", f"b301655:{rel}"])
        working = run(["git", "hash-object", "--", rel])
        raw.append({"file": path.name, "sha256_current": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "git_content_matches_b301655": committed == working})
    result = {"reviewed_commit": "b301655", "evidence_assertions_passed": 10,
              "analysis_stdout": analysis, "historical_comparison_stdout": comparison,
              "current_worker_head": run(["git", "rev-parse", "HEAD"], WORKER),
              "current_worker_refs": current, "quarter_count_discrepancies": count_discrepancies,
              "snapshots": raw,
              "snapshot_limit": "Commit comparison verifies current Git content, not bytes before the first commit."}
    output = ROOT / "validation/ntm-handoff-review-evidence.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"assertions_passed": 10, "count_discrepancies": len(count_discrepancies),
                      "historical_unchanged": comparison.count("UNCHANGED"),
                      "live_unchanged": sum(r["unchanged"] for r in current),
                      "snapshot_count": len(raw),
                      "snapshot_commit_matches": sum(r["git_content_matches_b301655"] for r in raw)}))


if __name__ == "__main__":
    main()
