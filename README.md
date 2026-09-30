# AI 기업 9-factor 채점표

AI 기업을 아홉 항목으로 채점하는 프레임워크입니다. **판단자의 판단을 정해진 규칙으로 정리하고 검산합니다.** 코드가 기업을 평가해 주는 도구가 아닙니다.

앞의 다섯(① 네트워크 효과 · ② 신기술 게임체인저 · ③ Last Mover · ④ 호황 이후 비전 · ⑤ 아군 확보)은 더하고, 뒤의 넷(⑥ 가격 · ⑦ 순환금융 · ⑧ 비대칭 의존 · ⑨ 적자 깊이)은 뺍니다.

## 지금 상태 (2026-09-21)

| 항목 | 값 |
| --- | --- |
| 최신 실행 | `ai-scorecard-2026-09-obsreg` · 기준일 2026-09-02 · 규칙 v1.7 |
| 점수 지문 | `results_hash 4a3f6c05b206ef81…` |
| 리뷰 | 독립 세션 4영역 리뷰 9라운드 끝에 네 영역 pass (2026-09-17) |
| 승인 | 2026-09-17 사용자 승인. 그 뒤 **설명 문장과 화면 표시만** 고쳤고 점수 파일은 바이트 단위로 동일합니다. 초안이 바뀌어 승인 효력이 멈춘 **재승인 대기** 상태입니다 |
| 테스트 | `npm run test:scorecard` 797건 통과 |

조정총점은 alphabet 15 · amazon 15 · meta 15 · microsoft 14 · tsmc 10 · anthropic 10 · spacex-xai 9 · nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · openai 4 · oracle 2 입니다.

## 아홉 항목은 어떻게 매겨지나

항목마다 틀이 잡힌 깊이가 다릅니다.

| 단계 | 항목 | 점수가 나오는 방식 |
| --- | --- | --- |
| 측정값만으로 계산 | ⑥ 가격 | 공시 숫자(매출·순이익·시가총액)를 규칙의 절대 구간에 넣습니다. 사람 판단이 들어가지 않습니다 |
| 측정값 + 사람 판단 | ⑨ 적자 깊이 | 영업손익·현금흐름은 공시에서, `현금흐름 추세` 같은 여덟 가지 판정은 사람이 넣습니다. 흑자 회사의 0점과 −1점은 사람이 고른 추세 한 칸으로 갈립니다 |
| 정해진 질문에 답하면 표가 환산 | ③ ⑤ ⑦ | ③ 은 네 기준의 통과·실패, ⑤ 는 동맹·적대 등급, ⑦ 은 두 축을 사람이 정하고 코드는 표로 환산만 합니다 |
| 점수를 직접 입력 | ① ② ④ ⑧ | 점수와 근거 문장을 통째로 적습니다. ② 는 규칙에 환산표가 있지만 이번 실행에서는 쓰이지 않았습니다 |

코드가 맡는 일은 셋입니다. 모든 기업에 **같은 잣대를 강제**하고, **산수 실수를 없애고**, 어떤 입력에서 어떤 점수가 나왔는지 **지문으로 묶어 추적**할 수 있게 합니다.

## 쓰는 법

```
plan → research → calculate → draft → review → (사용자 승인) → build
```

| 단계 | 명령 | 산출물 |
| --- | --- | --- |
| 실행 생성 | `python scripts/scorecard_cli.py init <slug> --as-of 2026-09-02 --title ... --request ...` | `plan/<slug>.md`, `scorecard/runs/<slug>/{run,observations,judgments,sources}.json` |
| 리서치 | `python scripts/scorecard_cli.py research <slug>` | `research/<slug>.md` |
| 계산 | `python scripts/scorecard_cli.py calculate <slug>` | `results.json`, `preview.md` |
| 초안 | `python scripts/scorecard_cli.py draft <slug>` | `drafts/<slug>.md` |
| 리뷰 | `python scripts/scorecard_cli.py review-template <slug>` 뒤 독립 세션 4영역 리뷰 | `reviews/<slug>.md` |
| 승인 | `python scripts/scorecard_cli.py approve <slug> --by <이름>` (사용자만 실행) | `approval.json` |
| 빌드 | `python scripts/build_report.py <slug>` | `output/<slug>.html`, `output/<slug>-audit.md`, `scorecard/history.csv` |
| 상태 확인 | `python scripts/scorecard_cli.py status <slug>` · `python scripts/validate_report_contract.py <slug>` | 단계별 완료 여부와 계약 위반 목록 |

Claude Code 에서는 `/score-plan`, `/score-research` 처럼 슬래시 명령으로도 부를 수 있습니다. 각 단계의 에이전트 작업 계약은 `.claude/skills/score-*/SKILL.md` 에 있습니다.

slug 는 `ai-scorecard-` 로 시작하고 plan frontmatter 의 `report_type: ai_scorecard` 로 분기합니다. 기준선 v1.5 는 `python scripts/scorecard_cli.py import-baseline` 으로 원본에서 읽어 옵니다.

**판단을 입력하는 명령은 아직 없습니다.** 지금 판단 데이터는 v1.5 채점표에서 기계로 읽어 온 것과 에이전트가 고친 것입니다.

## 파일은 네 종류입니다

| 종류 | 무엇 | 위치 |
| --- | --- | --- |
| 기준 | 무엇을 보고 몇 점을 줄지 | 사람용 `AI_company_analysis_factor/` (채점규칙 · 별표 A~J) · 기계용 `scorecard/rules/v1.7.json` |
| 입력 | 공시 숫자와 사람 판단 | `scorecard/runs/<slug>/observations.json` · `judgments.json` · `sources.json` |
| 계산 | 입력에 기준을 적용하는 코드 | `scripts/scorecard/` (`calc_f6_params.py` · `calc_f9.py` · `calc_qual.py` · `render_*.py` · `validate.py`) |
| 지시 | 에이전트의 작업 순서와 금지 사항 | `AGENTS.md` · `.claude/skills/score-*` · `.claude/agents/` |

점수는 기준·입력·계산 셋만으로 결정됩니다. 지시 문서는 일하는 순서를 적은 안내서이고 점수에 영향을 주지 않습니다.

**사람용 규칙 문서는 v1.5 에 멈춰 있습니다.** v1.6·v1.7 의 변경은 기계용 JSON 과 결정 기록에만 있어, 별표 일부(⑥ 전체 · ⑦ 별표 I · ⑨ 게이트 · ② 의 5점 조건 · ⑤ 의 +2 조건)가 지금 점수와 다릅니다.

## 지문으로 묶여 있습니다

각 단계의 산출물에는 앞 단계 파일의 지문(sha256)이 기록됩니다. 승인 파일은 규칙·숫자·판단·실행 설정·점수·초안 여섯 개의 지문을 담습니다. 앞 단계가 한 글자라도 바뀌면 리뷰와 승인이 자동으로 무효가 됩니다. 근거 문장만 고쳐도 같습니다. 그래서 승인된 리포트는 **어떤 입력에서 나온 점수인지 나중에도 증명**할 수 있습니다.

리포트 본문에는 읽는 사람을 위한 내용만 싣습니다. 해시, 결정 번호(C-01~C-29), 긴장 번호, 리뷰 진행 기록, 정정 이력은 `output/<slug>-audit.md` 에 있습니다.

## 가드레일

Claude Code 프로젝트 훅이 반복 실패를 사전에 차단합니다. 설정은 `.claude/settings.json`, 스크립트는 `.claude/hooks/` 아래에 단일 책임으로 있습니다.

| 훅 | 역할 |
| --- | --- |
| `block-dangerous-bash.sh` | `rm -rf /`, `sudo`, `git push --force` 등 되돌리기 어려운 명령 차단 |
| `protect-sensitive-files.sh` | `.env*`, `.git/`, `docs/finance-style-guide.md`, `docs/output-spec.md` 수정 차단 |
| `forbid-financial-advice.sh` | 투자 권유·수익 보장·FOMO 표현 차단 |
| `enforce-plan.sh` | 선행 산출물 순서 강제 |
| `enforce-citations.sh` | 숫자 주장에 출처 표식 요구 |
| `remind-review.sh` | draft 변경 후 최신 리뷰 `pass` 가 없으면 세션 종료 차단 |
| `inject-memory-context.sh` · `enforce-memory.sh` | 작업 메모 주입과 검증 |

훅은 Claude Code 가 이 프로젝트 설정을 읽을 때 자동 적용됩니다. Codex 런타임에는 자동으로 걸리지 않아 별도 연결이 필요합니다.

## 이해상충

채점 대상에 Anthropic 이 들어 있고, 이 저장소의 작업 상당 부분을 Anthropic 의 Claude 가 수행했습니다. Anthropic 과 그 직접 경쟁사(OpenAI · Google)에 걸린 판단은 **Claude 가 아닌 세션이 재판정**하는 것을 원칙으로 합니다. 최종 승인은 항상 사용자가 합니다.

## 작업공간과 브랜치

Orca 작업공간은 폴더 복사본이 아니라 이 저장소의 git worktree 입니다. 커밋은 모두 이 저장소 하나에 있습니다.

| 브랜치 | 역할 |
| --- | --- |
| `HANSOLJJ/worker` | 코드·규칙·데이터를 실제로 고치는 곳 |
| `HANSOLJJ/설계진행` | 과제 분배와 검증 기록(`validation/`) |
| `HANSOLJJ/review-obsreg` | 독립 리뷰 기록(`reviews/_parts/`) |
| `HANSOLJJ/NTM-전망치조사` · `HANSOLJJ/C-13` · `HANSOLJJ/scarpper` | 자료 조사와 보조 검증 |

2026-09-21 에 위 브랜치를 `main` 으로 합쳤습니다. 같은 경로에 서로 다른 내용이 있던 C-13 의 네 파일은 `validation/*/c13/` 아래에 따로 보존했습니다.

## 다음에 정할 것

1. **사람용 v1.7 규칙 문서** — v1.5 원문에서 출발해 바뀐 자리만 `이전 → 지금` 으로 표시합니다. 규칙을 사람 말로 옮길 때마다 오류가 나왔으므로 독립 대조를 거칩니다.
2. **별표를 리포트에 싣기** — 본문이 별표를 46번 가리키지만 내용은 리포트에 없습니다.
3. **재승인과 정식 빌드** — 점수는 그대로이고 설명만 바뀌었습니다.
4. **기업 추가 명령** — `add-company` 로 레지스트리에 등록하고, `init --from-run` 으로 이전 실행을 이어받아 **새 기업만 조사**합니다. 기존 기업 불변은 `diff` 가 기계로 증명합니다. 계획 승인 완료, 구현 중입니다.
5. **규칙 폴더를 `v1.5/` · `v1.7/` 로 정리** — `scripts/scorecard/baseline_import.py` 와 테스트 둘이 지금 경로를 직접 참조하므로 경로 수정과 함께 해야 합니다.
6. **정성 판단의 입력 창구** — 에이전트가 질문별로 답·근거·출처를 조사해 제안하고, 사용자가 검토 화면에서 동의하거나 고치는 방식을 검토 중입니다.
7. **v1.8 방향** — 점수를 직접 입력하는 ① ② ④ ⑧ 을 ③ ⑤ ⑦ 처럼 정해진 질문으로 쪼개고, 질문마다 공시에서 잴 수 있는 값(고객 집중도 · 벤치마크 순위 · 출하 여부 · 수주잔고)을 붙입니다.

세부 미결 사항은 `docs/scorecard/open-items.md`, 도메인 명세는 `docs/scorecard/design-guideline.md`, 구조 지침은 `docs/scorecard/structure.md` 에 있습니다.

## 설치와 보조 명령

```bash
uv sync --frozen
npm run check
```

```bash
npm run test:scorecard                              # 채점표 테스트
python3 scripts/validate_report_contract.py <slug>  # 계약 검증
python3 scripts/validate_memory.py                  # 작업 메모 검증
node server.js                                      # output/ 로컬 미리보기
```

- Python 3.12+ 와 uv, `pyproject.toml` 의 PyYAML·yfinance, Node.js 18+, Claude CLI
