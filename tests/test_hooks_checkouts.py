# 같은 저장소의 다른 체크아웃(원본 폴더·다른 워크트리)에 대한 훅 판정을 잠그는 테스트
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_hooks import guard, shell, write


class TwoCheckoutsCase(unittest.TestCase):
    """세션 루트 `wt` 와 다른 체크아웃 `main` 을 임시 폴더에 두고 체크아웃 목록을 모의한다."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()
        self.root = self.tmp / "wt"
        self.main = self.tmp / "main"
        for d in (self.root, self.main):
            d.mkdir()
        patcher = mock.patch.object(guard, "checkout_roots", lambda root: (self.root, self.main))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.m = self.main.as_posix()

    def put(self, base: Path, rel: str, text: str = "x") -> Path:
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def protect(self, payload: dict) -> guard.Decision:
        return guard.protect_sensitive_files(payload, root=self.root)


PROTECTED = (".env", "scorecard/history.csv", "scorecard/rules/v1.7.json", "scorecard/baseline/v1.5/triggers.json",
             "output/ai-scorecard-2026-09-obsreg/draft.md", "output/ai-scorecard-2026-10-new/approval.json")


class OtherCheckoutProtectedTest(TwoCheckoutsCase):
    def test_file_tools_block_protected_paths_in_other_checkout(self):
        for rel in PROTECTED:
            for tool in ("Write", "Edit"):
                with self.subTest(rel=rel, tool=tool):
                    d = self.protect(write(f"{self.m}/{rel}", tool=tool))
                    self.assertEqual(d.kind, "block")
        d = self.protect(write(f"{self.m}/scorecard/history.csv"))
        self.assertIn("scorecard/history.csv (체크아웃 main)", d.text)

    def test_shell_writes_block_protected_paths_in_other_checkout(self):
        self.put(self.main, "scorecard/baseline/v1.5/triggers.json")
        for cmd in (f"rm {self.m}/.env", f"rm {self.m}/scorecard/history.csv", f"echo x > {self.m}/scorecard/rules/v1.7.json",
                    f"rm -rf {self.m}/scorecard/baseline", f"rm -rf {self.m}/scorecard", f"mv {self.m}/output/ai-scorecard-2026-09-obsreg /tmp/x",
                    f"cd {self.m}/scorecard && rm history.csv", f"sed -i s/a/b/ {self.m}/scorecard/history.csv",
                    f"Remove-Item {self.m}/.env"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.protect(shell("Bash", cmd)).kind, "block")

    def test_removing_a_whole_checkout_or_its_parent_is_blocked(self):
        for cmd in (f"rm -rf {self.m}", f"rm -rf {self.tmp.as_posix()}", f"Remove-Item -Recurse {self.m}"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.protect(shell("PowerShell", cmd)).kind, "block")

    def test_interpreter_mentions_by_absolute_path(self):
        for cmd in (f"python -c \"open('{self.m}/.env','w')\"",
                    f"uv run python fix.py {self.m}/scorecard/history.csv",
                    f"python -c \"open('{self.root.as_posix()}/scorecard/history.csv','w')\"",   # 세션 루트 자신의 절대 경로
                    f"bash -c 'echo x > {self.m}/scorecard/baseline/v1.5/scores.json'"):
            with self.subTest(cmd=cmd):
                self.assertEqual(self.protect(shell("Bash", cmd)).kind, "block")

    def test_unprotected_and_read_only_are_allowed(self):
        for payload in (write(f"{self.m}/docs/notes.md"), write(f"{self.tmp.as_posix()}/elsewhere/notes.md"),
                        write(f"{self.m}/output/ai-scorecard-2026-10-new/draft.md"),
                        shell("Bash", f"cat {self.m}/.env"), shell("Bash", f"rm {self.m}/docs/notes.md"),
                        shell("Bash", f"python fix.py {self.m}/docs/notes.md"),
                        shell("Bash", f"rm -rf {self.tmp.as_posix()}/elsewhere"),
                        shell("Bash", f"git -C {self.m} log -- scorecard/history.csv"),
                        # 같은 접두로 시작하는 이웃 폴더는 체크아웃이 아니다
                        shell("Bash", f"python fix.py {self.m}2/scorecard/history.csv")):
            with self.subTest(payload=payload["tool_input"]):
                self.assertEqual(self.protect(payload).kind, "allow")

    @unittest.skipUnless(os.name == "nt", "Git Bash 드라이브 표기는 Windows 에서만 푼다")
    def test_git_bash_drive_spelling(self):
        drive, rest = self.m[0].lower(), self.m[2:]
        for prefix in (f"/{drive}", f"/mnt/{drive}", f"/cygdrive/{drive}"):
            with self.subTest(prefix=prefix):
                self.assertEqual(self.protect(shell("Bash", f"rm {prefix}{rest}/.env")).kind, "block")
                self.assertEqual(self.protect(shell("Bash", f"python -c \"open('{prefix}{rest}/.env','w')\"")).kind, "block")
        own = self.root.as_posix()
        self.assertEqual(self.protect(shell("Bash", f"rm /{own[0].lower()}{own[2:]}/.env")).kind, "block")


class OtherCheckoutStageAndAdviceTest(TwoCheckoutsCase):
    def test_enforce_plan_checks_the_owning_checkout(self):
        target = f"{self.m}/output/t/draft.md"
        d = guard.enforce_plan(write(target), root=self.root)
        self.assertEqual(d.kind, "block")
        self.assertIn("선행 산출물 누락", d.text)
        self.put(self.main, "output/t/plan.md")
        self.put(self.main, "output/t/research.md")
        self.assertEqual(guard.enforce_plan(write(target), root=self.root).kind, "allow")
        self.assertEqual(guard.enforce_plan(write(f"{self.m}/output/t/report.html"), root=self.root).kind, "block")

    def test_financial_advice_is_checked_in_other_checkout(self):
        d = guard.forbid_financial_advice(write(f"{self.m}/output/t/draft.md", "지금 매수 하자"), root=self.root)
        self.assertEqual(d.kind, "block")


class CheckoutListTest(unittest.TestCase):
    def setUp(self) -> None:
        guard.checkout_roots.cache_clear()
        self.addCleanup(guard.checkout_roots.cache_clear)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name).resolve()

    def test_folder_without_git_is_a_single_checkout(self):
        self.assertEqual(guard.checkout_roots(self.tmp), (self.tmp,))

    def test_git_failure_blocks_outside_paths_only(self):
        root = self.tmp / "wt"
        (root / ".git").mkdir(parents=True)
        with mock.patch.object(guard.subprocess, "run", side_effect=OSError("git 없음")):
            outside = guard.protect_sensitive_files(write(f"{self.tmp.as_posix()}/main/scorecard/history.csv"), root=root)
            self.assertEqual(outside.kind, "block")
            self.assertIn("판정을 할 수 없어", outside.text)
            # 세션 루트 안의 경로는 git 을 부르지 않는다
            self.assertEqual(guard.protect_sensitive_files(write("docs/notes.md"), root=root).kind, "allow")
            self.assertEqual(guard.protect_sensitive_files(write("scorecard/history.csv"), root=root).kind, "block")
            self.assertEqual(guard.protect_sensitive_files(shell("Bash", "git status"), root=root).kind, "allow")

    @unittest.skipUnless(shutil.which("git"), "git 없음")
    def test_real_worktree_is_listed_and_protected(self):
        main, wt = self.tmp / "main", self.tmp / "wt"
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run([*git, "init", "-q", str(main)], check=True)
        subprocess.run([*git, "-C", str(main), "commit", "-q", "--allow-empty", "-m", "init"], check=True)
        subprocess.run([*git, "-C", str(main), "worktree", "add", "-q", str(wt), "-b", "wt"], check=True)
        self.addCleanup(subprocess.run, [*git, "-C", str(main), "worktree", "remove", "--force", str(wt)], check=False)
        self.assertEqual(guard.checkout_roots(wt), (wt, main))
        d = guard.protect_sensitive_files(write(f"{main.as_posix()}/scorecard/history.csv"), root=wt)
        self.assertEqual(d.kind, "block")
        self.assertEqual(guard.protect_sensitive_files(shell("Bash", f"rm -rf {main.as_posix()}/scorecard/baseline"), root=wt).kind, "block")


if __name__ == "__main__":
    unittest.main()
