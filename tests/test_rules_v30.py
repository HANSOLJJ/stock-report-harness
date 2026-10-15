# 규칙 v3.0 기계용 파일과 스키마 수용(계획 S2) — 층 선언·항목 단위·연속값 곡선·체크리스트를 잠그고 옛 규칙 파일이 그대로인지 본다
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import RULES_DIR, load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

V30 = load_rules("v3.0")
V21 = load_rules("v2.1")


def payload() -> dict:
    return copy.deepcopy(V30.payload)


class StructureTest(unittest.TestCase):
    def test_ranges_follow_rules_md_section_1(self):
        expected = {"F1": [0, 20], "F2": [0, 20], "F3": [0, 20], "F4": [0, 20], "F5": [0, 20],
                    "F6": [-20, 0], "F7": [-12, 0], "F8": [-20, 0], "F9": [-16, 0]}
        self.assertEqual({fid: spec["range"] for fid, spec in V30.payload["factors"].items()}, expected)
        self.assertEqual(V30.payload["scoring"]["moat_max"], 100)
        self.assertEqual(V30.payload["scoring"]["trap_min_active"], -68)

    def test_units_and_modes(self):
        f = V30.payload["factors"]
        self.assertEqual({fid: (f[fid]["unit"], f[fid]["mode"], f[fid]["judgment_kinds"]) for fid in ("F1", "F2", "F3", "F4", "F5")}, {
            "F1": ("business", "business", ["business"]),
            "F2": ("layer", "layer_paths", ["layer_paths"]),
            "F3": ("layer", "layer_cp", ["layer_cp"]),
            "F4": ("company", "holdings", ["holdings"]),
            "F5": ("company", "alliance", ["alliance"]),
        })

    def test_eleven_layers_and_outside(self):
        # 2026-10-14 사용자 결정: 전력을 AI 사슬 조건 층으로 맨 아래에 더해 열한 층이다.
        layers = V30.payload["layers"]
        self.assertEqual(len(layers["order"]), 11)
        self.assertEqual(layers["order"][:2], ["power", "foundry"])
        self.assertEqual(layers["order"][-1], "device")
        self.assertEqual(layers["outside"]["id"], "outside")
        self.assertEqual(set(layers["ai_chain_conditional"]), {"power", "data_platform", "user_platform", "device"})
        self.assertIn("power", V30.payload["factors"]["F2"]["no_benchmark_layers"])
        self.assertEqual(layers["time_window_months"], 24)

    def test_every_market_definition_matches_its_hash(self):
        # 2026-10-15: 규칙이 품은 시장 정의표 해시가 저장소의 파일과 맞아야 한다(정의를 고치면 해시도 고친다)
        files = V30.payload["factors"]["F1"]["markets"]["files"]
        self.assertGreaterEqual(len(files), 7)
        for mid in files:
            with self.subTest(market=mid):
                self.assertEqual(V30.market(mid)["market_id"], mid)

    def test_traps_are_four_times_v21(self):
        f30, f21 = V30.payload["factors"], V21.payload["factors"]
        self.assertEqual(f30["F7"]["matrix"], {k: v * 4 for k, v in f21["F7"]["matrix"].items()})
        self.assertEqual(f30["F8"]["score_multiplier"], 4)
        p30, p21 = V30.f6["parameters"], V21.f6["parameters"]
        for pid in p21:
            with self.subTest(pid=pid):
                self.assertEqual([b["score"] for b in p30[pid]["bands"]], [b["score"] * 4 for b in p21[pid]["bands"]])
        for key in ("floor", "g1_bep_retreat_score", "g2_fcf_negative", "g2_fcf_positive_deteriorating"):
            with self.subTest(key=key):
                self.assertEqual(V30.f9[key], V21.f9[key] * 4)

    def test_curve_anchors_reproduce_section_4_points(self):
        self.assertEqual(V30.f6["parameters"]["P1"]["curve"], {"x_transform": "log2", "anchors": [[1, 0], [8, -12]],
                                                               "note": V30.f6["parameters"]["P1"]["curve"]["note"]})
        self.assertEqual(V30.f6["parameters"]["P2"]["curve"]["anchors"], [[8, 0], [20, -4], [40, -8]])
        self.assertEqual(V30.f9["g3_runway_curve"]["anchors"], [[0, -8], [1, -4], [3, 0]])
        self.assertEqual(V30.payload["factors"]["F3"]["acceleration"]["curve"]["anchors"], [[0.9, 0], [1.1, 6]])


class ChecklistTest(unittest.TestCase):
    def test_q01_to_q25(self):
        self.assertEqual([c["id"] for c in V30.checklist()], [f"Q{n:02d}" for n in range(1, 26)])

    def test_focus_matches_rules_md_section_7(self):
        """rules.md 7절은 "질문 문구는 현행 규칙 JSON 의 checklist 와 같다" 고 적는다. 둘이 갈리면 여기서 걸린다."""
        text = (ROOT / "docs" / "scorecard" / "rules.md").read_text(encoding="utf-8")
        section = text.split("## 7. ", 1)[1].split("\n## ", 1)[0]
        doc = {m.group(1): m.group(2).strip() for m in re.finditer(r"^\| (Q\d\d) \| (.+?) \|", section, flags=re.M)}
        for item in V30.checklist():
            with self.subTest(qid=item["id"]):
                self.assertEqual(doc.get(item["id"]), item["focus"])


class RejectTest(unittest.TestCase):
    def assertRejected(self, p: dict, needle: str) -> None:
        with self.assertRaises(SchemaError) as cm:
            validate_rules(p)
        self.assertIn(needle, str(cm.exception))

    def test_unknown_layer_in_no_benchmark_list(self):
        p = payload()
        p["factors"]["F2"]["no_benchmark_layers"] = ["cloud", "data_platform", "aplication", "device"]
        self.assertRejected(p, "'aplication'")

    def test_every_layer_in_exactly_one_benchmark_list(self):
        # 2026-10-15: 개발 플랫폼이 두 목록 어디에도 없었다. 빠진 층·겹친 층·하나만 빠진 층을 각각 거부한다.
        p = payload()
        p["factors"]["F2"]["no_benchmark_layers"].remove("dev_platform")
        self.assertRejected(p, "['dev_platform'] 이 benchmarks 와 no_benchmark_layers 어디에도 없음")
        p = payload()
        p["factors"]["F2"]["no_benchmark_layers"].append("model")
        self.assertRejected(p, "['model'] 이 benchmarks 와 no_benchmark_layers 에 함께 있음")
        p = payload()
        p["factors"]["F2"]["benchmarks"]["chiplet"] = "없는 층"
        self.assertRejected(p, "benchmarks: 알 수 없는 층 id ['chiplet']")
        self.assertIn("dev_platform", V30.payload["factors"]["F2"]["no_benchmark_layers"])

    def test_gap_months_layer_typo(self):
        p = payload()
        p["factors"]["F2"]["gap_months"]["by_layer"] = {"chip": 12}
        self.assertRejected(p, "'chip'")

    def test_anchor_x_not_increasing(self):
        p = payload()
        p["factors"]["F3"]["acceleration"]["curve"]["anchors"] = [[1.1, 6], [0.9, 0]]
        self.assertRejected(p, "오름차순")

    def test_anchor_score_above_part_max(self):
        p = payload()
        p["factors"]["F4"]["field_strength"]["curve"]["anchors"] = [[0, 0], [0.2, 5]]
        self.assertRejected(p, "[0, 4] 밖")

    def test_f6_parameter_curve_outside_score_range(self):
        p = payload()
        p["policies"]["f6"]["parameters"]["P2"]["curve"]["anchors"] = [[8, 0], [40, -9]]
        self.assertRejected(p, "P2.curve")

    def test_f9_curve_outside_range(self):
        p = payload()
        p["policies"]["f9"]["g3_runway_curve"]["anchors"] = [[0, -17], [3, 0]]
        self.assertRejected(p, "g3_runway_curve")

    def test_log2_needs_positive_x(self):
        p = payload()
        p["policies"]["f6"]["parameters"]["P1"]["curve"]["anchors"] = [[0, 0], [8, -12]]
        self.assertRejected(p, "양수")

    def test_layer_unit_without_layers(self):
        p = payload()
        del p["layers"]
        self.assertRejected(p, "최상위 layers")

    def test_unknown_unit(self):
        p = payload()
        p["factors"]["F4"]["unit"] = "segment"
        self.assertRejected(p, "unit")

    def test_f8_multiplier_too_large(self):
        p = payload()
        p["factors"]["F8"]["score_multiplier"] = 5
        self.assertRejected(p, "score_multiplier")

    def test_cell_values_must_cover_four_kinds(self):
        p = payload()
        del p["layers"]["cell_values"]["preparing"]
        self.assertRejected(p, "cell_values")

    def test_unknown_share_below_half(self):
        # 2026-10-14 사용자 결정: 미확인은 만점의 40%(가운데보다 조금 낮게)
        self.assertEqual(V30.payload["scoring"]["unknown_share"], 0.4)
        self.assertAlmostEqual(V30.unknown_points(4), 1.6)
        self.assertIsNone(V21.unknown_points(4), "선언하지 않은 옛 규칙은 미확인 점수가 없다")
        for bad in (0.5, 0, -0.1, "0.4"):
            p = payload()
            p["scoring"]["unknown_share"] = bad
            with self.subTest(bad=bad):
                self.assertRejected(p, "unknown_share")

    def test_f8_supply_floor_uses_v30_layer_ids(self):
        self.assertEqual(V30.payload["factors"]["F8"]["supply"]["layers_none_floor"]["layers"], ["chip_design", "cloud"])
        p = payload()
        p["factors"]["F8"]["supply"]["layers_none_floor"]["layers"] = ["chip", "cloud"]
        self.assertRejected(p, "layers_none_floor.layers: 알 수 없는 층 id 'chip'")


class OldRulesUntouchedTest(unittest.TestCase):
    def test_old_rule_files_still_load(self):
        for version in ("v1.5", "v1.6", "v1.7", "v1.8", "v1.9", "v2.0", "v2.1"):
            with self.subTest(version=version):
                self.assertNotIn("layers", load_rules(version).payload)

    def test_approved_runs_still_bind_their_rule_files(self):
        """승인된 v2.0·v2.1 실행의 run.json 이 품은 규칙 해시와 지금 규칙 파일의 해시가 같아야 한다."""
        for slug, version in (("ai-scorecard-2026-10-rejudge", "v2.0"), ("ai-scorecard-2026-10-v21", "v2.1")):
            with self.subTest(slug=slug):
                run = json.loads((ROOT / "output" / slug / "run.json").read_text(encoding="utf-8"))
                digest = hashlib.sha256((RULES_DIR / f"{version}.json").read_bytes()).hexdigest()
                self.assertEqual(run["rule_hash"], digest)


if __name__ == "__main__":
    unittest.main()
