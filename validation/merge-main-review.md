# MERGE-MAIN 검토 — 워크트리 간 전파 구조 수리

- 검토일. 2026-09-11.
- 대상. worker `e0eebfb` 중단 보고 · NTM `a70b2c8` · main `4cd5eae`·`4056de2`.
- 판정. **worker `pass`(중단이 옳았다) · NTM `pass`.** **worker 가 내 전제를 뒤집었고 그것이 이 라운드의 핵심이다.**

## 내가 틀린 것 — 한 사례로 셋을 일반화했다

설계진행에서 머지해 보니 AGENTS.md 충돌이 전부 "main 이 최신" 방향이었다. 그래서 세 워크트리에 똑같이 지시했다.

> AGENTS.md 는 `git checkout --theirs AGENTS.md` 로 받으십시오.

**worker 에서는 그것이 파괴적 지시였다.**

```
worker AGENTS.md   ## AI Scorecard 계약 (report_type: ai_scorecard)   13줄
main   AGENTS.md   "scorecard" 낱말  0건
```

**그 워크트리의 작업 전체를 규정하는 절이다.** 명령 8개, 단일 진실 위치, 정성 판정 범위, 승인 해시 규칙, 테스트 명령이 거기 있다. `--theirs` 로 받았으면 통째로 사라졌다.

**worker 가 멈추고 보고해서 잡혔다.** 내가 "AGENTS.md 외의 충돌은 해결하지 말고 멈추라" 고 적은 것이 걸린 것이 아니다 — worker 는 **AGENTS.md 자체도 해결하지 않고** 전제를 되짚었다. 지시받은 범위를 넘어 지시의 근거를 검증한 것이다.

**한 워크트리에서 확인한 것을 같은 이름이라는 이유로 다른 워크트리에 옮겼다.** 오늘 AGENTS.md `## 원자료 조사 규율` 마지막 줄에 적은 바로 그 실수를, 그 줄을 적은 날에 했다.

## 사후 대조 — 실제로 갈린 것은 worker 하나뿐이었다

|  | 브랜치 고유 절 | `--theirs` 안전 |
|---|---|---|
| 설계진행 | 없음 | 안전 (이미 완료) |
| C-13 | 없음 (4곳 차이 전부 main 이 최신) | 안전 |
| NTM | 없음 | 안전 (이미 완료) |
| **worker** | **AI Scorecard 계약 13줄** | **아님** |

**3/4 에서 맞는 지시였다. 그래서 더 위험했다** — 세 번 잘 돌아간 뒤 네 번째에서 조용히 지웠을 것이다.

## 처리 — worker 제안대로 main 에 올렸다

```
main 4056de2   ## Build 계약 다음, ## 금지·주의 앞
               worker 원문 13줄 + 다음 한 줄
```

> 구현은 scorecard 작업 브랜치에서 진행 중이며 `scorecard/`·`scripts/scorecard_cli.py`·`docs/scorecard/`는 그 브랜치가 머지될 때 들어온다. 이 절은 그때까지 계약 선언으로만 유효하다.

**브랜치에만 사는 절을 남기는 선택지도 있었고 그것을 버린 이유를 적는다.** 남기면 머지마다 같은 충돌이 나고, 그때마다 사람이 "이건 지워도 되나" 를 다시 판단한다. **어제 고친 병이 그대로다** — 같은 파일이 브랜치별로 다른 상태를 유지하는 것. main 에 없는 파일을 가리키게 되는 비용은 절 안에 한 줄로 적어 상쇄했다.

## NTM 이 찾은 것 — 충돌 0 이 머지 성공이 아니다

```
git merge main   →  충돌 없이 통과
결과             →  ## Orca worktree 간 메시지와 작업 실행  절이 두 번
                    113행 이하 중복본이 main 이 교체한 옛 전파 규칙을 담음
```

**새 규칙(82행)과 옛 규칙(113행 이하)이 한 파일에 공존했다.** "AGENTS.md 는 main 에서만 고친다" 와 "각 worktree 의 같은 규칙을 갱신한다" 가 나란히 있었다. 지운 12줄을 대조했고 전부 옛 판본이다.

**한쪽이 절을 통째로 교체하고 다른 쪽이 그 자리를 안 건드리면 git 이 양쪽을 나란히 남길 수 있다.** 머지 후 결과 파일을 읽지 않았으면 그대로 갔다. **NTM 이 회신에 적어서 잡혔다.**

## 코드 충돌 판정 — worker

### `.claude/hooks/enforce-plan.sh` — main 채택

```
브랜치  scorecard = report_type(slug) == 'ai_scorecard'   ai_scorecard 만 면제
main    cf3f2da  hero 이미지를 전 유형 선택 사항으로       상위 집합
```

**합칠 자리가 아니라 덮는 자리다.** `report_type()` 헬퍼는 이 파일에서 미사용이 되나 **지우지 않는다** — hero 요건이 되살아나면 다시 쓴다.

### `scripts/build_report.py` — 세 곳 전부 합친다

(2) scorecard 분기는 main 에 대응물이 없는 순수 추가다. 충돌로 잡혔을 뿐이다.

(3) 이 자리가 미묘하다. **브랜치가 `image_path is not None` 을 ai_scorecard 판별의 대리값으로 썼는데 main 이 그 대리값을 깨뜨렸다.**

```
main 이 hero 를 선택 사항으로 만든 뒤
  stock_report 도 image_path == None 가능
  → 브랜치판: hero 없는 stock_report 가 "Generated files:" 를 찍는다
  → main 판:  ai_scorecard 가 "image manifest 미완료" 를 찍는다
             그 유형에 manifest 라는 것이 없다
```

**양쪽 다 틀린다.** 어느 한쪽을 고르는 것으로 안 되고 판별을 실제 `report_type_for()` 로 되돌려야 한다. **대리값은 그것이 참인 동안만 참이고, 그 조건이 바뀐 것을 대리값 쪽이 모른다.**

## 남은 것

| 건 | 상태 |
|---|---|
| 설계진행 머지 | 완료 `2b4b29a` |
| NTM 머지 | 완료 `a70b2c8` · `4056de2` 추가 머지 발송 |
| C-13 머지 | 발송 `msg_6157d7599bd5` — `--theirs` 안전 확인 완료 |
| worker 머지 재개 | 발송 `msg_4e888b13dab1` — 충돌 3곳 판정 포함 |
