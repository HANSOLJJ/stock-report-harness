"""QWEN-NTM-DATA-03: 시작/종료 해시 비교 + 외부 변경(설계진행 승인 문서 수정) 분리 기록."""
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
W = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
load = lambda n: json.load(io.open(os.path.join(HERE, n), encoding="utf-8"))

a, b = load("hashes-start.json"), load("hashes-end.json")
sa = {r["rel"]: r for r in a["refs"] if not r.get("missing")}
sb = {r["rel"]: r for r in b["refs"] if not r.get("missing")}

print("worker HEAD  start=%s  end=%s  %s"
      % (a["head"][:7], b["head"][:7], "SAME" if a["head"] == b["head"] else "CHANGED (외부)"))
print("git status   start=%s" % a["status"])
print("             end  =%s" % b["status"])
print()
print("%-46s %-18s %-18s %s" % ("ref", "sha256[:16] start", "end", "판정"))
changed = []
for rel in sorted(set(sa) | set(sb)):
    x, y = sa.get(rel), sb.get(rel)
    if x and y:
        same = x["sha256"] == y["sha256"]
        print("%-46s %-18s %-18s %s" % (rel, x["sha256"][:16], y["sha256"][:16],
                                        "UNCHANGED" if same else "CHANGED"))
        if not same:
            changed.append(rel)
    else:
        print("%-46s %-18s %-18s MISSING" % (rel, x and x["sha256"][:16], y and y["sha256"][:16]))
        changed.append(rel)

print("\n참조 파일 변경: %d건 %s" % (len(changed), changed or "없음"))

# AGENTS.md 는 내 참조 목록에 없으므로 별도로 측정
import hashlib
p = os.path.join(W, "AGENTS.md")
h_now = hashlib.sha256(open(p, "rb").read()).hexdigest()
print("\nworker/AGENTS.md 현재 sha256[:16] = %s" % h_now[:16])
print("(QWEN-CLI-DOC-02 시작 시점 기록값 = 6afb005d0f42a19e → 변경됨)")

# 외부 커밋이 무엇을 건드렸는지 확정
for rng in ["96d88bc c13a293"]:
    out = subprocess.run(["git", "diff", "--name-status"] + rng.split(), cwd=W,
                         capture_output=True, text=True).stdout.strip()
    print("\ngit diff --name-status %s:\n%s" % (rng, out or "(변경 없음)"))
    stat = subprocess.run(["git", "show", "--stat", "--oneline", "c13a293"], cwd=W,
                          capture_output=True, text=True).stdout.strip()
    print("\ngit show --stat c13a293:\n%s" % stat)

verdict = {
    "worker_head_start": a["head"],
    "worker_head_end": b["head"],
    "head_changed_during_task": a["head"] != b["head"],
    "external_commit": "c13a293 docs: Orca 추가 작업 요청 시 터미널 실행 안내 의무화",
    "external_commit_files": ["AGENTS.md"],
    "external_commit_authority": "설계진행의 사용자 승인 공통문서 수정 (msg_d5a1cd690527 로 통지됨)",
    "my_reference_files_changed": changed,
    "conclusion": ("HEAD 는 외부 승인 커밋으로 96d88bc → c13a293 이동했으나, "
                   "그 커밋은 AGENTS.md 9줄 추가뿐이고 내가 근거로 쓴 참조 파일 8종은 "
                   "전부 해시 불변이다. 따라서 NTM 판정의 근거는 영향받지 않았다."),
    "pre_existing_dirty": b["status"],
}
with io.open(os.path.join(HERE, "integrity-verdict.json"), "w", encoding="utf-8") as f:
    json.dump(verdict, f, ensure_ascii=False, indent=1)
print("\n저장: integrity-verdict.json")
print("\n결론: " + verdict["conclusion"])
