# FIX-53 RC-07: 새 checkout 트리에서 obsreg 입력 해시와 baseline 승인 해시가 원시 바이트로 재현되는지 대조한다
"""사용: python verify_fresh_checkout.py <새 checkout 경로>

- obsreg: run·observations·judgments·sources 원시 바이트 sha256 == results.json input_hashes, rules 파일 == run.rule_hash,
  results.json 의 results_hash 를 sha256_obj 로 다시 계산해 일치.
- baseline: rules·observations·judgments·run 원시 바이트 == approval.json hashes, results_hash 재계산 == approval.
  draft 는 drafts/ 가 gitignore 라 새 checkout 에 없다 — 대조하지 못한다고 출력한다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(obj) -> str:
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def results_hash(res: dict) -> str:
    body = {k: v for k, v in res.items() if k != "results_hash"}
    return canonical(body)


def main() -> int:
    tree = Path(sys.argv[1]).resolve()
    ok = True
    runs = tree / "scorecard" / "runs"

    d = runs / "ai-scorecard-2026-09-obsreg"
    res = json.loads((d / "results.json").read_text(encoding="utf-8"))
    run = json.loads((d / "run.json").read_text(encoding="utf-8"))
    print("[obsreg] 입력 해시 (원시 바이트 vs results.input_hashes)")
    for key, fname in (("run", "run.json"), ("observations", "observations.json"), ("judgments", "judgments.json"),
                       ("sources", "sources.json")):
        got, want = sha(d / fname), res["input_hashes"].get(key)
        ok &= got == want
        print(f"  {'ok' if got == want else 'XX'} {key:13} {got[:16]} vs {str(want)[:16]}")
    rules_path = tree / "scorecard" / "rules" / f"{run['rule_version']}.json"
    got = sha(rules_path)
    for label, want in (("rules(run.rule_hash)", run["rule_hash"]), ("rules(input_hashes)", res["input_hashes"].get("rules"))):
        ok &= got == want
        print(f"  {'ok' if got == want else 'XX'} {label:22} {got[:16]} vs {str(want)[:16]}")
    rh = results_hash(res)
    ok &= rh == res["results_hash"]
    print(f"  {'ok' if rh == res['results_hash'] else 'XX'} results_hash 재계산 {rh[:16]}")

    b = runs / "ai-scorecard-2026-09-baseline"
    appr = json.loads((b / "approval.json").read_text(encoding="utf-8"))["hashes"]
    brun = json.loads((b / "run.json").read_text(encoding="utf-8"))
    bres = json.loads((b / "results.json").read_text(encoding="utf-8"))
    print("[baseline] 승인 해시 (원시 바이트 vs approval.json)")
    checks = {"rules": sha(tree / "scorecard" / "rules" / f"{brun['rule_version']}.json"),
              "observations": sha(b / "observations.json"), "judgments": sha(b / "judgments.json"),
              "run": sha(b / "run.json"), "results": bres["results_hash"]}
    for key, got in checks.items():
        ok &= got == appr[key]
        print(f"  {'ok' if got == appr[key] else 'XX'} {key:13} {got[:16]} vs {appr[key][:16]}")
    brh = results_hash(bres)
    ok &= brh == bres["results_hash"]
    print(f"  {'ok' if brh == bres['results_hash'] else 'XX'} results_hash 재계산 {brh[:16]}")
    draft = tree / "drafts" / "ai-scorecard-2026-09-baseline.md"
    print(f"  -- draft: {'있음' if draft.is_file() else 'drafts/ 가 gitignore 라 새 checkout 에 없음 — 대조 불가'}")
    print("판정:", "재현됨" if ok else "재현 안 됨")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
