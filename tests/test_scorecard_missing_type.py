# 결측 유형(missing_type) 스키마와 F9 정책-range 정합 검사 고정 테스트 (MISS-LABEL-23)
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.schema import (  # noqa: E402
    MISSING_TYPE_FOR_DISCLOSURE_POLICY,
    MISSING_TYPES,
    SchemaError,
    load_json_strict,
    validate_observations,
    validate_rules,
)

RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"


def company_map() -> dict:
    return {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}


def payload(items: list[dict]) -> dict:
    return {"schema": "scorecard.observations/1", "run_id": "ai-scorecard-2026-09-baseline", "items": items}


def obs(**over) -> dict:
    item = {
        "observation_id": "alibaba.offbalance_B.t", "company_id": "alibaba", "metric": "offbalance_B",
        "value": None, "unit": "USD", "as_of": "2026-09-02", "kind": "actual",
        "source_id": "SRC-t", "status": "not_disclosed",
    }
    item.update(over)
    return item


class TestMissingTypeSchema(unittest.TestCase):
    """값이 없는 이유를 라벨이 직접 말하게 한다. status 하나로는 네 뜻이 갈리지 않는다."""

    def test_four_types_defined(self):
        self.assertEqual(MISSING_TYPES,
                         {"unverified", "not_disclosed_confirmed", "not_applicable", "indeterminate"})

    def test_only_confirmed_type_drives_disclosure_policy(self):
        """C-16 이 걸리는 유형은 하나뿐이다. 우리가 안 찾은 것은 여기 들어오지 않는다."""
        self.assertEqual(MISSING_TYPE_FOR_DISCLOSURE_POLICY, "not_disclosed_confirmed")
        self.assertIn(MISSING_TYPE_FOR_DISCLOSURE_POLICY, MISSING_TYPES)

    def test_valid_missing_type_passes(self):
        for mt in sorted(MISSING_TYPES):
            validate_observations(payload([obs(missing_type=mt)]), company_map(),
                                  run_id="ai-scorecard-2026-09-baseline")

    def test_unknown_missing_type_rejected(self):
        with self.assertRaises(SchemaError):
            validate_observations(payload([obs(missing_type="dunno")]), company_map(),
                                  run_id="ai-scorecard-2026-09-baseline")

    def test_missing_type_on_present_value_rejected(self):
        """값이 있는데 결측 유형을 다는 것은 모순이다."""
        with self.assertRaises(SchemaError):
            validate_observations(payload([obs(value=1.0, status="verified", missing_type="unverified")]),
                                  company_map(), run_id="ai-scorecard-2026-09-baseline")

    def test_missing_type_is_optional(self):
        """기존 관측은 이 필드가 없다. 과거 실행이 계속 로드돼야 한다."""
        validate_observations(payload([obs()]), company_map(), run_id="ai-scorecard-2026-09-baseline")

    def test_approved_run_still_validates(self):
        """승인 대상 파일을 바꾸지 않았다는 것을 스키마 쪽에서도 확인한다."""
        items = load_json_strict(RUN / "observations.json")["items"]
        validate_observations({"schema": "scorecard.observations/1",
                               "run_id": "ai-scorecard-2026-09-baseline", "items": items},
                              company_map(), run_id="ai-scorecard-2026-09-baseline")
        self.assertFalse(any("missing_type" in o for o in items),
                         "승인된 실행의 관측에는 아직 missing_type 이 없어야 한다(반영은 새 실행·승인 사항)")


class TestF9PolicyRange(unittest.TestCase):
    """F6 와 같은 형태로 정책과 factor range 를 로드 시점에 맞춘다."""

    def _rules(self, version: str) -> dict:
        return json.loads((ROOT / "scorecard" / "rules" / f"{version}.json").read_text(encoding="utf-8"))

    def test_v15_and_v16_pass(self):
        for v in ("v1.5", "v1.6"):
            validate_rules(self._rules(v))

    def test_v17_passes_after_c06_rescale(self):
        """검사는 v1.7 의 세 값(floor·bep_retreat·밴드 셋째)을 잡았고 C-06 확정으로 해소됐다.

        해소 전 메시지는 floor=-5, g1_bep_retreat_score=-5, g1_bands_proposed[2].score=-5 였다.
        **밴드를 임의로 고쳐 통과시킨 것이 아니라 C-06 이 값을 정해 준 뒤에 반영했다.**
        """
        validate_rules(self._rules("v1.7"))

    def test_v17_would_be_blocked_if_rescale_reverted(self):
        """재척도를 되돌리면 다시 걸린다. 검사가 살아 있는지 본다."""
        r = self._rules("v1.7")
        r["policies"]["f9"]["floor"] = -5
        with self.assertRaises(SchemaError) as ctx:
            validate_rules(r)
        self.assertIn("floor=-5", str(ctx.exception))

    def test_check_catches_a_newly_introduced_violation(self):
        """검사가 상수 출력이 아니라 입력을 읽는지 본다."""
        r = self._rules("v1.5")
        validate_rules(r)                                   # 원본은 통과
        r["policies"]["f9"]["g2_fcf_negative"] = -9         # range [-5,0] 밖
        with self.assertRaises(SchemaError) as ctx:
            validate_rules(r)
        self.assertIn("g2_fcf_negative=-9", str(ctx.exception))

    def test_threshold_keys_are_not_treated_as_scores(self):
        """연 수·배수 같은 임계치는 점수가 아니다. 범위 검사 대상에서 빠져야 한다."""
        r = self._rules("v1.5")
        r["policies"]["f9"]["g3_runway_keep_years"] = 3     # 양수지만 점수가 아니다
        r["policies"]["f9"]["g4_coverage_keep"] = 1.0
        validate_rules(r)
