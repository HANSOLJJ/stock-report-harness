# FIX-52 스키마 보강 — net_cash 세 블록 존재 강제와 판단 점수·매트릭스 출력의 factor range 검사를 고정한다
"""이 테스트가 지키는 계약 둘.

1. **검사는 블록이 있을 때만 도는 것이 아니라 블록 자체를 요구한다.** 작업 정의인 net_cash 에서
   `scope_separation`·`two_axes`·`banned_word` 를 지우면 검증이 거부해야 한다(리뷰 C codex 발견).
2. **판단이 만드는 점수는 factor range 안이다.** 승계 score 와 F7 매트릭스 출력 둘 다. v1.7 함정 재배분에서
   F7 range 는 [-2,0] 으로 줄었는데 매트릭스 `large|yes` 가 -3 에 남아 nvidia·oracle 이 범위 밖 점수를 받았다.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_judgments, validate_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / RUN_ID
REGISTRY = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}


def judgments() -> dict:
    return json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))


class NetCashBlocksRequiredTest(unittest.TestCase):
    def _reject(self, mutate, needle: str) -> None:
        payload = copy.deepcopy(RULES.payload)
        mutate(payload["policies"]["f6"]["net_cash"])
        with self.assertRaises(SchemaError) as cm:
            validate_rules(payload)
        self.assertIn(needle, str(cm.exception))

    def test_deleting_scope_separation_is_rejected(self):
        self._reject(lambda nc: nc.pop("scope_separation"), "scope_separation: 작업 정의")

    def test_deleting_two_axes_is_rejected(self):
        self._reject(lambda nc: nc["scope_separation"].pop("two_axes"), "two_axes: 작업 정의")

    def test_deleting_banned_word_is_rejected(self):
        self._reject(lambda nc: nc["scope_separation"]["two_axes"].pop("banned_word"), "banned_word: 작업 정의")

    def test_current_rules_pass(self):
        validate_rules(copy.deepcopy(RULES.payload))


class JudgmentScoreInRangeTest(unittest.TestCase):
    def test_rules_reject_matrix_cell_outside_range(self):
        payload = copy.deepcopy(RULES.payload)
        payload["factors"]["F7"]["matrix"]["large|yes"] = -3
        with self.assertRaises(SchemaError) as cm:
            validate_rules(payload)
        self.assertIn("large|yes", str(cm.exception))

    def test_pre_rescale_rules_reject_nvidia_and_oracle(self):
        """**S1 반영 전 규칙(`large|yes=-3`)으로 판단을 검증하면 nvidia·oracle 에서 거부된다.**"""
        payload = copy.deepcopy(RULES.payload)
        payload["factors"]["F7"]["matrix"]["large|yes"] = -3
        with self.assertRaises(SchemaError) as cm:
            validate_judgments(judgments(), REGISTRY, payload, RUN_ID)
        self.assertIn("nvidia", str(cm.exception))                       # 파일 순서상 먼저 걸리는 쪽
        # oracle 도 같은 이유로 걸린다 — nvidia 를 범위 안으로 돌려도 멈춘다
        jud = judgments()
        for j in jud["items"]:
            if j["company_id"] == "nvidia" and j["factor"] == "F7":
                j["inputs"]["own_money_returns"] = "no"
        with self.assertRaises(SchemaError) as cm:
            validate_judgments(jud, REGISTRY, payload, RUN_ID)
        self.assertIn("oracle", str(cm.exception))

    def test_carried_score_outside_range_is_rejected(self):
        jud = judgments()
        target = next(j for j in jud["items"] if j["kind"] == "score" and j["factor"] == "F8")
        target["score"] = -6
        with self.assertRaises(SchemaError):
            validate_judgments(jud, REGISTRY, RULES.payload, RUN_ID)

    def test_current_judgments_pass(self):
        validate_judgments(judgments(), REGISTRY, RULES.payload, RUN_ID)


class F7RescaleTest(unittest.TestCase):
    """S1 — range 를 유지하고 매트릭스를 재척도한다(사용자 결정)."""

    def test_matrix_fits_range_and_loss_is_written(self):
        f7 = RULES.payload["factors"]["F7"]
        self.assertEqual(f7["range"], [-2, 0])
        self.assertEqual(f7["matrix"], {"small|no": 0, "large|no": -2, "small|yes": -1, "large|yes": -2})
        r = f7["matrix_rescale"]
        self.assertIn("세로축", r["discrimination_loss"])
        self.assertIn("해당 없음 — 예약", r["current_impact"])
        self.assertIn("영향이 없다", r["current_impact"])

    def test_nvidia_oracle_replaced_with_old_kept(self):
        res = {c["company_id"]: c for c in json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))["companies"]}
        for cid in ("nvidia", "oracle"):
            with self.subTest(cid=cid):
                j = next(x for x in judgments()["items"] if x["company_id"] == cid and x["factor"] == "F7")
                self.assertEqual(j["judgment_id"], f"{cid}.F7.fix52")
                self.assertEqual(j["reviewer"], "설계진행(리뷰 C codex 발견 · 사용자 결정)")
                self.assertEqual(j["reviewed_at"], "2026-09-15")
                self.assertEqual(j["inputs"], {"funding_dependent_share": "large", "own_money_returns": "yes"})
                self.assertTrue(j["superseded"]["evidence"][0].startswith("-3"))   # 옛 문언 보존
                self.assertEqual(res[cid]["factors"]["F7"]["score"], -2)
        self.assertEqual(res["nvidia"]["total"], 9)
        self.assertEqual(res["oracle"]["total"], 2)

    def test_v15_matrix_untouched(self):
        self.assertEqual(load_rules("v1.5").payload["factors"]["F7"]["matrix"]["large|yes"], -3)


if __name__ == "__main__":
    unittest.main()
