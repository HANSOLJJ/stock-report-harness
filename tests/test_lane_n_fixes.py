# 레인 N(재검증 V2-1~V2-3) 수정을 잠근다: 승인 파일 이름·approval_id 재계산, 승인 실행 보호, 이어받기의 근거·트리거
from __future__ import annotations

import os
import unittest

from tests.test_approval_commands import EXISTING, SLUG, FlowBase
from scorecard import engine, stages
from scorecard.schema import SchemaError, approval_file_present, approval_id_for, load_json_strict, validate_approval, write_json


def rename_case(path, new_name: str) -> None:
    """Windows 는 대소문자만 다른 이름으로 바로 바꾸지 못할 때가 있어 두 번 옮긴다."""
    tmp = path.with_name(path.name + ".tmp")
    os.replace(path, tmp)
    os.replace(tmp, path.with_name(new_name))


class ApprovalFileNameTest(FlowBase):
    """V2-3. 승인은 이름이 정확히 approval.json 인 파일만이고, approval_id 는 다시 계산해 대조한다."""

    def setUp(self) -> None:
        super().setUp()
        self.ready()
        stages.approve(SLUG, approved_by="user", via="browser", allow_agent_session=True)

    def test_case_variant_file_is_not_an_approval(self):
        rename_case(self.approval_path, "Approval.json")
        self.assertFalse(approval_file_present(self.box.run_dir))
        with self.assertRaisesRegex(SchemaError, "정확히 approval.json"):
            load_json_strict(self.approval_path)
        self.assertFalse(stages.status(SLUG)["approval"])
        self.assertEqual(stages.summary(SLUG)["approval"]["exists"], False)
        with self.assertRaises(SchemaError):
            stages.revoke(SLUG, by="user", note="x", allow_agent_session=True)

    def test_arbitrary_approval_id_is_rejected(self):
        approval = load_json_strict(self.approval_path)
        self.assertEqual(approval["approval_id"], approval_id_for(SLUG, approval["hashes"]))
        write_json(self.approval_path, {**approval, "approval_id": "0000000000000000"})
        with self.assertRaisesRegex(SchemaError, "다시 계산한 값"):
            validate_approval(load_json_strict(self.approval_path), SLUG)
        self.assertFalse(stages.status(SLUG)["approval_valid"])
        self.assertFalse(stages.summary(SLUG)["approval"]["valid"])


class ExistingApprovalIdTest(unittest.TestCase):
    def test_existing_runs_approval_id_equals_recomputed(self):
        for slug in EXISTING:
            with self.subTest(slug=slug):
                approval = load_json_strict(engine.run_dir(slug) / "approval.json")
                self.assertEqual(approval["approval_id"], approval_id_for(slug, approval["hashes"]))
                validate_approval(approval, slug)
                self.assertTrue(stages.status(slug)["approval_valid"])


if __name__ == "__main__":
    unittest.main()
