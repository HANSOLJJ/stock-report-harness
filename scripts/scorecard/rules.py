# 규칙 원본(scorecard/rules/*.json) 로드·해시와 구간표·사다리·매트릭스·실행 단위 결정 조회 헬퍼
from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from report_contract_lib import ROOT

from .schema import SchemaError, load_json_strict, sha256_file, validate_rules

RULES_DIR = ROOT / "scorecard" / "rules"


class RuleSet:
    def __init__(self, payload: dict[str, Any], path: Path):
        self.payload = validate_rules(payload)
        self.path = path
        self.version: str = payload["rule_version"]
        self.hash: str = sha256_file(path)

    # ------------------------------------------------------------ lookups
    def factor(self, fid: str) -> dict[str, Any]:
        return self.payload["factors"][fid]

    def factor_range(self, fid: str) -> tuple[int, int]:
        lo, hi = self.factor(fid)["range"]
        return int(lo), int(hi)

    @property
    def f6(self) -> dict[str, Any]:
        return self.payload["policies"]["f6"]

    @property
    def f9(self) -> dict[str, Any]:
        return self.payload["policies"]["f9"]

    @property
    def source_policy(self) -> dict[str, Any] | None:
        """자료 원천 allowlist. 정책이 없는 규칙 버전(v1.5)은 None 이라 기존 실행에 영향이 없다."""
        return self.payload.get("sources")

    def source_violation(self, url: str | None) -> str | None:
        """생산 원천 url 하나를 검사한다. 위반이면 사유, 통과면 None."""
        policy = self.source_policy
        if not policy or not url:
            return None
        host = urlsplit(url).hostname or ""
        host = host.lower()
        for entry in policy.get("denied", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                return f"{host} 는 생산 원천에서 배제됨 — {entry['reason']}"
        # 채택 안 함이 먼저다. 이 블록이 없으면 not_adopted host 가 마지막 fallback 으로 떨어져
        # "약관 확인 후 규칙에 등재하고 쓴다" 는 안내가 나온다 — **우리가 막으려는 행동을 지시하게 된다.**
        for entry in policy.get("not_adopted", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                return (f"{host} 는 검토를 마치고 채택하지 않기로 결정된 원천 — "
                        f"{entry['reason']} (결정 {entry['decided_at']}, {entry['decided_by']}). "
                        f"재조사 불필요. 재개 조건: {entry['reopen_condition']}")
        # 과거 규칙 파일 호환. v1.6·v1.7 초판은 conditional_candidates 를 쓴다. 지우지 않는다.
        for entry in policy.get("conditional_candidates", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                need = ", ".join(entry["required_written_conditions"])
                return f"{host} 는 미승인 후보 — 서면 확정 필요: {need}"
        allowed = [e["host"] for e in policy.get("allowed", [])]
        if any(host == a or host.endswith("." + a) for a in allowed):
            return None
        # 검토를 마치고 안 넣기로 한 host 는 그 사유를 돌려준다. 판정(위반)은 같지만 **안내가 다르다** —
        # 아래 fallback 은 "약관 확인 후 등재하고 쓴다" 라서 이미 확인하고 막은 host 에 재조사를 지시한다
        # (not_adopted 에서 고친 것과 같은 함정, SCOPE-34).
        for entry in policy.get("unlisted", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                return (f"{host} 는 검토를 마치고 등재하지 않은 host — {entry['reason']} "
                        f"(검토 {entry['decided_at']}). 재조사 전에 이 사유부터 본다.")
        return f"{host} 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"

    def decision(self, decision_id: str) -> dict[str, Any] | None:
        for item in self.payload["decisions"]:
            if item["id"] == decision_id:
                return item
        return None

    def pending_decisions(self) -> list[dict[str, Any]]:
        return [d for d in self.payload["decisions"] if d["status"] == "pending"]

    def checklist(self) -> list[dict[str, Any]]:
        return list(self.payload["checklist"])

    # ------------------------------------------------------------ F6 band
    def f6_band(self, per: float) -> tuple[int, str]:
        """PER 을 반개방 구간표에 넣어 (점수, 구간 라벨) 반환. 표시 반올림은 개입하지 않는다."""
        lower = 0.0
        for band in self.f6["bands"]:
            upper = band["upper"]
            if upper is None or per < upper:
                label = f"{lower:g}~{upper:g}" if upper is not None else f"{lower:g}+"
                return int(band["score"]), label
            lower = float(upper)
        raise SchemaError("f6 bands 가 구간을 덮지 못함")

    def f6_boundaries(self) -> list[float]:
        return [float(b["upper"]) for b in self.f6["bands"] if b["upper"] is not None]

    def f6_boundary_flag(self, per: float) -> dict[str, Any]:
        tol = float(self.f6["boundary_tolerance"])
        nearest = min(self.f6_boundaries(), key=lambda b: abs(per - b) / b)
        distance = (per - nearest) / nearest
        # 정확히 3% 인 경우도 경계 대상(T-02). 부동소수 오차로 빠지지 않게 12자리에서 반올림해 비교한다.
        return {
            "flag": round(abs(distance), 12) <= tol,
            "nearest_boundary": nearest,
            "distance_ratio": distance,
            "tolerance": tol,
        }

    # ------------------------------------------------------------ F6 v1.7 파라미터
    @property
    def f6_mode(self) -> str:
        """per_band(v1.5·v1.6) 인지 parameters(v1.7) 인지. 과거 규칙 파일도 계속 읽는다."""
        return self.f6.get("mode", "per_band")

    def f6_parameters(self) -> dict[str, Any]:
        return self.f6.get("parameters") or {}

    def f6_parameter_band(self, pid: str, value: float) -> tuple[int, str]:
        """파라미터 값을 반개방 구간에 넣어 (점수, 구간 라벨) 반환. 표시 반올림은 개입하지 않는다."""
        spec = self.f6_parameters().get(pid)
        if spec is None:
            raise SchemaError(f"F6 파라미터 {pid!r} 가 규칙에 없음")
        if spec["comparison"] == "upper_exclusive":
            lower = 0.0
            for band in spec["bands"]:
                upper = band["upper"]
                if upper is None or value < upper:
                    label = f"{lower:g}~{upper:g}" if upper is not None else f"{lower:g}+"
                    return int(band["score"]), label
                lower = float(upper)
        else:                                     # lower_inclusive — 큰 값이 좋다
            upper = None
            for band in spec["bands"]:
                low = band["lower"]
                if low is None or value >= low:
                    label = f"{low:g}~{upper:g}" if (low is not None and upper is not None) else (
                        f"{low:g}+" if low is not None else f"~{upper:g}")
                    return int(band["score"]), label
                upper = float(low)
        raise SchemaError(f"F6 파라미터 {pid} 구간표가 값을 덮지 못함: {value!r}")

    def f6_parameter_boundaries(self, pid: str) -> list[float]:
        spec = self.f6_parameters().get(pid) or {}
        key = "upper" if spec.get("comparison") == "upper_exclusive" else "lower"
        return [float(b[key]) for b in spec.get("bands", []) if b.get(key) is not None]

    def f6_parameter_boundary_flag(self, pid: str, value: float) -> dict[str, Any]:
        """경계 ±tolerance 표시. 점수를 바꾸지 않는다."""
        tol = float(self.f6["boundary_tolerance"])
        edges = self.f6_parameter_boundaries(pid)
        if not edges:
            return {"flag": False, "nearest_boundary": None, "distance_ratio": None, "tolerance": tol}
        nearest = min(edges, key=lambda b: abs(value - b) / abs(b) if b else abs(value - b))
        distance = (value - nearest) / nearest if nearest else 0.0
        return {
            "flag": round(abs(distance), 12) <= tol,
            "nearest_boundary": nearest,
            "distance_ratio": distance,
            "tolerance": tol,
        }

    def f6_tracks(self) -> dict[str, Any]:
        return self.f6.get("tracks") or {}

    def f6_track(self, track_id: str) -> dict[str, Any]:
        spec = self.f6_tracks().get(track_id)
        if spec is None:
            raise SchemaError(f"F6 트랙 {track_id!r} 가 규칙에 없음")
        return spec

    def f6_p4(self) -> dict[str, Any]:
        return self.f6.get("p4") or {}

    def f6_stale_months(self, period_basis: str | None) -> int | None:
        """`stale_asof` 임계(개월). 선언이 없거나 기준을 모르면 `None` — 검사를 건너뛴다.

        **보고 주기에 상대적으로 둔다.** 단일 임계는 안 된다 — 6 하나면 연간 신고자가 상시 걸려
        `period_basis_not_ttm` 과 중복되고, 16 하나면 분기 신고자가 10개월 묵어도 안 걸린다.
        """
        cond = {c["id"]: c for c in self.f6_p4().get("conditions", [])}.get("stale_asof") or {}
        thresholds = cond.get("thresholds_months")
        if not thresholds or period_basis is None:
            return None
        key = (cond.get("basis_map") or {}).get(period_basis, period_basis)
        value = thresholds.get(key)
        return None if value is None else int(value)

    def f6_fx(self) -> dict[str, Any]:
        return self.f6.get("fx") or {}

    def f6_net_cash(self) -> dict[str, Any]:
        """P2 의 `net_cash` 가 **무엇을 세는가**. 규칙에 정의가 없던 자리를 채운 작업 정의다 (NETCASH-37).

        두 가지를 같이 들고 있다.

        1. **작업 정의** — `현금 + 시장성 유가증권 − 총차입금 − 리스부채`. **'유가증권 전체' 가 아니라
           '시장성 있는 것' 이다** — 지분법 투자와 비상장 지분은 팔아서 기업 청구권을 상환할 수 없어
           뺀다(`securities_scope`). 출처는 v1.5 legacy 역산이지 설계가 의도한 정의라는 증거가 아니다.
           몇 개사에서 맞고 몇 개사가 다른지는 **`evidence.matched.count` 와 `evidence.differs.count` 가
           갖고 있다** — 숫자를 여기 박아 두면 라운드가 바뀔 때마다 이 문서만 뒤처진다(실제로 그랬다).
        2. **적용 범위 구분** (`scope_separation`) — 설계 지침 6.4 는 **런웨이** 절이라 즉시 쓸 수 있는
           현금만 세고, 여기 P2 는 **EV 조정**이라 시장성 있는 재무적 자산을 센다. 같은 '현금' 이라는 말이
           두 자리에서 다른 것을 가리키므로 한쪽 논거를 다른 쪽으로 옮기면 조용히 틀린다. alphabet
           한 회사에서만 1,865.6억 달러가 갈리고 부호까지 뒤집힌다.

        `status` 가 `working_definition` 인 동안은 **확정 정의가 나오면 대체된다**는 뜻이다.
        """
        return self.f6.get("net_cash") or {}

    # ------------------------------------------------------------ F6 비상장 (C-12)
    def f6_private_bands(self) -> dict[str, Any]:
        return self.f6.get("private_bands") or {}

    def f6_private_correction(self) -> dict[str, Any]:
        return self.f6.get("private_correction") or {}

    def f6_private_band(self, value: float) -> tuple[int, str]:
        """비상장 배수를 v1.5 구간표에 넣어 (점수, 구간 라벨). 상장 밴드와 표가 다르다."""
        spec = self.f6_private_bands()
        bands = spec.get("bands") or []
        if not bands:
            raise SchemaError("F6 비상장 밴드가 규칙에 없음 — C-12 미확정")
        for band in bands:
            lower = band.get("lower")
            if lower is None or value >= float(lower):
                return int(band["score"]), str(band.get("label") or lower)
        raise SchemaError(f"F6 비상장 밴드가 값 {value!r} 를 덮지 않음")

    def f6_ttm_window(self) -> dict[str, Any]:
        return self.f6.get("ttm_window") or {}

    def f6_q4_restatement_check(self, components: list[dict[str, Any]],
                                overlap_conflicts: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """`FY - (Q1+Q2+Q3)` 의 네 성분이 **같은 재작성 세대**에서 왔는지 본다 (F6-REG-28).

        같은 기간의 같은 지표라도 나중 보고서가 회계기준 변경으로 다시 낸 값이 있다. 그 값과
        원래 기준의 분기 누계를 빼면 **어느 분기에도 존재한 적 없는 수**가 나온다. MSFT FY2016 이
        그 사례이고 규칙 파일 `policies.f6.ttm_window.restatement_generation.why` 에 적어 두었다.

        ## 세대를 무엇으로 가르는가 — 두 번 좁혔다

        처음에는 `accession` 으로 갈랐다. **모든 복원이 막혔다** — 정상 복원도 FY 는 10-K, 분기는
        10-Q 에서 오므로 accession 이 늘 다르다. 다음에는 개념 이름(`tag`)으로 갈랐다. **alphabet 이
        막혔다** — `Revenues` 에서 `RevenueFromContractWithCustomerExcludingAssessedTax` 로 태그가
        바뀌었을 뿐이고 겹치는 기간의 값은 일치한다. 이름이 다른 것과 기준이 다른 것은 다르다.

        그래서 **값으로 가른다.** 성분들의 태그가 여럿이어도 겹치는 기간에서 값이 일치하면 같은
        세대이고, 어긋나면 다른 세대다. 그 증거는 수집기가 이미 `overlap_conflicts` 로 모아 둔다.
        `restated`(같은 태그 안에서 같은 기간에 값이 여럿이었는가)가 성분마다 다른 것도 섞임이다.

        `components` 는 `{"label", "tag", "restated"}` 들이고, `overlap_conflicts` 는
        `{"period", "kept": {"tag", "val"}, "other": {"tag", "val"}, "rel_diff"}` 들이다.
        규칙에 `restatement_generation` 선언이 없으면(v1.5·v1.6) 검사를 건너뛴다.
        """
        spec = self.f6_ttm_window().get("restatement_generation")
        if not spec:
            return {"checked": False, "ok": True, "reason": "규칙에 restatement_generation 선언 없음"}
        tags = {c.get("tag") for c in components}
        restated = {bool(c.get("restated")) for c in components}
        action = spec.get("on_mixed", "hold")
        if len(restated) > 1:
            who = [c.get("label", "?") for c in components if c.get("restated")]
            return {"checked": True, "ok": False, "action": action, "tags": sorted(t for t in tags if t),
                    "reason": f"재작성된 성분과 아닌 성분이 섞였다 — 재작성: {', '.join(who)}"}
        hits = []
        for conflict in overlap_conflicts or []:
            pair = {(conflict.get("kept") or {}).get("tag"), (conflict.get("other") or {}).get("tag")}
            if len(pair & tags) == 2:
                hits.append(conflict)
        if hits:
            worst = max(hits, key=lambda c: c.get("rel_diff", 0))
            return {"checked": True, "ok": False, "action": action, "tags": sorted(t for t in tags if t),
                    "conflicts": hits,
                    "reason": f"성분의 개념들이 겹치는 기간에서 값이 어긋난다 — {worst['period']} "
                              f"{worst['kept']['tag']} {worst['kept']['val']:,} 대 "
                              f"{worst['other']['tag']} {worst['other']['val']:,} "
                              f"(상대차 {worst.get('rel_diff', 0) * 100:.2f}%). 회계기준이 다르다"}
        return {"checked": True, "ok": True, "tags": sorted(t for t in tags if t),
                "reason": ("한 개념에서 왔다" if len(tags) == 1 else
                           "개념이 여럿이나 겹치는 기간의 값이 일치한다 — 태그 이름만 바뀐 것이다")}

    # ------------------------------------------------------------ F3 ladder
    def f3_ladder(self, points: float, imitation_pass: bool, door_closed_pass: bool) -> tuple[int, str]:
        spec = self.factor("F3")
        for rung in spec["ladder"]:
            if points in rung["points"]:
                score = int(rung["score"])
                note = f"통과점 {points:g} → {score}"
                if rung.get("requires_imitation_pass") and not imitation_pass:
                    score = 3
                    note += " (모방불가 완전 pass 아님 → 상한 3)"
                elif rung.get("requires_imitation_pass") and spec.get("score5_requires_door_closed") and door_closed_pass:
                    score = 5
                    note += " + 문 닫힘 증거 → 5"
                return score, note
        raise SchemaError(f"F3 통과점 {points!r} 은 사다리에 없음")

    # ------------------------------------------------------------ F5 / F7
    def f5_formula(self, A: int, H: int) -> int:
        spec = self.factor("F5")
        if A not in spec["A_allowed"] or H not in spec["H_allowed"]:
            raise SchemaError(f"F5 입력 범위 밖: A={A}, H={H}")
        return 3 + A + H

    def f7_matrix(self, share: str, returns: str) -> int:
        key = f"{share}|{returns}"
        matrix = self.factor("F7")["matrix"]
        if key not in matrix:
            raise SchemaError(f"F7 매트릭스 키 없음: {key}")
        return int(matrix[key])


def load_rules(version: str) -> RuleSet:
    path = RULES_DIR / f"{version}.json"
    payload = load_json_strict(path)
    ruleset = RuleSet(payload, path)
    if ruleset.version != version:
        raise SchemaError(f"규칙 파일 rule_version {ruleset.version!r} != 요청 {version!r}")
    return ruleset


def run_decision(run: dict[str, Any], decision_id: str) -> dict[str, Any] | None:
    for item in run.get("decisions", []):
        if item["id"] == decision_id:
            return item
    return None


def decision_choice(run: dict[str, Any], rules: RuleSet, decision_id: str) -> str | None:
    """실행 단위 결정이 있으면 그 선택을, 없으면 None. 규칙의 choices 밖 선택은 오류."""
    item = run_decision(run, decision_id)
    if item is None:
        return None
    spec = rules.decision(decision_id)
    if spec is None:
        raise SchemaError(f"run.decisions: 규칙에 없는 결정 ID {decision_id}")
    choices = spec.get("choices") or []
    if choices and item["choice"] not in choices:
        raise SchemaError(f"run.decisions[{decision_id}]: choice {item['choice']!r} 는 {choices} 중 하나")
    return str(item["choice"])
