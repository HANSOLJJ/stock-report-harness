# ADD-01 — 레지스트리 등록 명령이 **추가만** 하고 형식을 지키는지 고정한다
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import registry  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_companies  # noqa: E402

COMPANIES = ROOT / "scorecard" / "companies.json"
CLI = ROOT / "scripts" / "scorecard_cli.py"

NEW = {
    "company_id": "samsung",
    "display_name": "Samsung Electronics",
    "aliases": ["삼성전자"],
    "type": "부품",
    "listed": True,
    "ticker": "005930",
    "exchange": "KRX",
    "share_basis": "common",
    "adr_ratio": None,
    "reporting_currency": "KRW",
    "scope": "반도체·디바이스 전반",
}


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", str(CLI), "add-company", *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))


class RenderLineTest(unittest.TestCase):
    """레지스트리는 **한 줄 = 한 기업** 이다. 이 형식이 깨지면 `추가만 했다`를 diff 가 증명하지 못한다."""

    def test_current_registry_is_reproduced_byte_for_byte(self):
        raw = COMPANIES.read_text(encoding="utf-8")
        payload = load_json_strict(COMPANIES)
        # 마지막 항목을 뺀 나머지 줄은 끝에 `,` 가 붙는다 — 그 한 글자만 빼고 비교한다.
        body = [ln[:-1] if ln.endswith(",") else ln for ln in raw.split("\n")]
        for item in payload["companies"]:
            with self.subTest(cid=item["company_id"]):
                self.assertIn(registry.render_company_line(item), body)
        self.assertEqual(len(payload["companies"]), 14)
        self.assertNotIn("\r\n", raw)                      # 줄바꿈은 LF 다

    def test_line_format_is_the_one_line_form(self):
        line = registry.render_company_line(NEW)
        self.assertTrue(line.startswith("    {"))
        self.assertNotIn("\n", line)
        self.assertEqual(json.loads(line), NEW)            # 한 줄이 그대로 그 항목이다
        self.assertIn("삼성전자", line)                     # ensure_ascii=False


class AddCompanyTest(unittest.TestCase):
    """추가는 텍스트 삽입이다 — 앞 줄은 쉼표 하나 말고 바뀌지 않는다."""

    def setUp(self) -> None:
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name) / "companies.json"
        shutil.copyfile(COMPANIES, self.path)
        self.before = self.path.read_text(encoding="utf-8").split("\n")
        self.addCleanup(self.dir.cleanup)

    def test_insert_keeps_every_earlier_line_byte_identical(self):
        out = registry.add_company(dict(NEW), path=self.path)
        self.assertEqual((out["company_id"], out["count_before"], out["count_after"]), ("samsung", 14, 15))
        after = self.path.read_text(encoding="utf-8").split("\n")
        idx = out["line_no"] - 2                                  # 삽입 지점(앞 항목의 줄)
        self.assertEqual(after[:idx], self.before[:idx])          # 앞 줄들은 바이트 동일
        self.assertEqual(after[idx], self.before[idx] + ",")      # 쉼표 한 글자만 붙는다
        self.assertEqual(after[idx + 1], registry.render_company_line(NEW))
        self.assertEqual(after[idx + 2:], self.before[idx + 1:])  # 꼬리도 그대로
        self.assertEqual(after[-3:], ["  ]", "}", ""])            # 파일 끝 유지
        self.assertNotIn("\r\n", self.path.read_text(encoding="utf-8"))

    def test_added_file_still_passes_the_shared_validator(self):
        registry.add_company(dict(NEW), path=self.path)
        companies = validate_companies(load_json_strict(self.path))
        self.assertIn("samsung", companies)
        self.assertEqual(len(companies), 15)

    def test_validator_catches_the_bad_items_not_us(self):
        """중복·알 수 없는 키·잘못된 값은 **`validate_companies` 가** 잡는다 — 검증을 새로 쓰지 않았다."""
        cases = {
            "중복 id": {**NEW, "company_id": "nvidia", "display_name": "x", "aliases": []},
            "알 수 없는 키": {**NEW, "founded": 1969},
            "잘못된 type": {**NEW, "type": "반도체"},
            "잘못된 share_basis": {**NEW, "share_basis": "gdr"},
            "id 정규식": {**NEW, "company_id": "Samsung Electronics"},
            "adr_ratio 타입": {**NEW, "share_basis": "adr", "adr_ratio": "다섯"},
        }
        for name, item in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(SchemaError):
                    registry.add_company(item, path=self.path)
                self.assertEqual(self.path.read_text(encoding="utf-8").split("\n"), self.before)

    def test_display_name_and_alias_collision_is_refused(self):
        """스키마는 id 중복만 본다. 이름이 겹치면 `resolve_company_id` 가 조용히 엉킨다."""
        for name, item in (("표시명", {**NEW, "display_name": "NVIDIA"}),
                           ("별칭", {**NEW, "aliases": ["MSFT"]}),
                           ("대소문자만 다름", {**NEW, "display_name": "nvidia"})):
            with self.subTest(case=name):
                with self.assertRaises(SchemaError) as cm:
                    registry.add_company(item, path=self.path)
                self.assertIn("충돌", str(cm.exception))

    def test_differently_formatted_registry_is_refused(self):
        """`write_json`(indent=2)으로 다시 쓴 파일은 편집하지 않는다 — 사람이 먼저 정리한다."""
        payload = load_json_strict(self.path)
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        spread = self.path.read_text(encoding="utf-8")
        with self.assertRaises(SchemaError) as cm:
            registry.add_company(dict(NEW), path=self.path)
        self.assertIn("손으로 편집", str(cm.exception))
        self.assertEqual(self.path.read_text(encoding="utf-8"), spread)   # 건드리지 않았다

    def test_broken_registry_is_reported_before_we_touch_it(self):
        """원래 깨져 있던 파일을 우리 탓으로 만들지 않는다."""
        payload = load_json_strict(self.path)
        payload["companies"][0].pop("scope")
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        with self.assertRaises(SchemaError) as cm:
            registry.add_company(dict(NEW), path=self.path)
        self.assertIn("추가 전", str(cm.exception))

    def test_plan_does_not_write(self):
        plan = registry.plan_company_line(dict(NEW), path=self.path)
        self.assertEqual(plan["line"], registry.render_company_line(NEW))
        self.assertEqual(self.path.read_text(encoding="utf-8").split("\n"), self.before)


class CliGuardTest(unittest.TestCase):
    """스키마가 못 잡는 **짝 모순**은 CLI 층이 막는다. 공용 검증기는 건드리지 않는다."""

    def test_dry_run_writes_nothing(self):
        before = COMPANIES.read_bytes()
        res = run_cli("samsung", "--name", "Samsung Electronics", "--type", "부품",
                      "--scope", "반도체", "--listed", "--ticker", "005930",
                      "--exchange", "KRX", "--currency", "KRW", "--dry-run")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("[DRY-RUN]", res.stdout)
        self.assertIn(registry.render_company_line({**NEW, "aliases": [], "scope": "반도체"}), res.stdout)
        self.assertEqual(COMPANIES.read_bytes(), before)

    def test_listed_or_private_is_required_and_exclusive(self):
        res = run_cli("x", "--name", "X", "--type", "업무", "--scope", "s", "--dry-run")
        self.assertEqual(res.returncode, 2)
        self.assertIn("--listed", res.stderr)
        both = run_cli("x", "--name", "X", "--type", "업무", "--scope", "s", "--listed", "--private", "--dry-run")
        self.assertEqual(both.returncode, 2)

    def test_pair_contradictions_are_refused(self):
        cases = {
            "비상장 + ticker": ["x", "--name", "X", "--type", "업무", "--scope", "s", "--private", "--ticker", "AAA"],
            "비상장 + share-basis common": ["x", "--name", "X", "--type", "업무", "--scope", "s", "--private",
                                             "--share-basis", "common"],
            "adr 인데 비율 없음": ["x", "--name", "X", "--type", "업무", "--scope", "s", "--listed",
                                   "--ticker", "AAA", "--exchange", "NYSE", "--share-basis", "adr"],
            "common 인데 비율 있음": ["x", "--name", "X", "--type", "업무", "--scope", "s", "--listed",
                                      "--ticker", "AAA", "--exchange", "NYSE", "--adr-ratio", "5"],
            "상장인데 거래소 없음": ["x", "--name", "X", "--type", "업무", "--scope", "s", "--listed", "--ticker", "AAA"],
        }
        for name, args in cases.items():
            with self.subTest(case=name):
                res = run_cli(*args, "--dry-run")
                self.assertEqual(res.returncode, 1, res.stdout)
                self.assertIn("[FAIL]", res.stderr)

    def test_the_current_fourteen_satisfy_the_same_guards(self):
        """지금 14개사가 이 가드를 전부 만족한다 — 가드가 현실과 어긋나지 않는다."""
        for item in load_json_strict(COMPANIES)["companies"]:
            with self.subTest(cid=item["company_id"]):
                if item["listed"]:
                    self.assertNotEqual(item["share_basis"], "private")
                    self.assertTrue(item["ticker"] and item["exchange"])
                else:
                    self.assertEqual(item["share_basis"], "private")
                    self.assertIsNone(item["ticker"])
                    self.assertIsNone(item["exchange"])
                if item["share_basis"] in {"adr", "ads"}:
                    self.assertIsNotNone(item["adr_ratio"])
                else:
                    self.assertIsNone(item["adr_ratio"])

    def test_name_collision_is_refused_by_the_cli_too(self):
        res = run_cli("newco", "--name", "NVIDIA", "--type", "부품", "--scope", "s",
                      "--listed", "--ticker", "AAA", "--exchange", "NYSE", "--dry-run")
        self.assertEqual(res.returncode, 1)
        self.assertIn("충돌", res.stderr)

    def test_registry_as_of_is_not_touched(self):
        """최상위 `as_of` 는 기준선 14개사 기준일이지 레지스트리 개정일이 아니다."""
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "companies.json"
            shutil.copyfile(COMPANIES, path)
            before = load_json_strict(path)["as_of"]
            registry.add_company(dict(NEW), path=path)
            self.assertEqual(load_json_strict(path)["as_of"], before)


if __name__ == "__main__":
    unittest.main()
