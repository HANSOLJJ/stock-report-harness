"""QWEN-CLI-DOC-02: 격리 검증 — worker 를 건드리지 않는 최소 실험.

1) scorecard_cli.py 의 approve argparse 정의를 그대로 재현해 `--by ""` 가 통과하는지 확인.
   (worker 의 approve 는 실행하지 않는다 — 산출물을 쓰기 때문.)
2) schema.validate_approval 이 빈 approved_by 를 거부하는지, worker 모듈을 import 만 해서 확인.
   import 와 함수 호출은 읽기 전용이며 파일을 쓰지 않는다.
"""
import argparse
import sys

# ---- 1) argparse 재현 (scorecard_cli.py:167-171 과 동일 정의)
p = argparse.ArgumentParser(prog="scorecard_cli.py approve")
p.add_argument("slug")
p.add_argument("--by", required=True)
p.add_argument("--note")

for argv in (["s", "--by", "홍길동"], ["s", "--by", ""], ["s", "--by", "   "], ["s"]):
    try:
        ns = p.parse_args(argv)
        print("ACCEPT  argv=%-28r -> by=%r (len=%d, strip_len=%d)"
              % (argv, ns.by, len(ns.by), len(ns.by.strip())))
    except SystemExit as exc:
        print("REJECT  argv=%-28r -> SystemExit(%s)" % (argv, exc.code))

# ---- 2) worker 의 실제 validate_approval 호출 (읽기 전용, 파일 쓰기 없음)
sys.path.insert(0, r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scripts")
from scorecard.schema import SchemaError, validate_approval  # noqa: E402

BASE = {
    "schema": "scorecard.approval/1",
    "run_id": "ai-scorecard-test",
    "approval_id": "abc123",
    "approved_at": "2026-09-08",
    "hashes": {"rules": "r", "observations": "o", "judgments": "j",
               "run": "u", "results": "s", "draft": "d"},
}
for label, by in [("정상 이름", "홍길동"), ("빈 문자열", ""), ("공백만", "   "), ("None", None), ("숫자", 7)]:
    payload = dict(BASE, approved_by=by)
    try:
        validate_approval(payload, "ai-scorecard-test")
        print("PASS-SCHEMA  approved_by=%-10r (%s) -> 검증 통과" % (by, label))
    except SchemaError as exc:
        print("FAIL-SCHEMA  approved_by=%-10r (%s) -> %s" % (by, label, exc))

# ---- 3) approved_by 키 자체를 빼면?
payload = {k: v for k, v in BASE.items()}
try:
    validate_approval(payload, "ai-scorecard-test")
    print("PASS-SCHEMA  approved_by 키 없음 -> 검증 통과")
except SchemaError as exc:
    print("FAIL-SCHEMA  approved_by 키 없음 -> %s" % exc)
